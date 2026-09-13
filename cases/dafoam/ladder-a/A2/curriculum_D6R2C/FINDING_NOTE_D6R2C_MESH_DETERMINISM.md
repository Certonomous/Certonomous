# FINDING NOTE — `D6R2C` — THE FAMILY MESH SEQUENCE IS BIT-FOR-BIT DETERMINISTIC ACROSS 47.7 DAYS

**Team:** dafoam. **Date:** 2026-09-13. **Status:** a MEASUREMENT, not a gate. **It grades nothing,
re-opens nothing and is not a verdict.** `FM11` remains `BLOCKED`, `FM10` `NOT A RESULT`, `O_mp`
`GATE FAIL`.

**Why it exists.** The measurement fell out of `FM11`'s refusal — `REFUSE_FRESH_IS_BASE` fired
because the `Zb` sub-arm's regenerated mesh was byte-identical to the base — and the identity is
worth recording on its own terms, because two of the owner's standing rules depend on it and
neither had evidence.

---

## 1. WHAT WAS MEASURED

`genWingMesh.py` (pyHyp hyperbolic extrusion) plus the family mesh sequence
— `genWingMesh.py` → `plot3dToFoam -noBlank volumeMesh.xyz` → `autoPatch 60 -overwrite`, in that
order, read from `FM11/Zb/mesh_generation.log` lines 2, 60 and 173 — was re-run on
**2026-09-13** around `surfaceMesh_base.cgns`, the same surface the base mesh was built from on
**2026-07-28**.

| quantity | base mesh (2026-07-28) | regenerated (2026-09-13) |
|---|---|---|
| `constant/polyMesh/points.gz` md5 | `0fb1935a9b8781b73ac4ccb136e3ec68` | **`0fb1935a9b8781b73ac4ccb136e3ec68`** |
| file size | 696,852 bytes | **696,852 bytes** |
| declared point count | 40,209 | **40,209** |
| mtime (UTC) | `2026-07-28 00:18:12` | `2026-09-13 17:33:34` |

**Point-by-point, parsed from both files and compared, not inferred from the hash:**
**max \|Δ\| = 0.0 m EXACTLY**, on all three components, with **40,209 of 40,209 points identical**.
Elapsed between the two: **47 days 17:15:22 (47.72 days)**.

`genWingMesh.py` itself is md5 `dab5e959187ab2e2bfb4e2c0ded0feb6`, the value both launchers pin as
`MD5_GENWINGMESH` and `G-FREEZE` asserts before every launch — so the script that ran on 09-13 is
provably the script the family froze.

---

## 2. THE md5 IDENTITY IS A TRUE STATEMENT ABOUT THE POINTS, NOT AN ARTEFACT OF THE CONTAINER

**This is the clause that makes the finding usable, and it is measured rather than assumed.** A
gzip member carries an `MTIME` field in header bytes 4–7; if OpenFOAM wrote a real timestamp there,
two identical point clouds written on different days would have **different** md5s and an md5
comparison would be useless — and, worse, a *matching* md5 would mean something other than matching
points.

Read from the two files' first ten header bytes, both `1f 8b 08 00 | 00 00 00 00 | 00 03`:
the `MTIME` field is **`0x00000000` = 0** in both. OpenFOAM zeroes it.

**So `points.gz` md5 equality is exactly equivalent to point-cloud equality here** — which is why
the independent point-by-point comparison above returns `0.0 m` and why `REFUSE_FRESH_IS_BASE`'s
md5 test is a sound test of the thing it claims to test.

---

## 3. AN INDEPENDENT SECOND CHANNEL AGREES

The hash and the point parse both read `points.gz`. A third, structurally different reading agrees:

- `O_mp`'s own arm log's **first** `checkMesh` block — on the base mesh, 2026-09-13 01:32Z run —
  prints `Mesh non-orthogonality Max: 66.96543422 average: 11.48508811`.
- `FM11/Zb/mesh_generation.log:453` — on the **regenerated** mesh — prints
  `Mesh non-orthogonality Max: 66.96543422 average: 11.48508811`.

Identical to all printed digits, through a code path that never touches an md5.

---

## 4. WHY IT MATTERS

The owner's standing rules 8 and 9 both **presuppose** a reproducible extrusion, and until now
nothing in this family had measured it:

> **8.** *"Periodic re-meshing with restart. Every N iterations, or whenever the surface
> displacement exceeds a registered fraction of the local first-cell height, regenerate the mesh
> from the current smooth surface…"*
>
> **9.** *"Fresh-mesh checkpoints of the objective. Every N iterations, evaluate the current design
> on a freshly generated mesh at matched lift. If deformed-mesh and fresh-mesh drag differ by more
> than the registered tolerance…"*

If the mesher were not deterministic, a fresh-mesh checkpoint's drag difference would carry an
unmeasured mesh-generation component and rule 9's tolerance would be uninterpretable; rule 8's
"regenerate and restart" would introduce a discontinuity nobody could separate from the design
change. **This note supplies the missing premise, at one design point.**

It also licenses the cheap form of the check: **for a re-mesh at an unchanged surface, `points.gz`
md5 equality is a sufficient test**, no point parse needed — provided §2's `MTIME = 0` clause is
re-checked whenever the OpenFOAM build changes.

---

## 5. WHAT THIS NOTE DOES NOT CLAIM

- It does **not** claim determinism at a *different* surface. One surface, one design point
  (shape ≡ twist ≡ 0), one build, one machine. **A single measurement, not a characterised
  property.**
- It does **not** claim the *solver* is deterministic. It is measured not to be, to about
  `3e-5` relative in `J` by path — `N-D48` in `docs/NUMERICS_KNOWLEDGE.md`. **This note is about
  the mesher and nothing else.**
- It does **not** claim `MTIME = 0` for any writer other than the OpenFOAM build these two files
  came from. It is read from these two files.
- It does **not** excuse `REFUSE_FRESH_IS_BASE` blocking `FM11`. The guard's *test* is sound; its
  *premise* was scoped to arms where "fresh" meant the optimum's mesh — recorded as a lesson in
  `docs/LESSONS.md`.

---

**Artifacts, all still on disk at the time of writing:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/base/constant/polyMesh/points.gz`;
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM11-a2-wing-matched-lift/FM11/Zb/constant/polyMesh/points.gz`;
`…/FM11/Zb/mesh_generation.log`; `…/FM11/Zb/genWingMesh.py`;
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp_20260913T013230Z_226722.log`;
`cases/dafoam/ladder-a/A2/curriculum_D6R2C/d6r2c_fm11_run_arm.sh:66` (`MD5_GENWINGMESH`).
