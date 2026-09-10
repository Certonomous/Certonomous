# Clause satisfiability audit — every closure completion / admissibility clause

**Date:** 2026-09-10
**Team:** closure · lane, for closure-supervisor
**Instrument:** `docs/closure/satisfiability_sweep.py` (committed with this record)
**Compute:** none. Zero solver runs. Reads and re-reads of artifacts already on disk.

---

## 0. The test, and why it exists

`grade_r5d.py:296` carries the clause `n_exec == write_iter`. It was frozen after a
diff read that concluded it was "strictly stricter". It **is** stricter. It is also
**broken**: no run the solver can produce can satisfy it.

The lesson this audit applies to every other clause in the closure line:

> **"Strictly stricter" is not a sufficient check on a guard. A guard that can never
> pass is not strict, it is broken. Every completion clause must be shown
> SATISFIABLE BY THE REAL PRODUCER'S OUTPUT — not merely green against a fixture.**

For each clause the audit asks ONE question and answers it with a measurement against
a NAMED population on disk: **is there any real artifact that SATISFIES it?**

**Three labels, and no hedging words.** These are audit labels, NOT gate verdicts —
they are deliberately disjoint from the rule-1 vocabulary so no reader mistakes a row
here for a graded result.

| Label | Meaning |
|---|---|
| `SATISFIABLE` | measured, N of M pass, N >= 1 |
| `UNSATISFIABLE` | measured, 0 of M, with the structural reason stated |
| `NOT MEASURED` | no population on disk — reported as absence, never as a finding |

**A null is not a finding.** The first hand-sweep of the R5D defect read `log.run`
inside `r4/frozen/`, whose logs are named `log.frozen`; it examined **0** records and
would have "confirmed" the defect from a null. The first draft of the sweep script
made the same class of error in the other direction, looking for `log.solve` one level
under `r4/aposteriori/` whose cases sit **two** levels down. Both were caught by
censusing the population before writing any clause verdict. Every population below is
stated with its root, its log name and its depth.

---

## 1. Populations, censused before any clause was graded

| Key | Root | Log | Depth | N |
|---|---|---|---|---|
| `R4_FROZEN` | `/home/ubuntu/closure-data/r4/frozen` | `log.frozen` | 1 | 27 |
| `R5C_FROZEN` | `/home/ubuntu/closure-data/r5c/frozen` | `log.frozen` | 1 | 27 |
| `R4_APOST` | `/home/ubuntu/closure-data/r4/aposteriori` | `log.solve` | 2 | 60 |
| `WU_APOST` | `/home/ubuntu/closure-data/aposteriori/wu2018` | `log.solve` | 2 | 18 |
| `WU_FROZENK` | `/home/ubuntu/closure-data/aposteriori_frozenk/wu2018` | `log.solve` | 2 | 36 |
| `KAANDORP_APOST` | `/home/ubuntu/closure-data/aposteriori/kaandorp` | `log.run` | 1 | 31 |
| `M1_KOMEGA` | `/home/ubuntu/closure-data/multimodel_sweep/kOmega` | `log.run` | 1 | 39 |
| `M1_KOSST_NULL` | `/home/ubuntu/closure-data/multimodel_sweep/kOmegaSST_null` | `log.run` | 1 | 39 |
| `G1_LEVELS` | `/home/ubuntu/closure-data/g1` | `log.run` | 1 | 3 |
| `G2_LEVELS` | `/home/ubuntu/closure-data/g2` | `log.run` | 1 | 3 |
| `RC3_WU` | `/home/ubuntu/closure-data/rc3/wu2018` | `log.solve` | 1 | **0 — root absent** |
| `RC4_KAANDORP` | `/home/ubuntu/closure-data/rc4/kaandorp` | `log.solve` | 1 | **0 — root absent** |

RC3 and RC4 have no population **by design**: both are DRAFT/UNFROZEN and no compute
has run. Their own clauses are therefore `NOT MEASURED` on their own artifacts, and
Part 2 measures them against the **predecessor producers they will actually run**.

`M2_kepsilon_family` and `LR1_duct_qcr_ladder` have **no run population under
`closure-data`**. Their clauses are `NOT MEASURED`; no verdict is issued on them.

## 2. Reader controls — which fired

Every counting reader was shown able to see a **non-zero** on a NAMED real artifact,
and then shown to **fall to zero** when its token was scrubbed from a copy of that
same artifact. A reader failing either direction stops the sweep with `rc=2`.

