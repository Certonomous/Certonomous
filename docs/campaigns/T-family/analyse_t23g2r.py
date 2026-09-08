#!/usr/bin/env python3
"""T23G2R COMPARATOR.  Grades the NEAR-WALL FIX-SUCCESSOR to T23G2 -- the same
three-level ladder with the inner boundary-layer first-cell height reduced so
`centrebody_up` clears max y+ <= 1.0 (T23G2's G-YPLUS GATE FAIL), plus the
endTime margin that lets the reused G-CONV be met on L2.

EVERY GATE, THRESHOLD AND BAND IS REUSED VERBATIM FROM THE FROZEN T23G2 AND IS
NOT RELAXED (T23G2R_PREREGISTRATION.md section 3).  Only three things differ from
analyse_t23g2.py, and each is a diff a reviewer can see: (1) the run target /
level names / endTimes point at T23G2R; (2) the ABSENT-primary-y+-instrument
branch REFUSES instead of falling through -- the prospective R6 that T23G2 owed
its successor (T23G2_RESULTS.md section 8; T23G2R section 5.2); (3) the comparator
records its own running blob as provenance (VERIFICATION_CHARTER.md section 2au.2
print-only, since a self-referential IDENTICAL assertion against its own freeze
commit is a git pre-image -- see the note at GRADING_PATH_FREEZE_COMMIT) and
carries a --selftest that drives the planted controls RED/GREEN.

IT LAUNCHES NOTHING.  It reads artifacts and refuses.

DEFAULT DENY, EVERYWHERE.  A missing artifact, an unparsable one, a control that
cannot be constructed, or any non-PASS is a REFUSAL (exit 2) -- never a softer
number and never a silently skipped gate.  An unevaluated gate is NOT a passed
one (VERIFICATION_CHARTER.md section 9).

WHAT THIS FILE DOES NOT REIMPLEMENT, ON PURPOSE:
  * rule 5 gating, the observed order, the GCI and the planted-zero contract all
    come from ``scripts/roache_triple.py``.  ``PLANT``, ``FS`` and the state
    names are IMPORTED and never redefined (CLAUDE.md rule 14 -- a lesson is not
    applied until every call site asserts it).
  * rule 4 completion is DELEGATED to ``mark_done_t23.py`` as a subprocess.  No
    completion logic lives here.

THE ONE THING THIS COMPARATOR MUST NOT DO, AND THE REASON:
  ** GRADE THE FINE VALUE, NEVER THE RICHARDSON EXTRAPOLATE. **
  The extrapolate sign inversion is a known live defect in this family's
  comparators, survivable only because it is display-only everywhere it lives.
  This file was written AFTER that defect was known, so gating on the
  extrapolate here would make a display-only defect load-bearing.  The
  extrapolate is REPORTED beside the fine value and is never a gate input.
"""
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/ubuntu/Certonomous"
RUNS = os.path.join(REPO, "verification/runs/T-family/T23G2R_runs")
T23_RUNS = os.path.join(REPO, "verification/runs/T-family/T23_runs")

sys.path.insert(0, os.path.join(REPO, "scripts"))
import roache_triple as RT                                    # noqa: E402
from roache_triple import PLANT, FS, refuse                    # noqa: E402

sys.path.insert(0, HERE)
import t23g_readonly_diagnosis as GEOM                         # noqa: E402

# --------------------------------------------------------------------------
# THE REGISTRATION, TRANSCRIBED.  Every number below is quoted from the frozen
# file; none is chosen here.  Section references are to T23G2_PREREGISTRATION.md.
# --------------------------------------------------------------------------
LEVELS = ("T23G2R_L1", "T23G2R_L2", "T23G2R_L3")
# endTime raised from T23G2's 6000/12000/24000 so the REUSED (unchanged) G-CONV
# is met on L2, which missed by 4.1% at 12000 (T23G2R_PREREGISTRATION.md section
# 2.3).  Raising the iteration budget MEETS a frozen gate; it does not move one.
ENDTIME = {"T23G2R_L1": 8000, "T23G2R_L2": 16000, "T23G2R_L3": 28000}  # T23G2R 2.3
# UNCHANGED from T23G2 section 2.1: the near-wall fix reduces the first-cell
# height only, leaving layer/cell counts identical, so G-MESHSIM's 2.25 ratio holds.
CELLS = {"T23G2R_L1": 40320, "T23G2R_L2": 90720, "T23G2R_L3": 204120}  # 2.1
DIM = 2                       # 5 deg wedge, one cell circumferentially; 2.1
R_REFINE = 1.5                # 2.25x cells per step at dim = 2

T_REF = 288.0                 # triples are graded on dT = T - 288.0 K; 3

# G-ORDER, as amended by A1.2.  [0.5, 1.5] and NOT [1.5, 2.5], because the
# formal order of the energy equation's convection term is ONE:
#   T23G_F/system/fluid/fvSchemes line 33 -- `div(phi,h) bounded Gauss upwind`
# Sanaa's section 0 point 3 is scheme-relative ("p within 0.5 of the scheme's
# formal order"); [0.5, 1.5] IS her rule applied, not a relaxation of it (A2.3).
ORDER_BAND = (0.5, 1.5)
ORDER_QUANTITY = "Q4"         # core volume-averaged T; section 3

# G-BAND, as amended by A1.2: tightened from [45, 60] once the scheme stopped
# changing.  Applied to the FINE value of Q1, on dT.
BAND_Q1 = (46.0, 56.0)

# AMENDMENT v1.1, 2026-09-02 -- REPAIR R4, BAND LIMB ONLY.
#
# GRANTED AND WIDENED: VERIFICATION_CHARTER.md v1.38 section 2d.7, commit
# 3dad5bae.  THE ROLLUP-EXCLUSION LIMB OF R4 WAS REFUSED AND IS NOT IMPLEMENTED
# HERE; see the note in main().
#
# WHO IS REGISTERED TO RECEIVE Q4's BAND, QUOTED FROM THE FROZEN section 3 ROLE
# TABLE: Q1 at :452 "reported; receives Q4's band", Q3 at :453 "receives Q4's
# band", Q2 at :454 "receives Q4's band".  THREE, AND ONLY THREE.
#   * Q6 at :455 -- "volume-averaged T | housing | reported; carried because
#     section 0.3 measured it and it costs nothing".  NO BAND.
#   * Q4 at :450 -- "PRIMARY ORDER QUANTITY -- G-ORDER and the GCI are computed
#     on this and on nothing else".  NO FINE-VALUE BAND.
# The frozen code passed BAND_Q1 to grade_ladder for ALL FIVE at one line, so the
# UNREGISTERED BAND REACHED TWO QUANTITIES, not the one the petition reported.
# Repairing only Q6 would leave half the defect standing while reporting it
# repaired, which is why the ruling widened the grant.
#
# Q4 IS NOT LEFT UNGATED BY THIS.  Its registered gate is G-ORDER on p(Q4)
# (:450, :834), which REPAIR R3 makes reachable in the same amendment.  What Q4
# never had was a registered FINE-VALUE band.
BAND_TRANSFER_REGISTERED = ("Q1", "Q3", "Q2")

# G-CONV, section 5.3.  `h` carries Sanaa's tightened 1e-9; the rest 1e-8.
RESID_TOL = {"h": 1.0e-9, "Uy": 1.0e-8, "Uz": 1.0e-8,
             "p_rgh": 1.0e-8, "k": 1.0e-8, "omega": 1.0e-8}
UX_EXCLUSION_MAX = 1.0e-12    # measured per level, never assumed

# G-PLATEAU, section 5.3 as amended: EVERY graded quantity, not only the maxima.
PLATEAU_WINDOW_ITERS = 2000
PLATEAU_MAX_SPREAD_K = 0.005          # Sanaa's tightened stationarity
PLATEAU_MAX_SPREAD_REL = 0.001        # 0.1 % for Q5, which is in W

# G-RATIO, section 5.3: Sanaa's section 0 point 2, promoted to a gate.
RATIO_MIN = 10.0

# G-YPLUS, as amended by A2.2: GATED on EVERY wall patch, EVERY level.
YPLUS_MAX = 1.0
YPLUS_INSTRUMENT_AGREE_REL = 0.02     # 2 %; disagreement REFUSES, never averages

# G-MESHSIM, section 5.5 as amended by A2.4.
MESHSIM_CELL_RATIO = 2.25
MESHSIM_CELL_TOL = 1e-9
MESHSIM_D1_RATIO = 1.5
MESHSIM_D1_TOL = 0.005                # 1.500 +/- 0.005
MESHSIM_MIN_HOUSING_CELLS = 8         # at the COARSEST level; T23G carried 4

NU = 1.8e-05 / 1.2            # fluid kinematic viscosity, m2/s (mu/rho, const)

# --------------------------------------------------------------------------
# AMENDMENT v1.1, 2026-09-02 -- REPAIR R2 (T23G2_PREREGISTRATION.md:671).
#
# GRANTED AND WIDENED: VERIFICATION_CHARTER.md v1.38 section 2d.7, commit
# 3dad5bae.  The registration at :671 says this comparator will "record its own
# grading-path shas on the artifact's face"; it recorded none -- a REGISTERED
# FEATURE NEVER BUILT (section 2d.4.3), not a departure from a registered path.
#
# FIVE FILES, NOT THE FOUR PETITIONED.  The ruling refused the petitioned scope:
# `t23g_readonly_diagnosis` is imported at :46 and used in `yplus_from_fields`,
# `_first_cell_heights`, `gate_meshsim` and `_u_maxima`, so it is on the grading
# path for G-YPLUS, G-MESHSIM and G-CONV, and it was in neither the freeze table
# nor the petition's list.  A sha recorder that leaves a grading-path member
# silent is the defect it was built to cure.
#
# THE DUAL-SHA CONDITION (section 2d.4.3) IS WHY TWO COLUMNS ARE PRINTED AND NOT
# ONE.  The recorder records this file's sha -- and ADDING the recorder CHANGES
# that sha.  The registration contemplated provenance present from the FIRST
# GRADED SOLVE; what this repair can deliver is provenance FROM THE REPAIR
# FORWARD, carrying a POST-REPAIR sha that is NOT the blob frozen at
# pre-registration.  The registered intent is UNRECOVERABLE and this recorder
# does not claim to restore it.
# PIN-AT-FREEZE.  The supervisor sets this to the commit that freezes T23G2R at
# freeze time (rule 2 / VERIFICATION_CHARTER section 2b).  While it reads
# "PIN-AT-FREEZE" the file is an UNFROZEN DRAFT: verify_self() (called first in
# main) REFUSES to GRADE, because a comparator that has not been pinned to a
# freeze commit has not been shown to be the file that ran.  --selftest does NOT
# need it -- it tests the instrument, not the freeze.
#
# THE SELF MEMBER CANNOT ASSERT "IDENTICAL vs its own freeze commit" -- SECTION
# 2au.2.  An earlier draft of this block claimed it could ("this file's committed
# blob IS the blob that runs, so verify_self can assert IDENTICAL, not merely
# record two columns").  THAT CLAIM WAS FALSE AND IS RETRACTED: the freeze sha
# would have to live INSIDE the hashed file (this very constant), so writing the
# freeze commit into the body changes the blob, which changes the commit -- a
# SHA-1 pre-image / fixed point git cannot construct (established empirically,
# heat-transfer lane 2026-09-08; pinning to a first/predecessor commit fails the
# same way, because writing any pin moves the blob off every prior committed one).
# The SELF member is therefore handled by the VERIFICATION_CHARTER section 2au.2
# PRINT-ONLY pattern, exactly as analyse_t10avf2_sweep.py (blob f3619318, frozen
# at 5fb1d8a9 with EXPECTED_SELF_BLOB = None): verify_self PRINTS the running blob
# as provenance and does NOT refuse on it.  The freeze is anchored OUTSIDE the
# hashed content -- by a FREEZE-PIN line in the freeze commit message recording
# this blob, plus the supervisor's grade-time on-disk byte-identity check -- and
# by EXPECTED_SELF_BLOB below only IF it is ever set (assert-only-if-set; it stays
# None because setting it to this file's own blob is the same self-reference
# impossibility).  The NON-self grading-path members are not self-referential;
# their dual-sha record stands UNCHANGED in print_grading_path_shas (REPAIR R2).
GRADING_PATH_FREEZE_COMMIT = "043ddce7eec16737de05f459902483f2f24ad791"  # re-pin: commit carrying the T23G2R_L*-extended mark_done_t23.py (prereg section 10.5); build_t23g2r.py inherited from ancestor 2a1e03a6
EXPECTED_SELF_BLOB = None          # section 2au.2 print-only; asserted only if the
                                   # supervisor ever sets it (see note above).
SELF_REL = "docs/campaigns/T-family/analyse_t23g2r.py"
GRADING_PATH = (
    "docs/campaigns/T-family/T23G2R_PREREGISTRATION.md",
    "docs/campaigns/T-family/analyse_t23g2r.py",
    "docs/campaigns/T-family/t23g_readonly_diagnosis.py",
    "verification/runs/T-family/T23_runs/mark_done_t23.py",
    "scripts/roache_triple.py",
)


def note(msg):
    print(msg)


def _need(path, what):
    if not os.path.isfile(path):
        refuse("%s: %s is not on disk; the gate it feeds CANNOT be evaluated "
               "and an unevaluated gate is not a passed one" % (what, path))
    return path


def case_dir(level):
    d = os.path.join(RUNS, level)
    if not os.path.isdir(d):
        refuse("case directory %s does not exist; T23G2R has not been run" % d)
    return d


