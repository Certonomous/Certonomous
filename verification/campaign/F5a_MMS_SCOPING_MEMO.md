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
12. **The absent Re-100 pre-registration.** No F5a pre-registration exists anywhere
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

## 8. THE DECISION THIS MEMO PUTS TO THE SUPERVISOR

**F5a-MMS is technically sound, cheaper to *verify* than to *validate*, and it does
not fall over on the fact the survey rested it on — Roshko is held, readable and
title-page verified by an independent render.**

**But it is not cheap, and its `P` limb is weaker than the survey believed.** In
priority order:

1. **Settle the `P` band question (§4.3) FIRST, at zero compute.** If Roshko's
   scattered points cannot support a band worth gating, **F5a-MMS buys `V` and `G`
   and no `P`, and it is then just a more expensive F3** — which already has `V` and
   is 35.23 core-min from `G`. **That single ruling decides whether this proposal is
   worth 465 core-minutes or worth nothing.**
2. **If `P` survives, close the two open measurements before freezing anything:**
   the three `checkMesh` runs (§3.4) and the L1 MMS cost probe (§5.5). Both are
   small, bounded and solver-free or nearly so.
3. **Only then write the pre-registration**, deriving every band and every plateau
   threshold from principle, and **declaring in its §2 that the medium level's
   settled `St` was already known** (§3.5.4).

**No compute should be authorised on the strength of this memo.** It fixes nothing
and it is not a pre-registration.

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
