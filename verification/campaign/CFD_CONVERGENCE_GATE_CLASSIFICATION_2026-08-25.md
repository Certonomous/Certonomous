# cfd — CONVERGENCE / PLATEAU GATE CLASSIFICATION, 2026-08-25

> **THIS DOCUMENT GRADES NOTHING AND MOVES NO VERDICT. NO EXISTING VERDICT IN
> ANY TEAM, cfd's INCLUDED, IS INDICTED BY ANYTHING BELOW.** It is a lane's
> classification of gate *designs*, plus one diagnostic run on artifacts already
> on disk. Every cfd row named here keeps the verdict it already carries.
>
> **It is also not a ruling.** The ruling is
> `verification/campaign/CFD_CONVERGENCE_GATE_RULING_2026-08-25.md` (`ea41497b`)
> as amended by `..._RULING_AMENDMENT_2026-08-25.md` (`665935ea`), both by the
> cfd supervisor. §4 below is a **draft recommendation** offered into that
> ruling, not a rival to it.
>
> **ZERO NEW COMPUTE.** Every number cites an artifact already on disk. **No
> `docs/COST_CALIBRATION.md` row is owed and none is filed** — rule 12's
> estimate-versus-actual comparison attaches to a *process completion* with a
> solver spend. This is a records-and-instrument item with no solver run, and
> saying so is more honest than filing a row of zeroes.

---

## 0. THE TWO PREMISES I WAS HANDED THAT THE DISK CONTRADICTS

My brief carried four factual premises. **Two hold, two do not.** Both
corrections are instances of the shape the amendment (`665935ea` §4) names as
the deepest thing to come out of this work — *a comparison whose inputs were not
what the code assumed* — and the second is an instance in the very instruction
that warned me about it.

### 0.1 HOLDS — the triple instrument is not A, B or C

`scripts/roache_triple.py:133` states, in its own "what this instrument cannot
see" block:

> `* anything about iterative convergence or plateau.  Those states are the`
> `  CALLER's measurements, handed in; step (a) only acts on them.`

Confirmed, and confirmed in the code as well as the prose:
`grade_ladder(…, iterative_states=None, plateau_states=None, …)`
(`scripts/roache_triple.py:537`) *receives* the states and acts on them at
`:581–:592`; it computes none. **The entire exposure lives in the callers.** The
triple instrument is correctly classified as neither A, B nor C.

### 0.2 HOLDS — a two-point gate cannot distinguish convergence from aliasing

Structural, needs no demonstration, and cfd's own
`scripts/check_convergence.py:75–83` had already written it down before this
audit existed: an endpoint difference "aliases against a case approaching steady
state as a decaying oscillation whose period is near the window length", and a
last-quarter window "silently loosens as a run is extended".

### 0.3 DOES NOT HOLD — `grade_f4.py` has no `standoff_stats`, and line 511 is not the gate value

My brief stated: *"`grade_f4.py` computes `standoff_stats` as mean/std over
`snapshot_times(case_dir)` and takes the gate value at
`snapshot_times(case_dir)[-1]` (line 511)."* Three parts, all wrong:

| claim | what is on disk |
|---|---|
| a function `standoff_stats` | **no such identifier exists** in `grade_f4.py`. The function is `standoff()`, `verification/runs/F4_runs/conversion_2026-08-25/grade_f4.py:381` |
| the gate value is taken at `snapshot_times(...)[-1]` | the gate value is the **mean over the last `N_SNAPSHOTS = 3`** — `grade_f4.py:708` builds `so`, `:712` grades the triple on `so[lv]["mean"]`, `:718` takes the band deviation from `so["fine"]["mean"]` |
| line 511 is that gate value | `:511` is inside **`control_p2`**, the *negative* planted-zero control (`:505`). It selects the last snapshot as the file to **plant into** at the θ ≈ 36° station, and then requires the θ = 0 gate value to come back **bit-identical**. It is a control, not a gate. |

The correction matters in the safe direction: the gate is a 3-sample mean, which
is *better* than the single endpoint reading I was told it was. It is still a
3-sample estimate, and §2 classifies it on that basis.

### 0.4 DOES NOT HOLD — **there are not eight sample sets on disk; there are three**

This is the load-bearing correction, and it is the one that decides §3.

