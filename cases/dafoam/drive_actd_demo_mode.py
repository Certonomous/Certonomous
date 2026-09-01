#!/usr/bin/env python3
"""Drive Act D end to end through DEMO MODE and check what it published.

A PY_COMPILE IS NOT A WITNESS. This drives the act through the shared stage
sequencer on an injected clock, captures every payload that would reach a
screen, and asserts against the record the act reads from rather than against
anything written here. It launches nothing: the solver stage advances the
recorded run's own monitors, and the mesh stage never invokes a mesher (the
shared sequencer does not read ``MeshPlan.command`` at all).

What it asserts, and every one of them is a thing that would be wrong on
camera if it failed:

* all nine stages render, in ``demo_mode.STAGES`` order, each with its banner;
* the major-iteration counter reaches 47 of the 100 it was allowed, with all
  48 counted iterations published and none dropped;
* the displayed clock reads 20:00, and the two per-part figures shown beside
  it sum to 20:00 rather than to the run's own 3601 s;
* the pacing is a pure transform of the time column: every published objective
  and constraint value equals the recorded one to the bit;
* the adjoint monitor ships ragged, 100 solves opened, 99 completed, one left
  open, with one to four trace points each;
* the geometry stage renders a present-tense sentence that a measurement
  supports;
* the planted controls fire, on the objective curve and on the clock.

    python3 cases/dafoam/drive_actd_demo_mode.py
"""
from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sdk"))

os.environ.setdefault("CERTONOMOUS_NARRATION_PACE_MS", "0")
os.environ.setdefault("CERTONOMOUS_SWEEP_PACE_MS", "0")

RECORD = REPO / "cases" / "dafoam" / "ladder-a" / "A2_demo_mode_drive.json"


def capture(screen_seconds: float = 1200.0):
    """Drive the act on a virtual clock. Returns (events, sequencer record).

    The clock is injected and the sleep advances it, so twenty minutes of
    screen time passes in microseconds and not one published value changes:
    the sequencer's pacing is a scheduling decision and the values it
    schedules come from the record.
    """
    from workflows import adjoint_act, make_transcript

    now = [0.0]

    def clock() -> float:
        return now[0]

    def sleep(seconds: float) -> None:
        if seconds > 0:
            now[0] += seconds

    events = []

    def emit(kind, payload=None):
        events.append({"event": kind, "payload": payload})

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        script = make_transcript("adjoint-wing", emit)
        record = adjoint_act.drive(emit=emit, script=script,
                                   screen_seconds=screen_seconds,
                                   sleep=sleep, clock=clock)
    return events, record, adjoint_act.ACT.self_check()


def _of(events, kind):
    return [e["payload"] for e in events if e["event"] == kind]


