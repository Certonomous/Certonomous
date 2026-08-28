#!/usr/bin/env python
"""Curriculum SO-2a -- NACA0012, THE GEOMETRIC CONSTRAINT FAMILY (thickness /
volume / LE-radius) of Sanaa's shape-optimisation ladder: the FD-VERIFIED
CONSTRAINT-GRADIENT rung, rung 1 of the SO-2 constraint-family ladder.

DERIVED FROM `curriculum_SO1a/so1a_xf.py` (md5 f34bd5bf550786ff926aed81b342cced)
with EXACTLY these registered deltas and no other
(`so2a_xg_DELTAS_from_so1a_xf.diff`):

  * THE GRADED QUANTITIES ARE THE THREE GEOMETRIC CONSTRAINTS the tutorial's own
    `runScript.py` declares -- `geometry.thickcon`, `geometry.volcon`,
    `geometry.rcon` (:152-155, :176-178) -- not `CD`/`CL`.  SO-1a verified the
    OBJECTIVE gradient and the LIFT-EQUALITY gradient and said in its own scope
    limits that *"nothing about the thickness, volume or LE-radius constraints
    the tutorial also declares ... they belong to SO-2"*.  This is that item.
    `DAFOAM_CHARTER.md` section 2 forbids an optimisation driven by a gradient
    with no FD table beside it, so this rung is the precondition for ANY SO-2
    optimisation rung that carries a geometric constraint.

  * THE CONSTRAINT OUTPUTS ARE VECTORS, so every FD row records the FULL vector
    on each side and the FULL central-difference vector.  The Jacobian is graded
    PER (constraint, output index, DV index) PAIR.

  * NO STEP-BASED TRIVIAL BASELINE IS WRITTEN, AND THAT IS A REGISTERED
    DECISION, NOT AN OMISSION.  SO-1a's `TB_STEPS` (h = 1e-8) is wrong FOR ITS
    QUANTITY -- a flow functional whose repeatability eta is 1.3e-10 -- and is
    NOT wrong for THIS one: a geometric constraint is produced by pyGeo
    deterministically from the shape DV with NO iterative solve, so it is
    bit-repeatable and h = 1e-8 does NOT enter the subtractive-cancellation
    regime.  A step too LARGE is equally unavailable: `A_stepsize_study.md`
    measured the primal FAILING at h = 5e-2 and 1e-1 on this very case, so the
    probe would return an exception rather than a reading, and an errored probe
    is not a baseline.  The registered trivial baseline for this item is
    therefore a CYCLIC-SHIFT (wrong-component) baseline computed BY THE GRADER
    from this artefact at zero extra cost -- see PREREGISTRATION.md section 3,
    gate G-TB.  It costs 10 primals fewer than SO-1a's.

  * `patchV` IS PERTURBED ON PURPOSE, to buy the FD side of gate G-STRUCT:
    a geometric constraint is a function of the SHAPE alone, so
    d(constraint)/d(patchV) must be EXACTLY 0.0 on BOTH the adjoint and the FD
    side.  That gate reads a ZERO, which is precisely the reading rule 3 exists
    to distrust, so it is composed ONLY after the planted control has shown the
    same reader seeing a NON-zero in the same run.

  * ARTEFACT CONSTRUCTION IS FACTORED INTO `build_X_record` /
    `build_F_record` / `write_artefact`, WHICH `main()` USES AND THE
    COMPARATOR'S SELFTEST IMPORTS AND DRIVES.  Sanaa's birth requirement,
    2026-08-28, verbatim: *"A planted control must travel the real production
    path -- written by the real producer's code, read through the real reader"*.
    SO-1a's selftest wrote its F fixture with an INLINE `json.dump` of a
    hand-written dict, so a key this instrument renamed would have left the
    fixture passing and the reader blind -- the schema-divergence failure named
    in that directive.  Nothing in this module imports mpi4py, openmdao or
    dafoam at module scope, so the writers are importable on the host WITHOUT
    the container, which is what makes the requirement dischargeable at all.

  * Printed tokens SO1A_* -> SO2A_*; artefact names so1a_* -> so2a_*.
  * The two-primal eta measurement, the CTRL planted-zero component with its
    disk read-back refusal, the emit/fsync discipline, the producer-md5 refusal
    and the MPI rank-0 file rule are SO-1a's / D15's / D5's / D4's bytes.

DAFOAM_CHARTER.md section 2: an adjoint gradient is not a result until an FD
table stands beside it.  Section 3: the step is proved to lie in the plateau.
Section 4: the gate names its trivial baseline BEFORE its own run.  Section 5:
serial before parallel.  Section 6: two rows, identity by hash.  All five are
instrumented here.
"""

