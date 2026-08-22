# DC cooling certificate template

**ASHRAE-style DC cooling certificate specification — grows one line per passed
thermal rung (Sanaa's directive H-6, 2026-08-22).**

This file is the **spec of which quantity classes are backed**, not a
certificate. Certificates are minted by `sdk/chief_engineer/certificate.py`,
which seals an evidence bundle with SHA-256 (`evidence_hash`, canonical payload).
What this file governs is which lines that minting is entitled to print.

The directive it implements is recorded verbatim at
`docs/campaigns/T-family/THERMAL_BUILDUP_DIRECTIVE.md`. H-6: *"as each rung
passes, its quantity class ... gets its line in the ASHRAE certificate template,
so the product artifact grows with the validation instead of after it."*

---

## 1. Rules

1. **A line enters on a PASS or GATE REACHED verdict from a FROZEN comparator,
   and on nothing else.** The comparator's freeze is Charter §2d, and the
   commit that froze it is named in the line's source file. A verdict read off
   a report rather than out of a comparator's own output does not enter.
2. **BLOCKED, NOT A RESULT and GATE FAIL rows are listed in section 3, "Not yet
   certifiable", with the reason** — never omitted, and never softened into a
   caveat on a certified line. A rung that reported and failed is a rung with a
   record, and the record is the product.
3. **A GATE REACHED line is marked as such on its face.** GATE REACHED means the
   rung reached its gate and the row was reported rather than graded, usually
   because the deviation sits below a stated floor. It is not a PASS and the
   certificate may not print it as one.
4. **Every limit quoted carries its provenance tier.** The lab holds the ASHRAE
   recommended upper inlet limit at tier SECONDARY only. Quoted from
   `docs/VALIDATION_INVENTORY.md` §10.6:

   > The recommended upper limit this lab actually holds is **27 degC**,
   > recorded at `docs/campaigns/F14-cooling-ladder/K2c_RACK_ROW_VALIDATION_SEARCH.md`
   > section 5 at tier **SECONDARY** (via Wibron 2018 p. 2), and it is a
   > guideline rather than a measurement.

   **No Fahrenheit figure is quoted from recollection.** §10.6 exists because a
   round 80 degF was written as though it had been read somewhere and had not
   been; that correction is the reason this rule is in the spec rather than in
   a style note.
5. **A quantity class is backed by the rung that measured it, not by the rung
   above it.** A pipe-`Nu` line does not back a rack-inlet-temperature claim,
   and the "Planned lines" table in section 4 is a schedule, not a holding.
6. **Verdict vocabulary is the fixed set** — PASS, GATE REACHED, GATE FAIL, NOT
   A RESULT, BLOCKED, plus PENDING for unrun work. No sixth term enters this
   file.

---

## 2. Certificate lines (backed today)

| quantity class | DC meaning | backing rung/row | verdict | value vs reference | band | grid triple | source file |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **duct/pipe forced-convection `Nu`, laminar, constant-`q″`** | heat pickup per unit length in a laminar duct or cold-plate channel at fixed heat input | **T1c L2**, `Nu` constant `q″` | **PASS** | 4.365298 vs exact 4.3636364, dev **0.0381 %** | GCI **0.0459 %** | 3-level ladder, observed `p` **2.031** | `docs/campaigns/T-family/T1c_RESULTS.md` |
| **duct/pipe laminar friction, `f·Re` (constant-`Ts` arm)** | pressure drop per unit length in the same channel; the pumping-power half of a cold-plate spec | **T1c L1**, `f·Re` | **PASS** | 63.98771 vs exact 64, dev **0.0192 %** | GCI **0.0236 %** | 3-level ladder; observed `p` not reported (`—` in the source table) | `docs/campaigns/T-family/T1c_RESULTS.md` |
| **duct/pipe laminar friction, `f·Re` (constant-`q″` arm)** | as above, on the constant-flux arm | **T1c L3**, `f·Re` | **PASS** | 63.98771 vs exact 64, dev **0.0192 %** | GCI **0.0236 %** | 3-level ladder; observed `p` not reported (`—` in the source table) | `docs/campaigns/T-family/T1c_RESULTS.md` |
| **conjugate wall conduction flux** | heat crossing a multi-layer server-wall or cold-plate stack-up | **T9a R0**, wall `q″` [W/m²] | **PASS** | 19.854991 vs exact 19.502682, dev **1.806 %** | GCI **2.043 %** | 20.425588 → 20.069440 → 19.854991, **CONVERGING**, `p` 1.079 | `docs/campaigns/T-family/T9a_RESULTS.md` |
| **conjugate interface temperature** | contact temperature at a material interface — the die-to-spreader / spreader-to-sink junction class | **T9a R2**, wall `T` interface 2 [K] | **PASS** | 300.023872 vs exact 300.024378, dev **0.00017 %** (−0.51 mK) | GCI **0.00025 %** (0.75 mK) | 300.022999 → 300.023532 → 300.023872, **CONVERGING**, `p` 0.952 | `docs/campaigns/T-family/T9a_RESULTS.md` |
| **fin conduction efficiency** | heat-sink fin effectiveness | **T9a R3**, fin efficiency `η` | **GATE REACHED** (reported, not graded) | 0.8331737 vs exact 0.8332367, dev **0.00756 %** | GCI **0.00077 %**, below the **0.025 %** O(Bi) floor | 0.8331455 → 0.8331658 → 0.8331737, **CONVERGING**, `p` 1.990 | `docs/campaigns/T-family/T9a_RESULTS.md` |
| **fin tip temperature ratio** | tip-to-base temperature drop along a heat-sink fin | **T9a R4**, `1/cosh(mL)` | **GATE REACHED** (reported, not graded) | 0.7523951 vs exact 0.7523781, dev **0.00226 %** | GCI **0.00011 %**, below the **0.025 %** O(Bi) floor | 0.7523988 → 0.7523962 → 0.7523951, **CONVERGING**, `p` 1.997 | `docs/campaigns/T-family/T9a_RESULTS.md` |
| **enclosure radiative exchange, box walls — floor** | radiant load onto the raised floor / under-rack surface of an enclosed volume | **T10a B0**, box floor `q` [W/m²] | **PASS** | 6483.263010 vs exact 6484.920941, dev **0.02557 %** | GCI **0.03326 %** | 6480.760 → 6482.287 → 6483.263, **CONVERGING**, `p` 0.954 | `docs/campaigns/T-family/T10a_RESULTS.md` |
| **enclosure radiative exchange, box walls — x-walls** | radiant exchange with the aisle-facing side walls | **T10a B2**, box x-walls `q`, mean [W/m²] | **PASS** | −1260.793300 vs exact −1254.691645, dev **0.48631 %** | GCI **0.67756 %** | −1269.197 → −1264.164 → −1260.793, **CONVERGING**, `p` 0.853 | `docs/campaigns/T-family/T10a_RESULTS.md` |
| **enclosure radiative exchange, box walls — y-walls** | radiant exchange with the end walls | **T10a B3**, box y-walls `q`, mean [W/m²] | **PASS** | −1971.177941 vs exact −1964.697075, dev **0.32987 %** | GCI **0.48472 %** | −1980.140 → −1974.801 → −1971.178, **CONVERGING**, `p` 0.825 | `docs/campaigns/T-family/T10a_RESULTS.md` |

**Ten lines, of which two are GATE REACHED and eight are PASS.** Every one comes
from an EXACT-tier rung — a closed-form reference that cannot be wrong. **No
line on this certificate is yet backed by a published measurement**, and no line
above is a data-centre quantity: they are the component physics the DC quantity
classes in section 4 will be built from.

---

## 3. Not yet certifiable

| quantity class | backing rung/row | verdict | why it is not certifiable | route back |
| --- | --- | --- | --- | --- |
| **duct/pipe forced-convection `Nu`, laminar, constant-`Ts`** | **T1c L0**, `Nu` constant `Ts` | **GATE FAIL** | 3.659958 vs exact 3.6567934, dev **0.0865 %** against a GCI band of **0.0301 %** — missed by ~2.9 bands | open; the constant-`q″` half of the class (L2) passes and does not carry it |
| **duct/pipe `Nu` at the originally registered station** | **T1c L4** | **NOT A RESULT** | station as originally registered; no band armed | superseded by L0/L2 |
| **turbulent pipe `Nu`, `Re` 1e4** | **T1b B0** | **PASS as returned by the frozen comparator; grid triple DIVERGENT** | **PASS as returned by the frozen comparator; every triple DIVERGENT/STAGNANT; under the binding triple gate adopted for T3/L4 these read NOT A RESULT.** 31.619 vs 30.907, dev 2.84 % against band 2.305 %, `p` −0.219 | **L4 arms `R_*_x`**, running since 2026-08-21; `R_10k_x` ETA 2026-08-23 ~01:40Z |
| **turbulent pipe `Nu`, `Re` 3e4** | **T1b B2** | as above; triple **DIVERGENT** | as above. 72.480 vs 73.684, dev 3.89 % against band 1.635 %, `p` −0.150 | L4 arms, ETA ~2026-08-26 06–08Z |
| **turbulent pipe `Nu`, `Re` 1e5** | **T1b B4** | as above; triple **DIVERGENT** | as above. 185.771 vs 190.398, dev 5.33 % against band 2.430 %, `p` −0.059 | L4 arms, ETA ~2026-08-26 06–08Z |
| **turbulent pipe `Nu`, `Re` 3e5** | **T1b B6** | as above; triple **STAGNANT** | as above. 449.255 vs 456.723, dev 5.75 % against band 1.635 %, `p` +0.010 | L4 arms, ETA ~2026-08-26 06–08Z |
| **conjugate interface temperature, hot interface** | **T9a R1**, wall `T` interface 1 [K] | **GATE FAIL** | 348.778673 vs exact 348.781082 — **−2.41 mK against a 0.92 mK GCI band** (0.00069 % vs 0.00026 %), triple CONVERGING at `p` 1.738 | **H-4 diagnosis arm**: interface scheme vs mesh vs property jump, one change per run. REPORTED 2026-08-22 — cause identified (T9a-D, D454): interface scheme; a re-graded T9a under a new pre-registration with `Gauss harmonic` is the path to a certifiable line |
| **enclosure radiative exchange, ceiling** | **T10a B1**, box ceiling `q` [W/m²] | **GATE FAIL** | −3269.602153 vs exact −3265.532221 — **0.12463 % against a 0.07676 % GCI band**, ~1.6 bands, triple CONVERGING at `p` 1.480 | **H-3a refinement arm** (discretisation finding, cheap). PENDING |
| **grey radiative exchange, curved geometry — inner sphere** | **T10a S0**, inner sphere `q` [W/m²] | **NOT A RESULT** | triple **DIVERGENT** (`p` −3.253), no band armed; the outer-sphere row-sum defect (4.3–4.8 %, non-converging under fixed quadrature) dominates | **H-3b characterisation**: mesh-family sweep, geometry sweep, reproducer from clean case; upstream candidate #4, **filing remains Sanaa's call**. PENDING |
| **grey radiative exchange, curved geometry — outer sphere** | **T10a S1**, outer sphere `q` [W/m²] | **NOT A RESULT** | triple **DIVERGENT** (`p` −1.838), no band armed | as above. PENDING |
| **separated-flow heat transfer, peak Stanton number** | **T3 G1**, `St_peak` | **NOT A RESULT** | **NOT A RESULT (ladder not converged; triples DIVERGENT/OSCILLATORY) and primary not held** — no case meets the registered `1e-6` criterion and every graded triple is DIVERGENT or OSCILLATORY, so gates (1)/(2) of `T3_PREREGISTRATION.md` §7.1 fire ahead of gate (3); Vogel & Eaton (1985) is still NOT OBTAINED as of 2026-08-22 and obtaining it is necessary, not sufficient | converge the ladder (ext1 extension launched 2026-08-22, `T3_EXT1_AMENDMENT.md`) **and** acquire the primary. See `T3_RESULTS.md` and `T3_PREREGISTRATION.md` §2 |
| **separated-flow heat transfer, reattachment location of the peak** | **T3 G2**, `x_peak/H` | **NOT A RESULT** | as above | as above |
| **separated-flow heat transfer, `St` at 10 H** | **T3 G3**, `St_10H` | **NOT A RESULT** | as above | as above |
| **separated-flow heat transfer, `St` at 20 H** | **T3 G4**, `St_20H` | **NOT A RESULT** | as above | as above |

**On the word used for T3, corrected 2026-08-22.** This table first read
**BLOCKED** on all four T3 rows, on the expectation that the missing document
would be what stopped them. The frozen comparator returned something else: **NOT
A RESULT** on all four, because no case meets the registered `1e-6` convergence
criterion and every graded triple is DIVERGENT or OSCILLATORY — gates (1) and
(2) of `T3_PREREGISTRATION.md` §7.1 fire ahead of gate (3), so the rows never
reach the point where the absent primary is the binding constraint. The
certificate takes the comparator's word rather than editing the comparator to
match the expectation. Vogel & Eaton (1985) is still NOT OBTAINED and its
absence is still disqualifying; obtaining it is **necessary and not
sufficient**, and the ladder must converge as well.

**On the four T1b rows.** They are recorded here exactly as the rung recorded
them: **PASS as returned by the frozen comparator; every triple
DIVERGENT/STAGNANT; under the binding triple gate adopted for T3/L4 these read
NOT A RESULT.** A comparator's PASS is not overwritten after the fact — Charter
§2d — so the verdict stands as returned and the certificate declines the line.

---

## 4. Planned lines (spine)

The H-2 spine maps to the four DC quantity classes H-6 names. **Every row is
PENDING; nothing below is held.**

| quantity class | DC meaning | rung(s) that will back it | directive | state |
| --- | --- | --- | --- | --- |
| **inlet temperature** | rack-inlet air temperature, the quantity the ASHRAE 27 degC guideline is stated about | **T5** (heated cubes = the rack physic) → **T12** (room-scale validation) | H-2, H-6 | **PENDING** — T5 primary HELD, cost registration pending; T12 ACQUIRE, over $25 |
| **recirculation** | hot air returning to the inlet across the top or ends of a rack | **T5** → **T8** (plume / stratification = the aisle physic) | H-2, H-6 | **PENDING** |
| **stratification height** | the vertical position of the hot/cold interface in the aisle and the room | **T8** → **T12** | H-2, H-6 | **PENDING** — T8 has a partial-EXACT entry rung (Morton–Taylor–Turner plume entrainment) available before its data arrives |
| **transient response** | thermal ride-through: how inlet temperature moves after a CRAC trip or a load step | **T11** (transient conjugate module) | H-5, H-6 | **PENDING** — lumped and 1D transient solutions are closed form; the published transient data is not held |

**The rack-row rung (K2 / F14 K2c) closes the spine** and inherits all four
classes. Its raised-floor primaries are `NOT OBTAINED` in their entirety —
`docs/VALIDATION_INVENTORY.md` records eight papers, every Unpaywall check
`is_oa: false` — so no line of this certificate is backed at rack-row scale
today, and the spec says so rather than leaving the row blank.

---

## 5. What this file does not claim

**Nothing here is a certificate and nothing here is a capability.** Section 2
lists ten lines a minted certificate would be entitled to print today; all ten
come from closed-form references, none is a data-centre quantity, and the four
DC quantity classes in section 4 are all PENDING. **A spec that grew a line
before its rung passed would be the failure H-6 exists to prevent.**
