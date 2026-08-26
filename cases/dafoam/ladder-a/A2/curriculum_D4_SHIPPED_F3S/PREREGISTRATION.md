# D4S-F3S — pre-registration: **THE TWO-ROW ENDPOINT FD TABLE UNDER ONE STATIONARITY ACCEPTANCE RULE**

**Item id:** `D4S-F3S` — successor of `D4-SHIPPED` (`cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED/`, Addendum 2e at `d75b38d2`) and of `curriculum_D4` §11 (`1697ea49`). **Version 1.0, FROZEN at the commit that carries this file.** Authored 2026-08-26T22:41:27Z by dafoam lane V2 (fifteenth session) on the dafoam-supervisor's order of 2026-08-26 ~22:20Z (`[lab-attributed]`), quoted where it governs. **Nothing here is sent, filed, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7). **No frozen file is edited** (rule 6): every ancestor is cited by path and copied by md5, never modified. Permission for the detached launch through the queue runner: Sanaa's own words at **`bc0e687e`**.

> **ID-NAMESPACE WARNING (carried by every document in this family).** `docs/DOCKET.md:129,130,139,140` carries fleet defects numbered D5, D6, D14, D15; those are different objects from the dafoam curriculum items of the same number. No bare `D<n>` here is a docket row.

---

## 1. WHY THIS ITEM EXISTS — `D4S-PREREG-DEF-1`, and the ruling that bounds the repair

`D4-SHIPPED` Addendum 2e (post-compute, `d75b38d2`) established from disk that the SHIPPED row's endpoint FD arm F3 died at its FIRST primal on the producer's own acceptance clause — `d4_opt_runScript.py:36-37` `primalMinResTol 1.0e-8`, `primalMinResTolDiff 1e3`, i.e. accept iff the minimum residual ≤ 1e-5 — while that primal was **stationary to 0.004 % over its last 600 iterations** at a `nuTilda` floor of **1.115891818e-05**; the PATCHED row's endpoint primal (curriculum_D4 F3, `rc=0`, G5 5/5) floored at **9.780100659e-06** on the same rule and was accepted by 2.2 %. **A threshold sitting at the instrument's own residual floor decides the arm by which side of the floor the endpoint lands.** That is a defect of the registration inherited by citation, not of the toolchain, the decomposition or the staging (all three were checked from disk and cleared: Addendum 2e A2e.2 (a)–(e)).

**The supervisor's ruling, verbatim where it binds this item:** *"loosening an acceptance threshold knowing which side of it the endpoint lands is the fitting objection (rule 2). What IS allowed … a successor item D4S-F3S … the acceptance rule stated as a STATIONARITY criterion, not a threshold … applied identically to BOTH rows: F-S and F-P endpoint FD arms re-run under the same rule (the PATCHED row re-run so the rule is one rule, not a SHIPPED-only relaxation)."* The restated-threshold proposal found on disk (`curriculum_D4_SHIPPED/d4s_primal_accept_wrap.py`, uncommitted, `primalMinResTolDiff` 1e3 → 2e3) is **NOT adopted here and is not this item's ancestor**: it was a threshold moved after seeing which side the endpoint sat on. This item's rule never compares a residual to a level (§3).

**What the item buys, or does not:** the family's first two-row G5 verdict on A2 — both endpoint FD tables under one acceptance rule — or the honest reason.

## 2. WHAT IS INHERITED **BY CITATION**, unchanged

