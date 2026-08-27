# Curriculum item D17 — `Cone_Supersonic` as a 2D WEDGE at M 1.958 (`DAHisaFoam`, inviscid): RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-27 by lane A of the DAFoam team.** The governing document is `PREREGISTRATION.md`
in this directory, frozen before any container started at commit **`2d8796e3`**. **This file does not
revise the pre-registration.** No gate, threshold, cap, band edge or label was altered by this lane.

**Launched by the queue-runner daemon with no agent alive** — `verification/queue/LAUNCH_LOG.tsv`
row `2026-08-27T11:34:40Z dafoam D17_chain 733039 733039 2 180.3 2d8796e3…`. `STATUS.D17_chain` carries
`launcher_rc=0`, **the exit status of the launch argv and not the solver rc**.

---

## 1. Verdict

| row | image | verdict |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` (`sha256:9d45679d…5290f07fc`, `libidwarp.so` md5 `f0fcb488…`) | **`PASS`** |
| **PATCHED** | `dafoam-idwarp-rot:v1` (`sha256:2927768a…dee30f6d35`, `libidwarp.so` md5 `85f59e87…`) | **`PASS`** |

# Item verdict: `PASS`

**This is NOT the registered prediction.** §9 committed *"P5 HIT → SHIPPED `GATE FAIL`, PATCHED
`PASS`, item `GATE FAIL`"*. **P5 MISSED and the item PASSED.** The registered text anticipated exactly
this possibility and told the lab how to read it — §7's *"a split is reported as a split with every
number, never averaged"*. See §6.

**`DAHisaFoam` has now run in this lab.** Registered exposure (a) — *"if its primal does not satisfy
DAFoam's convergence guard, X-S exits non-zero with `Primal solution failed`, the chain STOPS, the
item is `NOT A RESULT`"* — **did not fire**. All five arms exited rc 0 and the density-based HiSA
solver cleared its own primal guard on this box, on the tutorial's options, unmodified.

## 2. The grading path, verified before any number here was believed

`d17_grade.py` on disk hashes **`a940b0ee51c9102bb27dd6aa4516f366`**, identical to the committed blob at
the freeze commit `2d8796e3`; so do `PREREGISTRATION.md`, `d17_xf.py`, `d17_run_arm.sh`,
`d17_chain_driver.sh`, `d17_runScript.py`, `d17_aggregate_memory.py`, `d17_decomposeParDict` and
`d17_cpuset_overlap.py` — nine of nine MATCH. Re-run by this lane on the registered invocation, the
grader returned **json byte-identical** to
`/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic/D17_grade_20260827T130641Z.json`, rc 0.

## 3. The two rows, component by component — objective `CD` only, band D 5.0 % per component

`CL` is a symmetry reading and is never graded (§3(ii) of the frozen document). Components are the
registered subset `shape[0], [1], [3], [4], [5]`; steps {1e-2, 1e-3, 1e-4}, middle-step reference.

| dv | idx | `J_adj` SHIPPED | `J_adj` PATCHED | `d_FD` (`d_ref`) | rel err SHIPPED | rel err PATCHED | SHIPPED | PATCHED |
|---|---|---|---|---|---|---|---|---|
| shape | 0 | `-0.012306679898990102` | `-0.01227420942660536` | `-0.011989896954528456` | 2.6421 % | 2.3713 % | `PASS` | `PASS` |
| shape | 1 | `-0.005409944314451196` | `-0.005415317277883117` | `-0.005378200160693902` | 0.5902 % | 0.6901 % | `PASS` | `PASS` |
| shape | 3 | `-0.0008668285662173739` | `-0.000886944080085996` | `-0.0009122771820191389` | 4.9819 % | 2.7769 % | `PASS` | `PASS` |
| shape | 4 | `-0.09753214987090586` | `-0.09748993001537437` | `-0.0974682542411176` | 0.0656 % | 0.0222 % | `PASS` | `PASS` |
| shape | 5 | `-1.5838904223030261` | `-1.5838542758011367` | `-1.5839007473535949` | 0.0007 % | 0.0029 % | `PASS` | `PASS` |

**SHIPPED: 5 PASS, 0 GATE FAIL, 0 NOT A RESULT, 0 sign flips, aggregate 0.0207 % → band D `PASS`, band E `PASS`.**
**PATCHED: 5 PASS, aggregate 0.0184 % → band D `PASS`, band E `PASS`.**

**`shape[3]` at 4.98 % SHIPPED sits 0.02 percentage points inside a 5.0 % band. It is a PASS by the
frozen band and it is recorded here as a marginal one** — the honest reading is that the weakest
component of this wedge is at the edge of what a 5 % band resolves, and that is consistent with §3(c)'s
registered exposure about noise-limited plateaux at 1e-4. Its plateau held; the component is graded,
not `NOT A RESULT`.

**`CL` symmetry reading — reported, never composed:**

| row | `CL_baseline` | `max abs(J_adj CL)` | `max abs(d_FD CL)` |
|---|---|---|---|
| SHIPPED | `1.4432899320127035e-15` | `3.7174933679093303e-06` | `1.6651178991189397e-05` |
| PATCHED | `1.4432899320127035e-15` | `2.752921943551781e-05` | `1.6651178991189397e-05` |

`CL` is zero by construction for the symmetric wedge at 0° and reads 1.44e-15, i.e. machine zero. The
non-zero `dCL/dshape` entries (3.7e-06 shipped, 2.75e-05 patched) are reported because the frozen text
requires it; **they move no verdict** and none is claimed from them.

## 4. Baselines, divergence and the other gates

`CD_baseline` **`0.26988560705696185`**, `CL_baseline` **`1.4432899320127035e-15`**,
`eta_F` `1.1786127629420662e-12`, mesh **40,000 cells** — the DERIVED count of §0 (2 blocks × 100 × 100
× 1, ×2 by `mirrorMesh`) **confirmed by the run**; G-M2 `PASS`, so the derivation is validated and no
defect of it is disclosed.

**`CD_baseline` 0.26989 against the pre-registered oblique-shock estimate 0.27** (θ = 11.31°,
M 1.958, β ≈ 41.7°, `Mn1` ≈ 1.30, `p2/p1` ≈ 1.82, `Cp` ≈ 0.30, band [0.08, 0.45]). The band was wide;
the agreement is to **0.04 %** of the point. Recorded as a reading, not as a validation gate: the band
is what was registered and the band is what was graded.

Shipped-vs-patched divergence on the adjoint `CD` totals: shape[0] **0.264 %**, shape[1] **0.099 %**,
shape[3] **2.268 %**, shape[4] **0.043 %**, shape[5] **0.002 %**.

| gate | verdict | reading |
|---|---|---|
| G1 completion | `PASS` | 5/5 arms rc 0, `OOMKilled` false, every field from a ledger row; `delivered` absent on MESH → `NOT_MEASURED`, named |
| G-M2 mesh identity | `PASS` | 40,000 == 40,000 (derived count confirmed) |
| G6 dot-product / duality | **NOT MEASURED** | named, never composed |
| G9 toolchain per row | `PASS` | 5/5 arms, three independent readings of the row's `.so` agree |
| G10 caps | `PASS` | every arm under its cap; total **172.833** core-min against ceiling 785.0 |
| G12 placement | `PASS` | `cpuset 12,15` on 5/5; delivered cores 1.982–1.997 of 2; MESH `NOT_MEASURED`, named |
| G-CPUSET (this family's new guard) | no wait | `cpuset_waited_s=0` on all five arms; the overlap poll found no live container sharing cores 12 or 15 |

**No GCI is quoted** — no grid family in this item.

**Planted-zero controls, all live.** Instrument channel `ctrl_zero` `0.0` / `ctrl_planted` `0.617`
against a wanted `0.617` on both images. Grader-level plant seen on both rows, 15 values each, worst
residual **4.27e-17**, files `grader_controls/F_{S,P}_planted.json`.

## 5. Predictions, scored by the comparator against the frozen text

| id | registered claim | outcome |
|---|---|---|
| P1 | mesh is 40,000 cells (DERIVED, never measured before) | **HIT** |
| P2 | `abs(CL)` baseline ≤ 1.0e-3 | **HIT** — 1.44e-15 |
| P3 | `CD` baseline in [0.08, 0.45] | **HIT** — 0.26989 against a 0.27 point |
| P4 | PATCHED row `CD` PASS on ≥ 4 components | **HIT** (5/5) |
| P5 | SHIPPED `shape[0]` outside band D or sign-flipped | **MISS** — 2.64 %, inside the 5.0 % band, `PASS`, no flip |
| P6 | total graded core-min in [60, 450] | **HIT** — 172.833 |
| P6b | MESH wall ≤ 120 s | **HIT** — 10 s |

## 6. The cross-item reading — a SPLIT, reported as a split, with every number

The frozen document (§7, line 80) registered D15 P5, D16 P5 and D17 P5 as **one claim at three Mach
numbers**, and registered in advance how a split is to be read: *"a split is reported as a split with
every number, never averaged."* The reading, on the graded artefacts:

| item | regime | solver | registered P5 component | SHIPPED rel err on `CD` | P5 |
|---|---|---|---|---|---|
| D15 | M 0.288 subsonic | `DARhoSimpleFoam` | `shape[6]` | **44.87 %** | **HIT** |
| D16 | M 0.685 transonic | `DARhoSimpleCFoam` | `shape[6]` | 1.95 % | **MISS** |
| D17 | M 1.958 supersonic | `DAHisaFoam` | `shape[0]` | 2.64 % | **MISS** |

**One HIT, two MISS. This is a SPLIT and it is reported as one.** Neither of the frozen document's two
clean readings — *"HIT on all three = the rotation defect reaches the baseline gradient independent of
regime and solver"*, *"MISS on all three = the shipped row passes at the baseline in every compressible
regime"* — is what the artefacts say.

**What the three items jointly support, stated no more strongly than the numbers allow:** the
shipped-versus-patched split is **real and large at M 0.288** (D15: SHIPPED `GATE FAIL`, 3 of 5 `CD`
components outside band, up to 44.87 %, against a PATCHED row at 0.007–1.66 %); it is **present but
marginal and displaced at M 0.685** (D16: SHIPPED `GATE FAIL` on `shape[0]` at 5.15 % against a 5.0 %
band, and on `CL` `shape[6]` at 41.80 %); and it is **absent on the graded objective at M 1.958**
(D17: both rows `PASS`, shipped-patched divergence ≤ 2.27 % on every component).

**What they do not support, and this lane declines to write:** that the defect "reaches the
compressible solvers" as a general statement, or that it does not. Three items, three geometries in
part, three solver classes, one mesh each, one design point each. **The supervisor's own sweep is owed
before this reading is repeated upward as settled**, and this record states the split rather than a
conclusion drawn from it.

**A confound named, not waved:** D17 is not a like-for-like third point. It changes geometry (a planar
wedge, not the A1 airfoil), FFD block, DV definition (`shape` has 6 thickness functions and no
`patchV`), solver class (density-based HiSA, not SIMPLE), and physics (inviscid Euler, no aoa
variable). A MISS here is therefore weaker evidence against the defect's reach than D16's MISS, which
holds the mesh, the FFD and the DV set fixed against D15 and changes only the Mach number and the
solver variant.

## 7. What this item establishes, and what it does not

**It establishes** the first `DAHisaFoam` result in this lab: a density-based supersonic Euler primal
and its adjoint, run on both toolchain rows, with the baseline `CD` gradient FD-verified on five
components to **0.0007–4.98 %** shipped and **0.002–2.78 %** patched, and a baseline `CD` of 0.26989
that lands on an independently pre-registered oblique-shock estimate. The capability-grid cell
`2D · steady · supersonic`, gradient column, has its first two-row FD-verified reading.

**It does not establish** — quoting the frozen §8 and adding nothing — anything about the shock's
position or strength (no `Cp` is graded), about viscous drag (inviscid), about `CL` (a symmetry
reading), about anything axisymmetric (this is a planar wedge; the `axisym` cell does not move), about
the thickness/volume constraints (no optimiser ran), or about `DAHisaFoam` beyond the tutorial's own
options. No optimiser ran, there is no grid family and no GCI is quoted.

## 8. Cost — actual against the frozen estimate

| arm | ranks | wall s | core-min | cap | predicted point | ratio |
|---|---|---|---|---|---|---|
| MESH | 1 | 10 | 0.167 | 5.0 | 0.3 | 0.557 |
| X-S | 2 | 235 | 7.833 | 90.0 | 12.0 | 0.653 |
| F-S | 2 | 2,272 | 75.733 | 300.0 | 78.0 | 0.971 |
| X-P | 2 | 213 | 7.100 | 90.0 | 12.0 | 0.592 |
| F-P | 2 | 2,460 | 82.000 | 300.0 | 78.0 | **1.051** |
| **total** | | | **172.833** | 785.0 | **180.3** | **0.959** |

Gross = cleaned. **The two F arms are over the 3,600-s stall figure on wall time by the letter — they
are not stalls**: each is a 32-primal FD sweep at ≈ 71–77 wall s per primal, delivered cores held at
1.996–1.997 of 2 throughout, and both reached their registered end with rc 0 and a complete artefact.
Stated rather than waved.

**WASTE: 0.000 core-min** on the arms. **Already spent and billed in §4 of the frozen document and not
hidden here: 3.05 core-min** ($0.0026 DERIVED) of pre-compute image-identity probes, so the item's
full cost is **175.883 core-min = $0.1504 DERIVED**. The arms alone: **$0.1478 DERIVED, NOT MEASURED**
at $0.0513/core-h, c7a.4xlarge, `cost_basis` REPORTED-BY-OWNER (`COMPUTE_BUDGET_CHARTER.md` §5).
Predicted $0.1542 DERIVED.

**Gap attribution: the estimate was right, and it is worth saying WHY rather than banking the 0.959.**
§4 priced a cold HiSA primal at **3.1 core-min** from D7FR's 3.3 at 42,120 cells scaled by 40,000/42,120,
with the explicit assumption *"HiSA's implicit pseudo-time GMRES step is heavier than a SIMPLE
iteration and there are 500 of them against ~1,000 — taken as a wash, stated as the assumption."*
**The wash held.** Measured, the F arms ran 32 primals in 75.73 and 82.00 core-min → **2.37 and 2.56
core-min per primal**, against a modelled 2 baselines × 3.1 + 30 × 3.1 × 0.748 (C-76's warm factor) =
75.9. The X arms came in **at 0.59–0.65 of their point** — the colouring exposure the caps were sized
for (D5's 9.0–27.7 core-min) did not materialise on a structured 2D 5-state mesh; colouring here is
cheap. The 7.5× X caps and 3.8× F caps were runaway guards, not targets, and were never approached.

**The one arm above its point is F-P at 1.051.** F-P ran alone (no live sibling containers in its
aggregate record) and still cost **8.3 % more than F-S**, which ran with two siblings live. So the
difference is not contention: it is the patched IDWarp's own warp cost, and it is the honest per-arm
figure, not noise to absorb.

**Carry forward:** for `DAHisaFoam` on a structured 2D mesh at ~40,000 cells on 2 ranks, price a cold
primal at **2.4–2.6 core-min**, colouring at **≈ 1–2** (not D5's 9–28), and a cold adjoint pair at
**≈ 4–5**. The wash assumption between HiSA's 500 heavier pseudo-steps and SIMPLE's ~1,000 lighter
iterations is **confirmed at this size** and may be reused, with this record cited.

The calibration row is `C-157` in `docs/COST_CALIBRATION.md`.

## 9. Artefacts, all still on disk

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D17-cone-supersonic/`:
`D17_grade_20260827T130641Z.json`, `CHAIN_DONE`, `ledger.txt` (5 `ARM=` rows), `STATUS.chain` and the
five per-arm `STATUS.*`, per-arm `*.inspect.txt` kernel records, `{X,F}-{S,P}/d17_{X,F}.json`,
`grader_controls/F_{S,P}_planted.json`, per-arm `*_cpuset_series.txt`, solver logs (F arms 5.29 MB each)
and memory windows.
