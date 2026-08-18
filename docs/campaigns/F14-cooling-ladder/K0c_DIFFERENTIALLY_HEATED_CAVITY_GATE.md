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

---

# Addendum A1, 2026-08-18. The turbulent-rung Nusselt reference was OBTAINED

**Nusselt number, turbulent rung: reference OBTAINED by addendum A1 dated
2026-08-18.**

This addendum is **append-only and supersedes nothing by deletion** (W-4).
Section 2.3 above still carries the sentence "Nusselt number, turbulent rung:
reference NOT OBTAINED", and it is **left standing and unedited** because it was
true when written on 2026-08-17 and because the specification's value is that it
can be diffed against its own commit. Everything above this line is as it was.
What changed is the world, not the record: the paper arrived.

## A1.1 What arrived, and how it was identified

Betts and Bokhari (2000) was recorded in Section 2.1 as `is_oa: false`,
paywalled, full text not seen. **On 2026-08-18 the full text arrived in the
repository and was read in full.** It was located **by content**, not by path -
a concurrent lane reorganised `docs/papers/` into topic subdirectories the same
day, so the path given in the dispatch no longer existed. Identification was on
the PII string carried in the PDF's own metadata:

| Field | Value |
| --- | --- |
| Path as found 2026-08-18 | `docs/papers/buoyant_natural_convection/betts_bokhari_2000_ijhff_21.pdf` |
| PDF metadata title | `PII: S0142-727X(00)00033-3` |
| SHA-256 | `905cce61e84bc485b086f9215277fd94bf823f3ffc12453084ab580423baeb94` |
| Pages | 9 (journal pp. 675-683) |
| Tier | **READ IN FULL**, 2026-08-18 |

That PII is the DOI `10.1016/S0142-727X(00)00033-3` named in Section 2.1. It is
the same paper, and the acquisition path Section 2.1 named is now closed.

## A1.2 The reference: Betts and Bokhari Table 1, p. 682

Table 1 is headed "Summary of mid-height results" and p. 683 records that it
"also contains derived results, such as average Nusselt number and an estimate of
eddy viscosity at the centre-line". Transcribed complete, both columns:

| Quantity | Lower Ra (0.86e6) | Higher Ra (1.43e6) |
| --- | ---: | ---: |
| Cold wall temperature (C) | 15.1 | 15.6 |
| Hot wall temperature (C) | 34.7 | 54.7 |
| Av. wall temp. gradient (C/m) | 1540 | 3900 |
| **Average Nusselt number** | **5.85** | **7.57** |
| Centre-line dT/dx (C/m) | 68 | 131 |
| Mid-cavity rms temperature (C), uncorrected | 0.92 | 1.48 |
| Max. vert. velocity (Av) (m/s) | 0.139 | 0.191 |
| Mid-cavity rms, v (m/s) | 0.10 | 0.134 |
| Mid-cavity dV/dx (1/s) | 4.8 | 5.1 |
| Mid-cavity rms u (m/s) | 0.053 | 0.077 |
| Mid-cavity u'v' (m2/s2 x 1e3) | 2.4-2.8 | 4.2-5.0 |
| nu_T/nu at centre-line | 35 | 55 |
| alpha_T/alpha at centre-line | 23 | 30 |

Air properties, same table:

| | 15.1 C | 34.7 C | 54.7 C |
| --- | ---: | ---: | ---: |
| Thermal conductivity (W/mK x 1e3) | 25.3 | 26.8 | 28.3 |
| beta (1/K x 1e3) | 3.47 | 3.25 | 3.05 |
| nu (m2/s x 1e6) | 14.6 | 16.5 | 18.4 |
| Prandtl number | 0.704 | 0.700 | 0.697 |

## A1.3 Stated experimental uncertainty on the Nusselt number

The paper states no uncertainty on Nu directly. It states one on the quantity Nu
is computed from, **p. 681**: after describing the fourth-order polynomial fit to
the near-wall temperature profile with "typical standard errors of 0.07 C", and
"taking into account also uncertainty in positional accuracy and thickness of the
thermocouple", it records that **"the wall temperature gradients from this
analysis are estimated to be accurate to +/-5%"**.

Nu is directly proportional to that gradient (A1.4), so **+/-5 % is the stated
experimental uncertainty on the reference Nusselt number**. It is the authors'
own number, not one constructed here.

Corroborating statements read in full:

| Statement | Page |
| --- | --- |
| Integration of the fluxes over the cavity height gives heat transfer 1.1 % (lo Ra) and 3.3 % (hi Ra) higher on the hot wall than the cold, "within the estimated experimental error", against 14.7 % in Dafa'Alla and Betts and 20 % in Ziai | 681 |
| Air-side wall temperatures vary +0.2/-0.4 C about the mean on the cold side and +/-0.2 C on the hot | 680 |
| Digital accuracy of the temperature chain about 0.1 C | 678 |
| Vibration effects on LDA under 0.1 mm/s | 679 |
| Correcting the temperature record for the 0.07 s response time raised rms temperature by only 4 % | 682 |

## A1.4 The Nusselt definition, checked rather than assumed

**The paper gives no formula for Nu.** The definition was recovered from p. 677,
where the rubber wall conductivity of 0.155 W/mK is described as "close to the
effective mean conductivity across the cavity under the turbulent conditions
(i.e. Nusselt number times molecular conductivity of air)". That fixes
`k_eff = Nu . k`, hence `Nu = q W / (k dT)`, hence for a wall gradient `g`,
`Nu = g W / dT`.

That reconstruction was **tested against Table 1's own numbers**, because a
definition inferred from a parenthetical is worth exactly as much as its check:

