#!/usr/bin/env python3
"""F25 -- minimal reader/writer for OpenFOAM ascii volVectorField / volScalarField
files (lineage: cases/F23_HP_WEDGE/foam_io_f23.py), used by build_f25.py (to
write 0/U from the mesh's own 0/C) and by grade_f25.py (to read U at every
checkpoint and 0/C, 0/V from the processor directories).

ONE ADDITION over F23: a FAST PATH for the internalField list (numpy
`fromstring` on the bracket-stripped list body) -- the fine level carries
2.1 M cells over 40 checkpoints and the per-entry regex path is too slow to
grade in a sitting.  The fast path is VERIFIED against the regex path at
selftest on the real solver-written file the format is pinned to and on a
synthetic file (grade_f25.control_reader_fast_path_equals_regex_path); it falls
back to the regex path whenever its entry count disagrees with the declared
N.  Refusals are `raise`; zero `assert` (L-332)."""
import re

import numpy as np

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_STRIP = str.maketrans({"(": " ", ")": " "})


class FieldFormatError(Exception):
    pass


def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _parse_list_regex(text, start, kind):
    """Parse `N ( ... )` beginning at text[start:], kind in ('vector','scalar').
    Returns (ndarray, end_index).  The entry-by-entry regex path."""
    m = re.compile(r"\s*(\d+)\s*\(", re.S).match(text, start)
    if not m:
        raise FieldFormatError("expected `N (` at offset %d" % start)
    n = int(m.group(1))
    pos = m.end()
    if kind == "vector":
        pat = re.compile(r"\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM))
        out = np.empty((n, 3))
        for k in range(n):
            mm = pat.match(text, pos)
            if not mm:
                raise FieldFormatError("vector list: bad entry %d of %d" % (k, n))
            out[k] = (float(mm.group(1)), float(mm.group(2)), float(mm.group(3)))
            pos = mm.end()
    else:
        pat = re.compile(r"\s*(%s)" % _NUM)
        out = np.empty(n)
        for k in range(n):
            mm = pat.match(text, pos)
            if not mm:
                raise FieldFormatError("scalar list: bad entry %d of %d" % (k, n))
            out[k] = float(mm.group(1))
            pos = mm.end()
    mm = re.compile(r"\s*\)").match(text, pos)
    if not mm:
        raise FieldFormatError("list of %d entries not closed" % n)
    return out, mm.end()


def _parse_list_fast(text, start, kind):
    """The fast path: the list body is the text between the opening `(` and the
    first `\\n)` after it (every entry sits on its own line, and an entry's own
    `)` is never preceded by a newline).  Returns (ndarray, end_index) or None
    when the entry count disagrees -- the caller then uses the regex path."""
    m = re.compile(r"\s*(\d+)\s*\(", re.S).match(text, start)
    if not m:
        return None
    n = int(m.group(1))
    pos = m.end()
    end = text.find("\n)", pos)
    if end < 0:
        return None
    body = text[pos:end]
    if kind == "vector":
        arr = np.fromstring(body.translate(_STRIP), sep=" ")
        if arr.size != 3 * n:
            return None
        arr = arr.reshape(n, 3)
    else:
        arr = np.fromstring(body, sep=" ")
        if arr.size != n:
            return None
    return arr, end + 2


def _parse_list(text, start, kind, fast=True):
    if fast:
        r = _parse_list_fast(text, start, kind)
        if r is not None:
            return r
    return _parse_list_regex(text, start, kind)


def read_field(path, fast=True):
    """Return dict(kind, internal=ndarray, uniform, uniform_value, patches={name: ndarray|None}).
    Uniform internal fields are returned with internal=None, uniform=True and
    their value in uniform_value (see scalar_field_values)."""
    text = _strip_comments(open(path).read())
    m = re.search(r"class\s+(volVectorField|volScalarField)\s*;", text)
    if not m:
        raise FieldFormatError("%s: no volVectorField/volScalarField class" % path)
    kind = "vector" if m.group(1) == "volVectorField" else "scalar"
    m = re.search(r"internalField\s+nonuniform\s+List<(vector|scalar)>", text)
    if not m:
        mu = re.search(r"internalField\s+uniform\s+", text)
        if not mu:
            raise FieldFormatError("%s: no internalField" % path)
        internal, uniform = None, True
        pos = mu.end()
        # OpenFOAM writes a field whose entries are all equal as `uniform <value>`
        # (a cubic mesh's 0/V is exactly that); carry the value so a caller with
        # the cell count can expand it.
        if kind == "vector":
            mv = re.compile(r"\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM)).match(text, pos)
            uniform_value = (float(mv.group(1)), float(mv.group(2)), float(mv.group(3))) if mv else None
        else:
            mv = re.compile(r"(%s)" % _NUM).match(text, pos)
            uniform_value = float(mv.group(1)) if mv else None
        if uniform_value is None:
            raise FieldFormatError("%s: uniform internalField without a readable value" % path)
    else:
        internal, pos = _parse_list(text, m.end(), kind, fast=fast)
        uniform, uniform_value = False, None
    patches = {}
    mb = re.search(r"boundaryField\s*\{", text[pos:])
    if mb:
        body = text[pos + mb.end():]
        for pm in re.finditer(r"(\w+)\s*\{([^{}]*)\}", body):
            name, inner = pm.group(1), pm.group(2)
            mv = re.search(r"value\s+nonuniform\s+List<(vector|scalar)>", inner)
            if mv:
                arr, _ = _parse_list(inner, mv.end(), kind, fast=fast)
                patches[name] = arr
            else:
                patches[name] = None
    return dict(kind=kind, internal=internal, uniform=uniform, uniform_value=uniform_value, patches=patches, path=path)


def scalar_field_values(path, n_cells):
    """A volScalarField's internal values as an array of length n_cells: a
    nonuniform list must carry exactly n_cells entries; a `uniform` field is
    expanded to n_cells copies of its value (a cubic mesh's 0/V)."""
    F = read_field(path)
    if F["kind"] != "scalar":
        raise FieldFormatError("%s is not a volScalarField" % path)
    if F["uniform"]:
        return np.full(n_cells, F["uniform_value"])
    if F["internal"].shape[0] != n_cells:
        raise FieldFormatError("%s carries %d entries, expected %d" % (path, F["internal"].shape[0], n_cells))
    return F["internal"]


def fmt_list(arr, kind):
    if kind == "vector":
        body = "\n".join("(%.17g %.17g %.17g)" % tuple(r) for r in arr)
    else:
        body = "\n".join("%.17g" % v for v in arr)
    return "%d\n(\n%s\n)" % (len(arr), body)


def write_from_template(template_path, out_path, replacements):
    text = open(template_path).read()
    for key, val in replacements.items():
        if key not in text:
            raise FieldFormatError("template %s lacks placeholder %s" % (template_path, key))
        text = text.replace(key, val)
    if "__" in re.sub(r"//[^\n]*", "", text):
        raise FieldFormatError("template %s still carries an unfilled placeholder" % template_path)
    open(out_path, "w").write(text)


def plant_into_vector_file(src, dst, comp, delta):
    """Copy an ascii volVectorField file adding `delta` to component `comp` of
    EVERY internalField entry, rewriting only that list.  Returns rows changed."""
    text = open(src).read()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*(\d+)\s*\(", text)
    if not m:
        raise FieldFormatError("%s: no nonuniform vector internalField to plant into" % src)
    n = int(m.group(1))
    pos = m.end()
    pat = re.compile(r"\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM))
    pieces = [text[:pos]]
    for k in range(n):
        mm = pat.match(text, pos)
        if not mm:
            raise FieldFormatError("plant: bad entry %d" % k)
        vals = [float(mm.group(1)), float(mm.group(2)), float(mm.group(3))]
        vals[comp] += delta
        pieces.append("\n(%.17g %.17g %.17g)" % tuple(vals))
        pos = mm.end()
    pieces.append(text[pos:])
    open(dst, "w").write("".join(pieces))
    return n
