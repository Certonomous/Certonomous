# Curriculum item D15 — NACA0012 subsonic compressible (M 0.288), FD-vs-adjoint at the baseline design: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-27 by lane A of the DAFoam team.** The governing document is `PREREGISTRATION.md`
in this directory, frozen before any container started at commit **`8fc2bdeb`**. **This file does not
revise the pre-registration.** No gate, threshold, cap, band edge or label was altered by this lane.

**The run was launched by the queue-runner daemon with no agent alive** — `verification/queue/LAUNCH_LOG.tsv`
row `2026-08-27T11:32:30Z dafoam D15_chain 730849 730849 2 28.3 8fc2bdeb…`. `STATUS.D15_chain` carries
`launcher_rc=0`, which is **the exit status of the launch argv and not the solver rc**; the file says so
itself. Every per-arm outcome below is read from the run's own ledger and kernel records.

---

## 1. Verdict

| row | image | verdict |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` (`sha256:9d45679d…5290f07fc`, `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663`) | **`GATE FAIL`** |
| **PATCHED** | `dafoam-idwarp-rot:v1` (`sha256:2927768a…dee30f6d35`, `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425`) | **`PASS`** |

# Item verdict: `GATE FAIL`

This is the registered prediction. The pre-registration §9 committed, before any container started:
*"P1–P4, P6 HIT; P5 HIT → SHIPPED row `GATE FAIL`, PATCHED row `PASS`, item **`GATE FAIL`**"*.

## 2. The grading path, verified before any number here was believed

`d15_grade.py` on disk hashes **`b429ec89e7a738647081783b8b755711`**, identical to the committed blob at
the freeze commit `8fc2bdeb`. So do `PREREGISTRATION.md`, `d15_xf.py`, `d15_run_arm.sh`,
`d15_chain_driver.sh`, `d15_runScript.py`, `d15_aggregate_memory.py` and `d15_decomposeParDict` — eight
of eight MATCH. The chain driver asserted the same md5 before staging and again before grading.

The grader was re-run by this lane on the registered invocation
(`python3 d15_grade.py --root /home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic --out …`)
and returned **json byte-identical** to the in-chain result at
`/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/D15_grade_20260827T114315Z.json`,
rc 0. The verdict is reproducible on the frozen path from the artefacts on disk.

## 3. The two rows, component by component — objective `CD`, band D 5.0 % per component

`d_ref` is the FD value at the middle step of the registered triple (plateau band 10 % against both
neighbours). `rel_err` is `|J_adj − d_ref| / |d_ref|`.

| dv | idx | `J_adj` SHIPPED | `J_adj` PATCHED | `d_FD` (`d_ref`) | rel err SHIPPED | rel err PATCHED | SHIPPED | PATCHED |
|---|---|---|---|---|---|---|---|---|
| shape | 0 | `-0.008102836637285232` | `-0.007221766503489129` | `-0.00721698539479787` | **12.2745 %** | 0.0663 % | `GATE FAIL` | `PASS` |
| shape | 3 | `0.008917268399778` | `0.0092905364130168` | `0.00929694782297874` | 4.0839 % | 0.0690 % | `PASS` | `PASS` |
| shape | 6 | `-0.007790869436592362` | `-0.014133812719678937` | `-0.014132790944809681` | **44.8738 %** | 0.0072 % | `GATE FAIL` | `PASS` |
| shape | 7 | `-0.0002487026407917859` | `-0.00020994801762558475` | `-0.0002065253447147697` | **20.4223 %** | 1.6570 % | `GATE FAIL` | `PASS` |
| patchV | 1 | `0.001959450045064941` | `0.001959450045064941` | `0.001959853718691562` | 0.0206 % | 0.0206 % | `PASS` | `PASS` |

**SHIPPED `CD`: 2 PASS, 3 GATE FAIL, 0 NOT A RESULT, 0 sign flips, aggregate 34.6807 % → band D `GATE FAIL`, band E `GATE FAIL`.**
**PATCHED `CD`: 5 PASS, aggregate 0.0474 % → band D `PASS`, band E `PASS`.**

**G5c on `CL`, the same components:**

| dv | idx | rel err SHIPPED | rel err PATCHED | SHIPPED | PATCHED |
|---|---|---|---|---|---|
| shape | 0 | 0.5806 % | 0.0080 % | `PASS` | `PASS` |
| shape | 3 | 0.4572 % | 0.0069 % | `PASS` | `PASS` |
| shape | 6 | **30.0728 %** | 0.0045 % | `GATE FAIL` | `PASS` |
| shape | 7 | 1.2261 % | 0.0262 % | `PASS` | `PASS` |
| patchV | 1 | 0.0096 % | 0.0096 % | `PASS` | `PASS` |

SHIPPED `CL` aggregate 4.2394 % — inside band E, **outside band D on `shape[6]`** → row `GATE FAIL`.
PATCHED `CL` aggregate 0.0099 % → `PASS`.

**The `patchV[1]` row is the CTRL planted-zero component and it reads 0.0206 % on BOTH images and
`divergence_pct` exactly `0.0` between them** — the two images are byte-identical on the one component
the rotation code cannot touch. That is the control that makes the `shape` divergences evidence.

## 4. Baselines, divergence and the other gates

`CD_baseline` **`0.014600274376560973`**, `CL_baseline` **`0.4228845159564578`**, `eta_F` `1.3010603705509993e-10`,
mesh **4,032 cells** — identical across both rows (G-M2 `PASS`).

Shipped-vs-patched divergence on the adjoint `CD` totals, reported with its number as registered:
shape[0] **10.874 %**, shape[3] **4.018 %**, shape[6] **44.878 %**, shape[7] **15.583 %**, patchV[1] **0.000 %**.

| gate | verdict | reading |
|---|---|---|
| G1 completion (arm-kind-aware, age guard, L-342 field classes) | `PASS` | 5/5 arms rc 0, `OOMKilled` false, every field from a ledger row; `delivered` absent on MESH → `NOT_MEASURED`, named, never composed |
| G-M2 mesh identity | `PASS` | 4,032 == 4,032 |
| G6 dot-product / duality | **NOT MEASURED** | the tutorial exposes no dot-product test; named, never composed |
| G9 toolchain per row | `PASS` | 5/5 arms: ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print and the artefact's in-process md5 all name the row's registered toolchain |
| G10 caps | `PASS` | every arm under its cap; total **10.100** core-min against ceiling 165.0 |
| G12 placement | `PASS` | `cpuset 2,3` on 5/5; delivered cores 1.573–1.982 of 2 where measured; MESH `NOT_MEASURED`, named |

**No GCI is quoted.** There is no grid family in this item; standing rule 5 has no row here.

**Planted-zero controls, all live (rule 3).** Instrument channel: `ctrl_zero` `0.0` and `ctrl_planted`
`0.617` against a wanted `0.617` on BOTH images — the reader was shown able to see a non-zero before its
zero was accepted. Grader-level plant: seen on both rows, 15 values each, worst residual
**6.51e-19** against the planted value, files `grader_controls/F_S_planted.json` and `F_P_planted.json`.

## 5. Predictions, scored by the comparator against the frozen text

| id | registered claim | outcome |
|---|---|---|
| P1 | mesh is 4,032 cells | **HIT** |
| P2 | `CL` baseline in band | **HIT** |
| P3 | `CD` baseline in band | **HIT** |
| P4 | PATCHED row `CD` PASS on ≥ 4 components | **HIT** (5/5) |
| P5 | SHIPPED `shape[6]` outside band D or sign-flipped | **HIT** — 44.87 % against a 5.0 % band |
| P6 | total graded core-min in [12, 80] | **MISS** — 10.100, below the band |
| P6b | MESH wall ≤ 120 s | **HIT** — 10 s |

**P6 is the only miss and it is a cost miss, not a physics miss.** It is scored as a MISS here and
carried into the calibration row; the band is not adjusted.

## 6. What this item establishes, and what it does not

**It establishes** that on the SHIPPED IDWarp the `shape` gradients of a **compressible** solver
(`DARhoSimpleFoam`, M 0.288) disagree with finite differences by up to **44.87 %** at the tutorial's
baseline design, while the same components on the PATCHED image agree to **0.007–1.66 %** — with the
non-`shape` control component identical on both. The capability-grid cell `2D · steady ·
subsonic-compressible`, gradient column, has its first two-row FD-verified reading.

**It does not establish** anything about an optimiser (none ran), about grid convergence (one mesh,
no GCI), about 3D, or about whether the rotation defect is the *only* contributor to the shipped
divergence. It grades the endpoint gradient at one design point on one mesh.

## 7. Cost — actual against the frozen estimate

| arm | ranks | wall s | core-min | cap | predicted point | ratio |
|---|---|---|---|---|---|---|
| MESH | 1 | 10 | 0.167 | 5.0 | 0.3 | 0.557 |
| X-S | 2 | 41 | 1.367 | 20.0 | 4.0 | 0.342 |
| F-S | 2 | 103 | 3.433 | 60.0 | 10.0 | 0.343 |
| X-P | 2 | 52 | 1.733 | 20.0 | 4.0 | 0.433 |
| F-P | 2 | 102 | 3.400 | 60.0 | 10.0 | 0.340 |
| **total** | | | **10.100** | 165.0 | **28.3** | **0.357** |

Gross = cleaned; no arm is near the 3,600-s stall figure. **WASTE: 0.000 core-min** — every arm ran to
its registered end and every artefact was graded. **$0.0086 DERIVED, NOT MEASURED** at $0.0513/core-h,
c7a.4xlarge, `cost_basis` REPORTED-BY-OWNER — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Predicted $0.0242 DERIVED.

**Gap attribution: misprediction of the compressible primal rate, not contention.** §4 adopted a ×2
compressible factor over C-71's incompressible warm primal (0.14 → 0.28 core-min) and priced the F arms
at 32 primals × 0.28 + setup = 10.0 each. Measured, the F arms cost **3.43 and 3.40** — so a warm
`DARhoSimpleFoam` primal on 4,032 cells at np = 2 is **≈ 0.10 core-min**, i.e. the ×2 factor was
**over-conservative by ≈ 2.9×** and the true compressible-over-incompressible factor at this size is
**below 1**, not 2 (np = 2 buys real speed on a mesh this small despite the communication argument).
The X arms show the same: 1.37/1.73 against a 4.0 point priced from C-31's np = 1 measurement.
Contention was present and not limiting — `d16_X-S` and `d17_X-S` were live during F-S and X-P
(launcher aggregate records) and delivered cores stayed at 1.57–1.98 of 2.

**Carry forward:** for `DARhoSimpleFoam` at ~4,000 cells on 2 ranks, price a warm perturbed primal at
**0.10 core-min** and a cold primal + two adjoints + colouring at **1.4–1.8 core-min**, not from C-31's
np = 1 incompressible figure scaled by 2.

The calibration row is `C-154` in `docs/COST_CALIBRATION.md`.

## 8. Artefacts, all still on disk

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/`:
`D15_grade_20260827T114315Z.json` (the graded record), `ledger.txt` (5 `ARM=` rows),
`STATUS.chain` and `STATUS.{MESH,X-S,F-S,X-P,F-P}`, per-arm `*.inspect.txt` kernel records,
`{X,F}-{S,P}/d15_{X,F}.json` (totals and FD endpoints), `grader_controls/F_{S,P}_planted.json`,
per-arm solver logs and `*_h5_window_*.txt` memory windows.

