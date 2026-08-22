#!/usr/bin/env python3
"""R4 SpaRTA-class build lane - shared registry and OpenFOAM case helpers.

Frozen preregistration: PREREGISTRATION.md (sha256 058444309f87a9e1f6faccca2086
bf16364df7a06bb7702d155c35b1fcacbbe8).  This module SELECTS NOTHING and FITS
NOTHING; it holds the training-family registry, the case-building helpers, and
the L-221 libs law.

L-221 (docs/LESSONS.md): any writer of a `libs` entry INSERTS-OR-REPLACES and
then asserts the library name is present.  A bare str.replace is a silent no-op
on the 21 Parm_PH_29 hills, which carry no libs line at all, and the run then
returns the *baseline* field, which looks like a physical answer.
"""
from __future__ import annotations

import os
import re
import shutil

BENCH = "/home/ubuntu/closure-challenge-benchmark"
DATA = os.path.join(BENCH, "data")
WORK = "/home/ubuntu/closure-data/r4"
SPARTA_LIB = "libspartaTurbulenceModels.so"

# ---------------------------------------------------------------- registry
# The split is the benchmark README's own (PREREGISTRATION sec. 0.1); the 21
# training hills / 4 training ducts below are read back from the FS2 record
# (/home/ubuntu/closure-data/features/fs2_training_only.json) at import time so
# the two lanes cannot drift apart.
HILLS_TRAIN = [
    "alpha_05_10071_3036", "alpha_05_4071_3036", "alpha_05_7071_2024",
    "alpha_05_7071_3036", "alpha_05_7071_4048", "alpha_075",
    "alpha_10_12000_2024", "alpha_10_12000_3036", "alpha_10_12000_4048",
    "alpha_10_6000_2024", "alpha_10_6000_3036", "alpha_10_6000_4048",
    "alpha_10_9000_2024", "alpha_10_9000_3036", "alpha_10_9000_4048",
    "alpha_125", "alpha_15_10929_2024", "alpha_15_10929_3036",
    "alpha_15_10929_4048", "alpha_15_13929_3036", "alpha_15_7929_3036",
]
DUCTS_TRAIN = ["AR_1_Ret_180", "AR_3_Ret_180", "AR_5_Ret_180", "AR_10_Ret_180"]

# Never opened by this lane for any purpose (benchmark README's strict rule).
TEST_CASES = {"alpha_15_13929_4048", "alpha_15_13929_2024",
              "alpha_05_4071_4048", "alpha_05_4071_2024",
              "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"}
VAL_CASES = {"alpha_05_10071_4048", "alpha_05_10071_2024",
             "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"}


def _hill_path(case):
    for alpha in ("alpha_05", "alpha_075", "alpha_10", "alpha_125", "alpha_15"):
        p = os.path.join(DATA, "Parm_PH_29", alpha, case)
        if os.path.isdir(p):
            return p
    raise FileNotFoundError(case)


def training_cases():
    """[(case, benchmark_path, family)] over the 27 training cases."""
    out = [(c, _hill_path(c), "hills") for c in HILLS_TRAIN]
    out += [(c, os.path.join(DATA, "DUCT", c), "ducts") for c in DUCTS_TRAIN]
    out.append(("PHLL10595", os.path.join(DATA, "PH_Breuer"), "PHLL10595"))
    out.append(("CBFS13700", os.path.join(DATA, "CBFS"), "CBFS13700"))
    return out


def assert_no_test_case(cases):
    """Charter sec.22.3 / doctrine R1: assert the zero-shot boundary in code."""
    bad = sorted(set(cases) & (TEST_CASES | VAL_CASES))
    assert not bad, f"ZERO-SHOT VIOLATION: test/validation case in fit set: {bad}"


# ------------------------------------------------------------ OF utilities
def latest_time(path):
    ts = [d for d in os.listdir(path)
          if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d)
          and os.path.isdir(os.path.join(path, d)) and d != "0"]
    if not ts:
        return "0"
    return max(ts, key=float)


