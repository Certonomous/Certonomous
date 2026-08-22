# T3 results: heated backward-facing step against a primary that is not held

Campaign T, tier 1, rung T3, attempt 1. Written 2026-08-22, from a solve that
began 2026-08-21 18:03 Z and finished 2026-08-22 10:59 Z. Run tree
`verification/runs/T-family/T3_runs/`, 8 cases
(`R_c R_m R_f P_m C_lam_m W_m D_m O_m`). Comparator `analyse_t3.py`, frozen at
commit `628ef452` (2026-08-21 18:02:09 Z) before any case directory existed
(Charter §2d — the earliest case `0/T` is `R_f` at 18:03:22 Z, **+73 s** after
the freeze), verified byte-identical at analysis time: sha256
`f41c544d…498741`. Secondary digitisation `T3_secondary_digitisation.json`
frozen in the same commit, sha256 `8383a677…1faff4`, also byte-identical.
**`T3_reference_primary.json` does not exist**; `primary_sha256` is `null`.

**Rung verdict: NOT A RESULT — 4 of 4 graded rows, and not on the reference.
Every ladder level is NOT CONVERGED against the registered `1e-6` criterion and
every graded triple is DIVERGENT or OSCILLATORY, so gates (1) and (2) of
pre-registration §7.1 both fire ahead of gate (3). BLOCKED — the state the
supervisor expected and the state §7.2 registered as "verdict today" — is *not*
reached, because the rows never get far enough down §7.1 for the missing
primary to be what stops them. The primary's absence remains true and remains
disqualifying, but it is not today's binding constraint: the ladder is.
0 PASS, 0 GATE FAIL, 0 BLOCKED, 4 NOT A RESULT.** Analysed 2026-08-22
17:33:22 Z (`gate_t3.json`, sha256 `5e23f84e…780c04`). Docket: **D450**
(assigned at commit time; latest assigned was D447 when this was written).

Prediction 8 of §8 said "at least one of G1–G4 comes back not CONVERGING". All
four did, and for two independent reasons. That prediction is the one this rung
most emphatically confirmed.

---

## 1. Completion audit: 8 of 8 cases

`mark_done_t3.py` was re-run at 2026-08-22 17:32 Z and reported **`8/8 cases
meet the strict completion rule`**, exit 0. Only `DONE.R_f` was created; the
other seven markers pre-existed and the tool never retracts.

| case | `STATUS` | wall, s | `nProcs` | cells | `DONE` marker written (Z) |
| --- | --- | ---: | ---: | ---: | --- |
| R_c | `rc=0 wall=3269 checkMesh_rc=0` | 3 269 | 1 | 36 000 | 2026-08-21 22:22:18 |
| R_m | `rc=0 wall=15901 checkMesh_rc=0` | 15 901 | 1 | 92 160 | 2026-08-21 22:38:22 |
| **R_f** | `rc=0 wall=60974 checkMesh_rc=0` | 60 974 | 1 | 235 520 | **2026-08-22 17:32:43 (this report)** |
| P_m | `rc=0 wall=15849 checkMesh_rc=0` | 15 849 | 1 | 92 160 | 2026-08-21 22:56:28 |
| C_lam_m | `rc=0 wall=10314 checkMesh_rc=0` | 10 314 | 1 | 92 160 | 2026-08-21 21:26:07 |
| W_m | `rc=0 wall=1490 checkMesh_rc=0` | 1 490 | 1 | 28 160 | 2026-08-21 21:52:09 |
| D_m | `rc=0 wall=10580 checkMesh_rc=0` | 10 580 | 1 | 79 360 | 2026-08-21 21:27:39 |
| O_m | `rc=0 wall=26780 checkMesh_rc=0` | 26 780 | 1 | 128 000 | 2026-08-22 01:33:13 |

`R_f` finished at 10:59:39 Z on 2026-08-22 and sat unmarked for 6 h 33 min
purely because the marker tool had not been re-run; nothing about the case
changed in that window.

### 1.1 Strict-rule evidence for `R_f`, test by test

The six tests of `mark_done_t3.py` (§9 of the pre-registration), each verified
directly on disk before the tool was run:

