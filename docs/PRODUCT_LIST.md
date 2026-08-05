# IV. PRODUCT — canonical list (supervisor-maintained)

Protocol (Katie, 2026-08-04): an item is crossed `[x]` only when FULLY done, with evidence linked. Every
cross-off adds a new item. `[-]` = attempted, blocked or failed with diagnosis. `[~]` = done in substance,
pending supervisor adversarial verification (assume wrong until defended). Updated continuously; the
day's changelog is at the bottom.

Priority order: 1. DAFoam investigation · 2. Closure benchmark challenge · 3. Remaining items ·
4. New items · 5. Literature review.

## 4A. Closure modeling line
- [x] Stage 0 do-no-harm gate on the corrector (never score below raw RANS).
- [-] Stage 1 FIML field inversion (beta on SST omega-destruction) via DAFoam adjoint, FD-verified; first target NASA hump.
      Capability half DONE and FD-verified (2.67%, 5,000 DVs, step-independent — `dafoam/ladder-b/S1_FIML_FIELD_INVERSION.md`).
      CONDITIONING BLOCKER BROKEN ON CBFS (2026-08-04, commit 1cd44c04; supervisor sweep CONFIRMED on all five axes,
      incl. independent FD at a never-published cell to 0.021% — `VERIFICATION_cbfs_unblock_supervisor_sweep.md`,
      9c19ccc8; docket item done at 185.0 core-min): rebuilt libDASolver
      with ASM sub-block complete LU (env DAFOAM_SUBPC_TYPE=lu, image dafoam-subpclu:v1) converges the CBFS beta adjoint
      (21,000 DVs, KSP reason 2) with FD 0.059–0.199% vs the 2.67% bar, zero sign flips — first converged, FD-verified
      field-inversion gradient on a closure-relevant case. Regression control reproduces -9 with the switch off.
      fixedPoint route refuted at zero compute (SA-only); "unreachable at runtime" belief corrected (L-34). 185.0/240
      core-min. Hump now blocked on convergence RATE vs memory envelope, not singularity — Richardson-wrapped attempt
      staged for a fresh budget.
      Note: DAFoam's native beta hook is on omega *production*; destruction-term hook needs a model patch
      (`w3-beta-on-omega-destruction-model-patch`).
- [x] Stage 2 learn the closure from inverted fields (GP line optional pre-registered GP-vs-trees bake-off).
- [x] Stage 3 pre-registered zero-shot transfer test.
- [-] C2 error decomposition vs the top-4 gap. Decomposition DONE and thrice-corrected (`closure_challenge_C2_error_decomposition.md`):
      real deficit is the ducts (62.9% of gap to rank 2), not alpha_05. Full closure blocked on the same adjoint conditioning failure.
      Regime-model route CLOSED 2026-08-04: 11 of 21 training cases qualify (gate-declined framing), model trained
      test-blind, but pre-declared hurt cap failed on the declined test cases' parametric sibling — NO-GO, nothing scored,
      round 4 stands. Mechanism finding (L-33): regime retraining moves the baseline-quality boundary (~0.07 → ~0.055)
      instead of removing it. Successor candidate (second-stage ~0.055 threshold) filed, needs its own pre-registration
      (`closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md`).
- [x] M1 methods taxonomy [764 lines, 0 fabricated citations].
- [ ] M2 reproduction ladder: FIML -> TBNN -> SpaRTA. SpaRTA rung has its first real result: CBFS correction-field
      reproduction inside the binding factor-two band (0.39753 vs published 0.22703, no adjoint, 27.7 core-min, 2026-08-01);
      both SpaRTA docket items closed 2026-08-04 at 0 new core-min (`W5_SPARTA_GATE_STATUS.md`). FIML rung blocked on
      conditioning; TBNN duct Re-generalisation approved: `w2-tbnn-duct-reynolds-generalisation`.
- [ ] M3 hybridization experiments (each with a named hypothesis).

## 4B. Closure benchmark challenge
- [x] ~~Current 0.0741 vs rank-4 target 0.0779~~ SUPERSEDED: entry of record is **round 4, 0.0654, rank 3 of 5**
      (Reissmann 0.0595 · Wu&Zhang 0.0624 · **us 0.0654** · Liu 0.0737 · Montoya 0.0779). Gap to rank 2: 0.0030.
      Best-on-board 5 of 8 cases; last only on NASA_2DWMH. 5 scoring calls used (self-imposed discipline; no benchmark limit).
