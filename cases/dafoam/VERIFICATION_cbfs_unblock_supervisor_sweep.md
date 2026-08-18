# Supervisor sweep: adversarial verification of the CBFS adjoint sub-PC unblock (W4)

**Session 2026-08-04. Independent verification agent, working under the doctrine that the claim
is wrong until it survives attack. Nothing was taken on the record's word: the patch was diffed
against the actual built image file by file, the FD table was recomputed from the raw perturbation
vectors and logs, the regression signature was matched digit for digit against the pre-patch
record, one FD point was re-derived at a cell the lab never published, with a driver and case copy
made for this sweep, and the env-off regression was re-run cold.**

**The claim under attack** (commit `1cd44c04`, record
`demo-output/website/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md`, evidence
`/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/`): the CBFS adjoint `-9 DIVERGED_NANORINF`
blocker is broken by a rebuilt `libDASolver` (patch
`subpclu_patch/DALinearEqn_subpclu.patch`, image `dafoam-subpclu:v1`, env switch
`DAFOAM_SUBPC_TYPE=lu` → ASM sub-block complete LU); the CBFS beta-field adjoint (21,000 DVs)
converges (reason 2, 667 iters); FD at 3 cells: 0.085%/0.059%/0.199%; env-off regression
reproduces `-9` exactly; the `fiml-adjoint-conditioning-unblock` gate is met.

## Verdicts

| attack | verdict |
|---|---|
| 1. Patch proofread (one change only, default off, regression signature) | **CONFIRMED** |
| 2. Method proofread (primal purity, gradient indexing, truncation behavior) | **CONFIRMED** |
| 3. Independent reproduction (new cell 6490 FD + own env-off regression re-run) | **CONFIRMED** |
| 4. Ledger (185.0 core-min, entries vs timestamps) | **CONFIRMED** |
| 5. Logic ("closure-relevant", leakage) | **CONFIRMED** — one disclosed hump caveat restated in §5 |

No defect found. The docket item `fiml-adjoint-conditioning-unblock` is closed by this sweep
under the supervisor's authorization for a fully-confirmed verification.

---

## 1. Patch proofread: one hunk, one behavior, default off, regression digits exact

**The diff is what it says it is.** `DALinearEqn_subpclu.patch` is a single hunk at
`DALinearEqn.C:266` that adds a comment block plus an env-var read: `localPCType = PCLU` only
when `getenv("DAFOAM_SUBPC_TYPE")` equals `"lu"`, plus one `Info` line on block 0. No tolerance,
objective, residual-definition, shift, ordering, or fill change — those lines
(`PCFactorSetPivotInBlocks`, `MAT_SHIFT_NONZERO`, ordering switch) are untouched below the hunk.

**The built image matches the diff — checked against the image, not the patch file.** The full
`DALinearEqn.C` was extracted from both `dafoam-subpclu:v1` and the parent
`dafoam/opt-packages:latest` and diffed: the only difference is the 19 added lines of that hunk
(`DIFF` reproduced in this sweep's shell log). An md5 sweep of **every** `.C`/`.H` under
`repos/dafoam/src` in both images shows exactly two changed files: `DALinearEqn.C` and its
`lnInclude` copy — nothing else in the source tree moved. All three AD-mode libraries
(`libDASolver.so`, `libDASolverADR.so`, `libDASolverADF.so`) contain the `DAFOAM_SUBPC_TYPE`
string, so all three were rebuilt from the patched source.

**Default really is off, and the regression signature is bit-exact.** `run_cbfs_sublu.sh` passes
`-e DAFOAM_SUBPC_TYPE=lu` only for the `sublu` variant; the regress variant's log
(`cbfs_regress_computetotals.log`) contains no `DAFOAM_SUBPC_TYPE` line and ends
`Total iterations: 0. PetscConvergedReason: -9.` with iteration-0 residual
`7.091590452305e-04` — the same reason, iteration count, and all 13 residual digits as the
pre-patch record: S1's CBFS ordering sweep ("the printed iteration-0 residual is identical
(7.091590452305e-04) in all five", `S1_FIML_FIELD_INVERSION.md:418`) and PROOF §25.2–25.3
(`PROOF.md:2646`, `:2707`). The regress and sublu run directories use byte-identical
`runScript.py` (diffed: `IDENTICAL`) — B3's exact `-9` configuration (patchVelocity DV, rcm,
pcFillLevel 1), so the treatment/control pair differs by the env var alone.

