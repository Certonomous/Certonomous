# DPW8_V2 L4 divergence — diagnosis pre-registration

**Status:** PENDING — frozen before any compute. No solver has been launched under this document.
**Date frozen:** 2026-08-23 (box clock, `date -u` = Sun Aug 23 19:44:06 UTC 2026)
**Team:** cfd
**Parent record:** `verification/campaign/DPW8_V2_joukowski.md` §3-CORRECTION, §3a, §3b
**Run tree:** `verification/runs/DPW8_V2_runs/`
**Case code (confirmed location today):** `verification/runs/DPW8_V2_runs/{build_mesh.py, joukowski_theory.py, make_case.py, run_case.py}` — the parent record's citation of `demo-output/website/campaign/DPW8_V2_runs/` is **stale**; that path does not exist (`ls` returns "No such file or directory"). A MOVE_MAP batch relocated the tree. The archived solver log still carries the old path in its `Exec :`/`Case :` banner, which is expected and is not a discrepancy.

---

## 0. What this document is, and what it is not

This pre-registers a **diagnosis of a recorded divergence**. It is **not** the L4 gate rung.

- The L4 (Fine, 384×128, 49,152-cell) rung of DPW8_V2 remains **NOT GATED** whatever this diagnosis returns, and this document creates no path to gating it.
- **No `PASS`, `GATE REACHED` or `GATE FAIL` will be issued from this pre-registration**, because there is no physics gate here to pass or fail.
- **No CL, Cd, Cp or grid-convergence claim will be drawn from either arm.** Both arms run 600 iterations of a 3000-iteration case; their fields are diagnostic-only-by-construction, and any coefficient they produce is a *stability indicator*, not a physics measurement. Nothing from this document may be cited as a DPW8_V2 result.
- The per-arm outputs below are labelled **BOUNDED** / **NOT BOUNDED**. These are **measurement outcome labels for a stability indicator, not gate verdicts**, and are deliberately outside the rule-1 vocabulary so they cannot be mistaken for one. The rule-1 vocabulary is used only for the *diagnosis question* itself (§7) and for run completion (§6).

### The question

The L4 rung diverged deterministically: reproduced bit-for-bit on relaunch, `k` blow-up to 2,448,939, `bounding k` events, max |Cd| = 53,437, `checkMesh` reporting `Mesh OK`, and cell aspect ratio ruled out (L3's max AR 925.3 exceeds L4's 642.7 and L3 converges). Root cause is **not established**.

> **Is the L4 divergence a startup/relaxation robustness failure, or something at the L4 discretisation level?**

---

## 1. A correction to the experiment as briefed, made BEFORE freezing

Two premises the diagnosis was framed on are wrong on the disk, and are corrected here rather than carried into the run.

### 1.1 The turbulence convection schemes are ALREADY first-order upwind

`verification/runs/DPW8_V2_runs/run_L4_gate/system/fvSchemes`, read today:

```
div(phi,U)                      bounded Gauss linearUpwind grad(U);
div(phi,k)                      bounded Gauss upwind;
div(phi,omega)                  bounded Gauss upwind;
```

`div(phi,k)` and `div(phi,omega)` are already `bounded Gauss upwind` — the most diffusive, most stable convective discretisation OpenFOAM offers for those equations. There is no stabilising change available on that lever. Worse, the briefed alternative `limitedLinear 1` is **less** diffusive than `upwind`; switching to it would make the arm *more* prone to blow up, so an unbounded result would be uninterpretable and a bounded result would be a stronger claim than the experiment could support. That arm as briefed is an anti-diagnostic and is not run.

**Arm B is therefore re-specified to the only convective discretisation lever that still exists on this case:** `div(phi,U)`, currently second-order `bounded Gauss linearUpwind grad(U)`, dropped to first-order `bounded Gauss upwind`. Rationale: with k and omega convection already fully upwinded, a discretisation-level cause must enter `k` through its **production** term, which is driven by the velocity gradient. `linearUpwind grad(U)` reconstructs face values from a cell-limited gradient; on L4's finest near-wall spacing that reconstruction is the remaining place a spurious strain-rate spike can be manufactured and fed into P_k. This keeps Arm B a genuine one-lever discretisation test.

