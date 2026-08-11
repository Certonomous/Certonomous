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
      core-min. ~~Hump now blocked on convergence RATE vs memory envelope, not singularity~~ — **CORRECTED
      2026-08-11: the hump's adjoint boundary is UNCHARACTERISED, not diagnosed.** The account rested on one attempt
      killed at iteration 900 whose log contains `ConvergedReason` **zero times**; no allocation failure, no OOM, no
      PETSc memory error — the non-zero exit was the container stop, not a KSP verdict. So the rate was never measured
      to completion and the memory envelope was never shown to be binding. **We equally have no evidence the operator
      IS singular**; the honest statement is that no convergence was observed within the iterations we ran.
      Richardson-wrapped attempt staged; its "fresh budget" was never actually requested.
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
      below published precision and must never be quoted as per-case wins. ~~The number is INTERNAL and never appears
      in an external claim~~ **[SUPERSEDED 2026-08-10: the internal-only restriction was WITHDRAWN by chief ruling —
      an outsider recomputed the figure from public data in about a minute, so withholding it bought nothing and
      only looked concealed. The figure TRAVELS with the entry, and may never appear without its interval (2-100%
      at 95%) and the not-decided pairs.]** — and no surface, internal or outward, may print "rank 1" without it.
      → NEW ITEM (from this cross-off): **closure.html coherent rewrite** under Katie's GUI conventions — DONE
      (page is round-5 current; consistency re-verified by Ladder V rung V10, 49f71b8c).
- [x] alpha=15,AR14 status (superseded by round 5, kept for history): AR_14 is now 3 of 5 and best-on-board is 4 of 8
      after the priced-in-writing round-5 tie loss (+0.0029); the earlier "best-on-board with a 0.00003 lead" reading
      is obsolete — must not be reported as a comfortable win, and per V8's banned-claims list, not as "best-on-board"
      either.
- [x] Find out challenge policies / whether Certonomous can submit. DONE (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §1–§4):
      steward Ryley McConkey (MIT); no eligibility clause, no fee, no deadline, no scoring limit; leakage rule audited in code, not violated.
      Two flagged ambiguities: company name in Authors column; no license on benchmark/training-data repos.
      → NEW ITEM (from this cross-off): **[KATIE-ONLY — NO AGENT MAY COMPLETE THIS ITEM]** Submission send package.
      **This item is NOT a task on any agent's queue and crossing it off is not a goal.** A cold-start test on
      2026-08-11 named sending this submission "the most dangerous thing you could do tonight in ignorance", and
      named the mechanism precisely: *an agent optimising for a cross-off completes it.* The act is irreversible,
      carries the company name, and is reserved to Katie in two charters. The package is filing-READY and HELD; its
      headline is not statistically decided (P(rank 1) = 68%, 2-100% at 95%, a standing two cases wide). Katie fills
      author names + reference URL, approves,
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

### 2026-08-10 (late night) — the channel that could forge a verification is closed, and it was never exercised

- **THE FALSE-POSITIVE CHANNEL IS CLOSED** (ad7f9eb1, suite 1222/0). The Infra family did not argue the risk, it
  DEMONSTRATED it: running the pre-fix launcher from one case while declaring another produced five hash-bound,
  parse-passing files certifying `div(phi,U) bounded Gauss upwind` while the solve that actually ran used
  `linearUpwind grad(U)` — a manufactured verification, on demand. **Exposure checked rather than assumed: ZERO.**
  All 149 registry logs carry no echo block at all and the newest registry artifact predates the echo's arrival in
  the launcher by twenty hours; positive control confirmed the same grep finds 11 echo lines in a known-present
  specimen. The channel was open and never once exercised.
- **The fix is L-45 built into the design:** the echo is now emitted BY the launched process FROM its own working
  directory, in the same shell that then `exec`s the command; `--case` survives only so the emitter can DISAGREE
  with it and refuse. A refusal writes a fence with no BEGIN marker, so it reads downstream as `unverifiable` and can
  never be mistaken for a pass — the gate fails open by construction. The launcher's shell copy of the echo format
  was DELETED in favour of the canonical Python one, on the principle that two implementations of an evidence format
  are two things that can disagree about what was proved. The `exec` is load-bearing (it keeps `$!` on the solver's
  real pid — L-6, the trap this launcher exists to close) and a test pins it. Eight new tests, content-first, each
  verified to FAIL against the pre-fix launcher.
- The supervisor also **corrected its own v1.2 sweep** (one entry filed as a false negative was actually SAFE — the
  launcher redirects the command's stdout into the registry log, so for those runs the registry log IS the run log),
  and the launcher count grew from six to eight while being counted. All six remaining gaps are false-NEGATIVES —
  they lose verifications, they cannot forge them — so nothing recorded is wrong. Filed as P-4.1 (PROPOSALS_OPEN
  v2.5, the first proposal that file has carried under charter 4), zero core-min, recommending the targeted half and
  explicitly AGAINST full consolidation: the detached path is what every long solve uses and its PID/exit-file
  protocol is the L-5/L-6/D12 failure family, where a defect orphans solves rather than losing an echo.
- Infra guidelines v1.3, new §1.8: **evidence is derived from what executed, never from what was declared.**

### 2026-08-10 (night, late) — six launch paths that lost evidence are closed, and the one that would have risked runs is refused

- **P-4.1 RULED THE NIGHT IT WAS FILED: C+D approved, full consolidation (B) REFUSED**, on the reason the family filed
  it with, now standing policy — the detached path is what every long solve uses, its PID/exit-file protocol is the
  L-5/L-6/D12 failure family, and a defect there ORPHANS SOLVES rather than losing an echo. We do not accept a small
  chance of losing runs to buy a large certainty of gaining echoes. That is L-45's asymmetry applied to a migration
  rather than to a gate, and it is the second time in one night the same reasoning decided a question.
- **FAMILY CODE NOW HAS ONE LAUNCHER DEFINITION** (`tmr_verification._foam`) and one place that decides what counts as
  a solve (`lever_echo.launches_a_solver`). The four detached/watched solver paths route through the same emitter the
  sanctioned launcher uses; `coefficient_uq_plate.py`'s private `_foam` is deleted (behaviour proved identical —
  `_run_prefix()` resolves to exactly the `openfoam2606` the copy hardcoded, and additionally honours
  `OPENFOAM_RUN_PREFIX`); `naca4412_credential_repair.py`'s private `run()` is deleted rather than left unused,
  because a second launcher sitting in a file is a second launcher somebody adds a call to. Suite 1230/0 (from 1222/0).
- **THREE PROPERTIES OF THE DETACHED WRAPPER ARE LOAD-BEARING AND EACH HAS A TEST**, because each is one edit from
  being lost: the echo comes from that shell's own working directory (L-45); `$?` is read immediately after the solver
  so `solve.exit` still carries the SOLVER's exit code — a leak there would collect a failed solve as a successful one;
  and the emitter creates the log rather than Python pre-seeding it, so the callers' `if not log_path.exists(): raise`
  launch check still tests whether the shell ran. Pre-seeding would have silently made that safety check vacuous,
  which is the exact shape of defect this whole pass is about.
- **THE WORK FOUND ONE MORE, AND IT WENT LIVE WHILE BEING FIXED.** The `-postProcess` over-fire filed as *latent* in
  the v1.2 sweep became real the moment `naca4412` was re-pointed at the shared runner: `simpleFoam -postProcess -func
  yPlus` would have written a lever echo into a utility log. A solver binary that integrates nothing is not a solve,
  and keying on the solver NAME alone cannot see that — the same class of mistake as keying on `args[0]`, found by the
  consolidation that was fixing the first one.

### 2026-08-10 (night) — the Saad proof fails honestly, and the failure names a capability boundary

- **STRATEGY §2's FIRST PROOF CLAUSE: NOT MET, refuted by execution** (a9bb202d → dda82819 → 368996c3, 61.6 core-min
  against ~35 approved, flagged progressively at 45 and 58 rather than at the end). Diagonal spread does not
  discriminate on this case: **rung 2 spreads 14.40 decades and converges, rung 3 spreads 14.47 and cannot.** The
  agent killed the hypothesis it most expected to confirm, with a 6.2 core-min comparison dump of its own devising.
  Its chosen lever (Schwarz overlap 1→2) then failed the falsifier it had stated in advance — κ ratio 0.979/1.062,
  residual 3% WORSE — and it disclosed that this branch was written AFTER seeing the diagnosis and is therefore one
  notch weaker than the pre-registered ideal, rather than presenting it as pre-committed.
- **What the arm bought: an elimination table.** Method breakdown (true residual tracks recursive to 7–12 digits
  through the stall — faithful arithmetic, an operator that genuinely offers no progress), subspace size, field
  separation, geometric localisation (extremes LESS near-wing than average — the tip-TE pathology is not the driver),
  volume scaling, spread magnitude, Schwarz overlap, stronger PC application — every structural cause this build can
  reach, refuted by measurement rather than argument. Survivor: **κ ≈ 10¹¹, insensitive to every preconditioner
  parameter the build exposes.**
- **THE FINDING THAT OUTRANKS THE FAILED CLAUSE — a capability boundary, and a reportable one:** the remedies the
  evidence points to (two-level coarse space, `PCFIELDSPLIT`/`PCGAMG`, `lgmres`/`dgmres`) are UNREACHABLE because
  DAFoam's `KSPSetType`/`PCSetType` override `KSPSetFromOptions`. The standard PETSc escape hatch does not work, so a
  user who diagnoses their own conditioning correctly still cannot act on it. Routed to the defect report as a third
  diagnosability-class defect. Strategy §2's clause re-phrased by chief note (original retained unedited per L-44):
  *conditioning diagnosed to a stated mechanism and the chosen remedy either applied or shown unreachable, with the
  elimination table published either way.*
- The one reachable knob left unrun — `pcFillLevel: 1`, a −36% winner at rung 1 — was DELIBERATELY not run: the
  diagnosis never indicted dropped fill, so a convergence there would be knob-luck, and the chief's ground rule
  forbids dressing that as the proof. Approved separately as engineering, kept out of the proof.

### 2026-08-10 (night, latest) — three passes made the evidence exist; this one makes it survive the next run

- **L-42 ENFORCED, 0 core-minutes.** Every launch path in the shared runner destroyed the prior run's log — `_foam`
  opened it `"w"`, the three detached paths `unlink`ed it — so a rerun into an existing case took the record's
  mechanical `levers_verified_active` basis with it. `_supersede_log()` now archives an existing non-empty log under a
  UTC-stamped name before anything writes, following `launch_solve.sh`'s convention, which was the lab's only
  L-42-surviving path and survived it by accident of its registry naming. Exposure measured, not assumed: **90
  committed solver logs in reusable case dirs, 9 already carrying echo blocks, 111 reusable `study-b52-*` dirs with a
  closure arm live in them.** Suite 1239/0.
- **THE CASUALTY IS AMENDED, NOT RECONSTRUCTED.** `H_re10595_realizableKE/record.json` gains a dated
  `evidence_amendment` with **zero pre-existing keys changed** (verified key-by-key). The facts, from the artifacts:
  the record describes a 30,000-iteration run written 03:46:17Z; the surviving log ends at `Time = 12000` and was
  written 23:52:59Z by a later rerun whose own honest record sits beside it. **Nothing was falsified and no number is
  withdrawn** — the 30,000-iteration fields survive under `30000/`. What is gone is that run's log and everything only
  a log can settle, and it is gone **unreconstructibly, not merely unsupported**: the launcher echo did not exist
  until 22:59 that night, nineteen hours later. The amendment exists so the two runs' agreement is never mistaken for
  verification.
