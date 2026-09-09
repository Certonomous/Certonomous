# PRE-REGISTRATION — VMFL063-R3: Separated Laminar Flow Over a Blunt Plate

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — page 193
(Test Case and geometry), page 194 Table .63.1 (Ansys Fluent) and Table .63.2 (CFX).**
Sidecar title-page verified against the PDF beside it under `CLAUDE.md` rule 15 for
this successor: PDF page 1 = *"Ansys Fluid Dynamics Verification Manual / ANSYS, Inc.
/ Southpointe / 2600 Ansys Drive / Canonsburg, PA 15317 / Release 2026 R1 / March
2026"*; VMFL063 read directly off the PDF at printed p.193–194 (PDF index 207–208; the
PDF is offset ~14 pages from the printed number — printed 179 = PDF 193 confirmed).
Read not by filename, file type or hash.

Drafted by `ansys-lane-opus` **2026-09-09**; the fleet was killed and re-formed, and this
registration was **continued and doctrine-corrected before freeze by `ansys-lane-opus48`**
the same day (the plateau tolerance re-derived from the gate tolerance per §16.2/§20.2, the
genuine-plateau fix per §16.2/§16.3, a runtime R2-blob provenance check, and the answer-blind
smoke — all off-gate, all pre-compute; §§4.4/5/8 and the comparator carry the detail). It is
delivered UNCOMMITTED for the supervisor's §3 check-1 and then to freeze. From the moment its
commit lands this is a frozen file under `CLAUDE.md` rule 6: departures are dated addenda at
the foot, never edits above.

