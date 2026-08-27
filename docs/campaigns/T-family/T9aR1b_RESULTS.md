# T9a-R1b (`W1b`) results — layered 1-D conduction, HARMONIC interface scheme, interface temperature

Graded 2026-08-27 by the frozen comparator at three levels.
**RUNG VERDICT: `PASS` — one of one GRADED row PASS.**

**The census is over GRADED rows only (D534).** `R0` (`q_hot`) is a **`REPORTED`
row class, not a verdict**, and is excluded from the tally and named here rather
than absorbed into it.

Pre-registration: `docs/campaigns/T-family/T9aR1b_PREREGISTRATION.md`.
Run root: `verification/runs/T-family/T9aR1b_runs/`.
Comparator stdout at `verification/runs/T-family/T9aR1b_runs/log.analyse_t9aR1b.20260827T164837Z.txt`;
machine record at `verification/runs/T-family/T9aR1b_runs/gate_t9aR1b.json`.

---

## 1. The freeze set — five of five MATCH on both channels

`build_t9aR1b.py` `ef589866` / `817f42719b70afc0`; `analyse_t9aR1b.py`
`fd6c43a0` / `735a8690208a50f4`; `mark_done_t9aR1b.py` `68c78731` /
`67a3b8fc9da612aa`; `run_one_t9aR1b.sh` `d7990722` / `031e6e045604ef50`;
`T9aR1b_registered.json` `cfe867c6` / `6da0bebc54dd844f`. **No drift. No frozen
file edited.** `__pycache__` cleared before the run.

## 2. Completion — three of three

`mark_done_t9aR1b.py`: **`DONE W1b_c`, `DONE W1b_m`, `DONE W1b_f`**, rc 0.
All three `STATUS.*` read `rc=0 … capped=no checkmesh_rc=0 note=clean`.

**`wall_s=0` on all three arms, and that is real, not a broken record.** These are
35-, 56- and 90-cell 1-D cases: the solver's own `ExecutionTime` reads
**0.05 s / 0.05 s / 0.06 s**, below the launcher's one-second wall resolution.
Each log carries **1 000 `ExecutionTime` lines against `endTime` 1000**, an `End`
line, and a last written time of 1000. The run is complete; it is merely faster
than the clock that timed it. See §6.

## 3. A LATENT INSTRUMENT DEFECT, REPORTED AND NOT REPAIRED

`mark_done_t9aR1b.py` is **derived from T14's**, and it inherits T14's L-342 class
declaration verbatim (`:14-15`): *"PHYSICS-CRITICAL: rc, End, last time, field
present, **ExecutionTime count**, the age guard."* The verification team's
`docs/L342_GRADER_AUDIT.md` classifies a refusal keyed on the `ExecutionTime`
line count as **CONFLATED — MISCLASSIFIED**, on the ground that the count records
bookkeeping rather than whether the solve completed.

**It did not fire on this rung, and that is stated as a measurement, not a
reassurance:** the count is **1 000 against an expected 1 000 on every arm**, so
the clause passed on its own merits and no verdict here rests on the
classification. **The defect is latent, not triggered.** It is **not repaired**:
the rung has fired, the file is frozen, and §2d.1 is not this lane's route. The
tension is genuine and sits above this lane — `CLAUDE.md` rule 4 itself lists
*"`ExecutionTime` count == `endTime`"* among the strict completion conjuncts,
while the audit classifies it as infrastructure. **Referred to the verification
supervisor.**

The registration's own infrastructure list is applied correctly and was driven:
`wall_s, timeout_s, ranks, core_min, capped, checkmesh_rc, solver, solver_path,
note, started_utc, ended_utc` — absent → NOTE, grade proceeds.

## 4. Controls

- **`C_CONV`** (checkpoint form, L-140/L-141): the last two written checkpoints
  (900, 1000) agree in `T` to 1e-09 K. Measured **move 0.000e+00 K on every
  level** — checkpoint-converged True, c/m/f.
- **`C_MAP`**, **`C_SCHEME`**, **`C_REF`**: all passed (the comparator exits 2 on
  any of them; it did not). `C_SCHEME` is the one that matters for this rung's
  identity — it requires the **harmonic** interface line in `CASE.txt` and
  `system/fvSchemes` on disk and **refuses the parent's linear line**.
- **Referent** `q = 19.502682 W/m²`, `T_i1 = 348.781082399 K`, derived and
  **cross-checked against T9a's registered values**.
- **`C_PZ` planted-zero (rule 3): PASS.** Plant 1.234e-03 K into **cell 25, the
  cell adjacent to interface 1 — the point reader's own station**; recovered
  **1.17632e-03 K**, floor 1e-07. The plant is placed where the reader actually
  looks, which is the only placement that tests this reader.

## 5. THE GRADED ROW — and its triple is `EXACT`, which needs stating plainly

| row | c | m | f | exact | deviation | band | triple | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| **R1** `T_i1` | 348.781082399 | 348.781082399 | 348.781082399 | 348.781082399 | **2.899e-12 K** | **1.000e-06 K** (absolute floor) | **EXACT** | **PASS** |

