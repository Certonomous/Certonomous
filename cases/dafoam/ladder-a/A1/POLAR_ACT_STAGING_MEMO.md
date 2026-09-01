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
The honest sentence is *"this is what the solver's last iterate looks like at a
point the platform refused"*. Forbidden: *"you can see the flow separating"*,
*"the wake is shedding"*, and every relative of them.

## 4. ⚠⚠ AND THE HOLE THIS OPENS, MEASURED

`aoa_read.G-STALL` is the guard that stops us binding a stall word to a numeric
angle. It is fail-closed, it carries two-sided controls (C7/C7b) and it **passed
on both arms**. But **it reads STRINGS**, and it requires the stall word and the
angle to sit in one string within sixty characters of each other:

| string | `G-STALL` |
|---|---|
| `the stall angle is 13.0 deg` (control C7) | **FIRES** |
| `At 18 deg the flow stalls over the upper surface.` | **FIRES** |
| `The flow separates over the upper surface here.` | **does not fire** |
| `The wake is shedding behind the section.` | **does not fire** |

**On a rendered frame the ANGLE is in the frame label and the CLAIM is in the
caption. Two channels. The regex cannot see them together.** So a caption may
assert a mechanism the run never measured and every existing instrument in this
lab stays green.

*No gate reads prose* was already this family's known hazard. **No gate reads
pictures either — and this is the first time we have put a picture where an
argument used to be.**

### The guard that closes it

`cases/dafoam/ladder-a/A1/polar_frame_captions.py`. It holds the approved
captions, a **mechanism** pattern deliberately carrying words `G-STALL` does not
have at all (`separates`, `shedding`, `recirculation`, `reattach`, `turbulent`)
and requiring **no angle anywhere**, and a **result-voice** pattern for captions
that present a refused iterate as a flow result.

**22/22 arms, both directions**: eight forbidden captions must be rejected, four
honest ones must be accepted, every published caption is swept, and each also
goes through the act's own camera-string checker `demo_mode.check_demo_language`.

Two arms exist only to stop this memo rotting: one asserts that **8/8 of the
forbidden captions still evade `G-STALL`**, so if a successor widens that guard
this file goes red and the claim above gets corrected rather than quietly
becoming false; the other asserts `G-STALL` still fires on its own control C7.

**One defect it caught in itself on the first run:** the mechanism pattern
carried `turbulent wake` and *"The wake is turbulent here."* walked straight
through it. Found by the plant, not by reading. **A phrase pattern is only as
good as the word order its author imagined.**

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
