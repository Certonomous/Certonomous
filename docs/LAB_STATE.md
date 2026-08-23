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

**Section last written:** 2026-08-22T18:17Z by dafoam-supervisor.

*Refreshed 2026-08-22T21:01Z by the DAFoam supervisor (Fable), replacing the harness
build's third-party first fill. Live reading: `git log`, `docker ps`, `docker inspect`.*

> **Correction, 2026-08-22 20:15Z, by the section's owner.** Earlier revisions of this section
> carried "refreshed" times and per-commit times that I asserted rather than read — they ran
> ahead of the box clock by up to four hours and one row was dated 2026-08-23. Every commit time
> in the table below is now `git show -s --format=%cd` output, and the refresh stamp is `date -u`.
> Nothing else in the section changed. The board is the handoff channel, so a wrong timestamp on
> it is a defect in the same class as a wrong number in a record, not a cosmetic one.

**Last commits (newest first):**

| sha | committed (UTC) | what |
|---|---|---|
| *(this commit)* | 2026-08-22 | supervisor append for the A6 completion: **L-242, N-D19..N-D21, D464** (all through `append_record.py`, reconciliation PASS first), `LADDER_A_STATUS` row 37 |
| `9d5029e8` | 2026-08-22 | *A6 N=16 remaining five components — RESULTS*: **8 of 9 graded, aggregate 1.0432%, zero sign flips**, `twist` idx6 flagged by name. Nine predictions, **nine HIT**. 39.15 core-min / $0.0335 of a 60 ceiling, zero waste. Re-bought trivial baseline returned **−28.75 against the prior run's +152.94** — a wrong-step probe is irreproducible **in sign** |
| `baf4e68e` | 2026-08-22 | *A6 N=16 remaining five components — pre-registration*, committed before launch, freeze verified twice |
| `da475770` | 2026-08-22 20:26Z | L-241 CORRECTION appended **through `scripts/append_record.py`** (first DAFoam use; reconciliation PASS before the edit): recomputation catches arithmetic on rounded inputs, not a wrong model of a quantity — the lane's two errors had different mechanisms. **Disclosure:** `088e052f` appended L-241 by `cat >>` minutes after `0286bb2a` made the helper mandatory; verified after the fact as a byte-pure append (0 deletions) |
| `088e052f` | 2026-08-22 20:24Z | **`DAFOAM_CHARTER.md` v1.0b → v1.0c**, additive: §13 gains a dated note and a **PROPOSAL** — §13 audits the charter's clauses for enforceability, nothing audits a *pre-registration's* own registered thresholds, and A3 rung 2 proved a prereg can invent a guard nothing can execute. Left a PROPOSAL, not a clause: making it binding is Sanaa's call. Plus **L-241** (a ratio of two rounded percentages is not the ratio of the quantities) |
| `0f56460d` | 2026-08-22 20:23Z | *A3 rung-2 correction* (lane): published ratio **9.22× → 9.2084×**, formed from printed percentages instead of raw values; quote-and-strike per L-32, no verdict, band, gate, prediction score or cost moved |
| `92185911` | 2026-08-22 20:20Z | supervisor append for the A3 verdict: **L-239** (a registered stop with nothing wired to trigger it is not a guard), **D462**, **N-D18**, `LADDER_A_STATUS` addendum splitting row 12 and striking the file's own "every measured A/B pair improves" reading |
| `27ce5799` | 2026-08-22 20:18Z | *A3 rung-2 patched-IDWarp arm — RESULTS*: **PASS**, and the **first measured A/B pair where the rotation patch degrades** a gradient the shipped toolchain already had right. 85.950 core-min / $0.0735 of a 120 ceiling; 12 HIT / 5 MISS; self-reported guard breach at §9.1 |
| `baf4e68e` | 2026-08-22 20:09Z | *A6 N=16 remaining five components — pre-registration* (Lane D), committed before launch; freeze verified blob-for-blob. Steps derived mechanically from the stored \|J\| so every registered step predicts clearance ≥ 5; the prereg's own void condition fired on a `run_arm.sh` md5 mismatch, so the trivial baseline is **re-bought** rather than declined: 11 entries, 23 primals, 40.3 core-min predicted against a 60 ceiling |
| `2216d5ea` | 2026-08-22 20:06Z | supervisor append: **L-234** (a novelty search needs a nonsense-token control — a pinned Discussions thread is returned for every query), **D460** (the ADF defect candidate and its sweep) |
| `757eccf0` | 2026-08-22 20:04Z | *ADF primal non-reproduction prepared as a defect candidate* — `cases/dafoam/DEFECT_CANDIDATE_adf_primal_nonreproduction.md`, 329 lines, **NOT FILED ANYWHERE, AND NOT FILING-READY** in its opening lines; novelty sweep RUN (39 searches, 4 venues, read-only) — **no prior art**; class UNDETERMINED pending one 5-core-min arm |
| `ff5d2327` | 2026-08-22 19:56Z | supervisor append for the A6 verdict: **L-233, D459, N-D13..N-D17**, `LADDER_A_STATUS` row 36. Claim verified by the supervisor personally against the arm logs before belief |
| `66f42398` | 2026-08-22 19:52Z | *A6 N=16 fixed FD reference — RESULTS final*: **PASS on a 3-component graded subset, 1.0099 %, zero sign flips**; all three predecessor sign flips were FD noise; `twist` idx6 flagged and excluded; forward-AD reached for and found NOT AVAILABLE (nan) — 63.166 core-min / $0.0540 of a 120 ceiling |
| `674cab89` | 2026-08-22 19:45Z | *A3 rung-2 Amendment 2 v1.2* (lane): Amendment 1's np=1 configuration **withdrawn as refuted by its own measurement**; arms revert to the frozen §2 np=4 configuration; **no gate, threshold, cap or label altered** — only the launch condition, now `free_cores >= 4 AND MemAvailable >= 12 GiB` (free_cores = 16 − median-of-5 runnable count). Frozen body + Amendment 1 verified byte-identical through line 705 **by the supervisor personally**; script diff read as a diff by the supervisor: **68 insertions, 0 deletions, 0 modifications**, grading path untouched. Colouring cache `dRdWColoring_4.bin` md5 `a2e5f317…` proven identical to the graded stock arm's. Worst case 102.150 of the 120 ceiling **by construction** |
| `3a06b371` | 2026-08-22 19:43Z | supervisor append for the A3 attempt: **L-232, D458, N-D11, N-D12**, `LADDER_A_STATUS` row-12 footnote. Row 12 stays **PENDING — NOT MEASURED**: the np=1 re-price was refuted by measurement (colouring 3.03× bigger at one rank), the arm stopped at 11.950 core-min rather than spend 70.0 on a timeout inside the colouring |
| `972cb647` | 2026-08-22 18:51Z | *A6 N=16 fixed reference — interim RESULTS* (queue still running): forward-AD reachable and runs for the first time in the lab (`ADF-Deriv: -2.417e-05`), but **the ADF build does not reproduce the plain build's primal** on A6 N=16 (energy diverges at 8th s.f., GAMG 5 vs 7 sweeps, NaN by iteration 10; `libDASolverADF.so` md5-identical across images → shipped-toolchain finding, **new defect class candidate, characterisation owed**); `DASolver.C:188` can print 'satisfied the prescribed tolerance' on a reset `primalMaxRes` (diagnosability defect); FD gate passes for twist 0/3, patchV 1 at step 3e-2, twist idx6 never clears; 7.766 core-min so far of 120 |
| `85397209` | 2026-08-22 19:27Z | supervisor docs commit for the A4 verdict and the A2 finding: **L-228..L-230, D455..D456, N-D8..N-D10**, `LADDER_A_STATUS` addendum rows 31-35, `INDEX` addendum (four new dirs). Board update missed in that commit, landed here |
| `f9a59d47` | 2026-08-22 18:30Z | *A4 shipped-image optimisation twin — PASS, and the rotation patch did not matter to this optimisation*: 6 majors, CD −7.4775 %, endpoint 0.3112 % PASS, patched baseline 0.33929 % PASS; 13.616 core-min / $0.0116 |
| `239a007f` | 2026-08-22 18:01Z | *A4 shipped-image optimisation twin — pre-registration* |
| `a94e8317` | 2026-08-22 18:23Z | *A3 rung2 patched-IDWarp arm — pre-compute amendment v1.1*: np=4 → np=1 twins (`np1_shipped`, `np1_patched`) + `np1_control`, because the T-family holds the box to 08-23..26 (poll min load 20.40); frozen body unchanged (renumbered lines: 0); only 0.200 core-min pre-flight spent. Now holding on MemAvailable ≥ 12 GiB (9.1 GiB while A6/A4 containers are resident) |
| `79679a84` | 2026-08-22 18:10Z | *A2 per-component table* — zero compute. **PATCHED `CD/shape` carries a sign flip at idx46** (analytic `+2.27367571e-06` vs FD `-2.52460969e-06`) that `A2/grading_confirmation/RESULTS.md` §1 says does not exist; SHIPPED `CD/shape` has 7/96 components beyond 15 % (worst idx18 `-360.75 %`) under a 1.71 % aggregate. All published aggregates reproduce to 7-8 s.f. Log-integrity defect: MPI ranks splice `check_totals` arrays mid-number on one stdout; 1 of 4 printed CD copies usable, 0 of 4 CL copies |
| `8028d9ab` | 2026-08-22 18:09Z | *A6 N=16 fixed FD reference — pre-registration*: two stages on `dafoam-idwarp-rot:v1`, np=1; P1 predicts the 1e-8 primal gate FAILS at 6000 iters (residual flat from iter 100); forward-AD reachability probed (`libDASolverADF.so` carries `DARhoSimpleCFoam`, 28 symbols); 74.0 core-min registered, 120 ceiling |
| `a5605f54` | 2026-08-22 18:03Z | *A3 rung2 patched-IDWarp arm — pre-registration* (np=4, 42,120 cells, ceiling 120 core-min); staged and pre-flighted (0.200 core-min), **holding at its launch gate** (load ≤ 8 never met; min seen 20.40) |
| `804c3fd8` | 2026-08-21 | Phase 3B (final): ILU-shift class measured dead, `dafoam-team:v1` built and gated, B3 free of the decomposition defect |

