# T4b results — impinging jet on a heated plate, refined near-wall family (first cell halved from T4)

Graded 2026-08-27 by the frozen comparator at three levels.
**RUNG VERDICT: `NOT A RESULT` — three of three graded rows `NOT A RESULT`, all at
gate (1).**

**And the reason matters: the rung did NOT fail on grid convergence.** All three
triples came out `CONVERGING`, exactly as prediction P8 registered. Every row was
stopped by gate (1) — iterative convergence and flow-development controls — under
standing rule 5, order (1). No graded value is claimed and none is available.

Pre-registration: `docs/campaigns/T-family/T4b_PREREGISTRATION.md`.
Run root: `verification/runs/T-family/T4b_runs/`.

---

## 1. The freeze set — five of five MATCH, with the launcher checked against the AMENDED row

| file | registered blob | registered sha256₁₆ | |
| --- | --- | --- | --- |
| `analyse_t4b.py` | `69abe6e5` | `06674874d025c11b` | MATCH |
| `mark_done_t4b.py` | `d5411c3f` | `2d8bdfe91e24138c` | MATCH |
| `build_t4b.py` | `85f6fe84` | `1728afa3f5cef1d4` | MATCH |
| `launch_t4b.sh` | **`8bd93c23`** | **`9c035b147bd1b4ef`** | MATCH |
| `T4b_registered.json` | `0837e95e` | `a4eb13e7eca5435f` | MATCH |

**The launcher was checked against the AMENDED value, not §11's original.** §11's
row `1f12792d` / `9d77ea35b82c94f1` was **STRUCK, not deleted**, by the
pre-firing amendment and replaced with `8bd93c23` / `9c035b147bd1b4ef`; the
amendment records that every other §11 row is unchanged and that no gate, band,
threshold, floor, control, cap, timeout or cost moved. Checking the disk against
the struck value would have manufactured a false drift. **This is what a
correctly transcribed strike looks like** — the replacement sha is written down,
and it is worth contrasting with K0f AMENDMENT 2, which struck two rows without
transcribing their replacements (see `K0f_RESULTS.md` §E1).

The comparator prints its own provenance and it agrees with the disk:
`analyse_t4.py` (frozen, imported) `9842dbc8…`, `analyse_t4b.py` `06674874…`,
`T4b_registered.json` `a4eb13e7…`.

## 2. Completion — three of three, and a stale refusal that has cleared

`mark_done_t4b.py`: **`DONE T4b_IJ_c`, `DONE T4b_IJ_m`, `DONE T4b_IJ_f`**, rc 0.
All three `STATUS.*` read `rc=0 … capped=no checkmesh_rc=0 note=clean`.

**The earlier refusal at `log.analyse_t4b.refused.20260826T205552Z.txt` was
correct and is now stale**, and it is worth stating why rather than deleting it.
It read *"REFUSE: no `DONE.T4b_IJ_f` — the whole rung is graded or none of it
is"*. `T4b_IJ_f` did not finish until **04:23:57Z on 2026-08-27**, seven and a
half hours after that refusal. The refusal was a `PENDING` correctly expressed as
a refusal to grade a partial rung — **not a defect, and not a verdict** — and the
comparator's own words are the right rule: it does not overrule the completion
checker.

## 3. Controls — four planted controls PASS, and the gate-(1) controls do not

**Planted controls (rule 3), all four PASS:**

| control | plant | recovered / result | |
| --- | --- | --- | --- |
| G reader (frozen) | 1.234e-03 at line 43685 | 3.20409e-05, floor 1e-06 | PASS |
| y+ reader | — | **blind path 0 on every patch**; registered path plate max 0.6893; **U ×4 → y+ ×2 (expected 2)** | PASS |
| exit-line reader | 1.234e-03 at line 5208 | 4.60364e-05, floor 1e-06 | PASS |
| flux reader | inlet `phi` ×1.01 | imbalance 0.00990094775 (**predicted 0.00990094775**) | PASS |

The y+ control is the strongest of the four and deserves naming: it runs a
**blind path that returns 0 on every patch**, so a reader that cannot see is
distinguishable from a wall that is genuinely fine; and it then perturbs `U` by
×4 and confirms y+ moves by ×2, which is the square-root scaling a correct y+
reader must show. **A zero from that reader is evidence because the reader was
shown able to produce a non-zero AND to scale correctly.**

**Gate-(1) controls, by level — five failures across the three levels:**

