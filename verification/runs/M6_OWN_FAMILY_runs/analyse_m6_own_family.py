#!/usr/bin/env python3
"""M6 OWN-MESH FAMILY comparator -- the own-family {L2, L1, L0} grading harness for
verification/campaign/M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md (FROZEN 2026-09-08).

WHY THIS FILE EXISTS.  The frozen prereg's grading path is pinned to cases/M6SR/analyse_m6sr.py
(git blob 8007b23da5bb3173dacb6eda1d67ca5d90ce9139), whose §12.3 "HONEST NOTE ON COMPARATOR
APPLICABILITY" records, in terms, that that module's MEASUREMENT FUNCTIONS are the pinned,
check-1'd instrument BUT its LEVEL-DISCOVERY / REGISTRATION LAYER is M6SR-specific -- main()
and _discover_levels() hardwire the level ids L3/L2/L1, the M6SR mesh paths, the M6SR cell
triple A4_CELLS = (99840, 399360, 1597440), the endTimes (3000, 4000, 5000), and the M6SR
createPatchDict / patch-name set {wing, inout, sym}.  It therefore CANNOT grade this own-mesh
fine triple as invoked.  §12.3 rules that an own-family grading harness "must be authored and
pass the cfd-supervisor's check-1 before any grade, and will be pinned by a dated FREEZE
ADDENDUM that re-pins the grading-path blob and alters no gate/threshold/band/cap/label (the
T23G2R re-pin precedent)."  THIS FILE IS THAT HARNESS.  It is a DRAFT for the cfd-supervisor's
check-1 (MEASUREMENT LOGIC) and check-4; nothing is wired live and nothing is graded until then.

THE MEASUREMENT CORE IS REUSED VERBATIM, NOT REIMPLEMENTED.  This module IMPORTS
cases/M6SR/analyse_m6sr.py (referred to as `A`) and calls its PINNED functions UNCHANGED --
byte-for-byte the blob 8007b23d.  The Cp comparison and the Roache/GCI math are NOT rewritten:

    A.read_case_2308        the 271 AR-138 taps, REFUSING on a sha256 mismatch (§4.1)
    A.d1_discriminator      the A-MAP Cn-monotonicity discriminator (§4.3)
    A.cfd_sections_for_case the CFD Cp producer at the seven registered stations (§8.5)
    A.gate_p_figure_data    Gate P's per-station figure data
    A.set_to_set_assignment §4.5's order-independent channel (called inside A.gate_p)
    A.gate_p                Gate P itself -- surface Cp vs the taps, ΔCp=±0.02, x/c<=0.90
    A.roache_triple         THE GCI MATH -- classification + observed order p + GCI at Fs=1.25
    A.gci_fine_from_gate_g  the band Gate P's numerical channel consumes (r-invariant)
    A.cd_series / A.residual_series / A.gate_g2   the iterative-convergence machinery (G1/G2)
    A.completion_clauses    rule-4 strict completion + the age guard (§8.6)
    A.controls / A.control_c16 / A.d1_branch_reachability   the planted controls (rule 3)
    A.read_checkmesh / A.points_stream_sha / A.read_boundary   the mesh readers (L-459)
    A.section7_condition_1 / A.section7_conditions_2_3_4   the ill-posedness screen predicates
    A._verdict / A.Refusal / A.InternalDefect / A.Unregistered / A._emit / A._write

THE DIFF vs analyse_m6sr.py IS THE OWN-FAMILY ADAPTATION LAYER, AND ONLY THAT:
  * level ids L2/L1/L0 (NOT M6SR's L3/L2/L1), coarse-to-fine
  * own-family run roots verification/runs/M6_OWN_FAMILY_runs/L{2,1,0}/solve
  * own-family cell counts (71760 / 574080 / 4592640), cell ratio 8.00 (NOT 4.00)
  * own-family endTimes (draft; §7.2's 6000-iteration cost basis -- supervisor confirms)
  * own-family createPatchDict / patch-name set {wing, symmetry, farfield}
    (NOT M6SR's {wing, inout, sym})
  * the Gate-G FRAMING: this triple refines ALL THREE directions (surface x4 = 2^2 AND
    wall-normal layers x2 = 2^1 per level), so its Roache ratio r = 2.000 is the GENUINE
    ISOTROPIC 3-D refinement ratio and A.roache_triple yields a CREDENTIAL-GRADE OBSERVED
    ORDER of accuracy.  M6SR's clause L-HONEST -- "SURFACE-refinement band ... LOWER BOUND ...
    NOT an observed order" -- describes a family that holds the wall-normal direction fixed
    (M6SR A6: 64 cells per wing face at every level).  THAT FRAMING IS NOT CARRIED OVER; it is
    FALSE for this triple.  The MATH is A.roache_triple UNCHANGED; only the interpretation and
    the derived r differ, and both are DERIVED from the own-family registered counts below.

Nothing in A's measurement functions is altered, monkey-patched, or shadowed.  A's module
constants A.A4_CELLS, A.S7_EXPECTED_PATCH_NAMES etc. remain M6SR's; this module never mutates
them -- it supplies its OWN counts and names as parameters / local constants.

EXIT VOCABULARY (identical to A, §9.2):
    0   graded; the verdicts are in the output (a verdict may itself be GATE FAIL / NOT A
        RESULT -- rc 0 means the INSTRUMENT ran, never that a gate passed).
    2   REFUSAL.  A control did not fire, a pinned hash moved, a completion clause failed, or
        a parameter this comparator needs is not registered.  REFUSE RATHER THAN DEGRADE.
    11  a Section-7 launch-path level is BLOCKED (a statement about the MESH, not the document).
    70  INTERNAL DEFECT of this comparator.  Never a finding about the M6.

NO BARE `assert` (§9.2, L-475): every guard is an explicit raise.
NOTHING UNDER /home/ubuntu/certonomous-runs/ IS WRITTEN.  Inputs there are read only.
SUBMISSIONS ARE PARKED (rule 7): this file sends nothing anywhere.
"""

