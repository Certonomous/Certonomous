# Resource-dependent tests: a mechanical sweep of the suite after L-62

**Written 2026-08-11. Scope: every test function under `sdk/tests/`.**

L-62 records a suite test that was red for ten days and flipped colour inside
six minutes, because its verdict was a function of the box's spare cores rather
than of the code. This document is the generalisation sweep it asks for: every
other test whose verdict could be reading the neighbours instead of the source.

Nothing here is a fix. No test, source file or guard was modified. Every
measurement was made in a throwaway tree cut with `git archive` from commit
**`75b6ea5e`**, so the source under test is committed source at a named commit,
and the working tree the other agents are live in was never touched.

**The box moved under this sweep, which is the point.** The 1-minute load
average ranged between **10.25 and 1.42** while the measurements ran, as other
agents' jobs drained and arrived — a 7x swing, and a 3x swing *inside a single
suite run*. Every measurement below therefore carries the core count and the
load it was taken under; section 2 is that table. A sweep for load-dependent
verdicts that does not record its own load has the defect it is hunting.

---

## 1. Method, and why it is not an inspection

The confirmed defect lived **three call hops from the assertion** — the test
asserted a list length and never mentioned cores. Reading tests would not have
found it, so this sweep does not read tests to decide. It **instruments the
resource** and then **forces it**.

**Enumeration (mechanical, transitive by construction).** Two runners in the
scratch tree wrap every primitive through which a machine-resource quantity can
enter this codebase, count the calls **per test function**, and record each
test's outcome:

| wrapped | resource it carries |
| --- | --- |
| `chief_engineer.compute_audit._probe` | the single host measurement: cores, MemTotal, MemAvailable, 1-min load, live solver count, scripted-load count |
| `chief_engineer.compute_audit.audit` | the capacity verdict every workflow calls before planning fan-out |
| `os.cpu_count`, `multiprocessing.cpu_count`, `os.sched_getaffinity` | direct core reads, and the default width of every `ThreadPoolExecutor` |
| `subprocess.run` / `Popen` argv matching `nproc`, `/proc/loadavg`, `/proc/meminfo`, `pgrep` | shell-level host peeks |
| `shutil.disk_usage`, `Path.read_text("/proc/meminfo")`, `open("/proc/meminfo")` | free disk and available memory |

A test counts as **resource-touching** if any wrapper fired anywhere inside it,
at any depth. That is what makes the enumeration transitive rather than
lexical: the fleet test that started all this touches `audit` four frames down
and is caught by construction, exactly as it would have been ten days ago.

**Demonstration (the variable is moved, both ways).** The whole suite was then
run end to end at forced extremes on identical committed source, and the
per-test outcomes diffed. Nothing below is an argument that a test is
insensitive; each is a pair of runs.

**Positive control (the instrument is shown to be able to fail).** L-62's rule
is that a test which only ever passes has not been shown to test anything. The
same applies to a sweep. Before trusting any "no difference" result, the
pre-fix assertion from the confirmed defect was replayed against HEAD's
workflow through this rig:

```
[host 03:19:01Z nproc=16 load1=1.91]  forced cores=3
    granted-shape=[0, 1, 0]        pre-fix `len(shape)==3` -> GREEN
[host 03:19:16Z nproc=16 load1=1.63]  forced cores=96
    granted-shape=[0, 94, 9, 0]    pre-fix `len(shape)==3` -> RED
```

The rig reproduces the known defect, and separates the two capacities by 93
slots. A zero-difference result from it therefore means something.

---

## 2. Host conditions at each measurement

`nproc` was **16** at every measurement. The 1-minute load average and
`MemAvailable` at each:

| # | measurement | UTC | load1 | MemAvailable |
| --- | --- | --- | --- | --- |
| 1 | scratch tree created; LOW suite run begins | 03:02 | **10.25** | 28.9 GB |
| 2 | LOW suite run ends (`cores=3`) | 03:08 | — | — |
| 3 | HIGH suite run ends (`cores=96`) | 03:10 | — | — |
| 4 | BASE suite run ends (unforced) | 03:13 | — | — |
| 5 | LOW-repeat suite run ends (`cores=3`) | 03:16 | — | — |
| 6 | host re-stamped | 03:18:05 | **3.74** | 28.8 GB |
| 7 | positive control, forced 3 cores | 03:19:01 | 1.91 | 29.1 GB |
| 8 | positive control, forced 96 cores | 03:19:16 | 1.63 | 28.8 GB |
| 9 | A-1 disk/memory bracket, six forced points | 03:19:30–31 | 1.42 | 29.0 GB |
| 10 | process-table forcing, real `ps` | 03:19:50 | 4.33 | — |
| 11 | process-table forcing, shimmed `ps` | 03:20:13 | 3.28 | — |
| 12 | emitted-page probe | 03:20:47 | 4.43 | — |
| 13 | **BASE re-run**, unforced, 11 samples | 03:24:20–03:27:03 | **3.57–10.05**, mean 6.01 | 28.7–29.0 GB |
| 14 | **LOW re-run** (`cores=3`), 19 samples | 03:27:03–03:32:39 | **3.68–5.23**, mean 4.53 | 28.0–29.0 GB |
| 15 | **HIGH re-run** (`cores=96`), 9 samples | 03:32:39–03:34:54 | **3.82–13.13**, mean 9.64 | 28.4–29.0 GB |
| 16 | A-1 repair verification | 03:34:40 | 12.88 | — |

Rows 1–5 carry endpoint load only. The first four suite runs were made before
the runner sampled its own host, and that was a defect in this sweep's method
rather than something to paper over: a sweep hunting load-dependent verdicts
that does not record its own load is the thing it is hunting. It was repaired by
adding a 20-second host sampler — reading `/proc/loadavg` and `/proc/meminfo`
through the **unpatched** primitives — and **re-running BASE, LOW and HIGH under
it** (rows 13–15).

The drift turned out to be free evidence rather than a problem, and it is the
strongest evidence in this document:

* The **BASE runs are unforced** — they take whatever capacity the box offers.
  Row 13 ran across a **3x load swing inside a single run** (3.57 to 10.05), so
  its own `audit()` capacity moved while the suite was executing.
* Row 15 ran at mean load 9.64 peaking at **13.13 of 16 cores** — the busiest
  moment of the whole sweep — while row 14 ran at mean 4.53. Same source, same
  forced setting, neighbours differing by more than 2x.
* The original LOW run (row 1–2) executed at load ~10; its stamped repeat (row
  14) at ~4.5.

Every one of those produced identical verdicts, which is reported in section 10.

Forced capacities used throughout:

| run | forced | resulting `audit().capacity` |
| --- | --- | --- |
| LOW | `cores=3`, MemAvailable 2 GB | **1** |
| HIGH | `cores=96`, MemAvailable 256 GB | **94** |
| BASE | nothing | whatever the box offered (~4 at load 10, ~11 at load 3) |
| DISK/MEM HIGH | free disk 500 GB, MemAvailable 64 GB | every guard clears |
| DISK/MEM LOW | free disk 5 GB, MemAvailable 1 GB | every guard trips |

---

## 3. The denominator

**The sweep measured exactly one commit: `75b6ea5e` (03:02:05 UTC), which was
HEAD when the scratch tree was cut.** That is stated rather than assumed: the
swept tree was diffed file-by-file against `git archive 75b6ea5e` over
`sdk/tests`, `sdk/workflows`, `sdk/chief_engineer` and `scripts`, and the only
difference is the `__pycache__` the runs themselves generated.

| quantity | count |
| --- | --- |
| test files under `sdk/tests/` | 56 (plus `__init__.py`) |
| test functions defined at `75b6ea5e` | **1300** |
| test functions **executed and scored** | **1300** |
| test functions examined for resource dependence | **1300 — 100%, no gap** |
| resource-touching (any wrapper fired, any depth) | **73** by core/capacity, **1** by disk/memory |
| additionally identified as resource-reading-and-pinned | **20** |

Every defined test ran; the defined set and the executed set were reconciled by
AST and are identical, with no residue in either direction. A test is "clean"
here because no wrapper fired inside it at any depth during a real run, which is
a stronger statement than a grep produces.

**The tree moved while this sweep ran, and the denominator is pinned against
that on purpose.** Between the archive at 03:02 and this document at 03:27, HEAD
advanced eight commits to `ba5a8cbc`. One of them (`ba5a8cbc`, 03:25:59) added
**22 test functions** to `sdk/tests/test_rank_claim_surfaces.py`, taking it from
13 to 35; and `sdk/tests/test_head_engineer.py` carries a further **9**
uncommitted test functions in the working tree. Those 31 are outside this
sweep — they did not exist in the committed source it measured. Section 12 says
what that costs.

---

## 4. The three-way classification

