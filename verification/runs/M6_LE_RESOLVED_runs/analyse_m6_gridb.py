#!/usr/bin/env python3
"""M6 GRID (b) grading harness -- a THIN READ-ONLY WRAPPER over the FROZEN M6 measurement core.

WHY THIS FILE EXISTS.  Sanaa's grid-vs-model ruling option (b) retired the own-family 72k/574k
pyHyp mesh and re-based the M6 test grid on the A3 primal-validated surface, LE- and
shock-resolved at y+<1 (verification/campaign/M6_LE_RESOLVED_GRIDB_PREREGISTRATION.md, DRAFT).
The own-family grader verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py (blob
da0df95c) is HARD-WIRED to that dead family's level ids/paths/cell-counts, so it cannot grade
grid (b) as-invoked.  The cfd-supervisor APPROVED authoring a new thin wrapper over the pinned
core (the T23G2R re-pin precedent, and the sanctioned gatep_diag_n5.py pattern).  THIS FILE IS
THAT WRAPPER.  It is a DRAFT for the cfd-supervisor's check-1 (measurement logic) and check-4;
nothing is graded until it is pinned by a FREEZE ADDENDUM in the prereg.

THE MEASUREMENT CORE IS IMPORTED AND CALLED UNCHANGED -- byte-for-byte the blob 8007b23d.  The
Cp comparison, the A-MAP discriminator, the Roache/GCI math, the strict completion rule and the
planted controls are A's PINNED functions, NOT reimplemented:
    A.read_case_2308        the 271 AR-138 taps, sha256-REFUSED on mismatch (Gate P reference)
    A.d1_discriminator      the A-MAP Cn-monotonicity discriminator
    A.cfd_sections_for_case the CFD Cp producer (foam-sampled wing surface, interpolate true)
    A.gate_p                Gate P -- surface Cp vs the taps, ΔCp=±0.02, x/c<=0.90  (UNCHANGED)
    A.set_to_set_assignment §4.5's order-independent channel
    A.roache_triple         THE GCI MATH -- classification + observed order p + GCI at Fs=1.25
    A.gci_fine_from_gate_g  the band Gate P's numerical channel consumes (r-invariant)
    A.cd_series / A.residual_series / A.gate_g2   the iterative-convergence machinery (G1/G2)
    A.completion_clauses    rule-4 strict completion + the age guard
    A.controls / A.control_c16   A's PINNED planted-control suite (rule 3)
    A.read_boundary / A.read_checkmesh / A.section7_condition_1 / A.section7_conditions_2_3_4
    A._verdict / A.Refusal / A.InternalDefect / A.Unregistered / A._emit / A._write / A.sha256_file

THE DIFF vs analyse_m6sr.py / analyse_m6_own_family.py IS THE GRID-(b) ADAPTATION LAYER ONLY --
LOCAL constants, no mutation of A:
  * level ids Lc/Lm/Lf (coarse->fine), grid-b run roots M6_LE_RESOLVED_runs/L{c,m,f}/solve
  * grid-b EXACT-NESTING counts (Lc+Lm MEASURED first-hand 2026-09-10 from L{c,m}/solve/
    log.checkMesh; Lf coarsen-nesting value PENDING its own build): surface faces (6240/24960/99840,
    ratio 4.00), marched layers (150/300/600, ratio 2.00), cells (936000/7488000/59904000,
    ratio 8.00) -- r = sqrt(4) = 2.000
  * patch-name set {wing, symmetry, farfield}
  * endTimes (draft; the prereg §6 6000-iteration basis -- supervisor confirms at freeze)
  * THE HONEST GATE-G NOTE: grid (b) refines chordwise x2 AND spanwise x2 (surface x4) AND the
    wall-normal LAYER COUNT x2 -- but s0 is held FIXED at 1.546e-6 for y+<1 at every level
    (Sanaa's integrate-to-wall directive), so the wall-normal FIRST cell does not scale.  Whether
    the resulting Gate-G order is a full observed order or carries an honest caveat is the
    verification-team / rule-5 question flagged in the prereg (§7); THIS WRAPPER DOES NOT DECIDE
    IT and does NOT assert a clean observed order.  The MATH is A.roache_triple UNCHANGED.

NOTHING in A is altered, monkey-patched or shadowed.  A's module constants stay M6SR's; this file
supplies its OWN counts/names as local constants.  BOTH frozen blobs are re-hashed on disk before
any read and REFUSE on drift (rule 2).  A live rule-3 plant is driven through the ACTUAL grid-b
fields before any real read.  Reads only; writes at most the Gate-P figure JSON under the run
root.  SUBMISSIONS ARE PARKED -- sends nothing (rule 7).  NO BARE assert (L-475): explicit raise.

EXIT VOCABULARY (identical to A):
    0   graded (a verdict may itself be GATE FAIL / NOT A RESULT -- rc 0 means the INSTRUMENT ran)
    2   REFUSAL (a control did not fire, a pinned blob moved, a completion clause failed, a
        needed parameter is unregistered) -- REFUSE RATHER THAN DEGRADE
    11  a Section-7 launch-path level is BLOCKED (a statement about the MESH)
    70  INTERNAL DEFECT of this wrapper -- never a finding about the M6
"""
import math
import os
import subprocess
import sys
import tempfile

