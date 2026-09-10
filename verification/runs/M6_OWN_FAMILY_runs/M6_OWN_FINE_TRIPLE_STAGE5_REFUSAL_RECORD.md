# M6 OWN-FAMILY FINE TRIPLE {L2,L1,L0} — STAGE-5 REFUSAL RECORD

**DRAFT — NOT COMMITTED.** Authored by a cfd lab-lane, 2026-09-10, ZERO COMPUTE
(no solver launched; every number below is read from an artifact already on disk).

**Governing document:** `docs/charters/CASE_PROTOCOL_CHARTER.md` v1.0 (IN FORCE
2026-09-10). **It IS at HEAD**, landed by `e24953a6b` while this record was being
drafted; the committed blob is byte-identical to the working-tree copy classified
against (verified by diff). Classification below is retrospective: the protocol
(2026-09-10) post-dates every event it classifies (2026-09-07 to 2026-09-09), so
nothing here is a charter violation — it is the first application of a new standard
to an old failure. **§5 requires "the cause class for any non-pass" but supplies no
stage-5 taxonomy** (verified by grep over the HEAD blob); see §5b.

**Case:** `M6-OWN-FINE-TRIPLE` (cfd) · run root
`verification/runs/M6_OWN_FAMILY_runs/`
**Pre-registration:** `verification/campaign/M6_OWN_FAMILY_FINE_TRIPLE_PREREGISTRATION.md`,
frozen at `16913288687539e1cd1e2ea66c49511dfd9faf65`, v1.1 with the §13 grading-path
re-pin addendum.

---

## 1. STAGE

**Stage 5 (Grade).** The frozen own-family comparator was armed detached and run
against the triple. Stages 1 (setup) and 2 (bug check) have partial instances in the
run root; **stage 3 (smoke) has no instance at all** (§3 below); stage 4 (full run)
was entered at L2 only and terminated in a §4 stop condition.

## 2. EXIT CONDITION

The comparator **REFUSED, exit 2** — it did not degrade, which is the behaviour
CLAUDE.md rule 4 and protocol §2 require of it.

- `M6_OWN_FAMILY_FINE_TRIPLE_AUTOGRADE.rc` = **2**
- `M6_OWN_FAMILY_FINE_TRIPLE_AUTOGRADE.out`:
  `REFUSED: L2: rule-4 strict completion FAILED on ['rc_zero',
  'rc_read_from_SOLVER_RC_not_around_setsid', 'End_line', 'last_time_equals_endTime',
  'ExecutionTime_count_equals_endTime', 'fields_present_at_endTime',
  'age_guard_every_field_newer_than_0_over_U', 'ALL']`

All seven clauses failed simultaneously. That signature is **not** a solve that fell
short; it is a solve that produced no time directory beyond `0/`.

## 3. WHAT EXISTS PER LEVEL — measured from disk

| Level | Mesh | `solve/` dir | Time dirs | Solver log | Verdict |
|---|---|---|---|---|---|
| **L0** (4,592,640 cells) | built (pyHyp) | **absent** | none | none — `log.pyhyp_nominal`, `log.cgns_utils` only | never solved |
| **L1** (574,080 cells) | built (pyHyp) | **absent** | none | none — mesh logs only | never solved |
| **L2** (71,760 cells) | built (pyHyp) | **present** | **`0/` only** (+ `processor{0..3}/0`) | `log.rhoSimpleFoam`, crashed | **solve attempted, died in iteration 1** |
| **L3** (mesh study) | 3 variants built | absent | none | mesh logs only | not a triple member |
| **L3b** (mesh study, N27–N47) | 5 variants built | absent | none | mesh logs only | not a triple member |

**The chief's reading is CONFIRMED in its conclusion and CORRECTED in its mechanism.**
No level of the graded triple holds a flow solution, and the triple could never have
been graded. But L2 is **not** a level where nothing ran: a full run was launched, the
mesh was decomposed, and `rhoSimpleFoam` started and crashed. The distinction matters
for the cause class (§5) — this is a crashed stage 4, not an empty stage 4.

`L2/solve/0/` holds `T U alphat k nut omega p` written at 23:15:09Z. Nothing else was
ever written. `postProcessing/yPlus/` exists (23:15:54Z) — the function object fired
once before the crash.

