# F17c — PRE-REGISTRATION: Kovasznay flow, Re = 40, THE ITERATIVE-CONVERGENCE FLOOR (`simpleFoam`)

Team cfd. Case `cases/F17c_kovasznay_floor/`. Run root
`verification/runs/F17c_runs/`. Version 1.0, written 2026-08-27 by cfd lane R2
(the re-form of lane A, killed ~18:25Z mid-task; lane A wrote the case files,
this lane inspected, re-derived and completed them — see §11).

**Instrument-check** (`CASE_SELECTION_CHARTER.md` §3, labelled here at
registration, as F17 and F17b were): counts toward no challenge column.

**Nothing has been run.** §9 records the absence check in the writing
invocation.

---

## 1. WHAT THIS RUNG IS FOR, IN ONE PARAGRAPH

F17b re-ran the Kovasznay ladder at 192×128 / 384×256 / 768×512 and returned
**NOT A RESULT × 2**. Not because the physics failed and not because the band
was wrong — the fine values sat *inside* both registered bands — but because
F17b inherited F17's iterative floor **byte-for-byte**: a fixed 4,000 SIMPLE
iterations at every level. On F17's grids that floor left the iterative
contribution two orders below the discretisation error. On F17b's grids it did
not, and F17b's own registered Class C plateau criterion — correctly — refused a
fine level that was still moving by 13.5 % of itself over its last 1,100
iterations (`F17b_KV40_EXT_RESULTS.md` §1). That is **L-346**: *an
iterative-convergence floor is DERIVED from this case's own measurement, never
inherited from another case.*

F17c changes **exactly one thing**: the per-level iteration count. The meshes,
the case dictionaries, the discretisation model, both gates, both bands and
every Class C tolerance are F17b's, unchanged. **The gate that caught F17b is
not touched** — L-346's fix is to derive the iteration count, never to relax the
criterion.

---

## 2. THE CASE — unchanged from F17 §2 and F17b §2

Kovasznay flow, the steady closed-form solution of the incompressible
Navier–Stokes equations at Re = 40:

    u = 1 − exp(λx) cos(2πy),   v = (λ/2π) exp(λx) sin(2πy),
    p = (1 − exp(2λx))/2,        λ = Re/2 − sqrt(Re²/4 + 4π²),   ν = 1/Re = 0.025

Domain x ∈ [−0.5, 1.0], y ∈ [−0.5, 0.5], cyclic in y, one cell thick in z.
Solver `simpleFoam` (OpenFOAM v2606, `/usr/lib/openfoam/openfoam2606`), laminar,
Gauss linear throughout, `fvSolution` and `fvSchemes` byte-identical to F17
(blobs `f0eea325` / `96a0fc1b`).

**The reference is not a paper on this box** (rule 15): the closed form is
verified by **symbolic substitution into the steady incompressible
Navier–Stokes equations at selftest time**, with the three residuals required
identically zero and a planted control (λ × 1.1) required to make the momentum
residuals non-zero. Control 1 and control 2 of §7.

---

## 3. THE LADDER — F17b's THREE LEVELS UNCHANGED, r = 2 EXACTLY

| level | Nx × Ny | cells | h | refinement | ranks |
|---|---|---|---|---|---|
| coarse | 192 × 128 | 24,576 | 1/128 | — | **1** |
| medium | 384 × 256 | 98,304 | 1/256 | r = 2.000 in BOTH directions | **1** |
| fine | 768 × 512 | 393,216 | 1/512 | r = 2.000 in BOTH directions | **1** |

Uniform square cells at every level, so h = LX/Nx = LY/Ny and the meshes are
geometrically similar: **r = 2.000 exactly, dim = 2** in `roache_triple`.
Every level runs **SERIAL on 1 rank**; `decomposePar` is never invoked at any
level; decomposition seed `none` (identity decomposition — there is no
partition and no RNG, so no F6a-class partition drift between invocations).

**Mesh admissibility** (`docs/standards/MESH_STANDARD.md` §3): `checkMesh` must
report `Mesh OK` and max non-orthogonality ≤ 70°, max skewness ≤ 4 at every
level, enforced **inside `build_f17c.py` at build time** (it refuses above the
gates), and recorded per level in `MESH_LINE.txt`. F17b measured 0° / 1.4e−14,
4.3e−14, 8.5e−14 on these same three meshes.

