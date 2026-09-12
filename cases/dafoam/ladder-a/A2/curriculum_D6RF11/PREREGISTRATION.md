# Curriculum D6RF11 — the FD arm re-run under the primal config that was ALREADY MEASURED to clear the floor at this exact design

**Item id:** `D6RF11` (dafoam, A2 MACH wing; successor to `D6RF3`, whose `F_mp` closed `rc=1`).
**Version 1.0 — FROZEN 2026-09-12 by dafoam `lab-lane` for `dafoam-supervisor`.**
**Committed BEFORE any container starts** (`CLAUDE.md` rule 2). The freeze sha is the commit that
introduces this file, **and the grading path `d6rf11_grade.py` is committed in the same commit** —
the rule-2 departure disclosed on D6R2 at `bc3aa7ce2` is not repeated here.
Permission for detached launches: **`bc0e687e`**. **Nothing is sent, filed or posted** (rule 7).
**This item has burned 0 core-min, started no container, and IS ARMED-BUT-HOLDING** — it fires only
when both release conditions in section 5 are true.

---

## 0. THE PREMISE THE SUPERVISOR GAVE ME WAS WRONG, AND I CHECKED IT BEFORE SPENDING ON IT

The ruling asked for a probe to test whether the D6RF10-R3 primal fix **transfers across cases**:
*"if it does not, the fix does not transfer and that is a bigger finding than a pass."* That framing
assumes R3's measurement was taken at a different design point from the one D6RF3's FD arm failed on.

**It was not. I compared the two design vectors and they are bit-identical.**

| | D6RF10 `P_conv` (where R3 measured `6.323e-06`, PASS) | D6RF3 `F_mp` (where the FD arm failed, `1.3162e-05`) |
|---|---|---|
| `OptView.hst` md5 | `70fafa07bdee618fef13039433c01114` | `70fafa07bdee618fef13039433c01114` — **same file**, and the same as D6R's own `O_mp/OptView.hst` |
| `_n_major_rows` | 88 | 88 |
| `_final_J` | `0.022238800232340834` | `0.022238800232340834` |
| `shape` (96 DVs) | — | `max_abs_diff = 0.000e+00` |
| `twist` (7 DVs) | — | `max_abs_diff = 0.000e+00` |
| `patchV_cl04/05/06` (6 DVs) | — | `max_abs_diff = 0.000e+00` |

The two JSON files differ in md5 **only in their `_extractor` / `_extractor_md5` metadata strings**,
which name the extractor that wrote them. Every design variable is identical to the bit.

**Consequence, stated plainly: there is no transfer gap to test.** The R3 config's `6.323e-06` was
measured at *exactly* the design where the FD arm plateaued at `1.3162e-05`. Re-running a single
primal there would spend 618 core-min to re-learn a number already on disk, twice-plateaued.

**So this item asks the question that is actually still open**, and it is a better use of the same
compute. Section 1 states it.

## 1. WHAT IS STILL UNMEASURED, AND WHAT THIS ITEM BUYS

D6RF10 measured **one unperturbed primal** at the endpoint. The FD arm does something the probe
never did: it deforms the mesh to the endpoint, then **perturbs each design variable and re-solves**.
Three things are therefore untested and all three are on the critical path to any 3D gradient here:

1. Whether a **perturbed** design converges under the R3 config, or only the unperturbed endpoint.
2. Whether the FD driver's own code path — extract → units assert → `d6rf3_fd_endpoint.py` — gets
   past `Primal solution failed!` at all.
3. Whether **any** FD sample row is written, which is the thing the charter's bright line requires
   and which this territory has never once produced on a 3D case.

**D6RF11 is D6RF3's `F_mp` arm re-run with ONE registered change: the primal config package.**

## 2. THE ONE REGISTERED DELTA — and it is a PACKAGE, not a knob

Reproduced byte-for-byte from `d6rf10_cmd_R3.sh`, the leg that MEASURED the PASS:

