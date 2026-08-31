# Curriculum item SO-1cR — np-invariance of the A1 NACA0012 gradient at the optimum, re-run past SO-1c's row-label break: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-31 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** SO-1cR never landed one. Its comparator wrote a `PASS` on both rows into a
preserved run root **outside git**, and until today the verdict of record for this item existed only
there, in one calibration row and in one census row — `docs/dafoam/GRADING_CHAIN.md` bullet 8 in
the live, and `cases/dafoam/INDEX.md`'s 2026-08-31 SO-series addendum, which names this item among
six in that state.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no gate was evaluated, no artefact was written, no preserved run root was
> touched, and **zero solver core-minutes were spent.** Every verdict, gate reading, band, count,
> refusal string and cost figure below is **copied from an existing artefact and cited to it by
> absolute path and by JSON key, ledger field or line number.** Where a figure a reader would want
> is **not** on record, this document says so and says where a reader would have to go — it does
> not supply one. **This record states NO arithmetic of its own.** Uniquely among the six records
> written in this batch, SO-1cR already has a landed calibration row, so even its dollar figure and
> its actual/predicted ratio are **copied**, not derived here. A results record that quietly derives
> a fresh figure is a second grading of the same item wearing a scribe's clothes.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings are **the
> morning report's**, matched literally, so a curriculum record must not wear them. This record
> follows the family's own convention — `curriculum_SO1a/RESULTS.md`,
> `curriculum_AV1R/RESULTS.md`, `A2/curriculum_D6R/RESULTS.md`.

---

# 1. Item verdict — `PASS`, on both rows

