# Curriculum item SO-1bR — the A1 NACA0012 drag-minimisation optimisation, re-run on the repaired IDWarp pair: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-31 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** SO-1bR never landed one. Its comparator wrote a `PASS` on both rows into a
preserved run root **outside git**, and until today the verdict of record for this item existed only
there and in one census row. That is `docs/dafoam/GRADING_CHAIN.md` bullet 8 in the live — *"the
authoritative verdict is born outside version control"* — and `cases/dafoam/INDEX.md`'s
2026-08-31 SO-series addendum names this item first among the six in that state.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no gate was evaluated, no artefact was written, no preserved run root was
> touched, and **zero solver core-minutes were spent.** Every verdict, gate reading, band, count,
> refusal string and cost figure below is **copied from an existing artefact and cited to it by
> absolute path and by JSON key, ledger field or line number.** Where a figure a reader would want
> is **not** on record, this document says so and says where a reader would have to go — it does
> not supply one. **The two places where this record states arithmetic rather than a copied figure
> are labelled as such at the point of use** (§6's dollar total and §6's whole-item ratio, and
> nothing else). A results record that quietly derives a fresh figure is a second grading of the
> same item wearing a scribe's clothes.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings
> (`## 1. SPEND` … `## 6. WAITING LIST`) are **the morning report's**, matched literally, so a
> curriculum record must not wear them. This record follows the family's own convention for a
> curriculum item — `curriculum_SO1a/RESULTS.md`, `curriculum_AV1R/RESULTS.md`,
> `A2/curriculum_D6R/RESULTS.md`.

---

# 1. Item verdict — `PASS`, on both rows, and it travels with a qualification the artefact itself wrote

| | |
|---|---|
| **Item verdict** | **`PASS`** |
| Grading artefact of record | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/SO1bR_grade_20260831T160245Z.json` → `verdict` |
| `refusal` | **`null`** — the comparator did not refuse |
| Companion `.out` | `…/SO1bR_grade_20260831T160245Z.out` line 2: `verdict=PASS verdict_line_present=True` |
| Comparator exit | `grader_rc=0` — `…/STATUS.chain:9`, whose own note reads `comparator-exit-status-NOT-the-verdict` |

**The `PASS` carries a qualification the comparator itself wrote into the artefact, and the two
travel together.** Verbatim from `SO1bR_grade_20260831T160245Z.json` → `verdict_line`:

    SO1bR PASS -- RESTS ON THE PATCHED ROW OF CURRICULUM-SO1aR, WHOSE ITEM VERDICT IS GATE FAIL AND
    WHOSE SHIPPED ROW IS GATE FAIL: G5_CD GATE FAIL 3/5 aggregate 40.4814% with 1 sign flip(s),
    G5c_CL GATE FAIL 4/5 aggregate 4.3270%, worst component shape[6] at 637.7570% sign_flip=True.
    THE SHIPPED TOOLCHAIN FAILED THE GRADIENT THIS RESULT RESTS ON.

The same qualification is recorded independently at `…json` → `upstream_provenance`, whose
`upstream_item` is `CURRICULUM-SO1aR`, `upstream_item_verdict` is **`GATE FAIL`**, and whose
`rows` read `{"SHIPPED": "GATE FAIL", "PATCHED": "PASS"}` from
`SO1aR_grade_20260828T171830Z.json`. **This item's own `PASS` is not disputed by that; the
qualification is a statement about what the result rests on, and it is reproduced here because
reporting the word `PASS` without it would misrepresent the artefact.**

# 2. THE TWO ROWS — both ran, and both are `PASS`

Copied from `SO1bR_grade_20260831T160245Z.json` → `grade.rows`:

| row | verdict | key |
|---|---|---|
| **SHIPPED** | **`PASS`** | `grade.rows.SHIPPED` |
| **PATCHED** | **`PASS`** | `grade.rows.PATCHED` |

**Both rows executed and both are graded, so a two-row verdict exists for this item**
(`GRADING_CHAIN.md` bullet 7: *"Every item is TWO ROWS, SHIPPED and PATCHED; an item with only one
row executed yields no verdict at all, not a partial one."*).

# 3. CAUSE CLASS — none applies, and none is assigned

`docs/dafoam/GRADING_CHAIN.md`'s cause-class table is headed **"Cause classes on this family's
non-`PASS` verdicts"** and carries **no row for SO-1bR**. `cases/dafoam/INDEX.md`'s SO-series
addendum states the rule in its own column for this item: **`— (PASS carries no class)`**.

**This record therefore assigns no cause class and invents none.** Whether the qualification in §1
obliges a class of its own is not a scribe's call; it is the supervisor's, and this record does not
pre-empt it.

# 4. THE ARMS, THEIR TOOLCHAIN AND THEIR SPEND

All figures copied from `/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/ledger.txt`
(per-arm `ARM=` rows and the `D4S_IDWARP_SO_MD5:` line that follows each) and cross-checked against
`SO1bR_grade_20260831T160245Z.json` → `grade.gates.G10_caps.per_arm`. **This lane read those files
and wrote neither.**

| arm | row | rc | wall s | ranks | core-min | cap core-min | ledger line |
|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 127 | 1 | **2.117** | 5.0 | `ledger.txt:3` |
| `O-P` | PATCHED | 0 | 282 | 1 | **4.7** | 25.0 | `ledger.txt:7` |
| `E-P` | PATCHED | 0 | 192 | 1 | **3.2** | 30.0 | `ledger.txt:11` |
| `O-S` | SHIPPED | 0 | 283 | 1 | **4.717** | 25.0 | `ledger.txt:15` |
| `E-S` | SHIPPED | 0 | 192 | 1 | **3.2** | 30.0 | `ledger.txt:19` |
| **total** | | | | | **17.933999999999997** | ceiling **115.0** | `grade.gates.G10_caps.total_core_min` / `.ceiling` |

`G10_caps.verdict` = **`PASS`**; `not_measured` = `[]`; no arm `crossed` its cap.

`STATUS.chain` records the chain in two started blocks — `chain=started arms=[MESH O-P E-P O-S E-S]`
at `20260831T150123Z` and `chain=started arms=[O-P E-P O-S E-S]` at `20260831T154243Z` — closing
`chain=COMPLETE stamp=20260831T160245Z`. **Two queue entries correspond**, both in git:
`verification/queue/dafoam/launched/SO1bR.json` (`cost_core_min_estimate` **20.2**) and
`…/SO1bR_r2.json` (`cost_core_min_estimate` **18.08**), each carrying
`prereg_commit = fa18e2312fb2a35f93f57f29c799b8dfe33ec07a`.

## 4.1 Toolchain per row — `G9` reads `PASS` and the identity is per arm, not per item

Copied from `ledger.txt` and from `SO1bR_grade_20260831T160245Z.json` → `grade.gates.G9_toolchain.per_arm`.

| row | image | digest | `libidwarp.so` md5 (ledger `D4S_IDWARP_SO_MD5`) |
|---|---|---|---|
| **SHIPPED** (`MESH`, `O-S`, `E-S`) | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** |
| **PATCHED** (`O-P`, `E-P`) | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`** |

