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

---

## 14. ext1 re-grade (2026-08-24)

**Dated section appended 2026-08-24T16:15:34Z under Charter §2b clause 2 and CLAUDE.md
rule 6. This is amendment 1 of this document. Lines whose number changed above
this section: 0.** *On the version bump rule 6 asks for: this document has never
carried a version line at its head, and none is retro-fitted here — inventing a
"v1.0 → v1.1" series after the fact would assert a provenance the file does not
have. The dated-amendment number and the zero-lines-moved assertion carry the
same guarantee and are checkable against the file.* It alters no gate, no
threshold, no cap and no label. Sections 1–13
above are the attempt-1 record at `endTime 20000` and stand unedited; this
section reports the ext1 extension registered in `T3_EXT1_AMENDMENT.md` (D452)
and re-graded by the same frozen comparator. **The rung verdict does not
change: `NOT A RESULT` on all four graded rows, 0 of 4 graded.** What changed is
*which gate* fires and *what the ladder now looks like*, and both are recorded
below because a verdict that stays the same for a different reason is not the
same verdict.

### 14.1 Completion audit: 8 of 8 under the two-segment rule

Every case satisfies the strict completion rule as extended by
`mark_done_t3_ext1.py`'s two-segment rule (`T3_EXT1_AMENDMENT.md` §8), which is
strictly *more* refusing than the original: it adds both-segment `rc=0`, both-segment
`End`, the summed `ExecutionTime` identity, the `first Time = 20001` continuity
test, and a second age-guard datum (`STATUS.<case>`) on top of `0/T`.

`R_f`, the critical path, clause by clause — read from disk, not from the marker:

| clause | `R_f` |
| --- | --- |
| `STATUS.R_f` `rc=0` **and** `STATUS_EXT1.R_f` `rc=0` | `0` and `0` |
| `End` in `log.solve` **and** in `log.solve.ext1` | present / present |
| last time dir == `system/controlDict` `endTime` | `78000` == `78000` |
| `NEEDED` + `NEEDED_TURBULENT` at that time | `T U p_rgh alphat phi` + `nut k omega`, all present |
| `^ExecutionTime` count, segment 1 (unaltered) | **20 000** |
| `^ExecutionTime` count, ext1 | **58 000**; sum **78 000** == `endTime` |
| first `Time =` of `log.solve.ext1` | **`20001`** — exactly one past segment 1 |
| age guard vs the case's own `0/T` | fields `2026-08-24T14:53:16–17Z` ≫ `0/T` `2026-08-21T18:03:22Z` |
| age guard vs `STATUS.R_f` | fields ≫ `STATUS.R_f` `2026-08-22T10:59:39Z` |

The same eight clauses hold on all eight cases: segment-1 `ExecutionTime` count
is **20 000** on every case, the first ext1 `Time` is **20001** on every case,
the summed count equals `endTime` on every case, each `log.solve.ext1` carries
exactly one `End`, and each last time directory equals its `endTime`.

| case | `STATUS_EXT1.<case>` | ext1 `ExecutionTime` lines | sum | last time dir | finished (UTC) |
| --- | --- | ---: | ---: | ---: | --- |
| `R_c` | `rc=0 wall=13782 endTime=80000` | 60 000 | 80 000 | 80 000 | 2026-08-22T21:41:26Z |
| `R_m` | `rc=0 wall=14884 endTime=36000` | 16 000 | 36 000 | 36 000 | 2026-08-22T21:59:48Z |
| **`R_f`** | `rc=0 wall=162094 endTime=78000` | 58 000 | 78 000 | 78 000 | **2026-08-24T14:53:19Z** |
| `P_m` | `rc=0 wall=15095 endTime=36000` | 16 000 | 36 000 | 36 000 | 2026-08-22T22:03:20Z |
| `C_lam_m` | `rc=0 wall=33909 endTime=80000` | 60 000 | 80 000 | 80 000 | 2026-08-23T03:16:55Z |
| `W_m` | `rc=0 wall=7230 endTime=80000` | 60 000 | 80 000 | 80 000 | 2026-08-22T19:52:16Z |
| `D_m` | `rc=0 wall=6380 endTime=28000` | 8 000 | 28 000 | 28 000 | 2026-08-22T19:38:07Z |
| `O_m` | `rc=0 wall=34509 endTime=46000` | 26 000 | 46 000 | 46 000 | 2026-08-23T03:26:56Z |

