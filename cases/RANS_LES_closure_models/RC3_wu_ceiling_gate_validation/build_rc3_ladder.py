#!/usr/bin/env python3
"""RC3 C-ladder builder -- the six registered configurations, per case.

Registration: cases/RANS_LES_closure_models/RC3_wu_ceiling_gate_validation/
PREREGISTRATION.md, section 3 (the C-ladder), section 8 (strict completion,
clause 7 the build guard), section 9 (anti-gaming register, what is FIXED) and
section 11 (this module's registered job and its registered refusals).

WHAT THIS MODULE IS FOR
-----------------------
It builds, from the READ-ONLY benchmark clone, the six configurations section 3
registers, for each of the three in-scope cases:

    C0 NULL  b^Delta = 0                       k transported
    C1       b^Delta = b_LES - b_RANS          k transported
    C2       b^Delta = b_LES - b_RANS          k frozen at k_base
    C3       b^Delta = b_LES - b_RANS          k frozen at k_LES
    C4       b^Delta supplied by rc3_fixedpoint.py (section 3.1)   k frozen at k_LES
    CX       b^Delta = C3's field, cell-permuted under the registered seed
                                                k frozen at k_LES

REGISTERED REFUSALS (section 11), every one a sys.exit(2), never an assert:
  * the libs entry absent after insertion,
  * a pre-existing time directory in the destination case (section 8 clause 7),
  * a missing benchmark field.

NO ast.Assert CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE (section 6.1, L-332 /
D476 section 31.3).  `assert` is deleted by `python3 -O`; every guard below is a
`refuse()` call, which raises SystemExit(2) under every interpreter flag.  This
file contains no `assert` statement at all, which `--selftest` verifies by
parsing its own source with `ast`.

CONVENTIONS RE-DERIVED FROM THE PREDECESSORS, NOT IMPORTED FROM THEM
--------------------------------------------------------------------
Standing rule 6 and section 1.5 forbid editing any file of the Wu or Kaandorp
chains, and section 6.1 forbids reusing their guard call sites (each of which is
an `assert`).  The two conventions this builder needs were therefore READ from
those files and re-implemented here:

  * b^Delta is `b_LES - b_RANS` -- Wu2018_PIML_RF/aposteriori/make_fields.py:5
    ("bijDelta := Delta b  (= b_LES - b_RANS convention)").  Because the RANS
    anisotropy is the Boussinesq one, b_RANS = -(nu_t/k) S, so the field written
    is  b_LES + (nu_t/k) S, masked where k underflows.  That is algebraically
    the same object the Kaandorp builder writes at
    Kaandorp2020_TBRF/aposteriori/setup_case.py:82 (`b_target + lin`), and the
    two chains' TRUTH rows are therefore the same injection.
  * freezing k is done by the EXISTING model kOmegaSSTCorrectedFrozenK from the
    EXISTING library libwu2018FrozenK.so (built by the frozenk lane; present at
    /home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/lib/).
    Section 9's anti-gaming row fixes the model as "the same solver the
    predecessors ran; no new solver is written" -- no new solver is written
    here, and the frozen-k model is one of the two the predecessors ran.
    Reported to the supervisor as a wording tension in the registration, not
    resolved by this module on its own authority.

REUSE, SCOPED (L-512)
---------------------
`r4_lib.latest_time` (R4_sparta_build/r4_lib.py:76) is reused UNMODIFIED for the
one job it does exactly -- highest-numbered non-zero time directory.  It is not
edited and not reimplemented.  `r4_lib.set_libs` is NOT reused: its guard is an
`assert` (r4_lib.py:112), which section 6.1 forbids for a guard, so the
insert-or-replace is re-implemented here with a disk read-back and sys.exit(2)
at every call site (L-221/L-222: a lesson is not applied until EVERY call site
checks).

WHAT THIS MODULE MAY NOT DO
---------------------------
It launches nothing.  It refuses to build anything at all while the
registration is DRAFT/UNFROZEN, because the registration's own opening block
says "NOTHING MAY RUN AGAINST THIS DOCUMENT" while `prereg_commit:` reads
PENDING_SUPERVISOR_FREEZE.  That refusal is `refuse_if_unfrozen()`; it clears
itself when the supervisor's freeze commit replaces the token with a sha.
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

from of_read import (read_field, latest_time_dir, sym_to_full,  # noqa: E402
                     anisotropy, structured_gradient)
import sst_baseline_metrics as SB                               # noqa: E402
import r4_lib                                                   # noqa: E402

PREREG = os.path.join(HERE, "PREREGISTRATION.md")
UNFROZEN_TOKEN = "PENDING_SUPERVISOR_FREEZE"

BENCH = "/home/ubuntu/closure-challenge-benchmark/data"
ROOT = "/home/ubuntu/closure-data/rc3/wu2018"

# Section 3: the case set, FIXED.  NASA_2DWMH is BLOCKED and is not here.
CASES = {
    "AR_1_Ret_360": (os.path.join(BENCH, "DUCT", "AR_1_Ret_360"), "duct"),
    "AR_3_Ret_360": (os.path.join(BENCH, "DUCT", "AR_3_Ret_360"), "duct"),
    "CBFS13700":    (os.path.join(BENCH, "CBFS"), "cbfs"),
}

SPARTA_LIB = "libspartaTurbulenceModels.so"
FROZENK_LIB = "libwu2018FrozenK.so"
MODEL_TRANSPORTED = "kOmegaSSTCorrected"
MODEL_FROZEN_K = "kOmegaSSTCorrectedFrozenK"

# Section 3, the C-ladder, verbatim in code.  `k` values: "transported",
# "frozen_base" (the shipped SST k), "frozen_LES" (k_LES).
CONFIGS = {
    "C0": {"bdelta": "zero",      "k": "transported"},
    "C1": {"bdelta": "truth",     "k": "transported"},
    "C2": {"bdelta": "truth",     "k": "frozen_base"},
    "C3": {"bdelta": "truth",     "k": "frozen_LES"},
    "C4": {"bdelta": "external",  "k": "frozen_LES"},
    "CX": {"bdelta": "scrambled", "k": "frozen_LES"},
}

SCRAMBLE_SEED = 20260910          # section 9, FIXED
BSCALE = 1.0                      # section 9, FIXED: no blending, no clipping
K_FLOOR_FRAC = 1e-4               # b^Delta = 0 where k_RANS underflows
ITER_CAP = 30000                  # section 10's iteration cap; a backstop, not a gate
WRITE_INTERVAL = 1000
PER_SOLVE_TIMEOUT_S = 3600        # section 10, registered enforcement
CAMPAIGN_WALL_CAP_S = 24000       # section 10, = 400 core-min at ranks 1
RANKS = 1                         # section 9/10, FIXED: serial

# Section 8 clause 4: the fields that must exist at the last written time.
REQUIRED_FIELDS = ("U", "p", "k", "omega", "nut", "phi")

# Benchmark fields without which no configuration can be built at all.
BENCH_FIELDS_ZERO = ("U_LES", "k_LES", "tauij_LES")
BENCH_FIELDS_TIME = ("U", "p", "k", "omega", "nut")


# --------------------------------------------------------------- refusals
def refuse(msg):
    """The only refusal primitive in this module.  Survives `python3 -O`."""
    sys.stderr.write("RC3 REFUSED (sys.exit 2): " + str(msg) + "\n")
    sys.stderr.flush()
    raise SystemExit(2)


def refuse_if_unfrozen(prereg_path=PREREG):
    """The registration's own opening block, made executable.

    While `prereg_commit:` reads PENDING_SUPERVISOR_FREEZE the document is
    DRAFT/UNFROZEN and says, in its first lines, that nothing may run against
    it.  Building a case IS running against it, so this refuses.  The freeze
    commit replaces the token with a sha and this clears itself.
    """
    if not os.path.exists(prereg_path):
        refuse("registration absent: " + prereg_path)
    txt = open(prereg_path, errors="replace").read()
    if UNFROZEN_TOKEN in txt:
        refuse("RC3 is DRAFT/UNFROZEN (" + UNFROZEN_TOKEN + " still in "
               + prereg_path + "); nothing may be built or run against it")
    return True


def _default_writer(path, text):
    open(path, "w").write(text)


def set_libs_or_refuse(control_dict, libs, _writer=_default_writer):
    """L-221/L-222: INSERT-OR-REPLACE the libs entry, then READ IT BACK.

    A bare str.replace is a silent no-op on a controlDict that carries no libs
    line, and the solve then runs the STOCK model and returns a field that looks
    like an answer.  The check is a disk read-back and a sys.exit(2) -- never an
    `assert`, which `python3 -O` deletes (section 6.1).

    `_writer` exists so the selftest can drive a writer that silently fails to
    land the entry and show that this guard FIRES.  It defaults to the real one.
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
    if len(re.findall(r"^\s*libs\s*\(", back, flags=re.M)) != 1:
        refuse("L-221: " + control_dict + " carries "
               + str(len(re.findall(r"^\s*libs\s*\(", back, flags=re.M)))
               + " top-level libs entries after insertion; expected exactly 1")
    return back


