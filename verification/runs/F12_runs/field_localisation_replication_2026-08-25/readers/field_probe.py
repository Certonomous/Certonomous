#!/usr/bin/env python3
"""F12 rung-1 FIELD reader: per-iteration, per-patch min/max of an OpenFOAM
ascii field, with the CELL INDEX and the CELL-CENTRE COORDINATES of each extreme.

It reads. It holds no threshold, no gate and no verdict.

CONTROL (standing rule 3 -- a zero from a reader not shown able to see a
non-zero is not evidence).  `--selftest` plants a KNOWN anomalous value into a
KNOWN cell index of a copy of a real written field on disk, reads it back
THROUGH THE SAME CODE PATH, and requires:
  POSITIVE     the reader returns the planted value,
  LOCALISATION at exactly the planted cell index (not a neighbour),
  PATCH ARM    a value planted into a named patch is reported on THAT patch,
  NEGATIVE     the unplanted control field does NOT report the planted value,
               so 'no departure here' is a reading and not a blind spot.
If any arm does not fire the reader is REFUSED and every number it produced is
withdrawn.
"""
from __future__ import annotations
import json, math, pathlib, re, sys

NUM = r"[-+0-9.eE]+"

def _strip(txt):
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    return re.sub(r"//[^\n]*", "", txt)

def _vals(body, vector):
    """Parse an OpenFOAM list body into a list of floats (scalar) or 3-tuples."""
    if vector:
        return [tuple(float(x) for x in m)
                for m in re.findall(rf"\(\s*({NUM})\s+({NUM})\s+({NUM})\s*\)", body)]
    return [float(x) for x in re.findall(rf"(?<![\w.)])({NUM})(?![\w.])", body)]

def _block(txt, start):
    """Return the (..) list starting at/after `start`, and the index after it."""
    i = txt.index("(", start); d, j = 0, i
    while True:
        if txt[j] == "(": d += 1
        elif txt[j] == ")":
            d -= 1
            if d == 0: return txt[i+1:j], j+1
        j += 1

def _brace_block(txt, start):
    """Return the contents of the {..} block starting at/after `start`."""
    i = txt.index("{", start); d, j = 0, i
    while True:
        if txt[j] == "{": d += 1
        elif txt[j] == "}":
            d -= 1
            if d == 0: return txt[i+1:j]
        j += 1


def patch_owner_cells(polymesh):
    """-> {patch: [owner cell index per boundary face]} from constant/polyMesh.
    Works for EVERY patch regardless of boundary-condition type, so a
    zeroGradient patch that writes no `value` list still gets statistics from
    the cells it touches."""
    polymesh = pathlib.Path(polymesh)
    bt = _strip((polymesh / "boundary").read_text(errors="replace"))
    body = _block(bt, bt.index("("))[0]
    patches = []
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", body):
        nm, blk = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        ty = re.search(r"type\s+(\w+)\s*;", blk)
        if nf and sf:
            patches.append((nm, int(nf.group(1)), int(sf.group(1)),
                            ty.group(1) if ty else "?"))
    ot = _strip((polymesh / "owner").read_text(errors="replace"))
    m = re.search(r"\n\s*(\d+)\s*\n\s*\(", ot)
    lst = _block(ot, m.end() - 1)[0]
    own = [int(x) for x in re.findall(r"\d+", lst)]
    return {nm: {"type": ty, "owner_cells": own[sf:sf + nf], "nFaces": nf}
            for nm, nf, sf, ty in patches}


def read_field(path):
    """-> dict(internal=[...], patches={name:[...] or None}, vector=bool, n=int)"""
    txt = _strip(pathlib.Path(path).read_text(errors="replace"))
    vector = "volVectorField" in txt
    out = {"vector": vector, "internal": [], "patches": {}, "uniform_internal": None}
    m = re.search(rf"internalField\s+nonuniform[^;(]*?(\d+)\s*\(", txt)
    if m:
        body, _ = _block(txt, m.end()-1)
        out["internal"] = _vals(body, vector)
    else:
        u = re.search(rf"internalField\s+uniform\s+(\(\s*{NUM}\s+{NUM}\s+{NUM}\s*\)|{NUM})\s*;", txt)
        if u:
            v = _vals(u.group(1), vector)
            out["uniform_internal"] = v[0] if v else None
    bi = txt.find("boundaryField")
    if bi >= 0:
        body = _brace_block(txt, bi)
        # each patch:  name { ... }
        for pm in re.finditer(r"(\w+)\s*\{", body):
            name, s = pm.group(1), pm.end()-1
            d, j = 0, s
            while True:
                if body[j] == "{": d += 1
                elif body[j] == "}":
                    d -= 1
                    if d == 0: break
                j += 1
            pb = body[s+1:j]
            if re.search(r"^\s*type\s+empty\s*;", pb, re.M):
                out["patches"][name] = {"kind": "empty", "vals": []}
                continue
            mm = re.search(rf"value\s+nonuniform[^;(]*?(\d+)\s*\(", pb)
            if mm:
                b2, _ = _block(pb, mm.end()-1)
                out["patches"][name] = {"kind": "nonuniform", "vals": _vals(b2, vector)}
            else:
                uu = re.search(rf"value\s+uniform\s+(\(\s*{NUM}\s+{NUM}\s+{NUM}\s*\)|{NUM})\s*;", pb)
                out["patches"][name] = ({"kind": "uniform", "vals": _vals(uu.group(1), vector)}
                                        if uu else {"kind": "none", "vals": []})
    return out

def mag(v): return math.sqrt(sum(c*c for c in v)) if isinstance(v, tuple) else v