## 2. Method proofread: the FD table survives recomputation from raw artifacts

**(a) Primal purity and the baseline control.** The patch touches only `createMLRKSP` — the
adjoint linear solve; the primal never enters that code. Measured, not argued: the FD driver
(`run_cbfs_fd.sh`) runs `-task run_model` (no adjoint) on the patched image with the env var
**unset**, and its unperturbed baseline objective is `1.5279278906359758e-02` — bit-identical to
all 17 digits with the adjoint run's objective computed with the env var **set**
(`cbfs_beta_computetotals.log:12073`). The stated control holds, and it doubles as a
primal-invariance proof across the switch. Every perturbed objective differs from baseline only
through the beta file: each `fd_beta_*.npy` was loaded in this sweep and verified to differ from
`fd_beta_ones.npy` (all-ones, verified) at **exactly one index** — the named cell — by exactly
±h. Fresh process per point and cold `rm -rf processor*` are in the driver text.

**(b) Indexing cannot fake agreement here — and the numbers were recomputed anyway.** The FD
perturbation is applied to component `c` of the OpenMDAO `dvs.beta` vector, and the adjoint value
is `g[c]` of `compute_totals()` **with respect to that same vector**
(`cbfs_beta/runScript.py:117-154`): whatever DAFoam's internal cell ordering is, FD and adjoint
are indexed in the same space by construction, so an off-by-one or reordering would show as
disagreement, not agreement. `cbfs_beta_grad.npy` matches the log's `GRAD` line
(n=21000, norm 1.4558046603e-05, min/max match), `g` at cells 5491/6740/12486 equals the
published adjoint column to all digits, and the three cells sit at ranks 0, 3, and 14 of |g| —
"spanning the top of the distribution" as claimed. Recomputing central differences from the
objectives in `cbfs_fd_summary.txt` reproduces `fd_table.json` exactly:
0.0854% / 0.4599% / 0.0589% / 0.1989%. (Provenance nit, no number touched: the checked-in
`make_fd_points.py`/`analyze_fd.py` at the evidence root are the *hump* variants; the CBFS
table's assembly script is not on disk. This sweep's independent recomputation closes that gap.)

**(c) Truncation behavior.** Cell 5491's FD error grows 1.634e-9 → 8.772e-9 as h doubles — a
factor 5.4 against O(h²)'s ideal 4, with the FD moving away from the adjoint value, and
Richardson extrapolation of the two FD values lands within ~0.04% of the adjoint number.
Consistent with central-difference truncation dominating, as the record claims.

## 3. Independent reproduction: a cell the lab never published, this sweep's own driver

