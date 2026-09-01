# ACT C (battery module) — GUI CONTENT SPECIFICATION

**Status: DRAFT FOR HEAT-TRANSFER SUPERVISOR APPROVAL. Nothing here has reached a
screen. The verification lines and the certificate block in §5 REQUIRE the
supervisor's approval before capture.**

Authority: Sanaa's six GUI fixes, `etc/sessions/2026-09-01T1900Z_sanaa_jf1_gui_fixes.md`
(commit `85d52954`); her convergence-prerequisite doctrine,
`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`
(commit `f4c8e466`), whose §7 rules for Act C: *"run the fix in §2 now; demo
shows it if graded in time, else the honest-refusal act. (a) as fallback, not as
plan… **Never show the 0.4 K run.**"*

Division of labour: cfd owns the shared machinery and everything under `sdk/`.
This document is ACT-SIDE CONTENT only.

---

## 0. WHICH ACT C THIS IS, BECAUSE THERE ARE TWO AND ONLY ONE MAY BE SHOWN

There are two Act C artefacts in the tree and they must not be confused.

1. **`/home/ubuntu/Certonomous/sdk/workflows/battery_module_act.py`** — the
   full battery-module act. **IT IS NOT REGISTERED.** Its module docstring is
   explicit: *"THIS MODULE REGISTERS NOTHING… the sequencer cannot resolve
   `battery-module` and cannot put this act on a screen. That is the point of
   the file, not a gap in it."* Every one of its ten stages calls `_refuse()`.
   `ACT = None` at line 205. It becomes showable only through
   `register_when_a_solved_run_backs_it()`, which refuses while
   `conformance_problems()` is non-empty.

2. **THE GATE SCREEN — the honest-refusal act, and the one that goes on camera.**
   Sheet `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/ACT_C_GATE_sheet.pdf`
   (source `.tex`, builder `build_actC_gate_sheet.py`) plus three figures in
   `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actC_gate/`.

**This specification is for (2).** Act C's subject is not a cooling result. Its
subject is **a gate that refused**, and everything below is written so that the
refusal is what the viewer sees.

### ⛔ THE 0.4 K RUN — SIX FIGURES THAT MAY NOT BE SHOWN

`/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures/actc_*` are the
**0.4 K run** Sanaa barred. Measured, from the rendered PDFs:
`actc_per_cell_table.pdf` carries `293.419751` K; `actc_cell_histories.pdf`
spans 293.1–293.4 K; `actc_field_snapshots.pdf` carries
`min 293.000000 K / max 293.119198 K`; `actc_pack_uniformity.pdf` tops out at
0.10 K spread. That is the 0.42 K rise named in `battery_module_act.py` lines
18–20.

**None of `figures/actc_cell_histories`, `actc_field_snapshots`,
`actc_pack_uniformity`, `actc_per_cell_table`, `actc_step_independence` may
appear on any Act C surface.** They are not a figure-standard problem; they are
a doctrine violation. They are also NOT swept by the withholding guard (§C),
because the guard reads only the gate directory — so nothing mechanical stops
them reaching a screen. Only this rule does.

---

## 1. PANEL SEQUENCE: GEOMETRY → MESH → FIELDS, NOTHING ELSE

Act C is the hardest of the three acts to fit to this fix, because **it has no
solved fields to show**, and inventing a fields panel is exactly the failure the
act exists to demonstrate.

| Panel stage | Exact artifact, absolute path | Status |
|---|---|---|
| **Geometry** | `/home/ubuntu/Certonomous/sdk/geometry/battery_module_8cell.stl` (97,284 bytes) | **PRESENT, BUT NOT VALIDATED AS THE SOLVED BODY.** `battery_module_act.py` line 72 names it `CANDIDATE_SURFACE` with the comment: *"It has NOT been measured against any solved case, so this act does not name it as the solved body and does not render it."* |
| **Mesh** | `/home/ubuntu/Certonomous/verification/runs/T-family/T25R2_MODULE_runs/MESH_VERIFICATION.txt`; level directories `T25R2_L1`, `T25R2_L1_OC20`, `T25R2_L2`, `T25R2_L2_DT025` | The meshes exist and were verified. The gate sheet already quotes a 16,608-cell figure (guard output, ABS-TEMP negative arm). |
| **Fields** | **NONE, DELIBERATELY.** | There is no gradeable solved field. See §1.1. |

