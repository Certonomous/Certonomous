#!/usr/bin/env python
"""Curriculum SO-2M -- NACA0012 INCOMPRESSIBLE, the FD-VERIFIED PITCHING-MOMENT
GRADIENT RUNG.  Sanaa's SO-2 third family (moment cap), first rung.  VALUE and
JACOBIAN of `CMZ`, TWO TOOLCHAIN ROWS, NO OPTIMISER.

DERIVED FROM `curriculum_SO1a/so1a_xf.py` (md5 f34bd5bf550786ff926aed81b342cced)
-- the parent the FROZEN document names at PREREGISTRATION.md section 10 -- with
EXACTLY these registered deltas and no other (so2m_xm_DELTAS_from_so1a_xf.diff):

  * THE PRODUCER IS NO LONGER A BYTE COPY OF THE TUTORIAL, AND THAT IS SAID
    OPENLY RATHER THAN QUIETLY.  `so2m_runScript.py` is the tutorial's
    `NACA0012_Airfoil/incompressible/runScript.py` (md5
    0557da51f6f179f6de865144343c499f) PLUS the two insertions registered at
    PREREGISTRATION.md section 3 and nothing else.  Its own md5 is therefore a
    NEW value and is pinned below.  SO-2a's frozen section 0.1(2) predicted this
    exact change -- "a moment cap needs a third force/moment function added to
    daOptions, which changes the frozen producer, changes its md5, and puts a
    NEW, NEVER-FD-VERIFIED FUNCTIONAL into the graded set" -- so the md5 moving
    is the EXPECTED consequence of the item existing, never a drift.  BOTH md5s
    are checked here: the producer's own, AND the tutorial's, so a checkout that
    moved under this item refuses (NL-2, PREREGISTRATION.md section 10).

  * `CMZ` JOINS `CD` AND `CL` AS A FIRST-CLASS OUTPUT.  `compute_totals` is taken
    over THREE functionals and every FD row records `dCD`, `dCL` AND `dCMZ` from
    the SAME primals, so the moment Jacobian costs no primal beyond SO-1a's.
    `CMZ` is the GRADED functional (G5m); `CD` and `CL` ride along as context and
    as the two numbers whose behaviour on this case is already on the record.

  * THE PLANTED CONTROL MOVES AN ENTRY INSIDE A TUPLE THE READER MUST TRAVERSE IN
    FULL, AND THE CONTROL THAT EMPTIES THAT TUPLE IS REFUSED.  A control whose
    container is empty is "seen" by a broken reader too, so `CONTROL_OUTPUTS` is
    a REGISTERED, ORDERED tuple of three output keys; the synthetic CTRL row
    carries all three at exactly 0.0; the planted twin moves ENTRY 0 (`dCMZ`) by
    PLANT and leaves the other two at exactly 0.0.  The instrument re-reads the
    row FROM DISK and exits 2 if the plant is invisible, if the tuple is short,
    or if a companion entry moved.

  * `patchV[1]` (angle of attack) is the component G-NZ is registered on: `CMZ`
    is a FLOW functional, so `d(CMZ)/d(aoa)` must be structurally NON-zero.  A
    reader that returns zeros because it read the wrong key, the wrong slice or
    an empty tuple FAILS that gate rather than passing it -- the opposite failure
    direction from SO-2a's exact-zero `G-STRUCT`.

  * Printed tokens SO1A_* -> SO2M_*; artefact names so1a_* -> so2m_*.
  * The two-primal eta measurement, `writeCompression` read from the case's own
    controlDict, the emit/fsync discipline and the MPI rank-0 file rule are
    SO-1a's / D15's / D5's / D4's bytes, unchanged.

DAFOAM_CHARTER.md section 2: an adjoint gradient is not a result until an FD
table stands beside it.  Section 3: the step is proved to lie in the plateau --
and here PER PAIR, not once for the item.  Section 4: the gate names its trivial
baseline BEFORE its own run.  Section 5: serial before parallel, np = 1, and no
FD reference is carried across np.  L-332: NO `assert` anywhere in this file.
"""

import hashlib
import json
import os
import sys
import time

