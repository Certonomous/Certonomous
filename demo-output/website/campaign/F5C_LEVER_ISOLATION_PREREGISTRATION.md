# F5c — isolating the algorithm lever from relaxation: pre-registration

**Written 2026-08-10, before the run exists.** Chief-approved on the Stage A
report: *"the ≈2.4 core-min isolating run separating the algorithm lever from
relaxation is APPROVED — it converts a bar its own author called too low into a
real attribution."*

Parent: `F5C_UNSTEADY_PROBE_PREREGISTRATION.md` (`3734270d` + `d64565c1`);
Stage A results `F5C_STAGE_A_RESULTS.md` (`27a94361`). Model rule per
SUPERVISION_CHARTER §5: session default. Stated, not silent.

---

## 1. What Stage A left confounded

Stage A's M2 scored **PROVEN** — the two legs echoed different
`system/fvSolution` sha256 values and their x_r/H differed by 1.313 H. I reported
at the time that **the bar was too low and the lever was not isolated**, and this
arm fixes the second half of that.

The two legs are the two configurations the record carries, and they differ in
**two** things at once:

| leg | `consistent` | relax p / U | x_r/H |
| --- | --- | --- | --- |
| A1 | **yes** (SIMPLEC) | **0.3 / 0.6** | 5.564 |
| A3 | **no** (SIMPLE) | **0.15 / 0.4** | 6.876 |

So the record's standing claim — *"SIMPLEC moved the number substantially"* — is
a diagonal of a 2×2 factorial with two corners missing. Nothing about the
algorithm alone follows from it.

## 2. The run — one leg completes the factorial

**A4: `coarse`, plain SIMPLE (`consistent no`), relax p 0.3 / U 0.6, 2 000
iterations, `--sample-every 50`.** Everything else identical to A1 and A3.

One run buys **both** isolations:

| contrast | holds fixed | isolates |
| --- | --- | --- |
| **A1 vs A4** | relaxation at 0.3 / 0.6, 2 000 it | **`consistent` alone** |
| **A4 vs A3** | algorithm at `consistent no`, 2 000 it | **relaxation alone** |

## 3. The bar — set from the mistake Stage A made, not from the detector

Stage A's M2 required |Δx_r| > 0.81 H, one `coarse` face spacing. That was wrong,
and the data showed why: each leg's x_r swings far more than that **within its own
run**. A difference between two runs cannot be attributed to what differs between
them if it is smaller than what each does on its own.

**Measured second-half peak-to-peak x_r/H spreads, from Stage A:**
A1 **6.560 H**, A2 1.262 H, A3 **2.578 H**.

> ### M4 — the pre-registered bar
> An effect is **ATTRIBUTABLE** only if its |Δx_r/H| **exceeds the larger of the
> two contributing runs' own second-half peak-to-peak x_r spread.**
>
> - **Algorithm (A1 vs A4):** attributable only if |Δx_r/H| > max(6.560, A4's own
>   spread) — i.e. **> 6.560 H at minimum**.
> - **Relaxation (A4 vs A3):** attributable only if |Δx_r/H| > max(2.578, A4's own
>   spread) — i.e. **> 2.578 H at minimum**.
>
> **NOT ATTRIBUTABLE otherwise**, with the honest reading stated in §4.
>
> Mechanical precondition, checked either way: the echoed `system/fvSolution`
> sha256 for A4 must **differ** from both A1's (`2569808326111612…`) and A3's
> (`94150fe67f56a6e5…`). If it matches either, the run did not do what it was
> asked and nothing is scored.

**I expect this bar to fail, and say so before running.** A1's own swing is
6.56 H and the whole A1–A3 difference was 1.31 H; the algorithm effect has to be
five times the *entire* observed configuration difference to clear it. **The
likely outcome is NOT ATTRIBUTABLE, and that is a real answer, not a null
result** — it would retire the record's "SIMPLEC moved the number substantially"
claim on evidence rather than leaving it confounded forever.

**Stating the temptation in advance so it cannot be indulged:** the available
motivated read here is to lower the bar back to the face spacing (0.81 H), under
which almost any difference "counts". That is exactly the error Stage A made, it
is now documented, and it is pre-refused here.

## 4. What each outcome means — fixed before the run

- **O-I1 — algorithm ATTRIBUTABLE (|Δx_r| > 6.560 H).** SIMPLE and SIMPLEC give
  genuinely different reattachment at fixed relaxation, by more than either run's
  internal wander. The record's claim is **vindicated and isolated for the first
  time**, and the algorithm becomes a first-class variable for any future F5c arm.
- **O-I2 — relaxation ATTRIBUTABLE but algorithm not.** The 1.313 H that Stage A
  saw was **relaxation, not SIMPLEC**. The record's attribution is not merely
  unproven but **misattributed**, and `F5bc_unsteady_statistics.md`'s diagnostic
  table needs its algorithm column re-labelled.
- **O-I3 — neither attributable (expected).** At 2 000 iterations on `coarse`,
  **neither lever is resolvable, because each configuration's own iteration wander
  exceeds every difference between configurations.** The record's
  "SIMPLEC moved the number substantially" is **withdrawn as unsupported** — not
  disproven, unsupportable at this iteration count and detector. This is the
  outcome that closes a claim standing since 2026-07-29.
- **O-I4 — A4 does not run.** Plain SIMPLE at p 0.3 / U 0.6 is *outside the
  relaxation range SIMPLE is normally stable at* — SIMPLEC exists precisely to
  permit those values. **A4 may diverge or crash, and that is a pre-registered,
  reportable outcome, not a failed run:** it would mean the factorial corner is
  physically unreachable, the two recorded configurations are **not separable even
  in principle**, and the record's algorithm attribution can never be isolated by
  this route. If A4 diverges, the finding is reported and no second attempt is
  made at a different relaxation — that would be a different experiment.

## 5. Cost, from the nearest measured basis

**Basis: Stage A's A3 — the same solver, same mesh, same 2 000 iterations, same
`consistent no`, same sampling — measured at 126.6 s = 2.11 core-min**, and A1
(same mesh/iterations, `consistent yes`) at 2.39. **Predicted 2.1–2.4 core-min**
against the chief's approved ≈2.4. No scaling factor is applied to anything; the
predictor is the basis.

If A4 diverges early (O-I4) it costs less, and the measured number is reported
whatever it is.

## 6. Machinery and discipline

Runs through the same driver path as Stage A: mesh birth certificate written at
creation and admitted at entry (`f0e1fef2`), lever echo at t=0 so
`levers_verified_active` is built from the log, case archived under
`F5c_runs/stage_a_A4/` via `collect.py` because `postProcessing/` is gitignored.
`setsid`-detached with `.t0`/`.rc`/`.t1` ledgers, polled inline. Box load checked
against the A3 family's `a3_diag_rung3` container before launch.

## 7. What will NOT be claimed

- No gate is passed; F5c still has no headline number and this arm does not
  produce one. **A4's x_r/H is not a candidate headline** under any outcome — it
  is a factorial corner, measured at an iteration count now known to be far from
  convergence.
- No wander verdict, in either direction (chief policy: not from a `coarse`
  detector).
- No claim about which algorithm is *correct*. This arm measures separability,
  not correctness.

*Nothing below this line existed when this document was committed.*
