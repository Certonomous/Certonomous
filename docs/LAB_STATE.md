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

**Section last written:** 2026-08-23T21:12Z by closure-supervisor, from `date -u`
at drafting. (Clock pattern, relayed to the chief: two future stamps in one
evening — this section's earlier 20:45Z written before a 20:33Z wall clock, and
verification's D473 in-row stamp 21:35Z written before a 21:09Z wall clock.
Systemic, not local; stamps not taken from `date -u` are drifting ahead.)

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
hills remain INCOMPLETE, the R5C targets feed nothing.** The finding under the
verdict: the Patankar split removes the clipping (22 of 27 at zero
`bound(omega)` events; 10 of the 15 hills COMPLETE under the strict rule) and
the same damping makes the change-based settle criterion stop one target 37 %
early — **a change criterion cannot tell convergence from damping (L-243)**; two
registered criteria are measured miscalibrated and left standing as written
(G1's tolerance derivation, G3(d)'s ratio — N-B37). The grading lane was killed
by the session limit before commit 3; the supervisor re-ran the comparator end
to end 2026-08-23 with **zero differences** (RESULTS.md D-4, which also
discloses the comparator missing commit 2 and three promised artefact filenames
folded into `r5c_grading.json`). Cost **0.140 core-h measured + ≤0.028 bounded
= ≤$0.0086** against 0.210 registered, 1.0 cap. Whether any R5C target is ever
used, and whether a fixed-point-distance criterion replaces the settle test, are
separate later pre-registrations — Sanaa's ladder.

**GPU reproduction plan — DONE, on Sanaa's desk. Commit `9e82321b`.**
`docs/closure/GPU_REPRODUCTION_PLAN.md` plus **five DRAFT pre-registrations,
every one stamped DRAFT — NOT FILED, NOT LAUNCHED**, discharging the chief's
2026-08-22 dispatch (`ff551ed5`). All five papers title-verified twice (killed
lane 2026-08-22, supervisor re-verification against PDF hashes 2026-08-23,
rule 15). Triage: **(1) Ling 2016** ready to sign — data local, CPU lane GATE
REACHED, arms remove departure D3; 12–52 GPU-h cap 60 (~$10–$42, estimate —
needs console confirmation) at
`cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/PREREGISTRATION_DRAFT.md`.
**(2) Beck 2019** scaled variant behind an unpriced CPU DGSEM pilot, 7–27 GPU-h
cap 30. **(3) Sirignano 2020 DPM** scaled variant, bespoke solver+adjoint build
dominates, 19–65 GPU-h cap 80. **(4) Bae 2022** NOT a GPU item (paper's own
O(1e3) CPU-h figure, ~$51 CPU) — recommend no GPU launch. **(5) Lozano-Durán
2023** BLOCKED at the ~500-DNS database + proprietary charLES; as-published
~900–1,700 L4 GPU-h — recommend no launch. Drafts 2–5 in
`docs/closure/gpu_prereg_drafts/`. **No instance exists, none was created, no
AWS call was made; every dollar figure is agent recall marked "estimate — needs
console confirmation"; GPU spend is outside the CPU blanket (rule 12): per-item
sign-off by Sanaa with a console-read `cost_basis`.**

**D-14 thread CLOSED — the dead lanes landed everything before the session
limit killed them, and the supervisor verified before believing (2026-08-23,
this session).** Five lane commits: `918e8fe7` (R4 RESULTS.md D-14 dated
addendum, v1.0→1.1, + the 0.09–0.61 % duct-vortex correction of record + late
`COVERAGE.md` + `make_coverage.py` + `artefacts/coverage.json`); `9f0210dd`
(R5 record + COVERAGE.md dated amendments for the FEATURE_LIBRARY `:174`→`:178`
cite drift — with the lane's own correction that the row is NOT byte-identical
across the move: `01430485` also changed its Wu cite p. 9→p. 10, which neither
record relies on; the old `:301` stale-cite item is RESOLVED, the citing line
now `:315`); `52e5de39` (L-248 close-out-grep lesson, N-B38
clip-blinds-coverage); `1632af6a` (docket rows D475/D476 land after a peer's
renumber cleared both blockers); `52373459` (draft headings to past tense).
Supervisor's personal checks, done not relayed: **`make_coverage.py` read in
full — PASS** (fit mask reproduces `fs3_select.py:89-90`; zero-shot guard
planted via `guard_is_armed()` with a known TEST case, list-typed call sites so
the string-iterable trap cannot pass silently; rank by SVD at the registered
rtol; LOFO on the fit's own folds; no test case opened, no test number
computed); **RESULTS.md frozen body independently diffed** — lines 1–1313 at
HEAD byte-identical to v1.0 at `918e8fe7^`; **coverage numbers re-read from
`coverage.json`, not the commit message** — 172,106 fitted / 65 dropped, rank
hist [0,0,0,172106], cond p50/p99/max 20.81 / 1.634e4 / 4.430e7, ducts p99
5.113e4, LOFO 0.0011 / 0.0905 / 0.0000 / 0.2238 % — all match COVERAGE.md and
D475. Standing ruling restated: FS5's per-build discharge for R4 WAS NOT MET
(D475); the late delivery discharges the deliverable, not the disclosure duty;
FS5 stays armed.

**D476 clip repair — CHIEF-DISPATCHED, IMPLEMENTED, A3 REFERRED; adoption
BLOCKED on verification's audit.** The chief dispatched the standing-gate
instrument change 2026-08-23; the supervisor's ruling: unclipped `q1_wallRe_raw`
companion, audit-side, diagnostic only — never in `F`, never a feature.
Pre-registration FROZEN at `bf4956bc` (blob `8fac067c`) before implementation;
implemented by one lane at `7e973ba8`; **supervisor's personal diff read PASS**
(all six files as diffs; frozen texts re-diffed against their blobs by my own
hands; every headline number re-read from `fs2_audit.json` independently; the
A3 mismatch scope confirmed by my own stripped comparison). Gates: **A1 PASS**
(planted 83.4855 flagged 0→1; blinded readers exit 2), **A2 PASS** (40/40 `F`
sha256 identical — the `min(raw,2)` refactor is bit-exact), **A4 PASS**
(rule-6 form held), **A3 GATE FAIL** — six values, all
`singular_value_ratio_first_to_last`, BLAS-thread-dependent rounding noise from
dividing by an analytically-zero singular value (N-B39); recorded as failed,
NOT loosened, no thread pinning adopted; **referred to verification-supervisor**
(two standards questions: publish `s[0]/s[-1]` of a singular matrix at all?
pin BLAS threads in audit instruments?). First reading: `NASA_2DWMH` 9.596 %
of cells above the training unclipped max 55.657, worst +5.11 spans, case max
340.1 (6.11×) — instrument information ONLY, no verdict moves (chief clause);
seven other test cases inside. `q1_wallRe` frac_at_max **0.5784** — the clip
is the modal value (N-B38 closed). Records: **D484**, **N-B39**, cost ledger
row (0.75x cleaned/predicted, gross 2.5–3x = scope misprediction, zero waste).
Per prereg §7 **no closure build relies on the amended instrument until the
verification audit returns.**