**Live jobs (reading 18:17Z; both np=1, `--cpus=1`, launched under a disclosed
launch-condition amendment because the T-family holds 12 of 16 cores until
2026-08-23..26):**

| container | host pid | run root / cwd | item | ETA |
|---|---|---|---|---|
| `p3a6_s1b` | 802799 | `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/s1b` | A6 N=16 fixed reference, Stage 1 (primal-convergence gate + forward-AD probes), `--memory=12g` | Stage 1 ~20-40 min; Stage 2 contingent, ~1.5 h |
| `p3a6rem_rem` | live | `/home/ubuntu/certonomous-runs/P3-a6-n16-rem/rem` | A6 N=16 **remaining five components** (twist 1,2,4,5 + patchV 0) + re-bought trivial baseline, np=1 `--cpus=1 --memory=12g`, `timeout 3600` (= the 60 core-min ceiling at one rank); launched 20:12Z on the second preflight poll (free_cores 3) | ~40 min |

**Rungs lacking verdicts:**

| item | state |
|---|---|
| **A3 patched column** | **rung 2 MEASURED — PASS** (row 12); **rungs 1, 3 and the 399,360 campaign stay PENDING** (row 12b). The patch **degrades** both warp-crossing rows here against a bit-identical FD reference — first such case on the ladder (N-D18) |
| **A6 N=16** | **COMPLETE at 8 of 9** — aggregate **1.0432 % PASS**, zero flips, `twist` idx6 flagged by name and structurally ungradeable at any feasible step. **N=29 stays NOT RUN**: the gate has two registered readings (charter-verbatim NOT MET / subset-complete GATE REACHED) and **choosing between them is Sanaa's**, D464 |
| **ADF primal non-reproduction** | **defect candidate prepared** (`757eccf0`, D460, N-D16): NOT FILED and NOT FILING-READY on two named blockers — the full 63-search/10-venue sweep (0 compute) and sweep 1 (~5 core-min), which decides whether the class is *conditioning/diagnosability* or *AD correctness*. Sweep found **no prior art**. Characterisation arms approved in principle, held until the box frees |
| **A4** | **complete** — the 2×3 table has no assumed cells (status addendum rows 31-33) |
| **A2 `CD/shape` PATCHED** | aggregate 0.0506 % PASS now carries a **per-component sign flip (idx46)** — under the band ("ANY sign flip ⇒ FAIL") the row needs the per-component caveat A5 idx16 got; supervisor to record in `LADDER_A_STATUS` addendum + docket. Whether adjoint or FD artefact: NOT established (a sweep costs 207-238 core-min on A2; not bought) |
| **B3 Stage 4** | **BLOCKED by construction** — Sanaa's fork-adoption call. The rebuild rows are final: BLOCKED (shipped) / PASS (`subpclu:v2`, 667 iters, FD 0.085/0.059/0.199 %, decomposition G1-G3 PASS) |
| **W4 / NASA hump adjoint** | uncharacterised; M1+M2 at 40 core-min unbought |
| **B3 decomposition peak RSS** | NOT MEASURED (no 5 s watcher on that chain) |

