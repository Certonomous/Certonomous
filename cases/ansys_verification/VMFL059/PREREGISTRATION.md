# VMFL059 — Conduction in a Composite Solid Block: PRE-REGISTRATION (template form)

**NOT FILED ANYWHERE.** Nothing here or in the case it registers is sent, emailed,
uploaded, filed, posted or commented outside this box (CLAUDE.md rules 7, 8;
`ANSYS_VERIFICATION_CHARTER.md` §8). The manual is proprietary Ansys documentation.
**SUBMISSIONS PARKED.**

**NOT YET RUN — frozen before any solver starts** (CLAUDE.md rule 2). At writing,
**`verification/runs/ansys_verification/VMFL059/` did not exist** — checked with
`ls -d` at **2026-08-25T17:08:06Z**, which returned *No such file or directory*.
**Graded compute is LOCKED**; launch authorisation comes from the
`ansys-verification-supervisor` after its four personal checks, and **no agent
message is Sanaa's consent** (rule 9). Drafted by `ansys-lane-opus48` on the
`docs/ansys_verification/PREREG_TEMPLATE.md` standard form. Departures land as
dated addenda at the foot, never by editing above (rule 6).

**Reference kind = closed-form/exact → this case can buy V. Tier ceiling = PASS.**

---

## The standard form (frozen)

```
1. CASE       : VMFL059 — Conduction in a Composite Solid Block — manual p.185.
                Solver = OpenFOAM v2606 laplacianFoam (steady limit). This box has
                no Fluent/CFX; the archive was read for setup only. NOT YET RUN;
                run dir absent at 2026-08-25T17:08:06Z.
2. REFERENCE  : cooled (right) wall = 378 K ; adiabatic (left) wall = 413 K.
                Source = F.P. Incropera & D.P. DeWitt, Fundamentals of Heat and Mass
                Transfer, 5th ed., p.117 (closed-form 1-D composite wall with
                generation). Ansys Fluent = 378.14 / 413.17 K (ratio 1.0004) —
                CONTEXT ONLY, never the gate.
3. REF KIND   : closed-form/exact → buys V. The comparator derives 378 and 413
                two ways from first principles (--selftest) and they coincide with
                the manual's printed targets to full printed precision.
4. CEILING    : PASS (a validation credential if the band is met on both walls).
5. QUANTITIES : areaAverage(T) on patch rightWall (cooled) and leftWall (adiabatic),
                in K, read post-solve via postProcess patchAverage.
6. THE GATE   : |T_lab − T_exact| / |T_exact| ≤ 0.01 (1%), on BOTH walls, at L3.
                Inside on both ⇒ PASS; outside on either ⇒ GATE FAIL.
7. LADDER     : laplacianFoam; DT is read as a FIELD (verified in createFields.H:
                READ_IF_PRESENT), set to k=75 (material 1) / k=150 (material 2) by
                setFields on cell zones — NO multi-region setup. Volumetric
                generation q''' = 1 500 000 W/m3 via scalarSemiImplicitSource
                (volumeMode specific) in the material-1 cell zone only. Right-wall
                convection h=1000 W/m2K, T∞=303 K imposed by a codedMixed Robin BC
                (valueFraction = h/(h + k·deltaCoeffs), mesh-independent). Three
                birth-certified meshes (cases/ansys_verification/VMFL059/mesh_birth/).
8. SEED       : r=2 grid triple, refined in x AND y. L1/L2/L3 = 280 / 1120 / 4480
                cells. Interface at x=0.05 is a BLOCK FACE at every level. Serial.
9. RISK       : conductivity SMEARING at the material interface. If x=0.05 were not
                a cell face the interpolated DT would blur k across the jump and bias
                BOTH wall temperatures; the two-block mesh pins the interface on a
                face at every refinement, removing it. This is the predicted-before-
                compute failure mode.
10. ORDER     : formal p_f = 2 (Gauss linear laplacian, corrected snGrad). Expected
                observed p_obs ≈ 2; **p_obs > 2.3 is SUSPICIOUS** (this is a
                piecewise-quadratic/linear field an FV scheme can represent nearly
                exactly, so an inflated order would signal a reference coincidence,
                not real 3rd-order accuracy).
11. WEDGE     : N/A — Cartesian planar geometry, not axisymmetric. No sin(t)/t term.
12. COST      : ≈ 3 core-minutes total for the triple (three 2-D solves, 280–4480
                cells, ~500 steps each; smoke L1 = 11 wall-s single core = 0.18
                core-min). Basis = reported-by-owner (box cannot read its billing,
                COMPUTE_BUDGET §5). CAP = 15 core-minutes; overrun STOPS the run.
13. CONTROLS  : comparator grade_vmfl059.py, --selftest GREEN (reference two ways,
                plant K=1.234 read back, classifier). Planted-zero control fires on
                BOTH wall readers (rule 3). Strict completion: rc, End line, latest
                == endTime, age guard on 0/T (rule 4). Roache triple gating: non-
                CONVERGING ⇒ NOT A RESULT; GCI at Fs=1.25 printed (rule 5).
```

