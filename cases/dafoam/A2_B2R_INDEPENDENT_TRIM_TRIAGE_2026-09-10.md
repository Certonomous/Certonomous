# A2-B2R independent lift-trim — CRASH TRIAGE AND RUNG VERDICT — 2026-09-10

**Rung verdict: `NOT A RESULT`** — on the pre-registration's **own registered branch
`DIVERGED-TRIM`**, not on an unregistered crash. This is a supervisor's §3 check-2 crash triage,
done first-hand from the artifacts, recorded `[lab-attributed]` under the owner's 2026-09-10T03:45Z
directive. **SUBMISSIONS PARKED** (CLAUDE.md rule 7): nothing here is filed, sent, posted or
reported anywhere outside this box, and no upstream defect is filed by this record.

**Pre-registration:** `cases/dafoam/A2_B2R_INDEPENDENT_TRIM_PREREGISTRATION.md` (frozen).
**Run root:** `/home/ubuntu/certonomous-runs/A2B2R-independent-trim/`
**Launched** 2026-09-10T04:18:32Z, pid 1064679, 4 ranks; **exited** 04:19:24Z. `launcher_rc=0`
(`cases/dafoam/STATUS.queue.A2B2R-independent-trim`, whose own note says that code is the exit
status of the launch argv and **not** the solver rc); `RUN_RC.txt` reads `INNER_RC=1`.

---

## 1. THE 52-SECOND LIFE IS NOT A LAUNCHER FAILURE. The launch was clean and the physics ran.

Everything up to and including the first row worked, and each of these is read from the artifacts:

- **Age guard PASS** (`AGE_GUARD.txt`): `pinned_names_verified=25 processor_zero_seen=28
  processor_zero_rewritten_late=0 artifacts=2`.
- **Both frozen instruments byte-identical**, verified by me against the HEAD blobs, not relayed:
  `a2_decomposition_driver.py` sha256 `c4f42149…89cf0` and `a2b2r_rows.json` sha256
  `40a3fe7b…abe487` — the run copy, the worktree copy and `git show HEAD:` all three agree.
- **Decomposition and setup clean**, mesh staged, `DECOMP_NROWS 4`, `DECOMP_ROW_BEGIN
  R1_A4_anchor_cold`, `DECOMP_SETCHECK … twist 0.000e+00 shape 0.000e+00 patchV 0.000e+00`.
- **Row 1 solved to its horizon**: `decomp.log:874` `Time = 1000`, `ExecutionTime = 27.11 s`.
- Cost `wall_s=49 ranks=4 core_min=3.27 cap_core_min=40.00` — 8% of its cap.

## 2. WHAT KILLED IT, NAMED EXACTLY

At `decomp.log:891-895`, immediately after row 1's `End`:

    Primal min residual 1.042376255e-05
    did not satisfy the prescribed tolerance 1e-08
    Primal solution failed!

DAFoam then raised `AnalysisError("Primal solution failed!")` from
`dafoam/mphys/mphys_dafoam.py:345` (`DAFoamSolver.solve_nonlinear`); OpenMDAO wrapped it as
`'scenario1.coupling.solver' <class DAFoamSolver>: Error calling solve_nonlinear()`; the exception
propagated out of the driver and **`mpirun` terminated all four ranks**. Rows 2, 3 and 4 never
began. **So all four rows read `NO VALUE — NOT A RESULT (row did not complete)`** and the frozen
comparator's `GRADE.txt` closes with `G1R anchor  ANCHOR ROW ABSENT -> whole rung NOT A RESULT`.

The pre-registration **anticipated this branch and priced it correctly**: §6.4 registers
`DIVERGED-TRIM` = *"`AnalysisError`, no `DECOMP_RESULT` line"* → row **NOT A RESULT**, gate
**NOT A RESULT** (arm UNGRADED); and §6.4's rung mapping gives *"no arm produced a value →*
**NOT A RESULT** *— and A2's registered falsifier is again UNGRADED, which is the honest sentence,
not a softer one."* That is the sentence, and it is not softened here.

## 3. THE PART THAT MATTERS: THE PHYSICS PASSED THE GATES. THE PRINT LINE DIDN'T HAPPEN.

Row 1's own residual block and force values are **in the log**, at `decomp.log:874-888`:

| quantity | measured | registered gate | would it have passed? |
|---|---|---|---|
| `CD` | **0.02124797341** | `G1R`: \|CD − 0.02124478277\|/0.02124478277 ≤ 0.5% | **0.015%** — passes, 33× inside |
| `CL` | **0.4999465153** | `G1R`: \|CL − 0.49994884178\| ≤ 5e-4 | **2.33e-06** — passes, 215× inside |
| `CL` vs trim target | same | `G3R`: \|CL − 0.5\| ≤ 5e-4 | **5.35e-05** — passes |
| worst per-equation `finalRes` | **4.652519276e-07** (`nuTilda`) | `G4R`: ≤ **1e-6** | **passes** |
| `DECOMP_RESULT` line | **absent** | `G4R`: exactly one | **FAILS** |

**So the anchor row reproduced A2's anchor to 0.015% in CD and 2.3e-06 in CL, and met G4R's
residual clause with 2.1× headroom. It failed one clause only: the driver's own result line was
never printed, because DAFoam threw first.** The grader is **right** to refuse the row, and it is
**not** rescued here — §6.3's own maxim binds both ways: *bookkeeping never voids physics; physics
never launders bookkeeping.* The row has no value on the record, and the rung is `NOT A RESULT`.

**And the quantity that killed it is the very quantity this pre-registration had already ruled
non-comparable.** §6.2 corrects A2's `G4` precisely because `primalMinResTol` acts on DAFoam's
**normalised total** residual while the log prints **per-equation `finalRes`**, and it registers
`G4R` on the readable quantity instead. The registration got that right — and could not reach it,
because DAFoam's runtime enforces `primalMinResTol` unconditionally and **aborts the process**
rather than returning a non-converged point the driver could grade.

## 4. THE SAME ACCEPTANCE RULE IS BLOCKING TWO ITEMS, AND `nuTilda` IS THE CULPRIT IN BOTH

`1.042376255e-05` — the figure DAFoam calls its *"Primal min residual"* — is **byte-identical to
`nuTilda initRes` on `decomp.log:884`**. The same is true on D6RF10 R3, where the banner figure
`1.391750109e-05` is byte-identical to that log's `nuTilda initRes`
(`D6RF10_GRADE_RECORD.md` §0, commit `cadc459c`). **Two items, two independent logs, two matches.**

In both, the pressure field — the quantity the D6/A2 convergence campaign is actually built around —
is comfortably **below** the campaign's `1.0e-05` accept floor: `p initRes` **5.765826264e-06** here
and **6.3233727e-06** on D6RF10 R3. **The binding obstacle on the A2 MACH wing is the
Spalart–Allmaras `nuTilda` residual, not pressure.**

Stated as a **hypothesis with two strong data points, not an established fact**, because it rests on
a byte-match in two logs and not on reading DAFoam's source: **DAFoam's "Primal min residual" is the
WORST across the transported-equation set, despite its name.** A lane is establishing the definition
from source. If it holds, three consequences follow and each needs its own decision:
1. The open GATE-R-level referral to verification
   (`docs/dafoam/REFERRAL_TO_VERIFICATION_A2_GC_P_GATE_R_LEVEL_2026-09-10.md`, `c5f97bd9`) is asking
   about a **live blocker on running work**, not a bookkeeping nicety.
2. D6RF10's whole ladder was searching pressure-coupling levers (correctors, SIMPLEC,
   under-relaxation) against an obstacle that is **not in the pressure equation**.
3. A2-B2R cannot produce a single row on this box until either the abort is made non-fatal or
   `nuTilda` is driven below `primalMinResTol` — and the latter is a different campaign.

## 5. COST (rule 12)

Registered point **17.8 core-min** (266.5 wall s), cap **40 core-min**
(pre-registration §10). Actual **3.27 core-min** (49 wall s × 4 ranks ÷ 60), = 0.0545 core-h →
**$0.0028 DERIVED, NOT MEASURED** at $0.0513/core-h, reported-by-owner
(`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing). Ratio actual/predicted
**0.184**, and that low figure is **an abandonment, not an efficiency** — it stopped after 1 of 4
rows. **Waste, named separately and not absorbed (charter §6): all 3.27 core-min**, since no graded
value was produced. What it bought instead is §3 and §4 of this record. 0 GPU-h.

## 6. WHAT IS NOT DECIDED HERE

- **No pre-registration is amended and no gate, threshold or lever is moved.** Any route to making
  A2-B2R produce rows that changes a registered quantity needs its own dated amendment before any
  compute; a route that changes none is operational. A lane is enumerating both classes, DRAFT only.
- **Nothing is filed upstream.** The four prepared DAFoam defect classes (D-A/D-A2, D-B/D-B2, D-C,
  D-E) all carry `Status: NOT FILED ANYWHERE`, filing is Sanaa's alone, and whether this behaviour
  belongs to an existing class or a new one is not settled in this record.
- **The rung verdict is not revisited.** `NOT A RESULT`. A successor may buy the rows; this run did
  not.