## 4. THE CRASH — measured

- `L2/solve/RC_rhoSimpleFoam.txt` → `WRAPPER_RC=136` = 128 + 8 = **SIGFPE**.
- `L2/solve/log.rhoSimpleFoam` tail: `mpirun noticed that process rank 1 ... exited on
  signal 8 (Floating point exception)`; backtrace frame
  `Foam::hePsiThermo<psiThermo, pureMixture<sutherlandTransport<species::thermo<
  hConstThermo<perfectGas<specie>>, sensibleInternalEnergy>>>>::calculate(...)`
  called from `::correct()`.
- `grep -c '^Time = '` = **1**; last is `Time = 1`. `ExecutionTime` lines = **0**.
  `End` lines = **0**.
- First-iteration initial residuals are all ≈1.0 (`Ux` 0.99999990, `Uz` 1,
  `e` 0.99999999) — the crash is in the **first** thermo update, before any
  convergence history exists.
- `L2/solve/STOPPED.txt` (23:16:06Z): *"rhoSimpleFoam inner rc=136 (outer 0). A
  non-zero rc inside the container is a FAILED STEP."*

**Physics reading:** internal energy left its admissible range in iteration 1, driving
`hePsiThermo::calculate` to an FPE. Under protocol §4 that is the registered stop
condition *"a field outside its bounds: stop"*. The stop was correctly detected and
correctly recorded by the driver.

## 5. CAUSE CLASS

### 5a. The underlying physics cause — IS in the taxonomy
**Protocol §4 monitor stop: "a field outside its bounds → stop."** Taken to its limit
(FPE rather than a bounds report), but it is that class, and §4's ladder applies:
diagnose by class, one registered first action, resume. That ladder was in fact walked
retrospectively (§6).

### 5b. The stage-5 event — a MISSING CLASS
Protocol §5 requires *"the cause class for any non-pass"* at grading, but supplies **no
stage-5 taxonomy**. Every named class in the charter is a stage-3 prediction failure
(§3), a stage-4 monitor stop (§4), or a park condition (§8). **None describes a
comparator refusing because the state it was asked to grade does not exist.** The
chief's instinct that this reveals a missing class is upheld.

**PROPOSED CLASS — this is a proposal, not a ruling, and belongs on the
verification-supervisor's desk:**

> **`STAGE-GATE-ESCAPE`** — a case reaches stage 5 whose stage-4 exit was a registered
> stop condition, because the stage-4→stage-5 gate tested the **liveness** of the run
> rather than its **completion**. The stage-5 refusal is correct and carries no
> information about the case; the finding is entirely upstream.

I depart from the chief's proposed wording *"upstream-stage-failure surfacing at stage
5"* on the evidence. That phrasing names the symptom. The defining feature here is not
that an upstream stage failed — stage 4 failed **loudly and correctly**, writing
`STOPPED.txt` fifty-one seconds after the crash — but that **no gate read it**. The
class should name the absent gate, because that is what a future case can be protected
against.

## 6. THE PROCESS FAILURE — the sequence, with timestamps

All times UTC, from file mtimes, `launcher.queue.out`, `STEP_RC.txt`, the
autograde `.stamp`, and `verification/queue/LAUNCH_LOG.tsv`.

