# Campaign F11, cooling ladder. Literature legs

Opened 2026-08-17. This folder holds the gate specifications for the campaign's
validation rungs, written from the literature before any fine mesh burns. No
solver was launched in producing anything here; compute authorization is the
owner's and was not spent.

**Naming collision, flagged for a ruling:** the identifier F11 is already carried
by `demo-output/website/campaign/F11_lid_driven_cavity_ladder.md` (dated
2026-07-30, a lid-driven cavity verification family). This folder uses F11 as the
internal name of the cooling ladder per the 2026-08-17 dispatch. The two are
different campaigns sharing a tag; one of them should be renumbered, and until the
ruling lands every cross-reference should name the folder path, not the bare tag.

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

## Trust position, stated up front

| Rung | Reference class | Tier ceiling today |
| --- | --- | --- |
| K0c laminar (de Vahl Davis) | Numerical benchmark, secondary reproductions cross-checked | Verification only; TREND ONLY ceiling (no experiment) |
| K0c turbulent (Betts and Bokhari) | Experiment, primary data files in this folder | Eligible for VALIDATED on passing the gate |
| K0d (Blay cavity) | Experiment, primary not yet obtained | TREND-ONLY until the ASME HTD Vol. 213 paper is acquired; acquisition route named in the spec |

## Papers backing these specs

Full texts read this session and cited with locators live in `docs/papers/` under
the house pdf-plus-txt convention:
`gjesdal_wasberg_andreassen_2003_physics0305049`, `han_xie_2019_1903.09506`,
`nielsen_rong_olmedo_2010_clima_annex20`, `xu_chen_2000_indoor_air_two_layer`,
`oulghelou_beghein_allery_2020_2009.06724`, `zou_zhao_chen_2018_building_simulation`,
`vierendeels_merci_dick_2002_wit_afm02`, and the INL report extract
`martineau_et_al_2009_inl_ext_09_15333` (text extract plus source URL; the PDF is
public at inldigitallibrary.inl.gov and was not duplicated here for size).
