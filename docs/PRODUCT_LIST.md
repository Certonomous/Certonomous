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
      FIRST INVERSION RUN 2026-08-04→07 (`S1_CBFS_INVERSION_RESULT.md`, 335.98/600 core-min, pre-registered e6321e95):
      machinery PROVEN (17 converged adjoints, ‖g‖ down 106x, bit-identical controls), both gates FAIL for a measured
      reason — the case inlet is the patchV pilot's 0.72-uniform overwrite of the benchmark's 0.9149-bulk profile, so
      the loss floor is an irreducible 27% mass-flux mismatch (W4 §5c corrected, dated addendum). Successor:
      `s1-cbfs-objective-repair-and-reinversion` (proposed). Stage 2 blocked on it.
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
- [ ] F5c backward-facing step reattachment vs Driver-Seegmiller. ~~OOM + gradient blowups~~ — **that premise is refuted in our own
      record** and should not be carried forward: the 2026-07-30 addendum in `campaign/F5bc_unsteady_statistics.md` found no OOM-kill,
      no solver abort and no commit anywhere connecting F5c to memory, traced the description to a probable conflation with B3 CBFS
      (which genuinely does hit the adjoint memory wall), and a 20,000-iteration control held RSS flat at ~79 MB on a 30 GB box.
      What is actually open: a steady RANS solve that converges numerically at every rung and lands 4–12× wrong on reattachment,
      wandering non-monotonically with iteration count and algorithm. Diagnosis plan: `campaign/NEXT_CASES_SLATE.md` item 3.
      [premise corrected 2026-08-05]
- [x] F4 hypersonic blunt body vs Billig standoff (+ SWBLI stretch).
- [-] F6a NASA hump [gate reached]. Pass with *; overpredicted bubble length (k-SST diffusion suspect).
      1. Try different models. 2. If confirmed → epistemic-uncertainty showcase. Also `w1-hump-challenge-conditions` (approved, 60).
