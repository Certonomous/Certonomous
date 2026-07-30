#!/usr/bin/env python3
"""
check_convergence.py -- classify a solver log as CONVERGED, NOT_CONVERGED, or
CANNOT_TELL, from the solver's OWN convergence statements and raw residual
statistics. Never from a single quoted residual number, and never from a
process exit code.

WHY THIS EXISTS. Six times in one night this project published a number as
sound that came from a run which had not met its own convergence criterion,
and every one of the six was caught by someone looking at something else
(L-14, L-15, and this session's own hump/A4/TMR/wall.json findings). Nobody
had ever swept for this deliberately, and there was no reusable tool to wire
into the one place every run already passes through: scripts/launch_solve.sh's
collector.

THE FOUR SIGNATURES THIS CHECKER IS BUILT AGAINST (all real, all found the
same night this file was written):

  1. A normalised per-field residual collapses to a tiny fixed value and
     stops moving -- reads as convergence -- while a separate RAW residual
     statistic (DAFoam's own "Printing Primal Residual Statistics" block)
     shows a catastrophic blow-up. (A4 Ahmed body: omega Initial residual
     sat at 5.87e-31 for 450 straight iterations while the raw
     "omega Residual Norm2" was 1.13e+35.)
  2. A PETSc-backed solve exits zero and prints its own "solution finished"
     message over a residual that has underflowed to denormal range.
     PetscConvergedReason is NEGATIVE the whole time; nothing about the exit
     code or the printed success sentence says so. (The 79,560-cell ONERA M6
     adjoint probe: KSP residual 1.48e-322, PetscConvergedReason -5
     (DIVERGED_BREAKDOWN), printed "Residual tolerance satisfied, solution
     finished!" anyway.)
  3. A steady SIMPLE-family run reaches its iteration cap having NEVER
     printed the solver's own "SIMPLE solution converged in N iterations"
     statement, and a residual number from partway through is quoted as if
     the run were done. (kOmega's first attempt, and the oneC/twoC full
     eigenvalue-perturbation corners.)
  4. A residual is quoted from the FINAL column of an OpenFOAM linear-solve
     line ("Initial residual = X, Final residual = Y") when the actual gate
     (residualControl) is checked against the INITIAL column. The two sit
     right next to each other and the Final one is always smaller, which is
     exactly what makes it tempting to misread. (The r4 sweep's Delta=0.25
     point.)

THE RULE THIS CHECKER ENFORCES: only the solver's own convergence statement
(OpenFOAM's "SIMPLE solution converged" string, or PETSc's own
ConvergedReason) counts as a positive signal, cross-checked against raw
residual statistics where available, and the INITIAL residual is the only
one ever compared to a gate. A process exit code and a solver's own
prose "success" message are both explicitly NOT trusted (signature 2).

USAGE
    check_convergence.py <log_file> [--case CASE_DIR] [--json]
    python3 -c "from check_convergence import classify; print(classify('x.log'))"

Exit code: 0 = CONVERGED, 1 = NOT_CONVERGED, 2 = CANNOT_TELL, 3 = usage/IO error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Tunable thresholds. Kept in one place and named, not scattered as magic
# numbers, so a future reader can see exactly what "denormal" and "blown up"
# mean to this checker without reading the logic.
# ---------------------------------------------------------------------------

# A residual below this is not a well-converged value, it is numerical noise
# collapsing toward the float64 denormal floor (~5e-324). Real converged
# residuals in this project's cases bottom out around 1e-9 to 1e-14; nothing
# legitimate sits anywhere near 1e-250. This is signature 1 and signature 2.
DENORMAL_FLOOR = 1e-250

# A raw (unnormalised) DAFoam "Residual Norm2" statistic bigger than this is
# not a slow transient, it is a blown-up field. Genuinely converging runs in
# this project's own logs sit under ~1e4 even mid-run; the confirmed blow-up
# case (A4) was 1.13e+35, the confirmed sane case (A4 coarse) was 1.13e+35
# vs 1848 -- thirty-two orders apart. 1e6 leaves enormous headroom below the
# real failure and well above any real mid-run transient seen this session.
RAW_RESIDUAL_BLOWUP = 1e6

# Crash signatures that make "did it converge" moot -- it didn't finish.
CRASH_PATTERNS = [
    r"FOAM FATAL ERROR",
    r"FOAM FATAL IO ERROR",
    r"Segmentation fault",
    r"exited on signal \d+ \(Killed\)",
    r"SIGFPE",
    r"[Ff]loating[- ][Pp]oint [Ee]xception",
    r"std::bad_alloc",
    r"mpirun noticed that process rank",
    r"MPI_ABORT",
    r"Out of memory",
    r"Killed process \d+",
]

# Steady-family OpenFOAM/DAFoam solvers this project uses. Matched against
# the log's "Exec :" banner when present. Absence of a banner match is NOT
# by itself disqualifying -- some DAFoam runs are driven through a Python/
# pyDAFoam wrapper that never prints the plain OpenFOAM "Exec :" line for
# the actual solve (confirmed on A4 and A6 tonight: both show real
# "Solving for <field>, Initial residual" lines with no matching Exec
# banner). Content-based detection (see `_looks_steady_family`) is the
# primary signal; the Exec banner is a secondary corroboration only.
STEADY_FAMILY_EXEC = re.compile(r"Exec\s*:\s*.*\b(\w*[Ss]impleFoam\w*)\b")
TRANSIENT_FAMILY_EXEC = re.compile(
    r"Exec\s*:\s*.*\b(\w*[Pp]impleFoam\w*|\w*[Pp]isoFoam\w*|interFoam|rhoCentralFoam)\b"
)

RE_SIMPLE_CONVERGED = re.compile(r"SIMPLE solution converged in (\d+) iterations", re.IGNORECASE)
RE_TIME = re.compile(r"^Time = ([0-9.eE+-]+)\s*$", re.MULTILINE)
RE_SOLVING_LINE = re.compile(
    r"Solving for (\w+),\s*Initial residual\s*=\s*([0-9.eE+-]+),\s*Final residual\s*=\s*([0-9.eE+-]+)"
)
RE_PETSC_REASON = re.compile(r"PetscConvergedReason:\s*(-?\d+)")
RE_KSP_RESIDUAL = re.compile(r"KSP Residual norm\s+([0-9.eE+-]+)")
RE_RAW_STATS_BLOCK = re.compile(r"Printing Primal Residual Statistics\.(.*?)(?:\n\s*\n|\Z)", re.DOTALL)
RE_RAW_STATS_FIELD = re.compile(r"(\w+) Residual (?:Norm2|Mean|Max):\s*([\(\)0-9.eE+\- ]+)")

# PETSc KSPConvergedReason codes worth naming in the report (not exhaustive --
# any positive code is treated as converged, any negative as failed, per
# PETSc's own convention; these labels are just for a readable reason string).
PETSC_REASON_LABELS = {
    2: "CONVERGED_RTOL_NORMAL", 3: "CONVERGED_ATOL_NORMAL", 4: "CONVERGED_ITS",
    -2: "DIVERGED_NULL", -3: "DIVERGED_ITS", -4: "DIVERGED_DTOL",
    -5: "DIVERGED_BREAKDOWN", -6: "DIVERGED_BREAKDOWN_BICG",
    -7: "DIVERGED_NONSYMMETRIC", -8: "DIVERGED_INDEFINITE_PC",
    -9: "DIVERGED_NANORINF", -10: "DIVERGED_INDEFINITE_MAT",
    -11: "DIVERGED_PC_FAILED",
}

UTILITY_EXEC = {
    "decomposePar", "reconstructPar", "blockMesh", "snappyHexMesh", "checkMesh",
    "surfaceFeatureExtract", "topoSet", "createPatch", "refineMesh", "renumberMesh",
}


def _read(path: Path, cap_bytes: int = 60_000_000) -> str:
    size = path.stat().st_size
    with open(path, "r", errors="replace") as f:
        if size > cap_bytes:
            # Convergence evidence (the strings this checker looks for) lives
            # at the END of a log almost without exception. Read a generous
            # head (for Exec banners / early context) and a generous tail
            # (for the actual verdict) rather than truncating blindly.
            head = f.read(cap_bytes // 4)
            f.seek(max(0, size - (cap_bytes * 3) // 4))
            tail = f.read()
            return head + "\n...[truncated, large log]...\n" + tail
        return f.read()


def _find_crash(text: str) -> Optional[str]:
    # OpenFOAM prints a harmless startup banner --
    # "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)" --
    # on every single run, whether or not one ever occurs. It contains the
    # substring "SIGFPE" and the phrase "Floating point exception" as pure
    # boilerplate; skip any line containing "trapping enabled" so this
    # banner can never be mistaken for a real crash.
    for line in text.splitlines():
        if "trapping enabled" in line or line.strip().startswith("trapFpe:"):
            continue
        for pat in CRASH_PATTERNS:
            m = re.search(pat, line)
            if m:
                return f"{pat!r} matched: {line.strip()!r}"
    return None


def _looks_steady_family(text: str) -> bool:
    """Content-based steady-solver detection, independent of the Exec banner
    (which pyDAFoam-wrapped runs often omit for the actual solve step)."""
    if STEADY_FAMILY_EXEC.search(text):
        return True
    if TRANSIENT_FAMILY_EXEC.search(text):
        return False
    if not RE_SOLVING_LINE.search(text):
        return False
    # Distinguish pseudo-time SIMPLE iteration (Time = 1, 2, 3, ... this
    # project's universal steady convention) from real transient marching
    # (Time = 0.00448..., adaptive fractional deltaT). Check the first few
    # Time values found.
    times = RE_TIME.findall(text)[:5]
    if not times:
        return False
    try:
        floats = [float(t) for t in times]
    except ValueError:
        return False
    # Steady pseudo-time: integer-valued, monotonically increasing by a
    # constant step (usually 1).
    return all(abs(v - round(v)) < 1e-9 for v in floats)


def _last_petsc_reasons(text: str) -> list[int]:
    return [int(x) for x in RE_PETSC_REASON.findall(text)]


def _raw_stats_blowup(text: str) -> Optional[dict]:
    """Parse DAFoam's 'Printing Primal Residual Statistics' block if present
    and report any field whose raw Norm2 exceeds RAW_RESIDUAL_BLOWUP, or is
    inf/nan. Returns None if no such block exists in the log at all (not
    every solver prints one) -- absence here means "no corroboration
    available", not "clean"."""
    blocks = RE_RAW_STATS_BLOCK.findall(text)
    if not blocks:
        return None
    block = blocks[-1]  # last one = end-of-run state
    offenders = {}
    for field, raw in RE_RAW_STATS_FIELD.findall(block):
        if not field.endswith("Norm2") and "Norm2" not in raw:
            pass
        # values can be scalar or a parenthesised vector "(a b c)"
        nums = re.findall(r"[0-9.eE+-]+", raw)
        for n in nums:
            try:
                v = float(n)
            except ValueError:
                continue
            if v != v or v in (float("inf"), float("-inf")) or abs(v) > RAW_RESIDUAL_BLOWUP:
                offenders.setdefault(field, []).append(v)
    return {"block_found": True, "offenders": offenders} if True else None


