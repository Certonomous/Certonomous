#!/usr/bin/env python3
"""F6c-RSM successor gate: secondary-flow RMS of an RSM duct field vs DNS.

Grades the fresh SSG / EBRSM solves registered in
``verification/campaign/F6C_RSM_SUCCESSOR_PREREGISTRATION.md`` (a DRAFT at the
time of writing; this grader is written for its check-4 freeze and is NOT itself
authorised). The gate quantity is the secondary-flow RMS -- the cross-sectional
root-mean-square of the in-plane velocity magnitude -- as a percentage of
``U_bulk``, compared to the DNS reference.

GATE G-F6cR (per case, prereg section 2): PASS iff RMS/DNS in [0.80, 1.20]
(a +/-20 % validation-agreement band), else GATE FAIL. This is a SINGLE-MESH
model-form gate, NOT a Roache grid-convergence triple: rule 5 does not apply, no
GCI is or may be quoted (prereg section 2, scope limit).

WHY THIS GRADER REFUSES RATHER THAN DEGRADES. Every path that cannot be turned
into defensible evidence exits 2 with a stated reason, never a soft number:
  * absent solver log or absent field -> REFUSE (exit 2) (rule 4, never degrade);
  * an incomplete run (no End, last time != endTime, age-guard breach) -> REFUSE;
  * a planted-zero control that the reader cannot see, or that was never run
    -> REFUSE (rule 3 / L-459: a zero from a reader not shown able to see a
    non-zero is not evidence);
  * a reference PDF handed in without title-page verification -> REFUSE (L-144).

The only values this grader will PRINT AS A VERDICT come from the fixed
vocabulary: PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.

HARD CONSTRAINT of the lane that wrote this: nothing this grader prints is a
result until the cfd-supervisor has read the diff (check 1) and frozen the
grading path against the committed prereg blob (check 4). The grader refuses to
run without ``--prereg-commit`` for exactly that reason.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

# --------------------------------------------------------------------------
# Pinned DNS reference (prereg section 2; provenance secondary_flow_gate.json).
# These are the numbers the gate compares against; they are fixed HERE at the
# freeze, never read from a mutable run artifact.
# --------------------------------------------------------------------------
DNS_PCT_UBULK = {
    "AR_1_Ret_360": 2.2201,   # % U_bulk (DNS 0.7344 m/s / U_bulk 33.0777 m/s)
    "AR_3_Ret_360": 2.07,     # % U_bulk
}
BAND_LO, BAND_HI = 0.80, 1.20   # RMS/DNS PASS band, +/-20 %  (prereg section 2)

# Planted-zero control perturbation (rule 3), m/s in-plane. A known non-zero the
# reader MUST report back through the same code path a real read uses.
PLANT = 1.234e-03

# Fixed verdict vocabulary -- the ONLY strings this grader emits as a verdict.
VERDICTS = {"PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING"}

def required_fields(model: str) -> tuple[str, ...]:
    """Fields a COMPLETED incompressible RSM run must carry at endTime.

    U is the graded field; p, R and epsilon WITNESS that the RSM model was
    actually active. R is the six-component symmetric Reynolds-stress tensor an
    RSM transports directly -- a linear eddy-viscosity run (kOmegaSST, the parent
    model) writes k/omega and NO R, so requiring R makes completion refuse a run
    where the kOmegaSST -> SSG/EBRSM model change did not take. EBRSM additionally
    transports the elliptic-blending scalar f.

    Provenance: F6C_RSM_SUCCESSOR_PREREGISTRATION.md section 3, items 1 and 3
    ("R, epsilon, and for EBRSM the elliptic-blending f"; "the fields the RSM
    actually transports: U, p, epsilon, the six R components, f"). Confirmed
    against the D5 solver field set: verification/runs/D5_rsm_runs/SSG/<endTime>/
    holds {U,p,R,epsilon} and .../EBRSM/<endTime>/ additionally holds f.
    """
    base = ("U", "p", "R", "epsilon")
    return base + ("f",) if model == "EBRSM" else base


class ControlRefused(Exception):
    """Raised when a planted-zero control cannot be seen; converted to exit 2.
    A named exception, never a bare ``assert`` -- asserts vanish under -O and
    are swallowed silently (this grader swallows nothing)."""


def refuse(msg: str) -> "NoReturn":  # noqa: F821
    print(f"REFUSE (exit 2): {msg}")
    sys.exit(2)


# --------------------------------------------------------------------------
# OpenFOAM vector field reader (decomposed, never reconstructed).
# --------------------------------------------------------------------------
def read_of_vector_field(path: str) -> np.ndarray:
    """Parse an OpenFOAM ``nonuniform List<vector>`` internalField from *path*.
    Raises on any malformed field -- the caller decides refuse vs NOT A RESULT."""
    with open(path) as fh:
        txt = fh.read()
    m = re.search(r"nonuniform\s+List<vector>\s*\n(\d+)\s*\n\((.*?)\n\)\s*;?",
                  txt, re.S)
    if m is None:
        raise ValueError(f"no 'nonuniform List<vector>' internalField in {path}")
    n = int(m.group(1))
    vecs = re.findall(r"\(([^()]+)\)", m.group(2))
    arr = np.array([[float(x) for x in v.split()] for v in vecs], dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"{path}: parsed shape {arr.shape}, expected (N,3)")
    if arr.shape[0] != n:
        raise ValueError(f"{path}: header says {n} cells, parsed {arr.shape[0]}")
    return arr


def locate_U_fields(case_dir: str, time: str) -> tuple[list[str], str]:
    """Return the U field paths to read and the mode.

    DECOMPOSED, NEVER RECONSTRUCTED (prereg section 4; F25/F27 precedent). If the
    case is decomposed (``processor*/``) the internal fields are read per
    processor and concatenated -- the reconstructed ``<time>/U``, if present, is
    NEVER read. A serial run's ``<time>/U`` is the native field, not a
    reconstruction, and is read directly.
    """
    proc = sorted(glob.glob(os.path.join(case_dir, "processor*")),
                  key=lambda p: int(re.search(r"processor(\d+)", p).group(1)))
    if proc:
        paths = [os.path.join(p, time, "U") for p in proc]
        missing = [p for p in paths if not os.path.isfile(p)]
        if missing:
            refuse(f"decomposed run missing U at {missing[0]} (and {len(missing)-1} "
                   f"more) -- cannot grade a partial decomposition, never degrade.")
        return paths, "decomposed"
    serial = os.path.join(case_dir, time, "U")
    if os.path.isfile(serial):
        return [serial], "serial"
    refuse(f"no U field found: neither processor*/{time}/U nor {time}/U exists.")


def read_secondary_rms(case_dir: str, time: str,
                       reader=read_of_vector_field) -> tuple[float, int]:
    """Cross-sectional RMS of in-plane (y,z) velocity magnitude, m/s, over all
    interior cells. Streamwise is x; in-plane secondary flow is (Uy, Uz)."""
    paths, _mode = locate_U_fields(case_dir, time)
    blocks = [reader(p) for p in paths]
    U = np.concatenate(blocks, axis=0)
    sec_sq = U[:, 1] ** 2 + U[:, 2] ** 2          # |in-plane|^2 per cell
    return float(np.sqrt(np.mean(sec_sq))), int(U.shape[0])


# --------------------------------------------------------------------------
# Planted-zero control (rule 3), TWO-SIDED.
# --------------------------------------------------------------------------
def _write_vector_fragment(arr: np.ndarray, path: str) -> None:
    body = "\n".join(f"({x[0]:.10g} {x[1]:.10g} {x[2]:.10g})" for x in arr)
    with open(path, "w") as fh:
        fh.write("internalField   nonuniform List<vector>\n"
                 f"{arr.shape[0]}\n(\n{body}\n)\n;\n")


def planted_zero_control(arr: np.ndarray, reader=read_of_vector_field) -> dict:
    """Plant a known non-zero in-plane perturbation into a COPY of the field,
    read it back through the SAME reader, and confirm the plant is visible by
    comparing the read-back array ELEMENTWISE to what was planted.

    REFUSES (ControlRefused) if the reader cannot see the plant -- either it
    fails to reproduce the planted values, or it returns something no different
    from the un-planted field (a reader that ignores its input). A grader must
    have a PASSED control before any zero (or any value) it reports is evidence
    (rule 3 / L-459).
    """
    if PLANT <= 0:
        raise ControlRefused("PLANT is not a positive perturbation")
    planted = arr.copy()
    planted[:, 1] += PLANT
    planted[:, 2] += PLANT
    with tempfile.NamedTemporaryFile("w", suffix=".U", delete=False) as tf:
        tmp = tf.name
    try:
        _write_vector_fragment(planted, tmp)
        back = reader(tmp)
    finally:
        os.unlink(tmp)
    if back.shape != planted.shape:
        raise ControlRefused(
            f"reader returned shape {back.shape}, planted {planted.shape}")
    resid_planted = float(np.max(np.abs(back - planted)))      # -> 0 if seen
    resid_original = float(np.max(np.abs(back - arr)))         # -> PLANT if seen
    tol = 1e-6                                                  # %.10g round-trip
    if resid_planted > tol:
        raise ControlRefused(
            f"planted in-plane perturbation {PLANT} m/s NOT recovered: max "
            f"|read-back - planted| = {resid_planted:.3g} > {tol}. A zero from "
            "this reader would not be evidence.")
    if resid_original < 0.5 * PLANT:
        raise ControlRefused(
            f"reader appears BLIND to the plant: max |read-back - un-planted| = "
            f"{resid_original:.3g}, expected ~{PLANT} -- the reader does not "
            "reflect what was written, so its zero is not evidence.")
    return {"passed": True, "plant_ms": PLANT,
            "resid_read_vs_planted": resid_planted,
            "resid_read_vs_unplanted": resid_original}


# --------------------------------------------------------------------------
# Strict completion rule (rule 4) -- incompressible RSM analog, with age guard.
# --------------------------------------------------------------------------
def read_end_time(case_dir: str) -> float:
    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse(f"no system/controlDict at {cd} -- cannot establish endTime.")
    with open(cd) as fh:
        txt = fh.read()
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", txt, re.M)
    if m is None:
        refuse("controlDict has no endTime entry.")
    return float(m.group(1))


def check_completion(case_dir: str, time: str, log_path: str | None,
                     model: str) -> list[str]:
    """Return a list of completion failures (empty == run is done). Absent log or
    absent controlDict REFUSE (exit 2); other failures are returned so the caller
    can mark the run NOT A RESULT."""
    fails: list[str] = []
    if log_path is None or not os.path.isfile(log_path):
        refuse(f"solver log absent ({log_path}) -- a run with no log is not a run.")
    with open(log_path, errors="replace") as fh:
        log = fh.read()
    if "\nEnd\n" not in log and not log.rstrip().endswith("End"):
        fails.append("no 'End' line in solver log")
    end_time = read_end_time(case_dir)
    # last time == endTime (compare the requested grading time to endTime)
    try:
        if abs(float(time) - end_time) > 1e-9 * max(1.0, abs(end_time)):
            fails.append(f"graded time {time} != controlDict endTime {end_time}")
    except ValueError:
        fails.append(f"graded time {time!r} is not numeric")
    # required fields present at the graded time
    proc0 = sorted(glob.glob(os.path.join(case_dir, "processor0")))
    field_root = os.path.join(proc0[0], time) if proc0 else os.path.join(case_dir, time)
    for f in required_fields(model):
        if not os.path.isfile(os.path.join(field_root, f)):
            fails.append(f"required field {f} absent at {field_root} "
                         f"(RSM model witness; kOmegaSST would not write it)")
    # age guard: the graded U must be NEWER than the case's own 0/U (touched last
    # at launch, so it dates the run that produced the answer).
    zero_U = os.path.join(case_dir, "0", "U")
    graded_U = os.path.join(field_root, "U")
    if os.path.isfile(zero_U) and os.path.isfile(graded_U):
        if os.path.getmtime(graded_U) <= os.path.getmtime(zero_U):
            fails.append("age-guard breach: graded U is not newer than 0/U")
    elif not os.path.isfile(zero_U):
        fails.append("no 0/U to run the age guard against")
    return fails


# --------------------------------------------------------------------------
# L-144 -- any reference PAPER read must be title-page verified.
# --------------------------------------------------------------------------
def guard_reference_pdf(path: str | None) -> None:
    if path is None:
        return  # the DNS reference is pinned as numbers above, no paper is read
    refuse(f"reference PDF {path} handed in, but this grader pins the DNS numbers "
           "at the freeze and title-page verification (L-144) is not implemented "
           "here -- refusing rather than trusting a filename.")


# --------------------------------------------------------------------------
# Grade
# --------------------------------------------------------------------------
def grade_case(case_dir: str, time: str, case_key: str, model: str,
               log_path: str | None, Ub: float | None) -> dict:
    if case_key not in DNS_PCT_UBULK:
        refuse(f"no pinned DNS reference for case {case_key!r}; known: "
               f"{sorted(DNS_PCT_UBULK)}")
    dns_pct = DNS_PCT_UBULK[case_key]

    # (1) completion first -- an incomplete run is not graded
    fails = check_completion(case_dir, time, log_path, model)
    if fails:
        return {"case": case_key, "model": model, "verdict": "NOT A RESULT",
                "reason": "; ".join(fails)}

    # (2) read the field (decomposed, never reconstructed)
    try:
        rms_ms, n_cells = read_secondary_rms(case_dir, time)
        arr, _ = _read_all_U(case_dir, time)
    except ValueError as exc:
        return {"case": case_key, "model": model, "verdict": "NOT A RESULT",
                "reason": f"field read failed: {exc}"}

    # (3) planted-zero control -- MUST pass before any value is evidence
    control = planted_zero_control(arr)   # raises ControlRefused -> exit 2

    # (4) normalise and grade against the pinned band
    if Ub is None:
        Ub = float(np.mean(arr[:, 0]))    # bulk approx = mean streamwise velocity
    rms_pct = 100.0 * rms_ms / Ub
    ratio = rms_pct / dns_pct
    verdict = "PASS" if BAND_LO <= ratio <= BAND_HI else "GATE FAIL"
    return {
        "case": case_key, "model": model, "verdict": verdict,
        "n_cells": n_cells, "Ubulk_ms": Ub,
        "secondary_rms_ms": rms_ms, "secondary_rms_pct_Ubulk": rms_pct,
        "dns_pct_Ubulk": dns_pct, "ratio_to_dns": ratio,
        "band": [BAND_LO, BAND_HI], "gci_quoted": False,  # single mesh, rule 5 N/A
        "planted_zero_control": control,
    }


def _read_all_U(case_dir: str, time: str) -> tuple[np.ndarray, int]:
    paths, _ = locate_U_fields(case_dir, time)
    U = np.concatenate([read_of_vector_field(p) for p in paths], axis=0)
    return U, int(U.shape[0])


# --------------------------------------------------------------------------
# Selftest -- the plant fired in the REFUSING direction (rule 3 / L-459).
# --------------------------------------------------------------------------
def selftest() -> int:
    rng = np.random.default_rng(6)
    n = 400
    # a synthetic field with a KNOWN non-zero in-plane secondary flow
    U = np.zeros((n, 3))
    U[:, 0] = 30.0 + rng.normal(0, 0.5, n)          # streamwise ~ U_bulk 30
    U[:, 1] = rng.normal(0, 0.40, n)                # in-plane y
    U[:, 2] = rng.normal(0, 0.40, n)                # in-plane z
    known_rms = float(np.sqrt(np.mean(U[:, 1] ** 2 + U[:, 2] ** 2)))
    print(f"[selftest] synthetic field: {n} cells, known in-plane RMS "
          f"{known_rms:.6f} m/s")

    # (a) SEEN direction: the real reader recovers the plant
    ok = planted_zero_control(U, reader=read_of_vector_field)
    print(f"[selftest] CONTROL SEEN: real reader recovers the {PLANT} m/s plant; "
          f"max|read-planted|={ok['resid_read_vs_planted']:.2e}, "
          f"max|read-unplanted|={ok['resid_read_vs_unplanted']:.4f} "
          f"(~PLANT) -> control PASSED")

    # (b) REFUSING direction: a BLIND reader that ignores the plant (returns the
    #     un-planted field). The control MUST fire (ControlRefused) -- proving it
    #     has teeth and a zero from such a reader would be rejected.
    def blind_reader(_path):
        return U.copy()   # ignores whatever was written -- cannot see the plant
    fired = False
    try:
        planted_zero_control(U, reader=blind_reader)
    except ControlRefused as exc:
        fired = True
        print(f"[selftest] CONTROL FIRED (refusing direction): {exc}")
    if not fired:
        print("[selftest] FAIL: the control did NOT fire against a blind reader "
              "-- it has no teeth.")
        return 1

    # (c) a band-grade sanity check on the pinned numbers (no run touched)
    dns = DNS_PCT_UBULK["AR_1_Ret_360"]
    for pct, want in ((dns * 1.10, "PASS"), (dns * 0.52, "GATE FAIL")):
        got = "PASS" if BAND_LO <= (pct / dns) <= BAND_HI else "GATE FAIL"
        tag = "ok" if got == want else "MISMATCH"
        print(f"[selftest] band: {pct:.4f} %% -> {got} (expected {want}) [{tag}]")
        if got != want:
            return 1
    # every emitted verdict is from the fixed vocabulary (explicit check, not a
    # bare assert -- asserts vanish under -O, which this file refuses to rely on)
    if not {"PASS", "GATE FAIL", "NOT A RESULT"} <= VERDICTS:
        print("[selftest] FAIL: emitted verdicts are not a subset of the fixed "
              "verdict vocabulary")
        return 1

    # (d) RSM MODEL WITNESS: completion must refuse a run that carries no
    #     Reynolds-stress field R -- the kOmegaSST -> SSG/EBRSM model change did
    #     not take. Build a temp case whose endTime holds U/p/epsilon but NO R.
    for model, extra in (("SSG", []), ("EBRSM", ["f"])):
        want = required_fields(model)
        if "R" not in want or "epsilon" not in want:
            print(f"[selftest] FAIL: {model} required fields {want} miss R/epsilon")
            return 1
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "system"))
        os.makedirs(os.path.join(td, "0"))
        os.makedirs(os.path.join(td, "1000"))
        with open(os.path.join(td, "system", "controlDict"), "w") as fh:
            fh.write("endTime 1000;\n")
        open(os.path.join(td, "0", "U"), "w").close()
        log = os.path.join(td, "log.run")
        with open(log, "w") as fh:
            fh.write("... solving ...\nEnd\n")
        # endTime carries U, p, epsilon but NOT R; make them newer than 0/U
        for f in ("U", "p", "epsilon"):
            open(os.path.join(td, "1000", f), "w").close()
        os.utime(os.path.join(td, "0", "U"), (1, 1))
        fails_noR = check_completion(td, "1000", log, "SSG")
        if not any("required field R absent" in f for f in fails_noR):
            print(f"[selftest] FAIL: an R-less SSG run was NOT refused -- the "
                  f"model witness has no teeth. fails={fails_noR}")
            return 1
        print("[selftest] RSM WITNESS FIRED: an SSG run missing R -> NOT A RESULT "
              f"({[f for f in fails_noR if 'field R' in f][0]})")
        # now add R (and f is only required for EBRSM): the R-absence must clear
        open(os.path.join(td, "1000", "R"), "w").close()
        fails_R = check_completion(td, "1000", log, "SSG")
        if any("required field R absent" in f for f in fails_R):
            print(f"[selftest] FAIL: R present but still flagged absent: {fails_R}")
            return 1
        print("[selftest] RSM WITNESS CLEARS: with R written, the SSG completion "
              "no longer flags a missing stress field")

    print("[selftest] SELFTEST PASS: two-sided planted control has teeth "
          "(SEEN passes, blind reader REFUSED); RSM model witness R refuses a "
          "run that did not transport the Reynolds stresses; band grader maps to "
          "the fixed verdict vocabulary.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="F6c-RSM secondary-flow gate")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--prereg-commit",
                    help="git commit of the frozen F6c-RSM prereg (rule 2). "
                         "Required for a real grade; the supervisor hashes the "
                         "disk blob against it at check 4.")
    ap.add_argument("--case-dir")
    ap.add_argument("--time")
    ap.add_argument("--case-key", choices=sorted(DNS_PCT_UBULK))
    ap.add_argument("--model", choices=["SSG", "EBRSM"])
    ap.add_argument("--log")
    ap.add_argument("--reference-pdf", default=None)
    ap.add_argument("--ubulk", type=float, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.prereg_commit:
        refuse("no --prereg-commit: this grader will not produce a verdict "
               "outside a frozen pre-registration (rule 2).")
    guard_reference_pdf(args.reference_pdf)
    for req in ("case_dir", "time", "case_key", "model"):
        if getattr(args, req) is None:
            refuse(f"--{req.replace('_', '-')} is required for a real grade.")

    try:
        result = grade_case(args.case_dir, args.time, args.case_key, args.model,
                            args.log, args.ubulk)
    except ControlRefused as exc:
        refuse(str(exc))

    if result["verdict"] not in VERDICTS:
        refuse(f"internal error: verdict {result['verdict']!r} not in vocabulary")
    result["prereg_commit"] = args.prereg_commit
    print(json.dumps(result, indent=2))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(result, fh, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
