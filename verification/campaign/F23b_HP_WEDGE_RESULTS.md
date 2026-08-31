# F23b_HP_WEDGE — RESULTS AND CRASH TRIAGE

**Verdict: `BLOCKED`.** The label is the one §A1.5 pre-registered for this outcome and it
stands. **The cause is not the one the run appears to show, and the corrected cause is the
finding.**

- **Team:** cfd. **Rung id:** `F23b_HP_WEDGE`.
- **Pre-registration:** `verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md`, frozen at
  commit **`57d31dde434f3af8332cc8a882808bdb28e21079`**.
- **Ran:** 2026-08-31T00:23:32Z → 00:25:57Z, pid/sid 1644184, 4 ranks, **145 wall s**.
  Held once at 00:22:27Z for core headroom, then launched.
- **Triage by:** `cfd-supervisor`, personally, 2026-08-31 —
  `SUPERVISION_CHARTER.md` §3 check 2. *A crash, a divergence or a refused solve is a
  finding about the case, the method or the toolchain until triage demonstrates otherwise.*

---

## 1. WHAT HAPPENED, AND WHY IT IS NOT A CRASH

The launcher exited **rc 1** at phase **A0**. Two independent inside-the-wrapper captures
agree: `cases/F23b_HP_WEDGE/STATUS.F23b_HP_WEDGE` (`launcher_rc=1
end=2026-08-31T00:25:57Z`) and the launcher's own EXIT-trap record
`verification/runs/F23b_HP_WEDGE_runs/RUN_STATUS.F23b_HP_WEDGE.txt`
(`launcher_rc=1 phase=A0 preflight=0`). Neither is an rc read around a `setsid` line, so
neither is the false zero that construction produces.

**`simpleFoam` itself exited 0.** The refusal came from the grader:
`grade_f23b.py --arm-born` read best `|1 − Ubar| = 9.692465e-04` over 40 checkpoints
against the frozen acceptance threshold of **`1.0e-10`**, and under §A1.5 that means the
arm-acceptance reader is **NOT BORN**, ARM-P and ARM-F must **REFUSE** rather than
accept-or-reject, and the rung is `BLOCKED`.

**So this is a registered refusal firing exactly as designed.** The obvious reading —
*the A0 control solve underperformed* — is the one triage exists to test, and it is
**wrong**.

---

## 2. THE FINDING — THE ACCEPTANCE TEST WAS UNSATISFIABLE ON ANY FINITE MESH, AND THE PROOF IS INTERNAL TO THE FROZEN DOCUMENT

`|1 − Ubar|` is a **discretisation error**, not an iterative residual. It floors at the
mesh's own truncation error and goes to zero **only under mesh refinement, never under more
iterations**. `1e-10` is an iterative-convergence tolerance. Applying it to a
discretisation-error quantity makes the test unsatisfiable on any finite mesh.

**This is not an inference from the failed run. It is arithmetic on the registration's own
predictions.** §12 registers predicted `f·Re` per ladder level. The case's own relation
(§1) is `f·Re = 2 D² G / (ν Ubar)` with `D = 1`, `G = 0.32`, `ν = 0.01` — which returns
exactly `64.0` at `Ubar = 1`, verified. Inverting it, `Ubar_h = 64 / f·Re_h`:

| level | cells | registered predicted `f·Re` | **implied predicted `\|1 − Ubar\|`** | **ratio to the 1e−10 threshold** |
|---|---|---|---|---|
| coarse | 131,072 | 63.992221588 | **1.215525e−04** | **1,215,525 ×** |
| medium | | 63.998078262 | **3.002806e−05** | 300,281 × |
| fine | | 63.999542924 | **7.141864e−06** | **71,419 ×** |

**§5.5 sets ARM-P's acceptance at `|1 − Ubar| ≤ 1e−10` at the COARSE level — the very level
whose own registered prediction sits 1.2 million times above that threshold.** Even the
**finest** level of the ladder is predicted 71,419× above it.

A0's observed **9.692465e-04** at 1,024 cells is 9,692,465× the threshold and sits on the
same discretisation-error family, at the magnitude a 16-cell radial resolution implies.

**ARM-P could not have accepted. ARM-F could not have accepted. A0 could not have
accepted.** The branch rule of §5.5 had no reachable accepting outcome at any level, under
any relaxation, after any number of iterations.

### 2.1 Where the registration's reasoning went wrong, precisely

§A1.5 justifies A0 by citing F23's §7: *"that exact 16 × 64 configuration converging (`Ux`
2.3e−16 by iteration 4,000), so it is the one configuration on this box already known to
deliver a converged artifact."*

**That citation is sound — for the clause it actually supports.** A0's acceptance has
**two** clauses:

1. `Ux` initial residual ≤ **1e−12** — a genuine **iterative** quantity. F23 §7's
   `2.3e−16` is exactly this quantity, and this clause is defensible.
2. `|1 − Ubar|` ≤ **1e−10** — a **discretisation** quantity. F23 §7's record says
   **nothing whatever** about it.

**The registration cited evidence for one clause and applied it to two.** Two quantities
that both look like "convergence" were treated as one, and only one of them can reach a
tolerance like `1e-12` by iterating.