- [-] F6b periodic hills vs ERCOFTAC. **Gate verdict 2026-08-05, on OUR OWN mesh this time** (the 2026-07-29 gate used the
      benchmark's shipped grid and could not separate model error from grid error). Verification PASS: our ERCOFTAC-polynomial
      mesh reattaches at x/h 7.6472 vs the shipped mesh's 7.6439, **0.043%** against a pre-registered ±5%, and the point moves
      only 1.4% over a fourfold cell range. Physics **FAIL, as pre-registered**: 7.6472 vs the literature band 4.21–4.70
      (Rapp & Manhart 2011 exp / Breuer 2009 LES / Fröhlich 2005 LES), **+72% on the band midpoint**. Profiles 12.82% scaled MAE.
      4 of 5 pre-registered predictions held. `campaign/F6b_ERCOFTAC_{PREREGISTRATION,RESULTS}.md`, 24.6+ core-min.
      **Open successor, not a cross-off:** the 62,400-cell rung does not converge and its residuals sit on a flat plateau —
      either under-relaxation or genuine unsteadiness, undecided on purpose. Docket
      `f6b-why-the-finest-hill-will-not-converge` (55). Stays uncrossed until that is answered.
- [-] F6c duct vs DNS. Captures 0% of anisotropy — structural model deficiency, not us. Research-result candidate;
      `closure-duct-tensor-basis-carrier` proposal (120) is the constructive follow-up.
- [ ] NACA 0012 wall credential re-grade: W3 found the published Cd (0.01205, outside ±30% band) is not reproducible —
      3 of 4 same-recipe meshes land inside the band (`campaign/W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md`). Needs a verdict protocol
      for mesh-draw-sensitive credentials. [added 2026-08-02 by W3, adopted onto list 2026-08-04]

## 4D. 3D case families
- [x] F1 ONERA M6 transonic wing vs AGARD Cp stations.
- [ ] F10 real 3D viscous RANS batch family (replace the panel-method stand-in).
- [-] F8 NREL Phase VI wind turbine (MRF, then transient). GATE: NO VERDICT — unconverged forces not gateable
      (p2p spread 960% of the 800 N·m reference, 19.2x the pre-registered cap; L-24). MECHANISM FOUND (75d5a4ca):
      the rotor was set spinning AGAINST its power-extracting direction — the case never operated as a turbine;
      flipped omega calms the history 21x. Citation conflation in our own docket untangled (TP-500-29494 Simms vs
      TP-500-29955 Hand; 800 N·m is secondary-tier, corroborated 3 ways incl. P=Qω≈6 kW). Flipped-omega settle
      (~13 core-min) running as rider; transient branch is the fallback.
- [ ] AIAA DPW: study public data/methodology, then attempt CRM/DPW-class case (converged primal first).
      A6 wing-alone primal now matches DAFoam's published tutorial baseline to 0.0067% (provisional — see 4E A6).
      `w1-dpw5-hex-three-level-ladder` proposed (400).
- [x] B52: why the mesh doesn't converge smoothly — ANSWERED (dfc50ee8, 19.1/20 core-min, pre-registered 48cfedfb):
      the ladder is NOISE — rung 8's increment (−2.78e-4) is 15% of the measured 1.91e-3 mesh-noise floor; the
      surface-resolution alternative REFUTED by its own decision rule (faces scale N^0.707, inside the uniform-like
      window); refit honestly conclusive:false. Docket item closed done.
      → NEW ITEM (from this cross-off): **B52 floor decision** — either a noise-floor-reducing recipe change
      (pre-registered) or documented retirement of the ladder at its floor with the family moved to regression duty.

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

## 4I. Uncertainty quantification line (NEW 2026-08-05, Katie's directive: every result ships with a band — fast)
- [x] Dow (MIT) structural-uncertainty reading: SM thesis + AIAA 2011-1762 READ IN FULL (no Dow PhD on this line exists —
      bounds the program); 2011-3865 unobtainable (4 routes logged, filed to access list); DO scoped and DECLINED with a
      falsifier (our propagation has no time in it). Headline: Dow's nu_t-discrepancy parameterization is strictly richer
      than our beta-on-production — where the SST limiter binds, nu_t has NO omega-dependence, the leading suspect for the
      S1 plateau (zero-compute mask test routed to the S1 close-out). Bonus: verification script found the thesis's own
      headline column mislabels its formula (norm vs energy, up to 20.8 points). 3 proposals filed (absorption fraction
      34cm; statistical step 0cm; band validation ~160cm). (`W2_DOW_STRUCTURAL_UQ_PROGRAM.md`, 7a4aae9c)
      → NEW ITEM (from this cross-off): **Run the Dow program's first two rungs** — absorption fraction on CBFS
      (does eddy-viscosity form absorb 70–92% of model error on our case, as Dow found on his?) + the statistical step
      with the limiter/null-space diagnosis.
- [x] UQ propagation ladder, first rung DONE on the TMR flat plate (fa4191f5/ecb5bdbe, 44.7/100 core-min, pre-registered
      6c3f850a): MC (42 solves) vs order-2 PCE (held-out Q² 0.964) vs GP (0.963) agree; coefficient band = 30.3% of the
      reference Cd — **~104x the +0.29% validation discrepancy** ("a validated case is one whose closure was calibrated
      near the answer"). Dominant coefficient σ_w1 (0.925 total-effect) via γ1 ownership, adversarially traced; published
      transonic ranking does NOT transfer. Provenance of the docket's intervals audited: 3 of 5 provenances corrected
      (one rests on a private communication). GP error bars ~3x too narrow — recorded, used nowhere. Modules landed with
      28 tests: `uncertainty_band.py` + `pce_surrogate.py` (numpy-native — no chaospy/sklearn on box). DO declined with
      falsifier. γ1-rounding finding: OpenFOAM's 5/9 rounding moves Cd more than the validation gap.
      → NEW ITEMS (from this cross-off): **certificate wire-in** of the band module (documented, needs its own test pass
      after 4925fafb) + **Dow band-validation rung** (~160 core-min proposal: does the propagated band contain truth on a
      held-out case).
- [ ] Band machinery: a module that attaches an uncertainty band (numerical + coefficient + model-form channels, per
      UNCERTAINTY-DOCTRINE) to every published case result; wire into the certificate/report path.
- [x] Standing model-form batch (the never-idle engine) — BUILT AND PRODUCING (a8f2329a/691eb11f, 22.5/120 core-min):
      idempotent queue-gated runner survived two kills + a power cycle with zero lost cells; 20/32 cells done.
      First bands: plate re5e6 spread 62.4% across 4 closures, CONTAINS CFL3D SST-V; re1e6 and re2e7 banded with
      exclusions named; Family B honestly refuses a band (all closures stall/FPE — gate evidence). Family N launching
      detached. (`MODEL_FORM_BATCH_DESIGN.md`, `MODEL_FORM_BAND.{json,md}`, study record in house format.)
      → NEW ITEM (from this cross-off): **realizableKE wall-treatment question** (high-Re model on y+<1 grid — the
      batch's first ambition item) + fold the model-form channel into the certificate band via `uncertainty_band.py`.

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

- PAPERS-PROTOCOL ARM CLOSED (c3061eaa): pre-registered prediction REFUTED the honest way — dCD/du0 is decomposition-
  invariant (3.55% vs 3.68%, a loose-tolerance floor). Unpredicted bigger finding: the defect is CONFIGURATION-SENSITIVE —
  under the papers' verification configuration (inletOutlet + patchVelocity input) the shape-row defect does NOT fire
  under scotch (0.019% vs established 8.95%, same mesh+partition). Why-unnoticed now maximal: the historical protocol
  misses twice (never varies decomposition; instantiates a configuration the defect spares). Confound-separating control
  (~3–5 core-min) routed to the reach agent's matrix. Upstream report amended, still NOT FILED.

- CHARTERS ITERATED (1ea0a493..80a53c37, 67 tests green): P-1.1 gain table reconciled + unknown-source_kind refusal live;
  P-3.1 hard_criterion field enforced for new proposals (grandfathered old); P-6.2 gross/cleaned basis labels on every
  emitted spend figure; P-7.1 free-spend thresholds DRAFTED decision-ready (60/proposal, 240/agent/day, 480/fleet/day,
  docket above — answerable as "P-7.1: A"). Charter-agent incident disclosed: forbidden git stash, reversed, zero loss —
  lesson queued behind the in-flight LESSONS.md edit.
- DEFECT FOUND by charter sweep: pending study's certificate reports quantified=True (test_certificate.py fails at HEAD,
  pre-existing) — honesty-machinery bug, fix agent dispatched.
- LATEX: closure-challenge campaign report SHIPPED — 24 pp compiled PDF, every number artifact-traced
  (`demo-output/website/latex/closure_challenge_report.{tex,pdf}`, 0249c6e9). DAFoam defect report in progress.
- PAPERS-PROTOCOL ARM (c3061eaa): prediction refuted in the strong direction — dCD/du0 decomposition-invariant, so the
  2018 paper's own check misses the defect twice (never varies decomposition; checks the derivative class the defect
  spares). Upstream report reframed fills-a-declared-hole. New trigger clue (staging edits suppressed the shape defect;
  separating control ~3–5 core-min) handed to the reach agent.

- CHARTERS ITERATED (1ea0a493..80a53c37, 67 tests green): P-1.1 gain table + source_kind refusal ENFORCED;
  P-3.1 hard_criterion field REQUIRED for new proposals (221 old entries grandfathered); P-6.2 gross/cleaned labels
  live on the reporting path; P-7.1 free-spend thresholds DECISION-READY (answer "P-7.1: A" to enact: 60/proposal,
  240/agent-day, 480/fleet-day, approved caps override). LaTeX closure report SHIPPED: 24pp compiled PDF, 0249c6e9.
  Follow-up dispatched: pre-existing certificate truthfulness bug (pending study claims quantified: True).

- BOTH LATEX REPORTS SHIPPED (Katie's ask): closure campaign 24pp (0249c6e9) + DAFoam defect case 27pp (d7d87a05),
  both compiled clean, every number sourced, hedges preserved. They are the durable companions to the two unfiled
  upstream reports and the submission draft.

- REACH MATRIX COMPLETE (0b022b36, 159.9/180 core-min, zero lost to kills): trigger refined to freestreamVelocity-BC-
  in-tape (necessary; patchV inert per N9) x cut geometry (scotch np>=3 worst, slabs benign); second defect case Ahmed-35
  (cross-residual 5.45x, same localization); CBFS + sail + 3 more clean — 7-case perfect BC correlate; damage priced by
  objective contraction (L-36: a gradient check certifies a contraction, not an operator). Misses scored honestly
  (N2, N3/4/5, N7-magnitude NOT HELD). Supervisor sweep DISPATCHED before the case file closes. Both docket items done.
- SUITE GREEN: 1104/0 after hygiene agent (44be9dd5, 289611fb); one real fix — wall percentage now recomputed from the
  displayed coefficient (16%→17% at next rebuild, same measurement). Certificate truthfulness fix 4925fafb; R7 correction
  filed in SUPERVISOR_RULINGS (3640debd).

- DAFOAM CASE FILE FILING-READY (4a49ab43): reach-matrix sweep CONFIRMED 6/6 with the two confounds named and stated in
  the report's own voice (defect side = n=1 mesh family; freestreamVelocity anti-correlated with patchV — N9's within-case
  swap breaks both and carries the causal weight); 27pp companion PDF recompiled with the trigger addendum. Everything on
  the DAFoam side now reduces to Katie's two filing decisions.
- S1 INVERSION LIVE (snapshot 16:15Z): 7 accepted iterations, J 1.0→0.99908 monotone, |g| down 30x, beta in [0.74, 1.15],
  eval-1 control bit-exact vs W4; 165/600 core-min. Agent owns completion.

### 2026-08-05 (evening) — third fleet death survived, and the defect gets a scheme
- INCIDENT 3: weekly usage limit killed all ten agents ~17:20Z; credits restored 17:27Z; all ten resumed from transcript.
  Detached solves ran straight through it again (model-form cells, MC samples). Three deaths, zero scientific state lost —
  the pre-register-before-compute rule is what makes that true, and it is now being codified as an OPS charter section.
- DEFECT ROBUSTNESS, the day's sharpest result (671f40bb): the numerics-formality arm was NOT a formality. Switching
  convection `linearUpwind limited` → `bounded Gauss upwind` (same mesh, same scotch cut) drops the error 8.95% → **0.228%**,
  with the adjoint converging in 68 Krylov iterations against the record's 590. The registered rule fired: the defect is
  scheme-specific and the mechanism question REOPENS. Two one-knob arms registered to separate convection from gradient.
- SUPERVISOR HYPOTHESIS (relayed, under test): all three of this lab's DAFoam-family defects may be ONE class —
  **a branch recorded in a differentiated path**. The limiter in `linearUpwind limited` is a branch; `freestreamVelocity`
  (necessary per the reach matrix) is a flux-direction branch; L-29's IDWarp degenerate-rotation guard was a branch.
  Sharpest test registered: is UNLIMITED second-order (`Gauss linear`, no limiter) clean or dirty under scotch?
  If only the limited scheme is dirty, the mechanism is named at the level upstream can act on — and the report is
  reframed from "the parallel transposed-Jacobian is wrong" to the exact construct whose taping breaks.
  **The upstream report does NOT get filed until this resolves.**
- METHOD PRIORITY REVIEW (d84b649f): our closure method was NOT copied — but Hanna et al. 2017/2019 (coarse-grid error
  surrogate) is a mandatory citation we never carried, and two of our own compressions overclaim (Ling & Templeton
  *identify* uncertain regions; they control no correction). Eight owed citations tabulated; repairs in flight;
  13 countable negatives support the gate-to-physics-baseline combination as genuinely novel.
- S1 CBFS INVERSION: pre-registered NEGATIVE result — optimizer plateaued at J≈0.99908 (0.09%), under its own bar,
  despite an FD-verified gradient and monotone descent. Diagnosis in progress; the production-vs-destruction term
  mismatch is the leading suspect, which would make the destruction-term patch the real unblocker.

- QCR LANDS AS THE RANK-1 ROUTE (303247bb, 0afd7e61): QCR2000 built as a turbulence-model class (~180 lines, no rebuild);
  falsifier CONFIRMS F6c's structural-limit claim (stock in-plane RMS 3.16e-16 vs QCR 0.6239% vs LES 0.7570%; Ccr1=0
  reproduces stock exactly, r=+0.953); training-duct MAE down 33–57%. Campaign finding: we already beat rank 1 on 4/8 —
  matching rank-2's duct scores alone gives 0.0563 vs Reissmann 0.0595 = RANK 1. Route dispatched (95 core-min,
  validation-first all-or-none gate; NO scoring call without supervisor sign-off). Learned-beta route C dead on its own
  pre-registration; a discriminating duct inversion now precedes any A2 spend.
