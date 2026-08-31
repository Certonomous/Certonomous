# Curriculum item SO-2a — the A1 NACA0012 geometric-constraint Jacobians `d(thickcon, volcon, rcon)/d(shape, patchV)`: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-31 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** SO-2a never landed one. Its comparator wrote a `PASS` on both rows into a
preserved run root **outside git**, and until today the verdict of record for this item existed only
there and in one census row — `docs/dafoam/GRADING_CHAIN.md` bullet 8 in the live, and
`cases/dafoam/INDEX.md`'s 2026-08-31 SO-series addendum, which names this item among six in that
state.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no gate was evaluated, no artefact was written, no preserved run root was
> touched, and **zero solver core-minutes were spent.** Every verdict, gate reading, band, count,
> refusal string and cost figure below is **copied from an existing artefact and cited to it by
> absolute path and by JSON key, ledger field or line number.** Where a figure a reader would want
> is **not** on record, this document says so and says where a reader would have to go — it does
> not supply one. **The two places where this record states arithmetic rather than a copied figure
> are labelled as such at the point of use** (§7's dollar total and §7's ratio, and nothing else).
> A results record that quietly derives a fresh figure is a second grading of the same item wearing
> a scribe's clothes.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings are **the
> morning report's**, matched literally, so a curriculum record must not wear them. This record
> follows the family's own convention — `curriculum_SO1a/RESULTS.md`,
> `curriculum_AV1R/RESULTS.md`, `A2/curriculum_D6R/RESULTS.md`.

---

# 1. Item verdict — `PASS`, on both rows

| | |
|---|---|
| **Item verdict** | **`PASS`** |
| Grading artefact of record | `/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient/SO2a_grade_20260831T002529Z.json` → `verdict` |
| Companion `.out` | `…/SO2a_grade_20260831T002529Z.out`, one line: `VERDICT PASS  rows={'SHIPPED': 'PASS', 'PATCHED': 'PASS'}  written=…` |
| Comparator exit | `grader_rc=0` — `…/STATUS.chain:8`, note `comparator-exit-status-NOT-the-verdict` |
| Chain | `chain=COMPLETE stamp=20260831T002529Z` — `…/STATUS.chain:7`; five of five registered arms `rc=0` |

# 2. THE TWO ROWS — both ran, both `PASS`, and the two rows are IDENTICAL to the printed precision

Copied from `SO2a_grade_20260831T002529Z.json` → `rows`:

| row | verdict | arms |
|---|---|---|
| **SHIPPED** | **`PASS`** | `MESH`, `X-S`, `G-S` |
| **PATCHED** | **`PASS`** | `X-P`, `G-P` |

**Both rows executed and both are graded, so a two-row verdict exists for this item**
(`GRADING_CHAIN.md` bullet 7).

**And here the two rows agree exactly.** `divergence_shipped_vs_patched`, copied whole:
`{"nonzero_pairs": [], "status": "REPORTED WITH ITS NUMBER, NEVER GATED", "worst_pct": 0.0}`. Every
`G5g` figure in §3 is **byte-identical between the SHIPPED and PATCHED objects.**

**That is the item's central finding and it was registered in advance.** Prediction
`P5_SHIPPED_row_ALSO_PASS_and_divergence_is_zero` is scored **`HIT`**, and
`P6_G_STRUCT_exact_zero_both_rows` is scored **`HIT`**. **The geometric constraints do not depend on
the flow state**, so the IDWarp difference that separates the two images cannot reach them — and
the artefact says so with a measured `0.0`, not an assumption. **A zero divergence here is
informative precisely because the same instrument reports large divergences on flow-coupled items**
(the sibling `curriculum_SO1bR/RESULTS.md` §5.1 records a non-zero one at `shape[0]`).

# 3. CAUSE CLASS — none applies, and none is assigned

`docs/dafoam/GRADING_CHAIN.md`'s cause-class table is headed **"Cause classes on this family's
non-`PASS` verdicts"** and carries **no row for SO-2a**. `cases/dafoam/INDEX.md`'s SO-series
addendum states the rule in its own column for this item: **`— (PASS carries no class)`**.

**This record therefore assigns no cause class and invents none.**

# 4. WHAT THE GATES READ — copied, not re-evaluated

From `SO2a_grade_20260831T002529Z.json` → `gates`.

