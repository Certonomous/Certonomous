# FINDING NOTE — the A2 MACH-wing family's boundary-layer growth ratio is ~1.33, and the primal sits on a residual floor

**Status: A CANDIDATE, NOT A DEMONSTRATED CAUSE.** Nothing in this note is a verdict, a gate or a
registered change. It records two measurements and names what they could and could not explain, so a
future item can start from evidence instead of from a hunch.
**Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`**, who asked that it be kept out of
the FM6 registration and carried upward as a future item. **Nothing here is sent, filed or submitted**
(`CLAUDE.md` rule 7).

---

## 1. WHY THIS NOTE EXISTS

Arm `FM5` (after-item 9) was `NOT A RESULT`: the fresh-mesh primal ran 1000 iterations with `U`, `he`
and `nuTilda` converged and **the pressure equation alone stalled** at `Primal min residual
1.278377566e-05` against `primalMinResTol = 1.0e-8`.

The rung-1 hypothesis under Sanaa's mesh-then-numerics-then-model ladder was that the family script's
extrusion had given the **fresh** mesh a wall-normal layer defect. **That hypothesis was tested and
refuted** (§2). But the measurement made to refute it turned up a property of **both** meshes that is
worth keeping (§3), and the residual history turned up a second one (§4).

---

## 2. THE REFUTATION — MEASURED, AND THE COMPARISON IS EXACT

`faces.gz`, `owner.gz`, `neighbour.gz` and `boundary` are **byte-identical** between the fresh mesh
(`FM5/constant/polyMesh`) and the base (`base/constant/polyMesh`), and identical again to the warped
mesh `O_mp` ran (`O_mp/mp04/constant/polyMesh`):

| file | md5, all three |
|---|---|
| `faces.gz` | `0a94bba01e37c8587676b056c7a2bb05` |
| `owner.gz` | `16febaf5dfa4137ef7fb1ec4a3659ec5` |
| `neighbour.gz` | `803a7546fd09fcbd673ef1ed52b4fcd6` |
| `boundary` | `c8d1891562dc7a1d5822cd6b94c2c2d4` |

Only `points.gz` differs (`0fb1935a…` base, `a7bfb41c…` fresh). **The three meshes therefore share cell
ordering: same topology, different geometry.**

The wall-normal marching was built **once** — 1008 chains off the `wing` patch, each following the
opposite face of each hexahedron outward, **every chain exactly 39 layers, matching the family script's
registered `N = 39`** — and evaluated against both point sets. Same cells, same chains, same code path.

| quantity | **fresh (pyHyp extrusion of the deformed surface)** | **base (the mesh `O_mp` warped)** |
|---|---|---|
| growth ratio, median | **1.330314** | **1.330151** |
| growth ratio, mean | 1.322246 | 1.322055 |
| growth ratio, max | 1.618285 | 1.618969 |
| growth ratio, min | 0.901984 | 0.898859 |
| first-cell height, median | 2.313647e-03 m | 2.336999e-03 m |
| first-cell height, min / max | 6.076509e-04 / 7.347350e-03 | 6.126944e-04 / 7.601977e-03 |
| pairs with ratio > 1.30 | 25980 / 37296 = 69.66 % | 26046 / 37296 = 69.84 % |
| pairs with ratio > 1.20 | 36822 / 37296 = 98.73 % | 36765 / 37296 = 98.58 % |

Per-layer median ratio, layers 1–12:

```
fresh  1.3115 1.3176 1.3161 1.3099 1.3031 1.2960 1.2917 1.2906 1.2905 1.2892 1.2890 1.2878
base   1.3056 1.3215 1.3190 1.3117 1.3067 1.2989 1.2928 1.2917 1.2918 1.2892 1.2901 1.2887
```

**The medians differ by 0.012 %, the means by 0.014 %, and the fresh mesh's MAXIMUM ratio is LOWER than
the base's.** Its first cell is **1.0 % smaller**, i.e. marginally finer. **There is no growth-ratio
defect in the fresh mesh.** The hypothesis is refuted, and independently so: the same stall occurs on
the **warped** mesh (§4), which the extrusion never touched.

*(Corroborating, measured by `dafoam-supervisor`, not by this note: the fresh mesh's maximum aspect
ratio is 411.4 against the base's 1007–1050 trips — on that metric too the fresh mesh is the better of
the two.)*

---

## 3. THE CANDIDATE — ~1.33 PER LAYER IS AGGRESSIVE, IN BOTH MESHES

Standard boundary-layer meshing practice puts the wall-normal expansion ratio at **1.1–1.2**. This
family runs at a **median 1.33**, with **98.7 % of all cell pairs above 1.20** and **69.7 % above 1.30**.
That comes from the family script's own pyHyp parameters — `N = 39`, `s0 = 1.0e-3`, `marchDist = 300.0`,
`cMax = 0.1` — reaching a 300 m far field in 39 layers off a millimetre first cell, which forces a large
ratio arithmetically.

**WHAT THIS CANNOT EXPLAIN, STATED FIRST SO THE NOTE IS NOT MISREAD.** It cannot explain any
fresh-versus-warped difference, because it is **the same in both**, and it is present in the mesh that
produced every graded `O_mp` number. Nothing in `D6R2C`'s record is invalidated by it.

**WHAT IT IS A CANDIDATE FOR.** The question underneath three `NOT A RESULT` rows: *why does this
configuration stall at all?* A high expansion ratio degrades the accuracy of the wall-normal gradient
reconstruction and raises the condition number of the pressure equation — and it is the **pressure
equation alone** that stalls, with `U`, `he` and `nuTilda` all converged. That is a coincidence worth
testing. **It is not evidence that it is the cause, and this note does not claim it is.**

**HOW IT WOULD BE TESTED, IF A FUTURE ITEM TAKES IT.** Re-extrude with the same family script at a lower
ratio — more layers for the same `marchDist`, or a larger `s0` — and re-solve the same design point. If
the floor of §4 moves, the ratio is implicated; if it does not, this candidate is eliminated cheaply.
**That is a new pre-registration and it is not registered here.**

---

## 4. THE SECOND MEASUREMENT — THE PRIMAL IS ON A FLOOR, NOT CONVERGING SLOWLY

From `FM5_20260913T064704Z_1398444.log`, the pressure equation's per-iteration normalised residual on
the **fresh-mesh** solve (the trajectory whose final value matches the reported
`Primal min residual 1.278377566e-05` to all ten digits):

| iteration | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| `p initRes` | 1.103e-03 | 1.837e-04 | 2.242e-05 | 1.3034e-05 | 1.2795e-05 | 1.27849e-05 | 1.27841e-05 | 1.27839e-05 | 1.27838e-05 | 1.278378e-05 |

**It falls by 4.5 decades in the first 300 iterations and then stops.** Over the last 400 iterations it
moves by a **relative 8.456e-05** — the sixth significant figure. The other trajectory in the same log
behaves the same way one decade lower, plateauing at `1.2161568500e-06` with a relative change of
`2.646e-04` over its last 400 iterations.

**THE CONSEQUENCE, AS ARITHMETIC.** At the rate observed over `FM5`'s last 400 iterations, reaching
`primalMinResTol = 1.0e-8` from `1.278e-05` — a factor of 1278 — would take of order

```
400 × ln(1278) / ln(1.00008456)  ≈  3.4 × 10^7 iterations
```

**This is not a primal that needs more iterations. It is a primal that has stopped.**

**WHY THIS MATTERS TO THE NEXT EXPERIMENT, AND IT CUTS AGAINST IT.** Arm `FM6` registers a converged
initial field. **A converged initial field changes where the solve STARTS, not where the floor IS.** If
the floor is a property of the discretisation, `FM6` will reach it faster and still not converge. That
possibility is registered in advance in `PREREGISTRATION_AFTER_ITEM9_R2.md` with its predicted
signature, so that outcome is a **measured refutation of the rung-2 change** rather than something
reinterpreted afterwards.

**HONEST LIMIT OF §4.** `p initRes` is the linear solver's own normalised residual for one iteration;
`primalMinResTol` is measured by DAFoam on a different norm. The two are **not** the same quantity, and
this note does not equate them. What is established is the **shape** of the trajectory — a fall, then a
flat line — and that shape is normalisation-independent. Which phase and condition the second trajectory
belongs to was **not** established: the log holds more than one solve and the splitting was unreliable,
so no claim is made about it beyond its own numbers.

---

## 5. WHAT THIS NOTE DOES NOT CLAIM

- **It does not claim the growth ratio causes the stall.** It is a candidate with a coincidence behind
  it and a cheap test in front of it.
- **It does not claim the fresh mesh is defective.** It measured the opposite: on every metric compared
  here the fresh mesh equals or slightly betters the base.
- **It does not re-grade anything.** `FM5`, `FM3`, `FM4`, `DEC`, `DEC2` and `DEC3` stand at
  `NOT A RESULT`; `O_mp` stands at `GATE FAIL`.
- **It registers no change and authorises no compute.** The one registered change on Sanaa's ladder is
  in `PREREGISTRATION_AFTER_ITEM9_R2.md`, and it is not this.
- **It does not touch `primalMinResTol`.** If the floor survives a clean mesh and a converged initial
  field, that is a finding about this `DARhoSimpleFoam` configuration and it goes to Sanaa as one.

---

## 6. THE ARTEFACTS THESE NUMBERS CAME FROM

| measurement | artefact |
|---|---|
| growth ratio, both meshes | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh/FM5/constant/polyMesh` and `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/base/constant/polyMesh` |
| connectivity identity | the same two, plus `…/O_mp/mp04/constant/polyMesh` |
| residual history | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-AFTER-a2-wing-decomposition-and-freshmesh/FM5_20260913T064704Z_1398444.log` |
| the warped-mesh stall statistics | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp/d6r2c_evals.jsonl` (md5 `2c0b8143caad198cd2e21d8047986aa3`) |

**The measuring script is not a repository artefact and is not cited as one** (rule 13): it was a
throwaway in the lane's scratchpad. Every number above is reproducible from the four artefacts named,
and the method is stated in §2 in enough detail to re-derive it.
