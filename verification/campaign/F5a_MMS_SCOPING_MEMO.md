# F5a-MMS — SCOPING AND COSTING MEMO

**Written 2026-08-25 by a cfd lab-lane under cfd-supervisor. ZERO COMPUTE: no
solver, no mesher, no case directory was created by this lane.**

**THIS IS NOT A PRE-REGISTRATION AND MUST NEVER BE CITED AS ONE.** It fixes no
gate, no threshold, no band, no cap and no label. Its purpose is to let the cfd
supervisor rule on whether F5a-MMS is worth pre-registering at all. If it is
ruled worth doing, a **separate frozen pre-registration** is written and
committed **before any compute**, under standing rule 2.

**Its subject** is §8.2 of `verification/campaign/F_FAMILY_TRIPLE_CROWN_SURVEY.md`
(commit `9ad2ad16`), which found that **no F case can reach `HOLDS` as it stands**
and proposed **F5a-MMS** as the one route it could see: **V** from a manufactured
solution, **G** from a cheap 2D equal-ratio triple, **P** from Roshko's own
measured Strouhal points.

**Vocabulary.** The standing rule 1 verdict vocabulary — `PASS` / `GATE REACHED` /
`GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` — and the tier vocabulary —
`HOLDS` / `GATE REACHED` / `SURVEYED` / `NOT HELD` / `NEVER RUN` — are separate
and are never conflated in this memo.

**Instrument constraint observed.** This memo quotes **no** GCI, observed order or
Richardson value from `sdk/workflows/tmr_verification.py`. It quotes none at all,
because F5a has produced none. Any Roache value in a future F5a pre-registration
comes from `scripts/roache_triple.py` and from nothing else.

---

## 1. THE SURVEY'S LOAD-BEARING CLAIMS, RE-VERIFIED BY THIS LANE

The supervisor's instruction was to verify these rather than inherit them, because
if the title-page verification does not reproduce the whole proposal collapses.
**It reproduces. Two of the survey's other claims do not, and one of this lane's
own interim readings was wrong and is recorded as such.**

### 1.1 Rule 15 title-page verification — REPRODUCES

`docs/papers/turbulence_models/roshko_1954_naca_tr_1191.pdf` (26,719,255 B) was
opened by this lane and **page 1 was rendered and read as an image** — not by
filename, not by file type, not by hash, and **not by its `.txt` sidecar**, which
rule 15 forbids and which is the trap the survey itself flagged for Meinders.

The rendered title page reads, verbatim:

> **REPORT 1191 — ON THE DEVELOPMENT OF TURBULENT WAKES FROM VORTEX STREETS — By
> ANATOL ROSHKO — California Institute of Technology**

**The survey's rule-15 claim is confirmed by an independent render.** The `.txt`
sidecar is 284,526 B of real OCR text, not a stub — but nothing in this memo's
verification rests on the sidecar, which is used only as a page index.

### 1.2 CORRECTION 1 — the correlation is stated for `50 < R < 150`, NOT `40 < R < 150`

The survey states the paper *"carries `S = 0.212(1 − 21.2/R)` for `40 < R < 150`"*.
**Read from the rendered page (PDF page 13 = report page 11), the paper attaches
the formula to a different range:**

> (1a) `F = 0.212R − 4.5` &nbsp;&nbsp;&nbsp; **50 < R < 150**
> (1b) `F = 0.212R − 2.7` &nbsp;&nbsp;&nbsp; 300 < R < 2,000
>
> which correspond to
>
> (2a) `S = 0.212 (1 − 21.2/R)` &nbsp;&nbsp;&nbsp; **50 < R < 150**
> (2b) `S = 0.212 (1 − 12.7/R)` &nbsp;&nbsp;&nbsp; 300 < R < 2,000

**`40 < R < 150` is a different statement in the same paper** — it is the **stable
range**, given on the same page as *"Stable range 40 < R < 150"* and on report page
8 as *"a stable, regular vortex street is obtained only in the Reynolds number
range from about 40 to 150."* Figure 9's caption independently confirms the
formula's range as `50 < R < 140`.

**Why this is material and not pedantry:** the survey's range would license an F5a
rung at **Re 40–50**, which is inside the stable range but **outside the range the
paper gives its own correlation for**. A V limb taken from (2a) at Re 45 would be
using the formula outside its stated validity, on the authority of a range the
paper attached to a different statement. **Any F5a-MMS pre-registration must
confine correlation use to `50 < R < 150`.**

### 1.3 Figure 5 — the survey is CORRECT, and this lane's own interim reading was WRONG

Recorded because the check was real and it changed direction once.

This lane first read report page 11's prose — *"The R-dependence of the pressure
drag coefficient `C_Dp`, taken from reference 19, page 425, is shown in figure 5"* —
and provisionally concluded that Figure 5 was a pressure-drag figure reproduced
from another author, which would have been fatal to the P limb.

**That reading was wrong, and rendering the figure settled it.** PDF page 11
(report page 9) carries:

> **FIGURE 5. — Strouhal number against Reynolds number for circular cylinder.**

with **Strouhal number `S` on the left axis (.12 to .22)** and **Reynolds number
`R` on a LOGARITHMIC axis from 10 to 10,000**, carrying Roshko's own measured
points for **eight cylinder diameters** — `d` = 0.0235, 0.0362, 0.0613, 0.0800,
0.0989, 0.158, 0.318, 0.635 cm — plus Kovasznay's points as a separate symbol.
**Reference 19 supplies only the dashed `C_Dp` overlay drawn against a secondary
right-hand axis (0 to 2.0); it does not supply the Strouhal points.**

**The survey's Figure 5 claim stands.** The prose that misled this lane is the
paper's own, and a reader working from the sidecar alone would have made the same
error. **This is a second, independent demonstration that rule 15's "render it"
rule earns its keep** — the OCR text supported a false conclusion that the image
refuted.

### 1.4 CORRECTION 2 — Figure 4 exists, carries the SAME data on a LINEAR axis, and the survey does not mention it

PDF page 10 (report page 8) carries:

> **FIGURE 4. — Strouhal number against Reynolds number for circular cylinder.**

Identical caption, identical symbol set, **linear `R` axis from 0 to 1,400**, `S`
axis .120 to .220 with **gridlines every 0.010**. Report page 8 states *"The
present measurements of S(R) are given in figures 4 and 5."*

**The two figures are the same measurements plotted twice**, and which one to
digitise is a real design choice with a measurable consequence — §4.2 below.

### 1.5 The paper's own uncertainty statement, read from the render

Report page 8: *"scatter is small, and the measurements agree with those of
Kovasznay … It is believed that the **best-fit line is accurate to 1 percent**."*
And immediately after: *"The measurements are corrected for tunnel blockage, but
**no attempt is made to account for end effects**."*

Both sentences matter and both are used in §4.

---

## 2. THE V LIMB — the manufactured solution

### 2.1 What is proposed

A **steady, divergence-free manufactured velocity field** imposed on the **same
solver** (`pimpleFoam`, OpenFOAM v2606, the build the P limb uses) and on the
**same mesh family** (the 4-block O-grid of §3), with an analytic momentum source
added through a `codedSource` `fvOption` so no solver rebuild is required.

