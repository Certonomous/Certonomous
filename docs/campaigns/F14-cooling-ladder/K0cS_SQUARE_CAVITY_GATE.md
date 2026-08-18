# K0cS. Turbulent square cavity validation gate (Ampofo and Karayiannis; Tian and Karayiannis)

Campaign F14, gate K0c, **square-cavity turbulent rung**, tag K0cS. Written
2026-08-18, before any solver was launched for it. This document was the
reference half of the rung; the prediction half was `K0cS_PREREGISTRATION.md`
and the executed half was `K0cS_RESULTS.md`.

## 0. Why this rung existed, and what changed on 2026-08-18

`K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` Section 2.1 evaluated two candidate
turbulent datasets on 2026-08-17 and recorded the square-cavity pair of Ampofo
and Karayiannis (2003) and Tian and Karayiannis (2000) as the **stronger dataset
on paper but closed**: Unpaywall returned `is_oa: false` on both DOIs, and the
ruling written that day was "no number from it can be carried today ... until
then it earns no rung."

On **2026-08-18 three primaries arrived in the repository** and were verified by
this agent before any number was carried out of them. The Section 2.1 ruling was
therefore **superseded for these two papers**, and this document is the rung the
2026-08-17 ruling said they had not yet earned. Section 2.1 itself was left
standing and unedited (W-4); it was correct on the day it was written.

### 0.1 Provenance of the three primaries, re-verified 2026-08-18

The day order gave paths that a concurrent reorganisation had already changed.
Each file was therefore located **by content**, not by path, and identified from
the DOI or PII string carried in its own PDF metadata rather than from its
filename.

| Paper | Path as found 2026-08-18 | Identifier in PDF metadata | SHA-256 | Pages |
| --- | --- | --- | --- | --- |
| Ampofo, F. and Karayiannis, T.G. (2003). Experimental benchmark data for turbulent natural convection in an air filled square cavity. *Int. J. Heat and Mass Transfer* 46, pp. 3551-3572 | `docs/papers/buoyant_natural_convection/ampofo_karayiannis_2003_ijhmt_46.pdf` | `doi:10.1016/S0017-9310(03)00147-9` | `c193d79e3eb8cba5d1fd6af085c3a8c4c9497df80f90292287282694ed64ffaf` | 22 |
| Tian, Y.S. and Karayiannis, T.G. (2000). Low turbulence natural convection in an air filled square cavity. Part I: the thermal and fluid flow fields. *Int. J. Heat and Mass Transfer* 43, pp. 849-866 | `docs/papers/buoyant_natural_convection/tian_karayiannis_2000_ijhmt_43.pdf` | `PII: S0017-9310(99)00199-4` | `aa10b2855bc3785e8dffb2f9bc25de0f25fcde955a2ac34cbe6354060d2b9b79` | 18 |
| Betts, P.L. and Bokhari, I.H. (2000). Experiments on turbulent natural convection in an enclosed tall cavity. *Int. J. Heat and Fluid Flow* 21, pp. 675-683 | `docs/papers/buoyant_natural_convection/betts_bokhari_2000_ijhff_21.pdf` | `PII: S0142-727X(00)00033-3` | `905cce61e84bc485b086f9215277fd94bf823f3ffc12453084ab580423baeb94` | 9 |

The three DOI and PII strings matched the three citations the day order named.
Tier for all three: **READ IN FULL** this session. Every number below carries the
**journal page** it was read from. No number below was recalled, and no number
below was digitized from a figure.

**Betts and Bokhari does not grade this rung.** It is listed here only because
its arrival was verified in the same pass; it grades the *tall*-cavity rung and
its extraction is in Section 4 of `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`
(addendum A1) and in `K0cT_NUSSELT_REGRADE.md`.

### 0.2 What was NOT obtained, stated before the reference tables rather than after

- **Tian and Karayiannis (2000) Part II**, "Low turbulence natural convection in
  an air filled square cavity Part II: the turbulence quantities", was **NOT
  OBTAINED**. Its existence was confirmed from the Part I reference list (p. 866)
  and from Part I p. 863, which deferred the Reynolds-stress and turbulent-heat-
  flux fields to it. **Every corroborating value for a turbulence statistic is
  therefore single-source in this document** (Ampofo Table 2 only), and every such
  row is marked SINGLE SOURCE and carries a wider band for that reason. No
  turbulence statistic was cross-checked between two experiments on this rung, and
  no row was invented to cover the gap.
