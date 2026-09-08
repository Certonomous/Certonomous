# rhoCentralFoamBoundedDMR — BUILD PROVENANCE

Recorded 2026-09-08 by the cfd `lab-lane` per the chief-approved DMR-R3 L5
bounded-T solver build, following `docs/OPENFOAM_SOLVER_BUILD.md` §4–§7 and the
frozen-ready DRAFT prereg
`verification/campaign/DMR_R3_L5_BOUNDED_T_PREREGISTRATION_DRAFT.md` §5.

**This is a build record only. The prereg is NOT frozen and no solve was launched.**
The cfd supervisor's §3 check-1 (solver diff, read as a diff) and check-4
(gate/lever/root/commit) are OWED before any freeze or launch.

## 1. Build environment (measured on this box)

| Item | Value | How read |
|---|---|---|
| OpenFOAM | v2606, `openfoam2606-common` (dpkg) | `dpkg -S …/etc/bashrc` |
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` | `g++ --version` |
| Build target | `linux64GccDPInt32Opt` | `WM_OPTIONS` from `openfoam2606 -c` |
| `FOAM_APPBIN` (system) | `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin` | env |
| `FOAM_USER_APPBIN` (build dest) | `/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin` | env |
| Build command | `openfoam2606 -c "cd <src> && wmake"` | — |
| Full build log | `build_provenance/wmake_build.log` (rc=0, no warnings/errors) | captured |

## 2. wmake target name — READ FROM the committed Make/files (not asserted)

`Make/files` line 1 (compilation unit): `rhoCentralFoamBoundedDMR.C`
`Make/files` line 3: `EXE = $(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMR`

A DISTINCT binary name and a DISTINCT install dir (`FOAM_USER_APPBIN`, not the
system `FOAM_APPBIN`). It does not overwrite the stock `rhoCentralFoam` (system
`FOAM_APPBIN`) nor the F4 `rhoCentralFoamBounded` (`FOAM_USER_APPBIN`).

## 3. Produced binary hashes (pin these at freeze — prereg §5 item 4)

| Field | Value |
|---|---|
| path | `$(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMR` |
| bytes | 970576 |
| md5 | `4159e374a8f70c5aaf9df60add94264b` |
| sha256 | `b6995cf6c5b1bf6fc0b1dce6b0efca6cf9c30636e0b666aec629864ccf6ba8e1` |

Functional smoke: `rhoCentralFoamBoundedDMR -help` returns the usage banner.

## 4. Rebuild-verify (prereg §5 item 5; build-doc §5) — BIT-IDENTICAL

Rebuilt from tracked source ONLY (no carried-forward build products) under a
redirected `$HOME=<mktemp -d>`, so `FOAM_USER_APPBIN` resolved into the scratch
tree and nothing under `/home/ubuntu/OpenFOAM` was written. Result:

- rebuild rc=0; `cmp` reported **BIT-IDENTICAL** to the installed binary.
- rebuilt md5 `4159e374a8f70c5aaf9df60add94264b` == installed md5.
- rebuilt sha256 `b6995cf6c5b1bf6fc0b1dce6b0efca6cf9c30636e0b666aec629864ccf6ba8e1` == installed sha256.
- The scratch tree was removed after the compare.

On this box, with this toolchain, rebuildable-from-tracked-source == bit-identical
(consistent with build-doc §6). This is one measurement on one toolchain, not a
guarantee for any other g++/target.

## 5. Protected binaries — confirmed UNTOUCHED (hash + mtime unchanged)

| Binary | md5 (before == after) | mtime unchanged |
|---|---|---|
| stock `rhoCentralFoam` (`FOAM_APPBIN`) | `5b1be2233a0902158ab2da88ac73e3ac` | 2026-06-19 13:46:16 |
| F4 `rhoCentralFoamBounded` (`FOAM_USER_APPBIN`) | `ee83ca590752bd34265d306faf3ad660` | 2026-07-30 01:06:50 |

(The F4 md5 matches `docs/OPENFOAM_SOLVER_BUILD.md` §6.)

## 6. Change set vs stock v2606 rhoCentralFoam (check-1 reads the diff files)

`diff -rq` and the content diffs are saved beside this file:
- `diff_rq_vs_stock.txt` — the whole-tree overview
- `diff_C_vs_stock.txt` — the `.C`: EXACTLY two added `#include "boundE.H"` lines
- `diff_createFields_vs_stock.txt` — the DMR eMin/eMax derivation block
- `diff_Make_vs_stock.txt` — `Make/files` (source name + EXE) and `Make/options` (BCs `-I`)

The substantive solver change set is exactly the four items of prereg §2.2 / §5.1:
1. added `boundE.H` (element-wise clip `e = min(max(e, eMin_bound), eMax_bound)`
   + parallel-reduced firing diagnostic);
2. `createFields.H` addition deriving `eMin_bound`/`eMax_bound` from the DMR
   constants (`Cv = 2.5 − 8314.47/11640.3 = 1.785717`, `Tref = 298.15`,
   `TMin`/`TMax` from `controlDict`, defaults `1e-3`/`1e4`);
3. two `#include "boundE.H"` lines in the time loop (after
   `e.correctBoundaryConditions();` before the first `thermo.correct();`, and
   before the second `thermo.correct();` in the inviscid-only `if(!inviscid)`
   branch — never fired by the inviscid DMR case);
4. `Make/files` `EXE` renamed to `$(FOAM_USER_APPBIN)/rhoCentralFoamBoundedDMR`.

Build-infrastructure diffs (identical in kind to the proven, published F4 solver):
- the `.C` file is renamed `rhoCentralFoam.C` → `rhoCentralFoamBoundedDMR.C` (the
  named target); its CONTENT differs from stock by exactly the two include lines;
- `Make/options` uses an absolute `-I` into the installed
  `rhoCentralFoam/BCs/lnInclude` and links `-lrhoCentralFoam` (the F4 pattern; the
  BCs headers/symbols come from the installation, so `BCs/`, `Allwmake`,
  `Allwclean` are not copied and show as "Only in stock");
- the five stock headers (`centralCourantNo.H`, `createFieldRefs.H`,
  `directionInterpolate.H`, `readFluxScheme.H`, `setRDeltaT.H`) are byte-identical
  to stock (md5 verified).

## 7. Derived clip bounds (checkable; match prereg §2.3)

`R = 8314.47/11640.3 = 0.714283`; `Cv = 2.5 − R = 1.785717`; `γ = 1.40000`;
`Tref = 298.15`; `TMin = 1e-3`, `TMax = 1e4`.
`eMin_bound = Cv·(TMin − Tref) = −532.4097 J/kg`;
`eMax_bound = Cv·(TMax − Tref) = 17324.757 J/kg`;
ambient `e = Cv·(1.0 − Tref) = −530.626 J/kg`; ambient `T = 1.000` (nondim).
`eMin_bound` sits just below ambient `e` and far below every post-shock `e`, so the
low clip touches only sub-ambient-by-orders-of-magnitude (nonphysical) excursions.