| inherited | source | value (the cited document governs) |
|---|---|---|
| the case, mesh, np, decomposition | `curriculum_D4/PREREGISTRATION.md` §1, §5 | MACH wing CD-min at CL 0.5, 38,304 cells, np=4, `scotch` ×4 — the arms inherit their source arm O's `processor*` (byte-identical across both rows and equal to `decomposePar -force`, D4-SHIPPED Addendum 2e A2e.2 (b)) |
| **band D / E** — the bright line | `curriculum_D4/PREREGISTRATION.md:82` | **5.0 % per graded component and 5.0 % aggregate, zero sign flips; plateau ≤ 10 %** |
| the five graded components, in order | `curriculum_D4/PREREGISTRATION.md` §6 | `shape[46]`, `shape[18]`, `shape[0]`, `twist[0]`, `patchV[1]` |
| the step ladder, clearance floor 5, ratio 2, `ETA_FLOOR` 1e-14 | `curriculum_D4/d4_fd_endpoint.py:41-48` (md5 `c6112b0e…`) | copied verbatim into `d4s_f3s_fd_endpoint.py` (DELTAS diff, §7) |
| the D4-DEF-4 repair step and its four instruments | `curriculum_D4/d4_repair_instruments.md5`; D4-SHIPPED Addendum 2d | `d4_endpoint_physical.py --age-datum <copy epoch>` before the FD; md5-asserted before and after staging |
| the endpoint-arm staging path (copy of a graded `O/`, D4-DEF-6 step (f), copy epoch as datum, source censused intact) | D4-SHIPPED Addendum 2d, `d4s_stage_endpoint_arm.sh` | `d4s_f3s_stage_arm.sh` (DELTAS 212 lines) |
| the launcher family: G-ROOT.1–.5, digest by hash, cap assertion, in-container deadline, `rc` from `docker inspect`, no `--rm`, sampler, ledger row | D4-SHIPPED Addendum 2/2d, `d4s_run_arm.sh` md5 `506c99e6…` | `d4s_f3s_run_arm.sh` (DELTAS 331 lines) |
| chain driver: H5 window 45/60 s floor 16.0 GiB, aggregate < 30.6 GiB wait-and-retry bounded 14,400 s, ALREADY_BOUGHT, STATUS lines | D4-SHIPPED Addendum 2b/2d, `d4s_chain_driver.sh` | `d4s_f3s_chain_driver.sh` (DELTAS 189 lines) |
| the two toolchain identities by HASH | `curriculum_D4_SHIPPED/PREREGISTRATION.md` §3.1 | SHIPPED `9d45679d…` / `libidwarp.so` `f0fcb488…`; PATCHED `2927768a…` / `85f59e87…` |
| L-342 field classes; planted zero; count refusals; positional terminal statement; arm-kind rule (both arms SOLVER) | D4-SHIPPED Addendum 2, 2b; `d4d0c29d` | ported into `d4s_f3s_grade.py` |
| cpuset, memory, cap | D4-SHIPPED §2 (F3 row), §5b | **5,6,7,9; 12 g; 120.0 core-min per arm** |

**No band, threshold, cap or label in that table is altered here.**

## 3. WHAT IS NEW — THE STATIONARITY ACCEPTANCE RULE, and only that

### 3.1 The rule (`d4s_f3s_accept.py`, one implementation, two call sites)

A primal is **ACCEPTED** iff, on its own printed solver output:

| clause | statement | registered constant |
|---|---|---|
| **R1** | the solver's `End` line is present, the last printed `Time =` equals the case's `endTime`, and the window `Time ≥ endTime − WINDOW_ITERS` holds ≥ `MIN_WINDOW_SAMPLES` printed samples | `END_TIME_REGISTERED = 1000`, `WINDOW_ITERS = 200`, `MIN_WINDOW_SAMPLES = 3` (the producer prints every `printInterval = 100` iterations, so the window is the samples at 800, 900, 1000) |
| **R2** | for EVERY equation the solver prints — `U0 U1 U2 he p nuTilda` — `max_window \|r(t) − r(end)\| / r(end) ≤ STATIONARITY_TOL`, with `r(end)` finite and positive | `STATIONARITY_TOL = 1.0e-3` |
| **R3** | `Time step continuity errors : sum local` at the last sample ≤ `CONTINUITY_BOUND`; global and cumulative finite | `CONTINUITY_BOUND = 1.0e-6` |
| **R4** | every parsed number, and the primal's CD and CL, finite | — |

A capture yielding **zero** `Time =` samples is a **READER FAILURE → REFUSAL**, never an acceptance (rule 3). **No clause compares a residual to a level.** The rule is therefore **blind to which side of 1e-5 the floor sits** — demonstrated, not asserted (§3.3).

### 3.2 The derivation, from the two measured floors and nothing else

