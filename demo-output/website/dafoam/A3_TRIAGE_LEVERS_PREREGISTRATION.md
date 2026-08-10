# A3 iteration-count lever triage (scope C subset) — PRE-REGISTRATION

Filed 2026-08-10 by the DAFoam solver agent, chief ruling 2 of the 2026-08-10 dispatch.
Approved 35–45 core-min, running BEFORE rung 3 because its output is instrumental to rung 3's
price and cap. Committed BEFORE compute.

## 1. The question, and why it is worth its cost

Rung 2 measured the thing that now governs the ladder's economics: **iteration count scales
superlinearly in cells** — CD exponent 1.50, CL exponent 1.70 — which is why rung 3 (79,560
cells) is priced at ~113 core-min with a required `gmresMaxIters` ≥ 4000 rather than ~2x rung
2. Every one of those iterations is Krylov work against the PC. **Does any available lever cut
the iteration count on the WORKING (PC-active) configuration?** A lever that does changes rung
3's price and cap directly; one that does not confirms the superlinear trend as intrinsic to
this operator rather than an artifact of a weak preconditioner setting.

This is the live half of scope C. The dead half — the same levers against the superseded
`transonicPCOption: 2` baseline — is retired (`D3_VARIANT_COLD_RERUN_PREREGISTRATION.md` §6).

## 2. Rung, baseline, and the honest scope limit

**Rung 1 (21,840 cells, `A3-onera-m6-sweep-n15_21840`)**, whose working-config baseline is
measured, converged and FD-verified: **CD 368 iterations, CL 383 iterations**, both reason 2
(11b90d25), 7.33 core-min. Rung 1 is chosen because three arms fit the approved budget there
(~12 core-min each) and would not at rung 2 (~29 core-min each, ~87 total).

**Pre-stated scope limit, so no one over-reads the result:** this triage measures each lever's
DIRECTION and rough MAGNITUDE at 21,840 cells. It does **not** prove transfer to 79,560 cells —
a lever's benefit can itself be mesh-dependent. A material winner here earns a single
confirmation arm at rung 2 before rung 3's pre-registration adopts it; a null here is taken as
evidence against that lever generally, since none of the three is expected to reverse sign with
mesh size.

## 3. The three levers and the selection basis

Selected as the three with a mechanism that acts on **Krylov iteration count** specifically —
not on memory, not on robustness, not on scope. The other eight retired variants fail this
basis: `sparsify`/`mgso_sparsify` weaken the PC to save memory (expected to INCREASE
iterations), `bigbudget` only raises the cap (not a lever), `cl_only` narrows scope,
`noresnorm`/`mgso` variants act on residual scaling and orthogonalization robustness rather
than on the preconditioner's spectral effect.

| # | lever | change from the working config | mechanism on iteration count |
|---|---|---|---|
| L1 | **pcFillLevel 0 → 1** | `adjEqnOption.pcFillLevel: 1` | a stronger incomplete factorization clusters the preconditioned spectrum — the textbook first lever; each iteration costs more, so the verdict is iterations AND wall |
| L2 | **gmresRestart 200 → 1000** | `adjEqnOption.gmresRestart: 1000` | a larger Krylov subspace before restart retains more search directions; restarting at 200 discards them, and at 987–1171 total iterations this run restarts ~5x |
| L3 | **Richardson PC iterations** | `adjEqnOption.globalPCIters: 3, localPCIters: 3` | applies the preconditioner repeatedly per Krylov step — a stronger effective PC per iteration |

**A recorded prior that makes this a real test, not a formality:** R5 found that *strengthening*
the PC (fill 1, Richardson) REINTRODUCED collapse on this family — but that was measured with
the transonic PC inactive, i.e. against the superseded baseline. Whether the same strengthening
helps or hurts once the PC is actually on is exactly what has never been asked.

## 4. Configuration and proofs (identical across arms except the lever)