### 1.1 What replaces the fields panel — and why that is the act, not a gap

Sanaa's sequence ends in fields because the jet flap and the motor have them.
Act C's third panel is **the gate**, and the substitution must be stated on
screen rather than glossed:

> Geometry → Mesh → **The check that refused**

The third panel therefore shows the three gate figures, in this order:

1. `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actC_gate/actC_gate_sequence.pdf`
   — *"Sweep sequence, 30 s frame"*: 5-against-10 and 10-against-20, showing the
   answer closing by 11.6× (6.02e-03 → 5.21e-04).
2. `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actC_gate/actC_gate_over_run.pdf`
   — *"Agreement over the run"*: the coolant outlet and the solid, against the
   limit, across the run.
3. `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actC_gate/actC_gate_checks.pdf`
   — *"Agreement against its limit"*: the three arms A (solid field, every cell,
   every frame), B (streamwise difference within a cell), C (coolant outlet,
   area-mean).

**Panel-1 rule for the geometry:** the module surface may be rendered on load —
Sanaa's fix 2 requires the STL to render immediately — but its caption must
carry the limitation, because unlike Act A we have not measured it against a
solved case. Screen-safe caption:

> The module as supplied. This surface has not been checked against a completed
> solve, so it is shown as the shape asked about, not as a solved body.

If the supervisor prefers not to render an unvalidated surface at all, the
alternative is to render nothing in panel 1 and say so — but that collides with
Sanaa's *"no 'surface renders here once it lands'"*. **Rendering with the honest
caption is the recommendation.**

---

## 2. THE STL RENDERS ON LOAD AND MUST BE THE SOLVED GEOMETRY

`/home/ubuntu/Certonomous/sdk/geometry/battery_module_8cell.stl` renders on load,
per §1.

**Act C has no equivalent of Act A's retired-body defect** — there is no second
battery surface on disk and no generator regenerating a stale one. I checked the
served geometry directory: `battery_module_8cell.stl` is the only battery
surface present.

**But the second half of the fix cannot be satisfied and must not be pretended.**
Sanaa's clause is *"The STL must be the solved geometry."* For Act C there is no
completed solve, so **the surface cannot be certified as the solved geometry**.
The honest position is the caption in §1.1. No geometry-match table may be shown
for Act C: `battery_module_act.py::geometry()` refuses for exactly this reason
(*"no solved body to measure the served surface against"*), and that refusal is
correct and must not be worked around.

---

## 3. HEADER STATUS LIVE, REAL VALUES NOT FIXED

### 3.1 Stage strings, in order, for Act C

Act C does not run the nine-stage `demo_mode.STAGES` walk — it is not a
registered demo-mode act (§0). Its header sequence is shorter and must reflect
what actually happens:

| # | **Header string Act C must show** | What is on screen |
|---|---|---|
| 1 | `Forming the team` | prompt, as the user typed it |
| 2 | `Planning` | restatement of the cooling question |
| 3 | `Fleet at work` | the module surface renders |
| 4 | `Meshing` | the three levels, from `MESH_VERIFICATION.txt` |
| 5 | `Checking` | the three gate arms, §1.1 panel 3 |
| 6 | `Report` | §5 |

**There is no `Solving, point N of 5` stage for Act C, and one must not be
shown.** Act C's story is that the check ran and refused; a solving counter
would imply a completed sweep that does not exist.

**cfd dependency D-C1:** `Checking` and `Report` are not in `demo_mode.BANNERS`
(which maps `gates` → `"solving"` and `results` → `"results"`). Same dependency
as Act A's D-A7.

### 3.2 The four header fields — where each real value comes from

Identical findings to Act A; I searched `demo_mode.py`, `demo_sequencer.py` and
`sdk/chief_engineer/server.py` for each.

