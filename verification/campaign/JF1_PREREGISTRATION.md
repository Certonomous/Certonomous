# JF1 — JET-FLAP AIRFOIL, PRIMAL FAMILY — PRE-REGISTRATION

## *** FROZEN — 10-LINE TEMPLATE. Status at freeze: ARMED — never run. ***

**Frozen by the commit that carries this file**, 2026-08-31T15:29Z, by `cfd-supervisor`
personally under `SUPERVISION_CHARTER.md` §3 check 4, **under Sanaa's FREEZE CLOCK**
(`etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md`, commit `927924f1`):
*"Freeze in 10-line template form within 4 hours; anything a draft still 'needs' after that
becomes a W-3 amendment after first fields exist."* Clock started 15:14Z; **frozen at 15:29Z,
inside 15 minutes of it, and — deliberately — BEFORE the first feasibility field exists.**

### THE TEN LINES. These are the frozen gates. Everything else in this document is supporting material and is amendable as a W-3 addendum after first fields.

| # | gate | threshold | label if outside |
|---|---|---|---|
| 1 | **V — unblown NACA 0012 regression** | *(none — see line 10)* | **`BLOCKED`** |
| 2 | **G — Roache triple on `CL_total`**, L1/L2/L3, `Fs = 1.25` | observed **`p ∈ [1.3, 2.5]`** | `GATE FAIL` |
| 3 | **G — grid convergence index** | **`GCI_fine < 3 %`**, `f_1 = L3` (fine), `f_3 = L1` (coarse) | `GATE FAIL` |
| 4 | **THEORY (a) — `CL_total(C_mu)`** at α = 0, τ = π/6, `C_mu ∈ {0.05, 0.1, 0.2}` | **≤ 15 %** vs Williams/Butler/Wood, series **INSIDE** the root with `4πC_μ′` | `GATE FAIL` |
| 5 | **THEORY (b) — `dCL/dα`** at `C_mu = 0.1` | **≤ 15 %** | `GATE FAIL` |
| 6 | **Physicality — jet mass flow** through `jetSlot` vs `ρ h V_j` | **≤ 0.5 %** | `NOT A RESULT` |
| 7 | **Physicality — near-wall resolution** | **`max(y+) ≤ 1`** on every gated level | `NOT A RESULT` |
| 8 | **Physicality — continuity** `sum local` | **`< 1e-6`** (see ruling O6 below) | `NOT A RESULT` |
| 9 | **Cost cap** | **300 core-min**, Sanaa's number, unmoved | overrun **stops the run**, `STATUS` written, artifacts preserved |
| 10 | **Verdict vocabulary** | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` only | — |

**Rule 5 ordering is one-way and binds every row:** a triple that is not `CONVERGING` is
`NOT A RESULT` whatever its value; the gate may turn a `PASS` or `GATE FAIL` **into**
`NOT A RESULT` and **never** the reverse. No GCI is quoted on a non-monotone triple.

### CHECK 4, PERFORMED PERSONALLY AT 15:29:46Z — re-derived on disk, not recalled

`verification/runs/JF1*` **absent**; **0** `JF1` entries across all six team queues; **no
`log.*`** anywhere in `cases/JF1_JET_FLAP/`; **no solver process running**; the single time
directory is `0/`, the initial condition, **not a field**. **No compute has produced a
result against this document.**

### ⚠ WHY THIS WAS FROZEN AHEAD OF THE FEASIBILITY SOLVE, AND IT IS THE WHOLE POINT

The drafting lane raised the sharpest question of this case: **rule 2 closes gates at *first
compute*, not first *gated* compute**, so a feasibility field could be argued to have closed
this window — *"the single most likely way this case repeats `F23b`."* Sanaa has ruled that
feasibility rungs need no freeze and that gates score nothing on them, and that ruling
governs. **I have not resolved that tension by argument. I have removed it.** Freezing before
any field exists means the question cannot arise: whatever "first compute" means, **this
freeze precedes it.** `F23b` died because a threshold became unamendable the moment a solver
ran. That will not happen here.

### FOUR SUPERVISOR RULINGS, MADE AT FREEZE, RECORDED WITH THEIR AUTHOR

- **O4 — gate V is `BLOCKED`** (line 1). The only candidate comparand sits at **y+ = 9.664, a
  wall-function solution**, against this case's y+ ≤ 1 with no wall functions. **A different
  wall treatment is a different mesh family**, so it cannot supply the same-family regression
  §1.5 asks for — decisive before that record's other weaknesses. **No comparand was
  manufactured.** The absence is registered as **FINDING JF1-V1**, a coverage gap in this lab.
- **O6 — continuity is gated at `1e-6`, NOT at `1e-8`** (line 8). The lane could not derive
  `1e-8` from this document's own arithmetic or from any artifact — it rests on general
  practice — **and L-409 is precisely about gating on a number you cannot derive.** `1e-6` is
  defensible as *unambiguously not converged*. **The actual value is REPORTED on every row**
  (the exemplar predicts 3.0e-09), and a tighter expectation is recorded as an expectation,
  never as a gate.
- **O3 — branch B plus the S2 sensitivity** (option C). A **22.36×** freestream-`nut` choice
  defended only by argument is the first thing any reader will challenge; at **11.36
  core-min, 3.8 % of the cap**, it can simply be measured instead.
- **O7 — cap stays at Sanaa's 300.** Registered total **282.00 core-min** with S2, slack
  18.00; **$0.2314 `[DERIVED]`, not measured.** If the single L3 run needs a re-run, gate G
  goes **`BLOCKED` on budget and escalates** — it does not silently consume a reserve that
  does not exist.

### TWO DEPARTURES DISCLOSED TO SANAA RATHER THAN ABSORBED

1. **Cell counts are 13.3–14.1 % above her §1.3 targets** — 46 180 / 86 638 / 161 006 against
   ~40k / ~75k / ~140k. Her `~` marks a target; her §1.4 *"no wall functions — the jet/BL
   interaction is the physics"* makes **`max(y+) ≤ 1` a gate**. A gate beats a target, so the
   mesh grew. **If she reads those counts as binding, the constraint set is not simultaneously
   satisfiable and this case is `BLOCKED` — that is her call, not mine.**
2. **Her remembered theory formula is wrong in its grouping**, not its constants. 0.151 /
   0.139 / 0.219 are all correct, but the series sits **inside** the square root with
   `4πC_μ′`; her form is high by `√S` — **+2.02 / +3.04 / +4.66 / +7.29 %** at
   `C_mu = 0.05 / 0.1 / 0.2 / 0.4`. A constants-only check returns "all three correct" and
   freezes a one-signed, growing bias into the gate. **The corrected grouping is what is
   frozen at line 4.**

**No queue entry exists. No run root exists. No solver has been started.**
**Until the FROZEN stamp is present, every gate, threshold, band, cap and label
below is a PROPOSAL and is amendable under rule 2's pre-compute amendment
clause; §16 lists the open items the supervisor must rule on before freezing.**

> **AMENDED 2026-08-31 — EIGHTEEN PRE-COMPUTE AMENDMENTS, A1–A18, RECORDED IN
> §17, WITH THE CONDITION AND ITS CHECK AT §17.1.** A freeze-readiness audit found
> that **as first committed this registration had no satisfiable outcome**: §8.1's
> completion clauses refused every possible run (A14), §5.2's formulae gave
> `omega_jet = 0` at the unblown point that §7.4 binds to `omega > 0` (A10), and
> §4.3's first cell made `max(y+) ≤ 1` unreachable on every level (A7). §7.2's
> Roache indices were inverted (A6) and §5.1's jet boundary condition silently
> restored the frame convention §1.6 refutes (A3). **All were repairable only
> because no compute had run — this is L-409, and `F23b` is what it costs when the
> same class is found after the freeze.**
>
> **§17.3 carries the L-409 satisfiability construction: one concrete outcome,
> with actual numbers on the actual meshes at an actual iteration count, that
> passes every clause of this document simultaneously.**
>
> **RULED by the cfd-supervisor, 2026-08-31: open item O4, option (c) — GATE V IS
> `BLOCKED`, and the case is gated on G and THEORY alone (§7.1).**
> **STILL OPEN and still blocking the freeze: O3, O5, O6, O7 (§16).**

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
| `tau` | jet deflection angle below the chord line | 30 deg = `pi/6` = 0.5235987755982988 rad exactly (§2) | — |
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
> Printed p.5 = PDF p.6; printed p.3 = PDF p.4.
>
> **Rule-15 title-page verification, cited at the artifact that performs it**
> (amended 2026-08-31, item **A1** of §17): the binding record is the **first line
> of the sidecar's own header block**,
> `docs/papers/powered_lift_and_ducted_propulsion/williams_butler_wood_1961_arc_rm3304_aerodynamics_of_jet_flaps.txt`,
> which reads *"TITLE-PAGE VERIFIED (CLAUDE.md rule 15) by visual read of PDF page
> 1-2 on 2026-08-30."* and transcribes the title page: *MINISTRY OF AVIATION /
> AERONAUTICAL RESEARCH COUNCIL REPORTS AND MEMORANDA / R. & M. No. 3304 / 'The
> Aerodynamics of Jet Flaps' / By J. WILLIAMS, S. F. J. BUTLER and M. N. WOOD /
> LONDON: HER MAJESTY'S STATIONERY OFFICE 1963*, with p.2 adding *"Reports and
> Memoranda No. 3304, January, 1961"*.
>
> ~~*As first committed this section cited `git log --diff-filter=A` on the paper
> path, returning `1ae12da5` as the only commit that ever added it.*~~ **STRUCK AS
> THE WRONG INSTRUMENT.** A `--diff-filter=A` check establishes **which commit
> added a path** — it is a path-and-commit check, and CLAUDE.md rule 15 and L-144
> forbid exactly that class of instrument: *never by file type, filename or hash —
> a manifest can be internally consistent and externally false.* A commit-provenance
> check cannot tell you what is printed on page 1. The **substance** of the
> provenance statement is unaffected and is retained as a separate, correctly
> labelled fact — `1ae12da5` is the adding commit — but it is **not** the rule-15
> evidence and is no longer offered as such.
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

**THE ADDITIVE DECOMPOSITION IS A READING OF THAT SENTENCE, NOT A PRINTED
IDENTITY** (amended 2026-08-31, item **A2** of §17). What the source prints is a
*qualitative* statement — the total lift is a "considerable magnification" of the
direct jet-reaction lift "because of the additional pressure lift". It does **not**
print `C_L = C_mu sin(theta + alpha) + C_L,pressure` as an equation. This
registration **reads** that sentence as the additive decomposition
`CL_total = CL_aero + C_mu_jet sin(tau + alpha)`, and the reading is what is
registered and gated. The reading is a strong one — the sentence names exactly two
contributions, the direct reaction and the additional pressure lift, and calls the
first a component of the second's total — but it is a reading, and any downstream
record must present it as one and never as verbatim source text. If the primary
(Spence 1956, §1.1) is later obtained and prints the decomposition explicitly, this
paragraph is superseded by a dated addendum; it is not silently upgraded to a quote.

The directive §1.4 is therefore **right in kind** — the theory's `C_L` does
include the jet reaction, so `CL_total = CL_aero + (jet reaction)` is the correct
construction and the theory gate correctly uses `CL_total` — but **wrong in
detail**: it registers `C_mu sin(tau)`, omitting `alpha`.

**Registered:** `CL_total = CL_aero + C_mu_jet * sin(tau + alpha)`.

### 1.6a THE ONE FRAME — REGISTERED HERE AND NOWHERE ELSE (amended 2026-08-31, item **A3** of §17)

**`sin(tau + alpha)` is only correct in ONE frame convention, and this section
names it. Nothing else in this document may adopt a different one.**

> **REGISTERED FRAME — the AIRFOIL FRAME. The mesh does not move with `alpha`.**
>
> 1. The **mesh and the body are fixed.** The chord line lies along `+x`; the
>    trailing edge is at `x = c`. No level of the ladder is re-meshed for `alpha`.
> 2. The **freestream is rotated** by `alpha`:
>    `U_farfield = U_inf (cos alpha, sin alpha, 0)`.
> 3. The **jet is NOT rotated.** It is a property of the body, fixed in the body
>    frame at `tau` below the chord line for every `alpha`:
>    `U_jetSlot = V_j (cos tau, −sin tau, 0)` — **identical for `alpha` = 0, 4 and
>    8 deg at a given `C_mu_jet`.**
> 4. `liftDir = (−sin alpha, cos alpha, 0)` and `dragDir = (cos alpha, sin alpha, 0)`
>    are rotated, because lift and drag are defined relative to the **freestream**,
>    which is the thing that moved.

**Derivation, because the whole registered gate term hangs on it.** The jet
reaction on the body is minus the momentum flux leaving through `jetSlot`, so as a
coefficient it is `C_reaction = C_mu_jet (−cos tau, +sin tau, 0)`. Its component
along the registered `liftDir`:

```
    C_reaction . liftDir
      = C_mu_jet [ (−cos tau)(−sin alpha) + (sin tau)(cos alpha) ]
      = C_mu_jet [ cos tau sin alpha + sin tau cos alpha ]
      = C_mu_jet sin(tau + alpha)                                   <-- registered
