#!/usr/bin/env python3
"""VMFLGPU005 -- graded comparator. Tall differentially-heated cavity (Betts &
Bokhari 2000, IJHFF 21, 675-683, EXPERIMENTAL); manual p.235; CPU parent VMFL052.

    grade_vmflgpu005.py --run-root <dir>   grade a completed run
    grade_vmflgpu005.py --selftest         drive every guard, exit 0/1

OBJECT UNDER VERIFICATION: the lab's GPU solver path (OpenFOAM v2606
buoyantBoussinesqSimpleFoam + petsc4Foam + PETSc-CUDA on the L4). NOT Ansys.

MODEL (frozen by the supervisor from import_files/VMFL052_natural.cas):
standard k-omega (kw-std-on? #t), low-Re correction (kw-low-re-mod? #t),
integrate-to-wall -- reproduced as OpenFOAM kOmega on a boundary-layer-resolving
r=2 triple with CONTINUOUS (tanh) wall functions.

NO `assert` ANYWHERE. `python3 -O` strips assert, so a guard built on one
evaporates exactly when run for speed. Every refusal is an explicit branch into
refuse(). Driven under both interpreters by --selftest.

EVERY PLANTED FAILURE ASSERTS THE EXPECTED REFUSAL TEXT, never merely a non-zero
exit (L-357).

------------------------------------------------------------------------------
THE GATE (PREREGISTRATION sections 4-7), and what each limb may earn:

  LIMB A  GPU EXECUTION -- binary, physics-critical. PETSc -log_view per-event
          accounting PARSED BY COLUMN POSITION AGAINST THE TABLE'S OWN HEADER:
          GPU %F is the FINAL column, CpuToGpu Count is the 5th-from-last. The
          GPU arm must show GPU %F >= GPU_PCTF_MIN and CpuToGpu Count > 0; the
          forced-CPU control must show GPU %F == 0 and CpuToGpu Count == 0.
          REFUSES on GPU %F > 100 (a percentage cannot exceed 100 -- the exact
          guard that would have caught VMFLGPU007's silent false pass, where a
          max()-of-trailing-tokens reader returned the CpuToGpu SIZE IN MBYTES
          210 and cleared a 99.0 floor). An ABSENT table REFUSES, never read as 0.
          This reader is DRIVEN in --selftest on the REAL frozen bytes of
          VMFLGPU007's own gpu and cpu -log_view tables (reference/REAL_LOGVIEW_*).

  LIMB B  |q_GPU - q_CPU| / |q_CPU| <= BAND_B at EVERY level. PASS-CAPABLE:
          identical mesh, identical scheme, so discretisation error cancels on
          both sides and no triple is needed to make the claim.

  LIMB C1 MID-HEIGHT physics vs Betts & Bokhari TABLE 1 (first-hand experimental
          digits, LOWER-Ra column = this case): C1a average Nusselt number 5.85;
          C1b max mean vertical velocity 0.139 m/s; C1c centre-line dT/dx 68 K/m.
          CEILING: TIER_CEILING_C1 = "PASS", earned ONLY on a CONVERGING Roache
          triple inside band. The PASS-capability is contingent on the CONVERGING
          TRIPLE (systematic refinement, rule 5), NOT on the reference kind alone.

  LIMB C2 Y/h = 0.05 physics vs the VMFL052 archive CSV (Ansys's DIGITISATION of
          the paper's figure -- DOUBLY INDIRECT): peak up-flow +0.147826 m/s,
          peak down-flow -0.081739 m/s, core temperature. CEILING:
          TIER_CEILING_C2 = "GATE REACHED", never PASS, hard-coded and
          selftest-enforced. Reproduces the manual's OWN comparison.

  Paper (C1) and CSV (C2) are SEPARATE channels; a disagreement between them is
  REPORTED, never averaged, never reconciled (PREREGISTRATION section 5 clause).

  ROACHE TRIPLE (rule 5), applied to every gated physics channel on the GPU arm:
  (1) any level not iteratively converged/plateaued -> NOT A RESULT; (2) triple
  not CONVERGING (DIVERGENT/OSCILLATORY/STAGNANT/EXACT, or observed order below
  P_MIN) -> NOT A RESULT, value and triple printed; (3) CONVERGING -> PASS/GATE
  REACHED inside band else GATE FAIL, GCI at Fs=1.25 printed. No GCI when the
  three values are not monotone. The gate can only turn a PASS/GATE REACHED/GATE
  FAIL INTO NOT A RESULT, never the reverse.
------------------------------------------------------------------------------
"""
import argparse
import glob
import math
import os
import re
import shutil
import sys
import tempfile

VERSION = "VMFLGPU005-comparator-1.0-s2"
# ---------------------------------------------------------------- SUCCESSOR S2
# S2 (2026-08-28) is grade_vmflgpu005.py's SUCCESSOR under CLAUDE.md rule 2: the
# parent (blob f80254fd712b1cda5a86908de2ad92f4cc85f062) is FROZEN and is NOT
# edited. S2 differs from it in ONE thing only -- the planted-zero control (rule
# 3) -- rebuilt to meet Sanaa's 2026-08-28 birth requirement: the plant must
# travel the REAL production path (written into the real sample file on disk,
# read BACK through the parent's own unmodified read_line()), not injected
# downstream of the reader as the parent did (it mutated the already-parsed rows
# and re-ran only the c1b_vmax reducer). Every band, threshold, ceiling, tier,
# limb, refusal clause, completion clause, Roache classifier and physics
# constant is byte-identical to the parent; the only other differences are this
# header, the two imports added above, the one call-site line that feeds the
# control a case directory instead of parsed rows, and the control's --selftest
# arms.

# ------------------------------------------------------------------ VOCABULARY
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
# VERIFICATION_CHARTER §2f.3: a CONTINUUM limb (value vs experiment/correlation/
# exact/manufactured solution) is capped at GATE REACHED -- PASS is unavailable,
# and §2h.4 cond.1's floor-demonstration exception does NOT fire because the
# reference (Betts & Bokhari) is an EXPERIMENT, not the exact/manufactured
# solution of the model we discretise. Both C1 and C2 are CONTINUUM limbs; a
# Roache triple cures DISCRETISATION error but not the MODEL-FORM error the
# residual against an experiment still contains (§2h.3). The PASS credential of
# this case lives in LIMB B, a SAME-DISCRETE-PROBLEM IDENTITY limb (§2f.3), to
# which a triple is irrelevant because discretisation error cancels on both sides.
TIER_CEILING_C1 = "GATE REACHED"  # CONTINUUM (mid-height vs experiment) -- never PASS
TIER_CEILING_C2 = "GATE REACHED"  # CONTINUUM + doubly indirect (Y/h=0.05 digitisation)
LIMB_B_PASS_CAPABLE = True        # SAME-DISCRETE-PROBLEM IDENTITY -- PASS available

# -------------------------------------------------------- FROZEN PHYSICS CONSTANTS
# Materials FIRST-HAND from import_files/VMFL052_natural.cas.
K_AIR = 0.02605       # W/m-K, thermal conductivity (archive)
W_CAV = 0.0762        # m, cavity width (manual p.235; paper 0.076 m)
H_CAV = 2.18          # m, cavity height
T_COLD = 288.25       # K, cold wall (manual)
T_HOT = 307.85        # K, hot wall (manual)
DT_WALL = T_HOT - T_COLD  # 19.6 K
Y_MID = 1.09          # m, mid-height (y/H = 0.5)
Y_LOW = 0.109         # m, Y/h = 0.05

# ----------------------------------------------------------- REFERENCES + BANDS
# C1 -- Betts & Bokhari Table 1, LOWER-Ra column (first-hand experimental digits).
REF_C1A_NU = 5.85     # average Nusselt number (hot-wall averaged; hot 1.1% above
                      # cold, within the paper's +/-5% experimental accuracy)
REF_C1B_VMAX = 0.139  # m/s, "Max. vert. velocity (Av)" = max of the MEAN vertical
                      # velocity over the mid-height traverse (our reading of "(Av)",
                      # from the paper's nomenclature V,v = mean,rms vertical vel.)
REF_C1C_DTDX = 68.0   # K/m, centre-line horizontal dT/dx at mid-height
BAND_C1A = 0.20       # relative; JUSTIFIED (BAND_DECISION section of prereg) from the
                      # documented k-omega-class bias on natural-convection cavity Nu.
BAND_C1B = 0.20       # relative
BAND_C1C = 0.30       # relative (core gradient is the hardest of the three)

# C2 -- VMFL052_WB.wbpz import_files CSV (Ansys digitisation of the figure).
REF_C2_VUP = 0.147826087    # m/s, exp1 peak up-flow near the hot wall
REF_C2_VDOWN = -0.08173913  # m/s, exp1 peak down-flow near the cold wall
REF_C2_TCORE = 292.246      # K, exp2 (Y/h=0.05) core temperature at mid-width x=W/2
BAND_C2_VUP = 0.20          # relative
BAND_C2_VDOWN = 0.30        # relative (smaller magnitude)
BAND_C2_TCORE = 1.5         # ABSOLUTE (K); the core T is close to the mean, so an
                            # absolute band is the honest form. C2 is GATE REACHED.

# ---------------------------------------------------------------- LIMB A / B
BAND_B = 1.0e-4       # limb B: |q_GPU - q_CPU| / |q_CPU|
GPU_PCTF_MIN = 99.0   # PETSc -log_view GPU %F on the GPU arm
GPU_PCTF_MAX = 100.0  # a percentage cannot exceed this -- REFUSE above it