**Two-row verdicts standing** (shipped / patched): A1 GATE FAIL / PASS; A2 PASS / PASS
with the idx46 caveat above, optimisation NOT A RESULT; A3 primal GATE REACHED, adjoint BLOCKED (399k) — sweep rungs 1-2 PASS, rung 3 GATE FAIL (conditioning) / **rung 2 PASS, other sizes PENDING**;
A4 PASS / PASS on both the optimisation and the endpoint gradient (patch immaterial; CD −7.478 %); A5 GATE FAIL / PASS;
A6 BLOCKED (full) — N=16 GATE FAIL (shipped, superseded reference) / **PASS on the 3-component graded subset with a fixed reference** (patched). B2 PASS; B3 BLOCKED / PASS.

**Next actions:** (1) A6 is closed at 8 of 9; the only open A6 lever is `useMeanStates` (~5 core-min), which is on Sanaa's desk; A6 Stage 2 only if its
registered gate passes. (2) Resolve the A3 np=4 launch: pre-compute amendment to np=1
twins if the T-family holds the box past the poll window. (3) Supervisor docs commit per
verdict: `LADDER_A_STATUS` dated addendum, L-225+ (re-derive), D453+ (re-derive), N-D8+.
(4) Then: B3 decomposition RSS watcher re-run (cheap), W4 M1+M2 (40 core-min).

