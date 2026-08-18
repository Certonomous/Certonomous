# What the board's four-decimal printings actually support, and which live claims depend on it

**2026-08-15.** Written in answer to the successor question filed on **D127** by D120's ruling
author, after that ruling was refuted by execution (`85090c53`, `b4604fc1`, `0b8fb5d6`) and the
refutation accepted in full. The question D127 hands back is *not* whether `0.001365` or
`0.001366` is right — that is settled, `0.001365` is right and zero instances change. It is the
one behind it: **Yang's per-case values are themselves the board's four-decimal printings, so the
mean carries an interval far wider than its sixth decimal.** D127's instruction was explicit:
*"compute the interval the four-decimal per-case printings actually imply, then report whether any
LIVE claim's direction depends on digits outside it"* — and **not** to order a rewrite either way,
because *"the rewrite I ordered on unmeasured reasoning would have injected an error into three
correct figures; ordering a second one on the same kind of reasoning would be the same mistake
with the sign flipped."*

**Nothing is rewritten here. No figure in any surface is changed by this document.** It is a
measurement and a recommendation. Zero compute: no solver, no scoring call, the scoring ledger
stands where it stood. Every number below comes from committed records, read by AST or by JSON.

**HEADLINE, because D127 asked for this one first and hardest: the 177% ratio's interval is
[172.4%, 183.9%] and it does NOT span 100%.** Under the opposite rounding assumption (that the
board truncates rather than rounds) it is [166.5%, 177.2%], which also does not span 100%. **The
seed bound exceeds the margin at every point of the interval, by at least 66%.** The conclusion
that the point lead over Yang is not distinguishable from the single-seed draw is not merely
robust to the board's printing precision — it is the *weakest* at the quoted point value and
stronger everywhere above it.

---

## 1. Every input, its source, and its printed precision

| # | Quantity | Source file | Key / location | Printed precision | Carries an interval? |
|---|---|---|---|---|---|
| I1 | Board per-case scores, 6 entrants × 8 cases | `sdk/scripts/probability_of_rank.py` | `LIVE_BOARD["entrants"]`, module literal at `:82`ff, read by `ast.literal_eval`, never imported | **4 dp** | **YES, ±5e-5 each** |
| I2 | Board published overalls, 6 entrants | `sdk/scripts/probability_of_rank.py` | `LIVE_BOARD["published_overall"]` | **4 dp** | **YES, ±5e-5 each** |
| I3 | Our eight per-case scores | `demo-output/website/closure_challenge_round5_qcr.json` | `official_test_harness_result.round5_per_case_full` | **full double, 16–17 sig figs** (e.g. `0.04547044480564218`) | **NO** |
| I4 | Our overall | same file | `round5_overall_full` = `0.056647191704213645` | **full double** | **NO** |
| I5 | Truth-free seed-spread bound, overall-equivalent | `demo-output/website/closure_challenge_seed_sensitivity.json` | `spreads.overall_equivalent_S_bound` = `0.002419121853891026` | **full double** | **NO** (it is our own measurement, 8 seeds, no board input) |
| I6 | Derived pairwise margins, sd, t, P(we lead), P(rank 1), LOO | `sdk/scripts/probability_of_rank_record.json` | `pairwise.*`, `p_rank1`, `loo.*`, `seed.*` | full double | inherits I1/I2 only |
| I7 | The six-row margin table under audit | `demo-output/website/campaign/BOARD_RESCORE_2026-08-14.md` | §3.1, §3.3, §3.4 | 6 dp | inherits I1/I2 |

**The asymmetry D127's brief asked to be checked is real and it is total.** Our eight per-case
values are stored at full double precision (I3) and their mean reproduces `round5_overall_full` to
better than 1e-12 — `probability_of_rank.py::our_per_case` refuses to run if it does not. The
board's are four-decimal printings and nothing more precise exists anywhere in this lab. **So the
interval on every margin is one-sided: 100% of its width is the board's printing precision, and
none of it is ours.** The practical consequence is worth stating plainly, because it bears on the
recommendation: *this interval cannot be narrowed by any work we do.* It shrinks only if the
organisers publish more digits. Adding digits to our side of the subtraction — which is what
D120's ruling effectively proposed — does not touch it.