| gate | reading |
|---|---|
| `G1_completion` | **`PASS`** |
| `G-M2_mesh_identity` | **`PASS`** — `mesh_cells` **4032** |
| `G-CDIM_constraint_dimensions` | **`PASS`** — sizes taken from *"the PRODUCER's own call arguments in `so2a_runScript.py` (nSpan=2, nChord=10 → 20; volume → 1; LE-radius nSpan=2 → 2), never from a guess about pyGeo internals"*. Its own note: *"a size mismatch is a `GATE FAIL`, not a refusal: the gradient grading runs off the sizes ACTUALLY RECORDED, so a layout surprise does not corrupt it"* |
| `G-CV_constraint_feasibility` | **`PASS`** — bounds from `so2a_runScript.py:176-178`, the producer's own `add_constraint` calls; `feasibility_tolerance` **1e-09**. Scope, verbatim: *"feasibility AT THE GRADED DESIGN. Feasibility AT AN OPTIMUM is SO-2b's gate; no optimiser runs in this item"* |
| `G5g_SHIPPED` | **`PASS`** (§4.1) |
| `G5g_PATCHED` | **`PASS`** (§4.1) |
| `G9_toolchain` | **`PASS`** (§5) |
| `G10_caps` | **`PASS`** (§7) |
| `G12_placement` | **`PASS`** |
| `G6_dot_product_duality` | **`NOT MEASURED`** — the artefact's own words: *"the tutorial exposes no dot-product/duality test…"* |

## 4.1 `G5g` — the bright line on the constraint Jacobians, per constraint

Copied from `gates.G5g_SHIPPED.G5g_constraint_jacobians.per_constraint`. **The `G5g_PATCHED` object
carries the identical figures** (§2).

| constraint | candidate pairs | graded | pass | gate fail | sign flips | aggregate rel err % | worst rel err % | band D | band E |
|---|---|---|---|---|---|---|---|---|---|
| `rcon` | 8 | **6** | **6** | 0 | 0 | **9.64373972832878e-09** | **4.7421253692237684e-07** | `PASS` | `PASS` |
| `thickcon` | 80 | **60** | **60** | 0 | 0 | **1.3719580207874863e-11** | **1.2851625944119158e-05** | `PASS` | `PASS` |
| `volcon` | 4 | **4** | **4** | 0 | 0 | **6.149010985718915e-12** | **9.292545931293527e-12** | `PASS` | `PASS` |

`excluded_frac` is **0.25** on `rcon` and `thickcon` and **0.0** on `volcon`, every exclusion
reasoned `NEAR_ZERO` — the excluded pairs are ones where both the adjoint and the FD reference are
exactly `0.0`, so a relative error is undefined rather than unfavourable. **The exclusions are
recorded with their reason and their count, not silently dropped.**

The FD referee is a **three-step** table at h ∈ {1e-2, 1e-3, 1e-4} with a `plateau_neighbour_pct`
pair printed per pair — `DAFOAM_CHARTER.md` §2's bright line satisfied on its own terms
(`GRADING_CHAIN.md` bullet 4: *"No FD table, no gradient verdict."*).

**These are agreements at the 1e-9 to 1e-12 level.** They are that clean because the geometric
constraints are analytic in the design variables and carry no flow adjoint — which is the same fact
that produces the zero divergence in §2 and the cheap `X` arm in §7.

## 4.2 THE BIRTH REGISTER — seven readers, each shown able to see a non-zero

`SO2a_grade_20260831T002529Z.json` → `birth_register`: **`n_born` 7, `n_not_born` 0**, readers
`R1_read_ledger`, `R2_fatal_token_sites`, `R3_read_mesh_cells`, `R4_read_X`, `R5_read_F`,
`R6_read_constraint_baseline`, `R7_arm_datum`. Its `requirement` field, verbatim:

> *"Sanaa 2026-08-28: no instrument grades anything until 'was this reader ever shown able to see a
> non-zero through the real code path?' is answered YES, demonstrated…"*

The plants that answered it, from `controls`:

| control | what it read back |
|---|---|
| `grader_plant_F_P` / `grader_plant_F_S` | `grader_plant_F_seen` **true**, `n_values` **345**, `worst_residual` **1.7932703932910243e-16**, files `…/grader_controls/F_{P,S}_planted.json` |
| `grader_plant_X_struct_P` / `_S` | `grader_plant_X_seen` **true**, `read_back` **0.001234**, and `G-STRUCT` **flipped to `GATE FAIL`** on the planted copy — constraint `thickcon`. **The gate is shown failing**, which is what makes it load-bearing |
| `grader_plant_cells` | `on_disk_before_plant` **4032**, `read_back` **4039**, `want` **4039** — the mesh-cell reader proved able to see a changed count |
| `grader_plant_c5` | `grader_plant_c5_seen` **true** on arm `X-S`, `n_lines_real` **614**, `positive_sites` **1**, `negative_sites` **0**, `banner_excluded_and_counted` **1** |
| `instrument_ctrl_P` | `both_directions` **true**, `n_zero_entries_read` **23**, `want` **0.617** |

**`CLAUDE.md` rule 3 was exercised in both directions on this item** — the reader was shown seeing a
plant, and the gate was shown flipping under one. **The `grader_plant_c5` entry is the SO-1a
false-positive class handled correctly**: one `trapFpe` enablement banner seen, excluded, **and
counted** so the exclusion is auditable rather than invisible.

## 4.3 Predictions — copied verbatim from `predictions`

**HIT (ten of eleven):** `P1_cells_4032`, `P2_constraint_baselines_all_near_1`,
`P3_G_CV_feasible_at_the_graded_design`, `P4_patched_row_constraint_jacobians_PASS`,
`P5_SHIPPED_row_ALSO_PASS_and_divergence_is_zero`, `P6_G_STRUCT_exact_zero_both_rows`,
`P7_G_TB_trivial_baseline_FAILS_as_registered_on_PATCHED`,
`P8b_mesh_wall_le_120s`,
`P9_age_datum_resolves_to_the_COMPRESSED_twin_on_every_solver_arm`,
`P10_X_arm_cheap_no_flow_adjoint_per_constraint_row`.
**MISS (one):** `P8_total_core_min_band` (§7).

`P10`'s `HIT` is a measured finding and was registered as one: the pre-registration states that a
miss *"means each of the 23 geometric rows costs a flow adjoint … a real and useful finding about
mphys's handling of flow-independent constraints"* (`PREREGISTRATION.md:181`). **It did not.** The
`X` arms cost **0.333 core-min** each (§7).

# 5. TOOLCHAIN PER ROW — `G9` reads `PASS`

From `/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient/ledger.txt`
(per-arm `ARM=` rows and the `D4S_IDWARP_SO_MD5:` line that follows each).

