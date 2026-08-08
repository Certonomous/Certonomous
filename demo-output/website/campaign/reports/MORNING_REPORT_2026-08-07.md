CERTONOMOUS MORNING REPORT
Date:       2026-08-07
Assembled:  2026-08-07T22:12:35Z
Sections:   6 of 6
Missing:    none

## 1. SPEND

SPEND, 2026-08-06 to 2026-08-07
Last night:     0.000 core-minutes (basis: gross) across 0 runs recorded in the ledger
Of which:       0.000 useful, 0.000 wasted (basis: gross)
Cleaned:        0.000 core-minutes (basis: cleaned; 0 stall row(s) removed by the 3600 second rule)
Left running:   3 solver-shaped process(es) in the process table at assembly: sudo docker run --rm --name s1inv_eval007 --cpus=2 --memory=22g -e DAFOAM_SUBPC_TYPE=lu -v /home/ubuntu/certonomous-runs/S1-cbfs-reinversion ...; docker run --rm --name s1inv_eval007 --cpus=2 --memory=22g -e DAFOAM_SUBPC_TYPE=lu -v /home/ubuntu/certonomous-runs/S1-cbfs-reinversion:/mnt ...; mpirun --allow-run-as-root -np 4 python runScript.py -task compute_totals -betafile beta_cur.npy -gradout grad_eval007.npy -primalTol 1e-8
Week to date:   0.000 core-minutes (basis: gross; from 2026-08-03, the Monday of this ISO week)
Dollar spend:   not readable from this instance, see waiting list

Basis, per the compute budget charter section 2: gross sums every ledger row with a timestamp in the stated window; cleaned is gross minus the rows the stall rule matches (a row over 3600 wall seconds is host stall, scripts/self_audit.py). Last night is 2026-08-06 00:00 UTC to 2026-08-07 00:00 UTC. The stall rule matched 0 row(s) in the night window, so gross and cleaned are the same figure there. The week figure is gross; its cleaned counterpart is not printed because the audit reports the week's stall contamination itself.
The ledger records wall seconds per row and no rank count, so rows are counted at one rank and these core-minutes are wall-minutes, a lower bound. Runs not recorded in the ledger are not counted here; the newest ledger row is dated 2026-07-29T11:17:07Z. 1 torn line(s) were skipped and are counted in no figure.

Source: demo-output/website/mega-batch/ledger.jsonl

## 2. LADDER POSITIONS

Rung sense, per section 2 rule 1: the tables below are the lettered program tracks with numbered cases; the per-case maturity climb and the mesh refinement ladders live inside the case records the rows cite. The source board carries no moved-last-night field, so none is printed here.

**Ladder A - DAFoam verification and reproduction** (columns reproduced: Rung, Case, Status; the headline measured result column is in the source)
| Rung | Case | Status |
| --- | --- | --- |
| A1 | NACA0012 incompressible, official tutorial | **COMPLETE; ~~FD-verified~~ CD/shape FAIL against the shipped toolchain under the current standard (sign-flipped idx6); cause found and fixed in a local patch, 2026-08-01 - see note below the FD table** |
| A2 | MACH tutorial wing (3D) | **COMPLETE, optimization run; ~~the FD verification is NOT currently re-runnable (2026-08-01)~~ *(superseded 2026-08-02: B-7 closed - the 14% spread was a wrong-script error, the published verification re-runs digit-for-digit and the regrade is done; PASS re-measured, see the 2026-08-04 update above)*** |
| A3 | ONERA M6 transonic | **primal UNCONVERGED; adjoint blocked at every mesh size** |
| A4 | Ahmed body 25 deg | **gradient ~~CONDITIONAL~~ → PASS *(superseded 2026-08-02: the 10.04% was the `scotch` decomposition, not the gradient - see the 2026-08-04 update above)*, supervisor sweep CONFIRMED 2026-08-04 (`dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md`, commit 27d25762); primal drag WITHDRAWN** |
| A5 | U-bend internal flow | ~~running~~ *(stale cell, superseded)* **COMPLETE; FD verdict FAIL against the shipped toolchain; cause found and fixed in a local patch, 2026-08-01 - see note below the FD table** |
| A6 | CRM wing (wing-alone; DPW4 wing-body rejected on time-box grounds), transonic | **COMPLETE, converged primal, matches published tutorial baseline** |

**Ladder B - closure literature with adjoints**
| Rung | Status | Result |
| --- | --- | --- |
| B1 | **COMPLETE** | Ranked reproduction plans written; benchmark clone and public leaderboard located on this box |
| B2 | **COMPLETE, verified** | Uncorrected duct baseline reproduced to 0.16% and 0.64% |
| B3 | running | The field inversion itself |
| B4 | queued | Feed findings back into the closure track |