- **The turbulent Prandtl number in the square cavity was NOT OBTAINED.** Neither
  paper reported an eddy diffusivity or an eddy viscosity for this cavity. (The
  *tall* cavity does carry both; see the addendum named above.) The Prt used in
  the solves was therefore a modelling choice with no square-cavity anchor, and it
  was registered as such rather than gated.
- **No uncertainty on the stratification parameter was stated by either paper.**
  Tian p. 862 gave `Sp = 0.50` with no error bar and no fitting window. The band
  in Section 3 was therefore constructed from the *observed window sensitivity of
  the primary table*, which is derived and stated, not from an author's estimate.

---

## 1. The case, as the two papers specified it

Both papers reported the **same physical rig** (Ampofo p. 3554 stated the cavity
and confirmed that the two-dimensionality had been "thoroughly examined and
verified by the earlier work of Tian and Karayiannis"; Tian p. 852 gave the same
dimensions and the same plate temperatures). That is what makes the pair a
reproducibility measurement rather than two unrelated datasets, and Section 3
uses it as one.

| Item | Specification | Source |
| --- | --- | --- |
| Geometry | 0.75 m high x 0.75 m wide x 1.5 m deep; horizontal aspect ratio ARz = 2 | Ampofo p. 3554; Tian p. 852 |
| Dimensionality | 2D at the mid-plane. Ampofo p. 3554 recorded that profiles at three depths (Z = 0, 0.533, 0.8) differed by 4 percent on peak velocity and 0.5 mm on its position | Ampofo p. 3554 |
| Hot wall (x = 0) | Isothermal, 50 +/- 0.15 C, 6 mm mild steel | Ampofo p. 3554; Tian p. 852 |
| Cold wall (x = L) | Isothermal, 10 +/- 0.15 C, 6 mm mild steel | Ampofo p. 3554; Tian p. 852 |
| Top and bottom walls | 1.5 mm mild steel sheet, **highly conducting**. NOT adiabatic and NOT perfectly conducting: the measured profiles are tabulated and were imposed directly (Section 2.3) | Ampofo p. 3554; Tian p. 852 |
| Rayleigh number | Ra = 1.58e9, based on cavity side L and dT = 40 K | Ampofo p. 3554; Tian p. 852 |
| Ambient | 30 +/- 0.2 C, set equal to the cavity mean temperature; two guard cavities on the passive vertical walls | Ampofo p. 3554; Tian p. 852 |
| Velocity scale | V0 = sqrt(g beta H dT) = 1 m/s. **Table 2 velocities are normalised by this and it is exactly 1 m/s**, so tabulated values are also m/s | Ampofo p. 3557 (Table 2 footnote); Tian p. 855 |
| Coordinates | X = x/L measured **from the hot wall**; Y = y/L from the bottom | Ampofo Tables 2-6 headers, pp. 3556-3559 |
| Nusselt definition | Nu_local = L/(Th - Tc) . |dT/dxi|_wall, evaluated in the conductive layer by linear best fit over the first 6-9 measuring points | Ampofo Eq. (15), p. 3564; identical to Tian Eq. (1), p. 859 (5-9 points) |
| Stratification definition | Sp = L/(Th - Tc) . dT/dy at x/L = 0.5, y/L = 0.5 | Tian Eq. (4), p. 862 |

**Boussinesq admissibility, recorded because it fails the lab's own line.**
beta.dT at T_mean = 303.15 K is 3.2987e-03 x 40 = **0.132**, which is above the
0.1 line in `docs/physics_rules.yaml`. Ampofo p. 3564 independently measured the
consequence: "the 40 K temperature difference causes about 11 percent density
difference in the cavity". Two solver-side consequences followed and were
registered in `K0cS_PREREGISTRATION.md` before the run rather than discovered
after it: a Boussinesq solve cannot reproduce the measured hot/cold asymmetry,
and it cannot reproduce the measured centre-point temperature offset. Both were
therefore **reported and not gated** (Section 3.4).

---

## 2. Reference values, with the page each was read from

### 2.1 Stated experimental uncertainty

This is the half of an extraction that decides whether a band is honest, so it is
first rather than last.