REPO = "/home/ubuntu/Certonomous"
_M6SR_DIR = os.path.join(REPO, "cases", "M6SR")
if _M6SR_DIR not in sys.path:
    sys.path.insert(0, _M6SR_DIR)
import analyse_m6sr as A   # noqa: E402  -- the pinned, check-1'd measurement core

# ---- FROZEN BLOB PINS (rule 2).  Re-hashed on disk before any read; REFUSE on drift. --------
# CORE is the imported measurement core; GRADER is the superseded own-family grader, pinned for
# lineage (this wrapper supersedes it for grid (b)).  gatep_diag_n5.py pins both the same way.
CORE_PATH = os.path.join(REPO, "cases/M6SR/analyse_m6sr.py")
CORE_BLOB = "8007b23da5bb3173dacb6eda1d67ca5d90ce9139"
GRADER_PATH = os.path.join(REPO, "verification/runs/M6_OWN_FAMILY_runs/analyse_m6_own_family.py")
GRADER_BLOB = "da0df95c81ded5833821cfd8a1f711d7f849f93c"

# ---- GRID-(b) REGISTERED COUNTS (LOCAL constants; transcribed from the prereg §3.1/§4). -----
GRIDB_LEVEL_IDS = ("Lc", "Lm", "Lf")                    # coarse -> fine
# TRANSCRIBED FROM THE REAL BUILT COARSEST MESH (lane, 2026-09-10). The prior values
# (12232, 48928, 195712) were PREDICTED from gen_m6_gridb.LEVELS's superseded re-loft dims
# (chord 140/279/557); that re-loft is NOT buildable (cgnsutilities Block-constructor transpose
# bug, see build_capped_surface.py). The BUILDABLE path is coarsen-x{2,1,0} of the capped 9-zone
# master surface -> wing 65x41 / 129x81 / 257x161. Lc wall-face count MEASURED first-hand from
# verification/runs/M6_LE_RESOLVED_runs/Lc/solve/log.checkMesh (boundary 'wing' nFaces 6240).
# Lm=24960 MEASURED first-hand 2026-09-10 from Lm/solve/log.checkMesh (march "Total Faces: 24960";
# cells 7488000/300), and independently corroborated by cases/M6SR M6SR_PREREGISTRATION §2.2
# ("the 24,960-face surface"). Lf=99840 is the native (coarsen-x0) count = 6240*16 = 24960*4,
# PENDING its own build (the ~60M-cell fine is a chief capacity decision, held for check-4).
GRIDB_SURFACE_FACES = (6240, 24960, 99840)              # ratio 4.00; Lc+Lm MEASURED, Lf PENDING build
# y+<1 needs ~150 wall-normal layers to reach the farfield (dry-run confirmed); the ×8
# 3D-refinement (observed-order) family doubles them 150/300/600.  (A cheaper SURFACE-ONLY
# lower-bound family holds ~150 layers at every level -> cells ×4; that variant's counts and
# its M6SR-style L-HONEST note would be supplied instead -- prereg §3.1/§7. This wrapper is
# written for the ×8 family the supervisor's framing approved.)
GRIDB_MARCHED_LAYERS = (150, 300, 600)                  # ratio 2.00; Lc BUILT with 150 (N=151 nodes)
# Lc MEASURED: 6240 * 150 = 936000 cells, first-hand from Lc/solve/log.checkMesh ("cells: 936000").
# Lm MEASURED: 24960 * 300 = 7488000 cells, first-hand from Lm/solve/log.checkMesh ("cells: 7488000").
# Lf = 99840 * 600, exact x8 nesting, PENDING its own build.
GRIDB_CELLS = (936000, 7488000, 59904000)               # ratio 8.00 = faces * layers; Lc+Lm MEASURED
GRIDB_CELL_RATIO_EXACT = 8
GRIDB_PATCH_NAMES = frozenset(("wing", "symmetry", "farfield"))
GRIDB_END_TIMES = (6000, 6000, 6000)                    # prereg §6 cost basis (DRAFT)
# DRAFT pin -- the supervisor pins the built dict's sha at the FREEZE ADDENDUM (like the
# own-family's OWN_CREATEPATCHDICT_SHA256). Absent/placeholder until the meshes are built.
GRIDB_CREATEPATCHDICT_SHA256 = "<DRAFT -- pinned at FREEZE ADDENDUM once L{c,m,f} are built>"

