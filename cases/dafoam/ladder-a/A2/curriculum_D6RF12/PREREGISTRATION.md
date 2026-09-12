# D6RF12 — **THE nuTILDA REPAIR APPLIED TO THE A2 FD PROBE.** PRE-REGISTRATION.

**FROZEN AT THIS COMMIT** by a `lab-lane` of the dafoam team, 2026-09-12, **before any
D6RF12 compute exists** (CLAUDE.md rule 2). The run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF12-a2-wing-fd-nutilda-repair`
**does not exist** at this commit — that is the condition, and it was checked by listing
the parent directory in the same invocation that wrote this line. The **grading path
`d6rf12_grade.py` is committed IN THIS SAME COMMIT**. Gates, thresholds, cap and label are
closed from here. **SUBMISSIONS PARKED** (rule 7).

---

## 1. Why this item exists

D6RF11 graded **`GATE FAIL`** (G1=FAIL, G2=PASS, G3=PASS, G4=PASS). Its `fvSolution`
carries `nNonOrthogonalCorrectors 12` — so the R3 package installed — but the **LOOSE**
linear-solver stopping rule: GAMG `relTol 0.1` / `tolerance 0`, smoothSolver `relTol 0.1`
/ `tolerance 0` / `nSweeps 1`. It was frozen before knobs 7–8 were identified.

**D6RF12 is D6RF11 with knobs 7–8 and nothing else.**

## 2. The mechanism, measured on four items and closed from both ends

`d6rf7_fvSolution:67` — the registered repair base, whose `:80` names itself *"THIS IS THE
nuTilda REPAIR (D6RF4 §1.5)"* — states the cause: **`tolerance 0` means no absolute
tolerance can ever terminate an inner solve, so `relTol` alone sets the plateau.**

Measured from the other end, on the last printed step of each item's own log:

| item | `nIters` | initRes/finalRes **within the outer step** | initRes/floor | outcome |
|---|---|---|---|---|
| D8G pre-fix (loose) | 1 | **12.3×** | 4.074× | failed |
| D6RF11 (loose) | 1 | **23.8×** | 1.139× | failed |
| A3GC-AR1 | **3** | **25.1×** | 1.009× | failed |
| **D8G R1 (tight)** | 3 | **1119.7×** | **0.787×** | **CLEARED** |

**Three failures in a 12–25× band; one clearance at 1120×; no overlap.** `nIters`
correlates but does **not** discriminate — A3GC-AR1 has `nIters: 3` and still missed.
**How far the linear solve is driven inside each outer step does.** That is why the
registered prediction below is a *factor*, not a direction.

## 3. The delta — six values, and nothing else

From `cases/dafoam/ladder-a/A2/curriculum_D6RF7/d6rf7_fvSolution`, applied to D6RF11's
`fvSolution`:

| solver | knob | D6RF11 (loose) | **D6RF12 (tight)** |
|---|---|---|---|
| GAMG (`p`) | `relTol` | 0.1 | **0.001** |
| GAMG (`p`) | `tolerance` | 0 | **1e-12** |
| GAMG (`p`) | `minIter` | *(absent)* | **5** |
| smoothSolver | `relTol` | 0.1 | **0.001** |
| smoothSolver | `tolerance` | 0 | **1e-09** |
| smoothSolver | `nSweeps` | 1 | **3** |

`nNonOrthogonalCorrectors 12` and every other D6RF11 setting are **unchanged**. The fix is
**not tuned to chase a nicer number**; these are the six values `d6rf7_fvSolution` already
carries with their own measured justification.

## 4. **REGISTERED PREDICTIONS — WRITTEN BEFORE THE RUN, ON THREE INDEPENDENT AXES**

**(a) QUANTITATIVE.** The cleared arm drives the solve **47.0×** further per outer step
than D6RF11 (1119.7 / 23.8). Applied to D6RF11's measured `nuTilda initRes`
**1.139494133e-05**, this predicts

> **`nuTilda initRes` ≈ 2.4e-07 at the last printed step**, against the **1.0e-05** floor
> — a margin of roughly **41×**, not a squeak.

**(a2) QUANTITATIVE — `p`, AND IT IS NOT A BYSTANDER.** D6RF11's **true outer** `p`
residual is **2.556601762e-05 = 2.557× OVER its 1.0e-05 floor** (§6a: its grader read the
13th corrector's residual, 1.719431323e-09, and PASSED a gate that should have FAILED).
Knobs 7–8 change the **GAMG `p` solver** as well as the smoothSolver, so `p` must be
predicted too. Derived identically to (a), from the **first (outer) solve** of each final
block: D6RF11 reduces `p` by **15.66×**, the cleared D8G R2 arm by **1108.16×**, a further
drive of **70.74×**. Applied to 2.556601762e-05:

> **outer `p initRes` ≈ 3.6e-07** against the **1.0e-05** floor — a margin of about **28×**.

***A successor that predicts one equation and is silent on the other cannot distinguish
"the repair works" from "the repair works on the equation we happened to watch."***

**(b) COMPLETION.** `d6rf3_fd_endpoint.jsonl` carries **at least one row of
`kind == "fd_step"`**, **and** the log carries the producer's own terminal marker
**`D6RF3_FD_ENDPOINT_WRITTEN`**.

**All three outcomes are registered in advance, and they apply to (a) and (a2) alike:**

| outcome | reading |
|---|---|
| lands near **2.4e-07** and (b) holds | mechanism confirmed **with a factor**, not a direction |
| **clears the floor but lands near 9e-06** | the knobs worked **for some other reason**, and we need to know that |
| **does not clear** | **the nuTilda story is wrong** — which is bigger than another pass |

***A prediction that can only be right is not worth registering.*** Axis (b) exists
because without it this item could pass its FD gate again on an inventory row and prove
nothing — see §6.

## 5. Gates

1. **G1** — zero genuine primal failures: **zero** occurrences of
   `did not satisfy the prescribed tolerance`.

   **COUNTED ON THAT STRING, NEVER ON A RAW GREP OF `Primal solution failed!`** — which
   counts Python traceback frames, not failures. Measured (D8G ADDENDUM 10): D8G pre-fix
   and D6RF11 each show **1** genuine tolerance failure against **17** raw grep hits,
   because the `AnalysisError` propagated up through OpenMDAO and printed a stack; A3GC-AR1
   shows 1 and 1; D8G R1 shows 0 and 0. **Every stalled item has exactly ONE genuine
   failure.**

   **THE MISCOUNT IS INHERITED AND IS RECORDED HERE SO THE NEXT READER INHERITS THE
   CORRECTION RATHER THAN THE ERROR.** `d6rf11_grade.py:20` reads
   `G1_MAX_PRIMAL_FAILURES = 0  # D6RF3 recorded 17` — the "17" is the same traceback
   miscount, sitting in that comparator's **comment**. **Its threshold is `0` and is
   correct either way, so nothing was ever mis-gated; only the provenance is wrong.** That
   file is frozen and **is not touched** (rule 6).