### 1.2 The `bounding k` events are at iteration 262 and 264, not ~14

Measured from the archived relaunch log by mapping each `bounding k` line to the enclosing `Time =` block:

```
line  7435:  Time=262:  bounding k, min: -5.392193224e-07 max: 2448938.729 average: 57572.62663
line  7492:  Time=264:  bounding k, min: -5.610033731e-06 max: 2432568.241 average: 57809.41616
```

The parent record's "begins within ~14 iterations" describes the **force-coefficient** excursion, not the k-bounding: first |Cd| > 1 at iteration 9, first |Cd| > 10 at iteration 26. Both statements are true of different signals; the brief conflated them. This matters because a startup grace window that excluded only the first ~14 iterations would have been set on a false picture. The window in §4 is set from the measured iteration numbers.

### 1.3 A healthy rung on this case also has a violent startup transient

The most important threshold-setting fact, and the one that would have broken a naive gate: **L3, which converged cleanly and passed its zero-lift gate, reaches max |Cd| = 240.4 at iteration 43** and first exceeds |Cd| = 10 at iteration 25. A criterion of the form "any |Cd| > 10 anywhere means diverged" would falsely condemn the known-good rung. All Cd thresholds below are therefore evaluated on **windows that exclude the startup transient**, and are justified against the healthy rungs' values *in the same windows*.

---

## 2. Evidence base — every threshold below is read from these files

| Artifact | Path | md5 |
|---|---|---|
| Diverged L4 relaunch solver log | `demo-output/website/solve_registry/dpw8_v2_L4_gate_20260729T231415Z.log` | `a838e79619258cf9db2f7df328510322` |
| Diverged L4 force coefficients (relaunch) | `verification/runs/DPW8_V2_runs/run_L4_gate/postProcessing/forceCoeffs1/0/coefficient.dat` | `aeac958a18d2376910b66391c8d858bc` |
| Diverged L4 force coefficients (original, salvaged) | `verification/runs/DPW8_V2_runs/run_L4_gate/postProcessing_partial_1200_bak/forceCoeffs1/0/coefficient.dat` | (not hashed; used only for the §3-CORRECTION cross-check) |
| Diverged L4 y+ history | `verification/runs/DPW8_V2_runs/run_L4_gate/postProcessing/yPlus1/0/yPlus.dat` | — |
| Healthy L3 solver log | `verification/runs/DPW8_V2_runs/run_L3_physics/log.simpleFoam` | `16350124021757cde657ffb4f3d6827e` |
| Healthy L3 force coefficients | `verification/runs/DPW8_V2_runs/run_L3_physics/postProcessing/forceCoeffs1/0/coefficient.dat` | — |
| Healthy L3 y+ history | `verification/runs/DPW8_V2_runs/run_L3_physics/postProcessing/yPlus1/0/yPlus.dat` | — |
| Healthy L1 force coefficients | `verification/runs/DPW8_V2_runs/run_L1_feasibility/postProcessing/forceCoeffs1/0/coefficient.dat` | — |

The `run_L4_gate` directory is **evidence and is read-only for the whole of this experiment.** Nothing in it is written, moved, renamed or deleted. Both arms are fresh directories.

### 2.1 Column identification — the §3-CORRECTION trap, closed

The parent record's original L4 diagnosis was wrong because it read columns 8–9 of `coefficient.dat` as Cl. The header line, read today from the L4 file, is:

```
# Time  Cd  Cd(f)  Cd(r)  Cl  Cl(f)  Cl(r)  CmPitch  CmRoll  CmYaw  Cs  Cs(f)  Cs(r)
```

