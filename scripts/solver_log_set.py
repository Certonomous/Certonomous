#!/usr/bin/env python3
"""THE SOLVER LOG SET -- count a run's physics across EVERY segment it was run in.

WHY THIS EXISTS, with the run that paid for it.

On 2026-09-12 the box was resized and rebooted at 21:32Z.  SUBOFF SOLVE_L2 had
reached Time = 63 with a complete checkpoint at t = 60 in all four rank trees.
Sanaa's ruling that evening, byte-exact: "I DONT want to restart from 0 what do
you not understand about us being under time pressure ?", standing on her earlier
universal rule of 2026-08-26, BOOKKEEPING NEVER VOIDS PHYSICS.

The obstacle was never the physics.  It was that every completion reader in this
lab counts `ExecutionTime` LINES IN ONE FILE and compares that count to
`round(endTime/deltaT)`.  A resumed run does not produce one file, and -- this is
the part that the obvious repair gets wrong -- CONCATENATING THE SEGMENTS DOES NOT
FIX IT EITHER.

MEASURED ON SOLVE_L2, which is why this module counts the way it does:

    segment 1 (killed by the reboot)   62 ExecutionTime lines, Time = 1 .. 63
    resume from the t = 60 checkpoint  2,940 lines,            Time = 61 .. 3000
    -------------------------------------------------------------------------
    naive sum of lines                 3,002
    required                           3,000
    distinct physics steps reached     3,000   <-- the true answer

Iterations 61, 62 and 63 were run TWICE: once before the kill, and again after the
resume, because the checkpoint they are re-run from is t = 60.  A line count
double-counts them.  Appending the second segment onto the first (`>` -> `>>`)
makes the count reachable but makes it WRONG BY THE SIZE OF THE GAP BETWEEN THE
LAST CHECKPOINT AND THE KILL -- a number that varies per kill and that nobody can
see from the log.

So the count is taken on the PHYSICS: the set of DISTINCT `Time =` values the run
actually reached, unioned across every segment.  Re-run steps collapse, as they
should, because a step re-run is still one step of physics.

THIS IS STRICTLY STRONGER THAN WHAT IT REPLACES, AND THAT IS DELIBERATE.
Standing rule 4 clause 5 is not weakened here; WHERE the count is read from
changes, WHAT is required does not, and one hole is closed on the way:

    old:  3,000 ExecutionTime lines in one file.  A log with 3,000 lines that
          SKIPS step 1,500 passes.  A log that logs step 7 twice passes.
    new:  the distinct steps reached must be exactly {1 .. endTime}.  A skipped
          step is named.  A repeated step is collapsed, not credited twice.

The age guard, the endTime match, the `End` line and the field list ALL STAND and
are not this module's business -- it reports `end_line` and `last_time` for the
caller's own clauses and gates nothing itself.

WHAT COUNTS AS A SEGMENT.  `log.<solver>` is the original.  `log.<solver>.resumeN`,
`log.<solver>.N` and `log.<solver>.<anything>` are continuations.  They are ordered
original-first, then by numeric suffix where there is one and mtime where there is
not.  A driver that APPENDS all its segments into the single original file is
handled by exactly the same code path, because the union is taken over lines, not
over files -- which is the point: the reader no longer cares how the writer chose
to lay its segments out on disk.

CONTROLS (standing rule 3 -- a zero from a reader not shown able to see a non-zero
is not evidence).  `--selftest` builds temporary fixtures, never a real run tree:

  * PLANTED STEP.  A step is REMOVED from the middle of a complete log and the
    reader is REQUIRED to name that exact step as missing.  A reader that cannot
    see a planted hole cannot be trusted to report its absence, and the suite
    REFUSES (exit 2) if it does not see it.
  * THE SOLVE_L2 SHAPE, with its real numbers: 62 lines to Time = 63, resume from
    60 to 3,000, and the suite requires n_steps == 3000 while the raw line sum is
    3,002 -- i.e. it requires the two figures TO DISAGREE, so a regression back to
    line counting goes red rather than silently passing.
  * SPLIT vs APPENDED must give the SAME answer on the same physics.
  * A single unresumed log still gives the historical answer, so no completed run
    changes meaning under this module.
  * STALE `End`, IN BOTH LAYOUTS.  A run that finished, had its endTime raised, was
    resumed and then KILLED must NOT be credited with an `End`.  Split layout: the
    stale End lands in an earlier file and the last-segment rule catches it.
    APPENDED layout: there is only one file, so the stale End sits mid-file in the
    LAST segment and the last-segment rule cannot see it -- which is why `End` is
    credited only when it FOLLOWS the final `Time =` line.  Both are tested,
    because the appended layout is the one the SUBOFF driver now uses.
  * REAL `End` STILL CREDITED -- the control on the control, so the fixture above
    cannot pass by making `End` uncreditable.

`--mutation-control` neuters the distinct-set logic in a temporary COPY of this
file and requires the suite to go RED; a control that cannot fail is not a control.

No bare `assert` appears in this file, so `python3` and `python3 -O` return the
same rc.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

TIME_RE = re.compile(r"^Time = ([0-9.eE+-]+)\s*$", re.M)
EXEC_RE = re.compile(r"^ExecutionTime = ", re.M)
END_RE = re.compile(r"^End\s*$", re.M)


def segments(case: str | os.PathLike, solver: str = "simpleFoam") -> List[Path]:
    """Every log segment for one run, ORIGINAL FIRST.

    The original is `log.<solver>` exactly.  Continuations are `log.<solver>.*`
    EXCEPT the driver's own bookkeeping sidecars, which are not solver logs and
    carry no physics: `.solve` phase logs for other utilities are named
    `log.decomposePar.solve` etc. and never match `log.<solver>.`, so the only
    exclusions needed are explicit.
    """
    case = Path(case)
    base = case / f"log.{solver}"
    out: List[Path] = [base] if base.is_file() else []
    tail: List[Path] = []
    for p in sorted(case.glob(f"log.{solver}.*")):
        if p.name.endswith((".gz", ".bz2", ".xz")):
            continue
        if not p.is_file():
            continue
        tail.append(p)

    def key(p: Path):
        m = re.search(r"(\d+)$", p.name)
        return (0, int(m.group(1))) if m else (1, p.stat().st_mtime)

    tail.sort(key=key)
    return out + tail


def scan(case: str | os.PathLike,
         solver: str = "simpleFoam",
         end_time: Optional[float] = None,
         delta_t: float = 1.0) -> Dict[str, Any]:
    """Read a run's physics across every segment.

    Returns `n_steps` -- DISTINCT `Time =` values reached, unioned across segments
    -- plus `n_exec_lines_raw`, which is BOOKKEEPING and is reported so a reader
    can SEE the double-count rather than be protected from it.  `end_line` is read
    from the LAST segment only: an `End` in an earlier segment belongs to a run
    that was later continued, and does not say this run finished.
    """
    segs = segments(case, solver)
    steps: set = set()
    n_exec_raw = 0
    per_segment: List[Dict[str, Any]] = []
    end_line = False
    for i, p in enumerate(segs):
        body = p.read_text(errors="replace")
        found = [float(x) for x in TIME_RE.findall(body)]
        n_ex = len(EXEC_RE.findall(body))
        # AMENDMENT 2026-09-12 -- `End` MUST FOLLOW THE FINAL `Time =` LINE.
        #
        # `END_RE.search(body)` alone credits a STALE End sitting mid-file, and the
        # APPENDED layout -- the one the SUBOFF driver now uses, where a resume
        # appends into the original file -- puts exactly that case in the LAST
        # segment, where the last-segment rule cannot catch it.  Shape: a run
        # finishes at endTime and writes End; endTime is later raised; the resume
        # appends and is then KILLED with no trailing End.  A body search returns
        # True for a run that was killed.
        #
        # This does not bite SOLVE_L2 tonight -- segment 1 was killed by the reboot
        # and wrote no End -- and the other clauses would refuse anyway.  But rule
        # 4's strength is that its six clauses are INDEPENDENT, and a body search
        # degrades one of them to always-true in the layout now standardised on.
        # A clause that cannot fail is not a clause.
        m_end = None
        for m_end in END_RE.finditer(body):
            pass
        last_time_pos = -1
        for m_t in TIME_RE.finditer(body):
            last_time_pos = m_t.start()
        seg_end = bool(m_end) and (m_end.start() > last_time_pos)
        n_exec_raw += n_ex
        steps.update(found)
        per_segment.append({
            "log": p.name,
            "n_Time_lines": len(found),
            "n_distinct_Time": len(set(found)),
            "n_ExecutionTime_lines": n_ex,
            "first_Time": min(found) if found else None,
            "last_Time": max(found) if found else None,
            "End_line": seg_end,
        })
        if i == len(segs) - 1:
            end_line = seg_end

    ordered = sorted(steps)
    r: Dict[str, Any] = {
        "segments": per_segment,
        "n_segments": len(segs),
        "resumed": len(segs) > 1,
        "n_steps": len(ordered),
        "n_exec_lines_raw": n_exec_raw,
        "line_count_overcounts_by": n_exec_raw - len(ordered),
        "end_line": end_line,
        "last_time": ordered[-1] if ordered else None,
        "first_time": ordered[0] if ordered else None,
        "counting": ("DISTINCT PHYSICS STEPS unioned across every segment, NOT a "
                     "line count in one file. A step re-run after a resume is one "
                     "step of physics and is counted once."),
    }
    if end_time is not None:
        expected_n = int(round(end_time / delta_t))
        want = [round((i + 1) * delta_t, 10) for i in range(expected_n)]
        seen = {round(t, 10) for t in ordered}
        missing = [t for t in want if t not in seen]
        extra = sorted(seen - set(want))
        r["expected_n_steps"] = expected_n
        r["missing_steps"] = missing[:20]
        r["n_missing_steps"] = len(missing)
        r["unexpected_steps"] = extra[:20]
        # The clause, stated exactly: every registered step reached, and none
        # outside the registered range.  Strictly stronger than `count == N`.
        r["clause_exec_count"] = (len(missing) == 0 and len(extra) == 0
                                  and len(ordered) == expected_n)
        r["clause_last_eq_endTime"] = (r["last_time"] is not None and
                                       abs(r["last_time"] - end_time) < 1e-9)
    return r


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------

def _write_log(path: Path, times, end=False, banner=True) -> None:
    parts = []
    if banner:
        parts.append("Build  : v2606\nnProcs : 4\n")
    for t in times:
        parts.append(f"Time = {t:g}\n\nExecutionTime = {t:.2f} s  ClockTime = {t:.0f} s\n\n")
    if end:
        parts.append("End\n")
    path.write_text("".join(parts))


def _selftest() -> int:
    fails: List[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        if not cond:
            fails.append(f"{name}: {detail}")

    with tempfile.TemporaryDirectory() as td:
        # --- 1. the SOLVE_L2 shape, with its real numbers ------------------
        c = Path(td) / "L2"
        c.mkdir()
        # THE FIXTURE MODELS THE SHAPE, NOT THE ARTIFACT, AND THE TWO DIFFER BY ONE
        # LINE.  The docstring quotes the REAL SOLVE_L2 log: 62 ExecutionTime lines,
        # because the kill took the 63rd before it was flushed, giving a real raw sum
        # of 3,002.  This fixture writes 63 CLEAN steps, so its raw sum is 3,003.
        # Both numbers are right about their own object; the fixture is deliberately
        # the tidier one so the control does not depend on exactly where a kill
        # happened to land.  The property under test is identical either way: the raw
        # line sum EXCEEDS the distinct step count by the size of the resume overlap.
        _write_log(c / "log.simpleFoam", range(1, 64))            # 63 steps, killed
        _write_log(c / "log.simpleFoam.resume1",
                   range(61, 3001), end=True, banner=True)        # resume from t=60
        r = scan(c, "simpleFoam", end_time=3000, delta_t=1.0)
        check("L2 n_steps", r["n_steps"] == 3000, f"got {r['n_steps']}")
        check("L2 raw line sum", r["n_exec_lines_raw"] == 3003,
              f"got {r['n_exec_lines_raw']}")
        # THE TWO FIGURES MUST DISAGREE.  If a regression puts line counting
        # back, this is the check that goes red.
        check("L2 line count DOES overcount",
              r["n_exec_lines_raw"] != r["n_steps"],
              "raw line sum equals n_steps -- the double-count is invisible, "
              "which means the reader is counting lines again")
        check("L2 clause", r["clause_exec_count"] is True, str(r.get("missing_steps")))
        check("L2 last time", r["clause_last_eq_endTime"] is True, str(r["last_time"]))
        check("L2 end line from LAST segment", r["end_line"] is True, "")
        check("L2 resumed flag", r["resumed"] is True, "")

        # --- 2. PLANTED HOLE.  A reader that cannot see it is refused. -----
        c2 = Path(td) / "PLANT"
        c2.mkdir()
        planted = 1500
        keep = [t for t in range(1, 3001) if t != planted]
        _write_log(c2 / "log.simpleFoam", keep, end=True)
        r2 = scan(c2, "simpleFoam", end_time=3000, delta_t=1.0)
        check("PLANT sees the hole", r2["n_missing_steps"] == 1,
              f"n_missing={r2['n_missing_steps']}")
        check("PLANT names the exact step", r2["missing_steps"] == [float(planted)],
              f"named {r2['missing_steps']}")
        check("PLANT refuses the clause", r2["clause_exec_count"] is False, "")
        if r2["n_missing_steps"] != 1 or r2["missing_steps"] != [float(planted)]:
            sys.stderr.write(
                "REFUSED: the planted missing step was not seen. A reader that "
                "cannot see a hole it was shown cannot be trusted to report one "
                "it was not.\n")
            return 2

        # --- 3. a line count ALONE would have passed the planted case ------
        # 2,999 lines != 3,000 so the old reader would have caught THIS hole,
        # but not a log that logs one step twice and another never.  Show that.
        c3 = Path(td) / "PLANT2"
        c3.mkdir()
        dup = [t for t in range(1, 3001) if t != 1500] + [1499]
        _write_log(c3 / "log.simpleFoam", dup, end=True)
        r3 = scan(c3, "simpleFoam", end_time=3000, delta_t=1.0)
        check("PLANT2 line count would have passed",
              len(dup) == 3000, f"fixture wrong: {len(dup)}")
        check("PLANT2 distinct count catches it", r3["clause_exec_count"] is False,
              "a log with the right NUMBER of lines but a missing step passed")

        # --- 4. SPLIT and APPENDED must agree ------------------------------
        c4 = Path(td) / "APPEND"
        c4.mkdir()
        one = c4 / "log.simpleFoam"
        _write_log(one, range(1, 64))
        with one.open("a") as f:
            for t in range(61, 3001):
                f.write(f"Time = {t:g}\n\nExecutionTime = {t:.2f} s  ClockTime = {t:.0f} s\n\n")
            f.write("End\n")
        r4 = scan(c4, "simpleFoam", end_time=3000, delta_t=1.0)
        check("APPEND == SPLIT on n_steps", r4["n_steps"] == r["n_steps"],
              f"{r4['n_steps']} vs {r['n_steps']}")
        check("APPEND clause", r4["clause_exec_count"] is True, "")

        # --- 5. an UNRESUMED log keeps its historical meaning --------------
        c5 = Path(td) / "PLAIN"
        c5.mkdir()
        _write_log(c5 / "log.simpleFoam", range(1, 101), end=True)
        r5 = scan(c5, "simpleFoam", end_time=100, delta_t=1.0)
        check("PLAIN n_steps", r5["n_steps"] == 100, f"got {r5['n_steps']}")
        check("PLAIN agrees with the line count", r5["n_exec_lines_raw"] == 100, "")
        check("PLAIN clause", r5["clause_exec_count"] is True, "")
        check("PLAIN not resumed", r5["resumed"] is False, "")

        # --- 6. an End in an EARLIER segment is not this run's End ---------
        c6 = Path(td) / "STALEEND"
        c6.mkdir()
        _write_log(c6 / "log.simpleFoam", range(1, 64), end=True)
        _write_log(c6 / "log.simpleFoam.resume1", range(61, 100), end=False)
        r6 = scan(c6, "simpleFoam", end_time=3000, delta_t=1.0)
        check("STALEEND end_line is False", r6["end_line"] is False,
              "an End line from a segment that was later continued was credited "
              "to the resumed run")

        # --- 7. APPENDED layout: a stale End MID-FILE is not credited ------
        # The hole the split-layout fixture (6) cannot reach: here the stale End
        # lands in the LAST segment, because there is only one file.
        c7 = Path(td) / "STALEEND_APPENDED"
        c7.mkdir()
        one7 = c7 / "log.simpleFoam"
        _write_log(one7, range(1, 101), end=True)      # finished at 100, wrote End
        with one7.open("a") as f:                      # endTime raised; resume appends
            for t in range(101, 151):
                f.write(f"Time = {t:g}\n\nExecutionTime = {t:.2f} s  ClockTime = {t:.0f} s\n\n")
            # KILLED: no trailing End
        r7 = scan(c7, "simpleFoam", end_time=200, delta_t=1.0)
        check("APPENDED stale End is NOT credited", r7["end_line"] is False,
              "an End line sitting mid-file was credited to a run that was killed; "
              "rule 4's End clause has been degraded to always-true in the appended "
              "layout")
        check("APPENDED stale End: other clauses still refuse",
              r7["clause_exec_count"] is False and r7["n_missing_steps"] == 50,
              f"n_missing={r7.get('n_missing_steps')}")
        check("APPENDED stale End: last_time is the resume's",
              r7["last_time"] == 150.0, str(r7["last_time"]))

        # --- 8. a REAL End, after the final Time line, IS credited ---------
        # The control on the control: fixture 7 must not pass by making `End` never
        # creditable.  Same appended shape, finished properly.
        c8 = Path(td) / "REALEND_APPENDED"
        c8.mkdir()
        one8 = c8 / "log.simpleFoam"
        _write_log(one8, range(1, 101), end=True)
        with one8.open("a") as f:
            for t in range(101, 201):
                f.write(f"Time = {t:g}\n\nExecutionTime = {t:.2f} s  ClockTime = {t:.0f} s\n\n")
            f.write("End\n")
        r8 = scan(c8, "simpleFoam", end_time=200, delta_t=1.0)
        check("APPENDED real End IS credited", r8["end_line"] is True,
              "the End rule is now so strict it cannot pass a completed run")
        check("APPENDED real End: clause passes", r8["clause_exec_count"] is True, "")

    if fails:
        sys.stderr.write("SELFTEST RED:\n" + "\n".join("  " + f for f in fails) + "\n")
        return 1
    sys.stdout.write("SELFTEST GREEN: 8 fixtures, planted hole seen and named, "
                     "split == appended, unresumed unchanged, stale End not credited in "
                     "EITHER layout, real End still credited.\n")
    return 0


def _mutation_control() -> int:
    """Neuter the distinct-set logic in a COPY and require the suite to go RED."""
    src = Path(__file__).read_text()
    mutated = src.replace("steps.update(found)", "steps.update(range(1, 3001))", 1)
    if mutated == src:
        sys.stderr.write("MUTATION CONTROL BROKEN: the mutation site was not found; "
                         "the control cannot fail and is therefore not a control.\n")
        return 2
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "solver_log_set.py"
        p.write_text(mutated)
        import subprocess
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, str(p), "--selftest"],
                           capture_output=True, text=True, env=env)
        if r.returncode == 0:
            sys.stderr.write("MUTATION CONTROL RED->GREEN: the neutered reader PASSED "
                             "its own suite. The suite does not test what it claims.\n")
            return 1
    sys.stdout.write("MUTATION CONTROL OK: the neutered reader FAILS the suite "
                     f"(rc={r.returncode}).\n")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "--mutation-control" in sys.argv:
        sys.exit(_mutation_control())
    if len(sys.argv) > 1:
        import json
        case = sys.argv[1]
        solver = sys.argv[2] if len(sys.argv) > 2 else "simpleFoam"
        et = float(sys.argv[3]) if len(sys.argv) > 3 else None
        print(json.dumps(scan(case, solver, et), indent=2, default=str))
        sys.exit(0)
    sys.stderr.write(__doc__ or "")
    sys.exit(2)
