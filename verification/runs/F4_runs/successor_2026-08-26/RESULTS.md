CERTONOMOUS MORNING REPORT
Date:       2026-08-26
Assembled:  2026-08-26T16:18Z
Sections:   6 of 6
Missing:    none

# F4-S shock-locus successor — GRADED

**Campaign:** F4-S (nine `rhoCentralFoam` cases, cyl × M ∈ {6.0, 7.0, 8.0} × {coarse 1000, medium 4000, fine 16000 cells}, serial, np = 1). **Team:** cfd, lab-lane under cfd-supervisor.
**Pre-registration:** `verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md`, frozen at **`d98868fb3c4750c3d7ec2873d1bddf98de2aca4a`** (blob `5a863176b0544dd465a4c73c7b6278c860551713`).
**Comparator:** `grade_f4s.py`, disk blob **`9585c90606aa7e60b985ed5d7c6e115e020667b4`** == `git rev-parse d98868fb:<path>`; `--selftest` rc 0; `python3 -O --selftest` rc 2 (the registered entry refusal). **Launcher:** `launch_f4s.py`, disk blob **`ea49d2c7709598f8b3892d25ea5310c75cc669a4`** == committed. Freeze check done by this lane before grading; all three EQUAL.
**Status:** `STATUS.F4S` = `rc=0 end=2026-08-26T16:13:30Z`; launcher fired 15:57Z; `CAP_HALT.json` does NOT exist (neither in the run root nor under `runs/`).

## 1. SPEND

- **Predicted (frozen, §9.2):** 26.30 core-min, np = 1. **Hard cap (§9.3):** 36.0 core-min on wall × ranks ÷ 60, per-case guard 1200 s.
- **Actual gross, MEASURED:** **16.1755 core-min** — `runs/RUN_LEDGER.json` `running_total_core_min = 16.175540618101756`, the sum over nine cases of `wall_s_total × ranks ÷ 60` (blockMesh + checkMesh + solver + sample + surfsample), `ranks = 1` throughout, decompose NOT invoked. Per case (core-min): M6.0 0.1375 / 0.5121 / 3.8691; M7.0 0.1260 / 0.6286 / 4.6588; M8.0 0.1497 / 0.6902 / 5.4035.
- **Solver-only cross-check from the logs' own `ClockTime`** (NOT `ExecutionTime`): 5 + 29 + 230 + 6 + 37 + 278 + 7 + 40 + 322 = **954 s = 15.900 core-min**; the 0.2755 core-min remainder is mesh, checkMesh and sampling clocks, which this launcher captured separately as §9.1 required. `ClockTime`/`ExecutionTime` ≈ 1.00 at every level (e.g. M8.0 fine 322 / 319.14).
- **Cleaned = gross = 16.1755.** No case wall exceeds 1200 s (max 324.2 s, M8.0 fine); nothing near the 3600-s stall rule. **Waste: 0.000 core-min**, named separately — nothing stalled, killed or re-run; no cap crossed (44.9 % of 36.0).
- **Ratio actual / predicted = 16.1755 / 26.30 = 0.615.**
- **Dollars: $0.01383 DERIVED, NOT MEASURED** at $0.0513/core-h (c7a.4xlarge, reported-by-owner; `COMPUTE_BUDGET_CHARTER.md` §5). Predicted $0.02249; cap $0.03078.
- **Launch load, read by the launcher in its own invocation** (`runs/LAUNCH_LOAD.json`): **load1 0.19, load5 0.25, load15 0.10 on 16 CPUs** at 1787759839 (≈15:57Z). **The cost basis is conditioned on this reading:** the 24.1108 solver basis (C-91) was measured at a load of 11.14→15.05 of 16. **Contention: NONE at launch** (ratio 0.19/16 = 1.2 %), so the 0.615 is attributed to a quiet box (the C-115 pattern — a fact about the afternoon, not about the estimator), not to improved estimating. No uncontended control existed for C-91; this run IS that control: the same nine cases ran 1.51× faster on the solver limb (15.90 vs 24.11) with `nWrites` doubled.
- **Grading cost:** pure Python, seconds; not clocked separately; the ≤ 0.5 allowance was not consumed measurably.
- Field data (time directories, `postProcessing/`) stays on disk: `du -sh runs` = **141M**. Committed: this file, `GRADE_F4S.out`, `GRADE_F4S.json`, `STATUS.F4S`, `launcher.out`, `runs/RUN_LEDGER.json`, `runs/LAUNCH_LOAD.json`, `runs/LAUNCH_HEAD.txt`, per-case `log.rhoCentralFoam` and `RC.txt`. **Per-case `result.json` files were expected by the brief and DO NOT EXIST in this run tree** (the ledger row is the per-case record instead); stated, not papered over.

Source: `runs/RUN_LEDGER.json`; `runs/LAUNCH_LOAD.json`; `runs/cyl/M*/*/log.rhoCentralFoam`; `verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md` §9.

## 2. LADDER POSITIONS