def retag(src, dst, obj):
    """Copy an OpenFOAM field file, rewriting only its FoamFile `object` name."""
    s = open(src).read()
    s2, n = re.subn(r"^(\s*object\s+)\S+;", rf"\g<1>{obj};", s, count=1,
                    flags=re.M)
    assert n == 1, f"no FoamFile object line in {src}"
    open(dst, "w").write(s2)


def set_libs(control_dict_path, lib=SPARTA_LIB):
    """L-221: INSERT-OR-REPLACE the libs entry, then ASSERT it is there.

    Never a bare replace.  The Parm_PH_29 hills carry no libs line, so a
    replace-only path succeeds by doing nothing and the solve dies (or, worse,
    silently returns the baseline).
    """
    s = open(control_dict_path).read()
    entry = f'libs ( "{lib}" );'
    if re.search(r"^\s*libs\s*\(", s, flags=re.M):
        s = re.sub(r"^\s*libs\s*\([^;]*\);\s*$", entry, s, count=1, flags=re.M)
    else:
        # insert after the FoamFile block so it is read before anything else
        m = re.search(r"^// \* \*.*$", s, flags=re.M)
        pos = m.end() if m else 0
        s = s[:pos] + "\n\n" + entry + "\n" + s[pos:]
    open(control_dict_path, "w").write(s)
    s = open(control_dict_path).read()
    assert "libspartaTurbulenceModels" in s, (
        f"L-221: libs entry did not land in {control_dict_path}")
    return s


def strip_functions(s):
    """Drop the shipped functions block: it #includeFuncs v7/v2112-era files."""
    i = s.find("functions")
    return s[:i] + "functions { }\n" if i >= 0 else s


def write_control_dict(path, end_time, write_interval, start_time=0,
                       write_precision=15, libs=True):
    """Rewrite a copied controlDict for a from-scratch bounded, resumable run."""
    s = open(path).read()
    s = strip_functions(s)
    s = re.sub(r"^\s*startFrom\s+.*$", "startFrom       startTime;", s,
               count=1, flags=re.M)
    if re.search(r"^\s*startTime\s+", s, flags=re.M):
        s = re.sub(r"^\s*startTime\s+.*$", f"startTime       {start_time};", s,
                   count=1, flags=re.M)
    else:
        s = re.sub(r"^startFrom.*$",
                   f"startFrom       startTime;\nstartTime       {start_time};",
                   s, count=1, flags=re.M)
    s = re.sub(r"writeInterval\s+\$endTime", f"writeInterval   {write_interval}",
               s)
    s = re.sub(r"^\s*endTime\s+.*$", f"endTime         {end_time};", s, count=1,
               flags=re.M)
    s = re.sub(r"^\s*writeInterval\s+.*$", f"writeInterval   {write_interval};",
               s, count=1, flags=re.M)
    s = re.sub(r"^\s*purgeWrite\s+.*$", "purgeWrite      0;", s, count=1,
               flags=re.M)
    s = re.sub(r"^\s*writePrecision\s+.*$",
               f"writePrecision  {write_precision};", s, count=1, flags=re.M)
    s = re.sub(r"^\s*writeFormat\s+.*$", "writeFormat     ascii;", s, count=1,
               flags=re.M)
    s = re.sub(r"^\s*runTimeModifiable\s+.*$", "runTimeModifiable no;", s,
               count=1, flags=re.M)
    open(path, "w").write(s)
    if libs:
        set_libs(path)          # insert-or-replace + assert (L-221)
    else:
        s = open(path).read()
        s = re.sub(r"^\s*libs\s*\([^;]*\);\s*$", "", s, flags=re.M)
        open(path, "w").write(s)


def write_turbulence_properties(case, ras, extra=""):
    body = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties;
}}

simulationType RAS;

