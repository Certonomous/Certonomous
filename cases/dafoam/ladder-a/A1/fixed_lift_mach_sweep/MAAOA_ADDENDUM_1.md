# MAAOA — ADDENDUM 1 — 2026-09-03 — POST-COMPUTE — **NO VERDICT OF RECORD IS THIS ITEM'S PERMANENT DISPOSITION**, AND THE §2d.1 REPAIR EXCEPTION IS **REFUSED** ON THREE OF ITS FOUR CONDITIONS

**STATUS: LANDED as this item's addendum of record.** Drafted by a `lab-lane`
under `dafoam-supervisor`, read by the supervisor personally, and committed on
that read. Conclusion (b) ACCEPTED by the supervisor; §4.1's precedent limb was
added on the supervisor's direction and **verified at source by this lane
rather than relayed**. Nothing in this item is filed, sent, uploaded, posted or
shared outside this box (rule 7).

**This is a DATED ADDENDUM under rule 2 / `VERIFICATION_CHARTER.md` §2b limb 2.**
It alters **no gate, no threshold, no cap and no label.** It appends to nothing:
`MAAOA_PREREGISTRATION.md` is frozen and is not edited by this document
(rule 6). It records a disposition and it states what a successor must do
differently.

**Item:** `MAAOA` — fixed-lift (Ma, AoA) sweep, A1WR L3, seven points.
**Freeze:** `MAAOA_PREREGISTRATION.md` at `586b72caf39dad1f79b028cf590818da585688a2`;
instrument md5s in `MAAOA_MD5.txt`.
**Chain:** `STATUS.MAAOA_chain` — `rc=0 phase=COMPLETE spend_total=664.0 reader_rc=2`,
2026-09-02T21:58:19Z.

---

## 1. THE DISPOSITION

> **`MAAOA` HAS NO VERDICT OF RECORD, AND THAT IS PERMANENT.**
> No point of this item carries a graded verdict — not `MA288`–`MA685`, and
> **not `INCOMP`.** The frozen reader `maaoa_read.py` ran, refused at `rc=2`,
> and **a refusal is not a verdict** (D19, D19R2). The grading path is fixed at
> the pre-registration commit and **no other reader, no hand grading and no
> code path other than the one that ran may be substituted** (rule 2;
> `VERIFICATION_CHARTER.md` §2d).

The item's **cost** obligation under rule 12 is separately and fully
discharged — `docs/COST_CALIBRATION.md` row
`C-20260902T221439.942229Z-6ec6c321`, which asserts no verdict and says so on
its face. **Cost is closed; grading is not open.**

### 1.1 ⚠ AND THE REFUSAL COST THIS ITEM NOTHING FAVOURABLE — STATED HERE, NOT BURIED AT §6.2

A refusal that removes a verdict invites the reading that a good result was
lost. **On this item that reading is false, and it is false on measurement.**

- **The refusal is the only reason a FALSE convergence reading was not
  published.** `maaoa_read.py:190` computes `bool(CONV.search(t))` over the
  **whole** log and prints the result under the column header `"last conv"`
  (`:201`) — **an *any*-test wearing a *last*-test's label.** Driven read-only
  through the frozen reader's own parsers: **had M1 passed, this reader would
  have printed `INCOMP … last conv = yes`.** That is **false** — `INCOMP`'s
  five primals converged at 002/003/004 and **the published primal, 005, ran
  to `Time = 4000` and printed no convergence line at all** (§6.1).
- **The compressible arm was heading for a `GATE FAIL` regardless of M1.**
  Five of the six compressible points measure **y+max ≥ 1.0** (6.6296, 2.9770,
  1.1096, 1.0526, 1.1462; `MA685` 0.4892) — registered outcome (C), `G-YPLUS`
  `GATE FAIL` with the wall-resolved claim withdrawn for those points.
- **The one point that trimmed did not converge.** `INCOMP`'s published primal
  is **`UNCONVERGED`** on the solver's own criterion (§6.1).

> **NOBODY MAY LATER READ THIS REFUSAL AS HAVING COST THIS ITEM A FAVOURABLE
> RESULT.** What it withheld was a `GATE FAIL` on five of six compressible
> points and one `TRIMMED` row carrying a **wrong** convergence column.

## 2. THE REFUSAL, RE-DRIVEN AND SHOWN DETERMINISTIC

Re-driven 2026-09-03 by a lane that launched no solver and no container.

- **Instrument identity verified against the committed blob**, not asserted:
  `maaoa_read.py` md5 `79fddadcc748d3b83efb1d4ed8023475` on disk == the same
  from `git show HEAD:` == the pin in `MAAOA_MD5.txt`. Likewise
  `maaoa_runScript_incomp.py` `944dc9e0…`, `maaoa_runScript_comp.py`
  `bd22df02…`, `maaoa_cmd.sh` `d3f0fe7d…`. **All four clean.** `__pycache__`
  cleared before the drive (the stale-bytecode inversion hazard).
