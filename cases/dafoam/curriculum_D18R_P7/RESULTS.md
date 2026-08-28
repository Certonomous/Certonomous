# D18R-P7 — RESULTS. One prediction of `CURRICULUM-D18`, re-graded from its preserved artefact

**Item:** `D18R-P7`. **Team:** dafoam, lane AA. **Date:** 2026-08-28.
**Pre-registration:** `cases/dafoam/curriculum_D18R_P7/PREREGISTRATION.md`, frozen at
**`9ef4b5ed`** — committed **before** any execution; the comparator's md5 in §3 of that
document was verified **disk == committed blob** immediately before the run.
**Phase 2, item 1** of Sanaa's ordered re-grade sweep
(`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md` §2).

> **THE ONE-LINE ANSWER.** D18's prediction **P7** moves **`MISS` → `HIT`**:
> S/N **19.8691 → 0.1383** against the inherited threshold 1.0.
> **D18's item verdict is `PASS` and DOES NOT MOVE. Both rows stay `PASS`. The
> capability-grid census move 5 → 6 cells stands. Nothing about the physics, the mesh or
> the toolchain comparison is bought by this item.**

---

## 0. WHAT THIS IS, AND WHAT IT IS NOT

This is **not** a re-run, a re-solve or a re-mesh. **Zero solver compute.** It reads D18's
**preserved grade JSON** and re-evaluates **one** registered prediction through a
**successor** comparator, because the original scored that prediction with a defective
composition. **D18's frozen files are not edited** (rules 2 and 6) and its gates stay closed.

**The direction of the error is the finding.** P7 predicted *"the two rows are **NOT**
discriminating"*. **That prediction was correct.** The defective instrument scored it
`MISS`. This is a **false negative on the prediction itself** — an instrument defect that
published as a toolchain finding, which is the class Sanaa's sweep was ordered to hunt.

## 1. THE DEFECT — LINE NUMBERS, AND THREE CITATIONS CORRECTED

Against `cases/dafoam/curriculum_D18_cone_hypersonic/d18_grade.py`, md5
`e4ade11ed9e3db18d2c4988b30e929b4`, **disk == HEAD blob verified at execution**.

| line | code | the asymmetry |
|---|---|---|
| `:581` | `worst_div = max([d["divergence_pct"] for d in div], default=None)` | **numerator — NO verdict filter** |
| `:582-583` | `pc = [c for c in PATCHED components if isinstance(c.get("rel_err_pct"), (int, float))]` → `worst_noise = max(...)` | **denominator — graded-only** |
| `:588` | `sn = worst_div / worst_noise` | the ratio |
| `:589` | `preds["P7_two_rows_NOT_discriminating"] = "HIT" if sn <= 1.0 else "MISS"` | the score |

**Two halves of one ratio, filtered differently.** A component the grader has already
declared **`NOT A RESULT`** can supply the entire *signal* while being structurally barred
from supplying any *noise*. The mechanism is at `:379-382`: on `NO_PLATEAU` the component
loop `continue`s **before** `rel_err_pct` is assigned at `:385`, so *unreadable* and
*no numeric error* are the same state — which is precisely why the denominator excludes it
and the numerator does not.

**Three citations corrected, none of them drift in the cited file (md5 unchanged):**

| citing document | says | actual |
|---|---|---|
| dispatching brief, lane AA | `:582-586` | **`:581-583`**, ratio `:588` |
| `docs/capability/dafoam_GRID.md` Correction 3, row 5 | `:585-589` | **`:581-583`**, ratio `:588` |
| `curriculum_D18_cone_hypersonic/RESULTS.md` §7a | `:585-589`, and `:381-384` for the omission | **`:581-583`**; the omission is sharper as **`:382` `continue` before `:385`** |

**`:381-384` is approximately right and is not called wrong** — it brackets the `continue`.
The other two are off. **This lane edits none of these documents**; the grid's one-line
successor edit is **owed**, and §7's footnote is the **supervisor's** call.

## 2. THE CORRECTED COMPOSITION, AND A REDUNDANCY WORTH NAMING

```
GRADED(row)  = registered components with row verdict in {PASS, GATE FAIL}
               AND a numeric rel_err_pct
SIGNAL_SET   = GRADED(SHIPPED) ∩ GRADED(PATCHED) ∩ COMPONENTS_REGISTERED
worst_div    = max divergence_pct over SIGNAL_SET      <-- the repair
worst_noise  = max rel_err_pct  over GRADED(PATCHED)   <-- unchanged
sn           = worst_div / worst_noise ;  P7 = HIT if sn <= 1.0
```

`NOT A RESULT` is the exclusion criterion — **not** "failed the band". A `GATE FAIL`
component is a **measured** disagreement and stays in.

