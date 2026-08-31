#!/usr/bin/env python
"""Curriculum SO-1cR -- NACA0012 INCOMPRESSIBLE drag-min-at-fixed-lift, the
POST-OPTIMUM DECOMPOSITION-INVARIANCE ROW of Sanaa's shape-optimisation ladder
SO-1 (directives 2026-08-27T16:54Z section 4, the third step of the per-case
pattern: "post-optimum verification (re-solve at optimum, constraints checked,
np-invariance spot row)").

SO-1b buys the re-solve at the optimum and the constraint check.  THE
np-INVARIANCE SPOT ROW IS THE ONE THIRD IT DOES NOT BUY, and it is this file.

DERIVED FROM `curriculum_SO1a/so1a_xf.py` (md5 pinned in so1cr_chain_driver.sh)
with EXACTLY these registered deltas and no other
(so1cr_xn_DELTAS_from_so1a_xf.diff):

  * ONE MODE `N` INSTEAD OF TWO.  SO-1a splits X (adjoint) and F (FD) into two
    arms because they answer two questions at one design point.  SO-1cR must
    take BOTH IN THE SAME PROCESS AT THE SAME DECOMPOSITION, because
    `DAFOAM_CHARTER.md` section 5 makes an FD reference part of a
    CONFIGURATION, not a property of a case: "A gradient verified at one np is
    a statement about that np and is never carried to another."  An np = 4
    analytic gradient graded against an np = 1 FD table would be exactly the
    W4_IDX16 carrying failure section 5 names.  So each arm buys its OWN FD
    table beside its own analytic gradient.

  * THE DESIGN POINT IS SO-1b's OPTIMUM, READ FROM DISK, NEVER RE-DERIVED.
    `-optimum <path>` names SO-1b's own `so1b_E.json` for THIS row.  That one
    artefact carries `design_point` (x*), `adjoint` (the np = 1 analytic
    gradient AT x*, which is the comparison basis) and `identity` (the row's
    libidwarp hash).  It is SO-1b's LAST ARM's artefact, so it exists only if
    SO-1b's chain reached and completed the arm that produced what SO-1cR reads.
    THE np = 1 GRADIENT IS NOT RE-BOUGHT.

  * np = 4 BY REGISTRATION, AND THE DECOMPOSITION IS A RECORDED DATUM OF THE
    RUN.  `DAFOAM_CHARTER.md` section 5 forbids "a parallel gradient table with
    no decomposition column" and forbids "describing a case as
    decomposition-invariant from one arm".  `nprocs` is asserted == 4 against
    MPI itself AND against `numberOfSubdomains` in the case's own
    `system/decomposeParDict`; the METHOD and, for `simple`, the SUBDIVISION
    `n` are parsed from that same dictionary and written into the artefact.
    A disagreement REFUSES.  Two decompositions are bought per row (`scotch`
    and `simple 4x1x1` -- the two A4 varied, at 8.95 % and 0.00054 %).

  * G-ROWX AT THE READ.  The in-process `libidwarp.so` md5 must equal the md5
    recorded in the SO-1b artefact being read, or this file REFUSES.  A row is
    an image hash, never a directory name, and reading another row's optimum
    would silently produce a two-row comparison that is one row twice.

  * THE BASELINE IS NOT SOLVED AT ALL.  SO-1a's `primal("baseline")` at the
    producer's defaults is replaced by `primal("optimum")` after x* is set.
    Every FD perturbation is taken ABOUT x*, not about the undeformed shape.
    That is the whole point of the rung: IDWarp's defect is a MESH-DEFORMATION
    defect, so a deformed mesh is where a partition-interface interaction would
    be worst, and `DAFOAM_CHARTER.md` section 9's own argument -- "a gradient
    verified at iteration 0 is not verified at iteration 47" -- transfers to
    the decomposition without a word changed.

  * Printed tokens SO1A_* -> SO1CR_*; artefact names so1a_* -> so1cr_*.

  * KEPT BYTE-FOR-BYTE IN SUBSTANCE from SO-1a: the registered STEPS and
    COMPONENTS, the charter-4 TB_STEPS trivial baseline, the two-primal eta
    measurement, the CTRL planted-zero component with its disk read-back
    refusal, `writeCompression` read from the case's own controlDict, the
    emit/fsync discipline and the MPI rank-0 file rule.

`DAFOAM_CHARTER.md` section 2: an adjoint gradient is not a result until an FD
table stands beside it.  Section 3: the step is proved to lie in the plateau.
Section 4: the gate names its trivial baseline BEFORE its own run.  Section 5:
the decomposition is disclosed, never assumed away, and never carried.
Section 6: shipped and patched are always two rows.
"""