- **Two consecutive drives against `/home/ubuntu/certonomous-runs/MAAOA`
  returned `rc=2` and byte-identical output.** The refusal is deterministic.
- The refusal line, verbatim: **`SELFTEST REFUSED -- M1: 5 controls.`**
  M1 `*** FAIL ***`; **M2, M3, M4, M5 all `PASS`.**
- The reader wrote **no `MAAOA_POINTS.json`** — it returns at `maaoa_read.py:172`,
  before any row is composed. **There are no pre-repair values for this item.
  The pre-repair state is the empty set.** (§4 conditions (3) and (4) turn on
  this.)

### 2.1 What M1 is, precisely — and it plants nothing

M1 is the **positive control**, not a plant. `maaoa_read.py:105-107`:

```
    r1 = parse_trim(base)
    chk("M1", r1 is not None and trim_verdict(r1)[0] == "TRIMMED",
        "unmodified bytes -> full row, TRIMMED")
```

It requires the **unmutated** `base` bytes to (a) parse to a full trim row and
(b) grade `TRIMMED`, i.e. `|CL − 0.5| ≤ 1.0e-3` (`:36`, `:72-81`). The plants
live in M2 (`:109-115`, CL → 0.612345), M3 (`:117-123`, parser disabled), M4
(`:125-131`, y+max → 1.71) and M5 (`:133-139`, stall/MDD claim strings).

### 2.2 The fixture is a live artifact of the graded run — confirmed, not inferred

`maaoa_read.py:161-167` selects `base`:

```
    base, note = FIXTURE, "WRITER_BUILT fixture (no completed point on disk yet)"
    for u in sorted(run.glob("MA*")) + sorted(run.glob("INCOMP")):
        lp = u / "out" / "trim.log"
        if lp.is_file() and parse_trim(lp.read_text(errors="replace")):
            base, note = lp.read_text(errors="replace"), str(lp)
            break
```

**The static `FIXTURE` constant (`:84-90`) is a fallback, used only while no
point has produced a parseable log.** Once one has, the control's input becomes
that point's own bytes. `sorted(run.glob("MA*"))` puts `MA288` first, so:

- **Selected fixture: `/home/ubuntu/certonomous-runs/MAAOA/MA288/out/trim.log`**,
  sha256 `ae964c2f64cd959bc698b3f95e1f5706b9a074a40310c65a3f895b669e9703e2` —
  printed by the reader itself.
- That file is **59,165 bytes, owner `root`, mtime 2026-09-02 20:08:56Z** —
  written by this item's own container, inside the chain window
  18:36:41Z–21:58:19Z. **It is an output of the run being graded, not a static
  fixture.** Confirmed, not refuted.
- Its trim line (`MA288/out/trim.log:1580`) carries the runner's failure
  sentinel — `CL=1 CD=1 err=AnalysisError(… Primal solution failed!)`. It
  parses (so the loop breaks on it) and grades `NOT TRIMMED` (|1 − 0.5| = 0.5).
  **M1's premise was falsified by the run's own outcome.**
- **The same reader passes M1 on the static `FIXTURE` constant** (CL = 0.500042
  → `TRIMMED`), which is the state in which §4 of the pre-registration recorded
  the controls "driven PASS before this freeze". **The instrument is not
  defective in its controls; it is defective in its choice of the control's
  input, and that defect only becomes visible once a run exists.**

Generalised as **L-435** (`9442fc36`), the inverse of L-288.

---

## 3. THE CLAUSE THAT APPLIES, AND THE TWO ESCAPE HATCHES THAT DO NOT

**§2d places mutation controls ON the grading path, by name:** *"every band,
every reference, every row definition, every verdict rule, the discrimination
test and **the mutation control** — is fixed at the pre-registration commit."*
The selftest apparatus is therefore inside §2d, and a post-compute change to it
needs §2d.1 or it is forbidden. `MAAOA_PREREGISTRATION.md` §4 independently
registers it: *"Planted controls: reader selftest M1–M5 … driven PASS before
this freeze."* **§2d.1 is the applicable clause. It does reach a selftest
control's fixture.**

Two boundary limbs of §2d were tested and **neither reaches this**:

1. **"A comparator that cannot run at all"** (§2d boundary limb 1, the D419
   case). **Does not apply, and this is the most tempting escape hatch, so it
   is answered on the record.** The reader RAN: it executed its full selftest,
   wrote its complete output, and returned the **exit code its own
   pre-registration registers for this condition** (§4 G-YPLUS: *"blind/all-zero
   channel ⇒ refuse exit 2 (rule 3)"*; `maaoa_read.py:170-172`). A dangling path
   constant is an instrument that cannot answer; this is an instrument that
   answered. And that limb's own test — *"whether the repair can change a
   number"* — is answered **YES**: the repair changes every number in this item
   from nonexistent to published.
2. **W-4 correction to a published record** (§2d boundary limb 3, the D420
   case). **Does not apply — nothing was published.**

---

## 4. §2d.1, CONDITION BY CONDITION

The clause, verbatim (`VERIFICATION_CHARTER.md:1936-1942`):

> *"A change on the grading path made after the first graded solve is permitted
> when, and only when, all four hold: (1) it repairs a DEMONSTRABLE ERROR rather
> than a preference; (2) the error was established by an instrument INDEPENDENT
> OF THE HYPOTHESIS — one that grades nothing, such as a near-identity, a guard
> or a control; (3) the record discloses it, names that instrument, and
> QUANTIFIES WHAT MOVED; and (4) the pre-repair values are recorded beside the
> published ones. **Failing any of the four, 2d stands.**"*

| # | condition | MAAOA | evidence |
|---|---|---|---|
| **1** | repairs a **DEMONSTRABLE ERROR** rather than a preference | **SPLIT — met on the defect, NOT met on the repair** | The *defect* is demonstrable and is a statement about code, not about an answer: `maaoa_read.py:161-167` makes the positive control's input a function of the graded run's outcome, so M1's premise is not guaranteed by construction. But the *repair that would unblock grading* — re-basing or relaxing M1's input so it passes — **is not distinguishable from a preference at the moment it is chosen, because it is chosen to make M1 pass.** §2d.1's own contrast case: *"the numbers looked wrong, so the band was widened."* |
| **2** | error established by an instrument **INDEPENDENT OF THE HYPOTHESIS**, one that **grades nothing** — *the charter calls this the load-bearing condition* | **FAILS** | **The error was established by the graded instrument's own refusal on the graded data**, at 21:58:19Z (`/home/ubuntu/certonomous-runs/MAAOA/MAAOA_read_20260902T182040Z.txt`; L-435 is derived from it). **No near-identity, no guard, no independent control flagged it.** Contrast K0cS, the case the exception was cut for: the **heat balance** — a near-identity, reported and never gated — moved 2.5–8.4 % → 0.0000 %. That instrument *does not know which direction a verdict wants to move.* Here the finder **is** the grader, on this run, and it knows exactly: from refusal to verdict. The objection that the defect is *readable* in the code at the freeze commit does not rescue this — **nobody read it then; it was read because of the refusal**, and a code read by the team whose item lacks a verdict is not "an instrument that grades nothing", it is a party with a stake, which is precisely what condition (2) exists to exclude. |
| **3** | record discloses it, names that instrument, and **QUANTIFIES WHAT MOVED** | **FAILS — on binding precedent (§2d.4.1), and on structure** | See §4.1. Disclosure and naming are satisfied (this addendum, L-435, `docs/LAB_STATE.md` dafoam S-28). **"Quantifies what moved" is not.** |
| **4** | **pre-repair values recorded beside the published ones** | **FAILS — on binding precedent (§2d.4.1), and on structure** | See §4.1. **There are no pre-repair values.** The reader returned at `maaoa_read.py:172` before composing a single row and wrote no `MAAOA_POINTS.json` (verified absent on disk). |

### 4.1 CONDITIONS (3) AND (4) — RULED ALREADY, TWICE, BY VERIFICATION. THIS IS PRECEDENT, NOT OUR READING OF A CLAUSE

**This team does not get to construe §2d.1's conditions (3) and (4) for
itself.** Two rulings are directly on the point and both were verified at
source by this lane rather than relayed:

- **`§2d.3.3`** (v1.36, 2026-08-31, the **T20 grant**,
  `docs/charters/VERIFICATION_CHARTER.md:4389-4399`) created the only shortcut
  that exists: *"A `§2d.1` repair may satisfy conditions (3) and (4) by
  DISCLOSING AN ABSENCE — but the absence must be MEASURED AND NAMED, never
  asserted"* (`:4395`) — **and bounded it at `:4397`: *"AND IT IS AVAILABLE
  ONLY WHILE THAT COUNT IS ZERO. The moment one graded solve exists under the
  registration, (3) and (4) bite in full… This clause creates no path for
  repairing a rung that has produced numbers."***
- **`§2d.4.1`** (v1.37, 2026-09-02, the **T23G2 denial**, `:4424-4436`) then
  narrowed it. `:4430`: *"What T23G2 lacks is a VERDICT, not NUMBERS — and (3)
  'quantifies what moved' and (4) 'pre-repair values recorded beside the
  published ones' key on **values**, not on verdicts."* The ruling, `:4432`:
  > *"the absence-disclosure shortcut keys on the absence of NUMBERS, never on
  > the absence of a VERDICT. A rung whose solves have COMPLETED has numbers,
  > **whether or not a comparator has consented to grade them.** For such a
  > rung, conditions (3) and (4) BITE IN FULL."*

**MAAOA IS T23G2's SHAPE, NOT T20's — measured, not argued.** T20 had zero
solves and nothing on disk. `MAAOA`'s chain reads `phase=COMPLETE`, all seven
points ran their full 4,000 iterations and wrote logs and `trim.json` to
`/home/ubuntu/certonomous-runs/MAAOA/`; **`INCOMP` alone settles it with
`CL = 0.4999987189650539`, `CD = 0.014434696273095972`, `alpha_trim` 4.755644949811032°.**
`MAAOA` **has numbers and lacks a verdict.** `:4432`'s clause *"whether or not
a comparator has consented to grade them"* is written for precisely this fact
pattern. **The `§2d.3.3` shortcut is therefore DENIED to `MAAOA` on precedent,
and (3) and (4) bite in full.**

**AND `§2d.4.1`'s own reasoning names this item's mechanism explicitly.**
At `:4436`: *"read loosely it would let any ungraded rung call itself
value-free. **A comparator that refuses to run is then a qualification for the
shortcut — the instrument's own failure becoming the ground for relaxing the
rule that governs repairing it.** That is circular."* **`MAAOA`'s comparator
literally refused.** Claiming the shortcut here would be the exact circularity
that ruling was written to forbid.

**⚠ AND `MAAOA` FAILS (3) AND (4) BOTH WAYS, WHICH IS A NARROWER POSITION THAN
EITHER PRIOR ITEM OCCUPIED — SURFACED RATHER THAN GLOSSED.** `§2d.4.1:4434`
holds that requiring (3)/(4) of a completed rung *"is therefore not an
obstacle"*, because the discharge is affordable: *"every repair's effect is
measurable by running the comparator over the same data before and after the
repair and publishing both."* Heat-transfer duly performed it at zero solver
compute (`:4561`). **That route is UNAVAILABLE to `MAAOA`, and not because it
lacks numbers — because its comparator's BEFORE state emits nothing to
tabulate.** The before column would hold a refusal, and `:4430` is explicit
that (3)/(4) key on **values, not verdicts**; a refusal is not a value. So:

| | `§2d.3.3` absence shortcut | `§2d.4.1:4434` before/after discharge |
|---|---|---|
| **T20** | AVAILABLE (0 solves) | n/a |
| **T23G2** | DENIED (has numbers) | **AVAILABLE, and performed at 0 core-min** |
| **`MAAOA`** | **DENIED** (has numbers) | **UNAVAILABLE** (comparator's before-state emits no values) |

**`MAAOA` is the first item to sit in that gap, and the honest consequence is
that (3) and (4) are not merely unmet but unmeetable here.** That is flagged
for verification as a fact about this item, **not** as a petition and **not**
as a ground for relief — an item that cannot satisfy a condition does not
thereby become exempt from it. `§2d.1`'s operative sentence is unconditional:
*"when, and only when, all four hold… Failing any of the four, 2d stands."*

**SECOND GROUND, corroborating and no longer load-bearing:** conditions (3) and
(4) presuppose a repair that moves a computed quantity from one value to
another. **§2d.1 is cut for a repair that corrects a number** — K0cS could say
*"every Nusselt number was wrong by 10–27 percent"* — **and not for one that
converts a refusal into a result.** Here what moves is not a number but the
*existence* of numbers. This was this lane's original reasoning; it is retained
because it agrees with the precedent, and it is placed second because a team's
own construction of a clause is the weakest authority for a ruling that could
later be cited by someone whose interest it serves.

**ONE RULE, THREE ITEMS, THE SAME ANSWER.** T20 granted, T23G2 denied,
`MAAOA` denied — and it goes against dafoam here exactly as it went against
heat-transfer eighteen hours earlier. **That is what a charter is for**
(`§2d.3.4`: *"Two teams, two rungs, one rule, the same answer… Had I ruled T20
differently I would have been wrong about one of them."*).

### 4.2 CONCLUSION — (b). THE REPAIR IS **NOT LEGAL** HERE

**Three of four conditions fail.** Condition (2) fails, and `§2d.1:1944` states
in terms that *"Condition (2) is the load-bearing one and the other three are
hygiene"* — **so (2) alone decides this item.** Conditions (3) and (4)
independently fail on binding precedent (§4.1), and the hygiene
characterisation does not soften that: the operative sentence is
unconditional — *"when, and only when, all four hold… Failing any of the four,
2d stands."* **2d stands. The grading path does not change. `MAAOA` has no
verdict of record, permanently.**

And the clause's closing sentence is directly on point:
**"Nothing a verdict depends on may be repaired on the authority of the verdict
it produces."** This item's entire disposition *is* the reader's refusal.
Repairing the control is repairing the thing that produced the outcome, on the
authority of wanting a different one.

**Recorded against ourselves:** repairing a control so that grading may proceed
moves this item from *no verdict* to *some verdict*, which is the flattering
direction, and it is the direction in which every point that already "worked"
would be published. **That is exactly where bias enters, and it is why the
answer is no.**

### 4.3 IT IS NOT (c) — nothing here is reserved above this team

**M1 is not a gate.** `MAAOA_PREREGISTRATION.md` §4's gate table registers
`G-GATEDEP`, `G-FREEZE`, `G-IMG`, `G-TRIM`, `G-YPLUS`, `G-WALLTREAT`,
`G-STALL`/`G-MDD`, `G-CAPS`, `G-NOBAND`. **M1–M5 are listed beneath that table
as "Planted controls", not as gates.** Repairing M1 would not widen or retire
`G-TRIM` or any other gate, so the reservation on *retiring a standard, gate
threshold or charter clause* is not triggered and this does not go to Sanaa's
desk on that limb.

**One limb IS flagged for verification, and it is not a blocker:** M1 is this
reader's implementation of **standing rule 3's positive limb** — a reader shown
able to read a *good* row, as the complement of the planted-perturbation
refusal. **A successor that weakens M1 to a bare "it parses" test weakens the
lab's rule-3 posture generally**, and should not be designed by the team whose
item wants a verdict without a verification read. §5 below is written so that
no such weakening is needed.

---

## 5. WHAT A SUCCESSOR REGISTRATION MUST DO DIFFERENTLY

A successor is a **fresh pre-registration on a fresh run root**, frozen before
its first compute under §2b limb 1. That is **not a §2d.1 question at all** and
is entirely legal: §2d.1 governs changing *this* item's grading path; it says
nothing about building a correct instrument for a *new* one. **The successor
re-runs the physics; it does not re-grade `MAAOA`'s artifacts.**

Binding requirements, all of which are defects **measured** in this item:

1. **THE PRE-COMPUTE SELFTEST TRANSCRIPT IS COMMITTED *IN* THE FREEZE COMMIT —
   and this requirement comes first because it is the one `MAAOA` cannot now
   evidence** (§8 below). With a static fixture (limb b) the selftest is
   run-independent, so its transcript belongs **in the freeze commit**, not in
   the run root, and it is the artifact that discharges the freeze's
   "controls driven PASS" assertion.
   **(b) THE SELFTEST FIXTURE IS STATIC AND IN-FILE.** The positive control
   reads a constant embedded in the reader — the existing `FIXTURE` at
   `maaoa_read.py:84-90` is already correct and already passes M1. **Delete the
   live-artifact preference at `:161-167` entirely.** A control's input may
   never be a function of the run being graded (**L-435**). Assert it: the
   successor's selftest carries a check that `base is FIXTURE`. The two limbs
   are one requirement — a run-independent control is what makes a pre-compute
   transcript meaningful, and a pre-compute transcript is what proves the
   control was run-independent.
2. **`last conv` MUST MEAN LAST.** `maaoa_read.py:190` computes
   `bool(CONV.search(t))` over the **whole** log and prints it under the header
   `"last conv"` (`:201`). That is an **any**-test wearing a **last**-test's
   label. **Measured consequence, and it is not hypothetical: had M1 passed,
   this reader would have printed `INCOMP  … last conv = yes`, which is false**
   — `INCOMP`'s five primals converged at 002/003/004 and **the published
   primal, 005, ran to `Time = 4000` and printed no convergence line at all**
   (§6.1 below). **The refusal is the only reason a wrong convergence reading
   was not published.** The successor segments the log per primal and reads the
   **last** one.
3. **THE CONVERGENCE READING IS PER-EQUATION, NOT A SINGLE SCALAR.** DAFoam's
   `"Minimal residual … satisfied the prescribed tolerance"` line is one
   number and is absent on a capped primal. The successor reads the
   **per-equation `initRes` block of the final iteration** — `U0 U1 U2 p
   nuTilda`, **all five, named individually** — and states which are above
   `primalMinResTol`. **On this item's own `INCOMP`, three of five are under
   and two are over** (§6.1). A three-of-five reading reported as "all" is the
   flattering-direction error this requirement exists to make impossible.
4. **THE `G-YPLUS` CHANNEL IS A SAMPLE AND THE REGISTRATION MUST SAY SO.** The
   reader reads the last printed `yPlus` line, up to `printInterval = 100`
   iterations stale, on a field measured swinging within a run (`S-27`). This
   item registered that caveat and still gated on the sample. **Whether a gate
   may sit on a sampled field is on Sanaa's desk (gate design is reserved) and
   the successor does not pre-empt it.**
5. **THE COMPRESSIBLE ARM'S PREMISE IS NOT RE-REGISTERED WITHOUT A REPAIR.**
   All six compressible points primal-failed with `Primal min residual`
   0.6722–0.8993. `S-27` closed that triage as a **wall-resolved-compressible
   setup failure** — one mesh, one image, one item, `DASimpleFoam` converging
   where `DARhoSimpleFoam` fails 0-of-11 — **not Mach and not physics.**
   **Re-registering the same six points on the same setup would spend the same
   553.85 core-min for the same nothing.** A successor either carries the
   repair or drops the compressible arm and says why.
6. **COST.** `MAAOA`'s measured forward rates are the successor's anchors and
   are already on the ledger row: compressible `DARhoSimpleFoam` at A1WR L3,
   np = 1, run 6-up beside A1WR's 8 units ≈ **1.38 s/iter**; incompressible
   `DASimpleFoam` run 1-up ≈ **0.49 s/iter**; **a converging fixed-lift Newton
   trim costs ~13,400 primal iterations, not the ~7,900 registered.**

---

## 6. THE THINGS THIS ITEM DID MEASURE, WHICH CARRY NO VERDICT AND MUST NOT ACQUIRE ONE

Reported as **measurements with their artifacts**. Under
`VERIFICATION_CHARTER.md` §2 a value may be reported without a verdict; a
verdict requires a gate that was reached, and none was.

### 6.1 `INCOMP` — the point that ran clean, stated fully rather than favourably

From `/home/ubuntu/certonomous-runs/MAAOA/INCOMP/out/trim.json` (the **runner's**
output — not the reader's, and therefore **not a graded artifact**):

| quantity | value |
|---|---|
| `alpha_trim_deg` | 4.755644949811032 |
| `CL` | 0.4999987189650539 |
| `CD` | 0.014434696273095972 |
| `error` | `null`, rc = 0 |
| `wall_s` | 6558.116363763809 (110.15 core-min, inside the 120 cap) |

`|CL − 0.5| = 1.281035e-06`, i.e. **780.6× inside `G-TRIM`'s 1.0e-3 — 2.892
orders, not three.**

**AND THE UNFLATTERING HALF, WHICH BELONGS BESIDE IT.** From
`/home/ubuntu/certonomous-runs/MAAOA/INCOMP/out/trim.log`, five primals over
three Newton steps:

| primal | log lines | outcome | `Total Residual Norm2` |
|---|---|---|---|
| 001 | 482–1162 | ran to `Time = 4000`, **no convergence line** | 1796.807733513592 |
| 002 | 1191–1697 | converged, `9.997083655914609e-09` at `Time = 2946` | 32.68805550254275 |
| 003 | 1722–2084 | converged, `9.997287330332059e-09` | 42.92048357402096 |
| 004 | 2113–2219 | converged, `9.999330409965113e-09` at `Time = 458` | 52.31878635352416 |
| **005** | 2244–2924 | **ran to `Time = 4000`, no convergence line** | **45.91224977662464** |

**Primal 005 is the one whose numbers are published** — the
`MAAOA_TRIM_VALUES` line sits at `:2932`, immediately after 005's block.

Primal 005's **final-iteration (`Time = 4000`) per-equation initial residuals,
all five as printed**:

| equation | `initRes` | vs `primalMinResTol` = 1e-08 |
|---|---|---|
| `U0` | 2.611685273913492e-09 | under |
| **`U1`** | **1.322328781718701e-08** | **OVER, 1.32×** |
| **`U2`** | **2.484578318569751e-08** | **OVER, 2.48×** |
| `p` | 6.797482254798008e-09 | under |
| `nuTilda` | 9.134569451258965e-09 | under |

**Three of five under tolerance, two over.** The solver's own convergence
declaration is absent, and the two velocity components are why.

**Under §2's fidelity chips, `INCOMP`'s published primal is `UNCONVERGED`** —
the solve did not settle and the number is not evidence yet. That is a
*measurement*, not a verdict, and it does not become one here.

### 6.1.1 ⚠ THREE CORRECTIONS TO `docs/LAB_STATE.md` DAFOAM `S-28` §3, MADE BY THIS LANE'S RE-MEASUREMENT

`S-28` §3 left the convergence question open on purpose — *"THE RECORD REPORTS
BOTH HALVES AND COMPOSES NEITHER"*. **Re-measurement closes it, and it closes
against the board's reading.** These are corrections **of the supervisor's own
record**, attributed to this lane, and they are recorded here rather than
smoothed into the prose. `S-28` is not edited (rule 6); this is its correction
of record.

| # | `S-28` §3 said | the artifact says |
|---|---|---|
| 1 | *"its final-iteration residuals are `U0` 2.61e-09, `p` 6.80e-09, `nuTilda` 9.13e-09 — **ALL** under tolerance"* | **The `Time = 4000` block prints FIVE `initRes` lines, not three.** The three quoted values are each exactly right; **the two omitted — `U1` 1.322328781718701e-08 and `U2` 2.484578318569751e-08 — are both OVER 1e-08**, `U2` by 2.48×. **Three of five is not "all"**, and the selection kept the smallest of the three `U` components. **This is the flattering direction**, and it *explains the instrument's silence*: primal 005 did not converge by the solver's own criterion. |
| 2 | *"its `Total Residual Norm2` of 45.912 sits **inside** the 32.688–52.319 span of the three that did converge"* | **Arithmetically correct, mis-scoped as evidence.** Recomposed from the log's own components: `U` only = **45.912249373**; all four channels = **45.912249777** against the logged **45.91224977662464**; **`p` contributes 1.317e-04 of the total.** ⚠ **`Total Residual Norm2` IS the `U`-norm to nine figures** — so "it sits in family" is a statement entirely about the `U` channel, **in a norm far too coarse to see the two `U` residuals that failed.** It is also compared across primals stopped by *different rules* (002/003/004 at 1e-8; 005 at `endTime`), and primal 001 — the other non-converger — sits at **1796.807733513592**, 39× the family. The statistic separates 001 by 39× and cannot separate 005 at all. |
| 3 | *"and `CL` settles monotonically to seven figures"* | **Both halves wrong.** Over primal 005's 41 `CL` prints, **16 of 40 increments are ≤ 0** — monotone only over the tail, not the primal. And it had **not settled**: the final increment is **+6.002e-06 per 100 iterations**, shrinking only ~7 % per print, **still climbing in the sixth decimal when `endTime` stopped it.** `\|CL − 0.5\| = 1.281035e-06` (780.6× inside `G-TRIM`, 2.892 orders) is unaffected — but *"settles"* claims a plateau the last two prints refute. |

> **CONSEQUENCE FOR THE BOARD'S FRAMING, STATED PLAINLY.** `S-28` §1 called
> `INCOMP` *"THE POINT THAT WORKED"* and *"a genuine fixed-lift trim [with] no
> graded verdict"*, and headlined it as **the casualty**. **That framing is
> overstated.** `INCOMP` trimmed — `G-TRIM` would have held by 780.6× — **but
> its published primal is `UNCONVERGED`**, and a successor should not assume it
> grades `PASS` on convergence. **The casualty framing survives only on trim,
> not on the solve.**

**Fourth relayed figure corrected in two days.** The pattern the supervisor
named in `S-28` §2 — *"a relayed number needs its scope carried with it, or it
becomes false the moment it travels"* — reproduces here in a fourth form:
**a subset of a printed block, quoted with the quantifier "all".**

### 6.2 What the reader would have printed, had M1 passed — reported so the refusal's cost is honest

Driven read-only through the frozen reader's own parsers, launching nothing:

| point | `G-TRIM` | y+max | `last conv` (as coded) |
|---|---|---|---|
| MA288 | NOT TRIMMED | 6.6296 | no |
| MA400 | NOT TRIMMED | 2.9770 | no |
| MA500 | NOT TRIMMED | 1.1096 | no |
| MA600 | NOT TRIMMED | 1.0526 | no |
| MA650 | NOT TRIMMED | 1.1462 | no |
| MA685 | NOT TRIMMED | 0.4892 | no |
| INCOMP | TRIMMED | 0.0259 | **yes — and this is FALSE, per §5 requirement 2** |

`G-WALLTREAT` would have passed on all seven (`BCType=nutLowReWallFunction`
present, Spalding line absent, every point).

**This table is a diagnostic and is NOT a verdict**, and it is not one for two
independent reasons: (a) the reader refused, so nothing it would have printed
is a graded reading; (b) one of its columns is measurably wrong. It is recorded
only so that the successor's design (§5) rests on measurement.

**Note what the six compressible y+ figures show:** five of six sit **≥ 1.0**,
which is registered outcome (C) — `G-YPLUS` `GATE FAIL` and the wall-resolved
claim withdrawn for those points. **The item was heading for a `GATE FAIL` on
the compressible arm regardless of M1.** Stated here so that nobody later reads
the refusal as having cost this item a favourable result.

---

## 7. `INCOMP` HAS NO ROUTE TO A VERDICT OF ITS OWN, AND THE COMPOSITION RULE IS CITED, NOT INVENTED

**The registration grades the PHYSICS GATES per point.** `G-TRIM`: *"that
point's CD is not a fixed-lift drag"*. `G-YPLUS`: *"y+max ≥ 1.0 on any point ⇒
`GATE FAIL` **there** … withdrawn **for those points**"*. `G-CAPS`: *"a cap-stop
is `NOT A RESULT` **on that point**"*. §2 registered outcome (B) is expressly
per-point.

**But the INSTRUMENT is item-scoped and all-or-nothing, and the instrument is
the grading path.** `maaoa_read.py:168-172` runs the selftest **first** and
returns 2 **before any row is composed**. There is no per-point selftest, no
partial-output path and no per-point exit.

**So there is NO legal route by which `INCOMP` carries a verdict while the item
does not.** Four grounds, each sufficient:

1. **Rule 2 / §2d.** The grading path is fixed at the pre-registration commit
   and is `maaoa_read.py`. To emit `INCOMP`'s row I must run a different reader,
   or a different code path through this one. **Both are substitutions of the
   grading path.**
2. **The numbers are the runner's, not the grader's.** `INCOMP/out/trim.json`
   is written by the process being graded. Grading from it bypasses the control
   apparatus entirely — **which is standing rule 3's whole point.**
3. **§2's own worked precedent, the M6 row:** *"A gate that was not reached is
   stated as not reached, never replaced by a nearer gate that was."* M6's Cp
   gate was never evaluated because an upstream gate failed, and the row says
   so rather than reporting the deviation it did manage to compute. **`MAAOA`'s
   `G-TRIM` on `INCOMP` is that Cp gate.**
4. **Per-point gates do not create a per-point instrument.** The registration's
   per-point structure says what a verdict *would say* once produced. It does
   not authorise producing one by another means, and no clause of the freeze
   confers a partial-grading power. **I decline to invent one.**

**The honest statement, and it is the correct one: the good point is ungraded.**
`INCOMP`'s numbers stand as measurements citing
`/home/ubuntu/certonomous-runs/MAAOA/INCOMP/out/trim.json` and its `trim.log`,
carrying **no verdict, no chip and no band** — and §6.1 records that its
published primal did not converge, so the successor should not assume it grades
`PASS` either.

---

## 8. ⚠ UNRESOLVED — THE FREEZE ASSERTS A PRE-COMPUTE CONTROL PASS THAT NO ARTIFACT ON DISK DATES BEFORE COMPUTE

**Recorded as a finding, and deliberately NOT as a defect finding — it is
unresolved, and saying which is the point.**

`MAAOA_PREREGISTRATION.md` §4 asserts: *"Planted controls: reader selftest
M1–M5 (parse/flip/blind/y+ plant/claim plants), every mutation asserted to
land, **driven PASS before this freeze**."*

**Measured:** the only selftest transcript on disk is
`/home/ubuntu/certonomous-runs/MAAOA/MAAOA_read_20260902T182040Z.txt`, and its
**mtime is 2026-09-02 21:58:19Z — the chain's END, not its start.** The
`182040Z` in the filename is the **chain stamp** (it matches
`COST_MAAOA.txt`'s `stamp=20260902T182040Z`), not the write time. Its contents
are the **refusal**, not a pass. **No artifact dated before first compute
records the M1–M5 pass**, and the run root did not exist before compute, so
none could have been written there.

> **A freeze that asserts a control passed before compute, with no artifact
> dated before compute, is an UNEVIDENCED ASSERTION IN A FROZEN DOCUMENT.**

**This is the same class** as the runScript headers whose declared departure
count did not match their own bytes: a frozen document making a checkable
factual claim that its own artifacts do not check.

**Why this is left unresolved rather than called a defect.** The assertion is
very likely **true** — the reader passes M1 on the static `FIXTURE` constant
today (§2.2), which is the state it would have been in before any run root
existed, so there is no reason to doubt the drive happened. **What is missing
is the evidence, not the event.** Distinguishing *checked-and-found-bad* from
*we-do-not-know* is charter law (§9's `ran_before_found`), and this is the
second. **It is recorded as unknown, and it is not collapsed into the bad one.**

**Forward remedy** is §5 requirement 1, which is first on that list for exactly
this reason. **No verdict, label or gate turns on this finding, and it does not
alter §4's conclusion** — the §2d.1 refusal rests on conditions (2), (3) and
(4), none of which depends on it.

---

## 9. WHAT THIS ADDENDUM DOES NOT DO

- It **alters no gate, threshold, cap or label** of `MAAOA_PREREGISTRATION.md`,
  and appends nothing to it. Original text stands unstruck because **nothing in
  it is withdrawn** — the freeze was honoured end to end and the instrument
  behaved exactly as frozen.
- It **grades nothing** and supplies no verdict for any point.
- It **files, sends, uploads and posts nothing** outside this box (rule 7).
- It **does not authorise the successor.** §5 states requirements; the
  successor is its own pre-registration, frozen before its own first compute,
  and the rule-3 limb flagged at §4.2 goes to verification first.

---

**END OF ADDENDUM 1.**