# -------------------------------------------------------------- ROACHE TRIPLE
R_REFINE = 2.0        # r=2 geometric refinement
FS_GCI = 1.25         # safety factor (three-grid)
P_MIN = 0.05          # observed-order floor (rule 5)

# ---------------------------------------------------------------- MESH FAMILY
# (name, cells) -- MEASURED pre-freeze (blockMesh+checkMesh, MESH_PREFREEZE_RECORD).
LEVELS = (("L1", 6720), ("L2", 26880), ("L3", 107520))
ARMS = ("gpu", "cpu")

# ---------------------------------------------------------------- y+ CONTROL
YPLUS_LAM = 11.06     # yPlusLam for kappa=0.41, E=9.8 (the STEPWISE switch point)
WF_PATCHES = ("coldWall", "hotWall", "bottomWall", "topWall")
BLENDED_WF_FIELDS = {"omega": "omegaWallFunction", "k": "kLowReWallFunction"}
CONTINUOUS_BLENDERS = ("tanh", "exponential")  # STEPWISE/MAX/BINOMIAL are not accepted here

# ------------------------------------------------------------------ PLATEAU
PLATEAU_WINDOW = 1000
PLATEAU_MIN_SAMPLES = 1000
PLATEAU_PTP_TOL = 2.0e-3      # m/s, peak-to-peak of U_y over the window (~1.4% of Vmax)
PLATEAU_ALIVE_MIN = 1.0e-2    # m/s, the channel must have MOVED over its history

# ------------------------------------------------------------ PLANTED CONTROL
PLANT = 1.234e-3      # m/s, planted into a COPY of the velocity reader
PLANT_MIN_FRACTION = 0.1


class Refusal(Exception):
    pass


_EMITTED = []


def emit(msg):
    _EMITTED.append(msg)
    print(msg)


def refuse(clause, msg):
    raise Refusal("REFUSE (VMFLGPU005 %s): %s" % (clause, msg))


# ==========================================================================
# READERS. one_match refuses unless EXACTLY ONE file matches (L-347).
# ==========================================================================
def one_match(pattern, clause, what):
    hits = sorted(glob.glob(pattern))
    if not hits:
        refuse(clause, "READER ABSENT: no file matches %s (%s). An absent reader "
                       "is NEVER read as a zero." % (pattern, what))
    if len(hits) > 1:
        refuse(clause, "%d files match %s for %s: %s. An ambiguous reader could "
                       "silently pick the wrong file, so it refuses."
                       % (len(hits), pattern, what, [os.path.basename(h) for h in hits]))
    return hits[0]


# Column layout of the `sets` raw output, CONFIRMED by the reader smoke
# (SMOKE_READER_PATH_RECORD.txt). OpenFOAM sorts fields ALPHABETICALLY, so the
# file is `<set>_T_U.xy` with columns:  x  T  Ux Uy Uz  (T BEFORE U). The smoke
# caught this: an x,Ux,Uy,Uz,T assumption would have read T as Uy. Fixed here.
COL_X, COL_T, COL_UX, COL_UY, COL_UZ = 0, 1, 2, 3, 4
N_LINE_COLS = 5


def read_line(case_dir, funcname, setname, clause):
    """Read a `sets` raw traverse -> list of (x, Uy, T) sorted by x."""
    base = os.path.join(case_dir, "postProcessing", funcname)
    if not os.path.isdir(base):
        refuse(clause, "no sample directory %s; the traverse has no source." % base)
    path = one_match(os.path.join(base, "*", "%s_*" % setname), clause,
                     "the %s traverse" % setname)
    rows = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) < N_LINE_COLS:
            continue
        try:
            rows.append((float(p[COL_X]), float(p[COL_UY]), float(p[COL_T])))
        except ValueError:
            continue
    if not rows:
        refuse(clause, "the traverse %s parsed to ZERO rows -- a reader that "
                       "returns nothing has failed, not measured a null." % path)
    rows.sort(key=lambda r: r[0])
    return rows


def c1b_vmax(rows, clause="RB"):
    """C1b: max of the MEAN vertical velocity U_y over the mid-height traverse."""
    return max(r[1] for r in rows)


def c1c_dtdx(rows, clause="RC"):
    """C1c: horizontal dT/dx at x = W/2 (central difference on the traverse)."""
    xc = W_CAV / 2.0
    # nearest interior index to xc
    idx = min(range(1, len(rows) - 1), key=lambda i: abs(rows[i][0] - xc), default=None)
    if idx is None:
        refuse(clause, "the mid-height traverse has fewer than 3 points, so a "
                       "central dT/dx at x=W/2 cannot be formed.")
    x0, _, t0 = rows[idx - 1]
    x2, _, t2 = rows[idx + 1]
    if x2 == x0:
        refuse(clause, "degenerate abscissa at x=W/2 (x[i-1]==x[i+1]); dT/dx undefined.")
    return (t2 - t0) / (x2 - x0)


def c2_peaks(rows, clause="R2"):
    """C2: peak up-flow (max U_y) and peak down-flow (min U_y) at Y/h=0.05."""
    return max(r[1] for r in rows), min(r[1] for r in rows)


def c2_tcore(rows, clause="R2T"):
    """C2 core temperature at x=W/2 on the Y/h=0.05 traverse."""
    xc = W_CAV / 2.0
    idx = min(range(len(rows)), key=lambda i: abs(rows[i][0] - xc))
    return rows[idx][2]


def read_nusselt(case_dir, clause="RN"):
    """C1a: hot-wall-averaged Nusselt number from the WALL-NORMAL T GRADIENT.

    The reader smoke proved buoyantBoussinesqSimpleFoam has no compressible thermo,
    so the wallHeatFlux FO refuses. On the resolved integrate-to-wall mesh the wall
    flux is conductive (q = k*dT/dn; turbulent alphat -> 0 at the wall), so
        Nu_hot = |dT/dn|_hot_avg * W / DT_WALL      (K_AIR cancels).
    grad(T) is surface-sampled on hotWall as postProcessing/wallGradT/<t>/
    grad(T)_hotWall.raw with columns x y z grad(T)_x grad(T)_y grad(T)_z; the wall
    normal at x=W is +x, so dT/dn = grad(T)_x (column 3). Returns (Nu, gradmean).
    """
    base = os.path.join(case_dir, "postProcessing", "wallGradT")
    if not os.path.isdir(base):
        refuse(clause, "no wall-temperature-gradient channel at %s; C1a (Nusselt) "
                       "has no source and is NEVER read as a zero." % base)
    path = one_match(os.path.join(base, "*", "grad(T)_hotWall.raw"), clause,
                     "the hot-wall temperature gradient sample")
    gx = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) < 6:
            continue
        try:
            gx.append(float(p[3]))          # grad(T)_x = dT/dn at the x=W wall
        except ValueError:
            continue
    if not gx:
        refuse(clause, "the hot-wall gradient sample %s parsed to ZERO rows -- a "
                       "reader that returns nothing has failed, not measured a "
                       "null." % path)
    gradmean = sum(gx) / len(gx)
    nu = abs(gradmean) * W_CAV / DT_WALL
    return nu, gradmean


# ==========================================================================
# LIMB A -- GPU EXECUTION, PARSED BY COLUMN POSITION AGAINST THE HEADER.
# ==========================================================================
def _logview_rows(txt):
    """Yield (event, tokens) for MatMult/KSPSolve data rows of a -log_view table.
    tokens are the numeric fields AFTER the event name."""
    for line in txt.splitlines():
        m = re.match(r"^\s*(MatMult|KSPSolve)\s+(.*)$", line)
        if not m:
            continue
        toks = m.group(2).split()
        nums = []
        ok = True
        for t in toks:
            try:
                nums.append(float(t))
            except ValueError:
                ok = False
                break
        if ok and nums:
            yield m.group(1), nums


def logview_gpu(case_dir, clause="A"):
    """GPU %F (final column) and CpuToGpu Count (5th-from-last), by POSITION.

    The -log_view event-table columns after the event name end, in order:
    ... Total-Mflop/s  GPU-Mflop/s  CpuToGpu-Count  CpuToGpu-Size  GpuToCpu-Count
    GpuToCpu-Size  GPU%F. So GPU %F = tokens[-1] and CpuToGpu Count = tokens[-5].
    This is the repair of VMFLGPU007's defect, where max() of the last four
    tokens returned CpuToGpu Size in Mbytes (210) and cleared a 99.0 floor.
    """
    log = one_match(os.path.join(case_dir, "log.*Foam"), clause + "0", "the solver log")
    txt = open(log, errors="replace").read()
    return parse_logview_text(txt, clause, src=log)


