# T23G2Rn — PRE-REGISTRATION (DRAFT). §2ba NUMERICS SUCCESSOR TO T23G2R's G-CONV GATE FAIL

Predecessor: T23G2R (NOT A RESULT — G-CONV p_rgh floor-pinned at the 1e-8 linear-solver tolerance), verification/runs/T-family/T23G2R_runs/T23G2R_RUNG_VERDICT.txt

> ## FROZEN — two-commit freeze, heat-transfer supervisor, 2026-09-09. NO SOLVER LAUNCHED YET.
> The supervisor's §3 measurement-script diff-read of `build_t23g2rn.py`,
> `analyse_t23g2rn.py` and the completion wrapper `mark_done_t23g2rn.py` is DONE
> (all sound; the comparator's grading logic is byte-identical to frozen
> `analyse_t23g2r.py`, only identity constants differ; the build edit is proved
> p_rgh-block-local and value-local). This registration and its scripts are frozen
> by the **two-commit freeze** (commit 1/2 carries this prereg + the three scripts
> with `GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"`; commit 2/2 sets
> `GRADING_PATH_FREEZE_COMMIT` to commit 1/2's sha). The comparator SELF member is
> anchored per `VERIFICATION_CHARTER.md` §2au.2: `EXPECTED_SELF_BLOB = None`
> (print-only), the authoritative blob recorded by the `FREEZE-PIN:
> analyse_t23g2rn.py@<blob>` line in the **commit 2/2 message**, and grade-time
> byte-identity of the on-disk comparator against that recorded blob. Every number
> below the "reused gates" line is a **DESIGN ESTIMATE** except where it quotes a
> MEASURED predecessor artifact, each labelled as such. **STILL OWED before the
> graded launch (personal check 4): the §5.3 pre-flight gate (incl. the on-disk
> p_rgh `tolerance 1e-10` / `relTol 0` assertion) and the §7 autograder arming — no
> solver launches until both are in place.**

---

## 0. §2ba LINEAGE — a numerics fix, no gate change

**Predecessor: `T23G2R` (explicit, for §2ba linkage).** This registration is the
active, dated **numerics** fix-successor to **T23G2R**'s **`G-CONV` `GATE FAIL`**.
Under `VERIFICATION_CHARTER.md` §2ba this is a *fix-until-runs numerics change*: it
alters a **linear-solver stopping tolerance only** — no gate, threshold, band, cap,
label or directive is created, moved or retired. It is within-lab authority and
under the $25/run pre-authorisation (CLAUDE.md rule 12).

**T23G2R keeps its `NOT A RESULT` verdict** (`§2an.2`). This linkage **moves no
verdict** and **creates no gate, threshold, band, cap or label of its own; it reuses
T23G2R's**, which are themselves reused verbatim from frozen T23G2. The one net-new
item T23G2R already carried (the prospective `R6` refusal) is inherited unchanged and
can only add a refusal.

**Scope boundary, stated plainly.** T23G2R was `NOT A RESULT` because `G-CONV` failed
on L2 and L3 (`T23G2R_RUNG_VERDICT.txt:19`, verbatim `G-CONV: GATE FAIL`), which then
voided the Roache triple (rule 5 step (a)) and so drove `G-RATIO` and `G-ORDER` to
`NOT A RESULT` as well (`:23-35`). `G-MESHSIM` PASSED and `G-YPLUS` PASSED
(`:17,:21`) — **T23G2R's near-wall fix worked and is not disturbed here.** The single
change below is aimed at the ONE gate that failed, `G-CONV`, and at its measured
cause. If the now-descending residual lets the triple grade, the previously-voided
`G-RATIO`/`G-ORDER` cells become live again — that is registered as an open outcome
(§4), not a gate change.

---

## 1. THE DIAGNOSIS — p_rgh floor-pins at the linear-solver tolerance, which EQUALS the gate

**The failure is a numerics artefact: the p_rgh outer (initial) residual cannot
descend below ~1e-8 because the GAMG linear solver's own `tolerance` (1e-8) EQUALS
the `G-CONV` convergence gate (1e-8).** Confirmed from the frozen T23G2R record
without re-running anything:

1. **G-CONV failed on L2/L3 by a hair, at the gate value.** The T23G2R comparator
   read final p_rgh initial residuals of **1.208e-08 (L2)** and **1.036e-08 (L3)**,
   both just above the reused `≤ 1e-8` gate; L1 CONVERGED
   (`verification/runs/T-family/T23G2R_runs/T23G2R_COMPARATOR_STDOUT.txt:61-64`,
   verbatim `T23G2R_L2 NOT CONVERGED worst asserted: p_rgh 1.208e-08` /
   `T23G2R_L3 NOT CONVERGED worst asserted: p_rgh 1.036e-08`). All other asserted
   residuals (`h Uy Uz k omega`) were within tolerance.

2. **The residual floor-pins, it does not fail to descend from lack of iterations.**
   In `verification/runs/T-family/T23G2R_runs/T23G2R_L2/log.solve` the p_rgh initial
   residual descends normally (0.999993 → 1.75e-4 → 2.25e-5 → 4.62e-6 → 7.51e-7 →
   1.94e-8 by iter ~2400) and then, once it reaches the ~1e-8 neighbourhood, the
   GAMG solver reports **`Final residual = Initial residual, No Iterations 0`** — it
   performs **zero** linear iterations because the residual is **already at its own
   1e-8 `tolerance`**. From roughly iter ~2480 (L2) / ~5749 (L3) onward the outer
   initial residual **flat-oscillates in ≈ 0.9–1.3e-8** with `No Iterations 0` or
   `1`, and the last three L2 samples are 1.288e-08 / 1.283e-08 / 1.208e-08 — it
   never settles below the 1e-8 gate (same artifact, `Solving for p_rgh` lines).

3. **The cause is `tolerance == gate`.** `docs/campaigns/T-family/build_t23g2r.py`
   lines 817-823 set the p_rgh GAMG block `tolerance 1e-08; relTol 0.01;`. The
   comparator's `G-CONV` gate is `p_rgh ≤ 1e-8`
   (`docs/campaigns/T-family/analyse_t23g2r.py:113`, `RESID_TOL["p_rgh"] = 1.0e-8`).
   When the linear-solve tolerance equals the convergence gate, the linear solver
   **stops reducing p_rgh the instant its residual crosses 1e-8**, so the next outer
   iteration's initial residual bounces back up to ~1e-8 and the gate can never be
   met. This is a numerics-configuration defect, not a physical non-convergence.

4. **"More iterations" is contraindicated.** The residual is flat-oscillating at the
   floor by iter ~2500 (L2); the run already spends 16,000 (L2) / 28,000 (L3) outer
   iterations. Adding iterations cannot move a floor set by the linear tolerance.
   The fix is to lower the linear floor **below** the gate so the linear solver keeps
   reducing p_rgh; the outer initial residual can then descend below 1e-8.

**Verdict of the diagnosis: drop the linear floor two decades below the gate.** This
is the textbook repair for a residual pinned at its linear-solver tolerance.

---

## 2. THE CHANGE — the ONLY change: the p_rgh linear-solver floor, dropped below the gate

### 2.1 The single edit (`system/fluid/fvSolution`, p_rgh block, all three levels identically)

| p_rgh key | T23G2R (frozen) | **T23G2Rn (proposed)** |
|---|---|---|
| `tolerance` | `1e-08` | **`1e-10`** (two decades below the 1e-8 gate) |
| `relTol` | `0.01` | **`0`** (absolute floor governs; no early relative exit) |
| `solver` | `GAMG` | **`GAMG` — UNCHANGED** |
| `smoother` | `GaussSeidel` | **`GaussSeidel` — UNCHANGED** |

`relTol 0` removes the relative early-exit so the absolute `tolerance 1e-10` is the
binding stop, guaranteeing the linear solver drives p_rgh well below the 1e-8 gate
each outer iteration. All three levels (`T23G2Rn_L1/L2/L3`) take the identical p_rgh
block and are **all re-run**, so the Roache triple is graded on a consistent numerics
configuration.

### 2.2 What is held BYTE-INVARIANT from T23G2R

Everything else. Re-asserted, not assumed: the **mesh** (T23G2R's near-wall
first-cell heights `1.080000e-05 / 7.200000e-06 / 4.800000e-06 m` inner band and
`7.750800e-06 / 5.167200e-06 / 3.444800e-06 m` outer band; cell counts
`40,320 / 90,720 / 204,120`; 2.25 similarity), the **endTimes** `8000 / 16000 /
28000` (UNCHANGED — the fix is the linear floor, not the iteration budget; "more
iterations" is contraindicated per §1.4), geometry, operating point, properties,
turbulence model, wall treatment, the conjugate interface, all schemes, `ranks = 1`,
and — crucially — **every OTHER solver block**: `rho` (PCG, tol 1e-8, relTol 0),
`"(U|h|k|omega)"` (PBiCGStab, tol 1e-9, relTol 0.01), the solid `h` solver, the
`SIMPLE` block (no `residualControl`), and **all `relaxationFactors`** (p_rgh 0.3,
rho 1, U/h/(k|omega) 0.7). The build script `build_t23g2rn.py` **REFUSES (exit
non-zero) if any non-p_rgh dictionary differs** from what `build_t23g2r.py` produces
(§5). Any file that differs and is not the p_rgh block is a REFUSAL, not a note.

---

## 3. THE REUSED GATES — VERBATIM FROM T23G2R (which reuses T23G2's), NONE RELAXED

**Every gate, threshold and band below is reused BYTE-FOR-INTENT from the frozen
T23G2R comparator (`analyse_t23g2r.py`), which reuses T23G2's. Not one is relaxed.
The successor freezes these before it re-runs (prediction-first).**

- **`G-CONV` (the failing gate) — REUSED UNCHANGED:** at `endTime`, on every level,
  **`h` ≤ 1e-9** and `Uy Uz p_rgh k omega` initial residual **≤ 1e-8** at the last
  iteration; `Ux` excluded with the exclusion itself measured per level
  (`analyse_t23g2r.py:112-114`, `RESID_TOL`). **The 1e-8 p_rgh threshold is NOT
  moved.** The change (§2) lowers the *linear-solver* floor to 1e-10 so the run can
  MEET the frozen 1e-8 gate; the gate value is untouched (rule 2).
- **`G-MESHSIM` — REUSED UNCHANGED:** cell-count ratio exactly **2.250000** per
  region; first-cell height ratio **1.500 ± 0.005**; per-cell growth **≤ 1.25**;
  housing wall cells **≥ 8** at the coarsest level (`analyse_t23g2r.py:129-133`).
- **`G-YPLUS` — REUSED UNCHANGED:** max y+ ≤ **1.0** on EVERY wall patch, EVERY level;
  two instruments agreeing within 2 %, both planted (`:124-126`); the prospective
  `R6` refusal (absent primary log ⇒ REFUSE) inherited from T23G2R
  (`analyse_t23g2r.py:786-799`).
- **Roache triple gating — REUSED UNCHANGED:** `Fs = 1.25`, `scripts/roache_triple.py`
  under CLAUDE.md rule 5 ordering — any level not iteratively converged/plateaued →
  `NOT A RESULT`; a non-`CONVERGING` triple → `NOT A RESULT` with values, both
  triples and orders printed; `CONVERGING` → `PASS` inside band else `GATE FAIL`.
- **`G-ORDER` band — REUSED UNCHANGED:** p(`Q4`) in **[0.5, 1.5]**
  (`analyse_t23g2r.py:81`), with the `R7`/`R3` repair in place.
- **`Q3` / band-transfer — REUSED UNCHANGED:** ΔT = T − 288.0 K in **[46.0, 56.0] K**
  transferred to Q1/Q3/Q2 (`:86,:109`). **The band is NOT moved.**
- **The six graded quantities and roles — REUSED UNCHANGED:** Q4 core vol-avg T
  (PRIMARY ORDER), Q5 housing surface heat flux (REPORTED, NEVER GATED), Q1, Q3, Q2,
  Q6 (`analyse_t23g2r.py:938-961`).
- **Planted-zero controls — REUSED UNCHANGED:** 6 quantities × 3 levels + 2 y+
  readers = **20**, each asserted by `RT.assert_plant_control` (`R5` retained),
  refusing on a control that cannot read its plant back (rule 3).

**No gate value, threshold or band above differs from T23G2R by any amount. The only
change is the p_rgh linear-solver tolerance/relTol (§2.1).**

---

## 4. PREDICTIONS — prediction-first, frozen before the re-run

DESIGN ESTIMATES.

| id | prediction | basis |
|---|---|---|
| **P-CONV** | with the linear floor at 1e-10, the p_rgh outer (initial) residual descends **below 1e-8 on ALL three levels** at the unchanged endTimes → **`G-CONV` PASS** | the residual was pinned at the linear tolerance, not at a physical plateau; L1 already CONVERGED at 1e-8 with headroom |
| **P-TRIP** | with all three levels iteratively converged, rule 5 step (a) no longer voids the triple → the Roache triple becomes **gradeable** (CONVERGING / non-CONVERGING per the values), and `G-RATIO`/`G-ORDER` become live cells again | T23G2R's NOT A RESULT on those cells was a downstream consequence of G-CONV, `T23G2R_RUNG_VERDICT.txt:23-35` |
| **P-YM** | y+ and mesh are unchanged by a linear-solver-tolerance edit → **`G-YPLUS` PASS, `G-MESHSIM` PASS** carry over from T23G2R | the mesh and endTimes are byte-invariant (§2.2); §2 touches no field or geometry |

**Registered loss modes (honest, not waved).**
- **P-CONV can lose.** The p_rgh residual could floor at a **physical plateau above
  1e-8** (e.g. a genuine steady-state limit-cycle in this conjugate coupling) rather
  than at the linear tolerance. If it does, `G-CONV` `GATE FAIL` again, the rung stays
  `NOT A RESULT`, and **a further successor is owed** — reported as exactly that.
- **P-TRIP can lose the rung a different way.** If the now-gradeable triple lands
  **out of band** (`G-ORDER` outside [0.5, 1.5], or `Q1/Q3/Q2` fine value outside
  [46.0, 56.0] K, or a non-CONVERGING triple), that is a `GATE FAIL` / `NOT A RESULT`
  reported as such. Making the triple *gradeable* is not the same as making it
  *pass*; the change removes a numerics artefact, it does not steer any value.

---

## 5. THE SCRIPTS + THE COMPLETION-INSTRUMENT DECISION (supervisor's)

Written by this draft (NOT sha-frozen; the §3 diff-read and freeze are the
supervisor's):

1. **`docs/campaigns/T-family/build_t23g2rn.py`** — a parametric edit of
   `build_t23g2r.py` that imports it and overrides ONLY the p_rgh block in
   `FLUID_SOLUTION` (`tolerance 1e-10`, `relTol 0`). It **prints the p_rgh block it
   writes** and **REFUSES (exit non-zero) if any non-p_rgh dictionary differs** from
   what `build_t23g2r.py` produces (every other file is `build_t23g2r`'s own output,
   verbatim; the p_rgh delta is proved block-local by a split/whitespace-robust
   check). See §2.
2. **`docs/campaigns/T-family/analyse_t23g2rn.py`** — the comparator, grading LOGIC
   byte-identical to frozen `analyse_t23g2r.py`; the ONLY differences are the
   case-name/path constants (`T23G2R`→`T23G2Rn`, `RUNS`, `LEVELS`, `ENDTIME`, `CELLS`,
   `SELF_REL`, `GRADING_PATH`) and the self-freeze machinery
   (`GRADING_PATH_FREEZE_COMMIT = "PIN-AT-FREEZE"`, `EXPECTED_SELF_BLOB = None`), so
   the DRAFT guard REFUSES to grade until the supervisor pins the freeze commit.
3. **Reused unchanged, on the grading path:** `scripts/roache_triple.py`,
   `docs/campaigns/T-family/t23g_readonly_diagnosis.py`, and the rule-4 completion
   instrument — see §5.1.

### 5.1 The rule-4 completion instrument — OPTION (b) CHOSEN by the supervisor (2026-09-09)

**DECISION (heat-transfer supervisor, 2026-09-09): OPTION (b).** The frozen
`mark_done_t23.py` blob `982e1db6` stays **byte-invariant** — no frozen-file edit.
A thin wrapper `verification/runs/T-family/T23_runs/mark_done_t23g2rn.py` was
authored: it **imports** `mark_done_t23` and reuses its six-clause logic verbatim
(no copy, no drift), widening only the **in-memory** `CASES` to add
`T23G2Rn_L1/L2/L3`. `analyse_t23g2rn.py`'s `require_done()` target and the `mark_done`
member of `GRADING_PATH` are re-pointed to the wrapper (§5 return diff). The
options as originally assessed are retained below for the record.

The comparator delegates rule-4 completion to a `mark_done` instrument by subprocess,
called with the level names. `verification/runs/T-family/T23_runs/mark_done_t23.py`
(frozen, on-disk blob **`982e1db6622454c2e5cc3e9eb4d6811e87735b78`**) whitelists case
names in its `CASES` tuple and **REFUSES (exit 2)** any name absent.
`T23G2Rn_L1/L2/L3` are **not** in it. Two ways to make completion evaluable, **both
insertion-only, six clauses untouched, fail-closed**; the choice is the supervisor's
§3 call (this lane does NOT pick):

- **(a) ADDITIVE rule-14 insertion** of `T23G2Rn_L1/L2/L3` into `mark_done_t23.py`'s
  `CASES` — the exact pattern by which `T23G2_L*` (v1.2 amendment) and `T23G2R_L*`
  (v1.3 amendment) were added. Insertion-only on line 95 plus a dated v1.4 amendment
  block; the six clauses, `NEEDED`, `AGE_REF`, `CASES[0]` and `--selftest` untouched.
  **This changes the frozen instrument's working-tree blob** `982e1db6` → a new blob.
  Impact on the pins that reference `982e1db6` (§5.2): all resolve to immutable git
  history and are **not broken**; only a *hypothetical re-run* of the already-closed
  T23G2R comparator would print `DIFFERS` in its print-only, non-refusing R2 recorder.
  Under (a) the comparator's `require_done()` and its `GRADING_PATH` entry stay
  byte-identical (they already call `mark_done_t23.py`).
- **(b) SEPARATE thin instrument** (e.g. `mark_done_t23g2rn.py`) that `import`s
  `mark_done_t23` and reuses its `check`/`run`/`NEEDED`/`AGE_REF`/six-clause logic
  verbatim, widening only an **in-memory** `CASES` for the three new names. This keeps
  `mark_done_t23.py`'s bytes — and blob `982e1db6` — **exactly invariant**; no pin
  shifts even hypothetically. Cost: one new small file, and `analyse_t23g2rn.py`'s
  `require_done()` target + one `GRADING_PATH` entry re-point to the thin instrument
  (a localized 2-line change the supervisor applies at freeze).

**Chosen: (b).** The comparator's `require_done()` and `GRADING_PATH` mark_done
member now name `mark_done_t23g2rn.py`; every clause that grades still lives in
`mark_done_t23.py @982e1db6`, reached by import. (R2-provenance note for the
supervisor's re-read: the wrapper's blob is recorded by the R2 recorder, and the
wrapper's source names the base it imports; if the supervisor wants the base blob
`982e1db6` recorded on the comparator's face as well, add
`"verification/runs/T-family/T23_runs/mark_done_t23.py",` back as an ADDITIONAL
`GRADING_PATH` member alongside the wrapper — one added line, no logic change.)

### 5.3 PRE-FLIGHT GATE — the p_rgh-value assertion (supervisor directive, 2026-09-09)

Before the graded launch, the §5.1-referenced pre-flight (function objects shown to
construct in a scratch copy of a **built** case, **no graded artifact written**) is
strengthened with an **EXPLICIT numerics gate**: after the scratch build, grep the
**written** `system/fluid/fvSolution` and assert the p_rgh block reads
**`tolerance 1e-10`** and **`relTol 0`** (and that `solver GAMG`/`smoother
GaussSeidel` are unchanged). **The graded launch is REFUSED until this assertion
passes on a real built case.** This guards the specific risk that
`build_t23g2rn.py`'s `B.FLUID_SOLUTION = modified` module-global override might not
reach disk if `build_t23g2r.main()` did not read the global at write-time — the
assertion is read off the *written file*, not off the in-memory string, so a silent
non-propagation is caught before any solver iterates. (The build script also prints
the p_rgh block it writes and refuses on any non-p_rgh dictionary difference, §2.2;
this gate is the independent on-disk confirmation.)

### 5.2 Pins that reference `mark_done_t23.py @ 982e1db6` (for the supervisor's judgement)

Grepped 2026-09-09; all resolve the blob via the T23G2R freeze commit
`043ddce7…` (`git rev-parse 043ddce7:…/mark_done_t23.py` = `982e1db6…`, immutable):

- `docs/campaigns/T-family/T23G2R_PREREGISTRATION.md:417` (§10.1 freeze table),
  `:493`, `:500` — the FROZEN T23G2R pre-registration pinning the blob.
- `verification/runs/T-family/T23G2R_runs/T23G2R_COMPARATOR_STDOUT.txt:21-22` — the
  T23G2R R2 recorder output at grade time (post-repair AND frozen columns both
  `982e1db6…`, marked `IDENTICAL`).
- `verification/runs/T-family/T23G2R_runs/T23G2R_RUNG_VERDICT.txt:6` — `mark_done_pin
  : 982e1db6`.

None is broken by option (a): the pre-registration pin and the comparator's frozen
rev-parse both read immutable history; the two run-artifact files are fossils of a
closed rung. This is the same situation T23G2R itself created when it extended the
blob `37165979 → 982e1db6` (its own v1.3 amendment + a supervisor re-pin), so precedent
exists. Option (b) sidesteps it entirely.

---

## 6. COST — rule 12, POINT + CAP in core-minutes, cost_basis honest

**`cost_basis = REPORTED-BY-OWNER`:** the rate is owner-stated ($0.0513/core-h,
2026-08-21/22) and the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure here is a measurement. Basis:
T23G2R's **MEASURED** per-level actuals (`ranks = 1`) scaled by a **×1.15 ASSUMED**
per-iteration uplift (`relTol 0` → more GAMG V-cycles per outer iteration) for POINT,
and a **CAP at ×1.35** of the predecessor actual.

| level | cells | `endTime` | predecessor actual [core-min] | **POINT** (×1.15) | **CAP** (×1.35) | timeout [s] |
|---|---|---|---|---|---|---|
| `T23G2Rn_L1` | 40,320 | 8,000 | 26.07 | **29.98** | **35.19** | 2,111 |
| `T23G2Rn_L2` | 90,720 | 16,000 | 151.2 | **173.88** | **204.12** | 12,247 |
| `T23G2Rn_L3` | 204,120 | 28,000 | 604.08 | **694.69** | **815.51** | 48,931 |
| **CAMPAIGN** | | | 781.35 | **898.55** | **1054.82** | |

Timeout = CAP core-min × 60 / ranks (ranks = 1). **The timeout IS the cap. An
overrun STOPS the run; a capped level is not restarted with a bigger number**
(rule 12). **USD — DERIVED, NEVER MEASURED:** POINT 898.55 core-min = 14.98 core-h ×
$0.0513 = **$0.77**; CAP 1054.82 core-min = 17.58 core-h × $0.0513 = **$0.90**. Under
the $25/run pre-authorisation, and still costed here per rule 12. **Estimate-versus-
actual calibration (rule 12) is owed at completion**: a row in
`docs/COST_CALIBRATION.md` comparing this POINT against the measured actual, gap
attributed, waste named separately. The predecessor per-level actuals are the T23G2R
measured cost record; if that record is not on disk at freeze the figures revert to
DESIGN ESTIMATE and the supervisor is told.

---

## 7. THE §2ba DETACHED AUTOGRADER — SPECIFIED, NOT ARMED

A `§2ba` detached autograder is specified for T23G2Rn's levels and is **NOT armed by
this draft** (no solver launches until the freeze is committed — personal check 4).
Contract (modelled on the T23G2R autograder `autograde_t23g2r_l3.sh`):

- **Detached from the agent:** launched under `setsid` so PPID becomes 1; it survives
  the launching lane's exit (L-agents-die-with-the-agent).
- **Grade-once guard:** refuses to grade twice; a durable marker prevents a second
  autograde overwriting the first verdict.
- **Poll both pids with `kill -0`:** waits on the solver pid(s) and does not grade
  until the run has ended (rc captured inside the detached wrapper, never around the
  `setsid` line — setsid parent returns 0 for every outcome).
- **~20 h ceiling:** a wall ceiling so a stalled poll cannot run forever.
- **Clears `__pycache__`** before invoking the comparator (stale-pycache inverts
  mutation tests).
- **Runs the FROZEN comparator verbatim** (`analyse_t23g2rn.py`, once pinned) — no
  re-implementation, no flags that change grading.
- **Exit-map 0/1/2/3:** 0 PASS, 1 GATE FAIL, 2 REFUSAL, 3 NOT A RESULT.
- **Writes a durable `T23G2Rn_RUNG_VERDICT.txt`** recording the comparator's own
  `RUNG VERDICT` line verbatim, the comparator pin, the mark_done pin, the exit code
  and the stdout artifact path — the same shape as `T23G2R_RUNG_VERDICT.txt`.

The autograder script and its arming are **OWED after the freeze** and are the
supervisor's to review; the §5.3 pre-flight gate (function objects shown to construct
in a scratch copy with no graded artifact written, **plus the explicit on-disk p_rgh
`tolerance 1e-10` / `relTol 0` assertion**) is also owed before the graded launch —
the launch is refused until it passes — its cost reported separately.

---

## 8. WHAT THIS DRAFT DELIBERATELY DOES NOT DO

- **It does not edit any frozen file.** T23G2R keeps its bytes and its `NOT A RESULT`
  verdict; `mark_done_t23.py @982e1db6` is **not** edited by this lane (§5.1 presents
  both options as text; the supervisor decides and applies).
- **It does not commit anything, freeze any sha, or run any solver.**
- **It does not move, widen or relax any gate, threshold, band, cap or label.** The
  only change is the p_rgh linear-solver tolerance/relTol (§2.1), a §2ba numerics fix.

*Drafted 2026-09-09 by a heat-transfer `lab-lane`. NOT FROZEN — the §3 code
diff-read of `build_t23g2rn.py`/`analyse_t23g2rn.py`, the completion-instrument
decision (§5.1), the blob pins and the freeze commit are the supervisor's
(non-delegable). Nothing is committed, frozen or launched by this lane.*
