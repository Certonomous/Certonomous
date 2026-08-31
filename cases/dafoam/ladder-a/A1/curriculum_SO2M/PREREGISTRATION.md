# CURRICULUM SO-2M — THE MOMENT-CAP FAMILY ON SO-1's NACA0012: the FD-VERIFIED PITCHING-MOMENT GRADIENT RUNG, VALUE **and** JACOBIAN, ON TWO TOOLCHAIN ROWS — PRE-REGISTRATION, STAGE 1 (FROZEN)

**Version 1.0. FROZEN.** Dated **2026-08-31**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or on completion** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**
Every decision below is `[lab-attributed]`. This document is written in **10-line TEMPLATE form** under the FREEZE CLOCK (Sanaa, `etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md` §1). Anything it still needs lands as a dated amendment **after first fields exist** and may alter no gate, threshold, cap or label.

---

## 1. ITEM, RUNG, AND WHY THIS IS THE ONE THAT IS NEXT

**Item id `SO2M`.** Run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient`. Case dir `cases/dafoam/ladder-a/A1/curriculum_SO2M/`.

Sanaa's SO ladder, verbatim (`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md` §4):

> SO-2 Constraint families on SO-1: thickness/area/volume, lift equality, moment cap — one per rung.

**Three families; two are closed on the record and the third has never been touched.**

1. **thickness / area / volume — CLOSED as a rung.** `curriculum_SO2a` bought `d(thickcon, volcon, rcon)/d(shape)` with an FD table on both rows.
2. **lift equality — RULED NOT AVAILABLE as a new rung, by a frozen document, not by this lane.** `curriculum_SO2a/PREREGISTRATION.md` §0.1(1): the equality constraint is declared inside the SO-1 problem itself (`runScript.py:176`) and its gradient `dCL/dx` is already a first-class graded gate — SO-1a's `G5c`, measured `PASS` at **0.021237769014679053 %** aggregate on the PATCHED row and `GATE FAIL` on the SHIPPED row (`curriculum_SO1a/RESULTS.md:101,103`). Its feasibility **at the optimum** is likewise already gated — SO-1b's `G-CL` and `G-GEO`, and SO-1bR's O/E arms all closed `rc=0` on both rows at 2026-08-31T15:48–16:02Z (`/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/ledger.txt`).
3. **moment cap — OPEN, and it is the ONLY open SO-2 family.** `curriculum_SO2a/PREREGISTRATION.md` §0.1(2), frozen 2026-08-28: *"A MOMENT CAP DOES NOT EXIST IN THIS CASE AND CANNOT BE ADDED WITHOUT CHANGING THE PRODUCER … That is a larger item and it is not first."* It was not first. It is now next, and §8 of that same document records the ladder position it left open: *"Nothing about a moment cap — no moment function exists in this producer."*

**By Sanaa's own per-case pattern — `FD-verified gradient rung -> optimisation rung -> post-optimum verification -> D7R attribution` — the first rung of a family carrying a NEW functional is the FD-verified gradient rung. THIS ITEM RUNS NO OPTIMISER.** The moment *cap* (an inequality on `CMZ` inside a constrained optimisation) is the rung after this one and is not frozen here: a cap on a functional whose Jacobian has never carried an FD table is barred by `DAFOAM_CHARTER.md` §2.

**THE LETTER `b` IS DELIBERATELY NOT TAKEN.** `curriculum_SO2a/PREREGISTRATION.md` §8 reserves the name **SO-2b** for *"feasibility at an optimum"*. This lane does not reuse, renumber or repurpose that name, and does not mint a letter by counting. `SO2M` names the family (moment), which is what Sanaa's sentence names.

## 2. RULE-2 AMENDMENT CONDITION — the run directory that does not exist, and how it was checked

At **2026-08-31T17:18:59Z**, in one invocation and **beside a known positive** (`CLAUDE.md` rule 3; L-400):

* `test -e /home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient` → **ABSENT**; the same reader on SO-2a's run root → **EXISTS**. The absence is a reading of the disk, not of a broken test.
* `grep -l 'ITEM=SO2M'` over every run-root `ledger.txt` → **0 files**; the same reader for `SO2a` → **1 file**.
* A tree scan of `cases/dafoam/ladder-a`, `docs/dafoam` and `verification/queue/dafoam` for `SO2M|SO-2M` → **no hit**, beside a known positive of **39** files matching `SO2a` in `cases/dafoam/ladder-a/A1`. *(The exit code of that scan is NOT cited: it was taken through a pipe into `head` and would be `head`'s rc, not `grep`'s. The zero is cited from the empty output and its known positive, never from the rc.)*

**This item has burned 0 core-min of solver compute, started no container and created no run directory.** Before first compute the gates below are amendable **with the condition stated and checked**; after the first arm container they are CLOSED and only dated addenda that alter no gate, threshold, cap or label may land (`VERIFICATION_CHARTER.md` §2b, §2d).

## 3. GROUND, PRODUCER AND THE ONE DELTA — verified incompressible, SO-1's mesh / FFD / constraints / adjoint unchanged

Capability cell **`2D · steady · incompressible`**, column *gradients computed + FD-verified*. `DASimpleFoam`, Spalart–Allmaras, `U0 = 10.0`, `aoa0 = 5.13918623195176`, `A0 = 0.1`, `rho0 = 1.0`, `primalMinResTol 1.0e-8`, mesh **4,032 cells** regenerated by this item's own `MESH` arm, FFD 5×2×2 → **8 `shape` functions + `patchV` [|U|, aoa]**, geometric constraints and lift equality **declared exactly as the tutorial declares them and not modified**. **np = 1 on every arm** (`DAFOAM_CHARTER.md` §5: a gradient verified at one np is a statement about that np; nothing here is carried to another np).

**THE ONE DELTA, and it is a copy rather than a derivation.** `so2m_runScript.py` = the tutorial's `NACA0012_Airfoil/incompressible/runScript.py` (md5 **`0557da51f6f179f6de865144343c499f`**, the value SO-1a and SO-2a both froze) **plus** the `CMZ` entry of `daOptions["function"]` and the constant `L0 = 1.0`, both copied **verbatim** from the sibling file in the SAME tutorial directory, `runScript_Stability_Not_Working.py` (`:76-85` and `:44`):

```
"CMZ": {"type": "moment", "source": "patchToFace", "patches": ["wing"],
        "axis": [0.0, 0.0, 1.0], "center": [0.25, 0.0, 0.05],
        "scale": -1.0 / (0.5 * U0 * U0 * A0 * L0)}
