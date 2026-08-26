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

## ADDENDUM 2026-08-26 — G-F3-2 / M2.0_th15 HELD (cfd-supervisor ruling)

Stamped `2026-08-26T16:05:15Z` (`date -u`). Appended at the foot; lines whose number changed above this section: 0.

(a) The row at line 14 — `G-F3-2 wedge shock angle / M2.0_th15 | PASS | −1.435 % | ±2.0 % | CONVERGING, p = 0.034, GCI 169.06 %` — was graded by the frozen `grade_f3.py`, whose `roache()` carries no order floor: any positive p with monotone values is CONVERGING under it.

(b) The shared instrument `scripts/roache_triple.py` now carries `P_MIN = 0.05` (commit c525c247). Under that floor |p| = 0.034 is classified `DEGENERATE`, a non-CONVERGING class → `NOT A RESULT`, and no GCI is quoted.

(c) This record's own discussion (lines ~33-36 above) already said the grid gives the value no support — "a GCI of 169 % means the fine-grid value has effectively no grid support" — and required anyone citing the row to carry the GCI with it.

(d) The F3 successor re-ran this triple on 2026-08-26 and graded G-F3S-2 `NOT A RESULT` (rule 5 limb (1): coarse and medium NOT_PLATEAUED; the triple OSCILLATORY) — see `verification/runs/F3_runs/successor_triple_2026-08-26/RESULTS.md:18`.

(e) RULING: the row is **HELD** — its `PASS` may not be cited. The printed verdict at line 14 is NOT rewritten, because re-grading a frozen record is reserved to Sanaa (VERIFICATION_CHARTER; CLAUDE.md rule 2). It is placed on her desk with the recommendation that the successor's `NOT A RESULT` supersedes it. Decided `[lab-attributed]` under her silence-is-approval directive, as to the HOLD only.

## ADDENDUM 2026-08-26 — G-F3-2 / M2.0_th15 RE-GRADED under the P_MIN = 0.05 DEGENERATE floor (Sanaa: 'OK for this', e94a19ad)

Stamped `2026-08-26T17:31:34Z` (`date -u`). Appended at the foot, after the HELD addendum above (line 88); **lines whose number changed above this section: 0**. Authority: Sanaa's own words **"OK for this"**, boarded by the chief at `e94a19adde18d49c38d447b55c1d0511f733e5da` (2026-08-26 17:26:59Z, `docs/LAB_STATE.md:1223`), verified by this lane with `git show e94a19ad | grep 'OK for this'` before any file was touched. Executed by a cfd lab-lane at zero compute.

**(a) The original row (line 14), quoted verbatim and struck — never rewritten in place:**

~~`| G-F3-2 wedge shock angle / M2.0_th15 | **PASS** | −1.435 % | ±2.0 % | CONVERGING, p = 0.034, **GCI 169.06 %** |`~~

**(b) The re-graded row:**

| gate / pair | verdict | deviation | band | triple |
| --- | --- | --- | --- | --- |
| G-F3-2 wedge shock angle / M2.0_th15 | **NOT A RESULT** | −1.435 % | ±2.0 % | **DEGENERATE**, \|p\| = 0.034 < P_MIN = 0.05 (`scripts/roache_triple.py`, c525c247) — no GCI quoted |

Fine value 44.692792746510406° against exact 45.343616761855984° (deviation −1.4353 %, inside ±2.0 %) — the band verdict is unchanged; rule 5 turns it to NOT A RESULT because the triple is not CONVERGING. The gate can only turn a PASS into NOT A RESULT, never the reverse.

**(c) Both triples for M2.0_th15, values read from `F3_CONVERSION_GRADED.json` in this directory (`gates/*/M2.0_th15/triple/triple_coarse_medium_fine`):**

| row | coarse | medium | fine | increments c→m, m→f | state under P_MIN = 0.05 | observed order |
|---|---|---|---|---|---|---|
| G-F3-2 wedge shock angle β (deg) | 47.58767882153372 | 46.12330850878531 | 44.692792746510406 | 1.4643703127484144, 1.4305157622749007 (R = 0.9769) | **DEGENERATE** | 0.033745037001710325 |
| G-F3-1 wedge surface pressure p2/p1 | 2.294626109090909 | 2.18680091969697 | 2.196237603787879 | 0.10782518939393881, −0.009436684090908809 (R = −0.0875) | **OSCILLATORY** (unchanged from line 11) | none — no order exists for an OSCILLATORY triple |

No GCI is printed beside either row: neither state is CONVERGING.