import hashlib
import json
import os
import sys
import time

PRODUCER = "so1cr_runScript.py"
PRODUCER_MD5 = "0557da51f6f179f6de865144343c499f"
ANCHOR = "# OpenMDAO setup"
ITEM = "SO1cR"

# ---- registered constants (PREREGISTRATION.md section 3) --------------------
REGISTERED_NPROCS = 4        # DAFOAM_CHARTER.md section 5: asserted, never assumed
ETA_FLOOR = 1.0e-14          # a measured eta below this is replaced by this and FLAGGED
STEPS = {
    "shape":  [1.0e-2, 1.0e-3, 1.0e-4],     # SO-1a's registered step set, inherited unchanged
    "patchV": [1.0e-1, 1.0e-2, 1.0e-3],     # degrees of aoa
}
# THE CHARTER-4 TRIVIAL BASELINE, inherited from SO-1a unchanged: the SAME probe
# at a DELIBERATELY WRONG step five orders below the registered middle step.  If
# the WRONG step also passes band D the gate is not measuring the step and that
# arm's G5N verdict is WITHDRAWN -- registered here, before its own run.
TB_STEPS = {
    "shape":  [1.0e-8],
    "patchV": [1.0e-6],
}
# The REGISTERED SUBSET, IDENTICAL to SO-1a's and SO-1b's, which is what makes
# baseline, optimum-at-np1 and optimum-at-np4 the SAME measurement at three
# configurations.  shape[6] is the LE thickness function -- the A1 idx6-class
# component the shipped row sign-flipped at its baseline.
COMPONENTS = [
    ("shape", 0),
    ("shape", 3),
    ("shape", 6),
    ("shape", 7),
    ("patchV", 1),
]
CTRL_STEP = 1.0e-3
PLANT = 1.234e-03            # CLAUDE.md rule 3

OUT_N = "so1cr_N.json"
JSONL_N = "so1cr_N.jsonl"


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
    it as `0/U.gz`.  The setting is a fact about the run and is recorded as one.
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


def case_decomposition():
    """Read the DECOMPOSITION from THE CASE'S OWN system/decomposeParDict.

    `DAFOAM_CHARTER.md` section 5 forbids "a parallel gradient table with no
    decomposition column".  Here the column is a GATE: the method and, for
    `simple`, the subdivision `n` are parsed from the dictionary the run
    actually used, written into the artefact, and cross-checked by the grader
    against the arm's registered decomposition.  An unreadable dictionary is
    REPORTED, never guessed -- a decomposition the reader had to assume is
    exactly the missing column the charter names.
    """
    p = os.path.join("system", "decomposeParDict")
    out = {"decomp_method": None, "decomp_n_subdomains": None,
           "decomp_simple_n": None, "decomp_source": os.path.abspath(p)}
    try:
        text = open(p, errors="replace").read()
    except OSError as exc:                                    # noqa: BLE001
        out["decomp_error"] = repr(exc)[:200]
        return out
    in_simple = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("numberOfSubdomains"):
            try:
                out["decomp_n_subdomains"] = int(s.rstrip(";").split()[-1])
            except ValueError:
                out["decomp_error"] = "numberOfSubdomains unparseable: %r" % s[:80]
        elif s.startswith("method"):
            out["decomp_method"] = s.rstrip(";").split()[-1]
        elif s.startswith("simpleCoeffs"):
            in_simple = True
        elif in_simple and s.startswith("n "):
            frag = s.rstrip(";").split("(", 1)
            if len(frag) == 2:
                out["decomp_simple_n"] = frag[1].split(")")[0].split()
            in_simple = False
    return out


def parse_args(argv):
    mode, opt = None, None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
        if a == "-optimum" and i + 1 < len(argv):
            opt = argv[i + 1]
    if mode != "N" or not opt:
        sys.stderr.write("SO1CR_XN usage: so1cr_xn.py -mode N -optimum <path to SO-1b so1b_E.json>\n")
        sys.exit(64)
    return mode, opt