- **THE FIX NEARLY BECAME THE BUG, TWICE, IN OPPOSITE DIRECTIONS — both now written into the guidelines as rules.**
  (1) The first design pre-seeded the log from Python, which would have made the callers' `if not log_path.exists():
  raise` launch check pass whether or not the shell ever ran: **a fix that creates the artifact a check tests for
  disables the check, invisibly, with everything still green.** (2) The readable archive name
  `log.simpleFoam.superseded_<stamp>` would have been caught by five log globs in the repo, one of which picks the
  LARGEST match — an archive bigger than the live log would have been classified as the run. The stamp is a prefix,
  and a test pins it against all four glob shapes. Same rule, once at the guard and once at the consumers.
- **A "LATENT" FINDING IS A FINDING WITH A DATE ON IT.** Recorded in the guidelines at the chief's instruction, on the
  `-postProcess` over-fire that went live the same night in the very pass that re-pointed the script carrying it: when
  a finding is graded latent, write down **what specifically is holding it latent**, because that condition is a
  dependency and the next change is as likely to remove it as to preserve it.

### 2026-08-10 (late) — evidence now survives the next run, and the fix nearly became the bug twice

- **L-42 ENFORCEMENT LANDED** (2423e42b, zero core-min as priced, suite 1239/0): every family launch path now
  supersedes an existing log under a UTC-stamped archive before anything writes, so a rerun can no longer destroy the
  prior run's hash-bound lever evidence. Naming follows `launch_solve.sh` — the lab's only L-42-surviving path, which
  survived by accident of its registry design and is now the deliberate convention. The test that names the point: a
  first run's echo SURVIVES a second run that changes the levers, archive parsing to the original hashes and the new
  log to different ones. Empty logs are removed rather than archived; the archiver never raises (a lost archive costs
  one run's evidence, a refused launch costs the run).
- **THE FIX NEARLY BECAME THE BUG, TWICE, IN OPPOSITE DIRECTIONS — now L-46.** (a) Pre-seeding the log from Python
  would have made every caller's `if not log_path.exists(): raise` launch check vacuous, invisibly, with all tests
  green. (b) The readable archive name would have been picked up by FIVE glob-based log consumers, one of which
  selects the LARGEST match — an archive bigger than the live log would have been classified AS the run, turning an
  evidence-preservation fix into an evidence-confusion bug. The stamp became a prefix, pinned by a test. The second
  was found only because the first rule was applied deliberately, which is the argument for writing rules down.
- **The known L-42 casualty amended, not reconstructed**, and the facts came out sharper than first reported:
  NOTHING was falsified and no number is withdrawn — the 30,000-iteration fields survive on disk and the run did
  reach the count its record states. What is gone is that run's LOG, and gone UNRECONSTRUCTIBLY: the launcher echo
  did not exist until nineteen hours after the run, so the record carries no `levers_verified_active` and now never
  can. The amendment states the cell's standing is unchanged precisely so the two runs' agreement is never misread
  as verification. Charter §9's distinction applied exactly: *unreconstructible* is a different word from
  *unsupported*.
- **Latent-finding rule added** (guidelines §3.3): the `-postProcess` over-fire went live in the very pass that
  removed the condition holding it latent — so when grading a finding latent, WRITE DOWN what specifically holds it
  latent, because that condition is a dependency and the next change is as likely to remove it as preserve it.
  "Not exploitable yet" and "not a defect" are different verdicts.

### 2026-08-10 (closing) — the B-52 turn is withdrawn, and a convergence check that needs no residual

- **THE B-52 LADDER'S "TURN" IS WITHDRAWN AS A CLAIM (chief ruling), on two independent grounds.** (1) The
  pre-registered closure arm (f4ccfe92 / c12c876b, 23.7 of ~31 core-min) returned INDETERMINATE as its own
  pre-registration had predicted it might — but T_hi = 2.445 < 3.0 **EXCLUDES SIGNAL**, which is exactly what the
  audit needed. (2) The decisive fact needs no statistics at all: **the published turn is literally
  max(rung 6) − min(rung 7) of the eight draws.** Re-estimated from ALL of them the increment is
  **+8.2e-5 ± 1.2e-3 (t = 0.071) — 49× smaller than the published value, OPPOSITE in sign, and smaller than the
  ~1.8e-4 bias from not matching the two rungs' resolutions.** A selected extremum is not a measurement. The agent
  labelled this re-analysis unregistered; the ruling rests on the arithmetic of how the number was constructed, which
  needs no pre-registration to be true.
- **The agent WITHDREW ITS OWN approved extension ask** (+46.2 core-min): at the measured T̂ it would not have reached
  a verdict either, NOISE is unreachable at any n, and MARGINAL vs INDETERMINATE has identical consequences for all
  26 audit grades. Declining approved compute because the answer would not change a single downstream decision is
  the discipline working at its most expensive point.
- **L-47 — a convergence check immune to instrument error.** The F5c isolating arm (9eaefc7f / 881866b9) completed a
  2×2 factorial and found relaxation alone moves reattachment 4.224 H while the algorithm moves 2.911 H and does not
  clear its bar: **the SIMPLEC attribution standing since 2026-07-29 is MISATTRIBUTED, not merely unproven.** The
  general instrument is the finding: relaxation factors cannot move a converged fixed point, so two solves differing
  only in relaxation disagreeing by a factor of 2.6 is proof of non-convergence **that never consults a residual** —
  immune to the exact error class that started this thread (a record reading the linear solver's final residuals
  instead of SIMPLE's initial ones).
- F5c's three corrections landed as dated amendments across EIGHT records (7f4c2657), including LESSONS L-39 and a
  source docstring; the re-posed item is filed with `est_core_min` deliberately NULL, because recording a floor as an
  estimate manufactures the same false confidence the band ruling just corrected.
- Frozen-artifact ruling applied: exactly one of the four withdrawal targets was frozen (R4's pre-registration), left
  byte-untouched with the withdrawal placed on its results record. A boundary case was disclosed rather than hidden —
  the agent's own F5c pre-registration correction predates its outcome, which L-44 does not reach.

### 2026-08-10 (capstone) — the tenth candidate falls, and the A3 investigation closes with a precisely bounded unknown

- **NON-NORMALITY REFUTED — and it goes the OTHER way** (pre-reg 7783f603, results 15b64e81, **0 of a 25 core-min
  cap**: both operators were already on disk from the diagnosis arms, so the decisive measurement was 81 seconds of
  offline numpy). Normalized Frobenius departure from normality: **rung 2, which CONVERGES, measures 4.299e-03;
  rung 3, which STALLS, measures 2.651e-03.** Ratio 0.617 against a pre-registered bar of 3.0, with non-overlapping
  confidence intervals — the stalling rung is measurably LESS non-normal than the converging one, by 1.62×. A
  resolved difference, not a null from noise. **The agent's own fill-1 arm generated the hypothesis and its own
  follow-up refuted it** — the outcome it had written it should be most willing to report, and the one that arrived.
- Step 1 refuted the competing reading at zero cost, from logs already on disk: within-run variability of the Krylov
  condition estimate is at most 6.5×, while the fill0→fill1 jump is ~2.5e+07 — six to seven orders apart, so the
  estimator-artifact explanation cannot account for it. **Unplanned bonus control:** two different arms hours apart
  return near-identical estimates at matched iterations, validating the instrument's reproducibility AND
  independently re-confirming that doubling the Schwarz overlap did nothing.
- **Limitation stated because it bounds the claim in both directions:** this measures DAFoam's assembled `dRdWTPC`,
  not the matrix-free Jacobian nor the preconditioned operator whose normality actually governs GMRES — which this
  build never assembles. Honest scope: the non-normality of the operator DAFoam builds its preconditioner FROM does
  not distinguish the converging rung from the stalling one, and therefore fails to explain the table. It does not
  prove the preconditioned operator is well-behaved.
- **THE A3 INVESTIGATION CLOSES. Ten candidate causes tested and refuted by measurement:** method breakdown, Krylov
  subspace size, field separation, geometric localisation, mesh volume scaling, diagonal-spread magnitude, one-level
  Schwarz overlap, stronger PC application, ILU fill level, non-normality. The surviving statement: **the rung-3 wall
  is real, it is not memory, and nothing this build exposes — and nothing measurable on the operator it assembles —
  distinguishes it from the rung that converges.** What remains unexplained is now precisely bounded rather than
  vaguely open, and the capability-boundary defect (f29378d9) names why the next class of remedy cannot be attempted
  here at all without a source change. From "blocked at every mesh size, cause unknown" to that, in one campaign.

### 2026-08-10 (night, last) — the evidence machinery stops recording solutions, and a reported limit turns out not to exist

- **THE LEVER ECHO WAS 97.8% SOLUTION DATA.** On B-52 rung 6 the echo block was 24.6 MB of a 25.2 MB solver log —
  `0/U` 13.1 MB, `0/phi` 11.5 MB, exactly the two files `potentialFoam -writephi` writes. `0/` was echoed as "the
  boundary conditions", but after initialization it holds the BC specification (a lever) AND computed field values
  (not a lever, and `phi` is not a boundary condition at all). One rule fixes it — any `nonuniform List` payload over
  4 kB is elided wherever it appears, leaving its element count, byte count and sha256 — and the result is **24.6 MB
  to 8.5 kB, 2896x**, with every lever still verbatim. Suite 1247/0, 0 core-min.
- **THE SAME FIX CLOSED THE B-52 G4 FAILURE**, which was the same defect wearing a second face: the replicate-equality
  clause was comparing whole-file hashes of two SOLUTIONS on two different meshes, which can never be equal. Entries
  now carry two hashes — `sha256` still binds to the exact bytes on disk (never weakened, and tested), `lever_sha256`
  covers the lever content. On the two real replicates the file hashes still differ and **the lever hashes now match
  exactly**, while changing `noSlip` to `slip` still breaks equality.
- **THE FIRST VERSION OF THAT FIX FAILED ITS OWN G4 TEST** — the elision marker embedded the payload's byte count and
  hash, so every replicate differed through the very marker added to describe the difference. Caught by running the
  check against the two real cases instead of reasoning about it. Third time this campaign that a fix's own claim
  needed testing rather than believing.
- **A REPORTED LIMIT DOES NOT EXIST.** Five campaign paths were routed in as "solver launches via shell strings —
  either give them a vector interface or mark them permanently unverifiable". **24 of 24 commands contain ZERO shell
  metacharacters**: they are argument vectors spelled as strings, and the `bash -c` is there to source an environment
  `_run_prefix()` already resolves. The routing agent's principle (splitting an arbitrary shell string to decide what
  ran is spelling-keying, forbidden) is right and stays — it just does not bite once the call sites pass vectors.
  Filed as **P-4.2** recommending NEXT-TOUCH, and recommending AGAINST the permanent marking: a false constraint in a
  standard is worse than an open gap, because a gap invites a fix and a constraint forbids one.

### 2026-08-10 (closing 2) — the withdrawal executes, and a second family's turn moves under one redraw

- **THE 26 GRADES RE-RUN AND APPLIED** (5ba5db81, canonical record `B52_TURN_WITHDRAWAL_2026-08-10.md`): five
  promotions amend → WITHDRAW, no demotions. Final 8 withdrawn / 15 amended / 8 survive / ~152 sites in three
  no-action classes, applied across 16 files with every original retained and `R4_PREREGISTRATION.md` still
  byte-untouched. Guard constants and UQ fixtures unchanged per ruling — verified zero executable lines changed, 94
  tests green. The proposal GENERATORS were amended too, so a regeneration cannot reintroduce withdrawn text.
  **The reasoning worth keeping from the regrade:** *"X ± Y does not survive by widening Y when X is withdrawn"* —
  an uncertainty cannot rescue a central value that no longer exists.
- **A SECOND LADDER'S TURN MOVES UNDER ONE REDRAW.** Free sweep first: **9 of 12 stored ladders carry NO
  draw-scatter evidence at all** (none currently publishes a band, so nothing is presently wrong — but nothing is
  presently checked either). The agent picked Ahmed 25° on LOAD rather than exposure: its turn is the last leg under
  the cross-family claim the B-52 withdrawal broke, and its c3 end had **n = 1** — the exact weakness that killed the
  B-52. Pre-registered as the increment-movement test (e543bc5e) after catching its own reversed CI unpacking showed
  the cheap leg could not declare SIGNAL. **Result: one same-recipe redraw at c3 moves Cd by 5.83e-3 — 6.6× the
  increment the turn consists of, 60× the c4/c4b pair — and the re-estimated increment FLIPS SIGN, +8.9e-4 →
  −1.98e-3.** 6.8 core-min.
- Validated before believing: instrument checked against published values (two exact, others within 4e-7); the new
  draw is CLEANER than the original (skewness 1.50 vs 2.00); it CONVERGED in 203 iterations; and **Cl moves with Cd
  (+22%)**, i.e. a flow-state change rather than arithmetic. The 25° slant bistability is named as a hypothesis and
  explicitly NOT claimed.
- **The honest limit, self-imposed: n = 2.** The mesh gate refused all three third-draw candidates and the agent did
  NOT extend its own allowance to force one through. It therefore applied **no amendment** to the standing *"not one
  unlucky mesh"* headline — n = 2 is thin evidence to move a headline, and it left the ruling to the chief. Free
  second finding: the Ahmed recipe controls delivered cell count WORSE than the B-52's — locally anti-correlated
  with the requested product, with the published draw sitting at a local maximum.
- Self-correction, second of the thread: the audit's summary said 22 amendments, recounting the rows gives 20 (two
  split dispositions double-counted). Both of this thread's arithmetic slips were found by RECOUNTING rather than
  re-reading, which is the practice worth generalising.

### 2026-08-10 (closing 3) — the escape hatch opens, and L-40 turns up inside the upstream code

- **THE PATCH WORKS AND IS REGRESSION-CONTROLLED** (5e720034, 21.5 core-min against ~15, overrun recorded not folded
  in). **Gate A — the load-bearing one for upstream: PASS, BIT-IDENTICAL.** Rung 1 on the patched image reproduces
  CD 368 / CL 383, reason 2 on both, cold signature to all 16 digits — iteration counts are the sharpest equality
  test available and they did not move. **The override is NOT load-bearing**, so the defect report's recommended fix
  stands and needs no re-grading: the maintainer's first objection is now answered by measurement rather than
  assertion. **Gate B — restoration: PASS**; `-ksp_view` reports `fgmres` where the shipped build reports `gmres`.
  Image tagged distinctly, both prior images untouched and reachable, every arm records its image tag.
- **Gate B produced two upstream findings, and the second upgrades our own recommendation.** (1) Overriding the
  solver type resets family settings applied to the previous object — the view shows PETSc's default restart rather
  than the configured 200 — correct "user override wins" semantics, but it must be documented, and in the test that
  small restart turned a 368-iteration convergence into a 1000-iteration failure. (2) **The build's own info echo
  goes STALE under an override: with fgmres in force the log still prints `Solver Type: gmres`.** That is **L-40 in
  its purest form, found inside the upstream code** — the switch you set is not the switch that ran, printed by the
  program itself. Revised recommendation: the reordering fix PLUS an effective-value echo read back after the
  options call. The first restores the user's control; the second restores their ability to verify it, which is the
  whole point of a diagnosability fix.
- Stage 2 is unblocked: the class the diagnosis named and the build forbade (`lgmres`/`dgmres`, `gamg`, `fieldsplit`,
  complete-LU sub-blocks) is reachable at rung 3 for the first time — to be run as the first honest test of that
  class, explicitly not as a rescue attempt, with each override carrying its own restart setting so Gate B's lesson
  cannot be misread as the arm's result.

### 2026-08-10 (night, final) — the propagation sweep: eight lessons, four families, and instances in every one

- **THE DEBT WAS REAL.** Strategy §1 requires a lesson learned in one line to be checked against the others within a
  week; eight lessons (L-41→L-48) landed in two days with no propagation pass. The sweep found instances in **every
  family**, at 0 core-min. Full matrix with evidence per cell: Infra guidelines v1.8 §9.
- **L-42 IS THE LARGEST DEBT, EVERYWHERE.** BATCH: `model_form_batch.py:856,1242` copy solver logs into the committed
  `out_dir` with an unconditional `copy2` (plus `gzip -f`) while `record.json` beside them IS superseded 460 lines
  away — the exact mechanism of the H_re10595 casualty. CASES: 9+ sites. MARINE: `make_dambreak.py:270` +
  `run_dambreak.sh` clobbering every log. Exemplar to copy: `R4_runs/run_c3_replicates.py:117` cites L-42 by name and
  refuses to re-stage a completed solve.
- **THE SWEEP FOUND TWO HOLES IN THE L-42 FIX ITSELF**, both mine, both now closed with tests: the settle-watched
  launch path got the lever echo added and the archive call forgotten, and `_copy_best_effort` — the shared archiver
  for the F5 ladders and four workflows — overwrote the committed copy. Fourth instance of L-46's shared form in one
  campaign, second where the author's own claim was the thing under test. Suite 1250/0.
- **AND ONE IN THIS FAMILY'S OWN PROCEDURE.** Infra guidelines §1.5 carried the resume ordering L-41 names as WRONG
  for two days after the lesson landed — pgrep first, git log nowhere — and it was edited to v1.7 without anyone
  noticing. Corrected. The same wrong ordering sits in `ESCALATION_CHARTER.md:416` and `PROPOSALS_OPEN.md:905`, both
  chief-owned and routed rather than edited.
- **ONE FAIL-FALSE CHANNEL FOUND (BATCH), AND A DELEGATED SWEEP HAD CALLED IT SAFE.**
  `model_form_batch.assert_mesh_certified_at_entry(..., fallback=)` satisfies the mesh gate from a caller-supplied
  SECOND directory with no hash binding, bypassing the hash-bound `certificate_admits()` that exists so "a certificate
  cannot drift onto a different mesh". Real, unexercised, used cross-family by GEN_ALT and FPE_DIAG. The delegated
  agent's null was a claim about its reach — L-43 demonstrating itself inside the sweep checking for L-43.
- **L-47 IS THE CHEAPEST UNCLAIMED INSTRUMENT IN THE LAB**, available in three families and used in one. The standout:
  `F6b_ERCOFTAC_RESULTS.md:171` NAMES THE GAP ITSELF — "may simply need tighter under-relaxation… should be tested
  first" — while its reattachment claim stands at **+63% to +66% against reference**.
- **L-44 IS CLEAN, AND MEASURED**: all 50 tracked pre-registrations and rule freezes checked by commit history — 26
  post-freeze edits add only, 3 touch existing lines and all 3 survive inspection, one of them correcting a document
  *against its own interest* ("written before launch" → "after it, not before").

### 2026-08-10 (closing 4) — the Ahmed turn goes too, and the replicate check is four for four

- **CHIEF RULING: the Ahmed 25° ladder's turn is WITHDRAWN as a feature**, on the same standard applied to the B-52.
  At n = 4 (pre-reg f4dec659, results 573e5793, 11.4 core-min) the DISSOLVES branch is confirmed — the increment
  inverts, sign flipped, −8.907e-4 — and the sensitivity analysis makes the withdrawal robust to which draw is
  excluded: **the published increment does not survive either way, it inverts or halves.** The fact needing no
  branch at all: with the suspected outlier REMOVED, the c3 scatter is 1.01× the entire c3→c4 increment. **The turn
  is unreadable from single draws in either direction.**
- The *"not one unlucky mesh"* sentence keeps its wording — it is literally true and now argues the OPPOSITE of what
  it was written to argue: the scatter is broad (branch B3, R = 0.324 against a bar calibrated by simulation as the
  10th percentile of the pure-scatter null), so the defence fails not because one mesh was unlucky but because no
  single draw carries the increment. The dated caveat a reader meets BEFORE the claim is landed (4f73e0af).
- **The near miss was reported as a near miss and the bar did not move:** R = 0.324 sits at the 14.6th percentile,
  and a bar at the 15th would have read B2 instead of B3. The bar was fixed before the draws existed and stays
  fixed; the ambiguity is stated rather than resolved by hindsight. The extreme draw was a REDRAW, which points at
  the recipe without reaching the bar.
- **THE FILED RULE'S ARGUMENT IS THE STRONGEST FACT OF THE DAY: every replicate family this lab has ever measured
  returned a material finding. FOUR FOR FOUR — the check has never once come back clean.** B-52 (turn withdrawn),
  NACA 0012 (the published mesh was the family maximum at +1.35σ), NACA 4412 (scatter 5.8–12.7% of the mean), Ahmed
  (increment inverts). Filed as `w3-no-ladder-feature-without-draw-scatter` (8801bf61) with its archive replay as
  its own entry condition. **Retrofit priced from measured bases at 12.8–21.7 core-min for the whole remaining
  scope — less than checking the B-52 alone cost (40.9, which ended in a withdrawal).**
- Scope self-corrected again: the "9 of 12 unchecked ladders" figure was wrong — 4 of the 12 stored studies carry no
  ladder at all, so it is 8 real ladders, 3 already checked, **real retrofit scope 5**. Found by RECOUNTING, which
  is now §7 of the Cases guidelines: *a recount is a fresh measurement, a re-read is the same measurement repeated.*
  The rule caught a third error within the hour of being written.

### 2026-08-10 (closing 5) — the audit's own count was wrong, and the reason is the day's own defect class

- **THE LADDER-FEATURE REPLAY OVERTURNED ITS OWN NUMBERS** (dd3cac8d), reported rather than resolved. Live records
  asserting a ladder feature: 16 → **32**. Evidence at the deciding rung: 4 → 8. Would be RESTATED: 5 → **17**, a
  RESTATE share of 50% → **77%**. Withdrawals: **still 5, none new** — so the rule remains cheap discipline, now on
  a correct denominator. The agent's pre-registered prediction P2 scored FALSE on its undercount and TRUE on the
  reconciliation: **the prediction was right and the measurement was wrong.**
- **Why the first route failed, and it is L-49:** its pattern spelled the concept the way the records it had spent
  the day inside spell it, so tested against nine genuine assertions the second route found, **it caught one**. Nine
  whole bodies were invisible (Ahmed 35°, motorBike, cube, TMR bump/flat-plate, lid-driven cavity, F7 dam-break, F4
  hypersonic, F3 wedge, F6b ERCOFTAC). **The failure was biased, not noisy — a search built from what you have been
  reading returns what you have been reading, and it feels exhaustive while doing it.** This is the day's own defect
  class (spelling-keyed detection) in a THIRD instance, written by the author into the audit that was checking for
  the first two. New guideline §7a: "a different route" must differ in KIND, and the test before trusting a count is
  *could this method have found a member of the class I have never seen?*
- **Consequence flagged, not silently absorbed: the filed rule's retrofit price UNDERSTATES.** The 12.8–21.7 core-min
  figure covers only the five unchecked ladders in the curriculum studies; the reconciliation surfaced ladder
  features for bodies whose ladders live only in campaign records (F3, F4, F7, F6b, TMR bump, the cavity, DPW8),
  outside the priced scope. Each needs its own measured solve cost — flagged for separate pricing rather than
  guessed at.

### 2026-08-10 (closing 6) — the unreachable class is tested at last, and fails: twelve eliminations

- **STAGE 2: BOTH ARMS FAIL — the eleventh and twelfth eliminations** (0fcc98a0 / e1755100). Run on the patched image
  with the control's own script so `PETSC_OPTIONS` was the only difference, and **both reported the control's exact
  iteration-0 residual**, establishing commensurability by measurement rather than assumption. `lgmres`: `-3` at 400,
  residual 5.10× worse than control and 3.88× above its own start (the anomaly of a RISING residual flagged rather
  than binned — the arm cannot separate genuine divergence from an augmented-recurrence reporting artifact, and does
  not need to, since under either reading it neither converged nor descended). `gamg`: `-5` at 200, exploding 180
  orders after barely moving; memory never a factor at 7.0 GiB.
- **Bounded exactly as ordered — this is not vindication and the scope is narrower than "the class fails."** Two
  off-the-shelf members at documented defaults on a convection-dominated nonsymmetric adjoint; AMG's defaults target
  elliptic/SPD-like operators, so arm 2 says *off-the-shelf AMG fails here*, not that a coarse space cannot work. A
  physics-appropriate coarse space remains untested and is not cheap. The shipped-toolchain ceiling stood on its own
  and nothing on a patched image revises it.
- **What the arms proved beyond their verdicts: the escape hatch works on BOTH axes** — the readback showed
  `type: lgmres` with the explicit restart holding, and `type: gamg` with `levels=4` multiplicative V-cycles, i.e.
  the patch unlocks an entire PRECONDITIONER FAMILY and not merely the Krylov type. **That is the defect report's
  cost made concrete: a user reaching for either gets silence on the shipped build, and these two arms are what they
  would have been unable to try.**
- **Third independent instance of a methodological caveat:** the condition estimate read 2.70e+05, 9.57e+10 and
  7.71e+17 across arms whose behaviour ranged only from *stalling* to *worse* — six orders of spread over no
  behavioural difference, on top of fill-1's 10⁷ improvement buying 1.9×. **Three arms now say the same thing: this
  estimate is not the instrument for this question.**
- Two disclosures the agent volunteered rather than passed over: the shared runner hardcodes a 16 GiB container cap
  while the pre-registration stated 22 GiB — never approached (7.0 GiB peak) so it had no effect, but **running
  something other than what was pre-registered is recorded**, and it is L-40 in the memory dimension (routed to
  Infra). And stage 2 came in at 124.4 core-min against ~52 (2.4×), arm 2 alone 4.1× over, with a nameable cause —
  both arms priced off an ILU per-iteration basis when AMG's hierarchy setup bears no relation to it — and a
  correction for any future AMG arm: **price the setup phase separately and cap on wall, not iterations, when
  per-iteration cost is unknown.** The agent stopped arm 2 at its graded solve rather than spending ~30 further
  core-min on this family's known false-success path.

### 2026-08-10 (closing 7) — a refutation audited before it propagated, and the DAFoam family rests

- **THE AGENT AUDITED ITS OWN REFUTATION BEFORE IT TRAVELLED** (7.0 core-min, self-executed under threshold; f61222ae).
  Its FD-2 correction rested on a source read plus a config read — **the same evidence class as the wrong verdict it
  corrects** — so it measured instead: one token flipped on a small case gives 435 iterations to tolerance with the
  flag off, 490 with it on. **The flag is ACTIVE, proven by behaviour rather than by reading**, the refutation now
  stands on three legs with the third of a different kind, and no correction is owed on the material already routed.
  Recorded as **L-50**: a correction must not travel on the evidence class of the thing it corrects — two source
  reads disagreeing is a disagreement about reading; a source read and a measurement agreeing is a finding.
- Bonus of the same shape: the converged objectives agree to 7–8 significant figures, which is the expected
  algorithm relationship (different path, same steady state). The retracted claim had been that the two algorithms
  *land on numerically different steady states* — requiring genuine bistability AND different attractors, far
  stronger than "the codes differed", never demonstrated, and moot because both runs used the same algorithm.
  **A4's 22.05% gap remains genuinely unexplained**, as its record says.
- Overrun disclosed at full occupancy: 7.0 core-min against ~2, entirely two setup misfires (assuming a rank count
  instead of reading the decomposition dict, then re-running before clearing a stale one). Configuration mistakes
  billed as compute, named as such.
- **THE DAFOAM FAMILY RESTS.** The agent declined to manufacture work: A3 closed at twelve eliminations, the defect
  candidate and branch-taping class are filing-ready and held by policy, two findings are routed to other families,
  and the single defensible remaining item (~29 core-min) is a hypothesis tidy-up that **would not change any
  verdict**. Chief ruling: **DECLINED** — the same standard applied all day, that compute which cannot move a
  decision is not spent.

### 2026-08-10 (night, closing) — a runner that overrides a declared limit without saying so is L-40 in the resource dimension

- **THE DEFECT IS THE SILENCE, NOT THE NUMBER.** A DAFoam arm pre-registered a 22 GiB cap; the runner applied 16 GiB.
  Peak was 7.0 GiB so nothing was affected, and it surfaced only because one agent stated a number and another
  compared. Same shape as an echo certifying dictionaries the solve did not use: the record said one thing, the
  execution did another, and nothing in between raised its hand.
- **THE REPORTED INSTANCE IS NOT IN CODE THE INFRA FAMILY OWNS**, and looking for it found something worth more:
  `DEFAULT_MEM_GB` is 12 and no `--memory=16g` literal exists in `sdk/` or `scripts/`. The cap lives in **four
  UNTRACKED shell scripts in the run tree** (`img_run.sh`, `triage_run.sh`, `run_arm_a.sh`, `run_arm_b.sh`), each
  hardcoding `--cpus=4 --memory=16g`. **Those launchers' resource policy is not in version control at all** — no
  review, no diff, no history covers the numbers that bind every A3 arm. Routed to DAFoam.
- **TWO WORSE INSTANCES FOUND IN THE RUNNER INFRA DOES OWN, both fixed.** `docker_dafoam` carried
  `ranks = min(DEFAULT_RANKS, max(1, ranks))` — ask for more ranks, get fewer, silently, while the pre-registration
  AND the core-minute arithmetic (wall × ranks / 60) both go on citing the number asked for. That is worse than the
  reported case: a default versus an active clamp. Now a stated refusal. And `--cpus` was **never set at all** while
  DAFoam pre-registrations have declared `--cpus=3/4` for weeks — every one unenforced, nothing said.
- **THE INSTRUMENT: a RUNTIME-ENVELOPE block** at the head of each container step log carrying the EFFECTIVE memory,
  cpus, ranks, timeout and image. A limit nobody applied records as `UNCAPPED` rather than being omitted, because an
  absent line and an unrecorded value are indistinguishable to a later reader. A resource cap is a lever, and charter
  §9 says a lever is verified from the execution, never the declaration. Suite 1258/0, 0 core-min. Guidelines v1.9 §10.

### 2026-08-10 (closing 8) — the runner was substituting its own values, and the policy that overrode a pre-registration is in no version control

- **A SILENT RANK DOWNGRADE, worse than the instance that prompted the sweep** (16c3047e, suite 1258/0, zero
  core-min): the container runner carried `min(DEFAULT_RANKS, max(1, ranks))` — ask for MORE ranks than the default
  and you silently get fewer, **while the pre-registration and the core-minute figure (`wall × ranks / 60`) both go
  on citing the number you asked for.** The reported memory case was a default; this was an ACTIVE CLAMP, and it sits
  directly under the lab's cost arithmetic. Verified harmless in fact — both existing callers pass the default, so no
  published core-minute figure is affected — and now a stated refusal naming the alternative rather than a silent
  substitution. Asking for FEWER ranks is still honoured.
- **`--cpus` was never set at all**, while DAFoam pre-registrations have been declaring `--cpus=3`/`--cpus=4` for
  weeks. Every one of those declarations was unenforced and nothing said so. Now honoured when given.
- **The reported instance is not in version-controlled code at all — and that is the bigger finding.** No
  `--memory=16g` literal exists in `sdk/` or `scripts/`; the cap lives in **four UNTRACKED shell scripts in the run
  tree**. So the pre-registration is version-controlled and **the thing that overrode it is not**: no review, no
  diff, no history covers the numbers binding every A3 arm. Routed to the DAFoam family to reconcile. Reach stated
  honestly per L-43's corollary: the first sweep of the 65 GB run tree hit its timeout, and a timeout null is not an
  absence, so it was re-run scoped.
- **The rule adopted, and it generalises past resources:** *a runner may not quietly substitute its own value for a
  declared one — it honours it, or it refuses out loud, and either way the log records what actually bound.*
  Implemented as a fenced RUNTIME-ENVELOPE block at the head of each container step log carrying the EFFECTIVE
  memory, cpus, ranks, timeout and image; a limit nobody applied records as `UNCAPPED` rather than being omitted,
  because an absent line and an unrecorded value are indistinguishable to a later reader.
- Two defects closed in passing rather than left: the log archiver now lives canonically in one module (a second copy
  would have broken the one-implementation-per-evidence-format rule written three commits earlier), and the container
  step log now supersedes rather than overwrites — an unflagged L-42 site in the sweeping agent's own module. One
  item stays open and routed: **two launchers now disagree about what they enforce**, which is the
  two-implementations problem in its second instance.

### 2026-08-10 (closing 9) — the retrofit's binding constraint is not compute: it is whether the ladder is a ladder

- **THREE LADDERS RESOLVED AT ≈0.2 CORE-MIN against 4.8–8.2 approved** (79ab1765), and none of the budget was
  quietly returned — each disposition carries its reason. **ahmed_25 and ahmed_35: RESTATE on RECIPE grounds** —
  their own audit says *"TWO mesh recipes, and no knob moves twice."* A ladder that changes recipe between rungs is
  not measuring discretization at all, so drawing replicates would have **precisely measured the wrong quantity**.
  **motorBike: UNVERIFIABLE AT SOURCE** — the feature turns on the medium→production increment and the medium rung's
  case, recipe and mesh no longer exist. That is the third-outcome ruling firing exactly as written; forcing it into
  restate or withdraw would have manufactured a verdict.
- **The certification gate paid on the one rung that still exists:** the surviving production mesh had **no
  certificate and no checkMesh record until today**; minted now it reads clean at 353,688 cells with no hard errors.
  The prediction that the curriculum ladders had never been through that gate is confirmed.
- **Two pre-flight findings that changed the campaign before a single mesh was drawn.** (1) The scatter ratio has
  **essentially no power at n = 3** — the bar calibrates to 0.0754, requiring the two surviving draws to be nearly
  identical — so **the deciding statistic must be the increment-movement test**, which is what actually decided both
  the B-52 and Ahmed; the ratio is reported, not graded. (2) **A recipe audit must precede the draws, and it is
  free**: three of the five approved ladders have never had one and **the other two failed one**.
- The convention was transmitted to the other half as a **shared module with a fixed seed** rather than a message —
  so both halves derive the SAME bar rather than two that happen to agree, the same reasoning that put every lever
  echo behind one predicate. It reproduces the Ahmed verdict exactly as a regression check, and the near-miss
  precedent is written in as the standard: the bar did not move when the measured value landed at the 14.6th
  percentile against a 10th-percentile bar.
- **The rule is vindicated in the way that matters most:** it asked for evidence at the deciding rung and got back
  *"that evidence cannot exist"* — which is exactly the sentence it exists to force onto a published feature's face.
  The binding constraint on this retrofit turns out to be not compute but **whether the ladder is a ladder and
  whether its meshes still exist.**

### 2026-08-10 (closing 10) — a spurious turn appears 29% of the time under the null, and a deciding rung is deleted by design

- **THE CALIBRATION PRODUCED THE RULE'S BEST ARGUMENT.** Bar fixed at T* = 0.7183 σ̂ for a 10% false-positive rate,
  from 4M simulated trials with the n=3-vs-n=1 asymmetry modelled — and the same simulation says that **under the
  null, a spurious turn appears 29.0% of the time.** Roughly three ladders in ten will show a turn that is not
  there. That single number argues for §17 better than any argument the lab has made for it.
- **`naca0015_sail`: OUT OF SCOPE, verdict complete, 4.8–8.1 core-min NOT spent.** Every published record reports
  rung values, an observed order, a band and `conclusive: false` — no turn, no oscillation, no non-monotonicity
  asserted anywhere. The judgement call was stated so it could be disagreed with rather than discovered: the study
  json carries passing guard fields, and the agent reads those as internal verdict machinery rather than a published
  shape claim, **with the cost of disagreeing priced at 4.8–8.1 core-min**. It would survive scrutiny anyway on
  evidence already banked — n = 2 at production, scatter 138.8× its own iterative 2σ and 7.4% of the envelope it
  publishes, i.e. **an envelope measured conservative against its own mesh scatter**, the strongest draw record of
  the five.
- **`cube`: in scope decisively — and the rung its feature turns on NO LONGER EXISTS.** The feature is live on five
  surfaces, but the turn sits at the medium rung and that rung has no case, no points file and no dictionaries,
  because the study runner **clears the body-keyed mesh cache before each rung by design** so only the finest
  survives. The existing replicate pair is at the wrong rung and failed by its own account. Rather than draw against
  an unverifiable rung or declare defeat without trying, the agent pre-registered a **reconstruction gate**
  (02ee4a4d): regenerate through the archived code path, with the exact cell count 103,934 as the fingerprint
  standing in for the checksum the deleted dictionaries make impossible. Match → verified-by-fingerprint and draws
  proceed; miss or failure → unverifiable at source, both counts published. Its prediction: the turn does not
  survive — clearing the bar would require scatter below 0.639% of Cd, 5.7× tighter than the B-52's.
- **A generic mechanism, screened for the other half without grading their arms:** the same cache deletion means the
  retrofit's premise may fail on possibly three of five ladders. Evidence handed over as a screen, not a verdict —
  *"the split says I don't grade their arms"* — with the method attached so Cases can check its own cases.
- **Two record corrections flagged, not fixed:** two live records state a study directory was DELETED and **it
  exists**, with mesh and logs, so any conclusion resting on its absence needs re-checking. And the 2026-08-08 mesh
  audit's *"CERTIFIED (pre-existing record)"* means a checkMesh LOG exists — **not** that a certificate was written:
  zero `birth_certificate.json` files exist under any cube or sail path. The audit's certified count meant something
  weaker than it read.

### 2026-08-10 (night, tail) — the rank clamp had a twin one level up, in the launcher, on the same arithmetic

- **THE ENVELOPE WORK HAD A TAIL, AND IT WAS THE SAME DEFECT.** `launch_solve.sh --ranks` is a number the CALLER
  declares; the collector multiplies by it (core-min = wall × ranks / 60); **nothing checked it against the command.**
  That is the container's rank clamp with the clamp removed — cost still wrong, still silent, feeding every
  pre-registration, every cost grading and the calibration scorecard's measured basis.
- **THE LAUNCHER NOW READS THE RANK COUNT FROM THE ARGUMENT VECTOR IT IS ABOUT TO EXEC** (`-np N`) — the invocation
  itself, not a string to be split. Agreement is silent and prices on the observed value; disagreement prints a loud
  `RANK MISMATCH`, records `ranks` / `ranks_observed` / `ranks_priced_on` in the completion record and the
  RUNTIME-ENVELOPE block, and **prices on what RAN**; a command nesting a shell reports `UNVERIFIABLE` and falls back
  with the fallback named, because a number reported as checked when it was not is the whole defect.
  **Demonstrated: a run declaring 8 ranks while executing `-np 2` now records `core_min: 0.5`. It used to bill 2.0 —
  four times the truth, silently.**
- **ONE SUITE FAILURE, TRIAGED AND ESCALATED RATHER THAN COMMITTED AROUND** (Infra §1.2). `test_aircraft_optimization
  ::ShootRoundTests::test_the_fleet_comes_up_once_and_goes_down_once` fails on its `_SolvedApi` subtest, roster shape
  `[0, 14, 9, 0]`. **Not this pass's doing, established rather than asserted**: it reproduces with this pass's
  uncommitted files stashed, and the workflow contains zero references to anything touched. Diagnosis for its owner —
  `n_slots = min(granted, len(grid))` is 14 while `n_par = min(granted, len(finalists))` is 9, so the fleet changes
  size mid-run; the code comment states the contract as "it used to drop back to ZERO… and climb again", and
  `[0,14,9,0]` never returns to zero, so it meets the stated intent while failing the encoded `len(shape) == 3`.
  Whether the assertion or the workflow drifted is the owner's call. It also fails standalone every time, so its
  suite-green history implies an outcome that depends on test ordering.

### 2026-08-10 (closing 11) — five confounded ladders turn out to be one generator defect, with its fix already filed

- **THE SWEEP CORRECTED ITS OWN HEADLINE, TWICE** (3e1956e4), and both errors were FRAME errors rather than reading
  errors — now **L-51**. "Nobody had written the confound down" was false (two bodies carry an audit saying exactly
  that; the pre-flight had queried only the five retrofit ladders and generalised to bodies it never asked about),
  and "exactly one ladder is known to be a ladder" was badly wrong (the enumeration glob structurally could not
  reach the purpose-built replacement families, which live under other names). **Corrected picture: 5 confounded,
  ≥13 clean, 3 undeterminable, 3 not grid ladders.**
- **THE FINDING ONLY THE SECOND ROUTE COULD REACH, and it changes the shape of the problem entirely: all five
  confounded ladders come from ONE code path.** `geometry_study.py::refinement_rungs()` — whose own docstring admits
  that when the level floor would make two rungs identical, the coarser one *also scales the background divisions so
  the cell budgets stay distinct*. **The guard checks distinctness, not comparability.** So this is one generator
  defect with five downstream victims, not five independent failures — and **its fix is already filed as docket item
  #75**, with four of the five bodies already carrying a single-recipe replacement family.
- The verified fact stands on both wings: coarse→medium moves the background only, while medium→production holds the
  divisions exactly and moves surface, region and feature levels — so those rungs' differences cannot be read as
  discretization increments. The draw-scatter measurements on those bodies remain valid AS scatter; what does not
  survive is treating the stored rungs as a ladder.

### 2026-08-10 (closing 12) — the same defect one level up, on the same arithmetic, in the launcher just fixed

- **`launch_solve.sh --ranks` was the rank clamp with the clamp removed** (a39896cc): a number the CALLER declares,
  which the collector multiplies by (`core-min = wall × ranks / 60`), and **which nothing ever checked against the
  command that ran.** Demonstrated live: a run declaring 8 ranks while executing `-np 2` now records **0.5 core-min
  where it used to bill 2.0 — four times the truth, silently, into the same calibration record the lab prices all
  future work from.** The launcher now reads the rank count from the argument vector it is about to exec — the
  invocation itself, never a string to be split — and agrees silently, disagrees LOUDLY with both values and the one
  it priced on landing in the record, or reports `UNVERIFIABLE` with the fallback named when a nested shell hides
  the vector. A number reported as checked when it was not is the whole defect, so the null says so rather than
  guessing.
- A second-pass correction worth the pattern: the not-comparable case first rendered as `UNCAPPED`, borrowing the
  envelope's word for *no limit applied*. **Those are different facts**, and the envelope exists precisely so a
  later reader never has to guess which — it now reads `NOT_COMPARABLE`.
- **A suite failure triaged and ESCALATED rather than committed around**: an aircraft-optimization test fails on a
  fleet-shape assertion, established as not the sweeping agent's by reproducing it with that pass's files stashed.
  The diagnosis for its owner: the fleet changes size between two waves, so the observed shape **satisfies the
  contract stated in the code's own comment while failing the encoded assertion** — whether the assertion is
  stricter than the contract or the workflow drifted is the owner's call, and weakening a test without naming the
  moved contract would be a rail-bypass. It also fails standalone every time, which means its suite-green history
  implies an outcome that depends on test ordering.
- **The self-audit pattern is now at six instances, and the agent named the tell:** *"I have just fixed this class,
  so I am done with it."* The propagation sweep found the hole in its own L-42 fix; then the answer to "does the
  envelope work have a tail" turned out to be the same defect in the launcher it had just finished fixing.

### 2026-08-10 (closing 13) — the mesh-certificate coverage the lab believes it has is ZERO

- **ALL 105 ROWS MARKED "CERTIFIED (pre-existing record)" CARRY NO CERTIFICATE** (63533ee1). Every path resolves on
  disk; **105 of 105 hold a `log.checkMesh` and 0 of 105 hold a `birth_certificate.json`.** Corroborated from the
  other side: 33 certificate files exist anywhere in the tree, 29 written today, so only 4 predate today **and none
  is among the 105**. The operational consequence is the point: `certificate_admits()` requires the FILE, a
  `points_sha256` matching the mesh actually present, and an accepted verdict — a log satisfies none of them, so
  **the standard's own checker quarantines all 105**, which is exactly what happened unprompted to both M6 members
  and both retrofit ladders today. Honest restatement of the audit's headline: its 105 are **CHECKED BUT
  UNCERTIFIED** — the evidence exists, the artifact does not, and downstream machinery believes the word.
- **The meshes are not impugned and the audit's verdicts stand** — the defect is that "CERTIFIED" names an artifact
  that was never written. The fix is mechanical and needs no solver: `write_certificate` already accepts a checkMesh
  log and hash-binds the result, so a scripted pass can mint all 105 from logs the audit already located, with
  per-mesh failures (unparseable log, points changed since, hash mismatch) reported rather than papered over. Priced
  and offered rather than executed, since these are other families' cases; the audit's own proposal for it has been
  sitting unexecuted. **Routed to Infra.**
- **L-50 caught its own author within hours of being written.** Re-checking the "the evidence is gone" claim, the
  agent found its OWN correction had travelled on weaker evidence than the claim it corrected — it had written that a
  directory exists "complete with its solver log", repeating a survey summary it had not checked. Measured directly:
  the directory exists and was never deleted, and it contains **no log file at all**. So the original records are
  right in effect and wrong in their stated reason; the finding they support never rested on the absence and is now
  re-verified at source. What changes for readers is useful: **that case's mesh and solved state are available even
  though its log is not.**
- The 29% null-rate figure is ready for the charter with everything needed to quote it: 4,000,000 trials, a stated
  seed, the statistic written out, and the n=3-at-the-turn-rung versus n=1-at-the-neighbours asymmetry **modelled
  rather than assumed away** — which is why the bar is 0.7183 σ rather than the 0.6308 σ it would be with three
  draws everywhere.

### 2026-08-10 (night, last) — the rank channel never fired, and 105 meshes called CERTIFIED had no certificate

- **RETROSPECTIVE ON THE RANK CHANNEL: A MEASURED ZERO.** Of 146 completion records, 3 carry a rank declaration and
  **all 3 agree** with the `mpirun -np` the execution itself recorded — so no core-minute figure in the registry is
  mis-priced and nothing downstream of one is affected. Recovered by two independent routes (OpenFOAM's `nProcs`
  header; driver logs echoing their own commands), because the first returned nothing and **a null from one instrument
  is not an absence**; each route carries a planted positive control. The other 143 records carry no cost line at all.
  My own reach check had to be corrected mid-sweep when an `or ""` made an ABSENT line read as a value — seventh time
  this campaign the auditing instrument carried the defect it was auditing for.
- **105 MESHES MARKED "CERTIFIED (pre-existing record)" CARRIED THE LOG AND NONE CARRIED THE CERTIFICATE.** The
  standard requires the FILE, so `certificate_admits()` quarantined all 105 — which is what happened unprompted to two
  M6 members and two retrofit ladders. **95 minted, 10 refused and reported, 0 minted-but-refused.** 0 core-min.
- **THE REFUSALS ARE THE RESULT, exactly as ordered.** 7 rows are marked CERTIFIED while **the log each one cites
  parses to hard errors under the audit's own verdict rule** — three with **negative-volume cells**, and
  `tmr-bump-finer` at aspect ratio 2.23e6, above the pyHyp threshold. No certificate was written for them: minting a
  `broken` one would quarantine another family's mesh on a parser's say-so, and an absent certificate already
  quarantines it, so the ruling stays with the owner. 3 more meshes state no cell count of their own.
- **THE CROSS-CHECK WAS THE LOAD-BEARING PART**: every mint had to show the log's cell count equals the mesh's own
  `nCells`. Without it the pass would have re-created by hand the very drift the `points_sha256` binding exists to
  prevent. Provenance is on each file's face (`retrospective-from-archived-log`, log path, both mtimes, cross-check),
  and **6 of 95 rest on a log written before the points file** — disclosed, not relied on. The audit gets a dated
  amendment, not a rewrite; no verdict revised, no mesh impugned.
- **AND `launch_solve.sh` WAS NOT EXECUTABLE IN GIT.** The lab's only sanctioned launcher is tracked `100644`; it has
  worked solely because every working tree happened to carry the bit locally, and a fresh clone could not run it.
  Found because rewriting the file dropped the local bit and this family's own launcher tests went red. Fixed for the
  three scripts this family owns; **29 tracked scripts carry a shebang and no exec bit** and are reported, not
  mass-chmodded. Suite 1261/0.

### 2026-08-10 (closing 14) — the rank channel never fired, and the mesh audit's "exactly one born-broken" is SUPERSEDED

- **RANK RETROSPECTIVE: A MEASURED ZERO** (02475da2). Of 146 completion records, **3 carry a rank declaration and
  all 3 agree** — declared 4, executed `-np 4`. No core-minute figure in the registry is mis-priced, so no cost
  grading, factor-3 verdict or calibration-scorecard input is affected. The executed count was recovered by **two
  independent routes** reading what the execution itself wrote; **route (a) returned nothing on all three**, and a
  null from one instrument is not an absence, so route (b) carried it — with a planted mismatch caught by both.
  Reach stated: the other 143 records carry no cost fields at all, so no mis-priced figure can exist from them.
- **[PRECISION CORRECTED, same night, by the executing agent: the claim below is stated at its ACTUAL strength.
  What is established is that SEVEN CITED LOGS CONTRADICT THEIR ROWS — not that seven meshes are born broken.**
  `checkMesh` was never re-run on those meshes; the rows were refused at the verdict gate before the cell-count
  cross-check could run. If a cited log is stale or describes a superseded state of its mesh, the row could still be
  right and the log wrong — a different finding, and still one its owner needs. The audit's `BORN BROKEN: 1` was a
  statement about the set it re-parsed itself, sitting beside 105 pre-existing records it took on trust; what moves
  is the coverage that headline implied, not a verified count of broken meshes. The chief propagated the stronger
  version verbally and it is corrected here.]**
- **CORRECTION TO THIS MORNING'S HEADLINE — the coverage behind "exactly ONE born-broken mesh" is SUPERSEDED.** The minting pass refused
  10 of 105 rows, and **7 of those are a discrepancy in the audit itself**: each is marked CERTIFIED while **the log
  it cites parses to HARD ERRORS under the audit's own verdict rule** — three `rae2822-meshcheck` meshes with
  NEGATIVE-VOLUME CELLS, and `tmr-bump-finer` at aspect ratio **2.23e6**, above the pyHyp threshold and far above the
  NASA-grid signature the audit itself documents as a flag. The audit trusted pre-existing logs without re-parsing
  them; re-parsing changes the count. (3 further rows state no cell count of their own, so the cross-check cannot
  run.) **No certificate was written for any of the 10** — minting a `broken` one would quarantine another family's
  mesh on a parser's say-so, and an absent certificate already quarantines it, so the conservative action and the
  honest one coincide and the ruling stays with each owner. **95 minted, 0 minted-but-refused.**
- The cross-check was the load-bearing part: every mint had to show the log's cell count equals the mesh's own
  `nCells` read from the polyMesh header — without it the pass would have re-created by hand exactly the drift the
  hash binding exists to prevent, *the fix for a class being where that class reappears*. Provenance is on each
  file's face (`retrospective-from-archived-log`, log path, both mtimes, cross-check result), and **6 of 95 rest on
  a log written before the points file** — cell counts agree so size is unchanged, and the ordering is disclosed
  rather than relied upon.
- **A real over-count found and recorded rather than fixed:** each of the three declared launches ran serial meshing
  AND several parallel solves under one scalar rank declaration, so its `core_min` prices the serial phase at 4×.
  Different defect from the one being retrospected; named, not absorbed.
- **The lab's only sanctioned launcher is tracked as NON-EXECUTABLE** — it has worked solely because every working
  tree happened to carry the bit locally, and a fresh clone could not run it. Latent since the file was created,
  surfaced when a rewrite dropped the local bit and the family's own tests went red. Fixed for the three scripts
  that family owns; **29 tracked scripts carry a shebang and no exec bit**, reported rather than mass-changed.
- Seventh self-audit instance: the agent's own reach check had a fallback that made an ABSENT line read as a value,
  inflating its first count — caught by refusing to accept a surprising number.
- Closing figures corrected by the agent against the chief's summary: **eleven commits, not six**, and its family
  guidelines ran **v1.0 → v1.12, not v1.1 → v1.9**. Suite 1210 → 1261 / 0 failed stands. The self-audit count is
  **seven instances**, and the agent's closing note is the one to keep: *not one was found by suspecting myself in
  the abstract — every one came from running the check that would fail if the work were wrong.*

### 2026-08-10 (closing 15) — fresh measurement settles all seven: four rows wrong, three exonerated and certified

- **THE STALE-LOG HYPOTHESIS IS ELIMINATED** (8845be5f). Fresh `checkMesh` on all seven refused rows agrees with each
  cited log **exactly** — verdict, cell count, aspect ratio and the full hard-error list, to the digit. So the logs
  describe these meshes as they now stand, and **what is wrong is the rows, not the logs**. The stronger claim only
  became available with the measurement, and only then.
- **Four rows are WRONG.** Three `rae2822-meshcheck` meshes reproduce **negative-volume cells**, wrong-oriented face
  pyramids, non-orthogonality and skewness errors — broken meshes marked `CERTIFIED`. `tmr-bump-finer` is broken **by
  the standard's own aspect-ratio threshold** (2,230,928.97 against 1e6) and NOT by a geometric error — it has no
  negative volumes, a weaker failure, stated separately rather than blurred into the other three. **No `broken`
  certificate written for any of the four**: an absent certificate already quarantines, so writing one buys no
  protection and asserts a verdict the standard does not need.
- **Three rows are EXONERATED and now certified.** The `w1-bump-nasa-grids` trio had been refused for a different
  reason — their `polyMesh` headers genuinely lack a cell count, as expected for converted NASA grids, so the
  cross-check could not run. **Re-running `checkMesh` performs that cross-check a different way — counting the mesh
  directly instead of reading a note about it** — and the counts matched the logs exactly. Certificates minted from
  the fresh run; three meshes move from quarantined to admitted. Permitted here where it is not for the four,
  because this is a NEW MEASUREMENT rather than a re-parse.
- **Frame stated first, and the corpus count deliberately NOT restated:** the finding covers exactly these seven
  meshes as they exist on disk at 19:19 UTC. Within that frame, four fail the audit's own verdict rule. **Nothing
  follows about the other 98** — and the agent refused to extrapolate a corpus figure from a seven-mesh frame,
  naming it as precisely the error its own recipe sweep made twice earlier today.
- Honest next question flagged rather than proposed: whether the 95 rows minted from archived logs deserve the same
  fresh-`checkMesh` treatment. Priced at ~0.07 core-min each, **≈7 core-min for all 95.**

### 2026-08-10 (closing 16) — 95 of 95 agree, and the parser says "clean" when checkMesh crashes

- **THE RETROSPECTIVE CERTIFICATES NOW REST ON FRESH MEASUREMENT** (d606ce6b): staged as ordered with the six
  ordering-flagged rows first, all six clean, then the remaining 89. **AGREE 95 · DRIFT 0 · did-not-run 0 ·
  hash-mismatch 0, at 3.49 core-min against ~7 approved.** The corpus stands on measurement rather than inherited
  paper.
- **A FAIL-FALSE CHANNEL FOUND IN THE CERTIFICATE MACHINERY, and it was found only because the agent tracked the
  right thing separately.** `parse_check_log` returns `verdict: "clean"` on a checkMesh **FATAL ERROR** — it matches
  error PATTERNS, and a log where the tool died contains none. **The only thing standing between that and a false
  clean certificate is `write_certificate`'s refusal when the cell count is `None`** — a guard that turns out to
  have been doing invisible load-bearing work. The agent caught it because its harness tracked *"did checkMesh
  actually run"* as a **separate column** from *"do the verdicts agree"*; the count came back zero, but it could not
  have been read off the verdict. This is L-45's category — a gate that can manufacture a pass rather than merely
  miss one — inside the machinery that now gates every mesh in the lab. **Routed to Infra; reported, not patched,
  because it is another family's file.**
- **Provenance defect self-reported and corrected:** the three exonerated certificates defaulted to `at-creation`
  and therefore claimed to have been written when the mesh was made. They were not. Corrected to
  `fresh-recheck-of-existing-mesh` with the reason on each certificate's face, and the same fix applied to one
  minted earlier in the day. **Neither existing provenance constant is honest for this case**, so a third belongs in
  the module — Infra's call, and nothing branches on the value meanwhile.
- **The four wrong rows corrected on the audit's face** (d4832a20), dated amendment with the original retained, and
  **the two failure modes deliberately kept apart**: three meshes with genuine geometric errors (negative volumes AND
  wrong-oriented pyramids, reproduced fresh) versus one threshold failure with **no geometric error at all**. Written
  so that a reader taking "four rows are wrong" to mean "four meshes have negative volumes" would be wrong about
  three quarters of it.
- The frame-first discipline caught its author again mid-task: a first scan for the six flagged certificates returned
  zero because the timestamps are nested one level below where it looked. Same class as the day's others — the
  method read its sample correctly and the sample was not the population.

### 2026-08-10 (closing 17) — the rule reaches the corpus, and a cross-solver rate is caught being a factor in disguise

- **THE 17 RESTATEMENTS ARE APPLIED** (a21d013f), so §17 has now touched the published record rather than remaining a
  charter section with no effect on the corpus. **Frame first, as the standing form requires: 17 restatements out of
  32 records asserting a ladder feature, out of 151 records scanned** — those 17 now state on their face that no
  replicate mesh has ever been drawn at the rung their feature turns on, and **nothing follows about the other 119**,
  the 8 with evidence, the 5 withdrawn or the 2 already compliant.
- Each restatement names the ladder's **recipe class**, because the class changes what the gap MEANS: on a
  **confounded** ladder the feature is unsupported twice over (its increments were never discretization increments at
  all); on a **clean** one the missing scatter is the only thing between the feature and a real measurement.
  **11 clean · 5 confounded · 1 undeterminable.**
- **A PRICING ERROR CAUGHT BEFORE IT WAS QUOTED, and it is the calibration finding catching its own author.** The
  first pass priced all seven remaining candidates from the two measured bases available — both **steady,
  incompressible `simpleFoam` on snappyHexMesh bodies** — putting F4 at 0.49–0.83 core-min. **F4 runs transient,
  explicit `rhoCentralFoam` to endTime 6.0.** A per-cell rate does not cross that gap. Priced instead from F4's own
  record (14.66 core-min across 9 runs at 1:4:16 cells): **≈7.5 core-min, 8.9× what the cross-solver rate said.**
  The agent's own words are the lesson: *the predictor is the basis, not a factor — and a per-cell rate borrowed
  across solver families is a factor wearing a basis's clothes.*
- **The other seven are DELIBERATELY LEFT UNPRICED.** Each needs its own basis read from its own record, and
  inventing a cross-solver rate for them is the error just caught. ~1 hour of zero-compute reading, offered rather
  than assumed.
- **F4 is the sharpest test §17 will ever get**: its record asserts that *"convergence with mesh refinement is
  explicitly NOT monotonic, and scatter does not fully explain it"* — **a claim ABOUT scatter, made without ever
  measuring scatter** — on a ladder the sweep classifies CLEAN (one knob moving, radial grading held), so the answer
  cannot be confounded away. Either outcome changes the record: scatter explains the non-monotonicity and that
  sentence is wrong, or it does not and the sentence is vindicated by measurement for the first time.

### 2026-08-10 (closing 18) — the pre-flight kills the approved run, and the rule's scope was wrong as adopted

- **F4's APPROVED 7.5 CORE-MIN: DECLINED, NOTHING SPENT** (d8a81e55). Checking before spending found the restatement
  wrong twice. **(1) F4's "scatter" is TEMPORAL scatter and it WAS measured** — reported per rung (3.5% coarse, 2.3%
  medium, 0.4–0.8% fine) as an explicit snapshot band from three late-time writes, with every deviation set against
  its own band. *"Scatter does not fully explain it"* means the resolution-to-resolution swings EXCEED those measured
  bands: a careful claim about a measured quantity, not the gap it was annotated as. **(2) Mesh-draw scatter cannot
  exist for that ladder** — its generator builds a deterministic structured polar O-grid, so the same parameters give
  a byte-identical mesh every time. **(3) The record had already named the true cause** (a resolution-dependent bias
  in the peak-gradient detector itself — the same class as the F5c reattachment-detector defect), diagnosed rather
  than left open.
- **AND THE WHOLE "CLEAN" SET COLLAPSES WITH IT.** All 11 campaign ladders restated as *clean, no scatter measured*
  use **deterministic structured generators**, verified generator by generator — so **the quantity the rule asks for
  is identically ZERO for every one of them.** All 11 restatements corrected, originals retained. Only the
  snappyHexMesh bodies have a draw distribution at all; those six restatements stand as written. **The priced
  shortlist collapses entirely** — the seven candidates deliberately left unpriced were all deterministic too, so
  the hour of record-reading I did not order would have priced measurements that cannot be taken.
- **§17 GAINS TWO SCOPE REQUIREMENTS, one of them because the rule was wrong as adopted:** a restatement names the
  **recipe class** (clean means one measurement away from real; confounded means unsupported twice over;
  undeterminable means neither can now be established) — and **the rule applies ONLY WHERE A DRAW EXISTS.** On a
  deterministic generator it is satisfied by STATING that, not by measuring; demanding a number that cannot exist
  would be the rule failing in a new direction. A related trap is recorded with it: **check WHICH scatter a record
  means before annotating it for lacking one.**
- **THE CASES QUEUE IS GENUINELY EMPTY, and the reason is a fact worth having:** of the six ladders where draw
  scatter exists and is unmeasured, four are confounded (measuring them would be precise measurement of the wrong
  quantity) and two are undeterminable (the rung cases are gone). **There are currently ZERO ladders in this lab
  where a draw-scatter measurement would be both possible and meaningful.** Second time today this agent declined
  approved compute; F5c remains honestly unpriceable and no number was manufactured for it.

### 2026-08-10 (night, reopened) — the mesh gate could mint a clean certificate from a crash

- **A FAIL-FALSE CHANNEL INSIDE THE MACHINERY THAT GATES EVERY MESH IN THE LAB**, found by the Cases family while
  re-checking all 95 retrospective certificates (95 agree, zero drift, half the approved cost). `parse_check_log`
  matched error PATTERNS, and a log where checkMesh DIED contains none — so it returned `verdict: "clean"`.
- **WORSE THAN REPORTED, established by reproducing it.** The cell-count refusal was described as the only thing
  standing between that and a false clean certificate; it is not even sufficient. **checkMesh prints its mesh stats
  EARLY**, so a run that dies during the geometry checks carries a cell count and passed both parser and guard — that
  shape mints a `clean` certificate outright with nothing in its way.
- **THE FIX: the parser asks "did the check run" before "what did it find"**, and returns a third verdict,
  `unverified`, on a fatal marker, a missing terminating `End`, or no cell count. Deliberately not `broken` — broken
  means checked and found bad, unverified means we do not know, and collapsing them would impugn a mesh whose only
  fault is a missing log. The completion marker is **calibrated, not guessed: 105 of 105 real logs end with `End`, 0
  of 105 carry a fatal marker**, and re-running all 105 after the fix leaves the split unchanged (90 clean / 8 flagged
  / 7 broken / 0 newly unverified). **Exposure zero**: none of the 95 minted certificates is affected, no revocation
  owed. Suite 1268 passed.
- **THE FIX BROKE ON ITS OWN CORPUS FIRST, and the check caught it.** A draft fatal pattern included `Floating point
  exception` — which appears in the STARTUP BANNER of a healthy checkMesh log — and misread all 105 real logs as
  crashes. The term was added AFTER the pattern was calibrated and before it was re-validated. Eighth instance this
  campaign of the same shape, and the standing rule earned it again.
- **THIRD PROVENANCE CONSTANT ADDED**: `fresh-recheck-of-existing-mesh`, matching the string the Cases family
  hand-wrote exactly, so its three certificates are already conformant. Neither existing constant was honest for a
  re-check of an existing mesh, and a provenance field that cannot express what happened gets filled in with something
  false by whoever next needs it.

### 2026-08-10 (closing 19) — the forgery channel was worse than reported, and the fix broke on its own corpus first

- **THE CHANNEL HAD NOTHING IN ITS WAY.** Reproduced before fixing: `checkMesh` prints its mesh stats **early**, so a
  log that dies in the geometry checks still carries a cell count. It therefore passed the parser as `clean` AND
  passed the cell-count refusal — the guard described as the only thing standing between a crashed run and a
  certificate **does not cover the live case at all**; it only catches a crash before the stats line. Such a log
  would have minted a clean certificate outright.
- **Fixed by asking DID THE CHECK RUN before WHAT DID IT FIND** (06f747e8, suite 1268 passed): a third verdict
  `unverified` when a fatal marker appears, when the log never reaches checkMesh's own terminating `End`, or when no
  cell count exists. **`unverified` is deliberately NOT `broken`** — checked-and-found-bad and we-don't-know are
  different facts, and collapsing them would impugn a mesh whose only fault is a missing log, the opposite error and
  just as wrong. The cell-count guard is KEPT as a second line rather than the only one, and a hand-rolled
  certificate path that inherited none of these refusals now states its own. **Completion marker calibrated, not
  guessed: 105 of 105 real logs end with `End`, 0 carry a fatal marker; re-run after the fix gives 90 clean / 8
  flagged / 7 broken / 0 newly unverified — the corpus split is unchanged. Exposure: ZERO**, all 95 minted
  certificates re-checked under the fixed parser, none reclassified, no revocation owed.
- **THE FIX BROKE ON ITS OWN CORPUS FIRST, and it is the most literal instance of the campaign's own rule.** A draft
  pattern included `Floating point exception` — which appears in the **startup banner of a HEALTHY log**
  (`sigFpe : Enabling floating point exception trapping`) — misreading all 105 real logs as crashes. The term was
  added AFTER calibration and BEFORE re-validation, and was caught only by re-running the calibration over the whole
  corpus rather than the single sample under test. **The fix for "you changed it, did you re-run the check" failed
  exactly that way.** Recorded in the module comment beside the pattern, so the next person to widen it sees what
  widening cost. Eighth self-audit instance of the campaign.
- **A quieter finding with a long tail:** three long-standing test fixtures turned out to be synthetic logs **lacking
  the terminator real `checkMesh` always emits** — standing in for output the world does not produce. Made faithful
  rather than relaxing the parser to accept them.
- The provenance constant was added matching the Cases family's hand-written string **exactly**, so their three
  certificates are already conformant and need no migration — and those are the same three meshes refused earlier for
  stating no cell count of their own, which a fresh check then supplied.
- **All three families now report AT REST, each having demonstrated it rather than asserted it.**

### 2026-08-10 (night) — the cold reviewer reproduces the score exactly, and finds the package would have been sent wrong
*[Date corrected: this entry and the charter amendments it accompanied were first dated 2026-08-11, taken from the
dispatch's own header rather than from the clock. `date -u` reads 2026-08-10. Caught by the Pass-1 agent, which
recorded the machine clock rather than silently reconciling it to the paperwork — the same discipline the lab's own
clock-audit rule asks for.]*

- **A11 COLD REPRODUCTION: PASSED, bit-for-bit** (636c0b91), by an agent that read ONLY the submission package and what
  the package points at — it did NOT open the status file, the rank-probability record, the campaign files, or any
  Ladder V rung, and its frame is stated on its face. Overall re-scored on the benchmark's own unmodified scorer:
  **0.056647191704213645, identical to the last bit**; 8/8 hashes match; all four published entrants re-score to their
  leaderboard values; the RANS-identity floor reproduces; **three duct CSVs re-derived at exactly zero deviation** from
  the frozen fields, two more at the CSVs' own write precision. Evaluation-point ordering — the silent-killer failure
  mode — is clean at max|diff| = 0. The untrained claim verified in code, and test-blindness verified by the ABSENCE of
  any truth file in the three test-duct run dirs though the benchmark ships one for each.
- **AND THE PACKAGE WOULD HAVE BEEN SENT WRONG. Three BLOCKING defects:** the cover material is **two rounds stale** —
  its email quotes 0.0654, names the round-3 directory and gives round-4 per-case values; **the description document
  the package requires DOES NOT EXIST**, only a spec for it (the same defect class the package itself closed for the
  CSVs, one level up, uncaught); and the package never says where the benchmark or scorer is or how to install it —
  the cold agent found them by filesystem search. Every provenance pointer dangles on receipt and the reference URL is
  still a placeholder. **This is precisely what a cold pass is for, and it is why the gate exists.**
- **CHIEF RULING REVERSED — P(rank 1) is no longer internal-only.** I ruled that figure internal by its own gate. The
  cold agent computed **0.674 from public data in about a minute**, independently of ours, and its judgement is
  correct: *the withholding buys nothing and costs credibility.* A number an outsider can trivially reproduce is not
  protected by being withheld; it only looks concealed. The figure travels with the entry, with its interval and its
  not-decided pairs.
- **The disclosure gap is the most serious of the three weakest points:** the round-5 route was chosen while the
  per-case test scores were known, and the disclosure list discloses only the round-2 leakage. The lab's own rule
  freeze concedes the point in its own words and then closes every remaining degree of freedom — but **that honest
  sentence lives in a file that does not travel with the submission.** It must.
- Also named: §4.7's asymmetry argument was never extended to the three QCR rows; and five of eight predictions are
  not the lab's model, with the trained model on the hump measurably WORSE than doing nothing (+0.00014, refused for
  the entry, correctly).
- **Strongest verified asset, and it does not depend on our score at all:** on exactly the two cases the train-only
  gate DECLINED, the supplied baseline beats all four published entries (0.046108 vs 0.0569; 0.071863 vs 0.0760).
  That is a finding about the benchmark itself.

### 2026-08-10 (night) — Pass 2: the entry's substance survived every attack, its paperwork did not

- **LADDER V IS NOT GREEN, AND THE GATE HOLDS.** Pass 2 (92562841): V7 PASS (three defects, not the two we knew),
  V6 **PASS on the rule / FAIL on currency**, V8 **FAIL — 8 failing claims**, V9 FAIL then fixed, V10 FAIL then
  **PARTIALLY** fixed. No rule violation was found anywhere, and the QCR path is the cleanest thing in the entry —
  **no truth file exists in any of the three test-duct run directories while both validation arms have them**, an
  asymmetry that is the positive control proving the finding is a measurement rather than a blind spot.
- **The worst claim failure would have been fatal to send:** the cover email announces **0.0654** over an attachment
  scoring **0.056647**. A prior section had instructed the update; nobody executed it. The most serious was the
  disclosure gap — the round-5 route was chosen while per-case test scores were known, our own rule freeze concedes
  it in our own words, and that sentence lived in a file that does not travel. **Now written into the description at
  full strength, mitigations placed AFTER the admission rather than doing its work.**
- **Four external surfaces, including a hero KPI tile, claimed best-on-board 4 of 8 without mentioning that two of
  the four are the organisers' own baseline file** — our own audit's "highest-priority disclosure", absent from every
  one of them. Fixed, generator re-verified key by key.
- **Three findings that were nobody's rung and would not have surfaced without an adversarial pass:** a tracked,
  SHIPPING `dist/` archive carrying round-3/4 numbers with **zero caveats**, which no cross-surface list has ever
  included; a live self-audit guard **pinned to round 3 and therefore failing the wall for being correct**; and
  `closure.html` still shipping a prior-art sentence struck on 2026-08-05 that credited two papers with a mechanism
  they never reported — **to a readership including two of the benchmark's own authors**. The report had it right;
  the public page did not.
- The sweep-count check is **retired**: it read 16 at the start of the sweep and 17 before it finished, because a
  sibling pass filed its report mid-sweep. Replaced by three invariants — a count that changes while you count it is
  not an invariant, which is L-53's concurrency problem in a different costume.
- Left for Katie and nothing invented: author names, the reference URL, and two outstanding items — all marked as
  hand-offs rather than filled in. **Nothing was sent. The scoring ledger is unchanged at 6.**

### 2026-08-10 (night) — two monitor rules cannot fire on any production run, and the false sentence is built from true ones

- **D1, CHIEF-VERIFIED PERSONALLY: S6 (residual stall) and S8 (Courant excursion) CANNOT FIRE ON ANY PRODUCTION RUN.**
  The production class constructs its monitor passing only `novel` and an event callback, and **has no parameter by
  which either gate could ever be supplied**; both rules return early when unset. Three construction sites exist
  repo-wide — one production (ungated), one offline replay, one test file. I checked this myself rather than accept
  it from the audit, and it holds. **`MONITOR_STANDARD.md`'s claim that "the whole of both approved monitor proposals
  is in force" is FALSE for every production path** — the geometry studies, the Ahmed act, the NASA hump act, the UQ
  studies.
- **Where it hid is the lesson (L-55):** the standard's PER-RULE status lines are scrupulously honest — each says the
  rule fires *"when constructed with residual_target"* / *"with courant_limit"*. Every one of those sentences is
  true. The SUMMARY sentence is false and is built from nothing but true ones. **A summary drops conditionals because
  that is what summaries do, and the honest clause upstream makes the summary feel audited.**
- **D2, the same shape twice more:** S9's monitor entry point is called only by tests — it is live on a separate
  ledger path and covers **no** production run. And two records describe a five-day threshold defect affecting
  *"every caller that took the monitor default"* — **every caller was the test suite.** The recorded defect had empty
  production blast radius and nobody had asked who the callers were.
- **D3–D5, three more reopened**: the motorBike knowledge-base benchmark describes a mesh **the lab's own skewness
  gate now rejects** (8.94 against a hard 4.0), reopening four conclusions across three documents; *"every OpenFOAM
  log prints the FPE banner"* is false for the DAFoam family (5 of 149 logs lack it) and the rule's warrant is
  additionally sourced to that retired mesh — though the rule itself is correct and unaffected, which is the honest
  direction of the error; and one cited source location is literally `NotImplemented` dead code.
- **The audit's own discipline is why I trust its nulls**: two positive controls FAILED and were disclosed (one
  because `timeout` cannot invoke a shell builtin); a 66 GB unscoped sweep timed out and was **discarded as VOID
  rather than reported as absence**; and a near-miss false FOUND-DEAD was caught because the live path used a
  different symbol. Its counts are labelled a **LOWER BOUND** — 8 rows classified against ~200 triaged candidates,
  chosen for reachability rather than sampled. Read as *"these five are dead"*, never *"only these five are dead."*
- Two escalations named for a further pass, neither log-verified: **three standing verdicts resting on one untested
  relaxation switch**, and an observability finding that may be the largest of all — a print-interval setting gates
  whether clip events are recorded at all, with **689 clip events where the archive recorded 3**, which would make
  every archived clip rate in the lab a floor.

### 2026-08-10 (night, reopened again) — a standard claimed coverage nothing supplied, out of nothing but true sentences

- **S6 AND S8 CANNOT FIRE ON ANY PRODUCTION RUN**, and could not on the day `MONITOR_STANDARD.md` said "the whole of
  both approved monitor proposals is in force". Both need a gate; `HeadEngineer.__init__` takes
  `case_name, out_root, *, novel, on_event` — **no parameter exists by which either could be supplied**. Unreachable on
  the geometry studies, the Ahmed act, the NASA hump act and the UQ studies. S9's `check_wall_time` has no caller but
  tests. Standard corrected FIRST, before any code: false sentence retained with its correction beside it, honest
  coverage table added. MONITOR_STANDARD v1.5.
- **WHERE IT HID IS THE TRANSFERABLE PART.** Every per-rule Status line in that standard is scrupulously honest — they
  say a rule fires *"when constructed with residual_target"*. **The summary sentence is false and is built from nothing
  but true ones**, because a summary drops the conditionals and the honest clause upstream makes it feel audited. The
  practice: when a capability is claimed in force, find its production CALL SITE — not the definition, not the test.
- **THE WIRING IS REFUSED BY ITS OWN EVIDENCE, and the evidence had to be read one level down.** Section 3.1 requires a
  replay before adoption. The S6 replay reports 37 fires over 46 logs — 80%, above the two-thirds that got S7 withdrawn
  — but **all 46 recovered targets are the same value, `p: 1e-15`**, a run-to-the-cap sentinel from one case family
  that no solve reaches. The 80% is one family judged against an unreachable number, not a fire rate. **S6 has never
  been replayed on a representative corpus**, and the artifact that appears to discharge the requirement does not.
  Recorded as a gap with a price (~1 pass each, 0 core-min), never as a limit.
- **BLAST RADIUS CORRECTED IN TWO RECORDS**: the five-day threshold defect said "every caller that took the monitor
  default" was exposed. **Every caller was the test suite.** The code defect was real; the exposure was not. A record
  that overstates its blast radius spends the same credibility as one that understates it — and this family has now
  corrected one of each in a single day.

### 2026-08-10 (night) — the standard is corrected, and the wiring is refused by the evidence that was supposed to justify it

- **STANDARD CORRECTED FIRST, no code touched** (07472cf2, MONITOR_STANDARD v1.5, 0 core-min). The false sentence is
  **retained with its correction beside it** so the correction has something to point at, and the standard now carries
  an honest coverage table: S6/S8 unreachable on every production path, S9 live on the ledger through one symbol and
  unreachable through the other. The supervisor verified D1 and D2 with its own hands before amending anything.
- **THE WIRING IS REFUSED, AND BY ITS OWN EVIDENCE.** The supervisor intended to wire the gates. Adoption requires a
  replay with a stated fire count — so it went to read the existing S6 replay, and **the artifact that appears to
  discharge that requirement does not.** It reports 37 fires over 46 gated logs, 80%, above the two-thirds that got
  a sibling rule WITHDRAWN. One level down: **all 46 recovered targets are the same value, a run-to-the-cap sentinel
  from a single case family that no solve ever reaches.** The 80% is one family judged against an unreachable
  number. **S6 has never been replayed on a representative corpus.** In the supervisor's words: *the figure that
  looked like a reason to wire it was simultaneously a reason not to, and neither reading was sound — which is why I
  read past it.*
- Recorded as **a gap with a price, never as a limit**: S6 needs a replay with real per-case targets, S8 a Courant
  replay over the 21 transient logs, S9 its orphaned entry point routed or deleted — each ~1 pass at 0 core-min.
- **The design ruling that comes with it, and it generalises:** when these are wired, **the gate must come from the
  case's own dictionaries** — the residual controls in `fvSolution`, the Courant limit in `controlDict` — **not from
  a constructor argument.** A constructor argument reproduces exactly this defect one layer up: whoever forgets it
  gets silence. Same derive-from-what-configures-the-run discipline as every other fix today.
- **Blast radius corrected in both records: "every caller" was the test suite.** The five-day threshold defect was
  real and its fix was right, but **no production run was ever judged on the unapproved default** — the ledger path
  read the governed constant correctly throughout. The supervisor's own observation is the one to keep: *this family
  has now corrected an understated blast radius (the seven born-broken meshes) and an overstated one (this) in a
  single day — and a record that overstates spends the same credibility as one that understates.*
- **U3 names a third state:** S9 is wired, correct, and **has never once been exercised** — 0 of 208,193 ledger rows
  carry its field because the rule landed after the ledger's last row, though in memory it would flag 30 historical
  rows. Reachable, unreachable, and *wired-but-never-fired* are three different facts and the next coverage table
  needs the third column.

### 2026-08-10 (night) — section C: a fresh clone skips the safety gate, and six adopted rules rest on 28% of the corpus

- **THE HEADLINE: C5 AND C2 WERE THE SAME DEFECT.** `launch_solve.sh` gates its preflight on `[ -x "$PF" ]` while
  `case_preflight.sh` was tracked non-executable. **On a fresh clone the test is false, the gate is SKIPPED, and the
  launcher launches anyway** — with no line saying the case was never checked. Our own doctrine promises this is one
  of four things "the caller cannot forget"; on a clone the harness forgot too. **Demonstrated, not argued**, with an
  always-failing preflight: at 755 it REFUSES, at 664 — what a clean checkout writes — it LAUNCHES. This box masked
  it entirely, because only the commit travels. Fixed.
- **THE HUMP IS CLEAN — the target Katie named explicitly.** 13 lever/conclusion pairs, 9 verified, **zero
  found-dead**, over a frame defined by what a DAFoam adjoint always prints (651 logs) rather than by what an auditor
  thought to spell. The transonic option IS echoed in all seven hump logs, at a value meaning *off* on a solver where
  it does nothing — **latent, not dead**, no conclusion leans on it, and **the deadness claim is DECLINED** because
  the source is not on this host. Recorded as *"not found in the files searched, which were…"*. One hump-adjoint
  attempt was also found outside every prior audit's frame.
- **The six dead levers are in the MONITORING STANDARDS, not the physics** — and the live one is **D4**: *"every
  OpenFOAM log prints a trapping banner"* is false (5 of 149 lack it), and it **still stands verbatim** in the
  standard's newest version, because tonight's correction touched the other two findings and not this one.
- **C2: 100 instruments audited; 67 never ask "did it run?"** Nine have a third state; **20 are false-positive
  channels and 12 of those have a named archived conclusion running through them.** The worst is not a parser: the
  monitor-replay tool globs `*.log` while OpenFOAM's convention is `log.<app>`, so **the corpus behind SIX ADOPTED
  RULES is 449 files against the 1,618 that exist.** And the omitted quarter **refutes a published line** — the
  standard says no case outside one family reaches a declared target; **53 cases across 10 families** were sitting in
  files the glob could not match. This compounds tonight's other replay finding: the corpus was not merely
  unrepresentative, it was 28% of itself.
- ~~**ROOT CAUSE FOUND** for the auto-stop that has powered the box off mid-campaign (Katie's complaint, three
  times):~~ **DOWNGRADED 2026-08-11 from "root cause" to "candidate mechanism, causal link unevidenced."**
  `is_idle.sh` **concludes IDLE from an absence** — its work list omits `checkMesh` (182 logs), `potentialFoam` (49),
  `setFields` and `sample`. A busy box running any of those reads as idle. **That code defect is real and current,
  verified line by line by an independent pass.** The power-offs are independently attested — Katie saw them three
  times. **What is missing is the link between the two:** an audit looking for it found **no wiring from this script
  to anything that halts the machine**, and the record cited for the cost states only the script's purpose and
  status. **The resolution: the power-off is `/usr/local/bin/auto-stop.sh`, a root cron job outside the repo**
  (`logger "auto-stop: idle ${idle}min, shutting down"; sudo shutdown -h now`), while `sdk/scripts/is_idle.sh` is a
  **diagnostic that prints BUSY or IDLE and halts nothing.** The audit found no wiring **because it was looking at
  the wrong script.** Both carry the same defect class — idle concluded from a `pgrep` absence — and they are
  different objects. **And the fix is still NOT a longer list** — a list is the same defect with more entries
  (L-49). Escalated to the chief and now to Katie, since powering the box off is her cost control.
- C5's real number: the dispatch's "29" was a subtree count. **Repo-wide there are 238 shebang-bearing tracked files
  and 3 with an exec bit.** Routed by owner, not mass-changed. The check itself nearly shipped the defect it hunts —
  its first draft read the INDEX and went green on a mode that was staged and never committed; that near-miss is now
  its own regression test. Suite 1,284 passed / 0 failed.
- **Priced and not spent, routed to the chief:** the relaxation-invariance check costs one extra solve per arm, and
  **three standing verdicts rest on that one untested switch.**

### 2026-08-10 (night) — the memory architecture lands, and it corrects the brief that commissioned it

- **TWO FALSE PREMISES IN THE CHIEF'S OWN DISPATCH, found and reported rather than written around** (56a6a828).
  (1) I quoted *"chat is not the record"* as an agent's words; **that string appears in zero files** — I invented a
  quotation and attributed it. (2) I wrote that *"two transcripts became unreachable"*; the agent checked and reports
  transcripts survive. **The precise version, which is mine to state:** I observed a resume FAILURE — an agent could
  not be resumed and reported no transcript found — and I generalised that to the file being lost, which is a
  different claim I never checked. The real loss it identified is a dead scratchpad taking two arms' logs
  unreconstructibly. (3) "Nine days" is **7 d 15 h**, and is wrong in four files including my own.
- **A living document may not carry a fixed header date.** Two status files are marked do-not-start-here:
  `CAMPAIGN_STATUS.md` is a frozen 2026-07-28 snapshot **still being written to**, in which `B52`, `W1`–`W3`,
  `LADDER_V`, `MODEL_FORM`, `DMR`, `F5c` and `certificate` all occur **zero times** — every campaign since 08-01 is
  invisible in the most inviting file in the directory.
- **The cold-start reading order is ordered by COST OF NOT KNOWING**, which is why a commit procedure precedes the
  science: the escalation charter's §3 still prescribes the practice §9.6a measured as insufficient after four
  collisions, and **no version was bumped, so nothing signals it.**
- **13 duplicates found, 7 already drifted, none edited.** The fleet-death count appears in six places with **five
  different values** (the right answer is eight). The nine-day figure is wrong in all four copies. The B-52 audit's
  own table still displays a retracted count against its recount — the satellite was corrected and the record was
  not. A section was added listing five near-collisions that are **NOT** defects, so the next sweep does not unify
  two populations into one wrong number.
- **The staleness detector's finding is the sharpest part: convention is already at 97% compliance — the gap is
  DETECTION, not convention.** And the obvious two-timestamp detector **fails against the actual incident**, because
  the record was **born stale, not aged into it** — the refuting commit predates the review it contradicts. The
  proposal therefore ships two instruments and makes re-finding that one known instance its first pass-or-fail gate.
- The agent **made the error it was documenting, twice**, and corrected both in place: a version number read from a
  regex that matched another document's citation of a version. Its own words — *that is L-43 with my own instrument
  as the specimen.*
- **My date error propagated into filenames.** Twelve tracked files carry `2026-08-11`, three of them in the
  **filename**, where a date is a sort key — because I took the date from a dispatch header rather than the clock and
  then specified those names. The files are not renamed (five committed reports reference them); **the correction is
  recorded here and on the ladder's face: everything named `2026-08-11` was created on 2026-08-10.**

### 2026-08-10 (night) — V14 finds the shipping archive carries the struck sentence, and the surface our own grep cannot see

- **THE RUNG JUSTIFIED ITSELF ON ITS FIRST RUN** (d358fd96). Mechanical discovery over 48,654 files / 15 GB, six
  frames each with its own positive control, reduced from **227 claim-carrying lines to 11 stale surfaces**.
- **Rank 1: the TRACKED, SHIPPING archive** carries a round-4 score as "entry of record" in its hero, a round-3 KPI,
  a stale scoring-call count — **and lines 254–256 carry the struck prior-art sentence VERBATIM**, crediting two
  groups with a mechanism they never reported, to a readership including two of the benchmark's own authors.
- **Rank 2 is the finding no list could ever have produced:** an untracked, **gitignored** `dist/` directory with
  identical defects — *"the surface this lab's grep wrapper structurally cannot see."* A hand-maintained sweep cannot
  contain what the tooling is configured to hide.
- **Rank 3 is KATIE'S OWN SCRIPT.** `LAPTOP_SHOOT.md`'s spoken 60-second track says the round-4 number **"is our
  entry of record"** and carries the withdrawn best-on-board phrasing. Public-facing by design. **Hers to correct;
  surfaced, not edited.**
- **The structural insight that makes the fix cheap:** ranks 1, 2 and 5 are **built artifacts whose sources are
  already correct** — the bundle script copies pages that are all current, so **a plain rebuild fixes them with no
  hand-editing.** Same failure mode as the self-audit guard pinned to round 3: **a derived surface outliving its
  source.** That guard is re-confirmed fixed.
- **The STALE/HISTORICAL judgement held**, which is the rung's real difficulty: the frozen pre-registrations, the
  round-2/3/4 artifacts, and five status sections are **HISTORICAL and must not be touched**, and one apparent hit
  is a different physical quantity entirely.
- **The largest hole, named by the rung itself: a stale claim carrying NO NUMBER at all** — *"we lead the board"* —
  catchable only where it happened to sit beside a literal. A number-search cannot find a claim without a number,
  and that is the natural brief for a follow-on rung.

### 2026-08-10 (night) — V15 FAILS: the claims-table pass produced text that fails the claims table

- **THE LADDER CANNOT GO GREEN** (6afe15e3). Katie's A15 was right and its first run proved it: **the pass that
  audits claims wrote 442 lines of outward text, and that text does not pass the audit.** L-53 one level up.
- **BLOCKING F1 — the outward disclosure quotes a case that is not in the submission.** The description document
  offers **5.8×10⁻⁴** in bold as "the measured number" for the submitted duct fields. That value belongs to the
  **VALIDATION** duct; the three submitted ducts are 8.5 / 5.3 / 5.4 ×10⁻⁴. **It understates the worst submitted case
  by 32%, in the direction that flatters, four lines below the table that gives the correct range** — and the
  adversarial pass carried the same number into its own claims table.
- **BLOCKING F2 — and it is MY defect, not the ladder's.** Both new package files are dated a day into the future.
  I caught that class at `e59ae644`, corrected `PRODUCT_LIST` **alone**, and the package shipped with it: nine
  closure surfaces assert tomorrow's date, **including the two files that actually travel**. A peer independently
  scoped the class and its twelve files do not include the outward two. **The fix for a class is where that class
  reappears — I fixed my own copy and not the class.**
- Four more, each in the flattering direction: a proof-by-chronology says "three days before" where the measured gap
  is **1 d 22 h** (55% overstated); the rank probability and the margin are computed from **two different values of
  the competitor's score** without saying so; the seed sensitivity that moves P(rank 1) from 52% to 81% **does not
  travel**, though the reversal's own logic says it must; and one section's **only uncited sentence is its defence**.
- **The ladder graded surfaces against a rule it withdrew two rows later** — 16 surfaces marked PASS immediately
  before the rule they were graded against was superseded — and **two sweep claims are false where a positive control
  would have shown it**, including a **bare 68% with no interval** sitting live in a campaign file: the exact
  prohibition the ladder adopted, violated while the sweep reported the invariant holding.
- **My commit set was short by five**, most importantly **the Pass-4 dispatch itself** — *"the rung that says 'any
  text written during the ladder' omitted the commit that created the rung."* Nothing I named was misattributed.
- **My citation fix was verified against the code rather than accepted**, as instructed: the anchors are correct and
  the rung did re-verify twice. **But the date in my note was wrong** — the shift was 2026-07-31, not 07-30. A wrong
  date inside a note about stale references. Corrected at `a454c6bb`.
- **The disclosure PASSES on the hard criterion**, and this matters: it admits before it mitigates, quotes the frozen
  rule freeze verified with `git show` rather than the working copy, and states in terms that no mitigation cancels
  the concession. Two reservations recorded — the last word goes to a rules argument, and it is ranked below the
  best-on-board count, *"which is not the judgement its own prose makes."*

### 2026-08-10 (night) — the bundle shipped a recording of the run Katie's own script warns against

- **ALL FOUR STALE DEFECTS ARE GONE FROM THE SHIPPING ARTIFACT**, verified by extracting the committed zip and
  grepping the extraction rather than the sources (892f11f7 / dc5b12bd): hero 0.0654 → **0.0566**, KPI 0.0676 →
  **0.0566**, the stats file corrected to round 5 with the right scoring-call count, and **the struck prior-art
  sentence returns ZERO hits anywhere in the bundle.** Historical values correctly survive — the per-round table and
  the *"was 0.0654 until round 5"* supersession note are not stale claims.
- **THE FINDING THAT OUTRANKS THE REBUILD, and it is shoot-critical.** The rebuild replaced all four mission
  recordings, and one swap is a **correction rather than a side effect**: the bundle that has been shipping carried
  an aircraft recording **with no wing-geometry upload**, exploring the wrong span ladder at the wrong areas.
  `LAPTOP_SHOOT.md:177` — **Katie's own script** — names this exact failure: *"a run without it searches a different
  span ladder and lands on a different wing."* **The shipping bundle contained a recording of the run the script
  warns against.** The rebuild replaces it with the correct act; all four acts are complete in both, nothing
  truncated. Verified read-only that the swap moves the bundle TOWARD what the script describes.
- **A DISTINCT FAILURE MODE, deliberately not filed under today's other one.** `check_bundle_drift()` **explicitly
  covers all three site pages** and, run against the committed bundle, returned **FAIL with 18 items naming the two
  stale pages**. This is NOT a check that structurally could not see its target — the check worked, and **its output
  did not reach a rebuild for ten days.** A check that fails loudly into a void is a different disease from one that
  fails silently, and conflating them would send the wrong fix. After the rebuild it returns **PASS, zero items** —
  end-to-end verification, stronger than four greps coming back clean.
- **RULING ON THE GITIGNORED DIRECTORY: IT STAYS**, on the agent's reasoning, which reverses the obvious call.
  It is a build output and nothing deploys from it — but **the drift check compares against it**, so deleting the
  stale copy would remove the one thing correctly reporting the staleness. *"The directory is the check's eyes; the
  ignore entry is the blindfold on everything else."* What let it drift invisibly was never its existence but its
  **gitignoring**, since the lab's grep wrapper honours ignore files. Regenerated in place; tree and shipped artifact
  now match byte-for-byte.

### 2026-08-10 (night) — the corpus was an instrument nobody had examined, and correcting it reversed a refusal

- **D4 CORRECTED, and the measurement is five times worse than the audit found**: **39 of 149 logs carry no trapping
  banner**, not 5, and across every prefix rather than one family — because the banner only appears when an
  environment variable is set, making it **a fact about how a run was LAUNCHED, not a property of OpenFOAM**
  (07472cf2). The amendment says which of the two moved: **the warrant, not the rule**. And the measurement
  *flatters* the rule's design — a banner-keyed detector would have been blind on those 39 logs **and** would have
  read the other 110 healthy runs as fatal. The original reasoning reached the right rule through a claim that was
  not true.
- **THE REPLAY CORPUS: 449 → 1,375** (b69cd45e), derived rather than widened — it keys on what an application run
  actually prints, with binaries excluded by content rather than extension, **so no naming rule participates at any
  point.** The proof that this mattered: **`*.log` plus `log.*` together still miss 96 real run logs.** A list of two
  patterns is the same defect with more entries.
- **AND IT OVERTURNED THE SAME AGENT'S REFUSAL FROM THE PREVIOUS PASS.** On the corrected corpus the gated set goes
  46 → **222**, one family → three, one target value → eight. Separating the unreachable sentinel gives the number
  the adoption rule actually asks for: **41 fires over 87 logs with genuinely declared targets — 47%, well under the
  two-thirds that withdrew a sibling rule** — and it is **not uniform** (94% / 51% / 20% by family), a spread a
  single global rate hides in both directions. *"My refusal was right on the evidence then available and is no
  longer supported."* What still blocks wiring is now narrow and stated: target recovery must read each case's OWN
  residual controls, and the sentinel class must be excluded or the gate fires on 99% of that family.
- A published line in the standard is refuted by the same correction: **70 logs outside the named family carry real
  declared targets**, sitting in files the glob could not match.
- **Recorded as L-43's third corollary — the CORPUS is an instrument too.** Six rules were adopted against a corpus
  nobody had asked *what does this select, and what does it silently drop?* **Ninth instance this campaign of the
  instrument, rather than the reasoning, being the defect.**

### 2026-08-10 (night) — the gate ships, verified through served HTML, and a test that could have blamed a colleague

- **WARN → FAIL ON ABSENCE SHIPPED** (`54cf11bb`, alone and revertable in one move; rebuild separate at `a1545dbd`).
  All four conditions met. The message now says what absence MEANS: *"the drift detector for the shipped artifact is
  OFF, not merely uninformative"*, with the detail that a stale zip beside it would report clean.
- **Verified END-TO-END through served HTML, not by unit test**: build → drift check (PASS, 56/56 byte-for-byte) →
  extract as the instructions say → run the console → fetch the pages. All four pages 200; **the served hero reads
  0.0566, the served KPI reads 0.0566, and the struck prior-art sentence returns zero hits over HTTP.** That is the
  artifact as a viewer receives it, which is the only frame that matters for a shipped bundle.
- **A TEST DESIGN FINDING WORTH MORE THAN THE GATE.** The first control arm was written against the live repo bundle
  and failed — because another family committed a file in the nine minutes between the rebuild and the test run.
  **"A test whose control arm depends on no other agent committing reports other people's work as its own
  failure."** Rewritten hermetic against a synthetic tree, with both control arms kept so the fix cannot degrade
  into fail-always. In a fleet where six agents commit concurrently, a test with an ambient dependency is a
  false-accusation channel.
- **The one genuine surprise was the detector working.** The drift check went FAIL again minutes after passing —
  another family's commit — and was rebuilt to absorb it. **A one-file gap caught within nine minutes** is the best
  available evidence that the check is worth keeping armed, and it arrived by accident during the pass arguing for
  arming it.
- Two mid-run anomalies were diagnosed rather than worked around, and **both were the agent's own** — a console that
  auto-increments its port and reports the port it chose (queried at the old one), and a process-kill pattern
  matching its own command line. Neither was a defect in the artifact or the change.
- **The agent's timing judgement, requested and given:** ship it. *"The risk of leaving it is a silent detector
  through a shoot; the risk of taking it is a FAIL that correctly tells you to run one command."*

### 2026-08-10 (night) — both blocking items closed, and the corrections found more than the audit that ordered them

- **F1 CLOSED and the figure was in THREE ladder documents, not the two V15 found** (7de8733c). All four duct values
  re-derived from the JSON, and **the submission side proved two independent ways** — the forward record's own
  changed-list (`closure_challenge_round5_qcr_forward.json` `/what_ships`, where `AR_7_Ret_180` appears in neither
  `changed` nor `unchanged`) and the absence of a validation-duct CSV in the shipped directory — rather than taken
  from the brief. *(Citation corrected 2026-08-11 per V15 round 2 finding N4: this read "the manifest's own
  changed-list". `closure_challenge_submission_round5/MANIFEST.json` has no changed-list — its `files` key names all
  eight cases undifferentiated and the string `AR_7` does not occur in it at all. **The claim is true and both proofs
  stand**; only the artifact named for the first one was wrong, in a sentence whose whole point was that it was
  verified against the primary artifact rather than taken from the brief.)* The
  replacement names its cases instead of giving a bare range: *"the three submitted ducts measure 8.5, 5.3 and
  5.4 ×10⁻⁴"*, **so the number can never again be read as belonging to a case the reader will not receive.**
- **F2 CLOSED, and the date list was longer than every prior count** (9477a2ed): **19 tracked files**, against a
  peer's twelve and V15's seventeen — two landed after both measurements. Of 73 occurrences, **29 were assertions and
  all are corrected** (including both outward files the peer's list omitted); **44 were references and were correctly
  left alone**, and **zero** were genuine future dates. *(Counts corrected 2026-08-11 per V15 round 2 finding N3: this
  entry and `9477a2ed`'s body both said 74 and 45. Re-measured over `git ls-files` at the fix's own parent `8cc6bf70`,
  `git grep -oI "2026-08-11"` returns **73 in 19 files**; 73 − 29 = 44. The commit body cannot be edited, so the
  correction lives here. The 29, the 19 and the corrective work itself are exact and unchanged.)* No filename renamed; the three carrying the wrong date in
  their name got in-file notes. The one pass that recorded the discrepancy against the clock rather than inheriting
  it already had its note.
- F3–F7 closed: a chronology corrected from "three days" to **1 d 22 h 37 m** at four sites; the seed sensitivity now
  travels as a fourth row of the outward interval table, per the reversal's own logic; two citations verified at the
  frozen benchmark commit and cited inline; and the single bare 68% fixed — **the only one in that sweep's actual
  frame**, five sibling surfaces already compliant. *(Exhaustiveness claim corrected 2026-08-11 per V15 round 2
  finding N6. The sweep was announced as covering tracked `.md`/`.html`/`.tex`/`.py`, and its result did not: its true
  frame is **per-SURFACE, over tracked `.md`/`.html`/`.py`**. `latex/closure_challenge_report.tex` — row 16 of the
  16 claim-bearing surfaces, and NOT this lab's file to edit — carries the figure at **12 sites** and an interval at
  exactly one (lines 259–260), so it passes per-surface and fails per-claim, and **per-claim is the reading this
  ladder recorded** at `LADDER_V_PASS2_2026-08-11.md:338` (*"its owner should confirm every one of the twelve now
  carries the interval, which is the new requirement"*). Nine `.tex` sites carry the figure with no interval in
  local context — lines **61, 78, 203, 237, 287, 699, 717, 768, 786** — and two more state the WITHDRAWN
  internal-only rule (**243**, **287**). Re-swept independently over all tracked files at 2026-08-11: outside ladder
  reports quoting the rule and dated changelog entries, the `.tex` is the only surface with bare figure sites, and
  the outward `DESCRIPTION_DOCUMENT.md` is compliant at all six of its sites. **Routed to the `.tex`'s owner; not
  edited here.**)*
- **Two items it STOPPED on rather than fixed, and the stop rule was right both times.** (1) **A third value of the
  competitor's score** — one document's stated figure, the margin it derives, and its own table imply three different
  numbers; reconciling needs the scorer re-run, which is a computation rather than a text fix. (2) The statement
  *"INTERNAL ONLY; the 68% figure never appears in an external claim"* **is now false on four surfaces because of my
  own reversal** — and rewriting a rule statement is a decision, not an accuracy fix.
- **I have corrected the three records I own** — they now read that the restriction was withdrawn by chief ruling and
  that the figure travels, never without its interval and the not-decided pairs. **The report's copy is routed to its
  owner.** My reversal changed what is true and I did not sweep the statements describing the old rule; that is the
  same fix-the-copy-not-the-class defect I committed with the dates, twice in one night.

### 2026-08-10 (night) — S6 fires for the first time ~~on production~~, and ~~every prediction hit exactly~~
*(**CORRECTED 2026-08-11 — see that date's entry. The PRIMARY prediction was never scored and no document said so.**
It was a post-wiring fire rate on `HeadEngineer` runs; that run cost **zero core-minutes**, so no such run existed.
An **analogue family** was scored in its place, and this heading then hardened the analogue into "production".
The primary prediction is **still open**.)*

- **WIRED AND FIRING** (pre-reg `ab0c8d76`, wiring `1471b8f3`, suite 1294, 0 core-min). Both conditions were
  implemented as **mechanisms rather than policies**, which is why they hold.
- **Condition 1:** the gate reads the staged case's OWN `fvSolution`, from the single place every case passes
  through — **not a constructor argument**, because *"a parameter the caller must remember is the exact defect being
  closed, one layer up: whoever forgets it gets silence rather than an error."*
- **Condition 2 is the elegant one — a STRUCTURAL discriminator, not a threshold.** A residual target at or below
  that field's own linear-solver tolerance **cannot be reached**, since the outer residual cannot go below what the
  inner solve resolves. Both numbers come from the same file, so **the exclusion is a relation the case states about
  itself and no magic constant appears anywhere.** It separates the corpus exactly: **135 of 135 sentinels captured,
  zero false in either direction.** The motivating case says it in its own text — a real target commented out and
  replaced with an unreachable one to force a run to its cap — which also forced a comment-stripping parser, since a
  naive one would have read the DEAD value.
- **Condition 3: pre-registered SEPARATELY, before any wiring code existed**, so the ordering is provable rather than
  asserted — then **scored by replaying the SHIPPED helpers**, not the script they were designed with. *"A rule
  validated in one form and shipped in another is the failure this campaign kept meeting."*
- ~~**Every prediction hit exactly:**~~ **THE SECONDARY predictions hit exactly** (the primary was never scored —
  see above). 81 gated logs predicted, 81 measured; 35 fires at 43% predicted, 35 at 43%
  measured; 135 sentinels excluded, 135; the family spread 48% / 92% / 20% predicted and measured. **The spread
  surviving wiring intact is the real check** — a uniform rate would have meant the recovery logic was not seeing
  what the replay saw. Fail-open count stated rather than folded in: 6 logs declaring no tolerance are not gated,
  because reachability cannot be established and so is not asserted.
- **The generalisation is now placed where a rule-AUTHOR meets it, not only an auditor** — immediately before the
  adoption gate: a replay must state how its corpus was selected, **whether that selection is a derivation or a
  list**, what it could not see, and what fraction of the plausible universe it covers. With the cost recorded
  beneath it: six rules adopted against 28% of the evidence, and the number that looked like a fire rate was one
  family measured against a target no solve can reach.

### 2026-08-11 — V15 round 2: NOT at the fixed point, and the trend is right

- **VERDICT: NO. There will be a round 3** (`c1ebfb4f`). Round 1 found ten failures, **round 2 finds six, none
  blocking, and only one touches the outward package.** The fix round's corrective WORK is exact almost everywhere —
  *"it is the arithmetic REPORTING the work that keeps failing."* Three commits correctly stopped rather than fixed;
  two put the fix in the generator rather than the output.
- **My commit list was short by SIX** (round 1 it was short by five), and **the omission includes the termination
  rule's own commit** — I dispatched a rung about "all text written during the ladder" and left out the commit that
  created the rule defining when that auditing stops. **Round 1 caught the identical omission one rung earlier.**
  Recorded as **L-56**: when you write a rule about a class, the act of writing it joins that class. Both instances
  were self-excluding in effect and did no damage; **the recurrence is the finding.**
- **N1 (MAJOR): a FIFTH surface still asserts the withdrawn internal-only rule** — and it is **the JSON the outward
  document cites as its source.** It survived every sweep because the documents write *"the 68% figure"* while the
  JSON writes *"the figure"*: **a grep missing by three characters.** My own record said four surfaces; it was five.
  **CLOSED 2026-08-11 at `d9552d73`**, to the wording already committed at `1db6fc3c`, in this file's ASCII house
  style; `INTERNAL ONLY` now occurs zero times in it and `self_audit.check_closure_entry_of_record` still returns
  PASS. **And it was not five.** Round 3 was told not to fix a phrase-miss by grepping the same phrase again, so the
  surface set was re-derived structurally — *(restriction predicate)* within 400 characters of *(a referent for the
  figure)*, no spelling of the sentence used anywhere in the search, over every tracked text file plus every member
  of `dist/certonomous-demo.zip` opened rather than inferred. **Fourteen surfaces carry a statement of the rule.
  Eight are correctly superseded, struck or quoted** (the chief's three, `PROBABILITY_OF_RANK`, `CHALLENGE_SLATE:37`,
  `LADDER_V_TRIPLE_VERIFICATION:54–56`, the routed report copy, and the JSON now). **Six still assert it in the
  present tense**, all outside this pass's ownership and therefore reported, not rewritten — the same call the chief
  made in this entry, that rewriting a rule statement is a decision:
  **(1)** `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md:108–110`, **the family's rule document** (row 12 of the 16),
  still instructing supervisors that *"the figure is INTERNAL: internal surfaces carry it, public surfaces in
  `dist/` carry the qualitative clause only"*;
  **(2)** `docs/PRODUCT_LIST.md:60–61` — **this file** — *"The number is INTERNAL and never appears in an external
  claim"*, in the live round-5 standing item, twelve hundred lines above the entry that reverses it;
  **(3)** `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1184–1191`, a *"Wording note, deliberate (chief ruling 2026-08-10)"*
  keeping the figure out of the outward draft **because it is internal by its own gate** — while line 575 of the same
  file states the withdrawal correctly, so the draft contradicts itself;
  **(4)** `latex/closure_challenge_report.tex:243` and **:287** (see N6; not this lab's file to edit);
  **(5)** `docs/CAPABILITY_STRATEGY.md:83`, the STRATEGY PROOF CLAUSE itself — *"internal only, but it is the house
  asking the right question"* — **the origin of the gate**, which is why every copy of it reads that way;
  **(6)** `agenda/proposals/probability-of-rank-a-posterior-over-our-score-against-the-board.json`, four fields
  (`objective`, `rationale`, `sequencing`, `gate`) — an **approved, dated** proposal, where a rewrite under an
  unchanged `decided_at` would forge the record, so it needs a supersession note rather than an edit.
  **The finding under the finding:** the count was never going to come out right, because a rule withdrawn at its
  statement was never swept at its *origin*. Five of the six were found by a search that did not know how the
  sentence is spelled.
  *(Provenance, because a claims table run over commits would otherwise mis-attribute this: the N1-derivation and
  N2-verification paragraphs in this entry were written by the round-3 correction pass and were swept into
  `afe1af99` — a concurrent pass's `git commit -a` about an unrelated absence check — before round 3 could commit
  them with a pathspec. The text is byte-unchanged and is round 3's; **`afe1af99`'s body does not describe its own
  diff.** Round 3's own commits are `d9552d73` (N1), `07af6f02` (N3), `8ce7cedd` (N4), `35c59035` (N5),
  `4e719a6b` (N6).)*
- **N2 (MAJOR):** round 1's finding about four non-compliant external surfaces was **renumbered during the fix round
  and reported closed while still open** at HEAD. (Being closed now by the concurrent pass; the auditor reported the
  committed state and said so.) **CLOSED and verified 2026-08-11 by round 3 at `656c09c9`** (committed 00:11:36 UTC,
  four minutes after round 2 froze its frame at `249b611c`). Re-read from `git show HEAD:<path>`, not the working
  tree: `benchmarks.html` (4 figure sites, 2 interval sites, both blocks pair them), `benchmarks.json`,
  `wall/wall.json` and `build_benchmarks.py` each now carry **P(rank 1) = 68%** *and* **2–100% at 95%**, the
  not-decided pairs were already present, and **the figure appears without its interval on none of the four.**
  Round 2's zeros were correct at the revision it pinned; the renumbering that hid the finding is the part worth
  keeping — **a finding renumbered is a finding lost.**
- N3–N6: two counts measure one lower than reported (73/44, not 74/45); a citation to *"the manifest's own
  changed-list"* — **the manifest has no such list**; the new outward seed paragraph credits a bound of 0.002419 when
  the bootstrap loaded **0.0024**, which is the same precision defect it disclosed one paragraph earlier; and the
  bare-figure sweep **calls itself exhaustive while omitting the report**, where the figure appears seven times with
  its interval once.
- **All four of my specific checks came back clean or better:** the three duct values exact and the excluded case
  proved absent two ways; 29 date corrections with **no meaning changed anywhere**; the chronology re-derived
  independently to the minute (1 d 22:37:22, a 54.4% overstatement); and my three rule-statement corrections
  accurate, byte-identical to each other, and adding **new text but not a new claim.**
- The auditor's frame **moved four times while it derived it** and it pinned HEAD with three timestamps in the
  document — the termination rule behaving as designed rather than failing.

### 2026-08-11 — V6 and V14 PASS, V10 fails on one surface, and the pass reported its own new failure first

- **V6 PASS**: all nine compliance findings verdicted against round 5 **inside the audit itself** rather than in a
  satellite, moot findings kept with their reasons, and the untrained-path compliance line added **with a positive
  control** — zero truth files in all three test ducts against three in each validation arm, and the coefficient's
  compiled default overridden nowhere.
- **V14 PASS as a rung**, stale list dispositioned in full. The eight judgements turned on stale-versus-historical
  every time and two produced more than a label: rank 5's number was **hard-coded in a generator**, so the note went
  into the generator and **both outputs were re-derived**, verified by running it into a scratch directory
  before/after/again; and rank 6 turned up **a manifest string the script WRITES at line 412 that the discovery rung
  had not listed** — a generator emitting a stale number into an output it produces.
- **Two stops rather than fixes, both correct.** A gate at `NUMERICS_KNOWLEDGE.md:560` names a PH-only comparison
  while stating an overall bar; both candidate numbers were computed and **neither substituted, because that would
  change which experiment the gate is.** And the round-5 continuity figure was corrected while **explicitly avoiding
  the trap V15 caught in the outward document** — naming the validation duct as validation rather than letting its
  number stand for the submission.
- **V10 FAIL — one surface, and it is the shipped bundle.** The tree is consistent and both closure checks pass, but
  `dist/certonomous-demo.zip` is **two files behind**: one from this pass's own compliance fix, one from a monitor
  commit that landed ten minutes after the last rebuild. The agent **did not rebuild it**, honouring the ring-fence I
  set, and named the remedy and its owner instead.
- **"My round is not a fixed point — it introduced one new failure, stated first not last."** That is the
  termination rule working as intended: a fix round that reports the failure it created, at the top, rather than
  declaring victory and leaving it for the next audit. Round 3's scope now includes it, plus three commits nobody but
  their author has read.
- A concurrent audit rung graded this pass's first six commits while it worked: **every row passed.**

### 2026-08-11 — the three prior zeros were UNSOUND, and the sentence is genuinely absent anyway

- **THE POSITIVE CONTROL IS THE FINDING** (`f2e16a47`, `7cd558b1`). The struck prior-art sentence was planted into a
  scratch copy of the shipped page, wrapped across five lines and split by markup — then both instruments were run
  against a file that **demonstrably contains it**: the **line-bounded grep used in all three prior passes returned
  ZERO**; the normalised search (whitespace collapsed, tags stripped, dashes and accents folded) **found all seven
  fragments.** So the three prior zeros were **unsound, not merely unconfirmed** — a false absence is what that tool
  produces on wrapped text, and absence was the entire claim.
- **The sentence is genuinely absent**, now on evidence that cannot fake a zero: verified three ways — the extracted
  committed archive, the current source, and **the bytes served over HTTP** — all agreeing, across 78 text files,
  with the sweep's own control passing on the planted copy. **V10 stands closed on sound evidence.**
- **And the correction turns out to be better than "removed".** Four author-name fragments ARE present and should be:
  the 2026-08-05 fix was **a two-part split, not a deletion**. As shipped, classifiers that *identify* where a
  baseline is unreliable are credited to the two groups that reported that — with the text saying explicitly that one
  of them **"controls nothing"** — while *using such a classifier to control where a correction applies* is credited
  **separately, and only to the two groups that actually reported it.** The struck version had credited all four with
  the control mechanism "repeatedly." **That is the defect fixed, not merely erased.**
- **A flaw in the checking method, found and recorded by its own author:** four of the seven fragments were author
  names the CORRECTED text legitimately contains, so they read PRESENT and meant nothing. **"A fragment shared by the
  defect and its fix is evidence of neither."** Only the mechanism clause and one phrase discriminate — and those are
  the two that came back absent. Now family practice §9, with the campaign's lineage attached: a launcher keying on a
  command's first token, a parser reporting clean on a crash, a regex spelling one hyphenation, a glob spelling one
  directory prefix — **each read its input correctly and could not see what it was asked about, and this one was
  hiding inside the procedure we had just promoted to the standard.**

### 2026-08-11 — the report carries the interval at every site, and the build proved a judgement rather than arguing it

- **ALL TEN SITES CARRY THE INTERVAL** (`5fa933ee`, 40 pages, 0 errors, zero overfull boxes before and after, the two
  underfull boxes byte-identical in badness). **No site had to drop it** — even the table cell took the full form,
  because the column's widest entry was already wider and abbreviating bought nothing.
- **The judgement call was settled by the build, not by argument.** The disputed site's interval lived a few lines
  below, after a floating table — and **that table moved from page 5 to page 6 between the two builds.** Source
  adjacency is not page adjacency, and a float that migrates once will migrate again on the next edit, so leaving
  the site bare would have made the no-bare-figure rule *contingent on a page-breaking accident*. It got its own.
- **The withdrawn caution was replaced, not deleted.** It now states the figure and its interval, then in italic:
  *"Until 2026-08-10 this item read differently… That restriction was withdrawn, and the reasoning is recorded here
  rather than deleted, because a reader who met the old rule is owed the reason it went."* Then the reason — an
  outsider recomputed 0.674 from the published board and our own per-case scores in about a minute — and the
  replacement rule. **Publishing "rank 1" while withholding how little it survives resampling inverts the lab's own
  standard**, and the document now says so.
- Three artifacts gained provenance rows, one of which closes a **pre-existing** gap: the rank-probability record had
  been cited in a table caption and **never indexed**.
- **AND IT CAUGHT AN ERROR I PROPAGATED INTO ITS OWN BRIEF.** I told it to expect an unchanged float warning at
  37.81813pt. **That warning is not in this document at all** — it belongs to the other report's log. Both the
  baseline and new builds contain zero occurrences. I carried an expectation across two documents without checking
  it, and had the agent trusted me it could have read a genuine absence as a discrepancy, or worse **used
  "unchanged" as a green light for a warning that was never there.** Fourth time tonight I have passed forward
  something I had not verified.
- Two `h` float-placement notices appeared and were **verified rather than assumed**: every table lands adjacent to
  its own prose, none orphaned. Silencing them would have been a larger change than the ruling warranted.

### 2026-08-11 — the report is complete, and a one-word edit was checked against the document's own voice

- **Line 272 taken as approved** (`45b3be0f`): *"The **internal** sentence this supports is"* → *"The **honest**
  sentence this supports is"*. The word was not invented — the writer checked first and found **"The honest ___" is
  already this document's own idiom** (three prior uses in its own sections), so a one-word edit in someone else's
  register lands in a voice the report already speaks.
- **A residue sweep of the whole file followed**, on the principle that *fixing one instance without checking for
  siblings is how the next one survives.* Six occurrences of "internal" remain and **all six are correct**: two mean
  *scored in-house* and are unrelated to the withdrawn gate, one is unrelated in subject, and three sit inside the
  corrected caution's past-tense recital and provenance — **where the word RECORDS the withdrawal rather than
  asserting it.** That distinction is the whole difference between a residue and a history.
- Compile clean at 40 pages, zero errors, the same two underfull boxes at unchanged badness, no new warnings.
- **The sharper half of my brief error, in the writer's own diagnosis:** *"'unchanged' is the one word in a warning
  expectation that cannot be checked against the new build alone, because it makes a claim about a baseline I had
  not built yet."* Which is why it **built the previous version side by side before touching a character** — and
  that is what turned my green light into a locatable discrepancy in a different document's log. Standing practice
  now: any brief saying *expect this unchanged* requires building the baseline first, however routine it looks.
- The report remains **filing-READY, NOT FILED**; nothing sent, filed or uploaded at any point tonight.

### 2026-08-11 — the cold-start test refuses to claim its own pass, and names the night's real danger

- **12 of 12 — and the agent WOULD NOT claim a pass**, because the test's answer key sits in the same document the
  test agent is sent to read: eleven of twelve answers are legible **without opening a single cited file.** *"As
  written, the test cannot fail."* Against primary files only the honest score is **11.5/12**. A test that cannot
  fail measures nothing, and the agent said so instead of banking the result.
- **Time to competence: 3 min 38 s**, 21 tool calls, ~4,600 lines across 17 files, stuck nowhere. The reading order
  is genuinely well built, and ordering it by cost-of-not-knowing — commit rule before science — is vindicated.
- **THE MOST DANGEROUS THING ON THIS BOX, named by an agent that had never seen this campaign: sending the closure
  submission** — irreversible, carries the company name, reserved to Katie in two charters. And it named the
  mechanism exactly: *"an agent optimising for a cross-off completes it"*, because the package sits at filing-READY
  beside an open checklist item literally titled **"Submission send package."** **Closed immediately** (9e6fc374):
  the item is now marked KATIE-ONLY, states that it is not a task on any queue and that crossing it off is not a
  goal, and carries why — including that its headline is not statistically decided.
- **Step 0 — the step the memory document itself calls load-bearing — was teaching a rule the lesson book corrected
  last night.** L-57 (a pathspec commit isolates by file, not by author) had not reached it. Amended. That is the
  same shape as the defect the document already logs: **a reading order that teaches a rule its own lessons have
  superseded.**
- **A defect class the lab had no name for, now L-58: a detector that EXPIRES.** Twelve files were dated a day into
  the future — findable by one cheap check. Three could not be renamed without breaking committed citations, and
  then **midnight passed and the detector lapsed**: a filename asserting today is indistinguishable from one
  asserting the day it was written. A trivial defect with an expiring detector **outranks a serious one you can find
  any time**, and if it cannot be fixed inside the window it is logged as PERMANENT before the window closes.
- 15 further defects opened, and the three worth acting on first are gaps rather than errors: the reading order
  **never reaches Katie's own instructions**, which the document itself ranks *Absolute*; it never reaches **what is
  blocked**; and it has **no step telling a fresh agent who else is live** on a tree with six concurrent writers.
  Also: no single file lists the standing prohibitions — they are scattered across five.

### 2026-08-11 — V8 FAILS on the cover email, which has not been touched since 2026-08-01

- **THE DESCRIPTION DOCUMENT PASSES 30 OF 31 QUANTITATIVE SENTENCES**, each traced to a **primary artifact rather
  than to a sibling surface** — the overall and all eight per-case values, the floor recomputed from its own row, the
  best-on-board count against the per-case rank fields, the duct agreement, the continuity figures, the seed bound,
  every bootstrap interval, the frozen rule-freeze quote verbatim, the chronology, and the scoring-call count. Banned
  list clear throughout; all ten figure sites carry an interval.
- **BUT V8 FAILS, and the failing artifact is the one that actually gets sent.** The cover email is **round-4 and
  untouched since 2026-08-01**: its subject line and body announce **0.0654** for a payload scoring **0.056647**.
  Five of the original eight failures are open verbatim — the score, the wrong directory, an entire claims table of
  round-4 per-case values, a prediction-set count of four against a ledger of six, and a duct figure that is stale
  **against our own interest**. Three of the eight are genuinely closed.
- **A NEW failure inside the travelling document, and it propagates.** The margin (0.0028863) and the competitor's
  re-scored value (0.0595338) are stated in adjacent sentences **and do not subtract** — one is misrounded by
  3×10⁻⁷. Checked both ways. Nothing downstream moves, but it is the same class as the previous round's finding and
  it **originates in one report and propagates into three others.** Reported, not fixed.
- **The auditing agent's own corrections failed the rung, and it caught them itself.** Running the cross-surface
  instrument against text it had just written showed the sweep token **fell across a line break** in both markdown
  fixes — *"invisible to the grep it exists to serve, the exact failure mode this ladder has now recorded three
  times."* Rewrapped, and the fix now states WHY the token must sit unbroken.
- **Fixed-point consequence, stated by the rung itself:** a re-run over previous-round text produced a new failure,
  so **the ladder has not converged and round N+1 exists.**
- Two closures worth noting for their care: the approved proposal took a **new supersession field** only after the
  agent proved no validator would reject it and that the convention already existed in the corpus — with the four
  decided fields asserted **byte-equal before and after, programmatically rather than by eye**. And the
  self-contradicting draft note was corrected by **naming which of its two passages was right and why**, rather than
  quietly aligning them.

### 2026-08-11 — round 4: NO fixed point, and the failures have migrated entirely into the changelog

- **Trend: 10 → 6 → 7. The count stopped falling — and two things fell monotonically anyway: BLOCKING failures
  2 → 0 → 0, and OUTWARD-PACKAGE accuracy defects 3 → 1 → 0.** Round 3 is **the first round to put nothing wrong
  where an outsider would meet it**, to write no bare rank claim, and to build the wrap-proof absence instrument —
  which round 4 then adopted for its own sweeps and used to independently confirm a zero.
- **The class has moved, and the diagnosis is the finding: *every one of the seven is a description of a correction
  that is less exact than the correction.* Three sit in text written for the sole purpose of recording a defect
  accurately** — which is the worst possible place for them. The package is clean where a reader would look; our
  records ABOUT cleaning it are not.
- **MY OWN LESSON CONTAINED A WRONG NUMBER.** L-57 and its provenance commit both said a chief commit swept **59
  lines** of another agent's work. Hunk-by-hunk it is **34** — 59 is the commit's total insertion count, and the
  other 25 were its own on-message section. **Two commits whose sole purpose was to state an unrewritable incident
  correctly overstated it by 74%, one of them a numbered lesson future passes will cite.** Corrected in place; the
  correction is the lesson's own point applied to itself — read the diff, not the summary of it.
- **My commit list was wrong in a NEW direction, and this one ran the flattering way:** six commits I named were
  already audited in round 2, and auditing them again would have **inflated this round's pass count by six commits'
  worth.** Every previous dispatch error made a round look worse; this is the first that would have made one look
  cleaner. Two genuine misses as well, both my own changelog entries — **the third consecutive round I omit that
  exact class**, and the lesson I wrote about self-omission names the rule-creating class and not this one.
- **A derivation this lab has been citing does not reproduce.** Round 3's "14 surfaces, 6 still asserting" comes back
  as 20 at its own stated window and 25 at a wider one — and **at its stated window it misses the surface it ranks
  first.** Its "six still assert" was falsified **2 m 57 s later by my own next commit**, which closed two of them,
  one in the same file as the list. And its claim that five of six were invisible because they avoided the
  documents' words is **false for three** — half that miss was frame narrowness, not spelling, **and the note I
  wrote into the strategy teaches the wrong half.**
- The auditor's frame **moved mid-audit** and it caught this only because a re-read disagreed with a measurement
  taken four minutes earlier; it then re-took every affected measurement against the pinned revision rather than
  patching the difference.

### 2026-08-11 — V10 independently confirmed, and the independent check found what the self-graded one missed

- **THE ABSENCE CLAIM IS NOW PROVEN, not asserted.** The checker reconstructed the struck sentence **from the commit
  before its removal** rather than from anyone's report, then split its needles into three classes — 5 discriminators
  unique to the struck text, 3 shared with the corrected text (used only as reach controls), and 4 unique to the fix
  — because **a fragment shared by defect and fix is evidence of neither.** Calibrated both ways on known-good and
  known-defective files. **Positive control: the sentence was planted in its most evasive available form** — wrapped
  over ten lines, split mid-word by markup, em-dash and accented names entity-escaped. The new instrument found all
  five discriminators; a plain fixed-string search returned **zero files**. The unsound-zero failure mode was
  reproduced deliberately and the method shown immune to it.
- Result: all five discriminators **zero**, all seven shared and fix-only needles **hit in the same file** — proving
  reach into the exact page. Drift derived independently from the build script before seeing the other agent's
  number: **56/56 byte-identical, plus 24/24 and 8/8 against their real source roots, 90 members fully accounted.**
- **AND THE NEW FINDING, which the self-graded closure could not have caught:** `closure.html` makes **three rank-1
  claims** and carries the not-decided pairs but **never states the probability or its interval.** The cause is
  scope, not a rebuild defect: the fix closed "the four external surfaces", and the guard it added **reads only the
  wall's string** — so the most prominent page in the shipping bundle is **unguarded.** By V10's own wording that is
  a live inconsistency, so **V10 does not close yet.** This is precisely what independent verification is for: the
  original check verified what it had been asked about, and the second asked whether the question was complete.
- **V5's two gaps closed, and the generator warning earned its place**: the checker verified that the page is NOT
  generated (its sibling *is*, at a named line — untouched) before hand-editing, so no fix was applied to an output a
  generator would overwrite. Citations written in **each file's own existing style** rather than an imported one, and
  "overridden nowhere" **verified in the source and across every dictionary in the round-5 run tree** rather than
  inherited from the brief.
- Consequence flagged rather than left: the page fix puts the tracked bundle **one file behind**, and the drift gate
  now correctly reports it. The rebuild belongs to the bundle's owner.

### 2026-08-11 — the cover email is round-5, and the margin discrepancy was resolved rather than flagged

- **ALL SIX DEFECTS CLOSED** (`e87650db`). The subject line and body now carry **0.056647** against the 0.1036 floor,
  read from the round-5 record rather than from a sibling document; the directory, the eight CSVs re-counted on disk,
  the entire per-case table rebuilt, the prediction-set count corrected from four to **six**, and the stale duct
  figure replaced with the measured values — **flagged in the text as a disclosure that had overstated our own
  defect, and corrected for that reason rather than because correcting it flattered us.**
- **THE MARGIN DISCREPANCY IS RESOLVED, NOT FLAGGED.** Rather than propagate either number, the writer **re-scored
  the competitor's four published CSV directories through the benchmark's own unmodified scorer** at the frozen
  commits: 0.05953352830400628, giving a margin of **0.00288634**. So **0.0028863 was right and the transcribed
  0.0595338 was the misrounded one.** A competitor's public files only — no scoring call on our predictions, ledger
  stands at 6.
- **And it recorded the SECOND pair that must not be smoothed:** the 68% probability rests on the *transcribed*
  value, and that bootstrap **has not been re-run on the re-scored basis.** Naming a discrepancy you cannot close,
  beside one you just did, is the harder half.
- The best-on-board count is executed in both places **and in neither is it stateable alone** — every instance reads
  "4 of 8, and two of those four are the organisers' own baseline file, so 2 of 8 belongs to our model", with the
  four verified case-by-case against all four published submissions rather than inherited.
- **The leakage disclosure LEADS the email**, in the lab's frozen pre-registered words, admits, and only then
  mitigates: *"Nothing we did afterwards cancels it and we do not offer anything as cancelling it."* No official-rank
  language — *"if your scoring differs from ours, your number is the number."* The sweep token sits **unbroken on
  one line** in both places, after three ladder-recorded failures of exactly that kind.
- The blocking banner became a **dated discharge**: the original banner and its defect table are kept **verbatim as
  the record**, with a row-by-row closure table appended rather than the evidence deleted.
- One item flagged and correctly not taken under the single-file rule: the travelling description document still
  prints the misrounded digit and owes a one-character correction.

### 2026-08-11 — the relaxation check CONFIRMS the hills verdict, and the sweep finds S6 armed nowhere it was claimed

- **THE +63–66% MISS IS THE MODEL'S. THE VERDICT STANDS** (pre-reg `ce0b14be` before compute; results `ef3e4872`
  onward; 18.28 core-min against a declared 50, priced throughout from this case's own measured per-iteration cost).
  Three arms spanning a **third-to-triple range in path length** agree to **0.0105% and 0.0183%** — 48× and 27×
  inside the 0.5% bar — with separation, bubble topology and a nine-station profile all passing their own bars.
  **Seventeen other surfaces carrying that number do not have to move.**
- **The frame was moved BEFORE any number was taken, and that is the finding under the finding.** The record does
  name its own relaxation gap — but that sentence is about a rung **carrying no verdict**, while all three graded
  claims are read off a different rung. Testing the named rung and reporting it as the verdict's check would have
  been *exactly* the L-55 shape: a true sentence about the wrong thing. The graded rung was tested instead, and the
  other rung's gap is now fenced as still open.
- **The instrument was made to FAIL before it was allowed to pass.** A registered control — same case, same
  relaxation, stopped early — was refused certification at all four sample points, and the two that matter have a
  *well-formed two-crossing bubble* and still read 3.3% and 1.06%. An unconverged field reads 1.06%; a genuinely
  different relaxation reads 0.0105%. **That hundredfold gap is what licenses the headline**, and without the control
  the agreement would have meant nothing.
- A falsified prediction that failed **on its mechanism**: the pre-registration assumed the alternatives would be
  slower, and one converges in **66% of the incumbent's iterations** — so the shipped relaxation is not merely
  untested here, it is **a third slower than the solver's own default.**
- **THE PROPAGATION PREMISE WAS OFF BY FOUR LESSONS**: L-49 through L-52 had never been swept either, so the debt was
  nine, not five. **16 of 20 cells carry a live instance**, and L-55 hits all four families.
- **The serious one, and it lands on a rule we wired tonight:** the monitor standard says the residual-stall rule
  **fires on production and names a specific family** — but the gate has exactly one non-test call site, and that
  family's runner never reaches it. **Every test bypasses the constructor to call the gate directly, so the tests
  prove it works WHEN ARMED and nothing proves it GETS armed.** Routed to Infra: the wiring is real, the coverage
  claim is not.
- **The transferable result of the whole sweep**, in the agent's words: in all four families **the falsifying fact
  was already written down** — eight lines above, thirty-seven lines later under another item, in a sibling document
  with the correct scope. **Nothing was hidden.** Twenty-three items routed, none fixed across a family boundary,
  every instance re-measured by the sweeper because *a delegated null is a claim about the delegate's reach.*

### 2026-08-11 — the coverage sentence is corrected by call site, and the failing shape appeared exactly once

- **THE FINDING HOLDS AND ITS AUTHOR OWNED IT PLAINLY** (`675442fd`): *"the act my own coverage sentence named was
  never armed."* The runner constructs the engine and calls **thirteen** of its methods — the one that arms the gate
  is not among them, because it stages its case another way. The wiring and its measured fire rates are untouched;
  they were always claims about behaviour **when armed**.
- **Corrected by CALL SITE, not by family.** The standard now enumerates the six paths that actually reach the
  arming point, names the runner that does not, and covers any future runner that stages a case another way. The
  agent explicitly refused to substitute a different family name — *"naming a family is what went wrong, and a
  correction that named another would repeat it."*
- **Two tests, both through the real constructor**: one asserts the gate comes out armed **without the caller asking
  for it**, and one **pins the arming-site count at exactly one**, so a second site makes the standard's enumeration
  go stale *loudly* rather than silently. Verified by removing the arming line in a scratch copy — both fail, and
  they are the only tests of that rule that do.
- **The reusable half is a rule about tests, not about monitors:** every existing test of this rule reached **past**
  the constructor to call the gate directly. *"A test that reaches past the constructor cannot see a constructor
  that never calls the thing."* They proved the mechanism and were silent on reach, which is exactly the blind spot
  that let the false sentence stand. Written down as: **a coverage claim is tested through the same door production
  uses.**
- **The derivation, which is the part that closes the question rather than the instance:** 14 per-rule coverage
  claims, 13 of which name only prose. Classified — corpus fire-counts are *measurements* with replay artifacts, not
  reach claims; scope claims are either **enforced in code** or **self-enforcing by construction** (a steady log
  contains no Courant line at all, which is stronger than a guard); and **production-reach claims number exactly one
  — the false one.** So the failing shape appeared once, established by a repeatable check rather than a reading.
- Suite 1295 passed, 1 failed — **and the failure is the exec-bit guard firing on a live agent's just-committed
  script**, a guard that exists because of this same family's earlier finding. The system working as designed, on
  work in flight. Routed, not touched, because that agent is mid-arm.

### 2026-08-11 — V10's surface closes clean, and the guard that would have caught it is derived rather than listed

- **The digit was fixed by MEASUREMENT** (`fdb1ec5c`): the checker re-ran the benchmark's own scorer over the
  competitor's published directories at the frozen commits and **independently reproduced the resolution to all 20
  digits** rather than trusting the record that resolved it. The second discrepancy — that the probability rests on
  the transcribed value and its bootstrap has not been re-run — was **left standing and its arithmetic confirmed**,
  not smoothed.
- **Three rank claims on the bundle's most prominent page now carry the figure and its bound** (`87f84b44`), after
  verifying the page is **not** generated (its sibling is, at a named line) so the fix could not be overwritten. The
  interval used is the **double**-bootstrap band, not the Monte Carlo one — which measures only how long the
  resampling ran.
- **THE GUARD IS DERIVED, NOT LISTED** (`1611011b`): every tracked path plus every member of every shipped archive,
  matched on the *assertive form* of a placement near the closure board — **35 claim-bearing surfaces out of 20,641
  paths, a set no maintained list had ever matched.** Severity is derived too: travelling surfaces FAIL, lab records
  WARN. **The one list it does contain — homonym exclusions — is named as a list in the code**, and excludes senses
  of the phrase rather than surfaces, because without it the guard fires on solver logs and gets switched off.
- **It states what it cannot see**, in the verdict line, not a footnote: non-UTF-8 (so a claim living only in a
  compiled PDF is invisible while its source is not), untracked files, oversized files, render-time text, and — the
  subtle one — **the distance from a claim to its companion, since compliance is per file, so one compliant
  paragraph clears every claim in that file.** 13 tests, all failing against the prior code, with the anti-list
  property pinned by **a surface invented inside the test that no list has ever contained.**
- **Two of the checker's own absence claims came back FAIL — and the artifact was right, the claims were wrong.**
  Two old scores DO appear in the bundle, as correctly attributed round history. It **replaced the blunt absence
  claim with the true one** (never unattributed to its round; 5 and 4 occurrences, all attributed) and added a
  positive assertion instead — rather than deleting the test that failed.
- **Rebuild: drift gate PASS, zero items**, verified on the extracted committed archive and then **over HTTP**, with
  a positive control that planted the four literals and reflowed the token — proving the instrument finds what is
  there and that the wrapped-token failure mode is detectable. Served bytes equal extracted bytes.
- **One member changed that nobody asked for, and it is named in the commit**: a certificate PDF, 74 bytes, new
  serial over identical evidence, traced to the suite re-running that act mid-round. Shipped as built rather than
  hand-restored — the honest choice, and stated.
- **New standing debt made visible for the first time:** 9 lab records still claim rank 1 with no companion. All
  non-travelling, all pre-existing, none previously findable.

### 2026-08-11 — an 84-member UQ ensemble with no convergence evidence of any kind

- **THE FINDING THAT OUTRANKS THE TASK THAT FOUND IT.** Pricing a proposal surfaced it: **84 of 84 members** of a
  random-matrix UQ ensemble carry the **unreachable residual target** — the exact defect one case family diagnosed
  and closed *for itself* on 2026-08-05 and **never propagated**. So **0 of 84 print a convergence sentence, and
  that zero is a FALSE NEGATIVE rather than a convergence fact.** Separately, **76 of 84 have a momentum residual
  RISING over the run's second half** — the worst by 9.94×. **An 84-member ensemble feeding a UQ result has no
  convergence evidence of any kind.** Stated as measurement, routed to its owning family.
- **A census turned a single-case finding into a reach measurement**: of 317 configuration files carrying a
  relaxation block, **122 (38.5%) sit at the inherited setting** now measured a third slower than the solver's
  default — and only 5 at the default, **three of which were created tonight.** The proposal is priced per case from
  each case's own log, with **one arm recorded as a cost GAP requiring a feasibility probe rather than estimated**,
  and the four published rungs excluded in writing because re-running them would re-base a result onto a number
  produced after it.
- **L-59 — a fix that appears to succeed.** This repo has `core.filemode` false, so an exec-bit fix followed by a
  pathspec commit is **silently discarded**: the index says 100755, the written tree says 100644, and the guard
  reads GREEN off a tree that never changed. Avoided only because the module's own docstring warned of it, then
  **verified against HEAD, which is the authority**. Fixed with a **one-invocation config override rather than a repo
  config change**, which would have perturbed five concurrent agents' diffs.
- **A test has been red for TEN DAYS and it is a real defect, not flake.** Established rather than asserted: it
  reproduces in isolation, fails against a **clean archive checkout of HEAD** (so it is committed state, not local
  dirt), and bisects to its introduction. The observed roster shows the fleet bouncing between two waves — **exactly
  what the test's own comment says must not happen** — and only the solved-API subtest fails. Routed to its owner.
- The sentence the sweeping agent asked to keep, and its reason for keeping it: *"the falsifying fact was already
  written down… What the machinery buys is not discovery — it is that someone looks in the right place."*

### 2026-08-11 — V8 still FAILS, and the blocking claim is one no digit-level check could see

- **The cover email is FIXED and verified fixed** — all six defects **closed, not edited**, each traced to a primary
  artifact, with the scorer re-run at the frozen commits for a **third independent 20-digit reproduction** of the
  resolved margin pair. Best-on-board verified at full precision on exactly the four named cases. 8/8 hashes match;
  the frozen quotation is verbatim; the pre-registration-to-scoring gap is 12 m 59 s exactly as claimed.
- **F1, BLOCKING, in the document that travels — and it is a rank claim in disguise.** The description document calls
  the runner-up **"the rank-3 entry."** The published board puts them at **rank 2**, and the lab's own source record
  for that very sentence says rank 2. **"Rank 3" is only true in a five-way list that inserts our own unsubmitted
  entry at the top** — so the phrase is **a rank claim for ourselves, carrying no probability, no interval and no
  undecided pairs**, three sections before the ones that do.
- **Why every prior pass missed it, in the auditor's own words: *"because it is not a digit."*** The claims table's
  frame is quantitative sentences; this claim is encoded in an **ordinal word**. Thirty-of-thirty-one passed it, and
  so did 63 digit-level checks in this very audit. **A claims table that verifies numbers cannot see a claim carried
  by a word** — which is the frame lesson again, on the instrument the ladder trusts most.
- Three further failures are **text this fix round wrote**: two passages still assert that the travelling document
  "owes a one-digit correction" which had already landed four minutes earlier, and one says the competitor's
  published directories number four when there are eight — **in the very sentence reporting a re-score that
  necessarily read all eight.** Plus two minor: a "kept verbatim" that is true of a defect table and false of its
  rewritten headline, and one number attributed to a group when it belongs to one entrant.
- **Ladder consequence, stated by the rung:** the round is **not clean on its own output**, so round N+1 exists. The
  six hard checks all passed, including the sweep token unbroken at all seven occurrences — measured with a detector
  whose positive control proves it can tell wrapped from unwrapped.

### 2026-08-11 — the ensemble's agreement with reference data is produced by its LEAST-converged members

- **ALL THREE NUMBERS CONFIRMED, none overstated** (`735517cd`), each negative carrying a control — including a
  **spliced control**: the same count over the 84 logs *plus one converging log* returns 1, proving the instrument
  can see the sentence it reports missing. One honest refinement: the missing sentence is a **false** negative for
  exactly one member (the control, which genuinely converged) and a **true** negative for the other 83.
- **MECHANISM: capped, and nowhere near converged.** 82 of 84 stopped at the iteration cap; two have truncated logs
  and **were admitted through the residual gate on stale residuals.** Only one snapshot exists per member, so the
  quantity of interest cannot be trended — and the one per-iteration output that can be **is not settled**: median
  swing **86% of its own level** over the final 500 iterations, **23 of 84 reverse its sign**, and only **2 of 84**
  settle below 5%. The control settles to 0.08%, which is the positive control proving the instrument sees settling.
- **THE FINDING THAT DECIDES EVERYTHING, and it was never measured before: reattachment is a MONOTONE FUNCTION OF
  SETTLEDNESS.** Most-settled quartile mean 7.21 against a baseline of 7.64; least-settled **5.25**, against
  reference values of 4.6–4.7. **The members that carry the ensemble's agreement with reference data are the
  least-settled ones.** Restricting to the settled half drops profile coverage from **1.000 to 0.752** and halves the
  envelope width. Stated honestly as correlational — a competing physics reading cannot be excluded on existing data.
- **23 claims graded: 8 SURVIVE, 5 QUALIFIED, 9 INVALID.** Everything solver-independent survives — the sampler's
  checks, two genuine bug finds, a paper inconsistency, a sign error, the cost record. **What fails is precisely the
  quantitative reach toward the reference data.**
- **AN INVERSION, and it has already reached binding governance.** The family's most-propagated conclusion —
  *"report the ungated ensemble"* — is what this audit most directly contradicts, and it now sits in a **binding
  pre-registration, a live program rule, and a pre-registered proposal gate.** Independent corroboration already in
  the repo: **98 of 175 archive-wide residual-stall firings are this ensemble's members — 56% of all firings from 6%
  of the corpus.**
- **PROPAGATION: 120 of 365 configuration files carry an unreachable target** *(confirmed 2026-08-11 as the
  claim-bearing figure; a sweep's 136 of 381 was withdrawn — its 16 extra files are an auditor's own continuation
  copies)*, derived from the self-relation rather
  than listed. 84 are this ensemble; **21 in an unexamined family recommended as the next audit**; 5 are inherited
  from the benchmark's own authors and **deliberately preserved with cause**, which the derivation correctly
  distinguishes.
- **Why it travelled is now L-60:** the parent case closed this exact false negative **by argument**, earning it with
  a monotone four-decade residual history. The ensemble **inherited the dictionary and the excuse — but not the
  evidence that made the excuse valid.** A waiver is evidence-bearing, and the evidence does not copy with the
  configuration.
- **Not recoverable from existing data** — no intermediate snapshots exist. Priced, not proposed: caveats plus
  escalation at 0 core-min; **152 core-min to continue the 13 coverage-carrying members**, the only step that
  discriminates artifact from physics; full re-runs at 15–26 core-hours. With a caution that matters: since the
  control settles and the members do not, **the perturbed cases may have no steady solution at all** — in which case
  no target and no cap would ever produce one.

### 2026-08-11 — the ordinal sweep finds the defect's source, and the guard we built tonight cannot see this class

- **F1 fixed with the board verified at the frozen commit AND re-derived arithmetically** — the benchmark's own
  scorer re-run over every entrant's eight CSVs, giving the same ordering the README states. Not taken from a report.
- **THE SWEEP FOUND THE SOURCE, not just the symptom.** Frame: 20,542 tracked files → 111 referencing the
  leaderboard → **107 entrant-adjacent rank statements, 18 flagged, 17 proximity artifacts checked by hand, 2 real.**
  The second is **the same wrong ordinal in the sentence family that SEEDED the travelling copy** — the defect had a
  parent, and fixing only the child would have left it to be re-copied.
- **The agent's own instrument failed first, exactly as the auditor's had.** Its line-bounded pass scored 63 of 64
  and missed the second instance, because that line ends mid-phrase with the entrant's name on the next line. Its
  conclusion generalises the night's most-repeated defect: **a line-bounded reader missing a wrapped claim is not
  specific to one token.**
- **A THIRD instance of the same shape, carried by a comparative rather than an ordinal**: *"the runner-up"* used for
  the entrant who is **rank 1** on the published board. True only in a five-way list with our own unsubmitted entry
  on top — **the identical silent rank-1 assertion**, in the travelling document, three sections before the passage
  that states the claim properly. Three sites fixed.
- **What it deliberately did NOT touch is as good as what it fixed:** all eight per-case ordinals re-derived
  independently and found correct; and statements under dated round-3 headings left alone because **re-basing them
  onto round 5 would destroy the record.** One "verbatim" claim was **measured** — 30 body lines byte-identical, the
  heading replaced and demoted, a blank line changed — and all three stated, because *"only the heading changed"
  would have been the same overreach one line smaller.*
- One correction was **worse than stale**: a record printed the misrounded value **inside the very sentence
  introducing the re-score as its corrective.** Amended, with everything the block protects left standing.
- **ESCALATED AND NOT TAKEN — the guard we built tonight cannot see this defect class.** Its rank-claim pattern is
  **digit-anchored**, so neither the wrong ordinal, nor its parent, nor any "runner-up" site would ever have fired —
  and **the file's own comment already admits it** cannot see a rank claim phrased in words. The agent refused to
  extend it on the ground that **new guard patterns are unverified code entering the ladder**, and recommended a
  rung instead. Correct, and it is now the ladder's next structural gap.
- Also escalated rather than resolved: one sentence that is **false on overall standing and true on the ducts it is
  actually about** — with the cover email's parallel phrasing named as the candidate fix precisely because it
  carries no placement word at all.

### 2026-08-11 — the ten-day-red fleet test is green, and for ten days it was reporting how busy the box was

- **CLOSED: the suite's one red, open since 2026-08-01.** Verified green on my own independent run
  (`1 passed, 4 subtests passed`), not on the agent's word.
- **Three agents saw three different things, and none of them was careless.** The test asserted the worker
  roster takes exactly three steps; the roster's **shape is a function of the box's free cores**, not of the
  code. On **identical committed source**, forced probes gave `[0, 6, 0]` · `[0, 9, 0]` · `[0, 10, 9, 0]` ·
  `[0, 14, 9, 0]`. It flipped colour **inside one session** — red at 02:41 at capacity 14, green at 02:47 at
  capacity 5, after eight other agents' jobs landed on the shared box.
- **The comment and the assertion had disagreed since birth** — both committed 13 seconds after the fix they
  were written to pin. The fix's own message records the defect as a **bounce**; the comment forbids a bounce;
  **the assertion forbids any change of size at all**, a strictly stronger claim than the workflow, the control
  room, or any standing ruling makes. The test over-reached its own comment by one quantifier and the busy
  machine hid it.
- **The repair is not a loosening, and that was the hard part.** Deleting a failing assertion is not a fix. The
  new rule is that **each level must equal the fan-out actually running** — the slots the sweep dispatched to,
  the slots carrying a live solve. **The number is pinned to the run rather than to a constant**, the same
  principle that made the convergence detector trustworthy: gate on a relation the system states about itself.
- **Verified in both directions in isolated trees**, which is what closes it: the old assertion **fails** against
  HEAD at forced 24 cores and **passes** at 8 on identical source — the defect demonstrated rather than argued —
  and the new test **fails at both capacities** when the original bounce is restored.
- **Bonus finding, and it clears a shoot worry:** the two recordings were pulled apart by their roster traces.
  The wrong one that was shipping shows `granted = 13`, which **proves it was a recording of the standing prompt,
  not the typed shoot-day directive** — one mistake produced both symptoms, the wrong span ladder *and* the only
  run with the step-down on screen. The rebuild already fixed both; on the shoot-day prompt this box would need
  ≥ 20 cores to show a step. **No camera risk, nothing to change for the shoot.**
- Recorded as **L-62**: a test whose verdict depends on spare cores is a load sensor wearing a test's clothes;
  when a test disagrees between people, suspect the environment before the observers.

### 2026-08-11 — the convergence-target audit exonerates the runs, corrects our own count, and finds the detector's headline is not held-out

**The audit was sent to look for false convergence claims and found none — that is the result, and it is a good one.**

- **Frame first, and it corrected my brief twice.** The corpus is **21 of 21** of the eligible population, not a
  sample — `residualControl` lives only in `fvSolution` and there are exactly 21. The auditor named the trap
  himself: **"21 flagged" carries no selectivity information**, because the flag could not have returned any other
  non-zero number. Second correction: my brief called these "never examined"; that was **stale by three days**, so
  the numbers were **re-derived independently** rather than the earlier narrative repeated.
- **The 21 collapse to 2 distinct files by md5** (8 `ph_*` share one, 13 `cbfs_*` another; residual content
  byte-identical). Twenty-one cases, two derivations, fully auditable.
- **(a) Unreachable AND claimed converged — ZERO of 21.** Every convergence statement about these runs rests on a
  criterion **pre-registered before the runs**, never on the dead lever; and the one run that failed it is reported
  as cap-stopped unsettled and **excluded from grading under the paper's own exclusion rule**. Nothing to escalate.
- **(b) Wasted compute — 16 of 21**, priced from the logs: **≈45 core-minutes of provably unnecessary iteration**,
  a lower bound, with per-case stop points measured. **A finding inside the finding:** for the CBFS family the
  obvious remedy would not work — pressure plateaus around 1.5e-6–6.7e-6 while momentum falls to 1e-9, so a
  "reachable-looking" 1e-6 target **still would not fire.** *A reachable-looking target that never fires is the same
  defect wearing better clothes.*
- **(c) Flagged in error — 0, but our headline over-reaches on 5.** Five cases never execute a pressure loop at all
  (two `-postProcess`, one `endTime 0`, two solve only k/ω). **Counting them is counting a dead switch in an
  unwired room.** Honest split: **16 live-but-harmless + 5 inert.**
- **Controls in both directions, including one the earlier ladder lacked.** Seven synthetic cases with ground truth
  declared before running, plus real positive and negative files. **Control G is the one that matters**: a config
  whose *dead* commented value is `1e-15` and whose live value is reachable — it stays silent, proving the
  instrument is **not string-matching `1e-15`.**
- **One disagreement with the earlier audit, and it strengthens that audit:** 2 of 16 momentum residuals rise, not
  1. Both risers are the **deliberately sign-flipped falsifier arms** whose degradation is the reported finding.
  None of the 10 publication-bearing runs rises.
- ~~**OUR OWN COUNT HAS DRIFTED AND NOBODY RE-RAN IT.** "120 of 365" is now **136 of 381**.~~
  **WITHDRAWN BY ME, 2026-08-11 — and the withdrawal is the more useful finding.** The arithmetic resolves exactly:
  381 − 365 = 16, 136 − 120 = 16, and there are **precisely 16 `fvSolution` files under `f6d_option_a`** — an
  auditor's **own continuation copies**, whose targets its own pre-registration deliberately leaves unchanged. Both
  counts are right for their moment and **neither is a worsening.** The claim-bearing figure is still **120 of 365**.
  I published the 136 without asking where the growth came from. *A defect count that grows because an auditor made
  copies to audit with is exactly the number that gets quoted once and corrected never* — and I nearly made it one.
  **Second defect in the same action:** my in-line correction to the propagation figure **silently matched nothing**
  and never landed, while the commit message announced it as done. A `str.replace` that finds no match is a **no-op
  that reports success**. Only luck made the un-landed edit the correct outcome. Recorded as **L-67**.
- **THE ESCALATION — the S6 headline is not the held-out number it reads as.** The detector's docstring names its
  motivating sentinel as literally `p 1e-15;//1e-4;`, which is the **exact byte sequence** in one of these cases,
  and 18 of these 21 logs are **inside the corpus the 135-of-135 was scored against.** In the auditor's words:
  *the detector and this corpus are not independent evidence of each other.* The rule is not thereby wrong — it is
  still constant-free and still correct on every case examined — but **the evidential weight the score carries is
  not what we have been quoting.** Recorded as **L-63**; a held-out re-score is now owed.
