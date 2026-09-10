#!/usr/bin/env python3
"""
check_ladder_preflight.py -- the STANDING INSTRUMENT for VERIFICATION_CHARTER §2bb,
the per-rung PRE-FLIGHT standard.  A ladder is not launched until every rung it will
run has been PRE-FLIGHTED, and this check refuses (exit 2) any ladder whose pre-flight
manifest does not prove it.

WHY THIS EXISTS  (paid for by D6RF9 -- commits e3d9cd8f / a256c14d / c17cbdf3)
------------------------------------------------------------------------------
Two failure shapes recur, and both are cheap to catch BEFORE the solver burns
core-minutes and expensive to untangle after:

  * A DEADLINE THAT CANNOT BE MET.  D6RF9-R2 was given a frozen 855 s deadline and
    its 12-corrector step could never reach endTime inside it (commit 6c9f0f26).
    The run hit rc=124 TIMEOUT, produced an INCOMPLETE tree (rule 4: last time !=
    endTime), and -- crucially -- a timeout is NOT a measured floor-miss, so the
    core physics question was CONFOUNDED rather than answered.  A deadline must be
    sized from a MEASURED per-step wall cost with a safety margin, never hand-typed.
  * A SOLVER PATH THAT WAS NEVER CLEANLY EXERCISED.  D6RF9-R3/R4 crashed rc=59 on a
    decomposePar 'already decomposed' collision (source dirs carried processor dirs).
    Each DISTINCT (solver, decomposition) path a ladder uses must be shown to reach
    its first solve and decompose cleanly ONCE, on disk, before the ladder launches.

A pre-flighted rung therefore carries two independent proofs: a deadline SIZED from a
measured sample with the §2bb 1.25x margin, and a SMOKE run of its solver path whose
log is on disk and whose recorded outcome is clean (rc 0, first solve reached,
decompose ok).

WHAT IT ENFORCES
----------------
Usage:  check_ladder_preflight.py <LADDER_PREFLIGHT.json>

The manifest schema (one entry per rung the ladder will run):

  {
    "ladder_id": "<id>",
    "rungs": [
      {
        "rung": "R2",
        "solver": "DARhoSimpleFoam",
        "decomposition": {"method": "scotch", "nprocs": 4},
        "endTime": 2000,
        "deadline_s": 855,
        "preflight_smoke_log": "<path that MUST exist on disk>",
        "deadline_sizing": {
          "measured_per_step_wall_s": <float>,
          "n_steps_sampled": <int>,
          "steps_to_endTime": <int>,
          "projected_wall_s": <float>
        },
        "solver_path": {"rc": 0, "reached_first_solve": true, "decompose_ok": true},
        "runtime_params": {                       # L-517 launcher-vs-registration
          "registered": {"endTime": 2000, "deltaT": 1.0, "deadline_s": 855, "cap_core_min": <num>},
          "launcher":   {"endTime": 2000, "deltaT": 1.0, "deadline_s": 855, "cap_core_min": <num>},
          "source": {"registration": "<path | git-sha>", "launcher": "<path | git-sha>"}
        },
        "config_exercise": {                      # L-516 + L-504-ref2
          "config_exercised": true,               # the rung's REAL frozen config installed + iterated
          "config_ref": "<path | git-sha>",
          "launcher_paths_fixpointed": true,      # every runtime path-reference asserted present post-stage
          "n_paths_checked": <int>,               # >= 1
          "fixpoint_ref": "<path | git-sha>"
        }
      }
    ]
  }

REFUSAL RULES (exit 2, message names the rung + which rule failed) -- ANY of:
  * manifest missing / unparseable, or "rungs" absent / empty.
  * any rung missing "deadline_sizing" or "solver_path" (that rung is not pre-flighted).
  * DEADLINE SIZING --
      - n_steps_sampled < MIN_STEPS_SAMPLED (a two- or three-step sample is not a
        measurement); OR
      - projected_wall_s != measured_per_step_wall_s * steps_to_endTime within a
        relative tolerance (a hand-typed projection that does not match its own
        sample is fabricated, not measured); OR
      - deadline_s < projected_wall_s * SAFETY (the deadline lacks the 1.25x margin
        the D6RF9-R2 timeout was paid for).
  * SOLVER PATH --
      - preflight_smoke_log does not exist on disk (resolved against the manifest's
        own directory AND cwd); OR
      - solver_path.rc != 0; OR reached_first_solve is not true; OR decompose_ok is
        not true.
  * DISTINCT-PATH COVERAGE -- each rung's path key is f"{solver}|{method}|{nprocs}".
    Every distinct key present among the rungs must be covered by >= 1 rung whose
    solver_path PASSED cleanly.  A key that appears ONLY on rungs that all fail
    solver_path was never cleanly exercised -> REFUSE.  (A rung may thus point at a
    byte-identical sibling's smoke, but every distinct path is smoked at least once.)
  * RUNTIME-PARAM CONSISTENCY (L-517 stale-launcher class) -- each rung's
    "runtime_params":
      - the block, or either "registered"/"launcher" sub-object, absent/not-an-object
        -> REFUSE; OR
      - for each key: launcher != registration (exact for int; REL_TOL+ABS_FLOOR for
        float), or a key present in one but absent in the other -> REFUSE; OR
      - the existing top-level endTime/deadline_s != runtime_params.registered's
        (a manifest whose two copies of the truth disagree) -> REFUSE; OR
      - source.registration or source.launcher does not RESOLVE (a path that exists,
        or a git-sha; mirrors check_exhaustion_evidence.py) -> REFUSE.
  * CONFIG-EXERCISE + PATH FIXPOINT (L-516 / L-504-ref2) -- each rung's
    "config_exercise":
      - the block absent/not-an-object -> REFUSE; OR
      - config_exercised is not true (a static check cannot see an invalid injected
        config) -> REFUSE; OR
      - launcher_paths_fixpointed is not true, or n_paths_checked < 1 -> REFUSE; OR
      - config_ref or fixpoint_ref does not RESOLVE -> REFUSE.

EXIT_OK (0) only if EVERY rung passes deadline-sizing AND every distinct path is
covered by a passing smoke AND every rung's own solver_path passes AND every rung's
runtime_params and config_exercise limbs pass.

WHAT THIS CHECK CANNOT SEE  (stated because a check that overstates its reach is
worse than none):
  * whether the smoke log's recorded outcome is TRUE -- it reads the manifest's
    recorded rc/reached/decompose, not the log's bytes.  The log's EXISTENCE is
    proven here; a human reads it.  (An honest limb: the manifest is the thing
    frozen and audited, and a fabricated recorded outcome is a deeper integrity
    fault the supervisor's crash-triage backstops.)
  * whether the measured per-step cost is representative of the whole run (early
    steps can be cheaper than a fully-developed field).  It checks the ARITHMETIC
    of the projection against the stated sample, and the 1.25x margin absorbs some
    of this; it does not re-run the sample.
  * the runtime-param and config-exercise attestations are MANIFEST-RECORDED, exactly
    like the solver_path outcome.  The check proves the manifest CARRIES the
    launcher==registration equality, the config-exercise attestation and the
    path-fixpoint attestation, and that every declared ref (source.registration,
    source.launcher, config_ref, fixpoint_ref) RESOLVES (a path exists, or a git-sha).
    It does NOT read the launcher's source to re-derive rung_endtime()/rung_cap(),
    nor re-run the config smoke, nor read the referenced record's bytes.  A fabricated
    attestation is a deeper integrity fault the supervisor's §3 crash-triage /
    big-claim backstops.  Requiring each ref to RESOLVE (not a bare bool) is what
    gives these arms teeth beyond a checkbox -- the same posture as
    check_exhaustion_evidence.py.

⚡ THE PLANTED CONTROL  (rule 3, §28.8)
--------------------------------------
`--selftest` builds synthetic manifests in a throwaway tempdir (with REAL temp files
for the smoke logs, so the exists-check is exercised on disk), runs THIS FILE as a
subprocess entry point against each, and asserts the exit code.  It drives BOTH
directions, each RED arm paired with a control that flips it back to prove the arm is
load-bearing:
  GREEN   full pre-flight, 3 rungs / 2 distinct paths (one inherits) -> exit 0
  RED-1   undersized deadline (projected*1.25 > deadline_s)          -> exit 2  (control: bump deadline -> 0)
  RED-2   crashed solver path, ONLY rung on its path (uncovered)     -> exit 2  (control: rc 0 / decompose ok -> 0)
  RED-3   missing deadline_sizing / missing solver_path              -> exit 2
  RED-4   fabricated projection (!= measured*steps)                  -> exit 2  (control: fix arithmetic -> 0)
  RED-5   non-existent smoke log                                     -> exit 2  (control: create the file -> 0)
  RED-6   short sample (n_steps_sampled < MIN_STEPS_SAMPLED)         -> exit 2
  RED-7   launcher endTime != registration (L-517)                  -> exit 2  (control: equalise -> 0)
  RED-8   launcher deltaT != registration (float-tol)               -> exit 2  (control: equalise -> 0)
  RED-9   runtime_params absent                                     -> exit 2
  RED-10  source.registration non-resolving path                    -> exit 2  (control: real file -> 0)
  RED-11  top-level deadline_s != registered.deadline_s             -> exit 2  (control: equalise -> 0)
  RED-12  config_exercised false (L-516)                            -> exit 2  (control: true -> 0)
  RED-13  launcher paths not fixpointed / n=0 (L-504-ref2)          -> exit 2  (control: true / 1 -> 0)
  RED-14  config_ref non-resolving path                             -> exit 2  (control: real file -> 0)
selftest() returns True only if EVERY arm hit its expected exit code, and cleans up
its tempdir.  main() exits EXIT_OK if selftest passed else EXIT_VIOLATION.

Exit codes:  0 = pre-flight complete (PASS);  2 = REFUSED (a rule failed, or an empty
population; a refusal is never a clean bill -- rule 3);  3 = the --selftest plant did
not fire as required (EXIT_VIOLATION, main only).

This file is diff-read by the verification-supervisor before its output is believed
(SUPERVISION §3 check 1); it writes nothing outside its own scratch fixture tree and
it moves no verdict.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile

EXIT_OK, EXIT_REFUSE, EXIT_VIOLATION = 0, 2, 3

# A sample of fewer than this many steps is not a measurement of the per-step cost.
MIN_STEPS_SAMPLED = 5
# The §2bb deadline margin: the deadline must be at least this multiple of the
# projected wall time.  Paid for by D6RF9-R2's rc=124 timeout (commit 6c9f0f26).
SAFETY = 1.25
# Projection-vs-sample arithmetic tolerance: a relative part plus a tiny absolute
# floor, so a genuine float round-trip passes but a hand-typed figure refuses.
REL_TOL = 1e-6
ABS_FLOOR = 1e-9
# A ref (source.registration / source.launcher / config_ref / fixpoint_ref) may be
# a git-sha; this recognises the 7-40 char lowercase-hex form (mirrors
# check_exhaustion_evidence.py).
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def git(repo: str, *args: str) -> tuple[int, str, str]:
    """Run git in `repo`, swallowing failures into the return code.
    (Reused verbatim from check_exhaustion_evidence.py.)"""
    try:
        r = subprocess.run(["git", "-C", repo, *args],
                           capture_output=True, text=True)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except OSError:
        return 1, "", "git unavailable"


def repo_root(start: str) -> str:
    """The git toplevel that contains `start`, else cwd (so git-sha resolution
    has a repository to ask; a non-repo start simply never resolves a sha).
    (Reused verbatim from check_exhaustion_evidence.py.)"""
    rc, out, _ = git(start, "rev-parse", "--show-toplevel")
    return out if rc == 0 and out else os.getcwd()


def ref_resolves(record_dir: str, repo: str, ref) -> bool:
    """A ref resolves iff it is an existing path (as-given / relative to the
    record's own directory / relative to cwd), OR a 7-40 char lowercase-hex
    string naming a commit that exists in `repo`.
    (Reused verbatim from check_exhaustion_evidence.py.)"""
    if not ref or not isinstance(ref, str):
        return False
    cands = [ref, os.path.join(record_dir, ref), os.path.join(os.getcwd(), ref)]
    if any(os.path.exists(c) for c in cands):
        return True
    if SHA_RE.match(ref):
        rc, _, _ = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        if rc == 0:
            return True
    return False


def _smoke_exists(manifest_dir: str, p: str) -> bool:
    """A smoke log path exists if it resolves to a file on disk relative to the
    manifest's OWN directory, relative to cwd, or as given (absolute)."""
    if not p:
        return False
    cands = [p, os.path.join(manifest_dir, p), os.path.join(os.getcwd(), p)]
    return any(os.path.exists(c) for c in cands)


def _path_key(rung: dict) -> str:
    """The distinct-path key f"{solver}|{method}|{nprocs}" -- the (solver,
    decomposition) combination that must be smoked at least once."""
    dec = rung.get("decomposition") or {}
    return f"{rung.get('solver')}|{dec.get('method')}|{dec.get('nprocs')}"


def _solver_path_passed(sp: dict) -> bool:
    return sp.get("rc") == 0 and sp.get("reached_first_solve") is True \
        and sp.get("decompose_ok") is True


# --------------------------------------------------------------------------
# the check
# --------------------------------------------------------------------------
def check_manifest(path: str) -> tuple[int, str]:
    """Validate a ladder pre-flight manifest.  Returns (exit_code, final_line):
    (EXIT_OK, "PASS: ...") when every rung is pre-flighted, else
    (EXIT_REFUSE, "REFUSE: <rung> <reason>")."""
    if not os.path.exists(path):
        return EXIT_REFUSE, f"REFUSE: {path} manifest does not exist on disk"
    try:
        with open(path, errors="replace") as f:
            man = json.load(f)
    except (OSError, ValueError) as e:
        return EXIT_REFUSE, f"REFUSE: {path} manifest unparseable ({e})"
    if not isinstance(man, dict):
        return EXIT_REFUSE, f"REFUSE: {path} manifest is not a JSON object"

    ladder = man.get("ladder_id", "<unnamed-ladder>")
    rungs = man.get("rungs")
    if not isinstance(rungs, list) or not rungs:
        return EXIT_REFUSE, f"REFUSE: {ladder} 'rungs' is absent or empty (nothing pre-flighted)"

    manifest_dir = os.path.dirname(os.path.abspath(path))
    repo = repo_root(manifest_dir)

    # PER-RUNG limbs that refuse on the spot: structure, deadline-sizing, smoke-log
    # existence.  The solver_path pass/fail is RECORDED (not refused on the spot) so
    # the distinct-path COVERAGE limb below is genuinely reachable and load-bearing;
    # a rung whose own solver_path fails is caught either by coverage (its path was
    # never cleanly smoked) or by the final own-path sweep.
    path_cover: dict[str, bool] = {}       # key -> any rung on it passed cleanly
    path_first_rung: dict[str, str] = {}   # key -> first rung name seen on it
    failed_own: list[str] = []             # rung names whose own solver_path failed

    for r in rungs:
        if not isinstance(r, dict):
            return EXIT_REFUSE, f"REFUSE: {ladder} a rung entry is not a JSON object"
        name = r.get("rung", "<unnamed-rung>")

        ds = r.get("deadline_sizing")
        sp = r.get("solver_path")
        if ds is None:
            return EXIT_REFUSE, f"REFUSE: {name} missing deadline_sizing (rung not pre-flighted)"
        if sp is None:
            return EXIT_REFUSE, f"REFUSE: {name} missing solver_path (rung not pre-flighted)"
        if not isinstance(ds, dict):
            return EXIT_REFUSE, f"REFUSE: {name} deadline_sizing is not a JSON object"
        if not isinstance(sp, dict):
            return EXIT_REFUSE, f"REFUSE: {name} solver_path is not a JSON object"

        # ---- DEADLINE SIZING ------------------------------------------------
        try:
            per_step = float(ds["measured_per_step_wall_s"])
            n_steps = int(ds["n_steps_sampled"])
            steps = int(ds["steps_to_endTime"])
            projected = float(ds["projected_wall_s"])
        except (KeyError, TypeError, ValueError) as e:
            return EXIT_REFUSE, f"REFUSE: {name} deadline_sizing malformed ({e})"

        if n_steps < MIN_STEPS_SAMPLED:
            return EXIT_REFUSE, (f"REFUSE: {name} deadline-sizing sample too short "
                                 f"(n_steps_sampled={n_steps} < MIN_STEPS_SAMPLED={MIN_STEPS_SAMPLED})")

        expected = per_step * steps
        if abs(projected - expected) > REL_TOL * abs(expected) + ABS_FLOOR:
            return EXIT_REFUSE, (f"REFUSE: {name} deadline-sizing projection fabricated "
                                 f"(projected_wall_s={projected} != "
                                 f"measured_per_step_wall_s*steps_to_endTime={expected})")

        try:
            deadline = float(r["deadline_s"])
        except (KeyError, TypeError, ValueError) as e:
            return EXIT_REFUSE, f"REFUSE: {name} deadline_s missing or malformed ({e})"

        if deadline < projected * SAFETY:
            return EXIT_REFUSE, (f"REFUSE: {name} undersized deadline "
                                 f"(deadline_s={deadline} < projected_wall_s*{SAFETY}="
                                 f"{projected * SAFETY}; no {SAFETY}x margin -- D6RF9-R2 timeout class)")

        # ---- SOLVER PATH: smoke log must exist (refuse on the spot) ---------
        smoke = r.get("preflight_smoke_log")
        if not _smoke_exists(manifest_dir, smoke):
            return EXIT_REFUSE, (f"REFUSE: {name} preflight_smoke_log does not exist on disk "
                                 f"({smoke!r})")

        # ---- SOLVER PATH: rc / first-solve / decompose (recorded) -----------
        passed = _solver_path_passed(sp)
        if not passed:
            failed_own.append(name)
        key = _path_key(r)
        path_cover[key] = path_cover.get(key, False) or passed
        path_first_rung.setdefault(key, name)

        # ---- RUNTIME-PARAM CONSISTENCY (L-517) ------------------------------
        # The freeze/launch hash-check guards the GRADING-PATH blob; it does NOT
        # catch a stale launcher whose hardcoded per-rung RUNTIME params have
        # diverged from the frozen registration.  Cross-check them here.
        rp_block = r.get("runtime_params")
        if not isinstance(rp_block, dict):
            return EXIT_REFUSE, f"REFUSE: {name} missing runtime_params"
        reg = rp_block.get("registered")
        lau = rp_block.get("launcher")
        if not isinstance(reg, dict) or not isinstance(lau, dict):
            return EXIT_REFUSE, f"REFUSE: {name} missing runtime_params"
        for k in reg:
            if k not in lau:
                return EXIT_REFUSE, (f"REFUSE: {name} runtime param {k!r} present in registration "
                                     f"but absent from launcher -- L-517 stale-launcher class")
        for k in lau:
            if k not in reg:
                return EXIT_REFUSE, (f"REFUSE: {name} runtime param {k!r} present in launcher "
                                     f"but absent from registration -- L-517 stale-launcher class")
        for k, rv in reg.items():
            lv = lau[k]
            if isinstance(rv, float) or isinstance(lv, float):
                try:
                    differ = abs(float(lv) - float(rv)) > REL_TOL * abs(float(rv)) + ABS_FLOOR
                except (TypeError, ValueError):
                    differ = True
            else:
                differ = (lv != rv)
            if differ:
                return EXIT_REFUSE, (f"REFUSE: {name} launcher runtime param {k} ({lv}) != "
                                     f"registration ({rv}) -- L-517 stale-launcher class")
        # manifest self-consistency: the existing top-level endTime/deadline_s must
        # equal runtime_params.registered.{endTime,deadline_s} (a manifest whose own
        # two copies of the truth disagree is fabricated, not measured).
        for k, top in (("endTime", r.get("endTime")), ("deadline_s", deadline)):
            regv = reg.get(k)
            try:
                mism = abs(float(top) - float(regv)) > REL_TOL * abs(float(regv)) + ABS_FLOOR
            except (TypeError, ValueError):
                mism = True
            if mism:
                return EXIT_REFUSE, (f"REFUSE: {name} manifest self-inconsistent: top-level {k} "
                                     f"({top}) != runtime_params.registered.{k} ({regv})")
        # source.registration and source.launcher must each RESOLVE (a path that
        # exists or a git-sha) -- an attestation with a dead reference is not evidence.
        src = rp_block.get("source")
        for k in ("registration", "launcher"):
            ref = src.get(k) if isinstance(src, dict) else None
            if not ref_resolves(manifest_dir, repo, ref):
                return EXIT_REFUSE, (f"REFUSE: {name} runtime_params.source.{k} does not resolve "
                                     f"({ref!r}) -- an attestation with a dead reference is not evidence")

        # ---- CONFIG-EXERCISE + PATH FIXPOINT (L-516 / L-504-ref2) -----------
        # A static check cannot see an invalid injected daOption/config; the rung's
        # REAL frozen config must have been installed and iterated, and every runtime
        # instrument path the launcher references must have been fixpointed post-stage.
        ce = r.get("config_exercise")
        if not isinstance(ce, dict):
            return EXIT_REFUSE, f"REFUSE: {name} missing config_exercise"
        if ce.get("config_exercised") is not True:
            return EXIT_REFUSE, (f"REFUSE: {name} config not exercised -- L-516: a static check "
                                 f"cannot see an invalid injected config")
        try:
            n_paths = int(ce.get("n_paths_checked"))
        except (TypeError, ValueError):
            n_paths = 0
        if ce.get("launcher_paths_fixpointed") is not True or n_paths < 1:
            return EXIT_REFUSE, (f"REFUSE: {name} launcher path-references not fixpointed "
                                 f"-- L-504-ref2 driver path-reference class")
        for k in ("config_ref", "fixpoint_ref"):
            ref = ce.get(k)
            if not ref_resolves(manifest_dir, repo, ref):
                return EXIT_REFUSE, (f"REFUSE: {name} config_exercise.{k} does not resolve "
                                     f"({ref!r}) -- an attestation with a dead reference is not evidence")

    # ---- DISTINCT-PATH COVERAGE ---------------------------------------------
    for key, covered in path_cover.items():
        if not covered:
            return EXIT_REFUSE, (f"REFUSE: {path_first_rung[key]} distinct path {key!r} "
                                 f"never cleanly exercised (no rung on it passed its solver_path smoke)")

    # ---- every rung's OWN solver_path must pass -----------------------------
    if failed_own:
        return EXIT_REFUSE, (f"REFUSE: {failed_own[0]} solver_path did not pass "
                             f"(rc!=0, first solve not reached, or decompose not ok)")

    return EXIT_OK, (f"PASS: ladder {ladder} pre-flight complete "
                     f"({len(rungs)} rungs, {len(path_cover)} distinct paths)")


# --------------------------------------------------------------------------
# selftest -- the planted control, both directions
# --------------------------------------------------------------------------
def _rt(endtime, deadline_s, ref):
    """A valid runtime_params block whose launcher equals its registration and whose
    source refs point at the on-disk fixture `ref`."""
    reg = {"endTime": endtime, "deltaT": 1.0, "deadline_s": deadline_s, "cap_core_min": 250.0}
    return {"registered": dict(reg), "launcher": dict(reg),
            "source": {"registration": ref, "launcher": ref}}


def _ce(ref):
    """A valid config_exercise block: config exercised, paths fixpointed, refs on disk."""
    return {"config_exercised": True, "config_ref": ref,
            "launcher_paths_fixpointed": True, "n_paths_checked": 1, "fixpoint_ref": ref}


def _base_manifest(sm1: str, sm2: str, sm3: str, ref: str) -> dict:
    """The GREEN fixture: 3 rungs, 2 distinct paths.  R1 and R2 share the byte-
    identical scotch/4 path (R2 'inherits' R1's smoked path); R3 is a distinct
    scotch/8 path.  All deadline sizings are arithmetically consistent and carry the
    1.25x margin; all solver_path outcomes pass; every rung carries a valid
    runtime_params (launcher == registration, top-level == registered) and a valid
    config_exercise (bools true, n_paths_checked >= 1, refs -> the real on-disk
    fixture `ref`)."""
    return {
        "ladder_id": "SELFTEST-LADDER",
        "rungs": [
            {"rung": "R1", "solver": "DARhoSimpleFoam",
             "decomposition": {"method": "scotch", "nprocs": 4},
             "endTime": 2000, "deadline_s": 855.0, "preflight_smoke_log": sm1,
             "deadline_sizing": {"measured_per_step_wall_s": 0.3, "n_steps_sampled": 10,
                                 "steps_to_endTime": 2000, "projected_wall_s": 600.0},
             "solver_path": {"rc": 0, "reached_first_solve": True, "decompose_ok": True},
             "runtime_params": _rt(2000, 855.0, ref), "config_exercise": _ce(ref)},
            {"rung": "R2", "solver": "DARhoSimpleFoam",
             "decomposition": {"method": "scotch", "nprocs": 4},   # same path as R1
             "endTime": 2000, "deadline_s": 855.0, "preflight_smoke_log": sm2,
             "deadline_sizing": {"measured_per_step_wall_s": 0.3, "n_steps_sampled": 8,
                                 "steps_to_endTime": 2000, "projected_wall_s": 600.0},
             "solver_path": {"rc": 0, "reached_first_solve": True, "decompose_ok": True},
             "runtime_params": _rt(2000, 855.0, ref), "config_exercise": _ce(ref)},
            {"rung": "R3", "solver": "DARhoSimpleFoam",
             "decomposition": {"method": "scotch", "nprocs": 8},   # distinct path
             "endTime": 2000, "deadline_s": 700.0, "preflight_smoke_log": sm3,
             "deadline_sizing": {"measured_per_step_wall_s": 0.2, "n_steps_sampled": 8,
                                 "steps_to_endTime": 2000, "projected_wall_s": 400.0},
             "solver_path": {"rc": 0, "reached_first_solve": True, "decompose_ok": True},
             "runtime_params": _rt(2000, 700.0, ref), "config_exercise": _ce(ref)},
        ],
    }


def selftest() -> bool:
    """Drive the planted control RED-then-GREEN through THIS FILE's entry point.
    Returns True iff every arm hit its expected exit code."""
    print("=" * 78)
    print("PLANTED CONTROL -- VERIFICATION_CHARTER §2bb / rule 3.  Both directions.")
    print("A pre-flight gate whose refusal has not been shown able to become a pass")
    print("(and back) is worthless.")
    print("=" * 78)

    me = os.path.abspath(__file__)
    ok = True
    tmp = tempfile.mkdtemp(prefix="ladder_preflight_plant_")

    def run_entry(manifest: dict, fname: str) -> int:
        mp = os.path.join(tmp, fname)
        with open(mp, "w") as f:
            json.dump(manifest, f)
        r = subprocess.run([sys.executable, me, mp], capture_output=True, text=True)
        return r.returncode

    def arm(label: str, manifest: dict, want: int, fname: str):
        nonlocal ok
        got = run_entry(manifest, fname)
        good = (got == want)
        ok = ok and good
        print(f"  {label:52s} -> exit {got}  (want {want})  {'PASS' if good else 'FAIL'}")

    try:
        # real smoke-log files on disk, so the exists-check is genuinely exercised
        sm1 = os.path.join(tmp, "smoke_r1.log")
        sm2 = os.path.join(tmp, "smoke_r2.log")
        sm3 = os.path.join(tmp, "smoke_r3.log")
        for s in (sm1, sm2, sm3):
            with open(s, "w") as f:
                f.write("Time = 1\nDILUPBiCGStab: Solving for Ux\n")
        # a real on-disk fixture the runtime-param source refs and the config/fixpoint
        # refs point at, so the resolve-check is genuinely exercised on disk.
        ref = os.path.join(tmp, "ref_fixture.md")
        with open(ref, "w") as f:
            f.write("registration line 517; launcher rung_endtime(); fixpoint evidence.\n")

        # ---- GREEN ---------------------------------------------------------
        arm("GREEN full pre-flight (3 rungs, 2 paths)",
            _base_manifest(sm1, sm2, sm3, ref), EXIT_OK, "green.json")

        # ---- RED-1 undersized deadline + control ---------------------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["deadline_s"] = 700.0        # 600*1.25 = 750 > 700
        arm("RED-1 undersized deadline (750 > 700)",
            m, EXIT_REFUSE, "red1.json")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["deadline_s"] = 900.0        # 750 <= 900: control passes
        m["rungs"][0]["runtime_params"]["registered"]["deadline_s"] = 900.0  # keep self-consistent
        m["rungs"][0]["runtime_params"]["launcher"]["deadline_s"] = 900.0
        arm("RED-1 control: deadline bumped to 900",
            m, EXIT_OK, "red1_ctl.json")

        # ---- RED-2 crashed solver path, only rung on its path + control ----
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][2]["solver_path"] = {"rc": 59, "reached_first_solve": False,
                                        "decompose_ok": False}   # R3 sole rung on scotch/8
        arm("RED-2 crashed solver path, path uncovered",
            m, EXIT_REFUSE, "red2.json")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][2]["solver_path"] = {"rc": 0, "reached_first_solve": True,
                                        "decompose_ok": True}    # control passes
        arm("RED-2 control: solver path clean (rc 0)",
            m, EXIT_OK, "red2_ctl.json")

        # ---- RED-3 missing pre-flight structures ---------------------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        del m["rungs"][1]["deadline_sizing"]
        arm("RED-3a missing deadline_sizing",
            m, EXIT_REFUSE, "red3a.json")
        m = _base_manifest(sm1, sm2, sm3, ref)
        del m["rungs"][1]["solver_path"]
        arm("RED-3b missing solver_path",
            m, EXIT_REFUSE, "red3b.json")

        # ---- RED-4 fabricated projection + control -------------------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["deadline_sizing"]["projected_wall_s"] = 610.0  # != 0.3*2000=600
        arm("RED-4 fabricated projection (610 != 600)",
            m, EXIT_REFUSE, "red4.json")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["deadline_sizing"]["projected_wall_s"] = 600.0  # arithmetic fixed
        arm("RED-4 control: projection matches sample",
            m, EXIT_OK, "red4_ctl.json")

        # ---- RED-5 non-existent smoke log + control ------------------------
        missing = os.path.join(tmp, "does_not_exist_smoke.log")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["preflight_smoke_log"] = missing
        arm("RED-5 non-existent smoke log",
            m, EXIT_REFUSE, "red5.json")
        with open(missing, "w") as f:      # control: create the file
            f.write("Time = 1\n")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["preflight_smoke_log"] = missing
        arm("RED-5 control: smoke log now exists",
            m, EXIT_OK, "red5_ctl.json")

        # ---- RED-6 short sample --------------------------------------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["deadline_sizing"]["n_steps_sampled"] = 3   # < MIN_STEPS_SAMPLED
        arm("RED-6 short sample (n_steps_sampled=3 < 5)",
            m, EXIT_REFUSE, "red6.json")

        # ---- RED-7 launcher endTime != registration (int, exact) + control -
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["runtime_params"]["launcher"]["endTime"] = 1999  # != registered 2000
        arm("RED-7 launcher endTime != registration (L-517)",
            m, EXIT_REFUSE, "red7.json")
        arm("RED-7 control: launcher endTime equalised",
            _base_manifest(sm1, sm2, sm3, ref), EXIT_OK, "red7_ctl.json")

        # ---- RED-8 launcher deltaT != registration (float-tol path) + control
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["runtime_params"]["launcher"]["deltaT"] = 1.001  # != registered 1.0
        arm("RED-8 launcher deltaT != registration (float-tol)",
            m, EXIT_REFUSE, "red8.json")
        arm("RED-8 control: launcher deltaT equalised",
            _base_manifest(sm1, sm2, sm3, ref), EXIT_OK, "red8_ctl.json")

        # ---- RED-9 runtime_params absent -----------------------------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        del m["rungs"][0]["runtime_params"]
        arm("RED-9 runtime_params absent",
            m, EXIT_REFUSE, "red9.json")

        # ---- RED-10 source.registration non-resolving + control ------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["runtime_params"]["source"]["registration"] = "no_such_registration_ZZZ.md"
        arm("RED-10 source.registration non-resolving path",
            m, EXIT_REFUSE, "red10.json")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["runtime_params"]["source"]["registration"] = ref  # real tempdir file
        arm("RED-10 control: source.registration -> real file",
            m, EXIT_OK, "red10_ctl.json")

        # ---- RED-11 top-level deadline_s != registered.deadline_s + control -
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["deadline_s"] = 999.0        # 600*1.25=750 <= 999 (margin OK), != registered 855.0
        arm("RED-11 top-level deadline_s != registered",
            m, EXIT_REFUSE, "red11.json")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["deadline_s"] = 999.0
        m["rungs"][0]["runtime_params"]["registered"]["deadline_s"] = 999.0
        m["rungs"][0]["runtime_params"]["launcher"]["deadline_s"] = 999.0
        arm("RED-11 control: registered/launcher equalised to 999",
            m, EXIT_OK, "red11_ctl.json")

        # ---- RED-12 config_exercised false + control -----------------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["config_exercise"]["config_exercised"] = False
        arm("RED-12 config_exercised false (L-516)",
            m, EXIT_REFUSE, "red12.json")
        arm("RED-12 control: config_exercised true",
            _base_manifest(sm1, sm2, sm3, ref), EXIT_OK, "red12_ctl.json")

        # ---- RED-13 launcher_paths_fixpointed false / n=0 + control --------
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["config_exercise"]["launcher_paths_fixpointed"] = False
        m["rungs"][0]["config_exercise"]["n_paths_checked"] = 0
        arm("RED-13 launcher paths not fixpointed (L-504-ref2)",
            m, EXIT_REFUSE, "red13.json")
        arm("RED-13 control: fixpointed true / n_paths_checked 1",
            _base_manifest(sm1, sm2, sm3, ref), EXIT_OK, "red13_ctl.json")

        # ---- RED-14 config_ref non-resolving + control ---------------------
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["config_exercise"]["config_ref"] = "no_such_config_ZZZ.md"
        arm("RED-14 config_ref non-resolving path",
            m, EXIT_REFUSE, "red14.json")
        m = _base_manifest(sm1, sm2, sm3, ref)
        m["rungs"][0]["config_exercise"]["config_ref"] = ref  # real tempdir file
        arm("RED-14 control: config_ref -> real file",
            m, EXIT_OK, "red14_ctl.json")

        print("=" * 78)
        if ok:
            print("SELFTEST: PASS -- every arm hit its expected exit code; each RED arm is")
            print("paired with a control that flips it, proving the arm is load-bearing.")
        else:
            print("SELFTEST: FAIL -- at least one arm did NOT hit its expected exit code.")
            print("A pre-flight gate whose plant does not fire prints no admissible pass (rule 3).")
        print("=" * 78)
        return ok
    finally:
        # scratch fixture tree only -- never the shared worktree
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", nargs="?",
                    help="path to a LADDER_PREFLIGHT.json pre-flight manifest")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the both-directions planted control; exit 3 if it does not fire")
    args = ap.parse_args(argv)

    if args.selftest:
        return EXIT_OK if selftest() else EXIT_VIOLATION

    if not args.manifest:
        ap.error("a LADDER_PREFLIGHT.json path is required (or --selftest)")

    code, line = check_manifest(args.manifest)
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