My brief, and then my supervisor's mid-task amendment, both stated that F4 has
nine uniformly spaced checkpoints per case and that the Δ / 2Δ / 3Δ test is
therefore runnable — the amendment measured three cases directly and tabulated
gaps of 0.749979 … 0.750195.

**The gap measurement is correct. The thing measured is not the thing the gate
reads.** Those nine are **field time directories**. The frozen gate reader
`find_shock` (`grade_f4.py:114`) consumes
`postProcessing/sampleDict/<t>/r0_T_p_rho.xy` — a **400-point interpolated line
sample**, written by a `functionObject`, not a field directory. Measured across
**all eighteen case trees** (nine cases × two trees):

| | per case |
|---|---|
| field time directories | **9** — `0`, 0.749979, 1.499854, 2.2498543, 2.99985434, 3.749854339, 4.4998543386, 5.2498543386, 5.9998543386 |
| `postProcessing/sampleDict` times | **3** — 4.4998543386, 5.2498543386, 5.9998543386 |
| `postProcessing/surfaceSampleDict` times | **3** — the same three |

Every one of the eighteen reads `sampled=3 fielddirs=9`. Every
`r0_T_p_rho.xy` on disk under `verification/runs/F4_runs/` sits at one of 27
distinct times (9 cases × 3), all clustered at ≈ 4.5, ≈ 5.25 and ≈ 6.0.
**Nothing exists near 0.75, 1.5, 2.25, 3.0 or 3.75.** The record's own
`snapshot_times_used` field
(`verification/runs/F4_runs/cyl/M6.0/fine/result.json`) reads
`['4.4999677', '5.25008297', '6.000009029']` — the last three of **three**, not
of eight.

**Consequence.** Recomputing the frozen gate at 2Δ and 3Δ spacing requires
`postProcess -func sampleDict` on nine cases — **new compute**, which my brief
forbids, **and a write into a graded tree**, which it also forbids. Deriving the
standoff from the raw `rho` fields instead (they *are* present at all eight)
would be a **new instrument**, which my brief forbids a third time. So:

> **The Δ / 2Δ / 3Δ test is `BLOCKED` — not by policy, but by the artifact
> inventory. The temporal history it needs was never sampled.**

I did not run it and I am reporting no number from it. §3 reports the test that
*was* free, which turns out to answer the question anyway.

**This is the sixth instance of the amendment's own tally**, and it landed
inside the instruction issuing the warning. That is not a criticism of the
warning — it is the measure of how little this shape announces itself. Applying
the amendment's rule to itself: *state what two things you are comparing and
prove they are comparable before you read the difference.* Nine directories were
compared against a reader that consumes three.

---

## 1. THE CLASSIFICATION — SCAN METHOD FIRST

The method note is binding, so the instrument is reported before the territory.

**Narrow scan.** `git ls-tree -r HEAD --name-only`, filtered on grader/analyser
filename patterns (`grade_f*`, `analyse_f*`, `launch_f12*`, `roache_triple`).
**13 hits.**

**Broad scan.** `find . -name '*.py' | xargs grep -l` on
`roache_triple|triple_from_cells|grade_ladder` — a **content** scan over the
**disk**, including untracked and gitignored paths. **10 hits.**

**They disagreed, in both directions, and the reconciliation is the finding:**

* **In broad, not in narrow** — `scripts/parallel_batch.py`,
  `sdk/workflows/rae2822_case9.py`, `verification/runs/F12_runs/run_f12_rung.py`,
  `verification/runs/F2_runs/f2_ladder.py`, `T8_runs/analyse_t8.py`. Cause: the
  narrow scan matched **filenames**, and these do not look like graders. **A
  filename filter is not a classifier**; `sdk/workflows/rae2822_case9.py` is
  F12's actual grading path and no naming convention would have caught it.
* **In narrow, not in broad** — `grade_f3.py`, `grade_f7a.py`, `analyse_f13.py`,
  `analyse_f5b_physics.py`, `analyse_fields.py`,
  `analyse_f4_sigfpe_step01.py`. Cause: these **never reference
  `roache_triple.py` at all**. Two of them (F3, F13) implement their own triple
  arithmetic in-file. **A content scan for the shared instrument is blind to a
  grader that reimplements it** — and `grade_f3.py:377–395` does exactly that.
