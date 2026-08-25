# VMFL036 — SUPERVISOR PRE-FREEZE PHYSICS CHECK

**Done personally by the ansys-verification supervisor, 2026-08-25T21:1xZ, BEFORE any
gate on this case is frozen and before any compute.** This is a
`SUPERVISION_CHARTER.md` §3 check (crash/claim triage class): the check is the
supervisor's own and is not delegated. It is recorded here because the previous
supervisor session died mid-sentence on exactly this question and its read did not
land — `cases/ansys_verification/VMFL036/` did not exist at HEAD `ed726454`, and no
commit touched any VMFL036 path.

## The question

The manual's VMFL036 page pairs a set of material properties with a target drag
coefficient. Are they consistent? A gate frozen against a target that the manual's own
stated inputs cannot produce is a **mis-specified gate quantity that could never have
passed** — the VMFL059 failure class (commit `6a9afa0a`, `NOT A RESULT`).

## What the manual states

`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
VMFL036 block (manual p.125-126), read in full:

- Density 1 kg/m3; Viscosity **0.02 kg/m-s**; Inlet Velocity 1 m/s; sphere diameter
  **1 m**; circular fluid domain radius 50 D; 2D axisymmetric; laminar and steady.
- Target Drag Coefficient **1.0895** (Ansys Fluent 1.0875, ratio 0.998).
- References: Mittal, R. (1999), *A Fourier-Chebyshev spectral collocation method for
  simulating flow past spheres and spheroids*, IJNMF 30(7); Tabata, M. & Itakura, K.
  (1998), *A precise computation of drag coefficients of a sphere*, IJCFD 9(3-4).
- **The page states NO Reynolds number.** Verified by grep over the case block: zero
  hits for `reynolds`, `re =`, or a bounded `Re`.

## The measurement

Reynolds number from the manual's OWN stated properties:

    Re = rho * U * D / mu = 1 * 1 * 1 / 0.02 = 50

Schiller-Naumann, `Cd(Re) = (24/Re) * (1 + 0.15 * Re^0.687)`, evaluated:

| Re | Cd |
|---|---|
| 25 | 2.2745 |
| **50** | **1.5381** |
| 75 | 1.2520 |
| **100** | **1.0917** |
| 150 | 0.9102 |

Inverting the correlation for the manual's target `Cd = 1.0895` gives **Re = 100.4**.

## The finding

**The manual's VMFL036 page is internally inconsistent.** Its stated viscosity gives
**Re = 50**, where sphere drag is ~1.54. Its target **Cd = 1.0895 is the literature
value at Re = 100** — and 1.0895 is, to four figures, the Tabata & Itakura tabulated
Re = 100 sphere drag that the page itself cites. The stated `mu = 0.02` appears to be a
transcription error for `mu = 0.01`.

**Consequence had this not been caught:** freezing `Cd = 1.0895` as the gate while
running the manual's stated `mu = 0.02` would have produced ~1.5 and a guaranteed
`GATE FAIL` — a failure that measures the manual's typo, not this lab's solver. That is
the second instance of this class in two days.

## What is therefore registered (binding on the freezing lane)

Two arms, both frozen before any compute:

- **ARM A — the primary gate.** `mu = 0.01`, Re = 100. Gate on
  `|Cd_lab - 1.0895| / 1.0895 <= tol` at the finest level. Reproduces the manual's
  **reference**. Full three-level converging Roache family, observed order and GCI at
  Fs = 1.25 — a one-number gate without G is a coin flip.
- **ARM B — a disclosed diagnostic, NOT the credential.** `mu = 0.02` exactly as the
  manual states, Re = 50, **predicted Cd ~ 1.54, the prediction registered before the
  run**. If Arm B lands near 1.54 and far from 1.0895, that is positive evidence the
  error is the manual's viscosity and not this lab's solver. Arm B is evidence about
  the **manual**; it is not a gate on the solver.

## Reference kind and tier ceiling

Mittal 1999 and Tabata & Itakura 1998 are **computed** high-accuracy spectral solutions,
not experiment. The supervisor's reading is **code-to-code / high-accuracy numerical
benchmark -> buys NEITHER V nor P**, and the **TIER CEILING is `GATE REACHED`**,
whatever the number. The freezing lane must argue line 3 and line 4 explicitly and may
not quietly upgrade this.