| | |
|---|---|
| **Item verdict** | **`PASS`** |
| Grading artefact of record | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-dragmin-npinv/SO1cR_grade_20260831T175758Z.json` → `verdict` |
| Companion `.out` | `…/SO1cR_grade_20260831T175758Z.out` — the same object, pretty-printed; `verdict` at **line 3** |
| Comparator exit | `grader_rc=0` — `…/STATUS.chain:8`, note `comparator-exit-status-NOT-the-verdict` |
| Chain | `chain=COMPLETE stamp=20260831T175758Z` — `…/STATUS.chain:7`; five of five registered arms `rc=0` |

# 2. THE TWO ROWS — both ran, both `PASS`, and each row carries two decompositions

Copied from `SO1cR_grade_20260831T175758Z.json` → `rows` and `arms`:

| row | verdict | arms | arm verdicts |
|---|---|---|---|
| **SHIPPED** | **`PASS`** | `Ns-S` (scotch), `Ni-S` (simple 4×1×1) | **`PASS`**, **`PASS`** |
| **PATCHED** | **`PASS`** | `Ns-P` (scotch), `Ni-P` (simple 4×1×1) | **`PASS`**, **`PASS`** |

**Both rows executed and both are graded, so a two-row verdict exists for this item**
(`GRADING_CHAIN.md` bullet 7). The `MESH` arm is stamped `ROW=SHIPPED` in the ledger and produces no
gradient; the four graded arms above are the solver arms.

# 3. CAUSE CLASS — none applies, and none is assigned

`docs/dafoam/GRADING_CHAIN.md`'s cause-class table is headed **"Cause classes on this family's
non-`PASS` verdicts"** and carries **no row for SO-1cR**. `cases/dafoam/INDEX.md`'s SO-series
addendum states the rule in its own column for this item: **`— (PASS carries no class)`**.

**This record therefore assigns no cause class and invents none.**

# 4. WHAT THE GATES READ — copied, not re-evaluated

From `SO1cR_grade_20260831T175758Z.json` → `gates`.

| gate | reading |
|---|---|
| `G1_completion` | **`PASS`** |
| `G-M2_mesh_identity` | **`PASS`** |
| `G-MESHID_same_mesh_as_SO1b` | **`PASS`** — this item's mesh points sha256 `6349e38f09d59e9b712e04cc9d6258d904a7cd5f2c89edae920f5b26af963394` equals SO-1b's, from the one reference file `…/optref/so1b_mesh_points_sha256.txt`, with exactly **1** mesh-log candidate. The gate's own note: *"the standard defines np-invariance ON THE SAME MESH; this item regenerates the mesh, so identity is asserted, not assumed"* |
| `G-DECOMP` | **`PASS`** ×4 — `Ns-P`/`Ns-S` scotch `n_subdomains 4`, `Ni-P`/`Ni-S` simple `['4','1','1']`, `mpi_nprocs 4`, each read from that arm's own `/mnt/<arm>/system/decomposeParDict` |
| `G-XSTAR` | **`PASS`** ×4 |
| `G-NP_np_invariance_at_the_optimum` | **`PASS`** ×4 — the item's subject gate. Per-arm `CD` invariance `s_g`: **2.6783329640937475e-06** on both PATCHED arms and **2.7409402612690873e-06** on both SHIPPED arms, against `band_s_g` **1.0e-03**; `sign_flip_max` **0**; reference `np1` from `/mnt/<arm>/so1b_E.json` |
| `G-NP_objective_spread` | **`PASS`** ×4 |
| `G-METHOD_scotch_vs_simple_at_fixed_np4` | **`PASS`** on row `P` and row `S`, `band_s_g` **1.0e-03**. Its `reference_convention` is registered rather than chosen after the numbers: *"`simple 4x1x1` is the REFERENCE limb and `scotch` the graded limb, fixed here before the run: A4 measured `simple 4x1x1` at 0.00054 % against FD and `scotch` at 8.95 %"* |
| `G5N_CD` | **`PASS`** ×4 — the FD bright line on `dCD/dx`. On `Ns-P`: `shape[0]` **0.32284324486377663 %**, `shape[3]` **0.04401035136643356 %**, `shape[6]` **0.027398016346464178 %**, `shape[7]` **1.107182494457175 %**, each with a three-step plateau at h ∈ {1e-2, 1e-3, 1e-4} |
| `G5cN_CL` | **`PASS`** ×4 |
| `G_TB_trivial_baseline` | **`PASS`** ×4 (§4.1) |
| `G9_toolchain` | **`PASS`** (§5) |
| `G10_caps` | **`PASS`** (§6) |
| `G12_placement` | **`PASS`** |
| `G-CLOCK_two_frames` | **`NOT_MEASURED` on all five arms** — `not_measured: ["MESH","Ns-P","Ni-P","Ns-S","Ni-S"]`, `max_delta_core_min` and `sum_delta_core_min` both `NOT_MEASURED`. **Recorded as not measured, never as passed.** The registered prediction `P_CLOCK_host_frame_exceeds_container_frame_on_every_arm` is scored `NOT_MEASURED` for the same reason |
| `G6_dot_product_duality` | **`NOT MEASURED`** — the artefact's own words: *"the tutorial exposes no dot-product/duality test…"* |

`band_provenance`, copied: `s_g` **1.0e-3** from `ADJOINT_VERIFICATION_STANDARD.md` §3's band table,
*"inherited BY CITATION"*, 6× B3's measured 1.1–1.7e-4 floor; `s_J` **2.2e-5** from
`PARALLEL_GATE_DOCTRINE.md:38, :194-198`; band D / E / plateau **5.0 / 5.0 / 10.0** from
`curriculum_D4/PREREGISTRATION.md:82` and `D7FR:228-229` via SO-1a and SO-1b, *"byte-identical, not
re-derived"*. **This record does not re-derive them either.**

## 4.1 THE TRIVIAL BASELINE — one of this family's two live controls, and it fired

`GRADING_CHAIN.md` bullet 6 cites this item by name as the family's second independent live control:
*"an arm run at a deliberately absurd step (h = 1e-8) that must fail."* Copied from
`gates.G_TB_trivial_baseline["Ns-P"].components`:

| component | `tb_step` | `rel_err_pct` | sign flip | `tb_verdict` |
|---|---|---|---|---|
| `shape[0]` | 1e-08 | **97.73099578254906** | no | **`GATE FAIL`** |
| `shape[3]` | 1e-08 | **92.92982945558117** | no | **`GATE FAIL`** |
| `shape[6]` | 1e-08 | **345.7814839483765** | **yes** | **`GATE FAIL`** |
| `shape[7]` | 1e-08 | **101.59634602447206** | **yes** | **`GATE FAIL`** |
| `patchV[1]` | 1e-06 | **62.83396944312544** | no | **`GATE FAIL`** |

`n_passing_band_D_at_the_WRONG_step` = **0** against `max_allowed` **1**, so the gate's own verdict
is **`PASS`**, and its `consequence` string says what that means: *"the trivial baseline FAILS as
registered, so the FD gate is measuring the step"*. **Five of five components fail, two with sign
flips** — the same instrument that returned this item's `PASS` is shown able to fail on the same
data at a step that should not work. **That is the whole content of a control**, and it is why
`GRADING_CHAIN.md` bullet 6 cites SO-1cR rather than asserting the principle.

The registered prediction `P_TB_trivial_baseline_fails_ge4_of_5_on_every_arm` is scored **`HIT`**.

## 4.2 THE PLANTED-ZERO CONTROL — driven, and its artefacts are on disk

From `SO1cR_grade_20260831T175758Z.json` → `controls`. On each of the four solver arms the
instrument control reads `instrument_ctrl_zero` **0.0** and `instrument_ctrl_planted` **0.617**
against `want` **0.617** — **the reader is shown seeing a non-zero before its zero is believed**
(`CLAUDE.md` rule 3). Two grader plants are recorded seen, `grader_plant_Ns-P` and
`grader_plant_Ni-S`, each `grader_plant_seen: true`, `n_values` **15**, `worst_residual`
**1.0842021724855044e-18**, writing
`…/grader_controls/N_Ns-P_planted.json` and `…/grader_controls/N_Ni-S_planted.json`. The directory
`…/grader_controls/` exists in the preserved root and holds three files —
`N_Ni-S_planted.json`, `N_Ns-P_np_planted.json`, `N_Ns-P_planted.json`. **The control fired; this is
not a `NOT EXERCISED` item.**

## 4.3 The shipped/patched divergence — REPORTED, and it gated nothing

`divergence_shipped_vs_patched_CD_at_fixed_decomposition` carries per-component
`J_shipped` / `J_patched` pairs; at scotch the largest `divergence_pct` in the entries copied is
**0.1482794793430414 %** at `shape[0]`, with `shape[3]` at **0.042287592766664536 %** and
`shape[6]` at **0.013026513420168032 %**. **The comparator reports these; no gate consumes them.**

`no_improvement_percentage`, copied verbatim: *"this item quotes NO improvement percentage, so
G-D7R has no row here; and NOTHING here lifts SO-1b's own SUPPRESSED_BY_G_D7R — only SO-1b's
attribution artefact can"*.

## 4.4 Predictions — copied verbatim from `predictions`

**HIT:** `P_A_cells_4032`, `P_MESHID_same_mesh_as_SO1b`,
`P_2_simple_4x1x1_inside_s_g_band_on_both_rows`, `P_5_objective_inside_s_J_band_on_every_arm`,
`P_TB_trivial_baseline_fails_ge4_of_5_on_every_arm`, `P_mesh_wall_le_120s`.
**MISS:** `P_1_scotch_outside_s_g_band_on_at_least_one_row`,
`P_4_shape6_is_the_largest_scotch_component`,
`P_6_patched_simple_FD_PASS_and_patched_scotch_NOT`,
`P_7_shipped_shape6_outside_band_D_at_both_decompositions`, `P_I_total_core_min_band`.
**NOT_MEASURED:** `P_CLOCK_host_frame_exceeds_container_frame_on_every_arm`,
`P_3_s_g_larger_at_the_optimum_than_at_the_baseline`.

`P_3_note`, copied: AV-1R's baseline np-invariance figure is the comparison basis and *"is NOT read
by this comparator: AV-1R is a separate re…"* — the item declines the comparison rather than
approximating it.

**Four of the eleven scored predictions MISSED, and every miss is in the direction of the gradient
being CLEANER than registered** — `scotch` was predicted to fall outside the invariance band on at
least one row and did not; the shipped `shape[6]` was predicted outside band D at both
decompositions and was not. **The misses are copied as written; this record does not interpret
them into a finding.**

# 5. TOOLCHAIN PER ROW — `G9` reads `PASS`

From `/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-dragmin-npinv/ledger.txt`
(per-arm `ARM=` rows and the `D4S_IDWARP_SO_MD5:` line that follows each) and
`SO1cR_grade_20260831T175758Z.json` → `gates.G9_toolchain`.

| row | arms | image | digest | `libidwarp.so` md5 |
|---|---|---|---|---|
| **SHIPPED** | `MESH` (`:3`), `Ns-S` (`:17`), `Ni-S` (`:22`) | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** (`:5`, `:19`, `:24`) |
| **PATCHED** | `Ns-P` (`:7`), `Ni-P` (`:12`) | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`** (`:9`, `:14`) |

