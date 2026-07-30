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
| Re 3900 | **complete, t=90** (finished 20260729T233155Z) — **provisional**, see spacing trap below | **1.7547** | — (envelope 1.1713) | 1.4133 | **0.2493** | 10,902 s | 44,000 cells |
| Re 3900 (corrected spacing) | **running**, launched 20260729T233553Z | — | — | — | — | — | 44,000 cells |

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
- **Spanwise resolution: three presets, all built and mesh-checked** (the
  third, `reference_clean`, was added after the determinant follow-up
  below — see that section for why).
  - `reference_exact`, dz/D = 0.05 → 120 spanwise cells → **2,688,000 total
    cells**. Reproduces Jiang & Cheng's own validated resolution exactly.
    **Fails checkMesh** (see below) — kept for citation fidelity, not
    launch-clean.
  - `reference_clean`, dz/D = 0.05217 (n_span=115) → **2,576,000 total
    cells**. ~4.3% coarser than Jiang & Cheng's own value, found by a free
    checkMesh sweep to be the closest clean point to their resolution —
    **recommended over `reference_exact`.**
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

### Mesh sizing: all three presets actually built and checkMesh'd (free, serial, <30s each)

| preset | cells | blockMesh | checkMesh | non-orth (max) | skewness (max) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `pilot` (dz/D=0.1) | 1,344,000 | 7.2 s | 13.9 s | 4.6e-6 | 0.0266 | **Mesh OK**, clean |
| `reference_clean` (dz/D=0.05217) | 2,576,000 | 13.3 s | 27.1 s | 4.4e-6 | 0.0266 | **Mesh OK**, clean |
| `reference_exact` (dz/D=0.05) | 2,688,000 | 13.9 s | 28.4 s | 4.6e-6 | 0.0266 | **Failed 1 check** — 33,600 cells (one full near-wall ring: 4 blocks x 70 tangential x 120 spanwise) flagged for small cell determinant (<0.001) |

### Follow-up on the determinant flag (free, checkMesh-only, no solve): the two questions the supervisor asked before scheduling

**Q1: can `reference_exact` be fixed without touching the in-plane mesh?**
Yes — but the fix runs in the opposite direction from the naive guess.
Holding `n_radial=80`, `n_tangential=70`, `first_cell=0.00447D`,
`farfield_diameters=20` exactly fixed (i.e. touching **only** the spanwise
cell count), a bisection sweep of `dz/D` from 0.03 to 0.10, each point built
with `blockMesh` and checked with `checkMesh -allTopology -allGeometry`:

| dz/D | n_span | cells | min cell determinant | checkMesh |
| --- | --- | --- | --- | --- |
| 0.030 | 200 | 4,480,000 | 0.000166 | FAIL (56,000 cells) |
| 0.040 | 150 | 3,360,000 | 0.000453 | FAIL (42,000 cells) |
| 0.045 | 133 | 2,979,200 | 0.000681 | FAIL (37,240 cells) |
| **0.050** | **120** | **2,688,000** | **0.000959** | **FAIL (33,600 cells) — Jiang & Cheng's own value** |
| 0.05085 | 118 | 2,643,200 | 0.001013 | PASS (1% above threshold — thin margin) |
| **0.05217** | **115** | **2,576,000** | **0.001103** | **PASS — recommended (`reference_clean`)** |
| 0.05357 | 112 | 2,508,800 | 0.001202 | PASS |
| 0.05505 | 109 | 2,441,600 | 0.001312 | PASS |
| 0.060 | 100 | 2,240,000 | 0.001730 | PASS |
| 0.10 | 60 | 1,344,000 | 0.007882 | PASS (`pilot`) |

The minimum cell determinant rises **monotonically** with dz across the
entire tested range — thinner spanwise cells are *worse*-conditioned here,
the opposite of the "finer must mean more extreme aspect ratio in the bad
direction" guess, because the flagged cells sit in the near-wall ring where
the O-grid's curved (`arc`) inner/outer edges give the cell a small
built-in warp; when dz is large that warp is a negligible fraction of the
cell's dominant (spanwise) length scale, but when dz is pulled down toward
the same order as the radial/tangential extent the warp is no longer
swamped and the normalized determinant drops. The clean/failing boundary
sits between dz=0.05085 (n_span=118, 1% above the 0.001 cutoff — too thin a
margin to trust) and dz=0.05 (fails). **`reference_clean` (n_span=115,
dz/D=0.05217, det_min=0.00110) is the closest point to Jiang & Cheng's own
0.05 with a real safety margin, found and verified without moving a single
in-plane parameter.** Per their own Table 3 (dz 0.05 -> Cl_rms 0.1191;
dz 0.0706 -> Cl_rms 0.1597), a point 4.3% off 0.05 should sit very close to
their converged 0.1191, not meaningfully toward 0.1597 — so `reference_clean`
is expected to be a near-exact stand-in for their production mesh, not a
compromise.

**Q2: is spanwise grading legitimate here?** **No**, on both a physics
argument and a measured mesh-quality one.

- *Physics.* Grading means resolving different `dz` at different `z`
  stations. The wall-normal (radial) grading in this same mesh IS
  physically justified: the boundary layer has a real, spatially localized
  steep gradient at the solid wall, so more resolution belongs there. The
  spanwise direction has no analogous feature — the domain is a cyclic,
  translationally periodic approximation of an infinite cylinder, and Mode
  B is a **spatially homogeneous, spanwise-periodic** instability with no
  privileged z-location. Grading dz along z would resolve one region of the
  span more finely than another for no physical reason, risking exactly the
  kind of resolution-dependent bias (favoring growth/phase-locking near the
  fine end, under-resolving it near the coarse end) that would contaminate
  Cl_rms — the quantity this whole test exists to measure honestly. Uniform
  dz, as Jiang & Cheng used, is the physically correct choice.
