# The next-cases slate

Date: 2026-08-05. Zero compute: nothing in this file was solved for it. It
reads the open case families in `docs/PRODUCT_LIST.md` §4C and §4D, the open
W1 docket items, `docs/DPW-CRM-SCOPING.md` and the hardness floor in
`docs/charters/CASE_SELECTION_CHARTER.md`, and it ranks them the way the lab
already ranks proposals, so that the next fleet wave can start the top of the
list cold.

## How this ranks

`docs/charters/GOALS_AND_PROPOSALS_CHARTER.md` §2 axis A is already
implemented and is not a proposal:

    rank_value = gain_points(source_kind) / max(est_core_min, 1.0)

with `challenge` 4.0, `measurement` and `gate` 3.0, `capability`, `ledger`,
`reading`, `inbox` 2.0, `report` 1.0. So this file does not invent a ranking;
it applies that one, and where a case's `est_core_min` on the docket is a
guess, it says so, because the axis is a ratio and the charter's own words are
that a denominator nobody checks is a denominator that drifts.

**Two things this exercise found before any ranking happened, and both change
what the top of the slate should be:**

1. **F5c's premise is already refuted in our own record.** The product list
   says "F5c backward-facing step reattachment vs Driver-Seegmiller. OOM +
   gradient blowups." The 2026-07-30 addendum in
   `campaign/F5bc_unsteady_statistics.md` traced that claim to no primary
   source anywhere in the repository — no OOM-kill, no solver abort, no
   commit — and attributed it to a probable conflation with B3 CBFS, a
   *curved* backward-facing step in the DAFoam adjoint pipeline that genuinely
   does hit the memory wall and genuinely does produce NaN gradients. A
   20,000-iteration control run held RSS flat at ~79 MB on a 30 GB box. **So
   there is no F5c OOM to diagnose.** F5c's real, documented failure is
   different and is still open: a steady RANS solve that converges numerically
   at every rung and lands on a reattachment length 4 to 12 times wrong, and
   wanders non-monotonically with iteration count and algorithm. The slate
   item below is written against that failure, not the OOM one.
2. **F8's "MRF first" has already been run, twice, and does not converge.**
   `F8_runs/phase6_mrf/` holds a 230,135-cell UAE Phase VI Sequence S case at
   7 m/s, taken to t=1500 and then restarted to t=3000. `SIMPLE solution
   converged` appears zero times in either log, and the blade-force history
   widened rather than settled: Fx span 508 N over t=1500–2250 and 729 N over
   t=2250–3000, Fy swinging −775 to +1276 N against an original −336 to +280 N.
   More steady iterations demonstrably do not fix it. So "MRF first" is not
   the next step for F8; it is the step already taken, and the cheap next
   move is to measure what the oscillation is centred on.

## The ranking

| # | case | source_kind | est core-min | rank value | reference in hand? |
| --- | --- | --- | --- | --- | --- |
| 1 | **F8 — gate the MRF forces that already exist against Hand et al.** | `measurement` | 6 | **0.500** | citation found, data not on disk |
| 2 | **B52 8th refinement rung** (`agp-1dec50b65c2f`) | `gate` | 20 | **0.150** | self-referential ladder; no external reference |
| 3 | F5c — reattachment-length diagnosis (not an OOM diagnosis) | `gate` | 25 | 0.120 | yes, digitised in the record |
| 4 | Ahmed 35° asymptotic ladder (`w1-ahmed-family-asymptotic-ladder`) | `gate` | 27 | 0.111 | yes, SAE 840300 |
| 5 | F6a hump at challenge conditions (`w1-hump-challenge-conditions`) | `challenge` | 60 | 0.067 | yes, shipped in the benchmark clone |
| 6 | F5b pitching NACA 0012 (`w1-f5b-pitching-naca0012`) | `gate` | 120 | 0.025 | **partly — see below, this is the problem with it** |
| 7 | F10 real 3D viscous RANS batch | `capability` | 120 (unpriced) | 0.017 | none named |
| 8 | DPW5 hex three-level ladder (`w1-dpw5-hex-three-level-ladder`) | `gate` | 400 | 0.0075 | yes, committee grids on disk |

The ordering is what the charter's arithmetic gives. Two comments on it, both
of which are about the denominator rather than the ranking:

- **F6a at challenge conditions is the only `challenge`-kind item on the board
  and it still ranks fifth**, because its 60 core-min is an `estimate` and the
  gain table's 4.0 cannot outrun a denominator six times item 2's. If that 60
  is wrong — and the hump's own gate rung cost **2.47 core-min** on a
  51,626-cell mesh at 800→1772 iterations — this item is mispriced by more
  than the factor of three the charter says triggers a `cost_basis`
  correction, and it belongs near the top. **That re-pricing is the single
  highest-value zero-compute action on this slate** and it is item 5's first
  task, not a separate proposal.