| level | C1 plate y+max | C1b pipe y+max | C2 U_c/U_bulk | C3 imbalance | C6.1 p_rgh floor | C6.2 growth ratio | C6.3 field change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c (t=20000) | 0.6893 ok | 0.3979 ok | **1.1746 FAIL** | 4.28e-08 ok | **2.121e-06 FAIL** | 0.99999953 ok | 1.186e-09 ok |
| m (t=30000) | 0.3490 ok | 0.2017 ok | 1.1909 ok | 3.61e-10 ok | 1.329e-07 ok | **1.1366 FAIL** | **2.848e-04 FAIL** |
| f (t=40000) | 0.1758 ok | 0.1020 ok | 1.2021 ok | 1.19e-08 ok | 3.201e-08 ok | 1.00523 ok | **8.170e-04 FAIL** |

## 4. THE THREE GRADED ROWS — all `NOT A RESULT`, and the triples are not why

| row | station | fine value | reference | band | triple | p | GCI | verdict |
| --- | --- | ---: | ---: | --- | --- | ---: | --- | --- |
| **G1** | r/D = 1.0 | 1.0847 | 1.0890 | [1.0690, 1.1090] | **CONVERGING** | 1.414 | **n/a** | **NOT A RESULT** |
| **G2** | r/D = 2.0 | 0.8120 | 0.7888 | [0.7688, 0.8088] | **CONVERGING** | 0.672 | **n/a** | **NOT A RESULT** |
| **G3** | r/D = 3.0 | 0.5371 | 0.4632 | [0.4432, 0.4832] | **CONVERGING** | 1.008 | **n/a** | **NOT A RESULT** |

**Standing rule 5, order (1), applied exactly as written.** A level that is not
iteratively converged makes the row `NOT A RESULT` *before* the triple is
consulted, and the gate can only turn a verdict **into** `NOT A RESULT`, never
the reverse. **No GCI is quoted on any row.**

**Where the band sits is recorded as information, NOT as a verdict**, because a
verdict on these rows does not exist: G1's 1.0847 lies inside its band, G2's
0.8120 lies 0.0032 above its upper edge, and G3's 0.5371 lies 0.0539 above its
upper edge. **Nobody may read those positions as PASS or GATE FAIL.** They are
recorded so that the eventual re-run has something to compare against.

## 5. THE FINDING — the endTimes are too short, and they get MORE too short as the mesh refines

Read the C6.3 column of §3 in order: **c 1.186e-09, m 2.848e-04, f 8.170e-04**
against a floor of 2e-04. The coarse level is settled to nine decimal places; the
medium level misses the floor by 1.4×; the fine level misses it by **4.1×**.
**The field change at the registered `endTime` GROWS by nearly three orders of
magnitude from c to f, and the two finer levels are moving when they are read.**

The registered `endTime` schedule is 20 000 / 30 000 / 40 000 — it rises by 1.5×
and 1.33× while the cell count rises by 4× each step. **A jet impingement region
resolved four times more finely needs more iterations to settle, not fewer per
cell**, and the schedule assumed the opposite direction. The coarse level's own
two failures are different in kind and smaller: `C2` says the pipe flow is not
fully developed at 48 cells (1.1746 against a required ±3 % of 1.2245), and
`C6.1` says its `p_rgh` plateau sat at 2.12e-06 against a 1e-06 floor.

**This is a recoverable rung, and what it needs is arithmetic that already
exists:** longer `endTime`s on m and f, sized so C6.3 clears 2e-04, plus a longer
inlet pipe or more radial cells for C2 at the coarse level. **This lane does not
set those numbers** — that is a new registration, not a lane's call.

## 6. Predictions — scored honestly, and the pattern is that the PHYSICS predictions held

- **P1 (plate y+max) — HIT on all three.** Predicted c [0.55, 0.80], m [0.28,
  0.42], f [0.14, 0.22]; measured **0.6893 / 0.3490 / 0.1758**.
- **P1b (pipe y+max) — HIT on all three.** Predicted c [0.12, 0.45], m [0.06,
  0.25], f [0.03, 0.14]; measured **0.3979 / 0.2017 / 0.1020**.
- **P2 (U_c/U_bulk in [1.19, 1.26]) — MISS on the coarse level, HIT on m and f.**
  Measured **1.1746 / 1.1909 / 1.2021**. The coarse miss is the same fact as the
  `C2` gate failure and is not double-counted as two findings.
- **P3 (mass imbalance ≤ 1e-4) — HIT on all three.** Measured 4.28e-08 /
  3.61e-10 / 1.19e-08.
- **P4 (`p_rgh` plateau at c in [2e-07, 1e-06]) — MISS.** Measured
  **2.121e-06**, about 3× the 7e-07 point and 2.1× the interval's top. **The
  registration had already disclosed this as the thin one** — *"the C6.1 margin on
  the coarse level is 1.43× and is disclosed"* — and the margin was not there.
  **A disclosed thin margin that then fails is the disclosure working, not a
  surprise.**
