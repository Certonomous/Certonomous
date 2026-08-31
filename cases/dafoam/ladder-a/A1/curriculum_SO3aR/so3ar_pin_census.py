#!/usr/bin/env python3
"""SO-3aR PIN CENSUS -- A SWEEP BY **ROLE**, NEVER BY THE SHAPE OF A VALUE.

WHY THIS FILE EXISTS, AND IT IS THE WHOLE OF SO-3aR's REASON TO EXIST
====================================================================
SO-3a died at its SECOND arm on 2026-08-31T18:43:21Z.  Every preflight gate
passed, a container started, and the solver exited 2 in ten seconds on:

    SO3A_XF REFUSE producer md5 c0821199159026ec597549ee034b73ac
            != frozen UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED

`so3a_xf.py:111` carried `PRODUCER_MD5 = "UNSET-PRODUCER-PIN-SENTINEL-FAILS-
CLOSED"` -- its own producer pin, never filled.  THE PIN ITSELF WORKED
PERFECTLY: it refused to run the instrument against an unverified producer, and
the md5 it printed is in fact the correct md5 of `so3a_runScript.py`.  The item
could never have launched.  Item verdict NOT A RESULT, 0.334 core-min burnt.

AND HERE IS THE IRONY THAT THIS FILE IS THE ANSWER TO.  SO-3a's own frozen
AMENDMENT S2-1 §4 DELETED an earlier sentinel, `MD5_UNSET`, for a stated and
CORRECT reason: its value was 32 zeros, *a well-formed md5*, so a pin-counting
leg would have counted a dead sentinel as a real pin.  `so3a_xf.py`'s sentinel
is the BETTER design -- deliberately NOT md5-shaped, so it can never
accidentally equal any file's digest.

**AND THAT IS EXACTLY WHY THE CENSUS COULD NOT SEE IT.**  SO-3a's census legs
`(x12)`, `(x13)` and `(x14)` selected pins BY THE SHAPE OF THE VALUE --
`grep -oP "^$1=\\K[0-9a-f]{32}"` and
`grep -cE '^MD5_[A-Z_0-9]+=[0-9a-f]{32}'` -- and only inside ONE file, the chain
driver.  A constant whose value is deliberately not 32 hex is OUTSIDE THAT RULE
SET.  `(x14)` reported "13 declared, 13 driven" and was RIGHT ABOUT THIRTEEN
md5-SHAPED PINS IN ONE FILE and SILENT about a fourteenth that was not.
**The property that makes the sentinel safe against false matching is the
property that makes it invisible to the census that would have flagged it
unset.**  A zero that is a statement about a rule set is not a statement about
the code.

THE INVERSION THIS FILE MAKES
=============================
The value's shape is **the thing under test**, never the selector.  A constant
is enumerated because of what it IS FOR, by two independent enumerators whose
union no single blindness can escape:

  E-NAME   -- the IDENTIFIER carries the token `MD5` (any case), in shell or in
              python, WHATEVER THE VALUE LOOKS LIKE.  This alone catches
              `PRODUCER_MD5 = "UNSET-..."`.
  E-SHAPE  -- the VALUE is a bare 32-hex or 64-hex (or `sha256:`+64-hex)
              literal, WHATEVER THE IDENTIFIER IS CALLED.  This alone catches a
              pin named `PRODUCER_FINGERPRINT`, which E-NAME would miss.

Neither enumerator is trusted alone; a pin found by EITHER must carry a
disposition, so hiding a pin requires defeating BOTH at once.

Then, and only then, the VALUE is tested:

  A1  every enumerated constant has a row in the REGISTERED DISPOSITION TABLE
      below -- a NEW pin with no row is RED, so a pin cannot be added silently.
  A2  every pin of kind LOCAL / TUTORIAL / CONTAINER holds a REAL md5
      (`^[0-9a-f]{32}$`).  A sentinel, an empty string, a 31-hex typo -> RED.
      **THIS IS THE ASSERTION THAT WOULD HAVE STOPPED SO-3a BEFORE LAUNCH.**
  A3  every pin of kind LOCAL / TUTORIAL EQUALS the md5 of the file it pins.
  A4  every enumerated pin has at least ONE consumer site -- a dead pin sits in
      the tree one edit from re-use (AMENDMENT S2-1 §4's own reason for
      deleting `MD5_UNSET`).
  A5  every CONSUMER SITE reads a constant that is in the pin set -- a new
      unpinned consumer is RED.
  A6  the target this file registers for a pin EQUALS the target the CODE
      hashes at that pin's consumer site.  The table cannot drift from the code
      it describes.
  A7  every disposition row names a constant that EXISTS in the sources -- a
      stale row propping up a deleted pin is RED.

RULE 3, THE PLANTED CONTROL, ON THE CENSUS'S OWN READER
=======================================================
A census that parses nothing reports zero problems.  Before any assertion is
evaluated this file PLANTS a known perturbation into an in-memory copy of every
source it reads -- one pin's value replaced by a sentinel -- and RE-RUNS ITS OWN
EXTRACTOR over the planted text.  If the extractor cannot see the plant, the
census REFUSES (exit 2) and reports nothing.  A zero from a reader not shown
able to see a non-zero is not evidence.

EXIT CODES.  0 = GREEN (every assertion holds).  1 = RED (an assertion failed;
every failure is printed with the constant, its value, its file and its line).
2 = REFUSE (the census's own reader is blind, or a source is unreadable) -- a
refusal is NOT a green and is NOT a red; it is the absence of a reading.

SCOPE.  This file is an INSTRUMENT of curriculum SO-3aR and speaks for no other
item.  It introduces no lab-wide rule and no general-purpose tool (Sanaa's
2026-08-31 PLUMBING FREEZE): it is one item's repair of one item's instrument,
done once, to the fail-closed + planted-control standard.
"""

