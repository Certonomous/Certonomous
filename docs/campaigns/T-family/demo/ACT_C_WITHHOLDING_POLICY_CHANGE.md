# ACT C — THE TEMPERATURE-WITHHOLDING GUARD IS RE-SCOPED. A RECORDED POLICY CHANGE.

**Dated 2026-09-01. Written by a heat-transfer `lab-lane`.**

**Authority.** Sanaa, verbatim *"battery: approved."*, captured at
`etc/sessions/2026-09-01T2010Z_sanaa_battery_approved.md`, commit **`0fe482c4`**.
The plan she approved reads, in the same capture: *"The temperature-withholding
guard is consciously re-scoped to admit T25R4's numbers when they land, as a
policy decision recorded here, not a silent bypass."* This file is that record.

Composed with, and not superseded by, her demo shooting protocol at **`cfcf766f`**
(`etc/sessions/2026-09-01T2030Z_sanaa_demo_shooting_protocol.md`), whose battery
beat is *"the run completes, the gate refuses it, the platform says so and
schedules the corrected run. The feature is the refusal."*

**Scope.** `docs/campaigns/T-family/demo/check_actC_gate_screen.py`, Amendment 1,
recorded at the foot of that file's module docstring; and the new derivation it
consults, `docs/campaigns/T-family/demo/actC_graded_admission.py`.

---

## 1. THE OLD BEHAVIOUR, STATED AND STRUCK — NOT REWRITTEN

> ~~Every decimal in the absolute-temperature band [200, 500] and every kelvin
> quantity at or above `KELVIN_MAX = 0.1` K is a thermal result, and is refused
> unconditionally on every Act C surface. There is no exception and no
> allowlist.~~

That sentence was correct policy from the day the guard was written until this
one. It is struck rather than edited so a reader who finds the two knows which
is current and why.

## 2. WHAT IT BECOMES

The two bands are **unchanged**, `KELVIN_MAX` is **unchanged at 0.1**, and every
value inside them is still refused — with **one** exception:

> A numeric token in a previously-banned band is admissible **only if it matches
> a value the corrected run actually graded**, at the token's own printed
> precision. Everything else refuses exactly as before.

## 3. ⚠ WHY THIS IS AN ALLOWLIST AND NOT A WIDER THRESHOLD

Widening `KELVIN_MAX`, or narrowing the `[200, 500]` band, is the obvious
implementation and it is the wrong one. **A widened band admits every value
inside it** — including a number nobody graded, a number typed by hand into a
sheet during a late edit, and the adiabatic bounds this guard has withheld since
it was written. A band cannot tell a graded value from a plausible one.

An allowlist can. And a **hand-maintained** allowlist is a hole with a comment
on it, so this one is **derived from the graded artefact** and is never written
by a person:

1. **The source is the corrected run's committed graded artefact**,
   `verification/runs/T-family/T25R4_MODULE_runs/T25R4_GRADE.json`, read out of
   `git HEAD` rather than off the disk — an uncommitted grading in a shared
   working tree is somebody's unfinished work and a screen must not depend on a
   file `git checkout` would remove. (The name follows the family's own
   convention; Act A reads `T23_runs/T23_GRADE.json`.)
2. **Only runs the lab reports contribute.** A declared value whose run carries
   any verdict other than `PASS` or `GATE REACHED` is not admitted.
3. **Every declared value is cross-checked against the grading itself.** A value
   that appears in the declaration and nowhere in its own run's graded subtree
   is a **refusal**, not a silent drop — a number in the declaration and nowhere
   in the grading was typed, and dropping it would make that invisible.
4. **The match is at the token's own precision**, half a unit in its last place:
   a sheet printing `298.87312` as `298.9` matches, and the neighbouring
   `298.8` does not. A token with no decimal point is never admitted, because
   an integer kelvin token carries a whole unit of slack.

## 4. ⚡ THE PROPERTY THAT MAKES THIS SELF-ENFORCING

**If the corrected run has not graded, the derived set is EMPTY, and the guard's
behaviour is bit-identical to its behaviour before this change.** Every branch
of the derivation fails closed: no artefact, an uncommitted artefact, an
unparseable artefact, a wrong rung, an absent declaration, a run whose verdict
is not reportable — each yields the empty set, not a partial one.

That is not a convenience. It is the mechanism by which **Sanaa's own battery
beat is enforced rather than remembered.** Her screen 8 permits exactly two
endings — the convergence study shown done, or shown automatically underway —
and forbids a third. While the corrected run is ungraded, the instrument itself
makes the act end on the refusal and the "your study is running" line. The
fallback is the **default**; the reporting ending is the exception a graded
artefact has to earn.

The act module reads the **same** derivation, so the act and the guard cannot
disagree about what is showable.

