# D18R-P7 — PRE-REGISTRATION (FROZEN)

**Item:** `D18R-P7` — successor re-grade of **one** registered prediction, `P7`, of curriculum
item **D18** (`cases/dafoam/curriculum_D18_cone_hypersonic/`).
**Team:** dafoam. **Lane:** AA. **Date:** 2026-08-28.
**Subject:** D18's **preserved grade JSON**, `/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic/D18_grade_20260828T032852Z.json`.
**Solver compute: ZERO.** Nothing is meshed, nothing is solved, no container starts.
**Provenance:** Phase 2, item 1 of Sanaa's ordered re-grade sweep,
`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md` §2 —
*"re-grade each from preserved artifacts through the repaired instrument; report which
verdicts moved."*

---

## 1. THE DEFECT, WITH ITS LINE NUMBERS

Read against `cases/dafoam/curriculum_D18_cone_hypersonic/d18_grade.py`, md5
`e4ade11ed9e3db18d2c4988b30e929b4`, verified **disk == HEAD blob** at this freeze.

```
581   worst_div   = max([d["divergence_pct"] for d in div], default=None)
582   pc          = [c for c in g5["P"]["G5_CD"]["components"]
                       if isinstance(c.get("rel_err_pct"), (int, float))]
583   worst_noise = max([c["rel_err_pct"] for c in pc], default=None)
588   sn          = worst_div / worst_noise
589   preds["P7_two_rows_NOT_discriminating"] = "HIT" if sn <= PRED["P7_SN_min_to_discriminate"] else "MISS"
```

**The two halves of one ratio are filtered asymmetrically.** The numerator (`:581`) sweeps
**every** registered component with **no verdict filter**. The denominator (`:582-583`)
sweeps only components carrying a numeric `rel_err_pct` — that is, only components the same
grader was able to read. So a component the grader has already declared **`NOT A RESULT`**
can supply the entire signal while being structurally barred from supplying any noise.

**On D18 that is exactly what happened.** The whole 64.3953 % P7 signal is `shape[3]` — the
component **both** rows graded `NOT A RESULT` (`NO_PLATEAU`; the three registered FD steps
disagree by 1572.6916 % / 195.6583 % against a 10 % plateau rule). P7 was therefore scored
on a number D18 itself refuses to stand behind.

**Two corrections of the record, made here rather than repeated:** the defect is at
**`:581-583`** (ratio at `:588`), **not** `:582-586` as the dispatching brief has it, and
**not** `:585-589` as `docs/capability/dafoam_GRID.md` Correction 3 row 5 has it. Both
citations are off; the frozen file is unchanged (md5 above) so this is a citation error in
the citing documents, not drift in the cited one. A one-line successor edit is owed to the
grid; **this pre-registration does not make it** and does not edit either document.

## 2. THE DIRECTION OF THE ERROR, WHICH IS THE POINT

P7's registered prediction is *"the two rows are **NOT** discriminating (S/N ≤ 1.0)"*. That
prediction was **correct**. The defective instrument scored it `MISS`. This is a **false
negative on the prediction itself** — an instrument defect dressed as a toolchain finding,
which is the class of failure Sanaa's sweep was ordered to hunt.

## 3. WHAT IS RE-GRADED, AND THE FROZEN INSTRUMENT

| | |
|---|---|
| Comparator | `cases/dafoam/curriculum_D18R_P7/d18r_p7_grade.py`, md5 **`d8f1811e9815eb2a4b0f13d94d5cdb12`** |
| Birth control | `cases/dafoam/curriculum_D18R_P7/d18r_p7_birth_control.sh`, md5 **`dd944b86931673bb33af5f7dea37e824`** |
| Producer (READ ONLY, NEVER EDITED) | `cases/dafoam/curriculum_D18_cone_hypersonic/d18_grade.py`, md5 `e4ade11ed9e3db18d2c4988b30e929b4` |
| Subject artefact | `/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic/D18_grade_20260828T032852Z.json` |
| Frozen unit count | `EXPECTED_UNITS = 13`, selftest must pass under `python3` **and** `python3 -O` |

**D18's own frozen files are not edited** (rules 2 and 6). This is a **successor**
comparator in its own directory. D18's gates are CLOSED and stay closed.

## 4. THE CORRECTED COMPOSITION RULE (registered before execution)

```
GRADED(row)  = registered components whose row verdict is in {PASS, GATE FAIL}
               AND whose rel_err_pct is a number
SIGNAL_SET   = GRADED(SHIPPED) ∩ GRADED(PATCHED) ∩ COMPONENTS_REGISTERED
worst_div    = max divergence_pct over SIGNAL_SET          <-- THE REPAIR
worst_noise  = max rel_err_pct  over GRADED(PATCHED)       <-- unchanged, already graded-only
sn           = worst_div / worst_noise
P7           = HIT if sn <= 1.0 else MISS
```

