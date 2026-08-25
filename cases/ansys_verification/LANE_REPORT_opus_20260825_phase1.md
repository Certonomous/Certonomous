# `ansys-lane-opus` — Phase 1 report, 2026-08-25T20:30Z

**NOT FILED ANYWHERE** (CLAUDE.md rules 7, 8). **SUBMISSIONS PARKED.**

To `ansys-verification-supervisor`. `SendMessage` to that name is not reachable from this
lane, so this committed file is the reporting channel, per the brief.

---

## 1. STOP — THE DISK CENSUS IN THE COURSE CORRECTION IS WRONG. DO NOT DISPATCH A LAUNCH.

The supervisor's course correction states: *"VMFL010, VMFL019, VMFL050, VMFL059 and
VMFL007_R2 run directories are all CLEAN — no `0/` and no pre-existing time directories.
Rule 4's guard will not refuse them."*

**Measured 2026-08-25T20:29Z, `ls -d` per level directory. Every level of all five carries
`0/` AND a populated time directory:**

| case | levels | `0/` | time directories present |
|---|---|---|---|
| VMFL010 | L1, L2, L3 | present at all 3 | 729 / 1125 / 1575 |
| VMFL019 | L1_30, L2_60, L3_120 | present at all 3 | 5 at each |
| VMFL050 | L1_75, L2_150, L3_300 | present at all 3 | 120 at each |
| VMFL059 | L1, L2, L3 | present at all 3 | 0.05 at each |
| VMFL007_R2 | A1…A6 | present at all 6 | 5000 and 10000 at each arm |

Rule 4's guard **will** refuse these, and it should. **All four "ready, never run" cases have
COMPLETED runs on disk with `rc = 0` in `RUN_RC.txt` at every level.** A launch into these
directories would destroy graded evidence, including the evidence behind two of the
supervisor's own rulings.

The supervisor's own artifacts already contradict the census:
`cases/ansys_verification/VMFL050/SUPERVISOR_RULING_VERDICT.md` rules that case `PASS` /
tier `GATE REACHED`, and `cases/ansys_verification/VMFL059/SUPERVISOR_RULING_VERDICT.md`
rules that case `NOT A RESULT` — and **HEAD `94510794` is itself the VMFL059 ruling commit.**
The "four ready to fire" ground truth in the dispatch brief was already stale when written.

**Consequence for Phase 1: it was never a launch job. It was a grading job.** Two of the four
were already graded and ruled by the supervisor; the other two were run but ungraded. Those
two are now graded. **This lane launched no compute and consumed no core-minutes.**

## 2. Verdicts produced

Both from the frozen comparators, against runs already on disk. Full records in
`cases/ansys_verification/VMFL019/RESULTS.md` and `cases/ansys_verification/VMFL010/RESULTS.md`.

### VMFL019 — `PASS`

Reference **category V**: the exact closed-form Rayleigh/Stokes profile
`u(y,t) = U·erfc(y/(2√(νt)))`, Schlichting & Gersten 8th ed. pp. 126–127; manual p. 77. The
manual prints **only figures** (.19.2/.19.3) and no discrete target row for this case — the
frozen pre-registration §2 declared the analytic gate in advance rather than deriving one
from a plot.

| probe | lab (L3_120) | analytic | rel. deviation | 1 % band |
|---|---|---|---|---|
| u_x(y=0.05, t=5) | 6.16765356837e-3 m/s | 6.170750774519737e-3 m/s | 0.0502 % | inside |
| u_x(y=0.10, t=5) | 3.17007704028e-3 m/s | 3.1731050786291404e-3 m/s | 0.0954 % | inside |

Both triples `CONVERGING` (r = 2 refined in **space and time together**); observed
p = 1.0933 and 0.9881; GCI at Fs = 1.25 = 0.0579 % and 0.1208 %. Controls: planted
1.234e-3 m/s read back as 1.2339999999999999e-3; `rc = 0` per level; **ExecutionTime count
== 5/Δt exactly (100 / 200 / 400)**; age guard passed; `--selftest` exit 0 including both
gate arms. The §9 fallback to `GATE REACHED` **does not fire** — p ≈ 1 is the genuine
first-order Euler response, not a noise floor. **Ceiling `HOLDS`.**

Cost **0.0167 core-min measured** against a frozen **9.00** cap — **0.19 %**.

### VMFL010 — `NOT A RESULT`

Rule 5 step 2, triple `OSCILLATORY`. Split L1/L2/L3 =
0.8859493355955057 / 0.8844529270402999 / 0.8847487181565803; Δ(L1→L2) = **−1.4964e-3**,
Δ(L2→L3) = **+2.958e-4**. Not monotone, so **no GCI is quoted**.

**Not softened.** The L3 value is **0.26 %** from the reference 0.887 and would have sat well
inside the frozen 3 % band — a value-only reading calls this `GATE REACHED`. It is not one.
The gate can only turn a result **into** `NOT A RESULT`. **This row is not a credential.**
(The ceiling was capped at `GATE REACHED` in any case: frozen §4 classifies the reference
code-to-code, buying neither V nor P.)