import math
import os
import sys
import tempfile

# --------------------------------------------------------------------------------------
# IMPORT THE PINNED INSTRUMENT.  A.REPO derives from A.__file__, so importing does not
# perturb A's own path logic.  The blob this file was authored against is pinned below and
# re-verified at run time by the solve driver (run_m6_own_family_triple.sh) before any grade.
# --------------------------------------------------------------------------------------
_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_THIS))))
_M6SR_DIR = os.path.join(REPO, "cases", "M6SR")
if _M6SR_DIR not in sys.path:
    sys.path.insert(0, _M6SR_DIR)
import analyse_m6sr as A   # noqa: E402  -- the pinned, check-1'd measurement core

# The prereg §12.3 pins the measurement core by this git blob.  Recorded here so a reader can
# see WHICH analyse_m6sr.py this harness was authored against; the driver re-hashes both this
# file and analyse_m6sr.py against their committed blobs before spending a core-minute (rule 2).
PINNED_M6SR_BLOB = "8007b23da5bb3173dacb6eda1d67ca5d90ce9139"

# --------------------------------------------------------------------------------------
# OWN-FAMILY REGISTERED COUNTS.  Every figure is transcribed from the FROZEN prereg §1/§3/§4.
# Nothing is chosen here; the refinement ratio is DERIVED from these, not stored (see below).
# --------------------------------------------------------------------------------------
OWN_LEVEL_IDS = ("L2", "L1", "L0")                      # coarse -> fine (prereg §1)
OWN_CELLS = (71760, 574080, 4592640)                    # prereg §1/§4 -- ratio 8.00, 8.00
OWN_SURFACE_FACES = (1560, 6240, 24960)                 # prereg §1 -- ratio 4.00 (2-D, x2^2)
OWN_MARCHED_LAYERS = (46, 92, 184)                      # prereg §1 (pyHyp N-1: 47/93/185) -- x2
OWN_CELL_RATIO_EXACT = 8                                # 8.00 = 2^3 (surface 2^2 * normal 2^1)
OWN_PATCH_NAMES = frozenset(("wing", "symmetry", "farfield"))   # prereg §3 (NOT M6SR's names)
OWN_CREATEPATCHDICT_SHA256 = \
    "3e235b4d1324f4eb3f3986dc6e136ca621e39feb6b091aa2c9bf23cc892b368f"  # DRAFT pin (§ check-1)

# ENDTIMES -- DRAFT.  The frozen prereg registers no explicit per-level endTime; §7.2 costs the
# triple at ~6,000 iterations PER LEVEL (uniform), and §7.3's x2 cap margin explicitly covers
# "a restart / extra-iteration allowance if L0 needs more than ~6,000 iterations to plateau".
# These endTimes are transcribed from that 6,000-iteration cost basis and are a DRAFT the
# cfd-supervisor confirms at check-4 (they become frozen via the FREEZE ADDENDUM, not here).
OWN_END_TIMES = (6000, 6000, 6000)                      # L2, L1, L0 -- §7.2 cost basis (DRAFT)

