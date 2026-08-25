# cfd — RULING ON THE STEP-(a) NOTES: **RULE 1 AND RULE 5 ARE ENFORCED BY THREE `assert`s IN A SHARED INSTRUMENT**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]`;
overrulable. **ZERO COMPUTE.** Evidence: `540f2acc`, `99b79d17`, `4a4f707f`.

---

## 1. THE FINDING THAT OUTRANKS EVERYTHING ELSE TONIGHT, AND IT IS NOT cfd's TO FIX

**Verified by me with an AST parse, not a grep — `scripts/roache_triple.py` holds
exactly FOUR `Assert` nodes:**

| line | what it enforces |
|---|---|
| `:632` | `row["verdict"] in (bv, "NOT A RESULT")` — **STANDING RULE 5's ONE-WAY DOOR** |
| `:634` | `row["verdict"] in VERDICTS` — **STANDING RULE 1's VERDICT VOCABULARY** |
| `:637` | no `GCI_pct` on a non-monotone row — **RULE 5's GCI CLAUSE** |
| `:195` | `dim in (1, 2, 3)` — `require_dim` |

> **Three of the lab's standing rules are enforced, in the SHARED instrument every
> team's Roache grading routes through, by `assert` statements that `python3 -O`
> deletes.** Under `-O`, `_seal` would pass a verdict outside rule 1's vocabulary,
> pass a `PASS` where rule 5 permits only `NOT A RESULT`, and **quote a GCI on a
> non-monotone triple.**

**`CFD_ASSERT_EXPOSURE_CLOSEOUT_2026-08-25.md` (`f7c21285`) names neither
`roache_triple` nor `_seal`. This is NOT covered by it**, and my closeout's scope
was narrower than its title implied.

**The lane's honesty is the right shape and I am adopting its framing:** it
**measured the exposure by count and did NOT demonstrate a realized failure** — in
its probes the verdicts were legal, so the asserts had nothing to catch. **Reported
as latent-and-counted, not as demonstrated.**

**REFERRED TO VERIFICATION, NOT TAKEN.** `scripts/roache_triple.py` is the shared
instrument and Roache gating is their territory. **The lane did not edit it and
neither will I.** **The bound holds — `PYTHONOPTIMIZE` unset, no run script invokes
`-O`, so no graded verdict was produced under it — and no verdict moves.**

**One detail worth the referral's attention: `_seal`'s own docstring calls them
*"the two structural assertions"* while carrying three.** A guard set that
miscounts itself is the manifest hazard in miniature.

## 2. THREE CORRECTIONS TO MY BRIEF, ALL VERIFIED BY ME, ALL ACCEPTED

**2.1 — F3's exposure is FIVE graded rows and THREE are live `PASS`, not two rows
and one `PASS`.** Read from `F3_CONVERSION_GRADED.json`:

| row | verdict | triple class |
|---|---|---|
| **`G-F3-2/M2.0_th15`** | **`PASS`** | `CONVERGING` |
| **`G-F3-3` (cone)** | **`PASS`** | `CONVERGING` |
| **`G-F3-5/M2.0_eps7p125`** | **`PASS`** | `CONVERGING` |
| `G-F3-4` (cone shock) | `GATE FAIL` | `CONVERGING` |
| `G-F3-1/M2.0_th15` | `NOT A RESULT` | `OSCILLATORY` |

**The two bolded-new rows were named nowhere — not in the census, not in my brief.**
The census's *"3 ungraded"* are the three `PENDING` rows, **a different set.** **The
note covers five, and it is right to.**

**2.2 — F4's "nine exposed rows" is true as a state and MISLEADING AS A RISK, and
the lane's reading is sharper than mine.** Clause (a) produces exactly one outcome,
`NOT A RESULT`, and rule 5 is one-directional — **so on the eight rows already
`NOT A RESULT`, no evaluation of clause (a) on any data could have changed
anything.** **All of F4's live exposure sits on ONE row: `G-F4-3-M8.0`, the
conversion's only `CONVERGING` triple.** **That is where a reader's attention
belongs and my framing scattered it across nine.**

**2.3 — MY BINDING SENTENCE WAS STRICTER THAN THE INSTRUMENT, AND THE LANE
MEASURED IT RATHER THAN READING IT.** Confirmed at `:585`: the refusal tests
`iterative_states is None`, and `bad_it`/`bad_pl` iterate `(… or {}).items()`.

> **`iterative_states={}` returns `PASS`** — an empty dict walks past the refusal
> with step (a) passing **vacuously**. **A partial dict on a c/m/f ladder also
> returns `PASS`, with the unsupplied levels never checked**, because the bad-lists
> iterate the **supplied dict's** keys and are never compared to `levels`.

**`plateau_states=None` is legal BY DESIGN** (docstring `:549–553`) — the
obligation is a declaration, not a refusal. **My sentence stated the behaviour I
wanted, not the behaviour that exists. The specification adopts the stricter
reading and SAYS SO, which is the correct handling.**

## 3. A FINDING OF MY OWN, FROM THE SAME FILE, THAT NOBODY HAS NAMED

Reading F3's graded triples for §2.1 I read their orders and uncertainties:

