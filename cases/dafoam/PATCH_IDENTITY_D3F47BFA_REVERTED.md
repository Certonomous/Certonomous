# ✅ RESOLVED — `d3f47bfa` IS **REVERTED FORWARD**. `empty` BOUNDING PLANES ARE **CATEGORICALLY UNUSABLE** WITH DAFoam ON THIS CASE FAMILY.

**The A1 2-D templates carry `type symmetry` on `symmetry1`/`symmetry2`, and that is CORRECT.
Do not change it to `empty`. DAFoam refuses the result.**

Supersedes `PATCH_IDENTITY_D3F47BFA_UNVERIFIED.md`, which described the same commit while its
verification was still pending. **Nothing here is filed upstream — `NOT FILED`, rule 7.**

---

## THE MEASUREMENT

`A1ZE` ran through the queue daemon on 2026-09-03 (run root
`/home/ubuntu/certonomous-runs/A1ZE`, stamp `20260903T190524Z`), one variable, two coarse arms
built from the same sources in the same invocation:

| arm | bounding planes | result |
|---|---|---|
| **`Sc`** control | `symmetry` | **`rc=0`**, 206 s, 3.4333 core-min, **completed its full 2,000 iterations**. `Mesh has 3 solution (non-empty) directions (1 1 1)`; `U2` present, floor `6.656746e-08` |
| **`Ec`** treatment | `empty` | **`rc=97`** (in-container `rc=134`, **SIGABRT, core dumped**), 88 s, 1.4667 core-min, **zero time steps completed** |

**The patch did exactly what it intended at the topology level** — the staging guard read
`planes='empty' mesh=2/2 fields_checked=7 of 7 bad=0`, and the solver itself printed
`Mesh has 2 solution (non-empty) directions (1 1 0)`. **Then it aborted three lines later:**

> `--> FOAM FATAL ERROR: (openfoam-2506)`
> `Mesh geometric directions is less than 3 and not supported!`
> `From Foam::checkGeometry(...) in file DACheckMesh/DACheckGeometry.C at line 278.`

## THE CAUSE, WITH A HASH

Read read-only from the image A1ZE registers and its `G-IMG` asserts —
`dafoam-idwarp-rot:v1`, `sha256:2927768a16ac…` —
`/home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DACheckMesh/DACheckGeometry.C`
(also reachable at `.../adjoint/lnInclude/DACheckGeometry.C`; **both resolve to md5
`e6b9497656105a2cf6958e5a6d329823`**):

```cpp
if (mesh.nGeometricD() < 3)
{
    FatalErrorInFunction
        << "Mesh geometric directions is less than 3 and not supported!"
        << abort(FatalError);
}
```

**This is a DAFoam file — `DA` prefix, DAFoam's own repo tree, compiled into `libDASolver.so` — not
vanilla OpenFOAM. DAFoam refuses any mesh with fewer than three geometric directions,
unconditionally, by design. An `empty` bounding plane gives two.**

**So `symmetry` on these planes is not an oversight inherited from an upstream tutorial. It is the
only thing that runs.** Upstream's own comment at `DAUtility.C:775-780` — *"we often need to run 2D
simulations with symmetry BC, so one component of the residual vector … may be high"* — was
recorded in A1ZE's Addendum B **before this run** and now reads as exactly what it says: DAFoam
expects 2-D meshes with `symmetry` BCs and built its residual criterion to tolerate the high
z-component that requirement forces.

## ⚠ WHAT THE REVERT DOES **NOT** REST ON

**The frozen grader's verdict is `A1ZE_VERDICT NOT A RESULT` and it stands untouched.**

**A1ZE's registered condemnation clause DID NOT FIRE.** Its §3b registers that a `GATE FAIL` on
`G-DIRN.E` or `G-U2.E` condemns this sha. Neither fired and neither could have: **`G-DIRN.E`
anticipated *"the change did not take effect"* (`N` still 3), and what happened is the opposite and
worse — the change took effect perfectly, `N = 2`, and the toolchain then refused the result.**
`G-U2.E` was never reached, because the strict completion rule failed first. `G-EMPTY` on `Ec`
**passed**; the `BLOCKED` rows belong to `S3`/`E3`, which never staged.

**A hand-composed verdict is a defect whichever way it leans, so none is composed.** The revert
rests on a separate, measured engineering fact: **the three A1 2-D templates at HEAD could not run
at all.** That is a broken artefact in the tree, not a graded verdict, and repairing it is ordinary
maintenance — the blocking-physics-fix class of Sanaa's 2026-09-03 ~20:00Z ruling, running in the
opposite direction from the one that motivated `d3f47bfa`.

## THE REVERT

**Forward-only, a new commit, no history rewritten.** All **41** files `d3f47bfa` touched are
restored to their `d3f47bfa^` content and nothing else is modified. Verified by execution:

- the committed file set **diffed against `git show --name-only d3f47bfa` and EQUAL**, 41 paths;
- every restored file **md5-equals its `d3f47bfa^` blob — 0 mismatches of 41**;
- `createPatchDict` returns to **`5e89709961881491e3f05dc97bbcf75c`** on all three templates
  (from `b06b32856f75d4813a763af819b6149c`);
- `type symmetry` counts restored **22 / 30 / 30**; `type empty` on those two patches now **0/0/0**;
- **no file diverged between `d3f47bfa` and HEAD beforehand** (three-way: `d3f47bfa` blob == HEAD
  blob == disk, all 41), so the revert clobbers no later work.

## COST

**4.9 core-min of a 532.0 core-min ceiling, $0.0042 DERIVED** at the owner-stated $0.0513/core-h and
**not measured** — this box cannot read its own billing. A1ZE's coarse-pair-first ordering is why a
defect that would have cost ~512 core-min on the L3 pair surfaced for **4.9**.

## WHAT REMAINS OPEN

**Whether the redundant z-momentum equation contaminates the published `CL`/`CD` is now
UNANSWERABLE by this route** — there is no `empty` solve to compare against, because DAFoam will not
produce one. A1ZE §1b's coefficient question is **`BLOCKED` by the toolchain**, not unmeasured by
choice.

**SUBMISSIONS PARKED. Nothing sent, filed, uploaded, registered or posted outside this box.**