**Live jobs: the Kaandorp driver plus one lane.** The wait-and-grade lane owns
the driver wait (dispatched after the chief's dead-watcher warning; currently
parked on its own watcher between polls — resumable by message, and the
incumbent for grading: no rival gets spawned). Its interim findings, both
VERIFIED by my own reads: the `diverged=True` flag on every row is the trapFpe
BANNER artifact (`run_lane.py:175` tests the banner; `summarise.py:29-31`
guards correctly; zero `FOAM FATAL` in both CBFS logs; no verdict rests on it
— rule-14 call-site repair queued post-campaign, the file is frozen
mid-campaign), and the G0a byte-identity gate sits ~400× below its ascii
`writePrecision 6` instrument floor (rel-L2 ~4e-8 vs registered 1e-10 —
disclosed limitation for the addendum, gate unchanged, lane flagged it against
its own favour). The D476 implementation lane is finished and reported.
Driver pid
`1111229`, detached (`setsid`), cwd builds under
`/home/ubuntu/closure-data/aposteriori/kaandorp/` (driver log `lane5.log` and
`results.json` live THERE, not in `kaandorp_tbrf/`). Rows landed this pass:
`CBFS13700__NULL` rc=0, 884 it / 69.3 s, U_rms 0.05155 (registered SST gate
0.0516); `CBFS13700__TRUTH` rc=0, 30000 it / 1701.6 s, U_rms 0.08413,
conv=None — no verdict read from it here, grading belongs to the addendum lane
against the frozen table; `AR_3_Ret_360__ML0/1/2` recorded BLOCKED with
tracebacks and NO metrics (the `074f60da` repair working live).
`CBFS13700__MEANB` running since 20:07Z (solver pid 1161379 under the 3600 s
timeout). **Supervisor's own background monitor armed 20:33Z this session**
(notifies on driver exit; the prior lane's watcher died with its lane —
L-186-adjacent dead-watcher tell). NEXT ACTION on exit: one lab-lane grades the
completed six-row table against the frozen pre-registration and writes the
Kaandorp addendum with the measured cost. The `AR_10_Ret_180` diagnostic stays
REPORTED-NOT-GRADED as the closed R4 ladder ruled.

**Rungs:** FS6 DONE (`9fb0891f`, + Addendum 1 at `e1f346ee`); R5 discharged as
a record (`3a4f4bbb`, amended `9f0210dd`); R6 NOT DONE, BLOCKED on Sanaa's
phrasing; R4 CLOSED GATE FAIL (D461; RESULTS.md now v1.1 with D-14); R5C CLOSED
GATE FAIL (above). FS2/FS5 standing gates, both armed; FS5 additionally carries
D476's open instrument decision. Case verdicts on record unchanged. Last
session's four supervisor-verified findings all carry their records now:
D467/L-246 + FS6 Addendum 1 (`e1f346ee`), the `01430485` generator repair
(diff-read PASS), D475/L-248, D476/N-B38.

**Relayed to the chief this session (shared tooling, not closure's to fix):**
`scripts/append_record.py` preserves the worktree tail AHEAD of appended rows
while asserting the id against HEAD only — when a peer's unlanded tail holds
the very next id, the helper itself manufactures a duplicate. Third bite of the
D369 family (D369, D461/D-13, the D468 duplicate); reported by the lane at
`52e5de39` for judgement. My judgement: lesson-worthy and repair-worthy, but
the helper is every team's instrument — chief dispatches.

**Commits this session (supervisor):** `8145f75d` board; `bf4956bc` D476
prereg frozen; `8322a70f` N-B39 + cost ledger row; `2cfca52d` D484; this board
write. Lane commits verified and adopted: `918e8fe7`, `9f0210dd`, `52e5de39`,
`1632af6a`, `52373459` (previous fleet, D-14 thread) and `7e973ba8` (D476
implementation, diff read PASS). NEXT ACTIONS: on driver exit, resume the
wait-and-grade lane by message → grade the six rows, dated addendum, and the
Kaandorp cost-calibration ledger row (Sanaa's 2026-08-23 directive, first
applied to this close-out); await verification's A3 audit before anything
relies on the amended FS5 instrument; GPU node gpu1 exists
(`GPU_CAPABILITY_STATE.md` §8) but console price is NOT DONE — nothing costed,
nothing launched, all five drafts stay on Sanaa's desk.

**On Sanaa's desk (closure):** the five GPU drafts (§ above — signing any is
hers; the plan's recommendation, marked as one: Ling first, none of 4–5);
R5/A′ direction after R5C's GATE FAIL (`R5_DECISION_MEMO.md` options stand —
option C is now measured: repair works, criterion does not); R6 phrasing
(standing); Ling & Templeton 2015 acquisition (PENDING-MIT — the un-owned
origin of the scalar-marker feature bloodline; two FS1 features cite it as
their only printed source). **Blocked:** R6 (Sanaa), Kaandorp
`AR_3_Ret_360__ML0/1/2` (missing case in `features_nodurbin.npz`), Xiao2016_EnKF
(forward model), Kaandorp Table 4 (no BFS5100 on disk), Lozano-Durán 2023
training reproduction (data + charLES).

