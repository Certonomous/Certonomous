# VMFL019 — Transient Flow Near a Wall Set in Motion (Stokes' First Problem): `PASS`

**NOT FILED ANYWHERE.** Nothing here leaves this box (CLAUDE.md rules 7, 8;
`ANSYS_VERIFICATION_CHARTER.md` §8). **SUBMISSIONS PARKED.**

Graded by `ansys-lane-opus`, 2026-08-25T20:27Z, against the pre-registration frozen
and committed BEFORE the run. The lane did not launch this case — it was already on
disk, complete — and did not modify the comparator.

---

## VERDICT: `PASS`

Both gate probes lie inside the frozen 1 % band against the **exact analytic**
Rayleigh/Stokes profile `u(y,t) = U·erfc(y/(2√(νt)))`.

| probe | lab (L3_120) | analytic | relative deviation | inside 1 % band |
|---|---|---|---|---|
| u_x at y = 0.05 m, t = 5 s | 6.16765356837e-3 m/s | 6.170750774519737e-3 m/s | **0.0502 %** | yes |
| u_x at y = 0.10 m, t = 5 s | 3.17007704028e-3 m/s | 3.1731050786291404e-3 m/s | **0.0954 %** | yes |

Reference **category V (code verification)** — an exact closed form, not a code-to-code
number. Source: H. Schlichting & K. Gersten, *Boundary Layer Theory*, 8th ed.,
pp. 126–127, 2000; manual p. 77. **The manual prints only figures .19.2/.19.3 for this
case and no discrete target row**, so the gate is against the analytic value directly —
this was declared in the frozen pre-registration §2, not decided after the fact.
Ansys's own Fluent/CFX curves are figure-only and are **not** the gate.

## Roache triple (rule 5) — `CONVERGING` at both probes

Space and time refined together at ratio r = 2 (Ny 30/60/120; Δt 0.05/0.025/0.0125 s).

| probe | f_coarse | f_med | f_fine | state | observed p | GCI_fine (Fs = 1.25) |
|---|---|---|---|---|---|---|
| y = 0.05 | 6.15750138722e-3 | 6.16441382001e-3 | 6.16765356837e-3 | `CONVERGING` | 1.0933 | 0.0579 % |
| y = 0.10 | 3.16108837043e-3 | 3.16706434421e-3 | 3.17007704028e-3 | `CONVERGING` | 0.9881 | 0.1208 % |

Both triples are monotone, so the GCI is quotable. The observed orders ≈ 1 are the
expected first-order response of the Euler time integration refined in lockstep with the
mesh; they are **not** a noise floor, so the pre-registration §9 fallback that would have
capped this row at `GATE REACHED` **does not fire** and the ceiling `HOLDS`.

## Controls — each checked, not taken from a summary

- **Strict completion (rule 4), per level, evidenced on disk.** `rc = 0` in each
  `RUN_RC.txt`; one `End` line in each `log.icoFoam` (matched by **exact name**, never a
  `log*` glob — a glob matches `log.blockMesh` first); last `Time = 5` == `endTime 5`;
  `U` and `p` present at `endTime`; ExecutionTime count == 5/Δt exactly at every level
  (**100 / 200 / 400**); age guard passed (fields newer than the case's own `0/U`).
- **Planted-zero (rule 3).** 1.234e-3 m/s planted into `u_x` of probe 0 at L3_120 and read
  back from disk: `reader_delta = 1.2339999999999999e-3`. The reader is shown able to see
  a non-zero, so its zero-deviation reading is evidence.
- **Comparator `--selftest`: exit 0**, all checks green, including both gate arms (a
  +2 % perturbation is refused, +0.5 % is admitted) and the classifier's `DIVERGENT` /
  `OSCILLATORY` / `EXACT` branches. A selftest proves the grader, not the case; the case
  itself is evidenced by the completion clauses above.

## Cost and calibration (rule 12)

| | core-minutes |
|---|---|
| pre-registered estimate (§7) | ≈ 0.15 clean |
| frozen cap | 9.00 |
| **actual, measured from `RUN_RC.txt`** | **0.0167** (L1 0.0000 + L2 0.0000 + L3 0.0167) |

Actual/cap = **0.19 %**; actual/estimate = **0.11**. The estimate over-predicted because
the pre-registration deliberately took ~60× slack for an unfamiliar regime under a loaded
box; the attribution is **misprediction (conservative slack), not contention and not
waste** — no level stalled and nothing was thrown away. Dollars at the owner-stated
$0.0513/core-h are **derived, not measured** (the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5): 0.0167 core-min ⇒ ≈ **$1.4e-5**.

## Artifacts on disk

- Run root: `verification/runs/ansys_verification/VMFL019/`, levels `L1_30/`, `L2_60/`, `L3_120/`
- Grading: `verification/runs/ansys_verification/VMFL019/GRADING_VMFL019.json`
- Probes: `<level>/postProcessing/probesU/0/U`
- Pre-registration blob `e303c4dea3d82644e487a11ba173306cabf8d0ec` — **verified equal to
  `HEAD:cases/ansys_verification/VMFL019/PREREGISTRATION.md`** at grading time
- Comparator blob `c20d72fc4e03a431f0d874b943420ca2de1c6a8c` — **verified equal to HEAD**
- Launcher blob `0e86784673c342e88a87f4b4c969a4d30f80ad3d` — **verified equal to HEAD**

Each `RUN_RC.txt` additionally records `prereg_blob=e303c4de…`, so the run itself carries
the identity of the pre-registration it ran under.