RUN_ROOT = os.path.join(REPO, "verification/runs/M6_LE_RESOLVED_runs")

# The HONEST Gate-G note carried on every grid-b output.  It does NOT claim a clean observed
# order; it discloses the fixed-s0 wall-normal refinement and defers the observed-order question.
GRIDB_ORDER_NOTE = (
    "Grid (b) is an r=2 three-level family: each level refines the surface x4 (chord x2, span x2) "
    "AND the wall-normal LAYER COUNT x2, so cells scale 2^3 = 8.00 per level and the Roache ratio "
    "is r = 2.000. HONEST CAVEAT (prereg §7, verification/rule-5 owned): s0 is held FIXED at "
    "1.546e-6 m for y+<1 at every level (Sanaa's integrate-to-wall directive), so the wall-normal "
    "FIRST cell does NOT scale with the level -- the wall-normal refinement comes from the layer "
    "count / outer spacing. Whether Gate G's p is a full observed order or carries an honest band "
    "caveat is NOT decided by this wrapper; A.roache_triple's MATH is unchanged and the "
    "classification (rule 5) still governs -- a non-CONVERGING triple is NOT A RESULT."
)

GRIDB_NOT_CLAIMED = [
    "the order is credential-grade ONLY IF Gate G classifies CONVERGING; a non-CONVERGING triple "
    "is NOT A RESULT whatever the number says (rule 5)",
    "the wall-normal first cell is held fixed for y+<1 and does NOT refine with the level; the "
    "observed-order interpretation of Gate G is deferred to verification (prereg §7)",
    "the uncorrected AR-138 wall interference is DISCLOSED and deliberately NOT in the band "
    "(A.gate_p carries this verbatim)",
    "Gate P grades x/c <= 0.90; the rear 10% is plotted and reported, NEVER graded (prereg §5)",
    "A-MAP (section->y/b) is ASSUMED, not measured; D1 adjudicates its ordering only",
    "SUBMISSIONS ARE PARKED -- nothing is sent, filed or registered outside this box (rule 7)",
]


def _blob(path):
    return subprocess.check_output(["git", "-C", REPO, "hash-object", path]).decode().strip()


def _pin_blobs():
    """Re-hash both frozen blobs on disk; REFUSE on drift (rule 2)."""
    for path, want in ((CORE_PATH, CORE_BLOB), (GRADER_PATH, GRADER_BLOB)):
        got = _blob(path)
        if got != want:
            raise A.Refusal(f"{path} blob {got} != pinned {want}. The grading path is pinned by "
                            "hash and admits no substitute (rule 2). REFUSED.")


