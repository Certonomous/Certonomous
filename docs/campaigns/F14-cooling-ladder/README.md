# Campaign F14, cooling ladder. Literature legs

Opened 2026-08-17. This folder holds the gate specifications for the campaign's
validation rungs, written from the literature before any fine mesh burns. No
solver was launched in producing anything here; compute authorization is the
owner's and was not spent.

> **Addendum 2026-08-17, later the same day.** The paragraph above is left
> standing because it was true when written and because the specifications'
> value is that they can be diffed against their own commit. It is now out of
> date in one respect: the **K0c laminar rung has been executed** under a
> compute authorization scoped to it and to the K0b mesh-sensitivity pair, and
> two run trees have joined this folder — `K0c_runs/` and
> `K0b_mesh_sensitivity/`. The specifications themselves are untouched. The
> result is `K0c_RESULTS.md`. **K0c's turbulent rung, K0d, K2b, the rack-row
> module and any turbulent SST case remain unrun and unauthorized.**
>
> **Addendum 2026-08-18.** The **K0c turbulent rung has now been executed** under
> its own compute authorization (150 core-minutes of the overnight thermal
> ceiling; 95.0 spent). `K0cT_runs/` and `K0cT_RESULTS.md` have joined this
> folder and the specification is again untouched. The result is a **GATE FAIL
> against a real experiment**, which is why the trust table below no longer says
> "eligible".

## Naming collision: ruled 2026-08-17. This campaign is F14

**The ruling.** This cooling campaign was dispatched on 2026-08-17 under the label
F11. That label was already taken. **The cooling campaign is F14 from this commit
forward. F11 continues to mean the lid-driven cavity ladder and nothing else.**
The owner named this campaign F11 without knowing the tag was taken and has been
told it moved.

**Grounds, measured rather than asserted:**

- `demo-output/website/campaign/F11_lid_driven_cavity_ladder.md` was created
  2026-07-30, three weeks before this campaign's dispatch. It has the earlier
  claim on the tag.
- It carries gate results against Ghia, Ghia and Shin 1982 and owns a populated
  `demo-output/website/campaign/F11_runs/` tree. It has the larger footprint.
  Precedence therefore runs to the incumbent, and the newcomer moves.
- F14 was verified entirely unused: zero occurrences repository-wide, as are F15
  through F22. F12 is a live campaign with its own pre-registration, so F14 is the
  next free tag. (F13 was named as "next unused" in an older document written
  before F12 was checked; that reading is superseded by this one.)

**Reading older documents.** An F11 reference in anything written before
2026-08-17 means the lid-driven cavity ladder. An F11 reference in a
2026-08-17 document about *this* work means this campaign under its withdrawn
dispatch label, and should be read as F14. Two such documents were written by a
concurrent agent under a physics-based naming scheme and are deliberately **left
unedited**, because one of them is a preregistration whose value is that it can be
diffed against its own commit:

- `demo-output/website/campaign/THERMAL_K0_PREREGISTRATION.md` §0 records this
  collision as open and awaiting the owner. It is closed by the ruling above.
- `demo-output/website/campaign/THERMAL_K0_runs/build_cases.py` header points at
  that §0.

Neither file names this folder's path, and neither is renamed: `THERMAL_K0_*` is a
physics label that never collided.

Nothing in this folder is a website surface and none of it feeds application
materials.

## Contents

