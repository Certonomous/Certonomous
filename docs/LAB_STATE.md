# LAB_STATE — the resume board

**This file is the only handoff channel between sessions.**

Agent teams do not survive a compaction, a session switch or a crashed terminal.
Nothing about a live agent is persisted anywhere else: not its brief, not what it
had read, not what it was part-way through. The session scratchpad is **not** a
handoff channel — it was wiped three times in one day and only the things already
in the repository survived (L-186). A repository document never cites a scratch
path.

So: **what is not on this board is lost.** Each supervisor owns its own section
and updates it **at every commit and at every verdict** — not at the end of a
turn, because the end of a turn may never arrive.

**How to read it.**

- Anything marked **VERIFY** was not confirmed by the writer at the time of
  writing. Treat it as a lead, not a fact.
- The board can be stale. `/form-teams` and `/lab-state` both take a live reading
  beside it (`git log`, `ps aux`, `readlink /proc/<pid>/cwd`) and **the reading
  wins**. A correction belongs to the supervisor who owns the section, not to
  whoever noticed.
- Every team section carries a **`**Section last written:**` stamp**. `scripts/check_harness.py`
  flags a section older than its own territory — the team committed and did not
  update its board, which is exactly the L-226 failure.
- Verdict vocabulary only: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
  BLOCKED / PENDING.**

**Board populated 2026-08-22T18:05Z at HEAD `a5605f54` by the harness build.** It
was assembled from git log, the campaign index files, the charter records and a
live process reading. Every section below is a first fill by a third party, not by
the team that owns it; each supervisor should correct its own section on its first
commit. **HEAD moved six times during the two hours this board was assembled** —
re-derive rather than trust the shas below.

---

## CHIEF — standing directives in force

**The chief is the GLOBAL SUPERVISOR and never solves.** It routes and relays.
First action every session: read this board, run `/form-teams`, report the roster
to Sanaa. Sends are reserved to Sanaa.

| # | Directive | Source | State |
|---|---|---|---|
| **THERMAL BUILDUP DIRECTIVE (H-1 … H-7)** | DC-cooling is the destination; capacity priority behind only R4's CPU-minutes | Sanaa, recorded verbatim 2026-08-22, `docs/campaigns/T-family/THERMAL_BUILDUP_DIRECTIVE.md` | **IN FORCE**, ledger live in that file |
| H-1 | Vogel & Eaton (1985) unblocks T3's gate rows; confirm T5's primary status | same | (a) **NOT on disk** — repo-wide search, zero hits. (b) T5 primary **HELD**, sha256 re-verified |
| H-2 | DC spine order inside the T-family: **T3 → T5 → T8 → T12 → K2 rack row**; everything else interleaves | same | **IN FORCE**; index reordered, old order retained as superseded |
| H-3 | T10a follow-through, two arms: (a) ceiling refinement, (b) view-factor quadrature characterisation → upstream candidate #4 | same | both **PENDING**, lanes dispatched, preregs not yet written |
| H-4 | T9a 2.4 mK interface miss: diagnosis arm, **one change per run** | same | **EXECUTED** — T9a-D REPORTED 2026-08-22, prereg + results on disk (D454, L-227); cause is the interface scheme |
| H-5 | Tier order after the spine: T4, T6, T7, T2, T9b/c, T10b, T11 | same | queued behind the spine; nothing started ahead of it |
| H-6 | Every thermal gate feeds the DC certificate spec as it passes | same | `docs/product/DC_CERTIFICATE_TEMPLATE.md` created |
| H-7 | Two institutionalizations: bands-vs-corrections caveat into the charters verbatim; the libs lesson as law | same | **BOTH DONE** — VERIFICATION_CHARTER §2e (v1.10), CLOSURE_MODELLING §22.4 (v1.1.2); `scripts/foam_libs.py` + `lint_foam_libs.py` |
| **GPU-blocked reproductions now unblocked for pre-registration** | Closure supervisor to pre-register DPM, Bae, Lozano-Durán, Beck (and Ling2016 TBNN GPU training) with GPU-hour cost bases; nothing launches before Sanaa signs each | chief, 2026-08-22 | **DISPATCHED** |
| **R3 = SpaRTA** | The closure line rebuilds on SpaRTA-class, Sanaa's pick from the R2 shortlist | Sanaa 2026-08-21, verbatim *"R3: Sparta"*, appended to `docs/closure/R2_SHORTLIST_MEMO.md` | **DECIDED** |
| **R4 approved** | Sanaa said *"R4 approved"* in the same message | same | **APPROVED**; R4 build **OPEN, no verdict** |
| **R4's CPU-minutes have first call on capacity** | named in the thermal directive's own header | Sanaa 2026-08-22 | **IN FORCE** |
| **SUBMISSIONS PARKED** | Nothing is sent, filed, uploaded, registered or posted anywhere. Sending is Sanaa's alone | Katie 2026-08-07; `GOALS_AND_PROPOSALS` §8, `CLOSURE_MODELLING` §19, `DAFOAM` §10 | **IN FORCE**, indefinitely |
| **Blanket compute approval** | Runs above the $25 pre-authorisation are blanket-approved, **and are still costed in their pre-registration** | Sanaa 2026-08-21, *"all the teams have my approval for everything"* — **owner-stated, chief's session record** | **IN FORCE** |
| **GPU quota GRANTED, no GPU attached** | AWS raised "All G and VT instances" in us-east-2 to 8 (vCPUs; one g6.2xlarge/g5.2xlarge or two xlarge). No GPU on this box. `BLOCKED-GPU` retired as a standing verdict. **GPU spend sits OUTSIDE the 2026-08-21 CPU blanket**: each GPU run needs a console-priced GPU-hour cost basis and Sanaa's per-item sign-off. Case-number link (178725840000468) is an inference, unconfirmed | AWS message pasted by Sanaa 2026-08-22, recorded verbatim in `docs/GPU_CAPABILITY_STATE.md`; rule 12 amended at e0cf8f0c | **IN FORCE** |

**Lab-wide live compute:** 12 single-core solvers, all `buoyantBoussinesqSimpleFoam`,
all owned by heat-transfer. At $0.0513/core-h that is **~$0.62/h** (c7a.4xlarge at $0.0513/core-h, owner-stated) while all 12
run. No other team has anything on the box.

**On Sanaa's desk, aggregated:** the T10a view-factor defect as upstream candidate
#4 (filing is hers); **K2a rack row module, awaiting her approval**; four DAFoam upstream defect classes, all `NOT FILED`; the
`RESULT_PRIORITY_CHARTER` orderings (v0.5 draft, awaiting her ruling); the
`GATE FAIL` vs bare `FAIL` ledger-vocabulary conflict (referred, unruled); and the
D389 S13 normalisation question (re-grades the whole thermal corpus; no single
rung may take it).

**Chief's rulings, 2026-08-22 (harness session).**

- **D-1 RESOLVED.** The stale shared git index (176 staged deletions, including all
  14 harness files) was cleared by the chief with `git read-tree HEAD` under Sanaa's
  standing approval. **Index clean, working tree untouched.** The loaded gun is
  unloaded; the lesson stands — never a bare `git commit`, always the private index.
- **D-2 RESOLVED.** The four compute facts are **owner-stated by Sanaa,
  2026-08-21/22, chief's session record**: c7a.4xlarge at $0.0513/core-h; runs
  under $25 pre-authorised; *"all the teams have my approval for everything"*
  (2026-08-21); AWS case **178725840000468** for the G-instance quota. VERIFY is
  dropped on these four and on nothing else.
- **D-3 … D-6 are with Sanaa and no agent acts on them.** D-3 lane cap, D-4 the
  five-team split, D-5 `GATE FAIL` vs bare `FAIL`, D-6 the VM2026R1 canonical home.
- **D-6, board note — DO NOT TOUCH EITHER COPY.** `VM2026R1_Fluids/` at the repo
  root holds **123 files, 2.5 GB** (Fluent / CFX / Forte archives). A second copy is
  **being scp'd into `docs/papers/verification_validation/` right now** — 10 files so
  far, **transfer in progress**. Nothing is graded from either, nothing is tracked,
  and neither is moved, deleted or reorganised until Sanaa rules and the transfer
  finishes. A half-copied tree read as a corpus is a measurement of nothing.

---

**Section last written:** 2026-08-22T21:05Z by chief (ubuntu-fb) — GPU grant recorded, GPU pre-registrations dispatched
## closure

**Section last written:** 2026-08-24T16:17:18Z by closure-supervisor (this chief session's
re-spawn, 16:04Z; predecessor killed by an API error at ~16:00Z after one
interim report), from `date -u` in the writing invocation. **Two closure
supervisors are live in two chief sessions; the work split agreed 16:01Z is
exactly one owner per item and is recorded here so the board is truthful.**
The PARALLEL session's closure supervisor owns the Ling 2016 GPU arm (its
grading, RESULTS commit `353925c7`, D490, C-16, and the gpu1 stop request) and
wrote the Ling block below at 16:07Z — carried verbatim, not re-verified by this
session; its board line "results commit `the commit carrying this section`"
resolves to `353925c7`. THIS session owns the Kaandorp close-out, the D476/FS5
adoption ruling and the rest of the board.