---

## The supervisor's check-3 sweep on the P5 reach claim — added 2026-08-27, dated section, appended

**Lines whose number changed above this section: 0** — this section is appended at the foot and
nothing above it is edited. Proved by byte comparison: the file's first N lines are byte-identical to
the committed blob this section was appended to, N being the blob's own line count.

**This is the DAFoam supervisor's check-3 sweep, not this lane's reading.** `SUPERVISION_CHARTER.md`
§3 makes verification of a big claim before belief a personal supervisor duty that may not be
delegated. The supervisor read every number below from the graded jsons before this text was
written; this lane re-derived each one independently from the same jsons and from the three
`RESULTS.md` tables, and reports the arithmetic as reproduced. **No gate, threshold, band, cap,
label or verdict moves here.** D15 stays `GATE FAIL`, D16 stays `GATE FAIL`, D17 stays `PASS`, and
every registered prediction keeps the outcome its comparator scored.

### The claim under test

The three items registered **one** P5 at three Mach numbers: *does the IDWarp rotation defect reach
the compressible solvers?* The scored outcomes were **HIT / MISS / MISS** at M 0.288 / 0.685 / 1.958.
**The naive reading of that pattern — "bounded to the incompressible path" — is wrong, and so is a
clean monotone-in-Mach story.** Both are refused below by the items' own evidence.

