#!/usr/bin/env python3
"""RC4 case builder -- the three registered configurations N / T-b / T-bR.

Registration: cases/RANS_LES_closure_models/RC4_kaandorp_propagation_repair/
PREREGISTRATION.md -- section 3 (the configurations), section 5 P1 (the one
change), section 6.1 (no ast.Assert), section 8 (strict completion, clause 7
the build guard), section 10 (the anti-gaming register) and section 11 (this
module's registered job and its registered refusals).

THE THREE CONFIGURATIONS (section 3), verbatim in code
------------------------------------------------------
    N NULL   b^Delta = 0                    kDeficit = 0
    T-b      b^Delta = b_LES - b_RANS       kDeficit = 0        (the predecessor's TRUTH row)
    T-bR     b^Delta = b_LES - b_RANS       kDeficit = the frozen-RANS extracted R

`bScale` = 1.0 in every scored configuration; `k` and `omega` are TRANSPORTED,
never frozen -- freezing `k` is the sibling chain's variable and mixing it in
here would move two things at once (section 3, section 10).

THE ONE CHANGE, BUILT IN RATHER THAN HOPED FOR
----------------------------------------------
Section 5's P1 requires T-bR to differ from T-b in exactly one field file.
This builder does not build T-bR independently: it copies the finished T-b tree
byte for byte and then replaces exactly `<time>/kDeficit`.  P1 is therefore true
by construction AND verified afterwards by rc4_onechange.py, which is the
instrument that can fail.  Note that this deliberately differs from the
predecessor's post-hoc diagnostic, which copied BOTH the extracted `kDeficit`
AND the extracted `bijDelta` into its TRUTHR row
(Kaandorp2020_TBRF/aposteriori/frozen_R.py:125-126) and so moved two things;
section 3 registers T-bR's `b^Delta` as `b_LES - b_RANS`, the same field T-b
carries, which is what makes the comparison attributable.

REGISTERED REFUSALS (section 11), every one a sys.exit(2), never an assert:
  * the libs entry absent after insertion (L-221/L-222, at EVERY call site),
  * a pre-existing time directory in the destination (section 8 clause 7),
  * a missing benchmark field.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).  `--selftest` parses this file and requires zero.

NO RC2 MODULE IS IMPORTED, CALLED, EDITED OR EXTENDED (section 11).  No file
under Kaandorp2020_TBRF/aposteriori/ is edited: `setup_case.py` and
`frozen_R.py` were READ for their method and are RE-IMPLEMENTED here, which is
also what section 6.1 requires, since every guard at those call sites is an
`assert` that `python3 -O` deletes.

REUSE, SCOPED (L-512): `r4_lib.latest_time` (R4_sparta_build/r4_lib.py:76) is
reused UNMODIFIED for the one job it does exactly.  `r4_lib.set_libs` is NOT
reused -- its guard is an `assert` (r4_lib.py:112).

NOTHING IS LAUNCHED.  Every build entry point refuses while the registration
carries PENDING_SUPERVISOR_FREEZE, which is the registration's own opening
clause ("NOTHING MAY RUN AGAINST THIS DOCUMENT") made executable.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CLOSURE = os.path.dirname(HERE)
COMMON = os.path.join(CLOSURE, "_common")
R4 = os.path.join(CLOSURE, "R4_sparta_build")
for _p in (COMMON, R4):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from of_read import read_field, sym_to_full, anisotropy       # noqa: E402
import sst_baseline_metrics as SB                             # noqa: E402
import r4_lib                                                 # noqa: E402

PREREG = os.path.join(HERE, "PREREGISTRATION.md")
UNFROZEN_TOKEN = "PENDING_SUPERVISOR_FREEZE"

BENCH = "/home/ubuntu/closure-challenge-benchmark/data"
ROOT = "/home/ubuntu/closure-data/rc4/kaandorp"

# Section 3: the case set, FIXED.  BFS5100 is BLOCKED (not on disk); PHLL10595
# is out of scope for the graded ladder and appears only as evidence.
CASES = {
    "AR_1_Ret_360": (os.path.join(BENCH, "DUCT", "AR_1_Ret_360"), "duct"),
    "AR_3_Ret_360": (os.path.join(BENCH, "DUCT", "AR_3_Ret_360"), "duct"),
    "CBFS13700":    (os.path.join(BENCH, "CBFS"), "cbfs"),
}

SPARTA_LIB = "libspartaTurbulenceModels.so"
MODEL = "kOmegaSSTCorrected"          # section 10, FIXED; no new solver written
CONFIGS = ("N", "T-b", "T-bR")
TIME0 = "0"                           # the input time directory, `<time>` in P1
KDEFICIT = "kDeficit"

BSCALE = 1.0                          # section 10, FIXED
K_FLOOR_FRAC = 1e-4
ITER_CAP = 30000                      # section 9's iteration cap; a backstop
WRITE_INTERVAL = 1000
PER_SOLVE_TIMEOUT_S = 3600            # section 9, registered enforcement
CAMPAIGN_WALL_CAP_S = 21000           # section 9, = 350 core-min at ranks 1
RANKS = 1                             # section 9/10, FIXED: serial

# Section 8 clause 4: kDeficit is in the list, "because it is the field this
# item exists to change, and a T-bR row without it on disk did not run the
# configuration it claims".
REQUIRED_FIELDS = ("U", "p", "k", "omega", "nut", "phi", KDEFICIT)
COPY_FIELDS = ("U", "p", "k", "omega", "nut", "phi")

BENCH_FIELDS_ZERO = ("U_LES", "k_LES", "tauij_LES")
BENCH_FIELDS_TIME = ("U", "p", "k", "omega", "nut")


def refuse(msg):
    sys.stderr.write("RC4 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


def refuse_if_unfrozen(prereg_path=PREREG):
    """The registration's own opening block, made executable.  Clears itself
    when the freeze commit replaces the token with a sha."""
    if not os.path.exists(prereg_path):
        refuse("registration absent: " + prereg_path)
    if UNFROZEN_TOKEN in open(prereg_path, errors="replace").read():
        refuse("RC4 is DRAFT/UNFROZEN (" + UNFROZEN_TOKEN + " still in "
               + prereg_path + "); nothing may be built or run against it")
    return True


def _default_writer(path, text):
    open(path, "w").write(text)


def set_libs_or_refuse(control_dict, libs=(SPARTA_LIB,), _writer=_default_writer):
    """L-221/L-222: INSERT-OR-REPLACE, then READ BACK FROM DISK and refuse.

    Never an `assert` (section 6.1).  The predecessor's equivalent guards --
    frozen_R.py:79, setup_case.py:115, setup_case.py:124 -- are all asserts and
    vanish under `python3 -O`, letting the solve run WITHOUT the model while
    returning a field that looks like an answer.  `_writer` is injectable so
    the selftest can drive a silent no-op and show this guard FIRES.
    """
    if not os.path.exists(control_dict):
        refuse("controlDict absent: " + control_dict)
    s = open(control_dict).read()
    entry = "libs ( " + " ".join('"' + lib + '"' for lib in libs) + " );"
    if re.search(r"^\s*libs\s*\(", s, flags=re.M):
        s = re.sub(r"^\s*libs\s*\([^;]*\);[ \t]*$", entry, s, count=1, flags=re.M)
    else:
        m = re.search(r"^// \* \*.*$", s, flags=re.M)
        pos = m.end() if m else 0
        s = s[:pos] + "\n\n" + entry + "\n" + s[pos:]
    _writer(control_dict, s)
    back = open(control_dict).read()
    missing = [lib for lib in libs if lib not in back]
    if missing:
        refuse("L-221: libs entry did not land in " + control_dict
               + "; missing after read-back: " + ", ".join(missing))
    n = len(re.findall(r"^\s*libs\s*\(", back, flags=re.M))
    if n != 1:
        refuse("L-221: " + control_dict + " carries " + str(n)
               + " top-level libs entries after insertion; expected exactly 1")
    return back


def guard_no_existing_times(dst):
    """Section 8 clause 7: refuse a destination that already carries `0` or any
    numeric time directory."""
    if not os.path.isdir(dst):
        return True
    bad = [n for n in sorted(os.listdir(dst))
           if os.path.isdir(os.path.join(dst, n))
           and (n == "0" or re.fullmatch(r"[0-9]+(\.[0-9]+)?", n))]
    if bad:
        refuse("section 8 clause 7 build guard: " + dst
               + " already carries time directories " + ", ".join(bad))
    return True


def require_bench_fields(tag):
    """Registered refusal: a missing benchmark field."""
    if tag not in CASES:
        refuse("unregistered case tag: " + str(tag))
    src = CASES[tag][0]
    if not os.path.isdir(src):
        refuse("benchmark case absent: " + src)
    t = r4_lib.latest_time(src)
    if t == "0":
        refuse("benchmark case has no non-zero time directory: " + src)
    missing = ["0/" + f for f in BENCH_FIELDS_ZERO
               if not os.path.exists(os.path.join(src, "0", f))]
    missing += [t + "/" + f for f in BENCH_FIELDS_TIME
                if not os.path.exists(os.path.join(src, t, f))]
    if missing:
        refuse("missing benchmark field(s) in " + src + ": " + ", ".join(missing))
    return src, t


# ------------------------------------------------------- field arithmetic
def truth_bdelta(tag):
    """b^Delta = b_LES - b_RANS as an (N,6) symmTensor.

    b_RANS is the Boussinesq anisotropy -(nu_t/k) S of the case's own converged
    SST field, so the field written is b_LES + (nu_t/k) S, masked where the RANS
    k underflows -- algebraically the object the predecessor writes at
    setup_case.py:82, re-derived here rather than imported.
    """
    src, fam = CASES[tag]
    d = SB.load_case(tag, src, fam)
    kL = np.asarray(d["k_LES"], float)
    kref = float(np.mean(np.abs(kL)))
    bL, okL = anisotropy(sym_to_full(np.asarray(d["tau_LES"], float)), kL,
                         k_ref=kref)
    k = np.asarray(d["k"], float)
    bR, okR = anisotropy(sym_to_full(np.asarray(d["tau_R"], float)), k,
                         k_ref=kref)
    ok = (okL & okR & np.isfinite(bL).all(axis=(1, 2))
          & np.isfinite(bR).all(axis=(1, 2)))
    bd = np.nan_to_num(np.where(ok[:, None, None], bL - bR, 0.0),
                       nan=0.0, posinf=0.0, neginf=0.0)
    idx = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    return np.stack([bd[:, i, j] for i, j in idx], axis=1), int((~ok).sum()), d


# ------------------------------------------------------------ OF writing
def patch_bcs(case, ncomp):
    bpath = os.path.join(case, "constant", "polyMesh", "boundary")
    if not os.path.exists(bpath):
        refuse("polyMesh/boundary absent in " + case)
    txt = open(bpath).read()
    body = txt[txt.index("// *"):]
    zero = "0" if ncomp == 1 else "(" + " ".join(["0"] * ncomp) + ")"
    out = []
    for n, blk in re.findall(r"(\w+)\s*\{([^}]*)\}", body, re.S):
        m = re.search(r"type\s+(\w+)\s*;", blk)
        if m is None:
            continue
        t = m.group(1)
        if t in ("cyclic", "empty", "symmetry", "symmetryPlane", "wedge"):
            out.append("    " + n + " { type " + t + "; }")
        else:
            out.append("    " + n + " { type calculated; value uniform "
                       + zero + "; }")
    return "boundaryField\n{\n" + "\n".join(out) + "\n}\n"


def write_of_field(path, obj, cls, dims, data, case, ncomp):
    if np.isscalar(data):
        v = str(data) if ncomp == 1 else "(" + " ".join([str(data)] * ncomp) + ")"
        internal = "internalField   uniform " + v + ";\n"
    else:
        a = np.asarray(data, float)
        typ = "scalar" if ncomp == 1 else "symmTensor"
        if ncomp == 1:
            rows = "\n".join("%.17g" % v for v in a)
        else:
            rows = "\n".join("(" + " ".join("%.17g" % c for c in r) + ")"
                             for r in a)
        internal = ("internalField   nonuniform List<" + typ + ">\n"
                    + str(a.shape[0]) + "\n(\n" + rows + "\n)\n;\n")
    open(path, "w").write(
        "FoamFile { version 2.0; format ascii; class " + cls + "; object "
        + obj + "; }\n" + "dimensions      " + dims + ";\n" + internal
        + patch_bcs(case, ncomp))


def write_bdelta_and_verify(case, tdir, b6, _writer=None):
    """Write bijDelta and read it back through the scorer's own reader.

    Standing rule 3 applied to the WRITER.  The tolerance is PLANT-RELATIVE --
    machine epsilon at the field's own largest magnitude, floored at 1e-12 --
    never an absolute 1e-15 (L-508: an absolute bar false-refuses on O(1)+ data
    and destroyed a legitimate instrument in this team).

    `_writer` is injectable so the selftest can drive a writer that lands
    corrupted values on disk and show that this guard FIRES.

    DISCLOSURE: section 11's registered refusal list for this module names
    three refusals and this is a fourth, added under STANDING RULE 3.  It can
    only stop a mis-built case from ever running; it can never move a verdict.
    Flagged for the supervisor's section 3 check-1 to accept or strike.
    """
    path = os.path.join(tdir, "bijDelta")
    if _writer is None:
        write_of_field(path, "bijDelta", "volSymmTensorField",
                       "[0 0 0 0 0 0 0]", b6, case, 6)
    else:
        _writer(path, b6, case)
    back = np.asarray(read_field(path), float).reshape(-1, 6)
    want = np.asarray(b6, float).reshape(-1, 6)
    if back.shape != want.shape:
        refuse("bijDelta read-back shape " + str(back.shape) + " != written "
               + str(want.shape) + " in " + path)
    amax = float(np.abs(want).max()) if want.size else 0.0
    tol = max(1e-12, 8.0 * float(np.finfo(float).eps) * amax)
    err = float(np.abs(back - want).max()) if want.size else 0.0
    if err > tol:
        refuse("bijDelta did not survive the round trip in " + path
               + ": max|read-written| = %.3g > tol %.3g (field max %.3g)"
               % (err, tol, amax))
    return {"path": path, "max_roundtrip_error": err, "tolerance": tol,
            "field_max_abs": amax, "n_cells": int(want.shape[0])}


# ------------------------------------------------------------- the build
def _base_case(tag, cfg, root):
    """Everything N and T-b share; T-bR never comes through here."""
    src, t0 = require_bench_fields(tag)
    dst = os.path.join(root, tag, cfg)
    guard_no_existing_times(dst)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(os.path.join(dst, TIME0))
    os.makedirs(os.path.join(dst, "constant"))
    shutil.copytree(os.path.join(src, "system"), os.path.join(dst, "system"))
    shutil.copytree(os.path.join(src, "constant", "polyMesh"),
                    os.path.join(dst, "constant", "polyMesh"))
    tp = os.path.join(src, "constant", "transportProperties")
    if os.path.exists(tp):
        shutil.copy(tp, os.path.join(dst, "constant", "transportProperties"))
    if os.path.exists(os.path.join(src, "caseDef")):
        shutil.copy(os.path.join(src, "caseDef"), os.path.join(dst, "caseDef"))
    for f in COPY_FIELDS:
        p = os.path.join(src, t0, f)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(dst, TIME0, f))

    cd = os.path.join(dst, "system", "controlDict")
    s = open(cd).read()
    s = re.sub(r"^\s*libs.*$", "", s, flags=re.M)
    s = re.sub(r"^startFrom.*$", "startFrom       startTime;", s, flags=re.M)
    if re.search(r"^startTime\s+", s, flags=re.M):
        s = re.sub(r"^startTime\s+.*$", "startTime       0;", s, flags=re.M)
    else:
        s = re.sub(r"^startFrom.*$",
                   "startFrom       startTime;\nstartTime       0;", s, flags=re.M)
    s = re.sub(r"^endTime\s+.*$", "endTime         " + str(ITER_CAP) + ";",
               s, flags=re.M)
    s = re.sub(r"writeInterval\s+\$endTime",
               "writeInterval   " + str(WRITE_INTERVAL), s)
    s = re.sub(r"^writeInterval\s+.*$",
               "writeInterval   " + str(WRITE_INTERVAL) + ";", s, flags=re.M)
    if re.search(r"^purgeWrite", s, flags=re.M):
        s = re.sub(r"^purgeWrite.*$", "purgeWrite      2;", s, flags=re.M)
    else:
        s = s.replace("writeInterval   " + str(WRITE_INTERVAL) + ";",
                      "writeInterval   " + str(WRITE_INTERVAL)
                      + ";\npurgeWrite      2;", 1)
    i = s.find("functions")
    if i >= 0:
        s = s[:i] + "functions { }\n"
    open(cd, "w").write(s)
    set_libs_or_refuse(cd, (SPARTA_LIB,))       # L-222: EVERY call site checks

    open(os.path.join(dst, "constant", "turbulenceProperties"), "w").write(
        "FoamFile { version 2.0; format ascii; class dictionary; "
        'location "constant"; object turbulenceProperties; }\n'
        "simulationType RAS;\n"
        "RAS { RASModel " + MODEL + "; turbulence on; printCoeffs on; }\n")

    fv = os.path.join(dst, "system", "fvSolution")
    txt = open(fv).read()
    block = ('    residualControl\n    {\n'
             '        p               1e-6;\n'
             '        U               1e-6;\n'
             '        k               1e-6;\n'
             '        omega           1e-6;\n    }')
    if "residualControl" in txt:
        txt = re.sub(r"\n\s*residualControl\s*\{[^{}]*\}", "\n" + block, txt,
                     count=1)
    else:
        txt = re.sub(r"(SIMPLE\s*\{)", r"\1\n" + block, txt, count=1)
    open(fv, "w").write(txt)
    return dst, src, t0


def build(tag, cfg, kdeficit_src=None, root=ROOT, check_freeze=True):
    """Build one registered configuration.  Returns a record dict.

    T-bR is NOT built from scratch: it is a byte copy of the finished T-b tree
    with exactly `<time>/kDeficit` replaced, which is section 5's P1 made true
    by construction and then verified by rc4_onechange.py.
    """
    if check_freeze:
        refuse_if_unfrozen()
    if cfg not in CONFIGS:
        refuse("unregistered configuration: " + str(cfg)
               + " (registered: " + ", ".join(CONFIGS) + ")")

    if cfg == "T-bR":
        tb = os.path.join(root, tag, "T-b")
        if not os.path.isdir(tb):
            refuse("T-bR is built from the finished T-b tree, which is absent: "
                   + tb + ".  Build T-b first; building T-bR independently "
                   "would put more than one change between the two rows")
        if kdeficit_src is None:
            refuse("T-bR requires the frozen-RANS extracted kDeficit; none "
                   "supplied for " + tag + " (rc4_extract_R.py provides it, "
                   "and only after P-1 admits the case)")
        if not os.path.exists(kdeficit_src):
            refuse("extracted kDeficit absent: " + str(kdeficit_src))
        dst = os.path.join(root, tag, cfg)
        guard_no_existing_times(dst)
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(tb, dst, symlinks=True)
        shutil.copyfile(kdeficit_src, os.path.join(dst, TIME0, KDEFICIT))
        kd = np.asarray(read_field(os.path.join(dst, TIME0, KDEFICIT)),
                        float).reshape(-1)
        if not np.isfinite(kd).all():
            refuse("the extracted kDeficit copied into " + dst
                   + " carries non-finite values")
        if float(np.abs(kd).max()) == 0.0:
            refuse("the extracted kDeficit copied into " + dst + " is "
                   "identically zero, so T-bR is not a different "
                   "configuration from T-b and the item has no arm")
        zu = os.path.join(dst, TIME0, "U")
        if not os.path.exists(zu):
            refuse("0/U absent after build in " + dst)
        os.utime(zu, None)
        return {"case": dst, "tag": tag, "config": cfg, "model": MODEL,
                "built_from": tb, "kdeficit_source": kdeficit_src,
                "kdeficit_rms": float(np.sqrt((kd ** 2).mean())),
                "kdeficit_max_abs": float(np.abs(kd).max()),
                "endTime": ITER_CAP, "ranks": RANKS,
                "per_solve_timeout_s": PER_SOLVE_TIMEOUT_S}

    dst, src, t0 = _base_case(tag, cfg, root)
    nmask = 0
    if cfg == "N":
        n = int(np.asarray(read_field(os.path.join(dst, TIME0, "U")),
                           float).reshape(-1, 3).shape[0])
        b6 = np.zeros((n, 6))
    else:
        b6, nmask, _ = truth_bdelta(tag)
    rb = write_bdelta_and_verify(dst, os.path.join(dst, TIME0),
                                 BSCALE * np.asarray(b6, float))
    # Section 3: kDeficit is 0 in BOTH N and T-b.  T-b reproduces the
    # predecessor's TRUTH row exactly so the two ceilings sit side by side.
    write_of_field(os.path.join(dst, TIME0, KDEFICIT), KDEFICIT,
                   "volScalarField", "[0 2 -3 0 0 0 0]", 0, dst, 1)
    zu = os.path.join(dst, TIME0, "U")
    if not os.path.exists(zu):
        refuse("0/U absent after build in " + dst + "; section 8 clause 6's "
               "age guard would have no reference")
    os.utime(zu, None)         # clause 6: 0/U is touched LAST at case build
    return {"case": dst, "tag": tag, "config": cfg, "model": MODEL,
            "kdeficit": 0.0, "n_masked_cells": nmask, "bdelta_roundtrip": rb,
            "endTime": ITER_CAP, "ranks": RANKS,
            "per_solve_timeout_s": PER_SOLVE_TIMEOUT_S,
            "benchmark_source": src, "benchmark_time": t0}


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


def _mini_controldict(path, with_libs):
    body = ("FoamFile { version 2.0; format ascii; class dictionary; "
            "object controlDict; }\n"
            "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n"
            "application     simpleFoam;\nstartFrom       startTime;\n"
            "startTime       0;\nendTime         100;\nwriteInterval   10;\n")
    if with_libs:
        body += 'libs ( "libfrozenIncompressibleTurbulenceModels.so" );\n'
    open(path, "w").write(body)


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    tmp = tempfile.mkdtemp(prefix="rc4_build_selftest_")
    try:
        p = os.path.join(tmp, "draft.md")
        open(p, "w").write("prereg_commit: " + UNFROZEN_TOKEN + "\n")
        note("unfrozen guard FIRES on the draft token",
             _fires(refuse_if_unfrozen, p))
        p2 = os.path.join(tmp, "frozen.md")
        open(p2, "w").write("prereg_commit: de28101d\n")
        note("unfrozen guard PASSES a frozen registration",
             refuse_if_unfrozen(p2) is True)
        note("unfrozen guard FIRES on the LIVE RC4 registration",
             _fires(refuse_if_unfrozen, PREREG))

        c1 = os.path.join(tmp, "cd_nolibs")
        _mini_controldict(c1, with_libs=False)
        note("libs INSERT lands the sparta library",
             SPARTA_LIB in set_libs_or_refuse(c1))
        c2 = os.path.join(tmp, "cd_absentlib")
        _mini_controldict(c2, with_libs=True)
        back = set_libs_or_refuse(c2)
        note("libs REPLACE removes libfrozenIncompressibleTurbulenceModels.so, "
             "which exists nowhere on this machine",
             SPARTA_LIB in back and "libfrozenIncompressible" not in back)
        c3 = os.path.join(tmp, "cd_sabotage")
        _mini_controldict(c3, with_libs=False)
        note("libs guard FIRES when the write silently does not land (L-221; "
             "the predecessor's equivalent guard is an assert)",
             _fires(set_libs_or_refuse, c3, (SPARTA_LIB,),
                    _writer=lambda pth, s: open(pth, "w").write(
                        s.replace(SPARTA_LIB, "libGONE.so"))))
        c4 = os.path.join(tmp, "cd_dup")
        _mini_controldict(c4, with_libs=False)
        note("libs guard FIRES on a duplicated top-level entry",
             _fires(set_libs_or_refuse, c4, (SPARTA_LIB,),
                    _writer=lambda pth, s: open(pth, "w").write(
                        s + '\nlibs ( "' + SPARTA_LIB + '" );\n')))
        note("libs guard FIRES on an absent controlDict",
             _fires(set_libs_or_refuse, os.path.join(tmp, "nocd")))

        d = os.path.join(tmp, "with_zero")
        os.makedirs(os.path.join(d, "0"))
        note("build guard FIRES on a pre-existing 0/ directory",
             _fires(guard_no_existing_times, d))
        d2 = os.path.join(tmp, "with_time")
        os.makedirs(os.path.join(d2, "3450"))
        note("build guard FIRES on a pre-existing numeric time directory",
             _fires(guard_no_existing_times, d2))
        note("build guard PASSES a clean destination",
             guard_no_existing_times(os.path.join(tmp, "absent")) is True)

        note("benchmark guard FIRES on an out-of-scope case tag "
             "(PHLL10595 is evidence only, not a graded case)",
             _fires(require_bench_fields, "PHLL10595"))
        note("benchmark guard FIRES on the BLOCKED BFS5100",
             _fires(require_bench_fields, "BFS5100"))
        fake = os.path.join(tmp, "fakebench")
        os.makedirs(os.path.join(fake, "0"))
        os.makedirs(os.path.join(fake, "500"))
        for f in BENCH_FIELDS_TIME:
            open(os.path.join(fake, "500", f), "w").write("x")
        saved = CASES["CBFS13700"]
        CASES["CBFS13700"] = (fake, "cbfs")
        fired = _fires(require_bench_fields, "CBFS13700")
        CASES["CBFS13700"] = saved
        note("benchmark guard FIRES on a case missing its LES fields", fired)
        if os.path.isdir(CASES["AR_1_Ret_360"][0]):
            src, t = require_bench_fields("AR_1_Ret_360")
            note("benchmark guard PASSES the real AR_1_Ret_360 clone",
                 os.path.isdir(src) and t != "0", "latest time " + str(t))

        note("build REFUSES an unregistered configuration tag",
             _fires(build, "AR_1_Ret_360", "T-bRR", None, tmp, False))
        note("build REFUSES T-bR when T-b has not been built",
             _fires(build, "AR_1_Ret_360", "T-bR", None, tmp, False))
        tbdir = os.path.join(tmp, "AR_1_Ret_360", "T-b")
        os.makedirs(os.path.join(tbdir, TIME0))
        note("build REFUSES T-bR with no extracted kDeficit supplied",
             _fires(build, "AR_1_Ret_360", "T-bR", None, tmp, False))
        note("build REFUSES T-bR when the named kDeficit file is absent",
             _fires(build, "AR_1_Ret_360", "T-bR",
                    os.path.join(tmp, "nokd"), tmp, False))
        zerokd = os.path.join(tmp, "zero_kDeficit")
        open(zerokd, "w").write(
            "FoamFile { version 2.0; format ascii; class volScalarField; "
            "object kDeficit; }\ndimensions [0 2 -3 0 0 0 0];\n"
            "internalField   nonuniform List<scalar>\n3\n(\n0\n0\n0\n)\n;\n"
            "boundaryField { }\n")
        open(os.path.join(tbdir, TIME0, "U"), "w").write("0\n")
        note("build REFUSES an identically-zero extracted kDeficit -- T-bR "
             "would not be a different configuration from T-b",
             _fires(build, "AR_1_Ret_360", "T-bR", zerokd, tmp, False))
        note("build REFUSES while the registration is DRAFT/UNFROZEN",
             _fires(build, "AR_1_Ret_360", "N", None, tmp, True))

        cdir = os.path.join(tmp, "rt")
        os.makedirs(os.path.join(cdir, TIME0))
        os.makedirs(os.path.join(cdir, "constant", "polyMesh"))
        open(os.path.join(cdir, "constant", "polyMesh", "boundary"), "w").write(
            "// * * *\n2\n(\n inlet { type patch; }\n walls { type wall; }\n)\n")
        good = np.arange(60, dtype=float).reshape(10, 6) * 1e5
        rb = write_bdelta_and_verify(cdir, os.path.join(cdir, TIME0), good)
        note("bijDelta round-trip PASSES on O(1e6) data with a PLANT-RELATIVE "
             "tolerance (L-508: an absolute 1e-15 bar would false-refuse here)",
             rb["max_roundtrip_error"] <= rb["tolerance"],
             "err %.3g tol %.3g field max %.3g"
             % (rb["max_roundtrip_error"], rb["tolerance"], rb["field_max_abs"]))
        def corrupting(path, b6, case):
            bad = np.asarray(b6, float).copy()
            bad[0, 0] = bad[0, 0] + 1.0
            write_of_field(path, "bijDelta", "volSymmTensorField",
                           "[0 0 0 0 0 0 0]", bad, case, 6)

        note("bijDelta round-trip FIRES when the writer lands corrupted "
             "values on disk",
             _fires(write_bdelta_and_verify, cdir, os.path.join(cdir, TIME0),
                    good, corrupting))
        note("bijDelta round-trip FIRES on a shape mismatch",
             _fires(write_bdelta_and_verify, cdir, os.path.join(cdir, TIME0),
                    good,
                    lambda path, b6, case: write_of_field(
                        path, "bijDelta", "volSymmTensorField",
                        "[0 0 0 0 0 0 0]", np.asarray(b6)[:3], case, 6)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    width = max(len(n) for n, _, _ in ok)
    for name, passed, detail in ok:
        print(("  %-" + str(width) + "s  %s%s")
              % (name, "PASS" if passed else "FAIL",
                 ("   [" + detail + "]") if detail else ""))
    bad = [n for n, p, _ in ok if not p]
    if bad:
        sys.stderr.write("SELFTEST FAILED: " + "; ".join(bad) + "\n")
        raise SystemExit(1)
    print("build_rc4_cases selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    sys.stderr.write(
        "build_rc4_cases.py builds registered cases and therefore refuses "
        "while RC4 is DRAFT/UNFROZEN.  Run --selftest to exercise the "
        "instrument; the builder itself is the supervisor's to release.\n")
    refuse_if_unfrozen()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
