# F12 attempt 2, rung 2 (medium) — LAUNCH ATTEMPTED, REFUSED BY THE INSTRUMENT

**Verdict: `BLOCKED`.** Rung 2 did not fire. No solver started, no registered run
directory was created, and no gate was read. Lane report, cfd team, 2026-08-25.

Authority for the attempt: `verification/campaign/F12_GATE_B_RULING_2026-08-25.md`
§5 ruling 1 — *"Rung 2 (medium) FIRES"* — read in full before any action. That
ruling authorises rung 2 **and only rung 2**; rungs 3-5 were not launched and not
staged, and their absence is asserted below both before and after.

---

## 1. THE BLOCKER, STATED FIRST

`launch_f12_rung.py` **refuses rung 2 itself.** Its `rate_calibration_gate()`
interlock (line 381) is a conjunction over rung 1's outcome, and rung 1 aborted
with `rc = 134`. The refusal, emitted by the launcher unmodified:

> `ABORT: rung 'attempt2_medium_workshop_M0.734_a2.79' is CLOSED. The`
> `rate-calibration rung 'attempt2_coarse_workshop_M0.734_a2.79' has not SUCCEEDED`

with three conjuncts failing: `rc = 134, not 0`; `completion limbs FAILED:
['End_line_present', 'ExecutionTime_count_equals_endTime',
'age_guard_all_fields_newer_than_0_T', 'fields_present_at_endTime',
'last_time_equals_endTime', 'rc_is_zero']`; and `the rate-calibration rung is not
complete`. Captured stderr, 457 bytes. Rung 1's own artifacts corroborate directly:
`attempt2_coarse_workshop_M0.734_a2.79/RC.txt` holds `134`, and its `grade.json`
has `complete: false` with all six strict-completion limbs `false`.

**This is not a defect and it was not worked around.** The interlock was closed on
a conjunction deliberately, by this team, as a self-reported correction after the
earlier version opened on a crashed rung (launcher docstring, amendment item 1).
It carries its own negative control planting `rc = 134`. It is behaving exactly as
designed. The launcher's own `--selftest` asserts the same outcome in terms:
*"THE REAL rung 1 (rc = 134) -> rungs 2-5 REFUSED"* (line ~939).

**Opening rung 2 requires changing bytes of `launch_f12_rung.py`.** Per the
supervisor's standing instruction and `SUPERVISION_CHARTER.md` §3 check 1, a change
to a launch/measurement instrument needs the supervisor's personal diff read before
its output is believed. **No such change was made and no modified launcher was run.**
The decision is referred up. Note the tension the supervisor must resolve: the
ruling of 2026-08-25 authorises rung 2, while the frozen §5 of the pre-registration
— *"That measured rate then replaces both estimates before rungs 2-5 are
considered"* — is what the interlock encodes, and rung 1 never produced a
successful rate. Whether the ruling supersedes that ordering is a supervisor call,
not a lane call.

## 2. GRADING PATH PINNED BY HASH — standing rule 2, done before anything else

Both instruments hash-MATCH their HEAD blob. HEAD = `81182ebfffe9ea1ddcfde8976a5f0b7a6b3b2921`.

| Path | HEAD blob | Disk `git hash-object` | |
|---|---|---|---|
| `verification/campaign/F12_PREREGISTRATION.md` | `462492a82b6cf848eaaff25661ded45e623e723f` | `462492a82b6cf848eaaff25661ded45e623e723f` | **MATCH** |
| `.../mesh_ladder_attempt2_2026-08-25/launch_f12_rung.py` | `8233c379e188e4c0baa6bf11f2f54f076592fb43` | `8233c379e188e4c0baa6bf11f2f54f076592fb43` | **MATCH** |

Re-verified byte-identical AFTER all work on this lane. Not one byte of either file
was altered.

## 3. RUNGS 3, 4 AND 5 — ABSENT BEFORE AND AFTER

Asserted against the registered directory names in `RUNGS` (launcher line 198):

| Rung | Directory | Before | After |
|---|---|---|---|
| 2 | `attempt2_medium_workshop_M0.734_a2.79` | ABSENT | ABSENT |
| 3 | `attempt2_fine_workshop_M0.734_a2.79` | ABSENT | ABSENT |
| 4 | `attempt2_medium_tape_M0.730_a2.79` | ABSENT | ABSENT |
| 5 | `attempt2_medium_farfield2x_M0.734_a2.79` | ABSENT | ABSENT |

The refusal fires before `compose_case()`, so nothing was created and nothing was
removed. `verification/runs/F12_runs/` holds the same ten entries after as before.

## 4. GATE A, MEDIUM LEVEL — recorded from existing evidence, mesh NOT rebuilt

From `RESULTS_GATE_A.md:20`: medium = 92,160 cells, **max non-orthogonality
51.5250 deg**, **max skewness 18.475 deg**, **faces > 70 deg = 0**, **`PASS`**.
Consistent with the ruling's quoted 51.53 for the medium level. The mesh was not
rebuilt and no mesh artifact was touched.

## 5. THE BINDING INSTRUMENT CONDITION — §3 of the ruling — SATISFIED AND CONTROLLED

New reader: **`first_solve_residuals.py`**, in this directory. It takes the FIRST
`Solving for <field>` of each `Time =` block, which is what `simpleControl` reads.
It holds no threshold, no gate arithmetic and no verdict; it is a reader, not a
grading path, and it does not modify or wrap the pinned launcher.

