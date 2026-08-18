#!/usr/bin/env python3
"""
Macro-expanding OpenFOAM field reader for B3 (Ladder B, Certonomous).

Problem this solves: CBFS's LES reference fields (0/U_LES, 0/k_LES,
0/tauij_LES, 0/p_LES) are written using OpenFOAM's textual
`#include "relative/path"` macro mechanism plus `$name` dictionary-entry
substitution, e.g.:

    #include "interpolatedFields/U_internalField"
    ...
    internalField   $U_internalField;

`Ofpp.parse_internal_field` (the package B2 used for scoring) does not
resolve `#include` or `$name` at all -- it just regexes for a line starting
with `internalField` that literally contains the substring `nonuniform` or
`uniform`. Since the on-disk line is `internalField   $U_internalField;`,
neither substring is present, so Ofpp's loop runs to the end without a
match and returns None. No exception is raised. This is the exact silent
failure mode flagged in B2.

Approach: do the same textual macro expansion OpenFOAM's own preprocessor
would do (splice in `#include`d file contents, then substitute `$name`
tokens with the previously-defined entry's value text), producing a fully
literal dictionary with no macros left. Feed that expanded text, as a list
of byte lines (same shape `open(fn, "rb").readlines()` produces), straight
into Ofpp's own `parse_internal_field_content` / `parse_boundary_content`.
This deliberately reuses Ofpp's already-trusted low-level array parser
rather than reimplementing OpenFOAM list parsing --- the new code here is
only the macro-resolution step.

CRITICAL: every result is checked against None / empty and reported
explicitly. A silent None is exactly the failure mode this file exists to
avoid reproducing.
"""
import os
import re
import sys

sys.path.insert(0, "/home/ubuntu/closure-challenge-pkg/src")
from Ofpp.field_parser import parse_internal_field_content, parse_boundary_content

_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
_LINE_COMMENT_RE = re.compile(r"//[^\n]*")
_INCLUDE_RE = re.compile(r'^\s*#include\s+"([^"]+)"\s*$', re.M)
_DOLLAR_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


def _resolve_includes(path, _seen=None):
    """Recursively splice #include "relpath" directives into the file text.

    Relative paths are resolved against the directory of the *including*
    file, matching OpenFOAM's own #include semantics.
    """
    if _seen is None:
        _seen = set()
    path = os.path.abspath(path)
    if path in _seen:
        raise ValueError(f"circular #include detected at {path}")
    _seen = _seen | {path}

    with open(path, "r") as f:
        text = f.read()

    directory = os.path.dirname(path)

    def _sub(m):
        inc_path = os.path.join(directory, m.group(1))
        if not os.path.exists(inc_path):
            raise FileNotFoundError(
                f"#include \"{m.group(1)}\" referenced from {path} "
                f"resolves to {inc_path}, which does not exist"
            )
        return _resolve_includes(inc_path, _seen)

    return _INCLUDE_RE.sub(_sub, text)


def _strip_comments(text):
    text = _BLOCK_COMMENT_RE.sub("", text)
    text = _LINE_COMMENT_RE.sub("", text)
    return text


def _split_top_level_entries(text):
    """Walk the flattened dictionary text and return an ordered dict of
    {entry_name: raw_value_text} for every top-level `name value;` or
    `name { ... }` entry. Value text excludes the entry name and the
    terminating ';' (for scalar/list entries) or the outer braces are kept
    for dict-valued entries.
    """
    entries = {}
    i = 0
    n = len(text)
    ident_re = re.compile(r"[A-Za-z_][A-Za-z0-9_<>]*")

    while i < n:
        # skip whitespace
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        m = ident_re.match(text, i)
        if not m:
            # stray character at top level (e.g. leftover ';') -- skip it
            i += 1
            continue
        name = m.group(0)
        j = m.end()
        # skip whitespace between name and value
        k = j
        while k < n and text[k].isspace():
            k += 1
        if k < n and text[k] == "{":
            # dict-valued entry: find matching brace
            depth = 0
            start = k
            p = k
            while p < n:
                if text[p] == "{":
                    depth += 1
                elif text[p] == "}":
                    depth -= 1
                    if depth == 0:
                        p += 1
                        break
                p += 1
            entries[name] = text[start:p]
            i = p
            # optional trailing ';'
            while i < n and text[i].isspace():
                i += 1
            if i < n and text[i] == ";":
                i += 1
        else:
            # scalar/list-valued entry: consume until a ';' at paren-depth 0
            depth = 0
            p = j
            while p < n:
                c = text[p]
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                elif c == ";" and depth == 0:
                    break
                p += 1
            entries[name] = text[j:p].strip()
            i = p + 1  # skip the ';'
    return entries


