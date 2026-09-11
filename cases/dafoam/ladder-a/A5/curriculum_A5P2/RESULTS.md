# A5P2 — RESULTS. **THE A5 U-BEND PLATEAU IS BROKEN, AND THE OBJECTIVE NEVER MOVED.**

Pre-registration frozen `94b808fe46672ecde03cfc1b36e707d2686aa800`. All five arms ran under the frozen launcher and were graded by the frozen `a5p2_grade.py` (md5 `a02f7d0e0c4392b01e18bbaa5071d293`), **every arm exit 0 — no grader refusal, every planted control passed.** Run root `/home/ubuntu/certonomous-runs/A5P2-ubend-plateau`, 4,800 hexahedra, np=4, cpuset 12-15.

| arm | the one change | `p` initRes(5000) | `Bounding` | `TP1−TP2` | verdict |
|---|---|---|---|---|---|
| P0 | none — control | 2.056815e-04 | 0 | 52.34517755 | `GATE FAIL` |
| P1 | SIMPLEC (`consistent yes`) | 5.931624e-05 | 0 | 52.34522042 | `GATE FAIL` |
| **P2** | **`nNonOrthogonalCorrectors` 0→2** | **1.448577e-08** | 0 | 52.34509736 | `GATE FAIL` |
| P3 | p-relaxation 0.30→0.70 | 3.376481e-04 | 0 | 52.34619774 | `GATE FAIL` |
| P4 | `nuTilda` relaxation → 0 (diagnostic) | 1.051843e-01 | 0 | 51.81317123 | `NOT A RESULT` (`solver_rc=1`) |

**NO ARM ACHIEVED `BREAK`.** `BREAK = G1 AND G2`; P2 clears **G1** by 1,420× and fails **G2** — its last-decile spread is `1.686e-06`, between the `1.0e-03` convergence requirement and the `1.0e-06` new-plateau falsifier, so it is graded `GATE FAIL — indeterminate drift`. **That is the registered outcome for that region and it was not invented afterwards.**

**1. THE REGISTERED PREDICTION ON P2 IS FALSIFIED, IN THE INFORMATIVE DIRECTION.** P2 was registered **before the run** as a predicted **NO-BREAK** — a deliberate discriminating negative, on the reasoning that a mesh at max non-orthogonality **3.512°** cannot be limited by non-orthogonal correction. It is the arm that moved the residual, by **14,199×**, and its `p` solve now takes **53 inner iterations against P0's 3**. A fixed point that survived tightened linear tolerances, a tenfold iteration extension and SIMPLEC was cleared by two correctors on a nearly-orthogonal mesh.

**2. AND THE RESULT THAT MATTERS MORE: THE OBJECTIVE IS INVARIANT.** Across the four valid arms `TP1−TP2` spans **52.34509736 … 52.34619774** — a range of **1.1e-03, i.e. 2.1e-05 relative** — while `p` initRes spans **1.449e-08 … 3.376e-04, a factor of 23,309.** **The pressure residual moved four orders of magnitude and the answer did not move at all.** So the `2.06e-04` plateau was **never holding the solution away from convergence**; it was an artefact of missing non-orthogonal correction in the pressure equation. **The pre-registered prediction that `TP1−TP2` would stay within `1e-05` of P0 across P2 is CONFIRMED at `8.0e-08` relative.**

**3. `nuTilda` IS THE BINDING PHYSICS, AND P4 IS THE EVIDENCE.** P4 — the only arm that touches the SA equation — is the only arm whose objective moves, by **0.532 (1.0 %)**, and the only one whose solver failed (`rc=1`). **Hammer the pressure equation and the answer is unchanged; freeze the turbulence equation and the answer moves.** This is consistent with `primalMaxRes` sitting on `nuTilda` (3.62e-04) in every arm.

**4. REPRODUCIBILITY, unforced.** A5P2's P0 and P2 reproduce A5P's to the printed precision — `2.056815e-04` and `1.448577e-08` in both independent executions.

**COST:** 19.4 core-min measured across the five arms against a registered 22.7 estimate and a 68 cap — **ratio actual/predicted 0.855**, in line with this lab's habitual ~15 % under-run. `$0.0166` **derived at $0.0513/core-h, not measured** (the box cannot read its own billing).

**WHAT THIS DOES NOT ESTABLISH.** It is a plateau ladder, not a grid-convergence study, and **no GCI is claimed**. Whether A5's grid triple (4,800 / 38,400 / 307,200, r=2, ratio exactly 8.000) now satisfies Case Protocol §5's ten-times rule is **UNMEASURED** — P2 gives an iterative error four orders below the old plateau, which is the prerequisite, but the level-to-level difference has not been measured and until it is the triple stays unregistered.