- CHARTER TRANCHE 2 (84cc2f78, c3033a36; suite 1124 green): P-1.4 replay-before-docket rail live; citation-tier checker
  built (7 hits reported — 2 real paywalled-relay defects routed to repairs); P-1.2 axis-B analysis PROPOSED (option D);
  P-5.2 six orderings drafted as D8–D13 for Katie's rulings; OPS fleet-resilience section landed citing all three deaths.
- CROSS-CASE PATTERN (F6a + F6b): k-omega SST overpredicts separated-region length on BOTH the hump (bubble) and the
  hills (+72% reattachment, mesh-verified, pre-registered FAIL) — the epistemic-uncertainty showcase now has two legs;
  the model-form batch quantifies whether the model family brackets truth on both.

- METRIC CENSUS + EVAL BATTERY LANDED (03814b0a/fa4191f5/3a05ca70): 10 papers read in full, 24 metrics with verbatim
  citations, 20 figures in the literature's own conventions. Sharpest reveal: our duct correction gets the AMOUNT right
  (69–112% intensity) and the STRUCTURE wrong (one vortex vs the true counter-rotating pair) — invisible to every scalar.
  Honestly against us: loses to raw RANS on one of its own training cases; relocates error where the metric weighs least.
  Census also caught the benchmark's preprint stating no metric limitation and rank-1's reference DOI resolving to an
  unrelated paper. Topology check routed into the QCR validation gate. Hump-class battery gap documented (needs a
  validated wall-gradient operator), queued.

