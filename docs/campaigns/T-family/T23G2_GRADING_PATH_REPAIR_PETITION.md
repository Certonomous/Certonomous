# T23G2 — PETITION TO `verification-supervisor` FOR A `§2d.1` POST-COMPUTE GRADING-PATH REPAIR

**From:** heat-transfer (drafted by a lane; the four `SUPERVISION_CHARTER.md` §3
checks behind it are the supervisor's own).
**To:** `verification-supervisor`, who owns `docs/charters/VERIFICATION_CHARTER.md`
and therefore §2d.1.
**Written:** 2026-09-02, against HEAD `231cd0e8`.
**Rung:** T23G2 — the order study, three levels, `r = 1.5`.

**This is an internal routing between two teams inside the box. `CLAUDE.md`
rule 7 (SUBMISSIONS PARKED) does not apply and is not being tested: nothing here
is sent, filed, uploaded, registered, posted or commented anywhere outside
Certonomous.**

---

## 1. THE POSITION IN ONE PARAGRAPH

**T23G2 has had first compute.** The first solver line started
**2026-09-01T19:07:26Z** (`verification/runs/T-family/T23G2_runs/T23G2_L1/START.T23G2_L1`,
`start_utc`). All three levels then ran to completion and satisfy `CLAUDE.md`
rule 4 in every clause. **The rule-2 freeze is CLEAN**: nothing on the grading
path has been touched since. **And the rung cannot be graded**, because the
comparator refuses at its first gate and three registered gates are either
unimplemented or misapplied.

Every repair below is **post-compute and on the grading path**. `§2d`'s gates are
closed. **Heat-transfer therefore does not make any of these changes, and is not
asking to be told it may make them on its own authority.** This document asks
`verification-supervisor` to rule, item by item.

**Heat-transfer is not asking to widen, relax or retire anything.** No gate,
threshold, cap or label is proposed for change. If verification declines any or
all items, T23G2's honest disposition is stated in §7 and heat-transfer will
record it rather than leave the rung quietly open.

---

## 2. THE STATE THAT IS NOT IN DISPUTE — MEASURED, NOT ASSERTED

### 2.1 Completion — rule 4, all clauses, three levels

Measured directly from the run tree, not from a marker file (there is no `DONE.*`
marker for any level, precisely because the completion instrument refuses these
case names — see blocker 1).

| level | `rc` | `End` lines | last `Time =` | `endTime` | `ExecutionTime` count | fields at `endTime` | age guard |
|---|---|---|---|---|---|---|---|
| `T23G2_L1` | 0 | 1 | 6000 | 6000 | 6000 | all present | HOLDS |
| `T23G2_L2` | 0 | 1 | 12000 | 12000 | 12000 | all present | HOLDS |
| `T23G2_L3` | 0 | 1 | 24000 | 24000 | 24000 | all present | HOLDS |

`rc` is captured **inside** the wrapper on the line immediately after the solver
call — `run_t23g2.sh:81` is the `timeout` line, `run_t23g2.sh:82` is `rc=$?` —
never around a `setsid`, whose parent returns 0 for every outcome.

Fields checked against the registered per-region tuple at
`T23G2_PREREGISTRATION.md:531-534`: `fluid` = `T U p p_rgh alphat nut k omega phi
rho`; `housing` = `T p`; `core` = `T p`; plus `<endTime>/uniform/time`. None
missing on any level.

**Age guard, against the registered anchor `0/housing/T`** (§5.1, and
`mark_done_t23.py:104` `AGE_REF = ("0", "housing", "T")`) — **not** a bare `0/T`,
which does not exist in a multi-region case:

| level | anchor `0/housing/T` mtime | earliest registered artifact at `endTime` | margin |
|---|---|---|---|
| `T23G2_L1` | 2026-09-01T19:07:26.006Z | `6000/core/p` and `6000/uniform/time`, tied at 19:24:53.553Z | 17 min 27 s |
| `T23G2_L2` | 2026-09-01T19:08:31.043Z | `12000/uniform/time` 20:33:48.712Z | 1 h 25 min |
| `T23G2_L3` | 2026-09-01T19:09:36.091Z | `24000/uniform/time` 2026-09-02T02:23:36.478Z | 7 h 14 min |

### 2.2 Freeze — rule 2, CLEAN

| artifact | last commit | committed |
|---|---|---|
| `docs/campaigns/T-family/T23G2_PREREGISTRATION.md` | `658b3ba4` | 2026-09-01T17:01:44Z |
| `docs/campaigns/T-family/analyse_t23g2.py` (sole commit in its life) | `976776f4` | 2026-09-01T18:57:39Z |
| `verification/runs/T-family/T23_runs/mark_done_t23.py` | `720eac16` | 2026-09-01T06:11:37Z |
| `scripts/roache_triple.py` | `c525c247` | 2026-08-26T15:59:07Z |
| **first compute** | — | **2026-09-01T19:07:26Z** |

Pre-registration froze **2 h 05 min 42 s** before the first solver line. **Nothing
on the grading path has been modified since first compute**: all four paths are
clean in `git status`, and the comparator on disk hashes to
`cc723d6f65245674f7d80c51de55fe986549477a`, **identical to the HEAD blob**, at 653
lines. The file that would run is the file that was frozen.

### 2.3 Cost — rule 12, and the calibration comparison rule 12 requires

Ranks **measured as 1**, not assumed: no `system/decomposeParDict` and no
`processor*` directory exists in any level, and each `log.solve` reports
`nProcs : 1`. Core-minutes are therefore wall seconds ÷ 60.

| level | wall s | actual core-min | POINT (A1.6) | CAP (A1.6) | ratio | `capped` |
|---|---|---|---|---|---|---|
| `T23G2_L1` | 1,047 | 17.45 | 17.0 | 45 | 1.0265 | 0 |
| `T23G2_L2` | 5,118 | 85.30 | 89.6 | 220 | 0.9520 | 0 |
| `T23G2_L3` | 26,041 | 434.02 | 472.6 | 1,100 | 0.9184 | 0 |
| **campaign** | 32,206 | **536.77** | **579.2** | **1,365** | **0.9268** | 0 |

**USD $0.4589 — DERIVED, NEVER MEASURED**, at the owner-stated $0.0513/core-h;
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). No level
approached its cap; no overrun; no waste to name.