RAS
{{
    RASModel        {ras};
    turbulence      on;
    printCoeffs     on;
{extra}}}
"""
    open(os.path.join(case, "constant", "turbulenceProperties"), "w").write(body)


def copy_skeleton(src, dst, with_fvoptions=True):
    """system/ + constant/{polyMesh,transportProperties} + caseDef."""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.join(dst, "0"))
    os.makedirs(os.path.join(dst, "constant"), exist_ok=True)
    shutil.copytree(os.path.join(src, "system"), os.path.join(dst, "system"))
    shutil.copytree(os.path.join(src, "constant", "polyMesh"),
                    os.path.join(dst, "constant", "polyMesh"))
    for f in ("transportProperties",):
        p = os.path.join(src, "constant", f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(dst, "constant", f))
    for f in ("caseDef", "fieldDef"):
        p = os.path.join(src, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(dst, f))
    if not with_fvoptions:
        p = os.path.join(dst, "system", "fvOptions")
        if os.path.exists(p):
            os.remove(p)


# --------------------------------------------------- strict completion rule
def run_complete(case, required_fields, endtime=None, logname=None):
    """STRICT COMPLETION RULE.  Returns (ok: bool, reason: str, info: dict).

    A run counts as complete only when ALL of:
      * a recorded rc == 0,
      * the log's last lines carry an "End" line,
      * the last time directory equals endTime in controlDict,
      * every required field is present in that time dir AND newer than 0/.
    """
    info = {}
    if not os.path.isdir(case):
        return False, "case directory absent", info
    logs = ([logname] if logname else
            sorted(f for f in os.listdir(case) if f.startswith("log.")))
    if not logs:
        return False, "no log file", info
    log = os.path.join(case, logs[-1])
    info["log"] = log
    rcf = os.path.join(case, "rc")
    if not os.path.exists(rcf):
        return False, "no recorded rc", info
    rc = open(rcf).read().strip()
    info["rc"] = rc
    if rc != "0":
        return False, f"rc={rc}", info
    tail = open(log, errors="replace").read()[-4000:]
    if not re.search(r"^End\s*$", tail, flags=re.M):
        return False, "no End line in log", info
    cd = os.path.join(case, "system", "controlDict")
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+);", open(cd).read(), flags=re.M)
    et = m.group(1) if m else None
    info["endTime"] = et
    lt = latest_time(case)
    info["latest_time"] = lt
    if endtime is None and et is not None and float(lt) != float(et):
        return False, f"last time {lt} != endTime {et}", info
    tdir = os.path.join(case, lt)
    zero = os.path.join(case, "0")
    for f in required_fields:
        fp = os.path.join(tdir, f)
        if not os.path.exists(fp):
            return False, f"missing field {f} in {lt}/", info
        zp = os.path.join(zero, f)
        if os.path.exists(zp) and os.path.getmtime(fp) <= os.path.getmtime(zp):
            return False, f"field {f} not newer than 0/", info
    return True, "complete", info


def frozen_complete(case):
    """STRICT COMPLETION RULE, frozen-extraction variant.

    `kCorrectiveFrozenFoam` breaks out of the time loop at its own settle
    criterion and calls writeNow(), so the last time directory is the settle
    iteration, NOT controlDict's endTime (which is only the backstop cap).
    The rule is applied with the settle iteration read from the log standing in
    for endTime, and the log's own SETTLED marker added as a fifth condition.
    """
    info = {}
    if not os.path.isdir(case):
        return False, "case directory absent", info
    log = os.path.join(case, "log.frozen")
    if not os.path.exists(log):
        return False, "no log.frozen", info
    rcf = os.path.join(case, "rc")
    if not os.path.exists(rcf):
        return False, "no recorded rc", info
    rc = open(rcf).read().strip()
    info["rc"] = rc
    if rc != "0":
        return False, f"rc={rc}", info
    txt = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", txt, flags=re.M):
        return False, "no End line in log", info
    if "NOT CONVERGED" in txt:
        return False, "log says NOT CONVERGED (backstop cap reached)", info
    m = re.search(r"CONVERGED \(settle criterion\) at iteration (\d+)", txt)
    if not m:
        return False, "no settle-criterion line in log", info
    info["converged_at"] = int(m.group(1))
    m2 = re.search(r"L2\(R\) moved ([0-9.eE+-]+)% .*?\[(SETTLED|NOT SETTLED)\]",
                   txt, flags=re.S)
    if not m2:
        return False, "no settle-verification line in log", info
    info["R_drift_pct"] = float(m2.group(1))
    info["settled"] = m2.group(2)
    if m2.group(2) != "SETTLED":
        return False, f"settle verification returned {m2.group(2)}", info
    m3 = re.search(r"Writing fields at iteration (\d+)", txt)
    info["write_iter"] = int(m3.group(1)) if m3 else None
    # A sixth condition, added after the first R4 extraction pass measured the
    # failure it catches: `bound(omega, omegaMin)` replaces every negative
    # omega cell with a local average, so a run whose omega is clipped on every
    # iteration can satisfy "omega stopped changing" by having been clipped to
    # a constant.  Two hills reported CONVERGED at iteration 51 that way, with
    # a settle drift of exactly 0.0.  A clipped extraction is not an
    # extraction; the count before the field write is the test.
    pre = txt[:txt.index("Writing fields")] if "Writing fields" in txt else txt
    info["bounding_omega_before_write"] = pre.count("bounding omega")
    if info["bounding_omega_before_write"] > 0:
        return False, (f"omega bounded on {info['bounding_omega_before_write']} "
                       f"iterations before the write (clipped, not settled)"), info
    lt = latest_time(case)
    info["latest_time"] = lt
    if info["write_iter"] is not None and float(lt) != float(info["write_iter"]):
        return False, (f"last time {lt} != solver write iteration "
                       f"{info['write_iter']}"), info
    tdir = os.path.join(case, lt)
    zero = os.path.join(case, "0")
    for f in ("U", "k", "omega", "nut", "bijDelta", "kDeficit", "bijData",
              "grad(U)"):
        fp = os.path.join(tdir, f)
        if not os.path.exists(fp):
            return False, f"missing field {f} in {lt}/", info
        zp = os.path.join(zero, f)
        if os.path.exists(zp) and os.path.getmtime(fp) <= os.path.getmtime(zp):
            return False, f"field {f} not newer than 0/", info
    return True, "complete", info


# ------------------------- headerless LES lists (the DUCT family ships these)
CONSTRAINT_PATCH = {"empty", "cyclic", "cyclicAMI", "symmetry", "symmetryPlane",
                    "wedge", "processor", "processorCyclic",
                    "nonConformalCyclic"}


def patch_types(case_dir):
    """[(name, type)] for every boundary patch, in constant/polyMesh order."""
    txt = open(os.path.join(case_dir, "constant", "polyMesh", "boundary")).read()
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    body = txt[txt.index("("):txt.rindex(")")]
    return [(m.group(1), m.group(2)) for m in
            re.finditer(r"(\w+)\s*\{[^{}]*?type\s+(\w+)\s*;", body, re.S)]


def _patch_field(ptype):
    return ptype if ptype in CONSTRAINT_PATCH else "zeroGradient"


def les_list_body(les_file):
    """'<name> nonuniform List<T>\\nN\\n(...);'  ->  ('List<T>', 'N\\n(...);')."""
    txt = open(les_file).read()
    head, rest = txt.split("\n", 1)
    m = re.search(r"(List<\w+>)", head)
    assert m, f"unexpected headerless LES field header in {les_file}: {head!r}"
    return m.group(1), rest.strip()


def splice_internal(bench_field, les_file, dst, obj):
    """Rewrite a benchmark field file's internalField with a headerless LES
    list, keeping ITS OWN boundaryField, dimensions and class untouched.

    Used for the DUCT family, whose `*_LES` files are bare value lists with no
    FoamFile header and no boundary values.  The boundary conditions therefore
    remain the benchmark's own (noSlip / cyclic / symmetry), not invented here.
    """
    typ, body = les_list_body(les_file)
    s = open(bench_field).read()
    s, n = re.subn(r"^(\s*object\s+)\S+;", rf"\g<1>{obj};", s, count=1,
                   flags=re.M)
    assert n == 1, f"no FoamFile object line in {bench_field}"
    s, n = re.subn(r"^internalField\s+[^;]*;",
                   f"internalField   nonuniform {typ}\n{body}",
                   s, count=1, flags=re.M | re.S)
    assert n == 1, f"no internalField entry in {bench_field}"
    open(dst, "w").write(s)


def write_field_from_les(les_file, dst, obj, ofclass, dims, pats):
    """Build a full field file around a headerless LES list.

    Constraint patches take their own type; every other patch takes
    zeroGradient.  Used only for the ducts' `tauij`, for which the benchmark
    ships no field file at all.  In `kOmegaSSTFrozen` the data stress enters
    the k budget through `bijData_() && tgradU()()` -- internal fields only --
    so the patch values do not enter the extracted `kDeficit` or `bijDelta`.
    """
    typ, body = les_list_body(les_file)
    L = [f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {ofclass};
    location    "0";
    object      {obj};
}}

dimensions      {dims};

internalField   nonuniform {typ}
{body}

boundaryField
{{"""]
    for pn, pt in pats:
        L.append(f"    {pn}\n    {{\n        type            "
                 f"{_patch_field(pt)};\n    }}")
    L.append("}\n")
    open(dst, "w").write("\n".join(L))