# The credential-grade note carried on every own-family Gate-G / Gate-P output, IN PLACE OF
# M6SR's clause L-HONEST.  It is the affirmative counterpart: this family DOES yield an
# observed order, because it refines all three directions.
OWN_FAMILY_ORDER_NOTE = (
    "This is a THREE-LEVEL, r=2, ISOTROPICALLY NESTED grid family: each level refines the "
    "surface by x4 (=2^2 in-plane) AND the wall-normal layer count by x2, so cells scale by "
    "2^3 = 8.00 per level. Its Roache ratio r = 2.000 is the GENUINE 3-D refinement ratio and "
    "the order it yields is a TRUE OBSERVED ORDER OF ACCURACY -- NOT a surface-refinement lower "
    "bound (M6SR's clause L-HONEST does not apply: that family holds the wall-normal direction "
    "fixed). The GCI at Fs=1.25 is the credential-grade family band Sanaa named as her "
    "deliverable, subject to Gate G classifying CONVERGING (rule 5)."
)

# The honest caveats that DO still apply to this family (M6SR NOT_CLAIMED, minus the
# 'no observed order' item, which this family exists to overturn).
OWN_NOT_CLAIMED = [
    "the observed order is credential-grade ONLY IF Gate G classifies CONVERGING; a "
    "non-CONVERGING triple is NOT A RESULT whatever the number says (rule 5)",
    "the uncorrected AR-138 wall interference (semispan/tunnel-width 0.7, AGARD declines to "
    "quantify) is DISCLOSED and deliberately NOT in the band (A.gate_p carries this verbatim)",
    "the sharp trailing edge vs AGARD's 0.14104%-chord design TE is why Gate P grades only "
    "x/c <= 0.90; the rear 10% is plotted and reported, NEVER graded (prereg §5)",
    "A-MAP (the section->y/b assignment) is ASSUMED, not measured; D1 adjudicates its "
    "ordering only (A.d1_discriminator / A.set_to_set_assignment)",
    "no measured y+; the freestream k/omega are registered, not a tunnel model",
    "SUBMISSIONS ARE PARKED -- nothing is sent, filed or registered outside this box (rule 7)",
]