**`NOT A RESULT` is the exclusion criterion — not "failed the band".** A `GATE FAIL`
component is a **measured** disagreement and stays in the signal set; only a component the
grader could not read at all is removed. The filter is applied **symmetrically** to both
halves of the ratio, which is the whole of the repair.

**The threshold is INHERITED, NOT CHOSEN.** `P7_SN_min_to_discriminate = 1.0` is D18's own,
frozen at `d18_grade.py:108` before D18 ran. This successor changes **no** gate, **no**
threshold and **no** label. What this freeze buys is the **composition rule** and the
**refusal set** (§5), fixed before execution.

**Honest disclosure, because rule 2's evidentiary content is that the gate could not be
chosen to fit the answer.** The corrected value is elementary arithmetic on published
numbers and is **already known** to the lane and independently recomputed at
`docs/capability/dafoam_GRID.md` Correction 3 row 5. The freeze here cannot and does not
claim outcome-blindness. It claims something narrower and checkable: the rule above, the
refusal set below, the unit count and the both-directions control were all fixed and
committed **before** the re-grade was executed and recorded.

## 5. REFUSAL SET (the comparator returns rc 2 / `NOT A RESULT`, never a degraded number)

1. `item` is not `CURRICULUM-D18`.
2. Any of `gates`, `rows`, `predictions`, `divergence_shipped_vs_patched_CD` absent.
3. Divergence list empty.
4. `SIGNAL_SET` empty (no component graded in **both** rows).
5. `GRADED(PATCHED)` empty — no noise term.
6. `worst_noise == 0`.
7. A component in `SIGNAL_SET` has no divergence entry.
8. **The item verdict recomposed from the six registered inputs disagrees with the recorded
   one** — this reader never publishes beside a verdict it cannot re-derive.
9. `ast.Assert` count non-zero in its own source (L-332).

## 6. WHAT THIS RE-GRADE MAY **NOT** CONCLUDE

Stated so no reader can borrow more than it bought.

* **NOTHING about the physics.** No solver ran. The wedge, the shock, M 5.0002 and the
  perfect-gas / calorically-perfect caveat (`Cp 1005` constant, `mu 0`, `RASModel dummy`,
  slip wall) stand exactly as D18 left them. This cell remains **hypersonic in the Mach
  number only**.
* **NOTHING about the mesh.** One mesh, 40,000 cells. **No grid family exists, so NO GCI IS
  QUOTED** (standing rule 5 has no row here).
* **NOTHING about the SHIPPED-vs-PATCHED toolchain comparison as a physical finding.** A
  corrected S/N ≤ 1 says the two rows are **not distinguishable above the common-mode FD
  noise on the graded components**. It does **not** say the two builds are identical, and it
  says **nothing at all** about `shape[3]`, which remains unreadable in both rows.
* **NOTHING about `G6`** (dot-product/duality, `NOT MEASURED` — the tutorial exposes none)
  and nothing about complex-step, which this family has never run anywhere.
* **NOTHING about the capability grid census.** No cell moves; the 6-of-36 count is
  untouched. The grid's D18 cell already carries this caveat and needs a **footnote, not a
  rewrite**.
* **IT DOES NOT TOUCH THE ITEM VERDICT — and it proves that rather than asserting it.**

## 7. THE ITEM VERDICT CANNOT MOVE — REGISTERED PROOF OBLIGATION

`d18_grade.py:596-601` composes the item verdict from exactly six readings: the two row
verdicts, `G-M2`, `G9`, `G10`, `G12`. **`preds` is absent from that expression**; it is
serialised into the output dict afterwards and never read back. P7 is therefore
*structurally incapable* of reaching the verdict.

The successor **re-evaluates that expression** from the preserved JSON's own gate fields
(`recompose_item_verdict()`) and **refuses** if the result differs from the recorded verdict
(refusal 8). Unit **U6** drives the recomposer to a *different* answer (`GATE FAIL`) on a
producer-built fixture, so a recomposer that merely echoes its input is caught.

**Registered expectation: D18's item verdict is and remains `PASS`; both rows remain `PASS`;
the grid census move 5 → 6 cells stands.** If execution implies otherwise, this item
returns `NOT A RESULT` and escalates rather than publishing.

## 8. THE BIRTH REQUIREMENT — BOTH DIRECTIONS, THROUGH THE REAL PRODUCER

Sanaa, 2026-08-28, canonizing rule 3's question as a **precondition**: *"no instrument
grades anything until that answer is yes, demonstrated"*, and: *"A control defined in terms
of the thing it controls is not a control. A planted control must travel the real production
path — written by the real producer's code, read through the real reader."*

