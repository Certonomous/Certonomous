# F6b — in-house periodic hill vs ERCOFTAC: pre-registration

Written 2026-08-05, **before any solve of an in-house periodic-hill mesh was
started**. Family F6, sub-family b, product-list item 4C "F6b periodic hills vs
ERCOFTAC". Companion result file: `F6b_ERCOFTAC_RESULTS.md` (written after).

## Why this is not a repeat of the 2026-07-29 F6b gate

The 2026-07-29 gate (`dafoam/f6b_periodic_hills/F6b_periodic_hills.md`,
GATE REACHED, 34.1 core-min) solved **the benchmark's own shipped
`PH_Breuer` case on the benchmark's own shipped 15,600-cell mesh**. It
established that stock `kOmegaSST` over-predicts the recirculation length by
~64%, and it verified that against the shipped RANS field to five significant
figures. What it could not separate is the mesh: every number in it inherits a
grid the lab did not build and never refined.

This run is the other half. **The mesh is ours**, generated from the published
ERCOFTAC hill polynomial by `F6b_runs/make_ph_mesh.py`, on a three-rung
refinement ladder, and the solve is ours. The closure challenge ships its own
periodic-hill RANS fields; a validated *in-house* PH primal is what the
case-family ladder (4C) and any future closure work actually need, because a
correction fitted on somebody else's grid cannot be transferred to ours without
this measurement.

## Geometry provenance, verified before the pre-registration was closed

The lower wall is the ERCOFTAC UFR 3-30 piecewise-cubic hill profile (six
cubic segments, hill height h = 28 mm, one flank spanning 0 ≤ x ≤ 54 mm),
coded from the published coefficients in `make_ph_mesh.py` and nondimensionalised
by h. Domain `Lx = 9h`, `Ly = 3.035h`, streamwise-cyclic, 2-D.

**Independent check, already run (zero compute):** our polynomial evaluated at
the 121 lower-wall points of the benchmark's shipped `PH_Breuer` mesh agrees
with the shipped wall to a **maximum error of 1.30e-7 h** (mean 1.56e-8 h).
Two independently produced descriptions of the same wall, agreeing to seven
decimals. Recorded here so that any later geometry disagreement is a solver or
mesher finding rather than an unresolved question about which hill was meshed.

## Case setup

Physics and numerics are the benchmark case's own, so that the mesh is the only
variable against the 2026-07-29 record: incompressible steady `simpleFoam`,
stock `kOmegaSST`, `nu = 9.438414346389807e-05`, `meanVelocityForce` holding
`Ubar = 0.72` (giving `Re_H = Ubar·h/nu = 10595`), `bounded Gauss linearUpwind`
convection, `k` fixed at 1e-15 on both walls with `omegaWallFunction` and
`nutLowReWallFunction` (the shipped low-Re wall treatment).

Three deviations from the shipped dictionaries, each stated with its cause:

1. `residualControl { p 1e-15; }` is replaced by `1e-6` on `U`, `p`, `k`,
   `omega`. 1e-15 is unreachable for a GAMG pressure solve on this mesh, which
   is exactly why the 2026-07-29 run could never print `SIMPLE solution
   converged` and tripped a documented gate-checker false negative. Setting a
   reachable tolerance is the fix that record asked for.
2. `libs ("libfrozenIncompressibleTurbulenceModels.so")` dropped — not
   distributed in the public benchmark clone and not needed by a stock
   `kOmegaSST` forward solve (same finding as F6a/F6c/F6b-2026-07-29).
3. Station samplers rewritten as inline `sets` function objects with
   `type midPoint` (the shipped `lineCell` is not a valid sample type in
   OpenFOAM v2606), and `wallShearStress` written on the bottom wall.

## The refinement ladder

| rung | nx × ny | cells | target first cell at the flat wall |
| --- | --- | --- | --- |
| coarse | 84 × 92 | 7,728 | 0.01104 h |
| medium | 120 × 130 | 15,600 | 0.00781 h |
| fine | 170 × 184 | 31,280 | 0.00552 h |

The medium rung is deliberately at the shipped mesh's own cell count and
near-wall spacing (the shipped mesh is 120 × 130 with a first cell of
0.00782 h at the flat section), so that "our mesh vs their mesh at the same
resolution" is a controlled comparison. Refinement ratio between rungs is
√2 in each direction.

**Measured near-wall resolution of the shipped mesh, for the record:** taking
the shipped converged `wallShearStress`, the lower wall's peak friction
velocity gives **max y⁺ ≈ 4.4** at the first cell centre (mean 1.30); the top
wall reaches y⁺ ≈ 1.37. A `nutLowReWallFunction` / `k = 1e-15` wall treatment
presumes the first cell sits in the viscous sublayer. The medium rung inherits
that y⁺; the fine rung roughly halves it, which is the point of running the
ladder.

## Reference data and the tolerance, with citations

`Re_H = 10595` is the canonical periodic-hill station. The accepted references
do not agree with each other, and the pre-registered tolerance is taken from
their disagreement rather than invented:

| source | separation x/h | reattachment x/h |
| --- | --- | --- |
| Fröhlich, Mellen, Rodi, Temmerman & Leschziner (2005), *JFM* **526**, 19–66 — highly resolved LES, hosted by NASA TMR (`tmbwg.github.io/turbmodels/Other_LES_Data/2dhill_periodic.html`, "Separation is near x=0.2h and reattachment is near 4.6-4.7h") | ~0.20 | 4.6–4.7 |
| Breuer, Peller, Rapp & Manhart (2009), *Computers & Fluids* **38**, 433–457 — LES/DNS Reynolds-number series, values as tabulated on ERCOFTAC KBwiki UFR 3-30 Evaluation ("x_S/h ≈ 0.18 at Re = 5600 but then settles down at a slightly larger value of x_S/h ≈ 0.19 at Re = 10,595"; "reattachment lengths are x_R/h = 5.24, 5.19, 5.41, 5.09, and 4.69 for Re = 700 to 10,595") | 0.19 | 4.69 |
| Rapp & Manhart (2011), "Flow over periodic hills: an experimental study", *Experiments in Fluids* **51**, 247–269 — PIV/LDA water channel; reattachment at x/h ≈ 4.21 at Re = 10595, separation not reliably measurable ("In the experiment it was not possible to determine the separation point reliably", ERCOFTAC UFR 3-30 Evaluation) | not measurable | 4.21 |

**Reference band adopted: reattachment x_R/h ∈ [4.21, 4.70], separation
x_S/h ∈ [0.19, 0.20].** The reattachment band is 0.49 h wide, i.e. **±5.5%
about its midpoint 4.455** — that spread is the literature's own
experiment-versus-LES scatter and is the smallest deviation this case can
resolve against. Separation is quoted by both LES sources and by neither
experiment, so its band is LES-only and is narrow by construction.

## Gates, pre-registered

**Gate V — verification of our pipeline (this is the pass/fail gate on us).**
Our medium rung, on our own mesh, must reproduce the shipped mesh's converged
`kOmegaSST` answer for the same physics:

- reattachment within **±5%** of the shipped-mesh value **x_R/h = 7.6439**
  (i.e. 7.262–8.026), and separation within **±0.05 h** of the shipped-mesh
  value **x_S/h = 0.2590**. The 5% figure is deliberately tighter than the
  ±5.5% literature scatter above: a mesh-to-mesh difference smaller than the
  reference's own scatter cannot be argued about against the reference, so that
  scatter is the loosest defensible tolerance and we take half of it.
- **grid sensitivity:** |x_R(fine) − x_R(medium)| / x_R(medium) < 5%. If the
  ladder has not settled to within the reference scatter, no reattachment
  number from this case is a validated number, whatever it agrees with.

**Gate P — physics vs ERCOFTAC (the closure-relevant measurement).**
Reattachment x_R/h against the band [4.21, 4.70] and separation x_S/h against
[0.19, 0.20], reported as measured on every rung.

**Gate Q — mean-velocity profiles.** Scaled MAE of |U| at the nine standard
stations x/h = 0…8 against the Breuer LES field the benchmark ships on the
`PH_Breuer` mesh (`0/U_LES`), interpolated onto our own station points. The
2026-07-29 run measured 12.51% (serial pipeline) / 12.95% (4-rank) on the
shipped mesh.

## Predictions, written before the runs

1. **Gate P will FAIL, on reattachment, by over-prediction.** Predicted
   x_R/h ∈ **[7.0, 8.3]**, i.e. **+50% to +95%** over the reference band's
   midpoint. Basis: the 2026-07-29 in-house measurement on the shipped mesh
   (7.6439) and the same one-sided SST bias measured on F6a's NASA hump
   (+13.9% on reattachment). The direction is now a citation, not a
   recollection — the 2026-07-29 prediction file guessed the *opposite* sign
   and was falsified, and this one is calibrated on that failure.
2. **Gate P will PASS on separation.** Predicted x_S/h ∈ [0.20, 0.30]; the
   shipped-mesh value was 0.2590, just outside the LES band on the high side.
   Note the honest asymmetry: separation off a curved crest is set by the
   pressure gradient, which SST gets nearly right, while reattachment is set by
   shear-layer mixing, which it does not.
3. **Gate V will PASS**, and this is the risky prediction. Predicted medium-rung
   x_R/h ∈ [7.26, 8.03]. If our own mesh at the same nominal resolution lands
   outside that window, the finding is about our mesher or the arc-length cell
   distribution along the hill flank, and it would mean the shipped-mesh number
   the lab has been quoting since 2026-07-29 is grid-specific.
4. **Grid sensitivity will be the marginal one.** Predicted
   |Δx_R| medium→fine of **3–12%**. A separation bubble this long, on a
   marginal-y⁺ low-Re wall treatment, is the kind of quantity that has not
   settled at 15,600 cells; the prediction that it has is the weakest claim in
   this file, and if it fails, the honest verdict is that the reattachment
   number is not yet mesh-converged and Gate V's second clause fails.
5. **Gate Q**: scaled MAE in **[10%, 16%]** on the medium rung.

## Budget and disqualifiers

80 core-min ceiling, 2 cores per solve, three solves. Hard iteration cap 6,000
per rung with `residualControl` at 1e-6; a rung that hits the cap without
meeting `residualControl` is reported as not converged and its numbers are
labelled as such rather than quietly used.

**What would disqualify the whole family from carrying a wall credential**
(per the case-selection charter's step 3): if the fine rung's reattachment
differs from the medium rung's by more than the reference band's own ±5.5%
scatter, then the case as meshed cannot resolve the quantity it exists to
report, and neither a pass nor a fail against ERCOFTAC means anything until it
is re-run on a converged ladder.

**HARD criterion:** `existing-family` (F6b is on the record since 2026-07-29);
the underlying regime meets criterion 1's spirit — separation whose
reattachment location is the entire reported quantity — and criterion 6, since
the periodic hill is the closure challenge's own training-case class.
