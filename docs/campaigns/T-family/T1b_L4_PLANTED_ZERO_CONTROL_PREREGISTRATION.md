# T1b L4 — PLANTED-ZERO CONTROL: pre-registration of an EXTERNAL control instrument

**Status: FROZEN ON COMMIT. ARMED. NOT YET RUN.**
**Rung:** T1b L4 (`verification/runs/T-family/T1_runs/`, the 16-case pool).
**Written:** 2026-08-25, by the heat-transfer supervisor, **BEFORE the pool is
gradeable** — two of its sixteen cases are still solving and
`analyse_t1b_L4.py:170-173` refuses without all sixteen markers. **No T1b L4
grade exists at the moment this is frozen, and that is the entire evidentiary
content of the document.**

---

## 1. The defect this control answers

**CLAUDE.md standing rule 3 is not armed on the T1b chain.** Rule 3 reads: *"A
zero from a reader not shown able to see a non-zero is not evidence. Every
comparator plants a known perturbation, reads it back from disk, and **refuses**
if the reader cannot see it."*

**Established by a lane and then re-verified personally by the supervisor**, with
a positive control on the same reader in the same invocation:

| file | lines | plant-idiom hits | grades what |
|---|---|---|---|
| `T1_runs/analyse_t1b_L4.py` | 285 | **0** | the L4 pool — the rung about to be graded |
| `T1_runs/analyse_t1b.py` | 278 | **0** | supplies `measure()` — Nu, f, u_tau, y+ |
| `T1_runs/analyse_t1c.py` | 540 | **0** | supplies `gci()` and `iterative_convergence()` |
| *positive control* `T3_runs/analyse_t3.py` | — | **27** | (rule 3 armed) |
| *positive control* `T10a_runs/analyse_t10a.py` | — | **38** | (rule 3 armed) |

**The positive control is what makes the zero evidence** — the same grep on the
same box in the same invocation returns 27 and 38 on the two comparators known to
carry the plant, so the three zeros are a real absence and not a blind reader.
This is rule 3's own logic applied to the search for rule 3.

**The most exposed reader is `analyse_t1c.py`**, because it supplies
`iterative_convergence()` — **the reader whose verdict gates step (1) of Roache
triple gating.** Under CLAUDE.md rule 5, step (1) is what sends a row to `NOT A
RESULT` for a level that is not converged or not plateaued. **A reader that
silently cannot see a difference would report convergence everywhere**, and
nothing else in the T1b chain would catch it. That is precisely the failure rule
3 was written against, sitting on the gate's first step.

**These three files are not unguarded in general** — they carry refusal paths (2,
2 and 2 `exit(2)` sites; 2, 5 and 17 `refuse` mentions). **They are unguarded
against the specific failure of a blind reader**, which is the one refusals
cannot catch, because a blind reader raises nothing.

---

## 2. THE FROZEN COMPARATOR IS NOT EDITED — the ruling

**Ruling: the three files are NOT modified. The control is built as a SEPARATE
INSTRUMENT that grades nothing.**

The reasoning, stated so it can be overturned:

1. `analyse_t1b_L4.py` and its two dependencies are **on the frozen grading
   path**, fixed at the pre-registration commit (CLAUDE.md rule 2). Their
   worktree copies were verified byte-identical to their HEAD blobs this session
   (sha256 `9698adb0…48e31d`, and the `mark_done` / T3 / T10a comparators
   likewise). **Editing any of them breaks that hash** and
   `scripts/check_comparator_freeze.py` would correctly class them UNFROZEN.
2. **The §2d.1 repair exception does not apply and is not invoked.** §2d.1
   permits a change **on the grading path** that repairs a demonstrable error in
   a produced value. **Adding a control repairs no value and moves no number** —
   there is nothing here of the shape K0cS's area-weighted `wall_nu` had. Reaching
   for §2d.1 where it does not fit would devalue it for the case it was cut to
   fit.
3. **An external control is the stronger instrument anyway**, on §2d.1's own
   load-bearing condition (2): *an error found by something that grades nothing
   cannot have been selected to move a verdict in a wanted direction, because the
   thing that found it does not know which direction that is.* A control that
   lives outside the comparator **grades nothing by construction**.

**Consequence, and it is the point:** this control **can only ever turn the
rung's numbers into `NOT A RESULT`. It can never turn anything into a `PASS`.**
That is the same asymmetry CLAUDE.md rule 5 fixes for the triple gate — *the gate
can only turn a PASS or GATE FAIL **into** NOT A RESULT, never the reverse.*

---

## 3. What the control does — registered before it is built

`verification/runs/T-family/T1_runs/planted_zero_control_t1b.py`, to be written
against this frozen specification.

1. **Copy, never touch.** Copy one completed case's field data to a scratch
   directory outside the case. **The control never writes into any case
   directory**, and never into a directory holding a running solver.
2. **Plant by line index, not by value match.** Read the copied `T` field, choose
   a target line inside the `internalField` block **by index**, and add a known
   perturbation. Planting by index rather than by matching a value is deliberate:
   a value-matching plant can silently fail to land when the value it looks for
   is absent, and then the control reports success while having done nothing.
   This is `analyse_t10a.py`'s idiom (`planted_zero_control()`, line 377) and it
   is adopted here rather than reinvented.
3. **Read the plant back FROM DISK**, through the very functions the frozen
   comparator uses — imported from `analyse_t1b.py` / `analyse_t1c.py`, not
   reimplemented. **A reimplemented reader tests the reimplementation, not the
   instrument**, and would be worthless here.