So **Time is field 0, Cd is field 1, Cl is field 4** (0-based). Columns 8–9 are `CmRoll`/`CmYaw`, of which `CmYaw` happens to equal Cd/100 for this setup — which is exactly how the misread produced plausible-looking small numbers.

**The grading reader identifies Cd and Cl by matching the header names, never by hardcoded index, and refuses (exit 2) if the `# Time ... Cd ... Cl ...` header line is absent or either name is not found.** A hardcoded index anywhere in the reader is a defect, not a shortcut.

### 2.2 Measured windowed statistics — the numbers the thresholds come from

max |Cd| by window, all three rungs, computed from the files in §2 with the header-identified Cd column:

| window (iterations) | L1 healthy | L3 healthy | **L4 diverged** |
|---|---:|---:|---:|
| 1–50 | 7.92e-02 | **240.379** | 53437.5 |
| 51–100 | 7.03e-03 | 125.303 | 26252.9 |
| **100–600** | 6.19e-04 | **1.73803** | **779.795** |
| 150–600 | — | 1.31333 | — |
| 200–600 | 3.30e-04 | 0.575513 | 564.307 |
| **300–600** | 3.26e-04 | **0.0236456** | **431.226** |
| 500–600 | 3.26e-04 | 0.0220439 | 431.226 |

`bounding k` line counts, same code path (`grep -c "bounding"`) on each solver log: **L1 = 0, L3 = 0, L4 diverged = 2**.

y+ on the `airfoil` patch at Time = 600, from `yPlus.dat`:

| rung | min | max | **average** |
|---|---:|---:|---:|
| L3 healthy @600 | 1.508e-03 | 8.8193 | **3.3257** |
| L3 healthy @300 | 7.867e-04 | 23.912 | 5.6760 |
| **L4 diverged @600** | 9.882e-02 | 195.917 | **122.159** |

---

## 3. The two arms

Both arms are **fresh copies**. Neither touches `run_L4_gate`.

**Construction, identical for both:**

```
mkdir -p verification/runs/DPW8_V2_runs/<ARM>
cp -r verification/runs/DPW8_V2_runs/run_L4_gate/0       verification/runs/DPW8_V2_runs/<ARM>/
cp -r verification/runs/DPW8_V2_runs/run_L4_gate/constant verification/runs/DPW8_V2_runs/<ARM>/
cp -r verification/runs/DPW8_V2_runs/run_L4_gate/system   verification/runs/DPW8_V2_runs/<ARM>/
```

Copying, not regenerating via `make_case.write_case`, is deliberate and is required for the arms to be honest controls: `make_case.py:70` writes `writeInterval {END_TIME}`, so a regenerated case would carry `writeInterval 3000`, not the `300` that is actually in the diverged case's `controlDict`. A regenerated case would **not** be the configuration that diverged. Copying `{0, constant, system}` reproduces it byte-for-byte, mesh included (12 MB `constant/polyMesh` per arm, 24 MB total).

**Common edit, applied to both arms (this is the shared diagnostic setting, not a variable):**
- `system/controlDict`: `endTime 3000;` → `endTime 600;`
- `system/controlDict`: `writeInterval` stays `300`; `purgeWrite` stays `2`.

600 iterations is decisive on the measured evidence: the diverged run is at |Cd| = 780 by iteration 105, has both its `bounding k` events by iteration 264, and its Cd is pinned at −431.226 from iteration 300 through 600. The healthy L3 is under |Cd| = 0.024 across 300–600. The two populations are separated by a factor of ~1.8 × 10⁴ inside this budget.

**Arm A — relaxation only.** Directory `verification/runs/DPW8_V2_runs/run_L4_diagA_relax`.
Single edit to `system/fvSolution`:
```
relaxationFactors
{
    fields    { p 0.15; }                              # was 0.25
    equations { U 0.3; k 0.3; omega 0.3; }             # were 0.6
}
```
`fvSchemes` is untouched. Everything else identical to the diverged configuration.