| # | test | evidence for `R_f` |
| --- | --- | --- |
| 1 | `STATUS` reports `rc=0` | `STATUS.R_f` = `rc=0 wall=60974 checkMesh_rc=0` |
| 2 | `log.solve` ends with OpenFOAM's own `End` | last non-blank line of `log.solve` is `End` |
| 3 | last written time = `controlDict` `endTime` | time dirs `0 0.orig 18000 20000`; `endTime 20000;` — last numeric time **20000 == 20000** |
| 4 | final time carries every field the comparator reads | `constant/turbulenceProperties` says `simulationType RAS`, so `T U p_rgh alphat phi` **and** `nut k omega` are required; `20000/` holds all nine (plus `p`, `uniform`) |
| 5 | `ExecutionTime` line count = `endTime` | `grep -c '^ExecutionTime' log.solve` = **20000** — no skipped iteration, no restart replay |
| 6 | age guard: every final field newer than the case's own `0/T` | `0/T` 2026-08-21 18:03:22.426 Z; `20000/{T,U,p_rgh,alphat,phi,nut,k,omega}` all 2026-08-22 10:59:38.86–39.52 Z, **+60 977 s**. No field is stale |

Test 6 is the L-143 contamination guard, and it is the reason a marker is
evidence rather than an assertion.

## 2. The comparator run record

```
$ python3 /home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/analyse_t3.py --selftest
selftest: 21/21 checks passed                                    exit 0

$ python3 /home/ubuntu/Certonomous/verification/runs/T-family/T3_runs/analyse_t3.py
...
4 graded rows: NOT A RESULT 4
PRIMARY NOT OBTAINED: no band is armed; a graded row that passes the
convergence and triple gates is BLOCKED, and the secondary digitisation is
printed for information only.
wrote .../gate_t3.json                                           exit 0
```

Run in place (no `--root`), stderr empty, exit 0 on both invocations.
`generated_utc` 2026-08-22T17:32:54Z, `finished_utc` 2026-08-22T17:33:22Z.