```

A `so2m_runScript_DELTAS_from_tutorial.diff` is required to show **exactly** these insertions and nothing else; the instrument refuses on any other difference. **The sibling file's name is disclosed, not hidden:** what does not work in it is the **stability-derivative objective** built by forward FD at `:135-146`, which this item does not use and does not import. The `CMZ` block is a plain function declaration of the same shape as the `CD` and `CL` blocks this lab has run scores of times. **That the declaration evaluates at all is a REGISTERED FALSIFIER (§7, P1), not an assumption.**

## 4. ARMS — five, one detached chain, TWO ROWS, np = 1 throughout

| arm | kind | row / image | ranks | task | artefact | marker |
|---|---|---|---|---|---|---|
| **MESH** | SCRIPT | SHIPPED | 1 | the tutorial's own `preProcessing.sh` + `checkMesh` | `MESH/checkMesh.log` | `Mesh OK.` |
| **X-S** | SOLVER | SHIPPED `dafoam/opt-packages:latest` `sha256:9d45679d…f07fc` | 1 | one primal, then `compute_totals(of=[CD, CL, CMZ], wrt=[shape, patchV])` | `X-S/so2m_X.json` | `SO2M_X_WRITTEN` |
| **G-S** | SOLVER | SHIPPED | 1 | 42 primals: 2 baseline (η) + 5 comps × 3 steps × 2 signs + trivial baseline 5 × 2 | `G-S/so2m_F.json` (+ `.jsonl`) | `SO2M_F_WRITTEN` |
| **X-P** | SOLVER | PATCHED `dafoam-idwarp-rot:v1` `sha256:2927768a…30f6d35` | 1 | as X-S | `X-P/so2m_X.json` | `SO2M_X_WRITTEN` |
| **G-P** | SOLVER | PATCHED | 1 | as G-S | `G-P/so2m_F.json` | `SO2M_F_WRITTEN` |

**TWO ROWS, and the rule that makes them mandatory** (`DAFOAM_CHARTER.md` §1, §6, §10): *a DAFoam verdict is two rows — shipped and patched — or it is not a verdict about DAFoam.* One mesh, generated once in the SHIPPED image (mesh generation does not touch IDWarp; D14-M @ `60cfd4c8`). Chain stops at the first non-zero rc and then grades whatever exists; **the grader's own rc is INFRASTRUCTURE and is never the verdict** (L-342).

## 5. GATES, THRESHOLDS, LABELS — all frozen now, vocabulary `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else

