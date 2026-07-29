# F5a — unsteady cylinder Reynolds ladder

Ladder: Re 1000 -> 2000 -> 3900 -> 5000 -> 10,000 -> 1e5 -> 1e6. Each rung must
pass its gate before the next starts.

**Provenance note.** The agent running this ladder was interrupted twice and left
results on disk without a report. Re 1000 and the first 63% of Re 2000 were
salvaged by the supervisor directly from solver output on 2026-07-29 ~02:0x UTC,
and recorded with **no citable reference values** — the record explicitly said
the completed Re 1000 rung was ungated because no reference had been verified.

**This update (2026-07-29, ~20:15-20:35 UTC) corrects two things found stale by
L-1 (check the record against the filesystem before redoing work), and closes the
reference gap that made the previous record ungated:**

1. Re 2000 **had already finished** by the time this session started. A relaunch
   at 02:16:14Z crashed immediately on a cwd bug (`cannot find file
   ".../system/controlDict"`, logged as `FAILED_ATTEMPT_cwd_bug`); the very next
   relaunch at 02:16:45Z ran clean to `t=90` and finished at 03:23:00Z,
   3965.11 s ClockTime. The "INCOMPLETE at 63%" note below was true when written
   and is now stale — the corrected numbers are in the table.
2. Real citable references now exist for the Re 1000 rung, on **both** sides of
   the dimensionality question the brief asked for. Re 2000's reference is
   weaker and is flagged as such, not silently upgraded to match Re 1000's
   confidence.

---

## Measured

| rung | status | Cd_mean | Cd std | Cl_rms | St | wall-time | mesh |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Re 1000 | complete, t=90 | **1.4678** | 0.1445 | 0.9666 | **0.2343** | 2417.17 s | 22,400 cells |
| Re 2000 | **complete, t=90** (corrected) | **1.5879** | 0.2095 | 1.1837 | **0.2421** | 3965.11 s | 27,360 cells |
| Re 3900 | **running**, launched 20260729T203008Z | — | — | — | — | predicted ~6,400 s (see cost model) | 44,000 cells |

Statistics taken over the second half of each run (t=45-90). Strouhal from
mean-crossing periods of the lift signal. Re 2000's full-window numbers were
recomputed directly from `postProcessing/forceCoeffs1/0/coefficient.dat`
(10,204 rows, full t=0.0045-90) — independently re-derived, not copied from
any agent's self-report, per L-2. Re 1000's independent recomputation matches
the salvaged record to 4 decimal places on every column, which is itself a
confirmation that the salvage was accurate.

Each rung's mesh is **sized up for the rung**, not shared: 22,400 -> 27,360 ->
44,000 cells for Re 1000 -> 2000 -> 3900. This is appropriate (finer Re needs
finer near-wall and near-wake resolution to keep the same 2D "DNS-style"
un-modelled solve well resolved) and answers the ladder's own open learning
question — "mesh that converged: not yet established per rung" — each rung
now has its cell count on the record.

## A methodology trap found and corrected before Re 3900 launched

The Re 3900 case directory had already been staged (mesh built, `checkMesh`
clean) by whatever agent instance was interrupted. It was staged as a **2D
URANS run with the kOmegaSST turbulence closure** — `constant/turbulenceProperties`
said `simulationType RAS; RASModel kOmegaSST;`, and `0/` carried `k`, `omega`,
`nut` initial fields that Re 1000 and Re 2000 never had. `case_preflight.sh`
passed it clean as a kOmegaSST case.

This was not a preflight-catchable bug (fields matched the model, decomposition
was consistent) — it was a **silent methodology fork**. Every rung from Re 100
through Re 2000 was run laminar: the incompressible Navier-Stokes equations
with no turbulence model at all, deliberately, because the entire point of this
ladder is to measure what an **un-modelled 2D solve** predicts against 3D
reality, so the deviation can be attributed to dimensionality and nothing else.
Switching to kOmegaSST at Re 3900 would have moved two variables at once —
Reynolds number (intended) and turbulence closure (not logged, not decided
here) — which is exactly what P5 forbids: "one change per rung, or the result
teaches nothing." A deviation at Re 3900 measured against a kOmegaSST run could
not be attributed to dimensionality vs turbulence-model error vs Re increase;
the whole point of the ladder would have been lost on its most important rung.