The `--selftest` proved all four branches of §7.1 on synthetic triples before
anything real was read, including the two that matter here: a DIVERGENT,
STAGNANT or OSCILLATORY triple with the fine value **inside** a band still
returns NOT A RESULT (D440's amendment, made binding in this rung), and a
missing primary returns BLOCKED with the secondary deviation carried as
information. It also proved the unequal-ratio GCI reproduces T1c's `gci()` to
`0.00e+00` when the ratios are equal, and that the verdict vocabulary is closed.

| artifact | sha256 recorded in `gate_t3.json` |
| --- | --- |
| `analyse_t3.py` (comparator) | `f41c544d7552e7abfe6adeb8ff1d7ff4c14288017d36821ea3040f1158498741` |
| `T3_secondary_digitisation.json` (secondary) | `8383a677e79d5b2b5ddd9756f2f4815efdc7893cedf5c22bf3ce9f6a1d1faff4` |
| `T3_reference_primary.json` (primary) | **`null` — `primary_present: false`** |

Both non-null hashes were re-derived from `git show HEAD:<path> | sha256sum`
and match the working tree byte for byte: the comparator that graded this rung
is the one frozen at `628ef452`.

### 2.1 The planted-zero control

Registered in §5: the convergence zero is verified live, before the comparator
reads anything, by writing `1.234e-03 K` into a copy of a real field and
reading it back off disk.

```
planted-zero control on R_m: {'passed': True, 'planted': 0.001234,
  'read_back_delta': 0.0012340000000108375,
  'reader_max_change': 0.0014646250706960018,
  'reader_state': 'NOT_CONVERGED', 'between': ['18000', '20000']}
```

**PASS.** The planted `1.234e-03 K` was read back to `1.0e-14 K`, the reader saw
it, and the control left the original file untouched. The reader's own
`max_change` on the untouched `R_m` pair is `1.4646e-03 K`, i.e. `R_m` is
genuinely moving by more than the planted amount — the instrument is not
reporting zeros because it cannot see change.

## 3. Iterative convergence: every case fails, and this is gate (1)

Criterion (§5, T1c's number, amended into the design before any case existed):
the largest change of any cell value of `T`, and separately of `U`, between the
checkpoints at `18000` and `20000` must be at most `1e-6` **of that field's
range**.

| case | `T` max change, K | `T` relative | `U` max change, m/s | `U` relative | vs `1e-6` tol | state |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| R_c | 2.5248 | 4.944e-02 | 1.6776 | 1.524e-01 | **49 400 ×** | NOT CONVERGED |
| R_m | 1.4646e-03 | 2.855e-05 | 1.5174e-03 | 1.378e-04 | 138 × | NOT CONVERGED |
| R_f | 5.5392e-02 | 1.095e-03 | 4.0825e-02 | 3.703e-03 | **3 700 ×** | NOT CONVERGED |
| P_m | 7.9186e-04 | 1.526e-05 | 1.5174e-03 | 1.378e-04 | 138 × | NOT CONVERGED |
| C_lam_m | 10.667 | 6.000e-01 | 24.895 | 1.189e+00 | 1 190 000 × | NOT CONVERGED |
| W_m | 4.6049e-05 | 1.417e-06 | 1.3735e-05 | 1.252e-06 | **1.25 ×** | NOT CONVERGED |
| D_m | 9.7155e-04 | 1.893e-05 | 1.3382e-08 | 1.246e-09 | 19 × | NOT CONVERGED |
| O_m | 4.9409e-03 | 9.622e-05 | 2.1092e-03 | 1.915e-04 | 192 × | NOT CONVERGED |

**The criterion is not relaxed after the fact** (§5 says so in terms). `W_m`
misses by a factor of 1.25 and `D_m` by 19; `R_c` misses by 49 400 and the
laminar control by six orders of magnitude. §5 anticipated exactly this — "a
separated RANS flow under SIMPLE may never meet this; if it does not, the rows
are NOT A RESULT and the record says so" — and §11 anticipated the mechanism:
"a steady RANS of a flow whose shear layer flaps; the iterative-convergence
gate reports a limit cycle as NOT CONVERGED and the rung then says so rather
than averaging."

**The ladder is not ordered by mesh.** `R_m` (relative `2.9e-05`) is 38 × better
converged than `R_f` (`1.1e-03`) and 1 700 × better than `R_c` (`4.9e-02`).
Whatever the coarse and fine levels are doing at 20 000 iterations, it is not a
monotone approach to a steady state, and the finest mesh is *further* from one
than the medium. That is the most likely origin of §4's DIVERGENT triples, and
it means the triples cannot yet be read as a statement about mesh convergence
at all. §5's registered remedy is an **extension** from `latestTime` under the
T1b §6 disclosure rule, with the decision taken on the convergence state alone
and never with a `St` in view. This report takes no such decision; it records
the state.

## 4. The Roache triple, and the state of each graded quantity

Effective refinement ratios from the cell counts: `r21 = 1.5986`, `r32 =
1.6000`. Observed order uses the unequal-ratio fixed-point form; `Fs = 1.25`.

**Every number in this section is the frozen comparator's own output, read from
`gate_t3.json`. Nothing here is a re-computation by this report.**

| quantity | coarse | medium | fine | `e21` | `e32` | observed `p` | GCI | state |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `St_peak` (G1) | 0.00336773 | 0.00343808 | 0.00354497 | −1.0689e-04 | −7.0350e-05 | **−0.892** | not emitted | **DIVERGENT** |
| `x_peak/H` (G2) | 6.08935 | 6.13506 | 6.12114 | +1.3926e-02 | −4.5710e-02 | ratio **−3.282** | not emitted | **OSCILLATORY** |
| `St(10 H)` (G3) | 0.00298297 | 0.00304716 | 0.00312892 | −8.1759e-05 | −6.4192e-05 | **−0.516** | not emitted | **DIVERGENT** |
| `St(20 H)` (G4) | 0.00224935 | 0.00229616 | 0.00234778 | −5.1623e-05 | −4.6808e-05 | **−0.209** | not emitted | **DIVERGENT** |
| `x_R/H` (M1) | 7.01279 | 7.01011 | 6.98332 | +2.6788e-02 | +2.6854e-03 | **−4.903** | not emitted | **DIVERGENT** |
| `Cf(15 H)` | 0.00159320 | 0.00163293 | 0.00166762 | −3.4686e-05 | −3.9725e-05 | **+0.285** (37 iters) | not emitted | **STAGNANT** |

**On GCI.** The string `gci` does not appear anywhere in `gate_t3.json`, for
any quantity. This is the comparator behaving correctly, not an omission: a GCI
is a Richardson error estimator, it requires a positive observed order, and
four of these six orders are negative while a fifth is 0.285. `Fs = 1.25` is
recorded in the JSON as the constant it would use. **No GCI band exists for any
T3 quantity today, and this report does not manufacture one** — computing a
band from `p = −0.892` would be arithmetic performed on a quantity that has no
meaning, and §7.1 forbids the row it would feed regardless.

`St_peak`, `St(10 H)` and `St(20 H)` all rise monotonically from coarse to
fine with *growing* increments — the signature of DIVERGENT. `x_peak/H` goes
up then down, sign-flipping with |ratio| > 1: OSCILLATORY. None of the four is
CONVERGING, so §7.1 gate (2) fires on all four independently of gate (1).

## 5. The gate table

Order of evaluation, §7.1: **(1)** any ladder level NOT CONVERGED → NOT A
RESULT; **(2)** triple not CONVERGING → NOT A RESULT; **(3)** no primary file →
BLOCKED; **(4)** primary held → PASS or GATE FAIL.

| row | quantity | fine value | triple state | iterative conv. `c`/`m`/`f` | **verdict** | comparator's `why` |
| --- | --- | ---: | --- | --- | --- | --- |
| **G1** | `St_peak` | 0.00354497 | DIVERGENT (`p` −0.892) | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** | level c,m,f not iteratively converged |
| **G2** | `x_peak/H` | 6.12114 | OSCILLATORY | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** | level c,m,f not iteratively converged |
| **G3** | `St(10 H)` | 0.00312892 | DIVERGENT (`p` −0.516) | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** | level c,m,f not iteratively converged |
| **G4** | `St(20 H)` | 0.00234778 | DIVERGENT (`p` −0.209) | NOT CONV / NOT CONV / NOT CONV | **NOT A RESULT** | level c,m,f not iteratively converged |

Tally recorded in `gate_t3.json`: `PASS 0, GATE FAIL 0, NOT A RESULT 4,
BLOCKED 0, PENDING 0, REPORTED 0`. **`0 of 4` graded rows, which §7.2 called
"the honest count", and a rung with no graded row is not a capability.**

### 5.1 Why these rows read NOT A RESULT and not BLOCKED

The supervising brief for this analysis expected `BLOCKED` on all four rows,
with the reason "primary reference (Vogel & Eaton 1985, DOI 10.1115/1.3247522)
not on disk; `T3_reference_primary.json` absent". That expectation is what
§7.2's "verdict today" column registered, and it is what the freeze commit
message says. **It is not what the frozen comparator returned, and the
comparator is the authority.** The reason is the *order* in §7.1: the primary's
absence is gate (3), and gates (1) and (2) both fire first. A row cannot be
BLOCKED on a missing reference when it has already failed to produce a value
worth comparing to one.

Both statements are true and both belong in the record:

- **`T3_reference_primary.json` is absent.** Re-confirmed on disk at the top of
  this analysis; `git log --oneline -3` shows `31fd2268` / `6f7d5965` /
  `4cc8c22c`, all T10a and T5/T4 work — no state lane has pulled the primary.
  `primary_present: false`, `primary_sha256: null`. Vogel & Eaton 1985, ASME J.
  Heat Transfer 107(4) 922–929, DOI **10.1115/1.3247522**, remains NOT OBTAINED
  on every path named in §2.
- **Even if it appeared this minute, all four rows would still read NOT A
  RESULT**, because gates (1) and (2) are upstream of it. Obtaining the primary
  is necessary and is *not* sufficient. This is the substantive finding of the
  rung and it inverts the pre-registered expectation of what stands in the way.

`BLOCKED` is therefore the state these rows reach *after* the ladder converges
and the triples come back CONVERGING, and it is not reached today.

### 5.2 A guard fired on the fine level

The heat-balance GUARD (§6) is reported on every case and tallied in nothing.

| case | closure residual | imbalance % | vs 0.5 % |
| --- | ---: | ---: | --- |
| R_c | 7.387e-04 | 0.0739 | within |
| R_m | 8.996e-04 | 0.0900 | within |
| **R_f** | **8.234e-02** | **8.234** | **OUTSIDE** |
| P_m | 3.824e-04 | 0.0382 | within |
| **C_lam_m** | **9.932e-01** | **99.32** | **OUTSIDE** |
| W_m | −8.225e-05 | 0.00823 | within |
| D_m | 2.124e-04 | 0.0212 | within |
| O_m | 3.458e-03 | 0.3458 | within |

`R_f` — the level whose value would be graded — closes its energy budget to
8.2 %, against a governed 0.5 %, while the two coarser levels on the same
geometry close to better than 0.1 %. Under Charter §2c a GUARD withdraws the
run and never the hypothesis, and this one is consistent with §3's diagnosis:
`R_f` is the SST level furthest from a steady state, and an unsteady field does
not close a steady energy balance. It is a **third** independent reason the
fine value cannot be carried into a graded row today. `C_lam_m`'s 99.3 % is
expected of a laminar case that never converged and is not a finding.

Mass closes on every case (`R_f` mass imbalance `−1.5e-14` relative).

## 6. The secondary comparison: REPORT ONLY

Smirnov, Smirnovsky, Schur, Zaitsev and Smirnov (2016), *J. Phys.: Conf. Ser.*
**745**, 032016, DOI 10.1088/1742-6596/745/3/032016, CC-BY 3.0, PDF sha256
`020a09f1…5b1237`, title and authors verified from the printed pages 1–2
(L-144). The held artifact is the digitisation of its Figure 9, frozen before
any case existed.

**This comparison arms no band and returns no verdict.** It is not a
reference; it is a digitisation of a figure in a third-party paper that
re-plots the primary's symbols, it states no experimental uncertainty, and
§2.1 is explicit that "every comparison against it is REPORTED, never graded".
The increments below are the digitiser's own symbol-radius increments, not
anyone's measurement uncertainty. **A reader who sees a T3 number "against
experiment" is seeing a secondary digitisation.**

| row | quantity | fine value | secondary | digitisation increment | deviation |
| --- | --- | ---: | ---: | ---: | ---: |
| G1 | `St_peak` | 0.00354497 | 0.00358215 | ± 8.921e-05 | **−1.04 %** |
| G2 | `x_peak/H` | 6.12114 | 6.86552 | ± 0.1826 | **−10.84 %** (−0.744 H) |
| G3 | `St(10 H)` | 0.00312892 | 0.00300102 | ± 8.921e-05 | **+4.26 %** |
| G4 | `St(20 H)` | 0.00234778 | 0.00227002 | ± 8.921e-05 | **+3.43 %** |
| M1 | `x_R/H` | 6.98332 | 6.65897 | ± 0.2314 | **+4.87 %** |

The peak magnitude sits 1 % from the digitised peak and the two downstream
stations within 4.3 %; the peak *location* is 0.74 H upstream of the digitised
one. None of that grades anything, and none of it changes a verdict above.

## 7. The reported rows

| row | kind | result |
| --- | --- | --- |
| **M1** `x_R/H` | lever | **REPORTED** 6.98332 on the fine level, 1 crossing; triple 7.01279 → 7.01011 → 6.98332, DIVERGENT (`p` −4.903). The momentum lever: a momentum error is mesh or solver, a Stanton error with correct momentum is the thermal closure |
| **DP** `Pr_t` 1.0 vs 0.85 | discrimination | **REPORTED — SEPARATED (PROVISIONAL**, against the registered 3 % floor). `St_peak` 0.003247 (`P_m`) vs 0.003438 (`R_m`), separation **5.55 %**; at `10 H`, **5.48 %**. Both bands `null` — no band exists to test against |
| **DC** laminar baseline | Charter §2c | **REPORTED — NOT CONVERGED, UNMEASURED (not satisfied)**, exactly as §5 and §7.2 registered for this outcome. `St_peak` 0.006795 vs 0.003438, +97.6 %, read at the last checkpoint |
| **DW** wall functions vs resolved | comparison | **REPORTED.** `St_peak` **−19.36 %**, `St(10 H)` −20.03 %, `St(20 H)` −9.26 %. Achieved `y+` 0.152 / 15.41 / 22.58 (min/mean/max) and **100.0 % of heated-wall faces below `y+` 30** — the wall function is outside its own validity on every face it is applied to |
| **DD** thin inlet layer | comparison | **REPORTED — registered direction MET.** `delta_99/H` 0.1195 (`D_m`) vs 0.6710 (`R_m`); `St_peak` 0.003977 vs 0.003438, **+15.68 %**, and `x_R` 6.543 vs 7.010 (shorter) |
| **DO** outlet independence | guard for G4 | **REPORTED — criterion MET.** `St(20 H)` differs by −1.369e-06 relative and `x_R` by −3.35e-05 H against the 1 % criterion. G4 is not further disqualified by the outlet |
| **HB** heat balance | GUARD | **REPORTED**, §5.2. Two cases outside 0.5 %: `R_f` at 8.234 %, `C_lam_m` at 99.32 % |

## 8. The registered predictions, scored

§8's predictions were written before any solve, to be wrong in a recorded
direction.

| # | prediction | outcome | result |
| --- | --- | --- | --- |
| 1 | `x_R/H` fine between 6.0 and 7.5 | 6.983 | **HELD** |
| 2 | `St_peak` fine within ±15 % of the digitised peak; `x_peak/H` within ±1.0 of its location | −1.04 %; −0.744 H | **HELD**, both |
| 3 | `Pr_t` 0.85→1.0 moves `St_peak` and `St(10 H)` by 8–12 % | 5.55 % and 5.48 % | **MISSED** — real, above the 3 % floor, but roughly half the T1b shift |
| 4 | laminar `St_peak` ≥ 25 % **below** SST, **or** does not converge | +97.6 % **above**, and did not converge | **direction wrong; escape clause held.** Row UNMEASURED, so G1 is not additionally disqualified by it |
| 5 | wall-function arm differs from resolved medium by > 5 % at `St_peak`; substantial face fraction below `y+` 30 | −19.36 %; 100.0 % of faces | **HELD**, both, and the fraction is total rather than substantial |
| 6 | `D_m` has higher `St_peak` than `R_m` and a shorter `x_R` | +15.68 %; 6.543 vs 7.010 | **HELD**, both |
| 7 | `delta_99/H` at −3.8 H between 0.95 and 1.20; `Re_H` within ±5 % of 28 000 | **0.668–0.671** on the ladder; `Re_H` 27 702–27 705 (−1.06 %) | **SPLIT — `delta_99` MISSED low by ~37 %**; `Re_H` HELD on the ladder. `D_m` reads `Re_H` 26 510 (−5.32 %), marginally outside, by design of the thin-layer arm |
| 8 | at least one of G1–G4 comes back not CONVERGING | **all four**, plus every level NOT CONVERGED | **HELD, emphatically** |

Prediction 7's `delta_99` miss is the one to carry forward: the design targeted
the secondary's stated `1.07 H` layer at `−3.8 H` and achieved `0.67 H`, a
different inlet condition from the facility's. Since prediction 6 establishes
that this rung's `St_peak` is *sensitive* to the inlet layer thickness at
+15.7 % for a 5.6 × thinning, a 37 % shortfall in `delta_99` is not a detail —
it is a registered discrepancy in the setup that any future graded comparison
must answer for.

## 9. Cost

`nProcs = 1` on every case, serial; the box was shared with the DAFoam and
closure teams throughout, so wall includes contention and is an upper bound on
solver time. Core-hours = wall seconds / 3600 (`nProcs` 1). **0.0513 USD per
core-hour.**

| case | cells | predicted core-s | measured wall, s | core-h | USD | measured / predicted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R_c | 36 000 | 1 800 | 3 269 | 0.9081 | 0.0466 | 1.82 × |
| R_m | 92 160 | 4 608 | 15 901 | 4.4169 | 0.2266 | 3.45 × |
| R_f | 235 520 | 11 776 | 60 974 | 16.9372 | 0.8689 | **5.18 ×** |
| P_m | 92 160 | 4 608 | 15 849 | 4.4025 | 0.2258 | 3.44 × |
| C_lam_m | 92 160 | 4 608 | 10 314 | 2.8650 | 0.1470 | 2.24 × |
| W_m | 28 160 | 1 408 | 1 490 | 0.4139 | 0.0212 | 1.06 × |
| D_m | 79 360 | 3 968 | 10 580 | 2.9389 | 0.1508 | 2.67 × |
| O_m | 128 000 | 6 400 | 26 780 | 7.4389 | 0.3816 | 4.18 × |
| **total** | | **39 176** | **145 157** | **40.3214** | **2.0685** | **3.71 ×** |

**145 157 core-seconds × 1 core = 40.3214 core-hours × 0.0513 USD/core-h =
2.0685 USD.** Against the §10 prediction of 10.88 core-hours and 0.56 USD, and
against the pre-authorised 25 USD ceiling (487 core-hours): this rung spent
**8.3 % of the ceiling** and **3.71 ×** its own prediction.

**Where the prediction went wrong.** §10 planned at `4.0e5` cell-iterations per
core-second and recorded a pre-freeze smoke measurement of `1.94e5` on `R_c`.
Measured here:

| case | cells | cell-it/core-s |
| --- | ---: | ---: |
| W_m | 28 160 | 3.78e5 |
| R_c | 36 000 | 2.20e5 |
| C_lam_m | 92 160 | 1.79e5 |
| D_m | 79 360 | 1.50e5 |
| R_m | 92 160 | 1.16e5 |
| P_m | 92 160 | 1.16e5 |
| O_m | 128 000 | 9.56e4 |
| R_f | 235 520 | **7.73e4** |

Throughput falls by **4.9 ×** from the smallest case to the largest — far more
than the "about 19 % slower above 100 k cells" the plan allowed for. The
correct planning model for a 2D turbulent case on this box is not a constant
rate but one that degrades steeply with cell count, most likely on cache
residency. The wall prediction was also beaten in the other direction: `R_f`
was expected to take 3.3 h uncontended or ~6.7 h at the smoke-test rate, and
took **16.9 h**. This is a cost-science finding and it is cheap at 2 USD.

Comparator, marker tool and this report: zero solver compute.

## 10. What unblocks this rung

Two things are needed, in this order. **Obtaining the primary is the second of
them, not the first.**

### 10.1 First: an iteratively converged ladder

Nothing in §7.1 can be reached while `R_c`, `R_m` and `R_f` are NOT CONVERGED,
and no triple can be read as a mesh statement while the fine level is 38 ×
further from steady than the medium. §5 registered the remedy and its
discipline: **extension from `latestTime`** under the T1b §6 disclosure rule —
new log, new `STATUS`, first extension `Time` exactly `endTime + 1`, marker
re-judged across both segments — with **the decision taken on the convergence
state alone and never with a `St` in view**. §11 registered the alternative
outcome honestly: a steady RANS of a flapping shear layer may be in a limit
cycle that no extension resolves, in which case the rung says so rather than
averaging. At 2.07 USD for the whole rung, an extension of every case to 60 000
iterations is still under 2 USD (§10 of the pre-registration says the same).
This report takes no such decision and runs nothing.

Should the ladder converge and the triples still come back not CONVERGING,
§8's prediction 8 already names the response: **a fourth level, proposed and
not run.**

### 10.2 Second: the primary reference file

`verification/runs/T-family/T3_runs/T3_reference_primary.json`, absent today.
Its schema is fixed by §7.3 and **nothing in `analyse_t3.py` changes when it
appears**:

```json
{"provenance": {"citation": "...", "page_or_table": "...", "sha256": "...",
                "title_verified_page1": true, "digitised": false},
 "rows": {"G1": {"value": 0.0, "uncertainty": 0.0, "units": "St"},
          "G2": {"value": 0.0, "uncertainty": 0.0, "units": "x/H"},
          "G3": {"value": 0.0, "uncertainty": 0.0, "units": "St"},
          "G4": {"value": 0.0, "uncertainty": 0.0, "units": "St"}}}
```

`uncertainty` is **the authors' stated figure**, in the units of the row — an
experiment's band is its stated uncertainty, and it is the only band this rung
may arm. If the numbers had to be digitised from the primary's figure,
`digitised` is `true` and the comparator adds the digitisation increment in
quadrature. **The person who fills this file reads it from the printed page
(L-144) and writes the page number.**

The source is Vogel & Eaton 1985, ASME J. Heat Transfer **107**(4) 922–929,
DOI **10.1115/1.3247522**; the companion Stanford Thermosciences Report MD-44
(August 1984) would serve equally. §2 records every open path checked and
failed, and the three acquisition routes with their prices — an ASME
pay-per-view purchase, a Stanford scan-on-demand or ILL of MD-44, or an
institutional subscription held by a lab member. **Each is a spend or an access
decision outside the compute authorisation and goes to Sanaa as a decision, not
an assumption.**

### 10.3 Then: re-run the comparator

Once both conditions hold, `python3 analyse_t3.py` run in place is the only
remaining step. It reads the primary if it is there, arms each row's band from
the stated uncertainty, and returns PASS or GATE FAIL per row. It needs no
edit, no flag and no argument — the comparator has been frozen since
2026-08-21 18:02:09 Z and stays frozen.

## 11. What this rung cannot see

Everything in §11 of the pre-registration still stands — agreement with the
experiment, which `Re_H` and `delta/H` the digitised symbols represent,
three-dimensionality, unsteadiness, any closure other than `kOmegaSST`, any
`Pr_t` other than 0.85 and 1.0 — and this attempt adds three:

- **A mesh-converged `St` at any station.** Not because the triples are
  DIVERGENT alone, but because the levels feeding them are not iteratively
  converged, so the triples are not yet measuring the mesh.
- **A trustworthy fine-level value of anything.** `R_f` fails the 0.5 % heat
  balance at 8.2 %; the field it would be read from does not conserve energy.
- **Whether the inlet condition matches the facility's.** `delta_99/H` came in
  at 0.67 against a targeted 1.07, and prediction 6 shows this rung's `St_peak`
  is sensitive to exactly that.

## 12. What changed on disk

Three files, all inside the T3 tree or beside the pre-registration; no frozen
file was touched and nothing was committed.

| path | change |
| --- | --- |
| `verification/runs/T-family/T3_runs/DONE.R_f` | **created** by `mark_done_t3.py`, 16 bytes, "strict rule met" |
| `verification/runs/T-family/T3_runs/gate_t3.json` | **created** by `analyse_t3.py`, sha256 `5e23f84e…780c04` |
| `docs/campaigns/T-family/T3_RESULTS.md` | **created** — this file |

Plus 40 comparator by-products, disclosed here because they were not
anticipated: `analyse_t3.py` invokes OpenFOAM's `writeCellCentres` on each case
to get cell centroids, which wrote `20000/{C,Cx,Cy,Cz}` and `log.writeCellCentres`
into all eight case directories. They are derived geometry, they are recomputed
on every comparator run, they overwrite the copies the 2026-08-21 run left, and
they touch no solved field: `0/`, `18000/` and the solved contents of `20000/`
are untouched, and `mark_done_t3.py` re-run afterwards still reports 8/8.

`analyse_t3.py`, `build_t3.py`, `T3_PREREGISTRATION.md`, `T3_CONTRACT.md` and
`mark_done_t3.py` are byte-identical to `628ef452`. Running the marker tool
rewrote no existing marker (it never retracts and skips markers that exist), so
the seven pre-existing `DONE.*` mtimes are untouched and the comparator-freeze
margin computed from them is unaffected.

## 13. Rung verdict

**T3 verdict: NOT A RESULT — 4 of 4 graded rows, on gates (1) and (2) of
§7.1, both of which fire ahead of the missing primary. Every one of the eight
cases is NOT CONVERGED against the registered `1e-6` criterion (`R_c` by
49 400 ×, `R_f` by 3 700 ×, `R_m` by 138 ×, `W_m` by 1.25 ×); all four graded
triples are DIVERGENT (`St_peak` `p` −0.892, `St(10 H)` −0.516, `St(20 H)`
−0.209) or OSCILLATORY (`x_peak/H`); no GCI exists for any quantity and none
was manufactured; the `R_f` heat-balance GUARD fired at 8.234 % against 0.5 %.
`T3_reference_primary.json` is absent and Vogel & Eaton 1985 (DOI
10.1115/1.3247522) remains NOT OBTAINED — so `BLOCKED (primary reference not
held)` is the state these four rows would reach once the ladder converges, and
it is not the state they are in today; obtaining the primary is necessary and
not sufficient. Planted-zero control PASS (1.234e-03 K planted, read back to
1e-14). Secondary (Smirnov 2016) report-only, arming no band and returning no
verdict: −1.04 % at `St_peak`, −10.84 % at `x_peak/H`, +4.26 % at 10 H, +3.43 %
at 20 H, +4.87 % at `x_R/H`. DP SEPARATED (PROVISIONAL) at 5.55 %; DC
UNMEASURED; DO criterion MET; DW −19.36 % with 100 % of wall-function faces
below `y+` 30; DD +15.68 % in the registered direction. Predictions 1, 2, 5, 6,
8 HELD; 3 MISSED; 4 direction wrong on the held escape clause; 7 split, with
`delta_99/H` 0.67 against a targeted 1.07. 8 of 8 cases complete under the
strict rule; 40.3214 core-hours, 2.0685 USD, 3.71 × the predicted cost and
8.3 % of the authorised ceiling.**