| class | meaning | count |
| --- | --- | --- |
| **(a) verdict-changing** | a different machine reading produces a different pass/fail | **1** |
| **(b) resource-reading but pinned** | forces or mocks the quantity, so the verdict is invariant by construction | **20** |
| **(c) reads a resource, assertion insensitive** | an unpinned host reading reaches the code under test; the verdict does not move | **74** |
| not resource-touching | no wrapper fired at any depth, no seam pinned | 1205 |

Class (c) is 72 tests caught by the core/capacity wrappers, plus the two
`test_morning_report_emitter` command-line tests, which the wrappers could not
see (section 8) and which were forced separately.

---

## 5. Class (a): the finding

### A-1. `test_mega_batch.LedgerTests.test_run_batch_valve_only_resumes`

**File:** `sdk/tests/test_mega_batch.py:87`, assertion at `:102`.
**Verdict is a function of:** free disk on the filesystem holding the temp
directory, and `/proc/meminfo` `MemAvailable`. Neither word appears in the test.

It is the **only test in the suite that reads either quantity.** The disk/memory
instrumentation fired in exactly one of 1300 tests, four times each:

```
test_run_batch_valve_only_resumes  {'/proc/meminfo': 4, 'shutil.disk_usage': 4}
```

The dependence is four hops down, the shape L-62 describes:

```
test_run_batch_valve_only_resumes        sdk/tests/test_mega_batch.py:100
  -> mega_batch.run_batch(...)           sdk/workflows/mega_batch.py:912
     -> should_stop()                    sdk/workflows/mega_batch.py:982
        -> resource_guard_tripped()      sdk/workflows/mega_batch.py:959
           -> free_disk_gb(work_root)    sdk/workflows/mega_batch.py:888 -> shutil.disk_usage
           -> available_mem_gb()         sdk/workflows/mega_batch.py:893 -> /proc/meminfo
```

`run_batch`'s defaults are `min_free_disk_gb=20.0` and `min_avail_mem_gb=2.0`.
The guard is evaluated before the first submission — `guard_state["last_check"]`
starts at `0.0`, so the `RESOURCE_CHECK_SECONDS` throttle cannot suppress the
first check — and it **latches**: once tripped the session stops for good. The
test overrides neither floor, so on a box below either one the batch submits
**zero** tasks and `assertEqual(len(first), 4)` reads `0 != 4`.

**Forced evidence, identical committed source, all six points taken at
`nproc=16, load1=1.42, MemAvailable 29.0 GB` (03:19:30–31Z):**

| forced free disk | forced MemAvailable | verdict |
| --- | --- | --- |
| 500 GB | 64 GB | **PASS** — 14/14 green |
| 20.1 GB | 64 GB | **PASS** |
| **19.9 GB** | 64 GB | **FAIL** — `AssertionError: 0 != 4` |
| 500 GB | **2.1 GB** | **PASS** |
| 500 GB | **1.9 GB** | **FAIL** — `AssertionError: 0 != 4` |
| 5 GB | 1 GB | **FAIL** — `AssertionError: 0 != 4` |

The flip is bracketed to a tenth of a gigabyte on each axis independently, and
each threshold is exactly the workflow's own guard floor. This is not a boundary
chosen to make a point; it is the code stating where its verdict changes.

**Why it is green today, and why that is not reassuring.** This box currently
holds 345 GB free and ~29 GB MemAvailable, so the guard clears with room. But
`mega_batch.py:876-884` records the incident the guard exists for: *"committed
memory at 112.90% of RAM ... the box livelocked in reclaim before the OOM killer
could act"*, with two DAFoam adjoint containers and a batch sharing 30 GB. On a
box where that is possible, `MemAvailable < 2 GB` is possible; and on the day it
happens this test goes red **and its red will be a true statement about the
machine and a false one about `load_done_indices` and the resume logic it was
written to protect.** That is L-62 with the resource swapped from cores to
memory, and it will cost the same day of reading the wrong file.

**Recommended repair — a strengthening, not a loosening.** Do not delete the
`4` and the `7`; do not raise the floors; do not mock `shutil.disk_usage`.

**The quantity to pin to already exists and the test already throws it away.**
`run_batch` returns `stats["guard_trip"]` — `None`, or the reason string naming
which floor fired (`mega_batch.py:1047`) — and the test calls `run_batch(...)`
purely for effect, discarding the return value on both lines. The run states its
own stop reason; nobody reads it. So:

1. pass `min_free_disk_gb=0.0, min_avail_mem_gb=0.0` from this test, so the host
   cannot decide the verdict — the floors are already parameters and this test
   is already the caller;
