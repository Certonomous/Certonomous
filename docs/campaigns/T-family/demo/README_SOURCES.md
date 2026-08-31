# Source map for the two customer-facing result sheets

**INTERNAL FILE.** This document uses real rung ids, verdict vocabulary and
artifact paths freely. **The two `.tex` files in this directory may not, and do
not** — see the jargon check at the foot.

Prepared by a heat-transfer `lab-lane` at the heat-transfer-supervisor's
dispatch, 2026-08-31, under the DEMO STANDARD v2 output rules R1–R10
(`etc/sessions/2026-08-31T2256Z_sanaa_demo_standard_v2.md`, commit `64589fcc`,
read in full at source).

Deliverables in this directory:

| file | act | state |
|---|---|---|
| `ACT_A_thermal_map_sheet.tex` | A — motor-in-duct thermal map | complete; compiles to **one page**, `pdflatex`, rc 0 |
| `ACT_C_battery_module_sheet.tex` | C — battery module under a takeoff pulse | confidence section complete; module results **reserved and empty** (not run); one page, rc 0 |

Both `.tex` files are self-contained: no external figure, no package beyond a
base TeX Live install. **This box has no `tikz`/`pgfplots`** (`kpsewhich`
returns nothing for `tikz.sty`, `pgf.sty`, `pgfplots.sty`, `siunitx.sty`,
`tcolorbox.sty`, `pict2e.sty`, `multirow.sty`), so Figure 1 of sheet A is drawn
in the native LaTeX `picture` environment with `\qbezier`. Output is vector at
any zoom, which satisfies the house style without a dependency the box cannot
meet.

---

## PART 1 — SHEET A, every user-visible number and where it was verified

Primary source: `docs/campaigns/T-family/CASE3_MAP_RESULTS.md` (the assembled
T23 + T24 map). Secondary: `docs/campaigns/T-family/T23_RESULTS.md`,
`docs/COST_CALIBRATION.md`.

### Table 1 — the sixteen peak temperatures

| sheet value | source | line |
|---|---|---|
| 80 W row: 38.1374 / 29.0795 / 25.5462 / 23.5897 °C | `CASE3_MAP_RESULTS.md` §1 | 118 |
| 155 W row: 59.9609 / 42.3896 / 35.5104 / 31.6747 °C | same | 119 |
| 230 W row: 81.7844 / 55.6997 / 45.4746 / 39.7598 °C | same | 120 |
| 305 W row: 103.6078 / 69.0098 / 55.4389 / 47.8448 °C | same | 121 |
| hottest point (305 W, 10 m/s) = 103.6078 °C | same | 121, 133–134 |
| coolest point (80 W, 40 m/s) = 23.5897 °C | same | 118, 134 |
| margin +96.3922 K to 200 °C at the hottest point | same, §2.1 table, `[MEASURED, T23_RESULTS.md §1]` | 155 |
| air temperature 288 K = 14.85 °C | `T23_RESULTS.md` §2 — `T_inf = 288.0 K` REGISTERED and MEASURED as the inlet `fixedValue` | 101–102 |

**Cross-check performed:** 200 − 103.6078 = 96.3922 ✓. And
103.6078 − 88.758 (the measured rise at 305 W / 10 m/s, `T23_RESULTS.md:106`)
= 14.85 °C, which confirms the 288 K air temperature independently of the line
that states it.

### The uncertainty column — R1's mandatory column, honestly empty

The sheet prints **"not quantified (single mesh level)"** on all four rows and
carries the same statement in plain English in the caveat box.

Authority, quoted from the frozen registration through
`CASE3_MAP_RESULTS.md` §4 (lines 292–305):

> *"T24 registers the PHYSICALITY TIER of the map and NOTHING ELSE … NO ROACHE
> TRIPLE, NO GCI, NO OBSERVED ORDER, NO NUSSELT NUMBER, NO HEAT-BALANCE
> CLOSURE. Every point runs at L1 only."*
> *"A SINGLE MESH LEVEL ADMITS NO TRIPLE. Any Roache classification, GCI or
> observed order quoted from a T24 artifact is a CATEGORY ERROR."*
> *"ALL SIXTEEN POINTS OF THIS MAP RAN AT MESH LEVEL L1 AND ONLY L1 … THERE IS
> NO DISCRETISATION ERROR BAR ON ANY POINT OF IT, AND NONE CAN BE CONSTRUCTED
> FROM WHAT WAS RUN."*

