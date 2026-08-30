# JF1 — JET-FLAP AIRFOIL, PRIMAL FAMILY — PRE-REGISTRATION

## *** UNFROZEN DRAFT — NOT A PRE-REGISTRATION UNTIL THE SUPERVISOR FREEZES IT ***

**Status: UNFROZEN DRAFT. Verdict: PENDING.**
**No compute has been launched against this document and none may be until the
cfd-supervisor has performed the non-delegable check 4 of `SUPERVISION_CHARTER.md`
§3 (pre-registration committed before compute) and stamped this file FROZEN with
the freezing commit sha.**
**No queue entry exists. No run root exists. No solver has been started.**
**Until the FROZEN stamp is present, every gate, threshold, band, cap and label
below is a PROPOSAL and is amendable under rule 2's pre-compute amendment
clause; §16 lists the open items the supervisor must rule on before freezing.**

| Field | Value |
|---|---|
| Rung id | `JF1` |
| Family | Jet-flap airfoil, **primal only** |
| Team | cfd |
| Drafted | 2026-08-30 |
| Directive | `etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md`, CASE 1 §1.1–§1.6, blob `1aa9ad238af0a8cc50d00ea7d218cf1b83a1b07a` |
| Scope excluded | §1.7 ADJOINT RUNG — **dafoam's, out of scope here.** Nothing in this document registers, costs, gates or authorises any adjoint, FFD, gradient or optimisation work. |
| Solver | OpenFOAM v2606, `simpleFoam` (`/usr/lib/openfoam/openfoam2606`) |
| Verdict vocabulary | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` — these six words and no synonym (CLAUDE.md rule 1) |

---

## 0. SYMBOL DEFINITIONS — READ BEFORE ANY OTHER SECTION

The directive uses the symbol `C_mu` for **two unrelated quantities** in the same
paragraphs. This registration abolishes that symbol. Two distinct names are used
everywhere below, and any script, dictionary, comparator or downstream record
derived from this document **must** use them:

| Symbol used here | Meaning | Value / range | Never written as |
|---|---|---|---|
| `C_mu_jet` | jet momentum coefficient, 2D per unit span: `C_mu_jet = (rho_j h V_j^2) / (0.5 rho_inf U_inf^2 c)` | swept: 0.0, 0.05, 0.1, 0.2, 0.4 | `C_mu` |
| `C_mu_turb` | the k-omega/k-epsilon model constant | **0.09**, fixed, never swept | `C_mu` |
| `tau` | jet deflection angle below the chord line | 30 deg = 0.5235988 rad | — |
| `theta` | the source's symbol for the same jet deflection (`ARC R&M 3304`) | identical to `tau` | — |
| `alpha` | angle of attack | 0, 4, 8 deg | — |
| `h` | slot height | 0.005 m (`h/c` = 0.005) | — |
| `c` | chord | 1.0 m | — |
| `V_j` | jet exit speed | derived, §2 | — |
| `CL_aero` | lift coefficient from surface integration only (`forceCoeffs`) | measured | — |
| `CL_total` | `CL_aero + C_mu_jet * sin(tau + alpha)` | the gated comparand | — |

**Why this is not pedantry.** The directive §1.4 writes the turbulence inlet
condition as `omega = sqrt(k)/(C_mu^0.25 * l)`. Read literally with the jet
coefficient, at the sweep point `C_mu_jet = 0.0` — the unblown reference, which
is in the sweep — the expression is `0^0.25 = 0` in the denominator: **a division
by zero.** The symbol in that formula therefore *cannot* be the jet coefficient;
it is `C_mu_turb = 0.09`, and `C_mu_turb^0.25 = 0.5477225575`. The error is also
not a constant offset that a reviewer would spot as an offset — it **changes
sign across the sweep**:

| `C_mu_jet` | `omega` if the jet coefficient is used | correct value is |
|---|---|---|
| 0.0 | **undefined (÷0)** | — |
| 0.05 | **+15.83 % too high** | 13.67 % lower |
| 0.1 | −2.60 % too low | **+2.67 % higher** |
| 0.2 | −18.10 % too low | +22.09 % higher |
| 0.4 | **−31.13 % too low** | **+45.20 % higher** |

Note the row that matters most for how this defect hides: at `C_mu_jet = 0.1` —
**the single point at which the Roache triple is taken** — the error is only
−2.6 %. A spot check performed at the gate point alone would have found nothing.

---

## 1. THE THEORY SOURCE, AND ITS CITATION STATUS

### 1.1 The primary is not obtainable and is not cited as though it were

The directive names the primary reference as Spence, D. A. (1956), *"The lift
coefficient of a thin, jet-flapped wing"*, Proc. R. Soc. Lond. A **238**,
pp. 46–68, and instructs the team to pull it and verify the constants on the
page. **It could not be pulled.** `royalsocietypublishing.org` returns **HTTP 403**
on the DOI landing page, on `/doi/pdf/` and on `/doi/epdf/`. **No one in this lab
has read Spence (1956).** This document therefore does **not** cite Spence as a
verified source and no downstream record derived from it may do so.

### 1.2 The verified source is a secondary, stated as one

The formulae and all three constants are verified instead on:

> **Williams, J., Butler, S. F. J. and Wood, M. N. (1961), "The Aerodynamics of
> Jet Flaps", Aeronautical Research Council Reports and Memoranda No. 3304**
> (Ministry of Aviation, H.M.S.O. 1963; previously R.A.E. Report No. Aero. 2646 —
> A.R.C. 22,823), **printed page 5, equation (2)**; jet-reaction convention on
> **printed page 3, §2**.
>
> Filed: `docs/papers/powered_lift_and_ducted_propulsion/williams_butler_wood_1961_arc_rm3304_aerodynamics_of_jet_flaps.pdf`
> — **added at commit `1ae12da5`**, verified by `git log --diff-filter=A` on the
> paper path, which returns `1ae12da5` as the only commit that ever added it.
> Printed p.5 = PDF p.6; printed p.3 = PDF p.4.
>
> *(Provenance correction, recorded rather than silently applied: the brief that
> commissioned this draft cited `ff89c721` for this paper. That commit is
> `ansys VMFL069 LANDS AS NOT A RESULT` and touches no paper. Checked, not
> assumed; the wrong sha is recorded here so the correction is auditable.)*

**This is a SECONDARY source and is labelled as one on every line where it is
cited.** It is a strong secondary — authoritative, RAE, contemporaneous with
Spence, and by the man who ran the British jet-flap programme — but it is a
secondary, and calling it a primary would be a false provenance claim.

**Precedent.** This follows Sanaa's own established remedy for exactly this
shape. Her standing directives of **2026-08-27, §0** ruled that until the
ASME V&V 20 text lands, *every V&V-20 practice cites Dowding 2016 as secondary,
stated as such.* Identical situation — an unobtainable primary, an authoritative
secondary that reproduces it — and identical remedy: **cite the secondary, say
it is a secondary, and record the primary as unobtained with the reason.**

**Record of the unobtained primary:** Spence (1956), Proc. R. Soc. A 238, 46–68 —
**NOT OBTAINED, HTTP 403 from the publisher on all three access paths, 2026-08-30.**
Corroborated as the origin of eq. (2) by ARC R&M 3304 printed p.3, which states
that *"The two-dimensional problem was solved by Spence using a treatment akin to
classical 'mean line' theory, both for ejection from the trailing edge and over a
plain (hinged) flap"* (refs 26, 27 there). If the primary is later obtained, the
formulae below are re-verified against it and this section is superseded by a
dated addendum; the numbers are **not** silently re-attributed.

### 1.3 The source read, verbatim in structure

Read as a **page image** of PDF p.6 at 200 dpi on 2026-08-30 (the `.txt` sidecar
is tesseract OCR of a scanned TIFF, states in its own header that it contains OCR
errors and that equations are especially corrupted, and was **not** used for any
number in this document).

ARC R&M 3304, printed p.5, eq. (2), the whole bracket, with the source's own
sectional-momentum symbol `C_mu'`:

```
    (dCL/dtheta)_inf = [ 4*pi*C_mu' * ( 1 + 0.151*C_mu'^(1/2) + 0.139*C_mu' ) ]^(1/2)

    (dCL/dalpha)_inf = 2*pi * ( 1 + 0.151*C_mu'^(1/2) + 0.219*C_mu' )
```

and eq. (1) immediately above it:

```
    (C_L)_inf = theta * (dCL/dtheta)_inf  +  alpha * (dCL/dalpha)_inf
```

**A third symbol, disclosed:** the source's `C_mu'` (primed) is the **sectional**
momentum coefficient; its unprimed `C_mu` in eq. (3) is the wing-mean coefficient
used for the finite-aspect-ratio factor `F(A, C_mu)`. This case is strictly
two-dimensional, so `C_mu' = C_mu_jet` here and eq. (3) is **not used**. The
distinction is recorded so that no downstream reader imports eq. (3).

### 1.4 GROUPING — THE DIRECTIVE'S FORM IS WRONG AND THE CONSTANTS ARE RIGHT

The directive §1.5 records, as remembered:

```
    dCL/dtau   = 2 sqrt(pi C_mu) (1 + 0.151 sqrt(C_mu) + 0.139 C_mu)      <-- WRONG GROUPING
    dCL/dalpha = 2 pi (1 + 0.151 sqrt(C_mu) + 0.219 C_mu)                 <-- CORRECT
```

Against the page: **the three constants 0.151, 0.139 and 0.219 are correct**, to
the three significant figures the source prints (as `0·151`, `0·139`, `0·219`).
**The grouping of the theta-derivative is not.** In the source the series sits
**inside** the square root together with `4*pi*C_mu'`; the directive places it
**outside**. The alpha-derivative is not square-rooted at all and the directive
writes it correctly. The two derivatives are grouped differently in the source
and share the constant 0.151 — which is precisely the shape a memory error takes.

**This is the finding that most justifies the verification instruction.** A check
that verified only the *constants* would have returned "all three correct" and
frozen a one-signed, monotonically growing bias into the theory gate.