`G9_toolchain.verdict` = **`PASS`**; every arm's `ok` is `true`, and on the four solver arms the
`printed_so_md5` (what the container printed) equals the `artefact_so_md5` (what the arm's own
output carried). On `MESH` the `artefact_so_md5` is `null` and the `printed_so_md5` is the SHIPPED
value — the mesh arm produces no gradient artefact to stamp.

# 5. WHAT THE GATES READ — copied, not re-evaluated

From `SO1bR_grade_20260831T160245Z.json` → `grade.gates`.

| gate | reading |
|---|---|
| `G1_completion` | **`PASS`** |
| `G-M2_mesh_identity` | **`PASS`** |
| `G5E_CD_SHIPPED` | **`PASS`** — aggregate **0.14081834174076063 %**, 5/5 graded pass, 0 sign flips, band D and band E both `PASS` |
| `G5E_CD_PATCHED` | **`PASS`** — aggregate **0.1420187528655736 %**, 5/5, 0 sign flips |
| `G5E_CL_SHIPPED` | **`PASS`** — aggregate **0.17032434227238882 %**, 5/5, 0 sign flips |
| `G5E_CL_PATCHED` | **`PASS`** — aggregate **0.17490792406387992 %**, 5/5, 0 sign flips |
| `G-OPT_SHIPPED` (`O-S`) | **`PASS`** — `EXIT: Optimal Solution Found.`, **11** majors against `max_iter_registered` **30**, `hit_iteration_bound` false, exit line confirmed on an independent channel |
| `G-OPT_PATCHED` (`O-P`) | **`PASS`** — identical exit line, **11** majors, same bound |
| `G-CL_SHIPPED` (`E-S`) | **`PASS`** — `CL_at_re_solve` 0.5000001817843563 against target 0.5, residual 1.8178435634563783e-07 ≤ 1e-04 |
| `G-CL_PATCHED` (`E-P`) | **`PASS`** — `CL_at_re_solve` 0.4999999446923125, residual 5.5307687485406376e-08 |
| `G-GEO_SHIPPED` / `G-GEO_PATCHED` | **`PASS`** / **`PASS`** — 23 of 23 rows seen, none out of bound, slack 1e-06 |
| `G-D7R_SHIPPED` / `G-D7R_PATCHED` | **`PASS`** / **`PASS`** — improvement vs cold **16.176652508849244 %** / **16.176670236254335 %** |
| `G_TB_SHIPPED` / `G_TB_PATCHED` | **`PASS`** / **`PASS`**, and the gate's meaning is in its own `consequence` string: *"the trivial baseline FAILS as registered, so the FD gate is measuring the step"* — **5 of 5 components read `tb_verdict: GATE FAIL` at the absurd step**, `n_passing_band_D_at_the_WRONG_step` **0** against `max_allowed` **1** |
| `G10_caps` | **`PASS`** (§4) |
| `G12_placement` | **`PASS`** |
| `G6_dot_product_duality` | **`NOT MEASURED`** — the artefact's own words: *"the tutorial exposes no dot-product/duality test…"* |

