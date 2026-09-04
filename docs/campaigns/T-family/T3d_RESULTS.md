# T3d — RESULTS. The run completed, the marker was earned, and the **grading path refused on its own registered inputs**: the pinned builder never wrote what the pinned grader reads

**RUNG VERDICT: `NOT A RESULT`.**

> **The verdict is taken from the registered path's own refusal shape and is NOT composed by hand.**
> `analyse_t3d.py` **REFUSED (exit 2)** at `analyse_t3.py:461`, **upstream of its rows block**:
>
> ```
> REFUSE: H absent from .../T3_runs/R_fx/CASE.txt
> ```
>
> **No graded row was reached.** That is the same shape as **T15**, whose comparator refused
> upstream of its rows block and whose four registered rows were recorded `NOT A RESULT`
> *because none was reached* (`T15_RESULTS.md:3`, `:6`). This record follows that precedent,
> ratified for T3d before it was written.

**Why `NOT A RESULT` and not `PENDING`.** `PENDING` is the display/queue state for *not yet run*
(`CLAUDE.md` rule 1; `VERIFICATION_CHARTER` §9). T3d **ran**. Calling it `PENDING` would hide
**4,723.200 core-minutes** of spent compute behind a word that means "not started" — the same
reasoning T15 gave for its own 1,196 (`T15_RESULTS.md:12-15`). The rung held at `PENDING`
legitimately while its completion marker was unobtainable; **that condition was lifted by
`VERIFICATION_CHARTER` §2ao, and what remains is not a queue state.**

---

## 1. THE FULL PATH, IN ORDER, WITH WHAT EACH STEP ESTABLISHED

| step | outcome |
|---|---|
| **run** | **COMPLETE.** 24,000 of 24,000 iterations, `End` + `Finalising parallel run`, ended **2026-09-04T03:55:34Z** |
| **rule 4** | **ALL SIX CLAUSES HOLD** (§3) |
| **completion marker** | **EARNED, not asserted** — written by the frozen instrument under §2ao (§2) |
| **D-J1 obligation** | **DISCHARGED. D-J1 did NOT fire** (§4) |
| **iterative convergence** | **`|U|` is NOT CONVERGED at 3.69× tolerance** (§4) |
| **grading path** | **REFUSED (exit 2) on a missing input its own registered builder never wrote** (§5) |

**Two independent reasons this rung yields no graded row, and they must not be conflated:**
the **grading path could not execute at all** (§5, a registration defect), and **had it executed,
rule 5 clause (1) would have made the fine level `NOT A RESULT` anyway** on `|U|`'s
non-convergence (§4). **The second is physics; the first is bookkeeping. The verdict rests on
the first, because that is the one the registered path actually produced.**

---

## 2. THE COMPLETION MARKER — EARNED UNDER §2ao, NOT ASSERTED

`DONE.R_fx` had **no registered producer**. Heat-transfer petitioned for one
(`T3d_DONE_MARKER_2D1_PETITION.md`, `b0ac3ac6`) and **the petition was REFUSED as unnecessary**
by `VERIFICATION_CHARTER` **§2ao** (charter v1.59, `0525984b`; notice `a255b897`), which unblocked
the result by a better route **that the petitioner had itself disclosed against its own interest**.

Invocation, recorded per the ruling's condition 1 at
`verification/runs/T-family/T3_runs/T3d_MARK_DONE_R_fx_OUTPUT.txt`:

```
python3 mark_done_t3.py --root verification/runs/T-family/T3_runs R_fx
→ 1/1 cases meet the strict completion rule        (exit 0)
```

`mark_done_t3.py` was **frozen 2026-08-21, before `R_fx` existed**, is byte-identical to HEAD
(`5da28c73`), **applies** rule 4's clauses from the case's own artifacts, and is **stricter than
the constitution** — `:34` requires `phi` on top of rule 4's thermal seven. **No new file, no
registered sha moved, `analyse_t3d.py` byte-untouched.**

---

## 3. RULE 4 — ALL SIX CLAUSES, APPLIED AND SHOWN

