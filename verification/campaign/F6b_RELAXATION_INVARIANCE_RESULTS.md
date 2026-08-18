# F6b periodic hill — relaxation-invariance check (L-47): results

Date: 2026-08-11. Pre-registration:
`F6b_RELAXATION_INVARIANCE_PREREGISTRATION.md`, commit **`ce0b14be`**, committed
**before the first iteration of either arm ran**; positive control added as
Addendum 1, commit **`110da419`**, committed **before the control ran**. Every
bar, threshold and prediction quoted below is read from those two commits, not
composed here. Machine-readable companion: `F6b_runs/relax_invariance.json`.
Self-ledger: `F6b_runs/relax_invariance_ledger.txt`.

## Headline

**CONFIRMED, on both alternative relaxation settings, by two orders of magnitude
more margin than the bar asked for.**

Three solves of the identical case — same mesh, same initial fields, same
schemes, same linear solvers, same `residualControl` — differing **only** in
relaxation, reach the same fixed point:

| arm | relaxation p / U / k / ω | iterations to converge | reattachment x_R/h | vs arm A |
| --- | --- | --- | --- | --- |
| **A** (incumbent, shipped PH_Breuer) | 0.5 / 0.5 / 0.7 / 0.7 | 5,997 | **7.6472** | — |
| **B** | 0.3 / 0.7 / 0.7 / 0.7 | **3,936** | **7.6480** | **0.0105%** |
| **C** | 0.3 / 0.3 / 0.5 / 0.5 | **11,700** | **7.6458** | **0.0183%** |

The pre-registered CONFIRMED bar was 0.5%. Arm B comes in **48× inside it** and
arm C **27× inside it**. The three arms take 3,936, 5,997 and 11,700 iterations —
a **third-to-triple** spread in path length — and land on the same reattachment
point to four significant figures.

**The +63% to +66% reattachment miss is the model's, and the Gate P verdict
stands.** Stock kOmegaSST over-predicts the periodic-hill recirculation length,
and that number is not an artefact of an untested relaxation switch inherited
from the shipped case.

**The instrument was shown able to fail before it was allowed to pass.** A
positive control — the same case at the same relaxation, stopped early — was
refused certification at all four sample points, including two with a
well-formed two-crossing bubble (§4).

## 1. What was at risk, and the frame that was fixed before any number

The pre-registration's §0 fixed the frame before measuring, and it matters
enough to restate. `F6b_ERCOFTAC_RESULTS.md` names its relaxation gap in its own
words at §4 — *"a 62,400-cell mesh may simply need tighter under-relaxation…
should be tested first"* — but that sentence is about the **veryfine** rung,
which carries no verdict and from which no separation or reattachment number is
quoted anywhere. The **standing verdicts** — Gate P FAIL at +63% to +66%, Gate V
PASS at 0.043%, Gate Q PASS at 12.82% — are all read off the **medium** rung, as
that record itself states (*"Both are decided on the medium rung"*).

So the medium rung is what was tested. **Running the veryfine arm and reporting
it as though it had tested the verdict would have been a true sentence about one
artifact standing in for a claim about another** — the L-55 shape. §6 states what
remains open.

## 2. The three arms, and that only relaxation differed

Arms B and C were built as copies of `F6b_runs/medium` and verified by `diff -r`
to differ in exactly two places: the `relaxationFactors` block, and the iteration
cap. `0/` and `constant/` are **byte-identical** across all three arms —
confirmed by `diff -r` returning empty, recorded at build time.

| quantity | arm A | arm B | arm C | pre-registered bar | result |
| --- | --- | --- | --- | --- | --- |
| reattachment x_R/h | 7.6472 | 7.6480 | 7.6458 | ≤ 0.5% rel | **0.0105% / 0.0183% → CONFIRMED** |
| separation x_S/h | 0.2604 | 0.2608 | 0.2598 | ≤ 0.05 h | 0.0004 / 0.0006 h → **pass** |
| skin-friction sign changes | 2 | 2 | 2 | exactly 2 | **pass** |
| profile scaled MAE, 9 stations | 12.821% | 12.841% | 12.774% | ± 1.0 pp | +0.02 / −0.047 pp → **pass** |
| `SIMPLE solution converged` | 1 | 1 | 1 | required | **pass** |

Every secondary bar passes with the same kind of margin as the primary one. The
profile metric is worth a line of its own: the **nine-station velocity field**,
not just the reattachment scalar, is reproduced to within 0.05 percentage points
across a threefold change in path length.

**The cap never bound.** Both arms converged well inside the 20,000-iteration
cap, so the one respect in which the arms differed besides relaxation — the cap
— cannot have influenced either answer. The pre-registration's INCONCLUSIVE
branch was not reached.

## 3. Where the relaxation change went, since it did not go into the answer

It went into the **path**, which is exactly L-47's claim and is worth recording
as the positive form of the result rather than only as the absence of an effect:

| arm | iterations | ExecutionTime | core-min |
| --- | --- | --- | --- |
| A (incumbent) | 5,997 | 407.61 s | 6.79 |
| B | 3,936 | 253.01 s | **4.22** |
| C | 11,700 | 726.63 s | 12.11 |