**An unregistered partial-pool control, reported as inferred and not as
measured.** The live marker log's `DONE markers before:` line lists **seven**
markers, `R_f`'s absent. The inference is that an earlier invocation, run after
the other seven had finished but while `R_f` still iterated, marked 7 of 8 and
**refused `R_f`** — P4's mechanism exercised on the real pool at partial
completion rather than only on forged directories in the §8.1 selftest. **This is
an inference from one line of a log, not a measurement**: that earlier
invocation's own output was not kept, and no attempt is made here to date it.
What *is* measured, and is what the inference would predict, is that the
comparator never graded a partial pool — see §14.2.

### 14.2 The comparator run, and who ran it

**Instrument integrity, verified independently by two lanes.** All six
instruments are byte-identical to their `HEAD` blobs (`git diff HEAD` empty on
each), and the four that `T3_EXT1_AMENDMENT.md` §11 tabulates match those
recorded hashes:

| instrument | sha256 | §11 |
| --- | --- | --- |
| `analyse_t3.py` | `f41c544d…498741` | matches |
| `mark_done_t3.py` | `ba466e23…fc2d60d` | matches |
| `build_t3.py` | `7527a546…36f739` | matches |
| `run_one_t3.sh` | `7cd0df46…4879ff` | matches |
| `mark_done_t3_ext1.py` | `387a2c9e…9a11a0c` | new in §8 |
| `run_one_t3_ext1.sh` | `845a4059…8081bc` | new in §9 |

`gate_t3.json`, sha256 `8e766cd5dbc59cff336f9756a90967d92f34e981094f3b8b427089eeb34ba573`,
mtime `2026-08-24T15:58:44Z`. `analyse_t3.py` exit code **0**. The comparator
sha256 stored *inside* the graded artifact is `f41c544d…498741`, i.e. the frozen
one.

**Planted-zero control: FIRED and PASSED.** `PLANT = 1.234e-03 K` planted into a
copy of `R_m`'s `34000/T` and read back from disk: `read_back_delta`
`1.2340000000108375e-03`, `reader_max_change` `1.2340000000108375e-03`,
`passed: true`, and the reader's verdict on the perturbed pair flips to
`NOT_CONVERGED`. The reader is therefore demonstrably able to see a non-zero, and
the `CONVERGED` results in §14.3 are evidence rather than silence. **There is one
control, not two**: the frozen comparator plants once, on `R_m`
(`analyse_t3.py:307`), and the refusal at `:801` is armed on that single control.

**Provenance of the run, disclosed because it is not this lane's.** The marker
(`15:57:59Z`) and the comparator (`15:58:26Z`, finishing `15:58:44Z`) were run by
a **lane of a parallel session**, before the chief redirected T3 ext1 to this
session at `16:00Z`; that lane was stopped at `16:03Z` and wrote no results
record. Its two tool logs are committed beside this record as
`T3_runs/log.mark_done_ext1.20260824T155759Z.txt` and
`T3_runs/log.analyse_t3.ext1.20260824T155826Z.txt`, each carrying its own `date -u`,
`HEAD` and instrument hashes.

**Stated exactly: what this lane did and did not run.** This lane **did not run**
`analyse_t3.py` and **did not run** the live `mark_done_t3_ext1.py`. Re-running the
comparator would have rewritten the graded artifact for no gain, the instrument
being frozen and hash-verified. This lane **did** independently re-hash all six
instruments against `HEAD`; **did** re-derive every number in §14.3–§14.5 and
§14.7 from `gate_t3.json` and from the case directories on disk, not from the
parallel lane's log; **did** verify `R_f`'s completion clause by clause from disk
(§14.1); and **did** run `python3 mark_done_t3_ext1.py --dry-run` once at
`2026-08-24T16:09:32Z` as its own confirmation, which reported
`DRY RUN -- nothing written or removed: 8/8 cases meet the strict completion rule
(8 with an ext1 extension)`, `rc=0`, all eight `PASS [ext1 included]`, removing
nothing and leaving `gate_t3.json` byte-identical.