### 2.2 The registration's own real readings agree, once separated

§5.1 drove the same reader over F23's completed levels and read `|1 − Ubar| = 3.6251e−02`
(coarse) and `4.2091e−01` (medium) — far **above** the §12 predictions of `1.22e−04` and
`3.00e−05`. There is no contradiction: those levels were **`NOT_PLATEAUED`** (§5.1 records
them 280× and 1,030× outside their own plateau tolerance, *"still accelerating from rest at
the last checkpoint"*), so their readings carry a large **iterative** error **on top of** the
discretisation floor.

**That decomposition is what makes the finding airtight.** Drive the iteration to machine
zero and the readings fall — to the §12 floor of `~1.2e−04` at coarse, and no further. The
threshold sits six orders **below the floor**.

---

## 3. THE SECOND DEFECT — THE DECIDING ARTIFACT WAS WRITTEN TO `/tmp` AND THE REBOOT DESTROYED IT

`cases/F23b_HP_WEDGE/run_f23b.sh:87` puts the whole pre-ladder in
`SCRATCH="${TMPDIR:-/tmp}/f23b_preladder_$$"` and **copies nothing back**. The 14:35Z reboot
wiped it. A0's `log.build`, `log.decomposePar`, `log.simpleFoam`, `RC.txt`,
`ARM_ALLOWANCE.txt` and all four `processor*/` trees are **gone**.
`verification/runs/F23b_HP_WEDGE_runs/` holds exactly one 448-byte text file.

**Consequence, stated plainly: the number `9.692465e-04` is currently UNCITABLE.** It
survives only as prose in `cases/F23b_HP_WEDGE/launcher.queue.out`. By this lab's own
standard a number whose artifact is gone is not a result, so §2's finding is deliberately
**not** built on it — §2 rests on the registration's own registered predictions, which are
on disk and re-readable. The observed value is quoted as corroboration, never as the load
bearing evidence.

**The real constraint that produced the defect is worth keeping:**
`scripts/queue_runner.py:496` truncates a file named `STATUS.*` **unconditionally**, and
F23b's launcher correctly avoided that name for its own record. Avoiding the collision was
right; solving it by going to `/tmp` was not. The successor writes its pre-ladder **under
the run root**, retained.

---

## 4. COST — BURNED, WASTED, AND TWO BOOKKEEPING DEFECTS

| | core-min | basis |
|---|---|---|
| A0 solve, charged by the launcher's own accountant | **1.86667** | 28.0 wall s × 4 ranks ÷ 60, from `RUN_STATUS.F23b_HP_WEDGE.txt` |
| harness remainder (path resolve, 4 selftests each also under `-O`, freeze verify, `build_f23b`, `decomposePar`) | **≈ 1.95** | **DERIVED, not measured** — 145 total wall s minus the 28 s mpirun, at an assumed 1 rank |
| **gross process spend** | **≈ 3.82** | |

**All of it is WASTE**, in the operative sense: it produced no retained artifact and would
have to be re-spent in full. Waste is **named separately and never absorbed** into an
estimate-versus-actual ratio. Dollars **derived, not measured** at $0.0513/core-h:
**$0.00160** charged, **≈ $0.00327** gross. No cap was breached — the pre-ladder cap 20.0
was 9.3% consumed, the ladder cap 293.0 untouched.

**Two bookkeeping defects (L-342 — infrastructure defects void a cost claim, never
physics):**

1. **A0 overran its own line item 5.33×.** Registered 0.350 core-min (build 0.050 + solve
   0.294 at §9.1's measured coarse rate). Actual charged solve **1.86667** = **6.35×** the
   registered solve. **§9.1's coarse rate does not transfer to a 1,024-cell case** the way
   §A1.6 assumed.
2. **The launcher charges only the `mpirun`.** The build and `decomposePar` are uncharged
   though A0's registered 0.350 explicitly budgets 0.050 for the build. **≈1.95 core-min of
   real spend sits outside every running total.**

---

## 5. DISPOSITION — WHY THIS IS NOT REPAIRABLE HERE

**First compute has occurred under `57d31dde`, so rule 2 CLOSES the gates.** A dated
addendum may not alter a gate, a threshold, a cap or a label, and the acceptance threshold
is all four at once. **`F23b` cannot be repaired; it ends `BLOCKED`.**

§A1.5 clause (4) already anticipated the shape of the resolution: **a new registration under
a new sha**, never a third arm under this one. A successor is in draft and carries two
registered departures — a `|1 − Ubar|` acceptance derived from the level's own **h²
discretisation prediction with a stated margin** rather than from an iterative tolerance,
and a pre-ladder written **under the run root**. The successor's threshold is derived from
the prediction **before compute** and explicitly **not** chosen to clear the observed
`9.692465e-04`, which would be selecting a gate to fit an answer.

**What this rung bought for its ≈3.82 wasted core-minutes:** the knowledge that a whole
class of acceptance test in this lab — a bulk-quantity error gated at a residual tolerance
— is unsatisfiable by construction, and that the defect is invisible to every instrument
because **the instrument works perfectly**. The reader read correctly, the refusal fired
correctly, the launcher recorded correctly, and the answer was still unreachable. That is
worth more than the `PASS` would have been.