def verify_self():
    """SELF-HASH provenance (CLAUDE.md rule 2; VERIFICATION_CHARTER.md section
    2au.2 print-only pattern, precedent analyse_t10avf2_sweep.py @5fb1d8a9).

    While GRADING_PATH_FREEZE_COMMIT is the placeholder "PIN-AT-FREEZE", the file
    is an unfrozen DRAFT and this REFUSES -- an unpinned comparator has not been
    shown to be the file that ran, so it must not grade.

    Once pinned, the SELF member is PRINT-ONLY.  A comparator CANNOT assert its
    working-tree blob IDENTICAL to its blob at its OWN freeze commit: the freeze
    sha would have to live inside the hashed file, so writing it changes the blob
    and hence the commit -- a SHA-1 pre-image (see the note at
    GRADING_PATH_FREEZE_COMMIT).  So this PRINTS the running blob as provenance
    and does NOT refuse on it; the freeze is anchored by the commit-message
    FREEZE-PIN plus the supervisor's grade-time byte-identity check.  The only
    SELF assertion is against EXPECTED_SELF_BLOB, and only if it is set.  The
    NON-self grading-path members are recorded, unchanged, by
    print_grading_path_shas (REPAIR R2)."""
    def _g(args):
        r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True,
                           text=True)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    now = _g(["hash-object", os.path.abspath(__file__)])
    if GRADING_PATH_FREEZE_COMMIT == "PIN-AT-FREEZE":
        refuse("SELF-HASH: GRADING_PATH_FREEZE_COMMIT is still the DRAFT "
               "placeholder 'PIN-AT-FREEZE'.  This comparator is UNFROZEN and "
               "will not grade; the supervisor pins the freeze commit at freeze "
               "(rule 2).  Working-tree blob is %s.  Use --selftest to exercise "
               "the instrument without a freeze." % (now or "UNAVAILABLE"))
    if EXPECTED_SELF_BLOB is not None and now != EXPECTED_SELF_BLOB:
        refuse("SELF-HASH: this comparator's working-tree blob %s does NOT match "
               "EXPECTED_SELF_BLOB %s.  The file that is running is not the file "
               "that was frozen; it will not grade (rule 2)."
               % (now or "UNAVAILABLE", EXPECTED_SELF_BLOB))
    note("SELF-HASH: running blob %s (freeze pin %s) -- PRINT-ONLY provenance "
         "(section 2au.2).  The SELF member is anchored by the commit-message "
         "FREEZE-PIN and the grade-time byte-identity check, not by a self-"
         "referential IDENTICAL assertion%s.\n"
         % (now or "UNAVAILABLE", GRADING_PATH_FREEZE_COMMIT,
            "" if EXPECTED_SELF_BLOB is None else "; EXPECTED_SELF_BLOB asserted"))


# ==========================================================================
# RULE 4 -- DELEGATED, CALLED, NEVER REIMPLEMENTED
# ==========================================================================
def require_done():
    """`mark_done_t23.py` as a subprocess.  T23G2's endTime is a LEVEL VARIABLE
    (A1.6), unlike T23G's invariant 10000, so each level is checked against its
    own registered endTime and the value is passed explicitly rather than left
    to a default that would silently check the wrong time."""
    md = os.path.join(T23_RUNS, "mark_done_t23.py")
    if not os.path.isfile(md):
        refuse("the completion instrument %s is not on disk; rule 4 cannot be "
               "evaluated and this file will NOT reimplement it" % md)
    note("COMPLETION -- rule 4, DELEGATED to %s and CALLED\n"
         % os.path.relpath(md, REPO))
    # endTime is NOT passed: that instrument reads it from each case's own
    # system/controlDict (mark_done_t23.py:160), so T23G2's per-level endTime
    # (A1.6) is handled correctly without this file telling it what to expect.
    # A comparator that ASSERTED the endTime it wanted would be marking its own
    # homework.
    bad = []
    for lv in LEVELS:
        r = subprocess.run([sys.executable, md, "--root", RUNS, lv],
                           capture_output=True, text=True)
        for line in (r.stdout or "").rstrip().split("\n"):
            if line.strip():
                note("  | " + line)
        if r.returncode != 0:
            bad.append((lv, r.returncode, (r.stderr or "").strip()[:300]))
    if bad:
        refuse("rule 4 completion FAILED for %s; a run that fails any clause is "
               "not done, and this comparator will not grade it"
               % ", ".join("%s (rc=%d) %s" % b for b in bad))
    note("")


# ==========================================================================
# SERIES READERS -- the function-object output the build script writes
# ==========================================================================
def _read_dat(path, want_field=None, value_col=-1):
    """A tab-separated OpenFOAM functionObject .dat.  Returns [(iter, value)].
    REFUSES on an unparsable file rather than returning an empty series that
    would read downstream as 'no movement'."""
    out = []
    for line in open(path, errors="replace"):
        if line.startswith("#"):
            continue
        f = [c.strip() for c in line.split("\t") if c.strip()]
        if len(f) < 2:
            continue
        if want_field is not None:
            if len(f) < 5 or f[1] != want_field:
                continue
            out.append((float(f[0]), float(f[4])))
        else:
            try:
                out.append((float(f[0]), float(f[value_col])))
            except ValueError:
                continue
    if not out:
        refuse("%s parsed to an EMPTY series; an empty series is not a "
               "stationary one" % path)
    return out


def series_minmax(cd, region):
    p = _need(os.path.join(cd, "postProcessing", region, "%s_T" % region,
                           "0", "fieldMinMax.dat"), "fieldMinMax(%s)" % region)
    return _read_dat(p, want_field="T")


def series_volavg(cd, region):
    nm = "core_volavg_T" if region == "core" else "housing_volavg_T"
    p = _need(os.path.join(cd, "postProcessing", region, nm, "0",
                           "volFieldValue.dat"), nm)
    return _read_dat(p)


def series_patch_T(cd):
    p = _need(os.path.join(cd, "postProcessing", "housing", "housing_patch_T",
                           "0", "surfaceFieldValue.dat"), "housing_patch_T")
    return _read_dat(p)


def series_wall_heat(cd):
    p = _need(os.path.join(cd, "postProcessing", "housing", "housing_wall_heat",
                           "0", "surfaceFieldValue.dat"), "housing_wall_heat")
    return _read_dat(p)


# ==========================================================================
# G-PLATEAU and G-RATIO -- section 5.3, on EVERY graded quantity
# ==========================================================================
def plateau(series, endtime, rel=False):
    """Peak-to-peak over the last PLATEAU_WINDOW_ITERS iterations.  Selection is
    by ITERATION SPAN, never by sample count, because Q1/Q3 sample every 100 and
    the T23G2 additions sample every 200 (build script comment)."""
    tail = [v for (it, v) in series if it >= endtime - PLATEAU_WINDOW_ITERS]
    if len(tail) < 3:
        refuse("only %d samples in the last %d iterations; G-PLATEAU needs at "
               "least 3 and an unevaluated gate is not a passed one"
               % (len(tail), PLATEAU_WINDOW_ITERS))
    spread = max(tail) - min(tail)
    last = series[-1][1]
    lim = (abs(last) * PLATEAU_MAX_SPREAD_REL) if rel else PLATEAU_MAX_SPREAD_K
    return ("PLATEAUED" if spread <= lim else "NOT PLATEAUED"), spread, lim, len(tail)


def g_ratio(name, iter_change, level_diffs, control=None,
            iterative_states=None, plateau_states=None):
    """Sanaa's section 0 point 2, gated: the iterative change on the finest level
    must be at least 10x smaller than the SMALLEST consecutive inter-level
    difference.  Otherwise the observed order is noise, not discretisation.

    AMENDMENT v1.1, 2026-09-02 -- REPAIR R5.  THE EXACT-ZERO LICENCE IS NOW
    EXECUTABLE INSTEAD OF DOCUMENTARY.  The frozen comment below claimed that
    "the planted-zero control is what makes an exact zero mean something" while
    NOTHING IN THIS FUNCTION LOOKED AT A CONTROL.  On T23G2 that claim was
    carrying real weight and the ruling says so: G-RATIO passes on all six
    quantities ONLY because the measured iterative change is exactly 0.0, and 13
    of the 18 registered controls did not exist.  Six exact zeros were carrying
    six G-RATIO passes on a licence that was not there -- standing rule 3's exact
    shape.  The zero-branch now REFUSES unless the control for that reader, at
    that level, was constructed and PASSED.

    AMENDMENT v1.2 -> v1.3, 2026-09-02 -- REPAIR R8.  THE LAW IS STATED AT
    VERIFICATION_CHARTER.md v1.42 sections 2d.10 and 2p.8, commit c4007e42.  NO
    REPAIR WAS ORDERED AND NONE WAS PETITIONED: the ruling states that "whether
    and when analyse_t23g2.py is changed is heat-transfer's, subject to section
    2d.1 and to section 2d.4.1's full-force (3) and (4)".  R8 IS THIS TEAM'S
    CHANGE, NOT A COMPLIED-WITH ORDER.

    THE PASS THIS REPAIRS FAILED ON TWO INDEPENDENT GROUNDS, EITHER SUFFICIENT,
    AND BOTH ARE IMPLEMENTED SEPARATELY BELOW SO THAT NEITHER HIDES THE OTHER.

    LIMB 1 -- section 2d.10, THE LICENSING-GATE CLAUSE, ruled generally: "a gate
    whose purpose is to LICENSE another quantity must return NOT A RESULT
    whenever that quantity is itself NOT A RESULT.  A licence issued for a voided
    claim is not a verdict -- it is a CATEGORY ERROR, an assurance about an
    object that does not exist."  This function's own stated purpose is the
    sentence four lines above the first amendment block: "otherwise the observed
    order is noise, not discretisation."  IT EXISTS TO LICENSE THE OBSERVED
    ORDER.  Rule 5 step (a) has already voided that order, so there is no order
    for G-RATIO to license.  The test below MIRRORS step (a) exactly -- the same
    two tests, on the same two dicts, that roache_triple.grade_ladder applies at
    :605-618, and that gate_order was taught to read under R7.  No new criterion,
    no new threshold, no new state name, no reimplementation.

    LIMB 2 -- THE GROUND THE PETITION DID NOT RAISE, ADDED BY THE RULING: "with
    iter_change exactly 0.0, the zero-branch returns infinity REGARDLESS OF THE
    NUMERATOR ENTIRELY.  The PASS is attributable to the denominator being zero
    and to no property of the ladder -- it would have returned infinity and PASS
    for any numerator, contaminated or pristine.  That is section 2p in its own
    right: A PASS FROM A DEGENERATE PATH."  The ruling's own words for what the
    number then is: UNINTERPRETABLE, not meaningless.  A large value could mean
    grid differences dominate iterative error, or that a level's iterative error
    inflated the inter-level differences, and the instrument cannot distinguish
    them.  So the exact-zero branch no longer returns PASS; it returns NOT A
    RESULT and prints what it would have graded.

    R5's REFUSAL IS DELIBERATELY LEFT IN FRONT OF BOTH LIMBS AND IS NOT
    WEAKENED.  An exact zero with no planted-zero control still REFUSES (exit 2),
    which is stronger than any verdict; R8 must not convert an R5 refusal into a
    NOT A RESULT merely because a later limb would have voided the cell anyway.

    UNTOUCHED BY R8, AND STATED SO IT CANNOT BE ASSUMED OTHERWISE: RATIO_MIN =
    10.0 at :106 is unchanged -- not widened, not narrowed, not moved -- and
    G-RATIO's registered meaning at T23G2_PREREGISTRATION.md section 5.3 is
    unchanged.  The gate is not retired and is still evaluated on every graded
    quantity.  What changes is ONLY the precondition under which it is
    interpretable.

    DIRECTION: STRICTLY RESTRICTIVE.  Every path added below can only turn a
    PASS or a GATE FAIL INTO NOT A RESULT -- the one direction CLAUDE.md rule 5
    permits -- and no path can turn a non-PASS into a PASS.

    Returns (verdict, ratio, smallest, grounds), where `grounds` is the list of
    R8 limbs that fired and is EMPTY on PASS and on GATE FAIL.
    """
    smallest = min(abs(d) for d in level_diffs)
    if iter_change <= 0.0:
        # an exact zero passes, and the planted-zero control is what makes an
        # exact zero mean something (rule 3).  Reported, not silently blessed.
        # R8 LEAVES THIS REFUSAL EXACTLY WHERE R5 PUT IT, AND FIRST.
        if control is None:
            refuse("G-RATIO would PASS %s on an EXACT ZERO iterative change and "
                   "NO planted-zero control was supplied for that reader at the "
                   "finest level.  A zero from a reader not shown able to see a "
                   "non-zero is not evidence (CLAUDE.md rule 3)." % name)
        RT.assert_plant_control(control)

    # What an unlicensed gate would have graded.  Printed either way, so that a
    # NOT A RESULT never hides the number it declined to interpret.
    would_be = float("inf") if iter_change <= 0.0 else smallest / iter_change

    # ---- REPAIR R8 -- rule 5 step (a), BEFORE any licence is issued ----------
    # The mirror of roache_triple.grade_ladder:605-618, on the two dicts that
    # function is given; the refusal when iterative states were never supplied
    # is grade_ladder:609-612's refusal, not a new one.
    if iterative_states is None:
        refuse("G-RATIO: no iterative-convergence states were supplied for %s; "
               "step (a) of rule 5 cannot be evaluated for this gate and an "
               "unevaluated step is not a passed one" % name)
    bad_it = sorted(k for k, v in iterative_states.items() if v != "CONVERGED")
    bad_pl = sorted(k for k, v in (plateau_states or {}).items()
                    if v != "PLATEAUED")

    grounds = []
    if bad_it or bad_pl:
        grounds.append(
            "R8 LIMB 1 (VERIFICATION_CHARTER.md section 2d.10, the licensing-"
            "gate clause): levels %s are not iteratively converged or not "
            "plateaued, so rule 5\n  step (a) has ALREADY VOIDED the observed "
            "order that G-RATIO exists to license.  There is NO ORDER for this "
            "gate to license, and a licence\n  issued for a voided claim is a "
            "CATEGORY ERROR, not a verdict."
            % ",".join(bad_it + bad_pl))
    if iter_change <= 0.0:
        grounds.append(
            "R8 LIMB 2 (VERIFICATION_CHARTER.md section 2d.10's second ground, "
            "section 2p): the iterative change is EXACTLY 0.0, so this gate's "
            "zero-branch\n  returns infinity REGARDLESS OF THE NUMERATOR "
            "ENTIRELY.  The numerator was never consulted, so a PASS here would "
            "be attributable to the\n  denominator being zero and to NO PROPERTY "
            "OF THE LADDER -- a pass from a degenerate path.  The ratio is "
            "UNINTERPRETABLE, not meaningless.")
    if grounds:
        return "NOT A RESULT", would_be, smallest, grounds

    ratio = would_be
    return (("PASS" if ratio >= RATIO_MIN else "GATE FAIL"), ratio, smallest, [])