## 5. WHAT IS NOT RE-SCOPED

- **The adiabatic bounds (2.400 / 10.800 / 10.7950 K) stay refused
  unconditionally.** They are analytic consequences of the registered heat
  input, not outputs of any solve; they would disclose the scale of the answer
  by the back door. The barred set is checked **before** the allowlist and no
  derived set reaches it. Driven: an artefact that *declares* the adiabatic
  bound still cannot get it on screen.
- **Celsius stays banned outright.**
- **The eight thermal-claim phrases stay banned outright.** What Sanaa approved
  was put to her in terms of T25R4's **numbers**; widening the phrase ban is a
  separate policy question and is **not taken here**. Consequence, stated so it
  is not discovered on camera: even after the corrected run grades, this act
  cannot say "the hottest cell" on a screen. That is a live restriction, and
  lifting it needs its own record.
- **`T25R2_L1`'s temperatures remain barred** on the measurement the supervisor
  made: its `p_rghFinal` ran at `tolerance 1e-08; relTol 0` with a mean of 1.83
  solver iterations over 36,000 solves, initial residuals sitting on the
  threshold. Nothing in this change admits them; they are not T25R4 outputs and
  the derivation only ever admits T25R4 outputs.
- **The five figures of the 0.4 K run stay barred**, and are now barred
  **mechanically**: see §6.

## 6. ADDED IN THE SAME CHANGE — `BARRED-FIGURE`

The content specification's §0 recorded that nothing mechanical stopped the five
figures of the barred 0.4 K run reaching a screen; only a written rule did. A
written rule is not an instrument. The sweep now refuses if
`actc_cell_histories.pdf`, `actc_field_snapshots.pdf`, `actc_pack_uniformity.pdf`,
`actc_per_cell_table.pdf` or `actc_step_independence.pdf` appears in a swept
directory. They are barred by **provenance**, and no numeric test recovers that
from the pixels.

## 7. DRIVEN BOTH WAYS, AND THE RESULTS

A loosening that has not been shown to still refuse is not a guard.

**Unit arms, run on every invocation of the guard** (`allowlist_control()`, whose
plants are written independently of the derivation's own, per the L-425
discipline): 6 planted graded values admitted, 12 non-graded values still
refused, including the barred set and an integer token.

**Derivation arms** (`actC_graded_admission.py --selftest`, `PASS`, 0 failed):
empty / unparseable / wrong-rung / undeclared / non-reportable-verdict artefacts
all derive the empty set; a planted grading derives exactly its two values;
eight non-graded neighbours stay refused; a declared-but-unbacked value refuses;
and the git reader is driven with a real scratch repository — the same grading
derives **nothing** while uncommitted and **two values** once committed.

**End-to-end arms on a really rendered page** (`drive_actC_allowlist.py`, `PASS`):
a copy of the gate sheet was compiled carrying `301.4409 K` and its non-graded
neighbour `301.5409 K`, and **`pdflatex` returned success** — the toolchain is
happy to render a withheld temperature onto a filmed surface.

| direction | derived set | result |
|---|---|---|
| 1 | empty | **4 tokens refused, 0 released.** Both planted temperatures refused, by `ABS-TEMP` and by `KELVIN-UNIT`. Identical to the behaviour before this change. |
| 2 | `{301.4409}` | **2 released, 2 refused.** Exactly the graded value released; its neighbour still refused, on the same page in the same run. |
| 3 | both | the committed sheet is clean under both settings — the change moves nothing that was already passing. |

Live sweep after the change: `4 artifacts checked, 108 numeric tokens read`,
`ABS-TEMP 0/27`, all four artifacts clean and latexified, **rc = 0** — the same
figures as before the change, with the admissibility line now printed on every
run so nobody has to infer which regime a sweep ran in.

## 8. ⛔ THE COVERAGE GAP, RESTATED BECAUSE IT DID NOT GO AWAY

The guard reads PDFs through `pdftotext` and **cannot see a live HTML Report
tab.** That was §C.4 of the content specification and it is still true for
arbitrary control-room markup.

It is **no longer true for this act's own content.** `check_actC_act_screen.py`
enumerates every string the act module produces — all nine stages, the geometry
and assumptions tables, the expert discussion beats, the banner words, and every
field of the Report tab — and applies the **same** rules, imported from the PDF
guard rather than copied, so the two surfaces cannot drift. It swept 359 screen
strings and 103 numeric tokens, with a planted control that trips four rules and
a floor beneath which a sweep that read almost nothing cannot pass.

**Two things that sweep exposed and one it cannot fix:**

- The contract's `Table` language-checks its **title and headers only, not its
  rows**. Every number a viewer reads is in a row. This sweep checks them; the
  contract does not. Reported to the team that owns it.