4. **Assert the recovered change equals the planted change**, to the registered
   tolerance below.
5. **REFUSE with `sys.exit(2)`** if the reader cannot see the plant, printing
   which reader was blind and to what.

### 3.1 Registered constants — frozen by this commit

| constant | value | why this value |
|---|---|---|
| `PLANT` | **`1.234e-03` K** | the same constant `analyse_t3.py` uses (line 81). Deliberately **not** round, so a coincidental match is implausible; deliberately **small**, so a reader that sees it will see any physically meaningful difference. |
| `TOL_REL` | **`1.0e-06`** relative on the recovered change | the recovered change is a float round-trip through an ASCII field file, not a physics quantity |
| readers under test | **`analyse_t1b.measure`** and **`analyse_t1c.iterative_convergence`** | the two the L4 verdict actually depends on |
| exit on failure | **`2`** | the lab's refusal code; comparators refuse rather than degrade |

### 3.2 The control's own positive and negative arms — BOTH are required

**A control that only ever runs the positive arm is itself unproven.** Both arms
run, and **both must give their registered answer** or the control refuses:

- **POSITIVE ARM:** plant `PLANT`, read back. **The reader MUST see it.** If it
  does not → **REFUSE**: the reader is blind and every zero it has ever produced
  for this rung is worthless.
- **NEGATIVE ARM:** plant **nothing** — copy the field and read it back
  unmodified. **The reader MUST report no change.** If it reports a change → the
  reader is **noisy**, its zeros are not zeros, and the control **REFUSES**
  equally. A reader that always reports a difference passes the positive arm
  while being just as useless.

---

## 4. THE PREDICTION — registered before the control is run

**Prediction, and it is falsifiable:** both readers **WILL** see the plant, and
the negative arm **WILL** report no change. In other words **the control is
expected to PASS, and the T1b chain's zeros are expected to be real zeros.**

**This is registered as a prediction precisely because it is the comfortable
answer.** If the control refuses instead, that is the more valuable outcome and
it is recorded as such — not re-run until it agrees, not weakened, and not
attributed to the control. **The grading of the T1b L4 pool does not proceed
until this control passes.**

**If the control refuses**, the disposition is fixed here in advance so it cannot
be chosen later to suit the finding:

| outcome | disposition |
|---|---|
| positive arm fails (reader blind) | **the T1b L4 rung is `NOT A RESULT`**, and every previously published T1b number that depended on the blind reader is **withdrawn**, not re-graded. Escalated: it would touch T1b and T1c both. |
| negative arm fails (reader noisy) | same verdict, same withdrawal. A noisy reader's zeros are not zeros. |
| both arms pass | the control is recorded as PASSED with its numbers, and grading proceeds. **The control's passing is not itself a result** — it arms an existing gate, it does not create one. |

---

## 5. Scope — what this document does and does not cover

**Covers:** the T1b chain only — `analyse_t1b_L4.py`, `analyse_t1b.py`,
`analyse_t1c.py`.

**Does NOT cover, and these are recorded as OPEN rather than quietly carried.**
The same lane sweep named further graders in this team's territory with no plant
machinery found: `K0b_D403_rerun/grade_d403.py`, `K0b_D406_repair/grade_d406.py`,
`K0cG_runs/analyse_k0cg.py`, `K0cP_runs/analyse_k0cp.py`,
`K0cQ_runs/analyse_k0cq.py`, `K0cR_runs/analyse_k0cr.py`,
`K0cS_runs/analyse_k0cs.py`, `K0cT_runs/regrade_nusselt.py`,
`K0cX_runs/analyse_k0cx.py`, `K0cX_runs/grid_convergence.py`,
`K2b_runs/analyse_k2b.py`, `K2b_runs/analyse_k2bU.py`, `K2e_runs/analyse_k2e.py`,
`T9a_runs/analyse_t9a.py`, `T9aH_runs/analyse_t9a.py`.

**That list is a lead, not a finding.** The lane searched for the plant *idiom*
and did not verify that each of those refuses at exit 2, nor that none carries an
equivalent control under another name. **It is not repeated upward as a count of
defects**, and no verdict is moved on it here. It is docketed for a sweep that
checks each file individually, with a positive control, in the way the three T1b
files were checked.

**`K0cT_runs/analyse_k0ct.py` and `K0c_runs/analyse_k0c.py` DO carry plant
machinery**, as do the `T10aR`, `E4`, `E4a2`, `T9aH/analyse_t9aH.py`,
`T9a/analyse_t9aD.py`, `analyse_dts*.py` and `analyse_pesweep.py` graders. Named
here so the open list above is not read as the whole territory.

---

## 6. Cost

**Zero solver compute.** The control reads existing field files and copies one
case's data to scratch. Estimated **under 1 core-minute**, well inside the $25
pre-authorisation; **$0.0009 derived at $0.0513/core-h, derived and not
measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md`
§5). **No cap is registered because there is nothing to cap**; per this team's
standing ruling, a prediction is not a cap and none is claimed here.

The actual figure is compared against this estimate at completion and lands as a
row in `docs/COST_CALIBRATION.md` (CLAUDE.md rule 12).

---

## 7. What this document does not do

- It **does not** modify any frozen file.
- It **does not** create, move or retire any gate, threshold, band, cap or label.
- It **does not** grade anything. The control produces **PASS** or **REFUSE**,
  and neither is a rung verdict.
- It **does not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).