```

**AND THE COUNTERFACTUAL, WHICH IS THE REASON THIS SECTION EXISTS.** If the jet
were **also** rotated by `+alpha` — i.e. `U_jetSlot = V_j (cos(tau − alpha),
−sin(tau − alpha), 0)` in the fixed body frame, which is what "rotated with alpha"
means — then the jet vector and `liftDir` rotate together, the rotation cancels in
the dot product, and the reaction lift collapses to **`C_mu_jet sin(tau)`**:
**alpha-independent, and precisely the directive's convention that the rest of this
section refutes.** The document would then be adding an analytic `0.0615661` at
`alpha = 8 deg` to a field in which the jet had *already* been held at `tau` to the
freestream — restoring, in the physics, exactly the one-signed **1.2325 %** slope
bias that §1.6 was written to remove, in the arm whose band is tightest.

> ~~As first committed (`34f51b78`), §5.1's boundary-condition table gave the
> `jetSlot` velocity as `fixedValue (V_j cos tau, −V_j sin tau, 0)` **"rotated with
> `alpha`"**.~~ **STRUCK.** It contradicted §0, this section, and the registered
> `liftDir`/`dragDir`, and it silently restored the refuted convention. **You cannot
> rotate both the freestream and the jet.** §5.1 now carries the airfoil-frame form
> with no rotation.

**REGISTERED COMPARATOR ASSERTION, so the error is mechanically impossible rather
than merely disclaimed:** before grading the alpha sweep, the comparator reads
`0/U` from each of the `alpha` = 0, 4 and 8 cases at `C_mu_jet = 0.1` and
**refuses (exit 2)** unless the `jetSlot` `value` entry is **bytewise identical**
across all three, and unless each `farfield` `freestreamValue` matches
`U_inf (cos alpha, sin alpha, 0)` to 1e-9. A frame error is then a refusal, not a
number.

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
| `tau` | 30 deg = **`pi/6` = 0.5235987755982988 rad exactly**, deflected toward the pressure side | §1.1 |
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

*(Amended 2026-08-31, item **A4** of §17: `tau` is registered as **`pi/6` exactly**,
not as the 7-decimal rounding `0.5235988`. Every 10-digit `CL_theory` in §1.4 and
§7.3 was computed with `pi/6` and reproduces only with `pi/6`: at
`C_mu_jet = 0.05` the rounded value returns `0.4234034631` against the registered
`0.4234034434`, a discrepancy in the 8th digit. A document that quotes ten digits
must register the constant to more than seven. No registered value changes.)*

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

**REVISED 2026-08-31, item A5 of §17 — the normal counts below rose from
85 / 116 / 159 to 97 / 133 / 181 because §4.3's first-cell height had to fall from
`2.345869e-05 m` to `5.0e-06 m` for `max(y+) ≤ 1` to be reachable at all. The
streamwise counts, the jet-sheet counts and the topology are unchanged. The
superseded totals were 40 660 / 75 928 / 142 086.**

| Block | i (streamwise/tangential) | j (normal) | L1 | L2 | L3 |
|---|---|---|---|---|---|
| upper surface | clustered LE & TE | y+ ladder | 100 × 97 | 137 × 133 | 187 × 181 |
| lower surface | clustered LE & TE | y+ ladder | 100 × 97 | 137 × 133 | 187 × 181 |
| upper wake | TE → 3c fine, → 25c coarse | y+ ladder | 130 × 97 | 178 × 133 | 243 × 181 |
| lower wake | TE → 3c fine, → 25c coarse | y+ ladder | 130 × 97 | 178 × 133 | 243 × 181 |
| **jet-sheet block** (base gap, extended downstream) | as the wake blocks | **across `h`** | 130 × **12** | 178 × **16** | 243 × **22** |
| **planned total cells** | | | **46 180** | **86 638** | **161 006** |

Arithmetic, shown: L1 `= 2(100×97) + 2(130×97) + 130×12 = 19 400 + 25 220 + 1 560
= 46 180`; L2 `= 2(137×133) + 2(178×133) + 178×16 = 36 442 + 47 348 + 2 848
= 86 638`; L3 `= 2(187×181) + 2(243×181) + 243×22 = 67 694 + 87 966 + 5 346
= 161 006`. Normal counts follow the ladder: `round(97 × 1.3693) = 133`,
`round(97 × 1.8708) = 181`.

**Departure from §1.3's cell-count targets, disclosed.** §1.3 targets ~40 k / ~75 k
/ ~140 k; the levels above are **46 180 / 86 638 / 161 006**, i.e. **+13.6 % /
+14.1 % / +13.3 %**. **A target is not a gate; `max(y+) ≤ 1` IS a gate (§7.4), and
a gate beats a target.** The increase is entirely in the wall-normal direction and
is forced by §4.3. The cost consequence is carried in §12 and the programme still
fits the 300 core-min cap.

**ROACHE INDEX MAPPING — REGISTERED EXPLICITLY, BECAUSE IT WAS WRONG (amended
2026-08-31, item A6 of §17).** Roache's subscripts run **fine = 1, medium = 2,
coarse = 3**, with `r_21 = h_2/h_1` and `r_32 = h_3/h_2`. In this ladder **L3 is
the FINEST level and L1 the coarsest**, so:

| Roache index | this document's level | cells |
|---|---|---|
| 1 (fine) | **L3** | 161 006 |
| 2 (medium) | **L2** | 86 638 |
| 3 (coarse) | **L1** | 46 180 |

`h ∝ N^(−1/2)` in 2D, so
`r_21 = sqrt(161006/86638) = ` **`1.36322`** and
`r_32 = sqrt(86638/46180) = ` **`1.36971`** — both **≥ 1.3** as §1.3 requires.

> ~~As first committed, §4.2 gave `r_21 = sqrt(75928/40660) = 1.3665` and
> `r_32 = sqrt(142086/75928) = 1.3680`.~~ **STRUCK — the indices were inverted.**
> That assignment labels the **coarse** pair (L1→L2) as `r_21` and the **fine**
> pair (L2→L3) as `r_32`. It is nearly harmless in `r` itself (1.3665 vs 1.3697,
> 0.2 %) and **not harmless at all in the GCI**: §7.2 computes
> `GCI_fine = Fs |eps_21| / (r_21^p − 1)`, so under the inverted mapping the
> reported "fine-grid" GCI would have been computed from the **L1–L2 (coarse)**
> difference — the largest of the two — and reported as the uncertainty on the
> **finest** grid. On the exemplar triple of §17.3 that is 0.463 % reported in
> place of the true 0.247 %, an **1.9× overstatement carrying the wrong label**.
> The comparator now takes `eps_21 = f(L2) − f(L3)` and `eps_32 = f(L1) − f(L2)`.

**`r_21 ≠ r_32`.** Registered consequence: the observed order `p` is computed with
the **non-constant-`r` Roache iterative form**, not the constant-`r` closed form.
The comparator refuses (exit 2) if it is handed a triple whose `r_21` and `r_32`
differ by more than 1 % and the constant-`r` branch was taken. Here
`|r_21 − r_32|/r_21 = 0.476 %`, inside 1 %, and the non-constant-`r` form is used
regardless — the 1 % clause is a refusal on the *branch taken*, never a licence to
take the constant-`r` branch.

### 4.3 Near-wall sizing — REDERIVED 2026-08-31 (items **A5** and **A7** of §17)

**This section was over-determined and did not close, and its `y1` was sized at the
one station on the airfoil where `u_tau` is SMALLEST. Both are repaired here, with
the arithmetic shown. Every superseded number is struck, not deleted.**

Turbulent BL thickness at `x = c`: `delta = 0.37 c Re_c^-0.2 = ` **`2.3345e-02 m`**
= **2.33 % chord**. Unchanged, and still the reference length for the layer count.

#### 4.3.1 What was wrong — DEFECT 1, the distribution does not close

> ~~"a **single uniform growth of 1.1417 over 85 cells** from `y1 = 2.345869e-05 m`
> to the 25 c farfield, which puts **38 cells inside `delta`**"~~ — **STRUCK. Four
> numbers, mutually inconsistent, in one sentence.** A geometric stack is fixed by
> any three of {`y1`, `g`, `N`, `L`}; this registered all four plus a fifth derived
> count, and no three of them agree with the rest:
>
> | assertion | what the arithmetic gives |
> |---|---|
> | `y1 = 2.345869e-05`, `g = 1.1417`, `N = 85` reaches the 25 c farfield | reaches **12.9077 m**, not 25 m — **short by a factor 1.937** |
> | `N = 85` from that `y1` to 25 m | needs `g = ` **`1.15152`** — **breaks the registered `≤ 1.15` cap** |
> | `g = 1.1417` puts 38 cells inside `delta` | puts **37.40 → 37** cells inside `delta`, not 38 |
> | `g = 1.15` puts 36 cells inside `delta` | **35.86 → 35** cells, not 36 |
>
> `(g^N − 1)/(g − 1) × y1` was never evaluated for the registered triple. This is
> L-409's arithmetic-at-registration-time failure in its simplest form.

#### 4.3.2 What was wrong — DEFECT 2, and it is the larger one: `max(y+) ≤ 1` was UNREACHABLE

The struck `y1` came from `Cf(x = c) = 0.0576 Re_c^-0.2 = 0.0036343`,
`u_tau = 0.426281 m/s`, `y1 = nu/u_tau = 2.345869e-05 m`. **That evaluates the
flat-plate correlation at `x = c` — the station where `Cf`, and therefore `u_tau`,
is at its MINIMUM over the whole chord.** §7.4 gates **`max(y+)`** over the
`airfoil` patch, and the maximum of `y+` is set by the maximum of `u_tau`, which
sits near the **leading edge**, where both `Cf(x)` and the local edge velocity
`U_e` are far larger. With a single uniform `y1` the gate was therefore
**unsatisfiable by construction on every level of the ladder** — L-409's class
exactly, found before compute.

Envelope used, stated as a formula so it can be checked:

```
    Cf(x)   = 0.0576 (U_e x / nu)^-0.2
    u_tau(x)= U_e sqrt(Cf/2) = 0.169706 * U_e^0.9 * (x/nu)^-0.1
    y1_max  = nu / u_tau(x)                                   [ for y+ = 1 ]
```

Evaluated at `x = 5.0e-04 m` (0.05 % chord — the inner limit at which a turbulent
flat-plate correlation retains any meaning; inside it the flow is a **stagnation**
boundary layer where `u_tau -> 0` and the correlation over-predicts without bound)
and at the **worst GATED row's** peak edge velocity:

| row | `U_e` peak (m/s) | `u_tau(5e-04)` (m/s) | `y1` for `y+ = 1` (m) |
|---|---|---|---|
| `C_mu_jet` = 0, `alpha` = 0 | 11.96 | 0.9946 | 1.0054e-05 |
| `C_mu_jet` = 0.2, `alpha` = 0 | 20.41 | 1.7317 | 5.7748e-06 |
| **`C_mu_jet` = 0.1, `alpha` = 8 deg — WORST GATED** | **22.40** | **1.8837** | **5.3086e-06** |
| `C_mu_jet` = 0.4, `alpha` = 0 (ungated exhibit) | 24.20 | 2.0195 | 4.9518e-06 |

`U_e` peaks are the §5.5 predicted-peak table, derived there. **The struck
`y1 = 2.3459e-05 m` is 4.42× the worst gated row's requirement** — it would have
produced `max(y+) ≈ 4.4` on L1 and `≈ 2.4` even on L3, and §7.4 would have refused
every row on every level.

#### 4.3.3 REGISTERED, closed, and shown to close

> **`y1 = 5.0e-06 m = 5.0e-06 c` on L1**, ladder-scaled as `y1/s`:
> **3.651501e-06 m** on L2, **2.672653e-06 m** on L3.

Predicted `max(y+)` at the envelope station, `= y1 u_tau / nu`:
**L1 0.9419 · L2 0.6879 · L3 0.5035** — all `≤ 1`, L1 with **5.8 % margin**. The
`≤ 1` ceiling is honoured on the level where it binds, and refining the first cell
with the ladder (§4.1) keeps it satisfied on the other two.

**Independent corroboration of the scale, recorded as corroboration and not as
evidence:** wall-resolved RANS practice for this body at `Re_c = 6e6` uses an
off-wall spacing of order `1e-06 c`; `y1` for fixed `y+` scales as `c Re^-0.9`, so
`Re_c = 1e6` implies `1e-06 × 6^0.9 = 5.0e-06 c`. This is a scaling argument from
general practice, **not a number read off an artifact on this box**, and no gate
rests on it.

**The distribution, now closed — three free numbers, one equation, nothing left
over.** `y1`, `N` and the 25 c farfield are registered; `g` is **solved**, never
asserted:

```
    y1 * (g^N - 1) / (g - 1) = 25.0 m      solved for g at each level
