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

**Section last written:** 2026-08-23T19:35Z by closure-supervisor.

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

**Live jobs: none.** The R4 BUILD lane's last diagnostic
(`AR_10_Ret_180/discovered_ronly`) finished — `rc=0`, `End` line, last time dir
7500 — and remains **REPORTED-NOT-GRADED** exactly as the closed R4 ladder ruled
(no gate, verdict or number depends on it). Box load is the T-family's.

**Rungs lacking verdicts:** unchanged from 2026-08-22 except R5C (now CLOSED,
above): **R5** no verdict artefact; **R6** NOT DONE, BLOCKED on Sanaa's
internal-scoring phrasing; **FS6** NOT DONE. R4 CLOSED GATE FAIL (D461). FS2/FS5
standing gates. Case verdicts on record unchanged, plus **R5C: GATE FAIL**.

**Commits this session** (closure, newest first): `9e82321b` GPU plan + five
drafts; `0ac76ec2` R5C commit 3 (verdict, comparator, grading JSON, D465,
L-243, N-B35–37). Before them: `23b9d7ba` (R5C step 2, solver copy), `f364cf2d`
(R5C prereg frozen alone). Both supervisor commits used the private-index
protocol; the second's CAS correctly absorbed heat-transfer's intervening
`cdb5cc0b` (D466/L-244 — id sequences interleaved cleanly).

**On Sanaa's desk (closure):** the five GPU drafts (§ above — signing any is
hers; the plan's recommendation, marked as one: Ling first, none of 4–5);
R5/A′ direction after R5C's GATE FAIL (`R5_DECISION_MEMO.md` options stand —
option C is now measured: repair works, criterion does not); R6 phrasing
(standing). **Blocked:** R6 (Sanaa), Kaandorp `AR_3_Ret_360__ML0/1/2` (missing
case in `features_nodurbin.npz`), Xiao2016_EnKF (forward model), Kaandorp
Table 4 (no BFS5100 on disk), Lozano-Durán 2023 training reproduction (data +
charLES).

**⚠ Standing hazard unchanged:** the shared index is stale — `git status` shows
phantom `D` rows for committed R5C files (L-223 shape, read from the other
side). **Read tracked status with `git ls-tree -r HEAD <dir>`, never
`git ls-files`; inspect, never revert; the index is chief's call.**

**Compute:** 487 core-h pre-authorised (charter §18). This session's closure
spend: **$0 new solver compute** — R5C's runs were the killed lane's (≤$0.0086
total, under its cap); grading and drafting were zero-solve. Nothing live under
this team.
## dafoam

**Section last written:** 2026-08-23T19:35Z by dafoam-supervisor.

*Live reading at write time: `git log`, `docker ps -a` (no dafoam containers), `ps aux` (no dafoam processes), `date -u`. Every commit time below is `git show -s --format=%cd` output.*

**⚠ TWO SESSIONS ARE WORKING THIS TERRITORY.** A second live session (pid 1100087, `claude --resume 64b13819`, started 19:04Z) committed `c8254a4a` — the **W4 M1+M2 pre-registration** — at 19:33:04Z today, four minutes after this session's chief took its live reading, with no docket claim. Its run root `/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/` exists (19:26Z); no container was live at 19:35Z. **Claim ledger, this session (19:35Z): W4 M1+M2 is THEIRS — this session will not touch it. This session claims: (a) ADF characterisation sweep 1 + full novelty sweep (D460 blockers), (b) B3 decomposition peak-RSS watcher re-run, (c) A3 rungs 1/3 patched-column pre-registrations.** Any other agent in this territory: read this block before dispatching.

**Last commits (newest first):**

