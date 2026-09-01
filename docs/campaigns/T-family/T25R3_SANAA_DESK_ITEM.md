# T25R3 — SANAA'S DESK: three of your five §2 instructions the box will not do, and what we ran instead

**2026-09-01. Two minutes. Registration `8cef4791`, amended `A1`. Lane +
supervisor, heat-transfer.**

Your directive at `f4c8e466` ordered the battery-module fix run today. **It is
registered and the meshes are built.** Three of your five §2 instructions turned
out to be impossible on this box, for reasons that are arithmetic or a line of
OpenFOAM source rather than judgement. **We registered a substitute for each and
are proceeding; under the desk-item rule these are `[lab-attributed]` and adopted
unless you rule within a day. The runs do not wait — the demo is wall-clock
bound.**

---

## 1. ⛔ "Three meshes, channel cells 8/12/18"

**THE DECIDING SENTENCE: your finest level (18 cells across the channel) would
have been COARSER than the 24-cell mesh that produced the failure we are trying
to explain. A convergence study whose finest level is coarser than the run it
exists to explain cannot settle anything.**

Second, independently: holding y+ ≤ 1 as your §0.1 requires, 8 / 12 / 18 cells
across a 3 mm gap need per-cell growth ratios of **2.64 / 1.82 / 1.47**. The mesh
builder refuses anything above **1.35**. Your cell counts and your own y+
requirement are mutually exclusive on this geometry.

**REGISTERED INSTEAD: 24 / 36 / 54 cells across the gap** — 16,608 / 37,368 /
**84,078** cells. Refinement ratio **r = 1.5000 exactly** at both steps, which is
**inside your [1.5, 2.0] band**, at its lower edge. All three meshes are now
built and `checkMesh`-clean.

**COST: ~9× more compute than your family would have been.** You wrote "cost is
not a constraint", so we took you at your word rather than shaving the mesh.

---

## 2. ⛔ "residualControl on p, U, h (1e-7)... no fixed-count sweeps anywhere"

**`chtMultiRegionFoam` has no such control.** Read at source, not in the docs:
`chtMultiRegionFoam.C:109` is a plain counted loop,
`for (int oCorr=0; oCorr<nOuterCorr; ++oCorr)`, and the solver reads exactly one
key, `nOuterCorrectors`. There is no tolerance to set. Getting what you asked for
would mean patching OpenFOAM.

**REGISTERED INSTEAD:** `nOuterCorrectors 15` — your number, as a fixed count —
plus a **sixth run at 30 sweeps** and a gate `G-I` that is **your own §0.2 rule**
promoted to a gate: the iterative change must be at least 10× smaller than the
mesh-to-mesh difference. Measured in kelvin, not in a residual whose meaning in
kelvin nobody knows.

**This is stricter than it sounds.** Composing `G-I` with the discretisation gate
means **iterative convergence to 0.010 K is required for a `PASS`. T25R2 failed
at 0.023 K.** The substitute is **2.3× tighter** than the number that failed the
predecessor.

**COST: one extra run, 314 core-min.**

---

## 3. ⛔ "or adaptive with maxCo 0.5"

The Courant number is ≈1600 at the old step. `maxCo 0.5` means dt ≈ 1.6e-04 s —
**≈5.8 million steps, ~22 core-days for one run of six**, about 490× the
registered step count. It would also destroy the time-convergence study, which
needs a step you can halve exactly.

**REGISTERED INSTEAD: your other option, verbatim** — dt = 0.02 s to t = 70 s,
0.1 s after. Your 1 s load ramps are in, at both edges.

---

## 4. Two things we caught that would have silently wasted the whole spend

- **Your §0.3 acceptance band cannot be [1.5, 2.5] here.** That is the band for a
  second-order scheme; this case runs `Euler` in time and `upwind` in space, both
  **formally first order**. We registered **[0.5, 1.5]**, which is your rule
  applied to the schemes that actually run. The band you wrote would have been
  unpassable by construction.
- **The solver writes `T`, not `h`.** Your §2 names `h`; it is solved for but
  never written to disk. Registering `h` as a required output field would have
  made the completion rule unsatisfiable on every run and produced nothing from
  ~2,000 core-minutes.

---

## 5. What it costs and when you can see it

| | |
|---|---|
| six runs, pre-registered | **1,979 core-min**, hard cap 7,916 |
| dollars, **derived not measured** | **$1.69**, $6.77 at cap |
| against T25R2's actual spend | **×99.9** |
| **grid-convergence verdict** | **≈3.2 h from launch** (3.6 h with contention) |
| **full rung, both ladders** | **≈5.7 h from launch** (6.3 h with contention) |

**Honest and unshaved: if the demo is sooner than ~6 hours from launch, the full
rung will not have graded, and your §7 fallback — the honest-refusal act —
applies.** The space ladder alone lands ~2.5 h earlier and is a real result on
its own.

## 6. What this rung can and cannot reach, said before it runs

**Best case is a VERIFICATION verdict with an uncertainty band** — the answer is
shown to stop moving under mesh and step refinement.

**It can never be a validation.** There is no public dataset for this module: the
geometry is a construction and the loads are your ruling. The band is numerical
only and contains **no model-form uncertainty** — not the 2-D idealisation, not
the isotropic solid, not `kOmegaSST` at `Re = 3200` where it is weakest. Whatever
temperature this rung reports, that is what it is a statement about.

**SUBMISSIONS PARKED. PERMANENTLY PRIVATE.**
