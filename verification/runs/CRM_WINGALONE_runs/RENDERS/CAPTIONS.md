# CRM WING-ALONE RENDER — CAPTION. **USE VERBATIM.**

## `CRM_L2R_mesh_surface.png`

> **NASA CRM wing-alone — surface mesh, L2 (1,158,144 cells), M = 0.85, Re = 5×10⁶, α = 2.0°.**
> 11,136 rendered faces on the `wing` patch — **exactly the count registered in §2 of the
> pre-registration** and hit by arm P1C, per-patch identity verified against the case's own
> `boundary`.
> **L2 is the ONLY mesh-admissible level in this family** (L1 `GATE FAIL` on layer quality,
> L3 `GATE FAIL` on non-orthogonality), so **no grid-convergence claim exists or can exist**.
> **The run graded `GATE FAIL`** — residuals and force plateau both breached. **No `Cd`, `Cl`
> or `Cm` is quoted on this image**; the QoI is **REPORTED, NOT GATED**, because no wing-alone
> CRM force or Cp dataset exists on this box to validate against.

**HONEST DEFECT IN THIS RENDER, NOT HIDDEN:** the wing is **dark and small in frame**. The
geometry is correct and verified (swept, tapered, Yehudi break visible at the inboard trailing
edge), but camera and lighting are poor. Per the renderer's own doctrine *"polish is camera,
colormap, background, resolution; polish is NEVER the data"* — **the data is right and the
polish is owed.** It is not fit for a filmed demo as it stands.

## WHAT MUST NOT BE PUT ON THIS IMAGE
- No `Cd`/`Cl`/`Cm` as validated values — there is nothing on this box to validate against.
- No grid-convergence or observed-order claim.
- No suggestion that `GATE FAIL` is a soft pass. The run completed; two registered gates were
  breached.