| File | What it is |
| --- | --- |
| `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` | Validation gate spec for the differentially heated cavity. Laminar verification rung against the de Vahl Davis benchmark (Ra 1e3 to 1e6, reference values triple-corroborated from full texts, pass bands with justification). Turbulent validation rung against the Betts and Bokhari ERCOFTAC Case 079 experiment (primary data in hand, gate on mid-height velocity peaks and core stratification, derived metrics scripted). States plainly which reference values could not be obtained (laminar core stratification; turbulent Nusselt number) and what would close each gap |
| `K0d_TURBULENT_MIXED_CONVECTION_GATE.md` | Claim, sourcing, and gate spec for the turbulent mixed-convection rung. Three candidates evaluated (Blay heated-floor ventilated cavity, IEA Annex 20 nonisothermal room, heated backward-facing step). Recommendation: the Blay cavity, with its defect stated: the primary ASME proceedings paper is unobtainable today, so the rung is filed TREND-ONLY with the gate rows fixed and the reference numbers awaiting the primary. The other two candidates fall in the same bin or below |
| `compute_reference_metrics.py` | Recomputes every derived number in the K0c turbulent-rung table from the primary data files. The gate quotes nothing derived that this script does not print |
| `reference-data/MANIFEST.md` | Provenance of the primary data: source URLs, archive SHA-256, file naming key |
| `reference-data/betts_bokhari/` | The 22 primary data files the K0c gate names, byte-identical copies from the ERCOFTAC Case 079 archive |
| `K0cT_RESULTS.md` | **Added 2026-08-18.** The executed **turbulent** rung against the Betts and Bokhari experiment: **GATE FAIL, 8 of 18 graded rows**, every deviation a number, the turbulence-model decision argued with its alternatives named, the deviation **attributed to the model** by a rule registered before the run using a model twin, a mesh pair and a boundary-condition twin, four controls with their kinds (one of which missed its registered prediction and says so at full volume), and the Nusselt number reported as an explicitly **UNGRADED** measurement. 95.0 core-minutes against a 119.6 estimate written first |
| `K0cT_runs/` | **Added 2026-08-18.** The nine cases: two graded two-mesh pairs, the kOmegaSST/LaunderSharmaKE model twin, the adiabatic-ends boundary-condition twin, and three control twins. `COST_PROPOSAL.txt` and `CONTROL_PREDICTIONS.txt` are timestamped files written **before** any graded case ran, and both are reproduced verbatim into `gate_k0ct.json` |
| `K0c_RESULTS.md` | **Added 2026-08-17.** The executed laminar rung: the gate table with every deviation as a number, the five controls and their kinds, the cost in core-minutes, and the core stratification reported as an explicitly ungraded measurement |
| `K0c_runs/` | **Added 2026-08-17.** The eight graded cases (four Ra on a mandatory two-mesh pair each) plus three control twins, their dictionaries, `0.orig/` initial conditions, solver logs and `scripts/heat_balance.py` audits. Time directories and meshes are gitignored and rebuilt from the dictionaries |
| `K0b_mesh_sensitivity/` | **Added 2026-08-17.** The K0b mesh-sensitivity pair (32x32 and 128x128) that completes the triple with the committed 64x64 leg, answering proposal P2 of `THERMAL_K0_RESULTS.md` |
| `K1_STANDING_THERMAL_CHECKS.md` | **Added 2026-08-17.** K1a/K1c: the four thermal checks made standing (`docs/physics_rules.yaml` block `thermal`, monitor standard v1.9 signatures S13–S15) and verified by execution against planted defects |
| `K2a_RACK_ROW_MODULE_SPEC.md` | **Added 2026-08-17, zero compute.** The parameterized rack-row module: geometry, parameter ranges, a boundary condition on every surface (BC types verified in the installed OpenFOAM v2606 source), the Boussinesq admissibility policy against the lab's own 30.0 K limit, mesh strategy, measurement and audit plan, and the compute cost estimate with its basis. **Awaiting owner approval; no solve authorized** |
| `K2c_RACK_ROW_VALIDATION_SEARCH.md` | **Added 2026-08-17, zero compute.** The rack-row facility validation search and gate: one experimental primary obtained in full (Wibron et al. 2018, hard-floor 10-rack module, CC-BY, PDF in `docs/papers/`), gate rows fixed with the reference column awaiting a labelled digitization addendum; the raised-floor rung filed NOT OBTAINED in its entirety, every candidate's availability check dated |

## Trust position, stated up front

