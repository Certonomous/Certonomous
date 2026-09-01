# ACT C — REGISTRATION, AND EVERY DEPENDENCY ON THE cfd TEAM

**Dated 2026-09-01. Written by a heat-transfer `lab-lane`.**
For: heat-transfer supervisor, and through them the cfd team, which owns `sdk/`.

The act module is
`docs/campaigns/T-family/demo/actC_battery_module_act.py`. **Nothing under
`sdk/` was written or modified by this work.**

---

## 1. WHY THE MODULE IS NOT IN `sdk/workflows/`, AND HOW IT REGISTERS

`sdk/` is the cfd team's tree. This act is heat-transfer content — our run, our
numbers, our wording — so it sits beside the campaign it belongs to and imports
the contract rather than being committed into somebody else's package. It is
importable and it validates today.

It does **not** register on import, deliberately: `register_act` puts a key into
a shared registry and a second act answering one key is how a shoot shows the
wrong run. Registration is one line, made by whoever wires the shoot:

```python
import sys; sys.path.insert(0, "docs/campaigns/T-family/demo")
import actC_battery_module_act as actC
actC.register("battery-module")          # -> demo_mode.register_act
```

`actC.conformance_problems()` returns `validate_act`'s list; it is **empty**
today. Running the module directly prints the admissibility state and that list.

There is a **second, unregistered** `BatteryModuleAct` at
`sdk/workflows/battery_module_act.py` whose ten stages all refuse and whose
`ACT` is `None`. It is superseded by this one. **Retiring or repointing it is
cfd's call, not ours** — but two classes of the same name in one tree is a
hazard, and it is raised here rather than left to be discovered.

---

## 2. WHAT RENDERS TODAY

Everything below is measured from artifacts on disk, at the moment it is asked
for. `validate_act`: **no problems**.

| Beat | State |
|---|---|
| Real geometry, rendering on load | **Yes, and now ParaView-rendered.** Measured against the solved body on **7 comparisons**, all 7 agreeing; `solved_geometry_sentence()` renders. `actC_geometry.png`: 8 blocks, 7 gaps, housing visible, subject covers 29.2 % of the frame. |
| Real mesh, cell by cell | **Rendered.** `actC_mesh_module.png` (3,840 cells, 21.3 % of frame) and `actC_mesh_coolant.png` (12,768 cells, 8.1 %), both cell-by-cell from the run's own `polyMesh`, both cell counts asserted against the mesh record. The control room still has no event to animate the draw live — **D-C3** stands for that. |
| Fields panel | **Refuses, and the refusal is mechanical.** `render_actC_paraview.py field` calls the derivation and exits 2 while nothing is graded. See §2a. |
| Team progress, stage tracking | Banner map and a moving agent census supplied. See D-C1 and D-C2. |
| Expert discussion | **Yes.** Five beats across restatement, geometry, meshing, feasibility and checks, in the researcher, engineer, numericist and monitor roles. |
| Geometry table, assumptions table | **Yes.** 8 rows and 10 rows, every quantity with a value and a unit, user-defined separated from lab-defined. |
| Small multiples | **Act side yes.** Two arms, four series (two step counters, two pressure-settling traces), `sweep_points = 2`. |
| Results tables, conclusion, compute | **Yes.** 3 tables, 7 verification lines, 5 limitations. Compute **19.763 processor-minutes measured** against the **26.39** frozen estimate — **25.1 % UNDER prediction**; dollars derived at the recorded rate, never measured. |
| Early cost-prediction beat, closing predicted-vs-actual beat | **Yes, both.** See §2b. |
| Report tab | **Yes.** Title, abstract, methods, 4 result rows, uncertainty, next steps, 3 conclusion lines, certificate sentence. |
| Convergence study ending | **Yes, and enforced.** See §4. |

