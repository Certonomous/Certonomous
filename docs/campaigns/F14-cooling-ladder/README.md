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
| Digitized reference values from Wibron et al. 2018 Figures 3, 6, 7, 8 | Arming K2c-A's reference column; the rung is TREND-ONLY until then | Not paywalled — the primary is in this repository; the labelled extraction has not been performed | Zero-compute digitization addendum against `docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf`, digitization increment stated per quantity |

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