2. bind the return value and assert `stats["guard_trip"] is None` and
   `stats["session_completed"] == 4` beside the existing counts. The asserted
   quantity becomes *"every task this session asked for was submitted, and the
   run says it stopped for the reason the test gave it"* — pinned to what the run
   states about itself rather than to the box;
3. add a second test that forces the floors *high* and asserts the batch stops
   **and names the guard** in `stats["guard_trip"]`.

Point 3 is what makes this a strengthening rather than a loosening: the guard's
firing path has never once been exercised by a test. Today the only thing that
has ever executed it is the host, silently, as a side effect — which is why the
day it fires, it will look like a bug in the resume logic.

**The recommendation was run, not just written** (03:34:40Z, nproc 16,
load1 12.88 — the box had gone busy again). Steps 1 and 2 were applied in a
scratch script against the same forced readings, and the existing count
assertion was kept exactly as it is:

| forced host reading | as written today | as recommended |
| --- | --- | --- |
| disk 500 GB, mem 64 GB | completed 4, `guard_trip=None` → **passes** | completed 4, `guard_trip=None` → **passes**, and `assertIsNone` passes |
| disk 5 GB, mem 1 GB | completed 0, `guard_trip='free disk 5.0 GB below the 20.0 GB floor'` → **fails** | completed 4, `guard_trip=None` → **passes** |
| disk 0.5 GB, mem 0.1 GB | completed 0, same trip → **fails** | completed 4, `guard_trip=None` → **passes** |

So the repair holds at a host reading two orders of magnitude below the floor,
keeps every existing assertion, and adds one. It is not a loosening: the `4` and
the `7` stay, and the new `assertIsNone(stats["guard_trip"])` would fail on any
future change that let the guard fire in a run this test believes is clean.

---

## 6. Class (b): resource-reading and correctly pinned — the pattern to copy

Twenty tests read a resource quantity and force it. A correct one is worth
recording as the pattern to copy, and two of these are better than merely
correct.

| test / fixture | tests | what it pins | how |
| --- | --- | --- | --- |
| `test_aircraft_optimization.ShootRoundTests.test_the_fleet_comes_up_once_and_goes_down_once` | 1 | `compute_audit._probe` | `mock.patch.object`, run at **both** 8 and 24 cores in a `subTest` loop, so neither fleet shape can hide behind a loaded box. The repaired defect, and the best example in the tree. |
| `test_shape_optimization.ActRegisterTests` via `_run_act` (`:145`) and `_Capacity` (`:105`) | 4 | `workflows.shape_optimization.audit` | replaced wholesale; both `fits=True` and `fits=False` branches exercised from `setUpClass` |
| `test_agenda.AgendaEndpoints`, three approve tests | 3 | `server._agenda_audit` | both CONSTRAINED and FITS covered |
| `test_orchestration_stack.ComputeAuditTests._audit` (`:32`) | 2 | the whole `ComputeAudit` record | constructed field by field, so headline and panel wording are asserted against fixed numbers |
| `test_worker_recovery._fleet` (`:33`), `WorkerRecoveryTests` only | 2 | pool width | `ApiFleet(..., max_workers=4)` with `plan.worker_count` fixed; `slots = min(len(tasks), worker_count, max_workers)` can never see the host. Its sibling `ShapeOptimizationSweepRecoveryTests` calls `_solve_slot` directly and sizes no pool at all. |
| `test_morning_report_emitter.build` (`:40`) | 8 | the **live process table** | `def build(scan=lambda: [])` — the default argument displaces `_scan_processes`, which would otherwise `ps -eo args` the whole box |

**The two best are the ones where the seam is in production code, not in the
test.** `server._agenda_audit` (`server.py:706`) carries the docstring
*"Module-level so tests can pin the verdict; production always measures the real
machine"*, and `build_morning_report(..., scan=_scan_processes)` takes the host
reading as a parameter. A test pinning through a declared seam does not have to
reach into internals and does not break when internals move. Any repair
proposed in this document should prefer that shape.

One note on naming, because it misled me for twenty minutes:
`test_a_live_process_scan_lands_on_the_left_running_line` reads as though it
scans the live box. It does not — it passes a synthetic one-line table, and its
sibling assertions go through `build()`'s pinned empty scan. The test is honest;
its name is the thing that is load-bearing and wrong.

---

## 7. Class (c): touches a resource, verdict does not move — demonstrated

Seventy-four tests let a real, unpinned host reading reach the code under test.