import argparse
import ast
import hashlib
import json
import os
import re
import sys

MD5_RE = re.compile(r"^[0-9a-f]{32}$")
HEX32_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{32}$")
HEX64_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")

# ---------------------------------------------------------------------------
# THE SOURCES SWEPT.  Every file of this item that a human could put a pin in.
# The list is asserted COMPLETE against the directory listing (A0) so a new
# instrument file cannot join the item without joining the census.
# ---------------------------------------------------------------------------
SOURCES = [
    "so3ar_chain_driver.sh",
    "so3ar_run_arm.sh",
    "so3ar_xf.py",
    "so3ar_grade.py",
    "so3ar_runScript.py",
    "so3ar_aggregate_memory.py",
    "so3ar_stop_marker.sh",
    "so3ar_groot5_selftest.sh",
    "so3ar_xf_selftest.py",
    "so3ar_pin_census.py",
]
# Files in the case directory that are DELIBERATELY not swept, each with its
# reason.  An exclusion that is stated is reviewable; a silent one is not.
SOURCES_EXCLUDED = {
    "so3ar_decomposeParDict": "an OpenFOAM dictionary, not a program; it holds "
                              "no constants and executes nothing",
    "so3ar_derive_from_so3a.sh": "the one-shot derivation script; it runs "
                                 "BEFORE the item exists and pins nothing -- "
                                 "the md5s it prints are READINGS of the "
                                 "parent, taken at run time, not constants",
}