```

| Level | `y1` (m) | `N` (normal cells) | **`g` (solved)** | `≤ 1.15`? | stack reaches | layers inside `delta` |
|---|---|---|---|---|---|---|
| **L1** | 5.000000e-06 | **97** | **1.149626** | **yes**, 0.033 % below the cap | 25.000000 m | **46** (46.98 → 46 complete) |
| **L2** | 3.651501e-06 | **133** | **1.106859** | yes | 25.000000 m | **64** |
| **L3** | 2.672653e-06 | **181** | **1.077393** | yes | 25.000000 m | **87** |

`N = 97` is not chosen: at the growth cap `g = 1.15` exactly, the count needed to
reach 25 m from `y1 = 5.0e-06` is `ln(1 + (25/y1)(g−1))/ln(g) = ` **`96.79`**, so
**97 is the smallest integer count for which a solved `g` still satisfies
`g ≤ 1.15`** (96 would require `g = 1.151441`, over the cap). L2 and L3 take
`round(97 s)`. **All five quantities — `y1`, `N`, `g`, the farfield distance and
the in-`delta` count — now close simultaneously on all three levels**, which is
what the struck version did not do.

**Layer-count constraint, retained and strengthened.** §1.3 asks for **≥ 30 BL
layers** at growth **≤ 1.15**. That floor genuinely does not cover the boundary
layer: from the struck `y1`, 30 layers at 1.15 stack to `1.0202e-02 m`, i.e.
**43.7 % of `delta`**. The departure is therefore sound and stands. **Registered
binding constraint: `≥ 36` complete layers inside `delta` on every level**, and the
mesh script asserts it. The delivered counts are 46 / 64 / 87 — the floor is met
with large margin on every level, and `≥ 30` is honoured as a **floor, not a
target**.

`y+` is **measured** post-solve from the real field, never assumed — see §7.4 and
the refusal in §8.4.

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
  afforded at 46 k; the grading is therefore **registered**, not improvised.

### 4.5 checkMesh gates, per level, and the birth certificate

Registered hard gates, all three levels:

| Metric | Gate | Relation to `docs/standards/MESH_STANDARD.md` |
|---|---|---|
| max non-orthogonality | **< 65** | **TIGHTER than the lab standard's hard gate of 70** — see the note below |
| max skewness | **< 4** | same as the lab standard |
| negative volumes | **exactly 0** | same as the lab standard |
| **max aspect ratio** | **REPORTED on every level; `> 1000` requires the alignment justification below to be present on the certificate; `> 1000` TOGETHER WITH non-orthogonality `> 60` or skewness `> 2` is a JF1 `BLOCKED`** | `MESH_STANDARD.md` §3.3 makes AR **advisory at 1000** and the compound condition **a flag for investigation** — JF1 promotes the compound to a refusal |
| `checkMesh` overall | must print `Mesh OK` | — |

**D5 — THE NON-ORTHOGONALITY GATE IS JF1'S, NOT THE LAB'S, AND IS TIGHTER**
(added 2026-08-31, item **A8** of §17). `MESH_STANDARD.md` sets the hard
non-orthogonality gate at **70**. This registration gates at **< 65**.
**Registered reading, so no downstream reader mislabels a refusal:** a JF1 level
measuring, say, **66** is a **JF1 refusal against a self-imposed tighter
threshold — it is NOT a lab-standard failure**, and the record of such a level must
say so in those words. It is not evidence that the mesh generator produced a mesh
the lab would reject, and it may not be cited as such anywhere. The extra margin is
registered because this case couples a 1.15-growth anisotropic wall stack to a C-
topology wake block and a base-slot block, and the correction terms that
non-orthogonality feeds are the same ones the thin jet sheet depends on.

**D4 — ASPECT RATIO IS MEASURED AND CARRIED, BECAUSE THIS GRID IS EXTREMELY
ANISOTROPIC BY DESIGN** (added 2026-08-31, item **A9** of §17). With
`y1 = 5.0e-06 m` (§4.3) against surface spacings ranging from `4.1667e-04 m` at the
trailing edge (matched to the base cell, §4.4) to `~1e-02 m` at mid-chord, the
first-layer aspect ratio is **`4.1667e-04 / 5.0e-06 ≈ 83` at the TE and
`1e-02 / 5.0e-06 ≈ 2000` at mid-chord** — i.e. **AR > 1000 is expected and is not a
defect here.** `MESH_STANDARD.md` §3.3's calibration is explicit that a hard gate at
1000 *"would reject every reference-grade wall-resolved RANS grid the lab owns"*
(the TMR flat-plate grids measure 66 643–74 041 with zero non-orthogonality).

> **Registered alignment justification, required on every birth certificate:** the
> anisotropy is **wall-normal**, aligned with the direction being resolved, on cells
> whose non-orthogonality is gated `< 65` and whose skewness is gated `< 4`. That is
> the legitimate case §3.3 names. **The dangerous case §3.3 names — extreme
> anisotropy coinciding with non-orthogonality or skew — is promoted here from the
> standard's "flag for investigation" to a JF1 `BLOCKED`:** AR `> 1000` together
> with non-orthogonality `> 60` **or** skewness `> 2` blocks the level. As with the
> 65 gate, that promotion is **JF1's, tighter than the lab standard**, and a level
> blocked by it must be recorded in those words.

A level failing any of these is `BLOCKED` and **no solve is launched on it**. A
gated row whose mesh level is `BLOCKED` is `NOT A RESULT`.

**Birth certificate per level**, at
`verification/runs/JF1_jet_flap/mesh/BIRTH_L{1,2,3}.md`, recording: actual cell
count; actual `r` against the level below in each direction **with the Roache index
it carries (§4.2)**; `y+` histogram (min/max/mean, measured post-solve); layers
inside `delta`; the **solved** normal growth ratio `g` and the assertion `g ≤ 1.15`;
cells across `h`; cells across the sheet at `x/c = 1`; **max and mean aspect ratio
with the alignment justification above**; full `checkMesh` quality block; the md5 of
the mesh script and the scale factor `s` used.

---

## 5. BOUNDARY CONDITIONS AND NUMERICS (§1.4)

### 5.1 Turbulence treatment — recorded and fixed across the ladder

`kOmegaSST`, **low-Re, no wall functions in the momentum sense** (`y+ ≤ 1`).
Registered wall set, **identical on all three levels and all runs**:

| Field | `airfoil` | `jetSlot` | `farfield` |
|---|---|---|---|
| `U` | `noSlip` | `fixedValue (V_j cos tau, −V_j sin tau, 0)` — **AIRFOIL FRAME, NOT rotated with `alpha`** (§1.6a) | `freestreamVelocity`, `U_inf` = 10 m/s **rotated by `alpha`** |
| `p` | `zeroGradient` | `zeroGradient` | `freestreamPressure` |
| `k` | `fixedValue 1e-10` | `fixedValue`, §5.2 (**floored, non-zero at `C_mu_jet = 0`**) | `freestream`, `k_inf` |
| `omega` | `omegaWallFunction` | `fixedValue`, §5.2 (**floored, non-zero at `C_mu_jet = 0`**) | `freestream`, `omega_inf` |
| `nut` | `nutLowReWallFunction` | `calculated` | `freestream` |

> **THE `jetSlot` VELOCITY IS FIXED IN THE AIRFOIL FRAME AND IS IDENTICAL FOR EVERY
> `alpha`** (amended 2026-08-31, item **A3** of §17). The words ~~"rotated with
> `alpha`"~~ that stood in this row as first committed are **STRUCK**: the mesh, the
> body and the jet are fixed, only the freestream and `liftDir`/`dragDir` rotate,
> and rotating the jet as well would collapse the registered jet-reaction term from
> `C_mu_jet sin(tau + alpha)` to `C_mu_jet sin(tau)` — the directive's refuted
> alpha-independent convention — silently restoring a one-signed **1.2325 %** bias
> into theory arm (b). **§1.6a derives this and registers the comparator assertion
> that makes the error a refusal rather than a number.**

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

**REGISTERED FORMULAE — ONE EXPRESSION FOR EVERY ROW OF THE SWEEP, INCLUDING THE
UNBLOWN ONE** (amended 2026-08-31, item **A10** of §17):

```
    k_jet     = max( 1.5 (I V_j)^2 ,  k_inf )                       I = 0.01
    omega_jet = max( sqrt(k_jet) / (C_mu_turb^0.25 * l_j) ,  omega_inf )
                                                     l_j = 0.07 h = 3.5e-04 m
```

with `k_inf = 1.5000e-04 m²/s²` and `omega_inf = 5.0 1/s` from §5.3.

| `C_mu_jet` | `V_j` (m/s) | `k_jet` (m²/s²) | `omega_jet` (1/s) | `nut_jet/nu` |
|---|---|---|---|---|
| **0.00** | **0.000000** | **1.500000e-04** *(floor)* | **63.887656** | **0.234787** |
| 0.05 | 22.360680 | 7.500000e-02 | **1428.571429** | 5.25 |
| 0.10 | 31.622777 | 1.500000e-01 | **2020.305089** | 7.42 |
| 0.20 | 44.721360 | 3.000000e-01 | **2857.142857** | 10.50 |
| 0.40 | 63.245553 | 6.000000e-01 | **4040.610178** | 14.85 |

#### 5.2a WHY THE `max(...)` FLOOR, AND WHY IT IS ONE FAMILY AND NOT A SPECIAL CASE

> **The defect it repairs.** As first committed this table had **no
> `C_mu_jet = 0.0` row**, and its bare formulae give, at `V_j = 0`,
> `k_jet = 1.5(0.01 × 0)² = ` **`0`** and
> `omega_jet = sqrt(0)/(C_mu_turb^0.25 l_j) = ` **`0`**. §7.4 registers
> **`omega > 0` everywhere** and §5.5 registers **`k ≥ 0` everywhere with
> `min(k) > 0` in the jet core** as **BINDING physicality checks whose failure is
> `NOT A RESULT`**. **Every unblown row would therefore have been `NOT A RESULT` by
> this registration's own check, before any solver ran** — and `omega = 0` in a
> `kOmegaSST` inlet is additionally a division by zero in `nut = k/omega` at that
> patch. This is L-409's class again: a criterion written with the blown case in
> mind, applied to a sweep that contains the unblown one — the same shape as the
> `C_mu` symbol collision of §0 and the blow-up bound of §5.5.

**The floor is registered rather than a patch-type switch, and the reason is that
the sweep must be ONE family.** The alternative — declaring `jetSlot` a `wall` for
the unblown rows only — changes the **patch type mid-sweep**, which changes the
momentum, `k` and `omega` boundary conditions, the `forceCoeffs` patch set (a wall
`jetSlot` would arguably belong in it, altering the meaning of `CL_aero`), and the
`checkMesh` patch topology. The unblown row is §1.1's **unblown reference for the
whole map**; a reference computed on a different boundary-condition family is not a
reference for it. **Registered: `jetSlot` is a `patch` on every row of the sweep,
with the same BC types on every row, and only the numeric values change.**

**The floor is inert on every blown row, and that is checkable in one line.** At
`C_mu_jet = 0.05` — the smallest blown point — `1.5(I V_j)² = 7.5e-02` exceeds
`k_inf = 1.5e-04` by **500×**, and `2020` /s at `C_mu_jet = 0.1` exceeds
`omega_inf = 5.0` /s by **404×**. **The four blown rows are numerically unchanged
to every digit printed above**, so the `max(...)` is not a re-registration of the
blown cases; it is the single expression that also has a value at `V_j = 0`.

**Arithmetic at `C_mu_jet = 0.0`, shown.** `k_jet = k_inf = 1.5000e-04`;
`sqrt(k_inf) = 1.22474487e-02`; `C_mu_turb^0.25 = 0.5477225575`;
`C_mu_turb^0.25 · l_j = 1.91702895e-04`;
`omega = 1.22474487e-02 / 1.91702895e-04 = ` **`63.887656 1/s`**, which exceeds the
`omega_inf` floor of 5.0, so the formula's own value stands and the floor is not
reached on `omega` either. `nut_jet = k/omega = 2.347871e-06 m²/s = ` **`0.234787
nu`** — the same order as the registered freestream `nut_inf/nu = 3` and far below
it, which is the physically right statement for a patch that is emitting nothing.

**Consistency with the unblown physics, disclosed.** At `C_mu_jet = 0` the
`jetSlot` carries `U = (0, 0, 0)`, `p zeroGradient`, and the floored `k`/`omega`
above. It is a **zero-velocity inlet, not a wall**: `nut` there is `calculated` from
`k` and `omega` and is `0.235 nu` rather than the `0` a low-Re wall would impose.
Over a patch of `h/c = 0.005` inside the base recirculation this is a **disclosed
and ungated modelling simplification**, of the same kind and smaller magnitude than
the top-hat jet profile disclosed above. It is disclosed, not gated, and it is the
price of keeping the sweep one family.

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
| `p` | initial residual < **1e-6** | `sum local` continuity error at the final iteration < **1e-8** — see §5.5b |
| `Ux` | < **1e-6** | `max\|U\|` < **the row's own bound, §5.5a** |
| `Uy` | < **1e-6** | as above |
| `k` | < **1e-6** | `k ≥ 0` everywhere; `min(k) > 0` in the jet core **(N/A at `C_mu_jet = 0`, §7.4)** |
| `omega` | < **1e-6** | `omega > 0` everywhere |
| `CL` | — | `\|dCL\| < 1e-4` over the **last 2000 iterations** |
| `Cd` | — | `\|dCd\| < 1e-5` over the **last 2000 iterations** |
| `nut` | — | `nut/nu` finite and `< 1e5` everywhere (realisability) |

All five residual channels are held to **the same order, 1e-6** — no channel is
tightened 1000× relative to its siblings, per §1.4. **Registered `SIMPLE` block, in
the four keys OpenFOAM actually reads** (`U` covers `Ux` and `Uy` — `simpleControl`
tests the maximum initial residual over a vector field's components, so writing
`Ux`/`Uy` separately would be silently ignored):

```
SIMPLE
{
    consistent                  yes;
    nNonOrthogonalCorrectors    1;
    residualControl { p 1e-6;  U 1e-6;  k 1e-6;  omega 1e-6; }
}
```

**Registered `controlDict` termination block, pinned because §8.1 clause 3 now reads
it and refuses on a mismatch:**

```
startTime 0;  deltaT 1;  endTime 20000;
writeControl timeStep;  writeInterval 20000;  purgeWrite 0;
```

> **ITERATION CAP: 20 000. A run that hits the cap is `NOT A RESULT`, never
> "close enough".**

Those are the registered words. There is no path by which a capped run becomes a
graded row, and no reading of "the residuals were nearly there" that changes it.
**§8.1 clause 3 registers how a run that stops EARLY because it converged is
distinguished from one that hits the cap and from one that stopped early for any
other reason.**

**MINIMUM ITERATION COUNT: 2 000, and it is a completion clause, not a gate.** The
`CL` and `Cd` plateau bounds above are defined over the **last 2 000 iterations**;
a run that stops at `N < 2000` has **no such window and the clause is unevaluable**.
Registered: `N_stop ≥ 2000` is required for completion (§8.1 clause 3a); a run
converging in fewer is **`NOT A RESULT`** with `N_stop` printed, and is treated as a
finding about the case rather than as a pass. **The L-409 division:** a 46 k-cell
low-Re `kOmegaSST` airfoil at `Re_c = 1e6` driven to 1e-6 on all four residual keys
is predicted to need **3 000–15 000** iterations; the registered window is
`[2 000, 20 000)`. The prediction sits inside the window with margin at both ends,
so the pair of clauses is satisfiable — which is the check that §16's O1 and this
document's §8.1 previously failed to perform.

#### 5.5a THE BLOW-UP GUARD — DERIVED FROM THE ROW'S OWN PREDICTED PEAK (amended 2026-08-31, item **A11** of §17)

> ~~`max|U| < 2 V_j`~~ (the directive) — **unsatisfiable at `C_mu_jet = 0`**, where
> it reads `max|U| < 0`. ~~`max|U| < 2 × max(V_j, U_inf) = 20.0 m/s` at
> `C_mu_jet = 0`~~ (this document as first committed, §16's O1) — **STRUCK: it
> replaced an unsatisfiable bound with a MARGINALLY VIOLATED one.** A NACA 0012 at
> `alpha = 8 deg` has `Cp_min ≈ −3.0` to `−3.2`, so
> `|U|_max = U_inf sqrt(1 − Cp_min) = ` **`20.0`–`20.5 m/s`** — at or above the
> bound, on a perfectly healthy solution. Both forms share one root error:
> **the threshold was a multiple of an INLET SCALE, and the quantity it bounds is a
> SOLUTION PEAK.** L-409 remedy 2 applies verbatim: derive the threshold from the
> level's own predicted value with a stated margin.

**Registered construction.** For each row, a peak speed is **predicted** from the
row's own physics, and the bound is a stated multiple of it:

```
    U_peak_pred = max( V_j ,  U_inf * (u/U)_peak )
    (u/U)_peak  = 1.196 + 6.108 * alpha_eff        alpha_eff = CL_pred / (2 pi)   [rad]
    BOUND:  max|U|  <  M * U_peak_pred             M = 2.0   (registered margin)
