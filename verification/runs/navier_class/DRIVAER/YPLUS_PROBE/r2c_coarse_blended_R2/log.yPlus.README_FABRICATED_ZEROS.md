# 🔴 `log.yPlus` IN THIS DIRECTORY IS FABRICATED. DO NOT READ ITS NUMBERS.

**Read this before opening `log.yPlus`.** This file is a marker, not a result. It is placed
beside the log deliberately and **must not be deleted**: the log is *evidence of a defect* and
destroying it would destroy the proof.

## What `log.yPlus` is

```
Exec : postProcess -func yPlus -time 2000
```

That is the **generic `postProcess` binary**, which **constructs neither a turbulence model nor a
thermo**. `yPlus` therefore takes an explicit `else` branch
(`src/functionObjects/field/yPlus/yPlus.C:172-184`): it prints
*"Unable to find turbulence model in the database: yPlus will not be calculated"*, prints the
remedy itself, and **returns false without computing the field**. `write()` then emits the
**construction zeros** of a field that was allocated and never filled.

**The warning is IN THIS LOG.** Its `52 of 52` all-zero patch readings are **structurally fabricated** —
not a measurement of a small y+, not a converged result, and not evidence about this mesh.

**`rc = 0` and an `End` line are both present.** A run can satisfy every clause of the strict
completion rule and still carry a wholly fabricated field. **Completion says the run finished; it
says nothing about whether a reader inside it could see.**

## What to read instead

```
Exec : simpleFoam -postProcess -func yPlus -time 2000      <-- log.yPlus2, THE VALID SPELLING
```

Representative reading from the valid arm: `patch top y+ : min = 26339.90331, max = 33321.56898, average = 30236.06347`. **0 of 52 patches are all-zero there.**

**The only valid spelling is `<app> -postProcess -func yPlus`.** The generic form is never
correct for a wall-function case, at any time, on any mesh.

## Provenance

**`L-603`** in `docs/LESSONS.md` — *a functionObject that needs a constructed model and degrades
QUIETLY is the hazard; one that dies LOUDLY is safe.* Compare `forces`, which **fatals** on the
same missing model (`forces.C:262-265`). Same absent object, two branches, opposite danger.
Mechanism also stated at `verification/campaign/DRIVAER_SOLVED_YPLUS_2026-09-12.md:24`, whose
table at `:21-22` had already rejected the generic form as a failed control.
Guard: `scripts/yplus_reader_guard.py` refuses an identically-zero y+ reading.

*Marker written 2026-09-13 by a cfd `lab-lane`. Nothing here leaves the box.*