- **Divergence-free by construction**, derived from an analytic stream function
  `u = ∇×ψ`, so **no mass source is needed** and PIMPLE's pressure equation is not
  asked to absorb a continuity residual. This is the single most important design
  choice in the limb; a manufactured field that is not divergence-free turns the
  pressure solve into an uncontrolled part of the experiment.
- **Dirichlet velocity on every boundary** — the cylinder wall and the farfield —
  taken from the manufactured field, so the boundary treatment is not being
  verified along with the interior and cannot mask an interior error.

### 2.2 The graded quantity and the expected order

- **Quantity: the volume-weighted discrete `L2` norm of `|u − u_manufactured|`
  over all cell centres**, at the three levels of §3.
- **Expected observed order: `p ≈ 2`**, from OpenFOAM's default `Gauss linear`
  interpolation on a smooth field.
- **Honest expectation, stated before anyone runs it:** on a *graded, curvilinear*
  O-grid the observed order for second-order schemes commonly lands **1.7 – 2.0**
  rather than exactly 2. A pre-registration should band the order accordingly and
  derive that band from the grading arithmetic, not from a first measured value.

### 2.3 What makes it a genuine code-verification exercise — and the one place it is weaker than it looks

**It is genuine on the spatial discretisation**: the reference is exact by
construction, owes nothing to Roshko, and the error norm is computed against a
closed-form field on the same cells the P limb solves on. A wrong discretisation
cannot pass it by accident, and there is no route by which the measured error is
derived from the reference.

**It is weaker than it looks in one respect, and this is stated here rather than
discovered by a reviewer:** a **steady** manufactured field verifies the spatial
operators and the boundary treatment, and **verifies nothing about the time
integration, the PIMPLE outer-corrector loop or the shedding dynamics** — which is
the entire mechanism the P limb depends on. So V and P here are **independent**,
which is what Ruling 4 clause 5 asks for — but they are arguably *too* independent:
**the V does not underwrite the P.** A HOLDS row assembled this way carries a V
certifying a code path the P limb only partially exercises.

**An unsteady MMS would close that gap and is materially harder** — it requires a
time-dependent source and turns the error norm into a function of `Δt` as well as
`h`, i.e. two ladders rather than one. **It is not proposed here, and the gap is
named rather than absorbed.**

---

## 3. THE G LIMB — the ladder

### 3.1 The mesh family, and it already exists on this box at one level

The anchor is a real, completed case on this box:
**`/home/ubuntu/certonomous-runs/unsteady-cylinder/cyl-re100/`** — `pimpleFoam`,
OpenFOAM `_481094f-20260618 v2606`, **`nProcs : 1`**, `nu = 0.01`, `magUInf = 1`,
`lRef = 1`, i.e. **Re = 100**. Its `blockMeshDict` is a **4-block O-grid**, each
block `(90 70 1)` with `simpleGrading (186.339 1 1)`, farfield 20 diameters:
**25,200 cells.**

### 3.2 The proposed levels, refinement ratio and dimensionality

| level | per-block `(nr nt 1)` | cells | status |
|---|---|---|---|
| **L1 coarse** | `(45 35 1)` | **6,300** | does not exist |
| **L2 medium** | `(90 70 1)` | **25,200** | **EXISTS AND HAS BEEN SOLVED** |
| **L3 fine** | `(180 140 1)` | **100,800** | does not exist |

- **`r = 2` exactly, by construction, in BOTH mesh directions** — both `nr` and
  `nt` double at every level, so the ratio is fixed by the generator and is never
  inferred from a cell count. `form="equal"` is asserted so the instrument
  **refuses** an unequal ladder.
- **`dim = 2` explicitly** — these are single-cell-thick 2D `blockMesh` slabs.
- Graded through **`scripts/roache_triple.py` only**.

### 3.3 The one place `r = 2` is NOT exact, quantified rather than waved past

Holding `simpleGrading 186.339` constant while doubling `nr` does **not** halve the
near-wall cell exactly. Computed from the geometric-progression arithmetic:

| transition | first-cell height ratio | departure from exact halving |
|---|---|---|
| L1 → L2 (`nr` 45 → 90) | **0.5094** | **+1.9 %** |
| L2 → L3 (`nr` 90 → 180) | **0.5046** | **+0.9 %** |

**Is that departure material? It is bounded by a measurement this lab already
owns.** `R7_STROUHAL_SPACING_RESULTS.md` measured, at **Re 1000**, that a
**+55.29 %** change in first-cell height moved Strouhal by **+0.120 %**. Scaling
that measured sensitivity linearly, a **1.9 %** first-cell mismatch would move
Strouhal by of order **0.004 %** — three orders below any band worth gating.

**Two honest caveats on that bound.** It is measured at Re 1000, not Re 100, and
the same document measured the same perturbation moving Strouhal by **−35.1 %** at
Re 3900 — so the sensitivity is strongly regime-dependent and the low-Re end is the
robust end, which is where F5a-MMS sits. And the scaling is linear extrapolation
from one point. **If the supervisor wants the departure removed rather than
bounded, it is removable at zero cost**: set each level's `simpleGrading` so the
first cell halves exactly, which changes the total expansion ratio by under 2 % and
costs nothing but a dictionary value.

### 3.4 THE MESH ADMISSION GATE — measured at the anchor, UNVERIFIED at two of three levels

**This is the F12 lesson applied before the fact.** F12 has since fired and been
graded `GATE FAIL` / `NOT HELD`, dying on the **max non-orthogonality ≤ 70°** hard
gate at **all three levels** (70.6463 / 70.8615 / 72.5422°) with over-threshold face
counts scaling ×4.03 and ×4.00 — a fixed *fraction* of the mesh that refinement
does not cure. **Registering a ladder whose meshes were never shown admissible is
what cost F12 its campaign, and F5a must not repeat it.**

**Measured, from `log.checkMesh` of the 25,200-cell anchor:**

| gate | `MESH_STANDARD.md` §3 | measured at L2 | margin |
|---|---|---|---|
| max non-orthogonality | hard gate **70°** | **4.436338e-06 °** | ~7 orders |
| max skewness | hard gate **4** | **0.01911847** | **209×** |
| max aspect ratio | reported | **2.5020** | — |
| `checkMesh` verdict | — | **`Mesh OK`** | — |

**Corroborating evidence that this is a property of the topology and not of the
level:** the R7 cylinder mesh at a **different** cell count (22,400) reports the
**identical** max non-orthogonality, `4.436338e-06`, with max skewness 0.02658 and
`Mesh OK`. A structured 4-block O-grid is orthogonal by construction and the number
does not move with resolution.

**But this lane states plainly what is NOT verified.** **The L1 and L3 meshes do
not exist and have not been `checkMesh`'d.** The argument above is a topology
argument plus two data points at neighbouring cell counts. **It is not a
measurement of the levels that would actually be graded.**

> **PRE-CONDITION ON ANY F5a-MMS PRE-REGISTRATION, and this lane recommends it be
> made binding: build all three meshes and run `checkMesh` on each, and register
> the three measured non-orthogonality, skewness and aspect-ratio values IN the
> pre-registration, BEFORE the levels are frozen.** That is one `blockMesh` and one
> `checkMesh` per level and **no solver at all**. This lane did not do it because
> its brief forbade running a mesher.

### 3.5 PLATEAU — the hardest part of the proposal, and this lane's honest reading