def guard_no_existing_times(dst):
    """Section 8 clause 7: refuse a case directory that already carries a `0`
    or any numeric time directory.  A rebuilt case starts from a clean copy or
    the item stops."""
    if not os.path.isdir(dst):
        return True
    bad = []
    for name in sorted(os.listdir(dst)):
        if not os.path.isdir(os.path.join(dst, name)):
            continue
        if name == "0" or re.fullmatch(r"[0-9]+(\.[0-9]+)?", name):
            bad.append(name)
    if bad:
        refuse("section 8 clause 7 build guard: " + dst
               + " already carries time directories " + ", ".join(bad)
               + "; a rebuilt case starts from a clean copy")
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
    missing = []
    for f in BENCH_FIELDS_ZERO:
        if not os.path.exists(os.path.join(src, "0", f)):
            missing.append("0/" + f)
    for f in BENCH_FIELDS_TIME:
        if not os.path.exists(os.path.join(src, t, f)):
            missing.append(t + "/" + f)
    if missing:
        refuse("missing benchmark field(s) in " + src + ": " + ", ".join(missing))
    return src, t


# ------------------------------------------------------- field arithmetic
def truth_bdelta(tag):
    """b^Delta = b_LES - b_RANS as an (N,6) symmTensor, (xx,xy,xz,yy,yz,zz).

    b_RANS is the Boussinesq anisotropy of the case's own converged SST field.
    Cells whose RANS k underflows (k <= K_FLOOR_FRAC * mean|k_LES|) carry 0, the
    convention both predecessor builders use.
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
    ok = okL & okR & np.isfinite(bL).all(axis=(1, 2)) & np.isfinite(bR).all(axis=(1, 2))
    bd = np.where(ok[:, None, None], bL - bR, 0.0)
    bd = np.nan_to_num(bd, nan=0.0, posinf=0.0, neginf=0.0)
    idx = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    return np.stack([bd[:, i, j] for i, j in idx], axis=1), int((~ok).sum()), d


def scramble_bdelta(b6, seed=SCRAMBLE_SEED):
    """Section 3.2: ONE permutation of the cell index array, applied identically
    to all six components, so every cell keeps a physically realisable tensor
    and only its LOCATION is destroyed.  The distribution is preserved exactly.
    """
    b6 = np.asarray(b6, float)
    if b6.ndim != 2 or b6.shape[1] != 6:
        refuse("scramble_bdelta expects an (N,6) array, got shape "
               + str(b6.shape))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(b6.shape[0])
    return b6[perm], perm


def b_linear_from_fields(C, U, nut, k, k_floor):
    """b_linear = -(nu_t / k) S(U), the anisotropy the solver recomputes from
    the CURRENT iterate every iteration.  Section 3.1's fixed point needs it
    read from a converged field, which is why it lives here and not inline."""
    A = structured_gradient(np.asarray(C, float), np.asarray(U, float))
    S = 0.5 * (A + A.transpose(0, 2, 1))
    k = np.asarray(k, float)
    nut = np.asarray(nut, float)
    ok = k > k_floor
    out = np.zeros_like(S)
    out[ok] = -(nut[ok] / k[ok])[:, None, None] * S[ok]
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0), ok


# ------------------------------------------------------------ OF writing
def patch_bcs(case, ncomp):
    """A `calculated` boundaryField for every non-constraint patch, matching the
    predecessors' convention so the shipped mesh's patch names are honoured."""
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
            rows = "\n".join("(" + " ".join("%.17g" % c for c in r) + ")" for r in a)
        internal = ("internalField   nonuniform List<" + typ + ">\n"
                    + str(a.shape[0]) + "\n(\n" + rows + "\n)\n;\n")
    open(path, "w").write(
        "FoamFile { version 2.0; format ascii; class " + cls
        + "; object " + obj + "; }\n"
        "dimensions      " + dims + ";\n" + internal + patch_bcs(case, ncomp))


def write_bdelta_and_verify(case, tdir, b6, _writer=None):
    """Write bijDelta and READ IT BACK through the scorer's own reader.

    Standing rule 3 applied to the WRITER: a builder not shown able to put a
    non-zero on disk is not shown to have built anything.  The tolerance is
    PLANT-RELATIVE, not an absolute 1e-15 (L-508: an absolute bar false-refuses
    on O(1)+ data and cost this team a legitimate instrument): it is machine
    epsilon at the largest magnitude in the field, floored at 1e-12.

    `_writer` is injectable so the selftest can drive a writer that lands
    corrupted values on disk and show that this guard FIRES.

    DISCLOSURE: section 11's registered refusal list for this module names three
    refusals and this is a fourth.  It is added under STANDING RULE 3, which
    binds whether or not a document repeats it, and it can only stop a
    mis-built case from ever running -- it can never move a verdict.  Flagged
    for the supervisor's section 3 check-1 to accept or strike.
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
def build(tag, cfg, bdelta6=None, root=ROOT, check_freeze=True):
    """Build one configuration of one case.  Returns a record dict.

    `bdelta6` is required for configuration C4 (section 3.1 supplies it from
    the outer fixed point) and is ignored for the other five, whose b^Delta is
    defined by section 3 and is computed here.
    """
    if check_freeze:
        refuse_if_unfrozen()
    if cfg not in CONFIGS:
        refuse("unregistered configuration: " + str(cfg)
               + " (registered: " + ", ".join(sorted(CONFIGS)) + ")")
    src, t0 = require_bench_fields(tag)
    spec = CONFIGS[cfg]
    dst = os.path.join(root, tag, cfg)

    guard_no_existing_times(dst)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(os.path.join(dst, "0"))
    os.makedirs(os.path.join(dst, "constant"))
    shutil.copytree(os.path.join(src, "system"), os.path.join(dst, "system"))
    shutil.copytree(os.path.join(src, "constant", "polyMesh"),
                    os.path.join(dst, "constant", "polyMesh"))
    tp_src = os.path.join(src, "constant", "transportProperties")
    if os.path.exists(tp_src):
        shutil.copy(tp_src, os.path.join(dst, "constant", "transportProperties"))
    if os.path.exists(os.path.join(src, "caseDef")):
        shutil.copy(os.path.join(src, "caseDef"), os.path.join(dst, "caseDef"))

    for f in REQUIRED_FIELDS:
        s = os.path.join(src, t0, f)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(dst, "0", f))

    # --- the k treatment (section 3, column 3)
    if spec["k"] == "frozen_LES":
        kles = os.path.join(src, "0", "k_LES")
        if not os.path.exists(kles):
            refuse("missing benchmark field 0/k_LES in " + src)
        txt = open(kles).read()
        txt2, n = re.subn(r"object\s+k_LES\s*;", "object      k;", txt, count=1)
        if n != 1:
            txt2 = txt
        open(os.path.join(dst, "0", "k"), "w").write(txt2)
    model = MODEL_TRANSPORTED if spec["k"] == "transported" else MODEL_FROZEN_K
    libs = ((SPARTA_LIB,) if spec["k"] == "transported"
            else (SPARTA_LIB, FROZENK_LIB))

    # --- b^Delta (section 3, column 2)
    nmask = 0
    if spec["bdelta"] == "zero":
        b6 = np.zeros((_ncells(dst), 6))
    elif spec["bdelta"] == "truth":
        b6, nmask, _ = truth_bdelta(tag)
    elif spec["bdelta"] == "scrambled":
        base, nmask, _ = truth_bdelta(tag)
        b6, _perm = scramble_bdelta(base)
    else:
        if bdelta6 is None:
            refuse("configuration C4 requires a b^Delta from rc3_fixedpoint.py; "
                   "none supplied for " + tag)
        b6 = np.asarray(bdelta6, float)
    b6 = BSCALE * np.asarray(b6, float)
    rb = write_bdelta_and_verify(dst, os.path.join(dst, "0"), b6)

    # kDeficit: the Wu chain is b-only (section 3's ladder names no R channel).
    write_of_field(os.path.join(dst, "0", "kDeficit"), "kDeficit",
                   "volScalarField", "[0 2 -3 0 0 0 0]", 0, dst, 1)

    # --- controlDict
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
    set_libs_or_refuse(cd, libs)          # L-222: EVERY call site checks

    # --- turbulenceProperties
    open(os.path.join(dst, "constant", "turbulenceProperties"), "w").write(
        "FoamFile { version 2.0; format ascii; class dictionary; "
        'location "constant"; object turbulenceProperties; }\n'
        "simulationType RAS;\n"
        "RAS { RASModel " + model + "; turbulence on; printCoeffs on; }\n")

    # --- fvSolution residualControl.  Frozen-k arms exclude k and omega from
    # the criterion, because those channels are not solved; the transported
    # arms keep them.  A convergence aid (L1-L5), disclosed, never answer-changing.
    fv = os.path.join(dst, "system", "fvSolution")
    txt = open(fv).read()
    if spec["k"] == "transported":
        block = ('    residualControl\n    {\n'
                 '        p               1e-6;\n'
                 '        U               1e-6;\n'
                 '        k               1e-6;\n'
                 '        omega           1e-6;\n    }')
    else:
        block = ('    residualControl\n    {\n'
                 '        "(U|Ux|Uy|Uz)"  1e-6;\n'
                 '        p               1e-6;\n    }')
    if "residualControl" in txt:
        txt = re.sub(r"\n\s*residualControl\s*\{[^{}]*\}", "\n" + block, txt,
                     count=1)
    else:
        txt = re.sub(r"(SIMPLE\s*\{)", r"\1\n" + block, txt, count=1)
    open(fv, "w").write(txt)

    # --- section 8 clause 6: 0/U is TOUCHED LAST, so it dates the build and
    # every field the solve writes must be newer than it.
    zu = os.path.join(dst, "0", "U")
    if not os.path.exists(zu):
        refuse("0/U absent after build in " + dst + "; the age guard of "
               "section 8 clause 6 would have no reference")
    os.utime(zu, None)

    return {"case": dst, "tag": tag, "config": cfg, "model": model,
            "libs": list(libs), "k_treatment": spec["k"],
            "bdelta_kind": spec["bdelta"], "n_masked_cells": nmask,
            "bdelta_roundtrip": rb, "endTime": ITER_CAP,
            "ranks": RANKS, "per_solve_timeout_s": PER_SOLVE_TIMEOUT_S,
            "benchmark_source": src, "benchmark_time": t0}