**Ladder C - closure challenge**
| Rank | Entry | Overall |
| --- | --- | --- |
| **1** | **ours, unsubmitted (round 5, scored locally)** | **0.0566** |
| 2 | Reissmann, Fang, and Sandberg | 0.0595 |
| 3 | Wu and Zhang | 0.0624 |
| - | ours, unsubmitted (round 4, superseded) | 0.0654 |
| 4 | Liu, Wang, Zhao, and Xiao | 0.0737 |
| 5 | Montoya, Oulghelou, and Cinnella | 0.0779 |

**Ladder D - background**
| Item | Status |
| --- | --- |
| D1 mega batch | Running, 3 workers, single-instance lock in force. Session count and 0 failures tracked in the runner log; morning count is the true count |
| D2 queue refill | **6 proposals drafted and style-validated, 755 core-min costed** |
| D3 nightly retro | Queued for end of night |

Source: demo-output/website/ACTIVE_RESEARCH.md

## 3. GATES

| act | gate | reference | measured | deviation | verdict | artifact |
| --- | --- | --- | --- | --- | --- | --- |
| Cylinder vortex shedding, Re 100 | Strouhal vs Roshko-Williamson correlation | 0.1590 | 0.1578 | 0.77% | PASS | `mission-output/cylinder-vortex-shedding/transcript.md` |
| Supersonic wedge, M 2.0, 15 deg | Oblique-shock angle vs theta-beta-M relation | 45.344 | 44.693 | 1.44% | PASS | `mission-output/supersonic-wedge/transcript.md` |
| Supersonic cone, M 2.35, 10 deg | Conical shock angle vs Taylor-Maccoll | 26.737 | 27.309 | 2.14% | PASS | `mission-output/supersonic-cone/transcript.md` |
| Diamond airfoil, M 2.0, 7.125 deg | Wave drag vs shock-expansion theory | 0.03633 | 0.03624 | 0.26% | PASS | `mission-output/diamond-airfoil/transcript.md` |
| Hypersonic cylinder, M 8 | Shock standoff vs Billig correlation | 0.4152 | 0.4181 | 0.70% | PASS | `mission-output/hypersonic-cylinder/transcript.md` |
| Ahmed body, 25 deg slant | Drag vs Ahmed/Ramm/Faltin SAE 840300 (frontal basis) | Cd 0.285 | Cd 0.3041 | 6.7% | SOLVER-BACKED | `mission-output/ahmed-body/transcript.txt` |
| NASA wall-mounted hump | Separation / reattachment x/c vs NASA experiment | sep 0.665, reatt 1.100 | sep 0.6544, reatt 1.2534 | -1.6% / +13.9% | VALIDATED | `mission-output/nasa-hump/transcript.txt` |
| ONERA M6 wing | Primal residual vs its own tolerance (intended gate, Cp at 7 spanwise stations vs AGARD AR-138, NOT evaluated) | 1e-08 | 1.02e-06 | did not satisfy | UNCONVERGED | `mission-output/onera-m6/transcript.txt` |
| CRM wing-body | Drag vs DAFoam CRM_Wing tutorial, Cd 0.02090 +/-2% | 0.0209 | 0.020901 | +0.007% | VALIDATED | `mission-output/crm-wingbody/transcript.txt` |

9 of 9 acts have run; 9 carry a graded number.

The Ahmed body row: the source directs readers to demo-output/website/campaign/AHMED_BODY_RECONCILIATION.md before narrating it.

Source: demo-output/website/campaign/NINE_ACT_GATE_TABLE.md

## 4. FD TABLES

The consolidated view, reproduced from the source. Per-component tables live in the case records the rows cite; the sources read carry no machine-readable record of which rung moved last night, so no per-rung movement table is printed and the consolidated view stands alone.