def parse_logview_text(txt, clause, src="<text>"):
    if "GPU %F" not in txt and "Summary of Stages" not in txt and "-log_view" not in txt:
        refuse(clause + "1", "no PETSc -log_view table in %s. An ABSENT table is "
                             "NEVER read as a zero: without it there is no evidence "
                             "about where the linear algebra ran." % src)
    # Validate the header order: CpuToGpu precedes GpuToCpu and the table ends %F.
    header = None
    for line in txt.splitlines():
        if "CpuToGpu" in line and "GpuToCpu" in line and line.rstrip().endswith("%F"):
            header = line
            break
    if header is None:
        # tolerate the two-line PETSc header (labels split across lines): require
        # the sub-header row that ends in %F and names Count/Size twice.
        for line in txt.splitlines():
            if line.rstrip().endswith("%F") and line.count("Count") >= 2 and line.count("Size") >= 2:
                header = line
                break
    if header is None:
        refuse(clause + "5", "the -log_view table in %s has no header row ending "
                             "in '%%F' with CpuToGpu/GpuToCpu columns, so column "
                             "position cannot be validated and this reader will "
                             "NOT guess an index." % src)
    pctf_min, pctf_max, h2d = None, None, None
    for _event, nums in _logview_rows(txt):
        if len(nums) < 6:
            refuse(clause + "6", "a MatMult/KSPSolve row in %s has only %d numeric "
                                 "columns, fewer than the 6 the GPU-%%F/CpuToGpu "
                                 "positions require; refusing rather than indexing "
                                 "past the row." % (src, len(nums)))
        gpupctf = nums[-1]
        cpu2gpu = nums[-5]
        if gpupctf > GPU_PCTF_MAX:
            refuse(clause + "2", "a -log_view row in %s reports GPU %%F = %.6g, "
                                 "ABOVE 100. A percentage cannot exceed 100, so the "
                                 "final column is not GPU %%F (this is exactly the "
                                 "VMFLGPU007 defect, where a max() reader returned "
                                 "the CpuToGpu SIZE IN MBYTES). Refusing." % (src, gpupctf))
        pctf_min = gpupctf if pctf_min is None else min(pctf_min, gpupctf)
        pctf_max = gpupctf if pctf_max is None else max(pctf_max, gpupctf)
        h2d = cpu2gpu if h2d is None else h2d + cpu2gpu
    if pctf_min is None:
        refuse(clause + "1", "the -log_view table in %s carries no MatMult/KSPSolve "
                             "row, so no GPU flop fraction can be read." % src)
    # BOTH aggregations are returned; limb_A uses them ASYMMETRICALLY (see there):
    # the GPU-arm floor is tested on the MIN, the forced-CPU control leak on the MAX.
    return dict(gpu_pctf_min=pctf_min, gpu_pctf_max=pctf_max, h2d=int(h2d))


def limb_A(gpu_dir, cpu_dir, level, clause="A"):
    """ASYMMETRIC AGGREGATION, and the asymmetry is the whole point (VMFLGPU007-R2):
    the forced-CPU control leak is tested on the MAX over events (a leak on ANY row
    refuses -- the control must be zero EVERYWHERE), while the GPU-arm floor is
    tested on the MIN over events (EVERY qualifying event must be on the device --
    the GPU arm must be high EVERYWHERE). Testing the floor on the MAX would let a
    GPU MatMult (%F=100) mask a p_rgh KSPSolve that silently fell back to the host
    (%F=0), certifying a GPU claim that is FALSE for the exact operation this case
    exists to verify."""
    g = logview_gpu(gpu_dir, clause)
    c = logview_gpu(cpu_dir, clause)
    # CONTROL LEAK -> MAX (a leak on any event refuses).
    if c["gpu_pctf_max"] > 0.0 or c["h2d"] > 0:
        refuse(clause + "3", "%s: the FORCED-CPU CONTROL (mat_type aij, vec_type "
                             "standard) REPORTED GPU WORK on some event (max GPU %%F "
                             "= %.4g, CpuToGpu Count = %d). The tells cannot "
                             "discriminate GPU from CPU on this build, so this row "
                             "certifies NOTHING." % (level, c["gpu_pctf_max"], c["h2d"]))
    # GPU-ARM FLOOR -> MIN (every event must be on the device).
    if g["gpu_pctf_min"] < GPU_PCTF_MIN:
        refuse(clause + "4", "%s: the LOWEST-GPU-fraction event on the GPU arm reports "
                             "GPU %%F = %.4g, below the registered floor %.4g. If "
                             "MatMult ran on the GPU while the p_rgh KSPSolve fell "
                             "back to the host, the MAX over events would have cleared "
                             "this floor while the Poisson solve -- the object under "
                             "verification -- ran on the CPU. The floor is tested on "
                             "the MIN for exactly that reason."
                             % (level, g["gpu_pctf_min"], GPU_PCTF_MIN))
    if g["h2d"] <= 0:
        refuse(clause + "5", "%s: the GPU arm reports ZERO host-to-device (CpuToGpu) "
                             "transfers. A solve that never staged a buffer to the "
                             "device did not use it." % level)
    return dict(gpu=g, cpu=c)


# ==========================================================================
# BLENDER CONTROL -- the triple is clean only if the wall functions are
# CONTINUOUS (tanh/exponential). REFUSES on STEPWISE or unset (rule-5 validity).
# ==========================================================================
def blender_control(case_dir, clause="W"):
    realised = {}
    for fld, wftype in BLENDED_WF_FIELDS.items():
        f0 = None
        for cand in (os.path.join(case_dir, "0", fld), os.path.join(case_dir, "0", fld + ".gz")):
            if os.path.isfile(cand) and cand.endswith(fld):
                f0 = cand
                break
        if f0 is None:
            refuse(clause + "1", "no 0/%s to check the wall-function blender on; the "
                                 "continuity of the wall model across the triple "
                                 "cannot be established and is NEVER assumed." % fld)
        txt = open(f0).read()
        bf = re.search(r"boundaryField\s*\{(.*)\}", txt, re.S)
        if not bf:
            refuse(clause + "2", "0/%s has no boundaryField block." % fld)
        body = bf.group(1)
        for patch in WF_PATCHES:
            pm = re.search(r"%s\s*\{(.*?)\}" % re.escape(patch), body, re.S)
            if not pm:
                refuse(clause + "3", "0/%s has no entry for wall patch %r; the "
                                     "blender there cannot be verified." % (fld, patch))
            pbody = pm.group(1)
            if wftype not in pbody:
                refuse(clause + "4", "0/%s patch %r is not %s; this comparator "
                                     "certifies the blender only on the frozen wall "
                                     "function." % (fld, patch, wftype))
            bm = re.search(r"blender\s+(\w+)\s*;", pbody)
            blender = bm.group(1) if bm else "STEPWISE(default-unset)"
            if (bm is None) or (blender not in CONTINUOUS_BLENDERS):
                refuse(clause + "5", "0/%s patch %r has blender %r, which is NOT one "
                                     "of the continuous blenders %s. A STEPWISE or "
                                     "unset blender switches the wall model "
                                     "DISCONTINUOUSLY as the triple refines and "
                                     "y+ crosses yPlusLam, tangling a model change "
                                     "into the observed order -- 'a number wearing "
                                     "the shape of a rigour it does not have'. "
                                     "Refusing." % (fld, patch, blender, list(CONTINUOUS_BLENDERS)))
            realised["%s/%s" % (fld, patch)] = blender
    return realised


# ==========================================================================
# y+ CONTROL -- report max y+ per level; refuse only if a level exceeds
# yPlusLam WHILE a wall function is STEPWISE (the exact triple-corrupting
# condition). With the tanh blender enforced above this is belt-and-braces.
# ==========================================================================
def yplus_max(case_dir, clause="Y"):
    base = os.path.join(case_dir, "postProcessing", "yPlusFO")
    if not os.path.isdir(base):
        refuse(clause + "1", "no y+ record at %s. Integrate-to-wall validity (the "
                             "faithful reproduction of Ansys's low-Re k-omega) is a "
                             "registered condition and cannot be checked without it." % base)
    path = one_match(os.path.join(base, "*", "*.dat"), clause + "1", "the y+ record")
    ymax = None
    per_patch = {}
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) < 5:
            continue
        try:
            mx, av = float(p[3]), float(p[4])
        except ValueError:
            continue
        per_patch[p[1]] = (float(p[2]), mx, av)
        ymax = mx if ymax is None else max(ymax, mx)
    if ymax is None:
        refuse(clause + "2", "the y+ record %s parsed to zero patch rows." % path)
    return dict(max=ymax, per_patch=per_patch)


# ==========================================================================
# STRICT COMPLETION (rule 4). ExecutionTime count is INFRASTRUCTURE (L-342):
# petsc4Foam prints init timing lines inside Time=1, so it is a property of what
# the libraries print, not of the physics.
# ==========================================================================
FIELDS_AT_ENDTIME = ("T", "U", "p_rgh", "k", "omega", "nut", "alphat")


def _field_present(d, f):
    return os.path.isfile(os.path.join(d, f)) or os.path.isfile(os.path.join(d, f + ".gz"))


