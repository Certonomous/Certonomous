# rhoCentralFoamBoundedDMRb — BUILD PROVENANCE (DMR R3 L5b CORRECTED)

Recorded 2026-09-08 by the cfd `lab-lane` per the chief-approved DMR-R3 **L5b**
bounded-T CORRECTED solver build, following `docs/OPENFOAM_SOLVER_BUILD.md` §4–§7
and the DRAFT prereg
`verification/campaign/DMR_R3_L5b_BOUNDED_T_CORRECTED_PREREGISTRATION_DRAFT.md`.

**This is a build record only. The prereg is NOT frozen and the graded L5b family
was NOT launched.** The cfd supervisor's §3 check-1 (solver diff read as a diff,
**AGAINST THE ACTUAL FIELD this time**) and check-4 (gate/lever/root/commit) are
OWED before any freeze or launch. Nothing is sent/filed/uploaded (rule 7).

## 0. WHY L5b — the L5 miscalibration this build corrects

L5 (`rhoCentralFoamBoundedDMR`) graded **NOT A RESULT**
(`DMR_R3_L5_BOUNDED_T_RESULTS.md`): its floor `eMin_bound = -532.410` was derived
from a HAND e-formula `e = Cv*(T-298.15)` (an ASSUMED `Tref=298.15`, `eref=0`),
predicting ambient `e(T=1.0) = -530.626`. But OpenFOAM's ACTUAL `hConst
sensibleInternalEnergy` assigns ambient `e ≈ -743.589 J/kg` (measured, byte-identical
across all three grids), so the `-532.410` floor sat **above the entire physical `e`
field** and clipped **100 % of cells from the first timestep** at every resolution,
corrupting the run. ROOT CAUSE: the floor was validated against an assumed reference,
not the solver's OWN initial `e` field.

**L5b fixes exactly that**, with two changes vs L5 and nothing else:
1. **Field-anchored derivation** (createFields.H): `eMin_bound = e_min_initial −
   Cv·(T_min_initial − TMin)` where `e_min_initial`/`T_min_initial` are the MEASURED
   global minima (`gMin`) of the initial `e`/`T` fields — NO assumed `Tref`/`eref`.
   `eMax_bound` anchored symmetrically on the measured maxima. The floor sits
   `Cv·(T_min_initial − TMin)` BELOW the coldest physical cell **by construction**.
2. **Mandatory t=0 zero-clip startup assertion** (createFields.H): on the physical
   initial field, count cells with `e < eMin_bound` (reduced across ranks); if `> 0`,
   `FatalError` + non-zero exit ("REFUSE: clip fires on N cell(s) at t=0 …"). A
   correctly-calibrated floor is inert at t=0; this assertion would have caught L5
   before a core-minute was spent (plant-the-zero, in the solver).

## 1. Build environment (measured on this box)

| Item | Value | How read |
|---|---|---|
| OpenFOAM | v2606, `openfoam2606-common` (dpkg) | `dpkg -S …/etc/bashrc` |
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` | `g++ --version` |
| Build target | `linux64GccDPInt32Opt` | `WM_OPTIONS` from `openfoam2606 -c` |
| `FOAM_APPBIN` (system, protected) | `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin` | env |
| `FOAM_USER_APPBIN` (build dest) | `/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin` | env |
| USER (daemon trap, §2 build-doc) | `ubuntu` — pinned so `WM_PROJECT_USER_DIR` resolves to `ubuntu-v2606`, not `user-v2606` | `export USER=ubuntu` |
| Build command | `openfoam2606 -c "cd <src> && wmake"` | — |
| Full build log | `build_provenance/wmake_build.log` (rc=0, no warnings/errors) | captured |

## 2. wmake target name — READ FROM the committed Make/files (not asserted)

`Make/files` line 1 (compilation unit): `rhoCentralFoamBoundedDMRb.C`
`Make/files` line 3: `EXE = $(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMRb`

A DISTINCT binary name in `FOAM_USER_APPBIN`. It does NOT overwrite stock
`rhoCentralFoam` (system `FOAM_APPBIN`), F4 `rhoCentralFoamBounded`, or the L5
`rhoCentralFoamBoundedDMR` (all confirmed untouched, §5).

## 3. Produced binary hashes (pin these at freeze — prereg §5)

| Field | Value |
|---|---|
| path | `$(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMRb` |
| bytes | 974800 |
| md5 | `9729eb8f61f0097ff0ec7a49a7bf5780` |
| sha256 | `5b40e616b9861a053721c492251a1e3005e6601cef88970a5380ea81714122d5` |

Functional smoke: `rhoCentralFoamBoundedDMRb -help` returns the usage banner.

## 4. Rebuild-verify (build-doc §5) — BIT-IDENTICAL

Rebuilt from tracked source ONLY (no carried-forward build products) under a
redirected `$HOME=<mktemp -d>` (and `USER=ubuntu`), so `FOAM_USER_APPBIN` resolved
into the scratch tree and nothing under `/home/ubuntu/OpenFOAM` was written:

- rebuild rc=0; `cmp` reported **BIT-IDENTICAL** to the installed binary.
- rebuilt md5 `9729eb8f61f0097ff0ec7a49a7bf5780` == installed md5.
- scratch tree removed after the compare. Log: `build_provenance/rebuild_verify.log`.