| Time | Event | Artifact |
|---|---|---|
| 2026-09-07 21:33:08 | run root created | `RUN_ROOT_CREATED_EPOCH` = 1788816788 |
| 2026-09-07 21:35 | L2 mesh built, `L2/RESULT.json` | `L2/log.pyhyp` |
| 2026-09-08 18:23–18:36 | L1, L3, L3b meshes built | per-level `RESULT.json` |
| 2026-09-08 21:30 | L0 mesh built | `L0/RESULT.json` |
| 2026-09-08 22:10 | own-family grader authored | `analyse_m6_own_family.py` |
| 2026-09-08 22:14 | solve driver authored | `run_m6_own_family_triple.sh` |
| 2026-09-08 23:01 | pre-registration last written | prereg mtime |
| **2026-09-08 23:14:42** | **daemon launches L2, phase `all`** | `LAUNCH_LOG.tsv` row: pid 523528, ranks 14, 1068.0 core-min, commit `dddca8ba` |
| 2026-09-08 23:14:57 | solver pin verified (v2506, sha256 `d9a2a456…`); grading path pinned (`da0df95c…`, `8007b23d…`) | `launcher.queue.out` |
| 2026-09-08 23:15:08 | grading-path rehearsal: all planted controls passed under `python3` and `python3 -O` | `log.comparator_controls`, `..._O` |
| 2026-09-08 23:15:29 | `decomposePar` rc=0, 20 s, 4 ranks, 1.333333 core-min | `STEP_RC.txt` |
| **2026-09-08 23:15:59** | **`rhoSimpleFoam` SIGFPE, inner rc=136, 37 s, 2.466667 core-min** | `RC_rhoSimpleFoam.txt` |
| 2026-09-08 23:16:06 | driver aborts, writes `STOPPED.txt`; accumulator frozen at 3.800000 | `STOPPED.txt`, `SOLVE_SPENT_COREMIN.txt` |
| 2026-09-08 23:16:06 | queue status written: `launcher_rc=6` | `STATUS.queue.M6-OWN-FINE-TRIPLE` |
| **2026-09-08 23:24:52** | **autograde watcher ARMED — 8 m 46 s AFTER the abort** | `.stamp` `armed=…` pid 526908 ppid=1 |
| 2026-09-08 23:29:07 | watcher sees driver gone after 17×15 s, runs grader | `.stamp` `driver_terminal=…after_17x15s` |
| 2026-09-08 23:29:07 | **grader REFUSES, rc=2** | `AUTOGRADE.rc`, `.out` |
| **2026-09-09 00:29:28** | **first smoke run of the entire family** — 1 h 13 m after the abort | `L2/smoke_stabilized/log.write_case` |
| 2026-09-09 00:29 → 09-09 17:46 | 27 post-hoc diagnostic smokes (`L2/smoke_*`, `L2_arfix_diag/smoke_*`, `L2_arfix2_{A,B}`) | per-dir `RC*.txt` |

### 6a. Gate 1 — stage 3 is ABSENT, not failed
`run_m6_own_family_triple.sh` accepts `PHASE` ∈ `{stage, solve, all}` (line 102).
`stage` means *file staging*, not a protocol stage. `grep -niE 'smoke|dry.?run'` over
the driver returns **nothing**. `grep -niE 'smoke|dry.?run|first.?iteration|shakedown|
pilot'` over the frozen pre-registration returns **nothing**. There is no smoke stage
in the instrument and none was registered.

I tested this rather than assuming it: a naive mtime search finds `smoke_*` content
dated 2026-09-07, which *appears* to pre-date the launch — but those hits are all
`constant/polyMesh/{points,neighbour,…}`, mesh files copied with preserved mtimes.
Restricting to solver artifacts (`RC*.txt`, `log.*`), the **earliest is 2026-09-09
00:29:28Z**. **No smoke run predates the full launch anywhere in the family.**

Had stage 3 existed, an L2 smoke at §3's registered 5–10 % of iterations would have hit
the identical first-iteration SIGFPE for ≈2.5 core-min, and the full run would never
have launched. In this instance the saving is small only because the crash was
instantaneous.

### 6b. Gate 2 — the stage-4→stage-5 gate is UNENFORCED, and this is the proximate defect
`autograde_watch_m6_own_family.sh` lines 26–34: the sole wait condition is
`pgrep -f 'run_m6_own_family_triple.sh'`. When the process is gone, the grader runs.
Nothing reads `STOPPED.txt`, `STEP_RC.txt`, `RC_rhoSimpleFoam.txt` or
`STATUS.queue.*`. The script's own comment (lines 24–25) states the intent explicitly:
wait for the driver to terminate *"(all levels solved, **OR a level crashed and the &&
chain aborted**)"*, and line 34 records the timeout branch as *"grading anyway (grader
will refuse on incomplete, honest)"*.