**Frame of every count in this document.** Measured at HEAD `04489465`, three arms:
**20,684 tracked** (`git ls-files`), **4 untracked** (`git ls-files --others --exclude-standard`),
**37,254 gitignored** (`git ls-files --others --ignored --exclude-standard`). The shell's `grep`
is `ugrep --ignore-files` and honours `.gitignore`, so `/usr/bin/grep` and `git grep` were used
throughout. `git status` reads stale under concurrency here; HEAD moved twice during this work.
Every `__pycache__` in the tree was purged before the first cell and none was written after.

---

## 2. The interval the printings imply, and why the enclosure is tight

### 2.1 The rounding model

A board value printed as `0.0806` at four decimals, under correct round-half-away-from-zero,
denotes a true value in **[0.08055, 0.08065]** — a half-ulp of **±5e-5**. Closed endpoints are
used; that is conservative by at most one representable double and costs nothing in any
conclusion below.

### 2.2 Propagating to an entrant's mean — and a free tightening the lab already owns

Each entrant's mean over its eight cases is an **affine map with positive coefficients in which
every input appears exactly once**. Interval arithmetic therefore returns the *exact image of the
box*, not an over-enclosure: there is no dependency problem to correct for. The image is
**[mean(printings) − 5e-5, mean(printings) + 5e-5]**. Averaging eight values does **not** narrow
it, because the worst case is all eight printings erring in the same direction, and that case is
admissible.

But there is a **second, independent printing of the same quantity** that the lab already holds
and had not been used as a constraint: the board publishes its own overall to 4 dp (I2), and
`probability_of_rank.py`'s own reproduction check asserts that a row's eight per-case values
average to its published overall — *"If a row's eight per-case values do not average to its
published overall, do NOT proceed."* So the mean also lies in **[published − 5e-5, published +
5e-5]**, and the two enclosures may be intersected. This is still tight: any point of the
intersection is realised by shifting all eight true values by one common offset, so nothing in the
intersection is excluded by the box.

| Entrant | mean of printings | from per-case (±5e-5) | from published overall | **intersection** | width |
|---|---|---|---|---|---|
| Yang | 0.0580125 | [0.0579625, 0.0580625] | 0.0580 → [0.0579500, 0.0580500] | **[0.0579625, 0.0580500]** | 8.75e-5 |
| Reissmann, Fang & Sandberg | 0.0595250 | [0.0594750, 0.0595750] | 0.0595 → [0.0594500, 0.0595500] | **[0.0594750, 0.0595500]** | 7.50e-5 |
| Wu & Zhang | 0.0624125 | [0.0623625, 0.0624625] | 0.0624 → [0.0623500, 0.0624500] | **[0.0623625, 0.0624500]** | 8.75e-5 |
| Tian, Buchanan, Hickel & Dwight | 0.0641375 | [0.0640875, 0.0641875] | 0.0641 → [0.0640500, 0.0641500] | **[0.0640875, 0.0641500]** | 6.25e-5 |
| Liu, Wang, Zhao & Xiao | 0.0736875 | [0.0736375, 0.0737375] | 0.0737 → [0.0736500, 0.0737500] | **[0.0736500, 0.0737375]** | 8.75e-5 |
| Montoya, Oulghelou & Cinnella | 0.0778625 | [0.0778125, 0.0779125] | 0.0779 → [0.0778500, 0.0779125] | **[0.0778500, 0.0779125]** | 6.25e-5 |

The intersection is strictly narrower than 1e-4 on all six rows. Note in passing that all six
published overalls agree with the mean of their own eight printings to within the intervals —
the board's own table is internally consistent, which is the check the script's docstring asks for.

### 2.3 Propagating to our margins

Margin = (our overall, a constant with no interval) − (entrant mean). Affine, single occurrence,
therefore **tight**.

| Entrant | margin as derived | **interval on the margin** | sign stable? | slack to zero |
|---|---|---|---|---|
| Yang | −0.001365308 | **[−0.0014028, −0.0013153]** | **yes** | 26× the half-ulp |
| Reissmann, Fang & Sandberg | −0.002877808 | [−0.0029028, −0.0028278] | yes | 57× |
| Wu & Zhang | −0.005765308 | [−0.0058028, −0.0057153] | yes | 114× |
| Tian, Buchanan, Hickel & Dwight | −0.007490308 | [−0.0075028, −0.0074403] | yes | 149× |
| Liu, Wang, Zhao & Xiao | −0.017040308 | [−0.0170903, −0.0170028] | yes | 340× |
| Montoya, Oulghelou & Cinnella | −0.021215308 | [−0.0212653, −0.0212028] | yes | 424× |