Base = rung 1's converged config: `transonicPCOption: 1`, stock ILU, `natural`,
`gmresRelTol 1e-4`, `DAFOAM_SUBPC_TYPE` UNSET, 4 ranks, task `compute_totals`.
**`gmresMaxIters` set to 2000 in ALL arms including nothing else** — so a lever that makes
things worse reports a larger iteration count instead of truncating at a cap and confounding
the grade (the attempt-1 lesson). The baseline it is graded against (368/383) converged far
below any cap and is unaffected by this.

Staged copy per arm (guidelines §8 item 3) — never sequential reruns in one dir — each
`decomposePar -force` from the pristine serial `0/`. Required in every arm's log before its
number counts: `transonicPCOption 1;`, NO sub-LU banner, the rung-1 cold signature
`0.5969274433533561`, and the lever's own echo in the DAOption/KSP dump (`ILU PC Fill Level:`,
`GMRES Restart:`, `Global PC Iters:`/`Local PC Iters:`). Launcher-side `lever_echo.txt` per arm
declares the intended lever; the solver's own dump is what confirms it.

Memory guard: rung 1's record ILU peak is 5,876.6 MiB; L1 and L2 both raise memory (fill-in;
subspace storage). Cap `--memory=16g`; if an arm approaches the cap or drives host
MemAvailable below 6 GB it STOPS and the memory behavior is reported as the finding.

## 5. Grading (pre-registered, so no lever gets credit for noise)

Primary metric: **iterations to `PetscConvergedReason: 2`**, per solve, versus the baseline
(CD 368, CL 383). Secondary, reported always: **wall per arm** — a lever that cuts iterations
but costs more per iteration may not be a win, and the ladder pays wall, not iterations.

- **MATERIAL WINNER**: reduces the iteration count by **>10%** on BOTH solves AND does not
  increase wall. (>10% is the pre-registered materiality bar from the scope-C filing.)
- **MIXED**: cuts iterations >10% but increases wall — reported as such, adopted only if rung
  3's binding constraint is the cap rather than time.
- **NULL**: within ±10% on either solve.
- **HARMFUL**: increases iterations >10%, or fails to converge (any negative reason). A
  non-convergence under a strengthened PC is the R5 collapse signature re-appearing WITH the
  transonic PC on — a finding in its own right, and it would be reported as one.

## 6. What each outcome means for rung 3 (pre-stated, per the ruling)

- **A material winner** → rung 3's pre-registration ADOPTS it, and rung 3's price and cap are
  recomputed from the winner's measured iteration ratio (e.g. a 25% cut moves the CL estimate
  from ~3,460 to ~2,600 iterations and the cap requirement from ≥4000 to ≥3000). One rung-2
  confirmation arm runs first, per §2's scope limit.
- **All three null** → **the superlinear exponent is intrinsic**, not an artifact of a weak PC
  setting: rung 3 launches at the corrected basis exactly as filed (~113 core-min,
  `gmresMaxIters` ≥ 4000), and the exponent becomes the honest basis for any extrapolation
  toward production meshes rather than a number awaiting a cheaper trick.
- **A harmful/collapse result** → recorded as the R5 strengthening signature reproduced with
  the PC active, which sharpens the conditioning story; rung 3 proceeds as filed.

## 7. Mechanics and price

setsid + `.t0/.rc/.t1` ledger per arm, logs `triage_<lever>.log` in each staged dir, run
**sequentially** (three concurrent 4-rank arms would contend for memory on a 30 GB box; the
graded metric is iteration count, but the memory guard is what forces the ordering), polled
inline, explicit handoff if the turn ends mid-run. Price: 3 arms x ~12 core-min ≈ **36
core-min**, inside the approved 35–45; measured spend reported per arm. Results appended to
this file's §8 and carried into rung 3's pre-registration.

## 8. RESULTS, 2026-08-10 — all three levers cut iterations materially; **the R5 strengthening prior is overturned with the PC active**