**The comparator never graded a partial pool.** The parallel lane's log records
the **pre-run** `gate_t3.json` as sha256 `5e23f84e…780c04` with mtime
`2026-08-22 17:33:22Z` — the original pre-launch artifact, committed at
`fd831c11`, untouched across the entire 2-day extension. Nothing graded anything
between the launch and `15:58:44Z`.

*A note on this record's own provenance, for the same reason §13 of the amendment
recorded a hash that moved:* two sessions were dispatched onto this item
independently and both began it; the collision was resolved by the chief at
`16:00Z` in favour of this session. No lesson is filed for it here — the
duplicate-dispatch failure mode is already known practice (claim the item in
`docs/DOCKET.md` before starting) — but it is recorded because two lanes reaching
for one graded artifact is exactly the condition under which a `gate_t3.json`
could have been overwritten mid-read, and it was not.

### 14.3 Iterative convergence after ext1

The registered criterion (`T3_PREREGISTRATION.md` §5): the largest change of any
cell value of `T`, and separately of `U`, between the last two checkpoints, at
most `1e-6` of that field's range.

| case | checkpoints | rel Δ`T` | rel Δ`U` | state |
| --- | --- | ---: | ---: | --- |
| `R_c` | 78000 / 80000 | **4.833e−02** | **1.499e−01** | NOT CONVERGED |
| `R_m` | 34000 / 36000 | 1.535e−08 | 8.754e−09 | **CONVERGED** |
| **`R_f`** | 76000 / 78000 | **9.679e−08** | **7.796e−08** | **CONVERGED** |
| `P_m` | 34000 / 36000 | 3.684e−09 | 8.754e−09 | **CONVERGED** |
| `C_lam_m` | 78000 / 80000 | **7.045e−01** | **1.103e+00** | NOT CONVERGED |
| `W_m` | 78000 / 80000 | **1.409e−06** | **1.252e−06** | NOT CONVERGED |
| `D_m` | 26000 / 28000 | 3.373e−07 | 6.321e−11 | **CONVERGED** |
| `O_m` | 44000 / 46000 | 1.278e−09 | 1.865e−10 | **CONVERGED** |

Five of eight now meet the criterion, against **none** at attempt 1 (§3). The
three that do not are exactly the three the amendment classed STALLED.

### 14.4 The graded rows

Effective refinement ratios from `nCells`: `r21 = 1.5986`, `r32 = 1.6000`;
`Fs = 1.25`.

| row | quantity | triple `c` / `m` / `f` | triple state | `p` | GCI (fine) | verdict |
| --- | --- | --- | --- | ---: | --- | --- |
| G1 | `St_peak` | 0.00336772 / 0.00343791 / 0.00350859 | **DIVERGENT** | −0.0148 | — | **NOT A RESULT** |
| G2 | `x_peak/H` | 6.0895 / 6.13516 / 6.14120 | **CONVERGING** | **+4.304** | **0.0188 %** (RE 6.14027) | **NOT A RESULT** |
| G3 | `St(10 H)` | 0.00298296 / 0.00304705 / 0.00310443 | **STAGNANT** | +0.2317 | — | **NOT A RESULT** |
| G4 | `St(20 H)` | 0.00224934 / 0.00229610 / 0.00233824 | **STAGNANT** | +0.2175 | — | **NOT A RESULT** |
| M1 | `x_R/H` | 7.01291 / 7.01011 / 6.98336 | DIVERGENT | −4.809 | — | REPORTED |

**All four fire at gate (1), not gate (2).** Every graded row carries
`iterative_convergence: {c: NOT_CONVERGED, m: CONVERGED, f: CONVERGED}` and the
reason line `-- level c not iteratively converged`. Under
`T3_PREREGISTRATION.md` §7.1 the order is (1) any ladder level NOT CONVERGED →
`NOT A RESULT`; (2) triple not CONVERGING → `NOT A RESULT`; (3) no primary →
`BLOCKED`. Gate (1) fires, so gate (2) is never reached and gate (3) is never
reached. This is a **change of cause** from attempt 1, where all three levels
were NOT CONVERGED and every triple was DIVERGENT or OSCILLATORY: the medium and
fine levels are now converged and it is the **coarse** level alone that stops the
ladder.

