# D6RF4 — RESULTS

**Item:** `D6RF4`, A2 wing convergence probe — the `D6RF3` successor that asks one
question with data: *does tightening the linear-solve tolerance bring this A2-wing
case to the registered DAFoam acceptance floor?*
**Registration:** `cases/dafoam/ladder-a/A2/curriculum_D6RF4/PREREGISTRATION.md`,
last committed at `ed809aec` (2026-09-06 18:32:48Z, **before** the 19:00:38Z run),
worktree blob md5 `13168c57b38e530b7e5aae811679264d` (worktree == `HEAD` blob in this
invocation). The pre-registration-committed-before-compute check, and the fixing of the
grading path at the freeze, are the dafoam-supervisor's personal `SUPERVISION_CHARTER.md`
§3 checks and are recorded in the supervisor's grading record, not re-asserted here.
**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe`.
**Log:** `P_conv_20260906T190038Z_83499.log` (98,385 bytes).
**Ran:** 2026-09-06, `P_conv` reached the primal on its **fifth launch**.
**Written:** 2026-09-06, by a `lab-lane` recording numbers the dafoam-supervisor
verified at source and graded and triaged. Every figure below was re-read from the
named artefact in this invocation; where the raw log carries a subtlety the supervisor's
one-line summary does not, it is stated (§2.3), not smoothed.

> ### VERDICT — `NOT A RESULT`
>
> The primal **completed its iterations** — `End` at log `:2118`, `Time = 1000` at
> `:2101`, `ExecutionTime = 57.43 s` at `:2116` — but **failed DAFoam's post-`End`
> acceptance** (ledger `rc=1`) on `cl04.coupling.solver` (`AnalysisError: Primal
> solution failed!`, log `:2257`, `:2258`, `:2325`, `:2392`). This is the **`N-D42`**
> acceptance-refusal mode: `primalMinResTolDiff` is a post-`End` acceptance ratio bar,
> not a solver control. The arm produced **no gradient product** — the registered
> `d6rf4_fd_endpoint.json` is **absent**; only a 138-byte progress
> `d6rf4_fd_endpoint.jsonl` was written — and the **frozen grader correctly REFUSED
> (`REFUSE: G1`)** for want of that product (`d6rf4_grade_stdout.txt`).
>
> **This is a completion, not a failure of the process** (Sanaa, 2026-09-04): the
> solve ran to its iteration budget and printed `End`; the refusal is the acceptance
> bar, read afterwards.
>
> **This is a ONE-ROW `PATCHED` outcome and is NOT a full `DAFOAM_CHARTER.md` §6
> verdict about DAFoam** (§12.6's registered label, carried here verbatim). The row
> bought is `PATCHED`, image `dafoam-idwarp-rot:v1`, digest
> `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`,
> `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425`. No `SHIPPED` row is bought.
>
> **Spend: 5.4 core-min against a 54.0 core-min cap** (10.0 % of cap). The arm
> terminated on an **acceptance failure, NOT a cost overrun** — the cap was never
> approached.

---

## 1. WHAT HAPPENED — THE PRIMAL RAN TO `End` AND WAS REFUSED BY THE ACCEPTANCE BAR AFTERWARDS

The solve completed the full `endTime 1000` and printed `End`. The DAFoam acceptance
refusal came **after** `End`, on the coupling solver — the `N-D42` ordering, read
directly from this run's own log:

| fact | value | artefact |
|---|---|---|
| final outer iteration | `Time = 1000` | log `:2101` |
| `End` | present | log `:2118` |
| final `ExecutionTime` | `57.43 s` (`ClockTime 59 s`) | log `:2116` |
| DAFoam acceptance | **FAILED** — `cl04.coupling.solver ... Primal solution failed!` | log `:2257`, `:2258`, `:2325`, `:2392` |
| ledger row | `ARM=P_conv ROW=PATCHED rc=1 core_min=5.4` | `ledger.txt` |
| gradient product | **ABSENT** (`d6rf4_fd_endpoint.json`); only 138-byte `.jsonl` | `P_conv/` listing |

`primalMinResTol 1e-08` (log `:337`, `:943`, `:1549`) and `primalMinResTolDiff 1000`
(log `:508`, `:1114`, `:1720`) give an effective DAFoam accept floor of
**`1e-08 × 1000 = 1e-05`** (`N-D42`, `N-D43`: the floor is the *product*, not
`primalMinResTol`).

---

## 2. THE MEASUREMENT — THE REACHABLE-TOLERANCE QUESTION, ANSWERED WITH DATA

This is the record's real content. The item exists to test whether tightening the
linear-solve tolerance brings this case under the registered accept floor. It does not.

### 2.1 The accept floor was never touched — verified by a planted control

`ACCEPT_FLOOR_UNMOVED` fired **EXERCISED-PASS** on the container log
(`d6rf4_accept_floor_DRIVE_EVIDENCE.txt`, driven 2026-09-06T02:36:53Z, instrument
`d6rf4_accept_floor_control.py` md5 `2fc0b320affac2397c3bb7301eb9ec35`, exit 0):
`primalMinResTol=1e-08`, `primalMinResTolDiff=1000`, `accept_floor=1e-05`, plant seen
(`reader_saw_the_plant=True`, `occurrences=3/3`, `original_unchanged=True`). Five planted
drifts — including the specific `diff 1000 → 1e12` drift *"that would let D6RF3's own
1.316e-05 through"* — were **REFUSED in both senses**, three blind readers were refused,
and an absent-floor case was refused as `UNMEASURED`. **The floor is UNMOVED at the
registered value; the bar was never widened to fit.**

### 2.2 Tightening `relTol` crushed the inner p-solve ~200× — it worked on the inner solve

Tightening the linear-solve `relTol` (`0.1 → 0.001`, `d6rf4_fvSolution_TIGHT`) drove p's
**corrected (final) p-solve** to `initRes 6.337682167e-08` (log, `Time = 1000`) versus
`D6RF3`'s binding `primalMaxRes 1.316217833e-05` — a factor of **≈ 207×**. The inner
linear solve responded exactly as intended.

### 2.3 But the outer accept floor did NOT drop below `1e-05` — `nuTilda` binds

At the final outer iteration (`Time = 1000`), the per-field initial residuals read:

| field | `initRes` at `Time = 1000` | vs floor `1e-05` |
|---|---|---|
| `U0` | `2.050400149e-07` | well under |
| `U1` | `7.782685238e-07` | well under |
| `U2` | `5.580946633e-08` | well under |
| `he` | `9.791852881e-09` | well under |
| `p` (1st, **uncorrected**) | `1.658293702e-05` | **over** |
| `p` (2nd, **corrected/final**) | `6.337682167e-08` | under |
| `nuTilda` | `1.40915531e-05` | **over** |

`nNonOrthogonalCorrectors 1` gives two p-solves per outer iteration; the **corrected
(final) p-solve is the field's accepted residual (`6.34e-08`, under floor)**, so among
the fields' accepted residuals **`nuTilda` at `1.409e-05` is the binding over-floor
field** — this is the supervisor's graded attribution, and it is consistent with the log.

**Honest flag, stated rather than smoothed (task instruction).** The raw log also
carries the **uncorrected first p-solve `initRes 1.658e-05`, numerically the larger of
the two over-floor `initRes` readings.** It is an intermediate (pre-non-orthogonal-
correction) residual, not p's accepted residual, so it does not change the binding-field
attribution; but a reader scanning `initRes` lines alone would see it and could
mis-attribute the bind to p. Whether DAFoam's internal `primalMaxRes` reads the
uncorrected or the corrected p residual was **not independently reconciled here** (no
recompute) — both over-floor values are recorded so a successor need not re-derive them.

### 2.4 Conclusion, stated plainly

**Tightening the linear-solve tolerance does NOT bring this A2-wing case to the
registered acceptance floor. `nuTilda` binds. The `D6RF3` acceptance refusal is not
fixed this way.** A successor would need a different numerical approach — `nuTilda`'s
own convergence, or more correctors — **NEVER a looser floor, which would be widening a
gate to fit an answer a longer or better-posed run might have delivered honestly**
(`N-D43`; Sanaa 2026-09-04: the case is worked until it passes its gate, and the gate is
never widened). This finding, with the reachable-tolerance question, goes to Sanaa's
desk. This record states it as **the answer, not a proposal to change anything.**

---

## 3. THE `G1`-BEFORE-`G-CONV` ORDERING RULING (supervisor's)

The frozen grader refused at **`G1`** (product absent) before reaching `G-CONV`, and the
ordering is **CORRECT**. `G-CONV`'s registered input is the **central-difference FD
product**, not raw log residuals; grading the residuals when the product is absent would
grade a **different quantity than the one registered**. The per-field residuals of §2 are
therefore the **diagnostic** finding of this run, **not a gate verdict**. A successor
design note — a residual-diagnostic row that *reports-never-gates* the binding field on a
failed primal — may be worth it; that is a successor's question and **is not a change to
D6RF4**.

---

## 4. STRICT COMPLETION AND DAFOAM ACCEPTANCE

The primal satisfies the physical-completion clauses (`End`, `Time = 1000`,
`ExecutionTime` consistent), which is why Sanaa's *"this is a completion, not a failure
of the process"* applies. It fails **DAFoam's post-`End` acceptance** (`rc=1`), which is
an acceptance-rule outcome (`N-D42`), not a statement that the solve did not run. The
item is `NOT A RESULT` because the registered gradient product was never produced and the
gated rows have no input — not because the primal did not finish.

---

## 5. GATES — `G1` REFUSED FOR WANT OF THE REGISTERED PRODUCT

`d6rf4_grade_stdout.txt`:
`REFUSE: G1`, `registered_product_absent =
/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe/P_conv/d6rf4_fd_endpoint.json`,
note *"the producing arm RAN, so an absent product refuses (D6's behaviour, kept)."*
Every downstream gated row (`G-CONV`, the falsifiers) is `NOT A RESULT` for want of that
input.

---

## 6. ONE ROW BOUGHT (`DAFOAM_CHARTER.md` §6, §12.6)

`PATCHED` row bought: image `dafoam-idwarp-rot:v1`, digest
`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`,
`libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425` (`D4S_IDWARP_SO_MD5`, `ledger.txt`).
No `SHIPPED` row is bought. Per §12.6 this is **explicitly NOT a full §6 two-row verdict
about DAFoam.**

---

## 7. COST — SEE THE CALIBRATION LEDGER

Ledger actual **5.4 core-min** (`ledger.txt`: `container_wall_s=75`,
`delivered_cores_mean=3.3475` of 4, `max_nr_throttled=220` — a small contention factor),
against a registered estimate of `17.90` core-min and a cap of `54.00`. **Only `L1` (the
tightened primal) ran**; the arm died at `L1`'s failed acceptance, so `L2`
(`baseline_repeat`) and `L3` (`F5`, the original-`fvSolution` falsifier) **did not run**.
The full estimate-vs-actual comparison, and the reason the registered **`×6` multiplier
cannot be calibrated from this run**, are filed as one row in `docs/COST_CALIBRATION.md`.
`cost_basis`: core-minutes **MEASURED** from this item's own ledger; dollars **DERIVED**
at $0.0513/core-h (c7a.4xlarge, reported-by-owner — the box cannot read its own billing,
`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 8. WHAT A SUCCESSOR IS OWED, AND WHAT IT MAY NOT DO