**Ampofo and Karayiannis, Table 1, p. 3555** ("Summary of uncertainties in the
measured and estimated parameters"), transcribed complete:

| Parameter | Degree of uncertainty |
| --- | --- |
| Wall temperature | 0.15 K |
| Air temperature | 0.10 K |
| Air velocity | 0.07 % |
| Reynolds stress | 0.10 % |
| Turbulent heat flux | 0.15 % |
| Rayleigh number | 0.62 % |
| **Nusselt number** | **0.25-1.13 %** |
| Wall shear stress | 1.38 % |

Supporting statements read in the same paper:

| Statement | Page |
| --- | --- |
| Repeatability: maximum deviation between readings from experiments performed at different times was 0.5 K for temperature and 2 mm/s for velocity | p. 3555 |
| Energy balance over the whole cavity: 98.12 W in at the hot wall and 21.67 W in at the bottom; 97.77 W out at the cold wall and 22.53 W out at the top; **percentage error of heat input and output less than 0.5 %** | p. 3555 |
| Sample count 10 000 per point, chosen because uncertainty of a statistical value becomes less than 5 % above 5000 samples | p. 3555 |
| Thermocouple 25.4 um E-type, accuracy 0.1 K, traverse accurate to 0.1 mm | p. 3554 |
| LDA probe volume 0.31 mm diameter x 9.8 mm; measured range -0.5082 to +0.5082 m/s, resolution 6.20e-5 m/s | pp. 3554-3555 |

**Tian and Karayiannis, p. 852**, transcribed complete: "The error in the Ra was
1.515e6 or 0.6%. The error in the Nu was **0.2133** and in the wall stress 1.5%."
Also p. 852: wall plates isothermal at 50 +/- 0.15 and 10 +/- 0.15 C; temperature
reading true within 0.1 K; thermocouple location better than 0.2 mm; repeatability
0.5 K and 2 mm/s.

The Tian Nusselt error is quoted **as an absolute**, not a percentage; against
that paper's own average Nu of 64.0 it is 0.33 %.

**The stated uncertainties were not used as the pass bands, and Section 3.1 gives
the measured reason.**

### 2.2 Integral heat transfer

| Quantity | Ampofo | page | Tian | page | spread |
| --- | ---: | --- | ---: | --- | ---: |
| Average Nu, hot wall | 62.9 | 3564 | 64.0 | 859, 861 | 1.7 % |
| Average Nu, cold wall | 62.6 | 3564 | 65.3 | 859, 861 | 4.3 % |
| Average Nu, bottom wall | 13.9 | 3564 | 14.97 | 860 | 7.7 % |
| Average Nu, top wall | 14.4 | 3564 | 15.67 | 860 | 8.8 % |
| Local Nu at mid-height, hot wall | 58 (Table 6) / "about 59" (text) | 3559 / 3564 | 59.5 | 861 | 2.6 % |
| Local Nu at mid-height, cold wall | 60 (Table 6) | 3559 | 57.1 | 861 | 5.1 % |
| Maximum local Nu | 136 at Y = 0.02 (Table 6) / "about 138" (text) | 3559 / 3564 | "about 135" | 859 | 2.2 % |
| Minimum local Nu on hot wall | 17 at Y = 0.9867 (Table 6) / "about 20" (text) | 3559 / 3564 | "drops to 17" | 859 | - |
| Hot/cold average Nu closure | 0.5 % (62.9 vs 62.6) | 3564 | "less than 2 %" (64.0 vs 65.3) | 859 | - |

Two correlations were also read, and are carried as context rather than as
reference values because neither is a measurement of this cavity: Tian p. 862
quoted Lankhorst `Nu = 0.241 Ra^0.260`, giving 59.38 at Ra 1.58e9, and Fusegi et
al. `Nu = 0.163 Ra^0.282`, giving 64.0.

Third-party comparison values recorded by Tian p. 861 for the same quantity, at
tier SECONDARY and **not used as reference**: Mergui et al. gave 47.6 and 53.6
(hot, cold) at Ra 1.34e9; Beghein et al. gave 63.86 (adiabatic horizontal walls)
and 55.59 (perfectly conducting). The last pair is the reason this rung imposed
the measured horizontal-wall profiles rather than either ideal: the two idealised
boundary conditions differ from each other by 13 % on average Nu, which is larger
than every band in Section 3.

### 2.3 Boundary condition data actually imposed

**Ampofo Table 4, p. 3558**, "Mean temperature distribution on horizontal walls",
theta = (T - Tc)/dT against X = x/L, dT = 40 K. Transcribed complete and imposed
as a piecewise-linear wall temperature on both horizontal walls:

| X | Top wall | Bottom wall | | X | Top wall | Bottom wall |
| ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 0.0000 | 1.0000 | 1.0000 | | 0.4000 | 0.6779 | 0.3960 |
| 2.0000e-3 | 0.9490 | 0.9184 | | 0.5000 | 0.6393 | 0.3503 |
| 6.6700e-3 | 0.9333 | 0.9038 | | 0.6000 | 0.6135 | 0.3116 |
| 0.0133 | 0.9342 | 0.8862 | | 0.7000 | 0.5578 | 0.2722 |
| 0.0267 | 0.9183 | 0.8639 | | 0.8000 | 0.4880 | 0.2214 |
| 0.0533 | 0.8782 | 0.7733 | | 0.9000 | 0.3372 | 0.1490 |
| 0.1000 | 0.8210 | 0.6608 | | 0.9467 | 0.2338 | 0.0938 |
| 0.2000 | 0.7597 | 0.5263 | | 0.9733 | 0.1409 | 0.0445 |
| 0.3000 | 0.7107 | 0.4520 | | 0.9867 | 0.1334 | 0.0352 |
| | | | | 0.9933 | 0.1234 | 0.0272 |
| | | | | 0.9980 | 0.0967 | 0.0185 |
| | | | | 1.0000 | 0.0000 | 0.0000 |

This is the **measured** boundary condition and it removed the adiabatic-versus-
perfectly-conducting ambiguity that Section 2.2 recorded as a 13 % effect. The
two profiles were not antisymmetric to each other: at X = 0.5 the top carried
0.6393 while `1 - bottom(0.5)` was 0.6497, a defect of 0.0104 in theta (0.42 K).
That defect was carried into the solve rather than smoothed, and it is the reason
the centre-point temperature row in Section 3.4 is **near**-identity rather than
identity.

### 2.4 Mid-height profiles and their extrema

**Ampofo Table 2, pp. 3556-3557**, "Experimental results at Y = 0.5 in the
cavity", 62 stations from X = 0 to X = 1, eleven columns
(v, u, v'rms, u'rms, (T-Tc)/dT, T'rms/dT, u'v', v'T', u'T', k), all normalised by
V0 = 1 m/s and dT = 40 K. The full table was parsed mechanically rather than
transcribed by eye, and the extrema below were computed from that parse:

| Quantity | Value | at X | Tier |
| --- | ---: | ---: | --- |
| Peak upward vertical velocity, mid-height | +0.2127 m/s | 0.00667 (5.0 mm from hot wall) | READ IN FULL, Table 2 |
| Peak downward vertical velocity, mid-height | -0.2185 m/s | 0.99070 (7.0 mm from cold wall) | READ IN FULL, Table 2 |
| Antisymmetry defect of the two peaks | 2.7 % | - | DERIVED from the two above |
| Peak rms vertical velocity, mid-height | 0.0717 m/s | 0.01330 | READ IN FULL, Table 2, **SINGLE SOURCE** |
| Peak rms horizontal velocity, mid-height | 0.0343 m/s | 0.03330 | READ IN FULL, Table 2, **SINGLE SOURCE** |
| Peak rms temperature, mid-height | 0.0753 x 40 K = 3.01 K | 0.00667 | READ IN FULL, Table 2, **SINGLE SOURCE** |
| Peak turbulence kinetic energy, mid-height | 4.45e-3 m2/s2 | 0.01330 | READ IN FULL, Table 2, **SINGLE SOURCE, and carrying a modelling assumption** |
| theta at cavity centre (X = 0.5, Y = 0.5) | 0.5174 | 0.5 | READ IN FULL, Table 2 and Table 5 |

Corroboration where it existed: Ampofo p. 3559 stated the mid-height velocity
peak at "X = 0.007 (5 mm)", which matched the parsed X = 0.00667. Ampofo p. 3564
stated the peak Reynolds stress as 1.08e-3 and 0.99e-3 m2/s2 near the hot and
cold walls at about X = 0.033, which matched the Table 2 column. Tian p. 861
gave theta at the cavity centre as 0.514 against Ampofo's 0.5174, a 0.66 %
spread; Tian p. 855 gave a peak vertical velocity of **0.225 m/s** but at
Y = 0.4, not at mid-height, so it corroborates the magnitude and **not** the
mid-height row.

**The turbulence kinetic energy row carries an assumption made inside the
experiment, and it is not the solver's.** Ampofo measured only u' and v'.
Equations (4) and (5), p. 3554, estimated the third component as
`w'^2 = (u'^2 + v'^2)/2` and hence `k = 1.5(u'^2 + v'^2)/2`, citing Kreplin and
Eckelmann and Spalart for the ordering `u'^2 <= w'^2 <= v'^2` and stating
directly that "it is very difficult to estimate w' without direct measurements".
Comparing a two-equation model's k against that number would compare two
assumptions, so **k is reported and not gated** (Section 3.4).

### 2.5 Mid-width temperature and the stratification parameter

**Ampofo Table 5, p. 3558**, "Mean temperature distribution along mid-width", 41
stations, theta against Y at X = 0.5. Values used in Section 3 (full table in the
PDF; the analyser re-parses it rather than trusting this excerpt):

| Y | 0.2000 | 0.3000 | 0.4000 | 0.4500 | 0.5000 | 0.5500 | 0.6000 | 0.7000 | 0.8000 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| theta | 0.3804 | 0.4213 | 0.4564 | 0.4854 | 0.5174 | 0.5463 | 0.5662 | 0.6068 | 0.6356 |

**Tian p. 862** reported `Sp = 0.50` "by polynomial fitting", **without stating
the fitting window**, and recorded three further values in the same paragraph:
Ziai 0.51, Mergui et al. 0.37, and a numerical range of 0.490 to 0.901 across the
Eurotherm Seminar 22 contributions with the 50 % agreement band at 0.511-0.572
and an average of 0.539. Tian's own sentence: "Generally, the numerical modelling
results predicated a higher value of Sp than the experimental results."

**The window sensitivity was measured rather than assumed**, because Tian did not
state one. Least squares on the Ampofo Table 5 stations:

| Window in Y | Sp | stations | fit rms |
| --- | ---: | ---: | ---: |
| 0.45 to 0.55 | 0.6090 | 3 | 0.029 K |
| 0.40 to 0.60 | 0.5610 | 5 | 0.122 K |
| **0.30 to 0.70** | **0.4813** | **9** | **0.219 K** |
| 0.20 to 0.80 | 0.4496 | 13 | 0.266 K |

**The choice of window moves Sp by 0.16, which is larger than any model-to-model
difference this rung could hope to resolve.** That is the dominant uncertainty on
this quantity and it is a property of the definition, not of the instrument. The
window was therefore **fixed at Y = 0.30 to 0.70, least squares**, matching the
window `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` Section 2.3 already used for
the tall cavity, so that the two rungs of this campaign measure the same thing.
On that window the reference was **Sp = 0.481** (Ampofo Table 5) with Tian's
0.50 sitting 3.9 % away, inside the window spread.

The resolvable increment from the instrument alone was far smaller: air
temperature accuracy 0.10 K (Table 1, p. 3555) over a window of 0.4 in Y gives
dSp = 0.0125. **The instrument was not the limit on this quantity; the definition
was.**

### 2.6 Local distributions

**Ampofo Table 6, p. 3559**, "Local Nusselt number distribution along the walls",
transcribed complete:

| Y | Nu hot | Nu cold | | X | Nu bottom | Nu top |
| ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 0.0200 | 136 | 21 | | 0.0133 | 75 | 22 |
| 0.0493 | 122 | 33 | | 0.0400 | 58 | 18 |
| 0.1000 | 95 | 42 | | 0.0800 | 40 | 8 |
| 0.2000 | 84 | 44 | | 0.1333 | 38 | 5 |
| 0.3000 | 72 | 47 | | 0.2000 | 36 | 2 |
| 0.4000 | 65 | 50 | | 0.2800 | 20 | -4 |
| 0.5000 | 58 | 60 | | 0.3600 | 16 | -8 |
| 0.6000 | 52 | 62 | | 0.5000 | 10 | -11 |
| 0.7000 | 47 | 69 | | 0.6400 | 8 | -18 |
| 0.8000 | 40 | 80 | | 0.7200 | 4 | -23 |
| 0.9000 | 36 | 87 | | 0.8000 | 1 | -31 |
| 0.9493 | 28 | 122 | | 0.8667 | -12 | -35 |
| 0.9867 | 17 | 138 | | 0.9200 | -15 | -42 |
| | | | | 0.9600 | -19 | -55 |
| | | | | 0.9867 | -25 | -70 |

The horizontal-wall Nusselt **changes sign**, which is a structural feature of
the conducting-wall boundary condition rather than noise: heat entered the cavity
over the hot end of the bottom wall and left it over the cold end. Tian p. 859
located the sign change at x/L = 0.825 on the bottom and 0.175 on the top; the
Ampofo table above crosses between X = 0.8000 and 0.8667 on the bottom and
between 0.2000 and 0.2800 on the top. **The two experiments disagreed on the
bottom-wall crossing location by about 0.03 in X and agreed on the top to within
0.03.** Because the bottom and top average Nu are small differences of large
signed contributions, they are the least reproducible integral quantities in
Section 2.2 (7.7 % and 8.8 % spread), and Section 3 bands them accordingly.

**Ampofo Table 3, p. 3558**, "Wall shear stress":

| Quantity | Value | Location |
| --- | ---: | --- |
| Peak wall shear stress, hot wall | 1.66e-3 N/m2 | Y = 0.4 |
| Peak wall shear stress, cold wall | 1.76e-3 N/m2 | Y = 0.6 (0.4 from the cold wall's leading edge) |
| Antisymmetry defect of the two peaks | 5.9 % | DERIVED |

The pairing was read from the two column headers, which ran the hot column as
distance from the bottom wall and the cold column as distance from the top wall,
so that equal rows carried equal distance travelled along each plate. That
reading was corroborated by Tian p. 855, which put the minimum boundary-layer
thickness "at about Y = 0.4 at the hot wall and Y = 0.6 at the cold wall" -
the same antisymmetric pairing.

### 2.7 Boundary-layer structure, used to size the mesh rather than to grade

| Statement | Value | Page |
| --- | --- | --- |
| Inner layer width at Y = 0.5 | 5 mm (X = 0.0067) | Ampofo 3559 |
| Outer layer width at Y = 0.5 | 75 mm (X = 0.1) | Ampofo 3559 |
| Viscous layer | about 3 mm | Ampofo 3559 |
| Conductive layer (linear T, constant flux) | about 2 mm | Ampofo 3559 |
| Inner layer thickness variation along the wall | 4 to 7 mm | Ampofo 3559 |
| Reynolds stress zero over | first 3 mm from the wall | Ampofo 3564 |

The 2 mm conductive layer set the near-wall mesh requirement in
`K0cS_PREREGISTRATION.md`: a solve that puts fewer than a handful of cells inside
2 mm cannot reproduce the wall gradient that **defines** the reference Nusselt
number, and would fail the gate for a mesh reason wearing a turbulence-model
label.

---

## 3. The gate

Deviation is REL(q) = 100 x |q_solve - q_ref| / |q_ref|, taken on the **fine mesh
of a two-mesh pair** with the coarse solved alongside and both values reported.
Per `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` Section 2.5, a solve presented
without its grid-sensitivity pair is **not graded at all**; that rule was carried
unchanged onto this rung and it is the rule under which one case in
`K0cS_RESULTS.md` is reported rather than graded.

### 3.1 Why the bands are not the papers' stated uncertainties

Ampofo's stated Nusselt uncertainty was 0.25-1.13 % and Tian's was 0.33 %. **The
two experiments, in the same rig, on the same nominal case, disagreed with each
other by up to 8.8 %** (Section 2.2). The disagreement exceeds the larger of the
two stated uncertainties by a factor of about eight.

A band set at the stated instrument uncertainty would therefore fail a solve that
sat exactly on one of the two published measurements, which is not a defensible
gate. **The reproducibility spread between the two independent experiments is the
honest uncertainty on this case, and the bands below are built from it.** Where
the two disagree, the reference is their mean and the disagreement is printed
next to it, so a reader can see the reference's own width without recomputing it.

This is a measured statement, not a stylistic preference: the numbers behind it
are the six spread values in the last column of Section 2.2.

### 3.2 Graded rows

| # | Quantity | Reference | Its own spread | Pass band | Justification |
| --- | --- | ---: | ---: | --- | --- |
| G1 | Average Nu, hot wall | 63.45 (mean of 62.9, 64.0) | 1.7 % | REL <= 10 % | About 2.3x the worst vertical-wall reproducibility spread (4.3 %, row G2). Catches the classic failure modes, which move Nu by tens of percent |
| G2 | Average Nu, cold wall | 63.95 (mean of 62.6, 65.3) | 4.3 % | REL <= 10 % | Same band as G1 so the two walls are graded alike; the band is 2.3x this row's own spread |
| G3 | Average Nu, bottom wall | 14.44 (mean of 13.9, 14.97) | 7.7 % | REL <= 20 % | 2.3x this row's spread, held to the same multiplier as G1/G2 rather than chosen. These are small differences of large signed contributions (Section 2.6) |
| G4 | Average Nu, top wall | 15.04 (mean of 14.4, 15.67) | 8.8 % | REL <= 20 % | As G3 |
| G5 | Local Nu at mid-height, hot wall | 58.75 (mean of 58, 59.5) | 2.6 % | REL <= 12 % | Slightly wider than G1 because the solve value is read at a single station rather than integrated, so it carries mesh noise the integral does not |
| G6 | Maximum local Nu on the hot wall | 136.5 (mean of 138, 135) | 2.2 % | REL <= 20 % | The most mesh-sensitive entry on the gate: it sits at Y = 0.02 where the thermal layer is thinnest. Same reasoning that widened Nu_max on the laminar rung of the parent gate |
| G7 | Stratification parameter Sp, Y = 0.30-0.70 LSQ | 0.481 (Ampofo Table 5; Tian 0.50 at 3.9 %) | window sensitivity 0.16 | absolute, \|Sp_solve - 0.481\| <= 0.12 | 0.75x the measured window spread (Section 2.5), so the definition's own ambiguity cannot decide the verdict. Still separates the experimental cluster (0.45-0.61) from the laminarised over-stratified core that Tian p. 862 recorded numerical contributions reaching (0.901) |
| G8 | Peak mid-height vertical velocity, magnitude | 0.2127 m/s | 2.7 % antisymmetry defect | REL <= 15 % | About 4x the experiment's own antisymmetry defect and about 4x the 4 % depth-to-depth spread Ampofo recorded on p. 3554 |
| G9 | Peak mid-height vertical velocity, location | X = 0.00667 | - | within 0.005 in X (3.75 mm) | 7.5x the 0.5 mm depth-to-depth position spread (Ampofo p. 3554), and still inside the 5 mm inner layer, so a solve that puts the peak outside the inner layer fails |
| G10 | Peak Reynolds shear stress \|u'v'\| at mid-height, hot-wall side | 1.08e-3 m2/s2 | 8 % (hot vs cold wall) | REL <= 40 % | See the amendment note below: this row replaced a peak-rms-velocity row that a two-equation model cannot answer. Band is 5x the experiment's own hot/cold asymmetry (Ampofo p. 3564) and single-source, because Tian Part II was NOT OBTAINED |

**Amendment, 2026-08-18, recorded before any graded case was launched and left
visible rather than folded in.** Row G10 was first written as *peak rms vertical
velocity at mid-height, reference 0.0717 m/s, band 30 %*. **That row was not
answerable by any of the three models on this rung and it was withdrawn before
compute rather than after.** The reason, stated plainly because a row removed
without its reason reads later as a row that passed:

- **A two-equation eddy-viscosity model does not predict v'rms.** kOmegaSST,
  kEpsilon and LaunderSharmaKE each carry one scalar for the whole Reynolds
  stress tensor's trace. Recovering a *component* from k requires assuming
  isotropy, `v'rms = sqrt(2k/3)`.
- **That assumption is known false on this exact case, and the primary says so.**
  Ampofo p. 3559 measured `u'rms` at less than half `v'rms` in the boundary layer
  at mid-height. Grading a solve through an isotropy assumption the experiment
  had already refuted would have graded the assumption, not the model, and every
  model would have failed it for the same reason.
- **What replaced it is the model's own constitutive output.** An eddy-viscosity
  model predicts `u'v' = -nu_t . dv/dx` directly, with no additional assumption on
  the solve side, and Ampofo measured `u'v'` directly (p. 3564, and the `u'v'`
  column of Table 2, pp. 3556-3557). That is a like-for-like comparison and it
  discriminates between the models, which is what the row was for.
- **The old row's quantity is still reported**, in the not-graded set of Section
  3.3, so nothing measured is lost; only its claim to grade is.

The same test was applied to every other row on this gate and G10 was the only
one that failed it.

### 3.3 Rows deliberately NOT graded, and why each

**An identity is not a control** (`VERIFICATION_CHARTER.md` lines 106-111). Each
row below was reported in `K0cS_RESULTS.md` and counted toward no verdict.

| Quantity | Why it was not gated |
| --- | --- |
| Heat balance closure over the sealed cavity | Near-identity. The discrete temperature equation conserves at every iteration on a sealed domain whether or not the solve is converged, so a closure of 0.00 % is evidence about the discretisation and not about the physics. Ampofo's own 0.5 % (p. 3555) is a real measurement because his cavity leaked and his instruments were imperfect; the solver's is not the same quantity |
| theta at the cavity centre | **Near-identity for a Boussinesq solve.** Tian p. 862 stated it outright: "In numerical modelling involving the Boussinesq approximation, a symmetrical result is predicted so that the dimensionless temperature is 0.5 at the centre." The experiments gave 0.5174 (Ampofo) and 0.514 (Tian). Grading this row would grade the Boussinesq approximation, which was fixed across every case, and would report the same failure for every turbulence model. It is a **measurement of the non-Boussinesq defect** and is reported as one. It is near-identity rather than identity only because the imposed horizontal-wall profiles were not exactly antisymmetric (Section 2.3, defect 0.0104 in theta) |
| Turbulence kinetic energy k at mid-height | Both sides carry an assumption. Ampofo's k rests on Eqs. (4)-(5), p. 3554, estimating an unmeasured w'; a two-equation model's k rests on its own closure. Comparing them grades neither |
| Peak rms vertical velocity at mid-height, 0.0717 m/s (Ampofo Table 2) | **The row that was withdrawn from the graded set** (amendment note under Section 3.2). The solve side can only reach a velocity *component* from k by assuming isotropy, and Ampofo p. 3559 measured the flow to be strongly anisotropic there (u'rms under half v'rms). The measured value is reported next to `sqrt(2k/3)` from each solve, and the gap between them is a measurement of the isotropy assumption rather than of the turbulence model |
| Wall shear stress | Reported against Ampofo Table 3. Not gated: the near-wall momentum gradient on a y+ < 1 mesh under a high-Reynolds-number wall function is a quantity whose solve value is set by the wall treatment rather than measured by it, and the rung already grades that physics through G1-G6 where a reference exists in two experiments rather than one |
| Turbulent Prandtl number | **NOT OBTAINED** for this cavity (Section 0.2). Reported as the fixed input it was |

### 3.4 Trust tier

A solve passing every row of Section 3.2 on both meshes of its pair was eligible
for VALIDATED on this case. A solve missing its grid pair was not graded and
capped at TREND ONLY regardless of how close its numbers looked. A solve graded
against any row of Section 2 replaced by a remembered value was not graded at
all.

---

## 4. Claim, source, domain rows (charter Section 3 format)

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| Average Nu on the vertical walls of a 0.75 m air-filled square cavity at Ra 1.58e9 with conducting horizontal walls is 62.6-65.3 | Ampofo p. 3564 and Tian pp. 859-861, both READ IN FULL | Ra 1.58e9, ARz = 2, dT = 40 K, horizontal walls at the measured profiles of Ampofo Table 4 | Adiabatic or perfectly conducting horizontal walls: Beghein et al. via Tian p. 861 give 63.86 and 55.59 for those two idealisations, a 13 % split. Also not applicable to other Ra without a correlation |
| Two independent experiments in the same rig disagree by up to 8.8 % on integral Nusselt, against stated uncertainties of 0.25-1.13 % | DERIVED from the two tables above | Setting bands on this case | Claiming either experiment is wrong; the spread is the reproducibility, not an error attribution |
| The stratification parameter is window-dependent at the 0.16 level | DERIVED from Ampofo Table 5, p. 3558 | Any comparison of Sp between a solve and a paper that did not state its window | Comparisons where both sides state and share a window |
| A Boussinesq solve of this case cannot reproduce the measured centre-point temperature of 0.514-0.5174 | Tian p. 862, READ IN FULL, stated by the authors | Reading the centre-point row of `K0cS_RESULTS.md` | Any turbulence-model attribution; the defect is the same for every model |
| Turbulence statistics on this case are single-source | Tian Part II NOT OBTAINED, confirmed from Part I p. 866 reference list | Row G10 and the reported k row | The integral Nusselt and stratification rows, which are two-source |