| row | arms | image | digest | `libidwarp.so` md5 |
|---|---|---|---|---|
| **SHIPPED** | `MESH` (`:3`), `X-S` (`:7`), `G-S` (`:11`) | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** (`:5`, `:9`, `:13`) |
| **PATCHED** | `X-P` (`:15`), `G-P` (`:19`) | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`** (`:17`, `:21`) |

`G9_toolchain.verdict` = **`PASS`**.

# 6. THE STOPPED FIRST LAUNCH — `SO2a-DRIVER-DEF-1`, and why the graded chain is a second launch

**This item was launched twice, and the first launch bought nothing.** The record is in this
directory, in git: `curriculum_SO2a/SUPERVISOR_STOP.txt`, dated **2026-08-30T231849Z**, opening
*"STOPPED BY: dafoam-supervisor, personally, [lab-attributed]. Not a crash, not a cap, not an OOM,
and NOT a physics failure — no solver ever started."*

Copied from that file: `so2a_chain_driver.sh:143` called `$HERE/so2a_aggregate_memory.py`, which
**did not exist on disk and had never existed in any commit on any branch**; `AGG` was empty on
every poll, the `json.load` raised, and the driver was **guaranteed** to poll to the 14400 s bound
and write `chain=BLOCKED_AGGREGATE` at the first arm. Measured before the stop: **9 poll lines,
every payload empty**; **0 of 5 arm directories**; **0 containers ever created**; ledger holding
`ITEM=SO2a` and one `STAGED` line only. **Spend: wall 323 s, ranks 1, SOLVER COMPUTE ZERO
core-min**, booked as **waste, named**.

**The chain graded in §1–§5 is the relaunch.** The ledger's `STAGED stamp=20260830T231326Z`
(`ledger.txt:2`) is the stopped launch's staging; `STATUS.chain:1` records the surviving chain
starting at `20260831T000507Z` and completing at `20260831T002529Z`.

**The freeze's own blind spot, from the same file:** *"§7's instrument table freezes EIGHT files and
DOES NOT LIST THE SCRIPT THAT IMPLEMENTS THAT GATE. The §7 md5-agreement control therefore read
'eight of eight AGREE' while the ninth dependency was absent. A GATE WAS FROZEN WITHOUT ITS
IMPLEMENTATION. An instrument table that enumerates instruments but not their dependencies can be
complete and wrong at the same time."* **That is `CLAUDE.md` rule 14's shape at the freeze level**,
and the repair's carry-forward has a call site rather than a memory:
`scripts/sweep_dafoam_script_references.py`, validated against a known positive first
(`docs/COST_CALIBRATION.md`, row `C-20260831T163653.411934Z-257629d0`).

# 7. COST — rule 12

Per-arm figures copied from `ledger.txt` and from `gates.G10_caps.per_arm`:

| arm | row | rc | wall s | ranks | core-min | cap | ratio actual/predicted (artefact's own field) | ledger line |
|---|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 10 | 1 | **0.167** | 5.0 | 0.8789 | `:3` |
| `X-S` | SHIPPED | 0 | 20 | 1 | **0.333** | 12.0 | 0.222 | `:7` |
| `G-S` | SHIPPED | 0 | 142 | 1 | **2.367** | 25.0 | 0.789 | `:11` |
| `X-P` | PATCHED | 0 | 20 | 1 | **0.333** | 12.0 | 0.222 | `:15` |
| `G-P` | PATCHED | 0 | 121 | 1 | **2.017** | 25.0 | 0.6723 | `:19` |

| | |
|---|---|
| **Actual, MEASURED** | **5.2170000000000005 core-min** — `gates.G10_caps.total_core_min`; `ceiling` **79.0**; `verdict` **`PASS`**; `not_measured` `[]`; no arm `crossed` |
| Registered estimate | **9.19 core-min point, band [5.5, 28.0]**, ceiling **79.0 = Σ caps**, *"asserted in `main()`"* — `curriculum_SO2a/PREREGISTRATION.md:150`; the same in `verification/queue/dafoam/launched/SO2a_chain.json` (`cost_core_min_estimate` 9.19, `cap_core_min_registered` 79.0, `prereg_commit` `5f0e083e3c9f08be1f2920ee2c95c1b323b4f1c4`) |
| Prediction on cost | `P8_total_core_min_band` = **`MISS`** — the measured 5.217 falls **below** the band's lower edge of 5.5 |
| Contention, on record | the ledger's own `siblings_pre` / `siblings_post` fields record a live sibling container `d6ra2_ACC_mp_20260830T235332Z_1606819` on **four of five arms** (`:3`, `:7`, `:11`, `:15`); `G-P` (`:19`) ran with `siblings_pre=[]`. **This record copies the field and draws no conclusion from it** — attributing the gap is the calibration row's job, and the row does not exist |
| Waste | the stopped first launch (§6): **323 wall s, ranks 1, SOLVER COMPUTE ZERO core-min**, plus an 8 GiB reservation held for the 323 s. Named separately and **never folded into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6) |
| GPU | **0 GPU-h** — no GPU instance was launched |

**Dollars: $0.004461 — DERIVED, NOT MEASURED.** `cost_basis` **REPORTED-BY-OWNER, NOT MEASURED**;
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Stated plainly: this is
THIS RECORD'S ARITHMETIC** on the on-record 5.217 core-min at the recorded c7a.4xlarge rate of
$0.0513/core-h (`CLAUDE.md` rule 12), **not a figure copied from any artefact.**

**The whole-item actual/predicted ratio is likewise THIS RECORD'S ARITHMETIC and is stated once,
labelled:** 5.217 ÷ 9.19 = **0.5676**. It is offered only because all five registered arms ran to
`rc=0`, so numerator and denominator price the same program — the condition that made the same
division dishonest for `SO-3a` and for `D6R`. **The gap is not attributed here**; §4.3's `P10` HIT
and the contention field above are the two candidate terms and choosing between them is the
calibration row's work.

> **⚠ NO CALIBRATION ROW EXISTS FOR SO-2a's OWN GRADED CHAIN SPEND, AND ONE IS OWED — AND THE ROWS
> THAT DO MENTION SO-2a WILL MISLEAD A READER WHO ARRIVES COLD.**
>
> `docs/COST_CALIBRATION.md` carries two SO-2a rows: the struck **`C-215`** at **:300** and its
> landed replacement **`C-20260831T163653.411934Z-257629d0`** at **:315**. **Both are the
> instrument repair of §6, not this item**, and both say so in their own words: *"THIS ROW IS NOT
> THE SO-2a ITEM."* Their predicted cell reads **"NONE REGISTERED"** and their ratio cell reads
> **"NO RATIO. Nothing was predicted, so nothing is divided."** Their measured figure, **0.367
> core-min**, is instrument time — four timed drives — and **$0.00031** derived, **not the item's
> solver spend.**
>
> **The carried sentence to watch:** both rows also state *"SO-2a has bought nothing and its label
> remains `PENDING`."* That was true when first written on **2026-08-30**, before the relaunch. The
> replacement row landed **2026-08-31T16:36:53Z** and carries the struck row's data cells
> **byte-for-byte by design**, so the sentence travelled forward past the grade artefact of
> **2026-08-31T00:25:29Z** that this record cites. **The row is not wrong about its own subject —
> it is scoped to the repair and says so — but a reader who meets that sentence without §1 of this
> file will take away the wrong verdict.** It is **flagged here and not fixed**: editing another
> team's landed ledger row is not a scribe's call, and the row's byte-for-byte carry is itself a
> deliberate integrity property. **Writing the item's own row is the supervisor's**, and rule 11
> requires its id to be derived inside the committing invocation (or allocated by
> `scripts/append_record.py`, as `:315` was).

# 8. WHERE THE FULL READINGS LIVE

1. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO2a-a1-naca0012-geometric-constraint-gradient/SO2a_grade_20260831T002529Z.json`**
   (outside git) — the verdict of record, `rows`, all ten gate objects with their per-pair tables,
   `birth_register`, `controls`, `completion`, `predictions`, `age_datum_resolution`.