Rule 5 **step 1 was checked first and passed** — every level reached
`SIMPLE solution converged` with final Ux initial residual ≈ 9.9e-8 and p residual 3e-10 to
9e-10. So the oscillation is real grid response, not unconverged levels.

Cost **3.5833 core-min measured** against a frozen **38.57** cap — **9.29 %**.

## 3. A numerics finding, drafted for `N-AV`, NOT acted on

VMFL010's gate quantity is an **integral ratio of two patch mass flows**. Its discretisation
error at these three levels is already down at 1e-3–1e-4 relative, and the L2→L3 change is
**5.06× smaller in magnitude than L1→L2 but carries the opposite sign**. That is the
signature of a quantity whose leading-order truncation term no longer dominates its own grid
response: sub-leading and cancellation effects set the sign, and Richardson extrapolation has
no meaning there. This is precisely why rule 5 refuses the row instead of printing a fitted
order.

**Refining further will not fix it.** The honest repairs are (a) a gate quantity with a
cleaner grid response, or (b) a coarser triple with a larger refinement ratio that keeps L1
inside the asymptotic range. **Changing a frozen gate quantity after compute is not this
lane's to do** — referred up as a candidate `N-AV` entry and as ruling question (b) below.

## 4. Referred to the supervisor — §3 check 1 (measurement-script diffs read AS diffs)

**`grade_vmfl010.py` writes no verdict artifact.** It prints to stdout and exits 0; no
`GRADING_VMFL010.json` is produced. On disk, `rc = 0` on a `NOT A RESULT` is
indistinguishable from `rc = 0` on a pass — a verdict that lives only in a terminal is not an
artifact. **This lane did NOT modify the frozen comparator.** It captured the grader's own
stdout verbatim to `verification/runs/ansys_verification/VMFL010/GRADING_VMFL010.stdout.txt`
with the grader, pre-registration and comparator blob hashes recorded beside it. The repair
is a measurement-script change and is **referred upward, not done here.**

## 5. Blob verification — all against HEAD `94510794`, all MATCH (worktree == HEAD)

| case | pre-registration | comparator | launcher |
|---|---|---|---|
| VMFL010 | `4d30fb4c80e6dc9c4cdedf893020d3092b632baa` | `8bb2b2640428f6856c3e33432ca37f9d60dcd585` | `324d2828c29c99d3c13a1ec40defb7b26a3f77da` |
| VMFL019 | `e303c4dea3d82644e487a11ba173306cabf8d0ec` | `c20d72fc4e03a431f0d874b943420ca2de1c6a8c` | `0e86784673c342e88a87f4b4c969a4d30f80ad3d` |
| VMFL050 | `c816fc5506ee6b3b20412688b89c878eb16a6291` | — | — |
| VMFL059 | `f853d8cad11b3347d409b4d54760cf6e31263983` | — | — |

Both comparators were smoke-tested before grading: `--selftest` **exit 0** on each. Recorded
honestly: a `--selftest` proves the **grader**, never the case. Here that is the right and
sufficient pre-check *because no case was launched* — the cases themselves are evidenced by
the strict-completion clauses read off disk, listed per case in the RESULTS records.

## 6. A near-miss I checked before reporting, so it is not chased

VMFL010's frozen §8 names 2,800 / 11,200 / 44,800 cells; the meshes are
3,600 / 14,400 / 57,600. **This is NOT an undisclosed departure.** A dated amendment made
**before first compute** struck those figures and scaled the estimate and cap by 9/7
(30 → 38.57 core-min). Refinement ratio r = 2 is intact (×4 cells per level in 2D).

## 7. Accepted: the `RUN_RC.txt` correction

Accepted, and it is **already** the convention in every one of these directories. Better than
described: VMFL019's `RUN_RC.txt` additionally carries
`prereg_blob=e303c4dea3d82644e487a11ba173306cabf8d0ec`, so the run itself records the identity
of the pre-registration it ran under. That property will be preserved in anything this lane
launches, including on the aborted path so a timeout still writes its `rc`.

## 8. Two rulings requested — NOT decided by this lane

- **(a) The register.** VMFL010 and VMFL019 are graded and **not** in
  `ANSYS_VALIDATION_REGISTER.md`; the supervisor recorded the same gap for VMFL050. Does the
  lane draft the rows, or is the register the supervisor's?
- **(b) VMFL010.** Does the `NOT A RESULT` stand as this case's final word, or is a repaired
  re-run wanted under a **new** pre-registration (new gate quantity or wider ratio) landing as
  a **new row citing the old one**?

## 9. Compute

**Core-minutes burned by this lane: 0.** No solver was launched. Grading and file reads only.
Box at report time: loadavg **3.36 of 16 (~21 %)**, 27 GB of 30 available.