| Rung | derivative | analytic vs FD, relative error | grade |
| --- | --- | --- | --- |
| A1 | geometric constraints wrt shape | **4.4e-14 to 1.4e-10** | not stated in source row |
| A1 | CD wrt flow parameter | **0.232%** | PASS* |
| A1 | CL wrt flow parameter | **0.232%** | PASS* |
| A1 | CL wrt shape | **1.67%** | PASS* |
| A1 | CD wrt shape | **11.43%** on the difference-vector norm, but the two gradient magnitudes agree to **0.451%**. **FAIL against the shipped toolchain** (sign-flipped idx6; 634% under the real seed). *Patched local IDWarp (2026-08-01), rotations ON, real seed: idx6 → 5.54e-04% sign agreeing; idx0/idx1 11.92%/11.58% → 1.23e-05%/1.26e-05%; idx7 1.31e-06%; idx4 1.47e-04%. Stock still fails* | FAIL |
| A4 | CD wrt rear-slant shape | **10.04%**, adjoint 0.21821, FD 0.24258. ~~**CONDITIONAL** under the current standard.~~ *(Superseded 2026-08-02: the 10.04% is a `scotch`-decomposition artifact - 1.10% shipped at np=1 (the single graded configuration of record, per `dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md` W-3, commit 27d25762), 0.00054% patched under `simple` at np=4. **PASS**, supervisor sweep CONFIRMED 2026-08-04 (`dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md`, commit 27d25762).)* It was graded PASS against the calibrated band, which is retired; two other records graded it CONDITIONAL before the decomposition finding | PASS / CONDITIONAL |
| A5 | objective wrt shape, 27 components | **46.6%** aggregate; only 5 of 27 within the 12% band; **2 sign flips** - **FAIL against the shipped toolchain**. *Patched local IDWarp (2026-08-01), rotations ON, real seed: idx8 207.0% flip → 3.0e-06, idx17 121.6% flip → 7.0e-06, signs agree; all 27 stock-objective components rel_err 0.0000 (before-worst 80.79%). Stock still fails* | FAIL |

A grade without an asterisk is the source row's own verdict wording, reproduced; where a row carries more than one verdict word the row's full text beside it says which stands.
A grade marked * is recomputed from the row's stated relative error against the current standard (PASS at 5 percent or better with no flagged component, CONDITIONAL from 5 to 15 percent, FAIL above 15 percent or on any sign-flipped component), per section 7 rule 3.

Source: demo-output/website/ACTIVE_RESEARCH.md

## 5. REFILLED QUEUE

Count by status: proposed 62, approved 49, approved-queued 0, dismissed 13, done 98.
Refill totals: 111 open items (proposed, approved, approved-queued), 11038 core-minutes costed over the 47 rows carrying an estimate; 64 rows carry none.
Rank order is the ranking function's: expected knowledge gain per core-minute descending, then case-folded objective, then id (sdk/chief_engineer/agenda.py).