| file | touching tests | how the resource enters |
| --- | --- | --- |
| `test_aircraft_optimization.py` | 41 | `main()` → `audit(min(12, len(grid)), memory_per_worker_mb=128)` at `aircraft_optimization.py:1740`; `granted` then caps the screening fan-out and the finalist pool. (42 touch the audit; the 42nd is the repaired fleet test, which pins it — class (b).) |
| `test_valve.py` | 15 | `main()` → `audit(min(12, n_solves), ...)` at `valve_study.py:268`; `granted = min(capacity.capacity, n_solves)` at `:303` |
| `test_race_study.py` | 14 | `audit(MAX_WORKERS, ...)` at `race_study.py:560` — headline and panel only; the value gates nothing |
| `test_sobol_mission.py` | 1 | `audit(2, ...)` at `sobol_sensitivity.py:541` |
| `test_pce_surrogate.py` | 1 | `os.cpu_count()` from inside the numerical stack, not from lab code |
| `test_morning_report_emitter.py` | 2 | the CLI path runs `morning_report.py --emit`, whose default scan reads the real process table |

### The demonstration

All 1300 tests, run end to end at each forced extreme on identical committed
source:

**Nine full-suite runs, 1300 tests each — 11,700 scored outcomes.** All diffs
are stated against the first LOW run as the reference:

| run | forced | host load1 during the run | diffs vs LOW |
| --- | --- | --- | --- |
| LOW | capacity 1 | ~10 (endpoint) | — reference |
| HIGH | capacity 94 | ~10 → ~4 | **0** |
| BASE | unforced | ~10 → ~4 | **0** |
| LOW-repeat | capacity 1 | ~4 | **0** |
| BASE re-run | unforced | 3.57–10.05 | **0** |
| LOW re-run | capacity 1 | 3.68–5.23 | **0** |
| HIGH re-run | capacity 94 | 3.82–13.13 | **0** |
| DISK/MEM HIGH | disk 500 GB, mem 64 GB | — | **0** |
| DISK/MEM LOW | disk 5 GB, mem 1 GB | — | **1** — A-1 only |

**One outcome difference in 11,700, and it is A-1.** The capacity was moved by a
factor of 94, the host load by a factor of 3.7 across runs and by 3x *within* a
single run, and nothing else in the suite noticed.

The same 73 tests touched a resource in every core run: no test read a resource
at one capacity and not at the other, so the enumeration is not itself
capacity-dependent.

For the two emitter CLI tests, which no in-process wrapper can see, the process
table itself was forced by putting a `ps` shim on `PATH` — this crosses the
process boundary, which patching cannot:

| forced process table | verdict |
| --- | --- |
| real `ps`, quiet box (03:19:50Z, load1 4.33) | **PASS** |
| shimmed: 3 solver-shaped neighbours — `mpirun`, `snappyHexMesh`, `vspaero` (03:20:13Z, load1 3.28) | **PASS** |
| shimmed: solver line containing an em dash and a literal `PENDING:` token | **PASS** — all 10 emitter tests green |

### Why they survive, structurally

The pattern that saves them is worth naming, because it is what a new test
should copy: **in every one of these workflows the capacity sizes the pool,
never the work.** The airliner screens the whole grid whichever slot each point
lands on (`slot = idx % n_slots`, `aircraft_optimization.py:1829`); the finalist
table has nine rows because there are nine finalists, not because nine slots
were granted. The valve emits one dispatch pair per candidate angle, not per
slot. A test asserting the size of the *work* is invariant. A test asserting the
size of the *fleet* — which is exactly what the confirmed defect did — is not.

---

## 8. Where this instrument is blind, and what was done about it

The wrappers are in-process. **A resource read inside a child process is
invisible to them.** Nine test files spawn children:

| file | what the child does | resource risk | how covered |
| --- | --- | --- | --- |
| `test_morning_report_emitter.py` | `morning_report.py --emit` | **reads the live process table** | forced via `PATH` shim, three states, all green (section 7) |
| `test_control_room_pacing/_cp_ramp/_typesetting.py` | `node` harness over recorded fixtures | wall-clock only | timing measured, section 10 N-4 |
| `test_agenda.py` | `node` script parse | none | inspected |
| `test_exec_bits.py` | `git ls-files` | none | inspected |
| `test_lever_echo.py` | fake solver launcher, then `ps -o args -p <pid>` | live process table for one PID | section 10 N-3 |
| `test_head_engineer.py`, `test_vspaero.py`, `test_geometry_study.py` | `_wsl` / solver runner, mocked in tests | none | inspected |