- A rendered result in scientific notation (`1.199542e-03`) trips the shared
  checker's **commit-hash** rule, because a mantissa is seven hex characters
  carrying a digit and a letter. The act now renders fixed decimals, which is
  better for a viewer anyway; the checker defect stands and is reported.
- The cost sentence the shared contract composes — *"derived at the recorded
  rate"* — tripped **this campaign's** `RECORDED` rule, which the act does not
  author and cannot reword. **RESOLVED 2026-09-01 by supervisor ruling, and
  resolved in the right direction:** our rule over-banned. Sanaa's 20:30Z
  never-list item is the phrase *"not recorded"*, not the bare word, and
  "derived at the recorded rate" states the cost basis rule 12 demands rather
  than confessing an absence. `check_demo_language.py` Amendment 1 narrows that
  one alternative to `not\s+recorded`, with the old alternative quoted and
  struck, no other banned phrase touched, and both arms driven — it still fires
  on all four wordings of "not recorded in this bundle" and stays silent on the
  cost sentence and three further legitimate uses of the word. ⚠ The gap that
  narrowing opens is stated in that amendment rather than left to be found: a
  sentence like *"these values were recorded earlier this week"* is now caught
  by no rule, and closing it means extending `PAST-RUNNING`, which is a
  different banned phrase and excluded by the ruling's own condition.

## 8a. AMENDMENT 2 — `PROCESS-WORD`, AND THE DEFECT THAT EARNED IT

Sanaa's 20:30Z protocol extends the never-list with process vocabulary — *"prior
runs, replay, agreements, paths, ids, tiers"*. **Measured the same day: all three
gate figures carried the word "Agreement" in their RENDERED in-figure titles,
and the sheet carried it in a table row — 6 occurrences in the sheet, 5 across
the figures.**

Nothing caught it, and the reason generalises: the contract's `Figure` checks
the title an act **declares**, while the offending string was matplotlib text
rendered **inside** the PDF. A declaration check is not a rendering check. Only
the rendered-artifact audit found it.

Ruled by the heat-transfer supervisor: regenerate rather than argue the word.
The figures and the sheet now say *difference* and *differ*, which carry the
same meaning; measured after, **0 occurrences in all four artifacts**. The act's
declared figure titles were aligned to the rendered ones, so each figure has one
name.

`PROCESS-WORD` refuses `agreement(s)`, `prior run(s)` and `tier(s)` on Act C
surfaces, with one plant per alternative and four negative arms. **Proved able
to fire rather than assumed:** replayed against the *previous committed*
figures it fires 2 / 2 / 1 times. It is kept **local to the Act C sweep** —
adding it to the shared checker would apply it to Act A's screens, which is a
policy call above this lane; measured first, all five words occur **zero** times
across the four Act C artifacts today, so it turns nothing red and only stops
recurrence.

## 8b. THE CAPTION / BULLET / NUMBER PASS, AND WHAT IT DID TO THE COVERAGE

Sanaa, 2026-09-01 ~20:14Z: *"implement the fix i asked for for the captions, and
shorten the sentences and have them in bullet points, and wherever the point can
be made accross with numbers its better. EVERYTHING should be paraview."*

Rewriting captions to be numeric means **putting more numbers on screen**, and
every one of them goes through the allowlist. The derived set is still empty, so
every temperature is still refused and the act still ends on the refusal beat.
No caption asked for a kelvin magnitude it could not have.

What the rewrite did to the sweeps is worth recording, because it is the
coverage argument the guard's own docstring asks for:

| | before the pass | after |
|---|---|---|
| sheet + figures, numeric tokens read | 108 | **159** |
| `ABS-TEMP` candidates examined | 27 | **54** |
| `KELVIN-UNIT` candidates examined | **0** — "nothing to look at" | **12**, and 0 hits |
| act strings swept | 359 | **366** |
| act numeric tokens | 103 | **200** |

`KELVIN-UNIT` is the line that matters. Before the pass it had examined **zero**
candidates on these artifacts and its clean report rested entirely on its own
plant. After it, it has live coverage — twelve real kelvin quantities on the
page — and still reports zero hits. **A rule with 0 hits over 12 candidates is
different evidence from 0 over 0**, and the numeric captions are what turned one
into the other.

⚡ **AND THE PROVENANCE OF THAT IS WORTH STATING, BECAUSE IT WAS NOT THE POINT OF
THE INSTRUCTION.** Sanaa's directive was about presentation — captions carry
numbers rather than English sentences. Nobody asked for guard coverage. But a
rule that inspects numbers cannot demonstrate anything on a page with no numbers
on it, so putting real quantities on screen is exactly what converts its clean
report from an assertion resting on its own plant into a measurement over live
candidates. **A presentation instruction incidentally bought this act its first
real evidence that the kelvin rule works on the artifacts it guards.** The
credit is hers, and it is recorded here rather than absorbed as though the guard
had always had that coverage.