def completion(case_dir, endtime, rc_text, clause="C"):
    log = one_match(os.path.join(case_dir, "log.*Foam"), clause + "0", "the solver log")
    txt = open(log, errors="replace").read()
    rc = None
    if rc_text is not None:
        m = re.search(r"^\s*rc\s*=\s*(-?\d+)\s*$", rc_text, re.M)
        if m:
            rc = int(m.group(1))
    if rc is not None and rc != 0:
        refuse(clause + "1", "solver rc = %d in %s" % (rc, case_dir))
    if re.search(r"^End\s*$", txt, re.M) is None:
        refuse(clause + "2", "no 'End' line in %s -- the solver did not finish its time loop" % log)
    times = re.findall(r"^Time = (\S+)\s*$", txt, re.M)
    if not times:
        refuse(clause + "3", "no 'Time =' lines in %s" % log)
    try:
        last = float(times[-1])
    except ValueError:
        refuse(clause + "3", "last 'Time =' value %r in %s is not a number" % (times[-1], log))
    if abs(last - float(endtime)) > 1e-9:
        refuse(clause + "3", "last time %s != registered endTime %s in %s" % (times[-1], endtime, log))
    if len(times) != int(float(endtime)):
        refuse(clause + "4", "%d 'Time =' lines against a registered endTime of %s in "
                             "%s. The 'Time =' count IS the physics-critical clause "
                             "(L-342); the ExecutionTime count is not." % (len(times), endtime, log))
    td = os.path.join(case_dir, str(endtime))
    if not os.path.isdir(td):
        refuse(clause + "5", "no time directory %s" % td)
    missing = [f for f in FIELDS_AT_ENDTIME if not _field_present(td, f)]
    if missing:
        refuse(clause + "5", "field(s) %s absent from %s -- neither X nor X.gz" % (", ".join(missing), td))
    zero_T = os.path.join(case_dir, "0", "T")
    if not os.path.isfile(zero_T):
        refuse(clause + "6", "the age-guard reference %s does not exist" % zero_T)
    t0 = os.path.getmtime(zero_T)
    stale = []
    for f in FIELDS_AT_ENDTIME:
        for cand in (os.path.join(td, f), os.path.join(td, f + ".gz")):
            if os.path.isfile(cand) and os.path.getmtime(cand) <= t0:
                stale.append(f)
                break
    if stale:
        refuse(clause + "6", "AGE GUARD: field(s) %s at %s are NOT newer than the "
                             "case's own 0/T; they cannot be shown to be this run's "
                             "output." % (", ".join(stale), td))
    exec_lines = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    infra = None
    if exec_lines != len(times):
        infra = ("INFRA: %d ExecutionTime lines against %d 'Time =' lines "
                 "(petsc4Foam prints init timing before the first solve). "
                 "INFRASTRUCTURE under L-342 -- reported, never refuses." % (exec_lines, len(times)))
    return dict(rc=("NOT MEASURED" if rc is None else rc), times=len(times), last=last, infra=infra, log=log)


# ==========================================================================
# PLATEAU -- on the gate quantity's OWN history (probeU U_y), with a LIVENESS
# floor. A dead channel and a converged one look identical to a peak-to-peak test.
# ==========================================================================
def _probe_uy_series(case_dir, clause):
    base = os.path.join(case_dir, "postProcessing", "probeU")
    if not os.path.isdir(base):
        refuse(clause + "1", "no plateau channel at %s" % base)
    path = one_match(os.path.join(base, "*", "U"), clause + "1", "the probeU U history")
    vals = []
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # probes U: "time (Ux Uy Uz)" possibly with parens
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
        if len(nums) >= 3:
            try:
                vals.append(float(nums[2]))   # Uy = 2nd component after time
            except ValueError:
                pass
    return vals, path


def plateau(case_dir, clause="I"):
    vals, path = _probe_uy_series(case_dir, clause)
    if len(vals) < PLATEAU_MIN_SAMPLES:
        refuse(clause + "2", "the plateau channel %s has %d samples, fewer than the "
                             "registered minimum %d, so no window statement can be "
                             "made." % (path, len(vals), PLATEAU_MIN_SAMPLES))
    win = vals[-PLATEAU_WINDOW:]
    ptp = max(win) - min(win)
    full = max(vals) - min(vals)
    if ptp > PLATEAU_PTP_TOL:
        refuse(clause + "3", "the plateau window peak-to-peak is %.6g m/s, above the "
                             "registered %.6g: the mid-height wall-jet velocity has "
                             "NOT settled. (Turbulent natural convection RANS is slow "
                             "and may not reach this within an affordable endTime; if "
                             "so the honest verdict is NOT A RESULT, not a loosened "
                             "tolerance.)" % (ptp, PLATEAU_PTP_TOL))
    if full < PLATEAU_ALIVE_MIN:
        refuse(clause + "4", "LIVENESS: the plateau window is flat (ptp %.6g) but the "
                             "channel moved only %.6g m/s over its ENTIRE history, "
                             "below the registered floor %.6g. A dead channel and a "
                             "converged one look identical to a peak-to-peak test."
                             % (ptp, full, PLATEAU_ALIVE_MIN))
    return dict(samples=len(vals), window_ptp=ptp, history_range=full)


# ==========================================================================
# PLANTED-ZERO CONTROL (rule 3) -- SUCCESSOR S2, BIRTH-REQUIREMENT FORM.
# Sanaa 2026-08-28: "a planted control must travel the real production path --
# written by the real producer's code, read through the real reader -- and prove
# the instrument sees a non-zero the same way reality would deliver one." The
# parent control mutated the reader's ALREADY-PARSED rows in memory and re-ran
# only the c1b_vmax reducer, so it exercised an argmax reducer, never the FILE
# reader. S2 plants a SIZED offset into the U_y column of EVERY row of a COPY of
# the real midHeight sample file, reads it BACK FROM DISK THROUGH the parent's
# own unmodified read_line(), and then runs the SAME planted file through the
# FULL gate functional c1b_vmax(). Sized to the channel (a fraction of the
# in-window max |U_y|, never a fixed absolute an averaging reader could dilute --
# L-340), and applied to EVERY row so it can never land outside the reader's
# support (L-347). Refuses via refuse() (never assert; python3 -O safe); the
# --selftest suppress arm proves it can FAIL, not merely pass.
# ==========================================================================
def planted_zero_control(gpu_dir, clause="P1", _selftest_suppress_plant=False):
    plant_k = 0.05          # plant size as a fraction of the in-window max |U_y|
    rb_tol = 1.0e-9         # read-back tolerance, relative to the plant scale
    base_dir = os.path.join(gpu_dir, "postProcessing", "midLine")
    if not os.path.isdir(base_dir):
        refuse(clause, "no sample directory %s; the planted-zero control has no "
                       "real production artifact to travel through." % base_dir)
    # LOCATE the real file the gate reader parses, via the comparator's OWN
    # one_match, so the successor reads EXACTLY what the parent read.
    src = one_match(os.path.join(base_dir, "*", "midHeight_*"), clause,
                    "the midHeight traverse (planted-zero source)")
    base_rows = read_line(gpu_dir, "midLine", "midHeight", clause)
    base_vmax = c1b_vmax(base_rows)
    signal = max(abs(r[1]) for r in base_rows)
    if signal <= 0.0:
        refuse(clause, "the midHeight U_y channel is identically zero, so there "
                       "is nothing for a plant to be sized to.")
    plant = plant_k * signal

    def _plant_uy_column(path, delta):
        out = []
        for line in open(path):
            s = line.strip()
            if not s or s.startswith("#"):
                out.append(line)
                continue
            p = s.split()
            if len(p) < N_LINE_COLS:
                out.append(line)
                continue
            try:
                uy = float(p[COL_UY])
            except ValueError:
                out.append(line)
                continue
            p[COL_UY] = repr(uy + delta)
            out.append(" ".join(p) + "\n")
        fh = open(path, "w")
        try:
            fh.write("".join(out))
        finally:
            fh.close()

    tmp = tempfile.mkdtemp(prefix="vmflgpu005_s2_plant_")
    try:
        rel = os.path.relpath(src, gpu_dir)
        dst = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(dst))
        shutil.copy(src, dst)
        # NEGATIVE ARM: an unplanted copy must read back identical to baseline
        # THROUGH read_line() -- proving the reader is deterministic on the bytes.
        neg_rows = read_line(tmp, "midLine", "midHeight", clause)
        if len(neg_rows) != len(base_rows) or any(
                abs(neg_rows[i][1] - base_rows[i][1]) > 0.0
                for i in range(len(base_rows))):
            refuse(clause, "the NEGATIVE arm moved: an unplanted copy of %s did "
                           "not read back identical to baseline through "
                           "read_line(). The reader is not deterministic and no "
                           "zero it reports is evidence." % src)
        # PLANT into EVERY U_y on the real bytes (unless the selftest suppresses
        # it to prove the control can FAIL). The EXPECTATION is always `plant`.
        if not _selftest_suppress_plant:
            _plant_uy_column(dst, plant)
        seen_rows = read_line(tmp, "midLine", "midHeight", clause)
        if len(seen_rows) != len(base_rows):
            refuse(clause, "planted-zero: the row count changed across the plant.")
        worst = max(abs((seen_rows[i][1] - base_rows[i][1]) - plant)
                    for i in range(len(base_rows)))
        scale = max(abs(plant), 1.0)
        if not (worst <= rb_tol * scale):
            refuse(clause, "PLANT-BLIND (P1a, reader sensitivity): a plant of "
                           "%.9g m/s was written into the U_y column of EVERY row "
                           "of %s, but read back through read_line() the worst "
                           "per-row discrepancy is %.9g. A reader not shown able "
                           "to see a known non-zero through the real file cannot "
                           "certify a zero (rule 3)." % (plant, src, worst))
        # P1b: the SAME planted file through the FULL gate functional c1b_vmax.
        seen_vmax = c1b_vmax(seen_rows)
        delta = seen_vmax - base_vmax
        expect = plant
        if delta <= PLANT_MIN_FRACTION * expect:
            refuse(clause, "PLANT-BLIND (P1b, gate-functional sensitivity): a "
                           "uniform plant of %.9g m/s into U_y should have moved "
                           "the gate quantity max U_y UP by ~%.9g but c1b_vmax "
                           "moved by %.9g. A plant the raw reader sees but the "
                           "gate does not is the register-row-#31 failure "
                           "(rule 3)." % (plant, expect, delta))
        return dict(row=len(base_rows), plant=plant, expected=expect,
                    observed=abs(delta), worst_readback=worst,
                    n_rows=len(base_rows), file=src)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ==========================================================================
