# VMFL045 — run-and-grade lane report to `ansys-verification-supervisor`

**From:** `ansys-lane-opus48` (Opus 4.8), the **run-and-grade** lane (a second lane
dispatched on VMFL045). **Date:** 2026-08-25.
**Delivery:** `SendMessage` lane→supervisor is one-way and failed ("No agent named
'ansys-verification-supervisor' is reachable"), so this committed file is the report of
record (L-306). **Written to a DISTINCT path** — `LANE_REPORT.md` is the FIRST lane's
crash-triage report of record (commit `f1f58fd`), which this lane reads and credits and
does **not** overwrite.

**HEADLINE: VMFL045 run 1 is `NOT A RESULT` / tier `NOT HELD` at 0.0000 core-min — the
frozen case crashed on its first timestep on a frozen-`fvSolution` `e`/`h` defect. Run 1
is recorded; the repair is the frozen (NOT launched) VMFL045-R2 rung. A concurrent
second dispatch launched nothing into the live run — the launcher's guard refused it.**

---

## 1. What I did, in order (all authorised by the supervisor's triage)

1. **Safety check (01:36:44Z):** run dir ABSENT, no solver processes, load 2.15. Clean.
2. **Freeze verification:** all three named blobs match (prereg `7a7f9d52`, comparator
   `0c83eeef`, launcher `db393261`); all ten §10 input blobs match HEAD; worktree
   copies of prereg/comparator/launcher byte-identical to HEAD. **The freeze is intact.**
3. **Launch attempt:** wrote the launch contention sample, launched `run_vmfl045.sh`
   with `setsid`. **The launcher REFUSED at guard 1** (`LAUNCHER_EXIT=2`): `L1_90x76`
   already existed. **I launched no solver and created nothing inside `L1_90x76`.**
4. **Triage** (converging with the first lane and the supervisor — see §2).
5. **Records written and committed** (§4), **R2 built and frozen but NOT launched** (§3).

## 2. The two findings

**Finding A — concurrent dispatch on a reading stale by seconds (the supervisor's,
recorded as such).** Two lanes were dispatched on VMFL045. The supervisor checked at
01:35:26Z, saw no run dir, concluded the first lane was dead, and dispatched this lane.
The first lane then launched at **01:36:45Z** — one second after this lane's own safety
check at 01:36:44Z also found the dir absent. This lane's launcher refused into the
pre-existing `L1_90x76`. **Nothing was corrupted, and the launcher's guard-1 is the only
reason that is true** — the same failure class as a stale git base, in agent dispatch.
(A live foreign monitor PID 1969799 was polling the run dir for a GRADING json that a
crashed run never produced; harmless, timed out.)

**Finding B — the frozen case does not run (crash = finding, triaged; INDEPENDENTLY
REPLICATED).** `rhoCentralFoam` crashed on its first timestep, `rc=1`, `wall=0 s`:
`Entry 'e' not found in dictionary "system/fvSolution/solvers"`. Root cause, reached
independently by the first lane, this lane and the supervisor: frozen
`thermophysicalProperties` sets `energy sensibleInternalEnergy` (field `e`) but the
frozen `fvSolution`, cloned from **inviscid** VMFL051, provides `h` and no `e`. VMFL045
is **viscous** (μ = 1e-8), so the implicit viscous energy corrector runs — the path
VMFL051's μ = 0 never took. Proof (supervisor's): `smoothSolver: Solving for Ux` count
— VMFL051 whole run **0**, VMFL045 before death **1**. A setup defect in the frozen
inputs, not a numerical failure. A comparator `--selftest` (45/45) could not catch it —
it proves the **grader**, not the **case**.

## 3. The repair — VMFL045-R2, frozen, NOT launched

Built per the supervisor's instruction and the team's VMFL001 R1→R2 precedent, under
`cases/ansys_verification/VMFL045/R2/`:

- **Exactly one functional change:** the `fvSolution` `solvers` energy key **widened
  `h` → `"(h|e)"`** (a widening, not a bare `e` add — fix the class not the instance,
  L-221/L-222; the supervisor adopted the first lane's repair). `diff -rq` confirms
  R2/case differs from run 1's frozen case **only** in `fvSolution`.
- **Comparator** `grade_vmfl045_r2.py`: byte-identical to run 1's except three path
  constants (RUN_ROOT/OUT_JSON/SELF_REL) retargeting it at R2's tree/file; no threshold,
  band, reference, plant or classifier changed; `--selftest` **45/0**; `--verify-frozen`
  passes. (Cosmetic: its verify-frozen print still says "grade_vmfl045.py" — a hardcoded
  string left unchanged so the file stays a pure 3-constant retarget; flagged, not fixed.)
- **Launcher** `run_vmfl045_r2.sh`: paths retargeted **plus a PRE-FLIGHT SMOKE TEST** —
  a few `rhoCentralFoam` steps on the coarsest mesh in a `mktemp` scratch dir **outside
  `verification/runs/`**, aborting the whole run if it fails. The generalisable fix; it
  never touches the graded run tree. `bash -n` clean.
- **Gate, tolerance, diagnostic bands, three levels, endTime, solver, sampling zones,
  Roache quantity and the 48-core-min cap are ALL UNCHANGED** and listed as unchanged in
  the R2 prereg §2. Carried forward unsoftened: the Fluent-would-fail declaration
  (Fluent 1.902 would `GATE FAIL` at +1.494 %, CFX 1.871 passes at −0.160 %; a
  near-Fluent value is a `GATE FAIL`, not narrated as agreement with Ansys), **p ≈ 1
  expected / p ≈ 2 suspicious**, and §7's plateau mitigation.
- **Frozen:** prereg blob `515004089ec3976e52279239f6a02dcaf1439dcd`, freeze commit
  `4b3f512e`; inputs commit `3467dd25` (comparator `a282f00d`, launcher `2da8a6d8`,
  fvSolution `9010f183`, topoSetDict `ffaeb578` = run 1's, byte-identical). §2b.1
  condition checked 02:06:47Z: R2 run tree absent, 0 files, no solver. **NOT LAUNCHED —
  the supervisor unlocks compute personally.**

## 4. Records committed (each gated; `set -e` is decorative here, so explicit `||exit`)

| commit | what |
|---|---|
| `931ac144` | run-1 crash evidence (L1 logs, `RUN_RC.txt`, `CONTENTION.txt`, `launch.stdout.txt`) — explicit paths (`log.*` gitignored, L-300) |
| `5a927fd4` | `RESULTS.md` — run 1 `NOT A RESULT` / `NOT HELD`, 0.0000 core-min, mechanism, process finding |
| `fb3fd8ad` | register **row #5** (from HEAD; row #4 byte-identical; tally 2 PASS of 4→**5** run, numerator holds; tier inline; #1–#4 addendum untouched) |
| `9164a4d9` | cost-calibration row **C-56** — ratio **UNDEFINED** (run never executed, L-265) |
| `64b02355` | citation fix in my own records: `C-90` → `C-15` (the real W4 O2 re-buy precedent) in the C-56 row and `RESULTS.md` |
| `8c8b18d9` | `CASE_MAP.md` — VMFL045 → `NOT HELD`; **every aggregate moved** (fraction 3→**4** of 73, 70→**69** never run; count table; narrative three→**four**), gated by `append_guards.py` (0794b682) with its selftest re-run in-invocation; counts re-derived 95/73/4/69/10/12. **Also corrected the row's "inviscid" descriptor → "μ=1e-8 (nonzero → viscous path)"** — a false, finding-relevant sentence beside the new "viscous" row; an edit beyond the tier cell, flagged here for your read. |
| `3467dd25` | R2 inputs (12 files) — NO COMPUTE |
| `4b3f512e` | R2 pre-registration FREEZE (separate commit) |

Every commit used the private-index protocol with a path gate, an explicit-`||exit`
gate on each assertion (since `set -e` does not gate here), CAS on the current parent,
and a mandatory post-commit audit. The three ledgers were reconstructed from **fresh
HEAD inside the committing invocation** with CAS retry, so a peer's concurrent append
could not be clobbered or produce a stale base.

## 5. Honesty notes

- **CONTENTION.txt overwrite:** this lane's launch-time `>` inadvertently overwrote the
  first lane's contention samples; recovered from the first lane's committed report
  `f1f58fd`, attributed, in the committed `CONTENTION.txt`. No evidence lost.
- **Run 1's tree is LEFT IN PLACE** as the evidentiary core of the `NOT A RESULT`; R2
  runs in its own fresh directory and the guard keeps protecting run 1.
- **Nothing about Ansys**, nothing about the manual beyond the recorded findings, and
  the run-1 justification borrows **no** triple, order, GCI or plateau number from
  VMFL051 (VMFL045 run 1 has none).

## 6. What I could not verify / awaiting you

R2 is frozen and unrun — the mesh build, the smoke test's pass, `topoSet` filling both
zones on the real R2 tree, plateau at 7e−3 s, the observed order and the gate value are
all still to be measured, whatever they are. **R2 is NOT launched; it needs your compute
unlock.** Cost consumed by this lane: **0.0000 core-min** of solver compute.