**Named honestly: the two conjuncts in `GRADED(row)` are redundant in this producer.**
`d18_grade.py:385-386` sets `rel_err_pct` and a graded verdict in the same two statements,
so "verdict is graded" and "`rel_err_pct` is numeric" are the same condition today. The
successor tests **both** anyway, so that a future producer which emits one without the other
is refused rather than silently mis-filtered. Belt and braces, stated rather than left to
look like rigour.

## 3. THE MOVE — BOTH VALUES

Artefact: `/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic/D18_grade_20260828T032852Z.json`.
Output: `cases/dafoam/curriculum_D18R_P7/D18R_P7_regrade.json`.

| | original (frozen `d18_grade.py`) | corrected (`d18r_p7_grade.py`) |
|---|---|---|
| **P7** | **`MISS`** | **`HIT`** |
| S/N | **19.869056971069952** | **0.13831072288719595** |
| signal | **64.39527107787734 %** at **`shape[3]`** | **0.4482626682416995 %** at **`shape[1]`** |
| noise | 3.2409827588515716 % at `shape[0]` (PATCHED) | 3.2409827588515716 % at `shape[0]` (PATCHED) — **unchanged** |
| signal set | all 5 registered components | `shape[0]`, `shape[1]`, `shape[4]`, `shape[5]` |
| excluded | — | **`shape[3]`**, divergence 64.39527107787734 %, **`NOT A RESULT` in BOTH rows** |
| threshold | 1.0 — **inherited from `d18_grade.py:108`, not chosen here** | same |

Per-component divergences, all five: `shape[0]` 0.299774246235848 %, `shape[1]`
0.4482626682416995 %, **`shape[3]` 64.39527107787734 %**, `shape[4]` 0.15806510321663936 %,
`shape[5]` 0.00432339861639655 %. `shape[3]`'s exclusion is the producer's own reading, not
this lane's: `NO_PLATEAU`, neighbour disagreements **1572.6916073866519 %** and
**195.65830115401738 %** against a 10 % plateau rule, **identical in both rows**.

**INDEPENDENT CORROBORATION — CHECKED, AND IT AGREES.** `docs/capability/dafoam_GRID.md`
Correction 3 row 5 recomputed the corrected figure separately and published
**`0.4482626682416995 %`** and **`0.1383`**. This lane's re-grade, through a comparator that
lane never saw, returns **0.4482626682416995 %** and **0.13831072288719595** → `round(·, 4)`
= **0.1383**. **Agreement to every published digit.** Two independent derivations, one
number.

## 4. ⚠ THE ITEM VERDICT DID **NOT** MOVE — AND IT IS PROVEN, NOT ASSERTED

`d18_grade.py:596-601` composes the item verdict from **exactly six** readings: the two row
verdicts, `G-M2`, `G9`, `G10`, `G12`. **`preds` is absent from that expression** — it is
serialised into the output dict afterwards and never read back. P7 is *structurally
incapable* of reaching the verdict.

The successor does not take that on trust. It **re-evaluates the expression** from the
preserved JSON's own gate fields and **refuses** if the recomposition disagrees with the
recorded verdict (refusal 8). Measured:

* six composition inputs read back: **`PASS`, `PASS`, `PASS`, `PASS`, `PASS`, `PASS`**
* recomposed verdict **`PASS`** == recorded verdict **`PASS`**
* rows: SHIPPED **`PASS`**, PATCHED **`PASS`** — unchanged
* unit **U11** confirms the refusal fires: a JSON whose recorded verdict is tampered to
  `GATE FAIL` is **refused**, not published beside.
* unit **U6** confirms the recomposer is **not an echo**: on a producer-built fixture with a
  planted 7 % FD error on SHIPPED `shape[4]`, the producer's verdict is `GATE FAIL` and the
  recomposer **tracks it** to `GATE FAIL`.

**The capability-grid census stands at 6 of 36 cells with evidence, 30 not attempted.**
No cell moves. **Nothing in this item touches the grid.**

## 5. THE BIRTH REQUIREMENT — MET, BOTH DIRECTIONS, THROUGH THE REAL PRODUCER

Sanaa's canonization (2026-08-28) makes rule 3's question a **precondition**, and the lane
sharpening registered in `PREREGISTRATION.md` §8 adds: **a one-directional control certifies
half an instrument.** W3's control
(`cases/dafoam/curriculum_D12R2/d12y_w3_fatal_scan_control.sh:51`) planted only the crash
form — it proved a true positive and never proved silence on the benign form, which is
exactly why it could not catch the defect it existed to catch.

**Status per reader, with the driven unit.**