Two further limits of the instrument, stated so the numbers are not read as
stronger than they are: `ps` was **not** in the shell-argv marker list, which is
why the emitter's live scan had to be found by reading rather than by the
wrapper; and the `git archive` tree cannot carry untracked working data, which
is what section 9 is about.

---

## 9. Assertions stronger than their own stated contract

L-62's second lesson is that the confirmed defect was not a wrong test but one
that over-reached its comment by one quantifier, and that the gap stays
invisible until the environment moves. Three such gaps survive in the
resource-touching set. None changes a verdict today — but neither did the
confirmed one, until the box got quiet.

**O-1. `test_mega_batch.py:88` — the comment claims an independence the
assertion does not have.** The comment reads *"Force a valve-only stream so the
batch needs no external solver."* The contract it states is independence from
external machinery. The assertion at `:102` additionally requires the host to
hold more than 20 GB of free disk and more than 2 GB of available memory. The
comment says what was pinned and is silent on what was left live. This is the
same shape as the confirmed defect — a sentence stating a weaker claim directly
above an assertion making a stronger one — and it sits on the one class (a) test
in the suite. That is not a coincidence: the comment is why nobody looked.

**O-2. `test_aircraft_optimization.py:143-144` — "are fed" versus "more than
20".** The comment reads *"The dispatch panel and the live trace are fed as the
grid is screened."* "Fed" claims the count is non-zero. The assertion is
`assertGreater(events.get("dispatch.update", 0), 20)`. The 20 is a bare literal
with no stated derivation; the quantity it stands for is `2 * len(grid)`, which
the workflow computes. It is invariant today only because the grid size is fixed
in code — it is pinned to a constant rather than to the run, which is precisely
the property L-62's repair replaced. **Recommended:** assert against
`2 * len(grid)`, or against the grid size the run emits, so the numeral tracks
the sweep it describes.

**O-3. `test_aircraft_optimization.py:823` — `assertEqual(len(rows), 9)` under
the comment `# one row per finalist solve`.** The comment states a *relation*;
the assertion states a *literal*. The finalist count and the pool width
`min(granted, 9)` are two different quantities that happen to share the numeral
9. They were confirmed independent here — at forced capacity 1 the table still
carries nine rows — but a reader comparing the two numerals cannot tell which 9
is which, and a change to either would fail this test for a reason its comment
does not name. **Recommended:** assert against the workflow's own finalist
constant.

Recorded as the correct version of O-2: `test_valve.py:115-116` carries *"the
dispatch panel and the live objective trace are fed"* above
`assertGreaterEqual(events.get("dispatch.update", 0), 2 * n)`. The assertion is
stronger than the comment, but `n` is `len(CANDIDATE_ANGLES)`, read from the code
under test. It is already pinned to the run and needs no change.

---

## 10. Is the suite's pass/fail reproducible on this box while other agents run?

**Direct answer: yes for 1299 of 1300 tests, measured rather than argued; and
the exception is A-1, whose resource is memory and disk rather than cores.**

**Nine** full-suite runs on identical committed source (`75b6ea5e`), on a
16-core box carrying other agents throughout, spanning load 1.42 to 13.13 —
including two runs whose own load swung by 3x while they executed. Eight of the
nine produced **the identical outcome for every one of the 1300 tests**; the
ninth differed by A-1 alone, and only because disk and memory were forced below
the workflow's floors.

That is the answer, and it is a measurement rather than an argument: **the
suite's colour is currently reproducible under concurrent load.** The runs that
matter most for the question are the unforced ones, because those are what an
agent actually gets when it types the test command — and the unforced run that
straddled a 3x load swing agreed test-for-test with a run pinned to a single
slot and with a run pinned to 94.

The eleven non-passes are `git archive` artifacts, not flakes. They are tests
that read the working tree's untracked data (`chief-engineer-runs/`, the solver
archives) or shell out to `git`, neither of which a `git archive` export
carries. Two were re-checked inside the real repository:
`test_control_room_cp_ramp` and all ten `test_morning_report_emitter` tests pass
there, and `test_exec_bits` fails there for a live unrelated reason — a
shebang-bearing script another agent has in flight
(`demo-output/website/dafoam/f6d_random_matrix_uq/run_option_a_queue.sh`, no exec
bit, not in the waiver register) — which is a real finding for its owner and
nothing to do with machine resources.

So the answer has two halves, and the second is the one that matters:

* **Core count and load do not currently move the suite's colour.** That is a
  measured result over 11,700 scored outcomes, across a 93-slot capacity spread
  and a 9x load range, with a positive control proving the rig would have caught
  it if they did.
* **Free disk and available memory do**, through exactly one test, and its
  threshold is a floor this lab has already crossed once — the incident is
  written into the source file that carries the guard. Until A-1 is pinned, a
  red suite on a memory-starved box is ambiguous in precisely the way L-62
  names, and somebody will spend the day reading `load_done_indices`.

One reservation about coverage rather than colour follows as N-1.

---

## 11. Found while looking for something else

**N-1. A verdict-invariant test whose *branch* coverage is decided by the
neighbours.** `test_aircraft_optimization.WorkflowTests.test_worker_cap_and_time_budget_are_on_the_record`
(`:216`) is a model class (c) test: it asserts a *relation*
(`Taken + Held back == Available`, and the narration may not contradict the
table under it) rather than a count, and its comment records that it used to
assert `Held back > 0` and failed on any box busy enough to audit at capacity 1.
The relation is invariant — confirmed at capacity 1 and 94. But the test then
branches on `counts["Held back"] > 0`, and **which arm executes is chosen by the
box**: at capacity 1 only "no headroom to leave" is checked, at capacity 94 only
"not taking every worker". On this box under normal agent load, one of the two
narration arms is never executed, and nothing reports that. The verdict is
honest; the coverage is a measurement of the neighbours. The repair is the one
the fleet test already received: force both capacities in a `subTest` loop so
both arms run on every box.

**N-2. Two live-memory gates that no test reaches at all.**
`docker_dafoam.wait_for_headroom` (`:64`) polls `/proc/meminfo` and **blocks up
to 1800 seconds** waiting for 6 GB of headroom. It is called from
`onera_m6.py:447,504` and `crm_wingbody.py:201,260`. No test executes it — those
workflows sit behind `docker_available()`, false here. If docker ever becomes
available on a test box, a memory-starved run converts four workflow entries
into a half-hour stall inside the suite. Not a current defect; an unexercised
path whose failure mode is a **hang rather than a red**, which is strictly worse
to diagnose than the thing this sweep was hunting.

**N-3. `test_lever_echo.py:847` reads the live process table for PID reuse.**
`ps -o args= -p <pid>` against a PID the test has just launched, asserting the
wrapper name is absent. If the PID has already exited, `ps` returns nothing and
the assertion passes vacuously; if the PID were recycled onto an unrelated
process it would also pass. Not capacity-sensitive, but a test that can only
fail by accident, and it passed at both forced capacities for reasons unrelated
to what it means to check.

**N-4. The wall-clock margins are wide, and this was measured rather than
assumed.** The `node`-harness tests carry `subprocess.run(..., timeout=180)` and
`timeout=600`. Under full agent load all five complete in **1.3 seconds** — a
130x to 450x slowdown would be needed to turn a timeout into a red. The harness
itself steps a **virtual** clock, so the timing claims inside it are not
wall-clock claims at all. This is the only wall-clock family in the suite.

**N-5. Three environment-gated skip families change the suite's shape without
saying so.** `shutil.which("node")` guards seven tests; `AUDIT_LOGS.exists()`
and four `test_log_signatures` archive checks guard five more. On a box without
node, twelve tests silently vanish from the total. This is tool presence, not
machine capacity, so it is outside this sweep's scope — but a suite count means
a different thing on two boxes and no line of run output says which.

**N-7. A suite count in a commit message can include tests that are not in the
commit.** Reconciling this sweep's denominator turned up a small instance worth
naming. The fix commit for L-62 records *"Suite 1309 passed"*; the committed
source at `75b6ea5e` defines **1300** test functions. The nine-test difference
is `sdk/tests/test_head_engineer.py`, which carries +130 uncommitted lines in the
working tree — so the count that went into the permanent record was measured on
a tree nobody else can reproduce, and a reader checking out that commit and
running the suite will get a different number with nothing wrong. Not a defect
in any test; a reminder that a number quoted as evidence should say what it was
measured on. This document states its commit for that reason.

**N-6. A probe that found nothing, recorded because a negative result from a
forced variable is worth more than an untested assumption.** I suspected that a
neighbour's command line could reach the emitted morning-report page and trip
the house dash rule, since the em-dash test runs only on the pinned path while
the CLI test runs on the live one. Forced with a shimmed `ps` emitting
`--tag run—alpha`, the page came back reading `run-alpha`: every scanned command
line goes through `_cell()` (`morning_report.py:300`), which applies
`_typography()` before the string reaches the page. The guard is in the builder,
not only in the pinned test. No defect — but it was worth forcing rather than
assuming, because the one test that checks for dashes never sees this input.

