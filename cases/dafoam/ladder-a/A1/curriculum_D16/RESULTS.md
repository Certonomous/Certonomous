# Curriculum item D16 — NACA0012 transonic (M 0.685, `DARhoSimpleCFoam`), FD-vs-adjoint at the baseline design: RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED.

**Written 2026-08-27 by lane A of the DAFoam team.** The governing document is `PREREGISTRATION.md`
in this directory, frozen before any container started at commit **`3ccb0c81`**. **This file does not
revise the pre-registration.** No gate, threshold, cap, band edge or label was altered by this lane.

**Launched by the queue-runner daemon with no agent alive** — `verification/queue/LAUNCH_LOG.tsv`
row `2026-08-27T11:33:35Z dafoam D16_chain 731626 731626 2 40.3 3ccb0c81…`. `STATUS.D16_chain` carries
`launcher_rc=0`, **the exit status of the launch argv and not the solver rc**; per-arm outcomes below
are read from the run's own ledger and kernel records.

---

## 1. Verdict

| row | image | verdict |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest` (`sha256:9d45679d…5290f07fc`, `libidwarp.so` md5 `f0fcb488…`) | **`GATE FAIL`** |
| **PATCHED** | `dafoam-idwarp-rot:v1` (`sha256:2927768a…dee30f6d35`, `libidwarp.so` md5 `85f59e87…`) | **`PASS`** |

# Item verdict: `GATE FAIL`

The item verdict matches the registered prediction. **The mechanism does not.** §9 committed
*"P5 HIT → SHIPPED `GATE FAIL`"* on `shape[6]`; **P5 MISSED** and the row failed on a different
component. See §5 and §6.

## 2. The grading path, verified before any number here was believed

`d16_grade.py` on disk hashes **`0b8338b3e483548da3515e79da28762a`**, identical to the committed blob at
the freeze commit `3ccb0c81`; so do `PREREGISTRATION.md`, `d16_xf.py`, `d16_run_arm.sh`,
`d16_chain_driver.sh`, `d16_runScript.py`, `d16_aggregate_memory.py`, `d16_decomposeParDict` — eight of
eight MATCH. Re-run by this lane on the registered invocation, the grader returned **json
byte-identical** to `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/D16_grade_20260827T114714Z.json`,
rc 0.

## 3. The two rows, component by component — objective `CD`, band D 5.0 % per component

| dv | idx | `J_adj` SHIPPED | `J_adj` PATCHED | `d_FD` (`d_ref`) | rel err SHIPPED | rel err PATCHED | SHIPPED | PATCHED |
|---|---|---|---|---|---|---|---|---|
| shape | 0 | `0.02233273145960374` | `0.02362930768551476` | `0.02354559855968774` | **5.1511 %** | 0.3555 % | `GATE FAIL` | `PASS` |
| shape | 3 | `-0.05251875709762791` | `-0.05193530745867652` | `-0.05198729798993468` | 1.0223 % | 0.1000 % | `PASS` | `PASS` |
| shape | 6 | `-0.26926975592222957` | `-0.2742311722207006` | `-0.27462471798355564` | 1.9499 % | 0.1433 % | `PASS` | `PASS` |
| shape | 7 | `0.010877066324133593` | `0.010975991329311898` | `0.010918369557681717` | 0.3783 % | 0.5278 % | `PASS` | `PASS` |
| patchV | 1 | `0.005755233917435056` | `0.005755233917435056` | `0.005743948015809325` | 0.1965 % | 0.1965 % | `PASS` | `PASS` |

**SHIPPED `CD`: 4 PASS, 1 GATE FAIL, 0 sign flips, aggregate 1.9648 % → band D `GATE FAIL` (on `shape[0]`), band E `PASS`.**
**PATCHED `CD`: 5 PASS, aggregate 0.1460 % → band D `PASS`, band E `PASS`.**

**G5c on `CL`, the same components:**

| dv | idx | `J_adj` SHIPPED | `J_adj` PATCHED | `d_FD` | rel err SHIPPED | rel err PATCHED | SHIPPED | PATCHED |
|---|---|---|---|---|---|---|---|---|
| shape | 0 | `1.4749374700022155` | `1.4498934912570502` | `1.4498060758789677` | 1.7334 % | 0.0060 % | `PASS` | `PASS` |
| shape | 3 | `2.2043931555501657` | `2.206433089300235` | `2.2059876267361833` | 0.0723 % | 0.0202 % | `PASS` | `PASS` |
| shape | 6 | `0.1719991470989628` | `0.30036038691943534` | `0.29554229567385626` | **41.8022 %** | 1.6303 % | `GATE FAIL` | `PASS` |
| shape | 7 | `0.7163858930452103` | `0.7227502319397503` | `0.7225232224048472` | 0.8494 % | 0.0314 % | `PASS` | `PASS` |
| patchV | 1 | `0.140747871128196` | `0.140747871128196` | `0.1407690108255366` | 0.0150 % | 0.0150 % | `PASS` | `PASS` |

SHIPPED `CL` aggregate 4.5797 % — inside band E, **outside band D on `shape[6]`** → `GATE FAIL`.
PATCHED `CL` aggregate 0.1758 % → `PASS`.

**`patchV[1]` — the CTRL planted-zero component — reads 0.1965 % (`CD`) and 0.0150 % (`CL`) on BOTH
images, `divergence_pct` exactly `0.0`.** The control that makes the `shape` divergences evidence.

## 4. Baselines, divergence and the other gates

`CD_baseline` **`0.016187719043742013`**, `CL_baseline` **`0.44232916845895787`**,
`eta_F` `1.6635906541218048e-10`, mesh **4,032 cells** (G-M2 `PASS`, both rows identical).

Shipped-vs-patched divergence on the adjoint `CD` totals: shape[0] **5.487 %**, shape[3] **1.111 %**,
shape[6] **1.809 %**, shape[7] **0.901 %**, patchV[1] **0.000 %**.

| gate | verdict | reading |
|---|---|---|
| G1 completion | `PASS` | 5/5 arms rc 0, `OOMKilled` false, every field from a ledger row; `delivered` absent on MESH → `NOT_MEASURED`, named |
| G-M2 mesh identity | `PASS` | 4,032 == 4,032 |
| G6 dot-product / duality | **NOT MEASURED** | named, never composed |
| G9 toolchain per row | `PASS` | 5/5 arms, three independent readings of the row's `.so` agree |
| G10 caps | `PASS` | every arm under its cap; total **15.935** core-min against ceiling 245.0 |
| G12 placement | `PASS` | `cpuset 4,14` on 5/5; delivered cores 1.971–1.989 of 2; MESH `NOT_MEASURED`, named |

**No GCI is quoted** — no grid family in this item.

**Planted-zero controls, all live.** Instrument channel `ctrl_zero` `0.0` / `ctrl_planted` `0.617`
against a wanted `0.617` on both images. Grader-level plant seen on both rows, 15 values each, worst
residual **1.28e-17**, files `grader_controls/F_{S,P}_planted.json`.

## 5. Predictions, scored by the comparator against the frozen text

| id | registered claim | outcome |
|---|---|---|
| P1 | mesh is 4,032 cells | **HIT** |
| P2 | `CL` baseline in band | **HIT** |
| P3 | `CD` baseline in band | **HIT** |
| P4 | PATCHED row `CD` PASS on ≥ 4 components | **HIT** (5/5) |
| P5 | SHIPPED `shape[6]` outside band D or sign-flipped | **MISS** — `shape[6]` on `CD` reads **1.95 %**, inside the 5.0 % band, `PASS` |
| P6 | total graded core-min in [15, 120] | **HIT** — 15.935 |
| P6b | MESH wall ≤ 120 s | **HIT** — 10 s |

## 6. What this item establishes, and what it does not

**It establishes** that the shipped-versus-patched IDWarp split **is present at M 0.685** — the SHIPPED
row fails and the PATCHED row passes, on the same mesh, the same design point and the same FD
reference — but that **it does not land on `shape[6]` in `CD`** as D15 and the incompressible A1 rows
did. On `CD` it lands on `shape[0]` (5.15 % against a 5.0 % band, a marginal crossing); on `CL` it
lands on `shape[6]` and lands hard (41.80 %).

**The registered prediction P5 is recorded as a MISS and is not re-scored.** The frozen text named
`shape[6]` on the graded objective, and `shape[6]` on the graded objective passed. **This is a finding
about the transferability of the D15/A1 component signature across Mach number, and it belongs in the
docket rather than in a repaired band.** The honest statement of what moved: the defect's *magnitude*
redistributes across components with the flow regime, so a component-specific prediction carried over
from another Mach number is not supported by this run.

**It does not establish** anything about an optimiser, grid convergence (one mesh, no GCI), 3D, or
whether the rotation branch is the sole contributor. `transonicPCOption 1` is registered as the
solver's setting; this record makes no claim about its runtime activity beyond G9's toolchain identity.

## 7. Cost — actual against the frozen estimate

| arm | ranks | wall s | core-min | cap | predicted point | ratio |
|---|---|---|---|---|---|---|
| MESH | 1 | 10 | 0.167 | 5.0 | 0.3 | 0.557 |
| X-S | 2 | 62 | 2.067 | 30.0 | 6.0 | 0.345 |
| F-S | 2 | 164 | 5.467 | 90.0 | 14.0 | 0.390 |
| X-P | 2 | 62 | 2.067 | 30.0 | 6.0 | 0.345 |
| F-P | 2 | 185 | 6.167 | 90.0 | 14.0 | 0.440 |
| **total** | | | **15.935** | 245.0 | **40.3** | **0.395** |

Gross = cleaned; no arm near the 3,600-s stall figure. **WASTE: 0.000 core-min.**
**$0.0136 DERIVED, NOT MEASURED** at $0.0513/core-h, c7a.4xlarge, `cost_basis` REPORTED-BY-OWNER
(`COMPUTE_BUDGET_CHARTER.md` §5). Predicted $0.0345 DERIVED.

**Gap attribution: misprediction of the transonic primal rate, contention present and not limiting.**
§4 applied D7FR's cell-scaled figure **directly** — 0.32 core-min per primal at 4,032 cells — and priced
the F arms at 32 primals × 0.32 + 3.8 = 14.0. Measured, the F arms cost **5.47 and 6.17**, so a warm
`DARhoSimpleCFoam` primal here is **≈ 0.13–0.15 core-min**, about **2.3× cheaper** than the linear
cell-scaling from a 42,120-cell np = 4 anchor predicts. The registered exposure — *"a transonic primal
on this coarse mesh may converge more slowly … the F caps carry 6.4× the point for that reason"* —
**did not materialise**: the caps were never approached (6.17 against 90.0). Contention: `d15_F-S`,
`d17_X-S`, `d15_F-P` and `d17_F-S` were live across the D16 arms; delivered cores held at 1.971–1.989
of 2, so contention cost less than 1.5 % and is named, not blamed.

**Carry forward:** linear cell-scaling from a larger, wider-decomposed anchor **overprices** a small
2-rank compressible case by ≈ 2.3×; the per-cell rate improves as the mesh shrinks because fixed
per-iteration overhead amortises differently at 2,016 cells per rank. D16 is ≈ 1.4–1.8× D15 arm for
arm, which is the honest transonic-over-subsonic factor at this size.

The calibration row is `C-156` in `docs/COST_CALIBRATION.md`.

## 8. Artefacts, all still on disk

Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/`:
`D16_grade_20260827T114714Z.json`, `ledger.txt` (5 `ARM=` rows), `STATUS.chain` and the five per-arm
`STATUS.*`, per-arm `*.inspect.txt` kernel records, `{X,F}-{S,P}/d16_{X,F}.json`,
`grader_controls/F_{S,P}_planted.json`, per-arm solver logs and memory windows.

