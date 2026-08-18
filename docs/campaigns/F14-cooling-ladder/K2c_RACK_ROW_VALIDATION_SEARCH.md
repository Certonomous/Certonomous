# K2c. Rack-row facility validation search and gate specification

Campaign F14, rung K2c. Written 2026-08-17, zero compute spent, no solver
launched. **NO SOLVE MAY RUN AGAINST THIS GATE UNTIL THE OWNER APPROVES THE
K2a SPECIFICATION AND AUTHORIZES COMPUTE.** Order of this document, per the
campaign brief and the K0c/K0d house form: the search with every availability
check dated, then the gate rows with citations, then what could not be obtained,
recorded so a later rung cannot pass against a number it produced itself.

Provenance tiers as in K0c: READ IN FULL (full text read this session, locator
given), SECONDARY (number read in a full text that attributes it elsewhere,
chain stated), RECALLED (standard in the field but not confirmed in any source
this session — never graded on), NOT OBTAINED (no number exists in this
repository; acquisition path named). Every availability check below was run
2026-08-17 against the Unpaywall API (`api.unpaywall.org/v2/<DOI>`), with
CrossRef bibliographic queries used to establish DOIs. Per the standing
campaign naming rule, this campaign's own vocabulary for the facility class is
rack-row / machine-room; the published papers' titles below are quoted
verbatim, as citations must be.

**The search's one-line result:** one primary experimental dataset for
rack-inlet validation was obtained in full text this session — a **hard-floor**
facility. **No raised-floor (perforated-tile) measurement primary could be
obtained**; every candidate checked is paywalled. The gate therefore has one
armable rung and one rung filed NOT OBTAINED, and the honest split between them
is this document's main content.

---

## 1. The search: candidates, checked rather than assumed

| Candidate | What its record offers | Availability, checked 2026-08-17 | Verdict |
| --- | --- | --- | --- |
| **Wibron, E., Ljung, A.-L., Lundström, T.S. (2018). Computational Fluid Dynamics Modeling and Validating Experiments of Airflow in a Data Center. *Energies* 11(3), 644. DOI `10.3390/en11030644`, CC-BY** | Full experimental characterization of an operating 10-rack, 4-CRAC machine-room module (SICS ICE Module 1, Luleå; hard floor, partial hot-aisle containment) with measured boundary conditions (their Tables 1–2), rack-front/rack-back temperature sensors on all racks, velocity profiles at five locations, instrument accuracies stated, GCI grid study, and a three-way turbulence-model comparison (k–ε, RSM, DES) against the measurements | Unpaywall `is_oa: true` (gold, CC-BY). MDPI host refused this box's fetches (HTTP 403); obtained instead from the Luleå University DiVA repository, `urn:nbn:se:ltu:diva-67958` → `ltu.diva-portal.org/smash/get/diva2:1191242/FULLTEXT01.pdf`, SHA-256 `4de4798ed5eed60feda123c7a2398674a6a9177f44906175847d90f5227d7b77`, filed at `docs/papers/wibron_ljung_lundstrom_2018_en11030644.{pdf,txt}` | **Selected. READ IN FULL.** The only candidate whose primary is in this repository. Section 2 |
| Karki, K.C., Radmehr, A., Patankar, S.V. (2003). Use of Computational Fluid Dynamics for Calculating Flow Rates Through Perforated Tiles in Raised-Floor Data Centers. *HVAC&R Research* 9(2). DOI `10.1080/10789669.2003.10391062` | Title and venue from the CrossRef/Unpaywall record. Content beyond the title: RECALLED (tile-flow-rate prediction against plenum measurements) and not relied on | Unpaywall `is_oa: false`, no OA location, no repository copy | NOT OBTAINED. Section 4 |
| Schmidt, R.R., Cruz, E. (2002). Raised floor computer data center: effect on rack inlet temperatures of chilled air exiting both the hot and cold aisles. ITHERM 2002. DOI `10.1109/itherm.2002.1012507` | Title from the CrossRef record: rack-inlet temperature measurements in a raised-floor facility — the exact quantity the K2a module grades | Unpaywall `is_oa: false` | NOT OBTAINED. Section 4 |
| Schmidt, R.R. et al. (2004). Raised-floor data center: perforated tile flow rates for various tile layouts. ITHERM 2004. DOI `10.1109/itherm.2004.1319226` | Title from the CrossRef record | Unpaywall `is_oa: false` | NOT OBTAINED |
| VanGilder, J.W., Schmidt, R.R. (2005). Airflow Uniformity Through Perforated Tiles in a Raised-Floor Data Center. ASME InterPACK. DOI `10.1115/ipack2005-73375`; journal version: Airflow distribution through perforated tiles in raised-floor data centers, *Building and Environment* (2006), DOI `10.1016/j.buildenv.2005.03.005` | Titles from CrossRef. Cited in the obtained primary as [24]: "results are not totally grid independent even for a grid size as small as 2.5 cm, but do not change significantly below a grid size of about 15.2 cm" (Wibron 2018, p. 10, READ IN FULL — tier SECONDARY for the claim itself) | Both DOIs: Unpaywall `is_oa: false` | NOT OBTAINED |
| Abdelmaksoud, W.A. et al. (2010). Experimental and computational study of perforated floor tile in data centers. ITHERM 2010. DOI `10.1109/itherm.2010.5501413` | Title from CrossRef: the tile-jet momentum measurement that would arbitrate K2a §2.2's superficial-velocity simplification. Companion "Improved CFD modeling of a small data center test cell" cited by the obtained primary as its buoyancy warrant ([22]) | Unpaywall `is_oa: false` | NOT OBTAINED |
| Arghode, V.K., Joshi, Y. (2014). Experimental Investigation of Air Flow Through a Perforated Tile in a Raised Floor Data Center. *J. Electronic Packaging*. DOI `10.1115/1.4028835` | Title from CrossRef | Unpaywall `is_oa: false` | NOT OBTAINED |
| Athavale, J., Yoda, M., Joshi, Y. et al. (2018). Experimentally Validated Computational Fluid Dynamics Model for Data Center With Active Tiles. *J. Electronic Packaging*. DOI `10.1115/1.4039025` | Title from CrossRef | Unpaywall `is_oa: false` | NOT OBTAINED |
| Hamann, H. et al. Recovery Act: A Measurement–Management Technology for Improving Energy Efficiency in Data Centers... (Final Technical Report). DOE/OSTI. DOI `10.2172/1044604` | Title from CrossRef; a DOE final report on measured thermal characterization of operating facilities | Unpaywall `is_oa: true`, `osti.gov/servlets/purl/1044604`. **Not read this session** — a program final report of unknown data quality, deferred rather than skimmed | OBTAINABLE, UNREAD. No gate row until read; acquisition is one fetch |
| Wibron, E., Ljung, A.-L., Lundström, T.S. (2019). Comparing Performance Metrics of Partial Aisle Containments in Hard Floor and Raised Floor Data Centers Using CFD. *Energies* 12(8), 1473. DOI `10.3390/en12081473` | Same group's raised-floor study. From its title and the 2018 paper's reference [6] (their 2016 HEFAT paper, "CFD simulations comparing hard floor and raised floor configurations"): CFD comparisons, and this session found no indication either contains raised-floor *measurements* — but neither full text was read, so that is an expectation, not a finding | Not fetched this session (MDPI 403 on this box; a DiVA route likely exists as for the 2018 paper) | OBTAINABLE, UNREAD. Named as the first place to look for a raised-floor validation before paying for any paywalled candidate |

No curated open benchmark archive for rack-row facility airflow (an ERCOFTAC-case
equivalent) was found by this session's searches — CrossRef bibliographic,
Unpaywall, OpenAlex and Semantic Scholar records were the instruments, and the
absence claim is scoped to them, not to the world.

## 2. The obtained primary, and what it actually contains