- **Owed:** an approach that converges `nuTilda` (and, if it recurs, the uncorrected
  first p-solve) under `1e-05` at this case's `endTime` — `nuTilda`'s own solver
  settings, or more non-orthogonal correctors — measured, not assumed.
- **Owed:** the `L3`/`×6` calibration leg, which this run could not buy (§7).
- **May NOT:** loosen the accept floor (`primalMinResTol × primalMinResTolDiff`) to admit
  this endpoint. `N-D43`: the floor is a product of two per-case settings, and widening
  it to fit is not permitted.
- **May NOT:** carry `primalMinResTolDiff = 1000` to a different case family — it is
  `100` on the S1 CBFS family (`N-D43 CORRECTION`, 2026-09-06).

---

## AMENDMENT — 2026-09-06T23:11:56Z — **§2.3's OPEN QUESTION RESOLVED: THE BINDING FIELD IS p's UNCORRECTED FIRST SOLVE, NOT nuTilda. And the failure is RECOVERABLE by sourced fixes — capability gap NOT proven (SANAA-DIRECT 4ae4b33).**

**§2.3 left open which field `primalMaxRes` reads. RESOLVED, verified by the supervisor at source:** the log's `Primal min residual 1.658293702e-05` (`:2121`) is **byte-identical to `p`'s uncorrected first-solve `initRes`** (`:2107`) — so the max-over-states DAFoam refused on is **`p`'s first solve at 1.66× the 1e-5 floor, NOT `nuTilda`** (1.409e-5, 1.41× — a genuine SECOND over-floor field, but not the binding one). My prior boards said "nuTilda binds"; the correct statement is **p's first solve is the binding (max) field; nuTilda is a real second.** Both are nonlinear steady-state plateaus (the linear solves reach 1e-8/1e-9). **Mechanistic cause, sourced:** the mesh's max non-orthogonality **71.48 exceeds DAFoam's own default `maxNonOrth: 70`** (in this log at `:217/:275/:578`), and the p first-solve floor IS the magnitude of the explicit non-orthogonal correction term.

