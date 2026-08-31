# VMFL006 — RESULTS — Multicomponent Species Transport in Pipe Flow

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, pp. 27–28.**
Graded by `ansys-lane-opus48` on 2026-08-31T17:31Z against the freeze committed at
`e28a6a29`. HEAD at grading `f1a723ac3a0d8da5c9e54ab7a0a80127ab366f26`.

---

## VERDICT: `NOT A RESULT`

**Cause: the frozen convergence CONTROL refused (exit 2).** The comparator
`grade_vmfl006.py`, run over the run root on the frozen grading path, **REFUSED at
the L1 convergence clause** — the T residual channel is exactly flat (NULL RANGE)
over the last 200 iterations — and exited 2 **before producing a grading JSON**.
Per the frozen `PREREGISTRATION.md` §13 point 3 ("any completion, control or
reproduction clause refuses") this is `NOT A RESULT`, whatever the physics value.
This is **not** a defective solve — see the diagnostic section below, where the
physics is measured to be excellent — it is a frozen convergence clause that is
**jointly unsatisfiable on this run**, for opposite reasons across the three levels.

No `GRADING_VMFL006.json` exists in the run root: the frozen comparator writes the
JSON only on the non-refusing path, and it refused. This record is the grading
artifact.

---

## 1. Freeze verification (re-hashed on the grading path, never taken on trust)

The four frozen files hash **IDENTICAL** on disk, at `e28a6a29`, and at HEAD
`f1a723ac`; `e28a6a29` is an ancestor of HEAD:

| File | blob (disk = freeze = HEAD) |
|---|---|
| `PREREGISTRATION.md` | `0cf33d7c6e34…` |
| `grade_vmfl006.py` | `d639a2e80457…` |
| `graetz_reference_vmfl006.py` | `355f70bb10b8…` |
| `run_vmfl006.sh` | `3b1204c62e5d…` |

Supervisor's personal rule-2 verification (freeze 17:16:25Z; earliest run-root byte
17:18:52Z; gap +147 s; run root absent at freeze) is built on, not re-done.

## 2. Selftest — 47/47 in both modes

`grade_vmfl006.py --selftest`, `__pycache__` cleared first (stale bytecode inverts
selftests):

- `python3` : **47 PASS / 0 FAIL, rc 0**, "SELFTEST: all checks passed".
- `python3 -O` : **47 PASS / 0 FAIL, rc 0**, identical.

Reachability confirmed **from the selftest itself**, not asserted: `PASS`
(constructed in-band converging run → PASS; small-GCI probe → PASS), `GATE FAIL`
(5 % offset run → GATE FAIL), and every `NOT A RESULT` cause — STAGNANT triple
(equally-spaced), below-floor p, the GCI ceiling (VMFL063 shape 18.23 %, row-#46
limb-C shape 188.19 %), and absent `RUN_RC.txt` (rc-unknown) — are each exercised.
The instrument is proven to reach more than one answer.

## 3. Controls that ran and passed on the frozen grading path (before any level)

All pre-level controls executed live on the grading path and passed:

- **AST no-assert guard** — live on disk bytes, 10105 AST nodes scanned, 0 asserts.
  Live on the grading path, not only in selftest; the selftest additionally proves
  it FIRES (exit 2) on a planted assert and on an unparseable source. This matters
  because `python3 -O` strips asserts, so the guard reads bytes rather than trusting
  a docstring.
- **Live cross-instrument reference reproduction** — frozen `REF_LAB` (instrument B,
  shooting) reproduced by instrument A (finite-volume Sturm–Liouville) to a **worst
  relative disagreement of 2.383599×10⁻⁶** against `REF_REPRO_TOL = 1.0×10⁻⁵`.
- **Series truncation** — 5.873×10⁻²¹ relative at x = 0.01 m (N = 14 terms).
- **p-floor planted control** — (1.0,1.1,1.2) → NOT A RESULT, no GCI.
- **GCI-ceiling planted control** — a 188.19 % GCI (uncertainty larger than the value
  it qualifies) → NOT A RESULT.
- **Infrastructure-tolerance control (L-342)** — verdict identical with COST.txt
  present and deleted; a broken End line still refuses.

## 4. THE REFUSAL, per level (the operative finding)

The frozen convergence clause (`convergence()`, `grade_vmfl006.py:601`) requires the
last-200-iteration T-residual window to be **both** at/below `RES_FLOOR = 1×10⁻⁹`
**and** not exactly flat (`ptp > 0`, the NULL-RANGE refusal §5 declared). On this run:

| Level | T_initial in last-200 window | Clause outcome |
|---|---|---|
| **L1** | converged to floor **8.874106×10⁻¹⁵** by Time=413; **exactly constant** (distinct=1) for the last ~2587 iters | **REFUSE — NULL RANGE** (operative; grader exits here) |
| **L2** | converged to floor **9.988851×10⁻¹⁵** by Time=1348; exactly constant thereafter | would REFUSE — NULL RANGE |
| **L3** | still descending at endTime: window **1.837×10⁻⁸ … 6.183×10⁻⁸**, distinct=200; max **6.18×10⁻⁸ > RES_FLOOR 1×10⁻⁹** | would REFUSE — above the residual floor |

The grader refused at L1 (the first level in the loop), so L2/L3's convergence, the
station reads, the Roache triple and the planted-zero loop were **never reached on
the graded path**. The two coarse levels converge so hard they hit the double-
precision floor and go flat (NULL RANGE); the fine level has not reached the 1×10⁻⁹
floor within the frozen 3000 iterations (residual-floor refusal). **No level can
simultaneously be below 1×10⁻⁹ and still varying in its last 200 samples** given this
solver's geometric decay to a hard machine floor at fixed endTime — the clause is
jointly unsatisfiable here. This is a **pre-registration defect, not a solve defect**,
and is a candidate for a fixed R2 re-registration of the convergence clause. The
frozen clause is **not edited** (rule 6); the refusal stands as the graded outcome.

