# Campaign F14, cooling ladder. Literature legs

Opened 2026-08-17. This folder holds the gate specifications for the campaign's
validation rungs, written from the literature before any fine mesh burns. No
solver was launched in producing anything here; compute authorization is the
owner's and was not spent.

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

## Trust position, stated up front

| Rung | Reference class | Tier ceiling today |
| --- | --- | --- |
| K0c laminar (de Vahl Davis) | Numerical benchmark, secondary reproductions cross-checked | Verification only; TREND ONLY ceiling (no experiment) |
| K0c turbulent (Betts and Bokhari) | Experiment, primary data files in this folder | Eligible for VALIDATED on passing the gate |
| K0d (Blay cavity) | Experiment, primary not yet obtained | TREND-ONLY until the ASME HTD Vol. 213 paper is acquired; acquisition route named in the spec |

## References NOT OBTAINED. Three gate rows cannot be graded today

Carried at the top level because a rung whose reference was never obtained must not
later pass because someone forgot the reference is missing. **No number below
exists in this repository. None of these three rows may be marked passed until the
named acquisition path closes and the row is extended by addendum.**

| Missing reference | Which rung it blocks | Why not obtained | Acquisition path |
| --- | --- | --- | --- |
| Tabulated core temperature gradient for the de Vahl Davis square cavity | K0c **laminar** rung, stratification half of the K0c mandate | Neither primary carries it openly: de Vahl Davis 1983 (DOI `10.1002/fld.1650030305`) and Le Quere 1991 (*Computers and Fluids* 20, pp. 29-41, DOI `10.1016/0045-7930(91)90025-D`) are both paywalled; Unpaywall `is_oa: false`, checked 2026-08-17. No number was invented | Obtain either paper via the MIT access route (`docs/research/MIT_ACCESS_DOCKET.md` pattern), then extend the K0c laminar table by addendum |
| Measured Nusselt number for the Betts and Bokhari tall cavity | K0c **turbulent** rung, heat transfer row | The ERCOFTAC database provides no Nusselt files; the paper carrying the measured heat transfer (DOI `10.1016/S0142-727X(00)00033-3`) is paywalled, Unpaywall `is_oa: false` | Obtain Betts and Bokhari (2000) full text, **or** derive wall heat flux from the near-wall temperature files with the derivation and its resolvable increment stated by addendum |
| Blay, Mergui and Niculae (1992) primary, ASME HTD Vol. 213, pp. 65-72 | **All of K0d.** The rung is filed **TREND-ONLY**: gate rows fixed, reference numbers still awaiting the primary | No DOI exists (CrossRef query on the full title, 2026-08-17, no matching record; ASME HTD volumes of that era are unregistered) and no OA copy was found. The profiles exist today only as figures in secondary papers | Acquire the ASME HTD Vol. 213 proceedings paper; until then K0d cannot rise above TREND-ONLY whatever a solve produces |

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