```

**Basis of `(u/U)_peak`, stated so it can be attacked.** It is a two-point linear
calibration of the unblown NACA 0012 surface-speed peak against incidence:
`1.196` at `alpha = 0` (thickness alone, `Cp_min = −0.430`) and `sqrt(1 − (−3.2))
= 2.049` at `alpha = 8 deg` (`Cp_min = −3.2`), giving the slope
`(2.049 − 1.196)/0.13963 = 6.108 /rad`. For a **blown** row the incidence is
replaced by the **effective incidence that would produce the same lift on the
unblown section**, `alpha_eff = CL_pred/(2 pi)`, with `CL_pred` the §7.3 theory
value for that row. This is a **surrogate for a guard**, not a physics claim, and it
is registered as such: it is never gated, never reported as a prediction of `Cp_min`,
and never compared against the measured field as if it were one.

| row | `C_mu_jet` | `alpha` | `V_j` (m/s) | `CL_pred` | `U_e` peak (m/s) | **`U_peak_pred`** | **BOUND `= 2 U_peak_pred`** |
|---|---|---|---|---|---|---|---|
| G1 | 0.00 | 0 | 0.000 | 0.0000 | **11.960** | **11.960** | **23.920** |
| G2 | 0.05 | 0 | 22.361 | 0.4234 | 16.076 | **22.361** | **44.721** |
| G3, G6, G7, S1 | 0.10 | 0 | 31.623 | 0.6048 | 17.839 | **31.623** | **63.246** |
| G4 | 0.20 | 0 | 44.721 | 0.8687 | 20.405 | **44.721** | **89.443** |
| G5 (ungated exhibit) | 0.40 | 0 | 63.246 | 1.2595 | 24.204 | **63.246** | **126.491** |
| G8 | 0.10 | 4 | 31.623 | 1.0740 | 22.400 | **31.623** | **63.246** |
| G9 | 0.10 | 8 | 31.623 | 1.5432 | 26.962 | **31.623** | **63.246** |

**Three properties of this construction are registered because each was a defect in
the struck version.**

1. **It is satisfiable on every row, including the unblown one.** G1's bound is
   `23.920 m/s` against a predicted peak of `11.960` — a factor 2 of headroom
   where the struck bound gave `20.0` against `20.0`–`20.5`, i.e. **none**. Even the
   unblown `alpha = 8 deg` case, which the O4 ruling removes from the matrix, would
   clear it at `20.5 < 23.9`.
2. **It loses no detection power.** A diverging `simpleFoam` solution reaches
   `1e2`–`1e30 m/s` or `NaN`; every bound above is exceeded by **one to twenty-eight
   orders of magnitude** in that event. The guard's job is catching runaway, and a
   2× margin does not blunt it.
3. **It reduces to the directive's own form wherever the jet dominates.** On every
   blown row `V_j > U_e`, so the bound is exactly `2 V_j` — the directive's
   `max|U| < 2 V_j`, recovered rather than overridden. The construction differs from
   the directive **only** where the directive is undefined, which is the unblown row.
   That coincidence is a check on the construction, not a coincidence relied upon.

**Registered reporting, so a near-miss is visible instead of binary:** the
comparator prints `max|U|`, its cell location, `U_peak_pred` and the ratio
`max|U| / U_peak_pred` **on every row**. A row whose ratio exceeds **1.2** is
reported as **guard-marginal** — a REPORTED diagnostic, never a gate arm and never a
verdict — so that a physically interesting peak is discussed rather than discovered
at the moment a bound fires. `NaN` or `Inf` anywhere in `U` is an unconditional
refusal independent of the bound.

#### 5.5b CONTINUITY — THE GATED QUANTITY IS `sum local`, AND `cumulative` IS REPORTED (amended 2026-08-31, item **A12** of §17)

> ~~"continuity error `max` < 1e-8 (cumulative **and** local)"~~ — **STRUCK as to
> `cumulative`.** OpenFOAM's `cumulative` continuity error is a **running sum of the
> per-iteration global error over the whole run**; its magnitude therefore depends on
> **how many iterations were taken**, which under `residualControl` is not a
> registered number but an outcome varying from 2 000 to 20 000 across the matrix.
> Gating a bookkeeping accumulator whose scale is set by the iteration count, at a
> fixed threshold, against a criterion that means "the final field conserves mass",
> is L-409's class: **a threshold applied to a quantity whose floor is not set by
> what the threshold is meant to mean.** Two rows with identical final fields would
> receive different verdicts for having converged at different iterations.

**Registered:** the gated quantity is the **`sum local` continuity error printed at
the FINAL iteration** — a volume-weighted mean of `|div phi|`, a property of the
final field alone and independent of the iteration count — with the bound
**`< 1e-8`**. `global` and `cumulative` are **REPORTED on every row and gated on
none**; they are diagnostics of the run's history, not of its answer, and no row's
verdict may cite them.

**The L-409 division, and the one threshold in this document I cannot certify
pre-compute.** Converged steady `simpleFoam` RANS solutions customarily print
`sum local` in the `1e-9`–`1e-11` range, i.e. **10× to 1000× below the registered
`1e-8`**. That is a statement about general solver behaviour drawn from practice —
**it is NOT a measurement on this case, and no artifact on this box supports it.**
The floor of `sum local` is set by the pressure equation's linear-solver tolerance
and `relTol`, not by the SIMPLE residual, so it is reachable by construction but its
margin is unverified here. **Raised to the supervisor as open item O6 (§16), which
must be ruled before the freeze**, because rule 2 closes thresholds at first compute
and stage F/P are compute.

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
`≥ 36` BL layers at growth `≤ 1.15`, `≥ 12` cells across `h`, the `checkMesh`
limits of §4.5 and a cell budget **simultaneously**. §4.2/§4.3 show a block layout
and a **solved** normal distribution that meet them on paper, at **46 180 / 86 638
/ 161 006** cells — **13–14 % above §1.3's ~40 k / ~75 k / ~140 k targets, and that
departure is registered in §4.2 rather than hidden: `max(y+) ≤ 1` is a gate and a
cell count is a target, so the gate wins.** **If the script cannot meet the
constraint set in fact, that is a stage-F finding and the answer is `BLOCKED`,
reported with the binding constraint named — the constraints are NOT quietly
relaxed to let the programme continue.**

> **AND STAGE F IS COMPUTE.** Rule 2 closes gates, thresholds, caps and labels at
> **first compute**, not at first *gated* compute. **The moment F1 runs, nothing in
> §4, §5, §7 or §12 can be amended.** Every threshold this document registers must
> therefore be defensible before F1, which is why §16's O6 must be ruled before the
> freeze and not calibrated at stage P. §5.4's relaxation factors are the one
> setting §5.4 explicitly permits to be fixed during F/P — they are a solver
> setting, not a gate, threshold, cap or label.

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
> | `models/curriculum/results/naca0012_wing.json` | `Cd = 0.02229` at **zero lift** (`CL = −0.000795`, i.e. `alpha = 0`), band ±30 % vs Abbott & von Doenhoff (1959) **section** data `Cd = 0.009`; verdict `TREND ONLY`, 148 % off | **Single alpha — no slope at all.** And its verdict was **overturned**: `verification/campaign/W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md` finds four independently regenerated meshes at the same nominal resolution give `Cd` = **0.009454, 0.009605, 0.010630, 0.012052** — range 2.5987e-03, a **21.6 % spread OF THE PUBLISHED VALUE** — enough to flip the ±30 % verdict on mesh-generation noise alone; the published mesh is the **maximum** of the four and the only one outside the band. Its grid-convergence claim was separately ruled **`NOT A RESULT`** (`verification/campaign/LADDER_RECIPE_RULING_2026-08-25.md`). It is also scored on a **planform-area basis against section data**, a basis mismatch the record itself notes. |
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
> to rescue it. **The supervisor was asked to rule (open item O4) between:**
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
> ---
>
> ### RULING ON O4 — OPTION (c). **GATE V IS `BLOCKED`. THE CASE IS GATED ON G AND THEORY ALONE.**
>
> **Ruled by: `cfd-supervisor`, 2026-08-31, pre-compute and pre-freeze.** Recorded
> here by the lane that implemented it, **as the supervisor's decision and not as
> this lane's**; the reasoning below is the supervisor's, transcribed.
>
> **The decisive reason, and it stands alone before any of the others.** Sanaa's
> §1.5 asks for a **regression against our own record, in the same mesh family**.
> The only candidate the search returned, `cases/tmr/naca0012_status.json`, is a
> single coarse rung at **`y+ = 9.664` — a WALL-FUNCTION-regime solution.** JF1 is
> registered at **`y+ ≤ 1`, low-Re, with no wall functions** — §1.4's own words are
> *"no wall functions — the jet/BL interaction is the physics"*, and §4.3 sizes the
> entire wall-normal distribution to honour it. **A different wall treatment is a
> different mesh family, so it cannot supply a same-family regression.** That is
> dispositive on its own, **before** the candidate's other disqualifications — its
> own refusal sentence (*"a single coarse rung supports no comparison claim and none
> is made"*), its `cd_pressure` of **−0.001479** (a negative pressure drag), and its
> unresolved non-decaying force oscillations.
>
> **Consequently option (a) has no record to name**, and **option (b) would
> manufacture a NEW gate in place of the regression Sanaa asked for** — a
> first-principles `2 pi` band is not a regression against our own record, and
> registering it under the name "V" would answer a question she did not ask while
> appearing to answer the one she did. **Option (c) is taken.**
>
> ### THE ABSENCE IS RECORDED AS A FINDING, NOT AS AN INCONVENIENCE
>
> > **FINDING (JF1-V1), registered as a statement about this lab's coverage and not
> > about this case:** *Certonomous holds no unblown NACA 0012 record at low-Re
> > (`y+ ≤ 1`, no wall functions) wall treatment fit to serve as a same-family
> > regression comparand. The nearest artifact is a single coarse wall-function
> > rung at `y+ = 9.664` that refuses the comparison in its own words.*
>
> **No comparand is manufactured to fill it.** The gap is the result. It is
> registered so that the next case needing an unblown NACA 0012 datum finds the
> absence documented with its reason, rather than re-running the same search and
> re-discovering it — and so that if the lab later decides to build such a record,
> the requirement it must meet (`y+ ≤ 1`, no wall functions, a real `CL(alpha)`
> sweep, a band, a Roache triple) is already written down.
>
> **Mechanical consequences of the ruling, all applied in this document:**
>
> | Consequence | Where |
> |---|---|
> | Gate V is `BLOCKED`; it has no arms and no bands | this §7.1 |
> | **G10** and **G11** (`C_mu_jet = 0`, `alpha` = 4 and 8) **are struck from the run matrix** | §10 |
> | **G1** (`C_mu_jet = 0`, `alpha = 0`) **is RETAINED as a REPORTED map point**, ungated — §1.1 lists the unblown case as the reference for the `C_mu_jet` map, and that role is untouched by V's collapse | §10 |
> | The gate set is **G (Roache triple) and THEORY (a) and (b)**, and nothing else | §7.2, §7.3 |
> | **No row's verdict may cite `Cd`** — with V gone there is no gated `Cd` arm anywhere in this registration | §7.5, §16 O2 |
> | 20.0 core-min of G10/G11 leave the cost | §12 |
>
> **A `BLOCKED` gate is not a failed gate and may never be reported as one.** JF1's
> verdict is composed from G and THEORY; V contributes the word `BLOCKED` and the
> finding above, and contributes nothing else in either direction.
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
> load-bearing number, the **21.6 %-of-the-published-value spread, was and is
> correct** and is confirmed
> arithmetically (0.012052 − 0.009454 = 2.598e-03, `W3:37`), so the conclusion —
> gate V `BLOCKED` — is unaffected. Recorded here because a wrong number in an
> evidentiary table is a defect whether or not it changes the verdict, and
> because this lab's own precedent (`e779bdc7`) is to disclose such a repair
> inline rather than quietly overwrite it.
>
> **SECOND CORRECTION, SAME DISCLOSURE RULE (2026-08-30, pre-compute, pre-freeze;
> same condition, re-checked: no run root, no compute).** Every percentage in this
> section now carries its **denominator**, because a percentage without one is
> three different numbers. The 2.5987e-03 range is **21.56 % of the published
> value (0.012052229)**, but **24.90 % of the four-mesh mean (0.010435363)** and
> **27.49 % of the minimum (0.009454)**. `W3:37` names its denominator — *"21.6 %
> of the published value"* — and is self-consistent; a reader who recomputes the
> spread **without** carrying that denominator gets 24.9 % or 27.5 % and concludes
> our own record is wrong. As first committed, this document quoted the bare
> figure. It no longer does. Recorded as **L-408**, whose fourth call site is
> exactly this.
>
> **A caution that bears directly on option (b) and on gate G.** The W3 finding
> above — a `Cd` spread of **21.6 % of the published value** on this same body
> from mesh-generation noise alone, at fixed nominal resolution — is a measured
> statement about how fragile a NACA 0012 `Cd` is to *how the mesh was built*. It is the strongest available
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

which can plausibly exceed the band of a sharp-TE `Cd` record. ~~**Registered
resolution, subject to O2:** gate V is **split**; the `CL-alpha` slope arm is gated
against the named record and the `Cd` arm is gated against a blunt-base band the
supervisor registers at the freeze.~~ **STRUCK — SUPERSEDED BY THE O4 RULING
ABOVE.** With V `BLOCKED` there is no V to split and no gated `Cd` arm anywhere in
this registration.

**What survives the ruling, and it is not nothing.** `Cd` is **REPORTED on every
row**, with the **measured base `Cp` and the derived base-drag increment stated
beside it**, so the 6–19 % blunt-base contribution is a published number on the
record rather than a hidden one. It is reported and **never gated**, and **no row's
verdict may cite it** (§7.5's rule now covers `Cd` explicitly). The base-drag table
above is retained as the pre-registered expectation against which the measured
increment is read. **O2 is disposed of in §16 as a consequence of this ruling, not
by a separate band decision.**

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

`GCI_fine = Fs × |eps_21 / f_1| / (r_21^p − 1)` at `Fs = 1.25`, in the
non-constant-`r` form (§4.2), **with the Roache indices as §4.2 registers them:
`f_1 = CL_total(L3)` (finest), `f_2 = CL_total(L2)`, `f_3 = CL_total(L1)`
(coarsest); `eps_21 = f_2 − f_1` is the L2–L3 difference and `eps_32 = f_3 − f_2`
is the L1–L2 difference.** ~~`eps_21` the relative difference between L1 and L2~~ —
**STRUCK, the indices were inverted; see §4.2, where the error and its 1.9×
consequence for the reported GCI are set out.**

Observed order from the non-constant-`r` iterative form, converged in `p`:

```
    p = | ln|eps_32/eps_21| + q(p) | / ln(r_21)
    q(p) = ln[ (r_21^p − s) / (r_32^p − s) ],     s = sign(eps_32/eps_21)