# ROACHE TRIPLE (rule 5). classify -> one of CONVERGING / DIVERGENT /
# OSCILLATORY / STAGNANT / EXACT / BELOW_P_MIN. GCI only when CONVERGING.
# ==========================================================================
def classify_triple(f_coarse, f_med, f_fine, clause="T"):
    e21 = f_med - f_coarse     # coarse->med
    e32 = f_fine - f_med       # med->fine
    tiny = 1e-30
    if abs(e21) < tiny and abs(e32) < tiny:
        return dict(kind="EXACT", p=None, gci=None, e21=e21, e32=e32,
                    note="all three levels equal -- no discretisation error to measure")
    if abs(e21) < tiny or abs(e32) < tiny:
        return dict(kind="STAGNANT", p=None, gci=None, e21=e21, e32=e32,
                    note="one refinement pair is identical -- observed order undefined")
    R = e32 / e21
    if R < 0.0:
        return dict(kind="OSCILLATORY", p=None, gci=None, e21=e21, e32=e32,
                    note="e21 and e32 have opposite sign (R=%.4g<0) -- not monotone, no GCI" % R)
    if R >= 1.0:
        return dict(kind="DIVERGENT", p=None, gci=None, e21=e21, e32=e32,
                    note="|e32|>=|e21| (R=%.4g>=1) -- refinement is not reducing the error" % R)
    # 0 < R < 1: monotone converging. Observed order and GCI.
    p = math.log(abs(e21 / e32)) / math.log(R_REFINE)
    if p < P_MIN:
        return dict(kind="BELOW_P_MIN", p=p, gci=None, e21=e21, e32=e32,
                    note="observed order p=%.4g below the floor P_MIN=%.4g" % (p, P_MIN))
    gci = FS_GCI * abs(e32 / f_fine) / (R_REFINE ** p - 1.0) if abs(f_fine) > tiny else None
    return dict(kind="CONVERGING", p=p, gci=gci, e21=e21, e32=e32,
                note="monotone converging (R=%.4g), p=%.4g, GCI_fine=%s"
                     % (R, p, ("%.4g%%" % (100 * gci) if gci is not None else "n/a")))


def channel_verdict(name, triple, value_fine, ref, band, absolute, ceiling, clause):
    """Rule-5 order: not CONVERGING -> NOT A RESULT; else PASS/GATE REACHED (up to
    ceiling) inside band else GATE FAIL."""
    if triple["kind"] != "CONVERGING":
        return dict(name=name, verdict="NOT A RESULT", value=value_fine, ref=ref,
                    triple=triple, dev=None, held=None,
                    why="triple is %s (%s) -- rule 5: NOT A RESULT whatever the value"
                        % (triple["kind"], triple["note"]))
    dev = abs(value_fine - ref) if absolute else abs(value_fine - ref) / abs(ref)
    held = dev <= band
    if held:
        v = ceiling            # PASS or GATE REACHED, the channel's ceiling
    else:
        v = "GATE FAIL"
    return dict(name=name, verdict=v, value=value_fine, ref=ref, triple=triple,
                dev=dev, held=held,
                why="CONVERGING (p=%.4g, GCI=%s); %s %.6g vs ref %.6g, dev %.4g %s band %.4g"
                    % (triple["p"], ("%.3g%%" % (100 * triple["gci"]) if triple["gci"] else "n/a"),
                       "inside" if held else "outside", value_fine, ref, dev,
                       "<=" if held else ">", band))


# ==========================================================================
def vocabulary_selfcheck(verdict, clause="V"):
    if verdict not in VOCAB:
        refuse(clause + "1", "verdict %r is not one of the fixed vocabulary %s (rule 1)"
                             % (verdict, list(VOCAB)))
    return True


def ceiling_selfcheck(clause="Z"):
    if TIER_CEILING_C2 != "GATE REACHED":
        refuse(clause + "1", "TIER_CEILING_C2 is %r, not 'GATE REACHED'." % TIER_CEILING_C2)
    if TIER_CEILING_C1 != "GATE REACHED":
        refuse(clause + "2", "TIER_CEILING_C1 is %r, not 'GATE REACHED'. C1 is a "
                             "CONTINUUM limb (mid-height vs the Betts & Bokhari "
                             "EXPERIMENT); VERIFICATION_CHARTER §2f.3 caps it at "
                             "GATE REACHED and §2h.4 cond.1 does not fire for an "
                             "experimental reference, so PASS is unavailable to it. "
                             "PASS lives in limb B (same-discrete-problem identity)." % TIER_CEILING_C1)
    return True


def worst_channel_verdict(channels):
    """Combine per-channel verdicts: NOT A RESULT dominates, then GATE FAIL, then
    the ceiling (GATE REACHED before PASS)."""
    order = {"NOT A RESULT": 0, "GATE FAIL": 1, "GATE REACHED": 2, "PASS": 3}
    return min((c["verdict"] for c in channels), key=lambda v: order[v])


# ==========================================================================
# THE GRADE
# ==========================================================================
def read_rc(run_root, level, arm):
    p = os.path.join(run_root, "RUN_RC.%s.%s" % (level, arm))
    return open(p).read() if os.path.isfile(p) else None


def read_endtime(run_root, level, arm):
    p = os.path.join(run_root, "RUN_RC.%s.%s" % (level, arm))
    if os.path.isfile(p):
        m = re.search(r"^\s*endtime\s*=\s*(\S+)\s*$", open(p).read(), re.M)
        if m:
            return m.group(1)
    refuse("E1", "cannot determine the registered endTime for %s/%s: no 'endtime =' "
                 "line in %s. The completion rule's 'last time == endTime' clause has "
                 "no referent, so this refuses rather than letting the run define its "
                 "own finish line." % (level, arm, p))