def run_checks() -> tuple[dict, bool]:
    """Drive the act once and grade what it published. Never writes a file.

    Split out from :func:`main` so the mutation control below can run the
    SAME checks under a deliberately broken act. A control that ran a
    different, gentler set of checks would prove nothing about these ones.
    """
    from workflows.demo_mode import STAGES, validate_act
    from workflows import adjoint_act

    problems = validate_act(adjoint_act.ACT)
    if problems:
        return ({"refused_at_validation": problems,
                 "all_checks_held": False,
                 "checks": [{"check": "the act satisfies the demo-mode "
                                      "contract", "held": False,
                             "detail": problems}]}, False)

    events, sequencer_record, self_check = capture()
    series = json.loads(
        (REPO / "cases/dafoam/ladder-a/A2_replay_series.json")
        .read_text(encoding="utf-8"))
    clock = series["display_clock"]

    checks: list[dict] = []

    def check(name: str, held: bool, detail) -> None:
        checks.append({"check": name, "held": bool(held), "detail": detail})

    # ---- 1. every stage, in order, with a banner -------------------------
    order = [p["stage"] for p in _of(events, "stage.begin")]
    check("every stage renders in its normal order",
          tuple(order) == tuple(STAGES), order)
    published = list(sequencer_record["stages"])
    check("every stage published its content",
          tuple(published) == tuple(STAGES), published)
    banners = _of(events, "stage.banner")
    check("every publication carried a banner",
          len(banners) == sequencer_record["emitted"],
          {"banners": len(banners),
           "publications": sequencer_record["emitted"]})

    # ---- 2. the counter --------------------------------------------------
    frames = _of(events, "solve.frame")
    end = _of(events, "solve.end")[0]
    check("the counter reaches the recorded last iteration",
          frames[-1]["iteration"] == int(series["counter_runs_to"]) == 47,
          {"reached": frames[-1]["iteration"],
           "recorded": series["counter_runs_to"]})
    check("the counter runs against the cap the run was allowed",
          end["iterations"] == int(series["max_iter_setting"]) == 100,
          end["iterations"])
    check("no counted iteration was dropped to fit",
          len(frames) == len(series["series_major"]) == 48,
          {"published": len(frames),
           "recorded": len(series["series_major"])})

    # ---- 3. the clock ----------------------------------------------------
    elapsed = _of(events, "demo.elapsed")[0]
    parts = end["elapsed_parts"]
    total = sum(p["seconds"] for p in parts)
    check("the displayed clock reads twenty minutes",
          elapsed["clock"] == "20:00" and end["elapsed"] == "20:00",
          {"stage": end["elapsed"], "act": elapsed["clock"]})
    check("the parts shown beside it sum to twenty minutes",
          abs(total - float(clock["display_total_s"])) < 1e-6
          and end["elapsed_parts_sum"] == "20:00",
          {"parts": parts, "sum_s": total})
    check("the elapsed figure never appears without its basis",
          "production configuration" in elapsed["elapsed"],
          elapsed["elapsed"])

    # ---- 4. the transform touched the time column and nothing else -------
    recorded = series["series_major"]
    value_mismatches = []
    for frame, row in zip(frames, recorded):
        if frame["iteration"] != row["iter"]:
            value_mismatches.append({"iter": row["iter"], "field": "iter"})
        pairs = (("Drag coefficient", "objective_CD"),
                 ("Lift coefficient", "CL"),
                 ("Volume constraint", "volcon"))
        for shown, key in pairs:
            if frame["coefficients"][shown] != row[key]:
                value_mismatches.append({"iter": row["iter"], "field": key})
        for shown, key in (("Constraint violation", "inf_pr"),
                           ("First order measure", "inf_du")):
            if frame["residuals"][shown] != row[key]:
                value_mismatches.append({"iter": row["iter"], "field": key})
        if abs(frame["elapsed_s"] - row["wall_s"]
               / float(clock["pacing_ratio"])) > 1e-3:
            value_mismatches.append({"iter": row["iter"], "field": "time"})
    check("every published value is the recorded one, the clock aside",
          not value_mismatches, value_mismatches[:5])
    check("the pacing is the ratio the record states",
          abs(float(clock["pacing_ratio"]) - 3.0006618690490723) < 1e-12,
          clock["pacing_ratio_stated"])

    # ---- 5. the adjoint monitor, ragged as the log is --------------------
    adjoint = _of(events, "solve.adjoint")
    summary = series["adjoint_summary"]
    trace_lengths = sorted({len(a["trace"]) for a in adjoint})
    check("every adjoint linear solve is published",
          len(adjoint) == int(summary["linear_solves_opened"]) == 100,
          len(adjoint))
    check("the solve the clock ended inside is published as unfinished",
          sum(1 for a in adjoint if not a["completed"])
          == int(summary["linear_solves_truncated"]) == 1,
          {"left_open": end["adjoint_solves_left_open"]})
    check("the trace ships ragged rather than padded",
          trace_lengths == [int(summary["ksp_trace_points_per_solve_min"]),
                            2, 3,
                            int(summary["ksp_trace_points_per_solve_max"])],
          trace_lengths)

    # ---- 6. geometry, mesh, gates, results -------------------------------
    geometry = _of(events, "demo.geometry")[0]
    check("the geometry stage states the solved case in the present tense",
          geometry["statement"].startswith("Solved on this geometry"),
          geometry["statement"])
    check("no surface loaded never appears",
          not any("no surface" in json.dumps(e).lower() for e in events),
          "absent")
    mesh = _of(events, "demo.mesh")[0]
    check("the mesh stage states the cell count and no duration",
          mesh["cells"] == "38304 cells" and "second" not in json.dumps(mesh),
          mesh)
    results = _of(events, "demo.results")[0]
    check("the header names the solver of the source run",
          results["solver"].startswith("Solver: DAFoam DARhoSimpleFoam"),
          results["solver"])
    check("the cost line is this run's own cost",
          "240.1 core-minutes" in results["cost"], results["cost"])

    # ---- 7. the standing prohibitions ------------------------------------
    camera = json.dumps([e["payload"] for e in events]).lower()
    check("the act never says the optimizer converged",
          "converged" not in camera, "absent")
    check("the act never says optimum", "optimum" not in camera, "absent")

    # ---- 8. the planted controls -----------------------------------------
    check("the replay reader was shown a perturbation and read it back",
          self_check["plant_control"]["reader_is_evidence"],
          self_check["plant_control"])
    check("every string this act can produce passed the screen checker",
          self_check["strings_checked"] > 0,
          self_check["strings_checked"])

    held = all(c["held"] for c in checks)
    report = {
        "_what": ("Act D driven end to end through DEMO MODE: what the "
                  "sequencer published, checked against the record the act "
                  "reads from."),
        "_driver": "cases/dafoam/drive_actd_demo_mode.py",
        "_act": "sdk/workflows/adjoint_act.py",
        "nothing_launched": ("no solver and no mesher ran; the shared "
                             "sequencer does not read MeshPlan.command and "
                             "the solver stage reads committed records"),
        "stages_published": published,
        "events_emitted": len(events),
        "publications": sequencer_record["emitted"],
        "solver_frames": len(frames),
        "adjoint_events": len(adjoint),
        "displayed_clock": {"total": end["elapsed"], "parts": parts},
        "pacing_ratio": clock["pacing_ratio"],
        "self_check": self_check,
        "checks": checks,
        "all_checks_held": held,
    }
    return report, held


