# SUPERSEDED — `d3f47bfa` IS NO LONGER UNVERIFIED. IT WAS **MEASURED TO BREAK THE CASE FAMILY** AND IS **REVERTED FORWARD**.

**Read `cases/dafoam/PATCH_IDENTITY_D3F47BFA_REVERTED.md` instead.**

This file described the commit while its verification was pending. `A1ZE` has since run: the
`empty` treatment arm **SIGABRTed with zero time steps**, because **DAFoam hard-aborts on any mesh
with fewer than three geometric directions** — `DACheckGeometry.C:276-281`, md5
`e6b9497656105a2cf6958e5a6d329823`, in image `dafoam-idwarp-rot:v1` `sha256:2927768a16ac…`. An
`empty` bounding plane gives two. **`type symmetry` on these planes is correct and is restored.**

**Note what the successor is careful about:** A1ZE's frozen grader returned **`NOT A RESULT`** and
its registered condemnation clause **did not fire** — the revert rests on the templates being
unrunnable, not on a gate reading.

**NOT FILED. SUBMISSIONS PARKED.**