import hashlib
import json
import os
import sys
import time

PRODUCER = "so2a_runScript.py"
PRODUCER_MD5 = "0557da51f6f179f6de865144343c499f"
ANCHOR = "# OpenMDAO setup"
ITEM = "SO2a"

# ---- registered constants (PREREGISTRATION.md section 3) --------------------
ETA_FLOOR = 1.0e-14
# The three geometric constraints the PRODUCER itself declares.  Names are the
# OpenMDAO paths; short keys are what the artefact and the grader use.
CONSTRAINTS = (("thickcon", "geometry.thickcon"),
               ("volcon", "geometry.volcon"),
               ("rcon", "geometry.rcon"))
# The sizes IMPLIED BY THE PRODUCER'S OWN CALL ARGUMENTS, not by a guess about
# pyGeo internals: `nom_addThicknessConstraints2D("thickcon", ..., nSpan=2,
# nChord=10)` -> 20; `nom_addVolumeConstraint("volcon", ...)` -> 1;
# `nom_addLERadiusConstraints("rcon", leList, 2, ...)` -> nSpan = 2 -> 2.
# The instrument RECORDS the sizes it actually finds; the grader compares them
# against these and GATE FAILs on a mismatch (G-CDIM) rather than refusing, so
# a layout surprise does not corrupt the gradient grading.
CON_SIZES_EXPECTED = {"thickcon": 20, "volcon": 1, "rcon": 2}

STEPS = {
    "shape":  [1.0e-2, 1.0e-3, 1.0e-4],     # registered step set, FFD y-displacement units
    "patchV": [1.0e-1, 1.0e-2, 1.0e-3],     # registered step set, degrees of aoa
}
# The REGISTERED DV SUBSET, named in advance.  The four `shape` components are
# SO-1a's, so the two items' readings sit on the same components; `patchV[1]`
# is the angle of attack and is here to buy the FD side of G-STRUCT, whose
# registered value is EXACTLY ZERO.
COMPONENTS = [
    ("shape", 0),
    ("shape", 3),
    ("shape", 6),
    ("shape", 7),
    ("patchV", 1),
]
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03            # rule 3

OUT_X = "so2a_X.json"
OUT_F = "so2a_F.json"
JSONL_F = "so2a_F.jsonl"
JSONL_X = "so2a_X.jsonl"
TERMINAL_X = "SO2A_X_WRITTEN"
TERMINAL_F = "SO2A_F_WRITTEN"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def idwarp_identity():
    try:
        import idwarp
        p = idwarp.__file__
        so = os.path.join(os.path.dirname(p), "libidwarp.so")
        return {"idwarp_file": p, "libidwarp_so_md5": md5_of(so)}
    except Exception as exc:                                  # noqa: BLE001
        return {"idwarp_file": None, "libidwarp_so_md5": None, "error": repr(exc)[:200]}


def case_write_compression():
    """Read `writeCompression` from THE CASE'S OWN system/controlDict.

    AV-1 and AV-2 both returned NOT A RESULT because a frozen comparator pinned
    the age-guard datum to the NAME `0/U` while `writeCompression on` rewrites
    it as `0/U.gz` on a serial arm.  SO-1a's five arms MEASURED the consequence
    (four solver arms resolved to the compressed twin, MESH to the plain name);
    the setting is a recorded datum of the run, never an assumption of a reader.
    """
    p = os.path.join("system", "controlDict")
    try:
        for line in open(p, errors="replace"):
            s = line.strip()
            if s.startswith("writeCompression"):
                return {"write_compression": s.rstrip(";").split()[-1],
                        "write_compression_source": os.path.abspath(p)}
    except OSError as exc:                                    # noqa: BLE001
        return {"write_compression": None, "write_compression_source": None,
                "write_compression_error": repr(exc)[:200]}
    return {"write_compression": None, "write_compression_source": os.path.abspath(p),
            "write_compression_error": "key absent from controlDict"}