- [x] alpha=15,AR14 status: still best-on-board, but AR_14 lead collapsed to 0.00003 after round 4's un-reverted duct regression —
      must not be reported as a comfortable win.
- [x] Find out challenge policies / whether Certonomous can submit. DONE (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §1–§4):
      steward Ryley McConkey (MIT); no eligibility clause, no fee, no deadline, no scoring limit; leakage rule audited in code, not violated.
      Two flagged ambiguities: company name in Authors column; no license on benchmark/training-data repos.
      → NEW ITEM (from this cross-off): **Submission send package** — Katie fills author names + reference URL, approves,
      sends the email (with the alpha_05-rows-are-baseline disclosure); ask steward about the two ambiguities in the same email.
- [ ] Update the Active Research board with movement. REOPENED: board still headlines round 3 / 0.0676; round 4 never
      written to it. Update dispatched 2026-08-04.

## 4C. 2D case families
- [x] F2 transonic RAE2822.
- [x] F3 supersonic exact-theory suite [all three gates PASS].
- [x] F5a unsteady cylinder Strouhal [shipped, 0.7% at Re=100].
- [ ] F5b pitching NACA 0012 dynamic stall vs AGARD CT (docket `w1-f5b-pitching-naca0012`, approved, 120 core-min).
- [ ] F5c backward-facing step reattachment vs Driver-Seegmiller. OOM + gradient blowups.
- [x] F4 hypersonic blunt body vs Billig standoff (+ SWBLI stretch).
- [-] F6a NASA hump [gate reached]. Pass with *; overpredicted bubble length (k-SST diffusion suspect).
      1. Try different models. 2. If confirmed → epistemic-uncertainty showcase. Also `w1-hump-challenge-conditions` (approved, 60).
- [ ] F6b periodic hills vs ERCOFTAC.
- [-] F6c duct vs DNS. Captures 0% of anisotropy — structural model deficiency, not us. Research-result candidate;
      `closure-duct-tensor-basis-carrier` proposal (120) is the constructive follow-up.
- [ ] NACA 0012 wall credential re-grade: W3 found the published Cd (0.01205, outside ±30% band) is not reproducible —
      3 of 4 same-recipe meshes land inside the band (`campaign/W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md`). Needs a verdict protocol
      for mesh-draw-sensitive credentials. [added 2026-08-02 by W3, adopted onto list 2026-08-04]

## 4D. 3D case families
- [x] F1 ONERA M6 transonic wing vs AGARD Cp stations.
- [ ] F10 real 3D viscous RANS batch family (replace the panel-method stand-in).
- [ ] F8 NREL Phase VI wind turbine (MRF, then transient).
- [ ] AIAA DPW: study public data/methodology, then attempt CRM/DPW-class case (converged primal first).
      A6 wing-alone primal now matches DAFoam's published tutorial baseline to 0.0067% (provisional — see 4E A6).
      `w1-dpw5-hex-three-level-ladder` proposed (400).
- [ ] B52: figure out why mesh doesn't converge smoothly (docket `agp-1dec50b65c2f` 8th rung, 20 core-min).

## 4E. DAFoam ladder — investigation root-caused; regrades in progress
- [-] A1 NACA 0012 drag min, FD-verified adjoint. FAIL against SHIPPED toolchain stands, but fully root-caused:
      IDWarp 2.6.2 `getRotationMatrix3d` degenerate-rotation guard differentiates to a hard zero at the undeformed baseline
      (upstream `mdolab/idwarp#57`, open five years). 4-line patch collapses idx6 634% sign-flip → 5.5e-4%
      (`ROOTCAUSE_getRotationMatrix3d.md`, `PATCH_getRotationMatrix3d.md`, LESSONS L-29).
      SUPERVISOR SWEEP 2026-08-04: CONFIRMED on all four axes — math re-derived independently, scripts clean,
      idx8 flip+collapse reproduced with an independent driver, upstream anchor traced
      (`VERIFICATION_rotation_patch_supervisor_sweep.md`, commit 6782d33a). Upstream filing prepared, unfiled — **Katie's call**,
      now with a defended basis.