**The cell this ladder targets in `docs/MESH_STANDARD.md`'s grid table.** That
table is the six-row L1…L6 family (Tiny / Coarse / Medium / Fine / Extra Fine /
Ultra Fine) with the `[(L+2)/(L+1)]³` size-growth and `[(L+2)/(L+1)]` linear
rules. F17c's three levels are **L4 → L5 → L6 (Fine → Extra Fine → Ultra
Fine)**, and they deliberately do **not** sit on that table's ratios: the
standard's ratios are 1.95× / 1.73× per step in **3-D cell count**, whereas a
Roache triple needs a **constant** refinement ratio, and this 2-D ladder uses
r = 2 linear in both directions = **4.00× in cell count per step, constant**.
That is a **declared departure, registered here before compute, not a
violation**: `MESH_STANDARD.md`'s growth rule is for building a mesh *family*
for a design study; rule 5 requires a constant r for an order to be extractable
at all, and a diminishing ratio would make the observed order a function of
which step it was measured on. F17 and F17b took the same departure on the same
grounds. **Nothing in this rung claims conformance to the `[(L+2)/(L+1)]³`
rule.**

---

## 4. THE ITERATIVE FLOOR — DERIVED FROM THIS LADDER'S OWN MEASUREMENT (L-346)

### 4.1 The measurement, its cost, and what it was

**The measurement is a re-reading of F17b's own 40 written checkpoints per
level, at ZERO NEW COMPUTE. It was neither a scratch run nor a ladder level:
no solver was started, no run directory was created, and nothing was written
under any run root.** The artefacts read are
`verification/runs/F17b_runs/<level>/<t>/U` for t = 100 … 4000, plus each
level's own `0/C`, through **this repository's frozen reader**
(`foam_io_f17c.read_field`). Cost: **0.000 core-min of solver time**; the
analysis itself is ~3 wall-minutes of single-core file parsing in a scratch
script, which is not a run and is not costed as one.

**Reader control (rule 3, planted at the reader level).** The re-reading used a
second, independently written vectorised parser; it was required to agree with
the frozen reader **on the same file, byte for byte**, before any number was
taken from it: `F17b_runs/fine/4000/U`, 393,216 cells, **max |difference| =
0.000e+00**, and E2 through both readers = **6.155850e−06**, identical to the
value in `F17b_KV40_EXT_RESULTS.md` §1. A reader that had not been shown able
to reproduce a known non-zero would not have been used.

### 4.2 What the measurement says

The graded quantity **E2** was recomputed at all 40 checkpoints of each level
and its increments over the last 20 were fitted as a geometric sequence
(log |ΔE2| linear in iteration, least squares, ρ quoted per 100 iterations):

| level | ρ per 100 iters | E2 at 4,000 | remaining to its own converged value | state at 4,000 |
|---|---|---|---|---|
| coarse | 0.89131 | 1.423137e−04 | **+1.03e−10 = 0.00007 %** | converged |
| medium | 0.78558 | 3.558768e−05 | **+9.36e−09 = 0.026 %** | converged |
| fine | **0.98517** (+2σ 0.98538; last observed ratio 0.98435) | 6.155850e−06 | **+4.3489e−06 = 41.40 %** | **41 % short** |

**The fine level was 41.4 % short of its own converged value at 4,000
iterations.** (F17b's record states 13.5 %; that is the *drift over the last
window*, a different quantity — 41.4 % is the *distance still to travel*. Both
are correct and they are not the same number.) Extrapolated converged
E2_fine = **1.050478e−05**, which sits **inside the UNCHANGED registered band**
[2.299887e−06, 2.069898e−05].

**The second gate is not the binding one, and this is stated rather than
assumed.** The same fit on `u_at_probe` gives ρ = 0.92945 (coarse, remaining
1.4e−07 %), 0.76567 (medium, 3.1e−05 %) and, at fine, **ρ = 1.0645 — greater
than one, so no geometric extrapolation is available and none is claimed.** The
fine probe series is not diverging; it had already PLATEAUED in F17b (drift
1.97e−06, variance ratio 1.344) and its increments are at the scale where the
fit has nothing left to fit. **E2 is therefore the quantity the floor is
derived from**, and the probe gate rides on it.