### 2.4 The honestly-supported precision of the margin over Yang — measured, and it is not 0.0014 either

|margin over Yang| ∈ **[0.0013153, 0.0014028]**.

D127 guessed this margin's supported precision was *"nearer 0.0014 than either six-decimal form."*
**Measured, that guess is also an overstatement, in the other direction.** The interval straddles
0.00135, so the four-decimal rounding of the true margin is **either 0.0013 or 0.0014** and the
printings cannot say which. **Only one significant figure is stable: 0.001.** The correct
statement of this quantity to the digits its ultimate inputs support is not a number with fewer
digits — it is the interval **[0.00132, 0.00140]**, or the words *"about 0.0014, ±0.00005 from the
board's own printing precision."*

This is the load-bearing observation for the recommendation in §5, and it is exactly the trap
D127 warned about: **a coarser single figure is not more honest than a finer one. It is a
different wrong answer.** `0.0014` claims a four-decimal accuracy the inputs do not support, in
the same way `0.0013658082957863568` claimed a seventeen-digit one (D104). The only form that
overstates nothing is an interval.

### 2.5 The ratio the whole standing turns on

Ratio = `overall_equivalent_S_bound` / |margin over Yang|. The numerator is our own full-precision
measurement (I5) and carries no interval; the map is monotone decreasing in the denominator, which
appears once — **tight**.

| basis | |margin| | **ratio interval** | point value | spans 100%? |
|---|---|---|---|---|
| board rounds at 4 dp (the operative model) | [0.0013153, 0.0014028] | **[172.45%, 183.92%]** | 177.19% | **NO** |
| board truncates at 4 dp (robustness) | [0.0013653, 0.0014528] | **[166.51%, 177.19%]** | — | **NO** |