| sha | committed (UTC) | what |
|---|---|---|
| `c8254a4a` | 2026-08-23 19:33Z | **NOT THIS SESSION'S** — W4 M1+M2 prereg (`cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md`, 632 lines), committed before any compute by the second session. 40.0 core-min predicted, 60 ceiling, decision rule on the complete-vs-incomplete factorization axis registered |
| `6c6de745` | 2026-08-22 21:01Z | supervisor append for the A6 close: **L-242** (a trivial baseline at a deliberately wrong step is irreproducible in magnitude AND sign: −28.75 vs +152.94 from identical configuration), **N-D19..N-D21**, **D464**, `LADDER_A_STATUS` **row 37**. All four aggregates recomputed independently by the supervisor before recording (8-graded 1.0432%, 3-subset reproduces 1.0099%, 5-bought 1.4185%, 9-folded 1.0440%) |
| `4fd84e7b` | 2026-08-22 20:58Z | lane draft rows for the supervisor's append helper (A6 remaining-five) |
| `9d5029e8` | 2026-08-22 20:57Z | *A6 N=16 remaining five components — RESULTS*: **PASS on the graded set of 8, aggregate 1.0432%, zero sign flips, every component ≤ 5%**; the five bought (twist 1,2,4,5 + patchV 0) fall from 57.62/67.93/57.06/90.17/82.79% at the predecessor's noise-dominated step to 1.359/1.733/1.032/0.389/0.569% at noise-sized steps — the adjoint never moved, only the reference. twist idx6 stays FLAGGED and excluded by name (clearance 2.42×, plateau 83.53%). 9 predictions, 9 HIT. **39.15 core-min / $0.0335** of a 60 ceiling |
| `da475770` | 2026-08-22 20:26Z | L-241 CORRECTION via `scripts/append_record.py` (first DAFoam use) |
| `088e052f` | 2026-08-22 20:24Z | **`DAFOAM_CHARTER.md` v1.0b → v1.0c** (§13 enforceability PROPOSAL, unratified) + L-241 |
| `92185911` | 2026-08-22 20:20Z | supervisor append for the A3 rung-2 verdict: L-239, D462, N-D18, status row-12 split |
| `27ce5799` | 2026-08-22 20:18Z | *A3 rung-2 patched-IDWarp arm — RESULTS*: **PASS, and the first measured A/B pair where the rotation patch degrades** a gradient the shipped toolchain had right. 85.950 core-min / $0.0735 |
| `757eccf0` | 2026-08-22 20:04Z | ADF primal non-reproduction prepared as a defect candidate, **NOT FILED ANYWHERE, NOT FILING-READY** (D460) |
| `66f42398` | 2026-08-22 19:52Z | *A6 N=16 fixed FD reference — RESULTS*: PASS on 3-component subset 1.0099%; forward-AD found NOT AVAILABLE (nan). 63.166 core-min / $0.0540 |

Older rows (A4 twin PASS `f9a59d47`, A2 per-component `79679a84`, A3 prereg chain, Phase 3B `804c3fd8`): see this section at `git show 6c6de745:docs/LAB_STATE.md` and `git log`.

**Live jobs:** **none owned by this session.** The second session's W4 M1+M2 run had not launched a container as of 19:35Z; its prereg is committed and its run root staged. Box otherwise: 4 heat-transfer solvers, 12 cores free, load1 ~4.2.

**Rungs lacking verdicts:**

| item | state |
|---|---|
| **A6 N=16** | **COMPLETE at 8 of 9 — PASS, aggregate 1.0432%, zero sign flips** (status row 37). twist idx6 NOT A RESULT (FD-ungradeable at any step). **N=29 stays NOT RUN**; its gate has two registered readings — charter-verbatim NOT MET / subset-complete GATE REACHED — and **the choice is Sanaa's (D464)**, as is the ~5 core-min ninth-component arm |
| **A3 patched column** | rung 2 MEASURED — PASS (row 12, degrades vs shipped, N-D18); **rungs 1, 3 and the 399,360 campaign PENDING (row 12b)** — claimed by this session for pre-registration |
| **ADF primal non-reproduction (D460)** | defect candidate NOT FILING-READY on two named blockers: full 63-search/10-venue novelty sweep (0 compute) and characterisation sweep 1 (~5 core-min, decides conditioning/diagnosability vs AD correctness). Box now free — claimed by this session, lane dispatching |
| **B3 decomposition peak RSS** | NOT MEASURED (no 5 s watcher on that chain) — claimed by this session, lane dispatching |
| **W4 / NASA hump adjoint M1+M2** | **prereg committed `c8254a4a` by the second session — THEIRS.** This session does not touch it |
| **A2 `CD/shape` PATCHED idx46** | caveat **RECORDED** — status rows 34-35 carry it; whether adjoint or FD artefact stays NOT established (sweep 207-238 core-min, not bought) |
| **B3 Stage 4** | BLOCKED by construction — Sanaa's fork-adoption call |

