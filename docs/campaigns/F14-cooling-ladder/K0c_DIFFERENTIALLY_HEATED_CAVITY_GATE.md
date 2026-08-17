# K0c. Differentially heated cavity validation gate

Campaign F14, gate K0c. Written 2026-08-17, zero compute spent, no solver launched.
This document is the F3-equivalent for thermal work: an exact published reference,
nowhere to hide. A later agent executes this gate without rereading the literature;
everything needed is here or in `reference-data/`.

> **Two references on this gate were NOT OBTAINED, and the rows they would grade
> cannot pass.** (1) The **laminar** core stratification reference: no tabulated
> core temperature gradient was obtained; de Vahl Davis 1983 and Le Quere 1991 are
> both paywalled (Section 1, end). (2) The **turbulent** Nusselt number reference:
> the database ships no Nusselt files and the paper is paywalled (Section 2.3).
> Acquisition paths are named at each place and summarised in the campaign README.
> An executing agent must not mark either row passed on a number it produced
> itself; with no reference there is nothing to compare against.

The gate has two rungs. The laminar rung is a **verification** rung against a
numerical benchmark of the de Vahl Davis lineage. The turbulent rung is a
**validation** rung against experiment, and it is the only rung on this gate that
can feed a trust tier above TREND ONLY, per the standing rule that no tier above
TREND ONLY exists without an experimental comparison.

Every citation below carries a provenance tier from the literature charter section 2.
Tier SECONDARY marks a number read in full in a paper that attributes it to a source
not read this session; the attribution chain is stated each time. No number in this
document was recalled from memory.

---

## 1. Laminar rung. De Vahl Davis square cavity, Ra 1e3 to 1e6

### 1.1 The reference and what was actually seen

The benchmark is:

> de Vahl Davis, G. (1983). Natural convection of air in a square cavity: a bench
> mark numerical solution. *International Journal for Numerical Methods in Fluids*,
> 3(3), pp. 249-264. DOI `10.1002/fld.1650030305`.

**Availability check, run 2026-08-17:** Unpaywall on `10.1002/fld.1650030305`
returned `is_oa: false`, no OA location. The full text was NOT read this session.
Tier for the paper itself: PAYWALLED, abstract-only. What the abstract literally
states (via the Wiley landing page and two full-text papers quoting it, below):
second-order central differences with mesh refinement and Richardson extrapolation,
solutions for 1e3 <= Ra <= 1e6, believed accurate to better than 1 percent at the
highest Rayleigh number and to about one tenth of that at the lowest.

Because the original tables were not seen, the exact internal table numbering of
the 1983 paper is **not asserted here**. The benchmark values are carried at tier
SECONDARY from three independent full-text reproductions, each read in full this
session, which agree with each other exactly where they overlap:

| Source (all tier READ IN FULL) | What it reproduces | Locator |
| --- | --- | --- |
| Han, Y. and Xie, X. (2019). Robust globally divergence-free weak Galerkin finite element methods for natural convection problems. arXiv:1903.09506v1 | Full de Vahl Davis row set (u1max, u2max, Nu_avg, Nu_max, Nu_min) at Ra 1e3 to 1e6, in the column headed Ref. [12], where [12] is the 1983 paper | Table 3, p. 30 |
| Gjesdal, T., Wasberg, C.E., Andreassen, O. (2003). Spectral element simulations of buoyancy-driven flow. arXiv:physics/0305049 | De Vahl Davis extrapolated Nu at Ra 1e4, 1e5, 1e6, plus Hortmann et al. (1990) values | Table 1, and Figs. 6-8 |
| Martineau, R.C. et al. (2009). Comparative Analysis of Natural Convection Flows... INL/EXT-09-15333, Idaho National Laboratory | Reference values at Ra 1e6: Nu_avg 8.8, Nu_max 17.925, Nu at y=0.5 8.799, Nu_min 0.989, attributed to the de Vahl Davis papers | Table 3, Section 4.3.1 |