# ==========================================================================
# G-YPLUS -- A2.2: GATED on EVERY wall patch, EVERY level, two instruments
# ==========================================================================
def _endtime_for(cd):
    for lv, t in ENDTIME.items():
        if os.path.basename(cd) == lv:
            return str(t)
    refuse("cannot resolve endTime for %s" % cd)


def yplus_from_fields(cd, u_path=None):
    """Independent y+ from U, nut and the polyMesh.  The wall condition is
    `nutLowReWallFunction`, so nut_w = 0 and u_tau = sqrt(nu * U_t / y).

    AMENDMENT v1.1, 2026-09-02 -- REPAIR R5.  `u_path` exists SO THAT THIS READER
    CAN BE PLANTED INTO AND READ BACK.  T23G2_PREREGISTRATION.md:601 registers of
    this reader: "It must plant a known perturbation and read it back, and refuse
    if it cannot see it (rule 3)."  It planted nothing, and argued its validity
    DOCUMENTARILY instead -- "its validation is A1.4".  A CITATION IS NOT A
    CONTROL.  `control_yplus_field_reader` below writes a planted copy of `U` to
    disk and drives THIS function over it; nothing else uses `u_path`, and the
    default path is the frozen one.  A1.4's validation is NOT WITHDRAWN and is
    restated here verbatim from the frozen docstring, because a repair must not
    quietly delete a record: "This reader's ability to see what it claims is
    established in T23G2_PREREGISTRATION.md A1.4: on T23G_M it reproduced
    T23_RESULTS.md section 4's OpenFOAM-produced values to every digit that
    record carries."  What changes is its STATUS: it now ACCOMPANIES a live
    control instead of STANDING IN FOR one."""
    mf = GEOM.Mesh(cd, "fluid")
    et = _endtime_for(cd)
    Ui, Ub = GEOM.read_field(_need(u_path or os.path.join(cd, et, "fluid", "U"),
                                   "U"))
    nuti, nutb = GEOM.read_field(_need(os.path.join(cd, et, "fluid", "nut"), "nut"))
    Uc = GEOM.expand(Ui, mf.nCells)
    nutc = GEOM.expand(nuti, mf.nCells)
    out = {}
    for pn, pb in mf.boundary.items():
        if pb["type"] not in ("wall", "mappedWall"):
            continue
        nf, sf = pb["nFaces"], pb["startFace"]
        if Ub[pn][0] == "no-value" and "noSlip" in str(Ub[pn][1]):
            Uw = [(0.0, 0.0, 0.0)] * nf
        else:
            Uw = GEOM.expand(Ub[pn], nf)
        nutw = GEOM.expand(nutb[pn], nf)
        vals = []
        for i in range(nf):
            fi = sf + i
            c = mf.owner[fi]
            fa = mf.fa[fi]
            A = math.sqrt(sum(x * x for x in fa))
            nh = tuple(x / A for x in fa)
            dv = tuple(mf.fc[fi][k] - mf.C[c][k] for k in range(3))
            y = abs(sum(dv[k] * nh[k] for k in range(3)))
            rel = tuple(Uc[c][k] - Uw[i][k] for k in range(3))
            dot = sum(rel[k] * nh[k] for k in range(3))
            tang = tuple(rel[k] - dot * nh[k] for k in range(3))
            Ut = math.sqrt(sum(x * x for x in tang))
            utau = math.sqrt(max((NU + nutw[i]) * Ut / y, 0.0))
            vals.append(y * utau / NU)
        out[pn] = dict(min=min(vals), max=max(vals),
                       avg=sum(vals) / len(vals), n=len(vals))
    if not out:
        refuse("%s: no wall patches found; y+ CANNOT be evaluated" % cd)
    return out


def yplus_from_log(cd, path=None):
    """The PRIMARY instrument: `chtMultiRegionSimpleFoam -postProcess -func
    yPlus`, whose log is filed as log.yPlus.fluid.  Plain `postProcess` is
    MEASURED BLIND on this family -- it does not construct the compressible
    turbulence model -- so a log whose own text says so, or whose numbers are
    perfect zeros, is REFUSED and never read (CLAUDE.md rule 3)."""
    p = path or os.path.join(cd, "log.yPlus.fluid")
    if not os.path.isfile(p):
        return None
    txt = open(p, errors="replace").read()
    if "Unable to find turbulence model" in txt:
        return "BLIND"
    out = {}
    for m in re.finditer(r"patch\s+(\S+)\s+y\+\s*:\s*min\s*=\s*([-\d.eE+]+)"
                         r"\s*,?\s*max\s*=\s*([-\d.eE+]+)\s*,?\s*average\s*=\s*"
                         r"([-\d.eE+]+)", txt):
        out[m.group(1)] = dict(min=float(m.group(2)), max=float(m.group(3)),
                               avg=float(m.group(4)))
    if not out:
        return None
    if all(v["max"] == 0.0 and v["min"] == 0.0 for v in out.values()):
        refuse("%s reports y+ = 0 on every patch.  A perfect zero from a reader "
               "not shown able to see a non-zero is REFUSED, not read "
               "(CLAUDE.md rule 3)." % p)
    return out


# ==========================================================================
# AMENDMENT v1.1, 2026-09-02 -- REPAIR R5, THE TWO Y+ READER CONTROLS.
#
# GRANTED: VERIFICATION_CHARTER.md v1.38 section 2d.7, commit 3dad5bae -- "R5
# GRANTED, AND IT IS THE MOST IMPORTANT OF THE SIX".
#
# THE DEPARTURE.  :624-625 registers "Six quantities x three levels = 18
# controls, plus the two y+ readers = 20".  The frozen code called
# `plant_control_for` at ONE line, at the FINEST LEVEL ONLY, for FIVE quantities:
# 5 controls against a registered 20.  :601 registers that the cross-check y+
# reader "must plant a known perturbation and read it back, and refuse if it
# cannot see it (rule 3)"; it planted nothing.
#
# THE PLANT IS MULTIPLICATIVE HERE, AND THAT IS NOT A REDEFINITION OF `PLANT`.
# `PLANT` is IMPORTED and never redefined (rule 14).  y+ is not linear in U, so
# an ADDITIVE plant has no closed-form expected shift; a SCALE of (1 + PLANT) on
# every vector in `U` has one, EXACTLY:
#     every fluid wall patch is `noSlip`, so U_wall is IDENTICALLY zero, so
#     U_t -> s * U_t exactly, u_tau = sqrt(nu_eff * U_t / y) -> sqrt(s) * u_tau,
#     and y+ = y * u_tau / nu -> sqrt(s) * y+ on EVERY face of EVERY wall patch.
# THE noSlip PRECONDITION IS ASSERTED FROM THE FILE, NEVER ASSUMED: a wall patch
# carrying a `value` block breaks the closed form and REFUSES.
#
# THIS CONTROL CAN FAIL, WHICH IS THE ONLY PROPERTY THAT MAKES IT A CONTROL.  A
# reader that ignored `U`, cached a previous read, or could not see the planted
# file returns the SAME y+ and the expected ratio sqrt(1 + PLANT) = 1.000617 is
# missed by six orders of magnitude.
# ==========================================================================
YPLUS_PLANT_SCALE = 1.0 + PLANT       # PLANT imported, NEVER redefined (rule 14)
YPLUS_PLANT_TOL_REL = 1.0e-9


def _plant_u_file(src, dst, scale):
    """Write a copy of an OpenFOAM vector field with EVERY vector scaled.  The
    FoamFile header is copied verbatim; only the body is transformed."""
    txt = open(src, errors="replace").read()
    i = txt.find("// * * *")
    if i < 0:
        refuse("%s carries no FoamFile header delimiter; the plant would have to "
               "guess where the data starts, and it will not" % src)
    j = txt.index("\n", i) + 1
    head, body = txt[:j], txt[j:]
    pat = re.compile(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)")
    n = [0]

    def rep(m):
        n[0] += 1
        return "(%s %s %s)" % tuple(repr(float(m.group(k)) * scale)
                                    for k in (1, 2, 3))

    out = pat.sub(rep, body)
    if n[0] == 0:
        refuse("%s: the plant matched NO vector, so nothing was perturbed and "
               "the control would be vacuous" % src)
    open(dst, "w").write(head + out)
    return n[0]


def control_yplus_field_reader(cd, base):
    """CONTROL 19 of the registered 20.  Plants into `U` on disk and drives the
    REAL reader over the planted file.  REFUSES if the reader cannot see it."""
    mf = GEOM.Mesh(cd, "fluid")
    up = _need(os.path.join(cd, _endtime_for(cd), "fluid", "U"), "U")
    _, Ub = GEOM.read_field(up)
    for pn, pb in mf.boundary.items():
        if pb["type"] not in ("wall", "mappedWall"):
            continue
        if not (Ub[pn][0] == "no-value" and "noSlip" in str(Ub[pn][1])):
            refuse("wall patch %s of %s is not `noSlip`, so the planted scale "
                   "has no closed-form expected shift on it.  The control's "
                   "prediction is asserted from the file, never assumed, and an "
                   "unpredictable control is refused rather than relaxed."
                   % (pn, cd))
    tmp = up + ".plant"
    try:
        nvec = _plant_u_file(up, tmp, YPLUS_PLANT_SCALE)
        planted = yplus_from_fields(cd, u_path=tmp)
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)
    expected = math.sqrt(YPLUS_PLANT_SCALE)
    worst = (None, 0.0)
    for pn in sorted(base):
        b, a = base[pn]["max"], planted[pn]["max"]
        if b <= 0.0:
            refuse("%s/%s: base y+ max is %r, so a multiplicative plant could "
                   "not move it and the control would be vacuous" % (cd, pn, b))
        if a == b:
            refuse("%s/%s: the independent y+ reader returned the IDENTICAL "
                   "value %.12g from a planted `U`.  It cannot see a "
                   "perturbation it is required to see, so its zeros and its "
                   "y+ mean nothing (CLAUDE.md rule 3)." % (cd, pn, b))
        err = abs(a / b - expected) / expected
        if err > worst[1]:
            worst = (pn, err)
        if err > YPLUS_PLANT_TOL_REL:
            refuse("%s/%s: planted/base y+ max = %.15g, expected sqrt(1 + PLANT)"
                   " = %.15g, relative miss %.3e > %.0e.  The reader saw "
                   "SOMETHING but not the planted quantity, which is worse than "
                   "seeing nothing." % (cd, pn, a / b, expected, err,
                                        YPLUS_PLANT_TOL_REL))
    return dict(passed=True, planted=PLANT, scale=YPLUS_PLANT_SCALE,
                expected_ratio=expected, worst_patch=worst[0],
                worst_rel_miss=worst[1], vectors_planted=nvec,
                reader="y+ independent field reader", artifact=up,
                level=os.path.basename(cd))


def control_yplus_log_reader(cd, base_log):
    """CONTROL 20 of the registered 20.  Plants a known ADDITIVE shift into a
    copy of `log.yPlus.fluid` and re-reads it with the REAL regex parser.

    R6 IS NOW LIVE (section 5.2), so an ABSENT primary log has already REFUSED in
    gate_yplus before this control is reached; only a BLIND primary log (a log
    that exists and declares its turbulence model absent -- A1.4's validated
    case) reaches here as a None base_log and is DISCLOSED, counted against the
    registered 20 rather than refused, exactly as under T23G2."""
    if not isinstance(base_log, dict) or not base_log:
        return None
    p = os.path.join(cd, "log.yPlus.fluid")
    pn = sorted(base_log)[0]
    before = base_log[pn]["max"]
    txt = open(p, errors="replace").read()
    pat = re.compile(r"(patch\s+%s\s+y\+\s*:\s*min\s*=\s*[-\d.eE+]+\s*,?\s*max"
                     r"\s*=\s*)([-\d.eE+]+)" % re.escape(pn))
    m = pat.search(txt)
    if m is None:
        refuse("%s: the control could not locate the `max` field for patch %s "
               "that the reader itself parsed; a control that cannot be "
               "constructed is a refusal, never a pass" % (p, pn))
    planted_txt = (txt[:m.start()] + m.group(1)
                   + repr(float(m.group(2)) + PLANT) + txt[m.end():])
    tmp = p + ".plant"
    try:
        open(tmp, "w").write(planted_txt)
        after_all = yplus_from_log(cd, path=tmp)
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)
    if not isinstance(after_all, dict) or pn not in after_all:
        refuse("%s: the primary y+ reader could not re-read the planted copy at "
               "all; it cannot be shown able to see a perturbation and its "
               "readings mean nothing (CLAUDE.md rule 3)" % p)
    return RT.external_plant_control("y+ primary log reader @%s/%s"
                                     % (os.path.basename(cd), pn),
                                     before, after_all[pn]["max"],
                                     artifact=p, level=os.path.basename(cd))