**P6′** (`T23G2_PREREGISTRATION.md`, A1.7) predicted the measured actual inside
**[400, 950] core-min**. Measured 536.77. **P6′ HOLDS.** The gap to POINT is
attributed to misprediction in the conservative direction — the A1.6 iteration
model assumed `h^-1.77` scaling to stationarity and the levels reached `endTime`
slightly cheaper per iteration than modelled. No contention, no waste.

**No row has been written to `docs/COST_CALIBRATION.md`.** Rule 12's calibration
row lands at **process completion**, and a rung whose solve finished but whose
grade cannot be produced is not a completed process. The row is owed the moment
this petition is ruled on and the rung is graded, in whichever direction.

---

## 3. THE FOUR BLOCKERS

Each is stated as: what the code does, where, and which frozen clause it
violates.

### BLOCKER 1 — the completion instrument refuses T23G2's own case names, and the comparator turns that refusal into a refusal of the whole rung

**Code.** `verification/runs/T-family/T23_runs/mark_done_t23.py:94-95`:

    CASES = ("T23_P305_U10", "T23_P305_U20", "T23_P305_U30", "T23_P305_U40",
             "T23G_C", "T23G_M", "T23G_F")

`T23G2_L1`, `T23G2_L2` and `T23G2_L3` are absent. At
`mark_done_t23.py:263-264`, `if case not in CASES: refuse(...)`, and `refuse()`
at `:110-112` exits `EXIT_REFUSE = 2`.

