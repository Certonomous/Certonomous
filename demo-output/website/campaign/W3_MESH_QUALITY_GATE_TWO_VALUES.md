# W3 — a mesh-quality gate that says whether it read the mesh or the recipe

**Written 2026-08-02, zero solver compute.** Serves docket item
`w3-a-gate-that-returns-two-values`, *"Replace the mesh-quality gate, which
cannot distinguish a good mesh from one pressed against a ceiling."*

Code: `sdk/workflows/geometry_study.py` (`ceiling_pinned`,
`mesh_quality_reading`, `mesh_pinning_notes`), `sdk/workflows/_mesh_quality.py`,
`sdk/chief_engineer/certificate.py::_mesh_rows`,
`sdk/scripts/naca4412_credential_repair.py::parse_checkmesh`.
Tests: `sdk/tests/test_geometry_study.py::PinnedGateTests`.

---

## 1. What the old gate was reading

`external_aero._MESH_QUALITY` writes the same `meshQualityDict` into every
snappyHexMesh case this lab builds:

```
maxNonOrtho 65;  maxBoundarySkewness 4;  maxInternalSkewness 4;
relaxed { maxNonOrtho 75; }
```

Those are constraints the mesher enforces. A mesh hard enough to press on one
reports the ceiling back. Over the **98** `log.checkMesh` files on this box
(`/home/ubuntu/certonomous-runs`, read 2026-08-02):

| reading | meshes | where |
| --- | --- | --- |
| max non-orthogonality 64.64–64.99, under the strict 65 | 9 | NACA 4412 fine + replicates A/B/E + `finer_relayered_ngrow0`, motorBike, `mb-iterfix/medium`, B-52 `finer2-uq` 64.646803 and `rung7-uq` 64.640997 |
| max non-orthogonality 74.31–74.96, under the relaxed 75 | 3 | NACA 4412 `finer`, `finer_relayered`, replicate C |
| max skewness 3.896–3.99994, under the ceiling 4 | 5 | B-52 `fine-uq`, `finer2-uq`, `rung7b-uq`, `validation-scratch/b52`, motorBike |
| above the relaxed ceiling | 6 | rae2822 O-grids 80.2–160.9, `tmr-naca-a0-coarse` 85.7 — externally supplied, **no `log.snappyHexMesh`, so no dictionary applied**, which is the control |

**Two of this lab's own gates sit on top of a dictionary number.**
`MAX_NON_ORTHOGONALITY = 70` lies *between* the strict 65 and the relaxed 75, so
for any mesh that pressed its constraint it returns pass-at-65 or fail-at-75 and
nothing between. `MAX_SKEWNESS = 4.0` is *exactly* the dictionary ceiling:
`study-b52-finer2-uq` reads **3.9999437** and clears a 4.0 gate by 5.6 × 10⁻⁵.
**That gate cannot fail a mesh the dictionary held.**

### 1.1 The clean demonstration, measured today for free

The same four background-division triples on the NACA 4412 wing, at two
refinements (`W3_NACA4412_RESOLUTION_SCATTER.md`):

| triple | refinement 3 max | refinement 4 max |
| --- | --- | --- |
| (33 60 20) | 58.374353 | 64.989619 |
| (34 59 21) | 62.390692 | 64.958100 |
| (32 61 21) | 57.556267 | **74.962443** |
| (34 60 21) | 60.801266 | 64.976520 |

At refinement 3, where no mesh presses its constraint, four different meshes
read four different numbers across **4.83°**. At refinement 4 three of them
agree to **0.032°** — they are reporting the same ceiling — and the fourth
reports the other ceiling. A gate at 70 splits that column 3–1, and the split is
the branch `snappyHexMesh` ended on.

## 2. What the gate returns now

`mesh_quality_reading(stats)` returns the verdict **and** whether the verdict was
decided by a measurement:

* `verdict` / `passed` — unchanged, so no caller loses a judgement it had;
* `informative` — **False** when either reading sits within 1.0° (non-ortho) or
  0.15 (skewness) of a `meshQualityDict` ceiling;
* `non_orthogonality_pinned_to`, `skewness_pinned_to` — *which* constraint the
  number is a restatement of;
* `severe_faces`, `faces`, `severe_fraction` — the **extent**, which is what the
  binary threw away;
* `notes` — the sentences that say all of the above in the record.

