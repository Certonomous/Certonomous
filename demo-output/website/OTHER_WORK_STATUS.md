# Other Work Status: Infrastructure, Credentials, Research, Process — Week of 2026-07-25 to 2026-07-28

## 1. INFRASTRUCTURE AND STABILITY

### The two outages and root causes

**Outage 1: 2026-07-27, ~05:12:56 UTC — memory exhaustion, no swap**
- True cause: memory committed at **112.90% of RAM**, free memory 450 MB, reclaim scanning at ~10x daily average per final `sar` sample at 05:10:03
- Concurrent load: two DAFoam adjoints (sail `check_totals` -np 3, wing `compute_totals` -np 4, both in graph colouring / adjoint phase, peak 21 GB resident) + 4-worker mega-batch on c7a.4xlarge (16 vCPU, **32 GB RAM only**, 2 GB/core)
- No OOM message because reclaim livelock precedes OOM killer with zero swap; `journald` could not allocate to record it
- 74-second log gap (05:11:42 to 05:12:56) was silent window, not failure point; machine kept writing to disk during gap
- Commits salvaged through `d6e2c56` (05:11:26); last file write at 05:12:56.247 UTC
- **All recovery verified non-destructive:** ledger resumed at index 186,902 with zero gap or truncation; no committed work lost

**Outage 2: unspecified prior to 2026-07-27 — Docker networking collision theory REFUTED**
- Hypothesis: Docker subnet (172.17.0.0/12 default) could collide with VPC (172.31.32.0/20), causing network blackhole
- Verdict: **Not the cause** — no user-defined Docker networks were created that night; all containers joined default `bridge` (nid=3e86037d9e25); no subnet collision observed
- Network isolation pin (10.200/10.201 on docker0) installed correctly and persists, but it is a future-proofing measure, not a regression fix for an outage already explained by memory

### Resource guards and stability measures

**Mega-batch guards (commits `f1527b9`, tested and verified)**

| Guard | Problem solved | Default | Tested working | Status |
|-------|---|---|---|---|
| `--min-free-disk-gb` | Batch filling disk, then failing to de-allocate | 20 GB | Forced to 100,000 GB: trips immediately, 0 tasks run, reason logged | **Verified, live, stops batch cleanly** |
| `--min-avail-mem-gb` | Memory exhaustion (root cause of 2026-07-27 livelock) | 2 GB | Forced to 9,999 GB: trips immediately, 0 tasks run | **Verified, live, stops batch cleanly** |
| Sample period | — | Every 10 s | — | **Live** |
| Happy-path validation | Confirm guards don't block normal work | — | 4 of 4 real solves completed OK with default floors | **Passed** |

Single-instance lock (`acquire_runner_lock`, commit `f198cf4`): guards against double-launch that corrupted 55 ledger rows on 2026-07-27 when second runner launched at 05:11 while first was still alive. Lock refuses to start if `runner.pid` names a live process whose cmdline contains `mega_batch`. **Verified working:** attempted second launch against live PID 4408 was **REFUSED**, exit 1, file not clobbered. Stale PID (999999) was reclaimed correctly. Live non-runner process (sleep) was allowed. `--force` override exists for manual recovery.

**16 GB swapfile (commit `b1706a3`, 2026-07-28 00:14:18 UTC)**

- Location: `/swapfile`, 16 GB, mkswap'd, swapon'd, made persistent in `/etc/fstab`
- Verified reboot-safe: swapoff + `swapon -a` (reads fstab) brought it back correctly
- vm.swappiness=10 set in `/etc/sysctl.d/99-swappiness.conf` (safety net, not routine paging tier)
- **Problem solved:** converts hard livelock (zero-swap exhaustion) into survivable, observable degradation
- **Not tested under real load yet** — installed after the outage event, machine has not been stressed to memory ceiling since then
- Disk free when installed: 456 GB, so swapfile is affordable; no re-balance needed

**Mega-batch keeper (commit `7468ef1`, 2026-07-28 03:21:06 UTC)**

