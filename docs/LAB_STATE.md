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
| **GPU-blocked reproductions now unblocked for pre-registration** | Closure supervisor to pre-register DPM, Bae, Lozano-Durán, Beck (and Ling2016 TBNN GPU training) with GPU-hour cost bases; nothing launches before Sanaa signs each | chief, 2026-08-22 | ~~**DISPATCHED**~~ **2026-08-24:** Ling2016 TBNN GPU arm 1 graded **NOT A RESULT** at `353925c7`; arm 2 prereg in drafting under her *"i approve of everything"* with per-item costing still required (rule 9: a blanket is not a per-item read; GPU spend needs its console-priced GPU-hour cost basis) |
| **R3 = SpaRTA** | The closure line rebuilds on SpaRTA-class, Sanaa's pick from the R2 shortlist | Sanaa 2026-08-21, verbatim *"R3: Sparta"*, appended to `docs/closure/R2_SHORTLIST_MEMO.md` | **DECIDED** |
| **R4 approved** | Sanaa said *"R4 approved"* in the same message | same | **APPROVED**; R4 build **OPEN, no verdict** |
| **R4's CPU-minutes have first call on capacity** | named in the thermal directive's own header | Sanaa 2026-08-22 | **IN FORCE** |
| **SUBMISSIONS PARKED** | Nothing is sent, filed, uploaded, registered or posted anywhere. Sending is Sanaa's alone | Katie 2026-08-07; `GOALS_AND_PROPOSALS` §8, `CLOSURE_MODELLING` §19, `DAFOAM` §10 | **IN FORCE**, indefinitely |
| **Blanket compute approval** | Runs above the $25 pre-authorisation are blanket-approved, **and are still costed in their pre-registration** | Sanaa 2026-08-21, *"all the teams have my approval for everything"* — **owner-stated, chief's session record** | **IN FORCE** |
| **GPU quota GRANTED, no GPU attached** | AWS raised "All G and VT instances" in us-east-2 to 8 (vCPUs; one g6.2xlarge/g5.2xlarge or two xlarge). No GPU on this box. `BLOCKED-GPU` retired as a standing verdict. **GPU spend sits OUTSIDE the 2026-08-21 CPU blanket**: each GPU run needs a console-priced GPU-hour cost basis and Sanaa's per-item sign-off. Case-number link (178725840000468) is an inference, unconfirmed | AWS message pasted by Sanaa 2026-08-22, recorded verbatim in `docs/GPU_CAPABILITY_STATE.md`; rule 12 amended at e0cf8f0c | **IN FORCE.** ~~gpu1 running~~ **2026-08-24: gpu1 STOPPED by Sanaa** (her words: *"also i stopped that instance"*); **driver self-shutdown APPROVED as a standing GPU mechanism** (her words: *"GPU shutdown suggestion: yes approved"*) — every GPU driver stops its own instance when its run ends |
| **ansys-verification team created** | A sixth standing team on Sanaa's directive: Fable supervisor, 2 Opus lanes (5 and 4.8), 2 Haiku lanes (pull code / watch logs only); reads the Ansys Fluid Dynamics Verification Manual first; runs its cases as pre-registered lab verdicts in the lab's own solvers; keeps `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (only PASS rows are credentials); updates LESSONS / NUMERICS / charters with what it finds; the verification team audits it. Lane cap 4 is her explicit exception to §8's 3 | Sanaa 2026-08-24, verbatim in `docs/charters/ANSYS_VERIFICATION_CHARTER.md` §1; agent definitions in `.claude/agents/ansys-*.md` take effect at the next session start | **IN FORCE**; first-fill section `## ansys-verification` below |

**Lab-wide live compute:** 12 single-core solvers, all `buoyantBoussinesqSimpleFoam`,
all owned by heat-transfer. At $0.0513/core-h that is **~$0.62/h** (c7a.4xlarge at $0.0513/core-h, owner-stated) while all 12
run. No other team has anything on the box.

**On Sanaa's desk, aggregated:** the T10a view-factor defect as upstream candidate
#4 (filing is hers); **K2a rack row module, awaiting her approval**; four DAFoam upstream defect classes, all `NOT FILED`; the
`RESULT_PRIORITY_CHARTER` orderings (v0.5 draft, awaiting her ruling); ~~the
`GATE FAIL` vs bare `FAIL` ledger-vocabulary conflict (referred, unruled);~~ (D-5
CLOSED 2026-08-24 under the chief's disclosed interpretation, see the rulings
below) and the
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
- ~~**D-3 … D-6 are with Sanaa and no agent acts on them.** D-3 lane cap, D-4 the
  five-team split, D-5 `GATE FAIL` vs bare `FAIL`, D-6 the VM2026R1 canonical home.~~
  **2026-08-24 — D-3 … D-6 CLOSED on Sanaa's words**, verbatim, given in reply to the
  chief's explanation of exactly these four items: *"yes it's approved by me. I
  ratify the six team structure. I apporve all actually"* (chief's session record;
  scope discipline: applied to D-3..D-6 ONLY, read onto no other desk item,
  submission or send).
  - **D-3 CLOSED** — the 3-lane cap per supervisor is standing law, with the
    ansys-verification team's 4 lanes (2 opus + 2 haiku) as her explicit exception,
    recorded in `ANSYS_VERIFICATION_CHARTER.md` §3 and the 2026-08-24 addendum at
    the foot of `SUPERVISION_CHARTER.md`.
  - **D-4 CLOSED** — the six-team structure is ratified in her words (closure,
    dafoam, heat-transfer, cfd, verification, ansys-verification). Earlier the same
    day the row had been narrowed to "open for her explicit word" after her
    *"Let's have an ansy-verification team"* made it six; that word has now been given.
  - **D-5 CLOSED under the chief's interpretation, stated as such:** her approval
    is read as approving CLAUDE.md rule 1's vocabulary as written — legacy ledger
    cells reading bare `FAIL` (3 known: V5:1070, V14:1080, V15:1081) are to be
    corrected to `GATE FAIL` by their owning teams by quote-and-strike, never
    rewritten. The interpretation is the chief's and is disclosed here so she can
    overturn it.
  - **D-6 RESOLVED** (see the next bullet), her *"I approve all"* confirming.
- ~~**D-6, board note — DO NOT TOUCH EITHER COPY.** `VM2026R1_Fluids/` at the repo
  root holds **123 files, 2.5 GB** (Fluent / CFX / Forte archives). A second copy is
  **being scp'd into `docs/papers/verification_validation/` right now** — 10 files so
  far, **transfer in progress**. Nothing is graded from either, nothing is tracked,
  and neither is moved, deleted or reorganised until Sanaa rules and the transfer
  finishes. A half-copied tree read as a corpus is a measurement of nothing.~~
  **D-6 RESOLVED 2026-08-24 by Sanaa's directive creating the ansys-verification
  team with exclusive ownership of the archives and the manual** — her words: *"I
  wanted a verification team to exclusively work on these verification cases."*
  The canonical-home decision is now the **ansys-verification supervisor's first
  action**, informed by the harness-build inspection in
  `ANSYS_VERIFICATION_CHARTER.md` §9 (root copy 123 files / 2.5 GB complete;
  papers copy 10 files / 26 MB, a DEAD transfer, 9 files byte-identical and
  `VMFL011B.wbpz` truncated at 327,680 of 670,152 B) and the verification team's
  memo `docs/VM2026R1_FILING_ANALYSIS.md`. **Until it rules, neither copy is moved
  or deleted.** Confirmed by her *"I apporve all actually"* of the same day.

---

~~**Section last written:** 2026-08-22T21:05Z by chief (ubuntu-fb) — GPU grant recorded, GPU pre-registrations dispatched~~

