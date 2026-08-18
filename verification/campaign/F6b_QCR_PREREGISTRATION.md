# F6b periodic hills, QCR2000 arm — pre-registration

Written 2026-08-08, before any solve. Item: `f6b-qcr2000-on-the-hills`
(approved 2026-08-07, 12 core-min, from the negative-verdict review entry 1).
The executed hump QCR null (outcome two at a 0.010 x/c bar,
`W1_HUMP_CHALLENGE_RESULTS.md`) makes this the deciding leg: on the ducts
the untrained QCR2000 term was decisive (AR_1 0.0811→0.0455), on the hump it
was null. The hills' APG separation decides whether the separation of
"anisotropy missing" from "shear stress mis-scaled" generalises across the
2D separated-flow class.

## 1. Case, instrument, single change

- Base: the **verified F6b medium rung** — the lab's own 15,600-cell
  periodic-hill mesh whose reattachment agrees with the shipped-grid value
  to 0.043% and whose grid sensitivity measured 0.097% (Gate V of the F6b
  record, decided on this rung). Same `0/`, same `fvSchemes`/`fvSolution`
  (`residualControl` p/U/k/omega 1e-6), same forcing and physical setup,
  same 4 ranks, cold start — identical to the verdict run in every respect
  except:
- **Single change:** `RASModel kOmegaSSTQCR`
  (`libkOmegaSSTQCRTurbulenceModels.so`, the identical lab-built QCR2000
  library and model of the duct round-5 result and the hump arm).
- Cap: `endTime 12000` — declared now, sized for the criterion per
  guidelines 3.4: the SST verdict rung converged at 5,997 of a 6,000 cap
  (2 iterations of headroom is not a sized cap), and the QCR term's
  nonlinearity has converged slower on some duct cells. A run that hits
  12,000 without `residualControl` is reported unconverged; the registered
  gate is then decided only if the reattachment quantity itself is settled
  under S12 as written (S12 flags travelling iff drift ≥ 1e-3 AND monotone
  fraction ≥ 0.90; window: the last 2,000 iterations of the crossing
  position, both numbers printed with the record and the carrying clause
  named) — otherwise NO VERDICT, per L-24 and the F8 precedent.
- Extraction: the F6b record's own `gate.py` crossing machinery on
  `wallShearStress` at the final time (patch `bottomWall`), unmodified
  conventions.

Comparator (SST, this same mesh, the verdict rung): separation-side
crossings per the F6b record; **reattachment x/h = 7.6472** vs the
literature band 4.21–4.7, midpoint 4.455 (+72%).

## 2. Gate — containment/materiality against the +72% FAIL

Materiality bar, declared now: **0.10 x/h** on reattachment (about 3% of
the 3.19 x/h error; the F6b grid-sensitivity spread on this quantity was
0.0074 x/h, so the bar is an order of magnitude above instrument noise).

- **Outcome R (repaired):** reattachment enters the literature band
  4.21–4.7. The constitutive route resurrects the hills the way it did the
  ducts; the hump null then marks the hump as the odd leg out.
- **Outcome P (partial):** moves ≥ 0.10 x/h **toward** 4.455 without
  entering the band. Anisotropy matters on APG separation but is not the
  whole deficit; magnitude reported.
- **Outcome N (null):** |Δ| < 0.10 x/h, or movement away. The two-leg
  pattern closes consistent: QCR2000 repairs secondary-flow anisotropy and
  does not touch separated-shear-layer bubble length on either leg; the
  omega budget inherits the class-level question.

## 3. Predictions (numeric, kept as written)

1. The run converges on `residualControl` within 12,000 iterations.
2. **Outcome N**: |reatt(QCR) − 7.6472| < 0.10 x/h — the hump null
   generalises, because the hills' failure is the same shear-stress
   magnitude deficit and QCR2000's quadratic terms redistribute stresses
   without changing the limiter-governed magnitude. (If falsified toward P
   or R, that is the bigger finding: the legs differ, and APG/curvature
   anisotropy is implicated — the clause stays as written either way.)
3. Cost: ≤ 15 core-min gross (the item's 12 sized on the SST rung's 6.79
   at 5,997 iterations, plus the declared 12,000 cap's margin; wall × 4
   ranks, inside the session's remaining headroom).

## 4. Bookkeeping

Run dir `demo-output/website/campaign/F6b_runs/medium_qcr2000` (the family's
rung convention), registry entry per solve, results appended as a dated
section to the F6b results line plus the cross-leg table in the W1 hump
record updated from "pending" to the measured row, docket outcome on
`f6b-qcr2000-on-the-hills`.

---
*Nothing below this line existed when the run was launched.*

**Dated citation note, 2026-08-08 (Ladder V rung V5; additive only):** the
QCR2000 term named throughout is Spalart, P. R., "Strategies for turbulence
modelling and simulations," *Int. J. Heat Fluid Flow* **21**(3), 252–263
(2000); `Ccr1 = 0.3` is that paper's published constant, untouched.
