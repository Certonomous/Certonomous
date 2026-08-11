# Research directions, August 2026 — ten proposals, ranked, priced

**Filed:** 2026-08-11, 21:43 UTC (`date -u`, executed). **Commit anchor:** `2b695682`.
**Compute spent producing this document: zero.** No solver, no container, nothing launched.
**Nothing was sent, emailed, uploaded or registered.** Submission stays parked and is Katie's.

Katie's list item 4, new research directions. This is a proposing brief. Every direction below
is filed as a costed proposal or is explicitly recorded as *not* filed with the reason; Katie
decides what is bought.

## The standard this document is written against

`docs/CAPABILITY_STRATEGY.md`: **expertise is proven by solving OUR OWN open problems.** A
direction that does not close an open problem on the product list or the docket, or build a
capability the lab demonstrably lacks, is a topic and is not here. Every entry states four
things and a fifth where it applies:

1. **The open problem it closes**, by its identifier on `docs/PRODUCT_LIST.md` or `docs/DOCKET.md`.
2. **The falsifier**, and — per Verification Charter **§2a**, adopted today — an explicit answer
   to *could a wrong treatment still pass this gate?* An identity is reportable and never gateable.
3. **The external referent**, per §6a — a published value, an exact analytic result, a benchmark
   distribution, an independent implementation, **or a plain statement that it has none.**
4. **The cost and its basis**, priced against a measured rate wherever one exists.
5. **What kills it early and cheaply**, for the ambitious ones.

### The calibration fact these prices are written against

`scripts/calibration_scorecard.py`, executed at `64281b6b`: **0 of 3 scoreable pairs within 20%**,
and **16 further closed proposals recorded no actual cost at all.** The strategy's auto-approval
rule (three for three within 20%) is *runnable and unsatisfied*. F8 cost 47.7 core-min against
its own estimate of 6 — an 8× overrun, on an estimate built by analogy. **Every price below that
is not zero is built against a measured rate on this box, and says which one.** Core-minutes are
wall-seconds × ranks ÷ 60 throughout, basis gross, per `docs/charters/COMPUTE_BUDGET_CHARTER.md` §2.

---

## The ranked list

| # | Direction | Horizon | Cost | Filed? |
|---|---|---|---|---|
| **R1** | Does the inferred correction land where the model is wrong, or where the objective is sensitive? | Cheap | **0 core-min** | **filed** |
| **R2** | The reordering lever 257 runs requested and none proved | Cheap | **8 core-min** | **filed** |
| **R3** | Triangulate the F7a reference before buying more free-surface mesh | Cheap | **0 core-min** | **filed** |
| **R4** | Per-family cost scaling laws, scored on held-out runs | Cheap | **0 core-min** | **filed** |
| **R5** | The whitened re-inversion: does the correction move when sensitivity is divided out? | Real result | **340 core-min** | **filed** |
| **R6** | Band-containment census: how many scoreable pairs does this lab own? | Ambitious (kill test free) | **0 core-min** | **filed** |
| **R7** | NACA Report 1191 settles which Strouhal form governs the filmed gate | Cheap | **0 core-min** | **filed** |
| **R8** | A physics-informed, transferable prior on the discrepancy field | Ambitious | unpriced | not filed — blocked |
| **R9** | Regular-wave added resistance, and the two pieces that would make irregular seas reachable | Ambitious | unpriced | not filed — amend the existing proposal |
| **R10** | Wigley hull wave resistance | Real result | cost-blind | not filed — measure the rate first |

---

## R1 — Does the inferred correction land where the model is wrong, or where the objective is sensitive?

**Horizon: cheap and compounding. Cost: 0 core-min. FILED** as
`s1-does-the-correction-land-where-the-error-is-or-where-the-sensitivity-is`.

**Open problem closed:** `PRODUCT_LIST.md` §4A, Stage 1 FIML field inversion, carried `[-]`. The
S1 line now has a **passing objective gate and an undiagnosed failing geography gate**, and the
failure is three days old with no explanation attached to it.

**The situation, measured.** G1 PASS at **0.25847**, a 74.2% reduction against a bar of ≤0.70.
G2 FAIL at **26.9%** against >50%, where G2 counts the fraction of the top decile of |β−1| whose
cell centres lie in the pre-declared window (0 ≤ x/h ≤ 6, 0 ≤ y/h ≤ 2). It also failed *before*
the objective repair, at **29.0%**. So the repair moved the objective by a factor of four and
moved the geography slightly the wrong way.

**The window is not the suspect, and I checked before assuming it was.** The re-inversion
pre-registration's amendment D records a stage-A loss audit that *confirmed* the window: those
cells carry **41.2% of the loss on 8.4% of the cells**, the largest loss-per-cell concentration
in the domain, and the amendment route that could have moved the window was deliberately not used.
So the loss is inside the window and the correction is not — 39.6% of the top decile sits upstream
of the step crest, 31.5% above the shear layer.

**Two readings survive and nobody has separated them.** Either model-form error in this closure
is set upstream by boundary-layer history and merely *expressed* in the bubble — a physical claim
worth publishing — or the inversion deposits its correction wherever the adjoint is loudest,
which is a statement about identifiability and not about turbulence at all.