### The signal-to-noise table

**Signal** is the worst shipped-versus-patched divergence on the adjoint `CD` totals,
`divergence_pct = |J_shipped − J_patched| / |J_shipped|`, read from
`divergence_shipped_vs_patched_CD` in each item's grade json. **Noise** is the worst
**PATCHED**-row FD relative error on the same graded objective `CD` — the common-mode error the two
rows share, since both rows are graded against the same FD reference. Both columns are the `CD`
channel; the `CL` channel is stated separately below and is not folded in.

| item | M | solver | worst shipped-vs-patched divergence (SIGNAL) | worst PATCHED-row FD error (COMMON-MODE NOISE) | S/N |
|---|---|---|---|---|---|
| D15 | 0.288 | `DARhoSimpleFoam` | **44.878 %** (`shape[6]`) | 1.657 % (`shape[7]`) | **27.1** |
| D16 | 0.685 | `DARhoSimpleCFoam` | **5.487 %** (`shape[0]`) | 0.528 % (`shape[7]`) | **10.4** |
| D17 | 1.958 | `DAHisaFoam` | 2.268 % (`shape[3]`) | 2.777 % (`shape[3]`) | **0.82** |

`CL`, stated so the `CD` numbers are not reused where they do not reach: D15's patched `CL` worst is
0.0262 %, D16's is **1.6303 %** (`shape[6]`), D17 grades no `CL` at all (symmetry reading).