---

## The supervisor's check-3 sweep on the P5 reach claim — added 2026-08-27, dated section, appended

**Lines whose number changed above this section: 0** — this section is appended at the foot and
nothing above it is edited. Proved by byte comparison: the file's first N lines are byte-identical to
the committed blob this section was appended to, N being the blob's own line count.

**This is the DAFoam supervisor's check-3 sweep, not this lane's reading.** `SUPERVISION_CHARTER.md`
§3 makes verification of a big claim before belief a personal supervisor duty that may not be
delegated. The supervisor read every number below from the graded jsons before this text was
written; this lane re-derived each one independently from the same jsons and from the three
`RESULTS.md` tables, and reports the arithmetic as reproduced. **No gate, threshold, band, cap,
label or verdict moves here.** D15 stays `GATE FAIL`, D16 stays `GATE FAIL`, D17 stays `PASS`, and
every registered prediction keeps the outcome its comparator scored.

### The claim under test

The three items registered **one** P5 at three Mach numbers: *does the IDWarp rotation defect reach
the compressible solvers?* The scored outcomes were **HIT / MISS / MISS** at M 0.288 / 0.685 / 1.958.
**The naive reading of that pattern — "bounded to the incompressible path" — is wrong, and so is a
clean monotone-in-Mach story.** Both are refused below by the items' own evidence.

