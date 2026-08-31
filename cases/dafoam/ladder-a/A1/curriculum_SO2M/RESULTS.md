# Curriculum item SO-2M — the A1 NACA0012 moment gradient `d(CMZ)/d(shape, patchV)`: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-31 by a lane of the DAFoam team, on the supervisor's instruction, as this item's
FIRST results record.** SO-2M never landed one. Its comparator wrote a `NOT A RESULT` into a
preserved run root **outside git**, and until today that verdict of record existed only there and in
two census rows — `docs/dafoam/GRADING_CHAIN.md` bullets 5 and 8, and `cases/dafoam/INDEX.md`'s
2026-08-31 SO-series addendum, which names this item among six in that state.

> ## THIS IS A SCRIBE'S RECORD, AND THAT CONSTRAINS EVERY NUMBER IN IT
>
> **Nothing here was graded, re-graded, re-derived or computed by the lane that wrote it.** No
> comparator was run, no gate was evaluated, no artefact was written, no preserved run root was
> touched, and **zero solver core-minutes were spent.** Every verdict, gate reading, band, count,
> refusal string and cost figure below is **copied from an existing artefact and cited to it by
> absolute path and by JSON key, ledger field or line number.** Where a figure a reader would want
> is **not** on record, this document says so and says where a reader would have to go — it does
> not supply one. **The two places where this record states arithmetic rather than a copied figure
> are labelled as such at the point of use** (§6's item total and §6's dollar figure, and nothing
> else). A results record that quietly derives a fresh figure is a second grading of the same item
> wearing a scribe's clothes.
>
> **This lane wrote exactly one file in this directory — this one.** Every other file here, staged
> or not, was left untouched.

> **A note on this record's shape.** `REPORTING_CHARTER.md` §2's six fixed headings are **the
> morning report's**, matched literally, so a curriculum record must not wear them. This record
> follows the family's own convention — `curriculum_SO1a/RESULTS.md`,
> `curriculum_AV1R/RESULTS.md`, `A2/curriculum_D6R/RESULTS.md`.

---

# 1. Item verdict — `NOT A RESULT`, by the comparator's OWN CONTROL refusing

| | |
|---|---|
| **Item verdict** | **`NOT A RESULT`** |
| Grading artefact of record | `/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient/SO2M_grade_20260831T195531Z.json` → `verdict` |
| Comparator exit | **`grader_rc=2`** — `…/STATUS.chain:8`, note `comparator-exit-status-NOT-the-verdict` |
| Chain | **`chain=COMPLETE arms_bought=5 of 5`** — `…/STATUS.chain:7`. **Every registered arm ran and every one returned `rc=0`** |
| Gate readings composed | **none** — the comparator refused at the CONTROL stage, before composing any row |