def grade(run_root):
    emit("%s  run_root=%s" % (VERSION, run_root))
    emit("MODEL (frozen, supervisor-verified): standard k-omega low-Re, integrate-"
         "to-wall (import_files/VMFL052_natural.cas: kw-std-on? #t, rng-ke-on? #f, "
         "kw-low-re-mod? #t). Reproduced as OpenFOAM kOmega + tanh wall functions on "
         "an r=2 BOUNDARY-LAYER-RESOLVING triple. Fluent's low-Re damping terms are "
         "NOT claimed (declared modelling difference).")
    ceiling_selfcheck()

    per = {}
    for level, cells in LEVELS:
        gd = os.path.join(run_root, "gpu", level)
        cd = os.path.join(run_root, "cpu", level)
        for d in (gd, cd):
            if not os.path.isdir(d):
                refuse("D1", "arm directory %s does not exist" % d)
        et_g = read_endtime(run_root, level, "gpu")
        et_c = read_endtime(run_root, level, "cpu")
        if et_g != et_c:
            refuse("D2", "%s: the two arms registered different endTimes (%s vs %s). "
                         "Limb B is a statement about the linear algebra ONLY IF both "
                         "arms took the same number of outer iterations." % (level, et_g, et_c))

        comp_g = completion(gd, et_g, read_rc(run_root, level, "gpu"), "CG")
        comp_c = completion(cd, et_c, read_rc(run_root, level, "cpu"), "CC")
        plat_g = plateau(gd, "IG")
        plat_c = plateau(cd, "IC")
        la = limb_A(gd, cd, level)
        bl = blender_control(gd, "W")
        yp = yplus_max(gd, "Y")
        # y+ / STEPWISE cross-check (belt-and-braces; tanh already enforced above).
        if yp["max"] > YPLUS_LAM and any(b not in CONTINUOUS_BLENDERS for b in bl.values()):
            refuse("Y3", "%s: max y+ = %.4g exceeds yPlusLam %.4g WHILE a wall "
                         "function is not continuous -- the exact condition under "
                         "which the STEPWISE switch corrupts the triple." % (level, yp["max"], YPLUS_LAM))

        mid_g = read_line(gd, "midLine", "midHeight", "RGmid")
        mid_c = read_line(cd, "midLine", "midHeight", "RCmid")
        low_g = read_line(gd, "lowLine", "lowHeight", "RGlow")
        nu_g, q_g = read_nusselt(gd, "RNg")
        nu_c, q_c = read_nusselt(cd, "RNc")

        control = planted_zero_control(gd, "P1")

        per[level] = dict(
            cells=cells,
            c1a_gpu=nu_g, c1a_cpu=nu_c,
            c1b_gpu=c1b_vmax(mid_g), c1b_cpu=c1b_vmax(mid_c),
            c1c_gpu=c1c_dtdx(mid_g), c1c_cpu=c1c_dtdx(mid_c),
            c2_vup=c2_peaks(low_g)[0], c2_vdown=c2_peaks(low_g)[1], c2_tcore=c2_tcore(low_g),
            comp_g=comp_g, comp_c=comp_c, plat_g=plat_g, plat_c=plat_c,
            limbA=la, blender=bl, yplus=yp, control=control)
        for cinfra in (comp_g["infra"], comp_c["infra"]):
            if cinfra:
                emit("  %s %s" % (level, cinfra))
        emit("  %s cells=%d | Nu gpu=%.4f cpu=%.4f | Vmax gpu=%.5f cpu=%.5f | dTdx "
             "gpu=%.3f cpu=%.3f | y+max=%.3g | plant %s"
             % (level, cells, nu_g, nu_c, per[level]["c1b_gpu"], per[level]["c1b_cpu"],
                per[level]["c1c_gpu"], per[level]["c1c_cpu"], yp["max"],
                "fired" if control["observed"] > 0 else "DID NOT FIRE"))

    emit("BLENDER CONTROL: %s" % per["L3"]["blender"])

    # ---- LIMB B: GPU==CPU at every level (PASS-capable) --------------------
    b_worst, b_all = 0.0, True
    for level, _ in LEVELS:
        for tag, g, c in (("Nu", per[level]["c1a_gpu"], per[level]["c1a_cpu"]),
                          ("Vmax", per[level]["c1b_gpu"], per[level]["c1b_cpu"]),
                          ("dTdx", per[level]["c1c_gpu"], per[level]["c1c_cpu"])):
            if abs(c) < 1e-30:
                refuse("B0", "%s/%s: forced-CPU value is %.6g, relative comparison "
                             "undefined" % (level, tag, c))
            rel = abs(g - c) / abs(c)
            b_worst = max(b_worst, rel)
            if rel > BAND_B:
                b_all = False
    emit("LIMB A: GPU execution established at every level; forced-CPU control "
         "reported no GPU work at any level.")
    emit("LIMB B (%s, PASS-CAPABLE -- identical mesh and scheme): worst |dq|/|q| = "
         "%.3e against band %.1e" % ("HOLDS" if b_all else "MISSES", b_worst, BAND_B))

    # ---- LIMB C1: three channels, each a Roache triple on the GPU arm ------
    c1a = channel_verdict("C1a Nu", classify_triple(per["L1"]["c1a_gpu"], per["L2"]["c1a_gpu"], per["L3"]["c1a_gpu"]),
                          per["L3"]["c1a_gpu"], REF_C1A_NU, BAND_C1A, False, TIER_CEILING_C1, "C1a")
    c1b = channel_verdict("C1b Vmax", classify_triple(per["L1"]["c1b_gpu"], per["L2"]["c1b_gpu"], per["L3"]["c1b_gpu"]),
                          per["L3"]["c1b_gpu"], REF_C1B_VMAX, BAND_C1B, False, TIER_CEILING_C1, "C1b")
    c1c = channel_verdict("C1c dTdx", classify_triple(per["L1"]["c1c_gpu"], per["L2"]["c1c_gpu"], per["L3"]["c1c_gpu"]),
                          per["L3"]["c1c_gpu"], REF_C1C_DTDX, BAND_C1C, False, TIER_CEILING_C1, "C1c")
    for ch in (c1a, c1b, c1c):
        emit("LIMB C1 %s (ceiling %s): %s" % (ch["name"], TIER_CEILING_C1, ch["why"]))
    c1_verdict = worst_channel_verdict([c1a, c1b, c1c])

    # ---- LIMB C2: Y/h=0.05, GATE REACHED ceiling ---------------------------
    c2u = channel_verdict("C2 Vup", classify_triple(per["L1"]["c2_vup"], per["L2"]["c2_vup"], per["L3"]["c2_vup"]),
                          per["L3"]["c2_vup"], REF_C2_VUP, BAND_C2_VUP, False, TIER_CEILING_C2, "C2u")
    c2d = channel_verdict("C2 Vdown", classify_triple(per["L1"]["c2_vdown"], per["L2"]["c2_vdown"], per["L3"]["c2_vdown"]),
                          per["L3"]["c2_vdown"], REF_C2_VDOWN, BAND_C2_VDOWN, False, TIER_CEILING_C2, "C2d")
    c2t = channel_verdict("C2 Tcore", classify_triple(per["L1"]["c2_tcore"], per["L2"]["c2_tcore"], per["L3"]["c2_tcore"]),
                          per["L3"]["c2_tcore"], REF_C2_TCORE, BAND_C2_TCORE, True, TIER_CEILING_C2, "C2t")
    for ch in (c2u, c2d, c2t):
        emit("LIMB C2 %s (ceiling %s): %s" % (ch["name"], TIER_CEILING_C2, ch["why"]))
    c2_verdict = worst_channel_verdict([c2u, c2d, c2t])

    # ---- paper-vs-CSV DISAGREEMENT, reported never reconciled --------------
    emit("PAPER-vs-CSV (reported, NEVER averaged): C1b mid-height Vmax %.5f (paper "
         "Table 1 = %.5f) and C2 Y/h=0.05 peak up %.5f (archive CSV = %.5f) are at "
         "DIFFERENT heights and different provenance; any disagreement stands as "
         "recorded." % (per["L3"]["c1b_gpu"], REF_C1B_VMAX, per["L3"]["c2_vup"], REF_C2_VUP))

    # ---- PER-LIMB verdicts, then WHOLE-ROW = the weakest link --------------
    # Each limb keeps its own verdict (the register row states all three). B and
    # C1 can individually earn PASS; C2 caps at GATE REACHED; the ROW's single
    # verdict is the min, because the row is only as strong as its weakest limb.
    order = {"NOT A RESULT": 0, "GATE FAIL": 1, "GATE REACHED": 2, "PASS": 3}
    b_verdict = "PASS" if b_all else "GATE FAIL"   # SAME-DISCRETE-PROBLEM IDENTITY: PASS available
    emit("PER-LIMB: B(GPU==CPU, SAME-DISCRETE-PROBLEM IDENTITY, PASS-capable) = %s | "
         "C1(mid-height vs Betts&Bokhari experiment, CONTINUUM ceiling GATE REACHED) "
         "= %s | C2(Y/h=0.05 digitisation, CONTINUUM ceiling GATE REACHED) = %s"
         % (b_verdict, c1_verdict, c2_verdict))
    verdict = min([b_verdict, c1_verdict, c2_verdict], key=lambda v: order[v])
    why = ("weakest of the three limbs. C1 and C2 are CONTINUUM limbs capped at "
           "GATE REACHED (§2f.3): a Roache triple cures discretisation error but not "
           "the model-form error the residual against an EXPERIMENT still carries. "
           "The PASS credential of this case lives in limb B alone (same-discrete-"
           "problem identity, to which a triple is irrelevant).")

    vocabulary_selfcheck(verdict)
    emit("VERDICT: %s -- %s" % (verdict, why))
    emit("NOT CLAIMED: nothing about Ansys (this box has no Fluent); nothing about GPU "
         "performance (a GPU arm slower than the CPU arm passes every limb); no PASS on "
         "C2; no byte-identity with Fluent's low-Re k-omega.")
    return verdict


# ==========================================================================
# FIXTURES + SELFTEST. -O safe (zero bare asserts). Limb A driven on the REAL
# frozen bytes of VMFLGPU007's own -log_view tables.
# ==========================================================================
def _here():
    return os.path.dirname(os.path.abspath(__file__))


def _real_logview(arm):
    p = os.path.join(_here(), "reference", "REAL_LOGVIEW_%s_vmflgpu007_L1.txt" % arm.upper())
    return open(p).read() if os.path.isfile(p) else None