def expand_openfoam_field(path):
    """Return a dict of {entry_name: fully-resolved value text} for the
    top-level dictionary entries in an OpenFOAM field file, after splicing
    in #include directives and resolving $name references.

    IMPORTANT (a second bug found while building this, beyond B2's original
    "silent None" report): OpenFOAM dictionaries use LAST-ENTRY-WINS
    semantics when a key is defined more than once. CBFS's own 0/p_LES
    exploits this deliberately: it has a placeholder
    `internalField   uniform 0;` BEFORE the #include block, which is then
    legitimately overridden by `internalField   $p_internalField;` AFTER
    the include. Ofpp's parse_internal_field_content scans line-by-line and
    returns on the FIRST line starting with "internalField" -- so even
    after macro expansion, feeding the whole flattened document back into
    Ofpp's scanner reproduces a *second*, more dangerous failure mode: not
    a None, but a plausible-looking WRONG value (uniform 0.0 instead of the
    real 21000-cell LES pressure field). This function avoids that by
    building an explicit last-wins dict of top-level entries first, and
    the caller feeds ONLY the single resolved entry it wants to Ofpp's
    line parser, never the whole document.
    """
    raw = _resolve_includes(path)
    stripped = _strip_comments(raw)
    entries = _split_top_level_entries(stripped)  # dict assignment => last occurrence wins

    resolved = {}

    def _resolve(name, stack=()):
        if name in resolved:
            return resolved[name]
        if name not in entries:
            raise KeyError(
                f"'${name}' referenced but no top-level entry named "
                f"'{name}' was found (macro expansion incomplete)"
            )
        if name in stack:
            raise ValueError(f"circular macro reference: {' -> '.join(stack + (name,))}")
        val = entries[name]
        val = _DOLLAR_RE.sub(lambda m: _resolve(m.group(1), stack + (name,)), val)
        resolved[name] = val
        return val

    for name in list(entries.keys()):
        _resolve(name)
    return resolved


def _to_bytelines(text):
    return [line.encode("utf-8") for line in text.splitlines(keepends=True)]


def parse_internal_field_macro(path):
    """Macro-aware replacement for Ofpp.parse_internal_field. Returns a
    numpy array. Returns None only if there genuinely is no `internalField`
    entry anywhere in the fully-resolved dictionary (matching Ofpp's own
    convention for that case) -- never silently for an unresolved macro,
    and never the shadowed/placeholder value for a duplicate key (see
    expand_openfoam_field docstring).
    """
    resolved = expand_openfoam_field(path)
    if "internalField" not in resolved:
        return None
    snippet = "internalField   " + resolved["internalField"] + ";\n"
    lines = _to_bytelines(snippet)
    return parse_internal_field_content(lines)


def parse_boundary_field_macro(path):
    resolved = expand_openfoam_field(path)
    if "boundaryField" not in resolved:
        return None
    snippet = "boundaryField\n" + resolved["boundaryField"] + "\n"
    lines = _to_bytelines(snippet)
    return parse_boundary_content(lines)


if __name__ == "__main__":
    import numpy as np

    CBFS = "/home/ubuntu/Certonomous/demo-output/website/dafoam/ladder-b/duct_baseline/CBFS"
    for fname in ["U_LES", "k_LES", "tauij_LES", "p_LES"]:
        fpath = os.path.join(CBFS, "0", fname)
        if not os.path.exists(fpath):
            print(f"{fname}: file does not exist, skipping")
            continue
        arr = parse_internal_field_macro(fpath)
        if arr is None:
            print(f"{fname}: MACRO READER RETURNED None -- BLOCKER NOT CLEARED")
            continue
        arr = np.asarray(arr)
        print(f"{fname}: shape={arr.shape} dtype={arr.dtype} "
              f"min={arr.min(axis=0) if arr.ndim > 1 else arr.min()} "
              f"max={arr.max(axis=0) if arr.ndim > 1 else arr.max()} "
              f"mean={arr.mean(axis=0) if arr.ndim > 1 else arr.mean()}")