| Control | Named artifact | Live | Scrubbed | Fired |
|---|---|---|---|---|
| `EXEC_R5D_ON_FROZEN` (`ExecutionTime = [0-9.]+ s`, grade_r5d.py:293 verbatim) | `r4/frozen/PHLL10595/log.frozen` | non-zero | 0 | yes |
| `EXEC_ANCHORED_ON_SOLVE` | `r4/aposteriori/PHLL10595/ceiling/log.solve` | non-zero | 0 | yes |
| `TIME_ANCHORED_ON_SOLVE` | same artifact | non-zero | 0 | yes |
| `EXEC_ANCHORED_ON_RUN` | `multimodel_sweep/kOmega/CBFS/log.run` | non-zero | 0 | yes |
| `MTIME` (age-guard strict `>`) | two files 1e6 s apart | newer seen | older rejected | yes |
| `EXEC/TIME` on the Kaandorp producer | `aposteriori/kaandorp/AR_1_Ret_360__FROZENEXTRACT/log.run` | 405 / 405 | 0 | yes |
| field-presence reader | same case, time dir `647/` | `U` = True | `NOT_A_FIELD` = False | yes |
| `rc`-file reader | `r4/aposteriori` | **60 of 60 present** | — | yes |
| continuity-value reader | `aposteriori/kaandorp/results.json` | bar 1e9 admits 16/16 | bar 0.0 admits 0 | yes |

The `rc`-file and continuity controls are the load-bearing ones: **both zeros reported
in §4 and §5 below are real absences, measured by a reader shown able to see the
positive on a sibling population.**

---

## 3. PART 1 — per-clause classification

### 3a. Frozen-extraction family — `r4_lib.frozen_complete` (`r4_lib.py:272`)

| Clause | Cite | `R4_FROZEN` | `R5C_FROZEN` | Label |
|---|---|---|---|---|
| c1 `rc == 0` | r4_lib.py:287-292 | 27/27 | 27/27 | SATISFIABLE |
| c2 `End` line | r4_lib.py:294-295 | 27/27 | 27/27 | SATISFIABLE |
| c3 settle-criterion line present | r4_lib.py:298-301 | 14/27 | 27/27 | SATISFIABLE |
| c4 settle verification == `SETTLED` | r4_lib.py:302-309 | 14/27 | 27/27 | SATISFIABLE |
| c5 zero `bounding omega` before write | r4_lib.py:316-322 | 12/27 | 22/27 | SATISFIABLE |
| c6 last time dir == write iteration | r4_lib.py:323-328 | 27/27 | 27/27 | SATISFIABLE |
| c7 eight fields present AND newer than `0/` | r4_lib.py:329-340 | 27/27 | 27/27 | SATISFIABLE |
| **composite** | r4_lib.py:272 | **12/27** | **22/27** | SATISFIABLE |

The shared helper is sound. Every one of its conditions is met by real solver output,
and the composite passes on 12 of 27 (R4) and 22 of 27 (R5C). The R4 shortfall is
**physics** — omega clipped before the write, the sixth condition doing exactly the job
it was added for — not a broken guard.

### 3b. THE DEFECT — `grade_r5d.completion_rule4` (`grade_r5d.py:293-300`)

| Clause | `R4_FROZEN` | `R5C_FROZEN` | Label |
|---|---|---|---|
| clause 5 `n_exec == write_iter` | **0/27** | **0/27** | **UNSATISFIABLE** |
| composite `completion_rule4` | **0/27** | **0/27** | **UNSATISFIABLE** |

**Structural reason.** `kCorrectiveFrozenFoam.C` and `kCorrectiveFrozenFoamV2.C` each
emit the string `ExecutionTime = ` at **exactly one source line**, and that line sits
**outside the outer loop**:

| | `Writing fields at iteration` + `writeNow()` | `ExecutionTime = ` |
|---|---|---|
| `kCorrectiveFrozenFoam.C` | :174 / :175 | **:192** |
| `kCorrectiveFrozenFoamV2.C` | :226 / :227 | **:244** |

`n_exec` is therefore structurally **1** for every run either solver can ever produce,
while `write_iter` is the settle iteration and is **>= 50 by construction**. The
equality is unreachable. Every case returns INCOMPLETE **independently of physics** —
including the 12 R4 and 22 R5C records that pass all six real conditions.