1. **`rc = 0`** (`STATUS.R_fx`).
2. **`End`** — exactly one `^End$` in the 23.3 MB `log.solve`; final line `Finalising parallel run`.
3. **last time == `endTime`** — `endTime = 24000` parsed from the case's **own** `system/controlDict`; time directories `0, 22000, 24000`.
4. **fields at `24000/`** — all seven of `T U p_rgh alphat nut k omega`; `turbulenceProperties` reads `simulationType RAS`, `RASModel kOmegaSST`. **`phi` also present**, which the marker requires and `CLAUDE.md` rule 4's list omits.
5. **`ExecutionTime` count** 24,000 against `endTime` 24,000 — **difference exactly 0**.
6. **age guard** — `0/T` **2026-09-03T18:04:05Z** against `0.orig/T` **17:23:41Z**; `0/T` is the dating file, confirmed on disk against `started_utc 18:04:57Z`. All eight fields at `24000/` newer by **≈ +35,486 s**.

**Beyond the six: `reconstructpar_rc = 0`** — live, because `R_fx` ran decomposed on 8 ranks.

---

## 4. THE D-J1 OBLIGATION IS DISCHARGED — AND THE ANSWER VINDICATES THE OBLIGATION, NOT THE DEFECT

This board carried a binding obligation from 2026-09-03T19:30:29Z: **T3d may not be closed until
`R_fx`'s own measured `field_range` for both `T` and `|U|`, at the graded checkpoint pair, is
recorded beside the verdict.** Discharged here.

Measured by `probe_djone_denominator.py` (`59bdf2db`), which **imports the frozen readers
unmodified** — `analyse_t1c.iterative_convergence` and `analyse_t3.iterative_convergence_vector`,
the same functions the grader calls — and refuses at exit 2 unless its own three-limb planted-zero
control passes first:

| field | `field_range` | `max_change` | `relative` | `tol` | `state` | pair |
|---|---:|---:|---:|---:|---|---|
| `T` | **50.2889** | 4.03886e-05 | 8.03132e-07 | 1e-06 | `CONVERGED` | (22000, 24000) |
| **`\|U\|`** | **11.0325** | 4.0703e-05 | **3.68937e-06** | 1e-06 | **`NOT_CONVERGED`** | (22000, 24000) |

**BRANCH TAKEN: `rng > 0` ON BOTH FIELDS. D-J1 DID NOT FIRE.** The obligation's own rule —
*if either range is `0.0` or is not measurable, the level is `NOT A RESULT` and P-1 is UNANSWERED,
not answered `CONVERGED`* — **does not apply, because its condition is not met.** The ratio is a
real ratio on each field.

**The control passed before any level was probed:** LIMB W reproduced `R_m` 51.2959 / 11.0155 and
`R_f` 50.7293 / 11.0257 against independently recorded values; LIMB P showed a true zero on
identical copies then read a 1.234e-03 K plant back **from disk** within 32 ulp; LIMB D reproduced
D-J1 itself (dmax 10.0 K certified `CONVERGED` at rng 0.0). **The non-zeros above therefore come
from a reader demonstrated able to see both a non-zero and a zero.**

> **THE PHYSICS: `|U|` IS NOT ITERATIVELY CONVERGED, 3.69× OVER TOLERANCE.** This is the **honest**
> branch reporting a **genuine** failure, not a defect's output. `analyse_t3.py:627-628` composes
> `convergence_state` to `NOT_CONVERGED` whenever the `U` limb is, and `analyse_t3d.py:200` gates
> the ladder on that field. **Under rule 5 clause (1) a level not iteratively converged is
> `NOT A RESULT` whatever its value.**
>
> **The obligation was worth keeping.** The point was never that D-J1 *would* fire — it was that
> `CONVERGED` must not be written without its denominator beside it. **Given a real denominator,
> the reader says `NOT_CONVERGED`.**

**`T` DID converge** (8.03e-07 ≤ 1e-06), so **registered prediction P-1, which is stated over `T`
alone (`T3d_PREREGISTRATION.md:54`), is MET on its own terms.** It does not rescue the rung: the
ladder gates on the composed `convergence_state`, not on `T` alone.

---

## 5. ⚠ THE REGISTRATION DEFECT — THE PINNED BUILDER AND THE PINNED GRADER COULD NEVER HAVE SATISFIED EACH OTHER

**`build_t3d.py:89` writes `CASE.txt` as six lines of prose with NO key-value pairs of any kind:**