- **Two provenance defects found while not looking:** a run whose prose says it "stopped by the pre-registered
  protocol, not by a cap" while **its own log records a fourth segment launched and killed 519 iterations later**
  (no graded number moves — the checkpoint is intact — but the prose describes a clean stop where the artifact
  records a kill); and **archived `controlDict`s that cannot reproduce the pre-registered campaign** — declared
  caps 30,000/10,000 against 20,000/12,500 on disk, wrong in *both* directions.
- **Remediation priced and declined: 152 core-min to re-run, buying zero correction** — the graded quantities are
  checkpoint field norms already written to disk, and a target that never fired never altered the trajectory.
  Editing the config under a completed, cited run would make the archived dictionary stop matching the one the
  cited solve actually read. **Recorded against the case rather than in it.**

### 2026-08-11 — two rulings on the 84-member ensemble, and a funding rule pre-registered before the evidence lands

**Both decisions were escalated to me rather than taken, and the escalation is the good news.** The agent's gate
fired VOID on its own experiment, it worked out that its own gate was mis-specified, and it **did not rewrite it** —
*"doing that after seeing which way it fell is the precise sin pre-registration prevents."*

- **RULING 1 — the literal reading. The experiment is VOID.** Not because the agent's analysis is wrong; it is right,
  and the restart-transient mechanism it named is excluded by measurement (two of three controls flat). It is because
  **"the premise turned out to be false" is a conclusion reached after seeing the outcome.** A gate that can be
  dissolved by post-hoc argument is not a gate — if that move is available once it is available always.