`G9_toolchain.verdict` = **`PASS`**.

# 6. COST — rule 12, and the calibration row already exists

| arm | row | decomposition | rc | wall s | ranks | core-min | cap | ledger line |
|---|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | — | 0 | 10 | 1 | **0.167** | 5.0 | `:3` |
| `Ns-P` | PATCHED | scotch | 0 | 61 | 4 | **4.067** | 30.0 | `:7` |
| `Ni-P` | PATCHED | simple | 0 | 61 | 4 | **4.067** | 30.0 | `:12` |
| `Ns-S` | SHIPPED | scotch | 0 | 61 | 4 | **4.067** | 30.0 | `:17` |
| `Ni-S` | SHIPPED | simple | 0 | 61 | 4 | **4.067** | 30.0 | `:22` |

| | |
|---|---|
| **Actual, MEASURED** | **16.435000000000002 core-min** — `gates.G10_caps.total_core_min_host_COST`, equal to `total_core_min_container_GATE`; ceiling **125.0**; `verdict` **`PASS`**; `not_measured` `[]` |
| Frame | **HOST**, and the artefact says why: *"the box is occupied for the host wall, so the COST claim uses it and it is the LARGER of the two frames"* (`cost.frame`). `frame_fallbacks` lists all five arms — the container frame was not measured, so `HOST_FALLBACK` is the gate frame on every one |
| Registered estimate | **40.6 core-min**, band **[22.0, 80.0]**, cap **125.0** — `curriculum_SO1cR/PREREGISTRATION.md:253`; the same in `verification/queue/dafoam/launched/SO1cR_chain_wait.json` (`cost_core_min_estimate` 40.6, `cap_core_min_registered` 125.0, `prereg_commit` `100da1e71b1716a0cb1cf54e562cdb55aeec76df`) |
| Prediction on cost | `P_I_total_core_min_band` = **`MISS`** — under the band |
| GPU | **0 GPU-h** — no GPU instance was launched |

