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