The tolerances are read off the measured population, not chosen: the widest gap
between a pinned reading and its ceiling is **0.36°** (64.641 vs 65) and 0.104
(3.896 vs 4), and the nearest *unpinned* reading is **58.4°** and 3.535. Any cut
between separates the two populations; 1.0 and 0.15 are that cut.

The certificate's mesh block now prints the pinned clause beside the number, and
prints a pinned angle to two decimals — at one decimal a genuine 74.962 renders
as `75.0`, which is exactly its own limit and hides the very thing being flagged.

## 3. One half of the item's own premise does not survive

The docket rationale proposed two replacement readings. **Only one of them
works, and this record says so rather than shipping both.**

* **Average non-orthogonality is unpinned** — the four refinement-4 replicates
  read 9.3878–9.4849 while their maxima are bimodal at 65 and 75. True.
* **But it is not a quality gate.** On this lab's own population it does not
  separate good meshes from bad: the rae2822 O-grids, whose maxima are
  **80.2–160.9** with no dictionary applied, average **9.05–11.13** — the same
  9.39–9.90 that the accepted snappyHexMesh meshes read. It is reported by
  `mesh_quality_reading` and explicitly **not** gated on
  (`average_discriminates: False`).
* **A count of faces above threshold does survive, with a caveat the rationale
  did not state.** At checkMesh's own 70° threshold the count *partitions*
  identically to the 70° max gate, because the strict branch is at 65 and can
  have no face above 70. What it adds is not a different partition but an
  **extent**: 797 faces of 5,740,702 rather than "74.96 fails 70". Its
  magnitudes are unpinned and span two orders of magnitude across the
  population — 9.7 × 10⁻⁵ to 2.8 × 10⁻⁴ on the rae2822 O-grids, 8.1 × 10⁻³ to
  9.7 × 10⁻³ on the rae2822 C-grids, exactly 0 on every mesh whose dictionary
  held.

## 4. The parser that fed the gate never read the quantity

`naca4412_credential_repair.parse_checkmesh` matched only
`Max non-orthogonality = X`, which OpenFOAM 2606 does not print — it prints
`Mesh non-orthogonality Max: X average: Y`. **Every stored `result.json` under
`w3-naca4412-layered-replicates` carries a cell count and a skewness and no
non-orthogonality at all**, and the published replicate table's angles were read
out of the logs by hand. Both spellings are matched now, along with the face
count, the average and the severe-face count. `_mesh_quality.parse_check_mesh`
gained the same three readings.

## 5. Every affected credential, regraded

Two graded records carry a non-orthogonality reading.

**`models/curriculum/results/ahmed_35.json`** reads 49.6 — 15.4° clear of the
strict ceiling, unpinned, informative. No regrade needed, and saying so is part
of the check.

**`models/curriculum/results/naca4412_wing.json`**, all three ladder rungs, in
`grid_study.rungs[*].mesh_quality_regrade_2026_08_02`:

| rung | cells | max | pinned to | severe faces / faces | fraction | informative |
| --- | --- | --- | --- | --- | --- | --- |
| medium | 263 359 | 58.374353 | — | 0 / 820 472 | 0 | **yes** |
| **fine (graded)** | 645 251 | 64.989619 | **65** | 0 / 2 008 367 | 0 | no |
| finer | 1 849 113 | 74.962218 | **75** | **797 / 5 740 702** | 1.39 × 10⁻⁴ | no |

Two things change on this credential.

* **The graded rung's `mesh_gates_pass: true` is not a measurement.** 64.989619
  is 0.010° under the ceiling the recipe wrote; the 70° gate could not have
  failed it. The pass still stands — but it stands on the **extent**, 0 of
  2,008,367 faces above 70°, not on the maximum.
* **The finer rung's gate failure is real in kind and small in extent.** 797 of
  5,740,702 faces, 1.39 × 10⁻⁴, against exactly zero on both other rungs. The
  magnitude 74.96 carries none of that information; it is the ceiling. The
  rung's real difference from the other two is **layer coverage at 58.3% of
  target**, not non-orthogonality — which is where the ladder's non-monotonicity
  should be looked for.

## 6. Cost

Zero solver compute. Reading: 98 `log.checkMesh` files, three graded records,
one code path. The refinement-3 replicate maxima in §1.1 are a by-product of
`W3_NACA4412_RESOLUTION_SCATTER.md` and are not charged here.
