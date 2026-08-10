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
- [x] ~~0.0741~~ → ~~round 4, 0.0654, rank 3~~ → **ROUND 5, 0.056647, RANK 1 OF 5** (scored locally at benchmark commit
      deb91557; 07a7fe9e; the 6th pre-registered call, ACCEPTED mechanically under the criterion frozen at 0bade54a
      before any solve): **us 0.0566** · Reissmann 0.0595 · Wu&Zhang 0.0624 · Liu 0.0737 · Montoya 0.0779. The whole
      delta is the ducts (untrained QCR2000: AR_1 0.0811→0.0455, AR_3 0.0775→0.0400); AR_14's tie LOST (+0.0029) exactly
      as priced in writing, not reverted per the bundle's terms; our QCR ducts land within 0.0004 of Wu&Zhang's published
      ducts — same term, independent solve, same answer. Caveat everywhere: LOCAL scoring, not an official placement.
      **AND from 2026-08-10 (b2aa6887) a second mandatory caveat beside the first: P(rank 1) = 68%** (400k case-level
      bootstrap; rank distribution 67.6 / 18.6 / 12.8 / 0.9 / 0.2). The lead over Reissmann is NOT statistically
      decided — paired per-case t = −0.495, dispersion 5× the margin, 4 of 8 cases won — and Wu&Zhang is not decided
      either (t = −0.953). Only Liu (98.7%) and Montoya (99.8%) are beaten on method. Eight cases cannot resolve a
      rank probability better than 2–100% at 95% (double bootstrap). The standing is TWO CASES WIDE: drop alpha_15
      and we are rank 2 on the point score; drop the hump and P = 91%. AR_1/AR_3 margins (0.00003 / 0.00008) are ties
      below published precision and must never be quoted as per-case wins. The number is INTERNAL and never appears
      in an external claim — but no internal surface may print "rank 1" without it.
      → NEW ITEM (from this cross-off): **closure.html coherent rewrite** under Katie's GUI conventions — DONE
      (page is round-5 current; consistency re-verified by Ladder V rung V10, 49f71b8c).
- [x] alpha=15,AR14 status (superseded by round 5, kept for history): AR_14 is now 3 of 5 and best-on-board is 4 of 8
      after the priced-in-writing round-5 tie loss (+0.0029); the earlier "best-on-board with a 0.00003 lead" reading
      is obsolete — must not be reported as a comfortable win, and per V8's banned-claims list, not as "best-on-board"
      either.
- [x] Find out challenge policies / whether Certonomous can submit. DONE (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §1–§4):
      steward Ryley McConkey (MIT); no eligibility clause, no fee, no deadline, no scoring limit; leakage rule audited in code, not violated.
      Two flagged ambiguities: company name in Authors column; no license on benchmark/training-data repos.
      → NEW ITEM (from this cross-off): **Submission send package** — Katie fills author names + reference URL, approves,
      sends the email (with the alpha_05-rows-are-baseline disclosure); ask steward about the two ambiguities in the same email.