| reader | born? | driven unit(s) | must-FLAG | must-NOT-flag |
|---|---|---|---|---|
| `d18r_p7_grade.py` — the corrected P7 composition | **BORN** | selftest **U3/U4** (real producer in-process) **and** `d18r_p7_birth_control.sh` **ARM A/ARM B** (real producer as a subprocess, on the real preserved root) | **U4 / ARM B** | **U3 / ARM A** |
| `recompose_item_verdict()` — the item-verdict guard | **BORN** | **U5** (tracks `PASS`) and **U6** (tracks `GATE FAIL` on a planted fixture); **U11** drives the refusal | **U6/U11** | **U5** |
| `d18_grade.py` — the producer | **NOT RE-BORN BY THIS ITEM, and not claimed to be.** It is exercised here as the producer, not graded. Its own rule-3 controls are D18's (`RESULTS.md` §5, worst residual 4.2718e-17) and are untouched. | — | — | — |

**The producer is not simulated.** Each control arm copies the **preserved run root**, plants
into **the artefact the real solver wrote** (`X-S/d18_X.json`), runs the **real frozen**
`d18_grade.py` so the grade JSON is emitted by the real producer in the real schema, and
reads that JSON through the successor.

**Evidence:** `cases/dafoam/curriculum_D18R_P7/d18r_p7_birth_control_evidence.txt`.

| arm | plant | required | **measured** |
|---|---|---|---|
| **ARM 0** reproduction | none | frozen grader rc 0; `predictions`, `verdict`, divergence **identical** to the landed grade | **rc 0; `SAME`** — the landed grade is reproducible from the preserved root |
| **ARM A** must-NOT-flag | `×1000` on SHIPPED `shape[3]` adjoint → divergence **99.9644 %** at a component `NOT A RESULT` in **both** rows | successor **`HIT`**, signal falls back to a graded component, exactly 1 excluded; **original formula on the SAME JSON must say `MISS`** | successor **`HIT`**, S/N **0.1383**, signal **`shape[1]`**, excluded **1**; original **`MISS`**, S/N **30.8439** |
| **ARM B** must-flag | `×1.5` on SHIPPED `shape[1]` adjoint → divergence **33.6322 %** at a component **graded in both rows** | successor **`MISS`**, signal **is** the planted component, S/N > 1 | successor **`MISS`**, S/N **10.3772**, signal **`shape[1]`**, excluded **0** |

**Read ARM A carefully — it is the whole point.** A ~100 % divergence was planted, the
biggest signal available, and the corrected reader **did not move**: still `HIT`, still
0.1383. On the **same producer-emitted JSON** the **original** formula returned `MISS` at
S/N 30.8439. **The defect is reproduced live on planted input, not argued from the landed
numbers.** And ARM B proves the silence is not blindness: the corrected reader's own S/N
moved **0.1383 → 10.3772** in response to a plant it was required to see.

A reader that always flags dies at ARM A. One that never flags dies at ARM B. One
hard-coded to D18's numbers dies at **U1** (clean producer fixture: S/N **0.0**, **nothing**
excluded, both formulas `HIT`).

## 6. SELFTEST

| interpreter | `__pycache__` cleared first | units | expected | failures |
|---|---|---|---|---|
| `python3` | yes | **13** | 13 | **0** |
| `python3 -O` | yes | **13** | 13 | **0** |

`EXPECTED_UNITS = 13` was frozen in the pre-registration **before** execution; the count is
checked against it, so a silently dropped unit fails the selftest. `ast.Assert` count **0**
in the successor's own source (L-332), and **U13** proves the assert counter can see a
planted assert (=1) — the counter's zero is a **planted-control** zero, not an unverified
one. Refusal units **U7–U11** cover five of the nine registered refusal clauses; **U8** is
driven through the real producer (all five components `NO_PLATEAU` on PATCHED).

The producer is imported with `sys.dont_write_bytecode = True`, so importing a **frozen**
case's comparator cannot drop a `__pycache__` into its directory, and no stale bytecode can
invert a unit. **Verified after execution: 0 `__pycache__` directories under
`cases/dafoam/`.**

## 7. COST — ESTIMATE VERSUS ACTUAL (rule 12)

**Solver compute: 0.000 core-min.** No mesh, no solve, no container, no GPU. The live D6R
chain at 4 ranks was not disturbed and `verification/queue/` was not opened.