- **The VOID costs far less than it looks, and the split is the ruling's real content.** A control exists to isolate a
  **difference**; a claim that is not a difference claim never needed one.
  - **Survives**: that **no member reached a settled state**, several past 12,000–16,000 iterations — and above all
    that a case chosen **because it was among the best-settled of all 84** destabilises on continuation into a growing
    oscillation past 1.3 x/h. **It had been in a quiet phase of an unsteady flow, not at a steady solution** — which
    no static settledness measure could have distinguished.
  - **Dies**: "10 of 13 moved, 9 toward baseline." That is exactly the comparative the controls were there to
    license. It may not be carried over, and may not be laundered by restating it as description.
- **The asymmetry is why the ruling is cheap: the surviving evidence points at Outcome 3, and the evidence that dies
  is what would have supported Outcome 1.** The VOID is conservative in the funding direction — **it can only stop us
  spending, never start us.** That is the safe direction to be wrong in.
- **The gate did not mis-fire.** Its trigger caught something real — *the control was not a control.* Only its stated
  inference was wrong. Recorded as **L-65**, because "the gate mis-fired" and "the gate fired for a reason it named
  badly" are opposite lessons and only the second is true here.
- **RULING 2 — funding rule PRE-REGISTERED NOW, before the remaining 5 cases land** (5 of 16 still running as this
  was written):
  - **no member of the 13 settles → Option C is NOT funded.** 25.7 core-hours would buy 80 more arbitrary phases of
    an unsteady flow. *A longer run of a thing that does not converge is not more evidence, it is the same evidence
    at higher cost.*
  - **≥ 1 member settles → Option C stays live**, and I want that member's identity and its distance from `null`
    before anything is committed.
  - **`null` remains the only settled run → that is the headline**, in these words: **the only settled member of the
    ensemble is the only unperturbed one** — which says the perturbation, not the numerics, prevents settling.