**Reverted before launch:** `turbulenceProperties` set back to
`simulationType laminar` (byte-identical to Re 1000 / Re 2000's), and the
`0/k`, `0/omega`, `0/nut` files removed so `0/` now matches the established
`U`, `p`-only convention. `case_preflight.sh` re-run clean as `model: laminar`.
Mesh, `deltaT`, `endTime`, `maxCo` were left exactly as staged — those are Re
3900-specific choices, not the turbulence-model fork, and there is no reason to
distrust them.

**This is worth a LESSONS.md entry** (added below): a staged case that passes
preflight can still encode an undocumented change of experimental variable.
Preflight checks internal consistency (fields match model); it cannot check
consistency *against a sibling case's convention*, because it has no memory of
what the ladder has been doing. That check has to be done by eye, every time a
rung is inherited from an interrupted agent.

## Gate: Re 1000 (point reference, high confidence)

**Reference: Jiang, H. & Cheng, L. (2017). "Strouhal-Reynolds number
relationship for flow past a circular cylinder." *Journal of Fluid Mechanics*
832, 170-188.** Open-access accepted manuscript retrieved from the University
of Western Australia research repository. This paper runs both 2D and 3D DNS
of exactly this geometry up to exactly Re=1000 (their stated study ceiling),
using OpenFOAM, and reports a 2D/3D mesh-convergence table at Re=1000 (their
Tables 2 and 3) that itself cross-validates against four independent sources:

| source | type | St | Cd_mean | Cl_rms |
| --- | --- | --- | --- | --- |
| Jiang & Cheng (2017), refined 2D mesh | 2D DNS | 0.2377 | 1.513 | 1.031 |
| Henderson (1997), *J. Fluid Mech.* 352 | 2D DNS (independent code) | 0.237 | 1.505 | — |
| **Jiang & Cheng (2017), refined 3D mesh** | **3D DNS** | **0.2105** | **1.0138** | **0.1191** |
| Papaioannou et al. (2006), *J. Fluid Mech.* 558 | 3D DNS (independent) | 0.216 | 1.030 | — |
| Tong et al. (2015) | 3D DNS (independent) | 0.215 | 1.08 | 0.20 |
| Williamson & Brown (1998), *Phys. Fluids* 10 | 3D **experiment** | 0.212 | — | — |
| Norberg (1994), *J. Fluid Mech.* 258 | 3D **experiment** | 0.210 | — | — |

**Our measured Re 1000 (2D laminar, this ladder): Cd_mean=1.4678, Cl_rms=0.9666,
St=0.2343.**

| metric | vs 2D reference (avg 2D DNS ~1.509 / 0.2374 / 1.031) | vs 3D reference (source-to-source range, not an average) | verdict |
| --- | --- | --- | --- |
| Cd_mean | **-2.7%** | **+35.9% to +44.8%** (Tong 1.08 low, Jiang & Cheng 1.0138 high; Papaioannou 1.030 mid at +42.5%) | matches 2D family tightly; over-predicts 3D by the documented amount |
| St | **-1.3%** | **+8.5% to +11.6%** (Papaioannou 0.216 low, Norberg 0.210 high) | matches 2D family tightly; over-predicts 3D by the documented amount |
| Cl_rms | **-6.2%** | **+383% to +712%** (Tong 0.20 low, Jiang & Cheng 0.1191 high) | matches 2D family; 3D Cl_rms collapses by close to an order of magnitude |

Every deviation above is stated as a **source-to-source range**, computed
individually against each cited 3D value, not as a deviation against the
average of the sources. (An earlier draft of this record mixed bases — an
average-based lower bound paired with an extreme-based upper bound on the Cd
row, which understates the true spread and is internally inconsistent with
its own source table. Caught in review and corrected; St and Cl_rms were
checked on the same pass and were already computed on the correct,
extreme-to-extreme basis.)

**Verdict: GATE REACHED, correctly attributed.** The solve agrees with
independent 2D DNS to within a few percent on every metric (Cd, St, and Cl_rms
all move together) — that is the check that the solver itself is not at fault.
It then deviates from 3D experiment/DNS by a large, directionally-consistent,
mechanistically-explained amount, worst on Cl_rms. Jiang & Cheng's own
mechanism (Section 4.2 of the paper) explains exactly why: in the 3D flow the
recirculation region is longer, so the separating shear layer is weaker at the
point of shedding and less driven by the vortex rolling up on the opposite
side of the cylinder — the 3D vortex-shedding frequency and the momentum it
carries both drop relative to 2D. The huge Cl_rms gap is the classic,
independently-documented signature of spanwise phase decorrelation: a 3D wake
sheds vortices with a spanwise-varying phase, so the span-integrated lift
partially cancels, while a 2D solve has no span to decorrelate across and
integrates a single in-phase signal. This is a **known, referenced physical
mechanism**, not an unexplained residual.

## Gate: Re 1000, 3D — turning the attribution into a demonstration (DESIGN PHASE, launch pending scheduling)

The Re 1000 gate above is an **attribution**: our 2D numbers are high by
almost exactly the amount 2D-vs-3D DNS is documented to differ, so the gap
is credited to dimensionality rather than solver error. That is an
argument, not a demonstration, and a skeptical reader is entitled to call it
a convenient excuse for a high drag number. The only way to turn it into a
demonstration is to run the SAME cylinder at the SAME Re in 3D on our own
solver and see whether it lands in the 3D family on its own. This section is
the design and cost work for that run, done before any core-hour is spent,
per the standing instruction to design first and wait to be scheduled. **No
production solve has been launched.** Two brief, bounded, serial-or-4/8-rank
calibration probes were run (seconds to ~100s each) purely to measure mesh
quality and cost — those are reported below and are not the gate.

### Reference extraction: Jiang & Cheng (2017) fetched and read directly

The 2D gate above already cites Jiang & Cheng (2017), *J. Fluid Mech.*
832:170-188 for its 3D-family numbers. For this design, the accepted
manuscript (UWA repository copy) was fetched and read in full — not
web-search-summarised — specifically for their own mesh-design and
mesh-dependence tables, since they are the ones building exactly this
geometry at exactly this Re in 3D and reporting how sensitive their answer
is to the two knobs this task has to choose: spanwise domain length and
spanwise cell size.

**Their mesh (Table 1, "Refined mesh," used for 300 < Re <= 1000):**
domain 30D to inlet/crossflow/outlet, 240 nodes around the cylinder
perimeter, first layer 2.315e-4 D, growth ratio <= 1.1, **spanwise domain
length Lz/D = 6, spanwise cell length dz/D = 0.05**.

**Their own 3D mesh-dependence study at Re=1000 (Table 3, the reference case
is Lz/D=6, dz/D=0.05):**

| case | Lz/D | dz/D | St | Cd | Cl_rms | -Cpb |
| --- | --- | --- | --- | --- | --- | --- |
| 1 (reference, adopted) | 6 | 0.05 | 0.2105 | 1.0138 | 0.1191 | 0.8373 |
| 2 (Lz doubled) | 12 | 0.05 | 0.2098 | 1.0104 | 0.1063 | 0.8320 |
| 3 (dz to 0.03) | 6 | 0.03 | 0.2106 | 1.0002 | 0.0998 | 0.8148 |
| 4 (dz to 0.0706) | 6 | 0.0706 | 0.2111 | 1.0420 | 0.1597 | 0.8759 |
| 5 (dz to 0.1) | 6 | 0.1 | 0.2125 | 1.0467 | 0.1624 | 0.8836 |
| Papaioannou et al. (2006), DNS | 3pi | 0.147 | 0.216 | 1.030 | — | 0.815 |
| Tong et al. (2015), DNS | 10 | 0.1 | 0.215 | 1.08 | 0.20 | 0.89 |
| Williamson & Brown (1998), exp. | — | — | 0.212 | — | — | — |
| Norberg (1994), exp. | — | — | 0.210 | — | — | 0.810 |

Their own text states the mechanism plainly: *"an increase in Lz to 12D
results in very close numerical results"* (case 1 vs 2, largest move
~11% on Cl_rms only, and it moves TOWARD the experimental band, not away),
so Lz/D=6 is adequate at Re=1000, because Mode A (spanwise wavelength ~4D,
needs Lz>10D, Henderson 1997 restricted Lz=3.96D specifically to force a
single Mode-A wavelength at Re=195) has already vanished by Re~270, leaving
Mode B (wavelength <1D, "becomes finer with increasing Re") as the only wake
mode at Re=1000. Forces are **much more sensitive to dz than to Lz**: dz
0.05->0.1 moves Cd +3.2% and Cl_rms +36%, because a coarse spanwise grid
cannot resolve Mode B's finer streamwise vortices and under-decorrelates the
span — this is precisely why Cl_rms is the discriminating quantity the task
brief called out, and precisely why it is the metric most at risk from an
under-resourced spanwise mesh.