**Falsifier.** Spearman rank correlation between |β_final − 1| and |g(β=1)| over all 21,000 cells,
plus top-decile overlap against a 10% chance level. SENSITIVITY-DRIVEN at ρ ≥ 0.6 and overlap ≥ 40%;
PHYSICAL at ρ ≤ 0.3 and overlap ≤ 15%; **UNDECIDED in between, reported as undecided and not forced.**

**§2a identity test — could a wrong treatment still pass?** **Yes, and this is the one real hazard.**
An inversion that barely moved would satisfy β − 1 ∝ −α·g **by construction** from its own first
gradient step, scoring a high ρ while proving nothing. That is why the fitted first-step prediction
is gated as an explicit null model, and why this run qualifies: 16 evaluations, 74.2% objective
reduction, ‖g‖ down by 106×. If the measured field and the fitted first step agree beyond ρ = 0.9,
the run is declared TOO CLOSE TO ITS FIRST STEP and the comparison is inconclusive, not a verdict.

**External referent.** The **window geometry** is checked against the separation and reattachment
locations of the Bentaleb, Lardeau & Leschziner (2012) LES of this exact configuration (*Journal of
Turbulence*; distributed on the NASA Turbulence Modeling Resource "Other LES Data" pages, verified
2026-08-11: Re = 13,700 on step height and inlet velocity, channel height 8.52h — matching ours).
**The correlation itself has NO external referent** and the proposal says so: it is a relationship
between two of our own archived arrays, diagnostic rather than validating.

**Cost basis.** Zero solver compute, and the basis for the zero is that **every input was verified
present on disk before filing** (`find`, executed, 2026-08-11):

| array | run directory | bytes |
|---|---|---|
| `beta_final.npy`, `grad_anchor8.npy`, `grad_eval001.npy`, `dv_to_serial_perm.npy` | `/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/cbfs_inv/` | 168,128 each |
| `fields_beta.npy`, `fields_C.npy`, `idx_topdecile.npy`, `mask_win.npy` | `/home/ubuntu/certonomous-runs/S1-cbfs-inversion/` | 168,128 / 504,128 / 16,928 / 21,128 |
| `grad_eval001.npy`, `grad_eval010.npy` | `/home/ubuntu/certonomous-runs/S1-cbfs-inversion/cbfs_inv/` | 168,128 each |

Precedent for pricing this class at zero: the D9 plateau-balance reconciliation recomputed three
published figures from two of these same arrays at zero solver compute and closed a disputed correction.

**What kills it early.** The gradient is in design-variable order and the fields are in serial cell
order. If `dv_to_serial_perm.npy` cannot be *proven* correct by a permute-invert-assert control, the
comparison stops there — a correlation between two differently ordered arrays is a number with no
meaning. One minute of work, and the proposal makes it step one.

**The capability limit that makes this the only shot.** Both inversion drivers delete the
per-evaluation gradient (`invert_lbfgsb.py:97`: `if neval > 1 and neval % 10 != 0: os.remove(gpath)`).
**Nine gradient arrays survive in the entire archive.** No L-BFGS curvature pair (`y_k = g_{k+1} − g_k`)
is reconstructible from any completed run — the step `s_k` survives in the accepted-iterate files and
its partner does not. Buying curvature as fresh gradients is **forced, not chosen**, which is what
prices the whole Bayesian line and is why R1 is worth running before any of it.

---

## R2 — The reordering lever 257 runs requested and none proved

**Horizon: cheap and compounding. Cost: 8 core-min. FILED** as
`the-reordering-lever-257-runs-requested-and-none-proved`.