- **F5b's 120 core-min is not the reason to be careful with it.** See below.

## Per case

### 1. F8 NREL Phase VI — gate the forces we already have (6 core-min)

- **Reference data:** Hand, M.M., Simms, D.A., Fingersh, L.J., Jager, D.W.,
  Cotrell, J.R., Schreck, S., Larwood, S.M. (2001), *Unsteady Aerodynamics
  Experiment Phase VI: Wind Tunnel Test Configurations and Available Data
  Campaigns*, NREL/TP-500-29494. Publishes low-speed-shaft torque and blade
  root bending moment against wind speed for the Sequence S test, including
  the 7 m/s point the case on disk is already set at. **The citation was found
  on 2026-07-29; the tabulated data is not on disk.** Fetchable from the NREL
  publications server; the fetch is part of this item and is its only real
  risk.
- **Mesh source:** already built and checked —
  `F8_runs/phase6_mrf/`, 230,135 cells, `checkMesh` reports Mesh OK.
- **Predicted wall:** minutes. The forces are already written
  (`postProcessing/bladeForces`); the work is a time-average over a stated
  window of the existing history plus its spread, against the published
  torque. The 6 core-min prices one short confirmation restart, not a new
  solve.
- **Hardness criterion:** 5, rotating.
- **What makes it hard, honestly:** the quantity is a mean of a series that
  never settled, so the answer has to be reported as a band, not a point, and
  the item's own gate has to say in advance what band width would make the
  comparison meaningless. That is the whole discipline of this item and it is
  why it is worth 6 core-min rather than 0.
- **Why it ranks first:** it is the only item on the slate where a published
  external reference can be reached from fields that already exist on disk. If
  the mean of the oscillation lands on the published torque, the finding is
  that frozen-rotor MRF gets the mean right and cannot get the history right,
  which is a clean statement about a known MRF limitation. If it does not, F8
  has a real bias and the transient case has a target to beat. **Both outcomes
  pay, which is what the charter asks of a proposal.**

### 2. B52 8th refinement rung (20 core-min)

- **Reference data:** none external, and this is the case's honest limit. The
  ladder grades itself: Cd across seven rungs is 0.05512, 0.04477, 0.04905,
  0.04720, 0.04957, 0.05228, 0.04822 at 40,656 → 441,057 cells
  (`models/curriculum/uq-studies/b52.json`), `monotone: false`,
  `conclusive: false`, band taken as largest spread × 1.25 = 0.00507.
- **Mesh source:** the same recipe, `system/` copied verbatim, background
  blockMesh divisions scaled again from rung 7's 55×49×82. Roughly 880,000
  cells.
- **Predicted wall:** rung 7 ran at 2 MPI ranks with 220,529 cells per rank;
  doubling cells at the same rank count roughly doubles both the wall and the
  memory. The docket's 20 core-min prices the grid and explicitly **does not
  price the iteration count** — its own `cost_basis` says so — and iterations
  are the term that can overrun.
- **Hardness criterion:** `existing-family`.
- **Hardness criterion, honestly:** this is a refinement rung on a family
  already on the record, not a new family. It buys a numerical band, not
  physics.
- **The risk worth naming before it is started:** rung 7 was pre-registered
  with a prediction that Cd would rise, and the prediction scored FALSE. An
  8th rung predicting monotonicity is making the same bet a second time. The
  proposal filed for it below therefore pre-registers the *alternative* — that
  the ladder is not converging because the recipe changes the near-body cell
  distribution between rungs rather than refining it uniformly — and states
  what measurement would separate the two.

### 3. F5c BFS — the diagnosis that is actually open (25 core-min)

- **Not an OOM diagnosis.** See the top of this file. The plan below replaces
  the product-list line, which should be corrected when this is picked up.
- **Reference data:** Driver, D.M. & Seegmiller, H.L. (1985), *Features of a
  Reattaching Turbulent Shear Layer in Divergent Channel Flow*, AIAA J. 23(2),
  163–171 — reattachment at x/H = 6.26 ± 0.10 for the expansion-ratio-1.125
  step at Re_H = 37,500. Already used by the 2026-07-29/30 F5c work.
- **Mesh source:** `F5c_runs/`, six existing runs across three rungs.
- **Predicted wall:** the six runs already on record cost 26.9 core-min in
  total, so a focused diagnosis at the same resolutions is the same order.