| Field | Real source | Verdict |
|---|---|---|
| **agents** | For a registered act, `act.agent_census()` consumed at `demo_sequencer.py:353`. **Act C is not registered and has no census.** | **NO SOURCE TODAY.** Either omit, or the supervisor registers a census for the gate act. Must not display a fixed number. |
| **human touchpoints** | No `touchpoint` / `human_touch` symbol exists anywhere in the three files. Only defensible count: stages requiring human input = **1** (the prompt). | **NO LIVE SOURCE.** Display the derived `1` labelled *"points where a person was asked: 1"*, or do not display the field. |
| **cycle** | No `"cycle"` symbol in any of the three files. | **NO REAL SOURCE — MUST NOT BE DISPLAYED.** |
| **workers** | `sdk/chief_engineer/server.py:376` — `workers = int((query.get("workers") or ["8"])[0])`: a caller-supplied query parameter defaulting to a hardcoded **8**. Measures nothing about the act. | **NO REAL SOURCE — MUST NOT BE DISPLAYED.** It would show the literal default 8 as telemetry, which is the fixed value Sanaa objected to. |

---

## 4. SMALL MULTIPLES — WHAT ACT C'S ANALOGUE IS

**Stated plainly, as asked: Act C has no sweep analogue of the jet flap's five
blowing levels or Act A's sixteen operating points. There is no sweep to lay out
side by side, because there is no completed solve.**

What Act C does have is a **three-arm comparison**, and it is already drawn
correctly as a small multiple: `actC_gate_checks.pdf` puts arms A, B and C side
by side against one shared limit axis. That figure is the analogue, and it needs
no change.

A second, weaker analogue exists and is **not recommended**: the sweep-count
ladder (5 → 10 → 20 outer correctors) in `actC_gate_sequence.pdf`. It is two
comparisons, not a sweep of physical operating points, and laying it out as
"small multiples" would dress a convergence diagnostic up as a parameter study.

**Recommendation: do not build a small-multiple component for Act C.** Show
`actC_gate_checks.pdf` as it stands and say the act has no sweep. Inventing one
here would be the same class of error as filling the certificate slot.

---

## 5. THE ACT ENDS IN A REPORT

⛔ **Every surface specified in this section is a NEW Act C surface and is
therefore subject to §C, the withholding guard. Read §C before drafting any of
it.**

### 5.1 Results table — the refusal IS the result

Act C's results table must not be a table of temperatures, because every
temperature it could carry is withheld. It is a table of **gate arms and their
verdicts**, in the units the guard admits (convergence differences, all below
0.1 K).

Proposed table, every value read from
`/home/ubuntu/Certonomous/docs/campaigns/T-family/T25R2_RESULTS.md` §2 and
`/home/ubuntu/Certonomous/verification/runs/T-family/T25R2_MODULE_runs/OC_GATE.json`:

| Arm | What it compares | Agreement | Limit | Verdict |
|---|---|---|---|---|
| A | Solid temperature field, every cell, every written frame | 1.199542e-03 K | 1.234e-02 K | inside, by 10.3× |
| B | Streamwise difference within a cell, at the pulse edge | 6.675809e-04 K | 1.234e-03 K | inside, by 1.85× |
| C | Coolant outlet, area-mean, over the run | 2.315190e-02 K | 1.234e-02 K | **outside, by 1.88×** |

**Guard arithmetic check on this table:** every magnitude is a convergence
difference; the largest is 2.315190e-02 K, below the guard's `KELVIN_MAX` of
0.1 K; no absolute temperature appears; no value falls in the guard's
`[200, 500]` ABS-TEMP band. **This table is admissible.** It must be
re-verified by running §C after it is rendered, not assumed.

**⛔ WHAT THIS TABLE MUST NEVER GAIN:** a peak-temperature column, a rise
column, an outlet-temperature column, the acceptance criteria in kelvin, the
energy ledger, or the adiabatic bounds (**2.400 K and 10.800 K — withheld**).
Every one of those is order 1 K or order 293 K, two orders above the admissible
band, and the guard is written to catch exactly them.

### 5.2 ⛔ VERIFICATION LINE — DRAFT, REQUIRES SUPERVISOR APPROVAL

Sanaa's jet-flap line is a positive claim. **Act C's honest line is a refusal.**
What we have, measured:

- **T25R2: `GATE FAIL` on O3**, every row of the rung `NOT A RESULT` by the
  propagation registered at §3.5.4 *before any compute*
  (`T25R2_RESULTS.md` lines 13–17, 38–40, 89–94).