Measured cost note: the two solver arms are **8.30 + 18.09 = 26.39** estimated
against **7.148 + 12.615 = 19.763** used. The rung's own record adds staging and
mesh verification (0.50 estimated, 0.017 used) for a rung total of 26.89 / 19.780.
The screen shows the two arms, which are the two runs on screen.

---

## 2a. PARAVIEW — WHAT IS RENDERED, AND THE THREE CONSTRAINTS

`render_actC_paraview.py`, output in `figures_actC_paraview/`. Sanaa, 2026-09-01
~20:14Z: *"EVERYTHING should be paraview."* The three gate figures are line and
bar plots and stay in matplotlib — ParaView replaces the canvas, not the
plotting.

| Constraint | How it is enforced, and what it measured |
|---|---|
| No render pipeline writes into a graded run tree | A scratch case is materialised per region; the `.foam` handle lives there and never in the run tree. `run_tree_fingerprint()` hashes **name, size and mtime of all 3,007 files** before and after every stage; identical each time. **Driven:** touching one file of 3,007 in a copy changes the fingerprint. |
| Refuse rather than emit a stale or empty image | Output removed before each render; every image read back and required to clear a spread floor **and** an ink-fraction floor. **Driven both ways:** a uniform white frame refuses (spread 0.00), a correct render of a speck refuses on ink fraction alone (spread 9.50, above the floor, 0.1 % of frame), and all three real renders are accepted. |
| A field render is gated on the graded artefact | `field` calls `actC_graded_admission.derive()` and **exits 2** today. A colour bar carries absolute kelvin and **no PDF or string sweep can read a PNG**, so this refusal is the only thing between the withholding rule and a picture that breaks it. |

Two findings taken from the Act A lane rather than rediscovered: a regioned case
opened the obvious way reads the **wrong mesh** and draws a plausible picture of
it — so each region is staged as its own single-region case and its cell count
asserted; and `os._exit` around `paraview.simple` discards buffered output — so
all output goes to file descriptors 1 and 2 directly, which is what makes the
one deliberate `os._exit` safe.

Three things measured here and stated rather than glossed:

- **This build has no working offscreen path.** `pvpython` segfaults in
  `vtkXRenderWindowInteractor::Initialize`; `pvbatch --force-offscreen-rendering`
  aborts in `CreateAWindow`. A virtual framebuffer is what makes any render
  possible, and the script re-executes itself under one.
- **"Can we import" is not "can we render".** `paraview.simple` imports fine
  under plain `python3`; it is the first `Render()` that crashes. A guard that
  asked about the import answered yes and walked into the crash, so the
  condition is an explicit sentinel instead.
- **The camera is set, not reset.** `ResetCamera` fits the 1 m extrusion of this
  two-dimensional case whatever direction the camera faces: fitting all extents
  gave 2.8 % of frame, facing the section and resetting made it **worse** at
  1.6 %. The parallel scale is computed from the section's own extents.

**What this render does not do:** the housing is visible but is **not**
colour-coded apart from the stack, because the surface is one solid and a box
clip would cut the stack with it. The distinction the assumption beat turns on is
carried by the geometry table and the beat. Colour-coding needs the surface
regenerated as two named solids, which is a change to the served geometry.

---

## 2b. THE TWO COST BEATS, AND THE NUMBER THAT DOES NOT FLATTER US

Sanaa, 2026-09-01 ~20:56Z: every act carries an early beat predicting the cost
and a closing beat comparing it to the actual.

**Both numbers were re-derived from the records for this beat rather than
inherited from an earlier reading**, because the pair's entire evidentiary value
is that one of them was frozen first. The predicted figure traces to
`T25R2_PREREGISTRATION.md` **§8.2**, the registered cost table: **8.30** and
**18.09** core-minutes, quoted by each arm's completion marker. The actual is
each marker's own solver core-minutes: **7.148** and **12.615**.

| | predicted | actual | ratio |
|---|---|---|---|
| Arm 1, ten sweeps | 8.30 | 7.148 | 0.8612 |
| Arm 2, twenty sweeps | 18.09 | 12.615 | 0.6973 |
| **Together** | **26.39** | **19.763** | **0.7489** |