**SUCCESSOR to VMFL063-R2** (register row **#68**, `GATE FAIL`). It does **not** vacate
row #68, which stands as the honest record of the R2 result. It is the OWED
`ANSYS_VERIFICATION_CHARTER` §2bc successor, on the supervisor's §2bc ruling of
2026-09-09: R2 exhausted the **grid** ladder (`GCI_fine = 0.48 %`, `p = 2.505`), so the
un-ruled-out lever is **model/setup**, not numerics.

---

## 0. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**NOT YET RUN. NO VMFL063-R3 SOLVER HAS EVER STARTED, ANYWHERE ON THIS BOX.** The gate,
the band, the domain ladder, the self-convergence tolerance, the ceilings, the cap and
the named outcomes below are therefore predictions, which is the entire evidentiary
content of this document.

Checked at **2026-09-09T19:17:28Z**, HEAD **`d99b9e7b`**, and stated so a reader can
re-run each check:

| condition | how it was checked | result |
|---|---|---|
| the run root does not exist | `test -e verification/runs/ansys_verification/VMFL063-R3` | **"No such file or directory"** |
| zero paths under the R3 run root at HEAD | `git ls-tree -r HEAD --name-only \| grep -c VMFL063-R3` | **0** |
| the register carries no VMFL063-R3 row | `grep -c VMFL063-R3` on `ANSYS_VALIDATION_REGISTER.md` | **0** |
| this case directory holds no `0/` or numeric time directory | `find` for a top-level `0` or numeric time dir under the case directory (it holds only `case/`, this file, the comparator, the generator, the launcher and the smoke) | **none** |

**Re-verified by the continuing lane at 2026-09-09T20:30Z** (the drafting lane's fleet was killed and re-formed; this is the resumed dispatch): run root still absent, `git ls-tree -r HEAD` carries **0** `VMFL063-R3` paths, the register carries **0** `VMFL063-R3` rows, and no `0/` or numeric time directory exists under the case directory. The exact HEAD is not pinned here because peers commit continuously; the supervisor restates this condition at the freeze commit (rule 2).

**There is no VMFL063-R3 number on this box for any band, cap, domain or window in this
document to have been fitted to.** Amendments before first compute are legal and must
restate this condition, naming the run directory that does not exist
(`verification/runs/ansys_verification/VMFL063-R3`). After first compute the gates close:
dated addenda only, and no addendum may alter a gate, threshold, band, cap, ceiling, the
domain ladder or the self-convergence tolerance.

---

## 1. WHY R3 EXISTS — THE R2 FALSIFICATION, AND THE LAMINAR ARGUMENT THAT FIXES THE LEVER

### 1.1 What R2 found (row #68, `GATE FAIL`), and what it FALSIFIED

R2 was a **resolution-only** successor (byte-identical case inputs to the base; the only
change was a finer `r = 2` grid triple 23 040 / 92 160 / 368 640). Its hypothesis
(R2 PREREGISTRATION §1.3) was **under-resolution**: that a properly resolved 2nd-order
triple would fall toward 4.0. R2 **falsified its own hypothesis**:

| level | cells | `LR/(2t)` |
|---|---|---|
| L1 | 23 040 | 6.164703 |
| L2 | 92 160 | 5.600237 |
| L3 (finest) | 368 640 | **5.500829** |

- Triple **CONVERGING**, observed order **p = 2.505456**, **GCI_fine (Fs=1.25) = 0.48 %**,
  Richardson-extrapolated `f = 5.479580`. The grid ladder is **exhausted and asymptotic**.
- Finest **5.500829 vs Target 4.0 → 37.52 % out of the ±10 % band → `GATE FAIL`** (limb
  A). Limb B (serial determinism) `PASS`; the row takes the worse limb.
- R2 RESULTS.md line 40, on record: *"the continuum answer of this laminar SIMPLE model
  is genuinely ~5.5, not 4.0."*

**A 37.5 % miss on a grid-converged solution is not a grid artefact.** The §2bc lever is
therefore **model/setup**, not numerics — the supervisor's ruling of 2026-09-09.

### 1.2 The laminar argument — the lever is SETUP/DOMAIN, and it CANNOT be model-form

VMFL063 is **laminar** (manual: *"Laminar flow, high resolution numerical models"*; no
turbulence closure; the case carries only `U`, `p`; `momentumTransport: simulationType
laminar`). Verified for this successor: `0/` = `U`, `p` only; no `k`/`omega`/`nut`.

Because the flow is laminar, **there is no turbulence closure in either code**. A
grid-converged laminar OpenFOAM solution and a grid-converged laminar Fluent solution of
the *same boundary-value problem* must agree to discretisation error — they solve the
identical PDE. Yet the lab's Richardson continuum value is **5.48** while the manual
carries **Fluent 4.16** and **CFX 4.05** — a **~32 % code-to-code gap on identical
laminar physics**. A code-to-code gap of that size, with numerics exhausted, is by
definition a **different boundary-value problem** — a **domain / boundary-condition
setup difference**, NOT the "OpenFOAM turbulence model vs Fluent's" that a model-form
argument would need (there is no turbulence model). This rules branch-form OUT and fixes
the lever as **setup/domain**.

### 1.3 The specific gap in R2's verification — grid-independent, never DOMAIN-independent

R2 established **grid**-independence and nothing else. The domain extents and the top
boundary condition were chosen a priori and **frozen, never varied**:

| item | R2 (and base) choice | manual | note |
|---|---|---|---|
| upstream length `Lu` | 0.900 m (10·2t) | **unspecified** | never varied |
| far-field/top height `H` | 1.800 m (20·2t) | **unspecified** | blockage `t/H = 2.5 %` |
| **top boundary condition** | **`symmetryPlane`** (a frictionless slip wall: `v_n = 0`, zero shear) | **unspecified** | makes the domain a finite-height **channel**, not the external free stream the manual depicts |
| downstream extent `Ld` | outlet at the plate end, x = 1.5 m | plate length 1500 mm | never varied |

A converged GCI (0.48 %) measures **discretisation error on a FIXED domain**. It is
**blind to domain-truncation and confinement error.** The `symmetryPlane` top forces
zero mass flux and zero shear across the upper boundary — an inviscid confining wall.
For a growing boundary-layer displacement plus a separation bubble in what the manual
describes as an *external free stream*, that confinement forces the displaced flow to
accelerate over the bubble and plausibly **lengthens** `LR` — directionally consistent
with 5.5 > 4.16. R2 never tested it.

**The archive was not — and cannot be — opened.** `VMFL063_FLUENT.cas` / `VMFL063_WB.wbpz`
are **not present on this box** (searched under the case directories, 2026-09-09; the R2
prereg cited a sha256 for a copy this repository does not hold). Ansys's exact domain and
top BC therefore remain unknown, and the domain-independence study below is the principled
answer-blind resolution, standing alone.

### 1.4 The R3 lever — a DOMAIN-INDEPENDENCE study, ANSWER-BLIND

At a **FIXED grid-converged resolution** (R2-L3's near-wall and leading-edge cell sizes,
reused verbatim so grid error stays ≤ the domain effect), R3:

- **(i)** systematically enlarges the domain — `Lu` and `H` grow over a frozen ladder
  (§4) — and reads `LR/(2t)` at each domain; and
- **(ii)** as a distinct arm, replaces the confining `symmetryPlane` far-field top with a
  **non-confining constant-pressure open boundary** (`U pressureInletOutletVelocity` /
  `p fixedValue 0`) — the physically correct representation of the manual's external free
  stream.

**ANSWER-BLIND (rule 2; supervisor's §2bc ruling item 3).** The domain ladder is sized
and STOPPED by **`LR` self-convergence** — successive domains agreeing to a
pre-registered tolerance `DOMAIN_TOL` (§4) — **NEVER by proximity to the 4.0 reference.**
The reference 4.0 is not used to size, stop, or tune anything. If the domain-independent
`LR/(2t)` still lands ~5.5, that is a **standing `GATE FAIL`** (or the §10 fork), not a
reason to enlarge further or to tune. **The gate is byte-identical to R2** (§5); the fix
is entirely **off-gate** (domain extent + top-BC type).

---

## 2. THE CASE, EXACTLY AS THE MANUAL STATES IT

Manual p.193, load-bearing numbers reproduced without adjustment. Everything the manual
**explicitly specifies** is carried unchanged from R2/base; the **only** R3 changes are
the two off-gate setup levers (top-BC type + domain extent).

| quantity | manual value | in the R3 case files |
|---|---|---|
| density | 1 kg/m³ | kinematic pressure, `rho = 1` |
| viscosity | 1.7894e-5 kg/m-s | `constant/transportProperties`: `nu 1.7894e-05` |
| plate thickness 2t | 90 mm | `TWO_T = 0.090`; plate top surface at `y = t = 0.045` |
| plate length | 1500 mm | plate wall `plateTop` x ∈ [0, 1.5] (UNCHANGED; the manual fixes plate length) |
| inlet velocity | 0.0517 m/s | `0/U`: `fixedValue uniform (0.0517 0 0)` |
| Reynolds number | 260 | `0.0517·0.090/1.7894e-5 = 260.03`; comparator `--selftest` checks 260 to < 2e-4 |
| turbulence | **laminar** | `constant/momentumTransport`: `simulationType laminar` (no `k`/`omega`/`nut`) |
| convection scheme | (manual: "high resolution") | `div(phi,U) bounded Gauss linear` — 2nd-order central, **UNCHANGED from R2/base** |

**The TWO off-gate setup changes (the lever), and NOTHING else:**

1. **Far-field top BC type** — `symmetryPlane` → **non-confining open boundary**:
   `0/U farfield: pressureInletOutletVelocity value uniform (0.0517 0 0)`;
   `0/p farfield: fixedValue uniform 0`; and the far-field patch in the mesh becomes
   `type patch` (was `type symmetryPlane`). This de-confines the top: flow may cross it,
   representing the free stream. **All other BCs are byte-identical to R2** (inlet
   `fixedValue` 0.0517, outlet `zeroGradient U`/`p = 0`, `centreline symmetryPlane`,
   `plateFace`/`plateTop noSlip`, `frontAndBack empty`).
2. **Domain extent** — `Lu` and `H` enlarged over the frozen ladder (§4), at fixed
   near-field resolution via DOF-free padding blocks (§4). The plate length and the
   downstream extent `Ld` are **held at the manual's plate end (x = 1.5)** for the core
   ladder; an optional `Ld`-sensitivity diagnostic is named in §4 and gates nothing.

Everything the manual specifies is faithful; the changes are confined to what the manual
leaves **unspecified** (domain extent, top-BC type) — the un-ruled-out §2bc cause.

---

## 3. THE REFERENCE TIER, AND WHY `PASS` IS OUT OF REACH FOR LIMB A (UNCHANGED FROM R2)

**Reference kind: EXPERIMENTAL** — Lane & Loehrke measured `LR`; the manual carries it as
*Target 4.0*. Limb A makes a **CONTINUUM claim**; its ceiling under
`VERIFICATION_CHARTER` §2f.3 is **`GATE REACHED`** (`PASS` unavailable — discretisation
error is not separable from a continuum property). `TIER_CEILING_A = "GATE REACHED"` is
hard-coded and `verdict_for_limb_a()` refuses (exit 2) if it ever emits `PASS`.

**Limb B is a SAME-DISCRETE-PROBLEM IDENTITY claim** (§2f.3) — L1 vs its twin L1D; the
error cancels exactly, `PASS` is available. **The ROW verdict is the WORST limb**, so the
best possible R3 row is **`GATE REACHED`, which is not a credential**
(`ANSYS_VERIFICATION_CHARTER` §6: *"Only PASS rows are credentials."*). Stated before
compute so nobody later reads limb B's `PASS` as one.

---

## 4. THE DOMAIN LADDER, THE FIXED GRID, AND THE ANSWER-BLIND SELF-CONVERGENCE RULE

### 4.1 The fixed grid resolution (reused from R2-L3, the converged level)

Every domain-ladder solve uses **R2-L3's near-field resolution VERBATIM** — the near-field
blocks (A: upstream below plate top; B: upstream above; C: downstream above the plate) are
**byte-identical to R2-L3**: counts `NXU=256, NXD=640, NYL=96, NYU=384` and gradings
`A (0.1 0.2 1)`, `B (0.1 160 1)`, `C (20 160 1)`. Resolution therefore equals R2-L3's,
verified in R2's frozen table:

| resolution (mm) | R2-L3 = R3 fixed grid |
|---|---|
| first cell off `plateTop` | 0.1447 |
| first cell at the leading edge, Δx | 0.3688 |
| Δx at the expected reattachment region | 2.0565 |

R2 certified this resolution grid-converged (`p = 2.505`, `GCI_fine = 0.48 %`). Holding it
fixed across the domain ladder makes grid error (≈ 0.5 %) ≤ the domain effect under study.

**GRID-INDEPENDENCE INHERITANCE — the load-bearing assumption, stated explicitly.**
Evaluating the gate at `D*` on this fixed near-field grid rests on one assumption, made
here before compute: **grid-independence at `D1`, `D2` and `D*` is INHERITED from R2's
converged near-field.** The near-field blocks A/B/C — which contain the blunt leading-edge
corner, the separated shear layer and the reattachment region, i.e. **all of the physics
that sets `LR`** — are reused **byte-identical** to R2-L3 (same vertices over x ∈ [-0.9,
1.5], y ∈ [0, 1.8]; same counts; same gradings; §4.2). The R3 changes are a **FAR-FIELD**
enlargement (padding blocks beyond that region) and a **top-BC type** change — neither
touches the near-wall cell sizes R2 drove to `GCI_fine = 0.48 %`. The near-wall
separation-bubble resolution is therefore unchanged by construction, so the grid
convergence R2 established carries to every R3 domain. (The gate at `D*` still runs the
full `r = 2` triple, so this inheritance is **checked, not merely assumed**: a triple that
is not `CONVERGING` makes the row `NOT A RESULT`, §10 outcome 4.)

### 4.2 DOF-free domain enlargement (the L-501 hazard, avoided by construction)

The mesh for every `(domain, level)` is emitted by the frozen, deterministic
`gen_domain_mesh.py` (§11) — the SOLE mesh authority. Enlargement **appends padding
blocks** and leaves the near-field unchanged:

- **Near-field** blocks A/B/C reproduce R2's geometry EXACTLY — same block boundaries
  (x ∈ [-0.9, 1.5], y ∈ [0, 1.8]), same `r = 2` octave counts (`NXU/NXD/NYL/NYU`), same
  gradings A(0.1 0.2 1) B(0.1 160 1) C(20 160 1). The generated `D0` mesh therefore
  reproduces R2-L3's cell count and quality identically (**368 640 cells, max AR 62.97**,
  verified by the smoke §7). The near-wall/leading-edge/reattachment cell sizes are thus
  identical to R2-L3's. **No near-field grid DOF.**
- **Padding blocks** tile the extension: upstream (x ∈ [-Lu, -0.9], split at y = 0.045 to
  match A/B) and top (y ∈ [1.8, H], split at x = -0.9 and x = 0 to match B/C and the
  upstream padding). Each padding block **shares the near-field's cell count on every
  shared edge** (so faces match and the near-field distribution is untouched), uses
  **uniform grading**, and has an outer-edge count fixed by a **frozen deterministic
  rule, not a free parameter**: `NX_up = NX_UP_L1·f·mult_up`, `NY_top = NY_TOP_L1·f·mult_top`,
  where `NX_UP_L1 = 12`, `NY_TOP_L1 = 24`, `f ∈ {1,2,4}` is the `r = 2` level factor, and
  `mult_up = round((Lu-0.9)/0.9)`, `mult_top = round((H-1.8)/1.8)`. The padding thus refines
  with the grid (`r = 2`) and its cell size stays ≈ constant across the ladder, keeping the
  far-field aspect ratio bounded (**max AR ≈ 129 at D1/D2 L3**, checkMesh `Mesh OK`,
  non-orthogonality 0 — verified §7). Padding is FAR from the bubble and cannot move `LR`;
  it is fixed deterministically all the same, so the VMFL022 grading-DOF hazard the
  supervisor rejected under L-501 is absent by construction.

The far field (now at `y = H`, and the outer upstream face at `x = -Lu`) carries the
de-confined open BC (§2); the BC-isolation twin `D0_CONFINED` reverts the far-field top to
`symmetryPlane` (case `0.confined/`). The buildability of the whole family (D0/D1/D2 at
L1/L2/L3) is exercised by the answer-blind smoke (§7) before any freeze.

### 4.3 The frozen domain ladder (by 2t multiples — never from any LR)

| domain | `Lu` | `H` | `Ld` | note |
|---|---|---|---|---|
| **D0** | 0.900 m (10·2t) | 1.800 m (20·2t) | 1.500 m | = R2 domain; the anchor (de-confined top) |
| **D1** | 1.800 m (20·2t) | 3.600 m (40·2t) | 1.500 m | first enlargement |
| **D2** | 3.600 m (40·2t) | 7.200 m (80·2t) | 1.500 m | second enlargement |

Extents are geometric multiples of the plate thickness `2t`, fixed a priori; **no LR
value enters their choice.** `Ld` is held at the manual's plate end for the core ladder.

### 4.4 The answer-blind self-convergence rule (frozen)

The plateau criterion follows `ANSYS_VERIFICATION_CHARTER` §16.2 / §20.2 in its
**mechanical form**: the threshold is **DERIVED FROM THE GATE TOLERANCE by a rule fixed
in advance, never from an observed floor**, the derivation is executable in the frozen
comparator bytes, and **whatever number falls out is binding, including if it fails.**

- **`DOMAIN_TOL = TOL / 10 = 0.010`** — the derivation is literal in the comparator
  (`DOMAIN_TOL = TOL / 10.0`), a fixed **10× headroom below the gate band**, so residual
  per-rung domain drift cannot move the verdict across the ±10 % band. **It references
  neither the Target 4.0 nor the answer — only the frozen band it is one-tenth of.**
  *(An earlier draft justified 0.01 from the R2 grid `GCI_fine` of 0.48 % — that is an
  observed floor, which §16.2 forbids; corrected before freeze to the gate-tolerance
  derivation. The number is unchanged; the justification is now doctrine-compliant.)*
- **A-priori achievability (§21.1, commensurate units — the achievability check, NOT the
  derivation):** the crossing reader resolves `LR/(2t)` to ≈ 0.42 % (R2-L3 `Δx ≈ 2.06 mm`
  / `2t`, over `LR/2t ≈ 5.5`), **finer than 1 %**, so the stop is satisfiable and not
  sub-resolution. (This uses the reader resolution only to confirm the derived threshold
  is reachable; it does not set it.)
- **GENUINE PLATEAU (§16.2, §16.3).** The ladder **`SELF_CONVERGED`** iff the **TERMINAL**
  ladder step is within `DOMAIN_TOL`. A within-tol step **followed by** an out-of-tol step
  is a fortuitous single step, **not** a plateau — the domain analogue of a non-`CONVERGING`
  Roache triple — and reports **`NOT_CONVERGED`**. **`D*`** = the **earliest** domain from
  which **every** remaining step stays within `DOMAIN_TOL` (the smallest domain beyond which
  enlargement no longer moves `LR`). The `--selftest` drives a false plateau
  (`5.50 / 5.505 / 5.20`) and requires `NOT_CONVERGED` (§16.4: a null is trusted only from a
  reader shown able to reject it), and a genuine early plateau (`5.50 / 5.495 / 5.49 → D* = D1`).
- If the terminal step is **out** of `DOMAIN_TOL` → **`NOT_CONVERGED`** (§10 outcome 5): the
  ladder is **NOT extended beyond the frozen extents**, and the row is `NOT A RESULT`; a
  bigger-ladder successor (R4) is owed.
- The reduced instrument (`LR`, a crossing locator) is **paired with a fixed-point
  instrument** — the independent near-wall `u_x` crossing, cross-checked at every domain
  (§16.3) — so the plateau is not read off a single reduction whose argmax can wander.

### 4.5 The BC-isolation arm (diagnostic; gates nothing)

`D0` (de-confined top) vs **`D0_CONFINED`** (identical mesh and extents, `symmetryPlane`
top — a self-contained re-run of R2-L3's boundary condition inside R3). Reports the
confinement delta on `LR/(2t)`. Diagnostic only; it does not touch the gate. It isolates
the top-BC-type effect at fixed domain and mesh. (An optional `Ld`-sensitivity diagnostic
— extend `Ld` at `D*` and confirm `|ΔLR2T| ≤ DOMAIN_TOL` — is likewise diagnostic and
gates nothing.)

---

## 5. THE GATE — BYTE-IDENTICAL TO R2, EVALUATED AT `D*` (L-487)

Once `D*` is fixed by §4.4, the gate is evaluated **exactly as R2** on a three-level
`r = 2` grid triple (`L1/L2/L3`) plus the determinism twin `L1D`, all built at `D*`'s
extents (near-field octave = R2's: `L1` 23 040-cell near-field / `L2` 92 160 / `L3`
368 640, padding scaled by §4.2):

### Limb A — CONTINUUM, ceiling `GATE REACHED`

```
LR = the LAST reversed-to-attached crossing of the physical wall shear on plateTop,
     inside the frozen window  X_WIN_LO < x <= X_WIN_HI,  linearly interpolated.
GATE:  |LR/(2t) - 4.0| / 4.0  <=  0.10     at the finest level L3 at D*
AND    the Roache triple on LR/(2t) at D* is CONVERGING
```

**Every gate constant is byte-identical to the R2 comparator**, carried over verbatim
(the R3 comparator IS the R2 comparator's gate/controls, unchanged; §11): `REF_LR2T = 4.0`,
`TOL = 0.10`, `X_WIN_LO/X_WIN_HI = 0.0/1.2`, `X_SIGN_REF = 1.35`, `TAU_EPS = 1e-14`,
`FS = 1.25`, `RATIO = 2.0`, `P_MIN = 0.05`, `K_PLANT = K_PLANT_U = 0.05`,
`CROSS_TOL_CELLS = 3.0`, `LR2T_PHYS_MAX = X_WIN_HI/TWO_T`, `TIER_CEILING_A = "GATE
REACHED"`, `TIER_CEILING_B = "PASS"`. **R3 does not touch the gate** (L-487: a successor
never widens the band). The last-crossing reader, the from-data sign convention, the
cross-instrument check and the gate-blind physical-range refusal are all inherited
unchanged.

**Byte-identity is VERIFIED, not asserted.** The entire carried region — `SystemExit2`
through `roache`, the three verdict functions, the two-stage/two-channel planted-zero
control, the readers and the AST/cardinality/numeric-time-dir guards — was diffed
line-for-line against the R2 frozen comparator (blob
`5d94fecbfa35013943b60e758ff433ad50ef00f7`) and is **identical**, the only differences
being additive R3 content (the domain layer). The comparator further records the R2 blob
(`R2_COMPARATOR_BLOB`) and `--verify-frozen` **re-hashes the R2 comparator file at grade
time and REFUSES (rc 2) on any drift**, so "the gate is byte-identical to R2" is a
machine-checked invariant, not a prose claim.

### Limb B — SAME-DISCRETE-PROBLEM IDENTITY, ceiling `PASS` (retained)

```
L1D is a SECOND independent solve of L1's discrete problem at D*: identical inputs,
mesh, endTime, run in its own directory.
GATE:  same converged iteration count
  AND  sha256(<t>/{wallShearStress,U,p}) identical between L1 and L1D
  AND  LR bitwise equal between L1 and L1D
```
Band: EXACT IDENTITY; no tolerance.

### The NEW element (added beside the gate; touches nothing)

The **domain-ladder self-convergence check** (§4.4): the comparator reports
`LR/(2t)` at each domain, the successive relative differences, `D*`, and the
`SELF_CONVERGED`/`NOT_CONVERGED` state. This determines `D*` and the §10 outcome; it does
**not** enter `verdict_for_limb_a()` or the band test.

---

## 6. STRICT COMPLETION (CLAUDE.md rule 4) — UNCHANGED BASIS FROM R2

Applied at every domain solve and every gate level including `L1D`; the comparator
**REFUSES (exit 2)** on any failed clause. The basis is R2's, declared before compute and
carried over verbatim: `rc = 0` (captured inside the detached subshell); an `End` line;
`SIMPLE solution converged`; **last `Time` < `endTime`** (the declared adaptation for a
`residualControl`-terminated steady solve — `last == endTime` means it ran out of clock
without converging); `ExecutionTime` count == iteration count; fields
`U p wallShearStress Cx Cy` present at `endTime`; numeric-latest time dir == log last
Time; and the **age guard** — every field at `endTime` strictly newer than the case's own
`0/U`, with the launcher refusing any level/domain directory that already holds a `0/` or
a numeric time directory. **INFRASTRUCTURE (L-342):** `RUN_RC.*` absent → rc `NOT
MEASURED`, disclosed, grade proceeds on physics clauses; present and non-zero → REFUSE.

**endTime AMENDMENT (pre-first-compute, off-gate; supervisor's §3 check-1 ruling
2026-09-09).** The graded ceiling is **`endTime = 100000`** (launcher `ENDTIME`, injected
into every `controlDict`), raised from R2's 30000 so that a legitimately converging D1/D2
solution — on the larger de-confined domains, which carry ~2× the cells of R2-L3 — is
**NEVER clock-truncated**; `residualControl` (`fvSolution`: `p 1e-08`, `U 1e-09`) still
stops a converging solve far earlier (R2-L3 converged at 10637), and the **RUNNING-TOTAL
COST CAP of 4000 core-min (rc 124), not `endTime`, is the binding budget limit** (rule 12).
**A level that reaches this ceiling without meeting `residualControl`
(`last_time == endTime`), or that shows a sustained limit cycle, is `NOT A RESULT`** —
genuine non-convergence or de-confined-domain unsteadiness (§10 outcomes 5/6) — **and is
NEVER rescued by a widened band or a loosened residual floor** (the gate `REF_LR2T = 4.0`
and the ±10 % band are untouched; this amendment moves no gate, threshold, band, cap,
ceiling or label). **Rule-2 condition, restated and checked:** no VMFL063-R3 solver has
run; the run directory `verification/runs/ansys_verification/VMFL063-R3` **does not exist**
(re-checked 2026-09-09T20:30Z), so there is no run this ceiling could have been fitted to.

---

## 7. COST (CLAUDE.md rule 12) — MEASURED BASIS ANCHORED TO R2's 146.5 core-min

**Measured basis:** R2 actuals (RESULTS.md / LAUNCH_RECORD.txt) — total **146.5166
core-min**; L3 (368 640 cells) = **134.03 core-min at 10 637 iterations** →
throughput ≈ **2.05e-6 s/cell/iteration** (serial). All R3 solves are serial (1 rank).

**How the estimate is built (NOT from a pre-freeze production run — §20.3).** No sizing
solve is run before the freeze; the estimate is R2's **measured throughput** (2.05e-6
s/cell/iteration) applied to the **exact geometric cell counts** the frozen
`gen_domain_mesh.py` produces, at a range of plausible convergence iterations. Buildability
and the de-confined BC are confirmed only by the **answer-blind pipeline smoke**
(`smoke_vmfl063_r3.py`, §11) — coarsest mesh, scratch-only, reference never read — which is
drafted and run before launch, not pre-freeze; it reveals no gate quantity.

**Cell counts from the frozen generator** (verified by running `gen_domain_mesh.py`):
near-field L3 = 368 640; D1-L3 = 482 304 (+padding); D2-L3 = 737 280 (+padding).

| solve | cells (L3) | plausible iters | predicted core-min (2.05e-6 s/cell/iter) |
|---|---|---|---|
| D0 (ladder, de-confined) | 368 640 | 15 000–25 000 | ≈ 190–315 |
| D0_CONFINED (BC isolation) | 368 640 | ≈ 10 600–15 000 (= R2 BC) | ≈ 135–190 |
| D1 (ladder) | 482 304 | 15 000–25 000 | ≈ 250–410 |
| D2 (ladder) | 737 280 | 15 000–25 000 | ≈ 380–630 |
| **ladder subtotal** | | | **≈ 1 000–1 400** |
| gate triple + L1D at `D*` | 23 040 / 92 160 / 368 640 (+padding at `D*`) | R2 actuals + padding | **≈ 150 (D\*=D0) … ≈ 1 500 (D\*=D2)** |

The gate-triple cost is dominated by `D*`: at `D*=D0` it is ≈ 150 core-min (R2-L3 anchor),
but if `D*` is `D1`/`D2` the triple is built at those padded extents and rises to ≈ 1 500.

| item | value |
|---|---|
| **ranks** | 1 (serial, every solve) |
| **HONEST ESTIMATE** | **≈ 2 500 core-min** total — **ESTIMATE, NOT MEASURED** (ladder ≈ 1 000–1 400 + gate triple ≈ 150–1 500, central case a mid/large `D*` at ~18–20 k iters). Raised from the earlier ≈ 850, which under-counted D2's 737 280 cells. |
| **CAP** | **4 000 core-min, RUNNING TOTAL across all solves** (≈ 1.6× estimate) — supervisor cap-setting call 2026-09-09 within Sanaa's 2026-08-21 blanket, legal pre-freeze (run root absent, so the cap is fitted to no result). Raised from 1 400 so the cap does **not** rc124-stop mid-ladder before the gate triple, which would be a **wasteful budget-NAR** (spend, no verdict) — waste under rule 12, and the dollars here are trivial. |
| **per-solve cap** | drawn down level-by-level in the launcher (`timeout_s = remaining_core_min·60/RANKS`); an overrun STOPS the run (rc 124) and does NOT get a new budget; `endTime` is never reduced to fit a cap |
| `cost_basis` | c7a.4xlarge at **$0.0513/core-h**, owner-stated 2026-08-21/22 — **REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read its own billing. Dollars **DERIVED**. |
| **$ at estimate** | **$2.14 derived** (2 500/60 × 0.0513) |
| **$ at cap** | **$3.42 derived** (4 000/60 × 0.0513) |

Both sit far under the $25 pre-authorised ceiling.

**KNOWN COST INEFFICIENCY, named separately (rule 12 — waste is named, never absorbed).**
The far-field padding blocks are carried at the **near-field cell resolution** although the
far field needs none of it — that is what inflates D1/D2 (the padding roughly doubles D2's
cell count over the near-field alone). It is a genuine inefficiency, **accepted for R3**
because the dollar cost is trivial (≈ $3.42 at cap) and because coarsening the far field
(a graded expansion away from the wall, near-field R2-L3 resolution preserved) is a **new
mesh lever that would need its own verification** — a future **R4**, not an R3 change. It
is disclosed here so the completion calibration attributes it correctly and does not fold
it into a misprediction ratio.

**Estimate-versus-actual calibration is OWED at completion** (rule 12): actuals from
`COST.txt`/`RUN_RC.*`, ratio actual/predicted, attribution (contention / waste /
misprediction, **the far-field-padding inefficiency named separately per the paragraph
above**), one row in `docs/COST_CALIBRATION.md`.

---

## 8. THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3) — INHERITED VERBATIM FROM R2

The reduction is unchanged (the last reversed-to-attached crossing), so R2's two-stage,
two-channel control is inherited byte-identical: **P1a** reader sensitivity (a sized
offset `K_PLANT·max|τ|` on every `plateTop` face of a copy of the real solver bytes, read
back from disk; every value must move by the plant) and **P1b** gate-functional
sensitivity (the planted profile through the full gate functional must move the crossing
upstream / out of the window), on both the wall-shear and the near-wall `u_x` channels,
with the L-487 GOOD-arm / INERT-arm matched pair. Either stage failing REFUSES (exit 2).
The AST guard (`ast.Assert` count 0), the cardinality guard and the numeric-time-dir
cross-check are inherited. `--selftest` drives every control to both PASS and refusal
under `python3` and `python3 -O`.

**NEW in R3's `--selftest` (6 added checks, 74 total, 0 failures under `python3` and
`python3 -O`):** the domain self-convergence check is driven to both `SELF_CONVERGED` and
`NOT_CONVERGED`; the **answer-blind proof** — a synthetic ladder self-converging at ~5.5,
FAR from 4.0, still reports `SELF_CONVERGED` and picks `D*`, so the rule references
`DOMAIN_TOL` only and never the Target; the **§16.4 null control** — a FALSE plateau
(`5.50 / 5.505 / 5.20`, a tiny step then a 5.5 % jump) is required to report
`NOT_CONVERGED`, proving the detector can REJECT a non-plateau (a null is trusted only
from a reader shown able to see the non-null); a genuine early plateau
(`5.50 / 5.495 / 5.49 → D* = D1`); and that `DOMAIN_TOL` equals `TOL/10` and neither the
band nor the Target.

---

## 9. ERROR BUDGET — disclosed BEFORE the freeze

| source | magnitude | sign / direction | how obtained |
|---|---|---|---|
| Domain truncation / top confinement | **the quantity under study** | tested by the ladder; driven ≤ `DOMAIN_TOL` (1 %) at `D*` | §4 |
| Grid (fixed at R2-L3) | `GCI_fine ≈ 0.48 %` | symmetric | R2 row #68 |
| Reference resolution | Target 4.0, 2 s.f. → ±1.25 % | symmetric | manual Table .63.1 |
| Leading-edge corner singularity | present; R2 triple still reached `p = 2.505` | — | numerics of a sharp corner |
| Refinement ratio | local `r ∈ [1.967, 2.052]` → ≤ 3.75 % in `p`/GCI | symmetric | R2 §4 |
| Two-dimensionality | finite-span experiment | NOT QUANTIFIED — named, not priced | — |
| Ansys's own domain | unknown; archive NOT on the box | — | §1.3 |

**None of these widens the band. The band is 10 % and stays 10 %.**

---

## 10. NAMED LIVE OUTCOMES — every one can happen, written down now (rule 1 vocabulary)

| # | outcome | the condition that produces it |
|---|---|---|
| 1 | **ROW `GATE REACHED`** *(best attainable)* | domain ladder `SELF_CONVERGED` (`D*` found); grid triple at `D*` `CONVERGING`; `L3@D*` inside the 10 % band; `L1/L1D` identical. **Not a credential.** |
| 2 | **ROW `GATE FAIL` (physics)** | domain `SELF_CONVERGED`; triple at `D*` `CONVERGING`; `L3@D*` **outside** the 10 % band. **If de-confining + enlarging still lands ~5.5, this GATE FAIL STANDS** — nothing is tuned to reach 4.0 (rule 2). A finding. |
| 3 | **ROW `GATE FAIL` (determinism)** | limb A holds but `L1/L1D` differ in any hash, iteration count or LR bit. |
| 4 | **ROW `NOT A RESULT` — grid triple at `D*` not `CONVERGING`** | `DIVERGENT`/`OSCILLATORY`/`STAGNANT`/`p < P_MIN`/`EXACT`. Not rescued by dropping a level or widening the band. |
| 5 | **ROW `NOT A RESULT` — domain `NOT_CONVERGED`** | no `Dn ∈ {D1, D2}` meets `DOMAIN_TOL`. This is a **frozen 3-domain ladder**: it is **NOT auto-extended** beyond D0/D1/D2. Domain-independence is then **not established**, the row is **`NOT A RESULT`**, and the case is **owed a bigger-ladder successor (R4)** with wider frozen extents — the domain question is escalated to a successor, never tuned inside R3. |
| 6 | **ROW `NOT A RESULT`** | no crossing in the window / cross-instrument disagreement / a control did not fire / a completion clause failed (all inherited). |
| 7 | **`BLOCKED`** | toolchain absent or `blockMesh` fails. A crash is a FINDING, not a retry. |
| 8 | **`PENDING`** | registered and not yet run — the state this document is in as committed. |
| 9 | **THE FORK (escalation, not a row verdict)** | domain `SELF_CONVERGED` **and** `L3@D*` still ~5.5 (outcome 2 stands as the row). Because it is laminar, this residual is a **code-to-code SETUP difference unresolvable without the proprietary archive** (not on the box) — neither E1 nor E2 as §2bc is bounded. **Escalate the §2bc boundary classification to the supervisor** (who takes the pending-boundary to chief/Sanaa). Do NOT declare a terminal verdict beyond the honest `GATE FAIL`, do NOT widen the band, do NOT tune. |

**`PASS` at row level is unreachable by construction (§3).**

**THE PREDICTION.** This lane declines to predict which outcome lands. What is predicted,
and is this document's falsifiable content, is that **the gate can return any of them** —
it is not constructed so only one answer is possible — and that the domain ladder
**directly tests the domain/confinement diagnosis of §1.3**: if confinement/truncation is
the cause, `LR/(2t)` moves with domain size and the de-confined top and the ladder
self-converges to a smaller value; if `LR/(2t)` is already domain-independent at `D0`,
the confinement diagnosis is falsified and outcome 9's fork is reached.

---

## 11. THE GRADING PATH, FROZEN

| artefact | path |
|---|---|
| pre-registration | `cases/ansys_verification/VMFL063-R3/PREREGISTRATION.md` (this file) |
| comparator | `cases/ansys_verification/VMFL063-R3/grade_vmfl063_r3.py` — R2's comparator gate/controls VERBATIM + the domain self-convergence layer (§5) + the off-gate `--pick-dstar` helper |
| mesh generator | `cases/ansys_verification/VMFL063-R3/gen_domain_mesh.py` — the SOLE, frozen, DOF-free mesh authority (§4.2); the launcher calls it for every `(domain, level)` |
| launcher | `cases/ansys_verification/VMFL063-R3/run_vmfl063_r3.sh` — freeze-pins the prereg/comparator/generator/every case input disk==HEAD, runs the ladder + `D0_CONFINED`, applies the frozen §4.4 rule via `--pick-dstar` to fix `D*`, then builds the gate triple at `D*` under `GATE/`. Running-total cap 4000 core-min (rc124 = cap = stop); age guard on every solve dir |
| answer-blind smoke | `cases/ansys_verification/VMFL063-R3/smoke_vmfl063_r3.py` — a CHEAP, SCRATCH-ONLY pipeline check (coarsest D0/L1, de-confined top): confirms buildability, that the new far-field BC runs, and that the LR reader plumbing parses real solver bytes end to end. Reads NO reference (§20.3-declared; the one coarse LR it could reveal goes to stderr behind a banner, never persisted, never compared). It launches no graded solve |
| case inputs | `cases/ansys_verification/VMFL063-R3/case/` — R2's inputs with the two off-gate changes of §2; plus `0.confined/` (the symmetryPlane-top variant for the `D0_CONFINED` BC-isolation twin) |
| run root | `verification/runs/ansys_verification/VMFL063-R3/` — **does not exist** |

**The launcher refuses to spend a core-minute unless, at launch:** this file, the
comparator, the generator AND every case input on disk hash equal to their HEAD blobs
(the freeze-pin — verified to ABORT pre-freeze); the comparator's `--selftest` is green
under both interpreters; and each solve directory holds no `0/` and no numeric time
directory. `grade_vmfl063_r3.py --verify-frozen` re-hashes this file and the comparator
against HEAD at grade time (rc 2 on mismatch).

**A graded run is HELD pending the supervisor's §3 checks and the launch decision (rule
9): nothing in this document authorises a graded solve.** The §7 smoke is a SEPARATE,
answer-blind, scratch-only act that reads no `LR`.

---

## 12. WHAT THIS REGISTRATION DOES NOT CLAIM

- It is not a statement about Ansys; this box has no Ansys solver, and the archive is not
  on the box. Fluent's 4.16 and CFX's 4.05 are context, never the gate.
- It does not tune the domain to hit 4.0; `D*` is fixed by `LR` self-convergence alone.
- It cannot earn a credential — ceiling `GATE REACHED` at row level, by construction.
- It establishes nothing about domains larger than `D2` or resolutions finer than R2-L3.
- It does not assert which outcome lands; §10 names them all, including the fork.
- Nothing here is sent anywhere. Submissions are parked; the manual is proprietary Ansys
  documentation held for this lab's private use (rules 7 and 8).