---

## 12. What I could not establish

* **Thirty-one test functions that exist now were never swept, because they did
  not exist at `75b6ea5e`.** Twenty-two landed in
  `sdk/tests/test_rank_claim_surfaces.py` at 03:25:59 (commit `ba5a8cbc`), and
  nine are uncommitted in `sdk/tests/test_head_engineer.py`. Both files belong to
  other live agents and both are on this task's do-not-touch list. **This is the
  standing cost of sweeping a repository that eight agents are committing to:
  any statement of the form "the suite has one resource-dependent test" is true
  of a commit, not of a moment.** The 13 rank-claim tests that existed at
  `75b6ea5e` *were* inside the 1300 and produced identical outcomes at every
  forced capacity, so they are covered even though the file was never opened.
* **The other excluded paths were not read at all**: `scripts/self_audit.py`,
  `scripts/audit_transcripts.sh` and `W2_sparta_runs/`.
* **Memory and disk pressure were forced by substitution, not by exhaustion.**
  A-1's flip was produced by replacing `free_disk_gb` and `available_mem_gb`, not
  by genuinely filling the disk or the RAM. That is the right instrument on a
  shared box — actually starving this machine would take down the neighbours —
  but the claim is therefore "the guard trips and the test goes red when the
  reading is low", not "the reading has been observed low on this box".
* **`test_pce_surrogate`'s `os.cpu_count` read was not traced to its caller.** It
  fires inside the numerical stack rather than in lab code. Its verdict is
  identical at 3 and 96 cores, which is what this sweep needs, but I did not
  establish which library reads it or whether a different BLAS thread count could
  perturb the lengthscale ratio it asserts.
* **Nothing was established about load heavier than this box carried today.**
  Load ran between 10.25 and 1.42 of 16 cores. The margins in N-4 look ample, but
  a measurement taken today is a measurement of today.

---

## 13. Ranked

| rank | item | class | why here |
| --- | --- | --- | --- |
| 1 | **A-1** `test_run_batch_valve_only_resumes` | (a) | the only test in the suite whose colour a machine reading can flip; bracketed to 0.1 GB on both axes; the incident its guard exists for is recorded in the same source file |
| 2 | **O-1** the comment sitting above A-1 | over-reach | the same one-quantifier gap L-62 numbers, on the same test — and the reason nobody looked |
| 3 | **N-1** headroom-narration branch coverage | (c) + coverage | verdict honest, coverage chosen by the neighbours; one `subTest` loop from complete |
| 4 | **O-2** `dispatch.update > 20` | over-reach | a bare literal standing in for a quantity the run computes |
| 5 | **O-3** `len(rows) == 9` | over-reach | two quantities sharing a numeral; comment names the relation, assertion names the literal |
| 6 | **N-2** `wait_for_headroom` unexercised | latent | fails as a 30-minute hang rather than a red |
| 7 | **N-5 / N-7** node-gated skips, and a suite count that included uncommitted tests | shape | a passed-count is not the same sentence on two boxes, or on two trees at the same commit |
| 8 | **N-3** PID-reuse `ps` read | weak | can only fail by accident |

---

## Appendix. Reproducing this

Everything ran from a scratch `git archive HEAD | tar -x` tree. The runners live
only in that tree and are deliberately **not** committed: they monkey-patch
`os`, `subprocess` and `shutil` at import time, which is acceptable in a
throwaway measurement harness and is not a thing that should be importable from
this repository.

```
git archive HEAD | tar -x -C $SCRATCH/tree
cd $SCRATCH/tree/sdk
python _sweep_runner.py       3 2048   low.json      # capacity 1
python _sweep_runner.py      96 262144 high.json     # capacity 94
python _sweep_runner.py       0 0      base.json     # observe only, force nothing
python _sweep_runner_mem.py 500 64     memhigh.json  # every guard clears
python _sweep_runner_mem.py   5  1     memlow.json   # every guard trips
python _control_prefix_assertion.py  3   # positive control -> GREEN
python _control_prefix_assertion.py 96   # positive control -> RED
```

`_sweep_runner.py` samples `/proc/loadavg` and `/proc/meminfo` every 20 seconds
through the **unpatched** primitives and writes the samples into its output
JSON, so every run states the box it ran on.