Cross-checks that were actually performed: the three sources agree on Nu_avg at
every overlapping Ra (2.243, 4.519, 8.800); Gjesdal Table 1 and Han and Xie Table 3
carry Hortmann et al. (1990) extrapolated values (2.245, 4.522, 8.825) which sit
0.1 to 0.3 percent from the de Vahl Davis values, which calibrates the pass band
below. The velocity extrema appear in Han and Xie only among the read sources;
they are carried at tier SECONDARY, single reproduction, and get a wider band.

### 1.2 Case setup

| Item | Specification | Source and tier |
| --- | --- | --- |
| Geometry | Square cavity, side L, two dimensional | Gjesdal 2003, READ IN FULL |
| Fluid | Boussinesq fluid, Pr = 0.71, constant properties | Gjesdal 2003, READ IN FULL |
| Left wall (x=0) | Isothermal, T_hot | Gjesdal 2003, READ IN FULL |
| Right wall (x=L) | Isothermal, T_cold | Gjesdal 2003, READ IN FULL |
| Top and bottom walls | Adiabatic, zero heat flux | Gjesdal 2003, READ IN FULL |
| All walls | No slip | standard for this benchmark; Han and Xie 2019 solve with no-slip velocity, READ IN FULL |
| Gravity | Downward, negative y | Gjesdal 2003, READ IN FULL |
| Ra definition | Ra = g beta dT L^3 / (nu alpha) | Gjesdal 2003, READ IN FULL |
| Rungs | Ra = 1e3, 1e4, 1e5, 1e6, steady | Gjesdal 2003 (flow stationary at these Ra), READ IN FULL |
| Nondimensionalisation of velocity | u* = u L / alpha (values below are in these units) | Han and Xie 2019 use the standard scaling; the reproduced values match the de Vahl Davis magnitudes reproduced identically across decades of literature. If a solve produces values a constant factor off, check the velocity scale first |

### 1.3 Reference values

All rows below: tier SECONDARY, read in Han and Xie 2019, Table 3, p. 30, column
Ref. [12], attributed there to de Vahl Davis 1983. Nu_avg additionally corroborated
by Gjesdal 2003 Table 1 (Ra >= 1e4) and by INL/EXT-09-15333 Table 3 (Ra = 1e6).

| Ra | u1max (vertical mid-plane) | u2max (horizontal mid-plane) | Nu_avg | Nu_max (hot wall) | Nu_min (hot wall) |
| --- | --- | --- | --- | --- | --- |
| 1e3 | 3.649 | 3.697 | 1.118 | 1.505 | 0.692 |
| 1e4 | 16.178 | 19.617 | 2.243 | 3.528 | 0.586 |
| 1e5 | 34.81 | 68.22 | 4.519 | 7.717 | 0.729 |
| 1e6 | 64.63 | 219.36 | 8.800 | 17.925 | 0.989 |

Definitions: u1max is the maximum horizontal velocity on the vertical mid-plane
x = 0.5; u2max the maximum vertical velocity on the horizontal mid-plane y = 0.5;
Nu_avg the average Nusselt number; Nu_max and Nu_min the extrema of the local
Nusselt number on the hot wall (Han and Xie 2019, quantity definitions above their
Table 3, READ IN FULL).

Known drift in the reference at Ra = 1e6, recorded so the executing agent is not
surprised: INL/EXT-09-15333 (READ IN FULL) computed Nu_max = 17.54 to 17.59 with
two independent formulations agreeing with each other to better than 0.15 percent
while both sitting about 2 percent below the de Vahl Davis 17.925, and that report
attributes the gap to the 81x81 uniform-grid limit of the 1980-era benchmark at its
highest Ra. Hortmann et al. extrapolated Nu_avg at 1e6 is 8.825 against de Vahl
Davis 8.800 (Gjesdal 2003 Table 1, READ IN FULL). The bands below absorb this.

### 1.4 The gate

Deviation is REL(q) = 100 x |q_solve - q_ref| / |q_ref|, evaluated on the fine mesh
of a two-mesh pair (refinement factor >= 1.5 in each direction), with the coarse
mesh solved first and both values reported. A rung result is quoted only with both
mesh values next to it.

