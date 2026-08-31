# Curriculum item SO-3a — the A1 NACA0012 alpha-multipoint gradient, three operating points at fixed shape: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-31 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** SO-3a never landed one. Its comparator wrote a `NOT A RESULT` into a
preserved run root **outside git**, and until today that verdict of record existed only there, in
one calibration row and in one census row — `docs/dafoam/GRADING_CHAIN.md` bullet 8 in the live,
and `cases/dafoam/INDEX.md`'s 2026-08-31 SO-series addendum, which names this item among six in that
state.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no gate was evaluated, no artefact was written, no preserved run root was
> touched, and **zero solver core-minutes were spent.** Every verdict, gate reading, band, count,
> refusal string and cost figure below is **copied from an existing artefact and cited to it by
> absolute path and by JSON key, ledger field or line number.** Where a figure a reader would want
> is **not** on record, this document says so and says where a reader would have to go — it does
> not supply one. **This record states NO arithmetic of its own.** Its cost figure, its dollar
> figure and its refusal to state a ratio are all **copied** from a landed calibration row. A
> results record that quietly derives a fresh figure is a second grading of the same item wearing a
> scribe's clothes.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings are **the
> morning report's**, matched literally, so a curriculum record must not wear them. This record
> follows the family's own convention — `curriculum_SO1a/RESULTS.md`,
> `curriculum_SO3aR/RESULTS.md`, `A2/curriculum_D6R/RESULTS.md`.

---

# 1. Item verdict — `NOT A RESULT`, and the stop marker's `PENDING` IS NOT IT

| | |
|---|---|
| **Item verdict** | **`NOT A RESULT`** |
| Grading artefact of record | `/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient/SO3a_grade_20260831T184321Z.out` |
| **There is NO `.json` for this item** | the `.out` is the only grade artefact on disk. `cases/dafoam/INDEX.md`'s addendum records this as one of its two named gaps: *"SO-3a and SO-3aR have `.out` grade artefacts and NO `.json`. Every other SO item in this table has both"* |
| Comparator exit | **`grader_rc=2`** — `…/STATUS.chain:6`, note `comparator-exit-status-NOT-the-verdict` |
| Gate readings composed | **none** — the comparator refused at `G1`, the first gate |

**WHAT THE COMPARATOR ACTUALLY WROTE**, verbatim, both lines of
`SO3a_grade_20260831T184321Z.out`:

    NOT A RESULT -- the comparator REFUSED
    {"REFUSE": "G1", "detail": {"C3_artefact_absent": "/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient/X-S/so3a_X.json", "arm": "X-S"}}

**And the chain said it independently**, `…/STATUS.chain:5`:
`chain=NOT A RESULT declared=5 executed=1 chain_rc=2`.

## 1.1 THE STOP MARKER SAYS `PENDING`, AND `PENDING` IS NOT AN ITEM VERDICT

`…/SO3a_STOP_MARKER.json` carries `"verdict": "PENDING"`. **That is a display/queue state and it is
never an item verdict** (`CLAUDE.md` rule 1: *"`PENDING` is a display/queue state … use it for 'not
yet run', never to soften a `GATE FAIL`"*; `VERIFICATION_CHARTER.md` §9; `REPORTING` §2 rule 5
reserves the form `PENDING: <path>`). **The marker says so itself in the adjacent key** —
`"verdict_source": "NO READABLE COMPARATOR VERDICT AT THIS ADDRESS"`, with
`"grade_json_error": "registered grade artefact ABSENT at …/SO3a_grade_20260831T184321Z.json"`.
**The marker was looking for the `.json`, did not find one, and honestly reported that it had no
verdict to display — it was not asserting that the item had none.** The comparator's own `.out`,
quoted above, is the verdict of record.

The rest of the marker, copied: `chain_rc` **2**, `stages_declared` **5**, `stages_executed` **1**,
`stages_short` **4**, `truncated` **true**, `G5J` **"NOT PRESENT IN THE ARTEFACT"**, `rows`
**"NOT PRESENT IN THE ARTEFACT"**, `marker_version` **1**, `written_utc`
**2026-08-31T18:43:21Z**. **The sibling `curriculum_SO3aR/RESULTS.md` §1 makes the identical
distinction on its own marker**, and `cases/dafoam/INDEX.md` quotes it doing so.

# 2. THE ROWS — NO TWO-ROW VERDICT EXISTS FOR THIS ITEM

`GRADING_CHAIN.md` bullet 7: *"Every item is TWO ROWS, SHIPPED and PATCHED; an item with only one
row executed yields no verdict at all, not a partial one."*

