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

## Outcome (2026-08-08, written after the batch stopped at 02:57:17Z)

Pre-registration committed `28e14422` at 02:27Z; launch 02:28:03Z. Total
**29.18 of 35 core-min**. Per-member, against the gate as frozen:

| member | verdict | detail |
| --- | --- | --- |
| kOmegaSST | **ADMITTED** | converged (sentence, 6,000-class attainment), steady bubble: x_S 0.260358, **x_R 7.647235** — the archived 7.6472 reproduced to 0.0005% (P1 HELD) |
| SpalartAllmaras | EXCLUDED | 12,000-iteration cap without the sentence; **0** skin-friction sign changes |
| kEpsilon | EXCLUDED | **S1 FPE at iteration 13** (exit −8), no written time — the family-B high-Re k-family crash class, now on the hills; the triage-table row applies |
| realizableKE | EXCLUDED | cap without the sentence; **0** sign changes |

**Entry-1 question 1 — does any closure enter [4.21, 4.70]?** Of the one
closure that produces a gateable number, none enters: SST sits at 7.6472,
+72% above the midpoint (the F6b physics FAIL, re-measured by a fresh solve).
The other three produce **no gateable number at this rung**: the record can
say only that no closure is measured inside the band, and only one closure
is measured at all.

**Entry-1 question 2 — does the inter-model band contain it?**
**VERDICT REFUSED: n = 1 admitted member.** No band exists (the batch's own
≥2 rule), and the pre-registered membership clause — the first application
of `no-containment-verdict-below-n3` — bars any containment statement.
The band artifact says "no band, 1 converged member" and that is the whole
of what may be claimed.

**Predictions, scored:** P1 HELD (0.0005%). P2 HELD, and over-fulfilled —
realizableKE failed as named, and so did both other non-SST members.
P3 NOT EVALUABLE as registered (its containment consequence required n ≥ 3,
which the membership clause refused); its per-member half held on the single
admitted member (7.647 > 4.70), stated without weight. The named risk FIRED
for SA and realizableKE (no steady bubble) — with the honesty note the
pre-registration's clause 3 exists to force: **0 crossings on an
unconverged field is not a claim that these models predict attached flow;
it is the absence of a gateable number, nothing more.**

**What the excluded members' logs actually show (zero-compute read, decisive
for the successor):** SA and realizableKE were **still descending
monotonically at the cap** — SA's Ux/p initial residuals fell 2.2e-5 →
5.1e-6 → 1.1e-6 across iterations 4,000/8,000/12,000 (a factor ~4.5 per
4,000, extrapolating to the 1e-6 targets within roughly 2,000–4,000 more
iterations), realizableKE the same shape at ~2e-5 at the cap. **This is NOT
the N_a10 unreachable-floor class** — the original criterion looks
reachable, the cap simply guillotined two slow convergers at 2× the
attainment of the two fast ones (the settle-vs-cap trap, §8a.1's lesson at
a different scale). An adjusted criterion is therefore NOT the right rescue
here and none is proposed; the right successor is an **extension arm**
(re-run SA and realizableKE at a 30,000 cap, ~2×12 core-min measured rate,
own pre-registration) that either seats them as members — making the n≥3
containment question answerable — or converts "slow" into a measured
non-convergence finding. kEpsilon's instant FPE is a different, precedented
class and needs the family-B-style diagnosis arm instead. Both filed as
successor recommendations for the chief's docket pass, not run.

**What entry 1 gets today:** not the anticipated either/or. The measured
finding is that **the inter-model band methodology hits a family-convergence
wall on the hills**: at the rung where SST converges cleanly and
reproducibly, three of four closures fail a uniform gate (crash, slow, slow)
— the bump's family-B result (0 of 4) now has a two-case pattern on
pressure-gradient/separated internal flow. For the epistemic-uncertainty
showcase, the hills currently contribute a one-member "band" that is no band
at all, and the honest sentence is the refusal — which is itself the first
live demonstration of why the n<3 rule deserves adoption.
