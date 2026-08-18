# N_a10 third member (SA) — adjusted settle criterion, pre-registered

Written 2026-08-08, **before the solve is launched**, by the Cases family
supervisor, executing entry 11 of
`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` (commit `81741be3`, wording
binding) under the chief's standing green light. Docket item:
`n-a10-third-member-under-an-adjusted-settle-criterion` (approved,
10 core-min). Machine spec of this criterion, read by the runner:
`MODEL_FORM_runs/adjusted_settle_n_a10.json`.

## The situation being adjudicated

The first family-N band (post-R12 regrade, `43ac7287`) at a10 has two members
(kOmegaSST 1.1164337, kEpsilon 1.0801964). It contains CFL3D's Cd (0.0123621
inside [0.0044952, 0.0142268]) and **misses CFL3D's Cl by 0.22%**: 1.0778081
against a band floor of 1.0801964 (gap 2.388e-3). Entry 11: at n=2 a min/max
band is a lower bound on the true spread; the miss more likely indicts the
membership than the model family. The arm: converge SA (excluded on
residualControl non-attainment, not divergence) and re-state containment at
n=3.

## Why the criterion is adjusted, from committed evidence only

Everything in this section is read from the **committed** 2026-08-07T22:33Z
SA record and its archived log (`MODEL_FORM_runs/N_a10_SpalartAllmaras/`,
commit `43ac7287`) — nothing from the run this file pre-registers.

- The standard gate's criterion 2 is the solver's own `SIMPLE solution
  converged` sentence against `p 1e-06`, `U 1e-08`, `nuTilda 1e-08`.
- Measured at the 12,000-iteration backstop: Ux initial residual ~5e-9
  (attained), **p flat at 2.5–2.9e-6 from iteration 2,000 to 12,000**
  (3.0e-6 → 2.56e-6 over ten thousand iterations), **nuTilda floored at
  ~1.6e-8** from iteration 6,000 on. The sentence is unreachable on this
  (case, model) pair — the same unreachable-tolerance class F6b closed by
  setting reachable criteria (`residualControl p 1e-15` precedent) — while
  the two admitted members' p did reach 1e-6, i.e. the floor is
  model-specific, not a case defect.
- Meanwhile Cl's trailing-2000 peak-to-peak is **8.6e-6** with a
  halves-drift of 1.7e-7 — 278× below the 2.388e-3 gap the containment
  decision turns on. The flow is settled; only the unreachable targets hold
  the member out.

## The adjusted criterion (frozen here, before the run)

**Numerics, schemes, relaxation and residualControl targets are byte-for-byte
the batch's own — nothing about the solve changes.** This preserves design
deviation 4 of `MODEL_FORM_BATCH_DESIGN.md` ("residual targets held fixed
across models") in substance: only the *declaration of settledness* is
replaced, because the run will again stop on the backstop, not the sentence.
The cell is ADMITTED to the band iff all of:

1. **Solver exit 0, no S1/S2 fatal** (gate criterion 1, unchanged).
2. **Residual-floor plateau** in place of the unreachable sentence: for each
   of p, Ux, nuTilda, the median initial residual over the final quarter of
   the history is (a) **within one decade of the standard target**
   (caps: p ≤ 1e-05, Ux ≤ 1e-07, nuTilda ≤ 1e-07) and (b) **fallen by less
   than a factor 2** from the previous quarter's median — i.e. the solver is
   demonstrably at its floor and that floor is one decade or less above the
   standard. Derivation of the caps: 10× the standard targets, chosen from
   the targets, not from SA's floors (which sit 4–20× *below* these caps on
   the committed run); a member whose floor exceeded a cap would be refused.
3. **S12 settle** on the Cl and Cd histories (gate criterion 3, unchanged).
4. **Decision-scaled stationarity** — the load-bearing clause, underivable
   from anything SA does: trailing-2000-iteration peak-to-peak
   **Cl ≤ 2.4e-4 and Cd ≤ 2.0e-4**, each 10% of the decision distance the
   containment question turns on (Cl gap to the band floor 2.388e-3; Cd
   distance from SA's archived value to its nearest band edge 1.97e-3). A
   member admitted to decide a containment question must carry iterative
   scatter an order of magnitude below that question's scale.
5. **Mesh:** non-orthogonality 85.70° vs the 70° hard gate, EXEMPT under R12
   (`docs/charters/SUPERVISOR_RULINGS.md`) for **banding purposes only**; the
   runner's R12 statement is carried on the record and this exemption never
   travels to physics gates or credentials.

Clauses 2 and 4 are evaluated **mechanically by the runner**
(`--adjusted-settle`, reading the committed spec JSON) and the full measured
numbers are stamped into the cell's `record.json` (`settle_criterion` block),
so admission is machine-auditable, not narrative. Any clause failing → the
cell stays EXCLUDED with the failing clause named.

## Outcomes, declared now

- **Admitted and CFL3D's Cl enters the n=3 band** → containment restated at
  n=3; the standing rule proposal filed is **"no containment verdict below
  n=3"** (a two-member aero band may report its interval but not a
  containment verdict).
- **Admitted and Cl still outside** → the miss is real on a three-member
  band; the rule proposal filed is a **membership-minimum rule for
  aero-family bands** (and the miss stands in the band artifact).