- Purpose: restart batch after it stops on its own memory guard, once memory has genuinely recovered
- Restart floor: 8 GB available (well above batch's own 2 GB floor)
- Monitor mechanism: match on full command line (`mega_batch.py`), confirm executable name (`python3`), exclude self and parent to avoid false `pgrep -f` matches (documented trap in LESSONS.md L-6)
- Key fix in `python3 -u`: unbuffered stdout so `runner.log` is honest progress signal, not a buffered delay (commit `9c4ba2c`, 2026-07-28 06:04:51 UTC). Without it, batch was genuinely running but `runner.log` showed nothing for 35 minutes
- **Status: Live and running** — confirmed appending to ledger normally, 206,645 → 206,647 rows observed over 45 seconds on 2026-07-28 06:03 UTC

**`is_idle.sh` idle detector (commit `ce534b3`, 2026-07-28 05:38:42 UTC)**

- Purpose: detect real work for auto-stop watchdog; reports BUSY or IDLE, exit code 0 (idle) or 1 (busy)
- Matches: mega-batch runner, batch keeper (WILL RESTART), all solver executables by name (simpleFoam, pimpleFoam, snappyHexMesh, etc.), DAFoam containers, closure training
- **Traps documented, not elided:**
  - Trap 1: Keeper will restart batch, so "batch not running" ≠ "idle" (stop keeper first)
  - Trap 2: `comm` is not distinctive (python3, bash match many things); all checks use full cmdline + confirm executable name
  - Trap 3: `pgrep -f` matches the asking shell; every check excludes $$ and $PPID, prevents self-matches
- **Status: Live** — validates three concrete incidents from 2026-07-27/28 where a wrapper shell or transient PID gave false "finished" readings

---

## 2. LEDGER INTEGRITY

### Duplicate audit and the 55 new duplicates discovered post-outage

**Discovery:** During ledger backup verification (commit `f198cf4`, 2026-07-27 23:xx), re-auditing the ledger by hand surfaced 55 previously unknown duplicate indices at **186,838–186,893**

| Statistic | Count |
|---|---|
| Total lines in ledger | 192,409 |
| Distinct indices | 191,219 |
| Total duplicate rows | 1,223 (1,168 historical + **55 new**) |
| Unparseable lines | 1 (line 61438, historical, deliberately preserved) |

**Timing of new 55 duplicates:** All written between **05:11:15 and 05:12:52 on 2026-07-27 — BEFORE the outage**, not across the restart crash. This proves recovery is not the cause.

**Mechanism:** `runner.pid` dated 05:11 held PID 2303296 while the 03:21 runner (PID 761552) was still alive. A second runner was launched on top of the first; both appended for ~100 seconds until box died. `runner.log` has no entries between #179198 and the restart's #186902 (non-persistent output). This is the **same failure mode** as the historical 1,168-duplicate episode in indices 59,899–61,068.

**The fix and verification:** `acquire_runner_lock()` refuses to start when `runner.pid` names a live process whose `/proc/<pid>/cmdline` contains `mega_batch`. Tested three ways:
- Second runner vs live PID 4408: **REFUSED**, exit 1, `runner.pid` not clobbered
- Stale PID (999999, dead): Start allowed, file reclaimed
- Live **non-runner** (sleep): Start allowed (cmdline check works)

**Impact on published figures (unresolved, reported not corrected):**

| Figure | Currently | Distinct truth | Error | Note |
|---|---|---|---|---|
| Evaluations in fleet | 180,368 | 179,200 | +1,168 (+0.65%) | Row count, not distinct evaluations |
| Completed evaluations | 180,296 | 179,190 | +1,106 | — |
| Failed evaluations | 72 | 10 | **7.2x overstated** | 62 were transient failures, re-tried and succeeded |
| Failure rate | 0.040% | 0.0056% | **7.2x overstated** | — |

**Recommendation for de-duplication (LESSONS.md L-2 applied):** Do not delete from ledger (it is append-only evidence). De-duplicate **in the distiller at read time** with **prefer-ok rule**: for each index, keep the successful row; if both failed, keep one. Naive keep-first/keep-last both corrupt data (discard 37 and 15 good solves respectively).

**Honest caveat on the backup (commit `f198cf4`):** Backup is on the same machine/disk as ledger. Protects against file corruption, bad de-duplication, accidental deletion. **Does NOT protect against losing the instance** — which is exactly what happened. Disk survived this time, that was luck. Genuine off-host durability (S3 or private GitHub) requires credentials this server lacks; flagged as Katie's gap to close.

### The torn line and the reduced-order valve issue

**Line 61,438 torn write:** Fragment beginning mid-token inside the duplicate zone (indices 59,899–61,068). Distiller skips silently. Should be **counted and reported** rather than swallowed, so future torn writes cannot hide.

**Reduced-order valve family:** Records **60,122 evaluations in 22.4 s total** (mean 0.0003 s/eval) — correct, honestly labelled as "reduced-order screen" in runner, but means **one-third of fleet's headline evaluation count is not solver work**. Worth naming before that count goes on website next to "solves".

---

## 3. CREDENTIALS-WALL WORK

### NACA 4412 wing credential

**Verdict: NOT VALIDATED** (not because a number is out of band, but because the grading method is self-referential and cannot produce a trustworthy verdict on this case)

**Attempt 1:** Relaxed nine `addLayersControls` at once
- Result: boundary-layer coverage collapsed from 58.3% to 4.36% (opposite of intent)
- Lesson (LESSONS.md L-3): hypothesis untested, not refuted; failed experiment produced one valuable incidental finding

**Attempt 2:** Changed exactly one thing — held `nGrow` at 0 while keeping other eight relaxations
- `nGrow 1` was the culprit (cascades non-extrusion on an already-struggling surface)
- Improvement: coverage **58.3% → 77.00%**, layers 6.0 → 8.42, mesh built faster (926 s vs 2153 s) with more cells
- Knowledge entry: **Cd is insensitive to boundary-layer coverage on this wing** — moved only 0.037% (0.0183273 → 0.0183341) across 17.7x coverage change

**Cl non-monotonicity survives:** Better coverage closes only ~26.5% of the Cl gap to fine rung; ladder remains non-asymptotic

**Why the verdict is NOT VALIDATED:** The grading method anchors the reference on the solve's own Cl. That means:
- Solve that over-predicts Cl (25.0% over on finer_ngrow0: 0.23940 vs fine 0.20955)
- Raises induced-drag term by 56.2%
- Lifts the reference band upward
- Makes an unconverged solve appear "in band" — a self-referential artifact

Result: finest rung (4.36% coverage) **passes**, two rungs with best coverage (94%+) **fail**. **"In band" can be bought by getting Cl wrong.**

**What this credential needs:**
1. Anchor reference on independent Cl (design target or experimental value), not the solve's own lift
2. Converge Cl across the ladder (it is not asymptotic; driver unidentified; suspects: pressure/induced split, wake/tip treatment at AR 3)
3. Add layer-coverage gate per §2 knowledge (Cd agreement cannot substitute for resolved boundary layer)

**Cost and evidence:** ~37.4 core-minutes (mesh 15.4, solve 22.0). Case dir: `/home/ubuntu/certonomous-runs/credential-repair-naca4412-finer_relayered_ngrow0`. Cells 2,091,678, converged residuals recorded.

### Pressure-slice audit

**Scope:** All 9 images under `demo-output/plots/pressure_slices/`, re-verified for consistency with corrected Cp pipeline (commit `47fffd3`, 2026-07-26 04:12 UTC)

| Image | Result | Notes |
|---|---|---|
| b52.png | PASS (0.71815) | Cross-checked against validation_numbers.json exactly |
| motorBike.png | PASS (0.99180 slice) | Slice max is body's outside-gap max; sliver artifact is off-plane |
| naca0015_sail.png | PASS (0.88555) | Reproduced independently |
| naca4412_wing.png | PASS (0.87642) | See reconciliation below |
| naca0015_sail_streamlines.png | **REGENERATED**, PASS (0.8858) | Was genuinely stale (2026-07-25 22:59, pre-fix); re-run from same mesh/solve cache; 5 proactive checks all PASS |
| validation/b52_cp_validation.png | PASS (0.71815) | Post-fix timestamp (2026-07-26 04:26:21, 14 min after fix) |
| validation/motorBike_cp_validation.png | **FAIL** (1.11920 on 1 face) | Sliver-cell artifact in ~1 mm brake gap; cell volume 1.21e-08 m³ = checkMesh global minimum; documented in MOTORBIKE_Cp_anomaly_investigation.md; rest of body clean at 0.99180 |
| validation/naca0015_sail_cp_validation.png | PASS (0.8865686) | **Pre-fix by mtime** (2026-07-25 22:38:51) but **NOT stale in content** — re-verified pixel-identical after fresh extraction |
| validation/naca4412_wing_cp_validation.png | PASS (0.8892005) | **Pre-fix by mtime** (2026-07-25 22:38:47) but **NOT stale in content** — re-verified pixel-identical after fresh extraction |

**The 0.8897 vs 0.8892 reconciliation:** Both real, traceable to identical raw peak p_max = 100.08748 m²/s²
- 0.8897 = p_max / q (no p_inf subtraction); source: test_field_render.py:321, PROOF.md
- 0.8892004618710941 = (p_max − p_inf) / q (proper normalization); source: validation_numbers.json (published, correct)
- Gap = 0.0524% = exactly p_inf / p_max correction

**One real FAIL, reported not fixed:** motorBike wall-cell Cp = 1.11920 on 1 face of 44,032, above stagnation ceiling 1.0. Owning cell is degenerate sliver (1 mm brake gap, matches mesh checkMesh global minimum). Not a regression; pre-existing, already investigated. **This one needs Katie's call** on whether to publish with caveat, clip colour scale, or re-mesh. Image left as-is, defect clearly documented.

**Bug found and fixed:** `run_checks` in render_sail_streamlines.py fed degenerate triangulation to matplotlib's `TrapezoidMapTriFinder` via near-margin point filter; crashed rather than passing falsely. Fixed by using same unfiltered full point set the actual render already uses successfully. No measured number touched; all 5 streamline checks now run to completion and pass.

### TMR NACA 0012 status

**Status: RESOLVED, docket item was stale** — already diagnosed in commit `6606434` (2026-07-27 03:38:19 UTC, 94 minutes before outage), before the outage interruption.

**"Missing viscous term" hypothesis REFUTED on two independent rungs:**

| Rung | Evidence | Finding |
|---|---|---|
| Transient (alpha 0, 300 CU) | Friction 0.000359 + pressure 0.000349 = 0.000708 (matches reported cd_mean exactly) | Viscous term present, ~50% of total |
| Steady (alpha 10) | OpenFOAM forces output: Cd 0.004494853, pressure 0.001479, **viscous 0.005974** | Viscous term is the LARGER component |

Viscous term is not missing. Real cause of low alpha-0 drag is **non-stationary average** — SST turbulence still developing cold-start, Cd rises monotonically across five 60-unit windows: 0.000322 → 0.000429 → 0.000539 → 0.000691 → 0.000894 (31.6% drift). Reported value is mid-transient snapshot, not converged. Commit `6606434` added `halves_drift()` stationarity gate; archived driver_status.json predates gate, left untouched.

**Negative pressure drag at alpha 10 is real and expected on coarse rung:** Front pressure −0.5588, rear +0.5574, residual (cd_pressure) = −0.001479. Residual is 0.265% of the cancelling terms — a 0.26% discretization error on either term flips the sign. TMR's coarsest rung (64 surface panels), d'Alembert predicts zero 2D inviscid pressure drag exactly.

**Honest gap:** Closing this properly needs time-accurate averaged solve on medium rung (~480 core-minutes). Scoped in agenda/proposals but not launched — budget decision for Katie. No commit produced from this track (work was verification arithmetic on archived data).

---

## 4. RESEARCH AND KNOWLEDGE

### Closure-methods taxonomy

**Document:** `docs/research/CLOSURE_METHODS.md` (commit `e1aa256`, 2026-07-28 05:31:53 UTC)

| Dimension | Count / Finding |
|---|---|
| Classes defined | **7 major classes** |
| Total entries (methods) | **38 distinct methods** across all classes |
| Citation verification tier (a) — primary source verified | **26 entries** |
| Tier (b) — secondary discussion only | **10 entries** |
| Tier (c) — could not establish | **0 entries** (gaps named, not guessed) |
| Backbone review (Duraisamy et al. 2019) | Verified; organizes taxonomy spine |

**Classes:**
1. Field inversion + ML (FIML lineage): 4 entries, Class 1 status — **DAFoam-running** candidates
2. Tensor-basis neural networks (TBNN): 1 entry, **Sandia public code**
3. Symbolic/sparse regression (SpaRTA/GEP): 2 entries, **PySR/SpaRTA code public**
4. SGS/LES neural closures: 2 entries, code/data status mixed
5. Model-form UQ by eigenvalue perturbation: 3 entries, **no training data needed**
6. Hybrids (NN-mean+GP, model mixtures, sparse variational GPs): 6 entries + subclasses, code/reproducibility mixed
7. Generative/operator (diffusion/score models, FNO/DeepONet): 2 entries with decisive verdict

**Class 7 verdict:** Diffusion and operator models are **not yet suitable as equation-embedded closures** — native operation is sampling/field-generation (surrogates), not providing a composable correction term. One head-to-head benchmark (DARSM vs DeepONet on square-duct + periodic-hill, same families as our benchmark) shows physics-structured alternatives currently win. Suitable for super-resolution of sparse experimental data (data-prep role), not as closure role.

**Where Certonomous sits:** Our closure-challenge entry (`train_closure_periodic_hill_correction.py`) is **outside every class** — post-hoc velocity-field correction via gradient-boosted trees, not a term re-entering equations. Structural consequence: no invariance guarantee by construction. Measured behavior matches prediction: correction hurts on 3 of 8 test cases (those where RANS baseline was already good) and helps where baseline was worst. **Architecture blind to extrapolation** — a feature-level out-of-distribution gate is the documented fix, not yet implemented.

**M2 reproduction ordering ranked by reproducibility + expected transfer:**
1. **Class 5** (eigenvalue perturbation): zero training data, deterministic, directly applicable to converged RANS fields we have; delivers uncertainty envelope not point correction
2. **Class 6c** (sparse variational GP): in-house (Mouzahir & Lermusiaux) already local and read; mature open-source implementation (GPflow, GPyTorch)
3. **Class 2** (TBNN): public code (Sandia, BSD-3), but needs dense per-cell DNS/LES anisotropy training data
4. **Class 3** (SpaRTA): public code, PH demonstrated, duct not
5. **Class 4** (SGS/LES NN): poor fit (LES-specific, we are RANS-only benchmark)

### NUMERICS_KNOWLEDGE.md additions

**Knowledge index entry point:** Every source in CLOSURE_METHODS.md is indexed in `docs/NUMERICS_KNOWLEDGE.md` under "Reading round M1 — closure methods taxonomy", in claim → source → gate/evidence format that file already uses. Enables tracing each claim back to verifiable source and forward to what measurement would validate/refute it.

### LESSONS.md — process rules earned from incidents

| Lesson | Incident | One-line summary |
|---|---|---|
| **L-1** | TMR NACA 0012 docket stale, DAFoam shapes stale, pressure slices stale | Verify docket entries against git log before investigating; repository state wins over brief |
| **L-2** | Backup script reported success while silently discarding 122,800 rows (67% of ledger) | Never trust a verifier's own success report; re-derive independently |
| **L-3** | NACA 4412 finer_relayered drove coverage wrong way, not refuting hypothesis | Negative result is a result; untested hypothesis is not a refuted one |
| **L-4** | 2026-07-27 outage: no OOM message, no panic, but 112.90% committed memory with reclaim at 10x baseline | Absence of error message is not absence of the error; check via independent channel |
| **L-5** | Three agents launched solves detached, set up monitors, exited — monitors died, results orphaned | Long-running solves need blocking foreground run OR supervisor-side watcher, not agent-side monitor |
| **L-6** | PID capture ($!` and `pgrep \| head -1`) routinely grabbed wrapper shell or transient, giving false "finished" reads | Capture PID from thing you launched; key waits on stable identifier (process name, lock file, or artifact) |
| **L-7** | DAFoam adjoint shape gradient disagreement at 46.6% — proposed "converge harder"; test refuted it; plateau is a genuine fixed point of discrete iteration | "Converge harder" not the default fix for gradient disagreement; first ask whether plateau is genuine fixed point |

**Total lessons: 7**, codified in LESSONS.md as required by commit `b1706a3`.

---

## 5. PROCESS AND GOVERNANCE

### Agenda proposal queue

**Total proposals: 19** queued in `demo-output/website/agenda/proposals/`

| Component | Count | Total core-minutes |
|---|---|---|
| Proposals with solve costs | 11 | 2,317 |
| Proposals with zero cost (analysis/documentation only) | 8 | — |
| **Total** | **19** | **2,317** |

**Newest proposals by timestamp (most recent first):**

1. **dafoam-simplec-comparison-audit** (2026-07-28 04:21) — 25 core-min
2. **dafoam-adjoint-memory-scaling-law** (2026-07-28 04:21) — 40 core-min
3. **dafoam-shape-derivative-step-size-study** (2026-07-28 00:51) — 35 core-min
4. **closure-duct-field-inversion** (2026-07-28 00:51) — 420 core-min
5. **closure-baseline-error-estimator-gate** (2026-07-28 00:51) — 45 core-min

**Highest-cost proposals:**
- tmr-naca0012-verification: 604 core-min
- tmr-naca0012-complete-ladders: 480 core-min (approval ambiguity in B-3, not gated technically)
- tmr-flatplate-finest-grids: 327 core-min
- closure-duct-field-inversion: 420 core-min

### Blockers list (consolidated, verified blocked)

**File:** `demo-output/website/agenda/BLOCKERS.md` (last updated 2026-07-28 00:0x UTC)

| Blocker ID | Item | Block reason | Unblock action |
|---|---|---|---|
| **B-1** | Billing alarm / spend cap confirmation | No IAM role (IMDS 404), no ~/.aws, no AWS_* env, no CLI | Attach instance role with cloudwatch/ce read perms, OR paste numbers |
| **B-2** | Ledger off-host sync (S3 or GitHub) | No AWS credentials; origin configured but no usable SSH key or HTTPS token | Attach instance role with s3:PutObject, OR deploy key / PAT for private repo |
| **B-3** | TMR NACA 0012 closure run (~480 core-min) | Approval ambiguity (message quoted closure-challenge track as example, not as final say); cap unknown (B-1) | Confirm spend cap (B-1), OR explicit "yes, run 480 core-min TMR" |

**Each verified blocked, not assumed.** No spend-cap number is reported (reporting unverified one would violate house rules). Ledger backup exists locally but doesn't protect against instance loss (the exact failure mode that occurred 2026-07-27). Single-instance lock is NOT blocked and is live (addresses B-2 at application level, waiting on credentials for true durability).

---

## Summary of Key Corrections and Findings

**Failures reported with equal prominence to successes:**

1. NACA 4412 credential **verdict NOT VALIDATED** — grading method is self-referential; unconverged solve can pass by over-predicting Cl
2. motorBike pressure slice **FAIL** — Cp 1.1192 on 1 sliver face; pre-existing mesh degeneracy, needs Katie's call on publication
3. TMR NACA 0012 Cd **no valid number published** — cold-start averaging drift, gate refuses both transient and steady paths; won't quote unvalidated number
4. DAFoam shape gradients **still unresolved**, 3 of 8 components: refinement makes disagreement worse, not better; ruled out discretization error as cause
5. Closure challenge entry **hurts on 3 of 8 test cases** — post-hoc corrector with no invariance guarantee performs as predicted: helps where baseline is worst, hurts where baseline is fine

**Corrections of earlier team claims:**

- Pressure slices: supervisor claimed "all images correct for publication" without regenerating any; only one was genuinely stale
- DAFoam shape gradients: supervisor overstated defect ("6 of 8 with two sign reversals" → actual: "3 of 8, sign flips already resolved in prior run")
- Hypothesis on gradient disagreement: supervisor proposed "converge harder" → testing refuted it; plateau is a genuine fixed point of discrete iteration
- TMR NACA 0012: supervisor hypothesis "missing viscous term" → measurement refuted; real cause is non-stationary averaging

**Infrastructure improvements verified working:**

- 16 GB swapfile installed and made reboot-persistent (not tested under real load yet)
- Resource guards (`--min-free-disk-gb`, `--min-avail-mem-gb`) tested and verified without disrupting happy path
- Single-instance lock tested: second runner vs live PID refused correctly
- Batch keeper live and restarting batch after memory recovery (confirmed with unbuffered output fix)
- Idle detector documented with three trap scenarios, matches confirmed

**Credentials work:** One validation achieved (TMR flat-plate at 0.293% vs CFL3D), two still open (NACA 4412 grading method defective, TMR NACA 0012 has no valid converged state).