**The condition's premise is confirmed on F12's own mesh, measured not recalled.**
`attempt2_coarse_workshop_M0.734_a2.79/system/fvSolution:36` reads
`nNonOrthogonalCorrectors 1` — **two** `p` solves per iteration, matching ruling §2,
not F2's three. At `Time = 6` in that run's log the first `p` is **2.199858e-02**
and the tail `p` is **9.241520e-04**: a **23.8x** within-iteration spread. A
tail-read is a materially different number, on this mesh, at this corrector count.

**Planted control (standing rule 3): 5/5, with the discrimination arm firing.**
Two distinguishable values were planted into a copy of a real log — `1.234e-03` at
the FIRST `p` position, `5.678e-09` at the LAST:

1. POSITIVE — the reader returns `1.234e-03`, the FIRST plant. **PASS**
2. NEGATIVE — the reader does **not** return `5.678e-09`. **PASS**
3. DISCRIMINATION — a deliberately-wrong tail reader over the *same* planted copy
   returns `5.678e-09`, proving the plant landed and the two positions are really
   distinguishable. **PASS** *(without this arm a passing reader is not evidence —
   it could be right by accident of a plant that never landed.)*
4. The two plants differ at all. **PASS**
5. On the UNPLANTED log the two series actually diverge: **147 of 148 iterations**.
   The distinction is not cosmetic. **PASS**

Reproduce: `python3 first_solve_residuals.py --selftest <log>` — exit 0 only if all
five fire. **If any arm fails the reader is refused and its numbers are not evidence.**

## 6. THE MEASUREMENT THE RUNG EXISTED TO MAKE — STILL `PENDING`

Where first-solve `p` floors **on a stable run** is **not measured**, because no
stable run exists and rung 2 did not fire. The ruling's §5.1 statement that this
quantity is unmeasured **still stands unchanged.**

What *is* now in hand is the validated reader applied to rung 1's truncated log —
`rung1_first_solve_reference.json`, 148 iterations of a run that aborted `rc = 134`.
**These are NOT the ruling's measurement and must not be quoted as it:** the run is
unstable, truncated at 148 of 6,000 iterations, and its `p` never began a descent.

| channel | first-solve floor | at iteration | last value | median q4 / median q3 |
|---|---|---|---|---|
| `p` | 9.5548e-03 | 5 | 2.1175e-01 | **1.399 (rose)** |
| `U` | 1.8450e-02 | 125 | 1.8814e-02 | 0.597 |
| `k` | 2.1169e-05 | 147 | 2.1169e-05 | 0.898 |
| `omega` | 4.0935e-06 | 109 | 5.3981e-06 | 0.209 |
| `e` | 6.1717e-02 | 4 | 8.1490e-02 | 0.924 |

Read only as: on the aborted rung 1, first-solve `p` reached no lower than
**9.55e-03** — about **9,550x** above gate B's 1e-6 — and was rising at abort.
Consistent in direction with ruling §4's risk statement; **not a substitute for it**,
and it grades nothing.

**Nothing was gzipped.** No gate-read file and no path named by a frozen document
was compressed. The single pre-existing `.gz` under `F12_runs`
(`pressure_probe_2026-08-25/evidence_armBprime/log.rhoSimpleFoam.gz`) is another
lane's and was not touched.

## 7. CONTENTION — measured, and it is bimodal again

`CONTENTION_rung2_attempt_2026-08-25.txt`, 10 samples over 80 s, 16 cores:
load1 **min 13.03, max 21.28, median 18.61 = 116 % of 16 cores**. The box is
**oversubscribed**, above the 80-90 % scheduling target, and swung 13.03 -> 21.28
inside 80 s — a third row for this team's bimodality finding. Sampled with spacing
after a first attempt using `read -t` collapsed to ten identical timestamps
(EOF on `/dev/null` returns immediately); the collapsed file was replaced, and the
defect is recorded rather than quietly fixed.

## 8. COST CALIBRATION — standing rule 12

| | |
|---|---|
| Rung 2 cap, frozen (`F12_PREREGISTRATION.md:349`) | **160 core-min** |
| Solver core-minutes actually incurred | **0** — no solver started |
| Actual / predicted | **0.00** |
| Dollars | **$0.00 DERIVED** at $0.0513/core-h, **not measured** (the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |
| Cap status | **NOT consumed.** Rung 2's 160 core-min remains fully available |

Non-solver lane compute (hashing, log parsing, control, sampling) was under one
core-minute and is **not** charged against the rung's cap. **Contention** is named
separately from **waste**: contention was 116 % median as measured in §7; **waste
was zero** — the refusal fired before any compute, which is the interlock working
as intended, not spend lost.

## 9. WHAT THIS LANE COULD NOT VERIFY

- **Gate B's convergence statement was not read**, because no solve ran. Whether
  `rhoSimpleFoam` prints `SIMPLE solution converged in N iterations` on F12's medium
  mesh is **`PENDING`**, exactly as before this attempt.
- **Where first-solve `p` floors on a stable run remains unmeasured** (§6).
- **Whether the 2026-08-25 ruling is intended to override the frozen §5 ordering
  that the interlock encodes** is a supervisor question and is not answered here.
- `scripts/roache_triple.py` is still **not pinned**; the launcher's own docstring
  records it as owed before rungs 2-5, where the triple is the graded object. That
  debt is untouched by this lane and would bind any future rung-2 firing.

## 10. FILES WRITTEN BY THIS LANE

All under `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/`:
`first_solve_residuals.py` (reader + control), `rung1_first_solve_reference.json`,
`CONTENTION_rung2_attempt_2026-08-25.txt`, and this record. **No existing file was
edited; no frozen file was touched; no run directory was created or removed.**