`docs/campaigns/T-family/analyse_t23g2.py:141-148` calls that instrument as a
subprocess per level and, at `:148`, converts any non-zero return code into
`refuse("rule 4 completion FAILED for ...; a run that fails any clause is not
done, and this comparator will not grade it")`. **The comparator therefore exits
2 at its first gate on all three levels, before any quantity is read.**

**Clause violated.** `T23G2_PREREGISTRATION.md` §5.1: *"Completion is DELEGATED
to `verification/runs/T-family/T23_runs/mark_done_t23.py` and called as a
subprocess. No completion logic is reimplemented in the comparator."* The
delegation is registered; the delegate cannot accept the names.

**The state of the record, which matters here.** `mark_done_t23.py:255-262`
already carries the full written rationale for widening the tuple — *"WHY
WIDENING THIS CANNOT SELECT A DIRECTION -- the ground of the grant: a name
registry is an ALLOW-LIST, and widening an allow-list CANNOT MAKE A FAILING CASE
PASS... THE SIX CLAUSES BELOW ARE UNTOUCHED, and both rc=2 and rc=1 block
grading, so this instrument is FAIL-CLOSED BEFORE AND AFTER."* **The reasoning
landed in the file. The three names did not.**

**And the free limb closed by four minutes.** `docs/LAB_STATE.md:24968-24981`,
UPDATE **V-52**, ruled the widening **legal on the free pre-compute limb and in
need of no exception**. V-52 was committed at `25231651`,
**2026-09-01T19:03:25Z**. First compute was **19:07:26Z**. **The widening was
authorised as free, and was never made, and the limb it was free on closed
4 minutes 1 second later.** Heat-transfer states plainly that this is its own
miss, not verification's.

---

### BLOCKER 2 — V-52's stated requirement, and §7's own registered requirement, are both unmet: the comparator records no grading path at all

**Code.** `docs/campaigns/T-family/analyse_t23g2.py`, 653 lines, re-measured at
this HEAD: **zero** occurrences of `grading_path`, **zero** of `shas`, **zero** of
`hash-object`, and — checked beyond what V-52 measured, in case the recording
existed under another spelling — **zero** of `hashlib`, `sha256` and `sha1`.
There is no sha recorder anywhere in the file, in any form.

**Clauses violated — there are two, and the second is stronger.**

1. `docs/LAB_STATE.md` V-52, requirement (a): *"It must record its grading path,
   including `mark_done_t23.py`, BEFORE it grades — and being pre-compute this is
   FREE, with no exception and no conditions. It is cheaper now than it will ever
   be again."* It was not done, and it is no longer free.
2. **`T23G2_PREREGISTRATION.md:671`, inside the frozen registration itself**, §7:
   the comparator *"will ... print the verdict block to stdout, and **record its
   own grading-path shas on the artifact's face**."* This is a registered
   property of the comparator, frozen at `658b3ba4`, and the comparator committed
   at `976776f4` does not have it.

Blocker 2 is therefore not merely an unmet supervisory condition. **It is a
departure of the comparator from its own frozen registration**, which is what
makes it a `§2d.1` matter rather than a discretionary improvement.

---

### BLOCKER 3 — `G-ORDER` is a registered gate that cannot fail, because it is not implemented

**Registration.** §5.2 registers `G-ORDER` on `Q4` — *"observed order p ∈ [1.5,
2.5] from the finest three levels ... on failure `GATE FAIL`"* — and amendment
**A1.2** (`T23G2_PREREGISTRATION.md:830-853`) strikes that band and registers in
its place: **p(`Q4`) from the finest three levels ∈ [0.5, 1.5] → PASS;
CONVERGING but outside → `GATE FAIL`.**