# --------------------------------------------------------------------------------------
# THE REFINEMENT RATIO -- DERIVED FROM THE FROZEN OWN-FAMILY COUNTS, NOT STORED.
#
# This is the own-family counterpart of A.refinement_ratio_from_registered_counts().  The
# DIFFERENCE, and the whole reason M6SR's function cannot be reused verbatim:
#   * M6SR derives r = sqrt(surface-face ratio 4) = 2.000 and stops there, because A6 holds
#     the wall-normal layers FIXED -- a TWO-dimensional refinement, hence a lower bound.
#   * This family refines the wall-normal layers TOO (46 -> 92 -> 184, ratio 2), so the same
#     r = 2.000 acts in ALL THREE directions and the cell ratio is 8 = 2^3 rather than 4 = 2^2.
# r itself is 2.000 EXACTLY in BOTH: it is sqrt(4) either way. What changes is the DIMENSION
# of the refinement and therefore whether the resulting order is a lower bound or an observed
# order. Both facts are DERIVED here from the registered counts; if any count moved, this
# refuses (an InternalDefect) rather than take a root of an inexact ratio.
# --------------------------------------------------------------------------------------
def refinement_ratio_own_family():
    """-> (r, basis).  r DERIVED from the own-family surface-face, layer and cell counts."""
    f, lay, c = OWN_SURFACE_FACES, OWN_MARCHED_LAYERS, OWN_CELLS
    # (a) cells = surface_faces * marched_layers, EXACTLY, at every level.
    for i in range(3):
        if f[i] * lay[i] != c[i]:
            raise A.InternalDefect(
                f"own-family level {OWN_LEVEL_IDS[i]}: surface_faces {f[i]} * layers {lay[i]} "
                f"= {f[i]*lay[i]} != registered cells {c[i]}. The r derivation rests on this "
                "factorisation and this comparator will not proceed on an inexact one.")
    # (b) surface-face ratio EXACTLY 4 on integers (2-D, r^2).
    if not (f[1] == 4 * f[0] and f[2] == 4 * f[1]):
        raise A.InternalDefect(
            f"own-family surface-face counts {f} are not in the exact ratio 4 that prereg §1 "
            "registers; r = sqrt(ratio) will not be taken on an approximate ratio.")
    # (c) wall-normal layer ratio EXACTLY 2 on integers (1-D, r^1) -- the fact M6SR lacks.
    if not (lay[1] == 2 * lay[0] and lay[2] == 2 * lay[1]):
        raise A.InternalDefect(
            f"own-family marched-layer counts {lay} are not in the exact ratio 2 that prereg "
            "§1 registers; without it this refinement is not isotropic and r is not 3-D.")
    # (d) cell ratio EXACTLY 8 on integers (3-D, r^3) -- and it must equal (face ratio)*(layer
    #     ratio) = 4*2, closing the loop.
    if not (c[1] == OWN_CELL_RATIO_EXACT * c[0] and c[2] == OWN_CELL_RATIO_EXACT * c[1]):
        raise A.InternalDefect(
            f"own-family cell counts {c} are not in the exact ratio {OWN_CELL_RATIO_EXACT} "
            "that prereg §1/§4 registers.")
    r = math.sqrt(4.0)              # = 2.000 EXACTLY (sqrt of a perfect square), from (b)
    if float(lay[1]) / float(lay[0]) != r or float(lay[2]) / float(lay[1]) != r:
        raise A.InternalDefect(
            "the wall-normal layer ratio does not equal sqrt(surface-face ratio); the "
            "refinement is not isotropic and r is not a single 3-D ratio. REFUSED.")
    return r, {
        "r": r,
        "DERIVED_NOT_CHOSEN": True,
        "surface_face_counts": list(f), "surface_face_ratios": [f[1] // f[0], f[2] // f[1]],
        "marched_layer_counts": list(lay), "layer_ratios": [lay[1] // lay[0], lay[2] // lay[1]],
        "cell_counts": list(c), "cell_ratios": [c[1] // c[0], c[2] // c[1]],
        "derivation": ("cells = surface_faces * marched_layers EXACTLY at every level; the "
                       "surface-face ratio is EXACTLY 4 (2^2, two in-plane directions x2) and "
                       "the wall-normal layer ratio is EXACTLY 2 (2^1), so the cell ratio is "
                       "8 = 2^3 and the single linear refinement is r = sqrt(4) = 2.000 in "
                       "ALL THREE directions. Checkable by hand without running anything."),
        "why_this_is_a_TRUE_OBSERVED_ORDER_not_a_lower_bound": (
            "M6SR's family holds the wall-normal direction FIXED (its A6: 64 cells per wing "
            "face at every level), so it refines 2 of 3 directions and its GCI is a "
            "SURFACE-refinement band and a LOWER BOUND (clause L-HONEST). THIS family refines "
            "the wall-normal layers too (46->92->184, ratio 2), so all three directions scale "
            "by r=2 and A.roache_triple's p is a genuine observed order of accuracy."),
        "not_rule_2_fitting": (
            "r is FORCED by three already-frozen prereg counts (surface faces, marched layers, "
            "cells) and could have been computed the moment §1 was frozen; nothing is selected "
            "to fit an answer. The DERIVATION is new; the freedom never existed."),
        "and_the_band_is_r_invariant_anyway": (
            "p is DEFINED as ln(d32/d21)/ln(r), so r^p == d32/d21 identically for ANY r and r "
            "CANCELS from GCI = Fs*|d21/f1|/(r^p - 1). A.gci_fine_from_gate_g relies on exactly "
            "this: it returns a band ONLY when every candidate ratio agrees, refusing to "
            "select one (rule 2). The band is therefore safe twice over."),
    }


# --------------------------------------------------------------------------------------
# LEVEL DISCOVERY -- own-family ids/paths/cells.  Mirrors A._discover_levels()'s SHAPE
# (coarse-to-fine, in-run-root polyMesh supersedes any source) with own-family constants.
# The SOLVE lives at <run_root>/L{id}/solve/ (the prereg §9 run roots), distinct from the
# mesh case at <run_root>/L{id}/case/ which is already built and screened.
# --------------------------------------------------------------------------------------
def _discover_levels_own_family(run_root):
    spec = []
    for lid, cells in zip(OWN_LEVEL_IDS, OWN_CELLS):
        solve = os.path.join(run_root, lid, "solve")
        lv = {
            "id": lid, "cells": cells,
            "case": solve,
            "checkmesh": os.path.join(solve, "log.checkMesh"),
            "polymesh": os.path.join(solve, "constant", "polyMesh"),
        }
        spec.append(lv)
    return spec


# --------------------------------------------------------------------------------------
# SECTION-7 PATCH-NAME SCREEN -- own-family names {wing, symmetry, farfield}.  This is the
# own-family counterpart of A.section7_condition_5 / A.verify_patch_name_source, whose
# registered name set is M6SR's {wing, inout, sym}.  The TYPE screen (A.section7_condition_1)
# and conditions 2/3/4 (A.section7_conditions_2_3_4) are REUSED UNCHANGED -- only the NAME set
# and its source dict differ.
# --------------------------------------------------------------------------------------
def verify_patch_name_source_own_family(level_id, run_root):
    """Re-hash the level's createPatchDict against the DRAFT pin; REFUSE on absence/mismatch."""
    if level_id not in OWN_LEVEL_IDS:
        raise A.Unregistered(
            f"{level_id!r} is not an own-family level; registered levels are "
            f"{list(OWN_LEVEL_IDS)}. Choosing a name set at grade time would fix a gate "
            "parameter after the freeze (rule 2). REFUSED.")
    # The dict that DETERMINED the boundary is the mesh case's createPatchDict; the solve mesh
    # is staged from that case, so the boundary it screens carries these names by construction.
    dict_path = os.path.join(run_root, level_id, "case", "system", "createPatchDict")
    if not os.path.isfile(dict_path):
        raise A.Refusal(
            f"{level_id}: the createPatchDict the expected patch-name set is DERIVED FROM is "
            f"ABSENT at {dict_path!r}. This screen will NOT fall back to the names the mesh "
            "carries. REFUSED.")
    got = A.sha256_file(dict_path)
    if got != OWN_CREATEPATCHDICT_SHA256:
        raise A.Refusal(
            f"{level_id}: createPatchDict at {dict_path!r} hashes {got}, not the pinned "
            f"{OWN_CREATEPATCHDICT_SHA256}. A different dict builds a boundary this registered "
            "expectation does not describe. REFUSED rather than screened against a stale "
            "expectation. (This pin is a DRAFT for the cfd-supervisor's check-1.)")
    return {"level": level_id, "createPatchDict": dict_path, "sha256": got,
            "expected_names": sorted(OWN_PATCH_NAMES),
            "derivation": "the dict's three `patches` entries name wing/symmetry/farfield; any "
                          "other name in the boundary is a source patch createPatch did not "
                          "consume, which is a MISMATCH and is BLOCKED."}


def section7_condition_5_own_family(level_id, patches):
    """Own-family name screen.  -> (state, detail).  state MATCH / MISMATCH / UNREGISTERED."""
    if level_id not in OWN_LEVEL_IDS:
        return "UNREGISTERED", {"level": level_id, "registered_levels": list(OWN_LEVEL_IDS)}
    got = frozenset(n for n, _t, _f in patches)
    if got == OWN_PATCH_NAMES:
        return "MATCH", {"level": level_id, "expected": sorted(OWN_PATCH_NAMES),
                         "actual": sorted(got)}
    return "MISMATCH", {
        "level": level_id, "expected": sorted(OWN_PATCH_NAMES), "actual": sorted(got),
        "unexpected": sorted(got - OWN_PATCH_NAMES), "missing": sorted(OWN_PATCH_NAMES - got),
        "basis": "rule-5 / prereg §3: the own-family boundary is wing/symmetry/farfield; a "
                 "survivor auto-patch or a renamed patch mis-applies boundary conditions."}


def section7_screen_own_family(level_id, run_root):
    """Section 7's five conditions for ONE own-family level.  -> record, label PASS/BLOCKED.

    REUSES A.section7_condition_1 (types) and A.section7_conditions_2_3_4 (openness / regions /
    min-volume) UNCHANGED; only condition 5 (names) is the own-family set.  It can only turn a
    launch OFF (rule 5); it never manufactures permission.
    """
    source = verify_patch_name_source_own_family(level_id, run_root)   # REFUSES first
    solve = os.path.join(run_root, level_id, "solve")
    pm = os.path.join(solve, "constant", "polyMesh")
    if not os.path.isdir(pm):
        raise A.Refusal(
            f"{level_id}: the polyMesh this screen must read is ABSENT at {pm!r}. With no mesh "
            "there is nothing to screen and this is NOT a pass. REFUSED.")
    bnd = A.read_boundary(pm)
    patches = [(b["name"], b["type"], b["nFaces"]) for b in bnd]
    cmp_ = os.path.join(solve, "log.checkMesh")
    cm = A.read_checkmesh(cmp_) if os.path.exists(cmp_) else {"state": "ABSENT"}

    clauses = {}
    ok1, d1 = A.section7_condition_1(level_id, patches)
    clauses["S7_C1_patch_types_wall_symmetry_patch"] = (ok1, d1)
    for name, (ok, det) in A.section7_conditions_2_3_4(level_id, cm).items():
        clauses[name] = (ok, det)
    st5, d5 = section7_condition_5_own_family(level_id, patches)
    clauses["S7_C5_patch_names_match_own_family_set"] = (st5 == "MATCH", d5)

    failed = [k for k, (ok, _d) in clauses.items() if not ok]
    return {
        "step": "B4s", "screen": "Section 7 -- own-family launch-path ill-posedness screen",
        "level": level_id, "polymesh": pm, "checkmesh": cmp_,
        "expected_patch_name_source": source, "actual_patches": patches,
        "clauses": {k: {"pass": bool(ok),
                        "label": A._verdict("PASS" if ok else "BLOCKED"), "detail": det}
                    for k, (ok, det) in clauses.items()},
        "failed_clauses": failed,
        "label": A._verdict("BLOCKED" if failed else "PASS"),
        "one_way_door": "Section 7 blocks a launch; it never authorises one (rule 5).",
    }


# --------------------------------------------------------------------------------------
# GATE G -- own-family orchestration.  THE GCI MATH IS A.roache_triple UNCHANGED; the rule-5
# ordering is identical to A.gate_g; the ONLY differences are (i) r is DERIVED from the
# own-family 3-D counts via refinement_ratio_own_family() [A.gate_g uses M6SR's surface-only
# derivation], and (ii) the band is framed as a CREDENTIAL-GRADE OBSERVED ORDER, not the
# L-HONEST surface-refinement lower bound.  A.gci_fine_from_gate_g consumes the
# `G3_G4_all_candidate_ratios` dict this builds, exactly as it does for A.gate_g.
# --------------------------------------------------------------------------------------
# Candidate ratios exercised by A.gci_fine_from_gate_g's agreement cross-check.  GCI is
# ALGEBRAICALLY INVARIANT under r, so all three MUST agree to within 1e-12 -- if they ever do
# not, A.gci_fine_from_gate_g returns no band rather than select one (rule 2).  The REGISTERED
# ratio for the reported observed order is r = 2.000, derived above.
OWN_R_CANDIDATES = {
    "r=2.000 isotropic linear refinement (cells 2^3=8.00; surface 2^2, wall-normal 2^1)": 2.0,
    "r=1.5874 cube root of the 8.00 cell ratio (a cross-check; GCI is r-invariant)":
        8.0 ** (1.0 / 3.0),
    "r=4.000 raw surface-face ratio (a cross-check; GCI is r-invariant)": 4.0,
}


def gate_g_own_family(levels_cd, levels_logs):
    """Gate G on the own-family {L2, L1, L0} triple, under rule 5's ordering.

    levels_cd / levels_logs are COARSE-TO-FINE [L2, L1, L0].  f1 = FINE = L0.
    """
    if len(levels_cd) != 3 or len(levels_logs) != 3:
        raise A.Refusal("Gate G needs exactly three levels. REFUSED.")
    finals = []
    for path in levels_cd:
        s = A.cd_series(path)
        finals.append(s[-1][1])
    f3, f2, f1 = finals              # L2 coarse, L1 medium, L0 fine
    diff = f3 - f2

    g1 = []
    for path in levels_cd:
        s = A.cd_series(path)
        tail = [v for t, v in s if t >= s[-1][0] - A.G1_TAIL_ITERATIONS]
        swing = (max(tail) - min(tail)) if len(tail) >= 2 else float("inf")
        g1.append({"path": path, "tail_iterations": A.G1_TAIL_ITERATIONS,
                   "CD_swing": swing, "tolerance": A.G1_FRACTION_OF_L3_L2 * abs(diff),
                   "pass": swing <= A.G1_FRACTION_OF_L3_L2 * abs(diff)})

    g2 = []
    for log, cdp in zip(levels_logs, levels_cd):
        steps, forms, _red = A.residual_series(log)
        g2.append(dict(A.gate_g2(steps, A.cd_series(cdp), diff), log=log,
                       print_forms_seen=forms))

    out = {"C_D": {"L2": f3, "L1": f2, "L0": f1},
           "levels_coarse_to_fine": list(OWN_LEVEL_IDS),
           "fine_level": OWN_LEVEL_IDS[-1],
           "G1": g1, "G2": g2,
           "OWN_FAMILY_ORDER_NOTE": OWN_FAMILY_ORDER_NOTE}

    # G3 / G4 -- all candidate ratios via A.roache_triple UNCHANGED; none adopted for the band
    # (A.gci_fine_from_gate_g reads this and refuses to select).
    triples = {}
    for name, r in OWN_R_CANDIDATES.items():
        triples[name] = A.roache_triple(f3, f2, f1, r)
    out["G3_G4_all_candidate_ratios"] = triples

    # Rule-5 clause (1): every level iteratively converged AND plateaued.
    if not (all(x["pass"] for x in g1) and all(x["pass"] for x in g2)):
        out["gate_G_label"] = A._verdict("NOT A RESULT")
        out["reason"] = ("rule 5 clause (1): a level is not iteratively converged or not "
                         "plateaued. The value and the triples are printed beside it.")
        return out

    # Rule-5 clause (2): the triple must classify CONVERGING.
    classes = {v["classification"] for v in triples.values()}
    if classes != {"CONVERGING"}:
        out["gate_G_label"] = A._verdict("NOT A RESULT")
        out["reason"] = (f"rule 5 clause (2): the triple classifies as {sorted(classes)}. GCI "
                         "is NEVER quoted when the three values are not monotone.")
        return out

    # Rule-5 clause (3): CONVERGING -> the OBSERVED ORDER and band are reported at the derived
    # isotropic r = 2.000.  The gate is REACHED (the family band exists); the PASS/GATE FAIL of
    # the deliverable is Gate P's, on the Cp taps, behind this gate.
    r_reg, r_basis = refinement_ratio_own_family()
    out["G3_G4_registered_ratio"] = r_basis
    out["G3_G4_roache_triple_at_registered_r"] = A.roache_triple(f3, f2, f1, r_reg)
    out["observed_order_p"] = out["G3_G4_roache_triple_at_registered_r"]["p_s"]
    out["gate_G_label"] = A._verdict("GATE REACHED")
    out["reason"] = (
        f"the triple classifies CONVERGING at the DERIVED isotropic refinement ratio r = "
        f"{r_reg} (from prereg §1's surface-face, layer and cell counts). Because the family "
        "refines ALL THREE directions, the order p is a CREDENTIAL-GRADE OBSERVED ORDER of "
        "accuracy and the GCI at Fs=1.25 is the family band Sanaa named -- NOT a "
        "surface-refinement lower bound (M6SR's L-HONEST does not apply here).")
    return out


# --------------------------------------------------------------------------------------
# CLI.  Mirrors A.main()'s modes for the own family: --controls / --selftest delegate to A's
# PINNED planted-control suite UNCHANGED (rule 3); --section7-screen runs the own-family launch
# screen; --grade / --gate-p grade the own-family triple with the reused measurement core.
# --------------------------------------------------------------------------------------
def main(argv):
    import argparse
    ap = argparse.ArgumentParser(add_help=True, description=__doc__)
    ap.add_argument("--controls", action="store_true",
                    help="run A's PINNED planted controls (rule 3) UNCHANGED and stop")
    ap.add_argument("--selftest", action="store_true",
                    help="A's controls + the -O parity control + the mutation control")
    ap.add_argument("--mutate", default=None, help="corrupt one shipped statistic; must go RED")
    ap.add_argument("--section7-screen", action="store_true",
                    help="own-family Section-7 launch screen for ONE level (needs --level). "
                         "EXIT 0 = PASS, 11 = BLOCKED, 2 = REFUSAL. Turns a launch OFF only.")
    ap.add_argument("--level", default=None, help="L2 | L1 | L0, for --section7-screen")
    ap.add_argument("--grade", action="store_true", help="grade Gate G and Gate P")
    ap.add_argument("--gate-p", action="store_true",
                    help="Gate P and its figure data ALONE (Gate G not run; label passed is "
                         "NOT A RESULT, so this mode can never produce a PASS)")
    ap.add_argument("--run-root",
                    default=os.path.join(REPO, "verification/runs/M6_OWN_FAMILY_runs"))
    ap.add_argument("--scratch", default=None)
    args = ap.parse_args(argv[1:])

    scratch = args.scratch or tempfile.mkdtemp(prefix="m6own_controls_")
    os.makedirs(scratch, exist_ok=True)

    # ---- PLANTED CONTROLS (rule 3) -- A's PINNED suite, UNCHANGED. --------------------
    if args.controls or args.selftest:
        fired, detail = A.controls(scratch, mutate=args.mutate)
        for cid in sorted(fired, key=lambda s: (len(s), s)):
            print(f"CONTROL {cid:5s} {'FIRED' if fired[cid] else 'DID NOT FIRE'} : "
                  f"{detail[cid]}")
        allfired = all(fired.values())
        if args.selftest:
            c16 = A.control_c16(scratch)
            print(f"CONTROL C16   {'FIRED' if c16['pass'] else 'DID NOT FIRE'} : "
                  f"python3 vs python3 -O -> rc {c16['rc_plain']} / {c16['rc_dash_O']}, "
                  f"identical control verdicts {c16['identical_control_verdicts']}")
            if not c16["pass"]:
                raise A.Refusal(f"-O parity did not hold: {c16}.")
        if not allfired:
            raise A.Refusal(
                "A PLANTED CONTROL DID NOT FIRE: "
                f"{[c for c in sorted(fired) if not fired[c]]}. A PASS reported by a reader "
                "whose plant did not fire is NOT A RESULT, not a pass (rule 3). REFUSED.")
        print("ALL REGISTERED CONTROLS FIRED (A's pinned suite, blob "
              f"{PINNED_M6SR_BLOB[:12]}).")
        return 0

    # ---- SECTION-7 LAUNCH SCREEN (one level). ----------------------------------------
    if args.section7_screen:
        if not args.level:
            raise A.Refusal("--section7-screen requires --level. A screen that does not know "
                            "which level it is screening is not a screen.")
        rec = section7_screen_own_family(args.level, args.run_root)
        A._emit({"result": rec, "OWN_FAMILY_ORDER_NOTE": OWN_FAMILY_ORDER_NOTE,
                 "NOT_CLAIMED": OWN_NOT_CLAIMED})
        return 11 if rec["failed_clauses"] else 0

    # ---- GRADE Gate G + Gate P (or Gate P alone). ------------------------------------
    if args.grade or args.gate_p:
        levels = _discover_levels_own_family(args.run_root)

        # Rule-4 strict completion + age guard, per level -- A.completion_clauses UNCHANGED.
        for lv, et in zip(levels, OWN_END_TIMES):
            cl = A.completion_clauses(lv["case"], et)
            if not cl["ALL"]:
                raise A.Refusal(
                    f"{lv['id']}: rule-4 strict completion FAILED on "
                    f"{[k for k, v in cl.items() if v is False]}. The comparator REFUSES "
                    "(exit 2) rather than degrade.")

        # Gate P's data, built and PERSISTED before Gate G -- Sanaa's named physics is not
        # taken down by a refusal about a band (mirrors A.main).  Cp comparison / reference /
        # A-MAP are A's PINNED functions, UNCHANGED; case_2308.dat is hash-refused inside them.
        ref = A.read_case_2308()
        d1 = A.d1_discriminator(ref)
        cfd_by_level, meta_by_level = {}, {}
        for lv, et in zip(levels, OWN_END_TIMES):
            sec, meta = A.cfd_sections_for_case(lv["case"], et, lv["polymesh"])
            cfd_by_level[lv["id"]] = sec
            meta_by_level[lv["id"]] = meta
        fig = A.gate_p_figure_data(ref, cfd_by_level, meta_by_level, d1)
        fig_path = os.path.join(args.run_root, "GATE_P_FIGURE_DATA.json")
        try:
            A._write(fig_path, __import__("json").dumps(fig, indent=2, default=str) + "\n")
        except OSError as exc:
            raise A.Refusal(f"could not persist Gate P's figure data to {fig_path}: {exc}. "
                            "Data that exists only in a pipe is not an artifact. REFUSED.")

        finest = levels[-1]["id"]    # L0 -- coarse-to-fine, so [-1] is the finest

        if args.gate_p:
            p = A.gate_p(ref, cfd_by_level[finest], d1, None, A._verdict("NOT A RESULT"))
            A._emit({"step": "Gate P only", "graded_level": finest, "gate_P": p,
                     "gate_G": "NOT RUN IN THIS MODE -- Gate P is behind Gate G, so the label "
                               "passed in is NOT A RESULT. This mode cannot produce a PASS.",
                     "figure_data": fig_path,
                     "OWN_FAMILY_ORDER_NOTE": OWN_FAMILY_ORDER_NOTE,
                     "NOT_CLAIMED": OWN_NOT_CLAIMED})
            return 0

        # Gate G -- own-family orchestration; the GCI MATH is A.roache_triple /
        # A.gci_fine_from_gate_g UNCHANGED.
        cds = [os.path.join(lv["case"], "postProcessing", "forceCoeffs", "0",
                            "coefficient.dat") for lv in levels]
        logs = [os.path.join(lv["case"], "log.rhoSimpleFoam") for lv in levels]
        g = gate_g_own_family(cds, logs)
        gci, gci_basis = A.gci_fine_from_gate_g(g)
        p = A.gate_p(ref, cfd_by_level[finest], d1, gci, g["gate_G_label"])
        A._emit({"step": "grade", "gate_G": g, "gate_P": p, "graded_level": finest,
                 "gate_P_numerical_band_basis": gci_basis, "figure_data": fig_path,
                 "OWN_FAMILY_ORDER_NOTE": OWN_FAMILY_ORDER_NOTE,
                 "NOT_CLAIMED": OWN_NOT_CLAIMED})
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except A.Refusal as _exc:
        print(f"REFUSED: {_exc}", file=sys.stderr)
        sys.exit(2)
    except A.InternalDefect as _exc:
        print(f"INTERNAL DEFECT of the comparator: {_exc}", file=sys.stderr)
        sys.exit(70)
    except Exception as _exc:            # a crash is NOT a refusal -- it is rc 70
        import traceback
        traceback.print_exc()
        print(f"INTERNAL DEFECT (unhandled {type(_exc).__name__}): {_exc}", file=sys.stderr)
        sys.exit(70)