**UNDER SANAA'S LAW: RECOVERABLE by named, sourced fixes — capability gap NOT proven.** Full analysis and citations: `docs/dafoam/D6RF4_CONVERGENCE_RESEARCH.md` (`1586fcf9`). Ranked, all to a **D6RF5 successor** (never a D6RF4 edit — gates closed by first compute): (1) `limited corrected 0.333` on laplacian+snGrad — caps the explicit correction that IS the binding residual; (2) `nNonOrthogonalCorrectors 1→3` (caveat: the bind is the FIRST p-solve, so measure, don't assume); (3) nuTilda under-relaxation for the second field; (4) bounded upwind div; then (7) re-mesh <70. **The accept floor stays 1e-5.**

**⚠ DAFoam's OWN documented remedy for "Primal solution failed" is to raise `primalMinResTol`/`primalMinResTolDiff` — i.e. WIDEN the accept floor, which the lab FORBIDS (N-D43). The stock fix is off-limits; the fix must be the numerics/mesh, which the ranked list supplies.** **A capability-gap claim would require RANK 1 + RANK 2 + a re-mesh below ~40° to STILL fail 1e-5, filed with that measurement; that proof does not exist today** — so this is a waypoint owing D6RF5, not a gap.

**SUBMISSIONS PARKED.**
