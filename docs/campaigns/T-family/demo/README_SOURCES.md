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
**REVISED 2026-08-31 — THE FUSED 483.6 FIGURE IS GONE FROM THE SHEET.** It was
this lane's arithmetic sum of two separately registered estimates, and no
combined estimate is registered anywhere. The sheet now reports the two phases
as the two phases they are; every figure below is read from a record, and
nothing on the sheet is a sum this lane invented.

| figure | value | source |
|---|---|---|
| phase 1 (four points at 305 W, four-at-once) — upfront estimate | 123.2 core-min REGISTERED | `docs/COST_CALIBRATION.md:325`, row `C-20260831T183346.079343Z-d971eca8`, column "estimate" |
| phase 1 — actual | 120.1285 core-min MEASURED | same row, "actual" column, from the four `log.solve` `ExecutionTime` lines |
| phase 1 — ratio, sheet prints 0.98 | 0.9751 | same row, ratio column — **registered at source, not derived here** |
| phase 2 (twelve points at 80/155/230 W, twelve-at-once) — upfront estimate | 360.4 core-min REGISTERED | `CASE3_MAP_RESULTS.md` §8 table, line 514 |
| phase 2 — actual | 457.0753 core-min MEASURED | same table, line 517 |
| phase 2 — ratio, sheet prints 1.27 | 1.2683 | same table, line 518 — **stated at source, not derived here** |
| **sheet's "total used 577.2 core-minutes"** | 577.2038 | §8, line 596, stated at source as the sum of the two measured actuals |
| attribution: machine sharing, twelve-at-once on 16 cores against an estimate calibrated at four-at-once | §8, lines 537–549 | measured penalty 26.7–29.9 % by two matched-band probes |
| derived cost $0.49 | $0.102710 + $0.3908 | `COST_CALIBRATION.md:325` and `CASE3_MAP_RESULTS.md:524` |
| rate $0.0513/core-h, owner-stated not metered | `CLAUDE.md` rule 12; `COMPUTE_BUDGET_CHARTER.md` §5 | the sheet says so in customer language |

**WHY SPLIT RATHER THAN LABEL THE SUM.** Both were open under R8, which asks for
compute used and the upfront estimate and does not ask for one fused number.
Splitting is the better read for three reasons, and the third is the decisive
one:

1. Every figure on the sheet then comes from a record. The fused 483.6 and the
   ratio 1.19 derived from it existed nowhere but on that sheet.
2. A reader takes "upfront estimate 483.6" for a budget that was set. None was.
3. **The split carries the information the fused figure destroyed.** Phase 1
   came in at 0.98 and phase 2 at 1.27. The sheet's own next sentence explains
   the overrun as machine sharing — and the two ratios are that explanation,
   visible: the four-at-once phase, the basis the estimate was calibrated on,
   landed on its estimate; the twelve-at-once phase did not. Averaged into
   1.19, the effect is smeared across both phases and the sentence explaining it
   has nothing to point at.

Total *used* is kept, because 577.2038 is stated as a sum at source (§8:596) and
is not this lane's arithmetic. No total *estimate* is printed, because none
exists.

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

**THE MODULE NOW EXISTS AT TWO TIME STEPS** (built 2026-08-31, neither solved):

| case | deltaT | steps to 900 s | built by |
|---|---|---|---|
| `T25_MOD_L1` | 0.5 s | 1800 | `build_t25.py --case-dir ... T25_MOD_L1` |
| `T25_MOD_L1_DT025` | 0.25 s | 3600 | `build_t25.py --case-dir ... T25_MOD_L1_DT025 --delta-t 0.25` |

Every physical row in the table below is shared by both cases and is unchanged.

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

**SUPERVISOR'S RULING, 2026-08-31 — QUESTION CLOSED.** The sheet stays exactly
as written above. The module is built and not yet solved, and **nothing about
queues, validators, permissions or approvals appears in any customer-facing
text** — R9. No explanation is added to the sheet. Two further instructions
carried with the ruling and are recorded here because a later editor will need
them: the solver launch is **denied**, and the refused queue entry's null
`prereg_path` / `prereg_commit` fields **may not be repaired to obtain a
launch** — that is the denied launch by another route. Neither the second case
built today nor any other module case has been queued or launched.

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
| 5 | Time-step check | peak temperature and time-to-peak at 0.5 s and 0.25 s |

**Nothing is drawn in any of them. No curve, no number, no trend, no
illustrative sketch.**

**On the second step size — the gap is CLOSED, and closed by building, not by
weakening the sentence.** The earlier state of this file recorded that the sheet
promised "two time-step sizes" and named neither, because only `dt = 0.5 s`
existed. That is no longer true. `T25_MOD_L1_DT025` was built on 2026-08-31 at
`dt = 0.25 s`, and the sheet now names both sizes. The frame stays reserved and
empty: **naming a step size is not solving at it**, and no number may be written
into that frame until both cases have run.

