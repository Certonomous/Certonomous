# Certonomous Case Protocol Charter

Version 1.0, dated 2026-09-10. Title as dispatched: **CASE PROTOCOL CHARTER — v1.0**; rendered here in the house style `docs/charters/README.md` §2 asks for (a title line, then a `Version N.M, dated YYYY-MM-DD` line). No line of the dispatched header's content is dropped.

**Status:** IN FORCE, effective immediately, 2026-09-10.
**Author:** Sanaa (owner), her own session turn, ~16:50Z 2026-09-10, session identity katie@certonomous.com. Recorded [SANAA-DIRECT], text reproduced byte-exact from her message; the only additions are this header and the provenance block at the foot.
**Scope (her words):** every 3D case and every Navier-class case.
**Relationship to CLAUDE.md:** this charter is her directive and governs its scope; its closing clause states a scoped exemption from the cap-stop in CLAUDE.md rule 12 and this charter's own §4 (see the provenance block). CLAUDE.md itself is not edited by any agent (rule 9).

Her text, byte-exact, begins after this line and ends before the provenance block:

# [SANAA-DIRECT] THE CASE PROTOCOL: ONE PATH, EVERY CASE, NO PROSE

Applies to every 3D case and every Navier-class case (SUBOFF, MRF impeller, porous radiator, booster, blunt body, scrubber, M6, CRM, the 3D adjoints). Effective immediately. A case that does not follow this path is not a case.

## 0. The principle
One deterministic path from registration to certificate. Each stage has a script, an exit condition, and a fixed action on failure. Supervisors report state, not narrative. The lab decides for itself: every failure is resolved from the lessons ledger and the numerics knowledge base by the supervisor that owns the case, and the decision is recorded with its basis. Nothing waits on me. I read the record when I return; I do not sit in the loop.

## 1. Setup: select everything before anything runs
The setup script produces a complete case from the registration and the knowledge base, with no free choices left to an agent:
- Geometry: admitted through the gate (units, watertightness, normals, regions, feature resolution, curvature-based surface resolution for 3D). Refusal names the deficiency and stops.
- Mesh: strategy from the case class; resolution from physics (y+ for the chosen closure and Reynolds number, cells across every named feature, refinement zones where shocks, wakes and separation are expected); three similar levels from one script at ratio 1.5 to 2; birth certificate with hash on each level.
- Model and numerics: closure from the knowledge base for this flow class with its known limit written into the case; schemes, relaxation, tolerances, correctors and wall treatment from the class defaults. Solver tolerance strictly tighter than any gate that reads its output (the T23G2Rn2 rule: a tolerance equal to a gate voids the rung).
- Boundary conditions and domain: from the registration; farfield or tunnel placement per the domain rules; blockage stated.
- Cost and routing: intrinsic estimate, cap at three times the estimate, workers and waves, CPU or GPU by the routing rule, all written to the registration.
- Gates: reference tier named (exact, correlation, measured), tolerance and pass bands frozen, comparator pinned by hash. Nothing below is run until the freeze check passes.
Exit condition: a complete case directory, a birth certificate per mesh level, a registration record with hashes. Any missing item is supplied by the setup script from the class defaults and the knowledge base; if the knowledge base has no entry for this flow class, the supervisor registers the class default with its provenance marked "class default, first use" and proceeds. A missing item never waits.

## 2. Bug check: prove the case can run before spending on it
Automatic, under one minute, no compute worth counting:
- checkMesh on every level: quality within the registered gates or the case stops.
- Dictionary and schema validation: every fvSolution, fvSchemes, boundary and material file parses and every referenced patch, region and field exists.
- Boundary-condition closure: every patch has a condition for every field; no default that silently fills a hole.
- Dead-lever audit: every setting the registration claims is present in the files that the solver reads.
- Instrument check: every reader that will grade this case detects a planted perturbation through the real path; a reader that cannot see its plant fails the case closed.
- Dry run: solver initialized, one iteration, exit status read. A wrapper may never manufacture an exit status; rc is read from the process, not inferred from a marker.
Exit condition: all checks green. On any red: the failing check, the file, and the line are written to the record; the fix is taken from the lessons ledger when a lesson matches; when none matches, the supervisor applies the smallest change that turns the check green, records it as a new lesson with the check that would have caught it, and continues. No case waits on a red bug check.

## 3. Smoke run: cheap, short, predicted
- Coarsest level, a registered fraction of the iterations or time (typically 5 to 10 percent), residual and force or temperature monitors on.
- Predictions registered before it starts: residual behavior, first-iteration cost, the sign and order of the graded quantity.
- Exit condition: residuals falling, no bounds violated, monitors alive, cost per iteration within the estimate's band, predictions met. Pass means the full run launches automatically. Fail means one registered change from the escalation ladder for the failed prediction's class, then smoke again. Two failed smokes on the same cause: the supervisor climbs one rung (mesh, then numerics, then model) using the numerics knowledge base, registers the successor, and the case continues. Three failures on the same cause: the case is parked as NOT A RESULT with the cause class and the three actions tried, the lesson is written, and the supervisor moves to the next case. It does not wait.