| quantity | PATCHED endpoint (D4 F3, 22 primals) | SHIPPED endpoint (D4-SHIPPED F3 r2, 1 primal) |
|---|---|---|
| `nuTilda` initRes at Time 800 / 900 / 1000 | 9.780100678e-06 / 9.78010066e-06 / **9.780100659e-06** | 1.115892463e-05 / 1.115891847e-05 / **1.115891818e-05** |
| max relative drift over the window, worst equation | `he` **1.94e-06** (all 22 primals) | `U2` **5.22e-07** |
| continuity `sum local` at Time 1000 | 1.891e-09 | 1.959e-09 |
| ratio to the registered tolerances | drift ≤ tol / **516**; continuity ≤ bound / 500 | same bounds |

`STATIONARITY_TOL = 1e-3` is **≥ 500× the worst measured drift on either row** (the selftest asserts the margin ≥ 100×, measured 516×); `CONTINUITY_BOUND = 1e-6` is ~500× the measured continuity error. A primal that is still moving by 0.1 % per 200 iterations, or whose continuity error is 500× worse than every primal this case has produced, is not accepted. The constants are bounds on the SHAPE of convergence, chosen from measured stationary series; they are not levels.

### 3.3 Driven before the freeze — `d4s_f3s_accept_selftest_evidence.txt`, 18/18 under `python3` and `python3 -O`

Positive controls: **every one of the 22 real PATCHED primal blocks ACCEPTED; the real SHIPPED F3 r2 primal ACCEPTED** (`nuTilda` 1.115891818e-05 > 1e-5, above the producer's threshold) — *"1_blind_to_the_1e-5_side: SHIPPED 1.115891818e-05 (> 1e-5) ACCEPTED; PATCHED 9.780100659e-06 (< 1e-5) ACCEPTED"*. Negative controls, each a planted mutant of a real block: 1.2 % drift at Time 800 → REJECTED (`R2`); 0.09 % drift → ACCEPTED (the tolerance is a tolerance); NaN → REJECTED (`R4`); continuity 2.5e-5 → REJECTED (`R3`); `End` removed → REJECTED (`R1`); truncated at Time 700 → REJECTED (`R1`); empty capture → **REFUSED**; an equation missing from the window → REJECTED. `ast.Assert` 0, the counter shown able to count a planted assert.

### 3.4 How the rule reaches the primal — `d4s_f3s_fd_endpoint.py`, DELTAS from the frozen `d4_fd_endpoint.py`

(i) **The producer's threshold clause is DISARMED, not loosened**: after the frozen header is exec'd (md5 `2906d52a…` asserted, the bytes unchanged), `daOptions["primalMinResTolDiff"]` is set to **`DISARM_TOL_DIFF = 1.0e12`** — an accept floor of 1e4 that no primal reaching `endTime` can exceed — and the EFFECTIVE value is READ BACK from the constructed `DASolver` (`getOption`); if it is not 1e12 the instrument REFUSES (rc 2). (ii) Every primal runs with rank 0's file descriptor 1 redirected at the OS level to `d4s_f3s_primal_NNN_<tag>.log` (so the C++ `Foam::Info` stream is captured; **mechanism probed in the shipped image before this freeze**: C-stdio, Python and raw-fd writes all captured, stdout restored — a 10-s single-core probe container, 0.17 core-min, reported in §4), re-emitted to stdout so the arm log carries it, parsed and evaluated by the rule; one record per primal in `d4s_f3s_accept.jsonl`. (iii) **A primal the rule does not accept REFUSES the arm at once** (rc 2, record written); the sweep never continues on a rejected primal, and no silent `FD_STEP_FAILED` row can exist (the ancestor's per-pair `try/except` is removed — the DELTAS diff shows it). (iv) Output names carry the item: `d4s_f3s_fd_endpoint.json` / `.jsonl`. Everything else — components, ladder, clearance, plateau, central differences, field names — is the ancestor's bytes.

**The grader re-evaluates every capture host-side with the SAME module (md5 asserted equal to the one the instrument recorded), binds the capture count to the accept records, to the FD file's `n_primals` and to the arm log's `Running Primal Solver` count, and refuses on any disagreement (G-ACC, §5).**

## 4. ARMS, PLACEMENT, COST — every run costed before it runs (rule 12)