Three staged arms, run sequentially, each with all four required proofs in-log
(`transonicPCOption 1;`, no sub-LU banner, cold signature `0.5969274433533561`, and the
lever's own echo). Baseline: rung 1's converged working config, CD 368 / CL 383, 110 s.

| arm | lever echo in-log | CD iters | CL iters | wall | core-min | verdict per §5 |
|---|---|---|---|---|---|---|
| baseline (11b90d25) | `ILU PC Fill Level: 0`, `GMRES Restart: 200` | 368 | 383 | 110 s | 7.33 | — |
| **L1 fill1** | `ILU PC Fill Level: 1` | **236 (−35.9%)** | **250 (−34.7%)** | 105 s (**−4.5%**) | 7.00 | **MATERIAL WINNER** (iterations cut, wall not increased) |
| **L2 restart1000** | `GMRES Restart: 1000` | 311 (−15.5%) | 306 (−20.1%) | 103 s (−6.4%) | 6.87 | **MATERIAL WINNER** |
| **L3 richardson** | `Global PC Iters: 3`, `Local PC Iters: 3` | **209 (−43.2%)** | **211 (−44.9%)** | 133 s (+20.9%) | 8.87 | **MIXED** (largest iteration cut; wall +21%) |

Triage spend **22.7 core-min against the approved 35–45** — inside budget, reported as
measured. All three arms returned `PetscConvergedReason: 2` on both solves; none collapsed.

**The finding that outranks the ranking.** R5 recorded that *strengthening* the preconditioner
(fill 1, Richardson) REINTRODUCED collapse on this family. With the transonic PC active, both
strengthening levers not only fail to collapse — they are the two largest iteration cuts on the
board (−36% and −44%). **The R5 collapse-on-strengthening was itself an artifact of the
inactive transonic PC**: strengthening a preconditioner assembled around a term that should
have been dropped made a bad approximation worse, and with the term correctly dropped
(`transonicPCOption 1`) the ordinary numerical-linear-algebra intuition holds again. That
retroactively explains a standing anomaly rather than adding one.

## 9. Implication for rung 3 (per §6's pre-stated mapping)

§6's material-winner branch fires — for all three. Rung 3 estimates, scaled from the corrected
basis (CD ≈ 2,570 / CL ≈ 3,456 iterations at 79,560 cells under the baseline config):

| lever adopted | rung 3 CD | rung 3 CL | cap requirement |
|---|---|---|---|
| none (baseline) | ~2,570 | ~3,456 | ≥ 4000 |
| L1 fill1 | ~1,648 | ~2,256 | ≥ 3000 |
| L2 restart1000 | ~2,172 | ~2,761 | ≥ 3500 |
| **L3 richardson** | **~1,460** | **~1,904** | **≥ 2500** |

**Recommendation for rung 3: adopt L3 (Richardson), not the wall-cheapest L1.** The reasoning
is which constraint binds at 79,560 cells. Rung 3's known second wall is MEMORY — the D3
envelope measured 17,603.8 MiB there at `pcFillLevel 0`, against a 30 GB box with a 6 GB host
floor (~24 GB usable). L1 adds ILU fill-in to a 6-field Jacobian (at 99,840 cells the archived
fill1 variant went from 18,422 MiB to ≥20,480 MiB, censored at its cap), and L2 stores 1000
Krylov vectors instead of 200 (~+3.8 GB at this size). **L3 is the only one of the three that
buys its iteration cut with no memory at all** — it applies the existing preconditioner more
times — and it buys the largest cut, halving the cap requirement. Its +21% wall is the right
currency to spend when memory and cap are what bind.

**Prerequisite, per §2's own scope limit, not waived:** the triage measured at 21,840 cells and
does not prove transfer to 79,560. Rung 3's pre-registration therefore carries a **rung-2
confirmation arm as stage 0** (L3 at 42,120 cells, graded against rung 2's measured CD 987 / CL
1171); rung 3 adopts the lever only if the confirmation reproduces a material cut, and reverts
to the filed baseline basis if it does not.