- **Not admitted (any clause fails)** → SA stays excluded, the n=2 miss
  stands, and the membership-minimum branch fires; the failed clause is the
  finding.

## Predictions (put at risk, scored after)

- **P1 (reproducibility):** the fresh solve lands within 1e-3 of the
  archived Cl 1.0290490 and within 1e-4 of Cd 0.0161921.
- **P2 (criterion):** all clauses pass, with clause-4 margins of order 20×
  (archived tail p2p 8.6e-6 vs the 2.4e-4 cap).
- **P3 (the verdict):** at n=3 the Cl band becomes ≈[1.0290, 1.1164] and
  CFL3D's 1.0778081 is **CONTAINED**; Cd's band ≈[0.0045, 0.0162] still
  contains 0.0123621 → the "no containment verdict below n=3" branch fires.
- **Named risk:** the fresh solve wanders (the C-grid wake-oscillation
  hazard) or lands elsewhere — then clause 3 or 4 vetoes, the exclusion
  stands as a measured irreproducibility finding, and the
  membership-minimum branch fires instead. Reported as it falls.

## Budget and mechanics

Cap 10 core-min (docket); predicted ~1.2 (measured 1.08 and 1.12 on the two
archived runs of this identical cell). Launch: the batch runner,
`--family N --regime a10 --model SpalartAllmaras --redo-excluded` (the
22:33Z record is superseded, never deleted, per convention),
`--adjusted-settle MODEL_FORM_runs/adjusted_settle_n_a10.json`, single core,
setsid-detached with inline polling (no agent-owned watcher); the runner's
queue gate yields to any three live solver containers (S1 reinversion and
others may hold the box). Band regeneration is the runner's own end-of-run
`write_band()`; containment is restated from that artifact only.

*Nothing below this line existed when the run was launched.*

## Outcome (2026-08-08, written after the run)

**Ordering, for the record:** this pre-registration and the criterion spec
were committed at 02:01:52Z (`9374f807`); the runner launched at 02:02:02Z
(runner.log). Ten seconds of daylight, in the right order.

**The run:** 12,000 iterations, 62.5 s, **1.07 core-min against the 10
approved**. The solve reproduced the archived 22:33Z run **to every printed
digit**: Cl 1.0290489902, Cd 0.016192147753 — bit-identical, a measured
solver-determinism datum on this grid. The criterion, evaluated mechanically
by the runner and stamped into the record:

| clause | measured | cap | verdict |
| --- | --- | --- | --- |
| p floored | final-quarter median 2.55e-6, prev 2.57e-6 | ≤ 1e-05, factor 2 | MET |
| Ux floored | 5.51e-9 vs 5.50e-9 | ≤ 1e-07, factor 2 | MET |
| nuTilda floored | 1.86e-8 vs 1.90e-8 | ≤ 1e-07, factor 2 | MET |
| Cl tail-2000 p2p | 8.63e-6 | ≤ 2.4e-4 | MET (28× margin) |
| Cd tail-2000 p2p | 3.68e-6 | ≤ 2.0e-4 | MET (54× margin) |
| S12, exit 0, no fatal | pass | — | MET |

**A wrapper defect, said loudly rather than smoothed over:** the runner's
02:03:07Z record stamped `admitted_in_place_of_residual_control: true` and
then **excluded the cell anyway** — the C1 fix's conservative clause ("a
workflow-flagged cell stays EXCLUDED regardless of how it grades") let the
TMR workflow's absolute tail-50 rule (Cd p2p 2.67e-6 > 1e-7) outrank the
registered criterion, which is precisely the C1 failure class inverted. The
pre-registered wording above is the criterion of record and it says ADMIT
on every clause. Disposition: the defect fixed in the runner (the workflow's
settle rule is now recorded but superseded when a pre-registered criterion
admitted the cell; any *other* workflow error still force-excludes); the
02:03:07Z record superseded per convention (never deleted) and the corrected
record carries a `correction` block naming all of this. **The criterion as
written decided, not the outcome** — the deciding text predates the run by
commit hash.

**Containment at n=3, from the regenerated band artifact:**

| QoI | n=3 band | CFL3D SST (897×257) | verdict |
| --- | --- | --- | --- |
| Cl | [1.0290490, 1.1164337] | 1.0778081 | **CONTAINED** (was NOT contained at n=2) |
| Cd | [0.0044952, 0.0161921] | 0.0123621 | **CONTAINED** (as at n=2) |

The 0.22% n=2 miss was **under-membership, exactly as entry 11 read it**: the
third member entered 0.0512 *below* the old band floor — the n=2 band was a
lower bound on the true spread by a factor of 2.4 on Cl.

**Predictions, scored:** P1 HELD (bit-identical, against a 1e-3 window);
P2 HELD (every clause, margins 28× and 54× vs the predicted ~20×); P3 HELD
(Cl contained at n=3). The named risk (wander/irreproducibility) did not
fire. **The declared branch fires: the rule proposal filed is
`no-containment-verdict-below-n3`** — a two-member band may report its
interval but not a containment verdict. R12 statement carried on the group,
banding scope only, unchanged.