- *Mesh quality, tested directly.* Three graded variants were built at the
  same total spanwise cell count as `reference_exact` (n_span=120, mean
  dz/D=0.05, `simpleGrading` ratios 2, 4, and 0.5 in the spanwise
  direction) and checkMesh'd:

  | span grading ratio | min cell determinant | checkMesh | vs uniform dz=0.05 (0.000959) |
  | --- | --- | --- | --- |
  | 2.0 | 0.000276 | FAIL (18,480 cells) | worse |
  | 4.0 | 0.0000644 | FAIL (28,280 cells) | much worse |
  | 0.5 | 0.000276 | FAIL (18,480 cells) | worse (mirror of 2.0, as expected) |

  Grading **does not fix the determinant problem — it worsens it**, because
  for a fixed cell count, concentrating cells anywhere necessarily makes
  the cells at the coarse end thinner-relative-to-neighbours than uniform
  spacing would. Grading was a dead end on the mesh-quality question it was
  meant to solve, independent of the physics objection above.

Both answers together mean the choice is not "accept a defect or accept a
weaker in-plane control" — a spanwise-only, in-plane-preserving fix exists
and has been built and verified (`reference_clean`), and grading was
checked and ruled out on its own (non-)merits, not assumed away.

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
window — a limitation stated openly below, not hidden). `reference_clean`
is scaled from the same measured `pilot` rate by its cell-count ratio
(2,576,000 / 1,344,000 = 1.92x) — an extrapolation on top of an
extrapolation, flagged as such, not a second independent measurement:**

| ranks | `pilot` (1.34M cells), measured (pessimistic) rate | `pilot`, optimistic (rate improves 15-20% past transient, unverified) | `reference_clean` (2.58M cells), scaled from the same pessimistic rate |
| --- | --- | --- | --- |
| 4 | ~1280 x 90 = 115,200 s (**~32 h**) | ~26-27 h | ~61 h |
| 8 | ~870 x 90 = 78,300 s (**~21.75 h**) | ~18 h | ~42 h |
| 16 (whole box, extrapolated efficiency, not measured) | ~55,900 s (**~15.5 h**) | ~13 h | ~30 h |

Memory: the `pilot` mesh occupies 221 MB on disk (`constant/polyMesh`);
`reference_clean` (96% as many cells as `reference_exact`) is essentially
the same, ~450-460 MB. Running memory for a laminar `pimpleFoam` case of
this size is expected in the low single-digit GB decomposed across ranks
(not separately measured under load — the calibration ran with 21-28 GB
free at the time).

### The honest conclusion this design work reaches

