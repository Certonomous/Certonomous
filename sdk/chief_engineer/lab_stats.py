"""Lifetime lab counters — the numbers the credentials view leads with.

The standing credentials panel must open with what the lab has *done over its
lifetime* — missions run, solver core-hours, knowledge entries, experimental
anchors, benchmarks active — never a "4 of 8" fraction. Those counters come
from durable records, chiefly the all-night mega-batch ledger, so the number
grows honestly as real evaluations accumulate and survives restarts.

Everything here reads on-disk truth and rounds nothing up. If the ledger holds
812 real evaluations, ``missions_run`` reflects 812 — plus any missions the
server itself has persisted — and not a padded thousand.
"""

from __future__ import annotations

import datetime
import json
import os
import re
from pathlib import Path
from typing import Any

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]

# Fixed knowledge-base sizes (mirrors chief_engineer.citations / KnowledgeBase).
_KNOWLEDGE_ENTRIES = 7
_OPERATING_LESSONS = 1

# The two benchmarks the website tracks (see demo-output/website/benchmarks.json).
_ACTIVE_BENCHMARKS = ("closure-challenge", "reduced-order-speedup")

# Real, public research challenges the lab can honestly target with its actual
# capabilities (external-aerodynamics RANS, vortex-lattice wings, reduced-order
# internal-flow screens). Each entry was verified live against its host before
# inclusion. NEVER carries an invented score, rank, or result: the ``status``
# is where the lab stands, and ``entry`` is the real pipeline it would submit.
#
# Display order is deterministic and owner-directed: the two ``lead`` entries
# (Drag Prediction Workshop, then the NASA Turbulence Modeling Resource) render
# immediately after the closure-challenge card; the rest follow in tuple order.
_RESEARCH_CHALLENGES = (
    {
        "title": "AIAA Drag Prediction Workshop (NASA Common Research Model)",
        "host": "AIAA, with the NASA Common Research Model",
        "url": "aiaa-dpw.org",
        "what": "a standing public forum that grades CFD drag predictions on the "
                "NASA Common Research Model against published wind-tunnel data",
        "status": "target identified",
        "entry": "our external-aerodynamics RANS pipeline on the Common Research "
                 "Model, graded against the published experimental drag",
        "lead": True,
    },
    {
        "title": "NASA Turbulence Modeling Resource verification cases",
        "host": "NASA Langley / Turbulence Model Benchmarking Working Group",
        "url": "tmbwg.github.io/turbmodels",
        "what": "the reference verification cases, including the 2D flat plate and "
                "bump-in-channel, that a RANS code must reproduce on refined grids",
        # Measured 2026-07-24/25 by workflows/tmr_verification.py; full
        # numbers, deviations, and figures in demo-output/website/tmr/
        # (flatplate_sst.json, bump_sst.json, card_update.json).
        #
        # The entry said "3-grid ladder" after the flat plate had grown to
        # five rungs, and said nothing about what the extra two bought. Both
        # halves are now stated, and they are two claims rather than one:
        # VERIFICATION_CHARTER section 3.4. The band is certified. The order
        # behind it is still rising at every rung (1.0833, 1.2587, 1.6344), so
        # this ladder has not been shown to be in the asymptotic range, and
        # the entry must not let the first claim carry the second.
        #
        # tmr_verification.card_entry_text still writes a 3-rung sentence when
        # the act runs, because 816 to 13056 is what the act itself solves on
        # camera. That is accurate for the act and is not edited here. This
        # entry is the standing campaign record, which is two rungs further
        # on, and the two are allowed to differ as long as neither claims the
        # other's ladder.
        #
        # THE BUMP CARRIES ITS STATUS, added 2026-08-01 under ruling R5. The
        # two halves of this card are NOT two results of equal standing, and
        # until now the card let them read as though they were: the flat-plate
        # half is the lab's best verification result and the bump half has a
        # ladder that is not conclusive. Measured, from the bump's own record
        # (demo-output/website/tmr/bump_sst.json and the entry in
        # campaign/NOT_PASSING_REGISTER.md):
        #
        #   - None of the three bump rungs ever prints the solver's own
        #     convergence statement. All three stop on a fixed iteration count
        #     instead, and the rung the public number is quoted from exits with
        #     initial residuals roughly 200 to 500 times over the case's own
        #     residualControl.
        #   - Observed order 0.5446 as published, 0.516 when matched at the
        #     same iteration count. Either way it is far below the scheme's
        #     formal order.
        #   - The drag split is what holds it there. Viscous drag converges
        #     monotonically at order 1.091; PRESSURE drag is non-monotone,
        #     increments 2.00e-05 down then 6.42e-06 up, and has no observed
        #     order at all. CFL3D's pressure drag on the same three grids
        #     converges cleanly at 2.914.
        #   - uq.eca_hoekstra_band refuses the triplet outright, conclusive
        #     false and no reportable band, because the extrapolation diverges.
        #
        # The disclosure goes in "entry" rather than in "status" because
        # control_room.html renders status as a short coloured tag and maps
        # anything it does not recognise to the neutral class, so a caveat put
        # there would be shortened into a label and lose its content. "entry"
        # is rendered in full. The alternative the ruling allows is withdrawing
        # the bump from this card altogether; it is disclosed instead, because
        # the comparison is worth showing and only its standing was missing.
        #
        # LANGUAGE: this is a camera surface. No dashes, and none of the words
        # in tmr_verification.BANNED_CARD_WORDS.
        "status": "flat plate measured, bump not conclusive",
        "entry": "flat plate now on a 5-grid ladder to 208,896 cells and bump "
                 "on 3, against the published CFL3D values: flat-plate Cd "
                 "0.0028636 vs 0.0028533 at matched grid size, bump Cd "
                 "0.003567 vs 0.003607. The flat plate's finest triple is the "
                 "first ladder here to earn a reportable discretization band, "
                 "4.244e-6 or 0.148% of the value, at observed order 1.634; "
                 "that order is still rising rung on rung, so the band is "
                 "earned and the asymptotic range is not claimed. The two "
                 "halves do not stand equally and the bump number carries its "
                 "status: none of its three rungs prints the solver's own "
                 "convergence statement, its observed order is 0.52 with the "
                 "pressure component non-monotone, and the discretization "
                 "certifier refuses the triplet, so that 1.1% agreement is a "
                 "comparison and not a converged result. NACA 0012 airfoil "
                 "next",
        "lead": True,
    },
    {
        "title": "FDA medical-device CFD benchmark (nozzle and blood pump)",
        "host": "U.S. Food and Drug Administration, Critical Path Initiative",
        "url": "github.com/OSEL-DAM/CFD-and-Blood-Damage-Benchmarks",
        "what": "the FDA benchmark nozzle and centrifugal blood-pump geometries with "
                "particle-image-velocimetry validation data for internal blood flow",
        "status": "scoping",
        "entry": "our reduced-order internal-flow screen and a RANS nozzle solve, "
                 "aligned with the valve agenda and graded against the published "
                 "velocity fields",
        "lead": False,
    },
    {
        "title": "Automotive CFD Prediction Workshop (DrivAer)",
        "host": "AutoCFD steering committee (Oxford, Ford, and partners)",
        "url": "autocfd.org",
        "what": "a road-car aerodynamics benchmark on the DrivAer model, correlated "
                "against Pininfarina wind-tunnel measurements",
        "status": "target identified",
        "entry": "our external-aerodynamics RANS pipeline, the one that already runs "
                 "the motorBike body, carried onto the DrivAer geometry",
        "lead": False,
    },
)


