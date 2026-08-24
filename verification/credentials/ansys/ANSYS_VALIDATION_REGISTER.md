# ANSYS VALIDATION REGISTER — every VM2026R1 case the lab has run

**Owner:** `ansys-verification-supervisor`. **Charter:**
`docs/charters/ANSYS_VERIFICATION_CHARTER.md` §6. **Created:** 2026-08-24 by
the harness-build lane, empty. **Append-only** under the private-index
protocol (CLAUDE.md rule 10): a row is never edited after it lands; a
correction or a re-run is a new row citing the old one.

**Reading rule.** Every case run is a row, whatever its verdict. **Only `PASS`
rows are credentials** — the lab's credential count from this suite is the
number of `PASS` rows and nothing else. `GATE FAIL` and `NOT A RESULT` rows
stay here honestly, with their numbers; they are findings, not deletions.
Verdict vocabulary only: `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT`
/ `BLOCKED` / `PENDING`. Dates are UTC from a `date -u` read in the writing
invocation. Dollars are **derived** at the owner-stated $0.0513/core-h, never
measured (the box cannot read its own billing).

Reference result and tolerance are the **frozen** values from the case's
pre-registration, whose sha is the row's `prereg sha`; the comparator sha is the
committed grading script that produced the number.

| # | Case | Date (UTC) | Verdict | Lab value | Reference (source, manual p.) | Tolerance (frozen) | Artifact path | Prereg sha | Comparator sha | Cost, core-min (measured) | $ (derived) | RESULTS path |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **VMFL001** — Flow Between Rotating and Stationary Concentric Cylinders (VM2026R1, pp. 15–16) | 2026-08-24 | **`NOT A RESULT`** | **none — comparator refused (exit 2) + L3 not converged.** The frozen comparator could not find its sampled file (v2606 writes `gateAxis_p_U.xy`, header-less; it was frozen to expect `U_gateAxis.*` with a header) and refused rather than guess a column; independently, L3 fails the registered iterative-convergence clause (final-iteration initial residuals Ux/Uy 1.19876e-06, p 2.89185e-06 vs frozen < 1e-6; plateau ptp 2.77178e-05 m/s vs frozen < 1e-6 m/s) while L1/L2 pass (4.69e-14 / 1.49e-12; ptp 1.00e-14 / 1.27e-11), which under CLAUDE.md rule 5 step 1 makes the rung `NOT A RESULT` before the triple is classified. No planted-zero firing, no triple, no GCI | v_θ at r = 20/25/30/35 mm = **0.0151 / 0.0105 / 0.0072 / 0.0046 m/s** — analytical, F. M. White, *Viscous Fluid Flow* §3-2.3, as printed in the manual's "Target, m/s" column, **manual pp. 15–16**. Context only, never the gate: Fluent 0.0151/0.0105/0.0072/0.0045, CFX 0.0150/0.0105/0.0071/0.0045 | **2 % relative at all four radii, at the finest level (L3, 64 × 256)** — frozen in `PREREGISTRATION.md` §3, justified from the manual's own printed-target rounding (worth 1.148 % at 35 mm) and tighter than the manual's own 3 % goal. Never reached | `verification/runs/ansys_verification/VMFL001/` (committed `ae30f914`) | **`d6ea5de9286ad5c8699b6e709e105c2cd484e8c1`** (as amended and as it ran; original freeze **`e0afc25936277798d3054137734fd9775311fbbb`**, commit `ffeed580`) | **`8cb29610e5d6f6fa4291df503a98bc99d0ff660f`** | **1.9833** (119 wall s, serial; cap 10, never approached) | **$0.0017** (derived at $0.0513/core-h, not measured) | `cases/ansys_verification/VMFL001/RESULTS.md` |

*Credential count: 0 PASS of 1 run.*
