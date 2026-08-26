# VMFL076-R2 — Forced Convection Over a Flat Plate — PRE-REGISTRATION

**Re-registration of VMFL076** (VM2026R1 p.219) under `ANSYS_VERIFICATION_CHARTER` §6: a
**NEW register row that cites row #27 and never overwrites it**. Row #27 stands as
`NOT A RESULT` whatever this row returns.

Frozen by sha **before any R2 solver starts** (CLAUDE.md rule 2). Drafted by
`ansys-lane-opus`, **2026-08-26**. This file is a frozen file under rule 6.

**NOT YET RUN.** `verification/runs/ansys_verification/VMFL076-R2/` **does not exist** at
**2026-08-26T22:45:32Z** — `test -e` on that exact path returns false. No R2 solver has
started, no level directory exists, no `RUN_RC.txt`, no `LAUNCH_RECORD.txt`. The attempt-1
run root `verification/runs/ansys_verification/VMFL076/` is **not touched by this
registration**.

---

## THE COMPARATOR IS THE SAME FILE — NOT "EQUIVALENT", THE SAME BYTES

`cases/ansys_verification/VMFL076-R2/grade_vmfl076.py` is **byte-identical** to
`cases/ansys_verification/VMFL076/grade_vmfl076.py`: both are git blob
**`42c8945544721e60a41fbe1a01513405b64d5f3c`**. Same name, same content, same blob. There
is therefore **no gate-section diff to publish, because there is no diff at all** — the
gate scalars, both bands, the tier ceiling, the reference evaluation, the Roache
classifier, the ten controls and the verdict path are not merely carried but are literally
the same object.

```
git hash-object cases/ansys_verification/VMFL076-R2/grade_vmfl076.py
git rev-parse HEAD:cases/ansys_verification/VMFL076/grade_vmfl076.py
# both print 42c8945544721e60a41fbe1a01513405b64d5f3c
```

**This is possible because the R1 comparator hard-codes no mesh.** It takes its levels and
their `endTime`s from `argv` (`grade_vmfl076.py <runroot> L1:endTime L2:endTime
L3:endTime`), so a different grid family needs **no comparator change whatsoever**. The
one thing this R2 alters lives entirely in the launcher's mesh table.

---

## THE ONE CHANGE, AND ROW #27 NAMED IT

Register row #27's `RESULTS.md` §2 diagnosed the R1 triple, on the R1's own numbers:

```
e21 = I(L2) - I(L1) = -5.007461e-05
e32 = I(L3) - I(L2) = +3.511790e-06
R   = e32/e21       = -0.070131      ->  OSCILLATORY
```

*"The grid family was refined past its own asymptotic range, so no order can be extracted
from it. A useful triple for this case would be COARSER, not finer."* And §7 names the
repair by name: *"**Would:** a COARSER triple that sits inside the asymptotic range — e.g.
40×15, 80×30, 160×60, with L1 of this run as its finest level. That is a NEW
pre-registration with its own freeze, not an amendment to this one."*

**That is exactly this registration, and nothing else.**