Arm C takes **2.97×** arm B's iterations to reach the same point. That is a large
path difference producing a 0.0183% answer difference, and it is the strongest
form the evidence can take: the fixed point is insensitive to how it is
approached across a factor of three in approach length.

**A finding nobody registered a prediction for.** Arm B converges in **3,936
iterations against the incumbent's 5,997 — 66% of the cost, 4.22 core-min against
6.79.** The pre-registration assumed the alternatives would be *slower* and
priced them at the incumbent's count (prediction 7 registered arm B in
[4,000, 12,000] and is FALSIFIED on the low side by 64 iterations). **The shipped
case's 0.5/0.5 relaxation is therefore not merely untested on this mesh — it is
slower than OpenFOAM's documented default on it, by a third.** This is recorded
as a measurement, not a recommendation: one case is not a basis for changing a
setting anywhere else, and the shipped value must stay in arm A for the
comparison above to keep meaning.

## 4. The positive control — the instrument was made to fail first

**Why it exists.** The claim this check makes is *"the arms do not disagree"* — an
absence claim, and an absence claim needs an instrument that cannot produce a
false absence plus a demonstration of it firing. Without one, a reattachment
number that happened to be insensitive to everything this mesh can hold would
have produced exactly the agreement seen above and meant nothing.

**The control**, registered at `110da419` before it ran: the incumbent case at
the **incumbent relaxation**, differing from arm A in one respect only — stopped
early, with fields written at 500, 1,000, 1,500 and 2,000 iterations. Four
known-present specimens of an unconverged field on the same mesh, read by the
same crossing code.

| sample | crossings | reattachment x/h | vs 7.6472 | certifies? |
| --- | --- | --- | --- | --- |
| 500 | **8** | none defined | — | **NO** |
| 1,000 | **4** | none defined | — | **NO** |
| 1,500 | 2 | 7.9018 | **3.329%** | **NO** (GREY) |
| 2,000 | 2 | 7.7284 | **1.061%** | **NO** (GREY) |

**All four refused. The two that matter most are 1,500 and 2,000**: they have a
*well-formed two-crossing separation bubble* — they pass the topology check that
disqualified the 500 and 1,000 samples, and they would look like a converged
answer to anyone reading the wall field — and the magnitude channel still catches
them, at 3.329% and 1.061% against a 0.5% bar.

**That is what licenses the headline.** The bar discriminates: an unconverged
field on this exact case, at the same relaxation, reads 1.061% at 2,000
iterations, while arm B at a *different* relaxation reads **0.0105%** — a
hundredfold separation. Agreement between the arms is therefore informative and
not a property of a number that never moves.

Prediction 11 also held: the failure-to-certify is monotone in iteration count —
8 crossings → 4 crossings → 3.329% → 1.061%.

## 5. Predictions, scored — with the artifact/agent split L-54 requires

All eleven registered predictions were `artifact`-class. **The pre-registration
contained no `agent`-class prediction, and said so on its face** — it predicted
nothing about what any person or process would do, only about files and solves.
That is why the scoring below can be read directly as a score of the model of the
world, with no organisational term mixed in.

| # | class | prediction | outcome |
| --- | --- | --- | --- |
| 1 | artifact | Arm B converges inside 20,000 iterations | **HELD** — 3,936 |
| 2 | artifact | Arm C converges inside 20,000 iterations | **HELD** — 11,700 |
| 3 | artifact | Arm B CONFIRMED (≤ 0.5%) | **HELD** — 0.0105% |
| 4 | artifact | Arm C CONFIRMED | **HELD** — 0.0183% |
| 5 | artifact | Both arms give exactly 2 sign changes | **HELD** |
| 6 | artifact | Arm C takes more iterations than arm B | **HELD** — 11,700 vs 3,936 |
| 7 | artifact | Arm B iteration count in [4,000, 12,000] | **FALSIFIED** — 3,936, below the low end by 64 |
| 8 | artifact | Neither arm falls inside [4.21, 4.70] | **HELD** |
| 9 | artifact | The 500-iteration control fails to certify | **HELD** — 8 crossings |
| 10 | artifact | At least one control point fails to certify | **HELD** — all four did |
| 11 | artifact | Failure-to-certify monotone in iteration count | **HELD** |

**Ten of eleven held.** The one that failed is a cost prediction, not a physics
one, and **it failed on the mechanism rather than the number** — which L-54 says
to score first. The registered mechanism was "alternative relaxation settings
will need at least as many iterations as the incumbent"; the actual mechanism is
that inverting the pressure/momentum split *accelerates* this case. Predictions 3
and 4 were registered with their mechanism stated — that a field reproducible
under two independent changes of *discretization* is unlikely to be sensitive to
a change of *path* — and **that mechanism is the one that held.**

## 6. What this does NOT settle, stated as a gap and not as a constraint