**Two-row verdicts standing** (shipped / patched): A1 GATE FAIL / PASS; A2 PASS / PASS with the idx46 per-component caveat (rows 34-35), optimisation NOT A RESULT; A3 primal GATE REACHED, adjoint BLOCKED (399k) — sweep rungs 1-2 PASS, rung 3 GATE FAIL (conditioning) / rung 2 PASS (degrades — N-D18), other sizes PENDING; A4 PASS / PASS (patch immaterial; CD −7.478 %); A5 GATE FAIL / PASS; A6 BLOCKED (full) — N=16 GATE FAIL (shipped, superseded reference) / **PASS at 8 of 9, aggregate 1.0432%, twist idx6 NOT A RESULT** (patched, fixed reference; rows 36-37). B2 PASS; B3 BLOCKED / PASS.

**Next actions:** (1) ADF characterisation sweep 1 + full novelty sweep — prereg committed before compute, ~5 core-min. (2) B3 decomposition RSS watcher re-run (cheap). (3) A3 rung-1 and rung-3 patched-column preregs (box has 12 free cores; np=4 launch gate now trivially met). (4) W4 — held, second session's item. (5) Supervisor docs commit per verdict as they land.

**On Sanaa's desk:** **D464 — the N=29 gate reading** (charter-verbatim NOT MET vs subset-complete GATE REACHED; the gap is one ~5 core-min arm). **R11 adoption evidence is two-sided** — A3 rung 2 measured the patch degrading; adoption is case-dependent, her call. **MemAvailable floor 12 GiB** ruling (Lane B's measured case for 6 GiB on primal-only arms; not lowered by any agent). **Five upstream defect drafts, all NOT FILED** (D-A/D-A2, D-B/D-B2, D-C, D-E + the ADF candidate `757eccf0`) — filing is hers alone. **B3 Stage 4 fork-adoption.** The near-zero sign-flip-under-a-passing-norm class (A1 idx6, A5 idx16, A2 idx46). **`DAFOAM_CHARTER.md` §13 enforceability PROPOSAL** (v1.0c, unratified).

**Blocked:** B3 Stage 4 (Sanaa); A6 N=29 verdict wording (Sanaa, D464); A6 full-size rung (BLOCKED, unchanged); ADF filing readiness (the two blockers above, now in work).

**⚠ Integrity flags on frozen records, none quoted from:** `A1_naca0012_incompressible.md:167-172` (refuted mechanism, zero strike); `A5_ubend_internal.md:194-196` (in-band set mismatch); `A2/grading_confirmation/RESULTS.md` §1 ("no sign flip anywhere in A2") falsified at PATCHED idx46.

**Shared-board rule in force (chief, 2026-08-22):** `docs/LAB_STATE.md` is never written in the shared worktree. Each board commit rebuilds from `git show $H:docs/LAB_STATE.md`, replaces only `## dafoam` (`scripts/lab_state_section.py --team dafoam --rev $H --out <scratch>`), stages by `git hash-object -w` + `update-index --cacheinfo` in the private index, and the diff-tree must be confined to this section. Carried in every lane brief.

**Record-append rule in force (chief, `0286bb2a`):** every append to `DOCKET.md`, `LESSONS.md`, `NUMERICS_KNOWLEDGE.md` goes through `python3 scripts/append_record.py` (merge form) with `scripts/check_record_reconciliation.py` run BEFORE the edit. Carried verbatim in every DAFoam lane brief.

**Charter:** `DAFOAM_CHARTER.md` **v1.0c** (2026-08-22) — the §13 enforceability PROPOSAL is unratified and awaits Sanaa.

**Images:** `dafoam-idwarp-rot:v1` (only image carrying the rotation patch, md5 `85f59e87…`), `dafoam-subpclu:v2` (PCLU), `dafoam-kspopts:v1`, `dafoam-team:v1` (`0b3c94c33a15`, both patches, ends `USER dafoamuser` → `--user root` for bind mounts). *The hash is the identity; the version string is not.* F6 series under `cases/dafoam/` is plain `simpleFoam`, not DAFoam work. **The stale shared index (577 staged deletions at 19:28Z) is the chief's call — inspect, never revert; all dafoam working-tree files verified identical to HEAD at 19:35Z.**
## heat-transfer