| | D6RF3 `F_mp` (`rc=1`) | D6RF11 |
|---|---|---|
| `solverName` | `DARhoSimpleFoam` | **`DARhoSimpleCFoam`** (SIMPLEC) |
| `nNonOrthogonalCorrectors` (SIMPLE scope only; `potentialFlow`'s 20 untouched) | as D6R | **12** |
| relaxation `(p\|p_rgh)` | `0.30` | **0.70** |
| relaxation `(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega)` | as D6R | **0.70** |
| `endTime` | `1000` | **2000** |
| `fvSchemes` | as D6R | **`d6rf7_fvSchemes_LIMITED`**, md5 `fbca617a0808c56113a34d156c5890b9`, asserted at every install site |
| instruments (`d6rf3_extract_endpoint.py`, `d6rf3_endpoint_physical.py`, `d6rf3_units_assert.py`, `d6rf3_fd_endpoint.py`, `d6rf3_opt_runScript.py`, the endpoint DV JSONs) | | **identical, byte-for-byte**, md5-asserted on both sides of the stage copy |

**It is honestly a package of six changes installed together, not one knob.** That is exactly how R3
measured its PASS, and reproducing the measured configuration faithfully matters more than isolating
which member of it does the work. Isolation is a later item and is named as such.

**The installer is `d6rf10_cmd_R3.sh`'s own `install_config()`, carried unchanged**, including its
refusal `installed ZERO sites -- a swap that swapped nothing` and its per-site grep-back of every
value it set. A config that did not install is not a run.

## 3. THE GATES, FROZEN. Threshold, cap, label.

Graded on the arm's log, `d6rf3_fd_endpoint.jsonl` and the ledger, all read after the container exits.

- **G1 — THE PRIMAL NO LONGER FAILS.** **Zero** occurrences of `Primal solution failed!` in the arm
  log. (D6RF3 recorded **17**.)
- **G2 — THE BINDING FIELD CLEARS ITS FLOOR.** The last `p` init-residual printed for the
  unperturbed endpoint primal is **< 1.0e-05** — the floor being `primalMinResTol 1e-8 ×
  primalMinResTolDiff 1e3` (N-D43: the floor is the PRODUCT), carried UNCHANGED from D6RF3
  (`d6rf3_opt_runScript.py:67-68`). **The tolerance is not touched.** Loosening
  `primalMinResTolDiff` would clear the floor by moving the floor, and this item does not do it.
- **G3 — AT LEAST ONE FD SAMPLE EXISTS.** `d6rf3_fd_endpoint.jsonl` present, newer than the age
  datum, and carrying **≥ 1** sample row. (The file keeps the `d6rf3_` name because the instrument
  that writes it is carried BYTE-IDENTICAL; renaming it would make it a different instrument.) A sample row is the thing this
  territory has never once produced on a 3D case.
- **G4 — IT IS THIS RUN'S.** `rc` captured INSIDE the wrapper; every product strictly newer than the
  age datum; cold-start guard passed before staging.

**LABELS.** `PASS` — G1 ∧ G2 ∧ G3 ∧ G4. `GATE FAIL` — G4 holds and any of G1–G3 misses, with the
residual, the failure count and the sample count printed beside it. `NOT A RESULT` — G4 fails.
No other label, no synonyms (rule 1). **No Roache triple is claimed and no GCI is quoted.**

## 4. THE PREDICTION, REGISTERED BEFORE THE RUN

**G1 and G2 are predicted to PASS.** The basis is not hope: R3 drove this exact design's binding
field to `6.323e-06`, **below the floor and plateaued** (late-window relative spread `1.47e-05 %`
over times 1500–2000), `R3_autograde.json`, binding verdict PASS.

**G3 is predicted to PASS but is the genuinely open one** — no perturbed design has ever been solved
on this case under any config.

**If G1 or G2 fails, that is the bigger finding**, and it means what the supervisor's framing meant
one level down: the fix does not survive the FD driver's own path even at the design where it was
measured, and the blocker is in the driver, not in the primal config.

## 5. RELEASE CONDITIONS — IT IS ARMED AND HOLDING, AND IT DOES NOT FIRE ON A CLOCK

`d6rf11_hold_release.sh` launches only when **BOTH** are true, re-read every 30 s:

1. **A3GC-AR1 has landed** — pid `2766682` (docker client, cwd `/home/ubuntu/certonomous-runs/A3GC-AR1`,
   container `sleepy_golick`, 4 ranks) is no longer alive. Four of our runs are live at load ≈ 44 on
   16 cores; a fifth starves the priority-1 case. **The release watches the process, not the clock** —
   an estimated 05:30Z is not evidence that it finished.
2. **The supervisor's GO exists** — the file `D6RF11_ARM.go` is present in the run root.
   **It is deliberately ABSENT at freeze**, because section 0 disproved the premise the launch
   ruling rested on, and arming an auto-fire on a question I have just shown is already answered
   would spend compute on the wrong measurement. `touch` that file to arm; the probe then fires the
   moment AR1 clears, with no further action.

The release script **never kills, signals or renices anything**. It waits and it launches.

## 6. COST, in core-minutes, BEFORE the run (rule 12)

| | figure | basis |
|---|---|---|
| unperturbed endpoint primal | **617.6 core-min** | **MEASURED** — D6RF10 ledger row `ARM=P_conv rung=R3 phase=candidate rc=0 wall_s=9264 core_min=617.6`, same case, same config, same design, cold start |
| one perturbed primal | **617.6 core-min** | the same measured figure applied again |
| **REGISTERED PREDICTION** | **1,236 core-min** | 2 × the measured R3 primal |
| derived dollars | **$1.06** | 1236/60 h × $0.0513/core-h. **DERIVED, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5) |
| cap | **NONE.** Reported only | Sanaa's NO-CAP ruling `6f3abf8a3`; no `timeout`, no `docker stop`, nothing kills on spend or clock |

**Why the cold figure and not a cheaper one.** The second primal restarts from the first's converged
state and should cost less, but **I have no measurement of a restart under this config on this case,
and I will not price a guess.** The cold figure is registered and the gap will be reported as
measured-versus-predicted at completion (rule 12's calibration clause).

**For the full FD table, if this probe passes:** D6R registered its `F_mp` at a predicted 231.2
core-min under the SIMPLE config; the **MEASURED** per-step penalty of this config package is
**37.2×** (`0.008293 → 0.308800 core-min/step`, from D6RF10's own R1 and R3 ledger rows), scaling to
**≈ 8,600 core-min ≈ $7.35 derived**. That figure is **an estimate from a measured ratio, not a
measurement**, and it is not registered as this item's cost — it is the number the next registration
must argue about.

## 7. What this item does NOT claim

It does not produce a verdict about DAFoam (**PATCHED row only** — the two-row rule is unmet, as on
D6R2). It does not verify the adjoint: an FD table with one sample is a probe, not the table the
charter's bright line requires. It does not isolate which member of the six-change config package
does the work. And it changes no tolerance anywhere.