**Standing rule 5 (2) names `EXACT` among the states that make a row
`NOT A RESULT`. This row is graded `PASS` instead, under a rule registered
BEFORE compute, and the ground is a TIGHTENING rather than a loosening.** The
pre-registration (§2) sets it out: a triple whose level differences are both
below the round-off floor 1e-09 K is EXACT; **an EXACT triple is then graded by
the absolute floor `|T_i1 − exact| ≤ 1e-06 K`** — about **1 000× the measured
round-off and 900× TIGHTER than T9a's R1 band of 0.92 mK** — and the document
says in terms **"No band is widened."** Any other non-CONVERGING state still
routes to `NOT A RESULT` with `p` printed and the GCI refused.

The physics is why the triple is exact: with the **harmonic** interface
conductivity, the discrete interface temperature in layered 1-D conduction is
**mesh-independent by construction**, so all three levels return the same value
to 12 significant figures. A grid-refinement study cannot show convergence in a
quantity that has nothing to converge from. The measured deviation is
**2.899e-12 K — six orders of magnitude inside the registered floor.**

**FLAGGED FOR THE VERIFICATION SUPERVISOR, and this is the SECOND such row this
lane has graded today** (T13's `G2`/`G3` are registered `exact_class` rows on the
same structural pattern: a degenerate triple graded by a pre-registered absolute
floor with a stated physical ground). **This lane reports the verdict the frozen
instrument produced and does not override it; whether standing rule 5 (2) should
carry a registered-floor exception for provably-degenerate triples is a
standing-rule question above this lane, and it is now recurring.**

## 6. `R0` — `REPORTED`, not graded (D534)

`q_hot` relative deviation: **c +5.920e-14, m +3.417e-12, f +3.044e-12.**
**Excluded from the verdict census.** It is recorded because P3 predicted it and
because it carries the rung's point: the parent T9a's **1.8 % linear-scheme
excess has vanished** under the harmonic scheme, to within 3e-12 relative.

## 7. Predictions — three HIT, one not triggered

- **P1 — HIT.** *"The R1 triple is EXACT to round-off: |e21|, |e32| < 1e-09 K."*
  All three levels identical; triple `EXACT`.
- **P2 — HIT.** *"|T_i1 − 348.781082399| < 1e-09 K on every level → PASS by the
  floor."* Measured **2.899e-12 K**.
- **P3 — HIT.** *"R0 `q` within 1e-09 relative on every level."* Worst
  **3.417e-12**.
- **P4 — NOT TRIGGERED, and not scored either way.** It was the conditional
  alternative *"if instead the triple is CONVERGING…"*. The triple was EXACT, so
  the branch never opened. **A conditional whose antecedent is false is not a
  hit**, and it is not counted as one.

## 8. Cost — rule 12, and the registered basis reads ZERO

- **Predicted: 0.0045 core-min** (0.0015 per level); cap total **3**.
- **Measured on the registered basis: 0.000 core-min.** `core_min = wall_s ×
  ranks ÷ 60` and all three `wall_s` are **0** — the runs are shorter than the
  launcher's one-second resolution.
- **THE RATIO IS THEREFORE UNDEFINED ON THE REGISTERED BASIS, AND NO RATIO IS
  INVENTED.** 0.000/0.0045 = 0.000 is an artefact of measurement granularity, not
  a calibration result, and reporting it as a 0.000 ratio would put a false
  perfect-underspend into the ledger.
- **The only usable actual is the solver's own `ExecutionTime`: 0.05 + 0.05 +
  0.06 = 0.16 s → 0.002667 core-min**, giving **0.593 against the POINT — stated
  as a DIFFERENT BASIS, not as the registered one.** `ExecutionTime` excludes
  process start-up and I/O that wall time includes, so it is a lower bound on the
  true spend.
- **Gross = cleaned.** Nothing near the 3 600 wall-s stall figure. **WASTE:
  0.000 core-min.** No arm approached its cap (3 core-min total registered).
- **The transferable finding: the lab's measured unit has a floor.** Below about
  one wall-second per case the registered core-minute basis cannot resolve the
  spend and returns zero, and a zero here means *"too small to measure"*, **not
  *"free"***. A rung of this size should either register `ExecutionTime` as its
  cost basis up front or accept that its calibration row carries no ratio. **This
  row carries no ratio on the registered basis, deliberately.**
- **Dollars, DERIVED, NOT MEASURED** at $0.0513/core-h: **$0.0000023** on the
  `ExecutionTime` basis; **$0.0000038** predicted. Both are effectively zero and
  are recorded for completeness, not as a budget statement.
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit from the tail.

## 9. Disclosures

- **The verdict rests on ONE graded row.** `R0` is REPORTED and excluded (D534).
- **The R1 triple is EXACT**, so this rung provides **no grid-convergence
  evidence** — it provides an exactness demonstration against a cross-checked
  referent. Anyone citing T9a-R1b as a Roache verification would be overstating
  it, and §5 says why the triple cannot be otherwise.
- **A latent CONFLATED clause sits in the frozen completion checker** (§3); it did
  not fire and was not repaired.
- No frozen file edited (rule 6). **Nothing sent, filed, uploaded, posted or
  registered outside this box** (rule 7).