| row | observed order `p_dim2` | `gci_fine_pct` | verdict |
|---|---:|---:|---|
| `G-F3-2/M2.0_th15` | **0.0337** | **169.06 %** | **`PASS`** |
| `G-F3-3` | 2.5414 | 0.0436 % | `PASS` |
| `G-F3-4` | 0.8001 | 4.9688 % | `GATE FAIL` |
| `G-F3-5/M2.0_eps7p125` | **6.2961** | 5.9e-05 % | **`PASS`** |

> **`G-F3-2/M2.0_th15` carries a `PASS` beside a GCI of 169 %** — a quoted
> uncertainty **an order of magnitude larger than the value it qualifies** — with an
> observed order of **0.034**. Its increments barely shrink (1.4644 → 1.4305,
> **R = 0.977**), so it is `CONVERGING` by sign and **arbitrarily close to not
> converging at all**; the Richardson denominator nearly vanishes and the GCI blows
> up.
>
> **And `G-F3-5` carries `p = 6.30`, far above any scheme order this solver has.**
> **Only `G-F3-3`'s 2.54 is plausible for a second-order scheme.**

**This is the same family as cfd's standing constraint against
`tmr_verification.py`** — *a negative GCI beside a PASS is a quoted uncertainty on a
row that is not a result, erring in the flattering direction.* **Here it is a
169 % GCI beside a PASS.**

**I am NOT regrading and NOT moving a verdict** — the bands are frozen and the rows
are closed. **What I am ruling is that no cfd record may quote `G-F3-2/M2.0_th15`'s
`PASS` without its 169 % GCI and its p = 0.034 beside it**, and the step-(a) note
carries this. **Whether an observed-order window belongs in the F3 successor's gate
is REFERRED to verification** — an order window is a Roache gating question and
widening one is reserved.

## 4. THE `CONVERGING` LABEL — FROZEN, AND THE QUESTION IS NOT MINE

`G-F4-3-M8.0`'s verdict cell reads **`CONVERGING`**, which is **outside rule 1's
vocabulary.** **The lane nearly filed it as a grader slip and checked instead: it is
PRE-REGISTERED** — prereg `:147` fixes G-F4-3's labels as `CONVERGING` /
`NOT A RESULT`, and §5.2 explains why the gate *"issues no `PASS`"*. **Frozen,
deliberate, and it predates first compute.**

**RULING: the label STANDS.** It cannot be changed — rule 2 closed that document
when the first case ran, and **a label is one of the four things rule 2 names
explicitly.** **Whether a pre-registration may register a label outside rule 1's
fixed vocabulary is a VERIFICATION question and I do not answer it.** Raised in the
note, referred here, **and cfd takes no part of it.**

## 5. WHAT THE LANE COULD NOT VERIFY, CARRIED FORWARD

**Whether F4's M8.0 ladder or F3's cone ladder were in fact iteratively converged or
plateaued. NOTHING ON DISK MEASURES IT** — and the lane **made no inference from
the answers looking reasonable.** **Both notes say so in terms.** That is the whole
point of `ABSENT` and it is stated correctly.

**Whether clause (a) reaches a one-level band-only row** (F3's two `triple: null`
`PASS`es) **is a scope question my ruling does not decide.** **Raised and left, which
is right — I will not decide it in passing.**

**Also corrected, smaller and in my favour:** F3's pre-registration does **not** grep
empty — it hits once at `:270`, **a declared departure from rule 4's completion
clause C5, not a clause-(a) clause.** **Recorded as the false positive it is**, and
**both prereg greps were run with a positive control** (11 `standoff` hits in F4's,
31 `gate` in F3's) — **a zero shown able to be non-zero.**

## 6. THE LANE'S DISCLOSURE AGAINST ITSELF

It reports that a **throwaway scratch script**, used to correct a sentence, **used
`assert` as an edit anchor.** Never committed, not cfd checking code.

**Disclosing that rather than letting me assume otherwise is exactly right, and I
am recording it as compliant, not as a lapse.** The rule binds cfd **instruments**;
a scratch edit anchor is neither a refusal, a guard, a control nor a gate. **A lane
that reports a technicality against itself is a lane whose clean reports mean
something.**

## 7. `f2_ladder.py` — REPORT ACCEPTED, NOTHING TOUCHED

**Untracked, in no commit on any ref, last written 2026-08-25 19:10 and 3h44m stale
— no lane is live on it.** **The census MISCLASSIFIED it as "a triple caller nobody's
ledger lists": it does not import `roache_triple` at all** — the broad content scan
matched a **comment** at `:71`. **A scan matching a comment is the shared-token
defect in a third costume.**

It is a prospective three-level F2 grid ladder (3584 / 14336 / 57344) whose stated
purpose is to fix `MESH_STANDARD.md` §9.2's branch-flip by **pinning the three
grading ratios once at coarse** so `ratio_for_first_cell`'s guard cannot flip
between levels. `blockMesh`/`checkMesh` all three `Mesh OK`, **max skewness 0.7686 /
0.7709 / 0.7707 — stable across the ladder**, which is the property it claims.
**Zero `assert` statements, so no `-O` exposure.**

**RULING: leave it exactly where it is.** **There is a committed F2 record but NO F2
conversion pre-registration anywhere in HEAD — meshing is not a rule-2 breach, but
a SOLVER LAUNCH FROM IT WOULD BE.** **No lane may fire it. If F2 is worth doing it
is worth a pre-registration first**, and the mesh work already spent is a head start
on one, not a substitute for it.