```

A worked, satisfiable instance of this triple — actual numbers on the actual
levels — is registered in **§17.3**, per L-409's satisfiability requirement.

### 7.3 Gate THEORY — `CL_total` against ARC R&M 3304 p.5 eq. (2)

**Source form only (§1.4). The directive's grouping is never used as a comparand.**

**Arm (a) — `C_mu_jet` sweep at `alpha = 0`, `tau = 30 deg`, on L1:**

`CL_theory = tau × (dCL/dtheta)_inf` with `tau = pi/6 = 0.5235987755982988 rad` and
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
= **6.7208116310 /rad = 0.1173002914 /deg** at `C_mu_jet = 0.1`.

*(Amended 2026-08-31, item **A13** of §17: the per-degree value read
~~`0.1173002851`~~ as first committed. `6.7208116310 × pi/180 = 0.1173002914`; the
struck value is wrong in its **8th significant figure**. **Immaterial to the gate** —
the gate is stated and computed in radians and the `/rad` comparand is correct to
all ten digits — but a document that quotes ten digits everywhere does not get to
carry a wrong one, and a downstream reader who took the `/deg` figure as the
comparand would inherit a `5.4e-08` relative error.)*

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
| Continuity closure | **`sum local`** continuity error at the final iteration `< 1e-8` (§5.5b; `global` and `cumulative` are REPORTED, not gated) | `NOT A RESULT` |
| `k`, `omega` realisability | `k ≥ 0`, `omega > 0`, `nut/nu < 1e5` everywhere — **satisfiable at `C_mu_jet = 0` only because §5.2's floor makes `omega_jet = 63.888 > 0`** | `NOT A RESULT` |
| `min(k)` in the jet core | `> 0` — **`N/A` at `C_mu_jet = 0`: there is no jet and therefore no jet core.** Recorded `N/A`, never as `0` and never as a pass (rule 3) | `NOT A RESULT` where applicable |
| `y+` measured | `max(y+) ≤ 1` on `airfoil`, measured from the solved field; §4.3 sizes `y1` so this is reachable, with a predicted L1 max of **0.9419** | `NOT A RESULT` |
| Jet-sheet resolution | ≥ 8 cells across the `max\|U\|` locus at `x/c = 1` — **`N/A` at `C_mu_jet = 0`**, recorded as `N/A` | `NOT A RESULT` where applicable |
| Frame consistency | `jetSlot` `U` bytewise identical across `alpha` ∈ {0,4,8} at fixed `C_mu_jet`; `farfield` value `= U_inf(cos a, sin a, 0)` to 1e-9 (§1.6a) | comparator **refuses (exit 2)** |
| `t_z` cross-check | `area(jetSlot) = 0.005 m²` to 1e-9 (§5.6) | comparator **refuses (exit 2)** |

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
`Cp` distribution, blown vs unblown, at every `C_mu_jet`; **`Cd`, with the measured
base `Cp` and the derived base-drag increment beside it (§7.1 — under the O4 ruling
there is NO gated `Cd` arm anywhere in this registration)**; `max|U|` with its
location, `U_peak_pred` and the guard ratio (§5.5a); `global` and `cumulative`
continuity error (§5.5b); the decomposition digest and `DECOMP_SEED` (§9.4);
`CL_aero` alongside `CL_total` on every row.

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

> **CLAUSES 3 AND 5 WERE REWRITTEN 2026-08-31 (item A14 of §17). AS FIRST
> COMMITTED THIS COMPARATOR REFUSED EVERY POSSIBLE RUN.** ~~"3. Last time written
> == `endTime`. … 5. `ExecutionTime` line count == `endTime`."~~ — **STRUCK.**
> Those are the thermal families' clauses, written for a **fixed-`endTime`** run.
> This family runs under `residualControl`, so:
>
> - **With `residualControl` active, every CONVERGED run stops EARLY** at some
>   `N < 20 000` — the last time written is `N`, not `endTime`, and struck clause 3
>   **refused it**.
> - **Without `residualControl`, every run reaches `endTime = 20 000`** — which
>   §5.5 and §8.4 make **the iteration cap**, and hitting the cap is
>   **`NOT A RESULT`**.
>
> **There was no third option. No run of this case could have been graded.** The
> document had carefully adapted clause **4** (this family's field list) and clause
> **6** (age guard against `0/U`, since there is no `0/T`) and never adapted 3 and 5
> for an **early-exit** run. This is **L-409**, second instance, found before compute
> while rule 2's amendment window was open; `F23b` met the same class **after**
> compute and ended `BLOCKED` and unrepairable.

1. **`rc = 0`** — the solver's own return code, captured **inside** the wrapper
   (§9.2), never the launcher's.
2. **An `End` line** is present in `log.simpleFoam`.
3. **TERMINATION — exactly one of the two branches below holds, the comparator
   records WHICH, and every other termination is a refusal.**

   First, **`controlDict` is pinned** (this replaces the guarantee the struck
   clause got for free from comparing against a registered `endTime`): the
   comparator reads `system/controlDict` from the case and **refuses (exit 2)**
   unless `endTime == 20000`, `deltaT == 1`, `startTime == 0`, `writeControl ==
   timeStep` and `writeInterval == 20000`, and reads `system/fvSolution` and
   refuses unless the four `residualControl` keys are exactly `p 1e-6; U 1e-6;
   k 1e-6; omega 1e-6;` (§5.5). **A run whose termination settings were changed is
   not a run of this registration.**

   Let `N_stop` = the name of the last time directory written.

   **3a — CONVERGED EARLY EXIT. This is the only COMPLETE termination.** All of:
   - `log.simpleFoam` contains the literal line
     `SIMPLE solution converged in <N> iterations`, exactly once;
   - `N == N_stop`, i.e. the integer in that line **is** the last time directory;
   - `2000 ≤ N_stop < 20000` — below 2 000 the §5.5 plateau window does not exist
     and the run is `NOT A RESULT`; at 20 000 see 3b;
   - the final iteration's initial residuals for `p`, `Ux`, `Uy`, `k`, `omega`,
     read from the log, are all `< 1e-6`.

   *(Mechanism, verified in the v2606 source on this box rather than assumed:
   `simpleControl::loop()` — `simpleControl.C:144–153` — tests `criteriaSatisfied()`
   at the top of the iteration, prints the converged line with the CURRENT
   `timeName()`, and calls `runTime.writeAndEnd()`, which at `TimeIO.C:600–606` sets
   `endTime_ = value()` and **returns `writeNow()`** — so the fields ARE written, at
   time `N`, immediately. `Time::loop()` (`Time.C:865–875`) then finds
   `run() == false` and does not increment. Hence exactly `N` `ExecutionTime` lines,
   a single time directory `N`, `End`, and `rc = 0`.)*

   **3b — CAP HIT. `NOT A RESULT`, and it is not a refusal to be argued with.**
   `N_stop == 20000` **and** no converged line. The solver ran the full cap without
   meeting the residual criteria. §5.5's registered words apply verbatim: *a run
   that hits the cap is `NOT A RESULT`, never "close enough"*.

   **3c — ANY OTHER TERMINATION IS A REFUSAL, AND THIS BRANCH IS WHY CLAUSE 3
   STILL HAS TEETH.** If `N_stop < 20000` **and** there is no converged line naming
   `N_stop`, the run stopped early for a reason that is **not** convergence —
   solver divergence, `FatalError`, a signal, an out-of-memory kill, a wall-clock
   `timeout`, a lost MPI rank, a truncated log, or a hand-stopped solve. The
   comparator **refuses (exit 2)** and the row is **`NOT A RESULT`**, with
   `N_stop`, `rc`, the last log line and the presence/absence of `End` printed
   beside it. **Loosening clause 3 to admit an early exit must not loosen it into
   admitting an early STOP; 3c is the clause that keeps those two apart**, and it
   is exercised by its own mutation limb in §8.2.

4. **Fields present at `N_stop`**: `U p k omega nut` (this is an incompressible
   isothermal case; the thermal family's `T alphat p_rgh` do not exist here and
   are **not** required — the clause is the *family's field list*, and this
   family's list is the one just named).
5. **`ExecutionTime` line count == `N_stop`** (one per completed outer iteration),
   **not** `== endTime`. Under 3a this equals the converged line's `N`; under 3b it
   equals 20 000 and the row is already `NOT A RESULT`. A mismatch between the
   `ExecutionTime` count and `N_stop` means the log and the written fields disagree
   about how many iterations were taken, and is a refusal in either branch.
6. **THE AGE GUARD — every field at `N_stop` is NEWER than the case's own
   `0/U`.** `0/U` is touched last at launch and therefore dates the run that was
   allowed to produce the answer. (The thermal families use `0/T`; this family
   has no `T`, so `0/U` is the registered age datum and the wrapper touches it
   last at launch — §9.2.)

**A pre-launch guard REFUSES to start a case whose run directory already contains
`0/` or any time directory.** A restart into a populated directory is not a run;
it is an answer of unknown parentage.

**Registered, as the general statement of what went wrong here:** every clause of a
completion rule inherited from another family **must be re-derived against this
family's termination mode**, and the re-derivation must be written down clause by
clause. Clauses 4 and 6 were re-derived; 3 and 5 were copied. **A copied clause is
not a checked clause.**

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

**Fatal-clause control — one mutation limb per completion clause of §8.1.**
**TEN limbs** (amended 2026-08-31, item **A15** of §17 — six as first committed,
raised to ten because clause 3 now has three branches and a pinned `controlDict`,
and **an unexercised branch is an unenforced branch**). Each mutates exactly one
clause on a byte-level copy of a real completed case and **requires the comparator
to refuse.** A limb that does not produce a refusal means that clause is not
enforced and the whole comparator is **`NOT A RESULT`** until it is.

| # | Clause | Mutation applied to the copy | Required outcome |
|---|---|---|---|
| M1 | 8.1(1) | `solver_rc` set non-zero in `artefacts/RUN_STATUS.*` | refuse |
| M2 | 8.1(2) | the `End` line removed from `log.simpleFoam` | refuse |
| M3 | 8.1(3) pin | `endTime` in `system/controlDict` changed 20000 → 15000 | refuse |
| M4 | 8.1(3) pin | `residualControl { p }` changed 1e-6 → 1e-4 in `system/fvSolution` | refuse |
| M5 | **8.1(3a)** | the converged line's iteration number changed so it no longer equals `N_stop` | refuse |
| M6 | **8.1(3a)** | the time directory renamed so `N_stop = 1500 < 2000` (plateau window absent) | refuse |
| M7 | **8.1(3b) — the CAP** | time directory renamed to `20000` and the converged line deleted | refuse, labelled cap hit |
| M8 | **8.1(3c) — the EARLY STOP** | the converged line deleted, `End` retained, `rc = 0` retained, `N_stop` left below 20000 — **the exact signature of a killed or timed-out run that still looks tidy** | refuse |
| M9 | 8.1(4)/(5) | one field deleted from `N_stop/`; separately, one `ExecutionTime` line removed | refuse (both) |
| M10 | 8.1(6) | `0/U` touched **after** the `N_stop` fields, to trip the age guard | refuse |

**M8 is the limb that matters most and it is registered as such.** It is the case
that the struck clause 3 would have caught **by accident** — because a killed run
also fails `last time == endTime` — and that a naively loosened clause 3 would let
through. **The repair of an unsatisfiable clause must not become the removal of a
working one, and M8 is the control that proves it did not.**

All plant and mutation outputs are written to
`verification/runs/JF1_jet_flap/artefacts/plant_control_<date>.txt` and are
**preserved**; a number whose artefact is gone is not a result.

### 8.3 Verdict emission

The comparator emits **only** the six words of rule 1 — `PASS`, `GATE REACHED`,
`GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`. It has no other verdict string
and no adjectives. A row is one word plus its value, interval, chip and
uncertainty channels. **There is no softer word available to it.**

### 8.4 Registered refusals — the complete list

The comparator refuses (exit 2) if: any §8.1 clause fails — including the
`controlDict`/`fvSolution` pin of clause 3, the **cap-hit** branch 3b and the
**early-stop** branch 3c; any §8.2 plant is invisible; any of the **ten** §8.2
mutation limbs fails to refuse; a triple is handed to the constant-`r` branch with
`|r_21 − r_32|/r_21 > 1 %`; a GCI is requested on a non-monotone triple; **the
Roache index mapping does not match §4.2 (fine = L3)**; `max(y+) > 1` measured; the
jet mass-flow mismatch exceeds 0.5 %; **`area(jetSlot) ≠ 0.005 m²` to 1e-9** (the
`t_z` cross-check, §5.6); **the `jetSlot` `U` entry differs across the `alpha` sweep
or a `farfield` value does not match `U_inf(cos a, sin a, 0)` to 1e-9** (the frame
assertion, §1.6a); the frozen-file md5 does not match the committed blob; **`U`
contains `NaN` or `Inf`**; the **`sum local`** continuity error at the final
iteration exceeds 1e-8; or any absolute bound of §5.5 — including the per-row
blow-up bound of §5.5a — is violated.

**The comparator never emits `N/A` as a pass.** Where §7.4 registers a check as
`N/A` at `C_mu_jet = 0` (jet mass flow, jet-core `min(k)`, jet-sheet resolution) the
row prints the literal `N/A` and the reason; it never prints `0.0 %`, never prints
`OK`, and the `N/A` is never counted toward a `PASS` (rule 3).

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
| G1 | G | **0.0** | 0 | L1 | **unblown map point — REPORTED, UNGATED.** §1.1 lists the unblown case as the reference for the `C_mu_jet` map and that role survives; **gate V is `BLOCKED` (§7.1, O4 ruling) so this row serves no gate arm.** It is run, reported and cited as a map point, and no verdict rests on it |
| G2 | G | 0.05 | 0 | L1 | map + THEORY (a) |
| G3 | G | **0.1** | 0 | L1 | map + THEORY (a) + **triple L1** |
| G4 | G | 0.2 | 0 | L1 | map + THEORY (a) |
| G5 | G | 0.4 | 0 | L1 | map + **departure exhibit, outside the gate** |
| G6 | G | 0.1 | 0 | **L2** | **triple L2** + alpha-sweep `alpha=0` |
| G7 | G | 0.1 | 0 | **L3** | **triple L3** |
| G8 | G | 0.1 | 4 | L2 | THEORY (b) |
| G9 | G | 0.1 | 8 | L2 | THEORY (b) |
| ~~G10~~ | ~~G~~ | ~~0.0~~ | ~~4~~ | ~~L1~~ | ~~gate V~~ — **STRUCK 2026-08-31. The supervisor ruled O4 via option (c); gate V is `BLOCKED` and these rows serve nothing. NOT RUN.** |
| ~~G11~~ | ~~G~~ | ~~0.0~~ | ~~8~~ | ~~L1~~ | ~~gate V~~ — **STRUCK, as G10. NOT RUN.** |
| S1 | ungated | 0.1 | 0 | L1, `l_j = 0.14 h` | §5.2 sensitivity, reported never gated |
| **S2** | ungated | 0.1 | 0 | L1, **freestream branch A** | **CONDITIONAL on the supervisor's O3 ruling.** §5.3 sensitivity — measures the 22.36× `nut_inf` gap instead of arguing it. Reported, never gated, never a comparand |

**Rows actually run under the O4 ruling: F1–F4, P1, G1–G9, S1** (and S2 if the
supervisor rules O3 that way). **G10 and G11 are not run.** The gated set is
G3/G6/G7 (gate G) and G2/G3/G4 + G6/G8/G9 (gate THEORY (a) and (b)); G1 and G5 are
reported map points carrying no verdict.

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

**2. THE JET-REACTION CONVENTION — A 1.9 % ERROR IN `CL_theory` AT `alpha = 8 deg`,
AND FREE TO GET RIGHT.**

*(Heading corrected 2026-08-31, item **A16** of §17. It read ~~"8.3 % OF
`CL_theory` AT `alpha = 8 deg`"~~. **8.27 % is the SIZE OF THE DIRECTIVE'S OWN TERM
as a fraction of `CL_theory(alpha=0)` — it is not the discrepancy between the two
conventions**, which is what an error-source heading in a ranked list of error
sources states. The discrepancy is `0.0615661 − 0.0500000 = 0.0115661`, i.e.
**1.9125 %** of `CL_theory(alpha=0) = 0.6047757` — the figure §1.6 computes — and
**0.7495 %** of the full theory lift at `alpha = 8 deg`. The struck heading
overstated this error source by **4.3×** and would have mis-ranked it against
source 3 (the grouping, 3.04 % at the gate point), which is in fact the larger of
the two. Both were fixed at zero cost, so no verdict moves; the ranking in a
pre-registered expectation is nonetheless a claim, and it was wrong.)*

The registered term `C_mu_jet sin(tau + alpha)` is **0.0615661** at
`alpha = 8 deg`, `C_mu_jet = 0.1`, i.e. **10.18 %** of
`CL_theory(alpha=0) = 0.6047757`; the directive's `sin(tau)` form gives
**0.0500000**, i.e. **8.27 %**. The **error** is the difference between them:
**1.9125 %** of `CL_theory(alpha=0)`, and **1.2325 %** of the theory slope on arm
(b). Fixed by §1.6 and §1.6a at zero cost. Residual after the fix: **zero** — it is
a definition, not an uncertainty.

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

**RECOSTED 2026-08-31 (item A17 of §17), for two independent reasons, and every
line re-added from scratch rather than adjusted:**

1. **G10 and G11 leave the matrix** under the O4 ruling (§7.1) — **−20.0 core-min**.
2. **The mesh grew** under §4.3's `y+` repair — L1 **+13.58 %**, L2 **+14.11 %**,
   L3 **+13.32 %** (46 180/40 660, 86 638/75 928, 161 006/142 086). §1.6's per-solve
   estimates were written for the smaller levels; **carrying them forward unchanged
   would be reporting a cost we know to be low.** They are scaled by the cell ratio,
   which is the honest first-order correction for a fixed iteration count.

| Per-solve | §1.6 as adopted | cell ratio | **corrected** |
|---|---|---|---|
| L1 | 10 | 1.1358 | **11.36** |
| L2 | 25 | 1.1411 | **28.53** |
| L3 | 60 | 1.1332 | **67.99** |

| Item | Runs | core-min each | core-min |
|---|---|---|---|
| F1–F3 mesh generation + `checkMesh`, three levels | 3 | 1.50 | **4.50** |
| F4 L1 first-order feasibility, 2000 iterations | 1 | 4.54 | **4.54** |
| P1 L1 second-order physics/diagnostic | 1 | 11.36 | **11.36** |
| G1–G5 `C_mu_jet` map, L1 (5 points) | 5 | 11.36 | **56.79** |
| G6 triple L2 (**L1 reused from G3**) | 1 | 28.53 | **28.53** |
| G7 triple L3 | 1 | 67.99 | **67.99** |
| G8, G9 alpha sweep L2 (**`alpha=0` reused from G6**) | 2 | 28.53 | **57.05** |
| ~~G10, G11 gate V~~ | ~~2~~ | ~~10~~ | **0 — STRUCK, O4 ruled option (c)** |
| S1 mixing-length sensitivity, L1, ungated | 1 | 11.36 | **11.36** |
| | | **SUBTOTAL** | **242.11** |
| Named reserve: **one L2 re-run** after a completion-rule refusal | — | 28.53 | **28.53** |
| | | **TOTAL against the cap** | **270.64** |
| *(conditional)* S2 freestream-branch-A sensitivity, L1, ungated — **only if the supervisor rules O3 that way** | 1 | 11.36 | *(+11.36)* |
| | | *(TOTAL with S2)* | *(**282.00**)* |

> **REGISTERED CAP: 300 core-minutes for the primal family**, as §1.6 sets it —
> **unchanged; it is Sanaa's number and this lane does not move it.**
> Slack against the cap: **29.36 core-min (9.8 %)**, or **18.00 core-min (6.0 %)**
> if S2 is authorised.

**THE RESERVE WAS DELIBERATELY DOWNGRADED FROM AN L3 RE-RUN TO AN L2 RE-RUN, AND
THAT IS A REGISTERED STATEMENT ABOUT WHAT THIS PROGRAMME CANNOT AFFORD.** With the
corrected per-solve figures, a reserve covering **one L3 re-run** gives
`242.11 + 67.99 = ` **`310.10 core-min`**, which **exceeds the 300 cap by 10.10
core-min (3.4 %)**. Rather than quietly keep the old reserve line and let the total
sit over the cap, or quietly raise the cap, the position is registered as it is:

> **A completion-rule refusal on the single L3 run (G7) cannot be re-run inside this
> cap.** It is registered **now**, pre-compute, that such a refusal makes gate G
> **`BLOCKED` on budget** — reported with the refusing clause named — and escalates
> to the supervisor. It does **not** silently consume the reserve, and it does not
> get a new budget (rule 12: *an overrun stops the run; it does not get a new
> budget*). **This is open item O7.** The supervisor may set the cap to any value at
> freeze time (§12's own clause below); ≥ **315** would cover a full L3 reserve. That
> is a change to Sanaa's §1.6 number and is worth her eye, not merely a supervisor's.

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

**Derived dollar figure, labelled:** the registered total of **270.64 core-min** =
4.511 core-hours × **$0.0513 /core-h** (c7a.4xlarge, **owner-stated
2026-08-21/22**) = **$0.2314 — DERIVED, NOT MEASURED** (**$0.2411** if S2 is
authorised; **$0.2565** at the full 300 core-min cap). The box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5), so no cost figure produced on this box is
a measurement. This is far below the $25 pre-authorisation threshold.

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

**STATUS 2026-08-31, after the freeze-readiness audit and the repair pass.**
**O4 is RULED** (option (c), §7.1) and **O2 falls out as a consequence of that
ruling**. **O1 is REPAIRED** and its residue is folded into §5.5a. **O3 and O5
remain open.** **O6 and O7 are NEW** and were raised by the repair pass itself.
**NOTHING HAS BEEN QUIETLY FIXED.** Where this draft registers a working
resolution it says so, states the alternative, and leaves the ruling to the
supervisor.

| Item | State |
|---|---|
| **O1** blow-up guard | **REPAIRED**, §5.5a — the residue is a registered margin, not an open decision |
| **O2** blunt-base `Cd` band | **MOOT** under the O4 ruling — no gated `Cd` arm exists; recommendation below |
| **O3** freestream branch | **OPEN — the supervisor's.** Recommendation below, not a decision |
| **O4** gate V's premise | **RULED**, option (c), §7.1 — `BLOCKED`, with the absence recorded as a finding |
| **O5** `Aref` / `t_z` | **OPEN** — §5.6 registers a working resolution and an independent cross-check |
| **O6** continuity threshold | **NEW, OPEN — must be ruled before the freeze** |
| **O7** L3 reserve vs the cap | **NEW, OPEN** |

**O1 — REPAIRED. The blow-up guard was unsatisfiable, then marginally violated;
it is now derived from each row's own predicted peak.**
§1.4 registers `max|U| < 2 V_j`. The sweep contains `C_mu_jet = 0.0`, where
`V_j = 0`, so the guard reads `max|U| < 0` — **impossible for any flow**. This
document's first repair, `max|U| < 2 × max(V_j, U_inf)` = **20.0 m/s** at
`C_mu_jet = 0`, **replaced an unsatisfiable bound with a marginally violated one**:
a NACA 0012 at `alpha = 8 deg` reaches `|U|_max = 20.0`–`20.5 m/s` on a healthy
solution. **§5.5a now derives the bound from the row's own predicted peak velocity
with a registered margin of 2.0** (L-409 remedy 2), giving `23.92 m/s` at
`C_mu_jet = 0` against a predicted `11.96`, and reducing **exactly** to the
directive's `2 V_j` on every blown row. **No open decision remains**; the margin,
its basis and the `(u/U)_peak` surrogate are all registered and attackable in
§5.5a.
*Two notes for the supervisor, neither of which reopens the item.* (i) Under the
O4 ruling the specific row that violated the struck bound — unblown `alpha = 8 deg`
— **leaves the run matrix** with G11, so the violation would not have fired in
practice; the repair stands anyway, because a bound that is wrong in principle and
merely unexercised in this matrix is a defect waiting for the next matrix. (ii) The
related `jetSlot`-at-zero-blowing question raised here is **settled in §5.2a**: the
patch stays a `patch` on every row with floored `k`/`omega`, rather than becoming a
`wall` mid-sweep, so the sweep remains one family.

**O2 — MOOT UNDER THE O4 RULING. Recommendation, not a decision.**
The item was: gate V compares a blunt-base body (base-drag increment **6–19 % of
`Cd`**, §7.1) against sharp-TE records. **With V `BLOCKED`, no gated `Cd` arm
exists anywhere in this registration, so there is no band to widen and no gate to
split.** The options, with consequences:

| Option | Consequence |
|---|---|
| **(i) Declare O2 disposed of by the O4 ruling. `Cd` is REPORTED on every row with the measured base `Cp` and the derived base-drag increment beside it, gated nowhere, and no row's verdict may cite it.** | The 6–19 % increment becomes a published number on the record instead of a hidden one. Nothing is lost that the O4 ruling had not already removed. **RECOMMENDED.** |
| (ii) Register a new blunt-base `Cd` band anyway | **Inconsistent with the O4 ruling**, which rejected option (b) precisely because inventing a new gate is not the regression Sanaa asked for. A blunt-base `Cd` band would have no comparand either — the same absence, one section later. |
| (iii) Leave O2 open pending a future unblown record | Leaves an open item that cannot close, since finding V's comparand is the same search that already failed. Better carried as **FINDING JF1-V1** (§7.1), which is where it now lives. |

**Recommended: (i).** §7.1 and §7.5 are already written to it; if the supervisor
prefers (ii) or (iii) those sections need amending before the freeze.

**O3 — OPEN. §1.4's two freestream-`omega` prescriptions differ by 22.36× in
`nut_inf`. THE SUPERVISOR'S, NOT THIS LANE'S — options and a recommendation only.**
Branch A (`L = 0.1 c`, `omega_inf = 0.2236 /s`) gives `nut_inf/nu = 67.08`;
branch B (`nut/nu = 3`, `omega_inf = 5.0 /s`) gives 3.00. §5.3 registers **branch
B**. The directive offers both and asks only that the choice be recorded, so this
is **not a directive error** — but it is a boundary condition that reaches the wall
layer the entire low-Re mesh (and §4.3's 46-layer stack) exists to resolve.

| Option | Consequence |
|---|---|
| **(A) Register branch A** | `nut_inf = 67 nu` is comparable to the eddy viscosity through much of the attached BL at `Re_c = 1e6`, and **95.1 %** of `k_inf` survives 25 c of convection, so the inflow condition is still fully present at the airfoil. Expect delayed separation, raised `Cf` (which also raises measured `y+` and pressures §4.3's 5.8 % margin), and a `CL` biased high. The mesh would be resolving a wall layer whose eddy viscosity was set at the far field. |
| **(B) Register branch B** *(what §5.3 registers)* | `nut_inf = 3 nu`, standard external-aerodynamics practice; `k` decays 68 % over 25 c so the airfoil sees `nut/nu ≈ 1`. **Risk, disclosed:** with very low freestream turbulence and **no transition model registered** (§2), `kOmegaSST` can hold a low-`nut` quasi-laminar region near the leading edge, which changes `Cf`, `y+` and the separation prediction — the same region §4.3's `y1` is sized against. |
| **(C) Register branch B AND measure the gap** — add **S2**, one ungated L1 solve at `C_mu_jet = 0.1`, `alpha = 0` with branch A, reported as a `CL_total` and `max(y+)` sensitivity exactly parallel to S1 | Converts a **22.36× unmeasured choice** into a measured, reported number for **11.36 core-min = 3.8 % of the cap** (total 282.00, slack 18.00). The registration then states not only which branch was chosen but what the other one would have given. |

**Recommended: (C).** A 22× boundary-condition choice defended only by argument is
the kind of thing that becomes the first question asked of the result; at 3.8 % of
the cap it can simply be measured. §10 carries S2 as **CONDITIONAL on this ruling**
and §12 costs it both ways. **This lane has not decided it and has not run it.**

**O4 — RULED 2026-08-31, OPTION (c). GATE V IS `BLOCKED`; THE CASE IS GATED ON G
AND THEORY ALONE. The full ruling, its reasoning and its mechanical consequences
are recorded at §7.1 as the supervisor's.**
The original statement of the item is retained below unaltered, because a ruling is
read against the item as it stood.
This is the largest open item and it is a **factual** defect in the directive, not
a physics or arithmetic one. §1.1 asserts the NACA 0012 baseline is *"already
gated on file for unblown CL-alpha and Cd"* and §1.5 builds gate V on *"the
on-file gated CL-alpha slope and Cd within their existing bands"*. A
repository-wide search found **no gated unblown NACA 0012 lift-curve-slope record
at all**, and no surviving gated `Cd` record: the nearest candidate
(`models/curriculum/results/naca0012_wing.json`) is `Cd` at a **single alpha** on
a **3D wing**, its verdict was **overturned as not reproducible**
(`W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md`, `Cd` spread of **21.6 % of the
published value** from mesh-generation noise alone) and its grid-convergence claim separately ruled **`NOT A RESULT`**
(`LADDER_RECIPE_RULING_2026-08-25.md`); the dafoam A1 row is an **adjoint FD
verification artefact** by the lab's own audit (`docs/VALIDATION_INVENTORY.md:364`);
the TMR row **refuses the comparison in its own words**; and F5b, the nearest
`CL(alpha)` attempt, is recorded as **"NO GATE EXISTS"**
(`docs/VALIDATION_INVENTORY.md:306`). §7.1 sets it all out with paths and numbers.
**This lane has NOT invented a comparand to rescue the gate and has NOT quietly
substituted one.** ~~The supervisor rules between options (a), (b) and (c) of §7.1.
**The freeze must not proceed past this item.**~~ — **RULED 2026-08-31: option
(c).** See §7.1. The decisive ground was one the item above had not identified:
the nearest candidate, `cases/tmr/naca0012_status.json`, sits at **`y+ = 9.664`, a
WALL-FUNCTION-regime solution**, while JF1 is `y+ ≤ 1` with no wall functions — **a
different wall treatment is a different mesh family and therefore cannot supply a
same-family regression**, which disposes of option (a) before any of the record's
other weaknesses are reached. The absence is recorded as **FINDING JF1-V1**.

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

**O6 — NEW, 2026-08-31. THE CONTINUITY THRESHOLD IS THE ONE NUMBER IN THIS
DOCUMENT I CANNOT CERTIFY PRE-COMPUTE, AND RULE 2 MEANS IT MUST BE SETTLED BEFORE
THE FREEZE, NOT AFTER STAGE P.**
§5.5b repairs the **class** error — the gated quantity is now `sum local` at the
final iteration, a property of the final field, with `global` and `cumulative`
demoted to REPORTED because a running accumulator's magnitude is set by the
iteration count, which under `residualControl` varies 2 000–20 000 across the
matrix. **That repair is not in doubt.** What is in doubt is the **value**,
`< 1e-8`. Converged steady `simpleFoam` RANS solutions customarily print `sum
local` in the `1e-9`–`1e-11` range — **10× to 1000× of margin** — but that is
general practice, **not a measurement on this case, and no artifact on this box
supports it.** The floor is set by the pressure equation's linear-solver tolerance
and `relTol`, not by the SIMPLE residual.

> **AND THE TRAP THAT MAKES THIS URGENT RATHER THAN TIDY: STAGES F AND P ARE
> COMPUTE.** §6's feasibility and physics stages are ungated, but they are runs.
> Rule 2 closes gates, thresholds, caps and labels at **first compute**, not at
> first *gated* compute. **A threshold cannot be "calibrated at stage P" — by the
> time P has run, no addendum may alter it.** This is exactly how `F23b` became
> unrepairable.

| Option | Consequence |
|---|---|
| **(i) Keep `sum local < 1e-8` gated, as §5.5b registers** | If the predicted 10–1000× margin holds, nothing happens and the check is real. If it does not, healthy rows land `NOT A RESULT` and the registration is unrepairable. **RECOMMENDED**, on the strength of the predicted margin, but recommended *knowingly*. |
| (ii) Relax to `< 1e-6` | Two orders of headroom; still far below any physically meaningful mass-conservation failure. Costs some detection power against a genuinely unconverged pressure field — though the `p` residual criterion at 1e-6 already covers that channel. |
| (iii) Demote `sum local` to REPORTED as well | Removes the risk entirely and removes the check entirely. **Not recommended** — mass conservation is exactly the kind of thing a jet-injection case should be gated on. |
| (iv) Register the threshold as **derived from the registered `p` solver settings** and register those settings | The principled answer, but it needs a derivation this lane cannot complete without either a solve or a source-level analysis of `continuityErrs.H` against this mesh's volume distribution. |

**Recommended: (i), with (ii) as the supervisor's fallback if he judges the
predicted margin too thin to freeze on.** Either way it is a **threshold**, so it
is his to set and it must be set **before** stage F runs.

**O7 — NEW, 2026-08-31. THE RECOSTED PROGRAMME CANNOT AFFORD TO RE-RUN L3.**
With the corrected per-solve figures (§12), the subtotal is **242.11 core-min** and
a reserve covering **one L3 re-run** would take the total to **310.10**, over the
**300** cap by **10.10 core-min (3.4 %)**. §12 registers the reserve as **one L2
re-run (28.53)**, total **270.64**, and registers explicitly that a completion-rule
refusal on the single L3 run (G7) makes gate G **`BLOCKED` on budget** rather than
silently consuming a reserve that is not there.

| Option | Consequence |
|---|---|
| **(i) Accept the L2 reserve and the registered `BLOCKED`-on-budget outcome for an L3 refusal** | Honest and inside Sanaa's cap. The realistic exposure is one refusal on one run out of thirteen; the registered response is an escalation, not a softened verdict. **RECOMMENDED.** |
| (ii) Set the cap to ≥ **315** at freeze time | §12 permits the supervisor to set the cap at freeze. But 300 is **Sanaa's §1.6 number**, and raising it is worth **her** eye rather than a supervisor's (rule 9: a supervisor's message is not her consent). |
| (iii) Drop S1 (11.36) to buy reserve | Trades a registered ungated sensitivity for contingency. Not recommended — S1 measures the `0.07 h` vs `0.14 h` mixing-length choice, which is a real 2× in `nut_jet`. |

**Recommended: (i).** If the supervisor also authorises S2 under O3, the total is
**282.00** and the slack is **18.00 core-min**, still inside the cap.

---

## 17. PRE-COMPUTE AMENDMENT RECORD — 2026-08-31

### 17.1 THE CONDITION, AND HOW IT WAS CHECKED

**Every amendment in this section is made under CLAUDE.md rule 2's pre-compute
amendment clause, which is legal ONLY while no compute has run against this
document, and which requires the condition to be stated together with how it was
checked. Both are given here, and the check was performed at write time, not
recalled.**

> **CONDITION: no compute has been launched against this registration.**
>
> **CHECKED, 2026-08-31T15:23:33Z, at HEAD `c4fadb21`, by naming the artifacts that
> would exist if it were false and observing that they do not:**
>
> | Check | Instrument | Result |
> |---|---|---|
> | The run root **`verification/runs/JF1_jet_flap/`** does not exist | `test -e` on that exact path | **ABSENT.** `verification/runs/` holds 60+ campaign roots; **no `JF1_jet_flap` among them** |
> | No JF1 queue entry exists | `grep -rl 'JF1' verification/queue/` across all six team queues | **0 files** |
> | Nothing named for this rung exists anywhere outside this document | `find . -name '*JF1*'` excluding `.git` | **exactly one path: this file** |
> | No solver has been started | there is no case directory, no `log.simpleFoam`, no `postProcessing/`, no `artefacts/RUN_STATUS.*` for this rung anywhere in the tree | **none** |
>
> **The document is also still UNFROZEN** — §15's freeze block is empty, the header
> carries the unfrozen banner, and no freezing sha exists. **This lane did not
> freeze it and is not entitled to.**

**Nothing in this section alters a gate, threshold, cap or label after compute,
because there has been no compute.** Every amendment strikes its original in place
rather than rewriting it, per this document's own established practice (§7.1's two
earlier corrections) and rule 6's spirit.

### 17.2 THE AMENDMENTS

| # | § | What changed | Class |
|---|---|---|---|
| **A1** | 1.2 | Rule-15 citation repointed from a `git log --diff-filter=A` provenance check to the **sidecar's own title-page header block**. A path-and-commit check is the instrument rule 15 forbids | citation |
| **A2** | 1.6 | The additive decomposition `CL = jet reaction + pressure lift` presented as **a reading** of the source's "magnification" sentence, not as a printed identity | provenance honesty |
| **A3** | 1.6a, 5.1 | **THE FRAME.** "rotated with `alpha`" struck from the `jetSlot` velocity; the single airfoil-frame convention registered and derived; comparator assertion added that `jetSlot` `U` is bytewise identical across the `alpha` sweep | **physics defect** |
| **A4** | 2 | `tau` registered as `pi/6` exactly, not the 7-dp rounding | precision |
| **A5** | 4.2, 4.3 | Normal cell counts 85/116/159 → **97/133/181**; totals 40 660/75 928/142 086 → **46 180/86 638/161 006** | **forced by A7** |
| **A6** | 4.2, 7.2 | **Roache index mapping corrected** — fine = **L3**, not L1. Under the inverted mapping the reported "fine-grid" GCI was computed from the coarse pair: **1.9× overstatement carrying the wrong label** | **gate-arithmetic defect** |
| **A7** | 4.3 | Near-wall sizing **re-derived**. The distribution did not close (four inconsistent numbers); `y1` was sized at the station of MINIMUM `u_tau`, making `max(y+) ≤ 1` **unreachable**. `y1` 2.345869e-05 → **5.0e-06 m**; `g` **solved**, not asserted | **unsatisfiable gate** |
| **A8** | 4.5 | Registered non-orthogonality `< 65` declared **tighter than `MESH_STANDARD.md`'s hard gate of 70**, so a level at 66 reads as a JF1 refusal, not a lab-standard failure | disclosure |
| **A9** | 4.5 | **Aspect ratio** added to the birth certificate with the `MESH_STANDARD` §3.3 alignment justification; the compound AR>1000 + nonOrtho>60/skew>2 promoted from advisory flag to JF1 `BLOCKED` | metric added |
| **A10** | 5.2, 5.2a | `k_jet` and `omega_jet` **floored** by `max(..., k_inf)` / `max(..., omega_inf)`; `C_mu_jet = 0` row registered. Without it `omega_jet = 0` and **every unblown row was `NOT A RESULT` by §7.4's own binding check** | **unsatisfiable check** |
| **A11** | 5.5a | **Blow-up guard re-derived** from each row's predicted peak with a registered margin of 2.0, replacing a multiple of an inlet scale that was marginally violated at `alpha = 8 deg` | **L-409 remedy 2** |
| **A12** | 5.5b, 7.4 | Continuity gate moved from `cumulative and local` to **`sum local` at the final iteration**; `global` and `cumulative` demoted to REPORTED (their magnitude is set by the iteration count, which is not a registered number) | **L-409 class** |
| **A13** | 7.3 | `dCL/dalpha` per-degree `0.1173002851` → **`0.1173002914`** (8th significant figure; the `/rad` comparand was and is correct) | arithmetic |
| **A14** | 8.1 | **COMPLETION CLAUSES 3 AND 5 REWRITTEN.** As first committed the comparator **refused every possible run**. Clause 3 now has three branches — 3a converged early exit (COMPLETE), 3b cap hit (`NOT A RESULT`), 3c any other early stop (refuse) — plus a `controlDict`/`fvSolution` pin; clause 5 counts against `N_stop`, not `endTime` | **L-409, the central repair** |
| **A15** | 8.2 | Mutation limbs 6 → **10**, one per branch of the new clause 3. **M8** exercises the early-stop branch specifically | control coverage |
| **A16** | 11.1 | Error-source 2's heading `8.3 %` → **`1.9125 %`**. 8.3 % is the size of the directive's own term, not the discrepancy; the struck heading overstated the source **4.3×** and mis-ranked it against source 3 | ranking claim |
| **A17** | 10, 12 | G10/G11 struck (O4 ruling); per-solve estimates scaled by the cell-count growth; reserve downgraded L3 → L2; total **293.5 → 270.64** against the unchanged **300** cap | recost |
| **A18** | 7.1, 16 | **O4 RULED** by the cfd-supervisor, option (c) — gate V `BLOCKED`, the absence recorded as **FINDING JF1-V1**. O2 disposed of as a consequence. **O6** and **O7** raised | ruling + new items |

**Amendments A3, A7, A10, A12 and A14 are the five that would have made this
registration produce no result at all.** A14 alone would have refused every run of
every row; A10 would have made every unblown row `NOT A RESULT`; A7 would have made
every row on every level fail `max(y+) ≤ 1`. **Each was found by reading the
document against itself, before compute, and each cost zero core-minutes to
repair.** After the freeze none of them was repairable.

### 17.3 THE SATISFIABILITY CHECK — L-409 REMEDY 5, PERFORMED AND REGISTERED

> **"Name ONE concrete outcome that would PASS every clause simultaneously — actual
> numbers, on the actual mesh, at the actual iteration count. Not 'a converged run':
> a specific one."** — L-409

**IT CAN BE CONSTRUCTED. Here it is: gate G's triple, with row G3 as its L1 member
also serving theory arm (a).** Every number below is checked against the clause it
must satisfy; nothing is asserted without the comparison.

**Mesh — the three levels, from §4.2/§4.3/§4.5:**

| | L1 (Roache 3) | L2 (Roache 2) | L3 (Roache 1) |
|---|---|---|---|
| cells | 46 180 | 86 638 | 161 006 |
| `y1` (m) | 5.000000e-06 | 3.651501e-06 | 2.672653e-06 |
| normal cells / solved `g` | 97 / 1.149626 | 133 / 1.106859 | 181 / 1.077393 |
| `g ≤ 1.15`? | ✔ | ✔ | ✔ |
| layers inside `delta` (≥ 36) | **46** ✔ | **64** ✔ | **87** ✔ |
| cells across `h` (≥ 12) | 12 ✔ | 16 ✔ | 22 ✔ |
| max non-orthogonality (< 65) | 38.2 ✔ | 39.1 ✔ | 40.4 ✔ |
| max skewness (< 4) | 1.61 ✔ | 1.66 ✔ | 1.72 ✔ |
| negative volumes (= 0) | 0 ✔ | 0 ✔ | 0 ✔ |
| max aspect ratio | 2 000 — AR > 1000 **with** nonOrtho 38.2 < 60 and skew 1.61 < 2, so alignment-justified, not blocked ✔ | 2 740 ✔ | 3 740 ✔ |
| `area(jetSlot)` (= 0.005 m² ±1e-9) | 0.005000000 ✔ | 0.005000000 ✔ | 0.005000000 ✔ |

**Run G3 — `C_mu_jet = 0.1`, `alpha = 0`, L1 — clause by clause against §8.1:**

| Clause | Concrete value | Verdict |
|---|---|---|
| 8.1(1) `rc = 0` | `solver_rc=0` in `artefacts/RUN_STATUS.G3.txt` | ✔ |
| 8.1(2) `End` line | present in `log.simpleFoam` | ✔ |
| 8.1(3) pin | `endTime 20000`, `deltaT 1`, `writeInterval 20000`, `residualControl p/U/k/omega = 1e-6` | ✔ |
| **8.1(3a)** | log carries `SIMPLE solution converged in 6742 iterations`, once; `N_stop = 6742`; `2000 ≤ 6742 < 20000`; final initial residuals `p 8.7e-07`, `Ux 4.1e-07`, `Uy 3.3e-07`, `k 6.2e-07`, `omega 5.5e-07`, all `< 1e-6` | **✔ COMPLETE** |
| 8.1(3b) cap | `N_stop = 6742 ≠ 20000` | not triggered ✔ |
| 8.1(3c) other stop | a converged line naming 6742 **is** present | not triggered ✔ |
| 8.1(4) fields at `6742/` | `U p k omega nut` all present | ✔ |
| 8.1(5) `ExecutionTime` count | 6 742 lines `== N_stop` | ✔ |
| 8.1(6) age guard | every field in `6742/` newer than `0/U` | ✔ |

**§5.5 absolute bounds, same run:**

| Bound | Registered | Value | Verdict |
|---|---|---|---|
| `sum local` continuity, final iteration | `< 1e-8` | 3.0e-09 | ✔ |
| `max\|U\|` (§5.5a) | `< 2 × 31.6228 = 63.2456 m/s` | **31.9** (ratio 1.009, not guard-marginal) | ✔ |
| `k ≥ 0`; `min(k)` jet core `> 0` | — | min `k` = 0 at farfield ✔; jet core 1.2e-02 > 0 ✔ | ✔ |
| `omega > 0` everywhere | — | min 5.0 (farfield) | ✔ |
| `nut/nu` finite, `< 1e5` | — | max 412 | ✔ |
| `\|dCL\|` over last 2 000 iters | `< 1e-4` | 4.0e-05 (window exists: 6 742 ≥ 2 000) | ✔ |
| `\|dCd\|` over last 2 000 iters | `< 1e-5` | 6.0e-06 | ✔ |

**§7.4 physicality, same run:**

| Check | Registered | Value | Verdict |
|---|---|---|---|
| jet mass flow | `≤ 0.5 %` | `Σ phi = 0.15808 m³/s` vs `V_j h t_z = 0.15811388 m³/s` → **0.021 %** | ✔ |
| `max(y+)` on `airfoil` | `≤ 1` | **0.94** (predicted 0.9419) | ✔ |
| jet-sheet cells at `x/c = 1` | `≥ 8` | **11** | ✔ |
| frame assertion | `jetSlot` `U` identical across `alpha` | identical | ✔ |

**Gate G — the triple, and it satisfies its own band:**

`CL_total` = **L1 0.604830**, **L2 0.606700**, **L3 0.607700**. With the corrected
Roache mapping (`f_1 = L3`), `r_21 = 1.36322`, `r_32 = 1.36971`:

```
    eps_21 = f_2 - f_1 = 0.606700 - 0.607700 = -0.001000
    eps_32 = f_3 - f_2 = 0.604830 - 0.606700 = -0.001870
    R      = eps_21/eps_32 = 0.53476        ->  0 < R < 1  =>  CONVERGING     [rule 5(3)]
    p      = 1.9546                          ->  inside [1.3, 2.5]            [PASS]
    GCI_fine = 1.25 * |eps_21/f_1| / (r_21^p - 1) = 0.2471 %  ->  < 3 %       [PASS]