# ------------------------------------------- planted-zero READER control
# CLAUDE.md standing rule 3: "A zero from a reader that has not been shown able
# to see a non-zero is not evidence.  Every comparator plants a known
# perturbation, reads it back from disk, and REFUSES if the reader cannot see
# it."  The lab's constant is PLANT = 1.234e-03.
PLANT = 1.234e-03


def planted_zero_reader_check(field_path, reader, scratch):
    """Plant PLANT into a scratch copy of an OpenFOAM field ON DISK, read it
    back with the SAME reader the comparator uses, and refuse if the reader
    cannot see it.  Returns the measured recovery; raises SystemExit(2) if the
    plant is not recovered to 1e-12.
    """
    import numpy as np
    s = open(field_path).read()
    i = s.index("internalField")
    j = s.index("boundaryField")
    head, body, tail = s[:i], s[i:j], s[j:]

    def bump(m):
        return f"{float(m.group(0)) + PLANT:.17g}"

    # first scalar of every parenthesised tuple, or every bare scalar
    if "(" in body.split("\n", 3)[3]:
        body2 = re.sub(r"\(\s*(-?[\d.eE+-]+)",
                       lambda m: "(" + f"{float(m.group(1)) + PLANT:.17g}",
                       body)
    else:
        body2 = re.sub(r"^\s*(-?\d[\d.eE+-]*)\s*$",
                       lambda m: f"{float(m.group(1)) + PLANT:.17g}",
                       body, flags=re.M)
    os.makedirs(os.path.dirname(scratch), exist_ok=True)
    open(scratch, "w").write(head + body2 + tail)
    a = np.asarray(reader(field_path), dtype=float).reshape(-1)
    b = np.asarray(reader(scratch), dtype=float).reshape(-1)
    if a.size != b.size:
        raise SystemExit(2)
    # only the planted component moved; take the maximum recovered delta
    d = b - a
    moved = d[np.abs(d) > 0]
    err = float(np.abs(moved - PLANT).max()) if moved.size else float("inf")
    # The recovery tolerance must be double-precision aware, not absolute: the
    # plant is recovered as (x + PLANT) - x, and where the field itself is
    # O(1e5) -- which it is on the hills, whose k_LES <= 0 cells carry
    # b^Delta ~ 3.5e4 -- the representable resolution at x is already
    # ~1e-11, so an absolute 1e-12 bar would refuse a perfect reader on
    # arithmetic grounds.  The bar is machine epsilon at the largest value in
    # the field, floored at 1e-12, and the achieved value is reported either
    # way.  The MEDIAN recovery is also required to match PLANT to 1e-9
    # relative, so a reader that loses the plant on most cells cannot pass on
    # a lenient maximum.
    amax = float(np.abs(a).max())
    tol = max(1e-12, 8.0 * np.finfo(float).eps * amax)
    med = float(np.median(moved)) if moved.size else float("nan")
    rel_med = abs(med / PLANT - 1.0) if moved.size else float("inf")
    ok = moved.size > 0 and err <= tol and rel_med <= 1e-9
    print(f"[planted-zero reader control] {os.path.basename(field_path)}: "
          f"plant={PLANT:g} recovered on {moved.size} values, "
          f"max|recovered-plant|={err:.3g} (tol {tol:.3g}, field max "
          f"{amax:.3g}), median recovery {med:.12g} -> "
          f"{'PASS' if ok else 'REFUSED'}")
    if not ok:
        raise SystemExit(2)
    return dict(field=field_path, plant=PLANT, n_moved=int(moved.size),
                max_abs_error=err, tolerance=tol, field_max_abs=amax,
                median_recovery=med, median_relative_error=rel_med,
                verdict="PASS")