**No number was invented, interpolated or borrowed for this column.** No GCI
from T18 or any other rung is anywhere near sheet A.

### Table 2 — the assumption beat

| sheet value | source | line |
|---|---|---|
| hand estimate, duct correlation: 329.1 / 197.3 / 148.0 / 121.6 °C | `T23_RESULTS.md` §1.2, column "DB predicted" | 79–82 |
| hand estimate, flat plate: 195.1 / 120.3 / 92.4 / 77.4 °C | same, column "FP predicted" | 79–82 |
| solved: 103.6078 / 69.0098 / 55.4389 / 47.8448 °C | same, column "solved" | 79–82 |
| overprediction on the rise, duct: 3.541 / 3.369 / 3.280 / 3.235 | `T23_RESULTS.md` §2 table | 106–109 |
| overprediction on the rise, flat plate: 2.031 / 1.947 / 1.911 / 1.896 | same | 106–109 |
| "high by 1.90× to 3.54×" | same, prose | 111–114 |
| 1.763× spread between the two closures | same | 112 |
| the ratio is taken on the temperature *rise* above 288 K | same, §2 rationale | 96–102 |

**⚠ CORRECTION TO THE BRIEF, CARRIED INTO THE SHEET.** The dispatch said the
overprediction factor *"GROWS WITH AIRSPEED"* and asked for the sentence *"the
error grows as the boundary layer thins with speed."* **At source the factor
SHRINKS with airspeed, monotonically, on both closures:** duct 3.541 → 3.369 →
3.280 → 3.235 and flat plate 2.031 → 1.947 → 1.911 → 1.896 as `U_inf` goes
10 → 20 → 30 → 40 m/s (`T23_RESULTS.md:106–109`). The sheet therefore states
the measured direction — **largest at the lowest airspeed, falling as airspeed
rises** — and the brief's sentence is not used. The range 1.90×–3.54× is
unaffected and is quoted as briefed.