- [x] A2 3D wing tutorial optimization vs documented result. HUGE; demo anchor. Re-verified 18/18 `check_totals` rows
      from a pristine clone; B-7 reproducibility blocker closed (wrong-script error, 2026-08-02).
- [-] A3 ONERA M6: primal DONE and validated (CD=0.02299556, Cp vs AGARD AR-138). Adjoint hard-blocked:
      `DIVERGED_BREAKDOWN` at every mesh size incl. 21,840 cells with >20 GB free — conditioning, not memory
      (14.17-decade diagonal spread, `R5_ADJOINT_CONDITIONING.md`).
- [x] A4 Ahmed-body adjoint: verdict moved UP to **PASS (1.10% at np=1 stock — the graded configuration of record)**.
      CROSSED 2026-08-04: sweep confirmed (27d25762), records reconciled (56a5a911), board gates cleared (01e18303).
      Successor items per protocol: the decomposition-mechanism item below, plus the A4-novelty research proposal (in drafting). The 10% error was DAFoam's
      default `scotch` decomposition (np=1 0.34% / np=4 scotch 8.95% / np=4 simple 0.00054%; converged wrong answer;
      A1/A2/A5 decomposition-invariant). Mechanism NOT identified — hanging-node hypothesis refuted backwards.
      SUPERVISOR SWEEP 2026-08-04: CONFIRMED — every cell re-extracted, np=2 independently re-run to every printed digit,
      face re-classification exact (`VERIFICATION_A4_decomposition_supervisor_sweep.md`, commit 27d25762; 2.9 core-min).
      Documentation defects D-1/D-2/W-1/W-3 filed as L-32; case-record reconciliation in progress.
      Graded configuration: np=1 stock, 1.10%. Primal SIMPLEC mismatch is separate and disclosed.
- [-] A5 internal-flow adjoint (U-bend). FAIL against shipped toolchain, cause fully identified = same rotation-guard bug
      (solve-free pure-geometry test reproduces idx8 207% flip component-by-component; standalone stock reproducer:
      13/27 components >30%). "No clue why" is obsolete.