PRODUCER = "so2m_runScript.py"
# THE PRODUCER'S OWN md5 -- a NEW value, because this item adds the third
# functional.  Set at the Stage-2 amendment and pinned in the driver and launcher.
PRODUCER_MD5 = "ae4a73429dd6972dc804b76d9a44aa05"
# THE TUTORIAL'S md5, frozen at PREREGISTRATION.md section 3 and section 10 NL-2.
TUTORIAL_MD5 = "0557da51f6f179f6de865144343c499f"
# The REGISTERED INSERTIONS, verbatim (PREREGISTRATION.md section 3; copied from
# the sibling runScript_Stability_Not_Working.py :44 and :76-84).  The producer
# must differ from the tutorial by EXACTLY these added lines and by NO removed
# line.  Checked against the tutorial when the tutorial is reachable.
REGISTERED_INSERTIONS = (
    "L0 = 1.0",
    '        "CMZ": {',
    '            "type": "moment",',
    '            "source": "patchToFace",',
    '            "patches": ["wing"],',
    '            "axis": [0.0, 0.0, 1.0],',
    '            "center": [0.25, 0.0, 0.05],',
    "            # NOTE. We scale it with -1 because DAFoam's CMZ calculation is positive for nose down",
    '            "scale": -1.0 / (0.5 * U0 * U0 * A0 * L0),',
    "        },",
)
TUTORIAL_PATHS = ("/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/runScript.py",)
ANCHOR = "# OpenMDAO setup"
ITEM = "SO2M"

# ---- registered constants (PREREGISTRATION.md sections 3, 6, 7) ---------------
ETA_FLOOR = 1.0e-14          # a measured eta below this is replaced by this and FLAGGED
STEPS = {
    "shape":  [1.0e-2, 1.0e-3, 1.0e-4],     # registered step set, FFD y-displacement units
    "patchV": [1.0e-1, 1.0e-2, 1.0e-3],     # registered step set, degrees of aoa
}
# THE CHARTER-4 TRIVIAL BASELINE at a DELIBERATELY WRONG step, five orders below
# the registered middle step (PREREGISTRATION.md section 5, G-TB).
TB_STEPS = {
    "shape":  [1.0e-8],
    "patchV": [1.0e-6],
}
# The REGISTERED SUBSET (PREREGISTRATION.md section 6): SO-1a's and SO-2a's four
# shape functions, so the three items' readings sit on the same components, PLUS
# patchV[1] (angle of attack), which carries G-NZ.
COMPONENTS = [
    ("shape", 0),
    ("shape", 3),
    ("shape", 6),
    ("shape", 7),
    ("patchV", 1),
]
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03            # standing rule 3; PREREGISTRATION.md section 7

# ---- THE REGISTERED OUTPUT VOCABULARY, DECLARED ONCE ------------------------
# RULE 14 (L-221/L-222), and the failure that cost this family a run 30 minutes
# before this file was written: SO-1c died at its second arm because a producer
# labelled per-row artefacts with one spelling and its consumers compared against
# another.  So the OUTPUT KEYS are declared HERE, ONCE, and every producer and
# every consumer in this item derives them from these tuples rather than from a
# literal typed at a call site.
#   OUTPUTS         -- the OpenMDAO variable suffix, in the order they are taken
#   DKEY_OF_OUTPUT  -- the FD-table key each output writes
# The two label sets are DISJOINT ("CMZ" is never a d-key, "dCMZ" is never an
# output name), so an artefact whose keys were swapped cannot be read as valid.
OUTPUTS = ("CD", "CL", "CMZ")
DKEY_OF_OUTPUT = {"CD": "dCD", "CL": "dCL", "CMZ": "dCMZ"}
# The GRADED functional of this item, named once.
GRADED_OUTPUT = "CMZ"
# THE CONTROL'S ORDERED TUPLE (PREREGISTRATION.md section 7, direction A): the
# reader must traverse all three; entry 0 is the one the plant moves.  A control
# that EMPTIES this tuple is REFUSED -- an empty container is seen by a broken
# reader too.
CONTROL_OUTPUTS = ("dCMZ", "dCD", "dCL")