def load_optimum(path, ident):
    """Read SO-1b's OWN artefact for this row: x*, the np = 1 analytic gradient
    at x*, and the row's library hash.  REFUSES on anything it cannot parse and
    REFUSES on a row mismatch (G-ROWX).  An unreadable dependency is not a
    licence to proceed.
    """
    try:
        with open(path) as fh:
            src = json.load(fh)
    except Exception as exc:                                  # noqa: BLE001
        sys.stderr.write("SO1CR_XN REFUSE optimum artefact unreadable %s: %r\n"
                         % (path, exc))
        sys.exit(3)
    for key in ("design_point", "adjoint", "identity", "nprocs", "row"):
        if key not in src:
            sys.stderr.write("SO1CR_XN REFUSE optimum artefact lacks %r: %s\n" % (key, path))
            sys.exit(3)
    if int(src["nprocs"]) != 1:
        sys.stderr.write("SO1CR_XN REFUSE the comparison basis must be the np = 1 gradient; "
                         "artefact records nprocs=%r\n" % (src["nprocs"],))
        sys.exit(3)
    # ---- G-ROWX.  A row is an image hash, never a directory name.
    want = (src.get("identity") or {}).get("libidwarp_so_md5")
    got = ident.get("libidwarp_so_md5")
    if not want or not got or want != got:
        sys.stderr.write("SO1CR_XN REFUSE G-ROWX: this process libidwarp md5 %r != the optimum "
                         "artefact's %r -- reading another row's optimum would make a two-row "
                         "comparison one row twice\n" % (got, want))
        sys.exit(3)
    return src