| Rung | Reference class | Tier ceiling today |
| --- | --- | --- |
| K0c laminar (de Vahl Davis) | Numerical benchmark, secondary reproductions cross-checked | Verification only; TREND ONLY ceiling (no experiment) |
| K0c turbulent (Betts and Bokhari) | Experiment, primary data files in this folder | **EXECUTED 2026-08-18: GATE FAIL, 8 of 18 rows. NO row earns VALIDATED** — Section 2.5 conditions eligibility on passing every row. `kOmegaSST` and `LaunderSharmaKE` on buoyant cavity stratification stay **TREND ONLY**, now with measured error bars: core stratification over-predicted by 0.140 and under-predicted by 0.076 against a reference of 0.095 ± 0.02. See `K0cT_RESULTS.md` |
| K0d (Blay cavity) | Experiment, primary not yet obtained | TREND-ONLY until the ASME HTD Vol. 213 paper is acquired; acquisition route named in the spec |
| K2c-A hard-floor rack-inlet (Wibron 2018) | Experiment, primary READ IN FULL and in `docs/papers/`; reference values live in its figures | TREND-ONLY until the labelled digitization addendum arms the reference column; then eligible for VALIDATED |
| K2c-B raised-floor / perforated-tile | No primary obtained; every candidate paywalled (checks dated 2026-08-17) | NOT OBTAINED — no gate rows exist; any tile-supply solve is TREND-ONLY whatever it produces |

## References NOT OBTAINED. Three gate rows cannot be graded today

Carried at the top level because a rung whose reference was never obtained must not
later pass because someone forgot the reference is missing. **No number below
exists in this repository. None of these three rows may be marked passed until the
named acquisition path closes and the row is extended by addendum.**

| Missing reference | Which rung it blocks | Why not obtained | Acquisition path |
| --- | --- | --- | --- |
| Tabulated core temperature gradient for the de Vahl Davis square cavity | K0c **laminar** rung, stratification half of the K0c mandate | Neither primary carries it openly: de Vahl Davis 1983 (DOI `10.1002/fld.1650030305`) and Le Quere 1991 (*Computers and Fluids* 20, pp. 29-41, DOI `10.1016/0045-7930(91)90025-D`) are both paywalled; Unpaywall `is_oa: false`, checked 2026-08-17. No number was invented | Obtain either paper via the MIT access route (`docs/research/MIT_ACCESS_DOCKET.md` pattern), then extend the K0c laminar table by addendum |
| Measured Nusselt number for the Betts and Bokhari tall cavity | K0c **turbulent** rung, heat transfer row. **STILL NOT OBTAINED after the rung was executed 2026-08-18.** That rung reports Nu = 4.871 (Ra 0.86e6) and 5.694 (Ra 1.43e6) as **UNGRADED MEASUREMENTS**, and its model twin gives 7.984 on the identical case — a **40 percent** model-to-model spread with no reference to adjudicate it. `K0cT_runs/analyse_k0ct.py` re-reads this NOT OBTAINED statement out of the specification on every run and **exits 2 if it has been removed** | The ERCOFTAC database provides no Nusselt files; the paper carrying the measured heat transfer (DOI `10.1016/S0142-727X(00)00033-3`) is paywalled, Unpaywall `is_oa: false` | Obtain Betts and Bokhari (2000) full text, **or** derive wall heat flux from the near-wall temperature files with the derivation and its resolvable increment stated by addendum |
| Blay, Mergui and Niculae (1992) primary, ASME HTD Vol. 213, pp. 65-72 | **All of K0d.** The rung is filed **TREND-ONLY**: gate rows fixed, reference numbers still awaiting the primary | No DOI exists (CrossRef query on the full title, 2026-08-17, no matching record; ASME HTD volumes of that era are unregistered) and no OA copy was found. The profiles exist today only as figures in secondary papers | Acquire the ASME HTD Vol. 213 proceedings paper; until then K0d cannot rise above TREND-ONLY whatever a solve produces |
| Any raised-floor rack-inlet or tile-flow measurement primary (best candidates: Schmidt and Cruz 2002, DOI `10.1109/itherm.2002.1012507`; Abdelmaksoud et al. 2010, DOI `10.1109/itherm.2010.5501413`; VanGilder and Schmidt 2006, DOI `10.1016/j.buildenv.2005.03.005`) | **All of K2c-B** (raised-floor rung), and the tile-momentum arbitration of K2a section 2.2 | Every candidate Unpaywall `is_oa: false`, checked 2026-08-17; no repository copies found. Full candidate table in `K2c_RACK_ROW_VALIDATION_SEARCH.md` section 1 | Read Wibron et al. 2019 (`10.3390/en12081473`, OA via the DiVA route) first at zero cost; failing that, the MIT access route on the IEEE/Elsevier candidates |
| Digitized reference values from Wibron et al. 2018 Figures 3, 6, 7, 8 | Arming K2c-A's reference column; the rung is TREND-ONLY until then | Not paywalled — the primary is in this repository; the labelled extraction has not been performed | Zero-compute digitization addendum against `docs/papers/data_center_indoor_airflow/wibron_ljung_lundstrom_2018_en11030644.pdf`, digitization increment stated per quantity |