- [-] A6 CRM wing-alone primal: CONVERGED below 1e-8, CD=0.0209014, matches published tutorial to 0.0067%. Provisional:
      temperature-residual ~8.5e8 signature (same precursor as A4's field collapse) filed open. Adjoint not attempted (memory wall).
- [x] Carry the warp patch to the blocked rungs. CROSSED 2026-08-04 at 0.0 of 180 core-min (247ac4a7): survey showed
      every warp-blocked rung already carries stock-beside-patched; still-blocked rungs die structurally upstream of
      warpDeriv or bypass IDWarp (`W4_CARRY_TO_BLOCKED_RUNGS.md`). Stale A2 board cell struck (L-32 pattern caught live).
      → NEW ITEM: **Adopt the patched-vs-shipped grading policy** — drafted as PROPOSED in DAFOAM_CASE_STATUS.md
      (shipped-toolchain verdicts, labeled patched grades under strict provenance, fork adoption reserved to Katie);
      supervisor review pending the discriminator agent's commit.
- [x] A4 decomposition-defect MECHANISM — CROSSED 2026-08-04 (elevated to priority-1 on Katie's instruction, same day):
      NAMED at subsystem level and sweep-CONFIRMED on all five axes. DAFoam v5's parallel matrix-free transposed-Jacobian
      product (`calcJacTVecProduct` global tape) is not the transpose Jacobian of the discrete residual under scotch
      decomposition — GMRES converges exactly on the wrong system (cross-residual 329x ||b|| under the serial operator,
      independently reproduced at 328.8x; localized to x-momentum rows on partition-interface cells; simple-slab 5,000x
      smaller). Prediction pre-registered and HELD. Records: `DISCRIMINATORS_A4_decomposition_mechanism.md` (49ab2816),
      `VERIFICATION_A4_mechanism_supervisor_sweep.md` (8e0a08bc). UPSTREAM REPORT PREPARED, not filed — **Katie's call**,
      does not overclaim per the sweep. 57.1 core-min total incl. honestly-ledgered coloring-arm overrun.
      → NEW ITEM (from this cross-off): **Line-level attribution** — instrumented libDASolver rebuild to trace the
      reverse tape over processor-boundary halo exchange (proposal territory per the gate's bounding clause).
      Reach items stay open (`w4-does-the-decomposition-defect-reach-other-cases`, 120; `w4-decomposition-invariance-is-a-gate`, 60).

## 4F. interFoam / marine line
- [-] F7a dam break vs Martin-Moyce. Sign flip when mesh refined. Must diagnose.
- [ ] F7a-fix: diagnose and re-gate (free-surface stack must pass its cheapest case before hulls).
- [ ] F7b Wigley hull wave resistance.
- [ ] F7c DTMB 5415 or KCS vs open workshop data.
- [x] NavyFOAM availability/license evaluated; vanilla interFoam for now (stated in docket).

## 4G. Research directions & lab self-proposals
- [x] One-click agenda operational (costed proposals, click approvals, ranked morning digest).
- [ ] TMR ladder: flat plate DONE (+0.29% vs CFL3D); bump-in-channel next; NACA 0012 attempt-2 time-boxed —
      insane aspect ratio, must understand before proceeding (`tmr-naca0012-complete-ladders`, 150).
- [ ] Valve F9 real pulsatile solve.
- [x] Standards docs: MESH_STANDARD, MONITOR_STANDARD (v1.3 incl. S12 unsettled-stop, landing 2026-08-04), INNOVATION_STANDARD.

## 4H. AI charters — iterated daily
- [x] Goals & research-proposal charter.
- [x] Literature-review charter (0 fabricated citations stays the standard).
- [x] Case-selection charter (hardness floor).
- [x] Verification charter.
- [x] Result-priority charter (draft v0.2; decision sheet D0–D7 awaiting Katie's rulings).
- [x] Compute-budget charter (P-6.1 spot-vs-on-demand blocked on AWS read-only role).
- [x] Escalation charter (P-7.1 free-spend thresholds: no number set — needs Katie).
- [x] Reporting charter: morning-report format FROZEN (v2.0, 2026-07-31, 12 sections + enforcement via `scripts/self_audit.py`).
      → ~~P-8.1 emitter half~~ CROSSED 2026-08-04: emitter built at `scripts/morning_report.py`, 26 tests green,
      first real report `campaign/reports/MORNING_REPORT_2026-08-04.md`, commit e9ef5a78.
      → NEW ITEM (from this cross-off): **Morning report runs itself** — schedule the emitter to run each morning,
      and make the spend ledger catch the day's runs (ledger's newest row was 5 days stale on first emit;
      connects to open docket item `w7-every-run-writes-to-the-registry`).
- [ ] Problem-research protocol (NEW 2026-08-04, Katie's directive): liaison researches every breakage online
      (literature, upstream issues, forums) and maintains a living systematic-method doc. First draft dispatched.

---

## Changelog

### 2026-08-04
- CROSSED: 4B policy question (submission draft complete, no eligibility bar) → added "Submission send package (Katie)".
- CROSSED: 4H reporting-charter format (v2.0 frozen) → added "P-8.1 emitter half".
- CROSSED: 4E A4 (PASS confirmed by supervisor sweep, records reconciled) → successors: A4 decomposition mechanism
  item + A4-novelty proposal.
- CROSSED: 4H P-8.1 emitter (built, 26 tests green, first report emitted) → added "Morning report runs itself
  + spend ledger catches the day's runs".
- FILED: three research proposals (2eb00350): A4 three-discriminators (W4, 45), duct structural-limit with falsifier
  (W2, 10), mesh-draw verdict protocol (W3, 20).
- MILESTONE: fiml-adjoint-conditioning-unblock CLOSED, sweep-confirmed — first converged, FD-verified field-inversion
  gradient on a closure-relevant case (CBFS). → NEW ITEM: **Run the Stage 1 inversion on CBFS** — beta inversion toward
  Bentaleb LES with the verified sub-LU adjoint; needs a costed proposal + pre-registration first (SLSQP-style loops are
  100+ gradient evaluations; estimate from the measured 16.2 core-min/adjoint before approving).
- LITERATURE: Wu/Zhang deep-read landed (393ad74f) — beta-on-destruction CONFIRMED (eq. 2/5/6, f_d shield coeff 8 not 20);
  full patch spec written (both destruction lines, DAkOmegaSST.C:745 AND :870, else PC inconsistent with residual).
  THREE C2 corrections found: paper trains hump+CBFS (hump is a scored test case — paper protocol would be in-sample);
  "zero-shot to DUCT" is our inference, not theirs; rank-2 model = SST-QCRC (beta + untrained QCR2000, c_r=0.3) — beta
  patch alone does not buy parity. New proposal w3-qcr-constitutive-term-for-rank2-parity filed; corrections dispatched.
  QCR capability doubles as the duct structural-limit falsifier — two lines converge on one build.
- UPDATED: 4B scores to round 4 (0.0654, rank 3/5); 4E rewritten rung-by-rung from `DAFOAM_CASE_STATUS.md`/`PROOF.md`
  (A4 → PASS pending verification; A1/A5 root-caused; A3 conditioning-blocked; A6 primal provisional-pass).
- ADDED: 4C NACA 0012 wall-credential re-grade; 4E warp-patch carry + grading policy; 4E A4 mechanism; 4H problem-research protocol.
- REOPENED: 4B Active Research board update (round 4 never posted).
- DISPATCHED: adjoint-conditioning unblock (approved docket item), SpaRTA frozen-RANS, alpha_05 regime-model check,
  rotation-patch + A4 verification sweeps, liaison research on DIVERGED_NANORINF/PCILU, S12 landing + docket close.

### 2026-08-05
- KATIE: full approval granted for all filed proposals ("do whatever you want"); proposals move to approved as agents claim them.
- DISPATCHED (case-building wave): defect-reach case matrix (more examples with/without refinement interfaces, 180 core-min);
  community novelty sweep (DAFoam issues+discussions, docs, CFD-Online — has anyone hit either defect); DAFoam method-papers
  fetch+read (how was the parallel adjoint ever verified, and on what meshes); closure-challenge proof audit (metric definition
  from the eval code, convergence/stability/a-posteriori inventory, entrant-by-entrant methods comparison);
  **Stage 1 CBFS inversion** (pre-registration first, 600 core-min cap, production-term-labeled).
- INFRA: auto-stop blind spot closed — `scripts/session_keepalive.sh` (f02a3a90) holds the box only while the supervision
  session is actively writing; self-expires at 45 idle min / 24 h. Armed now; armed first thing every session.

### 2026-08-05 (afternoon, post session-limit recovery)
- INCIDENT: the account session limit killed the supervisor and all four working agents at ~18:53Z on 08-04; the box
  auto-stopped overnight. Zero scientific loss — every agent's pre-registration was committed before its compute
  launched (e6321e95, 99f5d41d, 73fa6a33). All four agents resumed from transcripts 15:00Z. Lesson memorized
  (session-limit-kills-the-fleet); keepalive re-armed.
- NOVELTY ESTABLISHED (3c74dc03): 63 searches / 10 venues, zero prior reports of either defect; scotch never mentioned
  upstream while shipping as default; #946 is the near-miss and pre-answers the stock replies; sub-LU = sanctioned
  PETSc remedy. Papers verdict (bf6ac53b): the parallel Jacobian-free operator was verified once, in serial, on purpose.
- DISPATCHED (Katie's asks): two Opus LaTeX reports (closure-challenge campaign; DAFoam defect case); charter iteration
  agent (P-1.1 gain table + source_kind refusal, P-3.1 hard_criterion field, P-6.2 gross/cleaned spend labels,
  P-7.1 threshold recommendation drafted for Katie). Resumed: defect reach, CBFS inversion, closure gaps G1-G4,
  papers-protocol arm.

- GAPS G1–G4 CLOSED (fee5eaf9..30fd6d7a), both audits MATERIAL under pre-registered lines: seed-stability bound at
  test points 0.00242 ≈ the whole rank-2 gap (stable where truth exists; qualifiers in record + closure.html);
  post-hoc correction injects continuity error (hills 58x/124x, 35/36 corrected fields over the ratio-2 line —
  disclosed in submission draft §5.3; measured motivation for the in-PDE Stage 1 line). Round-4 MANIFEST + per-case
  convergence provenance landed. Zero scoring calls.

### Decision requests for Katie (standing)
1. File the prepared upstream `mdolab/idwarp#57` comment / bug report? (`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` ready.)
2. Closure-challenge submission: author names, reference URL, approval to email the steward (incl. the two ambiguity questions).
3. Result-priority decision sheet D0–D7; escalation free-spend threshold (P-7.1); AWS read-only role for P-6.1.