# ---------------------------------------------------------------------------
# THE REGISTERED DISPOSITION TABLE.  key = "<file>:<CONSTANT>" (a subscripted
# python pin is "<file>:<NAME>[<key>]").  value = (kind, target).
#
#   LOCAL      target is a path relative to THIS directory.  Must exist; the
#              pin must EQUAL its md5.
#   TUTORIAL   target is a path relative to TUT_SRC, which is read out of the
#              chain driver's OWN BYTES and never hard-coded here.  Must exist;
#              the pin must EQUAL its md5.
#   CONTAINER  the pin names a file INSIDE a container image and is NOT
#              resolvable on this host.  The value must still be a real md5 and
#              the pin must have a consumer; the NON-RESOLUTION IS PRINTED, and
#              this census never reports it as verified.
#   DIGEST     a container-image sha256, not an md5 and not a file on disk.
#              NAMED EXCLUSION from A2/A3 with its reason; A1/A4/A5/A7 still
#              bind it, so it cannot be deleted or orphaned silently.
# ---------------------------------------------------------------------------
DISPOSITION = {
    # ---- the chain driver's in-repo pins -----------------------------------
    "so3ar_chain_driver.sh:MD5_LAUNCHER":     ("LOCAL", "so3ar_run_arm.sh"),
    "so3ar_chain_driver.sh:MD5_GRADER":       ("LOCAL", "so3ar_grade.py"),
    "so3ar_chain_driver.sh:MD5_RUNSCRIPT":    ("LOCAL", "so3ar_runScript.py"),
    "so3ar_chain_driver.sh:MD5_XF":           ("LOCAL", "so3ar_xf.py"),
    "so3ar_chain_driver.sh:MD5_AGG":          ("LOCAL", "so3ar_aggregate_memory.py"),
    "so3ar_chain_driver.sh:MD5_DECOMP":       ("LOCAL", "so3ar_decomposeParDict"),
    "so3ar_chain_driver.sh:MD5_STOP_MARKER":  ("LOCAL", "so3ar_stop_marker.sh"),
    # ---- the chain driver's out-of-tree tutorial pins ----------------------
    "so3ar_chain_driver.sh:MD5_TUT_RUNSCRIPT": ("TUTORIAL", "runScript.py"),
    "so3ar_chain_driver.sh:MD5_TUT_GEN":       ("TUTORIAL", "genAirFoilMesh.py"),
    "so3ar_chain_driver.sh:MD5_TUT_PREPROC":   ("TUTORIAL", "preProcessing.sh"),
    "so3ar_chain_driver.sh:MD5_TUT_PS":        ("TUTORIAL", "profiles/NACA0012PS.profile"),
    "so3ar_chain_driver.sh:MD5_TUT_SS":        ("TUTORIAL", "profiles/NACA0012SS.profile"),
    "so3ar_chain_driver.sh:MD5_TUT_FFD":       ("TUTORIAL", "FFD/wingFFD.xyz"),
    # ---- THE LAUNCHER'S OWN THREE.  SO-3a's census did not hold these: they
    # ---- are declared in a DIFFERENT FILE from the driver, and (x12)/(x14)
    # ---- read the driver alone.  They are re-asserted inside every container
    # ---- launch, so they were driven in production and never censused.
    "so3ar_run_arm.sh:MD5_RUNSCRIPT":         ("LOCAL", "so3ar_runScript.py"),
    "so3ar_run_arm.sh:MD5_XF":                ("LOCAL", "so3ar_xf.py"),
    "so3ar_run_arm.sh:MD5_DECOMP":            ("LOCAL", "so3ar_decomposeParDict"),
    # ---- THE PIN THAT KILLED SO-3a.  A python constant, in a file the census
    # ---- did not read, holding a value the census's shape rule could not see.
    "so3ar_xf.py:PRODUCER_MD5":               ("LOCAL", "so3ar_runScript.py"),
    # ---- the comparator's libidwarp.so pins, per row.  These name a shared
    # ---- object INSIDE the image; the host has no copy, and G9 compares them
    # ---- against the value the CONTAINER prints into its own log.
    "so3ar_grade.py:SO_MD5[SHIPPED]":         ("CONTAINER", "libidwarp.so @ SHIPPED image"),
    "so3ar_grade.py:SO_MD5[PATCHED]":         ("CONTAINER", "libidwarp.so @ PATCHED image"),
    # ---- image digests: sha256, not md5, and an image is not a file ---------
    "so3ar_grade.py:IMG_DIGEST[SHIPPED]":     ("DIGEST", "dafoam/opt-packages SHIPPED image"),
    "so3ar_grade.py:IMG_DIGEST[PATCHED]":     ("DIGEST", "dafoam/opt-packages PATCHED image"),
    "so3ar_run_arm.sh:IMG_SHIPPED_DIGEST":    ("DIGEST", "dafoam/opt-packages SHIPPED image"),
    "so3ar_run_arm.sh:IMG_PATCHED_DIGEST":    ("DIGEST", "dafoam/opt-packages PATCHED image"),
}

# A pin whose in-repo file is STAGED into the run root under a DIFFERENT name.
# `so3ar_decomposeParDict` is copied to `base/system/decomposeParDict` because
# OpenFOAM requires that name; the bytes are identical and the pin is the same
# pin.  Registered here so A6 can accept the alias EXPLICITLY -- an unregistered
# name mismatch stays RED, which is the point of A6.
STAGED_AS = {
    "so3ar_decomposeParDict": ["decomposeParDict"],
}

PLANT = "PLANTED-CENSUS-CONTROL-NOT-AN-MD5"