- **Hardness criterion:** `existing-family`.
- **Hardness criterion for the diagnosis, stated as a question rather than a
  hope:** the recorded failure is a converged solve landing 4–12× wrong on
  reattachment. Three candidates separate cleanly and cheaply: (a) the inlet
  is placed too close to the step, so the incoming boundary layer at
  separation does not match Driver–Seegmiller's measured δ/H; (b) the
  expansion ratio or the step-height nondimensionalisation in our own
  post-processing is wrong, which would be a metric bug and not physics —
  **check this one first, it costs nothing and L-25 and L-28 are both this
  failure**; (c) genuine kOmegaSST bias, which on this case is documented at
  around −20%, nowhere near 4–12×. A discrepancy that large is almost never
  the turbulence model, and the diagnosis should be ordered accordingly.

### 4. Ahmed 35° asymptotic ladder (27 core-min, approved)

- **Reference data:** Ahmed, S.R., Ramm, G. & Faltin, G. (1984), SAE 840300.
  In hand and already used; the 35° configuration sits 12% from the
  experimental band.
- **Mesh source:** the R4 recipe, four rungs, uniform refinement, 4 ranks.
- **Predicted wall:** **this is the best-priced item on the slate.** Its
  `cost_basis` is `measured, not estimated`: R4 ran the identical four-rung
  experiment on the identical body at the identical rank count for about 27
  core-min (meshing 1.21 + ~2.6, then 0.84, 2.00, 3.39 and 16.74), and the
  original 240 core-min figure was priced on mesh generation for a different
  body.
- **Hardness criterion:** 1, three-dimensional separated flow with a
  documented bistable wake.
- **The gate to beat:** an observed order inside the theoretical window on a
  uniformly refined family. The 25° half of this item is already answered in
  the negative by R4 — non-monotone, increments −5.442e-03, −5.367e-03, then
  +8.895e-04, the first two equal to 1.4%, the signature of p near zero — so
  the 35° slant is the whole of what is left, and the honest prior is that it
  fails the same way. **Predicting a pass here would be ignoring our own
  strongest evidence.**

### 5. F6a hump at challenge conditions (60 core-min as filed, approved)

- **Reference data:** shipped in the benchmark clone
  (`closure-challenge-benchmark/data/NASA_2DWMH/`), plus NASA TMR's own
  experiment and SST solution, both already fetched and used by the
  2026-07-28 F6a gate.
- **Mesh source:** the benchmark's own 51,626-cell mesh.
- **Predicted wall:** **re-price this before launching it.** F6a's own three
  rungs cost 0.28 + 2.51 + 2.47 = 5.26 core-min on that mesh. Unless the
  challenge conditions change the mesh, 60 core-min is an order of magnitude
  high, and correcting it moves this item from fifth to first on the charter's
  own arithmetic. The re-pricing is zero compute and is the first task of the
  item.
- **Hardness criterion:** 6, challenge-aligned — this is the only slate item
  that touches a scored column (`NASA_2DWMH`, 18.2% of our measured deficit,
  and the one case where the round-4 entry is last on the board).
- **Hardness criterion, and the trap:** F6a already passed at its own
  conditions. Re-running the same mesh at slightly different conditions is not
  automatically a result. What makes this item worth its cost is the
  connection to the scored column, so its gate must be stated in terms of the
  benchmark's own scorer and not only in terms of separation and
  reattachment.

### 6. F5b pitching NACA 0012 (120 core-min, approved)

- **Reference data — this is the problem, and it is not a cost problem.** The
  case is McAlister, Carr & McCroskey, NASA TP-1100 (1978), case (e):
  α(t) = 15° + 10° sin(ωt), reduced frequency k = 0.15, Re = 2.5×10⁶, pitch
  about the quarter chord. The primary source has been downloaded and parsed.
  **TP-1100 does not publish a machine-readable CL(α) time series for case
  (e).** Its dynamic-stall data are scanned strip charts, and its
  SUMMARY/CONCLUSIONS give only test-matrix-wide extremes (C_L up to 3.5,
  C_M to −0.75), not case-(e) numbers.
- So the gate as the docket words it — "lift hysteresis loop against McAlister
  NASA TP-1100 at a stated tolerance" — **cannot be met with the data in
  hand**, and the 2026-07-29 work already recorded that and fell back to a
  qualitative comparison. Per the case-selection charter's step 4, check the
  detector before the physics: a quantitative gate whose reference does not
  exist in numeric form fails before a core-second is spent.
- **What to do instead, in order of cost:** (a) look for a digitised TP-1100
  case-(e) loop in the later literature that re-plots it — several
  dynamic-stall validation papers do — and cite that at its own provenance
  tier; (b) if none is found, re-target to a dynamic-stall case that *does*
  publish tabulated phase-resolved loads; (c) only then run. **Running first
  and discovering the reference is unusable is how a 120 core-min item becomes
  a 120 core-min qualitative picture.**