**Open problem closed:** docket **D10**, filed today from `docs/DEAD_LEVER_AUDIT.md` §4 U-1; docket
**B7** (the L-40 dead-lever class, the lab's most-cited lesson at 104 citations and its least mechanised).

**The measurement that motivates it.** Frame: 1,635 `*.log` files under `certonomous-runs` +
`Certonomous`, `/usr/bin/grep -lI`, 2026-08-11 17:24 UTC, repo `11b44cab`. **386** logs print the
requested `Mat ReOrdering:`; **257** request `rcm`; **8** carry a `matrix ordering:` readback from
the solver; the intersection of the last two is **0**. Meanwhile `rcm` is separately proven effective
five times — which is exactly the configuration that makes an unproven lever look settled.

**And the mechanism is already exhibited.** `A3-stage2-gamg/stage2_gamg.log:864,867,868` prints
`ASM Overlap: 1`, `Mat ReOrdering: natural` and `ILU PC Fill Level: 0` while that same run's
`-ksp_view` at `:884` shows `type: gamg`, and the file contains **0** `type: asm` and **0** `type: ilu`
objects (positive control: `A3-gateB-restoration/gateB.log` returns 1 of each). The wrapper prints
its levers regardless of which preconditioner was built.

**Falsifier.** Two arms of the archived rung-4 hump adjoint configuration to iteration 10 with
`-ksp_view` on: `natural` vs `rcm`. **DEAD** if the two PETSc dumps report the same ordering.
**ACTIVE** if they differ and each matches its request. **NO VERDICT** if neither dump carries an
ordering line — that is a statement about what this build exposes.

**§2a identity test — could a wrong treatment still pass?** **Yes, trivially, and that is the whole
point of the design.** A gate phrased as *"did the arm converge"* or *"did the wrapper print rcm"*
passes with the lever completely dead — the wrapper's own print is the surface the audit demonstrated
lying. Neither is gated. The PETSc dump is. Two arms rather than one because a single `natural` arm
cannot discriminate against PETSc's own default, which may also be natural.

**External referent.** PETSc's `-ksp_view` self-report on the object it built. **External to DAFoam's
wrapper**, which is the surface under suspicion, and **not external to PETSc**, which is stated rather
than glossed: there is no third party here who can tell us what PETSc built.

**Cost basis.** 8 core-min, from measured wall in the archived hump logs: two arms × 4 ranks × ~1 min,
because the adjoint's cost to iteration 10 is dominated by the ~112 s coloring and assembly phase
measured at `hump_adjoint_run1.log:2268`. Cross-check on the same box and solver family: the A3 rung-2
comparison dump cost **6.2 core-min** for a two-configuration diagnostic of the same shape
(`A3_SAAD_DELIBERATE_CONDITIONING_PREREGISTRATION.md:125`); the W1 hump two-arm challenge cost
**10.6 core-min** at 51,626 cells. Hard stop at iteration 10 bounds overrun by construction.

**Why it compounds.** 257 archived runs inherit the answer at once. That is the only reason to buy
it rather than caveat each conclusion that cites it.

---

## R3 — Triangulate the F7a reference before buying more free-surface mesh

**Horizon: cheap and compounding. Cost: 0 core-min. FILED** as
`f7a-triangulate-the-reference-before-buying-more-free-surface-mesh`.

**Open problem closed:** `PRODUCT_LIST.md` §4F, *"F7a-fix: diagnose and re-gate (free-surface stack
must pass its cheapest case before hulls)"*; naval ladder rung **S0**, which under the ladder rule
blocks F7b, F7c and every seakeeping item.

**The situation.** The gate FAILS at **+11.03%**. Its reference is eight points **digitised twice,
carefully, from Fig. 7 of a secondary source** (Leakey, Glenis & Hewett, arXiv:2108.08769, published
*CMAME* 393:114763, 2022). `F7a_REGATE_SPEC.md` §2.4 states in its own words that the primary paper
*"is not open access and has not been read by this lab"*, and carries that limitation on the verdict's
face rather than burying it. Two further facts point the same direction:

- **The comparator itself sits +23.3% from us** with physics, mesh and domain all matched
  (`F7a_REGATE_SPEC.md` §on `res16_papermodel`) — an offset more than twice the residual being chased.
- **The refinement rung was already recommended against**, at 760–1,520 core-min, on the measured
  grounds that it explores a direction shown to be small (docket **G1a**).

**What has never been done is the cheap thing: ask whether the reference is where the disagreement lives.**

**Falsifier.** Enumerate every published route to the Martin & Moyce square-column data and **class
each by its route** — primary tables read directly, re-tabulation by someone who read them, or
figure digitisation. **Exonerated (direction dies)** if ≥2 *independent* routes agree with the frozen
eight-point table within the recorded digitisation tolerance (≤0.01 in T, ≤0.005 in Z). **Disputed**
if two independent routes disagree with the frozen table, or each other, by >5% at any graded station
— 5% being the gate's own tolerance, so a reference spread that wide means the gate is **not decidable
against this benchmark at all** and S0 must move rather than be refined toward.

**§2a identity test — could a wrong treatment still pass?** **Yes, by one specific route:** counting
two sources as independent when both digitised the same figure, manufacturing agreement out of a single
origin. Route classification is therefore gated and mere source-counting is not.

**External referent.** The item *is* an external-referent audit. The referent is **Martin & Moyce (1952),
*Phil. Trans. R. Soc. A* 244:312–324**, "An experimental study of the collapse of liquid columns on a
rigid horizontal plane" — bibliographic details verified 2026-08-11 (Royal Society, JSTOR, Semantic
Scholar all resolve). **Access is UNVERIFIED** and may fail, in which case the item reports what it
could and could not obtain. **Labelled unverified:** the dam-break literature places this configuration's
data in that paper's own **tables 2 and 6** rather than in a figure. I found that assertion in secondary
sources and have not confirmed it against the paper. If it holds, the current reference is a digitisation
of a rendering of a table that exists.

**Cost basis.** Zero solver compute, and the basis is that the machinery to spend it has already been
proven unnecessary here: `F7a_REGATE_SPEC.md` §3 took the re-gate verdict **at zero core-min from
already-tracked field data**. Re-grading against a corrected table is arithmetic over data on disk.

**What kills it early.** If no second independent route exists in the open literature, report that and
stop — the benchmark is single-sourced for us, which is itself the finding.

---

## R4 — Per-family cost scaling laws, scored on held-out runs