# --------------------------------------------------------------------------------------
# THE REFINEMENT RATIO -- DERIVED from the grid-b counts, not stored.  Mirrors
# analyse_m6_own_family.refinement_ratio_own_family: exact face ratio 4, layer ratio 2, cell
# ratio 8, r = sqrt(4) = 2.000.  REFUSES (InternalDefect) on any inexact ratio.
# --------------------------------------------------------------------------------------
def refinement_ratio_gridb():
    f, lay, c = GRIDB_SURFACE_FACES, GRIDB_MARCHED_LAYERS, GRIDB_CELLS
    for i in range(3):
        if f[i] * lay[i] != c[i]:
            raise A.InternalDefect(
                f"grid-b level {GRIDB_LEVEL_IDS[i]}: surface_faces {f[i]} * layers {lay[i]} "
                f"= {f[i]*lay[i]} != registered cells {c[i]}. r rests on this factorisation.")
    if not (f[1] == 4 * f[0] and f[2] == 4 * f[1]):
        raise A.InternalDefect(f"grid-b surface-face counts {f} not in exact ratio 4.")
    if not (lay[1] == 2 * lay[0] and lay[2] == 2 * lay[1]):
        raise A.InternalDefect(f"grid-b marched-layer counts {lay} not in exact ratio 2.")
    if not (c[1] == GRIDB_CELL_RATIO_EXACT * c[0] and c[2] == GRIDB_CELL_RATIO_EXACT * c[1]):
        raise A.InternalDefect(f"grid-b cell counts {c} not in exact ratio {GRIDB_CELL_RATIO_EXACT}.")
    r = math.sqrt(4.0)              # = 2.000 exactly
    return r, {
        "r": r, "DERIVED_NOT_CHOSEN": True,
        "surface_face_counts": list(f), "marched_layer_counts": list(lay), "cell_counts": list(c),
        "derivation": ("cells = surface_faces * marched_layers exactly; surface-face ratio 4 "
                       "(chord x2, span x2), layer ratio 2, cell ratio 8 = 2^3; r = sqrt(4) = 2."),
        "honest_caveat": ("s0 fixed for y+<1 -- the wall-normal FIRST cell does not scale; the "
                          "observed-order interpretation is deferred to verification (prereg §7)."),
    }


def _discover_levels_gridb(run_root):
    spec = []
    for lid, cells in zip(GRIDB_LEVEL_IDS, GRIDB_CELLS):
        solve = os.path.join(run_root, lid, "solve")
        spec.append({"id": lid, "cells": cells, "case": solve,
                     "checkmesh": os.path.join(solve, "log.checkMesh"),
                     "polymesh": os.path.join(solve, "constant", "polyMesh")})
    return spec


# --------------------------------------------------------------------------------------
# LIVE RULE-3 PLANT on the ACTUAL grid-b fields (the gatep_diag_n5.py pattern).  A known Pa
# perturbation is planted into the sampled wing surface read from disk; every station's Cp MUST
# shift by exactly PLANT/q_inf.  If the reader cannot see the plant, its zero is not evidence.
# --------------------------------------------------------------------------------------
PLANT_PA = 1000.0


def _live_plant(levels):
    q = A.q_inf_pa()
    expected = PLANT_PA / q
    report = {}
    for lv, et in zip(levels, GRIDB_END_TIMES):
        if not os.path.isdir(lv["polymesh"]):
            report[lv["id"]] = {"skipped": "polyMesh absent (mesh not built yet)"}
            continue
        base, _ = A.cfd_sections_for_case(lv["case"], et, lv["polymesh"], plant_pa=0.0)
        pl, _ = A.cfd_sections_for_case(lv["case"], et, lv["polymesh"], plant_pa=PLANT_PA)
        worst = 0.0
        for s in base:
            b, p = dict(base[s]), dict(pl[s])
            for x in b:
                worst = max(worst, abs((p[x] - b[x]) - expected))
        report[lv["id"]] = {"expected_dCp_shift": expected, "worst_dev": worst}
        if worst > 1e-9:
            raise A.Refusal(
                f"{lv['id']}: planted {PLANT_PA} Pa but Cp shift deviates {worst} from "
                f"{expected} -- the reader cannot see the plant (rule 3). REFUSED.")
    return report