| Rank | id | objective | source_kind | est_core_min | cost_basis kind | status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | w5-audit-every-citation-in-the-submission-draft | Check every quotation in the submission draft against a source on disk before it is sent | challenge | none | estimate | proposed |
| 2 | w5-hlpw6-ai-ml-focus-group-is-the-cheap-way-in | Establish whether HLPW-6's AI/ML technology focus group is a route into the workshop that needs no CFD, and what an entry to it would consist of | challenge | none | estimate | proposed |
| 3 | w5-autocfd5-scouted-and-declined | Record AutoCFD5 as scouted and declined on physical grounds, so its deadline does not pull compute toward it | challenge | none | estimate | proposed |
| 4 | w5-rescope-the-high-lift-entry-on-physics | Rescope the high-lift entry on the two findings that decide it, and stop citing price | challenge | none | estimate | proposed |
| 5 | w5-decide-what-cannot-be-submitted | Rule on entries the lab can prepare and cannot send, before their compute is spent | challenge | none | estimate | proposed |
| 6 | w5-decide-what-cannot-be-sent-before-it-is-run | Rule on entries whose submission route is closed before their compute is committed | challenge | none | estimate | proposed |
| 7 | w5-what-else-does-the-importer-unlock | Survey which public workshop entries are now reachable, given topology decides and not the workshop | challenge | none | estimate | proposed |
| 8 | w5-the-wedge-extrapolates-to-an-impossible-angle | Correct a filmed act that fails two guards and prints the milder one | gate | none | estimate | proposed |
| 9 | w3-valve-band-never-adjudicated | Correct the one stored band that reports itself conclusive without ever facing a guard | measurement | none | estimate | proposed |
| 10 | w3-a-verdict-a-mesh-can-move | Decide what a credential may claim when an independently generated mesh moves it across its own band | measurement | none | estimate | proposed |
| 11 | w3-where-settling-scatter-belongs | Decide which channel carries settled-state scatter, and make the two filmed acts agree with it | measurement | none | estimate | proposed |
| 12 | w3-non-orthogonality-belongs-in-the-numerical-channel | Make mesh non-orthogonality a stated input to the numerical uncertainty, since it now predicts divergence | measurement | none | estimate | proposed |
| 13 | w3-narrate-the-strongest-signal-not-the-first | Order every declined verdict by how strong its evidence is, not by where it sits in a list | measurement | none | estimate | proposed |
| 14 | w3-a-declined-ladder-still-publishes-an-envelope | Rule on whether a credential may print an envelope taken from a ladder the certifier declined | measurement | none | estimate | proposed |
| 15 | w6-a-measurement-that-raised-the-price | Add the first calibration point where measuring made an item more expensive, not less | ledger | none | estimate | proposed |
| 16 | w6-idle-is-a-dispatch-failure-not-a-capacity-one | Close the loop between an approved item and a machine with nothing to do | capability | none | estimate | proposed |
| 17 | w6-a-queue-that-drains-itself-needs-a-ceiling | Decide the standing budget a self-dispatching queue may spend without asking | ledger | none | estimate | proposed |
| 18 | w6-the-lab-uses-a-tenth-of-its-box | Find out why the lab sustains 1.4 of 14 usable cores and decide whether that is a choice | ledger | none | estimate | proposed |
| 19 | w6-forecast-the-approved-backlog | Forecast the approved backlog against measured throughput before it is dispatched | ledger | none | estimate | proposed |
| 20 | w6-the-box-is-oversubscribed-now | Give the lab a concurrency limit, since it has gone from a tenth of its box to over it | ledger | none | estimate | proposed |
| 21 | agp-527efc1cbb44 | Harmonic-balance cycle solve | capability | none | estimate | approved |
| 22 | w6-the-box-went-from-a-tenth-to-full | Measure what changed when utilisation went from 1.4 cores to saturation, and whether the throughput followed | ledger | none | estimate | proposed |
| 23 | w2-mit-access-list | Open the paywalled-paper list for Katie MIT library access and work the open-access seed list down | reading | none | estimate | approved (standing authorization) |
| 24 | w6-a-rank-count-needs-cells-per-rank | Qualify the parallel rule, which inverts at thin decompositions | ledger | none | estimate | proposed |
| 25 | w5-close-the-secco-2021-citation-gap | Read the primary IDWarp reference and close the one disclosed gap in the novelty claim | reading | none | estimate | approved (standing authorization) |
| 26 | w6-papers-price-the-cheap-step | Record the cost gap between what closure papers report and what reproduction actually takes | ledger | none | estimate | approved (standing authorization) |
| 27 | w6-a-recipe-that-cannot-be-replicated | Record which recipes cannot be rebuilt, because one of four attempts could not be meshed at all | ledger | none | estimate | proposed |
| 28 | w6-an-estimate-without-a-rank-count | Refuse a compute estimate that does not state the rank count it was measured at | ledger | none | estimate | proposed |
| 29 | w6-the-largest-miss-was-on-an-unapproved-item | Refuse to spend on an item that was never approved, and count what already was | ledger | none | estimate | proposed |
| 30 | w4-aflr3-pyramid-convention | Report the grid-format convention that the published documentation states incorrectly | capability | none | estimate | proposed |
| 31 | w6-estimates-enumerate-cost-not-prerequisites | Require an estimate to name what must exist before the work can start | ledger | none | estimate | proposed |
| 32 | w6-a-cost-without-a-rank-count-is-not-a-cost | Require every compute estimate to state the rank count it assumes | ledger | none | estimate | proposed |
| 33 | agp-a3cc843ce473 | Resolve the shedding | capability | none | estimate | approved |
| 34 | w6-the-ledger-understates-a-failed-cold-solve | Spend the cost of a cold solve that raises, which currently costs the ledger nothing | ledger | none | estimate | proposed |
| 35 | agp-37da30f972b3 | Unsteady fluid-structure interaction | capability | none | estimate | approved |
| 36 | w7-a-print-interval-is-a-measurement-instrument | Audit every archive claim that rests on what a solver printed rather than what it did | report | none | estimate | proposed |
| 37 | w7-a-top-score-reachable-by-writing-one-key | Audit every graded level for one that can be reached without the evidence it claims | report | none | estimate | proposed |
| 38 | w8-a-label-is-fixed-where-it-is-emitted | Audit every place a surface renders an identifier as if it were a label | report | none | estimate | approved (standing authorization) |
| 39 | w7-weekly-claim-audit | Build the rolling re-verification of published claims against primary evidence as a scheduled script | report | none | estimate | approved (standing authorization) |
| 40 | w7-verify-reachability-from-outside | Check every surface the operator needs from outside the box, not from the box | report | none | estimate | approved (standing authorization) |
| 41 | w6-charter-clauses-resolve-to-their-evidence | Check that every charter clause citing an incident resolves to a file or a commit that exists | report | none | estimate | approved (standing authorization) |
| 42 | w7-instruction-echo-is-a-check | Check that every stated instruction is echoed and answered on camera | report | none | estimate | approved (standing authorization) |
| 43 | w6-generator-claims-are-per-case | Check which mesh generator a case actually uses before attributing a defect to one | report | none | estimate | approved (standing authorization) |
| 44 | w7-two-studies-moved-with-no-value-change | Decide whether a record timestamp should move when nothing it records did | report | none | estimate | proposed |
| 45 | w7-solver-stub-detector | Detect a solver launch that produced only a launcher stub and no run | report | none | estimate | approved (standing authorization) |
| 46 | w8-certificate-interval-lesson | Distil the certificate confidence-interval defect into a charter clause and a preflight check | report | none | estimate | approved (standing authorization) |
| 47 | w8-a-guard-states-its-sample | Find every guard in the stack whose tolerance is measured over more than it guards | report | none | estimate | approved (standing authorization) |
| 48 | w7-claim-an-item-before-working-it | Give the docket a claim, because three collisions have now happened | report | none | estimate | proposed |
| 49 | w7-two-agents-one-question | Make concurrent work on one docket item visible before it is duplicated | report | none | estimate | proposed |
| 50 | w7-an-unauditable-record-is-invisible | Make the audit see the records it currently skips | report | none | estimate | proposed |
| 51 | w7-every-run-writes-to-the-registry | Make the solve registry cover every solver run, or state plainly what it does not cover | report | none | estimate | proposed |
| 52 | w8-a-premise-can-be-false-and-still-worth-filing | Record how often a proposal premise turned out false, and what that says about how they are drafted | report | none | estimate | proposed |
| 53 | w8-a-category-can-be-the-error | Record that the unit of analysis is itself a hypothesis, from the committee-grid result | report | none | estimate | proposed |
| 54 | w8-right-verdict-wrong-reason | Record the near miss where a gate held for a reason that turned out to be arithmetic | report | none | estimate | approved (standing authorization) |
| 55 | w7-a-run-that-invoked-the-wrong-script | Record which script produced a result, and check it against the one the case documents | report | none | estimate | proposed |
| 56 | w7-exit-zero-is-not-a-solve | Refuse to read a solver exit status as evidence that a case converged | report | none | estimate | proposed |
| 57 | w7-the-m6-act-cannot-be-verified-at-all | Register the ONERA M6 act in the replay verification, which currently cannot drive it | report | none | estimate | proposed |
| 58 | w7-s4-and-s5-are-not-watching | Repair or withdraw the two monitor rules the archive replay showed are not working | report | none | estimate | proposed |
| 59 | w8-a-ruling-cites-what-it-protects | Require a ruling to name the artifact it claims to protect, and check that it does | report | none | estimate | proposed |
| 60 | w8-a-ruling-states-its-stake-and-checks-it | Require a ruling to name the consequence it rests on, and to verify that consequence | report | none | estimate | proposed |
| 61 | w7-a-record-written-names-the-item-it-closes | Require a study record to name the docket item it closes, or say that it closes none | report | none | estimate | proposed |
| 62 | w8-an-audit-attribution-is-a-claim | Require an audit finding to name the file it inspected, and check it before the finding travels | report | none | estimate | approved (standing authorization) |
| 63 | w8-a-style-rail-drops-a-proposal-on-a-slash | Stop the proposal style rails reading a quoted numeric ratio as a file path and dropping the proposal | report | none | estimate | proposed |
| 64 | w8-a-builder-that-infers-its-contents | Write down that a packager which infers its contents will miss anything built at run time | report | none | estimate | proposed |
| 65 | w3-race-bracket-on-a-local-fit | Bracket the race act's angle grid on a fit local to the peak, and re run the act on the tightened band | measurement | 6 | measured | proposed |
| 66 | w3-locationinmesh-lands-on-a-symmetry-plane | Move the generated case's mesh seed off the symmetry planes it currently sits exactly on | measurement | 10 | measured | proposed |
| 67 | w3-the-race-band-is-two-and-a-half-times-too-wide | Re-run and re-verify the race act with its bracket on a local fit | measurement | 10 | estimate | proposed |
| 68 | w2-the-duct-zero-stated-as-a-structural-limit-with-a-falsifier | State the duct secondary-flow zero as a structural limit of the linear eddy-viscosity class, defended from the integrity basis the lab has read, with a pre-registered falsifier run before the claim is published | gate | 10 | estimate | approved (standing authorization) |
| 69 | c5-duct-velocity-scale-transfer | Give the duct correction a genuine Reynolds-transfer test by generating our own duct training data at a second Reynolds number |  | 12 | measured | approved (standing authorization) |
| 70 | credential-layer-coverage-gate | Add a boundary layer coverage gate to every credential that grades on drag alone | measurement | 20 | estimate | approved (standing authorization) |
| 71 | dafoam-simplec-comparison-audit | Audit every comparison between a DAFoam result and a plain OpenFOAM baseline for the silently dropped consistent pressure correction | measurement | 25 | estimate | approved (standing authorization) |
| 72 | w1-ahmed-family-asymptotic-ladder | Build one asymptotic refinement ladder for the Ahmed family on the 35 degree slant, the half of this item that is still open; the 25 degree half is answered in the negative by R4 and is out of scope | gate | 27 | estimate | approved (standing authorization) |
| 73 | w3-a-verdict-protocol-for-mesh-draw-sensitive-credentials | Adopt a verdict protocol for band-edge credentials, with replicate meshes required before a verdict, scatter printed beside the value, and an interval stated where the scatter crosses the band | capability | 20 | measured | proposed |
| 74 | r8-how-often-does-convergence-reporting-mask-divergence | Establish how often a solver's convergence reporting can mask a run that did not converge, by classifying every run this lab holds with an automated checker and separately auditing what a sample of published papers on our own validation cases actually state about convergence | measurement | 30 | measured | approved (standing authorization) |
| 75 | w3-refinement-rungs-varies-two-knobs | Make a generated refinement ladder vary one knob, and make the guard check comparability rather than distinctness | measurement | 30 | estimate | proposed |
| 76 | dafoam-shape-derivative-step-size-study | Establish whether the shape derivative disagreement against finite difference is a step size artefact by sweeping the difference step across several decades | measurement | 35 | measured | approved (standing authorization) |
| 77 | w3-run-uq-studies-still-caps-every-rung-at-300 | Give the curriculum ladders the cell-count-derived iteration cap the TMR ladders already have | measurement | 40 | estimate | proposed |
| 78 | dafoam-adjoint-memory-scaling-law | Measure the adjoint peak memory as a function of cell count so case feasibility can be predicted before a run rather than discovered by failure | measurement | 40 | measured | approved (standing authorization) |
| 79 | w3-qcr-constitutive-term-for-rank2-parity | Add the untrained QCR2000 quadratic constitutive term (c_r = 0.3) the rank-2 closure entry carries, so a duct-score comparison against 0.0455/0.0399 can ever be like-for-like | capability | 30 | estimate | approved (standing authorization) |
| 80 | w3-beta-on-omega-destruction-model-patch | Expose a per-cell beta on the SST omega DESTRUCTION term, so the roadmap's original Stage 1 target and the Wu, Zhang and Zhang reproduction become buildable | capability | 30 | estimate | proposed |
| 81 | r5-a5-second-gradient-defect | Explain the single component -- idx16 of shapexUpper -- that the corrected warp moves further from the finite difference on the U-bend, now that 26 of the other 27 are clean | gate | 60 | estimate | approved (standing authorization) |
| 82 | w1-hump-challenge-conditions | Spawn the NASA hump at the closure challenge conditions as the successor to the passed steady gate | gate | 60 | estimate | approved (standing authorization) |
| 83 | r5-warp-linearisation-workaround | Establish whether the mesh-warp linearisation defect can be avoided in practice by expressing an opposing-direction combination design variable as a weighted set of single-point variables, and whether the resulting gradient then verifies | capability | 45 | measured | approved (standing authorization) |
| 84 | r7-locate-the-strouhal-onset | Pair the middle rung of the cylinder ladder so the Strouhal sensitivity onset is located rather than bracketed | gate | 78 | measured | proposed |
| 85 | w4-the-compressible-abort-is-ours | Diagnose the compressible solver abort, which is not a grid problem and was filed as one | capability | 60 | estimate | proposed |
| 86 | w5-probe-the-item-that-is-a-third-of-the-backlog | Establish whether the largest approved item is feasible before its cost is committed | capability | 60 | estimate | proposed |
| 87 | w3-explain-the-residual-2-7-percent | Explain the field-inversion gradient residual, now that clipping and convergence are both eliminated | measurement | 90 | estimate | proposed |
| 88 | w3-find-an-invertible-closure-case | Find a closure-relevant case this lab can actually invert on | measurement | 90 | estimate | approved (standing authorization) |
| 89 | r2-closure-coefficient-uncertainty | Give the model channel a measured parametric basis: propagate published k-omega SST closure-coefficient intervals through solves on the motorcycle held mesh and report the resulting drag envelope as coefficient-interval evidence alongside the current transferred estimate | reading | 60 | estimate | approved (standing authorization) |
| 90 | w5-degenerate-point-derivative-check | Make a reusable check that evaluates every adjoint at its own degenerate point, and run it across the stack | capability | 60 | estimate | approved (standing authorization) |
| 91 | w3-vspaero-model-form-band | Quantify the vortex-lattice model-form error, now the largest term in the race error budget | measurement | 90 | estimate | approved (standing authorization) |
| 92 | w2-tbnn-duct-reynolds-generalisation | Rebuild Ling's tensor-basis neural network and run his own Reynolds-number-generalisation experiment on the closure challenge's duct family: train on AR_1, AR_3, AR_5 and AR_10 at Ret 180, hold AR_7_Ret_180 for hyper-parameters, and predict the three scored duct cases without opening them | reading | 60 | estimate | approved (standing authorization) |
| 93 | r4-m6-wall-treatment-plateau | Test whether the ONERA M6 primal residual plateau at 1.02e-06 is caused by wall resolution sitting in the buffer layer, by re-running the case on a wall-resolved mesh (yPlus below 1) and on a clean wall-function mesh (yPlus above 30) and observing whether the plateau moves | gate | 90 | measured | approved (standing authorization) |
| 94 | r6-cylinder-wake-topology-onset | Locate the Reynolds number at which a two-dimensional cylinder wake stops producing a time-mean recirculation bubble, by running the single intermediate rung that halves the interval in which the transition is now known to lie | gate | 110 | measured | approved (standing authorization) |
| 95 | tmr-naca0012-complete-ladders | Complete the NACA 0012 ladders on the TMR-distributed grids: 225x65 and 449x129 at alpha 10, then full ladders at alpha 0 and 15, with observed order and Richardson values against the published finest-grid results | challenge | 150 | estimate | approved (standing authorization) |
| 96 | w1-f5b-pitching-naca0012 | Complete the F5b pitching NACA 0012 dynamic-stall physics and gate rungs | gate | 120 | estimate | approved (standing authorization) |
| 97 | r4-coarse-adjoint-prolongation | Determine whether a gradient computed on a coarse adjoint mesh is accurate enough to drive optimization on a fine primal mesh, by measuring gradient direction agreement (cosine similarity, not just magnitude) between coarse and fine adjoints on the one case where both are affordable | measurement | 120 | estimate | approved (standing authorization) |
| 98 | closure-duct-tensor-basis-carrier | Replace the duct correction's scalar-invariant inputs with a tensor-basis carrier, because the invariants are provably three-dimensional on a duct while the basis tensors are not, and grade it on the suggested duct validation case before any test score exists | gate | 120 | estimate | proposed |
| 99 | w4-a5-second-defect | Isolate the U-bend adjoint defect using the link-by-link method that closed A1 | capability | 90 | estimate | approved (standing authorization) |
| 100 | w5-rotations-off-mesh-quality-price | Price the useRotations=False workaround before anyone is told to use it | capability | 90 | estimate | approved (standing authorization) |
| 101 | r4-band-tightening-hump | Determine how tight the model-form uncertainty band on hump reattachment can be made while still containing the experiment, by replacing the extremal anisotropy limiting states with physically weighted perturbations and measuring the containment/width trade-off curve | challenge | 200 | estimate | approved (standing authorization) |
| 102 | w3-valid-family-for-ahmed-35-cube-and-sail | Build a single-knob production-recipe ladder for the cube and the NACA 0015 sail (ahmed_35 is being built under W1) | measurement | 160 | estimate | proposed |
| 103 | dpw8-v1-oat15a-committee-grid-primal | Run the DPW-8 V1 ONERA OAT15A transonic verification case on the committee-supplied Rizzi grid family, levels 1 through 4, to a converged primal at a single angle of attack, and report a grid-convergence trend on lift, drag and surface pressure against the workshop's own gridding and numerics rulebook | challenge | 240 | estimate | approved (standing authorization) |
| 104 | r5-perturbation-destroys-its-own-measurand | Test whether the anisotropy-perturbation uncertainty method destroys the very quantity it is built to bound, by establishing at what perturbation magnitude the separation bubble stops being a single closing structure and whether a converged solution exists beyond that point at all | challenge | 250 | estimate | approved (standing authorization) |
| 105 | naca0012-derive-reference-then-relayer | Derive the NACA 0012 finite-wing reference, then re-run its ladder with the boundary layer resolved | measurement | 200 | measured | approved (standing authorization) |
| 106 | naca4412-converge-lift-coefficient | Identify and remove the remaining driver of lift non-monotonicity on the NACA 4412 refinement ladder so the ladder reaches the asymptotic range | measurement | 220 | estimate | approved (standing authorization) |
| 107 | w4-a-pivoting-factorization-for-the-blocked-adjoints | Measure whether a pivoting-capable factorization converges the CBFS adjoint, on the case where a direct solve of its own dumped system already works | capability | 240 | estimate | proposed |
| 108 | w5-idwarp-singularity-free-rotation-patch | Patch getRotationMatrix3d to the singularity-free rotation form and show the gradient comes out right with rotations still ON | capability | 240 | estimate | approved (standing authorization) |
| 109 | w1-dpw5-hex-three-level-ladder | Run the two upper DPW5 hex levels and build the first committee-grid convergence ladder | gate | 400 | estimate | proposed |
| 110 | closure-duct-field-inversion | Reproduce the rank two entry's field inversion on the square duct cases, inverting a correction field on the turbulence destruction term through the discrete adjoint | reading | 420 | estimate | approved (standing authorization) |
| 111 | hlpw6-testcase1-coarse-grid-entry | Prepare a candidate entry for the sixth High-Lift Prediction Workshop test case 1 by running the published CRM-HLS blind case on the coarsest committee grid of 2.66 million cells across the six specified angles of attack, and assess whether the result is strong enough to be worth Katie approving an approach to the workshop organisers | challenge | 6390 | estimate | approved (standing authorization) |