- **T25R3 closed with no gradeable row.** The registered key was
  `p_rgh / p_rghFinal: tolerance 1e-08; relTol 0` — an **absolute** pressure
  tolerance, which `T25R3_RESULTS.md` line 42 records as *"a different physical
  demand on every mesh"*, so the three levels were never solved to a comparable
  standard. It burned **7,600 core-minutes to produce nothing gradeable**
  (line 109).

**Drafted verification lines for Act C — for the supervisor's approval:**

> 1. The check that decides whether this answer can be trusted was run before any
>    result was reported, and it refused. Two of its three arms were comfortably
>    inside their limit; the third was outside it by a factor of 1.88.
> 2. What the third arm means: the answer still moves when an arbitrary iteration
>    count is doubled, so the number the run would have reported is a property of
>    the settings, not of the battery.
> 3. Because that arm refused, no temperature from this run is reported here.
>    Reporting one would mean showing a number the method has not yet earned.
> 4. A follow-up run was made with a tighter pressure setting. It could not be
>    graded either: the setting was an absolute one, which asks a different
>    thing of each mesh, so the three meshes were never solved to a comparable
>    standard. That is a numerics defect on our side and it is being fixed.

**These four lines are the act.** Line 4 is the one most likely to be trimmed
for time and should not be: it is the difference between "our run failed" and
"our run failed, we know why, and the cause was ours."

**Guard arithmetic check:** lines 1–4 carry the numbers 1.88, 3, 2 and no kelvin
quantity at all. `1.88` and `3` are not decimals in [200, 500]; none carries a
`K` unit. **Admissible** — but must still be re-verified through §C once
rendered, because the guard reads the rendered PDF, not this draft.

**What must NEVER appear on an Act C screen:** any cell temperature, any
temperature rise, the coolant outlet temperature, the acceptance criteria, the
energy ledger, the adiabatic bounds (2.400 / 10.800 K), any Celsius quantity,
and any of the eight claim phrases the guard bans (`peak temperature is`,
`peak temperature of`, `hottest cell`, `rises by`, `warms to`, `reaches a peak`,
`energy balance closes`, `runs hotter`).

### 5.3 ⛔ CERTIFICATE BLOCK — DRAFT, REQUIRES SUPERVISOR APPROVAL

**Only a PASS is a credential. Act C has a `GATE FAIL`.** A certificate here
would be the single most damaging thing the demo could do, because the act's
whole claim is that we refuse when the evidence is not there.

The same machinery hazard as Act A applies:
`/home/ubuntu/Certonomous/sdk/chief_engineer/certificate.py` lines 49–50 and
73–74 alias `TREND ONLY` and `REFERENCE REGIME MISMATCH` onto `SOLVER-BACKED`.
**`build_certificate_v2` must not be wired to Act C.**

**Proposed refusal form:**

> **CERTIFICATE — NOT ISSUED**
>
> This result is not certified, and that is the finding rather than a
> disappointment. A certificate is issued only when a check set before the run
> was met. This run's check was set before it started, it ran, and it refused.
>
> **What was established:**
> • The check itself works, and was shown to work: it was driven with known
>   planted signals and caught every one of them.
> • Two of the three arms were inside their limit, one of them by a factor of ten.
> • The cause of the third arm's refusal is identified: the answer still moves
>   when an arbitrary iteration count is doubled.
> • The follow-up run's failure is also identified, and the cause was ours: an
>   absolute setting that asked a different thing of each mesh.
>
> **What was NOT established:**
> • Any temperature anywhere in this module. None is reported, and none is
>   withheld for presentation — it is withheld because the method has not yet
>   earned it.
> • Whether the cooling design is adequate. That question is not answered here.
>
> No certificate number is assigned to this run.

**Guard arithmetic check:** the block contains the words "ten" and "three" spelled
out and no numeral in the ABS-TEMP band, no `K` quantity, no Celsius. It avoids
all eight banned claim phrases. **Admissible** — re-verify through §C once rendered.

### 5.4 Limitations box — WRITTEN IN ADVANCE, USE AS IT STANDS

`battery_module_act.py::LIMITATIONS` (lines 89–98) is already written and
already language-checked at import — deliberately, *"before there is any
pressure from a result to soften it."* Four entries: channels must be resolved
as a fluid before any coolant claim; a single mesh supports no discretisation
error bar; a single time step supports no time-accuracy statement; no rig or
cell test data exists.