# --------------------------------------------------------------------------------------
# GATE G -- grid-b orchestration.  THE GCI MATH IS A.roache_triple UNCHANGED; the rule-5 ordering
# is identical to A.gate_g; r is DERIVED from the grid-b counts; the band is framed with the
# HONEST fixed-s0 caveat (NOT a clean observed-order claim).
# --------------------------------------------------------------------------------------
OWN_R_CANDIDATES = {
    "r=2.000 isotropic linear refinement (cells 2^3=8.00; surface 2^2, layers 2^1)": 2.0,
    "r=1.5874 cube root of the 8.00 cell ratio (cross-check; GCI is r-invariant)": 8.0 ** (1.0 / 3.0),
    "r=4.000 raw surface-face ratio (cross-check; GCI is r-invariant)": 4.0,
}


def gate_g_gridb(levels_cd, levels_logs):
    if len(levels_cd) != 3 or len(levels_logs) != 3:
        raise A.Refusal("Gate G needs exactly three levels. REFUSED.")
    finals = [A.cd_series(p)[-1][1] for p in levels_cd]
    f3, f2, f1 = finals              # Lc coarse, Lm medium, Lf fine
    diff = f3 - f2

    g1 = []
    for path in levels_cd:
        s = A.cd_series(path)
        tail = [v for t, v in s if t >= s[-1][0] - A.G1_TAIL_ITERATIONS]
        swing = (max(tail) - min(tail)) if len(tail) >= 2 else float("inf")
        g1.append({"path": path, "CD_swing": swing,
                   "tolerance": A.G1_FRACTION_OF_L3_L2 * abs(diff),
                   "pass": swing <= A.G1_FRACTION_OF_L3_L2 * abs(diff)})
    g2 = []
    for log, cdp in zip(levels_logs, levels_cd):
        steps, forms, _red = A.residual_series(log)
        g2.append(dict(A.gate_g2(steps, A.cd_series(cdp), diff), log=log, print_forms_seen=forms))

    out = {"C_D": dict(zip(GRIDB_LEVEL_IDS, (f3, f2, f1))),
           "levels_coarse_to_fine": list(GRIDB_LEVEL_IDS), "fine_level": GRIDB_LEVEL_IDS[-1],
           "G1": g1, "G2": g2, "GRIDB_ORDER_NOTE": GRIDB_ORDER_NOTE}

    triples = {name: A.roache_triple(f3, f2, f1, r) for name, r in OWN_R_CANDIDATES.items()}
    out["G3_G4_all_candidate_ratios"] = triples

    if not (all(x["pass"] for x in g1) and all(x["pass"] for x in g2)):
        out["gate_G_label"] = A._verdict("NOT A RESULT")
        out["reason"] = ("rule 5 clause (1): a level is not iteratively converged or not "
                         "plateaued. Value and triples printed beside it.")
        return out
    classes = {v["classification"] for v in triples.values()}
    if classes != {"CONVERGING"}:
        out["gate_G_label"] = A._verdict("NOT A RESULT")
        out["reason"] = (f"rule 5 clause (2): the triple classifies as {sorted(classes)}. GCI is "
                         "NEVER quoted when the three values are not monotone.")
        return out
    r_reg, r_basis = refinement_ratio_gridb()
    out["G3_G4_registered_ratio"] = r_basis
    out["G3_G4_roache_triple_at_registered_r"] = A.roache_triple(f3, f2, f1, r_reg)
    out["observed_order_p"] = out["G3_G4_roache_triple_at_registered_r"]["p_s"]
    out["gate_G_label"] = A._verdict("GATE REACHED")
    out["reason"] = ("the triple classifies CONVERGING at the derived r = 2.000; the GCI at "
                     "Fs=1.25 is the family band. The observed-order interpretation carries the "
                     "fixed-s0 caveat (GRIDB_ORDER_NOTE) -- verification/rule-5 owned.")
    return out