**The audit extends the supervisor's finding from 27 records to 54**, across two
independent populations built by two different campaigns. The reader control fired on
both.

**Why the selftest is green.** The fixture `grade_r5d.py:_make_complete_case` (~:416)
writes `wi` ExecutionTime lines — one per outer iteration. **No producer on this box
writes that log.** The fixture disagrees with the live population, and the selftest
certifies the fixture, not the solver.

**No repair is attempted here.** `grade_r5d.py` is frozen and read-only. A repair is a
registered successor and is the supervisor's to authorise.

### 3c. simpleFoam propagation family — `r4_lib.solve_complete` (`r4_lib.py:494`)

| Clause | `R4_APOST` | `WU_APOST` | `WU_FROZENK` | Label |
|---|---|---|---|---|
| last time dir == last solver iteration | 32/60 | 16/18 | 33/36 | SATISFIABLE |
| **composite** | **32/60** | **0/18** | **0/36** | **split — see below** |

`r4_lib.solve_complete` carries **no exec-count clause at all**, so the R5D defect was
**not** inherited through the shared helper. It was added on top, in R5D only.

- On `R4_APOST` the composite is **SATISFIABLE, 32 of 60**. The 28 failures are
  `rc=136` — SIGFPE, a real crash, correctly caught. A finding, not a broken guard.
- On `WU_APOST` (**0/18**) and `WU_FROZENK` (**0/36**) the composite is
  **UNSATISFIABLE**, and triage gives one reason for all 54 rows: **`no recorded rc`**.
  Measured: a file named `rc` is present **0 of 18** and **0 of 36**. Reader control:
  the identical reader finds `rc` present **60 of 60** on `R4_APOST`. The zero is real.

  **Structural reason.** The Wu runner
  `Wu2018_PIML_RF/aposteriori/run_solves.sh:14` records the return code as the text
  `rc=<n> seconds=<e>` inside **`log.solve.done`**. It never writes a file named `rc`.
  `r4_lib.solve_complete` (r4_lib.py:509-512) requires `<case>/rc` to exist.

  This is a **producer-contract gap, not a broken clause**: the guard is satisfiable
  the moment a runner writes the file, and `R4_APOST` proves 60 rows that do. It is
  carried here because **RC3 delegates its clauses 1–3 to this exact helper** — see
  Part 2, finding B.

### 3d. Sweep family — `grade_m1.completion` (`grade_m1.py:305-344`), `CAP_ITER = 20000`

| Clause | Cite | `M1_KOMEGA` | `M1_KOSST_NULL` | Label |
|---|---|---|---|---|
| `exec_count == CAP_ITER` | grade_m1.py:316 | 35/39 | 37/39 | SATISFIABLE |
| `last_time == CAP_ITER` | grade_m1.py:310-313 | 35/39 | 37/39 | SATISFIABLE |
| physics fields present at cap | grade_m1.py:314-315 | 35/39 | 37/39 | SATISFIABLE |
| age guard vs `0/U` | grade_m1.py:317-322 | 35/39 | 37/39 | SATISFIABLE |
| **composite** | grade_m1.py:305 | **35/39** | **37/39** | SATISFIABLE |

M1's exec-count clause has the **same wording** as R5D's but a **different producer**:
`simpleFoam` prints one `ExecutionTime` line per outer iteration, inside the loop. The
clause is satisfied by 72 of 78 real logs. **The wording was never the defect — the
producer was.** This is the cleanest demonstration in the audit that a completion
clause cannot be assessed without naming the binary that has to satisfy it.

The same clause appears at `grade_m1b.py:557` and `grade_m1d.py` on the same corpus,
and at `grade_g1b.py:737` and `grade_m2.py:143` in the same frozen shape.

### 3e. Grid-triple family — `grade_g1.completion` / `grade_g2.completion`

| Clause | Cite | `G1_LEVELS` | `G2_LEVELS` | Label |
|---|---|---|---|---|
| P7 `ExecutionTime` lines == registered `endTime` | grade_g1.py:501-505, grade_g2.py:710-715 | 3/3 | 3/3 | SATISFIABLE |
| P4 last time dir == registered `endTime` | grade_g1.py:478-483 | 3/3 | 3/3 | SATISFIABLE |

