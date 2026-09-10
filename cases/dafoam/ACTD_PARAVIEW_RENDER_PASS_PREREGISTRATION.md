# ACT D — ParaView render pass: PRE-REGISTRATION

**Status:** frozen before any render runs. No `pvbatch` process has been started
for this item. Everything below is fixed before compute.

**Item:** replace the geometry, mesh and field pictures on the four Act D sheets
with `pvbatch` renders taken from the real case files, with provenance on every
frame.

**Family:** dafoam. **Author:** dafoam lab-lane. **Date:** 2026-09-01.

---

## 1. SCOPE, AND THE PART OF IT THAT IS NOT SANAA'S

**`pvbatch` renders: GEOMETRY, MESHES AND SOLUTION FIELDS** — anything depicting
the 3D body, the grid, or a field painted on it.

**DATA PLOTS STAY latexfied matplotlib / native `picture`** per the figure
standard — drag against iteration, the polars, the step-size check, temperature
histories.

**⚠ THAT SPLIT IS `[lab-attributed]`, NOT SANAA'S INSTRUCTION, AND THIS FILE MAY
NOT BE CITED AS IF IT WERE.** Her words are *"showing the mesh. Itll look
better"* (~20:50Z) and *"Never that trashy canvas you were using before"*
(~21:10Z); the canvas being retired is the in-browser geometry/mesh renderer,
not matplotlib. The lab's reading is that a ParaView line chart would be a worse
figure, not a more compliant one. **It is disclosed to her to overturn.**

**Consequently the render scripts and the plot scripts are kept SEPARABLE, so a
reversal is a routing change and not a rewrite.** This is a registered structural
requirement, not a style preference: see gate **G-PV6**.

## 2. TOOLCHAIN IDENTITY — MEASURED, AND THE REASON IT IS BY HASH

**There are TWO ParaView installations on this box and a bare `pvbatch`
resolves to the OLDER of them.** This was measured while writing this file, and
it is exactly the situation `DAFOAM_CHARTER` §6 has in mind when it says the
hash is the identity and the version string is not.

| Path | Resolves to | md5 | Version | Build |
|---|---|---|---|---|
| `/usr/bin/pvbatch` **(what bare `pvbatch` gets)** | `/usr/bin/pvbatch3.12` | `0add3f8eb743f35aec634c8aca3d8674` | 5.11.2 | system pkg, Python 3.12 |
| `/opt/paraview/bin/pvbatch` (wrapper) | `/opt/ParaView-5.13.3-egl-MPI-Linux-Python3.10-x86_64/bin/pvbatch` | `82ec8db976f28f51f2003a56c04fc272` | 5.13.3 | EGL + MPI, Python 3.10 |
| ” (the real binary behind that wrapper) | `…/bin/pvbatch-real` | `dc272bb98d4ca91fd2f72dd3e89256b4` | 5.13.3 | EGL + MPI |

**REGISTERED CHOICE: the 5.13.3 EGL build, addressed BY ABSOLUTE PATH, never by
`pvbatch` on `PATH`.** Two reasons, both material rather than cosmetic:

1. **The EGL build renders headless without an X server.** The 5.11.2 build
   needs `xvfb-run`, which adds a second process whose failure mode is a blank
   image rather than an error — a silent-corruption path this item will not
   carry.
2. **A bare `pvbatch` silently selects 5.11.2.** A script written today and run
   after any `PATH` change would render with a different engine and say nothing.

**`xvfb` is therefore NOT in the registered path.** If the EGL build fails to
initialise, that is a `BLOCKED`, not a licence to fall back to the other binary:
a fallback would change the toolchain mid-item without changing the record.

## 3. GATES, THRESHOLDS AND LABELS — FIXED BEFORE COMPUTE

| Gate | What it asserts | Threshold | Label if it fails |
|---|---|---|---|
| **G-PV1** | The binary that rendered every frame is the registered one, checked by **md5 read at render time**, not by version string or path | md5 == `dc272bb98d4ca91fd2f72dd3e89256b4` | `NOT A RESULT` — frames from an unidentified engine |
| **G-PV2** | Every frame carries provenance: run root, time directory, field name, and the mesh cell count it was drawn from | present on 100 % of frames | `GATE FAIL` |
| **G-PV3** | **PLANTED CONTROL.** A known perturbation is written into a copy of the field, re-rendered, and the two images must DIFFER; and the unperturbed pair must MATCH | differ / match, both directions | `NOT A RESULT` — a renderer not shown able to see a change cannot certify one |
| **G-PV4** | The cell count ParaView reports for the loaded mesh equals `checkMesh` on the same case | exact equality | `GATE FAIL` |
| **G-PV5** | Morph frames are **real stored surfaces only**; frame count equals matched major iterations, and no frame is interpolated | 48 of 48, `major_iterations_unmatched == 0` | `GATE FAIL` |
| **G-PV6** | Render code and plot code are in **separate modules with no import from plot code into render code**, so the §1 split can be reversed by routing | import graph acyclic and one-way | `GATE FAIL` |

