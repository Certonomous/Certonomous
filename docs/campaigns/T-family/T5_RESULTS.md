# T5 results — PARTIAL, 2026-08-26T21:17Z: `T5_CUBE_c` and `H_c` DONE; the ladder is still running; no row graded

**Rung verdict: `PENDING`** — `verification/queue/heat-transfer/T5_CUBE_m_v2.json` … (M, P_m, L_m, F queued; `S_m` not enqueued). The frozen comparator wrote no verdict, verbatim (rc 0, `T5_runs/log.analyse_t5.20260826T211657Z.txt`):

```
T5_CUBE_c: done=True -- all clauses hold
T5_CUBE_m: done=False -- no STATUS file: nothing ran, or the launcher died before writing one
T5_CUBE_f: done=False -- no STATUS file: nothing ran, or the launcher died before writing one

No case has run: no rows are graded and no verdict is written.
```

No V, G or P row was printed, and the planted-zero control was not reached — the comparator stops before the plant when the triple is incomplete. Nothing is quoted here as a graded value. (The comparator's closing sentence "No case has run" is its fixed wording for an incomplete ladder; `T5_CUBE_c` has run, as its own first line says.)

Pre-registration `docs/campaigns/T-family/T5_PREREGISTRATION.md` (v1.7; AMENDMENTS 1–8; graded launches under AMENDMENT 6(b)/8(d), `run_one_t5.sh --no-detach` via the queue runner). Run tree `verification/runs/T-family/T5_runs/`. Written by a lab lane on the heat-transfer supervisor's order `[lab-attributed]`.

## 1. Frozen instruments, hashed before use

| instrument | freeze | `git hash-object` on disk | match |
|---|---|---|---|
| `T5_runs/analyse_t5.py` | blob `9c2c1d44` at `503a9a13` (supervisor's row; §16.9 sha256 `17703b78dad5`) | `9c2c1d44` | SAME |
| `T5_runs/mark_done_t5.py` | blob `a74ce20d` at `503a9a13` | `a74ce20d` | SAME |

`mark_done_t5.py --selftest`: 5 arms, 0 FAILED. `analyse_t5.py --selftest`: 16 arms, 0 FAILED; the one-way gate refusal fires under `-O`.

## 2. Completion — the strict rule, two of six graded cases

| case | wall s | ExecutionTime s | `Time =` lines / last | End | core-min | POINT (§11.1 Model B, AMENDMENT 2) | ratio | timeout s |
|---|---:|---:|---|---|---:|---:|---:|---:|
| T5_CUBE_c | 965 | 929.68 | 5000 / 5000 == endTime | yes | 16.083 | 45.6 | 0.353 | 8 208 |
| H_c | 994 | 958.66 | 5000 / 5000 | yes | 16.567 | 45.6 | 0.363 | 8 208 |

`mark_done_t5.py --root T5_runs T5_CUBE_c`, `H_c`: each `DONE` (rc 0); marker: `DONE T5_CUBE_c under the strict rule (rc=0, End, endTime, fields, age guard) at 2026-08-26T21:16:56Z`. In-wrapper `STATUS.T5_CUBE_c` / `STATUS.H_c`: `rc=0 … capped=0 checkMesh_rc=0 note=clean`, ranks 1.

## 3. FINDING — the `H_c` control is blind by construction (a registration defect, stated, not amended)

**What the pre-registration says `H_c` tests** (§5.6, verbatim): *"`H_c` runs the coarse level with `Gauss linear` on the solid laplacian, everything else identical, and the difference in the `h` and `T_sur` rows is REPORTED. … If `H_c` moves a graded row by more than its band, the scheme choice becomes a named uncertainty of this rung rather than a settled input"*; §16.5 (INTERPRETATION 12, ADOPTED): *"the `H_c` interface scheme is TESTED, not carried … Registered as an `H_c` twin at $0.04 derived — the best value in the rung: $0.04 to test rather than assume."*

**What was measured.** The only difference between the two cases' inputs is `system/epoxy/fvSchemes` lines 16–17: `laplacian(alpha,e|h) Gauss harmonic corrected` (T5_CUBE_c) vs `Gauss linear corrected` (H_c); `diff -rq` of `system/` shows no other file differing. At `5000/` the fields are **byte-identical** (md5, first 12 hex): `air/T` `c2cac072781e` = `c2cac072781e`; `air/U` `9981db36ef36` = `9981db36ef36`; `epoxy/T` `0b03589276e9` = `0b03589276e9`; `air/p_rgh` `b9dcf6142730` = `b9dcf6142730`. The supervisor's own measurement of `air/T` (md5 `c2cac072…`) is reproduced and extended to `epoxy/T` and `air/U`.

**Why, and what it means.** The edited scheme is the solid region's laplacian interpolation of `alpha` (thermal diffusivity). The epoxy is a single material with uniform `alpha`; the harmonic and linear interpolations of a uniform field are the same number at every face, so the solver assembles the identical matrix, and the identical iteration history follows to the last bit. The scheme that §5.6 meant to test — the interface treatment under a 9:1 conductivity jump — lives in the coupled boundary condition and in the **fluid**-side `alphaEff` laplacian, neither of which `H_c` varies. **The control as registered cannot fire, whatever the answer; its result is not a PASS and not evidence that the scheme choice is settled.** Under `CLAUDE.md` rule 2 nothing is amended post-compute: the defect is recorded here, and any re-designed control is a new registration, not a rewrite of §5.6/§16.5. The 16.567 core-min bought a measurement of the control's blindness, which is named as such and not netted off.

## 4. Cost so far — rule 12

- Predicted (AMENDMENT 2 table, Model B): 45.6 core-min each; $0.0390 derived each.
- Measured: 16.083 + 16.567 = **32.650 core-min** (wall 965 + 994 s × 1 rank ÷ 60), gross = cleaned (no row over 3 600 s); contention present, not limiting: ExecutionTime/ClockTime 96.3 % / 96.4 % (box at 14–16 of 16 cores). Ratios **0.353 / 0.363**: misprediction of the per-cell-iteration rate on a 5.4e4-cell conjugate case (Model B carried T9a-D's rate). **$0.0279 DERIVED, NOT MEASURED** at $0.0513/core-h. Waste 0.000 core-min on these two cases; the 17:41Z `T5_C` crash (0 core-min, `crash_1741Z/`) is AMENDMENT 8's record. Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit; the rung's full row follows at completion.

## 5. What remains

`T5_CUBE_m`, `P_m`, `L_m`, `T5_CUBE_f` are queued (`_v2` entries); `S_m` refuses without `M`'s surface T. When all markers exist: `analyse_t5.py --root T5_runs` (P rows BLOCKED under §7.5(3) until the reference is on disk and digitised; V/G rows gradeable), then this file is rewritten with every row.