**Final cost 25.1 % UNDER prediction.**

⛔ **N IS 25, NOT 5, AND UNDER IS NOT ACCURATE.** Sanaa's *"within 5%"* is the
pattern of the beat, not a figure to claim. And coming in under is comfortable in
a way an overrun is not — nobody objects to spending less — which is exactly the
comfort that would let a quarter-sized misprediction be written as though the
forecast had been good. **It was not. The forecast missed by a quarter, in the
direction that happens to flatter us.** The beat states the magnitude and the
direction and stops; per her 20:14Z rule the number carries it without an
explanatory sentence, and this is a number that does not need help.

The struck wording on the report row was *"about three quarters of what we quoted
you"*, which reads as though the forecast were fine. It now reads
`25.1% under prediction`.

Both beats are computed in code from the completion markers, so neither can drift
from the records, and no `/5` is applied: that ruling stands and this act runs a
conjugate solve on this box's processors.

**Swept after the edit, not before** — the beats put more numbers on screen:
sheet/figure sweep **rc 0** (159 numeric tokens, every rule 0 hits), act string
sweep **rc 0** (371 strings, 212 numeric tokens, up from 366 / 200), tail check
**rc 0** with the honesty statement confirmed present on the rebuilt page.
Nothing here asked the allowlist for anything: core-minutes, ratios and dollars
are not kelvin magnitudes, the derived set is still empty, and the refusal beat
is untouched.

---

## 3. ⚡ THE CONVERGENCE-STUDY ENDING IS ENFORCED, NOT REMEMBERED

Sanaa's screen 8 permits two endings and forbids a third. Which one plays is
decided by `actC_graded_admission.derive()` — the same derivation the screen
guard consults — and **not** by an author:

- **corrected run not graded** (today): the closing says *"The grid convergence
  study for this case is running now. The band lands in your inbox with the
  report."* and the solving stage declares **no temperature series at all**, so
  no temperature can reach an instrument.
- **corrected run graded and committed**: the same code, unedited, gains the
  temperature traces and the "study complete, every number carries its band"
  ending.

The recorded policy change is `ACT_C_WITHHOLDING_POLICY_CHANGE.md`.

---

## 4. ⛔ EVERY DEPENDENCY ON cfd, NAMED

