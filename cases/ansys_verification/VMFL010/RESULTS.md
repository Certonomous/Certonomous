# VMFL010 — Laminar Flow in a 90° Tee-Junction: `NOT A RESULT`

**NOT FILED ANYWHERE.** Nothing here leaves this box (CLAUDE.md rules 7, 8;
`ANSYS_VERIFICATION_CHARTER.md` §8). **SUBMISSIONS PARKED.**

Graded by `ansys-lane-opus`, 2026-08-25T20:27Z, against the pre-registration frozen and
committed BEFORE the run. The lane did not launch this case — it was already on disk,
complete — and did not modify the comparator.

---

## VERDICT: `NOT A RESULT`, on rule 5 step 2 — the grid triple is `OSCILLATORY`

| level | cells | flow split (main branch) |
|---|---|---|
| L1 | 3,600 | 0.8859493355955057 |
| L2 | 14,400 | 0.8844529270402999 |
| L3 | 57,600 | 0.8847487181565803 |

The sequence falls then rises: Δ(L1→L2) = **−1.4964e-3**, Δ(L2→L3) = **+2.958e-4**. It is
**not monotone**, so the triple classifies `OSCILLATORY`, and CLAUDE.md rule 5 step 2 makes
the row `NOT A RESULT` **whatever the value**. No GCI is quoted, because a GCI is never
quoted when the three values are not monotone.

**This is not softened, and the near-agreement does not rescue it.** The finest-level value
0.8847 sits **0.26 %** from the manual's reference 0.887 — comfortably inside the frozen
3 % band, so a value-only reading would have called this a `GATE REACHED`. It is not one.
The gate can only turn a result **into** `NOT A RESULT`, never the reverse, and this lane
is not reaching past it. **This row is not a credential.**

Note the ceiling was already capped before the run: the frozen pre-registration §4 declares
the reference **code-to-code**, buying neither V nor P, so the best this case could ever have
earned was `GATE REACHED` — never `PASS`. It earned neither.

## The triple is genuine — rule 5 step 1 was checked first and passed

A non-monotone triple is often an artefact of levels that never converged. **That is not the
cause here.** Every level reached SIMPLE's convergence criteria on its own:

| level | `SIMPLE solution converged` | final Ux initial residual | final p initial residual | last time |
|---|---|---|---|---|
| L1 | yes | 9.925464525e-08 | 6.685988006e-10 | 729 |
| L2 | yes | 9.822268888e-08 | 8.722207863e-10 | 1125 |
| L3 | yes | 9.946326653e-08 | 3.312030962e-10 | 1575 |

So the levels **are** iteratively converged and plateaued; the oscillation is real grid
response, not iteration noise.

**Diagnosis (a finding, not a write-off).** The flow split is an *integral ratio* of two
patch mass flows. Its discretisation error at these three levels is already down at the
1e-3–1e-4 relative level, and the change from L2 to L3 is **5.06× smaller in magnitude than
the change from L1 to L2 but carries the opposite sign**. That is the signature of a quantity
whose leading-order truncation term no longer dominates its own grid response — the error has
fallen into a regime where sub-leading and cancellation effects set the sign. Richardson
extrapolation has no meaning there, which is exactly why rule 5 refuses the row rather than
printing a fitted order. **Refining further will not fix this by itself**; the honest repairs
are either a gate quantity with a cleaner grid response, or a coarser triple that keeps the
leading term dominant (a larger refinement ratio placing L1 well inside the asymptotic range).
Recorded for the supervisor as a candidate `N-AV` numerics entry; **not** acted on here,
because changing a frozen gate quantity after compute is not this lane's to do.

## Controls

- **Strict completion (rule 4), evidenced on disk.** `rc = 0` in each `RUN_RC.txt`; one
  `End` line in each `log.simpleFoam` — matched by **exact name**, never a `log*` glob, since
  such a glob matches `log.blockMesh` first and would have read the *mesher's* `End` line;
  last time == the level's converged stop; postProcessing patch flows present.
- **Planted-zero (rule 3):** the comparator's plant arm is green under `--selftest`
  (`PASS plant seen`).
- **Comparator `--selftest`: exit 0** — 4/4, including that the reference kind is recognised
  as code-to-code and the success ceiling is therefore `GATE REACHED`, not `PASS`.

## A defect in the comparator, disclosed and NOT repaired by this lane

`grade_vmfl010.py` **writes no verdict artifact** — it prints to stdout and exits 0, and no
`GRADING_VMFL010.json` is produced. A verdict that lives only in a terminal is not an artifact,
and `rc = 0` on a `NOT A RESULT` cannot be distinguished from `rc = 0` on a pass by any later
reader of the disk. This lane **did not modify the frozen comparator**; it captured the
grader's own stdout verbatim to
`verification/runs/ansys_verification/VMFL010/GRADING_VMFL010.stdout.txt`, with the grader,
pre-registration and comparator blob hashes recorded beside it. **Repairing the comparator
is a measurement-script change and belongs to the supervisor's §3 check 1 (diffs read as
diffs) — it is referred upward, not done here.**

## Cost and calibration (rule 12)

| | core-minutes |
|---|---|
| pre-registered estimate (§12, as amended before first compute) | 10.29 |
| frozen cap (§12, as amended before first compute) | 38.57 |
| **actual, measured from `RUN_RC.txt`** | **3.5833** (L1 0.2167 + L2 0.5167 + L3 2.8500) |

Actual/cap = **9.29 %**; actual/estimate = **0.348**. Attribution: **misprediction**, in the
conservative direction — the estimate was scaled arithmetically from the corrected cell count
and still over-predicted. **No contention stall and no waste**: the longest level ran 171 wall
seconds, far under the 3600 wall-second stall threshold, and no level was discarded. Dollars
at the owner-stated $0.0513/core-h are **derived, not measured**
(`COMPUTE_BUDGET_CHARTER.md` §5): 3.5833 core-min ⇒ ≈ **$0.0031**.

**On the cell counts.** The frozen §8 named 2,800 / 11,200 / 44,800 cells and the meshes are
3,600 / 14,400 / 57,600. This is **not** an undisclosed departure: a dated amendment made
**before first compute** struck those figures and scaled the estimate and cap by 9/7 to the
values used above. The refinement ratio r = 2 is intact (×4 cells per level in 2D).

## Artifacts on disk

- Run root: `verification/runs/ansys_verification/VMFL010/`, levels `L1/`, `L2/`, `L3/`
- Captured verdict: `verification/runs/ansys_verification/VMFL010/GRADING_VMFL010.stdout.txt`
- Cost: `verification/runs/ansys_verification/VMFL010/COST.txt`
- Pre-registration blob `4d30fb4c80e6dc9c4cdedf893020d3092b632baa` — **verified equal to
  `HEAD:cases/ansys_verification/VMFL010/PREREGISTRATION.md`** at grading time
- Comparator blob `8bb2b2640428f6856c3e33432ca37f9d60dcd585` — **verified equal to HEAD**
- Launcher blob `324d2828c29c99d3c13a1ec40defb7b26a3f77da` — **verified equal to HEAD**