Both grid families satisfy P7 on **every** level. `grade_m2.py:143` carries the clause
in the identical frozen shape (`nexec == ENDTIME`) but **M2 has no run population** —
`NOT MEASURED`.

### 3f. RC2 — `rc2_divergence.py` / `regrade_rc2.py`

**No completion clause is defined in RC2**; it is a *reader* repair, and it already
applies the doctrine this audit exists to enforce. Its own docstring records the
governing ruling verbatim — **Sanaa 2026-08-28: "a control that writes a schema the
producer never emits certifies blindness"** — and it therefore runs its two-direction
control on **named real producer logs** rather than synthetic strings
(`rc2_divergence.py:197`, corpora at :139-160). Its negative corpus is 16 named
Kaandorp logs and its positive corpus is 6 named real fatal logs from elsewhere on the
box, taken because *not one* of the 16 carries a genuine fatal.

**RC2 is the instrument R5D should have been.** The doctrine was already written down
in this line before R5D was frozen.

### 3g. `grade_r5c.py`, `grade_r4b.py`, `grade_r4b_ib.py`

- `grade_r5c.py` reads `ExecutionTime` **as a cost figure only** (`:150-151`, last
  value, for core-hours) and delegates completion to `R.frozen_complete` unmodified
  (`:366`). **It carries no exec-count clause.** Not affected.
- `grade_r4b.py` delegates to `R.solve_complete` (`:837`) with no added clause.
  Not affected.
- `grade_r4b_ib.py` grades a **birth record**, not a solve; it has no completion
  clause of this class. Not affected.

**The defect is confined to `grade_r5d.py`. It was not inherited through `r4_lib.py`,
and no sibling grader carries it.**

---

## 4. PART 2 — RC3 and RC4, before the freeze

Both items are DRAFT/UNFROZEN with instruments built and **no compute run**, so their
own artifacts are `NOT MEASURED`. The audit therefore does what the R5D freeze failed
to do: **it reads the source of the producer each item will actually run**, and
measures each clause against that producer's real output.

**Both items run `simpleFoam`** — established by reading the builders, not assumed:
`build_rc3_ladder.py:548` and `build_rc4_cases.py:468` both write
`application     simpleFoam;`. RC4's "frozen operator" is `simpleFoam` plus the sparta
correction library, not a separate binary.

### Findings

| Clause | Instrument | Own population | Predecessor producer | Label | Verdict |
|---|---|---|---|---|---|
| clause 4 fields at last time | rc3_ceiling.py:245-250 | NOT MEASURED | `WU_APOST` 18/18, `WU_FROZENK` 36/36 | SATISFIABLE | safe |
| clause 5 `n_exec == n_time` | rc3_ceiling.py:253-263 | NOT MEASURED | `WU_APOST` 16/18, `WU_FROZENK` 33/36 | SATISFIABLE | safe |
| clause 6 age guard vs `0/U` | rc3_ceiling.py:265-278 | NOT MEASURED | `WU_APOST` 18/18, `WU_FROZENK` 36/36 | SATISFIABLE | safe |
| clause 4 fields (incl. `kDeficit`) | rc4_score.py:227-234 | NOT MEASURED | `KAANDORP_APOST` 27/31 | SATISFIABLE | safe |
| clause 5 `n_exec == n_time` | rc4_score.py:235-241 | NOT MEASURED | `KAANDORP_APOST` **31/31** | SATISFIABLE | safe |
| clause 6 age guard vs `0/U` | rc4_score.py:242-249 | NOT MEASURED | `KAANDORP_APOST` 27/31 | SATISFIABLE | safe |
| **clauses 1–3** (`r4_lib.solve_complete`) | rc3_ceiling.py:236, rc4_score.py:220 | NOT MEASURED | **`WU_APOST` 0/18, `WU_FROZENK` 0/36, `KAANDORP_APOST` 0/31** | **UNSATISFIABLE** | **FINDING B** |
| clause 8 continuity | rc3_ceiling.py:322, rc4_score.py:303 | NOT MEASURED | see FINDING C | SATISFIABLE | **FINDING C** |

**Clause 5 is the headline reassurance.** RC3 and RC4 formulate it as
`n_exec == n_time` — counting the producer's own `Time = ` lines — **not** against a
registered iteration count. On the Kaandorp producer it holds **31 of 31**. This is
the correct shape of the clause R5D got wrong, and it is already in both instruments.

