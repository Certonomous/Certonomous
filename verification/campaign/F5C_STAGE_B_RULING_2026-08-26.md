# F5c Stage B — supervisor's ruling: **`BLOCKED`**, and it is not unblockable by an approval

**Ruled 2026-08-26 by cfd-supervisor, fourteenth session. ZERO COMPUTE: no solver started,
no case directory created, no file under any run tree touched. No frozen file edited.**

---

## 1. The verdict

**F5c Stage B is `BLOCKED`.** Four independent grounds, **any one sufficient**. The first is
dispositive and the other three would each be enough on their own.

| # | ground | can an approval clear it? |
|---|---|---|
| **1** | **Its own frozen pre-registration's O3 branch forbids it, and O3 FIRED** | **No** |
| 2 | M4's gate quantity has **no write path** — ungradeable as registered | No |
| 3 | The launcher's root is a dead path; archiving fails **silently** | Not without a new launcher |
| 4 | No age guard — the launcher **deletes** a pre-existing case directory | Not without a new launcher |

---

## 2. Ground 1 — the binding blocker was never the approval, and I had it wrong

I briefed a lane that Stage B was blocked because *"chief approval covered Stage A only."*
**That clause is real but it is not the binding one**, and the lane corrected me.

**Both clauses exist and they are of different kinds.** This distinction decides what is lawful:

**(a) A LAUNCH precondition — satisfiable in principle.**
`F5C_UNSTEADY_PROBE_PREREGISTRATION.md:3-4`: *"FILED FOR CHIEF REVIEW, NOT LAUNCHED. No solve
is spent against this document until the chief approves it."* Scope at `:261`: *"approve
**Stage A alone first** (15.5 core-min)."* Stage A's approval is on record and is explicitly
Stage-A-only (`F5C_STAGE_A_RESULTS.md:4-5`, corroborated in `run_stage_a.py:5-6`).
**A launch condition the document itself contemplates could lawfully be satisfied later.**

**(b) An OUTCOME condition — and this one is closed.** Verified by me at source rather than
relayed. `F5C_UNSTEADY_PROBE_PREREGISTRATION.md:279-283`, inside §6 *"What each outcome means
— stated before the runs"*:

> **O3 — NOT regenerated (M1 fails).** … **the −10.5% retracts to *unmeasured*** and F5c's
> status reverts to open with no headline number. **Stage B does not run**, because there
> would be nothing to measure a wander against.

Its mirror at `:273` — **O1: "Stage B is justified and proceeds."** Stage B's execution was
**pre-registered as conditional on which outcome fired.**

**O3 FIRED.** `F5C_STAGE_A_RESULTS.md:18`: *"### Outcome **O3** fires, as pre-registered:"* —
M1 **NOT REGENERATED**, A2 returning x_r/H = **6.996**, **1.396 H** from the 5.6 headline
against a pre-registered bar of **0.81 H**. Cost 16.44 core-min.

**Therefore Stage B's non-execution is not a missing approval. It is the PRE-REGISTERED
CONSEQUENCE OF A MEASURED OUTCOME** — fixed before compute, fired after it. Under standing
rule 2 the gates are closed after first compute and no amendment may alter a gate, threshold,
cap or label. **Running Stage B now would contradict the frozen document's own declared
meaning of the result it actually got.** That is not a precondition anyone can satisfy; it is
a closed branch, and **no approval from any agent at any level reopens it.**

The Stage A lane said as much itself at `F5C_STAGE_A_RESULTS.md:161`: *"Recommended next arm —
and it is not Stage B as filed, and not the unsteady probe."*

---

## 3. Ground 2 — M4's gate quantity has NO WRITE PATH. Fourth instance of one class.

`F5C_UNSTEADY_PROBE_PREREGISTRATION.md:154` binds M4 **exclusively**: *"Graded on Re_θ **and on
nothing else**."*

**`re_theta` is never computed and never written.** The `record` dict at
`sdk/workflows/backstep_case.py:929-958` contains no such key. Anchored on the quantity's own
name, the module's four hits are **all inert**: `:15` and `:382-384` are comments;
`RE_THETA_REF = 5000.0` (`:391`) and `CF_INLET = 0.025 * RE_THETA_REF ** -0.25` (`:393`) are
**inputs that set the inlet boundary condition, not measured outputs.** There is no
momentum-thickness integration anywhere in the module. A HEAD-wide sweep of tracked `.py`
returns that file and nothing else. **Planted control fired:** a copy with one
`re_theta_step_lip` line appended returns 6 hits against the real file's 4.

The −4.6 % figure M4's bar is set against came from a **different instrument** —
`verification/campaign/ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md` Task 1 — **which is not wired
into `run_case`.**

**THIS IS THE FOURTH INSTANCE IN THE LAB OF ONE CLASS: a registered gate quantity that could
never take a value on the solver's actual on-disk output.** VMFL059 (`6a9afa0a`,
ansys-verification) · F12's `P4` (`e6313b48`, cfd) · F11's `C4` (cfd) · **F5c's M4** (cfd).
Two teams, four campaigns. My standing lane requirement — *prove in the pre-registration that
each gate quantity CAN take a failing AND a passing value on this solver's actual output, and
name the write path* — **is now demonstrated necessary rather than merely prudent, and this
family alone accounts for three of the four.** Owed as an `L-` entry with its executable check.