### 4.3 The registered counts

The registered Class C trend tolerance is **2.0e−04 relative drift over the
trailing 1,100-iteration (12-checkpoint) window and IS NOT TOUCHED.** Solving
drift(N) = rem(N) × (ρ⁻¹¹ − 1) ≤ 2.0e−04 × E2_∞ for N gives, by three
independent routes:

| route | medium | fine |
|---|---|---|
| point estimate ρ | 5,183 | 43,568 |
| ρ + 2σ | 5,262 | 44,110 |
| last observed increment ratio (no fit) | — | 41,768 |
| this lane's independent 100-iteration grid search | ≤ 5,300 | **43,600 / 44,200 / 41,600** |

**REGISTERED, rounding up past the worst of every route:**

    ITERS = coarse 4,000    medium 8,000    fine 48,000

`endTime` is **per level**; there is deliberately **no global iteration count**
in this rung, because one number serving three levels *is* the L-346 defect.
The counts live in `exact_f17c.ITERS`, the launcher's `LEVELS` table must agree
with them (checked before any compute), and each level's **written**
`controlDict` is read back and required to equal the registered count before
that level's solver starts — *the floor that runs must be the floor that was
registered.*

The coarse level is registered at 4,000 on the **direct measurement** that its
drift there was already 1.82e−06, 110× inside the tolerance — not on a decay
fit. What 48,000 buys, **as a prediction and not a result**: remaining movement
at fine = 0.11 % of E2_∞, three orders below the discretisation error where
L-346 asks for one.

**A considered alternative, rejected and recorded.** The slow fine-level
convergence is a property of SIMPLE at fixed relaxation as h falls; a better
pressure solve would reach the same discrete answer in fewer iterations. It is
**not taken**: it would change the case, break byte-identity with F17 and F17b,
and be registered without a pilot. Paying the iterations on a known-good
configuration is the cheaper risk.

---

## 5. THE GATES, THEIR BANDS, AND THE REGISTERED PREDICTION

Both gates, both bands, both references and the band-construction principle are
**F17b's, unchanged** (F17b's own Amendment 1 reference included). They are
reproduced here so this document is self-contained; they are **frozen in
`grade_f17c.py::bands()`**, which is the file that grades.

| gate | quantity | dim | band | reference |
|---|---|---|---|---|
| **G-F17-1** | `E2_velocity_L2` = sqrt(mean over cells \|U_h − U_exact\|²)/U0 at `<endTime>/U` | 2 | **[2.299886970024015e−06, 2.0698982730216133e−05]** | 0.0 |
| **G-F17-2** | `u_at_probe` = u/U0 at (0.5, 0), bilinear between the four surrounding cell centres | 2 | **[0.3823735001308136, 0.3823948460265708]** | **0.3823841730786922** |

**Band principle, declared and not fitted.** The one parameter both bands are
built from is `BAND_FACTOR = 3.0`. G-F17-1's band is the
discretisation-model prediction E2 = 6.899660910e−06 at h_fine = 1/512 × [1/3, 3];
G-F17-2's is the exact field sampled at the fine level's own cell centres and
interpolated by the grader's own `bilinear()` at (0.5, 0), u/U0 =
0.382384173078692 (pointwise exact 0.382372819953864), ± 3 × the model's
predicted pointwise error there (−3.557649293e−06) = ± 1.067294788e−05. The
model is the **linearised discrete equations forced by the exact field's own
truncation residual**, assembled and solved on the same uniform grids with the
same stencils `simpleFoam` uses — a function of the scheme and the grid and
nothing else. It is solved at 96×64 and 192×128 (2.89 GB RSS measured; 384×256
needs 14.9 GB and 768×512 exceeds this 30 GB box) and extrapolated at its own
observed order.

### 5.1 L-345 — THE REGISTERED MODEL TRIPLES DRIVEN THROUGH THE REAL `roache_triple`