**Ling 2016 TBNN GPU arm — CLOSED, VERDICT: NOT A RESULT. D490, L-267,
L-268, N-B40–N-B42, C-16; results commit `353925c7` (parallel session's
supervisor; block carried as written by it).** The lab's first GPU run:
pre-registration FROZEN alone at `e8309b6c` (sha256 `61b2097f…1d97`), code at
`11f93da6`, cost_basis **$0.8048/GPU-h from the published price list**
(`GPU_CAPABILITY_STATE.md` §9, commit `112b61b8`), run on `gpu1` under Sanaa's
verbatim GPU cost approval. Ladder: **G0 PASS** (plant 1.6e-14), **G1 NOT A
RESULT** (ARM-A TBNN at Ling's SGD 2.5e-7 × 200,000 full-batch epochs beats SST
/ `b=0` / train-mean on **0 of 8**), **G2 GATE FAIL**, **G3 NOT A RESULT on both
TBNN models** (3.1–5.3 % and 4.3–14.4 % violation vs 2.374 %; `max‖b‖_F` to
2.1e10), G4 not run as registered. Falsifier 1 fires as written but does not
settle D3: the frozen "full batch by construction" ran ~3.4e5× fewer updates per
epoch than Ling's per-point SGD — **a rate is not an optimiser (L-267)**.
Falsifier 2 does not fire: TPE's 9×77 beats 8×30 on validation by 0.005 inside
the 0.0073 spread and re-selects the CPU lane's batch 8192 + Adam 1.02e-3. Under
the verdict: ARM-B beats all baselines 7/8 (ducts 0.11–0.12) and violates
realisability on **25–46 % of duct cells** for 3 of 5 seeds — RMSE is blind to
the axis Charter §4 gates. **Compute 10.7054 GPU-h = $8.62 derived** (0.97× the
P0 projection; below the registered 12–52 floor — throughput assumption 42–80×
measured vs 5–20× assumed); **waste 7.88 GPU-h = $6.34 derived**, the node
idling after the overnight fleet kill until 15:56:45Z (L-268). **Node idle since
08:03:58Z; stop requested through the chief; only Sanaa can stop it** — this
session's read-only lane confirmed IDLE at 15:58Z (GPU 0 %, 0 MiB, no driver
process). The four other GPU drafts untouched. On Sanaa's desk: a per-point-SGD
ARM-A re-registration, and the chief's self-shutdown proposal for paid nodes
(hers to approve). Peer findings landed: comparator witness artefact (RESULTS
D-5) and the per-case `NASA_2DWMH` reading beside every pooled figure (same case
as FS5/D476's 9.6 %).

**Kaandorp a-posteriori — CLOSED OUT, VERDICT: NOT A RESULT for the whole lane,
on all three registered cases. Commits `a56cc309` (addendum + C-18) and
`961b0b3e` (D492 + L-269). No closure solver is live.** The driver (pid 1111229)
exited 2026-08-23T23:17Z; `lane5.log` ends `[done] lane wall-hours 3.66`. The
six `CBFS13700` rows were graded by hand against the frozen table
(`PREREGISTRATION.md`, one commit ever `0ebc9d53`, blob == HEAD == disk; no
grading script is registered and the record says so). **Supervisor's own reads
of `results.json`, done not relayed:** `TRUTH` U_rms **0.084131** vs the 0.0516
gate = **+63.05 %** (30 % bar ≤ 0.0361, 50 % bar ≤ 0.0258, both fail the same
way) — H0 GATE FAIL on the third case as on both ducts (+61.97 % / +57.0 %), so
the b-only ceiling inversion is not a duct artefact; `NULL` |Δ| **4.625e-05**
(G0b PASS at 1e-3); ML 0.15883 / 0.15107 / 0.15289, mean **0.15426**, mean+2sd
0.16238 above SST and above `MEANB` 0.13965; `x_reatt` 5.895 (NULL; SST 5.891)
→ 6.912 (TRUTH) → 7.948 (MEANB) → 8.78–14.46 (ML) against LES 4.241 — every
b-only injection moves reattachment the wrong way. H1–H3 NOT A RESULT by the
registered H0 cascade; **H5 GATE FAIL ×6** on the REGISTERED `U_bulk/L`
normalisation (0.262–13.67; the `NULL` control itself at 262× the 1e-3
threshold). **Ruled by this supervisor (D492): the frozen `U_bulk/L` clause
governs H5**; the v1.0 §1/§5 gradient-scale reading and its "NOT MEASURABLE"
cell (not in the rule-1 vocabulary) are a disclosed defect of the 2026-08-21
record, not rewritten (rule 6). **G0a PASS as frozen with the limitation
disclosed against the lane's own favour:** rel-L2 0.0 (byte-identical `600/U`),
but at `writePrecision 6` the reader's one-ulp floor is **4.002936e-07**, so
the registered 1e-10 sits **4,003×** below resolution (this session's brief
said ~4e-8 / ~400× from the predecessor's relay — the measured figures govern);
the plant came back at 4.002936e-07, so the zero is evidence and the defect is
the threshold — the THIRD clause in this one pre-registration its instrument
cannot serve (L-269). Completion: five rows at `endTime` 60000, `NULL` at 30884
on `residualControl`; `conv=None` measured — MEANB/ML0/1/2 limit-cycle at
0.69–1.04 `U_bulk` between checkpoints; `diverged=True` everywhere is the trapFpe
BANNER artifact (`run_lane.py:175`), zero `FOAM FATAL` in any log; the rule-14
call-site repair stays queued and the frozen driver is NOT edited.
`AR_3_Ret_360__MEANB` carries `nan` for `unrealisable_frac`/`b_rms_total` (empty
mask after `k` collapsed) — not measured, not zero. `AR_3_Ret_360__ML0/1/2`
BLOCKED (no block in `features_nodurbin.npz`), no metric written. **Cost, C-18:
388.8 core-min registered (prereg §7) vs 219.571 core-min measured = 3.6595
core-h = $0.1877 derived, ratio 0.565×, zero waste** (capped rows are
measurements under the registered rule; MEANB 3411.2 s, 5.2 % inside the 3600 s
timeout), attribution conservative misprediction (0.126 s/it from a
five-iteration check vs 0.0869 measured); load not recorded. Whole lane ≈ 5.2
core-h against 7.1 worst case / 15 cap. **REFERRED to verification via the
chief (D492, unruled):** (a) a gate whose threshold lies below its instrument's
resolution — PASS-as-frozen-with-disclosure, or its own label? and should
`check_comparator_freeze.py` refuse a threshold below the `writePrecision` of
the field it reads; (b) the ten pre-relaunch duct rows' logs carry mtimes
17:27–17:44Z on 2026-08-21, an hour BEFORE the 18:52:18Z freeze commit — rule 2
holds by git for the six CBFS rows (run 08-23) but for the ducts rests on the
file's 17:17:57Z mtime and its "posted to the supervisor" line. **Attribution
disclosed:** `a56cc309` was written by a Kaandorp grading lane whose parentage
(predecessor's lane surviving its supervisor vs this session's 16:06Z lane) is
unresolved at this write — VERIFY; this session's lane was messaged to stop if
it was not the author; exactly ONE addendum exists at HEAD (stamped
16:06:54Z) and no rival was written. **Correction owed in closure's next docket
row:** D492's parenthetical says the lane's draft ids "D491/L-269 were taken by
peers" — true of D491 (used for the D476 ruling), false of L-269, which landed
as drafted. Table 4 (BFS5100) stays BLOCKED-ON-DATA.

**D476/FS5 adoption — RULED: block LIFTED CONDITIONALLY. D491 at `53517fae`;
record Addendum 2 v1.1 at `41774899`.** Verification's cross-team audit pass 6
(`542408f7`) returned **AUDIT: SOUND WITH DISCLOSED DEVIATIONS — CANDIDATE** (a
verification lane's read; the verification supervisor's own read still owed;
the chief is asking). Ruling: the amended instrument's model-facing surface and
the unclipped `q1_wallRe_raw` companion (audit-side diagnostic ONLY) may be
relied on **once verification's supervisor confirms pass 6 as its own verdict**;
a reversal of any pass-6 finding voids the lift and re-arms the block without
further ruling. Never in `F`, never a feature, never a correction (L-219/L-220,
D446, §22.4); `singular_value_ratio_first_to_last` NOT quoted as a number in any
closure record until a registered instrument decision adopts verification's
recommendation (a); no thread pinning; A3 stays GATE FAIL; no standing verdict
moves. Three independent grounds: my D484 diff read; pass 6's own hasher (A2
40/40 `F` + 40/40 `names`, A1 plant re-derived, A4 `cmp` rc=0); this session's
lane re-read 40/40 + 40/40 pairs in `D476_A3_triage/A2_{before,after}.json`
under a live planted control (one hash zeroed → 39/40). **Attribution:** the
record (`41774899`, Addendum 2 written 16:05:46Z) was landed by the PARALLEL
session's closure lane at its supervisor's direction, ahead of this session's
lane, which reached the same ruling and STOPPED rather than write a rival
Addendum 3 — one record, two concurring supervisors. **Supervisor's personal
diff read of `41774899` (both files, as diffs, done not relayed): PASS.** The
addendum is a pure append (290-line prefix re-hashed to blob `b362ea32`); the
`make_feature_library.py` +13/0 guard (pass 6 §31.3) is accepted as a
strengthening with two limitations named and NOT repaired here: it is an
`assert` (off under `python -O`; `sys.exit(2)` is the candidate comparator
form) and its criterion is a one-sided line COUNT — a regeneration that grows
by k lines against a marker-less file with ≤ k hand-written lines still
destroys them silently; shrinkage false-refuses (the safe side). It generates
prose, not a measured number; `build_features.py` / `fs2_audit.py` /
`make_fs2_report.py` are disk == HEAD by sha256 and A2 covers them. Either
tightening is a further change to a frozen instrument: own dated addendum +
supervisor diff read. No build is queued that needs the lift (R6 BLOCKED on
Sanaa; R4, R5C closed). Standards recommendations (a) publish rank + smallest
singular value, ratio only when `s[-1]` clears rtol, and (b) pin threads or gate
on stored bytes — on Sanaa's desk, referred by verification.

**R5C (option C, omega-source repair) — CLOSED, VERDICT: GATE FAIL. D465, L-243,
N-B35–N-B37, commit `0ac76ec2`.** Graded against the frozen pre-registration
(sha256 `a1cfae5a…1277a`, committed alone at `f364cf2d`; re-hashed equal before
grading) by the registered comparator `grade_r5c.py` (sha256 `58eb99…605e5`).
Ladder as registered: **G0 planted-zero PASS** (plant seen to 2.4e-10 relative);
**G2 W2 byte-identity PASS** (settle 1492/354, 14 of 14 sha256 — the V2 legacy
branch IS R4's operator); **G1c switch-active PASS** (`nNegSourceCells` 476–2,274
on all 27 — the negative source is universal, N-B35); **G1 GATE FAIL**
(`kDeficit` rel L2 **1.1848e-04** on `alpha_10_12000_4048` against the
registered `1e-6`; eleven of twelve R4 targets reproduce at the IDENTICAL settle
iteration to 1e-7–1e-11); G3 10 of 27; G4 M=1 → GATE REACHED, **overridden** by
G1 per §3.1. **Registered consequence applied: R4's 12 targets stand, the 15
hills remain INCOMPLETE, the R5C targets feed nothing.** Finding under the
verdict: the Patankar split removes the clipping (22 of 27 at zero
`bound(omega)` events; 10 of the 15 hills COMPLETE under the strict rule) and
the same damping makes the change-based settle criterion stop one target 37 %
early — **a change criterion cannot tell convergence from damping (L-243)**; two
registered criteria measured miscalibrated and left standing (N-B37). The
supervisor re-ran the comparator end to end 2026-08-23 with **zero differences**
(RESULTS.md D-4). Cost **0.140 core-h measured + ≤0.028 bounded = ≤$0.0086**
against 0.210 registered, 1.0 cap (C-2). Whether any R5C target is ever used,
and whether a fixed-point-distance criterion replaces the settle test, are
separate later pre-registrations — Sanaa's ladder.

**GPU reproduction plan — DONE, on Sanaa's desk. Commit `9e82321b`.**
`docs/closure/GPU_REPRODUCTION_PLAN.md` plus five DRAFT pre-registrations
(rule 15 title-verified twice). **(1) Ling 2016** — SIGNED AND RUN by the parallel
session under Sanaa's approval (block above; D490). **(2) Beck 2019** scaled
variant behind an unpriced CPU DGSEM pilot, 7–27 GPU-h cap 30. **(3) Sirignano
2020 DPM** scaled variant, bespoke solver+adjoint build dominates, 19–65 GPU-h
cap 80. **(4) Bae 2022** NOT a GPU item (paper's own O(1e3) CPU-h, ~$51 CPU) —
recommend no GPU launch. **(5) Lozano-Durán 2023** BLOCKED at the ~500-DNS
database + proprietary charLES — recommend no launch. Drafts 2–5 in
`docs/closure/gpu_prereg_drafts/`, every one stamped DRAFT — NOT FILED, NOT
LAUNCHED; GPU spend is outside the CPU blanket (rule 12): per-item sign-off by
Sanaa with a console-read `cost_basis`.

**D-14 thread CLOSED (2026-08-23; supervisor verified before believing):** lane
commits `918e8fe7`, `9f0210dd`, `52e5de39`, `1632af6a`, `52373459` adopted;
`make_coverage.py` read in full PASS; R4 RESULTS.md frozen body lines 1–1313
byte-identical to v1.0; coverage numbers re-read from `coverage.json` (172,106
fitted / 65 dropped; cond p50/p99/max 20.81 / 1.634e4 / 4.430e7; LOFO 0.0011 /
0.0905 / 0.0000 / 0.2238 %) match COVERAGE.md and D475. FS5's per-build
discharge for R4 WAS NOT MET (D475); late delivery discharges the deliverable,
not the disclosure duty; FS5 stays armed.

**Rungs:** FS6 DONE (`9fb0891f`, + Addendum 1 `e1f346ee`); R5 discharged as a
record (`3a4f4bbb`, amended `9f0210dd`); R6 NOT DONE, BLOCKED on Sanaa's
phrasing; R4 CLOSED GATE FAIL (D461; RESULTS.md v1.1 with D-14); R5C CLOSED GATE
FAIL; Kaandorp a-posteriori CLOSED NOT A RESULT (above); Ling GPU CLOSED NOT A
RESULT (parallel session). FS2/FS5 standing gates, both armed; FS5's D476
instrument decision now RULED conditionally (above). **Rungs without verdicts:
none in this session's ownership.** Case verdicts on record otherwise unchanged.

**Live jobs: none.** No closure solver, no driver, no monitor. Lanes this
session: Kaandorp grading lane (its authorship of `a56cc309` unconfirmed at this
write — messaged to stop if not the author); D476 ruling lane finished (stopped
correctly, wrote nothing); read-only gpu1 lane (predecessor's) finished.

**Commits this session (supervisor):** `53517fae` D491 (D476 adoption ruling
docket row, D486 fallback disclosed); `961b0b3e` D492 + L-269 (Kaandorp records,
same fallback); this board write. Lane commits verified and adopted: `a56cc309`
(Kaandorp close-out — numbers re-read by me from `results.json`, addendum
headings and +513/0 append verified) and `41774899` (parallel session's lane —
both diffs read by me, PASS with the two §31.3 limitations named). NEXT ACTIONS:
(1) await verification's supervisor on pass 6 — the D476 lift becomes effective
on its confirmation, void on reversal; (2) the D492 referral limbs (a)/(b) go to
verification via the chief; (3) closure's next docket row carries the L-269
parenthetical correction; (4) the `run_lane.py:175` banner-test call-site
repair and the §31.3 `assert`→`sys.exit(2)` tightening are candidate instrument
changes for a future dated addendum + diff read, not started; (5) nothing new
launches — R6 waits on Sanaa, the GPU drafts 2–5 wait on her sign-off.

**On Sanaa's desk (closure):** gpu1 idle-stop (parallel session's request,
carried); GPU drafts 2–5 (signing is hers; plan recommends none of 4–5); the
per-point-SGD ARM-A re-registration question (D490); R5/A′ direction after
R5C's GATE FAIL (`R5_DECISION_MEMO.md`); R6 phrasing (standing); Ling & Templeton
2015 acquisition (PENDING-MIT); verification's standards recommendations (a)/(b)
from the D476 audit. **Blocked:** R6 (Sanaa); Kaandorp `AR_3_Ret_360__ML0/1/2`
(missing case in `features_nodurbin.npz`); Kaandorp Table 4 (no BFS5100 on
disk); Xiao2016_EnKF (forward model); Lozano-Durán 2023 (data + charLES); the
D476 lift's effectiveness (verification supervisor's own read).

**⚠ Standing hazards:** (1) shared index stale by decay (D486) — `git status`
shows phantom `D`/`MM` rows in closure territory (the Ling `gpu/` four, the two
feature files) while disk == HEAD by sha256; read tracked status with `git
ls-tree -r HEAD <dir>`; inspect, never revert; the index is chief's call.
(2) **L-253 disclosure:** this section was committed blob-based from `git show
HEAD:`; the WORKTREE copy of `## closure` lags HEAD by design and was NOT
fast-forwarded (foreign uncommitted edits sit elsewhere in the worktree file).
Read this section from HEAD. (3) Two closure supervisors are live in two chief
sessions; before any dispatch, check HEAD for a peer's landing on the same item
— this session's D476 lane found the item landed 4 minutes after dispatch and
stopped, which is the correct behaviour.

**Compute:** 487 core-h pre-authorised (charter §18). Live: nothing. This
session: zero solver core-minutes (reads, hashes, three commits). Kaandorp
lane total ≈ 5.2 core-h (C-18 for the last 3.66); Ling GPU 10.7054 GPU-h +
7.88 GPU-h idle waste and accruing until stopped (parallel session's ledger,
C-16).

## dafoam

**Section last written:** 2026-08-24T16:03:31Z by dafoam-supervisor (session 2 close-out addendum; third session's text untouched). *Stamp is `date -u` read in the commit invocation.*

**INCIDENT, self-caught and repaired same session (L-263):** records commit `41e566c3` truncated 561 chars off the D473 row — verification's own 21:14:28Z stamp-correction — because a pipe to `tail` masked two `append_record.py` REFUSALS and `update-index --add` then staged the stale worktree DOCKET the tool had refused. Caught in the post-commit verify by content; **repaired at `6da8a162`, bytes restored verbatim** (prefix+length asserted). New binding practice from L-263: never pipe a refusal-capable tool in a commit chain; stage only paths the tool printed WROTE for; **insertions-only assert on every append-only record commit**. Residue for the chief: the worktree `docs/DOCKET.md` is stale-truncated (its only unique line is the pre-correction D473 row — verified nothing newer); inspected, untouched, the chief's call like the shared index.

**B3 peak-RSS: MEASURED AND GRADED (attempt 2, `d062aace`+Addenda).** M0 PASS 18/18 both arms; **M2a PASS 9.719 / M2b PASS 8.000 GiB (by 114,688 bytes — flagged); M3a GATE FAIL 11.503 vs [5.5,9.0]; M3b GATE FAIL 11.133 vs [6.0,11.0]; M4 GATE FAIL — the registered claim falsified in the registered direction: np=1 is the LARGER arm on both instruments** (one python at HWM 11.487 GiB vs four ranks ≤2.453; N-D24); M5 PASS. Attempt-2 spend 42.91 core-min / $0.0367 derived, 0.93× of estimate (two opposite-sign errors cancelling, recorded as such), zero attempt-2 waste; item total 63.91 of 182.0. Calibration row `d45596f8`. Old 6.156 GiB figure was a 1.81× undersample — the old record's own hedge vindicated, quantifying addendum ordered (L-258). All peaks are under a 12 GiB cap; the unconstrained peak is a new registration, not bought.

**Stamp disclosure (this session, self-caught against its own commits):** the three prior stamps of this section were PROJECTED, not read, and all three sit in the future of their commits: 20:45Z on `539138b4` (committed 20:37:56Z), 21:05Z on `e2ce42a4` (20:57:28Z), 21:35Z on `26a81009` (21:10:41Z). The content beside them was live-read; only the stamps were asserted. From this commit the stamp is clock output.

**PARALLEL-SUPERVISOR NOTICE (chief relay, ~21:10Z):** `EXPERTISE_CURRICULUM` is **RATIFIED at `43b530cc`** (Sanaa, verbatim in the file) and its EXECUTION belongs to the **parallel session's dafoam supervisor** — nothing curriculum-shaped launches from this session. Two dafoam supervisors now share this board section: every board commit from this session diffs the section at the captured rev and reads the diff before staging — a parallel write found there is merged, never clobbered.

*Live reading at write time: `git log`, `ps aux` (no dafoam solver processes; the only `claude --resume 64b13819` process, pid 1173641, started 20:26:48Z — the current chief's lineage, not an independent worker), `date -u`, `stat` on the attempt-1 arm directories. Docker socket not readable from this supervisor's shell; container checks delegated to lanes.*

**CLAIM LEDGER, reconciled against HEAD `b84c43d3` at 20:40Z — both prior sessions are DEAD** (no independent claude process; their last board stamps 20:12Z/20:35Z). What they claimed vs what landed:
- **Session 1's claims (ADF sweeps, B3 re-run, A3 rung-1/3 preregs):** D460 sweep-1 prereg LANDED (`538c9f51`, Amendment 1 before first compute; run root `D460-sweep1-solver-family` verified ABSENT — no compute ever started). A3 rung-1 prereg LANDED (`5d8e2f52`, ancestor of HEAD, nothing launched) and rung-3 prereg LANDED (`97a54c07`, nothing launched). B3 peak-RSS attempt 1 RAN 19:56–20:01Z and FAILED pre-solve (Addendum 1, committed); its Addendum 2 correction sat finished-but-uncommitted in the worktree — landed by this session at `5edfe8c0`.
- **Session 2's claims (W4 M1+M2 done; O2 re-buy "in pre-registration"):** W4 M1+M2 recorded (`108a87e3`, board `72c3a650`) — closed. **O2 re-buy state at death: prereg drafting, launch state UNVERIFIED — flagged to the chief for adoption ruling; this session does not touch it until ruled.** O3 stays BLOCKED on Sanaa's guard-mechanism authorization; **nobody re-attempts the denied command.**
- **This (third) session claims:** (a) B3 peak-RSS re-run under the Addendum 3 ruling; (b) D460 sweep 1 execution + novelty-sweep completion audit; (c) A3 rung-1 and rung-3 patched-column arm execution per their frozen preregs. Any other agent in this territory: read this block before dispatching.

**CLOSE-OUT ADDENDUM, 2026-08-24T16:03:31Z (stamp is `date -u` in the commit invocation), by the 64b13819 session — "session 2" in the ledger above (`01ENBw3KPr5gMaj8Vt7rcxSB`), resumed by the chief 2026-08-24 ~15:55Z with O2/D1 close-out ruled MINE.** The third session's claims (B3 RSS, D460 sweep 1, A3 rungs 1/3) are untouched. What landed today, every number verified by this supervisor against the raw artifacts before writing:
- **W4 O2 re-buy — COMPLETE, results `5a93f6ee`** (Lane X wrote the record 21:31Z and died pre-commit; committed as found + close-out §12). **§3 decision `PENDING`** (zero completed `splu`); **`spilu` 4 of 4 `Factor is exactly singular`** — the CBFS signature on a second case (N-D27); `splu` **`NOT A RESULT`**, killed by the registered 20.0 GiB cgroup cap inside its first threshold (rc 137, `memory.peak` = 21,474,836,480 B exactly, right-censored). **15.00 core-min MEASURED / $0.01283 derived, 0.43× of 35.0, zero waste** — the cap was the pre-registered instrument; gap = memory-band misprediction, duration untested (calibration **C-15**, D488, L-264/L-265). **On Sanaa's desk:** the §3 answer now needs > 20 GiB free to one process — instance change or a factorization that fits — beside O3's guard authorization. `4932a7c3`-class incident: none; `c8254a4a`'s 60.0 ceiling stood unstretched.
- **Curriculum D1 (Tier 1, first executed item of the RATIFIED curriculum `43b530cc`) — `PENDING`, prereg `f07256fb` + Amendments 1–2 + after-first-compute Addendum §16 (`668ce997`).** Arm E COMPLETE: η **1.957350e-08** (P7 HIT), baseline CD 0.020910510006792161 / CL 0.49876526415423195. Lane Y found its step-rule implementation skipping the registered `3e-4` rung (`3×1e-4 > 3e-4` in binary), repaired the driver, voided arm E run 1 under the file's own §4.2(c), re-ran (η reproduced to every digit), then **died at arm O's preflight — arms O and C NOT RUN**. Repair checked by the supervisor against `VERIFICATION_CHARTER` §2d.1: all four conditions hold (L-266, D489). Spend 0.75 core-min gross / 0.30 named waste; calibration row at completion. **Continuation dispatched:** execution-only lane for arms O + C under the frozen file as amended (gate re-run per arm, kernel-only stops) — this session's claim.
- **1.11e+02 (predecessor's open question): RESOLVED earlier, no correction** — committed bytes already correct (110.52 from N-D15's draws; `0d96119d`).
- **Live jobs (this session):** the D1 continuation lane once it launches; nothing else. **Board hygiene:** built via `lab_state_section.py` from the HEAD blob, this block inserted after the third session's claim ledger, nothing of theirs edited.

**Supervisor ruling on the record (this session): B3 §A1.5 repair ACCEPTED — Addendum 3 at `5edfe8c0`.** Crash triage done personally, not adopted: ledger rows re-read against `chain_peakrss.out` (rc=1/7 s; rc=137/302 s, 20.13 core-min); paired control verified physically on disk (`triage/m777/reports` exists, `triage/m755/` empty); staged modes re-measured 775 `ubuntu:ubuntu` (confirming Addendum 2, whose 775-not-755 correction this session committed verbatim as the dead lane wrote it); `mpirun` exit-1 tail read. Re-run proceeds under `d062aace` per VERIFICATION_CHARTER §2d.1 (all four conditions; repair is upstream of the grading path — the frozen grader refused, exit 2, no graded number ever existed). Terms fixed in Addendum 3: `chmod 777` to match the graded chain exactly, everything else byte-identical, §9 from step 3, one repair exception only, 161.0 of 182.0 core-min remain, 21.0 waste stays charged.

**Last commits (newest first):**

| sha | committed (UTC) | what |
|---|---|---|
| `e7d1021b` | 2026-08-23 ~21:00Z | **THIS SESSION** — **L-257**: WebSearch `allowed_domains` unreliably honoured — lane measured it violated twice, supervisor A/B reproduced both extremes under identical parameters minutes apart; off-domain result set is a no-op, not a zero; venue zeros need a same-session in-domain positive control; corollary: ESI GitLab admits a title-level search route past its Cloudflare 403 |
| `f0448fab` | 2026-08-23 ~20:57Z | **THIS SESSION** — D460 sweep 1 **AMENDMENT 2, before first compute** (run root verified absent by `test ! -d` inside the commit invocation): A1-P gains a fourth permitted difference — `gen_arm.py:112` substitutes the fwdad print literals unconditionally, so A1-P as amended by Amendment 1 voided every correctly built control arm. Verified by the supervisor as code (`gen_arm.py:74,:112`, `s1b/runScript.py:312`) before amending |
| `73563d98` | 2026-08-23 ~20:5xZ | D460 lane — novelty-sweep completion addendum on the liaison file (222 lines): **quota MET — 127 searches (quota 63), 18 venues (quota 10), 17 read + ESI GitLab BLOCKED (Cloudflare 403, recorded in neither direction — correct rule-3-at-venue-level call)**. Material find: `mdolab/CMPLXFOIL` #28 (2024, merged) — analogue prior art from DAFoam's own lab, differentiated build fails where plain converges, lever is the stopping tolerance → raises the prior on D460's CONDITIONING branch, narrows no novelty claim. DAFoam org now enumerated 21/21 repos |
| `5edfe8c0` | 2026-08-23 ~20:43Z | **THIS SESSION** — B3 peak-RSS prereg: Addendum 2 (dead lane's finished correction, landed verbatim) + Addendum 3 (supervisor ruling above) |
| `97a54c07` | 2026-08-23 | session 1's lane — A3 rung-3 patched-IDWarp prereg FROZEN, nothing launched; identity comparator proved able to see a difference |
| `5d8e2f52` | 2026-08-23 | session 1's lane — A3 rung-1 patched-IDWarp prereg FROZEN, nothing launched, every registered stop wired to an executable script |
| `538c9f51` | 2026-08-23 | session 1's lane — D460 sweep 1 prereg + AMENDMENT 1 before first compute (assertion A1 was wrong and would have voided a correct arm) |
| `72c3a650` | 2026-08-23 | session 2 — dafoam board: W4 M1+M2 recorded, O2 re-buy in prereg, O3 guard authorization to Sanaa, curriculum D479 |
| `108a87e3` | 2026-08-23 | session 2 — W4 M1+M2 verdicts + the `4932a7c3` incident: L-250..L-252, N-D22..N-D23, D478..D479 |
| `1a20685e` | 2026-08-23 | session 1's lane — D460 sweep record addendum: "current-generation fork" claim upgraded from search summary to upstream source |
| `c8254a4a` | 2026-08-23 19:33Z | session 2 — W4 M1+M2 prereg (632 lines), before any compute |

Older rows (A6 close `6c6de745`, A3 rung-2 `27ce5799`/`92185911`, ADF candidate `757eccf0`, A6 N=16 `66f42398`/`9d5029e8`): see this section at `git show b84c43d3:docs/LAB_STATE.md` and `git log`.

**Live jobs: none dafoam-owned at 20:45Z.** Three lanes dispatching now (cap 3): Lane B3-RERUN (attempt 2 under Addendum 3 terms; est. 46 core-min inside the 161.0 remaining); Lane D460 (sweep 1 execution per `538c9f51` §9/Amendment 1, ~5 core-min registered, + novelty-sweep completion audit, 0 compute); Lane A3-ARMS (rung 1 then rung 3 per `5d8e2f52`/`97a54c07`, staggered so at most one np=4 dafoam adjoint runs beside B3's np=4 — each prereg's own launch gate governs). Box otherwise: 4 heat-transfer solvers + 1 closure solver.

**Rungs lacking verdicts:**

| item | state |
|---|---|
| **A6 N=16** | COMPLETE at 8 of 9 — PASS, aggregate 1.0432%, zero sign flips (row 37). twist idx6 NOT A RESULT. **N=29 NOT RUN**; gate wording is Sanaa's choice (D464), as is the ~5 core-min ninth-component arm |
| **A3 patched column** | rung 2 MEASURED — PASS (degrades vs shipped, N-D18). **Rung 1 MEASURED 21:0xZ, dual reading AS REGISTERED, choice on Sanaa's desk:** per-component rule → **PASS (patched) / PASS (shipped)**, control NOT EVALUABLE; aggregate band → FAIL pending investigation, both arms — the frozen prereg registered the conflict openly and reserved the choice. Headline, supervisor-verified against both logs: **R1-P8b HIT — the rung-2 degradation is NOT a property of the patch**: same library, `shape[115]` 9.2084× worse at rung 2, **2.42× better at rung 1** (0.3826% vs 0.9273%), tracking the sign of the shipped error; R1-P9 split (shape[5] moved 9.09% away) weakens any uniform directional claim; FD reference bit-identical across all three pairings; 0 sign flips (rung 2 had 3). 49.06 core-min / $0.0419 derived. **Rung 3 NOT A RESULT — stopped by memory at 85 s**, 0 of 11 checkpoints, no claim in any direction, cap not raised, no second budget; structural finding, supervisor-verified: the registered gate (16 GiB) cannot protect the registered floor (8 GiB) for an arm peaking 9.2 GiB (16.0−9.2=6.8<8.0) — registration design defect, both numbers frozen, neither changed; 6.80 core-min / $0.0058 derived; **re-registration draft ordered (new item, own price, gate ≥ 17.2 GiB limb), review before freeze**. 399,360 campaign PENDING |
| **ADF primal non-reproduction (D460)** | Novelty blocker **CLOSED at quota** (`73563d98`; ESI GitLab venue honestly BLOCKED — a title-level route now exists per L-257's corollary, unexecuted). Characterisation sweep 1: lane's scratch trial exposed A1-P as unsatisfiable (voided correct control arms); **AMENDMENT 2 frozen at `f0448fab` before first compute; launch authorized 20:5xZ, lane executing** (0 compute spent so far on this item; 5.0 core-min predicted / 20.0 ceiling). Non-gating anomaly noted: §9's F-SM cost basis cites an s1b ledger row (323 s / 5.383 core-min) not tied to a surviving log |
| **B3 decomposition peak RSS** | **MEASURED — see the graded block above** (M0/M2a/M2b/M5 PASS; M3a/M3b/M4 GATE FAIL, falsified in the registered direction). Attempt 1 NOT A RESULT (21.0 core-min named waste, charged). RESULTS commit + old-record quantifying addendum with the lane |
| **W4 M1+M2 / O2 / O3** | M1+M2 recorded by session 2 (O0/M2/M1-D PASS, M1 PENDING). **O2 re-buy: adoption UNRULED — with the chief.** O3 BLOCKED on Sanaa's guard authorization |
| **A2 `CD/shape` PATCHED idx46** | caveat RECORDED (rows 34-35); adjoint-vs-FD-artefact NOT established (sweep 207-238 core-min, not bought) |
| **B3 Stage 4** | BLOCKED by construction — Sanaa's fork-adoption call |

**Two-row verdicts standing** (shipped / patched): A1 GATE FAIL / PASS; A2 PASS / PASS with the idx46 per-component caveat (rows 34-35), optimisation NOT A RESULT; A3 primal GATE REACHED, adjoint BLOCKED (399k) — sweep rungs 1-2 PASS, rung 3 GATE FAIL (conditioning) / rung 2 PASS (degrades — N-D18), other sizes PENDING; A4 PASS / PASS (patch immaterial; CD −7.478 %); A5 GATE FAIL / PASS; A6 BLOCKED (full) — N=16 GATE FAIL (shipped, superseded reference) / **PASS at 8 of 9, aggregate 1.0432%, twist idx6 NOT A RESULT** (patched, fixed reference; rows 36-37). B2 PASS; B3 BLOCKED / PASS.

**Next actions:** (1) B3 attempt 2 → grade → RESULTS.md → verdict. (2) D460 sweep 1 arms + novelty completion audit → filing-readiness reassessment (readiness only; filing is Sanaa's). (3) A3 rung-1 arm, then rung-3 arm. (4) O2 re-buy adoption — awaiting the chief's ruling. (5) Supervisor records commit per verdict as they land.

**On Sanaa's desk:** **NEW — the A3 rung-1 §4 rule choice** (per-component PASS vs aggregate-band FAIL-pending-investigation; the frozen prereg registered both readings and reserved the choice as a gate-threshold reinterpretation; archived-row consistency argument recorded as context; verification supervisor to be consulted via the chief). **D464 — the N=29 gate reading** (charter-verbatim NOT MET vs subset-complete GATE REACHED; the gap is one ~5 core-min arm). **R11 adoption evidence is two-sided** — A3 rung 2 measured the patch degrading; adoption is case-dependent, her call. **MemAvailable floor 12 GiB** ruling. **Five upstream defect drafts, all NOT FILED** (D-A/D-A2, D-B/D-B2, D-C, D-E + the ADF candidate `757eccf0`) — filing is hers alone. **B3 Stage 4 fork-adoption.** The near-zero sign-flip-under-a-passing-norm class (A1 idx6, A5 idx16, A2 idx46). **`DAFOAM_CHARTER.md` §13 enforceability PROPOSAL** (v1.0c, unratified). **O3 memory-guard mechanism authorization** (session 2's escalation, still open). **EXPERTISE_CURRICULUM ratification asks** (D479, §6 of the file).

**Blocked:** B3 Stage 4 (Sanaa); A6 N=29 verdict wording (Sanaa, D464); A6 full-size rung (unchanged); O3 (Sanaa, guard mechanism); ADF filing readiness (two blockers, in work this session); O2 re-buy (chief's adoption ruling).

**⚠ Integrity flags on frozen records, none quoted from:** `A1_naca0012_incompressible.md:167-172` (refuted mechanism, zero strike); `A5_ubend_internal.md:194-196` (in-band set mismatch); `A2/grading_confirmation/RESULTS.md` §1 ("no sign flip anywhere in A2") falsified at PATCHED idx46.

**Untracked in territory, inspected not deleted:** `cases/dafoam/patched_build/team/DALinearEqn_kspopts.patch` and `_subpclu.patch` (uncommitted build artifacts, provenance owed a check); the shared index still stages deletions of the A3 rung-3 files whose worktree copies exist — L-223 shape, **the chief's call, untouched**.

**Shared-board rule in force (chief, 2026-08-22):** `docs/LAB_STATE.md` is never written in the shared worktree. Each board commit rebuilds from `git show $H:docs/LAB_STATE.md`, replaces only `## dafoam` (`scripts/lab_state_section.py --team dafoam --rev $H --out <scratch>`), stages by `git hash-object -w` + `update-index --cacheinfo` in the private index, and the diff-tree must be confined to this section; before every board commit, diff this section at the captured rev against the section file being staged, and read that diff. Carried in every lane brief.

**Record-append rule in force (chief, `0286bb2a`):** every append to `DOCKET.md`, `LESSONS.md`, `NUMERICS_KNOWLEDGE.md` goes through `python3 scripts/append_record.py` (merge form) with `scripts/check_record_reconciliation.py` run BEFORE the edit. Carried verbatim in every DAFoam lane brief.

**Charter:** `DAFOAM_CHARTER.md` **v1.0c** (2026-08-22) — the §13 enforceability PROPOSAL is unratified and awaits Sanaa.

**Images:** `dafoam-idwarp-rot:v1` (only image carrying the rotation patch, md5 `85f59e87…`), `dafoam-subpclu:v2` (PCLU), `dafoam-kspopts:v1`, `dafoam-team:v1` (`0b3c94c33a15`, both patches, ends `USER dafoamuser` → `--user root` for bind mounts). *The hash is the identity; the version string is not.* F6 series under `cases/dafoam/` is plain `simpleFoam`, not DAFoam work.
## heat-transfer

**Section last written:** 2026-08-24T16:16:26Z by heat-transfer-supervisor
(re-formed 2026-08-23 after the 2026-08-22 session limit).

**EXPERTISE CURRICULUM RATIFIED (2026-08-23, Sanaa via chief, verbatim in
Amendment 1 of `docs/campaigns/T-family/EXPERTISE_CURRICULUM.md`, committed
`fe409422`; proposal recorded D474; ratification docket row D483 — its first
append was REFUSED by the upgraded append_record prefix guard on a peer's
in-flight D472 in-row edit and landed on this retry, disclosed).**

**COST-CALIBRATION DIRECTIVE received (Sanaa via chief, 2026-08-23):** every
completed process states predicted vs actual (core-min from logs; dollars
derived at the recorded rate, labelled derived), the ratio, and gap
attribution. This team's first entry, T10a-R: **predicted 144 core-min /
$0.123 → actual 399 core-min wall-basis / $0.342 derived, ratio 2.77×;
attribution: contention (12 solvers live at launch, dominant) +
misprediction (generator memory/wall at n=18 496; the 21 GB peak vs 5.5 GB
estimate); waste: none identified — no stalled or discarded run.** To be
appended to `docs/COST_CALIBRATION.md` when the build lane lands it (not on
disk at this writing). Twelve candidates E1–E12 ranked
by DC-certificate leverage, tiered **behind the unchanged H-2 spine and H-5
order**. Ratification read under rule 9: approval of the proposal **as
written** — pre-authorised-class items proceed, each under its own frozen,
committed, costed pre-registration; **E2, E3-b, E7-3D, E12-build remain
NEEDS COSTING and return to Sanaa costed before launch**; rule-15 title
verification before any source is adopted; VM2026R1 notes still PENDING
D-6. Her "per usual" clause (formal .md updates per item; lab-wide
propagation of general knowledge through the chief) recorded as binding.
**E4 stage (a) — GRADED 2026-08-24T16:16:26Z: rung verdict NOT A RESULT (D493, ledger C-21, lessons L-270/L-271).** Frozen `628e29c4` before any case; 5/5 built, run serially, strict rule 5/5; frozen comparator exit 1 (graded), planted-zero held. **I1 PASS** (BC equation residual 3.794e-11 m²/s² vs 8.1e-8), **I2 PASS** (7.1e-10), **P1 PASS**, **Z1 PASS**; **R1/G1/G2/N1/D1 NOT A RESULT** — the registered bit-identity convergence gate cannot be met by iterates creeping ~6e-11 relative at writePrecision 12 (residuals 1e-10…1e-14); no order/GCI quoted; the §1.5-agreement diagnostic is held unconverted. Cost registered $0.033 → actual $0.0024 derived, **0.0748×**, misprediction: cross-solver-class basis (13.6×), no waste. **Successor E4a2 in design** (lane; same physics/rows/intervals, ONE re-registered thing — a bounded convergence gate with a derived floor, plateau reading, longer endTime, measurable first-crossing); freeze committed before any case, costed on E4a's measured basis. Stage (b) still on Sanaa's desk. Lab-wide propagation proposed via chief: solver class of every cost basis stated (L-271).

### T-family (thermal) — refreshed 2026-08-23 by the T-family supervisor

**Done this session (2026-08-23):**

- **T10a-R GRADED (D466, L-244): arm verdict GATE FAIL — 5 PASS / 4 GATE
  FAIL / 0 NOT A RESULT** against its own registered predictions; T10a itself
  closed and unchanged. `R_x` completed 2026-08-22 23:45:53Z; 3/3 strict-rule
  DONE; frozen comparator (byte-identical to the `7150182b` blob) run
  2026-08-23, rc 0, planted-zero OK everywhere, `gate_t10aR.json` written.
  **RX3 falsifier FIRED — the T10a/T9a band-smaller-than-error pattern does
  NOT persist at the fourth level:** m/f/x CONVERGING at p 0.6850 (c/m/f had
  implied 1.480 — the artefact), band opens to 0.14724 % and covers the
  0.07986 % B1 error (dev/band 0.542; all four rows 0.54–0.75). **RQ2
  falsifier FIRED** — 2AI→2LI moved B2 0.17547 % toward exact vs registered
  ≤ 0.010 %: a material part of the box error is the view-factor integration
  method (registered reservation confirmed, directive prediction missed, both
  on the record in advance). **RS identity PASS bit-exact** (qr(R_s)==qr(B_f)
  on all 7 056 faces): solver-tolerance category ruled out at once. Cost
  $0.342 gross vs $0.123 registered (2.77×), within the 10× stop threshold.
  Disclosure on the verdict line: prereg ADDENDUM 2 remains on disk,
  unfrozen/uncommitted (chief's ruling; item is on Sanaa's desk); every
  applied gate byte-identical to committed `7150182b`.
- **owner: peer session's heat-transfer supervisor as of 2026-08-24T16:00Z (chief's redirect); this session's scope is EXPERTISE_CURRICULUM execution only** — **T1b L4: `R_10k_x` DONE under the strict rule** (rc=0, End, 20000/20000).
  The prior board's VERIFY on its endTime is **resolved: 20 000 is the
  registered design** (`T1b_L4_AMENDMENT.md` §4 table: 20000/80000/80000/
  80000). `analyse_t1b_L4.py` refuses partial grading by design — no L4 row
  is graded until all four x-cases carry DONE. A completion watcher is
  running (30-min poll for STATUS.R_30k_x/R_100k_x/R_300k_x, deadline guard
  2026-08-27); on completion: mark → comparator → grade the (m,f,x) triples
  under the amended Roache rule.
- **T3 ext1 COMPLETE 8/8 (`R_f` finished 2026-08-24T14:53Z, rc=0, 78000/78000, wall 162 094 s = 45.0 h, 24 h ahead of the contended-basis ETA; strict-rule dry-run 8/8 PASS, supervisor triage: completed, not crashed).** **owner: peer session's heat-transfer supervisor as of 2026-08-24T16:00Z (chief's redirect); this session's scope is EXPERTISE_CURRICULUM execution only**. DISCLOSED HANDOVER STATE: before the redirect reached this session, its re-grade lane had ALREADY written the eight `DONE.<case>` markers (15:58:04Z, `log.mark_done_ext1.20260824T155759Z.txt`), run the frozen `analyse_t3.py` (15:58:44Z, `log.analyse_t3.ext1.20260824T155826Z.txt`, **`gate_t3.json` rewritten at that time**) and two residual-decay diagnostic logs (16:01–16:02Z); the lane was ordered to stop at 16:03Z and no `T3_EXT1_RESULTS.md` was written. Nothing reverted; the peer supervisor inherits this state and grades — this session does not.

**Live jobs — 3 solvers (T1b L4 arms), single-core `buoyantBoussinesqSimpleFoam` — **owner: peer session's heat-transfer supervisor as of 2026-08-24T16:00Z (chief's redirect); this session's scope is EXPERTISE_CURRICULUM execution only**; this session's L4 completion watcher was stopped 16:03Z.** Reading taken 2026-08-24T15:54Z (`date -u` in the reading invocation). **Do not
touch them.**

| pid | cwd | iteration / endTime | ETA |
|---|---|---|---|
| 442445 | `T1_runs/R_300k_x` | 73 157 / 80 000 (2026-08-24T15:54Z) | ~2026-08-25 |
| 450274 | `T1_runs/R_100k_x` | 60 758 / 80 000, advancing 0.36 it/s | ~2026-08-25 07Z |
| 488219 | `T1_runs/R_30k_x` | 55 382 / 80 000 | ~2026-08-25/26 |
| — | `T3_runs/R_f` | **78 000 / 78 000 DONE 2026-08-24T14:53Z** | — |

**Rung verdicts on record** (unchanged from 2026-08-22 except T10a's arm; **T3 and T1b rows — **owner: peer session's heat-transfer supervisor as of 2026-08-24T16:00Z (chief's redirect); this session's scope is EXPERTISE_CURRICULUM execution only****):

| rung | verdict |
|---|---|
| **T1c** | GATE FAIL 3/4; L4 row NOT A RESULT |
| **T1b** | PASS ×4 by the frozen comparator but every triple DIVERGENT/STAGNANT (D440); no mesh-converged value until the L4 arms land (10k arm DONE, 3 running) |
| **T1a** | BLOCKED — no band from one correlation |
| **T3** | NOT A RESULT 4/4; primary (Vogel & Eaton 1985) NOT OBTAINED — necessary, not sufficient, not the binding constraint; **ext1 running, 7/8 done, `R_f` ETA ≤ 2026-08-25T14:54Z** |
| **T9a** | GATE FAIL; T9a-D REPORTED (D454, L-227) — cause is the interface scheme |
| **T10a** | GATE FAIL (closed). **T10a-R arm GRADED 2026-08-23: GATE FAIL, 5 PASS / 4 GATE FAIL / 0 NOT A RESULT (D466, L-244)** — band covers the error at the fourth level, p 0.685; quadrature method material. T10a-VF REPORTED (D457, L-231); upstream candidate #4 drafted NOT FILED |
| **T4** | half-open — graded rows need closed ASME primaries |
| **T5** | PRIMARY HELD; prereg draft written 2026-08-22, unfrozen, 12 INTERPRETATIONs on Sanaa's desk |
| **T2, T6–T8, T9b/c, T10b, T11–T13** | not started; T6/T12/T13 and likely T7, T9c over $25 |

**F14 / DC-cooling ladder:** unchanged from 2026-08-22 (K0c PASS; K0cS/T/X
GATE FAIL; K0b + K0cG/P/Q/R verdicts VERIFY; K2a on Sanaa's desk; K2b cost
VOID; K2e/KV1 VERIFY).

**Next actions (this session, curriculum only):** 1. E4a: lane building + launching serially behind the L4 arms → mark → frozen comparator → results + calibration row → commit. 2. Then the next pre-authorised-class curriculum item whose prerequisites are met, own prereg frozen before compute. (L4 grading and T3 re-grade: **owner: peer session's heat-transfer supervisor as of 2026-08-24T16:00Z (chief's redirect); this session's scope is EXPERTISE_CURRICULUM execution only**.) 3. T5 waits on Sanaa's
INTERPRETATION rulings. 4. T10a-R successor questions (whether any rung arms
a band from a triple whose implied p exceeds the observed error decay —
L-244) belong to verification, flagged, not taken here.

**On Sanaa's desk** (carried, plus one new): Vogel & Eaton purchase
(~25–40 USD, figure unconfirmed); T5 draft INTERPRETATIONs; T1b L4 cost
10.54 USD registered vs ~5 approved (arms running, on the record); T10a
view-factor defect as upstream candidate #4 (NOT FILED, novelty search not
done); UPSTREAM_QUEUE #4 numbering conflict; K2a approval; **T10aR prereg
ADDENDUM 2 commit** — on disk, unfrozen, uncommitted after this lane's own
permission refusal; per the chief's ruling no agent re-routes it; if she
directs the commit, she or a fresh session makes it.

**Blocked:** T1a; T3 graded rows (primary missing *in addition to* the
ladder); T4 graded rows (ASME primaries).

**⚠ D389 open and deliberately unrepaired** (S13 mean-normalisation, ~24×
looser than it reads; moves verdicts across K0c/K2e/KV1). Owner: chief. No
single rung may take it.
## cfd

**Section last written:** 2026-08-23T21:16:02Z by cfd-supervisor (second owner session — the grading session; the session that authorized the arms died between their launch and their grading). Stamp taken from `date -u` in the committing shell invocation per the chief's 2026-08-23 timestamp directive; this session's earlier "20:55Z" stamp was projected, not read — owned here as an instance of the bd3edfe8 defect class.

**Last commit:** `0bbac521` (F4 step-0/1 prereg FROZEN, 3 paths +1,581), `f89aa7b4` (cfd's two COST_CALIBRATION rows), `7a96cf54` (OPENFOAM.md re-scope +87/−3), `1135e3c5` (F4 §8 source-read, pure append +329), `3b9bcf31` (F7a R0), `5ede69ac`/`ca65745c` (board), `ea204b3d` (D481 + L-255), `b8fe7eea` (L4 diagnosis results + 22 artifacts) — every one post-commit-verified (only its paths).

**Live jobs:** none — no cfd solvers, no lanes. Do not touch the heat-transfer `buoyantBoussinesqSimpleFoam` solvers or closure's Kaandorp `simpleFoam` (driver spawns a fresh solver pid per row — never cite a stale pid).

**Directives acknowledged in force (2026-08-23):** (a) **cost calibration** (Sanaa, verbatim on the CHIEF board): every completed process states predicted vs actual, ratio, gap attribution, waste separately named, row appended to `docs/COST_CALIBRATION.md` from HEAD content (the worktree copy of that file lost its whole table tonight — 51 lines behind HEAD; HEAD intact, reported to chief; never append from the disk copy). cfd rows landed at `f89aa7b4`: L4 diag **0.35x** of projection (zero waste; Arm A phenomenon-terminated at iter 182; Arm B basis carried load-19.5 contention, applied at load 5.03 — record the load beside any per-iteration basis); F7a R0 exact 0/0. **Standing obligation: F12's eventual row must name the 9.79x cross-solver spread as the calibration gap.** (b) **timestamps**: every stamp is `date -u` read in the same shell invocation as the write — in every cfd lane brief from now on.

**F4 step-0/1 prereg — FROZEN `0bbac521`, NOTHING LAUNCHED, and the supervisor's read GATES any launch (read is PENDING — checks #1/#4 are half-done: commit verified, all three blobs sha256 == disk, status-header gate language confirmed; the diff read of prereg + reader skeleton is NOT yet done and no launch may be authorized before it).** Lane's four pre-freeze corrections, all worth knowing: control case is `warmup20_bounded_realtime` (Euler), not `warmup20_bounded` (localEuler); endTime fixed to 6.5e-05 (1.0 was unreachable — rule-4 clause would never hold); writeInterval fixed to 1.3e-05 (1e-3 would write no fields — the recorded endTime/writeInterval trap); **Step 1 re-specified to the inlet patch ONLY** after the source read showed the briefed all-boundary variant is a bit-exact no-op on zeroGradient patches and puts mass through the solid wall on the no-slip patch. Reader is a frozen skeleton (grading bodies `NotImplementedError` by design, cannot be tuned to logs that do not exist); controls C1/C3 ran at freeze with six injected mutations all caught; C0/C2/C4 PENDING on run logs. Cap: **12 core-min run (6/step) + 3 build allowance, envelope ≤15 = $0.0128 derived**; rate is record-quoted-artifact-missing (the 279.93 s log is gone from disk), price reported-by-owner. §10.4 pre-commits the calibration close-out; its freeze-time condition line ("ledger not tracked at HEAD") was true at drafting and is now stale — the operative clause (verify at HEAD before appending) stands.

**DPW8_V2 L4 diagnosis — GRADED this session, under prereg `99f939ee` (blob sha256 re-verified by this session's supervisor before grading; reader `analyse_l4_diag.py` committed pre-launch at `30d93a0c`, disk == blob, full diff read by supervisor).** The prior board's "launching now" line resolved TRUE: the authoring lane launched both arms 20:01Z and they completed (20:03Z / 20:20Z) before that session died. Controls C1–C5 all green (C5 plant auto-raised to −175205 per §5, read back exactly, real file md5 unchanged). Results record: `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md` @ `b8fe7eea`; transcript `verification/runs/DPW8_V2_runs/L4_DIAG_GRADING_OUTPUT.txt`.
- **Arm A (relaxation only): BLOCKED** (§6) — SIGFPE at iter 182/600, rc 136. Supervisor triage (personal check #2): launcher exonerated (bashrc sourced, correct binary, 4450 s cap untouched at 124.26 wall s); ZERO bounding-k lines; divergence proceeded to FP overflow in the U-equation smoother. Header-identified Cd/Cl at the last written row (iter 181) = 1.6026e+37 / 8.0168e+37 — the supervisor's own first read quoted ~1e35 from the wrong columns (the §2.1 CmRoll/CmYaw trap, caught by the filing lane; nothing turned on it). The crash is the phenomenon, not the toolchain; the frozen §6 label stays BLOCKED, no post-hoc relabelling.
- **Arm B (div(phi,U) linearUpwind→upwind only): NOT BOUNDED** — B1 FAIL (bounding k @ iter 136, kmax 4.004e7), B2 FAIL (max|Cd| 100–600 = 17,520.5 vs <30), B3 FAIL (5,359.82 vs <5), B4 FAIL (y+ 189.906 vs <20). Completed cleanly (rc 0, End, age guard +1142.6 s).
- **Outcome map cell (§7): PENDING** (blocked arm). Established narrowly: the momentum-convection lever is eliminated as a sufficient rescue; the relaxation arm produced a harder divergence (triage finding beside its formal BLOCKED). **L4 stays NOT GATED; no physics number published.**
- **Cost:** 21.1 core-min solver (124.26 + 1142.22 wall s, single-rank), ≈21.5 total = **$0.018** (reported-by-owner rate). Under the 150 core-min cap; each arm under its 75.
- **Successor decision (supervisor, 2026-08-23):** no further L4 diagnosis compute now; both cheap levers spent. Third-lever question (omega wall BC at L4 first-cell spacing / near-wall treatment / §3b linear-solver stall — or record the family stopping at L3) filed as **D481**; needs its own costed prereg or the chief's word. Lesson **L-255**: a divergence-diagnosis prereg must pre-declare the label for a divergence-CRASH (§6's crash→BLOCKED turned the most informative outcome into a PENDING cell).

**Incidents:**
- (prior session, closed) commit `070da305` reverted heat-transfer's committed board section — worktree-behind-HEAD disease; repaired verbatim at `40984dac`. **Standing guard applied again this session:** at this board commit the worktree lagged HEAD on THREE foreign sections (closure == old `cb14e415`, dafoam == old `1f188613`, verification == old `539138b4` — each byte-identical to a committed ancestor, so nothing uncommitted existed); base for this commit is HEAD's file with only this section changed, so the commit diff touches only cfd lines.
- **NEW, for the chief:** the harness scratchpad is SHARED fleet-wide, not session-private, and generic filenames collide: heat-transfer's `878f1556` (their K0cG cost addendum, content correct and untouched) carries the cfd lane's D481/L-255 commit MESSAGE byte-identically — their commit invocation read our lane's `msg2.txt`. L-252 recurring. No content damage either direction (verified); history misattribution only. Recommend per-invocation-unique scratch filenames be made binding; rewriting the peer's commit is the chief's call, not ours.
- Shared-index phantom (chief's jurisdiction, inspect-only): `launch_l4_diag.sh` shows as staged deletion in the shared index while disk is byte-identical to HEAD's blob (verified sha256). Same class as the other phantom `D` rows at session start. Nothing reverted, nothing touched.

**Resolved earlier on 2026-08-23 (prior session, supervisor's own reads):**
- **W2 VERIFY closed.** `W2_sparta_runs/setup_sparta_case.sh` mtime 2026-08-22 17:38 = the closure team's H-7 libs-institutionalization lane; committed 17:48 in `5162ec8e`; disk is byte-identical to HEAD (the `MM` was the stale shared index). Diff read personally: adds only an L-221 `grep -q libspartaTurbulenceModels` assert that refuses on a missing libs entry. Benign; W2_sparta stays closed.
- **GEN_ALT is GRADED, not unwritten.** The prereg at `verification/runs/GEN_ALT_runs/GEN_ALT_PREREGISTRATION.md` carries a full scored Outcome (2026-08-08): verdict **GENERATOR-OWNED** per the pre-declared rule (blockMesh max-AR refinement factor ×0.945 vs pyHyp ×1.71 at matched counts; near-wall AR 37.4 vs 87.6-class; G1/G2 HELD, G3 refused by the born-clean gate at non-ortho 70.13/70.11 > 70 — no solve ever ran, by refusal, honestly). Freeze chain verified: prereg frozen `9c4fbef4` 23:16:04Z, outcome `41f0e1df` 23:19:01Z, moved in `a1fbe127`. Cost ≈0.4 core-min. Campaign record landed: `verification/campaign/GEN_ALT_generator_matrix.md` @ `8974eb75`.
- **MESH_STANDARD consistency check done (they were never to be merged).** `docs/standards/MESH_STANDARD.md` (v1.2, single-mesh quality gates + birth certificate + §7 marine) and `docs/MESH_STANDARD.md` (grid-family sizing/scatter) are complementary, both flag the name collision on their face, cross-refs sound, one-home-per-fact respected (§7.3). One staleness found and fixed: the family doc's header cited the companion as v1.0/2026-07-25 while its own Sources said v1.2 — header updated, no gate value touched.

**Open run families — triaged 2026-08-23 (read-only lane sweep, supervisor spot-checked; the 2026-08-22 first-fill table had 3 rows WRONG and 5 PARTLY WRONG):**

| family | actual state, from the records |
|---|---|
| **DPW8_V2 L4** | Diagnosis GRADED (see above): Arm A BLOCKED, Arm B NOT BOUNDED, map cell PENDING; L4 NOT GATED, root cause still open, third lever = D481. L1/L3 PASS stand |
| **F5b** | Feasibility **PASS** on record (`F5bc_unsteady_statistics.md`); Physics and Gate rungs literally "[to be completed]" — **PENDING**, not ungraded. Run dir really is one file. Trap: `F5b_cylinder_re100_act.json` is a DIFFERENT case (Re=100 shedding act). Next rung ≈25–35 core-min |
| **F5c** | Effectively closed: headline withdrawn to unmeasured; 1.313 H was RELAXATION (misattributed, `F5C_LEVER_ISOLATION_RESULTS.md`); **Stage B was NEVER chief-approved** ("Stage B NOT approved and not run", header of `F5C_STAGE_A_RESULTS.md`) and O3 firing makes it moot. First-fill's "chief-approved Stage B" was wrong. A3-vs-A4 disagreeing 4.224 H on a relaxation-only change is residual-free proof neither solve converged |
| **R4 (Ahmed turn)** | First-fill row WRONG: leg 2 ran 2026-08-10, **n = 4 of 4** (`R4_AHMED_C3_LEG2_RESULTS.md`; B3 broad scatter R = 0.324 vs 0.28 bar, near miss; DISSOLVES confirmed). Turn **WITHDRAWN as a feature** (chief ruling `8f5bf878`, `R4_AHMED_TURN_WITHDRAWAL_2026-08-10.md`). No SIGNAL/NOISE verdict claimed — the c4 CI leg was deliberately not taken. Optional n=7 (~3.1 core-min/draw) needs chief's word. NOT the closure R4 SpaRTA build |
| **F12** | Rule-12 defect **CLEARED 2026-08-23**: costed addendum committed `3f23c172` (chief-directed; supervisor verified the original 140 lines byte-identical, rule-6 assertion present). Five rungs ESTIMATED 383.5 core-min = $0.33 on the F2 same-solver analog, capped 1,300 core-min with the coarse rung as calibration (a 9.79× cross-solver spread vs the DPW8_V2 basis is real and unexplained — the medium cap deliberately stops the campaign if Basis B's rate is the true one). **F12 stays PENDING; the addendum authorizes no launch.** Implementation trap on record: `rae2822_case9.py` default timeout 7200 s would kill the fine rung (est. 13,118 s) — must be raised at build time, changes no gate |
| **F7a re-gate** | **GATE FAIL stands untouched at +11.03% max** (graded vs Martin & Moyce at dy = a/128). **R0 EXECUTED 2026-08-23, 0 core-min, `3b9bcf31`** (§7 appended to `F7a_REGATE_SPEC.md`, rule-6 assertion held at 0 renumbered lines): the paper (arXiv:2108.08769 v1, Leakey/Glenis/Hewett, title-page verified) states NO front-extraction method; the prereg's fallback back-out shows a single fixed rule (α = 0.65 floor-row contour) collapses the mean code-to-code offset **+23.36% → +0.70%** (~97% of the mean), while shape survives at ±7.3% max — a definition-independent code-to-code difference of order ±7% remains at a/16. P5 struck in magnitude (bar now ≈7%, kept as a reading per L-76). R1a/R1b/R1c NOT authorized by the addendum; supervisor read of the new diagnostic reader PENDING (personal check #1) before its numbers are relayed further |
| **MODEL_FORM successors** | First-fill row WRONG: all three preregs carry **executed outcome blocks** (FPE rescue 18.16 core-min; H ext 41.66; H hills 29.18). Verdicts are refusals by the n<3 rule ("containment REFUSED — no band exists at n = 1"). Substantive finding: a family-convergence wall on the hills. CLOSED as registered; row corrected |
| **mbc_retry, uq_batch** | CONFIRMED — both self-labelled by their own 2026-08-18 READMEs: "Nothing here is graded." No action; any rung wanting either outcome re-runs it |
| **F4** | θ=32.5°/35° gate cases still held — correct. Settles reference replaced with Kussoy & Horstman TM 101075, ±30% band pre-registered. θ=20° SIGFPE: **mechanism #6 ELIMINATED 2026-08-23 by code-path proof (`1135e3c5`, §8 of the campaign record; supervisor verified the load-bearing source lines himself)** — no reconstruction exists at non-coupled boundary faces (`surfaceInterpolationScheme.C:295-298`), pos==neg there, so the hypothesized limiter-bypass spike cannot occur and the boundary-face count never enters the path. Two NEW live hypotheses from the same read: (a) exact cancellation of the Kurganov aSf dissipation at real boundary faces → undissipated central flux (also explains why mechanism #5's null discriminated nothing); worst cells all in the inlet-adjacent column (ids ≡ 0 mod 120); (b) the excursions are CRYOGENIC (T ≈ 20 K / 3 K vs TMin = 20 K), reachable by a 2.7–3.5% \|U\| error at M 7.05 — no exotic mechanism needed. **Records defect found: the bounded-run logs the record and Group 3 cite are GONE from disk** (the 4–32% bounded fractions currently cite artifacts that do not exist; only the original crash log survives). Step-0/1 discrimination prereg being frozen (see Live jobs); ≈9.4 core-min when authorized |
| **F5** | CONFIRMED and understated: no 1e5/1e6 trees; re10000 is **mesh-only**; and the ladder's own record says **"do not climb to Re 5000 or Re 10,000"** (2D wake tops the recirculation-bubble gate's applicability; 5.9–13.7 h/rung for a weaker gate). Informative next step per the record is the 3D rung. Zero-compute follow-up: Dong & Karniadakis literature access to upgrade Re 10k/2k bands |

**Closed, verdicts on record:** 4G, B52_RUNG6 (REPRODUCE), D5_rsm (SSG and LRR
bracket the DNS; *which* RSM is right is not settled), DMR, F2 (PASS banded), F3
(PASS), F8 (**NO VERDICT — and that is the result**), F9 (PASS quasi-steady, gate 2
stays FAIL vs Womersley), F11 (GATE REACHED), FPE_DIAG (SHARED-BY-CLASS, recorded
only by citation from its successor prereg), GEN_ALT (GENERATOR-OWNED —
campaign record `verification/campaign/GEN_ALT_generator_matrix.md`, commit
`8974eb75`, 2026-08-23), MESH_AUDIT, W1, W1_hump, W2_sparta, W3.

**⚠ Structural fact this team must know:** with five exceptions, the run dirs under
`verification/runs/` carry **no README, RESULTS, PREREG or DONE marker at all**.
**The verdicts live one level up, in `verification/campaign/*.md`.** Do not
conclude a family is ungraded because its run directory is bare.

**Standards — two documents, not two copies (do NOT merge):** `docs/standards/MESH_STANDARD.md`
(v1.2) = quality gates; `docs/MESH_STANDARD.md` = grid families. Consistency
verified 2026-08-23 (see above). `docs/OPENFOAM.md` — triaged 2026-08-23: the
**v2606 claim is VALID** (`/usr/lib/openfoam/openfoam2606` is the only install);
what was stale was the framing — **FIXED at `7a96cf54`** (dated re-scope note
at top, WSL section marked HISTORICAL, container section marked as describing
an artifact that does not exist on this box — never tracked in any commit;
same-invocation bashrc-sourcing rule stated with the L4 §9 citation). Flagged
to the chief, outside cfd scope: four docs still carry `wsl -d Ubuntu --
openfoam2606` as a LIVE run instruction (`docs/HANDOFF.md:97,213`,
`docs/HANDOFF-BG2.md:26`, `docs/HANDOFF-RACEGUI.md:95`,
`docs/DEMO_RUNBOOK.md:12`).
`docs/OPENFOAM_SOLVER_BUILD.md`: two dead `demo-output/website/...` paths for
`rhoCentralFoamBounded_src` **fixed 2026-08-23** (source verified on disk at
`verification/runs/F4_runs/swbli_cylflare/`).

**Next actions:** (1) **supervisor diff-read of the frozen F4 prereg
`0bbac521` + reader skeleton — the gate on launch authorization** (envelope
≤15 core-min when authorized; grading bodies must be implemented and their
diff read before any output is believed). (2) supervisor diff-read of
`verification/runs/F7_runs/r0_implied_front_definition.py` (new measurement
script; its §7.3 numbers are not relayed beyond this board until read —
personal check #1). (3) F5b physics rung (~25–35 core-min) as the next cheap
compute candidate — needs its own frozen prereg first, with the calibration
close-out clause and load-stamped basis. (4) D481 third-lever decision for
DPW8_V2 L4 — chief/next session. (5) dead-path sweep: the
`demo-output/website/...` stale-citation class is corrected inside the F4
record (§8.10, `1135e3c5`) but persists in `NOT_PASSING_REGISTER.md`'s F4
entry and `mega-batch`'s driver. (6) the F4 missing-logs records defect:
decide whether Group 3's bounded-fraction figures need a VERIFY flag in
`NOT_PASSING_REGISTER.md` until step 0 regenerates the evidence (step 0's
instrumented re-run is exactly the recovery path).

**On Sanaa's desk:** nothing from cfd currently.

**Blocked:** nothing currently identified.

**Case tree:** `cases/{committee-grids, demo-surfaces, hlpw6, mega-batch, tmr,
unsteady-cylinder, valve}` is **dormant in git** — none is the subject of a recent
commit. **`tmr` is the most open of them**; **`mega-batch` has a broken driver
path** (it points into `demo-output/website/...`, and stale paths of that shape are
**systemic** across this team's records — treat any such citation as suspect until
resolved). `models/tmr/**` deliberately holds solver cases outside a run tree, a
documented `FILING_CHARTER` §3 exception: *the rule was wrong, not the tree.*

---

## verification

**Section last written:** 2026-08-24T16:15:20Z by verification-supervisor (stamp from
`date -u` read in the committing invocation). FOURTH session — a RE-SPAWN:
the session-4 predecessor (spawned ~15:53Z) died at ~16:00Z to a transient
API error with nothing committed and its lanes with it (L-186). Everything
below was re-derived from HEAD blobs and disk by this supervisor, not
remembered. Session 3's record (passes 1–5 believed, four instruments
believed — D471 `95333148`, D472 `8f94f170`, D473 `b2d9e7ce`+`dc1a2085`,
append_record `9a17109f`; ledger wiring `80a4d714` + C-11..C-14 believed;
stamp correction; incidents `d97ed4c9`/`890bfa7f`, L-245/L-247) stands in
git history at `ce204146` and is not repeated here.

**Pass 6 — D476 — BELIEVED (this session, own read).** Lane pass `542408f7`
(21:27Z, CANDIDATE) was never read by the supervisor that dispatched it; this
supervisor re-derived every load-bearing limb with its own code, read-only
toward closure: freeze `bf4956bc` one file/118 insertions/alone, blob
`8fac067c…` == `RESULTS.md:4`, 118-line prefix `cmp` rc=0 against HEAD's 147
lines, first evidence +162 s after the freeze; **A2 40/40** `F`+`names`
identical (own hasher); **A3 6 leaves / one leaf-name** unpinned and rep2,
**0 pinned** (own stripper); planted control on disk (cell 31818,
83.48553657531738, 0→1, PASS); ranks 100/110 (duct 96/110); frozen §4/§7/§8
text read. **AUDIT: SOUND WITH DISCLOSED DEVIATIONS — BELIEVED; the prereg-§7
adoption block on closure's amended FS5 instrument is RELEASED by this audit**
(A3 stays GATE FAIL; the §30(a) ratio question stays a recommendation for
Sanaa; no standing verdict moves). Recorded in `docs/CROSS_TEAM_GATE_AUDIT.md`
("Supervisor's own read of pass 6") and ledger row C-19 (0.22 core-min vs 3–6
predicted, ≈ 0.04×). Relayed to the chief for closure.

**D473 row at HEAD checked:** the 561-char stamp-correction tail
(`*[Stamp correction 2026-08-23T21:14:28Z … ]*`) is intact after dafoam's
`6da8a162` repair of their `41e566c3` truncation.

**Chief relay items answered this session:**
- **`scripts/mutation_harness_known_test_names.py` absent from disk, tracked
  at HEAD (blob `5ec5a9ce`, 203 lines, index entry present).** Finding: it is
  one of exactly TEN unstaged tracked deletions (` D`) in the worktree, and the
  ten are the same ten this board already listed 08-23 as "tracked, absent from
  disk": this harness (`c83c9de0`, 2026-08-17T18:35Z, trailer `Lab-Agent
  …/lab-check-repairs`), `K1_STANDING_THERMAL_CHECKS.md` (`4afefe54`,
  2026-08-17T18:59Z), and the eight K2bP heat-balance artifacts (`9f3971f6`
  MOVE_MAP R25, 2026-08-18; since adjudicated by heat-transfer as D477 —
  DELETE `a311d872`, REVERSED `0c742c66`, "worktree deliberately untouched").
  Each of the two 08-17 commits ADDED exactly one new file and that one file
  is the absent one; no commit ever deleted either; no linked worktree exists
  now (`git worktree list`: main only) but H4_ALLOCATION `af16ceef` found 8
  prunable worktrees pointing into the wiped scratchpad. **Reading: these
  files were never written to THIS worktree — they were committed from a
  scratchpad-resident linked worktree (or by hash-object from scratch) on
  08-17/18 and the shared index only began showing them as deletions after the
  chief's 21:15Z `read-tree HEAD` refresh. Not a disk-clearing event; the same
  mechanism as D477's eight.** Disposition recommended (not taken — chief's /
  Sanaa's call under the index rulings): restore the tracked bytes from the
  HEAD blob (`git show HEAD:<path> > <path>`) for the harness and K1; nobody
  has unfinished work on either, so nothing is reverted; the eight K2bP files
  follow heat-transfer's D477 disposition. Until restored, `check_absolutes.py`
  cites a planted-error control that cannot run — FAIL_OPEN_GATE_AUDIT line
  527 already reads it UNPARSED.
- **dafoam's proposed rule (L-262 / C-10): "launch-gate memory limb ≥
  neighbourliness floor + predicted arm peak."** Evaluation for the standards
  queue (recommendation; binding is Sanaa's): SOUND as a necessary condition
  and arithmetically forced — a gate at 16 GiB with an 8 GiB floor admits a
  9.2 GiB arm that breaches the floor before any co-tenant moves. Three
  refinements before it is written into a prereg template: (i) "predicted
  peak" must be the arm's REGISTERED UPPER band, not its point estimate, and
  the memory band must be priced from a measured fill on the same operator
  class (C-15's lesson) — an under-predicted peak defeats the rule silently;
  (ii) the limb must also reserve co-tenant growth: floor + peak + the
  registered growth allowance of the live solvers at launch (four
  `buoyantBoussinesqSimpleFoam` arms grow at write intervals), else the rule
  protects the floor only at t = 0; (iii) the guard's floor limb must sample
  `MemAvailable`, not `MemFree`, at the same cadence the launch gate polled,
  and the launch gate must record the margin it opened on (C-10 opened at
  0.02 GiB) — a gate that opens on poll 2 with 0.02 GiB margin is a gate that
  will fail the floor. With (i)–(iii) it is worth a VERIFICATION_CHARTER §2e
  sibling clause; goes to Sanaa's desk as a draft after their attempt-2 prereg
  lands and is audited.

**Live jobs:** no solver compute owned by this team. **Three lanes live (the
cap), each dispatched with a predicted cost:**
1. **Audit pass 7 — dafoam W4 O2 re-buy (`5a93f6ee`, PENDING, C-15) + B3
   decomposition (`b5ff25d7`/`bb5088c4`/`52c26ec1`)**; the O2 `PENDING`
   question (queue state vs softened NOT A RESULT for a cap-stopped run) is the
   sharp item. Predicted ≤ 1.0 core-min, zero solver.
2. **Audit pass 8 — Ling2016 TBNN GPU arm (`e8309b6c` freeze, `11f93da6`
   code, `353925c7` NOT A RESULT, C-16 10.7054 GPU-h = $8.62 + 7.88 GPU-h
   idle waste)** — the lab's first GPU run: freeze order, comparator-own
   output, console-priced vs price-list cost basis, per-item sign-off
   citation (GPU spend is outside the blanket), instance-stopped evidence.
   Predicted ≤ 1.0 core-min, zero GPU-h, zero solver.
3. **Stamp-vs-committer-date check, `scripts/check_stamp_vs_commit.py`** —
   the codification the chief assigned this team (one skew model shared with
   `check_harness.py`'s 10-min STALE tolerance; forward tolerance chosen from
   the measured distribution over 300 commits; six planted controls incl. the
   real bd3edfe8/21:38Z instances; report-only sweep at HEAD). Predicted
   ≤ 3.0 core-min. **Diff read by this supervisor before belief or wiring.**

**Standing items (unchanged state unless noted):**

| item | state |
|---|---|
| **VM2026R1_Fluids** | D-6, with Sanaa — NO AGENT TOUCHES EITHER COPY. Root copy 123 files / 2.5 GB; papers copy dead at 10 files / 26 MB. Ruling memo `docs/VM2026R1_FILING_ANALYSIS.md` (option A recommended). Nothing graded |
| **Ansys manual** | tracked PDF, no `.txt` sidecar (R8); basename violates R8 pattern; rides in the D-6 memo §4. Sidecar lane of 08-23 died; sidecar still absent — VERIFY, re-dispatch when a lane frees |
| **`GATE FAIL` vs bare `FAIL`** | D-5, with Sanaa; 3 bare cells (V5:1070, V14:1080, V15:1081); instrument D472 believed |
| **Comparator freeze audit** | instrument D471 believed; 45 graders 10/7/2/4/22/0; `analyse_t1b_L4` docket figure STRUCK; 87/156 markers without `finished_utc` relayed to heat-transfer |
| **Six standing audits** | all re-run 08-23 (`c5a9d4c7`, `f14fca9c`, `876a9ec1`, `af16ceef`, `69df4876`, `e3f3b521`); EXTERNAL_REFERENT's screen still uncommitted (own-audit defect, queued) |
| **Ten absent tracked files** | mechanism established above; disposition with the chief |

**Cross-team gate audit — targets after this session's dispatch:**
- IN FLIGHT: pass 7 (W4 O2 + B3), pass 8 (Ling2016 GPU).
- QUEUED, verdict-bearing chains now graded or landing: heat-transfer **T3
  ext1 `R_f`** (finished 14:53Z, ungraded, owner = peer session's
  heat-transfer); **T1b L4 re-run** — `R_300k_x` lands today (73076/80000 at
  15:52Z), `R_100k_x`/`R_30k_x` before 08-26 — the four PASS rows on
  DIVERGENT/STAGNANT triples (D440) are the sharpest live Roache instance;
  closure **Kaandorp** close-out (driver complete, this session's closure);
  dafoam **A3** (`5d8e2f52`/`97a54c07`, C-9/C-10 drafts awaiting RESULTS);
  cfd **E4a** (`628e29c4`, frozen, nothing launched — owner heat-transfer's
  peer).
- STILL OPEN from earlier passes: T10a's 6 UNMEASURED controls; the 4
  ungraded pooled `T1_runs` UNFROZEN rows; A6 N-D21 caveat CLOSED; A4 CLOSED;
  Wu2018 CLOSED; W4 M1+M2 §14 defect remedy owed by dafoam; T9aH two owed
  items (heat-transfer).
- INSTRUMENT QUEUE (this team): EXTERNAL_REFERENT screen rebuild-and-commit
  (or strike its bucket figures with a dated note); D473 declared-mode
  exercised on a real rung once any prereg carries the block; Ansys sidecar.

**Cost calibration (rule 12):** in force; this session's rows C-19 (pass 6);
passes 7/8 and the stamp check each land their own row at completion with the
predictions above as the comparator.

**On Sanaa's desk:** `RESULT_PRIORITY_CHARTER` v0.5 orderings; D-5; D-6 (memo
ready); D473 adoption + §3 clause (11.4%/24.1% replay); the §30(a)/(b) FS5
standards recommendations; the memory-limb rule draft (after dafoam's
attempt-2 prereg); the ten-absent-files restore (via the chief).

**Blocked:** VM2026R1 grading (D-6, Sanaa). Nothing else.

**Next actions** for whoever picks this up: read the three lanes' returns as
diffs/records personally (passes 7/8 → BELIEVED or not, with numbers; the
stamp check → diff read, then wire into the audit sweep); then dispatch, in
order, the T1b L4 audit as each arm lands (Roache triple gating is the
question), the EXTERNAL_REFERENT instrument rebuild, and the Ansys sidecar
(L-144 title-page verification). Every dispatch carries a predicted cost.