def main():
    mode, opt_path = parse_args(sys.argv)
    got = md5_of(PRODUCER)
    if got != PRODUCER_MD5:
        sys.stderr.write("SO1CR_XN REFUSE producer md5 %s != frozen %s\n"
                         % (got, PRODUCER_MD5))
        sys.exit(2)

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("SO1CR_XN REFUSE anchor %r appears %d times\n"
                         % (ANCHOR, src.count(ANCHOR)))
        sys.exit(2)
    header = src.split(ANCHOR)[0]

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "so1cr_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size

    ident = idwarp_identity()
    ident.update(case_write_compression())
    decomp = case_decomposition()

    # ---- G-NP.  CROSS-ASSERTED ON BOTH SIDES, before any solve.  MPI's own
    # ---- rank count AND the dictionary the decomposition was built from must
    # ---- both read the registered 4.  Two numbers derived from one source can
    # ---- both be wrong; these come from different sources.
    if nprocs != REGISTERED_NPROCS:
        sys.stderr.write("SO1CR_XN REFUSE G-NP: MPI reports nprocs=%d, registered %d\n"
                         % (nprocs, REGISTERED_NPROCS))
        sys.exit(4)
    if decomp.get("decomp_n_subdomains") != REGISTERED_NPROCS:
        sys.stderr.write("SO1CR_XN REFUSE G-NP: decomposeParDict numberOfSubdomains=%r, "
                         "registered %d (source %s)\n"
                         % (decomp.get("decomp_n_subdomains"), REGISTERED_NPROCS,
                            decomp.get("decomp_source")))
        sys.exit(4)
    if not decomp.get("decomp_method"):
        sys.stderr.write("SO1CR_XN REFUSE G-DECOMP: no decomposition method could be read "
                         "from %s -- a parallel gradient table with no decomposition column "
                         "is what DAFOAM_CHARTER.md section 5 forbids\n"
                         % (decomp.get("decomp_source"),))
        sys.exit(4)

    opt = load_optimum(opt_path, ident)
    row = opt["row"]

    Top = ns["Top"]

    def emit(rec):
        if rank != 0:
            return
        with open(JSONL_N, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    emit({"kind": "identity", "item": ITEM, "mode": mode, "row": row,
          "nprocs": nprocs, "producer_md5": got,
          "solverName": ns["daOptions"].get("solverName"),
          "U0": ns.get("U0"), "aoa0": ns.get("aoa0"),
          "CL_target": ns.get("CL_target"), "p0": ns.get("p0"),
          "optimum_from": os.path.abspath(opt_path), **ident, **decomp})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    # ---- THE DESIGN POINT IS SO-1b's OPTIMUM x*, SET FROM ITS ARTEFACT -------
    # SO-1a and SO-1b's own baseline block read the producer's defaults here.
    # This item overwrites them with x* and records BOTH, so the artefact shows
    # what the producer would have used and what this run actually solved at.
    defaults = {"shape": np.array(prob.get_val("shape"), dtype=float).copy(),
                "patchV": np.array(prob.get_val("patchV"), dtype=float).copy()}
    base = {}
    for k in ("shape", "patchV"):
        vals = [float(v) for v in opt["design_point"][k]]
        if len(vals) != defaults[k].size:
            sys.stderr.write("SO1CR_XN REFUSE x* has %d %s components, this problem has %d\n"
                             % (len(vals), k, defaults[k].size))
            sys.exit(3)
        base[k] = np.array(vals, dtype=float)
        prob.set_val(k, base[k].copy())
    emit({"kind": "design_point", "source": os.path.abspath(opt_path),
          "n_shape": int(base["shape"].size), "n_patchV": int(base["patchV"].size),
          "shape": [repr(float(v)) for v in base["shape"]],
          "patchV": [repr(float(v)) for v in base["patchV"]],
          "producer_defaults": {"shape": [repr(float(v)) for v in defaults["shape"]],
                                "patchV": [repr(float(v)) for v in defaults["patchV"]]}})

    CD = "scenario1.aero_post.CD"
    CL = "scenario1.aero_post.CL"

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        cd = float(prob.get_val(CD)[0])
        cl = float(prob.get_val(CL)[0])
        emit({"kind": "primal", "tag": tag, "CD": repr(cd), "CL": repr(cl),
              "wall_s": round(time.time() - t0, 3)})
        return cd, cl

    cd0, cl0 = primal("optimum")

    # ---- THE ANALYTIC GRADIENT AT x*, AT THIS DECOMPOSITION -----------------
    t0 = time.time()
    totals = prob.compute_totals(of=[CD, CL], wrt=["shape", "patchV"])
    emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
    jadj = {}
    for of_name, of_key in ((CD, "CD"), (CL, "CL")):
        jadj[of_key] = {}
        for dv in ("shape", "patchV"):
            arr = np.atleast_1d(np.array(totals[(of_name, dv)]).ravel())
            jadj[of_key][dv] = [repr(float(v)) for v in arr]
            emit({"kind": "adjoint", "of": of_key, "dv": dv, "n": int(arr.size),
                  "values": jadj[of_key][dv]})

    # ---- eta, then central differences at the REGISTERED steps, ABOUT x* ----
    cd0r, cl0r = primal("optimum_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": repr(eta_raw), "eta_used": repr(eta),
          "eta_floored": eta_flagged, "CD_optimum": repr(cd0),
          "CD_repeat": repr(cd0r), "CL_optimum": repr(cl0),
          "CL_repeat": repr(cl0r)})

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
                cdp, clp = primal("%s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("%s[%d]-%g" % (dv, idx, s))
                fd[key] = {"step": s, "dCD": repr((cdp - cdm) / (2.0 * s)),
                           "dCL": repr((clp - clm) / (2.0 * s)),
                           "CD_plus": repr(cdp), "CD_minus": repr(cdm),
                           "CL_plus": repr(clp), "CL_minus": repr(clm), "ok": True}
            except Exception as exc:                      # noqa: BLE001
                fd[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
        # ---- the CHARTER-4 TRIVIAL BASELINE at the DELIBERATELY WRONG step ----
        tb = {}
        for s in TB_STEPS[dv]:
            key = repr(s)
            try:
                set_perturbed(dv, idx, +s)
                cdp, clp = primal("TB %s[%d]+%g" % (dv, idx, s))
                set_perturbed(dv, idx, -s)
                cdm, clm = primal("TB %s[%d]-%g" % (dv, idx, s))
                tb[key] = {"step": s, "dCD": repr((cdp - cdm) / (2.0 * s)),
                           "dCL": repr((clp - clm) / (2.0 * s)),
                           "CD_plus": repr(cdp), "CD_minus": repr(cdm),
                           "CL_plus": repr(clp), "CL_minus": repr(clm), "ok": True}
            except Exception as exc:                      # noqa: BLE001
                tb[key] = {"step": s, "ok": False, "error": repr(exc)[:400]}
            emit({"kind": "tb_step", "dv": dv, "idx": idx, "step": s, "row": tb[key]})
        rows.append({"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd, "tb": tb})
    for k in ("shape", "patchV"):
        prob.set_val(k, base[k].copy())

    # ---- THE PLANTED-ZERO CONTROL COMPONENT (rule 3): no solve, written, read back
    ctrl = {"dv": "CTRL", "idx": 0, "status": "CONTROL", "fd": {
        repr(CTRL_STEP): {"step": CTRL_STEP, "dCD": repr(0.0), "dCL": repr(0.0),
                          "CD_plus": repr(cd0), "CD_minus": repr(cd0),
                          "CL_plus": repr(cl0), "CL_minus": repr(cl0), "ok": True,
                          "note": "synthetic: identical DVs on both sides -> derivative exactly 0"}},
        "planted": {"step": CTRL_STEP, "plant": PLANT,
                    "dCD": repr(PLANT / (2.0 * CTRL_STEP)),
                    "CD_plus": repr(cd0 + PLANT), "CD_minus": repr(cd0), "ok": True,
                    "note": "synthetic: CD_plus = CD_optimum + PLANT -> derivative exactly PLANT/(2 s)"}}
    emit({"kind": "control", "row": ctrl})
    rows.append(ctrl)

    if rank == 0:
        # READ BACK FROM DISK what was just emitted; refuse if the plant is invisible
        seen_zero, seen_plant = None, None
        with open(JSONL_N) as fh:
            for line in fh:
                rec = json.loads(line)
                if rec.get("kind") == "control":
                    r = rec["row"]
                    seen_zero = float(r["fd"][repr(CTRL_STEP)]["dCD"])
                    seen_plant = float(r["planted"]["dCD"])
        want = PLANT / (2.0 * CTRL_STEP)
        if seen_zero != 0.0 or seen_plant is None or abs(seen_plant - want) > 1e-12 * abs(want):
            sys.stderr.write("SO1CR_XN REFUSE planted-zero control not seen on read-back: "
                             "zero=%r plant=%r want=%r\n" % (seen_zero, seen_plant, want))
            sys.exit(2)
        sys.stdout.write("SO1CR_PLANTED_ZERO_CONTROL_SEEN zero=%r plant=%r\n"
                         % (seen_zero, seen_plant))
        out = {
            "item": ITEM, "mode": "N", "row": row, "producer_md5": got,
            "nprocs": nprocs, "identity": ident, "decomposition": decomp,
            "optimum_from": os.path.abspath(opt_path),
            "design_point": {"shape": [repr(float(v)) for v in base["shape"]],
                             "patchV": [repr(float(v)) for v in base["patchV"]]},
            "producer_defaults": {"shape": [repr(float(v)) for v in defaults["shape"]],
                                  "patchV": [repr(float(v)) for v in defaults["patchV"]]},
            "components_requested": [[d, i] for (d, i) in COMPONENTS],
            "n_components_requested": len(COMPONENTS),
            "steps": STEPS, "tb_steps": TB_STEPS, "ctrl_step": CTRL_STEP, "plant": PLANT,
            "CD_optimum": repr(cd0), "CL_optimum": repr(cl0),
            "CD_optimum_repeat": repr(cd0r), "CL_optimum_repeat": repr(cl0r),
            "eta_raw": repr(eta_raw), "eta_used": repr(eta), "eta_floored": eta_flagged,
            "adjoint": jadj,
            # THE COMPARISON BASIS, CARRIED VERBATIM AND NEVER RECOMPUTED.  The
            # grader re-reads the SAME source independently: two channels, and a
            # disagreement refuses.
            "adjoint_np1_reference": opt["adjoint"],
            "adjoint_np1_nprocs": int(opt["nprocs"]),
            "adjoint_np1_source": os.path.abspath(opt_path),
            "rows": rows, "n_rows": len(rows),
            "note_section_5": (
                "DAFOAM_CHARTER.md section 5: this table states its decomposition "
                "method and, for `simple`, its subdivision, in the same artefact as "
                "the number.  The np = 1 gradient beside it is SO-1b's, read from "
                "disk and never recomputed; the FD table beside it is THIS "
                "configuration's own, because an FD reference is part of a "
                "configuration and is never carried across np."),
        }
        with open(OUT_N, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.flush()
            os.fsync(fh.fileno())
        sys.stdout.write("SO1CR_DECOMP method=%s n_subdomains=%s simple_n=%s\n"
                         % (decomp.get("decomp_method"),
                            decomp.get("decomp_n_subdomains"),
                            decomp.get("decomp_simple_n")))
        sys.stdout.write("SO1CR_N_WRITTEN %s n_rows=%d\n" % (OUT_N, len(rows)))
    MPI.COMM_WORLD.Barrier()


if __name__ == "__main__":
    main()