- **P5 (G1 fine in [1.055, 1.085]) — value HIT at 1.0847**, triple `CONVERGING`
  with p 1.414 in the predicted [0.5, 2.5]. **Its `verdict_predicted: GATE FAIL`
  is a MISS**: the row is `NOT A RESULT`, and on band position it would have been
  PASS rather than GATE FAIL.
- **P6 (G2 fine in [0.795, 0.835]) — value HIT at 0.8120**; its predicted GATE
  FAIL is consistent with the band position but is **superseded by gate (1)** and
  is not scored as a verdict hit.
- **P7 (G3 fine in [0.515, 0.56]) — value HIT at 0.5371**, essentially on the
  0.538 point; same treatment as P6. The registration's stated reason —
  *"kOmegaSST over-predicts the decaying wall jet"* — is what the number shows.
- **P8 (all three triples `CONVERGING`) — HIT.** The registration says it was
  registered *"so a gate-(2) `NOT A RESULT` is a scored miss"*. **The
  `NOT A RESULT` came from gate (1), not gate (2)**, so P8 is a clean hit and the
  rung's failure is **not** attributable to grid behaviour. This is the single
  most useful line in the scoring: **the mesh family is behaving; the run
  schedule is not.**

## 7. Cost — rule 12, and the CEILING rule was right where the POINT was not

- **Predicted: POINT 515.90 core-min** (c 11.84, m 74.65, f 429.41); **CEILING
  773.85** (1.5 × POINT); cap total **1035** (c 25, m 150, f 860).
- **Measured: 729.667 core-min** = (846 + 5 178 + 37 756) wall s × 1 rank ÷ 60.
- **Gross = cleaned.** `IJ_m` and `IJ_f` exceed the 3 600 wall-s stall figure and
  **neither is a stall**: rc 0, `capped=no`, last time == `endTime` on both.
  **WASTE: 0.000 core-min** — nothing abandoned, nothing re-run, **no level
  reached its cap** (c 56.4 %, m 57.5 %, f 73.2 %, total 70.5 % of 1035).
- **Ratio actual/POINT 1.4144. Ratio actual/CEILING 0.943 — INSIDE the ceiling.**
- **NAMED SEPARATELY AND NOT LAUNDERED INTO THE RATIO: 729.667 core-min bought NO
  GRADED VALUE.** It is not waste in the charter §6 sense — every case ran its
  registered program to its registered `endTime` and the controls did their job —
  but a completion report that let a 1.41 ratio stand as the whole story would
  hide that the rung produced nothing gradeable. Following the C-149 precedent,
  it is stated here as its own fact.
- **Attribution: the same coupled-solver mesh-scaling penalty, and the ceiling
  rule anticipated it.** Measured core-s per cell-iteration **c 6.9940e-06,
  m 7.1346e-06, f 9.7543e-06** against the registered per-level T4 rates
  5.873843e-06 / 6.171232e-06 / 6.656298e-06 — **1.191× / 1.156× / 1.465×**, a
  1.395× rise across a 16× cell increase. **The registered CEILING rule named this
  mechanism in advance**: *"the halved first cell (aspect ratio 1627–1645) and a
  box at 12–13 of 16 cores busy can raise the `p_rgh` GAMG iteration count"*, and
  set 1.5 × POINT. **The realised 1.414 landed inside it. The ceiling was a good
  prediction; the POINT was not, and the difference between them is the value of
  writing a mechanism down rather than a number.**
- **Consistent with C-155 (T13) and K0f C-137**, all three `buoyantBoussinesq
  SimpleFoam`: the per-cell-iteration rate rises with mesh size for this coupled
  solver. It is milder here (1.395× against T13's 4.33×) because T4b's POINT was
  already built from **per-level measured T4 rates** rather than from a single
  coarse-level rate — **which is exactly the correction C-155 recommends, applied
  in advance, and it cut the miss from 3.17× to 1.41×.**
- **Dollars, DERIVED, NOT MEASURED** at $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5): **$0.6239** against POINT $0.4411 and CEILING
  $0.6616.
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit from the tail.

## 8. Disclosures

- **No graded value exists for this rung.** The fine values in §4 are printed
  beside their bands so a re-run has a baseline; they are **not** verdicts and
  must not be quoted as PASS or GATE FAIL.
- **The rung is `NOT A RESULT`, not `GATE FAIL`.** Those are different words for
  different facts, and the difference here is that the solve was not finished.
- The earlier refusal log is **retained, not deleted** (§2).
- No frozen file edited (rule 6). **Nothing sent, filed, uploaded, posted or
  registered outside this box** (rule 7).