2. **`…/ledger.txt`**, **`…/STATUS.chain`**, the five `STATUS.<arm>` files, the per-arm
   `*.log` / `*.inspect.txt` / `*.cpu.jsonl`, the five arm directories, and **`…/grader_controls/`**.
3. **`cases/dafoam/ladder-a/A1/curriculum_SO2a/PREREGISTRATION.md`** (this directory, frozen) —
   the gates, bands, caps, the anchor table at **:134–:136**, the cost table at **:150**, the
   predictions at **:176–:181**, the instrument table at **:307**, and **ADDENDUM A** at the foot
   with its prefix proof `so2a_addendum_prefix_proof.txt`.
4. **`curriculum_SO2a/SUPERVISOR_STOP.txt`** — §6 in full, in git, in this directory.
5. **`curriculum_SO2a/so2a_aggregate_memory_REFUSAL_EVIDENCE.txt`** (15 of 15 checks, rc 0),
   `so2a_grade_selftest_evidence.txt`, `so2a_groot5_selftest_evidence.txt`,
   `so2a_c5_trapfpe_confirmation_evidence.txt`, and the zero-delta
   `so2a_aggregate_memory_DELTAS_from_so1a.diff` — the instrument evidence, in git, here.
6. **`docs/COST_CALIBRATION.md`** rows `:300` and `:315` — the repair, with the caveat in §7.
7. **`cases/dafoam/INDEX.md`**, Addendum 2026-08-31 — this item's census row.

**If any figure in this record disagrees with the grade JSON or the ledger, the JSON and the ledger
are right.**

# 9. What this record does and does not do

**It does** give SO-2a an item-level record where it had none, so a reader arriving at this
directory finds the item's verdict instead of a pre-registration, a stop note and a silence.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, score any
prediction, run any comparator, touch the preserved run root, or add any number that was not
already written in a cited artefact — with the two arithmetic exceptions labelled at their point of
use in §7.

**It does not** fill the calibration row it flags as owed, edit the two landed rows whose carried
sentence it flags, or attribute the cost gap (§7). **It does not** touch
`docs/dafoam/GRADING_CHAIN.md`, `docs/dafoam/README.md` §3, `cases/dafoam/INDEX.md` or any frozen
document in this directory.

**It establishes nothing about the physics beyond what §4 copies from the comparator's own output**
— and §2 is explicit that the zero shipped/patched divergence is a statement about
flow-independence, not about the IDWarp defect's absence elsewhere. No solver ran for this record;
**zero solver core-minutes** were spent writing it.