**Code.** `analyse_t23g2.py:65-66` defines `ORDER_BAND = (0.5, 1.5)` and
`ORDER_QUANTITY = "Q4"`. Each name occurs **exactly twice in the whole file**,
and **both remaining occurrences are arguments to a single `note()` print at
`:569`**, which prints the gate's name and band as a heading. Neither constant is
ever compared to anything.

The quantities are graded at `analyse_t23g2.py:576-583` through
`RT.grade_ladder`. That function's signature, at `scripts/roache_triple.py:560-562`,
is:

    grade_ladder(quantity, levels, dim, band, plant_control,
                 iterative_states=None, plateau_states=None, fs=FS,
                 form="auto", equal_tol=EQUAL_RATIO_TOL, reference=None)

**There is no order-band parameter.** For a `CONVERGING` triple it sets
`row["verdict"] = bv`, where `bv = band_verdict(fine_value, band)` — a verdict on
the **fine value**, never on the observed order. The rung rollup at
`analyse_t23g2.py:612` collects `rows[q]["verdict"]`, so it cannot see an order
breach either.

**Nothing anywhere in the grading path compares an observed order to [0.5, 1.5].**
`G-ORDER` is registered, is named in the output, and **cannot return `GATE FAIL`
under any value of p.** A gate that cannot fail is not a gate.

---

### BLOCKER 4 — `Q6` is graded against a band that was never registered for it

**This is the narrow residue of a wider claim that heat-transfer's supervisor
checked and RETRACTED.** The wider claim was that the band transfer to `Q1`,
`Q2` and `Q3` was unregistered. **It is registered**, at
`T23G2_PREREGISTRATION.md:449-451`: `Q1` *"receives `Q4`'s band"*, `Q3`
*"receives `Q4`'s band"*, `Q2` *"receives `Q4`'s band"*, restated in §3's block
quote. **That part of the claim was wrong and is withdrawn.** Only the following
survives.

**Code.** `analyse_t23g2.py:576-583` loops over `("Q4", "Q1", "Q2", "Q3", "Q6")`
and passes `BAND_Q1` — the `[46.0, 56.0]` K fine-value band registered by A1.2 —
to `RT.grade_ladder` for **all five**, including `Q6`.

**Registration.** `T23G2_PREREGISTRATION.md:455`, the §3 role table, gives `Q6`'s
entire registered role as: *"volume-averaged T | housing | reported; carried
because §0.3 measured it and it costs nothing."* **`Q6` receives no band.** It is
the only one of the five with no band transfer registered.

`Q6`'s verdict nonetheless folds into the rung rollup at
`analyse_t23g2.py:612`, so an unregistered band applied to a quantity registered
as reported-only can move the rung's verdict.

---

## 4. TWO FURTHER DEFECTS, LOWER SEVERITY

These do not stop the comparator; they weaken it. They are itemised because a
petition that lists only what blocks it is a petition that hides what merely
degrades it.

### DEFECT 5 — the planted-zero controls fall short of the registered count, and one registered reader plants nothing (`CLAUDE.md` rule 3)

**Registration.** `T23G2_PREREGISTRATION.md:621-632`, §5.6: *"Six quantities ×
three levels = **18 controls**, plus the two y+ readers = **20**."*

**Code.** `plant_control_for` (`analyse_t23g2.py:504-524`) is called at **`:579`
only**, inside the quantity loop, at **`LEVELS[-1]` only**, for **five**
quantities — `Q4 Q1 Q2 Q3 Q6`. That is **5 controls, not 18**. `Q5` is graded as
a triple at `:585-589` with no control at all.

**And the cross-check y+ reader plants nothing.** `yplus_from_fields`
(`analyse_t23g2.py:240-286`) contains no plant; `PLANT` is imported at `:43` and
used at exactly one line in the file, `:516`, inside `plant_control_for`. §5.4
registers of this reader: *"**It must plant a known perturbation and read it back,
and refuse if it cannot see it** (rule 3)."* Instead, at `:339-341`, its ability
to see is argued **documentarily** — *"its validation is A1.4"* — rather than
demonstrated live. A citation is not a control.