def yplus_reader_controls(cd, base_field, base_log):
    """The two registered y+ reader controls (:624-625), on the FINEST level --
    the level whose reading carries the graded fine value.  Both are ASSERTED,
    and a failure is a refusal, not a note."""
    note("  PLANTED-ZERO CONTROLS ON THE TWO Y+ READERS (registered at "
         ":601 and :624-625)")
    cf = control_yplus_field_reader(cd, base_field)
    note("    [19/20] independent field reader @%s: planted x(1 + %g) into %d "
         "vectors of U;\n            every wall patch moved by sqrt(1 + PLANT) "
         "= %.12f, worst relative miss %.3e\n            on %s -- PASSED"
         % (cf["level"], PLANT, cf["vectors_planted"], cf["expected_ratio"],
            cf["worst_rel_miss"], cf["worst_patch"]))
    cl = control_yplus_log_reader(cd, base_log)
    if cl is None:
        note("    [20/20] primary log reader @%s: NOT CONSTRUCTED -- the "
             "primary instrument is\n            BLIND (an ABSENT log has "
             "already refused under R6, section 5.2), so the\n            "
             "registered count of 20 is NOT MET and this BLIND case is "
             "DISCLOSED rather\n            than refused (A1.4)."
             % os.path.basename(cd))
    else:
        RT.assert_plant_control(cl)
        note("    [20/20] primary log reader @%s: planted %g, read back %.12g "
             "-- PASSED"
             % (cl["level"], cl["planted"], cl["read_back_delta"]))
    note("")
    return cf, cl


def gate_yplus():
    note("G-YPLUS -- A2.2: GATED on EVERY wall patch, EVERY level (max <= %.1f)"
         % YPLUS_MAX)
    rows, verdict = {}, "PASS"
    for lv in LEVELS:
        cd = case_dir(lv)
        field = yplus_from_fields(cd)
        log = yplus_from_log(cd)
        if isinstance(log, dict):
            for pn, d in log.items():
                if pn in field:
                    a, b = d["max"], field[pn]["max"]
                    if abs(a - b) > YPLUS_INSTRUMENT_AGREE_REL * max(abs(a), abs(b), 1e-30):
                        refuse("y+ instruments DISAGREE on %s/%s: log %.6g vs "
                               "field %.6g (> %.0f%%).  A disagreement is a "
                               "REFUSAL, never an average."
                               % (lv, pn, a, b, 100 * YPLUS_INSTRUMENT_AGREE_REL))
            note("  %s: primary instrument PRESENT and agrees with the "
                 "independent reader to within %.0f%%" % (lv, 100 * YPLUS_INSTRUMENT_AGREE_REL))
        elif log == "BLIND":
            note("  %s: primary instrument BLIND (its own log says the "
                 "turbulence model was not in the database); the independent "
                 "reader carries the gate, and its validation is A1.4" % lv)
        else:
            # PROSPECTIVE R6 (T23G2R_PREREGISTRATION.md section 5.2).  T23G2's
            # gate_yplus continued to grade on the independent reader when the
            # primary log was ABSENT (T23G2_RESULTS.md section 8); verification
            # REFUSED R6 as a section 2d.1 repair of T23G2 but recorded it a good
            # change owed to "the NEXT registration".  This IS that registration,
            # so an ABSENT primary y+ log now REFUSES and does NOT fall through to
            # the independent reader.  It can only ADD a refusal; it relaxes
            # nothing.  BLIND is untouched -- a log that exists and declares itself
            # blind is A1.4's validated case, not the absence R6 addresses.
            refuse("%s: the primary y+ instrument log.yPlus.fluid is ABSENT.  "
                   "PROSPECTIVE R6 (section 5.2): an absent primary y+ instrument "
                   "REFUSES rather than falling through to the independent reader "
                   "alone.  The gate is registered on TWO instruments (section "
                   "5.4); one of them is missing." % lv)
        rows[lv] = field
        if lv == LEVELS[-1]:
            yplus_reader_controls(cd, field, log)     # REPAIR R5, controls 19-20
        for pn in sorted(field):
            d = field[pn]
            ok = d["max"] <= YPLUS_MAX
            if not ok:
                verdict = "GATE FAIL"
            note("    %-18s n=%4d  min %7.4f  avg %7.4f  max %7.4f   %s"
                 % (pn, d["n"], d["min"], d["avg"], d["max"],
                    "PASS" if ok else "GATE FAIL"))
    note("  G-YPLUS: %s\n" % verdict)
    return verdict, rows


# ==========================================================================
# G-MESHSIM -- section 5.5, measured from the BUILT mesh
# ==========================================================================
def gate_meshsim():
    note("G-MESHSIM -- section 5.5 / A2.4, measured from the BUILT polyMesh")
    verdict = "PASS"
    cells = {}
    for lv in LEVELS:
        cd = case_dir(lv)
        cells[lv] = {r: GEOM.Mesh(cd, r).nCells for r in ("fluid", "housing", "core")}
        tot = sum(cells[lv].values())
        if tot != CELLS[lv]:
            refuse("%s has %d cells; the registration says %d.  The mesh that "
                   "ran is not the mesh that was registered."
                   % (lv, tot, CELLS[lv]))
    for a, b in zip(LEVELS, LEVELS[1:]):
        for r in ("fluid", "housing", "core"):
            ratio = cells[b][r] / cells[a][r]
            ok = abs(ratio - MESHSIM_CELL_RATIO) <= MESHSIM_CELL_TOL
            if not ok:
                verdict = "GATE FAIL"
            note("  cells %-8s %s/%s = %.9f  %s"
                 % (r, b, a, ratio, "PASS" if ok else "GATE FAIL"))
    d1 = {lv: _first_cell_heights(case_dir(lv)) for lv in LEVELS}
    for a, b in zip(LEVELS, LEVELS[1:]):
        for pn in sorted(d1[a]):
            ratio = d1[a][pn] / d1[b][pn]
            ok = abs(ratio - MESHSIM_D1_RATIO) <= MESHSIM_D1_TOL
            if not ok:
                verdict = "GATE FAIL"
            note("  first cell %-18s %s/%s = %.6f  %s"
                 % (pn, a, b, ratio, "PASS" if ok else "GATE FAIL"))
    hc = cells[LEVELS[0]]["housing"]
    nz_mid = 140
    across = hc // nz_mid
    ok = across >= MESHSIM_MIN_HOUSING_CELLS
    if not ok:
        verdict = "GATE FAIL"
    note("  cells across the housing wall at the COARSEST level: %d (floor %d; "
         "T23G carried 4)  %s" % (across, MESHSIM_MIN_HOUSING_CELLS,
                                  "PASS" if ok else "GATE FAIL"))
    note("  G-MESHSIM: %s\n" % verdict)
    return verdict


def _first_cell_heights(cd):
    mf = GEOM.Mesh(cd, "fluid")
    out = {}
    for pn, pb in mf.boundary.items():
        if pb["type"] not in ("wall", "mappedWall"):
            continue
        nf, sf = pb["nFaces"], pb["startFace"]
        ds = []
        for i in range(nf):
            fi = sf + i
            c = mf.owner[fi]
            fa = mf.fa[fi]
            A = math.sqrt(sum(x * x for x in fa))
            nh = tuple(x / A for x in fa)
            dv = tuple(mf.fc[fi][k] - mf.C[c][k] for k in range(3))
            ds.append(abs(sum(dv[k] * nh[k] for k in range(3))))
        out[pn] = sum(ds) / len(ds)
    return out


# ==========================================================================
# G-CONV -- section 5.3
# ==========================================================================
def gate_conv():
    note("G-CONV -- section 5.3; h <= 1e-9 (Sanaa's tightened criterion), "
         "others <= 1e-8")
    verdict, states = "PASS", {}
    for lv in LEVELS:
        cd = case_dir(lv)
        res = _final_residuals(cd, ENDTIME[lv])
        bad = {k: res[k] for k, tol in RESID_TOL.items()
               if k not in res or res[k] > tol}
        mx = _u_maxima(cd, ENDTIME[lv])
        ratio = (mx[0] / mx[2]) if mx[2] > 0 else float("inf")
        if ratio > UX_EXCLUSION_MAX:
            refuse("%s: Ux is excluded from G-CONV BY MEASUREMENT, and the "
                   "measurement does not support it here: max|Ux|/max|Uz| = "
                   "%.3e > %.0e.  The exclusion is re-measured per level and "
                   "never assumed." % (lv, ratio, UX_EXCLUSION_MAX))
        states[lv] = "CONVERGED" if not bad else "NOT CONVERGED"
        if bad:
            verdict = "GATE FAIL"
        note("  %-11s %-14s worst asserted: %s   (Ux excluded, "
             "max|Ux|/max|Uz| = %.3e)"
             % (lv, states[lv],
                ", ".join("%s %.3e" % (k, v) for k, v in sorted(bad.items()))
                or "all within tolerance", ratio))
    note("  G-CONV: %s\n" % verdict)
    return verdict, states


def _final_residuals(cd, endtime):
    p = _need(os.path.join(cd, "log.solve"), "log.solve")
    txt = open(p, errors="replace").read()
    out = {}
    for f in ("Ux", "Uy", "Uz", "h", "p_rgh", "k", "omega"):
        ms = re.findall(r"Solving for %s, Initial residual = ([\d.eE+-]+)"
                        % re.escape(f), txt)
        if ms:
            out[f] = float(ms[-1])
    if "h" not in out:
        refuse("%s: no `h` residual in log.solve; G-CONV cannot be evaluated"
               % cd)
    return out


def _u_maxima(cd, endtime):
    p = _need(os.path.join(cd, str(endtime), "fluid", "U"), "U at endTime")
    i, _ = GEOM.read_field(p)
    kind, data = i
    if kind != "nonuniform":
        refuse("%s: U internalField is %r, not a nonuniform list" % (p, kind))
    return [max(abs(v[k]) for v in data) for k in range(3)]


# ==========================================================================
# THE QUANTITIES
# ==========================================================================
def read_quantities():
    """Every quantity is read from its function-object SERIES, whose last sample
    is the endTime value.  That gives the graded value and the plateau series
    from one artifact, which is what T23G could not do for Q2."""
    q = {}
    for lv in LEVELS:
        cd = case_dir(lv)
        et = ENDTIME[lv]
        s_h = series_minmax(cd, "housing")
        s_c = series_minmax(cd, "core")
        s_q4 = series_volavg(cd, "core")
        s_q6 = series_volavg(cd, "housing")
        s_q2 = series_patch_T(cd)
        s_q5 = series_wall_heat(cd)
        for nm, s in (("Q1", s_h), ("Q3", s_c), ("Q4", s_q4),
                      ("Q6", s_q6), ("Q2", s_q2), ("Q5", s_q5)):
            if s[-1][0] != et:
                refuse("%s/%s: last series sample is at iteration %g, not the "
                       "registered endTime %d" % (lv, nm, s[-1][0], et))
        q[lv] = dict(Q1=s_h[-1][1], Q3=s_c[-1][1], Q4=s_q4[-1][1],
                     Q6=s_q6[-1][1], Q2=s_q2[-1][1], Q5=s_q5[-1][1],
                     _series=dict(Q1=s_h, Q3=s_c, Q4=s_q4, Q6=s_q6,
                                  Q2=s_q2, Q5=s_q5))
    return q


def plant_control_for(qname, level, series_path_fn):
    """A planted-zero control on the REAL artifact, read back through the REAL
    parser -- not the generic series control.  A control that cannot be built is
    a refusal, never a pass."""
    cd = case_dir(level)
    p = series_path_fn(cd)
    before = _read_dat(p, want_field=("T" if qname in ("Q1", "Q3") else None))[-1][1]
    lines = open(p, errors="replace").read().split("\n")
    idx = max(k for k, l in enumerate(lines) if l.strip() and not l.startswith("#"))
    orig = lines[idx]
    cols = orig.split("\t")
    col = 4 if qname in ("Q1", "Q3") else len(cols) - 1
    cols[col] = repr(float(cols[col]) + PLANT)
    lines[idx] = "\t".join(cols)
    tmp = p + ".plant"
    open(tmp, "w").write("\n".join(lines))
    try:
        after = _read_dat(tmp, want_field=("T" if qname in ("Q1", "Q3") else None))[-1][1]
    finally:
        os.remove(tmp)
    return RT.external_plant_control("%s @%s" % (qname, level), before, after,
                                     artifact=p, level=level)