**Arm B — momentum convection scheme only.** Directory `verification/runs/DPW8_V2_runs/run_L4_diagB_scheme`.
Single edit to `system/fvSchemes`:
```
div(phi,U)                      bounded Gauss upwind;   # was: bounded Gauss linearUpwind grad(U)
```
`div(phi,k)` and `div(phi,omega)` stay `bounded Gauss upwind` (they already were — §1.1). `fvSolution` is untouched, so Arm B runs at the **original** relaxation `p 0.25 / U,k,omega 0.6`. Everything else identical to the diverged configuration.

**One change per run, and it is asserted, not asserted-about.** Before launch, for each arm:
```
diff -r verification/runs/DPW8_V2_runs/run_L4_gate/system verification/runs/DPW8_V2_runs/<ARM>/system
diff -r verification/runs/DPW8_V2_runs/run_L4_gate/0       verification/runs/DPW8_V2_runs/<ARM>/0
diff -r verification/runs/DPW8_V2_runs/run_L4_gate/constant verification/runs/DPW8_V2_runs/<ARM>/constant
```
The `system` diff must show **exactly** the lines declared above for that arm (its one lever, plus the `endTime` line) and nothing else. `0` and `constant` must diff **empty**. A diff that is not exactly this stops the arm before launch and is reported, not adjusted around. The diff output is saved to `<ARM>/PRELAUNCH_DIFF.txt` and cited in the results record.

Both arms are single core (`nProcs : 1`), matching L1/L3/L4 and the P1–P5 2–4 rank cap.

---

## 4. Pre-declared gates — the BOUNDED criterion

An arm is **BOUNDED** if and only if **all four** clauses hold. Any one failing makes the arm **NOT BOUNDED**. No clause is advisory and none is labelled diagnostic-only.

**B1 — no k bounding after startup.** Zero lines matching `bounding k` in the arm's solver log at `Time > 50`.
*Justification:* both healthy rungs have **zero** `bounding k` lines over their full 3000 iterations, and the diverged L4's two events are at iterations **262 and 264**. A 50-iteration grace therefore costs nothing in discriminating power (it cannot hide either known event) while protecting against a single benign startup bounce that neither healthy rung happens to exhibit but which a heavily under-relaxed start could plausibly produce.

**B2 — bounded force coefficient through the post-startup window.** max |Cd| over iterations **100–600 < 30**.
*Justification:* L3 healthy = **1.738** in this window; L4 diverged = **779.795**. The threshold sits 17× above the healthy value and 26× below the diverged one — essentially the geometric centre of the two (√(1.738 × 779.795) = 36.8), chosen slightly toward the healthy side so the gate is marginally harder to pass, not easier. The window starts at 100 because L3 healthy reaches 240.4 at iteration 43 (§1.3); a whole-run criterion would condemn a known-good rung.

**B3 — bounded force coefficient through the late window.** max |Cd| over iterations **300–600 < 5**.
*Justification:* L3 healthy = **0.0236** in this window; L4 diverged = **431.226**. The threshold is 86× below the diverged value. It is set at 5 rather than at the geometric centre (3.19) to absorb a bias I can predict but not yet measure: **Arm A's reduced relaxation slows the transient**, so at iteration 600 Arm A is at an earlier effective stage than an unrelaxed run. Under a pessimistic 2× slowdown, Arm A's 300–600 window maps onto L3's 150–300 window, bounded above by L3's 150–600 max of **1.313**. Threshold 5 gives 3.8× headroom over that pessimistic bound while staying two orders of magnitude below the divergence signature. Declaring this bias now, before the run, is the point of the freeze; it will not be discovered afterwards as a reason to move the number.