**Neither mesh-clean preset fits an idle-box budget of a few hours.**
`pilot` is a 13-to-32-hour job; `reference_clean` — now that it exists as a
clean, literature-matching option rather than being blocked by the
determinant defect — is roughly **1.9x that, 30-to-61 hours**, depending on
core count. Both are an order of magnitude past every other rung on this
ladder (Re 3900's 44,000-cell 2D case predicts ~1.8 hours). This machine
(16 cores, 30 GB RAM) can build and mesh-check any of the three designs for
free in under 30 seconds; it cannot solve any of them in the time a single
agent turn, or even a single day of shared use alongside the other live
jobs, comfortably allows.

**The calculus the supervisor asked about has changed, but not toward
"cheap."** Before this follow-up, the choice looked like "accept the
mesh defect and run `reference_exact`, or fall back to the coarser, more
biased `pilot`." Now it is a straight, honest trade with no defect forcing
the hand: `pilot` (13-32 h, accepts the documented +36% Cl_rms /
+3.2% Cd bias from being literature's own worst-resolved case) versus
`reference_clean` (30-61 h, ~4% off Jiang & Cheng's own converged
resolution, expected to land very close to their point numbers). Neither
option involves touching the in-plane mesh, so the 2D-rung control is
preserved either way.

**What it would take:** exclusive access to 8-16 cores for one to two-and-a-
half days, scheduled once the other live jobs (Re 3900, the hump SA resume,
the r4 band-tightening sweep, and whatever needs the 26 GB uncapped-memory
window) have cleared. Given a demo-filming day, the pragmatic recommendation
is `pilot` at 8 ranks (~18-22 h) as the affordable first cut, with
`reference_clean` (~34-42 h at 8 ranks) as the follow-up once the box is
free for a multi-day window — not a fallback forced by a mesh defect, but a
genuine cost/fidelity choice now that both are clean. This is the number
the hardware conversation elsewhere in this project needs.

### Pre-stated expectation (written before any production solve, per P2)

**`reference_clean` (Lz/D=6, dz/D=0.05217, cyclic span, seeded,
end_time=90):** expected to land close to Jiang & Cheng's own point values
— St~0.21, Cd~1.01-1.03, **Cl_rms~0.12-0.14** — since it sits only 4.3% off
their converged dz=0.05 and their own sensitivity table shows forces moving
little over that small a step (dz 0.05->0.0706 is a much bigger relative
move and only takes Cl_rms from 0.1191 to 0.1597).

**`pilot` (Lz/D=6, dz/D=0.1, cyclic span, seeded, end_time=90):** **this
preset IS Jiang & Cheng's own least-resolved sensitivity case (their Table
3 case 5), so its expected bias is literature-quantified, not a guess.**
Stated explicitly now so a correct pilot result is not later misread as a
missed gate:
- **St** should land close to the 3D family (~0.2125 per their case 5),
  clearly below the 2D rung's 0.2343.
- **Cd** is expected around **1.03-1.08** — their own case 5 measured
  1.0467, +3.2% above their converged 1.0138.
- **Cl_rms is the test, and here the expected band is explicitly wider
  than "close to 0.12-0.20": a result of ~0.16-0.27 is the EXPECTED
  outcome for this preset, not a miss.** Their own case 5 (identical
  dz/D=0.1) measured Cl_rms=0.1624, +36% above their converged 0.1191 —
  so a `pilot` result landing in roughly that neighbourhood should be read
  as the run reproducing their own documented dz=0.1 bias correctly, not
  as evidence the 3D setup failed. **What WOULD indicate a real problem:**
  Cl_rms landing anywhere close to the 2D rung's 0.9666 — that specific
  failure mode (an expensive 2D answer) would mean the transient/growth
  time was too short for genuine 3D decorrelation, or the seeding did not
  take, and would be reported as that failure, not reinterpreted after the
  fact. The pass/fail line for the *attribution* claim is "did Cl_rms drop
  by close to an order of magnitude," not "did it exactly hit 0.12-0.20."

**No launch has been made.** Awaiting scheduling given the live jobs above
and the owner's call on a 13-to-61-hour job on a demo-filming day.

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

## Gate: Re 3900 (four-quantity point gate — the rung that matters)

Run finished 2026-07-29 23:31:55Z, clean `End`, expected artifact present,
`t=90.0` reached exactly, 13,838 force-coefficient rows. Wall clock 10,902 s
(`ExecutionTime` 10,899.37 s). Near-wall resolution measured, not assumed:
`yPlus` on the cylinder patch min 0.0349 / **max 1.5325** / average 0.8395 — the
target-y+~1 sizing held, so the wall layer is resolved and the numbers below are
not a wall-treatment artifact.

**Statistics were independently re-derived from the run's own raw
`postProcessing/` output** (`analyze_re3900.py`, zero new core-minutes),
applying the same machinery `cylinder_ladder.py` uses — `time_weighted_stats`,
`measure_period`, `halves_drift`, and the module's own `base_cpb` /
`recirculation_length` logic.

The rung also wrote its own `F5_runs/re3900/record.json`. The independent
re-derivation **reproduces it exactly** on every quantity (Cd 1.7011,
St 0.24094, -Cpb 2.038308, `lr_over_d: null`, `u_min` 0.060774, drift 6.626%
at the t>=45 window) — a genuine L-2 confirmation that the self-report is
accurate, obtained by recomputing from raw solver output rather than by
trusting it. Both are reported because agreement between them is itself
evidence; neither was copied from the other.

**Averaging-window sensitivity, shown rather than hidden** (a single arbitrary
window is not evidence the mean is settled):

| window | Cd_mean | Cd drift | Cl_rms | St |
| --- | --- | --- | --- | --- |
| t >= 45 (half) | 1.7011 | 6.63% | 1.3774 | 0.2409 |
| **t >= 54 (primary)** | **1.7547** | **0.50%** | **1.4133** | **0.2493** |
| t >= 63 | 1.7632 | 1.21% | 1.4135 | 0.2536 |

The t>=45 half-window still carries 6.63% drift — the flow was *not* fully
settled at t=45, so the ladder's default "second half" convention is slightly
too generous at this rung. From t>=54 onward drift collapses to 0.5-1.2% and
the numbers agree to ~0.5% on Cd and ~1.7% on St. **Primary window t>=54**
(lowest drift); the t>=54 -> t>=63 spread is carried as the settled-value
sensitivity, not suppressed.

**Reference — the six-source Re=3900 table** (all six are **3D**: LES, DNS, DES
and PIV experiment), from the ICCM2018 SST-IDDES study seen directly this
session (He, Zhao & Wan, *Numerical Calculations for Smooth Circular Cylinder
Flow at 3900 Reynolds Numbers with SST-IDDES Turbulence Model*, Proc. ICCM2018,
open access), which tabulates its own sources side by side:

| source | method | Cd | -Cpb | St | L_rec/D |
| --- | --- | --- | --- | --- | --- |
| Lourenco & Shih (1993) | PIV **experiment** | 0.99 | 0.88 | 0.215 | 1.33 |
| Ma et al. (2000) | DNS | 0.84 | — | 0.220 | 1.59 |
| Xu et al. (2010) | SST-DES | 1.08 | — | 0.220 | 0.98 |
| Frederic & Tremblay (2002) | DNS | 1.03 | 0.93 | 0.220 | 1.30 |
| Frederic & Tremblay (2002) | LES | 1.14 | 0.99 | 0.210 | 1.04 |
| Kravchenko & Moin (2000) | LES | 1.04 | 0.94 | 0.210 | 1.35 |
| **source-to-source range** | | **0.84-1.14** | **0.88-0.99** | **0.210-0.220** | **0.98-1.59** |

**Our measured Re 3900 (2D laminar, this ladder, t>=54): Cd_mean=1.7547,
St=0.2493, Cl_rms=1.4133, -Cpb=2.0383, L_rec/D = no mean recirculation found.**

| metric | measured | vs 3D reference (source-to-source range) | verdict |
| --- | --- | --- | --- |
| Cd_mean | 1.7547 | **+53.9% to +108.9%** (vs 1.14 low, 0.84 high) | large over-prediction, direction as expected for 2D |
| St | 0.2493 | **+13.3% to +18.7%** (vs 0.220 low, 0.210 high) | over-prediction, direction as expected |
| -Cpb | 2.0383 | **+105.9% to +131.6%** (vs 0.99 low, 0.88 high) | base suction roughly doubled |
| L_rec/D | **none detected** | vs 0.98-1.59 | **NOT MEASURABLE BY THIS METRIC — topological finding, see below** |

Deviations are stated as source-to-source ranges computed individually against
each cited value, matching the convention corrected at the Re 1000 rung.

**Note on the reported envelopes.** `band` in this ladder's machinery is the
peak-to-trough *oscillation envelope*, not an uncertainty interval. Cd's
envelope is 1.1713 and -Cpb's is 3.0046 — these are large because the 2D
shedding is violent, and they are a *finding*, not a reason to distrust the
means (each mean is a time-weighted trapezoidal average over ~11-14 shedding
cycles with <=1.2% drift).

### The recirculation-bubble collapse — the most informative single result

The centerline probe fan (0.05D to 2.4D behind the base, 0.05D spacing) finds
**no mean reversed flow anywhere**. Mean streamwise velocity dips to a minimum
of **+0.0608** at 0.20D behind the base, then recovers monotonically:

| x/D behind base | 0.05 | 0.10 | 0.15 | **0.20** | 0.25 | 0.30 | 0.40 | 0.50 | 0.70 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mean u/U | +0.131 | +0.098 | +0.067 | **+0.061** | +0.095 | +0.153 | +0.276 | +0.417 | +0.583 |

The profile has the correct qualitative shape (deficit, minimum, recovery), so
the probe fan is working and positioned in the wake — the bubble genuinely is
not there. Every 3D reference has L_rec/D between 0.98 and 1.59. **The 2D
laminar solve's mean vortex-formation region has collapsed to below 0.05D**,
i.e. the vortices roll up essentially at the base.

This is not an isolated oddity — it is the *same* mechanism as the other three
deviations, and it makes them mutually consistent rather than three separate
problems: vortices forming at the base means the separating shear layers are at
their strongest when they roll up, which raises base suction (-Cpb doubled),
raises drag (Cd +54-109%), and raises shedding frequency (St +13-19%). This is
precisely the mechanism Jiang & Cheng invoke at the Re 1000 rung, running in
the same direction and now much further: in 3D the recirculation region is
*longer*, the shear layer weaker at shedding, and every derived quantity lower.

**One probe-fan limitation, flagged not buried:** the three most-downstream
probes (2.30/2.35/2.40 D) return byte-identical means (+0.89227), i.e. they are
all landing inside a single cell — the O-grid's radial grading (expansion ratio
280) makes far-wake cells very large. This does not affect L_rec/D (decided
near the base, where cells are fine) but it means the far-wake end of this
probe fan carries no independent information and should not be used for wake-
recovery claims at any rung.