**Standing rule 5 clause (1) already binds: any level not iteratively converged
*or not plateaued* → `NOT A RESULT`.** This is not a new gate. `VMFL051` is the
worked warning: a deviation of **−0.2337 %** that looked like a `PASS` still
returned **`NOT A RESULT`**, with the triple **`OSCILLATORY` at R = −1.3486** and
**no GCI quoted because the values were not monotone**.

**The difficulty is real: a shedding cylinder is unsteady by construction and a
periodic signal never plateaus pointwise.** `Cl` oscillates forever. So "plateau"
must be defined on a *derived* quantity, and defining it loosely is how a Strouhal
ladder produces a beautiful, meaningless order.

#### 3.5.1 The reading: plateau is a property of the EXTRACT, not of the signal

**The quantity that must plateau is the extracted Strouhal number itself, as a
function of the window it is extracted from.** A periodic signal has a well-defined
cycle, so "the cycle-averaged extract stops moving when you move the window" is a
genuine, checkable, falsifiable criterion and not a euphemism. Proposed shape, for
a pre-registration to fix:

For each level, extract `St` over **non-overlapping windows of exactly K whole
shedding cycles** (`K` fixed in advance), marching backwards from `endTime`. The
level is **PLATEAUED** only if **all four** hold:

1. **Cycle-to-cycle period stationarity** — within the final window,
   `σ(T_i)/mean(T_i) < ε₁`.
2. **Window-to-window invariance** — `|St(final) − St(previous)| / St < ε₂`.
3. **Amplitude stationarity** — `Cl` peak-to-peak changes by `< ε₃` between the
   same two windows.
4. **Mean-quantity drift** — `halves_drift` on `Cd` `< ε₄`, as a **fourth** clause
   and never as the only one.

#### 3.5.2 Can it be made rigorous? MEASURED ANSWER: yes, and by a wide margin

This lane extracted `St` from the anchor's **existing** `postProcessing/forceCoeffs1/0/coefficient.dat`
(zero compute — reading an artifact already on disk) by linear-interpolated upward
zero-crossings of `Cl` about its window mean:

| window (t) | cycles | period `T` | **`St`** | `σ(T)/T` | `Cl` p-p/2 | `halves_drift(Cd)` |
|---|---|---|---|---|---|---|
| 45 – 90 | 6 | 6.226822 | **0.160596** | **1.596 %** | 0.31192 | **4.1822 %** |
| 60 – 105 | 6 | 6.156069 | 0.162441 | 0.443 % | 0.31491 | 1.0657 % |
| 75 – 150 | 11 | 6.131368 | 0.163096 | 0.046 % | 0.31550 | 0.1526 % |
| 90 – 120 | 4 | 6.130784 | 0.163111 | 0.013 % | 0.31540 | 0.0338 % |
| 100 – 150 | 7 | 6.129825 | 0.163137 | 0.003 % | 0.31550 | 0.0211 % |
| **120 – 150** | 4 | **6.129694** | **0.163140** | **0.000 %** | 0.31550 | **0.0026 %** |

**The criteria separate a settled state from an unsettled one by roughly two orders
of magnitude**, which is what makes the definition rigorous rather than cosmetic:

- criterion 2 between the last two windows: **0.018 %**;
- criterion 1 in the final window: **0.000 %** (`σ(T) = 2.9e-05` on `T = 6.1297`);
- criterion 3 between the last two windows: **0.032 %**.

**So the answer to the supervisor's question is YES — plateau CAN be made rigorous
for a periodic quantity**, and the reason is structural: the periodicity supplies
the averaging window, and window-to-window invariance of a cycle-averaged extract
is a real convergence statement.

#### 3.5.3 And the measurement also shows the lab's CURRENT stationarity gate is far too loose for this

This is the sharpest finding in the memo and it is measured, not argued.