# ==========================================================================
# AMENDMENT v1.1, 2026-09-02 -- REPAIR R5, THE EIGHTEEN QUANTITY CONTROLS.
#
# :624-625 registers "Six quantities x three levels = 18 controls".  The frozen
# code built FIVE: `plant_control_for` was called at one line, at LEVELS[-1]
# only, for Q4 Q1 Q2 Q3 Q6.  Q5 had no control at all, and neither coarse nor
# medium level had one for anything.  THIRTEEN OF THE EIGHTEEN DID NOT EXIST.
#
# WHY THIS IS NOT BOOKKEEPING.  The ruling: G-RATIO passes on all six quantities
# ONLY because the measured iterative change is exactly 0.0, and `g_ratio`
# returns PASS on a zero on the STATED GROUND that a planted-zero control is what
# makes an exact zero mean something.  For thirteen of them that control was
# absent.  Even T23G2's PASSING gates were unlicensed.
#
# EVERY CONTROL IS ASSERTED AS IT IS BUILT.  `RT.assert_plant_control` REFUSES on
# a control that did not read its plant back, so an unconstructable or blind
# control stops the comparator instead of being counted.
# ==========================================================================
QUANTITIES = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6")


def all_quantity_plant_controls():
    """18 controls: every quantity, every level.  Returns {(q, level): control}."""
    note("PLANTED-ZERO CONTROLS ON EVERY QUANTITY AND EVERY LEVEL -- REPAIR R5, "
         "registered at :624-625")
    out = {}
    for qn in QUANTITIES:
        marks = []
        for lv in LEVELS:
            pc = plant_control_for(qn, lv, (lambda cd, _q=qn:
                                            _series_path(cd, _q)))
            RT.assert_plant_control(pc)
            out[(qn, lv)] = pc
            marks.append("%s %s" % (lv, "PASSED" if pc["passed"] else "FAILED"))
        note("  %s  planted %g  |  %s" % (qn, PLANT, "  |  ".join(marks)))
    note("  %d of the 18 registered quantity controls CONSTRUCTED AND PASSED\n"
         % len(out))
    return out


# ==========================================================================
# AMENDMENT v1.1, 2026-09-02 -- REPAIR R3.  G-ORDER, MADE REACHABLE.
#
# GRANTED: VERIFICATION_CHARTER.md v1.38 section 2d.7, commit 3dad5bae, "GRANTED
# -- AND MEASURED INERT".
#
# THE DEPARTURE, EXHIBITED BY QUOTATION AND BY MEASUREMENT.  A1.2 at
# T23G2_PREREGISTRATION.md:834 registers G-ORDER: "p(Q4) from the finest three
# levels in [0.5, 1.5] -> PASS; CONVERGING but outside -> GATE FAIL".  In the
# frozen code ORDER_BAND and ORDER_QUANTITY each occurred TWICE, both second
# occurrences inside a single note(), and RT.grade_ladder's signature carries no
# order-band parameter -- so G-ORDER COULD NOT RETURN GATE FAIL UNDER ANY VALUE
# OF p.  A registered gate unreachable in code is a departure; condition (2) is
# met under section 2d.5.
#
# THE BAND IS NOT INVENTED HERE.  ORDER_BAND = (0.5, 1.5) is frozen PRE-COMPUTE
# at :833-834 and is not touched by this repair.
#
# DIRECTION: RESTRICTIVE.  This can only ADD a GATE FAIL; it can remove none.
# The ruling records that on this data it adds none.
# ==========================================================================
def _apply_band_registration(row):
    """REPAIR R4, BAND LIMB.  A band verdict on a quantity the registration never
    gave a band to is NOT a graded verdict, and this makes that visible in the
    row rather than leaving it to be inferred from the registration.

    WHY THE ROW IS DOWNGRADED AND NOT REMOVED.  The rollup-exclusion limb of R4
    was REFUSED (section 2d.7): "REMOVING A ROW FROM A ROLLUP CAN ONLY WEAKEN THE
    ROLLUP OR LEAVE IT EQUAL.  IT CAN NEVER STRENGTHEN IT.  A rollup exclusion is
    therefore ALWAYS a permissive change and requires REGISTERED TEXT, never an
    inference."  No registered text excludes a reported-only quantity's verdict
    from the rollup.  So the row STAYS in the rollup and its verdict is instead
    made honest: with no registered band there is no band claim to make, and the
    row yields NO RESULT rather than an unregistered PASS.

    DIRECTION, and it is the whole safety argument: this can only turn a PASS or
    a GATE FAIL INTO NOT A RESULT, which is the one direction rule 5 permits and
    the direction roache_triple._seal already enforces.  It can never turn a
    non-PASS into a PASS.
    """
    if row["quantity"] in BAND_TRANSFER_REGISTERED:
        row["band_registered"] = True
        return row
    row["band_registered"] = False
    note("    BAND NOT REGISTERED FOR %s (T23G2_PREREGISTRATION.md section 3 "
         "role table transfers\n    Q4's band to Q1 :452, Q3 :453 and Q2 :454, "
         "and to NOBODY ELSE).  The band verdict\n    printed above is "
         "DISCLOSED, NOT GRADED: it is what an UNREGISTERED band would\n    have "
         "said, and it licenses nothing." % row["quantity"])
    if row["verdict"] != "NOT A RESULT":
        note("    VERDICT DOWNGRADED %s -> NOT A RESULT: with no registered "
             "band there is no\n    band claim to make.  The row is NOT removed "
             "from the rung rollup -- the\n    rollup-exclusion limb of R4 was "
             "REFUSED (section 2d.7)." % row["verdict"])
        row["verdict"] = "NOT A RESULT"
        row["why"] = ("no fine-value band is registered for %s (section 3 role "
                      "table); the band printed beside this row is unregistered "
                      "and grades nothing, so no band claim is made and the row "
                      "yields NO RESULT.  It remains in the rung rollup: "
                      "VERIFICATION_CHARTER.md section 2d.7 refuses rollup "
                      "exclusion without registered text."
                      % row["quantity"])
    else:
        note("    (the row was already NOT A RESULT on rule 5's earlier steps; "
             "the unregistered\n    band changed nothing about that.)")
    return row


def gate_order(rows):
    """G-ORDER on the PRIMARY ORDER QUANTITY (:450), folded into the rollup.

    The registered clause bites only on a CONVERGING triple -- "CONVERGING but
    outside -> GATE FAIL".  Where the finest triple is not CONVERGING there is no
    order claim to gate, and an absent measurement is reported as absent, never
    as a pass (VERIFICATION_CHARTER.md section 9).

    AMENDMENT v1.1 -> v1.2, 2026-09-02 -- REPAIR R7.  GRANTED at
    VERIFICATION_CHARTER.md v1.41 section 2d.9.1, commit 79bcfd83, on
    heat-transfer's petition at
    docs/campaigns/T-family/T23G2_R7_ORDER_GATE_PETITION.md.

    THE DEFECT R7 REPAIRS, AND IT WAS SHIPPED BY R3.  As delivered, this
    function read exactly two fields -- row["orders"][-1] and row["states"][-1]
    -- and graded on them.  BOTH ARE POPULATED UNCONDITIONALLY AT ROW
    CONSTRUCTION (scripts/roache_triple.py:597-598), which happens BEFORE rule
    5 step (a) executes at :604-618 and sets the row's verdict to NOT A RESULT.
    A row that step (a) has voided therefore STILL CARRIES a CONVERGING finest
    triple and a numeric order, and this gate read exactly those two.  The
    2026-09-02 capture is the evidence: "VERDICT: NOT A RESULT -- levels
    T23G2_L2 are not iteratively converged or not plateaued" once per graded
    quantity, and then "G-ORDER: PASS" forty-seven lines later, in the same
    output.

    CLAUDE.md rule 5, verbatim: "The gate can only turn a PASS or GATE FAIL
    INTO NOT A RESULT, never the reverse."  A PASS emitted on a claim step (a)
    has already voided is the reverse, and that is the departure R7 repairs.

    THE REPAIR MIRRORS grade_ladder's STEP (a) AND INVENTS NO CRITERION.  The
    two tests below are the same two tests, applied to the same two dicts, that
    roache_triple.grade_ladder applies at :605-618 -- the refusal when
    iterative-convergence states were never supplied, and the void when any
    level is not "CONVERGED" or not "PLATEAUED".  grade_ladder writes both
    dicts onto the very row it hands back (:601-602); this function now reads
    them instead of ignoring them.  No new threshold, no new state name, no
    reimplementation.

    UNTOUCHED BY R7, AND STATED SO IT CANNOT BE ASSUMED OTHERWISE:
    ORDER_BAND = (0.5, 1.5) and ORDER_QUANTITY = "Q4", both frozen pre-compute
    at T23G2_PREREGISTRATION.md:833-834, are unchanged -- not widened, not
    narrowed, not moved.  The gate is not retired.  What changes is ONLY the
    precondition under which the gate is evaluable.

    DIRECTION: STRICTLY RESTRICTIVE.  It can only turn a PASS or a GATE FAIL
    INTO NOT A RESULT -- the one direction rule 5 permits -- and it can never
    turn a non-PASS into a PASS.
    """
    note("G-ORDER -- A1.2 at T23G2_PREREGISTRATION.md:834, on %s, band %s"
         % (ORDER_QUANTITY, ORDER_BAND))
    row = rows.get(ORDER_QUANTITY)
    if row is None:
        refuse("G-ORDER is registered on %s and no row for it was graded; an "
               "unevaluated gate is not a passed one" % ORDER_QUANTITY)
    p = row["orders"][-1]
    state = row["states"][-1]

    # ---- REPAIR R7 -- rule 5 step (a), BEFORE any grid claim is gated -------
    # The mirror of roache_triple.grade_ladder:605-618, on the dicts that
    # function wrote onto this row at :601-602.
    it_states = row.get("iterative_convergence")
    pl_states = row.get("plateau")
    if it_states is None:
        refuse("G-ORDER: no iterative-convergence states are recorded on the "
               "%s row; step (a) of rule 5 cannot be evaluated for this gate "
               "and an unevaluated step is not a passed one" % ORDER_QUANTITY)
    bad_it = sorted(k for k, v in it_states.items() if v != "CONVERGED")
    bad_pl = sorted(k for k, v in (pl_states or {}).items()
                    if v != "PLATEAUED")

    if bad_it or bad_pl:
        verdict = "NOT A RESULT"
        note("  REPAIR R7 (VERIFICATION_CHARTER.md section 2d.9.1): levels %s "
             "are not iteratively\n  converged or not plateaued, so rule 5 "
             "step (a) has ALREADY VOIDED the grid claim\n  this gate would "
             "otherwise grade.  There is NO ORDER CLAIM to gate."
             % ",".join(bad_it + bad_pl))
        note("  The observed order is %s and the finest triple reads %s.  BOTH "
             "ARE PRINTED because\n  they are exactly what an unlicensed gate "
             "would have graded, and NEITHER licenses\n  anything: the band "
             "[%.1f, %.1f] on %s is untouched and remains registered."
             % ("None" if p is None else "%.4f" % p, state,
                ORDER_BAND[0], ORDER_BAND[1], ORDER_QUANTITY))
    elif p is None or state != "CONVERGING":
        verdict = "NOT A RESULT"
        note("  finest triple is %s and the observed order is %s; there is NO "
             "ORDER CLAIM to gate" % (state, "None" if p is None else "%.4f" % p))
    else:
        verdict = ("PASS" if ORDER_BAND[0] <= p <= ORDER_BAND[1]
                   else "GATE FAIL")
        note("  p(%s) = %.4f, band [%.1f, %.1f], finest triple %s"
             % (ORDER_QUANTITY, p, ORDER_BAND[0], ORDER_BAND[1], state))
    note("  G-ORDER: %s\n" % verdict)
    return verdict


# ==========================================================================
# REPAIR R2 -- the grading-path sha recorder.  IT GRADES NOTHING.
# ==========================================================================
def _git(args):
    r = subprocess.run(["git"] + args, cwd=REPO, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def grading_path_shas():
    """(rel, post-repair working-tree blob, pre-registration frozen blob).

    TWO DIFFERENT OBJECTS, labelled as two (section 2d.4.3).  The left column is
    what is running NOW; the right is what stood in the tree at
    GRADING_PATH_FREEZE_COMMIT, the commit that froze this comparator.
    """
    out = []
    for rel in GRADING_PATH:
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p):
            refuse("grading-path member %s is not on disk; the path this "
                   "comparator grades on cannot be recorded" % rel)
        now = _git(["hash-object", p])
        frozen = _git(["rev-parse", "%s:%s"
                       % (GRADING_PATH_FREEZE_COMMIT, rel)])
        out.append((rel, now or "UNAVAILABLE", frozen or "ABSENT-AT-FREEZE"))
    return out