| rung | g W / dT from Table 1 | tabulated Nu | agreement |
| --- | ---: | ---: | ---: |
| hi Ra, using Table 1 wall temps (dT = 54.7 - 15.6 = 39.1 K) | 3900 x 0.076 / 39.1 = **7.581** | 7.57 | **+0.14 %** |
| lo Ra, using Table 1 wall temps (dT = 34.7 - 15.1 = 19.6 K) | 1540 x 0.076 / 19.6 = **5.971** | 5.85 | **+2.08 %** |

**The definition is confirmed at the higher Ra to 0.14 percent. At the lower Ra
the paper is internally inconsistent with itself by 2.08 percent** - Table 1's
tabulated Nu cannot be recovered from Table 1's own tabulated gradient and wall
temperatures. That inconsistency is recorded, not smoothed: it is carried into
the validation uncertainty in A1.5 as an additional component rather than
resolved in either direction, because nothing in the paper says which of the two
entries is the rounded one.

A second, smaller ambiguity, also carried: the **abstract** states temperature
differentials of 19.6 C and **39.9** C, while **Table 1's wall temperatures give
19.6 and 39.1** C. The 39.9 is what Section 2.2 above parsed and what the
executed rung imposed. The two differ by 2.0 %.

This definition is **commensurate with the one the executed rung used**
(`K0cT_RESULTS.md` Section 6: `Nu = |dT/dn|_wall . W / dT`). They are the same
formula. That is what makes the re-grade in `K0cT_NUSSELT_REGRADE.md` legitimate
rather than a comparison of two different quantities wearing one name.

## A1.5 Validation uncertainty on the re-grade

Combined in quadrature from three independent components, all measured:

| component | lo Ra | hi Ra | source |
| --- | ---: | ---: | --- |
| stated accuracy of the wall temperature gradient | 5.00 % | 5.00 % | Betts p. 681 |
| Table 1 internal inconsistency (A1.4) | 2.09 % | 2.00 % | DERIVED from Table 1 |
| grid, from the executed coarse/fine pair | 0.28 % | 0.49 % | `K0cT_RESULTS.md` Section 6 |
| **u_val** | **5.43 %** | **5.41 %** | quadrature sum |

## A1.6 Two further references this table supplies, which the gate did not have

**(a) The reference Nusselt for the tall cavity now exists, so the Section 2.4
gate can carry a Nusselt row.** The row and its verdict are in
`K0cT_NUSSELT_REGRADE.md`, filed as a new dated record rather than by editing
`K0cT_RESULTS.md` (W-4).

**(b) A measured turbulent Prandtl number at the cavity centre-line, DERIVED from
Table 1.** With `Prt = nu_T / alpha_T = (nu_T/nu) / (alpha_T/alpha) x Pr`:

| rung | nu_T/nu | alpha_T/alpha | Pr | **Prt measured** | solve used | error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| lo Ra 0.86e6 | 35 | 23 | 0.704 | **1.071** | 0.85 | **-21 %** |
| hi Ra 1.43e6 | 55 | 30 | 0.700 | **1.283** | 0.85 | **-34 %** |

**The executed rung's constant Prt of 0.85 was 21 to 34 percent below the value
measured at the centre-line of the very cavity it was solving,** and the measured
value is not constant between the two rungs - it rose by 20 percent when Ra rose
by 66 percent. This is the "constant turbulent Prandtl number strains" failure
mode named in the day order, and it is now a number rather than a suspicion. It
is quantified by experiment in `K0cS_RESULTS.md`, control C3.

**(c) A corroboration of the DERIVED velocity metrics in Section 2.3 above.**
Section 2.3 derived peak mid-height vertical velocities of +0.140 m/s (lo) and
+0.190 m/s (hi) from the ERCOFTAC primary data files. Betts Table 1 gives "Max.
vert. velocity (Av)" of **0.139 and 0.191 m/s**. The independently derived
numbers and the paper's own table agree to **0.7 % and 0.5 %**, which validates
`compute_reference_metrics.py` against a source it never read.

## A1.7 One thing this addendum does NOT close

Section 2.3's core stratification row is **not** superseded. Betts Table 1 gives
`Centre-line dT/dx` of 68 and 131 C/m, but **`x` is the horizontal coordinate**
(notation, p. 676: "x, y, z horizontal, vertical and depth-wise"), so that row is
the horizontal traverse gradient at mid-height and **not** the vertical
stratification `S` that Section 2.3 derives. No vertical stratification figure
appears in Table 1.

What the paper does add is a **qualitative corroboration**, p. 682: "A notable
feature of the present results is the lack of any thermal stratification over the
mid-height region of the cavity. The temperature on the vertical centre-line is
effectively constant from y/H = 0.3 to 0.7." That supports Section 2.3's finding
that the lo-Ra `S` of 0.016 is indistinguishable from zero. **It sits awkwardly
with the hi-Ra derived `S` of 0.095**, which is not zero; the paper's sentence
does not distinguish the two Rayleigh numbers and no reconciliation is asserted
here. The Section 2.4 gate rows on `S` stand unchanged.

## A1.8 The analyser guard was updated in the same change-set as this addendum

`K0cT_runs/analyse_k0ct.py` re-read the sentence "Nusselt number, turbulent rung:
reference NOT OBTAINED" out of Section 2.3 on every run and exited 2 if it had
been removed. **That guard was deliberate and correct and was not defeated.** The
sentence was not deleted; it still stands in Section 2.3.

The guard's **referent was moved to this addendum** in the same change-set that
created it: the analyser now requires the sentence at the head of A1 - "Nusselt
number, turbulent rung: reference OBTAINED by addendum A1 dated 2026-08-18" - and
**exits 2 if that is absent**, so the rung still cannot silently lose its
provenance. Deleting the addendum breaks the analyser exactly as deleting the
NOT OBTAINED statement used to.
