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
| Real geometry, rendering on load | **Yes.** The served surface is measured against the solved body on **7 comparisons** and all 7 agree; `solved_geometry_sentence()` renders — *"This geometry, 16608 cells."* |
| Real mesh, cell by cell | **Act side yes, page side no.** Cell counts, per-feature resolution and the matched-interface count are read from the mesh record. The live cell-by-cell draw has no control-room event — see D-C3. |
| Fields panel | **No, and deliberately.** See §5. |
| Team progress, stage tracking | Banner map and a moving agent census supplied. See D-C1 and D-C2. |
| Expert discussion | **Yes.** Five beats across restatement, geometry, meshing, feasibility and checks, in the researcher, engineer, numericist and monitor roles. |
| Geometry table, assumptions table | **Yes.** 8 rows and 10 rows, every quantity with a value and a unit, user-defined separated from lab-defined. |
| Small multiples | **Act side yes.** Two arms, four series (two step counters, two pressure-settling traces), `sweep_points = 2`. |
| Results tables, conclusion, compute | **Yes.** 3 tables, 5 verification lines, 4 limitations. Compute **19.763 processor-minutes measured** against a **26.39** estimate, ratio **0.749**; dollars derived at the recorded rate, never measured. |
| Report tab | **Yes.** Title, abstract, methods, 4 result rows, uncertainty, next steps, 3 conclusion lines, certificate sentence. |
| Convergence study ending | **Yes, and enforced.** See §4. |

Measured cost note: the two solver arms are **8.30 + 18.09 = 26.39** estimated
against **7.148 + 12.615 = 19.763** used. The rung's own record adds staging and
mesh verification (0.50 estimated, 0.017 used) for a rung total of 26.89 / 19.780.
The screen shows the two arms, which are the two runs on screen.

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
| 1 | STL is the solved geometry and renders on load | **TICK (act side).** 7 of 7 measured comparisons agree and the sentence renders. The **housing shell** and the **drawn depth** are named on screen as features found, not hidden. Rendering on load is a page behaviour — cfd. |
| 2 | Header stages advance and match what is on screen | **PARTIAL.** Her seven words supplied and mapped; one order inversion is forced by the shared stage tuple (**D-C2**), and two of her words are absent from the shared default (**D-C1**). |
| 3 | Expert discussion present, assumptions table present | **TICK.** Five discussion beats; assumptions table of 10 rows separating user-defined from lab-defined; the one user-assumption correction beat is the housing. |
| 4 | Mesh shown as real cells; resolution table present | **PARTIAL.** Resolution table present, 6 rows, read from the mesh record. The live cell draw is **D-C3**. |
| 5 | Sweep monitors as small multiples on one screen | **TICK (act side).** Two arms, four series, `sweep_points = 2`. Simultaneity is the sequencer's. |
| 6 | Results table, compute line, conclusion | **TICK.** 3 tables; 19.763 measured against 26.39 estimated; 3 conclusion lines. |
| 7 | Report tab populated: plots, summary, next steps | **TICK.** `closing()` fully populated, 3 plots to the figure standard, 3 next investigations, none of them a remediation of the shown result. |
| 8 | Convergence study shown done, or the inbox line | **TICK, and enforced by the instrument** — see §3. |
| 9 | Zero forbidden language on any screen | **TICK, on both sweeps.** `check_actC_act_screen.py`: 359 screen strings, 103 numeric tokens, planted control tripping four rules, **rc = 0**. `check_actC_gate_screen.py`: 4 artifacts, 108 numeric tokens, every rule at 0 hits, **rc = 0**. The one breach that stood at first writing was the shared cost sentence (**D-C4**, resolved by ruling, not by rewording), and the word "Agreement" rendered inside three figures (**D-C8**, regenerated). |