def selftest():
    import tempfile
    results = []

    def check(good, tag, detail):
        results.append((bool(good), tag, detail))

    # ---- LIMB A ON REAL FROZEN BYTES (the supervisor's mandate) ------------
    gpu_txt = _real_logview("gpu")
    cpu_txt = _real_logview("cpu")
    if gpu_txt is None or cpu_txt is None:
        check(False, "real_logview_present",
              "reference/REAL_LOGVIEW_{GPU,CPU}_vmflgpu007_L1.txt not found -- the "
              "limb-A reader cannot be driven on real bytes")
    else:
        okg = False
        try:
            g = parse_logview_text(gpu_txt, "A", "REAL_GPU")
            okg = (g["gpu_pctf_min"] == 100.0 and g["h2d"] > 0)
        except Refusal as r:
            okg = "FIXTURE-REFUSED: %s" % r
        check(okg is True, "limbA_real_gpu_reads_100_and_transfers",
              "on VMFLGPU007's REAL gpu table: GPU %%F=%s, CpuToGpu=%s (want 100 and >0)"
              % (g["gpu_pctf_min"], g["h2d"]) if okg is True else str(okg))
        okc = False
        try:
            c = parse_logview_text(cpu_txt, "A", "REAL_CPU")
            okc = (c["gpu_pctf_max"] == 0.0 and c["h2d"] == 0)
        except Refusal as r:
            okc = "FIXTURE-REFUSED: %s" % r
        check(okc is True, "limbA_real_cpu_reads_zero",
              "on VMFLGPU007's REAL cpu table: GPU %%F=%s, CpuToGpu=%s (want 0 and 0)"
              % (c["gpu_pctf_max"], c["h2d"]) if okc is True else str(okc))
        # THE DEFECT: max() of the last four tokens of a real MatMult row returns
        # the CpuToGpu SIZE (210), not GPU %F (100). Prove positional parse differs.
        defect_val, correct_val = None, None
        for _e, nums in _logview_rows(gpu_txt):
            defect_val = max(nums[-4:]); correct_val = nums[-1]; break
        check(defect_val is not None and defect_val > 100.0 and correct_val == 100.0,
              "defect_reproduced_max_of_last4_is_MB",
              "max(last4)=%s (>100, the CpuToGpu MBytes that caused 007's false pass) "
              "vs positional GPU %%F=%s" % (defect_val, correct_val))
        # GPU %F > 100 must REFUSE.
        bad = gpu_txt.replace(" 100\n", " 210\n", 1)
        okr = False
        try:
            parse_logview_text(bad, "A", "BAD")
        except Refusal as r:
            okr = "ABOVE 100" in str(r) or "cannot exceed 100" in str(r)
        check(okr, "limbA_refuses_pctf_above_100", "a GPU %F of 210 is refused")

    # ---- SYNTHETIC RUN FIXTURE for the rest --------------------------------
    root = tempfile.mkdtemp(prefix="vmflgpu005_selftest_")

    def build_run(d, **over):
        """A clean CONVERGING triple, two arms, that grades PASS on C1 (in band),
        GATE REACHED on C2. Per-channel/level overrides via over['<key>']."""
        endtime = over.get("endtime", 15000)
        # per-level GPU physics values forming a monotone CONVERGING triple whose
        # fine value is ON the reference (so C1 lands PASS by default).
        vals = dict(
            c1a=(6.20, 5.95, 5.86), c1b=(0.150, 0.142, 0.1392), c1c=(74.0, 70.0, 68.2),
            c2u=(0.160, 0.151, 0.1479), c2d=(-0.090, -0.084, -0.0818), c2t=(293.0, 292.4, 292.21))
        vals.update(over.get("vals", {}))
        for i, (level, cells) in enumerate(LEVELS):
            et = over.get("endtime_%s" % level, endtime)
            for arm in ARMS:
                cd = os.path.join(d, arm, level)
                _make_arm(cd, level, arm, et,
                          {k: v[i] for k, v in vals.items()},
                          d, over)
        return d

    def run(tag, kind, text, builder):
        dd = os.path.join(root, tag)
        os.makedirs(dd, exist_ok=True)
        try:
            builder(dd)
        except Exception as exc:
            check(False, tag, "FIXTURE ERROR: %r" % (exc,))
            return
        del _EMITTED[:]
        try:
            v = grade(dd)
            gk, got = "verdict", v
        except Refusal as r:
            gk, got = "refuse", str(r)
        except Exception as exc:
            check(False, tag, "CRASHED (not a refusal): %s: %s" % (type(exc).__name__, exc))
            return
        if gk != kind:
            check(False, tag, "expected a %s, got a %s: %s" % (kind, gk, got))
            return
        check(text in got, tag, (got if kind == "verdict" else got.split(": ", 1)[-1][:110])
              if text in got else "wrong %s: expected %r in %r" % (kind, text, got))

    # CONTROL: all limbs hold, triple CONVERGING, in band. Whole-row = GATE
    # REACHED (C2 caps it); C1 and B each reach PASS per-limb -- verified below.
    run("control_row_gate_reached", "verdict", "GATE REACHED", lambda d: build_run(d))
    run("c1_out_of_band_gate_fail", "verdict", "GATE FAIL",
        lambda d: build_run(d, vals={"c1a": (9.0, 8.5, 8.2)}))   # Nu far high, still converging
    run("c1_divergent_not_a_result", "verdict", "NOT A RESULT",
        lambda d: build_run(d, vals={"c1b": (0.130, 0.142, 0.170)}))  # e32>e21 divergent
    run("c1_oscillatory_not_a_result", "verdict", "NOT A RESULT",
        lambda d: build_run(d, vals={"c1c": (70.0, 66.0, 69.0)}))     # sign flip
    run("limbB_miss_gate_fail", "verdict", "GATE FAIL",
        lambda d: build_run(d, cpu_scale={"c1a": 1.05}))
    run("completion_rc_refuses", "refuse", "solver rc = 3",
        lambda d: build_run(d, rc={"L1_gpu": 3}))
    run("completion_end_refuses", "refuse", "no 'End' line",
        lambda d: build_run(d, no_end={"L1_gpu": True}))
    run("age_guard_refuses", "refuse", "AGE GUARD",
        lambda d: build_run(d, stale={"L1_gpu": True}))
    run("timecount_refuses", "refuse", "'Time =' lines against a registered endTime",
        lambda d: build_run(d, ntimes={"L1_gpu": 999}))
    run("plateau_unsettled_refuses", "refuse", "has NOT settled",
        lambda d: build_run(d, plateau_bad={"L1_gpu": True}))
    run("plateau_dead_refuses", "refuse", "LIVENESS",
        lambda d: build_run(d, plateau_dead={"L1_gpu": True}))
    run("limbA_absent_refuses", "refuse", "ABSENT table is",
        lambda d: build_run(d, nolog={"L1_gpu": True}))
    run("limbA_leak_refuses", "refuse", "FORCED-CPU CONTROL",
        lambda d: build_run(d, cpu_gpu_leak={"L1": True}))
    # THE KSPSolve-FALLBACK ARM (VMFLGPU007-R2 asymmetry): GPU MatMult %F=100 but the
    # p_rgh KSPSolve %F=0 -> MIN catches it, MAX would have passed it.
    run("limbA_kspsolve_fallback_refuses", "refuse", "tested on the MIN for exactly that reason",
        lambda d: build_run(d, ksp_pctf={"L1_gpu": 0.0}))
    run("blender_stepwise_refuses", "refuse", "NOT one of the continuous blenders",
        lambda d: build_run(d, stepwise={"L1_gpu": True}))
    run("nusselt_absent_refuses", "refuse", "no wall-temperature-gradient channel",
        lambda d: build_run(d, no_nu={"L1_gpu": True}))
    run("ambiguous_reader_refuses", "refuse", "files match",
        lambda d: build_run(d, extra_mid={"L1_gpu": True}))
    run("endtime_mismatch_refuses", "refuse", "different endTimes",
        lambda d: build_run(d, endtime_L1_gpu=14999))

    # C2 can NEVER earn PASS even fully in band and converging, AND C1 DOES earn
    # PASS in the control: verified by inspecting the emitted per-limb lines.
    dd = os.path.join(root, "ceiling_probe")
    os.makedirs(dd, exist_ok=True)
    del _EMITTED[:]
    try:
        build_run(dd)
        grade(dd)
        blob = "\n".join(_EMITTED)
        c2_never_pass = ("LIMB C2" in blob) and all(
            "= PASS" not in ln for ln in blob.splitlines() if ln.startswith("LIMB C2"))
        c1_never_pass = ("LIMB C1" in blob) and all(
            "= PASS" not in ln for ln in blob.splitlines() if ln.startswith("LIMB C1"))
        b_can_pass = any(ln.startswith("PER-LIMB") and "= PASS" in ln for ln in blob.splitlines())
        check(c2_never_pass, "c2_ceiling_never_pass",
              "no LIMB C2 line reports PASS even fully in band (CONTINUUM ceiling)")
        check(c1_never_pass, "c1_ceiling_never_pass",
              "no LIMB C1 line reports PASS even fully in band and CONVERGING "
              "(CONTINUUM ceiling §2f.3 -- a triple does not lift it)")
        check(b_can_pass, "limbB_carries_the_pass",
              "limb B reaches PASS per-limb in the control (the case's PASS credential)")
    except Exception as exc:
        check(False, "c2_ceiling_never_pass", "CRASHED: %r" % (exc,))
        check(False, "c1_ceiling_never_pass", "CRASHED: %r" % (exc,))
        check(False, "limbB_carries_the_pass", "CRASHED: %r" % (exc,))

    # planted-zero control (rule 3) -- SUCCESSOR S2: DRIVEN TO BOTH OUTCOMES on a
    # REAL-SHAPED midHeight sample file written to disk, read back through the
    # parent's own read_line(). The parent's in-memory arm is retired.
    pdir = os.path.join(root, "s2_plant_fixture")
    _make_arm(os.path.join(pdir, "gpu", "L1"), "L1", "gpu", 15000,
              dict(c1a=6.20, c1b=0.1392, c1c=68.2, c2u=0.1479, c2d=-0.0818, c2t=292.21),
              pdir, {})
    gpu_l1 = os.path.join(pdir, "gpu", "L1")
    okp = False
    try:
        r = planted_zero_control(gpu_l1, "P1")
        okp = r["observed"] > PLANT_MIN_FRACTION * r["expected"] > 0.0
        detail_p = ("a plant sized to the U_y channel, written into EVERY row on "
                    "disk and read back through read_line(), moved max U_y by "
                    "%.6g against expected %.6g" % (r["observed"], r["expected"]))
    except Refusal as exc:
        detail_p = "REFUSED: %s" % exc
    check(okp, "planted_zero_fires_on_disk", detail_p)
    # SUPPRESS ARM: the plant never reaches disk, so the control MUST refuse P1a.
    oks = False
    try:
        planted_zero_control(gpu_l1, "P1", _selftest_suppress_plant=True)
    except Refusal as exc:
        oks = "PLANT-BLIND (P1a" in str(exc)
    check(oks, "planted_zero_refuses_when_plant_suppressed",
          "with the plant suppressed from disk the control refuses P1a -- the "
          "control is shown able to FAIL, not merely to pass")

    # ceiling + vocabulary + no bare asserts
    check(TIER_CEILING_C1 == "GATE REACHED" and TIER_CEILING_C2 == "GATE REACHED"
          and LIMB_B_PASS_CAPABLE is True,
          "ceilings", "C1=%r and C2=%r (both CONTINUUM, never PASS -- §2f.3); limb B "
          "PASS-capable=%r (same-discrete-problem identity)"
          % (TIER_CEILING_C1, TIER_CEILING_C2, LIMB_B_PASS_CAPABLE))
    okv = False
    try:
        vocabulary_selfcheck("VERIFIED")
    except Refusal as r:
        okv = "is not one of the fixed vocabulary" in str(r)
    check(okv, "vocabulary_rejects_synonym", "a non-vocabulary verdict is refused")

    n_assert = -1
    try:
        import ast
        n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(open(__file__).read())))
    except Exception:
        pass
    check(n_assert == 0, "zero_assert_statements",
          "ast.Assert nodes = %d (python3 -O strips assert; a guard on one evaporates)" % n_assert)

    import shutil
    shutil.rmtree(root, ignore_errors=True)
    for good, tag, detail in results:
        print("%s  %-40s %s" % ("PASS" if good else "**FAIL**", tag, detail))
    n_ok = sum(1 for g, _, _ in results if g)
    print("")
    print("%d/%d checks behaved as registered%s  (__debug__=%s)"
          % (n_ok, len(results), "" if n_ok == len(results) else "   -- SELFTEST FAILED", __debug__))
    return 0 if n_ok == len(results) else 1