def solve_complete(case, required=("U", "p", "k", "omega", "nut")):
    """STRICT COMPLETION RULE, simpleFoam-propagation variant.

    A propagation stops at its registered residualControl, not at endTime, so
    "last time == endTime" is replaced by "last time == the iteration the log
    says it stopped at", and the convergence state is carried as a separate,
    reported field rather than folded into the completion verdict:
      converged  -- SIMPLE solution converged (the registered stopping rule)
      cap-stop   -- endTime reached first; reported, never graded as converged
    """
    info = {}
    log = os.path.join(case, "log.solve")
    if not os.path.isdir(case) or not os.path.exists(log):
        return False, "no case directory or log.solve", info
    rcf = os.path.join(case, "rc")
    if not os.path.exists(rcf):
        return False, "no recorded rc", info
    info["rc"] = open(rcf).read().strip()
    if info["rc"] != "0":
        return False, f"rc={info['rc']}", info
    txt = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", txt, flags=re.M):
        return False, "no End line in log", info
    times = re.findall(r"^Time = (\d+)", txt, flags=re.M)
    if not times:
        return False, "no Time lines in log", info
    info["last_iteration"] = int(times[-1])
    m = re.search(r"SIMPLE solution converged in (\d+) iterations", txt)
    cd = open(os.path.join(case, "system", "controlDict")).read()
    et = re.search(r"^\s*endTime\s+([0-9.eE+-]+);", cd, flags=re.M)
    info["endTime"] = float(et.group(1)) if et else None
    info["stop_state"] = "converged" if m else "cap-stop"
    if m:
        info["converged_at"] = int(m.group(1))
    elif info["endTime"] is not None and info["last_iteration"] < info["endTime"]:
        return False, (f"neither converged nor reached endTime "
                       f"({info['last_iteration']} < {info['endTime']})"), info
    lt = latest_time(case)
    info["latest_time"] = lt
    if float(lt) != float(info["last_iteration"]):
        return False, (f"last time dir {lt} != last solver iteration "
                       f"{info['last_iteration']}"), info
    tdir, zero = os.path.join(case, lt), os.path.join(case, "0")
    for f in required:
        fp = os.path.join(tdir, f)
        if not os.path.exists(fp):
            return False, f"missing field {f} in {lt}/", info
        zp = os.path.join(zero, f)
        if os.path.exists(zp) and os.path.getmtime(fp) <= os.path.getmtime(zp):
            return False, f"field {f} not newer than 0/", info
    return True, f"complete ({info['stop_state']})", info