2. **G2** — the **TRUE OUTER** `p initRes` **<** the accept floor **1.0e-05**.
   **READ AS THE FIRST MATCH PER EQUATION PER TIME BLOCK, NEVER THE LAST** — see §6a. With
   `nNonOrthogonalCorrectors 12` the solver prints **13** `p initRes` lines per outer step,
   one per corrector, and the last is the residual of an almost-solved field.
3. **G3-FDSTEP** — §6. **Both limbs**: ≥ 1 row of `kind == "fd_step"` **and** the terminal
   marker present.
4. **G4** — the artefact is newer than the arm's own age datum (rule 4).
5. **Strict completion** (rule 4) and the **planted-zero control** (rule 3) apply to every
   reader.

**The accept floor does not move.** It is the **product** `primalMinResTol 1e-08 ×
primalMinResTolDiff 1e3` (N-D43) = **1.0e-05** — not touched here, and not in any
successor.

## 6. **G3-FDSTEP — THE REPAIRED GATE, AND WHY THE OLD ONE HAD TO BE REPLACED**

D6RF11's `G3` (`d6rf11_grade.py:111-113`) counts `len(rows)` of **any kind** against a
minimum of 1 and **prints the total as "FD sample rows"**. Measured: it **PASSED** on
D6RF11's single `kind: "endpoint_dvs"` DV-inventory row — 96 shape, 7 twist — written at
**log line 8, before any FD work**, while the producer's terminal marker
`D6RF3_FD_ENDPOINT_WRITTEN` printed **zero** times and the first
`Primal solution failed!` landed at **line 2748** inside `cl04.coupling.solver`.
**There was never an FD sample.**

**The old gate's bounds line made it worse, and this is the part worth carrying:** *"one
FD sample is a PROBE, not the FD table the charter's bright line requires"* conceded
exactly the right caveat **about the wrong object**, so a miscounted number arrived
pre-hedged and read as carefully qualified truth. **A correct caveat attached to a
miscounted quantity is more dangerous than no caveat at all**, because it buys the number
credibility it has not earned.

**G3-FDSTEP reads the `kind` field and requires the producer's own terminal marker** —
two independent limbs, because either alone is forgeable by an early exit.

**IT IS DRIVEN IN THREE DIRECTIONS BEFORE IT IS TRUSTED, and the controls ran before this
freeze** (`d6rf12_g3_control_evidence.txt`):

