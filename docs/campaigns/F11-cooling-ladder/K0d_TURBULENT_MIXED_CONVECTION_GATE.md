# K0d. Turbulent mixed convection gate

Campaign F11, gate K0d. Written 2026-08-17, zero compute spent, no solver launched.
Order of this document, per the brief: the claim first, then the sourcing, then the
gate spec with references.

---

## 1. The claim

A mixed-convection rung needs a flow where an imposed jet or supply stream and a
buoyant wall source contend at comparable strength, in a confined space, with
measured mean velocity and temperature fields good enough to grade against. The
claim this gate is built on:

> Turbulent mixed convection experiments with benchmark-quality confined-flow data
> are rare. The two notable ones in the indoor-air lineage are Schwenke (1975) and
> Blay, Mergui and Niculae (1992), and of these only the Blay cavity has boundary
> conditions recoverable today from open full texts.

The rarity statement is not this document's opinion; it is stated in a peer-reviewed
full text read this session: Xu, W. and Chen, Q. (2000), Simulation of mixed
convection flow in a room with a two-layer turbulence model, *Indoor Air* 10,
pp. 306-314 (tier READ IN FULL): "Experimental investigations on turbulent mixed
convection are very few. The only notable contributions are those by Schwenke
(1975) and Blay et al. (1992)."

## 2. The candidates, evaluated rather than assumed

| Candidate | What it offers | What it costs | Availability, checked 2026-08-17 |
| --- | --- | --- | --- |
| **Blay heated-floor ventilated cavity.** Blay, D., Mergui, S., Niculae, C. (1992). Confined turbulent mixed convection in the presence of a horizontal buoyant wall jet. *Fundamentals of Mixed Convection*, ASME HTD Vol. 213, pp. 65-72 (citation as printed in Xu and Chen 2000, READ IN FULL) | Purpose-built 2D turbulent mixed convection: plane wall jet over a heated floor in a square cavity; velocities, temperatures and velocity fluctuations measured at mid-width and mid-height planes (Xu and Chen 2000, READ IN FULL). Complete boundary conditions recoverable from two independent open full texts (Section 3). Physics is the closest match in the open literature to a cold supply stream contending with a heated floor in an enclosure | Primary proceedings paper not obtainable: no DOI exists (CrossRef bibliographic query on the full title, 2026-08-17, returned no matching record; ASME HTD volumes of that era are unregistered), no OA copy found. Venue metadata independently corroborated by the CiNii record CRID 1573105974176827520, fetched 2026-08-17 (title, first author, 1992, ASME, HTD Vol. 213; that record carries no abstract and no page numbers). The measured profiles therefore exist today only as figures in secondary papers; no tabulated open dataset was found this session. Two boundary-condition discrepancies across secondaries, recorded in Section 3.3 | Primary: NOT OBTAINED. Secondaries carrying setup and figures: open, read in full |
| **IEA Annex 20 two-dimensional room, nonisothermal case 2D2.** Specification: Nielsen, P.V. (1990). Specification of a Two-Dimensional Test Case. Aalborg University, IEA Annex 20 (citation as printed in Nielsen, Rong, Olmedo 2010, READ IN FULL) | Living benchmark with about 50 reported applications; isothermal case 2D1 has Laser-Doppler validation data; conditions L/H = 3.0, h/H = 0.056, Re = 5000, inlet turbulence k_o = 1.5 (0.04 u_o)^2, eps_o = k_o^1.5/l_o, l_o = h/10 (all from Nielsen, Rong, Olmedo 2010, Clima 2010, ISBN 978-975-6907-14-6, READ IN FULL). Benchmark web page named in that paper: www.cfd-benchmarks.com | The nonisothermal measurements are Schwenke's (Schwenke, H. 1975, Luft- und Kaltetechnik 5, pp. 241-246, citation via Xu and Chen 2000): a 1975 German journal not obtainable this session. The isothermal case 2D1 is well documented but has no temperature field, so it cannot gate a thermal quantity. 2D1 also carries a documented model-sensitivity trap: SST predicts a large occupied-zone recirculation that contradicts the Laser-Doppler data (Nielsen, Rong, Olmedo 2010, Fig. 8 discussion, READ IN FULL) | Spec and 2010 review: open, read in full. Schwenke data: NOT OBTAINED |
| **Heated backward-facing step.** Vogel, J.C. and Eaton, J.K. (1985). Combined Heat Transfer and Fluid Dynamic Measurements Downstream of a Backward-Facing Step. *J. Heat Transfer* (title and venue from the Unpaywall record for DOI `10.1115/1.3247522`) | Reputation as a careful separated-flow heat transfer dataset | Unpaywall on `10.1115/1.3247522`, 2026-08-17: `is_oa: false`, no OA location. Full text not seen, so neither the flow conditions nor whether buoyancy is a governing parameter could be verified this session; on the record available here it is a forced-convection separated-flow heat transfer case, not a demonstrated mixed-convection one. No open tabulated dataset found | NOT OBTAINED; regime match to K0d unverified |