| id | What | Why it matters | Whose |
|---|---|---|---|
| **D-C1** | `demo_mode.BANNERS` has no `Checking` or `Report` state; it maps `gates`→`solving` and `results`→`results`. | The act overrides `banners()` with Sanaa's seven words, which is legal, but the shared default still disagrees with her protocol for every other act. | cfd |
| **D-C2** | **Her stage ORDER puts "Reading the geometry" BEFORE "Planning"; `STAGES` fixes `restatement` before `geometry` and an act may not reorder.** So the act plays Planning → Reading the geometry. | This is the one place the act cannot follow her sequence, and no act can fix it — the tuple is shared. | cfd, and above a lane |
| **D-C3** | The live cell-by-cell mesh draw has **no control-room event**. `mesh.stats` and `mesh.checked` are emitted by several workflows and `control_room.html` has no handler for either. | Her checklist box *"mesh shown as real cells"* cannot tick from the act side alone. The act supplies counts, per-feature resolution and a wall-zoom hint; the drawing is cfd deliverable 2. | cfd |
| ~~**D-C4**~~ | ~~`demo_mode.cost_line()` renders "derived at the recorded rate"; the campaign checker refuses "recorded".~~ **RESOLVED 2026-09-01 AND WITHDRAWN — cfd need not action this.** | The heat-transfer supervisor ruled that our checker over-banned: Sanaa's 20:30Z never-list item is the phrase *"not recorded"*, not the bare word, and "derived at the recorded rate" is the cost-basis honesty rule 12 requires rather than a confession of an absence. The campaign checker's `RECORDED` alternative is narrowed to `not\s+recorded`, recorded as Amendment 1 in `check_demo_language.py` with the old alternative struck, and driven both ways: it still fires on all four wordings of "not recorded in this bundle" that the Act A display module emits, and stays silent on the cost sentence and three further legitimate uses. The other five alternatives of that rule are untouched. | closed |
| **D-C5** | `demo_mode.check_demo_language` does **not** cover four words on her 20:30Z never-list: bare *"tier"* (only `tier <digit>` matches), *"agreements"*, *"prior runs"*, and bare *"not recorded"* (only "not recorded in this bundle"). | A never-list enforced in six of nine classes reads as complete. | cfd |
| **D-C6** | `demo_mode.check_demo_language`'s **commit-hash** rule fires on scientific notation: `1.199542e-03` contains `199542e`, seven hex characters with a digit and a letter. | It refuses a legitimate rendered result. The act now renders fixed decimals, which is better for a viewer regardless, but the defect stands and will bite the next act that prints an exponent. | cfd |
| **D-C7** | `demo_mode.Table` language-checks its **title and headers only, never its rows**. Every number a viewer reads is in a row. | `check_actC_act_screen.py` checks rows for this act; nothing checks them for any other. | cfd |
| **D-C8** | ~~The three gate figures carry "Agreement" in their rendered in-figure titles.~~ **DONE 2026-09-01.** Titles and axis labels regenerated to say *difference* / *differ*; the sheet's table row too. Measured before: 6 occurrences in the sheet, 5 across the three figures. Measured after: **0 in all four artifacts.** | `PROCESS-WORD`, Amendment 2 to the Act C sweep, now refuses `agreement(s)`, `prior run(s)` and `tier(s)` on Act C surfaces so this cannot recur. Proved able to fire: replayed against the **previous** committed figures it fires 2 / 2 / 1 times. Kept local to Act C deliberately — adding it to the shared checker would apply it to Act A's screens, which is above this lane, and is recommended rather than taken. | closed |
| ~~**D-C11**~~ | ~~`scripts/check_sheet_tail_rendered.compile_tex` reports a stale PDF as a successful compile.~~ **FIXED 2026-09-01. NOT A CROSS-TEAM DEPENDENCY AT ALL — THE FILE IS OURS.** | ⚠ **I filed this against another team and I was wrong about who owns it.** Verified at source afterwards: every commit that has ever touched that file is heat-transfer (`dd01eff6`, `0c260475`, `9fb6173b`, `b5b7e1ac`), its `SHEETS` list contained only our two sheets, and all three callers are in this directory. It was created by this team, this morning, on the supervisor's own standing order. The deference was right as a reflex and wrong on the facts, and the facts were one `git log` away. **Amendment 1 to that file** now removes the target PDF before compiling, asserts `returncode == 0` (line 192 captured it and never read it, while `page_words` twelve lines up already checked it — an inconsistency inside our own file, not a house style), and asserts the PDF's mtime postdates the compile. Driven both ways in its own selftest: a good source still compiles and returns a PDF newer than its compile; a broken source is refused **and leaves no PDF behind**. | closed, ours |
| **D-C10** | ⚠ **A CONTRACT LIMITATION, RAISED BY D-C8.** `demo_mode.Figure.__post_init__` checks the title an act **declares**. The offending string was matplotlib text rendered **inside** the PDF, invisible to that check — the same blindness the content specification's §6.3 recorded for over-length in-figure titles. | A declaration check is not a rendering check. Every act built against this contract can carry a banned word or an over-length title in its rendered figures and pass validation. Only reading the rendered artifact finds it. | cfd |
| **D-C9** | `sdk/workflows/battery_module_act.py` defines a second, refusing `BatteryModuleAct`. | Superseded; retiring or repointing it is cfd's. | cfd |

---

## 5. BEATS THAT COULD NOT BE BUILT, NAMED RATHER THAN DROPPED