Alongside it, the four screen-safe `BLOCKED_ON` entries (lines 76–85) explain
why the act is not showing a cooling result. Both sets are already
`check_demo_language`-clean.

### 5.5 Cost line — MEASURED, and NOT divided by 5

From `T25R2_RESULTS.md` §4, measured solver core-minutes:

| Run | POINT estimate | Actual (core-min) | Ratio |
|---|---|---|---|
| staging + verify | 0.50 | 0.017 | 0.034 |
| `T25R2_L1` | 8.30 | 7.148 | 0.861 |
| `T25R2_L1_OC20` | 18.09 | 12.615 | 0.697 |
| **Total** | **26.89** | **19.780** | **0.736** |

Cap 390 core-min, **5.1 % used, 370.2 unspent. Waste: 0 core-min.** Dollars
**$0.0169**, **DERIVED, NOT MEASURED**, at $0.0513/core-h,
`cost_basis = REPORTED-BY-OWNER`. The rendered sheet already shows
`Total & 26.4 min & 19.8 min` (`ACT_C_GATE_sheet.tex` line 180).

The attribution is worth showing because it is a *good* calibration result: the
estimate priced doubling the sweeps at ×2.18 and the measured factor was
**×1.77**, so the forecast was conservative in the safe direction.

**Screen line, proposed:**

> Compute used: 19.8 processor-minutes against a 26.9 forecast, 0.74 times the
> forecast. At this machine's recorded rate that is about $0.02, derived rather
> than measured.

**Guard arithmetic check:** 19.8, 26.9, 0.74, 0.02 — none in [200, 500], none
carrying `K`. The guard's own ABS-TEMP negative arm already includes
*"the run costs 26.4 min of wall time"*, so this shape is explicitly known-safe.
**Admissible.**

**⚠ THE /5 IS NOT APPLIED HERE. See §7 of the Act A spec; the desk item covers
both acts.**

### 5.6 Conclusion tab vs Report tab

- **Report tab**: the gate-arm table (§5.1), the four verification lines (§5.2),
  the limitations box (§5.4), the cost line (§5.5), the certificate-not-issued
  block (§5.3).
- **Conclusion tab**, ending on a sentence, not a table:

> We were asked whether this battery module stays inside its temperature limit
> under a discharge pulse, and we are not going to tell you, because we cannot
> yet tell you honestly. The check we set before the run refused: the answer
> still moves when an arbitrary iteration count is doubled, so any temperature
> we quoted would be a property of our settings rather than of your battery. We
> know what to change, we know what the follow-up run got wrong and why it was
> our fault, and the compute this cost was a fifth of what we set aside. The
> useful output of this run is the refusal.

---

## 6. FIGURE STANDARD — AUDIT OF EVERY ACT C FIGURE

Method as for Act A: `pdftotext` over every figure PDF, first rendered line
word-counted as the in-figure title, full text scanned for
`prelimin|draft|provisional|WIP`.

**Banner result: `Preliminary` appears on ZERO of the eight Act C figures.**

### 6.1 Gate figures — the three that MAY be shown

All under `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actC_gate/`.

| Figure | In-figure title (words) | Defect | Fix |
|---|---|---|---|
| `actC_gate_checks.pdf` | "Agreement against its limit" (4) | none | **compliant** |
| `actC_gate_over_run.pdf` | "Agreement over the run" (4) | none | **compliant** |
| `actC_gate_sequence.pdf` | "Sweep sequence, 30 s frame" (5) | none | **compliant** |

All three pass the withholding guard (§C, re-run this session, rc=0) and all
three are confirmed LATEXIFIED by the committed reader.

*(Extraction note: `pdftotext` returns the y-axis label `agreement, K` as the
first line for the latter two; the titles above are the rendered titles. Both
are well inside 10 words either way.)*

### 6.2 The 0.4 K figures — the five that MAY NOT be shown

All under `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures/`.
Audited for completeness; **the defect on all five is that they are the barred
run, which no formatting fix cures.**

