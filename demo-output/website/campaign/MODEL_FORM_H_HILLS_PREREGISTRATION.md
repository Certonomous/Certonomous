# Model-form family H — periodic hills at the medium rung: pre-registration

Written 2026-08-08 by the Cases family supervisor, **before any family-H cell
has run**. Executes the negative-verdict review's entry 1 diagnostic
(approved `223c3b84`, ~35 core-min): do any of the four closures enter the
Rapp/Breuer/Fröhlich reattachment band, and does the inter-model band
contain it? Runner: `sdk/scripts/model_form_batch.py`, family `H`, extended
in the same commit as this file. The QCR constitutive route is already ruled
out on this case by the activity-checked null (+0.034 x/h,
`QCR_ACTIVITY_CHECK_2026-08-08.md`), which is what makes the model-family
question the live one.

## The case, and why R12 is NOT invoked

Each cell is a byte-copy of the **verified** F6b medium case
(`F6b_runs/medium`: the lab's own ERCOFTAC-polynomial mesh, 15,600 cells,
Gate V PASS at 0.043% against the shipped grid, grid sensitivity 0.097%),
with exactly the model-dependent pieces changed. **The mesh is compliant and
no exemption is needed or claimed: max non-orthogonality 39.66, max skewness
0.226, max aspect ratio 15.29 against hard gates of 70 and 4** (F6b results
§1). Nobody reaches for R12 here; the mesh verdict is read from the source
case's own `log.checkMesh`, copied beside each cell with the mesh it
describes (`polyMesh` copied bit-identical, md5-checkable).

## The four members and their model-dependent pieces (frozen here)

Physics identical to F6b: `simpleFoam`, `nu = 9.438414346389807e-05`,
`meanVelocityForce` `Ubar 0.72` (Re_H = 10,576 on the measured crest bulk —
the §1b-corrected statement), same schemes, same relaxation, same solvers.

| member | turbulence fields | wall treatment | derivation |
| --- | --- | --- | --- |
| kOmegaSST | case's own | case's own (k 1e-15, omegaWallFunction, nutLowReWallFunction) | unchanged — the control member |
| kEpsilon | + `0/epsilon` | epsilonWallFunction with lowReCorrection (batch convention, wall-resolved y+≈1.3) | eps_init = Cmu·k·omega = 0.09 × 0.00375 × 0.1102270 = 3.7202e-5 — the same eddy-viscosity-matching derivation as the batch's deviation 2 |
| realizableKE | + `0/epsilon` | same | same |
| SpalartAllmaras | + `0/nuTilda` | fixedValue 0 at walls (exact SA wall value) | nuTilda_init = 3·nu = 2.8315e-4, the batch's TMR SA convention (deviation 1) applied to the internal init |

Dictionary extensions per extra field: solver block cloned from omega
(PBiCG/DILU 1e-09), relaxation 0.7 (same as k/omega), `residualControl`
entry at 1e-6 (same as the case's own four), `div(phi,<field>)` cloned from
`div(phi,omega)` (`bounded Gauss linearUpwind grad(U)`). Nothing else moves
between members — the band's comparability rests on that.

## The gate, pre-registered (deviations from the batch's §4 gate declared)

A member is ADMITTED to the band iff all of:

1. **Exit 0, no S1/S2 fatal** (unchanged).
2. **The case's own residualControl (1e-6 on p, U, and every solved
   turbulence field) met** — the `SIMPLE solution converged` sentence in the
   log — within the **pre-stated iteration cap of 12,000**. The cap is sized
   from this family's own two measured attainments, both in front of us as
   ordered: stock SST converged at 5,997 of a 6,000 cap (3 iterations of
   daylight) and QCR needed 6,177; 12,000 is ~2× both. A cap-stop without
   the sentence is an exclusion, recorded as such. No adjusted criterion is
   pre-wired for this family: a plateaued member stays excluded in THIS
   record, and any adjusted-criterion rescue would need its own
   pre-registration (the N_a10 precedent), not a rider.
3. **Steady-bubble discipline** (replaces the batch's S12-on-coefficient
   clause — this case writes no force coefficients; declared deviation):
   exactly **2** skin-friction sign changes on the bottom wall at the final
   written time, with the first crossing in the separation direction
   (attached→reversed) — the F6b exactly-two rule plus the G3
   sign-direction check from the family findings. Any other count: the
   member has no reattachment point, is excluded from the x_R band, and its
   crossing count is recorded (the veryfine-rung lesson: the first two of
   twenty-two wiggles are not a separation and a reattachment).
4. Mesh: compliant per above; verdict from the copied `log.checkMesh`.

QoI: **x_R/h** (the band quantity), **x_S/h** recorded alongside and banded
for information; the entry-1 questions are decided on x_R only.

## Reference, band and containment tests (pre-declared)

Literature band, from the F6b pre-registration's own table (unchanged):
**x_R/h ∈ [4.21, 4.70]** — Rapp & Manhart 2011 (exp) 4.21; Breuer et al.
2009 (LES) 4.69; Fröhlich et al. 2005 (LES) 4.6–4.7; midpoint **4.455**.

- **Per-member entry test:** member x_R ∈ [4.21, 4.70].
- **Band containment test (primary):** the inter-model interval
  [min x_R, max x_R] over admitted members contains the band midpoint
  4.455 — the batch's point-containment convention, applied to the
  literature's own center. Per-source containment (4.21 / 4.65 / 4.69) is
  reported alongside as the secondary read.
- **Membership minimum:** if fewer than **3** members are admitted, the
  record states the member results and **refuses a containment verdict** —
  the first application of the filed `no-containment-verdict-below-n3`
  rule, applied here by pre-registration (the rule's own adoption gate, the
  archive replay, is untouched by this).

## Predictions, put at risk

- **P1:** kOmegaSST converges and reproduces the archived 7.6472 within 1%
  (same case, fresh solve).
- **P2:** at least one non-SST member fails the gate; realizableKE is the
  named likeliest (1 of 6 converged cells across families P and N).
- **P3 (the risky one, and the one that decides the showcase):** every
  admitted member lands ABOVE the literature band (x_R > 4.70) — the
  SST separated-flow overprediction extends to the linear eddy-viscosity
  family on this case, so **if n ≥ 3 the band does NOT contain 4.455** and
  the hills join the hump as a model-family failure with the constitutive
  route already excluded. Declared alternative, honestly live: kEpsilon's
  higher eddy viscosity in separated shear layers shortens its bubble into
  or below the band, stretching the band floor down and possibly containing
  the midpoint — if that happens, the epistemic-uncertainty showcase gains
  a working inter-model bar instead, and P3 is scored FALSE as written.
- **Named risk:** kEpsilon (or SA) produces no steady bubble at all
  (0 or >2 crossings) — then clause 3 excludes it with the count recorded,
  and n may fall below 3, triggering the membership refusal.

## Budget and mechanics

Approved ~35 core-min; runner `--max-core-min 35` (it stops before any cell
that would exceed; worst case one in-flight cell overshoots, stated).
Measured basis: 6.79 core-min per 6,000 iterations serial on this rung —
expected ~7/cell, worst ~13.6 at the cap. One core, one cell at a time,
queue gate live (S1 weighted arm and A3 sub-LU arm share the box; 16 cores,
~2 busy at pre-registration time). Launch setsid-detached, self-ledgering
per cell (`record.json` at cell finish), polled inline; band regenerated by
the runner's own end-of-run `write_band()`.

*Nothing below this line existed when the first family-H cell was launched.*