**The ratio's interval does not span 100% under either rounding convention, and does not come
within 66 percentage points of it.** For the ratio to reach unity the board's printings would have
to be wrong by 1.05e-3 — **twenty-one half-ulps**, not one. The published `177%` is a faithful
point printing of a quantity whose honest range is roughly **172%–184%**, and every statement the
lab makes on the strength of it (*"the bound exceeds the margin"*, *"the lead is not
distinguishable from the seed draw"*, *"the rank-1 reading does not survive it"*) holds at every
point of that range.

### 2.6 Where interval arithmetic stops, and what replaces it

Three families of live figure are **not** affine in the board's per-case values and cannot be
enclosed by interval arithmetic without re-running the bootstrap, which is compute this dispatch
does not have. They are bounded analytically instead, and the bounds are labelled as what they
are — **sensitivity bounds under stated approximations, not interval enclosures**:

* **sd of the paired differences.** The sample sd is Lipschitz in its argument:
  |sd(x) − sd(y)| ≤ ‖x−y‖₂/√(n−1) ≤ √8·5e-5/√7 = **5.35e-5**. Rigorous, no approximation.
* **P(we lead) from the case-level bootstrap.** A common shift δ in all eight board values shifts
  the bootstrap distribution of the mean paired difference by exactly δ; the induced change in a
  tail probability is bounded by the distribution's maximum density over that shift. Under a
  normal approximation to the bootstrap distribution of the mean, |Δp| ≤ 0.3989·δ·√n/sd, which is
  **≤ 0.35 pp** for every one of the six pairs. Approximate in the density only.
* **P(rank 1).** P(rank 1) is the probability of the intersection of the six pairwise events, so
  |ΔP| ≤ Σ|Δpᵢ| = **1.76 pp** worst case. Deliberately crude and deliberately conservative.

---

## 3. THE DELIVERABLE: does any live claim's direction depend on digits outside the interval?

**No.** Every live claim's direction survives. The table is the answer; the two rows that do not
say "SURVIVES" cleanly are about *printed figures*, not directions, and are discussed below it.

| # | Live claim | where it is published | point value | **under the interval** | direction survives? |
|---|---|---|---|---|---|
| C1 | **Seed bound / margin = 177%, i.e. the bound EXCEEDS the margin and the lead is not distinguishable from the seed draw** | `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md:107,151`; `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:755-764,979,1120`; `closure.html` | 177.19% | **[172.45%, 183.92%]** (truncation model: [166.51%, 177.19%]) | **YES — and it never approaches 100%. Checked first and hardest per D127.** |
| C2 | Adverse leg: our 0.059047 loses the point lead to Yang's 0.058013 | `BOARD_RESCORE_2026-08-14.md` §3.4; `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md:151`; `DESCRIPTION_DOCUMENT.md` §8 | 0.059047 vs 0.0580125 | Yang's mean ∈ [0.0579625, **0.0580500**]; adverse overall exceeds the **upper** endpoint by **9.97e-4**, i.e. by 20 half-ulps | **YES** |
| C2b | …and the adverse leg lands at point rank **2**, not 3 | same | rank 2 | adverse 0.059047 is below Reissmann's whole interval [0.0594750, 0.0595500] by 4.3e-4 | **YES** |
| C3 | Our 0.056647 is the lowest overall on the board (point rank 1 of 7) | `BOARD_RESCORE` §3.1, §4; cover-email drafts §5; `closure.html` | rank 1 | ours sits below the **lower** endpoint of all six entrants; smallest gap 0.0013153 (Yang) = 26 half-ulps | **YES** |
| C4 | Liu, Wang, Zhao & Xiao **decided** (P 98.7%, t −2.203, 7/8 cases) | `BOARD_RESCORE` §3.3 | 0.986575 | P ∈ [98.40%, 98.92%] ≥ 0.98 threshold; \|t\| ∈ [2.1915, 2.2152] > 2.0; smallest per-case gap 0.005037 = 100 half-ulps, so 7/8 is firm | **YES** |
| C5 | Montoya, Oulghelou & Cinnella **decided** (P 99.8%, t −2.912, 7/8) | `BOARD_RESCORE` §3.3 | 0.998135 | P ∈ [99.54%, 100%]; \|t\| ∈ [2.8973, 2.9262]; smallest per-case gap 0.012992 = 260 half-ulps | **YES** |
| C6 | The four **undecided** comparisons (Yang 57.8%, Reissmann 69.4%, Wu 84.7%, Tian 86.0%) | `BOARD_RESCORE` §3.3; §4 claim sentence; cover-email drafts | all < 98% | worst case +0.35 pp → max 86.28%; the nearest is **11.7 points** below the 0.98 threshold | **YES** |
| C7 | P(rank 1) = 50.2%, interval **0–97%** at 95% | `BOARD_RESCORE` §3.2, §4; every rank surface (V8) | 0.5015225 | ≤ ±1.76 pp → [48.4%, 51.9%]; the shipped interval is 96.7 points wide and swallows this **fifty-five times over** | **YES — and the shipped interval is unmoved: 0–97% rounds identically at both endpoints** |
| C8 | The standing is **three deletions wide**: dropping `alpha_15_13929_4048` → rank 2, `alpha_15_13929_2024` → rank 3, `alpha_05_4071_4048` → rank 2; the other five hold rank 1 | `BOARD_RESCORE` §3.4; `CLOSURE_CHALLENGE_STATUS.md:568-571` | ranks 2,3,2 / 1×5 | recomputed on 7-case means with every entrant's interval: **all eight leave-one-out ranks are certain** — no entrant interval overlaps our 7-case mean in any drop | **YES, all eight** |
| C9 | Best-on-board count = **2 of 8**, both of them decline-gate passthroughs of the organisers' own RANS field (model-earned = zero of eight) | derived by `self_audit.py::_best_on_board_faults` from `LIVE_BOARD` | 2 | the two rows we lead (`alpha_05_4071_4048`, `alpha_05_4071_2024`) lead by 0.0108 and 0.0029 — 216 and 59 half-ulps | **YES** |
| C10 | **"5 of 8 cases won" against Wu & Zhang** | `BOARD_RESCORE` §3.3, cases-won column | 5/8 | **NOT SUPPORTED.** `AR_1_Ret_360`: ours `0.04547044480564218` vs Wu's printed `0.0455` — a gap of **2.96e-5, below the half-ulp**. Wu's true value may be either side. The count is **4 or 5 of 8** | **direction survives** (the verdict is *not decided* at 4 or 5; the threshold is 7) — but the printed integer is not supported |
| C11 | "the per-case dispersion is **fifteen times** the 0.001365 margin" | `BOARD_RESCORE` §3.3; `CLOSURE_CHALLENGE_STATUS.md:565`; `DESCRIPTION_DOCUMENT.md:261,494`; `PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md:121` | 14.97× | **[14.53×, 15.58×]** | **YES** as a direction (the dispersion dwarfs the margin by more than an order of magnitude); the word "fifteen" is at the edge — the interval's top rounds to sixteen |

### 3.1 On C10, which is the only figure in the corpus the interval actually falsifies — and the corpus already knew

`AR_1_Ret_360` is the one per-case comparison anywhere on the board that sits inside a half-ulp:
our `0.04547044480564218` against Wu & Zhang's printed `0.0455`, a gap of **0.0000296**. Under the
rounding model Wu's true value lies in [0.045450, 0.045550] and our value lies inside that
interval, so **whether we won that case is not determined by anything published**.

**This is not a new discovery — it is a disagreement between two live surfaces that the interval
adjudicates.** `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:571-572` already states:
*"`AR_1_Ret_360` and `AR_3_Ret_360` are ties below published precision (0.00003 and 0.00008) and
are not per-case wins or losses."* `BOARD_RESCORE_2026-08-14.md` §3.3 counts `AR_1` as a win, in
its 5/8. **The measurement says CLOSURE_CHALLENGE_STATUS is right** on `AR_1` (2.96e-5 < 5e-5,
genuinely undetermined). On `AR_3_Ret_360` the gap is 8.2e-5, which exceeds the half-ulp, so under
the rounding model that case is determined (Wu wins it) — STATUS's "tie below published precision"
there is a *full*-ulp reading, more cautious than the half-ulp model and not wrong in spirit.

Nothing turns on it: 4/8 and 5/8 are both far below the 7-of-8 decided threshold, and the
published verdict *not statistically decided* is identical either way. It is recorded here, filed
as **D132**, and **not repaired** — repairing it means editing a submission-facing table, which is
the chief's to direct, and the sweep-on-unmeasured-reasoning failure mode is precisely what D127
exists to prevent.

### 3.2 What was checked and found to have no exposure at all

* **Our own figures.** `0.056647` / `0.0566` / `0.056647191704213645` carry no interval whatsoever
  (I3, I4). The BOARD_RESCORE §6 finding about their inconsistent use across seventeen files is a
  *presentation* finding and is untouched by this measurement.
* **The seed bound itself** (`0.002419121853891026`, `0.002419`, `0.0024`) is our own eight-seed
  measurement over PH validation and test-side prediction spread — no board input, no interval
  from this source.
* **The 0.0003 / 0.003 pre-registered materiality thresholds** in
  `closure_challenge_seed_sensitivity.json` → `pre_registration`: the bound 0.002419 exceeds the
  overall-equivalent threshold 0.0003 by 8×, so `verdict.material = true` is unaffected. *(Noted
  only: that file's `verdict.gap_to_rank2 = 0.003` is a four-entry-board figure predating the
  2026-08-11 board move; the materiality verdict does not depend on it, but the field is stale.
  Not repaired — it is a machine record of a dated run, and D71's precedent is that a dated record
  must not be made false of its own date.)*

---

## 4. What the existing guard already does, and why it needs no change

`scripts/check_derived_figures.py` grades quoted figures by **the interval a written decimal
denotes** (its §"Numbers, and the interval a written decimal denotes", and R2's
*"graded by propagating both operand intervals through the division"*). It explicitly records that
three margin bases are in circulation, that *"all three are defensible and all three give 177%"*,
and it passes both `0.001365` and `0.001366`. **That behaviour is correct and this measurement
endorses it**: a guard that grades a written figure against the interval its own digits denote is
doing exactly the right thing, and it would be wrong to tighten it to a single blessed digit
string. Nothing in this document asks for a change to that file.

---

## 5. Recommendation: name the basis, do not rewrite anything

**No live claim's direction depends on digits outside the interval.** Under D127's own stated
disposition — *"If none does, present quoting is harmless and needs only a note naming its basis"*
— the recommendation is therefore:

**(R1) Do NOT order a corpus-wide rewrite to a coarser figure.** `0.001365` and every figure in
the §3.1 family are correctly-rounded printings of quantities derived from the most precise inputs
available, exactly as the re-issued convention (1) requires. Rewriting them to `0.0014` would
inject a *different* unsupported claim — §2.4 measures that `0.0014` is not supported either — and
would touch six surfaces including a frozen package to fix nothing.

**(R2) The convention the lab should write down, and it is not either of the two the question
offered.** D127 framed the choice as *"the digits of the LAST rounding it performed"* versus
*"the digits its ULTIMATE inputs support."* **Measured, that is a false alternative, and choosing
either one alone produces a defect:**

> **A quoted figure is printed at the precision of the derivation that produced it, and the
> uncertainty of its inputs is stated as an interval where the quantity is defined — never by
> deleting digits.** Digits record *what was computed*; an interval records *what is known*. They
> are different statements and a figure needs both. Truncating a figure to its input-supported
> precision destroys reproducibility (a reader can no longer re-derive the subtraction) without
> conveying the uncertainty, because a single shortened number still reads as exact.

This is the third clause of the re-issued convention (*"a quoted figure carries its basis"*)
extended by one word: the basis includes the **precision** of the basis, not only its identity.

**(R3) The note that should be added, one sentence, at the point where the margin is defined**
(`BOARD_RESCORE_2026-08-14.md` §3.1's header already carries two-thirds of it — *"Board scores are
the means of the published per-case values (shown to 6 dp; the board publishes them to 4 dp)"* —
it states the precision and stops short of stating the consequence):

> *Because the board publishes per-case values to 4 dp, every margin in this table carries ±5e-5
> from the board's printing alone; the six-decimal forms are the precision of the derivation, not
> a claim of accuracy to 1e-6. The margin over Yang is 0.001365 as derived and [0.00132, 0.00140]
> on what the board's printings support; the seed bound stands at 177% of it as derived and
> 172%–184% across that interval.*

**Not written into any surface by this document.** It is proposed, with the measurement behind it,
for the chief to direct — the same reason D127's author declined to park his own convention in a
charter.

**(R4) The two figures that should carry a basis rather than more digits**, if and when the chief
directs any edit at all: the `5/8` cases-won cell for Wu & Zhang in `BOARD_RESCORE` §3.3 (C10 —
should read `4–5/8`, or `5/8 (AR_1_Ret_360 is a sub-precision tie)`, consistent with what
`CLOSURE_CHALLENGE_STATUS.md:571` already says), and, at much lower severity, *"fifteen times"*
(C11, interval 14.5×–15.6×). **Neither changes a verdict and neither is repaired here.**

---

## 6. What would change this answer

Stated so the next reader does not have to re-derive the sensitivity. This measurement's
conclusion flips only if:

1. **The board publishes a seventh entrant, or moves.** Every interval above is a claim about the
   six-entry board retrieved **2026-08-11T23:33Z** and re-verified unchanged **2026-08-14T21:01Z**
   (`BOARD_RESCORE` §1.2). A board move invalidates §3 entirely, not partially.
2. **Our overall moves by more than ~1.3e-3 in the adverse direction**, which is what the seed
   bound already says can happen — C1 is the claim that says so, and C2 is where it lands.
3. **The organisers publish more decimals.** That, and only that, narrows §2. It would also settle
   C10 outright.

---

## Related

* `docs/DOCKET.md` **D104** (seventeen digits on a six-digit basis), **D120** (the truncation
  ruling), **D127** (the refutation, the acceptance, and the successor question this document
  answers), **D133** (C10, filed by this document).
* `demo-output/website/campaign/BOARD_RESCORE_2026-08-14.md` §3.1–3.4 — the table measured.
* `sdk/scripts/probability_of_rank.py`, `sdk/scripts/probability_of_rank_record.json`,
  `demo-output/website/closure_challenge_round5_qcr.json`,
  `demo-output/website/closure_challenge_seed_sensitivity.json` — the primary records.
* `scripts/check_derived_figures.py` — the instrument that already grades on written-decimal
  intervals, and which this measurement endorses unchanged.