* **`verification/runs/F2_runs/f2_ladder.py` is on disk and NOT in HEAD**
  (`git cat-file -e HEAD:… → exists on disk, but not in 'HEAD'`; no commit
  touches it). The broad scan found it; a tracked-tree scan cannot. It grades
  nothing today, but it is a triple caller nobody's ledger lists.

**Neither scan alone was correct.** The union is the territory, and the
disagreement — not either result — is what produced the three findings above.
`git ls-files` was not used anywhere: it consults the shared index, measured
hiding 101 of 565 tracked `.md`.

---

## 2. THE CLASSIFICATION TABLE

Classes are the audit's: **A** = a relative tolerance on the last two
checkpoints or the last residual reading, which cannot distinguish convergence
from aliasing *in principle*; **B** = requires bit-identity or exactly-zero
change, so it fails in the safe direction; **C** = sustained-window floor + a
trend fit that rejects a growing series + an explicit stationarity test, refusing
below a minimum sample count.

**A fourth state was needed and is named rather than force-fitted: `ABSENT`** —
the grading path performs **no** iterative-convergence or plateau measurement at
all. `ABSENT` is not Class B: B fails safe *because it is a gate that rarely
passes*; `ABSENT` never refuses anything. Per `VERIFICATION_CHARTER.md` §9 and
`grade_ladder`'s own docstring, an absent measurement is recorded as absent and
**never as a pass** — a discipline `verification/runs/F12_runs/roache_triple_pin.json`
observes explicitly and the F3/F4 graders do not.

| # | gate / clause | file : line | class | graded rows resting on it |
|---|---|---|---|---|
| 1 | the Roache triple instrument | `scripts/roache_triple.py:133`, `:537`, `:581` | **not A/B/C** — computes no state, acts on the caller's | every triple row in the lab |
| 2 | F11 **plateau** — `\|q(final) − q(latest sample ≥ 250 it earlier)\| ≤ 1e-6` | `verification/runs/F11_runs/conversion_2026-08-25/grade_f11.py:768`, tol `:134`, gap `:135` | **A** (mitigated) | G-F11-1 … G-F11-6 — see §2.1 |
| 3 | F11 **iterative** — `check_convergence.classify()` | `grade_f11.py:749` → `scripts/check_convergence.py:308` | **A** (most mitigated in cfd) | G-F11-1 … G-F11-6 |
| 4 | F12 **gate B** — `"SIMPLE solution converged" in log_text` | `sdk/workflows/rae2822_case9.py:1134` | **A** (unmitigated) | see §2.2 |
| 5 | F12 **plateau** | — | **ABSENT, and correctly declared so** | `roache_triple_pin.json` `"plateau_states": null` + note |
| 6 | F4 iterative / plateau | `grade_f4.py:626–648` calls `RT.triple_from_cells`, **never** `grade_ladder` | **ABSENT, undeclared** | G-F4-1/2/3 × M6, M7, M8 — nine rows |
| 7 | F4 **gate value** — mean of the last 3 sample sets | `grade_f4.py:381`, `:708`, `:712`, `:718` | **weak C** — a real multi-sample mean, but n = 3, no trend fit, no stationarity test, no minimum-sample refusal | the same nine rows |
| 8 | F3 iterative / plateau | `grade_f3.py:377–395` — own triple arithmetic, no state | **ABSENT, undeclared** | G-F3-3 (`PASS`), G-F3-4 (`GATE FAIL`), 3 ungraded |
| 9 | F6a **(P-a)–(P-d)** | `verification/campaign/F6a_GREENBLATT_PREREGISTRATION.md:502–542` | **C — cfd's own registered Class C, and the best in the lab** | **none — not implemented**, `:1021` |
| 10 | `check_convergence.py` **signature 5**, `--monitor-regex` | `scripts/check_convergence.py:576`, `:664–:713` | **C** | none in cfd; the K0c family uses the same criterion |
| 11 | F5b window clauses | `analyse_f5b_physics.py:300` `window_mask` | **not a convergence gate** — a *period* window for a forced limit cycle | — |
| 12 | F7a, F13 | `grade_f7a.py` (98 lines), `analyse_f13.py` (179) | **ABSENT** — no convergence or plateau clause of any kind | — |
| 13 | `F2_runs/f2_ladder.py` | untracked, not in HEAD | **unclassified — grades nothing today** | none |

