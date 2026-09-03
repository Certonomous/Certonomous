# ⚠ THIS TEMPLATE'S BOUNDING PLANES WERE CHANGED `symmetry` → `empty`, AND THAT CHANGE IS NOT YET VERIFIED

`symmetry1` and `symmetry2` in `system/createPatchDict` and in every `0/` and `0.orig/` field
file were changed from `type symmetry;` to `type empty;` by commit
**`d3f47bfa50944c466ff0bad019b36a7b048a0fae`** (2026-09-03), which was landed **UNVERIFIED on
purpose** and says so in its own message.

`createPatchDict` md5 `5e89709961881491e3f05dc97bbcf75c` (before) →
`b06b32856f75d4813a763af819b6149c` (after).

**Do not treat a case built from this template as verified on patch identity until `A1ZE`
returns.** A `GATE FAIL` on `A1ZE`'s `G-DIRN.E` or `G-U2.E`, or a `G-EMPTY` `BLOCKED` on either
treatment arm, **condemns `d3f47bfa` and it is reverted forward**.

Full note, including exactly what a `GATE FAIL` does and does **not** condemn the commit for:
**`cases/dafoam/PATCH_IDENTITY_D3F47BFA_UNVERIFIED.md`**

Verification item: `cases/dafoam/ladder-a/A1/z_direction_empty_control/A1ZE_PREREGISTRATION.md`
(frozen 2026-09-03, not launched, not queued).

**SUBMISSIONS PARKED.**