| Figure | In-figure title (words) | Defect | Fix |
|---|---|---|---|
| `actc_cell_histories.pdf` | "Cell temperature histories, volume-averaged over the 120 mesh cells of each cell" (**12**) | (a) **barred run**; (b) **title over 10 words**; (c) carries a second in-figure caption line *"Cells 1 and 8 coincide; cells 2-7 coincide…"* | **Do not show.** If ever revived: retitle ≤10 words, move the coincidence note to the sheet. |
| `actc_pack_uniformity.pdf` | "Pack uniformity across the eight cells (shaded band: takeoff power pulse)" (**11**) | (a) **barred run**; (b) **title over 10 words** | **Do not show.** If revived: drop the parenthetical to the caption. |
| `actc_per_cell_table.pdf` | "Peak temperature and time to peak, per cell" (8) | (a) **barred run**; (b) **A TABLE RENDERED AS A FIGURE** — columns Cell / Peak temperature K / Peak rise above coolant K / Time to peak s / Uncertainty on the peak K; (c) **carries `293.419751` K, a withheld absolute temperature** | **Do not show.** If revived: the table moves to the sheet, and the temperatures are withheld regardless. |
| `actc_field_snapshots.pdf` | "Module temperature on the mesh, 960 cells" (7) | (a) **barred run**; (b) carries `min 293.000000 K` / `max 293.119198 K` — withheld absolute temperatures | **Do not show.** |
| `actc_step_independence.pdf` | "Time step check, 0.5 s against 0.25 s" (8) | (a) **barred run** | **Do not show.** Title and caption are compliant; the run is not. |

### 6.3 The mechanical gap this audit exposes

`demo_mode.Figure.__post_init__` enforces ≤10-word titles and one-line ≤20-word
captions **on the act's `Figure(...)` declaration**. It does not see the text
matplotlib renders *inside* the PDF. Both over-length titles found above are
in-figure titles, invisible to that check. **This is why the audit read rendered
artifacts rather than declarations**, and it is worth a standing check —
proposed as a desk item, not built here.

---

## C. ⛔ THE WITHHOLDING GUARD — COVERAGE OF EVERY NEW SURFACE

Guard: `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/check_actC_gate_screen.py`.
**Not modified by this work.**

### C.1 Re-run result, this session, read-only

```
4 artifacts checked, 108 numeric tokens read
ABS-TEMP 0 hits / 27 candidates · CELSIUS 0/0 · KELVIN-UNIT 0/0 · THERMAL-CLAIM 0/0 · LANGUAGE 0
PASS — rc=0
```

Controls all live: the latexified reader's planted control read a usetex-OFF
figure back as `NOT LATEXIFIED`; 22 positive arms fired on their own plants and
11 negative arms stayed silent; 20 language alternatives each fired on their own
plant. All four artifacts clean and LATEXIFIED. **The guard still passes on the
current artifacts.**

### C.2 The boundary, restated as the arithmetic the guard enforces

- **ADMISSIBLE** — a difference between two arms differing only in outer-sweep
  count. Every admissible value on these screens lies between **5.2e-04 and
  2.4e-02 K**; the two registered limits are 1.234e-03 and 1.234e-02 K.
- **WITHHELD** — anything telling a viewer how hot the module got: cell
  temperature, rise, outlet temperature, acceptance criteria, energy ledger, and
  **the adiabatic bounds (2.400 / 10.800 K)**, which would disclose the scale by
  the back door.
- **Two orders of magnitude separate the sets**, so the rule is decidable by
  reading a number rather than judging a sentence. `KELVIN_MAX = 0.1`;
  ABS-TEMP band `[200.0, 500.0]`; `MIN_TOKENS = 20`.

### C.3 HOW EVERY NEW SURFACE GETS COVERED — the rule for §5

The guard builds its target list at lines 263–266:

```python
targets = [SHEET]                       # ACT_C_GATE_sheet.pdf
if os.path.isdir(FIGDIR):
    targets += [os.path.join(FIGDIR, f) for f in sorted(os.listdir(FIGDIR))
                if f.endswith(".pdf")]
```

**THE RULE, and it needs no guard edit:**

> **Every new Act C surface — the results table of §5.1, the verification lines
> of §5.2, the certificate block of §5.3, the cost line of §5.5, and both tabs
> of §5.6 — must be rendered into `ACT_C_GATE_sheet.pdf` itself, or as a `.pdf`
> landing in `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/figures_actC_gate/`.**
> Both locations are swept automatically by the directory walk above. A surface
> placed anywhere else is invisible to the guard.