**Section 9's rule is satisfied on its own terms**, `grade.section_9_note`:
*"DAFOAM_CHARTER.md section 9: no row is PASS without the optimiser's own convergence statement."*
Both `G-OPT` gates carry that statement verbatim.

## 5.1 The optimum, and the shipped/patched divergence — REPORTED, and it gated nothing here

`grade.optimum`: PATCHED `CD_opt` **0.017527900146318345**, SHIPPED `CD_opt` **0.017527898174499734**,
both from `CD_cold` **0.02091051000679216**, both at 11 majors and `EXIT: Optimal Solution Found.`

`grade.divergence_shipped_vs_patched_CD_at_optimum` is a five-row list; the largest
`divergence_pct` in it is **0.14826498152947654 %** at `shape[0]`. **Registered prediction
`PF_shipped_CD_opt_not_below_patched` is a `MISS`** — the SHIPPED optimum came in
1.97e-09 below the PATCHED one, which is inside that divergence. The `MISS` is copied from
`grade.predictions`, not judged here.

## 5.2 Predictions — copied verbatim from `grade.predictions`

**HIT:** `PA_cells_4032`, `PB_CD_trimmed_in_D1_band`, `PB_CL_trimmed_on_target`,
`PC_patched_optimiser_converged_in_band`, `PD_patched_CD_opt_reproduces_D1`,
`PD_patched_improvement_reproduces_D1`, `PG_CL_held_at_re_solve_both_rows`,
`PH_naive_aoa_channel_larger_than_shape_on_PATCHED`, `PI_total_core_min_band`,
`PJ_trivial_baseline_fails_ge4_of_5_on_PATCHED`,
`PK_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm`.
**MISS:** `PF_shipped_CD_opt_not_below_patched`, `P_mesh_wall_le_120s`.
`PE_shipped_shape6_endpoint_verdict` = **`PASS`** at
`PE_shipped_shape6_endpoint_rel_err_pct` **0.028855490161491044**.

## 5.3 The rule-3 control WAS exercised, and the C-5 false-positive was seen and classified benign

`grade.controls` carries `P`, `S`, `grader_plant_P` and `grader_plant_S`. Separately,
`c5_sites` records **one benign site and zero fatal**: line 30 of the arm output,
`trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`, classified
*"OpenFOAM sigFpe SETUP banner — an ENABLEMENT NOTICE, not a crash"*. **This is the exact string
that produced SO-1a's false G1 refusal** (`cases/dafoam/INDEX.md`, SO-1b row, citing
`docs/COST_CALIBRATION.md` C-205); here the reader saw it and did not trip.

`rebind_audit` records **25 constants checked, `constants_moved` empty, and exactly one name
rebound — `fatal_tokens_in`**. `precondition_md5` is `447eaada4a896fc5f8b0f4ced4cb2af8`;
`preserved_root_manifest_files` is **640**.

Frozen instruments, from the artefact's own top-level keys:
`frozen_grader` = `cases/dafoam/ladder-a/A1/curriculum_SO1b/so1b_grade.py`, md5
**`88157ca3c04798750e97b87ca3d02a15`**; `frozen_stage1` = `curriculum_SO1bR/so1br_grade.py`, md5
**`9736ca91c9c111877f86dc048b38e929`**; `entry_point` = `curriculum_SO1bR/so1br_grade_cli.py`.

# 6. COST — rule 12

| | |
|---|---|
| **Actual, MEASURED** | **17.933999999999997 core-min** — `SO1bR_grade_20260831T160245Z.json` → `grade.gates.G10_caps.total_core_min`, itself the sum of the five `ARM=` rows in `ledger.txt` |
| Registered estimate | **20.2 core-min point, band [11.0, 58.0]**, ceiling **115.0** — `curriculum_SO1bR/PREREGISTRATION.md:603`, inherited from SO-1b and **not re-derived** by that document's own statement; the second queue entry `SO1bR_r2.json` carries **18.08** |
| Registered cap manifest | `SO1BR-CAP-MANIFEST v1 MESH=5.0 O-P=25.0 E-P=30.0 O-S=25.0 E-S=30.0 CEILING=115.0` — `PREREGISTRATION.md:538` |
| Prediction on cost | `PI_total_core_min_band` = **`HIT`** — `grade.predictions` |
| Waste | **none named in any artefact this record read** |
| GPU | **0 GPU-h** — no GPU instance was launched |