| Quantity | Ra | Pass band | Justification |
| --- | --- | --- | --- |
| Nu_avg | 1e3, 1e4, 1e5 | REL <= 1.0 percent | Reference self-declared accuracy 0.1 to 1 percent (abstract tier); later benchmarks sit within 0.3 percent of it (Gjesdal Table 1); band is about 3x that observed spread. Wrong-physics failures (missing buoyancy coupling, wrong Pr, wrong scale) miss by tens of percent |
| Nu_avg | 1e6 | REL <= 1.0 percent | The 8.800 vs 8.825 inter-benchmark gap is 0.28 percent; 1 percent still separates it cleanly from failure modes |
| Energy balance | all | |Nu_hot - Nu_cold| / Nu_avg <= 0.5 percent | With adiabatic horizontal walls the two wall averages must agree (INL/EXT-09-15333, Section 4.3.1, READ IN FULL); imbalance is a conservation defect independent of the reference |
| u1max, u2max | all | REL <= 2.0 percent | Single secondary reproduction, so the band is wider than for Nu; the quantity still catches gross momentum errors, which shift these values by much more |
| Nu_max, Nu_min | 1e3, 1e4, 1e5 | REL <= 2.0 percent | Wall-gradient extrema are the most mesh-sensitive entries in the table |
| Nu_max, Nu_min | 1e6 | REL <= 3.0 percent, and REPORT the value | Documented reference drift of about 2 percent at this Ra (Section 1.3); a 1 to 2 percent band here would fail correct solvers against an outdated extremum |

**Core stratification, laminar rung: reference NOT OBTAINED.** None of the three
full-text reproductions carries a tabulated core temperature gradient for this
case, and the two primary candidates that would (de Vahl Davis 1983; Le Quere, P.
(1991), Accurate solutions to the square thermally driven cavity at high Rayleigh
number, *Computers and Fluids* 20, pp. 29-41) are both paywalled. Availability
check run 2026-08-17: Unpaywall on `10.1016/0045-7930(91)90025-D` returned
`is_oa: false`. No number is invented here. The laminar rung therefore gates Nu
and the velocity extrema; the stratification half of the K0c mandate is carried by
the turbulent rung below, where primary data is in hand. To close the laminar
stratification gap: obtain either paper via the MIT access route
(`docs/research/MIT_ACCESS_DOCKET.md` pattern) and extend this table by addendum.

---

## 2. Turbulent rung. Betts and Bokhari enclosed tall cavity

### 2.1 The dataset, identified rather than assumed

The brief demanded a citable turbulent dataset be identified, not assumed. Two
candidates were checked:

| Candidate | What it offers | Availability, checked 2026-08-17 | Verdict |
| --- | --- | --- | --- |
| Ampofo, F. and Karayiannis, T.G. (2003). Experimental benchmark data for turbulent natural convection in an air filled square cavity. *Int. J. Heat and Mass Transfer* 46(19), from p. 3551. DOI `10.1016/S0017-9310(03)00147-9`. Square cavity 0.75 m, plates 50 and 10 C, Ra = 1.58e9 (abstract tier) | Local and average Nusselt numbers plus velocity and temperature profiles, at a Ra one decade above the Betts and Bokhari pair | Unpaywall: `is_oa: false`, no OA location. Companion papers Tian and Karayiannis (2000), DOI `10.1016/S0017-9310(99)00199-4`: also `is_oa: false` | The stronger square-cavity dataset on paper, but no number from it can be carried today. Route to MIT access; until then it earns no rung |
| Betts, P.L. and Bokhari, I.H. (2000). Experiments on turbulent natural convection in an enclosed tall cavity. *Int. J. Heat and Fluid Flow* 21, pp. 675-683 (citation as printed on the ERCOFTAC case page, READ IN FULL). Paper DOI `10.1016/S0142-727X(00)00033-3` | Mean and rms velocity and temperature profiles at nine heights, both Ra, plus measured top and bottom wall temperature profiles usable directly as boundary conditions | Paper: Unpaywall `is_oa: false`. **Data: fully open.** ERCOFTAC Classic Collection Case 079, archive `nctc-allfiles.zip` fetched 2026-08-17 from `cfd.mace.manchester.ac.uk/ercoftac/`, SHA-256 `4cd931c0c13a0ed5f898c39d94ea9f3b2ccd5dfc9cec75c00e37a818d7906dde`, 236 profile files | **Selected.** The gate is written against the primary data files, which are in `reference-data/betts_bokhari/` with the manifest |