def print_grading_path_shas():
    """SANAA'S UNIVERSAL RULE OF 2026-08-26 GOVERNS THE CHOICE NOT TO REFUSE ON
    AN UNAVAILABLE SHA: bookkeeping never voids physics.  A missing FILE is a
    refusal above, because a grading-path member that is not on disk cannot have
    graded anything.  A git query that cannot answer is INFRASTRUCTURE: it is
    printed as UNAVAILABLE, loudly, and it does not void a solve.  This is the
    same posture `analyse_t23g.py:grading_path_shas` took under its own
    section 2d.1 grant (DEAD_LEVER_AUDIT section 27.4)."""
    note("GRADING-PATH SHAS -- REPAIR R2, registered at "
         "T23G2_PREREGISTRATION.md:671")
    note("  THIS RECORDER GRADES NOTHING.  It reads no field and moves no "
         "comparison.")
    note("  Frozen column = the blob in %s, the commit that froze this "
         "comparator." % GRADING_PATH_FREEZE_COMMIT)
    for rel, now, frozen in grading_path_shas():
        same = "IDENTICAL" if now == frozen else "DIFFERS"
        note("  %s" % rel)
        note("      post-repair (working tree) : %s" % now)
        note("      pre-registration (frozen)  : %s   %s" % (frozen, same))
    note("")
    note("  THE TWO COLUMNS ARE TWO DIFFERENT OBJECTS AND ARE NOT INTERCHANGEABLE.")
    note("  THIS RECORDER DOES NOT RESTORE THE REGISTERED PROVENANCE AND DOES "
         "NOT CLAIM TO:")
    note("  :671 contemplated shas present FROM THE FIRST GRADED SOLVE.  Adding "
         "the recorder\n  CHANGES this file's sha, so only the forward half is "
         "available (section 2d.4.3).")
    note("  NO GRADED SOLVE WAS EVER PRODUCED UNDER A COMPARATOR CARRYING THIS "
         "RECORDER.\n")


# ==========================================================================
def main(argv):
    if "--selftest" in argv:
        return selftest()

    note("=" * 74)
    note("T23G2R COMPARATOR -- gates REUSED VERBATIM from frozen T23G2 "
         "(T23G2R_PREREGISTRATION.md section 3)")
    note("GRADING THE FINE VALUE.  The Richardson extrapolate is REPORTED and "
         "NEVER GATED ON.")
    note("=" * 74 + "\n")

    verify_self()                      # rule 2 self-hash, before any gate
    print_grading_path_shas()          # REPAIR R2, before the first gate
    require_done()
    ms = gate_meshsim()
    cv, it_states = gate_conv()
    yv, ypl = gate_yplus()

    q = read_quantities()
    controls = all_quantity_plant_controls()     # REPAIR R5 -- 18, all asserted

    # ---- G-PLATEAU and G-RATIO, on EVERY graded quantity -----------------
    note("G-PLATEAU and G-RATIO -- section 5.3, on EVERY graded quantity")
    pl_states, pv, rv = {}, "PASS", "PASS"
    r8_grounds = {}           # REPAIR R8 -- ground -> the quantities it voided
    for qn in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6"):
        pl_states[qn] = {}
        for lv in LEVELS:
            st, spread, lim, n = plateau(q[lv]["_series"][qn], ENDTIME[lv],
                                         rel=(qn == "Q5"))
            pl_states[qn][lv] = st
            if st != "PLATEAUED":
                pv = "GATE FAIL"
        vals = [q[lv][qn] for lv in LEVELS]
        diffs = [vals[0] - vals[1], vals[1] - vals[2]]
        _, sp, _, _ = plateau(q[LEVELS[-1]]["_series"][qn], ENDTIME[LEVELS[-1]],
                              rel=(qn == "Q5"))
        # REPAIR R5: the finest-level control for THIS quantity is what licenses
        # an exact-zero PASS, and g_ratio now refuses without it.
        # REPAIR R8: the same two dicts rule 5 step (a) reads are now handed to
        # the gate that licenses the order, so it cannot license a voided claim.
        # The keyword order below is LOAD-BEARING and is not cosmetic: the
        # registered mutation D5 (T23G2_MUTATION_SET_REGISTERED.md:61) patches
        # the `control=` keyword argument together with the call's CLOSING
        # PAREN as one literal string, and asserts it occurs EXACTLY ONCE.  R8
        # therefore keeps `control=` LAST in the argument list, and deliberately
        # does not quote that literal anywhere else in this file, so a
        # registered mutation is not silently retired by a repair.
        rst, ratio, smallest, grounds = g_ratio(
            qn, sp, diffs, iterative_states=it_states,
            plateau_states=pl_states[qn],
            control=controls[(qn, LEVELS[-1])])
        # REPAIR R8: NOT A RESULT DOMINATES GATE FAIL in this rollup.  It is the
        # one direction rule 5 permits, and reporting a voided cell as GATE FAIL
        # would be a verdict-vocabulary error in the strict direction as well.
        if rst == "NOT A RESULT":
            rv = "NOT A RESULT"
        elif rst != "PASS" and rv != "NOT A RESULT":
            rv = "GATE FAIL"
        for g in grounds:
            r8_grounds.setdefault(g, []).append(qn)
        note("  %s  plateau %s | finest iterative change %.6e, smallest "
             "inter-level difference %.6e, ratio %.1f (needs >= %.0f)  %s"
             % (qn, "/".join(pl_states[qn][lv][:4] for lv in LEVELS),
                sp, smallest, ratio, RATIO_MIN, rst))
    for g in r8_grounds:
        note("  %s" % g)
        note("  applies to: %s" % ", ".join(r8_grounds[g]))
    if r8_grounds:
        note("  THE TWO GROUNDS ARE INDEPENDENT AND EITHER ALONE IS "
             "SUFFICIENT.  Every number above is PRINTED because it is exactly "
             "what an\n  unlicensed gate would have graded, and NEITHER "
             "licenses anything: RATIO_MIN = %.0f is UNTOUCHED and G-RATIO "
             "remains registered\n  on every graded quantity."
             % RATIO_MIN)
    note("  G-PLATEAU: %s    G-RATIO: %s\n" % (pv, rv))

    # ---- the order, on Q4 -------------------------------------------------
    note("G-ORDER -- on %s (core volume-averaged T), band %s" %
         (ORDER_QUANTITY, ORDER_BAND))
    note("  The band is [0.5, 1.5] and NOT [1.5, 2.5] because the formal order "
         "of the\n  energy convection term is ONE: T23G_F/system/fluid/"
         "fvSchemes line 33,\n  `div(phi,h) bounded Gauss upwind`.  Sanaa's "
         "section 0 point 3 is scheme-relative.\n")

    rows = {}
    for qn in ("Q4", "Q1", "Q2", "Q3", "Q6"):
        levels = [dict(name=lv, cells=CELLS[lv], value=q[lv][qn] - T_REF)
                  for lv in LEVELS]
        pc = controls[(qn, LEVELS[-1])]      # REPAIR R5: built and asserted above
        row = RT.grade_ladder(qn, levels, DIM, BAND_Q1, pc,
                              iterative_states=it_states,
                              plateau_states=pl_states[qn])
        rows[qn] = row
        note(RT.format_row(row))
        _apply_band_registration(row)

    # Q5 -- REPORTED, NEVER GATED (section 5.2; P4 predicts it fails again)
    v5 = [q[lv]["Q5"] for lv in LEVELS]
    t5 = RT.triple_from_cells(v5[0], v5[1], v5[2],
                              CELLS[LEVELS[0]], CELLS[LEVELS[1]],
                              CELLS[LEVELS[2]], DIM)
    note("Q5 housing surface heat flux -- REPORTED, NEVER GATED")
    note("  values %s  state %s  order %s"
         % (v5, t5["state"], t5.get("order")))
    note("  A DIVERGENT or STAGNANT reading here is PRE-REGISTERED as the "
         "expected outcome (P4)\n  and is NOT a failure of this rung: the "
         "quantity is pinned by the imposed 305 W\n  source to ~4e-5 relative. "
         "A CONVERGING reading in [1.5, 2.5] would mean P4 LOST.\n")

    # ---- A2.1: the discriminating observation ----------------------------
    p4 = rows["Q4"]["orders"][-1]
    p1 = rows["Q1"]["orders"][-1]
    if p4 is not None and p1 is not None:
        spread = abs(p4 - p1)
        note("A2.1 -- THE DISCRIMINATING OBSERVATION, registered before the run")
        note("  p(Q4) = %.4f, p(Q1) = %.4f, spread = %.4f" % (p4, p1, spread))
        note("  H-MESH predicts spread < 0.05 with p in [0.7, 1.3]; "
             "H-IFACE predicts spread > 0.15\n  with p in [0.25, 0.65] and the "
             "housing quantity LOWER.  On T23G the spread was\n  0.0027, which "
             "is a point AGAINST H-IFACE recorded before this run.\n")

    ov = gate_order(rows)          # REPAIR R3 -- G-ORDER, folded into the rollup

    verdicts = [ms, cv, yv, pv, rv, ov] + [rows[q_]["verdict"] for q_ in rows]
    final = ("NOT A RESULT" if "NOT A RESULT" in verdicts else
             "GATE FAIL" if "GATE FAIL" in verdicts else "PASS")
    note("=" * 74)
    note("RUNG VERDICT: %s" % final)
    note("=" * 74)
    return RT.exit_code_for(final)


def _series_path(cd, qn):
    if qn in ("Q1",):
        return os.path.join(cd, "postProcessing", "housing", "housing_T", "0",
                            "fieldMinMax.dat")
    if qn in ("Q3",):
        return os.path.join(cd, "postProcessing", "core", "core_T", "0",
                            "fieldMinMax.dat")
    if qn == "Q4":
        return os.path.join(cd, "postProcessing", "core", "core_volavg_T", "0",
                            "volFieldValue.dat")
    if qn == "Q6":
        return os.path.join(cd, "postProcessing", "housing",
                            "housing_volavg_T", "0", "volFieldValue.dat")
    if qn == "Q2":
        return os.path.join(cd, "postProcessing", "housing", "housing_patch_T",
                            "0", "surfaceFieldValue.dat")
    if qn == "Q5":
        return os.path.join(cd, "postProcessing", "housing",
                            "housing_wall_heat", "0", "surfaceFieldValue.dat")
    refuse("no series path registered for %r" % qn)