L-345: *a gate quantity whose own registered model triple reads DEGENERATE is a
registration defect.* Both model triples were passed through
`scripts/roache_triple.py::all_triples` at **dim = 2** in the writing
invocation, before this document was committed:

| model triple | coarse | medium | fine | **state** | order |
|---|---|---|---|---|---|
| G-F17-1 `E2_pred` | 1.106948807e−04 | 2.763615641e−05 | 6.899660910e−06 | **CONVERGING** | 2.0020 |
| G-F17-2 exact + predicted probe error | 3.823157385e−01 | 3.823585695e−01 | 3.823692623e−01 | **CONVERGING** | 2.0020 |

Neither is DEGENERATE, STAGNANT, OSCILLATORY, EXACT or DIVERGENT. **No
registration defect under L-345.**

### 5.2 THE REGISTERED PREDICTION — stated before compute, falsifiable

Applying §4's extrapolation to **all three levels** and passing the result
through the real `roache_triple` at dim = 2, this lane predicts, **before any
solver has started**:

| gate | predicted coarse | predicted medium | predicted fine | predicted state | predicted p | fine inside band? | **predicted verdict** |
|---|---|---|---|---|---|---|---|
| G-F17-1 `E2` | 1.423138e−04 | 3.559705e−05 | **1.050478e−05** | CONVERGING | **2.0885** | yes | **PASS** |
| G-F17-2 `u_probe` | 3.824412e−01 | 3.823881e−01 | **3.823832e−01** | CONVERGING | **3.4322** | yes | **PASS** |

For contrast, the same triple built from F17b's **inherited** floor reads
CONVERGING at p = **1.8585** — the number F17b printed beside its NOT A RESULT
and was not entitled to claim. **The falsifiable content of this rung is that
deriving the floor moves the E2 order from 1.86 to ≈ 2.09 and turns two NOT A
RESULTs into two PASSes.** If the ladder returns anything else, the prediction
is wrong and the record will say so; the prediction changes no gate, no band, no
cap and no label.

The predicted probe order 3.43 is **not** ≈ 2 and is registered as such: the
probe error at these grids is dominated by the same-stencil interpolation term
that F17b's Amendment 1 identified, and no order claim is made for it. It is
predicted to PASS **on its band**, not on its order.

---

## 6. CRITERIA — how the verdict is reached, in rule 5's order

Unchanged from F17b §6. Reached through
`scripts/roache_triple.py::grade_ladder` and **through nothing else** —
**exactly one call node**, at `cases/F17c_kovasznay_floor/grade_f17c.py:756`,
censused by AST at every entry and driven both ways by control 7.

1. **Iterative convergence** — a census of the solver's own initial residuals
   over **every** iteration in the Class C window: Ux ≤ 1.0e−06, Uy ≤ 1.0e−06,
   p ≤ 1.0e−05. Any level failing → **NOT A RESULT**.
2. **Class C plateau on the graded quantity itself**, sampled at every written
   checkpoint (`writeInterval` 100): trend tolerance **2.0e−04** relative drift
   over a **12-checkpoint (1,100-iteration) window**, mean-split tolerance
   1.0e−04, variance-ratio band [0.2, 5.0], minimum 20 samples; element 4
   **exits** rather than returning a state. Any level not PLATEAUED → **NOT A
   RESULT**. **These are F17b's numbers, byte-for-byte. They are the gate that
   caught F17b and they are not relaxed.**
3. **Triple state** — DIVERGENT / STAGNANT / OSCILLATORY / EXACT / DEGENERATE /
   NO_ORDER → **NOT A RESULT**, with the value, both triples and both orders
   printed beside it.
4. **CONVERGING** → **PASS** inside the pre-registered band, else **GATE FAIL**,
   GCI at Fs = 1.25 printed. No GCI is quoted on a non-monotone triple.

The gate can only turn a PASS or GATE FAIL **into** NOT A RESULT, never the
reverse. **Rule 4 (strict completion)** is checked per level before any of the
above: recorded rc, an `End` line, last time == `endTime`, `Time =` count ==
`endTime`, `<endTime>/U` and `/p` present and **newer than that case's own
`0/U`** (the age guard; `0/U` is written last by `build_f17c.py`), and an R-RC-4
fatal/signal-token fence over the log with the `trapFpe` startup banner
excluded. **The comparator refuses (exit 2) rather than degrading.**