So the answer to "does a citable turbulent dataset exist" is yes, and it is the
Betts and Bokhari ERCOFTAC Case 079 dataset; the better-known square-cavity
alternative exists but is closed, and that closure is recorded rather than papered
over.

### 2.2 Case setup

All rows sourced from the ERCOFTAC Case 079 description page, fetched and read in
full 2026-08-17 (tier READ IN FULL for the page; the page is the database's own
statement of the experiment).

| Item | Specification |
| --- | --- |
| Geometry | Tall rectangular cavity, 2.18 m high x 0.076 m wide x 0.52 m deep, aspect ratio H/W = 28.7 |
| Working fluid | Air |
| Driving | Vertical plates differentially heated; temperature differentials 19.6 C and 39.9 C |
| Rayleigh numbers | 0.86e6 and 1.43e6, based on cavity width |
| Regime | Core flow fully turbulent at both Ra; property variations comparatively small |
| Top and bottom walls | Partially conducting (fitted rubber walls); measured wall temperature profiles are provided as data files and are the boundary condition to impose (files `mt_rt_z0_*.dat`, `mt_rb_z0_*.dat` in `reference-data/betts_bokhari/`) |
| Two-dimensionality | Temperature and flow fields closely two dimensional except near front and back walls; flow antisymmetric across the cavity diagonal |
| Plate temperatures | Not stated on the database page. Extrapolating the measured mid-height profiles to the walls gives approximately 15.1 and 34.7 C (lo) and 16.1 and 56.0 C (hi), consistent with the stated differentials. Exact plate values are in the paywalled paper; a solve should impose the stated differentials and report the absolute levels used |
| Coordinates in data files | x in mm across the width (0 to 76), heights as y/H, z spanwise from mid-span |

### 2.3 Reference values

Rows marked DERIVED are computed from the named primary data files by
`compute_reference_metrics.py` in this directory; rerun it rather than trusting
this table. theta = (T - T_cold_plate)/dT. S = d theta / d(y/H), least squares over
the mid-width (x = 38 mm) temperatures at y/H = 0.30 to 0.70.

| Quantity | Ra = 0.86e6 | Ra = 1.43e6 | Source files |
| --- | --- | --- | --- |
| Core stratification S (DERIVED) | 0.016, fit rms residual 0.14 K, resolvable increment on S about 0.02 | 0.095, fit rms residual 0.30 K, resolvable increment on S about 0.02 | `mt_z0_{30,40,50,60,70}_{lo,hi}.dat` |
| Mid-height peak upward mean velocity (DERIVED) | +0.140 m/s at x = 71.2 mm | +0.190 m/s at x = 70.2 mm | `mv_z0_50_{lo,hi}.dat` |
| Mid-height peak downward mean velocity (DERIVED) | -0.135 m/s at x = 6.2 mm | -0.189 m/s at x = 5.0 mm | `mv_z0_50_{lo,hi}.dat` |
| Antisymmetry defect of the two peaks (DERIVED) | 3.6 percent | 0.5 percent | same |
| Peak rms vertical velocity fluctuation at mid-height (DERIVED) | 0.105 m/s at x = 33.2 mm | 0.138 m/s at x = 34.0 mm | `fvv_z0_50_{lo,hi}.dat` |
| Mid-width mean temperature at y/H = 0.30 / 0.50 / 0.70 (DERIVED) | 25.07 / 25.26 / 25.39 C | 34.58 / 34.74 / 36.02 C | `mt_z0_{30,50,70}_{lo,hi}.dat` |

At the lower Ra the fitted S (0.016) is below its own resolvable increment (0.02):
the core there is unstratified within what the data can resolve, and per L-28 no
solve may be graded on a difference below that increment. The gate row for S at lo
Ra is therefore a bound, not a target.

