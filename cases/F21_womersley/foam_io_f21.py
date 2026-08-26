#!/usr/bin/env python3
"""F21 -- minimal reader/writer for OpenFOAM ascii volVectorField / volScalarField
files, used by build_f21.py (to write 0/U from the mesh's own 0/C) and by
grade_f21.py (to read U at every checkpoint).  Refusals are `raise`; zero
`assert` (L-332)."""
import re

import numpy as np

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


class FieldFormatError(Exception):
    pass


def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _parse_list(text, start, kind):
    """Parse `N ( ... )` beginning at text[start:], kind in ('vector','scalar').
    Returns (ndarray, end_index)."""
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


def read_field(path):
    """Return dict(kind, internal=ndarray, patches={name: ndarray|None|'uniform'}).
    Uniform internal fields are returned as a 1-row array with key uniform=True."""
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
    else:
        internal, pos = _parse_list(text, m.end(), kind)
        uniform = False
    patches = {}
    mb = re.search(r"boundaryField\s*\{", text[pos:])
    if mb:
        body = text[pos + mb.end():]
        for pm in re.finditer(r"(\w+)\s*\{([^{}]*)\}", body):
            name, inner = pm.group(1), pm.group(2)
            mv = re.search(r"value\s+nonuniform\s+List<(vector|scalar)>", inner)
            if mv:
                arr, _ = _parse_list(inner, mv.end(), kind)
                patches[name] = arr
            else:
                patches[name] = None
    return dict(kind=kind, internal=internal, uniform=uniform, patches=patches, path=path)


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
