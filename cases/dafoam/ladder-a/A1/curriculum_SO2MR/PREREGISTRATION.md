# CURRICULUM SO-2MR — THE SUCCESSOR TO SO-2M: THE SAME MOMENT-CAP GRADIENT RUNG, RE-REGISTERED WITH A DIRECTION-B PLANT THAT IS **SUFFICIENT BY CONSTRUCTION** — PRE-REGISTRATION, STAGES 1 AND 2 (FROZEN)

**Version 1.0. FROZEN.** Dated **2026-08-31**. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.
**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or on completion** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**
Every decision below is `[lab-attributed]`. **This document freezes STAGE 1 AND STAGE 2 TOGETHER** — unlike SO-2M, whose Stage-2 instruments landed as a later amendment, SO-2MR's instruments already exist, are pinned by md5 in this document's §11 table, and are DRIVEN GREEN before this freeze. Anything this document still needs lands as a dated amendment **after first fields exist** and may alter no gate, threshold, cap or label.

---

## 0. WHY THIS ITEM EXISTS — SO-2M's SOLVE WORKED AND ITS **CONTROL** DID NOT

**`SO-2M` is `NOT A RESULT`, its gates are CLOSED, its verdict stands, and none of its documents are rewritten by this one.** SO-2M's refusal is carried here **verbatim**, never paraphrased into something softer, and SO-2M's `RESULTS.md` remains the record of what happened there.