## 4. Full run: detached, monitored, survivable
- Launched detached from any agent: the runner daemon owns it, the process is parented to init, the autograder and the monitor are parented to init with it. The fleet dying does not touch the solver. Checkpoints written at the registered interval so a kill resumes from committed state.
- Monitor conventions, fixed: residual targets per equation, absolute bounds on fields, stationarity of the graded quantity over its window, linear-solver saturation, cost per iteration against the estimate, wall time against the cap.
- Monitor actions, fixed and pre-registered:
  - residual growth past the bound, or a field outside its bounds: stop.
  - plateau above target with a stalled linear solver: stop.
  - coherent oscillation with a fixed period in the graded quantity: stop, mark "physics voting unsteady."
  - cost per iteration beyond twice the estimate: stop, mark machine or case cause from the per-iteration timing and residual decay.
  - cap reached: stop, NOT A RESULT, never a raised cap.
- On any stop: diagnose by class (oscillation, growth, plateau); apply the one registered first action for that class from the escalation ladder (continuation from a converged neighbor, relaxation reduction, pseudo-transient, then transient re-registration); resume from checkpoint; record the action and the outcome. One change per run. Never the same action twice on the same state. Two stops on the same cause: climb the ladder. Ladder exhausted: park as NOT A RESULT with the full action history and the lesson, move on. The supervisor owns the whole ladder; no stop reaches me.
- Completion: exit status read, artifacts hashed, cost written. Completion is not certification.

## 5. Grade: the gates, then the family
- Readers run (already instrument-tested in stage 2); values read from files; every number traces to a file.
- Gates evaluated against the frozen comparator; verdict written as one of PASS, GATE FAIL, NOT A RESULT, with the cause class for any non-pass.
- Then the family: medium and fine levels launched by the same daemon with the same monitor, from the coarse solution as initial condition where admissible; observed order and GCI computed; iterative error verified at least ten times smaller than the level-to-level difference; order out of range adds a level automatically; band attached to every number.
- Certificate assembled from the record: reference, tolerance, band, what was not checked, hashes of geometry, mesh, settings and comparator. Or the refusal, with its reason.

## 6. Reporting: state, not prose
- Every stage writes one status line to the case record: stage, verdict, one number, one cause if not green. Supervisors relay those lines; they do not narrate.
- The board is per-case state files plus a generated rollup; a supervisor never asserts what a run is doing; it reads the process table and the case record.
- Anything an agent relays that it did not read from a file carries VERIFY.
- Weekly: cases graded, cases NOT A RESULT with their cause classes, crashes, mean cost miss, wall time per certified case. These five numbers are the health of the lab.
- Decisions made without me are the norm. Each is one line in the record: the situation, the lesson or knowledge-base entry it was decided from, the action, the outcome. A decision with no basis in the ledger or the knowledge base is recorded as a new lesson, not as a question.

## 7. Fronts
Until the protocol has produced ten certified cases: cfd on SUBOFF and M6; dafoam on the 3D adjoints; heat-transfer on T4e; ansys on its live queue; verification on the freeze hook and the instrument tests this protocol needs; closure paused. No new families.

## 8. What parks a case, and what never reaches me
- Parks the case (NOT A RESULT, lesson written, next case): refusal at admission that no lesson can repair, three failed smokes on one cause, a cap, a monitor ladder exhausted.
- Never stops the case: the fleet dying, a supervisor's context ending, a board being stale, my absence.
- Reaches me: nothing during the day. Only two things ever come to the desk, and only in the weekly: a spend that would exceed the standing envelope, and a decision that would change a frozen gate after registration (which is never taken by a supervisor, and which I will almost always refuse). Everything else is the supervisors' to decide, from the lessons and the knowledge base, on the record.

## 9. Standing authority
Supervisors have full authority over: mesh, model, numerics, escalation actions, successor registrations inside the envelope, parking a case, writing lessons and knowledge-base entries, and correcting their own sections. They do not have authority to raise a cap on a running case, to change a frozen gate, or to publish a number that failed its gate. Within that, they act; they do not ask. and for all these 3D cases that still need to run, i dont want to see any budget gates ( time or money). Bc i want to shoot them so we at least have hard 3D demos to show and then we can go back to having some restraint

---
## Provenance and the chief's reading (NOT her words; correctable by her)
- Recorded by a records lane on the chief's instruction, 2026-09-10T16:50Z (stamp from `date -u` in the writing invocation), zero compute.
- **Closing clause versus §4 and CLAUDE.md rule 12.** Her closing sentence exempts "all these 3D cases that still need to run" from budget gates, time or money, until hard 3D demos exist, after which "some restraint" returns. The chief reads this as: for the 3D demo cases now queued or to be queued, no wall-time cap and no core-minute cap STOPS the run; §4's "cap reached: stop, NOT A RESULT" and rule 12's "an overrun stops the run" are suspended for that scope only. Every such run is still COSTED in its registration (the estimate is calibration data, not a gate) and its actual is still landed in `docs/COST_CALIBRATION.md`, because she asked for the estimate-versus-actual comparison at every completion (rule 12) and nothing in this directive withdraws it. The exemption ends when she says restraint returns; supervisors record which runs ran under it.
- **What this charter does not change:** rule 7 (SUBMISSIONS PARKED), rule 8 (private), rule 9 (a blanket is not a per-item read; no agent may change a frozen gate), the GPU cost-basis rule, and the private-index protocol.
- **Fronts as dispatched by the chief at ~16:55Z:** cfd builds the stage-1 to stage-4 scripts as the first instances on SUBOFF and M6; verification builds the freeze hook, the stage-2 instrument tests, the per-case state-file and rollup format (converging with V-119); dafoam the 3D adjoints; heat-transfer T4e; ansys its live queue; closure PAUSED after committing its state.