# --------------------------------------------------------------------------------------
# SECTION-7 launch screen (grid-b names).  REUSES A.section7_condition_1 (types) and
# A.section7_conditions_2_3_4 (openness/regions/min-volume) UNCHANGED; only the NAME set differs.
# It can only turn a launch OFF (rule 5).
# --------------------------------------------------------------------------------------
def _s7_condition5_gridb(level_id, patches):
    got = frozenset(n for n, _t, _f in patches)
    if got == GRIDB_PATCH_NAMES:
        return True, {"level": level_id, "expected": sorted(GRIDB_PATCH_NAMES), "actual": sorted(got)}
    return False, {"level": level_id, "expected": sorted(GRIDB_PATCH_NAMES), "actual": sorted(got),
                   "unexpected": sorted(got - GRIDB_PATCH_NAMES),
                   "missing": sorted(GRIDB_PATCH_NAMES - got),
                   "basis": "rule-5 / prereg §6: grid-b boundary is wing/symmetry/farfield."}


def section7_screen_gridb(level_id, run_root):
    if level_id not in GRIDB_LEVEL_IDS:
        raise A.Unregistered(f"{level_id!r} not a grid-b level; registered {list(GRIDB_LEVEL_IDS)}.")
    solve = os.path.join(run_root, level_id, "solve")
    pm = os.path.join(solve, "constant", "polyMesh")
    if not os.path.isdir(pm):
        raise A.Refusal(f"{level_id}: polyMesh absent at {pm!r}; nothing to screen. NOT a pass.")
    patches = [(b["name"], b["type"], b["nFaces"]) for b in A.read_boundary(pm)]
    cmp_ = os.path.join(solve, "log.checkMesh")
    cm = A.read_checkmesh(cmp_) if os.path.exists(cmp_) else {"state": "ABSENT"}
    clauses = {}
    ok1, d1 = A.section7_condition_1(level_id, patches)
    clauses["S7_C1_patch_types"] = (ok1, d1)
    for name, (ok, det) in A.section7_conditions_2_3_4(level_id, cm).items():
        clauses[name] = (ok, det)
    ok5, d5 = _s7_condition5_gridb(level_id, patches)
    clauses["S7_C5_patch_names_grid_b_set"] = (ok5, d5)
    failed = [k for k, (ok, _d) in clauses.items() if not ok]
    return {"step": "B4s", "screen": "Section 7 -- grid-b launch-path ill-posedness screen",
            "level": level_id, "polymesh": pm,
            "clauses": {k: {"pass": bool(ok), "label": A._verdict("PASS" if ok else "BLOCKED"),
                            "detail": det} for k, (ok, det) in clauses.items()},
            "failed_clauses": failed, "label": A._verdict("BLOCKED" if failed else "PASS"),
            "one_way_door": "Section 7 blocks a launch; it never authorises one (rule 5)."}


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(add_help=True, description=__doc__)
    ap.add_argument("--controls", action="store_true",
                    help="run A's PINNED planted controls (rule 3) UNCHANGED and stop")
    ap.add_argument("--selftest", action="store_true", help="A's controls + the -O parity control")
    ap.add_argument("--mutate", default=None)
    ap.add_argument("--section7-screen", action="store_true", help="grid-b Section-7 screen (--level)")
    ap.add_argument("--level", default=None, help="Lc | Lm | Lf")
    ap.add_argument("--grade", action="store_true", help="grade Gate G and Gate P")
    ap.add_argument("--gate-p", action="store_true", help="Gate P and its figure data ALONE")
    ap.add_argument("--run-root", default=RUN_ROOT)
    ap.add_argument("--scratch", default=None)
    args = ap.parse_args(argv[1:])

    _pin_blobs()                                  # rule 2: refuse on drift before any read
    scratch = args.scratch or tempfile.mkdtemp(prefix="m6gridb_")
    os.makedirs(scratch, exist_ok=True)

    if args.controls or args.selftest:
        fired, detail = A.controls(scratch, mutate=args.mutate)
        for cid in sorted(fired, key=lambda s: (len(s), s)):
            print(f"CONTROL {cid:5s} {'FIRED' if fired[cid] else 'DID NOT FIRE'} : {detail[cid]}")
        if args.selftest:
            c16 = A.control_c16(scratch)
            print(f"CONTROL C16   {'FIRED' if c16['pass'] else 'DID NOT FIRE'} : -O parity")
            if not c16["pass"]:
                raise A.Refusal(f"-O parity did not hold: {c16}.")
        if not all(fired.values()):
            raise A.Refusal("A PLANTED CONTROL DID NOT FIRE: "
                            f"{[c for c in sorted(fired) if not fired[c]]}. REFUSED (rule 3).")
        print(f"ALL REGISTERED CONTROLS FIRED (A's pinned suite, core {CORE_BLOB[:12]}).")
        return 0

    if args.section7_screen:
        if not args.level:
            raise A.Refusal("--section7-screen requires --level.")
        rec = section7_screen_gridb(args.level, args.run_root)
        A._emit({"result": rec, "GRIDB_ORDER_NOTE": GRIDB_ORDER_NOTE, "NOT_CLAIMED": GRIDB_NOT_CLAIMED})
        return 11 if rec["failed_clauses"] else 0

    if args.grade or args.gate_p:
        levels = _discover_levels_gridb(args.run_root)
        for lv, et in zip(levels, GRIDB_END_TIMES):
            cl = A.completion_clauses(lv["case"], et)
            if not cl["ALL"]:
                raise A.Refusal(f"{lv['id']}: rule-4 strict completion FAILED on "
                                f"{[k for k, v in cl.items() if v is False]}. REFUSED (exit 2).")
        _live_plant(levels)                        # rule 3: plant must be seen on real fields
        ref = A.read_case_2308()                   # sha256-REFUSED inside on mismatch
        d1 = A.d1_discriminator(ref)
        cfd_by_level = {}
        for lv, et in zip(levels, GRIDB_END_TIMES):
            sec, _meta = A.cfd_sections_for_case(lv["case"], et, lv["polymesh"])
            cfd_by_level[lv["id"]] = sec
        finest = levels[-1]["id"]

        if args.gate_p:
            p = A.gate_p(ref, cfd_by_level[finest], d1, None, A._verdict("NOT A RESULT"))
            A._emit({"step": "Gate P only", "graded_level": finest, "gate_P": p,
                     "gate_G": "NOT RUN -- Gate P is behind Gate G (label NOT A RESULT).",
                     "GRIDB_ORDER_NOTE": GRIDB_ORDER_NOTE, "NOT_CLAIMED": GRIDB_NOT_CLAIMED})
            return 0

        cds = [os.path.join(lv["case"], "postProcessing", "forceCoeffs", "0", "coefficient.dat")
               for lv in levels]
        logs = [os.path.join(lv["case"], "log.rhoSimpleFoam") for lv in levels]
        g = gate_g_gridb(cds, logs)
        gci, gci_basis = A.gci_fine_from_gate_g(g)
        p = A.gate_p(ref, cfd_by_level[finest], d1, gci, g["gate_G_label"])
        A._emit({"step": "grade", "gate_G": g, "gate_P": p, "graded_level": finest,
                 "gate_P_numerical_band_basis": gci_basis,
                 "GRIDB_ORDER_NOTE": GRIDB_ORDER_NOTE, "NOT_CLAIMED": GRIDB_NOT_CLAIMED})
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except A.Refusal as _exc:
        print(f"REFUSED: {_exc}", file=sys.stderr); sys.exit(2)
    except A.InternalDefect as _exc:
        print(f"INTERNAL DEFECT of the wrapper: {_exc}", file=sys.stderr); sys.exit(70)
    except Exception as _exc:
        import traceback
        traceback.print_exc()
        print(f"INTERNAL DEFECT (unhandled {type(_exc).__name__}): {_exc}", file=sys.stderr)
        sys.exit(70)