- **THE COINCIDENCE I AM NOT TAKING ON ANYONE'S WORD: the case that collided is the case that went VOID.** A launcher
  collision put two solvers on `d0.2_s000`, and `d0.2_s000` is the control that moved −0.831. ~~The chain excluding
  causation looks sound to me — duplicate died at ~4265, first field write at 4500, ladder monotonic and
  single-writer, reattachment comes from fields while the damage was to the log.~~ **THREE OF THOSE FIVE LINKS ARE
  NOW FALSIFIED — see the correction entry of 2026-08-11. I published that chain as sound. The conclusion stands;
  the reasoning does not.**
- **The collision itself, recorded as L-64.** The rule we already had — use durable, self-ledgering launchers — is
  what made *both* launchers durable, and durability is what made the collision possible. The rule actually earned is
  narrower and the opposite shape: **two durable launchers over one case set are worse than none.** The second
  launcher's guard (launch only if no log exists) failed because **output appears after the race is already lost.**
  Damage was bounded by measurement, not argument, and the agent named itself as cause in its own commit.

### 2026-08-11 — the S6 headline survives on a corrected scope, and my own lesson about it was wrong twice

**Commissioned to check whether our "135 of 135" was really held-out. It is — and the re-score corrected L-63, the
lesson that commissioned it, on two specifics.**