def research_challenges() -> list[dict[str, Any]]:
    """Public research challenges the lab honestly targets (verified live).

    Returned as a fresh list of plain dicts so callers cannot mutate the module
    constant. Each dict keeps the same shape: title, host, url, what, status,
    entry, lead. The list order is the display order; ``lead`` entries render
    directly after the closure-challenge card. No score, rank, or result is
    ever asserted.
    """
    return [dict(item) for item in _RESEARCH_CHALLENGES]


def _ledger_path() -> Path:
    env = os.environ.get("CERTONOMOUS_MEGABATCH_LEDGER")
    if env:
        return Path(env).resolve()
    return (lab_paths.MEGA_BATCH / "ledger.jsonl").resolve()


def _credentials_root() -> Path:
    env = os.environ.get("CERTONOMOUS_CREDENTIALS")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "models" / "curriculum" / "results").resolve()


def _queue_root() -> Path:
    env = os.environ.get("CERTONOMOUS_QUEUE_ROOT")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "verification" / "queue").resolve()


# The runner's own predicate for "this launch record is the current one and not
# a copy retired by a later launch of the same case_id" -- transcribed from
# scripts/queue_runner.py:122 (ARCHIVED_RE) so the two cannot drift into
# disagreeing about which records are live. Skipping the retired copies is a
# CORRECTNESS requirement here, not tidiness: a retired record still names the
# SAME status_file as the launch that replaced it, so pairing its old start
# with that file's new end fabricates an interval nobody ran. Measured
# 2026-09-01: the 9 retired records on disk contributed a phantom 118.5
# core-hours that way, one of them (W3_chain) 92.5 core-hours by itself.
_QUEUE_ARCHIVED_RE = re.compile(r"\.\d{4}-\d{2}-\d{2}T\d{6}Z(\.\d+)?\.json$")
_QUEUE_END_RE = re.compile(r"end=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)")