* **G1 — the five rule-4 clauses, PRINTED INDIVIDUALLY PER ARM.** C1 rc VALUE (`docker inspect .State.ExitCode`; physics), C2 terminal marker, C3 artefact present, C4 **age guard** (artefact strictly newer than the arm's own `.so2m_age_datum`), C5 no fatal token — **scanned PER FILE AND PER LINE**, with exactly one benign exclusion `^\s*trapFpe:\s`, every exclusion COUNTED AND NAMED on the record, and `Foam::sigFpe::sigHandler` as an extra positive token. The whole-file substring scan that killed SO-1a's grade (`so1a_grade.py:122-125`) is **forbidden here and its absence is checked by an AST detector in both directions**. **R-RC** (Sanaa 2026-08-27 §0): rc VALUE is physics, rc RECORD is infrastructure; an absent record reads `NOT MEASURED` only when C2–C5 all hold, and never when the harness rc reads non-zero. Any clause failing on any arm → **`NOT A RESULT`**, comparator exit 2.
* **G-M2 — mesh identity:** `cells == 4,032` → `PASS`, else **`GATE FAIL`**.
* **G-CMV — the moment functional's own VALUE gate, banded before it is read.** At the baseline design (`shape = 0`, `aoa = aoa0`) the section is the **symmetric** NACA0012 and the reference point is the quarter chord, so thin-airfoil theory puts `Cm_{c/4}` at zero and viscous reality slightly off it. **Registered band: `|CMZ_baseline| ≤ 0.02` → `PASS`, outside → `GATE FAIL`**, with the value and its sign printed either way. The band is deliberately loose enough to survive viscosity and tight enough that a mis-declared reference point, a wrong axis or a wrong `scale` cannot sit inside it. **`CMZ` non-finite or absent from the artefact → `NOT A RESULT`.**
* **G5m — THE BRIGHT LINE, on `d(CMZ)/d(shape, patchV)`, per PAIR and per AGGREGATE.** Bands inherited **by citation, not re-derived**: **band D — per graded pair `|d_FD − J_adj| / |d_FD| ≤ 5.0 %` with the same sign**; **band E — aggregate vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖ ≤ 5.0 %`** (`curriculum_D4/PREREGISTRATION.md:82`, `curriculum_D7FR/PREREGISTRATION.md:228-229`, carried unchanged through SO-1a and SO-2a). A **sign-flipped** pair is `GATE FAIL` whatever its magnitude. The aggregate is named as **the vector-relative norm as printed** and is **never compared against the DAFoam papers' per-component average** (`DAFOAM_CHARTER.md` §2).
* **G-NZ — the structural NON-zero, the mirror of SO-2a's exact-zero gate.** `CMZ` is a FLOW functional, so `d(CMZ)/d(patchV[1])` (angle of attack) must be **non-zero on both the adjoint and the FD side**: `|value| > 1.0e-8` on each, else **`GATE FAIL`**, naming the entry. A reader that returns zeros because it read the wrong key, the wrong slice or an empty tuple fails this gate rather than passing it — which is the opposite failure direction from SO-2a's `G-STRUCT` and is why it is registered here.
* **G-TB — the `DAFOAM_CHARTER.md` §4 trivial baseline, and here the STEP-BASED one IS available.** `CMZ` is produced by an iterative solve, so a step five orders below the registered plateau enters subtractive cancellation. **Registered: the same five components at `h = 1e-8` must FAIL band D. `G-TB PASS` iff at most 1 of 5 components passes band D at the wrong step** (SO-1a's own registered form; it measured **0 of 5** on both rows, `curriculum_SO1a/RESULTS.md:104-105`). **G-TB is composed ONLY onto a row whose `G5m` verdict is `PASS`** — a row that already `GATE FAIL`s needs no trivial baseline to doubt it, and composing one there would convert a real gradient defect into `NOT A RESULT` and hide the finding. G-TB's own verdict is printed on every row either way.
* **G6 — dot-product / duality test and complex step: NOT MEASURED, and the grader prints that sentence beside the verdict rather than a value.** The reason is a measurement, not an omission: AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on BOTH images (`curriculum_AV2/RESULTS.md` §2, 5/5 rows `AnalysisError(... Primal solution failed!)`). `DAFOAM_CHARTER.md` §2 requires this to be SAID.
* **G9 — toolchain identity per row:** the ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print and the artefact's in-process `libidwarp.so` md5 must all name the row's registered toolchain — SHIPPED `f0fcb488e0e98156575cd19548e91663`, PATCHED `85f59e87253e0a71a813f64ca6e4c425`. Mismatch → **`GATE FAIL`**. Identity is an image id and a library hash, never a version string.
* **G10 — caps (§9):** every arm `core_min ≤ its cap`, sum ≤ **79.0**; a crossing is **`GATE FAIL`** and the in-container deadline is the stop. The ratio actual/predicted is printed per arm and lands as a `docs/COST_CALIBRATION.md` row at completion (`CLAUDE.md` rule 12).
* **G11 — OOM hard:** `--memory=4g --memory-swap=4g`; `OOMKilled true` is a G1 refusal, never a re-fire. **G12 — placement:** `cpuset == 9` on every arm; at np = 1 the delivered-cores floor does not apply and is reported as a number, `NOT_MEASURED` where absent.
* **DIVERGENCE shipped-vs-patched** on `d(CMZ)/dx`, per pair, is **reported with its number and never gated**.
* **ITEM VERDICT, composed here and not afterwards:** any refusal or any row `NOT A RESULT` → **`NOT A RESULT`**; else any of G-M2 / G-CMV / G-NZ / G9 / G10 / G12 or any row `GATE FAIL` → **`GATE FAIL`**; else **`PASS`**. `NOT_MEASURED` fields print beside the verdict, never inside it.
* **ROACHE (standing rule 5): THERE IS NO GRID FAMILY IN THIS ITEM — one mesh, 4,032 cells, no refinement triple. NO GCI IS QUOTED, and no row may carry one.**

## 6. THE FD TABLE — components, steps, and the plateau proved PER PAIR

**Components (5):** `shape[0]`, `shape[3]`, `shape[6]` (the LE function), `shape[7]` (the TE function) — SO-1a's and SO-2a's four, so the three items' readings sit on the same components — **plus `patchV[1]`** (angle of attack), which carries `G-NZ`.
**Steps:** `shape` **{1e-2, 1e-3, 1e-4}**; `patchV[1]` **{1e-1, 1e-2, 1e-3}** degrees. **Central differences, both signs → 2 + 5 × 3 × 2 + 10 = 42 primals per G arm.**
**Why these steps, by citation:** `cases/dafoam/ladder-a/A_stepsize_study.md` measured twelve invocations on THIS case (A1, 4,032 cells) and found the curve **flat at 2.5–3.0 % from 1e-4 to 3e-2, cosine 0.99998**, with the primal **FAILING** at 5e-2 and 1e-1. The registered triple lies wholly inside that measured plateau and wholly below the primal-failure region.
**THE PLATEAU IS PROVED PER PAIR, NOT ASSERTED ONCE FOR THE ITEM** (`DAFOAM_CHARTER.md` §2): for each (output, component) pair the **middle** step must agree with **at least one neighbour to 10 %**, else the pair is EXCLUDED as `NO_PLATEAU`. `|d_mid| < 1e-14` is EXCLUDED as `NEAR_ZERO`. A failed FD primal EXCLUDES its pair. **Every exclusion is COUNTED AND NAMED.** Fewer than **2** graded pairs on a row, or more than **75 %** of candidates excluded, reads **`NOT A RESULT`** — a gate that grades a quarter of its own Jacobian is not grading the Jacobian.

## 7. PLANTED CONTROLS — BOTH DIRECTIONS, read back from disk, refusing when blind (standing rule 3)

* **`PLANT = 1.234e-03`.** **Direction A (the reader can see a non-zero):** `CTRL` is a synthetic row, no solve — identical DVs on both sides so every FD entry is exactly `0.0`, and the planted twin moves entry 0 by `PLANT` on the plus side alone so that entry is exactly `PLANT / (2 · CTRL_STEP)` and the rest are still exactly `0.0`. It is **written by the instrument, re-read FROM DISK by the instrument** (which exits 2 if the plant is invisible) and **re-read again from disk by the comparator** (which exits 2 if it is invisible there). It changes a value inside a tuple the reader must traverse in full; **a control that EMPTIES that tuple is REFUSED**, because an empty container is seen by a broken reader too.
* **Direction B (the GATE flips under the plant):** the comparator re-reads a **copy of the real X artefact** with `PLANT` added to one `d(CMZ)/d(shape)` entry and **REFUSES unless `G5m` FLIPS from its live verdict to `GATE FAIL` on that copy**; and a second copy with `d(CMZ)/d(patchV[1])` forced to `0.0` must FLIP `G-NZ` to `GATE FAIL`. **A gate never shown failing is not known to be load-bearing** (L-314).
* Both directions run in the **same invocation** as the verdict they license, and both are printed on the record.

## 8. REGISTERED FALSIFIERS — named predictions that CAN MISS, and the outcome predicted PER ROW

| id | prediction | scored by | what a MISS means |
|---|---|---|---|
| **P1** | the `CMZ` moment function **evaluates at all** on `DASimpleFoam` in both images — the primal completes and `CMZ` is finite in `so2m_X.json` | artefact presence + finiteness | **a MISS is the finding**: the moment functional is unavailable on this solver/build, the moment-cap family is `BLOCKED` on the toolchain, and the SO-2 ladder's third rung is answered in the negative at ~1 core-min. The sibling tutorial's name (`…_Not_Working`) is why this is registered first. |
| **P2** | `\|CMZ_baseline\| ≤ 0.02` at `shape = 0`, `aoa = aoa0` (symmetric section about the quarter chord) | G-CMV | the reference point, axis or scale is not what the copied block declares, **or** the viscous moment on this mesh is far larger than thin-airfoil theory allows — either way a real finding about the functional, not a grading artefact |
| **P3** | `d(CMZ)/d(patchV[1]) ≠ 0` on both sides, and `\|d(CMZ)/d(aoa)\| < \|d(CL)/d(aoa)\|` in the same units-free comparison | G-NZ + a reported number | a MISS on the first clause means the functional is not wired to the flow; a MISS on the second means the section's moment is more `aoa`-sensitive than its lift, which would be a genuine surprise on this case |
| **P4** | **PATCHED row `G5m` PASSES** band D and band E | G5m | a MISS puts the patched toolchain's moment Jacobian in the same class as the shipped one and removes the two-row contrast this item is built on |
| **P5** | **SHIPPED row `G5m` GATE FAILS** — the travelling shipped `GATE FAIL` | G5m | **a MISS would be the more interesting outcome**: it would mean the IDWarp defect that produced SO-1a's shipped `CD` aggregate of **40.481353490548585 %** and its `shape[6]` sign flip (`curriculum_SO1a/RESULTS.md:100`) does **not** reach a moment functional, and the defect's reach would then be a measured property rather than an assumed one |
| **P6** | at most **1 of 5** components passes band D at the deliberately wrong step `h = 1e-8` on each row | G-TB | a MISS withdraws that row's `PASS` (`DAFOAM_CHARTER.md` §4) |

**PREDICTED OUTCOME, WRITTEN BEFORE ANY SOLVER RUNS SO IT CANNOT BE WRITTEN AFTERWARDS: P1, P2, P3, P4, P5 and P6 HIT → PATCHED row `PASS`, SHIPPED row `GATE FAIL`, ITEM VERDICT `GATE FAIL`.** The `GATE FAIL` is **registered as the expected outcome and is not avoided**; the item fails on its weakest link and the patched `PASS` does not carry the row (`curriculum_SO1a/RESULTS.md:33`). *SO-1bR's P2 and P4 both MISSED against a frozen document that had named that possibility in advance; that is the standard these six are written to.*

## 9. COST — core-minutes, caps, and dollars DERIVED

**Anchors are MEASURED core-minutes read from ledgers on this box, not estimates:** SO-1a `F-S 3.583` / `F-P 3.433` core-min for **42 primals** on this case at np = 1 (`/home/ubuntu/certonomous-runs/CURRICULUM-SO1a-…-gradient/ledger.txt`); SO-1a `X-S 1.017` / `X-P 1.200` for one primal + `compute_totals` over **two** functionals; SO-2a `MESH 0.167`, `X 0.333` each row, `G-S 2.367` / `G-P 2.017` for 32 primals (`/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-…-geometric-constraint-gradient/ledger.txt`).

**This item's G arm is SO-1a's F arm exactly — 42 primals, 5 components — so SO-1a's measured F figures are used unmodified.** The X arms add **one further adjoint solve** (a third functional), so SO-1a's measured X is carried with a margin rather than reduced.

| arm | point (core-min) | cap (core-min) | basis |
|---|---|---|---|
| MESH | 0.20 | 5.0 | SO-1a 0.183 / SO-2a 0.167, MEASURED |
| X-S | 1.50 | 12.0 | SO-1a X-S 1.017 MEASURED + one adjoint |
| G-S | 3.60 | 25.0 | SO-1a F-S 3.583 MEASURED |
| X-P | 1.50 | 12.0 | SO-1a X-P 1.200 MEASURED + one adjoint |
| G-P | 3.50 | 25.0 | SO-1a F-P 3.433 MEASURED |
| **total** | **10.30, registered POINT 11.0 carrying margin** | **CEILING 79.0** | — |

**Dollars, DERIVED and NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5): at **$0.0513/core-h, c7a.4xlarge, REPORTED-BY-OWNER** — point **11.0 core-min = 0.18333 core-h = $0.009405**; ceiling **79.0 core-min = 1.31667 core-h = $0.067545**. **Both are far under $25 and therefore pre-authorised — the figure is stated anyway, because a blanket is not a per-item read** (`CLAUDE.md` rules 9 and 12). **An overrun STOPS the run; it does not get a new budget.** At completion the actual/predicted ratio is computed per arm and lands as a row in `docs/COST_CALIBRATION.md` with the gap attributed (contention / waste / misprediction, waste named separately and never absorbed into the ratio).

## 10. NO-LAUNCH BRANCHES (registered BEFORE compute, at ZERO core-min), §18.7's BOUNDED WAIT, AND WHAT STAGE 1 DOES NOT CLAIM

**No-launch branches — each writes its named file and exits with its named rc, and each costs 0.00 core-min:**

| branch | condition | writes | rc | verdict |
|---|---|---|---|---|
| **NL-1 AGGREGATE** | the box's free memory cannot hold this item's 4 g beside the live siblings at the bound | `NOLAUNCH_AGGREGATE.txt` naming the sampled figures and the bound | **6** | **`BLOCKED`** |
| **NL-2 PRODUCER** | `so2m_runScript.py` differs from the tutorial by anything other than the two registered insertions, or the tutorial's md5 is not `0557da51f6f179f6de865144343c499f` | `NOLAUNCH_PRODUCER.txt` with the offending diff hunks | **4** | **`BLOCKED`** |
| **NL-3 ROOT** | the run root already exists, or a live container/driver holds this item's prefix, or a `rc=0` ledger row would be re-fired (`ALREADY_BOUGHT`) | `NOLAUNCH_ROOT.txt` | **3** | **`BLOCKED`** |
| **NL-4 FREEZE** | `so2m_grade.py`'s md5 does not equal the value pinned in the driver at the freeze commit | `NOLAUNCH_FREEZE.txt` | **5** | **`BLOCKED`** |

**§18.7 AGGREGATE-RESOURCE CLAUSE — A BOUNDED WAIT TERMINATING WITH A NON-ZERO rc, NEVER BLOCK-AND-CONTINUE.** The launcher waits **at most 14,400 s** for aggregate memory; on expiry it exits **rc = 6** (NL-1) and the item reads **`BLOCKED`**. It never proceeds after a wait it lost, and it never returns 0 on expiry. **The fraction of the declared program a block would discard is stated here rather than discovered later: an NL-1 at t=0 discards 5 of 5 arms (100 %) at 0.00 core-min; an NL-1 that fires between arms discards only the arms not yet bought, and the ledger's `rc=0` rows are kept, never re-run and never deleted.**

**WHAT STAGE 1 DOES NOT CLAIM, AND WHAT IS OWED (this is a STAGE-1 freeze under the FREEZE CLOCK).** Every **gate, threshold, band, cap, label, cost, control and prediction above is FROZEN by this commit and is closed to change once the first container starts.** **Not frozen here, and OWED as STAGE 2 before any launch:** the instrument `so2m_xm.py` (derived from `curriculum_SO1a/so1a_xf.py` with `of=[CD, CL, CMZ]` and the `CMZ` producer insertion, shipped with its DELTAS diff), `so2m_run_arm.sh`, `so2m_chain_driver.sh`, `so2m_grade.py`, their md5 table, and their driven self-tests including the two planted controls of §7 under **both** `python3` and `python3 -O` (L-332). **The queue entry for this item MUST NOT BE FILED until Stage 2 lands and the driver exists** — a filed entry whose launch argv is absent is recorded LAUNCHED and dies (L-344). Stage 2 lands as a dated amendment that alters no gate, threshold, cap or label.

**This item will NOT establish:** anything at np ≠ 1; anything about an optimum, a moment CAP as an optimisation constraint, or feasibility under one; anything about the other four `shape` functions or `patchV[0]`; any dot-product or complex-step reference (§5 G6); any grid-convergence statement (§5, no grid family, **no GCI**); anything about the RAE2822 transonic half of Sanaa's SO-1 sentence or about any compressible rung — **SO-3b and every Mach-multipoint rung remain behind the D15/D16 shipped-gradient gate by Sanaa's ruling of 2026-08-31T15:13Z and nothing here touches that gate.** It does not re-grade SO-1a, SO-1b, SO-1bR, SO-1c, SO-2a or SO-3a, does not convert any of their labels, and does not edit any frozen file of theirs.