| | R1 (row #27) | R2 (this) |
|---|---|---|
| L1 | 160 × 60 = 9 600 cells, `endTime` 2000 | **40 × 15 = 600 cells**, `endTime` 2000 |
| L2 | 320 × 120 = 38 400, `endTime` 3000 | **80 × 30 = 2 400**, `endTime` 2000 |
| L3 | 640 × 240 = 153 600, `endTime` 5000 | **160 × 60 = 9 600**, `endTime` 2000 — **byte-identical to R1's L1** |
| refinement ratio r | 2 | **2, unchanged** |
| comparator | blob `42c89455` | **the same blob `42c89455`** |
| gate scalars, both bands, ceiling, reference, controls, verdict path | — | **the same file** |
| `writeInterval` / `sampleInterval` | 250 / 50 at L1 | **250 / 50 at every level** — carried character for character from the R1 L1 row |
| per-level cap | 10 / 30 / 150 | **10 at every level** — carried character for character from the R1 L1 row |
| launcher `USER` | inherited | **pinned before the OpenFOAM bashrc, and recorded** (L-343) |
| case inputs (nine files) | — | **byte-identical, checked** |

### `endTime = 2000` at every level, justified WITHOUT reading any R1 answer

The R1 freeze **registered** 2000 iterations as sufficient for the 160 × 60 mesh, before
any compute. At a fixed relaxation a **coarser** mesh requires **no more** iterations than
a finer one, so 2000 is an **upper bound** for 80 × 30 and 40 × 15. Holding it constant
across the triple also removes a confound the R1 carried — its three levels ran to three
different `endTime`s — and keeps *"last time == `endTime`"* literally testable at every
level. **No R1 residual, gate value or triple entered this choice**; the R1's registered
number did, and a registration made before its own compute is not an answer.

### What is NOT changed, and why that is the whole point

The gate scalars, both bands (**GATE A** `|I_lab − I_ref|/I_ref ≤ 3.00e-02`, **GATE B**
`max|ΔΘ| ≤ 1.00e-02`, **both** required at the finest level), the tier ceiling
**`GATE REACHED`**, the Sparrow & Gregg similarity reference evaluated by the lab, the
sample line (x = 0.75 m, 201 fixed points), the slug-shortcut control and its registered
4.954869 % gap, and the rule-5 triple gating are **the same bytes**. **The R1 run's answers
are on disk**, so any change to any of them would be gate-fitting and is refused (rule 2).

---

## THE TEN-LINE FORM (deltas from the R1 freeze only; everything unlisted is carried)

```
 1. CASE            : VMFL076-R2 -- Forced convection over a flat plate, VM2026R1 p.219,
                      title-page verified. simpleFoam + scalarTransport, steady laminar
                      incompressible, Re_L = 9.0e4, Pr = 3.00e-03, Pe_L = 270, planar 2-D.
                      NOT YET RUN; verification/runs/ansys_verification/VMFL076-R2/ absent
                      at 2026-08-26T22:45:32Z.
 2.-- 7. REFERENCE, REFERENCE KIND, TIER CEILING, QUANTITIES, BANDS, LADDER: CARRIED
                      BYTE-IDENTICAL -- they are literally the same comparator file, blob
                      42c8945544721e60a41fbe1a01513405b64d5f3c.
 8. DECOMPOSITION  : r = 2 triple 40x15 / 80x30 / 160x60 = 600 / 2 400 / 9 600 cells,
    SEED             endTime 2000 at every level, writeInterval 250, sampleInterval 50.
                     SERIAL, RANKS = 1, no decomposition and no RNG. THE FINEST LEVEL IS
                     BYTE-IDENTICAL TO ATTEMPT 1's COARSEST.
 9. PRINCIPAL RISK : the coarser triple lands OUTSIDE the asymptotic range in the OTHER
                     direction -- at 600 cells the leading-edge cell is 25 mm and the
                     gate line at x = 0.75 m sits about 30 cells downstream, so L1 may be
                     too coarse for the boundary layer to be resolved at all. Then the
                     triple is again non-CONVERGING and the verdict is again NOT A RESULT.
                     THIS IS REGISTERED AS A REAL AND UNRESOLVED RISK: this registration
                     does NOT claim to know that 40x15 / 80x30 / 160x60 is inside the
                     asymptotic range. It claims only that the R1 family was measured to
                     be OUTSIDE it on the fine side, and that row #27 named this family as
                     the repair to try. A second non-CONVERGING triple would be a finding
                     about the case, not about this instrument.
10. EXPECTED ORDER : p_f ~ 2 formal. p_obs in [1.0, 2.4]; p_obs > 2.4 SUSPICIOUSLY HIGH,
                     carried character for character from the R1 freeze (the R1's
                     magnitude-only fit read 3.834, above that threshold, which the R1
                     freeze had declared suspicious BEFORE compute).
11. WEDGE/GEOM BIAS: N/A (planar 2-D Cartesian).
12. COST + CAP     : ESTIMATE 0.6 core-min TOTAL, and the basis is a MEASUREMENT: the R1's
                     L1 -- the SAME 160x60 mesh at the SAME endTime 2000 -- ran in 0.4500
                     core-min MEASURED (register row #27, RUN_RC.txt, ranks 1). That is
                     this R2's L3 exactly. The two coarser levels are priced from the R1's
                     own measured L1-mesh rate of 1.41e-06 s per cell per iteration, which
                     the R1 calibration measured to be ACCURATE ON SMALL MESHES (1.071x at
                     L1) and to UNDER-predict only as the mesh grows (2.67x at 16x the
                     cells) -- and both new levels are SMALLER than the mesh it was
                     calibrated on, so the known failure direction of that rate does not
                     apply here:
                        L1  600 cells x 2000 it x 1.41e-06 s = 1.7 s -> 0.028 core-min
                        L2  2 400      x 2000    x 1.41e-06  = 6.8 s -> 0.113 core-min
                        L3  9 600      x 2000                = 0.4500 core-min MEASURED
                        total 0.59 -> ESTIMATE 0.6 core-min.
                     CAPS: 10 core-min PER LEVEL (never a shared drawdown), carried
                     character for character from the R1 L1 row and deliberately NOT
                     tightened to the estimate -- a cap is a runaway guard, and tightening
                     it from a prediction converts it into one. Family ceiling 30 core-min.
                     An overrun STOPS the level and does NOT get a new budget (rule 12);
                     endTime is NEVER reduced to fit a cap. Rate $0.0513/core-h
                     (c7a.4xlarge) is REPORTED-BY-OWNER, NOT MEASURED -- the box cannot
                     read its own billing (COMPUTE_BUDGET_CHARTER sec.5); dollars are
                     DERIVED ($0.00051 at 0.6 core-min).
13. CONTROLS       : the comparator's own TEN controls, unchanged because it is the same
                     file: --selftest GREEN 10/10, exit 0. Plus the launcher freeze check
                     of prereg and comparator against HEAD, the nine case-input blob
                     checks, the level guard (driven: an unknown level exits rc 1), and
                     the L-343 USER pin recorded in LAUNCH_RECORD.txt.
```

**REGISTERED IN ADVANCE, so it is not a departure:** after this freeze a **launcher smoke**
is run — `run_vmfl076_r2.sh smoke L1`, the launcher's own `smoke` mode, which the R1
launcher already carries and which stages into a scratch directory rather than the graded
run root. It exercises the launcher end to end — the freeze check, the case staging, the
`blockMeshDict`/`controlDict` templating at the NEW mesh numbers, the L-343 `USER` pin, the
cap arithmetic and the `RUN_RC.txt` write — **grades nothing**, and **no gate, band, cap,
ceiling or label depends on it**. Its cost is seconds and is reported with the run's
calibration. It is registered here because the launcher carries three blocks that have
never executed: the new mesh table, the `ALL` loop, and the `USER` pin.

---

## "DO NOT RE-REGISTER" WAS CONSIDERED

Row #27 met **both** frozen gates at its finest level (0.9006 % against a 3.00 % band;
5.397e-03 against a 1.00e-02 band) and is still `NOT A RESULT`, because rule 5 turns a
non-`CONVERGING` triple into `NOT A RESULT` whatever the value. **The physics is already
in hand; what is missing is a grid family from which an order can be extracted.** That is
the cheapest possible thing to buy — **0.6 core-min, $0.00051 derived** — and it is bought
with a comparator that is not merely frozen but is *the same blob*, so there is no surface
on which a gate could have been re-tuned.

