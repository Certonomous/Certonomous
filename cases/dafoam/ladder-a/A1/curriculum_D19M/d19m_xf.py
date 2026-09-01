#!/usr/bin/env python
r"""Curriculum D19M -- THE COMPRESSIBLE ALPHA-MULTIPOINT OPTIMISATION INSTRUMENT.

NACA0012, `DARhoSimpleFoam`, M 0.288, A1's own 4,032-cell mesh, np = 1, BOTH
toolchain rows, weighted objective `J = SUM_i w_i * CD_i(alpha_i)` over ONE
SHARED `shape` vector.

THREE MODES: `O` (the IPOPT optimisation), `XE` (the adjoint AT THE FINAL DESIGN
POINT), `FE` (the FD table AT THE FINAL DESIGN POINT).  Terminal statements
`D19M_O_WRITTEN` / `D19M_X_WRITTEN` / `D19M_F_WRITTEN`.

===========================================================================
WHAT D19O ESTABLISHED, AND WHAT IT DID NOT
===========================================================================
D19O ran the compressible SINGLE-POINT optimisation on this ground and returned
`GATE REACHED` on both rows.  Two of its measurements shape this item and one
does NOT license anything here:

  (1) **A compressible optimiser major on A1 at np = 1 costs ~0.42 core-min** --
      MEASURED twice, `O-S` 5.400/13 = 0.4154 and `O-P` 4.217/10 = 0.4217. This
      item's cost model is anchored on it (PREREGISTRATION.md section 12).

  (2) **At D19O's optimum the SHIPPED and PATCHED rows agreed to 0.0232 % on
      `shape[6]`**, where D15 measured the shipped row 44.8738 % wrong AT THE
      BASELINE. The IDWarp degenerate-rotation branch fires when
      `axisMag = 1e-15 < sqrt(eps)`, certain on an undeformed mesh and false on a
      deformed one.

  (3) **AND THAT IS EXACTLY WHY THIS ITEM STILL RUNS BOTH ROWS.** The rows agree
      AT AN OPTIMUM and diverge AT A BASELINE. Collapsing to one row would bake
      in an agreement that is CONFIGURATION-DEPENDENT and destroy the only
      instrument that can detect it. `DAFOAM_CHARTER.md` section 6 is unmoved:
      a DAFoam verdict is two rows or it is not a verdict about DAFoam.

===========================================================================
`shape[7]` -- THE REGISTRATION IS CARRIED FORWARD UNCHANGED
===========================================================================
D19O MEASURED that `shape[7]`'s |dCD| at its optimum is 5.887e-03 against
2.099e-04 at the baseline -- a factor of 28 -- and that its plateau CLOSES there
(two-sided, coarse 0.974 % / fine 1.061 %).

**THAT DOES NOT LICENSE GRADING IT HERE, AND THIS ITEM DOES NOT.**
`EXCLUDED_FROM_AGGREGATE` still names `("shape", 7)`; `G-PLAT7` still returns
`NOT A RESULT` on both rows, set FROM THE REGISTERED LIST and never from a
measured value.  The reasons, registered before this run:

  * D19O's reading is at D19O's optimum on a SINGLE-POINT objective. This item
    optimises a DIFFERENT objective -- a weighted sum over three alpha -- and
    will reach a DIFFERENT design point. Nothing measured at one optimum is a
    statement about another.
  * The evidence that would let a successor register `shape[7]` as gradable IS
    NOW ON RECORD (`curriculum_D19O/RESULTS.md` section 3.1), and registering it
    IN ADVANCE is what a successor may do. **Promoting it here, after the fact,
    is the move the whole registration exists to prevent.**

===========================================================================
THE ROW IS READ FROM THE TOOLCHAIN'S OWN IDENTITY, NEVER FROM A FLAG
===========================================================================
This instrument md5s the `libidwarp.so` THIS INTERPRETER ACTUALLY IMPORTED, from
inside the container, and maps it to a row.  An md5 matching neither registered
toolchain REFUSES: this producer will not stamp a row it cannot prove.
"""
import hashlib
import json
import os
import sys
import time

ITEM = "D19M"
PRODUCER = "d19m_runScript.py"