# ===================== THE ARTEFACT WRITERS ===================================
# These four functions ARE the production write path.  `main()` calls them and
# NOTHING ELSE writes an artefact.  The comparator's selftest IMPORTS AND CALLS
# THEM to build every fixture, so a fixture cannot carry a key this instrument
# does not emit and cannot miss a key it does -- Sanaa's birth requirement,
# 2026-08-28.  They take plain Python floats and lists and import nothing, so
# they run on the host without DAFoam, which is what makes the requirement
# dischargeable without a container.

def con_vector(values):
    """One constraint output vector, as the artefact stores it: `repr` strings,
    so the artefact is exact and the reader's float() is the only conversion."""
    return [repr(float(v)) for v in values]


def build_fd_row(step, plus, minus):
    """One central-difference entry.  `plus` / `minus` are {short_name: [floats]}
    and the derivative vectors are computed HERE -- the grader never re-derives
    them, it reads what the producer wrote."""
    d = {}
    for name, _ in CONSTRAINTS:
        p, m = list(plus[name]), list(minus[name])
        d[name] = con_vector([(float(a) - float(b)) / (2.0 * step) for a, b in zip(p, m)])
    return {"step": step, "ok": True, "d": d,
            "plus": {n: con_vector(plus[n]) for n, _ in CONSTRAINTS},
            "minus": {n: con_vector(minus[n]) for n, _ in CONSTRAINTS}}


def build_fd_row_failed(step, error):
    return {"step": step, "ok": False, "error": str(error)[:400]}


def build_ctrl_row(base_values):
    """The rule-3 PLANTED-ZERO CONTROL COMPONENT.  Synthetic, no solve.

    `fd`      -- identical values on both sides -> derivative EXACTLY 0.0 in
                 every entry of every constraint.  This is the ZERO the reader
                 must be able to read.
    `planted` -- entry 0 of every constraint moved by PLANT on the plus side
                 alone -> derivative EXACTLY PLANT/(2*CTRL_STEP) there and 0.0
                 elsewhere.  This is the NON-ZERO the same reader must be able
                 to see, through the same keys, on the same path.

    A control that empties the tuple it tests certifies blindness.  This one
    changes a VALUE inside a tuple the reader must traverse in full, and both
    the instrument (below, on disk read-back) and the comparator re-read it.
    """
    zero_plus = {n: list(base_values[n]) for n, _ in CONSTRAINTS}
    zero_minus = {n: list(base_values[n]) for n, _ in CONSTRAINTS}
    plant_plus = {}
    for n, _ in CONSTRAINTS:
        v = list(base_values[n])
        v[0] = float(v[0]) + PLANT
        plant_plus[n] = v
    return {"dv": "CTRL", "idx": 0, "status": "CONTROL",
            "fd": {repr(CTRL_STEP): build_fd_row(CTRL_STEP, zero_plus, zero_minus)},
            "planted": build_fd_row(CTRL_STEP, plant_plus, zero_minus),
            "plant": PLANT,
            "note": ("synthetic, no solve: `fd` has identical DVs on both sides so every "
                     "derivative entry is exactly 0.0; `planted` moves entry 0 of every "
                     "constraint by PLANT on the plus side alone so that entry is exactly "
                     "PLANT/(2*step) and the rest are still exactly 0.0")}