---

## 7. CONTROLS — each shown able to REFUSE, in the writing invocation

`python3 cases/F17c_kovasznay_floor/grade_f17c.py --selftest` → **rc 0**,
**11 controls green**, 53.6 s. `python3 -O …/grade_f17c.py --selftest` →
**rc 2 at entry** (`-O` deletes every `assert`, including the `_seal`
invariants inside the shared `roache_triple.py`; with those gone rule 1 and
rule 5 are enforced by nothing, so the grader refuses to run at all).

1. symbolic substitution into steady NS — three residuals identically 0
2. **PZ-F17-LAMBDA** — λ × 1.1 planted; the momentum residuals must go non-zero
3. constant-ratio refinement checked in both directions (r = 2.0, 2.0 in x and y)
4. face-averaged boundary data balances to round-off (net flux 0, 0, 1.11e−16)
5. the discretisation model is solved and **second order** (2.00196, 2.00201)
6. **PZ-F17-CLASSC** — all four Class C limbs each shown able to refuse
   (flat → PLATEAUED, ramp → NOT_PLATEAUED_TREND, step → NOT_PLATEAUED_TREND,
   short series → exit 2)
7. **PZ-F17-GRADE_LADDER_CALLSITE** — AST census (one call node, **line 756**) plus
   a grep matcher driven **both ways**
8. solver dictionaries on disk agree with the registration (ν = 0.025;
   endTime coarse 4,000 / medium 8,000 / fine 48,000; the `ITERS_BASIS` string)
9. the reader parses **real solver-written `U` already on this box**
   (`verification/runs/ansys_verification/VMFL019/L1_30/5/U`, 120 cells)
10. **PZ-F17c-L342/L346/R-RC** — infrastructure vs physics field classes driven
    both ways: deleting an infrastructure field leaves the verdict channel
    unchanged and refuses only the **cost claim**; corrupting a physics field
    gives **NOT A RESULT**
11. **PZ-F17-AMEND1** — the probe reference is same-stencil: reference
    0.3823841731, stencil error 1.1353e−05, a zero-error field reads back
    **0.0**, and a 1.234e−03 plant reads back **1.234e−03**