Everything in this section is READ IN FULL from
`docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf` (page numbers are the
journal's, printed on each page).

**Facility** (§3.1, p. 3–4): Module 1 of the SICS ICE research facility,
Luleå. Hard-floor air cooling. Room 5.084 × 6.484 × 3.150 m³. Ten server racks
(600 mm wide Minkels cabinets) in two rows, back sides facing, forming a hot
aisle with **partial hot-aisle containment** (a door at the row end); four SEE
Cooler HDZ-2 CRAC units. Full racks house 18 Dell PowerEdge R730xd servers;
R5 is empty (with a small unblanked opening), R6 holds six servers. Switchgear
and UPS are present as unheated blockages; cables and pipes ignored.

**The modelling abstraction is the campaign's own.** The paper models racks and
CRACs as boundary-condition face pairs ("black box model", §3.3, p. 5) with the
rack rise computed exactly as K2a specifies: ΔT = q/(ṁ·c_p), their Eq. (9),
c_p = 1004.4 (printed "kg/(kJ·K)", p. 5 — a unit misprint for J/(kg·K),
recorded rather than silently corrected). It cites Zhang, VanGilder, Iyengar,
Schmidt (ITHERM 2008, their [21]) for the claim that rack-model detail does not
significantly affect the flow field (SECONDARY, chain stated). This makes the
case a validation of the K2a abstraction itself, not merely of one solver.

**Measured boundary conditions** (Tables 1–2, pp. 5–6, quoted in full):

| CRAC | face velocity | supply T |
| --- | --- | --- |
| C1 | 0.61 m/s | 19.7 °C |
| C2 | 0.62 m/s | 20.0 °C |
| C3 | 0.59 m/s | 19.8 °C |
| C4 | 0.62 m/s | 19.9 °C |

| Rack | face velocity | heat load |
| --- | --- | --- |
| R1 | 0.40 m/s | 5180 W |
| R2 | 0.46 m/s | 5194 W |
| R3 | 0.47 m/s | 5161 W |
| R4 | 0.45 m/s | 5152 W |
| R5 | 0.26 m/s | 0 W |
| R6 | 0.41 m/s | 1762 W |
| R7 | 0.38 m/s | 5194 W |
| R8 | 0.43 m/s | 5266 W |
| R9 | 0.42 m/s | 5326 W |
| R10 | 0.39 m/s | 5198 W |

Instruments and stated accuracies (§3.3 p. 5, §3.5 pp. 6–7): BC flow rates by
TSI DP-CALC 8715 with Velocity Matrix, ±3% of reading ±0.04 m/s (0.25–12.5
m/s); supply temperature by Kimo VT100, ±0.4% of reading ±0.3 °C; validation
velocities by Dantec ComfortSense Mini with 54T33 probe, **±2% of reading
±0.02 m/s (0.05–1 m/s), ±5% (1–5 m/s)**, 60 s at 10 Hz; validation
temperatures by Raritan DPX2-T1H1, **±1 °C**, mounted 1.09 m above the lower
edge of the rack doors on both sides of all ten racks. Velocity validation at
five labeled locations (L1–L5, their Figure 2), three or four heights each.

**Regime and solution character** (§3.4, p. 6): buoyancy matters — their
Archimedes number Ar = βgLΔT/V² ≈ 2.7. **Steady-state simulations had
difficulties converging due to fluctuations in the flow field; transient
simulations were used**, 60 s start-up + 600 s transient averaging, dt = 0.05 s
(0.025 s for DES), RMS residuals below 1e-5 per time step. This is direct,
on-case evidence for K2a §5's steadiness risk: the published reproduction of
exactly this class of module could not hold a steady solve.

**Grid** (§4.1, p. 7): tetra grids of 298,535 / 668,242 / 1,486,077 elements
(max cell 14.0 / 10.6 / 8.0 cm, r = 1.31, five inflation layers); GCI on the
fine grid gives **maximum discretization uncertainty 0.0521 m/s** on the L1
velocity profile.

**Findings a later solve will be read against** (§§4.3–5, pp. 9–13): all
CFD rack-front temperatures fall within the experimental error bars; on the
rack-back side 8 of 10 do, and the two misses are attributed by the authors to
the uniform-outlet-temperature simplification against real non-uniformity —
i.e. the black-box abstraction is accurate at **room level** and approximate at
**rack level**, in the authors' own words (p. 13). Near-rack velocity profiles
at L1/L2 are under-estimated at the upper points; moving the comparison line
10–15 cm toward the hot-aisle center restores agreement (their Figure 8),
attributed to gaps behind the rack doors — so **position tolerance is part of
any honest velocity gate on this case**. k–ε fails to predict the low-velocity
regions above the racks; RSM and DES agree closely; the paper recommends RSM
(p. 13). ASHRAE inlet envelopes quoted by the paper (p. 2, attributing ASHRAE
2011 thermal guidelines, their [9]): recommended 18–27 °C, allowable 15–32 °C —
tier SECONDARY, context only, never a pass band.

## 3. The gate

### 3.1 Rung K2c-A: hard-floor rack-inlet validation (Wibron 2018)

**Case to build:** the K2a module instantiated to this facility — every K2a
default replaced by the Section 2 values; hard floor (supply faces on the CRAC
fronts, returns on the CRAC tops), partial hot-aisle containment door, R5/R6
as measured, switchgear and UPS as unheated blockages. Boussinesq
admissibility per K2a §4: with ΔT_rack ≈ 10–13 K at the table's loads and
flows, β·ΔT sits near 0.04 before recirculation and the a-posteriori span
check is mandatory, expected to pass.

**Reference status: the comparison values live in the paper's Figures 3 and
6–8, not in tables.** Per the standing rule, no number is manufactured from
plot pixels without labelling. The gate rows are fixed now; the reference
column is armed by a **digitization addendum**: extract the Figure 6 per-rack
temperatures and Figure 7 profile points from the vector PDF in this
repository, with the digitization increment measured and stated per quantity,
exactly the "tabulated digitisation with stated provenance" route K0d names.
That addendum is a zero-compute task on a primary already in hand — unlike
K0d, nothing external is awaited. **Until it lands, this rung is TREND-ONLY;
after it lands, this rung is the campaign's first eligible for VALIDATED**
(experimental comparison with quantified deviation, per the standing
trust-tier rule).

Rows (deviation REL(q) as in K0c; every row graded on the K0c two-mesh
convention with both meshes reported):

| Quantity | Reference (armed by addendum) | Pass band | Justification |
| --- | --- | --- | --- |
| Rack-front temperature, per rack, at the sensor point (1.09 m, front) | Fig. 6a, digitized | within ±(1.0 K + digitization increment) | ±1 °C is the sensor's stated accuracy and the primary's own CFD lands every rack inside it; a solve of the same abstraction has no excuse for more, and a mis-set BC moves rack-front temperatures by several K (K0c C2's shape) |
| Rack-back temperature, per rack | Fig. 6b, digitized | REPORT-ONLY | The primary itself documents 2 of 10 outside error bars and attributes them to the uniform-ΔT abstraction; grading our solve where the abstraction is known approximate would grade the abstraction, not the solve |
| Velocity profile at L5 (CRAC front) and L3 (hot aisle) | Fig. 7c,e, digitized | REL ≤ 15% of local reading or ±(instrument accuracy + 0.052 m/s GCI), whichever is larger, at each measured height | The two locations where the primary shows robust agreement; the 15% mirrors the K0c turbulent-rung peak-velocity band; the additive floor keeps low-velocity points from being graded below what instrument-plus-discretization can resolve (L-28's rule) |
| Velocity profile at L1, L2, L4 | Fig. 7a,b,d, digitized | REPORT-ONLY with mandatory position-sensitivity sweep ±0.15 m | The primary's own comparison fails at face value here and recovers within 10–15 cm of position (Fig. 8); a gate that failed a solve for reproducing the primary's own documented sensitivity would be noise |
| Above-rack low-velocity region | qualitative, Fig. 9 | REPORT: present/absent | The k–ε failure mode named by the primary; the discriminator between turbulence treatments on this case |
| Heat-balance closure (advective) | — | ≤ `heat_balance_tol_pct` after KV1 validates the advective path (K2a §8) | necessary-not-sufficient, per K2a §8's statement; never cited as validation evidence |

**Turbulence-model caveat carried on the rung's face:** the primary validates
RSM/DES and documents k–ε's failure; K2a's default is k–ω SST, which the
primary did not test and which carries its own documented room-flow trap
(Annex 20, via K0d). An SST solve graded here is a *new* model-form result,
not a reproduction — that is what makes the rung worth running, and also what
forbids borrowing the primary's "within error bars" as an expectation.

### 3.2 Rung K2c-B: raised-floor / perforated-tile validation

**Filed NOT OBTAINED in its entirety.** Every measurement candidate (Section
1: Schmidt & Cruz 2002; Schmidt et al. 2004; VanGilder & Schmidt 2005/2006;
Abdelmaksoud et al. 2010; Arghode & Joshi 2014; Athavale et al. 2018; Karki et
al. 2003) is paywalled with no OA location as of 2026-08-17. Per the campaign
rule — **a case without a citable reference does not get a gate rung** — no
raised-floor gate rows are written, no provisional reference numbers exist,
and any K2b solve of the tile-supply configuration is **TREND-ONLY however
well it converges**, until one of these primaries is acquired. This is the
same discipline as K0d, and the same three prior NOT OBTAINED records stand as
the precedent.

Anything remembered about these papers' contents (tile flow splits, jet
momentum defects) is RECALLED and appears in this campaign only as motivation
for parameter choices, never as a reference value.

## 4. References NOT OBTAINED — extension rows for the campaign README table

| Missing reference | Which rung it blocks | Why not obtained | Acquisition path |
| --- | --- | --- | --- |
| Any raised-floor rack-inlet or tile-flow measurement primary (best candidates, in order of expected fit: Schmidt & Cruz 2002, DOI `10.1109/itherm.2002.1012507`; Abdelmaksoud et al. 2010, DOI `10.1109/itherm.2010.5501413`; VanGilder & Schmidt 2006, DOI `10.1016/j.buildenv.2005.03.005`) | **All of K2c-B**, and the tile-momentum arbitration of K2a §2.2 | All Unpaywall `is_oa: false`, 2026-08-17; no repository copies found | (1) Read Wibron et al. 2019 (`10.3390/en12081473`, OA, DiVA route) first — zero cost — to establish whether any open raised-floor measurement exists in that lineage; (2) failing that, MIT access route (`docs/research/MIT_ACCESS_DOCKET.md` pattern) on the IEEE/Elsevier candidates |
| Digitized reference values from Wibron 2018 Figures 3, 6, 7, 8 | Arming K2c-A's reference column (rung is TREND-ONLY until then) | Not missing — the primary is in this repository; the extraction with stated increments has not been performed | Zero-compute digitization addendum against `docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf`, increment stated per quantity, per K0d's "tabulated digitisation with stated provenance" route |
| Hamann et al. DOE final report content (DOI `10.2172/1044604`) | Nothing yet — no rung is built on it | OA but unread this session | Single fetch from `osti.gov/servlets/purl/1044604`; read before any use |

## 5. Claim, source, domain rows (charter section 3 format)

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| A 10-rack hard-floor module with black-box rack BCs (ΔT = q/(ṁc_p)) reproduces measured rack-front temperatures within ±1 °C sensor accuracy and room-level velocity fields, while rack-level (near-face) quantities are approximate | Wibron, Ljung, Lundström 2018, *Energies* 11:644, §§4.3–5, Figs. 6–8 (READ IN FULL, PDF in `docs/papers/`) | Scoping what the K2a abstraction can be graded on: room-level yes, rack-face detail no | Raised-floor supply; contained-aisle variants beyond the partial door; any facility whose BCs were not measured |
| Steady RANS of this module class may not converge; the published case required transient averaging (600 s) | same, §3.4 p. 6 | K2a §5 risk 1 and its cost multiplier | Cases with demonstrated steady behavior; nothing here forbids trying steady first |
| k–ε mispredicts the above-rack low-velocity regions; RSM and DES agree; solution-time argument favors RSM | same, §§4.4–5 | Model-choice caveats on any K2b solve; the qualitative Fig. 9 gate row | Any claim about k–ω SST, which the primary did not test |
| CFD results for this facility class stop changing significantly only below ~15.2 cm grid size, and are not fully grid-independent even at 2.5 cm | VanGilder et al. via Wibron 2018 p. 10 (SECONDARY — the underlying study is NOT OBTAINED) | Sanity floor for K2a §6's 6 cm base cell | Grading any mesh claim; the primary study is unread |
| ASHRAE recommended/allowable rack-inlet envelopes are 18–27 °C / 15–32 °C | ASHRAE 2011 guidelines via Wibron 2018 p. 2 (SECONDARY) | Context for reporting T_in,i | Any pass band; guidelines are not measurements |

---

## 6. Addendum pointer, appended 2026-08-17 (W-4: nothing above is edited)

The digitization addendum §3.1 called for was written and landed as
`K2c_DIGITIZATION_ADDENDUM.md`. It is appended to rather than merged into this
document, so this document can still be diffed against its own commit.

**What it changed, precisely:**

| Row of §3.1 | Status before the addendum | Status after |
| --- | --- | --- |
| Rack-front temperature, per rack | reference unarmed, rung TREND-ONLY | **ARMED for 8 racks at plus or minus 1.03 K.** R5 and R6 are NOT ARMABLE: the addendum found the paper plots no experimental bar for them. "Per rack" in §3.1 was written before that was known |
| Rack-back temperature, per rack | REPORT-ONLY | **REPORT-ONLY, unchanged.** Values digitized and labelled; 7 racks carry data, and the digitized values reproduce the authors' own "all except two" count exactly |
| Velocity at L5 and L3 | reference unarmed | **ARMED, 7 points**, bands per the addendum §5.2 |
| Velocity at L1, L2, L4 | REPORT-ONLY with the plus or minus 0.15 m sweep | **unchanged**, values digitized and labelled |
| Above-rack low-velocity region | REPORT: present / absent | **unchanged.** Figure 9 is raster; nothing was digitized |
| Heat-balance closure (advective) | blocked on KV1 | **still blocked.** KV1 was verified open and unattempted at `fc1e3bac`, and the script's `--allow-advective` was found not to compute the advective term at all |

**What it did not change, and this is the half that travels badly:**

- **§3.2, rung K2c-B, is untouched and remains NOT OBTAINED in its entirety.**
  No raised-floor gate rows exist. Any K2b solve of the tile-supply
  configuration is TREND-ONLY however well it converges.
- Of §4's three NOT OBTAINED rows, only the second (digitized reference values
  from this repository's own primary) is discharged. The raised-floor primary
  row and the Hamann DOE report row stand exactly as written.
- **No solve has run.** The header's prohibition is unchanged. Arming a
  reference column is not a grade, and the rung is VALIDATED-ELIGIBLE on two
  rows rather than VALIDATED on any.

---

## 7. Acquisition addendum, appended 2026-08-18 (W-4: nothing above is edited)

Zero compute. No solver launched. Two of §4's three NOT OBTAINED rows were the
subject of an acquisition attempt; both attempts succeeded as acquisitions, and
they came back with opposite results. **Neither changes a tier and neither
writes a gate row.** §3.2 is untouched and rung K2c-B remains without gate rows.

### 7.1 Wibron et al. 2019 was obtained, and §1's expectation about it was wrong

**Obtained, READ IN FULL.** Wibron, E., Ljung, A.-L., Lundström, T.S. (2019).
*Comparing Performance Metrics of Partial Aisle Containments in Hard Floor and
Raised Floor Data Centers Using CFD.* **Energies** 12(8), 1473. DOI
`10.3390/en12081473`, CC BY. 17 pages. Filed at
`docs/papers/wibron_ljung_lundstrom_2019_en12081473.{pdf,txt}`, SHA-256
`7abb37039d23aab8e0119aab9592ec446decab4e5766e0862d0f5dac2033c4bb`.

**The route §1 predicted does not exist, and that is worth recording before the
content.** §1 said *"a DiVA route likely exists as for the 2018 paper"*. The
Luleå DiVA record does exist, `urn:nbn:se:ltu:diva-74676` /
`diva2:1326523`, and it is **metadata only**: no `FULLTEXT01` attachment,
`ltu.diva-portal.org/smash/get/diva2:1326523/FULLTEXT01.pdf` returns HTTP 404,
and a scan of the fetched record page for any `get/` or `FULLTEXT` link returns
nothing. The 2018 route does not generalise across one publisher and one
research group. **The copy was obtained from the MDPI content host instead**,
`mdpi-res.com/d_attachment/energies/energies-12-01473/article_deploy/energies-12-01473.pdf`,
HTTP 200, 4,070,311 bytes. `www.mdpi.com` still returns **HTTP 403** to this box
on the same article, so the 403 recorded in §1 is a property of the front-end
host and not of MDPI.

**§1's recorded expectation, quoted: *"this session found no indication either
contains raised-floor measurements, but neither full text was read, so that is
an expectation, not a finding."* The expectation is now a finding, and it is
false.** The paper carries raised-floor measurements, taken in an operating
facility, with the instrument and its accuracy stated.

**The facility is not the same room as §2's.** The 2019 study is **Module 2**
at RISE SICS North / SICS ICE, 6.484 x 7.000 x 3.150 m3 (p. 3, §2.1). The 2018
primary this campaign already holds is **Module 1**, 5.084 x 6.484 x 3.150 m3.
Same facility, different rooms, different rack counts and different boundary
conditions. **The two references may not be combined into one facility model**,
and a rung that graded a Module 1 geometry against a Module 2 measurement would
be comparing two rooms.

**What it measures, with the locator for each:**

| Measured quantity | Where | Instrument and stated accuracy |
| --- | --- | --- |
| **Face velocity through all 14 perforated tiles**, raised floor, supply 18.3 degC | **Table 2, p. 5** | TSI DP-CALC Micromanometer Model 8715 with the Velocity Matrix add-on kit, area-averaged multi-point face velocity, each tile divided into five regions (§2.2, p. 4). **Plus or minus 3 percent of reading plus or minus 0.04 m/s** over 0.25 to 12.5 m/s |
| **Velocity profiles, raised floor with open aisles**, five locations L1 to L5, five heights each (0.6, 1.0, 1.4, 1.8, 2.2 m) | **§2.3, p. 6; plotted against CFD in Figure 4b, p. 9** | Dantec ComfortSense Mini with the 54T33 omnidirectional draught probe. **Plus or minus 2 percent of reading plus or minus 0.02 m/s** over 0.05 to 1 m/s, **plus or minus 5 percent of reading** over 1 to 5 m/s. 60 s duration at 10 Hz |
| CRAH inlet velocities, hard floor, four units | Table 1, p. 4 | as Table 2; each front side divided into 15 measurement zones |
| Per-rack mass flow rate and heat load, raised floor, R1 to R10 | Table 3, p. 5 | derived from measured server load; the correlation is the paper's Equation (1) |
| Supply temperature, both configurations | §2.2, p. 4 | Kimo VT100 hot-wire thermo-anemometer, plus or minus 0.4 percent of reading plus or minus 0.3 degC. **18.3 degC**, stated independent of location |

**Table 2 as read, with the increment carried through per tile.** Values are
verbatim from p. 5; the increment is this campaign's arithmetic on the paper's
own stated accuracy, `0.03 * v + 0.04` m/s, and nothing else:

| Tile | Face velocity (m/s) | Increment (m/s) | Tile | Face velocity (m/s) | Increment (m/s) |
| --- | --- | --- | --- | --- | --- |
| T1 | 1.197 | plus or minus 0.0759 | T8 | 1.309 | plus or minus 0.0793 |
| T2 | 1.358 | plus or minus 0.0807 | T9 | 1.377 | plus or minus 0.0813 |
| T3 | 1.540 | plus or minus 0.0862 | T10 | 1.512 | plus or minus 0.0854 |
| T4 | 1.228 | plus or minus 0.0768 | T11 | 1.529 | plus or minus 0.0859 |
| T5 | 1.220 | plus or minus 0.0766 | T12 | 1.188 | plus or minus 0.0756 |
| T6 | 1.593 | plus or minus 0.0878 | T13 | 1.206 | plus or minus 0.0762 |
| T7 | 1.594 | plus or minus 0.0878 | T14 | 1.455 | plus or minus 0.0837 |

Fourteen tiles, 1.188 to 1.594 m/s, mean 1.3790 m/s; the increment runs 5.5 to
6.4 percent of reading across the set. The spread across tiles, a factor of
1.34 between the slowest and the fastest, is the quantity a plenum solve would
have to reproduce, and the paper attributes it to the uneven rack loads of
Table 3 and to under-floor geometry (p. 5).

**What it does NOT carry, stated as plainly as what it does: no measured
rack-inlet temperature.** §3.2 (p. 8) states the choice in the authors' own
words: *"velocity was chosen as the means of comparison."* The only measured
temperature anywhere in the paper is the 18.3 degC supply. The **"Rack intake
temperatures"** of Figures 8, 10 and 11 are **simulation outputs** compared
across containment setups, and they carry no experimental bar. A reader who
took Figure 8 for a measurement would be reading a CFD result as an experiment.

**What this unblocks, and what it does not:**

| K2c-B half | State before | State after |
| --- | --- | --- |
| **Perforated-tile flow** | NOT OBTAINED; every candidate paywalled | **A measurement primary is now in this repository**, tabulated, per tile, with a stated instrument and a stated accuracy. **Usable as a referent only by a rung that SOLVES the under-floor plenum and predicts the per-tile split** |
| **Rack-inlet temperature** | NOT OBTAINED | **NOT OBTAINED, unchanged.** No candidate is discharged. Schmidt and Cruz 2002, `10.1109/itherm.2002.1012507`, remains the exact-quantity candidate and remains paywalled |

**The caveat that governs how Table 2 may be used, and it is a section 7
caveat.** In the source these fourteen velocities are **imposed boundary
conditions**, not predicted quantities: §2.2 (p. 4) states the tiles were
modelled as fully open with these measured velocities applied, and §2.1 (p. 4)
states *"the under-floor space was not taken into account in the
simulations."* **A lab rung that imposed Table 2 and then reported agreement
with Table 2 would be an identity**, of exactly the class
`docs/VALIDATION_INVENTORY.md` §7 censuses: the reference and the measurement
would share a parent. The values are a referent for a rung that predicts the
split from a plenum solve, and for nothing else.

**K2a §2.2, tile-momentum arbitration: partly, and SECONDARY.** Wibron 2019
p. 4 states, citing **Abdelmaksoud et al. 2010** (their reference [21], which is
one of this campaign's eight NOT OBTAINED primaries), that *"a fully open tile
model is however regarded to be adequate for tiles if the percentage of open
area is 50 percent or more"*, and records that the facility's tiles are **56
percent and 77 percent open**, both above that line. **Tier SECONDARY**: the
claim was read in a full text that attributes it elsewhere, the chain is stated,
and the underlying measurement is still NOT OBTAINED. It is admissible as a
warrant for a modelling choice and is not a reference value.

**Effect on the purchase list, which is the practical result.** §4's first row
named *"read Wibron et al. 2019 first, at zero cost"* as step (1) before any
paid acquisition. **Step (1) is now discharged, and it changes what is worth
buying.** The tile-flow candidates (Schmidt et al. 2004, Arghode and Joshi 2014,
VanGilder and Schmidt, Karki et al. 2003) are no longer the only route to a
tile-flow referent. The **rack-inlet-temperature** candidates are, and Schmidt
and Cruz 2002 names that exact quantity in its title.

**No gate row is written here, and §3.2 stands.** K2c-B has no gate rows and
this addendum writes none: half a reference is not half a rung, and the rung
specification that would predict a tile split does not exist and is the owner's.
A reference column is armed for that rung when it is written; per the K2c-A
precedent, **arming a reference column is not a grade**, and nothing in this
section moves any tier.

### 7.2 Hamann et al. 2012 was obtained, read, and does NOT support a gate row

**Obtained, READ IN FULL.** Hamann, H. (PI), Klein, L., et al. *Recovery Act: A
Measurement - Management Technology for Improving Energy Efficiency in Data
Centers and Telecommunication Facilities.* Final Technical Report, Award
DE-EE0002897, IBM T.J. Watson Research Center, report dated 06/28/2012. DOE/OSTI
DOI `10.2172/1044604`. Fetched from `osti.gov/servlets/purl/1044604`, HTTP 200,
1,440,705 bytes, 27 pages. Filed at
`docs/papers/hamann_klein_2012_osti_1044604.{pdf,txt}`, SHA-256
`aa8ceaafbcdc68f83bc9aeaacef9cba56e938449be02029b14936bbb035cbeb1`. The PDF's
own `Title` metadata field reads *"A Statistical Model for Data-Center
Temperatures"*, which is **not this document's title**; recorded so that a later
reader does not lift the metadata as the citation.

**The answer is no, and the deferral in §1 was right.** §1 filed it as *"a
program final report of unknown data quality, deferred rather than skimmed"*.
Read in full, it is a program final report on the **MMT** platform: sensing
hardware, statistical zone mapping, software development, commercialization and
projected energy savings. **It contains no reference value this campaign, or
any campaign, can gate on.**

| What was looked for | What is there |
| --- | --- |
| Tabulated rack-inlet temperatures | **None.** Every thermal result is a figure: Fig 8 (S-curve vertical inlet profiles at ten air-conditioner settings), Fig 9 (statistical fitting), Fig 10 (thermal zones), Figs 14 and 15 (thermal scans at 0.5 ft and 5.5 ft). No values, no coordinates, no sensor accuracy, no facility geometry, no boundary conditions |
| Tile flow rates | **None per tile.** The nearest number is Appendix A, p. 24: *"the targeted air flow was 83 percent ... the percentage of air from ACU that is passing through the perforated tiles"*, one facility-level figure with no uncertainty, no tile count and no tile geometry |
| A validated CFD comparison | **None quantitative.** §2.1 (p. 14) describes a deliberately **reduced-order** real-time model whose complexity is *"traded"* against measurement data, running *"in less than 2 seconds"* over a 50 kft2 facility. Its one validation, Fig 7, is the qualitative statement that predicted and measured cooling-zone maps *"are overlapping"*. No metric, no deviation, no band |
| Anything tabulated at all | Four tables, all energy and money: Table 1 (savings at three field test sites, kW / MWh per year / dollars per year), Table 2 (achievable savings), Table 3 (economic projection to 2035), Table 4 (power in kW and DCIE before and after) |

**And a measured reason the caution was warranted.** Appendix A, p. 24, states:
*"in more than 8 locations, the rack inlet temperature was higher than the
ASHRAE recommended upper temperature value of 80 degC."* **The unit is wrong by
the report's own subject matter.** §5 of this document already records the
ASHRAE recommended rack-inlet envelope as **18 to 27 degC** (SECONDARY, via
Wibron 2018 p. 2); 80 degC is 53 degC above that upper limit and would destroy
the equipment it is describing. The figure is consistent with **80 degF**, which
is 26.7 degC and sits within a tenth of a degree of the recorded 27 degC upper.
**The one rack-inlet number this report states, it states in the wrong unit.**
That is the demonstration, rather than the assertion, that "unknown data
quality" was the correct classification, and it is the reason nothing here
should be cited loosely.

**Effect on §4.** The third NOT OBTAINED row, *"Hamann et al. DOE final report
content, OA but unread"*, is **DISCHARGED as an acquisition and CLOSED as a
candidate**. Its "which rung it blocks" column already read *"nothing yet, no
rung is built on it"*, and that is now a finding rather than a status: it blocks
nothing, it can arm nothing, and **no later rung should spend a fetch on it
again**. A negative result is worth the fetch precisely here, because the row as
written would otherwise have invited the same fetch every time the list was
re-read.

### 7.3 What still stands after this addendum

- **§3.2 is untouched.** Rung K2c-B has no gate rows and none are written here.
  Any tile-supply solve is TREND-ONLY however well it converges.
- **No tier moved and no chip changed.** K2c-A is still VALIDATED-ELIGIBLE on
  two rows and VALIDATED on none.
- **No solve has run.** The header's prohibition is unchanged.
- Of §4's three rows: the first (any raised-floor primary) is **partly
  discharged on its tile-flow half and untouched on its rack-inlet half**; the
  second was discharged by the digitization addendum; the third is **closed**.

### 7.4 Correction to 7.2, appended 2026-08-18 within the hour, by the same session

**One sentence of section 7.2 above overstated its own arithmetic and is
corrected here rather than edited.** That section wrote that the report's *"80
degC"* is *"consistent with 80 degF, which is 26.7 degC and sits within a tenth
of a degree of the recorded 27 degC upper."* **The gap is a third of a degree
Celsius, not a tenth**, and the figure it is a third of a degree from is a
converted one, so the comparison is worth stating in one direction only.

Re-derived: this document's section 5 records the ASHRAE recommended rack-inlet
upper limit as **27 degC** (tier SECONDARY, via Wibron 2018 p. 2, and it is not
a measurement). `27 degC` is **80.60 degF**. The report's numeral **80** read as
Fahrenheit is **26.667 degC**, which is **0.60 degF** or **0.333 degC** below the
recorded limit; read as Celsius it is **53.0 degC above it**. **The finding is
unchanged and does not rest on the tenth of a degree**: a rack-inlet temperature
of 80 degC is not a data-centre reading in any facility, the numeral matches the
Fahrenheit reading of the limit the same sentence invokes, and the report states
it in Celsius. What is corrected is the closeness claim, which was this
session's arithmetic and was wrong by a factor of about three.

---

## 8. Rung K2c-B: the gate rows §3.2 could not write, appended 2026-08-18 (W-4: nothing above is edited)

**Zero compute. No solver launched.** Frame: repository HEAD `9f3971f6`, checks
run 2026-08-18 between 16:50Z and 17:10Z. **§3.2 above is left standing exactly
as written** — it was true when written, and the value of a NOT OBTAINED record
is that it can be diffed against its own commit. What follows supersedes it; it
does not edit it.

**Frame note.** HEAD moved to `e601e8d7` while this section was being written.
`git diff --name-status 9f3971f6 e601e8d7` was read and touches none of the
objects cited here. The anchor stays at `9f3971f6`.

**One-line result.** A raised-floor perforated-tile measurement primary was
obtained in full text. **K2c-B's gate rows are written below and its reference
column is armed on three of them.** The rung is **NOT gradeable by the K2a
module as specified**, for a reason §8.5 states and the K2a specification
states first, and **arming a reference column is not a grade** — the K2c-A
precedent of `K2c_DIGITIZATION_ADDENDUM.md` §8 governs here too.

### 8.1 The primary, and how it arrived

**Obtained, READ IN FULL.** VanGilder, J.W. (American Power Conversion Corp.);
Schmidt, R.R. (IBM Corp.). *Airflow Uniformity Through Perforated Tiles in a
Raised-Floor Data Center.* Proceedings of IPACK2005, ASME InterPACK '05, July
17–22, San Francisco, California, paper **IPACK2005-73375**, in *Advances in
Electronic Packaging, Parts A, B, and C*, **pp. 493-501** (CrossRef record,
retrieved 2026-08-18). **DOI `10.1115/ipack2005-73375`.** Nine pages, letter,
`Pages: 9` per `pdfinfo`. **Every page cite in this section is the paper's own
printed page number, 1 to 9, which equals its PDF page number** -- not the
proceedings pagination 493-501.
Filed at `docs/papers/data_center_indoor_airflow/vangilder_schmidt_2005_ipack.{pdf,txt}`,
SHA-256 `b515f9bb89a12caf82d1f5dc18e6debb31609d734deafad48f754aceb6e7f114`,
693,825 bytes.

| Provenance question | Answer, dated |
| --- | --- |
| Open access? | **No.** Unpaywall `is_oa: false`, no OA location, **checked 2026-08-18** on `10.1115/ipack2005-73375`. The journal version, `10.1016/j.buildenv.2005.03.005`, was checked the same day and is also `is_oa: false`. §1's 2026-08-17 checks stand and were not overturned; the paper was **bought access to, not found open** |
| Route | The **MIT access route** that §4's acquisition path named, against the ASME Digital Collection. Every page carries the publisher's own stamp: *"Downloaded from asmedigitalcollection.asme.org/InterPACK/proceedings-pdf/InterPACK2005/42002/493/4532097/493_1.pdf by Massachusetts Inst Of Tech. user on 18 August 2026"* |
| DOI verified | CrossRef bibliographic query, 2026-08-18, returned `10.1115/ipack2005-73375`, title *"Airflow Uniformity Through Perforated Tiles in a Raised-Floor Data Center"*, container *Advances in Electronic Packaging, Parts A, B, and C*, issued 2005 |
| **Caveat on the SHA-256** | The file's `Producer` reads *"Acrobat Distiller 5.0 (Windows); modified using iTextSharp"* and its `ModDate` is 2026-08-18T16:22:20Z: **the byte stream carries a per-download watermark**. The SHA-256 identifies **this copy** and a second download would not match it. This is unlike the CC-BY Wibron files, whose SHA-256 is a property of the article. Any later integrity check must be run against **this** copy |

**Tracking status at the time this section was written, 2026-08-18T17:15Z.**
Both files were present in the working tree and **untracked** (`git status`
reported `??`), because `docs/papers/` was mid-reorganisation by a concurrent
session which had staged its own renames but had not yet committed these two.
This section is committed with the campaign records and **not** with the PDF, so
a reader at the commit that lands this section may find the citation resolvable
only in the working tree until the papers reorganisation lands. The DOI, the
CrossRef record and the SHA-256 above are what make the reference identifiable
independently of any path.

**Filename note, for the record.** The file landed briefly as
`vangil der_schmidt_2005_ipack.pdf`, with a space, during a concurrent
reorganisation of `docs/papers/` into topic subfolders. It had been corrected to
`vangilder_schmidt_2005_ipack.pdf` by 16:57Z, by the agent doing the
reorganisation and not by this session. Recorded because the SHA-256 above was
first taken under the old name and is the same file.

### 8.2 A label correction the dispatching order needed, and the repository won

The day order that dispatched this work named VanGilder & Schmidt *"PRIMARY for
K2c-A (raised-floor supply physics)"* and Wibron *"PRIMARY for K2c-B context"*.
**The repository's labels are the reverse and the repository is authoritative.**
Verified before anything below was written:

- `README.md`, trust table: *"K2c-A hard-floor rack-inlet (Wibron 2018)"* and
  *"K2c-B raised-floor / perforated-tile"*.
- §3.1 above: *"Rung K2c-A: hard-floor rack-inlet validation (Wibron 2018)"*.
- §3.2 above: *"Rung K2c-B: raised-floor / perforated-tile validation"*.

**K2c-A is the hard-floor rung and its primary is Wibron 2018. K2c-B is the
raised-floor rung and its primary is, from this section, VanGilder & Schmidt
2005.** No rung was renamed and no existing row moved.

### 8.3 What the paper measures, and what it does not

All page numbers are the paper's own printed numbers, which equal the PDF page
numbers. Tier **READ IN FULL** throughout this subsection.

**The measured case.** One of the ten floor plans, **Floor Plan B**, is the only
one with measurements; the other nine are CFD-only (p. 3: *"Of the nine actual
data centers, one is a facility for which measurement data has been taken; this
case is used to validate the CFD model"*). Floor Plan B, p. 5:

| Property | Value, p. 5 |
| --- | --- |
| Facility | A portion of a large raised-floor data center at **IBM, Poughkeepsie, New York** |
| Test area | 6.06 m (20 ft) × 20 m (66 ft) |
| Raised-floor height | **29.2 cm (11.5 in)**, subfloor to bottom of tile |
| Tiles | 610 mm (2 ft) square; the perforated array is **4 × 15 = 60 tiles** between two CRAC units (p. 5: *"an array of 4 x 15 perforated tiles situated between the 2 CRAC units"*) |
| CRACs | 2, both operating, **neither with a turning vane**, blowers aimed at each other so the streams collide between them |
| Sealing | The test area was blocked off around its perimeter from raised floor to concrete subfloor, *"carefully sealed with cardboard and duct tape"*, and electrical and plumbing openings sealed |
| Tile open area | Nominally 25 %; **actual measurement gave 19.5 %** — *"Actual measurements of the tile showed an array of 0.64 cm (0.25 in) diameter holes resulting in a 19.5 % opening, not 25% as the manufacturer states"* |
| Tile impedance | **Measured on a flow bench**, Eq. (7a) p. 6: `DP[Pa] = 419 {Q[m3/s]}^1.99` |

**The measured results, Table 3, p. 6, quoted verbatim.** Percentage variation
from the mean per-tile airflow rate over the 60-tile array:

| | min. | max. | std. dev. |
| --- | --- | --- | --- |
| **Test** | **−141 %** | **85 %** | **62 %** |
| CFD | −232 % | 75 % | 75 % |

The paper defines the metric on p. 3: a negative percentage is flow below the
mean, *"A value less than –100% implies 'backflow' from the room down into the
plenum"*, and the standard deviation is its Eq. (5) over all n tiles. The paper's
own verdict on the comparison, p. 6: *"The predicted flow rates from the model
are in good agreement with the measured values."*

**Figure 3, p. 6, carries the per-tile values** — four panels, one per tile row,
Test and CFD airflow in cfm against tile number 1 to 15. **Not digitized today.**
Measured, not assumed: printed p. 6 carries **no raster image object**
(`pdfimages -list` reports images only on pp. 1, 4 and 7), and its page content
stream carries 194 moveto/lineto pairs and 306 rectangles, so the figure is
**vector and digitizable** by the method
`K2c_DIGITIZATION_ADDENDUM.md` §1.2 already established. That extraction is a
named, deferred, zero-compute route and **not a defect in this section**: §8.5
explains why 60 per-tile reference values would arm a rung that still could not
be graded.

**What the paper does NOT carry, stated as plainly as what it does:**

| Looked for | Found |
| --- | --- |
| A stated instrument, accuracy or uncertainty for the tile-flow measurements | **NOT OBTAINED.** §8.4 |
| Rack-inlet temperatures | **None.** The paper models the **plenum only** (p. 5: *"Only the plenum airflow is modeled in this investigation with a zero pressure boundary condition imposed above the raised floor"*). No temperature is measured or predicted anywhere in it |
| Plenum obstructions | Excluded by choice, p. 4: *"obstructions are not included in the CFD models"* |

### 8.4 The stated experimental uncertainty is NOT OBTAINED, and this is the rows' binding defect

**Verified by exhaustive search of the full text, not by impression.** The
strings `accuracy`, `uncertaint`, `error`, `±`, `+/-`, `repeatab`, `calibrat`,
`flow hood`, `balometer`, `velometer`, `anemometer` and `measurement device`
were searched over the whole extracted text. **The only `±` in the paper is p. 7
and p. 8, and both are about the spread of a normal distribution** (*"68% of all
perforated tiles will have airflow within ±1s"*; *"68% of the 25%-open tiles
will be within ±10% of the mean"*), which is a property of the tile population,
**not an instrument accuracy**. No measuring instrument is named anywhere for
the tile flow rates.

**Where the uncertainty would live.** The measurements are not this paper's own.
p. 5: *"In order to verify the modeling methodology used in this paper, the
experimental results reported in [6] are used."* Reference **[6]**, p. 9:
*"Schmidt, R. et al, 2001, 'Measurements and Predictions of the Flow
Distribution Through Perforated Floor Tiles In a Raised-Floor Data Center',
InterPACK 2001, Kauai, Hawaii."*

| Question | Answer, dated 2026-08-18 |
| --- | --- |
| DOI for Schmidt et al. 2001 | **None established.** Two CrossRef queries — bibliographic on the full title plus venue and year, and title-plus-author — returned no matching record in the top results. ASME InterPACK proceedings of that era are largely unregistered, the same condition already recorded for Blay, Mergui and Niculae (1992) |
| Copy in this repository | **None** |
| Acquisition route | The **same ASME Digital Collection / MIT access route that delivered this paper**, which is now demonstrated to work on ASME InterPACK proceedings; failing that, document delivery / ILL on the InterPACK 2001 proceedings volume |

**Consequence, applied and not argued around: no row below has an
experimentally-stated tolerance, so no row below carries one.** Where a
tolerance is quoted it is derived from **the published model's own deviation**
and is labelled **PROVISIONAL** on its face. That is a weaker warrant than
K2c-A's rows carry — those rest on the Raritan's ±1 °C and the Dantec's ±2 % ±
0.02 m/s, both stated by the primary — and the difference is the point of this
paragraph.

### 8.5 Can the K2a module be graded against these rows? NO, and the K2a specification says so first

**It cannot, and this is not a close call.** `K2a_RACK_ROW_MODULE_SPEC.md` §1,
under **"No plenum"**, states it before this reference existed:

> *"The under-floor plenum is not meshed in v1; tile supply is imposed at the
> tile face (Section 3). Consequence, recorded here because it scopes K2c:
> published tile-flow-**split** measurements (which tile gets how much of the
> CRAC flow) validate a **plenum** model and cannot gate this module, whose
> per-tile flows are inputs. What this module can be gated on is the **room
> side**: rack-inlet temperatures and aisle temperature/velocity fields for
> given tile flows."*

And §3.2 above set the same condition from the other direction, before the
reference arrived: a tile-flow reference is usable *"only by a rung that SOLVES
the under-floor plenum and predicts the per-tile split"*.

**So the state is exactly this, and it is not a soft blocker:**

| | State at HEAD `9f3971f6` |
| --- | --- |
| K2c-B's reference column | **ARMED on three rows**, from a published measurement, at a stated page |
| A rung that could be graded against it | **DOES NOT EXIST.** K2a v1 imposes per-tile flow as an input and meshes no plenum |
| What a K2a-v1 solve against these rows would produce | **AN IDENTITY, and it would report a clean PASS.** Imposing the 60 tile flows and then reporting their min, max and standard deviation back is a restatement of the inputs. `VERIFICATION_CHARTER.md` §2a: *"A gate whose quantity is derivable by construction from its own inputs is an IDENTITY, not a control. It may be reported. It may never be gated on"* |

**The honest sentence, and it is not the sentence the day's work was hoping
for: arming K2c-B's reference column does not make the existing module
gradeable against it.** What closes the gap is a **module revision that meshes
the under-floor plenum and predicts the split** — new specification work, the
owner's to authorize, not a solve of anything that exists today. The rows below
are written now so that the revision has a gate to be written against, and so
that the next reader does not have to buy the paper again to find out what it
contains.

**Nothing here is a purchase justified after the fact.** The acquisition also
discharged §4's first NOT OBTAINED row on its tile-flow half and closed two
mis-attributions (§8.7), both of which are worth the fetch independently of the
rung.

### 8.6 The gate rows

Rung K2c-B, raised-floor / perforated-tile. **Every row is BLOCKED on the
plenum-solving module of §8.5 and none may be graded before it exists.** Rows
are numbered from B1 so they can never be confused with §3.1's K2c-A rows.

**Case to build, when there is a module to build it in:** Floor Plan B as §8.3
tabulates it — 6.06 × 20 m sealed test area, 29.2 cm plenum, 60 perforated tiles
in a 4 × 15 array between two CRACs with no turning vanes, tiles at the
**measured 19.5 % open area** and the **measured** impedance
`DP[Pa] = 419 Q^1.99` (p. 6). The tile impedance and the open area are
**measured boundary-condition data, not gate rows**: they are inputs to the
solve and grading on them would be the same identity §8.5 names.

| Row | Quantity graded | Reference value | Page | Stated experimental uncertainty | Tolerance | Why |
| --- | --- | --- | --- | --- | --- | --- |
| **B1** | **Standard deviation of per-tile airflow, as % of the mean**, over all 60 tiles | **62 %** | Table 3, **p. 6** | **NOT OBTAINED** (§8.4) | **PROVISIONAL, ±13 percentage points** | The paper's own primary uniformity metric (Eq. 5, p. 3). The band is **the published FLOVENT k-ε model's own deviation**: it gave 75 % against the measured 62 %, and the authors called the comparison *"good agreement"* (p. 6). A solve no worse than the published model passes; a solve worse than it fails. **The band is not an experimental uncertainty and must never be quoted as one** |
| **B2** | **Maximum per-tile airflow, as % variation from the mean** | **+85 %** | Table 3, **p. 6** | **NOT OBTAINED** | **PROVISIONAL, ±10 percentage points** | Same basis: the published model gave +75 %, a 10-point miss, inside the same *"good agreement"* sentence |
| **B3** | **Minimum per-tile airflow, as % variation from the mean** (the backflow row) | **−141 %** | Table 3, **p. 6** | **NOT OBTAINED** | **REPORT-ONLY. NOT GRADED** | The published model gave **−232 %**, a **91-percentage-point** miss on the one metric that decides whether backflow occurs, inside the same sentence that called the agreement good. Grading a solve on a quantity the reference paper's own model missed by 91 points would grade the reference, not the solve. Same discipline, and the same reason, as §3.1's rack-back temperature row |
| **B4** | **Backflow present or absent at the tiles nearest the CRACs** | **PRESENT** | **p. 6**: *"The flow from some of the perforated tiles nearest the CRAC units showed some flow downward into the raised floor plenum"* | not applicable, qualitative | **REPORT: present / absent** | A sign, not a magnitude, and the one qualitative statement the measurement supports without an uncertainty. The counterpart of §3.1's above-rack low-velocity row |
| **B5** | **Location of the maximum: near the centre of the tile array, minima nearest the CRACs** | maximum near centre, minima at the CRAC ends | **p. 6** | not applicable, qualitative | **REPORT: reproduced / not reproduced** | The paper attributes it to the two opposing CRAC jets colliding near the array centre (p. 6). A shape test that a wrong plenum treatment can fail |
| **B6** | Independence of the uniformity metrics from the total airflow rate | Table 4, **p. 6**: halving and doubling the flow moved the standard deviation by ≤ 0.6 points | **p. 6** | not applicable | **IDENTITY. REPORT-ONLY, NEVER GRADED** | The paper **proves** it algebraically from the quadratic loss model, its Eqs. (2)–(4), p. 2: *"Equations (4a) and (4b) show that the fraction of total airflow along each path is independent of airflow rate."* A solve reproducing it reproduces its own discretised algebra. `VERIFICATION_CHARTER.md` §2a forbids gating it. It is worth **reporting** because a solve that failed it would have a bug |
| **B7** | Per-tile airflow, all 60 tiles | Figure 3, **p. 6**, **NOT DIGITIZED TODAY** | **p. 6** | **NOT OBTAINED** | **UNARMED.** No band, because no reference value has been extracted | The figure is vector and digitizable (§8.3). The row is written unarmed and named so a later session extends it rather than rediscovering it. **It is not a gap being papered over: with no plenum-solving module, 60 reference values would arm a row that still could not be graded** |

**No row above may be marked passed until a plenum-solving module exists AND
the row's reference column is read against a solve of it.** B1 and B2 in
addition carry the PROVISIONAL flag on their tolerance until the Schmidt et al.
2001 primary supplies a measured uncertainty.

### 8.7 Two mis-attributions this acquisition closed, one of them in this document

**(a) §1's row on VanGilder & Schmidt cited it as Wibron 2018's reference [24].
That attribution is WRONG, and the acquisition of the 2005 paper does NOT
discharge the claim built on it.**

§1 above wrote, in the VanGilder & Schmidt 2005/2006 row: *"Cited in the
obtained primary as [24]: 'results are not totally grid independent even for a
grid size as small as 2.5 cm, but do not change significantly below a grid size
of about 15.2 cm'"*. §5's fourth claim row carries the same attribution as
SECONDARY.

**Read from Wibron 2018's own reference list, p. 14, entry 24 is:** *"VanGlider,
J.W.; Zhang, X. Coarse-Grid CFD: The effect of Grid Size on Data Center
Modeling. ASHRAE Trans. 2008, 114, 166–181."* Counted through the list in order,
[24] is the twenty-fourth entry and is that paper. **It is a different paper by
a different pair of authors in a different venue three years later**, and the
VanGilder & Schmidt tile-uniformity papers of 2005 and 2006 are not in Wibron's
reference list at all.

**And the paraphrase does not match the 2005 paper either.** VanGilder & Schmidt
2005, p. 5, READ IN FULL, states the opposite structure: *"The maximum length of
any side of any grid cell was systematically reduced until predicted tile airflow
results **stabilized**. Ultimately, a grid size was selected with the following
characteristics: a maximum cell size of 15 cm (6 in), a minimum cell size of 2.5
cm (1 in), and a minimum of 8 cells in the plenum-depth direction."* The two
length scales in Wibron's sentence, 2.5 cm and about 15.2 cm (= 6 in), appear
here as **the two ends of the selected grid's cell-size range**, not as a
statement about where results stop changing. Whether Wibron's sentence is a fair
paraphrase of the **2008** paper is **NOT OBTAINED**: that paper has not been
read.

| Status of the grid-size claim | Before 2026-08-18 | After |
| --- | --- | --- |
| Attributed to | VanGilder & Schmidt 2005/2006 | **VanGilder & Zhang 2008, ASHRAE Trans. 114, 166–181** |
| Tier | SECONDARY, underlying study NOT OBTAINED | **SECONDARY, underlying study still NOT OBTAINED — a different study than the one named** |
| DOI | assumed to be the 2005/2006 DOIs | **None established.** CrossRef bibliographic query on title, authors, venue and year, 2026-08-18, returned no matching record. ASHRAE Transactions of that era are largely unregistered |
| Acquisition route | (the wrong paper's) | ASHRAE Technology Portal, or document delivery / ILL on ASHRAE Transactions vol. 114 |
| Where it is used | §6 of `K2a_RACK_ROW_MODULE_SPEC.md`'s sanity floor for the 6 cm base cell | **Unchanged in effect**: it was never graded on, and it is still never graded on. Only the citation is corrected |

**(b) §5's claim row is superseded, and the replacement is narrower.** The
corrected row, in this document's §5 format:

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| A raised-floor plenum CFD of an actual facility was run with a maximum cell size of 15 cm, a minimum of 2.5 cm and at least 8 cells across the plenum depth, after reducing cell size until tile-airflow results stabilised | **VanGilder & Schmidt 2005, IPACK2005-73375, p. 5 (READ IN FULL, PDF in this repository)** — now **PRIMARY**, replacing the SECONDARY chain | A sanity floor for K2a §6's 6 cm base cell, which is finer than both ends of this range | Any claim about where results *stop changing*, which this paper does not make; any claim about hexahedral-versus-tetrahedral grids; anything about the 2008 coarse-grid study, which is NOT OBTAINED |
| Measured tile open area was 19.5 % against a 25 % manufacturer nominal, and measured tile impedance was `DP[Pa] = 419 Q^1.99` | **same, p. 6, PRIMARY** | Boundary-condition data for any Floor-Plan-B case; a warrant that manufacturer-nominal open area is not a measurement | Any other tile type; the 56 %-open grates, whose loss coefficient 3.4 is from **manufacturer's published data** (p. 4), not measured here |
| Perforated-tile airflow uniformity is independent of total airflow rate | **same, Eqs. (2)–(4) p. 2 and Table 4 p. 6, PRIMARY** | Reporting; scoping a plenum module's parameter sweeps | **Any gate row. It is an identity** (§8.6, row B6) |

**(c) §7.1's 50 % open-area warrant is unchanged, and this paper does not
upgrade it.** §7.1 recorded, via Wibron 2019 p. 4 citing Abdelmaksoud et al.
2010, that *"a fully open tile model is however regarded to be adequate for
tiles if the percentage of open area is 50 percent or more"*, with the SICS ICE
facility's tiles at **56 % and 77 % open**, tier **SECONDARY**, *"a warrant for
a modelling choice and not a reference value"*. That stands exactly as written.
**VanGilder & Schmidt 2005 does not state that threshold and cannot be cited for
it**; Abdelmaksoud et al. 2010 remains NOT OBTAINED. What the 2005 paper adds is
adjacent and useful and is **not** the same claim: its two tile types are 25 %
and 56 % open with loss coefficients **51.3 and 3.4** from manufacturer data
(p. 4), and it states that with 56 %-open tiles *"the plenum and room (above the
raised floor) airflow are somewhat coupled"* so that plenum-only results are
*"strictly applicable only to the case of uniform room pressure above the tiles"*
(p. 5). **That is a caution about the 56 %-open case, from a primary, sitting
next to a SECONDARY warrant that 56 % is adequate.** Both are recorded; neither
is a reference value; the tension between them is the reader's to see and is not
resolved here.

### 8.8 Supersession: what this section closes in §4 and what it leaves open

**§4 is not edited.** Its status after this section:

| §4 row | Status at 2026-08-18 |
| --- | --- |
| **Row 1**, any raised-floor rack-inlet or tile-flow measurement primary | **DISCHARGED ON ITS TILE-FLOW HALF, TWICE OVER.** §7.1 delivered Wibron 2019's Table 2 (imposed boundary conditions, usable only by a plenum-solving rung); this section delivers VanGilder & Schmidt 2005's Table 3 (a genuine CFD-versus-measurement comparison of the tile split). **Its rack-inlet-temperature half is UNTOUCHED and remains NOT OBTAINED**: neither paper measures a rack-inlet temperature. Schmidt & Cruz 2002, DOI `10.1109/itherm.2002.1012507`, remains the exact-quantity candidate. The row named VanGilder & Schmidt 2006 (`10.1016/j.buildenv.2005.03.005`) as one of three best candidates; **the 2005 conference version was obtained instead**, and the 2006 journal version is not separately pursued |
| **Row 2**, digitized reference values from Wibron 2018 Figures 3, 6, 7, 8 | **DISCHARGED IN FULL, 2026-08-18.** Figures 6 and 7 armed the reference column on 2026-08-17 (`K2c_DIGITIZATION_ADDENDUM.md` §§4–5); Figures 3 and 8 were tabulated with their increments by that document's **§11**, which also records the finding that **neither could ever have armed a row** because neither carries an experiment Figure 7 does not already carry |
| **Row 3**, Hamann et al. DOE final report | **CLOSED** by §7.2. Unchanged |
| **New**, from §8.7 | **Two references were added to the NOT OBTAINED list by this section, not removed from it**: Schmidt et al. 2001 (InterPACK, no DOI established) for K2c-B's missing experimental uncertainty, and VanGilder & Zhang 2008 (ASHRAE Trans. 114, no DOI established) for the grid-size claim's true source |

### 8.9 What still stands after this section

- **§3.2's caveat is honoured, not evaded.** A tile-flow reference is usable only
  by a rung that solves the plenum and predicts the split. **No such rung
  exists**, so K2c-B's rows are written and **BLOCKED**, and any tile-supply
  solve by the K2a module as specified is **TREND-ONLY however well it
  converges** — unchanged from §3.2.
- **No tier moved and no chip changed.** K2c-A is VALIDATED-ELIGIBLE on two rows
  and VALIDATED on none. **K2c-B is not eligible for anything**, because a
  reference without a rung that can be graded against it is a reference, not a
  gate that has been reached.
- **No solve has run.** This document's header prohibition is unchanged.
- **The experimental uncertainty for every armed K2c-B row is NOT OBTAINED**,
  and the tolerances on B1 and B2 are PROVISIONAL and derived from a published
  model's deviation, which is a weaker warrant than K2c-A's rows carry.