# ===========================================================================
# extraction
# ===========================================================================
def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _shell_assignments(text):
    """Top-level `NAME=value` in shell.  Value is taken up to whitespace, so a
    trailing `# comment` is not swallowed.  Quotes are stripped."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(\S*)", line)
        if not m:
            continue
        val = m.group(2).strip("\"'")
        out.append((m.group(1), val, i))
    return out


def _python_assignments(text, path):
    """Module-level `NAME = "value"` and `NAME = {"k": "v", ...}` via ast, so a
    value inside a comment or a docstring can never be mistaken for a pin."""
    out = []
    tree = ast.parse(text, filename=path)
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Name):
            continue
        v = node.value
        if isinstance(v, ast.Constant) and isinstance(v.value, str):
            out.append((tgt.id, v.value, node.lineno))
        elif isinstance(v, ast.Dict):
            for k, dv in zip(v.keys, v.values):
                if (isinstance(k, ast.Constant) and isinstance(k.value, str)
                        and isinstance(dv, ast.Constant) and isinstance(dv.value, str)):
                    out.append(("%s[%s]" % (tgt.id, k.value), dv.value, dv.lineno))
    return out


def enumerate_pins(sources_text):
    """Return {pin_id: (value, file, line, [enumerators])}.

    E-NAME: identifier carries the token MD5 (any case).  VALUE SHAPE IGNORED.
    E-SHAPE: value is a bare 32/64-hex (optionally `sha256:`) literal.
             IDENTIFIER IGNORED.
    """
    pins = {}
    for fname, text in sources_text.items():
        if fname.endswith(".sh"):
            assigns = _shell_assignments(text)
        else:
            assigns = _python_assignments(text, fname)
        for name, value, line in assigns:
            enums = []
            base = name.split("[")[0]
            if "md5" in base.lower():
                enums.append("E-NAME")
            if HEX32_RE.match(value) or HEX64_RE.match(value):
                enums.append("E-SHAPE")
            if not enums:
                continue
            pins["%s:%s" % (fname, name)] = (value, fname, line, enums)
    return pins


SH_CHECKFILE_RE = re.compile(r'echo\s+"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?  ([^"]+)"')


def shell_var_map(text):
    """Every top-level `NAME=value` in one shell file, so a checkfile target
    written as `$LAUNCHER` can be resolved to the path it actually names.  A6
    compares the census's registered target against the CODE's target, and a
    comparison that cannot resolve a variable would report drift on every
    correct site -- which it did, on eight of them, the first time this ran."""
    m = {}
    for name, value, _ln in _shell_assignments(text):
        m.setdefault(name, value)
    return m


def expand_shell(expr, varmap, rounds=6):
    """Resolve `$VAR`, `${VAR}` and `${VAR:-default}` against one file's own
    assignment map.  This is a RESOLVER, not a shell: it is used only to answer
    "which file does this checkfile line name?", and where it cannot resolve, A6
    compares against the unresolved text and says so rather than passing."""
    for _ in range(rounds):
        new = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*):-([^}]*)\}",
                     lambda mm: varmap.get(mm.group(1)) or mm.group(2), expr)
        new = re.sub(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?",
                     lambda mm: varmap.get(mm.group(1), mm.group(0)), new)
        if new == expr:
            break
        expr = new
    return expr


SH_REF_RE = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?")


def shell_consumers(sources_text):
    """TWO shell site kinds, and they answer two different questions.

    CHECKFILE sites -- `echo "$VAR  <path>"` inside a file that runs
    `md5sum -c`, which is md5sum's OWN checkfile format (digest, two spaces,
    path).  That is a FORMAT rule about the CONSUMER, never a shape rule about
    a value, so a pin holding a sentinel is caught here exactly as a real one
    is.  These feed A5 (an unpinned consumer) and A6 (table-versus-code).

    REFERENCE sites -- any `$VAR` interpolation of a name in the pin set.
    These feed A4 (liveness) only.  A pin can be consumed by something that is
    not a checkfile -- the image digests are compared inside a `case`
    statement -- and calling such a pin dead would be a census reporting a
    defect that is an artefact of its own rule set, which is the exact error
    this whole file exists to answer."""
    check, refs = [], []
    for fname, text in sources_text.items():
        if not fname.endswith(".sh"):
            continue
        vm = shell_var_map(text)
        if "md5sum -c" in text:
            for m in SH_CHECKFILE_RE.finditer(text):
                line = text[:m.start()].count("\n") + 1
                check.append({"file": fname, "line": line, "var": m.group(1),
                              "target_expr": m.group(2).strip(),
                              "target_resolved": expand_shell(m.group(2).strip(), vm)})
        for m in SH_REF_RE.finditer(text):
            line = text[:m.start()].count("\n") + 1
            refs.append({"file": fname, "line": line, "var": m.group(1)})
    return check, refs


def _is_hash_expr(node, hash_names):
    if isinstance(node, ast.Name) and node.id in hash_names:
        return True
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Name) and f.id == "md5_of":
            return True
        if isinstance(f, ast.Attribute) and f.attr in ("hexdigest",):
            return True
        if isinstance(f, ast.Attribute) and f.attr == "md5":
            return True
    return False


def _pin_id_of(node, fname):
    if isinstance(node, ast.Name):
        return "%s:%s" % (fname, node.id)
    if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)):
        s = node.slice
        if isinstance(s, ast.Constant) and isinstance(s.value, str):
            return "%s:%s[%s]" % (fname, node.value.id, s.value)
        return "%s:%s[*]" % (fname, node.value.id)
    return None


def python_consumers(sources_text, pin_ids):
    """A python CONSUMER SITE is an `==`/`!=` comparison in which one operand
    is a pin (a Name, or a subscript of a Name) OR a hash expression.

    A subscript with a NON-CONSTANT key -- `SO_MD5[row]` -- consumes EVERY key
    of that dict, and is expanded to all of them.  Reading it as one pin id
    `SO_MD5[*]` and finding no match is how the first run of this file called
    four live pins dead.

    A hash compared against a MODULE-LEVEL name/subscript that is not a pin, or
    against a bare string LITERAL, is an UNPINNED CONSUMER (A5).  A hash
    compared against a LOCAL variable is a runtime-to-runtime comparison, not a
    pin site, and is recorded as informational -- this census's own reader is
    full of them."""
    sites = []
    for fname, text in sources_text.items():
        if not fname.endswith(".py"):
            continue
        tree = ast.parse(text, filename=fname)
        modlevel = set()
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        modlevel.add(t.id)
        hash_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) \
                    and _is_hash_expr(node.value, set()):
                hash_names.add(node.targets[0].id)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare) or len(node.ops) != 1:
                continue
            if not isinstance(node.ops[0], (ast.Eq, ast.NotEq)):
                continue
            left, right = node.left, node.comparators[0]
            for a, b in ((left, right), (right, left)):
                pid = _pin_id_of(a, fname)
                if pid and pid.endswith("[*]"):
                    stem = pid[:-3]
                    hit = [p for p in pin_ids if p.startswith(stem + "[")]
                    for p in hit:
                        sites.append({"file": fname, "line": node.lineno,
                                      "pin": p, "kind": "pin-operand-any-key"})
                    if hit:
                        continue
                if pid in pin_ids:
                    sites.append({"file": fname, "line": node.lineno,
                                  "pid_": pid, "pin": pid, "kind": "pin-operand"})
                elif _is_hash_expr(a, hash_names):
                    other = _pin_id_of(b, fname)
                    base = other.split(":")[1].split("[")[0] if other else None
                    if isinstance(b, ast.Constant) and isinstance(b.value, str):
                        kind = "hash-vs-literal"
                    elif base is not None and base in modlevel:
                        kind = "hash-operand"
                    else:
                        kind = "hash-vs-local"
                    sites.append({"file": fname, "line": node.lineno,
                                  "pin": other, "kind": kind})
    return sites


# ===========================================================================
# the census
# ===========================================================================
def read_sources(root):
    text = {}
    for f in SOURCES:
        p = os.path.join(root, f)
        if not os.path.isfile(p):
            raise IOError("source absent: %s" % p)
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            text[f] = fh.read()
    return text


def _perturb(value):
    """A value-changing perturbation that PRESERVES the enumerator class, so a
    pin found by E-SHAPE alone is still found after the plant and its NEW value
    can be read back.  The first plant I wrote replaced every value with a
    non-hex sentinel, which made the shape-enumerated pins VANISH from the
    reading -- the reader was working and my expectation was wrong, and a
    control whose expected reading is wrong is worse than none.  Recorded here
    rather than quietly corrected."""
    pre = "sha256:" if value.startswith("sha256:") else ""
    body = value[len(pre):]
    if re.match(r"^[0-9a-f]{32}$|^[0-9a-f]{64}$", body):
        first = "1" if body[0] != "1" else "0"
        return pre + first + body[1:]
    return value + "-P1"


def planted_control(sources_text):
    """RULE 3, ON THE CENSUS'S OWN READER.  For EVERY enumerated pin, plant a
    known perturbation into an in-memory copy of its source line, re-run the
    extractor, and require the extractor to read back EXACTLY the perturbed
    value.  A pin the extractor cannot be made to move is a pin it is not
    really reading, and the census REFUSES (exit 2) rather than reporting a
    zero.  A zero from a reader not shown able to see a non-zero is not
    evidence."""
    base = enumerate_pins(sources_text)
    report = []

    # ---- LIMB C1: PERTURB EVERY PIN THE EXTRACTOR ALREADY REPORTS ----------
    for pid in sorted(base):
        val, fname, line, _e = base[pid]
        want = _perturb(val)
        lines = sources_text[fname].splitlines(True)
        if not val:
            report.append((fname, "C1 " + pid, False, "pin value empty; nothing to plant"))
            continue
        planted = "".join(
            (ln.replace(val, want) if i == line - 1 else ln)
            for i, ln in enumerate(lines))
        if planted == sources_text[fname]:
            report.append((fname, "C1 " + pid, False, "plant did not change the text"))
            continue
        got = enumerate_pins({fname: planted}).get(pid, (None,))[0]
        report.append((fname, "C1 " + pid, got == want,
                       "planted %r, extractor read %r" % (want, got)))

    # ---- LIMB C2: INJECT A PIN INTO EVERY SOURCE AND REQUIRE IT FOUND ------
    # C1 ALONE IS BLIND IN EXACTLY THE WAY SO-3a's CENSUS WAS BLIND, and this
    # limb exists because leg (p4) caught it: a control that enumerates its
    # subjects FROM THE READER UNDER TEST cannot detect a reader that sees
    # NOTHING.  Blind the python extractor and C1 simply has no python pins to
    # perturb, reports every shell plant SEEN, and passes.
    #
    # C2 is an INDEPENDENT KNOWN POSITIVE: a pin this file writes itself, into
    # a source whose current pin count may be zero, which the extractor MUST
    # then report.  It proves the extractor can see a pin in THAT FILE AT ALL.
    for fname in sorted(sources_text):
        inj = "MD5_CENSUS_INJECTED_CONTROL"
        if fname.endswith(".sh"):
            text = sources_text[fname] + "\n%s=%s\n" % (inj, "0" * 32)
        else:
            text = sources_text[fname] + "\n%s = \"%s\"\n" % (inj, "0" * 32)
        try:
            got = enumerate_pins({fname: text}).get("%s:%s" % (fname, inj), (None,))[0]
        except SyntaxError as exc:
            report.append((fname, "C2 injected-pin", False,
                           "source did not parse after injection: %r" % (exc,)))
            continue
        report.append((fname, "C2 injected-pin", got == "0" * 32,
                       "injected a known pin, extractor read %r" % (got,)))
    return report


def run(root, tut_src_override=None):
    fail = []
    out = []

    def say(s):
        out.append(s)

    sources_text = read_sources(root)

    # ---- A0: the swept list is complete against the directory --------------
    present = sorted(f for f in os.listdir(root)
                     if f.startswith("so3ar_") and not f.endswith(".json")
                     and not f.endswith(".md") and not f.endswith(".txt")
                     and os.path.isfile(os.path.join(root, f)))
    unswept = [f for f in present if f not in SOURCES and f not in SOURCES_EXCLUDED]
    say("A0 SOURCES swept=%d excluded=%d unclassified=%d"
        % (len(SOURCES), len(SOURCES_EXCLUDED), len(unswept)))
    for f in unswept:
        fail.append("A0 UNCLASSIFIED SOURCE %s -- an instrument file joined the "
                    "item without joining the census" % f)

    # ---- RULE 3 planted control, BEFORE any assertion is believed ----------
    ctrl = planted_control(sources_text)
    blind = [r for r in ctrl if not r[2]]
    for fname, pid, seen, note in ctrl:
        say("  PLANT %-28s %-46s %s  (%s)"
            % (fname, pid, "SEEN" if seen else "NOT SEEN", note))
    if blind:
        say("REFUSE the census's own extractor could not see a planted change "
            "in %d source(s); a zero from a blind reader is not evidence"
            % len(blind))
        return 2, out

    pins = enumerate_pins(sources_text)
    pin_ids = set(pins)
    sh_sites, sh_refs = shell_consumers(sources_text)
    py_sites = python_consumers(sources_text, pin_ids)

    say("ENUMERATED %d pin-like constants across %d sources "
        "(E-NAME %d, E-SHAPE %d, both %d)"
        % (len(pins), len(SOURCES),
           sum(1 for v in pins.values() if "E-NAME" in v[3]),
           sum(1 for v in pins.values() if "E-SHAPE" in v[3]),
           sum(1 for v in pins.values() if len(v[3]) == 2)))
    say("CONSUMER SITES shell-checkfile=%d shell-reference=%d python=%d"
        % (len(sh_sites), len(sh_refs), len(py_sites)))

    # TUT_SRC read out of the driver's OWN BYTES
    tut_src = tut_src_override
    if tut_src is None:
        m = re.search(r"^TUT_SRC=(\S+)", sources_text["so3ar_chain_driver.sh"], re.M)
        tut_src = m.group(1).strip("\"'") if m else None
    say("TUT_SRC (read from so3ar_chain_driver.sh, not hard-coded) = %s" % tut_src)

    # ---- consumption index --------------------------------------------------
    consumed = {}
    for s in sh_sites + sh_refs:
        pid = "%s:%s" % (s["file"], s["var"])
        consumed.setdefault(pid, []).append(s)
    for s in py_sites:
        if s["pin"] and s["kind"].startswith("pin-operand"):
            consumed.setdefault(s["pin"], []).append(s)

    # ---- A1 / A2 / A3 -------------------------------------------------------
    say("")
    say("%-42s %-9s %-34s %s" % ("PIN", "KIND", "VALUE", "DISPOSITION"))
    for pid in sorted(pins):
        value, fname, line, enums = pins[pid]
        row = DISPOSITION.get(pid)
        if row is None:
            fail.append("A1 NO DISPOSITION for %s = %r (%s:%d, found by %s) -- a "
                        "pin was added and the census was not told what it pins"
                        % (pid, value, fname, line, "+".join(enums)))
            say("%-42s %-9s %-34s %s" % (pid, "?", value[:34], "*** NO DISPOSITION ***"))
            continue
        kind, target = row
        note = ""
        if kind in ("LOCAL", "TUTORIAL", "CONTAINER"):
            if not MD5_RE.match(value):
                fail.append("A2 NOT AN MD5: %s = %r at %s:%d -- a pin of kind %s "
                            "must hold 32 lowercase hex.  THIS IS THE ASSERTION "
                            "SO-3a's SHAPE-KEYED CENSUS COULD NOT MAKE."
                            % (pid, value, fname, line, kind))
                note = "*** NOT AN MD5 ***"
        if kind == "LOCAL":
            p = os.path.join(root, target)
            if not os.path.isfile(p):
                fail.append("A3 TARGET ABSENT: %s pins %s which does not exist"
                            % (pid, target))
                note = note or "*** TARGET ABSENT ***"
            else:
                actual = md5_of(p)
                if actual != value:
                    fail.append("A3 STALE PIN: %s = %s but md5(%s) = %s"
                                % (pid, value, target, actual))
                    note = note or "*** STALE ***"
                else:
                    note = note or "= md5(%s)" % target
        elif kind == "TUTORIAL":
            p = os.path.join(tut_src or "/nonexistent", target)
            if not os.path.isfile(p):
                fail.append("A3 TUTORIAL TARGET ABSENT: %s pins %s under %s"
                            % (pid, target, tut_src))
                note = note or "*** TARGET ABSENT ***"
            else:
                actual = md5_of(p)
                if actual != value:
                    fail.append("A3 STALE TUTORIAL PIN: %s = %s but md5 = %s"
                                % (pid, value, actual))
                    note = note or "*** STALE ***"
                else:
                    note = note or "= md5(TUT_SRC/%s)" % target
        elif kind == "CONTAINER":
            note = note or "NOT LOCALLY RESOLVABLE -- %s; verified only by G9 " \
                           "against the value the container prints" % target
        elif kind == "DIGEST":
            if not HEX64_RE.match(value):
                fail.append("A2 NOT A SHA256 DIGEST: %s = %r at %s:%d"
                            % (pid, value, fname, line))
                note = "*** NOT A DIGEST ***"
            note = note or "NAMED EXCLUSION from A2/A3 -- a sha256 image " \
                           "digest is not an md5 and an image is not a file"
        say("%-42s %-9s %-34s %s" % (pid, kind, value[:34], note))

    # ---- A4 dead pins -------------------------------------------------------
    say("")
    for pid in sorted(pins):
        if pid not in consumed:
            fail.append("A4 DEAD PIN: %s is declared and no site consumes it -- "
                        "a dead pin is one edit from fail-open re-use" % pid)
    say("A4 dead pins: %d" % sum(1 for p in pins if p not in consumed))

    # ---- A5 unpinned consumers ---------------------------------------------
    unp = []
    for s in sh_sites:
        pid = "%s:%s" % (s["file"], s["var"])
        if pid not in pin_ids:
            unp.append("A5 UNPINNED SHELL CONSUMER at %s:%d -- `md5sum -c` reads "
                       "$%s, which is not a registered pin (target %s)"
                       % (s["file"], s["line"], s["var"], s["target_expr"]))
    for s in py_sites:
        if s["kind"] in ("hash-operand", "hash-vs-literal") \
                and (s["pin"] is None or s["pin"] not in pin_ids):
            unp.append("A5 UNPINNED PYTHON CONSUMER at %s:%d (%s) -- a hash is "
                       "compared against %s, which is not a registered pin"
                       % (s["file"], s["line"], s["kind"],
                          s["pin"] or "a string literal"))
    fail.extend(unp)
    say("A5 unpinned consumer sites: %d  (informational hash-vs-local "
        "comparisons, not pin sites: %d)"
        % (len(unp), sum(1 for s in py_sites if s["kind"] == "hash-vs-local")))

    # ---- A6 the table's target == the code's target ------------------------
    drift = 0
    for s in sh_sites:
        pid = "%s:%s" % (s["file"], s["var"])
        row = DISPOSITION.get(pid)
        if not row:
            continue
        kind, target = row
        base = os.path.basename(target)
        seen = s["target_resolved"]
        names = [base] + STAGED_AS.get(base, [])
        if kind in ("LOCAL", "TUTORIAL") and base and not any(n in seen for n in names):
            fail.append("A6 TARGET DRIFT: this census registers %s -> %s, but the "
                        "code at %s:%d hashes %s (resolved: %s)"
                        % (pid, target, s["file"], s["line"], s["target_expr"], seen))
            drift += 1
    say("A6 table-versus-code target drift: %d  (targets resolved through each "
        "file's own shell variable map, not by pattern)" % drift)

    # ---- A7 stale disposition rows -----------------------------------------
    stale = [k for k in DISPOSITION if k not in pin_ids]
    for k in stale:
        fail.append("A7 STALE DISPOSITION ROW: %s is registered here and exists "
                    "in no source -- the row is propping up a deleted pin" % k)
    say("A7 stale disposition rows: %d" % len(stale))

    say("")
    if fail:
        say("PIN CENSUS RED -- %d failure(s):" % len(fail))
        for f in fail:
            say("  " + f)
        return 1, out
    say("PIN CENSUS GREEN -- %d pin-like constants enumerated BY ROLE across %d "
        "sources; every one carries a registered disposition, every md5-kind pin "
        "holds a real md5, every resolvable pin EQUALS the file it pins, no pin "
        "is dead, no consumer is unpinned, no table row is stale, and the "
        "extractor was shown able to see a planted change in every source."
        % (len(pins), len(SOURCES)))
    return 0, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--tut-src", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        rc, out = run(a.root, a.tut_src)
    except Exception as exc:                                    # noqa: BLE001
        print("PIN CENSUS REFUSE -- %r" % (exc,))
        return 2
    if a.json:
        print(json.dumps({"rc": rc, "lines": out}, indent=1))
    else:
        for line in out:
            print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