One measurement on one toolchain (g++ 13.3.0, `linux64GccDPInt32Opt`), not a
guarantee for any other — consistent with build-doc §6.

## 5. Protected binaries — confirmed UNTOUCHED (hash + mtime unchanged)

`diff protected_before.txt protected_after.txt` is EMPTY. Verbatim:

| Binary | md5 (before == after) | mtime unchanged |
|---|---|---|
| stock `rhoCentralFoam` (`FOAM_APPBIN`) | `5b1be2233a0902158ab2da88ac73e3ac` | 2026-06-19 13:46:16 |
| F4 `rhoCentralFoamBounded` (`FOAM_USER_APPBIN`) | `ee83ca590752bd34265d306faf3ad660` | 2026-07-30 01:06:50 |
| L5 `rhoCentralFoamBoundedDMR` (`FOAM_USER_APPBIN`) | `4159e374a8f70c5aaf9df60add94264b` | 2026-09-08 20:30:18 |

(F4 md5 matches `docs/OPENFOAM_SOLVER_BUILD.md` §6; L5 md5 matches the frozen L5
prereg §.)

## 6. Change set vs the L5 solver — EXACTLY three items (check-1 reads the diffs)

`diff -rq --exclude=linux64GccDPInt32Opt --exclude=build_provenance` between
`rhoCentralFoamBoundedDMR_src` (L5) and `rhoCentralFoamBoundedDMRb_src` (L5b),
saved at `build_provenance/diff_rq_vs_L5.txt`, reports EXACTLY:

1. **`createFields.H` differ** — the corrected field-anchored `eMin_bound`/`eMax_bound`
   derivation + the mandatory t=0 zero-clip startup assertion
   (`build_provenance/diff_createFields_vs_L5.txt`).
2. **`Make/files` differ** — `EXE` and source name renamed
   `rhoCentralFoamBoundedDMR` → `rhoCentralFoamBoundedDMRb`
   (`build_provenance/diff_Make_files_vs_L5.txt`).
3. **the `.C` renamed** — `rhoCentralFoamBoundedDMR.C` → `rhoCentralFoamBoundedDMRb.C`,
   CONTENT byte-identical to L5's `.C` (verified `cmp`, IDENTICAL).

**Everything else is byte-identical between L5 and L5b** (confirmed `cmp`):
`boundE.H` (the clip line `e = min(max(e, eMin_bound), eMax_bound)` and its BOUND
diagnostic — UNCHANGED from L5), `Make/options`, and the five stock headers
`centralCourantNo.H`, `createFieldRefs.H`, `directionInterpolate.H`,
`readFluxScheme.H`, `setRDeltaT.H` (md5s match build-doc §7 exactly).

Change set vs **stock v2606 `rhoCentralFoam`** (`diff_C_vs_stock.txt`,
`diff_createFields_vs_stock.txt`): exactly the two `#include "boundE.H"` lines in the
`.C` (identical to L5), the added `boundE.H`, the createFields.H derivation+assertion,
and `Make/files`/`Make/options` — and nothing else.

## 7. Derived clip bounds — VERIFIED against the ACTUAL R3 field (the proof)

A serial STARTUP-ASSERTION PROBE was run against the ACTUAL R3 (N=240, 960×240)
initial physical field (`blockMesh` + `setExprFields` + solver startup with `endTime`
forced to `3e-6` — this is a build-verification probe, **NOT** the graded family; it
ran in a scratch case, and the declared run root
`verification/runs/DMR_R3_L5b_BOUNDED_T_runs` was NEVER created). Evidence:
`build_provenance/t0_assertion_probe_R3.txt`. Verbatim:

```
Bounding e (DMR L5b positivity guard, FIELD-ANCHORED) to T floor 0.01 / ceiling 10000
  -> e in [-745.35714, 17111.794] J/kg
STARTUP ASSERT PASS: bounded-e clip fires on 0 cell(s) at t=0 (eMin_bound = -745.35714
  J/kg sits below field min e = -743.58928 J/kg); positivity floor is inert on the
  physical initial field.
```

- **`eMin_bound = -745.35714 J/kg`** (L5b), vs L5's miscalibrated `-532.410`.
- **`eMax_bound = 17111.794 J/kg`**.
- The anchor **field min `e = -743.58928 J/kg`** is BYTE-IDENTICAL to the "global
  worst e" the L5 run reported at its first step (`DMR_R3_L5_BOUNDED_T_RESULTS.md`) —
  confirming L5b reads OpenFOAM's ACTUAL hConst `e`, the very quantity L5's hand
  formula missed. `eMin_bound` now sits `Cv·(1.0 − 0.01) = 1.768 J/kg` BELOW it.
- **t=0 assertion PASSES: 0 cells clip** (L5 clipped 100 %). No BOUND fire in the
  first steps; rc=0; no FatalError. This is the proof the calibration is correct.

`R = 8314.47/11640.3 = 0.714283`; `Cv = 2.5 − R = 1.785717`; `γ = 1.40000`;
`TMin = 1e-2`, `TMax = 1e4` (from controlDict). NO assumed `Tref`/`eref` appears.