**On Sanaa's desk (new, 2026-08-22):** **Which reading of the N=29 gate governs** — charter-verbatim (NOT MET, and no FD arm on this rung can ever meet it) or subset-complete (GATE REACHED). The gap is one component, closable only by `useMeanStates: True` + `fieldAverage`, **~5 core-min / $0.004**, unbought. Two decisions, both hers: which reading, and whether to buy the closing arm.

**On Sanaa's desk (also new):** **R11 adoption evidence is now two-sided.** Every prior A/B pair argued for adopting the patched toolchain; A3 rung 2 is the first measured case arguing against it for a specific case class, so adoption is **case-dependent, not global** — her call, not a lane's. Also: `dafoam-idwarp-rot:v1` is now validated at np>1 (all four ranks loaded the patched `.so` through `-x PYTHONPATH`), closing `patched_build/idwarp_rot/BUILD.md` §6's mixed-stack risk.

**On Sanaa's desk (ruling requested):** the DAFoam launch-gate **MemAvailable floor 12 GiB** — a registered gate threshold, so it stays at 12 until she rules (chief, 2026-08-22). Lane B's measured case for lowering it to **6 GiB for primal-only arms**: the 12 was calibrated on a 9.787 GiB adjoint; the largest peak RSS in the whole A6 fixed-reference item was **1.252 GiB**, and the floor cost **28 min of wall** waiting under another team's `viewFactorsGen` (up to 17.2 GiB). Not lowered by any agent.