**The lab's operating stationarity gate on this exact family is `halves_drift(Cd)`
against 10 %** — R7 used it (*"against the 10 % gate"*) and the filmed cylinder act
used it (*"stationarity drift on the production mesh: 3.9 %, inside the 10 %
stationarity gate"*).

**On the anchor, the window t = 45–90 has `halves_drift(Cd)` = 4.18 % — it PASSES
the 10 % gate comfortably — while the Strouhal number extracted from that same
window is 0.160596, which is 1.56 % BELOW its own settled value of 0.163140.**

**A state that the lab's current stationarity gate calls stationary is still 1.6 %
away from its own asymptote on the quantity being graded.** Against a P band of
order 1 %, that is fatal, and it would be invisible: the run would look converged,
the drift gate would be green, and the Strouhal value would be wrong by more than
the band. **The 10 % `halves_drift` gate must not be the plateau clause for a
Strouhal ladder.** On this evidence it is loose by more than an order of magnitude.

#### 3.5.4 Three caveats this lane will not let stand unstated

1. **CONTAMINATION, declared. This lane has now READ the medium level's settled
   answer** — `St = 0.163140`, `Cd = 1.32956`, `T = 6.129694`. **Any F5a-MMS
   pre-registration is therefore written in knowledge of one of the three values it
   would grade.** The thresholds `ε₁…ε₄` must be derived **from principle** — the
   sampling interval, the cycle count, the mesh arithmetic — and **never** read off
   the table in §3.5.2, or the plateau clause is tuned to a known answer. The F3
   conversion faced the identical problem and handled it by declaring the knowledge
   and deriving every band from a stated principle; the same discipline is required
   here and it should be written into §2 of the pre-registration explicitly.
2. **The plateau timescale is itself mesh-dependent, and this is measured at ONE
   level only.** Numerical dissipation differs between 6,300 and 100,800 cells, so
   the transient may still be growing at `t = 150` on one level and long settled on
   another. **The plateau clause must therefore be per-level with a refusal — a
   level that has not plateaued by `endTime` returns `NOT A RESULT`.** It must NOT
   be "extend the run until it plateaus", which converts the clause into a tuning
   knob and destroys the freeze.
3. **Plateau does not buy monotonicity.** Even with all three levels plateaued, the
   triple can return `OSCILLATORY` or `DIVERGENT` and the row is then
   `NOT A RESULT` whatever the value — the `VMFL051` shape exactly. The lab's own
   unequal-ratio Re-100 cylinder ladder (2,496 / 5,032 / 8,640 cells → `St` 0.1245 /
   0.1490 / 0.1578) is monotone, but its own record says *"the ladder is not
   conclusive because the value the ladder extrapolates to falls outside the range
   it measured."* **Monotonicity at `r = 2` is a hope, not a plan.**

### 3.6 The existing 3-level Re-100 ladder cannot be reused, and here is why

`certonomous-runs/.solve-cache/cylinder-vortex-Re100-{coarse,medium,fine}` holds
**2,496 / 5,032 / 8,640** cells at `endTime` 90. Cell ratios **2.016** and
**1.717**; in 2D that is `h`-ratios **1.420** and **1.310** — **not equal-ratio**.
`form="equal"` would refuse it, and correctly. **A fresh ladder is required; the
existing one is not a shortcut.**

---

## 4. THE P LIMB — Roshko's measured points, and a problem the survey did not see

### 4.1 What would be compared, and at what Reynolds numbers

- **Quantity: the Strouhal number `St = f·D/U`**, from the shedding frequency of
  the `Cl` signal, over a plateaued window (§3.5).
- **Reynolds numbers: inside `50 < R < 150`** (§1.2 — *not* 40), which is
  simultaneously inside Roshko's stable range **and** inside the range he attaches
  to his own correlation. **Re = 100 is the natural rung** and is the one the lab
  already has a solved mesh for.
- **A real strength worth stating:** at Re 100 the cylinder wake is genuinely
  two-dimensional — the 3D wake transition sits near Re 180–190 — so the 2D
  idealisation is not a concession here. **Roshko's entire stable range lies below
  the 3D transition.** This is one of the very few places in the lab where a 2D
  computation is the physically correct model rather than a budget compromise.

### 4.2 Digitising the figure — feasible, and this lane says which figure and what it would cost in accuracy

The survey did not attempt this and did not pretend to. This lane did not digitise
either, but measured the two candidate figures from the renders so the question can
be ruled on:

| | **Figure 4** (report p. 8) | **Figure 5** (report p. 9) |
|---|---|---|
| `R` axis | linear, 0 – 1,400 | **logarithmic, 10 – 10,000** |
| fraction of axis width spanned by `50 < R < 150` | **≈ 7.9 %** | **≈ 19 %** |
| `S` axis | .120 – .220, **gridlines every 0.010** | .12 – .22, gridlines every 0.020 |
| extra content | none | dashed `C_Dp` curve on a second axis |

**Neither figure dominates: Figure 5 is ~2.4× better in `R` over the target band;
Figure 4 is 2× better in `S`.** The honest recommendation is **digitise BOTH and
cross-check**, and treat the disagreement between them as an empirical component of
the digitisation uncertainty rather than asserting a pixel budget.

**Feasibility: yes.** The scan is 26.7 MB and the symbols are individually
resolvable at render resolution; the eight cylinder-diameter symbols are
distinguishable from each other and from Kovasznay's.

**Two mandatory exclusions.** **Kovasznay's points must be excluded** — they are
another author's measurements reproduced inside a held primary, i.e. secondary, and
including them would smuggle an unverified source into a P cell. **The dashed
`C_Dp` overlay in Figure 5 must be excluded** — it is *"taken from reference 19,
page 425"* and is not Roshko's measurement either.

**Uncertainty, and here the pixel budget is NOT the dominant term.** At the render
resolution used here, 1 px ≈ 1.9e-04 in `S`, and realistic symbol-centre location
is ±2–3 px, i.e. **±(4–6)e-04 in `S`, about ±0.25–0.35 % at `S ≈ 0.165`.** That is
comfortably small. **It is not what limits the P limb.**

### 4.3 THE PROBLEM THE SURVEY DID NOT SEE, and it is the central finding of this memo

**The tight reference is `V`, and the `P`-eligible reference is scattered.**

- The paper's tight statement is about the **best-fit line**: *"it is believed that
  the best-fit line is accurate to 1 percent."* **But the best-fit line IS the
  correlation** `S = 0.212(1 − 21.2/R)` — and under **Ruling 4 a correlation is
  definitively `V` and definitively not `P`**, which is the survey's own §6.2(b)
  finding. **The one reference in this paper that is tight enough to gate on cannot
  buy `P`.**
- What *can* buy `P` is the **individual measured points**. Read off the rendered
  Figure 4 near `R ≈ 100`, those points scatter over roughly **`S` = 0.158 to
  0.172** — of order **±4 %**. A P gate built on that scatter is **four times wider
  than the deviation it would be trying to detect**, and a solve that is 2–3 % off
  would "pass" it meaninglessly.

**So the P limb as the survey conceived it — "P from Roshko's own measured points" —
buys a `PASS` that is not worth having, and this must be settled before, not after,
a pre-registration is frozen.** Three ways out, none of which is this lane's to
choose:

1. **Gate against the scatter band honestly** and accept that F5a's `P` is a weak
   `PASS` with an explicitly wide band, stated on its face. Defensible, and much
   less impressive than "the lab's first HOLDS" sounds.
2. **Ask verification whether the best-fit line, when read off a held primary's own
   figure, is `P` rather than `V` in this instance.** It is a fitted line and Ruling
   4 says correlation is `V`; this lane does not expect that to go F5a's way and
   does not propose it as a plan.
3. **Restrict the band to one cylinder diameter's symbol series**, which removes
   part of the inter-run scatter. Feasible from the figure; **whether it is
   legitimate to select a subset of an author's points is verification's call.**

**And the rubric question the survey already referred upward still stands:** whether
digitising Figure 4/5 **of a primary the lab holds and has opened** is a primary
reading, as against F7a's digitisation of a 2021 secondary. **If it is ruled the
other way, F5a's `P` dies with every other `P` in the family and the survey's
fallback finding stands: the F family cannot produce a `HOLDS` at all.**

### 4.4 What the lab's EXISTING Re-100 solves actually score against Roshko — measured

Zero compute; read from artifacts on disk. Roshko (2a) at Re 100 gives
`S = 0.212 × (1 − 0.212) = 0.167056`.

| source | cells | `St` | deviation vs Roshko (2a) |
|---|---|---|---|
| filmed cylinder act, fine mesh | 8,640 | 0.1578 | **−5.54 %** |
| **the anchor, settled window t = 120–150** | **25,200** | **0.163140** | **−2.34 %** |

**No mesh this lab has ever run at Re 100 lands within 1 % of Roshko's own
correlation.** The trend across the two is toward it as cells rise, which is
consistent with under-resolution, but **this lane will not extrapolate two
unequal-ratio points into a prediction for the fine level.**

**A separate and serious provenance point falls out of this.** The filmed cylinder
act's on-screen gate reads *"Correlation 0.1590 | Solved 0.1578 | Deviation
0.77 % — PASS"*. **`0.1590` is not Roshko's value at Re 100; Roshko's is
`0.167056`.** The repository's own research proposal
`research/agenda/proposals/naca-report-1191-settles-which-strouhal-form-governs-the-filmed-gate.json`
already records this: the house constant gives `0.158994`, the cited form gives
`0.167056`, *"a miss at 5.54 percent"*, and the proposal states the constants are
*"attributed by the repository to its own task prompt rather than to any paper."*
**That proposal's `status` is still `proposed`, and NACA 1191 is now on disk and has
now been read.** The item it exists to close is closeable at zero compute.
**REPORTED, NOT ACTED ON — it is a filmed surface and not this lane's to touch.**

---

## 5. COST

**Rule 12 binds: a proposal with no cost is disqualified, and a cost is never
called measured unless a record backs it.** The survey reported F5a `UNCOSTED` and
**refused to extrapolate F11's 8.02 core-min because F11 is steady and a Strouhal
ladder is unsteady. That refusal was correct and this memo does not undo it — F11
is not used here in any way.** Instead the cost is anchored on a **named, measured,
unsteady solve of this exact physics on this exact box.**

### 5.1 The anchor — measured, with its artifact

**`/home/ubuntu/certonomous-runs/unsteady-cylinder/cyl-re100/log.pimpleFoam`**

| what | measured |
|---|---|
| solver / build | `pimpleFoam`, OpenFOAM `_481094f-20260618 v2606` |
| ranks | **`nProcs : 1`** (serial) |
| cells | **25,200** |
| Reynolds number | **100** (`nu` 0.01, `magUInf` 1, `lRef` 1) |
| `endTime` / `deltaT` / stepping | 150 / 0.005 / `adjustTimeStep yes`, `maxCo 1.5` |
| time steps | **9,235** |
| last time reached | **`Time = 150`**, `End` present |
| **`ExecutionTime`** | **3,056.37 s** |
| **`ClockTime`** | **4,025 s** |

**Both figures are reported and neither is hidden.** `ClockTime` is the wall clock
and is the rule-12 basis (core-min = wall s × ranks ÷ 60); `ExecutionTime` is the
solver's own accounting. The **969 s gap is contention and I/O on a shared box**;
per `COMPUTE_BUDGET_CHARTER.md` §6 it is **named as waste, not absorbed into a
ratio**. **`ClockTime` 4,025 s exceeds the 3,600 s stall threshold, so this row is
stall-flagged** and its gross figure should be read as an upper bound.

### 5.2 The scaling model — stated AS a model, with its assumption exposed

Cost ∝ (cells) × (time steps). Under `adjustTimeStep` at fixed `maxCo`, halving `h`
halves `Δt`, so **steps double**; cells **quadruple** in 2D. **Cost therefore rises
×8 per level.** Physical `endTime` is set by the *physics* of transient decay, not
by the mesh, so it is held at 150 across all three levels — which is what makes the
model clean.

**The assumption that is NOT verified on this family:** that steps scale exactly as
`1/h`. This lab has no refinement pair of this case to check it against. It follows
from a fixed Courant limit and is standard, but **it is a model and it is labelled
one.** If it is wrong it is wrong in the cheap direction only if `Δt` falls slower
than `h`, and in the expensive direction otherwise.

### 5.3 The G+P ladder cost — COSTED

| level | cells | `ExecutionTime` basis | **core-min** | `ClockTime` basis | **core-min** |
|---|---|---|---|---|---|
| L1 coarse | 6,300 | 382.0 s | **6.37** | 503.1 s | **8.39** |
| **L2 medium** | 25,200 | **3,056.4 s (MEASURED)** | **50.94** | **4,025 s (MEASURED)** | **67.08** |
| L3 fine | 100,800 | 24,451.0 s | **407.52** | 32,200 s | **536.67** |
| **TRIPLE TOTAL** | | **27,889 s** | **464.82** | **36,728 s** | **612.14** |

- **Dollars, DERIVED NOT MEASURED**, at the owner-stated `$0.0513/core-h` (this box
  cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5): **$0.397** on the
  `ExecutionTime` basis, **$0.523** on the `ClockTime` basis.
- Under the $25 pre-authorisation — **which is not a ceiling** (standing rule 9). A
  pre-registration's own cap binds and must be set from its own arithmetic.

### 5.4 THE HEADLINE COST FINDING, and it contradicts the survey

**§8.2 of the survey is titled *"The proposal — F5a-MMS, and it is cheap."* On the
measured anchor, IT IS NOT CHEAP.** At **465 – 612 core-minutes** it would be the
**second most expensive item in the F family**, behind only F12's 1,300 core-min
cap and roughly **13 – 17× the entire F3 conversion (35.23 core-min)**.

The reason is structural and worth stating plainly: **an unsteady ladder pays ×8 per
level where a steady ladder pays ×4**, because refinement buys smaller time steps as
well as more cells. **The fine level alone is 407 core-min — 88 % of the ladder —
and at 32,200 s ClockTime serial it is a ~9-hour single run**, far past the 3,600 s
stall threshold, on a box shared with other teams' solvers.

**Parallel execution buys wall time and does NOT buy core-minutes.** R7 measured on
this same family that **4 ranks cost 17.4 % MORE core-minutes than 1 rank** (47.31
against 40.31) at 5,600 cells/rank, at a 3.41× speedup rather than the lab's
guidance figure of 4.71×. At the fine level the decomposition would be far fatter
(25,200 cells/rank), so the penalty should be smaller — **but that is UNMEASURED on
this box for this case and this memo does not assume it.** The core-minute figures
above are the serial ones and are the honest ones.

### 5.5 The V limb — UNCOSTED, with the single measurement that would close it

**The MMS ladder is UNCOSTED and this memo will not guess it.** It is a *steady*
solve with a `codedSource` `fvOption` — a different residual path, a different
convergence criterion and an extra per-cell source evaluation — and **the only
honest anchor for it would be F11's steady cavity, which is a different solver on a
uniform Cartesian mesh.** Extrapolating it would be exactly the move the survey
correctly refused.

> **THE MEASUREMENT THAT CLOSES IT:** one **L1-only** MMS run — 6,300 cells, the
> coarse mesh, the `codedSource` in place, run to its residual stop — and read its
> `ExecutionTime` and iteration count off its own log. The ×8-per-level model of
> §5.2 then gives L2 and L3 from a measured number on the correct code path.
> **This is a small, bounded, pre-registerable probe**, and on the anchor's
> arithmetic the whole MMS ladder would plausibly sit far below the shedding ladder
> because a steady solve does not pay the ×2 step penalty — **but "plausibly" is
> not a cost and it is not offered as one.**

**Consequence for the ruling:** the **G+P limb is COSTED at 465–612 core-min**; the
**V limb is UNCOSTED**; so **F5a-MMS as a whole is not yet fully costed**, and under
rule 12 the correct sequence is **probe first, pre-register second, run third.**

---

## 6. WHAT COULD MAKE THIS FAIL — named in advance

1. **The P band problem (§4.3) — the most likely killer, and it is not a compute
   problem.** The tight reference is `V` by Ruling 4; the `P`-eligible measured
   points scatter ±4 % at `R ≈ 100`, four times the deviation worth detecting.
2. **The rubric ruling on digitising a held primary's figure.** If it goes against
   F5a, `P` dies and with it every `P` in the F family.
3. **Plateau threshold contamination (§3.5.4).** This lane has read the medium
   level's settled `St`. Thresholds derived from that table would be tuned.
4. **Per-level plateau timescale (§3.5.4).** `endTime` 150 is verified adequate at
   25,200 cells and at no other level. A level that has not plateaued must return
   `NOT A RESULT`, not get a longer run.
5. **A non-monotone triple.** `OSCILLATORY` or `DIVERGENT` → `NOT A RESULT`
   whatever the value, no GCI quoted. The `VMFL051` shape.
6. **Mesh admission at L1 and L3 (§3.4) — UNVERIFIED.** The topology argument is
   strong and it is still not a measurement of the meshes that would be graded.
   **This is the F12 failure mode and it must be closed before the freeze.**
7. **Cost (§5.4).** 465–612 core-min, 88 % of it in one ~9-hour serial run on a
   shared box. A contention stall inside that run is a real operational risk and
   an overrun **stops the run**; it does not get a new budget.
8. **The MMS may not deliver order 2** on a graded curvilinear O-grid, and a
   `codedSource` `fvOption` is a code path with **no planted-zero control history
   in this lab**. Rule 3 applies to the MMS error reader with full force: it must
   plant a known perturbation, read it back, and **refuse** if it cannot see it.
9. **V does not underwrite P (§2.3).** A steady MMS verifies spatial operators and
   verifies nothing about the time integration the P limb depends on. Independent —
   arguably too independent. A reviewer will ask.
10. **`50 < R < 150`, not `40` (§1.2).** A rung below Re 50 uses the correlation
    outside its stated range.
11. **Model-form gap in the P reference.** Roshko *"corrected for tunnel blockage,
    but no attempt is made to account for end effects"*; the CFD is infinite-span
    2D. **Unquantified, and it is a real difference between the reference and the
    computation.**
12. **A latent dictionary regime gap (§8.2).** The anchor's `fvSolution` has no
    `residualControl` at all, so a steady MMS limb copied from it would compute an
    error norm on an unconverged field — **and a smoke test cannot detect that.**
13. **Roshko fails Ruling 7 condition 3 on six of seven registered rungs, and the
    seventh fails condition 4 by threefold (§9.4, §9.5).** The instrument the brief
    hoped was free is admissible at one rung, where the case then misses it.
14. **The absent Re-100 pre-registration.** No F5a pre-registration exists anywhere
    for any rung. Everything above is scoping, and none of it is frozen.

---

## 7. WHAT THIS LANE COULD NOT VERIFY

Stated plainly, because an honest gap is worth more than a confident guess.

1. **Mesh admission at L1 and L3.** No mesher was run; the brief forbade it.
2. **The MMS limb's cost**, and whether a `codedSource` `fvOption` MMS converges at
   all on this mesh family. Neither was tried.
3. **The digitisation itself.** Both figures were *rendered and measured for axis
   geometry*; **no point was digitised** and no band is proposed.
4. **The step-count scaling `steps ∝ 1/h`** (§5.2). It follows from a fixed Courant
   limit; it is unverified on this family because no refinement pair exists.
5. **Whether the fine level's `St` reaches Roshko's 0.167056.** Two unequal-ratio
   points trend toward it; that is not an extrapolation this lane will make.
6. **Whether V and P here would be ruled two distinct comparisons.** Verification's
   call, as the survey said.
7. **The parallel core-minute penalty at a fat decomposition.** R7 measured it at a
   thin one only.

---

## 8. LAUNCH GUARDS — scoped for both limbs, with what each one actually buys

### 8.1 The mechanism, cited and not owned

From ansys-verification's **VMFL045** crash. **A comparator selftest proves the
GRADER, not the CASE.** VMFL045's comparator passed **45/45 with real negative
controls** and could never have caught its crash: nothing in the pre-compute checks
exercised the actual solver dictionary set, and the case died at **wall 0 s** on
`FOAM FATAL IO ERROR: Entry 'e' not found in dictionary "system/fvSolution/solvers"`.

**The mechanism is what makes it relevant here.** VMFL045's `fvSolution` solvers
block was **byte-identical to VMFL051's**, and VMFL051 ran 1,693 timesteps fine with
the same missing entry — because **VMFL051 is inviscid and VMFL045 is viscous**, and
the solver only enters the implicit viscous corrector when `μ > 0`, which is the path
needing the missing key. Implicit solve counts: **0** across VMFL051's whole
successful run, **1** in VMFL045 before death. **The dictionary was complete for one
regime and incomplete for another, and the gap was latent, not visible.**

*Cited as another team's finding. This lane assigns no lesson from it.*

### 8.2 F5a is doubly exposed — and here is the AIMED check, not a decorative one

**F5a-MMS pairs an MMS run with a shedding-cylinder run: two different solver
configurations under one pre-registration.** Any dictionary shared or copied between
them crosses a regime boundary by construction. The supervisor asked that, if F5a's
configuration derives from another F case, the case be named so the check is aimed.
**It does, and it is named.**

**MEASURED by this lane:** the anchor case's `fvSolution` **`solvers` block is
BYTE-IDENTICAL** to that of the F5a ladder's Re-1000 case at
`/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re1000/system/fvSolution`.
**That is the VMFL045 shape exactly — one solvers block shared across two cases.**

Reading that dictionary against what the two limbs would each need turns up **three
regime gaps, and the first is WORSE than VMFL045's because it fails silently:**

1. **There is no `SIMPLE` dictionary and no `residualControl` anywhere in the
   file.** It carries `PIMPLE { nOuterCorrectors 2; nCorrectors 2;
   nNonOrthogonalCorrectors 1; }` and nothing else. **A steady MMS limb copied from
   this dictionary would have NO CONVERGENCE CRITERION** — it would run to `endTime`
   and stop, and the MMS error norm would be computed on a field that was never
   converged. **VMFL045 died loudly at wall 0 s; this would produce a plausible
   number.** It is the silent version of the same defect, and it is the one to fear.
2. **`ddtSchemes { default Euler; }` — first order in time.** The MMS limb claims
   **spatial** order 2; a first-order temporal error must not contaminate the norm,
   so the MMS must either run to a steady residual stop or set
   `ddtSchemes { default steadyState; }`. For the **shedding** limb it is a separate
   concern in its own right: **a Strouhal ladder that refines only in space while
   the time scheme stays first-order Euler is refining one axis of a two-axis
   error.**
3. **No `fvOptions` file exists in either `system/` or `constant/`.** The MMS limb
   requires one for its `codedSource`. **So the MMS case is not a copy of the
   anchor; it is the anchor plus a new dictionary** — a regime-crossing
   configuration change by construction, which is precisely the situation §8.1
   describes.

And a fourth, harmless but diagnostic: `constant/turbulenceProperties` reads
`simulationType laminar`, yet the solvers block carries `"(U|k|omega)"` and the
relaxation block carries `k` and `omega`. **Extra keys — the inverse of VMFL045's
missing one, and harmless here.** It is positive evidence that this dictionary was
**inherited from a turbulent case rather than written for this one**, which is the
inheritance the supervisor asked to have named.

### 8.3 The two guards, and an honest statement of what each addresses

**Guard 1 — pre-flight smoke test.** One timestep on the coarsest mesh, in a scratch
directory **outside `verification/runs/`**, aborting on failure. Seconds of cost.
**It is a launch condition, never a gate: it decides whether the run starts, not
what the run means.** Scoped for **both** limbs, because they are two
configurations.

- **What it buys:** the VMFL045 class — a dictionary complete for one regime and
  incomplete for another, dying at timestep 0. It would catch gap 3 above and any
  missing solver key.
- **What it does NOT buy, stated because a guard oversold is worse than none:** it
  **cannot** catch gap 1. A missing `residualControl` does not throw; the run starts
  happily and one timestep succeeds. **A smoke test cannot detect a missing
  convergence criterion.** That gap is closed by an explicit launcher assertion that
  the steady case's `fvSolution` contains a `residualControl` block — not by a smoke
  test.

**Guard 2 — the launcher must REFUSE to start the solver when the mesh admission
gate fails.** F12's frozen `run_case` computes `mesh_gate` and launches anyway:
**20.5 s of solver wall went into a mesh already known inadmissible**, and F12 then
failed the gate at **all three levels**, with over-threshold face counts scaling
**×4.03 and ×4.00** — a fixed *fraction* of the mesh that refinement does not cure.

- **Which risk each addresses, as instructed:** **a smoke test would NOT have saved
  F12** — it died at iteration 180, not timestep 0 — **gate enforcement would
  have.** The two guards cover **disjoint** failure modes and neither substitutes
  for the other. F5a needs both.

**Guard 3 — the rule-4 existing-directory guard, MIRRORED and not reinvented.**
`verification/runs/F12_runs/run_f12_rung.py:66–70` refuses (`rc=3`) when any
registered run directory already exists, because `run_case()` `rmtree`s it and a
rung is fired exactly once. **F5a's launcher mirrors that code rather than inventing
a new guard.**

**Standing practice carried in, already settled and not re-derived:** a **failed run
tree is PRESERVED**, never cleared to make room for a nicer one. F12's logs are
gitignored, so the fatal-error text lives in `result.json`'s **`traceback`** field
and F5a's launcher must write the same field. And for an **interrupted** run the
actual/predicted ratio is stated **undefined, not `0.0×`** — cfd practice arrived at
independently in **C-50**, which calibrates the **rate** instead and writes no total
ratio.

### 8.4 A guard the mesh limb already half-owns

The anchor mesh carries **`constant/birth_certificate.json`** — `verdict "clean"`,
`cells 25200`, `max_non_orthogonality 4.436338e-06`, `max_skewness 0.01911846979`,
`hard_errors []`, provenance `retrospective-from-archived-log`. **The mechanism for
registering §3.4's three measured admission values per level already exists in this
lab and should be reused rather than re-invented:** mint a birth certificate at mesh
build time for each of L1, L2 and L3, register the three verdicts in the
pre-registration, and have the launcher refuse on any non-`clean` verdict. That is
Guard 2 made executable rather than promised.

---

## 9. AMENDMENT — RULING 7, AND WHAT IT DOES TO THIS PROPOSAL

*Added after verification's Ruling 7 reached this lane. Nothing above is rewritten;
where this section corrects an earlier claim it says so.*

### 9.1 The ruling, recorded

**A correlation scores `V` only as a KNOWN-ANSWER INSTRUMENT, on four conditions,
all required:**

1. a published **closed form with stated coefficients** — *a table of scattered
   points is not a correlation, and a curve the lab fitted itself is the data, not
   an instrument*;
2. the source **held and title-page verified**;
3. a **stated validity range covering the case's condition**;
4. **its own scatter quoted, with the gate band wider than it.**

It establishes **no observed order** and is **`V`'s weakest instrument by a wide
margin.**

**§4.3's scatter finding is vindicated: it is now the fourth condition of a standing
ruling.**

### 9.2 The MMS `V` limb is NOT proposed for compute

Two independent grounds, both accepted here:

1. **It is mis-costed and therefore unauthorisable.** §5.5 leaves it **UNCOSTED**,
   and under rule 12 nothing may be authorised on an uncosted item. **§5.5's refusal
   to guess is now load-bearing rather than merely careful.**
2. **An MMS buys no column the lab lacks.** `V` is already green on **7 of cfd's 82
   rows**, and the rubric's `V` is **binary** — an MMS scores the same green as a
   Hagen–Poiseuille comparison.

**What an MMS would buy is a capability, not a column:** no row in this lab joins a
known answer to a converging ladder — the exact-solution rows carry no triple, and
the one clean triple has no known answer. **Verification named that as a rubric
defect rather than a reason to spend, and it is on Sanaa's desk as a question about
whether `V` should be graded by the strength of its instrument. It is not this
team's to pre-empt.**

> **§2's MMS design is RETAINED as a description of what would be built if a
> capability argument is ever ruled admissible. It is NOT proposed for compute, and
> no core-minute is requested for it.** §5.3's **464.82–612.14 core-min is the G+P
> shedding limb** and was never the MMS limb; the supervisor upheld that costing and
> did not strike it to `UNCOSTED`.

### 9.3 Roshko as a `V` instrument already in hand — conditions 1 and 2 are MET

**Condition 1 — closed form with stated coefficients: MET**, and the paper carries
**two** such forms, not one. §1.2 established this and it now becomes load-bearing:

| form | coefficients | **stated validity range** |
|---|---|---|
| **(2a)** | `S = 0.212 (1 − 21.2/R)` | **50 < R < 150** |
| **(2b)** | `S = 0.212 (1 − 12.7/R)` | **300 < R < 2,000** |

**Condition 2 — held and title-page verified: MET.** 26,719,255 B on disk; page 1
**rendered and read** by this lane (§1.1). **No compute at all was required for
either condition.**

### 9.4 CONDITION 3 — the range analysis, and it corrects the brief's premise

**The brief states that "F5a spans Re 100–180 while the range clause stops at 150."
It does not, and the true position is worse, not milder.**

**Read from the registered record**, `verification/campaign/F5a_cylinder_reynolds_ladder.md`
line 3: *"Ladder: Re 1000 → 2000 → 3900 → 5000 → 10,000 → 1e5 → 1e6. Each rung must
pass its gate before the next starts."* **There is no Re 180 rung anywhere, and the
top of the ladder is Re 1e6, not 180.** (The string "Re 100" does occur at line 63,
but in prose about a laminar/turbulent methodology fork — *"Every rung from Re 100
through Re 2000 was run laminar"* — not in the registered rung list.)

| registered rung | inside **(2a)** `50 < R < 150` | inside **(2b)** `300 < R < 2,000` |
|---|---|---|
| Re 1,000 | **no** | **YES** |
| Re 2,000 | no | **no — exactly on the endpoint** |
| Re 3,900 | no | no |
| Re 5,000 | no | no |
| Re 10,000 | no | no |
| Re 1e5 | no | no |
| Re 1e6 | no | no |

- **ZERO of the seven registered rungs fall inside (2a) `50 < R < 150`** — the range
  §1.2 corrected the survey on.
- **Exactly ONE, Re 1,000, falls strictly inside (2b) `300 < R < 2,000`.**
- **Re 2,000 sits exactly on (2b)'s upper endpoint, and the clause is strict**
  (`300 < R < 2,000`). It is therefore **not strictly inside**. Stated as a boundary
  case rather than rounded in, because rounding a case into its reference's range is
  the same error as trimming the case to fit.

**And the ladder is NOT trimmed to fit.** The five rungs from Re 3,900 upward lie
outside both ranges by up to four orders of magnitude. Under condition 3 **Roshko
cannot be quoted as a `V` instrument for any of them.** That is a statement about
what the instrument covers, **not a reason to shorten the ladder** — choosing the
experiment to suit the answer is the failure this whole memo exists to avoid.

**The Re-100 asymmetry, stated plainly.** The F5a-MMS proposal's own rung (§4.1) is
**Re 100, which IS inside (2a)** — but **Re 100 is not a registered F5a rung.** It
exists on this box only as the filmed demo act, the demo three-level cache (§3.6)
and the §5.1 anchor. **The one Reynolds number at which Roshko (2a) is admissible is
the one the ladder does not register.**

### 9.5 CONDITION 4 — the scatter check, and the one admissible rung FAILS it

Condition 4 requires the gate band to be **wider than the correlation's own
scatter**. §4.3 measured that scatter off the render: **≈ ±4 % at R ≈ 100.**

**At Re 1,000 — the only rung where condition 3 is met:**

| | value |
|---|---|
| Roshko **(2b)** at R = 1,000 | **0.209308** |
| F5a measured `St` (`F5a_cylinder_reynolds_ladder.md`, Measured table) | **0.2343** |
| corroborating independent value (`R7_STROUHAL_SPACING_RESULTS.md`) | 0.2343330 |
| **deviation** | **+11.94 %** |

**+11.94 % against a ±4 % band is a miss by roughly threefold.** A band wide enough
to satisfy condition 4 is ±4 %; the measurement sits three times outside it. **Under
Ruling 7, the Re-1000 rung graded against Roshko (2b) is a `GATE FAIL`** — and by a
margin no condition-4-compliant band could absorb.

For completeness, and **explicitly NOT as gradeable claims** because condition 3
fails for both: Re 2,000 measured 0.2421 against (2b) 0.210654 → **+14.93 %**;
Re 3,900 corrected-spacing 0.1564 against (2b) 0.211310 → **−25.99 %**. **Diagnostics
that decide nothing.**

> **So Roshko as a free `V` instrument does not make the MMS limb redundant in the
> way the brief hoped. It makes it unnecessary for a different and worse reason: at
> the one rung where the instrument is admissible, the case FAILS against it.**

### 9.6 THE CHARTER CONTRADICTION — reported, and it is not the contradiction the brief describes

**Located.** `docs/charters/VERIFICATION_CHARTER.md`, **§6b** (*"A reference that was
never obtained is recorded in one vocabulary"*, heading at line **1661**), the row at
line **1712**, quoted:

> *"No paper was found, despite a genuine search … that reports a point value of Cd
> or St at exactly Re=2000"*, followed by a fallback to a secondary reproduced as a
> figure in a 2014 thesis | `demo-output/website/campaign/F5a_cylinder_reynolds_ladder.md:562-571`
> | **`NOT OBTAINED` as a primary.** What is held is SECONDARY, and the row is graded
> BANDED and LOWER CONFIDENCE, which is the right handling of the state under a
> different name

**Both readings named, as instructed:**

- **The brief's reading:** §6b records F5a's reference as `NOT OBTAINED` while the
  paper is demonstrably on disk, so two lab records disagree.
- **This lane's reading, and it is the one the text supports: THERE IS NO
  CONTRADICTION.** The row is scoped to *"a point value of Cd or St **at exactly
  Re = 2000**"*. **It makes no claim about Roshko, and no `NOT OBTAINED` row anywhere
  in that charter names Roshko or Report 1191** — checked by grep across the whole
  file. The source it cites names the papers actually searched — **Jiang & Cheng,
  Norberg, Williamson, and Fey/König/Eckelmann — and Roshko is not among them.**
  **Both records are true simultaneously:** Roshko is held, **and** no primary
  reporting a point `St` at exactly Re 2,000 was found. Indeed **Roshko could not
  have supplied that point either** — (2b)'s range clause is strict at 2,000 (§9.4).

**Not resolved here, and the charter is not this team's to edit.** The report is:
on the text as written the two records are **consistent**, and **if verification
intends that row to bear on Roshko it should say so explicitly, because as written
it does not.**

**A separate and real defect in that row, found while checking it: its citation path
is stale.** The row cites `demo-output/website/campaign/F5a_cylinder_reynolds_ladder.md:562-571`.
**That path does not exist.** A non-ignoring `find` locates exactly one copy of the
file, at **`verification/campaign/F5a_cylinder_reynolds_ladder.md`**, which is also
the only tracked copy at HEAD. **The line numbers 562–571 resolve correctly on the
real path** — lines 564–567 carry the quoted sentence — so **only the directory is
stale and the row's substance is intact.** Verification's file, verification's fix.

### 9.7 The OCR claim, checked — and at the load-bearing characters it is the other way round

Verification declined to score Roshko partly because *"the sidecar OCR is degraded at
exactly the load-bearing characters."* **Checked page by page against the sidecar,
and then against the renders:**

- **Sidecar page 13 — the page where equations (2a) and (2b) live — is CLEAN.** It
  reproduces `(2a) S=0.212 (1-21.2/R)` / `50<R < 150` and
  `(2b) S=0.212 (1-12.7/R)` / `300<R < 2,000` correctly.
- **Sidecar page 10 IS degraded**, rendering the same constant as `.0.212 (1_ 2~2)`.
  But page 10's occurrence is the **annotation drawn inside Figure 4**, not the
  equation block.

**So the degradation is real, and it is not at the coefficients — it is at a figure
annotation.** The equation block OCRs clean.

**And it decides nothing either way, because under rule 15 the render is the
authority and this lane rendered both pages** (§1.2, §1.3). Every coefficient and
both range clauses in this memo are read off the **image**. **A record that had
relied on the sidecar would have been right at page 13 and wrong at page 10 — which
is precisely why rule 15 exists.**

---

## 10. THE DECISION THIS MEMO PUTS TO THE SUPERVISOR

*Rewritten after Ruling 7 (§9). The pre-Ruling-7 ordering is superseded and the
change is stated rather than silently applied: **the `V` limb has left the proposal
entirely**, and what remains to decide is narrower.*

**What survives Ruling 7:** the case does not fall over on the fact the survey rested
it on — **Roshko is held, readable and title-page verified by an independent
render** — and **the `G+P` shedding limb's costing stands as built** (§5.3, upheld,
not struck to `UNCOSTED`).

**What has left the proposal:** **the MMS `V` limb is not proposed for compute**
(§9.2), on two independent grounds — it is uncosted and therefore unauthorisable
under rule 12, and it buys a binary column the lab already holds seven of.

**What Ruling 7 newly costs the proposal:** the free `V` instrument the brief hoped
would replace the MMS is **admissible at one registered rung and the case fails
against it there** (§9.4, §9.5).

**In priority order, and item 1 still decides everything:**

1. **Settle the `P` band question (§4.3) FIRST, at zero compute.** Ruling 7's fourth
   condition has now made this a standing test rather than this lane's observation.
   If Roshko's scattered points cannot support a band worth gating, **F5a-MMS buys
   `G` alone** — and F5a is then strictly worse value than **F3**, which already
   holds `V` and is **35.23 core-min** from `G` under a frozen, armed, unfired
   pre-registration. **That single zero-compute ruling decides whether this proposal
   is worth 465 core-minutes or worth nothing.**
2. **Rule on what §9.5 means for the existing ladder, which is a separate question
   from the proposal.** The Re-1000 rung's `+11.94 %` against Roshko (2b) is a
   `GATE FAIL` under Ruling 7 at any condition-4-compliant band. **That is a finding
   about a rung already run, not about a rung being proposed**, and it needs a
   verdict independent of whether F5a-MMS ever happens.
3. **If `P` survives item 1, close the one remaining open measurement before freezing
   anything:** the three `checkMesh` runs of §3.4. **The L1 MMS cost probe of §5.5 is
   no longer on the path**, because the limb it would have costed is no longer
   proposed.
4. **Only then write the pre-registration**, deriving every band and every plateau
   threshold from principle, and **declaring in its §2 that the medium level's
   settled `St` was already known** (§3.5.4).

**No compute should be authorised on the strength of this memo.** It fixes nothing,
it is not a pre-registration, and after §9 it requests **no core-minute for the `V`
limb at all.**

---

*Standing rules observed: rule 1 (verdict vocabulary, kept distinct from the tier
vocabulary) · rule 3 (planted-zero flagged as mandatory for the MMS reader) ·
rule 5 (plateau is clause (1), not a new gate) · rule 7 (nothing here is sent
anywhere) · rule 9 (the $25 pre-authorisation is not a ceiling) · rule 12 (cost
above, dollars derived not measured; **no calibration row is added — this dispatch
spent no core-minutes, per the cfd supervisor's standing ruling that rule 12's
calibration duty does not reach zero-compute work**) · rule 13 (no scratch path is
cited by this document) · rule 15 (title-page verification by render, twice) ·
rule 16 (silent background operation).*