**(d) How the re-grade was computed — NOT by the frozen `grade_f3.py` (untouched, blob `6fea2e1d` at `48b7812a`), but by the shared instrument's own function on the three recorded values, in a scratch invocation at `2026-08-26T17:31:34Z` against `scripts/roache_triple.py` blob `78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8` (== the blob at c525c247, == HEAD, == disk):**

    python3 -c "import sys; sys.path.insert(0,'scripts'); import roache_triple as rt
    print('roache_triple.P_MIN =', rt.P_MIN)
    print('G-F3-2/M2.0_th15:', rt.gci_equal(47.58767882153372, 46.12330850878531, 44.692792746510406, 2.0, 2))
    print('G-F3-1/M2.0_th15:', rt.gci_equal(2.294626109090909, 2.18680091969697, 2.196237603787879, 2.0, 2))"

Printed, verbatim:

    roache_triple.P_MIN = 0.05
    G-F3-2/M2.0_th15: {'dim': 2, 'r21': 2.0, 'r32': 2.0, 'e21': 1.4305157622749007, 'e32': 1.4643703127484144, 'fs': 1.25, 'values': (47.58767882153372, 46.12330850878531, 44.692792746510406), 'form': 'equal', 'state': 'DEGENERATE', 'order': 0.033745037001710325}
    G-F3-1/M2.0_th15: {'dim': 2, 'r21': 2.0, 'r32': 2.0, 'e21': -0.009436684090908809, 'e32': 0.10782518939393881, 'fs': 1.25, 'values': (2.294626109090909, 2.18680091969697, 2.196237603787879), 'form': 'equal', 'state': 'OSCILLATORY', 'ratio': -11.426173468900622}

(`r = 2.0` is the record's `refinement_ratio_h`; `dim = 2` is the dimension the frozen grader used for its `p_dim2 = 0.03374503700171001`, which the instrument reproduces to the printed digits. `gci_equal` returns a state and no reason string; the reason is the instrument's rule at `roache_triple.py:262`: `if abs(p) < P_MIN: return dict(common, state="DEGENERATE", order=p)`.)

**(e) Corroborating row — the successor re-ran this triple:** `verification/runs/F3_runs/successor_triple_2026-08-26/RESULTS.md:18` — `G-F3S-2 wedge shock angle | NOT A RESULT | 32.2531525441 | 31.8505922313 | +1.2639 % | ±2.0 % | band PASS | OSCILLATORY | rule 5 limb (1) — coarse and medium NOT_PLATEAUED`; calibration row C-112. Two independent gradings of the wedge shock-angle triple, under two instruments, now agree that the grid gives the value no support.

**(f) The JSON.** `F3_CONVERSION_GRADED.json` → `gates/G-F3-2_wedge_shock_angle/M2.0_th15` keeps its original `"verdict": "PASS"` field **byte-untouched**; a sibling key `"regrade_2026-08-26"` is added beside it carrying verdict, state, p, floor, authority `e94a19ad` and the path of this addendum. Nothing else in the file changes.

**(g) Citing rows at HEAD, each given a dated quote-and-strike note pointing here (appended at the foot of each record under rule 6, lines above unchanged):** `verification/campaign/CFD_STEP_A_RULING_2026-08-25.md` lines 51 and 89; `verification/campaign/F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md` line 350; `verification/runs/F3_runs/conversion_2026-08-24/STEP_A_ABSENT_NOTE_2026-08-25.md` lines 90 and 106. **Not touched, and why:** `docs/COST_CALIBRATION.md` C-66 names `wedge/M2.0_th15` only as a cost line (1.60 / 1.64 ratios), never as a PASS — nothing to strike; `docs/LAB_STATE.md:7613, 7956–7969` — the chief's handoff file, left for the chief; `docs/PHASE2_MOVE_MAP.tsv`, `LANE_REPORT_CONVERSION_BATCH_2026-08-25.md:155`, `rerun_f3.py`, `grade_f3.py`, `instrument.py`, the run ledgers and `result.json` files — paths and inputs, no verdict. **The 2026-07-28 legacy record** (`verification/campaign/F3_supersonic_exact_theory.md:94,108`, `.json` `M2.0_th15.0`) reports a wedge-β `PASS (method-sensitive, documented)` on a **different triple** (1,800 / 7,200 / 28,800 cells, β 47.273 / — / 44.847) from the 2026-07-28 runs, not the conversion triple this authority covers; **not struck**, reported to the supervisor.

**Alters no band, no threshold, no cap. Nothing is sent (rule 7).**