- CITATIONS PAID (b0aa6102/f3d231b3): all eight owed citations landed at honest tiers across six documents; the
  identify-vs-control split applied in the two named places plus one the review missed (§7.4); Hanna read IN FULL —
  its own §4.3 names the conservation gap our G2 audit measured (lineage explains the cost, never excuses it);
  the two paywalled-relay defects fixed with relay chains named and DOIs Crossref-checked, both papers on Katie's
  MIT access list. PDF recompiled: 27pp, 0 errors. Tier-audit hits 7 → 5 (remainder benign/handled).

- F6B VERDICT (9e6d33a5/242de6fd, 50.2/80 core-min): pipeline VERIFIED on our own ERCOFTAC-polynomial mesh (0.043% vs
  shipped grid, 0.097% grid sensitivity), physics FAIL as pre-registered (+72% reattachment vs the Rapp/Breuer/Fröhlich
  band) — the two-legs SST separated-flow pattern (hump + hills) is now mesh-defended on the hills side. Re_H label error
  in our own records found and corrected (case IS canonical, built on crest bulk velocity). Finest rung honestly undecided
  (f6b-why-the-finest-hill-will-not-converge, 55). Slate ranked 8 families; two premise corrections (F5c OOM refuted;
  F8 MRF already run, unconverged); slate-toppers dispatched (F8 forces gate vs Hand 2001; B52 8th rung).