**Dollars: $0.01533 — DERIVED, NOT MEASURED.** `cost_basis` **REPORTED-BY-OWNER, NOT MEASURED**;
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Stated plainly: this is
THIS RECORD'S ARITHMETIC** on the on-record 17.934 core-min at the recorded c7a.4xlarge rate of
$0.0513/core-h (`CLAUDE.md` rule 12), **not a figure copied from any artefact.**

**A whole-item actual/predicted ratio is likewise THIS RECORD'S ARITHMETIC and is stated once,
labelled:** 17.934 ÷ 20.2 = **0.8878**. It is offered only because all five registered arms ran to
`rc=0`, so the numerator and denominator price the same program — the condition that made the same
division dishonest for `D6R` and for `SO-3a` (§6 of `A2/curriculum_D6R/RESULTS.md`;
`docs/COST_CALIBRATION.md`, the SO-3a row, which refuses its own ratio for exactly that reason).

> **NO CALIBRATION ROW EXISTS FOR SO-1bR, AND ONE IS OWED.** `docs/COST_CALIBRATION.md` carries
> **zero** occurrences of `SO-1bR` or `SO1bR`. Rows exist for the siblings `SO-1cR` and `SO-3a`;
> there is none for this item's 17.934 core-min. **Writing it is not a scribe's call** — it is the
> supervisor's, and rule 11 requires its id to be derived inside the committing invocation (or
> allocated by `scripts/append_record.py`, as the family's most recent rows were). **It is flagged,
> not filled.**

# 7. WHERE THE FULL READINGS LIVE — this record is a signpost, not a duplicate

1. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt/SO1bR_grade_20260831T160245Z.json`**
   (outside git) — the verdict of record, `grade.rows`, all sixteen gate objects with their
   per-component tables, `grade.optimum`, `grade.predictions`, `grade.controls`,
   `upstream_provenance` and `verdict_line`.
2. **`…/ledger.txt`**, **`…/STATUS.chain`**, the five `STATUS.<arm>` files and the per-arm
   `*.log` / `*.inspect.txt` / `*.cpu.jsonl` records — the arm census, the toolchain stamps and
   the memory windows.
3. **`cases/dafoam/ladder-a/A1/curriculum_SO1bR/PREREGISTRATION.md`** (this directory, frozen) —
   the gates, bands, caps, the cost table at **:601–:603** and the cap manifest at **:538**.
4. **`cases/dafoam/INDEX.md`**, Addendum 2026-08-31 — this item's census row and the flag that
   its verdict lived only outside git.
5. **`docs/dafoam/GRADING_CHAIN.md`** — bullets 7 and 8, and the cause-class table this item is
   correctly absent from.
6. **`cases/dafoam/ladder-a/A1/curriculum_SO1bR/so1br_selftest_evidence.txt`** and
   **`so1br_stage2_evidence.txt`** — the instrument evidence, in git, in this directory.

**If any figure in this record disagrees with the grade JSON or the ledger, the JSON and the ledger
are right.**

# 8. What this record does and does not do

**It does** give SO-1bR an item-level record where it had none, so a reader arriving at this
directory finds the item's verdict instead of a pre-registration and a silence.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, score any
prediction, run any comparator, touch the preserved run root, or add any number that was not
already written in a cited artefact — with the two arithmetic exceptions labelled at their point of
use in §6.

**It does not** fill the calibration row it flags as owed (§6), and it does not touch
`docs/dafoam/GRADING_CHAIN.md`, `docs/dafoam/README.md` §3 or `cases/dafoam/INDEX.md`.

**It establishes nothing about the physics beyond what §5 copies from the comparator's own output.**
No solver ran for this record; **zero solver core-minutes** were spent writing it.

> **Disclosed, not hidden.** `SO1bR_grade_20260831T160245Z.json` embeds a transient temporary path
> as `grade.gates.G-D7R_SHIPPED.path` / `G-D7R_PATCHED.path` (`/tmp/so1br_i468qv52/root_copy/…`),
> from the comparator's own working copy. That directory no longer exists, and `CLAUDE.md` rule 13
> says a repository document never cites a scratch path. It is a machine record of a transient copy
> rather than a handoff pointer, and this lane has **left it as executed** — editing an instrument's
> own output after the fact would be a worse defect than the one it discloses. **No path in this
> prose document is a scratch path.**