**Consequence, computed to 10 digits** (`derive.py`; the directive's form exceeds
the source's by exactly `sqrt(S)` where `S = 1 + 0.151*sqrt(C_mu_jet) + 0.139*C_mu_jet`):

| `C_mu_jet` | `S` | bias of the directive's form | `CL_theory` at tau=30 deg, **SOURCE** | `CL_theory`, directive's form |
|---|---|---|---|---|
| 0.05 | 1.0407146265 | **+2.0154 %** | **0.4234034434** | 0.4319368082 |
| 0.10 | 1.0616503927 | **+3.0364 %** | **0.6047756775** | 0.6231392095 |
| 0.20 | 1.0953292529 | **+4.6580 %** | **0.8687421542** | 0.9092079797 |
| 0.40 | 1.1511007853 | **+7.2894 %** | **1.2594769538** | 1.3512848267 |

**The SOURCE column is registered. The directive's column is recorded only to
show what was avoided and is never used as a comparand.**

### 1.5 THE C_mu RANGE WORRY IS RETIRED — AND WHY THAT MUST BE WRITTEN DOWN

The source introduces eq. (2) with, verbatim from printed p.5:

> *"The following simple interpolation formulae fit the computed values for
> `c_f/c = 0` (T.E. blowing) at `C_mu'`-values of 1 and 4 and asymptotically as
> `C_mu' -> 0`."*

`c_f/c = 0` is **pure trailing-edge blowing with no flap** — exactly the
configuration registered in §3 below. The sweep's top point, `C_mu_jet = 0.4`,
therefore lies **inside** the fitted range, bracketed below by the `C_mu' -> 0`
asymptote and above by the `C_mu' = 1` anchor. There is no extrapolation in
`C_mu_jet` anywhere in this registration, and no "small-`C_mu`" restriction is
registered as a risk.

**COROLLARY, REGISTERED AS BINDING:** 0.151, 0.139 and 0.219 are **FIT
PARAMETERS, NOT ASYMPTOTIC SERIES COEFFICIENTS.** They must never be
Taylor-expanded, truncated at a chosen order, re-derived, extended, or read as
physics. Any downstream record that treats eq. (2) as a truncated expansion —
including any statement of the form "to first order in `C_mu`" — is wrong on its
face. The formulae are used **whole or not at all**.

### 1.6 THE JET-REACTION CONVENTION USES sin(tau + alpha)

ARC R&M 3304, printed p.3, §2, read as a page image:

> *"The total lift `C_L` on the jet-flap aerofoil represents a considerable
> magnification of the direct jet-reaction lift `C_mu sin(theta + alpha)` from
> the corresponding vertical component of the jet momentum, because of the
> additional pressure lift on the aerofoil."*

and the definition on the same page: `C_mu [ = M_J V_J / q_0 S ]`, which for a
2D section per unit span is the directive's `(rho_j h V_j^2) / (0.5 rho_inf U_inf^2 c)`.

The directive §1.4 is therefore **right in kind** — the theory's `C_L` does
include the jet reaction, so `CL_total = CL_aero + (jet reaction)` is the correct
construction and the theory gate correctly uses `CL_total` — but **wrong in
detail**: it registers `C_mu sin(tau)`, omitting `alpha`.

**Registered:** `CL_total = CL_aero + C_mu_jet * sin(tau + alpha)`.

This is a **definitional** choice, not an uncertainty. It costs nothing to get
right, so it is got right. Quantified at `C_mu_jet = 0.1`, `tau = 30 deg`:

| `alpha` | registered term `C_mu_jet sin(tau+alpha)` | directive's `C_mu_jet sin(tau)` | difference in CL |
|---|---|---|---|
| 0 deg | 0.0500000000 | 0.0500000000 | 0.0000000000 |
| 4 deg | 0.0559192903 | 0.0500000000 | 0.0059192903 |
| 8 deg | **0.0615661475** | 0.0500000000 | **0.0115661475** |

The 8-deg difference of **0.01157 in CL** is **1.9125 %** of
`CL_theory(C_mu_jet=0.1, tau=30 deg, alpha=0) = 0.6047756775`, and **0.7495 %** of
the full theory lift at `alpha = 8 deg`, `CL_theory = 1.5431780085`.

**Additional consequence for gate (b), which is a slope gate and is registered
here because it is not obvious from the CL numbers above:** gate §1.5(b) measures
`dCL/dalpha`. Under the registered convention the jet reaction contributes
`d/dalpha [ C_mu_jet sin(tau+alpha) ] = C_mu_jet cos(tau+alpha)`, which is
**0.0866025404 /rad** at `alpha = 0` and **0.0828364299 /rad** as the
least-squares slope over the registered `alpha ∈ {0, 4, 8} deg`. Under the
directive's alpha-independent convention that contribution is **exactly zero**.
The directive's convention would therefore have biased the measured `dCL/dalpha`
**low by 1.2325 %** of the theory slope `6.7208116310 /rad` — a one-signed bias
inside a ±15 % band, applied to the arm the band is tightest on.

---

## 2. CASE DEFINITION AND DERIVED QUANTITIES (§1.1)

Registered exactly as §1.1 specifies. Every derived value below was recomputed
from the definitions, not copied.

| Quantity | Value | Source |
|---|---|---|
| Section | NACA 0012, blunt-base truncated (§3) | §1.1 |
| `c` | 1.0 m | §1.1 |
| `U_inf` | 10.0 m/s | §1.1 |
| `nu` | 1.0e-5 m²/s (`transportProperties`) | §1.1 |
| `Re_c` | **1.000e+06** (verified: 10 × 1 / 1e-5) | §1.1 |
| `rho_inf`, `rho_j` | equal (incompressible, same fluid); `rhoInf = 1` in `forceCoeffs` | §1.1 |
| `h/c` | 0.005 → `h` = 5.0 mm | §1.1 |
| `tau` | 30 deg = **0.5235988 rad**, deflected toward the pressure side | §1.1 |
| `C_mu_jet` sweep | 0.0, 0.05, 0.1, 0.2, 0.4 | §1.1 |
| `alpha` | 0 deg for the `C_mu_jet` sweep; secondary sweep 0, 4, 8 deg at `C_mu_jet` = 0.1 | §1.1 |

`V_j = U_inf sqrt( C_mu_jet / (2 h/c) )`, verified against
`C_mu_jet = 2 (h/c) (V_j/U_inf)^2`:

| `C_mu_jet` | `V_j` (m/s) | `Re_slot = V_j h / nu` | `M_j` (a = 343 m/s) |
|---|---|---|---|
| 0.0 | 0.000000 | 0 | 0.0000 |
| 0.05 | **22.360680** | 11 180 | 0.0652 |
| 0.10 | **31.622777** | 15 811 | 0.0922 |
| 0.20 | **44.721360** | 22 361 | 0.1304 |
| 0.40 | **63.245553** | 31 623 | **0.1844** |

The directive's rounded values 22.4 / 31.6 / 44.7 / 63.2 m/s are confirmed. All
jet Reynolds numbers are turbulent, so the kOmegaSST closure is applied to a
turbulent jet throughout and no transition model is registered. The highest jet
Mach number is 0.184; the isentropic density correction there is `1 + 0.2 M²`
= 1.0068, i.e. **0.68 %**, which is **registered as a disclosed and ungated
modelling error**, not as an uncertainty channel — the case is solved
incompressibly by construction.

---

## 3. GEOMETRY — THE CHOICES §1.2 LEAVES OPEN, AND WHICH WAS TAKEN

§1.2 requires two choices to be recorded. Both are recorded here with the reason.

### 3.1 Slot placement: **BLUNT-BASE SLOT** (the directive's primary option)

The NACA 0012 is truncated at the trailing edge to a blunt base of height
`h_base = h = 5.0 mm` (0.5 % chord), and **the slot patch is the base segment
itself**. The jet exits at the trailing edge in the direction `tau` below the
chord line. The lower-surface alternative offered by §1.2 is **not** taken.

**Reason, and it is a gate-integrity reason, not a convenience one.** The gated
comparand is `CL_total = CL_aero + C_mu_jet sin(tau + alpha)`, which presumes the
jet reaction is a clean momentum flux through a single patch, separable from the
surface pressure force. With the slot on the base, the `jetSlot` patch area is
unambiguously `h × 1 m` span, its outward normal is unambiguous, and no wall lies
downstream of the slot. With the slot on the lower surface upstream of the TE,
the jet runs over a length of solid surface before leaving, adds a Coanda/wall-jet
contribution to `CL_aero`, and the decomposition into "surface force" plus
"direct jet reaction" is no longer clean — which would make the theory gate's
comparand ambiguous at the level of the very term §1.6 above spends its effort
getting right. The base slot is also what `c_f/c = 0` in the source (§1.5) means:
pure T.E. blowing with no flap.

**Disclosed consequence, and it is the reason for open item O2 in §16:** the
gated section is no longer a sharp-trailing-edge NACA 0012. It carries a 0.5 %-chord
blunt base and therefore a base-drag increment absent from any sharp-TE record.

### 3.2 Domain: **C-MESH**, farfield at **25 c**

**Reason.** §1.3 requires the jet sheet to stay resolved for **≥ 1 c downstream**
and requires a wake refinement box 3 c long. A C-mesh lays grid lines **along**
the wake, so the jet sheet stays aligned with the mesh for the whole wake box; an
O-mesh's radial lines fan out and at 1 c downstream the azimuthal spacing would be
of order 0.1 c, smearing the sheet across one or two cells and destroying the
quantity the gate depends on. The C-topology additionally admits the block
construction in §4.2, in which the 12 cells across the slot **continue downstream
as a dedicated jet-sheet block** — so "the jet sheet is resolved for ≥ 1 c" holds
by construction of the topology rather than by hope.

Farfield radius/extent **25 c** (§1.2's floor; not 30 c, so the cell budget goes
into the wake instead of the far field). Wake outlet at 25 c.

### 3.3 Patches

| Patch | Type | Physical |
|---|---|---|
| `airfoil` | wall | the truncated NACA 0012 surface, upper and lower |
| `jetSlot` | patch | the base segment, `h` = 5 mm, area `h × 1 m` |
| `farfield` | patch | C-boundary + outlet at 25 c |
| `front`, `back` | empty | 2D, one cell thick |

---

## 4. MESH LADDER (§1.3)

### 4.1 Registered as a binding construction rule

**ONE parametric script**, `verification/runs/JF1_jet_flap/mesh/make_jf1_mesh.py`,
takes a single scale factor `s` and emits the whole level. **No level is ever
hand-edited.** The three levels are `s ∈ {1.0000, 1.3693, 1.8708}` applied to
**every cell count and every spacing in every direction** — including the
wall-normal first-cell height, which is **not** held fixed across the ladder (a
ladder that freezes the near-wall spacing is not systematically refined in that
direction and its observed order is not interpretable). `y+ ≤ 1` is a **ceiling**,
not a target, so refining the first cell keeps it satisfied.

An assertion in the script **refuses to emit** a level whose printed metrics
violate any registered constraint. The script prints, and the birth certificate
records, the **actual** counts and ratios; the numbers below are the **planned**
values.

### 4.2 Planned block distribution (C-topology, 2D, one cell thick)

| Block | i (streamwise/tangential) | j (normal) | L1 | L2 | L3 |
|---|---|---|---|---|---|
| upper surface | clustered LE & TE | y+ ladder | 100 × 85 | 137 × 116 | 187 × 159 |
| lower surface | clustered LE & TE | y+ ladder | 100 × 85 | 137 × 116 | 187 × 159 |
| upper wake | TE → 3c fine, → 25c coarse | y+ ladder | 130 × 85 | 178 × 116 | 243 × 159 |
| lower wake | TE → 3c fine, → 25c coarse | y+ ladder | 130 × 85 | 178 × 116 | 243 × 159 |
| **jet-sheet block** (base gap, extended downstream) | as the wake blocks | **across `h`** | 130 × **12** | 178 × **16** | 243 × **22** |
| **planned total cells** | | | **40 660** | **75 928** | **142 086** |

against §1.3's targets of ~40 k / ~75 k / ~140 k. Planned effective 2D refinement
ratios from the totals: `r_21 = sqrt(75928/40660) = 1.3665`,
`r_32 = sqrt(142086/75928) = 1.3680` — both **≥ 1.3** as §1.3 requires.

**`r_21 ≠ r_32`.** Registered consequence: the observed order `p` is computed with
the **non-constant-`r` Roache iterative form**, not the constant-`r` closed form.
The comparator refuses (exit 2) if it is handed a triple whose `r_21` and `r_32`
differ by more than 1 % and the constant-`r` branch was taken.

### 4.3 Near-wall sizing — derived, not assumed

Flat-plate estimate at `Re_c = 1e6`: `Cf(x=c) = 0.0576 Re^-0.2 = 0.003634`,
`u_tau = 0.426281 m/s`, so the `y+ = 1` first-cell height is

> **`y1 = 2.345869e-05 m = 2.346e-05 c`** on L1,
> → 1.713e-05 m on L2 (`y+` = 0.730), 1.254e-05 m on L3 (`y+` = 0.534).

**All three levels satisfy `y+ ≤ 1`** as §1.3 requires, and `y+` is *measured*
post-solve from the real field, not assumed — see the refusal in §8.4.

Turbulent BL thickness at `x = c`: `delta = 0.37 c Re^-0.2 = 2.3345e-02 m`
= **2.33 % chord**.

**A derived requirement §1.3's floor does not state.** §1.3 asks for **≥ 30 BL
layers** at growth **≤ 1.15**. Starting from `y1 = 2.346e-05 m`, 30 layers at 1.15
stack to only **1.02e-02 m = 44 % of `delta`** — the boundary layer would not be
covered. Covering `delta` needs **36 layers at growth 1.15**, or **38 at 1.14**.
The registered L1 normal distribution is a **single uniform growth of 1.1417 over
85 cells** from `y1` to the 25 c farfield, which puts **38 cells inside `delta`**
and satisfies both `≤ 1.15` and `≥ 30` with margin. `≥ 30` is honoured as a
**floor, not a target**; **≥ 36 layers inside `delta` on every level** is
registered as the binding constraint and is asserted by the mesh script.

### 4.4 Slot and wake resolution

- **≥ 12 cells across `h` on L1** → cell size `4.1667e-04 m`; scaled with the
  ladder to **16 (L2)** and **22 (L3)**. The slot is an inlet patch, not a
  channel: there is no wall along the base, so no `y+` constraint applies inside
  it and the 12 cells may be uniform.
- The jet-sheet block carries that same across-sheet count for the **whole 3 c
  wake box**, so the "resolved for ≥ 1 c downstream" requirement is a property of
  the topology. Registered assertion: **≥ 8 cells across the locus of `max|U|` at
  `x/c = 1.0` downstream of the TE**, measured from the solved field and recorded
  on the birth certificate; fewer than 8 is a **mesh defect**, and the row it
  supports is `NOT A RESULT`.
- Streamwise spacing at the TE is matched to the base cell size (4.17e-04 m on L1)
  so the surface and base distributions join without a jump.
- Wake streamwise grading: fine to 3 c, then coarse to the 25 c outlet. A uniform
  3 c box at slot spacing would need ~7 200 streamwise cells and cannot be
  afforded at 40 k; the grading is therefore **registered**, not improvised.

### 4.5 checkMesh gates, per level, and the birth certificate

Registered hard gates, all three levels:

| Metric | Gate |
|---|---|
| max non-orthogonality | **< 65** |
| max skewness | **< 4** |
| negative volumes | **exactly 0** |
| `checkMesh` overall | must print `Mesh OK` |

A level failing any of these is `BLOCKED` and **no solve is launched on it**. A
gated row whose mesh level is `BLOCKED` is `NOT A RESULT`.

**Birth certificate per level**, at
`verification/runs/JF1_jet_flap/mesh/BIRTH_L{1,2,3}.md`, recording: actual cell
count; actual `r` against the level below in each direction; `y+` histogram
(min/max/mean, measured post-solve); layers inside `delta`; cells across `h`;
cells across the sheet at `x/c = 1`; full `checkMesh` quality block; the md5 of
the mesh script and the scale factor `s` used.

---

## 5. BOUNDARY CONDITIONS AND NUMERICS (§1.4)

### 5.1 Turbulence treatment — recorded and fixed across the ladder

`kOmegaSST`, **low-Re, no wall functions in the momentum sense** (`y+ ≤ 1`).
Registered wall set, **identical on all three levels and all runs**:

| Field | `airfoil` | `jetSlot` | `farfield` |
|---|---|---|---|
| `U` | `noSlip` | `fixedValue (V_j cos tau, −V_j sin tau, 0)` rotated with `alpha` | `freestreamVelocity`, `U_inf` = 10 m/s rotated by `alpha` |
| `p` | `zeroGradient` | `zeroGradient` | `freestreamPressure` |
| `k` | `fixedValue 1e-10` | `fixedValue`, §5.2 | `freestream`, `k_inf` |
| `omega` | `omegaWallFunction` | `fixedValue`, §5.2 | `freestream`, `omega_inf` |
| `nut` | `nutLowReWallFunction` | `calculated` | `freestream` |

`k fixedValue 1e-10` is chosen over `kqRWallFunction`, which §1.4 offers as an
alternative: at `y+ ≤ 1` the zero-gradient `kqR` form and the near-zero fixed
value are numerically close, and the fixed value carries no ambiguity about
whether a wall function is active. `nutLowReWallFunction` sets `nut = 0` at the
wall, which is the correct low-Re statement. **Recorded as required by §1.4 and
frozen: `nutLowReWallFunction` + `omegaWallFunction` + `k = 1e-10`.**

**Disclosed:** the `jetSlot` velocity is a **uniform "top-hat" jet** with no
boundary-layer profile on the slot lips, as §1.4 directs. This is a real
modelling simplification: a real slot issues a profile with wall layers, and the
top-hat over-states the momentum near the lips. It is disclosed, not gated.

### 5.2 Jet inlet turbulence — `C_mu_turb = 0.09`, per §0

`k_jet = 1.5 (I V_j)²` with `I = 0.01`;
`omega_jet = sqrt(k_jet) / (C_mu_turb^0.25 * l_j)` with `l_j = 0.07 h = 3.5e-04 m`.

| `C_mu_jet` | `k_jet` (m²/s²) | `omega_jet` (1/s) | `nut_jet/nu` |
|---|---|---|---|
| 0.05 | 7.500000e-02 | **1428.571429** | 5.25 |
| 0.10 | 1.500000e-01 | **2020.305089** | 7.42 |
| 0.20 | 3.000000e-01 | **2857.142857** | 10.50 |
| 0.40 | 6.000000e-01 | **4040.610178** | 14.85 |

**Disclosed choice, not an error in the directive.** The standard mixing-length
form is `l = 0.07 D_h`, and the hydraulic diameter of a 2D slot is `D_h = 2h`, so
the textbook reading would be `l = 0.14 h = 7.0e-04 m` — half the `omega_jet`
above, `nut_jet/nu` doubled (14.85 at `C_mu_jet = 0.1`). §1.4 specifies `0.07 h`
and **`0.07 h` is registered**; the `0.14 h` alternative is recorded here so the
choice is visible. **Registered ungated sensitivity:** one L1 solve at
`C_mu_jet = 0.1` with `l_j = 0.14 h`, reported as a `CL_total` sensitivity, never
as a gate arm. Cost is carried in §12.

### 5.3 Freestream turbulence — **the two branches §1.4 offers are NOT equivalent**

`k_inf = 1.5 (I U_inf)²` with `I = 0.001` → **`k_inf = 1.5000e-04 m²/s²`**.

§1.4 offers two prescriptions for `omega_inf` and asks which was used. They are
**not** interchangeable, and the difference is large:

| Branch | `omega_inf` (1/s) | `nut_inf` (m²/s) | `nut_inf/nu` | `k` surviving 25 c of convection |
|---|---|---|---|---|
| A: `L = 0.1 c`, `omega = sqrt(k)/(C_mu_turb^0.25 L)` | 0.22360680 | 6.708e-04 | **67.08** | 95.1 % |
| B: viscosity ratio `nut/nu = 3` | 5.00000000 | 3.000e-05 | **3.00** | 32.5 % |

**Ratio of `nut_inf` between the two branches: 22.36×.**

**Registered: branch B, `omega_inf = 5.0 1/s`, `nut_inf/nu = 3`.** Reason: branch
A's freestream eddy viscosity of 67 ν exceeds the eddy viscosity through much of
the attached boundary layer at `Re_c = 1e6` and would contaminate the wall layer
the whole low-Re mesh exists to resolve; branch B's 68 % decay of `k` over 25 c is
ordinary and harmless for a fully-turbulent RANS solve. **This is a real decision
with a 22× consequence and it is flagged to the supervisor as open item O3 in
§16** — the directive left the choice open and required it recorded, which is what
this section does, but the size of the gap is worth a supervisor's eye before the
freeze.

### 5.4 Schemes and SIMPLE — as §1.4 registers

```
gradSchemes      : Gauss linear   (cellLimited Gauss linear 1 for k, omega if needed)
div(phi,U)       : bounded Gauss linearUpwind grad(U)
div(phi,k)       : bounded Gauss limitedLinear 1
div(phi,omega)   : bounded Gauss limitedLinear 1
laplacianSchemes : Gauss linear corrected
SIMPLE           : consistent yes; nNonOrthogonalCorrectors 1
relaxation       : p 0.3, U 0.7, k 0.7, omega 0.7  (starting values)
```

**Second order throughout on every gated level.** A first-order feasibility run is
permitted at the feasibility stage only and is **labelled `first-order —
FEASIBILITY ONLY, NOT A RESULT`** in its own log, its filename and its record.
A first-order field may never be graded, quoted, or used as an initial condition
for a gated row without that fact being recorded on the row.

Relaxation factors may be adjusted **only at the feasibility stage** and are then
**frozen and identical across the whole ladder**; a mid-ladder change invalidates
the triple and the row becomes `NOT A RESULT`.

### 5.5 Convergence criteria — residuals AND absolute bounds, both binding

**Every residual criterion has an absolute bound beside it. A run satisfying the
residual criteria but violating any absolute bound is `NOT A RESULT`.**

| Channel | Residual criterion | Absolute bound beside it |
|---|---|---|
| `p` | initial residual < **1e-6** | continuity error `max` < **1e-8** (cumulative and local) |
| `Ux` | < **1e-6** | `max|U|` < **2 × max(V_j, U_inf)** — blow-up guard, see O1 |
| `Uy` | < **1e-6** | as above |
| `k` | < **1e-6** | `k ≥ 0` everywhere; `min(k) > 0` in the jet core |
| `omega` | < **1e-6** | `omega > 0` everywhere |
| `CL` | — | `|dCL| < 1e-4` over the **last 2000 iterations** |
| `Cd` | — | `|dCd| < 1e-5` over the **last 2000 iterations** |
| `nut` | — | `nut/nu` finite and `< 1e5` everywhere (realisability) |

All five residual channels are held to **the same order, 1e-6** — no channel is
tightened 1000× relative to its siblings, per §1.4.

> **ITERATION CAP: 20 000. A run that hits the cap is `NOT A RESULT`, never
> "close enough".**

Those are the registered words. There is no path by which a capped run becomes a
graded row, and no reading of "the residuals were nearly there" that changes it.

### 5.6 Force computation — AND A SILENT-DEFAULT HAZARD VERIFIED IN THE v2606 SOURCE

**The `forceCoeffs` setup §1.4 specifies was checked against what OpenFOAM v2606
on this box actually does with those values, not against what the units imply.**
Source read: `/usr/lib/openfoam/openfoam2606/src/functionObjects/forces/`.
Three findings, one of them silent.

**HAZARD 1 (SILENT, and it is the one that matters) — `Aref` versus the 2D
extrusion thickness.** `forces.C:729` computes the pressure force as
`fP = rhoRef * Sfb[patchi] * (pb - pRef)` using the **actual mesh face-area
vectors `Sf`** — which, on a 2D one-cell-thick mesh, include the z-extrusion
thickness `t_z`. `forceCoeffs.C:164` then divides by `1/(Aref_*pDyn + SMALL)`
where `Aref_` is read **verbatim from the dictionary** (`forceCoeffs.C:313`,
`dict.readEntry("Aref", Aref_)`). OpenFOAM never reconciles the two.

> **Therefore `Aref = c` is correct if and only if the 2D extrusion thickness is
> EXACTLY `t_z = 1.0 m`.** §1.4 specifies `Aref = c` "per unit span" and **nothing
> in the directive pins `t_z`.** Airfoil mesh scripts commonly extrude to a thin
> slab (`0.1 c`, `0.01 m`, one cell of "whatever"); the case would still mesh,
> still run, still converge, and still produce a smooth and entirely wrong `CL`
> and `Cd` — scaled by `1/t_z` — with **no warning of any kind**. The `SMALL`
> guard at `forceCoeffs.C:328` catches only a *missing* or zero value, never a
> *mismatched* one.

**Registered, with an independent cross-check rather than a promise:**

1. `t_z = 1.0 m` **exactly**, and `Aref = c × t_z = 1.0 m²`, `lRef = c = 1.0 m`.
2. The mesh script asserts `t_z == 1.0` and refuses to emit a level otherwise.
3. **The comparator independently measures `t_z` from the solved case and does not
   take the script's word for it:** the `jetSlot` patch area is `h × t_z`, so
   `area(jetSlot)` **must equal `0.005 m²` to 1e-9**, read from `checkMesh` /
   `patchIntegrate` output. **If it does not, every `CL` and `Cd` in the case is
   scaled wrong and the comparator refuses (exit 2); all rows are `NOT A RESULT`.**
   The slot patch is the ideal probe because its area depends on `t_z` and on
   nothing else that is in question.

**HAZARD 2 (loud, but a real gap in §1.4's dictionary) — `rho` must be set to
`rhoInf`, and §1.4 does not say so.** `forces.C:539` and `:578` default
`rhoName_` to **`"rho"`**, not `"rhoInf"`; `rhoInf` is read into `rhoRef_` only
inside `if (rhoName_ == "rhoInf")` (`forces.C:638`). §1.4 lists `rhoInf = 1` but
never lists `rho rhoInf`. Written literally, the function object would look for a
`rho` **field**, not find one in an incompressible `simpleFoam` case, and
`FatalError` at `forces.C:176–180` — a loud failure at zero compute, not a silent
wrong number, but a failure nonetheless. **Registered: `rho rhoInf;` is a
required entry.**

**HAZARD 3 (same lesson, different quantity) — `phi` is VOLUMETRIC here.** In
incompressible OpenFOAM `phi` has units m³/s, not kg/s. §1.5's mass-flow check is
worded `rho h V_j`. With `rho = 1` and `t_z = 1 m` the two numbers coincide
**numerically**, which is exactly how a units error survives inspection.
**Registered in the units the solver actually produces:**
`Σ phi over jetSlot [m³/s]` compared against `V_j · h · t_z [m³/s]`, both sides
computed in the same script in the same units (§7.4).

**Registered `forceCoeffs` dictionary:**

```
type            forceCoeffs;
patches         (airfoil);          // jetSlot is NOT a wall and is NOT included
rho             rhoInf;             // HAZARD 2 — required, absent from §1.4
rhoInf          1;
magUInf         10;
lRef            1.0;                // = c
Aref            1.0;                // = c * t_z, valid ONLY because t_z == 1.0 m
CofR            (0.25 0 0);
liftDir         (-sin(alpha)  cos(alpha) 0);
dragDir         ( cos(alpha)  sin(alpha) 0);
```

`patches (airfoil)` only: `jetSlot` is an inlet, and including it would put the
jet's own pressure force into `CL_aero`, double-counting against the explicit
reaction term of §1.6. In v2606 `liftDir`/`dragDir` are mapped onto a coordinate
system (`forceCoeffs.C:293`, `setCoordinateSystem(dict, "liftDir", "dragDir")`,
with `dragDir → e1`, `sideDir → e2`, `liftDir → e3` at `:224–226`); the legacy
entry names are still accepted in v2606 and all of `liftDir`, `dragDir` and
`CofR` are given explicitly so none is taken from a default.

**`CL_aero` from `forceCoeffs` is the pressure + viscous force on the `airfoil`
wall patch only. The jet momentum flux through `jetSlot` is NOT a wall force and
is NOT in it.** Both are reported on every row:

```
    CL_aero   = forceCoeffs Cl on patch `airfoil`
    CL_total  = CL_aero + C_mu_jet * sin(tau + alpha)          [§1.6]
```

**The theory gate uses `CL_total`**, because the source's `C_L` includes the
direct jet reaction (§1.6). `CL_aero` is reported alongside on every row and is
never substituted for `CL_total`.

---

## 6. STAGING — FEASIBILITY → PHYSICS → GATE

Standing doctrine. No stage may be skipped and no later stage may start before
the earlier one has produced its artefact.

| Stage | What runs | What it produces | Gated? |
|---|---|---|---|
| **F — feasibility** | mesh script at all three `s`; `checkMesh`; one L1 first-order solve at `C_mu_jet = 0.1`, 2000 iterations | three birth certificates; proof the constraint set of §4 is simultaneously satisfiable; a converging first-order field | **No.** Nothing here is a result. |
| **P — physics** | one L1 second-order solve at `C_mu_jet = 0.1`, `alpha = 0`, to the full §5.5 criteria | jet-sheet trajectory; separation state; `y+` measured; mass-flow closure measured; relaxation factors fixed for the ladder | **No.** Diagnostic only. |
| **G — gate** | everything in §7, comparator run per §8 | the graded rows | **Yes.** |

**F is a real gate on the programme, not a formality.** §4 imposes `y+ ≤ 1`,
`≥ 36` BL layers at growth `≤ 1.15`, `≥ 12` cells across `h`, `checkMesh` limits
and ~40 k cells **simultaneously**. §4.2 shows a block layout that meets them on
paper. **If the script cannot meet them in fact, that is a stage-F finding and
the answer is `BLOCKED`, reported with the binding constraint named — the
constraints are NOT quietly relaxed to let the programme continue.**

---

## 7. GATES (§1.5)

All gates below are registered **before** any solve. `PASS` requires the row to be
inside the registered band **and** the row to have survived §8's completion rule
and, where applicable, §7.2's triple gating.

### 7.1 Gate V — regression against our own gated unblown NACA 0012 records

`C_mu_jet = 0.0`, `alpha ∈ {0, 4, 8} deg`, L1.

> ## GATE V IS `BLOCKED`. ITS PREMISE IS FALSE.
>
> §1.1 states, of the NACA 0012 baseline: *"already gated on file for unblown
> CL-alpha and Cd; reuse those records as the V column"*, and §1.5 gates V against
> *"the on-file gated CL-alpha slope and Cd within their existing bands"*.
>
> **A repository-wide search establishes that no such record exists.** There is no
> gated unblown NACA 0012 lift-curve-slope record in this lab, and no surviving
> gated `Cd` record either. The four nearest artefacts, each checked and each
> disqualified for a stated reason:
>
> | Artefact | What it actually is | Why it cannot serve as V's comparand |
> |---|---|---|
> | `models/curriculum/results/naca0012_wing.json` | `Cd = 0.02229` at **zero lift** (`CL = −0.000795`, i.e. `alpha = 0`), band ±30 % vs Abbott & von Doenhoff (1959) **section** data `Cd = 0.009`; verdict `TREND ONLY`, 148 % off | **Single alpha — no slope at all.** And its verdict was **overturned**: `verification/campaign/W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md` finds four independently regenerated meshes at the same nominal resolution give `Cd` = **0.009454, 0.009605, 0.010630, 0.012052** — range 2.5987e-03, a **21.6 % spread** — enough to flip the ±30 % verdict on mesh-generation noise alone; the published mesh is the **maximum** of the four and the only one outside the band. Its grid-convergence claim was separately ruled **`NOT A RESULT`** (`verification/campaign/LADDER_RECIPE_RULING_2026-08-25.md`). It is also scored on a **planform-area basis against section data**, a basis mismatch the record itself notes. |
> | `cases/dafoam/ladder-a/A1_naca0012_incompressible.{md,json}` | `CL = 0.49877`, `CD = 0.02091` at a single `alpha = 5.139 deg`; Spalart–Allmaras, `DASimpleFoam`, **4 032 cells** | An **adjoint FD-vs-analytic verification artefact**, not an aerodynamic gate. `docs/VALIDATION_INVENTORY.md:364` classifies it as internal-FD adjoint verification in the lab's own words. Single alpha, different closure, no external reference, no band. |
> | `cases/tmr/naca0012_status.json`, `verification/campaign/W1_TMR_NACA0012_DISPOSITION.md` | one converged rung only: `alpha = 10 deg`, 3 584 cells, `Cl = 1.11644`, `Cd = 0.00449` | The record **itself refuses the comparison** — *"a single coarse rung supports no comparison claim and none is made"* — and the 9-rung item was **dismissed as unaffordable**. Alpha 0 and 15 never reached steady state. |
> | F5b pitching NACA 0012 (`CL`/`CM`) | the repo's nearest thing to a `CL(alpha)` curve | `docs/VALIDATION_INVENTORY.md:306`: its Physics and Gate rows are literal `[to be completed]` placeholders — **"NO GATE EXISTS"**, the audit's own words. |
>
> **`F2_transonic_naca0012.md` is a shock-position gate at `M = 0.8` and is not a
> lift-slope record; it is also flagged degenerate in its own file.**
>
> **THEREFORE: GATE V AS §1.5 WORDS IT HAS NO COMPARAND AND IS REGISTERED
> `BLOCKED`.** This is not softened and it is not worked around. The directive's
> premise is false as a matter of fact, and this lane does not invent a comparand
> to rescue it. **The supervisor must rule (open item O4) between:**
>
> **(a)** name a different existing gated record this lane did not find;
> **(b)** re-scope V to a **first-principles / external-datum** band registered
> here before the freeze — thin-airfoil `dCL/dalpha = 2 pi /rad` ± a registered
> tolerance for the slope, and `Cd` against a **published** NACA 0012 datum cited
> as an external reference with its own provenance — which makes V a *new* gate,
> not a regression, and it must be labelled as one; or
> **(c)** declare V `BLOCKED`, drop it, and gate the case on G and THEORY alone.
>
> **Under (a) the record must be named by absolute path with its `CL`,
> `dCL/dalpha` and `Cd` values, its bands, its `Re`, turbulence model, mesh and
> solver, before the freeze.**
>
> **CORRECTION, DISCLOSED RATHER THAN PATCHED SILENTLY (2026-08-30, pre-compute,
> pre-freeze; legal under rule 2's pre-compute amendment clause — the condition is
> that no run root `verification/runs/JF1_jet_flap/` exists and no compute has
> occurred, checked at the time of writing).** As first committed at
> `34f51b78`, the row above stated the four-mesh `Cd` range as "0.00800 to
> 0.01205" and asserted the artefact was a "3D finite wing". **Both were wrong
> and are struck.** The 0.00800 figure belongs to W3's *refinement* series
> (0.012052 → 0.010406 → 0.008479 as cells increase, `W3:43`), a different
> quantity, and I mislabelled it as the same-nominal-resolution set; the correct
> set is `W3:114` and the range is 0.009454–0.012052. The "3D finite wing" claim
> was **asserted without evidence** — the record nowhere states dimensionality,
> and what it does state is a planform-area basis against section data. The
> load-bearing number, the **21.6 % spread, was and is correct** and is confirmed
> arithmetically (0.012052 − 0.009454 = 2.598e-03, `W3:37`), so the conclusion —
> gate V `BLOCKED` — is unaffected. Recorded here because a wrong number in an
> evidentiary table is a defect whether or not it changes the verdict, and
> because this lab's own precedent (`e779bdc7`) is to disclose such a repair
> inline rather than quietly overwrite it.
>
> **A caution that bears directly on option (b) and on gate G.** The W3 finding
> above — 21.6 % `Cd` spread on this same body from mesh-generation noise alone,
> at fixed nominal resolution — is a measured statement about how fragile a NACA
> 0012 `Cd` is to *how the mesh was built*. It is the strongest available
> justification for §4.1's binding rule that all three levels come from **one
> parametric script at three scale factors and are never hand-edited**, and it is
> why `LADDER_RECIPE_RULING_2026-08-25.md` ruled a recipe-forked ladder
> `NOT A RESULT`. Any `Cd` band registered under option (b) must be wide enough
> to survive that noise, or it is a gate that measures the mesh generator.

**Disclosed defect in this gate as §1.5 words it, independent of the above.** The
geometry registered in §3.1 is a **blunt-base** NACA 0012 with a 0.5 %-chord base.
Any sharp-TE record is not the same body. `CL-alpha` slope is nearly unaffected by
a 0.5 % base; **`Cd` is not.** A base of `h/c = 0.005` with a base pressure
coefficient in the ordinary range `Cp_base ∈ [−0.1, −0.3]` adds

| `Cp_base` | `ΔCd` | as % of NACA 0012 `Cd ≈ 0.008` at `Re = 1e6` |
|---|---|---|
| −0.10 | 0.00050 | **6.2 %** |
| −0.20 | 0.00100 | **12.5 %** |
| −0.30 | 0.00150 | **18.8 %** |

which can plausibly exceed the band of a sharp-TE `Cd` record. **Registered
resolution, subject to O2:** gate V is **split**. The `CL-alpha` **slope** arm is
gated against the named record. The `Cd` arm is **reported with the measured base
`Cp` and the derived base-drag increment stated beside it**, and is gated only
against a band the supervisor registers **for a blunt-base body** at the freeze —
a `Cd` arm gated against a sharp-TE band would be a gate that this geometry is
guaranteed to fail for a reason that is not a defect. **Widening or re-scoping a
band is a gate decision and is the supervisor's, not this lane's.**

### 7.2 Gate G — Roache triple on `CL_total`, `C_mu_jet = 0.1`, `alpha = 0`

Three levels L1/L2/L3, same everything but the mesh scale factor `s`.

| Registered quantity | Value |
|---|---|
| Comparand | `CL_total` (not `CL_aero`) |
| Observed order `p` | **`p ∈ [1.3, 2.5]`** |
| `GCI_fine` | **< 3 %** |
| Factor of safety | **`Fs = 1.25`** |
| `r_21`, `r_32` | measured from the actual cell counts, printed on the row |

**Rule 5 gating, and its direction, registered in full:**

1. If **any level** is not iteratively converged (§5.5) or not plateaued →
   the row is **`NOT A RESULT`**.
2. If the triple is **`DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT`** → the
   row is **`NOT A RESULT`**, and the value, both triples and the orders are
   printed beside it.
3. Only if the triple is **`CONVERGING`** does the row become **`PASS`** inside
   the registered band, else **`GATE FAIL`**, with the GCI printed.

> **THE GATE CAN ONLY TURN A `PASS` OR A `GATE FAIL` *INTO* `NOT A RESULT`.
> IT CAN NEVER TURN A `NOT A RESULT` INTO A `PASS` OR A `GATE FAIL`, IN EITHER
> DIRECTION, FOR ANY REASON.**

> **NO GCI IS EVER QUOTED WHEN THE THREE VALUES ARE NOT MONOTONE.** The
> comparator does not compute one; it prints the non-monotone triple and the
> label instead.

`GCI_fine = Fs × |eps_21| / (r_21^p − 1)` at `Fs = 1.25`, with `eps_21` the
relative difference between L1 and L2, in the non-constant-`r` form (§4.2).

### 7.3 Gate THEORY — `CL_total` against ARC R&M 3304 p.5 eq. (2)

**Source form only (§1.4). The directive's grouping is never used as a comparand.**

**Arm (a) — `C_mu_jet` sweep at `alpha = 0`, `tau = 30 deg`, on L1:**

`CL_theory = tau × (dCL/dtheta)_inf` with `tau = 0.5235988 rad` and
`(dCL/dtheta)_inf = [ 4 pi C_mu_jet ( 1 + 0.151 sqrt(C_mu_jet) + 0.139 C_mu_jet ) ]^(1/2)`:

| `C_mu_jet` | **`CL_theory` (REGISTERED)** | band | in the gate? |
|---|---|---|---|
| 0.05 | **0.4234034434** | `|CL_total − CL_theory| / CL_theory ≤ 15 %` | **yes** |
| 0.10 | **0.6047756775** | `≤ 15 %` | **yes** |
| 0.20 | **0.8687421542** | `≤ 15 %` | **yes** |
| 0.40 | 1.2594769538 | — | **NO — reported OUTSIDE the gate as the theory-departure exhibit** |

§1.5 words the band as "`≤ 15 %` at `C_mu ≤ 0.1`" while listing three points
`{0.05, 0.1, 0.2}`. **Registered reading: the 15 % band applies to all three
listed points**, since a gate stated for a point set must cover the point set; the
`C_mu_jet = 0.2` row is gated at 15 % like the others. Recorded as a reading of an
ambiguity, so that it is not later re-read to whichever answer helps.
`C_mu_jet = 0.4` is **outside the gate by registration** and is reported as the
departure exhibit — its `CL_theory` is quoted only there.

**DISCLOSED, as §1.5 demands: `tau = 30 deg` is at the edge of "small".** The
theory is a thin-airfoil, inviscid, small-deflection linearisation. See §11 for
what this registration predicts about it.

**Arm (b) — `dCL/dalpha` at `C_mu_jet = 0.1` from the alpha sweep, on L2:**

`(dCL/dalpha)_inf = 2 pi ( 1 + 0.151 sqrt(C_mu_jet) + 0.219 C_mu_jet )`
= **6.7208116310 /rad = 0.1173002851 /deg** at `C_mu_jet = 0.1`.

Measured: least-squares slope of `CL_total` over `alpha ∈ {0, 4, 8} deg`, in
**radians**, on L2. Band: `|slope_sim − 6.7208116310| / 6.7208116310 ≤ 15 %`.

The registered `sin(tau + alpha)` convention (§1.6) contributes
**0.0828364299 /rad** to the measured slope — 1.2325 % of the theory value. Under
the directive's `sin(tau)` convention that contribution would be zero and this arm
would carry a one-signed 1.23 % bias. This is why §1.6 is registered.

### 7.4 Physicality checks — every one of them is binding

| Check | Criterion | Failure |
|---|---|---|
| **Jet mass flow** | `\|Σ phi over jetSlot\| ` vs `rho h V_j`, per unit span: relative mismatch **≤ 0.5 %** | **> 0.5 % = mesh/BC defect.** The row is `NOT A RESULT`. |
| Continuity closure | global and local continuity error `< 1e-8` | `NOT A RESULT` |
| `k`, `omega` realisability | `k ≥ 0`, `omega > 0`, `nut/nu < 1e5` everywhere | `NOT A RESULT` |
| `y+` measured | `max(y+) ≤ 1` on `airfoil`, measured from the solved field | `NOT A RESULT` |
| Jet-sheet resolution | ≥ 8 cells across the `max\|U\|` locus at `x/c = 1` | `NOT A RESULT` |

The jet mass-flow check is registered with `rho = 1` and both sides computed in
the same units in the same script; `Σ phi` is taken from `patchFlowRate` /
`surfaceFieldValue` on `jetSlot` at the final time.

**Degenerate at `C_mu_jet = 0.0`:** `V_j = 0` makes both sides zero and the
relative mismatch `0/0`. Registered: at `C_mu_jet = 0.0` the check is **`N/A —
not run`, recorded as `N/A`, never as `0.0 %` and never as a pass.** A zero
mismatch reported from a zero-over-zero is exactly the false zero rule 3 exists
to forbid. See also open item O1.

### 7.5 Structure metrics — REPORTED, NEVER GATED

Reported on every row and gated on none: jet-sheet trajectory (locus of `max|U|`
downstream, `x/c` = 0.25, 0.5, 1.0, 2.0, 3.0); upper-surface separation (yes/no
and `x/c` of the separation point from `wallShearStress` sign change);
`Cp` distribution, blown vs unblown, at every `C_mu_jet`.

**These are reported and are never gated, and no row's verdict may cite them.**
A discrepancy printed here is a real discrepancy and is not annotated as
non-binding beyond the fact that it is not a gate arm.

---

## 8. THE COMPARATOR — REFUSALS, PLANTS AND THE COMPLETION RULE

Path: `verification/runs/JF1_jet_flap/analyse_jf1.py`. Frozen at the freezing
commit; its md5 is recorded in §15 at freeze time and verified against the
committed blob before grading, per rule 2.

**The comparator REFUSES (exit 2) rather than degrades.** There is no path in it
that emits a number when a precondition fails.

### 8.1 Rule 4 — the strict completion rule, IN FULL, as a registered refusal

A run is done **only if every one of the following holds**. Failing **any** clause,
the run is **not done**, the comparator **refuses (exit 2)**, and the row it would
have supported is **`NOT A RESULT`**:

1. **`rc = 0`** — the solver's own return code, captured **inside** the wrapper
   (§9.2), never the launcher's.
2. **An `End` line** is present in `log.simpleFoam`.
3. **Last time written == `endTime`.**
4. **Fields present at `endTime`**: `U p k omega nut` (this is an incompressible
   isothermal case; the thermal family's `T alphat p_rgh` do not exist here and
   are **not** required — the clause is the *family's field list*, and this
   family's list is the one just named).
5. **`ExecutionTime` line count == `endTime`** (one per outer iteration).
6. **THE AGE GUARD — every field at `endTime` is NEWER than the case's own
   `0/U`.** `0/U` is touched last at launch and therefore dates the run that was
   allowed to produce the answer. (The thermal families use `0/T`; this family
   has no `T`, so `0/U` is the registered age datum and the wrapper touches it
   last at launch — §9.2.)

**A pre-launch guard REFUSES to start a case whose run directory already contains
`0/` or any time directory.** A restart into a populated directory is not a run;
it is an answer of unknown parentage.

### 8.2 Rule 3 — the planted zero, proven through the real reader

Every zero this comparator can report is proven visible-when-non-zero, through
**the real code path**, before any grading. Refusal on any limb.

**Plant 1 — the `CL` reader.** `PLANT_CL = 1.234e-03`. A byte-level copy of a real
completed case is made; the `Cl` column of `postProcessing/forceCoeffs*/*/coefficient.dat`
is perturbed **by line index** at the final time by exactly `PLANT_CL`; the
**real, unmodified** `read_cl()` is run on the copy. **Required:**
`|CL_planted − CL_clean − PLANT_CL| < 1e-9`. If the reader cannot see the plant,
the comparator **refuses** and reports `NOT A RESULT` — a `CL` of any value from a
reader not shown able to see a change is not evidence.

**Plant 2 — the jet mass-flow reader (the check whose expected answer IS zero).**
A known **2.000 %** error is planted into the `jetSlot` `phi` sum on a copy; the
real checker must report **2.000 % ± 1e-6** *and* must **flag** it (`> 0.5 %`).
A checker that reports 0.0 % on the planted case has not been shown able to see a
non-zero and its 0.0 % on the real case is **not evidence**.

**Plant 3 — the theory-difference channel.** A deliberately wrong `CL_total` is
fed in; the reported relative difference must change by the corresponding amount.
A difference channel that reports the same number for two different inputs is not
a difference channel.

**Fatal-clause control — one mutation limb per completion clause of §8.1.** Six
limbs. Each mutates exactly one clause on a copy (non-zero `rc`; `End` line
removed; last time ≠ `endTime`; one field deleted; one `ExecutionTime` line
removed; **`0/U` touched *after* the `endTime` fields, to trip the age guard**)
and **requires the comparator to refuse.** A limb that does not produce a refusal
means that clause is not enforced and the whole comparator is **`NOT A RESULT`**
until it is.

All plant and mutation outputs are written to
`verification/runs/JF1_jet_flap/artefacts/plant_control_<date>.txt` and are
**preserved**; a number whose artefact is gone is not a result.

### 8.3 Verdict emission

The comparator emits **only** the six words of rule 1 — `PASS`, `GATE REACHED`,
`GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`. It has no other verdict string
and no adjectives. A row is one word plus its value, interval, chip and
uncertainty channels. **There is no softer word available to it.**

### 8.4 Registered refusals — the complete list

The comparator refuses (exit 2) if: any §8.1 clause fails; any §8.2 plant is
invisible; any §8.2 mutation limb fails to refuse; a triple is handed to the
constant-`r` branch with `|r_21 − r_32|/r_21 > 1 %`; a GCI is requested on a
non-monotone triple; `max(y+) > 1` measured; the jet mass-flow mismatch exceeds
0.5 %; the frozen-file md5 does not match the committed blob; the iteration cap
was hit; or any absolute bound of §5.5 is violated.

---

## 9. EXECUTION PROTOCOL

### 9.1 Run root

`verification/runs/JF1_jet_flap/` — outputs live under `verification/runs/`, never
beside the prose describing them. **It does not exist yet and this draft does not
create it.**

### 9.2 The wrapper — `rc` captured INSIDE it, never around a `setsid` line

```bash
#!/bin/bash
# JF1 solver wrapper. rc is captured INSIDE this script.
CASE_DIR="$1"; CASE_ID="$2"
cd "$CASE_DIR" || exit 64
mkdir -p artefacts
touch 0/U                                   # age datum, touched LAST at launch (8.1 clause 6)
decomposePar -force        > log.decomposePar 2>&1 || exit 65
mpirun -np 4 simpleFoam -parallel > log.simpleFoam 2>&1
RC=$?                                       # <-- the SOLVER's rc, inside the wrapper
reconstructPar -latestTime > log.reconstructPar 2>&1
printf 'solver_rc=%s\nend=%s\ncase_id=%s\nnote=exit-status-of-simpleFoam-itself\n' \
    "$RC" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$CASE_ID" \
    > "artefacts/RUN_STATUS.${CASE_ID}.txt"
exit "$RC"
```

**`RC=$?` is on the line immediately after the solver, inside the wrapper.
It is NEVER placed around a `setsid` line: `setsid timeout <cmd>` returns 0 for
every outcome, so an `rc` captured outside it reads 0 whatever happened.**

### 9.3 STATUS at exit, at a path the queue runner cannot occupy

`scripts/queue_runner.py` **unconditionally truncates two files in the launch
cwd**: `cwd / f"STATUS.{case_id}"` (line **496**) and `cwd / "launcher.queue.out"`
(line **497**), the latter **at argv start** by `> '{out}'` in the launch string.
Its own comment (lines ~490–494) states that its `STATUS` file records **the
launch argv's exit status — an infrastructure record — and never claims the
solver's rc**.

**Registered: this case's status is written to
`artefacts/RUN_STATUS.<case_id>.txt`, which is neither of those two paths and
which the runner never touches. Rule 4's `rc = 0` clause is read from that file
and from `log.simpleFoam`, never from `STATUS.<case_id>`.**

### 9.4 Deterministic decomposition, with the seed as a required field

| Field | Value |
|---|---|
| `numberOfSubdomains` | **4** |
| `method` | **`hierarchical`** — `n (4 1 1)`, `delta 0.001`, `order xyz` |
| `DECOMP_SEED` | **20260830** (exported by the wrapper as `SCOTCH_RANDOM_SEED` and recorded on every row) |
| decomposition digest | md5 of the sorted per-processor cell counts, recorded per level |

`hierarchical` is deterministic by construction and consumes no seed; the seed is
nevertheless **a required, recorded field on every row**, exported into the
environment, so that (i) the field can never be silently absent, and (ii) any
later switch to a seed-consuming method inherits a pinned value rather than a
default. **Registered assertion:** the decomposition digest for a given level is
**identical** across every run on that level; a digest change invalidates the
comparison and the affected rows are `NOT A RESULT`.

### 9.5 Artefact preservation

Preserved and never deleted: `log.*`, `artefacts/RUN_STATUS.*`, `postProcessing/`,
the final time directory, the birth certificates, the plant-control outputs, the
mesh script and its md5. **A number whose artefact is gone is not a result.**

---

## 10. RUN MATRIX

| # | Stage | `C_mu_jet` | `alpha` | Level | Serves |
|---|---|---|---|---|---|
| F1–F3 | F | — | — | L1, L2, L3 mesh + `checkMesh` | birth certificates |
| F4 | F | 0.1 | 0 | L1, **first order, labelled** | feasibility only |
| P1 | P | 0.1 | 0 | L1 | physics/diagnostic, fixes relaxation |
| G1 | G | **0.0** | 0 | L1 | map point **and** gate V `alpha=0` |
| G2 | G | 0.05 | 0 | L1 | map + THEORY (a) |
| G3 | G | **0.1** | 0 | L1 | map + THEORY (a) + **triple L1** |
| G4 | G | 0.2 | 0 | L1 | map + THEORY (a) |
| G5 | G | 0.4 | 0 | L1 | map + **departure exhibit, outside the gate** |
| G6 | G | 0.1 | 0 | **L2** | **triple L2** + alpha-sweep `alpha=0` |
| G7 | G | 0.1 | 0 | **L3** | **triple L3** |
| G8 | G | 0.1 | 4 | L2 | THEORY (b) |
| G9 | G | 0.1 | 8 | L2 | THEORY (b) |
| G10 | G | 0.0 | 4 | L1 | gate V — **CONDITIONAL: runs only if the supervisor resolves O4 via option (a) or (b). Under option (c) these two rows are not run.** |
| G11 | G | 0.0 | 8 | L1 | gate V — **CONDITIONAL, as G10** |
| S1 | ungated | 0.1 | 0 | L1, `l_j = 0.14 h` | §5.2 sensitivity, reported never gated |

Reuse is explicit: G3 is both the `C_mu_jet = 0.1` map point and the triple's L1;
G6 is both the triple's L2 and the alpha sweep's `alpha = 0`; G1 is both the
unblown map point and gate V's `alpha = 0`. **A row is run once and cited by every
gate it serves; it is never re-run to be counted twice, and never counted twice
without being run.**

---

## 11. PRE-REGISTERED EXPECTATION — WHERE AND HOW THIS GATE WILL FAIL IF IT FAILS

Registered **before** any solve. A predicted failure that then materialises is the
strongest result form this lab produces; a failure discovered after the solve is
just a failure.

### 11.1 The four error sources, ranked largest first

**1. THE `tau = 30 deg` LINEARISATION — DOMINANT AND IRREDUCIBLE.**
This is the one that will decide the theory gate. Note carefully what kind of
error it is: **within the theory, `CL` is exactly linear in `theta`** — eq. (1) is
`(C_L)_inf = theta (dCL/dtheta)_inf + alpha (dCL/dalpha)_inf`, with the derivative
independent of `theta`. So writing `CL_theory = tau × (dCL/dtau)` introduces **no
extrapolation error at all inside the theory**. The error is **MODEL-FORM**: the
question is whether the thin-sheet, small-slope, linearised-boundary-condition
assumptions under which eq. (2) was derived survive at a 30-degree deflection on
a 12 %-thick section.

A kinematic floor on the size of it: `tau = 0.5235988` rad against
`sin(tau) = 0.5000000` — **4.7 %** — before any jet-sheet decay, any entrainment,
any viscous loss along the sheet, and before the 12 % thickness of a NACA 0012 is
set against the flat plate of the theory. **This cannot be quantified a priori**
and this registration does not pretend to. It is registered as the expected
direction and mechanism, not as a number.

**Registered expectation:** if the theory gate fails, it fails **here**, it fails
**worse at larger `C_mu_jet`** (a stronger sheet turns further and departs further
from the linearised sheet condition), and the simulated `CL_total` is expected to
fall **below** theory, since every neglected mechanism — sheet decay, entrainment,
thickness, viscous loss — removes lift rather than adding it.

**2. THE JET-REACTION CONVENTION — 8.3 % OF `CL_theory` AT `alpha = 8 deg`, AND
FREE TO GET RIGHT.** The registered term `C_mu_jet sin(tau + alpha)` is
**0.0615661** at `alpha = 8 deg`, `C_mu_jet = 0.1`, i.e. **10.18 %** of
`CL_theory(alpha=0) = 0.6047757`; the directive's `sin(tau)` form gives
**0.0500000**, i.e. **8.27 %**. Fixed by §1.6 at zero cost. Residual after the
fix: **zero** — it is a definition, not an uncertainty.

**3. THE FORMULA GROUPING — 3.0 % AT THE GATE POINT, NOW FIXED.**
The directive's grouping is high by `sqrt(S)`: **+2.02 % / +3.04 % / +4.66 %** at
`C_mu_jet = 0.05 / 0.1 / 0.2`. Fixed by §1.4. Residual after the fix: **zero**.
Had it not been caught, it would have consumed a fifth of the ±15 % band at
`C_mu_jet = 0.2`, in one direction, invisibly.

**4. THE `C_mu` INTERPOLATION ERROR — NEGLIGIBLE OVER THIS SWEEP.**
Retired by §1.5: the sweep lies inside the range the formulae were fitted on, for
exactly this configuration (`c_f/c = 0`, pure T.E. blowing), bracketed by the
`C_mu -> 0` asymptote and the `C_mu = 1` anchor.

### 11.2 What a failure means and what it does not

A `GATE FAIL` on the theory arm is a statement about the **linearised theory at
30 degrees**, not about the solver, the mesh or the closure — **provided** gate G
(the triple) is `CONVERGING` with `GCI_fine < 3 %` and every §7.4 physicality
check has passed. If gate G is not `CONVERGING`, the theory row is `NOT A RESULT`
and says nothing about the theory at all. **The order of operations is rule 5's
and is not negotiable at reporting time.**

---

## 12. COST (§1.6), IN CORE-MINUTES

Unit: **core-minutes = wall seconds × ranks ÷ 60**, ranks = 4 (§9.4).
§1.6's per-solve estimates are adopted: **L1 ~10, L2 ~25, L3 ~60 core-min.**

| Item | Runs | core-min each | core-min |
|---|---|---|---|
| F1–F3 mesh generation + `checkMesh`, three levels | 3 | 1.5 | **4.5** |
| F4 L1 first-order feasibility, 2000 iterations | 1 | 4 | **4.0** |
| P1 L1 second-order physics/diagnostic | 1 | 10 | **10.0** |
| G1–G5 `C_mu_jet` map, L1 (5 points) | 5 | 10 | **50.0** |
| G6, G7 triple L2 + L3 (**L1 reused from G3**) | 1 + 1 | 25, 60 | **85.0** |
| G8, G9 alpha sweep L2 (**`alpha=0` reused from G6**) | 2 | 25 | **50.0** |
| G10, G11 gate V (**`alpha=0` reused from G1**) — **CONDITIONAL on O4** | 2 | 10 | **20.0** |
| S1 mixing-length sensitivity, L1, ungated | 1 | 10 | **10.0** |
| | | **subtotal** | **233.5** |
| Named reserve: **one** L3 re-run after a completion-rule refusal | — | 60 | **60.0** |
| | | **TOTAL against the cap** | **293.5** |

> **REGISTERED CAP: 300 core-minutes for the primal family**, as §1.6 sets it.
> Slack against the cap: **6.5 core-min (2.2 %)**.

**THE CAP IS A RUNAWAY GUARD, NOT A MONEY-SAVING STOP — and the distinction is
registered because the two look identical at the moment a run is killed.**

Sanaa's cost-lift directive is recorded verbatim at **`docs/LAB_STATE.md:712`**,
under the heading at `:706`, and reads in relevant part: *"I want the three teams
to forget about cost constraints for now... So no team stops anything in the name
of saving compute."* **She lifted constraints, not measurement.** The operational
reading — that caps become runaway guards rather than authorisation ceilings, and
that costing and calibration are unchanged — is **the chief's recorded reading,
cited here as a reading and not as her words**, and is correctable by her.

Registered consequence for this case:

- A run that exceeds its per-solve estimate by more than **2×** is **stopped for
  investigation**, because a 2× overrun means something is wrong — a stalled
  solve (a row over 3600 wall s is a stall), a runaway, contention, a mesh defect
  — **not** because compute is being conserved. The stop is a diagnostic action
  and is recorded as one, with the cause named.
- **No row of this programme is ever abandoned, and no gate ever softened, in the
  name of saving compute.** If the work needs more compute than the estimate, the
  honest report is that the estimate was wrong, and it lands in the calibration
  ledger as exactly that.
- **This lane does not raise the cap.** Rule 12's "an overrun stops the run; it
  does not get a new budget" still binds this lane, and rule 2 forbids altering a
  registered cap post-compute by any addendum. Neither of those bites *before*
  the freeze — this document is pre-compute and unfrozen, so the supervisor may
  set the cap to any value at freeze time. **After the freeze the number above is
  fixed.** A supervisor's, peer's or chief's message is not authority to raise it
  (rule 9); only Sanaa's own words or the permission system are.

**Derived dollar figure, labelled:** 300 core-min = 5.0 core-hours × **$0.0513
/core-h** (c7a.4xlarge, **owner-stated 2026-08-21/22**) = **$0.2565 — DERIVED, NOT
MEASURED.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5),
so no cost figure produced on this box is a measurement. This is far below the
$25 pre-authorisation threshold.

**ESTIMATE-VERSUS-ACTUAL CALIBRATION IS OWED AT COMPLETION AND IS NOT OPTIONAL.**
Per CLAUDE.md rule 12 and Sanaa's 2026-08-23 directive, at every process
completion — each rung graded and the case closed — the pre-registered estimate
above is compared against the actual incurred core-minutes read from the logs;
the ratio actual/predicted is stated; the gap is attributed (contention,
misprediction, waste — **waste named separately and never absorbed into the
ratio**, per `COMPUTE_BUDGET_CHARTER.md` §6); and the row lands in
**`docs/COST_CALIBRATION.md`** under that file's append rules and the rule-10
private-index protocol. **A completion report without this comparison is
incomplete.**

---

## 13. WHAT THIS REGISTRATION DOES NOT COVER

- **§1.7, the adjoint rung, in its entirety.** DAFoam, `DASimpleFoam`, the FFD
  box, the design variables, the FD-vs-adjoint gradient verification, the
  optimiser, the post-optimum re-solve and the 400 core-min adjoint cap are
  **dafoam's** and are registered by dafoam. Nothing above authorises, costs or
  gates any of it. This registration's cap of 300 core-min is the **primal**
  family's alone and is not additive authority for anything in §1.7.
- Any comparison against experiment. No experimental jet-flap dataset is
  registered here; the only comparand is eq. (2) of ARC R&M 3304 (secondary).
- Any three-dimensional or finite-aspect-ratio result. Eq. (3) of the source is
  explicitly **not used** (§1.3).
- Any claim about Spence (1956), which no one here has read (§1.1).

---

## 14. SUBMISSIONS

**PARKED.** Nothing arising from this case is sent, filed, uploaded, registered,
posted, emailed or commented outside this box, by any agent, at any level, ever.
Sending is Sanaa's decision alone and is taken by her. Parked is not cancelled:
artefacts are kept current, and no reading of "current" lets readiness slide into
sending.

---

## 15. FREEZE BLOCK — TO BE COMPLETED BY THE SUPERVISOR, NOT BY THIS LANE

| Field | Value |
|---|---|
| FROZEN | **NO — this document is an UNFROZEN DRAFT** |
| Freezing commit sha | *(supervisor)* |
| Freezing timestamp (UTC) | *(supervisor)* |
| Frozen by | *(supervisor — check 4, non-delegable)* |
| Condition asserted at freeze | *(supervisor: the run root `verification/runs/JF1_jet_flap/` does not exist)* |
| md5 of `analyse_jf1.py` at freeze | *(supervisor)* |
| md5 of `make_jf1_mesh.py` at freeze | *(supervisor)* |

**Until every field above is filled, no compute may be launched against this
document.** After first compute, gates are closed: changes land only as dated
addenda that cannot alter a gate, threshold, cap or label, and originals are
struck, never rewritten.

---

## 16. OPEN ITEMS — THE SUPERVISOR MUST RULE ON THESE BEFORE FREEZING

These are raised, not resolved. Three (**O1**, **O4**, **O5**) are places where
the directive as literally written cannot be executed or rests on a premise that
does not hold; **O2** is a consequence of §1.2's own geometry choice colliding
with §1.5's V gate; **O3** is a decision the directive left open whose two
branches turn out to be 22× apart. **NONE HAS BEEN QUIETLY FIXED.** Where this
draft registers a working resolution it says so, states the alternative, and
leaves the ruling to the supervisor.

**O1 — The blow-up guard is unsatisfiable at `C_mu_jet = 0.0`.**
§1.4 registers `max|U| < 2 V_j`. The sweep contains `C_mu_jet = 0.0`, where
`V_j = 0`, so the guard reads `max|U| < 0` — **impossible for any flow**, and the
unblown reference would fail its own absolute bound unconditionally. This is
structurally the same defect as the `C_mu` symbol collision (§0): a criterion
written with the blown case in mind, applied to a sweep that contains the unblown
one. §5.5 above registers **`max|U| < 2 × max(V_j, U_inf)`**, which reduces to the
directive's form wherever `V_j > U_inf` (i.e. at every blown point,
`V_j ≥ 22.36 > 10`) and gives `max|U| < 20 m/s` at `C_mu_jet = 0.0`.
**This is a change to a registered absolute bound and is therefore the
supervisor's ruling, not this lane's. It is flagged, not absorbed.**
Related and also for the supervisor: at `C_mu_jet = 0.0` the `jetSlot` patch has
`U = (0,0,0)` with `p zeroGradient` — a zero-velocity inlet, not a wall. The
alternative is to declare `jetSlot` a `wall` for the unblown rows only, which
changes the patch type mid-sweep. §7.4 already registers the mass-flow check as
`N/A` there rather than a false 0.0 %.

**O2 — Gate V compares a blunt-base body against (presumably) sharp-TE records.**
The base-drag increment is **6–19 % of `Cd`** (§7.1). Splitting V so the `Cd` arm
is reported with the measured base `Cp` beside it, and gated only against a band
registered for a blunt-base body, is the resolution proposed in §7.1 — but
**registering or widening a band is a gate decision and is reserved to the
supervisor.**

**O3 — §1.4's two freestream-`omega` prescriptions differ by 22.36× in `nut`.**
Branch A (`L = 0.1 c`) gives `nut_inf/nu = 67.08`; branch B (`nut/nu = 3`) gives
3.00. §5.3 registers **branch B** with the reasoning. The directive offers both
and asks only that the choice be recorded, so this is not a directive error — but
the size of the gap is worth the supervisor's eye before it is frozen, because it
is a boundary condition that reaches the wall layer the entire low-Re mesh exists
to resolve.

**O4 — GATE V'S PREMISE IS FALSE. THE RECORD §1.1 SAYS IS "ALREADY GATED ON FILE"
DOES NOT EXIST. Gate V is registered `BLOCKED`.**
This is the largest open item and it is a **factual** defect in the directive, not
a physics or arithmetic one. §1.1 asserts the NACA 0012 baseline is *"already
gated on file for unblown CL-alpha and Cd"* and §1.5 builds gate V on *"the
on-file gated CL-alpha slope and Cd within their existing bands"*. A
repository-wide search found **no gated unblown NACA 0012 lift-curve-slope record
at all**, and no surviving gated `Cd` record: the nearest candidate
(`models/curriculum/results/naca0012_wing.json`) is `Cd` at a **single alpha** on
a **3D wing**, its verdict was **overturned as not reproducible**
(`W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md`, 21.6 % `Cd` spread from mesh noise
alone) and its grid-convergence claim separately ruled **`NOT A RESULT`**
(`LADDER_RECIPE_RULING_2026-08-25.md`); the dafoam A1 row is an **adjoint FD
verification artefact** by the lab's own audit (`docs/VALIDATION_INVENTORY.md:364`);
the TMR row **refuses the comparison in its own words**; and F5b, the nearest
`CL(alpha)` attempt, is recorded as **"NO GATE EXISTS"**
(`docs/VALIDATION_INVENTORY.md:306`). §7.1 sets it all out with paths and numbers.
**This lane has NOT invented a comparand to rescue the gate and has NOT quietly
substituted one.** The supervisor rules between options (a), (b) and (c) of §7.1.
**The freeze must not proceed past this item.**

**O5 — `Aref` and the 2D extrusion thickness: a silent v2606 hazard the directive
does not close.** §1.4 specifies `Aref = c` "per unit span" but pins nothing about
the extrusion thickness `t_z`, while v2606 integrates over the **actual** face
areas (`forces.C:729`) and divides by the **dictionary's** `Aref`
(`forceCoeffs.C:164`) with no reconciliation. Every `CL` and `Cd` would be scaled
by `1/t_z`, silently, on a case that meshes, runs and converges. §5.6 registers
`t_z = 1.0 m` exactly plus an **independent comparator cross-check** on the
`jetSlot` patch area (`h × t_z` must equal 0.005 m² to 1e-9). Raised rather than
merely fixed because it is a gap in the registered force specification and the
supervisor should see it before the freeze. §5.6 also records that §1.4's
`forceCoeffs` block **omits the required `rho rhoInf;` entry** (v2606 defaults
`rhoName_` to `"rho"`, `forces.C:539`), without which the function object
`FatalError`s at `forces.C:176` — a loud failure, but a real omission.

---

*Drafted by a cfd lane, 2026-08-30. Every number above was computed from the
registered definitions and cross-checked against a page image of the printed
source; none was copied from the OCR sidecar, which states in its own header that
its equations are corrupted. Verdict: **PENDING**.*