```
R_fx -- T3d continuation of R_ff
seeded from R_ff/118000 by build_t3d.py
mesh IDENTICAL to R_ff (not a new level)
endTime 24000 = ADDITIONAL iterations; the counter restarts at 0
writeInterval 2000, purgeWrite unchanged from R_ff
registration: docs/campaigns/T-family/T3d_PREREGISTRATION.md
```

**`analyse_t3.py:461-468` reads SEVEN NUMERIC KEYS from that same file** — `H`, `nu`, `Pr`, `Prt`,
`dTdn_wall`, `T_in`, `U_in`, `endTime` — and refuses on the first it cannot find.

The three siblings `R_m`, `R_f` and `R_ff` **all** carry the structured builder block (`H 0.038 m`,
`nu 1.5e-05 m2/s`, `Pr 0.71`, …) because **a different builder wrote them**. Only `R_fx` — the level
T3d exists to add — came from `build_t3d.py`.

**BOTH FILES ARE SHA-PINNED IN THE SAME FROZEN REGISTRATION** (`T3d_PREREGISTRATION.md` §6) and
**both are byte-identical to HEAD**: `build_t3d.py` `f550319a`, `analyse_t3d.py` `980ae3b2`.
**Nothing drifted. The incompatibility was present at the moment of freezing, and no outcome of
the run could have been graded.**

**THIS IS T19's DEFECT WEARING A DIFFERENT HAT.** T19's *completion rule* was unsatisfiable from
birth because `residualControl` and the endTime-count clauses were mutually exclusive; T3d's
*grading path* is unsatisfiable from birth because the pinned builder does not write the inputs the
pinned grader reads. **T19 cost 29.133 core-min to discover. T3d cost 4,723.200.**

> ### WHAT WAS NOT DONE, AND WHY THE TEMPTATION IS NAMED RATHER THAN LEFT UNSTATED
> **No key was added to `CASE.txt`.** The value is knowable — the mesh is **identical to `R_ff`**,
> whose `CASE.txt` says `H 0.038 m` — **and that is exactly why the refusal had to be obeyed.**
> §2ao's own distinction governs and cuts the other way here: an **attestation** applies checks to
> artifacts the case already carries; **writing a missing key into the artifact is not attestation,
> it is authorship.** Supplying a grading input by hand after the run is fabricating the
> comparator's evidence, whatever the provenance of the number. **Ruling condition 2 — *if it
> refuses, that refusal is the finding and must not be worked around* — is obeyed.**

**The refusal is credible because the instrument was working when it refused:** the rule-3
planted-zero control (`P-2`) on `R_f` **PASSED** immediately before it — limb A and limb B both
true, `read_back_delta = 0.0012340000000108`, `N_ULP = 32`.

---

## 6. RULE 12 — ACTUAL, MEASURED

**4,723.200 core-min** (`STATUS.R_fx`: 35,424 wall s × 8 ranks ÷ 60, exact) against the frozen
**POINT 5,442.1** — **ratio 0.8679, 13.21 % UNDER**, **28.93 %** of the 16,326 cap.
**$4.0383 vs $4.6530, both DERIVED at $0.0513/core-h, reported-by-owner, never measured** — this
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).

**Attribution measured, not guessed: contention, in the favourable direction.** The prediction's
basis was `R_ff`'s **whole-run average** of 0.226755 core-min/iteration, taken on a **saturated**
box (%idle 10.96 on 08-27); `R_fx` met a lighter box and ran at **0.196800**. **The misprediction
is in the basis — a whole-run average carries its load conditions into a constant.**

**NO WASTE** — one launch, all four rcs zero, nothing discarded, no retry. Nothing folded into the
ratio (`COMPUTE_BUDGET_CHARTER` §6).

**Row `C-20260904T150910.320385Z-a636135b` already exists and is NOT duplicated here.**

---

## 7. WHAT THIS RECORD DOES **NOT** ESTABLISH

- **It is not a measurement of the T3 ladder.** No graded row was reached, so there is **no
  observed order, no GCI, no Richardson extrapolate, and no discretisation bound on anything.**
  Rule 5 was never reached past clause (1).
- **It does not establish that `|U|` cannot converge on this case.** It establishes that `|U|` had
  **not** converged after 24,000 additional iterations, at one checkpoint pair. **Whether the
  non-convergence is settling or persistent is UNDETERMINED and cannot be determined from what is
  on disk:** `purgeWrite 2` left only `22000/` and `24000/`, so **there is no third pair against
  which to test a trend.**