**Horizon: cheap and compounding. Cost: 0 core-min. FILED** as
`per-family-cost-scaling-laws-scored-on-held-out-runs`.

**Open problem closed:** `CAPABILITY_STRATEGY.md` §4 item 1, *"Cost model v2: per-family scaling laws
with confidence bands; forecasts auto-approve when 3-for-3 within 20%"* — a strategy item that was
**never filed** (the 2026-08-10 filing pass covered §1–§3 only).

**Why it is fundable now, and it was not last week.** The measured history is much larger than the
three scored pairs suggest. A sweep run for this filing found measured cost across every family that
matters, and — more importantly — found **the structure a naive fit would miss**:

| family | measured anchor | source |
|---|---|---|
| interFoam free-surface | **15 cases, 4,800 → 153,600 cells**, wall and ranks per case (0.5 → 190.2 core-min) | `F7a_REGATE_PREREGISTRATION.md:95-102` |
| DAFoam adjoint gradient (CBFS) | **17 consecutive evals, 15.83 → 17.70 core-min**, summing to 335.98 | `/home/ubuntu/certonomous-runs/S1-cbfs-inversion/ledger.csv` |
| steady RANS 80k–500k cells | **6.2 core-min for three Ahmed rungs at 4 ranks**; B52 rung 7 at 12.14, rung 8 at 19.1 | `W3_LADDER_RECIPE_AUDIT.md:197`; `B52_RUNG{7,8}_RESULTS.md` |
| periodic hills | 4 rungs, 1.71 → 25.57 core-min, 7,728 → 62,400 cells | `F6b_ERCOFTAC_RESULTS.md:39-48` |
| model-form batch | 36 cells, 101.5 core-min total, per-cell records | `MODEL_FORM_BAND.json` |

**The load-bearing finding.** Cost is **not** linear in cells for time-accurate free-surface work:
halving the wall-normal spacing doubles the cells *and* halves the Courant-limited timestep, so the
step is at least 4×. **The measured a/128 → a/256 step was 8.0×.** That number lives in one results
record and is used in **no** proposal.

**And it exposes a pricing defect on the board today.** `f7-seakeeping-added-resistance-capability-step`
states in its own `cost_basis` that *"no wave case has ever been timed on this machine and there is
nothing to scale from"*. **There is** — fifteen interFoam cases with wall time and rank count per case.
The estimate may still be right; it is not currently *derived*, which is what
`COMPUTE_BUDGET_CHARTER.md` §2 requires.

**Falsifier.** For each family with ≥4 measured points spanning ≥4× in the size variable: hold out the
single most recent run, **commit the fit and the predicted band before reading the held-out actual**,
then score. HIT if the actual falls inside the band **and** the point prediction is within 20%.
Publish the hit rate whatever it is, in the manner the calibration scorecard already publishes 0 of 3.

**§2a identity test — could a wrong treatment still pass?** **Yes, by two routes, both closed.** A law
fitted on all points including the held-out one reproduces it by construction — hence the hold-out is
declared, and the fit committed, before the actual is read, in separate commits so the ordering is
*provable* rather than asserted. And a band made wide enough to contain anything passes the containment
leg trivially — hence the 20% point criterion is gated alongside it and band width is reported per family.

**External referent. NONE, and stated rather than glossed.** These are this lab's own costs on this
lab's own box; no published value exists for what a solve should cost here. The held-out actual is
external to the **fit**, which is the only independence this design can claim, and it is claimed as
exactly that.

**Cost basis.** Zero solver compute — every input is a cost already paid and written down. Basis gross.
The second deliverable is the list of families whose costs are **unrecoverable**: the durable archive
holds **477 run directories**, and the central registry records a cost figure for only **3 of its 142**
completion records. That asymmetry is why this is a fitting task rather than a query, and it is the
list the record needs before the next sixteen items close without one.

> **Warning carried into the item:** the `0.145 core-s/iteration` figure at `F8_MRF_HAND2001_GATE.md:182`
> is contradicted by its own document (it is 0.58 divided by the four ranks a second time) and the docket
> forbids its use twice. Cite 0.54–0.60 core-s/iteration at 230,135 cells and name the bad figure explicitly.

---

## R5 — The whitened re-inversion: does the correction move when sensitivity is divided out?

**Horizon: a real result. Cost: 340 core-min, on the best measured basis in the lab. FILED** as
`s1-whitened-reinversion-does-the-correction-move-when-sensitivity-is-divided-out`.

**Open problem closed:** `PRODUCT_LIST.md` §4A Stage 1 (the failing geography gate) and Stage 2, which
is blocked behind it; `CAPABILITY_STRATEGY.md` §3, *"Bayesian inverse problems → PROOF: S1's
regularization chosen by theory"*.

**The idea, and it is a standard one in inverse problems that this lab has not applied.** The
regulariser is an unweighted L2 pull of β toward 1, applied identically in every cell. Under that
choice the optimiser buys objective reduction most cheaply where the sensitivity is largest, so the
correction concentrates **by construction** wherever the adjoint is loud — independently of where the
model is wrong. The geography gate has now failed twice under that formulation (29.0%, then 26.9%)
while a loss audit puts 41.2% of the loss inside the window. The standard cure for that shape is to
**whiten the prior by the sensitivity**, not to move the window or relax the bar.

