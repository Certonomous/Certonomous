# K0d — RULING: NOT FIT TO FIRE. Stop amending; re-register.

**Date:** 2026-08-25. **Author:** heat-transfer supervisor.
**Verdict: `BLOCKED`.** Zero core-minutes spent against a registered POINT of
829.36. K0d remains **FROZEN, ARMED, UNFIRED**; `K0d_runs/` does not exist.

**Sanaa's directive today:** *"Fire everything armed, today... Nothing armed
stays unfired overnight without a named blocker."* **This document is the named
blocker.** Her rigor clause, which she flagged herself: *"We are raising the
denominator — core-hours — not lowering the bar."* **The team is not idle** —
three thermal solvers are running under a separate pre-registration.

---

## 1. THE BLOCKER — the case's DEFINING PARAMETER is over-determined, and TWO OF ITS OWN AMENDMENTS RECONCILE IT DIFFERENTLY

**Re-derived personally, not accepted from a lane.** Three quantities are
registered independently and **cannot all hold**:

| `ν` | `β` | implied `Ra` | vs registered `Ra = 2.13e9` |
|---|---|---|---|
| 1.55e-5 (§3.2 l.189) | 1/298 = 3.356e-3 (§5 l.312) | **2.18866e9** | **+2.76 %** |
| 1.569e-5 (**§A1.2**) | 3.356e-3 (§5 l.312) | **2.13597e9** | +0.28 % |
| 1.55e-5 (§3.2 l.189) | **3.26577e-3 (§A5.7)** | **2.13000e9** | exact |
| 1.569e-5 | 3.26577e-3 | 2.07873e9 | −2.41 % |

**`AMENDMENT 1` §A1.2 reconciled this by moving `ν` to 1.569e-5. `AMENDMENT 5`
§A5.7 reconciled the SAME contradiction by moving `β` to 3.26577e-3.** Both are
frozen, both are in the document, **and they disagree.** A pre-registration whose
own amendments settle its defining dimensionless parameter two different ways
does not determine what physics is being simulated. **That is not a gap another
amendment fills; it is a contradiction, and I will not fire compute into it.**

## 2. FIVE AMENDMENTS HAVE NOT REACHED A FIXED POINT — the pattern IS the finding

| amendment | found |
|---|---|
| 1 | three pre-compute items ruled |
| 2 | pre-flight smoke test registered |
| **3** | **clause 4 unsatisfiable for three of nine cases — whole rung ungradeable** |
| **4** | **inlet `omega` unregistered on five of nine; G7 defined on unregistered stations** |
| **5** | **no `fvSchemes`, no `fvSolution`, no turbulence BC types registered; `phi` in no field set** |

**AMENDMENT 5's deliberate sweep found EIGHT more unregistered inputs.** Two can
move a graded value: **the initial `internalField` of every field is
unregistered** — a steady buoyant cavity need not be seed-independent, and K0cS
carries a seed case built for exactly that question — and **the profile sampling
method is unregistered** (`setFormat`, `interpolationScheme`, sample-set type),
which touches G1–G4, G5b and G8 directly. `ν` is separately registered as **two
numbers**.

**I stated a stopping rule before this sweep ran: if it found one more, the
recommendation would be re-registration rather than a fifth patch. It found
eight, plus a second internal contradiction. The rule fires.**

## 3. RULING

1. **K0d DOES NOT FIRE.** Not tonight, not on a sixth amendment.
2. **AMENDMENT 5 STANDS AS COMMITTED.** Its content is right, its arithmetic
   checks, and it is honest about what it did. It is not withdrawn.
3. **RECOMMENDED, AND ESCALATED RATHER THAN TAKEN:** K0d is **re-registered on
   Sanaa's 10-line template** — case, reference, quantities, bands, ladder,
   decomposition seed, criteria — **with the physics chosen ONCE and
   consistently**, superseding this document rather than patching it.
   **Retiring a frozen pre-registration is not a call this team takes alone.**
4. **The pre-flight smoke test's PASS stands** and is unaffected: it proved the
   dictionaries take a timestep. **It proves nothing about this document's
   internal consistency, and it never could** — that is a *document* property
   found by reading, not a *case* property found by running.

## 4. MY OWN ERROR, RECORDED — I RULED ON A FALSE PREMISE

**I ruled that `beta` and `TRef` were "registered nowhere".** They are — **§5
line 312**: *"Boussinesq, `T_ref = 298 K`, `β = 1/298 = 3.356e-3 K⁻¹`."*
**A lane's report said they were absent and I did not check the claim before
ruling on it.** AMENDMENT 5 therefore **SUPERSEDED a registered input** while
believing it was filling a gap. **The implementing lane caught it, disclosed it
in the instrument, and did not quietly proceed — that is the correct behaviour
and the error was mine.**

**This is the second time today I have ruled from a lane's summary instead of the
artifact** (the first: my `AMENDMENT 3` brief would have required `k` of a
laminar case). **Both were caught by lanes reading the instrument rather than the
brief. The lesson is not about lanes: a supervisor's ruling inherits the
evidential status of what it was formed from, and a summary is not a check.**

## 5. LAB-WIDE HAZARD — REPORTED, NOT FIXED, AND URGENT

**The shared git index stages this file at 986 lines against HEAD's 3 759.**
**A bare `git commit` by ANY agent in this repository would delete 2 773 lines
and ALL FIVE AMENDMENTS** — the staged blob contains **zero**. Measured, not
inferred: staged blob `02382413`, HEAD blob `e629f5c4`.

**Standing rule 10's "never a bare `git commit`" is not a style preference here;
it is the only thing standing between this rung and its own erasure.**
**Inspected, never reverted — the index is the chief's call.** Every commit this
team made today used the private-index protocol and never touched it.

## 6. WHAT IS NOT CLAIMED

That the eight further unregistered inputs are all consequential — six are inert
or minor and are named as such in `AMENDMENT 5` §A5.13. That the re-registration
would be quick to grade: it would not change that **G6 stays `PENDING` on Blay
1992, which is NOT OBTAINED.** That this document is worthless — **its physics
reasoning, its instrument audit and its cost registration are sound and are
reusable.** What it cannot currently do is determine its own run.