# THE PRODUCER IS NEW.  It is NOT byte-identical to D15's and this item makes NO
# header-reproduction claim -- see the producer's own docstring.  What IS asserted
# is the PHYSICS BLOCK, which is byte-identical to D19O's (modulo the `aoa0` line
# a multipoint model cannot carry) and which is delimited in the producer by
# explicit markers so the assertion is on bytes rather than on a line range.
PRODUCER_MD5 = "d1ae2ac5a620d9308b0d50059e944cf4"
PHYSICS_BEGIN = "# ---- D19M_PHYSICS_BEGIN ----\n"
PHYSICS_END = "# ---- D19M_PHYSICS_END ----"
PHYSICS_MD5 = "c66504acc57bd9ef009599e883d2ef3b"

ROW_BY_SO_MD5 = {
    "85f59e87253e0a71a813f64ca6e4c425": "PATCHED",   # dafoam-idwarp-rot:v1
    "f0fcb488e0e98156575cd19548e91663": "SHIPPED",   # dafoam/opt-packages:latest
}
NP_REQUIRED = 1

# ---- the multipoint registration.  MIRRORS the producer and is CHECKED against
# ---- it at runtime: a scenario added in one file and not the other REFUSES.
ALPHAS = [2.787333582, 4.787333582, 6.787333582]
WEIGHTS = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
SCENARIOS = ["point0", "point1", "point2"]
ALPHA_TOL = 1.0e-12          # G-ALPHA: absolute, on the read-back

# ---- the graded components.  FOUR, not D19O's five: `patchV` is NOT a design
# ---- variable in this item, so there is no `patchV[1]` derivative to grade.
COMPONENTS = [("shape", 0), ("shape", 3), ("shape", 6), ("shape", 7)]
EXCLUDED_FROM_AGGREGATE = [("shape", 7)]
EXCLUSION_REASON = (
    "REGISTERED BEFORE THE RUN as a NON-RESULT on the plateau clause, on BOTH "
    "rows, WHATEVER VALUE IT RETURNS -- carried forward UNCHANGED from D19O. "
    "D19R measured `shape[7]/CD` one-sided at 21.060684242435336 % on the fine "
    "side of s*=1e-3 at the BASELINE, and the component changes SIGN between "
    "3e-5 and 1e-5. D19O then measured that at ITS optimum the component is 28x "
    "larger and its plateau CLOSES -- which is evidence for a SUCCESSOR "
    "registration made in advance, NOT licence to grade it here after the fact. "
    "This item optimises a different objective and will reach a different design "
    "point; nothing measured at one optimum is a statement about another.")

S_STAR = {"shape": 1.0e-3}
S_STAR_SOURCE = ("/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-"
                 "subsonic-plateau/d19r_selected_step.json -> s_star.shape")
FD_STEPS_ENDPOINT = {"shape": [1.0e-2, 1.0e-3, 1.0e-4]}   # DECADE, G19R-1b's rule
PLATEAU_TOL_PCT = 10.0
FD_BAND_PCT = 5.0
AGG_BAND_PCT = 5.0
TB_STEP = 1.0e-8
TB_MAX_PASSING = 1
PLANT_K = 5.0
PLANT_K_SHRUNK = 0.5
CTRL_STEP = 1.0e-3

OPTIMIZER = "IPOPT"
OPT_TOL = 1.0e-5
MAX_MAJORS = 40              # a BUDGET, not a settle criterion
EXPECTED_MAJOR_ROWS = 12     # MEASURED: SO-3 multipoint 12 and 10 rows; D19O 13
                             # and 10. PRICING ONLY; it gates nothing.
MP_STRUCT_RTOL = 1.0e-10     # G-MP-STRUCT: dJ/dx == SUM w_i dCD_i/dx

OUT = {"O": "d19m_O.json", "XE": "d19m_X.json", "FE": "d19m_F.json"}
XOPT = "d19m_xopt.json"
MODES = tuple(OUT)
ETA_FLOOR = 1.0e-14

OBJ = "obj.J"
CD_OF = ["%s.aero_post.CD" % s for s in SCENARIOS]
CL_OF = ["%s.aero_post.CL" % s for s in SCENARIOS]


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def idwarp_identity():
    import idwarp
    p = idwarp.__file__
    so = os.path.join(os.path.dirname(p), "libidwarp.so")
    m = md5_of(so)
    return {"idwarp_file": p, "libidwarp_so_md5": m, "row": ROW_BY_SO_MD5.get(m)}


def parse_mode(argv):
    mode = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    if mode not in MODES:
        sys.stderr.write("D19M_XF usage: d19m_xf.py -mode %s\n" % "|".join(MODES))
        sys.exit(64)
    return mode