# =========================================================================
# The control: can these checks go red?
# =========================================================================

#: Each mutation breaks ONE thing, through a different door, and names the
#: check it is expected to turn red. A green from a checker not shown able to
#: go red is not evidence (CLAUDE.md rule 3), and this is that demonstration
#: for the checks above rather than for the act's data readers, which carry
#: their own plant.
def control() -> list[dict]:
    from workflows import adjoint_act

    frames = adjoint_act._major_frames
    parts = adjoint_act._clock_parts

    def drop_last(doc):
        return frames(doc)[:-1]

    def halve_parts(doc):
        return [(what, seconds * 0.5) for what, seconds in parts(doc)]

    def bend_one_value(doc):
        rows = frames(doc)
        rows[10]["objective_cd"] *= 1.001
        return rows

    def stretch_time(doc):
        rows = frames(doc)
        for row in rows:
            row["display_s"] *= 1.5
        return rows

    mutations = [
        ("a counted iteration is dropped to fit", "_major_frames", drop_last),
        ("the parts beside the clock stop summing to it", "_clock_parts",
         halve_parts),
        ("one published objective value is bent", "_major_frames",
         bend_one_value),
        ("the time axis is stretched away from the recorded ratio",
         "_major_frames", stretch_time),
    ]
    results = []
    for name, attribute, replacement in mutations:
        original = getattr(adjoint_act, attribute)
        setattr(adjoint_act, attribute, replacement)
        try:
            report, held = run_checks()
            reds = [c["check"] for c in report["checks"] if not c["held"]]
            outcome = "checks went red"
        except Exception as exc:                                # noqa: BLE001
            held, reds = False, [f"{type(exc).__name__}: {exc}"]
            outcome = "the act refused before publishing"
        finally:
            setattr(adjoint_act, attribute, original)
        results.append({"mutation": name, "caught": not held,
                        "how": outcome, "reds": reds})
    return results


def main() -> int:
    report, held = run_checks()
    if not held:
        report["control"] = {"skipped": "the clean drive did not hold, so the "
                                        "control was not run"}
        RECORD.write_text(json.dumps(report, indent=1) + "\n")
        print("REFUSED:")
        for entry in report["checks"]:
            if not entry["held"]:
                print("  NO ", entry["check"], entry["detail"])
        return 1

    controls = control()
    # The clean drive is re-run AFTER the mutations, so a mutation that failed
    # to restore itself cannot leave a green reading behind.
    report, held = run_checks()
    report["control"] = {
        "why": ("a green from a checker not shown able to go red is not "
                "evidence; each mutation breaks one thing through a "
                "different door"),
        "mutations": controls,
        "all_caught": all(c["caught"] for c in controls),
    }
    report["all_checks_held"] = held and report["control"]["all_caught"]
    RECORD.write_text(json.dumps(report, indent=1) + "\n")

    for entry in report["checks"]:
        print(f"  {'ok ' if entry['held'] else 'NO '} {entry['check']}")
    print(f"{sum(1 for c in report['checks'] if c['held'])}/"
          f"{len(report['checks'])} checks held; "
          f"{report['events_emitted']} events over "
          f"{len(report['stages_published'])} stages")
    for entry in controls:
        print(f"  {'ok ' if entry['caught'] else 'NO '} control: "
              f"{entry['mutation']} -> {entry['how']}")
    return 0 if report["all_checks_held"] else 1


if __name__ == "__main__":
    sys.exit(main())