def queue_summary(queue_root: Path | None = None) -> dict[str, Any]:
    """Measured compute the QUEUE RUNNER has spent, gross, live off disk.

    WHY THIS EXISTS (2026-09-01). The two lifetime tiles on the credentials
    wall -- "missions run" and "solver core-hours" -- were computed from the
    mega-batch ledger alone. That ledger's last row was written 2026-07-29
    11:17 and the batch runner has not written since, so both tiles stood
    frozen at 208,102 / 239.259 core-h while the lab ran a month of queued,
    pre-registered campaigns through ``scripts/queue_runner.py``. The tiles
    were not wrong about the ledger; they were stale about the lab. Nothing
    here is cached: like ``ledger_summary`` it reads the disk on every call,
    so the wall now moves as the queue runs and cannot go stale again.

    WHAT IS MEASURED, and from which artefacts. One row per CURRENT launch
    record under ``verification/queue/<team>/launched/*.json``:

      * start  = that record's ``_launch.started_epoch``, stamped by the
        runner at ``Popen`` time (queue_runner.py, ``meta["_launch"]``);
      * end    = the ``end=<utc>`` field of the detached wrapper's own STATUS
        file, named by ``_launch.status_file``;
      * ranks  = the entry's registered ``ranks``;
      * cost   = (end - start) x ranks / 60, the lab's unit (CLAUDE.md rule
        12: core-minutes = wall s x ranks / 60).

    A record with no STATUS file yet is a run still going or a run whose
    record was never completed: it is COUNTED AS UNFINISHED and contributes
    nothing, rather than being given an end time nobody measured.

    BASIS: **GROSS**, as ``COMPUTE_BUDGET_CHARTER.md`` defines it -- the sum
    over every row in the window with no row excluded for any reason, so it
    re-derives by summation alone with no judgement. It is deliberately NOT
    cleaned. The charter's one cleaning rule ("a ledger row over 3600 wall
    seconds is an infrastructure stall") is justified there by measured
    clustering in the mega-batch cylinder ledger, whose median row is 2.4
    seconds; queued T-family and DAFoam solves legitimately run for hours, so
    that threshold matches 47 of these 265 rows and would delete 90% of the
    figure (35,802 of 39,535 core-min, measured 2026-09-01) on a rule that was
    never calibrated for them. Cleaning here would be a judgement wearing a
    number's clothes, which is the exact failure the charter names.

    HONEST LIMITS, stated rather than left to be rediscovered:
      * The interval is LAUNCH-TO-COMPLETION wall, so for a chain/wait wrapper
        it includes time the wrapper spent waiting rather than solving. This
        figure is therefore an UPPER BOUND on solver compute, on the same
        gross basis the wall already published.
      * It covers the queue era only, which opens 2026-08-26T16:40:52Z. Work
        run between the ledger's last row (2026-07-29) and that date was
        launched by hand and is in neither source; it is uncounted, not zero.
    """
    root = queue_root or _queue_root()
    out: dict[str, Any] = {
        "launches_completed": 0, "launches_unfinished": 0,
        "core_minutes_gross": 0.0, "core_hours_gross": 0.0,
        "per_team": {}, "window_first_utc": None, "window_last_utc": None,
        "basis": "gross (no row excluded); launch-to-completion wall x ranks",
    }
    if not root.exists():
        return out
    core_minutes = 0.0
    per_team: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("*/launched/*.json")):
        if _QUEUE_ARCHIVED_RE.search(path.name):
            continue
        try:
            entry = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        launch = entry.get("_launch") or {}
        status = launch.get("status_file")
        started = launch.get("started_epoch")
        if not status or started is None:
            out["launches_unfinished"] += 1
            continue
        try:
            text = Path(status).read_text(encoding="utf-8", errors="replace")
        except Exception:
            out["launches_unfinished"] += 1
            continue
        match = _QUEUE_END_RE.search(text)
        if not match:
            out["launches_unfinished"] += 1
            continue
        end = datetime.datetime.strptime(
            match.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc).timestamp()
        wall = end - float(started)
        if wall < 0:          # clock skew or a STATUS from an earlier launch
            out["launches_unfinished"] += 1
            continue
        try:
            ranks = float(entry.get("ranks") or 1)
        except (TypeError, ValueError):
            ranks = 1.0
        cost = wall * ranks / 60.0
        core_minutes += cost
        out["launches_completed"] += 1
        team = str(entry.get("team", "unknown"))
        bucket = per_team.setdefault(team, {"count": 0, "core_minutes": 0.0})
        bucket["count"] += 1
        bucket["core_minutes"] += cost
        utc = launch.get("utc")
        if utc:
            if out["window_first_utc"] is None or utc < out["window_first_utc"]:
                out["window_first_utc"] = utc
            if out["window_last_utc"] is None or utc > out["window_last_utc"]:
                out["window_last_utc"] = utc
    out["core_minutes_gross"] = round(core_minutes, 1)
    out["core_hours_gross"] = round(core_minutes / 60.0, 3)
    out["per_team"] = {
        k: {"count": v["count"], "core_minutes": round(v["core_minutes"], 1)}
        for k, v in sorted(per_team.items())
    }
    return out