**Both gate quantities driven to a PASSING and a FAILING value THROUGH THE REAL
READER** (rule 3). `demonstrate()` writes a real OpenFOAM ascii
`volVectorField` at the fine size (exact + k × the model's own error field) to
disk and reads it back with `e2_from_files` / `u_probe_from_files` — the same
functions that grade:

| gate | construction | value | band | result |
|---|---|---|---|---|
| G-F17-1 | exact + **1×** model error | 6.899661e−06 | [2.299887e−06, 2.069898e−05] | **inside** (intended inside) |
| G-F17-1 | exact + **40×** model error | 2.759864e−04 | same | **outside** (intended outside) |
| G-F17-2 | exact + **1×** model error | 0.3823806152 | [0.3823735001, 0.3823948460] | **inside** (intended inside) |
| G-F17-2 | exact + **40×** model error | 0.3822418565 | same | **outside** (intended outside) |

A gate not shown able to take **both** values causes `demonstrate()` to refuse.

**`0` `ast.Assert` nodes in the shipped grading path** — `grade_f17c.py`,
`exact_f17c.py`, `foam_io_f17c.py`, `build_f17c.py` (the grader's own census,
`files_checked` 4, `assert_nodes` 0, `planted_assert_seen` **true**), and this
lane checked `proj_f17c.py` separately: also **0**. Five shipped Python files,
**0 asserts total**.

**The cap-enforcement path is planted-controlled too** (§8.3): `timeout` was
shown to return **124** on an overrunning command and **0** on one that
finishes, in the writing invocation.

---

## 8. COST — COSTED BEFORE THE RUN, RULE 12

### 8.1 The rate basis — MEASURED ON THESE EXACT MESHES

Per-cell-iteration rates taken as the **MARGINAL** cost — first and last
`ExecutionTime` readings differenced over 3,999 iterations so startup is
excluded — from F17b's own logs (`verification/runs/F17b_runs/<level>/
log.simpleFoam`), and **re-measured independently by this lane in the writing
invocation**, agreeing to every digit:

| level | cells | marginal s/iteration | **core-µs per cell-iteration** |
|---|---|---|---|
| coarse | 24,576 | 0.016592 | **0.6751** |
| medium | 98,304 | 0.091880 | **0.9347** |
| fine | 393,216 | 0.292833 | **0.7447** |

These are the **same three meshes, the same solver, the same box, 1 rank**.
This is a base-rate measurement, not a transfer.

### 8.2 THE GROWTH BASIS — STATED EXPLICITLY, AND IT IS *NO EXPONENT AT ALL*

This is the lab's standing calibration defect and this rung does not repeat it.
Across F21 / F22 / F18b the **base rates were right to 7–10 % every time** and
the **growth exponent, imported from another case, was wrong by +110 to +137 %
per doubling against a registered +72–80 %**. F17b's own cost note made a
milder version of the same error: it registered **+30 % per doubling** and the
fine level came in **25 % UNDER** that projection.

**F17c registers NO per-doubling growth exponent, because the measured rate is
not monotone in problem size.** It **rises 38.5 %** from coarse to medium and
**falls 20.3 %** from medium to fine. Across six levels spanning 256× in size —
F17's 1,536 / 6,144 / 24,576 at 0.5063 / 0.4676 / 0.5826 and F17b's three above
— it rises, falls, rises and falls again, peaking at 98,304 cells. **Any
exponent fitted to two of these levels extrapolates the wrong way to the
third**, which is exactly the failure mode F21 / F22 / F18b recorded.

What `proj_f17c.py` carries instead are **frozen per-level ratios from that one
measurement — not an exponent — and `GROWTH["fine"] = 0.7967 IS LESS THAN
ONE.** A projector that could not carry a growth factor below 1 would
over-project this ladder by 25 %. A mechanism is *offered and is not measured*:
this box is an AMD EPYC 9R14 with 16 MiB L2 and 64 MiB L3 in 2 instances and the
three working sets straddle that. **The non-monotonicity is the measurement;
the cache story is a hypothesis.**

**Contention multiplier = 1.0, on this rung's own measurement.** F17b's three
1-rank levels ran at wall/CPU ratios 1.0077 / 1.0080 / 1.0001 on a session-busy
box: the contention effect on this exact work is **bounded below 1 %**, inside
the ±16 % run-to-run spread the rate band already carries (the same
24,576-cell mesh measured 0.5826 µs/cell-iteration under F17 and 0.6751 under
F17b). This also retires **L-349** for this rung: `proj_f17c.py` reads no clock,
no `/proc` and no disk, takes every input as an argument, and cannot refuse work
because the box is full.

### 8.3 THE ESTIMATE, THE CAP, AND HOW THE CAP IS ENFORCED

| level | cell-iterations | rate (core-µs) | projected wall s | **projected core-min** |
|---|---|---|---|---|
| coarse | 98,304,000 | 0.6751 | 66 | **1.106** |
| medium | 786,432,000 | 0.9347 | 735 | **12.251** |
| fine | 18,874,368,000 | 0.7447 | 14,056 | **234.262** |
| **ladder** | 19,759,104,000 | — | **14,857** | **247.62** |

**REGISTERED ESTIMATE: 247.62 core-min** (= 4.127 core-h), all **1 rank**.
This is `proj_f17c.py`'s own arithmetic, printed by its `--selftest`; it is not
a second figure written beside the code.

**REGISTERED CAP: 370.0 core-min** = **1.4942 × the estimate**, and
`grade_f17c.py::CAP_CORE_MIN == run_f17c.sh::CAP_CORE_MIN == 370`, asserted by
the launcher **before any compute** and printed by `--preflight`.

**Dollars: $0.212 at the estimate, $0.316 at the cap — DERIVED, NOT MEASURED**
($0.0513/core-h, c7a.4xlarge, owner-stated and reported-by-owner; **this box
cannot read its own billing**, `COMPUTE_BUDGET_CHARTER.md` §5). Under the $25
pre-authorisation; a blanket is not a per-item read (rule 9), and this is the
per-item read.

**THE CAP IS ENFORCED INSIDE A LEVEL, NOT ONLY BETWEEN LEVELS — registered as a
change from F17b.** 93.6 % of this ladder's spend sits in **one** level. F17b
checked its cap only after each level *returned*, which is adequate when the
longest level is 1,174 wall s and **vacuous** when it is a projected 14,056: a
between-levels check would let the fine level overrun by any factor at all
before anything noticed. Rule 12 says an overrun **stops** the run. So the whole
remaining cap, converted to wall seconds at that level's rank count, is handed
to `timeout` around the solver:

| level | remaining cap at launch | **wall allowance** | projected wall | headroom |
|---|---|---|---|---|
| coarse | 370.000 | 22,200 s | 66 s | ×334 |
| medium | 368.894 | 22,133 s | 735 s | ×30.1 |
| fine | 356.643 | **21,398 s** | 14,056 s | **×1.52** |

A kill leaves an **incomplete** level, which rule 4 refuses and the grader
reports as **NOT A RESULT** — that is the correct outcome of an overrun, not a
defect. The allowance is written to `<level>/CAP_ALLOWANCE.txt` before the
solver starts. **The cap is never raised.** The pre-spend projection
(`proj_f17c.py`, exit 3 = HALT) still runs before every level.

### 8.4 WALL TIME, DISK AND MEMORY — registered because they are unusual here

- **Wall time ≈ 4.13 h at the estimate, 6.17 h at the cap**, at **1 rank of 16**.
  The fine level alone is a projected **14,056 wall s**. `COMPUTE_BUDGET_CHARTER`
  §6's *"a row over 3600 wall s is a stall"* heuristic **will fire on the fine
  level and it will not be a stall**: it is a single registered 48,000-iteration
  level. **This is registered now, before compute, so the results record cannot
  be accused of explaining it away afterwards.**
- **Disk: 16.8 GB of checkpoints projected** — `writeInterval` 100 is
  **unchanged from F17b** because the Class C window is defined in checkpoints,
  so changing the interval would silently change the criterion. That gives 480 /
  80 / 40 checkpoints. One fine checkpoint is **0.0334 GB measured**
  (`F17b_runs/fine/4000`: U 13.65 MB, p 5.69 MB, phi 14.02 MB) → fine 16.01,
  medium 0.67, coarse 0.08 GB. Free space **measured 261 GB** at
  2026-08-27T18:49:34Z; the ladder needs **6.4 %** of it. Run output stays under
  `verification/runs/F17c_runs/` and is **not committed**.
- **Memory floor 3.0 GB**, the same figure F17b registered: the binding
  consumer is the grader's own sparse model solve at 192×128 (**2.89 GB RSS
  measured**), not `simpleFoam`, which is < 1 GB serial at 393k cells.