**G-PV3 IS THE ONE THAT MATTERS AND IT IS TWO-SIDED ON PURPOSE.** CLAUDE.md
rule 3: a zero from a reader not shown able to see a non-zero is not evidence.
A render pipeline that quietly produces the same picture whatever the field
holds would otherwise pass every other gate on this list. The unperturbed-pair
arm is there because a one-sided control cannot tell a working renderer from one
that emits a different image every time.

**Verdict vocabulary is the lab's fixed set and nothing else:** `PASS` /
`GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

## 4. WHAT IS RENDERED

| Act | Case | Renders |
|---|---|---|
| Wing (A2) | 38,304-cell wing | geometry, surface mesh, gradient-on-skin field, 48 morph frames |
| SO-3 | 4,032-cell section | geometry, grid, grid leading-edge, field |
| D19M compressible | 4,032-cell section | geometry, grid, field |
| Polar (AOAI/AOAC) | 4,032-cell section | geometry, grid, field at a converged angle **and** at a non-converged angle |

**The polar's second field render is registered deliberately.** The act's whole
argument is that the 9–18° points are not physics; showing the field at a
non-converged angle beside a converged one lets a viewer see that for themselves
rather than take the refusal on trust.

**NOTHING RENDERED HERE IS A NEW PHYSICAL RESULT.** Every field drawn already
exists on disk from a landed run. This item produces pictures of existing
numbers and may not be cited as evidence for any physical claim.

## 5. COST — core-minutes, costed before the run (CLAUDE.md rule 12)

`pvbatch` is real compute and rule 12 does not exempt it because nothing is
being solved.

| | core-min |
|---|---|
| Predicted, at np = 1 | **45** |
| **HARD CAP** | **90** |

**Basis:** ~70 frames total (22 stills + 48 morph frames). 2D 4,032-cell stills
measured elsewhere at seconds each; the 38,304-cell wing frames are the cost
driver and are estimated at 5–10 s each, giving ~8 min for the morph alone. The
remainder is script iteration, which is the honest majority of the number and is
named as such rather than hidden in a per-frame rate.

**The cap stops the run.** An overrun does not get a new budget; it gets a
successor item sized honestly (rule 12). Derived dollar cost at the recorded
$0.0513/core-h is **~$0.077 at the cap** — *derived, not measured; this box
cannot read its own billing.*

**Estimate-versus-actual is reported at completion**, per rule 12's calibration
clause, as a row in `docs/COST_CALIBRATION.md`.

## 6. WHAT WOULD FALSIFY THE PASS

A `PASS` here means: every frame came from the registered binary, drawn from a
named run directory and time, at a cell count that matches `checkMesh`, with the
planted control firing in both directions, and the morph carrying only real
stored surfaces.

It does **not** mean the pictures are correct physics, and no gate above tests
that. **If any frame cannot be traced to a run root and a time directory, the
frame is `NOT A RESULT` and is not published**, however good it looks.

## 7. RETIREMENT — NOTHING IS DELETED

The citation sweep is done and it forbids deletion:

- `so3_grid_pair.pdf` is `\includegraphics`'d by **two sheets that compile
  today** (`ACT_D_multipoint_optimisation_sheet.tex:307`,
  `ACT_D_compressible_multipoint_sheet.tex:398`).
- `actD_crease_section.png` is the **evidence artefact of a geometry check**
  (`A2_crease_check.json:5`, `geometry_audit/crease_verdict.py:214,389`) and is
  served by `sdk/workflows/adjoint_act.py:660`.
- `_a2_shape` is **not a figure**: it is `sdk/workflows/_a2_shape.py`, imported
  by three SDK modules and covered by `sdk/tests/test_a2_shape.py`.

**These are retired as a SOURCE for new demo figures. The files stay.** A
verdict whose artefact is gone is not a result.


---

# AMENDMENT 1 — 2026-09-01, PRE-COMPUTE

**Version 1.0 → 1.1.**
**Lines whose number changed above this section: 0.**

## The condition, and how it was checked

`CLAUDE.md` rule 2 permits amendment **before first compute** and requires the
condition be stated and the check named. It is checked, not asserted:

- **`verification/runs/actD_paraview` DOES NOT EXIST.** Nor does
  `/home/ubuntu/certonomous-runs/ACTD-PARAVIEW`. Both tested by `[ -e ]` at the
  time of writing; both absent.
- **No `pvbatch` process is running.** `pgrep -af pvbatch` returns only its own
  invoking shell — the standing lesson that `pgrep`/`pkill` match their own
  command line, so that single row is not a solver.
- **Zero renders have been produced by this item.** No frame, no PNG, no run
  root.

Gates are therefore still open and this amendment may alter them. **After the
first render they close**, and anything further lands as a dated addendum that
cannot move a gate, threshold, cap or label.

## A1.1 — `G-PV1` GATED THE WRONG HALF OF A PAIR. It now gates both.

`/opt/paraview/bin/pvbatch` is a **29 KB ELF launcher** that execs
`bin/pvbatch-real`. The original `G-PV1` checked only `pvbatch-real`
(`dc272bb9…`) — but the process this item **invokes** is the wrapper
(`82ec8db9…`). **If the wrapper were replaced to exec something else, the gate
would keep checking a file that was no longer being used, and would pass.**

**`G-PV1` is superseded by `G-PV1a` and `G-PV1b`. Both must hold.**

| Gate | What it asserts | Threshold | Label if it fails |
|---|---|---|---|
| **G-PV1a** | The **wrapper actually invoked** is the registered one | md5 == `82ec8db976f28f51f2003a56c04fc272` | `NOT A RESULT` |
| **G-PV1b** | The **real binary it execs** is the registered one | md5 == `dc272bb98d4ca91fd2f72dd3e89256b4` | `NOT A RESULT` |

**THE GENERAL LESSON, WHICH IS WORTH MORE THAN THE PATCH: the hash is the
identity, AND A HASH IS ONLY AN IDENTITY WHEN IT IS BOUND TO A NAMED PATH.**
"The pvbatch md5" names two different files on this box, and two readers each
holding one of them will believe they disagree when they do not. Every md5 in
§2 is quoted beside its absolute path for exactly this reason.

## ⚠ A1.2 — NEW GATE `G-PV7`: THE BLANK-FRAME GUARD. This is the gate the item was missing.

**An md5 check proves WHICH ENGINE RAN. It proves NOTHING about whether the
output is an image or a blank rectangle.** §2 argued for EGL because `xvfb`'s
failure mode is a blank image rather than an error — the argument stands, **but
EGL fails the same way**: a context initialises, nothing is drawn, the process
exits 0, and every provenance gate passes on a uniform grey PNG. `G-PV1` green,
frame empty, nothing in the item notices.

**This is `CLAUDE.md` rule 3 applied to a renderer. A reader never shown able to
see a non-zero is not evidence; a renderer never shown able to produce a
non-blank, case-coupled image is not evidence either.**

| Gate | What it asserts | Threshold | Label if it fails |
|---|---|---|---|
| **G-PV7a** | **Every frame carries content.** No frame is uniform | modal pixel colour occupies **< 99.0 %** of pixels **and** the frame holds **≥ 64 distinct colours** | `NOT A RESULT` — a blank frame is not a picture of anything |
| **G-PV7b** | **The pipeline is coupled to the CASE, not merely to the engine.** A perturbed geometry renders differently | **≥ 0.1 %** of pixels differ after perturbation | `NOT A RESULT` |
| **G-PV7c** | **The quiet half.** An unperturbed re-render reproduces | **< 0.1 %** of pixels differ | `NOT A RESULT` — a renderer whose output moves on its own cannot certify that a change is real |

**The thresholds are SCALE-FREE ON PURPOSE.** A pixel-variance floor needs a
scale nobody can register honestly before seeing the first frame, and a floor
guessed in advance is a number chosen to be passed. Modal-colour share and
distinct-colour count need no scale: a blank frame is ~100 % one colour whatever
the palette, and a real render of a mesh is not.

**`G-PV7b`/`G-PV7c` are the two-sided pair.** `G-PV3` already plants into the
**field**; `G-PV7b` plants into the **geometry**, which is the arm that catches a
pipeline rendering a stale or hard-coded surface while faithfully reading a live
field. `G-PV7c` is the half usually left out, and without it a renderer that
emits a different image every time would score full marks on `G-PV7b`.

**`G-PV7` applies to EVERY published frame, not to a sample.**

## ⚠ A1.3 — EGL MAY NOT INITIALISE ON THIS BOX. A one-frame smoke test runs FIRST.

**`CLAUDE.md` rule 12: no GPU is attached to this box.** EGL normally wants a GPU
or a software EGL (Mesa `swrast`). **The registered engine may be unable to run
here at all.**

§2 already registers EGL failure as **`BLOCKED`, never a fallback**, and that
stands. What this amendment adds is **when we find out**:

**STAGE 0 — EGL SMOKE TEST, ONE FRAME, BEFORE ANY SCRIPT ITERATION.** A single
trivial render through the registered wrapper, graded on `G-PV1a`, `G-PV1b` and
`G-PV7a`. Registered cost: **≤ 2 core-min**, inside the existing cap, not added
to it.

**Why first: the honest majority of the 45 core-min is script iteration.**
Discovering an unusable engine after that is spent buys a `BLOCKED` at full
price; discovering it in one frame buys the same `BLOCKED` for approximately
nothing.

**IF STAGE 0 IS `BLOCKED`, NOTHING FALLS BACK.** The 5.11.2 + `xvfb` path is not
entered by default; it is registered properly, as its own amendment, with the
blank-image hazard gated by `G-PV7` rather than argued about. **`G-PV7` is what
makes that path safe if we ever take it, which is why it matters more than which
engine wins.**

## A1.4 — Cost, restated

Unchanged: **45 core-min predicted, 90 HARD CAP**, np = 1. Stage 0's ≤ 2 core-min
is **inside** that envelope. The cap still stops the run.


---

# ADDENDUM 1 — 2026-09-01, POST-COMPUTE

**Version 1.1 → 1.2.**
**Lines whose number changed above this section: 0.**
**ALTERS NO GATE, THRESHOLD, CAP OR LABEL.** This item has had first compute —
Stage 0, the coupling gates and 77 frames have all run — so `CLAUDE.md` rule 2
closes its gates and this can only record, never change.

## SANAA ANSWERED THE SCOPE QUESTION. THE `[lab-attributed]` TAG IS RETIRED.

`etc/sessions/2026-09-01T2021Z_sanaa_paraview_scope_answer.md`, committed
`a78d5055` at 20:21:06 UTC — verified by reading the file and the commit, not
relayed. Her words, verbatim:

> *"yes sorry i just meant the geometry and meshses, the other plots with latex
> and matplolib stay as is (the report plots)"*

**So §1's split is confirmed exactly as it was registered: `pvbatch` for
geometry, meshes and fields; report plots stay LaTeX/matplotlib.** Nothing in
this item is reworked and nothing is converted. `G-PV6` — render code and plot
code separable, one-way import graph — stays in force; it is now insurance
rather than a hedge.

## §1 IS NOT STRUCK, AND THAT IS DELIBERATE

§1 reads *"⚠ THAT SPLIT IS `[lab-attributed]`, NOT SANAA'S INSTRUCTION"*.
**That sentence was TRUE WHEN IT WAS WRITTEN and it stays.** The split *was*
lab-attributed, the file *was* open to being superseded by her, and recording
that was correct. **Striking a true sentence to attach a later development
misrepresents the record**: it would make the file read as though the lab had
always had her answer. The tag is retired *here*, by dated addendum, with the
original left standing.

## WHY THIS IS WORTH A LINE RATHER THAN A SILENT UPDATE

**The disclosure is what made the question askable.** The lab made a ruling it
could not source to Sanaa, tagged it as the lab's own rather than passing it off
as hers, kept the two code paths separable so a reversal would be a routing
change, and escalated when its chronological support collapsed — and she
answered in **seven minutes** (the caption directive is committed 20:14:46; her
answer 20:21:06).

**Had it been recorded as her instruction, there would have been nothing to ask
and no reason to ask it.** `[lab-attributed]` is not a hedge. It is the thing
that made the question possible, and it cost one sentence.

## ⚠ AND THE CHRONOLOGY THAT PROMPTED THE ESCALATION WAS ITSELF WRONG

The escalation was argued partly on filename timestamps. **Those are not the
authority.** Verified independently here by `git log --diff-filter=A`:

| directive file | committed (UTC) |
|---|---|
| `…2030Z_sanaa_demo_shooting_protocol.md` | 18:28:58 |
| `…2050Z_sanaa_install_paraview.md` | 18:33:25 |
| `…2110Z_sanaa_paraview_everywhere.md` | 18:38:02 |
| `…2200Z_sanaa_report_tab_reminder.md` | 19:14:59 |
| `…2014Z_sanaa_captions_bullets_numbers.md` | **20:14:46** |
| `…2021Z_sanaa_paraview_scope_answer.md` | **20:21:06** |

**Filename order inverts across the `2006Z` naming boundary**: earlier captures
were named from estimated times running ahead of the box clock. **The
authoritative sequence is git commit order.** Recorded here because this item's
§1 reasoning cited a chronology, and a reader checking that reasoning against
filenames would reach the wrong conclusion.


---

# ADDENDUM 2 — 2026-09-10, POST-COMPUTE: THE RULE-12 CALIBRATION, AND WHAT THE 45 core-min IN §5 DOES NOT MEAN

**Version 1.2 → 1.3.**
**Lines whose number changed above this section: 0.**
**ALTERS NO GATE, THRESHOLD, CAP OR LABEL.** This item had first compute on
2026-09-01 (ADDENDUM 1, commit `1af060a9`), so `CLAUDE.md` rule 2 closed its
gates. This section records and corrects the record of a cost; it moves nothing
that could be graded, and §5 is **not struck and not edited**.

## D2.1 — Why this is owed

§5 registers **45 core-min predicted at np = 1** (:107) and a **90 core-min HARD
CAP** (:108), restated unchanged in A1.4 (:258-259), and it promises at :121-122
that *"Estimate-versus-actual is reported at completion"*. That calibration was
landed on **2026-09-10** as row `C-20260910T041257.935995Z-c89badfc` in
`docs/COST_CALIBRATION.md` (commit `fd55f9c7`) — **nine days after completion**.

Until this addendum, this document's own face left a reader with 45 core-min and
nothing else, and a reader who never opened the calibration ledger would take 45
for the outcome. **It was not the outcome, and no defensible outcome figure
exists.** That is what this addendum is for.

The ruling that an addendum is owed is the dafoam supervisor's, 2026-09-10, and
is **`[lab-attributed]`** — it is not Sanaa's instruction and may not be cited as
one.

## D2.2 — The instrumented actual is a LOWER BOUND: **≥ 2.470 core-min**

Read on 2026-09-10 from the three JSON ledgers the run itself wrote under
`verification/runs/actD_paraview/`, not carried from any brief:

| ledger | renders costed | wall s | core-min |
|---|---|---|---|
| `stage0/stage0.json` → `render` | 1 | 1.797 | **0.030** |
| `coupling/coupling.json` → `core_min_total` | 3 | 5.293 | **0.0882** |
| `frames/render.json` → `core_min_total` | 77 | 141.136 | **2.352** |
| **INSTRUMENTED TOTAL** | **81** | **148.226** | **≥ 2.470** |

**np = 1 throughout, so core-min = wall s ÷ 60.** `stage0.json` and
`coupling.json` record `"ranks": 1` explicitly on every render.
`frames/render.json` records **no `ranks` key at all**; np = 1 is established
there instead by arithmetic — all **77 of 77** per-frame entries satisfy
`core_min == round(wall_s / 60, 4)`, checked entry by entry. The 77 per-frame
`core_min` values sum to **2.3519** and the file's own `core_min_total` of 2.352
agrees. All 77 carry `rc: 0`; the longest single render on record is **1.898
wall s**.

Derived dollar cost on the bound: **~$0.0021** at the recorded $0.0513/core-h —
*derived, not measured; this box cannot read its own billing*
(`COMPUTE_BUDGET_CHARTER.md` §5).

## D2.3 — NO RATIO IS QUOTED, and the refusal is the substance

2.470 ÷ 45 = **0.055x is a BOUND, not a ratio.** It is stated here only as a
bound and is not the item's actual/predicted figure, because the true ratio is
unknown and larger. **Quoting 0.055x as *the* ratio would credit this item with
an 18x under-spend that the artifacts do not support**, and would corrupt the
calibration series that rule 12 exists to build. The calibration row states the
same refusal in the same words.

## D2.4 — Three named reasons the full actual is NOT RECOVERABLE FROM ARTIFACTS

**(a) Script iteration is uninstrumented — and §5 itself named it as the bulk of
the estimate.** §5 at :113-114: *"The remainder is script iteration, which is the
honest majority of the number and is named as such rather than hidden in a
per-frame rate"*, restated in A1.3 at :245. The three JSONs record only the
**successful final render of each frame**; every failed or iterated `pvbatch`
invocation left no ledger. The single largest registered cost component has no
measurement at all.

**(b) 30 of the 111 PNGs are UNCOSTED — and this CORRECTS the calibration row,
which says 29 of 111 and 82 instrumented.** Counted on disk 2026-09-10:
`verification/runs/actD_paraview/` holds 111 PNGs — `stage0/` 2, `coupling/` 3,
`frames/` 77, `glyphs/` 29.

- `glyphs/` holds 29 PNGs and their `_render_*.py` scripts and **no JSON** —
  uncosted, as the calibration row says.
- **`stage0/` holds TWO PNGs from TWO scripts** — `smoke.png` (`smoke_render.py`)
  and `selftest_frame.png` (`selftest_render.py`) — while `stage0.json` costs
  **exactly one** render (1.797 wall s). The second `pvbatch` invocation is
  uncosted. The two frames are md5-identical
  (`720aea32b9650a7112b220b540bf6d89`), which is consistent with a reproducibility
  self-test, but an identical output is still a second render that was paid for
  and never recorded.

So the instrumented render count is **81, not 82**, and the uncosted PNG count is
**30, not 29**. **The bound is unaffected in value and only loosened in meaning:**
≥ 2.470 core-min still stands, and there is now one more uncosted render behind
it than the ledger row states. These 30 are **LEFT OUT AND STATED AS ABSENT**,
never approximated.

**(c) The 61.6-minute file-mtime span is WALL CLOCK, and it is REFUSED as an
actual.** Mtimes under the run root span 2026-09-01T19:31:25Z
(`stage0/smoke_render.py`) to 20:33:01Z (`glyphs/caption_refusal_2.png`) =
**61.6 min**. At np = 1 that span contains idle script-authoring gaps and **is
not core-minutes**. Presenting it as the actual would be inventing a number. It
is recorded here only to say that it was **considered and refused**.

## D2.5 — What the artifacts DO establish

- The instrumented compute is **2.7 % of the 90 core-min hard cap**.
- **No overrun flag, STATUS file, solver log or ledger** exists anywhere under
  `verification/runs/actD_paraview/` — searched for `STATUS*`, `*OVERRUN*`,
  `*.log` and `ledger*` on 2026-09-10, zero hits. Nothing suggests the cap was
  approached, and nothing records what was actually spent.
- Every gate verdict recorded by the run is `PASS` (`stage0.json`,
  `coupling.json`, `frames/render.json` each carry `"VERDICT": "PASS"`), and
  `frames/render.json` carries a `_not_rendered` entry declining one registered
  polar field rather than fabricating its provenance. **Those are the item's
  verdicts and this addendum does not touch them.**
- **NO WASTE IS NAMED** (`COMPUTE_BUDGET_CHARTER.md` §6) because none is
  measurable. That is an absence of measurement, not a claim of zero waste.

## D2.6 — The lesson, which is why this is worth a section

**An item that registers its cost as majority script iteration must instrument
the ITERATION, not only the successful renders** — otherwise its calibration row
cannot be written at all. This render pass counted its pennies precisely and was
blind where it spent its pounds: 81 successful renders are costed to four decimal
places, and the component §5 itself called *"the honest majority of the number"*
has no record whatsoever.

## D2.7 — Rule-6 compliance of this addendum itself

This section is appended at the foot and **inserts nothing above itself**.
Verified, not asserted: the **17,483 bytes / 328 lines** preceding this addendum
are **byte-identical** to the pre-addendum HEAD blob
`e636035dd4d97b484b3e71e3f6b9e92200c0fcec` (whole-file sha256
`0b8f6c8de940bc823865b5ac215336e1a18a96b62ea5bc2610237e4b59e0d999`), checked by
comparing the first 17,483 bytes of this file against that blob before the commit
that carries this section. **Lines whose number changed above this section: 0.**

This care is deliberate and is the point of the sibling item: the companion
document `cases/dafoam/ADJOINT_MEMORY_ENVELOPE_CITATION_SHIFT_MAP.md` exists
because commit `fa124d95` appended a correction to a frozen record **and also
inserted two lines into its body**, shifting every citation below by two. **An
addendum that documents that failure must not repeat it.**

*Drafted by a dafoam `lab-lane` under a ZERO-COMPUTE instruction: no solver, no
container, no `pvbatch` and no `mpirun` was invoked, and no number in this
section was produced by it. Every figure is read from the artifact cited beside
it.*