**THE REFUSAL, VERBATIM**, from `SO2M_grade_20260831T195531Z.json` → `refusal` (the whole file is
three keys: `item`, `verdict`, `refusal`), reproduced identically in
`…/SO2M_grade_20260831T195531Z.out` line 1:

    {"REFUSE": "CONTROL", "detail": {"G5m_did_NOT_flip_to_GATE_FAIL_under_the_planted_copy":
     {"d_ref": -0.04976246220706002,
      "demonstrated": true,
      "direction": "B -- the GATE is shown to FLIP under a plant",
      "file": "/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient/grader_controls/X_PATCHED_g5m_planted.json",
      "flipped": false,
      "live_verdict": "PASS",
      "plant": 0.001234,
      "plant_is_sufficient": false,
      "plant_needed_to_cross_band_D": 0.002488123110353001,
      "planted_component": ["shape", 6],
      "planted_verdict": "PASS",
      "row": "PATCHED"},
     "note": "PREREGISTRATION.md section 7 direction B REFUSES unless G5m reads GATE FAIL on the
     planted copy.  The arithmetic above says whether the registered PLANT is large enough to cross
     band D on this row's smallest graded reference."}}

**Read plainly: the solve worked and the gate did not.** Five of five arms bought, every `rc=0`, a
live `G5m` reading of `PASS` on the PATCHED row — and the comparator **refused to report it**,
because the registered plant of `1.234e-03` could not move `shape[6]` across band D on a reference
of `-0.04976246220706002`. It needed **`0.002488123110353001`**, roughly twice what it had.
`plant_is_sufficient: false`. **A gate never shown failing is not known to be load-bearing**
(this item's own `PREREGISTRATION.md:89`, citing L-314), and the comparator enforced that against
its own result.

**The clause it enforced**, verbatim from `curriculum_SO2M/PREREGISTRATION.md:89` (frozen, and not
edited by this record):

> **Direction B (the GATE flips under the plant):** the comparator re-reads a **copy of the real X
> artefact** with `PLANT` added to one `d(CMZ)/d(shape)` entry and **REFUSES unless `G5m` FLIPS from
> its live verdict to `GATE FAIL` on that copy** … **A gate never shown failing is not known to be
> load-bearing** (L-314).

**`docs/dafoam/GRADING_CHAIN.md` bullet 5 cites this refusal by name as the family's live proof
that its planted controls are machinery and not decoration:** *"The refusal is live machinery, not
decoration."*

# 2. THE ROWS — both rows' arms ran, and NO PER-ROW VERDICT WAS EVER WRITTEN

`GRADING_CHAIN.md` bullet 7: *"Every item is TWO ROWS, SHIPPED and PATCHED."* For this item the arms
of **both** rows ran to completion, and the comparator still produced **no `rows` object at all** —
it refused first.

| arm | row | rc | ledger line |
|---|---|---|---|
| `MESH` | SHIPPED | **0** | `ledger.txt:3` |
| `X-S` | SHIPPED | **0** | `ledger.txt:7` |
| `G-S` | SHIPPED | **0** | `ledger.txt:11` |
| `X-P` | PATCHED | **0** | `ledger.txt:15` |
| `G-P` | PATCHED | **0** | `ledger.txt:19` |

**There is no `rows` key in `SO2M_grade_20260831T195531Z.json`, and this record does not construct
one.** The only row-scoped words anywhere in the artefact sit *inside the refusal detail* —
`"row": "PATCHED"`, `"live_verdict": "PASS"`, `"planted_verdict": "PASS"` — and **those are
control diagnostics, not row verdicts.** `live_verdict: PASS` records what `G5m` read on the
unplanted PATCHED copy at the moment the control ran; it was never composed into a row, never
combined with `G-TB`, `G-NZ`, `G1`, `G9` or `G10`, and it is **not** this item's PATCHED row verdict.
**Nothing in this record may be quoted as SO-2M having passed on the PATCHED row.** The SHIPPED
row has no reading at all, live or otherwise.

**The item verdict is `NOT A RESULT` and nothing softer is available.** Rule 1 fixes the vocabulary
and forbids adjectives; a clean solve behind a refused control is still `NOT A RESULT`.

# 3. CAUSE CLASS — **GATE-DESIGN**, carried verbatim from `GRADING_CHAIN.md`

`docs/dafoam/GRADING_CHAIN.md`, cause-class table, row **SO-2M**, copied without alteration:

> | **SO-2M** | `NOT A RESULT` | **GATE-DESIGN** | Every arm `rc=0`, physics clean; the **registered plant** was too small to cross its own band. The comparator was correct; the gate as registered was defective. |

**This record carries that class and does not re-derive it.** `GRADING_CHAIN.md` bullet 10 states
the defect's shape in the same document, and is likewise carried rather than re-derived:

> **⚠ FINDING — the planted control is registered per item, and has been registered wrong.**
> SO-2M's plant was inherited from a CD-scale item as a **bare absolute** and was never sized
> against the functional it had to perturb: `1.234e-03` is 33.76 % of a CD reference but only
> **2.48 %** of `CMZ`'s, and could not cross its own 5 % band. Fixed forward by the SO-2MR ruling —
> the plant is registered **relative**, `plant_i = K · (band_D/100) · |d_ref_i|`, as a rule fixed at
> freeze, never a number chosen after seeing an answer.

**`GATE-DESIGN` is not `PHYSICS-FAIL`, and the distinction is the whole point of Sanaa's GRADING
TRANSPARENCY ORDER.** Only `PHYSICS-FAIL` and `MODEL-LIMIT` say anything about the lab's ability to
do physics (`GRADING_CHAIN.md`, cause-class preamble). **No physics claim, favourable or adverse,
rests on SO-2M.** It is not evidence that the moment gradient is right and it is not evidence that
it is wrong.

**The successor is registered elsewhere and is not this record's to describe.**
`cases/dafoam/INDEX.md`'s SO-series addendum lists `ladder-a/A1/curriculum_SO2MR/` as **"none —
scripts only; NO `PREREGISTRATION.md` and NOT TRACKED at HEAD … no verdict, and none is claimed …
it is a peer's live, unfinished work"**. **This lane did not open, read, stage or touch that
directory**, and states its status only by copying that in-git census row.

# 4. THE CONTROLS THAT DID FIRE — five planted artefacts are on disk

The refusal is a **control** refusal, so what the controls actually did is the item's most useful
content. Five files sit in
`/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient/grader_controls/`:

| file | what it is, per `PREREGISTRATION.md` §7 |
|---|---|
| `X_PATCHED_g5m_planted.json` | the Direction-B copy named in the refusal — the one on which `G5m` did **not** flip |
| `X_SHIPPED_g5m_planted.json` | the same Direction-B copy for the SHIPPED row |
| `X_SHIPPED_gnz_zeroed.json` | the second Direction-B copy: `d(CMZ)/d(patchV[1])` forced to `0.0`, which must flip `G-NZ` to `GATE FAIL` |
| `G_PATCHED_planted.json`, `G_SHIPPED_planted.json` | the FD-side plants |

**The refusal's own `"demonstrated": true` records that the machinery ran** — the plant was
written, re-read from disk, and its effect on the gate measured. **What failed is the plant's size,
not the reader.** This is the opposite failure mode to a blind reader, and it is why the class is
`GATE-DESIGN`: the instrument saw everything it was asked to see and correctly reported that what it
was asked to see was not enough.

**`CLAUDE.md` rule 3 was EXERCISED on this item, and its result was a REFUSAL — recorded as a
refusal, never as a pass.**

# 5. TOOLCHAIN PER ROW

From `/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient/ledger.txt`
(per-arm `ARM=` rows and the `D4S_IDWARP_SO_MD5:` line that follows each).

| row | arms | image | digest | `libidwarp.so` md5 |
|---|---|---|---|---|
| **SHIPPED** | `MESH` (`:3`), `X-S` (`:7`), `G-S` (`:11`) | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** (`:5`, `:9`, `:13`) |
| **PATCHED** | `X-P` (`:15`), `G-P` (`:19`) | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`** (`:17`, `:21`) |

**`G9` IS NOT ON RECORD FOR THIS ITEM.** The comparator refused before composing gates, so there is
no `G9_toolchain` verdict, no per-arm `ok` flag and no comparison of the printed `.so` md5 against
the artefact's own. **The table above is the ledger's raw stamp, not a gate reading**, and this
record does not turn one into the other. A reader who needs `G9` graded on this data must go to a
successor item that grades the preserved root.

# 6. COST — rule 12

Per-arm figures copied from `ledger.txt`:

| arm | row | rc | wall s | ranks | core-min | cap | ledger line |
|---|---|---|---|---|---|---|---|
| `MESH` | SHIPPED | 0 | 11 | 1 | **0.183** | 5.0 | `:3` |
| `X-S` | SHIPPED | 0 | 61 | 1 | **1.017** | 12.0 | `:7` |
| `G-S` | SHIPPED | 0 | 121 | 1 | **2.017** | 25.0 | `:11` |
| `X-P` | PATCHED | 0 | 51 | 1 | **0.85** | 12.0 | `:15` |
| `G-P` | PATCHED | 0 | 131 | 1 | **2.183** | 25.0 | `:19` |

| | |
|---|---|
| **Item total** | **NOT ON RECORD.** The comparator refused before writing a `G10_caps` block, so **no artefact carries a total for this item.** *Labelled arithmetic:* the five rows above sum to **6.250 core-min** — **THIS RECORD'S ARITHMETIC on five on-record figures, and NOT a figure any artefact prints** |
| Registered estimate | **10.30 core-min table total, registered POINT 11.0 carrying margin**, **CEILING 79.0** — `curriculum_SO2M/PREREGISTRATION.md:118`; the same point and cap in `verification/queue/dafoam/launched/SO2M_chain.json` (`cost_core_min_estimate` 11.0, `cap_core_min_registered` 79.0, `prereg_commit` `f1a723ac3a0d8da5c9e54ab7a0a80127ab366f26`) |
| Registered dollars | **point 11.0 core-min = 0.18333 core-h = $0.009405**, DERIVED and NOT MEASURED — `PREREGISTRATION.md`, the paragraph following the cost table |
| No arm crossed its cap | every `core_min` above is inside its `cap_core_min`, read row by row from the ledger; **but this is the ledger's own field, not a `G10` verdict** (§5) |
| GPU | **0 GPU-h** — no GPU instance was launched |

**Dollars: $0.005344 — DERIVED, NOT MEASURED.** `cost_basis` **REPORTED-BY-OWNER, NOT MEASURED**;
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Stated plainly: this is
THIS RECORD'S ARITHMETIC** on the 6.250 core-min itself derived above, at the recorded c7a.4xlarge
rate of $0.0513/core-h (`CLAUDE.md` rule 12), **not a figure copied from any artefact.** It rests on
a derived total and is therefore the weaker of the two arithmetic statements in this document.

**A whole-item actual/predicted ratio is NOT stated, and the omission is deliberate.** Unlike a
stopped chain, this one completed — all five registered arms ran — so a ratio would not be
misleading in the way `SO-3a`'s would be. It is withheld for a different and stricter reason: **the
numerator is not on record.** Dividing one arithmetic figure by a registered one and presenting the
quotient as this item's calibration would be a second grading. **The supervisor is entitled to that
ratio; a scribe is not the one to write it.**

> **NO CALIBRATION ROW EXISTS FOR SO-2M, AND ONE IS OWED.** `docs/COST_CALIBRATION.md` contains
> **zero** occurrences of `SO-2M` or `SO2M`. Rows exist for the siblings `SO-1cR` and `SO-3a`;
> there is none for this item's spend. **Writing it is not a scribe's call**, it is the
> supervisor's, and rule 11 requires its id to be derived inside the committing invocation (or
> allocated by `scripts/append_record.py`). **It is flagged, not filled.** The row, when written,
> will be the first in this family whose object is a chain that completed and still bought no
> verdict — the honest attribution is `GATE-DESIGN`, not misprediction and not contention.

# 7. WHAT THIS ITEM DID AND DID NOT BUY

**It did not buy a moment-gradient verdict.** `G5m`, the bright line on `d(CMZ)/d(shape, patchV)`,
was never composed onto either row. Registered predictions **P4** (*"PATCHED row `G5m` PASSES"*) and
**P5** (*"SHIPPED row `G5m` GATE FAILS"*) are **unscored** — the artefact carries no `predictions`
key at all. **This record does not score them.**

**It did not buy a trivial-baseline reading, a `G-NZ` reading, a `G1` reading, a `G9` reading or a
`G10` reading.** All of them sit behind the control that refused.

**It did not establish that the IDWarp defect does or does not reach a moment functional** — which
is the question `PREREGISTRATION.md:100` registered as the interesting one, noting that a `P5` miss
*"would mean the IDWarp defect … does not reach a moment functional, and the defect's reach would
then be a measured property rather than an assumed one."* **That question is open.**

**What it DID buy, plainly:** **five clean arms of preserved moment-gradient physics** — every
registered arm at `rc=0`, both rows, inside every cap, with the X and G artefacts and five planted
control copies still on disk — and **the family's sharpest demonstration that its planted controls
are load-bearing**, cited as such at `GRADING_CHAIN.md` bullet 5. It also bought the finding at
bullet 10: that a plant registered as a bare absolute is a plant that was never sized against the
functional it must perturb. **A refusal that costs 6.25 core-min and prevents a `PASS` from being
claimed on an unproven gate is the instrument working.**

# 8. WHERE THE FULL READINGS LIVE

1. **`/home/ubuntu/certonomous-runs/CURRICULUM-SO2M-a1-naca0012-moment-gradient/SO2M_grade_20260831T195531Z.json`**
   (outside git) — the verdict of record and the refusal, in three keys. The `.out` beside it
   carries the same refusal on one line.
2. **`…/ledger.txt`**, **`…/STATUS.chain`**, the five `STATUS.<arm>` files, the per-arm
   `*.log` / `*.inspect.txt` / `*.cpu.jsonl`, and the five arm directories `MESH/`, `X-S/`, `G-S/`,
   `X-P/`, `G-P/` with their X and G artefacts.
3. **`…/grader_controls/`** — the five planted control copies listed in §4.
4. **`cases/dafoam/ladder-a/A1/curriculum_SO2M/PREREGISTRATION.md`** (this directory, frozen) —
   `G5m` and its bands at **:68**, `G-TB` at **:70**, the plant and Direction A at **:88**,
   Direction B at **:89**, the predictions at **:99–:100**, the cost table at **:118**, and the
   Stage-2 clause at **:135**.
5. **`docs/dafoam/GRADING_CHAIN.md`** — bullet 5 (this refusal as the family's live control),
   bullet 10 (the mis-registered plant), and the cause-class table row carried in §3.
6. **`cases/dafoam/INDEX.md`**, Addendum 2026-08-31 — this item's census row, and the row that
   records `curriculum_SO2MR/` as untracked peer work with no verdict.

**If any figure in this record disagrees with the grade JSON or the ledger, the JSON and the ledger
are right.**

# 9. What this record does and does not do

**It does** give SO-2M an item-level record where it had none, so a reader arriving at this
directory finds the item's verdict, its refusal in full and its cause class instead of a
pre-registration and a silence.

**It does not** re-grade anything, move any gate, threshold, band edge, cap or label, score any
prediction, run any comparator, touch the preserved run root, or add any number that was not
already written in a cited artefact — with the two arithmetic exceptions labelled at their point of
use in §6.

**It does not** compose a row verdict out of the refusal's `live_verdict` (§2), turn the ledger's
toolchain stamps into a `G9` reading (§5), fill the calibration row it flags as owed (§6), or state
a ratio (§6).

**It does not** touch any other file in this directory, `docs/dafoam/GRADING_CHAIN.md`,
`docs/dafoam/README.md` §3, `cases/dafoam/INDEX.md`, or `curriculum_SO2MR/`.

**It establishes nothing about the physics of the moment gradient.** The physics was bought and
preserved; it was never read. No solver ran for this record; **zero solver core-minutes** were spent
writing it.