The directive's own ladder (`etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md`
§4.5, lines 434–436) registers `dt = 0.02 / 0.01 / 0.005 s` **at a refined mesh
level**, which is a different thing and is not what was built. 0.25 s is
**half of the as-built 0.5 s and is chosen by this lane**, for the reason that
halving is what makes the comparison a step-*independence* statement rather than
a comparison of two arbitrary steps. It is a build choice on an ungated
feasibility case, not a registered threshold, and it is not presented as one.

### How the second case was built, and what was checked on it

**Built by the builder, not by hand.** `build_t25.py` took a new `--delta-t`
argument (default `0.5`, so the default invocation is what it always was) and
`DT` became a parameter threaded through `fv_options`, `control_dict` and
`case_txt`. Nothing was copied and hand-edited.

**Reproducibility audit of that change, measured.** The builder was re-run at
default step into a scratch directory and every file diffed against the on-disk
`T25_MOD_L1`: **11 of 13 byte-identical**; the two that differ are
`constant/module/fvOptions` and `CASE.txt`, and both differ **only in comment
and provenance text** — the `fvOptions` diff with comments stripped is **empty**,
and the `CASE.txt` change is an **appended block**, so every original line of
`CASE.txt` keeps its original line number and the citations above still resolve.
`T25_MOD_L1` was **not** rebuilt; no built case was touched.

**The two cases differ in exactly one solver-read entry.** Comments stripped,
all thirteen dictionaries of the two cases were diffed pairwise: twelve are
identical and `system/controlDict` differs on one line, `deltaT 0.5` against
`deltaT 0.25`. Nothing else moved.

**The pulse-table sampling condition is now a guard, not a comment.** The
breakpoint repair rests on the claim that no solver step lands strictly inside
the residual 1 ms ramp between the `59.999` and `60.000` breakpoints. That claim
was previously asserted in a comment and evaluated by nobody. `build_t25.py`
now computes it in exact decimal arithmetic (`Fraction` over the decimal
strings, so it is a statement about the times the solver reaches, not about
binary rounding), refuses to emit a case for which the count is non-zero, and
writes the count into both `fvOptions` and `CASE.txt`.

| deltaT, s | steps strictly inside (59.999, 60.000) |
|---|---|
| 0.5 (the baseline) | **0** |
| **0.25 (the new case)** | **0** |
| 0.1 | 0 |
| 0.01 | 0 |
| 0.001 | 0 |
| 0.0005 | **1** — at 59.9995 |
| 0.0002 | **4** |

The last two rows are the **planted control** (`CLAUDE.md` rule 3): a zero from
a checker never shown able to return non-zero is not evidence. This checker
returns non-zero when non-zero is the truth, and returns 0 at 0.25 s. **The
breakpoint fix survives this step refinement.** It would not survive a step
finer than 1 ms, and the builder now refuses rather than emitting such a case
quietly.

**Every dictionary validated with `foamDictionary`, rc 0 on all 14** —
`system/{controlDict,fvSchemes,fvSolution,blockMeshDict}`,
`system/module/{blockMeshDict,fvSchemes,fvSolution}`,
`constant/{regionProperties,g}`,
`constant/module/{thermophysicalProperties,fvOptions}`,
`0.orig/module/{T,p}`, `constant/module/polyMesh/boundary`. Read back through
`foamDictionary -entry -value` rather than by trusting the writer: `deltaT`
`0.25`, `endTime` `900`, `application` `chtMultiRegionFoam`, `g` `(0 0 0)`, and
the pulse table `((0 5000) (59.999 5000) (60 1333.33) (900 1333.33))` — the
corrected breakpoints. `checkMesh` reports **960 cells**, matching the baseline.

**`constant/g` is present**, 357 bytes, `dimensions [0 1 -2 0 0 0 0]`,
`value (0 0 0)` — verified on disk after the build, not inferred from the
builder having a line that writes it. The builder's own assertion block also
refuses on its absence. This is the check the family paid for once already.

**Neither case is queued and neither is launched.** No solver was invoked.

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
| **the sheet now attributes that 1.0 to the 0.5 s solve specifically** | the record above is for `T25_MOD_L1` and for no other case | | — |
| **"the 0.25 s solve takes twice as many steps"** | 3600 against 1800 to the same 900 s endTime — arithmetic on `deltaT`, and the only claim the sheet makes about the finer case's cost | | — |
| **no estimate is quoted for the 0.25 s solve** | **none exists.** No estimate was registered for it and this lane did not invent one. Doubling 1.0 would have been a guess wearing a record's clothes | | — |
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
3. ~~**"Launch held pending an approval" (sheet C brief) — NOT VERIFIED.**~~
   **CLOSED 2026-08-31 by the supervisor's ruling**: the sheet stays as written,
   nothing about queues, validators, permissions or approvals appears in
   customer-facing text, and no explanation is added. See Part 2.