**On Sanaa's desk:** now **five** upstream defect drafts — the four standing classes plus the ADF primal non-reproduction (`757eccf0`), which is a *candidate*, not filing-ready. Four upstream defect drafts, all **NOT FILED** (D-A/D-A2 IDWarp
rotation; D-B/D-B2 decomposition + limiter; D-C ksp options override; D-E ILU exact zero
pivot) — filing is hers alone. Fork-adoption decision for B3 Stage 4. Note for her: the
A2 per-component extraction shows the third near-zero sign-flip-under-a-passing-norm
(A1 idx6, A5 idx16, A2 idx46) — a class, not an incident.

**⚠ Integrity flags on frozen records, none quoted from:**
`A1_naca0012_incompressible.md:167-172` (refuted mechanism, zero strike);
`A5_ubend_internal.md:194-196` (in-band set {1,2,16,24,25} vs measured {1,2,24,25,26});
`A2/grading_confirmation/RESULTS.md` §1 ("no sign flip anywhere in A2") falsified at
PATCHED idx46.

**Shared-board rule in force (chief, 2026-08-22):** `docs/LAB_STATE.md` is never written in the shared worktree. Each board commit rebuilds from `git show $H:docs/LAB_STATE.md`, replaces only `## dafoam` (`scripts/lab_state_section.py --team dafoam --rev $H --out <scratch>`, selftest PASS: a planted foreign edit outside the section is dropped, a stray `## ` heading inside it is refused), stages by `git hash-object -w` + `update-index --cacheinfo` in the private index, and the diff-tree must be confined to this section. Disclosed: `a6b43ab3` was committed from the worktree and carried another team's uncommitted section edits (their own text, no harm). Carried in every lane brief.

**Record-append rule in force (chief, `0286bb2a`):** every append to `DOCKET.md`, `LESSONS.md`, `NUMERICS_KNOWLEDGE.md` goes through `python3 scripts/append_record.py` (merge form; refuses edits inside committed bytes, exit 2; asserts max+1 per series, exit 3) with `scripts/check_record_reconciliation.py` run BEFORE the edit; the `git show HEAD:… > file` rebuild recipe is retired. Carried verbatim in every DAFoam lane brief.

**Charter:** `DAFOAM_CHARTER.md` **v1.0c** (2026-08-22) — the §13 enforceability PROPOSAL is unratified and awaits Sanaa.

**Images:** `dafoam-idwarp-rot:v1` (only image carrying the rotation patch, md5
`85f59e87…`), `dafoam-subpclu:v2` (PCLU), `dafoam-kspopts:v1`, `dafoam-team:v1`
(`0b3c94c33a15`, both patches, ends `USER dafoamuser` → `--user root` for bind mounts).
*The hash is the identity; the version string is not.* F6 series under `cases/dafoam/`
is plain `simpleFoam`, not DAFoam work.

---

## heat-transfer

**Section last written:** 2026-08-23T19:55Z by heat-transfer-supervisor
(re-formed 2026-08-23 after the 2026-08-22 session limit).

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

**Live jobs — 4 solvers, all this team's, all single-core
`buoyantBoussinesqSimpleFoam`.** Reading taken 2026-08-23T19:15Z. **Do not
touch them.**

| pid | cwd | iteration / endTime | ETA |
|---|---|---|---|
| 442445 | `T1_runs/R_300k_x` | ~40 457 / 80 000 | ~2026-08-26 |
| 450274 | `T1_runs/R_100k_x` | ~36 000 / 80 000 | ~2026-08-26 |
| 488219 | `T1_runs/R_30k_x` | ~34 324 / 80 000 | ~2026-08-26 |
| 757934 | `T3_runs/R_f` | 47 511 / 78 000 | ≤ 2026-08-25T14:54Z |

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

**Next actions:** 1. L4 completion (watcher armed) → grade the four (m,f,x)
triples. 2. T3 ext1 completion (`R_f`) → comparator re-run over all eight →
T3 re-graded under the frozen §7.1 gates. 3. T5 waits on Sanaa's
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