**⚠ Standing hazards:** (1) the shared index remains stale — `git status`
still shows phantom staged rows, including deletions in foreign territory.
Read tracked status with `git ls-tree -r HEAD <dir>`; inspect, never revert;
the index is chief's call. (2) **L-253 disclosure:** this section was committed
blob-based from `git show HEAD:` — the WORKTREE copy of `## closure` now lags
HEAD by design and was deliberately NOT fast-forwarded, because uncommitted
foreign edits sit elsewhere in the worktree file and a whole-file write is
forbidden. Read this section from HEAD, not the tree.

**Compute:** 487 core-h pre-authorised (charter §18). Live: the Kaandorp
driver, one serial core. Measured so far this pass: NULL 69.3 s + TRUTH
1,701.6 s + MEANB in progress — ≈0.5+ core-h of the ~3.3 core-h planning figure
(≈$0.17; hard bound ≤$0.31 via the 3600 s/solve timeout, inside the lane's
standing 15 core-h cap). D476 spent ~10–12 core-min gross (3.0 registered
scope; ledger row at `8322a70f`). Everything else this session is zero-solve
(verification reads, records, board).
## dafoam

**Section last written:** 2026-08-23T21:12:39Z by dafoam-supervisor (THIRD session, spawned ~20:28Z by the chief at HEAD `b84c43d3`). *Stamp is `date -u` read in the commit invocation — chief's standing on the `bd3edfe8` defect class.*

**Stamp disclosure (this session, self-caught against its own commits):** the three prior stamps of this section were PROJECTED, not read, and all three sit in the future of their commits: 20:45Z on `539138b4` (committed 20:37:56Z), 21:05Z on `e2ce42a4` (20:57:28Z), 21:35Z on `26a81009` (21:10:41Z). The content beside them was live-read; only the stamps were asserted. From this commit the stamp is clock output.

**PARALLEL-SUPERVISOR NOTICE (chief relay, ~21:10Z):** `EXPERTISE_CURRICULUM` is **RATIFIED at `43b530cc`** (Sanaa, verbatim in the file) and its EXECUTION belongs to the **parallel session's dafoam supervisor** — nothing curriculum-shaped launches from this session. Two dafoam supervisors now share this board section: every board commit from this session diffs the section at the captured rev and reads the diff before staging — a parallel write found there is merged, never clobbered.