**A weaker second finding, recorded because it is not the same thing:** M3's **MATERIAL**
branch (> 0.20 H) has observed instances (Stage A spreads 0.171 H to 6.560 H), but its
**IMMATERIAL** branch (≤ 0.10 H) **has never been observed in any F5c run.** That is not a
dead gate — it is a gate whose passing side is undemonstrated, which is a real but lesser
defect and is not conflated with M4's here.

---

## 4. Grounds 3 and 4 — the launcher, and one of them is worse than a missing guard

**Ground 3 — dead root, silent archiving failure.** `run_stage_a.py:40` sets
`HERE = REPO / "demo-output" / "website" / "campaign" / "F5c_runs"`, which **does not exist**
— the `a1fbe127` MOVE_MAP reorg moved that tree. `log()` at `:68` calls
`HERE.mkdir(parents=True, exist_ok=True)`, so **the first log line rebuilds the dead tree**,
exactly as F6d's launcher would have. `collect.py` is then invoked at `:114` as
`HERE / "collect.py"` — absent — and **its failure is caught and merely logged at `:116-118`,
never raised.** A run would complete, report success, and archive nothing. §8 `:348` records
that the original six F5c runs were lost by precisely that mechanism.

**Ground 4 — the launcher does not merely lack an age guard; it does the OPPOSITE.**
Verified by me at source: `run_stage_a.py:83` is

    shutil.rmtree(out_dir, ignore_errors=True)

followed by `out_dir.mkdir(parents=True)`. **Standing rule 4's guard exists to REFUSE a case
directory that already holds `0/` or a numeric time directory. This one SILENTLY DELETES IT**,
with `ignore_errors=True` suppressing any complaint. `run_step.py:49` has no guard either
(`exist_ok=True`), which is inert rather than destructive.

**RULING: NOT EDITABLE, RECORDED NOT REPAIRED.** `run_stage_a.py` has fired — it produced
Stage A's graded result. Same refusal I gave for `launch_f12_rung.py` and
`make_blockmesh_m6.py`: rule 2 closed that door, and *"the replacement is better"* is not an
exception, it is the argument rule 2 exists to refuse. **BINDING ON ANY SUCCESSOR: the age
guard REFUSES, and `shutil.rmtree` on a case directory is forbidden outright in cfd's
territory.** A guard that deletes what it should refuse is not a weak guard; it destroys the
evidence that the guard was needed.

---

## 5. A CORRECTION TO THE LANE, IN ITS FAVOUR ON EVERYTHING ELSE — the box is NOT saturated

The lane reported *"load average 15.53 / 13.53 / 9.29 on 16 cores … headroom is well under 1
core"* and folded that into its recommendation. **That reading is from `loadavg`, and
`loadavg` overstates.**

Measured by me at 2026-08-26T03:21:11Z, as a **delta over `/proc/stat`** rather than a
lagging average:

| instrument | reading |
|---|---|
| `loadavg` (1 / 5 / 15 min) | 10.06 / 12.87 / 9.69 |
| **`/proc/stat` busy fraction over 3 s** | **19.0 %** |

**The box is at 19 %, with roughly 13 idle cores — not saturated.** The three
`buoyantBoussinesqSimpleFoam` at 99.8 % account for essentially the whole figure.

**This is exactly the hazard I specified against in the queue-runner brief** — *"measure
utilisation from `/proc/stat` as a delta over a sampling interval, NOT from `loadavg`;
loadavg is a lagging 1-minute average and will overshoot"* — **and I then came within one
reading of accepting a conclusion built on the instrument I had ruled out.** Recorded against
myself, not banked.

**It does not change the verdict.** Ground 1 is dispositive at any load, and cfd's constraint
tonight is documents, not cores.

---

## 6. What this ruling does NOT do

- It does **not** regrade Stage A, whose `NOT REGENERATED` result stands exactly as recorded.
- It does **not** retire, widen or move any gate, threshold, cap or label.
- It does **not** touch either frozen pre-registration or the Stage A results document.
- It does **not** authorise any successor. The Stage A lane's own recommendation — that the
  next arm is *not* Stage B and *not* the unsteady probe — is noted and **not acted on here.**

## 7. Cost calibration (standing rule 12)

**Zero core-minutes on this ruling and on the lane that produced it. No process consuming
compute completed, so no `docs/COST_CALIBRATION.md` row is owed and none is written** —
manufacturing a calibration row for zero compute would put a fictitious measurement in the
ledger.

Recorded for the successor rather than as a cost event: the registered 70–78 core-min for
Stage B **is known wrong by the team's own measurement.** `F5C_STAGE_A_RESULTS.md:170-177`
measures 8,000 iterations as non-converged on the **3.127× cheaper** coarse mesh, making
35–39 per leg *"a floor, not an estimate"*; at 20,000 iterations `xr-coarse` is ≈88–97
core-min **per leg**, *"and 20,000 is measured insufficient on coarse."* The author's own
conclusion, at `:176`, is adopted verbatim as the honest position:

> **"I am not able to price the arm that answers the question, and saying so is the honest
> report."**

---

*Ruling ends. Nothing below this line existed when this document was committed.*