And the guard was not argued with once in the process: the derived set stayed
empty, every temperature stayed refused, the act still ends on the refusal beat,
and no caption asked for a magnitude it could not have.

Both sweeps were re-run **after** the rewrite, not before: shortened and
bulleted text is exactly where a banned phrase re-enters. Both are `rc = 0`.

### 8b.1 THE SHAPE ALL OF TONIGHT'S DEFECTS SHARE

Named here because this record is where the Act C instances live, and because a
shape with a name is checkable while four separate anecdotes are not:

> **A GREEN RESULT FROM AN INSTRUMENT THAT COULD NOT SEE WHAT IT WAS ASKED
> ABOUT.**

Four media, one shape: a false zero from a field reader that was never shown a
non-zero; a rendered `|` the font silently dropped; a `.rc.*` glob that could not
see a `STATUS.` file; and — the one measured here — a sheet builder that read a
PDF from a previous compile and called it this compile's output. The empty-image
guard in `render_actC_paraview.py` is the fifth medium, caught in advance rather
than after: an image that opens in a viewer and says nothing.

The remedy is the same in every medium and it is the one CLAUDE.md rule 3
already states for readers: **make the instrument demonstrate it can see the
thing before believing it when it says the thing is absent.** Remove the
artifact before regenerating it; assert the new one is new; drive the failing
case and require the refusal.

**The build-form instance is now fixed at its source, not only locally.**
`scripts/check_sheet_tail_rendered.py` Amendment 1 removes the target PDF
before compiling, asserts `returncode == 0` — the signal the old body captured
and never read — and asserts the PDF's mtime postdates the compile. Driven both
ways in that file's own selftest. Three sheets now check clean, and the sheet
that actually goes on camera was **added to the checked list**: it was verified
at build time by its own builder and by nothing afterwards, and a sheet is
filmed long after it is built.

⚠ **A correction to what I first wrote here, because I got the cause wrong and
graded my own mistake as a design property.** I recorded that
removal-before-compile "opens a brief window in which a concurrent reader sees
*not compiled*… a correct state, not a fault." That reading was comfortable and
false. The measured cause was **my own non-atomic edit**: a second lane invoked
the function between the removal step landing and its `import time` landing, hit
`NameError: name 'time' is not defined`, and **its sheet PDF was already gone** —
untracked, so not recoverable from git, only rebuildable. The rebuild succeeded
moments later and the loss was transient, but calling another lane's deleted
artifact "a correct state" was wrong twice over: it was not correct, and it was
caused by how I landed the change rather than by what the change does.

The operational condition now sits in the amendment beside the technical one: **a
remove-then-compile builder must land atomically, in one commit, and must not be
edited in place while another consumer builds against it.** Clause 1 deletes a
consumer's artifact and is only safe because the compile that follows cannot
fail — and an in-flight edit cannot guarantee that. Until such a step is
committed whole, every consumer's artifact is collateral, and untracked build
artifacts have no safety net.

⚠ And the control's own refusal originally named the real sheet's basename, so a
passing control printed a line indistinguishable from a live failure. The control
copy is now renamed, because **a control whose success output reads like a real
failure will be acted on as one.**

**Why this instance is the worst of the set**, adopting the Act A lane's sharper
framing: the other three returned *nothing* and at least looked empty — a false
zero, a caption that rendered blank, a glob that found no file. This one returned
a real, openable, plausible PDF that was simply the wrong one. **An empty answer
invites suspicion; a confident wrong answer does not.**

## 8c. PARAVIEW, AND THE ONE SURFACE NO SWEEP CAN READ

`render_actC_paraview.py` renders the geometry and both mesh regions from the
real case files, and **refuses** the field render. The refusal is the important
part: a colour bar carries absolute kelvin at its end ticks, and **neither the
PDF guard nor the string sweep can read a PNG**. A picture is the one route
around everything above. So the field mode calls the same derivation and exits 2
while the set is empty, which is today. The geometry and mesh renders carry no
text at all — no scalar bar, orientation axes off — so there is nothing on them
for a text sweep to have missed.

The run tree is fingerprinted across all 3,007 files before and after every
render and is identical each time; a touched mtime in a copy changes it.

## 9. LINE-CITATION NOTE

The content specification's §C.3 cites the guard's target list "at lines
263–266". Amendment 1 inserts code above it. That citation is **superseded**:
the target list is now built in `sweep_targets()`, and the specification is
re-cited in the same commit as this record.
