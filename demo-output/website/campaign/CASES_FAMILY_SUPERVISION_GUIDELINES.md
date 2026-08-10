# Cases/Campaigns family — supervision guidelines (v1.0, 2026-08-07)

Standing rules for the 2D and 3D benchmark families (product list §4C/§4D),
the standing model-form batch, and the new challenge slate, written by the
family's Fable supervisor under the SUPERVISION_CHARTER structure. Every rule
below is precedented in this family's own record; the precedent is cited so
the rule can be checked against it, argued with, or tightened — never
followed on faith. The chief supervisor retains scoring authorization,
cross-family arbitration, negative-verdict reviews, and product-list custody.

## 1. Pre-registered gates before any solve

1.1 **No solve without a committed pre-registration.** Gates, tolerances,
reference bands, predictions with numeric windows, budget, and disqualifiers
are committed before the first iteration runs (F6b: commit `31b0be16`; B52
rung 8: `48cfedfb`; F8: every section §1/§7/§11/§15 written before its
launch, with "*Nothing below this line existed when the run was launched*"
markers). This is also the fleet's survival mechanism: four fleet deaths,
zero scientific loss, precisely because the registration always predates the
compute.

1.2 **The verification gate and the physics gate are separate gates with
separate verdicts** — the F6b precedent is the family's canon. Gate V
(our pipeline reproduces the known answer on our own mesh: PASS at 0.043%)
and Gate P (the model against the literature band: FAIL at +72%) were
registered, run, and reported independently. A physics FAIL on a verified
pipeline is a *result*; a physics FAIL without a verification gate is an
argument. No family case registers a physics gate without stating what its
verification gate is and on which rung it is decided.

1.3 **Predictions are scored clause-by-clause and falsified predictions stay
in the record unedited** (F6b prediction 4, falsified by being too
pessimistic, left as written; B52 clause 2, FALSE as written and said so;
F8 §8/§12/§16 predictions scored FALSE or not-evaluable in their own words).
A pre-registration that gets quietly repaired afterwards is not one;
corrections are dated addenda that point at the error (F6b results §1b).

1.4 **When reality picks none of the registered branches, say so.** F8 §12's
divergence fit none of §11's three branches and was reported as exactly
that, not shoehorned into the nearest one. A registered rider or amendment
(dated, before launch) is the honest way to re-scope — see F8 §15.

## 2. Mesh-standard compliance, stated per rung

2.1 Every rung's record carries max non-orthogonality, max skewness, and max
aspect ratio from **that rung's own checkMesh log**, read against
`docs/standards/MESH_STANDARD.md`'s gates (F6b results §1 table; B52 rung 8;
model-form design §4.4). Aspect ratio is advisory and recorded, never a lone
rejection.

2.2 Topology deviations are recorded, not silently dropped (B52 rung 8's
"multiply connected (shared edge)" note is the model).

2.3 **Externally distributed grids are not exempt by silence.** The TMR
C-grid's 85.70° non-orthogonality mesh-gates all of model-form family N —
the batch's own validated baseline notwithstanding (finding C2,
`CASES_FAMILY_FIRST_PASS_FINDINGS_2026-08-07.md`). If a family needs a
distributed-grid exemption, the exemption is written into that family's
pre-registration and defended there, or the family moves to a compliant
grid. Nobody widens a gate after seeing a rung fail it.

2.4 Geometry provenance is verified before the pre-registration closes, at
zero compute, where a published description exists (F6b: the ERCOFTAC
polynomial vs the shipped wall to 1.3e-7 h, which caught a wrong cubic
segment at 60% of a hill height; F8 §10: chord/twist to millimeters against
TP-500-29955 Table A-1).

## 3. Convergence discipline

3.1 **Bands are min/max over converged cells only, and the exclusion list is
part of the result** — excluded members named with reasons in the artifact
(model-form design §4–5; the NASA hump lesson: one unconverged member moved
the whole containment verdict). A group with fewer than two converged
members has no band and says so.