## Provenance of the driving input (NOT derived from the target)

The volumetric generation **q''' = 1 500 000 W/m³** was read **directly from the
Ansys archive case** — `cond-slab.cas.h5`, string
`(source-terms (energy ((constant . 1500000) (inactive . #f) (profile "" "")))`,
corroborated in the archive's own `report.xml` Source Terms — **not** back-solved
from the 378/413 K answers (CLAUDE.md: never derive an input from the target). The
manual's p.185 text layer drops the numeric generation rate; the archive supplies
it. All other inputs (k, thicknesses, h, T∞, geometry) are stated on manual p.185.
Independent closed-form check with these inputs reproduces 378 K and 413 K exactly.

## Reference computation (the exact solution, in the comparator)

q''·= q'''·L1 = 1.5e6 × 0.05 = 75 000 W/m². Cooled wall = T∞ + q''/h = 303 + 75 = 378 K.
Interface = 378 + q''·L2/k2 = 378 + 75000×0.02/150 = 388 K. Adiabatic wall = 388 +
q'''·L1²/(2k1) = 388 + 25 = 413 K. Slab-2 thickness = 0.07 − 0.05 = 0.02 m.

**Amendments before first compute** must name the run directory that does not exist
and state the condition checked. After first compute: dated addenda only, and no
addendum may alter the gate, band, cap or label.

---

## AMENDMENT 1 — 2026-08-25 — tier ceiling and the "validation credential" sentence corrected (category error)

**Legality (CLAUDE.md rule 2, before-first-compute clause).** This amendment lands
**before any solver has touched VMFL059**: `verification/runs/ansys_verification/VMFL059/`
**does not exist** — checked with `ls -d` in the committing invocation, which returned
*No such file or directory*. Had that directory existed, the amendment would be illegal
and the defect would instead be disclosed as a post-compute addendum altering nothing.

**What was wrong.** Two sentences conflated the VERDICT vocabulary with the TIER
vocabulary and rested a credential claim on a false sentence:

- **Struck, line 17:** "Reference kind = closed-form/exact → this case can buy V.
  **Tier ceiling = PASS.**"
- **Struck, line 36:** "4. CEILING : **PASS (a validation credential** if the band is
  met on both walls)."

`PASS` is a **verdict** word (`PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED
/ PENDING`, grading the gate), not a **tier**. The tier vocabulary is `HOLDS / GATE
REACHED / SURVEYED / NOT HELD`, grading what the case establishes for the lab; the two
overlap only at `GATE REACHED`. A "tier ceiling of PASS" is a category error. And "a
validation credential" is false: line 33 of this same document already states the
reference is **closed-form/exact → buys V**. V is **code verification**. **P —
validation — requires a measured or experimental reference; a closed-form solution is
not one** (Sanaa's ruling 2026-08-25 limb (a): an exact/analytic reference scores V and
NEVER P). This is the VMFL007 precedent exactly.

**Correction (replaces the struck text).** Tier ceiling = **`GATE REACHED`** — the
P/validation column is unavailable on a closed-form reference, so the highest tier this
case can earn is `GATE REACHED`. It is **code verification (V)**, **not** a validation
credential. `GATE REACHED` is this team's **success condition, not a shortfall** (Sanaa
2026-08-25: *"it's fine that itll reach gate reach at best. Anything gate reached for for
that team means we reached ansys, which is good enough."*).

**What did NOT change — asserted explicitly.** No gate, no threshold, no band (1 % on
both walls, at L3), no reference value (378 K cooled / 413 K adiabatic), no Ansys context
value, no cap (15 core-minutes), no ladder, no seed, no control, and no verdict label
moved. Only the **tier ceiling** and the **false "validation credential" sentence** are
corrected. The grading path is untouched: `grade_vmfl059.py` was inspected and carries no
tier/credential wording (its only `PASS` strings are the gate verdict and selftest
labels), so it is **not** edited and the supervisor's check 4 is **not** re-opened.

**Provenance.** `docs/charters/ANSYS_VERIFICATION_CHARTER.md` §6; VMFL007
PREREGISTRATION.md (closed-form → ceiling `GATE REACHED`); `PREREG_TEMPLATE.md`
AMENDMENT 1 of the same date. lines whose number changed above this section: 0.