Then: **re-run the guard after every render, and treat rc≠0 as blocking.**
It is read-only and costs seconds:

```
python3 /home/ubuntu/Certonomous/docs/campaigns/T-family/demo/check_actC_gate_screen.py
```

### C.4 ⛔ THE COVERAGE GAP I MUST NAME HONESTLY

**The guard reads PDFs, through `pdftotext`. It cannot see a GUI surface.**

A "Report tab" and a "Conclusion tab" rendered as live HTML in the control room
are **not PDFs and are not swept by anything.** If §5's content reaches the
screen as markup rather than as a rendered sheet, every protection described in
§C.1–C.3 is absent, and the guard's `PASS` says nothing about it.

Three options, in order of preference:

1. **RECOMMENDED — the tabs render the sheet.** The Report and Conclusion tabs
   display `ACT_C_GATE_sheet.pdf` (or gate-directory PDFs) rather than
   re-rendering the content as markup. Coverage is then automatic and total, and
   there is exactly one copy of every sentence.
2. **Acceptable** — the tabs are generated from a source that is ALSO rendered
   to a PDF in `figures_actC_gate/`, and the guard is run on that PDF before
   capture. This relies on the two renderings not diverging, which is a real
   risk and must be stated to whoever wires it.
3. **NOT ACCEPTABLE** — tab content hand-written as markup with no swept
   artifact. This is precisely the leak the brief anticipated.

**cfd dependency D-C2:** extending the guard to read the GUI's own text would
need a new reader (DOM or JSON), which is a change to the guard and outside this
work. **Raised as a desk item; option 1 avoids needing it.**

---

## 7. ASSETS THAT MUST EXIST AND DO NOT

| Asset | Path it must occupy | Why |
|---|---|---|
| Act C results table, rendered | `docs/campaigns/T-family/demo/figures_actC_gate/actC_gate_results_table.pdf` **or** a new section of `ACT_C_GATE_sheet.pdf` | §5.1. **DOES NOT EXIST.** Must land in a guard-swept location per §C.3. |
| Act C certificate-not-issued block, rendered | same two options | §5.3. **DOES NOT EXIST.** |
| Act C verification lines, rendered | same two options | §5.2. **DOES NOT EXIST.** |
| Conclusion / Report tab content | see §C.4 option 1 | **DOES NOT EXIST.** Must not be authored as unswept markup. |
| `Checking` / `Report` banner strings | `sdk/workflows/demo_mode.py` `BANNERS` | §3.1, dependency D-C1 |
| An agent census for the gate act | cfd-owned, or supervisor decision to omit the field | §3.2 |
| A graded battery run | `verification/runs/T-family/T25R4_MODULE_runs/` | **DIRECTORY EXISTS, RUN DOES NOT.** It holds `stage_t25R4.py`, `run_one_t25R4.sh` and a `P1/` directory, with **no solver log and no `DONE.*` marker** as of this session — staged, not run. Pre-registration is committed at `docs/campaigns/T-family/T25R4_PREREGISTRATION.md`. Until it runs and grades, Act C is the honest-refusal act — which is Sanaa's own fallback ruling in her §7, not a failure of this spec. |

**Not missing, confirmed present:** the module STL, the four T25R2 level
directories, `MESH_VERIFICATION.txt`, `OC_GATE.json`, the gate sheet, all three
gate figures, the guard, and the pre-written limitations box.

---

# AMENDMENT 1 — 2026-09-01. THE VISION FRAME, THE SHOOTING PROTOCOL, AND A BUILT ACT.

*Appended, not rewritten. Nothing above this line is edited; the passages this
amendment supersedes are named and struck below. Lines whose number changed
above this section: 0.*

**Authorities, all later than the body of this document:**

- **The demo vision frame**, `etc/sessions/2026-09-01T1945Z_sanaa_demo_vision_frame.md`.
  The demos depict the FUTURE platform's user experience, in its best light, to
  gauge interest before years are committed. Narration carries no film-time-truth
  condition. What stays real: geometry, meshes, fields, numbers and figures come
  from real solved runs, and the lab's internal records stay under the full
  honesty regime, unchanged.