### 2026-08-07 (evening) — fourth fleet death survived; the day's two verdicts resume
- INCIDENT 4: weekly limit killed the five working agents ~17:45Z on 08-05; credits restored 08-07 19:59Z (two-day gap,
  box power-cycled). All five resumed from transcript; both keepalives armed through 08-08 19:59Z. The QCR agent froze
  its round-5 rule in a COMMIT before dying (0bade54a: all three ducts or none, decided by AR_7 alone, AR_14 tie at
  risk in writing) — the pre-register-first discipline survived its fourth test.
- RESUMED THREADS: branch-hypothesis survey ("A1 has no limiter — this changes R1's interpretation"; seven-case scheme
  survey at zero cost); QCR AR_7 validation arm + topology check; S1 reference-coverage audit (the 30%-RMS-vs-LES
  credibility question) + limiter mask; model-form batch cell collection; slate-toppers (F8 forces gate, B52 rung).
- S1 CBFS INVERSION CLOSED (335.98/600 core-min, `S1_CBFS_INVERSION_RESULT.md`): the lab's first actual field inversion
  on a closure-relevant case ran end to end — 17 converged sub-LU adjoints, gradient norm down 106x, eval-1 control
  bit-identical to W4 (objective AND gradient) — and **both pre-registered gates FAIL** (J_qoi −0.149% vs the ≤0.70 bar;
  window fraction 29.0% vs >50%). The coverage audit found the cause and it is an OBJECTIVE DEFECT, not a closure
  result: the case's `0/U` inlet is the patchV pilot's 0.72-uniform write-back over the benchmark's 0.9149-bulk profile
  (identical Uz noise columns = the fingerprint), so the varianceU loss floor is a 27% mass-flux mismatch no beta can
  remove (85.1% of loss at y>2; 3.7% in the physics window). W4 §5c's "real inlet restored" sentence CORRECTED (dated
  addendum). Second defect named: in-process primal restart walks off the converged state and DAFoam proceeds into the
  adjoint on a failed primal (prereg Amendment 1). Limiter-mask test: SST shear-stress limiter binds on 49.5% of the
  top-decile |beta−1| cells vs 7.7% base rate — the production hook is structurally weak exactly where beta wants to
  act. → NEW ITEM: `s1-cbfs-objective-repair-and-reinversion` (PROPOSED — restore the benchmark inlet, re-verify FD,
  re-baseline with a pre-stated prediction, re-run the surviving driver; w3 destruction patch stays the term-parity
  follow-on). Stage 2 stays blocked; nothing from this beta field may train anything.