## 5. Diagnostic physics — NOT the graded verdict, computed via the frozen readers

To characterise what the frozen path did not reach, the frozen functions
(`read_station`, `roache`, `planted_zero`) were invoked directly on the real level
data (same code, same files; the main path short-circuited at the L1 convergence
refusal). **These numbers decide nothing — the verdict is `NOT A RESULT` above.**

**Ten station θ at L3 (fine), and the per-station relative deviation against the
lab-evaluated exact Graetz reference `REF_LAB` (the gate metric):**

| x (m) | θ_lab (L3) | rel dev vs REF_LAB | manual 4dp (corrob.) |
|---|---|---|---|
| 0.01 | 0.822643449 | 5.619×10⁻⁴ | 0.8225 |
| 0.02 | 0.730702789 | 2.691×10⁻⁴ | 0.7308 |
| 0.03 | 0.659037314 | 6.229×10⁻⁵ | 0.6593 |
| 0.04 | 0.598864830 | 1.151×10⁻⁴ | 0.5992 |
| 0.05 | 0.546547893 | 2.794×10⁻⁴ | 0.5469 |
| 0.06 | 0.500142232 | 4.374×10⁻⁴ | 0.5006 |
| 0.07 | 0.458462780 | 5.920×10⁻⁴ | 0.4589 |
| 0.08 | 0.420724783 | 7.429×10⁻⁴ | 0.4212 |
| 0.09 | 0.386375800 | 8.846×10⁻⁴ | 0.3869 |
| 0.10 | 0.355037679 | 9.162×10⁻⁴ | 0.3555 |

- **Worst station: x = 0.10 m, rel dev 9.162127×10⁻⁴ = 0.09162 %** — every station
  is **inside** the frozen 1 % band (worst is ~10.9× inside).
- Worst |L3 − manual 4dp|/manual = **0.13549 %** — **corroboration only, decides
  nothing** (the gate is `REF_LAB`, never the printed column).
- **Roache triple at x = 0.10 m (`TRIPLE_I = 9`, r = 2.0):** 0.354896103 /
  0.354983201 / 0.355037679; d21 = 8.710×10⁻⁵, d32 = 5.448×10⁻⁵, R = 0.6255 →
  **state CONVERGING, observed order p = 0.6770, GCI_fine = 0.032031 %** — inside the
  frozen `GCI_MAX = 1 %` ceiling.
- **Planted-zero control on the real L1/L2/L3 mixing-cup files** (invoked directly;
  the frozen control code) fires **undiluted at all three levels**: reader_delta =
  **0.001234 = PLANT** at each (|delta − PLANT| ≤ 6.83×10⁻¹⁷). The plant is wired for
  all three levels (proven in selftest) and confirmed on the real data — this is
  **not** the row-#44/#46 L1-only weakness. It simply did not execute on the graded
  path because the convergence refusal preceded the plant loop.
- The characterisation `verdict_for(triple, inside=True)` returns **PASS** — i.e.
  the case would grade PASS but for the frozen convergence clause. This is stated as
  context; it is **not** the verdict and is **not** a credential.

## 6. Cost (rule 12) — MEASURED

The solver ran to completion at every level (rc = 0, End lines, last time == endTime
3000, time dirs {0, 3000}); the grading refusal does not un-run the solver.

| Level | wall s | core-min (RANKS = 1) |
|---|---|---|
| L1 | 5 | 0.0833 |
| L2 | 18 | 0.30 |
| L3 | 75 | 1.25 |
| **Total** | **98** | **1.6333 (MEASURED)** |

Against the registered **EXTRAPOLATED bracket 0.8–8.4 core-min** (midpoint 4.6),
cap 18: **1.633 core-min landed inside the bracket, near the fast end** (1.94× the
fast-end 0.84; 0.194× the slow-end 8.4; **0.355× the midpoint 4.6**). Realised
throughput **2.571×10⁶ cell-steps/s** sits in the assumed 5×10⁵–5×10⁶ window, in its
fast half. **Dollars DERIVED not measured** at $0.0513/core-h: **$0.001396**
(REPORTED-BY-OWNER rate; the box cannot read its own billing). Calibration row filed
to `docs/COST_CALIBRATION.md`.

## 7. The §12 caveat — this verdict may NOT be cited as a clean prediction-first freeze

`PREREGISTRATION.md` §12 records that **git cannot prove `TOL = 0.01` predates the
first VMFL006 field on this box**: the comparator was untracked from 2026-08-26, a
pre-freeze smoke ran 2026-08-26, and the band was first committed 2026-08-31. The
mitigating argument — the smoke's implied θ is **6.8561 %** from the reference,
~6.9 band-widths outside a 1 % band, so a fitted band would have been **wider**, not
tighter — is an **argument from direction, not proof**. Both halves ride the register
row. (Moot for the band in this instance, since the verdict is `NOT A RESULT` and no
PASS credential is claimed, but recorded for completeness.)

---

**Artifacts.** Committed by explicit path: this `RESULTS.md`, the register row, the
calibration row. On disk only (out of git): the solver logs, time directories,
`postProcessing/`, `RUN_RC.txt`, `birth_certificate.json`, `COST.txt` under
`verification/runs/ansys_verification/VMFL006/{L1,L2,L3}/`. No `GRADING_VMFL006.json`
was produced (the frozen comparator refused before writing it).