- **Grading wall time ≈ 10–12 min** (480 fine checkpoints × 0.6 s per frozen
  read × 2 gates), **zero solver compute**. Registered so a long grade is not
  mistaken for a hang.

### 8.5 CALIBRATION AT COMPLETION (rule 12's calibration clause)

At completion the results record **must** carry the estimate-versus-actual
comparison: actual in core-minutes from the logs' `ClockTime × ranks ÷ 60`,
gross and cleaned stated separately, waste named separately and never absorbed
into the ratio, the ratio actual/predicted, the gap attributed (contention /
waste / misprediction), and dollars **derived, not measured**. A row lands in
**`docs/COST_CALIBRATION.md`**. **A completion report without this comparison is
incomplete.**

---

## 9. RULE-2 ABSENCE CONDITION, CHECKED IN THE WRITING INVOCATION

**`/home/ubuntu/Certonomous/verification/runs/F17c_runs` DOES NOT EXIST at
2026-08-27T18:50:50Z.** Checked three ways in that invocation: `ls -d` →
*"No such file or directory"*; `os.path.exists` → **False**;
`os.path.lexists` → **False** (so it is not a dangling symlink either); and
`glob('verification/runs/*F17c*')` → **[]**. `--preflight` prints the same
condition from the launcher's own code path.