| registered arm | row | what happened | source |
|---|---|---|---|
| `MESH` | SHIPPED | **ran, `rc=0`** | `ledger.txt:3`; `STATUS.chain:2` |
| `X-S` | SHIPPED | **ran and REFUSED INSIDE THE CONTAINER, `rc=2`.** The container started; the extractor refused before touching physics | `ledger.txt:7`; `STATUS.chain:3`; `X-S_20260831T184310Z_277867.log` |
| `F-S` | SHIPPED | **NEVER RAN** | `STATUS.chain:4`, `chain=STOPPED_AT_FIRST_NONZERO arm=X-S rc=2` |
| `X-P` | PATCHED | **NEVER RAN** | same |
| `F-P` | PATCHED | **NEVER RAN** | same |

**NOT ONE PATCHED ARM RAN.** **There is therefore no PATCHED row verdict, no SHIPPED row verdict,
and none is manufactured here** — the `SHIPPED` arm that started refused before producing the
artefact its row would be graded on. The stop marker's `rows` field says the same thing in the
artefact's own words: **`"NOT PRESENT IN THE ARTEFACT"`.**

# 3. CAUSE CLASS — **INSTRUMENT**, carried verbatim from `GRADING_CHAIN.md`

`docs/dafoam/GRADING_CHAIN.md`, cause-class table, row **SO-3a**, copied without alteration:

> | **SO-3a** | `NOT A RESULT` | **INSTRUMENT** | Unfilled fail-closed producer pin; extractor refused before physics. `SO3a_grade_…out`, `so3a_xf.py:111`. |

**This record carries that class and does not re-derive it.**

## 3.1 The pin, at the line the class cites — and it did exactly what it was written to do

`cases/dafoam/ladder-a/A1/curriculum_SO3a/so3a_xf.py:111` (frozen, and not edited by this record)
reads, in full:

    PRODUCER_MD5 = "UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED"

Its own comment block at **:102–:110** explains the design, verbatim in part: *"`so3a_runScript.py`
is section 7 row 5 and is built AFTER this file in the registered build order, so at this file's
birth the pin is a SENTINEL THAT CANNOT MATCH ANY MD5 — 32 hex digits is the shape of an md5 and
this string is not one … `main()` REFUSES (exit 2) rather than running against an unpinned producer.
A placeholder that could PASS would be the SO2a-DRIVER-DEF-1 shape … The pin is set at the Stage-2
amendment."*

**The pin was never set at Stage 2, and the sentinel fired.** From the arm's own log,
`…/X-S_20260831T184310Z_277867.log`:

    SO3A_XF REFUSE producer md5 c0821199159026ec597549ee034b73ac != frozen UNSET-PRODUCER-PIN-SENTINEL-FAILS-CLOSED

**THE PIN WORKED, AND THE MD5 IT REJECTED WAS CORRECT.** That is the landed calibration row's own
finding, quoted in §5 — the failure is that the sentinel was never replaced, not that the guard
misfired. **A fail-closed sentinel that fires is a working sentinel**; the defect is a build-order
step that was registered and not executed.

**`INSTRUMENT` is not `PHYSICS-FAIL`.** Only `PHYSICS-FAIL` and `MODEL-LIMIT` say anything about the
lab's ability to do physics (`GRADING_CHAIN.md`, cause-class preamble). **No physics was reached and
no physics claim, favourable or adverse, rests on SO-3a.**

## 3.2 The census that could not see it — carried from the calibration row, not re-derived

The landed row's attribution cell, verbatim:

> *"The pin census reported 13 of 13 because it counts md5-SHAPED constants and this sentinel is
> deliberately not md5-shaped — the property that makes it safe against false matching made it
> invisible to the census. Successor SO-3aR carries a census that sweeps BY ROLE rather than by
> shape."*

**This is `CLAUDE.md` rule 14's shape at the audit level**: the pre-registration's own pin audit
(`PREREGISTRATION.md`, the `md5_pins` note carried into
`verification/queue/dafoam/launched/SO3a_chain.json`) asserted *"13 of 13 pins DECLARED in
`so3a_chain_driver.sh` are DRIVEN and EQUAL the files they pin"* and was **true and insufficient at
the same time** — the one pin that mattered lived in a different file and in a shape the counter
was built to skip.

# 4. TOOLCHAIN — one row stamped, one row NOT ON RECORD

From `/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient/ledger.txt`.