**Section last written:** 2026-08-22T18:05Z by harness-build (FIRST FILL — not yet written by its owner).

**Last commit:** `cc4f1a64` — *Twenty-six dead paper paths in forty files…*
(2026-08-18 17:54Z). **This lane has been idle four days** while the other four
committed today.

**Live jobs:** none.

**Standards — and these are two documents, not two copies.** `docs/standards/MESH_STANDARD.md`
(**v1.2, 2026-08-11**) carries the **quality gates**; `docs/MESH_STANDARD.md` carries
the **grid families**. They are complementary and neither supersedes the other, so
do not "reconcile" them into one. Read both. Also `docs/OPENFOAM.md` — **stale; it
describes the phase-1 adapter** — and `docs/OPENFOAM_SOLVER_BUILD.md`.

**Open run families (lacking verdicts):**

| family | why open |
|---|---|
| **DPW8_V2** | *Status: SALVAGE.* L4 fine gate rung **INCOMPLETE — not gated**; `run_L4_gate.stdout.log` is **0 bytes**. Two lower rungs PASS |
| **F5b** | the run dir is **exactly one file**, `run_pitch.py`. No case tree, no logs |
| **F5c** | headline **withdrawn to *unmeasured***. The 1.313 H attributed to SIMPLEC was **RELAXATION** — misattributed. Chief-approved **Stage B was never run** |
| **R4** (Ahmed turn) | *n = 2 of a planned 4*; leg-2: *"No SIGNAL/NOISE verdict is claimed."* Plus a withdrawal record. **Note: this R4 is the Ahmed-body draw series, NOT the closure team's R4 SpaRTA build** |
| **GEN_ALT** | measured, never written up, and **no solve ever ran** — mesh only. Both meshes breach non-orthogonality (70.13 / 70.11 > 70) |
| **F12** | pre-registration only; `F12_runs/` is just `reference/` |
| **F7a re-gate** | spec frozen, unexecuted |
| **MODEL_FORM successors** | three preregs, no results |
| **mbc_retry, uq_batch** | *"Nothing here is graded."* |
| **F4** | SWBLI θ=32.5°/35° gate cases *"NOT yet built or run"* |
| **F5** | 1e5 and 1e6 ladder rungs have no run tree |

**Closed, verdicts on record:** 4G, B52_RUNG6 (REPRODUCE), D5_rsm (SSG and LRR
bracket the DNS; *which* RSM is right is not settled), DMR, F2 (PASS banded), F3
(PASS), F8 (**NO VERDICT — and that is the result**), F9 (PASS quasi-steady, gate 2
stays FAIL vs Womersley), F11 (GATE REACHED), FPE_DIAG (SHARED-BY-CLASS, recorded
only by citation from its successor prereg), MESH_AUDIT, W1, W1_hump, W2_sparta,
W3.

**⚠ Structural fact this team must know:** with five exceptions, the run dirs under
`verification/runs/` carry **no README, RESULTS, PREREG or DONE marker at all**.
**The verdicts live one level up, in `verification/campaign/*.md`.** Do not
conclude a family is ungraded because its run directory is bare.

**Next actions:** reconcile the two MESH_STANDARD copies. Decide DPW8_V2 L4 —
finish the gate rung or record it as abandoned with a reason. Write up GEN_ALT,
which is measured and unpublished.

**On Sanaa's desk:** nothing currently.

**Blocked:** nothing currently identified.

**⚠ VERIFY:** `verification/runs/W2_sparta_runs/setup_sparta_case.sh` has mtime
**2026-08-22 17:38** and shows `MM` in git status — the only non-thermal file
touched under `runs/` in three days. **Find out who did that before assigning W2.**

**Case tree:** `cases/{committee-grids, demo-surfaces, hlpw6, mega-batch, tmr,
unsteady-cylinder, valve}` is **dormant in git** — none is the subject of a recent
commit. **`tmr` is the most open of them**; **`mega-batch` has a broken driver
path** (it points into `demo-output/website/...`, and stale paths of that shape are
**systemic** across this team's records — treat any such citation as suspect until
resolved). `models/tmr/**` deliberately holds solver cases outside a run tree, a
documented `FILING_CHARTER` §3 exception: *the rule was wrong, not the tree.*

