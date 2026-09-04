# PRE-REGISTRATION — VMFL034: Particle Aggregation inside a Turbulent Stirred Tank

**DRAFT — NOT YET FROZEN. NOT FREEZE-READY (see `§14`).**
**BLOCKER A — THE BINDING PHYSICS BLOCKER — IS NOW RESOLVED (see `§5a`, added
2026-09-04T15:18Z):** β₀ = 1 (dimVolume/dimTime, m³/s) and the six feed moments
`(1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)` were read **independently from the
shipped archive** (`report.xml`, `.cas.h5`, `.set`) — NOT back-calculated from the
target — and corroborated by two kernel-free physics checks (m3 volume
conservation exact; the CMSMPR zeroth-moment relation predicts m0 = 0.1318 vs the
manual's analytical target 0.132, −0.17 %). Blocker C (velocity-group coupling) is
also resolved: OpenFOAM's `velocityGroup` gives every size class one shared phase
velocity. **BLOCKER B IS NOW RESOLVED — the case and comparator EXIST and are built,
smoke-verified and untracked (`§B`, appended 2026-09-04T15:50Z).** `§B` returned two findings and the
supervisor RULED on both (`§C`, **Rulings A–D, applied 2026-09-04T16:02Z**):
(A) the kernel input is **β₀_OF = β₀_ref/α₂** — a declared unit conversion from the
α₂-scaled OF number density, source-verified (`§B.5`, `§C.A`); **= 2000 at the
rescaled operating point;** (B) because setting Da sets m0, **m0 is DEMOTED to a
calibration limb** and the gate is **m1, m2, m3, m4, m5** (`§C.B`); (C) the literal
run is infeasible (~10,050 core-h triple), so a **similarity rescale** (walls
6.0/6.06 m/s, inlet 0.10 m/s, τ=5 s, β₀=2000; Da and the six feed moments preserved
EXACTLY) is permitted with a **measured well-mixedness gate** the comparator enforces
(`§C.C`); (D) **α₂ pinned at 1e-2 and defended** (`§C.D`). Cost re-filed at ~35 core-h
triple (`§C.E`). Solver corrected to **`reactingTwoPhaseEulerFoam`** (`§13` superseded).
**Remaining freeze blocker: E (nothing committed / no queue row) — the supervisor's
act.** Well-mixedness is a run-time refusal gate, not a pre-freeze blocker.
Drafted by `ansys-lane-opus48` 2026-09-04 (`date -u` in the drafting invocation:
`Fri Sep  4 01:25:41 UTC 2026`); Blocker-A resolution appended by `ansys-lane-opus48`
in a later 2026-09-04 invocation. The supervisor performs `SUPERVISION_CHARTER` §3
check 4 and freezes; **this lane has frozen nothing, committed nothing, run no
solver, and touched no archive copy** (the archive was extracted to a scratch
directory outside the repository and deleted after reading — `§5a`). Everything
runnable is untracked.

The supervisor's rulings of 2026-09-04 are cited where they bind: `§12.2` for
this case **RULED `SAME` and PASS-capable** (message `affe9dd93ab43580b`,
reproduced at `§3`); and the two things the supervisor declined to accept at face
value — the frozen-flow equivalence (`§3a`) and the softness of the cost bracket
(`§12.4`) — are addressed where flagged.

---

## §0. CLEAN-SLATE ASSERTION (CLAUDE.md rule 2 — the condition, and how it was checked)

**NOT YET RUN. NO VMFL034 SOLVER HAS EVER STARTED, ANYWHERE ON THIS BOX.** Every
band, ceiling, cap, criterion and label below was fixed with no VMFL034 number in
existence. Checked in the drafting invocation, 2026-09-04T01:25:41Z:

| condition | check | result |
|---|---|---|
| the run root does not exist | `test -e verification/runs/ansys_verification/VMFL034` | **RUN ABSENT** |
| no VMFL034 artefact exists anywhere under the repository | `find . -iname '*VMFL034*' -not -path './.git/*'` | **0 hits** |
| the register carries no VMFL034 row | `grep -c VMFL034 verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | **0** |
| the case directory was empty at draft time | `git status --porcelain cases/ansys_verification/VMFL034` | **empty (dir just created, untracked)** |

Before first compute, amendments to this file are legal and must state the
condition and how it was checked, naming the run directory
`verification/runs/ansys_verification/VMFL034/` that **does not exist**. After
first compute, dated addenda only, which cannot alter a gate, threshold, cap or
label (`VERIFICATION_CHARTER` §2b/§2d, `CLAUDE.md` rule 2).

---

## §1. SOURCE — VERIFIED AGAINST THE PDF, NOT THE SIDECAR (CLAUDE.md rule 15)

Ansys Fluid Dynamics Verification Manual, Release 2026 R1. **Printed page 121**
(Overview, Test Case, Figure .34.1, material/geometry/BC table) **and printed
page 122** (journal file, Table .34.1 — the target table). Located in the PDF at
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.pdf`,
**PDF page 135 = printed page 121** and **PDF page 136 = printed page 122**,
verified by `pdftotext -f 135 -l 135` (carries *"VMFL034: Particle Aggregation
inside a Turbulent Stirred Tank"*) and `pdftotext -f 136 -l 136` (carries
*"Table .34.1"* and every target row). **The six targets were read from the PDF,
not only the sidecar** — a table is not a title page (`§25.5` spirit).

**Manual-stated case data, quoted and PDF-verified:**

| item | manual value | source line |
|---|---|---|
| reference | B. Wan, T.A. Ring, K. Dhanasekharan, J. Sanyal, *"Comparison of Analytical Solutions for CMSMPR Crystallizer with QMOM Population Balance Modeling in Ansys Fluent"*, China Particuology **Vol. 3, pp. 213–218, 2005** | Overview |
| solver (reference) | **Ansys Fluent** | Overview |
| physics/models | Multi-phase, **QMOM** population balance model, turbulent flow; **standard k-ε**; "The flow is turbulent, steady, and incompressible … Moments are solved on a frozen flow field." | Test Case (PDF p135 states *"Multi-phase, with QMOM population balance"* — the reference method is QMOM by name) |
| geometry | **square box side = 0.1 m**; **inlet/outlet openings = 0.02 m** | Geometry column |
| fluid | water, ρ = **998.2 kg/m³**, μ = **0.00103 kg/m-s** | Material Properties |
| BCs | **top wall 101 m/s**, **bottom wall 100 m/s** (both toward the outlet), **inlet velocity 0.005 m/s**, **outlet gauge pressure 0 Pa** | BC column |

**Target table (Table .34.1), quoted in full and PDF-verified:**

| Moment | **Target (analytical)** | Ansys Fluent | Ratio (manual) |
|---|---|---|---|
| m0 | **0.132** | 0.132 | 1.000 |
| m1 | **0.225** | 0.226 | 1.004 |
| m2 | **0.547** | 0.548 | 1.002 |
| m3 | **1.910** | 1.910 | 1.000 |
| m4 | **9.073** | 9.133 | 1.007 |
| m5 | **53.797** | 53.816 | 1.000 |

The manual's own caption: *"moment of PBE for Ansys Fluent turbulent simulations
is compared with analytical solution for aggregation alone at the outlet of the
tank"*, and the Test Case: *"compared to a steady state analytical solution for
the population balance in a stirred tank where aggregation takes place."* **The
Target column is therefore the ANALYTICAL solution, and it is the gate reference.
The Ansys Fluent column is quoted for context and is NOT the gate** (`§5` step 1).

**Fluent's own QMOM discretisation error against the analytical target (recorded
for `§4.3`'s sanity check, not used to derive the band):** worst is **m4 at
+0.661 %** ((9.133−9.073)/9.073); then m1 +0.44 %, m2 +0.18 %, m5 +0.035 %, m0
and m3 exact to the printed digits.

---

## §2. THE STRUCTURAL READING THAT GOVERNS THIS REGISTRATION

Two facts, both from the manual and both decisive below.

**(i) The reference is the EXACT solution of the SAME continuum model the solver
discretises.** The Target column is the steady-state analytical solution of the
aggregation population-balance equation (PBE) with a constant (size-independent)
kernel in a CMSMPR (continuous stirred, mixed-suspension mixed-product-removal)
tank — the classic Hulburt–Katz / Randolph–Larson moment closure. Fluent reaches
it by **QMOM** (6 moments); this lab will reach it by a **sectional (class)
method** — the only population-balance discretisation OpenFOAM v2606 carries
(`§13`). Both discretise the identical PBE. **This is a discretisation-vs-exact
comparison, not a code-to-code comparison** (`§3`).

**(ii) The moments span two-and-a-half orders of magnitude and the higher moments
are the discriminating ones.** m0 = 0.132 to m5 = 53.797; m5/m0 = 407. The higher
moments (m4, m5) are dominated by the largest aggregates and are the most
sensitive to the sectional size-range and class count — they are simultaneously
the **most informative** about aggregation and the **hardest to converge**. This
is the whole reason `§7`'s Roache triple refines the SIZE GROUPS, and the reason
`§4.3`'s band is relative, not absolute.

---

## §3. `§12.2` MODEL-SAMENESS — RULED **`SAME`** BY THE SUPERVISOR. THE CASE IS **PASS-CAPABLE**.

The supervisor ruled this on 2026-09-04 (message `affe9dd93ab43580b`), adopting
and strengthening this lane's argument. Reproduced in `§12.2`'s four required
parts so the ruling stands on the face of the frozen document:

**(1) The continuum model our solver discretises.** The aggregation population
balance equation for the number density `n(L, x)` of a dilute dispersed particle
phase, transported on a steady turbulent incompressible flow field, with a
**constant aggregation kernel** and **no breakage, no nucleation, no growth**
(`§5` confirms all three are off in the archive), in a CMSMPR configuration
(one inlet feed, one product outlet, mean residence time τ). Solver: OpenFOAM
v2606's sectional population-balance model (`libpopulationBalance.so`), with
`constantCoalescence` as the aggregation kernel.

**(2) The model the manual's reference is the exact solution of.** The identical
aggregation PBE with a constant kernel in a CMSMPR — its steady-state **analytical
moment solution** (`§1`, `§2`(i)).

**(3) SAME or DIFFERENT: `SAME`.** The supervisor's words: *"the manual's Target
column is the analytical solution of the aggregation PBE with a constant kernel,
and both QMOM and a sectional method are discretisations of THAT SAME continuum
equation. We are therefore comparing our discretisation of the PBE against the
exact solution of the PBE — which is a cleaner verification setup than a
code-to-code comparison, not a weaker one. §12.2's test is sameness of MODEL,
never exactness of algebra. `SAME`. Not capped."* **QMOM vs sectional is a
difference of discretisation, not of model.**

**(4) The moments are recovered by summation, and that recovery is exact.** The
gated quantities are the first six moments. A sectional solution stores the number
(or volume) in each size class `i` at representative size `L_i`; the moment of
order `k` is `m_k = Σ_i N_i L_i^k`, a finite exact sum with no closure
assumption. **The comparator computes the moments this way and the planted
control (`§10`) fires on that reader**, so the moment-recovery path is itself
verified before any grading.

> **CEILING: `PASS`.** `GATE FAIL`, `NOT A RESULT` and `BLOCKED` remain fully
> available. This is one of the very few never-run Fluent cases whose reference is
> the exact solution of the same PDE the lab's solver discretises, which is why
> the supervisor named it *"this team's most promising never-run case."*

**The one honest limit on the SAME ruling, budgeted not disqualifying.** A
sectional method's moment accuracy is bounded by the size-class range and count; a
too-narrow range truncates the largest aggregates and makes m4/m5 undershoot. This
is a **discretisation** error, bounded by the Roache size-group triple (`§7`), not
a model-form difference — exactly the treatment `Amendment 1.4 CLAUSE A` gives the
wedge bias. If the size-group triple is not `CONVERGING` on a moment, that moment
grades `NOT A RESULT` under rule 5, whatever its value.

---

## §3a. THE DECLARED DEPARTURE — WE RUN COUPLED TO STEADY STATE; THE MANUAL FREEZES THE FLOW. DEFENDED QUANTITATIVELY.

**Supervisor ruling of 2026-09-04, adopted:** *"this must be DECLARED AND DEFENDED
in the pre-registration as a named departure, with a quantitative dilution
argument … OR the frozen-field behaviour must be reproduced."* Declared here, and
defended.

**The manual's procedure (journal file, PDF p136, quoted):** solve flow + k-ε for
**700 iterations** with all moments off; then **freeze the flow** (`solve set
equations mixture flow no ke no mp no`), turn the six moments on, patch phase-2 to
`mp 1e-06`, and iterate the moments alone (200 + 2000 iterations). The moments are
transported on a flow field held fixed.

**Our departure:** OpenFOAM v2606 has no standalone "PBE-on-a-frozen-field"
solver; its population balance is embedded in the Euler–Euler phase-system solve.
We therefore run the **fully coupled** solver to steady state and read the moments
there.

**Why the two give the same steady moments — a MEASURED argument, from the archive
bytes, not an assumption:**

1. **The dispersed phase is dilute by construction.** The manual patches the
   phase-2 volume fraction to **`mp = 1e-06`** (journal file). The two-way
   momentum back-coupling term (drag on the continuous phase) scales with the
   dispersed volume fraction, so it is `O(1e-06)` of the continuous-phase
   momentum — negligible.
2. **The drag closure uses a CONSTANT diameter that does not depend on the
   aggregation state.** Read from the archived `.cas.h5` (`§5`): phase-2 carries
   `(diameter (constant . 1e-05))` and drag `schiller-naumann` on that fixed
   diameter. **The flow field therefore does not depend on the moments at all** —
   even the drag does not see the evolving size distribution. The moments ride the
   flow as a passive (aggregating) scalar field.
3. **Consequence.** Because the flow field is independent of the moments (dilute +
   fixed drag diameter), the coupled steady solution's flow field is identical to
   the frozen field, and the moments computed on it are identical to the
   frozen-flow moments. **The departure is exact in the dilute-constant-drag
   limit the archive fixes**, not merely "probably negligible."

**The residual OpenFOAM-implementation risk, named (Blocker C, `§14`):** OpenFOAM's
`velocityGroup`/`sizeGroup` machinery can assign each size class its own velocity,
which would re-introduce a size-dependence into transport. **The setup must use a
single shared velocity group (or the dilute passive limit)** so the size classes
share the phase velocity and the argument above holds. This is a setup obligation,
verified in the pre-flight smoke (`§14`), not a gate question.

---

## §4. THE GATE

### §4.1 The quantity

The six moments of the particle-size distribution **at the outlet**, `m_0 … m_5`,
recovered from the converged sectional solution by `m_k = Σ_i N_i L_i^k` over the
size classes, area-averaged over the outlet patch — the same quantity and location
the manual reports (*"moments … at the outlet of the tank"*, `report
population-balance moments outlet () () 6`).

### §4.2 The six limbs and the band

All six moments are **PRIMARY**. The band is **relative and uniform**, derived at
`§4.3`.

| limb | moment | reference target (analytical) | band (relative) | band (absolute) |
|---|---|---|---|---|
| **A** | m0 | 0.132 | **± 0.76 %** | ± 0.00100 |
| **B** | m1 | 0.225 | **± 0.76 %** | ± 0.00171 |
| **C** | m2 | 0.547 | **± 0.76 %** | ± 0.00416 |
| **D** | m3 | 1.910 | **± 0.76 %** | ± 0.01452 |
| **E** | m4 | 9.073 | **± 0.76 %** | ± 0.06895 |
| **F** | m5 | 53.797 | **± 0.76 %** | ± 0.40886 |

### §4.3 The band's derivation — stated as a rule, fixed before compute, yielding whatever it yields

**The band is RELATIVE and UNIFORM across the six moments, and here is the
argument the supervisor required for that** (its ruling: *"the bands cannot be
uniform across m0..m5 without an argument … If a per-moment band is not defensible,
say so and use a relative band with its justification"*):

- **Why relative, not absolute.** The moments span 0.132 to 53.797. An absolute
  band that suits m0 (±0.001 would be ±0.76 % of m0) is 0.0000019 % of m5 —
  unmeetable; an absolute band that suits m5 is meaningless for m0. A set of
  moments of different order is compared in **relative** terms. (This is the point
  of departure from VMFL024, whose three targets were all the same order and took
  an absolute band.)

- **Why uniform.** The reference is a **single analytical computation** printed to
  a uniform absolute precision of 3 decimals (half-digit quantisation ±0.0005).
  That gives a per-moment *relative* quantisation ranging from **±0.379 % (m0)**
  down to **±0.00093 % (m5)**. **It is not defensible to claim the same
  computation knows m5 four hundred times better, in relative terms, than it knows
  m0**, merely because m5 is a larger number. The honest relative precision of the
  computation is set by its **least-well-resolved moment, m0, at ±0.379 %**, and
  that is taken as the uniform reference precision `q`.

- **The rule, `tol = q + d`, both relative:**
  - **`q = 0.379 %`** — the reference's honest uniform relative quantisation
    (max over the six of half-a-printed-digit ÷ target = 0.0005/0.132).
  - **`d = 0.379 %`** — the numerical allowance, fixed by the charter rule
    *"the numerical allowance is set equal to, and never larger than, the
    reference's own quantisation"* (VMFL024 `§4.3`). This keeps the numerical
    allowance from ever dominating the gate.
  - **`tol = q + d = 0.758 %`, stated as ± 0.76 % relative on every moment.**

**THE BAND WAS NOT FITTED TO PASS, AND HERE IS THE PROOF.** The band is derived
wholly from the reference's own quantisation; **no VMFL034 number exists** (`§0`),
and the Ansys Fluent column was not used to size it. As an independent **sanity
check** (not the derivation): Fluent's own QMOM — a *peer discretisation* of the
identical PBE — lands worst at **+0.661 % on m4**, which is inside ±0.76 %. So the
band admits a competent discretisation without being loose, and it does so by
arithmetic, not by choice. A sectional method with a truncated size range that
undershoots m5 by, say, 3 % returns a clean `GATE FAIL` on limb F — the band is
exposed to failure.

### §4.4 The verdict rule

1. Strict completion (`§9`) fails on any graded run → **`NOT A RESULT`**.
2. Steady-convergence criterion (`§8`) fails → **`NOT A RESULT`**.
3. Planted control (`§10`) does not fire → **`NOT A RESULT`** (no number produced).
4. Size-group Roache triple (`§7`) not `CONVERGING` on a moment → that moment
   **`NOT A RESULT`**; if any of the six is `NOT A RESULT` the case verdict is
   **`NOT A RESULT`** (rule 5; the gate can only turn PASS/GATE FAIL into NOT A
   RESULT, never the reverse).
5. Otherwise, on the `CONVERGING`, converged finest-level values: **all six**
   inside ±0.76 % → **`PASS`** (GCI printed per moment); **any** outside →
   **`GATE FAIL`** (the offending moments and their GCI printed).

Every verdict prints, beside it: all six recovered moments, all six targets, the
±0.76 % band, the per-moment size-group triple classification and GCI, `§2`(ii)'s
note that m4/m5 carry the discretisation risk, `§3a`'s departure, and the cost.

---

## §5. THE SETUP INPUTS — MANUAL vs ARCHIVE, EACH WITH ITS PROVENANCE

**The manual UNDER-SPECIFIES the case.** It gives geometry, fluid, wall/inlet BCs
and the target moments, but states **no aggregation-kernel constant, no size
range, no feed/initial moment distribution, and no size-class count.** `§2` (the
charter) permits reading the shipped archive **for setup and reference numbers
only**; nothing in either VM2026R1 copy was written, moved, renamed, deleted or
git-added, and the `.cas.h5` was extracted to a scratch directory outside the
repository and **deleted after reading** (it carries proprietary Ansys content).

**Archive path:**
`/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/VMFL034_WB.wbpz`,
member `VMFL034_WB_1_files/import_files/VMFL034_aggregation.cas.h5` (a Fluent
Scheme-encoded settings blob inside HDF5, readable via `strings` without Fluent).

| datum | value | provenance | usable? |
|---|---|---|---|
| box side | 0.1 m | **manual** (Geometry) | yes |
| inlet/outlet opening | 0.02 m | **manual** | yes |
| top/bottom wall velocity | 101 / 100 m/s toward outlet | **manual** | yes |
| inlet velocity | 0.005 m/s | **manual** | yes |
| outlet | gauge p = 0 Pa | **manual** | yes |
| water ρ / μ | 998.2 / 0.00103 | **manual** | yes |
| turbulence | standard k-ε | **manual** | yes |
| **mean residence time τ** | **100 s** | **manual formula + arithmetic** (see below) | yes |
| population-balance method (reference) | **QMOM, 6 moments** (`pb-qmom/n-pb-qmom 6`) | archive | context (ours is sectional) |
| zones | `velocity-inlet inlet`, `pressure-outlet outlet`, walls `sidewall`/`bottomwall`/`topwall` | archive | yes — confirms manual BC layout |
| both phases | material `water-liquid`; phase-2 dispersed | archive | yes |
| phase-2 drag diameter | **constant 1e-05 m** (`(diameter (constant . 1e-05))`) | archive | yes — load-bearing for `§3a` |
| phase-2 volume fraction | patched **1e-06** | **manual journal** + archive | yes — load-bearing for `§3a` |
| drag / slip | schiller-naumann / manninen-et-al | archive | yes |
| aggregation active, breakage OFF, nucleation OFF | `aggregation-pb`; `pb/breakage-freq-rate 0`, `breakage-kernel (none)`, `nucleation-kernel (none)` | archive | yes — confirms **aggregation alone** |
| **aggregation-kernel constant β₀** | **`1` (dimVolume/dimTime = m³/s)** — `pb/coalescence-rate 1` × `pb/aggregation-rate-factor 1.` in the ASCII `.set`; aggregation phenomenon ON (`pb/phenomenon (#f #f #t #f)`), breakage/nucleation/growth OFF | archive (`.set`), corroborated by physics (`§5a`) | **YES — RESOLVED (`§5a`)** |
| **feed / initial (inlet) moment distribution** | **m0..m5 feed = `(1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)`** — read from `report.xml` (inlet phase-2 constant profiles) AND independently from `.cas.h5` (`pb-qmom ((constant . 1) … (constant . 4.4229999))`), flags `pb-qmom-bc 1 1 1 1 1 1`; outlet BC moments all 0 (backflow) | archive (`report.xml` + `.cas.h5`, two files agree) | **YES — RESOLVED (`§5a`)** |
| **size range (min/max diameter) and class count** | the reference method is **QMOM**, which tracks 3 abscissas + 3 weights (no bins); there is no reference "size range". The sectional `[L_min, L_max]` and `N_g` are OURS to choose (feed abscissas are O(1), see `§5a`); this is a **discretisation choice bounded by `§7`'s triple**, not a missing physics datum | not applicable to QMOM reference | **DISCRETISATION CHOICE (`§7`), not a blocker** |

**Residence time τ, computed from the manual's own stated formula** (*"the mean
residence time to be calculated from the inlet flow rate (velocity × inlet area)
and the volume (box area × unit depth)"*): with box area `0.1 × 0.1 = 0.01 m²`,
unit depth `1 m` → V = `0.01 m³`; inlet area `0.02 × 1 = 0.02 m²`, inlet velocity
`0.005 m/s` → Q = `1.0e-04 m³/s`; **τ = V/Q = 0.01 / 1.0e-04 = 100 s.** Provenance:
**manual formula + arithmetic**, re-derivable by any second party.

**A NOTE ON WHY β₀ IS NOT BACKED OUT OF THE TARGET, AND WHY IT DID NOT NEED TO
BE.** The constant-kernel CMSMPR analytical solution closes the steady zeroth
moment as `(m0_feed − m0)/τ = ½·β₀·m0²`; given τ and the target m0, β₀ *could* be
inverted. **That inversion route is rejected as circular** and IS NOT USED:
recovering the kernel from the reference moment and then using it to reproduce that
same moment would make the case's `PASS` self-fulfilling. **It did not need to be
used:** β₀ = 1 was read *directly and independently* from the shipped archive's
ASCII settings (`pb/coalescence-rate 1`, `§5a`), i.e. from the case-as-shipped, not
from the target. The zeroth-moment relation is then run **forward as an a-priori
prediction** (β₀=1 → m0 = 0.1318), and its agreement with the manual's analytical
target 0.132 (−0.17 %) is used only as **corroboration** that the archive value is
right and that the target is the constant-kernel analytical solution it claims to
be — never as the source of β₀. See `§5a`.

---

## §5a. BLOCKER A RESOLVED — β₀ AND THE FEED MOMENTS, WITH PROVENANCE PER VALUE (appended 2026-09-04)

**How the archive was read (and why the earlier `strings` read was ambiguous).**
The `.wbpz` was unzipped to a scratch directory outside the repository; nothing in
either VM2026R1 copy was written, moved, renamed, deleted or git-added, and the
extract was deleted after reading (proprietary Ansys content). The earlier attempt
read only the HDF5 `.cas.h5` with `strings` and hit defaults-mixed-with-active
ambiguity. This attempt found that the archive also ships **three plain-ASCII
members** that carry the settings unambiguously, so no HDF5 parser was needed
(`h5ls`/`h5dump`/`h5py` are all absent on this box — a separate finding):

- `…/dp0/FLU/Fluent/VMFL034_aggregation.set` — the full Scheme settings, ASCII.
- `…/progress_files/dp0/FLU/Fluent/report.xml` — the Fluent solver report, ASCII.
- `…/dp0/FLU/Fluent/VMFL034_moments2.pbm` — the outlet moments of the shipped run.

### §5a.1 The values, each with its provenance

| datum | value | source (independent of the target) |
|---|---|---|
| **β₀ (constant coalescence rate)** | **1** | `.set`: `(pb/coalescence-rate 1)` × `(pb/aggregation-rate-factor 1.)` |
| aggregation ON, growth/nucleation/breakage OFF | `(#f #f #t #f)` = (nucl,growth,**aggr**,break) | `.set`: `(pb/phenomenon (#f #f #t #f))`; `(pb/breakage-freq-rate 0)`, `(pb/nucleation-rate 1.4e-45)`; growth-rate 0.01 present but its phenomenon flag is #f (inactive) |
| **feed (inlet) moments m0..m5** | **1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999** | `report.xml` inlet phase-2 `((constant . 1) … (constant . 4.4229999))` **and** `.cas.h5` `(pb-qmom ((constant . 1) …))` — two files agree exactly |
| feed moments all active at inlet | flags `1 1 1 1 1 1` | `report.xml` `(1 1 1 1 1 1)`; `.cas.h5` `(pb-qmom-bc 1 1 1 1 1 1)` |
| outlet BC moments (backflow) | all 0 | `report.xml` / `.cas.h5` `(pb-qmom-bc 0 0 0 0 0 0)` |
| reference method | QMOM, frozen flow | `report.xml` SolverSettings (Flow/VF/Turbulence = no; Moment-0..5 = yes); `(pb/sg-pb-qmom? #t)` |
| shipped-run outlet moments (context, NOT the gate) | 0.13327, 0.22714, 0.54997, 1.90986, 9.09953, 53.65759 | `.pbm` — a re-run, near the manual's Fluent column |

**β₀ units.** OpenFOAM's `constantCoalescence` declares its constant as
`rate_("rate", dimVolume/dimTime, dict)` — dimensions **m³/s** `[0 3 -1 0 0 0 0]`
(volume per time per particle pair). This is the same physical dimension the
CMSMPR zeroth-moment relation requires (`§5a.2`), and β₀ = 1 works in that relation
with the case's nominal moment values — so **β₀ = 1 m³/s** is the value to set, with
the code-convention factor (below) to be pinned in the smoke.

### §5a.2 The moment algebra (Route 2) — the derivation, not just its conclusion

Population balance for number density `n(V)` (particle-volume coordinate) with a
**constant** aggregation kernel β₀ in a CMSMPR (perfectly mixed; feed `n_in`,
product removal at rate `1/τ`), at steady state:

`(n_in(V) − n(V))/τ + ½β₀∫₀^V n(V−V')n(V')dV' − β₀ n(V)∫₀^∞ n(V')dV' = 0`

Take volume-moments `M_j = ∫V^j n dV`. The aggregation source for `M_j` is
`½β₀∫∫[(V+V')^j − V^j − V'^j] n(V)n(V') dV dV'`:

- **j = 0:** `(V+V')^0 − 1 − 1 = −1` → source `= −½β₀M0²`. So
  **`(M0_feed − M0)/τ = ½β₀M0²`** — closes in `M0, β₀, τ` alone, **independent of
  the distribution's shape.** (This is the number balance: aggregation destroys one
  particle per event, hence the ½.)
- **j = 1:** `(V+V') − V − V' = 0` → source `= 0`. So **`M1 = M1_feed`: total
  particle volume is CONSERVED**, kernel-free and shape-free.
- **j ≥ 2 (integer):** `(V+V')^j` expands binomially into products `M_a M_{j−a}`, so
  integer volume-moments close but grow.

**Mapping to the manual's DIAMETER moments** `m_k = ∫L^k n dL`. With `V = k_v L³`
(`k_v = π/6` for spheres), `n(L)dL = n(V)dV` and `L^k = (V/k_v)^{k/3}`, so
`m_k = k_v^{−k/3} M_{k/3}`. Hence:

| manual moment | = volume-moment of order | closes under constant kernel? |
|---|---|---|
| **m0** | M0 (number) | **YES — fixes/validates β₀** |
| m1 | M_{1/3} (fractional) | no — needs feed shape → genuine prediction |
| m2 | M_{2/3} (fractional) | no — genuine prediction |
| **m3** | M1 (volume) | **YES — CONSERVED, `m3 = m3_feed`** |
| m4 | M_{4/3} (fractional) | no — genuine prediction |
| m5 | M_{5/3} (fractional) | no — genuine prediction |

Fractional volume-moments do **not** close for a constant kernel (`(V+V')^{p}`
with non-integer `p` is not a finite sum of moment products), so **m1, m2, m4, m5
depend on the full feed shape and are genuine predictions of the solve**; only m0
and m3 have closed analytic relations.

### §5a.3 The two kernel-free / a-priori checks (corroboration, not derivation)

1. **m3 conservation (kernel-free, shape-free).** `m3_feed = 1.91` (archive) equals
   the manual's analytical target `m3 = 1.910` **exactly**, and the shipped `.pbm`
   outlet `m3 = 1.90986`. Total volume is conserved as the algebra requires. This is
   a datum the manual gives for free and it confirms the feed's volume moment.
2. **m0 forward prediction (fixes nothing — checks everything).** With β₀ = 1
   (archive), τ = 100 s (manual geometry: `V/Q = 0.01/1e-4`, arithmetic verified),
   m0_feed = 1 (archive): `50·m0² + m0 − 1 = 0` → **m0 = 0.13177**. Manual analytical
   target m0 = 0.132 (**−0.17 %**); shipped `.pbm` m0 = 0.13327 (the +1 % is the
   well-mixed-ODE vs actual-2D-turbulent-CFD gap, expected). This simultaneously
   confirms (a) β₀ = 1 is the right archive value, (b) the manual's "analytical"
   Target column IS the constant-kernel CMSMPR analytical solution, and (c) the
   moment normalisation (m0_feed = 1) is self-consistent.

Feed-moment validity: the sequence `(1, 1.108, 1.39, 1.91, 2.821, 4.423)` has
Hankel determinants `det H2 = 0.162 > 0`, `det H3 = 0.00749 > 0` (eigenvalues
`0.0058, 0.262, 4.943`), so it is a valid moment sequence and a 3-node quadrature
(Fluent's QMOM feed representation) exists — the feed can be reconstructed for the
sectional method.

### §5a.4 DETERMINACY — how many unknowns remain, stated without papering

**Physics inputs: ZERO unknowns remain.** β₀ (=1), τ (=100 s), and all six feed
moments are now fixed from archive+manual, none from the target. The case is fully
specified.

**One residual MODELLING choice, named honestly (not a missing datum):** the
sectional method needs a feed *distribution* `n(L)`, not merely its six moments,
and because m1/m2/m4/m5 do not close, the outlet values depend on the feed shape
beyond those six moments. The reference (QMOM) represents the feed as three
weighted deltas from the six moments; the defensible sectional counterpart is a
feed whose first six diameter-moments reproduce the six archive values, on a grid
fine enough that the reconstruction is not rate-limiting. The residual
non-uniqueness of "a distribution with these six moments" is a **discretisation /
moment-inversion risk bounded by `§7`'s size-group triple**, resolved at setup
(Blocker B), and it does **not** re-open Blocker A.

### §5a.5 THE CIRCULARITY RULING — proposed, with the argument both ways (`§18`)

The design is **1 calibration + 5 genuine predictions**, NOT a 6-parameter fit to 6
targets — but note the calibration is not even needed here, because β₀ came from the
archive, so it is closer to **6 genuine predictions with an independent a-priori
consistency check on m0/m3**. The question `§18` forces: may a gate consume one of
its own reference targets (m0) as an input and still gate the other five?

- **Argument that it is illegitimate.** If β₀ were fitted to m0, then m0's limb
  would be tautological — it would `PASS` by construction, and reporting it as a
  passed limb would overstate the evidence. `§18` requires a lab-generated
  reference to name its independent path; a target consumed as an input is not
  independent of the prediction that reproduces it.
- **Argument that it is legitimate (and the actual situation here).** β₀ is **not**
  fitted to m0 — it is read from the shipped archive, independently of every target
  (`§5a.1`). The m0 relation is run **forward** as a prediction and merely
  *agrees* with the target; nothing about the gate consumed a target. m3 is a
  conservation identity, independent of β₀ entirely. So all six limbs remain genuine
  discretisation-vs-analytic comparisons: none was used to set an input.
- **Recommendation (the supervisor rules).** Gate all six as PRIMARY (as `§4`
  already does), because β₀ and the feed came from the archive, not the target. As a
  disclosure, mark in the register that **m0 and m3 additionally admit a closed
  analytic prediction** (m0 = 0.1318 forward; m3 = m3_feed conserved) that was
  computed a-priori and matched — this is corroboration of the reference, earning no
  PASS on its own (`§16`, `§33.2`), and it is exactly the `§18` "independent path"
  named for the two closed limbs. **If the supervisor prefers the conservative
  reading**, m0 may instead be demoted to a SECONDARY/disclosed limb (since its
  closed relation involves β₀), leaving m1,m2,m3,m4,m5 as the primary gate; this
  lane recommends against it, because β₀'s independence from the target makes the
  demotion unnecessary.

---

## §6. THE FLOW REGIME — recorded for `§11`, not a gate

- Reynolds number on the wall-driven flow: `Re = ρ U L / μ = 998.2 × 100 × 0.1 /
  0.00103 ≈ 9.7e6` — strongly turbulent, consistent with the manual's standard
  k-ε and its "The flow is turbulent" statement. The 100 m/s wall speeds are a
  synthetic device to generate turbulence in a 0.1 m water box; this is a
  verification abstraction, not a physical stirred tank, and nothing here depends
  on its physicality.
- The flow is **steady** (manual), so the OpenFOAM run is driven to a steady state
  (residual plateau + moment plateau, `§8`), not a fixed physical time.
- Because the flow is decoupled from the moments (`§3a`), the flow may be
  pre-converged first (700-iteration analogue) and the moments then driven to
  their own plateau on it — but a single coupled run to joint steady state is
  equivalent and is the registered path.

---

## §7. THE ROACHE TRIPLE REFINES THE **SIZE GROUPS** — the statement rule 5 requires, made up front

> **THE GATED QUANTITIES' DOMINANT AND MOST WORRYING DISCRETISATION ERROR IS
> SIZE-GROUP TRUNCATION, NOT SPATIAL MESH. THE ROACHE TRIPLE THEREFORE REFINES THE
> NUMBER OF SIZE CLASSES `N_g` AT A FIXED RATIO, WITH THE SPATIAL MESH HELD FIXED.
> THE SPATIAL MESH IS CHECKED BY A SEPARATE 2-LEVEL, NON-GATING SENSITIVITY
> DIAGNOSTIC.**

**Why size groups and not the mesh (the supervisor's point 4).** On a flow field
decoupled from the moments (`§3a`), spatial refinement changes the (frozen) flow
and the moment advection, but the error in the *quantity that worries us* — the
truncation of m4/m5, dominated by the largest aggregates — is a function of the
**size-class range and count**, not of the spatial mesh. A triple that refined
only the mesh would return a GCI that does not bound the error in m4/m5. So the
gated triple refines size groups.

**The size-group triple (three levels, refinement ratio r = 2 on class count, the
size range `[L_min, L_max]` held fixed once Blocker A fixes it):**

| level | class count `N_g` | role |
|---|---|---|
| **S1** | `N_g` (coarse) | triple |
| **S2** | `2·N_g` | triple |
| **S3** | `4·N_g` | triple (gate is read here) |

- Roache classification per moment at Fs = 1.25 (rule 5): a moment whose S1→S2→S3
  values are not monotone is not given a GCI; a moment whose triple is `DIVERGENT`,
  `STAGNANT`, `OSCILLATORY` or `EXACT` grades `NOT A RESULT`; only `CONVERGING`
  moments are gate-eligible, and the gate is read at S3 with its GCI printed.
- The concrete `N_g` (10/20/40 is the intended starting family) is fixed once
  Blocker A settles `L_min`, `L_max` (a class family cannot be laid out without the
  range). **The triple design is registered; the family bounds are a `§14`
  blocker.**

**The spatial-mesh sensitivity (2 levels, NON-GATING diagnostic).** Run at the
fixed gate `N_g` on meshes M1 (coarse) and M2 (fine, the reference spatial mesh).
The comparator prints all six moments on both meshes and `|m_k(M2) − m_k(M1)|`,
labelled `DIAGNOSTIC — NOT A CONVERGENCE PROOF AND NOT A GCI`. **Binding rule fixed
here:** if the spatial sensitivity on any moment exceeds that moment's reference
quantisation (`§4.3`'s `q` = 0.379 % relative), the spatial error is not
demonstrably subdominant and the case grades **`NOT A RESULT` (spatial error not
bounded)** — the size-group triple alone does not then bound total discretisation
error. Stated before compute so it cannot be waived after the numbers are visible.

---

## §8. THE CONVERGENCE CRITERION — STEADY-STATE ADEQUACY, FROZEN A-PRIORI, BINDING INCLUDING IF IT FAILS

This is a **steady** case; the criterion is iterative/pseudo-transient
convergence, not a fixed-time sample.

### §8.1 Rule 5 limb (1) — iterative convergence, binding on every level

- **Residual floor:** the continuity, momentum, k, ε and every size-group scalar
  residual fall below a fixed tolerance set in the frozen `fvSolution`/`controlDict`
  (named exactly once the solver dictionary is written — Blocker B), at the final
  iteration, on **every** level (S1, S2, S3, M1, M2).
- **Moment plateau at the outlet, on a FIXED iteration window** (not a
  fraction-of-run window — `ANSYS_VERIFICATION_CHARTER` Amendment 1.4 disclosure #1
  and `MONITOR_STANDARD` S13: *"a fraction-of-run window silently loosens as a run
  is extended, so the same case passes by being run longer"*). Rule, fixed here:
  over the **last 500 iterations**, the peak-to-peak of each outlet moment,
  **normalised by that moment's value**, is `≤ δ = tol/10 = 0.076 %`. `K = 10`
  encodes "iterative drift must be an order of magnitude below the band so it
  cannot move the verdict"; no observed value informs it (`§0`).

### §8.2 The pre-committed fallback, fixed before compute

If the plateau criterion fails at the registered iteration count: **extend once**
by a fixed additional block (a further 2000 iterations, mirroring the manual's own
2000-iteration moment block), **subject to the `§12` cap** which is not raised for
it. If it still fails, or the cap fires first, the case grades **`NOT A RESULT`
(steady state not demonstrated)**. **No loosened `δ` is available.**

---

## §9. STRICT COMPLETION (CLAUDE.md rule 4)

Binding on **every** run (S1, S2, S3, M1, M2). The comparator **refuses, exit 2**,
on any failed clause rather than grading a partial run.

| clause | this case |
|---|---|
| `rc = 0` | captured **inside** the detached subshell, never around the `setsid` line (`setsid parent returns zero`) |
| an `End` line | in `log.<solver>` |
| last time == `endTime` | the pseudo-steady `endTime` (iteration/pseudo-time count) reached |
| fields present at `endTime` | `U`, `p` (or `p_rgh`), `k`, `epsilon`, the phase fields, and **every size-group field** `f.i0 … f.i(N_g−1)` (or the solver's size-group naming) in the final time directory |
| ExecutionTime count == step count | count of `ExecutionTime` lines == count of `Time = ` lines (the internal-consistency form of the clause; the solver runs pseudo-transient so the literal `deltaT=1` form does not apply — declared, not smuggled, per the VMFL069-R2 precedent) |
| age guard | every field in the final time directory **newer** than the case's own `0/` launch marker; the launcher **refuses** if `0/` or any time directory already exists |

---

## §10. THE PLANTED CONTROL (CLAUDE.md rule 3)

The comparator's reader — the moment-recovery sum `m_k = Σ_i N_i L_i^k` — is the
thing that must be shown able to see a non-zero, because a false zero here would
make an unrun or empty case look like a match.

**Positive plant, on the GATE LEVEL'S OWN BYTES (S3).** `PLANT` = a known increment
added, **by cell index** (never by glob, never by pattern — `a zero needs a live
planted control`), to one size-group field `f.iJ` in the outlet cells, in a
**scratch copy** of `S3`'s final time directory (never the run tree). The
comparator re-runs the identical moment-recovery reader on the planted copy and
**refuses, exit 2**, unless each recovered moment `m_k` changes by exactly the
analytically-predicted amount `Δm_k = PLANT · L_J^k` (to a stated 1 % numerical
tolerance). This proves the reader can see a perturbation on the very bytes that
produce the gated numbers, and simultaneously proves the summation is wired
correctly across all six orders.

**Refusal is exit 2 and writes no grading JSON.** A comparator without a fired
plant has produced no number.

---

## §11. PRINCIPAL RISKS — ranked by what most likely makes this `NOT A RESULT` or `GATE FAIL`

1. **Feed-shape reconstruction (Blocker A's residual, `§5a.4`).** β₀ (=1) and the six
   feed moments are now fixed from the archive; what remains is building a sectional
   feed distribution that reproduces those six moments, since m1/m2/m4/m5 depend on
   feed shape beyond the moments. A poor reconstruction biases the non-closing
   moments. Bounded by `§7`'s triple and by the a-priori m0/m3 checks; a comparator
   setup risk, not a `BLOCKED`. (The former binding blocker — no β₀ / no feed — is
   **resolved**, `§5a`.)
2. **Sectional truncation of m4/m5.** A size range that omits the largest
   aggregates makes m5 (and then m4) undershoot; if the size-group triple does not
   reach `CONVERGING` before the cap, those moments grade `NOT A RESULT`; if it
   converges below the band, `GATE FAIL`. Guarded by `§7`'s size-group triple.
3. **The `§3a` velocity-group coupling** (Blocker C). If the setup lets size
   classes carry distinct velocities, the flow re-couples to the moments and the
   frozen-flow equivalence argument breaks. Fixed by a single shared velocity
   group, verified in the smoke.
4. **Euler–Euler steady convergence.** Multiphase population-balance solves can
   stall or oscillate before plateau; guarded by `§8` and its bounded fallback,
   and by the cap (`§12`).
5. **Spatial error not subdominant.** If the frozen flow is under-resolved, the
   moment advection carries spatial error the size-group triple does not bound;
   guarded by `§7`'s spatial sensitivity diagnostic and its `NOT A RESULT` rule.
6. **Solver selection.** OpenFOAM's `populationBalanceModel` lives in the
   `reactingEuler` family (`reactingMultiphaseEulerFoam` / `reactingTwoPhaseEulerFoam`);
   the exact solver that exposes `constantCoalescence` with breakup/nucleation off
   and a single velocity group must be confirmed against an ESI tutorial template
   (Blocker B). A wrong solver choice is a `BLOCKED` at the smoke, not a physics
   result.

---

## §12. COST — UNFILED PENDING A COSTED SMOKE (the `§26.3` discipline, VMFL024 precedent)

> ### ⛔ §12.0 STATUS — **NO COST NUMBER IN THIS SECTION IS FILED. `§12` IS A FREEZE BLOCKER.**
>
> `§26.3` forbids filing a point estimate whose own method has an unmeasured
> input. **This lab holds NO measured per-step rate for `reactingMultiphaseEulerFoam`
> (or any Euler–Euler multiphase + population-balance solver) on this box** — every
> `interFoam`/`rhoCentralFoam` rate the lab has measured is for a different solver
> family. Filing a point estimate would rest on a transferred rate the solver
> never exhibited (VMFL024's exact §12.6 lesson: *"an extrapolated cost basis
> transfers the rate it measured and not the physics it never contained"*).
> **`§12` is therefore unfiled; the bracket below is the PRE-SMOKE RECKONING.**
>
> **The unmeasured inputs, named exactly:** (1) the per-cell-per-iteration wall
> cost of the chosen Euler–Euler + N_g-size-group solver under this case's
> `fvSolution`; (2) the iteration count to a `§8` plateau, which for a stiff
> aggregation source is not known a-priori.

### §12.1 The pre-smoke bracket — labelled an ORDER-OF-MAGNITUDE bracket, per the supervisor's ruling

The supervisor's ruling of 2026-09-04, adopted verbatim in spirit: *"mark it
explicitly as an ORDER-OF-MAGNITUDE bracket with its two soft inputs named, in the
form … 'the bracket contained the answer; the point estimate did not'."* The two
soft inputs are exactly (1) and (2) in `§12.0`.

Method: `core-min = cells × iterations × per-cell-iter-cost × RANKS ÷ 60`, with a
2-D box mesh taken at ~10⁴ cells (representative; the reference spatial mesh is
itself a Blocker-B item), iterations to plateau taken at 3,000 (soft), and the
Euler–Euler + PBM per-cell-iter cost taken at 5e-4 s (soft — no measured basis).

| end | construction | core-min (per level) | triple + diagnostics |
|---|---|---|---|
| **FLOOR** | 2,500 cells × 1,500 iter × 1e-4 s | ≈ **6** | ≈ **40** total |
| **POINT (unfiled)** | 10⁴ cells × 3,000 iter × 5e-4 s | ≈ **250** | ≈ **1,500** total (3 size levels + 2 mesh) |
| **CEILING** | 2e4 cells × 6,000 iter × 1e-3 s, N_g = 40 | ≈ **2,000** | ≈ **6,000** total |

**The bracket spans two orders of magnitude, and that width IS the finding:** the
point estimate is not trustworthy without the smoke, and the honest statement is
the bracket. Even the ceiling (≈ 6,000 core-min ≈ 100 core-hours; **derived
$5.13** at $0.0513/core-h, **derived not measured** — the box cannot read its own
billing, `COMPUTE_BUDGET_CHARTER` §5) sits far under the $25 pre-authorised
per-run ceiling, so **cost is not the binding constraint on this case** (unlike
VMFRT005). The binding constraint is Blocker A.

### §12.2 The cap — provisional, set at the pre-smoke ceiling, retired by the smoke

> **PROVISIONAL CAP: 6,000 core-min RUNNING TOTAL across all runs of this case,
> derived $5.13. An overrun STOPS the run (rule 12); it does not get a new
> budget.** This is the pre-smoke ceiling; after the costed smoke anchors the
> per-step rate, `§12` is re-derived and the cap re-set at a true ~3× the filed
> point estimate under `§26.2` — an amendment to an unfrozen document (rule 2),
> before any graded compute.

### §12.3 The costed smoke — designed, NOT run, and designed so it CANNOT see the gate

A one-configuration probe measuring **two quantities and no others**: the
per-cell-per-iteration wall cost of the chosen solver on the coarsest mesh at the
coarsest `N_g`, and the per-iteration residual slope (to estimate iterations to
plateau). It runs in a scratch directory **outside**
`verification/runs/ansys_verification/` (CLAUSE B), writes **no** outlet-moment
probe and **no** time directory at the gate configuration, and produces no
physics reading, no verdict, and no input to any gate, band, threshold or label.
It **cannot see the gate**: it is run at a coarse `N_g` far below the gate level
and reads no moment at the outlet. Cost calibration is owed at completion (rule
12, `§5` step 7): one row in `docs/COST_CALIBRATION.md`, the first measured
Euler–Euler-multiphase rate this lab will hold, ratio + attribution + waste named
separately.

---

## §13. THE CASE — solver, model, mesh, numerics (the frame; specifics gated by `§14`)

| item | value / intent |
|---|---|
| solver | ~~`reactingMultiphaseEulerFoam`~~ **SUPERSEDED by `§B.1`: the built/tested solver is `reactingTwoPhaseEulerFoam`** (v2606, `…/bin/reactingTwoPhaseEulerFoam`, 882888 B, confirmed present and it ran the case) — the only compiled solver with `populationBalanceTwoPhaseSystem` + `constantCoalescence`/`velocityGroup` and a shipped `populationBalance` tutorial. |
| population balance | **sectional**, `libpopulationBalance.so`; aggregation kernel **`constantCoalescence`** (source header: *"Constant coalescence kernel. Used for verification and validation"*); **breakup OFF, nucleation OFF, drift OFF** — aggregation alone (`§5`) |
| kernel constant β₀ | ~~**1**, pinned by the smoke~~ **SUPERSEDED by `§B.5`.** The ½-convention needs no factor (source, supervisor ruling), but OF's number density is α₂-scaled, so the dictionary kernel is **β₀ = 1/α₂ = 100** for the built dilute case (α₂=1e-2): `coalescenceModels ( constant { rate rate [0 3 -1 0 0 0 0] 100; } )`. Derived from frozen α₂ + feed shape + Da=100, NOT from the smoke. Supervisor ruling required (B-open-1). |
| feed moments | m0..m5 = `1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999` — **RESOLVED (`§5a`)**; sectional feed built to reproduce these six (Blocker B setup) |
| size classes | `N_g` at S1/S2/S3 = `N_g / 2N_g / 4N_g` (`§7`); range `[L_min, L_max]` a **discretisation choice** (feed abscissas O(1), aggregates larger), bounded by `§7`, not a physics blocker |
| velocity group | **single shared velocity group** so size classes share the phase velocity (`§3a`, Blocker C) |
| phases | continuous water (ρ 998.2, μ 0.00103) + dilute dispersed particle phase, α₂ = 1e-06, drag `Schiller–Naumann` on a **constant 1e-05 m** diameter (`§3a`, `§5`) |
| turbulence | **standard k-ε** (manual) on the continuous phase |
| geometry | 2-D square box side 0.1 m; inlet opening 0.02 m and outlet opening 0.02 m on opposing/appropriate faces (layout per archive zones `inlet`/`outlet`/`sidewall`/`bottomwall`/`topwall`); **unit depth (2-D)** |
| BCs | top wall 101 m/s and bottom wall 100 m/s toward the outlet; inlet 0.005 m/s; outlet gauge p = 0; feed moment distribution **BLOCKER A** |
| time control | pseudo-transient/steady to a `§8` plateau; `endTime` = iteration count; `writeControl` guaranteeing a final time directory; `adjustTimeStep` per solver stability |
| mesh M2 (spatial, fine) | the reference spatial mesh (~10⁴ cells intended); M1 the coarse spatial-sensitivity level (`§7`) |
| launcher | sources its own environment unconditionally, asserts `command -v reactingMultiphaseEulerFoam` and `command -v blockMesh`, each aborting with a named message; smoke runs in the launcher's actual environment |

---

## §14. ⚠ FIVE FREEZE BLOCKERS — THIS DOCUMENT IS NOT FREEZABLE AS IT STANDS

**Blocker A is the binding one and is stated first.**

> **BLOCKER A — RESOLVED 2026-09-04 (`§5a`).** β₀ = 1 (m³/s) and the six feed
> moments `(1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)` were read **independently
> from the shipped archive** via resolution path (1) — but from the archive's
> plain-ASCII members (`report.xml`, `.set`) rather than the HDF5 `.cas.h5` blob
> that defeated the earlier `strings` read (the `.cas.h5` confirms them a second
> time). Two kernel-free physics checks corroborate: m3 volume conservation is exact
> (m3_feed 1.91 = target 1.910), and the CMSMPR zeroth-moment relation predicts
> m0 = 0.1318 vs target 0.132 (−0.17 %). Resolution path (2) — Wan et al. 2005 — was
> **not needed**; path (3) back-calculation was **not used** (rejected as circular,
> `§5`/`§5a.5`). The size range/class count is a `§7` discretisation choice, not part
> of Blocker A. **The case is no longer `BLOCKED` on physics data.**

> **BLOCKER B — RESOLVED 2026-09-04 (`§B`).** The case and comparator now EXIST,
> are smoke-verified and untracked; `§B` supersedes the solver name and β₀ below and
> raises two new pre-freeze rulings (B-open-1 β₀/α₂, B-open-2 feasibility). The
> original blocker text is retained below for the record.
> **[original]** No OpenFOAM case
> (`constant/phaseProperties`, `constant/populationBalanceProperties`,
> `constant/momentumTransport`/`turbulenceProperties`, `0/` fields for U, p, k, ε
> and every size-group, `system/{controlDict,fvSchemes,fvSolution,blockMeshDict}`),
> no launcher, and **no comparator** (`cases/ansys_verification/VMFL034/analyse_vmfl034.py`,
> which must implement `§4` limbs+band, `§4.4` verdict rule, `§7` triple
> classification + GCI, `§8` criteria, `§9` completion, `§10` both the summation
> reader and its planted control, `§7`'s DIAGNOSTIC labelling of the mesh
> sensitivity) — `--selftest`ed, committed, and its sha inserted here before the
> freeze (`§5` step 1). The solver selection (`§13`) is confirmed against an ESI
> `populationBalance` tutorial template here.
> **Route-4 setup facts now fixed for Blocker B (ESI v2606 source, `§5a`):**
> (a) dispersed phase `diameterModel velocityGroup` with `sizeGroups ( fN { d <dia>;
> value <volfrac>; } … )` where the `value`s (volume fractions of the group) **must
> sum to unity** and each field is `f<N>.<phase>.<popBal>`; (b) `populationBalanceCoeffs
> { <popBal> { coalescenceModels ( constant { rate rate [0 3 -1 0 0 0 0] 1; } );
> binaryBreakupModels (); breakupModels (); driftModels (); nucleationModels (); } }`;
> (c) **the comparator's moment reader must convert OpenFOAM's volume-fraction-per-
> diameter-bin to diameter moments**: `n_i = α₂·f_i / ((π/6)·d_i³)`, then
> `m_k = Σ_i n_i·d_i^k`. The m0 = 1 feed normalisation and the a-priori m0 = 0.1318
> check (`§5a.3`) are the guard that this conversion and the β₀ code-convention factor
> are correct — verified in the smoke before any grading. |

> **BLOCKER C — RESOLVED 2026-09-04.** OpenFOAM's `velocityGroup` diameter model
> (confirmed against the ESI v2606 tutorial
> `tutorials/multiphase/reactingTwoPhaseEulerFoam/RAS/bubbleColumnPolydisperse/constant/phaseProperties`
> and `diameterModels/velocityGroup/sizeGroup/sizeGroup.H`) assigns **one shared
> phase velocity to all size classes in the group** — that is precisely what
> `velocityGroup` means. Setting the dispersed phase's `diameterModel velocityGroup`
> with all `sizeGroups` under one `velocityGroup` therefore satisfies `§3a`'s
> single-shared-velocity requirement by construction. Still verified in the smoke as
> a setup assertion, but no longer an open design question.

> **BLOCKER D — COST IS UNFILED** (`§12.0`): the costed smoke (`§12.3`) must run
> and `§12` be re-derived and filed before the freeze, retiring the provisional
> cap. |

> **BLOCKER E — NOTHING IS COMMITTED AND NO QUEUE ROW EXISTS.** The directory is
> untracked; there is no `verification/queue/ansys-verification/VMFL034*.json`.
> **The supervisor commits (the freeze is `§3` check 4); this lane commits
> nothing.** |

**The pre-flight smoke** (CLAUSE B): ONE iteration on the COARSEST spatial mesh at
the coarsest `N_g`, in a scratch directory **outside**
`verification/runs/ansys_verification/`, in the launcher's actual environment. A
failure ABORTS the run and is a finding, not a retry.

---

## §15. THE OUTCOMES, NAMED IN WRITING BEFORE COMPUTE

1. `PASS` — all six moments inside ±0.76 % at S3, all size-group triples
   `CONVERGING`, spatial sensitivity subdominant, `§8`–`§10` satisfied. GCI printed
   per moment. **The ceiling (`§3`).**
2. `GATE FAIL` — any of the six converged moments outside ±0.76 % (with GCI).
3. `NOT A RESULT` — completion (`§9`), steady criterion (`§8`), a size-group triple
   not `CONVERGING` (`§7`, rule 5), spatial error not subdominant (`§7`), or the
   plant (`§10`) failing.
4. `NOT A RESULT` (budget/kill class) — the `§12` cap fires.
5. `NOT A RESULT` (solver death) — non-zero rc / floating-point exception. **A
   non-zero rc is a finding, not a retry.**
6. `BLOCKED` — Blocker A cannot be resolved (β₀ / feed distribution not obtainable
   on this box), or the CLAUSE B smoke fails. **A `BLOCKED` with β₀ named as the
   specific missing datum is the honest completion state Sanaa's 2026-09-04 order
   contemplates, and it goes to her desk.**

---

## §16. WHAT THIS REGISTRATION DOES NOT ESTABLISH

- It does **not** establish that OpenFOAM's sectional method equals QMOM; it
  establishes whether OpenFOAM's sectional discretisation of the aggregation PBE
  reaches the PBE's own analytical moment solution inside ±0.76 % (`§3`).
- It does **not** verify the turbulent flow field independently; the flow is a
  decoupled carrier (`§3a`) and its accuracy enters only through the moment
  advection, bounded by `§7`'s spatial sensitivity.
- It does **not** reproduce the manual's Fluent (QMOM) column, and does not use it
  as a reference (`§1`).
- It does **not** bound any error introduced by a β₀ or feed distribution that
  turns out to differ from Wan et al.'s; if Blocker A is resolved from the archive,
  the setup is "the case as shipped", corroborated by the shipped target, not
  proved against the primary source (which the lab does not hold).
- Reproducing the CMSMPR analytical moments by an independent well-mixed ODE path
  would verify **the reference**, not the solver, and earns **no `PASS`** on this
  case (`ANSYS_VERIFICATION_CHARTER` §18, §33.2); it is available only as an
  a-priori check that the target is the constant-kernel analytical solution it
  claims to be.

---

## §17. FREEZE CLAIM (`§37.2`) — WHAT THIS WAS FROZEN BEFORE

When the supervisor commits this file, the commit freezes it **before the run,
before the data, and before the reading**: no VMFL034 solver has run (`§0`), no
VMFL034 field data exists, and no VMFL034 moment has been read by any comparator
(the comparator does not exist, Blocker B). All three senses are stated so a reader
does not supply the most flattering one. The grading path is fixed at the
pre-registration commit and will be verified by hashing the frozen comparator
against its committed blob before it grades (`CLAUDE.md` rule 2).

---

## §B. BLOCKER B RESOLVED — THE CASE AND THE COMPARATOR EXIST (appended 2026-09-04T15:50Z by `ansys-lane-opus48`)

The OpenFOAM case (`0.orig/`, `constant/`, `system/`) and the comparator
`analyse_vmfl034.py` were built and left **UNTRACKED** (committing is the freeze,
the supervisor's `§3` check 4; this lane committed nothing, launched no graded run,
touched no archive copy). A short **smoke** was run into scratch
(`…/scratchpad/ansys-lane-034c/run/`, outside `verification/runs/`) purely to prove
the case builds and to establish the field interface — **no smoke output was used
to select β₀ or any convention** (Ruling 2).

This section also carries **TWO NEW FINDINGS that change frozen inputs and must be
ruled on before the freeze** (`§B.5`, `§B.6`), and it **SUPERSEDES two rows of
`§13`** (solver name; β₀ value/justification).

### §B.1 Solver — `reactingTwoPhaseEulerFoam`, NOT `reactingMultiphaseEulerFoam` (`§13` row SUPERSEDED)

`§13` named `reactingMultiphaseEulerFoam`. That is **corrected**. The only compiled
v2606 solver whose phase-system type is `populationBalanceTwoPhaseSystem` and which
carries the `constantCoalescence`/`velocityGroup`/`sizeGroups` API this case needs —
and the **only** solver with a shipped `populationBalance` tutorial — is
**`reactingTwoPhaseEulerFoam`**:
`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/reactingTwoPhaseEulerFoam`
(present, 882888 bytes). Template:
`tutorials/multiphase/reactingTwoPhaseEulerFoam/RAS/bubbleColumnPolydisperse`
(the sole tutorial matching `populationBalance` in `constant/phaseProperties`).
The case **built and ran** with it (smoke rc=0, `End`, fields written).

### §B.2 Feed-shape reconstruction — 3-node Wheeler quadrature + Kumar–Ramkrishna fixed pivot

The six feed moments `(1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)` were reproduced
in two stages, **forward from the archive moments, consuming no target**:
1. **3-node Wheeler (product-difference) quadrature** on the six feed moments gives
   abscissas `L = (0.51034, 1.15677, 1.85318)`, number-weights
   `w = (0.22888, 0.62870, 0.14242)` — reproducing all six moments to **machine
   precision** (residuals ≤ 1.8e-15). This is legitimate because the sequence is a
   valid (Hankel-positive) moment sequence (dets 0.1623, 0.007489).
2. **Kumar–Ramkrishna fixed pivot** places those three delta-nodes onto the
   geometric sectional grid by **volume** (`v ∝ d³`), which **conserves m0 (number)
   and m3 (volume) EXACTLY** and leaves a small, grid-refining residual on the
   feed-shape moments m1, m2, m4, m5. Measured per-moment feed residual:

   | N groups | m0 | m1 | m2 | m3 | m4 | m5 |
   |---|---|---|---|---|---|---|
   | 25 | 0.000% | −0.423% | −0.420% | 0.000% | +0.853% | +2.153% |
   | **35 (base)** | **0.000%** | **−0.245%** | **−0.264%** | **0.000%** | **+0.581%** | **+1.505%** |
   | 50 | 0.000% | −0.077% | −0.073% | 0.000% | +0.148% | +0.376% |

   The residual falls monotonically with refinement — it is a **discretisation
   decision bounded by the `§7` size-group triple**, exactly as Ruling 1 requires.
   That m0/m3 are exact by construction is why m0 and m3 have independent a-priori
   predictions (`§5a.3`) and why m3 is the **volume-conservation** limb.

### §B.3 The comparator — conversion guard, planted control, `§39.5` evidence

- **Moment conversion (the guarded step):** `n_i = α₂·f_i/(κ·d_i³)`, `κ = π/6`,
  then `m_k = Σ_i n_i·d_i^k`; outlet moments normalised to the manual's `m0_feed=1`
  scale by `C = m3_target/m3_feed(OF)`, `m3_feed(OF) = α₂_inlet/κ` (frozen). **m3 is
  therefore NOT forced to 1.910 — it tests volume conservation** (Ruling 1).
- **Planted control (rule 3), designed to FAIL a mutated reader.** The reduction is
  a weighted **sum over all 35 bins**; the plant perturbs a **PROPER SUBSET**
  (bins {8,9}) by `PLANT = 3.21e-4`, and requires the measured moment response to
  equal `Δm_k = (α₂/κ)·PLANT·Σ_{i∈S} d_i^{k−3}` — computed from the geometry the
  comparator itself holds. A subset (not the whole set) is used precisely because a
  plant over the entire reduction **cancels and is inert** (last night's failure).
  This **supersedes `§10`'s `Δm_k = PLANT·L_J^k`**: the comparator reads the
  **volume-fraction fields `f_i` that the solver writes**, not `N_i`, so the plant
  is placed on `f` and the expected response carries the full `/(κ d³)` conversion —
  which makes the plant catch a mis-conversion, not just a mis-summation.
  `--selftest` proves three mutated readers REFUSED: dropping κ, wrong power in the
  n-conversion (`d²`), and wrong moment power (`d^{k+1}`) — each fails the plant and
  exits 2. The plant also runs on the **real** reader before any zero is trusted.
- **Strict completion (rule 4) + age guard**, REFUSE (exit 2): checks a standalone
  `End` in the **solver-specific** log (`log.<application>`/`log.solver`, never
  `log.blockMesh`/`log.checkMesh`, which also print `End` — a real loophole found
  and fixed here), last written time == `endTime`, every `f<i>.air.bubbles` +
  `alpha.air` present, and every endTime field **newer than `0/alpha.air`**.
  Proven: endTime-mismatch, missing-`End`, and missing-sizeGroup cases each REFUSE
  with exit 2; a valid case returns 0.
- **`§39.5` — every path read is a path the solver WRITES**, proven on the real
  smoke output (`0.00015/`):
  - `f<i>.air.bubbles`, `i=0..34` — sizeGroup fields; `sizeGroup.C:46-60`
    constructs them `AUTO_WRITE` as `name.phase.popBal`; **all 35 appeared** in the
    smoke time directory.
  - `alpha.air` — dispersed volume fraction; appeared, outlet value 0.010 (α₂
    conserved).
  The outlet patch values are written `value nonuniform List<scalar>` (10 outlet
  faces); the comparator averages them. A `--selftest` on synthetic arrays proves
  LOGIC; the `--case` read of the **real** smoke output proves the INTERFACE — it
  returned m3 = 1.91000 exactly (conversion + normalisation correct) and outlet
  moments ≈ the feed (no aggregation after 15 steps, as expected).
- **Verdict logic matches the registration's CONJUNCTION**, not a looser limb: the
  band is the frozen **uniform ±0.76 %** of `§4.2`/`§4.3` on **all six** limbs
  (the comparator was initially drafted with looser per-limb bands and **corrected
  to match** — the precise failure the brief warned of). Per-limb **content**
  (Ruling 1) is carried alongside each limb. Overall = conjunction of all six
  primary limbs under rule-5 gating (`§4.4`).

### §B.4 Grid range and count — NOMINAL units (Ruling 4)

Geometric grid **d ∈ [0.45, 22.0] nominal**, **35 groups** base (ratio 1.121);
`§7` triple over group count **25 / 35 / 50**. Ruling 4 shaped this directly: the
feed mean size is `m1/m0 = 1.108` (nominal), the outlet volume-mean is
`m4/m3 = 4.75` and `m5/m4 = 5.93`, so the range spans O(1) up to a tail near ~15–20
— **NOT 1e-6** (the archive's `min-dia 1e-6` is a QMOM default, irrelevant to a
sectional setup). The upper bound 22.0 is set generously so the source loop's
`if (fi.x()+fj.x() > sizeGroups.last().x()) break;` (`populationBalanceModel.C:673`)
does not truncate aggregates; tail truncation at `d_max` is a systematic the `§7`
triple exposes.

### §B.5 ⚠ FINDING 1 — β₀ INTO THE DICTIONARY IS **1/α₂**, NOT 1 (refines, does not refute, the supervisor's convention ruling)

The supervisor resolved (msg `affe9dd93ab43580b`) that the **net-½ convention**
needs **no conversion factor**: `populationBalanceModel.C` birth carries `0.5*`
when `i==j` (`:274-286`), the pair loop is a half range `for (j=0; j<=i; j++)`
(`:671`), and `deathByCoalescence` (`:334-341`) yields net `dn/dt = −½β₀n²`, which
is the manual's convention. **That ruling is correct and stands.**

**But there is a SECOND, INDEPENDENT factor the convention analysis did not
address: OpenFOAM's sectional number density is scaled by the dispersed volume
fraction α₂.** Read from the same source, verified in the bytes here:
`deathByCoalescence` adds `coalescenceRate_()*fi.phase()*fj*fj.phase()/fj.x()`
(`:337`), where `fi.phase()`/`fj.phase()` **are the phase fraction α₂** and
`fj.x()` is the particle volume `κd³`. So the source term carries **α₂²**, and
since `N_i = α₂ f_i/(κ d_i³)`, the net balance is
`dN_tot/dt = −½ β₀ N_tot²` with `N_tot = α₂/κ · Σ f_i/d_i³ ∝ α₂`. Birth scales
identically (`:277`, `fj*fj.phase()/fj.x() = N_j`).

**Consequence.** The manual's answer depends on the aggregation number
`Da = β₀·N_feed·τ = 100` (β₀=1, m0_feed=1, τ=100 — all archive/geometry inputs).
In OpenFOAM, `N_feed = α₂/κ·Σf_i/d_i³`. For this feed shape `Σf_i/d_i³ = 0.5236 = κ`,
so **`N_feed(OF) ≈ α₂`**. To reproduce `Da = 100` the dictionary kernel must be
**`β₀_OF = Da/(N_feed·τ) = 1/α₂`**:

| α₂ (inlet) | N_feed(OF) | required β₀_OF [m³/s] |
|---|---|---|
| 1.0 | 1.000 | **1.000** |
| 1e-1 | 0.100 | 10.0 |
| **1e-2 (case)** | **0.010** | **100.0** |
| 1e-6 | 1e-6 | 1e6 |

So **`β₀=1` is correct ONLY at `α₂≈1`** (a non-dilute dispersed phase, which
removes the continuous water phase that carries the 100 m/s / k-ε flow and is
unphysical here). For the **dilute** phase the flow requires, `β₀ = 1/α₂`. This is
**not gate-fitting**: `β₀_OF` is derived from the **frozen inlet α₂ and feed shape**
and the manual's frozen `Da=100`, before any run — a declared, source-derived unit
conversion (Ruling 2 point 3), the α₂ number-density scale, **separate from** the ½
convention. The case as built uses **α₂ = 1e-2, β₀ = 100** (a moderate, numerically
safe self-consistent pair). Had `β₀=1` been frozen with dilute α₂, `Da≈1e-4` and
the solver would produce m0/m0_feed ≈ 1 (no aggregation) — a ~**660 %** false
GATE FAIL with no physics in it. **This root — Fluent-QMOM transports the moments
as free scalars (magnitude set by the BC, m0_feed=1) while OF-sectional ties number
density to α₂ — is the structural gap between the two methods for this case.**
**REQUIRES A SUPERVISOR RULING before freeze:** accept `β₀=1/α₂` with the declared
α₂, or run α₂ nearer unity. The `§13` row "β₀=1 … pinned by the smoke's m0=0.1318"
is **SUPERSEDED** (and its "pinned by the smoke" clause was itself the gate-fitting
Ruling 2 forbade).

### §B.6 ⚠ FINDING 2 — THE LITERAL TRANSIENT RUN IS INFEASIBLE (~3,350 core-hours/grid); a dimensionless rescale is proposed

`reactingTwoPhaseEulerFoam` is **transient only**; there is no frozen-flow /
steady PBE solver (the manual's Fluent freezes the flow and iterates moments). To
reach steady aggregation we need ~5τ = 500 s of physical time. **Measured** smoke
cost: **0.241 s/step** (single rank, 2500 cells, 35 groups). With 100/101 m/s walls
the Courant limit at Δx≈0.002 m forces **Δt ≈ 1e-5 s**, so 500 s ⇒ **5e7 steps ⇒
~3,352 core-hours per grid ⇒ ~10,000 core-hours for the `§7` triple** (~9 days wall
on 16 cores for **one** grid). **This is a feasibility blocker, and Blocker D's
cost is now quantified, not bracketed.**

**Proposed resolution (a similarity rescale that preserves the verification
content), for the supervisor:** the manual's outlet moments (feed-normalised)
depend only on the **dimensionless** `Da=100`, the **feed shape**, and the
**well-mixed** condition (recirculation timescale ≪ τ) — the walls are the CMSMPR
*stirring*, the tiny through-flow is the *product removal*. Reducing the wall speed
and/or raising the inlet velocity (thereby shortening τ) while holding `Da=100`
(scale β₀ accordingly) and keeping the box well-mixed yields the **same**
dimensionless problem at a computable cost (e.g. wall 10 m/s, τ≈1 s, ~5 s physical
⇒ ~10⁴–10⁵ steps ⇒ O(10) core-hours per grid). This departs from the manual's
literal BC numbers but not from the manual's **model** — it is a declared
similarity choice. **REQUIRES A SUPERVISOR RULING before freeze.**

### §B.7 One more tension to note (Ruling 3, drag diameter)

Ruling 3's decoupling mechanism cites a **constant 1e-5 m drag diameter**. In
OpenFOAM the **dispersed** phase's drag uses its own diameter = the velocityGroup
Sauter mean (O(1) nominal here), not 1e-5; only the **continuous** water phase is
given `constant d 1e-5`. The flow still decouples via (a) dilute α₂ and (b)
velocityGroup's single shared dispersed velocity (Ruling 3's second clause, and
`§3a`/Blocker C), but the exact "fixed 1e-5 drag diameter" clause does not map onto
the OF dispersed phase. Recorded, not resolved; second-order beside `§B.5`/`§B.6`.

### §B.8 Remaining freeze blockers after Blocker B

- **B-open-1 (`§B.5`):** the β₀=1/α₂ number-density scale — supervisor ruling on
  the α₂/β₀ pair.
- **B-open-2 (`§B.6`):** feasibility — accept the similarity rescale (and re-file
  τ, wall speed, β₀, endTime) or accept the ~10⁴ core-hour literal cost.
- **Blocker D:** cost is now quantified (`§B.6`) but the *chosen* operating point's
  cost must be re-filed once B-open-2 is ruled; `§12`'s bracket is retired by the
  measured 0.241 s/step.
- **Blocker E:** nothing committed; no queue row. The supervisor commits (freeze =
  `§3` check 4).
- **Naming:** the dispersed phase is `air` and the populationBalance `bubbles`
  (inherited from the template) though they model water-borne particle aggregation.
  Functionally correct; a rename to `particles`/`aggregation` before freeze is
  advisable for the credential's clarity but was not done here to keep the built
  case low-risk.

*Drafted by `ansys-lane-opus48`, 2026-09-04T15:50Z (`date -u` in this invocation:
`Fri Sep  4 15:50:28 UTC 2026`). No git operation performed; case and comparator
untracked; no graded run launched; smoke ran only in scratch and its output
selected no gate input.*

---

## §C. SUPERVISOR RULINGS A–D — APPLIED (appended 2026-09-04T16:02Z by `ansys-lane-opus48`)

The supervisor ruled on the two `§B` findings (message following `affe9dd93ab43580b`).
All four rulings are applied to the case and the comparator; the changes are recorded
here and wired into `analyse_vmfl034.py`. Still nothing committed, no graded run.

### §C.A  β₀_OF = β₀_ref/α₂ — ACCEPTED as a declared unit conversion

`Da = β₀_ref · m0_feed · τ = 1 × 1 × 100 = 100` is built from the **archive's β₀,
the archive's feed m0, and the manual's τ = V/Q** — no lab result enters, so it is a
conversion, not a fit. OpenFOAM's number density `N = α₂·f/(κd³)` is source-verified
(`populationBalanceModel.C:337`, `deathByCoalescence` = `rate·fi.phase()·fj·fj.phase()/fj.x()`,
where `fi.phase()`=α₂ and `fj.x()`=κd³), so `β₀_OF = Da/(N_feed·τ) = β₀_ref/α₂`
follows from the code's own definition. **Frozen kernel input at the rescaled point:
`β₀_OF = 100/(α₂·τ) = 100/(1e-2 · 5) = 2000` m³/s.**

### §C.B  m0 DEMOTED to a calibration limb — the price of Ruling A

m0 is a monotone function of `Da` alone (Da 50 → m0 0.180998; Da 100 → 0.131774;
Da 200 → 0.095125). Choosing `β₀_OF` to set `Da = 100` therefore **SETS m0 by
construction** — it is no longer an independent prediction and **may not license a
PASS.** This is exactly the fallback named **in advance** in Ruling 1.

- **GATE (primary predictions): m1, m2, m3, m4, m5.** m1/m2/m4/m5 are fractional
  volume-moments that do not close for a constant kernel — they depend on the feed
  shape, which the conversion does not touch, and are the case's real verification
  content. m3 tests volume conservation, independent of Da.
- **m0 — CALIBRATION/CONSISTENCY.** Reported beside the gate against its a-priori
  value **0.131774**; a miss beyond **±3 %** is a **REFUSAL trigger (exit 2)**, never
  a gate limb. (Comparator: `GATE_LIMBS=[1,2,3,4,5]`, `EXPECT_M0=0.131774`,
  `CALIB_M0_TOL=0.03`; the `--triple` overall verdict is the conjunction of the five
  gated limbs only.) **This supersedes `§4.2`'s listing of m0 as PRIMARY and the
  m0 clause of `§4.4`.**

### §C.C  THE SIMILARITY RESCALE — permitted, with its four binding conditions met

The literal transient triple is ~10,050 core-h (`§B.6`); the rescaled triple is
~35 core-h. The manual's 100/101 m/s walls in a 0.1 m water box are **synthetic** — a
device to produce a well-mixed field — and the analytical target depends only on `Da`
and the feed moments, not on the wall speeds. Rescale **PERMITTED** under `§12.2`
(sameness of model). The four conditions:

**1. DECLARED on the document's face, with factors and the manual's originals quoted.**

| quantity | manual (literal) | rescaled (graded) | factor |
|---|---|---|---|
| top wall | 101 m/s | **6.06 m/s** | ÷16.67 |
| bottom wall | 100 m/s | **6.00 m/s** | ÷16.67 (1 % differential preserved) |
| inlet velocity | 0.005 m/s | **0.10 m/s** | ×20 |
| residence τ = V/Q | 100 s | **5 s** | ÷20 |
| kernel β₀_OF | (100 at τ=100) | **2000** | ×20 (holds Da) |
| endTime | — | **25 s (5τ)** | — |

**2. Da and the six feed moments PRESERVED EXACTLY (arithmetic, in these bytes).**
`Da = β₀_OF·N_feed·τ = 2000 · 1e-2 · 5 = 100`, identical to the literal
`100 · 1e-2 · 100 = 100`. Both = **100**, exactly. The six feed moments are set
by the sizeGroup `value`s and grid `d`, which the rescale **does not touch**, so
`(1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)` are preserved byte-for-byte
(Wheeler+KR, `§B.2`). The rescale changes only velocities, τ and β₀ — the
dimensionless problem is invariant.

**3. WELL-MIXEDNESS MEASURED, with a pre-compute criterion the comparator ENFORCES.**
Recirculations during residence = `τ/t_recirc = 5·U_w/U_in`: literal 1e5, rescaled
**300**. 300 passes is far from the literal's 1e5, so well-mixedness is **measured,
not assumed**. Registered criterion, read on the internal field **before grading**,
comparator **REFUSES exit 2** if not met:
- `CoV(m0)` over the domain cells **≤ 0.10** (`WELLMIXED_COV_MAX`), and
- `|outlet-mean m0 − volume-mean m0| / volume-mean ≤ 0.05` (`OUTLET_VS_MEAN_TOL`).
Reader = `wellmixed_check()` in `analyse_vmfl034.py`; proven in `--selftest`
(uniform field CoV 0.000 passes; a ±50 % gradient CoV 0.500 refuses).
*Honest note:* the 0.10 threshold is a pre-compute estimate; if the reactor proves
marginally mixed at 300 recirculations the successor **raises U_w/U_in** (more
recirculations, more steps), never relaxes the threshold.

**4. If well-mixedness fails → `NOT A RESULT`; the successor changes the RESCALE,
never the gate or the target.** Written into the comparator's refusal message.

### §C.D  α₂ PINNED and DEFENDED at 1e-2

Because `β₀_OF = β₀_ref/α₂`, **any α₂ reproduces Da**, so α₂ is now a registered
choice, not an inherited datum. Archive value 1e-6; **chosen 1e-2.**
- **Why not 1e-6:** `β₀_OF = 1/α₂ · (100/τ)` would be **1e6·(100/τ)** — a numerically
  extreme kernel. At 1e-2 it is 2000, well-conditioned (reaction time
  `1/(β₀N)=1/(2000·1e-2)=0.05 s` ≫ Δt=1e-4 s).
- **Decoupling re-argued AT 1e-2 (not inherited from 1e-6):** the phase is still
  dilute (volume fraction 1 %). Momentum back-coupling is set by the **mass loading**
  `α₂·ρ_p/((1−α₂)ρ_w)`: with the built low-density dispersed thermo (ρ_p≈1) it is
  **≈1e-5**; even for water-density particles it is **≈1e-2 (1 %)**. Either way the
  drag reaction on the continuous water momentum is ≤1 %, so the flow is perturbed
  ≤1 % by the particles — the frozen-flow / decoupling closure (`§3a`, Ruling 3)
  **holds at 1e-2**, four orders less dilute than the archive but still firmly dilute.
- The α₂-tied number density is the reason for Ruling A; α₂ enters `β₀_OF`, `N_feed`
  and the comparator's `ALPHA2_INLET` consistently.

### §C.E  COST — RE-FILED at the rescaled operating point

- **Method:** measured per-step cost **0.24 s/step** (single rank, 2500 cells, 35
  groups; conservative — the rescaled smoke measured 0.093 s/step warm). Steps/grid =
  `5τ/Δt`, Δt = Co·Δx/U_w = 0.5·0.002/6 = 1.67e-4 s, 5τ = 25 s ⇒ **≈1.5e5 steps/grid**.
- **Estimate (derived $, not measured — the box cannot read its billing):**
  medium grid ≈ **10 core-h**; the `§7` triple (25/35/50 groups, coalescence loop
  ~N²) ≈ **35 core-h** ≈ **$1.80** at $0.0513/core-h.
- **Cap:** **70 core-h** (2× estimate) for the triple; an overrun **stops the run**
  (`CLAUDE.md` rule 12), it does not get a new budget. This **retires `§12`'s
  order-of-magnitude bracket** (Blocker D quantified).
- **Estimate-vs-actual ratio:** PENDING the graded run; to be filed to
  `docs/COST_CALIBRATION.md` at process completion (`CLAUDE.md` rule 12).

### §C.F  REMAINING FREEZE BLOCKERS after Rulings A–D

- **Blocker E — nothing committed / no queue row.** The supervisor commits (freeze =
  `§3` check 4); this lane commits nothing.
- **Well-mixedness is a RUN-TIME gate, not a pre-freeze blocker:** it is registered
  and enforced; whether 300 recirculations suffice is settled by the graded run
  itself (refuse → change rescale, Ruling C.4).
- **Naming (advisory, not blocking):** dispersed phase `air`, populationBalance
  `bubbles` (template-inherited) model water-borne particle aggregation; a rename to
  `particles`/`aggregation` before freeze would aid the credential's clarity.
- Blockers A, B, C (velocityGroup), D are resolved (`§5a`, `§B`, `§C`).

*Applied by `ansys-lane-opus48`, 2026-09-04T16:02Z. Comparator `--selftest` passes
(plant refuses three mutations; well-mixed reader passes uniform / refuses gradient;
m0 demoted); the rescaled case builds and runs (rc=0, `End`, all 35 sizeGroup fields
+ alpha written); the m0-calibration and strict-completion refusals were exercised
and each returns exit 2. No git operation; case untracked; no graded run launched;
smoke ran single-core in scratch only.*

---

## §D. GRADING-PATH PIN — **COMPLETED AT THE FREEZE, NOT DEFERRED** (charter `§39` addendum ruling)

VMFL046-R2 was frozen with its §14 reading *"Comparator: … — to be pinned by blob"*, and the queue
daemon caught the omission at launch: `GRADER-FREEZE … UNPINNED — … that absence is recorded rather
than read as a pass.` **The pin is therefore completed HERE, before the freeze commit exists.**
There is no chicken-and-egg: `git hash-object` yields a blob sha without committing, and writing
that sha into *this* file does not change the *comparator's* sha.

| | |
|---|---|
| **grading_freeze** | `cases/ansys_verification/VMFL034/analyse_vmfl034.py` |
| **git blob** | `d2453a7f2500325bf6a96c9dd3235749cb2146fd` |
| **sha256 of disk bytes** | `82c2eaa8c9a45db484401e7cbb20adacf264cbf49cd3d1bc12dc8a99015ac12b` |

**The queue row repeats this list verbatim**, so `VERIFICATION_CHARTER §2s.6`'s registration-first
precedence finds no conflict to resolve, and the daemon can verify the pin **without trusting this
document** — which is the entire reason the field exists.

### §D.1 DISCLOSED: THE PHASE NAMES ARE TEMPLATE-INHERITED AND DO NOT DESCRIBE THE PHYSICS
The dispersed phase is named **`air`** and the population balance **`bubbles`**, inherited from the
ESI `bubbleColumnPolydisperse` template the case is built from. **They label the CRYSTAL/PARTICLE
phase of a CMSMPR aggregation problem — there is no air and there are no bubbles in this case.**
The field names `f<i>.air.bubbles` and `alpha.air` are what the solver actually writes
(`sizeGroup.C:46-60`) and what the comparator reads, so they are load-bearing at the **interface**
and are retained deliberately.

> **Renaming was considered and REFUSED before the freeze, with the reason recorded rather than the
> conclusion alone:** a rename touches `phaseProperties`, all 35 written field names and every read
> path in the comparator — i.e. **exactly the `§39.5` interface that struck VMFL072** — on a case
> that currently builds and runs clean. **A cosmetic gain is not worth re-opening the one surface
> this team has already lost a freeze to.** The names are disclosed here instead, and any record
> citing this case must carry this note so a reader is never left inferring that air was modelled.