OUT_X = "so2m_X.json"
OUT_F = "so2m_F.json"
JSONL_F = "so2m_F.jsonl"
JSONL_X = "so2m_X.jsonl"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def producer_delta_report(src_text):
    """NL-2's condition, computed rather than asserted: the producer must differ
    from the tutorial by EXACTLY the registered insertions and by no removal.

    The tutorial checkout is NOT inside the container, so this returns
    `reachable: False` there and the md5 pin above carries the check.  When the
    tutorial IS reachable (the driver's pre-flight on the host) the line-level
    difference is computed and reported."""
    import difflib
    tut = None
    for p in TUTORIAL_PATHS:
        if os.path.isfile(p):
            tut = p
            break
    if tut is None:
        return {"reachable": False, "tutorial_paths_tried": list(TUTORIAL_PATHS)}
    got = md5_of(tut)
    added, removed = [], []
    for line in difflib.unified_diff(open(tut).read().split("\n"), src_text.split("\n"),
                                     lineterm="", n=0):
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])
    return {"reachable": True, "tutorial": tut, "tutorial_md5": got,
            "tutorial_md5_registered": TUTORIAL_MD5,
            "tutorial_md5_ok": got == TUTORIAL_MD5,
            "added": added, "removed": removed,
            "insertions_exact": (tuple(added) == REGISTERED_INSERTIONS and not removed)}


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
    the age-guard datum to the NAME `0/U` while `writeCompression on` turns it
    into `0/U.gz` on a serial arm.  The setting is a recorded datum of the run,
    never an assumption of the reader."""
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


def parse_mode(argv):
    mode = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
    if mode not in ("X", "G"):
        sys.stderr.write("SO2M_XM usage: so2m_xm.py -mode X|G\n")
        sys.exit(64)
    return mode


def main():
    mode = parse_mode(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("SO2M_XM REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)
    delta = producer_delta_report(open(PRODUCER).read())
    if delta.get("reachable") and not (delta["tutorial_md5_ok"] and delta["insertions_exact"]):
        sys.stderr.write("SO2M_XM REFUSE producer differs from the tutorial by "
                         "something other than the two registered insertions: %s\n"
                         % json.dumps(delta, sort_keys=True)[:800])
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("SO2M_XM REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    # the producer header parses sys.argv; give it the registered task
    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "so2m_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    # P1's FIRST HALF, checked in-process and printed: the CMZ entry must be
    # DECLARED in the producer's daOptions the header just built.  That it
    # EVALUATES is the other half and only the solve can say so.
    declared = sorted((ns.get("daOptions") or {}).get("function", {}).keys())
    if GRADED_OUTPUT not in declared:
        sys.stderr.write("SO2M_XM REFUSE %s is not declared in daOptions['function']: %r\n"
                         % (GRADED_OUTPUT, declared))
        sys.exit(2)
    sys.stdout.write("SO2M_FUNCTIONS_DECLARED %s\n" % (",".join(declared),))

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    jsonl = JSONL_F if mode == "G" else JSONL_X

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
          "producer_md5": got, "producer_delta": delta,
          "functions_declared": declared,
          "solverName": ns["daOptions"].get("solverName"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"), "CL_target": ns.get("CL_target"),
          "L0": ns.get("L0"), "A0": ns.get("A0"), "p0": ns.get("p0"), **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    # ---- the BASELINE design: the producer's own defaults, read back ----------
    base = {"shape": np.array(prob.get_val("shape"), dtype=float).copy(),
            "patchV": np.array(prob.get_val("patchV"), dtype=float).copy()}
    emit({"kind": "baseline_dvs", "n_shape": int(base["shape"].size),
          "n_patchV": int(base["patchV"].size),
          "shape": [repr(float(v)) for v in base["shape"]],
          "patchV": [repr(float(v)) for v in base["patchV"]]})

    # THE REGISTERED OpenMDAO NAMES, built ONCE from the OUTPUTS tuple so no call
    # site below types a functional name of its own (rule 14).
    OF_NAME = {o: "scenario1.aero_post.%s" % o for o in OUTPUTS}

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        vals = {o: float(prob.get_val(OF_NAME[o])[0]) for o in OUTPUTS}
        emit({"kind": "primal", "tag": tag,
              **{o: repr(vals[o]) for o in OUTPUTS},
              "wall_s": round(time.time() - t0, 3)})
        return vals

    v0 = primal("baseline")

    if mode == "X":
        t0 = time.time()
        totals = prob.compute_totals(of=[OF_NAME[o] for o in OUTPUTS], wrt=["shape", "patchV"])
        emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
        jadj = {}
        for o in OUTPUTS:
            jadj[o] = {}
            for dv in ("shape", "patchV"):
                arr = np.atleast_1d(np.array(totals[(OF_NAME[o], dv)]).ravel())
                jadj[o][dv] = [repr(float(v)) for v in arr]
                emit({"kind": "adjoint", "of": o, "dv": dv, "n": int(arr.size),
                      "values": jadj[o][dv]})
        if rank == 0:
            out = {"item": ITEM, "mode": "X", "producer_md5": got, "nprocs": nprocs,
                   "identity": ident, "outputs": list(OUTPUTS),
                   "graded_output": GRADED_OUTPUT,
                   **{"%s_baseline" % o: repr(v0[o]) for o in OUTPUTS},
                   "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                                    "patchV": [repr(float(v)) for v in base["patchV"]]},
                   "adjoint": jadj}
            with open(OUT_X, "w") as fh:
                json.dump(out, fh, indent=1, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            sys.stdout.write("SO2M_X_WRITTEN %s\n" % OUT_X)
        MPI.COMM_WORLD.Barrier()
        return

    # ---- mode G: eta, then central differences at the REGISTERED steps ---------
    v0r = primal("baseline_repeat")
    eta_raw = abs(v0[GRADED_OUTPUT] - v0r[GRADED_OUTPUT])
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "eta_on": GRADED_OUTPUT,
          **{"%s_baseline" % o: repr(v0[o]) for o in OUTPUTS},
          **{"%s_repeat" % o: repr(v0r[o]) for o in OUTPUTS}})

    def set_perturbed(dv, idx, delta):
        for k in ("shape", "patchV"):
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)

    def central(dv, idx, s, tag):
        set_perturbed(dv, idx, +s)
        vp = primal("%s%s[%d]+%g" % (tag, dv, idx, s))
        set_perturbed(dv, idx, -s)
        vm = primal("%s%s[%d]-%g" % (tag, dv, idx, s))
        rec = {"step": s, "ok": True}
        for o in OUTPUTS:
            rec[DKEY_OF_OUTPUT[o]] = repr((vp[o] - vm[o]) / (2.0 * s))
            rec["%s_plus" % o] = repr(vp[o])
            rec["%s_minus" % o] = repr(vm[o])
        return rec

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
                fd[key] = central(dv, idx, s, "")
            except Exception as exc:                      # noqa: BLE001
                fd[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        # ---- the CHARTER-4 TRIVIAL BASELINE at the DELIBERATELY WRONG step ----
        tb = {}
        for s in TB_STEPS[dv]:
            key = repr(s)
            try:
                tb[key] = central(dv, idx, s, "TB ")
            except Exception as exc:                      # noqa: BLE001
                tb[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "tb_step", "dv": dv, "idx": idx, "step": s, "row": tb[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd, "tb": tb})
    # restore
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())

    # ---- THE PLANTED CONTROL (standing rule 3; PREREGISTRATION.md section 7A) --
    # No solve.  Identical DVs on both sides, so EVERY entry of CONTROL_OUTPUTS is
    # exactly 0.0.  The planted twin moves ENTRY 0 by PLANT on the PLUS side alone,
    # so that entry is exactly PLANT/(2*CTRL_STEP) and the OTHER TWO are still
    # exactly 0.0.  The tuple is never emptied: a reader that cannot traverse it
    # would see an empty container as readable, so an empty control is REFUSED.
    ctrl_fd = {"step": CTRL_STEP, "ok": True,
               "note": "synthetic: identical DVs on both sides -> every derivative exactly 0"}
    for k in CONTROL_OUTPUTS:
        ctrl_fd[k] = repr(0.0)
    ctrl_planted = {"step": CTRL_STEP, "plant": PLANT, "ok": True,
                    "moved_entry": CONTROL_OUTPUTS[0],
                    "control_outputs": list(CONTROL_OUTPUTS),
                    "note": "synthetic: %s_plus = %s_baseline + PLANT -> that entry exactly "
                            "PLANT/(2 s); the other entries of CONTROL_OUTPUTS stay exactly 0.0"
                            % (CONTROL_OUTPUTS[0], CONTROL_OUTPUTS[0])}
    for i, k in enumerate(CONTROL_OUTPUTS):
        ctrl_planted[k] = repr(PLANT / (2.0 * CTRL_STEP) if i == 0 else 0.0)
    ctrl = {"dv": "CTRL", "idx": 0, "status": "CONTROL",
            "control_outputs": list(CONTROL_OUTPUTS),
            "fd": {repr(CTRL_STEP): ctrl_fd}, "planted": ctrl_planted}
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        # READ BACK FROM DISK what was just emitted; refuse if the plant is
        # invisible, if the traversed tuple is SHORT, or if a companion moved.
        seen = None
        with open(jsonl) as fh:
            for line in fh:
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    seen = rec["row"]
        want = PLANT / (2.0 * CTRL_STEP)
        problem = None
        if seen is None:
            problem = "control row absent on read-back"
        elif tuple(seen.get("control_outputs") or ()) != CONTROL_OUTPUTS:
            problem = "control tuple is not the registered one: %r" % (seen.get("control_outputs"),)
        else:
            zeros = [float(seen["fd"][repr(CTRL_STEP)][k]) for k in CONTROL_OUTPUTS]
            plants = [float(seen["planted"][k]) for k in CONTROL_OUTPUTS]
            if len(zeros) != len(CONTROL_OUTPUTS) or len(plants) != len(CONTROL_OUTPUTS):
                problem = "control tuple EMPTIED or SHORT on read-back"
            elif any(z != 0.0 for z in zeros):
                problem = "the unplanted control is not exactly zero: %r" % (zeros,)
            elif abs(plants[0] - want) > 1e-12 * abs(want):
                problem = "entry 0 does not carry the plant: got %r want %r" % (plants[0], want)
            elif any(p != 0.0 for p in plants[1:]):
                problem = "a COMPANION entry moved under the plant: %r" % (plants,)
        if problem is not None:
            sys.stderr.write("SO2M_XM REFUSE planted control not seen on read-back: %s\n" % problem)
            sys.exit(2)
        sys.stdout.write("SO2M_PLANTED_CONTROL_SEEN tuple=%s zero=%r plant=%r\n"
                         % (",".join(CONTROL_OUTPUTS),
                            [float(seen["fd"][repr(CTRL_STEP)][k]) for k in CONTROL_OUTPUTS],
                            [float(seen["planted"][k]) for k in CONTROL_OUTPUTS]))
        out = {
            "item": ITEM, "mode": "G", "producer_md5": got, "nprocs": nprocs,
            "identity": ident, "outputs": list(OUTPUTS), "graded_output": GRADED_OUTPUT,
            "d_key_of_output": dict(DKEY_OF_OUTPUT),
            "control_outputs": list(CONTROL_OUTPUTS),
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": STEPS, "tb_steps": TB_STEPS, "ctrl_step": CTRL_STEP, "plant": PLANT,
            **{"%s_baseline" % o: repr(v0[o]) for o in OUTPUTS},
            **{"%s_baseline_repeat" % o: repr(v0r[o]) for o in OUTPUTS},
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "eta_on": GRADED_OUTPUT,
            "baseline_dvs": {"shape": [repr(float(v)) for v in base["shape"]],
                             "patchV": [repr(float(v)) for v in base["patchV"]]},
            "rows": rows, "n_rows": len(rows),
        }
        with open(OUT_F, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("SO2M_F_WRITTEN %s n_rows=%d\n" % (OUT_F, len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
