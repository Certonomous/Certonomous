# F3 supersonic exact-theory suite — CONVERSION RESULTS

**Graded 2026-08-25 against the pre-registration frozen at `2bf4915a`, amended `e37d7610`
(pre-compute) and `8ef448a7` (**AMENDMENT 2**, §2d.1 schema repair, frozen BEFORE any
comparator ran). Grading path re-frozen at `48b7812a`, blob `6fea2e1d`.**

## Verdicts — 10 rows over 5 gates

| gate / pair | verdict | deviation | band | triple |
| --- | --- | --- | --- | --- |
| G-F3-1 wedge surface pressure / M2.0_th15 | **NOT A RESULT** | +0.072 % | ±0.5 % | **OSCILLATORY** |
| G-F3-1 / M2.5_th10 | **PENDING** | — | — | fine run never launched |
| G-F3-1 / M3.0_th15 | **PASS** | +0.007 % | ±0.5 % | single level |
| G-F3-2 wedge shock angle / M2.0_th15 | **PASS** | −1.435 % | ±2.0 % | CONVERGING, p = 0.034, **GCI 169.06 %** |
| G-F3-2 / M2.5_th10 | **PENDING** | — | — | fine run never launched |
| G-F3-2 / M3.0_th15 | **PASS** | −0.959 % | ±2.0 % | single level |
| G-F3-3 cone surface pressure | **PASS** | +0.287 % | ±0.5 % | CONVERGING, p = 2.541, GCI 0.044 % |
| G-F3-4 cone shock angle | **GATE FAIL** | **+2.139 %** | **±2.0 %** | CONVERGING, p = 0.800, GCI 4.969 % |
| G-F3-5 diamond wave drag / M2.0_eps7p125 | **PASS** | −0.258 % | ±1.0 % | CONVERGING, p = 6.296, GCI 0.0001 % |
| G-F3-5 / M2.5_eps5 | **PENDING** | — | — | fine run never launched |

**Tally: 5 PASS, 1 GATE FAIL, 1 NOT A RESULT, 3 PENDING.**

**9 planted-zero controls, all passed.** All 12 run entries carry the full four-key schema.

## The three rows that must not be read casually

**G-F3-4 — `GATE FAIL` at +2.139 % against a ±2.0 % band.** It misses by **0.139 percentage
points**, on a CONVERGING triple with GCI 4.969 %. **It is shipped as a documented failure and
is NOT re-posed** (charter §8, L-44). The band was frozen before the number existed; a miss
this narrow is exactly the case a pre-registration exists to keep honest.

**G-F3-2 / M2.0_th15 — `PASS` on the band, and the GCI is 169.06 %.** The verdict is correct
under the frozen rule (rule 5: a CONVERGING triple inside its band is a PASS, GCI printed).
**But the observed order is p = 0.034 — essentially zero — and a GCI of 169 % means the
fine-grid value has effectively no grid support.** The band is satisfied; the *grid* says
almost nothing. **Anyone citing this row must carry the GCI with it.** This is reported, not
gated, because converting it would be re-posing a gate after seeing the answer.

**G-F3-1 / M2.0_th15 — `NOT A RESULT` on an OSCILLATORY triple**, with the band deviation
(+0.072 %) well inside ±0.5 %. **Rule 5 operating in its only permitted direction**: a
non-CONVERGING triple is NOT A RESULT whatever the value says, and the value is printed
beside it rather than quoted as a result.

## The three PENDING rows

`wedge/M2.5_th10/fine`, `diamond/M2.5_eps5/fine` — **never launched.** §7 enforcement point 2:
a wave whose predicted cost does not fit the remaining budget with 20 % headroom is not
launched and its rows grade `PENDING`. Ledger:
`stopped_by: "budget check before wave 6"`. **The cap did its job.**

**This is the state that crashed the first grading attempt** — see AMENDMENT 2 and L-322.

## Runs

**10 of 12 launched, every one `rc = 0` MEASURED** from `RC.txt` via
`setsid bash -c 'CMD; echo $? > RC.txt; sync'`. **No proxy.** No kill, no per-run wall-cap
fire, no relaunch.

## Cost

**33.4177 core-min** (launcher ledger, wall × ranks ÷ 60) against **35.23 predicted** and a
**HARD CAP of 39.5** — `cap_respected: true`, **84.6 % of cap**.

**The grader independently reports 32.8825 core-min**, summing per-case `t_mesh_s + t_run_s +
t_sample_s`. The **0.5352 core-min difference is launcher overhead outside the timed
sections**. The ledger total is the figure of record; both are stated so neither looks like a
correction of the other.

**THE CALIBRATION RATIO IS 1.1290, NOT 0.949.** Computed over **launched runs only** (2,005.0
core-s actual vs 1,775.9 predicted), per the standing rule established at row **C-68**: *a
ratio over a set including unlaunched members is not a calibration ratio.* **Every one of the
ten launched runs exceeded its prediction** (1.01–1.64). The aggregate 0.949 is retained as an
**aggregate** and is never quoted as calibration.

**WASTE: ZERO.** The two unlaunched runs are the budget check refusing work that did not fit —
the cap working, not waste. **CONTENTION: BOUNDED, NOT MEASURED, and known to be
UNDER-COUNTED** (C-68): the box also carried F5b, F11 and a foreign `simpleFoam` in another
team's tree. **Dollars $0.0286 — DERIVED, NOT MEASURED.**

Rows: **C-66** (original), **C-68** (correction).

## Artifacts

`F3_CONVERSION_GRADED.json`, `F3_CONVERSION_RUN_LEDGER.json`, `RC.txt` (rc = 0),
`WATCH_TERMINAL.txt`, `runs/<family>/<pair>/<level>/`. Solver logs gitignored, on disk.