**A correction to my brief's scope line, item 11.** I was asked to classify
*"the F5b physics reader's plateau clauses P-a through P-d"*. **`(P-a)`–`(P-d)`
are not in F5b.** They are §3.1 of the **F6a** Greenblatt pre-registration
(row 9). `analyse_f5b_physics.py` contains no string `P-a`…`P-d` and no plateau
clause; its `window_mask` is a one-period analysis window for a *pitching*
(deliberately unsteady) case, where flatness would be a defect, not a gate.

### 2.1 The F11 rows — exposed by design, and **UNJUDGED**, not indicted

All six F11 gate rows are **`NOT A RESULT`**
(`verification/runs/F11_runs/conversion_2026-08-25/F11_CONVERSION_GRADED.json`),
and in every case the reason is the plateau clause, not the triple: each row's
`states` reads `['CONVERGING']` and each `band_verdict` reads `PASS`, while the
row verdict is `NOT A RESULT` — *"levels coarse[,medium] are not iteratively
converged or not plateaued; no grid claim can be made from this triple"*. The
Class A clause is currently **producing refusals, not passes**:
`coarse` reads `UNMEASURED` on G-F11-1/2/3 and `NOT_PLATEAUED` on G-F11-4/5/6;
`medium` reads `NOT_PLATEAUED` on four of six.

**So no F11 `PASS` rests on the Class A clause — there are no F11 passes.**
Where the exposure is real is the `fine` level, which reads `PLATEAUED` on all
six from a drift of **6.9e-08** between iterations **5000 and 5285** — a
**two-point comparison across a 285-iteration gap**. If that series were ringing
with a period near 285 iterations, those two points would sample a similar phase
and the drift would be small for the wrong reason. **I did not test whether it
is ringing, and I am not claiming it is.** The clause is **structurally Class A**
and the `fine` plateau readings are **`UNJUDGED`: not shown clean, not shown
exposed.** That phrasing is the amendment's and it is exact.

Two mitigations are real and should be credited: the **250-iteration minimum
gap** (`:135`) means this is not a "last two checkpoints" test, and the
**`UNMEASURED` path** (`:800–:812`) refuses rather than falling back — *"an
unevaluated step is not a passed one"*, and the docstring explicitly refuses the
tempting fallback to the last periodic sample. That refusal is Class C
behaviour bolted to a Class A criterion.

### 2.2 The F12 gate-B row

`solver_converged()` is a substring test. `simpleFoam` prints
`SIMPLE solution converged in N iterations` the **first** time every initial
residual falls under `residualControl` — a **single-iteration threshold
crossing**, which is precisely the T8 shape: 228 consecutive iterations under
1e-6, then never again, would still print it. It cannot un-fire.
**Class A, and the least mitigated in cfd's territory** — F11 at least routes the
same question through `check_convergence.py`.

Two things keep this from being an indictment. `roache_triple_pin.json`
`"grades_nothing": true, "moves_no_gate": true` — the pin grades nothing. And
cfd has **already written the fix**: F6a's `(P-a)` is exactly this clause
repaired — *"`SIMPLE solution converged in N iterations` with **N < the
registered `endTime` cap**. Reaching the cap is not convergence"* — with the
supervisor's ADDENDUM 3 ruling `(P-a)` governing.

### 2.3 The finding that surprised me most: **`ABSENT` outnumbers Class A**

**cfd's two largest graded conversions perform no step-(a) measurement at all.**
`grade_f4.py` calls `RT.triple_from_cells` (`:629`), not `RT.grade_ladder` —
so rule 5 clause (a) is never reachable for F4's nine rows. `grade_f3.py`
computes its own `klass` at `:377–:395` and hands the triple no states either.
Grepping `verification/campaign/F4_CONVERSION_PREREGISTRATION.md` for
`plateau|iterative|steady` returns **nothing**: the absence is registered by
omission, not by decision.