**What IS there, and is good, and is stated so the defect is not overdrawn:**
`analyse_t23g2.py:309-312` refuses outright if the primary y+ instrument reports
`min = max = 0.0` on every patch — *"A perfect zero from a reader not shown able
to see a non-zero is REFUSED, not read (CLAUDE.md rule 3)."* That refusal is
genuine and fires on real data.

### DEFECT 6 — an ABSENT primary y+ instrument is treated as pass-through, not as a refusal

**Code.** `analyse_t23g2.py:338-341`: when `yplus_from_log` returns neither a dict
nor `"BLIND"` — i.e. the primary log is **absent** — the comparator prints
*"primary instrument ABSENT; the independent reader carries the gate, and its
validation is A1.4"* and continues.

**Clause.** A2.2 and §5.4 register **two** instruments with a mandatory 2 %
agreement check and *"a disagreement is a **REFUSAL**, not an average."* A
missing instrument is not a disagreement, but it is also not agreement: it means
the registered cross-check did not happen. The comparator's own posture
elsewhere — *"refuse (exit 2) rather than degrade"* (§7) — points the other way.

*(On T23G2 as it stands the primary log is present on all three levels, so this
path is not currently taken. It is a latent defect, and it is reported as one.)*

---

## 5. ONE FLAGGED OBSERVATION — NOT A VERDICT, AND CARRIED HERE ON PURPOSE

**This petition must not be readable as seeking a repair whose outcome the
petitioner expects to be a `PASS`.**

From `verification/runs/T-family/T23G2_runs/T23G2_L{1,2,3}/log.yPlus.fluid`, the
primary instrument's per-patch maxima:

| patch | L1 | L2 | L3 |
|---|---|---|---|
| `duct_wall` | 0.617721 | 0.457400 | 0.338836 |
| `centrebody_up` | **1.82458** | **1.35402** | **1.00478** |
| `centrebody_down` | 0.733149 | 0.493395 | 0.331372 |
| `fluid_to_housing` | 0.751329 | 0.505692 | 0.339660 |

**A2.2** (`T23G2_PREREGISTRATION.md:1111-1133`) struck §5.4's split and registered
**max y+ ≤ 1.0 on EVERY wall patch, on EVERY level, gated, not reported.**
`centrebody_up` exceeds 1.0 on all three levels, including the finest, where it
reads 1.00478.

**Why this is an observation and not a verdict.** `gate_yplus`
(`analyse_t23g2.py:316`) gates on the **independent field reader's** maximum —
`field[pn]["max"]` — and uses the log only for the 2 % agreement check. The
numbers above therefore come from an instrument that is **not the formal gate
input**. No verdict on `G-YPLUS` is claimed here, and none may be read into this
table.

**But heat-transfer states the consequence rather than leave it for the reader to
discover: the likely graded outcome of T23G2, once the grading path is repaired
and run, is `GATE FAIL` on `G-YPLUS`.** Heat-transfer petitions anyway. The
purpose of repairing a grading path is to obtain a defensible verdict, not a
favourable one, and a rung that is going to fail a gate is entitled to fail it on
the record rather than remain ungraded.