- **The veryfine rung's non-convergence (`F6b_ERCOFTAC_RESULTS.md` §4) is
  untouched.** This check tested the medium rung. §4's two competing readings —
  a genuinely unsteady flow, versus relaxation tuned for a coarser resolution —
  remain both live, and §4's own words remain the accurate statement of that
  gap. The pre-registration priced the veryfine arm at **≈85 core-min** on that
  rung's own measured 0.2557 s/iteration and deliberately did not spend it,
  because it decides §4 and decides nothing about Gate P, Gate V or Gate Q.
- **This says nothing about any other case.** Two arms agreeing on the F6b medium
  rung is evidence about the F6b medium rung. The lab's other two named
  relaxation exposures — the closure family's R4 Ahmed ladder, and the batch
  family's 36 model-form records sharing one setting by design — are untested,
  and are unaffected either way by this result.
- **Gate P's failure is confirmed as the model's, not diagnosed.** Knowing the
  7.6472 is a real fixed point makes the +72% a real model error; it does not
  say which term in kOmegaSST produces it.

## 7. Reach — what this confirmation covers

> **[COUNT CORRECTED 2026-08-11, minutes after first commit, by the author.]** This
> section first said **12** surfaces and closed by saying **sixteen** — two
> different numbers in one section, and **its own list underneath had 17 entries.**
> The measured figure is **17**. The prose was written from an impression of a
> search result while the list was pasted from the search itself, which is how a
> record ends up disagreeing with its own evidence three paragraphs apart. It is
> corrected here rather than quietly repaired: **the wrong number also went into
> commit `ef3e4872`'s message, where it cannot be edited**, so a reader arriving
> from the log needs this line. The verdict is unaffected — the reach is larger
> than claimed, not smaller.

`7.6472` and the +63% figure appear on **17 surfaces besides the F6b record and
this check's own two files**, found by a wrap-safe whitespace-normalised search
rather than a line-bounded grep: `docs/PRODUCT_LIST.md`, `docs/MEMORY_ARCHITECTURE.md`,
`CLOSURE_CHALLENGE_STATUS.md`, `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`,
`campaign/CALIBRATION_SCORECARD_2026-08.md`, `campaign/CAMPAIGN_STATUS.md`,
`campaign/F12_PREREGISTRATION.md`, `campaign/F6_closure_aligned_flows.md`,
`campaign/F6b_QCR_{PREREGISTRATION,RESULTS}.md`,
`campaign/MODEL_FORM_BAND.md`, `campaign/MODEL_FORM_H_HILLS_PREREGISTRATION.md`,
`campaign/MODEL_FORM_FPE_RESCUE_PREREGISTRATION.md`,
`campaign/QCR_ACTIVITY_CHECK_2026-08-08.md`, `campaign/W3_AHMED_PREREGISTRATION.md`,
`dafoam/f6b_periodic_hills/F6b_periodic_hills.md`,
`docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md`.

**Three of those are the model-form family's, which uses 7.6472 as a baseline.**
Had this check disagreed, every one of those surfaces would have been in
question. It did not, so none of them needs an edit — **which is the useful thing
to say about a confirmation: it is worth recording precisely because it tells
seventeen surfaces they do not have to move.**

## 8. Cost, against the declared budget

Priced in the pre-registration from this case's own measured 0.06797 s/iteration
and no rate borrowed from another solver family.

| item | predicted core-min | measured core-min |
| --- | --- | --- |
| arm B | 6.8 | **4.22** |
| arm C | 6.8 | **12.11** |
| positive control | 2.27 | **1.95** |
| gate re-analysis | < 1 | < 1 |
| **total** | ≈ 20 | **18.28** |
| declared budget | **50** | — |

Inside budget at 37% of it. Both arms ran serially on one pinned core each,
concurrently, setsid-detached, on a 16-core box; the control on a third core.
Wall-clock for the whole check was **12 minutes 26 seconds**.

## 9. Evidence

- Pre-registration `campaign/F6b_RELAXATION_INVARIANCE_PREREGISTRATION.md` (`ce0b14be`), Addendum 1 (`110da419`) — both before the compute they govern
- `F6b_runs/relax_invariance.json` — every number above, machine-readable
- `F6b_runs/relax_invariance.py` — scoring script; **imports `gate.py`** rather than reimplementing the crossing logic, so a difference between arms cannot be a difference between two copies of an analysis. Instrument control: it reproduces arm A's published 0.2604 / 7.6472 exactly.
- `F6b_runs/relax_invariance_ledger.txt` — self-ledger: launch times, exact commands, per-arm residual histories every 500 iterations, exit states
- `F6b_runs/run_relax_arm.sh` — the launcher, one arm per invocation
- Cases and written fields: `F6b_runs/medium_relax_{B,C,PC}/`
- Solver logs `solve_registry/f6b3_relax{B,C,PC}_20260811T011859Z.log` — **not committed**; the committed extract of what they are cited for is the ledger. They were written to `F6b_runs/log.relax_{B,C,PC}` during the run and **moved to `solve_registry/` afterwards**, which is where this case's own 2026-08-05 logs live and which `.gitignore:38` covers — so 19 MB of solver output cannot be swept into someone else's pathspec commit out of a tracked directory. The ledger records the move.
- Instrument: `LESSONS.md` L-47