def _ncells(case_dir):
    u = os.path.join(case_dir, "0", "U")
    if not os.path.exists(u):
        refuse("0/U absent, cannot size the mesh: " + case_dir)
    return int(np.asarray(read_field(u), float).reshape(-1, 3).shape[0])


# ---------------------------------------------------------------- selftest
def _fires(fn, *a, **kw):
    """Run `fn` and report whether it refused with sys.exit(2).  A control that
    has only ever been run on good input is not a control (section 6)."""
    try:
        fn(*a, **kw)
    except SystemExit as e:
        return int(e.code or 0) == 2
    return False


def _mini_controldict(path, with_libs):
    body = ("FoamFile { version 2.0; format ascii; class dictionary; "
            "object controlDict; }\n"
            "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n"
            "application     simpleFoam;\n"
            "startFrom       startTime;\nstartTime       0;\n"
            "endTime         100;\nwriteInterval   10;\n")
    if with_libs:
        body += 'libs ( "libSomethingElse.so" );\n'
    open(path, "w").write(body)


def selftest():
    ok = []

    def note(name, passed, detail=""):
        ok.append((name, bool(passed), detail))

    # 0. No ast.Assert anywhere in this file (section 6.1 / L-332).
    tree = ast.parse(open(os.path.abspath(__file__)).read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    note("ast.Assert count == 0", n_assert == 0, "counted " + str(n_assert))

    tmp = tempfile.mkdtemp(prefix="rc3_build_selftest_")
    try:
        # 1. refuse_if_unfrozen fires on the token and clears without it.
        p = os.path.join(tmp, "PREREG_draft.md")
        open(p, "w").write("prereg_commit: " + UNFROZEN_TOKEN + "\n")
        note("unfrozen guard FIRES on the draft token",
             _fires(refuse_if_unfrozen, p))
        p2 = os.path.join(tmp, "PREREG_frozen.md")
        open(p2, "w").write("prereg_commit: 4e3c5bc6\n")
        note("unfrozen guard PASSES a frozen registration",
             refuse_if_unfrozen(p2) is True)
        note("unfrozen guard FIRES on an absent registration",
             _fires(refuse_if_unfrozen, os.path.join(tmp, "nope.md")))
        # The live registration is still DRAFT, so the guard must fire on it.
        note("unfrozen guard FIRES on the LIVE RC3 registration",
             _fires(refuse_if_unfrozen, PREREG))

        # 2. set_libs_or_refuse: insert, replace, and FIRE on a silent no-op.
        c1 = os.path.join(tmp, "cd_nolibs")
        _mini_controldict(c1, with_libs=False)
        back = set_libs_or_refuse(c1, (SPARTA_LIB, FROZENK_LIB))
        note("libs INSERT lands both libraries",
             SPARTA_LIB in back and FROZENK_LIB in back)
        c2 = os.path.join(tmp, "cd_haslibs")
        _mini_controldict(c2, with_libs=True)
        back2 = set_libs_or_refuse(c2, (SPARTA_LIB,))
        note("libs REPLACE removes the absent library and lands ours",
             SPARTA_LIB in back2 and "libSomethingElse" not in back2
             and len(re.findall(r"^\s*libs\s*\(", back2, flags=re.M)) == 1)
        c3 = os.path.join(tmp, "cd_sabotaged")
        _mini_controldict(c3, with_libs=False)
        note("libs guard FIRES when the write silently does not land (L-221)",
             _fires(set_libs_or_refuse, c3, (SPARTA_LIB,),
                    _writer=lambda pth, s: open(pth, "w").write(
                        s.replace(SPARTA_LIB, "libGONE.so"))))
        c4 = os.path.join(tmp, "cd_double")
        _mini_controldict(c4, with_libs=False)
        note("libs guard FIRES on a duplicated top-level entry",
             _fires(set_libs_or_refuse, c4, (SPARTA_LIB,),
                    _writer=lambda pth, s: open(pth, "w").write(
                        s + '\nlibs ( "' + SPARTA_LIB + '" );\n')))
        note("libs guard FIRES on an absent controlDict",
             _fires(set_libs_or_refuse, os.path.join(tmp, "nocd"), (SPARTA_LIB,)))

        # 3. guard_no_existing_times: fires on `0`, fires on a numeric dir,
        #    passes on a clean directory and on an absent one.
        d = os.path.join(tmp, "case_with_zero")
        os.makedirs(os.path.join(d, "0"))
        note("build guard FIRES on a pre-existing 0/ directory",
             _fires(guard_no_existing_times, d))
        d2 = os.path.join(tmp, "case_with_time")
        os.makedirs(os.path.join(d2, "788"))
        note("build guard FIRES on a pre-existing numeric time directory",
             _fires(guard_no_existing_times, d2))
        d3 = os.path.join(tmp, "case_clean")
        os.makedirs(os.path.join(d3, "system"))
        note("build guard PASSES a clean case directory",
             guard_no_existing_times(d3) is True)
        note("build guard PASSES an absent destination",
             guard_no_existing_times(os.path.join(tmp, "absent")) is True)

        # 4. require_bench_fields: fires on an unregistered tag and on a case
        #    whose benchmark fields are absent; passes on the real benchmark.
        note("benchmark guard FIRES on an unregistered case tag",
             _fires(require_bench_fields, "NASA_2DWMH"))
        fake = os.path.join(tmp, "fakebench")
        os.makedirs(os.path.join(fake, "0"))
        os.makedirs(os.path.join(fake, "100"))
        for f in BENCH_FIELDS_TIME:
            open(os.path.join(fake, "100", f), "w").write("x")
        open(os.path.join(fake, "0", "U_LES"), "w").write("x")
        saved = CASES.get("AR_1_Ret_360")
        CASES["AR_1_Ret_360"] = (fake, "duct")
        fired = _fires(require_bench_fields, "AR_1_Ret_360")
        CASES["AR_1_Ret_360"] = saved
        note("benchmark guard FIRES on a case missing 0/k_LES and 0/tauij_LES",
             fired)
        if os.path.isdir(CASES["AR_1_Ret_360"][0]):
            src, t = require_bench_fields("AR_1_Ret_360")
            note("benchmark guard PASSES the real AR_1_Ret_360 clone",
                 os.path.isdir(src) and t != "0", "latest time " + str(t))

        # 5. the scramble: distribution preserved EXACTLY, location destroyed,
        #    reproducible under the registered seed, and it refuses bad shapes.
        rng = np.random.default_rng(7)
        b6 = rng.normal(size=(500, 6))
        s1, p1 = scramble_bdelta(b6)
        s2, p2 = scramble_bdelta(b6)
        note("scramble preserves the tensor multiset exactly",
             np.array_equal(np.sort(s1, axis=0), np.sort(b6, axis=0)))
        note("scramble keeps each cell's six components together",
             all(np.array_equal(s1[i], b6[p1[i]]) for i in range(0, 500, 37)))
        note("scramble destroys location on most cells",
             int((s1 != b6).any(axis=1).sum()) > 400,
             "moved " + str(int((s1 != b6).any(axis=1).sum())) + " of 500")
        note("scramble is reproducible under the registered seed "
             + str(SCRAMBLE_SEED), np.array_equal(p1, p2))
        note("scramble REFUSES an array that is not (N,6)",
             _fires(scramble_bdelta, np.zeros((10, 3))))

        # 6. b_linear identity: for tau = (2/3)k I - 2 nu_t S, the Boussinesq
        #    anisotropy is exactly -(nu_t/k) S.  Checked on a synthetic field.
        n = 64
        C = np.stack([np.repeat(np.linspace(0, 1, 8), 8),
                      np.tile(np.linspace(0, 1, 8), 8),
                      np.zeros(n)], axis=1)
        U = np.stack([C[:, 1] * 2.0, np.zeros(n), np.zeros(n)], axis=1)
        k = np.full(n, 0.5)
        nut = np.full(n, 0.02)
        bl, okl = b_linear_from_fields(C, U, nut, k, 1e-6)
        A = structured_gradient(C, U)
        S = 0.5 * (A + A.transpose(0, 2, 1))
        want = -(nut / k)[:, None, None] * S
        note("b_linear = -(nu_t/k) S to machine precision",
             float(np.abs(bl - want).max()) < 1e-14,
             "max err %.3g" % float(np.abs(bl - want).max()))

        # 7. build() refuses an unregistered configuration and refuses C4 with
        #    no supplied field -- both under the freeze guard being bypassed.
        note("build REFUSES an unregistered configuration tag",
             _fires(build, "AR_1_Ret_360", "C9", None, tmp, False))
        note("build REFUSES C4 with no fixed-point field supplied",
             _fires(build, "AR_1_Ret_360", "C4", None, tmp, False))
        note("build REFUSES while the registration is DRAFT/UNFROZEN",
             _fires(build, "AR_1_Ret_360", "C0", None, tmp, True))

        # 8. the bijDelta round-trip guard FIRES when the writer truncates.
        cdir = os.path.join(tmp, "rtcase")
        os.makedirs(os.path.join(cdir, "0"))
        os.makedirs(os.path.join(cdir, "constant", "polyMesh"))
        open(os.path.join(cdir, "constant", "polyMesh", "boundary"), "w").write(
            "// * * *\n2\n(\n  inlet { type patch; }\n  walls { type wall; }\n)\n")
        good = np.arange(60, dtype=float).reshape(10, 6) * 0.1
        rb = write_bdelta_and_verify(cdir, os.path.join(cdir, "0"), good)
        note("bijDelta round-trip PASSES on a real write",
             rb["max_roundtrip_error"] <= rb["tolerance"],
             "err %.3g tol %.3g" % (rb["max_roundtrip_error"], rb["tolerance"]))
        def corrupting(path, b6, case):
            bad = np.asarray(b6, float).copy()
            bad[0, 0] = bad[0, 0] + 1.0
            write_of_field(path, "bijDelta", "volSymmTensorField",
                           "[0 0 0 0 0 0 0]", bad, case, 6)

        note("bijDelta round-trip FIRES when the writer lands corrupted "
             "values on disk",
             _fires(write_bdelta_and_verify, cdir, os.path.join(cdir, "0"),
                    good, corrupting))
        note("bijDelta round-trip FIRES on a shape mismatch",
             _fires(write_bdelta_and_verify, cdir, os.path.join(cdir, "0"),
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
    print("build_rc3_ladder selftest: %d/%d PASS" % (len(ok), len(ok)))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    sys.stderr.write(
        "build_rc3_ladder.py builds registered cases and therefore refuses "
        "while RC3 is DRAFT/UNFROZEN.  Run --selftest to exercise the "
        "instrument; the builder itself is the supervisor's to release.\n")
    refuse_if_unfrozen()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