**B4 — near-wall solution not nonsense.** Average y+ on the `airfoil` patch at `Time = 600 < 20`.
*Justification:* L3 healthy at 600 = **3.326**; L4 diverged at 600 = **122.159**; threshold at the geometric centre (√(3.326 × 122.159) = 20.2). This is the weakest of the four discriminators (37× separation, against B2's 449× and B3's 18,000×), and it is included because the failure is a near-wall one and y+ reads it directly. L4's mesh is 4× finer than L3's, so a healthy L4 should sit **below** L3's y+, making 20 generous; a slowed Arm A compares against L3 @300 = 5.676, still far under. If B4 alone fails while B1–B3 hold, that combination is reported explicitly and the arm is NOT BOUNDED — the threshold is not renegotiated after the fact.

---

## 5. Positive control — required, and run BEFORE any arm is graded (standing rule 3)

A zero from a reader not shown able to see a non-zero is not evidence, and three of the four clauses above are zero-or-small tests. The grading reader `verification/runs/DPW8_V2_runs/analyse_l4_diag.py` **refuses to grade any arm (exit 2) unless the following all reproduce in the same invocation.**

**C1 — the k-bounding counter sees a known non-zero.** Run the counter on the archived diverged log `demo-output/website/solve_registry/dpw8_v2_L4_gate_20260729T231415Z.log` (md5 `a838e79619258cf9db2f7df328510322`, asserted).
Expected, exactly: **2 events, at Time = 262 and Time = 264**, with `max: 2448938.729` and `max: 2432568.241` respectively.

**C2 — the same counter returns zero on a known-clean log.** Run the identical function on `run_L3_physics/log.simpleFoam` (md5 `16350124021757cde657ffb4f3d6827e`). Expected: **0**. This zero is admissible only because C1 in the same invocation proved the same code path returns 2 on a log that has two.

**C3 — the coefficient reader sees the known divergence signature.** Run the Cd/Cl reader on the archived diverged `coefficient.dat` (md5 `aeac958a18d2376910b66391c8d858bc`). Expected, exactly:
- header-identified indices Time = 0, Cd = 1, Cl = 4;
- Cd(201) = **−563.6550**, Cl(201) = **−396.5607**;
- Cd(401) = **−332.8891**, Cl(401) = **−8.8679**;
- max |Cd| over 100–600 = **779.795** at iteration 105;
- max |Cd| over 300–600 = **431.226**.
(All Cd/Cl compared to 4 decimal places; window maxima to 6 significant figures.)

**C4 — the y+ reader sees the known non-zero.** On `run_L4_gate/postProcessing/yPlus1/0/yPlus.dat` at Time = 600, expected average = **122.159**; on `run_L3_physics/.../yPlus.dat` at Time = 600, expected average = **3.3257**.

**C5 — the plant, into the arm's OWN file.** C1–C4 prove the reader works on the archive. They do not prove it is reading *this arm's* file. So for each arm, before that arm's verdict is computed: copy the arm's `coefficient.dat` to a scratch path, inject one row at iteration **350** carrying **Cd = −9.8765e+02**, run the reader on the copy, and assert it reports max |Cd| over 300–600 = **987.65** and over 100–600 = **987.65** (or the arm's own larger value if that exceeds it, in which case the plant is raised to 10× the arm's own maximum and the assertion re-made against the raised value). The arm's real file is never modified; the plant lives only in the scratch copy. **If the reader cannot see the plant in the arm's own file, that arm is not graded.**

The control block's full output is written to `<ARM>/POSITIVE_CONTROL.txt` and quoted in the results record. A results record that does not quote it is incomplete.

---

## 6. Completion — an arm is graded only if its run finished (standing rule 4)

Per arm, all of:
- solver `rc = 0`;
- an `End` line in the log;
- **last `Time = ` in the log == `endTime` == 600**;
- `ExecutionTime` line count == 600;
- fields `U p k omega nut` present under `600/`;
- **every field under `600/` newer than the arm's own `0/U`** — the age guard. `0/` is copied at arm construction and is touched last before launch, so it dates the run allowed to produce the answer.

A guard refuses to launch into a directory where any numeric time directory already exists.