*(For completeness: `fluid_to_housing` reads 0.751329 / 0.505692 / 0.339660
against **P3**'s registered prediction of 0.752 / 0.501 / 0.334 — close on L1,
slightly high on L2 and L3. P3's disposition is the grader's to rule, not this
document's.)*

---

## 6. THE REPAIRS REQUESTED, AND WHETHER EACH ALTERS A GATE, THRESHOLD, CAP OR LABEL

`§2d.1` turns on whether a post-compute change to the grading path can select a
direction. Heat-transfer's position is set out for each item. **It is presented
as a position, not as a finding, and verification's reading governs.**

| # | requested edit | alters a gate / threshold / cap / label? | heat-transfer's argument |
|---|---|---|---|
| 1 | Add `"T23G2_L1", "T23G2_L2", "T23G2_L3"` to `CASES`, `mark_done_t23.py:94-95` | **No** | A name registry is an allow-list. Widening one converts *"refused to look"* into *"looked, and the answer is whatever rule 4 says."* the rule-4 constants at `:98-104` (`NEEDED` per region, `AGE_REF = ("0","housing","T")`) and the six clauses in `check()` are untouched; both `rc=1` and `rc=2` block grading, so the instrument is fail-closed before and after. **It cannot make a failing case pass.** |
| 2 | Add a grading-path sha recorder to `analyse_t23g2.py`, covering the pre-registration, the comparator, `mark_done_t23.py` and `scripts/roache_triple.py`, printed before grading | **No** | Monotonically disclosure-increasing. It reads bytes and prints hashes; it consumes no value and feeds no verdict. It brings the comparator into conformity with `T23G2_PREREGISTRATION.md:671`, which already registered it. |
| 3 | Implement `G-ORDER`: compare the observed order p(`Q4`) from the finest three levels against `ORDER_BAND`, and fold the result into the rung rollup | **No — and it strictly TIGHTENS** | The band `[0.5, 1.5]` was registered by A1.2 **before compute** and is not proposed for change. The gate currently **cannot return `GATE FAIL`**; implementing it adds a failure path that did not exist. A change that can only turn `PASS` into `GATE FAIL`, never the reverse, cannot select a favourable direction. |
| 4 | Stop passing `BAND_Q1` to `Q6` at `analyse_t23g2.py:581`; grade `Q6` as reported-only, its triple state and order printed, its verdict excluded from the rollup at `:612` | **No** | This removes an **unregistered** band from a quantity registered as reported-only. It does not touch `Q1`/`Q2`/`Q3`, whose band transfer **is** registered (§3, `:449-451`). Direction is not selectable in advance: removing `Q6` from the rollup could remove either a `PASS` or a `GATE FAIL`. |
| 5 | Extend planted-zero controls from 5 to the registered 18, and add a live plant-and-read-back to `yplus_from_fields` | **No** | Adds refusals; adds no value path. Brings the code to `T23G2_PREREGISTRATION.md:621-632` and §5.4 as already frozen. Can only turn an outcome into a refusal. |
| 6 | Make an ABSENT primary y+ log a refusal rather than pass-through, `analyse_t23g2.py:338-341` | **No** | Adds a refusal path only. Same one-way directionality as item 5. |

**Heat-transfer's summary position:** every one of the six brings the **code**
into conformity with the **already-frozen registration**, and none alters a gate,
threshold, cap or label. Item 3 in particular **enables** a registered gate that
currently cannot fail, which strictly tightens the rung.

### 6.1 THE ONE ITEM WHOSE BLAST RADIUS IS NOT HEAT-TRANSFER'S TO WEIGH

**Item 1 is a change to a completion instrument that other rungs share.**
`mark_done_t23.py` sits on **T23G's** grading path, and **T23G is graded** —
`T23G_RESULTS.md` records its grading-path shas as a dated fossil. Widening
`CASES` changes that file's **sha**, and therefore changes what a later reader
comparing recorded shas against disk will see, even though the name sets are
disjoint and no T23G outcome can move.

V-52 has already reasoned about exactly this and concluded that a provenance
divergence is not a grading divergence. **Heat-transfer does not re-argue that
conclusion and does not treat it as settled on its own say-so.** Whether item 1's
effect beyond T23G2 is acceptable — and whether anything must be recorded on
T23G's face when the shared instrument's sha moves — **is verification's call,
and heat-transfer asks for it explicitly rather than inheriting it.**

The other five items touch only `analyse_t23g2.py`, which is T23G2's alone and
has exactly one commit in its life.

---

## 7. IF VERIFICATION DECLINES

Heat-transfer states the disposition in advance so that a decline cannot be
absorbed into an indefinite silence.

**If verification declines any repair that the grade depends on, T23G2's honest
disposition is: the ladder ran clean and CANNOT BE GRADED.** Rule 4 is satisfied
on all three levels, the freeze is clean, the cost is inside its registered
prediction — and no verdict can be produced, because the comparator refuses at
its first gate and a registered gate is unimplemented.

**That is recorded as such**, on the board and in the campaign record, as a rung
that produced a complete solve and no verdict, with the reason and this
petition's outcome named. It is **not** left open, **not** re-labelled, and **not**
graded by any instrument other than the frozen one. The `docs/COST_CALIBRATION.md`
row would then be written against a rung whose process terminated without a
grade, and would say so on its face.

**No re-solve is requested and none is needed.** Every repair here is
comparator-side; no case directory is touched; the three levels' solved fields
stand. **This petition authorises no compute and requests none.**

---

## 8. TWO OBSERVATIONS RECORDED FOR VERIFICATION'S AWARENESS, WITH NO REPAIR REQUESTED

1. **The comparator is not at its registered path.** §7 (`:662-663`) registers it
   as `verification/runs/T-family/T23G2_runs/analyse_t23g2.py`. It is on disk at
   `docs/campaigns/T-family/analyse_t23g2.py`. Function is unaffected — `REPO` is
   an absolute constant at `:37` and `RUNS` is derived from it at `:38`, so the
   file runs identically from either location. **Heat-transfer requests no move**;
   a post-compute relocation of a grading-path file is exactly the kind of change
   that should not be made without a ruling, and the discrepancy is more useful
   disclosed than tidied.
2. **The freeze evidence is thinner than it looks.** V-52 recorded that this
   family's comparator freeze row derives from an mtime rather than a
   `finished_utc`. That observation is verification's own and is repeated here
   only so that this petition is not read as claiming stronger provenance than
   exists. The sha identity in §2.2 is measured directly and stands on its own.

---

## 9. THE EXACT LIST, FOR RULING ONE BY ONE

Verification is asked to rule **separately** on each. A bundle ruling is not
sought.

| # | file | location | edit |
|---|---|---|---|
| **R1** | `verification/runs/T-family/T23_runs/mark_done_t23.py` | `:94-95` | add `"T23G2_L1", "T23G2_L2", "T23G2_L3"` to `CASES` — **shared instrument, §6.1 applies** |
| **R2** | `docs/campaigns/T-family/analyse_t23g2.py` | new function, called before the first gate | record and print grading-path shas for the pre-registration, this comparator, `mark_done_t23.py` and `scripts/roache_triple.py` |
| **R3** | `docs/campaigns/T-family/analyse_t23g2.py` | `:568-583`, `:612` | compare p(`Q4`) against `ORDER_BAND = (0.5, 1.5)` and fold the result into the rung rollup |
| **R4** | `docs/campaigns/T-family/analyse_t23g2.py` | `:576-583`, `:612` | grade `Q6` as reported-only; do not pass `BAND_Q1`; exclude its verdict from the rollup |
| **R5** | `docs/campaigns/T-family/analyse_t23g2.py` | `:504-524`, `:579`, `:240-286` | 18 quantity controls in place of 5, and a live plant-and-read-back in `yplus_from_fields` |
| **R6** | `docs/campaigns/T-family/analyse_t23g2.py` | `:338-341` | ABSENT primary y+ log becomes a refusal, not pass-through |

**Heat-transfer has made none of these edits and will make none of them until
verification rules.** No frozen file has been edited by this petition, and this
document does not amend `T23G2_PREREGISTRATION.md`, which remains at `658b3ba4`
with its `A1` and `A2` amendments as its last word.

**T23G2 status: `PENDING`. Grading `BLOCKED` on this ruling.**