**Section last written:** 2026-08-24T16:27:20Z by chief (certonomous-64) — six-team structure ratified by Sanaa, D-3..D-6 closed, ansys-verification team created; written by the harness-build lane on the chief's instruction, stamp from `date -u` in the writing invocation
## closure

**Section last written:** 2026-08-24T16:24:03Z by closure-supervisor (this chief session's
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
file's 17:17:57Z mtime and its "posted to the supervisor" line. **Attribution RESOLVED:** `a56cc309` was written by the PREDECESSOR supervisor's grading lane, which survived its supervisor's death (the lane's own answer, 16:17Z); this session's 16:06Z lane found the addendum on disk 74 s later, wrote nothing, and re-graded independently — its findings landed as the supervisor's correction addendum at `8dd3f8bc` (four false cross-references D488→D492 / C-15→C-18, ids written ahead of their appends; CBFS TRUTH keeps 91 % of baseline `k` yet inverts the ceiling most — §4's k-collapse account does not cover the third case, diagnostic only; refined 08-22 cost figure 1.069×, frozen §7 0.578×). Exactly ONE grading addendum exists plus the correction. **Correction of record landed in `8dd3f8bc` §1 (docket row still owed):** D492's parenthetical says the lane's draft ids "D491/L-269 were taken by
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

**Note, 2026-08-24T16:19:53Z (chief's corrections, verified at HEAD; the lines above stand as written and are corrected here, not rewritten):** (1) **The D491 condition is MET — the D476/FS5 adoption lift is EFFECTIVE for a build launch.** Verification's supervisor believed pass 6 as its own verdict at `f536b114` (every load-bearing limb re-derived with its own code; §7 adoption block RELEASED; A3 stays GATE FAIL; §30(a) stays a recommendation to Sanaa). Scope unchanged: companion audit-side diagnostic only, never in `F`, `singular_value_ratio_first_to_last` not quoted. (2) **Attribution corrected:** the lane that landed `41774899` was THIS session's — dispatched by the predecessor supervisor minutes before it was killed at ~16:00Z, it survived its parent and reported to the chief; it was NOT the parallel session's. The 'parallel session's lane' wording in the D476 block above, in D491's docket text and in hazard (3)'s example is wrong on that item; the general hazard (two closure supervisors, check HEAD before dispatch) stands. The same survival pattern explains `a56cc309`. The docket correction row is LANDED as **D494** at `a15b48b9` (nothing owed). (3) D492 referral limbs (a) and (b): verification's RECOMMENDATIONS (binding versions Sanaa's) returned via the chief and are APPLIED as a dated addendum at `8322b7b2` — G0a PASS stands with the value cell now reading `0.0 (floor 4.0e-07; registered 1e-10 unresolvable at writePrecision 6)`, the same reading for §5/§6; the ten duct rows' verdicts STAND with the §2d label "freeze self-attested, no commit witness" after my own negative search for any out-of-git posting record (harness session log begins 08-23; no brief/dispatch record; first commit holding the prereg is the ten-file results commit `0ebc9d53` at 18:52Z; filesystem: prereg last write 17:17:57Z, first scored log born 17:21:55Z); the six CBFS rows are frozen-by-commit. Verification will spec `check_threshold_resolution.py` (prospective-binding). Nothing owed by closure.

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
session: Kaandorp re-grade lane finished (wrote nothing; findings landed by me at `8dd3f8bc`); D476 ruling lane finished (stopped
correctly, wrote nothing); read-only gpu1 lane (predecessor's) finished.

**Commits this session (supervisor):** `53517fae` D491 (D476 adoption ruling
docket row, D486 fallback disclosed); `961b0b3e` D492 + L-269 (Kaandorp records,
same fallback); `6ff8e65c` board; `8dd3f8bc` Kaandorp correction addendum (+85/0,
from the HEAD blob); `506dde36` board; `979dec7f` board note; `a15b48b9` D494 correction row; `887bad8b` board; `8322b7b2` Kaandorp verdict-surface addendum (+79/0); this board write. Lane commits verified and adopted: `a56cc309`
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
disk); Xiao2016_EnKF (forward model); Lozano-Durán 2023 (data + charLES); (the D476 lift's condition is MET at `f536b114` — no longer blocked).

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

**Section last written:** 2026-08-24T16:23:53Z by dafoam-supervisor (FOURTH session, spawned ~15:52Z 2026-08-24 by the chief at HEAD `eb2a534b`; the session-2 close-out addendum below is the parallel supervisor's and is untouched). *Stamp is `date -u` read in the commit invocation.*

**FOURTH SESSION — 2026-08-24, this supervisor. Territory split ruled by the chief 16:0xZ: curriculum D1 and W4 O2 belong to the parallel (session-2 lineage) dafoam supervisor; this session owns D460 sweep 1, A3 rung-3 attempt 2 and the dead third session's residue.** A D1 lane this session dispatched 90 s before the ruling was stopped by order before any launch, copy or commit — zero disk/git change, 0.00 core-min, verified from disk. **Worktree finding:** the three `MM`/`D` files in this territory (`curriculum_D1/PREREGISTRATION.md`, `B3/decomposition_np4/RESULTS.md`, `B3/decomposition_peak_rss/RESULTS.md`) are BYTE-IDENTICAL to HEAD (blob hashes `ce821840`/`af8f2e3c`/`0a67de0b` match) — shared-index decay (D486), nothing to land, index is the chief's; the worktree `docs/COST_CALIBRATION.md` and `docs/DOCKET.md` are BEHIND HEAD, inspected, untouched.

**D460 sweep 1 — VERDICT `PASS`, class CONDITIONING / DIAGNOSABILITY (§7 row 5), RESULTS `2cdb7448` (+`63ff87f4` id correction), calibration row C-22 at `f62ec7ed` (its subject line says C-18 — wrong, disclosed in RESULTS §7c, row correct).** The forward-AD primal's NaN does NOT survive removal of the GAMG stopping rule: F-SM (`libDASolverADF.so` loaded, IDWARP md5 `85f59e87…`) and the P-SM control both ran 10 iterations with zero NaN under `smoothSolver`/`GaussSeidel` on `p`. G0 10/10 strings identical to the frozen own-build GAMG references; `r = |cum_F|/|cum_P| = 0.968227` vs the GAMG pair's 10.029307 (band 2.0). Comparator sha256 `239c1764…` equal on disk and in the committed blob, exit 0, three plants read back. P1–P4 HIT (P3/P4 registered at 0.55/0.50), P5 MISS (`p nIters` differ by 219, not fewer than the GAMG pair's 2). **Supervisor-verified independently from both logs before the lane graded — agreement on every gated number.** Caveat carried beside the PASS (§5a): the ratio fell because the CONTROL's continuity error grew 17.4× — the ADF arm's rose 1.68× — so the mechanism is "both builds converge on each other at a worse absolute level under smoothSolver", not "the amplification collapsed". Cost 4.717 core-min charged of 20.0 (graded arms 4.700, attempt-1 waste 0.017 named), ratio 0.940 = two opposite errors cancelling (P-SM 2.56× — 97% of its 230 s wall was harness overhead a per-iteration basis prices at zero; F-SM 0.248× — the healthy branch of a two-branch max), $0.004033 derived. **What it buys D460: the upstream class is CONDITIONING (documentation + warning, opposite-polarity instance of `OpenFOAM-AD` #2), not AD correctness. Draft stays NOT FILED; readiness reassessment is the next zero-compute item; filing is Sanaa's.** Candidate records drafted in RESULTS §9 (2 lessons + 9b-ii, 2 numerics, 1 docket) — supervisor read, landing lane next.

**A3 rung 3 patched-IDWarp np=4, ATTEMPT 2 — pre-registration FROZEN at `606930b4` (1,067 lines, 9 files, zero compute; run root `P5-a3-rung3-patched-attempt2` asserted absent at 16:17:01Z inside the commit).** Supervisor review of the dead lane's proposal (committed in the same sha as the record of review): the 17.2 GiB limb in my own earlier brief REJECTED — derived from a partial peak; limb set from the shipped arm's complete peak (8.0 + 11.65 = 19.65 GiB); disposition 1 (wait for a quiet window, 6 h poll, expire BLOCKED at 0 core-min); price 51.8 core-min predicted / 176.0 ceiling, $0.0443 derived; comparator + guards byte-identical to `97a54c07` (asserted by `cmp` in the commit); 10 changed lines in `stage.sh`/`drive.sh` all listed (2 run-root, 1 limb, 3 window, 4 header) — 7 beyond R1's literal wording, disclosed. **Verification's review of the general rule (relayed by the chief after the freeze) — SOUND with three refinements — is being landed as AMENDMENT 1 BEFORE FIRST COMPUTE: limb re-derived from P11's registered UPPER band 15.0 (= the RSS ceiling) + floor 8.0 + co-tenant allowance 2.0 = 25.0 GiB; margin-at-open recorded; floor sampled at the guard's cadence. Launch authorisation follows the supervisor's read of that commit.** VERIFY at next write: amendment sha.


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
| `f62ec7ed`/`63ff87f4` | 2026-08-24 16:16Z | **FOURTH SESSION lane** — D460 calibration row **C-22** (subject line wrongly says C-18; disclosed) + RESULTS id correction |
| `606930b4` | 2026-08-24 16:17Z | **FOURTH SESSION lane** — A3 rung 3 patched np=4 ATTEMPT 2 pre-registration FROZEN, zero compute, + reviewed proposal committed |
| `2cdb7448` | 2026-08-24 16:15Z | **FOURTH SESSION lane** — **D460 sweep 1 GRADED: PASS, class CONDITIONING / DIAGNOSABILITY** (r = 0.968, G0 10/10, no NaN either arm) |
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

**Live jobs: none dafoam-owned (this session's reading; `docker ps -a` empty of dafoam containers at 15:57Z; one peer D1 container `d1_armO_…` seen by the rung-3 lane at 16:07Z — the parallel supervisor's).** Lanes this session: D460 (DONE), rung-3 attempt-2 prereg (Amendment 1 in work, launch withheld). Historical text of the third session's dispatch follows in its claim ledger above.

**Rungs lacking verdicts:**

| item | state |
|---|---|
| **A6 N=16** | COMPLETE at 8 of 9 — PASS, aggregate 1.0432%, zero sign flips (row 37). twist idx6 NOT A RESULT. **N=29 NOT RUN**; gate wording is Sanaa's choice (D464), as is the ~5 core-min ninth-component arm |
| **A3 patched column** | rung 2 MEASURED — PASS (degrades vs shipped, N-D18). **Rung 1 MEASURED 21:0xZ, dual reading AS REGISTERED, choice on Sanaa's desk:** per-component rule → **PASS (patched) / PASS (shipped)**, control NOT EVALUABLE; aggregate band → FAIL pending investigation, both arms — the frozen prereg registered the conflict openly and reserved the choice. Headline, supervisor-verified against both logs: **R1-P8b HIT — the rung-2 degradation is NOT a property of the patch**: same library, `shape[115]` 9.2084× worse at rung 2, **2.42× better at rung 1** (0.3826% vs 0.9273%), tracking the sign of the shipped error; R1-P9 split (shape[5] moved 9.09% away) weakens any uniform directional claim; FD reference bit-identical across all three pairings; 0 sign flips (rung 2 had 3). 49.06 core-min / $0.0419 derived. **Rung 3 NOT A RESULT — stopped by memory at 85 s**, 0 of 11 checkpoints, no claim in any direction, cap not raised, no second budget; structural finding, supervisor-verified: the registered gate (16 GiB) cannot protect the registered floor (8 GiB) for an arm peaking 9.2 GiB (16.0−9.2=6.8<8.0) — registration design defect, both numbers frozen, neither changed; 6.80 core-min / $0.0058 derived; **re-registration draft ordered (new item, own price, gate ≥ 17.2 GiB limb), review before freeze**. 399,360 campaign PENDING |
| **ADF primal non-reproduction (D460)** | **Sweep 1 GRADED — PASS, class CONDITIONING / DIAGNOSABILITY** (`2cdb7448`; block above). Novelty blocker CLOSED at quota (`73563d98`). **Open: filing-readiness reassessment (zero compute, readiness only — filing is Sanaa's); §9f judgement whether D460's frozen record gets a dated addendum on the §5a mechanism (supervisor's, pending)** |
| **B3 decomposition peak RSS** | **MEASURED — see the graded block above** (M0/M2a/M2b/M5 PASS; M3a/M3b/M4 GATE FAIL, falsified in the registered direction). Attempt 1 NOT A RESULT (21.0 core-min named waste, charged). RESULTS commit + old-record quantifying addendum with the lane |
| **W4 M1+M2 / O2 / O3** | M1+M2 recorded by session 2 (O0/M2/M1-D PASS, M1 PENDING). **O2 re-buy: adoption UNRULED — with the chief.** O3 BLOCKED on Sanaa's guard authorization |
| **A2 `CD/shape` PATCHED idx46** | caveat RECORDED (rows 34-35); adjoint-vs-FD-artefact NOT established (sweep 207-238 core-min, not bought) |
| **B3 Stage 4** | BLOCKED by construction — Sanaa's fork-adoption call |

**Two-row verdicts standing** (shipped / patched): A1 GATE FAIL / PASS; A2 PASS / PASS with the idx46 per-component caveat (rows 34-35), optimisation NOT A RESULT; A3 primal GATE REACHED, adjoint BLOCKED (399k) — sweep rungs 1-2 PASS, rung 3 GATE FAIL (conditioning) / rung 2 PASS (degrades — N-D18), other sizes PENDING; A4 PASS / PASS (patch immaterial; CD −7.478 %); A5 GATE FAIL / PASS; A6 BLOCKED (full) — N=16 GATE FAIL (shipped, superseded reference) / **PASS at 8 of 9, aggregate 1.0432%, twist idx6 NOT A RESULT** (patched, fixed reference; rows 36-37). B2 PASS; B3 BLOCKED / PASS.

**Next actions (fourth session):** (1) Land D460's §9 record candidates via `append_record.py` (numbers re-derived at commit: L-267+, N-D28+, D490+ — VERIFY). (2) Rung-3 attempt-2 Amendment 1 → supervisor check-4 read → launch under its own 6 h gate poll; BLOCKED expiry is a registered outcome. (3) D460 filing-readiness reassessment at zero compute (readiness only). (4) §9f addendum judgement on D460's frozen record. (5) Board + report at each. Curriculum D1 / O2: NOT this session's — parallel supervisor.

**On Sanaa's desk:** **NEW (2026-08-24) — D460 sweep 1 PASS narrows the upstream class to CONDITIONING; the D460 draft stays NOT FILED, filing hers.** **NEW — the A3 rung-1 §4 rule choice** (per-component PASS vs aggregate-band FAIL-pending-investigation; the frozen prereg registered both readings and reserved the choice as a gate-threshold reinterpretation; archived-row consistency argument recorded as context; verification supervisor to be consulted via the chief). **D464 — the N=29 gate reading** (charter-verbatim NOT MET vs subset-complete GATE REACHED; the gap is one ~5 core-min arm). **R11 adoption evidence is two-sided** — A3 rung 2 measured the patch degrading; adoption is case-dependent, her call. **MemAvailable floor 12 GiB** ruling. **Five upstream defect drafts, all NOT FILED** (D-A/D-A2, D-B/D-B2, D-C, D-E + the ADF candidate `757eccf0`) — filing is hers alone. **B3 Stage 4 fork-adoption.** The near-zero sign-flip-under-a-passing-norm class (A1 idx6, A5 idx16, A2 idx46). **`DAFOAM_CHARTER.md` §13 enforceability PROPOSAL** (v1.0c, unratified). **O3 memory-guard mechanism authorization** (session 2's escalation, still open). **EXPERTISE_CURRICULUM ratification asks** (D479, §6 of the file).

**Blocked:** B3 Stage 4 (Sanaa); A6 N=29 verdict wording (Sanaa, D464); A6 full-size rung (unchanged); O3 (Sanaa, guard mechanism); ADF filing readiness — novelty blocker CLOSED, characterisation sweep 1 DONE (PASS), readiness reassessment pending; rung-3 attempt 2 — launch withheld pending Amendment 1 verification, then gated on MemAvailable.

**⚠ Integrity flags on frozen records, none quoted from:** `A1_naca0012_incompressible.md:167-172` (refuted mechanism, zero strike); `A5_ubend_internal.md:194-196` (in-band set mismatch); `A2/grading_confirmation/RESULTS.md` §1 ("no sign flip anywhere in A2") falsified at PATCHED idx46.

**Untracked in territory, inspected not deleted:** `cases/dafoam/patched_build/team/DALinearEqn_kspopts.patch` and `_subpclu.patch` (uncommitted build artifacts, provenance owed a check); the shared index still stages deletions of the A3 rung-3 files whose worktree copies exist — L-223 shape, **the chief's call, untouched**.

**Shared-board rule in force (chief, 2026-08-22):** `docs/LAB_STATE.md` is never written in the shared worktree. Each board commit rebuilds from `git show $H:docs/LAB_STATE.md`, replaces only `## dafoam` (`scripts/lab_state_section.py --team dafoam --rev $H --out <scratch>`), stages by `git hash-object -w` + `update-index --cacheinfo` in the private index, and the diff-tree must be confined to this section; before every board commit, diff this section at the captured rev against the section file being staged, and read that diff. Carried in every lane brief.

**Record-append rule in force (chief, `0286bb2a`):** every append to `DOCKET.md`, `LESSONS.md`, `NUMERICS_KNOWLEDGE.md` goes through `python3 scripts/append_record.py` (merge form) with `scripts/check_record_reconciliation.py` run BEFORE the edit. Carried verbatim in every DAFoam lane brief.

**Charter:** `DAFOAM_CHARTER.md` **v1.0c** (2026-08-22) — the §13 enforceability PROPOSAL is unratified and awaits Sanaa.

**Images:** `dafoam-idwarp-rot:v1` (only image carrying the rotation patch, md5 `85f59e87…`), `dafoam-subpclu:v2` (PCLU), `dafoam-kspopts:v1`, `dafoam-team:v1` (`0b3c94c33a15`, both patches, ends `USER dafoamuser` → `--user root` for bind mounts). *The hash is the identity; the version string is not.* F6 series under `cases/dafoam/` is plain `simpleFoam`, not DAFoam work.
## heat-transfer

**Section last written:** 2026-08-24T16:27:19Z by heat-transfer-supervisor (the
session holding T3 ext1, T1b L4 and D477 since the chief's redirect
2026-08-24T16:00Z). **Two heat-transfer sessions write this one section
and overwrite each other by construction** — `1a634bb2` (16:04Z, the
curriculum session) replaced this session's `d145cd22` wholesale. Until the
chief rules on single ownership, this session carries the curriculum
session's state VERBATIM under the sub-heading at the foot; the curriculum
session is asked to do the same for this session's rows. Earlier history
condensed: `eb2a534b`, `450735c1`, `b84c43d3`.

**Claim ledger — this session:** T3 ext1 close-out (LANDED `3dd28411` +
`398dfb3d`), T1b L4 completion + grading (watch LIVE), D477 restore per
the chief's ruling (lane LIVE). Curriculum items (E4a, E4a2, …): the
parallel session's, nothing launches from here.

### T3 — ext1 RE-GRADED 2026-08-24: NOT A RESULT 4/4 at gate (1) (`3dd28411`)

- **8/8 cases under the two-segment strict rule** (`mark_done_t3_ext1.py`,
  both `End`s, `20000 + ext1 ExecutionTime == endTime`, first ext1
  `Time = 20001`, age guard vs `0/T` and `STATUS.<case>`); `R_f` finished
  2026-08-24T14:53:19Z, 24 h 1 min ahead of the contended-basis ETA.
- **Frozen comparator `analyse_t3.py`** (sha `f41c544d…`, byte-identical to
  the §11 blob, verified by two lanes), exit 0, planted zero 1.234e-03 K
  read back and passed. `gate_t3.json` sha `8e766cd5…` (15:58:44Z).
  **Tally PASS 0 / GATE FAIL 0 / NOT A RESULT 4 / BLOCKED 0; 0 of 4
  graded.** All four rows fall at gate (1): `R_c` is in a limit cycle at the
  80 000 cap (rel ΔT 4.83e-02) — prereg §11's registered alternative; the
  rung says so and does not average.
- **What changed in cause:** `R_m`, `R_f`, `P_m`, `D_m`, `O_m` CONVERGED
  (`R_f` 9.68e-08 / 7.80e-08); `W_m` still outside at 1.409e-06 after
  60 000 more iterations (P1's exposed clause HELD); St ladder monotone in
  mesh for the first time; G3/G4 DIVERGENT→STAGNANT (p 0.23 / 0.22); **G2
  `x_peak/H` CONVERGING (p 4.304, GCI 0.0188 %, RE 6.1403) and NOT A
  RESULT anyway** — gate (1) fires first (rule 5, in the only direction it
  allows). `R_f` heat balance 8.234 % → 0.000393 %: amendment §4's
  non-convergence reading is now a measurement (P2 HELD). P3 primary clause
  HELD / secondary FALSIFIED by G2; P4 HELD.
- **Cost (C-23):** 4 798.05 core-min = 79.968 core-h = **$4.102 derived**
  (not measured) vs $4.08 registered = **1.005x — two cancelling errors**
  (no fixed startup term: W_m/D_m/R_c 1.40–1.62x; a 5-min contention window
  extrapolated across a 45-h critical path: `R_f` 0.653x of its ETA). Waste
  nil; stop threshold reached 17.9 %. Rung total $6.171 = 24.7 % of $25.
- Records: T3_RESULTS §14, T3_EXT1_AMENDMENT §15, index + directive rows
  (`3dd28411`); C-23, **D495** (fourth level `R_ff`), L-272 (`398dfb3d`) —
  ids re-derived at commit from the HEAD blob (C-16→C-23, D491→D495,
  L-269→L-272 had all moved). Supervisor's own checks done, not relayed:
  `3dd28411` read as a diff (11 885 of 11 896 deletions are the JSON
  regeneration; 8 `endTime 20000;` lines; 3 living rows; state moves in the
  JSON are exactly 9× NOT_CONVERGED→CONVERGED, 2× DIVERGENT→STAGNANT, 1×
  OSCILLATORY→CONVERGING); G2 order recomputed from e21/e32 = 4.30.
- **D495 — CHIEF RULING: NOT AUTHORIZED NOW.** 150–200 core-h, $8–10
  derived, 6.4–8.4 days serial; wall binds, H-2 puts T5/T8/T12 ahead, and
  two obstacles a fourth level does not solve remain: the Vogel & Eaton 1985
  primary (Sanaa's desk) and the **δ99/H inlet-window miss (0.668–0.671 vs
  [0.80, 1.35], prereg §4.4)**. Costed option on Sanaa's desk; revisit when
  the primary arrives. An inlet-window diagnosis arm is a candidate only —
  not pre-registered, not priced, not started.
- Left uncommitted, disclosed in `3dd28411`: seven `T3_runs/*/log.checkMesh`
  (a 2026-08-21T21:27Z checkMesh re-run, pre-ext1, header-only, unattributed).
- Provenance disclosed in §14.2: the marker and comparator were run by the
  parallel session's lane at 15:58Z before the 16:00Z redirect; this
  session's lane corroborated (six hashes, dry-run 8/8 at 16:09:32Z,
  `gate_t3.json` byte-identical) and did not re-run the comparator.

### Live jobs — T1b L4, reading 2026-08-24T16:02:14Z (lane, `date -u` in the invocation)

Three single-core `buoyantBoussinesqSimpleFoam`, endTime 80 000, all 99.9 %
CPU, cwd confirmed by `readlink`. **Do not touch them.**

| pid | cwd | iteration / endTime | rate (checkpoint mtimes) | ETA |
|---|---|---|---|---|
| 442445 | `T1_runs/R_300k_x` | 73 369 / 80 000 | 27.2 it/min | **~2026-08-24T20:06Z** |
| 450274 | `T1_runs/R_100k_x` | 60 877 / 80 000 | 19.5 it/min | ~2026-08-25T08:22Z (upper bound) |
| 488219 | `T1_runs/R_30k_x` | 55 524 / 80 000 | 17.5 it/min | ~2026-08-25T15:22Z (upper bound) |

Completion watch on `R_300k_x`: background until-loop, 10-min poll, cap
2026-08-24T23:00:52Z; marks under `mark_done_t1b_L4.py` (byte-identical to
HEAD, `f75f4a81…`; `analyse_t1b_L4.py` `9698adb0…`), does not grade. Grading
waits for all four x-cases DONE (the comparator refuses partial pools by
design). **Deadline guard: no `STATUS.R_{30k,100k,300k}_x` by 2026-08-27 is
a finding.** Disclosed slip: the watch lane's `--help` probe ran the marker
once in real mode at 15:59:47Z (no argparse) — rewrote `DONE.R_10k_x`
byte-identically, touched nothing else, running cases unreachable by it.
All four `R_*_x/log.checkMesh` worktree diffs are the runner's at-launch
`checkMesh` (header lines only, `points: 421275` both sides) — inspected,
not reverted. Projected `R_300k_x` cost ~70.6 core-h vs 59.0 registered
(1.20x, projection not a row); L4 owes its calibration row at completion.

### D477 — chief's ruling 2026-08-24, EXECUTING (lane LIVE)

Triage (read-only lane, zero compute) bounded the eight K2bP
`HEATBALANCE_{400,800}` clearings to **2026-08-18T04:24:55Z → 04:43:00.8Z**
(`fa2c8bb0` commit; case-directory mtimes) — a first-pass 800-iteration
artifact set superseded by the 5 000-iteration in-place re-run; D390 is the
right mechanism class, mis-mapped onto the HEAD blobs (a311d872's "never
existed" premise falsified by the frozen tree; 0c742c66's implied "D390
does not apply" also wrong). `K1_STANDING_THERMAL_CHECKS.md`: bounded
2026-08-17T18:59:00Z → 2026-08-18T04:07:19Z (L-122's own porcelain reading),
nowhere on the box, mechanism NOT identified; verification's independent
reading (`f536b114`) supports "never written to this worktree" (sole file of
its commit, never deleted by any commit, 8 prunable worktrees into the wiped
scratchpad). **RULING:** restore all nine from HEAD by `git show` (zero HEAD
bytes), two dated provenance notes in the K2bP case dirs, D477 in-row note
with both bounds and the corrected reading, **K1 provenance stays OPEN**;
`scripts/mutation_harness_known_test_names.py` is verification's, outside
this ruling.

### T9aH — GRADED 2026-08-23 (`359cccfb`, `b698dfc3`); rung table

T9aH: frozen path NOT A RESULT x3 + FR3/FR4 GATE REACHED exactly as §4.1
registered; new instrument H1–H5 PASS (worst 3.183e-12 K), null arm misses
2.41e+05x — interface-scheme cause CONFIRMED; $3.053e-04 derived; A.8
CLOSED. Open cross-rung question (verification/chief): `Gauss harmonic` as
the registered CHT default.

| rung | verdict |
|---|---|
| **T1c** | GATE FAIL 3/4; L4 row NOT A RESULT |
| **T1b** | PASS x4 frozen comparator but every triple DIVERGENT/STAGNANT (D440); no mesh-converged value until L4 lands (10k DONE, 3 running) |
| **T1a** | BLOCKED — no band from one correlation |
| **T3** | **NOT A RESULT 4/4 after ext1 (`3dd28411`)** — gate (1), `R_c` limit cycle; G2 triple CONVERGING but ungradeable; primary NOT OBTAINED; D495 fourth level NOT AUTHORIZED NOW |
| **T9a** | GATE FAIL; T9a-D REPORTED (D454, L-227); T9aH GRADED — cause CONFIRMED |
| **T10a** | GATE FAIL (closed); T10a-R GATE FAIL 5/4/0 (D466, L-244); T10a-VF REPORTED (D457, L-231), upstream candidate #4 NOT FILED |
| **T4** | half-open — graded rows need closed ASME primaries |
| **T5** | PRIMARY HELD; prereg draft unfrozen, 12 INTERPRETATIONs on Sanaa's desk — **next on the H-2 spine** |
| **T2, T6–T8, T9b/c, T10b, T11–T13** | not started; T6/T12/T13 and likely T7, T9c over $25 |

**F14 / DC-cooling:** K0c PASS; K0cS/T/X GATE FAIL; K0b BACKED x2; K0cG GAP
D470 (cost repaired `878f1556`, 1.350x); K0cQ GAP D468; K0cR/K0cP token
findings; K2e/KV1 GAP D469; K2b cost VOID; K2a on Sanaa's desk. Disk truth
`d4597293`. D477 as above.

**Next actions:** 1. `R_300k_x` lands (~20:06Z) → mark; `R_100k_x`,
`R_30k_x` (2026-08-25) → mark → `analyse_t1b_L4.py` → four (m,f,x) triples
under the amended Roache rule → calibration row → commit. 2. D477 lane's two
commits → board. 3. T5: on Sanaa's INTERPRETATIONs; freeze before any case.
4. D468 / D469 — separate, separately pre-registered, not unilateral.
5. Chief's ruling on single ownership of this board section.

**On Sanaa's desk:** Vogel & Eaton 1985 purchase (~25–40 USD, unconfirmed)
— T3's gate-(3) blocker and the D495 revisit trigger; **D495 `R_ff` as a
costed option (150–200 core-h, $8–10 derived)**; T5 INTERPRETATIONs; T1b L4
cost 10.54 USD registered vs ~5 approved (running, on the record); upstream
candidate #4 (NOT FILED); UPSTREAM_QUEUE #4 numbering; K2a; T10aR prereg
ADDENDUM 2 (on disk, unfrozen, uncommitted — no agent re-routes it).

**Blocked:** T1a; T3 graded rows (gate (1) ladder, then gate (3) primary,
then the inlet-window flag); T4 (ASME primaries).

**⚠ D389 open and deliberately unrepaired** (S13 mean-normalisation, ~24x
looser than it reads; moves verdicts across K0c/K2e/KV1). Owner: chief.

### EXPERTISE_CURRICULUM — the parallel session's state, carried VERBATIM from the board at HEAD (their words, not this session's; they own it)

**EXPERTISE CURRICULUM RATIFIED (2026-08-23, Sanaa via chief, verbatim in
Amendment 1 of `docs/campaigns/T-family/EXPERTISE_CURRICULUM.md`, committed
`fe409422`; proposal recorded D474; ratification docket row D483).**
Ratification read under rule 9: approval of the proposal **as written** —
pre-authorised-class items proceed, each under its own frozen, committed,
costed pre-registration; **E2, E3-b, E7-3D, E12-build remain NEEDS COSTING
and return to Sanaa costed before launch**; rule-15 title verification
before any source is adopted; VM2026R1 notes still PENDING D-6.

**E4 stage (a) — GRADED 2026-08-24T16:16:26Z: rung verdict NOT A RESULT (D493, ledger C-21, lessons L-270/L-271).** Frozen `628e29c4` before any case; 5/5 built, run serially, strict rule 5/5; frozen comparator exit 1 (graded), planted-zero held. **I1 PASS** (BC equation residual 3.794e-11 m²/s² vs 8.1e-8), **I2 PASS** (7.1e-10), **P1 PASS**, **Z1 PASS**; **R1/G1/G2/N1/D1 NOT A RESULT** — the registered bit-identity convergence gate cannot be met by iterates creeping ~6e-11 relative at writePrecision 12 (residuals 1e-10…1e-14); no order/GCI quoted; the §1.5-agreement diagnostic is held unconverted. Cost registered $0.033 → actual $0.0024 derived, **0.0748×**, misprediction: cross-solver-class basis (13.6×), no waste. **Successor E4a2 in design** (lane; same physics/rows/intervals, ONE re-registered thing — a bounded convergence gate with a derived floor, plateau reading, longer endTime, measurable first-crossing); freeze committed before any case, costed on E4a's measured basis. Stage (b) still on Sanaa's desk. Lab-wide propagation proposed via chief: solver class of every cost basis stated (L-271).

T10a-R (their 2026-08-23 grading, D466, L-244) is carried in the rung table
above; their full text is at `1a634bb2`.
## cfd

**Section last written:** 2026-08-24T16:24:49Z by cfd-supervisor (third owner session, a re-spawn after the ~16:00Z API kill; nothing from the killed predecessor reached disk — verified). Stamp is `date -u` read in the committing shell invocation.

**Last commit:** `290fcff2` (F4 SIGFPE step-0/1 prereg AMENDMENT 1 + reader fix, +449/−3, two paths, post-commit-verified). Earlier this family: `0bbac521` (F4 prereg FROZEN), `f89aa7b4` (cfd COST_CALIBRATION rows C-4/C-5), `7a96cf54` (OPENFOAM.md re-scope), `1135e3c5` (F4 §8 source-read), `3b9bcf31` (F7a R0), `b8fe7eea` (L4 diagnosis results).

**Live jobs:** F4 step-0/1 execution lane **AUTHORIZED and dispatched** ~16:35Z — build of `rhoCentralFoamBoundedDiag` + `rhoCentralFoamInletUpwindDiag`, control C0 twin-run, then `step0_instrumented/` and `step1_inletupwind/` under `verification/runs/F4_runs/swbli_cylflare/`, each single-rank under `timeout 360` (= the 6 core-min per-step cap), envelope ≤15 core-min = $0.0128 derived. pids/iterations: **VERIFY** — re-derive from `<STEP>/LAUNCH.txt`, `<STEP>/RC.txt`, `ps`. Load at authorization 5.40/4.41/3.81 on 16 cores (16:08:40Z); the lane records the load at launch beside the basis (directive (a)). Do not touch heat-transfer's three T1 L4 `buoyantBoussinesqSimpleFoam` arms (pids 450274/488219/442445) or dafoam's Docker tasks.

**Supervisor personal checks done this session (2026-08-24):**
- **F4 prereg `0bbac521` + reader skeleton — READ AS A DIFF (check #1) and commit verified (check #4).** Three defects found and amended pre-compute at `290fcff2` (§13, +362 at the foot, zero lines renumbered; reader +87/−3): (1) reader `RE_SIGFPE` matched the universal OpenFOAM banner `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).` — 100 % false-positive rate measured on clean F5/F7 logs; replaced by the `Foam::sigFpe::sigHandler` frame + `SIGFPE_RC = 136` primary; (2) §7.3 required `1.3e-05/`, which `purgeWrite 3` deletes after the 5.2e-05 write (the frozen file's own §11.6 contradicted §7.3) — now "any numeric time dir with all seven fields newer than `0/T`"; (3) §8.3 referenced freestream, but the four clamped cells are inlet-face owners (stride 120, exact from `polyMesh/owner`) and the corner face's profile |U| is 21.78 m/s (−98.3 %); 54/110 inlet faces exceed the 5 % band at t = 0 — reference is now the cell's own inlet-face profile value when inlet-adjacent, freestream otherwise, stated in the record. Bands, caps, labels unchanged. Disclosed: p/(RT) at the freestream face is 2.16 % below Table I ρ∞; the archived crash's rc is unrecoverable (no rc in the `.done` sidecar). §10.4's "COST_CALIBRATION not tracked" condition was false already at freeze (`ef6a9082` predates `0bbac521` by 9 min) — operative clause stands. **Grading bodies are still `NotImplementedError`; their diff is the next personal read before any F4 number is believed.**
- **`verification/runs/F7_runs/r0_implied_front_definition.py` — READ (check #1).** Sound for the relayed numbers: positive control reproduces the published six-station Z column within 0.02 (measured |δ| ≤ 4.25e-04) and refuses otherwise; the fixed-definition sweep is one rule at all six stations. **§7.3 numbers cleared for relay:** α = 0.65 floor-row contour collapses the mean code-to-code offset +23.36 % → +0.70 %, shape residual ±7.3 % max. One labeling defect: toe-width diagnostic computes 0.95·h_max but prints/keys "0.995" — not among the relayed numbers; hygiene lane checking whether the spec cites it (addendum if so, script untouched).

**DPW8_V2 L4 diagnosis — GRADED 2026-08-23 under prereg `99f939ee`, record `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md` @ `b8fe7eea`.** Arm A (relaxation only) **BLOCKED** — SIGFPE at iter 182/600, rc 136, triaged: the crash is the phenomenon (Cd/Cl at iter 181 = 1.6026e+37 / 8.0168e+37, zero bounding-k lines). Arm B (linearUpwind→upwind) **NOT BOUNDED** — B1–B4 all FAIL (bounding k @ 136, max|Cd| 17,520.5, y+ 189.9). Map cell **PENDING**; **L4 stays NOT GATED**; L1/L3 PASS stand. Cost 21.5 core-min = $0.018 (reported-by-owner rate), under the 150 cap. Third lever = **D481** (needs its own costed prereg or the chief's word). L-255 on record.

**Open run families (states re-verified 2026-08-23; unchanged 2026-08-24 except F4):**

| family | state |
|---|---|
| **F4** | Step-0/1 prereg frozen `0bbac521` v1.0 → **v1.1 at `290fcff2`**; **launched 2026-08-24 (see Live jobs)**; result PENDING on the run + grading-body read. θ=32.5°/35° gate held. Bounded-run logs GONE from disk — the 4–32 % fractions are record-quoted, artifact-missing (VERIFY flag going into NOT_PASSING_REGISTER via the hygiene lane); Step 0 is the recovery path |
| **F5b** | Feasibility PASS (`F5bc_unsteady_statistics.md`); Physics/Gate rungs PENDING. **Physics prereg DRAFT in progress** (lane; not frozen, not committed, supervisor read before freeze). Trap: `F5b_cylinder_re100_act.json` is a different case |
| **F5c** | Effectively closed: headline withdrawn; 1.313 H was relaxation; Stage B never approved and moot |
| **R4 (Ahmed turn)** | Leg 2 n = 4/4, turn WITHDRAWN as a feature (`8f5bf878`); optional n = 7 needs the chief's word. Not closure's R4 |
| **F12** | PENDING; costed addendum `3f23c172` (383.5 core-min est., 1,300 cap); its eventual calibration row must name the 9.79× cross-solver spread; `rae2822_case9.py` 7200 s timeout must be raised at build |
| **F7a re-gate** | GATE FAIL +11.03 % max stands. R0 executed (`3b9bcf31`, 0 core-min); reader read by supervisor 2026-08-24 (above). R1a/b/c NOT authorized |
| **MODEL_FORM successors** | CLOSED as registered (n<3 refusals; hills family-convergence wall) |
| **DPW8_V2 L4** | see above; D481 open |
| **mbc_retry, uq_batch** | self-labelled ungraded; no action |
| **F5** | no 1e5/1e6 trees; re10000 mesh-only; record says do not climb to Re 5000/10,000; 3D rung is the informative next step |

**Closed, verdicts on record:** 4G, B52_RUNG6, D5_rsm, DMR, F2, F3, F8 (NO VERDICT is the result), F9, F11, FPE_DIAG, GEN_ALT (`verification/campaign/GEN_ALT_generator_matrix.md`), MESH_AUDIT, W1, W1_hump, W2_sparta, W3.

**Housekeeping 2026-08-24 (read-only lane, supervisor spot-checked):** the four WSL stale-instruction flags are **discharged** at `eb2a534b` (`HANDOFF.md:148/278`, `HANDOFF-BG2.md:43`, `HANDOFF-RACEGUI.md:106`, `DEMO_RUNBOOK.md:37/59`); residual `HANDOFF.md:111` covered only by the file-level prohibition — not cfd's file, flagged to the chief. `scripts/mutation_harness_known_test_names.py` (worktree-deleted, tracked) is **verification's** D348 instrument; no cfd code calls it; `check_absolutes.py:546` cites it — passed to the chief, nothing restored. cfd board section was byte-identical HEAD == worktree at 16:00Z (no worktree-behind-HEAD disease here). Nine commits `eb2a534b..41774899`, none in cfd territory; heat-transfer opened `verification/runs/T-family/E4_runs/` (inside their line). `COST_CALIBRATION.md` worktree copy is 23,937 B vs 38,661 B at HEAD — **never append from disk**.

**⚠ Structural fact:** run dirs under `verification/runs/` mostly carry no README/RESULTS/marker; **verdicts live in `verification/campaign/*.md`.**

**Standards:** `docs/standards/MESH_STANDARD.md` (v1.2, quality gates) and `docs/MESH_STANDARD.md` (grid families) are two documents, not two copies — do NOT merge; consistency verified 2026-08-23. `docs/OPENFOAM.md` re-scoped at `7a96cf54` (v2606 at `/usr/lib/openfoam/openfoam2606` is the only install). `docs/OPENFOAM_SOLVER_BUILD.md` dead paths fixed 2026-08-23.

**Next actions:** (1) F4 execution lane report → supervisor triage of any crash (check #2), then a separate commit implementing the grading bodies → **supervisor diff-read (check #1)** → grading → `F4_SIGFPE_STEP01_RESULTS.md` with the §10.4 cost close-out and one COST_CALIBRATION row from HEAD content. (2) F5b physics prereg draft → supervisor read → freeze commit → then the ~25–35 core-min rung. (3) Hygiene lane: F7a toe-width addendum if cited; NOT_PASSING_REGISTER F4 VERIFY flag + stale-path check; `mega-batch` driver paths report-only. (4) D481 third-lever decision — chief/next session. (5) Amendment class to feed a lesson at the next LESSONS append (re-derive max+1 at commit): a reader regex that matches a solver's own startup banner is a 100 % false-positive crash detector — assert non-match on the banner in every crash-detecting reader.

**On Sanaa's desk:** nothing from cfd.

**Blocked:** nothing currently identified.

**Case tree:** `cases/{committee-grids, demo-surfaces, hlpw6, mega-batch, tmr, unsteady-cylinder, valve}` dormant in git; `tmr` most open; `mega-batch` driver path broken (points into `demo-output/website/...` — stale paths of that shape are systemic in this team's records; treat as suspect until resolved). `models/tmr/**` is a documented FILING_CHARTER §3 exception: the rule was wrong, not the tree.

## verification

**Section last written:** 2026-08-24T16:22:51Z by verification-supervisor (stamp from
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
("Supervisor's own read of pass 6", `f536b114`) and ledger row **C-20**
(`7478536d`; 0.22 core-min vs 3–6 predicted, ≈ 0.04× — an earlier draft of
this section said C-19; C-19 is closure's correction to C-16). Relayed to the
chief. **Sequence confirmed:** closure lifted the §7 block at `41774899`
(16:09:48Z) on the pass-6 CANDIDATE with a self-executing reversal clause
(their A2.1 (v): void if the supervisor's read reverses any pass-6 finding);
my belief at `f536b114` (16:15:20Z) reversed nothing — **pass 6 BELIEVED ⟹
closure's Addendum 2 v1.1 adoption (companion as audit-side diagnostic only,
A3 unchanged at GATE FAIL) STANDS**; the two records agree.

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
  mechanism as D477's eight.** **RULED AND EXECUTED (chief, 2026-08-24, same
  ruling as D477's):** restored by `git show HEAD:<path> > <path>` in one
  invocation, index untouched, restored hash `5ec5a9ce…` == HEAD blob, status
  clean, zero HEAD bytes changed; recorded as dated §8 of
  `docs/FAIL_OPEN_GATE_AUDIT.md` (the audit whose §7 read it UNPARSED); done
  by the supervisor because the lane cap was full — disclosed. K1 and the
  eight are heat-transfer's, untouched; the mechanism reading goes to their
  D477 note via the chief. `check_absolutes.py`'s positive control is
  restored, not re-proven — re-proof joins the next FAIL_OPEN_GATE re-run.
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

**Kaandorp standards referrals (D492, `961b0b3e`) — ANSWERED as
recommendations, 2026-08-24 ~16:2xZ (binding versions Sanaa's; reads only,
≈ 0.1 core-min):**
- **(a) G0a threshold 1e-10 vs one-ulp floor 4.00e-07 (writePrecision 6):**
  the label **PASS is correct and stays** — frozen criterion `< 1e-10`,
  measured 0.0 exactly (byte-identical, md5 `ff95ccb5…`), and rule 5 lets a
  gate turn a PASS only into NOT A RESULT, which this is not. What must move
  is the CLAIM: the instrument floor travels IN THE VALUE CELL —
  `0.0 (floor 4.0e-07; registered 1e-10 unresolvable at writePrecision 6)` —
  not in prose 570 lines below the table and not as a seventh label (rule 1:
  honesty is carried by the value and its interval). A threshold below the
  instrument's resolution is an interval statement (UNCERTAINTY-DOCTRINE's
  numerical channel). INSTRUMENT: yes — a sibling
  `check_threshold_resolution.py` (not the freeze checker, whose job is
  time-ordering): for every registered numeric gate reading an OpenFOAM
  field, parse `writeFormat`/`writePrecision` and REFUSE (exit 2) when the
  threshold is below one ulp of the field's largest component; binding
  prospectively, report-only replay over the archive (D473 pattern); must
  fire on this record's §5/§6 if they are the same shape. Spec owed by this
  team.
- **(b) Duct rows solved 17:27–17:44Z, prereg's only commit `0ebc9d53` at
  18:52:18Z:** `check_comparator_freeze.py` **does not see this case** —
  population is `analyse_*/grade_*/score_*.py`, the grader here is
  `summarise.py` + a hand grade (A.2), and no `DONE.*`/`finished_utc` marker
  exists under the case; a coverage residual added to D471. Git evidences:
  prereg byte-unchanged since 18:52:18Z (blob `411b25f1…`, no amendment),
  but `0ebc9d53` is a TEN-file commit carrying PREREGISTRATION.md AND
  RESULTS.md AND the four scripts AND the LESSONS/NUMERICS drafts (2,063
  insertions) — the pass-2 Wu2018 shape exactly: first commit is the results
  commit, freeze self-attested ("posted to the supervisor"), no commit
  witness. RULING RECOMMENDED: six CBFS rows (solved 08-23) FROZEN-BY-COMMIT,
  nothing owed; the ten duct rows' verdicts STAND (criterion unchanged, same
  file graded both) but each duct row's verdict surface carries the §2d
  disclosure label pass 2 attached to Wu2018 — "freeze self-attested, no
  commit witness". Not NOT A RESULT (rule 5 is grid convergence; §2b/§2d
  give disclosure, not re-grade). Closure's §3 personal check — a posting
  time in a dispatch record or harness session log, cited by path — is the
  one fact that could upgrade the label to a witnessed freeze.
- **Ids-written-ahead (closure's D488/C-15 → D492/C-18, corrected
  `8dd3f8bc`):** taken as the second instance class for the stamp-check lane
  (spec extended in flight: ID-AHEAD limb, planted controls C7–C9); lesson
  candidate accepted as worded — "an id in prose before its append is a
  prediction, not an identifier".

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
| **VM2026R1_Fluids** | **HANDED OVER — VERIFY.** Chief's heads-up 2026-08-24 ~16:20Z: Sanaa has directed a SIXTH standing team, `ansys-verification`, owning `VM2026R1_Fluids/`, the Ansys manual and its sidecar, `docs/VM2026R1_FILING_ANALYSIS.md` and D-6; the harness commit was not at HEAD when this was written (sha awaited). Until that sha is read: NO AGENT OF THIS TEAM touches either copy, the manual, the sidecar or the memo; D-6 stands as written. After it: their verdicts are cross-team audit targets like any other from their first verdict-bearing commit. Root copy 123 files / 2.5 GB; papers copy dead at 10 / 26 MB — last reading 08-23, unchanged by this team |
| **Ansys manual** | **HANDED OVER with the row above — VERIFY.** The 08-23 sidecar lane died with its session; sidecar still absent (R8) and the basename still violates the R8 pattern; both are struck from THIS team's dispatch queue and belong to `ansys-verification` once its commit lands |
| **`GATE FAIL` vs bare `FAIL`** | D-5, with Sanaa; 3 bare cells (V5:1070, V14:1080, V15:1081); instrument D472 believed |
| **Comparator freeze audit** | instrument D471 believed; 45 graders 10/7/2/4/22/0; `analyse_t1b_L4` docket figure STRUCK; 87/156 markers without `finished_utc` relayed to heat-transfer |
| **Six standing audits** | all re-run 08-23 (`c5a9d4c7`, `f14fca9c`, `876a9ec1`, `af16ceef`, `69df4876`, `e3f3b521`); EXTERNAL_REFERENT's screen still uncommitted (own-audit defect, queued) |
| **Ten absent tracked files** | mechanism established above; the harness RESTORED under the chief's ruling (FAIL_OPEN_GATE §8); K1 + the eight are heat-transfer's under the same ruling |

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
question), the EXTERNAL_REFERENT instrument rebuild, and the
`check_record_reconciliation.py` C-series planted form. The Ansys sidecar is
NOT this team's any more (see the VM2026R1 row). Every dispatch carries a
predicted cost. Also in the INSTRUMENT QUEUE line above, strike "Ansys
sidecar" — superseded by the handover.

---

## ansys-verification

**Section last written:** 2026-08-24T16:27:20Z by harness-build (FIRST FILL — not yet
written by its owner, `ansys-verification-supervisor`; stamp from `date -u` read
in the writing invocation). Team created this day on Sanaa's directive
(verbatim in `docs/charters/ANSYS_VERIFICATION_CHARTER.md` §1). Agent
definitions (`.claude/agents/ansys-verification-supervisor.md`,
`ansys-lane-opus.md`, `ansys-lane-opus48.md`, `ansys-lane-haiku.md`) **take
effect at the next session start** — a session that began before this commit
cannot spawn them (form-teams skill, "If a subagent_type is not found").

**Last commit:** this commit (harness-build lane, parent `b7359d15`): team added to
`harness/teams.yaml` v1.2, generator extended for team-owned lane types and
restricted tools, charter v1.0, register created empty, `docs/ansys_verification/README.md`,
LOCATIONS note, this section.

**Live jobs:** none. No compute has been run by this team; zero core-minutes.

**Rungs lacking verdicts:** none run. 0 of the manual's 95 indexed cases
(78 VMFL, 7 VMFRT, 10 VMFLGPU) opened; register holds 0 rows. **Credential
count: 0 PASS of 0 run.**

**Next actions, in order:**
1. **Read the manual first** (Sanaa's directive) —
   `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`,
   title-page verified against the PDF (rule 15): "Ansys Fluid Dynamics
   Verification Manual, ANSYS, Inc., Release 2026 R1, March 2026", 290 pages;
   sha256 prefixes at this writing PDF `ee1bf7ce8a79…`, sidecar `577659469a30…`.
2. **Rule on the archives' canonical home (D-6)** with charter §9's inspection
   and `docs/VM2026R1_FILING_ANALYSIS.md` as input; say which copy is
   authoritative; record the ruling here and in the docket. Neither copy is
   moved or deleted before the ruling.
3. **Open the first rung**: the manual's ladder starts VMFL001 (Flow Between
   Rotating and Stationary Concentric Cylinders, p. 15), VMFL002 (Laminar Flow
   Through a Pipe with Uniform Heat Flux, p. 17), VMFL003 (Pressure Drop in
   Turbulent Flow Through a Pipe, p. 19) — analytical-reference cases the lab's
   OpenFOAM can reproduce cheaply. Pre-registration per charter §5 (reference
   result, tolerance, cost in core-minutes), frozen and **committed** before any
   solver starts; prereg sha reported to the chief.
4. **First spawn of `ansys-lane-opus48` is the load test of the `claude-opus-4-8`
   pin** (documented id; provider-side availability on this box unverified until
   a spawn succeeds — VERIFY). If it fails, report it and amend the charter §3;
   do not guess another id.
5. At every completion: calibration row in `docs/COST_CALIBRATION.md`; register
   row; LESSONS / `N-AV` numerics rows; charter amendments routed via the chief.

**On Sanaa's desk:** none from this team. Her directive is executed as written;
the D-3..D-6 closures are recorded in the CHIEF section above.

**Blocked:** none. **VERIFY:** (a) the Opus 4.8 pin loads (item 4); (b) VMFL068
has no `_WB` archive in the root copy (77 Fluent archives for 78 indexed cases —
observed by `find`, cause unknown); (c) the FORTE set is stored twice inside the
root copy (`VMFRT_v261.zip`, 481 MB, plus its extraction) — a 2.5 GB `du` figure
that would be ~2.0 GB deduplicated.

*First fill by the harness-build lane, 2026-08-24. `ansys-verification-supervisor`
owns this section and corrects it at its first commit or verdict.*