**G2 is CONVERGING and is `NOT A RESULT` anyway, and that is the gate working.**
`x_peak/H` returns a CONVERGING triple with `p = 4.304` and `GCI_fine =
0.0188 %` — T3's first converging triple in either attempt. It is still
`NOT A RESULT`, because gate (1) fires on level `c` before the triple is
consulted. This is the rule the amendment §6 P3 wrote down so it could not be
renegotiated afterwards, and it is the direction the triple gate is allowed to
move a row: **the gate can turn a gradeable row INTO `NOT A RESULT`, never the
reverse.** A CONVERGING triple built on a level that is still moving is not a
mesh statement.

**`p = 4.304` is not a claim of fourth-order accuracy.** The discretisation is
nominally second order, so an observed order of 4.3 exceeds the scheme's formal
order and is read here as **the three values being too close together to resolve
an order at all** — the same reading, in the opposite direction, that makes G3
and G4 STAGNANT at `p ≈ 0.22`. The `x_peak/H` spread across the whole ladder is
`6.0895 → 6.1412`, i.e. **0.85 %**, and the fine-to-medium step is `0.0060`
against the medium-to-coarse `0.0457`. An observed order extracted from
differences that small is not evidence of superconvergence; it is a ratio of two
small numbers. The GCI is reported because the triple is monotone and CONVERGING,
as the rule requires, and it is not offered as a mesh-convergence claim for a
row that does not grade.

**Two things about the ladder changed, and both are findings.** First, the
Stanton ladder is now **monotone in mesh** — `0.003368 < 0.003438 < 0.003509`
— where §3 of this document found the ladder *not ordered by mesh*, with the fine
level further from steady than the medium. That disorder was iterative, not
discretisation: converging the levels removed it. Second, **G3 and G4 moved
DIVERGENT → STAGNANT** (from `p = −0.516` and `−0.209` to `+0.232` and `+0.218`)
and G2 moved OSCILLATORY → CONVERGING. Every triple moved toward order. What
remains is not divergence but **insufficient separation between levels**, which
is a different and more tractable problem, and it is what the registered response
in §14.8 addresses.

### 14.5 Heat-balance GUARD, before and after

Charter §2c GUARD, counted in no tally, against the governed 0.5 %
(`physics_rules.yaml`). "Before" is §5.2 of this document at `endTime 20000`;
"after" is `gate_t3.json` at each case's ext1 `endTime`.

| case | HB % before | HB % after | change | class (`T3_EXT1_AMENDMENT.md` §2) |
| --- | ---: | ---: | ---: | --- |
| **`R_f`** | **8.2340** | **0.0003935** | **↓ 20 900 ×** | DECAYING |
| `O_m` | 0.3458 | 0.0005548 | ↓ 623 × | DECAYING |
| `R_m` | 0.0900 | 0.0007866 | ↓ 114 × | DECAYING |
| `P_m` | 0.0382 | 0.0008762 | ↓ 44 × | DECAYING |
| `D_m` | 0.0212 | 0.0008942 | ↓ 24 × | DECAYING |
| `R_c` | 0.0739 | 0.07345 | −0.6 % | STALLED (limit cycle) |
| `W_m` | 0.0082 | 0.008225 | +0.3 % | STALLED (floor) |
| `C_lam_m` | 99.32 | **99.68 (OUTSIDE)** | +0.4 % | STALLED (limit cycle) |

**The storage-term mechanism argued in `T3_EXT1_AMENDMENT.md` §4 is now
measured, not inferred, and the separation is total.** §4 argued that a case
whose residual is still marching one way carries a net enthalpy storage term that
a steady energy balance cannot account for, and that a case in a stationary limit
cycle carries none. The prediction that follows is that the imbalance of a
DECAYING case must collapse as its residual falls, while a STALLED case's must
not move at all. Over 60 000 further iterations for the stalled cases and
8 000–58 000 for the decaying ones: **the five DECAYING cases fell by 24× to
20 900×; the three STALLED cases moved by less than 1 %.** There is no case in
between, which is the same clean bimodality §2 of the amendment found in the
residual fits. `C_lam_m` remains outside 0.5 % as predicted and is not a finding
either way.