## 3. Recommendation: the Blay cavity, and its defect stated plainly

**Recommended: Blay, Mergui, Niculae (1992).** Reasons, in order of weight:

1. It is the only candidate whose physics is actually the K0d physics: a supply
   jet and floor buoyancy at comparable strength in an enclosure, fully turbulent
   (Zou, Zhao, Chen 2018, READ IN FULL, call the flow turbulent in the entire
   domain and the experimental data of high quality).
2. Its boundary conditions are recoverable to gate-spec precision from two
   independent open full texts (3.1, 3.2), which is more than either alternative
   can offer for a thermal case.
3. It carries three decades of published model comparisons to grade against
   qualitatively while the primary is being obtained.

**The defect, stated rather than smoothed:** the primary data is not in hand. No
DOI, no OA copy, no open tabulated dataset. Until the ASME HTD Vol. 213 paper (or
a tabulated digitisation with stated provenance) is obtained, there are no
reference numbers a deviation can be computed against, and the charter forbids
manufacturing them from plot pixels in secondary papers without labelling. Per the
campaign rule that a case without a citable reference value does not get a gate
rung, **K0d is filed TREND-ONLY as of this writing.** The Annex 20 nonisothermal
case and the heated step fall in the same bin, and further down: their thermal
data was not located in any form.

Acquisition route to upgrade: file the Blay paper into the MIT-access docket
pattern (`docs/research/MIT_ACCESS_DOCKET.md`), target ASME HTD Vol. 213 (1992),
pp. 65-72. On receipt, extend Section 5 by addendum with tabulated reference
profiles and pass bands, and only then may this rung grade a solve.

### 3.1 Case setup (recoverable today, all from open full texts)

| Item | Specification | Source and tier |
| --- | --- | --- |
| Cavity | 1.04 m x 1.04 m cross-section, 0.7 m span, flow two dimensional, guard cavities at the spanwise ends | Oulghelou, Beghein, Allery (2020), Data-driven optimization approach for inverse problems, arXiv:2009.06724v2, Section 5.1, READ IN FULL |
| Inlet | Horizontal slot at the top of one vertical wall, height 18 mm; u = 0.57 m/s, v = 0; T_in = 15 C | Zou, Zhao, Chen (2018), *Building Simulation* 11(1), pp. 165-174, Section 3.2, READ IN FULL; velocity and temperature corroborated by Oulghelou 2020 Section 5.1 |
| Outlet | Slot at the bottom of the opposite wall, height 24 mm; zero-gradient outflow | Zou, Zhao, Chen 2018 (geometry); Oulghelou 2020 (outflow condition) |
| Floor | Heated, isothermal | both; temperature discrepancy recorded in 3.3 |
| Other three walls | Isothermal at 15 C, no slip | Oulghelou 2020, Section 5.1 |
| Nondimensional groups | Ra = 2.13e9 on cavity height and floor-to-wall dT; Re = 654 on inlet height and inlet velocity | Oulghelou 2020, Section 5.1, READ IN FULL |
| Inlet turbulence used in a published reproduction | k = 1.25e-3 m2/s2, eps = 5.76e-3 m2/s3 | Oulghelou 2020, Section 5.1; this is that paper's choice, not a measured value; record it as the default and vary it in the sensitivity block |
| Buoyancy treatment in published reproductions | Boussinesq | Zou, Zhao, Chen 2018; Oulghelou 2020 |

### 3.2 Comparison quantities (what the experiment measured)

Velocities, temperatures and velocity fluctuations at the mid-width plane
(x/L = 0.5, floor to ceiling) and the mid-height plane (y/H = 0.5) (Xu and Chen
2000, READ IN FULL; profile comparisons at exactly these planes appear in Zou,
Zhao, Chen 2018 Fig. 4 and Oulghelou 2020 Fig. 3, both READ IN FULL).

### 3.3 Boundary-condition discrepancies across secondaries, recorded