**The escape is by design, not by accident.** The instrument deliberately routes a
crashed run into the comparator, relying on the comparator to refuse. That is
defensible as fail-closed behaviour and it worked — but under protocol §4/§5 it is the
wrong gate: **stage 4 gates stage 5, and liveness is not completion.** The watcher was
armed at 23:24:52Z against a tree whose `STOPPED.txt` had been on disk since 23:16:06Z.
A single `[ -f STOPPED.txt ] && exit` would have converted a stage-5 refusal into a
stage-4 stop with its correct §4 cause class.

### 6c. Ranking the two defects — honestly, both
They are different failures with different costs and I decline to collapse them:
- **6b is the proximate defect.** It is why a stage-5 refusal record exists at all, and
  it is why the cause class had to be manufactured (§5b) instead of read off §4.
- **6a is the deeper defect.** It is why a case with a first-iteration thermo blow-up
  was launched as a 1,068-core-min full run in the first place.

### 6d. A third finding — the cap accumulator is blind to the diagnostic spend
`SOLVE_SPENT_COREMIN.txt` still reads `3.800000`. The 27 post-hoc smokes ran under the
same run root and cost ≈135.9 core-min of solver time, **none of which any accumulator
counted**. The §7.3 single hard cap (2,136 core-min) therefore under-reports the
family's true spend by a factor of ≈37. (Under the charter's closing clause this
costs nothing today — see §8 — but the accumulator is still wrong.)

## 7. THE NUMBERS

**Failed full run (L2) — WRAPPER-MEASURED, independently recomputed here:**

| Step | wall s | ranks | core-min stated | core-min recomputed (wall×ranks/60) | match |
|---|---|---|---|---|---|
| `decomposePar` | 20 | 4 | 1.333333 | 1.333333 | yes |
| `rhoSimpleFoam` | 37 | 4 | 2.466667 | 2.466667 | yes |
| **total** | 57 | 4 | **3.800000** | **3.800000** | yes |

`SOLVE_SPENT_COREMIN.txt` = `3.800000`. **Independently confirmed** — I recomputed it
from `STEP_RC.txt`'s raw `wall_s` and `ranks` fields rather than accepting the stated
`coremin`. The chief's 3.8 stands.

**This 3.8 core-min is 100 % waste**: it produced no time directory, no gradeable
state, and no gate value. Derived cost at the recorded c7a.4xlarge rate $0.0513/core-h:
**$0.0032, DERIVED, not measured** (the box cannot read its own billing —
`COMPUTE_BUDGET_CHARTER` §5).

**Post-hoc diagnostic spend — DERIVED from solver `ClockTime`, not from any accumulator:**
Sum of final `ClockTime` over the 24 diagnostic solver logs = **8,152 s = 135.87
core-min** (all serial, ranks=1; no `processor*` dirs in any smoke case). Derived
cost **$0.116**. This is **not** waste — it is the §4 ladder being walked, and it
succeeded: `smoke_rhopimple_{lts,nnoc3,ceiling5000}`, `smoke_arfix` and the fourteen
`L2_arfix_diag/smoke_*` cases all exit **rc=0** and reach **t=500**, whereas every
`rhoSimpleFoam` variant (`smoke_stabilized`, `smoke_simplec`, `smoke_diag_fo`,
`smoke_potentialfoam2`) repeats **rc=136**.

I discarded a first estimate of ≈5,752 core-min derived from directory mtime spans:
those spans include long idle gaps (one case spans 16 h of wall clock for 226 s of
solver time) and the figure was worthless. The `ClockTime` figure is the honest one.

**Family total: 139.67 core-min = 2.33 core-h = $0.119 DERIVED.** Of that, **3.8
core-min is waste** and **135.87 core-min is diagnosis that produced a result.**

## 8. LADDER ACTION

Protocol §4: on a bounds-violation stop, apply the one registered first action for that
class, resume from checkpoint, record action and outcome; two stops on the same cause →
climb the ladder.

**Retrospectively, the ladder was already walked** between 2026-09-09 00:29 and 17:46,
before the protocol existed to name it. It climbed §3's registered order — numerics,
then model — and terminated in a **finding**: the segregated steady solver
(`rhoSimpleFoam`) fails at iteration 1 on this mesh under every stabilisation tried,
while the transient/pseudo-transient route (`rhoPimpleFoam`, LTS and fixed-ceiling
variants) runs clean to t=500. Under §4 that is the pseudo-transient rung of the
escalation ladder, reached and **passed**.

