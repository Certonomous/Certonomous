# D19M and D19O are the same operating point with and without a lift constraint

**Proposal, not a verdict.** Nothing here grades anything. Every number is read
from the run's own artefact and the path is given beside it.

---

## 1. THE FINDING: THEY SHARE A BASELINE

`D19O` `CD_baseline_trimmed` = **0.01632675460978398**
  — `/home/ubuntu/certonomous-runs/CURRICULUM-D19O-a1-naca0012-subsonic-optimisation/O-S/d19o_O.json`

`D19M` at α = 4.787°, `CD` start = **0.016327**
  — `docs/dafoam/demo/ACT_D_compressible_multipoint_sheet.tex:414` (Table 2)

**Identical to six significant figures.** Same section, same 4,032-cell grid,
same solver, same freestream. `D19O` is the **lift-constrained twin of D19M's
middle operating point**, and neither sheet currently says so.

## 2. THE TABLE

| | C_D start → final | C_L start → final |
|---|---|---|
| **Lift unconstrained** (D19M, α = 4.787°) | 0.016327 → **0.012052** | 0.50000 → **0.07216** |
| **Lift constrained** (D19O, CL target 0.5) | 0.01632675 → **0.01279162** | 0.4999994 → **0.4999995** |

**The unconstrained run reaches the LOWER drag — 0.012052 against 0.012792 —
and pays for it by discarding about 86 % of the lift.** The constrained run
holds C_L to within 5.4e-7 of its target and takes the smaller, real reduction.

**That is the well-posedness correction beat, computed rather than asserted.**
Previously the act could only *describe* the ill-posedness and point at the
D19M row where lift collapses to −0.15737. This *demonstrates* it: one operating
point, two objectives, the flattering answer sitting beside the honest one.

## 3. WHAT THIS TABLE DELIBERATELY DOES NOT DO

**It never places 21.652 % beside 25.985 %.** Those are answers to different
questions on different problems and putting them in one column would read as
progress, which they are not. The comparison above is **C_D and C_L at one
operating point** — the only comparison of these two runs that is legitimate.

## 4. D19O's OWN NUMBERS, AND ITS CEILING

| Quantity | O-S arm | O-P arm |
|---|---|---|
| C_D baseline → final | 0.01632675460978398 → 0.01279162168845058 | → 0.012792001983085798 |
| C_L final (target 0.5) | 0.49999946447251814 | 0.500002326556085 |
| Drag reduction | 21.65239207561148 % | 21.650062802928048 % |
| IPOPT iterations (cap 40) | 12 | 9 |
| nprocs | 1 | 1 |

**Two independent decompositions agree to 2.3e-5 in the reduction.** That is a
reproduction result and deserves its own row rather than a footnote.

**⚠ THE CEILING TRAVELS WITH THE NUMBER.** `d19o_O.json`
`excluded_from_aggregate_reason` records `shape[7]` as a **REGISTERED
NON-RESULT on the plateau clause, on both rows, whatever value it returns** —
measured one-sided at 21.060684242435336 % on the fine side of s\* = 1e-3, sign
changing between 3e-5 and 1e-5, carrying 0.3351 % of ‖dC_D/dshape‖. Per
`DAFOAM_CHARTER` §3 it is excluded **by name** from any aggregate quoted as
agreement — never dropped silently and never rescued by a step at which it
happens to cross. **D19O has the same shape of ceiling D19M does and it must be
on the face the same way.**

The file also carries its own guard, verbatim: *"`DAFOAM_CHARTER.md` section 9
FORBIDS grading an optimisation by the size of its improvement. This number is
reported; it grades nothing."*

---

# 5. THE TWO CORRECTIONS TO THE POLAR FRAMING

## 5.1 The sampling bound

**The sweep is at 1° increments** — α = 0, 1, 2 … 18 in both arms
(`AOA_POINTS.json`, both curricula). Both regimes report `CONVERGED` at 0–8°
and `NOT CONVERGED` at 9–18°.

**So the claim is: "both regimes break between 8° and 9°, at 1° sampling."**
Never *"the boundary is identical"* and never *"the same boundary to the
degree"* in a sense implying exactness. **A genuine stall-angle difference
smaller than one degree would be invisible to this sweep.** The second form is
the one a viewer will repeat, so the first has to be what reaches the face.

## 5.2 The Reynolds framing: why we test, not what we proved

If the 9° break were physical stall it **should move with Reynolds number** —
and across a tenfold change it did not move by as much as our sampling can see.
That is more consistent with a common **numerical or resolution** limit than
with physics, and it is the best single argument for running A1WR.

**⚠ It is an argument for testing, not a result.** Stall angle is only weakly
Reynolds-dependent in this range, so a real shift could genuinely be sub-degree
and hide inside our 1° sampling. **The honest sentence is "this is why we are
running the wall-resolved study." "This proves it is numerical" is not, and
would be falsified the moment A1WR lands.**

## 5.3 The record already forbids the softer version

`cases/dafoam/ladder-a/A1/feasibility_aoa_polar/AOA_RESULTS.md:84-89`:

> *"the nine points that **did** converge are not thereby trustworthy at the top
> of their range either. This is a 4,032-cell wall-function mesh (y+ 16.7–92.4).
> It cannot resolve a separated boundary layer at any angle. **Convergence and
> correctness are independent here.**"*

So the act may not imply the 0–8° branch is validated either. It is a **sweep
demonstration**, never a polar.

## 5.4 The numbers that carry the refusal on screen

At α = 18°, the incompressible arm reports **C_D = −0.0244555793460258** and
**C_L = −0.3035110439292296**. Two impossible signs in one row: a NACA0012 at
+18° incidence cannot produce negative lift, and no body produces negative drag.

**But the compressible arm at the same angle reports C_D = 0.1186, C_L = 0.3106,
which is not obviously absurd.** That is why the refusal cannot rest on a number
looking wrong — one arm's number does not. The refusal rests on the solver's own
residual verdict, and the negative row is the illustration, not the mechanism.

**There is already a stall-word guard** that exits 2 on any output binding a
stall word to a numeric angle. It **PASSED on both arms**, with controls C7/C7b
proving it fires on a planted claim and stays quiet on the honest caveat. The
platform refusing to say "stall at 9°" is a planted-controlled instrument, not
a narration.

## 5.5 No point is dropped

`AOAI_PREREGISTRATION.md:172` and `AOAC_PREREGISTRATION.md:172`, identically:
**"NEVER dropped from the polar."** All 19 points appear in both arms. Showing
0–8° while omitting 9–18° is barred by the item's own frozen pre-registration.

---

## 6. MEASURED COSTS, ALREADY SPENT

| Run | wall s | ranks | core-min |
|---|---|---|---|
| D19O O-S (optimiser + trim) | 294.123 + 20.633 | 1 | **5.246** |
| D19O O-P (optimiser + trim) | 227.019 + 19.008 | 1 | **4.100** |
| AOAI polar, 19 points | 128.9 | 1 | **2.148** |
| AOAC polar, 19 points | 159.2 | 1 | **2.653** |

*Rank counts for D19O are read from `nprocs` in `d19o_O.json`. The polar rank
count is **inferred** from the cpuset record in `docs/LAB_STATE.md`, because
`AOA_POINTS.json` carries no rank field — inferred, not measured, and flagged
as such.*
