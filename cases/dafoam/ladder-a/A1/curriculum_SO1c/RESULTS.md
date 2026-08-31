# Curriculum item SO-1c — np-invariance of the A1 NACA0012 gradient at the optimum: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-31 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** SO-1c never landed one. Its comparator wrote a `NOT A RESULT` into a
preserved run root **outside git**, and until today that verdict of record existed only there and in
one census row — `docs/dafoam/GRADING_CHAIN.md` bullet 8 in the live, and
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
> not supply one. **The one place where this record states arithmetic rather than a copied figure
> is §5's dollar total, labelled as such at the point of use.** A results record that quietly
> derives a fresh figure is a second grading of the same item wearing a scribe's clothes.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings are **the
> morning report's**, matched literally, so a curriculum record must not wear them. This record
> follows the family's own convention — `curriculum_SO1a/RESULTS.md`,
> `curriculum_AV1R/RESULTS.md`, `A2/curriculum_D6R/RESULTS.md`.

---

# 1. Item verdict — `NOT A RESULT`, by comparator refusal

| | |
|---|---|
| **Item verdict** | **`NOT A RESULT`** |
| Grading artefact of record | `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv/SO1c_grade_20260831T171139Z.json` → `verdict` |
| Comparator exit | `grader_rc=2` — `…/STATUS.chain:5`, note `comparator-exit-status-NOT-the-verdict` |
| Gate readings composed | **none** — the comparator refused at `G1` before composing any gate |