No level directory exists, no `0/`, no numeric time directory, no log, no
`RC.txt`. **0.000 core-min have been spent on this rung.** The launcher
**refuses at exit 3** if the run root exists and **refuses at exit 1** if any
level directory already holds a `0/` or a numeric time directory — it deletes
nothing, anywhere, ever: `grep -n 'rm -rf|rmtree' run_f17c.sh` returns **exactly one
line, line 22, and it is the comment forbidding them**. There is no `rm`,
`rmtree` or `shutil.rmtree` against a case or run directory anywhere in the
launcher, the builder or the grader.

Amendments **before** first compute remain legal under rule 2 and must state
this condition and how it was checked. After first compute the gates are closed
and changes land only as dated addenda that cannot alter a gate, threshold, cap
or label.

---

## 10. LAUNCH SHAPE — for the supervisor's check 4; **NOT an authorisation**

    bash /home/ubuntu/Certonomous/cases/F17c_kovasznay_floor/run_f17c.sh \
         --prereg-commit=<the sha of THIS document's adding commit>

and, as a **separate** invocation at zero compute:

    python3 /home/ubuntu/Certonomous/cases/F17c_kovasznay_floor/grade_f17c.py \
         --prereg-commit=<the same sha>

The launcher **fires nothing without `--prereg-commit`** and verifies the sha is
a commit in this repository. `--preflight` runs every guard and every path
resolution **and stops at zero compute, including refusing to run
`blockMesh`** — a gate a mesher grades is fired the moment the mesher runs.

A queue entry is drafted at
`cases/F17c_kovasznay_floor/queue_entry_F17c_KV40_FLOOR.json` and is **HELD
under the case directory**. **This lane does not enqueue it.**
`SUPERVISION_CHARTER.md` §3 check 4 — pre-registration committed before compute
— is the supervisor's own and is **not** discharged by this document, by the
queue-entry validator, or by anything a lane can run.

---

## 11. PROVENANCE OF THE CASE FILES, AND WHAT THIS LANE CHANGED

`cases/F17c_kovasznay_floor/` was written by **cfd lane A**, which was killed at
~18:25Z before it could freeze. Lane A's files were **inspected, never
reverted** (rule 10). This lane (**cfd R2**) verified them and made **three**
changes, all **before first compute** and all recorded here:

1. **The estimate figure was wrong and is struck.** `grade_f17c.py` carried the
   comment *"1.4993× the 250.12 core-min point estimate"*. **250.12 is
   reproduced by no code in this case**; `proj_f17c.py`'s own arithmetic gives
   **247.62**. The comment is corrected and the discrepancy is recorded in the
   file itself rather than silently overwritten.
2. **The cap moved 375 → 370** so that cap/estimate = **1.4942 ≤ 1.5**. Against
   the true estimate, 375 was **1.5144×** — over the ceiling. Both the launcher
   and the grader carry 370 and the launcher asserts they agree.
3. **In-level cap enforcement was added** to `run_f17c.sh` (§8.3), with its
   `timeout` behaviour planted-controlled both ways.

Everything else — the floor derivation, both gates, both bands, every Class C
tolerance, the 11 controls, `proj_f17c.py` and the case dictionaries — is lane
A's and was **independently re-derived by this lane from F17b's artefacts on
disk**, reproducing ρ = 0.98517 / +2σ 0.98538 / last-ratio 0.98435,
E2_∞ = 1.050478e−05 and 41.40 % remaining **to every printed digit** (§4).

---

## 12. WHAT IS NOT REGISTERED HERE

No pressure gate (`p` is not graded). No turbulence claim — the case is
laminar. No claim about `simpleFoam`'s relaxation parameters or about SIMPLE's
convergence rate as a solver property; §4's ρ values are **measurements of this
case on this box**, not a solver characterisation. No re-grade of F17 or F17b
and no amendment to either — both are frozen and post-compute. No claim of
conformance to `MESH_STANDARD.md`'s `[(L+2)/(L+1)]³` growth rule (§3). **No
`BLOCKED-GPU`**: this rung is CPU-only by construction and no GPU is involved.

**Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7).
Everything here stays on this box (rule 8).