**Registered in advance, so it cannot be renegotiated afterwards:** if this triple is also
non-`CONVERGING`, the honest conclusion is that this gate scalar's grid response is not
usable on this case at any of the four mesh levels the lab has now run, and the next step
is a **diagnosis of the gate quantity** — not a third grid family.

## FALSIFICATION — named before the run

- **`GATE REACHED` is the hoped-for outcome and is NOT the predicted one.** It requires a
  `CONVERGING` triple AND both bands at L3. The bands are expected to be met (L3 here is
  R1's L1 mesh, and the R1 measured its deviation not to move under a 4x cell increase);
  the triple is **genuinely open**.
- **`NOT A RESULT` is a real and likely possible outcome** — any non-`CONVERGING` triple
  state, or an under-resolved L1, forces it whatever the values.
- **`GATE FAIL` is a real possible outcome** — a `CONVERGING` triple with a band missed.
- **A REFUSAL (exit 2) is a real possible outcome** and this R2 weakens nothing that could
  make one less likely: all ten of the comparator's controls are the same bytes, including
  the slug-shortcut control that refuses unless the exact/shortcut gap is 4.954869 % ± 0.01.
- **`PASS` is impossible by construction** — the tier ceiling is `GATE REACHED` and the
  comparator hard-codes it.

## GRADING PATH (fixed at this commit, rule 2)

`cases/ansys_verification/VMFL076-R2/grade_vmfl076.py`, blob
`42c8945544721e60a41fbe1a01513405b64d5f3c`, invoked as

```
python3 cases/ansys_verification/VMFL076-R2/grade_vmfl076.py \
        verification/runs/ansys_verification/VMFL076-R2 L1:2000 L2:2000 L3:2000
```

Launcher: `cases/ansys_verification/VMFL076-R2/run_vmfl076_r2.sh`, blob
`44b70b767d04bfd1063504187c1a55cd36179b4e`, invoked as
`run_vmfl076_r2.sh graded ALL`.

## PROVENANCE

- **Attempt 1, cited and not overwritten:** `cases/ansys_verification/VMFL076/` —
  `PREREGISTRATION.md`, `RESULTS.md` (§2 the OSCILLATORY triple, §7 the coarser-family
  repair this file executes), `PREFREEZE_GROUNDWORK.md` (commit `671936c0`), comparator
  blob `42c89455`; register row **#27**, `NOT A RESULT`. Measured cost 48.9000 core-min,
  of which L1 (this R2's L3 mesh and `endTime`) was **0.4500**.
- **Manual:** `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
  p.219, title-page verified against the PDF beside it (rule 15).
- **Standing rules and lessons applied:** CLAUDE.md rules 1–6, 10, 12, 13; **L-332**;
  **L-339**; **L-342**; **L-343** (the `USER` pin); **L-347** (every channel control run
  and reported — satisfied here by the R1 comparator, which already runs all ten of its
  controls before grading and names the one that fails).
- **Compute authority:** Sanaa's permission boarded at commit `bc0e687e`. RANKS = 1.

*Verdict vocabulary only (rule 1): PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED
/ PENDING. A GATE FAIL, a NOT A RESULT or a refusal is recorded honestly and never
softened.*