3.2 **Unconverged forces are not gateable** (monitor standard L-24: a run is
not converged, a *quantity* is). The F8 precedent binds: a window whose
peak-to-peak spread is 960% of a pre-declared 50% cap returns **NO VERDICT**,
not FAIL — a mean of a series that never settled is not a measurement of
anything. Every window statistic (window bounds, band cap, S12 drift test)
is declared before the history is read.

3.3 **The S10/S12 taxonomy applies as written.** A "converged residual" with
a diverging or travelling quantity is a specimen, not a pass: F8 §12 is the
family's live S10 exhibit (Ux residual 1.4e-8 while the blade moment sat at
1e99). S12 (drift ≥ 1e-3 AND monotone fraction ≥ 0.90) grades settledness on
the quantity, scale-free; "settled" means "not travelling", not "flat", and
the record states which clause carried the verdict (F8 §8 honesty note).

3.4 **residualControl targets must be reachable, and a settle-watcher cap is
not a residualControl allowance.** Two family precedents: F6b's inherited
`p 1e-15` made the convergence sentence unprintable and produced a
documented gate-checker false negative (fixed by declared deviation); the
model-form batch's first pass guillotined nine cells at the ladder's
3000-iteration watcher number before adopting its own `BATCH_BACKSTOP`
(design §8a.1). Know which criterion a case's gate is, and size the cap for
that criterion.

3.5 A rung that hits its cap without meeting its criterion is reported
unconverged and its numbers labelled as such, never quietly promoted (F6b
fine rung: used with the label, verdict decided on the converged medium
rung). A rung that does not converge **at all** is a result, recorded with
competing readings ranked by test cost and the cheaper discriminator run
first (F6b §4: under-relaxation before unsteadiness; the unsteady reading
stays "a hypothesis, not a finding" until the cheap test runs).

3.6 Convergence gates are applied by the family's **own pre-registered
machinery**, not by whatever settle rule the underlying workflow happens to
carry — the model-form family-N miscarriage (workflow's absolute tail-50
rule pre-empting the batch's registered S12 gate, finding C1) is the
cautionary precedent. When a workflow guard fires, its message is recorded
AND the registered gate is still applied to the on-disk evidence.

## 4. Crash and anomaly triage (all precedented — cite the precedent, skip re-diagnosis)

| signature | precedent | first move |
| --- | --- | --- |
| FPE (`sigFpe`, exit −8) within ~50 iterations, k-family closures at high Re on wall-resolved grids | `B_re1p2e7_{kEpsilon,kOmegaSST,realizableKE}` records (S1 FATAL) | record FATAL, exclude, do not soften the gate; the diagnosis arm is a filed proposal (negative-verdict review §9), not an improvisation |
| Steady MRF case diverges after `potentialFoam -writephi` init | F8 §14: `makeAbsolute` bakes the frame's solid-body sweep into a whole-domain zone (`MRFZone.cxx:447-489`, `potentialFoam.C:187`) — a ~150 m/s initial hurricane against 7 m/s inflow | never `-writephi`-init a whole-domain MRF zone; init with the zone `active false`, then restore (F8 §15 arm A). The F5b potentialFoam cure is for non-rotating cases only |
| Violent force oscillation on a steady MRF rotor, torque opposing rotation | F8 §3/§16: steady branch closed three ways (geometry §10, frame terms §14, init §16) | do not spend steady iterations; the transient branch inherits the quantified target (turbine-signed, band ≤ 400 N·m vs 800 N·m) |
| Solver stops early / late vs expectation | model-form §8a.1 settle-watcher vs residualControl distinction | check which criterion sized the cap before touching numerics |
| `coefficient.dat` missing or renamed after restart/collection | model-form §8a.4 (SA plate, reproduced twice); memory: restart collision renames blind the watchers | grade from the solver log fallback; `qoi_source` must be stamped on the record |
| Run ends with no written fields | F8 §7: endTime not a writeInterval multiple writes nothing | check endTime ∣ writeInterval before declaring endTime; restart provenance stated |
| Impulsive-start divergence, non-rotating moving-mesh case | F5b (`pcorr` block; `potentialFoam -writephi` fix) | apply the F5b cure — outside rotating frames only (see row 2) |
| [AMENDED 2026-08-10: on F5c the premise of this row is now false — the solve does NOT converge numerically; see `F5C_STAGE_A_RESULTS.md` §6. Check convergence on the SIMPLE INITIAL residuals before classifying a case here.] Steady solve converges numerically but the answer wanders non-monotonically with iterations/algorithm on separated flow | F5c (4–12× wrong, wandering); F6b veryfine limit cycle | suspect the steady-state premise, not the closure constants; metric/normalisation audit first (L-25/L-28 class), then the cheap unsteadiness discriminator. A 4–12× miss is almost never the turbulence model |
| Wake-driven force oscillation on coarse C-grids | model-form design §3 known hazard | S12 excludes the cell; that is the design working, not failing |

Anything genuinely new gets the liaison's breakage-research protocol (online
research + method-doc iteration) before a diagnosis is invented in-house.