4. **Total heat 34 080 J is DERIVED, not stated at source.** The arithmetic is
   printed on the sheet.
5. ~~**The 483.6 core-min upfront figure on sheet A is a SUM computed by this
   lane.**~~ **RESOLVED 2026-08-31 — the fused figure is off the sheet.** The
   two phases are reported separately, each estimate and each ratio read from
   its own record. See Part 1.
6. **The one-sentence physical explanation on sheet A is lane-attributed
   framing, not a measured mechanism.** No mechanism is on record. (The word
   "passage" in it was changed to "flow path" — see Part 4.)
7. ~~**The second time-step size for the module is not registered anywhere.**~~
   **CLOSED 2026-08-31 by building the case.** 0.25 s is a lane build choice on
   an ungated feasibility case, not a registered threshold, and is stated as
   such in Part 2. **The frame remains empty: naming the two step sizes is not
   solving at them.**
8. **Neither sheet has been reviewed by the supervisor.**
   `SUPERVISION_CHARTER.md` §3's four checks are the supervisor's own and none
   is claimed here. In particular the diff of `build_t25.py` is a
   measurement-script diff and is the supervisor's to read as a diff.
9. **Neither module case has been solved, and no cost has been incurred by
   either.** Everything reserved on sheet C is still reserved. The only compute
   spent today on this case family is meshing: `blockMesh` on the new case and
   one scratch rebuild for the reproducibility audit, seconds each at 1 rank.

---

## PART 4 — THE JARGON CHECK, RUN ON MY OWN OUTPUT

**RE-RUN 2026-08-31 after the edits above, on FOUR files: both `.tex` sources
and the `pdftotext -layout` extraction of both rendered PDFs.** The rendered
text is checked as well as the source, because what a reader sees is the PDF.

Sweep 1, case-sensitive:

```
grep -E -o 'T18|T20|T23|T24|T25|Case 3|PASS|GATE|NOT A RESULT|BLOCKED|PENDING|pre-registration|rule |L-|D-|docket|lesson|patch|defect|instrument'
```

Sweep 2, case-insensitive — **`permission`, `approval` and `queue` were added
this time**, since a leak there would be an R9 violation of exactly the kind
the supervisor's ruling turns on:

```
grep -E -i -o 'pass|gate|blocked|pending|rung|tier|verdict|prereg|permission|approval|queue'
```

| file | case-sensitive | case-insensitive |
|---|---|---|
| `ACT_A_thermal_map_sheet.tex` | **0** | **1** |
| `ACT_C_battery_module_sheet.tex` | **0** | **0** |
| sheet A, rendered PDF text | **0** | **1** |
| sheet C, rendered PDF text | **0** | **0** |

**`permission`, `approval`, `queue`, `prereg`, `verdict`, `rung`, `tier`,
`blocked` and `pending` return zero everywhere, in both files, source and
rendered.**

**PLANTED CONTROL.** A zero from a checker not shown able to see a non-zero is
not evidence (`CLAUDE.md` rule 3). Both sweeps were run against a planted line
reading `GATE FAIL on T25, see rule 4 and the docket; approval pending in the
queue.` — **4 hits case-sensitive, 4 hits case-insensitive.** The sweeps can see
what they are hunting.

**THE ONE RESIDUAL HIT, NAMED RATHER THAN HIDDEN.** Sheet A's opening line reads
"Conjugate heat transfer, steady, axisymmetric duct sector." **`Conjugate`
contains the substring `gate`.** It is the correct technical name for the
physics being solved and it is the customer's own vocabulary; rewriting it to
dodge a substring would make the sheet worse to read (R10) and would be evasion
of a check rather than compliance with the rule behind it. **It is reported, not
removed.** No internal vocabulary is present anywhere in either file.

One collision WAS removed, because removing it cost nothing: sheet A's phrase
"the real passage" became "the real flow path". `passage` contains `pass`;
`flow path` reads at least as well. Recorded so a later editor does not put
"passage" back.

Two near-misses from the first pass, still standing:

- `\rule{...}` is used for horizontal rules and for the shaded region. It
  matches `rule` but **not** the searched token `rule ` (with the trailing
  space); it is a LaTeX primitive and is not user-visible text. It is listed
  here so the check's zero is understood rather than assumed.
- The word "patches" was replaced by "channel-facing surfaces" throughout sheet
  C, and "the comparator/marker" language of the sources appears nowhere.

**Compile state at the same commit:** `pdflatex -interaction=nonstopmode
-halt-on-error`, **rc 0 and exactly one page for each of the two sheets**
(`pdfinfo` `Pages: 1`). Sheet A briefly went to two pages when the cost
paragraph was split; the prose was tightened rather than the content dropped,
and it is back to one page.

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