**Section last written:** 2026-08-23T19:45Z by heat-transfer-supervisor
(re-formed 2026-08-23 after the 2026-08-22 session limit).

> **Timestamp correction, 2026-08-23 19:45Z, by the section's owner.** The
> previous revision's stamp read 19:55Z but its commit (`cdb5cc0b`) is dated
> 19:27:03Z -- the stamp was asserted, not read from the clock (the `bd3edfe8`
> defect class; same disease the dafoam section corrected). Every time in this
> revision is `date -u` output or a log line read at 19:42Z.

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
- **T1b L4: `R_10k_x` DONE under the strict rule** (rc=0, End, 20000/20000).
  The prior board's VERIFY on its endTime is **resolved: 20 000 is the
  registered design** (`T1b_L4_AMENDMENT.md` §4 table: 20000/80000/80000/
  80000). `analyse_t1b_L4.py` refuses partial grading by design — no L4 row
  is graded until all four x-cases carry DONE. A completion watcher is
  running (30-min poll for STATUS.R_30k_x/R_100k_x/R_300k_x, deadline guard
  2026-08-27); on completion: mark → comparator → grade the (m,f,x) triples
  under the amended Roache rule.
- **T3 ext1 health check (untouched, per D452):** 7/8 extensions complete
  rc=0 (R_c 80000, R_m 36000, P_m 36000, C_lam_m 80000, W_m 80000, D_m
  28000, O_m 46000). **`R_f` alive** (pid 757934) at 47 511/78 000 as of
  19:15Z, pacing at or ahead of the 2026-08-25T14:54Z ETA. Comparator re-runs
  only after all eight.