Source: demo-output/website/agenda/docket.json

## 6. WAITING LIST

Everything verified blocked on her, from the consolidated blockers file; entries the file marks CLOSED are not waiting and are not listed. Decisions waiting on her live in the same file and ride the same rows.

| id | What is blocked | Verified blocked how | Unblock action | Since |
| --- | --- | --- | --- | --- |
| B-1 | Billing alarm and spend cap cannot be confirmed from this instance | Ops gate item 1. BLOCKED - verification, not assumption | attach an instance role with `cloudwatch:DescribeAlarms` and `ce:GetCostAndUsage` (read-only is sufficient), or paste the configured numbers directly and they will be recorded as reported-by-owner rather than measured. | not dated in source |
| B-2 | Ledger cannot be synced off-host | Ops gate item 3. BLOCKED both paths | either an instance role with `s3:PutObject` on a backup bucket, or a deploy key / PAT for the private repo. The moment either exists, the hourly sync goes in - the backup script and rotation already work. | not dated in source |
| B-3 | TMR NACA 0012 closure run - approval ambiguity, NOT a technical block | The cap itself is unknown | confirm the spend cap (B-1), or say "yes, run the 480 core-min TMR closure". | not dated in source |
| B-4 | External reachability cannot be settled from this box | `w7-verify-reachability-from-outside`. BLOCKED on the half that matters. Measured 2026-08-01 06:3x UTC | 1. From the operator laptop, off any Certonomous network: `curl -sS -o /dev/null -w '%{http_code}\n' --max-time 8 http://16.58.201.228:8080/` and the same for `:8765`. Two lines of output settle it permanently, and a 200 or a 000 both go on the record with the vantage point named. 2. Or attach a read-only instance role with `ec2:DescribeSecurityGroups`, which turns this into a check the box can run for itself every week. | 2026-08-01 |
| B-5 | Four papers this box cannot open. The two it could, it has read | `w2-mit-access-list`, `w5-close-the-secco-2021-citation-gap`. Opened 2026-08-01. Waiting on Katie's library, not on this box | open the list, work the four remaining entries top down, and paste back the section named beside each. The list is shorter and every entry left on it now carries a DOI plus the evidence that the free route was tried and failed. Nothing else in the reading program waits on this. | 2026-08-01 |
| B-6 | `closure-duct-field-inversion` is blocked on this box, and restating its cost does not change that | Docket rank 178 of 180, `est_core_min` 420.0, approved 2026-07-31. Recorded 2026-08-01 while working the "these four are affordable" batch | root-cause the CBFS adjoint's iteration-0 NaN/Inf. Until then the item cannot spend its budget no matter how affordable the budget is. It is left `approved` rather than dismissed because the objective - 62.9% of the deficit to the rank-two entry sits in the two duct cases - is unchanged and worth doing the moment the adjoint runs. | 2026-08-01 |

Source: demo-output/website/agenda/BLOCKERS.md