- **Every shipped figure reproduces exactly** before anything else is claimed: 135 excluded / 81 gated / 6 fail-open,
  35 fires, 48/92/20, zero "nothing else" violations — all produced by **importing the shipped helpers**, with no
  reimplementation, because a second implementation agreeing with itself proves nothing about the first.
- **THE HEADLINE SURVIVES, SCOPE CORRECTED, NOT WITHDRAWN.** In-sample **33/33**, held-out **102/102**, zero false
  captures either side — and the pre-registered 92/48/20 spread sits **entirely in the held-out partition.** I was
  right that the number needed splitting and **wrong that splitting would weaken it.**
- **L-63 named the wrong specimen.** It read the sentinel as `W2_sparta_runs/cbfs_prop`; the git record points at
  `dafoam/ladder-b/B3_work`. The byte sequence appears in **18 files**, so "the docstring cites this case" never
  identified which. The re-score **partitioned both ways rather than choosing** — the right move.
- **And the real limit is one I did not see, which is sharper.** Archive-wide, **every unreachable target is the same
  value** — `(1e-15, 1e-12)` ×132, `(1e-15, 1e-14)` ×4. So our constant-free relation and the **bare literal
  `target == 1e-15`** are **extensionally the same predicate on this archive**, agreeing on all 239 files in both
  directions. The 102 held-out captures are copies of the specimen propagated by template reuse: **held-out in
  provenance, in-sample in content.** Tightest ratio 50×, median 1000×, excluded class 0.001× — a **~4.7-decade gap
  the boundary has never been probed in.**
- **Operative correction to our wording:** drop *"evidence the rule generalises"*, say **"evidence the rule tracks the
  sentinel wherever the template was copied."** Recorded as **L-66**: a held-out score over near-duplicates measures
  template reuse, and the cheap test is to **build the crudest rival rule and see if the corpus can tell them apart.**
  Ours cannot — which is a reason to stop citing this corpus, not to abandon the rule.