**Falsifier.** G-W2: G2 measured identically to the published definition — same 2,100-cell top decile,
same window, same cell-centre test. PASS above 50%, FAIL below. **G-W3 gates the objective at the same
time**: G1 must stay ≤ 0.70. A whitened arm that crosses G2 by abandoning the objective is a FAIL of
the whole item, **declared here so it cannot be renegotiated afterward**. G-W1 is a reproduction control
that must run first: the archived final iterate must reproduce 0.25847 and 26.9%, or the comparison has
no origin and the item stops.

**§2a identity test — could a wrong treatment still pass?** **Yes, by a route worth naming.** Whitening
by the sensitivity *mechanically* pushes correction away from high-sensitivity cells; if those cells
happen to sit outside the window, G2 rises for a reason with nothing to do with turbulence. That is why
G-W3 gates the objective simultaneously — a correction that entered the window without keeping the
objective reduction has found the **null space**, not the model error — and it is why **R1 is a
prerequisite rather than a nicety**: R1 measures where the high-sensitivity cells are, so this arm's
outcome can be *read*.

**External referent. NONE for the gate**, and the proposal says so. G2 is measured against a window this
lab declared, using this lab's solver and mesh; no published value exists for the fraction of a
correction field lying in a window. The window's **physical anchoring** does have one — the Bentaleb
LES separation and reattachment locations — and the pre-registration must state which it brackets.

**Cost basis — measured, on the identical operation.** The immediately preceding re-inversion billed
**320.13 core-min for 16 evaluations**, 20.0 core-min/eval; the separately measured anchor evaluation
at the same primal tolerance took **599 s wall at 2 cores = 19.97 core-min**, agreeing to three parts
in a thousand. The final-state cold control plus write-out was measured twice on this line at **8.10**
and **8.54**. So 16 × 20.0 + 8.5 = **328.5**, taken at **340** to carry contention, where the same
evaluations measured 26.5–27.1. Independent cross-check: the earlier inversion at 4 ranks and a looser
tolerance measured 17 consecutive evaluations at 15.83–17.70, summing to 335.98. **Stable across two
runs, two rank counts and two tolerances.** Residual risk is contention, not physics. Basis gross.

**Why a domain expert would recognise it as work.** It separates a regularisation choice from a physical
claim in a field inversion, and it publishes whichever way it lands. A PASS says the correction
concentrates in the separated region once the penalty is geometrically fair — a statement about how
field inversion must be regularised. A FAIL is the stronger physical result: model-form error set
upstream of the region carrying the loss, meaning a closure learned only inside the bubble is learning
the wrong thing.

---

## R6 — Band-containment census: how many scoreable pairs does this lab own?

**Horizon: ambitious, and the kill test is free. Cost: 0 core-min for the census; the curve is unpriced
until it returns. FILED** as `band-containment-census-how-many-scoreable-pairs-does-this-lab-own`.

**Open problem closed:** `PRODUCT_LIST.md` §4I, *"Band machinery"*, open; `CAPABILITY_STRATEGY.md` §1
(calibration scorecard) and §3 (calibration & validation theory).

**The ambition, stated plainly.** The standing directive is that every result ships with a band. Nobody
has asked whether those bands are **calibrated**. A band is a probabilistic claim, and a probabilistic
claim never scored against outcomes is decoration. The lab already asks this of its *cost* forecasts and
publishes the bad answer (0 of 3); it has never asked it of its *physical* predictions, which are the
ones a customer would rely on. **A reliability curve over a lab's own CFD predictions — nominal coverage
against empirical coverage — is a thing essentially nobody in applied CFD ships.** That is where this lab
could be distinctive in six months.

**The evidence that it should be asked, and it points both ways.** The flat-plate propagation rung
produced a coefficient band spanning **30.3% of the reference Cd, ~104× the +0.29% validation
discrepancy**, and separately recorded that the GP error bars on that line were **~3× too narrow** — a
finding recorded and then used nowhere. The standing model-form batch produced a four-closure spread of
**62.4%** on one plate case that **does** contain the CFL3D SST-V reference, and honestly refused a band
on a family where every closure stalled. Those are individual containment facts. A reliability curve is
what turns them into a calibration statement.

**Falsifier — of the census, which is the fundable step.** GO if ≥8 admissible pairs exist; NO-GO below,
in which case the deliverable becomes a priced list of the cheapest cells that would make the curve
drawable. A pair is admissible only with (a) a published band carrying a stated nominal coverage and
channel composition and (b) a truth value from **outside this lab** that was not used to centre, tune or
calibrate that band. Three classes — ADMISSIBLE, EXCLUDED-NO-EXTERNAL-TRUTH, EXCLUDED-TRUTH-USED-IN-CONSTRUCTION
— and **all three counts are published**; a census reporting only its survivors is a shape this lab has
already been caught in.