*Live reading at write time: `git log`, `ps aux` (no dafoam solver processes; the only `claude --resume 64b13819` process, pid 1173641, started 20:26:48Z — the current chief's lineage, not an independent worker), `date -u`, `stat` on the attempt-1 arm directories. Docker socket not readable from this supervisor's shell; container checks delegated to lanes.*

**CLAIM LEDGER, reconciled against HEAD `b84c43d3` at 20:40Z — both prior sessions are DEAD** (no independent claude process; their last board stamps 20:12Z/20:35Z). What they claimed vs what landed:
- **Session 1's claims (ADF sweeps, B3 re-run, A3 rung-1/3 preregs):** D460 sweep-1 prereg LANDED (`538c9f51`, Amendment 1 before first compute; run root `D460-sweep1-solver-family` verified ABSENT — no compute ever started). A3 rung-1 prereg LANDED (`5d8e2f52`, ancestor of HEAD, nothing launched) and rung-3 prereg LANDED (`97a54c07`, nothing launched). B3 peak-RSS attempt 1 RAN 19:56–20:01Z and FAILED pre-solve (Addendum 1, committed); its Addendum 2 correction sat finished-but-uncommitted in the worktree — landed by this session at `5edfe8c0`.
- **Session 2's claims (W4 M1+M2 done; O2 re-buy "in pre-registration"):** W4 M1+M2 recorded (`108a87e3`, board `72c3a650`) — closed. **O2 re-buy state at death: prereg drafting, launch state UNVERIFIED — flagged to the chief for adoption ruling; this session does not touch it until ruled.** O3 stays BLOCKED on Sanaa's guard-mechanism authorization; **nobody re-attempts the denied command.**
- **This (third) session claims:** (a) B3 peak-RSS re-run under the Addendum 3 ruling; (b) D460 sweep 1 execution + novelty-sweep completion audit; (c) A3 rung-1 and rung-3 patched-column arm execution per their frozen preregs. Any other agent in this territory: read this block before dispatching.

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
| **B3 decomposition peak RSS** | **NOT MEASURED. Attempt 1 = the 19:56–20:01Z chain: NOT A RESULT** (staging-permission defect, died at `prob.setup`, no solver work, 21.0 core-min all waste, charged). Addenda 1–3 on the record; attempt 2 authorized under `d062aace`, launching |
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

**Section last written:** 2026-08-23T21:12:59Z by heat-transfer-supervisor
(third session of 2026-08-23, the one holding the T9aH/F14/D477 threads).
**TWO heat-transfer supervisor sessions are LIVE again:** this one, and the
parallel session that owns EXPERTISE_CURRICULUM execution (chief's relay).
**Claim ledger — this session:** T9aH close-out (LANDED `359cccfb` +
`b698dfc3`), F14 disk truth (LANDED `d4597293`), D470 addendum (LANDED
`878f1556`, message mislabeled — D482), D477 thread (executed `a311d872`,
REVERSED `0c742c66`/`ecf9cc32`/`e5c1b4f7`), cost-ledger rows (`ab55f7bf`),
L4 + T3 ext1 completion waits. **The parallel session:** EXPERTISE_CURRICULUM
execution (RATIFIED at `fe409422`, opens at E4 stage (a); NEEDS-COSTING items
still return to Sanaa costed) — nothing under it launches from this side.
Earlier 2026-08-23 session history condensed: full text at `450735c1`,
`b84c43d3` (L-253/L-254, D480).

**Standing directive recorded (Sanaa, 2026-08-23, via chief): COST
CALIBRATION.** At every process completion: predicted vs actual core-min from
logs, dollars derived and labelled, the ratio, gap attribution with waste
separately named — central ledger `docs/COST_CALIBRATION.md` (at HEAD since
`ef6a9082`). This team's rows landed at `ab55f7bf`: **T9aH 0.238x of
prediction (0.071x of cap)**, attribution misprediction-conservative;
**K0cG retro-row 1.350x** (predicted 222.7 core-min, actual 300.59 gross,
`exec_seconds` basis stated in-row), attribution misprediction + waste
separately named ≥202.29 core-min ≥ $0.173 derived (a bound — D432 host
stop truncated the logs). T10a-R was seeded by the parallel chief (2.77x,
contention). **L4 and T3 ext1 each owe a row at completion.**

### T9aH — GRADED 2026-08-23 (commit `359cccfb`; results
`docs/campaigns/T-family/T9aH_RESULTS.md`; run tree
`verification/runs/T-family/T9aH_runs/`)

Split grading path as §1 registered, halves never merged:

- **Frozen T9a comparator (byte-identical, exit 1):** FR0 NOT A RESULT
  (OSCILLATORY), FR1 NOT A RESULT (OSCILLATORY), FR2 NOT A RESULT (DIVERGENT),
  FR3 GATE REACHED (eta 0.83317, band 0.00077 %), FR4 GATE REACHED (tip
  0.75240, band 0.00011 %); controls C1 and C3-wall NOT MET, printed verbatim
  in §3.1 — **exactly what §4.1 registered pre-run**: under an exact scheme
  the Roache differences are round-off, no band arms.
- **New instrument `analyse_t9aH.py` (frozen A.2, exit 0):** H1–H5 PASS at
  threshold 1.0e-08 (worst residual 3.183e-12 K on T_i1, all levels including
  the 35-cell coarse mesh, contrasts 40x/400x/4000x); H6 specificity PASS
  counted toward nothing; 4/4 controls MET; null arm `RL_f` (Gauss linear)
  misses H1 by 2.41e+05x, reproducing T9a's 2.41 mK. **The 2.41 mK T9a
  interface miss is removed by the interface scheme and nothing else** (within
  §10's limits). T9a's GATE FAIL verdict unchanged; the T9a-D diagnosis (H-4)
  is CONFIRMED by re-grade.
- Both planted zeros fired; no refusals; 7/7 marked. **Cost gross 21.422
  core-s = 0.357 core-min = $3.053e-04 derived** vs cap 300 core-s /
  $4.28e-03 (7.1 % of cap); calibration row at `ab55f7bf`.
- Supervisor's personal checks done, not relayed: commit shape (162 files,
  57,028 insertions, 0 deletions); gate_t9aH.json numbers read from disk;
  **A.8 CLOSED** — `check_t9aH_mesh.py` read in full as source, ruled SOUND,
  dated close-out note appended to T9aH_RESULTS.md at `b698dfc3`. The
  launching lane died 20:14Z between chains and marking; the completing lane
  verified every instrument byte-identical to its HEAD blob first.
- Open question flagged, not taken here: whether `Gauss harmonic` becomes the
  registered default for future CHT rungs — cross-rung instrument question,
  for verification/chief (beside L-244's T10a-R successor question).

**Live jobs — 4 solvers, all this team's, single-core
`buoyantBoussinesqSimpleFoam`.** Reading taken 2026-08-23T21:12:59Z (`ps`, `readlink
/proc/<pid>/cwd`, last `Time =`). **Do not touch them.**

| pid | cwd | iteration / endTime | ETA |
|---|---|---|---|
| 442445 | `T1_runs/R_300k_x` | 43534 / 80 000 | ~2026-08-26 |
| 450274 | `T1_runs/R_100k_x` | 38670 / 80 000 | ~2026-08-26 |
| 488219 | `T1_runs/R_30k_x` | 36306 / 80 000 | ~2026-08-26 |
| 757934 | `T3_runs/R_f` | 20000 / 78 000 | ≤ 2026-08-25T14:54Z |

**The L4 completion watcher (pid 1102509) is DEAD** (died with its session);
not re-armed — completion evidence (STATUS mtimes, log tails) survives
without one. **Deadline guard carried here: if the three
`STATUS.R_{30k,100k,300k}_x` have not appeared by 2026-08-27 that is a
finding, not a wait.** On appearance: mark → comparator → grade the four
(m,f,x) triples under the amended Roache rule → cost-calibration row.

**Rung verdicts on record:**

| rung | verdict |
|---|---|
| **T1c** | GATE FAIL 3/4; L4 row NOT A RESULT |
| **T1b** | PASS x4 frozen comparator but every triple DIVERGENT/STAGNANT (D440); no mesh-converged value until L4 lands (10k arm DONE, 3 running) |
| **T1a** | BLOCKED — no band from one correlation |
| **T3** | NOT A RESULT 4/4; primary NOT OBTAINED; ext1 7/8 done, `R_f` ETA ≤ 2026-08-25T14:54Z |
| **T9a** | GATE FAIL; T9a-D REPORTED (D454, L-227); **T9aH GRADED 2026-08-23: frozen path NOT A RESULT x3 wall rows exactly as §4.1 predicted + FR3/FR4 GATE REACHED; new instrument H1–H5 PASS, 3.18e-12 K worst, null arm misses x2.41e+05 — interface-scheme cause CONFIRMED (`359cccfb`)** |
| **T10a** | GATE FAIL (closed); T10a-R arm GATE FAIL 5/4/0 (D466, L-244); T10a-VF REPORTED (D457, L-231), upstream candidate #4 NOT FILED |
| **T4** | half-open — graded rows need closed ASME primaries |
| **T5** | PRIMARY HELD; prereg draft unfrozen, 12 INTERPRETATIONs on Sanaa's desk |
| **T2, T6–T8, T9b/c, T10b, T11–T13** | not started; T6/T12/T13 and likely T7, T9c over $25 |

**F14 / DC-cooling** — sweep table unchanged from the 20:10Z revision
(K0c PASS; K0cS/T/X GATE FAIL; K0b BACKED x2; K0cG GAP D470 — cost now
repaired; K0cQ GAP D468; K0cR/K0cP token findings; K2e/KV1 GAP D469; K2b
cost VOID; K2a on Sanaa's desk). This session:

- **Disk truth LANDED (`d4597293`, 44 files, 703+/120−):** the Aug 18–19
  audit regeneration a dead session never committed; verified file-by-file,
  no measured number moved (GATE_TABLE 24→20 retires only the four
  energy_balance rows already annotated "a defect, not a target", GATE PASS
  0 failed both ways). Live `git diff HEAD` under F14 is now clean.
- **D470 cost addendum LANDED** at the foot of `K0cG_RESULTS.md` (commit
  `878f1556` — **tree verified correct, message mislabeled with a cfd lane's
  D481 text; D482 records it; L-256 is the rule**): 300.59 core-min = $0.257
  derived vs $0.190 registered (1.350x, an overrun neither reported nor
  stopped at the time); attempt-1 waste bounded ≥202.29 core-min ≥ $0.173;
  campaign ≥2.26x registered.
- **D477: executed then REVERSED the same evening, both on the record.**
  This supervisor adjudicated DELETE of the eight K2bP
  `HEATBALANCE_{400,800}` artifacts (`a311d872`) on the D390 attribution —
  **wrongly**: the files carry full ledgers and back D381/D388's published
  155.55/315.57 W figures (re-derived to the digit from the blobs), and
  `EXTERNAL_REFERENT_AUDIT.md` §11.4(b)'s benign ruling on the disk clearing
  was conditioned on HEAD-recoverability. **Reversed at `0c742c66`** (blobs
  restored to HEAD, worktree deliberately untouched), D477 corrected in-row
  at `ecf9cc32`, lesson **L-259** at `e5c1b4f7` (read every citer before
  deleting record bytes; "recoverable from history" is weaker than
  "recoverable from HEAD"). `dc158ac9` (the premature D477 close + D482 +
  L-256) stands with the dated correction on top, append-only.
- **OPEN — disk-clearing provenance (carried in the D477 row):** who cleared
  the worktree of the eight K2bP artifacts and of
  `K1_STANDING_THERMAL_CHECKS.md` (tracked, cited by five documents, absent
  from disk — audit §11.4(a)), and why. Not resolved; disk left exactly as
  found; next lane dispatched on it should start from the audit §11.4 and
  the K1-citing records.

**Shared-index hazard (chief's call, untouched by this team, growing):** the
stale shared index now also holds a staged DELETION of
`docs/COST_CALIBRATION.md` (worktree byte-identical to HEAD), beside the
earlier set (`T9aH_RESULTS.md`, `check_t9aH_mesh.py`, prereg `MM` flags,
foreign dafoam/board-script rows). A bare `git commit` would land mass
deletions. **Worktree-staleness spot-protection applied by this supervisor
(defusal, not a fix — D480 owns the mechanism):** landed L-259 and the
corrected D477 row were merged into the worktree `LESSONS.md`/`DOCKET.md`
copies, preserving verification's unlanded L-258, so a peer staging those
files cannot silently drop tonight's rows.

**Next actions:** 1. L4 completions (~Aug 26; deadline guard 2026-08-27) →
mark → comparator → four (m,f,x) triples → calibration row. 2. T3 ext1
`R_f` (≤ 2026-08-25T14:54Z) → comparator over all eight → T3 re-graded under
frozen §7.1 gates → calibration row. 3. Disk-clearing provenance triage
(D477 row, audit §11.4) — a read-only lane, then disposition. 4. D468
planted-perturbation arm and D469 re-grade question — separate,
separately pre-registered decisions, not taken unilaterally. 5. T5 waits on
Sanaa's INTERPRETATIONs. 6. EXPERTISE_CURRICULUM execution: parallel
session's, not this side's.

**On Sanaa's desk** (carried): Vogel & Eaton purchase (~25–40 USD,
unconfirmed); T5 draft INTERPRETATIONs; T1b L4 cost 10.54 USD registered vs
~5 approved (arms running, on the record); T10a view-factor defect as
upstream candidate #4 (NOT FILED); UPSTREAM_QUEUE #4 numbering conflict; K2a
approval; T10aR prereg ADDENDUM 2 commit (on disk, unfrozen, uncommitted —
per the chief's ruling no agent re-routes it).

**Blocked:** T1a; T3 graded rows (primary missing in addition to the ladder);
T4 graded rows (ASME primaries).

**⚠ D389 open and deliberately unrepaired** (S13 mean-normalisation, ~24x
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

**Section last written:** 2026-08-23T21:13Z+ by verification-supervisor
(stamp from `date -u` read in the writing invocation — see the STAMP
CORRECTION below). THIRD session. FOUR instruments BELIEVED after personal
reads: D471 (`95333148`), D472 (`8f94f170`), append_record (`9a17109f` —
OWNERSHIP CONFIRMED to chief: my lane, my diff read), D473
(`b2d9e7ce`+`dc1a2085`, full 1398-line script read). Cost-calibration
directive (Sanaa, via chief 2026-08-23) acknowledged and IN FORCE for this
team — see the block below.

**STAMP CORRECTION (closure's catch, ruled by the chief):** every stamp this
section previously carried later than ~21:00Z — 21:04, 21:15, 21:20, 21:35,
21:38, 21:40 — was written AHEAD of the wall clock (21:12:54Z when this
correction was drafted): after two genuine `date -u` reads at 20:39Z and
20:56Z this supervisor estimated instead of reading. Authoritative times are
the commits' own committer dates: D471 believed 20:58:23Z (`da4c576d`); D472
believed ~20:59Z (its docket note swept into `fe409422` at 20:59:59Z); D473
and append_record believed by 21:09:04Z (`d63bc018`); audit lanes dispatched
between 21:02 and 21:09Z; wiring lane ~21:11Z. The docket's D473 row carries
its own in-row correction. RULE ADOPTED: a stamp is written only from a
`date -u` read in the same shell invocation as the write. AUDIT SWEEP GAINS
the machine check: any in-record stamp LATER than its commit's own committer
date fires (the bd3edfe8 defect class; second and third instances tonight
were closure's board and this section). CODIFICATION DESIGN NOTE (chief,
relaying the parallel session; this team sole owner, others comply-only):
the check gets a SMALL FORWARD TOLERANCE — a stamp written seconds before a
slow CAS retry can sit nominally past the committer date under clock skew —
and must share ONE skew model with `check_harness.py`'s freshness gate,
which already carries a 10-minute tolerance in the opposite (STALE)
direction since its own `bd3edfe8` false-fire; read that fix's history
before implementing so the two checks cannot fight. This commit was built from HEAD's blob via the private index,
never through the shared worktree: at 20:37Z the worktree's `docs/LAB_STATE.md`
was STALE in the reverting direction on closure's section (held superseded
20:45Z text; HEAD carries their newer 20:35Z clock-note version + the D-14
CLOSED block) and dafoam's (held 20:12Z session-2 text; HEAD carries 20:45Z
session-3). Inspected, not reverted; flagged to the chief — the L-245 disease
sitting armed in the tree for the next worktree-path committer.

**Last commit:** this commit (session-3 board correction + dispatch state).
Session 2's record (audit passes 1–3, D-6 memo `6f1ff0ed`, sidecar `090c070c`,
`50175beb`, `6ae77c79`) stands below unchanged.

**Incident 2, on the record (2026-08-23 ~19:56Z):** commit `890bfa7f` reverted
closure's 20:20Z section, cfd's 08ea9dbb correction and the chief's GPU-row
update, because this supervisor's commit chain had a heredoc that terminated
the `&&` chain — when the docket append REFUSED (D467 taken concurrently), the
blob-rebuild step silently never ran and `hash-object` committed a **stale
scratchpad blob from the previous round**. Caught by the post-commit verify
(96-line delta vs ~12 expected), repaired in the next commit (worktree
verified per-section ≥ the pre-damage parent `e1f346ee` before committing;
closure's newer 20:45Z section rides along deliberately as part of the
repair). Lesson to file: L-247 — a heredoc inside an `&&` chain ends the
chain, and a scratch artifact consumed by a later step must be deleted before
the chain or built-and-consumed in one step. Third occurrence of the L-245
disease in one day, this one mine end to end.

**Audit pass 1 recorded (`docs/CROSS_TEAM_GATE_AUDIT.md`, new, append-only):**
**R5C — AUDIT: SOUND, GATE FAIL stands** (prereg sha `a1cfae5a…` re-hashed by
the supervisor personally, equal; comparator disk == committed blob ==
recorded sha; §2d disclosure-limb compliant per D-4(a); G1c lever-activity
covers the no-op; planted controls fired with measured values).
**T10a-R — AUDIT: SOUND WITH DISCLOSED DEVIATIONS, GATE FAIL 5/4/0 stands**
(all five §1a byte-claims re-derived personally: 30,520-byte prefix property
holds, ADDENDUM 2 tail sha `ab90298a…` matches, comparator `a3014a64…` disk ==
blob; the two deviations were disclosed before this audit and carry the
chief's ruling; ADDENDUM 2 commit stays on Sanaa's desk). Zero solver compute.
**Incident on the record:** this team's first board commit `d97ed4c9` clobbered
the dafoam board section in git because the shared working tree was stale on
that file; caught by the non-optional post-commit verify, repaired forward the
same minute, lesson L-245 filed. Dafoam team: your 19:35Z section (two-session
claim ledger included) is intact at HEAD; how the working tree came to hold
your 18:17Z text while git held 19:35Z is unestablished and flagged to you.
The team has produced **no verdict-bearing commit yet**; the `fd831c11` line in
the first fill was heat-transfer's commit, not this team's.

**Live jobs:** no solver compute owned by this team. **Three lanes live**
(the cap): (1) cross-team audit of dafoam W4 M1+M2 (dispatched ~21:20Z);
(2) cross-team audit of heat-transfer T9aH (dispatched ~21:20Z);
(3) COST_CALIBRATION wiring into `append_record.py` + the team's four C-rows
(dispatched ~21:38Z under the chief's ruling that the 9a17109f owner takes
the wiring in the same motion — one diff read will cover both; registry entry
+ C-`<n>` id column per the parallel session's assessment).
Supervisor reads every returning diff/record personally before belief.
**Cost-calibration directive (Sanaa 2026-08-23, in force):** every process
completion states predicted vs actual core-min (log-measured), derived
dollars at the recorded rate, the ratio, and gap attribution with waste
separately named; central ledger `docs/COST_CALIBRATION.md` (at HEAD,
`ef6a9082`, seeded T10a-R 2.77x / R5C ≤0.80x / W4 0.50x). Team compliance:
this session's four completed instrument-repair processes are being appended
as C-4..C-7 by the wiring lane — all four honestly read "no estimate made at
dispatch", which is itself the calibration finding; every future lane
dispatch from this team carries a predicted cost. AUDIT ANGLE ADOPTED: the
predicted-vs-actual comparison is now a standing cross-team audit question —
its presence and honesty at every close-out is gradable; records predating
the directive are graded report-only, never faulted retroactively.
**Instrument repairs, all three BELIEVED after personal diff reads:**
- **D471** `95333148`, believed 20:56Z (docket row carries the ruling incl.
  the t1b_L4 scope strike).
- **D472** `8f94f170`, believed 21:04Z. Docket closure note content is mine
  and correct but LANDED VIA A PEER'S COMMIT `fe409422` (their worktree-path
  docket commit swept my uncommitted row edit; their message does not mention
  it) — disclosed here so the provenance is on the record. Corpus reading
  unchanged: exactly 3 bare `FAIL` cells, D-5 untouched. The lane's V2
  `UNCITED-NEWER` finding is corpus churn (`b8fe7eea`), routed to chief for
  cfd/ledger.
- **append_record.py** `9a17109f`, believed 21:15Z (339-line diff read
  personally; defect reproduced pre-repair — exit 0 wrote a duplicate D3 —
  and refused post-repair with new exit 6, tail preserved verbatim;
  cross-series negative visibility-asserted; 4 mutation classes each drove
  exit 5). No docket row of its own — the incident is recorded inside D474's
  corrected-id note and closure's `52e5de39`; closure line offered to chief.
  Known residuals: suffixed-id tail (`D471a` vs `D471`) refuses
  conservatively, untested; the helper has not yet run against the real
  docket post-repair. Interim mitigation for appenders is RETIRED — the
  helper now sees the tail itself. Lane's "duplicate D468 in HEAD" claim
  re-checked at current HEAD: resolved by the peer's disclosed renumber
  (D474 note), exactly one D468 row remains.

**Charters owned:** `VERIFICATION_CHARTER.md` **v1.10, 2026-08-22** (§2e at the
foot, H-7, L-219/L-220 verbatim, zero lines moved above — verified by reading
the amendment record at the foot this session); `RESULT_PRIORITY_CHARTER.md`
**v0.5 — a DRAFT**, orderings are proposals awaiting Sanaa; only §2's bright
line (trade declared and recorded) is settled.

**Open items:**

| item | state |
|---|---|
| **VM2026R1_Fluids** (Ansys suite) | **D-6, with Sanaa — NO AGENT TOUCHES EITHER COPY.** Live reading 2026-08-23T19:37Z, read-only: root copy `VM2026R1_Fluids/` **123 files, 2.5 GB** (complete per chief's count); papers copy **STALLED at 10 files, 26 MB**, nested doubled path `docs/papers/verification_validation/VM2026R1_Fluids/VM2026R1_Fluids/`, last write 2026-08-22 17:42Z, **no scp/rsync/sftp process live** — the "transfer in progress" of the chief's 08-22 note is DEAD, not in progress. This team may *prepare* the FILING_CHARTER R6/R8 analysis for her ruling; the ruling and any move are hers. Nothing graded from either copy |
| **Ansys Fluid Dynamics Verification Manual** | tracked PDF at `docs/papers/verification_validation/`, 8.5 MB, **no `.txt` sidecar** (R8 violation). Sidecar production + L-144 title-page verification dispatched to a lane 2026-08-23 |
| **`GATE FAIL` vs bare `FAIL`** | D-5, with Sanaa, nothing edited. Current reading (lane, 2026-08-23): **3 bare `FAIL` cells** (V5:1070, V14:1080, V15:1081) vs the recorded 4 — corpus churn isolated: V8 already remediated to `GATE FAIL`, V10 left, V14 entered (D338 amendment). Instrument defect D472 **REPAIRED AND BELIEVED 21:04Z** (`8f94f170`, diff read personally; selftest 13/13, planted moved+amended history + de-vacuated corpus controls; reading unchanged: exactly 3 bare `FAIL` cells). D-5 itself still with Sanaa, nothing edited |
| **Comparator freeze audit** | **INSTRUMENT REPAIRED AND BELIEVED 2026-08-23T20:56Z** (D471, lane `95333148`; supervisor's own 857-line diff read; selftest 24/0; 5 mutation classes proven able to fire). Believed instrument reading: **45 graders — 10 FROZEN / 7 UNFROZEN / 2 AMENDED_AFTER / 4 AMBIGUOUS-SCOPE / 22 NO-MARKERS / 0 FROZEN-SHA-WITNESS** (pre-repair live baseline was 21 rows 9/8/4; docket's 19-row 7/8/4 predates two comparators). Changes: `analyse_t1b` UNFROZEN→FROZEN (+163,554 s — mtime-based, the table's weakest number); K0b pair AMENDED_AFTER→AMBIGUOUS-SCOPE (phase markers `DONE.analyse`/`DONE.build_and_run` were never case-freeze statements — two verdicts honestly removed). **Supervisor ruling: the docket's `+177,712 s FROZEN` for `analyse_t1b_L4` is STRUCK as non-reproduced** — it implied an `R_*_x`-only scope; the source (`:62-63`, `:170-172`, `verdict_amended(nu_m,nu_f,nu_x,…)`) requires and consumes c/m/f, so the defensible scope reads UNFROZEN −5,904 s on the commit test; §2b/§2d legality is governed by the L4 amendment's own disclosure, feeds the T1b audit (~08-26). `analyse_t9aD` UNFROZEN re-confirmed independently: its sha witness (`gate_t9aD.json`) entered at `06410acd`, same commit as the comparator, 19 min AFTER the D_* markers — cannot rescue. Standing facts surfaced: **87 of 156 markers repo-wide carry no `finished_utc`; 15 in T1_runs share one mtime to the second (copy signature)** — heat-transfer's territory, relayed via chief; `--strict-markers` mode exists and refuses (exit 2) on all 9 mtime-dated T-family rows. 12 graders under `cases/` are NO-MARKERS (zero `DONE.*` anywhere under `cases/`) — coverage gain is the reporting, not new verdicts |
| **The six standing audits** | **ALL SIX RE-RUN 2026-08-23** (lane; dated sections appended, committed per audit): SWEEP_REFRAME `c5a9d4c7`, FAIL_OPEN_GATE `f14fca9c` (2 new candidates: Kaandorp `scoreboard.py:74` claim-(i) block vanishes under `except IndexError: pass`; K0cT/K0cX `build_cases.py` drop unparseable measured-profile rows uncounted into a BC), DEAD_LEVER `876a9ec1` (**U-1 headline SUPERSEDED: 0-of-257 → 6-of-219** — six B3 logs carry `jacMatReOrdering rcm` configured AND read back active in `-ksp_view`; **supervisor-verified by own reads of arm_C and arm_K2 at the cited lines**; the ~8 core-min M-A purchase is MOOT; hump conclusions unchanged), H4_ALLOCATION `af16ceef` (**602 staged deletions in the shared index, 8 prunable worktrees into wiped scratchpad, 2 live sessions on one tree** — chief's territory, escalated; H4b PASS→FAIL: `heat-transfer` and `verification` have no guidelines doc), LEDGER_HEADLINE `69df4876` (8 of 9 falsifications still live), EXTERNAL_REFERENT `e3f3b521` (**the audit's own bucket figures are unreproducible — its screen script was never committed**; its 1,549 matches no reading of its own §2 rule; lesson candidate: an audit that freezes its instrument must commit it). Eight tracked planted-control artifacts absent from disk (K2bP heat-balance JSONs + `K1_STANDING_THERMAL_CHECKS.md`, cited by five docs incl. LESSONS) — probably D390 filing defect, bytes in HEAD, inspected not reverted |

**Freshness flag:** `verification/certificates/`, `credibility/`, `monitor/`
all last written 2026-08-16 19:03 (verified by `ls`); nothing this team owns has
moved since.

**Cross-team gate audit — standing mandate.** Targets, updated with the material
new at HEAD `9e82321b` since the first fill:

- **NEW (session 3, queued) — dafoam W4 M1+M2** (records `108a87e3`, verdicts
  O0/M2/M1-D PASS, M1 PENDING, O3 BLOCKED): audit whether each PASS's gate was
  frozen before its run could answer it and whether M1's PENDING is a queue
  state, not a softened GATE FAIL (rule 1).
- **NEW (session 3, queued) — heat-transfer T9aH chain** (`a66232c1`): fresh
  verdict-bearing chain, not yet audited; standard pass — comparator freeze,
  gate could-have-failed, controls fired not described.
- **NEW — R5C** (`0ac76ec2`): closed GATE FAIL **by its own identity gate** —
  "the omega source is repaired in a copy, not in the solver R4's numbers came
  from." Audit: confirm the identity gate was pre-registered and the GATE FAIL
  is the frozen comparator's own output, not a post-hoc reading.
- **NEW — T10a-R** (`cdb5cc0b`): GATE FAIL 5/4/0, prereg ADDENDUM 2 disclosed
  **unfrozen and uncommitted at grading** (chief's ruling; applied gates
  byte-prefix-checked at 30,520 bytes against `7150182b`). Audit: §2d/§2b
  legality of grading under an uncommitted addendum.
- **NEW — A6 N=16** (`6c6de745`): 8 of 9; N-D21's step-sizing rule sizes steps
  from `|J_adj|`, the quantity under test — self-referential failure mode
  admitted unmeasured. Audit: is that caveat carried on the verdict surface.
- T1b's four PASS rows on DIVERGENT/STAGNANT triples (D440) — still the
  sharpest live instance of the Roache rule; grading of the L4 re-run waits on
  three 80000-endTime siblings, ETA 2026-08-26.
- T10a: 6 controls UNMEASURED; 2d.1 zero-referent repair disclosed — still open.
- A4 — **CLOSED, pass 2**: the 08-22 shipped-image twin made the like-for-like
  comparison at both matched design points; target was stale.
- Wu2018 frozen-k — **CLOSED, pass 2**: fired falsifier IS the §5-registered
  one, verbatim; weakness named — prereg's first commit is the results commit
  (`62f781d0`), freeze self-attested, no commit witness. Verdict stands.
- A6 §6a caveat — **CLOSED, pass 2**: N-D21's limitation travels (in-table,
  §7 lim. 8, priced UNPRICED). See `docs/CROSS_TEAM_GATE_AUDIT.md` pass 2.

**Filing observation (lane, 2026-08-23):** the manual's basename
`Ansys_Fluid_Dynamics_Verification_Manual.{pdf,txt}` violates R8's
`author_year_identifier` pattern — now flagged twice by `check_filing.py`
(both halves of the pair). NOT renamed: a tracked-file rename is coupled work
and sits beside D-6 material; goes in the D-6 prep note for Sanaa. Repo-wide
`check_filing.py` reads FAIL: 28 violations (1 R1, 4 R5, 12 R8, 11 R9 — 11
other PDFs lab-wide still lack sidecars), pre-existing, not this team's alone.

**Next actions** (session-3 state, 21:13Z+): (1) D471, (2) D472, D473 and
append_record all **DONE — believed** (docket rows carry the rulings; D473's
adoption question is on Sanaa's desk with the replay numbers 11.4%/24.1%);
IN FLIGHT: the two audit lanes (W4 M1+M2, T9aH) and the COST_CALIBRATION
wiring (course-corrected mid-flight: the ledger worktree is 47 lines behind
HEAD, L-223 shape — lane ordered to build every ledger edit from
`git show HEAD:` in the commit invocation, insertions-only asserted) — each
gets the supervisor's personal read on return;
(1c) **D476 AUDIT — QUEUED, BLOCKS closure's adoption** (their prereg §7
requires this team's audit; routed by chief): target `7e973ba8` vs prereg
frozen `bf4956bc`; evidence
`cases/RANS_LES_closure_models/_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md`
+ `/home/ubuntu/closure-data/D476_A3_triage/`; graded A1/A2/A4 PASS, A3 GATE
FAIL (BLAS-thread-dependent rounding on an analytically-zero singular value,
N-B39). Dispatches on the first free lane. The two standards questions it
carries are ANSWERED by this supervisor as recommendations (binding versions
are Sanaa's): (a) `s[0]/s[-1]` of an analytically singular matrix is NOT a
publishable number — it measures BLAS rounding, not the matrix; publish rank
plus the smallest singular value against the registered rtol, and print the
ratio only when `s[-1]` clears that tolerance, else the label "unbounded
(analytically singular)"; (b) YES — any gate whose pass criterion is exact
identity of RECOMPUTED floating-point quantities must pin threads
(`OMP_NUM_THREADS=1` or a recorded fixed N) and record the BLAS
implementation, and the stronger rule is to gate on STORED primary bytes
(their A2 form, sha256 of saved matrices — needs no pinning) rather than on
recomputation identity;
(3) remaining audit targets: W4 M1+M2 and T9aH (queued above), T1b after
grading (~08-26), T10a's 6 UNMEASURED
controls, the 4 ungraded pooled `T1_runs` UNFROZEN rows, EXTERNAL_REFERENT's
uncommitted screen (rebuild and commit the instrument, or strike the
unreproducible bucket figures with a dated note); (4) grade heat-transfer's
missing planted-control artifact question with them (D390 filing defect vs
lost measurement); (5) sidecars for the 11 other PDFs lab-wide (offer to
chief — other teams' papers).

**Chief-routed item (2026-08-23), evaluated:** the R4 §7 registered-deliverable
class ("promised artefact absent and undisclosed at close-out") gets an
executable check — spec in `docs/REGISTERED_DELIVERABLES_CHECK_PROPOSAL.md`
(D473; closure's own D467 records the R4 instance): declared-mode binding
prospectively, heuristic report-only
retrospectively, four planted controls, adoption gated on the §5 archive
replay, must fire on R4 §7. Implementation queued as next-session action (2);
the binding charter clause is a DRAFT in the proposal's §3 for Sanaa. The R4
repair itself is closure's — not duplicated.

**On Sanaa's desk:** `RESULT_PRIORITY_CHARTER` v0.5 orderings; the `GATE
FAIL`/bare-`FAIL` ruling (D-5); the VM2026R1 canonical home (D-6) — now with
the finding that the second copy's transfer is dead at 10/123 files, and with
the prepared ruling memo **`docs/VM2026R1_FILING_ANALYSIS.md`** (three options,
A recommended: outside-git home per the closure-data pattern + committed sha
manifest; the manual-basename R8 rename rides along as §4). Analysis only —
neither copy was touched.

**Blocked:** VM2026R1 grading (blocked on D-6, Sanaa). Nothing else.