### The signal-to-noise table

**Signal** is the worst shipped-versus-patched divergence on the adjoint `CD` totals,
`divergence_pct = |J_shipped − J_patched| / |J_shipped|`, read from
`divergence_shipped_vs_patched_CD` in each item's grade json. **Noise** is the worst
**PATCHED**-row FD relative error on the same graded objective `CD` — the common-mode error the two
rows share, since both rows are graded against the same FD reference. Both columns are the `CD`
channel; the `CL` channel is stated separately below and is not folded in.

| item | M | solver | worst shipped-vs-patched divergence (SIGNAL) | worst PATCHED-row FD error (COMMON-MODE NOISE) | S/N |
|---|---|---|---|---|---|
| D15 | 0.288 | `DARhoSimpleFoam` | **44.878 %** (`shape[6]`) | 1.657 % (`shape[7]`) | **27.1** |
| D16 | 0.685 | `DARhoSimpleCFoam` | **5.487 %** (`shape[0]`) | 0.528 % (`shape[7]`) | **10.4** |
| D17 | 1.958 | `DAHisaFoam` | 2.268 % (`shape[3]`) | 2.777 % (`shape[3]`) | **0.82** |

`CL`, stated so the `CD` numbers are not reused where they do not reach: D15's patched `CL` worst is
0.0262 %, D16's is **1.6303 %** (`shape[6]`), D17 grades no `CL` at all (symmetry reading).