**§2a identity test — could a wrong treatment still pass?** **Yes, and this is the central hazard of the
whole direction, which is exactly why it is gated at the census rather than discovered at the curve.**
If the truth used to score containment is the same number the band was centred on or calibrated against,
**containment is an identity** and every band contains its truth by construction. The
EXCLUDED-TRUTH-USED-IN-CONSTRUCTION class exists to make that countable rather than invisible; a pair
whose class cannot be determined is excluded and said so.

**External referent.** One per admissible pair, **by construction** — a pair with no external referent is
not admissible. That is the whole admission rule, and it is why this direction cannot run on our own
machinery alone (L-74).

**What would have to be true, and what kills it early and cheaply.** It needs enough (band, external truth)
pairs to draw a curve. **Counting them costs nothing.** If the count is below 8, the ambition converts into
"buy external truth values, not more bands" — and that redirection is worth more than a curve drawn on
five points would have been. The only rate anchor for filling cells, if GO: the model-form batch at
**101.5 core-min for 36 cells**.

---

## R7 — NACA Report 1191 settles which Strouhal form governs the filmed gate

**Horizon: cheap and compounding. Cost: 0 core-min. FILED** as
`naca-report-1191-settles-which-strouhal-form-governs-the-filmed-gate`.

**Open problem closed:** docket **D12**, and **D13** behind it.

**The situation.** `NINE_ACT_GATE_TABLE.md:3` grades act 1 PASS at 0.77% against *"Strouhal vs
Roshko-Williamson correlation"*, reference 0.1590. The constants come from
`sdk/workflows/_exact_theory.py:253-260`, `St = 0.198(1 − 19.7/Re)`, whose docstring warrants them as
*"the exact form this lab's Re=100-180 cylinder family already gated against"* — i.e. attributed to the
task prompt. **The one form the repo cites to a paper disagrees**: `cylinder_vortex_shedding.py:22-24`
gives Roshko (1954), NACA Report 1191, as `St ≈ 0.212(1 − 21.2/Re)`. Executed arithmetic at Re = 100:
used form **0.158994** → **0.75%, PASS**; cited form **0.167056** → **5.54%, a miss**. The discrepancy
is seven times the passing margin, and it is on a camera surface.

**Falsifier.** The report either supports the used form with those constants over a range including
Re = 100, or it does not. SUPPORTED → re-cite the constants to the report and the act stands.
NOT SUPPORTED → re-grade against what the report supports, and **if the regrade is a miss it is
published as a miss**. NOT OBTAINED → the gate carries an explicit face caveat that its constant has no
cited source, which is its true present state.

**§2a identity test — could a wrong treatment still pass?** A check comparing our arithmetic against our
own constants passes with the attribution entirely wrong. **That is the state the gate is in today**,
and it is why the only admissible evidence is the report itself. No internal check substitutes.

**External referent.** Roshko (1954), NACA Report 1191, "On the development of turbulent wakes from
vortex streets" — open on the NASA technical reports server. Bibliographic identity taken from the
repository's own citation; **the report has not been read by this lab**, which is the defect.

**Cost basis.** Zero compute — the measured shedding value is already on the record, so a regrade is one
division, and the arithmetic establishing the discrepancy was already done host-side at zero compute
during the B6 audit.

**What kills it early.** Nothing; it is a bounded read with a three-valued answer. It is the smallest
complete instance of §6a (the referent travels with the verdict), and it sits on a surface Katie films.

---

## R8 — A physics-informed, transferable prior on the discrepancy field

**Horizon: ambitious. Unpriced. NOT FILED — and the reason is the point.**

**Open problem it would close:** `CAPABILITY_STRATEGY.md` §3, *"Bayesian inverse problems → PROOF: S1's
regularization chosen by theory (prior interpretation), posterior uncertainty on beta reported, not just
a point field"*; `PRODUCT_LIST.md` §4A Stages 1–2.

**Where this lab could be genuinely distinctive in six months.** Today the regulariser is "β near 1
everywhere" with a hand-set λ. If R1 returns PHYSICAL — the correction's geography is a property of the
flow and not of the adjoint — then the *location* of model-form error is a learnable, transferable
structure, and the right prior is not "β near 1 everywhere" but **"β departs from 1 in the separated
shear layer and nowhere else"**, encoded as a spatially varying prior variance keyed to a flow-feature
marker. That is a prior chosen by theory, which is exactly the PROOF clause, and a *transferable* prior
on the discrepancy field is a contribution in its own right rather than a case result.

**What would have to be true.** (a) The correction geography is physical, not the adjoint's sensitivity
map — **R1 decides this, at zero compute.** (b) A hump adjoint converges. It currently does not:
`PRODUCT_LIST.md` §4A records, corrected 2026-08-11, that the hump's adjoint boundary is
**UNCHARACTERISED, not diagnosed** — the account rested on one attempt killed at iteration 900 whose log
contains `ConvergedReason` zero times. **We equally have no evidence the operator is singular.** That is
a live blocker this direction inherits and which is not priced here.

**Falsifier, and it is a transfer test.** Fit the prior's *structure* on CBFS, apply it **unchanged** to
the NASA hump, and require the posterior to contain the reference truth. If the hump needs a different
prior, the structure is case-specific and the direction dies as a generalisation — it survives as a
per-case regulariser, which is worth much less and should be named as such rather than sold as the same
thing.

