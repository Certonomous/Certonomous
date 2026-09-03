# ⚠ THE BOUNDING PLANES ARE `type symmetry` AND THAT IS **CORRECT**. DO NOT CHANGE THEM TO `empty`.

`symmetry1` and `symmetry2` were changed to `type empty;` by commit
**`d3f47bfa50944c466ff0bad019b36a7b048a0fae`** (2026-09-03) and that commit is **REVERTED FORWARD**,
because it was **measured to break this case family**.

**`A1ZE` ran it:** the `empty` arm **SIGABRTed with zero time steps completed**, after printing
`Mesh has 2 solution (non-empty) directions (1 1 0)`. The cause, read from the registered image
`dafoam-idwarp-rot:v1` (`sha256:2927768a16ac…`) with a hash —
`DACheckGeometry.C`, md5 `e6b9497656105a2cf6958e5a6d329823`, lines 276-281:

```cpp
if (mesh.nGeometricD() < 3)
{
    FatalErrorInFunction
        << "Mesh geometric directions is less than 3 and not supported!"
        << abort(FatalError);
}
```

**DAFoam refuses any mesh with fewer than three geometric directions, by design. `empty` gives two.
`symmetry` is the only thing that runs.** The matching `symmetry` control arm completed `rc=0`.

`createPatchDict` md5 is back to `5e89709961881491e3f05dc97bbcf75c`.

**A1ZE's own verdict was `NOT A RESULT` and its registered condemnation clause did not fire** — the
revert rests on the template being unrunnable, not on a gate reading. Full record:
**`cases/dafoam/PATCH_IDENTITY_D3F47BFA_REVERTED.md`**

**NOT FILED. SUBMISSIONS PARKED.**