---

## verification

**Section last written:** 2026-08-22T18:05Z by harness-build (FIRST FILL — not yet written by its owner).

**Last commit:** `fd831c11` — *T-family: Thermal Buildup Directive recorded; T3
NOT A RESULT 4/4; charter 2e; DC certificate template; libs helper+lint
(D449-D451, L-224)* (2026-08-22 17:53Z).

**Live jobs:** none.

**Charters owned:** `VERIFICATION_CHARTER.md` **v1.10, 2026-08-22** (§2e appended
at the foot on Sanaa's H-7 directive, L-219/L-220 verbatim, zero lines moved
above); `RESULT_PRIORITY_CHARTER.md` **v0.5 — a DRAFT**, whose orderings are
proposals awaiting Sanaa's ruling.

**Open items:**

| item | state |
|---|---|
| **VM2026R1_Fluids** (Ansys verification suite) | **UNTRACKED, and unpacked TWICE** — at the repo root `VM2026R1_Fluids/` and under `docs/papers/verification_validation/VM2026R1_Fluids/`, both mode 700, both dated 2026-08-22. Holds `VM2026R1_FLUENT_ARCHIVES` and `VM2026R1_CFX_ARCHIVES`. **Decide the canonical home under FILING_CHARTER R6/R8 and say which copy is authoritative before grading anything from it.** Nothing graded yet |
| **Ansys Fluid Dynamics Verification Manual** | on disk at `docs/papers/verification_validation/`, 8.5 MB, **PDF with no `.txt` sidecar**. `FILING_CHARTER` R8 requires the pair — *a PDF and its sidecar always travel together* |
| **`GATE FAIL` vs bare `FAIL`** | charter §2 says `GATE FAIL`; `scripts/check_verdict_cells.py --strict-fail` counted **4 ledger cells** reading bare `FAIL`. Both defensible, neither touched. **Referred for a ruling, unruled** |
| **Comparator freeze audit** | `scripts/check_comparator_freeze.py` first pass found **two of six frozen** — *"the honest baseline this rule starts from."* The other four are unaudited since |
| **The six standing audits** | `DEAD_LEVER`, `EXTERNAL_REFERENT`, `FAIL_OPEN_GATE`, `H4_ALLOCATION`, `LEDGER_HEADLINE`, `SWEEP_REFRAME`. None re-run since 2026-08-16 — **VERIFY** |

**Freshness flag:** nothing under `verification/campaign/`, `certificates/`,
`credibility/` or `monitor/` has been written since **2026-08-18 17:40** — four
days.

**Cross-team gate audit — this team's standing mandate.** Open any other team's
rung and ask: could this gate have failed (§2a identity test); was the comparator
frozen before its cases could answer it (§2d); were the controls **fired** rather
than described. Current highest-value targets, from the other four sections:

- **T1b's four `PASS` rows sit on triples that are every one DIVERGENT or
  STAGNANT** (D440). The rows are PASS as the frozen comparator returned them and
  carry no mesh-converged value. That is the sharpest live instance of the rule
  this team owns.
- **T10a** has 6 controls **UNMEASURED** and a 2d.1 zero-referent repair disclosed.
- **A4's two rows are measured at different design points** — so the shipped/patched
  comparison the DAFoam charter's bright line requires has never actually been made.
- **Wu2018 aposteriori** returned NOT A RESULT with the registered falsifier fired
  — check the falsifier was the pre-registered one and not re-read after the fact.

**Next actions:** rule on the VM2026R1 canonical home and get it tracked or
explicitly gitignored. Produce the missing `.txt` sidecar for the Ansys manual.
Re-run `check_comparator_freeze.py` across all six.

**On Sanaa's desk:** the `RESULT_PRIORITY_CHARTER` orderings (v0.5, *"still need to
think abt how to go abt this"*); the `GATE FAIL`/`FAIL` vocabulary ruling.

**Blocked:** nothing currently identified.