### The four findings, and nothing beyond them

1. **The defect PERSISTS into the compressible solvers.** The SHIPPED row `GATE FAIL`s at both
   M 0.288 (`DARhoSimpleFoam`) and M 0.685 (`DARhoSimpleCFoam`). This is not an inference from a
   component; it is the two items' own row verdicts.

2. **Its magnitude falls about 8x across that step** — 44.878 % → 5.487 % worst divergence
   (ratio 8.18). Stated as a ratio between two measured points, not as a rate or a trend.

3. **The component it lands on MOVES**: `shape[6]` at M 0.288, `shape[0]` at M 0.685. **This is why
   P5 read MISS at D16 while the row still failed.** P5 was a prediction about a *component*, not
   about the *defect*: the registered falsifier was mis-specified. The row failed, the defect was
   present, and the prediction that was supposed to detect it scored MISS. This is a defect of the
   prediction, not of the item, and it is carried as a lesson rather than as a repaired band.

4. **D17 is NOT DISCRIMINATING and is reported as uninformative.** Its worst divergence (2.268 %) is
   **smaller than its own PATCHED control row's worst FD error** (2.777 %) — S/N **0.82**. Component
   by component, SHIPPED-minus-PATCHED relative error in percentage points reads
   **+0.271 / −0.100 / +2.205 / +0.043 / −0.002** on `shape[0]/[1]/[3]/[4]/[5]`, against a patched row
   that itself carries 2.371 % and 2.777 % on two of those five components. Its SHIPPED `PASS` rests
   on `shape[3]` at **4.982 %** clearing a 5.0 % band by **0.018 percentage points** — a 0.36 %
   relative margin, decided in the third decimal, on a case whose control row is equally elevated.
   **D17's P5 MISS is a statement about D17's FD quality on a shock-containing inviscid case, not
   about the toolchain, and it must not be counted as evidence of absence.**

### What this sweep is not

**Three points on three different geometries is not a Mach sweep.** D17 changes geometry (planar
wedge, not the A1 airfoil), FFD block, DV definition, solver class and physics all at once; D15 and
D16 share the mesh, the FFD, the DV set and the design point. **The D15 → D16 pair is the only clean
comparison in the set — only the Mach number and the solver variant change between them** — and
finding 2's 8x is a statement about that pair and about nothing else. No monotone-in-Mach claim is
made or implied, and two points cannot support one.

**No new compute was spent on this sweep.** Every number is read from artefacts already on disk:
`/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic/D15_grade_20260827T114315Z.json`,
`.../CURRICULUM-D16-a1-naca0012-transonic/D16_grade_20260827T114714Z.json`,
`.../CURRICULUM-D17-cone-supersonic/D17_grade_20260827T130641Z.json`. **0.000 core-min.**

### What the sweep changes for D16, specifically