**The refusal, verbatim** from `SO1c_grade_20260831T171139Z.json` → `refusal` (the whole file is
three keys: `item`, `verdict`, `refusal`), reproduced identically in
`…/SO1c_grade_20260831T171139Z.out` line 1:

    {"REFUSE": "G1", "detail": {"arm_absent_from_ledger": "Ns-P",
     "inspect_record_candidates": [],
     "note": "exactly one surviving inspect record may stand in for a missing row.  R-RC covers
     the rc RECORD only: DIGEST, cpuset and core_min are PHYSICS fields and have no fallback
     channel here."}}

**The comparator refused rather than degrading**, which is the registered behaviour
(`CLAUDE.md` rule 4: comparators *refuse (exit 2) rather than degrade*). Its own note says why the
one permitted fallback could not apply: `inspect_record_candidates` is **empty**, so there was no
surviving inspect record to stand in, and `DIGEST`, `cpuset` and `core_min` are named as **physics
fields with no fallback channel at all**.

# 2. THE ROWS — NO TWO-ROW VERDICT EXISTS FOR THIS ITEM, and that is stated rather than partially reported

`GRADING_CHAIN.md` bullet 7: *"Every item is TWO ROWS, SHIPPED and PATCHED; an item with only one
row executed yields no verdict at all, not a partial one."*

| registered arm | row | what happened | source |
|---|---|---|---|
| `MESH` | SHIPPED | **ran, `rc=0`** | `ledger.txt:3`; `STATUS.chain:2` |
| `Ns-P` | PATCHED | **ABORTED IN THE LAUNCHER, `rc=5`. No container was created and no ledger row was written.** | `STATUS.chain:3`; `STATUS.Ns-P:2`; `Ns-P_launch.out:13-14` |
| `Ni-P` | PATCHED | **NEVER RAN** | `STATUS.chain:4`, `chain=STOPPED_AT_FIRST_NONZERO arm=Ns-P rc=5` |
| `Ns-S` | SHIPPED | **NEVER RAN** | same |
| `Ni-S` | SHIPPED | **NEVER RAN** | same |

**No solver arm ran on either row.** `MESH` is a mesh-generation arm stamped `ROW=SHIPPED`; it
produces no gradient. **There is therefore no SHIPPED row verdict and no PATCHED row verdict, and
none is manufactured here.** The grade artefact carries no `rows` key at all — the comparator
refused before it could write one.

# 3. CAUSE CLASS — **INSTRUMENT**, carried verbatim from `GRADING_CHAIN.md`

`docs/dafoam/GRADING_CHAIN.md`, cause-class table, row **SO-1c**, copied without alteration:

> | **SO-1c** | `NOT A RESULT` | **INSTRUMENT** | Row-label break in call sites the R8 repair never swept. |

**This record carries that class and does not re-derive it.** For a reader who wants to see the
break itself, the launcher printed it. Verbatim from
`/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv/Ns-P_launch.out`, the last
two lines (**:13** and **:14**):

    G-OPTDEP artefact row 'P' != this arm row 'PATCHED'
    ABORT G-OPTDEP the optimum artefact for row PATCHED is unparseable or is another row's. REFUSED.

**The row label the guard was handed (`PATCHED`) and the row label the upstream optimum artefact
carries (`P`) are the same row under two names.** The guard did exactly what it was built to do —
it refused to grade a row against another row's optimum — and the two vocabularies had never been
reconciled at that call site. `cases/dafoam/INDEX.md`'s SO-1c row states the connection to the
refusal in §1: *"the break is why the arm is absent from the ledger under the label the grader looks
for."*

**The nine lines above the abort are all guards passing**, which is what makes the class
`INSTRUMENT` rather than anything else: `D4S_G_ROOT_PASS`, `D4S_G_ROOT5_PASS`,
`SO1C_G_CAP_PREREG_PASS` (`sum_of_caps=125.000000 ceiling=125.0`, head channel `AGREES`),
`D4_CAP_ASSERT`, the four staged-file `OK` lines, `SO1C_DECOMP_SELECTED` (scotch,
md5 `816f5ba44075fde47fa5db4269877bc8`), `D4S_G_ROW_PASS` and `D4_IMAGE_OK`. **The chain died on a
label, one line after proving its image, its caps and its inputs.**

**No physics was reached, and no physics claim, favourable or adverse, rests on this item.**

# 4. TOOLCHAIN — one row stamped, one row NOT ON RECORD

From `/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv/ledger.txt` and
`Ns-P_launch.out`.

| row | image | digest | `libidwarp.so` md5 |
|---|---|---|---|
| **SHIPPED** (`MESH`, `ledger.txt:3`, `:5`) | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** |
| **PATCHED** (`Ns-P`, `Ns-P_launch.out:11-12`) | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **NOT ON RECORD FOR THIS ITEM** |

**The PATCHED row's `libidwarp.so` md5 is not on record for SO-1c and this record does not supply
one.** The `D4S_IDWARP_SO_MD5` line is printed from *inside* the container, and no container was
created on this row (`STATUS.Ns-P:2`, `source=launcher_exit=docker_inspect_ExitCode`). The image and
digest were verified by the launcher before the abort and are copied above; the `.so` md5 was not.
A reader who needs the PATCHED `.so` md5 for this image must take it from an item where that row
actually ran — the sibling `curriculum_SO1cR` ledger carries it — **not from here.**

# 5. COST — rule 12

| | |
|---|---|
| **Actual, MEASURED** | **0.633 core-min**, ranks 1, wall 38 s — the single `ARM=MESH` row at `ledger.txt:3` |
| Registered estimate | **40.2 core-min**, ceiling **125.0** — `curriculum_SO1c/PREREGISTRATION.md:197`; the same figures in the in-git queue entry `verification/queue/dafoam/launched/SO1c_chain.json` (`cost_core_min_estimate` 40.2, `cap_core_min_registered` 125.0, `prereg_commit` `bd7f68d67f3de225eac6425650f2fd4cda1dd579`) |
| Registered cap manifest | `SO1C-CAP-MANIFEST v1 MESH=5.0 Ns-P=30.0 Ni-P=30.0 Ns-S=30.0 Ni-S=30.0 CEILING=125.0 RANKS_N=4` — `PREREGISTRATION.md:6` |
| Waste | **the whole 0.633 core-min.** The chain produced no gradeable output, so nothing it bought was recoverable. The sibling row for SO-1cR states this from the other side, naming *"SO-1c's 0.633 core-min"* as waste to be booked **on its own row's item** and explicitly **not folded** into SO-1cR's ratio — `docs/COST_CALIBRATION.md`, row `C-20260831T195247.871530Z-5dbe03c5` |
| GPU | **0 GPU-h** — no GPU instance was launched |

**Dollars: $0.000541 — DERIVED, NOT MEASURED.** `cost_basis` **REPORTED-BY-OWNER, NOT MEASURED**;
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Stated plainly: this is
THIS RECORD'S ARITHMETIC** on the on-record 0.633 core-min at the recorded c7a.4xlarge rate of
$0.0513/core-h (`CLAUDE.md` rule 12), **not a figure copied from any artefact.**

**NO ACTUAL/PREDICTED RATIO IS STATED, AND THE OMISSION IS DELIBERATE.** The registered 40.2 prices
**five** arms; the measured 0.633 bought **one**, and four never started. `0.633 ÷ 40.2` would read
as a 98.4 % underspend while describing a chain that never ran. That figure is on record nowhere,
and this lane will not manufacture one. **This is the same refusal the family's own ledger already
wrote for the sibling item SO-3a**, in that row's words: *"it is named here PRE-EMPTIVELY so nobody
computes it later."*

> **NO CALIBRATION ROW EXISTS FOR SO-1c, AND ONE IS OWED.** `docs/COST_CALIBRATION.md` contains
> **zero** rows for this item — its only two occurrences of the string `SO-1c` sit inside the
> **SO-1cR** row, which names this item's 0.633 core-min as waste belonging on a row that does not
> yet exist. **Writing it is not a scribe's call**, it is the supervisor's, and rule 11 requires its
> id to be derived inside the committing invocation (or allocated by `scripts/append_record.py`).
> **It is flagged, not filled.**

# 6. WHAT THIS ITEM DID NOT BUY

**It did not buy an np-invariance reading.** The item's whole subject — the gradient at the
optimum at np = 4 under two decomposition methods — required four solver arms, and **none ran**.

**It did not buy a two-row verdict** (§2), **a gradient verdict, an FD table, a trivial-baseline
reading, or any gate at all.** The comparator refused at `G1`, the completion gate, which is the
first gate in the chain.

**What it DID buy, plainly:** a demonstration that the row-label vocabulary is not uniform across
this family's call sites, caught by a guard that refused rather than grading the wrong row's
optimum. The successor `curriculum_SO1cR` carries `so1cr_rowlabel_sweep.py` and
`so1cr_rowlabel_sweep_evidence.txt` in git, and ran the same five arms to `PASS` on both rows.

# 7. WHERE THE FULL READINGS LIVE

1. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv/SO1c_grade_20260831T171139Z.json`**
   (outside git) — the verdict of record and the refusal, in three keys.
2. **`…/SO1c_grade_20260831T171139Z.out`**, **`…/ledger.txt`**, **`…/STATUS.chain`**,
   **`…/STATUS.Ns-P`** and **`…/Ns-P_launch.out`** — the refusal, the one ledger row, the chain
   stop and the guard trace quoted in §3.
3. **`cases/dafoam/ladder-a/A1/curriculum_SO1c/PREREGISTRATION.md`** (this directory, frozen) —
   the gates, bands, caps, the cost table at **:197** and the cap manifest at **:6**.
4. **`cases/dafoam/ladder-a/A1/curriculum_SO1cR/`** — the successor: `PREREGISTRATION.md`,
   `so1cr_rowlabel_sweep.py`, `so1cr_rowlabel_sweep_evidence.txt`, and its own `RESULTS.md`.
5. **`docs/dafoam/GRADING_CHAIN.md`** — the cause-class table row carried in §3.
6. **`cases/dafoam/INDEX.md`**, Addendum 2026-08-31 — this item's census row.

**If any figure in this record disagrees with the grade JSON or the ledger, the JSON and the ledger
are right.**

# 8. What this record does and does not do

**It does** give SO-1c an item-level record where it had none, so a reader arriving at this
directory finds the item's verdict and its cause class instead of a pre-registration and a silence.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, run any
comparator, touch the preserved run root, or add any number that was not already written in a cited
artefact — with the one arithmetic exception labelled at its point of use in §5.

**It does not** fill the calibration row it flags as owed (§5), supply the PATCHED `.so` md5 it
records as absent (§4), or compute the ratio it refuses (§5). **It does not** touch
`docs/dafoam/GRADING_CHAIN.md`, `docs/dafoam/README.md` §3 or `cases/dafoam/INDEX.md`.

**It establishes nothing about the physics** — no physics was reached. No solver ran for this
record; **zero solver core-minutes** were spent writing it.