### 14.6 The registered predictions of `T3_EXT1_AMENDMENT.md` §6, scored

**P1 — which cases reach `1e-6`. HELD, 8 of 8, no exceptions.** The five
DECAYING cases reach the criterion at their registered `endTime`: `R_m`
(1.535e−08), `P_m` (3.684e−09), `D_m` (3.373e−07), `O_m` (1.278e−09) and `R_f`
(9.679e−08, inside by 10 ×). The three STALLED cases do not, even at the 80 000
cap: `R_c` (4.833e−02, 48 000 × off), `C_lam_m` (7.045e−01), `W_m`
(1.409e−06).

**`W_m` is the clause that carried the risk and it held.** It was registered
deliberately as "the prediction most likely to look foolish" — 1.25 × away, the
closest of all eight. After **60 000 further iterations** its `T` relative change
moved from `1.417e−06` to `1.409e−06`: **0.6 %**, still outside. The residual-decay
diagnostic committed beside this record
(`T3_runs/log.residual_decay_diagnostic.v2.20260824T160252Z.txt`) measures its
delivered ext1 `T` slope at **−0.00005 decades per 1 000 iterations, `R² = 0.366`**.
**The "a flat residual is a floor, not a slow decay" reading of §2 is correct**,
and the alternative P1 named — that the field increment decays where the residual
does not — is falsified. That same diagnostic reproduced every published §2 slope,
including **5 of 5** on the tier-A rows that fixed the `endTime`s (e.g. `O_m` `T`
−0.14679 against the published −0.14680), so the extrapolator was not mis-fitted.

*Honest qualification on `R_f`.* It converged, but **faster than the model
claimed**: its delivered ext1 `T` slope is **−0.07180 (`R² = 0.998`)** against the
registered **−0.05266**, i.e. **1.36 × faster**, which is why it landed 10 ×
inside the criterion rather than at it. P1 held for `R_f` with margin the
log-linear model did not predict, and the margin is recorded rather than claimed.

**P2 — the `R_f` heat balance closes below 0.5 %. HELD, emphatically.** Observed
**0.0003935 %**, **1 270 × inside** the threshold. The registered falsification
condition — imbalance still above 0.5 % at 78 000 with the `T` residual at or
below `1e−06` — did not fire. **The question §4 raised is therefore closed by
measurement: the 8.234 % of §5.2 was non-convergence, and the fine level carries
no mesh, `alphat` or heated-patch fault.** That was the one open possibility that
would have invalidated the fine level outright, and it is now excluded.
`C_lam_m` was predicted to remain outside and does (99.68 %); as registered, that
is not a finding either way.

**P3 — do any triples become CONVERGING? SPLIT: the primary clause HELD, the
secondary clause FALSIFIED.**
- Registered primary clause, *"at least one of G1–G4 is still not CONVERGING
  after ext1"* — **HELD**: three of four (G1 DIVERGENT, G3 and G4 STAGNANT).
- Registered secondary clause, *"the most likely outcome is that none of the four
  is"* — **FALSIFIED in a recorded direction**: G2 `x_peak/H` came back
  CONVERGING at `p = 4.304`, `GCI 0.0188 %`.
- The reasoning P3 gave held exactly: `R_c` was STALLED, P1 predicted it would not
  converge, it did not, and all four rows therefore fall at gate (1) before gate
  (2) is reached.
- **The non-renegotiation clause was honoured.** The three still-non-CONVERGING
  triples stay `NOT A RESULT` — not relaxed, not averaged over, not reported with
  a "nearly", not converted to REPORTED because USD 4.10 was spent on them. And
  G2, the one row whose triple now passes, is `NOT A RESULT` too. Spending the
  extension bought the ladder more iterations to be judged on; it bought no change
  to the judgement.

**P4 — the marking tool. HELD**, as scored in `T3_EXT1_AMENDMENT.md` §10.3 at
`2026-08-22T17:53:21Z` while the extensions were in flight: `0/8`, all eight
stale `DONE.<case>` markers flagged and removed, the frozen comparator refusing
with exit 2, `gate_t3.json` untouched. It is **not re-scorable now** — the pool no
longer has the in-flight state P4 describes — and this lane did not re-run
`--dry-run` against a running pool to manufacture one. The inferred 7-of-8
partial-pool refusal in §14.1 is corroborating evidence for the same mechanism,
and is labelled as an inference there.