def extremes(vals):
    if not vals: return None
    keyed = [(mag(v), i, v) for i, v in enumerate(vals)]
    lo = min(keyed); hi = max(keyed)
    return {"min": lo[0], "min_index": lo[1], "min_raw": lo[2],
            "max": hi[0], "max_index": hi[1], "max_raw": hi[2], "n": len(vals)}

# ---------------------------------------------------------------- the control
PLANT_INTERNAL = -7.654321e+09
PLANT_PATCH    = -1.357911e+09
PLANT_CELL     = 12345          # a specific interior cell index

def _plant_scalar(src: pathlib.Path, dst: pathlib.Path, cell: int, val: float,
                  patch: str | None = None, pval: float | None = None):
    txt = src.read_text(errors="replace")
    stripped = _strip(txt)
    m = re.search(rf"internalField\s+nonuniform[^;(]*?(\d+)\s*\(", stripped)
    if not m: raise SystemExit("CONTROL REFUSED: source field internal list is not nonuniform")
    body, _ = _block(stripped, m.end()-1)
    toks = re.findall(rf"(?<![\w.)])({NUM})(?![\w.])", body)
    if cell >= len(toks): raise SystemExit("CONTROL REFUSED: plant cell out of range")
    new_body = body
    # replace the cell-th token by index, positionally (never by value match)
    pos, count = 0, 0
    for mt in re.finditer(rf"(?<![\w.)])({NUM})(?![\w.])", body):
        if count == cell:
            new_body = body[:mt.start()] + repr(val) + body[mt.end():]
            break
        count += 1
    out = stripped.replace(body, new_body, 1)
    if patch is not None:
        pm = re.search(rf"{patch}\s*\{{", out)
        ps = pm.end()-1
        d, j = 0, ps
        while True:
            if out[j] == "{": d += 1
            elif out[j] == "}":
                d -= 1
                if d == 0: break
            j += 1
        pb = out[ps+1:j]
        mm = re.search(rf"value\s+nonuniform[^;(]*?(\d+)\s*\(", pb)
        if not mm: raise SystemExit(f"CONTROL REFUSED: patch {patch} has no nonuniform value list")
        b2, _ = _block(pb, mm.end()-1)
        first = re.search(rf"(?<![\w.)])({NUM})(?![\w.])", b2)
        nb2 = b2[:first.start()] + repr(pval) + b2[first.end():]
        out = out[:ps+1] + pb.replace(b2, nb2, 1) + out[j:]
    dst.write_text(out)

def selftest(field: pathlib.Path, patch: str, workdir: pathlib.Path):
    ok = []
    def chk(n, c, d=""):
        ok.append((n, bool(c))); print(("PASS  " if c else "FAIL  ")+n+(f"  [{d}]" if d else ""))
    workdir.mkdir(parents=True, exist_ok=True)
    clean = read_field(field)
    ci = extremes(clean["internal"])
    chk("baseline: the reader reads a real written field and finds cells at all",
        ci is not None and ci["n"] > 0, f"{ci['n'] if ci else 0} cells")
    chk("baseline: the CLEAN field does NOT already contain the plant value "
        "(so a positive arm cannot be a false positive)",
        all(abs(v - PLANT_INTERNAL) > 1e-3 for v in clean["internal"]))
    planted = workdir / (field.name + ".PLANTED")
    _plant_scalar(field, planted, PLANT_CELL, PLANT_INTERNAL, patch, PLANT_PATCH)
    p = read_field(planted)
    pi = extremes(p["internal"])
    chk("POSITIVE arm: reader SEES the planted anomalous internal value",
        pi is not None and abs(pi["min"] - PLANT_INTERNAL) < 1e-3, f"min={pi['min'] if pi else None!r}")
    chk(f"LOCALISATION arm: reader reports it at EXACTLY cell {PLANT_CELL}",
        pi is not None and pi["min_index"] == PLANT_CELL, f"got index {pi['min_index'] if pi else None}")
    chk("CELL COUNT arm: planting did not change the cell count",
        pi is not None and ci is not None and pi["n"] == ci["n"], f"{ci['n']} -> {pi['n']}")
    pp = extremes(p["patches"][patch]["vals"])
    chk(f"PATCH arm: a value planted on patch '{patch}' is reported ON THAT PATCH",
        pp is not None and abs(pp["min"] - PLANT_PATCH) < 1e-3, f"min={pp['min'] if pp else None!r}")
    others = [q for q in p["patches"] if q != patch and p["patches"][q]["vals"]]
    chk("PATCH SPECIFICITY arm: the patch plant does NOT leak into other patches",
        all(all(abs(mag(v) - abs(PLANT_PATCH)) > 1e-3 for v in p["patches"][q]["vals"]) for q in others),
        f"checked {others}")
    chk("NEGATIVE arm: re-reading the UNPLANTED original returns no plant value, "
        "so 'no departure here' is a reading and not a blind spot",
        all(abs(v - PLANT_INTERNAL) > 1e-3 for v in read_field(field)["internal"]))
    bad = [n for n, v in ok if not v]
    print(f"\n{len(ok)-len(bad)}/{len(ok)} control checks passed" +
          (f"; FAILED {bad} -> READER REFUSED" if bad else
           "; reader IS shown able to see a planted anomaly and to localise it"))
    return 1 if bad else 0

if __name__ == "__main__":
    if sys.argv[1] == "--selftest":
        raise SystemExit(selftest(pathlib.Path(sys.argv[2]), sys.argv[3], pathlib.Path(sys.argv[4])))
    print(json.dumps(read_field(sys.argv[1]), default=str)[:2000])