**Nusselt number, turbulent rung: reference NOT OBTAINED.** The database provides
no Nusselt files and the paper carrying the measured heat transfer is paywalled
(check above). The gate below is on velocity and stratification. To close: obtain
Betts and Bokhari (2000) full text, or derive wall heat flux from the near-wall
temperature files with the derivation and its increment stated by addendum.

### 2.4 The gate

Comparisons at mid-span (z = 0), against the named files, after demonstrating the
solve is statistically converged (for unsteady approaches, averaging long enough
that the reported metrics move by less than a fifth of their band).

| Quantity | Pass band | Justification |
| --- | --- | --- |
| Core stratification S, hi Ra | |S_solve - 0.095| <= 0.05 | Data-derived uncertainty on S is about 0.02 (fit residual); band is 2.5x that. The failure mode this hunts is the laminarised strongly stratified core (S of order 0.5 and larger) that under-resolved or mis-damped turbulence models produce; 0.05 separates the two regimes by an order of magnitude |
| Core stratification S, lo Ra | |S_solve| <= 0.07 | Reference indistinguishable from zero within 0.02; bound set at reference-plus-band from the hi-Ra reasoning |
| Mid-height peak velocities, both signs, both Ra | REL <= 15 percent on magnitude; peak location within 5 mm | The measured antisymmetry defect (up to 3.6 percent) bounds the data's internal consistency; 15 percent is about 4x that while still far inside the factor-level errors of a wrong near-wall treatment. Location band is 2x the local station spacing |
| Mid-width temperature at y/H = 0.30, 0.50, 0.70, both Ra | within 1.0 K (lo), 2.0 K (hi), about 5 percent of dT | Core temperature scatter between adjacent stations is 0.14 to 0.30 K rms; band is 3x to 7x that and still catches a mis-set wall boundary condition, which shifts the core by several K |
| Antisymmetry of the two mid-height peaks | defect <= 10 percent | The experiment achieves 0.5 to 3.6 percent; a solve violating antisymmetry grossly has a boundary-condition or convergence defect |

### 2.5 Trust tier

A solve passing every row of 2.4 on both A rungs is eligible for VALIDATED on this
case (experimental comparison, quantified deviation). Passing the laminar rung
(Section 1) alone supports verification claims only and caps at TREND ONLY. A solve
run against this document without the grid-sensitivity pair, or with any reference
row replaced by a remembered value, is not graded at all.

---

## 3. Claim, source, domain rows (charter section 3 format)

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| Nu_avg for the Boussinesq square cavity at Ra 1e3 to 1e6 is 1.118 / 2.243 / 4.519 / 8.800 | de Vahl Davis 1983 via Han and Xie 2019 Table 3 (SECONDARY, triple-corroborated for Nu); Gjesdal 2003 Table 1; INL/EXT-09-15333 Table 3 | 2D, Boussinesq, Pr = 0.71, adiabatic horizontal walls, steady, Ra <= 1e6 | Large temperature difference (non-Boussinesq) cavities; Vierendeels, Merci and Dick (WIT Transactions, Advances in Fluid Mechanics IV, 2002, Table 1, READ IN FULL) show Nu = 8.687 at Ra 1e6 with epsilon = 0.6, a 1.3 percent shift from Boussinesq at identical Ra. Also not applicable above Ra 1e6, nor to 3D cavities |
| de Vahl Davis extrema Nu_max at Ra 1e6 is about 2 percent high against modern solutions | INL/EXT-09-15333 Section 4.3.1 and Table 3 (READ IN FULL) | Grading Nu_max at Ra = 1e6 only | Nu_avg, which shows no such drift |
| Betts and Bokhari profiles are 2D at mid-span and antisymmetric across the diagonal | ERCOFTAC Case 079 page (READ IN FULL) | Mid-span comparisons at z = 0 | Near front and back walls; spanwise stations exist in the dataset to check this |
| The lo-Ra core stratification is indistinguishable from zero within S of 0.02 | DERIVED from primary data files, this directory | Gate row for S at Ra 0.86e6 | Any claim of a measured nonzero lo-Ra stratification below 0.02 |