**§2a identity test.** The hazard is sharp: if the flow-feature marker is derived from the same solve
whose error it is meant to predict, **the prior is fitted to its own target** and the transfer test is
an identity. Hard constraint: the marker must be computable from the **baseline β = 1 solve alone**,
before any inversion.

**External referent.** The hump's LES/experimental reference for the transfer leg. The prior's *form*
has none and would have to say so.

**What kills it early and cheaply: R1, at zero compute.** If ρ is high, there is no physical geography
to build a prior on and R8 should not be bought at all.

**Why it is not filed.** It is blocked behind R1's verdict *and* behind an uncharacterised hump adjoint,
and filing a costed proposal now would mean pricing an analogy. That is precisely the error the 8× F8
overrun records. It goes in the ambition slot; it does not go in the queue yet.

---

## R9 — Regular-wave added resistance, and the two pieces that would make irregular seas reachable

**Horizon: ambitious. Unpriced. NOT FILED as new — recommend amending the existing proposal.**

**Open problem:** docket **G4**; `NAVAL_CAPABILITY_GAP_MAP.md` §5 rung S6, the map's one flat *"cannot"*.

**The distinctive claim.** A validated, open, end-to-end **spectral added-resistance capability** built
on vanilla OpenFOAM, with a pre-registered averaging contract, is rare. Added resistance is *a small
difference of two large, noisy, time-averaged forces* — and this lab's actual comparative advantage is
measurement-definition discipline (`F7a_REGATE_SPEC.md` exists because an unpinned front definition
produced +13.4% and −16.1% on the same solve). That discipline is exactly what the quantity needs.

**What is genuinely missing**, per the gap map §5, and it is new development rather than configuration:

1. **A spectrum discretiser we write ourselves** — JONSWAP or Pierson-Moskowitz sampled into the explicit
   `wavePeriods` / `waveHeights` / `wavePhases` / `waveDirections` component tables
   `irregularMultiDirectional` demands. No named spectra ship. This is precisely the unchecked-helper
   hazard docket B6 names, so it needs validation against a published spectrum, not just a plot.
2. **An absorber that survives a broadbanded sea.** `shallowWaterAbsorption` at a single outlet patch is
   the only absorber we have; the published irregular-sea literature replaces it with relaxation zones,
   which we do not have in either native or third-party form.

**What would have to be true.** Patch-local absorption holds up against a multi-frequency train. **This
is unknown to us and untested**, and it is the genuine technical risk: a reflecting outlet contaminates
the very mean force added resistance is defined as.

**What kills it early and cheaply — and this is the recommendation.** A **two-frequency train in an empty
flume**, with along-flume wave-height variation measured against a declared band. If the variation exceeds
the band, the outlet reflects and the entire S6 branch dies **before a hull is ever meshed**. That is a
small addition to the already-filed `f7-seakeeping-added-resistance-capability-step` (135 core-min), whose
stage W2 currently tests a *single* regular wave. **Recommend amending that proposal's W2 to add the
two-frequency arm rather than filing a duplicate** — its pre-registration is not yet frozen and Verification
Charter §2b makes amendment legal only while there is no answer to tune to, which is now.

**External referent.** For the discretiser: a published spectrum (JONSWAP's own definition is analytic, so
this leg has an **exact analytic referent**). For added resistance: published model-scale added-resistance
data, which the gap map has **not** yet verified as obtainable — labelled unverified.

**And the honest caveat the gap map insists on:** *"an agent that discovers we lack the boundary conditions
and quietly substitutes something else has destroyed the deliverable."* No proposal on this line may imply
S6 is reachable today.

---

## R10 — Wigley hull wave resistance

**Horizon: a real result. NOT FILED — measure the rate first.**

**Open problem:** `PRODUCT_LIST.md` §4F, *"F7b Wigley hull wave resistance"*, open and never attempted;
docket **G2**.

**Why it looks ready.** Geometry is not a risk: `wigley.stl.gz` (301,385 B) **ships with OpenFOAM** and
was verified on disk. Three Froude stations are already pinned with justification
(`NAVAL_CAPABILITY_GAP_MAP.md` §6.2a): **Fr = 0.250, 0.289, 0.316**, chosen because 0.250 and 0.316 each
carry **both** a tabulated CT *and* Kajitani wave-profile data. The marine section of `MESH_STANDARD` §7
already landed.

**Falsifier.** CT at Fr 0.250 and 0.316 against **0.003340** and **0.003620** (*Fluids* 9(11) 266, citing
Bai & McCarthy 1979), on two mesh rungs against a pre-registered band; wave profile at Fr 0.289 against
Kajitani et al. 1983 (17th ITTC, DTIC ADP003037) as an independent second quantity.

**§2a identity test — could a wrong treatment still pass?** **Yes, and it is the classic naval one.** CT
is often reported via a form factor plus an ITTC-57 friction line; if the friction line is *our* choice,
the "wave resistance" is partly definitional and a wrong solve can be made to agree. **Gate on total CT,
which the tank measured**, and report Cw separately with its decomposition named. A wrong treatment can
pass a Cw gate by choosing the friction line; it cannot pass a CT gate that way.

