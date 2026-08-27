"""
M1 multi-model sweep -- STAGING.

Stages 2 arms x 39 Closure Challenge benchmark cases into
/home/ubuntu/closure-data/multimodel_sweep/<ARM>/<CASE_ID>/ as `0.orig/` with
NO `0/` and NO numeric time directory, per PREREGISTRATION.md section 5.

THIS SCRIPT LAUNCHES NOTHING.  It copies files.  Its DEFAULT IS A DRY RUN:
nothing is written without an explicit --execute.

Every refusal is `raise Refusal` / `sys.exit(2)` and NEVER an `assert`
(L-332: `python3 -O` deletes assertions, and a refusal that vanishes under an
optimiser flag is not a refusal).  --selftest is designed to be run under
`python3 -O` with every refusal still firing, and it ships a planted-failure
proof for every guard (L-314): the guard is mutated to a no-op and the control
must flip.

Usage
  python3 stage_m1.py                         # dry run, all arms, all cases
  python3 stage_m1.py --case CBFS --arm kOmega
  python3 stage_m1.py --execute               # actually stage
  python3 -O stage_m1.py --selftest           # guards + planted-failure proofs
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS -- these are frozen by PREREGISTRATION.md and must not
# be changed without a dated addendum (standing rule 2, rule 6).
# --------------------------------------------------------------------------
SRC_ROOT_DEFAULT = "/home/ubuntu/closure-challenge-benchmark/data"
DST_ROOT_DEFAULT = "/home/ubuntu/closure-data/multimodel_sweep"

ARMS = {
    "kOmegaSST_null": "kOmegaSST",   # the sweep's planted control
    "kOmega":         "kOmega",      # the substitute closure
}
SOURCE_MODEL = "kOmegaSST"           # the only model an includable case may name
NUT_IC_REQUIRED = "uniform 0"        # the control that excluded NASA_2DWMH

CAP_ITER = 20000                     # PREREGISTRATION.md section 3
ORIG_FIELDS = ("U", "p", "k", "omega", "nut")     # exactly these five
DROP_FROM_CONSTANT = ("C", "Cx", "Cy", "Cz", "V")  # section 5.4, uniform policy
AGE_DATUM = "U"                      # 0/U is the registered age datum
ROOT_FILES = ("caseDef", "fieldDef")  # staged when present; see section 5.5
PLANT_CANDIDATES = ("nut", "U")       # 0.orig fields the rule-3 plant may use

PLANT = 1.234e-03                    # standing rule 3 planted-zero perturbation

CONTROLDICT_PATCH = [
    ("application",    "simpleFoam"),
    ("startFrom",      "startTime"),
    ("startTime",      "0"),
    ("stopAt",         "endTime"),
    ("endTime",        str(CAP_ITER)),
    ("deltaT",         "1"),
    ("writeControl",   "timeStep"),
    ("writeInterval",  str(CAP_ITER)),
    ("purgeWrite",     "0"),
    ("writeFormat",    "ascii"),
    ("writePrecision", "15"),
]
MANIFEST_NAME = "STAGING_MANIFEST_M1.json"

TIME_DIR_RE = re.compile(r"^[0-9]+(\.[0-9]+)?$")


class Refusal(Exception):
    """Every guard raises this.  Never an assert (L-332)."""

    def __init__(self, code, msg):
        super().__init__(f"REFUSE [{code}]: {msg}")
        self.code = code


def refuse(code, msg):
    raise Refusal(code, msg)


# --------------------------------------------------------------------------
# OpenFOAM ascii field reader.  Duplicated verbatim in grade_m1.py ON PURPOSE:
# each instrument carries its own reader and its own planted-zero control, so a
# divergence between the two is detectable rather than shared.
# --------------------------------------------------------------------------
def read_internal_field(path):
    """Return dict(kind, rank, n, values) for an OpenFOAM ascii vol*Field.

    values is a FLAT list of floats (vectors flattened component-major).
    Raises Refusal if the internalField cannot be located or parsed.
    """
    if not os.path.isfile(path):
        refuse("FIELD-MISSING", f"no field file at {path}")
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"^\s*internalField\s+(uniform|nonuniform)", txt, re.M)
    if not m:
        refuse("FIELD-PARSE", f"no internalField entry in {path}")
    if m.group(1) == "uniform":
        tail = txt[m.end():]
        stop = tail.find(";")
        if stop < 0:
            refuse("FIELD-PARSE", f"unterminated uniform internalField in {path}")
        body = tail[:stop].strip()
        if body.startswith("("):
            comps = [float(x) for x in body.strip("()").split()]
            return dict(kind="uniform", rank=len(comps), n=1, values=comps)
        try:
            return dict(kind="uniform", rank=1, n=1, values=[float(body)])
        except ValueError:
            refuse("FIELD-PARSE", f"uniform internalField is not numeric in {path}: {body!r}")
    # nonuniform
    m2 = re.search(r"List<(\w+)>\s*\n?\s*(\d+)\s*\n?\s*\(", txt[m.start():])
    if not m2:
        refuse("FIELD-PARSE", f"cannot locate nonuniform List header in {path}")
    rank = {"scalar": 1, "vector": 3, "symmTensor": 6, "tensor": 9}.get(m2.group(1))
    if rank is None:
        refuse("FIELD-PARSE", f"unsupported List type {m2.group(1)} in {path}")
    n = int(m2.group(2))
    start = m.start() + m2.end()
    depth = 1
    i = start
    while i < len(txt) and depth > 0:
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    if depth != 0:
        refuse("FIELD-PARSE", f"unbalanced parentheses in {path}")
    body = txt[start:i].replace("(", " ").replace(")", " ")
    vals = [float(x) for x in body.split()]
    if len(vals) != n * rank:
        refuse("FIELD-PARSE",
               f"{path}: header says {n} entries of rank {rank} = {n * rank} "
               f"numbers, found {len(vals)}")
    return dict(kind="nonuniform", rank=rank, n=n, values=vals)


def plant_into_field(path, plant=PLANT):
    """Add `plant` to the FIRST numeric token of the internal field, IN PLACE in
    the file ON DISK, then re-open the file and prove the plant landed.

    An in-memory plant does NOT satisfy standing rule 3 and is not used.
    """
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"^\s*internalField\s+(uniform|nonuniform)", txt, re.M)
    if not m:
        refuse("PLANT", f"no internalField in {path}")
    if m.group(1) == "uniform":
        anchor = m.end()
    else:
        m2 = re.search(r"List<\w+>\s*\n?\s*\d+\s*\n?\s*\(", txt[m.start():])
        if not m2:
            refuse("PLANT", f"cannot locate nonuniform data in {path}")
        anchor = m.start() + m2.end()
    mnum = re.compile(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?").search(txt, anchor)
    if not mnum:
        refuse("PLANT", f"no numeric token after the internalField header in {path}")
    before = float(mnum.group(0))
    after = before + plant
    txt2 = txt[:mnum.start()] + repr(after) + txt[mnum.end():]
    open(path, "w").write(txt2)
    # RE-OPEN FROM DISK.  A value held in memory proves nothing.
    back = re.compile(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?").search(
        open(path, "r", errors="replace").read(), anchor)
    if back is None or abs((float(back.group(0)) - before) - plant) > 1e-12:
        refuse("PLANT", f"the plant did not land in {path}: {before} -> "
                        f"{back.group(0) if back else None}")
    return before, float(back.group(0))


def planted_zero_control(field_path, workdir):
    """Copy `field_path`, plant PLANT into the COPY ON DISK, re-read BOTH
    through read_internal_field(), and report the largest change the reader
    sees.  The caller REFUSES if the reader cannot see it."""
    a = os.path.join(workdir, "control_clean")
    b = os.path.join(workdir, "control_planted")
    shutil.copyfile(field_path, a)
    shutil.copyfile(field_path, b)
    before, after = plant_into_field(b, PLANT)
    fa = read_internal_field(a)
    fb = read_internal_field(b)
    if len(fa["values"]) != len(fb["values"]):
        refuse("PLANT", "planted and clean copies parsed to different lengths")
    seen = max(abs(x - y) for x, y in zip(fb["values"], fa["values"]))
    return dict(planted=PLANT, read_back_delta=after - before,
                reader_max_change=seen, passed=seen >= PLANT - 1e-15)


# --------------------------------------------------------------------------
# dictionary helpers
# --------------------------------------------------------------------------
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _match_block(txt, keyword):
    """Return (open_brace_idx, close_brace_idx) of `keyword { ... }`, or None."""
    m = re.search(r"(?m)^[ \t]*" + re.escape(keyword) + r"\b[^\S\n]*\n?[^\S\n]*\{", txt)
    if not m:
        return None
    ob = txt.index("{", m.start())
    depth = 0
    for i in range(ob, len(txt)):
        if txt[i] == "{":
            depth += 1
        elif txt[i] == "}":
            depth -= 1
            if depth == 0:
                return ob, i
    return None


def read_keyword(txt, key):
    m = re.search(r"(?m)^[ \t]*" + re.escape(key) + r"[ \t]+([^;]*);", txt)
    return m.group(1).strip() if m else None


def set_keyword(txt, key, value):
    """Set a top-level keyword, inserting it after the FoamFile block if absent."""
    pat = re.compile(r"(?m)^([ \t]*)" + re.escape(key) + r"[ \t]+[^;]*;")
    if pat.search(txt):
        return pat.sub(lambda mo: f"{mo.group(1)}{key}    {value};", txt, count=1)
    ff = _match_block(txt, "FoamFile")
    if ff is None:
        return txt.rstrip() + f"\n\n{key}    {value};\n"
    close = ff[1]
    nl = txt.find("\n", close)
    nl = close + 1 if nl < 0 else nl + 1
    return txt[:nl] + f"\n{key}    {value};\n" + txt[nl:]


def empty_functions_block(txt):
    span = _match_block(txt, "functions")
    if span is None:
        return txt.rstrip() + "\n\nfunctions\n{\n}\n"
    ob, cb = span
    return txt[:ob] + "{\n}" + txt[cb + 1:]


def empty_residual_control(txt):
    """Empty every residualControl sub-dictionary in the file."""
    while True:
        span = _match_block(txt, "residualControl")
        if span is None:
            return txt
        ob, cb = span
        if txt[ob:cb + 1].strip() == "{\n    }":
            return txt
        txt = txt[:ob] + "{\n    }" + txt[cb + 1:]


def residual_control_bodies(txt):
    """Every residualControl body in the file, as stripped strings."""
    out, cursor, hay = [], 0, txt
    while True:
        span = _match_block(hay, "residualControl")
        if span is None:
            return out
        ob, cb = span
        out.append(hay[ob + 1:cb].strip())
        hay = hay[cb + 1:]
        cursor += cb
    return out


def libs_lines(txt):
    return sorted(re.findall(r"(?m)^[ \t]*libs[ \t]*\(.*?\);", txt))


def set_ras_model(txt, model):
    pat = re.compile(r"(?m)^([ \t]*)RASModel[ \t]+[^;]*;")
    if not pat.search(txt):
        refuse("TP-NO-RASMODEL", "turbulenceProperties has no RASModel entry")
    return pat.sub(lambda mo: f"{mo.group(1)}RASModel        {model};", txt, count=1)


def read_ras_model(txt):
    return read_keyword(txt, "RASModel")


def numeric_time_dirs(root):
    if not os.path.isdir(root):
        return []
    return sorted(d for d in os.listdir(root)
                  if TIME_DIR_RE.match(d) and os.path.isdir(os.path.join(root, d)))


def _first_int_after_header(path):
    """The standalone integer that heads an OpenFOAM ascii list file."""
    txt = open(path, "r", errors="replace").read()
    ff = _match_block(txt, "FoamFile")
    start = ff[1] if ff else 0
    m = re.search(r"(?m)^\s*(\d+)\s*$", txt[start:])
    return int(m.group(1)) if m else None


def mesh_counts_from_disk(case_dir):
    """Read the mesh size back off disk TWICE, by two independent routes."""
    pm = os.path.join(case_dir, "constant", "polyMesh")
    own_path = os.path.join(pm, "owner")
    pts_path = os.path.join(pm, "points")
    if not (os.path.isfile(own_path) and os.path.isfile(pts_path)):
        refuse("MESH-MISSING", f"polyMesh owner/points missing under {pm}")
    head = open(own_path, "r", errors="replace").read(4000)
    note = dict(re.findall(r"(nPoints|nCells|nFaces|nInternalFaces):\s*(\d+)", head))
    note = {k: int(v) for k, v in note.items()}
    out = dict(note=note)
    out["points_list_length"] = _first_int_after_header(pts_path)
    out["owner_list_length"] = _first_int_after_header(own_path)
    # nCells from the owner list itself, when the file is ascii.
    ncells_from_owner = None
    if "format" in open(own_path, "r", errors="replace").read(1000) and \
            re.search(r"format\s+ascii", open(own_path, "r", errors="replace").read(1000)):
        txt = open(own_path, "r", errors="replace").read()
        ob = txt.find("(", txt.find(str(out["owner_list_length"] or -1)))
        cb = txt.rfind(")")
        if ob > 0 and cb > ob:
            try:
                ncells_from_owner = max(int(x) for x in txt[ob + 1:cb].split()) + 1
            except ValueError:
                ncells_from_owner = None
    out["ncells_from_owner_list"] = ncells_from_owner
    return out


# --------------------------------------------------------------------------
# GUARDS.  Each takes ctx and raises Refusal.  Each has a mutator used by the
# selftest and by the L-314 planted-failure proof.
# --------------------------------------------------------------------------
def g_R1_source_complete(ctx):
    src = ctx["src"]
    need = [("constant/polyMesh", True), ("0", True), ("system", True),
            ("constant/turbulenceProperties", False), ("system/controlDict", False),
            ("system/fvSolution", False), ("constant/transportProperties", False)]
    for rel, isdir in need:
        p = os.path.join(src, rel)
        ok = os.path.isdir(p) if isdir else os.path.isfile(p)
        if not ok:
            refuse("R1", f"source case {src} is missing {rel}")


def g_R2_not_excluded(ctx):
    if ctx["case_id"] == "NASA_2DWMH":
        refuse("R2", "NASA_2DWMH is EXCLUDED from M1 by PREREGISTRATION.md section 2.2")


def g_R3_source_model(ctx):
    tp = open(os.path.join(ctx["src"], "constant", "turbulenceProperties"),
              errors="replace").read()
    got = read_ras_model(tp)
    if got != SOURCE_MODEL:
        refuse("R3", f"{ctx['case_id']}: source RASModel is {got!r}, not {SOURCE_MODEL!r} "
                     f"-- an M1 case must ship the model the null arm re-solves")


def g_R4_nut_ic(ctx):
    """The control that produced the NASA_2DWMH exclusion.  39 of 40 uniform 0."""
    p = os.path.join(ctx["src"], "0", "nut")
    if not os.path.isfile(p):
        refuse("R4", f"{ctx['case_id']}: no 0/nut")
    txt = open(p, errors="replace").read()
    m = re.search(r"(?m)^\s*internalField\s+([^;]*);", txt)
    got = m.group(1).strip() if m else None
    if got != NUT_IC_REQUIRED:
        refuse("R4", f"{ctx['case_id']}: 0/nut internalField is {got!r}, not "
                     f"{NUT_IC_REQUIRED!r} -- an unexpanded dictionary variable or a "
                     f"non-zero seed is an unregistered initial condition")


def g_R5_dst_clear(ctx):
    dst = ctx["dst"]
    if os.path.isdir(dst) and os.listdir(dst):
        refuse("R5", f"{dst} already exists and is not empty -- a staged case is "
                     f"never overwritten")


def g_R6_no_time_dirs(ctx):
    dst = ctx["dst"]
    if os.path.isdir(os.path.join(dst, "0")):
        refuse("R6", f"{dst}/0 exists -- the age guard counts 0 as a numeric time "
                     f"directory; stage as 0.orig")
    tds = numeric_time_dirs(dst)
    if tds:
        refuse("R6", f"{dst} holds numeric time directories {tds} -- a run is never "
                     f"launched into a tree that already holds an answer")


def g_R7_orig_fields(ctx):
    d = os.path.join(ctx["dst"], "0.orig")
    if not os.path.isdir(d):
        refuse("R7", f"{d} missing -- run_m1.sh arms 0/ from 0.orig/")
    got = sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))
    if got != sorted(ORIG_FIELDS):
        refuse("R7", f"0.orig holds {got}, expected exactly {sorted(ORIG_FIELDS)}")


def g_R8_libs_preserved(ctx):
    """Standing rule 14: the libs line is LEFT IN PLACE, never deleted to tidy."""
    a = libs_lines(open(os.path.join(ctx["src"], "system", "controlDict"),
                        errors="replace").read())
    b = libs_lines(open(os.path.join(ctx["dst"], "system", "controlDict"),
                        errors="replace").read())
    if a != b:
        refuse("R8", f"{ctx['case_id']}: libs lines changed by staging.\n"
                     f"  source: {a}\n  staged: {b}\n"
                     f"  Standing rule 14 -- libs entries are never replaced or deleted.")


def g_R9_includes_resolve(ctx):
    """Every #include "<relpath>" in any staged system/ or 0.orig/ file must
    resolve to a file that IS in the staged tree.

    This is not only about system/fvOptions.  The eight duct cases carry
    SYMBOLIC INITIAL FIELDS -- 0/U reads `internalField uniform $Uinlet;` with
    `Uinlet ($U_b 0 0);` and `U_b #calc "$Re_b*$nu/$h";` above it, resolved
    through `#include "../caseDef"` from inside 0/U itself.  Staging 0.orig
    without caseDef produces a case that fails at read time on the FIELD, not
    only on fvOptions.
    """
    for root_file in ROOT_FILES:
        if os.path.isfile(os.path.join(ctx["src"], root_file)) and \
                not os.path.isfile(os.path.join(ctx["dst"], root_file)):
            refuse("R9", f"{ctx['case_id']}: source has {root_file}, staged tree does "
                         f"not -- dictionary variables resolved through it would be "
                         f"unexpanded at read time")
    unresolved = []
    for sub in ("system", "0.orig"):
        d = os.path.join(ctx["dst"], sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            fp = os.path.join(d, f)
            if not os.path.isfile(fp):
                continue
            txt = open(fp, errors="replace").read()
            for inc in re.findall(r'(?m)^\s*#include\s+"([^"]+)"', txt):
                target = os.path.normpath(os.path.join(d, inc))
                if not os.path.isfile(target):
                    unresolved.append(f"{sub}/{f} -> {inc}")
    if unresolved:
        refuse("R9", f"{ctx['case_id']}: staged #include directives do not resolve: "
                     f"{unresolved}")


def g_R10_fvoptions(ctx):
    src_has = os.path.isfile(os.path.join(ctx["src"], "system", "fvOptions"))
    dst_has = os.path.isfile(os.path.join(ctx["dst"], "system", "fvOptions"))
    if src_has and not dst_has:
        refuse("R10", f"{ctx['case_id']}: source has system/fvOptions and the staged "
                      f"tree does not -- the meanVelocityForce that drives the "
                      f"periodic cases would be gone and the flow unforced")


def g_R11_controldict(ctx):
    txt = open(os.path.join(ctx["dst"], "system", "controlDict"), errors="replace").read()
    for key, val in CONTROLDICT_PATCH:
        got = read_keyword(txt, key)
        if got is None or got.split("//")[0].strip() != val:
            refuse("R11", f"{ctx['case_id']}: staged controlDict {key} reads {got!r}, "
                          f"expected {val!r}")
    span = _match_block(txt, "functions")
    if span is None or txt[span[0] + 1:span[1]].strip() != "":
        refuse("R11", f"{ctx['case_id']}: staged controlDict functions block is not empty")


def g_R12_residual_control_empty(ctx):
    txt = open(os.path.join(ctx["dst"], "system", "fvSolution"), errors="replace").read()
    for body in residual_control_bodies(txt):
        if body != "":
            refuse("R12", f"{ctx['case_id']}: staged fvSolution residualControl is not "
                          f"empty ({body!r}) -- an early stop violates standing rule 4's "
                          f"'last time == endTime' and 'ExecutionTime count == endTime'")


def g_R13_arm_applied(ctx):
    tp = open(os.path.join(ctx["dst"], "constant", "turbulenceProperties"),
              errors="replace").read()
    got = read_ras_model(tp)
    want = ARMS[ctx["arm"]]
    if got != want:
        refuse("R13", f"{ctx['case_id']} arm {ctx['arm']}: staged RASModel reads {got!r}, "
                      f"expected {want!r}")


def g_R14_constant_fields_dropped(ctx):
    cd = os.path.join(ctx["dst"], "constant")
    present = [f for f in DROP_FROM_CONSTANT if os.path.exists(os.path.join(cd, f))]
    if present:
        refuse("R14", f"{ctx['case_id']}: staged constant/ still holds {present} -- the "
                      f"registered policy drops C, Cx, Cy, Cz, V on all 78 uniformly")


def g_R15_cells_corroborated(ctx):
    c = mesh_counts_from_disk(ctx["dst"])
    note = c["note"]
    if not note:
        refuse("R15", f"{ctx['case_id']}: staged polyMesh/owner carries no size note")
    if c["points_list_length"] is not None and "nPoints" in note:
        if c["points_list_length"] != note["nPoints"]:
            refuse("R15", f"{ctx['case_id']}: owner note says nPoints {note['nPoints']}, "
                          f"the staged points file holds {c['points_list_length']}")
    if c["owner_list_length"] is not None and "nFaces" in note:
        if c["owner_list_length"] != note["nFaces"]:
            refuse("R15", f"{ctx['case_id']}: owner note says nFaces {note['nFaces']}, "
                          f"the staged owner list holds {c['owner_list_length']}")
    if c["ncells_from_owner_list"] is not None and "nCells" in note:
        if c["ncells_from_owner_list"] != note["nCells"]:
            refuse("R15", f"{ctx['case_id']}: owner note says nCells {note['nCells']}, "
                          f"max(owner)+1 on the staged list is {c['ncells_from_owner_list']}")
    corroborations = sum(1 for k in ("points_list_length", "owner_list_length",
                                     "ncells_from_owner_list") if c[k] is not None)
    if corroborations == 0:
        refuse("R15", f"{ctx['case_id']}: the manifest's cell count could not be "
                      f"corroborated by ANY second read of the staged tree -- a number "
                      f"nothing checked is not a reading")
    ctx["mesh_counts"] = c


def g_R16_planted_zero(ctx):
    """Standing rule 3, inside the staging tool: the manifest's field reader is
    shown able to see a non-zero before any of its numbers are believed.

    The plant goes into a COPY ON DISK and is read back by re-opening the file.
    An in-memory plant does not satisfy rule 3 and is not used.

    `0.orig/nut` is the primary carrier because it is `uniform 0` on all 39
    cases -- so the control is literally "plant a non-zero into a field of zeros
    and prove the reader sees it".  `0.orig/U` is used additionally where it is
    parseable; on the eight ducts it is NOT (`uniform $Uinlet`), and that is
    recorded rather than worked around.
    """
    base = ctx["dst"] if os.path.isdir(os.path.join(ctx["dst"], "0.orig")) else ctx["src"]
    sub = "0.orig" if base == ctx["dst"] else "0"
    results, symbolic = {}, []
    for name in PLANT_CANDIDATES:
        field = os.path.join(base, sub, name)
        if not os.path.isfile(field):
            continue
        try:
            read_internal_field(field)
        except Refusal:
            symbolic.append(name)          # unexpanded dictionary variable
            continue
        with tempfile.TemporaryDirectory(prefix="m1plant_") as tmp:
            results[name] = planted_zero_control(field, tmp)
    if not results:
        refuse("R16", f"{ctx['case_id']}: NO 0.orig field could be read numerically "
                      f"({symbolic} are symbolic), so the reader could not be shown "
                      f"able to see a non-zero and its zeros would mean nothing")
    for name, pz in results.items():
        if not pz["passed"]:
            refuse("R16", f"{ctx['case_id']}: planted-zero control FAILED on "
                          f"0.orig/{name} -- the reader cannot see a {PLANT} "
                          f"perturbation planted on disk. {pz}")
    ctx["planted_zero"] = dict(controls=results, symbolic_fields=sorted(symbolic))


PRE_GUARDS = [("R1", g_R1_source_complete), ("R2", g_R2_not_excluded),
              ("R3", g_R3_source_model), ("R4", g_R4_nut_ic),
              ("R5", g_R5_dst_clear)]
POST_GUARDS = [("R6", g_R6_no_time_dirs), ("R7", g_R7_orig_fields),
               ("R8", g_R8_libs_preserved), ("R9", g_R9_includes_resolve),
               ("R10", g_R10_fvoptions), ("R11", g_R11_controldict),
               ("R12", g_R12_residual_control_empty), ("R13", g_R13_arm_applied),
               ("R14", g_R14_constant_fields_dropped),
               ("R15", g_R15_cells_corroborated), ("R16", g_R16_planted_zero)]
ALL_GUARDS = dict(PRE_GUARDS + POST_GUARDS)


# --------------------------------------------------------------------------
# enumeration and staging
# --------------------------------------------------------------------------
def enumerate_cases(src_root):
    out = []
    for dirpath, _dirs, _files in os.walk(src_root):
        if os.path.basename(dirpath) != "polyMesh":
            continue
        root = os.path.dirname(os.path.dirname(dirpath))
        if not (os.path.isdir(os.path.join(root, "0"))
                and os.path.isdir(os.path.join(root, "system"))
                and os.path.isfile(os.path.join(root, "constant", "turbulenceProperties"))):
            continue
        out.append(root)
    return sorted(out)


def stage_one(src, dst, arm, case_id, execute):
    ctx = dict(src=src, dst=dst, arm=arm, case_id=case_id)
    for _code, g in PRE_GUARDS:
        g(ctx)
    if not execute:
        g_R16_planted_zero(ctx)          # the reader is proven even in a dry run
        return ctx
    os.makedirs(dst, exist_ok=False)

    # constant/
    os.makedirs(os.path.join(dst, "constant"))
    shutil.copytree(os.path.join(src, "constant", "polyMesh"),
                    os.path.join(dst, "constant", "polyMesh"))
    shutil.copyfile(os.path.join(src, "constant", "transportProperties"),
                    os.path.join(dst, "constant", "transportProperties"))
    tp = open(os.path.join(src, "constant", "turbulenceProperties"),
              errors="replace").read()
    open(os.path.join(dst, "constant", "turbulenceProperties"), "w").write(
        set_ras_model(tp, ARMS[arm]))
    # C, Cx, Cy, Cz, V are deliberately NOT copied (section 5.4).

    # system/  -- everything, then exactly two files patched
    os.makedirs(os.path.join(dst, "system"))
    for f in sorted(os.listdir(os.path.join(src, "system"))):
        sp = os.path.join(src, "system", f)
        if os.path.isfile(sp):
            shutil.copyfile(sp, os.path.join(dst, "system", f))
        elif os.path.isdir(sp):
            shutil.copytree(sp, os.path.join(dst, "system", f))
    cdp = os.path.join(dst, "system", "controlDict")
    txt = open(cdp, errors="replace").read()
    for key, val in CONTROLDICT_PATCH:
        txt = set_keyword(txt, key, val)
    txt = empty_functions_block(txt)
    open(cdp, "w").write(txt)
    fsp = os.path.join(dst, "system", "fvSolution")
    # READ FULLY FIRST.  `open(p, "w").write(open(p).read())` truncates the file
    # before the inner read is evaluated and silently writes an empty file --
    # measured while writing this script, and it defeated guard R12.
    fs_txt = open(fsp, errors="replace").read()
    open(fsp, "w").write(empty_residual_control(fs_txt))
    # fvSchemes is NOT touched.

    # caseDef / fieldDef, when the source has them.  dynamicCode/ is NOT copied:
    # #calc regenerates it, and a stale compiled object is a silent hazard.
    for rf in ROOT_FILES:
        if os.path.isfile(os.path.join(src, rf)):
            shutil.copyfile(os.path.join(src, rf), os.path.join(dst, rf))

    # 0.orig/ -- exactly five fields, NO 0/, NO numeric time directory
    os.makedirs(os.path.join(dst, "0.orig"))
    for f in ORIG_FIELDS:
        sp = os.path.join(src, "0", f)
        if not os.path.isfile(sp):
            refuse("R7", f"{case_id}: source 0/{f} missing")
        shutil.copyfile(sp, os.path.join(dst, "0.orig", f))

    for _code, g in POST_GUARDS:
        g(ctx)
    return ctx


def _symbolic_census(dst):
    """Which 0.orig fields carry an unexpanded dictionary variable or a
    preprocessor directive.  Recorded, never silently repaired."""
    out = {}
    d = os.path.join(dst, "0.orig")
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        txt = open(os.path.join(d, f), errors="replace").read()
        m = re.search(r"(?m)^\s*internalField\s+([^;]*);", txt)
        ic = m.group(1).strip() if m else None
        out[f] = dict(internalField=ic,
                      symbolic=bool(ic and "$" in ic),
                      directives=sorted(set(re.findall(r"(?m)^\s*(#\w+)", txt))))
    return out


def manifest_entry(ctx):
    dst = ctx["dst"]
    files = {}
    for dirpath, _d, fnames in os.walk(dst):
        for f in sorted(fnames):
            p = os.path.join(dirpath, f)
            files[os.path.relpath(p, dst)] = sha256_file(p)
    src_cd = os.path.join(ctx["src"], "system", "controlDict")
    dst_cd = os.path.join(dst, "system", "controlDict")
    cdtxt = open(dst_cd, errors="replace").read()
    mc = ctx.get("mesh_counts") or mesh_counts_from_disk(dst)
    return dict(
        arm=ctx["arm"], case_id=ctx["case_id"], src=ctx["src"], dst=dst,
        files_sha256=files,
        cells_from_owner_note=mc["note"].get("nCells"),
        npoints_from_owner_note=mc["note"].get("nPoints"),
        points_list_length=mc["points_list_length"],
        owner_list_length=mc["owner_list_length"],
        ncells_from_owner_list=mc["ncells_from_owner_list"],
        zero_dir_absent=not os.path.isdir(os.path.join(dst, "0")),
        numeric_time_dirs=numeric_time_dirs(dst),
        orig_fields=sorted(os.listdir(os.path.join(dst, "0.orig"))),
        rasmodel_readback=read_ras_model(
            open(os.path.join(dst, "constant", "turbulenceProperties"),
                 errors="replace").read()),
        controldict_readback={k: read_keyword(cdtxt, k) for k, _v in CONTROLDICT_PATCH},
        functions_block_empty=(lambda s: s is not None and cdtxt[s[0] + 1:s[1]].strip() == "")(
            _match_block(cdtxt, "functions")),
        residual_control_bodies=residual_control_bodies(
            open(os.path.join(dst, "system", "fvSolution"), errors="replace").read()),
        libs_lines_src=libs_lines(open(src_cd, errors="replace").read()),
        libs_lines_dst=libs_lines(cdtxt),
        caseDef=os.path.isfile(os.path.join(dst, "caseDef")),
        fieldDef=os.path.isfile(os.path.join(dst, "fieldDef")),
        symbolic_orig_fields=_symbolic_census(dst),
        fvOptions=os.path.isfile(os.path.join(dst, "system", "fvOptions")),
        planted_zero=ctx.get("planted_zero"),
        age_datum=f"0.orig/{AGE_DATUM}",
    )


def main(argv):
    ap = argparse.ArgumentParser(description="M1 staging (dry run by default)")
    ap.add_argument("--src-root", default=SRC_ROOT_DEFAULT)
    ap.add_argument("--dst-root", default=DST_ROOT_DEFAULT)
    ap.add_argument("--arm", action="append", choices=sorted(ARMS), default=None)
    ap.add_argument("--case", action="append", default=None)
    ap.add_argument("--execute", action="store_true",
                    help="actually write.  WITHOUT THIS NOTHING IS WRITTEN.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--planted-failure", metavar="GUARD",
                    help="L-314 proof: mutate GUARD to a no-op and show the control flips")
    args = ap.parse_args(argv[1:])

    if args.selftest:
        return selftest()
    if args.planted_failure:
        return planted_failure_proof(args.planted_failure)

    arms = args.arm or sorted(ARMS)
    roots = enumerate_cases(args.src_root)
    wanted = set(args.case) if args.case else None
    print(f"source root : {args.src_root}")
    print(f"dest root   : {args.dst_root}")
    print(f"enumerated  : {len(roots)} case roots")
    print(f"MODE        : {'EXECUTE (writing)' if args.execute else 'DRY RUN (writing nothing)'}")
    print()
    entries, skipped, failed = [], [], []
    for root in roots:
        case_id = os.path.basename(root)
        for arm in arms:
            dst = os.path.join(args.dst_root, arm, case_id)
            try:
                ctx = stage_one(root, dst, arm, case_id, args.execute)
            except Refusal as e:
                if e.code in ("R2", "R3", "R4"):
                    skipped.append((arm, case_id, str(e)))
                else:
                    failed.append((arm, case_id, str(e)))
                continue
            if args.execute:
                entries.append(manifest_entry(ctx))
            else:
                entries.append(dict(arm=arm, case_id=case_id, src=root, dst=dst,
                                    planted_zero=ctx.get("planted_zero")))
    print(f"staged/planned : {len(entries)}")
    print(f"skipped by an exclusion guard (R2/R3/R4) : {len(skipped)}")
    for a, c, m in skipped:
        print(f"   SKIP {a}/{c}: {m}")
    if failed:
        print(f"FAILED : {len(failed)}")
        for a, c, m in failed:
            print(f"   FAIL {a}/{c}: {m}")
    if args.execute:
        os.makedirs(args.dst_root, exist_ok=True)
        mpath = os.path.join(args.dst_root, MANIFEST_NAME)
        json.dump(dict(
            tool="stage_m1.py",
            tool_sha256=sha256_file(os.path.abspath(__file__)),
            staged_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            cap_iterations=CAP_ITER, arms=ARMS, entries=entries,
            skipped=[dict(arm=a, case_id=c, reason=m) for a, c, m in skipped],
        ), open(mpath, "w"), indent=2, sort_keys=True)
        print(f"manifest : {mpath}")
    if failed:
        return 2
    return 0


# --------------------------------------------------------------------------
# SELFTEST.  Runs under `python3 -O` with every refusal still firing.
# --------------------------------------------------------------------------
def _write(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(txt)


def _synth_case(root, with_casedef=True, with_fvoptions=True, with_libs=True,
                nut_ic="uniform 0", model=SOURCE_MODEL):
    """A minimal but structurally real ascii OpenFOAM case: 2 cells, 11 faces."""
    hdr = ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
           "    class %s;\n    note \"%s\";\n    object %s;\n}\n")
    npts, ncells, nfaces = 12, 2, 11
    pts = "\n".join(f"({i} 0 0)" for i in range(npts))
    _write(f"{root}/constant/polyMesh/points",
           (hdr % ("vectorField", "", "points")) + f"\n{npts}\n(\n{pts}\n)\n")
    own = " ".join(str(i % ncells) for i in range(nfaces))
    _write(f"{root}/constant/polyMesh/owner",
           (hdr % ("labelList",
                   f"nPoints: {npts} nCells: {ncells} nFaces: {nfaces} nInternalFaces: 1",
                   "owner")) + f"\n{nfaces}\n(\n{own}\n)\n")
    _write(f"{root}/constant/polyMesh/neighbour",
           (hdr % ("labelList", "", "neighbour")) + "\n1\n(\n1\n)\n")
    _write(f"{root}/constant/polyMesh/faces",
           (hdr % ("faceList", "", "faces")) + f"\n{nfaces}\n(\n" +
           "\n".join("4(0 1 2 3)" for _ in range(nfaces)) + "\n)\n")
    _write(f"{root}/constant/polyMesh/boundary",
           (hdr % ("polyBoundaryMesh", "", "boundary")) + "\n0\n(\n)\n")
    _write(f"{root}/constant/transportProperties",
           "transportModel  Newtonian;\nnu  [0 2 -1 0 0 0 0] 1e-4;\n")
    _write(f"{root}/constant/turbulenceProperties",
           f"simulationType RAS;\n\nRAS\n{{\n    RASModel        {model};\n"
           f"    turbulence      on;\n    printCoeffs     on;\n}}\n")
    for f in DROP_FROM_CONSTANT:
        _write(f"{root}/constant/{f}", (hdr % ("volScalarField", "", f)) +
               "\ninternalField   uniform 1;\nboundaryField{}\n")
    # 0/
    _write(f"{root}/0/U", (hdr % ("volVectorField", "", "U")) +
           "\ninternalField   nonuniform List<vector>\n2\n(\n(1.5 0 0)\n(2.5 0 0)\n)\n;\n"
           "\nboundaryField\n{\n}\n")
    for f, ic in (("p", "uniform 0"), ("k", "uniform 0.00668"),
                  ("omega", "uniform 0.11"), ("nut", nut_ic)):
        _write(f"{root}/0/{f}", (hdr % ("volScalarField", "", f)) +
               f"\ninternalField   {ic};\n\nboundaryField\n{{\n}}\n")
    for f in ("U_LES", "k_LES", "tauij_LES", "C", "Cx"):
        _write(f"{root}/0/{f}", (hdr % ("volScalarField", "", f)) +
               "\ninternalField   uniform 1;\n\nboundaryField\n{\n}\n")
    _write(f"{root}/0/uniform/time", "value 0;\n")
    # a shipped converged time directory -- the thing that must NOT be copied
    _write(f"{root}/1234/U", (hdr % ("volVectorField", "", "U")) +
           "\ninternalField   nonuniform List<vector>\n2\n(\n(1 0 0)\n(2 0 0)\n)\n;\n"
           "\nboundaryField\n{\n}\n")
    # system/
    libs = 'libs ( "libfrozenIncompressibleTurbulenceModels.so" );\n\n' if with_libs else ""
    _write(f"{root}/system/controlDict",
           (hdr % ("dictionary", "", "controlDict")) + "\n" + libs +
           "startFrom       latestTime;\n\nstopAt          endTime;//writeNow\n\n"
           "endTime         500000;\n\ndeltaT          1;\n\n"
           "writeControl    timeStep;\n\nwriteInterval   $endTime;\n\npurgeWrite      0;\n\n"
           "writeFormat     ascii;\n\nwritePrecision  6;\n\nrunTimeModifiable true;\n\n"
           "functions\n{\n    #includeFunc residuals\n    #includeFunc convergenceProbes\n}\n")
    _write(f"{root}/system/fvSolution",
           (hdr % ("dictionary", "", "fvSolution")) +
           "\nsolvers\n{\n    p\n    {\n        solver GAMG;\n    }\n}\n\n"
           "SIMPLE\n{\n    nNonOrthogonalCorrectors 0;\n\n"
           "    residualControl\n    {\n        k               5e-6;\n"
           "        omega           1e-10;\n    }\n    pRefCell 0;\n}\n")
    _write(f"{root}/system/fvSchemes",
           (hdr % ("dictionary", "", "fvSchemes")) +
           "\nddtSchemes { default steadyState; }\nwallDist { method meshWave; }\n")
    if with_fvoptions:
        _write(f"{root}/system/fvOptions", '#include "../caseDef"\n\nmomentumSource{}\n')
    if with_casedef:
        _write(f"{root}/caseDef", "nu 1e-4;\nRe_b 3000;\nh 1e-3;\n")
    _write(f"{root}/fieldDef", "residualFields (U p k omega);\n")
    return root


def _check(label, ok, detail=""):
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))
    return bool(ok)


def _stage_into(tmp, **kw):
    src = _synth_case(os.path.join(tmp, "src"), **kw)
    dst = os.path.join(tmp, "dst", "kOmega", "SYNTH")
    ctx = stage_one(src, dst, "kOmega", "SYNTH", execute=True)
    return src, dst, ctx


def _rewrite(path, fn):
    """Read fully, transform, then write.  NEVER open(p,"w").write(open(p).read()):
    the truncation happens before the inner read is evaluated."""
    txt = open(path, errors="replace").read()
    open(path, "w").write(fn(txt))


MUTATORS = {
    # R1 guards the SOURCE, so its mutation must land on the source tree.
    "R1": lambda src, dst: os.remove(os.path.join(src, "system", "controlDict")),
    "R2": None,
    "R3": None,
    "R4": None,
    "R5": None,
    "R6": lambda src, dst: os.makedirs(os.path.join(dst, "0"), exist_ok=True),
    "R7": lambda src, dst: os.remove(os.path.join(dst, "0.orig", "nut")),
    "R8": lambda src, dst: _rewrite(
        os.path.join(dst, "system", "controlDict"),
        lambda t: re.sub(r"(?m)^[ \t]*libs[ \t]*\(.*?\);\n", "", t)),
    "R9": lambda src, dst: os.remove(os.path.join(dst, "caseDef")),
    "R9b": lambda src, dst: os.remove(os.path.join(dst, "fieldDef")),
    "R10": lambda src, dst: os.remove(os.path.join(dst, "system", "fvOptions")),
    "R11": lambda src, dst: _rewrite(
        os.path.join(dst, "system", "controlDict"),
        lambda t: set_keyword(t, "endTime", "500000")),
    "R12": lambda src, dst: _rewrite(
        os.path.join(dst, "system", "fvSolution"),
        lambda t: t.replace("residualControl\n    {\n    }",
                            "residualControl\n    {\n        k 5e-6;\n    }")),
    "R13": lambda src, dst: _rewrite(
        os.path.join(dst, "constant", "turbulenceProperties"),
        lambda t: set_ras_model(t, "kEpsilon")),
    "R14": lambda src, dst: open(os.path.join(dst, "constant", "Cx"), "w").write("x\n"),
    "R15": lambda src, dst: _rewrite(
        os.path.join(dst, "constant", "polyMesh", "owner"),
        lambda t: t.replace("nCells: 2", "nCells: 999")),
    # R16's failure mode is a BLIND READER, not a bad file: a reader that
    # returns the same value whatever is on disk would report a zero change and
    # every "no difference" this tool prints would be meaningless.  Mutating the
    # file cannot express that, so R16 is planted by swapping the reader itself
    # (handled by _plant_R16 below, not by a file mutator).
    "R16": None,
}


def _plant_R16(src, dst):
    """Swap read_internal_field for a BLIND reader and return whether R16
    refuses.  Restores the real reader unconditionally."""
    global read_internal_field
    real = read_internal_field
    try:
        read_internal_field = lambda path: dict(kind="uniform", rank=1, n=1,
                                                values=[0.0])
        return _refuses(lambda: g_R16_planted_zero(
            dict(src=src, dst=dst, arm="kOmega", case_id="SYNTH")))
    finally:
        read_internal_field = real


def selftest():
    print("stage_m1.py --selftest")
    print(f"  running under python3 {'-O (assertions DELETED)' if not __debug__ else '(assertions live)'}")
    ok = True

    # 0. no assert carries a refusal (L-332)
    src_txt = open(os.path.abspath(__file__), errors="replace").read()
    body = "\n".join(l for l in src_txt.split("\n") if not l.strip().startswith("#"))
    ok &= _check("no `assert` statement anywhere in this file (L-332)",
                 not re.search(r"(?m)^\s*assert\b", body))

    # 1. happy path
    with tempfile.TemporaryDirectory(prefix="m1st_") as tmp:
        src, dst, ctx = _stage_into(tmp)
        me = manifest_entry(ctx)
        ok &= _check("0/ absent after staging", me["zero_dir_absent"])
        ok &= _check("no numeric time directory staged", me["numeric_time_dirs"] == [],
                     str(me["numeric_time_dirs"]))
        ok &= _check("0.orig holds exactly U p k omega nut",
                     me["orig_fields"] == sorted(ORIG_FIELDS), str(me["orig_fields"]))
        ok &= _check("shipped 1234/ was NOT copied",
                     not os.path.exists(os.path.join(dst, "1234")))
        ok &= _check("RASModel read back off disk == arm",
                     me["rasmodel_readback"] == "kOmega", str(me["rasmodel_readback"]))
        ok &= _check("controlDict endTime read back == 20000",
                     me["controldict_readback"]["endTime"] == "20000")
        ok &= _check("controlDict startFrom read back == startTime",
                     me["controldict_readback"]["startFrom"] == "startTime")
        ok &= _check("controlDict application inserted where absent",
                     (me["controldict_readback"]["application"] or "").startswith("simpleFoam"))
        ok &= _check("functions block emptied", me["functions_block_empty"])
        ok &= _check("residualControl emptied",
                     me["residual_control_bodies"] == [""], str(me["residual_control_bodies"]))
        ok &= _check("libs line preserved byte-for-byte (rule 14)",
                     me["libs_lines_src"] == me["libs_lines_dst"] and me["libs_lines_dst"] != [])
        ok &= _check("caseDef staged", me["caseDef"])
        ok &= _check("fieldDef staged", me["fieldDef"])
        ok &= _check("symbolic-field census recorded for every 0.orig field",
                     sorted(me["symbolic_orig_fields"]) == sorted(ORIG_FIELDS))
        ok &= _check("fvOptions staged", me["fvOptions"])
        ok &= _check("constant/{C,Cx,Cy,Cz,V} dropped",
                     not any(os.path.exists(os.path.join(dst, "constant", f))
                             for f in DROP_FROM_CONSTANT))
        ok &= _check("cell count corroborated by a second read of the staged tree",
                     me["cells_from_owner_note"] == me["ncells_from_owner_list"] ==
                     2, f"note={me['cells_from_owner_note']} owner_list={me['ncells_from_owner_list']}")
        pz = me["planted_zero"]
        ok &= _check("planted zero: the reader SEES a plant made on disk",
                     bool(pz["controls"]) and
                     all(c["passed"] and abs(c["reader_max_change"] - PLANT) < 1e-12
                         for c in pz["controls"].values()),
                     str(pz))
        ok &= _check("the plant ran on 0.orig/nut (a field of zeros) and on 0.orig/U",
                     sorted(pz["controls"]) == ["U", "nut"], str(sorted(pz["controls"])))

    # 1b. a case with a SYMBOLIC 0/U (the eight ducts) still gets a live control,
    #     via 0.orig/nut, and the symbolic field is RECORDED not repaired.
    with tempfile.TemporaryDirectory(prefix="m1st_") as tmp:
        src = _synth_case(os.path.join(tmp, "src"))
        _rewrite(os.path.join(src, "0", "U"),
                 lambda t: t.replace("internalField   nonuniform List<vector>\n2\n"
                                     "(\n(1.5 0 0)\n(2.5 0 0)\n)\n;",
                                     '#include "../caseDef"\nUinlet ($h 0 0);\n'
                                     'internalField   uniform $Uinlet;'))
        dst = os.path.join(tmp, "dst", "kOmega", "SYMBOLIC")
        ctx = stage_one(src, dst, "kOmega", "SYMBOLIC", execute=True)
        me2 = manifest_entry(ctx)
        ok &= _check("symbolic 0.orig/U does not defeat the rule-3 control",
                     list(me2["planted_zero"]["controls"]) == ["nut"] and
                     me2["planted_zero"]["controls"]["nut"]["passed"],
                     str(me2["planted_zero"]))
        ok &= _check("the symbolic field is RECORDED as symbolic",
                     me2["symbolic_orig_fields"]["U"]["symbolic"] is True,
                     str(me2["symbolic_orig_fields"]["U"]))
        ok &= _check("R9 resolves the #include that the symbolic field needs",
                     not _refuses(lambda: g_R9_includes_resolve(ctx)))
        os.remove(os.path.join(dst, "caseDef"))
        ok &= _check("R9 refuses when 0.orig/U includes a caseDef that is not staged",
                     _refuses(lambda: g_R9_includes_resolve(ctx)))

    # 2. the exclusion guards, on the conditions that actually excluded NASA_2DWMH
    with tempfile.TemporaryDirectory(prefix="m1st_") as tmp:
        s = _synth_case(os.path.join(tmp, "s"), nut_ic="uniform $nut")
        ok &= _check("R4 refuses `0/nut internalField uniform $nut`",
                     _refuses(lambda: g_R4_nut_ic(dict(src=s, case_id="X"))))
        s2 = _synth_case(os.path.join(tmp, "s2"), model="AugmentedkOmegaSST")
        ok &= _check("R3 refuses RASModel AugmentedkOmegaSST",
                     _refuses(lambda: g_R3_source_model(dict(src=s2, case_id="X"))))
        ok &= _check("R2 refuses NASA_2DWMH by name",
                     _refuses(lambda: g_R2_not_excluded(dict(case_id="NASA_2DWMH"))))
        d = os.path.join(tmp, "occupied")
        os.makedirs(d)
        open(os.path.join(d, "x"), "w").write("x")
        ok &= _check("R5 refuses a non-empty destination",
                     _refuses(lambda: g_R5_dst_clear(dict(dst=d))))

    # 3. every post-guard refuses its own mutation
    with tempfile.TemporaryDirectory(prefix="m1st_") as tmp:
        src, dst, ctx = _stage_into(tmp)
        ok &= _check("R16 refuses a BLIND reader (planted failure of the control "
                     "itself)", _plant_R16(src, dst))
        ok &= _check("    and the real reader still passes on the same tree",
                     not _refuses(lambda: g_R16_planted_zero(
                         dict(src=src, dst=dst, arm="kOmega", case_id="SYNTH"))))
    for code, guard in POST_GUARDS + [("R1", g_R1_source_complete)]:
        mut = MUTATORS.get(code)
        if mut is None:
            continue
        with tempfile.TemporaryDirectory(prefix="m1st_") as tmp:
            src, dst, ctx = _stage_into(tmp)
            mut(src, dst)
            ok &= _check(f"{code} refuses its planted failure",
                         _refuses(lambda: guard(dict(src=src, dst=dst, arm="kOmega",
                                                     case_id="SYNTH"))))

    # 4. L-314: mutate each guard to a NO-OP and prove the control FLIPS
    print("  L-314 planted-failure proofs (guard -> no-op, control must flip):")
    for code, guard in POST_GUARDS + [("R1", g_R1_source_complete)]:
        mut = MUTATORS.get(code)
        if mut is None:
            continue
        with tempfile.TemporaryDirectory(prefix="m1st_") as tmp:
            src, dst, ctx = _stage_into(tmp)
            mut(src, dst)
            noop = lambda _ctx: None            # the guard, mutated to a no-op
            flipped = not _refuses(lambda: noop(dict(src=src, dst=dst)))
            ok &= _check(f"    {code} no-op does NOT refuse (so {code} is load-bearing)",
                         flipped)

    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 2


def _refuses(fn):
    try:
        fn()
    except Refusal:
        return True
    except Exception:
        return True
    return False


def planted_failure_proof(code):
    """L-314, standalone: show that removing GUARD lets a bad tree through."""
    guard = ALL_GUARDS.get(code)
    if guard is None:
        print(f"unknown guard {code}; known: {sorted(ALL_GUARDS)}", file=sys.stderr)
        return 2
    mut = MUTATORS.get(code)
    if mut is None:
        print(f"{code} has no tree mutator (it refuses on a source property, not a "
              f"staged one); see selftest step 2", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="m1pf_") as tmp:
        src, dst, _ctx = _stage_into(tmp)
        mut(src, dst)
        live = _refuses(lambda: guard(dict(src=src, dst=dst, arm="kOmega", case_id="SYNTH")))
        dead = _refuses(lambda: None)
        print(f"guard {code}: live guard refuses = {live}; no-op guard refuses = {dead}")
        print("PROOF", "PASS" if (live and not dead) else "FAIL")
        return 0 if (live and not dead) else 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
