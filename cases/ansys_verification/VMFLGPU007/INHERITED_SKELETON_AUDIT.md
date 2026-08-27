# VMFLGPU007 — audit of the INHERITED case skeleton

**Written by `ansys-lane-opus` (lane R2), 2026-08-27, before any pre-registration exists and
at ZERO COMPUTE.** The `case/` and `reference/` trees in this directory were left uncommitted
on disk by the lane killed at ~17:50Z. My brief was to *inspect it, do not assume it is
right, and commit what you keep*. This file records exactly what I checked, what passed, and
what I did **not** check — so that nothing here is mistaken for a verified input later.

**Compute state, measured, not assumed:** there is **no `VMFLGPU007` run root anywhere** —
not `verification/runs/ansys_verification/VMFLGPU007` on the lab box, not on the GPU
instance, and `find /home/ubuntu -iname '*VMFLGPU007*'` outside this case directory returns
nothing on either machine. (`VMFL007` and `VMFL007_R2` under the run tree are the CPU case
VMFL007 — a **different case**, not this one.) **Zero core-minutes and zero GPU-seconds have
been spent on VMFLGPU007.**

`BAND_DECISION_ORDER.md` (inherited, kept) refers to *"a 20-iteration smoke of this case runs
`rc = 0` and writes every artefact"*. **No artefact of that smoke survives on either box**, so
I cannot verify it and **I do not carry it as a measurement.** It is recorded here as an
inherited claim with no surviving evidence. Nothing in the band rests on it.

## VERIFIED IN THIS LANE

| input | what I checked | result |
|---|---|---|
| `reference/VMFL013_htc.xy` | parsed it myself and took the maximum | **peak Nu = 64.8530 at x/H = 5.8209**, 19 two-column rows, x/H spans 0.8206–15.8999. **Exactly the numbers `BAND_DECISION_ORDER.md` fixes the band on** — that document's central claim is independently confirmed. The leading `0 0 0 0` line is a 4-column padding row and is correctly not one of the 19. |
| `constant/thermophysicalProperties` | recomputed the Prandtl number from the manual's own three properties | `Pr = mu·Cp/k = 1e-4 × 10000 / 1.408 = 0.7102272727…`, and the file carries `Pr 0.7102272727272728`. **Internally consistent with the manual's table**, and an air-like Pr as the case requires. `rhoConst rho = 1.0`, `Cp = 10000`, `mu = 1e-4` all match the manual's Material Properties column. |
| `constant/turbulenceProperties` | read against the manual | `RAS { RASModel kEpsilon; … }` — the standard k-ε the manual's Analysis Assumptions block specifies. |
| `constant/g` | read | `(0 0 0)` — gravity off. With `g = 0` the buoyant solver's `p_rgh` is identically `p`; the choice buys a temperature field without introducing buoyancy the manual does not specify. Registered as a modelling choice, not a physical claim. |
| `system/fvSolution.template` | read | solvers `p_rgh` and `"(U|h|k|epsilon)"`, all routed through `petsc` with `__MATTYPE__` / `__VECTYPE__` placeholders — the two-arm GPU/forced-CPU substitution this family uses. |
| `0/T` | read | inlet `fixedValue 300`; **`heatedWall` = `externalWallHeatFluxTemperature`, `mode flux`, `q uniform 1000`** — matching the manual's *"Wall heat transfer, Q̇ = 1,000 W/m²"*. `stepFace`, `ductBottom`, `topWall` are `zeroGradient` (adiabatic). |
| `0/` completeness | drove the repaired guard against a materialised copy | `FIELD COMPLETENESS OK: closure=kEpsilon required={T, U, epsilon, k, p_rgh} all present in 0/` |

## NOT VERIFIED — stated plainly so it is not assumed

- **The mesh.** `system/blockMeshDict.template` has not been read line by line, no `blockMesh`
  has been run, no cell counts confirmed and **no mesh birth certificate exists**. The
  geometry the manual omits (expansion ratio, channel width, upstream and downstream domain
  lengths) has **not** been traced back to the `VMFL013_WB.wbpz` archive by me.
- **The 101-point inlet.** `constant/boundaryData/inlet/{points,0/U,0/k,0/epsilon}` and their
  provenance from `reference/VMFL013_step_ve.set.prof` are **unchecked**; the header comment
  claims 101 points at x = −3.8 H and I did not count them or confirm the mapping.
- **`0/U`, `0/k`, `0/epsilon`, `0/nut`, `0/alphat`, `0/p`, `0/p_rgh` boundary conditions**,
  beyond their existence.
