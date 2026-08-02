# W3 — replicate meshes at the NACA 4412 rung the credential is graded from

**Meshed and solved 2026-08-02 08:24:30 → 08:37:30 UTC.** Serves docket item
`agp-d392641d60f4`, *"Close the validation gap on the NACA 4412 finite wing"*.

Driver: `sdk/scripts/naca4412_layered_replicates.py`, which imports
`sdk/scripts/naca4412_credential_repair.py` rather than copying it, so the case
build cannot drift from the one that produced the graded rung. Cases:
`/home/ubuntu/certonomous-runs/w3-naca4412-layered-replicates/{A,B,C,D,E}`.

---

## 1. Why this and not what the item asked for

The item proposes that *"a refined near-wall setup can close the gap or explain
it on the record."* **The refined near-wall setup is already what is being
graded, and near-wall resolution is already measured not to be the lever.**

* The graded rung is `add_layers=True`, 12 prism layers, target y⁺ 30, 94.5% of
  target layer thickness (`models/curriculum/results/naca4412_wing.json`).
* `ACTIVE_RESEARCH.md` §C3, measured 2026-07-28: at fixed refinement, across a
  **17.7-fold change in boundary-layer coverage (4.36% → 77.0%), drag moved
  0.037%** while lift moved 9.41%.

So the premise's own instrument is spent. Meanwhile every replicate study this
lab has run — Ahmed 25°, cube, NACA 0015 sail (`W3_PUBLISHED_RUNG_REPLICATES.md`)
and NACA 0012 (`W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md`) — was built with
`addLayers false`, and the 4412 is **the only wall credential graded from a
layered mesh**. Layer addition is where snappyHexMesh makes its most
path-dependent decisions, so the unlayered scatter does not transfer. Nobody had
measured whether this credential's +34.6% (now +16.35% against the repaired
reference) survives a change of background mesh.

## 2. Method

Four cases identical in every respect except the `blockMeshDict` hex division
triple. **A is the control and must reproduce the stored mesh.** The three
perturbations B, C, D are the *same triples* used on the NACA 0012, so the two
bodies are comparable and the set was not chosen after seeing this body's
answer. All at **4 MPI ranks, scotch**, 161,312–166,719 cells per rank.

Reference, from `models/curriculum/naca4412_wing/reference.yaml` as repaired on
2026-08-01 (commit `d45f3090`, the version that no longer moves with the solve
it grades): **Cd 0.015696, band ±9.56% → [0.014195, 0.017197]**.

## 3. One of the four replicates could not be built at all

**D at (35 58 20) fails to mesh.** `snappyHexMesh` rejects the recipe's own seed
point in the refinement phase:

```
--> FOAM FATAL ERROR: (openfoam-2606)
Point (6.50165 0 0.0349165) is not inside the mesh or on a face or edge.
Bounding box of the mesh:(-3.0012 -9 -2.96598) (7.0018 9 3.03582)
```