### 14.7 Cost: estimate versus actual (CLAUDE.md rule 12)

Serial throughout, `nProcs = 1`, so **core-minutes = wall seconds ÷ 60**. Walls
are read from `T3_runs/STATUS_EXT1.<case>`; the `ExecutionTime` column is the last
`^ExecutionTime` of each `log.solve.ext1` and is solver time only.

| case | wall s | **core-min** | ext1 `ExecutionTime` s | ET/wall | §5 predicted core-s | actual/§5 | §10.4 ETA h | actual/§10.4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `R_c` | 13 782 | 229.70 | 11 825.25 | 0.858 | 9 818 | 1.404 × | 3.24 | 1.181 × |
| `R_m` | 14 884 | 248.07 | 13 168.67 | 0.885 | 12 712 | 1.171 × | 4.44 | 0.931 × |
| **`R_f`** | **162 094** | **2 701.57** | 160 062.45 | **0.988** | 176 716 | **0.917 ×** | 68.91 | **0.653 ×** |
| `P_m` | 15 095 | 251.58 | 13 263.77 | 0.879 | 12 712 | 1.187 × | 4.49 | 0.934 × |
| `C_lam_m` | 33 909 | 565.15 | 32 129.92 | 0.948 | 30 892 | 1.098 × | 10.61 | 0.888 × |
| `W_m` | 7 230 | 120.50 | 5 599.45 | 0.775 | 4 470 | 1.617 × | 1.34 | 1.499 × |
| `D_m` | 6 380 | 106.33 | 4 962.07 | 0.778 | 4 233 | 1.507 × | 1.22 | 1.452 × |
| `O_m` | 34 509 | 575.15 | 32 576.64 | 0.944 | 34 812 | 0.991 × | 12.91 | 0.743 × |
| **total** | **287 883** | **4 798.05** | | | 286 364 | **1.005 ×** | 108.3 h | **0.738 ×** |

**Actual ext1 spend: 4 798.05 core-minutes = 79.968 core-hours.** Derived cost
**USD 4.102** at USD 0.0513 per core-hour (c7a.4xlarge, owner-stated
2026-08-21/22) — **derived, not measured**: the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

- Against the **§5 pre-launch prediction** of 79.55 core-h / USD 4.08: **1.005 ×**.
- Against the **§10.4 revised measured-rate figure** of 108.3 core-h / USD 5.56:
  **0.738 ×**.
- **Gross == cleaned == 79.968 core-h.** All eight rows exceed 3 600 wall
  seconds (the smallest, `D_m`, is 6 380 s), but **none is a stall**: the
  3 600-second rule detects a hung or abandoned row, and every one of these
  terminated under OpenFOAM's own hand with `rc=0`, an `End` line, the last time
  equal to `endTime` and the full `ExecutionTime` count. There is nothing to clean
  out.
- **Waste, separately named per `COMPUTE_BUDGET_CHARTER.md` §6: nil, zero
  core-minutes.** No rerun, no crash, no abandoned segment, no discarded field, no
  launcher refusal. Every core-minute spent produced a field that was graded.
- **Stop thresholds were never approached.** The binding stop registered in §5 was
  USD 22.93 of ext1 spend; actual USD 4.102 is **17.9 %** of it. The 10 ×
  threshold (USD 40.80) is **10.1 %**. Neither came within a factor of five.
- **Rung total.** Attempt 1 was 40.324 core-h / USD 2.069 (§9). After ext1:
  **120.29 core-hours = USD 6.171 derived**, **24.7 %** of the pre-authorised
  USD 25 ceiling. §5 predicted "rung after ext1: USD 6.15" → **1.003 ×**.

**Attribution — and the 1.005 × is not a claim of a 0.5 %-accurate model.** Two
opposite errors cancelled, and recording the aggregate alone would be the wrong
lesson.