| direction | fixture | required | measured |
|---|---|---|---|
| **negative, REAL** | D6RF11's actual inventory-only file + its actual log | **FAIL** | **FAIL** — `kinds {endpoint_dvs: 1}`, `n_fd_step_rows 0`, marker absent |
| **positive** | same file + one planted `fd_step` row + a log carrying the marker | **PASS** | **PASS** |
| **negative, forged completion** | planted `fd_step` row but **marker absent** | **FAIL** | **FAIL** — an early exit cannot forge completion |

`state: EXERCISED-PASS`. **On the same real file the old gate returns PASS and G3-FDSTEP
returns FAIL** — the defect demonstrated on the artifact itself, not in the abstract.
*A gate that has only ever seen its passing case is how the old one shipped.*

## 6a. **FIRST-MATCH READING — THE CORRECTOR ARTIFACT, AND THE FALSE PASS IT ALREADY PRODUCED**

`primalResidualControl` prints **one `initRes` line per corrector**, from inside the
corrector loop. A reader that keeps the **LAST** match in a time block therefore reads the
final corrector's residual off an almost-solved field — a tiny number that says nothing
about whether the **outer** iteration converged.

**IT HAS ALREADY PRODUCED A FALSE PASS, ON THE ITEM THIS ONE SUCCEEDS.** Measured:

| | D6RF11 final block |
|---|---|
| `p initRes` lines in the block | **13** (`nNonOrthogonalCorrectors 12` + 1) |
| **TRUE outer `p`** (first line) | **2.556601762e-05** = **2.557× OVER** the 1.0e-05 floor |
| what `d6rf11_grade.py:98` read (`res[-1]`) | **1.719431323e-09** = 1.72e-04× the floor |
| understatement | **14,869×** |
| **G2 as graded** | **PASS** |
| **G2 in truth** | **FAIL** |

D6RF11's item verdict does not move — it was `GATE FAIL` on G1 — but **both** G1 and G2
fail, not one.

**THE SHARPER FORM OF THIS DEFECT CLASS, AND IT IS THE DANGEROUS ONE.** `d8g_grade.py:559`
is `read_max_init_res` — **named for a `max`, implemented as a last**, because
`vals[eq] = ...` inside a `finditer` loop lets each match overwrite the previous. That one
a name-based sweep catches. **`d6rf11_grade.py` does not misname anything**: it stores
`last_p_initRes`, truthfully, and then **gates that honest "last" against a floor that
means "outer"**. *An honestly-named LAST consumed as if it were the OUTER gives no warning
at the call site at all.* Both forms are in scope here; this comparator reads the **first**
match and says so at the point of use.

**Single-corrector logs are immune — one line per block — which is why this never fired
before.** Verified by count, not inferred: A3GC-AR1 runs `nNonOrthogonalCorrectors 0` and
prints exactly **1** `p initRes` line in its final block, so its grading is untouched.
**`nuTilda` prints exactly ONE line per block in EVERY arm measured** — D8G pre-fix, R1,
R2, D6RF11 and AR1 — so the §2 reduction-factor table is immune to this artifact entirely.

**STANDING RISK, FLAGGED NOT FIXED:** `a3gc_grade.py:700-701` carries the same
overwrite-in-loop pattern into `last_initRes`. A3GC-AR1 is immune because it runs
`nNonOrth 0`, **but any future A3GC arm with correctors would be exposed.** That file is
frozen and is **not touched** (rule 6); this is a disclosure, not a repair.

## 7. Cost

**Estimate: ~95 core-min**, 4 ranks — D6RF11's own F-probe arm as the basis, plus the
tighter inner solve. **STATED AS AN ESTIMATE**, which `scripts/cost_calibration.py`
records as the class that has produced every over-run above 1.05× on this ledger; the
estimate-versus-actual comparison lands in `docs/COST_CALIBRATION.md` at completion
(rule 12), with **contention named separately from misprediction and neither divided into
the other**, and waste named separately even when zero.

**NO CAP OF ANY KIND.** Sanaa 2026-09-12, fourth ruling: *"NO RUN GETS STOPPED BC OF A
TIME OR BUDGET CAP."* Absent by construction: no `timeout -k`, no cap-derived deadline, no
`rc=124/137` path, no launch budget, no kill branch.

**MEMORY CONTAINMENT KEPT** — `--memory` / `--memory-swap` / `--oom-score-adj`. A ceiling
that cannot bind a healthy run is a seatbelt, not a cap (D8G ADDENDUM 8).

## 8. Bounds, stated before the numbers exist

**PATCHED ROW ONLY.** No shipped-row arm runs here, so nothing in this item is a verdict
**about DAFoam** — only about this patched build. **One FD probe is not the FD table the
charter's bright line requires**, and axis (b) clearing does **not** discharge it: it
establishes only that the FD arm *completed*, not that any step lies in the plateau.
