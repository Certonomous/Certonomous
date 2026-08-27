# FADR fixture provenance -- the INBOUND retrieval, recorded under PREREGISTRATION.md section 2

**INBOUND ONLY. Nothing of this lab left the box in this act.** No account, no login, no token,
no header carrying lab data, no issue, no comment, no upload. **SUBMISSIONS REMAIN PARKED**
(`CLAUDE.md` standing rule 7). This record is the retrieval's whole evidentiary content.

| field | value |
|---|---|
| **source URL** | `https://github.com/DAFoam/reg_test_files/archive/refs/heads/main.tar.gz` |
| **sha256** | `0154df31254d596d8bb36dff7d289e35e2791b9a1c6d4607164fbe0bb3937fa3` |
| **bytes** | 7772803 |
| **UTC, request issued** | 2026-08-27T18:51:18Z |
| **UTC, retrieval complete** | 2026-08-27T18:51:19Z |
| **stored at** | `/home/ubuntu/certonomous-runs/FADR-fixture/reg_test_files-main.tar.gz` (outside git: binary) |
| **retrieved by** | dafoam lane C, `fadr_fetch_fixture.sh` |
| **certificate checking** | ENABLED. Upstream's own `tests/Allrun:13` passes `--no-check-certificate`; this retrieval does NOT, because a retrieval needing certificate checking disabled is one whose provenance cannot be stated. |

## CONTENT VERIFICATION -- the archive was OPENED, and this is what was SEEN

**Standing rule 15: never by filename, never by file type, never by hash alone. The sha256 above is
PROVENANCE, NOT IDENTIFICATION.**

- The archive extracts as gzip+tar and holds **1154 entries** under a single top-level
  directory `reg_test_files-main`.
- It holds **26 case directories**: ChannelConjugateHeat ChannelConjugateHeatV4 ChannelTopoCHT CompressorFluid ConvergentChannel CurvedCubeHexMesh CurvedCubeSnappyHexMesh DamBreak NACA0012 NACA0012BetaSA NACA0012DynamicMesh NACA0012DynamicMeshV4 NACA0012FieldInversion NACA0012Unsteady NACA0012UnsteadyComp NACA0012UnsteadyV4 NACA0012V4 PeriodicHill PlateHole PlateHoleV4 Ramp UBendDuct Wing WingProp flange pitzDailyScalarTransport 
- **`ConvergentChannel` IS PRESENT** -- the case
  `runRegTests_DASimpleFoamForward.py` chdirs into
  (`os.chdir("./reg_test_files-main/ConvergentChannel")`).
- Every path the test script reaches for exists inside it, checked by EXISTENCE:
  `0/`, `0.incompressible/`, `system/`, `system.incompressible/`,
  `constant/turbulenceProperties.sa`, `FFD/FFD.xyz`.
- **Read INSIDE the files, not at them:** `ConvergentChannel/system/controlDict` carries the
  OpenFOAM banner and its class/object line reads ` class dictionary;`. `ConvergentChannel/FFD/FFD.xyz`
  opens with `1` then `3 3 3 ` -- a PLOT3D FFD block, which is what
  `OM_DVGEOCOMP(file="FFD/FFD.xyz", type="ffd")` requires.
- First entries of the archive listing, as read:

```
reg_test_files-main/
reg_test_files-main/.gitignore
reg_test_files-main/ChannelConjugateHeat/
reg_test_files-main/ChannelConjugateHeat/aero/
reg_test_files-main/ChannelConjugateHeat/aero/0/
reg_test_files-main/ChannelConjugateHeat/aero/0/T
reg_test_files-main/ChannelConjugateHeat/aero/0/U
reg_test_files-main/ChannelConjugateHeat/aero/0/alphat
reg_test_files-main/ChannelConjugateHeat/aero/0/nuTilda
reg_test_files-main/ChannelConjugateHeat/aero/0/nut
reg_test_files-main/ChannelConjugateHeat/aero/0/p
reg_test_files-main/ChannelConjugateHeat/aero/FFD/
reg_test_files-main/ChannelConjugateHeat/aero/FFD/channelFFD.xyz
reg_test_files-main/ChannelConjugateHeat/aero/FFD/genFFD.py
reg_test_files-main/ChannelConjugateHeat/aero/constant/
reg_test_files-main/ChannelConjugateHeat/aero/constant/polyMesh/
reg_test_files-main/ChannelConjugateHeat/aero/constant/polyMesh/boundary
reg_test_files-main/ChannelConjugateHeat/aero/constant/polyMesh/faces.gz
reg_test_files-main/ChannelConjugateHeat/aero/constant/polyMesh/neighbour.gz
reg_test_files-main/ChannelConjugateHeat/aero/constant/polyMesh/owner.gz
reg_test_files-main/ChannelConjugateHeat/aero/constant/polyMesh/points.gz
reg_test_files-main/ChannelConjugateHeat/aero/constant/thermophysicalProperties
reg_test_files-main/ChannelConjugateHeat/aero/constant/turbulenceProperties
reg_test_files-main/ChannelConjugateHeat/aero/paraview.foam
reg_test_files-main/ChannelConjugateHeat/aero/system/
```

## WHAT THIS RECORD DOES NOT ESTABLISH

It does not establish that the fixture is unchanged from the one upstream's stored reference values
were produced against -- upstream publishes a moving `main` branch, not a tag, and the digest above
therefore pins **what this box received at 2026-08-27T18:51:19Z**, nothing earlier. If the regression fails,
**fixture drift is a candidate explanation and is named here before the run**, not after it.

## THE DIGEST IS A GATE, NOT A NOTE

`fadr_chain_driver.sh` recomputes the sha256 at launch and **refuses (exit 2)** if it is not
`0154df31254d596d8bb36dff7d289e35e2791b9a1c6d4607164fbe0bb3937fa3`.