**The calibration row for this item is LANDED, so its figures are copied, not derived here.**
`docs/COST_CALIBRATION.md`, row id **`C-20260831T195247.871530Z-5dbe03c5`**:

* **Ratio actual/predicted: `0.4048`** — the row's own ratio cell.
* **Dollars: `$0.01405` DERIVED at $0.0513/core-h, NOT MEASURED** — the row's own words.
* **Waste: `16.435 core-min — cleaned equals gross; waste 0.000`**, and, explicitly, *"SO-1c's
  0.633 core-min is NOT folded in here (named separately as waste on its own row's item)"*.
* **Gap attribution, copied verbatim:** *"MISPREDICTION, and it is INHERITED rather than this
  item's: the registered MESH point had been raised 0.167 → 0.633 on SO-1c's dead-run datum, and
  the real MESH cost 0.167 again, so the dead run's figure was the outlier and not the model. Every
  solver arm landed at 13.6 % of its 30.0 cap. NO CONTENTION TERM IS CLAIMED: the box carried no
  sibling dafoam item during the chain. Registered prediction `P_I_total_core_min_band` is recorded
  as a MISS — we came in UNDER the band, booked as a miss rather than quietly enjoyed."*
* Its own evidence cells: commit `3610f4ac`, `docs/LAB_STATE.md` S-22h, and the grade object.

**This record adds no cost figure of its own and computes no ratio.** The row above already carries
the rule-12 estimate-versus-actual comparison in full.

# 7. WHERE THE FULL READINGS LIVE

1. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1cR-a1-naca0012-dragmin-npinv/SO1cR_grade_20260831T175758Z.json`**
   (outside git) — the verdict of record, `rows`, `arms`, all sixteen gate objects with their
   per-component tables, `controls`, `cost`, `band_provenance` and `predictions`. The `.out`
   beside it is the same object pretty-printed.
2. **`…/ledger.txt`**, **`…/STATUS.chain`**, the five `STATUS.<arm>` files, the per-arm
   `*.log` / `*.inspect.txt` / `*.cpu.jsonl`, and **`…/grader_controls/`** (three planted files).
3. **`cases/dafoam/ladder-a/A1/curriculum_SO1cR/PREREGISTRATION.md`** (this directory, frozen) —
   the gates, bands, caps, the cost table at **:253** and the cap manifest at **:6**.
4. **`cases/dafoam/ladder-a/A1/curriculum_SO1cR/so1cr_rowlabel_sweep_evidence.txt`**,
   **`so1cr_grade_selftest_evidence.txt`**, **`so1cr_groot5_selftest_evidence.txt`** — the
   instrument evidence, in git, in this directory.
5. **`docs/COST_CALIBRATION.md`**, row `C-20260831T195247.871530Z-5dbe03c5` — the whole rule-12
   comparison, quoted in §6.
6. **`docs/dafoam/GRADING_CHAIN.md`** bullet 6 — this item cited as the family's trivial-baseline
   control; and `cases/dafoam/INDEX.md`, Addendum 2026-08-31, for the census row.
7. **`cases/dafoam/ladder-a/A1/curriculum_SO1c/`** — the predecessor this item repaired, whose own
   `RESULTS.md` records the row-label break at `Ns-P_launch.out:13-14`.

**If any figure in this record disagrees with the grade JSON, the ledger or the calibration row,
those are right.**

# 8. What this record does and does not do

**It does** give SO-1cR an item-level record where it had none, so a reader arriving at this
directory finds the item's verdict instead of a pre-registration and a silence.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, score any
prediction, run any comparator, touch the preserved run root, or add any number that was not
already written in a cited artefact. **It states no arithmetic of its own at all.**

**It does not** touch `docs/dafoam/GRADING_CHAIN.md`, `docs/dafoam/README.md` §3,
`cases/dafoam/INDEX.md` or `docs/COST_CALIBRATION.md`.

**It establishes nothing about the physics beyond what §4 copies from the comparator's own output.**
No solver ran for this record; **zero solver core-minutes** were spent writing it.