**Pre-declared exception, declared now so it cannot be a post-hoc rescue:** if the log contains `SIMPLE solution converged in N iterations` with N < 600, the arm counts as COMPLETE with `endTime` read as N, and the §4 windows are truncated at N (B3 and B4 then require N ≥ 300; if N < 300 the arm is **BLOCKED** for insufficient window). §3b of the parent record establishes `residualControl` is unreachable on this case — the `U` momentum solve is pinned at a ~6.4e-7 residual floor against a `U 1e-8` criterion — so this exception is expected never to fire, and an early convergence would itself be strong evidence of boundedness.

An arm that fails any completion clause is **`BLOCKED`**, not NOT BOUNDED. A crashed or killed arm is a finding and goes to the supervisor for triage before anything else is concluded from it.

---

## 7. Pre-declared outcome map — what each result licenses, and what it does not

| Arm A (relaxation) | Arm B (momentum scheme) | Diagnosis conclusion |
|---|---|---|
| BOUNDED | NOT BOUNDED | The cause **includes startup/relaxation robustness**. The relaxation carried over unchanged from the coarser rungs is insufficient at L4's near-wall spacing. The momentum-convection lever alone does not rescue it. |
| NOT BOUNDED | BOUNDED | The cause **includes the momentum-convection discretisation at L4** — `linearUpwind grad(U)`'s gradient reconstruction on the finest near-wall spacing, feeding P_k. The relaxation lever alone does not rescue it. |
| BOUNDED | BOUNDED | **Informative, not contradictory.** Both levers independently restore boundedness, so the L4 divergence is a robustness failure reachable from either direction and **neither lever is uniquely identified as the cause**. This is reported exactly that way: two sufficient levers, no unique attribution, and explicitly **no claim that one of them is "the" root cause**. The natural follow-up (not pre-registered here, not run under this document) would be a partial-lever ladder to find which lever is *necessary*. |
| NOT BOUNDED | NOT BOUNDED | **`NOT A RESULT`** for the diagnosis question. What is established is narrower and is still worth recording: the two cheapest single-lever hypotheses are **eliminated**, and the cause lies outside both relaxation and convective discretisation — the remaining suspects being the near-wall treatment / wall functions, the `omega` wall boundary condition on L4's first-cell spacing, and the linear-solver stall documented in §3b. No cause is asserted. |
| any | `BLOCKED` | Diagnosis is **`PENDING`** on the blocked arm. A single BOUNDED arm plus a BLOCKED arm licenses only the statement that that one lever is sufficient; it licenses nothing about the other. |

**In every row above, the L4 gate rung stays NOT GATED and no physics number is published.**

---

## 8. Cost (standing rule 12)

**Unit: core-minutes = wall s × ranks ÷ 60. Both arms are single-rank, so core-minutes = wall minutes.**

**Measured basis:** the L4 relaunch ran **3,387.58 s of solver time to reach iteration 1137**, single core (`verification/campaign/DPW8_V2_joukowski.md` §3a; log `dpw8_v2_L4_gate_20260729T231415Z.log`). That is **2.979 s/iteration**, measured on this exact mesh, this exact solver, this exact box.

| item | figure |
|---|---|
| per-iteration cost (measured) | 2.979 core-s/iter |
| per arm, 600 iterations | 1,787 s = **29.8 core-min** |
| two arms | **59.6 core-min** |
| plus `checkMesh` + preflight, both arms | ≈ 1 core-min (L4 `checkMesh` is seconds) |
| **projected total** | **≈ 61 core-min** |
| dollar figure | 61/60 × $0.0513 = **$0.052** |
| `cost_basis` | **reported-by-owner rate**, $0.0513/core-h, c7a.4xlarge, owner-stated 2026-08-21/22. The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); the dollar figure is derived, not measured. The **iteration rate is measured**, from the cited log. |
| **CAP** | **150 core-min total across both arms (75 core-min per arm)** |

