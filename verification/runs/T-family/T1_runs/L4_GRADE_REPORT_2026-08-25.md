# T1b L4 pool grade — lane report, 2026-08-25

Lane: `lab-lane`, heat-transfer team. Grading only; **zero solver compute**.
Authority: Sanaa's explicit go for the T1b L4 pool grade, relayed by
heat-transfer-supervisor.

**No tier is assigned in this document.** Tiering (HOLDS / GATE REACHED /
SURVEYED / NOT HELD / NEVER RUN) is the supervisor's and depends on a rubric
ruling Sanaa has not given. What follows is verdicts and numbers only.

---

## 0. Headline

| | |
| --- | --- |
| Graded rows | **0** |
| PASS | 0 |
| GATE FAIL | 0 |
| NOT A RESULT | **4** (X0, X1, X3, X4 — every Nu row) |
| Other | X2, friction, carries the comparator's own label `REPORTED` (see §7.1) |
| Comparator exit code | **0** |
| GCI quotable on any row | **none** — no triple is CONVERGING |

**The exit code 0 does not mean the rung passed.** `analyse_t1b_L4.py:281`
returns `EXIT_FAIL` only if the GATE FAIL list is non-empty; with every row
gated out to NOT A RESULT the list is empty and the process exits 0 on a rung
that produced no graded row at all. Recorded here because it is a
flattering-direction reading hazard, and this family's standing prior is that
its recent record defects all ran in that direction.

---

## 1. Marker sweep (STEP 2)