- **The negative side was re-derived** (it had never been checked): of 1,240 not-flagged logs, the gated classes are
  **disjoint per field**, the fail-opens are clean on hand-reading, and **zero cases anywhere declare a 1e-15 target
  and escape.** Also: 21 defect-carrying cases have **no run log** and were never counted by the 135 — unknowable
  rather than missed, and the distinction is stated.
- **NEW CODE DEFECT, needs a rung:** `_solver_tolerances` **cannot resolve OpenFOAM regex-group field keys** — a
  `residualControl { "(U|p)" }` never meets `solvers { "(U|k)" }` because matching is string equality. **All 6
  "fail-open" logs are this**, so a parser artefact has been reported as a property of the archive; and one case is
  **armed on a third of what it declares.** Fails safe, but it silently disarms the gate.
- **AND THE FINDING I MOST NEEDED TO HEAR: our pre-registration's own sentinel row is retrospective wearing a
  prediction's clothes.** Its 135/81/6 table was **computed in the same commit that states it**, yet sits in the
  RESULT table beside genuinely forward predictions marked "met". **That is L-63's failure mode reproduced inside the
  document L-63 is about.**
- Worth keeping: **retaining the superseded artifact is the only reason provenance was answerable at all.** Without
  the superseded replay JSON the answer would have been "not establishable."

### 2026-08-11 — the two provenance defects were 3× larger than reported, and the fixer's own first pass reproduced the false negative

- **Defect 1 verified against the artifact**, not argued: the log holds **four** restart segments, and the fourth has
  **no `End`** — it stops mid-Time 15,519 with only Ux/Uy solved. `grep -c "^End"` returns 3.
- **No number moves, and it is settled by evidence rather than asserted**: the next write was due at 20,000, so the
  kill was 4,481 iterations short of touching anything; checkpoint files timestamp **before** the log's final write;
  and the 519 stray iterations were **already priced** in the cost basis. The true half of the original claim was
  kept — the protocol really was satisfied at 15,000, far below the cap.
- **Defect 2 was 3× bigger than the audit found. 6 mismatch, 12 match, 3 have no declared limit** — the brief arrived
  with 2 and **4 more `cbfs_m*pub` files were found by checking all 21.** *A defect found in two files and never
  searched for in the other nineteen is a sample, not a finding* — and this time the sample was wrong by a factor of
  three. Cause differs by direction: the understating files record **the last manual segment launched**, not the cap;
  the one overstating file is a deliberate beyond-cap confirmation segment **already labelled as such at the time.**
- **Not one case artifact was touched.** The correction went into prose plus a new archive-side note, per the rule
  that editing the dictionaries would make the archive stop matching the solves it documents.
- **The searcher's own first pass reproduced tonight's signature false negative.** Its pattern `not\s+by\s+a\s+cap`
  missed a second surface reading "stopped by protocol, **not cap**"; the looser second pass caught it. Denominator
  stated: **3,935 files scanned twice, whitespace collapsed before matching so wrapping cannot hide a phrase.** The
  claim exists on **exactly one** surface.