**What SO-2M measured, and it is a first for this lab.** The chain ran **CLEAN**: `chain=COMPLETE arms_bought=5 of 5`, every arm `rc=0` — `MESH 0.183`, `X-S 1.017`, `G-S 2.017`, `X-P 0.85`, `G-P 2.183` core-min (`curriculum_SO2M/RESULTS.md:185-189`, read from that item's ledger). Registered falsifier **P1 HIT**: `CMZ_baseline = 0.0078407548669119`, finite, with `adjoint.CMZ` present for both `shape` and `patchV`. **`d(CMZ)/dx` exists in this lab for the first time.** The physics did everything that was asked of it.

**What refused, and it refused correctly.** The frozen comparator exited `grader_rc=2` on its own direction-B planted control (`SO2M_grade_20260831T195531Z.json` → `refusal`, reproduced at `curriculum_SO2M/RESULTS.md:50-65`):

    {"REFUSE": "CONTROL", "detail": {"G5m_did_NOT_flip_to_GATE_FAIL_under_the_planted_copy":
     {"d_ref": -0.04976246220706002, "demonstrated": true,
      "direction": "B -- the GATE is shown to FLIP under a plant",
      "flipped": false, "live_verdict": "PASS", "plant": 0.001234,
      "plant_is_sufficient": false,
      "plant_needed_to_cross_band_D": 0.002488123110353001,
      "planted_component": ["shape", 6], "planted_verdict": "PASS", "row": "PATCHED"}}}

**ROOT CAUSE, AND IT IS TRANSFERABLE: AN ABSOLUTE PLANT MAGNITUDE DOES NOT PORT ACROSS FUNCTIONALS.** The same `1.234e-03` is **33.76 %** of the `CD`-scale reference that `SO2a` and `SO-1cR` plant against (`|d_ref| ≈ 0.00365546`) and sails across a 5 % band. Against `CMZ`'s reference — about **14×** larger — it is **2.479781 %** of `|d_ref| = 0.049762462207060022` and **cannot cross a 5.0 % band by construction**: crossing needs `0.0024881231103530011` and the registered plant was short of that by a factor of **2.016307**. The plant was inherited from a `CD`-scale item and registered as a **bare absolute for a functional it had never been sized against**.

**THE COMPARATOR IS NOT DEFECTIVE AND IS NOT RELAXED HERE.** It is the best behaviour on this board: it **refused rather than report a `PASS` from a gate it had not shown able to `GATE FAIL`** — standing rule 3 at full strength — and it printed the exact arithmetic needed to repair itself. **Nothing about it is loosened, and `CMZ` gets no exemption.** Band D stays 5.0 %, band E stays 5.0 %, every gate below is SO-2M's gate at SO-2M's threshold.

**No `VERIFICATION_CHARTER.md` §2d.1 repair exception is reached for or relied on.** SO-2MR is a **successor item that re-runs the program from zero**, not an edit to a closed one. The re-run costs **11.0 core-min ≈ $0.009405** (§9), which is why the honest successor is affordable and the reach for an exception is unnecessary.

## 1. ITEM, RUNG, AND WHAT IS AND IS NOT NEW

**Item id `SO2MR`.** Run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO2MR-a1-naca0012-moment-gradient`. Case dir `cases/dafoam/ladder-a/A1/curriculum_SO2MR/`.

The rung, the ladder position and the justification are **SO-2M's, carried unchanged**: Sanaa's SO ladder (`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md` §4) names *"SO-2 Constraint families on SO-1: thickness/area/volume, lift equality, moment cap — one per rung"*; thickness/area/volume is closed by `curriculum_SO2a`, lift equality was ruled not-a-new-rung by that same frozen document's §0.1(1), and **moment cap is the one open family**. This item is the **FD-verified gradient rung** of that family and **RUNS NO OPTIMISER**. `curriculum_SO2M/PREREGISTRATION.md` §1 is the argument and it is cited, not restated.

**WHAT IS NEW IN SO-2MR — the complete list, and it is ONE substantive item.**

1. **The direction-B plant is registered as a RULE RELATIVE TO THE QUANTITY IT PERTURBS, with `K` fixed at freeze** (§7). This is the only change to any control, gate, threshold or instrument behaviour.
2. **A freeze-time SUFFICIENCY LEG, driven RED**, which reproduces SO-2M's refusal from SO-2M's own recorded `d_ref` and then shows the new rule clearing the same number (§7, §11).
3. **The item-token rename** `SO-2M → SO-2MR`, `SO2M → SO2MR`, `so2m → so2mr`, performed mechanically by `so2mr_derive_from_so2m.sh` with a **negative assertion** (18 sibling-item citation tokens counted on both sides and required equal, so the rename cannot eat a quotation) and a **positive assertion** (no parent token survives in any derived file).
4. **A re-pin of `MD5_LAUNCHER`, `MD5_GRADER` and `MD5_XM`** (§11). These were inherited through the rename and were **stale the moment the rename ran** — the rename rewrites the bytes it pins. Left as inherited, this item's own **NL-4 FREEZE** branch would have refused its first arm.

**NOTHING ELSE MOVES.** Band D 5.0 %, band E 5.0 %, `G-CMV ≤ 0.02`, `G-NZ` at `1.0e-8`, `G-TB` at `h = 1e-8` on all five components composed **only** onto a `PASS` row, `G6 NOT MEASURED`, **no grid family and no GCI**, **two rows**, five arms, np = 1, and the registered predicted outcome **PATCHED `PASS` / SHIPPED `GATE FAIL` / ITEM `GATE FAIL`** are all SO-2M's, carried unchanged and re-frozen here.

## 2. RULE-2 FREEZE CONDITION — the run directory that does not exist, and how it was checked

At **2026-08-31T22:15:13Z**, in one invocation and **beside a known positive** (`CLAUDE.md` rule 3; L-400):

* `test -e /home/ubuntu/certonomous-runs/CURRICULUM-SO2MR-a1-naca0012-moment-gradient` → **ABSENT**; the same reader on **SO-2M's** run root → **EXISTS**. The absence is a reading of the disk, not of a broken test.
* `grep -l 'ITEM=SO2MR'` over every run-root `ledger.txt` → **0 files**; the same reader for `ITEM=SO2M` → **1 file**.
* Queue entries naming `SO2MR` anywhere under `verification/queue/dafoam/` → **0**; the same lister for `SO2M_chain.json` → **1**.
* `docker ps -a` filtered on the `so2mr_` container prefix → **0 containers**, against 19 containers visible to the same lister on this box.

**This item has burned 0 core-min of solver compute, started no container and created no run directory.** Independently re-asserted by the pin selftest's own legs `(o0)`, `(z3)` and `(z4)` at 2026-08-31T22:14:52–22:14:56Z, which additionally **refuse to run at all if the run root exists**. After the first arm container the gates below are CLOSED and only dated addenda that alter no gate, threshold, cap or label may land (`VERIFICATION_CHARTER.md` §2b, §2d).

**A note on what "frozen" means for the instruments.** Until this commit **not one file in this case directory was tracked at `HEAD`** (`git ls-files` on the directory returned nothing). The comment repairs and the re-pin recorded in §11 were therefore **pre-freeze edits to unfrozen, untracked files, not amendments to frozen ones** — `CLAUDE.md` rule 6 is not reached and no amendment is owed for them. From this commit forward, every file in the §11 table is frozen and any departure is a dated amendment appended at the foot with a version bump.

## 3. GROUND, PRODUCER AND THE ONE DELTA — verified incompressible, SO-1's mesh / FFD / constraints / adjoint unchanged

Carried from `curriculum_SO2M/PREREGISTRATION.md` §3 **unchanged and by citation**: capability cell **`2D · steady · incompressible`**, column *gradients computed + FD-verified*; `DASimpleFoam`, Spalart–Allmaras, `U0 = 10.0`, `aoa0 = 5.13918623195176`, `A0 = 0.1`, `rho0 = 1.0`, `primalMinResTol 1.0e-8`, mesh **4,032 cells** regenerated by this item's own `MESH` arm, FFD 5×2×2 → **8 `shape` functions + `patchV` [|U|, aoa]**, geometric constraints and lift equality **declared exactly as the tutorial declares them and not modified**. **np = 1 on every arm** (`DAFOAM_CHARTER.md` §5: a gradient verified at one np is a statement about that np).

**THE ONE PRODUCER DELTA, and it is a copy rather than a derivation.** `so2mr_runScript.py` = the tutorial's `NACA0012_Airfoil/incompressible/runScript.py` (md5 **`0557da51f6f179f6de865144343c499f`**, the value SO-1a, SO-2a and SO-2M all froze) **plus** the `CMZ` entry of `daOptions["function"]` and the constant `L0 = 1.0`, both copied **verbatim** from the sibling file in the SAME tutorial directory, `runScript_Stability_Not_Working.py` (`:76-85` and `:44`):

```
"CMZ": {"type": "moment", "source": "patchToFace", "patches": ["wing"],
        "axis": [0.0, 0.0, 1.0], "center": [0.25, 0.0, 0.05],
        "scale": -1.0 / (0.5 * U0 * U0 * A0 * L0)}
```

`so2mr_runScript_DELTAS_from_tutorial.diff` shows **exactly** these insertions and nothing else, and **NL-2 PRODUCER computes the diff rather than asserting it** (§10). **The sibling file's name is disclosed, not hidden:** what does not work in it is the **stability-derivative objective** built by forward FD at `:135-146`, which this item does not use and does not import. **SO-2M has now MEASURED that this declaration evaluates** — `CMZ_baseline = 0.0078407548669119`, finite, on both images — so P1 below is re-registered as a falsifier that has already HIT once and must hit again on this item's own artefacts, never as an inherited assumption.

## 4. ARMS — five, one detached chain, TWO ROWS, np = 1 throughout

| arm | kind | row / image | ranks | task | artefact | marker |
|---|---|---|---|---|---|---|
| **MESH** | SCRIPT | SHIPPED | 1 | the tutorial's own `preProcessing.sh` + `checkMesh` | `MESH/checkMesh.log` | `Mesh OK.` |
| **X-S** | SOLVER | SHIPPED `dafoam/opt-packages:latest` `sha256:9d45679d…f07fc` | 1 | one primal, then `compute_totals(of=[CD, CL, CMZ], wrt=[shape, patchV])` | `X-S/so2mr_X.json` | `SO2MR_X_WRITTEN` |
| **G-S** | SOLVER | SHIPPED | 1 | 42 primals: 2 baseline (η) + 5 comps × 3 steps × 2 signs + trivial baseline 5 × 2 | `G-S/so2mr_F.json` (+ `.jsonl`) | `SO2MR_F_WRITTEN` |
| **X-P** | SOLVER | PATCHED `dafoam-idwarp-rot:v1` `sha256:2927768a…30f6d35` | 1 | as X-S | `X-P/so2mr_X.json` | `SO2MR_X_WRITTEN` |
| **G-P** | SOLVER | PATCHED | 1 | as G-S | `G-P/so2mr_F.json` | `SO2MR_F_WRITTEN` |

**TWO ROWS, and the rule that makes them mandatory** (`DAFOAM_CHARTER.md` §1, §6, §10): *a DAFoam verdict is two rows — shipped and patched — or it is not a verdict about DAFoam.* One mesh, generated once in the SHIPPED image (mesh generation does not touch IDWarp; D14-M @ `60cfd4c8`). Chain stops at the first non-zero rc and then grades whatever exists; **the grader's own rc is INFRASTRUCTURE and is never the verdict** (L-342). **G-ROW**: the launcher derives the row TWICE — once from the image digest, once from the arm name — and refuses `rc=4` when the two disagree; that cross-check is DRIVEN in both directions by `so2mr_pin_selftest.sh`, not asserted (SO-1c lost a run to a row-derivation safety that was believed rather than exercised).

## 5. GATES, THRESHOLDS, LABELS — all frozen now, vocabulary `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else

**Every gate in this section is SO-2M's gate at SO-2M's threshold. Not one is loosened, tightened, renamed or removed.**

* **G1 — the five rule-4 clauses, PRINTED INDIVIDUALLY PER ARM.** C1 rc VALUE (`docker inspect .State.ExitCode`; physics), C2 terminal marker, C3 artefact present, C4 **age guard** (artefact strictly newer than the arm's own `.so2mr_age_datum`), C5 no fatal token — **scanned PER FILE AND PER LINE**, with exactly one benign exclusion `^\s*trapFpe:\s`, every exclusion COUNTED AND NAMED on the record, and `Foam::sigFpe::sigHandler` as an extra positive token. The whole-file substring scan that killed SO-1a's grade (`so1a_grade.py:122-125`) is **forbidden here and its absence is checked by an AST detector in both directions**. **R-RC** (Sanaa 2026-08-27 §0): rc VALUE is physics, rc RECORD is infrastructure; an absent record reads `NOT MEASURED` only when C2–C5 all hold, and never when the harness rc reads non-zero. Any clause failing on any arm → **`NOT A RESULT`**, comparator exit 2.
* **G-M2 — mesh identity:** `cells == 4,032` → `PASS`, else **`GATE FAIL`**.
* **G-CMV — the moment functional's own VALUE gate, banded before it is read.** At the baseline design (`shape = 0`, `aoa = aoa0`) the section is the **symmetric** NACA0012 and the reference point is the quarter chord, so thin-airfoil theory puts `Cm_{c/4}` at zero and viscous reality slightly off it. **Registered band: `|CMZ_baseline| ≤ 0.02` → `PASS`, outside → `GATE FAIL`**, with the value and its sign printed either way. **`CMZ` non-finite or absent from the artefact → `NOT A RESULT`.**
* **G5m — THE BRIGHT LINE, on `d(CMZ)/d(shape, patchV)`, per PAIR and per AGGREGATE.** Bands inherited **by citation, not re-derived**: **band D — per graded pair `|d_FD − J_adj| / |d_FD| ≤ 5.0 %` with the same sign**; **band E — aggregate vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖ ≤ 5.0 %`** (`curriculum_D4/PREREGISTRATION.md:82`, `curriculum_D7FR/PREREGISTRATION.md:228-229`, carried unchanged through SO-1a, SO-2a and SO-2M). A **sign-flipped** pair is `GATE FAIL` whatever its magnitude. The aggregate is named as **the vector-relative norm as printed** and is **never compared against the DAFoam papers' per-component average** (`DAFOAM_CHARTER.md` §2).
* **G-NZ — the structural NON-zero.** `CMZ` is a FLOW functional, so `d(CMZ)/d(patchV[1])` (angle of attack) must be **non-zero on both the adjoint and the FD side**: `|value| > 1.0e-8` on each, else **`GATE FAIL`**, naming the entry. **A blind reader — one returning zeros because it read the wrong key, the wrong slice or an empty tuple — FAILS this gate rather than passing it**, which is the opposite failure direction from SO-2a's `G-STRUCT` and is why it is registered here. Driven by selftest leg V2.
* **G-TB — the `DAFOAM_CHARTER.md` §4 trivial baseline.** **Registered: the same five components at `h = 1e-8` must FAIL band D. `G-TB PASS` iff at most 1 of 5 components passes band D at the wrong step.** **G-TB is composed ONLY onto a row whose `G5m` verdict is `PASS`** — a row that already `GATE FAIL`s needs no trivial baseline to doubt it, and composing one there would convert a real gradient defect into `NOT A RESULT` and hide the finding. G-TB's own verdict is printed on every row either way.
* **G6 — dot-product / duality test and complex step: NOT MEASURED, and the grader prints that sentence beside the verdict rather than a value.** The reason is a measurement, not an omission: AV-2 measured that seeding forward mode makes the primal FAIL on this exact case on BOTH images (`curriculum_AV2/RESULTS.md` §2, 5/5 rows `AnalysisError(... Primal solution failed!)`). `DAFOAM_CHARTER.md` §2 requires this to be SAID.
* **G9 — toolchain identity per row:** the ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print and the artefact's in-process `libidwarp.so` md5 must all name the row's registered toolchain — SHIPPED `f0fcb488e0e98156575cd19548e91663`, PATCHED `85f59e87253e0a71a813f64ca6e4c425`. Mismatch → **`GATE FAIL`**. Identity is an image id and a library hash, never a version string.
* **G10 — caps (§9):** every arm `core_min ≤ its cap`, sum ≤ **79.0**; a crossing is **`GATE FAIL`** and the in-container deadline is the stop. The ratio actual/predicted is printed per arm and lands as a `docs/COST_CALIBRATION.md` row at completion (`CLAUDE.md` rule 12).
* **G11 — OOM hard:** `--memory=4g --memory-swap=4g`; `OOMKilled true` is a G1 refusal, never a re-fire. **G12 — placement:** `cpuset == 9` on every arm; at np = 1 the delivered-cores floor does not apply and is reported as a number, `NOT_MEASURED` where absent.
* **DIVERGENCE shipped-vs-patched** on `d(CMZ)/dx`, per pair, is **reported with its number and never gated**.
* **ITEM VERDICT, composed here and not afterwards:** any refusal or any row `NOT A RESULT` → **`NOT A RESULT`**; else any of G-M2 / G-CMV / G-NZ / G9 / G10 / G12 or any row `GATE FAIL` → **`GATE FAIL`**; else **`PASS`**. `NOT_MEASURED` fields print beside the verdict, never inside it.
* **ROACHE (standing rule 5): THERE IS NO GRID FAMILY IN THIS ITEM — one mesh, 4,032 cells, no refinement triple. NO GCI IS QUOTED, and no row may carry one.**

## 6. THE FD TABLE — components, steps, and the plateau proved PER PAIR

**Components (5):** `shape[0]`, `shape[3]`, `shape[6]` (the LE function), `shape[7]` (the TE function) — SO-1a's, SO-2a's and SO-2M's four, so the items' readings sit on the same components — **plus `patchV[1]`** (angle of attack), which carries `G-NZ`.
**Steps:** `shape` **{1e-2, 1e-3, 1e-4}**; `patchV[1]` **{1e-1, 1e-2, 1e-3}** degrees. **Central differences, both signs → 2 + 5 × 3 × 2 + 10 = 42 primals per G arm.**
**Why these steps, by citation:** `cases/dafoam/ladder-a/A_stepsize_study.md` measured twelve invocations on THIS case (A1, 4,032 cells) and found the curve **flat at 2.5–3.0 % from 1e-4 to 3e-2, cosine 0.99998**, with the primal **FAILING** at 5e-2 and 1e-1. The registered triple lies wholly inside that measured plateau and wholly below the primal-failure region.
**THE PLATEAU IS PROVED PER PAIR, NOT ASSERTED ONCE FOR THE ITEM** (`DAFOAM_CHARTER.md` §2): for each (output, component) pair the **middle** step must agree with **at least one neighbour to 10 %**, else the pair is EXCLUDED as `NO_PLATEAU`. `|d_mid| < 1e-14` is EXCLUDED as `NEAR_ZERO`. A failed FD primal EXCLUDES its pair. **Every exclusion is COUNTED AND NAMED.** Fewer than **2** graded pairs on a row, or more than **75 %** of candidates excluded, reads **`NOT A RESULT`** — a gate that grades a quarter of its own Jacobian is not grading the Jacobian.

## 7. PLANTED CONTROLS — BOTH DIRECTIONS, AND THE ONE SUBSTANTIVE DELTA OF THIS ITEM

### 7.1 Direction A — the reader can see a non-zero (UNCHANGED from SO-2M)

**`PLANT = 1.234e-03`** for direction A, and here the absolute value is **correct and stays**, because direction A does not compare against a band: `CTRL` is a synthetic row, no solve — identical DVs on both sides so every FD entry is exactly `0.0`, and the planted twin moves entry 0 by `PLANT` on the plus side alone so that entry is exactly `PLANT / (2 · CTRL_STEP)` and the rest are still exactly `0.0`. It is **written by the instrument, re-read FROM DISK by the instrument** (which exits 2 if the plant is invisible) and **re-read again from disk by the comparator** (which exits 2 if it is invisible there). It changes a value inside a tuple the reader must traverse in full; **a control that EMPTIES that tuple is REFUSED**, because an empty container is seen by a broken reader too.

### 7.2 Direction B — THE GATE MUST BE SHOWN ABLE TO FAIL, AND THE PLANT IS NOW SUFFICIENT **BY CONSTRUCTION**

**THE RULE, REGISTERED HERE AT FREEZE AS A RULE, NOT AS A NUMBER CHOSEN AFTER SEEING AN ANSWER.** For the target graded pair `i` with FD reference `d_ref_i` and adjoint value `J_i`:

```
P_i = K * (band_D / 100) * |d_ref_i|              (MAGNITUDE)
s_i = +1 if J_i >= d_ref_i else -1                (SIGN — AWAY from d_ref)
J_i' = J_i + s_i * P_i
```

**`K` IS REGISTERED AT FREEZE AS `K = 2.0`** (`so2mr_grade.py`, `FLIP_PLANT_K = 2.0`), together with `band_D = 5.0 %`. Because `s_i` moves `J_i` **away** from `d_ref_i`, no cancellation is possible from any live position and

```
|d_ref_i - J_i'| = |d_ref_i - J_i| + P_i   EXACTLY
rel_planted      = rel_live + K * band_D  >=  K * band_D  =  10.0 %
```

against a **5.0 %** band. **The planted copy crosses band D by construction, with 100 % margin, on every row, at every functional scale, whatever the live agreement happens to be.**

**AGAINST SO-2M's OWN RECORDED NUMBER.** `|d_ref| = 0.049762462207060022`; crossing band D needs `0.0024881231103530011`. SO-2M's registered absolute plant `0.001234` is **2.479781 %** of `|d_ref|` — short by a factor of **2.016307** — and could not cross. **SO-2MR's rule gives `P = 0.0049762462207060022`, which is 10.000000 % of `|d_ref|` and exceeds the threshold by a factor of exactly 2.** *The number SO-2M could not clear, SO-2MR clears by construction.*

**WHY THIS IS NOT FITTING THE CONTROL TO THE DATA — stated here so it need not be inferred.** The plant's **purpose** is to demonstrate that the gate CAN read `GATE FAIL`. **A plant too small to cross the band demonstrates nothing and is a control in name only.** Scaling the plant to the band is not weakening the control; it is **making the control do its job**. Concretely, and each clause is checkable against this document:

* It moves **no gate, no threshold, no band and no acceptance criterion.** Band D remains 5.0 %, band E remains 5.0 %, and §5 above is SO-2M's §5.
* **Every registered verdict of every row is computed from the LIVE artefact**, exactly as SO-2M computed it. **The planted copy is never any row's verdict** — it is written to `grader_controls/X_<row>_g5m_planted.json`, graded, and used only to answer the question *did the gate move?*
* The rule is **fixed before any solver runs** and is **independent of every number this item will produce**: `K` and `band_D` are constants in the frozen bytes, and `d_ref_i` is whatever the FD arm measures. There is no free parameter left to choose after seeing an answer.
* It makes the control **strictly harder to pass**, not easier: the comparator now **REFUSES `PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION`** whenever `P ≤ need`, a refusal SO-2M's instrument could not even express.

**THE TARGET PAIR SELECTION IS CARRIED FROM SO-2M UNCHANGED** — the graded `shape` pair with the **smallest `|d_ref|`**, ties broken by the smaller index — **so that the only registered delta is the plant's size and sign.** Under an absolute plant the choice mattered (the smallest reference was where an absolute plant had its best chance). Under this rule the choice **cannot affect sufficiency at all**, because the plant is sized to whichever reference is chosen. **That the selection has become irrelevant IS the repair.**

**THE SECOND HALF OF DIRECTION B IS UNCHANGED:** a copy with `d(CMZ)/d(patchV[1])` forced to `0.0` must FLIP `G-NZ` to `GATE FAIL`. **A gate never shown failing is not known to be load-bearing** (L-314). Both directions run in the **same invocation** as the verdict they license, and both are printed on the record. **On a row whose live verdict is already `NOT A RESULT` the direction-B control is recorded `demonstrated: false` with its reason** — never as a control that passed, and never as a refusal that would convert an exclusion finding into a second one.

### 7.3 THE FREEZE-TIME SUFFICIENCY LEG, DRIVEN RED — evidence, not intention

Six selftest legs carry the rule, all **DRIVEN GREEN at freeze under both `python3` and `python3 -O`** (§11), and **two of them are drives, not assertions**:

* **B0 — THE KNOWN POSITIVE.** This comparator's band arithmetic, applied to **SO-2M's own recorded `d_ref = -0.049762462207060022`**, reproduces **SO-2M's recorded threshold `0.0024881231103530011` to 1e-15**, and shows SO-2M's absolute plant at **2.4798 %** of `|d_ref|` — unable to cross a 5.0 % band. **SO-2M's refusal is RE-DERIVED here, not quoted.** A rule that could not reproduce the defect it exists to prevent would make every green below it unearned.
* **B0b — THE REPAIR ON THE SAME NUMBER.** The SO-2MR rule at that same `d_ref` gives `P = 0.0049762462207060022`, exceeding the threshold by a factor of exactly 2.
* **B0c — THE SIGN RULE**, driven from both sides: sign is `-1` when `J < d_ref` and `+1` when `J >= d_ref`, so `|d_ref - J'| = |d_ref - J| + P` in both cases and no cancellation is reachable.
* **B0d — THE ALGEBRA:** `rel_planted = rel_live + K · band_D` verified to 1e-9 on a live fixture.
* **B3 — DRIVEN RED, AND THIS IS THE LEG THE SUPERVISOR ASKED FOR.** `K` — and nothing else — is moved to **0.5**, below 1, so the plant can no longer cross band D. The **same clean fixture that grades `PASS` at the registered `K`** is re-graded, and the leg **requires the comparator to REFUSE with `PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION` BY NAME**. A bare `refused()` would be satisfied by any refusal and could not tell a working assertion from an unrelated crash, so the refusal kind is matched by name and an unrelated exception FAILS the leg. **This is what makes the sufficiency assertion load-bearing rather than merely present.**
* **B4 — THE RESTORE, ASSERTED FROM OUTSIDE.** `K` is back at its registered `2.0` after the RED drive (restored in a `finally`, so a failure inside cannot leave the module mutated) and the clean fixture grades `PASS` again — **the RED leg left no residue.**

Two further legs, **B1** and **B2**, drive the rule at the **`CL`-class scale at which SO-2M's absolute plant was MEASURED unable to cross band D**, and show the rule-sized plant flipping the gate there: the plant needed is `0.0057799` against SO-2M's `0.001234` (a factor of 4.7 short), where SO-2MR's rule gives `0.0115598`, a factor of 2 over. **Same machinery, same band, sufficient plant.**

## 8. REGISTERED FALSIFIERS — named predictions that CAN MISS, and the outcome predicted PER ROW

| id | prediction | scored by | what a MISS means |
|---|---|---|---|
| **P1** | the `CMZ` moment function **evaluates at all** on `DASimpleFoam` in both images — the primal completes and `CMZ` is finite in `so2mr_X.json` | artefact presence + finiteness | **HIT ONCE ALREADY ON SO-2M** (`CMZ_baseline = 0.0078407548669119`) and re-registered here because a prediction scored on another item's artefacts is not scored on this one's. A MISS now would mean the evaluation is not reproducible across two identical registrations, which is a finding about the toolchain, not about the moment family |
| **P2** | `\|CMZ_baseline\| ≤ 0.02` at `shape = 0`, `aoa = aoa0` (symmetric section about the quarter chord) | G-CMV | the reference point, axis or scale is not what the copied block declares, **or** the viscous moment on this mesh is far larger than thin-airfoil theory allows — either way a real finding about the functional, not a grading artefact |
| **P3** | `d(CMZ)/d(patchV[1]) ≠ 0` on both sides, and `\|d(CMZ)/d(aoa)\| < \|d(CL)/d(aoa)\|` in the same units-free comparison | G-NZ + a reported number | a MISS on the first clause means the functional is not wired to the flow; a MISS on the second means the section's moment is more `aoa`-sensitive than its lift, which would be a genuine surprise on this case |
| **P4** | **PATCHED row `G5m` PASSES** band D and band E | G5m | a MISS puts the patched toolchain's moment Jacobian in the same class as the shipped one and removes the two-row contrast this item is built on |
| **P5** | **SHIPPED row `G5m` GATE FAILS** — the travelling shipped `GATE FAIL` | G5m | **a MISS would be the more interesting outcome**: it would mean the IDWarp defect that produced SO-1a's shipped `CD` aggregate of **40.481353490548585 %** and its `shape[6]` sign flip (`curriculum_SO1a/RESULTS.md:100`) does **not** reach a moment functional, and the defect's reach would then be a measured property rather than an assumed one |
| **P6** | at most **1 of 5** components passes band D at the deliberately wrong step `h = 1e-8` on each row | G-TB | a MISS withdraws that row's `PASS` (`DAFOAM_CHARTER.md` §4) |
| **P7** | **the direction-B control DEMONSTRATES on every graded row** — `plant_is_sufficient: true` and `plant_margin_ratio == 2.0` to 1e-12 on each — so the comparator reaches a verdict instead of refusing | the control record itself | **THIS IS THE PREDICTION SO-2M MISSED**, and it is registered as a falsifier rather than assumed. A MISS means the rule does not port either, and the finding would then be that direction-B sufficiency needs something other than band-relative scaling — a strictly more valuable result than a quiet `PASS` |

**PREDICTED OUTCOME, WRITTEN BEFORE ANY SOLVER RUNS SO IT CANNOT BE WRITTEN AFTERWARDS: P1–P7 HIT → PATCHED row `PASS`, SHIPPED row `GATE FAIL`, ITEM VERDICT `GATE FAIL`.** The `GATE FAIL` is **registered as the expected outcome and is not avoided**; the item fails on its weakest link and the patched `PASS` does not carry the row (`curriculum_SO1a/RESULTS.md:33`). *SO-1bR's P2 and P4 both MISSED against a frozen document that had named that possibility in advance; SO-2M's direction-B control MISSED against a document that had not. P7 exists so that this item cannot repeat the second case.*

## 9. COST — core-minutes, caps, dollars DERIVED, and SO-2M's 6.25 core-min carried as WASTE

**Anchors are MEASURED core-minutes read from ledgers on this box, not estimates.** SO-2MR's program is **SO-2M's program exactly** — same five arms, same 42 primals per G arm, same np = 1, same mesh — so **SO-2M's own measured figures are the anchor and they are used unmodified**: `MESH 0.183`, `X-S 1.017`, `G-S 2.017`, `X-P 0.85`, `G-P 2.183` (`curriculum_SO2M/RESULTS.md:185-189`, from that item's ledger).

| arm | point (core-min) | cap (core-min) | basis |
|---|---|---|---|
| MESH | 0.20 | 5.0 | SO-2M 0.183 MEASURED |
| X-S | 1.50 | 12.0 | SO-2M 1.017 MEASURED, margin carried |
| G-S | 3.60 | 25.0 | SO-2M 2.017 MEASURED, SO-1a F-S 3.583 MEASURED as the upper anchor |
| X-P | 1.50 | 12.0 | SO-2M 0.85 MEASURED, margin carried |
| G-P | 3.50 | 25.0 | SO-2M 2.183 MEASURED, SO-1a F-P 3.433 MEASURED as the upper anchor |
| **total** | **10.30, registered POINT 11.0 carrying margin** | **CEILING 79.0** | — |

**The point and ceiling are SO-2M's, deliberately unchanged**, so that this item's calibration row is directly comparable with its predecessor's rather than re-baselined against a measurement that only exists because the predecessor ran.

**Dollars, DERIVED and NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5): at **$0.0513/core-h on c7a.4xlarge, a rate that is REPORTED-BY-OWNER (Sanaa, 2026-08-21/22, corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`) and is NOT a figure this box measured** — point **11.0 core-min = 0.1833333 core-h = $0.009405**; ceiling **79.0 core-min = 1.3166667 core-h = $0.067545**. **Both are far under $25 and therefore pre-authorised — the figure is stated anyway, because a blanket is not a per-item read** (`CLAUDE.md` rules 9 and 12). **An overrun STOPS the run; it does not get a new budget.**

**SO-2M's SPEND, CARRIED AS WASTE AND NAMED HONESTLY.** SO-2M's five arms cost **6.250 core-min** (this document's arithmetic on five on-record ledger figures; **no artefact prints that total**, because the comparator refused before writing a `G10_caps` block — `curriculum_SO2M/RESULTS.md:193`). At the reported-by-owner rate that is **0.1041667 core-h = $0.005344, DERIVED**. **It is WASTE, and the cause is a CONTROL failure — a GATE-DESIGN defect in the registered plant size — NOT a solver failure:** every arm returned `rc=0`, the chain completed 5 of 5, and `CMZ` evaluated finite on both images. **Per `COMPUTE_BUDGET_CHARTER.md` §6 this waste is named separately and is NEVER absorbed into SO-2MR's actual/predicted calibration ratio.** At this item's completion the ratio is computed per arm from this item's own ledger and lands as a row in `docs/COST_CALIBRATION.md`, with SO-2M's 6.250 core-min carried **beside** it as a separately labelled waste line, never inside the ratio (`CLAUDE.md` rule 12).

## 10. NO-LAUNCH BRANCHES (registered BEFORE compute, at ZERO core-min), §18.7's BOUNDED WAIT

**Each writes its named file and exits with its named rc, and each costs 0.00 core-min. All four are DRIVEN by `so2mr_pin_selftest.sh` on sandbox copies whose only deltas are printed as a diff.**

| branch | condition | writes | rc | verdict |
|---|---|---|---|---|
| **NL-1 AGGREGATE** | the box's free memory cannot hold this item's 4 g beside the live siblings at the bound | `NOLAUNCH_AGGREGATE.txt` naming the sampled figures, the bound and the DISCARD ACCOUNTING | **6** | **`BLOCKED`** |
| **NL-2 PRODUCER** | `so2mr_runScript.py` differs from the tutorial by anything other than the registered insertions, or the tutorial's md5 is not `0557da51f6f179f6de865144343c499f` | `NOLAUNCH_PRODUCER.txt` with the offending diff hunks | **4** | **`BLOCKED`** |
| **NL-3 ROOT** | the run root already exists, or a live container/driver holds this item's prefix, or a `rc=0` ledger row would be re-fired (`ALREADY_BOUGHT`) | `NOLAUNCH_ROOT.txt` | **3** | **`BLOCKED`** |
| **NL-4 FREEZE** | `so2mr_grade.py`'s or `so2mr_run_arm.sh`'s md5 does not equal the value pinned in the driver at this freeze commit | `NOLAUNCH_FREEZE.txt` | **5** | **`BLOCKED`** |

**§18.7 AGGREGATE-RESOURCE CLAUSE — A BOUNDED WAIT TERMINATING WITH A NON-ZERO rc, NEVER BLOCK-AND-CONTINUE.** The launcher waits **at most 14,400 s** for aggregate memory; on expiry it exits **rc = 6** (NL-1) and the item reads **`BLOCKED`**. It never proceeds after a wait it lost, and it never returns 0 on expiry — **driven, and the driver is shown never to reach the launcher after losing the wait.** **The fraction of the declared program a block would discard is stated here rather than discovered later: an NL-1 at t=0 discards 5 of 5 arms (100 %) at 0.00 core-min; an NL-1 that fires between arms discards only the arms not yet bought, and the ledger's `rc=0` rows are kept, never re-run and never deleted.**

## 11. THE FROZEN INSTRUMENTS — md5 table, and the self-tests DRIVEN GREEN BEFORE THIS FREEZE

**Unlike SO-2M, this item freezes its instruments in the same commit as its gates.** Every file below is frozen by this commit; a departure is a dated amendment appended at the foot of this document with a version bump and the assertion `lines whose number changed above this section: 0`.

| file | md5 | role |
|---|---|---|
| `so2mr_chain_driver.sh` | `dc93c0365d9c7516ad55256a1c698e9b` | the five-arm detached chain, the four NO-LAUNCH branches, the pin block |
| `so2mr_run_arm.sh` | `c27a40f507f60be4bfdc4bead696a612` | one arm, one container, G-ROW double row derivation, the ledger row |
| `so2mr_grade.py` | `4f625c58c1c5f7b9a9c8f6cdda9c530c` | **the frozen comparator**, `FLIP_PLANT_K = 2.0`, 80 selftest units |
| `so2mr_xm.py` | `f9da5713cd762f3da5ff350d8403f3ae` | the in-container instrument: `compute_totals`, the FD table, the direction-A `CTRL` row |
| `so2mr_runScript.py` | `ae4a73429dd6972dc804b76d9a44aa05` | the producer — the tutorial plus the registered `CMZ` insertions |
| `so2mr_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | the NL-1 sampler |
| `so2mr_pin_selftest.sh` | `ec45d035a96845626e559cfc4e7f3734` | the pin census and the four NO-LAUNCH drives — **starts no container by construction** |
| `so2mr_decomposeParDict` | `e6f1b0060944bc86d6dff56480ad2bd4` | `numberOfSubdomains 1`, scotch |
| `so2mr_runScript_DELTAS_from_tutorial.diff` | `deab7e4d901c53d5e7840f83643fd117` | the registered producer insertions, shown |
| `so2mr_derive_from_so2m.sh` | `c3a91e49cb2a7cc10bfc2670a30a5dde` | the recorded mechanical derivation from SO-2M's bytes |

**THE PINS ARE A CENSUS, NOT A CLAIM.** `so2mr_pin_selftest.sh` enumerates every `MD5_*=` assignment **out of the driver's and launcher's own bytes**, maps each through one registered table, and refuses on any pin with no target. At freeze: **pins that EXIST = 14, pins DRIVEN = 14, unmapped = 0, mismatched = 0**, with a planted-negative leg proving that the zero mismatches is a reading (a corrupted pin in a copy is caught) and a second proving an unmapped pin cannot appear silently. *This leg exists because SO-1c's driver carried twelve pins and its selftest drove four while claiming "every pin".*

**DRIVEN GREEN AT FREEZE, 2026-08-31T22:14–22:15Z, ZERO CONTAINERS AND ZERO CORE-MINUTES:**

* `python3 so2mr_grade.py --selftest` → **`SELFTEST PASS 80/80`**, `failures=0`, rc=0.
* `python3 -O so2mr_grade.py --selftest` → **`SELFTEST PASS 80/80`**, `failures=0`, rc=0 — **run under `-O` because `-O` strips `assert`, and a control that lives in an `assert` is absent in production** (L-332).
* `bash so2mr_pin_selftest.sh` → **`pass=26 fail=0 pins_exist=14 pins_driven=14`**, rc=0, and its own closing legs record that the case-directory listing is byte-identical before and after (`018e05c041a24594b2864eef53b87251`), the SO-2MR run root is **still absent**, and the `so2mr_` container count is **0 before and 0 after**.

**80 = 74 + 6.** SO-2M's frozen comparator carried 74 selftest units; SO-2MR adds **exactly six** — B0, B0b, B0c, B0d, B3, B4 — for the plant rule. **Legs are ADDED; none is removed and none is weakened.**

## 12. WHAT THIS ITEM DOES NOT CLAIM

**This item will NOT establish:** anything at np ≠ 1; anything about an optimum, a moment CAP as an optimisation constraint, or feasibility under one; anything about the other four `shape` functions or `patchV[0]`; any dot-product or complex-step reference (§5 G6); any grid-convergence statement (§5, no grid family, **no GCI**); anything about the RAE2822 transonic half of Sanaa's SO-1 sentence or about any compressible rung — **SO-3b and every Mach-multipoint rung remain behind the D15/D16 shipped-gradient gate by Sanaa's ruling of 2026-08-31T15:13Z and nothing here touches that gate.**

**It does not re-grade, re-open, convert or edit SO-1a, SO-1aR, SO-1b, SO-1bR, SO-1c, SO-1cR, SO-2a, SO-2M, SO-3a or SO-3aR.** **SO-2M's `NOT A RESULT` stands as SO-2M's verdict**; SO-2MR is a new item with its own root, its own ledger and its own verdict, and it does not retroactively make SO-2M anything other than what its frozen documents say it was.

**THE QUEUE ENTRY IS NOT FILED BY THIS DOCUMENT.** A `QUEUE_ENTRY_DRAFT.json` accompanies this freeze carrying this document's own freeze commit as `prereg_commit`; **arming it is the supervisor's decision under `SUPERVISION_CHARTER.md` §3 check 4, not this lane's** (`CLAUDE.md` rule 9 — no agent's message is Sanaa's consent, and a lane does not arm its own item).