**Rule 4 strict completion, checked by this lane on all nine cases (and independently by the comparator's Gate 0, which refused nothing):**

| case | `RC.txt` | `End` | last `Time =` == last dir | `Time =` count == `ExecutionTime` count | fields `T U p rho` newer than own `0/T` | `ClockTime` s |
|---|---|---|---|---|---|---|
| M6.0 coarse | 0 | yes | 5.9998543386 | 6095 = 6095 | yes (+6 s) | 5 |
| M6.0 medium | 0 | yes | 6.000170662342686 | 11096 = 11096 | yes (+29 s) | 29 |
| M6.0 fine | 0 | yes | 6.000009028713065 | 22113 = 22113 | yes (+230 s) | 230 |
| M7.0 coarse | 0 | yes | 6.000140535443495 | 6386 = 6386 | yes (+7 s) | 6 |
| M7.0 medium | 0 | yes | 6.000241494438384 | 12714 = 12714 | yes (+37 s) | 37 |
| M7.0 fine | 0 | yes | 5.999999353137987 | 25272 = 25272 | yes (+278 s) | 278 |
| M8.0 coarse | 0 | yes | 5.999790920062758 | 7207 = 7207 | yes (+8 s) | 7 |
| M8.0 medium | 0 | yes | 6.000109745318508 | 14327 = 14327 | yes (+41 s) | 40 |
| M8.0 fine | 0 | yes | 5.99992751891617 | 28465 = 28465 | yes (+322 s) | 322 |

The last time straddles `endTime = 6.0` on both sides, exactly as §8's registered reach test (`t_last + dt_final > endTime`) anticipates; the comparator applied that clause and admitted all nine. Ladder: three-level Roache family per Mach, r = 2 in each direction (dim 2, `r21 = r32 = 2.0`), window 8 snapshots (min 8), Fs = 1.25, equal-spacing form.

Source: `runs/cyl/M*/*/{RC.txt,log.rhoCentralFoam}`; `GRADE_F4S.json` (`rows[*].levels`, `rows[*].triples`).

## 3. GATES

Comparator run: `python3 grade_f4s.py --root runs --json GRADE_F4S.json` at 16:3xZ, rc 0, stdout in `GRADE_F4S.out`. Header printed: `dim 2  Fs 1.25  form equal  window 8 (min 8)`, `ast.Assert nodes in this grader: 0`.

**Verdict lines, verbatim from `GRADE_F4S.out`:**

```
G-F4S-1-M6.0           0.452242 -> 0.448301 -> 0.446461
   states ['CONVERGING']  orders [1.0983089232384085]
   band (0.42551403932551807, 0.45341729109677825)  (+/- 3.1747 % of Billig)  deviation +1.5918 %
   band_verdict (G-F4S-2 channel): PASS
   VERDICT: PASS
   observed order 1.0983  GCI 0.4516 % at Fs = 1.25

G-F4S-1B-M6.0          0.432018 -> 0.437939 -> 0.445395
   states ['DIVERGENT']  orders [-0.332576028845835]
   band (0.42551403932551807, 0.45341729109677825)  (+/- 3.1747 % of Billig)  deviation +1.3492 %
   band_verdict (G-F4S-2 channel): PASS
   VERDICT: NOT A RESULT

G-F4S-1-M7.0           0.437521 -> 0.431854 -> 0.429132
   states ['CONVERGING']  orders [1.057981105532655]
   band (0.4110090956234202, 0.43818745887741045)  (+/- 3.2005 % of Billig)  deviation +1.0677 %
   band_verdict (G-F4S-2 channel): PASS
   VERDICT: PASS
   observed order 1.0580  GCI 0.7328 % at Fs = 1.25

G-F4S-1B-M7.0          0.438816 -> 0.433553 -> 0.432018
   states ['CONVERGING']  orders [1.7776065017951055]
   band (0.4110090956234202, 0.43818745887741045)  (+/- 3.2005 % of Billig)  deviation +1.7474 %
   band_verdict (G-F4S-2 channel): PASS
   VERDICT: PASS
   observed order 1.7776  GCI 0.1829 % at Fs = 1.25

G-F4S-1-M8.0           0.425915 -> 0.418500 -> 0.417276
   states ['CONVERGING']  orders [2.5987241529429244]
   band (0.4016298298252267, 0.42880819307921697)  (+/- 3.2728 % of Billig)  deviation +0.4955 %
   band_verdict (G-F4S-2 channel): PASS
   VERDICT: PASS
   observed order 2.5987  GCI 0.0725 % at Fs = 1.25

G-F4S-1B-M8.0          0.423246 -> 0.405921 -> 0.417544
   states ['OSCILLATORY']  orders [None]
   band (0.4016298298252267, 0.42880819307921697)  (+/- 3.2728 % of Billig)  deviation +0.5599 %
   band_verdict (G-F4S-2 channel): PASS
   VERDICT: NOT A RESULT
```

**Per gate, per Mach (δ/R, coarse → medium → fine; Billig reference; band ± one local radial cell):**

| gate | M | coarse | medium | fine | triple | p | GCI (Fs 1.25) | band | deviation | VERDICT |
|---|---|---|---|---|---|---|---|---|---|---|
| G-F4S-1 (RH crossing) | 6.0 | 0.452242 | 0.448301 | 0.446461 | CONVERGING | 1.0983 | 0.4516 % | [0.425514, 0.453417] | +1.5918 % | **PASS** |
| G-F4S-1B (argmax) | 6.0 | 0.432018 | 0.437939 | 0.445395 | DIVERGENT | −0.3326 | not quoted (non-monotone triple state) | same | +1.3492 % | **NOT A RESULT** |
| G-F4S-1 | 7.0 | 0.437521 | 0.431854 | 0.429132 | CONVERGING | 1.0580 | 0.7328 % | [0.411009, 0.438187] | +1.0677 % | **PASS** |
| G-F4S-1B | 7.0 | 0.438816 | 0.433553 | 0.432018 | CONVERGING | 1.7776 | 0.1829 % | same | +1.7474 % | **PASS** |
| G-F4S-1 | 8.0 | 0.425915 | 0.418500 | 0.417276 | CONVERGING | 2.5987 | 0.0725 % | [0.401630, 0.428808] | +0.4955 % | **PASS** |
| G-F4S-1B | 8.0 | 0.423246 | 0.405921 | 0.417544 | OSCILLATORY | none | not quoted | same | +0.5599 % | **NOT A RESULT** |

- **G-F4S-2 (the `band_verdict` channel):** PASS on all six rows, computed first and unconditionally; the final verdict on every row is either that band verdict or NOT A RESULT — rule 5's one-way door held on all six.
- **Rule 5 clause order, as the comparator printed it:** G-F4S-1B-M8.0 fell to **clause (a)** — its `why` line reads *"levels coarse,coarse are not iteratively converged or not plateaued; no grid claim can be made from this triple"* (`GRADE_F4S.json`: coarse `NOT CONVERGED` / `NOT PLATEAUED` on the argmax series; medium and fine CONVERGED/PLATEAUED); the triple state OSCILLATORY is printed beside it. G-F4S-1B-M6.0 fell to clause (b), DIVERGENT. All nine crossing-detector series were CONVERGED and PLATEAUED at every level. (The doubled "coarse,coarse" in the why-line is the frozen comparator's own wording — one level named twice for its two failing clauses — reproduced, not edited.)
- **Planted-zero controls:** `planted_zero.passed = true` on all six rows — plant 1.234e-03 into rho at the crossing's lower bracketing index in a copy of the fine-level `.xy`, read back delta 1.2340e-03 by `read_xy(rho column)` (artifact e.g. `runs/cyl/M6.0/fine/postProcessing/sampleDict/6.000009028713065/r0_T_p_rho.xy`). Controls P0, P1, P1b, P2, P3 per Mach and P4, P5, C1 all passed (`GRADE_F4S.json` `controls`); none refused.
- **Cp / modified-Newtonian limb:** `PENDING: a citable reference-class uncertainty for modified Newtonian pressure.` (registered §3). **SWBLI limb:** `BLOCKED` on Sanaa's unmade event-1/event-2 ruling.

**Registered predictions (§15) scored:**

1. **G-F4S-1 `CONVERGING` at ≥ 2 of 3 Mach numbers — MET, and exceeded: 3 of 3**, each PASS against Billig inside the ± one-cell band. F4's non-convergence was the argmax detector at M6.0 and M8.0, now measured rather than diagnosed.
2. **G-F4S-1B `NOT A RESULT` × 3 — PARTIALLY MET: 2 of 3.** M6.0 NOT A RESULT (but by DIVERGENT, not the predicted OSCILLATORY); M8.0 NOT A RESULT (OSCILLATORY, plus a clause-(a) coarse-level refusal); **M7.0 REFUTED — the argmax triple was CONVERGING (p 1.78, GCI 0.18 %) and graded PASS.** §15's own reading of that outcome applies at M7.0: the §5 premise (the argmax detector cannot settle) is weaker than stated for that Mach number, and §5.2 is the thing to re-read first. The "high confidence" attached to this prediction is on the board as a miss.

Source: `GRADE_F4S.out`; `GRADE_F4S.json`; `verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md` §3, §6, §12, §15.

## 4. FD TABLES

nothing

Source: not applicable to this campaign (no finite-difference gradient check is registered in §3).

## 5. REFILLED QUEUE

nothing

Source: `verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md` §3 — the Cp limb stays PENDING on a reference-class uncertainty and the SWBLI limb stays BLOCKED; this lane queues nothing, the supervisor decides.

## 6. WAITING LIST

- The two detectors disagree at M7.0 (both CONVERGING, both PASS, fine values 0.429132 vs 0.432018 — a 0.67 % gap, inside the band). Whether that is worth a registration of its own is the supervisor's call, not this lane's.
- `scripts/roache_triple.py` remains referred to verification; the `-O` entry refusal is what protects this path (§14 item 2).
- Not verified by this lane: no independent re-derivation of the Billig reference values or of the band widths — taken from the frozen comparator as registered.

Source: `GRADE_F4S.json`; `verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md` §14.
