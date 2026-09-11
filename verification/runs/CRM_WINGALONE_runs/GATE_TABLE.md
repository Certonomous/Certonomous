# CRM WING-ALONE — REGISTERED GATE RESULTS, ALL THREE LEVELS

Thresholds are quoted from the frozen registration §10 and were not chosen after any result.
Verdict vocabulary is rule 1's, and only rule 1's.

| gate | threshold | **L1 (144,768)** | **L2 (1,158,144)** | **L3 (9,265,152)** |
|---|---|---|---|---|
| **G-M1** max non-orthogonality | <= 70 deg (warn 65-70) | **56.7118 — PASS** | **68.2589 — PASS**, in the 65-70 **warning band** | **79.3672 — 🔴 GATE FAIL** |
| **G-M2** max skewness, boundary faces incl. | <= 4 | **2.54152 — PASS** | **3.22296 — PASS** | **3.10133 — PASS** |
| **G-M3** max aspect ratio | 1000, **ADVISORY** | 153.309 — below advisory | 168.964 — below advisory | 188.853 — below advisory |
| **G-M4** march, `Sl` -> 1.000, min quality & volume **positive at EVERY layer** | all clauses | **🔴 GATE FAIL** — min quality **-0.05046** at layer 3 | **PASS** — min quality **+0.00743**, `Sl` 1.001 | **PASS** — min quality **0.07911**, `Sl` 1.000 |
| **G-M5** nesting: 26 blocks, dims halving, 4 triple- / 20 quad-points | structural | **PASS** | **PASS** | **PASS** |

**Artifacts** (all still on disk):
`L1|L2|L3/log.checkMesh`, `L1|L2|L3/pyhyp.log`, `L1|L2|L3/CONVERT_RC.txt`, `L1|L2|L3/DONE_EXTRUDE`,
`L1|L2|L3/DONE_CHECK`, `L3/foam/constant/polyMesh/sets/nonOrthoFaces`.

## G-M5 in detail — BOTH pairs measured, including the one §9 left open

| pair | blocks | dims exactly halving | **max decimation deviation** | verdict |
|---|---|---|---|---|
| L2 (11,136) -> L1 (2,784) | 26 -> 26 | all 26 | **0.000000e+00** | ALL_26_PASS |
| **L3 (44,544) -> L2 (11,136)** | 26 -> 26 | all 26 | **0.000000e+00** | ALL_26_PASS — **§9's gap, now measured** |

**Topological invariants, all three levels: 4 triple-points and 20 quad-points**, with 1-/2-share
counts 62/471, 130/985, 266/2013 — reproducing §3.3 exactly.

🔴 **THE ZEROS ARE CONTROLLED.** A known perturbation of **1.234e-03** was planted into one node of
one coarse block on **each** pair and read back at **1.234000e-03** both times. The reader is shown
able to see a non-zero, so the zeros are evidence. **The zeros were measured at the full node
resolution of the coarse level — 2,820 and 11,206 unique points respectively** — and say nothing
about any finer resolution than that.

## G-M1: the number that fails, and the number beside it

L3's max is **79.3672 deg**, so **G-M1 GATE FAIL** — the gate is on the max and the max breached.
**Two facts must be reported beside it, and neither changes the verdict:**
- **Only 8 faces out of 27,868,288 exceed 70 deg** (`sets/nonOrthoFaces`), and the **average is
  19.597 deg**.
- 🔴 **`checkMesh`'s OWN built-in check prints `Non-orthogonality check OK`** on this mesh, because
  its internal test is not the lab's. **The lab's registered threshold is what grades this rung.**
  Reporting only checkMesh's "OK" would have passed a mesh the registration fails.

## The trend, which was PREDICTED BEFORE L3 RAN

`L3_PREDICTION_BEFORE_RUN.md` was written while `L3/volumeMesh.xyz` did not exist (verified with a
positive control on the file reader) and predicted **"~77.5 — would BREACH the 70 gate."**
**Measured: 79.3672. The prediction was correct in direction and 2.4 % low in magnitude.**

| | L1 | L2 | L3 | direction |
|---|---|---|---|---|
| G-M1 max non-orth | 56.7118 | 68.2589 | **79.3672** | **worsens, near-linearly (+11.55, +11.11)** |
| G-M1 average | 17.0248 | 18.3436 | 19.597 | worsens slowly |
| G-M2 max skewness | 2.54152 | 3.22296 | 3.10133 | **NOT monotone** |
| checkMesh face-tet errors | 144 | 20 | **4** | **IMPROVES strongly** |
| pyHyp min quality | -0.05046 | +0.00743 | +0.07911 | **IMPROVES** |

🔴 **A SINGLE "QUALITY DEGRADES WITH REFINEMENT" STORY DOES NOT FIT THIS DATA.** Three columns
improve with refinement and one worsens. This is **not** the DPW5 pattern that killed `CRM_M085`
(*every* column worsening), and §1 forbids importing that verdict anyway. **The family has exactly
one failing trend — max non-orthogonality — and it is localised to 8 faces.**

## VERDICTS

- **L1 — `GATE FAIL` (G-M4).** Per §10's verdict column a G-M4 breach makes the level **`BLOCKED`**.
- **L2 — `PASS` on all five registered gates**, with G-M1 in the declared warning band.
- **L3 — `GATE FAIL` (G-M1, 79.3672 > 70).**
- **The three-level family as a nested r = 2 triple — `NOT A RESULT`.** Two of its three members fail
  a registered gate, so it cannot serve as the grid triple a successor flow rung would need.
  **This is a mesh-admission verdict only: no QoI exists under this document (§10B), so no Roache
  triple was computed and no GCI is quoted.**