### The design

Only one variable is added relative to the established, already-gated 2D
Re=1000 rung: a real, resolved spanwise dimension. Everything else — Re,
laminar closure, in-plane O-grid topology, farfield extent, first-cell
height, dt0, maxCo — is held **byte-identical** to the `re1000` rung
(verified: `block_mesh_dict(1.0, 20.0, 80, 70, 0.00447, span=0.1)` with the
new function reproduces the existing `re1000/system/blockMeshDict` exactly,
diffed to zero). This is the direct application of the ladder's own P5
discipline ("one change per rung") to a rung that is not even on the
Reynolds axis — the axis being changed here is dimensionality itself, so it
alone must move.

- **Spanwise domain, Lz/D = 6.** Taken directly from Jiang & Cheng's own
  converged choice for this exact Re, not an independent guess — and their
  own sensitivity case (Lz=12D) confirms 6D is not confinement-limited at
  Re=1000, because Mode A (the mode that needs a long span) is not present
  at this Re.
- **Spanwise resolution: two presets, both built and mesh-checked.**
  - `reference`, dz/D = 0.05 → 120 spanwise cells → **2,688,000 total
    cells**. Reproduces Jiang & Cheng's own validated resolution exactly.
  - `pilot`, dz/D = 0.10 → 60 spanwise cells → **1,344,000 total cells**.
    Their own least-resolved sensitivity case (Table 3 case 5) — Cd and
    Cl_rms visibly biased high relative to their converged case (+3.2%,
    +36%), but Cl_rms is still 0.1624, i.e. **6-7x below** the 2D value
    (~0.97-1.03), still discriminating 2D from 3D by close to an order of
    magnitude even though it is not grid-converged in the tight sense their
    production mesh is.
