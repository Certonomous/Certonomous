# The polar act: stage the refused field, not the negative number

**Proposal and a correction.** Nothing here grades anything. Every number is read
from the run's own artefact and the path is given beside it.

---

## 1. THE CHANGE

**Stage the rendered velocity field at α = 18° — the angle the platform refused —
where the negative drag coefficient was going to go.**

The frame is `verification/runs/actD_paraview/frames/polar_field_alpha18_not_converged.png`,
rendered from the case's own saved state and graded `PASS` on `G-PV4`, `G-PV7a`
and both binary-identity gates (`verification/runs/actD_paraview/frames/render.json`).

## 2. WHY IT BEATS THE NUMBER, AND THE CORRECTION IT CARRIES

The negative drag coefficient at α = 18° — **C_D = −0.0244555793460258**, with
**C_L = −0.3035110439292296** beside it — was proposed as the on-screen
justification for the refusal, on the grounds that it *"does the whole job."*

**It does not, and the reason is measurable.** The claim rests on a viewer
already knowing that drag cannot be negative. And **the compressible arm at the
same angle reports C_D = 0.1186, C_L = 0.3106** — nothing a viewer would find
absurd. So on one of the two arms the number argues for nothing at all.

**A visibly disordered wake is legible to anyone, in either arm.** That is the
whole of the case for the change.

## 3. ⚠ THE LIMIT, WHICH IS THE BINDING PART OF THIS MEMO

**The caption may not diagnose.** Oscillatory striping in a non-converged steady
RANS field can be numerical oscillation, an unconverged transient, **or** a real
unsteady structure the steady formulation cannot hold. **We do not know which. We
have not measured it. The act may not say.**

**The frame is a CORRELATE of a refused state, never a MECHANISM for it.** The
refusal rests on the solver's own residual verdict and on nothing in the picture.

**Sanaa's caption rule and this constraint point the same way, which is why the
published caption is now numbers only:**

    alpha = 18 deg  |  iter 1000/1000  |  tol 1e-8 not met  |  9/19 converged

**A number cannot assert a mechanism.** Forbidden: *"you can see the flow
separating"*, *"the wake is shedding"*, and every relative of them.

**What is deliberately NOT quoted:** a residual value. `AOA_POINTS.json` records
`achieved_min_residual: None` for α = 18° — DAFoam printed no satisfaction line,
so there is no measured residual to give. `1e-8` is the **registered tolerance**
and the caption says it was not met; that is a verdict, not a measurement, and
the caption does not dress it as one.

## 4. ⚠⚠ THE HOLE THIS OPENS, MEASURED — AND HOW THE CAPTION RULE CHANGED IT

`aoa_read.G-STALL` stops us binding a stall word to a numeric angle. It is
fail-closed, carries two-sided controls (C7/C7b) and **passed on both arms**. But
**it reads STRINGS**, and needs the stall word and the angle within sixty
characters **of one string**.

### Under the original prose captions, it could not see them

| string | `G-STALL` |
|---|---|
| `the stall angle is 13.0 deg` (control C7) | **FIRES** |
| `The flow separates over the upper surface here.` | **does not fire** |
| `The wake is shedding behind the section.` | **does not fire** |

**The ANGLE was in the frame label and the CLAIM was in the caption. Two
channels — the regex could never see them together, however it were tuned.**

### Sanaa's caption rule moved the angle into the caption, and partly closed it

Her caption directive (newest of her directives **by git commit order**; the
filename timestamps invert across the `2006Z` naming boundary and are not the
authority) requires captions of numbers, symbols and units. That puts the angle
**in the caption**, so a stall word now sits beside it in one string:

| numeric caption | `G-STALL` |
|---|---|
| `alpha = 18 deg \| stall \| 9/19` | **FIRES** |
| `18 deg \| separation onset \| 10/19` | **FIRES** |
| `alpha = 18 deg \| wake shedding \| 9/19` | **does not fire** |
| `18 deg \| flow separates \| 10/19` | **does not fire** |

**⚠ THE COVERAGE IS RESTORED ONLY FOR THE VOCABULARY `G-STALL` ALREADY HAS.**
`shedding`, `separates`, `recirculation` and `turbulent` are not in its word list
at all, so a mechanism claim using them is invisible to it **in either format,
with or without an angle.**

That correction came from an arm going red on an overclaim in this memo's own
supporting file: `wake shedding` was first filed as a string the new format
would catch, and it is not.

**So the mechanism guard stays PRIMARY and is not weakened on the strength of
`G-STALL` now seeing more.** It requires no angle and carries the vocabulary
`G-STALL` lacks.

### The guard

`cases/dafoam/ladder-a/A1/polar_frame_captions.py` — **35/35 arms, both
directions**: eight angle-less captions must be rejected and must evade
`G-STALL`; two numeric captions in its own vocabulary must be rejected and must
be caught by it; three numeric captions outside its vocabulary must be rejected
and must still evade it; four honest numeric captions must be accepted; every
published caption is swept, and each also goes through
`demo_mode.check_demo_language`.

### ⚠ The limit of the rot-arms, written down because it was discovered

The arms assert this memo's claim against **`G-STALL`'s behaviour**, so they fire
when the **instrument** changes. **They did not fire when the caption FORMAT
changed** — and that is what actually moved the claim. The guard never moved; the
**subject** moved.

**A rot-arm catches the instrument changing under a document. It does not catch
the world changing under it.** The mitigation is that the claim is now stated
**conditionally** — *"of captions carrying no angle"* — so a format change
narrows its scope instead of falsifying it.

**One defect the guard caught in itself on its first run:** the mechanism pattern
carried `turbulent wake` and *"The wake is turbulent here."* walked through it.
Found by the plant, not by reading. **A phrase pattern is only as good as the
word order its author imagined.**

## 5. WHAT THE ACT MAY NOT DO

- **No point is dropped.** All 19 angles appear in both arms
  (`AOAI_PREREGISTRATION.md:172`, `AOAC_PREREGISTRATION.md:172`: *"NEVER dropped
  from the polar"*). Showing 0–8° and omitting 9–18° is barred by the item's own
  frozen pre-registration.
- **The converged branch is not validated either.**
  `feasibility_aoa_polar/AOA_RESULTS.md:84-89`: *"the nine points that did
  converge are not thereby trustworthy at the top of their range either …
  Convergence and correctness are independent here."* It is a **sweep
  demonstration**, never a polar.
- **The boundary claim is bounded by the sampling.** The sweep is at 1°
  increments, so the statement is *"both regimes break between 8° and 9°, at 1°
  sampling"* — never *"the boundary is identical"*.
- **The Reynolds non-movement is why we test, not what we proved.** Stall angle
  is only weakly Reynolds-dependent in this range, so a real shift could be
  sub-degree and hide inside the sampling.
- **No converged-angle field exists to compare against.** The sweep re-solves in
  place, so only the final angle's fields survive; the converged branch's were
  overwritten. A neighbouring angle relabelled would be fabricated provenance.
  Recorded in `render.json` under `_not_rendered`.

## 6. THE FRAME'S OWN PROVENANCE

| | |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible` |
| case / time | `case/1000` — and `case/1000/uniform/time` reads `1000` |
| angle, verdict | α = 18.0°, `NOT CONVERGED`, `last_time 1000` (`AOA_POINTS.json`, last point) |
| field | `U`, velocity magnitude |
| mesh | 4,032 cells, asserted against the case's own `checkMesh.log` |