# ---- fixture writer --------------------------------------------------------
def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def _make_arm(cd, level, arm, endtime, vals, root, over):
    key = "%s_%s" % (level, arm)
    os.makedirs(cd, exist_ok=True)
    # 0/ fields (age-guard reference written FIRST)
    _write(os.path.join(cd, "0", "T"), "0/T marker\n")
    if over.get("stale", {}).get(key):
        os.utime(os.path.join(cd, "0", "T"), (2 ** 31, 2 ** 31))
    # 0/omega and 0/k with the blender (STEPWISE only if injected)
    blend = "stepwise" if over.get("stepwise", {}).get(key) else "tanh"
    for fld, wf in (("omega", "omegaWallFunction"), ("k", "kLowReWallFunction")):
        body = "boundaryField {\n"
        for patch in WF_PATCHES:
            body += "  %s { type %s; blender %s; value uniform 1; }\n" % (patch, wf, blend)
        body += "}\n"
        _write(os.path.join(cd, "0", fld), body)
    # endTime fields
    et = str(endtime)
    for f in FIELDS_AT_ENDTIME:
        _write(os.path.join(cd, et, f), "field %s\n" % f)
    # solver log. For the timecount test: last time == endTime but COUNT < endTime
    # (so C3 passes and C4 -- the physics-critical 'Time = count' clause -- fires).
    ntw = over.get("ntimes", {}).get(key)
    if ntw:
        lines = ["Time = %d" % i for i in range(1, ntw)] + ["Time = %d" % int(endtime)]
    else:
        lines = ["Time = %d" % i for i in range(1, int(endtime) + 1)]
    n = len(lines)
    body = "\n".join(lines) + "\n" + "\n".join("ExecutionTime = %d s" % i for i in range(n + 2))
    if not over.get("nolog", {}).get(key):
        leak = over.get("cpu_gpu_leak", {}).get(level) and arm == "cpu"
        pctf = 100.0 if (arm == "gpu" or leak) else 0.0
        cpu2gpu = 2401 if (arm == "gpu" or leak) else 0
        body += ("\nSummary of Stages\n"
                 "Event  Count Time Flop ... CpuToGpu GpuToCpu GPU\n"
                 "  Max Ratio ... Count Size Count Size %F\n")
        ksp_pctf = over.get("ksp_pctf", {}).get(key, pctf)   # KSPSolve fallback arm
        body += ("MatMult 6000 1.0 1.0e0 1.0 1.0e8 1.0 0 0 0 0 0 0 0 0 0 0 0 0 0 1000 2000 %d 7.0e1 0 0.0e0 %g\n"
                 % (cpu2gpu, pctf))
        body += ("KSPSolve 1200 1.0 1.0e0 1.0 1.0e8 1.0 0 0 0 0 0 0 0 0 0 0 0 0 0 300 500 %d 7.0e1 0 0.0e0 %g\n"
                 % (cpu2gpu, ksp_pctf))
    if not over.get("no_end", {}).get(key):
        body += "\nEnd\n"
    _write(os.path.join(cd, "log.buoyantBoussinesqSimpleFoam"), body + "\n")

    # midLine traverse (x, Ux, Uy, Uz, T). Build a profile whose max Uy == vals c1b
    # and whose central dT/dx == vals c1c. cpu arm scaled by cpu_scale for limb B.
    scale = over.get("cpu_scale", {}).get("c1a", 1.0) if arm == "cpu" else 1.0
    c1b = vals["c1b"] * (over.get("cpu_scale", {}).get("c1b", 1.0) if arm == "cpu" else 1.0)
    c1c = vals["c1c"]
    # Sample lines: columns x T Ux Uy Uz (fields sorted alphabetically -> `_T_U`).
    nxs = [W_CAV * i / 399.0 for i in range(400)]
    def midrow(x):
        # Uy peaks at c1b near the hot wall; T linear so dT/dx == c1c at centre.
        uy = c1b * math.sin(math.pi * x / W_CAV)
        T = T_COLD + c1c * x
        return (x, T, 0.0, uy, 0.0)
    mid = "# x T Ux Uy Uz\n" + "\n".join("%.8g %.8g %.8g %.8g %.8g" % midrow(x) for x in nxs)
    _write(os.path.join(cd, "postProcessing", "midLine", str(endtime), "midHeight_T_U.xy"), mid + "\n")
    if over.get("extra_mid", {}).get(key):
        _write(os.path.join(cd, "postProcessing", "midLine", str(endtime), "midHeight_T_U_2.xy"), mid + "\n")
    # lowLine traverse -> C2 vup/vdown/tcore
    vup, vdown, tcore = vals["c2u"], vals["c2d"], vals["c2t"]
    def lowrow(x):
        uy = vdown * math.cos(math.pi * x / W_CAV) ** 3 if x < W_CAV / 2 else vup * math.sin(math.pi * (x - W_CAV/2) / W_CAV)
        return (x, tcore, 0.0, uy, 0.0)
    low = "# x T Ux Uy Uz\n" + "\n".join("%.8g %.8g %.8g %.8g %.8g" % lowrow(x) for x in nxs)
    low += "\n%.8g %.8g 0 %.8g 0\n%.8g %.8g 0 %.8g 0\n%.8g %.8g 0 0 0" % (
        W_CAV*0.98, tcore, vup, W_CAV*0.02, tcore, vdown, W_CAV/2, tcore)
    _write(os.path.join(cd, "postProcessing", "lowLine", str(endtime), "lowHeight_T_U.xy"), low + "\n")
    # grad(T)_hotWall.raw -> C1a Nu = |grad(T)_x|_avg * W / DT_WALL (so Nu == c1a)
    if not over.get("no_nu", {}).get(key):
        nu = vals["c1a"] * (over.get("cpu_scale", {}).get("c1a", 1.0) if arm == "cpu" else 1.0)
        gradmean = nu * DT_WALL / W_CAV
        rows = "\n".join("%.8g %.8g 0.005 %.8g 0 0" % (W_CAV, 0.01 + 0.02 * j, gradmean) for j in range(20))
        whf = "# grad(T)  FACE_DATA 20\n# x y z  grad(T)_x grad(T)_y grad(T)_z\n" + rows
        _write(os.path.join(cd, "postProcessing", "wallGradT", str(endtime), "grad(T)_hotWall.raw"), whf + "\n")
    # probeU plateau channel
    settled = not over.get("plateau_bad", {}).get(key)
    dead = over.get("plateau_dead", {}).get(key)
    series = []
    for i in range(1200):
        if dead:
            uy = 0.10
        elif settled:
            uy = 0.10 + 0.05 * math.exp(-i / 40.0)   # flat over the last-1000 window
        else:
            uy = 0.10 + 0.05 * math.sin(i / 3.0)   # never settles
        series.append("%d (0 %.8g 0)" % (i, uy))
    _write(os.path.join(cd, "postProcessing", "probeU", "0", "U"),
           "# probe U\n" + "\n".join(series) + "\n")
    # yPlus record
    _write(os.path.join(cd, "postProcessing", "yPlusFO", str(endtime), "yPlus.dat"),
           "# time patch min max average\n"
           + "".join("%s\t%s\t0.2\t3.0\t1.0\n" % (endtime, p) for p in WF_PATCHES))
    # RUN_RC
    et_reg = over.get("endtime_%s" % key, endtime)
    _write(os.path.join(root, "RUN_RC.%s.%s" % (level, arm)),
           "arm = %s\nlevel = %s\nrc = %d\nendtime = %s\n"
           % (arm, level, over.get("rc", {}).get(key, 0), et_reg))


def main(argv=None):
    ap = argparse.ArgumentParser(description=VERSION)
    ap.add_argument("--run-root")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.run_root:
        print("usage: grade_vmflgpu005.py --run-root <dir> | --selftest")
        return 2
    try:
        grade(a.run_root)
        return 0
    except Refusal as r:
        print(str(r))
        return 2


if __name__ == "__main__":
    sys.exit(main())
