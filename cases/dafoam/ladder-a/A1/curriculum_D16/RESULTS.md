# Curriculum item D16 — NACA0012 transonic (M 0.685, `DARhoSimpleCFoam`), FD-vs-adjoint at the baseline design: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-27 by lane A of the DAFoam team.** The governing document is `PREREGISTRATION.md`
in this directory, frozen before any container started at commit **`3ccb0c81`**. **This file does not
revise the pre-registration.** No gate, threshold, cap, band edge or label was altered by this lane.

**Launched by the queue-runner daemon with no agent alive** — `verification/queue/LAUNCH_LOG.tsv`
row `2026-08-27T11:33:35Z dafoam D16_chain 731626 731626 2 40.3 3ccb0c81…`. `STATUS.D16_chain` carries
`launcher_rc=0`, **the exit status of the launch argv and not the solver rc**; per-arm outcomes below
are read from the run's own ledger and kernel records.

---

## 1. Verdict

| row | image | verdict |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` (`sha256:9d45679d…5290f07fc`, `libidwarp.so` md5 `f0fcb488…`) | **`GATE FAIL`** |
| **PATCHED** | `dafoam-idwarp-rot:v1` (`sha256:2927768a…dee30f6d35`, `libidwarp.so` md5 `85f59e87…`) | **`PASS`** |

# Item verdict: `GATE FAIL`

The item verdict matches the registered prediction. **The mechanism does not.** §9 committed
*"P5 HIT → SHIPPED `GATE FAIL`"* on `shape[6]`; **P5 MISSED** and the row failed on a different
component. See §5 and §6.

## 2. The grading path, verified before any number here was believed

`d16_grade.py` on disk hashes **`0b8338b3e483548da3515e79da28762a`**, identical to the committed blob at
the freeze commit `3ccb0c81`; so do `PREREGISTRATION.md`, `d16_xf.py`, `d16_run_arm.sh`,
`d16_chain_driver.sh`, `d16_runScript.py`, `d16_aggregate_memory.py`, `d16_decomposeParDict` — eight of
eight MATCH. Re-run by this lane on the registered invocation, the grader returned **json
byte-identical** to `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/D16_grade_20260827T114714Z.json`,
rc 0.

## 3. The two rows, component by component — objective `CD`, band D 5.0 % per component

| dv | idx | `J_adj` SHIPPED | `J_adj` PATCHED | `d_FD` (`d_ref`) | rel err SHIPPED | rel err PATCHED | SHIPPED | PATCHED |
|---|---|---|---|---|---|---|---|---|
| shape | 0 | `0.02233273145960374` | `0.02362930768551476` | `0.02354559855968774` | **5.1511 %** | 0.3555 % | `GATE FAIL` | `PASS` |
| shape | 3 | `-0.05251875709762791` | `-0.05193530745867652` | `-0.05198729798993468` | 1.0223 % | 0.1000 % | `PASS` | `PASS` |
| shape | 6 | `-0.26926975592222957` | `-0.2742311722207006` | `-0.27462471798355564` | 1.9499 % | 0.1433 % | `PASS` | `PASS` |
| shape | 7 | `0.010877066324133593` | `0.010975991329311898` | `0.010918369557681717` | 0.3783 % | 0.5278 % | `PASS` | `PASS` |
| patchV | 1 | `0.005755233917435056` | `0.005755233917435056` | `0.005743948015809325` | 0.1965 % | 0.1965 % | `PASS` | `PASS` |

**SHIPPED `CD`: 4 PASS, 1 GATE FAIL, 0 sign flips, aggregate 1.9648 % → band D `GATE FAIL` (on `shape[0]`), band E `PASS`.**
**PATCHED `CD`: 5 PASS, aggregate 0.1460 % → band D `PASS`, band E `PASS`.**

**G5c on `CL`, the same components:**

| dv | idx | `J_adj` SHIPPED | `J_adj` PATCHED | `d_FD` | rel err SHIPPED | rel err PATCHED | SHIPPED | PATCHED |
|---|---|---|---|---|---|---|---|---|
| shape | 0 | `1.4749374700022155` | `1.4498934912570502` | `1.4498060758789677` | 1.7334 % | 0.0060 % | `PASS` | `PASS` |
| shape | 3 | `2.2043931555501657` | `2.206433089300235` | `2.2059876267361833` | 0.0723 % | 0.0202 % | `PASS` | `PASS` |
| shape | 6 | `0.1719991470989628` | `0.30036038691943534` | `0.29554229567385626` | **41.8022 %** | 1.6303 % | `GATE FAIL` | `PASS` |
| shape | 7 | `0.7163858930452103` | `0.7227502319397503` | `0.7225232224048472` | 0.8494 % | 0.0314 % | `PASS` | `PASS` |
| patchV | 1 | `0.140747871128196` | `0.140747871128196` | `0.1407690108255366` | 0.0150 % | 0.0150 % | `PASS` | `PASS` |

SHIPPED `CL` aggregate 4.5797 % — inside band E, **outside band D on `shape[6]`** → `GATE FAIL`.
PATCHED `CL` aggregate 0.1758 % → `PASS`.

**`patchV[1]` — the CTRL planted-zero component — reads 0.1965 % (`CD`) and 0.0150 % (`CL`) on BOTH
images, `divergence_pct` exactly `0.0`.** The control that makes the `shape` divergences evidence.

## 4. Baselines, divergence and the other gates

`CD_baseline` **`0.016187719043742013`**, `CL_baseline` **`0.44232916845895787`**,
`eta_F` `1.6635906541218048e-10`, mesh **4,032 cells** (G-M2 `PASS`, both rows identical).

Shipped-vs-patched divergence on the adjoint `CD` totals: shape[0] **5.487 %**, shape[3] **1.111 %**,
shape[6] **1.809 %**, shape[7] **0.901 %**, patchV[1] **0.000 %**.

| gate | verdict | reading |
|---|---|---|
| G1 completion | `PASS` | 5/5 arms rc 0, `OOMKilled` false, every field from a ledger row; `delivered` absent on MESH → `NOT_MEASURED`, named |
| G-M2 mesh identity | `PASS` | 4,032 == 4,032 |
| G6 dot-product / duality | **NOT MEASURED** | named, never composed |
| G9 toolchain per row | `PASS` | 5/5 arms, three independent readings of the row's `.so` agree |
| G10 caps | `PASS` | every arm under its cap; total **15.935** core-min against ceiling 245.0 |
| G12 placement | `PASS` | `cpuset 4,14` on 5/5; delivered cores 1.971–1.989 of 2; MESH `NOT_MEASURED`, named |

**No GCI is quoted** — no grid family in this item.

**Planted-zero controls, all live.** Instrument channel `ctrl_zero` `0.0` / `ctrl_planted` `0.617`
against a wanted `0.617` on both images. Grader-level plant seen on both rows, 15 values each, worst
residual **1.28e-17**, files `grader_controls/F_{S,P}_planted.json`.

## 5. Predictions, scored by the comparator against the frozen text

| id | registered claim | outcome |
|---|---|---|
| P1 | mesh is 4,032 cells | **HIT** |
| P2 | `CL` baseline in band | **HIT** |
| P3 | `CD` baseline in band | **HIT** |
| P4 | PATCHED row `CD` PASS on ≥ 4 components | **HIT** (5/5) |
| P5 | SHIPPED `shape[6]` outside band D or sign-flipped | **MISS** — `shape[6]` on `CD` reads **1.95 %**, inside the 5.0 % band, `PASS` |
| P6 | total graded core-min in [15, 120] | **HIT** — 15.935 |
| P6b | MESH wall ≤ 120 s | **HIT** — 10 s |

## 6. What this item establishes, and what it does not

**It establishes** that the shipped-versus-patched IDWarp split **is present at M 0.685** — the SHIPPED
row fails and the PATCHED row passes, on the same mesh, the same design point and the same FD
reference — but that **it does not land on `shape[6]` in `CD`** as D15 and the incompressible A1 rows
did. On `CD` it lands on `shape[0]` (5.15 % against a 5.0 % band, a marginal crossing); on `CL` it
lands on `shape[6]` and lands hard (41.80 %).

**The registered prediction P5 is recorded as a MISS and is not re-scored.** The frozen text named
`shape[6]` on the graded objective, and `shape[6]` on the graded objective passed. **This is a finding
about the transferability of the D15/A1 component signature across Mach number, and it belongs in the
docket rather than in a repaired band.** The honest statement of what moved: the defect's *magnitude*
redistributes across components with the flow regime, so a component-specific prediction carried over
from another Mach number is not supported by this run.

**It does not establish** anything about an optimiser, grid convergence (one mesh, no GCI), 3D, or
whether the rotation branch is the sole contributor. `transonicPCOption 1` is registered as the
solver's setting; this record makes no claim about its runtime activity beyond G9's toolchain identity.

## 7. Cost — actual against the frozen estimate

| arm | ranks | wall s | core-min | cap | predicted point | ratio |
|---|---|---|---|---|---|---|
| MESH | 1 | 10 | 0.167 | 5.0 | 0.3 | 0.557 |
| X-S | 2 | 62 | 2.067 | 30.0 | 6.0 | 0.345 |
| F-S | 2 | 164 | 5.467 | 90.0 | 14.0 | 0.390 |
| X-P | 2 | 62 | 2.067 | 30.0 | 6.0 | 0.345 |
| F-P | 2 | 185 | 6.167 | 90.0 | 14.0 | 0.440 |
| **total** | | | **15.935** | 245.0 | **40.3** | **0.395** |

Gross = cleaned; no arm near the 3,600-s stall figure. **WASTE: 0.000 core-min.**
**$0.0136 DERIVED, NOT MEASURED** at $0.0513/core-h, c7a.4xlarge, `cost_basis` REPORTED-BY-OWNER
(`COMPUTE_BUDGET_CHARTER.md` §5). Predicted $0.0345 DERIVED.

**Gap attribution: misprediction of the transonic primal rate, contention present and not limiting.**
§4 applied D7FR's cell-scaled figure **directly** — 0.32 core-min per primal at 4,032 cells — and priced
the F arms at 32 primals × 0.32 + 3.8 = 14.0. Measured, the F arms cost **5.47 and 6.17**, so a warm
`DARhoSimpleCFoam` primal here is **≈ 0.13–0.15 core-min**, about **2.3× cheaper** than the linear
cell-scaling from a 42,120-cell np = 4 anchor predicts. The registered exposure — *"a transonic primal
on this coarse mesh may converge more slowly … the F caps carry 6.4× the point for that reason"* —
**did not materialise**: the caps were never approached (6.17 against 90.0). Contention: `d15_F-S`,
`d17_X-S`, `d15_F-P` and `d17_F-S` were live across the D16 arms; delivered cores held at 1.971–1.989
of 2, so contention cost less than 1.5 % and is named, not blamed.

**Carry forward:** linear cell-scaling from a larger, wider-decomposed anchor **overprices** a small
2-rank compressible case by ≈ 2.3×; the per-cell rate improves as the mesh shrinks because fixed
per-iteration overhead amortises differently at 2,016 cells per rank. D16 is ≈ 1.4–1.8× D15 arm for
arm, which is the honest transonic-over-subsonic factor at this size.

The calibration row is `C-156` in `docs/COST_CALIBRATION.md`.

## 8. Artefacts, all still on disk

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/`:
`D16_grade_20260827T114714Z.json`, `ledger.txt` (5 `ARM=` rows), `STATUS.chain` and the five per-arm
`STATUS.*`, per-arm `*.inspect.txt` kernel records, `{X,F}-{S,P}/d16_{X,F}.json`,
`grader_controls/F_{S,P}_planted.json`, per-arm solver logs and memory windows.