**Recommended next action, for the cfd-supervisor (§9 standing authority — mesh, model,
numerics and successor registrations are the supervisor's, and I hold none of it):**
1. **Register a successor** for the fine triple on the `rhoPimpleFoam` pseudo-transient
   route, carrying the §4 monitor conventions. The diagnostic evidence for that choice
   already exists on disk and cost 135.87 core-min.
2. **Add stage 3 to the driver** (§6a): a registered 5–10 % smoke at the coarsest level,
   gating the full run.
3. **Fix the stage-4→stage-5 gate** (§6b): the watcher must read the run's terminal
   state, not its process table. Liveness is not completion.
4. **Refer the proposed `STAGE-GATE-ESCAPE` class** (§5b) to the verification-supervisor,
   who owns the taxonomy. I propose; I do not adopt.
5. **Correct the accumulator** (§6d) so diagnostic work under a run root is costed.
6. **Land the estimate-vs-actual row** in `docs/COST_CALIBRATION.md` (rule 12): predicted
   1,068 core-min for the triple, actual 3.8 core-min consumed before the stop — the
   ratio is not meaningful because the run never ran, and the row should say so rather
   than report 0.0036.

**Budget note.** `CASE_PROTOCOL_CHARTER` §9 closing clause suspends time and money gates
for the 3D cases still to run, and M6 is named in its scope line. The §7.3 cap of 2,136
core-min therefore does not stop the successor. Every run is still costed and still
lands its calibration row — the exemption removes the gate, not the accounting.

## 9. VERDICT

**`NOT A RESULT`** — CLAUDE.md rule 1 vocabulary.

No level of {L2, L1, L0} holds a flow solution. L2's stage-4 run terminated on a §4
bounds-violation stop (SIGFPE, iteration 1) after 3.8 core-min; L1 and L0 were never
launched. The stage-5 comparator refused (rc=2) on all seven rule-4 completion clauses
and was **right to refuse**. No Gate P value and no Gate G Roache triple exist, and
under rule 5 none could: there are no three values to be monotone.

The verdict attaches to the **run**, not to the physics (L-DPW8, `docs/LESSONS.md`
≈line 9969: *"`BLOCKED` is a statement about the run, never about the physics"*). The
physics finding — segregated steady fails, pseudo-transient succeeds — is in §8 and is
real, measured, and carried forward.

## 10. WHAT I COULD NOT VERIFY

- **Whether a queue entry was ever formally placed.** `M6-OWN-FINE-TRIPLE.queue_row.DRAFT.json`
  declares itself `NOT READY FOR PLACEMENT` with three open blockers (B1 no applicable
  grader, B2 no solve driver, B3 ranks not registered) and `PREPARED, NOT ENQUEUED`. Yet
  `LAUNCH_LOG.tsv` records a daemon launch at 23:14:42Z with ranks=14 and cost 1068.0,
  matching that draft's fields. `verification/queue/cfd/` holds **no** M6 entry today.
  Either an entry was created and consumed, or the launch bypassed placement. **The
  draft's own blockers B1 and B2 were in fact closed** — the grader (22:10) and the
  driver (22:14) were both authored before launch — so this may be nothing more than a
  stale draft. I could not determine it from disk and did not search git history for the
  deleted entry. **Flagged, not concluded.**
- **Prereg §8/§12.5 say "THROUGH THE QUEUE DAEMON, NOT A DIRECT SOLVE" and "No launch
  until check-4".** §12.1 records check-4 as passed. The `LAUNCH_LOG.tsv` row is
  consistent with a daemon launch. I found no evidence of a direct launch, and I am
  **not** alleging one.
- **The exact cell or patch where energy left bounds.** The backtrace gives the function,
  not the cell. No `-DFULLDEBUG` run exists and I launched none.
- **Whether the 27 diagnostic smokes were themselves pre-registered.** I did not audit
  them; they post-date the freeze and are diagnosis, not graded runs.

---

*Drafted by a cfd lab-lane, 2026-09-10. Nothing committed; nothing sent (rule 7). No
frozen file edited (rule 6). Zero compute.*