This is not the same defect as Class A and is arguably worse, because a Class A
gate at least refuses sometimes. **It is still not an indictment.** F3 and F4 are
transient solvers run to a fixed absolute `endTime` with a full rule-4 completion
rule (`grade_f3.py:158–195`, `grade_f4.py:148`), which is a real and checked
admissibility condition — it is simply **not a statement that the answer stopped
moving**. F4's nine rows are eight `NOT A RESULT` and one `CONVERGING`; F3's two
live rows are `G-F3-3 PASS` and `G-F3-4 GATE FAIL`. **All keep their verdicts.**
What is owed is a **record beside them** saying step (a) was never measured — the
discipline F12's pin already keeps and these two do not.

---

## 3. THE DIAGNOSTIC — what was free, and what it says

Evidence: `verification/runs/F4_runs/checkpoint_aliasing_2026-08-25/`
(`checkpoint_aliasing.py`, `checkpoint_aliasing.json`, `NOTE.md`).
**Grades nothing. Moves no verdict.** The frozen `grade_f4.py`
(HEAD blob `f51961435729558dc768d89e429c1818e8ae1da6`) is **imported**, not
copied and not edited; `grade_all` is never called, so its production-tree guard
is neither touched nor worked around; nothing is written into either graded tree.

**Two departures from `grade_f4.standoff()`, both declared in the file.**
(1) every sampled time is enumerated rather than `snapshot_times()`'s last three,
because that truncation is the variable under test; (2) a censored snapshot is
**excluded and counted** rather than refusing the whole case, since a refusal
would end the diagnostic at the first censored read. **The censoring rule itself
is unchanged.**

**Controls first, both passed.** The frozen `control_p1` planted rho spikes at
sample indices 137 and 300; `find_shock` located 138 and 301 (a single-point
spike peaks at the flanking sample). A second control plants at index **399** and
confirms the endpoint guard **would fire** — *the guard's never firing on the
graded station below is only evidence because the guard was shown able to fire.*
Both use `raise SystemExit`, never `assert`, so `python3 -O` cannot disable them
(the exposure the amendment `665935ea` §3 ruled on).

**Reproduction control.** The mean-of-last-3 basis reproduces the recorded
`G-F4-1` states exactly — `OSCILLATORY` at M6.0, M7.0 and M8.0, matching
`F4_CONVERSION_GRADE.json`. The two trees are byte-identical in every standoff
value, which is a reproduction fact worth recording on its own.

### 3.1 The hypothesis: **refuted as stated, and a sharper defect found**

My supervisor's hypothesis was **temporal phase aliasing** contaminating a mesh
triple, and he expected the 2026-07-28 detector diagnosis to survive.

**The detector diagnosis survives, and the station census confirms it
independently on disk** rather than repeating the record: across 27 reads per
station, `r5` is censored **27 of 27** (pinned at index 399, the domain edge) and
`r4` **12 of 27**. That is the record's *"pinning at 399 at θ ≈ 60°"*, measured.
**The graded station `r0` is censored 0 of 27** — so censoring does not cause the
`OSCILLATORY` rows.

**But the triple state is not invariant to checkpoint choice.** At **M7.0**:

| basis | state | e21 | e32 |
|---|---|---|---|
| single checkpoint 1 | `OSCILLATORY` | +13.00 q | −8.00 q |
| single checkpoint 2 | `EXACT` | +0.00 q | +4.00 q |
| single checkpoint 3 | `OSCILLATORY` | +5.00 q | −3.00 q |
| mean of last **2** | **`CONVERGING`, order 2.322** | +2.50 q | **+0.50 q** |
| mean of last 3 — **the graded basis** | `OSCILLATORY` | +6.00 q | −2.33 q |

**So my supervisor's hypothesis is not dead — the state does move. But the
mechanism is not phase aliasing, and I cannot test phase on three samples.**

`find_shock` is an `argmax` over a **fixed 400-point line** spanning `[0, 0.7]`
**identically at every mesh level**, so the detected standoff is **quantised to
q = 1.754386e-03** and can take only 400 values. That `CONVERGING` at M7.0 is
carried by **e32 = +0.50 q — half a detector sample.** An observed order of 2.322
fitted across half a quantum is not a measurement. The same quantisation produces
the two `EXACT` states, where two levels return the *identical* detected locus
and the Richardson exponent is undefined — `roache_triple.gci_equal:243` raises
`math domain error` rather than inventing a number, which is correct behaviour
that `grade_f4.py` happens never to have triggered.

### 3.2 The deeper finding — the pre-registration's own reasoning, one gate to the left