**External referent.** Two independent routes, per the gap map's verified literature pass — and both
disclosures ride with any gate spec: Kajitani's **Cw/CT vs Fn is FIGURE-ONLY** and must be digitised from
page images (the 1983 scan's OCR text layer is unreliable), and the **YNU 2.0 m geosim must not be pooled**
(L/B = 8, B/D = 2.0 — a different hull form).

**Why it is not filed: the cost basis is not there yet, and I will not invent one.** No hull case has ever
run here. The gap map prices the shipped `DTCHull` tutorial at 100–400 core-min and says the width **is
the point**. The nearest measured anchors are the fifteen interFoam dam-break cases (0.5 core-min at 4,800
cells → 190.2 at 153,600) and F8's 0.54–0.60 core-s/iteration at 230,135 cells — a *steady, single-phase*
case, which under-prices a Courant-limited VOF hull by an unknown factor. **Recommended sequencing: R4
first (it fits the free-surface scaling law from the fifteen measured cases), then the `DTCHull` tutorial
as the rate measurement, then Wigley priced against both.** Filing a number now would be exactly the
analogy-priced estimate that produced the 8× overrun.

**It is also blocked** behind S0 under the ladder rule, which is what **R3** is for.

---

## If Katie buys only one

**R1.** It costs nothing, every input is verified on disk, and it interrogates a **published FAIL verdict**
on the lab's flagship line that currently travels with no diagnosis at all. It is also the early-kill for
the two most ambitious directions here: R5 (340 core-min) and R8 (unpriced) are both premised on an answer
nobody has measured. If R1 returns SENSITIVITY-DRIVEN, it retires the physical reading of the 26.9% figure
in two published records and redirects the 340 core-min before it is spent. If it returns PHYSICAL, it is
the stronger result and it makes R8 fundable.

**The tension, stated rather than hidden:** Katie's stated preference is ambition in the next-investigation
slot, and R1 is not ambitious — it is a correlation over two arrays. **R8 belongs in the ambition slot.
R1 is what makes R8 safe to enter.** If "fund" means "spend compute", the answer is **R2 at 8 core-min**:
it settles a lever for 257 archived runs at once and is the cheapest class-level answer on the board.

---

## Filing record

Seven proposals written to `demo-output/website/agenda/proposals/`, each validated with
`agenda.proposal_violations` and `agenda.premise_violations` **executed on the file as written**, not assumed:

| id | est_core_min | source_kind | hard_criterion | violations | premise |
|---|---|---|---|---|---|
| `s1-does-the-correction-land-where-the-error-is-or-where-the-sensitivity-is` | 0 | measurement | no-case | **0** | 0 |
| `the-reordering-lever-257-runs-requested-and-none-proved` | 8 | capability | instrument-check | **0** | 0 |
| `f7a-triangulate-the-reference-before-buying-more-free-surface-mesh` | 0 | reading | no-case | **0** | 0 |
| `per-family-cost-scaling-laws-scored-on-held-out-runs` | 0 | ledger | no-case | **0** | 0 |
| `s1-whitened-reinversion-does-the-correction-move-when-sensitivity-is-divided-out` | 340 | gate | existing-family | **0** | 0 |
| `band-containment-census-how-many-scoreable-pairs-does-this-lab-own` | 0 | measurement | no-case | **0** | 0 |
| `naca-report-1191-settles-which-strouhal-form-governs-the-filmed-gate` | 0 | reading | no-case | **0** | 0 |

All seven load through `agenda.read_inbox()` (executed: inbox 117 records from 121 files; the 4
non-loading files pre-date this filing). Filename stem equals `id` on all seven; one-space indent;
`status: proposed` on all seven — **not** `queued`, which is not in the enum.

One draft was caught by the rails and repaired before writing: the cost-model rationale carried
*"a live pricing defect"*, which trips the banned-word rail. It was reworded, not exempted. **The rails
were run on every file rather than assumed** — three naval proposals filed earlier today each carried
8–11 violations that discard silently.

## What I did not do

- **Launched nothing.** No solver, no container, no compute of any kind.
- **Sent nothing.** No email, no upload, no registration, no external interaction. The closure
  submission stays parked and reserved to Katie.
- **Filed no docket IDs.** Docket IDs are append-only (W-4) and the docket is under concurrent
  edit tonight; the three directions that would add rows (R3 → G-series, R7 → D12/D13) say so in
  their `launch_prompt` and leave the write to the executing agent, which is the claim-before-dispatch
  rule in B's own header.
- **Did not edit any filed proposal.** R4's finding that the seakeeping `cost_basis` understates the
  available measured history, and R9's recommendation to amend that proposal's stage W2, are both
  routed through R4's own item rather than applied here.
- **Did not read Martin & Moyce (1952), NACA Report 1191, or the Bentaleb LES data files.** Every claim
  drawn from them is labelled with what was and was not checked, and the two literature items are the
  deliverables of R3 and R7 rather than their premises.