---

### FINDING B — clauses 1–3 cannot pass as the producers stand (both items)

`rc3_ceiling.completion` and `rc4_score.completion` both delegate clauses 1–3 to
`r4_lib.solve_complete(case, required=())`, which requires a file named **`rc`** in the
case directory, and both fix `LOG_NAME = "log.solve"` (rc3_ceiling.py:103,
rc4_score.py:99). Measured against the producers each will run:

| Producer | Writes `rc`? | Log name | RC clause-1–3 pass rate |
|---|---|---|---|
| Wu chain, `Wu2018_PIML_RF/aposteriori/run_solves.sh:14` | **no** — writes `rc=<n> seconds=<e>` into `log.solve.done` | `log.solve` ✓ | **0 of 18**, **0 of 36** |
| Kaandorp chain, `Kaandorp2020_TBRF/aposteriori/run_lane.py:158` | **no** — return code kept in `results.json` only | **`log.run`** ✗ | **0 of 31** |

Measured directly: `rc` present **0 of 18**, **0 of 36**, **0 of 31**; `log.solve`
present **0 of 31** on the Kaandorp tree, `log.run` **31 of 31**. Reader control: the
same readers find `rc` present **60 of 60** on `R4_APOST`. **Both zeros are real
absences.**

**Neither RC3 nor RC4 has a committed runner.** `RC3_wu_ceiling_gate_validation/`
holds `PREREGISTRATION.md`, `build_rc3_ladder.py`, `rc3_ceiling.py`,
`rc3_fixedpoint.py` — a builder and a scorer, no launcher. RC3's §9 anti-gaming row
fixes the model as *"the same solver the predecessors ran; no new solver is written"*.
Run with the predecessor's runner unchanged, **every RC3 row fails clause 1**,
`verdict()` hits its `incomplete` screen (rc3_ceiling.py:429-435) before any gate, and
RC3 returns **NOT A RESULT for the whole item** — six configurations × three cases,
none of them reachable, independently of the physics.

**And the fixture hides it, exactly as R5D's did.** `rc3_ceiling._fake_case` writes
`open(<case>/rc)` at **rc3_ceiling.py:536**. The selftest is green because the fixture
writes a file the live producer never writes.

**This is the R5D pattern, caught before the freeze.** The difference from R5D matters
and is stated plainly: R5D's clause is unsatisfiable **by the solver's source code**
and no runner can fix it. Finding B is a **producer-contract gap** — satisfiable the
moment the item ships a runner that writes `rc` and names the log `log.solve`, which
`R4_APOST` demonstrates 60 times over. It is cheap to close before the freeze and
frozen shut after it.

### FINDING C — clause 8's continuity bar, and the global screen

Both instruments enforce continuity as a **global** screen: a single scored row outside
the bar takes the **whole item** to NOT A RESULT (rc3_ceiling.py:436-442,
rc4_score.py:426-436), and `gate_arithmetic` in both **refuses outright** if such a row
reaches it (rc3_ceiling.py:374-379, rc4_score.py:366-374). There is deliberately no
quiet-acceptance path — that design is sound and should stay.

Measured on the recorded predecessor values in the NAMED artifact
`/home/ubuntu/closure-data/aposteriori/kaandorp/results.json` (16 rows carry
`divU_rms_over_gradscale`; reader control — a bar of 1e9 admits 16/16, a bar of 0.0
admits 0):

| Case | rows | `<= 1e-3` (RC4's binding bar) | `<= 1e-4` (RC3's bar) |
|---|---|---|---|
| `AR_1_Ret_360` | 7 | 7 | 3 |
| `AR_3_Ret_360` | 3 (metric recorded) | 3 | 3 |
| **`CBFS13700`** | **6** | **0** | **0** |
| total | 16 | 10 | 6 |

`CBFS13700` spans **5.26e-3 to 2.41e-1** — and its **NULL** row, the uncorrected
baseline that is the denominator of every cut, is already **5.26e-3**, so the failure
is not caused by any correction. `CBFS13700` is in scope for **both** items
(`build_rc3_ladder.py:108`; `X_REATT_LES` in both). `MIN_CASES = 2` of
`N_INSCOPE = 3` in both.

The classification is **SATISFIABLE** — 6 of 16 rows clear even the tighter bar, so
neither clause is broken. The finding is a **coupling hazard**, and it differs sharply
between the two items:

- **RC4 already knows.** `rc4_score.py:683` hardcodes the measured
  `CBFS13700__TRUTHR` continuity of **0.3219275282624856** into its selftest and asserts
  the verdict is NOT A RESULT. RC4 is honest about its exposure. Its consequence is
  still worth stating: with `CBFS13700` effectively lost, `MIN_CASES = 2 of 3` has
  **zero margin** — both `AR_1_Ret_360` and `AR_3_Ret_360` must survive or the item is
  NOT A RESULT.
- **RC3 does not.** RC3's bar is **10× tighter** (`CONTINUITY_MAX = 1e-4`,
  rc3_ceiling.py:93) and its fixture `_row` hardcodes
  `divU_rms_over_gradscale = 1e-6` on **every** synthetic row (rc3_ceiling.py:558) —
  **5,000× tighter than the real CBFS NULL**. The number `0.3219` appears nowhere in
  RC3. On the predecessor evidence, at 1e-4 RC3 loses all 6 `CBFS13700` rows **and**
  4 of 7 `AR_1_Ret_360` rows (TRUTH at 1.14e-4, and all three ML rows at 3.1–3.8e-4).

  Because the screen is global, that takes the **whole item** to NOT A RESULT.

**This is the same fixture-versus-population failure as R5D, in the admissibility
channel rather than the completion channel.** Honest limit on this finding: these are
the *Kaandorp* a-posteriori runs. For RC4 that is the direct predecessor, same chain
and same cases. For RC3 it is a **different chain (Wu) on the same three cases**, so it
bounds the expectation rather than settling it — but `CBFS13700`'s NULL row is a plain
uncorrected baseline solve, and its 5.26e-3 is a property of that mesh and case, not of
the correction. The audit reports it as a bounded expectation, not a measurement of
RC3's own rows, which do not exist.

---

## 5. Part 2 verdict

**RC3 — do not freeze tonight as it stands.** Two clauses would have to be answered
first, and both are cheap now and frozen shut afterwards:
1. **Finding B** — clause 1's `rc` file has no producer. Ship a runner, or the item is
   NOT A RESULT on 18 of 18 rows before any gate.
2. **Finding C** — `CONTINUITY_MAX = 1e-4` against a global screen, with a fixture
   5,000× tighter than the real baseline and `CBFS13700` at 5.26e-3 on the NULL alone.

**RC4 — one clause to answer.** Finding B applies with an extra limb: the Kaandorp
producer writes `log.run`, and RC4 fixes `LOG_NAME = "log.solve"`. Its clauses 4, 5 and
6 measure clean (27/31, **31/31**, 27/31), and its continuity exposure is already
encoded and tested in its own selftest.

**Neither instrument was edited, and no amendment is drafted here.** These are
findings; the amendments are the supervisor's.

---

## 6. What this audit did not verify

- **RC3 and RC4 have no runs.** Every RC row's own population is `NOT MEASURED`.
  Part 2 measures *producers*, not RC's own artifacts, and says so on every row.
- **`M2` and `LR1` have no run population** under `closure-data`. `grade_m2.py:143`
  carries the same P7 clause in the frozen `nexec == ENDTIME` shape and is
  `NOT MEASURED`. It is the highest-priority remaining gap in this sweep.
- **Finding C's bearing on RC3 is bounded, not measured** — different chain, same
  cases; see the honest limit stated in §4.
- Clause 7 in both RC items (the builder's `guard_no_existing_times`) is a
  **pre-run** guard on a directory that must not exist. It has no artifact population
  by construction and was not measured.
- `grade_m1b.py` / `grade_m1d.py` were read and their clause shapes matched to
  `grade_m1.py`; their own regrade corpora were not swept separately, because the
  clause and the corpus are the same ones measured in §3d.
- No `docs/COST_CALIBRATION.md` row is filed: this audit ran **zero solver compute**,
  so there is no estimate-versus-actual pair to calibrate.

---

## 7. Reproduction

```
python3 /home/ubuntu/Certonomous/docs/closure/satisfiability_sweep.py
```

Reads only. Writes nothing outside a temporary directory it removes. Refuses with
`rc=2` if any reader control fails in either direction. Green under `python3` and
`python3 -O`; no `assert` carries a guard or a refusal (L-332). JSON on stdout, the
summary table on stderr.