### The four findings, and nothing beyond them

1. **The defect PERSISTS into the compressible solvers.** The SHIPPED row `GATE FAIL`s at both
   M 0.288 (`DARhoSimpleFoam`) and M 0.685 (`DARhoSimpleCFoam`). This is not an inference from a
   component; it is the two items' own row verdicts.

2. **Its magnitude falls about 8x across that step** — 44.878 % → 5.487 % worst divergence
   (ratio 8.18). Stated as a ratio between two measured points, not as a rate or a trend.

3. **The component it lands on MOVES**: `shape[6]` at M 0.288, `shape[0]` at M 0.685. **This is why
   P5 read MISS at D16 while the row still failed.** P5 was a prediction about a *component*, not
   about the *defect*: the registered falsifier was mis-specified. The row failed, the defect was
   present, and the prediction that was supposed to detect it scored MISS. This is a defect of the
   prediction, not of the item, and it is carried as a lesson rather than as a repaired band.

4. **D17 is NOT DISCRIMINATING and is reported as uninformative.** Its worst divergence (2.268 %) is
   **smaller than its own PATCHED control row's worst FD error** (2.777 %) — S/N **0.82**. Component
   by component, SHIPPED-minus-PATCHED relative error in percentage points reads
   **+0.271 / −0.100 / +2.205 / +0.043 / −0.002** on `shape[0]/[1]/[3]/[4]/[5]`, against a patched row
   that itself carries 2.371 % and 2.777 % on two of those five components. Its SHIPPED `PASS` rests
   on `shape[3]` at **4.982 %** clearing a 5.0 % band by **0.018 percentage points** — a 0.36 %
   relative margin, decided in the third decimal, on a case whose control row is equally elevated.
   **D17's P5 MISS is a statement about D17's FD quality on a shock-containing inviscid case, not
   about the toolchain, and it must not be counted as evidence of absence.**

### What this sweep is not

**Three points on three different geometries is not a Mach sweep.** D17 changes geometry (planar
wedge, not the A1 airfoil), FFD block, DV definition, solver class and physics all at once; D15 and
D16 share the mesh, the FFD, the DV set and the design point. **The D15 → D16 pair is the only clean
comparison in the set — only the Mach number and the solver variant change between them** — and
finding 2's 8x is a statement about that pair and about nothing else. No monotone-in-Mach claim is
made or implied, and two points cannot support one.

**No new compute was spent on this sweep.** Every number is read from artefacts already on disk:
`/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/D15_grade_20260827T114315Z.json`,
`.../CURRICULUM-D16-a1-naca0012-transonic/D16_grade_20260827T114714Z.json`,
`.../CURRICULUM-D17-cone-supersonic/D17_grade_20260827T130641Z.json`. **0.000 core-min.**

### What the sweep changes for D15, specifically

**Nothing in this item's verdict, and one thing in how it is quoted.** D15 remains the sweep's
anchor: the highest signal (44.878 %) against the lowest noise of the three (1.657 %), S/N 27.1, and
the only item whose registered P5 component is also the component the defect lands on. **When D15 is
cited upward, it is cited as one of two clean points (with D16), never as the first point of a Mach
trend.** Its `shape[3]` SHIPPED row at 4.0839 % is inside the band and is a `PASS`; the item's
`GATE FAIL` rests on `shape[0]`, `shape[6]` and `shape[7]`, three components, not one.