| row | arms | image | digest | `libidwarp.so` md5 |
|---|---|---|---|---|
| **SHIPPED** | `MESH` (`:3`), `X-S` (`:7`) | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** (`:5`, `:9`) — confirmed a second time inside the container, `X-S_…log`: `D4S_IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663` |
| **PATCHED** | — | **NOT ON RECORD FOR THIS ITEM** | **NOT ON RECORD** | **NOT ON RECORD** |

**No PATCHED arm ran, so no PATCHED image, digest or `.so` md5 exists for SO-3a, and this record
supplies none.** A reader who needs the PATCHED toolchain stamp for this image must take it from an
item where that row actually ran — the sibling `curriculum_SO2a` and `curriculum_SO1cR` ledgers
carry it — **not from here.**

**`G9` IS ALSO NOT ON RECORD.** The comparator refused before composing gates, so there is no
`G9_toolchain` verdict. The table above is the ledger's raw stamp, not a gate reading.

**Memory note, copied:** both arms ran at `memory=12g`, raised from this family's 4 g convention;
`PREREGISTRATION.md:46` registers the raise and states its arithmetic.

# 5. COST — rule 12, and the calibration row already exists

Per-arm figures copied from `ledger.txt`:

| arm | row | rc | wall s | ranks | core-min | cap | in-container deadline s | ledger line |
|---|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 10 | 1 | **0.167** | 5.0 | 300 | `:3` |
| `X-S` | SHIPPED | **2** | 10 | 1 | **0.167** | 15.0 | 900 | `:7` |

| | |
|---|---|
| **Actual, MEASURED** | **0.334 core-min** — copied from the landed calibration row: *"0.334 core-min MEASURED (MESH 0.167 rc=0 + X-S 0.167 rc=2)"* |
| **Dollars** | **`$0.0003` DERIVED at $0.0513/core-h, NOT MEASURED** — copied from the same row's own cell. `cost_basis` REPORTED-BY-OWNER; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Registered estimate | **22.0 core-min point, band [14.0, 60.0]**, ceiling **115.0 = Σ caps** (`MESH 5.0; X-S 15.0; X-P 15.0; F-S 40.0; F-P 40.0`) — `curriculum_SO3a/PREREGISTRATION.md:46-47, :136`; the same in `verification/queue/dafoam/launched/SO3a_chain.json` (`cost_core_min_estimate` 22.0, `cap_core_min_registered` 115.0, `prereg_commit` `1a06a7d6c5c750d7071a8400b54aaa1d6a0966ab`) |
| Registered dollars | point **$0.01881**, ceiling **$0.09832**, both DERIVED and NOT MEASURED — `PREREGISTRATION.md:47` |
| Waste | **the whole 0.334 core-min** — the row's own words: *"cleaned equals gross; the whole 0.334 is WASTE, since the chain produced no gradeable output"* |
| GPU | **0 GPU-h** — `PREREGISTRATION.md:47`: *"this item launches no GPU instance"* |

**The calibration row is LANDED, so every figure above is copied and none is derived here.**
`docs/COST_CALIBRATION.md`, row id **`C-20260831T195247.871598Z-a44a49da`**.

**AND THAT ROW REFUSES ITS OWN RATIO, PRE-EMPTIVELY.** Verbatim:

> *"REFUSED — NO RATIO IS COMPUTED AND THE REFUSAL IS THE HONEST ENTRY. The registered 22.0 prices
> FIVE arms; the measured 0.334 bought ONE completed arm and one refusal. 0.334/22.0 = 0.0152 would
> read as a 98.5 % underspend while describing a chain that never ran, so it is named here
> PRE-EMPTIVELY so nobody computes it later. The honest per-arm figures are MESH 0.167 against a
> 5.0 cap and X-S 0.167 against a 15.0 cap."*

**This record honours that refusal and states no ratio.** Its gap attribution, likewise copied:
**"NOT A MISPREDICTION AND NOT CONTENTION — INSTRUMENT."** The row's evidence cells: commit
`e64e6e0d`, `docs/LAB_STATE.md` S-22l, and `…/STATUS.chain` plus
`X-S_20260831T184310Z_277867.log`.

# 6. WHAT THIS ITEM DID NOT BUY

**It did not buy a multipoint gradient verdict.** The item's subject — `compute_totals` of
`J = Σᵢ wᵢ·CDᵢ` and of each `CLᵢ` with respect to a shared 8-component `shape` vector across three
angles of attack, with a central-FD table beside it at a step proved in the plateau per pair
(`PREREGISTRATION.md:39`) — required the two `X` arms and the two `F` arms. **The FD arms never
ran, so the charter's bright line was never satisfied and no gradient verdict is possible**
(`GRADING_CHAIN.md` bullet 4: *"No FD table, no gradient verdict."*).