1. **Short runs over-ran systematically: `W_m` 1.617 ×, `D_m` 1.507 ×, `R_c`
   1.404 ×.** Their `ExecutionTime`/wall ratios are **0.775, 0.778 and 0.858** —
   **14–23 % of their wall was not solver time** (mesh read, field read, first
   write, wrapper). §5's model is `extra iterations × cells ÷ measured rate` with
   **no fixed-cost term**, so it must under-predict short runs, and the shorter
   the run the worse. **This is a misprediction of model form, not of throughput.**
2. **Long runs came in at or under prediction: `R_f` 0.917 ×, `O_m` 0.991 ×.**
   `R_f`'s `ExecutionTime`/wall ratio is **0.988** — fixed cost is 1.25 % of its
   wall and negligible — so its miss is pure throughput, and it ran *faster* than
   §5 assumed because §5's rates came from §9 of this document, measured under
   contention.
3. **Contention eased, and §10.4 measured it at its worst.** §10.4's rates came
   from a five-minute window on 2026-08-22 17:54–17:59Z when 15 of 16 cores were
   committed, and attributed a 1.36 × penalty to cache and memory-bandwidth
   contention. `R_f`'s ETA from that window was **2026-08-25T14:54Z**; it finished
   **2026-08-24T14:53:19Z, 24 h 1 min early**, at 0.653 × the predicted wall. As
   the siblings finished and a closure lane's ~3 cores freed, the contention fell
   away. **§10.4's penalty was real when measured and did not survive two days.**

**Calibration carried forward:** add a fixed startup/IO term to the cost model
(order 1 400–1 900 s per case on these meshes), and do not extrapolate a
five-minute contention window across a multi-day critical path. The row lands in
`docs/COST_CALIBRATION.md`.

**One caveat about the artifact.** `gate_t3.json`'s own `cost` block reports
**segment-1 walls only** — it reads `STATUS.<case>` (e.g. `R_f wall 60974 s`)
because the comparator was frozen before ext1 existed. That is correct frozen
behaviour, not a defect, but **it is not the ext1 cost and must not be cited as
one.** The ext1 figures above come from `STATUS_EXT1.<case>`.

### 14.8 What this leaves

**`R_c` is in a limit cycle at 80 000 iterations, and the rung says so.**
`T3_PREREGISTRATION.md` §11 registered exactly this alternative in advance: *"a
steady RANS of a flapping shear layer may be in a limit cycle that no extension
resolves, in which case the rung says so rather than averaging."* `R_c` was run
to the 80 000 cap precisely to convert the §2 extrapolation into a measurement,
and the measurement is that **60 000 further iterations moved its `T` relative
change from 4.944e−02 to 4.833e−02 — 2.2 % — and its heat balance by 0.6 %.** It
is not converging and it is not going to. **No average is taken and none will
be**; the rung reports the state.

**The four graded rows remain `NOT A RESULT` at gate (1).** They are not BLOCKED:
gate (3), the missing primary, sits downstream of gates (1) and (2) and is still
not reached. The primary, **Vogel & Eaton (1985), DOI 10.1115/1.3247522, remains
NOT OBTAINED**; `T3_reference_primary.json` does not exist and `primary_sha256`
is `null`. Obtaining it stays necessary and is still not sufficient.

**The registered response is a fourth mesh level, proposed and NOT run.**
`T3_EXT1_AMENDMENT.md` §6 P3 registered it before ext1 ran: *"if the levels
converge and the triples remain DIVERGENT or OSCILLATORY, the response is …
a fourth mesh level, proposed and not run."* The condition is met in the form the
prediction anticipated — with the refinement that what remains is STAGNANT rather
than DIVERGENT, i.e. **levels too close to resolve an order**, which a fourth
level addresses directly. Because `R_c` will not converge, the fourth-level triple
is **(`R_m`, `R_f`, `R_ff`)** — the three iteratively converged levels — and not
a re-run of the coarse level.

**A rough cost bound for `R_ff`, with its assumptions on its face. This is an
estimate, not a registration, and it authorises nothing.**

1. `r = 1.6` in 2D → cells × `1.6²` = **× 2.56** → `235 520 × 2.56` ≈
   **603 000 cells**.
2. Throughput degrades with cell count. Measured on the ext1 segment itself:
   `R_m` (92 160 cells) ran at **1.12e5** cell-iterations per core-second and
   `R_f` (235 520 cells) at **8.53e4** — a **2.556 ×** cell increase costing a
   **0.762 ×** rate. Applying the same factor across the same 2.56 × step gives
   `R_ff` ≈ **6.50e4** cell-it/core-s.