1. **The fields panel.** Her panel sequence is geometry → mesh → fields. Act C
   has no showable field: every temperature field figure carries absolute
   temperatures in its colour bar, and the five figures of the barred run are
   barred by provenance. The third panel is **the check that refused**, which is
   her own battery beat — *"the feature is the refusal"* — and the three gate
   figures fill it. When the corrected run grades, a field panel becomes
   possible and the derivation opens it.
2. **A planted control on the physics readers.** There is none for this run, and
   the act does not pretend otherwise: the settings check is decided **before**
   any reader is admitted, so the comparator's planted-zero controls *were never
   reached*. The act's control table therefore carries the checks that **were**
   driven — the age guard's tightest margin over every written moment, the
   matched-interface count, and the screen guard's own 22 positive and 11
   negative arms — and claims nothing more.
3. **The certificate block names no tier**, per her 20:30Z never-list, and no
   certificate is issued or linked. `build_certificate_v2` is **not** wired to
   this act: `chief_engineer/certificate.py` aliases two weaker labels onto a
   stronger one at lines ~49–50 and ~73–74, and the store is keyed by intent and
   is last-writer-wins.
4. **`workers` and `cycle` are not displayed.** `workers` is a query parameter
   defaulting to a hardcoded 8 and `cycle` has no source at all. The act feeds
   neither. `agent_census()` is the one counter it supplies, and it moves from 1
   to 5 and ends at 0.
5. **The owner's graphics-processor speedup is not applied.** That factor was
   measured on adjoint linear solves on a graphics processor; this act runs a
   conjugate solve on this box's processors. The question is on her desk and
   this act does not pre-empt it. `SolveReplay.cost_projection` is `None`.

---

## 6. HER SHOOTING CHECKLIST, TICKED OR NOT

| # | Box | State |
|---|---|---|
| 1 | STL is the solved geometry and renders on load | **TICK.** 7 of 7 measured comparisons agree, the sentence renders, and the surface is ParaView-rendered at 29.2 % of frame. Housing and drawn depth named as features found. Rendering *on load* is a page behaviour — cfd. |
| 2 | Header stages advance and match what is on screen | **PARTIAL.** Her seven words supplied and mapped; one order inversion is forced by the shared stage tuple (**D-C2**), and two of her words are absent from the shared default (**D-C1**). |
| 3 | Expert discussion present, assumptions table present | **TICK.** Five discussion beats; assumptions table of 10 rows separating user-defined from lab-defined; the one user-assumption correction beat is the housing. |
| 4 | Mesh shown as real cells; resolution table present | **TICK for the render, PARTIAL for the animation.** Both regions rendered cell by cell with cell counts asserted; 6-row resolution table. Animating the draw live is **D-C3**. |
| 5 | Sweep monitors as small multiples on one screen | **TICK (act side).** Two arms, four series, `sweep_points = 2`. Simultaneity is the sequencer's. |
| 6 | Results table, compute line, conclusion | **TICK.** 3 tables; 19.763 measured against 26.39 estimated; 3 conclusion lines. |
| 7 | Report tab populated: plots, summary, next steps | **TICK.** `closing()` fully populated, 3 plots to the figure standard, 3 next investigations, none of them a remediation of the shown result. |
| 8 | Convergence study shown done, or the inbox line | **TICK, and enforced by the instrument** — see §3. |
| 9 | Zero forbidden language on any screen | **TICK, on both sweeps, re-run AFTER the caption and bullet rewrite.** `check_actC_act_screen.py`: **366 strings, 200 numeric tokens**, planted control tripping four rules, **rc = 0**. `check_actC_gate_screen.py`: 4 artifacts, **159 numeric tokens**, every rule at 0 hits, **rc = 0**. The one breach that stood at first writing was the shared cost sentence (**D-C4**, resolved by ruling, not by rewording), and the word "Agreement" rendered inside three figures (**D-C8**, regenerated). |