def read_ledger(ledger_path: Path | None = None) -> list[dict[str, Any]]:
    """Every well-formed row of the mega-batch ledger (ok and failed alike)."""
    path = ledger_path or _ledger_path()
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def ledger_summary(ledger_path: Path | None = None) -> dict[str, Any]:
    """Counts, wall-time totals, and per-solver breakdown from the ledger."""
    rows = read_ledger(ledger_path)
    ok_rows = [r for r in rows if r.get("ok")]
    per_solver: dict[str, dict[str, Any]] = {}
    core_seconds = 0.0
    for row in ok_rows:
        solver = str(row.get("solver", "unknown"))
        wall = float(row.get("wall_seconds") or 0.0)
        bucket = per_solver.setdefault(solver, {"count": 0, "wall_seconds": 0.0})
        bucket["count"] += 1
        bucket["wall_seconds"] += wall
        core_seconds += wall
    return {
        "evaluations_ok": len(ok_rows),
        "evaluations_failed": len(rows) - len(ok_rows),
        "core_seconds": round(core_seconds, 1),
        "core_hours": round(core_seconds / 3600.0, 3),
        "per_solver": {
            k: {"count": v["count"], "wall_seconds": round(v["wall_seconds"], 1)}
            for k, v in sorted(per_solver.items())
        },
    }


def _experimental_anchors() -> int:
    """Curriculum bodies carrying a cited experimental reference value."""
    root = _credentials_root()
    if not root.exists():
        return 0
    anchors = 0
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("reference_cd") is not None and data.get("reference_source"):
            anchors += 1
    return anchors


def _benchmarks_path() -> Path:
    env = os.environ.get("CERTONOMOUS_BENCHMARKS")
    if env:
        return Path(env).resolve()
    return lab_paths.BENCHMARKS_JSON.resolve()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _ledger_study_path() -> Path:
    env = os.environ.get("CERTONOMOUS_LEDGER_STUDY")
    if env:
        return Path(env).resolve()
    return _ledger_path().parent / "learned_study.json"