**The one-sentence physical reason on the sheet** ("the hand method collapses
the whole cooling path onto one resistance taken from a fully-developed
correlation, while the real passage is a short annular gap in which the flow is
still developing and the surface removes heat considerably better than the
correlation allows") is **lane-attributed engineering framing of a measured
result, not a measured mechanism.** No mechanism is claimed at source; the
record names none. The sentence asserts only what the correlations are and what
the geometry is, and the directional claim beside it is the measurement.

### Table 3 — the equivalent-power reading

| sheet value | source | line |
|---|---|---|
| 592 W to reach 120 °C at 20 m/s | `CASE3_MAP_RESULTS.md` §2.2 table, "P at 120 °C" | 185 |
| 1043 W to reach 200 °C at 20 m/s | same, "P at 200 °C" | 185 |
| 305 W solved and demonstrated | same, §2.2 prose "The highest power anywhere in the map is 305 W" | 191 |
| labelled **extrapolated**, "not measurements" | same, §2.2, verbatim: *"EVERY FIGURE IN THAT TABLE IS `EXTRAPOLATED`. NOT ONE OF THEM IS A MEASUREMENT"* | 189–194 |

The sheet keeps that distinction in customer language and refuses to present
the implied loads as a rating. §10 item 1 of the source records that the
supervisor's own brief was wrong to call these interpolated; the sheet follows
the corrected reading.

### Figure 1 — the envelope plot

Coordinates are a linear map of the sixteen Table 1 values; the 200 °C limit
line is the customer-stated bound (`CASE3_MAP_RESULTS.md` §1, "B1's 200 °C
engineering bound", line 136). **No uncertainty band is drawn because none
exists.** Straight segments join the four solved airspeeds because
`CASE3_MAP_RESULTS.md` §2.2 (lines 204–208) records that **there is no
registered relation licensing interpolation in airspeed** — so the sheet's
caption says the segments join solved points and claims nothing between them.

### Verification lines — only what exists

| sheet statement | basis |
|---|---|
| "All sixteen points met success criteria fixed before running" | R5's binding translation of PASS. 16/16 PASS at `CASE3_MAP_RESULTS.md` §1/§7 (lines 39, 461–476); gates frozen at `T23_PREREGISTRATION.md` (`fe666fd5`) and `T24_PREREGISTRATION.md` (`b9057489`), lines 10–13 |
| "trends are monotonic and consistent across the whole map" | §1 lines 131–141: linear in power, steeply falling with airspeed, and the sixteen values in §7 confirm no reversal |
| **no grid-refinement check claimed** | §4, lines 302–305 |
| **no energy-conservation check claimed** | §4 deliverable table, "heat balance closed to 1 % — DEFERRED", line 318 |

**Energy closure and grid independence are absent from the sheet entirely.**
Neither is asserted, and neither is hinted at.

### Caveat box

| caveat | source |
|---|---|
| single mesh level, no numerical error bar | §4, lines 302–305 |
| radiation not modelled, **and no bound computed** | §5, lines 380–383, and §4 table line 320 ("radiative upper bound … DEFERRED") |
| buoyancy switched off; forced-convection dominance not established | §5, lines 352–377 |
| representative material properties | the two registrations' declared properties; the map's own framing as a physicality tier (§4) |
| axisymmetric sector idealisation | 5-degree wedge, `docs/COST_CALIBRATION.md` row `C-20260831T183346.079343Z-d971eca8`; `CASE3_MAP_RESULTS.md` §7 note on the wedge, line 500 |
| near-wall resolution exceeds target at 30 and 40 m/s | §4, line 340: max y+ 0.4037 / 0.7515 / 1.0790 / 1.3970 |
| nothing claimed between the four airspeeds | §2.2, lines 204–208 |

**⚠ SECOND CORRECTION TO THE BRIEF.** The dispatch asked for the caveat
"radiation not modelled **and bounded separately**". **At source radiation is
NOT bounded**: §5 line 383, *"the omission does not grow across the map, and it
is not bounded anywhere on it"*, and §4's deliverable table marks the radiative
upper bound `DEFERRED`. The sheet therefore says radiation is not modelled
**and that no bound on its effect has been computed.** Claiming a bound that
does not exist would have been the more serious of the two brief errors.

### Cost line (R8)

| figure | value | source |
|---|---|---|
| upfront estimate, 305 W subset | 123.2 core-min REGISTERED | `docs/COST_CALIBRATION.md:325`, row `C-20260831T183346.079343Z-d971eca8` |
| upfront estimate, 80/155/230 W subset | 360.4 core-min REGISTERED | `CASE3_MAP_RESULTS.md` §8 table, line 514 |
| **sheet's "upfront estimate 483.6 core-minutes"** | 123.2 + 360.4 | **sum of the two registered figures, computed by this lane** |
| actual, 305 W subset | 120.1285 core-min MEASURED | `COST_CALIBRATION.md:325` |
| actual, other twelve | 457.0753 core-min MEASURED | `CASE3_MAP_RESULTS.md` §8, line 517 |
| **sheet's "used 577.2 core-minutes"** | 577.2038 | §8, line 596, stated at source as the sum |
| **sheet's ratio 1.19** | 577.2038 / 483.6 = 1.1936 | **derived by this lane** from the two rows above |
| attribution: machine sharing, twelve-at-once on 16 cores against an estimate calibrated at four-at-once | §8, lines 537–549 | measured penalty 26.7–29.9 % by two matched-band probes |
| derived cost $0.49 | $0.102710 + $0.3908 | `COST_CALIBRATION.md:325` and `CASE3_MAP_RESULTS.md:524` |
| rate $0.0513/core-h, owner-stated not metered | `CLAUDE.md` rule 12; `COMPUTE_BUDGET_CHARTER.md` §5 | the sheet says so in customer language |

---

## PART 2 — SHEET C, every user-visible number and where it was verified

### Section 1 — the confidence beat: the 3-D transient conduction verification

Sources: `verification/runs/T-family/T18_runs/gate_t18.json` and
`verification/runs/T-family/T18_runs/T18_VERDICT_READINESS_AUDIT.md`. **Both
read in full.**

**Per the dispatch, the single-cell lumped rung was NOT used for this beat.**
It has never been graded and no measured percentage exists for it; nothing on
sheet C comes from it.

| sheet value | source | line |
|---|---|---|
| exact 0.6175896496 / 0.8591137894 / 0.5814449853 | `gate_t18.json` `reference` on rows G1/G2/G3 | 106, 129, 152 |
| solved 0.6176037117 / 0.8591831159 / 0.5815192620 | `gate_t18.json` `value_fine` | 111, 134, 157 |
| deviation from exact +0.00228 / +0.00807 / +0.01277 % | `gate_t18.json` `rel_deviation` 2.2769268e-05 / 8.0695348e-05 / 1.2774501e-04, expressed as a percentage | 124, 147, 170 |
| tolerance used 45.5 / 32.3 / 42.6 % | audit "half-band consumed" 0.4554 / 0.3228 / 0.4258 | 199–201 |
| grid-refinement uncertainty 0.0021 / 0.0104 / 0.0154 % | `gate_t18.json` `gci_pct`; audit recomputes each to 0.000e+00 difference | 119/142/165; audit 138–140 |
| observed order 1.9996 / 2.0006 / 2.0130 | `gate_t18.json` `observed_order`; audit recomputes independently, Δ = 0.000e+00 | 118/141/164; audit 115–117 |
| refinement ratio 3.999 / 4.002 / 4.036 vs theoretical 4.000 | audit `d21/d32` column, 3.998926 / 4.001589 / 4.036282 | 115–117, 128–131 |
| mesh levels 20 / 40 / 80 per side; finest 512 000 cells | `gate_t18.json` `N`; `planted_zero_controls.G1.cells_planted` = 512000 | 7–11, 51 |
| Bi = 1.0, Fo = 0.2 | `gate_t18.json` | 5–6 |
| factor of safety 1.25 behind the uncertainty column | `gate_t18.json` `factor_of_safety`; audit confirms it three ways incl. inversion of the published `gci_pct` | 14; audit 142–147 |

**THE R5 TRANSLATION, AND WHICH NUMBER `X` IS.** The sheet says
**"verified against the exact conduction solution to within 0.013 %"** and
states in the same breath that this is **the largest of the three deviations
from the exact value** (0.01277 % on the cooled-face reading), **not an average
and not a tolerance.** Band consumption is reported separately and explicitly
as "used less than half of the tolerance allowed for it before the run (worst
45.5 %)". Both readings of "within X %" are therefore on the sheet, each
labelled for what it is, so no reader can mistake one for the other.

Two facts about this rung that the sheet does **not** claim and must not:
the audit declares no verdict (its own line 3), and `gate_t18.json:4` records a
ceiling — the reference is exact, so this rung can never carry an experimental
comparison. The sheet accordingly claims only agreement with an exact solution
and says nothing about experiment.

### Section 2 — the module description

Source: `verification/runs/T-family/T25_MODULE_runs/T25_MOD_L1/CASE.txt`
(the case's own provenance block) and `build_t25.py`.

| sheet value | source | line |
|---|---|---|
| 8 cells | `CASE.txt` "n cells 8" | 24 |
| 100 mm along the flow | "cell Lx (flow) 0.1 m" | 25 |
| 30 mm thick | "cell Ly (thickness) 0.03 m" | 26 |
| 3 mm channel gap | "channel gap 0.003 m" | 28 |
| 261 mm stack height | "module height 0.261 m, DERIVED: 8*0.03 + 7*0.003" | 29 |
| depth modelled 1.0 m per unit depth | "cell Lz (unit depth) 1.0 m" | 27 |
| 15 W/cell takeoff, 4 W/cell cruise | "P_takeoff 15.0 W/cell", "P_cruise 4.0 W/cell" | 36–37 |
| pulse switch at 60 s, duration 900 s | "pulse switch t = 60.0 s", "duration 900.0 s" | 41–42 |
| initial and coolant temperature 293 K | "T_initial 293.0 K", "T_inf (coolant) 293.0 K" | 34–35 |
| **total heat 34 080 J** | **not stated at source — DERIVED by this lane**: 8 × (15 W × 60 s + 4 W × 840 s) = 8 × 4260 = 34 080 J, arithmetic on the four rows above | — |
| convective coefficient from the stated 8 m/s in a 3 mm gap, derived not measured | "h (channel faces) 53.9 W/m2K DERIVED … declared-representative, NOT measured, NOT a gate" | 43 |

The sheet shows the arithmetic for both derived figures (stack height and total
heat) beneath the table, so a reader can check them without this file.

### The module has not run — and what the sheet says about that

**Measured state of `T25_MOD_L1` on disk:** the case directory holds
`0.orig`, `CASE.txt`, `constant`, `log.blockMesh`, `system` and nothing else.
**No time directories, no `log.solve`, no `STATUS`, no `DONE` marker.** The
mesh was built; the solver never ran.

**⚠ THIRD DEPARTURE FROM THE BRIEF, REPORTED RATHER THAN WRITTEN IN.** The
dispatch says the launch "is held pending an approval". **I could not verify
that at source and it does not match what is on disk.** What is on disk is
`verification/queue/heat-transfer/refused/T25_MOD_L1.REFUSED.txt`, timestamped
2026-08-31T22:25:20Z: the queue entry was **REFUSED by the validator** on two
schema grounds — `prereg_path` empty and `prereg_commit` null where the exact
tag `FEASIBILITY` was required. That is a queue-entry matter, not an approval.
**The sheet states neither version**: R9 forbids any mention of lab process in
user-visible text, so the sheet says only that the module is built and checked
but not yet solved. **The supervisor should rule on which account is correct
before anyone repeats "pending approval" out loud.**

The case is in any event tagged `FEASIBILITY` and its own `CASE.txt` (lines
3–4, 13–17) states that it carries no gate, no band and no verdict, and that
nothing it produces may be graded. Sheet C's reserved frames are consistent
with that: they promise figures, not verdicts.

### The five reserved placeholders

Each is a visibly empty framed box carrying a short "Reserved / Not yet solved"
label, and each is preceded by a LaTeX comment (not user-visible) naming the
data that fills it.

| # | frame on the sheet | LaTeX comment says it is filled by |
|---|---|---|
| 1 | Figure 1 — per-cell temperature histories | eight curves, cell temperature °C against time s, 0–900 s, from the probe at each cell centre |
| 2 | Figure 2 — spread across the module | hottest-minus-coldest cell, K, against time, s |
| 3 | Table 2 — peak and time-to-peak, per cell | eight rows: peak temperature °C, time to peak s, uncertainty (from placeholder 5, or "not quantified" if only one step size is run) |
| 4 | Energy conservation | heat in (34 080 J) against heat stored plus heat removed, both integrated to 900 s, closure in %; R5 wording when filled is recorded in the comment |
| 5 | Time-step check | peak temperature and time-to-peak at two step sizes |

**Nothing is drawn in any of them. No curve, no number, no trend, no
illustrative sketch.**

**On the second step size:** the dispatch calls it "the planned two-step-size
check". The plan exists — the directive
(`etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md` §4.5, lines
434–436) registers a ladder `dt = 0.02 / 0.01 / 0.005 s` at a refined mesh
level — but the as-built feasibility case steps at `dt = 0.5 s`
(`CASE.txt:42`), and **no second step size is fixed for this case.** The sheet
therefore promises "two time-step sizes" and names neither; the LaTeX comment
records exactly this, so nobody later fills the frame with a step size that was
never registered.

### Caveat box

| caveat | source |
|---|---|
| channels not resolved as air flow; a convective boundary condition instead | `CASE.txt` SIMPLIFICATIONS 1, lines 48–58 |
| the spread comes from end cells having one cooled face against the interior cells' two, **not** from coolant heating along the channel | `CASE.txt` "WHAT THE MODULE SPREAD IN THIS RUN ACTUALLY MEANS", lines 67–72 — verbatim: *"It is NOT the coolant-heating-along-the-channel mechanism, which needs the fluid region."* |
| convective coefficient derived from the stated channel flow, not measured | `CASE.txt:43` and SIMPLIFICATION 5, line 65 |
| representative properties, conductivity equal in all directions | `CASE.txt:32` and SIMPLIFICATION 2, lines 59–61 |
| stack ends insulated, no plenum | SIMPLIFICATION 3, lines 61–63 |
| no direct cell-to-cell contact path | SIMPLIFICATION 4, lines 63–64 |
| the confidence check says nothing about the channel airflow | `gate_t18.json:3` — *"SOLID-ONLY 3-D transient conduction; NOT conjugate, NOT a flow case"* |

### Cost line (R8)

| figure | value | source | line |
|---|---|---|---|
| confidence check, upfront estimate | 87.902 core-min | `T18_VERDICT_READINESS_AUDIT.md` cost table, "POINT" total | 353 |
| confidence check, actual | 125.516 core-min | same table, "actual" total | 353 |
| ratio 1.428 | same | | 353 |
| "we said in advance it could be low by up to about 3× and it was low by 1.43×" | audit attribution paragraph | | 355–362 |
| no run hit its ceiling | audit, `capped` column all `no`, total cap 383 core-min | | 349–353 |
| derived $0.107 actual against $0.075 predicted | audit | | 363–364 |
| module run: upfront 1.0 core-min, hard ceiling 10.0 core-min | `verification/queue/heat-transfer/refused/T25_MOD_L1.json`, `cost_core_min_estimate` and `cap_core_min_registered` | | — |
| "the estimate rests on a file-writing rate this configuration has never been measured at" | same file, `cost_basis`: *"The I/O term, not the cell count, is what this estimate is guessing at, and it is a GUESS: this is the lab's first 8-block multi-patch chtMultiRegionFoam case and no measured I/O rate exists for it."* | | — |
| **not yet spent** | the case has no `log.solve` and no `STATUS` on disk | | — |

Note that the audit's own selftest spend of 0.777 core-min (audit line 373) is
**not** folded into the 125.516 figure on the sheet, matching the audit, which
names it separately.

---

## PART 3 — WHAT I COULD NOT VERIFY, STATED PLAINLY

1. **"The factor grows with airspeed" (sheet A brief) — FALSE at source.** It
   shrinks. Corrected in the sheet; see Part 1, Table 2.
2. **"Radiation … bounded separately" (sheet A brief) — NOT SUPPORTED.** No
   radiative bound exists. Corrected in the sheet; see Part 1, caveat box.
3. **"Launch held pending an approval" (sheet C brief) — NOT VERIFIED.** The
   queue record shows a validator refusal on schema grounds. Not written into
   the sheet either way; flagged here for the supervisor.
4. **Total heat 34 080 J is DERIVED, not stated at source.** The arithmetic is
   printed on the sheet.
5. **The 483.6 core-min upfront figure on sheet A is a SUM computed by this
   lane** from two separately registered figures; neither registration states a
   combined estimate. The ratio 1.19 is derived from it.
6. **The one-sentence physical explanation on sheet A is lane-attributed
   framing, not a measured mechanism.** No mechanism is on record.
7. **The second time-step size for the module is not registered anywhere.** The
   directive's ladder is for a different mesh level; the sheet names no value.
8. **Neither sheet was reviewed by the supervisor before I wrote this file.**
   `SUPERVISION_CHARTER.md` §3's four checks are the supervisor's own and none
   is claimed here.

---

## PART 4 — THE JARGON CHECK, RUN ON MY OWN OUTPUT

Command run against both `.tex` files, case-sensitive, before commit:

```
grep -c -E 'T18|T20|T23|T24|T25|Case 3|PASS|GATE|NOT A RESULT|BLOCKED|PENDING|pre-registration|rule |L-|D-|docket|lesson|patch|defect|instrument'
```

**Result: 0 hits in each file, including in the LaTeX comments.** The comments
were kept clean as well, though they are not user-visible.

Two near-misses that were deliberately written around and are worth recording
so a later editor does not reintroduce them:

- `\rule{...}` is used for horizontal rules and for the shaded region. It
  matches `rule` but **not** the searched token `rule ` (with the trailing
  space); it is a LaTeX primitive and is not user-visible text. It is listed
  here so the check's zero is understood rather than assumed.
- The word "patches" was replaced by "channel-facing surfaces" throughout sheet
  C, and "the comparator/marker" language of the sources appears nowhere.

---

## PART 5 — WHAT NEITHER SHEET DOES

- **Neither sheet is sent, filed, uploaded, posted or shown outside this box**
  (`CLAUDE.md` rules 7 and 8). They are repository documents.
- **Neither sheet declares a verdict**, in any vocabulary. Sheet A reports that
  sixteen points met criteria fixed in advance; sheet C reports agreement with
  an exact solution. Neither uses a verdict word.
- **Neither sheet contains a number that was not read from an artifact on
  disk**, except the four derived figures named in Part 3, each of which shows
  its arithmetic.