- LOOSE END noted: untracked F7a_R1/res16_alphaco sweep dirs (08-05 15:28, unowned by any known agent) — triage whether
  this is committed-work residue or an orphaned F7a-fix attempt before anything overwrites it.

- BRANCH HYPOTHESIS HELD — the defect has its mechanism (robustness campaign, 25f52868..0076a73, 128.3/150 core-min,
  L-37): the slope limiter's min/max selection is the gate — one-word edit collapses gradient error 8.95%→0.849% and the
  OPERATOR-level cross-residual 329x→0.0135x||b|| (24,300-fold). The BC lever only HIDES the defect (inletOutlet reads
  0.019% in check_totals while its operator misses by 1.047x||b|| — L-36 measured in the act). Hanging nodes eliminated
  (conformal mesh still fires, 2.82%); under refinement the conditioning collapse TRAVELS with the limiter (with it: no
  adjoint at all; without: 149-iter convergence). The bug is now named and 30-second-reproducible. Dispatched: the one
  decisive acquisition arm (A1 + limiter + BC — kills or confirms the n=1-family confound) + the supervisor sweep of the
  headline numbers. Upstream report NOT FILED until both land.

- ROBUSTNESS SWEEP CONFIRMED 6/6 (8bd47b35, 0.00 core-min — all offline): cross-residual pair reproduced to the digit
  (1.3548e-02 and 1.0472e+00 x||b||); the one-word edit verified literally one changed line; erratum in our favor
  (719 not 590 iterations — collapse is 17.5x, larger than claimed); four small fixes routed to the acquisition agent's
  close. The mechanism claims are now defended end-to-end; only the acquisition arm stands between the upstream report
  and filing-ready.

- ACQUISITION ARM: THIRD OUTCOME (0263d950..d63b3212, 15.2/30 core-min, L-38): A1 did NOT acquire the decomposition
  defect — instead the limiter breaks A1's SERIAL adjoint (92.8% CD, sign flip, vs step-stable FD; one-word lever →
  0.121%), decomposition-INVARIANT wrongness ("invariance certifies consistency, not correctness"). Upstream report
  scope honestly narrowed (decomposition variant = one mesh family on present evidence) and GAINS a single-process
  one-word reproducer. Sweep of the serial finding dispatched (the FD-kink question gets full seriousness before
  anything is filing-ready). primalMinResTol co-ingredient hypothesis gains weight.

### Decision requests for Katie (standing)
1. File the prepared upstream `mdolab/idwarp#57` comment / bug report? (`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` ready.)
2. Closure-challenge submission: author names, reference URL, approval to email the steward (incl. the two ambiguity questions).
3. Result-priority decision sheet D0–D7; escalation free-spend threshold (P-7.1); AWS read-only role for P-6.1.