| Item | Value A | Value B | Consequence |
| --- | --- | --- | --- |
| Floor temperature | 35.5 C: Oulghelou 2020 states theta_hot = 35.5 C in defining Ra = 2.13e9 | 35 C: Zou, Zhao, Chen 2018 Section 3.2; Oulghelou 2020 also imposes 35 C on the floor in its own solve despite quoting 35.5 for Ra | 0.5 K on a 20 K difference is 2.5 percent of the driving dT, larger than a useful temperature band; the primary must arbitrate before any pass band on temperature is set |
| Inlet turbulence | k and eps as above (Oulghelou) | Not stated in Zou, Zhao, Chen 2018 | Inlet turbulence is a known sensitivity for wall jets; treat as a swept parameter until the primary states the measured level |

## 4. What a solve against this case may claim today

- TREND-ONLY: circulation direction and pattern (single large circulation with the
  jet along the ceiling and a thermal plume from the floor, secondary recirculation
  in the upper corner on the inlet side, per figures in Zou, Zhao, Chen 2018 and
  the MERL reproduction TR2021-120, both READ IN FULL), qualitative shape of the
  mid-plane temperature and velocity profiles against the published figures.
- Nothing quantitative. No deviation number exists to compute until the primary
  reference values are in hand, and a confident percentage against a digitised
  figure would be exactly the failure mode this lab logged nine instances of this
  week.

## 5. The gate, to be armed by addendum on receipt of the primary

Deviation REL(q) as in K0c. The rows are fixed now so the addendum only fills
numbers:

| Quantity | Reference (to be filled from Blay 1992 tables or figures, with locator and digitisation increment stated) | Provisional band, to be confirmed against the primary's stated measurement uncertainty | Rationale for the provisional band |
| --- | --- | --- | --- |
| Mean temperature profile, x/L = 0.5, floor to ceiling | pending | within 0.5 K after the floor-temperature arbitration of 3.3 | Published reproductions with two commercial codes track the measured profile closely at this plane (Zou, Zhao, Chen 2018, Fig. 4a, READ IN FULL, qualitative); the band must not be finer than the digitisation increment |
| Mean velocity profile, x/L = 0.5 and y/H = 0.5 | pending | REL <= 15 percent at the jet peak; occupied-zone shape graded pointwise | Jet-peak magnitude is the discriminating quantity between wall treatments in the published comparisons |
| Turbulent kinetic energy profile, mid-planes | pending | REPORT-ONLY initially | Fluctuation measurements carry the largest experimental uncertainty in this class of rigs (Xu and Chen 2000 make this point for hot-sphere anemometry generally, READ IN FULL) |
| Global circulation sense | per the primary; the published reproductions show one large circulation with the jet along the ceiling and a floor plume (Zou, Zhao, Chen 2018 Fig. 4 discussion; MERL TR2021-120 Fig. 4; both READ IN FULL) | exact match required | A flipped or fragmented circulation is a regime error, not a percentage error, and it is the error mode the published model comparisons disagree on |

## 6. Claim, source, domain rows (charter section 3 format)

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| Turbulent mixed convection experiments of benchmark quality are rare; Schwenke 1975 and Blay 1992 are the notable confined-flow ones | Xu and Chen 2000, *Indoor Air* 10, pp. 306-314 (READ IN FULL) | Selecting K0d among indoor-air-lineage candidates | Mixed convection in pipes and channels, where that paper cites a separate literature |
| The Blay cavity setup is 1.04 m square, 18 mm inlet at 0.57 m/s and 15 C, 24 mm outlet, heated floor, other walls 15 C, Re = 654, Ra = 2.13e9 | Zou, Zhao, Chen 2018 Section 3.2 and Oulghelou 2020 Section 5.1 (both READ IN FULL, independent of each other) | Building the K0d case to run | The floor temperature to impose, which the two sources give as 35 vs 35.5 C (Section 3.3); and the measured profile values, which neither source tabulates |
| The Annex 20 2D room is L/H = 3.0, h/H = 0.056, Re = 5000 with stated inlet turbulence relations | Nielsen, Rong, Olmedo 2010, Clima 2010 (READ IN FULL) | The fallback isothermal verification of the room-airflow solver chain | Any thermal gate; the nonisothermal data (Schwenke 1975) was not obtained |
| The Vogel and Eaton step is a combined heat transfer and fluid dynamics measurement downstream of a backward-facing step | Unpaywall metadata record for DOI 10.1115/1.3247522 (metadata only) | Knowing the paper exists and is closed | Anything about its conditions, data quality, or regime; the text was not seen |