- **What it declined to touch is again the tell:** two JSON mirrors that never carried the claim (*"adding a stop-
  condition field they never had would be inventing a surface, not correcting one"*), and two dated pre-registrations
  whose cost line is **evidence the fourth segment ran, not a defect.**
- Found while not looking: the frozen solves **arithmetically confirm the pre-registered "+20% verification" rule**
  (settled 295 → wrote 354; settled 1,243 → wrote 1,492), independently validating the protocol those controlDicts
  encode.

### 2026-08-11 — the ensemble result lands under the pre-registered rule: Option C is NOT funded

- **The rule was committed BEFORE the last cases were read** (`ce6a66b4`), which is the only reason the verdict means
  anything. All 16 finished; zero solvers and zero queue runners remain; the published tree is pristine.
- **VOID taken literally.** The contested control finished at **−0.491 x/h** against a 0.25 threshold. The agent also
  **corrected its own earlier framing** at my ruling — it had called its gate *mis-specified*; the record now says the
  gate **was not wrong to fire**, its trigger caught something real, only its stated inference was named badly.
- **THE HEADLINE, and it survives the VOID because it needs no control: the only settled member of the ensemble is
  the only unperturbed one.** `null` at **0.031** is the sole case of 16 below threshold. Solver, mesh, restart path
  and budget are **identical across all 16** — the perturbation is the only difference, present in every unsettled
  case and absent from the settled one. **The perturbation, not the numerics, prevents settling.**
- **Zero of 13 members settled after 16,000 iterations — four times the published budget.** Several ended *worse*.
  The case chosen as a control **because it was among the best-settled of all 84** wandered 6.34 → 5.84 → 5.34 → 5.85
  → 5.00 and ended unsettled.
- **The headline does not rest on the contested case: drop it entirely and it is 12 of 12 unsettled, with `null`
  still the only settled run.** That is the right way to report a result with a disputed member.
- **The comparative did not survive and was not laundered.** Raw deltas left in the JSON for whoever re-registers it.
- **OPTION C IS NOT FUNDED**, by the rule fixed before the numbers were read. The nine INVALID claims stay INVALID and
  **recoverability stays open**, because the experiment that would have closed it is void. What changed is the price:
  **the cheap route is spent, and the surviving evidence says a longer steady run is not the instrument.** If the band
  is recoverable at all, the next pre-registration should price a **time-averaged unsteady statistic** instead.

### 2026-08-11 — the instrument integrity ledger: one verdict in three has never been shown to fire

- **Four independent enumeration axes, and the method's headline is that they disagree.** Verdict-word emission (89),
  filename self-declaration (137), non-zero exit (165), alternate lexicon (24) over a 534-file base → union 296, 142
  production, **66 verdicts profiled in full**. **Axis A missed 12 of axis D's 24 — half of one class** — and A and D
  together missed 13 instruments only their *names* revealed. **A single-lexicon sweep would have reproduced the
  `*.log` vs `log.<app>` glob error one level up.**
- **CLASSIFICATION: ~~reach demonstrated 30 · reach assumed 25~~ → CORRECTED 2026-08-11 to 28 · 27 · 11.** An
  independent headline audit found two instruments classed *demonstrated* on bases that are **reach statements, not
  firings** — so **"never been shown to fire" rises from 38% to 41%**, and the correction makes the ledger's central
  finding **stronger, not weaker.** And ~~32~~ **31** of 34 self-audit checks have no test — three have one, **and
  the ledger names the third itself.** 16 of
  those currently pass, so **nothing distinguishes "found no defect" from "cannot find a defect."**
- **RANKED BY COST — and #2 is urgent because it guards the shoot:**
  1. `case_preflight.sh` — **PASS on an empty directory**, and *silent* under `--quiet`, which is **the only mode the
     launcher uses.** Reproduced firsthand. **146 `.done` records rest on it.**
  2. ~~`audit_transcripts.sh` — reports *"clean"* **over a corpus root that does not exist**; the verdict counts
     none of the 17 transcripts.~~ **FALSIFIED 2026-08-11 — see the correction entry of that date. The configured
     root exists, is the exact path the 17 transcripts live at, and the gate has been reading all 17 all along.
     I published this and it was wrong.** The *class* is confirmed — it could not distinguish "scanned everything,
     found nothing" from "scanned nothing" — and the fix found **8 real hits**, now a decision item for Katie.
  3. **30 of 34 self-audit blind spots are computed, attached to the row, written to `--json`, and never printed.**
     This is tonight's L-61 in a worse form: **the caveat's presence in the data structure lets the check pass its own
     meta-audit while the reader never sees it.**
  4. The rank guard — digit-anchored, three known misses, verdict says *every travelling surface complies*.
  5. `is_idle.sh` — concludes idle from an absence; **6 work classes missing, verified line by line, and the code
     defect is real and current.** ~~Cost already realised 2026-07-30.~~ **RESOLVED 2026-08-11 — the cost is real
     and it belongs to a DIFFERENT SCRIPT.** The power-off is `/usr/local/bin/auto-stop.sh`, a **root cron job
     outside the repo** whose line 11 is literally `logger "auto-stop: idle ${idle}min, shutting down"; sudo
     shutdown -h now`. `sdk/scripts/is_idle.sh` is a **repo diagnostic that prints BUSY or IDLE and halts nothing.**
     The auditor was right that no wiring exists — **because it was the wrong script.** The two share a defect
     *class* (both conclude idle from a `pgrep` absence) and are different objects, which is exactly the
     same-token-different-object hazard found tonight in the adjoint attempt tables. **Both defects stand; the cost
     attaches to the cron job, not to the diagnostic.**
- **HUMP-ADJOINT — 11 distinct attempts + 3 staging faults, and ZERO were ever deliberately reproduced as a negative
  control.** 4 abandoned with no root cause, 2 built and never executed; two signatures verified against the logs
  directly, both **superseded, never explained**.
- **THE CONSEQUENCE, and it corrects a standing account of ours:** the position that the hump is *"blocked on
  convergence rate, not singularity"* rests on one attempt **killed at iteration 900 that never produced a
  `KSPConvergedReason`.** The rate was **never measured to completion** and the memory envelope was **never shown to
  be binding**. That is a capability boundary **assumed, not measured** — and we had it written up as filing-ready.
  Dispatched for correction, with the instruction not to overcorrect: we equally have no evidence the operator *is*
  singular, and the honest position is that the boundary is uncharacterised.
- **A hump gradient is claimed that never existed.** A document says the hump beta gradient *"has not been re-run
  under a second decomposition"* — but the FD-verified 3-cell gradient is **CBFS**. *A claim that X has not yet been
  re-verified silently asserts that X exists.*
- The ledger **corrected its own sub-agent** on a signature, and states its own limits: it could not establish whether
  the 16 never-fired checks would fire without planting a defect it was not authorised to write, and **its denominator
  is a lower bound, not a census** — attempts that left no log are invisible to every instrument it used.

### 2026-08-11 — I published a falsified claim about the filming gate, and the 8 real hits it found are Katie's call

**MY ERROR, corrected in place above.** I reported — here and to Katie directly — that the pre-filming discretion
gate *"reports clean over a corpus root that does not exist."* **It does not.** The configured root exists, it is
**the exact path the 17 transcripts live at**, the glob matches **precisely those 17**, and the shipped gate has
**never once printed `clean`** — run as-is it printed 5 findings. It has been reading everything all along.

**How the false claim was manufactured, and it is the most instructive thing in the report.** The audit's two
"controls" were injected copies sitting in a scratchpad, byte-identical to the real script except with `OUT=`
repointed at an empty and a nonexistent directory. **Someone read the control's configuration as production
configuration.** The ledger's own §4.2 **body is honest about this** — it shows the overridden `OUT=` on the command
line. **Its title is not, and the title is what travelled**: into this document and one other. *That is L-61 recurring
one level up — a caveat that does not travel with its headline reaches nobody* — and **I was the propagation vector**,
because I read the ledger's ranked list and republished the titles without opening the bodies.

- **The class is CONFIRMED and was worth the dispatch**: the gate could not distinguish *"scanned everything and
  found nothing"* from *"scanned nothing"*. Now it counts the corpus **before** judging it, prints **RED and exits 2
  with no verdict at all** on a missing/empty/transcript-less root, and its verdict states its reach —
  `17 transcript(s) x 3 rules (34 terms) scanned`. Five controls, both directions, all pass.
- **Three further defects found in the fixing**, each of which had been silently shrinking what the gate reported:
  it **exited 0 even with 5 hits**, so anything gating on exit code read green regardless of findings (semantic
  change flagged; no programmatic consumer exists); `head -4` **silently truncated each combination**, under-reporting
  exactly when a file had most to say; and **8 of 25 act directories have no transcript and had never been read by
  anyone** — invisible before, now named in the verdict count.
- **SIBLING GATES, reported not fixed** — and one is the other half of the pre-filming pair:
  `audit_camera_discretion.sh` **does** state its reach (`0 camera surface(s) scanned`) but **still exits 0**, so a
  typo'd act name silently audits nothing and passes; `verify_warm_replay.sh` returns all-zeros and exit 0 on a
  nonexistent act; and `case_preflight.sh` is confirmed worst — `PREFLIGHT PASS -- clear to launch` on an empty
  directory. Dispatched separately.
- **One concrete miss found**: a commit that changed the acts to say *"selected solver"* rather than the solver
  binary **missed one act**, which still names it.

### Decision request — 8 transcript lines, pre-filming, NOT edited by any agent

**Genuine hits. Nothing was changed; this is the director's call and an agent must not make it.** Three acts narrate
the cache in the words the rules header calls *"the single most important rule"*:

- `ahmed-body/transcript.txt:42`, `crm-wingbody/transcript.txt:17`, `nasa-hump/transcript.txt:28` — each reads
  **"replayed from the run that solved it"**.
- `ahmed-body/transcript.txt:37` — **names the solver binary** ("Solver of choice: OpenFOAM, steady RANS with
  k-omega SST"). The other two acts were changed to say *"selected solver"*; **this one was missed by that commit.**
- `unseen-geometry/transcript.txt:4–7` — all four lines end with an **internal documentation path** that would be on
  camera; line 7 also names the meshing tool.

### 2026-08-11 — the collision is excluded, and three of the five links I published as sound are falsified

**The disposition survives. The reasoning does not — and I had published the reasoning.** This is exactly why the
check was commissioned, and it is the best argument tonight for never letting an agent break its own coincidence.

- **(i) FAILS.** The duplicate did not restart at 4000. `controlDict` has **`startFrom latestTime`**, and the survivor
  had already written `7000/`, so the duplicate's own log header reads `Create mesh for time = 7000`. It ran
  7001→7859 over **≈60 s of overlap, not 25 — and it crossed a write time.** *"Time ≈ 4265" is what you get from 25 s
  at this case's rate if you assume a start at 4000* — one wrong premise, and it was the premise the whole
  conclusion rested on.
- **(ii) FAILS on "no rewrites".** `7500/` was **written twice**. The directory carries mtime 02:55:05 while every
  file inside carries 02:55:27 — **a directory older than its own contents is the signature of a complete
  overwrite.** And the tell was already sitting in the original report's own cadence numbers: 34–40 s throughout
  except 7000→7500 = 61.9 s and 7500→8000 = 17.3 s, **summing to a normal 79 s.**
- **(iii) PARTLY FAILS.** Fields intact — 2,896 files, no NULs, all footers, `4000/` md5-identical to published.
  But **single-writer fails at exactly one snapshot**, and *"only the log was damaged" is false*: a field snapshot
  and nine profile files were replaced. Log loss is 4000–**7329**, not 4000–7000.
- **(iv) HOLDS, traced in code** rather than accepted: the analysis opens only `wallShearStress` and the mesh, and the
  only log reader feeds settledness alone. **No path from log text to reattachment exists.**
- **(v) HOLDS.** The gate number was **independently reproduced at −0.8313**, and the collided snapshot lies outside
  every window. Settledness recomputed on the survivor's log segment alone differs by **0.27%**.
- **WHAT ACTUALLY CARRIES THE EXCLUSION is not the chain but per-snapshot writer identification.** Two independent
  records name the writer of all 24 snapshots — a stored gradient **matched at 15 digits** against each process's own
  log, and a `.dat` the duplicate never touched. **23 of 24 are the survivor's**, and the duplicate's own
  function-object directory **records exactly one write event, at 7500 — it counts its own writes for us.**
- **THE OTHER SIDE IS DECISIVE: the destabilisation's onset PREDATES the duplicate by 105 seconds.** Separation jumps
  0.257 → 2.789 x/h at Time 6000 while reattachment was still flat, and the swing keeps growing for **8,500
  iterations after the duplicate is dead.**
- **The strongest physics evidence is an accident.** The duplicate restarted from the survivor's own 7000 fields and,
  500 iterations later, **differed by 9.8% in driving pressure gradient.** Two solvers from the same state at
  restart-write precision. *A case at a steady solution does not do that* — **an unfunded twin experiment landing on
  Outcome 3.**
- **It refused to paper over the weak part.** No clean uncollided twin was found: *"best-settled case destabilises"*
  is **n=1**, and the sample splits 1–2. Analogues reproduce the mechanism but not the duration. And because my brief
  defined COLLISION EXCLUDED as *chain holds at every link* **and** *independent explanation*, and neither is fully
  met, **it recorded the departure from my own rule explicitly** rather than claiming the verdict — the same
  discipline I demanded over the VOID gate, applied back to me.
- **NEW DEFECT, and it generalises L-64:** `run_option_a_queue.sh` **checks its collision guard before an unbounded
  wait** — tests `[ -f log.simpleFoam ]`, then sleeps until the job count drops, then launches. **A case that
  acquires a log during the wait is launched anyway.** L-64's "confirm the predecessor dead" is necessary and **not
  sufficient**; this guard is stale-prone whenever the queue saturates. **FIXED 2026-08-11 — the race was reproduced
  and measured at a 20.04-second window, then closed with an atomic `mkdir` claim** (a file test is test-then-act and
  can be narrowed but never closed), with the file test retained as a second guard because the pool that caused the
  incident took no claim. Demonstrated with real races: 8-way concurrency → 7 refusals, 1 winner.
- **The general form of the hazard, worth more than the incident:** **`startFrom latestTime` makes a duplicate a
  FORK, not a repeat.** It branches from wherever the survivor reached and writes to the same snapshot names — which
  is why a 60-second duplicate hit a write time at all.
- **A free instrument fell out of it: a rewrite leaves a directory older than the files inside it.** That is a
  double-writer detector needing no log, no PID and no cooperation from the writer.
- **CONTAMINATION THAT SURVIVES INTO A PRODUCT:** the 7500 point enters no pre-registered metric, **but
  `option_a_result.json`'s trajectory and the `singleGraph_x*/7500/` profiles ARE the duplicate's** — so any future
  product consuming those inherits it. Needs marking at source.
- Also found: **`d0.2_s027` is not settled either** (0.253) while its reattachment is flat to 0.076 — *a flat QoI with
  an unsettled driver is a third behaviour the settled/moved framing does not name.* And Δ at completion is −0.4906,
  recovered from −0.8313 — **still a breach, so the VOID is unaffected.**

### 2026-08-11 — V16 is BUILT, not passed, and the guard is evidence rather than a constant

- **The board is PARSED FROM THE BENCHMARK'S OWN README TABLE, not transcribed** — so the guard is **evidence**, and
  a test proves it: **feed a permuted table and the same sentence flips clean→faulted**, which a typed-in constant
  can never do. That is the convergence-detector principle carried into text: **gate on a relation the source states
  about itself, never on a literal.**
- **Whole-text matching with a control that can tell the two modes apart**: two fixtures differing *only* in a line
  break give 1 fault whole-text and 0 line-bounded — and the test **asserts the 0 with the message "the control is
  void… so it proves nothing"**, so a future change that makes the control vacuous **fails rather than passes.**
- **It corrected its own earlier report against its own interest.** The real parent instance wraps the *name*, not
  the binding, and this guard keys on the first-author surname — so it survives that wrap either way. **It was its
  own sweep's regex, requiring the second author, that missed it.** The synthetic control is what proves whole-text
  matters. A tidier story was available and it declined to tell it.
- **The guard caught its author's own over-broad exclusion**: one rule ate *"Wu & Zhang **are** rank 2"* — the exact
  sentence the adjudication clause needed — because "are" looked like a word numeral. Restricted, with the reason in
  the code.
- **False-positive rate: 0.** The first crude instrument had flagged 18 of 107 with 17 artifacts; a broad rule measured
  at **11 hits, 11 of them noise** (the idiom *"in the first place"*, a study that *"wrote to a third place"*) was cut
  down, and **all 11 became tests.** ***Corrected 2026-08-11 by the independent grade:*** *this line originally read
  "on the 111-file board corpus: 421 placement expressions, 63 bound to an entrant". **The rate survived independent
  re-derivation over a wider frame — zero outside the declared use/mention class — but the corpus did not: no record
  anywhere states how 111 files were selected, because I never wrote the rule down.** A figure without a method is a
  citation to nothing, and this rung's own text requires the rate be stated against a* **measured** *corpus. The check
  now prints its denominator* **and its selection rule** *in its verdict — placements counted in the surfaces that name
  a board entrant, both counts shown — so the number reproduces from the frame line instead of from an unrecorded
  sweep. The lesson generalises past this rung: a denominator I can reproduce today and cannot describe is one nobody
  else can ever reproduce.*
- **Blind spots stated in the verdict line, not only in a comment**: **relational comparatives — *ahead of, behind,
  trails, leads, next-best* — need both operands and cannot be checked against one board rank.** That is *the largest
  remaining slice of placement language and it is unguarded.* Also entrants named by co-author, non-UTF-8, untracked
  files, archive members.
- **It could not engineer away use-vs-mention and said so instead.** One rule has no correct form to sit beside, so a
  record that *quotes* a defect is flagged — hence **WARN on a lab record, FAIL only where a surface travels.**
- **It bit within the hour, correctly.** On its first live run the guard flagged **another agent's ledger**, committed
  after the sweep, which quotes the three defects in order to name them. Right behaviour at the right severity, **on
  a surface no hand-maintained list would have contained.** Not edited — another agent's live file, and a mention.
- **THE DESIGN CHANGE I MOST WANT KEPT:** its first regression test asserted *the whole repository passes*, and went
  red within the hour on that very file. **A test any writer can redden by documenting a defect correctly teaches the
  lab to stop documenting defects.** Replaced with two narrower assertions. Recorded as **L-70**.
- It also amended the termination rule and send gate from 15 rungs to 16 in the same commit — *"a range that silently
  grows is how a gate stops gating."*
- **THE RUNG IS BUILT, NOT PASSED.** It found the defects and built the guard, so **under A15 it may not grade it**,
  and the V16 independence column now says so. An independent grader is commissioned.
- Verification: guard tests **35 passed**, full suite **1328 passed** *(2026-08-11: suite totals recorded tonight were
  taken from a tree eight agents were committing to, and at least one — 1309 — counted uncommitted tests. **A suite
  count is true of a commit, not of a moment**; treat any of tonight's totals as a reading, not a constant.)* One
  failure — `test_exec_bits` — is on another
  agent's newly added queue script and **reproduces without any of this agent's changes**; routed to its owner.

### 2026-08-11 — the preflight gate checked a directory that was not the case that ran, and 7 launches would have been blocked

**The exposure question had a real answer, and it was not zero.**

- **7 of 136 evaluable records would have been blocked by the new check** — 4 declared the **repo root** as the case,
  and 3 declared a **wrapper directory** while meshing actually ran in its subdirectories. **The gate checked a
  directory that was not the case that ran, found nothing to object to, and passed green and silent.** That is
  precisely the failure the gate exists to prevent, and it is why the answer is not zero.
- **The frame is stated and the number is honest about itself**: 7 is a **lower bound over 136 evaluable records, not
  over 146** — 6 case directories are gone and 4 records have no case line, so they cannot be evaluated at all. A
  further 20 fail only a pre-existing check against **post-run** state the runs themselves created — **a measurement
  artifact, not a launch-time defect, and deliberately not folded in.**
- **TWO OF THE THREE DEFECTS I PUBLISHED DID NOT REPRODUCE, and a third was overstated.** The executable bit was
  already fixed on 2026-08-10 and confirmed by a **real fresh clone**; the launcher's `[ -x ]` skip is gone, replaced
  by a `bash` fallback that gives "did not run" its own third verdict. And *"entirely silent under `--quiet`"* is too
  strong — **failures were audible.** The true defect is **narrower and worse: PASS was routed through the quiet
  channel, so success emitted nothing and an empty directory was a success. Silent-green, not silent-red.**
- **THAT IS THE SECOND LEDGER HEADLINE TO FAIL VERIFICATION TONIGHT**, after the filming gate. The independent
  headline audit already running is now the more important job, and it has a second data point.
- **The fix addressed the class.** Every existing check was *"look for a known defect and complain"* — a shape with
  one blind spot: **an empty directory presents no defect to any of them, so all pass and their silence composes into
  a green.** A new precondition stage enumerates what a case must **contain** and requires each positively. **The
  required list was chosen empirically, not by taste** — checked against all 78 surviving corpus cases; 76 carry
  every element and the 2 that don't were never cases.
- **Two more greens-from-nothing closed in the same sweep**: a header check that fired identically whether it parsed
  40 files or 0, and a patch check reporting *"checked against mesh (0 patches)"* having read no patch names. **No
  existing check was relaxed.**
- **The decisive control is a discriminating pair**, not a refusal: the wrapper directory goes red while **its real
  subcase goes green at 18 checks** — proving the gate discriminates rather than blanket-refuses. Across 78 corpus
  directories the verdict changed on exactly **2**, both genuine non-cases.
- **End-to-end verified through the launcher**: refusals launch nothing and write **0** registry files, with the
  registry redirected to scratch and **all 146 records intact and unmodified.**
- **Found while not looking: 4 zero-byte completion records** whose logs hold 3.6–6.5 MB of real solver output — the
  collector wrote **nothing**. Same *"absence reads as nothing happened"* family. Queued as its own rung.

### 2026-08-11 — the hump's adjoint boundary is uncharacterised, not diagnosed, and 8 claim sites are corrected

**Both findings confirmed against the artifacts before a word was changed.**

- **A6's log contains `ConvergedReason` ZERO times.** 2,279 lines ending mid-run at iteration 900. `rc=1` with **no
  allocation failure, no OOM kill, no PETSc memory error anywhere** — **the non-zero exit was the container stop, not
  a KSP verdict.** Memory available at the end: 1.6 GB. So neither half of *"rate, not singularity"* was measured.
- **The claimed hump gradient really never existed.** The FD-verified 3-cell gradient belongs to CBFS — the cells sit
  under a heading that says so. The hump has 51,626 DVs, **no gradient line in its log at all**, and its FD harness
  **exists but has never been executed.** The reach document's hump line was **a second count of the CBFS gradient
  under the wrong case name** — and CBFS is already listed two clauses earlier in the same sentence.
- **It added an argument the audit did not make**, and it is the strongest one: **the sub-LU repair cannot license
  "not singularity" at all**, because what it repaired is a singular ASM sub-block *incomplete* factorisation while
  GMRES applies the matrix-free operator — the operator/PC mismatch our own record documents on the other case.
- **8 claim sites corrected across 6 files, plus 2 outward-facing PDFs rebuilt**, with `pdftotext` confirming the only
  surviving instances of the phrase are inside explicit withdrawal quotes. Dated records got corrections **beside**
  them; the one claim that was **wrong when written rather than overtaken** was corrected in the body **with the
  original sentence quoted in full**, so the record of the claim survives.
- **My own file was the outstanding one.** `docs/PRODUCT_LIST.md:22` stated the withdrawn claim as **present-tense
  fact** while a later entry in the same file carried the correction — **the file contradicted itself.** Fixed above.
- **Search denominator, stated properly: 4,940 candidates enumerated, 4,938 scanned, 2 skipped**, across the repo and
  the 66 GB run archive, **with whitespace collapsed before matching.** That is what caught the two report sites,
  which phrase it as "Krylov convergence rate against a memory envelope" **without the word the natural line-grep
  would have used.** Plus a proximity sweep (38 files, all read), a wrap-proof token pass over 1,087 files, and every
  PDF in the tree checked via `pdftotext`.
- **FOUND WHILE NOT LOOKING, and one is an inversion worth keeping:** the warm-start audit **already contained the
  reproduction finding without naming it** — its rationale *"single-run record; no rerun existed to contaminate"* is
  the same fact as **"never reproduced," read as a virtue.** Recorded as **L-71**.
- Also: **`A6` names two different objects in this archive** — the hump sub-LU run in one table, a CRM wingbody case
  in another. Same token, same subsystem, different things; a live collision hazard for exactly this kind of audit,
  and not renamed because citations across many documents would break.
- And **a cost basis stale by ~7×**: a proposal prices one hump gradient attempt at "about 8 core minutes"; A6
  measured **54.60**. Correctly left alone — re-basing a dated pre-registration destroys what was budgeted on what
  evidence.
- **The instrument for stating an uncharacterised boundary already existed in this lab four days after the hump run**
  — another record says plainly *"NOT EVALUABLE ON THIS HOST — no KSP reason code was obtainable"* — **and was never
  applied to the hump.**

### 2026-08-11 — both sibling gates closed, three more found, and one gate fails slow on exactly the wrong morning

- **Both defects reproduced exactly** before either was touched — a typo'd act name printed its reach and exited 0 on
  one; the other printed three zeros and exited 0. **Neither was a false alarm**, which after tonight is worth saying.
- **Both now fail closed**: RED, exit 2, **no verdict line at all** on an unresolved name, an absent root, or a source
  that delivered nothing. Reach statements now carry per-source denominators, the **8 of 25 act directories with no
  transcript are named as unread**, and the replay verifier resolves **every** act *before any act runs*, so a typo
  costs nothing instead of landing after twelve replays. **Production output is byte-identical** on the counts that
  mattered — 36 surfaces, 16 flagged.
- **A DELIBERATE DIVERGENCE, flagged for ruling rather than hidden — and I upheld it.** On the discretion gate, hits
  do **not** change the exit code. The rules **promise** false positives, production legitimately flags 16, and
  **a permanently non-zero exit is one nobody reads** — which is how a printed reach came to be ignored in the first
  place. Same shape as **L-70**. *Failing closed on "I could not scan" and staying quiet on "I scanned and found
  things a human must judge" are different axes*, and separating them is correct.
- **THE ITEM THAT MATTERS FOR THE SHOOT: the replay verifier fails SLOW when the control room is down** — 240 × 2 s
  per act, up to 8 minutes each and **~1.7 hours for the default sweep** before anyone learns the box is not
  answering. **A filming morning is exactly when that sweep gets run and exactly when 1.7 hours of silence is
  unaffordable.** Judged out of class and left; I have ordered the reachability preflight, fail-fast with the reason.
- **THREE MORE SIBLINGS, verified by reading the code rather than relayed** — and the first is load-bearing:
  `check_convergence_sweep.py` **gates a closure claim and has no non-zero return anywhere in the file**, so a sweep
  full of non-converged results exits 0 exactly like a clean one. **The findings never reach the exit code at all.**
  Then a missing key yielding `None` → exit 0, hiding a printed warning from any caller that gates on status; and an
  empty corpus exiting 0 **even under `--strict`.** Dispatched.
- **Exit-code consumers checked before changing exit semantics: 15 files mention either script across a 20,552-file
  denominator, and none consumes an exit code** — no CI, no hooks, no Makefile, no generic runner. **Nothing starts
  failing.** That check is what made the change safe, and it was done first.
- **Ten controls, five per gate, both directions**, including planted real defects that fired. The two that could not
  be run against production were run against a stub, **because driving the real control room rewrites the act's
  transcript** — a constraint respected rather than worked around.
- **FOUND WHILE NOT LOOKING, and it is tonight's theme in one line:** an act **cleared this gate with three zeros**
  while the docket **already recorded it as unverifiable**. *The docket knew; the instrument said otherwise.* Also:
  the default sweep's own reach was never stated — it runs 13 of 14 registered acts, with one deliberately excluded,
  and never said so.

### 2026-08-11 — exactly one resource-dependent test in 1300, demonstrated over 11,700 scored outcomes

**And it opens by correcting me: the sweep never died.** I reported it "died on a connection error at its first tool
call" and resumed it. **It had already finished** — the failure notice carried the *first* line of its response
rather than its last, so completed work looked like work that never started. **A failed-status notification is not
evidence that nothing was done**, and I restarted on that assumption. It declined to redo the work and addressed only
the one genuinely new instruction, which is the right call.

- **Enumeration transitive BY CONSTRUCTION, not lexical** — wrappers count resource calls **per test function at any
  depth**. That matters because the one real finding is **four hops from its assertion and names neither disk nor
  memory.** A lexical sweep would have missed it, exactly as the confirmed defect was missed.
- **Frame: 1300 test functions defined, 1300 executed and scored — no gap.** And it **corrected its own earlier
  number** (1309 defined / 9 unscored) on discovering that figure compared a working-tree grep against an
  archive-tree run.
- **CLASSIFICATION: verdict-changing 1 · resource-reading-but-pinned 20 · reads-but-insensitive 74.** The one is a
  batch-ledger test whose flip point brackets to **0.1 GB on each axis independently** — green at 20.1 GB disk, red at
  19.9; green at 2.1 GB memory, red at 1.9 — and **both thresholds are the workflow's own latching guard floors**,
  with the livelock incident that guard exists for recorded in the same file.
- **DEMONSTRATED, NOT REASONED: nine full-suite runs, 11,700 scored outcomes, exactly one difference** — and capacity
  was moved **94×**. **The positive control was run first**: the pre-fix assertion is GREEN at forced 3 cores and RED
  at 96 against the same source, **so the zero-difference result means something.** Two tests no in-process wrapper
  can see were forced with a shim on `PATH`, crossing a boundary patching cannot.
- **It conceded my criticism and the fix was load-bearing.** Its first four runs carried endpoint load only; re-run
  under a 20-second sampler, load ranged **10.25 → 1.42 → 13.13**, including a **3× swing inside a single unforced
  run** whose capacity therefore moved mid-execution — **and it still agreed test-for-test** with runs pinned to 1
  slot and to 94.
- **REPRODUCIBILITY ANSWER: YES — measured, not argued.** The suite's colour does not depend on concurrent load.
- **It ran the repair rather than proposing it**, and the repair **adds** an assertion instead of weakening one:
  assert a value the function already returns and the test already discards.
- **N-7, and it lands on our own record: a suite total was entered permanently from an unreproducible tree.** A
  commit records "Suite 1309 passed"; the swept commit defines **1300**, and the nine were **uncommitted** tests.
  Annotated above. **A suite count is true of a commit, not of a moment.**
- **N-1, subtle and worth keeping: a test with an invariant verdict but branch coverage chosen by the neighbours** —
  only one narration arm ever executes on a given box. Always green, never fully exercised.
- **Limits stated without prompting**: 31 test functions now exist that were never swept because they postdate the
  swept commit, and **HEAD moved eight commits during the sweep.** *"That is the standing cost of measuring a
  repository eight agents are committing to."* Memory pressure was forced by substitution, not exhaustion — starving
  this box would have taken down the neighbours.

### 2026-08-11 — the ledger headline audit: 24 sound, 9 overstated, 8 falsified, and its method survives

**The verdict I asked for and got: accurate, not low.** Of 41 headline-grade claims, **24 SOUND · 9
TRUE-BUT-HEADLINE-OVERSTATES · 8 FALSIFIED.** The ledger's *method* survives; **its titles and round numbers do not
hold as well as its bodies** — and **seven of the eight falsifications are a count or an unstated frame that one
command would have settled**, in a document whose own subject is instruments that report clean without saying what
they counted.

- **THE FRAME IS THE MODEL FOR HOW TO MEASURE A MOVING REPO:** the tree moved **five times during a 20-minute audit**,
  and one of the audited scripts **acquired a 190-line fix mid-verification.** Every behavioural claim was therefore
  reproduced **from pinned source** (`git show <sha>:<path>`), never the worktree. That is the discipline L-72 asks
  for, applied without being told.
- **The control-contamination hunt came back NEGATIVE, and it looked hard.** Four repointed copies are still on disk;
  **all four belong to the single already-withdrawn finding.** No other claim traces to an edited copy. And it found
  the counter-example that shows the fix: a scratch copy that is **byte-identical to production and whose *filename*
  says what it is** — self-labelling controls, exactly L-68's remedy.
- **But a SECOND mechanism is confirmed**, as I suspected: **stale claims never re-checked before being ranked**, plus
  one claim **inherited from an earlier pass whose cited source does not record what it is cited for.** That is L-60
  reproduced inside a document written to catch such things.
- **CORRECTIONS TO MY OWN PUBLISHED FIGURES, made above.** Two instruments were classed *demonstrated* on bases that
  are **reach statements, not firings** — so the classification becomes **28 · 27 · 11**, and *"never been shown to
  fire" rises from 38% to 41%.* **The correction makes the ledger's central finding stronger, not weaker.** Also
  ~~32~~ **31** of 34 checks lack a test — **the ledger names the third itself.**
- **AND ONE LANDS ON A CLAIM I HAVE CARRIED FOR TWO WEEKS.** We recorded `is_idle.sh` as the **root cause** of the box
  powering off mid-campaign. The code defect is real and current — six work classes missing, verified line by line.
  The power-offs are real — Katie saw them three times. **But no wiring was found from that script to anything that
  halts the machine, and the record cited for the cost states only the script's purpose and status: no power-off, no
  date.** **A real defect and a real symptom do not make a cause.** Downgraded to *candidate mechanism*.
- **The audit found the same claim propagating one document further along** — into this file in compressed form,
  which is L-68's path exactly, and it caught it while looking at something else.
- **The ledger's own PASS/WARN/FAIL tally is unfalsifiable by construction**, having been taken over a tree never
  committed — which is why two of its arithmetic errors were catchable *only* by internal consistency.
- **The closest thing to a second headline/body split**, and it is instructive: a claim that an instrument *"is not
  found by any verdict-word search of its source"* — a plain grep returns **7 lines**. What actually misses it is
  **one specific axis**, and the headline generalised from that axis to all searches.
- **Two frames in adjacent columns of one table, neither declared** — a unique-file column counted over 142 files
  beside a hits column counted over 534.
- **SOUND and worth naming**, because a good verdict is only as useful as its confirmations: the empty-directory
  finding **reproduced exactly from pinned source**, and its adverb was *precise* — failures really are audible; only
  the PASS was silent. **34 blind-spot entries, all carrying a caveat, exactly 4 printed** — exact to the digit. The
  test-count column **9 of 9 exact.** All 13 known-answer convergence cases re-pass. The four enumeration axes are
  **internally exact** — their union is *precisely* the reported 296.

### 2026-08-11 — V16 graded PASS WITH EXCEPTIONS by an independent grader, and the exceptions are load-bearing

**The grade is honest and the guard is real. It is also narrower than its own verdict line admits.**

- **Claim 1 (board is parsed, not transcribed) — VERIFIED, by a harder test than the author's**: the grader rewrote
  **only the two rank digits in the real benchmark README** and the same probe sentence went 0 faults → 1. No board
  literal exists in the code.
- **BUT L-66's test says the corpus contains ZERO evidence for it.** The same machinery with a **hand-typed board
  disagrees on 0 of 974 files.** The permutation test is the *only* evidence that parsing matters — which is exactly
  what L-66 predicted and exactly why the permutation test had to exist. **The corpus evidences precision, never
  recall.**
- **THE NUMBER THAT MATTERS: 89% miss rate on invented phrasings** (40 of 45; 88% excluding declared blind spots).
  The five it caught all happen to contain its own patterns. **Entire families missed**: *placed / finished / came /
  took third*, *ranked third*, *third overall*, *No. 3*, table and CSV rows, *top the board* — **the last of which
  the older digit-anchored guard explicitly admits to missing.**
- **AND THE BLIND-SPOT LIST IS INCOMPLETE IN THE DIRECTION THAT MATTERS.** Its reach line omits the adjudication
  window, use/mention, a size cap, board positions past fifth, and — most seriously — *"placements phrased outside
  the two patterns"*, **an admission the guard it supersedes still makes.** The replacement's stated reach is **less
  honest than its predecessor's**, which is the precise failure L-61 exists to prevent.
- **A LIVE INSTANCE IT CANNOT SEE, on a shipping report's source**: a placement pinned on a named entrant, **wrapped
  across a line break**, in the same sentence family as the defect that opened the rung. **It is correct — by luck.**
  The guard would not have caught it had it been wrong.
- **Three failure modes worse than a miss**, all found by attacking the parser: an unbalanced regex metacharacter in a
  surname **raises an exception and crashes the entire audit** instead of reporting OFF; **a second numbered table
  anywhere in the README silently corrupts the ranks**; and **a shared first-author surname silently drops an entrant
  and then faults correct prose.** Also, the ordinal vocabulary is a **hard-coded 1–5 constant not derived from the
  parsed board**, so a longer board is unmatched past fifth — a literal surviving inside the thing built to remove
  literals.
- **The false-positive result is BETTER than claimed and its denominator is not justified**: re-derived over 974
  files, **503 placement expressions, exactly 2 faults**, both a record quoting the defects at correct severity. But
  **no record states how the original 111-file corpus was selected**, and nearby reasonable filters give different
  numbers.
- **Counts corrected**: the diff adds **22** tests, not 21; **21** fail against HEAD, not 20.
- **Claim 2's justification retracted**: on the *real* pre-fix instance, whole-text and line-bounded both return 1.
  The author found this and published it against its own interest — **but left the superseded claim standing in the
  shipped code comment and in the rung definition.**
- **Also found: a test that silently skips a missing file and can report a pass having asserted nothing.**
- **VERIFIED SOUND**: fires on all three original defects **on real git bytes rather than fixtures**, plus a fourth
  instance the claim never enumerated; the severity scoping errs conservative; and the 15→16 rung amendment is
  **accurate and complete** — exactly three live statements changed, with the one residual being a historical
  quotation correctly left alone.

**LADDER STATUS: NOT GREEN.** V16 is open with exceptions; V15 round 5 has not run and cannot until V16 closes.

### 2026-08-11 — the overwrite detector works, my specification of it was wrong, and it found six undisclosed rewrites

**MY ERROR FIRST: the detector as I briefed it does not work, and the agent had to correct me.** I passed on the
formulation *"a rewrite leaves a directory older than the files inside it"* without testing it. **An APPENDED file
leaves an identical signature** — appending creates no directory entry either. Implemented as I specified, it
produced **213 hits repo-wide**, mostly innocent probe directories. **Only a peer control separates a rewrite from an
append**, and that is now the tool's central mechanism, with my failed reasoning recorded inside it.

- **Attribution verified independently before anything was marked.** The contaminated directory is **the only one of
  26 in the case** where the directory is older than its contents; the duplicate's own function-object record shows
  **exactly one write event**; the stored gradient at that time is the duplicate's value, not the survivor's; and the
  survivor's untouched data file disagrees with the field **at that time and nowhere else.** Four independent lines.
- **Marked in the GENERATOR, not hand-patched into the output** — the result JSON was **re-derived with every
  pre-existing key bit-identical**, the only change an added contamination block. It now prints provenance at run
  time and carries a **register-drift guard, tested both directions**, so a stale note cannot emit silently.
- **Two placement decisions worth keeping**: it wrote **nothing inside the contaminated directory**, because doing so
  would update the mtime and **destroy the evidence**; and the marker travels with the archive rather than the repo,
  since the archive is gitignored.
- **SWEEP: 82 confirmed rewrites across 50,817 directories.** Filtered to solver output at t>0, the confirmed set is
  **8 directories**: the one we knew about, **six in an F7 case — undisclosed**, and one in a W4 case.
- **THE UNDISCLOSED ONE IS A DATA-INTEGRITY FINDING:** an F7 case **holds two runs' fields interleaved under one time
  ladder** — a serial run, then a decompose/parallel/reconstruct sequence six minutes later that overwrote the five
  coinciding times and added new ones. Sequential rather than a collision, so nothing raced — but **anyone reading
  that series reads a mixture**, and it is documented nowhere.
- **THE LIMITATION IT FOUND IN ITSELF IS THE BEST PART: the peer control fails when contamination is widespread.**
  Two cases have **16 of 17 time directories rewritten**, which destroys their own control, so **96 real rewrites
  drop to "unresolved."** *The instrument is least sensitive exactly where the damage is worst.* Stated in its
  verdict line, and it **softened an over-claiming message** of its own accord.
- **Three limits stated without prompting**: mtimes prove two writes but **cannot prove intent**; **any later touch,
  copy or checkout erases the signature permanently** and git records no mtimes at all, so the 50,817 denominator
  bounds *what is still visible, not what happened*; and **a clean sweep is not proof of no duplicate**, because a
  duplicate that never reached a write leaves no artifact anywhere.
- **`test_exec_bits` is green (15 passed) and it was exactly the L-59 shape** — the local file carried 755 while HEAD
  carried 644. Fixed with a one-invocation override and **verified as `100755` in the tree at HEAD, not the index.**
  The test itself was not touched.

### 2026-08-11 — the S6 parser gap was 38%, not 6 cases, and the primary prediction was never scored

**THE FINDING THAT MATTERS MOST, and it corrects a headline I wrote: the primary prediction was never scored, and no
document said so.** The pre-registration's *primary* was a post-wiring fire rate on `HeadEngineer` runs. **That run
cost zero core-minutes — the document says so itself — so no post-wiring production run existed.** The campaign
family, offered in the same section as an **analogue**, was scored in its place. Two records then hardened the
analogue into *"S6 fires on production for the first time"* and *"135/135 on production."* **Both corrected above.
The primary prediction is still open.**

- **THE PARSER GAP WAS 38%, NOT 6.** **85 of 222 gated logs** had at least one control the parser could not resolve;
  the six were only the ones where *nothing* resolved. **The other 79 stayed classed as gated on a partial reading**,
  so the defect was invisible in the class counts. After repair: **3**.
- **And it ran in both directions** — regex control keys *and* regex solver keys. Every one of the six had **both
  numbers present in its own file**; none was a genuine no-declaration case.
- **The resolution rule was READ FROM OPENFOAM'S SOURCE, not chosen**: literal keys beat regex regardless of
  declaration order; among several matching patterns the **last-declared wins**; matching is a **full** match, so an
  alternation does not match a component name. Cited to file and line. *"It is OpenFOAM's rule, not a choice of
  mine."*
- **The structural change was forced by the data**: reachability is now decided **per field**, not by comparing
  declared keys — because one case's single control names two fields whose tolerances come from two *different*
  solver entries. **The keys can never meet; the fields do.** Candidate names come only from what the case's own
  dictionaries name; nothing is invented.
- **RE-SCORED: fail-open 6 → 0. Gated 81 → 87 (41 fires, 47%). Families 51% / 94% / 20%.** No case crosses the
  sentinel boundary; **135 of 135 holds**; 13 logs get a different arming target, 11 needed their fire label
  recomputed and **none changed**. Campaign 51% sits inside the pre-registered 48% ±15pp — **no refutation condition
  fires.**
- **AND THE REPAIRED RELATION NOW REPRODUCES THE BARE-`1e-15` PARTITION EXACTLY** — the very figures a standard had
  already published. **Before the repair the two differed by precisely the six fail-opens.** That is L-63/L-66's
  point demonstrated rather than argued: on this archive the principled relation and the literal are **the same
  predicate**, and the only reason they had ever differed was our own parser bug.
- **"SCORED WITH THE SHIPPED HELPERS" CAUGHT NOTHING HERE AND COULD NOT HAVE** — it checks that two implementations
  agree, and **a defect both share is invisible to it.** The replay script that built the corpus **drops quoted keys
  the same way**, so on exactly these cases the two agreed *by both being blind*. Recorded as **L-74**. That script
  is **still unrepaired**; fixing it means regenerating a published artifact (~6 min replay).
- **The retrospective row was three rows, not one** — every row was checked and the finding **generalises beyond what
  the re-score named.** Labelled in place; the table and its "met"s untouched; **zero deletions** in all three edits.
- **Sweep denominator: 20,552 tracked → 19,091 readable → 9,574 containing the literal → 366 topical → 19 hand-
  screened**, matched with the whole file as one record so wrapping cannot hide a phrase, **and independently re-run
  in Python over normalised text — the two methods agreed on 17 and 18 files, union 19.** Two methods, both stated.
- **Found while not looking, and it is a case defect not a tool defect:** those cases **declare a `residualControl`
  entry OpenFOAM cannot apply** — the key names tensor components while the solver dictionary is keyed by the tensor,
  so **the SIMPLE convergence check silently never tests the Reynolds stresses in those runs.**
- **Also: two logs were scored against a dictionary written AFTER them.** The archived log predates its own case
  dictionary, so the replay armed from targets that run never used. **The production gate is protected because it
  reads the case it is about to stage; the replay is not.**
- Limits stated: the multiple-pattern rule is **exercised only by unit test, not by data**; whether the original
  scoring script shared the defect **cannot be established** because it was never committed; and transient-style
  nested `residualControl` blocks are **still not parsed at all**, so S6 cannot arm on a transient case even in
  principle.

### 2026-08-11 — the three remaining fail-open gates are closed, and the slow failure is 1.81 hours → 0.01 seconds

- **The slow failure was measured, not estimated**: the pre-fix sweep pointed at a closed port was **still polling act
  1 of 13 when a 120-second bound cut it off, having printed nothing** — timed at 2.091 s per poll, **8.4 minutes per
  act and 1.81 hours across the sweep before the first word.** After: a single 8-second probe, **RED and exit 2 in
  0.01 s.** The per-act poll stays, because a room that dies during act 7 is still its job.
- **All three siblings reproduced and fixed.** The worst printed **152 logs, 73 NOT_CONVERGED, 56 CANNOT_TELL — and
  exited 0**, with no non-zero return anywhere in the file.
- **THE JUDGEMENT CALL IS THE GOOD PART, and it applied my own ruling back to itself.** A bare failure exit would have
  made that gate **permanently non-zero at 129 of 152** — L-70 exactly. So it lifted the register pattern from an
  existing tool *along with its reasoning*: 129 dated basenames, **blessing nothing**, making the gap countable and
  stopping it growing. **A new unconverged log fails; so does a registered log that gets worse.** Healed and vanished
  logs are reported as drift and never reddened, **so the register cannot rot into an amnesty.**
- **It keyed the register on basenames rather than parsing a prose document** — *"no gate should depend on parsing
  English."*
- **Consumers re-searched per script rather than carried over** — 7 / 7 / 13 files. **The only executable consumer
  anywhere is one test module, 14 tests green before and after.** Production exits unchanged.
- **It introduced a defect and caught it in its own control**: the drift report dumped all 129 names on a partial
  sweep, **burying the finding**. Fixed before commit — and it noted that this is **the same drowning-in-its-own-
  output failure another script's comment already warns about**, which *"reappeared the moment I wrote new reporting
  code."*
- **`onera-m6` is now recorded at the instrument**, with the reason. It does **not** make the act verifiable — the
  name still fails to resolve and still takes the run RED. *"It replaces a shrug with a reason. Registering a prompt
  would have been inventing a verification claim."*

### 2026-08-11 — our `grep -r` has been silently skipping ignored files, and I confirmed it with a planted control

**This qualifies sweep denominators across tonight and earlier, including several I published.**

- **`grep` in this environment is a shell function**, not `/usr/bin/grep` — it execs `ugrep … --ignore-files …`, and
  **`--ignore-files` honours `.gitignore`.** I verified it myself: one token written to a visible file and an ignored
  one, **`grep -rl` returned only the visible one; `find` + real grep returned both.**
- **This lab gitignores its large case archives**, so a repo-wide `grep -r` **cannot see the run outputs at all** —
  including the archive carrying tonight's contaminated snapshot. Every *"swept N files, found nothing"* built on
  `grep -r` is a statement about **ignore-permitted files**, and no document said so.
- **The recursion is the finding**, in the auditor's words: *"this is the ledger's own central finding — a verdict
  that does not state what it swept — recurring in the tool the auditors used to check the instruments."*
- **What is NOT affected**: every count ruled on from `git ls-files` (same reach by construction) or `find` (no
  filter) — which is exactly why one discrepancy was decidable and another was not. **The audit's verdicts stand.**
- **It killed its own running sweep rather than let a fourth incommensurable number land** and tempt it into
  converting the number into a verdict. That is the right instinct: *a number whose frame you cannot state is worse
  than no number.* Recorded as **L-75**, and written to memory so it does not have to be rediscovered.
- **The headline audit closes at 24 SOUND · 9 OVERSTATES · 9 FALSIFIED of 42.** The ninth: *"two 906 MB tarballs left
  unopened"* — there are two, of **544 MB and 362 MB**, and **906 MB is their sum written as though it were each
  one's size.** So the unexamined residual is **906 MB total, not 1.8 GB** — the substance moves, not just the
  wording. **That is the fourth instance tonight of the same wrong-frame defect** in that one document.
- **It also caught itself**: an interim count was **a partial read of a file still being written**, its wait
  condition firing on first bytes rather than completion. It noticed only because the number collided with an
  unrelated one, and it never reached the record. **The same defect the document it was auditing has.**

### 2026-08-11 — V16's six exceptions are closed, recall measured twice independently, and one family was taken back out

- **The blind-spot statement was fixed FIRST, as ordered, and structurally.** It now **leads with the largest blind
  spot** — *any placement phrased outside the patterns* — adds the adjudication window, use/mention, the size cap and
  positions past the board, and ends **"GREEN HERE IS NOT COVERAGE."** Two tests hold it, and the second is the one
  that matters: **whatever the digit-anchored sibling admits about pattern reach, this guard must admit too.** The
  guard can no longer regress to being less honest than the thing it replaced.
- **RECALL WAS MEASURED TWICE, INDEPENDENTLY.** It built **its own 46 held-out sentences without seeing the grader's**
  and got **80% missed** — *corroboration of the grader's 89%, not a repetition of it.* Then nine families were added:
  **80% → 30% missed, with precision still exactly zero.**
- **AND ONE FAMILY WAS ADDED, MEASURED, AND TAKEN BACK OUT.** `No. N` fired on a **journal issue number in a
  bibliography beside a matching citation**. *Its removal is now a test.* Medals, roman numerals, other languages and
  table rows are deliberately excluded — **also as tests**, so the exclusions are decisions rather than gaps.
- **The three parser failures were taken before any new patterns**, each reproduced on a synthetic fixture first. The
  contract changed from *board or None* to **(board, head) or (None, reason)**, so **the reason reaches the verdict**:
  a metacharacter surname no longer raises and one bad surface can no longer end the audit; a second numbered table
  now forces **OFF with what it read**; a shared surname forces **OFF with both rows named** instead of dropping an
  entrant and faulting correct prose. **A fourth was found in passing** — a particle surname parsed to its particle.
- **The literal inside the thing built to remove literals is gone**: the ordinal vocabulary derives from the parsed
  board's length **plus a margin — and the margin is the point. An ordinal naming a position the board does not have
  is now its own fault, and says so.**
- **The retraction's replacement is real, not a patch.** The shipping `.tex` sentence **breaks between the ordinal and
  its rank word** — whole-text sees one placement, a line reader sees none. **That is the justification the retracted
  one wasn't**, and it is under test.
- **THE SENTENCE I ASKED TO BE HANDLED, handled exactly right:** verified **against the parsed board rather than
  against the grade** — the entrant really is rank 2, so **the text was left untouched.** But it is no longer unseen:
  the family that reads it **exists because of it.** *"It was correct by luck; it is now correct and checked."*
- **Two things it did to itself and reported, which are the useful part.** The widened guard **caught its own new test
  fixtures within a minute** — twelve faults, because it had written the defective sentences out in full **in the very
  file documenting why one must not**; they are assembled at runtime now. And an over-broad exclusion had eaten *the
  exact sentence the adjudication clause needed.*
- **It struck the 111/421/63 corpus from the ladder and from this file**: the *rate* survived the grader's wider
  re-derivation, but **the corpus had no selection method written down anywhere.** The check now prints its
  denominator **and its selection rule** in the verdict — L-75's lesson applied without being told.
- Counts corrected in the ladder from its own isolated worktree: **22 test methods added, 21 failing at HEAD.**
  Severity scoping now **declares itself a basename match, not a provenance check.** Scan time **3m04s → 1m10s**.
- **State: guard tests 57 passed, suite 1362 passed** — including the two failures that were live earlier tonight,
  both another agent's and both fixed by them. Every travelling surface agrees with the board; the only two faults
  are the **declared use/mention quotations** in another agent's file, correctly untouched.
- **IT DID NOT RE-GRADE ITSELF.** *"A15 applies to a fix round exactly as it applies to a build."* The re-grade is
  owed to the original grader and is dispatched.

### Decision requests for Katie (standing)

**COMPUTE AUTHORISATION REQUESTED — 40 core-min to convert an assumed boundary into a measured one.**
The hump work is priced at **365 core-min total (M1–M6)**, but it should **not** be bought as a block. My
recommendation is to buy **M1 + M2 only, at 40 core-min**, because they are the two that can make the rest
unnecessary:
- **M1 (25 core-min, OFFLINE)** — dump the hump preconditioner and RHS and run the **existing** offline harness for
  exact LU and conditioning statistics. **This decides singular vs ill-conditioned vs merely slow without a long
  solve at all**, using a tool already written and already applied to the other case.
- **M2 (15 core-min)** — **the negative control that has never been run on this case in eleven attempts.** Returns at
  iteration 0.
**If M1 returns a singular or catastrophically ill-conditioned operator, the two expensive items (M4 at 100 and M5 at
150) should not be bought at all** — and M5 is flagged as carrying an *unmeasured multiplier*, so 150 is its 1×
figure. Nothing has been run; the list is priced and parked.

1. File the prepared upstream `mdolab/idwarp#57` comment / bug report? (`UPSTREAM_BUG_REPORT_mesh_warpDeriv.md` ready.)
2. Closure-challenge submission: author names, reference URL, approval to email the steward (incl. the two ambiguity questions).
3. Result-priority decision sheet D0–D7; escalation free-spend threshold (P-7.1); AWS read-only role for P-6.1.