3. Iterations **at least 78 000**, `R_f`'s requirement. A finer mesh is not
   expected to converge in fewer, and this is the assumption most likely to be
   optimistic.
4. Serial, `nProcs = 1`, as the whole rung has been.

That gives **≈ 201 core-hours ≈ USD 10.3 derived**, or **≈ 153 core-hours ≈
USD 7.85** if the throughput does not degrade further — call it **150–200
core-hours, USD 8–10 derived**. Serial wall would be **6.4–8.4 days**, which is
the binding practical constraint rather than the money: it is 1.6–2.0 × `R_f`'s
already 45-hour critical path, and a decomposed run is the obvious question. On
the ledger it would consume **over half** the rung's USD 18.83 remaining headroom
under the USD 25 ceiling.

**This bound is where this record stops.** A fourth level needs its own
pre-registration, frozen by commit before any compute, carrying its own gate,
threshold, cap and costed budget, and the decision to build it is not this lane's
and not this record's. **Proposed, not run.**

**The `delta_99/H` inlet-window flag still stands and is unaffected by ext1.**
§8 prediction 7 of this document already records it — `delta_99/H` **0.668–0.671**
on the ladder against a targeted 1.07 and a registered window of 0.95–1.20,
**MISSED low by ~37 %** — and §11 and §13 already carry it forward; the comparator
still reports `delta99_H_R_m = 0.671` after ext1, unchanged. It is restated here
only to make one consequence explicit: under `T3_PREREGISTRATION.md` §4 item 4
the registered tolerance is `[0.80, 1.35]`, and a ladder outside it means the
thermal rows *"carry a flag 'inlet condition outside the registered window' and
are REPORTED, not graded, when the primary arrives."* **This is a second and
independent obstacle to G1–G4, downstream of the triple problem and not solved by
a fourth mesh level**, and it would still be live on the day Vogel & Eaton is
obtained. It is named here so that acquiring the primary is not mistaken for
unblocking the rung.

### 14.9 Rung verdict after ext1

**T3: `NOT A RESULT` 4 of 4 graded rows. 0 of 4 graded.**
`gate_t3.json` tally: **`PASS 0, GATE FAIL 0, NOT A RESULT 4, BLOCKED 0,
PENDING 0, REPORTED 0`.** The verdict of §13 is unchanged in value and changed in
cause: at attempt 1 all three ladder levels were NOT CONVERGED and every triple
was DIVERGENT or OSCILLATORY; after ext1 the medium and fine levels are converged,
one triple is CONVERGING, and the rung is stopped by the coarse level alone.
Cost of the extension: **79.968 core-hours, USD 4.102 derived**; cost of the rung
to date: **120.29 core-hours, USD 6.171 derived**.

### 14.10 Worktree disclosure

Committed with this section: the eight `<case>/system/controlDict` files, each
differing from its previous committed state by exactly one line —
`endTime 20000` → the case's ext1 `endTime`. That edit is
`run_one_t3_ext1.sh`'s, made by the `sed`-with-post-check path documented in
`T3_EXT1_AMENDMENT.md` §9; `startFrom latestTime` and `stopAt endTime` are
unchanged from their committed values. `system/controlDict.pre_ext1` snapshots
exist beside each and are untracked, as time directories and solver logs are
untracked throughout this run tree.

**Left as found, and not attributed:** seven `<case>/log.checkMesh` files
(`R_c`, `R_m`, `P_m`, `C_lam_m`, `W_m`, `D_m`, `O_m` — every case except `R_f`)
differ from their committed state. The diff is a re-run of `checkMesh` stamped
**`Aug 21 2026 21:27:25`** with a different PID, reading the mesh at `Time = 0`
instead of falling back to `constant` with a `FOAM Warning`. **It pre-dates the
ext1 launch by twenty hours and is not this extension's work.** It was inspected
and **not reverted** (CLAUDE.md rule 10: an unexpected change is inspected, never
reverted), and it is **not committed here** because it does not belong to this
item. Whose it is has not been established and no guess is recorded.

