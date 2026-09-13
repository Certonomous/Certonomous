# ⚠️ `log.yPlus` HERE IS THE DELIBERATE FAILING ARM OF A PAIRED CONTROL — NOT A RESULT, AND NOT AN ACCIDENT

**Read this before opening `log.yPlus`.** Unlike the three DrivAer probe directories, the zero in
*this* directory was **produced on purpose**. This whole directory is the **positive control** that
established the mechanism. Both files are kept; **neither may be deleted.**

| file | invocation | reading |
|---|---|---|
| `log.yPlus` | `postProcess -func yPlus -time 4000` — **the generic binary** | **1 of 1 patch all-zero**, OpenFOAM's own *"Unable to find turbulence model"* warning present |
| `log.yPlus2` | `rhoSimpleFoam -postProcess -func yPlus -time 4000` — **the valid spelling** | `patch wing y+ : min = 3.1146113, max = 44.370385, average = 18.416405` |
| `log.yPlus2.REDRIVEN_2026-09-13` | re-driven, same spelling | same |

**Those `log.yPlus2` figures are the ones quoted at
`verification/campaign/DRIVAER_SOLVED_YPLUS_2026-09-12.md:22`.** The zero beside them is quoted at
`:21` as *"THE CONTROL FAILED. THE METHOD IS BROKEN."*

**WHY THE PAIR MATTERS MORE THAN EITHER FILE.** A control needs a failing example **and** a passing
example (L-608). This directory is one of the few places in the repository where both exist side by
side on the same case, at the same time, on the same mesh — which is what makes the mechanism a
measurement rather than an inference. **The zero is the evidence. Do not read it as data, and do
not remove it.**

## Provenance
`L-603` — a functionObject that needs a constructed model and **degrades quietly** is the hazard;
one that **dies loudly** is safe. Mechanism at `src/functionObjects/field/yPlus/yPlus.C:172-184`.
Guard: `scripts/yplus_reader_guard.py`.

*Marker written 2026-09-13 by a cfd `lab-lane`. Nothing here leaves the box.*