### Re-verdicting L_rec/D: not a failed measurement, an inapplicable metric

The recirculation-length method — sign change of the *time-mean* centerline
velocity — presupposes a wake that holds a quasi-stationary bubble long enough
for a time-mean to resolve one. Checked directly rather than assumed: the raw
(non-averaged) `probesCenterline` series at Re 3900 shows the near-wake
streamwise velocity reversing sign on **34-39% of all 7,275 samples** in
`0.05D <= s/D <= 0.50` (excursions to -1.0 to -1.4, more than the freestream
speed). The flow separates continuously. What breaks is the *mean*, not the
*separation*. Correct record for this quantity at this rung:
**NOT MEASURABLE BY THIS METRIC ON THIS FLOW** — not FAIL, not "none" as if a
bubble should have been there and wasn't found. An inapplicable gate is a
different outcome from a missed one, and conflating them (the same distinction
this ladder already draws for A3/ONERA M6's adjoint: BLOCKED is not FAIL)
misleads in the opposite direction from intended.

Two boundary-condition and probe-placement checks were run before trusting
this, both negative (i.e. both rule out an artifact):
- `constant/polyMesh/boundary`: `cylinder { type wall; }`; `0/U` and the
  *solved* `90/U`: `cylinder { type noSlip; }`; `90/p`: `zeroGradient`. A
  genuine no-slip wall, not slip/symmetry — confirmed in the actual solved
  field, not just the initial condition.
- Probe coordinates (`x = D/2 + s*D`, matching the file's own header
  `# Probe 0 (0.55 0 0.05)`) checked against the mesh's own cylinder radius
  (`arc 0 1 (0.5 0 0)` in `blockMeshDict`) — probe 0 sits 0.05D **downstream of
  the surface**, not inside the solid, not laterally displaced. Independently
  re-sampled the same instant directly from the written `90/` field via a
  throwaway `sample`-type `postProcess` run (a different code path from the
  `probes` function object entirely): **0 of 250 points along the centerline
  have Ux<0** at t=90, agreeing qualitatively with the time-averaged probe
  result. Two independent extraction methods agree; the no-bubble finding is
  real, not a probe artifact.

### The onset is real, it is located, and it is not a smooth extinction

`base_cpb`/`recirculation_length` were re-run against the **already-completed**
Re 1000 and Re 2000 rungs (zero new core-minutes, `cylinder_ladder.py`'s own
functions, same probe-fan geometry) — a check neither of those rungs had had
applied before, because L_rec/D was a Re-3900-only addition to the module:

| rung | L_rec/D | -Cpb | reversal frequency, s/D=0.05-0.25 | mean bubble? |
| --- | --- | --- | --- | --- |
| Re 1000 | **0.397** | 1.608 | 38-48% | yes, clean |
| Re 2000 | **0.254** | 1.863 | 35-42% | yes, shorter |
| Re 3900 | **none** | 2.038 | 34-39% | **no** |

Both lower rungs have a genuine, monotonically shrinking mean bubble. The
breakdown is not gradual across the ladder — it happens specifically between
Re 2000 and Re 3900. **The departure from trend is the strongest part of this
result.** Fit a power law to the two measured points (n = ln(0.254/0.397) /
ln(2) = -0.644) and extrapolate: predicted L_rec/D at Re 3900 = **0.165**
(naive same-ratio reapplication gives 0.163 — the two methods agree). A method
that resolved 0.254D cleanly one rung earlier, extrapolated to predict
~0.165D, and then found **exactly nothing**, is not a continuation of the
shrinking trend. It is a departure from it.

**The mechanism, measured rather than described as "more chaotic":**
reversal *frequency* near the base is flat across all three rungs, 34-48%,
with no trend. What grows is the *asymmetry* of the fluctuation: the largest
positive (downstream-going) excursion in the same near-base window climbs
**0.22 -> 0.52 -> 0.81** from Re 1000 to Re 2000 to Re 3900, while the
negative excursions grow more modestly. The bubble does not disappear because
the flow stops reversing. It disappears because the forward-going swings grow
large enough to swamp the reversal in the time-mean. Specific and falsifiable:
if a corrected-spacing or higher-resolution rerun at Re 3900 shows reversal
frequency dropping sharply (rather than staying ~35%) alongside a recovered
mean bubble, this mechanism is wrong and needs replacing.

**Is 2D always just short of 3D by a fixed ratio, with Re 3900 merely being
where the ratio reaches zero? Checked directly, and the answer is no.**
Jiang & Cheng (2017) plot both 2D and 3D recirculation-type length against Re
up to 1000 (their Fig. 6, "2D and 3D Lf-Re relationships" — read from the
actual figure, not the extracted text, since this is graph data). At Re 1000:
2D DNS ~0.85-0.9D, 3D DNS ~2.0D — a real ~2.2-2.4x gap already exists at the
lowest rung on this ladder, not just at Re 3900. But a *constant* ratio cannot
produce what is actually observed: extrapolating a fixed 2.2-2.4x deficit onto
this ladder's own 2D trend (0.165D predicted at Re 3900) predicts a 3D
recirculation length around 0.36-0.40D at Re 3900 — the real 3D reference is
**1.40D**, nearly 4x more than a fixed-ratio story predicts. The ratio itself
is exploding, not holding steady. That is evidence for a widening, accelerating
divergence between 2D and 3D wake topology, not a proportional shortfall that
happens to reach its endpoint at this particular Re.

**The Lf-vs-Lr trap, stated explicitly so the next person does not fall into
it.** Jiang & Cheng's Fig. 6 is titled "Lf-Re," formation length, not
recirculation length — a different, conventionally *longer* quantity (referenced
to the fluctuation peak rather than the mean-velocity sign change), and the
~2x gap between their 2D Lf~0.85-0.9 and this ladder's own Re 1000 Lr=0.397
is exactly what comparing the wrong pair of quantities produces, not a defect
in either dataset. **Checked against the primary source rather than assumed:**
Parnaudeau et al. (2008) — the paper this ladder's Re 3900 gate cites for its
1.40D reference — defines its own `Lr` explicitly: "the recirculation length
Lr corresponds to the distance between the base of the cylinder and the sign
change of the centerline mean longitudinal velocity" (their Table II caption
separately lists `Lr, recirculation length` and `L<u'u'>, formation length` as
two deliberately distinct columns; the citation used here pulls the `Lr`
column). That is this ladder's own definition, exactly. **The Re 3900 gate's
external reference is definition-matched, not merely self-consistent** — the
comparison is valid as posed.

