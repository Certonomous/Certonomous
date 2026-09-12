# r2_fine attempt 1 — blockMesh rc=1 — TRIAGED, FALSIFIER CLASS 3a

**Verdict: NOT A RESULT.** Nothing was measured and nothing is quoted from this directory.
The build stopped at its first step, exactly as class 3a requires.

## What happened
`blockMesh` exited rc=1 with:

    --> FOAM FATAL IO ERROR: Cannot open include file ".../r2_fine/system/forceCoeffs"
        while reading dictionary "system/controlDict/functions"
        file: system/controlDict at line 33.

## Why — a real asymmetry in the graded R1 family, not a transient
`r1_fine/system/` was **mutated by R1 Stage A**: `controlDict`, `fvSchemes` and
`fvSolution` were replaced by SOLVER versions, and the mesh-build originals survive
beside them as `*.meshbuild`. `r1_coarse` and `r1_medium` were never solved and carry
only the mesh-build versions. Measured:

| file | r1_fine/`<f>.meshbuild` vs r1_coarse/`<f>` | r1_fine/`<f>` vs r1_coarse/`<f>` |
|---|---|---|
| controlDict | IDENTICAL | DIFFERS |
| fvSchemes | IDENTICAL | DIFFERS |
| fvSolution | IDENTICAL | DIFFERS |

So "`controlDict`" names two different files depending on the level, and r1_fine's
carries `#include "forceCoeffs"` — a solver function object, not a mesh-build input.

## The instrument defect this exposed, which is the more important half
The build wrapper asserted `cmp $SRC/system/$f $R/system/$f` **immediately after
copying `$SRC` → `$R`**. It compared the copy with its own source. **It could never
fail, at any level, for any file.** It read as a byte-identity guarantee and carried
no information whatsoever. That is the same defect class this campaign exists to hunt:
a check with no failing branch.

**REPAIR:** prefer `<f>.meshbuild` where it exists, and assert the **chosen** file is
byte-identical to **`r1_coarse/system/<f>`** — a comparison ACROSS levels, which CAN
fail, and which is what "the family differs only in `blockMeshDict`" actually claims.
`blockMeshDict` is excluded because it is per-level by design. A second limb refuses any
`system/` dict carrying an `#include`, since a mesh-build dict must be self-contained.

## What this does NOT change
No gate, threshold, band, label or cap. r2_coarse and r2_medium are unaffected: neither
source carries a `.meshbuild` variant and both sources' dicts are byte-identical to
r1_coarse's, which the repaired assertion re-verifies from scratch on the next build.