**Lane sharpening registered here: a one-directional control certifies half an instrument.**
W3's planted control (`cases/dafoam/curriculum_D12R2/d12y_w3_fatal_scan_control.sh:51`)
planted only the **crash** form — it proved the reader sees a true positive and never proved
it stays **silent** on the benign form, which is precisely why it could not catch the defect
it existed to catch. **This item's control therefore drives both directions on the same code
path.**

The producer is **not simulated**. Each arm copies the **preserved run root**, plants a
perturbation **into the artefact the real solver wrote** (`X-S/d18_X.json`), runs the **real
frozen** `d18_grade.py` over that root so the grade JSON is emitted by the real producer in
the real schema, and reads that JSON through the successor.

| Arm | Plant | The reader MUST | Registered expectation |
|---|---|---|---|
| **ARM 0** reproduction | none | reproduce | frozen grader rc 0; `predictions`, `verdict` and `divergence_shipped_vs_patched_CD` **identical** to the landed grade |
| **ARM A** must-NOT-flag | `×1000` on SHIPPED `shape[3]` adjoint — `NOT A RESULT` in **both** rows, divergence ≈ 99.96 % | **stay silent** | successor `HIT`, signal falls back to a **graded** component, exactly 1 excluded; the **original** formula on the **same** producer-emitted JSON says `MISS` — the defect reproduced live, not argued |
| **ARM B** must-flag | `×1.5` on SHIPPED `shape[1]` adjoint — **graded in both rows**, divergence ≈ 33.63 % | **flag** | successor `MISS`, signal **is** the planted component, S/N > 1 |

A reader that always flags dies at ARM A; a reader that never flags dies at ARM B; a reader
hard-coded to D18's numbers dies at selftest U1 (clean fixture, S/N 0.0, nothing excluded).

**In-module units U1–U13 use the same discipline**: every fixture is built by the real
producer's own `_fix()` and graded by its own `grade()`, imported with
`sys.dont_write_bytecode = True` so that importing a **frozen** case's comparator cannot drop
a `__pycache__` into its directory and no stale bytecode can invert a unit.

## 9. COST (rule 12; `COMPUTE_BUDGET_CHARTER.md` §5)

**Solver compute: ZERO core-minutes.** No mesh, no solve, no container, no GPU. The queue at
`verification/queue/` is not touched and the live D6R chain at 4 ranks is not disturbed.

**Instrument compute is NOT zero and is costed as such:**

| | |
|---|---|
| Registered estimate | **0.60 core-min** (ranks = 1 throughout: two selftests, three producer re-grades over copied roots, one re-grade of the landed artefact) |
| Cap | **3.00 core-min.** An overrun **stops the item**; it does not get a new budget. |
| Rate | **$0.0513 / core-h**, c7a.4xlarge, owner-stated 2026-08-21/22 |
| Dollars, estimate | **$0.000513 DERIVED**, not measured |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure in this item is derived from the owner-stated rate and is labelled so. |
| Disk | ~3 copies of the preserved run root in the session **scratchpad**, deleted on completion. The scratchpad is temp only and is **not** a handoff channel (L-186); no record here cites a scratch path. |

Estimate-versus-actual calibration is owed at completion and lands as a row in
`docs/COST_CALIBRATION.md` (rule 12).

## 10. RULE-2 CONDITION — the run directory that does not exist

Amendments before first compute are legal only with the condition stated **and how it was
checked**. Checked at this freeze, 2026-08-28:

* `/home/ubuntu/certonomous-runs/CURRICULUM-D18R-P7` — **does not exist** (`test -e` → false).
* `ls -d /home/ubuntu/certonomous-runs/*D18R*` → **0 entries**.
* `ls -d /home/ubuntu/Certonomous/verification/runs/*D18R*` → **0 entries**.
* `cases/dafoam/curriculum_D18R_P7/` contains **only** the two instrument files above and
  this document. No `D18R_P7_regrade_*.json`, no `RESULTS.md`, no evidence file exists yet.

**No such run directory will ever exist**: this item registers **no solver arm**. Its output
is a re-grade JSON and an evidence file written beside this document, and the gates below
close the moment the comparator is first executed against the preserved artefact.

## 11. WHAT LANDS, AND WHAT DOES NOT

Lands: `RESULTS.md` in this directory, the re-grade JSON, the birth-control evidence file,
and a `docs/COST_CALIBRATION.md` row.

**Does not land from this lane:** any edit to D18's frozen files (rule 6); any edit to
`cases/dafoam/curriculum_D18_cone_hypersonic/RESULTS.md` — whether that landed record gets an
appended footnote is the **supervisor's** call, and this lane **proposes wording only**; any
edit to `docs/capability/dafoam_GRID.md`; any change to the capability census. **Nothing is
sent, filed, uploaded, registered, posted or commented anywhere outside this box** (rule 7).