**It did not buy `G5J`** — the stop marker records it as **`"NOT PRESENT IN THE ARTEFACT"`** — **nor
`G1`, `G-TB`, `G9`, `G10`, `G-M2` or any other gate.** All of them sit behind the extractor that
refused.

**It did not buy a planted-control reading.** No `grader_controls/` directory exists in this run
root; the comparator refused before any control could fire. **`CLAUDE.md` rule 3 is recorded here as
NOT EXERCISED, and `NOT EXERCISED` is not `PASS`.**

**It did not establish anything about the three-scenario primal-failure behaviour** that
`GRADING_CHAIN.md`'s D6R correction names as *"the one real physical phenomenon here … separate,
ungraded"*. That question belongs to `SO3D` and is untouched by this item.

**What it DID buy, plainly:** a fail-closed pin firing correctly on a producer it could not verify,
at a cost of **0.334 core-min** — and the audit finding in §3.2, that a pin census counting by
*shape* is blind to exactly the sentinel whose non-md5 shape makes it safe. The successor
`curriculum_SO3aR` carries a census that sweeps **by role**.

# 7. WHERE THE FULL READINGS LIVE

1. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO3a-a1-naca0012-alpha-multipoint-gradient/SO3a_grade_20260831T184321Z.out`**
   (outside git, **`.out` only — there is no `.json`**) — the verdict of record and the refusal,
   both lines quoted in §1.
2. **`…/SO3a_STOP_MARKER.json`** — the fourteen keys quoted in §1.1, including the `PENDING`
   display state and the `verdict_source` that disowns it.
3. **`…/ledger.txt`**, **`…/STATUS.chain`**, `STATUS.MESH`, `STATUS.X-S`, and
   **`…/X-S_20260831T184310Z_277867.log`** — the two arm rows, the chain stop, and the `SO3A_XF
   REFUSE` line quoted in §3.1.
4. **`cases/dafoam/ladder-a/A1/curriculum_SO3a/PREREGISTRATION.md`** (this directory, frozen) —
   the ten registered lines at **:39**, the cap at **:46**, the cost at **:47**, the anchor table
   at **:122–:136**, the aggregate gate at **:157**, the `P-COST` prediction at **:237**, and the
   cache-state term at **:138**.
5. **`cases/dafoam/ladder-a/A1/curriculum_SO3a/so3a_xf.py:102-111`** (this directory, frozen) — the
   pin and its comment block.
6. **`curriculum_SO3a/so3a_xf_drive_evidence.txt`**, **`so3a_xf_selftest.py`**,
   **`so3a_stage2_evidence.txt`** — the instrument evidence, in git, in this directory.
7. **`docs/COST_CALIBRATION.md`**, row `C-20260831T195247.871598Z-a44a49da` — the whole rule-12
   entry, quoted in §5.
8. **`docs/dafoam/GRADING_CHAIN.md`** — bullet 1 (a missing artefact is a gradable state; a
   malformed one is a refusal), bullet 8, and the cause-class table row carried in §3;
   **`cases/dafoam/INDEX.md`**, Addendum 2026-08-31 — this item's census row and the `.out`/`.json`
   gap.
9. **`cases/dafoam/ladder-a/A1/curriculum_SO3aR/`** and
   **`feasibility_SO3a_alpha/`** — the successor item and the feasibility note that precedes it,
   each with its own record.

**If any figure in this record disagrees with the grade `.out`, the ledger or the calibration row,
those are right.**

# 8. What this record does and does not do

**It does** give SO-3a an item-level record where it had none, so a reader arriving at this
directory finds the item's verdict, its refusal and its cause class instead of a pre-registration
and a silence — and finds, stated plainly, that the stop marker's `PENDING` is not that verdict.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, run any
comparator, touch the preserved run root, or add any number that was not already written in a cited
artefact. **It states no arithmetic of its own at all**, and it honours the calibration row's
pre-emptive refusal to state a ratio (§5).

**It does not** supply the PATCHED toolchain stamp it records as absent (§4), turn the ledger's
stamps into a `G9` reading (§4), or read `NOT EXERCISED` as `PASS` (§6). **It does not** touch
`docs/dafoam/GRADING_CHAIN.md`, `docs/dafoam/README.md` §3, `cases/dafoam/INDEX.md`,
`docs/COST_CALIBRATION.md`, or any frozen document in this directory — **`so3a_xf.py` in particular
is quoted and NOT edited**; filling its pin now would be a post-hoc change to a frozen instrument.

**It establishes nothing about the physics** — no physics was reached. No solver ran for this
record; **zero solver core-minutes** were spent writing it.