Box idleness confirmed before any write: `find . -mmin -10` over the run
directory returned nothing; no solver process (the only `pgrep` hit was the
sweep's own shell — the known self-match trap). No `log.solve.ext1` exists on
any of the four x cases, so `mark_done_t1b_L4.py` took the strict `check()`
branch on all four and **no marker could be removed** — removal at line 199 is
reachable only for a case in the `ext` set.

A `--dry-run` preview (the script's own supported flag, line 182) was taken
first: `4/4 x-level cases meet the strict completion rule (0 with an ext1
extension)`, no marker written or removed. The real invocation
(`python3 mark_done_t1b_L4.py`, no arguments) then ran.

| | |
| --- | --- |
| DONE.* before | 41 |
| DONE.* after | **44** |
| Created | `DONE.R_30k_x`, `DONE.R_100k_x`, `DONE.R_300k_x` |
| Removed | **none** |
| Refusals | **none** — 4/4 met the strict rule |
| Marker content, all four x | `strict rule met` |

Exactly the three expected markers were created. `DONE.R_10k_x` was rewritten
with identical content (it was already present and already passing).

### 1.1 What `mark_done_t1b_L4.py` checks (STEP 1, read as source before running)

Read at `verification/runs/T-family/T1_runs/mark_done_t1b_L4.py`, 219 lines. It
imports `NEEDED`, `NEEDED_TURBULENT`, `control_end_time` and `is_laminar` from
`mark_done_t1b` so the field list and endTime parser are the frozen originals;
it re-expresses the same six tests against `STATUS.<case>` (the pool format
`run_one_t1b_L4.sh` writes) instead of `STATUS2.<case>`. The six clauses, in
`check()` (lines 98–122):

1. `STATUS.<case>` exists and reports `rc=0` (lines 104–108).
2. `log.solve` ends with OpenFOAM's own `End` line, matched as `^End\s*$`
   multiline (lines 113–114).
3. The last written non-zero time directory equals the controlDict `endTime`,
   to 1e-9 (lines 78–80).
4. That time directory carries every field the comparator will read —
   `NEEDED` plus `NEEDED_TURBULENT` for a non-laminar case (lines 82–84, 117).
5. The count of `^ExecutionTime` lines equals `int(endTime)` (lines 115,
   120–121).
6. **The age guard**: every field in that time directory has an mtime newer
   than the case's own `0/T`, which the runner touches last when it creates
   `0` from `0.orig` (lines 86–95, 118–119) — the D438 / L-143 stray-write
   guard.

A case is DONE only if **all six** hold; any failure appends a reason and the
marker is not written. `check_ext()` (lines 125–177) applies the same six
across two segments when `log.solve.ext1` exists, and additionally requires
the first `Time =` of the extension to be exactly one past the original
segment's `ExecutionTime` count (lines 168–176) — that branch was not taken
here.

**It writes only `DONE.*` marker files** (line 196, `open(.../f"DONE.{c}", "w")`)
and removes only `DONE.*` markers (line 200, and only for extended cases). It
opens no case field for writing and mutates no case tree. Confirmed by reading,
not by probing: a previous lane's `--help` probe once ran this script in real
mode, so it was read rather than exercised.

---

## 2. Freeze re-verification (STEP 3)

Computed in the **same shell invocation** as the grade, gated explicitly with
`|| { echo ABORT-FREEZE; exit 1; }` (no `set -e` — it does not gate at
Bash-tool top level in this harness). Each working-tree `git hash-object`
compared against `git rev-parse 17209b50:<path>`, the pre-registration commit.

| file | hash now | prereg blob | |
| --- | --- | --- | --- |
| `analyse_t1b_L4.py` | `59c345bd8f9c2744459dc9564942a47fb12bd5fe` | identical | OK |
| `analyse_t1b.py` | `17436d64dcea5234eafb170d30e0668d1ff8183d` | identical | OK |
| `analyse_t1c.py` | `3d56680271d5fabb30e60cdc2eb1a6551196711d` | identical | OK |
| `mark_done_t1b_L4.py` | `2055d35be50f53c0c23cb8abf46444ca5b359a80` | identical | OK |

All four match the supervisor's own reading taken minutes earlier. **The file
that ran is the file that was frozen.** No frozen file was edited by this lane;
no byte of `analyse_t1b_L4.py`, `mark_done_t1b_L4.py`, `analyse_t1b.py`,
`analyse_t1c.py` or `T1b_L4_AMENDMENT.md` was touched.

---

## 3. STEP 4(1) — per-level convergence and plateau, level by level

The gate is applied per level **before** any triple is formed, against that
level's own registered criteria:

- **Iterative convergence** — `analyse_t1c.iterative_convergence()`, field `T`,
  `tol = 1e-6` on the relative change (max absolute change between the last two
  written checkpoints, divided by the field range at the later one).
- **Plateau** — `Nu_station_spread <= PLATEAU_FRACTION * band(Re)` with
  `PLATEAU_FRACTION = 0.2` (`analyse_t1b.py:49`), spread taken across the
  stations 60 / 70 / 80 D. The threshold is **per Re**, since the band is.

Only the `(m, f, x)` levels are gated (`LEVELS_L4`); `c` is shown for context.

### 3.1 Iterative convergence

| case | state | relative | tol | max change (K) | field range (K) | checkpoints |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `R_10k_c` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.8701 | 18000 / 20000 |
| `R_10k_m` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.8720 | 18000 / 20000 |
| `R_10k_f` | CONVERGED | 2.093e-07 | 1e-06 | 1.8209e-07 | 0.8699 | 18000 / 20000 |
| **`R_10k_x`** | **NOT_CONVERGED** | **4.832e-02** | 1e-06 | **2.9992e-02** | 0.6206 | 18000 / 20000 |
| `R_30k_c` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.3227 | 18000 / 20000 |
| `R_30k_m` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.3231 | 18000 / 20000 |
| `R_30k_f` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.3220 | 38000 / 40000 |
| `R_30k_x` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.3208 | 78000 / 80000 |
| `R_100k_c` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.1093 | 18000 / 20000 |
| `R_100k_m` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.1093 | 18000 / 20000 |
| `R_100k_f` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.1089 | 56000 / 58000 |
| **`R_100k_x`** | **NOT_CONVERGED** | **1.954e-05** | 1e-06 | **2.1174e-06** | 0.1084 | 78000 / 80000 |
| `R_300k_c` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.0408 | 18000 / 20000 |
| `R_300k_m` | CONVERGED | 4.730e-08 | 1e-06 | 1.9265e-09 | 0.0407 | 18000 / 20000 |
| `R_300k_f` | CONVERGED | 0.000e+00 | 1e-06 | 0.0000e+00 | 0.0405 | 66000 / 68000 |
| **`R_300k_x`** | **NOT_CONVERGED** | **1.269e-04** | 1e-06 | **5.1175e-06** | 0.0403 | 78000 / 80000 |

**Three of the four x levels failed the registered iterative-convergence
criterion**, by factors of 48 320x (1e4), 19.5x (1e5) and 127x (3e5) over
tolerance. Every `c`, `m` and `f` level converged. `R_30k_x` is the sole x
level that converged, and it did so exactly (0.0 K between 78000 and 80000).

### 3.2 Plateau across 60 / 70 / 80 D

| case | Nu spread | threshold 0.2 x band | plateaued? | Nu at 60 / 70 / 80 D |
| --- | ---: | ---: | :---: | --- |
| `R_10k_c` | 0.0060 | 0.1758 | yes | 30.1252 / 30.1225 / 30.1192 |
| `R_10k_m` | 0.0046 | 0.1758 | yes | 30.8350 / 30.8304 / 30.8307 |
| `R_10k_f` | 0.0036 | 0.1758 | yes | 31.6219 / 31.6183 / 31.6193 |
| `R_10k_x` | 0.0815 | 0.1758 | yes | 32.4953 / 32.5760 / 32.5768 |
| `R_30k_c` | 0.0144 | 0.5725 | yes | 69.1177 / 69.1126 / 69.1033 |
| `R_30k_m` | 0.0126 | 0.5725 | yes | 70.7445 / 70.7338 / 70.7319 |
| `R_30k_f` | 0.0103 | 0.5725 | yes | 72.4901 / 72.4801 / 72.4798 |
| `R_30k_x` | 0.0098 | 0.5725 | yes | 73.9142 / 73.9044 / 73.9045 |
| `R_100k_c` | 0.0322 | 2.0311 | yes | 177.5384 / 177.5313 / 177.5062 |
| `R_100k_m` | 0.0300 | 2.0311 | yes | 181.6119 / 181.5905 / 181.5819 |
| `R_100k_f` | 0.0250 | 2.0311 | yes | 185.7963 / 185.7762 / 185.7713 |
| `R_100k_x` | 0.0244 | 2.0311 | yes | 189.2318 / 189.2115 / 189.2074 |
| `R_300k_c` | 0.0686 | 5.2512 | yes | 430.2883 / 430.2879 / 430.2197 |
| `R_300k_m` | 0.0721 | 5.2512 | yes | 439.8330 / 439.7944 / 439.7609 |
| `R_300k_f` | 0.0668 | 5.2512 | yes | 449.3222 / 449.2818 / 449.2554 |
| `R_300k_x` | 0.0461 | 5.2512 | yes | 457.1473 / 457.1080 / 457.1012 |

**All sixteen levels plateaued** against their registered thresholds. No row is
gated out on plateau.

One honest qualification, recorded because it points the same way as the
convergence failure and not the other way: `R_10k_x`'s spread of 0.0815 is
**14–23x** that of its own `c`, `m` and `f` siblings (0.0036–0.0060) and sits at
46 % of its threshold, with the 60 D station 0.08 below the other two. That is
the signature of a field still moving, consistent with §3.1. It nonetheless
**passes** the registered criterion, and this report does not upgrade or
downgrade it on that observation — the registered threshold is the threshold.

---

## 4. STEP 4(2) — the triples

`analyse_t1c.gci()`, r = 1.6, classifying each triple's state. Both the frozen
`(c, m, f)` triple and the amended `(m, f, x)` triple are given, as the
amendment requires.

### 4.1 Nusselt triples

| Re | Nu at m / f / x | `(m,f,x)` state | p | `(c,m,f)` state | p |
| ---: | --- | --- | ---: | --- | ---: |
| 1e4 | 30.831 / 31.619 / 32.577 | **DIVERGENT** | -0.413 | DIVERGENT | -0.219 |
| 3e4 | 70.732 / 72.480 / 73.904 | **STAGNANT** | +0.435 | DIVERGENT | -0.150 |
| 1e5 | 181.582 / 185.771 / 189.207 | **STAGNANT** | +0.422 | DIVERGENT | -0.059 |
| 3e5 | 439.761 / 449.255 / 457.101 | **STAGNANT** | +0.406 | STAGNANT | +0.010 |

**Not one of the four `(m, f, x)` Nusselt triples is CONVERGING.** Independently
of §3.1, every Nu row is NOT A RESULT on the triple state alone. Three of the
four rows are therefore doubly gated (level convergence *and* triple state); the
3e4 row is gated on triple state alone, its three levels having all converged
and plateaued.

### 4.2 Friction triples

| Re | f at m / f / x | `(m,f,x)` state | p | `(c,m,f)` state | p |
| ---: | --- | --- | ---: | --- | ---: |
| 1e4 | 0.03028 / 0.03106 / 0.03171 | STAGNANT | +0.381 | DIVERGENT | -0.307 |
| 3e4 | 0.02233 / 0.02290 / 0.02338 | STAGNANT | +0.399 | DIVERGENT | -0.233 |
| 1e5 | 0.01691 / 0.01733 / 0.01767 | STAGNANT | +0.387 | DIVERGENT | -0.132 |
| 3e5 | 0.01358 / 0.01389 / 0.01415 | STAGNANT | +0.379 | DIVERGENT | -0.057 |

All four friction `(m, f, x)` triples are STAGNANT.

### 4.3 GCI

**No GCI is quoted anywhere in this report, and none was printed by the
comparator.** A GCI is quotable only on a CONVERGING triple; no triple, Nusselt
or friction, frozen or amended, is CONVERGING. Every observed order above is
either negative or below 0.5, i.e. the x-to-f step did not fall to 1.6^-0.5 of
the f-to-m step.

---

## 5. STEP 4(3) — gate outcomes

Reached on no row: step (3) of the amended order is entered only on a CONVERGING
triple, and there is none.

| row | Re | quantity | value | verdict | why |
| --- | ---: | --- | ---: | --- | --- |
| X0 | 1e4 | Nu | 32.5768 | **NOT A RESULT** | level x not iteratively converged |
| X1 | 3e4 | Nu | 73.9045 | **NOT A RESULT** | triple `(m,f,x)` is STAGNANT |
| X2 | 3e4 | f | 0.02338 | `REPORTED` | not gated (see §7.1) |
| X3 | 1e5 | Nu | 189.2074 | **NOT A RESULT** | level x not iteratively converged |
| X4 | 3e5 | Nu | 457.1012 | **NOT A RESULT** | level x not iteratively converged |

### 5.1 Band deviations, stated for the record

These are **not verdicts**. The amended rule is explicit that the gate can only
turn a PASS or GATE FAIL **into** NOT A RESULT and never the reverse; every Nu
row above is NOT A RESULT and stays so. The distances are recorded because
three of the four were never printed by the comparator (it `continue`s at line
242 before `verdict_amended` runs) and because the 1e4 figure would otherwise
disappear from the record entirely.

| Re | Nu_x | reference | deviation | band | inside band? |
| ---: | ---: | ---: | ---: | ---: | :---: |
| 1e4 | 32.5768 | 30.9068 | **5.403 %** | 2.844 % | **NO** |
| 3e4 | 73.9045 | 73.6843 | 0.299 % | 3.885 % | yes |
| 1e5 | 189.2074 | 190.3984 | 0.625 % | 5.334 % | yes |
| 3e5 | 457.1012 | 456.7228 | 0.083 % | 5.749 % | yes |

The 1e4 x value sits at **1.90x its band**. Had its triple been CONVERGING and
its level converged, that row would have been GATE FAIL. It is not being graded
GATE FAIL here — it is NOT A RESULT — but a reader who saw only "NOT A RESULT"
beside three comfortable deviations would take a materially rosier view of the
1e4 rung than the numbers support. Recorded for that reason.

The band is the **disagreement between two correlations**, not either one's own
accuracy. Inside it means consistent with the canon, not verified to that
tolerance.

---

## 6. STEP 5 — the registered §3.6 prediction

`docs/campaigns/T-family/T1b_L4_AMENDMENT.md` §3.6, at lines 222–226 of the
file, registers a **compound** prediction. Quoted in full, since grading only
its first clause would flatter it:

> Prediction: **`R_10k_x` is NOT CONVERGED at 20000 and needs the section 4
> extension (to about 32000); `R_30k_x`, `R_100k_x`, `R_300k_x` are CONVERGED
> by 80000** (fine-level counts times 1.6 are 64000 / 92800 / 108800, so 1e5 and
> 3e5 are at risk of needing an extension as well; that is why the protocol is
> registered here rather than decided later).

The bold text is the registered prediction; the parenthesis is a caveat, not a
prediction, and does not carry the claim.

| clause | predicted | measured | verdict |
| --- | --- | --- | --- |
| `R_10k_x` NOT CONVERGED at 20000 | NOT_CONVERGED | NOT_CONVERGED, relative 4.832e-02 vs tol 1e-06 (48 320x), max change 2.9992e-02 K between 18000 and 20000 | **borne out** |
| `R_30k_x` CONVERGED by 80000 | CONVERGED | CONVERGED, relative 0.000e+00 between 78000 and 80000 | **borne out** |
| `R_100k_x` CONVERGED by 80000 | CONVERGED | **NOT_CONVERGED**, relative 1.954e-05 vs tol 1e-06 (19.5x), max change 2.1174e-06 K | **not borne out** |
| `R_300k_x` CONVERGED by 80000 | CONVERGED | **NOT_CONVERGED**, relative 1.269e-04 vs tol 1e-06 (127x), max change 5.1175e-06 K | **not borne out** |

**Verdict on §3.6 as registered: two of four clauses borne out, two not.** The
headline clause the brief names — `R_10k_x` NOT CONVERGED at 20000 — is borne
out, and decisively: it missed tolerance by more than four orders of magnitude,
and the amendment's own §4 table confirms `R_10k_x` was registered at endTime
20000 with checkpoints 18000 vs 20000, which is what ran.

The two failed clauses were **anticipated as a risk** by the parenthetical, and
that is exactly why §4's extension protocol was registered in advance rather
than decided now. That is to the amendment's credit as a protocol. It does not
convert a failed prediction into a borne-out one, and this report does not score
it that way.

**Consequence not yet actioned:** by §4's registered extension protocol, a level
reported NOT_CONVERGED at its endTime is resumed from `latestTime` to a raised
endTime by an extension runner of the `run_one_ext1.sh` form. Three x cases now
qualify (`R_10k_x`, `R_100k_x`, `R_300k_x`). **This lane launched no extension
and no solver of any kind** — the brief is grading only, and an extension is
compute the supervisor must authorise against a pre-registered cost.

---

## 7. Findings the comparator's own output does not surface

Recorded under this family's standing prior that recent record defects have all
run in the flattering direction. None of these is a defect in a frozen file's
*numbers*; each is a reporting gap. **No frozen file was edited to address any
of them.**

**7.1 `REPORTED` is outside the fixed verdict vocabulary.** Row X2 carries
verdict `REPORTED` (`analyse_t1b_L4.py:260`). The lab's fixed vocabulary is
PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING. The
amendment does register friction as "REPORTED, not gated" (§3.4), so the label
is pre-registered and intentional rather than invented at grading time; it is
nonetheless a vocabulary departure that a downstream ledger reading
`gate_t1b_L4.json` will encounter. Referred to the supervisor; not resolved
here.

**7.2 Three of four registered friction rows were never emitted.** The
`continue` at `analyse_t1b_L4.py:242` returns to the loop as soon as a Nu row is
gated out, before the friction row for that Re is built. Only the 3e4 friction
row (X2) exists in the output and in `gate_t1b_L4.json`. §3.4 of the amendment
registers friction predictions for all four Re, so three registered predictions
have no emitted row. The values are recoverable from `out["cases"]` in the same
JSON, and are given in §4.2 and §7.3 here so they are not lost.

**7.3 The §3.4 friction prediction, for completeness.** Outside my brief, which
named §3.6, but cheap to state and registered:

| Re | f_x | Petukhov | shortfall | predicted |
| ---: | ---: | ---: | ---: | --- |
| 1e4 | 0.03171 | 0.03148 | **+0.74 %** | "crosses above" — borne out |
| 3e4 | 0.02338 | 0.02364 | -1.08 % | inside predicted 0.7–1.6 % |
| 1e5 | 0.01767 | 0.01799 | **-1.77 %** | outside predicted 0.7–1.6 % |
| 3e5 | 0.01415 | 0.01444 | **-1.96 %** | outside predicted 0.7–1.6 % |

"The friction triples (m, f, x) are also NOT CONVERGING" is borne out — all four
are STAGNANT (§4.2).

**7.4 §3.5 y+.** Predicted 0.38–0.39 at the x level. Measured 0.3915 (1e4),
0.3881 (3e4), 0.3868 (1e5), 0.3864 (3e5). The 1e4 value is marginally **above**
the predicted band. Noted, not graded — §3.5 is outside my brief.

**7.5 The frozen comparator's four PASS verdicts stand beside these.** For the
record, as the amendment requires: `analyse_t1b.py` graded all four `(c, m, f)`
rows PASS (Nu 31.619 / 72.480 / 185.771 / 449.255, deviations 2.305 / 1.635 /
2.430 / 1.635 %) while their triples were DIVERGENT, DIVERGENT, DIVERGENT and
STAGNANT respectively. That is the defect the amendment exists to close, and it
is now closed on the L4 pool: under the amended order every one of those rows is
NOT A RESULT.

---

## 8. Cost

Measured for the grading invocation, from wall clock around
`python3 analyse_t1b_L4.py` in the same shell:

| | |
| --- | --- |
| Wall seconds | **87.565** |
| Ranks | 1 (single serial Python process) |
| **Core-minutes** | **87.565 x 1 / 60 = 1.459** |
| Solver compute | **zero** — no solver was launched by this lane |

Derived dollar cost at the recorded c7a.4xlarge rate of $0.0513/core-h:
1.459 core-min = 0.02432 core-h = **$0.0012, derived and not measured** (the box
cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5).

**Not measured:** the marker sweep (`--dry-run` plus the real invocation) was
not timed. It is stat and regex work over existing logs with no field
computation. No figure is offered for it rather than an estimate presented as a
measurement.

---

## 9. What this lane could not verify

- **Why** three x levels failed to converge at 80000 / 20000 iterations. The
  gate reports the state; diagnosing it would need the residual history and is
  not grading.
- **Whether an extension would converge them**, or where. §3.6's "about 32000"
  for `R_10k_x` is a registered estimate and remains ungraded — no extension has
  been run.
- **The frozen comparator's own measurement chain.** `analyse_t1b.measure()`,
  the wall radius read from `points`, and the alphaEff factor read from the
  written `alphat` were used as frozen and were not independently re-derived.
- **The planted-zero control.** This comparator does not carry a plant-and-read-
  back control of the kind `analyse_t3.py` and `analyse_t10a.py` do. No zero is
  load-bearing in this grade (every row is gated out on a non-zero criterion, and
  the several exact 0.000e+00 convergence readings are corroborated by non-zero
  readings on `R_10k_f`, `R_10k_x`, `R_100k_x`, `R_300k_x` and `R_300k_m` from
  the same reader — the reader is demonstrably able to see a non-zero). Recorded
  so the absence is on the record rather than assumed harmless.
- **Any tier.** Not assigned; see the header.

---

## 10. Artifacts

| what | path |
| --- | --- |
| Comparator output (rewritten by this run) | `verification/runs/T-family/T1_runs/gate_t1b_L4.json` |
| Markers created | `verification/runs/T-family/T1_runs/DONE.R_{30k,100k,300k}_x` |
| Frozen comparator | `verification/runs/T-family/T1_runs/analyse_t1b_L4.py` |
| Frozen marker tool | `verification/runs/T-family/T1_runs/mark_done_t1b_L4.py` |
| Band, committed before any case existed | `verification/runs/T-family/T1_runs/T1b_band.json` |
| Registered amendment | `docs/campaigns/T-family/T1b_L4_AMENDMENT.md` |
| Pre-registration commit | `17209b50` |

`gate_t1b_L4.json` was rewritten by the grading run and is left **uncommitted**
by this lane — the brief authorised committing this report path only. The
supervisor should decide whether that artifact is landed.

*Lane report. Verdicts and numbers only; tiering is the supervisor's.*