def plant_relative(d_ref, band_pct, k):
    return k * (band_pct / 100.0) * abs(d_ref)


def is_excluded(dv, idx):
    return (dv, idx) in EXCLUDED_FROM_AGGREGATE


def rel_pct(a, b):
    if b is None or a is None or b == 0.0:
        return None
    return abs(a - b) / abs(b) * 100.0


def weighted_J(cds):
    return sum(w * c for w, c in zip(WEIGHTS, cds))


# ============================================================================
# THE WRITERS.  Every fixture in every selftest of this item comes from these.
# ============================================================================
def build_fd_step(step, Jp, Jm, clp, clm):
    """One central-difference row. `clp`/`clm` are the three-scenario CL lists."""
    dJ = (Jp - Jm) / (2.0 * step)
    dCL = [(a - b) / (2.0 * step) for a, b in zip(clp, clm)]
    ok = all(v == v and abs(v) != float("inf") for v in [dJ] + dCL)
    return {"step": step, "dJ": repr(dJ), "dCL": [repr(v) for v in dCL],
            "J_plus": repr(Jp), "J_minus": repr(Jm),
            "CL_plus": [repr(v) for v in clp], "CL_minus": [repr(v) for v in clm],
            "ok": bool(ok), "is_trivial_baseline": bool(step == TB_STEP)}


def plateau_reading(fd_by_step, dv, key="dJ", scen=None):
    """The DECADE two-sided plateau at s*, G19R-1b's rule verbatim."""
    steps = FD_STEPS_ENDPOINT[dv]
    coarse, centre, fine = steps[0], steps[1], steps[2]

    def val(s):
        r = fd_by_step.get(repr(s))
        if not r or not r.get("ok"):
            return None
        v = r[key]
        return float(v[scen]) if scen is not None else float(v)

    c, m, f = val(coarse), val(centre), val(fine)
    cp, fp = rel_pct(c, m), rel_pct(f, m)
    two = (cp is not None and fp is not None
           and cp <= PLATEAU_TOL_PCT and fp <= PLATEAU_TOL_PCT)
    return {"s_star": centre, "coarse_step": coarse, "fine_step": fine,
            "coarse_pct": cp, "fine_pct": fp,
            "score_pct": max([x for x in (cp, fp) if x is not None], default=None),
            "two_sided": bool(two),
            "rule": "DECADE neighbours, max over both sides, tol %.1f %% -- "
                    "G19R-1b's rule UNCHANGED" % PLATEAU_TOL_PCT}


def row_from_fd(dv, idx, fd):
    """THE SINGLE WRITER FOR A COMPONENT ROW.  Mode FE calls it on the fd dict it
    accumulates; `build_fd_row` calls it too, so they cannot drift."""
    return {"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd,
            "excluded_from_aggregate": is_excluded(dv, idx),
            "registered_non_result": is_excluded(dv, idx),
            "plateau_J": plateau_reading(fd, dv, "dJ"),
            "plateau_CL": [plateau_reading(fd, dv, "dCL", scen=i)
                           for i in range(len(SCENARIOS))]}


def build_fd_row(dv, idx, per_step):
    """per_step maps step -> (Jp, Jm, clp_list, clm_list)."""
    return row_from_fd(dv, idx, {repr(s): build_fd_step(s, *v)
                                 for s, v in per_step.items()})


def build_ctrl_row(J0, cl0, k=PLANT_K, k_shrunk=PLANT_K_SHRUNK, band=FD_BAND_PCT):
    plant = plant_relative(J0, band, k)
    plant_sh = plant_relative(J0, band, k_shrunk)
    moved = abs(plant) / abs(J0) * 100.0
    moved_sh = abs(plant_sh) / abs(J0) * 100.0
    return {"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dJ": repr(0.0),
                          "dCL": [repr(0.0)] * len(SCENARIOS),
                          "J_plus": repr(J0), "J_minus": repr(J0),
                          "CL_plus": [repr(v) for v in cl0],
                          "CL_minus": [repr(v) for v in cl0], "ok": True,
                          "note": "synthetic: identical DVs on both sides -> exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": repr(plant), "K": k, "band_pct": band,
                    "d_ref": repr(J0), "formula": "plant = K * (band/100) * |d_ref|",
                    "moved_pp": repr(moved), "crosses_band": bool(moved > band),
                    "dJ": repr(plant / (2.0 * CTRL_STEP)),
                    "J_plus": repr(J0 + plant), "J_minus": repr(J0), "ok": True},
        "planted_shrunk": {"step": CTRL_STEP, "plant": repr(plant_sh), "K": k_shrunk,
                           "band_pct": band, "moved_pp": repr(moved_sh),
                           "crosses_band": bool(moved_sh > band),
                           "dJ": repr(plant_sh / (2.0 * CTRL_STEP)),
                           "note": "SUFFICIENCY RED LEG -- must NOT cross the band"}}