- **Strict-rule verification of the eight finished runs (this supervisor,
  19:34-19:42Z).** The seven finished T3 ext1 arms now carry DONE markers from
  the frozen `mark_done_t3_ext1.py` (selftest 14/14 first, `__pycache__`
  cleared; dry-run 7/7, then real run 7/7 PASS, ext1 included) -- the 7/8 line
  above was a STATUS rc=0 read, not the six-test rule; this is the rule, age
  guard included. `DONE.R_f` is ABSENT from disk though tracked in HEAD:
  correct, refusing-direction state while its extension runs (removal not
  witnessed by this session; consistent with the tool's registered behaviour);
  the deletion is committed with this revision so the frozen comparator cannot
  read a half-finished extension. `R_10k_x` re-verified independently:
  `mark_done_t1b_L4.py` 1/4 PASS (three siblings correctly refuse, still
  running), marker idempotent with `cdb5cc0b`'s. All six marking/grading
  scripts hashed byte-identical to their HEAD blobs before any output was
  believed. The seven `STATUS_EXT1.*` evidence files (previously untracked)
  are committed with this revision.

**Live jobs — 4 solvers, all this team's, all single-core
`buoyantBoussinesqSimpleFoam`.** Reading taken 2026-08-23T19:42Z (`ps`,
`readlink /proc/<pid>/cwd`, last `Time =` line of each log). **Do not touch
them.** The L4 completion watcher is pid 1102509 (30-min poll for the three
STATUS files, deadline guard 2026-08-27).

| pid | cwd | iteration / endTime | ETA |
|---|---|---|---|
| 442445 | `T1_runs/R_300k_x` | 41 245 / 80 000 | ~2026-08-26 |
| 450274 | `T1_runs/R_100k_x` | 36 947 / 80 000 | ~2026-08-26 |
| 488219 | `T1_runs/R_30k_x` | 34 835 / 80 000 | ~2026-08-26 |
| 757934 | `T3_runs/R_f` | 48 083 / 78 000 | ≤ 2026-08-25T14:54Z |

**Rung verdicts on record** (unchanged from 2026-08-22 except T10a's arm):

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

**Lanes live (dispatched 2026-08-23 ~19:40Z, 2 of the cap of 3):** (a) F14
VERIFY sweep -- read-only verification of the K0b (D403 rerun + D406 repair),
K0cG/K0cP/K0cQ/K0cR, K2e and KV1 recorded verdicts against their records and
run trees; commits nothing. (b) T9aH successor pre-registration (re-graded
T9a under `Gauss harmonic`, the H-4 follow-through named by T9a-D) -- drafts
and commits the prereg, then STOPS; no launch before this supervisor's
personal check of the committed prereg, grading path and cost.

**Next actions:** 1. L4 completion (watcher armed) → grade the four (m,f,x)
triples. 2. T3 ext1 completion (`R_f`) → comparator re-run over all eight →
T3 re-graded under the frozen §7.1 gates. 3. T5 waits on Sanaa's
INTERPRETATION rulings. 4. T10a-R successor questions (whether any rung arms
a band from a triple whose implied p exceeds the observed error decay —
L-244) belong to verification, flagged, not taken here. 5. T9aH: committed
prereg -> supervisor's personal check -> launch decision (lane live). 6. F14
VERIFY flags: clear to BACKED or record GAP per the sweep lane's report.

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

**Section last written:** 2026-08-23 by cfd-supervisor (first owner-written fill; replaces the harness first fill of 2026-08-22).

**Last commit:** see this section's git history — this supervisor's session of 2026-08-23 commits the MESH_STANDARD cross-ref fix + this board rewrite; two lanes commit their own records (GEN_ALT campaign record; DPW8_V2 L4 diagnosis prereg). Before that the team's last commit was `cc4f1a64` (2026-08-18), five days idle.

**Live jobs:** no solvers owned by cfd. Two lab-lanes dispatched 2026-08-23 (~19:45Z): (1) GEN_ALT campaign write-up, zero compute; (2) DPW8_V2 L4 divergence-diagnosis pre-registration — **freeze-then-STOP; launch only after supervisor verifies the freeze commit** (personal check #4). Diag budget when launched: 2 arms × ~30 core-min ≈ $0.05, cap 150 core-min. Do not touch the 4 heat-transfer `buoyantBoussinesqSimpleFoam` solvers.

**Resolved this session (2026-08-23, supervisor's own reads):**
- **W2 VERIFY closed.** `W2_sparta_runs/setup_sparta_case.sh` mtime 2026-08-22 17:38 = the closure team's H-7 libs-institutionalization lane; committed 17:48 in `5162ec8e`; disk is byte-identical to HEAD (the `MM` was the stale shared index). Diff read personally: adds only an L-221 `grep -q libspartaTurbulenceModels` assert that refuses on a missing libs entry. Benign; W2_sparta stays closed.
- **GEN_ALT is GRADED, not unwritten.** The prereg at `verification/runs/GEN_ALT_runs/GEN_ALT_PREREGISTRATION.md` carries a full scored Outcome (2026-08-08): verdict **GENERATOR-OWNED** per the pre-declared rule (blockMesh max-AR refinement factor ×0.945 vs pyHyp ×1.71 at matched counts; near-wall AR 37.4 vs 87.6-class; G1/G2 HELD, G3 refused by the born-clean gate at non-ortho 70.13/70.11 > 70 — no solve ever ran, by refusal, honestly). Freeze chain verified: prereg frozen `9c4fbef4` 23:16:04Z, outcome `41f0e1df` 23:19:01Z, moved in `a1fbe127`. Cost ≈0.4 core-min. What was missing was only the campaign-level record — lane dispatched to file it in `verification/campaign/`.
- **DPW8_V2 L4 decided: DIAGNOSE, not abandoned.** The campaign record's §3-CORRECTION already establishes L4 **DIVERGED deterministically** (k blow-up from ~iter 14, reproduced bit-for-bit; mesh quality and aspect ratio ruled out; root cause open). Supervisor decision 2026-08-23: run the record's own cheapest decisive experiment — two short pre-registered arms, one change per run (Arm A relaxation only; Arm B turbulence-convection scheme only), positive-control-gated grading. The gate rung itself remains **NOT GATED** until the diagnosis lands; any repaired full L4 (and the §3b family-consistent linear-solver question) is a successor decision.
- **MESH_STANDARD consistency check done (they were never to be merged).** `docs/standards/MESH_STANDARD.md` (v1.2, single-mesh quality gates + birth certificate + §7 marine) and `docs/MESH_STANDARD.md` (grid-family sizing/scatter) are complementary, both flag the name collision on their face, cross-refs sound, one-home-per-fact respected (§7.3). One staleness found and fixed this session: the family doc's header cited the companion as v1.0/2026-07-25 while its own Sources said v1.2 — header updated, no gate value touched.

**Open run families — triaged 2026-08-23 (read-only lane sweep, supervisor spot-checked; the 2026-08-22 first-fill table had 3 rows WRONG and 5 PARTLY WRONG):**

| family | actual state, from the records |
|---|---|
| **DPW8_V2 L4** | DIVERGED, root cause open; diagnosis prereg in flight this session (see above). L1/L3 PASS stand |
| **F5b** | Feasibility **PASS** on record (`F5bc_unsteady_statistics.md`); Physics and Gate rungs literally "[to be completed]" — **PENDING**, not ungraded. Run dir really is one file. Trap: `F5b_cylinder_re100_act.json` is a DIFFERENT case (Re=100 shedding act). Next rung ≈25–35 core-min |
| **F5c** | Effectively closed: headline withdrawn to unmeasured; 1.313 H was RELAXATION (misattributed, `F5C_LEVER_ISOLATION_RESULTS.md`); **Stage B was NEVER chief-approved** ("Stage B NOT approved and not run", header of `F5C_STAGE_A_RESULTS.md`) and O3 firing makes it moot. First-fill's "chief-approved Stage B" was wrong. A3-vs-A4 disagreeing 4.224 H on a relaxation-only change is residual-free proof neither solve converged |
| **R4 (Ahmed turn)** | First-fill row WRONG: leg 2 ran 2026-08-10, **n = 4 of 4** (`R4_AHMED_C3_LEG2_RESULTS.md`; B3 broad scatter R = 0.324 vs 0.28 bar, near miss; DISSOLVES confirmed). Turn **WITHDRAWN as a feature** (chief ruling `8f5bf878`, `R4_AHMED_TURN_WITHDRAWAL_2026-08-10.md`). No SIGNAL/NOISE verdict claimed — the c4 CI leg was deliberately not taken. Optional n=7 (~3.1 core-min/draw) needs chief's word. NOT the closure R4 SpaRTA build |
| **F12** | CONFIRMED orphaned prereg (chief: "the standing IOU"); `F12_runs/` is `reference/` only. **Rule-12 defect: the prereg carries NO cost figure** — needs a costed addendum before it can be scheduled at all |
| **F7a re-gate** | Spec frozen AND **the gate verdict is already taken from tracked data: FAIL at +11.03% max deviation** (prereg §1's own words). What is unexecuted is the diagnostic list; cheapest is **R0, 0 core-min** (literature recovery, arXiv:2108.08769 front-extraction). R1a (760–1,520 core-min) recommended against by the record itself. Live unexplained: 23.3% code-to-code offset |
| **MODEL_FORM successors** | First-fill row WRONG: all three preregs carry **executed outcome blocks** (FPE rescue 18.16 core-min; H ext 41.66; H hills 29.18). Verdicts are refusals by the n<3 rule ("containment REFUSED — no band exists at n = 1"). Substantive finding: a family-convergence wall on the hills. CLOSED as registered; row corrected |
| **mbc_retry, uq_batch** | CONFIRMED — both self-labelled by their own 2026-08-18 READMEs: "Nothing here is graded." No action; any rung wanting either outcome re-runs it |
| **F4** | θ=32.5°/35° gate cases still held — correct — but the row hid the work: Settles reference **overturned and replaced** with Kussoy & Horstman TM 101075, ±30% pass band pre-registered before the cases run; θ=20° warm-up SIGFPE with **5 mechanisms eliminated, root cause open** (`NOT_PASSING_REGISTER.md` Group 3); custom `rhoCentralFoamBounded` source at `verification/runs/F4_runs/swbli_cylflare/`. Named next lever, **zero compute**: source-read of `rhoCentralFoam` directional flux reconstruction at cells with two boundary faces |
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
what is stale is the framing — it documents a WSL2/docker phase-1 adapter
workflow on a native-Linux AWS box, and `sdk/docker/Dockerfile.openfoam-worker`
**does not exist** though the doc gives a build command for it. Zero-compute fix
pending: flag the container section, re-scope WSL as historical.
`docs/OPENFOAM_SOLVER_BUILD.md`: two dead `demo-output/website/...` paths for
`rhoCentralFoamBounded_src` **fixed this session** (source verified on disk at
`verification/runs/F4_runs/swbli_cylflare/`).

**Next actions:** (1) grade the DPW8_V2 L4 diagnosis arms when they complete,
then decide the successor (family-consistent repaired L4, or record the family
as stopping at L3 with the diagnosed cause). (2) F4 SIGFPE next lever — the
zero-compute source-read of `rhoCentralFoam`'s directional flux reconstruction
at double-boundary-face cells. (3) F7a R0 literature recovery, 0 core-min.
(4) F12: costed addendum question to the chief — the prereg is disqualified as
a proposal until priced (rule 12). (5) F5b physics rung (~25–35 core-min) as
the next cheap compute candidate. (6) `docs/OPENFOAM.md` re-scope, zero
compute. Same dead-path class as the fixed one persists in
`F4_hypersonic_blunt_body.md`'s artifact lines — sweep candidate.

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

**Section last written:** 2026-08-23T19:38Z by verification-supervisor (first
owner-written fill; supersedes the 2026-08-22 harness first fill, whose
"rule on the VM2026R1 canonical home" next-action over-reached — D-6 is with
Sanaa and neither copy is touched).

**Last commit:** this commit (CROSS_TEAM_GATE_AUDIT.md pass 1 + this board
update). Before it: `090c070c` (lane) — Ansys manual `.txt` sidecar, R8 pair
complete, L-144 title-page verified from the extracted text (*"Ansys Fluid
Dynamics Verification Manual … Release 2026 R1, March 2026"*), 368,949 bytes,
290 pages, clean; `50175beb` — L-245 filed; `6ae77c79` — LAB_STATE repair.

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

**Live jobs:** none owned by this team. (Verified 2026-08-23T19:36Z by `ps aux`:
4 `buoyantBoussinesqSimpleFoam` solvers live — pids 442445, 450274, 488219,
757934 — all heat-transfer's; never touched.)

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
| **`GATE FAIL` vs bare `FAIL`** | D-5, referred, unruled, with Sanaa. Not settled silently; `check_verdict_cells.py --strict-fail` re-run dispatched for a current count (status reading only) |
| **Comparator freeze audit** | baseline two of six frozen (charter §2d.1: K0cQ +237 s, K0cR +422 s; K0cS UNFROZEN-repaired, K0cX UNFROZEN-disclosed, two AMENDED_AFTER/W-4). Re-run across the current comparator population dispatched to a lane 2026-08-23 |
| **The six standing audits** | file mtimes measured 2026-08-23: `DEAD_LEVER` 08-11, `EXTERNAL_REFERENT` 08-16, `FAIL_OPEN_GATE` 08-11, `H4_ALLOCATION` 08-12, `LEDGER_HEADLINE` 08-11, `SWEEP_REFRAME` 08-11. First-fill VERIFY resolved: **none re-run since 2026-08-16, confirmed.** Re-sweep dispatched to a lane 2026-08-23 |

**Freshness flag:** `verification/certificates/`, `credibility/`, `monitor/`
all last written 2026-08-16 19:03 (verified by `ls`); nothing this team owns has
moved since.

**Cross-team gate audit — standing mandate.** Targets, updated with the material
new at HEAD `9e82321b` since the first fill:

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

**Next actions:** (1) DONE — Ansys manual sidecar (`090c070c`);
(2) lane: `check_comparator_freeze.py` re-run + `check_verdict_cells.py
--strict-fail` current count; (3) lane: six standing audits re-sweep with dated
amendments; (4) DONE — cross-team gate audit of R5C and T10a-R, both SOUND, recorded in
`docs/CROSS_TEAM_GATE_AUDIT.md` pass 1; next audit targets are that file's §3
open list (A4, A6 surface-caveat, Wu2018 falsifier, T1b after 08-26, T10a
controls); (5) prepare — not act on — the
VM2026R1 R6/R8 filing analysis for Sanaa's D-6 ruling, including the dead
partial transfer finding above.

**On Sanaa's desk:** `RESULT_PRIORITY_CHARTER` v0.5 orderings; the `GATE
FAIL`/bare-`FAIL` ruling (D-5); the VM2026R1 canonical home (D-6) — now with
the finding that the second copy's transfer is dead at 10/123 files, and with
the prepared ruling memo **`docs/VM2026R1_FILING_ANALYSIS.md`** (three options,
A recommended: outside-git home per the closure-data pattern + committed sha
manifest; the manual-basename R8 rename rides along as §4). Analysis only —
neither copy was touched.

**Blocked:** VM2026R1 grading (blocked on D-6, Sanaa). Nothing else.