def _fleet_learning() -> dict[str, Any]:
    """Learning-from-the-fleet-ledger card, driven by the distilled study.

    Every number comes from the study JSON that ``ledger_learning`` distilled
    out of real ledger rows; when no study exists yet the card says so plainly
    instead of inventing figures.
    """
    study = _load_json(_ledger_study_path())
    title = "Learning from the fleet ledger"
    if not study or "provenance" not in study:
        return {
            "title": title,
            "status": "PENDING",
            "summary": "The distiller has not run over the fleet ledger yet; "
                       "the first mega-batch pass will produce this card.",
            "available": False,
        }

    prov = study.get("provenance", {})
    families = study.get("families", {})
    family_rows = [
        {
            "solver": name,
            "label": fam.get("label", name),
            "ok": fam.get("ok", 0),
            "failed": fam.get("failed", 0),
            "failure_rate": fam.get("failure_rate", 0.0),
        }
        for name, fam in families.items()
    ]
    wing = study.get("wing", {})
    best_wing = wing.get("best")
    return {
        "title": title,
        "status": "ACTIVE RESEARCH",
        "summary": (
            f"Distilled from {prov.get('row_count', 0)} rows of the mega-batch "
            f"ledger ({prov.get('ok_rows', 0)} completed evaluations); every "
            f"relationship carries measured fit quality, never assertion."
        ),
        "available": True,
        "generated_at": study.get("generated_at"),
        "row_count": prov.get("row_count"),
        "ok_rows": prov.get("ok_rows"),
        "failed_rows": prov.get("failed_rows"),
        "families": family_rows,
        "best_wing": best_wing,
        "highlights": list(study.get("learned", [])),
    }


# Fallback only: used if benchmarks.json has not been generated yet or is
# missing the key. The live value always comes from closure_raw["our_entry"]
# below, which build_benchmarks.py writes into benchmarks.json; that file is
# the single source of truth for this status text, so this literal and the
# one in scripts/build_benchmarks.py must be kept in sync.
_NO_ENTRY_YET = (
    "No entry submitted. Measured a zero-training RANS reference floor of "
    "0.1036 overall, scored by the benchmark's own unmodified code; worse "
    "than every published entry, since it reflects no learned correction"
)


def research_programs() -> dict[str, Any]:
    """The lab's real research programmes, framed as work in progress.

    Closure-challenge and reduced-order speed figures come from the public
    benchmarks file; the fleet-learning card is driven by the distilled
    ledger study; the valve agenda lines are the queued programmes; and the
    challenges list is the real, public benchmarks the lab has targeted, in
    display order with the two ``lead`` entries placed by the owner directly
    after the closure card.
    """
    bench = _load_json(_benchmarks_path())
    closure_raw = bench.get("closure_challenge", {})
    speed_raw = bench.get("speed_benchmark", {})

    closure = {
        "title": closure_raw.get("name", "Closure-challenge benchmark"),
        # The generator's own status wins. This card used to hardcode
        # "ACTIVE RESEARCH" over whatever benchmarks.json said, so the file
        # could record a programme closed and the card would keep calling it
        # open, with nothing anywhere saying the two disagreed.
        "status": closure_raw.get("status", "ACTIVE RESEARCH"),
        "board": closure_raw.get("board", "public leaderboard"),
        # Which rank the board is shown against is a decision recorded in
        # benchmarks.json, not here. This fallback exists only so a missing
        # key cannot render a blank rank, and it must never silently disagree
        # with the generator: the number and the per-case row it labels have
        # to come from the same entry, or the card credits one team's cases
        # to another's rank.
        "target_rank": closure_raw.get("target_rank", 4),
        "target_overall": closure_raw.get("target_overall"),
        "target_per_case": closure_raw.get("target_per_case", []),
        "our_entry": closure_raw.get("our_entry", _NO_ENTRY_YET),
        # Zero-training RANS-identity reference floor, not a submission and
        # not a trained result; see the our_entry text above, which always
        # states that plainly wherever this card is rendered.
        "our_score": closure_raw.get("our_score"),
        "our_per_case": closure_raw.get("our_per_case", []),
        # The zero-training RANS-identity reference floor, so the card can show
        # the movement (floor -> gated entry) rather than only the end point.
        # Both values come from benchmarks.json; neither is computed here.
        "floor_overall": closure_raw.get("rans_identity_floor_overall"),
        # The per-case floor, carried for the same reason the overall floor is:
        # the card shows a per-case row for the target and for our entry, and
        # showing those two without the floor row they moved from is the
        # movement stated with one of its two ends missing. It was dropped by
        # nothing more than a key list that predated it.
        "floor_per_case": closure_raw.get("rans_identity_floor_per_case", []),
        "submitted": False,
        "target": "top 4",
        "repo": "github.com/rmcconke/closure-challenge-benchmark",
    }
    # DELIBERATELY NOT CARRIED: `source`. The benchmarks file cites an
    # internal working note, and internal file references never reach a
    # user-visible surface. Named here rather than left as an absence, so the
    # exclusion can be argued with instead of rediscovered.
    speed = {
        "title": speed_raw.get("name", "Reduced-order speed program"),
        "status": speed_raw.get("status", "measured"),
        "case": speed_raw.get("case", "NACA 4412"),
        "full_core_min": speed_raw.get("full_mc_core_min"),
        "reduced_core_min": speed_raw.get("reduced_core_min"),
        "speedup_x": speed_raw.get("speedup_x"),
    }
    queued = [
        {"name": "Harmonic-balance cycle solve",
         "note": "periodic flow solved in the frequency domain, not marched in time"},
        {"name": "Unsteady fluid-structure interaction",
         "note": "leaflet motion coupled to the flow it drives"},
        {"name": "Non-Newtonian rheology",
         "note": "shear-thinning blood models for the valve agenda"},
    ]
    return {
        "closure": closure,
        "speed": speed,
        "fleet_learning": _fleet_learning(),
        "queued": queued,
        "challenges": research_challenges(),
    }