| arm | row / image | source of the staged copy (READ-ONLY, on this launcher's FORBIDDEN list) | cap core-min | memory | deadline in-container | predicted core-min |
|---|---|---|---|---|---|---|
| **F-S** | SHIPPED `dafoam/opt-packages:latest` `9d45679d…` | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/O` (graded arm O, 100 majors, `.d4_age_datum` 1787717054) | 120.0 | 12 g | 1,800 s | 47.267 |
| **F-P** | PATCHED `dafoam-idwarp-rot:v1` `2927768a…` | `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O` (graded arm O, 80 majors) | 120.0 | 12 g | 1,800 s | 47.267 |

**Point 94.534 core-min = 2 × D4's measured PATCHED F3 (47.267, `CURRICULUM-D4-a2-wing-cdmin/f3_ledger.txt`, 709 s × 4); ceiling 240.0 = Σ caps.** Dollars DERIVED at $0.0513/core-h, reported-by-owner, **NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5): **$0.0808 point, $0.2052 ceiling.** Ranks 4, cpuset **5,6,7,9** (D4-SHIPPED's registered placement; D5 8,10,11,13, D15 2,3, D16 4,14, W2R 12 are disjoint; D6's held 2,3,4,14 does not overlap), H5 floor 16.0 GiB (45 samples / 60 s), aggregate caps + 12 g + host RSS < 30.6 GiB wait-and-retry bounded 14,400 s. Chain order **F-S then F-P**; the chain stops at the first non-zero rc. Already spent by this registration: **0.17 core-min** (the §3.4 probe, `docker run --rm`, 10 s, 1 core) — reported, its own figure. Runner watch: `cap_core_min_registered = 240.0`.

**Cost caveat, registered:** F-S has never completed on this case; 47.267 assumes the SHIPPED endpoint's 22 primals converge at the PATCHED rate (~25 s each, measured on r2's single primal: 25 s). P4 (§6) is the falsifier.

## 5. GATES — thresholds by citation, composition stated before compute

| gate | reads | verdict rule |
|---|---|---|
| **G1** per arm (SOLVER) | ledger row (`rc` = kernel `ExitCode`, `OOMKilled`), the arm log's LAST non-empty line, every registered artefact strictly newer than the arm's copy epoch | `PASS` iff kernel rc 0 ∧ OOM false ∧ `Finalising parallel run` positional ∧ 0 stale; harness/kernel disagreement → REFUSE |
| **G-ACC** per arm (NEW) | the per-primal captures, `d4s_f3s_accept.jsonl`, the `disarm` record, the FD file's `n_primals`, the log's `Running Primal Solver` count | `PASS` iff every capture re-evaluates ACCEPTED ∧ every instrument record agrees ∧ disarm read-back = 1e12; count disagreement → REFUSE; zero captures → REFUSE |
| **G5** per row — THE BRIGHT LINE | `d4s_f3s_fd_endpoint.json` | count refusal first (5 registered components in order); `PASS` iff aggregate ≤ 5 % ∧ every component ≤ 5 % ∧ 0 sign flips ∧ 0 without plateau (≤ 10 %); `NOT A RESULT` if 0 graded; else `GATE FAIL` |
| G6 / G6b / G7 per row | the FD file on disk | plant 1.234e-03 into `d_hi`, re-read through the same reader, all three channels must move and the source md5 must not; a blind reader must be REFUSED; empty / short / reordered / key-absent must each be refused by NAME |
| **G9** per row + distinct | the `D4S_IDWARP_SO_MD5:` line of the arm's log, the ledger's digest | F-S must carry `f0fcb488…` + `9d45679d…`, F-P `85f59e87…` + `2927768a…`; the two md5s must differ |
| G10 | ledger caps vs registered, Σ ≤ 240.0 | `PASS` / `GATE FAIL` (reports; never absorbs) |
| G11 | `OOMKilled` | any true → `NOT A RESULT` |
| G12 | `d4_placement_rank*.json` (4 files, count refusal), ledger cpuset, delivered mean (`NOT_MEASURED` tolerated, ≥ 3.0 if present) | `PASS` iff affinity ⊆ {5,6,7,9}, distinct single cores, cpuset as registered |
| **ITEM** | the above | `NOT A RESULT` if any arm fails G1 or G-ACC, any control fails, any OOM, or any row's G5 is `NOT A RESULT`; else **`PASS` iff both rows' G5 `PASS`; else `GATE FAIL`** (a two-row divergence is a finding, D4-SHIPPED §5) |

L-342: absent INFRASTRUCTURE fields (`memavail_*`, `delivered`, `siblings_*`) → `NOT_MEASURED`, disclosed, the grade proceeds; present-but-garbage → REFUSE; absent PHYSICS field → REFUSE. No GCI (no grid family; rule 5 has no row). Grader selftest **26/26 under `python3` and `-O`** on a sacrificial root built from curriculum_D4's REAL F3 table and its 22 real primal blocks (`d4s_f3s_grade_selftest_evidence.txt`): clean → `ITEM PASS`, aggregate 0.1634451673004621 % reproduced; `rc=1` → `NOT A RESULT`; harness/kernel disagree → REFUSE; terminal not last → fail; stale → fail; absent artefact → REFUSE; a 5 % planted drift in one capture → G-ACC `NOT A RESULT` with the instrument/grader disagreement recorded; capture count mismatch → REFUSE; disarm read-back 1e3 → G-ACC `NOT A RESULT`; SHIPPED arm carrying the PATCHED `.so` → G9 `GATE FAIL` and rows-not-distinct; `shape[18]` sign-flipped → G5 `GATE FAIL`, item `GATE FAIL`, P2 HIT; infra absent → `NOT_MEASURED` and `PASS`; infra garbage → REFUSE; physics absent → REFUSE; OOM → G11; cap crossing → G10 `GATE FAIL`, P4 MISS; two ranks on one core → G12 `GATE FAIL`; every token in the fixed vocabulary; `ast.Assert` 0 in grader and rule.

## 6. PREDICTIONS — scored HIT / MISS / UNSCORED by the grader, never adjusted

| id | prediction | falsifier |
|---|---|---|
| **P1** | **both arms: every primal of the sweep (22 each if all five components are PLANNED) is ACCEPTED under the stationarity rule, and both FD tables exist** | any primal rejected, or a `REFUSE` by the reader, on either row |
| **P2** | **SHIPPED row G5 = `GATE FAIL` with `shape[18]` outside band D or sign-flipped** — the component D4's registration named worst at the shipped BASELINE (−360.75 %, `curriculum_D4/PREREGISTRATION.md:62-66`) and D4-SHIPPED's S3 carried to the endpoint | **P2 MISSES if the SHIPPED row is 5/5 inside band D** — and that MISS is the finding that the IDWarp rotation defect does not reach the endpoint gradient on this case (the D1-C′ design-point-dependence reading), recorded, never averaged with a HIT |
| **P3** | **PATCHED row reproduces curriculum_D4 §11.3 to the printed digits**: every graded component's `J_adj` and `d_hi` within 1e-12 relative of `CURRICULUM-D4-a2-wing-cdmin/F3/d4_fd_endpoint.json` (same image, same decomposition, same endpoint, np=4; D4 §11.2 measured bit-identical CD across three arms) | any component off by > 1e-12 relative — a reproducibility finding about this box and image, recorded as such |
| **P4** | cost ratio actual/predicted **per arm in [0.8, 1.5]** | either arm outside |

If P2 HITS and P3 HITS the item is `GATE FAIL` on the SHIPPED row — the two-row divergence finding D4-SHIPPED §5 registered as reportable; if P2 MISSES and P3 HITS the item is `PASS` and D4's optimum-endpoint gradient becomes toolchain-independent on this case. Both are registered as reportable now.

## 7. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT — and the diffs for the supervisor's check 1

| file | md5 | ancestor / diff to read |
|---|---|---|
| `d4s_f3s_run_arm.sh` | `d65da2e06d5ec171d1ae6501728d80b3` | `d4s_f3s_run_arm_DELTAS_from_d4s.diff` (331 lines) from D4-SHIPPED `d4s_run_arm.sh` `506c99e6…`; 0 backticks on executable lines |
| `d4s_f3s_chain_driver.sh` | `da74cd11b3728fa6f5ac167b503255e3` | `d4s_f3s_chain_driver_DELTAS_from_d4s.diff` (189) from `d4s_chain_driver.sh` `01ddb189…`; creates the root on first fire, grades at chain end (rc labelled INFRASTRUCTURE), writes `CHAIN_DONE` |
| `d4s_f3s_stage_arm.sh` | `f0d0dd3689db27239f1d1d60d429ef77` | `d4s_f3s_stage_arm_DELTAS_from_d4s.diff` (212) from `d4s_stage_endpoint_arm.sh` `662569d5…`; **not driven** (driving it copies a 384 MB graded tree into the registered root before compute); `bash -n` clean; the ancestor ran to READY at 20:50:06Z on the same steps |
| `d4s_f3s_fd_endpoint.py` | `9ce78caab9c46d13398ee1d0643cf982` | `d4s_f3s_fd_endpoint_DELTAS_from_d4_fd_endpoint.diff` (386) from `d4_fd_endpoint.py` `c6112b0e…`; `ast.Assert` 0 |
| `d4s_f3s_accept.py` | `7377fd5e1eb0a558c2d38fc8da125fc2` | NEW (§3); selftest 18/18 plain and `-O` |
| `d4s_f3s_grade.py` | `2ed0651c786cb5bd8832f8660ba6c670` | NEW, ported from `d4s_grade.py` `f825c2cd…` (read as a file); selftest 26/26 plain and `-O` |
| `d4s_f3s_groot5_selftest.sh` | `15a5c6065f302bc93c5adc67a320933a` | evidence `d4s_f3s_groot5_selftest_evidence.txt` **16/16** at 22:39:07Z: live sacrificial container → rc 3; live sacrificial pid (cwd = root) → rc 3; stale pidfile ignored → bogus image aborted at the digest (rc 4); correct image per arm → G-ROOT.5, md5s, digest, G-ROW PASS then rc 5 at WORK-absent (nothing staged); wrong image per arm → G-ROW rc 4; `BASE=` D4-SHIPPED's and D4's roots → G-ROOT.1 rc 3; foreign arm → rc 64; sacrificial root unchanged, D4-SHIPPED `O/` untouched (7,962 entries), no container survives; **root removed and ABSENT** |
| `d4s_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | byte-identical to D4-SHIPPED's |
| `d4s_f3s_instruments.md5` | — | the two item instruments, asserted by the stager in the case dir and in the root, and by the launcher before every arm |

## 8. FREEZE

**Condition:** `/home/ubuntu/certonomous-runs/CURRICULUM-D4S-F3S-a2-wing-cdmin` **ABSENT at 2026-08-26T22:41:27Z** (also the G-ROOT.5 selftest's final leg at 22:39:07Z). **0 solver core-min spent; the only container this registration ran was the 10-s capture probe (§3.4).** The grading path is `d4s_f3s_grade.py` at the md5 above, asserted by the driver before it runs and to be hashed against this commit's blob before any grade is believed. After first compute gates are closed; changes land only as dated addenda that cannot alter a gate, threshold, cap or label.

**Launch path of record:** the queue runner — `verification/queue/dafoam/D4S_F3S_chain.json` with `prereg_commit` = the sha of this commit, argv `bash <case dir>/d4s_f3s_chain_driver.sh F-S F-P`, `cap_core_min_registered 240.0`, validated by `scripts/queue_entry_check.py`; **enqueueing is not authorisation** — the supervisor's check 4 is theirs. The driver's guards (G-ROOT.1–.5, ALREADY_BOUGHT, md5s, digest, G-ROW, H5, aggregate) are its preconditions; every one refuses before a core-second is spent, and the stager refuses an existing destination.

## 9. WHAT THIS ITEM WILL NOT ESTABLISH

Nothing about arm O (both optimisations are cited as graded/recorded: PATCHED `Optimal Solution Found` 80 majors; SHIPPED `Maximum Number of Iterations Exceeded` 100 majors, `inf_pr` 6.59e-05 — D4-SHIPPED RESULTS §7); nothing about a mesh other than D4's; no GCI; nothing at another np, decomposition, image or primal tolerance; nothing about the 91 `shape` components not in the table; nothing about physical accuracy against experiment. The FD and the adjoint share the primal and are wrong together where it is wrong (`V_STANDARD_FD_VS_ADJOINT.md` §13 item 12).