### Framing: a topological difference, not a percentage

Every other quantity this ladder has gated reads as "2D is high by some
percentage" (Cd +54-109%, St +13-19%, -Cpb +106-132% at this rung). Mean
recirculation length reads differently: the 2D solve does not produce a short
bubble, it produces **no bubble at all**, while reversing instantaneously a
third of the time and the 3D reference holds a real, stable 1.40D structure.
That is a **qualitative difference in wake topology between two
dimensionalities of the same flow at the same Reynolds number**, not a
quantitative gap of the kind the other three metrics give — and it arrives
with a mechanism attached (amplitude asymmetry swamping a still-reversing
flow) and a located onset (between Re 2000 and Re 3900, not smeared across the
whole ladder). For a ladder whose entire purpose is attributing 2D/3D
deviation to dimensionality, this is stronger evidence than any of the three
percentage-based metrics, not a fourth row that happened to fail.

**Still open, and this is what the corrected-spacing twin (launched
2026-07-29 23:35:53Z, see below) exists to answer:** whether this onset is
genuine 2D-wake character at Re 3900, or a consequence of the near-wall
spacing deficit measured separately (§ below, L-17). The same reversal-
frequency and L_rec/D checks will be run on the twin the moment it lands, so
the comparison is apples-to-apples against all three of Re 1000/2000/3900.