## 5. Escalation

5.1 **Any physics FAIL on a verified pipeline → the chief's negative-verdict
review.** Precedent: F6b's Gate-P FAIL entered
`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` §1. This family owns
executing that review's diagnostics 1–5, 9 and 10; each is run as filed,
pre-registered, costed — the review's wording is binding.

5.2 **Any proposed new family below the hardness floor → refuse** (case
selection charter; `W1_HARDNESS_FLOOR_RULING.md`; the slate's `no-case`
discipline — an unpriced, reference-less item like F10 is listed as
not-startable, not started).

5.3 **No scoring call, no external send, no upstream filing** originates in
this family — chief and Katie only. Gate-widening after the fact,
mesh-standard exemptions (§2.3), and any edit to `docs/PRODUCT_LIST.md`
(chief's custody) likewise go up, not through.

5.4 **A reference that cannot be reached in numeric form stops the item at
0 core-min** — BLOCKED, or a secondary source with its provenance tier
stated (F8 §2's 800 N·m secondary-tier handling; F5b's TP-1100 strip-chart
finding: check the detector before the physics). Denominator drift on the
docket (cost off by >3×) is corrected before launch (slate item 5).

## 6. Bookkeeping

6.1 `record.json`-class per-cell records are the unit of truth; bands,
ledgers and study records regenerate from them. Superseded records are
renamed, never deleted (`--redo-excluded` convention), and supersession
happens only after the budget/queue checks pass (finding C3).

6.2 Corrections are dated addenda naming who found what and pointing at the
authoritative record; original text stays in place. This pass's own
examples: the Re_H note on the 2026-07-29 F6b record, the TP-500-29494
conflation notes on the register and the slate.

6.3 Every item closes with a measured-vs-approved cost table (F8 §17; B52
rung 8; F6b §7), and honest accounting includes the expensive rung that
"failed" — F6b's non-converging rung was half the budget and the record
says it is the line it would be weakest without.

6.4 Fleet-death recovery: resume agents from transcript, reattach to
detached solves, never restart a watcher a dead agent owned (memory:
agent-watchers-die-with-the-agent); the pre-registration-first rule of §1.1
is what makes recovery cheap.

6.5 **Lever activity proof (L-40, Verification Charter v1.5 §9, Katie's
order 7be0afc2):** every load-bearing solver option, model choice or lever a
conclusion cites must be proven ACTIVE from the runtime log, not merely
present in a dictionary — "the switch you set is not the switch that ran."
New evidence records in this family carry `levers_verified_active` with the
proving log line per lever; the runner's record schema gains the field in
coordination with the Infra family (no schema fork here). This family's
QCR activity check (`QCR_ACTIVITY_CHECK_2026-08-08.md`) is the positive
template the lesson cites: selection line + coefficient banner + wired-in
term at file:line + field-level activity, with numbers.

## 7. Audit conventions — a recount is a measurement, a re-read is not

**Added 2026-08-10 on the chief's instruction, from two of my own arithmetic
slips found the same day.**

Both slips were in summary counts I had written myself, and **neither was found
by re-reading the document — both were found by recounting the rows.**

| slip | what re-reading gave | what recounting gave |
| --- | --- | --- |
| the B-52 turn's standing | "the turn sits inside the scatter at 1.32×" — read back as correct every time | a range over 3 draws compared against a pairwise difference: **two different statistics**, and the like-for-like number is 2.98× |
| the turn audit's summary table | "4 W, 22 A, 8 S" — read back as correct | **35 graded rows and 20 A**; the table had double-counted two split dispositions |

**The rule.** *A recount is a fresh measurement; a re-read is the same
measurement repeated.* Re-reading your own summary re-runs the reasoning that
produced it, including the error, and it feels like verification because the
text is familiar. Recounting from the underlying rows uses a different path to
the same number and can therefore disagree with it.

**Applies to:** any count, total, or summary statistic this family reports —
disposition tables, row counts, core-min totals, draw counts, gate tallies,
corpus sweeps.

**In practice.** When a document states a count, derive it a second time by a
different route before the document is committed — parse the rows
programmatically, or count from the artifact rather than the prose. Three of
this family's records now carry corrections found exactly this way, and each was
cheaper to make than to leave.

**Its sibling, already in the record:** `W3_MESH_NOISE_FLOOR_RESULTS.md` §3's
correction — *a range over n and a single pairwise difference are different
statistics and must not be compared*. That one is about which measurement you
took; this one is about whether you took it twice or looked at it twice.

### 7a. "A different route" must mean different IN KIND — and a search written from what you just read returns what you just read

**Added 2026-08-10, hours after §7, from the failure of §7's own first
application.** The draw-scatter rule's archive replay
(`W3_DRAW_SCATTER_RULE_REPLAY_RESULTS.md` §4b) derived its count twice as §7
requires. The two routes disagreed by **2×** on records and **3.4×** on the
number needing restatement, and **the programmatic route was the wrong one.**

**Failure 1 — a pattern that keys on one spelling cannot see the concept.**
Route A's regex spelled it `non-?monoton` and `increments grow|shrink`. Tested
against nine genuine ladder-shape assertions, **it caught one.** It could not see
`NOT monotonic` (space, not hyphen), `monotonically`, bare `monotone` used as an
argument, or `increment smaller`. This is the same defect the lab closed twice
that same day — `args[0]` instead of *does this launch a solver*, and splitting a
shell string to decide what ran. **It was written into the audit that was
checking for the first two.**

**Failure 2, and the one worth institutionalising — the miss was BIASED, not
noisy.** Route A's vocabulary was drawn from the records its author had spent the
day inside. It therefore found every ladder already under investigation and
missed nine bodies that were not. **A search built from what you have been
reading returns what you have been reading**, and it will feel exhaustive while
doing it, because everything you can think of to check is in it.

**The rule.** When §7 says derive the count by a different route, *different*
means **different in kind**, not the same method run twice:

| weak second route | strong second route |
| --- | --- |
| the same regex, re-read | a semantic sweep that does not share the first route's vocabulary |
| the same person recounting | an independent agent given the definition but not the patterns |
| grep with more synonyms *you* thought of | a route that can surface terms you did not think of |

**Practical test before trusting a count:** *could this method have found a
member of the class I have never seen?* If the method's vocabulary came from the
examples you already had, the answer is no, and the count is a lower bound rather
than a count. **Report it as a lower bound until a second route of a different
kind agrees.**

## 8. Ladder features need draw-scatter evidence (Verification Charter §17, adopted 2026-08-10)

**Binding on every ladder this family publishes.**

> **A ladder increment is not published as a FEATURE without draw-scatter
> evidence at the rung it turns on — or with the absence stated on its face.**

**Feature** = a claim about the SHAPE of a sequence of grid-refinement
increments (a turn, an oscillation, a divergence, a trend in increments,
monotonicity used as an argument). Rung values, bands, orders and
`conclusive: false` verdicts are not features.

**Remedy is RESTATEMENT.** An unchecked feature is unchecked, not false. Say so
where the feature is stated. Withdraw only what has been measured and did not
survive.

**In practice, for this family:**

1. **Before writing a shape claim, ask what the scatter is at the rung it turns
   on.** If nobody has measured it, the claim ships with that sentence attached.
2. **Two draws is the minimum that yields a number, and it is a weak one** — a
   single pairwise difference is a one-sample estimator of a scale, and this
   family has measured it disagreeing with an n = 5 sample by a factor of 2.6.
   Prefer n ≥ 3 at the deciding rung.
3. **Compare like with like.** A range over n draws and a single pairwise
   difference are different statistics (`W3_MESH_NOISE_FLOOR_RESULTS.md` §3), and
   both this family and its chief have published that comparison wrongly.
4. **An increment differences two singly-drawn rungs, so it carries √2σ, not σ** —
   or √(s₁² + s₂²) when the rungs' scatters are measured separately, which they
   should be.
5. **Calibrate the deciding bar by simulation against the null before the draws
   exist.** Never choose it after. State the false-positive rate on the face of
   the verdict, and **report a near miss as a near miss** — the Ahmed 25° arm
   missed its bar by 0.044 and said so. A bar that moves after the number is not
   a bar.
6. **The published draw can be an extremum and you will not know.** The B-52's
   turn was `max(rung 6) − min(rung 7)` of eight draws; nobody chose it that way.
   Check where the published draw sits in its own distribution.

### 7b. Different in kind protects the READING. It does not protect the SAMPLING FRAME.

**Added 2026-08-10, from the recipe sweep, which is §7a's own first application
failing in a new place.**

§7a said a second route must differ **in kind**. The recipe sweep did exactly
that: Route A read what the records *said* about each ladder's recipe; Route B
read what the generating dictionaries *showed had moved*. Structural against
textual — genuinely different in kind, and Route B's readings were correct.

**Route B was still wrong on its headline**, twice, and both times because of
something §7a does not cover:

| the error | the cause |
| --- | --- |
| *"nobody had written it down"* | the pre-flight queried `recipe_audit` on five ladders and never asked the two it then made claims about |
| *"exactly one ladder is known to be a ladder"* | the enumeration glob was `study-<body>*`; every purpose-built replacement family lives under another name |

**Neither is a reading error. Both are frame errors** — the method read its
sample correctly and the sample was not the population.

> **A route is defined by two things: how it reads, and what it reads.
> "Different in kind" governs the first. Nothing governs the second unless you
> make it.**

**The practical guards:**

1. **State the frame explicitly** — *"every directory matching `study-<body>*`"* —
   rather than implying *"every ladder."* A stated frame is falsifiable; an
   implied one is not.
2. **Ask what the frame structurally cannot contain.** A glob cannot contain
   things named otherwise. A query over five records cannot support a claim about
   a sixth.
3. **Never conclude ABSENCE from a search that did not look there.** *"No record
   says X"* requires having asked the records that would say it. This is L-42's
   sibling — an audit that cannot see the corpus reports absence rather than
   innocence — and it recurred here inside an audit written by someone who had
   cited L-42 that same day.
4. **The two routes should differ in frame as well as in kind.** Route A's frame
   was "all records mentioning a ladder"; Route B's was "case directories matching
   a glob." That they disagreed by a factor of three on the population is the
   signal, and it is only visible because the frames differed.