**Nothing in this item's verdict, and everything in how its P5 MISS is read.** §6 above already
declined to promote the MISS into a statement about the defect's reach; the sweep settles why that
was right. **D16's row failed and the defect was present — 5.487 % worst divergence against a
0.528 % patched control, S/N 10.4 — and the registered falsifier still scored MISS, because it named
`shape[6]` and the defect had moved to `shape[0]`.** The MISS is a defect of the prediction's
specification, not evidence about the toolchain, and it is the case that earns the lesson in
`docs/LESSONS.md`: **a registered falsifier should name the EFFECT, and the component only as its
expected locus.**

D16 is also half of the sweep's only clean comparison. Against D15 it holds the mesh (4,032 cells),
the FFD, the DV set and the design point fixed and changes the Mach number and the solver variant —
so the 8x fall in worst divergence between them is the one quantitative statement this set supports.

---

## The FD-plateau disclosure on the PATCHED row's `CL` `shape[6]` — added 2026-08-31, dated section, appended

**NOT FILED ANYWHERE.** Nothing in this section, or in the material it cites, is filed, sent, emailed,
uploaded, posted, registered or commented outside this box, now or ever (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED, and sending is Sanaa's decision alone.

**Lines whose number changed above this section: 0.** This section is appended at the foot, after the
2026-08-27 check-3 sweep, and nothing above it is edited. Proved mechanically, not asserted: the
pre-edit file is git blob **`2f0af0c3a4f74e364ddf53ad2b29c41cacdb675d`**, **255 lines**; a byte
comparison of that blob against the **first 255 lines** of the post-edit file is **empty**. Every line
above is byte-identical and this section begins at line **256**.

**Document version.** This record carries no numeric version field; it versions itself by **dated
appended sections**, the convention its own 2026-08-27 check-3 sweep established. The bump is
therefore that count — **dated appended sections 1 → 2**. No numeric version is invented here.

**IT MOVES NO GATE, NO THRESHOLD, NO BAND, NO CAP, NO LABEL AND NO VERDICT.** D16's item verdict stays
**`GATE FAIL`**; the rows stay SHIPPED **`GATE FAIL`** / PATCHED **`PASS`**; band D 5.0 % per
component, band E 5.0 % aggregate, the registered 10.0 % plateau tolerance, the 245.0 core-min ceiling
and every per-arm cap, and the scored outcomes of P1–P6b — **P5 included, which stays `MISS`** — all
stand exactly as recorded above. Gates closed at first compute (`CLAUDE.md` rule 2) and nothing here
reopens one. **This is a disclosure of what the registered plateau rule was and was not entitled to
conclude — not a regrade.** No compute was spent: **0.000 core-min**.

### 1. What was measured, and by what

A frozen, controlled, zero-solver-compute measurement at commit **`f032d94e`** read this item's own
frozen artefacts — no re-run, no regrade — and established that the **PATCHED row's FD plateau is NOT
PROVED** on one component of the lift constraint. The instrument is
`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_D19/d19_step_table.py` and the record is
**`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_D19/D15_D16_FD_STEP_TABLE.md`**. Its
sources are this item's frozen graded JSON
`/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic/D16_grade_20260827T114714Z.json`
(field `gates.G5_PATCHED.G5_{CD,CL}.components[].plateau_neighbour_pct`) and the raw endpoints in
`.../CURRICULUM-D16-a1-naca0012-transonic/{F-S,F-P}/d16_F.json`, from which the reader reproduced the
grader's published aggregate **0.146003 %** to 1e-9.

| PATCHED row, this item | components with a **two-sided** plateau | the exception |
|---|---|---|
| objective **`CD`** | **5 of 5**, worst neighbour `1.6132 %` | — |
| **`CL`** (G5c) | **4 of 5** | **`shape[6]` — ONE-SIDED: COARSE-side `14.0978 %`, fine-side `1.1268 %`** |

The two neighbour figures are the grader's own, unrounded:
`plateau_neighbour_pct = [14.097783376052847, 1.126810776327276]` on `CL` `shape[6]`, against the
registered tolerance of 10.0 %. The three registered steps are `{1e-2, 1e-3, 1e-4}`, graded at the
middle.

**The objective this item's optimiser would follow is the better-proved of the pair.** `CD` here is
the **only** one of the four PATCHED functions across D15 and D16 with a fully two-sided plateau on
all five components. The exposure is on the **constraint** Jacobian, and a lift-constrained drag
minimisation follows both.

### 2. Why the row still passed the rule that graded it

`d15_grade.py:75` — the grading path this item's `d16_grade.py` shares — sets
`PLATEAU_TOL_PCT = 10.0`, and `:356-358` refuses only when **both** neighbours miss:

    nb = [abs(d[0] - ref) / abs(ref) * 100.0, abs(d[2] - ref) / abs(ref) * 100.0]
    if min(nb) > PLATEAU_TOL_PCT:
        c.update({"verdict": "NOT A RESULT", "reason": "NO_PLATEAU"})

**`min`, not `max`.** A component that agrees with one neighbour and misses the other by any margin
whatever passes. **This is not a defect in the grader and it is not corrected here**: the rule was
frozen before this item's first compute, it graded exactly what it froze, and amending it now is
precisely what rule 2 forbids. The registered rule is entitled to conclude that the graded step is
**not isolated**; it is **not** entitled to conclude that the step sits in a **plateau**, because a
plateau is flat on both sides and a one-sided agreement is a boundary
(`VERIFICATION_CHARTER.md` §7 step 1).

### 3. This break IS diagnosed — unlike D15's, and in the opposite direction

`CL` `shape[6]` breaks at the **COARSE** end, 1e-2, with a differenced signal of `+6.744144e-03` and a
signal-to-noise against baseline bit-repeatability of **901,738**. At 900,000 to one, noise is not the
story. The deviation **grows with step**, which is the signature of truncation error, and on a
transonic section a 1e-2 shape perturbation moves the shock. **The plateau lies at 1e-3 and finer, and
1e-2 is simply outside it** — one extra decade would confirm it, not an investigation.

The contrast with the companion item is the reason both disclosures were written. D15's PATCHED `CD`
`shape[7]` breaks at the **FINE** end (`1.1559 %` coarse, `21.6299 %` fine) on the smallest component
in its set, at fine-step S/N **248.8**, and is **NOT diagnosed**: an S/N of 248.8 bounds the induced
error near 0.40 % against an observed break of 21.6299 %, ~50× larger, so cancellation there is a
hypothesis with a gap. **The two grounds fail on opposite functions and in opposite step directions**,
which is on its own sufficient reason that a sweep established on one does not transfer to the other.

### 4. The consequence, stated narrowly — the SHIPPED failures are UNAFFECTED

**This item's `GATE FAIL` and its cause class stand.** The SHIPPED row's `CD` failure is
**5.1511 %** on `shape[0]` against a 5.0 % band, and `CD` `shape[0]`'s plateau is **fully two-sided**
(neighbours 0.6646 % / 0.4980 %) — as is every other component on that function. **The row's `CD`
`GATE FAIL` is therefore entirely clear of the plateau ambiguity, which lives on `CL` alone.** The
`PHYSICS-FAIL — against the SHIPPED TOOLCHAIN` cause class assigned to this row in
`docs/dafoam/GRADING_CHAIN.md` stands unchanged; **this section does not edit that file.**

**One honest refinement rather than a blanket claim.** The SHIPPED `CL` `GATE FAIL` *is* on the
one-sided component — `shape[6]` at **41.8022 %** — which is about three times, not an order of
magnitude, beyond the 14.0978 % coarse-side excursion. Two things keep it standing anyway: the item's
`GATE FAIL` does not depend on it, since the `CD` row fails independently on a two-sided component;
and the split between the two rows on that component involves **no FD reference at all**. From the two
adjoint totals published in §3 above, `|J_shipped − J_patched| / |J_shipped|` on `CL` `shape[6]` is
**74.6290 %** — arithmetic performed in this section on the record's own published values, carrying no
gate and entering no ledger. Both rows are graded against the *same* `d_ref` at the *same* step, so an
imprecision in that reference is common-mode and cannot produce a 74 % split.

**What is qualified is one thing only: the PATCHED row's PRECISION on `CL` `shape[6]`.** Its
**1.6303 %** agreement with FD was demonstrated against a reference whose step placement is bracketed
on one side. That is a smaller claim than "the gradient is wrong", and this section makes no larger
one. The PATCHED `CD` aggregate of **0.146003 %**, the PATCHED `CL` aggregate of 0.1758 %, and the
row's `PASS` are untouched.

### 5. What this section does not do

It does not regrade; it does not re-score P5, which stays `MISS`; it does not amend
`PLATEAU_TOL_PCT` or the `min`/`max` reading retrospectively; it does not touch
`docs/dafoam/GRADING_CHAIN.md`, `docs/capability/dafoam_GRID.md`, the D19 registration or anything
under `curriculum_D19/`; and it creates no successor item. What a future item registers is a future
item's business.