# ==========================================================================
# --selftest -- NON-VACUITY OF THE PLANTED CONTROLS, DRIVEN RED-THEN-GREEN.
#
# VERIFICATION_CHARTER section 2ay.5 / section 28.8: a control that has never
# been shown to FIRE when broken is indistinguishable from one that cannot see a
# violation.  This harness drives, WITH NO RUN DATA and NO OpenFOAM, the plant
# machinery that every one of the registered 20 controls funnels through:
#   * the primary y+ LOG reader control (control 20) -- GREEN it sees the plant;
#     RED a blinded reader is refused; RED an all-zero log is refused (rule 3);
#     the BLIND-text and ABSENT (R6) cases are exercised on the parser.
#   * `_plant_u_file`, the ENGINE of the independent field reader (control 19) --
#     GREEN every vector is scaled; RED a body with no vector, and a file with no
#     header, are refused.
#   * `RT.external_plant_control` / `RT.assert_plant_control`, the assertion funnel
#     for all 18 quantity controls and both y+ controls -- GREEN a seen plant
#     passes; RED a blind (before == after) reader is refused.
#
# WHAT IT DOES NOT CLAIM: the per-format .dat parsing of the 18 quantity controls
# and the mesh-dependent field reader (control 19) READ REAL ARTIFACTS and are
# exercised AT GRADE TIME against the built L3 case (gate_yplus / R5), not here --
# this harness proves the assertion ENGINE they share is non-vacuous, and never
# reports a control it did not drive as passed.
# ==========================================================================
def selftest():
    import tempfile
    import shutil
    mod = sys.modules[__name__]
    note("=" * 74)
    note("T23G2R COMPARATOR --selftest : planted-control NON-VACUITY, RED/GREEN")
    note("  (no run data, no OpenFOAM; drives the shared plant/assert engine)")
    note("=" * 74 + "\n")
    green, red = [], []

    def expect_refusal(label, fn):
        try:
            fn()
        except RT.Refusal as e:
            red.append(label)
            note("  RED  %-46s REFUSED as required" % label)
            return
        refuse("SELFTEST FAILED: RED limb %r did NOT fire -- the control is "
               "vacuous, it would pass a broken reader" % label)

    def green_ok(label, ok):
        if not ok:
            refuse("SELFTEST FAILED: GREEN limb %r did not pass -- the control "
                   "cannot see a plant it must see" % label)
        green.append(label)
        note("  GREEN %-46s PASSED" % label)

    tmp = tempfile.mkdtemp(prefix="t23g2r_selftest_")
    try:
        cd = os.path.join(tmp, "T23G2R_L3")
        os.makedirs(cd)
        logp = os.path.join(cd, "log.yPlus.fluid")
        good_log = (
            "patch centrebody_up y+ : min = 0.4700, max = 0.8540, average = 0.6300\n"
            "patch fluid_to_housing y+ : min = 0.1500, max = 0.3500, average = 0.2500\n")

        # ---- LIMB A: the primary y+ LOG reader control (control 20) ----
        open(logp, "w").write(good_log)
        base_log = yplus_from_log(cd)
        green_ok("log reader: parses a real log to a dict",
                 isinstance(base_log, dict) and "centrebody_up" in base_log)
        cl = control_yplus_log_reader(cd, base_log)
        RT.assert_plant_control(cl)           # refuses if it did not see the plant
        green_ok("log reader control [20]: sees planted %g" % PLANT,
                 cl is not None and cl["passed"])

        # RED: a BLINDED reader that ignores the planted copy and echoes the base.
        real = yplus_from_log
        def blind(_cd, path=None):
            return base_log                   # ignores `path`, never sees a plant
        try:
            setattr(mod, "yplus_from_log", blind)
            expect_refusal("log reader control [20]: blinded reader",
                           lambda: RT.assert_plant_control(
                               control_yplus_log_reader(cd, base_log)))
        finally:
            setattr(mod, "yplus_from_log", real)

        # RED: an all-zero log is a planted-zero and is refused (rule 3).
        open(logp, "w").write(
            "patch centrebody_up y+ : min = 0.0, max = 0.0, average = 0.0\n"
            "patch fluid_to_housing y+ : min = 0.0, max = 0.0, average = 0.0\n")
        expect_refusal("log reader: perfect-zero log (rule 3)",
                       lambda: yplus_from_log(cd))

        # BLIND text and ABSENT (R6) : parser classification, not a refusal here.
        open(logp, "w").write("Unable to find turbulence model in the database\n")
        green_ok("log reader: BLIND log classified as BLIND",
                 yplus_from_log(cd) == "BLIND")
        os.remove(logp)
        green_ok("log reader: ABSENT log -> None (gate_yplus REFUSES on it, R6)",
                 yplus_from_log(cd) is None)

        # ---- LIMB B: _plant_u_file, engine of the field reader (control 19) ----
        up = os.path.join(cd, "U_fixture")
        open(up, "w").write(
            "FoamFile { }\n// * * * * * * //\n"
            "internalField nonuniform List<vector>\n3\n(\n"
            "(1.0 2.0 3.0)\n(-4.0 5.0 -6.0)\n(0.5 0.25 0.125)\n)\n;\n")
        dst = up + ".plant"
        n = _plant_u_file(up, dst, YPLUS_PLANT_SCALE)
        planted_txt = open(dst).read()
        os.remove(dst)
        vecs = re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)",
                          planted_txt)
        orig = [(1.0, 2.0, 3.0), (-4.0, 5.0, -6.0), (0.5, 0.25, 0.125)]
        scaled_ok = (n == 3 and len(vecs) == 3 and all(
            abs(float(vecs[i][k]) - orig[i][k] * YPLUS_PLANT_SCALE)
            <= 1e-12 * max(1.0, abs(orig[i][k])) for i in range(3) for k in range(3)))
        green_ok("field-reader engine _plant_u_file: every vector scaled", scaled_ok)

        nover = os.path.join(cd, "U_novec")
        open(nover, "w").write("FoamFile { }\n// * * * //\ninternalField uniform 0;\n")
        expect_refusal("field-reader engine: body with no vector",
                       lambda: _plant_u_file(nover, nover + ".p", YPLUS_PLANT_SCALE))
        nohdr = os.path.join(cd, "U_nohdr")
        open(nohdr, "w").write("(1.0 2.0 3.0)\n")
        expect_refusal("field-reader engine: file with no header",
                       lambda: _plant_u_file(nohdr, nohdr + ".p", YPLUS_PLANT_SCALE))

        # ---- LIMB C: the RT assertion funnel shared by ALL 20 controls ----
        seen = RT.external_plant_control("seen", 1.0, 1.0 + PLANT)
        green_ok("RT plant funnel: a seen plant passes", seen["passed"])
        expect_refusal("RT plant funnel: a blind reader (before == after)",
                       lambda: RT.assert_plant_control(
                           RT.external_plant_control("blind", 1.0, 1.0)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    note("")
    note("  GREEN limbs passed : %d" % len(green))
    note("  RED   limbs fired  : %d" % len(red))
    note("  SELFTEST OK -- the planted-control engine sees plants and refuses "
         "blind readers.")
    note("  (Per-format .dat quantity controls [18] and the mesh-bound field "
         "reader [19]\n   read REAL artifacts and are driven AT GRADE TIME; this "
         "harness proves the\n   assertion engine they share is non-vacuous.)")
    return 0


if __name__ == "__main__":
    # A REFUSAL EXITS 2, UNAMBIGUOUSLY, AND NEVER AS A TRACEBACK.
    # T23G's record had to read its verdict off stdout because exit 1 was
    # ambiguous by design there.  A refusal that arrives as an uncaught
    # exception is worse still: it is indistinguishable from the comparator
    # itself being broken.  Here 0 = PASS, 1 = a graded non-PASS, 2 = REFUSED.
    try:
        sys.exit(main(sys.argv[1:]))
    except RT.Refusal as e:
        print("\nREFUSED (exit 2): %s" % e)
        sys.exit(2)


# ==========================================================================
# AMENDMENT RECORD -- v1.0 -> v1.1, 2026-09-02.
#
# FOUR SECTION 2d.1 POST-COMPUTE GRADING-PATH REPAIRS, EACH GRANTED SEPARATELY BY
# verification-supervisor AT VERIFICATION_CHARTER.md v1.38 SECTIONS 2d.5-2d.8,
# COMMIT 3dad5bae, ON heat-transfer's PETITION AT
# docs/campaigns/T-family/T23G2_GRADING_PATH_REPAIR_PETITION.md.
#
#   R2  GRANTED AND WIDENED -- grading-path sha recorder, FIVE files not four,
#       with the section 2d.4.3 dual-sha condition.
#   R3  GRANTED -- G-ORDER made reachable and folded into the rollup.
#   R4  BAND LIMB GRANTED AND WIDENED to Q4 as well as Q6.  ITS ROLLUP-EXCLUSION
#       LIMB WAS REFUSED (section 2d.7) AND IS NOT IMPLEMENTED.
#   R5  GRANTED -- 18 quantity controls in place of 5, both y+ reader controls,
#       and the exact-zero G-RATIO licence made executable.
#   R1  GRANTED -- and it lives in mark_done_t23.py, not here.
#   R6  LIVE IN THIS SUCCESSOR (T23G2R).  On T23G2 it was REFUSED as a section
#       2d.1 repair and REFERRED for PROSPECTIVE registration in the next rung;
#       T23G2R IS that next rung (section 5.2).  gate_yplus's ABSENT branch now
#       REFUSES instead of falling through to the independent reader alone.  It
#       is strictly stricter: it can only ADD a refusal.  BLIND is untouched.
#
# T23G2R-SPECIFIC CHANGES vs analyse_t23g2.py, and NOTHING ELSE:
#   * run target / level names / endTimes point at T23G2R (RUNS, LEVELS,
#     ENDTIME); CELLS are UNCHANGED (the fix reduces first-cell height only).
#   * the prospective R6 refusal above.
#   * verify_self() -- while unpinned it REFUSES (DRAFT guard, rule 2); once
#     pinned the SELF member is PRINT-ONLY provenance (section 2au.2), because a
#     self-referential IDENTICAL assertion against its own freeze commit is a git
#     pre-image; the freeze is anchored by the commit-message FREEZE-PIN and the
#     grade-time byte-identity check.  Called first in main().  --selftest drives
#     the planted controls RED/GREEN without run data.
#   * EVERY gate, threshold and band is REUSED VERBATIM.  ORDER_BAND, BAND_Q1,
#     RESID_TOL, YPLUS_MAX, RATIO_MIN, MESHSIM_* and the R2-R5/R7 logic are
#     byte-for-intent the frozen T23G2 values; not one is relaxed.
#
# RULE 6, STATED HONESTLY RATHER THAN ASSERTED FALSELY.  Rule 6 requires the
# assertion "lines whose number changed above this section: 0".  THAT ASSERTION
# IS NOT MADE HERE AND CANNOT BE: every one of these repairs inserts EXECUTABLE
# lines into the body of the file, so line numbers below each insertion move.
# The frozen file was 653 lines; this one is longer, and citations into the
# frozen text -- the ruling's own :46, :455, :504-524, :579, :581, :612 -- resolve
# against the blob cc723d6f65245674f7d80c51de55fe986549477a at 976776f4, NOT
# against this file.  THE FROZEN BLOB IS THE ONE TO CITE.
#
# The form used instead is the T-family's OWN precedent for a section 2d.1 code
# repair: a dated in-file AMENDMENT block at each change site plus a version
# bump, as analyse_t23g.py carries at its :248 and :826 and as its own sha
# recorder was added under DEAD_LEVER_AUDIT sections 27.3-27.4.  Rule 6's
# "appended at the foot, lines above unchanged" is satisfiable by a frozen
# RECORD and is not satisfiable by a frozen EXECUTABLE that must gain executable
# lines -- section 2d.1's founding case was itself a mid-file code change, K0cS's
# wall_nu from an arithmetic to an area-weighted mean.  THE TENSION IS ESCALATED
# TO heat-transfer-supervisor RATHER THAN RESOLVED BY THE LANE, and the lane
# states plainly that it did not assert an invariant it could not verify.
#
# NOTHING WAS GRADED AND NOTHING WAS LAUNCHED BY THE LANE THAT MADE THESE EDITS.
# Every gate, threshold, band, cap and label is untouched: created 0, moved 0,
# retired 0.  T23G2_PREREGISTRATION.md was NOT edited.  No file was moved
# (section 2d.4.2 forbids relocating this comparator while T23G2 is ungraded).
# ==========================================================================
#
# ==========================================================================
# AMENDMENT RECORD -- v1.1 -> v1.2, 2026-09-02.  REPAIR R7, AND ONE OF IT.
#
# GRANTED at VERIFICATION_CHARTER.md v1.41 section 2d.9.1, commit 79bcfd83, on
# heat-transfer's petition at
# docs/campaigns/T-family/T23G2_R7_ORDER_GATE_PETITION.md.
#
#   R7  GRANTED ON ALL FOUR CONDITIONS -- gate_order now applies rule 5 step (a)
#       BEFORE it gates an order.  Where any level is not iteratively converged
#       or not plateaued the grid claim is already void and the gate returns
#       NOT A RESULT instead of PASS or GATE FAIL.  The whole change is in
#       gate_order and in nothing else.
#
# THE ONE THING THIS REPAIR DOES NOT DO, STATED FIRST BECAUSE IT IS THE THING
# MOST EASILY MISREAD.  ORDER_BAND = (0.5, 1.5) at :65 and ORDER_QUANTITY =
# "Q4" at :66 are BYTE-UNCHANGED, and both are frozen pre-compute at
# T23G2_PREREGISTRATION.md:833-834.  The gate is not retired.  Only the
# PRECONDITION for evaluability moved.  Gates, thresholds, bands, caps and
# labels created, moved or retired: 0 - 0 - 0 - 0 - 0.
#
# CONDITION (2)'s INSTRUMENT, AND IT IS NOT ONE WE BUILT.  The departure was
# exhibited against CLAUDE.md standing rule 5.  Section 2d.9.1 EXTENDED
# section 2d.5 a fortiori to reach it: a standing rule is lab-constitutional,
# predates every rung, grades nothing, and cannot know which direction a verdict
# wants, so it satisfies condition (2) on the same ground as a frozen
# registration and with more force.  THAT EXTENSION IS verification's RULING AND
# NOT THIS LANE's READING -- the petition at section 5 said plainly that the
# question was not ours to answer, and it was answered against our own interest
# in the sense that it turned one of our own PASSes into a NOT A RESULT.
#
# CONDITIONS (3) AND (4), DISCHARGED AT ZERO AND MEASURED:
#   * pre-repair cell   G-ORDER: PASS
#   * post-repair cell  G-ORDER: NOT A RESULT
#   * RUNG VERDICT      NOT A RESULT, UNCHANGED, exit code 3 in both captures.
#     The rollup already carried NOT A RESULT on three independent grounds
#     established before any repair existed.  R7 MOVES A CELL, NOT THE RUNG.
#   * p(Q4) = 0.6111 and the band [0.5, 1.5] are printed in BOTH captures.
#     NO VALUE MOVED.
#   The two captures are labelled, sha256'd and diffed at
#   verification/runs/T-family/T23G2_runs/T23G2_GRADE_CAPTURES.md, beside
#   T23G2_GRADE.out (pre-repair, NOT edited by this repair) and
#   T23G2_GRADE_POST_R7.out (post-repair).
#
# THE GATE WAS SHOWN ABLE TO SAY SOMETHING ELSE, WHICH IS RULE 3's PRINCIPLE
# APPLIED TO A VERDICT.  A NOT A RESULT from a gate never shown able to emit a
# PASS is indistinguishable from a gate hard-wired to refuse.
# r7_gate_control_t23g2.py drives THIS function -- the production one, not a
# copy of it (section 2p.7 limb (d)) -- over five inputs and requires five
# different answers; 5/5 passed.  Control 2 plants all-CONVERGED and gets PASS
# back.  Control 3 plants an order of 2.9000 and gets GATE FAIL back, which is
# what shows the registered band is still live and still discriminating.
#
# RULE 6, STATED HONESTLY RATHER THAN ASSERTED FALSELY -- THE SAME POSITION THE
# v1.1 BLOCK ABOVE TOOK, AND FOR THE SAME REASON.  The assertion "lines whose
# number changed above this section: 0" IS NOT MADE HERE AND CANNOT BE: R7
# inserts executable lines into gate_order at :903, so every line number below
# that point moved.  WHAT IS MEASURED INSTEAD, AND IT IS MEASURED AND NOT
# ESTIMATED:
#   * THE EXECUTABLE REPAIR, measured against the blob that produced
#     T23G2_GRADE.out (fa4e802f9e0eab63e8d4902e1d74e99f11748a8f): 68 lines
#     inserted, 1 line deleted, ALL OF THEM INSIDE gate_order.  THE ONE
#     DELETION IS THE `if` OF `if p is None or state != "CONVERGING":`
#     BECOMING AN `elif`, because rule 5 step (a) now stands in front of it.
#     No other line was removed anywhere in the file.
#   * against the FROZEN blob cc723d6f65245674f7d80c51de55fe986549477a at
#     976776f4, at that same point: 603 inserted, 20 deleted; frozen file 653
#     lines.
#   * THIS AMENDMENT BLOCK ITSELF is a pure comment append BELOW the
#     `if __name__ == "__main__"` guard.  It adds NO executable line and moves
#     NO executable line: every line above it keeps its number.
# THIS FILE DELIBERATELY DOES NOT RECORD ITS OWN POST-REPAIR BLOB SHA, BECAUSE
# WRITING THAT SHA INTO THE FILE CHANGES IT.  The blob is recorded OUTSIDE, at
# verification/runs/T-family/T23G2_runs/T23G2_GRADE_CAPTURES.md, beside the
# capture it produced -- and the comparator prints it on the artifact's face at
# every run through the R2 recorder, which is the check that cannot go stale.
# CITATIONS INTO THE FROZEN TEXT RESOLVE AGAINST THE FROZEN BLOB AND NOT AGAINST
# THIS FILE.  THE FROZEN BLOB IS THE ONE TO CITE.
#
# THE COMPARATOR DID NOT MOVE, AND NOW NEVER WILL.  Section 2d.9.2 closed the
# relocation PERMANENTLY, not conditionally: moving this file post-compute would
# not make T23G2_PREREGISTRATION.md section 7 true, it would make the RECORD
# false, converting a disclosed discrepancy into a concealed one.  The repair
# section 2d.1 licenses runs the other way -- a dated addendum correcting
# section 7's PATH TEXT, which is where the demonstrable error is.  You repair
# the record to match reality, never reality to match the record.
#
# NOTHING WAS GRADED AND NOTHING WAS LAUNCHED BY THE LANE THAT MADE THIS EDIT.
# The comparator was re-run three times over artifacts already on disk: 0
# core-min, $0.00.  T23G2_GRADE.out WAS NOT EDITED -- its sha256 is still
# 40f2fa33f4818cad7834e86257cd9dac8c6b786f24662c87bb0ffe2927261d2b, the value
# the petition recorded before this repair existed.
# ==========================================================================
#
# ==========================================================================
# AMENDMENT RECORD -- v1.2 -> v1.3, 2026-09-02.  REPAIR R8, AND ONE OF IT.
#
# THE LAW IS STATED AT VERIFICATION_CHARTER.md v1.42 SECTIONS 2d.10 AND 2p.8,
# COMMIT c4007e42.  THE CHANGE IS THIS TEAM'S.  No repair was ordered and none
# was petitioned: heat-transfer's section 6 asked whether G-RATIO shared R7's
# defect and expressly requested no repair.  The ruling states the law and says
# so in terms -- "whether and when analyse_t23g2.py is changed is
# heat-transfer's, subject to section 2d.1 and to section 2d.4.1's full-force
# (3) and (4)".  R8 IS NOT A COMPLIED-WITH ORDER, and the record should not later
# be read as though it were.  The ruling was read AT SOURCE, as a commit, before
# this repair was made, and not as a relay of it.
#
# WHAT WAS WRONG, ON TWO INDEPENDENT GROUNDS, EITHER SUFFICIENT.
#
#   GROUND 1, section 2d.10, the LICENSING-GATE clause, ruled generally: "a gate
#   whose purpose is to LICENSE another quantity must return NOT A RESULT
#   whenever that quantity is itself NOT A RESULT.  A licence issued for a voided
#   claim is not a verdict -- it is a CATEGORY ERROR, an assurance about an
#   object that does not exist."  g_ratio's own stated purpose, in its opening
#   docstring, is "otherwise the observed order is noise, not discretisation":
#   IT EXISTS TO LICENSE THE OBSERVED ORDER.  Rule 5 step (a) had already voided
#   that order -- T23G2_L2 is NOT CONVERGED and grade_ladder says so once per
#   graded quantity in the same output -- so there was no order for G-RATIO to
#   license, and it returned PASS on all six quantities anyway.
#
#   GROUND 2, THE ONE THE PETITION DID NOT RAISE AND THE RULING ADDED: with
#   iter_change exactly 0.0 the zero-branch returned infinity REGARDLESS OF THE
#   NUMERATOR ENTIRELY.  The PASS was attributable to the denominator being zero
#   and to NO PROPERTY OF THE LADDER; it would have returned PASS for any
#   numerator, contaminated or pristine.  That is section 2p in its own right: A
#   PASS FROM A DEGENERATE PATH.  The petition asked whether the numerator was
#   contaminated; the sharper answer is that on this data the numerator was never
#   consulted.
#
#   AND THE RULING'S OWN QUALIFICATION, WHICH IS NOT UPGRADED HERE: the ratio is
#   UNINTERPRETABLE, NOT MEANINGLESS.  A large value could mean grid differences
#   dominate iterative error, or that a level's iterative error inflated the
#   inter-level differences, and the instrument cannot distinguish them.
#
# WHAT THE CODE NOW DOES.  g_ratio takes the same two dicts rule 5 step (a) reads
# -- iterative_convergence and plateau -- and applies the SAME TWO TESTS that
# roache_triple.grade_ladder applies at :605-618, exactly as R7 taught gate_order
# to do.  Both grounds are evaluated SEPARATELY and BOTH are reported when both
# hold, because "either alone is sufficient" is only checkable if the instrument
# does not collapse them into one refusal.  No new criterion, no new threshold,
# no new state name, no reimplementation.  R5's planted-zero refusal is left
# exactly where R5 put it, IN FRONT of both limbs and not weakened: an exact zero
# with no control still REFUSES (exit 2) rather than being downgraded to a NOT A
# RESULT by a limb that would have voided the cell anyway.
#
# THE ROLLUP WAS ALSO WRONG AND IS FIXED WITH IT.  The G-RATIO summary read
# `if rst != "PASS": rv = "GATE FAIL"`, which would have relabelled a NOT A
# RESULT cell as GATE FAIL -- a verdict-vocabulary error under CLAUDE.md rule 1
# and a move in the direction rule 5 forbids.  NOT A RESULT now dominates.
#
# UNTOUCHED: RATIO_MIN = 10.0 at :106 and G-RATIO's registered meaning at
# T23G2_PREREGISTRATION.md section 5.3.  Gates, thresholds, bands, caps and
# labels created, moved or retired: 0 - 0 - 0 - 0 - 0.  Only the precondition for
# interpretability moved.  DIRECTION: STRICTLY RESTRICTIVE -- PASS or GATE FAIL
# into NOT A RESULT, never the reverse.
#
# A REGISTERED MUTATION WAS PROTECTED RATHER THAN SILENTLY RETIRED.  The
# registered mutation D5 (T23G2_MUTATION_SET_REGISTERED.md:61) patches the
# `control=` argument together with the call's closing paren as ONE literal and
# asserts it occurs exactly once.  R8's call site therefore keeps `control=` LAST
# and does not quote that literal anywhere else in this file.  A repair that
# reformats a call site can retire a registered mutation without anyone noticing,
# and that was checked rather than assumed.
#
# CONDITIONS (3) AND (4), DISCHARGED AND MEASURED.  Pre-repair cell G-RATIO:
# PASS, on all six quantities.  Post-repair cell G-RATIO: NOT A RESULT, on all
# six.  RUNG VERDICT: NOT A RESULT, UNCHANGED, exit code 3 in both captures.
# R8 MOVES A CELL, NOT THE RUNG.  NO NUMBER MOVED: the finest iterative change is
# 0.000000e+00 in both captures on all six quantities, the six smallest
# inter-level differences are identical in both, the printed ratio is inf in
# both, and `needs >= 10` is printed in both.
#
# THE REPRODUCTION CONTROL RAN FIRST AND IT DID NOT REPRODUCE, WHICH IS RECORDED
# RATHER THAN WORKED AROUND.  Re-running the UNREPAIRED comparator no longer
# reproduces T23G2_GRADE_POST_R7.out byte-identically: the R2 recorder's line for
# T23G2_PREREGISTRATION.md moved b2721aaa -> 0b597ba9 because commit b1d9070c
# landed ADDENDUM A3 -- the section 2d.4.2/2d.9.2 record repair -- after R7's
# capture was taken.  112 lines inserted, 0 deleted, gates 0.  It is a peer's
# committed, licensed work and it was INSPECTED, NOT REVERTED (rule 10).  A fresh
# pre-repair baseline was therefore taken from today's tree with the unrepaired
# code, and it differs from R7's capture in that ONE hunk and nothing else.
#
# THE GATE WAS SHOWN ABLE TO SAY SOMETHING ELSE -- section 2p.3(e), which the
# ruling made lab law in the same commit.  r8_gate_control_t23g2.py drives the
# PRODUCTION g_ratio BY IMPORT, not a copy (section 2p.7 limb (d)), prints the
# resolved file path and its sha256 so limb (d) need not be taken on trust, and
# runs nine controls: 9/9.  Control 2 plants an all-CONVERGED ladder with a real
# non-zero iterative change and gets PASS back; control 3 plants the SAME
# numerator with a ratio below RATIO_MIN and gets GATE FAIL back, which is what
# shows the registered threshold is still live and still discriminating.
#
# AND THE CONTROL WAS SHOWN ABLE TO FAIL.  r8_mutation_demo_t23g2.py mutates the
# lines R8 actually shipped and requires the suite to go red: 6 of 6 killed, with
# an unmutated NEGATIVE ARM run through the same machinery required to come back
# green.  THE FIRST RUN WAS 5 OF 6.  Removing g_ratio's own planted-zero refusal
# left the suite green, because roache_triple.assert_plant_control refuses on the
# same input one line later and a verdict-level control cannot tell the two
# apart.  Control 9 was added to require the refusal to come from g_ratio's OWN
# line, and the demonstration then killed 6 of 6.  BOTH ROUNDS ARE PUBLISHED.
#
# RULE 6, MEASURED AND NOT ASSERTED.  "Lines whose number changed above this
# section: 0" IS NOT CLAIMED and CANNOT BE: R8 inserts executable lines into
# g_ratio and into main, so line numbers below each insertion move.  MEASURED
# instead, against the blob that produced the pre-repair capture,
# d2187518bc3b257d6305db7ac4a4f3c06b746f39, and split into its two parts because
# they are two different kinds of change:
#
#   THE EXECUTABLE REPAIR: 130 lines inserted, 7 deleted, ALL INSIDE g_ratio and
#   its single call site in main -- diff -U0 reports hunks at :278, :292, :297,
#   :304, :1076, :1091, :1094 and :1098 and nowhere else.  The seven deletions
#   are the old def line, the old exact-zero `return "PASS"`, the two old tail
#   lines of the finite branch, the two old call lines and the old
#   `if rst != "PASS":` rollup line.
#
#   ⚠ THE COUNT WAS WRONG ON THE FIRST MEASUREMENT AND THE METHOD IS NAMED SO
#   NOBODY REPEATS IT.  Counting with `diff -u | grep -c '^+[^+]'` returned 118
#   where the true figure is 130: THE PATTERN SILENTLY SKIPS EVERY INSERTED BLANK
#   LINE, which appears in the diff as a bare `+`.  The figures here are
#   difflib's, and they CLOSE ARITHMETICALLY against the two file lengths, which
#   the grep figures do not.  A COUNT THAT DOES NOT CLOSE AGAINST THE FILE LENGTH
#   IS NOT A MEASUREMENT.  This matters beyond R8: the same grep idiom is the one
#   R7's record used, so R7's stated counts are LIKELY LOW BY THE SAME MECHANISM.
#   That is REPORTED, NOT SILENTLY CORRECTED -- R7's record is not this repair's
#   to edit.
#
#   THIS AMENDMENT RECORD: a PURE COMMENT APPEND BELOW the
#   `if __name__ == "__main__"` guard, 0 deletions.  It adds no executable line
#   and moves none: the guard sat at line 1179 before R8 and sits at line 1302
#   after it, moved by the 123 net executable lines above it and by nothing else.
#
#   ITS OWN LINE COUNT, AND THE TOTALS THAT INCLUDE IT, ARE RECORDED OUTSIDE
#   THIS FILE -- in verification/runs/T-family/T23G2_runs/T23G2_GRADE_CAPTURES.md
#   -- FOR THE SAME REASON THE POST-REPAIR SHA IS: a figure that counts the lines
#   of the paragraph stating it cannot be written into that paragraph without
#   falsifying itself.  R7 handled its own sha this way and R8 follows it.  The
#   frozen file is 653 lines; CITATIONS INTO THE FROZEN TEXT RESOLVE AGAINST THE
#   FROZEN BLOB cc723d6f65245674f7d80c51de55fe986549477a AND NOT AGAINST THIS
#   FILE.
#
# THIS FILE DELIBERATELY DOES NOT RECORD ITS OWN POST-R8 SHA, because writing
# that sha into the file changes it.  It is recorded OUTSIDE, in
# verification/runs/T-family/T23G2_runs/T23G2_GRADE_CAPTURES.md, and the R2
# recorder prints it on the artifact's face at every run.
#
# THE COMPARATOR DID NOT MOVE.  Section 2d.9.2 closed the relocation permanently
# and R8 does not reopen it.
#
# NOTHING WAS GRADED AND NOTHING WAS LAUNCHED BY THE LANE THAT MADE THIS EDIT.
# Every invocation was a read of artifacts already on disk: 0 core-min, $0.00,
# cost_basis = NOT APPLICABLE, no solver compute.  T23G2_GRADE.out and
# T23G2_GRADE_POST_R7.out WERE NOT EDITED -- sha256 still
# 40f2fa33f4818cad7834e86257cd9dac8c6b786f24662c87bb0ffe2927261d2b and
# dc79492b765a5c7a473119a47ec1364303a7cce420ff42098e6a395adfecc99a.
# ==========================================================================
