#!/usr/bin/env python3
"""F12 attempt 2 — rung LAUNCHER. Committed UNFIRED.

WHAT THIS IS, AND THE ONE SENTENCE THAT BOUNDS IT
-------------------------------------------------
This is a LAUNCHER, not a grading path. It orchestrates; it does not decide.
**Every graded number below is produced by calling a frozen function unchanged,
and this file asserts those functions' BYTES at run time and fails closed.** It
contains no comparator, no threshold and no gate arithmetic of its own beyond
reading the frozen thresholds out of constants that are quoted from the frozen
document and asserted present in its committed blob.

Authority: Sanaa's instruction of 2026-08-25 — *"Build a fresh three-level mesh
ladder that passes the admission gate at every level … mesh instrument replaced,
gate unchanged. Then run RAE 2822 / AGARD Case 9 against the unchanged
criteria."* Replacing the mesh instrument after first compute is an owner ruling.
Her approval is of the new ladder against unchanged criteria and NOTHING WIDER
(standing rule 9), and this file takes nothing beyond it. Disclosed in the
LAUNCHER ADDENDUM of 2026-08-25 at the foot of the pre-registration.

WHY THE EXISTING PATH CANNOT BE USED — four measured facts, not preferences
--------------------------------------------------------------------------
1. `run_case` writes `system/blockMeshDict` from the frozen module's own
   `blockmesh_dict` and offers hooks for SPACINGS only, never topology. Attempt 2
   is a different topology. Firing through it fires attempt 1's GATE-A-FAILING
   mesh.
2. `run_case` writes `method scotch;` into `decomposeParDict` — non-compliant
   with the parallel-gate doctrine ratified 2026-08-25, and the exact
   non-determinism this team measured (12777/12906/12965 then 12974/12870/12865
   on a byte-identical mesh).
3. `run_case` runs the solver in the FOREGROUND under a subprocess timeout, with
   no `setsid`, and takes `rc` from the subprocess object — it NEVER WRITES rc TO
   DISK. Standing rule 4's rc limb cannot be measured through it, only inferred,
   which rule 4 forbids.
4. `run_f12_rung.py`'s ABSENT guard refuses if ANY registered directory exists.
   Attempt 1's `coarse_workshop_M0.734_a2.79` exists and is preserved, so that
   driver now refuses every rung. It also cites a STALE pre-registration blob
   (`41ec748a…`, superseded by two addenda) — reported here, not repaired.

WHAT IT DOES NOT DO
-------------------
AMENDMENT 2026-08-25, AFTER RUNG 1 FIRED — TWO DEFECTS THIS LANE FOUND IN ITS
OWN WORK AND REPORTED AGAINST ITSELF
------------------------------------------------------------------------------
Rung 1 fired at 17:06:57Z and aborted with rc = 134. `grade.json` for rung 1 was
produced by the PRE-AMENDMENT bytes, committed at `f723fac6`, and that record
stands; `grade_PRE_AMENDMENT.json` preserves it beside the re-grade so the two
can be compared without git archaeology.

  1. THE RUNGS-2-TO-5 INTERLOCK WAS KEYED ON `RC.txt` EXISTING, NOT ON RUNG 1
     SUCCEEDING. It therefore OPENED on a crashed rung at 17:07:18Z. Nothing was
     fired through it. It is now closed on a CONJUNCTION — see
     `rate_calibration_gate` — and carries a negative control that plants 134 and
     proves it refuses. The defect class is the one this team catalogued twice in
     the same day: a guard that passes on the wrong condition. It was not asking
     "did rung 1 succeed"; it was asking "did rung 1 finish leaving a file", and
     those two diverge exactly when it matters most.
  2. THE AGE-GUARD LIMB PRINTED "all newer" ON A CORRECT `False`, because the
     "no field is older" branch evaluates over an EMPTY list. The verdict was
     right and the annotation contradicted it, which is worse than no annotation
     — the next reader believes the sentence, not the boolean. The verdict
     expression is UNCHANGED (`bool(present) and not older`); only the annotation
     moved, into `age_guard_detail`, which has its own control.

STILL OWED, and enforced by the interlock above rather than by a promise:
`scripts/roache_triple.py` is NOT pinned. That is correct for rung 1 — a single
rung cannot compute a triple — and it is owed before rungs 2-5, where the triple
IS the graded object.

It does not authorise its own use. Firing needs the cfd supervisor's personal
reading of this file as a diff (`SUPERVISION_CHARTER.md` §3 check 1, never
delegable). No agent message authorises a launch (standing rule 9).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import inspect
import json
import os
import pathlib
import shlex
import signal
import subprocess
import sys
import time

REPO = pathlib.Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "sdk"))

from sdk.workflows import rae2822_case9 as W                      # noqa: E402
from sdk.workflows import tmr_verification as T                   # noqa: E402
from sdk.chief_engineer import head_engineer as HE                # noqa: E402
from sdk.chief_engineer import lever_echo                         # noqa: E402
from sdk.chief_engineer.openfoam import host_run_prefix           # noqa: E402

HERE = REPO / "verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25"
RUN_ROOT = REPO / "verification/runs/F12_runs"
SELF_REL = ("verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/"
            "launch_f12_rung.py")
PREREG = "verification/campaign/F12_PREREGISTRATION.md"

# --- pinned bytes ----------------------------------------------------------
# The pre-registration AFTER the LAUNCHER ADDENDUM of 2026-08-25, which is
# insertions-only at the foot (137 added, 0 deleted; lines 1-888 byte-identical).
PREREG_BLOB = "462492a82b6cf848eaaff25661ded45e623e723f"
# F12's own module, hashed WHOLE. This is the case's grading path and it must not
# drift at all.
RAE_MODULE_BLOB = "a18314f77160b7a58f443073850a44b4d8fada7d"
# The attempt-2 dictionaries, as COMMITTED at d26f5bdc. The substitution is the
# entire delta between this launcher and the frozen path.
MESH_DICT_SHA256 = {
    "coarse": "d47f5b9c5e9718cc155b4173f2a898cfe26ce3b9be9c881fe201ce5c116ff637",
    "medium": "7364b20f9d556452dbab451ae792cb621ce311395feff34312e8aa3a9486b276",
    "fine":   "00b1fb36fc91f9b08c1d4a098eb5c4a2c38290d982fc27cef7f447e77bbe4982",
}
# EVERY downstream function that turns a solve into a number, hashed
# INDIVIDUALLY by inspect.getsource. A function-level pin survives an unrelated
# edit elsewhere in a shared module and STILL fails closed if a graded function
# changes — which a whole-file pin on a file three teams write cannot do.
GRADING_FN_SHA256 = {
    "rae2822_case9.build_case":
        "664f517626b31e20e21329903716ad28164c6a70e5f3495d525c1153c84087b5",
    "rae2822_case9.freestream_state":
        "0cf51967563d8e227e526625b8ea4db78a0bea92d1c11d355a4689d54b448635",
    "rae2822_case9.rae_section":
        "f1c76db6da571ee38f2d2ebfa22084c2b19ee88b38a0118c184aba9e82c6b1c2",
    "rae2822_case9.load_coordinates":
        "1213691cc235a53ecefa2756d05a715beb252d7f88e227101456ffc3d2d1e0e6",
    "rae2822_case9.load_experiment_cp":
        "1a6872bb5976dfd26ad09f061f6435eba5c0f813008da8e957d712f747d38f90",
    "rae2822_case9.reference_dir":
        "6b6ef53eea790f73008fd8b9f8afbe97810d48494e1fd08760c0b27c2ee26b2e",
    "rae2822_case9.surface_points":
        "49331beb2804b1528ec5c0772397446fc2a2ccccb86d49feb7ad2c102449a7e8",
    "rae2822_case9.parse_check_mesh":
        "6ed07209570857aa3818fa2d59fd9af374cd7b69b14e7c8dd0b345df5df8b3a6",
    "rae2822_case9.mesh_gate":
        "df0b2d18d7d104dc2aed1c633da383d34834899fe9a2ab04b7eb2fc1deaa5989",
    "rae2822_case9.solver_converged":
        "aff97421a70be7af4ed134df408876d6cc47765398e27d5e9449b9f50b744bf8",
    "rae2822_case9.split_surfaces":
        "f873298fda1faf46c7bab323a4d0e56a2eaa0ccb3351dddf92f1dac9c065ddb8",
    "rae2822_case9.sonic_cp":
        "f395c50f680d40175c5eec0bbbc00f303b3d871d588d8fd6708c19ee076cc54f",
    "rae2822_case9.shock_location":
        "59c75739ca9a1a12c85aac2d4e9436263326b8bbadf7b71e90f9ec6902a5263d",
    "rae2822_case9.cp_deviation":
        "6513b0f7142982765ba522d28e7d7958273e6018e6b11a9cd6596fdcfb3a10c0",
    "rae2822_case9.control_dict":
        "95acfa66bfb2b255b43164749e68c51c3e5a3f37cf640913abb443ba03563e4d",
    "rae2822_case9.initial_fields":
        "9b6e842cf0a7f1b5b23b53d075eb56f97b11940e1daf81e0cd3af8aa10c7b0c9",
    "rae2822_case9.thermophysical_properties":
        "1c254c7df54f65fcdbb956bc2850bfe021b654e3cd9c569d22c4f00367bc0f28",
    "rae2822_case9.fv_schemes":
        "fa15da44a97910fbd4ba5da99419ada1c8fdef94f19d2f8e9ce05fa4eb6c9257",
    "rae2822_case9.fv_solution":
        "745fb3f87250b551d749e0d31b7b8a1b2f0708802853dcf4bc13de4bbf5159d0",
    "rae2822_case9.first_cell_for_level":
        "2511c306f095339348fa88263b2486426f9a0dbb4bef95c6e17efd340f87e383",
    "rae2822_case9.far_first_cell_for_level":
        "3f3cfa866b642aa9e1b11ec12d3b5ed43ef7b7e200773e8943639a8d6803c949",
    "rae2822_case9.refinement_factor":
        "1505e96d3a4d4fcf513643a13cd9c67653d39bd2d5222887072be5d4f749d6c7",
    "tmr_verification.final_coefficient":
        "c5391c236e986ac3d23a8255120e13634498b06ad17e8e1ba158d069b2e6788b",
    "tmr_verification.parse_force_split":
        "b3bc8ce0a75c50e9dd43b5dce8ad3ab7fce20a66facebb2adcecc82c630e7045",
    "tmr_verification.ratio_for_first_cell":
        "f318cdf8d667d7ac15fa162d64b49fa3742f8eceff48766dffcdbff2407afc4e",
    "head_engineer.parse_coefficient_history":
        "1408fd2e5297c18d2387df0eae3b0d8a0cb2e8c403b405654a23425fbc969f3d",
}
_MODULES = {"rae2822_case9": W, "tmr_verification": T, "head_engineer": HE}

# Frozen sentences that must be present VERBATIM in the pre-registration blob.
FROZEN_SENTENCES = (
    "max non-orthogonality\n<= 70 degrees and max skewness <= 4",
    "upper surface RMS <= **0.08**",
    "lower surface RMS <= **0.04**",
    "<= **0.020**",
    "|CN - 0.803| / 0.803 <= **5%**",
    "|CD - 0.0168| / 0.0168 <= **20%**",
    "| coarse | 48 | 48 | 80 | 23,040 |",
)
# Quoted from the frozen document, asserted present above, and used for REPORTING
# the deviation. THIS FILE SETS NO THRESHOLD; it transcribes them.
GATE1_UPPER_RMS, GATE1_LOWER_RMS = 0.08, 0.04
GATE2_SHOCK_CHORD = 0.020
GATE3_CN_REF, GATE3_FRAC = 0.803, 0.05
GATE4_CD_REF, GATE4_FRAC = 0.0168, 0.20
CM_REF = -0.099          # REPORTED, NOT GATED, and that clause is frozen too.

# --- the five registered rungs, caps VERBATIM from the frozen section 5 -----
RUNGS = {
    "attempt2_coarse_workshop_M0.734_a2.79":
        dict(mesh="coarse", mach=0.734, alpha=2.79, farfield_r=50.0, cap_core_min=120.0),
    "attempt2_medium_workshop_M0.734_a2.79":
        dict(mesh="medium", mach=0.734, alpha=2.79, farfield_r=50.0, cap_core_min=160.0),
    "attempt2_fine_workshop_M0.734_a2.79":
        dict(mesh="fine", mach=0.734, alpha=2.79, farfield_r=50.0, cap_core_min=700.0),
    "attempt2_medium_tape_M0.730_a2.79":
        dict(mesh="medium", mach=0.730, alpha=2.79, farfield_r=50.0, cap_core_min=160.0),
    "attempt2_medium_farfield2x_M0.734_a2.79":
        dict(mesh="medium", mach=0.734, alpha=2.79, farfield_r=100.0, cap_core_min=160.0),
}
# RANKS = 1 DELIBERATELY, and this is the one choice a reader should challenge
# first. The frozen section 4 states its cost model "with ranks = 1", and a
# parallel solve changes the summation order and therefore the last digits of a
# GATED number — this team has a row where exactly that decided a convergence
# verdict. The deterministic `hierarchical` decomposition is still WRITTEN and
# its partition counts still RECORDED, by a -dry-run decomposition that creates
# no processor directories, so the doctrine's determinism clause is satisfied and
# evidenced without making the graded solve depend on it. Flip this one constant
# to run parallel; the cap is in core-minutes and is unit-invariant.
RANKS = 1
ITERATIONS = 6000
SAMPLE_INTERVAL_S = 15.0
DECOMP_METHOD, DECOMP_N, DECOMP_RANKS = "hierarchical", (2, 2, 1), 4
# Rungs 2-5 stay CLOSED until rung 1 returns a measured rate, per the frozen
# section 5: "That measured rate then replaces both estimates before rungs 2-5
# are considered."
RATE_CALIBRATION_RUNG = "attempt2_coarse_workshop_M0.734_a2.79"


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def abort(msg: str) -> None:
    sys.stderr.write("ABORT: " + msg + "\n")
    raise SystemExit(1)


def git_bytes(*args: str) -> bytes:
    p = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True)
    if p.returncode != 0:
        abort("git " + " ".join(args) + " rc=" + str(p.returncode))
    return p.stdout


# ---------------------------------------------------------------------------
# FROZEN-BYTES ASSERTIONS.  Everything below fails CLOSED.
# ---------------------------------------------------------------------------

def assert_frozen(check_self: bool = True) -> dict:
    ev = {"checked_utc": utc()}
    if check_self:
        disk = hashlib.sha256((REPO / SELF_REL).read_bytes()).hexdigest()
        blob = hashlib.sha256(git_bytes("cat-file", "-p", f"HEAD:{SELF_REL}")).hexdigest()
        if disk != blob:
            abort("this launcher DIFFERS from its HEAD blob; refusing to run")
        ev["launcher_sha256"] = disk

    got = git_bytes("rev-parse", f"HEAD:{PREREG}").decode().strip()
    if got != PREREG_BLOB:
        abort(f"pre-registration blob at HEAD is {got}, pinned {PREREG_BLOB}")
    on_disk = subprocess.run(["git", "-C", str(REPO), "hash-object", PREREG],
                             capture_output=True, text=True).stdout.strip()
    if on_disk != PREREG_BLOB:
        abort(f"worktree pre-registration {on_disk} != pinned {PREREG_BLOB}")
    text = git_bytes("cat-file", "-p", f"HEAD:{PREREG}").decode()
    for s in FROZEN_SENTENCES:
        if s not in text:
            abort(f"frozen sentence ABSENT from the pinned blob: {s!r}")
    ev["prereg_blob"] = PREREG_BLOB
    ev["frozen_sentences_found"] = len(FROZEN_SENTENCES)

    mod = git_bytes("rev-parse", "HEAD:sdk/workflows/rae2822_case9.py").decode().strip()
    if mod != RAE_MODULE_BLOB:
        abort(f"grading module blob is {mod}, pinned {RAE_MODULE_BLOB}. "
              "The grading path has moved; this launcher will not run against it.")
    disk_mod = subprocess.run(
        ["git", "-C", str(REPO), "hash-object", "sdk/workflows/rae2822_case9.py"],
        capture_output=True, text=True).stdout.strip()
    if disk_mod != RAE_MODULE_BLOB:
        abort("worktree sdk/workflows/rae2822_case9.py differs from its blob")
    ev["rae_module_blob"] = RAE_MODULE_BLOB

    bad = []
    for key, want in GRADING_FN_SHA256.items():
        modname, fname = key.split(".", 1)
        fn = getattr(_MODULES[modname], fname, None)
        if fn is None:
            bad.append(f"{key}: MISSING")
            continue
        got_h = hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()
        if got_h != want:
            bad.append(f"{key}: {got_h[:12]} != pinned {want[:12]}")
    if bad:
        abort("GRADING FUNCTION BYTES CHANGED — refusing:\n  " + "\n  ".join(bad))
    ev["grading_functions_pinned"] = len(GRADING_FN_SHA256)
    return ev


def assert_mesh_dict(level: str) -> str:
    src = HERE / level / "system" / "blockMeshDict"
    if not src.exists():
        abort(f"registered attempt-2 dictionary ABSENT: {src}")
    disk = hashlib.sha256(src.read_bytes()).hexdigest()
    if disk != MESH_DICT_SHA256[level]:
        abort(f"attempt-2 {level} dictionary sha256 {disk[:12]} != pinned "
              f"{MESH_DICT_SHA256[level][:12]}; refusing to substitute it")
    rel = str(src.relative_to(REPO))
    committed = hashlib.sha256(git_bytes("cat-file", "-p", f"HEAD:{rel}")).hexdigest()
    if committed != disk:
        abort(f"attempt-2 {level} dictionary on disk differs from its HEAD blob")
    return disk


# ---------------------------------------------------------------------------
# rc — written to disk at capture, read back, REFUSED if absent or malformed
# ---------------------------------------------------------------------------

def read_rc(path: pathlib.Path):
    """The run's own exit code, READ BACK FROM DISK.

    Rule 4's rc limb is MEASURED, never inferred. A missing file, an empty file
    or anything that is not an integer is a REFUSAL — not a zero, not a guess,
    and never 'the process looked finished'.
    """
    if not path.exists():
        return None, "RC.txt ABSENT — rc NOT MEASURED, and it is not inferred"
    raw = path.read_text(errors="replace").strip()
    if raw == "":
        return None, "RC.txt EMPTY — rc NOT MEASURED"
    try:
        return int(raw), None
    except ValueError:
        return None, f"RC.txt holds {raw!r}, not an integer — rc NOT MEASURED"


# ---------------------------------------------------------------------------
# case composition — the frozen build_case, then ONE substitution
# ---------------------------------------------------------------------------

def age_guard_detail(present, older) -> str:
    """The age-guard annotation. Separated out because it was WRONG.

    With no field at endTime the limb correctly returns False, but the previous
    inline expression annotated it "all newer" — the `not older` branch is
    vacuously true over an EMPTY list. A printed annotation that contradicts its
    own verdict is worse than none: the next reader believes the sentence.
    """
    if not present:
        return "no fields exist at endTime — nothing to compare against 0/T"
    if older:
        return f"not newer than 0/T: {older}"
    return f"all {len(present)} fields newer than 0/T"


def measured_rate(case: pathlib.Path | None = None):
    """Seconds per cell-iteration measured from a rung's own log, or None.

    A COST quantity, not a gate quantity. Returns None — never a guess — when
    the log, the iteration count or the cell count is missing.
    """
    case = (RUN_ROOT / RATE_CALIBRATION_RUNG) if case is None else case
    try:
        log = (case / "log.rhoSimpleFoam").read_text(errors="replace")
        chk = (case / "log.checkMesh").read_text(errors="replace")
    except OSError:
        return None
    its = len([l for l in log.splitlines() if l.startswith("Time = ")])
    ex = [l for l in log.splitlines() if l.startswith("ExecutionTime")]
    cells = W.parse_check_mesh(chk).get("cells")
    if not its or not ex or not cells:
        return None
    try:
        secs = float(ex[-1].split("=")[1].split("s")[0])
    except (IndexError, ValueError):
        return None
    if secs <= 0.0:
        return None
    return secs / (its * cells)


def rate_calibration_gate(case: pathlib.Path | None = None):
    """The interlock on rungs 2-5. A CONJUNCTION, not a file-existence test.

    THIS GUARD WAS WRONG AND IT OPENED ON A CRASHED RUNG. It asked whether
    RC.txt EXISTED; RC.txt existed holding 134. It now requires ALL of:

      * RC.txt present, AND
      * its content parses as an integer, AND
      * that integer is 0, AND
      * every one of rung 1's strict-completion limbs passes, AND
      * a measured rate exists.

    Any one absent REFUSES. Returns (allowed, reasons).
    """
    case = (RUN_ROOT / RATE_CALIBRATION_RUNG) if case is None else case
    why = []
    rc, rc_why = read_rc(case / "RC.txt")
    if rc is None:
        why.append(f"rc NOT MEASURED: {rc_why}")
    elif rc != 0:
        why.append(f"rate-calibration rung rc = {rc}, not 0 — IT DID NOT SUCCEED")
    gp = case / "grade.json"
    if not gp.exists():
        why.append("rate-calibration rung grade.json ABSENT — its completion "
                   "limbs are NOT MEASURED, and absence does not read as pass")
    else:
        try:
            g = json.loads(gp.read_text())
        except (ValueError, OSError) as exc:
            why.append(f"grade.json unreadable ({exc}) — refusing")
            g = None
        if g is not None:
            limbs = g.get("strict_completion_rule")
            if not isinstance(limbs, dict) or not limbs:
                why.append("completion limbs ABSENT from grade.json")
            else:
                failed = sorted(k for k, v in limbs.items()
                                if not (isinstance(v, dict) and v.get("pass")))
                if failed:
                    why.append(f"completion limbs FAILED: {failed}")
            if g.get("complete") is not True:
                why.append("the rate-calibration rung is not complete")
    if measured_rate(case) is None:
        why.append("no measured rate exists — the frozen section 5 makes that "
                   "rate replace both estimates BEFORE rungs 2-5 are considered")
    return (not why), why


def compose_case(case: pathlib.Path, spec: dict) -> dict:
    """Everything from the frozen `build_case`; then `system/blockMeshDict` is
    overwritten from the sha256-asserted committed attempt-2 dictionary.

    THAT SUBSTITUTION IS THE ENTIRE DELTA. Fields, thermophysical and turbulence
    properties, fvSchemes, fvSolution and controlDict -- including the
    forceCoeffs1, surfaceP, yPlus and MachNo function objects that produce every
    graded quantity -- are the frozen module's, byte-asserted above.
    """
    dict_sha = assert_mesh_dict(spec["mesh"])
    level = {"coarse": 0, "medium": 1, "fine": 2}[spec["mesh"]]
    params = W.build_case(case, mach=spec["mach"], alpha_deg=spec["alpha"],
                          level=W.LEVELS[level], iterations=ITERATIONS,
                          farfield_r=spec["farfield_r"])
    target = case / "system" / "blockMeshDict"
    frozen_sha = hashlib.sha256(target.read_bytes()).hexdigest()
    target.write_bytes((HERE / spec["mesh"] / "system" / "blockMeshDict").read_bytes())
    back = hashlib.sha256(target.read_bytes()).hexdigest()
    if back != dict_sha:
        abort("substituted blockMeshDict does not read back as the pinned one")
    (case / "system" / "decomposeParDict").write_text(
        T._foam_header("dictionary", "decomposeParDict")
        + f"\nnumberOfSubdomains {DECOMP_RANKS};\nmethod          {DECOMP_METHOD};\n"
          f"coeffs\n{{\n    n           ({DECOMP_N[0]} {DECOMP_N[1]} {DECOMP_N[2]});\n"
          "    order       xyz;\n}\n")
    # 0/T is touched LAST, so it dates the run allowed to produce the answer and
    # the age guard has something to compare against (standing rule 4).
    time.sleep(1.1)
    (case / "0" / "T").touch()
    return {"build_case_params": params,
            "blockMeshDict_replaced_sha256_from": frozen_sha,
            "blockMeshDict_replaced_sha256_to": dict_sha,
            "substitution_is_the_entire_delta": True}


# ---------------------------------------------------------------------------
# the external sampler — loadavg in EVERY sample; cap breach STOPS the rung
# ---------------------------------------------------------------------------

def sampler_main(case: pathlib.Path, cap_core_min: float, ranks: int,
                 pgid: int, t0: float) -> int:
    """Runs detached beside the solver. Every sample carries loadavg, because
    this team measured the contention allowance to be BIMODAL and a run that
    records only its launch load has measured the wrong thing.

    Cap breach STOPS the rung. An overrun stops the run; it does not get a new
    budget (standing rule 12).
    """
    samples = case / "SAMPLES.jsonl"
    rc_path = case / "RC.txt"
    while True:
        elapsed = time.time() - t0
        core_min = elapsed * ranks / 60.0
        it = None
        try:
            log = (case / "log.rhoSimpleFoam").read_text(errors="replace")
            marks = [ln for ln in log.splitlines() if ln.startswith("Time = ")]
            if marks:
                it = marks[-1].split("=", 1)[1].strip()
        except OSError:
            pass
        alive = pathlib.Path(f"/proc/{pgid}").exists()
        row = {"utc": utc(), "elapsed_s": round(elapsed, 1),
               "core_min": round(core_min, 4), "cap_core_min": cap_core_min,
               "frac_of_cap": round(core_min / cap_core_min, 4),
               "ranks": ranks, "latest_time": it, "alive": alive,
               "loadavg": open("/proc/loadavg").read().split()[:3]}
        if core_min > cap_core_min and alive:
            row["action"] = "CAP BREACHED — STOPPING THE RUNG"
            with samples.open("a") as f:
                f.write(json.dumps(row) + "\n")
                f.flush()
                os.fsync(f.fileno())
            try:
                os.killpg(pgid, signal.SIGTERM)
                time.sleep(20)
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            (case / "CAP_BREACH.txt").write_text(
                f"{utc()}  core_min {core_min:.4f} > cap {cap_core_min}  "
                f"STOPPED by the sampler; the rung does not get a new budget\n")
            return 0
        with samples.open("a") as f:
            f.write(json.dumps(row) + "\n")
            f.flush()
            os.fsync(f.fileno())
        if not alive and rc_path.exists():
            return 0
        if not alive and elapsed > 60:
            return 0
        time.sleep(SAMPLE_INTERVAL_S)


# ---------------------------------------------------------------------------
# launch
# ---------------------------------------------------------------------------

def launch(key: str) -> int:
    if key not in RUNGS:
        abort(f"unknown rung {key!r}")
    spec = RUNGS[key]
    if key != RATE_CALIBRATION_RUNG:
        allowed, why = rate_calibration_gate()
        if not allowed:
            abort(f"rung {key!r} is CLOSED. The rate-calibration rung "
                  f"{RATE_CALIBRATION_RUNG!r} has not SUCCEEDED:\n  - "
                  + "\n  - ".join(why))
    ev = assert_frozen()
    case = RUN_ROOT / key
    if os.path.exists(case):
        abort(f"registered run directory already exists: {case}. A rung is "
              "fired exactly once; an existing directory is EVIDENCE, and this "
              "launcher will not overwrite or remove it.")
    for p in (RUN_ROOT / "coarse_workshop_M0.734_a2.79",
              RUN_ROOT / "mesh_audit_2026-08-25" / "mesh_audit.json",
              HERE / "gate_a_attempt2.json"):
        if not p.exists():
            abort(f"earlier attempt evidence MISSING: {p}")

    started = utc()
    t0 = time.time()
    comp = compose_case(case, spec)

    def step(name, args, limit):
        s = time.time()
        r = T._foam(args, case, f"log.{name}", timeout=limit)
        return r, round(time.time() - s, 2)

    r_bm, t_bm = step("blockMesh", ["blockMesh"], 1800)
    if r_bm.returncode != 0:
        abort("blockMesh failed on the substituted dictionary; see log.blockMesh")
    r_cm, t_cm = step("checkMesh", ["checkMesh"], 1800)
    quality = W.parse_check_mesh((case / "log.checkMesh").read_text(errors="replace"))
    gate_a = W.mesh_gate(quality)          # the FROZEN gate, called not copied
    r_dp, t_dp = step("decomposePar", ["decomposePar", "-dry-run", "-cellDist"], 1800)
    dp_txt = (case / "log.decomposePar").read_text(errors="replace")
    parts = [ln.strip() for ln in dp_txt.splitlines() if ln.strip().startswith("Cells ")]

    prefix = list(host_run_prefix())
    solver = (["mpirun", "-np", str(RANKS), "rhoSimpleFoam", "-parallel"]
              if RANKS > 1 else ["rhoSimpleFoam"])
    # Lever echo at t=0 — the shared predicate and format, not a private copy
    # (VERIFICATION_CHARTER v1.5 §9). Bypassing `_foam` must not bypass this.
    try:
        block = lever_echo.echo_if_solver(solver, case)
    except OSError:
        block = ""
    (case / "log.rhoSimpleFoam").write_text(block or "")

    # rc is captured IMMEDIATELY into a shell variable, written RAW, fsync'd by
    # `sync`, and read back from the file. No formatting happens before capture.
    shell = ("echo $$ > PGID.txt; " + f"cd {shlex.quote(str(case))}; "
             + shlex.join(prefix + solver) + " >> log.rhoSimpleFoam 2>&1; "
             "RC=$?; echo \"$RC\" > RC.txt; sync")
    proc = subprocess.Popen(["setsid", "bash", "-c", shell],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            cwd=str(case), start_new_session=True)
    pgid = None
    for _ in range(100):
        try:
            pgid = int((case / "PGID.txt").read_text().strip())
            break
        except (OSError, ValueError):
            time.sleep(0.1)
    if pgid is None:
        abort("the solver's process-group id was never written; refusing to "
              "claim a launch whose process I cannot name or stop")
    detach = {"pid": pgid, "session_leader": None, "ppid": None}
    for _ in range(100):
        try:
            st = open(f"/proc/{pgid}/stat").read().rsplit(")", 1)[1].split()
            detach["ppid"] = int(st[1])
            detach["session_leader"] = (int(st[3]) == pgid)
        except OSError:
            break
        if detach["ppid"] == 1:
            break
        time.sleep(0.1)

    samp = subprocess.Popen(
        ["setsid", sys.executable, str(REPO / SELF_REL), "--sampler",
         "--case", str(case), "--cap", str(spec["cap_core_min"]),
         "--ranks", str(RANKS), "--pgid", str(pgid), "--t0", str(t0)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)

    resume = {
        "rung": key, "case": str(case), "started_utc": started,
        "pid_and_pgid": pgid, "sampler_pid": samp.pid,
        "detachment": detach, "ranks": RANKS, "iterations": ITERATIONS,
        "cap_core_min": spec["cap_core_min"],
        "cap_wall_s_at_this_ranks": spec["cap_core_min"] * 60.0 / RANKS,
        "loadavg_at_launch": open("/proc/loadavg").read().split()[:3],
        "frozen_evidence": ev, "composition": comp,
        "mesh": {"quality": quality, "gate_A": gate_a,
                 "blockMesh_s": t_bm, "checkMesh_s": t_cm,
                 "decomposition": {"method": DECOMP_METHOD, "n": list(DECOMP_N),
                                   "subdomains": DECOMP_RANKS,
                                   "seed": "none — hierarchical is seed-free",
                                   "summary_lines": parts, "dry_run": True,
                                   "s": t_dp}},
        "how_to_check": f"tail -2 {case}/SAMPLES.jsonl ; cat {case}/RC.txt",
        "how_to_stop": f"kill -TERM -{pgid}",
        "how_to_grade": f"{SELF_REL} --grade {key}",
        "note": ("the run does not depend on the agent that started it: the "
                 "solver is a session leader under setsid and the sampler is a "
                 "separate detached process."),
    }
    (case / "RESUME.json").write_text(json.dumps(resume, indent=1, default=str))
    print(json.dumps({"launched": key, "pgid": pgid, "gate_A": gate_a["passed"],
                      "max_non_ortho": quality.get("max_non_orthogonality"),
                      "cells": quality.get("cells"),
                      "cap_core_min": spec["cap_core_min"]}, indent=1))
    return 0


# ---------------------------------------------------------------------------
# grade — the strict completion rule, then the frozen gates, all called
# ---------------------------------------------------------------------------

def grade(key: str) -> int:
    spec = RUNGS[key]
    ev = assert_frozen()
    case = RUN_ROOT / key
    if not case.exists():
        abort(f"no such run directory: {case}")
    log = (case / "log.rhoSimpleFoam").read_text(errors="replace")
    rc, rc_why = read_rc(case / "RC.txt")

    times = [ln.split("=", 1)[1].strip() for ln in log.splitlines()
             if ln.startswith("Time = ")]
    exec_lines = [ln for ln in log.splitlines() if ln.startswith("ExecutionTime")]
    fields = sorted(p.name for p in (case / "0").iterdir()) if (case / "0").exists() else []
    end_dir = case / str(ITERATIONS)
    present = sorted(p.name for p in end_dir.iterdir()) if end_dir.exists() else []
    missing = [f for f in fields if f not in present]
    t_zero = (case / "0" / "T").stat().st_mtime if (case / "0" / "T").exists() else None
    older = [f for f in present
             if t_zero is not None and (end_dir / f).stat().st_mtime <= t_zero]

    limbs = {
        "rc_is_zero": (rc == 0, f"rc={rc}" if rc is not None else rc_why),
        "End_line_present": ("End" in log.split("\n"), None),
        "last_time_equals_endTime": (bool(times) and times[-1] == str(ITERATIONS),
                                     times[-1] if times else "no Time lines"),
        "fields_present_at_endTime": (bool(present) and not missing,
                                      f"missing {missing}" if missing else str(present)),
        "ExecutionTime_count_equals_endTime": (len(exec_lines) == ITERATIONS,
                                               f"{len(exec_lines)} of {ITERATIONS}"),
        # verdict expression UNCHANGED; only the annotation moved (see the
        # AMENDMENT note at the head of this file).
        "age_guard_all_fields_newer_than_0_T": (bool(present) and not older,
                                                age_guard_detail(present, older)),
    }
    complete = all(v[0] for v in limbs.values())

    out = {"rung": key, "graded_utc": utc(), "frozen_evidence": ev,
           "strict_completion_rule": {k: {"pass": v[0], "detail": v[1]}
                                      for k, v in limbs.items()},
           "complete": complete,
           "cap_breached": (case / "CAP_BREACH.txt").exists()}
    if (case / "CAP_BREACH.txt").exists():
        out["cap_breach"] = (case / "CAP_BREACH.txt").read_text()

    quality = W.parse_check_mesh((case / "log.checkMesh").read_text(errors="replace"))
    out["gate_A"] = W.mesh_gate(quality)
    out["gate_B_converged"] = W.solver_converged(log)     # frozen, called

    if not complete:
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("the strict completion rule is ALL-OR-NOTHING and this run "
                      "fails at least one limb; no gate value is quoted")
        (case / "grade.json").write_text(json.dumps(out, indent=1, default=str))
        print(json.dumps({"verdict": out["verdict"], "limbs": {k: v[0] for k, v in limbs.items()}}, indent=1))
        return 1

    coeff = sorted((case / "postProcessing" / "forceCoeffs1").rglob("coefficient*.dat"))
    if not coeff:
        abort("no forceCoeffs output — a zero from a reader that cannot see a "
              "non-zero is not evidence, and an absent file reads ABSENT")
    dat = coeff[-1].read_text(errors="replace")
    cd, cl, cm = (T.final_coefficient(dat, c) for c in ("Cd", "Cl", "CmPitch"))
    history = HE.parse_coefficient_history(dat)
    import math
    rad = math.radians(spec["alpha"])
    cn = cl["value"] * math.cos(rad) + cd["value"] * math.sin(rad)

    section = W.rae_section()
    state = W.freestream_state(spec["mach"], 6.5e6)
    raw = sorted((case / "postProcessing" / "surfaceP").rglob("*.raw"))
    surfaces = (W.split_surfaces(raw[-1].read_text(errors="replace"), section,
                                 W.P_INF, state["q_inf"]) if raw else {})
    exp = W.load_experiment_cp()
    dev = {s: (W.cp_deviation(surfaces.get(s), exp[s]) if surfaces.get(s) else None)
           for s in ("upper", "lower")}
    shock_cfd = W.shock_location(surfaces["upper"], spec["mach"]) if surfaces else None
    shock_exp = W.shock_location(exp["upper"], spec["mach"])

    def band(v, ref, frac):
        return {"value": v, "reference": ref,
                "relative_deviation": abs(v - ref) / abs(ref),
                "band": frac,
                "verdict": "PASS" if abs(v - ref) / abs(ref) <= frac else "GATE FAIL"}

    g = {}
    g["gate1_cp_rms"] = {
        "upper": dev["upper"], "lower": dev["lower"],
        "thresholds": {"upper": GATE1_UPPER_RMS, "lower": GATE1_LOWER_RMS}}
    if shock_cfd and shock_exp:
        d = abs(shock_cfd["sonic_x_over_c"] - shock_exp["sonic_x_over_c"])
        g["gate2_shock"] = {"cfd": shock_cfd, "experiment": shock_exp,
                            "delta_chord": d, "threshold": GATE2_SHOCK_CHORD,
                            "verdict": "PASS" if d <= GATE2_SHOCK_CHORD else "GATE FAIL"}
    g["gate3_CN"] = band(cn, GATE3_CN_REF, GATE3_FRAC)
    g["gate4_CD"] = band(cd["value"], GATE4_CD_REF, GATE4_FRAC)
    g["CM_reported_not_gated"] = {"value": cm["value"] if cm else None,
                                  "reference": CM_REF, "gated": False}
    out["gates"] = g
    out["coefficients"] = {"cd": cd, "cl": cl, "cm": cm, "cn": cn,
                           "iterations_run": len(history.get("Cd", [])),
                           "cd_split": T.parse_force_split(log, "Cd")}
    (case / "grade.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({"complete": complete, "gate_A": out["gate_A"]["passed"],
                      "gate_B": out["gate_B_converged"],
                      "CN": cn, "CD": cd["value"]}, indent=1))
    return 0


# ---------------------------------------------------------------------------
# selftest — ZERO COMPUTE, planted controls on every refusal path
# ---------------------------------------------------------------------------

def selftest() -> int:
    ok = []

    def chk(name, cond, detail=""):
        ok.append((name, bool(cond)))
        print(f"  [{'ok' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))

    ev = assert_frozen(check_self=False)
    chk("frozen bytes assert clean at HEAD",
        ev["grading_functions_pinned"] == len(GRADING_FN_SHA256),
        f"{ev['grading_functions_pinned']} functions pinned")

    # PLANTED: a REAL one-line change inside a graded function must be caught.
    # The plant is a MODIFIED COPY of the frozen module, imported under its own
    # name and hashed by the same code path. A plant that only renames a
    # function object does NOT work here and was tried first: inspect.getsource
    # resolves through the code object's file and line, so the renamed function
    # hashes IDENTICALLY and the control silently passes while proving nothing.
    import ast as _ast0
    src = (REPO / "sdk/workflows/rae2822_case9.py").read_text()
    mutated = src.replace(
        "def cp_deviation(cfd: list[tuple[float, float]],",
        "def cp_deviation(cfd: list[tuple[float, float]],  # PLANTED BYTE", 1)
    chk("the plant actually changed the module source", mutated != src)

    def _fn_hashes(text):
        tree = _ast0.parse(text)
        out = {}
        for n in _ast0.walk(tree):
            if isinstance(n, _ast0.FunctionDef):
                seg = _ast0.get_source_segment(text, n)
                if seg is not None:
                    out[n.name] = hashlib.sha256((seg + "\n").encode()).hexdigest()
        return out

    # First prove the EXTRACTOR agrees with the one assert_frozen actually uses.
    # A control read by an instrument that disagrees with the real one proves
    # nothing about the real one.
    clean = _fn_hashes(src)
    agree = [k.split(".", 1)[1] for k in GRADING_FN_SHA256
             if k.startswith("rae2822_case9.")
             and clean.get(k.split(".", 1)[1]) == GRADING_FN_SHA256[k]]
    want_n = len([k for k in GRADING_FN_SHA256 if k.startswith("rae2822_case9.")])
    chk("the control's extractor reproduces every pinned hash on the CLEAN file",
        len(agree) == want_n, f"{len(agree)} of {want_n}")

    dirty = _fn_hashes(mutated)
    mism = sorted(n for n in clean if dirty.get(n) != clean[n])
    chk("PLANTED one byte inside cp_deviation -> EXACTLY that function refused",
        mism == ["cp_deviation"], f"mismatched: {mism}")
    chk("the real module still asserts clean after the plant",
        assert_frozen(check_self=False)["grading_functions_pinned"]
        == len(GRADING_FN_SHA256))

    # PLANTED: rc reader must refuse absent / empty / non-integer, and read a real one
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d)
        v, why = read_rc(p / "nope"); chk("rc ABSENT -> refused, not zero", v is None and "ABSENT" in why)
        (p / "e").write_text("");    v, why = read_rc(p / "e"); chk("rc EMPTY -> refused", v is None)
        (p / "x").write_text("boom"); v, why = read_rc(p / "x"); chk("rc NON-INTEGER -> refused", v is None)
        (p / "z").write_text("0\n");  v, why = read_rc(p / "z"); chk("rc 0 read back as 0 (reader sees a real value)", v == 0)
        (p / "n").write_text("139\n"); v, why = read_rc(p / "n"); chk("rc 139 read back as 139 (reader sees a NON-zero)", v == 139)

    # PLANTED: the mesh-dictionary substitution must fail closed on a changed byte
    for lvl in ("coarse", "medium", "fine"):
        chk(f"attempt-2 {lvl} dictionary matches its pinned sha256",
            assert_mesh_dict(lvl) == MESH_DICT_SHA256[lvl])
    import shutil, tempfile as tf
    with tf.TemporaryDirectory() as d:
        bogus = pathlib.Path(d) / "coarse" / "system"
        bogus.mkdir(parents=True)
        shutil.copy(HERE / "coarse" / "system" / "blockMeshDict", bogus / "blockMeshDict")
        with (bogus / "blockMeshDict").open("a") as f:
            f.write("\n// planted byte\n")
        planted = hashlib.sha256((bogus / "blockMeshDict").read_bytes()).hexdigest()
        chk("PLANTED one byte into a copy -> sha256 differs (reader sees it)",
            planted != MESH_DICT_SHA256["coarse"])

    # the gate thresholds transcribed here must be the frozen ones
    text = git_bytes("cat-file", "-p", f"HEAD:{PREREG}").decode()
    chk("gate 1 thresholds 0.08 / 0.04 present verbatim in the frozen blob",
        "upper surface RMS <= **0.08**" in text and "lower surface RMS <= **0.04**" in text)
    chk("gate 2 threshold 0.020 chord present verbatim", "<= **0.020**" in text)
    chk("gate 3 5% and gate 4 20% present verbatim",
        "|CN - 0.803| / 0.803 <= **5%**" in text and "|CD - 0.0168| / 0.0168 <= **20%**" in text)
    chk("caps transcribed EQUAL the frozen section 5",
        [RUNGS[k]["cap_core_min"] for k in
         ("attempt2_coarse_workshop_M0.734_a2.79", "attempt2_medium_workshop_M0.734_a2.79",
          "attempt2_fine_workshop_M0.734_a2.79", "attempt2_medium_tape_M0.730_a2.79",
          "attempt2_medium_farfield2x_M0.734_a2.79")] == [120.0, 160.0, 700.0, 160.0, 160.0])
    # Read the AST, not the file text. The first version of this check grepped
    # its own source for "def cp_deviation" and tripped on the STRING inside
    # this very check -- a test that fails on a correct file tests nothing.
    import ast as _ast
    tree = _ast.parse((REPO / SELF_REL).read_text())
    defined = {n.name for n in _ast.walk(tree)
               if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))}
    reimplemented = defined & {"cp_deviation", "shock_location", "mesh_gate",
                               "solver_converged", "split_surfaces", "sonic_cp",
                               "parse_check_mesh", "final_coefficient",
                               "parse_force_split", "parse_coefficient_history",
                               "build_case", "blockmesh_dict", "freestream_state"}
    chk("this launcher REIMPLEMENTS no frozen grading function",
        not reimplemented, f"would have been: {sorted(reimplemented)}")
    # The ONE piece of arithmetic this launcher performs, declared rather than
    # hidden: `band()`, which is |v - ref| / |ref| <= frac. No frozen function
    # implements gates 3 and 4 -- `run_f12_rung.py` does not grade them either --
    # so it is transcribed from the frozen text, whose exact sentences are
    # asserted present in the pinned blob above. It introduces no threshold: the
    # references and fractions are the frozen 0.803 / 5 % and 0.0168 / 20 %.
    chk("the one transcribed arithmetic is band(), and it is declared",
        "band" in defined and GATE3_CN_REF == 0.803 and GATE3_FRAC == 0.05
        and GATE4_CD_REF == 0.0168 and GATE4_FRAC == 0.20)
    _b = None
    for _n in _ast.walk(tree):
        if isinstance(_n, _ast.FunctionDef) and _n.name == "band":
            _b = _n
    chk("band() is arithmetic only -- no I/O, no subprocess, no file access",
        _b is not None and not any(
            isinstance(x, _ast.Call) and getattr(getattr(x, "func", None), "id", "")
            in {"open", "print", "eval", "exec"} for x in _ast.walk(_b)))
    # ---- THE INTERLOCK, WITH A FAILING ARM ---------------------------------
    # A guard without a failing arm is a paragraph, not a check. The previous
    # version of THIS check asked only whether RC.txt was absent -- so once rung
    # 1 crashed and wrote 134 it reported the interlock closed while the
    # interlock was OPEN. Every conjunct is now planted and dropped in turn.
    import tempfile as _tf2

    def _fixture(d, rc="0\n", limbs_pass=True, complete=True,
                 with_grade=True, with_logs=True):
        c = pathlib.Path(d)
        if rc is not None:
            (c / "RC.txt").write_text(rc)
        if with_grade:
            limbs = {k: {"pass": limbs_pass, "detail": ""} for k in
                     ("rc_is_zero", "End_line_present", "last_time_equals_endTime",
                      "fields_present_at_endTime",
                      "ExecutionTime_count_equals_endTime",
                      "age_guard_all_fields_newer_than_0_T")}
            (c / "grade.json").write_text(json.dumps(
                {"strict_completion_rule": limbs, "complete": complete}))
        if with_logs:
            (c / "log.rhoSimpleFoam").write_text(
                "".join(f"Time = {i}\n" for i in range(1, 149))
                + "ExecutionTime = 13.29 s  ClockTime = 14 s\n")
            (c / "log.checkMesh").write_text("    cells:            23040\n")
        return c

    with _tf2.TemporaryDirectory() as d:
        c = _fixture(d)
        allowed, why = rate_calibration_gate(c)
        chk("POSITIVE arm: rc 0 + all limbs + complete + a rate -> ALLOWS",
            allowed, f"reasons: {why}")
        chk("  and the rate it measured is a real number",
            measured_rate(c) is not None and measured_rate(c) > 0)

    with _tf2.TemporaryDirectory() as d:
        c = _fixture(d, rc="134\n")
        allowed, why = rate_calibration_gate(c)
        chk("NEGATIVE arm: PLANTED rc = 134 -> REFUSES",
            not allowed and any("134" in r and "DID NOT SUCCEED" in r for r in why),
            f"reasons: {why}")

    for label, kw, needle in (
            ("rc ABSENT", dict(rc=None), "NOT MEASURED"),
            ("rc non-integer", dict(rc="boom\n"), "NOT MEASURED"),
            ("a completion limb FAILING", dict(limbs_pass=False), "limbs FAILED"),
            ("complete = False", dict(complete=False), "not complete"),
            ("grade.json ABSENT", dict(with_grade=False), "ABSENT"),
            ("no measured rate", dict(with_logs=False), "no measured rate")):
        with _tf2.TemporaryDirectory() as d:
            c = _fixture(d, **kw)
            allowed, why = rate_calibration_gate(c)
            chk(f"CONJUNCT dropped -- {label} -> REFUSES",
                (not allowed) and any(needle in r for r in why), f"reasons: {why}")

    allowed, why = rate_calibration_gate()
    chk("THE REAL rung 1 (rc = 134) -> rungs 2-5 REFUSED",
        not allowed, f"reasons: {why}")

    # ---- the age-guard annotation, which contradicted its own verdict -------
    chk("age-guard annotation on an EMPTY field list does NOT say 'all newer'",
        "all newer" not in age_guard_detail([], [])
        and "nothing to compare" in age_guard_detail([], []))
    chk("age-guard annotation still reads correctly when fields ARE newer",
        "all 2 fields newer" in age_guard_detail(["T", "U"], []))
    chk("age-guard annotation names the offenders when a field is NOT newer",
        "not newer than 0/T: ['T']" == age_guard_detail(["T", "U"], ["T"]))

    # Rung 1 HAS fired (2026-08-25T17:06:57Z, rc = 134) and its directory is
    # EVIDENCE. What must still hold is that rungs 2-5 are unfired.
    chk("rung 1 IS fired and its directory is preserved as evidence",
        (RUN_ROOT / RATE_CALIBRATION_RUNG).exists())
    chk("rungs 2-5 remain UNFIRED on disk",
        not any((RUN_ROOT / k).exists() for k in RUNGS if k != RATE_CALIBRATION_RUNG))

    bad = [n for n, v in ok if not v]
    planted = [n for n, _ in ok if n.startswith(("PLANTED", "NEGATIVE", "CONJUNCT"))
               or "PLANTED" in n]
    print(f"\n{len(ok) - len(bad)}/{len(ok)} checks passed"
          + (f"; FAILED: {bad}" if bad
             else f"; {len(planted)} controls with a FAILING arm fired"))
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--launch", metavar="RUNG")
    ap.add_argument("--grade", metavar="RUNG")
    ap.add_argument("--sampler", action="store_true")
    ap.add_argument("--case"); ap.add_argument("--cap", type=float)
    ap.add_argument("--ranks", type=int); ap.add_argument("--pgid", type=int)
    ap.add_argument("--t0", type=float)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.sampler:
        return sampler_main(pathlib.Path(a.case), a.cap, a.ranks, a.pgid, a.t0)
    if a.launch:
        return launch(a.launch)
    if a.grade:
        return grade(a.grade)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