`locationInMesh` is placed at the box centre in the span direction, which is
**exactly on a block-face plane whenever the span division count is even**
(index coordinate 30.000000 at the stored triple, 29.000000 at D's). B and C
have odd span counts and land at 29.5 and 30.5, safely interior. **The stored
production mesh is one of the fragile ones and got away with it.** A substitute
fourth replicate E = (34 60 21) was run; D is kept in the driver, not deleted,
because the failure is a result.

## 4. Results

| tag | divisions | cells | Cd | dev. from 0.015696 | in band? | Cl | max non-ortho | converged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A** (control) | (33 60 20) | **645 251** ✓ | 0.018262714 | **+16.35%** | no | 0.209554 | 64.989619 | yes |
| B | (34 59 21) | 652 249 | 0.020787415 | **+32.44%** | no | 0.246219 | 64.958100 | yes |
| C | (32 61 21) | 653 090 | 0.019911782 | **+26.86%** | no | 0.242685 | 74.962443 | yes |
| D | (35 58 20) | — | — | — | — | — | — | **did not mesh** |
| E | (34 60 21) | 666 878 | 0.020803581 | **+32.54%** | no | 0.246325 | 64.976520 | yes |

**Control.** A reproduces the stored production mesh to the cell — 645 251
against 645 251 — its drag to **1.6 × 10⁻⁵ relative** (0.018262714 against the
stored 0.018262421), its lift to 3.3 × 10⁻⁵, and its max non-orthogonality to
every printed digit (64.989619). The recipe is deterministic and this is the
same solve.

## 5. The verdict is reproducible. The number is not.

**All four meshes read outside the band, all on the same side, +16.35% to
+32.54%.** The NACA 4412's `NOT VALIDATED` verdict survives mesh construction.
That is a real check the credential passes, and it is the opposite of the NACA
0012, where one of four replicates was outside the band and three were inside and
the published mesh was the one that failed.

But the value it fails by does not survive at all:

| | value |
| --- | --- |
| Cd mean over the four buildable meshes | 0.019941373 |
| sample stdev | 1.194 × 10⁻³ |
| **range** | **2.541 × 10⁻³ = 12.74% of the mean** |
| A's own iterative noise (final-window σ) | 7.692 × 10⁻⁶ |
| **scatter ÷ 2σ iterative** | **165×** |
| reference band half-width (±9.56% of 0.015696) | 1.501 × 10⁻³ |
| **scatter ÷ band half-width** | **1.69×** |

**Mesh construction alone moves this body's drag by 1.69 times the entire
half-width of the band it is graded against.** Tightening that band is
meaningless until this is under control, and so is any claim about *where in*
the band a future solve lands.

Three further comparisons, each against a number this lab already published:

* **The published mesh is the minimum of its own family.** The graded value
  0.018263 is the smallest of the four — the most favourable, the closest to
  passing. On the NACA 0012 the published mesh was the *maximum* of its four, the
  least favourable. In both cases the published mesh is an extremum of its own
  replicate distribution, which is what publishing a single draw from a
  12.7%-wide distribution looks like.
* **The scatter is 28× the whole ladder's drag variation.** Commit `d45f3090`
  records the four finest rungs of this wing — 645 251 to 2 091 678 cells, a
  3.2-fold cell-count change — agreeing on drag to **0.45%**. One rung rebuilt
  four ways spans **12.74%**.
* **It is 344× the layer-coverage effect.** §1's 17.7-fold coverage change moved
  drag 0.037%. Background divisions move it 12.74%. Whatever is worth studying
  on this body's drag, it is not the boundary layer.

Lift is worse: range 3.677 × 10⁻² on a mean of 0.236196, **15.57%**. This is the
same ordering `naca4412-converge-lift-coefficient` found on the unlayered family
(lift scatter 120% of its increments against drag's 109%), and it holds with
layers resolved.

## 6. And the non-orthogonality gate is reading a dictionary ceiling, not a mesh

The credential's own record names the finer rung's **74.96** max non-orthogonality
as failing the lab's 70° gate, calls it *"degraded, not improved, at the largest
cell count"*, and nominates it *"the leading suspect for the non-monotonicity."*

Replicate C reaches **74.962443 at 653 090 cells** — a third of the finer rung's
1 849 113 — against the finer rung's **74.962218**. The two agree to
**3.0 × 10⁻⁶ relative**, which is not two meshes happening to be similarly bad.

The reason is in `external_aero.py:399,403`, which every case on this wall shares:

```
maxNonOrtho 65;
...
relaxed { maxNonOrtho 75; }
```

**Every mesh in this family is pinned to one of its own two dictionary limits.**
A, B and E sit at 64.958–64.990, just under the strict 65; C and the stored finer
rung sit at 74.962, just under the relaxed 75. Only the medium rung (58.374) is
genuinely below both. So `max non-orthogonality` on these meshes reports *which
constraint branch snappyHexMesh ended on*, not how good the mesh is — and a
70° gate applied to it is a coin whose two faces are 65 and 75.

### 6.1 The check, run rather than left as a claim

Every `log.checkMesh` under `/home/ubuntu/certonomous-runs`, 70 meshes. The
pinning is real, it reaches beyond this body, and it is **not universal** —
which is what makes it a usable rule rather than a scare:

| band | meshes | which |
| --- | --- | --- |
| **pinned to the strict 65** (64.64–64.99) | **8** | NACA 4412 fine + replicates A, B, E; `finer_relayered_ngrow0`; motorBike; `mb-iterfix/medium`; **B-52 `finer2-uq` 64.646803 and `rung7-uq` 64.640997** |
| **pinned to the relaxed 75** (74.31–74.96) | **3** | NACA 4412 `finer` 74.962218, `finer_relayered` 74.312074, replicate C 74.962443 |
| genuinely below both | ~53 | everything ≤58.4: NACA 4412 medium 58.374, B-52 `fine-uq` 57.716, the whole W3 0012/4412 unlayered families 29–49, the supersonic and cone ladders 7–15 |
| above the relaxed ceiling | 6 | `rae2822-meshcheck/og-*` 80.2–160.9, `tmr-naca-a0-coarse` 85.7 — **externally supplied grids, no `log.snappyHexMesh`, so no dictionary applies**, which is the control that confirms the reading |

**Eleven meshes across three unrelated bodies — the NACA 4412, the motorBike and
the B-52 — sit within 0.7° of one of two dictionary numbers.** The B-52 pair is
the strongest evidence that this is not a 4412 quirk: `finer2-uq` and `rung7-uq`
land at 64.646803 and 64.640997, 6 × 10⁻³ degrees apart, on a different body from
a different study, under the same `meshQualityDict`.

**And the lab's 70° gate sits between the two ceilings.** For any mesh hard
enough to press against the constraint — which is exactly the meshes a gate is
for — the gate has no resolution: it returns "pass at ≈65" or "fail at ≈75"
according to which branch `snappyHexMesh` ended on, and nothing in between. A
mesh that is genuinely below 65 was never in question.

What this does **not** say: that any of these meshes is bad. A mesh sitting on
its constraint is a mesh the constraint held, which is the constraint working.
The defect is in *reading the reported maximum as a measurement of quality* and
then attributing its movement to refinement.

## 7. Cost, measured on CPU

| | |
| --- | --- |
| ranks | 4, scotch |
| cells per rank | 161 312 / 163 062 / 163 272 / 166 719 |
| **total, CPU basis** | **29.608 core-min** |
| solve `ExecutionTime` vs `ClockTime` | 77.04/77, 74.78/75, 66.2/67, 74.15/74 — **contention −0.2% to +1.2%** |
| item's filed estimate (`cost_basis: estimate`) | 20 core-min → **1.48× over** |
| estimate re-derived from the graded rung's own measured 76.97 s snappy + 68.57 s solve at 4 ranks | ≈28 core-min → **1.06× over** |

The overrun sits exactly where the lab's own rule says it will: the filed
*estimate* basis missed by 1.48×, and a basis built from this body's own measured
run missed by 1.06×.

**And meshing cost is itself mesh-construction-sensitive.** `snappyHexMesh`
reported 76.36 s (A), 73.14 s (B), 96.51 s (E) and **361.79 s (C)** — the same
recipe at a different background triple costs **4.7× the meshing time**, on a job
this lab has repeatedly priced as meshing-bound.

## 8. What this does to the item

* The premise — *"a refined near-wall setup can close the gap"* — is **refuted on
  this body's own measurements**, and the item is re-scoped rather than closed on
  a number it did not ask for. See the docket.
* `models/curriculum/results/naca4412_wing.json`'s grid-study note, which names
  the 74.96 non-orthogonality as the leading suspect for the ladder's
  non-monotonicity, **rests on a dictionary ceiling** and should not carry that
  weight.
* The verdict `NOT VALIDATED` **holds**, and now holds on four meshes rather than
  one.