The in-document statements these rows summarise are at
`K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` §1 ("Core stratification, laminar rung:
reference NOT OBTAINED") and §2.3 ("Nusselt number, turbulent rung: reference NOT
OBTAINED"), and `K0d_TURBULENT_MIXED_CONVECTION_GATE.md` §2. This table does not
replace them; it makes them visible without opening the specs.

## Papers backing these specs

Full texts read this session and cited with locators live in `docs/papers/` under
the house pdf-plus-txt convention:
`gjesdal_wasberg_andreassen_2003_physics0305049`, `han_xie_2019_1903.09506`,
`nielsen_rong_olmedo_2010_clima_annex20`, `xu_chen_2000_indoor_air_two_layer`,
`oulghelou_beghein_allery_2020_2009.06724`, `zou_zhao_chen_2018_building_simulation`,
`vierendeels_merci_dick_2002_wit_afm02`, and the INL report extract
`martineau_et_al_2009_inl_ext_09_15333` (text extract plus source URL; the PDF is
public at inldigitallibrary.inl.gov and was not duplicated here for size).

**Added 2026-08-17 with the K2 specifications:**
`wibron_ljung_lundstrom_2018_en11030644` (CC-BY, fetched from the Luleå DiVA
repository after the publisher host refused this box; SHA-256 in the K2c spec).

---

# Addendum 2026-08-18, K2c re-status (W-4: nothing above is edited)

**Zero compute. No solver launched. No compute authorization requested or
spent.** Frame: repository HEAD `9f3971f6`; every check below was run
2026-08-18 between 16:50Z and 17:15Z. The tables above are left standing because
they were true when written and because their value is that they can be diffed
against their own commits. **The two K2c rungs moved; K0d did not.**

## The ladder, re-stated

| Rung | State at 2026-08-18 | What changed today |
| --- | --- | --- |
| K0c laminar (de Vahl Davis) | Verification only, TREND-ONLY ceiling | Nothing |
| K0c turbulent (Betts and Bokhari) | **GATE FAIL**, 8 of 18 rows, executed 2026-08-18 | Nothing |
| **K0d (Blay cavity)** | **TREND-ONLY. STILL BLOCKED, and deliberately restated so it is not lost among today's two unblockings.** See below | Nothing. **No part of today's work touches K0d** |
| **K2c-A hard-floor rack-inlet (Wibron 2018)** | **Reference column ARMED and COMPLETE.** VALIDATED-ELIGIBLE on two rows, **VALIDATED on none** | The digitization row was closed **in full**: Figures 6 and 7 armed the column on 2026-08-17, and Figures 3 and 8 were tabulated with their increments on 2026-08-18 |
| **K2c-B raised-floor / perforated-tile** | **GATE ROWS WRITTEN, reference column ARMED on three rows, and every row BLOCKED.** Not eligible for any tier | A measurement primary was obtained (VanGilder & Schmidt 2005) and seven gate rows were written against it |

**Three sentences that must travel together, because either one alone
misleads:**

1. **K2c-B has gate rows and a reference for the first time.**
2. **No rung can be graded against them**, because K2a v1 meshes no plenum and
   imposes per-tile flow as an input, so a v1 solve against these rows would be
   an **identity** and would report a clean PASS (`VERIFICATION_CHARTER.md`
   §2a). Closing that gap is a **module revision that solves the plenum** — new
   specification work, the owner's to authorize — not a solve of anything that
   exists today.
3. **Arming a reference column is not a grade.** The K2c-A precedent says so
   explicitly and it governs K2c-B identically.

## Closures to the "References NOT OBTAINED" table above

**The table above is not rewritten.** The discipline its own preamble states
runs both ways: *"a rung whose reference was never obtained must not later pass
because someone forgot the reference is missing"* — and equally, **a reference
that WAS obtained must be recorded loudly enough that the rung is not left
artificially blocked either.** The closures:

| Row of the table above | Status at 2026-08-18 | Where the record is |
| --- | --- | --- |
| Tabulated core temperature gradient, de Vahl Davis | **STILL NOT OBTAINED.** Untouched today | `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` §1 |
| Measured Nusselt number, Betts and Bokhari | **STILL NOT OBTAINED.** Untouched today | `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` §2.3 |
| Blay, Mergui and Niculae (1992) primary | **STILL NOT OBTAINED.** Untouched today. See the K0d block below | `K0d_TURBULENT_MIXED_CONVECTION_GATE.md` §2 |
| Any raised-floor rack-inlet or tile-flow measurement primary | **DISCHARGED ON ITS TILE-FLOW HALF. ITS RACK-INLET-TEMPERATURE HALF IS UNTOUCHED AND REMAINS NOT OBTAINED.** VanGilder & Schmidt 2005 (`10.1115/ipack2005-73375`) was obtained in full text via the MIT access route against the ASME Digital Collection, 2026-08-18, and carries a CFD-versus-measurement tile-flow comparison. **Neither it nor Wibron 2019 measures a rack-inlet temperature**; Schmidt & Cruz 2002 (`10.1109/itherm.2002.1012507`) remains the exact-quantity candidate and remains paywalled (Unpaywall `is_oa: false`, 2026-08-17) | `K2c_RACK_ROW_VALIDATION_SEARCH.md` **§8** |
| Digitized reference values from Wibron 2018 Figures 3, 6, 7, 8 | **DISCHARGED IN FULL.** Figures 6 and 7 on 2026-08-17; **Figures 3 and 8 on 2026-08-18**, tabulated with per-quantity increments. The completion also recorded that Figures 3 and 8 **could never have armed a row**: Figure 3 plots no experiment, and Figure 8's experimental markers are Figure 7's (control C6 measures the identity) | `K2c_DIGITIZATION_ADDENDUM.md` **§11** |

## Closure 2026-08-18, later the same day: the Betts and Bokhari Nusselt reference WAS OBTAINED

**This supersedes one row of the closures table above by date, and that row is
left standing unedited** (W-4). When it was written, "Measured Nusselt number,
Betts and Bokhari — **STILL NOT OBTAINED.** Untouched today" was true. Later the
same day the paper arrived and it stopped being true. Both statements are kept,
in date order, because the specification's value is that it can be diffed against
its own commit.

| | |
| --- | --- |
| What arrived | Betts, P.L. and Bokhari, I.H. (2000), *Int. J. Heat and Fluid Flow* 21, pp. 675-683, full text, **READ IN FULL** |
| How it was identified | **By content, not by path.** A concurrent lane reorganised `docs/papers/` into topic subdirectories the same day and the dispatched path no longer existed. Matched on the PII `S0142-727X(00)00033-3` in the PDF's own metadata. SHA-256 `905cce61e84bc485b086f9215277fd94bf823f3ffc12453084ab580423baeb94` |
| The reference | **Table 1, p. 682: average Nusselt number 5.85 (Ra 0.86e6) and 7.57 (Ra 1.43e6)** |
| Its stated uncertainty | The paper states none on Nu and **+/-5 %** on the wall temperature gradient Nu is computed from (p. 681) |
| Where the record is | `K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` **addendum A1**, appended; §2.3 above it untouched |
| The verdict it produced | `K0cT_NUSSELT_REGRADE.md`: **kOmegaSST GATE FAIL at both Rayleigh numbers**, -16.79 % and -24.75 %, at 3.1 and 4.6 times the validation uncertainty |
| The 40 percent model spread | **Resolved in favour of NEITHER model.** The reference sits 81.8 % of the way from kOmegaSST to LaunderSharmaKE. kOmegaSST is refuted; LaunderSharmaKE's error (+5.50 %) is the same size as the validation uncertainty (5.41 %), so it is neither confirmed nor refuted — and it is **NOT GRADED at all**, having been run on a single mesh against a grid-pair rule written the day before |
| The tripwire | **Moved, not defeated.** §2.3's NOT OBTAINED sentence was not deleted; the guard in `K0cT_runs/analyse_k0ct.py` now requires **both** it and addendum A1's marker, and refuses (exit 2) if either is gone. Proven in three directions |

**Two further references this one table supplied, which the campaign did not have:**

- **A measured turbulent Prandtl number for the tall cavity**, derived from Table
  1's centre-line eddy viscosity and eddy diffusivity ratios: **Prt = 1.07 at
  Ra 0.86e6 and 1.28 at Ra 1.43e6**, against the **0.85** the executed rung used.
- **A corroboration of `compute_reference_metrics.py`.** Its independently
  derived peak mid-height velocities (0.140 and 0.190 m/s) sit **0.7 % and 0.5 %**
  from Table 1's own 0.139 and 0.191 — a check against a source it never read.

**What this does NOT close:** the core stratification row. Table 1's
`Centre-line dT/dx` is a *horizontal* gradient (`x` is horizontal, notation
p. 676), not the vertical stratification, and no vertical stratification figure
appears in the paper (addendum A1.7).

## K0cS: a new rung opened today against two primaries that arrived with Betts

`K0cS_SQUARE_CAVITY_GATE.md` and `K0cS_PREREGISTRATION.md` were written and
committed **before any of their results existed**, so they can be diffed against
their own commit. The square-cavity turbulent rung is graded against **Ampofo and
Karayiannis (2003)** and **Tian and Karayiannis (2000) Part I**, both READ IN
FULL, both identified by content after the reorganisation, every number carrying
its journal page.

`K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` §2.1 ruled on 2026-08-17 that this
pair was "the stronger square-cavity dataset on paper, but no number from it can
be carried today ... until then it earns no rung." **That ruling is superseded for
these two papers only, by their arrival**, and §2.1 is left unedited.

**The bands on that rung are NOT the papers' stated uncertainties, and the reason
is measured:** the two experiments were run in the **same rig** and disagree with
each other by **up to 8.8 %** on integral Nusselt, against stated uncertainties of
0.25-1.13 % (Ampofo Table 1, p. 3555) and 0.33 % (Tian, p. 852). The
reproducibility spread between two independent measurements is the honest
uncertainty and the bands are built from it.

### K0cS executed the same day: GATE FAIL, and a laminar solve beat kOmegaSST on it

`K0cS_RESULTS.md` and `K0cS_runs/` joined this folder 2026-08-18.

| Model | Verdict | Rows |
| --- | --- | --- |
| kOmegaSST | **GATE FAIL** | 8 of 10 |
| kEpsilon | **GATE FAIL** | 6 of 10 |
| LaunderSharmaKE | **REFUSED**, not graded | fine mesh missed the registered convergence criterion |

**The registered headline prediction - no model passes - held.** 14 of 20 graded
rows failed and every row was shown flippable in both directions.

**Three findings worth reading the record for:**

1. **Two of this gate's rows cannot tell a turbulence model from no model.** The
   laminar control passes **four** rows; kOmegaSST passes **two**; and the set of
   rows kOmegaSST passes that laminar does not is **empty**. Their hot-wall
   Nusselt sits 1.21 percent apart. kOmegaSST's passed rows therefore carry no
   evidential weight about turbulence closure on this case. kEpsilon is the only
   model whose passes discriminate (three rows laminar fails).
2. **Grid refinement moved the stratification AWAY from the experiment** for both
   low-Re models - kOmegaSST 0.674 to 0.754, LaunderSharmaKE 0.620 to 0.778
   against a reference of 0.481. Their coarse agreement was cancellation between
   model error and discretisation error. A single-mesh solve would have reported
   a better number and a worse result, which is what the grid-pair rule exists to
   prevent.
3. **LaunderSharmaKE was REFUSED rather than failed**: on mesh refinement its
   damping function collapsed (0.887 to 0.034), `k` hit its floor on 25 996 of
   40 000 iterations, and the eddy viscosity ended four orders below molecular.
   The model left its own validity domain rather than losing to the data.

**A named failure mode closed NEGATIVE.** Control C3 moved Prt from 0.85 to the
1.28 derived from Betts Table 1 and hot-wall Nusselt moved **1.75 percent**
against a registered 5-20 percent. **Constant turbulent Prandtl number is not
where the square cavity loses accuracy.** That does not transfer to the tall
cavity, whose measured centre-line Prt of 1.07-1.28 remains 21-34 percent above
the 0.85 the K0cT rung used.

**Cost: 206.5 core-minutes, $0.177** - 44 percent of the 470.8 core-minute
pre-registered proposal and 0.71 percent of the $25 authorization. The
continuation reserve was not drawn.

**The pre-registration's per-model predictions were substantially wrong** and the
results record tabulates registered-versus-measured for every one. Two were wrong
in direction; the prediction that kEpsilon would be the worst performer was the
most wrong on the page.

## References NOT OBTAINED — two rows ADDED today

Today's acquisitions removed one half-row from the list above and **added two
references to it.** Both are named here so the list stays complete:

| Missing reference | Which claim it blocks | Why not obtained | Acquisition path |
| --- | --- | --- | --- |
| Schmidt, R. et al. (2001). *Measurements and Predictions of the Flow Distribution Through Perforated Floor Tiles In a Raised-Floor Data Center.* InterPACK 2001, Kauai | **The stated experimental uncertainty of every K2c-B row.** VanGilder & Schmidt 2005 uses these measurements (its reference [6]) and states no instrument, no accuracy and no uncertainty for them anywhere — verified by exhaustive string search of the full text, 2026-08-18. The tolerances on rows B1 and B2 are therefore **PROVISIONAL**, derived from the published model's own deviation and **not** from an experimental uncertainty | **No DOI established.** Two CrossRef bibliographic queries, 2026-08-18, returned no matching record; ASME InterPACK proceedings of that era are largely unregistered, the same condition already recorded for Blay 1992 | The **same ASME Digital Collection / MIT access route that delivered the 2005 paper**, now demonstrated to work on ASME InterPACK proceedings; failing that, document delivery / ILL on the InterPACK 2001 volume |
| VanGilder, J.W.; Zhang, X. (2008). *Coarse-Grid CFD: The Effect of Grid Size on Data Center Modeling.* ASHRAE Transactions 114, pp. 166–181 | The grid-size sanity floor cited in `K2a_RACK_ROW_MODULE_SPEC.md` §6. **This is Wibron 2018's reference [24]** — read from Wibron's own reference list, p. 14. `K2c_RACK_ROW_VALIDATION_SEARCH.md` §1 and §5 had attributed that citation to **VanGilder & Schmidt 2005/2006**, which is a different paper by a different pair of authors in a different venue three years earlier, and which is **not in Wibron's reference list at all**. **Obtaining the 2005 paper therefore did NOT discharge this claim** | **No DOI established.** CrossRef bibliographic query on title, authors, venue and year, 2026-08-18, returned no matching record; ASHRAE Transactions of that era are largely unregistered | ASHRAE Technology Portal, or document delivery / ILL on ASHRAE Transactions vol. 114. **Low priority: the claim was never graded on and still is not** |

## K0d: explicitly STILL TREND-ONLY, and the unblock condition named

**Restated at full volume because two other rungs moved today and K0d did not.**

| K0d | State at 2026-08-18 |
| --- | --- |
| Tier | **TREND-ONLY.** Gate rows fixed, **reference numbers still awaiting the primary** |
| The unblock condition, and it is the only one | **Blay, D., Mergui, S., Niculae, C. (1992). *Confined turbulent mixed convection in the presence of a horizontal buoyant wall jet.* Fundamentals of Mixed Convection, ASME HTD Vol. 213, pp. 65–72** |
| Why it is not simply bought | **No DOI exists.** CrossRef bibliographic query on the full title, **2026-08-17**, returned no matching record; ASME HTD volumes of that era are unregistered. Venue metadata was independently corroborated by CiNii record CRID 1573105974176827520, fetched 2026-08-17. **A record with no DOI cannot be purchased through a DOI-resolving route**, so this needs a **document-delivery / interlibrary-loan** route against the physical ASME HTD Vol. 213 (1992) proceedings, not a purchase |
| Papers on hand that people will be tempted to substitute | **Zhang, W. and Chen, Q. (2000)**, *Large eddy simulation of natural and mixed convection airflow indoors…*, Numerical Heat Transfer Part A 37(5), 447–463, at `docs/papers/buoyant_natural_convection/zhang_chen_2000_les_indoor.{pdf,txt}`; and **Kayne, A. and Agarwal, R.K. (2013)**, *Computational fluid dynamics modeling of mixed convection flows in buildings enclosures*, Int. J. Energy and Environment 4(6), 911–932, at `docs/papers/data_center_indoor_airflow/kayne_agarwal_2013_mixed_convection.{pdf,txt}`. Both arrived in this repository 2026-08-18 and **neither was read by the session writing this addendum** |
| What they may and may not do | They may **CORROBORATE** K0d. They **may NOT GATE** it. **A gate never binds to a secondary source's replotted data**: both are CFD papers that reproduce Blay's case, so a gate bound to their figures would grade this lab against another lab's model, and the two boundary-condition discrepancies already recorded in `K0d_TURBULENT_MIXED_CONVECTION_GATE.md` §3.3 (floor temperature 35 vs 35.5 °C; inlet turbulence stated by one source and not the other) are exactly the damage that does |

**K0d cannot rise above TREND-ONLY whatever a solve produces, and no solve of it
is authorized.**

## Files added or changed today

| Path | What |
| --- | --- |
| `K2c_RACK_ROW_VALIDATION_SEARCH.md` §8 | **Appended.** K2c-B's seven gate rows with page-level citations, the NOT OBTAINED experimental uncertainty, the plenum precondition, and two mis-attributions closed |
| `K2c_DIGITIZATION_ADDENDUM.md` §11 | **Appended.** Figures 3 and 8 tabulated with their increments; controls C9 and C10 added; the regression check on the two pre-existing `.dat` files |
| `reference-data/wibron_2018_digitized/fig3_grid_convergence.dat` | **New.** CFD-only, marked `***NOT A REFERENCE VALUE.***` in its own header |
| `reference-data/wibron_2018_digitized/fig8_position_sensitivity.dat` | **New.** CFD-only, same marking |
| `digitize_wibron2018.py` | **Repaired and extended.** It was **BROKEN at HEAD**, exiting 1 on a `FileNotFoundError`, because `docs/papers/` had been reorganised into topic subfolders and the primary's path was assembled from string segments — a fresh instance of **L-137**'s class, invisible to both a literal scan and an idiom scan. The repair is L-137's own: resolve by name with the SHA-256 still deciding. `fig6_rack_temperatures.dat` and `fig7_velocity_profiles.dat` were verified **byte-identical** after the rerun |
| `docs/papers/data_center_indoor_airflow/vangilder_schmidt_2005_ipack.{pdf,txt}` | **New primary**, 9 pages, SHA-256 `b515f9bb…`. Note: the byte stream carries a per-download watermark, so that hash identifies **this copy**, not the article |

**No solver ran. Nothing was submitted, sent, filed, uploaded or registered.**