- [x] Update the Active Research board with movement. DONE and verified twice: round-5 rewrite landed, then Ladder V
      rung V10 (49f71b8c) swept every surface — closure.html, wall.json/html, benchmarks.json, ACTIVE_RESEARCH.md, the
      .tex — and fixed the last two drifts (benchmarks.html was a round-3 fossil; two present-tense 0.0654 sentences
      scoped). One surviving latent defect killed in the same pass: build_benchmarks.py's literal still said round 3
      and would have silently regressed the public page on its next run.
      → NEW ITEM (from this cross-off): ~~**Ladder V early rungs V1/V3/V4/V5 as record-hardening**~~ DONE same day
      (9a21d65c): all four PASS — score reproduced to the last digit in a fresh venv, leakage asserts executed live
      with a negative control, AR_1 traced unbroken end-to-end, untrained-QCR proven structurally. Ladder V now stands
      V1–V5/V7/V10 all PASS (status ledger in LADDER_V_TRIPLE_VERIFICATION.md); the remaining rungs are exactly the
      set that needs a real submission package.
      → NEW ITEM (from that cross-off): **Model-form matrix on the periodic hills** (review entry 1's remaining
      diagnostic, ~35 core-min, chief-approved 2026-08-08): do any of the four closures enter the Rapp/Breuer/Fröhlich
      band, and does the inter-model band contain it? Feeds the epistemic-uncertainty showcase; the QCR null (activity-
      verified, 1a14e90b) makes the inter-model band the last cheap probe on the hills before the omega-budget work.

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
      (p2p spread 960% of the 800 N·m reference, 19.2x the pre-registered cap; L-24). ~~MECHANISM FOUND (75d5a4ca):
      the rotor was set spinning AGAINST its power-extracting direction~~ *(superseded by the §10 STL audit below —
      geometry exonerated; the flip run was the backwards one; struck 2026-08-07 per the Cases supervisor's R4)*.
      Citation conflation in our own docket untangled (TP-500-29494 Simms vs
      TP-500-29955 Hand; 800 N·m is secondary-tier, corroborated 3 ways incl. P=Qω≈6 kW). Flipped-omega settle
      SETTLE VERDICT (b63fbfbf, 13.6 core-min): flipped rotor SETTLES — first gateable band F8 ever produced (p2p 17.9%
      of Q_ref) — but torque is +138 N·m MOTORING-SIGNED vs 800 N·m; pre-registered sign rule refuses the milestone.
      Both directions now measured: NEITHER extracts power → blade pitch/twist/mirroring geometry defect, not numerics.
      STL AUDIT (0e769064, 0 core-min): geometry EXONERATED — chord to 2-3mm and twist EXACT vs TP-500-29955 Table A-1,
      no mirror, AoA +3.2/+5.2/+4.1 deg textbook attached; the flip evidence re-read correctly (the flipped run WAS the
      backwards one; its +138 N·m is expected reverse-drag). Real anomaly = the original direction's non-convergence,
      prime suspect impulsive start. INIT ARM DIVERGED (27dd8f86, 13.4 core-min): forces → 1e99 behind a 1.4e-8 Ux
      residual — a live S10 specimen. AUDIT + ARM A (76cf1aa4/1bb059a5): the divergence fully explained —
      potentialFoam's makeAbsolute baked the frame's solid-body sweep into the whole-domain zone (~150 m/s vs 7 m/s
      inflow; source-line citations MRFZone.cxx:447-489, potentialFoam.C:187) — we initialised a hurricane. Frame terms
      audited clean; single-variable corrected arm reproduces the original motoring limit cycle. **STEADY-MRF CLOSED
      THREE WAYS on evidence** (geometry / frame terms / initialisation); transient branch inherits the quantified
      target (turbine-signed, ≤400 N·m band vs 800 N·m). "MRF first" clause complete on a measurement trail.
      F8 total 47.7 core-min.
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

- A1 SERIAL SWEEP CONFIRMED 5/5 (0858e640, 0.00 core-min): the kink trap — the one axis that could gut the finding —
  was found unaddressed in the record (F1), then CLOSED from existing logs: smooth components can't be kink artifacts,
  and the branchy component's adjoint lies outside the FD's branch bracket, wrong side of zero, 3x magnitude.
  **THE DAFOAM CASE FILE IS FILING-READY, COMPLETE**: limiter-tape mechanism (operator-proven, 24,270-fold collapse
  verified), parallel variant (one mesh family, honestly scoped), serial variant (one-word single-process reproducer,
  kink-closed), novelty (63 searches), why-unnoticed (from the papers' own protocols), sub-LU remedy (PETSc-sanctioned),
  27pp compiled companion, every headline claim survived an independent adversarial sweep. Both upstream reports await
  only Katie's filing decision.

### 2026-08-07 (night) — Katie's restructuring directive executed
- SUBMISSIONS PARKED at Katie's word: nothing external gets sent; both LaTeX reports stay current via their designated
  agents (round-5/rank-1 update and the complete defect-class update both in flight, Opus writers).
- SUPERVISOR NEGATIVE-VERDICT REVIEW (personal, binding): `demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`
  — all 10 standing negative verdicts reviewed, 11 new diagnostics proposed and being filed (5 pre-approved: F5c inlet
  audit, F8 BEM cross-check, S10 replay, QCR-on-hills, A3 sub-LU arm — the A3 one closes a real gap: the unblock tool
  was never carried to the family it was invented near).
- NEW CHALLENGE SLATE (Katie's 2D+3D tables) adopted as the standing hard-case program; scoping agent producing
  `campaign/CHALLENGE_SLATE_2026-08.md` (status map, capability gaps with unlock rungs — FSI / compressible multiphase /
  free surface / rotating — reference-data verification, gain-table ranking, top-3 filed).
- SUPERVISION STRUCTURE STOOD UP: three Fable family supervisors launched (DAFoam/adjoint; Closure+UQ; Cases/campaigns)
  — each doing its first pass now: family-state blind-spot review, written supervision guidelines, and a personal
  line-by-line code check of its two highest-risk artifacts. SUPERVISION_CHARTER.md being written; chief retains
  scoring authorization, cross-family arbitration, negative-verdict reviews, list custody.

- SLATE SCOPED (cfd9214e): 10/21 already ours; capability gaps MEASURED (solids4Foam/preCICE/blastFoam not installed —
  each enters via an install+tutorial rung); F7a premise corrected (sign-flip was retracted; standing FAIL is dry-bed
  film friction, mechanism-diagnosed); 3 proposals filed (double Mach, F5c sequence, TGV — ranked on instrument grounds
  with the disagreement vs the chief's guess stated); top-2 runnable dispatched (hump-at-challenge-conditions repriced
  + QCR arm; double Mach).
- CHARTERS: nine now — SUPERVISION_CHARTER v1.0, verification v1.4 (negative-verdict rule), case-selection v1.3 (slate
  adopted), goals v1.4 (submissions parked), PROPOSALS_OPEN v2.4 (beec7da1, 61 tests green).
- DAFOAM FAMILY SUPERVISOR FIRST PASS (770436f9): five currency lags fixed; found A-1 HIGH — the sign error is STILL in
  the reusable cross-residual instrument (fix dispatched before any maintainer touches it) and B-2 — the cited patch's
  headers are dead paths (git apply fails; regeneration dispatched); DISC-6 (tex frames inletOutlet as clean) relayed to
  the tex owner. The supervision structure caught real defects on day one.

- INFRA SUPERVISOR FIRST PASS (675e2873): suite 1159/0; four medium defects FIXED with tests — incl. 19 inbox files
  silently dropped at intake (two of them today's S1 proposals; closure supervisor triaging) and the keepalive's
  single-sample disarm (K-1). Chief reconciliations done: two orphaned claims released on their delivered substance,
  two early closures given outcomes (72f6ef6a). All four family supervisors have now completed first passes — the
  structure found and fixed real defects in every family on day one.
- NEW Katie decision item (K-3, needs root): /usr/local/bin/auto-stop.sh's busy pattern omits pisoFoam, foamRun,
  reconstructPar, decomposePar, checkMesh, and Certonomous/scripts — a future case using those alone could be
  powered off mid-run. One-line pattern edit, root-owned. (K-2 ruled: the 45-min stale window stands — bounded
  cost when a session is genuinely quiet; active campaigns are covered by the double hold.)

### 2026-08-08 (night) — sixth fleet death survived; Ladder V goes on the record before any send exists
- CREDIT EXHAUSTION #3 (the sixth fleet kill overall, ~23:41–00:50 UTC; credits restored 12:50am, recovery started
  01:53). Zero scientific loss again: pre-registrations were committed before every in-flight compute. The box itself
  never rebooted (up since Aug 7 19:28), so the kill took the agents but left the tree; both keepalives verified —
  filming hold live to 19:59 UTC, session keepalive re-armed (auto-stop currently reads the lab BUSY).
- ALL FOUR KILLED AGENTS RESUMED from transcript with kill time + surviving state: Cases supervisor (file + run review
  entry 11's n=3 SA arm, pre-registration first), hump/double-Mach runner (three uncommitted outcomes + the 22:52:59
  docket-rail regeneration to verify and land), Infra supervisor (its pytest suite FINISHED as the kill hit per the
  chief's watcher — collect the tally, land the y+ gate fix at mega_batch.py:635 + retrospective), S1 reinversion
  (driver did NOT survive this time — last run-dir write 23:41 with no reboot to blame; diagnose from its ledger,
  warm-start from checkpoint).
- LADDER V RECORDED (ac4a83e1, `campaign/LADDER_V_TRIPLE_VERIFICATION.md`): the triple-verification protocol that
  blocks any future round-5 send — three passes, three different minds, three directions of attack (re-derive /
  adversarial / cold reproduction), 13 rungs, no self-grading, send gate ends at Sanaa's hands and Katie's. Submissions
  stay parked; the gate is recorded BEFORE any send exists, which is the anti-hindsight discipline applied to
  ourselves. Rungs V2/V7/V10 are executable now as record-hardening and may be run as normal docket items.

### 2026-08-08 (early morning) — the resumed fleet lands everything, and three review entries get their outcomes
- HUMP AT CHALLENGE CONDITIONS (74797a57 pre-reg, 9d711efb results): Gate V passed to the fourth digit against the
  verified F6a answer; Gate P reattachment FAIL at +13.92% — INSIDE the pre-registered +12–16% prediction window, so
  the two-leg SST bubble bias is confirmed at challenge conditions. The QCR arm returned a null (+0.0022 x/c away from
  experiment, bar 0.010): constitutive/anisotropy ruled out on the hump leg, omega budget implicated — a clean
  separation from the ducts, where the same untrained QCR was decisive. Review entry 2 outcome + a new a1-limiter
  diagnostic recorded (0a764729); the a1 arms (0.28/0.34) and QCR-on-hills are running now under a chief-owned watcher.
- DOUBLE MACH REFLECTION first result (84933043): Gate V passed both rungs (shock-position error 0.15%/0.17% of
  travel), rung-to-rung self-similarity passed (free slope within 0.05° across 2× refinement); two gate clauses failed
  AS WRITTEN and were kept + diagnosed as instrument defects (registration geometry; a threshold constant in cells).
  Honest amendment discipline: no reachable numeric triple-point band in the accessible canon, so the gates stand on
  kinematics + structure detection, stated before launch. The DMR cost estimate graded ~8× cheap-side vs the 45-cap
  session (measured 2.4 vs 20 filed) — decomposition recorded.
- INFRA y+ GATE FIX LANDED (590f5542): suite 1172/0 (tally collected from the pre-kill run, not re-run); retrospective
  proved the restart-rename blindness NEVER fired on a published row (three independent evidence lines: single-attempt
  ledger, structural rmtree, zero renamed files in surviving dirs). Docket item closed on both halves.
- S1 REINVERSION CLOSED (1c3bb2f6): the driver had finished on its own budget guard BEFORE the kill. G1 PASS — −74.2%
  on the repaired objective (the corrupted one managed −0.149%); FD re-verified to 0.03–0.12% after a dated primalTol
  amendment. G2 FAIL (26.9% vs >50%) but the failure decomposes: 77.6% of residual loss sits at y>2 where the
  reference-level mismatch lives, budget-capped still descending. Review ENTRY 12 (94349b83): weighted-loss variant
  promoted to highest-information arm (two independent measurements now point at loss placement), continuation arm
  waits behind it, and STAGE 2 HOLDS — no generalizer trains on a β field known to under-serve the window.
- ENTRY 11 ARM EXECUTED (9374f807 pre-reg, 06b78343 outcome): SA converged at a10 under the adjusted-but-preregistered
  criterion, 1.07 of 10 core-min — at n=3 the Cl band CONTAINS CFL3D (the third member entered 0.051 BELOW the old
  floor; the n=2 band under-stated Cl spread by 2.4×). The declared branch fired: `no-containment-verdict-below-n3`
  rule proposal filed with archive replay as its adoption gate — chief-endorsed (583b8c87). Bonus: the arm exposed and
  fixed a wrapper defect (admitted-but-excluded precedence collision), wrong record superseded-not-deleted.
- Watcher discipline note: two resumed agents parked on waiters that died with them (the known antipattern) — both
  watches were taken over by the chief inline; no work was lost either time.

### 2026-08-08 (pre-dawn) — the review's diagnostics all execute, and three "mysteries" die of measurement
- QCR CLASS SENTENCE HARDENED (1a14e90b activity check, hold lifted df755b49): "QCR2000 resurrects anisotropy-driven
  secondary flow and does not touch 2D separated-shear-layer bubble length" — three legs (ducts decisive, hump null,
  hills null), with the nulls adversarially defended: model selection in both logs, wall-shear deltas 9–19% on
  identical grids, pressure/velocity movement no stress-formula can fake, momentum-equation wiring cited to file:line.
- THE a1 KNOB MEASURED (2544c9af): converged hump curve 0.31→0.34→0.40 monotone toward experiment, d(reatt)/d(a1)
  ≈ −1.66 just above stock flattening to −0.27 — the stress-magnitude route has a mechanism; still fails Gate P at
  +9.4% (predicted). Reconciled against two previously-uncited 2026-08-01 arms; citation defect dated.
- F5c: THE 4–12× CATASTROPHE NEVER EXISTED (6d806733 audit, a10ebc31 corrections): wallShearStress sign convention,
  proven at fe121af2 NINE DAYS AGO and never absorbed by the records — corrected reading −10.5% with wander; inlet
  clean at reference station; unsteady-probe arm retargeted at the honest question. Meta-lesson L-39 (06517346):
  verdicts age silently; run the reconciliation sweep before diagnosing any standing mystery.
- F8: THE FORK RESOLVED BY ARITHMETIC (6d806733): pre-registered 4-arm BEM gives +686 to +793 N·m attached at λ=5.42
  — an attached steady solution exists in principle, so the motoring limit cycle is solver basin behavior; transient
  branch keeps its confirmed ≤400 N·m target; the +1.8° STL-offset ambiguity closed as the tip-chord pitch convention.
- S10d ADOPTED (a217d393, MONITOR_STANDARD v1.4): the replay found NO CATCH five clauses deep on our own divergence
  specimen; the amendment was adopted only after the Infra family reproduced the full replay itself — 974 histories,
  5 true fires (incl. three dpw5 divergences the old corpus never ingested), zero false positives; suite 1182/0.
- S1 WEIGHTED LINE: capturable at 0.9494/0.9468 vs the 0.70 bar (2c475ab5/71dbf5a8) — the weighted reinversion arm
  (250 core-min) approved behind an 8-core-min nonlocality control; Stage 2 held for the weighted successor's β;
  no G2-bar revision (the bar caught a real property of the loss).
- LADDER V PASS 1 COMPLETE (9a21d65c): V1–V5/V7/V10 all PASS — the score reproduced to the last digit in a fresh venv,
  leakage asserts run live with a negative control, one duct traced unbroken end-to-end, untrained-QCR proven
  structurally. Every rung runnable before a send exists has run; status ledger in the protocol doc (223c3b84).
- IN FLIGHT at changelog time: hills model-form matrix (family H, pre-reg 28e14422), A3 sub-LU adjoint arm, S1
  nonlocality control → FD gate → weighted arm.

### 2026-08-08 (morning) — Katie's L-40 order codified, both audits executed, and the review keeps eating its own entries
- L-40 CODIFIED (7be0afc2): "the switch you set is not the switch that ran" — LESSONS.md L-40 + Verification Charter
  v1.5 §9: `levers_verified_active` (load-bearing options need the log line proving they ran; unverified fails review)
  and the mesh birth certificate (born clean or it doesn't enter; certificate-less meshes quarantined).
- AUDIT 1, DEAD LEVERS (946e4a26): 126 lever/conclusion pairs VERIFIED with ~180 quoted log lines; 16 distinct
  unverifiable-from-logs; 4 found-dead — NONE NEW, NONE REOPENING (the A3 specimen already reopened; three
  previously-caught). Blast radius of the dead transonic PC mapped across every archived M6 adjoint log; retroactive
  annotations + the F5c SIMPLEC caveat + secondary record fixes ordered and in progress. Structural finding: four
  lever classes have no possible activity echo in stock logs — self-printing-banner instrumentation proposal filed
  for Infra adoption.
- AUDIT 2, MESH BIRTH CERTIFICATES (f41e969f): 178 unique meshes swept (from 5,303 dirs; dedup by points md5);
  105 pre-certified (spot-checks match digit-for-digit), 67 newly certified clean, 41+2 unreachable (listed),
  **exactly ONE born-broken — the known A3 vcoarse; the pyHyp pathology did NOT strike beyond the two specimens.**
  No numeric conclusion ever rested on the broken mesh. Biggest structural gap: the mesh cache stores bare polyMesh
  with no quality record — the entry-with-certificate proposal is filed with line-level insertion points; Infra
  adoption dispatched.
- HILLS MODEL-FORM MATRIX (c29a1a91): containment REFUSED at n=1 — the first live firing of no-containment-below-n3,
  by pre-registration. Family-convergence wall now has two geometries (bump 0/4, hills 1/4); kEpsilon's FPE crash
  class reproduced on the hills. Extension arm (30k cap, RUNNING) + paired FPE diagnosis (78495ab2) approved; the
  no-cap-chasing boundary pre-declared.
- A3 RE-FILE (0b4f3005): both levers L-40-proven active for the first time in M6 history; sub-LU is MEMORY-bound on
  M6 block sizes (>20 GiB, zero KSP blocks) — the agent's refusal to call a memory death a conditioning confirmation
  is quoted as precedent. PC-alone arm approved and RUNNING (the never-active lever solo, in the known envelope).
  New DAFoam finding filed for pricing: pyDAFoam silently warm-starts every rerun (writes primal end state into
  time 0) — the L-40 hazard in the state dimension.
- COMMIT-EVERYTHING SWEEPS at Katie's order before she stepped away: cd34b0a7 + 7475417d; tree clean at that point,
  subsequent agent landings layer on top.

### 2026-08-08 (evening) — seventh fleet death survived; Katie's capability strategy adopted
- SESSION-LIMIT KILL #7 (~03:40 UTC, reset 6:40am; Katie returned 22:22). The box survived 19 hours with both
  keepalives expired (resident servers held the busy pattern); zero scientific loss — every in-flight arm had its
  pre-registration committed. Session keepalive re-armed. Five agents resumed with kill states: Cases (extension-arm
  records on disk uncommitted — grade + containment statement), dead-lever auditor (annotation files mid-write in
  tree — verify hunks, finish, commit), Infra (mesh-certificate adoption mid-verification), A3 (negative control
  never launched — from pre-reg), S1 (weighted runScript — reconcile control/FD-gate state from its ledger first).
- CAPABILITY STRATEGY ADOPTED (docs/CAPABILITY_STRATEGY.md, 47e52caa): Katie's five-section program — self-improvement
  machinery, hard numerics (proven-by-solving-our-own-problems), probability/UQ as the moat, performance, sequencing.
  Read carefully: "Now-to-send: Ladder V only" holds the send queue for Ladder V alone (NOT an unpark; submissions
  stay parked until Katie says send). §1 slow-burn started per rule 3: the improvement dashboard + calibration
  scorecard agent is running its first monthly cut from existing records, including the pre-registration
  confidence-line proposal that starts capturing what reliability curves need. §2/§3 proven-by items map onto live
  work already moving (A3 preconditioning → Saad proof case; pyHyp characterization + birth certificates → mesh
  science; S1 → Bayesian inverse problems); each enters the docket with its proxy as hard criterion.

### 2026-08-08 (night) — entry 8 closes record-grade, and the lab measures itself for the first time
- ENTRY 8 CLOSED (551a7ba5/e4280b79/9bb948b2, review 7376ccc1): the negative control reproduced the record M6 failure
  BIT-FOR-BIT (entire stall sequence, terminal denormal, every digit) from the same starting state as the converged
  arm — identical state, opposite outcomes, one token. The FD table makes the M6 gradient a usable number (AoA 0.18%,
  max-gradient component 0.93%, two small signals honestly unverdicted); the adjoint is bit-reproducible across three
  runs. The warm-start audit: every record-grade conclusion COLD-CLEAN; two non-load-bearing warm flags ruled (no
  regrade on R5/M6 dumps; D3 variant nulls require cold rerun before citation). The A3 ladder climbs on as normal
  family work; the Opus .tex owner is reshaping the M6 chapter now (conditioning-wall → dead-lever with measured
  epilogue).
- FIRST IMPROVEMENT DASHBOARD + CALIBRATION SCORECARD (5b58d684, strategy §1 slow-burn): repeat-incident rate 2/40
  lessons (5%); lessons→preflight conversion 10/40 full + 10 partial (the one repeated-and-unenforced lesson, L-1/L-39
  reconciliation sweeps, named priority); median time-to-root-cause 58 h (range 0.09 h → 214 h, the dead lever);
  re-audit survival 307/315 pooled (97.5%) with the negative-verdict level reported separately at 4/7; orphans counted
  honestly (9 one-off dirs + 299 unledgered batch samples + 1 orphaned pre-registration). Calibration: N=98 graded
  predictions, 61% held; cost median ~0.77 record-level with exactly two factor-3 breaches; the basis-split finding
  ("the predictor is the basis, not a factor": measured-basis worst 1.84×, forecast-basis worst 13.55×); ZERO
  predictions carry numeric confidence but verbal-ordinal hedging is measurably well-calibrated (the flagged-weakest
  clause repeatedly the one that failed — five instances). Confidence-line proposal filed so the machinery starts
  capturing what reliability curves need; committee-grids held-count contradiction filed for correction.

### 2026-08-08 (late night) — the L-40 loop closes: lesson to charter to audits to adopted machinery in one day
- BOTH STANDARDS ADOPTED (ea0f7d9d + 4a8c92b4, suite 1210/0 over both together): mesh birth certificates live at all
  FOUR cache/entry chokepoints — the Infra verifier found a fourth the proposal missed (shock_bench's module-level
  cache) — with hash-bound certificates, quarantine-at-lookup, refuse-launch-pre-solve, R12 exemptions preserved, 22
  new tests; lever instrumentation live as lever_echo.py (sha256-bound echo blocks, hard-fail on unrecognized values,
  mechanical `levers_verified_active` builder wired into the shared solver runner and both model-form record paths,
  schema-via-Infra for the Cases family). MESH_STANDARD v1.1; family guidelines v1.1; every verification done with
  the adopter's own hands (born-broken specimen reproduced digit-for-digit; the no-echo claim retested on a LIVE log).
- The full L-40 arc, for the record: Katie's order (morning) → LESSONS L-40 + Verification Charter v1.5 (7be0afc2) →
  dead-lever audit 126-verified/none-new (946e4a26) + mesh audit 178-swept/one-born-broken (f41e969f) → retroactive
  annotations landed (e9a651e9) → enforcement machinery adopted and green (ea0f7d9d). The gap the charter admitted
  ("nothing mechanical verifies a dispatch's levers") is now closed mechanically for solver launches.
- S1 LINE CLOSED end-to-end (8b7b6489): four fleet deaths spanned, zero lost work, every failed gate pre-committed,
  both wrong predictions graded with measured reasons; W1-only filed with its priors-design trigger; Stage 2's hold
  carries a named unblock.

### 2026-08-10 — the A3 ladder has two verified rungs, and the eighth kill changed nothing
- EIGHTH FLEET KILL (credit exhaustion, 2026-08-08 late → 2026-08-10 14:48). Zero loss again; keepalive re-armed.
- **A3 RUNG 2 (42,120 cells): CONVERGED + FD PASS** (4e982b4a / a4c448db). CD 987 iterations reason 2, CL 1171
  reason 2; FD stronger than rung 1 — all THREE components evaluable and step-consistent (0.0077% / 0.2740% /
  0.0172% against an 8.09e-07 noise floor), with the runtime picking the max-gradient component itself so rung 1's
  mis-parse hazard is closed mechanically. The archived mesh carried NO birth certificate and was QUARANTINED by
  MESH_STANDARD v1.1 until certified — the first `birth_certificate.json` sidecar minted in the lab, reproducing the
  08-08 sweep's row exactly. Attempt 1's `-3` (KSP_DIVERGED_ITS at exactly the default cap) was REFUSED as a wall
  claim and then proven a budget knob: attempt 2 reproduces attempt 1's iteration-1000 residual to TEN significant
  digits and then converges.
- COLLISION AND ITS LESSON (L-41, 6d852180): the chief dispatched a second agent onto rung 2 believing the incumbent
  dead — fleet agents are invisible to `pgrep` because they run inside the SDK server. Zero duplicate compute (the
  newcomer stood down pre-launch), and the collision produced free adversarial verification: an independent
  digit-for-digit checkMesh replication, an outside reading of the L-40/cold-start proofs, and a pre-answer
  prediction of CL convergence near ~1250 iterations — GRADED A HIT (actual 1171, conservative by 6.7%), now in the
  calibration cohort.
- PRICING BASIS CORRECTED WITH ITS OWN OVERRUN REPORTED UNSOFTENED: rung 2 cost 99.5 core-min against ~47 estimated
  (2.1× over) because iterations scale SUPERLINEARLY in cells (exponents 1.50 CD / 1.70 CL; per-iteration cost
  ~linear). Rung 3 (79,560 cells) is therefore priced at ~113 core-min and REQUIRES `gmresMaxIters` ≥ 4000 or it
  dies on the cap — the calibration finding ("the predictor is the basis, not a factor") applied to itself.
- STRATEGY FILED AS DOCKET WORK (0d070079): 19 proposals — all 15 §2/§3 proven-by items with their PROOF clauses as
  gradeable gates, plus the 4 remaining §1 machinery items; three stale premises in the strategy corrected in place
  (431f0071), including the finding that the BATCH family was never swept by the dead-lever precedent (sweep
  ordered). Nine pre-existing inbox files found silently refused at intake — repair ordered.

### 2026-08-10 (afternoon) — the dead lever claims a second victim, and this one was a remedy
- **R5's "STRENGTHENING REINTRODUCES COLLAPSE" IS OVERTURNED** (triage pre-reg cfd6b5ff, results 3ac8257e, 22.7 of
  35–45 approved core-min). With the transonic PC ACTIVE, ILU fill-1 (−35.9% / −34.7% iterations) and Richardson
  smoothing (−43.2% / −44.9%) are the two largest cuts on the board and NEITHER collapses. Mechanism: strengthening a
  preconditioner built around a term that should have been dropped made a bad approximation worse; drop the term and
  ordinary numerical intuition returns. So the dead lever produced not only a false causal sentence about the WALL but
  a false ANOMALY about REMEDIES, which the remedy ladder was then shaped around for weeks. A standing anomaly
  RETIRED rather than a new one added. Routed to the defect report's owner and to R5's face as a dated retraction.
  - **[CORRECTED SAME DAY, 5aa3a142 — this entry's scope was too broad and the chief's wording above is superseded.]**
    The rung-3 stage-0 transfer test reproduced R5's exact restart-boundary collapse signature **with the PC ACTIVE**,
    at rung 2, from the lever that had just won at rung 1. So R5's OBSERVATION stands and is now reproduced; only its
    SCOPE was too broad. Corrected statement: **the strengthening collapse is real and MESH-DEPENDENT** — Richardson
    helps at 21,840 cells (both arms finish inside ~one restart cycle) and collapses at 42,120. The dead lever still
    cost the causal sentence about the wall; it did NOT invent the collapse. The agent falsified its own retraction
    three minutes after committing it and corrected it as loudly as it made it, which is the discipline working at
    its best. A labelled-unproven restart-destabilisation hypothesis is on record with a falsifiable prediction
    (fill-1 should also collapse at rung 2).
- D3's 11 flagged variants RETIRED as superseded (8c9b06c7, 0 core-min): each null says only "this lever did not
  rescue a run whose preconditioner was off" — true about a baseline no future run will use. The audit's
  cold-rerun-before-citation rule is satisfied by never citing them; the reasoning is written at both sites so
  retirement cannot read as avoidance.
- RUNG 3 PRE-REGISTERED AND APPROVED (3e585b07, ~170–190 core-min staged): the 79,560-cell member was quarantined for
  lacking a certificate — as predicted — then certified clean (family signature identical across all three rungs, so
  rung 3 differs in SIZE alone). Lever choice L3/Richardson endorsed over the wall-cheapest L1 on the right grounds:
  at this rung MEMORY binds, and L3 is the only winner that buys its cut with none, while halving the cap
  requirement (4000 → 2500). Stage 0 (transfer test at rung 2) is mandatory and its failure branch — "lever benefit
  is mesh-dependent" — is pre-declared a real finding, not a fallback. The ladder-level question is pre-stated: two
  points define the exponent and cannot test it; rung 3 is the first chance to see whether cells^1.50 / cells^1.70
  holds or breaks, which is what any extrapolation toward production meshes rests on.
- AUDIT INSTRUMENTS AUDITED (L-42, L-43, d021ffb9): a rerun into an existing case dir destroys the prior run's lever
  evidence (record/log mismatch found, verdict survived by luck of agreement); and the batch sweep's first pass named
  the family's headline conclusion as its top dead lever purely because gzipped logs and gitignore hid the corpus —
  withdrawn with evidence, corrected to 133 verified / 0 dead. Standing consequence: every archive-wide audit states
  its reach, and any negative headline carries a positive control. The FIRST dead-lever audit's 16 unverifiable + 4
  found-dead rows are being re-tested with a reach-proven instrument on exactly that rule.
- NINE SILENTLY-REFUSED INBOX FILES REPAIRED (6daecbe3, intake 93 → 99 accepted) — including the calibration
  scorecard's own confidence-line proposal. Three files whose hardness floor nobody had answered got it by CHIEF
  RULING (existing-family, reasoning recorded) rather than by default; the agent was right to refuse to answer on a
  filer's behalf. Batch-family dead-lever sweep: 133 VERIFIED / 67 unverifiable / **0 found-dead** (0dd9e4f2).

### 2026-08-10 (evening) — the ladder finds its ceiling, and a found-dead verdict turns out wrong

- **RUNG 3: DIVERGED BY STAGNATION — the reopened ladder has a CEILING, bracketed between 42,120 and 79,560 cells**
  (111.0 of the approved 170-190 core-min). CD hit the 4,000 cap with the residual FLAT ACROSS 2,700 ITERATIONS —
  1.31x total reduction, relative change 3.79e-07 from iteration 1300 to 4000. [Corrected 2026-08-10: this entry
  first said "flat to nine significant figures", which overstates by three digits — the printed pair agrees to SIX
  (1.615246604817e-02 -> 1.615245992220e-02). Caught by the report's author re-reading the raw log rather than the
  record. The verdict is untouched; the false precision is not, because it would have been quoted onward.] The pre-registered budget-vs-wall distinction — written before
  either negative reason code was ever seen — does the work: rung 2's `-3` was 1,407x monotone descent and a raised
  cap fixed it; this one is flat and no cap fixes it. And it is NOT a memory death (11.65 of 22 GiB, host never below
  17 GB, no swap), which is exactly what makes a conditioning verdict SAYABLE here rather than NOT EVALUABLE. The
  ceiling is bracketed, explicitly NOT located.
- **THE EXPONENT BREAKS, by kind rather than degree.** Predicted CD ~2,570 iterations; actual is no convergence at
  all. A two-point slope in this family is a description of two points, not a cost law — extrapolation toward the
  399,360-cell class is now foreclosed BY MEASUREMENT rather than by caution. That is the ladder-level question
  answered, and answered against the optimistic reading.
- **STAGE 0 EARNED THE CAMPAIGN**: the transfer test failed in its worst pre-registered branch — Richardson, the
  rung-1 winner, COLLAPSES at rung 2 (both solves `-5`, exactly 0.0 at the first restart boundary) — stopping rung 3
  from launching on a lever that would have killed it, for 15.9 core-min. Stage 2 (FD) correctly not launched,
  conditional on stage 1 converging: ~60-70 core-min saved by a pre-registered dependency.
- **FD-2 IS REFUTED — a found-dead verdict was WRONG, and it propagated** (rider run at zero marginal cost inside the
  rung-3 container; reported ahead of the stages as ordered). SIMPLEC IS implemented for DASimpleFoam (primal
  `pEqnSimple.H:27`, adjoint `DAResidualSimpleFoam.C:189`, textbook `rAtU` form, confirmed in BOTH images). Root
  cause: an INCLUDE-BLIND grep — the original search scanned `DASimpleFoam.C` and `DASolver.C`, while the logic lives
  in the `.H` include and the `DAResidual` file. The file list, not the search string, was the defect. Blast radius
  actioned: A4's stated cause for its 22.05% cross-code gap is RETRACTED on its face (7ca80f8d) — the measured 22.05%
  stands, its cause is now UNEXPLAINED, and a controlled `consistent` on/off arm is filed not run. FD-1 confirmed
  with the provenance it lacked. This is the answer to the chief's own order that a wrongly-reopened conclusion be
  reported loudly: one was, and it is.
- CLOSURE CLAIM PROPAGATION COMPLETE (18120bf8): six surfaces carry the rank caveat with a common sweep token
  (`not statistically decided`); the executing agent split internal surfaces (which carry P(rank 1) = 68%) from
  PUBLIC ones in `dist/` (qualitative clause only) rather than publish an internal-by-its-own-gate figure while
  obeying a propagation order — judgment CONFIRMED by the chief. Ladder V's V8 gains the rank-claim criterion.
  Three intake proposals filed (mechanical EIG numerator, refuse zero estimates without a basis, duplicate check at
  intake); 20 further surfaces + the .tex's ten rank assertions are routed.
- GAIN-TABLE INVERSION: the note ARGUES AGAINST ITS OWN HEADLINE (n=4, two of them duplicate filings; drop those and
  the tier leads). Chief ruling: NO re-pointing of the weights on this cohort — fitting seven weights to 114
  outcomes graded by one agent is the in-sample move the lab refuses everywhere else.

### 2026-08-10 (night) — the two-day-old lever gate had a hole on the launch shape that matters most, and no record fell through it

- **THE L-40 GATE NEVER FIRED IN PARALLEL.** The lever echo adopted 2026-08-08 tested `args[0] in SOLVERS`, so an
  `mpirun -np N <solver> -parallel` launch — how every long campaign solve launches — produced NO echo block,
  silently, with no error. Found by a B-52 solver agent BEFORE use rather than after and fixed at `199e9d17`; the
  2026-08-08 entry's "closed mechanically for solver launches" was true only of serial launches, and this entry is
  the correction. Infra family guidelines v1.2 carry the gap, the fix and the rule a next adopter inherits.
- **THE FIX'S OWN NO-OP CLAIM IS REFUTED, by the supervisor's hands.** `199e9d17` argued "no caller passes mpirun";
  `sdk/workflows/rae2822_case9.py:946` does, through the same runner, whenever `ranks > 1`. Verdict: not a no-op —
  but harmless and strictly improving, because every consumer of that log reads it from the tail while the echo is
  fenced at the head. Method: an AST sweep over all 830 `.py` files for every literal placing a solver name past
  index 0, carrying its own positive control. Regression test added and proven against the old predicate (2 tests +
  3 subtests fail there, pass here); suite 1214/0, up from 1210/0.
- **CLAIMS INTEGRITY: ZERO AFFECTED RECORDS, and the reason is structural, not lucky.** All 13 recorded
  `levers_verified_active` claims re-verify exactly — file set and sha256 — against the echo block in the log of the
  run they record; zero records carry the field empty. The defect made the gate fail OPEN, so it could only ever
  suppress a verification, never manufacture one. **Five further echo bypasses ARE open and escalated**: four
  `subprocess.Popen` solver paths inside `tmr_verification.py` itself, plus `launch_solve.sh` keying its echo on a
  caller-supplied `--case` path that nothing binds to the directory the solve runs in — the one site in the sweep
  that could produce a FALSE POSITIVE rather than a false negative. Not fixed under two live solver agents.

### 2026-08-10 (night) — the ceiling survives its sharpest challenge, and the restart boundary keeps appearing

- **THE CONDITIONING CEILING HARDENS — branch B, against a bar set before the number existed** (pre-reg 85a56e40,
  result 0dc6a050, 47.7 core-min inside a 66-82 estimate). The chief ordered the one untried lever whose MECHANISM
  matched the failure — GMRES restart 200 -> 1000, everything else identical, so the first 1,000 iterations are a
  single uninterrupted Krylov cycle and the cap set at 1,200 so it could not repeat the 4,000-iteration burn. Result:
  **1.647x improvement at the graded checkpoint against a pre-registered 10x bar** — below even the 2-5x "nudge" the
  pre-registration had already classified as branch B in advance. A 5x window buying 1.6x, with ~20,000+ further
  iterations needed at the observed rate, is a ceiling and not a budget. The 42,120-79,560 bracket is unchanged and
  the claim is now STRONGER than when filed, having survived the challenge whose mechanism matched its failure mode.
- **Disclosed against the lab's own claim, because it is real:** the wider window DID buy something — descent
  persisted through the whole uninterrupted cycle where the 200-window was flat by ~500 — and then flattened at
  EXACTLY iteration 1000, the restart boundary. That is the **third independent time this campaign that progress
  dies at a restart boundary** (stage 0's Richardson collapse, stage 1's stall, this flattening). Recorded as a live
  pattern with its named test: a restart-FREE method, or restart >= 2000 (~11.4 GB of Krylov vectors), which needs a
  bigger box than this one. The standing uncertainty is stated honestly — this excludes a restart-budget artifact at
  an AFFORDABLE window; it does not exclude that a restart-free method would eventually converge.
- Calibration for the scorecard: predicted peak memory 16.3 GiB, measured **15.76 GiB — 3.3% error**, a hit; and the
  "flat to nine significant figures" phrasing was corrected to six at both source sites (0a9a850e) after the report's
  author re-read the raw log rather than the record. The author's own note is the right lesson: that is the only way
  this class of error gets caught.
- LEVER-ECHO ENFORCEMENT AUDITED BY ITS OWN FAMILY (d7780f6a, suite 1214/0): the fix's "provable no-op" claim was
  REFUTED (rae2822_case9.py:946 passes exactly the mpirun spelling it said no caller passes) — behaviour-bearing but
  strictly improving. **Claims integrity: NO affected record exists** — all 13 mechanical-verification claims across
  12 records re-verify by file set and sha256, with a planted-mismatch positive control proving the checker detects
  rather than rubber-stamps, and the reason is structural: the gate FAILS OPEN. But the sweep found a path that does
  not: `launch_solve.sh` mints its echo from a caller-supplied `--case` while the solve runs in the launcher's
  inherited cwd, so a mismatch would write an echo of dictionaries that never ran at the head of a real solve's log.
  **L-45** (105c0a41): a gate that fails open costs evidence you can still collect; a gate that fails false costs the
  ability to trust the corpus. Fix prepared now, landing on quiet so it does not race two live arms.

### 2026-08-10 (night, late) — the gate that could have failed FALSE is closed, and it never fired

- **L-45 CLOSED, and the exposure was checked rather than assumed: ZERO.** All 149 logs in the solve registry carry
  no echo block at all, and the newest registry artifact of any kind stamps `20260808T020454Z` — twenty hours BEFORE
  the echo landed in `launch_solve.sh` at `ea0f7d9d`. The false-positive channel was open and never exercised, so no
  corpus cleanup was owed. Positive control on the search: the same grep finds 11 echo lines in a known-present
  specimen. A null with a positive control is a finding; without one it is a hope.
- **WHAT IT WOULD HAVE DONE, DEMONSTRATED RATHER THAN ARGUED.** The pre-fix launcher, run from one case while
  declaring another, certified `div(phi,U) bounded Gauss upwind` — hash-bound, `parse_echo`-passing, reported as
  mechanical launcher-echo verification — for a run that actually used `linearUpwind grad(U)`. Five files, all wrong,
  all provable-looking. That is the manufactured verification L-45 names, produced on demand.
- **THE FIX: the echo is now emitted BY the launched process, FROM its own working directory**, in the same shell
  that then `exec`s the command (the `exec` is load-bearing — it keeps `$!` on the solver's real pid, which is L-6).
  `--case` survives only so the emitter can DISAGREE with it and refuse, and a refusal writes a fence carrying no
  BEGIN marker, so it reads downstream as `unverifiable` and can never be mistaken for a pass. The launcher's shell
  copy of the echo format is deleted: one implementation, the canonical Python one every record is built with.
  Eight new tests; the mismatch test fails against the pre-fix launcher with the five wrong hashes in its diff.
  Suite 1222/0 (from 1214/0). Infra guidelines v1.3, new §1.8 (derive evidence from what executed) and §4.
- **THE COUNT GREW WHILE WE COUNTED IT: eight solver-launch mechanisms, not six**, of which two emit the echo. All
  six gaps are false-negatives — they lose verifications, they cannot forge them — so nothing recorded is wrong.
  Filed as **P-4.1** (`PROPOSALS_OPEN.md` v2.5, the first proposal that file has ever carried under charter 4) with
  the migration priced: zero core-minutes, ~1 pass for the recommended half, and an explicit recommendation AGAINST
  the full consolidation for now because it touches the detached-solve protocol L-5/L-6/D12 exist to protect.

### Decision requests for Katie (standing)
1. File the prepared upstream `mdolab/idwarp#57` comment / bug report? (`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` ready.)
2. Closure-challenge submission: author names, reference URL, approval to email the steward (incl. the two ambiguity questions).
3. Result-priority decision sheet D0–D7; escalation free-spend threshold (P-7.1); AWS read-only role for P-6.1.