- **Mesh source:** built and proven — the F2 transonic C-grid, whole-mesh
  rigid rotation via `solidBodyMotionFunction oscillatingRotatingMotion`, with
  two real bugs already found and fixed (`pcorr` solver block; impulsive-start
  divergence, fixed by a `potentialFoam -writephi` initialisation).
- **Predicted wall:** the one measurement that exists says this is the
  expensive family: F5b's coarse mesh is *smaller* than F5c's, and one period
  runs 15–25× longer in wall time, driven entirely by Courant-limited time
  steps. 120 core-min is plausible for one period at one resolution and buys
  no mesh ladder.
- **Hardness criterion:** 3, unsteady statistics.

### 7. F10 real 3D viscous RANS batch (unpriced)

- **Reference data:** none named anywhere. This is the item's blocker.
- **Naming collision, flagged rather than resolved:** the campaign status's
  F10 ("replace the panel-method stand-in") and the mega-batch's internally
  labelled "Family F10" (`AHMED_VISCOUS_3D` in `sdk/workflows/mega_batch.py`,
  which *is* shipped) are two different scopes under one label, and the
  2026-07-29 status file flagged the collision without reconciling it.
- **What it needs before it can be ranked at all:** a scope, a named
  reference per the case-selection charter's step 2, and a price. It is on
  this slate to say that it is not startable, not to start it.

### 8. DPW5 hex three-level ladder (400 core-min)

- **Reference data:** the AIAA DPW committee grids are on disk with recorded
  hashes, and `DPW-CRM-SCOPING.md` carries the participant scatter that any
  result would be graded against: DPW-VI wing-body median 257 counts, IQR
  ±4–5 counts, honest success band 250–264 counts.
- **Mesh source:** committee grids, not ours — which is the whole point, and
  `COMMITTEE_GRID_NUMERICS.md` already measured their quality: the DPW5 L1.T
  hex grid is 638,976 cells with 0.59% of faces above 70° non-orthogonality,
  against 6.70% for the same nodes as prisms and 29.12% as hybrid. The hex
  topology is the one to climb.
- **Predicted wall:** the docket's 400 core-min is an `estimate`, and the
  scoping report's own arithmetic for real DPW levels is in core-*hours*
  (L0 7.2M cells at 18–24 core-hours). Those are not the same grids: the
  committee L1.T hex on disk is 0.64M cells, so the docket figure is pricing
  the levels above the one already solved, not the workshop's L0–L2. **Anyone
  picking this up must reconcile those two numbers first**, because a
  400 core-min item that is really a 20 core-hour item would consume a week
  of the box.
- **Hardness criterion:** 2, shocks (transonic wing-body), plus 1.
- **Why it ranks last and should still be started eventually:** it is the only
  route to a grid-convergence ladder on grids the lab did not generate, which
  is the one confound our ladders never escape. It ranks last today because
  400 core-min against 3.0 gain points is what the charter's arithmetic says,
  and the ranking is not the decision.

## What was filed

The top two are filed as ready-to-run proposals with `launch_prompt` fields so
the next wave can start them without re-deriving anything:

- `demo-output/website/agenda/proposals/f8-mrf-forces-against-hand-2001.json`
- `demo-output/website/agenda/proposals/b52-eighth-rung-with-the-alternative-preregistered.json`

Items 4 and 5 are already approved on the docket and need no new filing; item 5
needs its price corrected before launch and item 6 needs its reference resolved
before launch, and both of those are stated above rather than filed as separate
proposals, because neither is a case and the charter's `no-case` value exists
for exactly that distinction.

## Corrections (2026-08-07, Cases family supervisor — original text above left in place)

1. **Item 1's reference citation was a conflation**, discovered when the item
   was executed (`F8_MRF_HAND2001_GATE.md` §2): NREL/TP-500-29494 is *Simms et
   al.* (blind-comparison report, torque as figures only); the Hand et al.
   author list this slate quotes belongs to TP-500-29955, which publishes no
   mean-torque table. The 800 N·m at 7 m/s the gate ultimately used is
   secondary tier (Processes 12(9):1994 Table 6). Item 1 itself is complete:
   verdict NO VERDICT as pre-registered, steady-MRF branch closed three ways
   (F8 gate §16).
2. **Item 3 quotes "Re_H = 37,500"** — the rounding the F5c record's own
   exact-parameters block explicitly rejected: Driver–Seegmiller's step-height
   Reynolds number is ≈36,000 (`F5bc_unsteady_statistics.md`, "Exact published
   parameters"). The reattachment reference 6.26 ± 0.10 is unaffected.
3. **Item 2 is complete** (B52 rung 8 run 2026-08-07, `B52_RUNG8_RESULTS.md`):
   Cd inside the span as predicted, surface-resolution alternative refuted at
   b = 0.707, ladder still `conclusive: false` — now held by `order_window`
   (fitted p = 28.7, a noise signature) instead of `monotone`.