`grade_f4.standoff_band_pct` (`:446`) transcribes prereg §5.1: the band is **one
local radial cell**, because *"two shock positions closer together than dr
produce the SAME detected locus"* and a deviation below `dr` *"is below the
instrument's resolution and is not a resolved disagreement."*

**That reasoning was applied to the band (G-F4-2) and never to the triple
(G-F4-1).** Applied to the triple — where the **signs** of `e21` and `e32` are
what decide `CONVERGING` versus `OSCILLATORY` — against a finest local cell of
7.75–7.95 q:

| graded row | state | e21 | resolved? | e32 | resolved? |
|---|---|---|---|---|---|
| G-F4-1-M6.0 | `OSCILLATORY` | −0.67 q | **no** | +6.67 q | **no** |
| G-F4-1-M7.0 | `OSCILLATORY` | +6.00 q | **no** | −2.33 q | **no** |
| G-F4-1-M8.0 | `OSCILLATORY` | −19.67 q | yes | +5.67 q | **no** |

> **Five of the six level-to-level differences on the graded standoff triples are
> smaller than one local fine cell — below the resolution the pre-registration
> itself defines.** The signs deciding the triple state are read off differences
> that document calls unresolved.

**The band derivation is sound and is not criticised**: ±7.75 q at fine is
comfortably *larger* than the 1 q detector quantum, so the band is not finer than
its instrument.

**What this changes: nothing, and deliberately.** All three `G-F4-1` rows are
`NOT A RESULT` and stay `NOT A RESULT`. The M7.0 `CONVERGING` appears only under
an averaging window nobody registered and I am not proposing; rule 5 is one-way
and rule 2 closed these gates at first compute. **The honest restatement is that
at M6.0 and M7.0 the triple is better described as `UNRESOLVED BY THE DETECTOR`
than as oscillatory — and both land on the same verdict, `NOT A RESULT`.** M8.0's
`OSCILLATORY` is robust: opposite signs at every checkpoint and every window,
with `e21` at 14–27 q.

**For the next F4-shaped registration**, the actionable item is not the gate but
the instrument: **400 points over `[0, 0.7]` cannot resolve a mesh triple whose
levels differ by less than one local cell.** A finer sample line costs nothing at
solve time and is a `functionObject` setting.

---

## 4. DRAFT — the Class C shape for cfd's next registrations

**A draft into the supervisor's ruling, not a ruling. Nothing here is retrofitted
into any frozen pre-registration** — rule 2 closes gates at first compute, and
none of §2's rows is reopened.

Heat-transfer is ruling the same for their territory. **cfd should land the same
shape, and cfd already has it registered**: F6a §3.1 `(P-a)`–`(P-d)` is a Class C
gate written by this team, and `analyse_e4a2.py` / `analyse_k0cx.py` are the
working implementations. The four elements below are stated in the union of those
three so that one shape lands, not two.

**C-1 — SUSTAINED FLOOR, never one interval.** The criterion holds for **each of
the last N consecutive intervals**. *"One lucky interval cannot pass the gate"* —
`E4a2_registered.json` `convergence_gate.C1`, `sustained_intervals: 3`,
implemented `analyse_e4a2.py:300–306`. K0cX's form is a **peak-to-peak spread
over a fixed iteration window** — 400 iterations sampled every 50
(`analyse_k0cx.py:92`, `:644–:660`). Both are sustained-window; **cfd should
prefer K0cX's peak-to-peak-over-fixed-window**, because
`scripts/check_convergence.py:75–83` already refuses the two alternatives *in
writing on every run*: an endpoint difference aliases against a decaying
oscillation whose period is near the window, and a fraction-of-the-run window
silently loosens as a run is extended.

**C-2 — A TREND FIT THAT REJECTS A GROWING SERIES.** A least-squares fit of
`log10(r)` against iteration over the last third; **GROWING** iff `R² ≥ 0.90`
**and** slope `≥ +0.01` decades/1000, and a growing series does not pass *even
while it is under the floor* (`analyse_e4a2.py:247–270`,
`E4a2_registered.json.C2`). **Read growth from the fitted trend, never from one
bounce** — E4a's own series grew 1.54× across three intervals while sitting three
decades inside its floor, and gating on that bounce would void a rung for
oscillating *at* a floor. F6a's `(P-d)` is the same idea in its own terms: across
10 samples the sign of the successive increment **may alternate at most once**;
two or more alternations ⇒ oscillatory ⇒ `NOT A RESULT`.