- **Spanwise boundary condition: cyclic (periodic), not a real end wall.**
  Standard for this class of DNS/LES (approximates an infinite cylinder
  without a physical end-wall's own confinement); implemented as a
  translational front/back patch pair, auto-detected by blockMesh from the
  matching geometry.
- **Seeding.** A z-uniform initial condition sitting exactly on the cyclic
  boundary's own symmetry plane can take a long time to grow 3D structure
  from floating-point round-off alone. `setFieldsDict` carves the span into
  12 alternating 0.5D slabs (fundamental wavelength 2x0.5D = **1D, matched
  to the Mode-B wavelength target**) each given a +/-0.02 U_inf spanwise
  velocity kick — the direct 3D analogue of the +/-0.1 crossflow
  perturbation this same codebase already uses to seed 2D shedding from an
  impulsive start, and for the same reason: small enough not to bias the
  eventual limit cycle (checked independently by the existing
  `halves_drift` stationarity gate), shaped at the target wavelength so it
  does not have to wait on whichever wavelength round-off excites first.
- **Force normalization.** `Aref = D x Lz` using the actual simulated span
  (6D), matching Jiang & Cheng's own CD/CL definition (`FD /
  (0.5 rho U^2 D Lz)`) — this makes the reported Cd/Cl directly, not just
  loosely, comparable: both are span-averaged coefficients over the real
  simulated span, not an arbitrary per-length convention.

Implementation: `sdk/workflows/cylinder_vortex_shedding.py`'s
`block_mesh_dict()` gained optional `n_span`/`spanwise_bc` parameters
(default `n_span=1`, `spanwise_bc="empty"`, verified byte-identical output
for every existing 2D caller with those defaults — no other rung is
affected). The new case builder lives in
`demo-output/website/campaign/F5_runs/cylinder_ladder_3d.py`.

### Mesh sizing: both presets actually built and checkMesh'd (free, serial, <30s each)

| preset | cells | blockMesh | checkMesh | non-orth (max) | skewness (max) | aspect ratio (max) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `pilot` (dz/D=0.1) | 1,344,000 | 7.2 s | 13.9 s | 4.6e-6 | 0.0266 | — | **Mesh OK**, clean |
| `reference` (dz/D=0.05) | 2,688,000 | 13.9 s | 28.4 s | 4.6e-6 | 0.0266 | 26.4 | **Failed 1 check** — 33,600 cells (one full near-wall ring: 4 blocks x 70 tangential x 120 spanwise) flagged for small cell determinant (<0.001) |

The `reference` mesh's determinant flag is a genuine, measured finding, not
a hypothetical one: pairing the near-wall first cell (0.00447D, unchanged
from the 2D rung) with the finer dz=0.05D spanwise cell produces extremely
anisotropic hexahedra whose normalized determinant metric trips checkMesh's
threshold, even though non-orthogonality and skewness stay excellent
(unaffected by dz). This is a known false-positive-prone check for
boundary-layer-type meshes and the cells are not necessarily invalid, but
solver tolerance was **not verified** — no solve was attempted on this
mesh. Until that is checked (or the near-wall/spanwise aspect ratio is
eased), the `reference` preset is not launch-clean; `pilot` is.

### Cost calibration: measured, not guessed, and explicitly a worst case

Two short, bounded probes were run on the `pilot` mesh (1,344,000 cells) to
replace guesswork with a real number: `setFields` (seeding), `decomposePar`,
then `pimpleFoam -parallel` under a hard wall-clock `timeout`, read from the
log's own per-step `Time =` / `ExecutionTime =` pairs (no self-reported
number, independently parsed).

| ranks | wall time | sim time reached | steps | rate (wall-s / sim-time unit) |
| --- | --- | --- | --- | --- |
| 4 | 92.7 s | 0.0724 | 9 | ~1280 |
| 8 | 93.6 s | 0.1089 | 12 | ~870 |

4->8 ranks: sim-time-per-wall-second improved ~1.5x, i.e. **~75% parallel
efficiency** for that doubling — measured, not assumed. **This calibration
window is entirely inside the impulsive-start transient** (deltaT still
climbing from 0.0057 toward the Courant-limited ceiling, and the first
pressure solve took 223 PCG iterations vs the handful a settled periodic
solve typically needs), so these rates are a pessimistic **upper bound** on
production cost, not a converged steady-state rate — getting an actual
steady-state number would require running long enough to leave the
transient, which is exactly the "large parallel run" this design phase was
told to hold off on.

**Extrapolated wall-time for a full run to end_time=90 (matching every
other rung's convention, not the literature's 800+ time-unit statistics
window — a limitation stated openly below, not hidden):**

| ranks | using the measured (pessimistic) rate | if the rate improves ~15-20% once past the transient (unverified extrapolation, not measured) |
| --- | --- | --- |
| 4 | ~1280 x 90 = 115,200 s (**~32 hours**) | ~26-27 hours |
| 8 | ~870 x 90 = 78,300 s (**~21.75 hours**) | ~18 hours |
| 16 (whole box, extrapolated efficiency, not measured) | ~55,900 s (**~15.5 hours**) | ~13 hours |

Memory: the `pilot` mesh occupies 221 MB on disk (`constant/polyMesh`);
running memory for a laminar `pimpleFoam` case of this size is expected in
the low single-digit GB decomposed across ranks (not separately measured
under load — the calibration ran with 21-28 GB free at the time).

### The honest conclusion this design work reaches

**Even the cheaper, mesh-clean `pilot` preset does not fit an idle-box
budget of a few hours — it is a 13-to-32-hour job depending on core count,
an order of magnitude past every other rung on this ladder** (Re 3900's
44,000-cell 2D case predicts ~1.8 hours; this 3D case is ~30x more cells
and produces ~10-20x more wall-time even in its cheapest, most optimistic
configuration). The literature-exact `reference` preset (2,688,000 cells,
plus its unresolved determinant flag) would cost roughly double that again.
This machine (16 cores, 30 GB RAM) can build and mesh-check either design
for free in under 30 seconds; it cannot solve either one in the time a
single agent turn, or even a single day of shared use alongside the other
live jobs (Re 3900, the hump SA resume, the r4 band-tightening sweep, and
whatever needs the 26 GB uncapped-memory window), comfortably allows.

**What it would take:** either (a) exclusive access to 8-16 cores for
roughly a day, scheduled once the other live jobs referenced above have
cleared, using the `pilot` preset and accepting its documented ~6-7x (not
literature's tighter ~8x) Cl_rms discrimination and the shortened (t=90 vs
800+) statistics window as stated limitations; or (b) more cores/a bigger
box, which would also let the `reference` preset's determinant flag be
resolved by adding in-plane near-wall resolution rather than only accepting
it; or (c) accepting a still-cheaper, still-honestly-labelled design (e.g.
a coarser in-plane mesh dedicated to this test alone, trading fidelity on
Cd/St to buy wall-time) if the supervisor decides the resource case above
does not clear the bar. This is the number the hardware conversation
elsewhere in this project needs.

### Pre-stated expectation (written before any production solve, per P2)

If launched as designed (`pilot`, Lz/D=6, dz/D=0.1, cyclic span, seeded,
end_time=90, stats window t=45-90 matching every other rung):
- **St** should land close to the 3D family (~0.21), clearly below the 2D
  rung's 0.2343 and below our own 2D 3D-deviation of +8.5 to +11.6%.
- **Cd** should drop from the 2D rung's 1.4678 toward the 3D family
  (~1.01-1.08), likely still slightly high versus Jiang & Cheng's own
  converged 1.0138 given the coarser dz/D=0.1 (their own case 5 at this
  same dz shows +3.2% high, i.e. ~1.03-1.08 is the expected band).
- **Cl_rms is the test.** Expected to collapse from the 2D rung's 0.9666
  by roughly an order of magnitude, landing in the 0.12-0.20 range if the
  seeded Mode-B structure saturates within the t=45 pre-averaging window;
  landing anywhere close to the 2D value (~1) would mean the run
  reproduced an expensive 2D answer — either the transient/growth time was
  too short for genuine 3D decorrelation, or the spanwise resolution was
  too coarse to resolve it — and would be reported as that failure, not
  reinterpreted after the fact.

**No launch has been made.** Awaiting scheduling given the live jobs above.

## Gate: Re 2000 (banded reference, lower confidence — and said so)

No paper was found, despite a genuine search (WebSearch, Unpaywall DOI lookups,
and direct download attempts against Physics of Fluids, JFM, Journal of Fluids
and Structures, and Annual Reviews) that reports a **point value** of Cd or St
at exactly Re=2000 for either a 2D or a 3D simulation, or for experiment.
Jiang & Cheng (2017) stops at Re=1000 by design. Norberg (2003), Williamson
(1996), and Fey/König/Eckelmann (1998) — the three papers most likely to carry
a Re=2000 data point on a continuous curve — are all paywalled with no
Unpaywall-listed open-access copy, and no legitimate free copy was located.

**What is available and citable: the regime classification and the
Cd/St-plateau band.** Zdravkovich's (1997) disturbance-free flow-regime table
places Re=1000-2000 at the boundary between "lower subcritical" (TrSL1) and
"intermediate subcritical" (TrSL2), i.e. Re=2000 sits inside the intermediate
subcritical band that runs to roughly 2-4x10^4. Zdravkovich's (1990) force-
coefficient compilation (reproduced as Fig. 3.3 in Lupi, F. (2014), PhD
dissertation, Ch. 3 "Flow around circular cylinders: state of the art",
Università degli Studi di Firenze — a secondary source chosen because the
primary Zdravkovich monograph was not obtainable, and the figure is explicitly
attributed and reproduced from Zdravkovich 1990 within it) shows Cd
**quasi-invariant across the whole subcritical band at Cd ~ 1.0-1.2**, and the
independently corroborated general-knowledge value for St in the same band is
**~0.19-0.21** (multiple independent tertiary sources agree on this range for
300 < Re < ~2x10^5; no single primary point citation at Re=2000 specifically).

**Our measured Re 2000 (2D laminar, this ladder): Cd_mean=1.5879, St=0.2421.**

| metric | vs 3D subcritical band (Cd~1.0-1.2 mid 1.1, St~0.19-0.21 mid 0.20) | verdict |
| --- | --- | --- |
| Cd_mean | **+32% to +59%** (mid-band: +44%) | consistent direction and similar magnitude to Re 1000's +35.9% to +44.8% (source range) |
| St | **+15% to +27%** (mid-band: +21%) | consistent direction; larger than Re 1000's +8.5-11.6%, worth tracking |

**Verdict: GATED, BANDED, LOWER CONFIDENCE — not a point gate.** The direction
and rough magnitude of the deviation match the Re 1000 pattern and the
established dimensionality mechanism, which is reassuring, but this is a
compilation-band comparison, not a matched-case comparison the way Re 1000 has.
No 2D-simulation cross-check exists at Re=2000 either, so unlike Re 1000 there
is no independent confirmation that the solver itself is behaving correctly at
this rung — only that its answer is in the right ballpark and the right
direction. **Stated honestly: this is weaker evidence than Re 1000's gate, and
it is reported as such rather than dressed up to look equally solid.** A
follow-up worth doing cheaply (zero core-minutes, P3) is a direct attempt at
Norberg (2003) or Williamson (1996) via institutional/library access, since
those are almost certainly the papers that would turn this into a point gate.

One internal-consistency note worth flagging, not over-interpreting on n=2:
the St deviation *grew* from Re 1000 to Re 2000 (+8.5-11.6% -> +15-27%) while
the Cd deviation stayed roughly flat (+35.9-44.8% -> +32-59%, bands overlap). If
that trend holds at Re 3900 — where a real point reference exists — it would
suggest St_2D keeps climbing past where St_3D has already plateaued, widening
the shedding-frequency gap faster than the drag gap as Re increases. That is a
prediction, written down before Re 3900's gate is computed, per P2.

## The 2D question, restated with numbers instead of a placeholder

Above Re ~190 the real cylinder wake is three-dimensional (mode A, then mode
B instability). A 2D solve has no span to shed momentum into, so it
systematically over-predicts drag, shedding frequency, and — most
dramatically — fluctuating lift, because span-wise phase decorrelation is the
main thing that suppresses 3D Cl_rms and a 2D solve cannot decorrelate across
a span it does not have. That is no longer an assertion pending a reference;
Re 1000 now has the reference, the mechanism, and numbers that move together
across five independent citations. Re 2000 has the same direction on a wider
band.

## Cost model (D13) — prediction revised on real data, before Re 3900 completes

| rung | wall-time | vs Re 100 | vs previous rung |
| --- | --- | --- | --- |
| Re 100 (batch family) | ~250 s | 1.0x | — |
| Re 1000 | 2417.17 s | **9.67x** | 9.67x per 10x Re |
| Re 2000 | 3965.11 s (actual, corrected from the 3715 s projection) | 15.86x | **1.640x per 2x Re** |

**The flat "~10x per decade, exponent ~0.99" rule from the previous write-up
does not hold going from Re 1000 to Re 2000.** Fit locally: cost ~ Re^n with
n = ln(3965.11/2417.17) / ln(2) = **0.714**, well below the 0.985 measured from
Re 100 to Re 1000. The projection this ladder posted for Re 2000 before it
finished (3715 s, D13) was only 6.7% off — a reasonable local extrapolation —
but the *global* exponent has clearly dropped as Re rises. This matches the
`adjustTimeStep`/`maxCo` mechanics: at fixed maxCo the timestep is set by the
fastest local cell velocity, and as the wake sheds more vigorously at higher
Re the timestep shrinks by less than the mesh refinement alone would predict,
because the refined mesh's smaller cells are partly offset by the flow not
accelerating linearly with Re everywhere in the domain.

**Revised prediction for Re 3900, using the local (Re 1000 -> Re 2000)
exponent rather than the stale decade-average one:**

predicted = 2417.17 s x (3900/1000)^0.714 = **~6,390 s (~1.77 hours)**,
materially lower than the 9,240 s figure this ladder posted before Re 2000 had
actually finished. This prediction is on the record now, written at
2026-07-29 ~20:33 UTC while the Re 3900 run is at t~1 of 90 (~1% complete),
before the outcome is known, per P2. If Re 3900 lands far from 6,390 s, the
locally-fit exponent is itself the thing that was wrong, and that will be
reported plainly rather than re-fit after the fact to look right.

## Why Re 3900 is the rung that matters

It is the canonical cylinder-wake benchmark, with extensive published LES, DNS
and experimental data (Lourenco & Shih 1993; Ong & Wallace 1996; Kravchenko &
Moin 2000; Parnaudeau et al. 2008) — several of which were seen directly
during this session's reference search (a 2018 ICCM SST-IDDES study
tabulates Cd, -Cpb, St, and L_rec/D from six independent Re=3900 sources side
by side: PIV experiment 0.99/0.88/0.215/1.33; DNS 0.84/-/0.220/1.59; SST-DES
1.08/-/0.220/0.98; DNS 1.03/0.93/0.220/1.30; LES 1.14/0.99/0.210/1.04; LES
1.04/0.94/0.210/1.35). Re 3900 is the first rung on this ladder where a
**point** 3D reference is actually easy to obtain — the opposite problem from
Re 2000. It should be gated hard on four quantities, not one: mean drag,
Strouhal number, recirculation-bubble length, and base pressure coefficient,
using that same six-source table.

**Per D6, the Re 3900 rung must also produce a scoped cost estimate for a 3D
LES/DES-class run alongside the 2D result**, so the decision to run 3D comes
back to the docket with a number attached rather than as a guess.

## Learning questions (D6, answered as the ladder climbs)

- **Mesh that converged:** now recorded per rung — 22,400 (Re 1000), 27,360
  (Re 2000), 44,000 (Re 3900) cells, each sized up for the rung rather than
  shared.
- **Where 2D stops being defensible:** physically, above Re ~190. Re 1000's
  gate now demonstrates *why*, quantitatively and with a cited mechanism, not
  just asserts it.
- **Cost scaling:** NOT a flat power law. Exponent measured at 0.985 (Re
  100->1000) and 0.714 (Re 1000->2000) — it is dropping, and the Re 3900
  prediction has been revised down accordingly (6,390 s vs the earlier 9,240 s
  decade-average projection).
- **Steady vs unsteady:** the batch's steady cylinder family runs ~2.4 s per
  evaluation against ~394 s for the unsteady family at Re 100-1000 — a factor
  of roughly 164x, measured, and the dominant cost driver in the whole batch.
- **New this update — a staged case is not a validated case.** Inheriting a
  case directory that passes `case_preflight.sh` is not the same as inheriting
  a case that matches the ladder's established methodology. See the
  methodology-trap section above; the corresponding LESSONS.md entry is L-11.