def _last_solving_lines(text: str) -> dict:
    """Last Initial/Final residual seen per field, and whether it is
    suspiciously denormal (signature 1/2)."""
    out = {}
    for field, init_r, final_r in RE_SOLVING_LINE.findall(text):
        out[field] = {"initial": float(init_r), "final": float(final_r)}
    return out


def _parse_residual_control(case_dir: Path) -> Optional[dict]:
    """Best-effort parse of system/fvSolution's residualControl block. Not
    required for a verdict -- enrichment only."""
    fv = case_dir / "system" / "fvSolution"
    if not fv.exists():
        return None
    try:
        text = fv.read_text(errors="replace")
    except OSError:
        return None
    m = re.search(r"residualControl\s*\{(.*?)\}", text, re.DOTALL)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        line = line.strip().strip('"').rstrip(";")
        parts = line.split()
        if len(parts) == 2:
            key, val = parts
            try:
                out[key.strip('"()|').replace("|", ",")] = float(val)
            except ValueError:
                continue
    return out or None


def classify(log_path: str, case_dir: Optional[str] = None) -> dict:
    path = Path(log_path)
    if not path.exists():
        return {"log": log_path, "status": "CANNOT_TELL", "solver_type": "n/a",
                 "reason": f"log file not found: {log_path}", "detail": {}}
    if path.is_dir():
        return {"log": log_path, "status": "CANNOT_TELL", "solver_type": "n/a",
                 "reason": f"path is a directory, not a log file: {log_path}", "detail": {}}

    text = _read(path)
    if not text.strip():
        return {"log": log_path, "status": "CANNOT_TELL", "solver_type": "n/a",
                 "reason": "log file is empty", "detail": {}}

    result = {"log": str(path), "detail": {}}

    # ---- 1. PETSc/adjoint context -----------------------------------------
    petsc_reasons = _last_petsc_reasons(text)
    if petsc_reasons:
        result["solver_type"] = "petsc_adjoint"
        result["detail"]["petsc_reasons"] = petsc_reasons
        labeled = [f"{r} ({PETSC_REASON_LABELS.get(r, 'unknown code')})" for r in petsc_reasons]
        result["detail"]["petsc_reasons_labeled"] = labeled
        ksp_residuals = [float(x) for x in RE_KSP_RESIDUAL.findall(text)]
        if ksp_residuals:
            result["detail"]["last_ksp_residual"] = ksp_residuals[-1]
        if any(r < 0 for r in petsc_reasons):
            result["status"] = "NOT_CONVERGED"
            neg = [r for r in petsc_reasons if r < 0]
            reason = (f"PetscConvergedReason negative ({labeled}); solve reports "
                      f"failure regardless of exit code or any printed success message")
            if ksp_residuals and ksp_residuals[-1] < DENORMAL_FLOOR:
                reason += (f". Signature match: last KSP residual {ksp_residuals[-1]:.3e} is in "
                           f"denormal range (<{DENORMAL_FLOOR:.0e}) -- collapsed, not converged "
                           f"(same pattern as the 79,560-cell ONERA M6 adjoint probe)")
            result["reason"] = reason
            return result
        else:
            # all positive -- but still guard against a denormal residual
            # sitting behind a nominally-positive reason code (not observed
            # yet; defensive, per signature 2's exact concern).
            if ksp_residuals and ksp_residuals[-1] < DENORMAL_FLOOR:
                result["status"] = "NOT_CONVERGED"
                result["reason"] = (f"PetscConvergedReason positive ({labeled}) but the last KSP "
                                     f"residual {ksp_residuals[-1]:.3e} is in denormal range -- "
                                     f"treated as collapsed, not converged, on the same reasoning "
                                     f"as signature 2, even though the reason code alone would read clean")
                return result
            result["status"] = "CONVERGED"
            result["reason"] = f"PetscConvergedReason positive for all solves ({labeled})"
            return result

    # ---- 2. Crash signature, no PETSc context ------------------------------
    crash = _find_crash(text)

    # ---- 3. OpenFOAM steady-SIMPLE family -----------------------------------
    if _looks_steady_family(text):
        result["solver_type"] = "openfoam_simple"
        m_list = list(RE_SIMPLE_CONVERGED.finditer(text))
        raw = _raw_stats_blowup(text)
        last_fields = _last_solving_lines(text)
        result["detail"]["last_solving_lines"] = last_fields
        if raw and raw["offenders"]:
            result["detail"]["raw_residual_stats"] = raw

        # Enrichment: compare last Initial residual per field to the case's
        # own residualControl, if the case directory is available. Diagnostic
        # only -- never overrides the solver's own convergence statement.
        rc = None
        if case_dir:
            rc = _parse_residual_control(Path(case_dir))
            if rc:
                result["detail"]["residual_control"] = rc
                over = {}
                for group, tol in rc.items():
                    fields = [f for f in group.split(",") if f]
                    if not fields:
                        fields = [group]
                    for f in fields:
                        if f in last_fields and last_fields[f]["initial"] > tol:
                            over[f] = {"initial": last_fields[f]["initial"], "tolerance": tol,
                                       "times_over": last_fields[f]["initial"] / tol}
                if over:
                    result["detail"]["fields_over_gate_at_initial_residual"] = over

        if m_list:
            n_iter = int(m_list[-1].group(1))
            result["detail"]["iterations_at_convergence"] = n_iter
            if raw and raw["offenders"]:
                # Signature 1: solver's own string says converged, raw stats
                # disagree catastrophically. Raw evidence wins.
                result["status"] = "NOT_CONVERGED"
                result["reason"] = (f"'SIMPLE solution converged in {n_iter} iterations' was printed, "
                                     f"BUT raw residual statistics show a blow-up in "
                                     f"{list(raw['offenders'].keys())} "
                                     f"(exceeds {RAW_RESIDUAL_BLOWUP:.0e} or is inf/nan) -- the printed "
                                     f"convergence declaration is not trusted over the raw statistics "
                                     f"(signature 1: normalised residual collapsed to a fixed value "
                                     f"while the raw field diverged)")
                return result
            result["status"] = "CONVERGED"
            result["reason"] = f"solver printed 'SIMPLE solution converged in {n_iter} iterations'"
            return result

        # No convergence string. Distinguish crash from ran-to-cap for the
        # reason text, but both are NOT_CONVERGED.
        if crash:
            result["status"] = "NOT_CONVERGED"
            result["reason"] = f"no 'SIMPLE solution converged' string, and the log shows a crash: {crash}"
            return result

        if raw and raw["offenders"]:
            result["status"] = "NOT_CONVERGED"
            result["reason"] = (f"no 'SIMPLE solution converged' string, and raw residual statistics "
                                 f"confirm a blow-up in {list(raw['offenders'].keys())} "
                                 f"(signature 1 pattern, e.g. A4 Ahmed body)")
            return result

        # Suspicious-but-not-blown-up denormal check on the per-field lines
        # themselves (signature 1 can also show up here without a raw-stats
        # block being present at all).
        denormal_fields = {f: v["initial"] for f, v in last_fields.items()
                            if 0 < v["initial"] < DENORMAL_FLOOR}
        if denormal_fields:
            result["status"] = "NOT_CONVERGED"
            result["reason"] = (f"no 'SIMPLE solution converged' string, and field(s) "
                                 f"{list(denormal_fields.keys())} show a denormal-range Initial "
                                 f"residual ({denormal_fields}) with no convergence declaration -- "
                                 f"treated as collapsed, not converged")
            return result

        if not RE_TIME.search(text):
            result["status"] = "CANNOT_TELL"
            result["reason"] = "looked like a steady OpenFOAM log but no 'Time = ' progression found"
            return result

        result["status"] = "NOT_CONVERGED"
        result["reason"] = ("no 'SIMPLE solution converged' string anywhere in the log -- ran to its "
                             "iteration cap (or was interrupted) without ever meeting its own gate "
                             "(signature 3: e.g. kOmega's first attempt, the oneC/twoC full corners)")
        return result

    # ---- 4. Not a recognised steady/adjoint log ----------------------------
    if crash:
        result["solver_type"] = "unrecognized"
        result["status"] = "NOT_CONVERGED"
        result["reason"] = f"crash signature found, no convergence evidence of any kind: {crash}"
        return result

    has_solving_lines = bool(RE_SOLVING_LINE.search(text))
    looks_transient = TRANSIENT_FAMILY_EXEC.search(text) or (
        has_solving_lines and RE_TIME.search(text) and not _looks_steady_family(text)
    )
    if looks_transient:
        result["solver_type"] = "transient_or_other"
        result["status"] = "CANNOT_TELL"
        result["reason"] = ("looks like a transient/unsteady run (fractional Time progression or a "
                             "transient solver banner) -- a steady-state convergence gate does not "
                             "apply here, and this checker does not implement a statistical-"
                             "stationarity check. Needs a human/different tool, not a false PASS.")
        return result
    if RE_TIME.search(text) and not has_solving_lines:
        result["solver_type"] = "unrecognized"
        result["status"] = "CANNOT_TELL"
        result["reason"] = ("a 'Time = ' progression is present but no per-field 'Solving for <field>, "
                             "Initial residual' lines were found in a recognisable format -- likely a "
                             "solver driven through a wrapper that reformats or omits the standard "
                             "OpenFOAM residual printout (seen tonight on A6/CRM's compressible solver "
                             "log). Not evidence of failure -- this checker cannot read this log's "
                             "convergence state and says so rather than guessing.")
        return result

    result["solver_type"] = "unrecognized"
    result["status"] = "CANNOT_TELL"
    result["reason"] = ("no recognised solver-convergence pattern found (no PETSc ConvergedReason, "
                         "no OpenFOAM 'Solving for <field>' lines) -- likely a utility log "
                         "(decomposePar/blockMesh/checkMesh/etc.), a non-OpenFOAM tool, or a format "
                         "this checker does not yet understand. Not evidence of failure.")
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log", help="path to a solver log file")
    ap.add_argument("--case", default=None, help="case directory (for residualControl enrichment)")
    ap.add_argument("--json", action="store_true", help="emit full JSON instead of one summary line")
    ap.add_argument("--oneline", action="store_true", help="emit a single compact 'STATUS: reason' line (for the collector)")
    args = ap.parse_args()

    result = classify(args.log, args.case)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    elif args.oneline:
        print(f"{result['status']}: {result.get('reason', '')}")
    else:
        print(f"log:    {result['log']}")
        print(f"status: {result['status']}")
        print(f"type:   {result.get('solver_type', 'n/a')}")
        print(f"reason: {result.get('reason', '')}")
        if result.get("detail"):
            print("detail:")
            print(json.dumps(result["detail"], indent=2, default=str))

    return {"CONVERGED": 0, "NOT_CONVERGED": 1, "CANNOT_TELL": 2}.get(result["status"], 3)


if __name__ == "__main__":
    sys.exit(main())