```

Monotone, so a GCI may be quoted at all. Every level iteratively converged and
plateaued, so rule 5(1) does not fire; the triple is `CONVERGING`, so rule 5(2)
does not fire. **Gate G: `PASS`.**

**Gate THEORY arm (a) at `C_mu_jet = 0.1`, on L1:**

```
    CL_total   = 0.604830          (G3, above)
    CL_theory  = 0.6047756775      (§7.3, ARC R&M 3304 p.5 eq. 2, source form)
    |diff|/CL_theory = 0.00898 %   <=  15 %                                   [PASS]
```

**Gate V: `BLOCKED` by the O4 ruling — which is a registered outcome, not a
failure to satisfy anything.**

> **CONCLUSION OF THE SATISFIABILITY CHECK: a concrete, fully specified outcome
> exists that satisfies EVERY clause of this registration simultaneously — mesh
> gates on all three levels, all six completion clauses in their early-exit branch,
> all seven absolute bounds, all §7.4 physicality checks, the Roache triple inside
> `p ∈ [1.3, 2.5]` with `GCI_fine = 0.247 % < 3 %`, and the theory band at
> 0.009 % of 15 %. The registration HAS a passing outcome.**
>
> **The values above are a CONSTRUCTED EXEMPLAR, not a prediction and not a
> result.** They are chosen to be individually plausible and mutually consistent,
> which is exactly what the check requires and all it requires. **No row of this
> table may ever be quoted as a JF1 measurement**, and the comparator has never
> seen them. Their only function is to prove that the clause set is not
> self-contradictory — the thing `F23b` could not have shown and was never asked to.

**One clause the check could NOT fully certify, stated plainly rather than
glossed:** the `sum local` continuity bound of `1e-8` (§5.5b). The exemplar's
`3.0e-09` is plausible and consistent with general solver behaviour, but unlike
`max(y+)`, `max|U|`, the layer counts, the `r` ratios and the theory values —
each of which is **derived here from registered quantities** — that one number
rests on practice rather than on this document's own arithmetic. **It is raised as
O6 and must be ruled before the freeze.** An honest gap is worth more than a
confident exemplar.

---

*Drafted by a cfd lane, 2026-08-30; amended by a cfd lane 2026-08-31 under rule 2's
pre-compute amendment clause, condition checked and recorded at §17.1. Every number
above was computed from the registered definitions and cross-checked against a page
image of the printed source; none was copied from the OCR sidecar, which states in
its own header that its equations are corrupted. **STILL UNFROZEN. No compute has
run. This lane did not freeze this document and did not file a queue entry.**
Verdict: **PENDING**.*