| | |
|---|---|
| Registered estimate | **0.60 core-min**, cap **3.00** |
| **Actual, registered execution** | **0.0578 core-min MEASURED** = 3.47 wall s at ranks 1 (selftest `python3` 0.09 s, `python3 -O` 0.22 s, birth control 3.12 s, re-grade 0.04 s — each timed by `/usr/bin/time`) |
| **Actual, gross** (incl. pre-freeze instrument development and validation) | **≈ 0.230 core-min** = ≈ 13.8 wall s at ranks 1 |
| Ratio actual/predicted | **0.096×** on the registered execution; **0.38×** gross. **Cap never approached** (1.9 % of cap gross); nothing stopped |
| Dollars | execution **$0.0000494 DERIVED**; gross **$0.000197 DERIVED** — at **$0.0513/core-h**, c7a.4xlarge, owner-stated 2026-08-21/22 |
| `cost_basis` | **REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| Attribution of the gap | **Misprediction, and it is mine.** 0.60 core-min was a deliberately loose estimate for an instrument-only item with no prior of this shape in the family. The dominant real cost is **not CPU** but **I/O**: three `cp -a` copies of a **243 MB** preserved run root. A future instrument-only re-grade in this family should be estimated at **≈ 0.10 core-min** with the copy count named. |
| **Waste, named separately and NOT absorbed into the ratio** (§6 of that charter) | **0.052 core-min** — one full birth-control re-run forced by a defect in this lane's own evidence printer (§8). Rework, not contention. |
| Disk | ≈ 729 MB transient (3 × 243 MB) in the session scratchpad, **deleted on completion**. The scratchpad is temp only and is not a handoff channel (L-186); **no path in this record cites it.** |

A row is owed in `docs/COST_CALIBRATION.md` and is landed with this record.

## 8. A DEFECT IN THIS LANE'S OWN EVIDENCE PRINTER, FOUND BEFORE THE FREEZE

Recorded because it is the same class this sweep exists to hunt, and because a lane that
reports only the defects it found in other people's code is not reporting.

The birth control's arm reader emitted the item verdict **bare** into a shell `set --`.
**`GATE FAIL` is a TWO-WORD value from the fixed vocabulary**, so on ARM B every column
after it shifted by one: the line printed `item=GATE sn_corr=FAIL sn_orig=10.3772`, putting
the **corrected** S/N in the **original** S/N's column and a fragment of a verdict in a
numeric field. **The pass/fail checks were unaffected** — they compare named single-word
fields — but the human-readable evidence line was wrong, and evidence is what a supervisor
reads.

**It was caught by reading a value that made no sense, not by a test.** Repaired in-script
before the freeze, with the reason in a comment; the field is now underscored to a single
shell word. **The general hazard, stated for the lab: every verdict-bearing field this lab
prints into a shell word list is exposed to this, and `NOT A RESULT` is THREE words.**

## 9. WHAT THIS RE-GRADE DID **NOT** BUY

* **Nothing about the physics.** No solver ran. The cell remains **hypersonic in the Mach
  number only** — `perfectGas`, `hConst` with `Cp 1005` constant, `mu 0`, `RASModel dummy`,
  slip wall. No real gas, no vibrational excitation, no chemistry, no viscous or radiative
  heating.
* **Nothing about the mesh.** One mesh, 40,000 cells. **No grid family exists, so NO GCI IS
  QUOTED** — standing rule 5 has no row here.
* **Nothing about the SHIPPED-vs-PATCHED comparison as a physical finding.** The corrected
  S/N ≤ 1 says the two rows are **not distinguishable above the common-mode FD noise on the
  graded components**. It does **not** say the two builds are identical, and it says
  **nothing at all** about `shape[3]`, which remains unreadable in both rows.
* **Nothing about `G6`** (dot-product/duality, `NOT MEASURED`) and nothing about
  complex-step, which this family has never run anywhere.
* **Nothing about the capability grid or its census.**
* **Nothing about D18's item verdict, rows or gates** — §4.
* **Nothing was sent, filed, uploaded, registered, posted or commented outside this box**
  (rule 7).

## 10. PROVENANCE

| artefact | path |
|---|---|
| pre-registration, frozen `9ef4b5ed` | `cases/dafoam/curriculum_D18R_P7/PREREGISTRATION.md` |
| successor comparator, md5 `d8f1811e9815eb2a4b0f13d94d5cdb12` | `cases/dafoam/curriculum_D18R_P7/d18r_p7_grade.py` |
| birth control, md5 `dd944b86931673bb33af5f7dea37e824` | `cases/dafoam/curriculum_D18R_P7/d18r_p7_birth_control.sh` |
| birth-control evidence | `cases/dafoam/curriculum_D18R_P7/d18r_p7_birth_control_evidence.txt` |
| re-grade output | `cases/dafoam/curriculum_D18R_P7/D18R_P7_regrade.json` |
| **subject** (preserved, untouched) | `/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic/D18_grade_20260828T032852Z.json` |
| producer, md5 `e4ade11ed9e3db18d2c4988b30e929b4`, **read only** | `cases/dafoam/curriculum_D18_cone_hypersonic/d18_grade.py` |
| D18's own record (**not edited by this lane**) | `cases/dafoam/curriculum_D18_cone_hypersonic/RESULTS.md` §7a |
| independent corroboration (**not edited by this lane**) | `docs/capability/dafoam_GRID.md` Correction 3, row 5 |