**C-3 — AN EXPLICIT STATIONARITY TEST ON THE GATED QUANTITY ITSELF.** This is
the clause that is not a residual statement. F6a `(P-c)` puts it plainly: *"A
residual floor is a statement about the linear solve, not about the answer"*, so
**the answer is sampled** and its peak-to-peak spread must be **≤ 10 % of that
quantity's gate half-width**. E4a2's `C3` is the field-space form: `|Q(t_K) −
Q(t_half)| / |Q(t_K)| ≤ 1e-7` across **half the run** on the frozen reader's own
quantity, because *"C1 and C2 are CHANGE criteria and L-243 is explicit that
change bounds nothing about distance to a fixed point"*. **Tie the tolerance to
the gate band**, as F6a does — a functional still moving by a tenth of the band
is not plateaued whatever the residuals say.

**C-4 — REFUSE BELOW A MINIMUM SAMPLE COUNT; never degrade.** `min_checkpoints`
is registered and a shortfall is **exit 2**, *"not a degraded reading"*
(`E4a2_registered.json`, enforced `analyse_e4a2.py:202–204`). K0cX refuses under
**nine** samples in its registered window — *"The criterion is not loosened to fit
the data available"* (`analyse_k0cx.py:658–662`). F6a refuses under **10**. And
the registration must be checked **at freeze** to produce enough samples:
`analyse_e4a2.py:792` asserts `endTime // writeInterval >= MIN_CKPT` in the
selftest, before any solve.

**Three additions cfd's own week earned, offered for the supervisor's judgement:**

* **C-5 — the ordering rule, registered so it cannot be re-ordered afterwards.**
  F6a §3.2: *"PLATEAU IS EVALUATED FIRST AND ITS RESULT IS BINDING. A deviation
  inside the band on a run that is NOT plateaued is `NOT A RESULT` — it is NOT a
  `PASS`."*
* **C-6 — `ABSENT` is declared, never left to inference.** §2.3's finding. Where
  a registration deliberately carries no plateau clause, the grade record must
  say so in the words `roache_triple_pin.json` already uses: *"ABSENT, not
  passed… an absent measurement [is] recorded as absent and never as a pass."*
  **This is the one item in §4 that also applies backwards** — not as a regrade,
  but as a note beside F3's and F4's existing rows.
* **C-7 — declare the instrument's resolution beside the gate.** §3.2's finding.
  Where the gated quantity comes from a quantised detector, the registration
  states the quantum and requires the triple's `e21`/`e32` to **exceed** it, on
  the same reasoning F4's prereg §5.1 already used for its band. **A sign is not
  a measurement when the difference carrying it is half a sample.**

**Sample-set provenance, adopted from the amendment and made concrete by §0.4:**
a comparator that subsamples checkpoints must **print the times it actually
used**, never the times requested. Nine directories on disk are not nine samples
if the reader consumes three.

---

## 5. WHAT I COULD NOT VERIFY — stated plainly

* **The Δ / 2Δ / 3Δ test was not run.** `BLOCKED` on the artifact inventory
  (§0.4). I report no number from it.
* **Whether F4's standoff series is actually ringing.** Three sample sets cannot
  resolve a phase. §3 shows the triple state moves with checkpoint choice and
  identifies quantisation as sufficient to explain it; it does **not** exclude a
  temporal component, and I make no claim either way.
* **Whether F11's `fine` plateau readings are aliased.** `UNJUDGED` — not shown
  clean, not shown exposed. Testing it needs the `centerlineSeries` history read
  as a series, which I did not do.
* **`scripts/parallel_batch.py` and `T8_runs/analyse_t8.py`** appear in the broad
  scan and are **not classified here**: the first is infrastructure, the second is
  heat-transfer's territory and is the live case in their audit.
* **`F2_runs/f2_ladder.py`** is untracked; I confirmed it grades nothing today
  and did not read it further.
* **F7a and F13** are marked `ABSENT` from a keyword scan of two short files
  (98 and 179 lines) plus their lack of any `roache_triple` reference. That is a
  weaker read than the line-by-line ones above and is labelled as such.