def build_X_record(nprocs, producer_md5, identity, con_base, con_sizes, jac,
                   cd_baseline, cl_baseline, totals_wall_s=None):
    """The X (adjoint / total-derivative) artefact.

    `jac[short_name][dv]` is a FLAT list of repr strings, row-major over
    (output index, dv index), with the 2-D shape recorded beside it so the
    reader never has to infer a layout."""
    return {"item": ITEM, "mode": "X", "producer_md5": producer_md5, "nprocs": nprocs,
            "identity": identity,
            "constraints": [n for n, _ in CONSTRAINTS],
            "constraint_sizes": dict(con_sizes),
            "constraint_baseline": {n: con_vector(con_base[n]) for n, _ in CONSTRAINTS},
            "jacobian": jac,
            "jacobian_shapes": {n: {dv: [int(con_sizes[n]), int(len(jac[n][dv]) // max(1, con_sizes[n]))]
                                    for dv in ("shape", "patchV")} for n, _ in CONSTRAINTS},
            "CD_baseline": repr(float(cd_baseline)), "CL_baseline": repr(float(cl_baseline)),
            "compute_totals_wall_s": totals_wall_s,
            "reported_not_gated": ("CD_baseline and CL_baseline are RECORDED for continuity "
                                   "with SO-1a and are NOT gated by this item")}


def build_F_record(nprocs, producer_md5, identity, con_base, con_base_repeat, con_sizes,
                   rows, eta_raw, eta_used, eta_floored, cd_baseline, cl_baseline,
                   baseline_dvs):
    """The F (finite-difference) artefact."""
    return {"item": ITEM, "mode": "F", "producer_md5": producer_md5, "nprocs": nprocs,
            "identity": identity,
            "constraints": [n for n, _ in CONSTRAINTS],
            "constraint_sizes": dict(con_sizes),
            "constraint_baseline": {n: con_vector(con_base[n]) for n, _ in CONSTRAINTS},
            "constraint_baseline_repeat": {n: con_vector(con_base_repeat[n]) for n, _ in CONSTRAINTS},
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": STEPS, "ctrl_step": CTRL_STEP, "plant": PLANT,
            "tb_steps": None,
            "tb_note": ("NO STEP-BASED TRIVIAL BASELINE IS BOUGHT AND THAT IS REGISTERED: "
                        "a geometric constraint is bit-repeatable (no iterative solve) so a "
                        "step too SMALL does not enter subtractive cancellation, and "
                        "A_stepsize_study.md measured the primal FAILING at h = 5e-2 and "
                        "1e-1 so a step too LARGE returns an exception, not a reading.  The "
                        "registered trivial baseline is the grader's CYCLIC-SHIFT "
                        "wrong-component baseline, G-TB."),
            "CD_baseline": repr(float(cd_baseline)), "CL_baseline": repr(float(cl_baseline)),
            "eta_raw": repr(float(eta_raw)), "eta_used": repr(float(eta_used)),
            "eta_floored": bool(eta_floored),
            "baseline_dvs": baseline_dvs,
            "rows": rows, "n_rows": len(rows)}


def write_artefact(path, rec, terminal, extra=""):
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("%s %s%s\n" % (terminal, path, extra))


# ===================== the run ================================================
def parse_mode(argv):
    mode = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    if mode not in ("X", "F"):
        sys.stderr.write("SO2A_XG usage: so2a_xg.py -mode X|F\n")
        sys.exit(64)
    return mode


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("SO2A_XG REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("SO2A_XG REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "so2a_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    jsonl = JSONL_F if mode == "F" else JSONL_X

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    ident.update(case_write_compression())
    emit({"kind": "identity", "item": ITEM, "mode": mode, "nprocs": nprocs,
          "producer_md5": got, "solverName": ns["daOptions"].get("solverName"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "CL_target": ns.get("CL_target"),
          "p0": ns.get("p0"), **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    base = {"shape": np.array(prob.get_val("shape"), dtype=float).copy(),
            "patchV": np.array(prob.get_val("patchV"), dtype=float).copy()}
    baseline_dvs = {"shape": [repr(float(v)) for v in base["shape"]],
                    "patchV": [repr(float(v)) for v in base["patchV"]]}
    emit({"kind": "baseline_dvs", "n_shape": int(base["shape"].size),
          "n_patchV": int(base["patchV"].size), **baseline_dvs})

    CD = "scenario1.aero_post.CD"
    CL = "scenario1.aero_post.CL"

    def read_constraints():
        out = {}
        for short, path in CONSTRAINTS:
            out[short] = [float(v) for v in np.atleast_1d(np.array(prob.get_val(path)).ravel())]
        return out

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        cv = read_constraints()
        cd = float(prob.get_val(CD)[0])
        cl = float(prob.get_val(CL)[0])
        emit({"kind": "primal", "tag": tag, "CD": repr(cd), "CL": repr(cl),
              "constraints": {n: con_vector(cv[n]) for n, _ in CONSTRAINTS},
              "wall_s": round(time.time() - t0, 3)})
        return cv, cd, cl

    cv0, cd0, cl0 = primal("baseline")
    con_sizes = {n: len(cv0[n]) for n, _ in CONSTRAINTS}
    emit({"kind": "constraint_sizes", "measured": con_sizes, "expected": CON_SIZES_EXPECTED,
          "note": "sizes are RECORDED here; G-CDIM in the grader compares them"})

    if mode == "X":
        t0 = time.time()
        of = [p for _, p in CONSTRAINTS]
        totals = prob.compute_totals(of=of, wrt=["shape", "patchV"])
        tw = round(time.time() - t0, 3)
        emit({"kind": "compute_totals", "of": of, "wall_s": tw})
        jac = {}
        for short, path in CONSTRAINTS:
            jac[short] = {}
            for dv in ("shape", "patchV"):
                arr = np.atleast_2d(np.array(totals[(path, dv)]))
                flat = [repr(float(v)) for v in arr.ravel()]
                jac[short][dv] = flat
                emit({"kind": "jacobian", "of": short, "dv": dv,
                      "shape": [int(arr.shape[0]), int(arr.shape[1])], "values": flat})
        if rank == 0:
            rec = build_X_record(nprocs, got, ident, cv0, con_sizes, jac, cd0, cl0, tw)
            write_artefact(OUT_X, rec, TERMINAL_X)
        MPI.COMM_WORLD.Barrier()
        return

    # ---- mode F: eta on the CONSTRAINT VALUES, then central differences --------
    cv0r, cd0r, cl0r = primal("baseline_repeat")
    eta_raw = 0.0
    for n, _ in CONSTRAINTS:
        for a, b in zip(cv0[n], cv0r[n]):
            eta_raw = max(eta_raw, abs(float(a) - float(b)))
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged,
          "note": ("eta is the worst-entry repeatability of the CONSTRAINT VALUES across two "
                   "baseline primals.  A geometric constraint is produced by pyGeo from the "
                   "shape DV with no iterative solve, so eta is EXPECTED to be 0.0 exactly "
                   "and floored -- and that expectation is exactly why this item's trivial "
                   "baseline cannot be a step too small (see tb_note)")})

    def set_perturbed(dv, idx, delta):
        for k in ("shape", "patchV"):
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    rows = []
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT",
                         "n_available": int(base[dv].size), "fd": {}})
            continue
        fd = {}
        for s in STEPS[dv]:
            key = repr(s)
            try:
                set_perturbed(dv, idx, +s)
                cvp, _, _ = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cvm, _, _ = primal("%s[%d]-%g" % (dv, idx, s))
                fd[key] = build_fd_row(s, cvp, cvm)
            except Exception as exc:                      # noqa: BLE001
                fd[key] = build_fd_row_failed(s, repr(exc))
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd})
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())

    ctrl = build_ctrl_row(cv0)
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        # READ BACK FROM DISK what was just emitted; refuse if the plant is invisible.
        # The read-back traverses the SAME keys the comparator's reader traverses.
        seen_zero, seen_plant = None, None
        with open(jsonl) as fh:
            for line in fh:
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    r = rec["row"]
                    seen_zero = [float(v) for n, _ in CONSTRAINTS
                                 for v in r["fd"][repr(CTRL_STEP)]["d"][n]]
                    seen_plant = [float(r["planted"]["d"][n][0]) for n, _ in CONSTRAINTS]
        want = PLANT / (2.0 * CTRL_STEP)
        bad = (seen_zero is None or seen_plant is None
               or any(v != 0.0 for v in seen_zero)
               or len(seen_plant) != len(CONSTRAINTS)
               or any(abs(v - want) > 1e-12 * abs(want) for v in seen_plant))
        if bad:
            sys.stderr.write("SO2A_XG REFUSE planted-zero control not seen on read-back: "
                             "n_zero=%r zero_max=%r plant=%r want=%r\n"
                             % (None if seen_zero is None else len(seen_zero),
                                None if seen_zero is None else max(abs(v) for v in seen_zero),
                                seen_plant, want))
            sys.exit(2)
        sys.stdout.write("SO2A_PLANTED_ZERO_CONTROL_SEEN n_zero_entries=%d plant=%r want=%r\n"
                         % (len(seen_zero), seen_plant, want))
        rec = build_F_record(nprocs, got, ident, cv0, cv0r, con_sizes, rows,
                             eta_raw, eta, eta_flagged, cd0, cl0, baseline_dvs)
        write_artefact(OUT_F, rec, TERMINAL_F, " n_rows=%d" % len(rows))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