def aggregate_excl_flagged(pairs):
    import math
    if not pairs:
        return None
    num = math.sqrt(sum((a - f) ** 2 for a, f in pairs))
    den = math.sqrt(sum(f * f for _a, f in pairs))
    return None if den == 0.0 else num / den * 100.0


def _load_producer():
    got = md5_of(PRODUCER)
    if PRODUCER_MD5 != "MD5_PRODUCER_UNSET" and got != PRODUCER_MD5:
        sys.stderr.write("D19M_XF REFUSE producer md5 %s != frozen %s\n" % (got, PRODUCER_MD5))
        sys.exit(2)
    src = open(PRODUCER).read()
    # THE PHYSICS ASSERTION.  This item cannot claim D15's header; it CAN and does
    # claim D19O's physics, on bytes, between explicit markers.
    if src.count(PHYSICS_BEGIN) != 1 or src.count(PHYSICS_END) != 1:
        sys.stderr.write("D19M_XF REFUSE physics markers appear %d/%d times\n"
                         % (src.count(PHYSICS_BEGIN), src.count(PHYSICS_END)))
        sys.exit(2)
    blk = src.split(PHYSICS_BEGIN)[1].split(PHYSICS_END)[0].strip()
    pmd5 = hashlib.md5(blk.encode()).hexdigest()
    if pmd5 != PHYSICS_MD5:
        sys.stderr.write("D19M_XF REFUSE physics block md5 %s != D19O's %s -- the "
                         "physics continuity claim rests on these bytes\n"
                         % (pmd5, PHYSICS_MD5))
        sys.exit(2)
    sys.stdout.write("D19M_PHYSICS_IDENTICAL_TO_D19O md5=%s\n" % pmd5)
    sys.stdout.write("D19M_PRODUCER_IS_NEW md5=%s no_header_reproduction_claim=true\n" % got)
    return got, pmd5