The cap is 2.5× the projection. That headroom is contention, not slack: four `buoyantBoussinesqSimpleFoam` solvers (pids 442445, 450274, 488219, 757934) and one closure-team `simpleFoam` (pid 1114301) are live on this 16-core box at load 5.03, so wall time — and therefore core-minutes — can stretch well past the uncontended rate. **An overrun stops the run; it does not get a new budget** (rule 12). If an arm passes 75 core-min it is stopped and reported as `BLOCKED` on budget, with whatever iterations it reached recorded.

Under the 2026-08-21 blanket this is far under $25 and pre-authorised; it is costed here anyway, because a blanket is not a per-item read (rule 9).

---

## 9. Operational notes — the traps this case has already sprung

Recorded so the next agent does not pay for them twice. Sources: parent record §3a, and confirmed on the box today.

1. **The Bash tool runs non-login shells and OpenFOAM is NOT on `PATH`.** The first L4 relaunch attempt died instantly with `nohup: failed to run command 'simpleFoam': No such file or directory` — `/etc/profile.d/openfoam-selector.sh` never executes. The archived one-line log `demo-output/website/solve_registry/dpw8_v2_L4_gate_20260729T231306Z.log` is that failure, preserved.
   **Fix: source the bashrc in the SAME command as the launch**, never in a preceding call:
   ```
   source /usr/lib/openfoam/openfoam2606/etc/bashrc "" && setsid ... simpleFoam ...
   ```
   **Path confirmed today, two ways:** the file exists (`/usr/lib/openfoam/openfoam2606/etc/bashrc`, 8105 bytes) and is the dpkg-installed location recorded at `docs/OPENFOAM_SOLVER_BUILD.md:78`. `run_case.py:15` hardcodes the same path. **Note:** `docs/OPENFOAM.md:118` gives `OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606"` — that is a **Windows/WSL host** instruction and is not applicable to this box; do not use it.

2. **Launch with `setsid` so the solver outlives the agent.** A foreground Bash solver gets SIGTERMed when the agent's shell goes away. The 2026-07-29 relaunch was itself killed externally at iteration 1137 on a box at load ~19.5.

3. **Check `.done` file BODIES, not their existence.** The same PATH failure produced a stale, misleading `.done` for the F5a Re 3900 rung the same evening — a `.done` recording a *launch* failure, matched by any glob asking "did this job finish". This arm's completion is decided by §6, never by a filename.

4. **Do not touch the running solvers.** Live on this box at freeze time: `buoyantBoussinesqSimpleFoam` pids 442445, 450274, 488219, 757934 (heat-transfer team) and `simpleFoam` pid 1114301 under `/home/ubuntu/closure-data/aposteriori/kaandorp/CBFS13700__TRUTH` (closure team). Load average 5.03 on 16 cores. Two additional single-core arms are within free capacity. Fleet agents are invisible to `pgrep`, so this sweep is a floor on what is running, not a ceiling.

5. **`run_L4_gate` is evidence.** Read-only for the whole of this experiment. Both arms are fresh directories (§3).

6. **`purgeWrite 2` with `writeInterval 300` at `endTime 600` keeps `300/` and `600/`.** That is intended; §6's age guard is checked against `600/`.

---

## 10. Freeze

The gate clauses (§4), their thresholds and the justifying numbers (§2.2), the positive control (§5), the completion rule (§6), the outcome map (§7) and the cost cap (§8) are **fixed at the commit of this file**. No arm may launch before that commit exists and the supervisor has verified it — pre-registration-committed-before-compute is a supervisor personal check and is not the lane's to sign off (`SUPERVISION_CHARTER.md` §3; CLAUDE.md rule 9).

Amendments before first compute are legal and must state the condition and how it was checked. The condition, checked at freeze: **neither `verification/runs/DPW8_V2_runs/run_L4_diagA_relax` nor `verification/runs/DPW8_V2_runs/run_L4_diagB_scheme` exists on disk** — no compute has been spent under this document. After first compute the gates are closed and changes land only as dated addenda that cannot alter a gate, threshold, cap or label.

Results will be recorded in `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md`, citing this file by its commit sha.