- **It does not establish that `build_t3d.py` is wrong anywhere else.** One defect is measured, in
  one function, on one output file. **No sweep of other builders was run and none is claimed.**
- **It is not a validation of any physics.** Nothing here is compared to an experiment.

---

## 8. THE SUCCESSOR — MANDATORY, AND UNDER §2an THIS ROUTES RATHER THAN TERMINATES

Under Sanaa's 2026-09-04 mandatory-completion order a `NOT A RESULT` is **a waypoint, not a resting
place**, and under `VERIFICATION_CHARTER` **§2an** (`c46c196f`) with `NONCONVERGENCE_STANDARD` §4 a
model-form failure **routes into the ladder rather than terminating the item**.

**`T3e` carries three defects forward, all of them ours:**

1. **The builder must write the structured `CASE.txt` its grader reads** — and the
   **builder-grader pair is driven end-to-end on a synthetic case BEFORE freezing**. T3d's freeze
   rehearsed neither against the other.
2. **The completion-marker producer is registered in the pre-registration, before compute**, per
   §2ao's own closing instruction. T3d registered none, eight days after the same team registered
   one correctly for `R_ff` under a `PRE-FIRST-COMPUTE` heading.
3. **The settling-versus-persistent question gets a registered checkpoint** — `purgeWrite` set so
   that **at least three consecutive pairs survive**, which is the minimum that can distinguish a
   decaying trend from a stalled one.

**The 4,723.200 core-min this rung spent is the argument for spending a few more properly**, not
against it.

---

**Artifacts of record.** `verification/runs/T-family/T3_runs/` — `STATUS.R_fx`, `DONE.R_fx`,
`T3d_MARK_DONE_R_fx_OUTPUT.txt`, `T3d_GRADE_STDOUT.txt`, `log.solve`, `22000/`, `24000/`,
`probe_djone_denominator.py`. **No `gate_t3d.json` exists**: `analyse_t3d.py` refused upstream of
its `json.dump` at `:413`, so the verdict rests on the landed stdout and on nothing else — stated
as a limitation of the record, not as a defect in it.

---

## AMENDMENT 1 — 2026-09-04 — §5's KEY LIST IS WRONG BY ONE, CORRECTED AGAINST THIS RECORD'S OWN INTEREST

**Appended by `heat-transfer-supervisor`. Lines whose number changed above this section: 0.**
**No verdict moves. `NOT A RESULT` stands, and the defect stands.**

`VERIFICATION_CHARTER` **§2ap.6** (v1.61, `156906fa`) re-measured §5's claim against the real
`R_fx/CASE.txt` and **corrected it by one key, in the direction that makes this record's own
finding slightly smaller.** Recorded here because a record that quietly keeps an overstated
figure is worse than one that never made it.

**§5 above states that `analyse_t3.py:461-468` reads seven numeric keys — `H`, `nu`, `Pr`, `Prt`,
`dTdn_wall`, `T_in`, `U_in`, `endTime` — and implies all seven are unsatisfiable from the prose
`CASE.txt`. `endTime` IS SATISFIABLE.** The builder's fourth prose line begins
`endTime 24000 = ADDITIONAL iterations`, so `line.startswith("endTime ")` matches and
`.split()[0]` parses as `24000.0`. **The COUNT of seven keys read was right; the LIST of
unsatisfiable ones was wrong by one — six, not seven.**

**`H` is the key that refuses first**, which is what the recorded refusal string already said and
what §5's quoted output already showed. **Nothing else in §5 changes, the mechanism is unaltered,
and the verdict is untouched.**

**AND ONE THING §2ap.1 ADDS THAT THIS RECORD DID NOT SEE — THE DEFECT WAS MASKED BEHIND ANOTHER
ONE.** The missing `DONE.R_fx` producer (§2ao) refused **first**, so the builder-grader
incompatibility **was not discoverable until that blocker was cleared, which took a charter
ruling.** ***A registration can carry two independent fatal defects, and the outer one hides the
inner one until it is resolved. Clearing a blocker is not evidence that a case is gradeable.***
That is a better statement of what happened here than §1's table gives, and it is adopted.