def main():
    mode = parse_mode(sys.argv)
    prod_md5, pmd5 = _load_producer()

    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", OPTIMIZER]
    import runpy
    ns = runpy.run_path(PRODUCER, run_name="d19m_producer")

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    if nprocs != NP_REQUIRED:
        sys.stderr.write("D19M_XF REFUSE np=%d; registered np=%d on EVERY arm.\n"
                         % (nprocs, NP_REQUIRED))
        MPI.COMM_WORLD.Abort(2)

    # THE INSTRUMENT AND THE PRODUCER MUST AGREE ON THE OPERATING POINTS.  A
    # scenario added in one file and not the other is a silent mismatch that
    # would put a gradient against the wrong angle.
    for name, mine, theirs in (("ALPHAS", ALPHAS, ns.get("ALPHAS")),
                               ("WEIGHTS", WEIGHTS, ns.get("WEIGHTS")),
                               ("SCENARIOS", SCENARIOS, ns.get("SCENARIOS"))):
        if list(theirs or []) != list(mine):
            sys.stderr.write("D19M_XF REFUSE %s disagree: instrument %r vs producer %r\n"
                             % (name, mine, theirs))
            MPI.COMM_WORLD.Abort(2)
    sys.stdout.write("D19M_MULTIPOINT_AGREES alphas=%r weights=%r scenarios=%r\n"
                     % (ALPHAS, WEIGHTS, SCENARIOS))

    ident = idwarp_identity()
    if ident["row"] is None:
        sys.stderr.write("D19M_XF REFUSE libidwarp.so md5 %s matches NEITHER registered "
                         "toolchain %r\n" % (ident["libidwarp_so_md5"], sorted(ROW_BY_SO_MD5)))
        MPI.COMM_WORLD.Abort(2)
    row = ident["row"]
    sys.stdout.write("D19M_ROW_FROM_TOOLCHAIN row=%s libidwarp_so_md5=%s imported_from=%s\n"
                     % (row, ident["libidwarp_so_md5"], ident["idwarp_file"]))

    jsonl = OUT[mode].replace(".json", ".jsonl")

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def write_json(path, obj):
        with open(path, "w") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())

    Top = ns["Top"]
    prob = om.Problem()
    prob.model = Top()

    if mode == "O":
        prob.driver = om.pyOptSparseDriver()
        prob.driver.options["optimizer"] = OPTIMIZER
        prob.driver.opt_settings = {
            "tol": OPT_TOL, "constr_viol_tol": OPT_TOL, "max_iter": MAX_MAJORS,
            "print_level": 5, "output_file": "opt_IPOPT.txt",
            "mu_strategy": "adaptive", "limited_memory_max_history": 10,
            "nlp_scaling_method": "none", "alpha_for_y": "full", "recalc_y": "yes"}
        prob.driver.options["debug_print"] = ["nl_cons", "objs", "desvars"]
        prob.driver.options["print_opt_prob"] = True
        prob.driver.hist_file = "OptView.hst"
    prob.setup(mode="rev")

    def read_points():
        cds = [float(prob.get_val(k)[0]) for k in CD_OF]
        cls = [float(prob.get_val(k)[0]) for k in CL_OF]
        return cds, cls

    def read_alphas():
        """G-ALPHA's data: the angles read BACK through the model, both paths."""
        out = []
        for i, sc in enumerate(SCENARIOS):
            a_dv = float(np.array(prob.get_val("patchV%d" % i)).ravel()[1])
            try:
                a_sc = float(np.array(prob.get_val("%s.patchV" % sc)).ravel()[1])
            except Exception:                                     # noqa: BLE001
                a_sc = None
            out.append({"scenario": sc, "registered": ALPHAS[i],
                        "read_dvs": a_dv, "read_scenario": a_sc,
                        "abs_err_dvs": abs(a_dv - ALPHAS[i]),
                        "abs_err_scenario": (None if a_sc is None
                                             else abs(a_sc - ALPHAS[i]))})
        return out

    emit({"kind": "identity", "item": ITEM, "mode": mode, "row": row, "nprocs": nprocs,
          "producer_md5": prod_md5, "physics_md5": pmd5,
          "alphas": ALPHAS, "weights": WEIGHTS, "scenarios": SCENARIOS,
          "solverName": ns["daOptions"].get("solverName"),
          "primalMinResTol": ns["daOptions"].get("primalMinResTol"),
          "U0": ns.get("U0"), "T0": ns.get("T0"), "p0": ns.get("p0"), **ident})

    # ======================= mode O: the optimisation =========================
    if mode == "O":
        b0 = np.array(prob.get_val("shape"), dtype=float).copy()
        t0 = time.time()
        prob.run_model()
        cds_b, cls_b = read_points()
        J_b = weighted_J(cds_b)
        alph = read_alphas()
        emit({"kind": "baseline", "J": repr(J_b), "CD": [repr(v) for v in cds_b],
              "CL": [repr(v) for v in cls_b], "alphas_read": alph,
              "wall_s": round(time.time() - t0, 3)})

        t0 = time.time()
        fail = prob.run_driver()
        opt_s = time.time() - t0
        cds_f, cls_f = read_points()
        J_f = weighted_J(cds_f)
        xopt = np.array(prob.get_val("shape"), dtype=float).copy()

        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import d19m_stall as STALL
        log = "opt_IPOPT.txt"
        L = STALL.read_log(log) if os.path.isfile(log) else {
            "n_rows": 0, "convergence": {"exit": None, "n_iterations": None,
                                         "converged": False},
            "stall": STALL.stall_reach([]), "cutbacks": {}}

        if rank == 0:
            red = (J_b - J_f) / J_b * 100.0 if J_b else None
            write_json(OUT["O"], {
                "item": ITEM, "mode": "O", "row": row, "nprocs": nprocs,
                "producer_md5": prod_md5, "physics_md5": pmd5, "identity": ident,
                "alphas": ALPHAS, "weights": WEIGHTS, "scenarios": SCENARIOS,
                "alphas_read_back": alph,
                "optimizer": OPTIMIZER, "opt_tol": OPT_TOL,
                "max_iter_registered": MAX_MAJORS,
                "expected_major_rows_for_pricing_only": EXPECTED_MAJOR_ROWS,
                "driver_fail_flag": bool(fail),
                "J_baseline": repr(J_b), "J_final": repr(J_f),
                "CD_baseline": [repr(v) for v in cds_b],
                "CD_final": [repr(v) for v in cds_f],
                "CL_baseline": [repr(v) for v in cls_b],
                "CL_final": [repr(v) for v in cls_f],
                "_CL_triple_travels": "CL is UNCONSTRAINED in this item (alpha is the "
                                      "operating point, so there is no DV to trim with). "
                                      "The THREE-CL TRIPLE therefore travels with every "
                                      "drag number this item publishes. A weighted-drag "
                                      "reduction at unstated lift is not a reportable "
                                      "number.",
                "weighted_drag_reduction_pct": repr(red) if red is not None else None,
                "_reduction_is_not_a_verdict":
                    "DAFOAM_CHARTER.md section 9 FORBIDS grading an optimisation by the "
                    "size of its improvement. This number is reported; it grades nothing.",
                "ipopt_exit": L["convergence"]["exit"],
                "ipopt_n_iterations": L["convergence"]["n_iterations"],
                "ipopt_printed_convergence": L["convergence"]["converged"],
                "ipopt_table_rows": L["n_rows"],
                "stall": L["stall"], "cutbacks": L["cutbacks"],
                "wall_s_optimiser": round(opt_s, 3),
                "dv_initial": [repr(float(v)) for v in b0],
                "dv_final": [repr(float(v)) for v in xopt],
                "excluded_from_aggregate": [[d, i] for d, i in EXCLUDED_FROM_AGGREGATE],
                "excluded_from_aggregate_reason": EXCLUSION_REASON,
                "inherits_unverified_gradient": True,
                "_inherits_unverified_gradient_why":
                    "The compressible gradient basis has NO GRADED VERDICT (D19R's "
                    "grader refused rc=2; D19R2 grading attempt 1 = NOT A RESULT) and "
                    "D19R's plateau did not close on shape[7]. FURTHERMORE the "
                    "MULTIPOINT objective J has NEVER had an FD table on compressible "
                    "ground at all -- this item's own FE arms are the first."})
            write_json(XOPT, {
                "item": ITEM, "row": row, "producer_md5": prod_md5,
                "shape": [repr(float(v)) for v in xopt],
                "J_final": repr(J_f), "CL_final": [repr(v) for v in cls_f],
                "ipopt_printed_convergence": L["convergence"]["converged"],
                "_what_this_is": "THE FINAL DESIGN POINT. The endpoint arms XE and FE "
                                 "read it and evaluate AT IT (DAFOAM_CHARTER.md "
                                 "section 9)."})
            sys.stdout.write("D19M_O_WRITTEN %s rows=%d exit=%r converged=%s\n"
                             % (OUT["O"], L["n_rows"], L["convergence"]["exit"],
                                L["convergence"]["converged"]))
        MPI.COMM_WORLD.Barrier()
        return

    # =============== modes XE / FE: AT THE FINAL DESIGN POINT =================
    if not os.path.isfile(XOPT):
        sys.stderr.write("D19M_XF REFUSE mode %s needs %s from arm O -- an endpoint "
                         "check at the BASELINE is what DAFOAM_CHARTER.md section 9 "
                         "forbids.\n" % (mode, XOPT))
        MPI.COMM_WORLD.Abort(2)
    xo = json.load(open(XOPT))
    if xo.get("row") != row:
        sys.stderr.write("D19M_XF REFUSE %s was written on row %r; this arm is on row "
                         "%r.\n" % (XOPT, xo.get("row"), row))
        MPI.COMM_WORLD.Abort(2)
    base = np.array([float(v) for v in xo["shape"]], dtype=float)
    if int(np.array(prob.get_val("shape")).size) != base.size:
        sys.stderr.write("D19M_XF REFUSE shape length %d in %s but %d in the model\n"
                         % (base.size, XOPT, int(np.array(prob.get_val("shape")).size)))
        MPI.COMM_WORLD.Abort(2)
    prob.set_val("shape", base.copy())
    alph = read_alphas()
    emit({"kind": "design_point_record", "source": XOPT,
          "shape": [repr(float(v)) for v in base], "alphas_read": alph})

    def evaluate(tag):
        t0 = time.time()
        prob.run_model()
        cds, cls = read_points()
        J = weighted_J(cds)
        emit({"kind": "evaluation", "tag": tag, "J": repr(J),
              "CD": [repr(v) for v in cds], "CL": [repr(v) for v in cls],
              "wall_s": round(time.time() - t0, 3)})
        return J, cds, cls

    def set_perturbed(idx, delta):
        v = base.copy()
        v[idx] += delta
        prob.set_val("shape", v)

    J0, cd0, cl0 = evaluate("endpoint_baseline")

    # ======================= mode XE: the adjoint =============================
    if mode == "XE":
        t0 = time.time()
        totals = prob.compute_totals(of=[OBJ] + CD_OF + CL_OF, wrt=["shape"])
        emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})

        def arr(of):
            return [float(v) for v in
                    np.atleast_1d(np.array(totals[(of, "shape")]).ravel())]
        dJ = arr(OBJ)
        dCD = [arr(k) for k in CD_OF]
        dCL = [arr(k) for k in CL_OF]
        # G-MP-STRUCT: dJ/dx must equal SUM_i w_i dCD_i/dx from the artefact's OWN
        # components.  This is what makes J a statement about one design vector.
        recon = [sum(WEIGHTS[i] * dCD[i][k] for i in range(len(SCENARIOS)))
                 for k in range(len(dJ))]
        worst = max((abs(a - b) / abs(a) if a != 0 else abs(a - b))
                    for a, b in zip(dJ, recon)) if dJ else None
        if rank == 0:
            write_json(OUT["XE"], {
                "item": ITEM, "mode": "XE", "row": row, "nprocs": nprocs,
                "producer_md5": prod_md5, "physics_md5": pmd5, "identity": ident,
                "alphas": ALPHAS, "weights": WEIGHTS, "scenarios": SCENARIOS,
                "alphas_read_back": alph,
                "at_design_point": XOPT, "design_point": {"shape": xo["shape"]},
                "J_at_design_point": repr(J0),
                "CD_at_design_point": [repr(v) for v in cd0],
                "CL_at_design_point": [repr(v) for v in cl0],
                "adjoint": {"J": [repr(v) for v in dJ],
                            "CD": [[repr(v) for v in a] for a in dCD],
                            "CL": [[repr(v) for v in a] for a in dCL]},
                "mp_struct": {"reconstructed_J": [repr(v) for v in recon],
                              "worst_rel": worst, "rtol": MP_STRUCT_RTOL,
                              "note": "dJ/dx vs SUM_i w_i dCD_i/dx, from this "
                                      "artefact's OWN components"},
                "no_optimiser_ran": True,
                "excluded_from_aggregate": [[d, i] for d, i in EXCLUDED_FROM_AGGREGATE],
                "excluded_from_aggregate_reason": EXCLUSION_REASON})
            sys.stdout.write("D19M_X_WRITTEN %s mp_struct_worst_rel=%r\n"
                             % (OUT["XE"], worst))
        MPI.COMM_WORLD.Barrier()
        return

    # ======================= mode FE: the endpoint FD table ===================
    J0r, _cd0r, _cl0r = evaluate("endpoint_baseline_repeat")
    eta_raw = abs(J0 - J0r)
    eta_flag = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flag else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flag,
          "note": "SAME-MESH rerun determinism of J AT THE OPTIMUM. The WEAKEST "
                  "bound available; it is not the perturbed-mesh noise."})

    declared, rows, failures = 2, [], []
    for dv, idx in COMPONENTS:
        if idx >= base.size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": int(base.size), "fd": {}})
            continue
        fd = {}
        for s in list(FD_STEPS_ENDPOINT[dv]) + [TB_STEP]:
            declared += 2
            try:
                set_perturbed(idx, +s)
                Jp, _cdp, clp = evaluate("shape[%d]+%g" % (idx, s))
                set_perturbed(idx, -s)
                Jm, _cdm, clm = evaluate("shape[%d]-%g" % (idx, s))
                fd[repr(s)] = build_fd_step(s, Jp, Jm, clp, clm)   # THE WRITER
                if not fd[repr(s)]["ok"]:
                    failures.append({"dv": dv, "idx": idx, "step": s,
                                     "reason": "non-finite estimate"})
            except Exception as exc:                              # noqa: BLE001
                fd[repr(s)] = {"step": s, "ok": False, "error": repr(exc)[:400],
                               "is_trivial_baseline": bool(s == TB_STEP)}
                failures.append({"dv": dv, "idx": idx, "step": s,
                                 "reason": repr(exc)[:200]})
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[repr(s)]})
        rows.append(row_from_fd(dv, idx, fd))                     # THE SINGLE WRITER
    prob.set_val("shape", base.copy())

    ctrl = build_ctrl_row(J0, cl0)                                # THE WRITER
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        seen_zero = seen_plant = seen_shrunk = None
        with open(jsonl) as fh:
            for line in fh:
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    r = rec["row"]
                    seen_zero = float(r["fd"][repr(CTRL_STEP)]["dJ"])
                    seen_plant = float(r["planted"]["dJ"])
                    seen_shrunk = float(r["planted_shrunk"]["dJ"])
        plant = plant_relative(J0, FD_BAND_PCT, PLANT_K)
        plant_sh = plant_relative(J0, FD_BAND_PCT, PLANT_K_SHRUNK)
        want, want_sh = plant / (2.0 * CTRL_STEP), plant_sh / (2.0 * CTRL_STEP)
        moved = abs(plant) / abs(J0) * 100.0
        moved_sh = abs(plant_sh) / abs(J0) * 100.0
        if (seen_zero != 0.0 or seen_plant is None
                or abs(seen_plant - want) > 1e-12 * abs(want)
                or seen_shrunk is None
                or abs(seen_shrunk - want_sh) > 1e-12 * abs(want_sh)):
            sys.stderr.write("D19M_XF REFUSE planted-zero control not seen on read-back: "
                             "zero=%r plant=%r want=%r\n" % (seen_zero, seen_plant, want))
            sys.exit(2)
        if not moved > FD_BAND_PCT:
            sys.stderr.write("D19M_XF REFUSE plant at K=%r moves %.4f pp and does NOT "
                             "cross the %.1f pp band -- the SO-2M failure\n"
                             % (PLANT_K, moved, FD_BAND_PCT))
            sys.exit(2)
        if moved_sh > FD_BAND_PCT:
            sys.stderr.write("D19M_XF REFUSE shrunken plant at K=%r DOES cross the band\n"
                             % PLANT_K_SHRUNK)
            sys.exit(2)
        sys.stdout.write("D19M_PLANTED_CONTROL_SEEN zero=%r K=%r moved=%.4f pp CROSSES | "
                         "K_shrunk=%r moved=%.4f pp DOES NOT CROSS (band %.1f pp)\n"
                         % (seen_zero, PLANT_K, moved, PLANT_K_SHRUNK, moved_sh,
                            FD_BAND_PCT))
        write_json(OUT["FE"], {
            "item": ITEM, "mode": "FE", "row": row, "nprocs": nprocs,
            "producer_md5": prod_md5, "physics_md5": pmd5, "identity": ident,
            "alphas": ALPHAS, "weights": WEIGHTS, "scenarios": SCENARIOS,
            "alphas_read_back": alph,
            "at_design_point": XOPT, "design_point": {"shape": xo["shape"]},
            "J_at_design_point": repr(J0), "J_at_design_point_repeat": repr(J0r),
            "CD_at_design_point": [repr(v) for v in cd0],
            "CL_at_design_point": [repr(v) for v in cl0],
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flag,
            "components_requested": [[d, i] for d, i in COMPONENTS],
            "steps_endpoint": FD_STEPS_ENDPOINT, "s_star": S_STAR,
            "s_star_source": S_STAR_SOURCE,
            "trivial_baseline_step": TB_STEP, "tb_max_passing": TB_MAX_PASSING,
            "plateau_tol_pct": PLATEAU_TOL_PCT, "fd_band_pct": FD_BAND_PCT,
            "agg_band_pct": AGG_BAND_PCT,
            "evaluations_declared": declared, "evaluations_failed": len(failures),
            "evaluation_failures": failures,
            "primals_per_evaluation": len(SCENARIOS),
            "ctrl_step": CTRL_STEP, "plant": repr(plant), "plant_K": PLANT_K,
            "plant_moved_pp": repr(moved), "plant_moved_pp_shrunk": repr(moved_sh),
            "rows": rows, "n_rows": len(rows),
            "contains_adjoint": False, "no_optimiser_ran": True,
            "excluded_from_aggregate": [[d, i] for d, i in EXCLUDED_FROM_AGGREGATE],
            "excluded_from_aggregate_reason": EXCLUSION_REASON})
        sys.stdout.write("D19M_F_WRITTEN %s n_rows=%d evals_declared=%d evals_failed=%d "
                         "primals=%d\n" % (OUT["FE"], len(rows), declared, len(failures),
                                           declared * len(SCENARIOS)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