- **"battery: approved."**, `etc/sessions/2026-09-01T2010Z_sanaa_battery_approved.md`,
  commit **`0fe482c4`**.
- **The demo shooting protocol**, `etc/sessions/2026-09-01T2030Z_sanaa_demo_shooting_protocol.md`,
  commit **`cfcf766f`**, whose battery beat is: *"the run completes, the gate
  refuses it, the platform says so and schedules the corrected run. The feature
  is the refusal."*

## A1.1 WHAT THIS DOCUMENT SAID, AND WHAT IT NOW SAYS

> ~~§0: "There are two Act C artefacts in the tree… This specification is for
> (2), the honest-refusal act. Act C's subject is not a cooling result."~~
>
> ~~§4: "Recommendation: do not build a small-multiple component for Act C."~~
>
> ~~§3.1: "Act C does not run the nine-stage `demo_mode.STAGES` walk — it is not
> a registered demo-mode act."~~

**Superseded.** Act C is now a full future-experience act built against the
nine-stage contract, with the refusal as its **climax** rather than as its
substitute for content: real geometry, real mesh, expert discussion, an
assumptions table, live monitors as small multiples over the two arms, results
tables, a conclusion, the compute line, and a Report tab. The module is
`actC_battery_module_act.py` and `validate_act` returns **no problems**.

What is **not** superseded and still binds: the 0.4 K run and all five of its
figures stay barred (§0), `T25R2_L1`'s temperatures stay barred, no certificate
is issued (§5.3), and `workers` and `cycle` are not displayed (§3.2).

## A1.2 THE WITHHOLDING GUARD IS RE-SCOPED — SEE ITS OWN RECORD

> ~~§C: "Guard: `check_actC_gate_screen.py`. **Not modified by this work.**"~~
>
> ~~§C.3: "The guard builds its target list at lines 263–266."~~

Amendment 1 to the guard admits a numeric token in the previously-banned bands
**only** when it matches a value the corrected run actually graded, derived from
that run's committed graded artefact and empty until it exists. The bands and
`KELVIN_MAX = 0.1` are unchanged; the adiabatic bounds stay refused
unconditionally; Celsius and the eight claim phrases stay banned outright.

The full record, including the old behaviour struck, the reason it is an
allowlist and not a wider threshold, and both drive directions with their
numbers, is **`ACT_C_WITHHOLDING_POLICY_CHANGE.md`**.

The line citation above is **superseded**: the target list is now built in
`sweep_targets()`. A new rule, `BARRED-FIGURE`, refuses the five barred figures
by filename, closing §0's own admission that only a written rule stopped them.

## A1.3 ⛔ §C.4's COVERAGE GAP — CLOSED FOR THIS ACT, OPEN FOR THE PAGE

§C.4 said the guard reads PDFs and cannot see a GUI surface, and listed option 1
(the tabs render the sheet) as the recommendation. That gap is **still real for
arbitrary control-room markup**.

It is **no longer real for this act's own content.** `check_actC_act_screen.py`
enumerates every string the act module produces — all nine stages, the geometry
and assumptions tables, the discussion beats, the banner words and every field
of the Report tab, table rows included — and applies the same rules, imported
from the PDF guard rather than copied. Measured: **359 screen strings, 103
numeric tokens, 25 surface groups**, with a planted control tripping four rules
and a floor beneath which a sweep that read almost nothing cannot pass.

**Run BOTH sweeps before capture and treat a non-zero exit as blocking:**

```
python3 docs/campaigns/T-family/demo/check_actC_gate_screen.py     # the sheet and figures
python3 docs/campaigns/T-family/demo/check_actC_act_screen.py      # the act's own strings
python3 docs/campaigns/T-family/demo/drive_actC_allowlist.py       # the loosening, both ways
```

## A1.4 WHAT IS STILL OPEN

Every dependency on the cfd team, every beat that could not be built, and
Sanaa's own nine-box shooting checklist ticked or not, are in
**`ACT_C_REGISTRATION_NOTE.md`**. Two capture blockers stand there: the shared
contract's cost sentence carries a word this campaign's checker bans (**D-C4**,
not ours to reword), and the three gate figures carry the word "Agreement" in
their rendered in-figure titles, now on her never-list (**D-C8**, ours to fix).