- **`system/fvSchemes`, `system/controlDict.template`** — not read.
- **`reference/VMFL013_nu2.xy`** (Fluent's own wall-4 Nu, 101 rows) — not parsed. It is
  Ansys's own result and is **context, never the gate** (charter §5.1).
- **The adiabatic choice** on the step face and opposite wall is a real degree of freedom —
  Vogel & Eaton heated the downstream wall — and must be registered explicitly in the
  pre-registration as a modelling decision.

**Consequence: this skeleton is committed as INHERITED WORK IN PROGRESS, not as a frozen
input set.** It is not a pre-registration, it freezes nothing, and no gate rests on it. The
unchecked items above must be closed before VMFLGPU007 can be frozen.

## The manual defect, verified in this lane rather than taken on report

The manual's **Test Case** paragraph for VMFLGPU007 (p.243) is **byte-identical to
VMFLGPU006's** (p.239) — 493 bytes, sha256 `97e3b55607077c11…`, sidecar lines 6229–6233
against 6168–6172, confirmed by `cmp`. It describes *"airflow over a Goldman stator blade at
the mid-span … typical of turbomachinery applications"*. **This case is a backward-facing
step. The paragraph is about a different geometry and is not a source of setup for it.**

**A third instance exists and it is legitimate:** the same paragraph appears at sidecar line
5453 under **VMFL071: Mid-Span Flow Over a Goldman Stator Blade** — the CPU Goldman case,
where it belongs — differing only in *"2D"* against VMFLGPU006/007's *"2.5D"*. So the defect
is specifically that **VMFLGPU007 carries VMFLGPU006's paragraph verbatim**, not that the
manual repeats a stock paragraph everywhere.

**What is NOT defective on that page, and this matters for the freeze** — the supervisor's
brief treats the prose as wholly unusable, and it is not:

- The **Reference** field is intact and correct: *J.C. Vogel, J.K. Eaton, "Combined Heat
  Transfer and Fluid Dynamic Measurements Downstream of a Backward-Facing Step", Journal of
  Heat Transfer, Vol. 107, pp. 922–929, 1985.*
- **Physics/Models** is correct and case-specific: *"Incompressible, turbulent flow with heat
  convection and reattachment."*
- **Input File** is correct: `vt007.msh, vmfl007.jou`.
- **The Analysis Assumptions and Modeling Notes block (p.244) is entirely correct and
  case-specific**, and IS a legitimate source of setup: *"The flow is steady and
  incompressible. Fluid properties are considered constant. Pressure based solver is used.
  The inlet boundary conditions are specified using the fully developed profiles for the
  velocity, k, and epsilon. The incoming boundary layer thickness is 1.1 H. Under the given
  pressure conditions, the Reynolds number, ReH is about 28,000. The standard k-ε model with
  standard wall functions is used for accounting turbulence."*
- The **Material Properties** column is correct and complete (ρ, μ, k, Cp) and passes the
  Prandtl consistency check above.

**The Geometry column IS truncated**: it gives `H = 1 m` and nothing else — no expansion
ratio, no channel width, no upstream or downstream domain length. The Boundary Conditions
column also carries a stray bare `I` before the velocity-profile entry.

**So the honest statement the pre-registration must carry is narrower and stronger than
"the prose is defective":** the **Test Case paragraph** is a verbatim copy of another case's
and is not the source of anything; the **Analysis Assumptions block and Material Properties
are sound and ARE sources**; and the **geometry is truncated and must come from the
`VMFL013_WB.wbpz` archive** (charter §2: archives are read for setup and reference numbers
only, never to make a claim about Ansys). The band comes from the digitised Vogel & Eaton
data in `reference/`, not from the manual's figure and not from Ansys's own curve.

**Archive location, measured:** `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/VMFL013_WB.wbpz`.

---

## A BLOCKER FOUND AT COMMIT TIME: the gate's reference data was GITIGNORED

**`.gitignore` line 68 is `*.xy`.** Both inherited reference files —
`reference/VMFL013_htc.xy` (the Vogel & Eaton measurements the band is built on) and
`reference/VMFL013_nu2.xy` (Fluent's own wall-4 curve) — are matched by it and were
therefore **invisible to git**. Confirmed with `git check-ignore -v`, not inferred.

**Why that is a freeze blocker and not a tidiness issue.** Under CLAUDE.md rule 2 the freeze
is the document's entire evidentiary content, and the gate here is
`|Nu_peak − 64.8530| / 64.8530 ≤ 0.20` — a band computed **from that file**. An untracked
reference cannot be cited by blob sha, cannot be shown unchanged between the freeze and the
grade, and could be edited after the answer was known with nothing in git to show it. **A
gate whose reference is untracked is not frozen.** This is the class of the standing lesson
*gitignored is not filed*: a check that asks git is blind to exactly the file that matters.

**The repair follows this family's own precedent rather than inventing one.** VMFLGPU003
faced the same rule and solved it by copying the archive's two-column data **byte-for-byte**
into a `.csv` beside the case (`reference/vmfl011_benchmark_xnorm.csv`, tracked). The same is
done here:

| tracked file (committed) | copied byte-for-byte from (on disk, untracked) | content |
|---|---|---|
| `reference/vmfl013_vogel_eaton_nu.csv` | `reference/VMFL013_htc.xy` | the EXPERIMENTAL reference — Vogel & Eaton 1985 as digitised by Ansys; **this is the file the band cites** |
| `reference/vmfl013_fluent_wall4_nu.csv` | `reference/VMFL013_nu2.xy` | Fluent's own wall-4 Nu, 101 rows — **context only, never the gate** (charter §5.1) |

Byte-identity was verified with `cmp` in the same invocation that made the copies; nothing
was re-digitised, re-fitted, smoothed or re-ordered. **The `.xy` originals stay on disk,
untracked, as the extraction artifacts they are** — they are not force-added past the ignore
rule, because the fix is to have a tracked artifact, not to defeat a rule other teams rely
on. **`.gitignore` is NOT edited by this lane.**

**The pre-registration must cite the `.csv` blob shas**, not the `.xy` paths.

`reference/VMFL013_step_ve.set.prof` is **not** matched by any ignore rule and is committed
under its own name.