def _persisted_missions() -> int:
    """Demo missions the server has persisted to state (best-effort)."""
    state_dir = os.environ.get("CHIEF_ENGINEER_STATE_DIR")
    if not state_dir:
        return 0
    root = Path(state_dir)
    if not root.exists():
        return 0
    return sum(1 for _ in root.glob("m-*.json"))


def lifetime_counters(ledger_path: Path | None = None,
                      include_queue: bool | None = None) -> dict[str, Any]:
    """The header row: missions run, core-hours, knowledge, anchors, benchmarks.

    ``missions_run`` = real+ROM evaluations in the ledger, plus any missions the
    server itself persisted, plus completed queue-runner launches. Honest,
    durable, never rounded.

    ``include_queue`` defaults to "only when no ledger was injected". A caller
    that passes its own ``ledger_path`` is scoping the counters TO THAT LEDGER
    -- a fixture, a bundle snapshot, a replay -- and folding this box's live
    queue into that answer would mix two unrelated worlds. Pass it explicitly to
    override in either direction.
    """
    if include_queue is None:
        include_queue = ledger_path is None
    summary = ledger_summary(ledger_path)
    persisted = _persisted_missions()
    # The queue era, added 2026-09-01. Both tiles used to end at the mega-batch
    # ledger, which stopped being written on 2026-07-29, so both stood still
    # through a month of queued campaigns. The two sources cannot double-count:
    # the ledger's last row is 2026-07-29T11:17 and the first queue launch is
    # 2026-08-26T16:40:52Z. A failure to read the queue must never take the wall
    # down, so it degrades to the ledger-only figure rather than raising.
    try:
        queue = queue_summary() if include_queue else None
    except Exception:
        queue = None
    if queue is None:
        queue = {"launches_completed": 0, "launches_unfinished": 0,
                 "core_minutes_gross": 0.0, "core_hours_gross": 0.0,
                 "per_team": {}, "window_first_utc": None,
                 "window_last_utc": None, "basis": "unavailable"}
    return {
        "missions_run": summary["evaluations_ok"] + persisted
        + queue["launches_completed"],
        "solver_core_hours": round(
            summary["core_hours"] + queue["core_hours_gross"], 3),
        "queue_core_hours": queue["core_hours_gross"],
        "knowledge_entries": _KNOWLEDGE_ENTRIES + _OPERATING_LESSONS,
        "experimental_anchors": _experimental_anchors(),
        "benchmarks_active": len(_ACTIVE_BENCHMARKS),
        "detail": {
            "ledger_evaluations": summary["evaluations_ok"],
            "ledger_failed": summary["evaluations_failed"],
            "ledger_core_hours": summary["core_hours"],
            "persisted_missions": persisted,
            "per_solver": summary["per_solver"],
            "queue": queue,
        },
        # The active-research programmes the credentials view showcases as
        # work in progress (R5): closure challenge, the public challenge
        # targets, reduced-order speed, and the queued valve agenda.
        "research": research_programs(),
    }


if __name__ == "__main__":
    print(json.dumps(lifetime_counters(), indent=2))