**New FD point.** Cell **6490** (rank 10 of |g|, adjoint g[6490] = 1.519706e-06 — from a
different rank band than any published cell) was re-derived with perturbation vectors built by
this sweep, in an isolated copy of the case
(`/home/ubuntu/certonomous-runs/W4-verify-sweep/`), two-sided h=0.05, `--cpus=2`
(another agent held the box's solver headroom):

```
beta[6490] = 1.05:  OBJ 1.5279354895693945e-02   (157 s)
beta[6490] = 0.95:  OBJ 1.5279202892977342e-02   (151 s)
central FD:  1.520027166028e-06
adjoint g:   1.519705840939e-06
rel err:     0.0211%
```

Tighter than any of the three published cells (0.085/0.059/0.199%), at a point the lab did not
choose. A wrong indexing, a stale gradient file, or a lucky triple would not survive this.

**Env-off regression, re-run cold by this sweep** (not the lab's log): fresh case copy, patched
image, `DAFOAM_SUBPC_TYPE` unset →
`Main iteration 0 KSP Residual norm 7.091590452305e-04`,
`Total iterations: 0. PetscConvergedReason: -9.`, rc=1 (`logs/regress_verify.log`, 241 s wall).
Reason, iteration count, and all 13 residual digits match the lab's regression log and the
pre-patch record independently of anything W4 wrote.

## 4. Ledger: 185.0 core-min, three entries opened to the second

| entry (billed) | check |
|---|---|
| offline ladder 693 s / 46.2 | individual walls in the five logs + the nd kill: 7.01 + 7.04 + 4.04 + 6.92 + 68.03 + 600 = **693.04 s**; log mtimes 15:11:00–15:33:54 bracket the sequence |
| hump 819 s / 54.6 | `hump_sublu_mem.log` first/last samples 15:44:39Z → 15:58:15Z = **816 s** of 5 s cadence against 819 s billed; summary stamped 15:58:18Z |
| FD sweep 642 s / 42.8 | per-run walls in `cbfs_fd_summary.txt` sum to **exactly 642**; the nine `fdlogs/` mtimes tile 16:06:51–16:16:21 at ~71 s spacing |

CBFS beta (246 s ending 16:03:30Z; log mtime 16:03:29, internal timing 231.5 s + container
start) and the regression (92 s; log mtime 15:24:11, internal 85.07 s) also reconcile. The seven
entries sum to **185.0** as published; the `sublu_nd.log` supports "killed at 600 s" (progress
lines stop after iter 100, no RESULT line).

## 5. Logic: "closure-relevant" and the leakage boundary hold

CBFS is the field-inversion **training** case: it is not among the 8 scored closure-challenge
test cases (`closure_challenge_criterion_test_case_table.json` — two PH alphas ×2 splits, three
ducts, `NASA_2DWMH`), the C2 record updated today reaffirms the entry trains on public CBFS
inversion data, and the reference field driving `varianceU` is CBFS's own public Bentaleb LES
(`0/UData`; provenance in `W2_SPARTA_CBFS_DATA_FORENSICS.md`). No scored test case's ground
truth entered the gate case. Calling a converged, FD-verified 21,000-DV beta gradient on that
case "closure-relevant" is the record's own longstanding usage (S1: "no closure-relevant case on
which this lab can run a field inversion" named CBFS and the hump as the two).

**One caveat, disclosed by the record itself, restated so it is not lost:** W4 §5b's hump attempt
computes `cfVar` against NASA_2DWMH experimental Cf — a **scored** case. That run produced no
gradient (stopped unconverged at ~iter 900), nothing from it feeds any entry or score, and S1 §7
already carries the standing warning that a hump inversion is in-sample by construction. The
gate claim rests on CBFS alone and is unaffected.

## 6. Cost of this sweep

| run | wall | cpus | core-min |
|---|---|---|---|
| FD primal, beta[6490]+0.05 | 157 s | 2 | 5.2 |
| FD primal, beta[6490]−0.05 | 151 s | 2 | 5.0 |
| env-off regression re-run | 241 s | 2 | 8.0 |

**18.3 core-min total.** The FD reproduction (10.3) sat under its 15 core-min cap. The
regression was estimated under its 7 core-min bar from the lab's 92 s / 4-cpu wall; the 2-cpu
oversubscription (4 ranks on 2 cpus) ran it to 8.0 — billed as measured, overrun stated rather
than hidden.

## 7. Evidence written by this sweep

`/home/ubuntu/certonomous-runs/W4-verify-sweep/`: `cbfs_fd/` (isolated case copy,
`vbeta_c6490_{p,m}0.05.npy` built independently), `logs/c6490_{p,m}0.05.log`,
`logs/regress_verify.log`. Everything else cited above is the lab's own evidence, read in place
and never modified.