**Docket, costed, not launched — sharpens the onset window.** A Re 2800 rung
(interpolated mesh ~35,700 cells, log-Re-interpolated between the 27,360-cell
Re 2000 and 44,000-cell Re 3900 meshes; laminar first-cell 0.002673 from this
ladder's own formula) would halve the current Re 2000-3900 onset window.
Predicted cost ~6,600 s (~1.83 h) on the Re 2000->3900 exponent (1.515,
see below — steeper than earlier rungs, so this estimate uses the locally
relevant exponent, not the stale 0.714 one). **Falsifiable prediction stated
before any run:** L_rec/D at Re 2800 is either (a) detectable and near
0.16-0.20D, supporting smooth extinction reaching zero around Re 3900, or (b)
already absent, placing the true onset below 2800. Parked behind the twin,
which is more informative to have first.

### `L_f`: the metric that survives where `Lr` doesn't (per `LITERATURE_REPRODUCTION_REVIEW.md` §5, Proposals 5-6)

`LITERATURE_REPRODUCTION_REVIEW.md` (a same-night, no-compute literature pass
run specifically against this finding) identifies the field-standard answer to
"what do you measure when the mean has no bubble": Gerrard (1966)'s formation
length `Lf`, built from the fluctuating field's own second moment rather than
the sign of the mean. Parnaudeau et al. (2008) — the same paper already cited
for this ladder's `Lr` reference — report their own centreline-based version,
`L<u'u'>` (distance to the peak of streamwise-velocity r.m.s. fluctuation on
the centreline), alongside `Lr` in the same Table II. That is directly
computable from the `probesCenterline` data already on disk (t>=45, all three
completed rungs), no new solve, and it depends only on the fluctuating field
— which the 34-39% reversal-frequency numbers above already prove is
well-resolved at Re 3900.

**Computed directly from raw probe series (population r.m.s. of Ux about its
own mean, per station, x of the peak):**

| rung | `Lf`/D (x of peak r.m.s.) | peak r.m.s. | max P(reversed) anywhere in range |
| --- | --- | --- | --- |
| Re 1000 | **0.350** | 0.301 | 48.1% |
| Re 2000 | **0.400** | 0.402 | 42.6% |
| Re 3900 | **0.400** | 0.528 | 38.7% |

**`Lf` is well-defined at all three rungs — clean, single-peaked profiles,
rising smoothly from the wall and decaying smoothly beyond the peak — exactly
where `Lr` stopped being definable at all.** And it does not collapse: 0.350
-> 0.400 -> 0.400, roughly flat to slightly growing, while `Lr` over the same
three rungs goes 0.397 -> 0.254 -> none. **This is the sharper statement of
the whole finding: the near wake does not stop having coherent structure at
Re 3900 — it stops having a structure the time-mean can see.** The shear
layers keep rolling up (peak r.m.s. itself grows monotonically, 0.301 -> 0.402
-> 0.528, consistent with the growing-amplitude mechanism already measured
above); what disappears is only the *sign-based* summary of that structure.

**Checked against the matching external reference, not left as a bare
number.** Parnaudeau et al.'s own `L<u'u'>/D` at Re 3900: **0.87 (PIV), 0.92
(HR LES)** (their Table II, read directly, same session as the `Lr` figures
already cited). Our measured 0.400 is **43-46% of their value** — a real,
disclosed, unresolved gap of the same directional character as every other
quantity this ladder has gated (2D running short/high relative to 3D), not
papered over just because the metric itself survived. **This is not the same
comparison as the Jiang & Cheng `Lf` mismatch corrected earlier in this
document** — Jiang & Cheng's `Lf` is Gerrard's original off-axis
double-shear-layer-peak definition, which needs off-centreline probe stations
this ladder never recorded; Parnaudeau's `L<u'u'>` is the centreline
single-peak version, definitionally closer to what is computed here, though
not proven numerically identical (both are legitimately called "formation
length" in the literature without a single universal normalisation).

**Proposal 6 (median-based `Lr_50`, `P(reversed)=0.5` crossing) — tested and
NOT validated; do not use it.** The proposal's own stated disproof condition
fired: at Re 1000 and Re 2000, where a clean mean bubble exists and `Lr_50`
was predicted to closely match the already-measured `Lr`, **reversal
probability never reaches 50% anywhere in the probed range at any of the
three rungs** (max 48.1%, 42.6%, 38.7% respectively) — `Lr_50` is undefined
at *every* rung, including the two where the ordinary mean-based `Lr` works
cleanly. The median-based metric does not reproduce the existing gate where
both should apply, so per the proposal's own falsification criterion it is
**not simply confirming `Lr`** and is not trusted at Re 3900 either. Recorded
as a genuine negative result, not silently dropped: reversal probability near
the base tops out somewhere in the high 30s to high 40s percent at every
rung tested, well short of a majority, even where a real mean bubble exists —
worth remembering as a general property of this wake rather than a
Re-3900-specific curiosity.

**Two honesty flags from the literature review, carried forward rather than
smoothed over:**

1. **This appears to be a genuinely novel observation.** No source the
   review could read states, as its own finding, that the 2D time-mean
   recirculation bubble disappears above some Reynolds number for the plain
   circular cylinder. The closest precedent (Singh & Mittal 2005, full 2D DNS
   from Re=100 to 10^7, sampling Re=3900 directly) is the right kind of study
   but its own streamline discussion skips exactly the Re=3900 panel that
   would confirm or refute this. Novel means unchecked by anyone else — the
   internal evidence (three rungs, two independent metrics, a growing-amplitude
   mechanism, a boundary-condition check, a probe-placement check) has to
   carry the weight a citation would otherwise share.
2. **One source is in direct tension with this finding and is not resolved.**
   Balachandar, Mittal & Najjar (1997, *JFM* 351:167-199) state, per their
   abstract (full text paywalled, confirmed via Unpaywall — `is_oa: false`),
   that a mean recirculation region is present in **all ten** of their cases
   spanning Re=250-140,000. If any of those ten is an unmodelled 2D case at a
   matched Re, it contradicts this finding directly. The abstract's own
   "span-averaged" language suggests the low-Re entries are 3D or
   turbulence-resolving data rather than a pure 2D-laminar configuration like
   this ladder's, but that cannot be confirmed without the full text. **Stated
   as an open, live tension — not resolved by the direction of the other
   evidence, and not hidden because the rest of the case reads cleanly.**

### The methodology trap bit a SECOND time — one layer deeper (found after the run finished)

The trap recorded above (case staged as kOmegaSST, reverted to laminar before
launch) was **only partly undone**. `constant/turbulenceProperties` and the
`0/` fields were reverted to the laminar convention — but **the mesh was not
rebuilt**, and the mesh had been generated with the *turbulent* first-cell
sizing:

| | first-cell height | formula |
| --- | --- | --- |
| Re 1000, Re 2000 (ladder convention) | — | `0.01*sqrt(200/Re)` (laminar branch) |
| **Re 3900 as actually run** | **0.0035167** | `estimate_first_cell(Re, y+=1)` — the **kOmegaSST branch** |
| Re 3900 laminar convention would be | 0.0022646 | `0.01*sqrt(200/3900)` |

The completed run's first cell is **55% coarser** than the ladder's laminar
convention. So this rung moved **two** variables against Re 1000/Re 2000 —
Reynolds number *and* near-wall spacing — which is precisely the
one-variable-at-a-time discipline the methodology-trap section claims to have
protected. Reverting a closure means reverting *everything the closure
influenced*, including mesh sizing; checking `turbulenceProperties` and `0/`
was not sufficient, and `case_preflight.sh` cannot catch this because a mesh
with the wrong spacing is still a valid mesh.

**A corrected-spacing rerun (`f5a_re3900_correctedspacing`, laminar first-cell
0.0022646, same 44,000 cells, grading 474.211 vs 280.383) was launched at
2026-07-29 23:35:53Z and is live as this is written.** Its result supersedes
the numbers above if they differ materially.

**This does not invalidate the measurements** — y+ was measured at max 1.53 /
avg 0.84, so the wall layer was genuinely resolved and the run is a valid
solve of the case it actually meshed. It means the *ladder comparison* (Re 1000
-> 2000 -> 3900 trend) has an uncontrolled second variable at the top rung, so
the trend rows below carry that caveat.

### Verdict: GATE REACHED (PROVISIONAL) as a model-deviation measurement — NOT as a solver validation

Four quantities were measured against a real six-source point table, and the
result is a large, directionally-consistent, single-mechanism deviation. That
is a genuine, reportable gate outcome and the ladder's most informative rung so
far.

**But it is weaker than the Re 1000 gate in a specific way that must not be
glossed:** at Re 1000 there were **2D DNS references** (Jiang & Cheng 2017,
Henderson 1997) that this solve matched to within a few percent on every
metric — that cross-check is what proved *the solver itself* was sound, letting
the 3D gap be attributed cleanly to dimensionality. **At Re 3900 all six
reference sources are 3D. No 2D-laminar cross-check exists at this rung**, so
this gate cannot separate "the 2D model is inadequate at Re 3900" (expected,
and almost certainly dominant) from "the solver has a Re-3900-specific problem"
(not expected, but not excluded either). Re 2000 was weak for lack of *any*
point reference; Re 3900 is weak for a different reason — an excellent point
reference that only exists for a different model class. Stated plainly rather
than presented as equal in strength to Re 1000.

A 2D-laminar Re=3900 reference is unlikely to exist in the literature (few
people publish a calculation they consider unphysical), so the honest closing
of this gap is the **3D rung**, not another paper search.

### Pre-registered prediction: FALSIFIED

The Re 2000 section recorded, before this rung's gate was computed (per P2):
that the St deviation would keep growing faster than the Cd deviation, "St_2D
keeps climbing past where St_3D has already plateaued, widening the
shedding-frequency gap faster than the drag gap as Re increases."

| rung | St deviation vs 3D | Cd deviation vs 3D |
| --- | --- | --- |
| Re 1000 | +8.5% to +11.6% | +35.9% to +44.8% |
| Re 2000 | +15% to +27% | +32% to +59% |
| **Re 3900** | **+13.3% to +18.7%** | **+53.9% to +108.9%** |

**The opposite happened.** The St gap did *not* keep widening — its band at Re
3900 sits inside Re 2000's and its midpoint fell (≈21% -> ≈16%). The Cd gap
widened sharply instead (≈45% -> ≈81% at the midpoint). The prediction was
wrong in its central claim, and is recorded as wrong rather than quietly
re-fit.

**Two caveats, stated so the falsification is not over-read:**

1. **Reference basis differs across rows.** Re 1000 was gated against a 2D+3D
   DNS set, Re 2000 against a *banded* regime description with no point source,
   and Re 3900 against a six-source 3D point table. The Re 2000 row carries the
   widest and least trustworthy interval.
2. **The Re 3900 row has the uncontrolled near-wall-spacing variable** described
   above, so part of its Cd growth could be spacing rather than Reynolds number.

The falsification is therefore solid on the *Cd* trend (which grew
unambiguously, by far more than either caveat could plausibly account for — a
36-point midpoint jump) and **provisional on the *St* trend** pending the
corrected-spacing rerun.

### Cost model outcome: prediction MISSED by +70.6%

The ladder predicted **~6,390 s** for this rung (posted at ~20:33 UTC with the
run ~1% complete, per P2), using the locally-fit Re 1000 -> Re 2000 exponent
0.714. **Actual: 10,902 s.** Error **+70.6%** — the run took nearly twice the
predicted time.

The report's own stated failure condition was met exactly: "If Re 3900 lands
far from 6,390 s, the locally-fit exponent is itself the thing that was wrong."
It was. Backing the exponent out of the measurements:

| interval | fitted exponent n (cost ~ Re^n) |
| --- | --- |
| Re 100 -> 1000 | 0.985 |
| Re 1000 -> 2000 | 0.714 |
| **Re 2000 -> 3900** | **1.515** |
| Re 1000 -> 3900 (overall) | 1.107 |

The exponent is **not monotonic and not stable** (0.985 -> 0.714 -> 1.515), so
*no* single-exponent power law describes this ladder's cost, and the previous
write-up's error was extrapolating from a two-point local fit at all — not
merely picking the wrong exponent value. **Recommendation for the remaining
rungs: quote cost predictions as a range spanning n=0.7 to n=1.6 rather than a
point estimate**, until enough rungs exist to characterize the curvature. On
that basis Re 5000 would be ~13,000-16,000 s (3.6-4.5 h) and Re 10,000
~21,000-49,000 s (5.9-13.7 h) — a spread wide enough that it should itself inform whether
the 2D ladder continues upward at all, given the model-adequacy finding above.

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
- **Cost scaling:** NOT a flat power law, and **not monotonic either** —
  updated after Re 3900. Exponent measured at 0.985 (Re 100->1000), 0.714 (Re
  1000->2000), **1.515 (Re 2000->3900)**. The "it is dropping" read recorded
  here before Re 3900 finished was wrong: the exponent dropped, then rose above
  both earlier values. The 6,390 s prediction built on that read missed by
  +70.6% (actual 10,902 s). Remaining rungs should be quoted as an n=0.7-1.6
  range, not a point estimate.
- **Steady vs unsteady:** the batch's steady cylinder family runs ~2.4 s per
  evaluation against ~394 s for the unsteady family at Re 100-1000 — a factor
  of roughly 164x, measured, and the dominant cost driver in the whole batch.
- **New this update — a staged case is not a validated case.** Inheriting a
  case directory that passes `case_preflight.sh` is not the same as inheriting
  a case that matches the ladder's established methodology. See the
  methodology-trap section above; the corresponding LESSONS.md entry is L-11.
- **New after Re 3900 — reverting a closure means reverting everything the
  closure sized.** L-11 was applied to `turbulenceProperties` and `0/` but not
  to the mesh, which kept the kOmegaSST y+~1 first-cell height (55% coarser
  than the laminar convention). `case_preflight.sh` structurally cannot catch
  this: a wrongly-sized mesh is still a valid mesh. The check that would have
  caught it is comparing the *staged* `stage_params.json` against the rung's
  own convention before launch, which costs nothing.
- **New after Re 3900 — the ladder's default averaging window is too
  generous.** "Second half" (t>=45) still carried 6.63% Cd drift at this rung,
  versus 0.50% from t>=54. Every rung's numbers should be reported with a
  window sweep, not a single window, and the window choice justified by its
  measured drift.

## Where the ladder goes next — reference availability decides it, and it says stop

**The next rungs' reference support was researched this session, before
committing compute** (the P3 "cheap check first" discipline). Result:

| rung | point reference available? | best source found | access |
| --- | --- | --- | --- |
| Re 5000 | **No** — nothing dedicated found | Williamson (1996) mentions Re=5,000 only in passing (Lin et al. 1995; Chyu & Rockwell 1995), qualitative, no numeric table | n/a |
| Re 10,000 | **Exists but unreachable** | Dong & Karniadakis (2005) *J. Fluids & Structures* 20(4):519-531, DOI 10.1016/j.jfluidstructs.2005.02.004; and Dong, Karniadakis, Ekmekci & Rockwell (2006) *JFM* 569:185-207, DOI 10.1017/S0022112006002606 (DNS+PIV at Re=3900/4000 **and** 10,000 — exactly the right paper) | **Paywalled**, confirmed via Unpaywall API on both DOIs (`is_oa: false`, no repository copy). Conference form (Dong, Lucor & Karniadakis 2004, DOI 10.1109/dod_ugc.2004.18) also closed. |
| Re 1000/3900 cross-check from one URANS solver | would have been ideal | Wang (2010) *J. Hydrodynamics* 22(2):221-228 — runs Re=1000, 3900 **and** 10,000 in one study | **Paywalled**, ScienceDirect fetch returned HTTP 403 |
| Re 10,000 (qualitative only) | yes | Williamson (1996) *Ann. Rev. Fluid Mech.* 28:477-539 — Re=10,000 sits in the "shear-layer transition regime" (Re 1,000-200,000): St gradually decreases, base suction increases with Re | **Open access**, full text read; but the St-Re curve is a figure, not a text-extractable number |

**Consequence:** Re 10,000 could only be gated as a **banded** rung (like Re
2000), not a point rung — despite the right paper existing — and Re 5000 could
not be gated at all on present access. That is a materially weaker gate than Re
3900's for **5.9-13.7 hours** of compute apiece.

**Recommendation: do not climb to Re 5000 or Re 10,000 next.** Two independent
reasons now point the same way, and they were established separately:

1. **Model adequacy (measured, this rung).** At Re 3900 the 2D laminar model
   has already lost the mean recirculation bubble entirely — a qualitative,
   not merely quantitative, failure. Going further up Re makes a model that is
   already qualitatively wrong more expensive, not more informative. The
   deviation would grow; nothing would be learned that this rung has not
   already shown.
2. **Reference availability (researched, this session).** The rung above buys a
   weaker gate than the rung just completed.

**The informative next step is the 3D rung, not a higher-Re 2D rung** — it is
the only thing that can close the one gap this gate could not: separating "2D
model inadequate" from "solver problem at Re 3900", since no 2D-laminar
reference exists at Re=3900 to cross-check against (and is unlikely to be
published by anyone, for the same reason this rung's result is a negative
one). A Re=1000 3D pilot is already live on this box, which is the right
sequencing — establish the 3D machinery at a rung where the 2D answer is
already validated against 2D DNS, before spending 3D money at Re 3900.

**A cheap, zero-compute alternative that would upgrade Re 10,000 to a point
gate:** institutional/library access to either Dong & Karniadakis paper. This
is the same P3 follow-up already logged against Re 2000 (Norberg 2003 /
Williamson 1996) and should be batched with it rather than pursued separately.
