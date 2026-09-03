# T25R6a — PETITION TO `verification-supervisor` FOR A §2d.1 POST-COMPUTE GRADING-PATH RULING ON ONE PREDICATE THAT NO RUN COULD EVER SATISFY

**From:** heat-transfer (drafted by a lane; the `SUPERVISION_CHARTER.md` §3 checks
behind it are the supervisor's own, and the strengthening in §7 is the
supervisor's finding, not the lane's).
**To:** `verification-supervisor`, who owns `docs/charters/VERIFICATION_CHARTER.md`
and therefore §2d.1 (`VERIFICATION_CHARTER.md:1914`, the four conditions at
`:1937`).
**Written:** 2026-09-03, against HEAD `9e7bc119`.
**Rung:** T25R6a, the C5 outer arm — `verification/runs/T-family/T25R6a_C5_OUTER_runs/`.

**Precedent, and it is why this document exists at all.** The T3/T5 spine §2d.1
repair was **not applied by heat-transfer on its own authority**. It was
petitioned (`docs/campaigns/T-family/SPINE_2D1_GRADING_PATH_PETITION.md`) and
**ruled item by item at commit `ad9eda53`** — *"the spine petition RULED item by
item: A GRANTED, B GRANTED on a ground the petition did not lead with, C
recorded"* — with **five binding conditions attached to the grant**, one of which
verification added against the petitioner. This rung takes the same route. **The
diff in §6/§7 is NOT APPLIED, no verdict is written, and this document grants
itself nothing.**

**This is an internal routing between two teams inside the box. `CLAUDE.md`
rule 7 (SUBMISSIONS PARKED) does not apply and is not being tested: nothing here
is sent, filed, uploaded, registered, posted or commented anywhere outside
Certonomous.**

**Every line quoted below was re-read from the file at the moment this document
was written**, not carried from notes and not carried from the brief this lane
was handed. Where the brief and the file disagreed, the file won; no such
disagreement was found on the citations in §3.

---

## 0. THE BLOCKED RESULT THIS PETITION NAMES

Sanaa's 2026-09-03 ~20:00Z ruling, verbatim
(`etc/sessions/2026-09-03T2000Z_sanaa_governance_reform.md:32-34`):

> *"Petitions, rulings, and charter amendments require a blocked result to name.
> No result blocked → no petition; the team decides locally and records the
> decision as a lesson."*

**The blocked result is `G-T6a`.**

`G-T6a` is registered at `docs/campaigns/T-family/T25R6a_PREREGISTRATION.md:473`:

> **`G-T6a` PASSES iff `Σ CAP(C5) ≤ 20,000` core-minutes**

`grade_t25R6a.py` returns at step `[5]` and **never reaches step `[7]` where
`G-T6a` is evaluated.** `Σ CAP(C5)` was **never computed by the frozen grader**.
The rung therefore **cannot reach a verdict on the gate it exists to decide**,
and it cannot reach one through **any** run, because the obstacle is not the
data — it is the predicate (§3). This is a blocked result in the strict sense the
ruling requires: not a delayed one, not an inconvenient one, an **unreachable**
one.

---

## 1. THE FACT THIS PETITION LEADS WITH, BECAUSE IT IS THE STRONGEST EVIDENCE AGAINST ITS OWN INTEREST

> ### **THE REPAIR MOVES THE VERDICT FROM `NOT A RESULT` TO `GATE FAIL`.**
> ### **AWAY FROM A `PASS`, NOT TOWARD ONE.**

| | pre-repair (published, on disk, unaltered) | post-repair |
|---|---|---|
| step reached | `[5]` equivalence control | `[7]` `G-T6a` |
| exit code | **4** (`EXIT_NOT_A_RESULT`, `grade_t25R6a.py:57`) | **3** |
| verdict | **`NOT A RESULT`** | **`GATE FAIL`** |
| ground | *"the equivalence control FIRED (prereg 6.4)"* | `Σ CAP(C5) = 20,006.8 > 20,000`, a ×1.00034 breach |
| `Σ CAP(C5)` | **never computed** | **20,006.80 core-min** |

**Nothing here was repaired in the direction anyone wanted.** Heat-transfer is
asking to be allowed to reach a **failing** gate. If verification wishes to test
this petition's motive, that row is the test, and it is stated first rather than
buried.

---

## 2. THE POSITION IN ONE PARAGRAPH

T25R6a has had first compute; its four cases are rule-4 clean; and the rung
**cannot be graded on any run of any quality**, because its step-`[5]` equivalence
predicate is **tautologically true for every value its delegated comparator can
return**. §2d's gates are closed, so the fix is post-compute and is **not
heat-transfer's to make**. This document asks `verification-supervisor` to rule.
**No gate, threshold, band, cap, price table, ceiling or label is proposed for
change.** If verification declines, the honest disposition is stated in §8 and
heat-transfer will record it rather than leave the rung quietly open.

---

## 3. THE DEMONSTRABLE ERROR — established by reading two FROZEN contracts against each other

### 3.1 The predicate, quoted by line

`verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py`, step `[5]`:

    :433        for lvl in LEVELS:
    :434            r = cmp_mod.compare(os.path.join(HERE, "C5_%s" % lvl),
    :435                                os.path.join(HERE, "B0_%s" % lvl))
    :436            equiv["C5_%s" % lvl] = str(r)
    :437            if r is not True and r != 0:
    :438                equiv_ok = False

**`grade_t25R6a.py:437` reads `if r is not True and r != 0:`.**
(`LEVELS = ["L1", "L3"]`, `grade_t25R6a.py:65`.)

### 3.2 The delegated comparator's contract, quoted by line

`verification/runs/T-family/T25R5_LINSOLVER_runs/compare_arms_t25R5.py`:

    :253    def compare(arm_case, base, quiet=False):
    ...
    :282        res["fired"] = fired
    ...
    :292        return res

**`compare()` builds a dict `res` and returns it.** It has exactly one `return`,
at `:292`, and it returns `res`. `res["fired"]` — the list of channels that
crossed a registered disqualifying threshold — is set at `:282` and is a key
**inside** that dict.

### 3.3 The consequence, which is arithmetic and not a matter of taste

`r` is a `dict`. Therefore:

- `r is not True` — a `dict` is never the `True` singleton. **Always true.**
- `r != 0` — a `dict` never compares equal to `0`. **Always true.**

> ### **THE PREDICATE IS TAUTOLOGICALLY TRUE FOR EVERY POSSIBLE RETURN.**
> ### **`equiv_ok` IS SET `False` UNCONDITIONALLY. THE GATE IS UNSATISFIABLE.**
> ### **NO RUN, OF ANY QUALITY, COULD EVER HAVE PASSED IT.**

The rung was refused **by its own arithmetic, not by its physics**. This is
established by reading two frozen files' contracts against each other. It is not
a preference for a different verdict; it is a type error with a proof.

### 3.4 THE PUBLISHED ARTIFACT ALREADY CONTRADICTED ITSELF ON ITS OWN FACE

`verification/runs/T-family/T25R6a_C5_OUTER_runs/T25R6a_VERDICT.json`, read at
the moment of writing and **not edited**:

    "verdict": "NOT A RESULT"
    "ground":  "the equivalence control FIRED (prereg 6.4)"
    "equivalence": {
      "C5_L1": "{... 'maxdT': 9.000018508231733e-09, ... 'fired': []}",
      "C5_L3": "{... 'maxdT': 4.2100003838640987e-07, ... 'fired': []}"
    }

**The file states its ground as "the equivalence control FIRED" while carrying
`'fired': []` at BOTH levels, in the same file.** `grade_t25R6a.py:436`
stringifies the whole returned dict into the artifact, so the evidence that no
channel fired was **serialised alongside the claim that one had, and then
discarded by the predicate at `:437`.**

The measured channels against their registered disqualifying thresholds
(`T25R6a_PREREGISTRATION.md` §6.4, carried unchanged from T25R5 §4):

| channel | registered DISQUALIFYING threshold | `C5_L1` | `C5_L3` | margin |
|---|---|---|---|---|
| `max\|ΔT\|`, coolant **and** module | **1.000e-03 K** | 9.000019e-09 | 4.210000e-07 | ×1.1e5 / ×2.4e3 |
| `max\|Δp_rgh\|` | **1.0 Pa** | 1.000008e-06 | 3.000008e-06 | ×1.0e6 / ×3.3e5 |
| `max\|ΔU\|` | **1.0e-03 m/s** | 2.139000e-08 | 2.780000e-09 | ×4.7e4 / ×3.6e5 |
| **`fired`** | — | **`[]`** | **`[]`** | — |

Three to six orders inside every registered threshold, on both levels.

---

## 4. THE FOUR §2d.1 CONDITIONS — carried across from `T25R6a_C5_REGRADE_RECORD.md` §4 and RE-VERIFIED against that record, not retyped from a brief

`VERIFICATION_CHARTER.md:1914` (§2d.1) permits a change on the grading path after
the first graded solve **when, and only when, all four hold.** The rung's own
record states them at
`verification/runs/T-family/T25R6a_C5_OUTER_runs/T25R6a_C5_REGRADE_RECORD.md:205-252`.

### (1) IT REPAIRS A DEMONSTRABLE ERROR RATHER THAN A PREFERENCE

§3 above. A gate no run can pass is not a strict gate; it is a broken one.
**This lane's assessment: strong.** The proof is type arithmetic over two frozen
contracts and does not depend on any physical quantity.

### (2) THE ERROR WAS ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS — §2d.1's load-bearing condition

**The record rests condition (2) on TWO instruments, and the property that makes
them admissible is that NEITHER OF THEM GRADES ANYTHING.**

- **The comparator's `fired` list.** `grade_t25R6a.py` computes it (via
  `compare()`, `compare_arms_t25R5.py:282`), serialises it into the verdict JSON
  at `:436`, and then **discards it — it gates nothing.** It reads `[]` at both
  levels. The published artifact carried, on its own face, the evidence that no
  channel fired while its `ground` field said one had.
- **The comparator's rule-3 planted-zero control.** It grades nothing; its sole
  function is to prove the reader can see a known non-zero. Re-verified against
  `T25R6a_C5_REGRADE_RECORD.md:79-91`: `PLANT = 1.234e-03` K
  (`compare_arms_t25R5.py:27`), planted **by line index** into cell 0 and cell
  n−1 of **both** regions, on a copy, read back **from disk**,
  `PLANT_TOL_K = 1e-9` (`:36`); recovered `1.234000e-03` exactly;
  **16/16 SEEN** (4 plants × 4 cases, driven 2026-09-03). **`PLANT` is ABOVE the
  `E1` disqualifying threshold `E1_T_K = 1.000e-03` K (`:41`) ON PURPOSE**, so the
  control proves **the gate can FIRE**, not merely that the reader can read. It is
  what converts `fired == []` from a silent zero into evidence, and it is the
  reason CLAUDE.md rule 3 is satisfied rather than merely invoked.

**Neither instrument knows anything about `Σ CAP`, the six ladder runs, or the
20,000 ceiling**, so neither can have been selected to move `G-T6a` in a wanted
direction — which is exactly the property §2d.1 is cut to require. Add §1: the
direction it actually moves is **toward a `GATE FAIL`.**

### (3) THE RECORD DISCLOSES IT, NAMES THAT INSTRUMENT, AND QUANTIFIES WHAT MOVED

`T25R6a_C5_REGRADE_RECORD.md` §4, table reproduced at §1 of this petition. What
moves is quantified line by line, including the values that go from *never
computed* to computed (`Σ CAP(C5)` = 20,006.80; `f_C5(L1)` = 10.651858;
`f_C5(L3)` = 7.059383; predictions `P-1..P-3` from *never evaluated* to
WINS/WINS/WINS). **Met.**

### (4) THE PRE-REPAIR VALUES ARE RECORDED BESIDE THE PUBLISHED ONES

`T25R6a_VERDICT.json` **stands on disk unaltered** and is quoted verbatim in §3.4
above and in the record. It is **struck by the record, never rewritten**
(CLAUDE.md rule 6). **Met, and the pre-repair state is a refusal at step `[5]`,
so nothing any published record currently asserts about `Σ CAP` can move — there
is no published `Σ CAP` to move.**

---

## 5. WHAT VERIFICATION SHOULD KNOW BEFORE IT GRANTS: THE NUMBER THE REPAIR UNBLOCKS IS ITSELF ON SANAA'S DESK

Granting this petition does **not** settle the rung. It moves the rung from
"cannot be read" to "reads `GATE FAIL` by 6.80 core-min against a measurement
whose own registered resolution is ±~6.7 %."

`Σ CAP(C5) = 20,006.80` core-min against a ceiling of 20,000 — a breach of
**+6.80**, ×1.00034 — with a registered uncertainty interval of
**[18,801.4 , 21,480.1] core-min**
(`T25R6a_C5_REGRADE_RECORD.md:157`). **The interval straddles the ceiling: the
measurement cannot resolve which side of 20,000 the ladder falls on.** That
question is with Sanaa, with **no recommendation attached from heat-transfer and
no widening requested**, and this petition does not touch it. **Verification is
being asked to unblock a reading, not to bless a number.**

---

## 6. THE DIFF AS THE REGRADE RECORD PROPOSED IT — NOT APPLIED

`T25R6a_C5_REGRADE_RECORD.md:254-269`, reproduced verbatim:

```diff
@@ grade(), step [5] EQUIVALENCE CONTROL @@
         r = cmp_mod.compare(os.path.join(HERE, "C5_%s" % lvl),
                             os.path.join(HERE, "B0_%s" % lvl))
         equiv["C5_%s" % lvl] = str(r)
-        if r is not True and r != 0:
+        if not isinstance(r, dict):
+            refuse("compare() returned %r, not the dict its frozen contract "
+                   "promises; the equivalence limb cannot be read." % type(r))
+        if r["fired"]:
             equiv_ok = False
```

---

## 7. THE SUPERVISOR'S AMENDMENT — THE PETITIONED FORM IS THE STRENGTHENED ONE, AND THIS IS A FINDING THE DRAFTING LANE DID NOT CATCH

**Heat-transfer does not petition the §6 form.** On personal reading of the
proposed diff the supervisor found a residual defect in it, and the petitioned
form is the strengthened one below. This is disclosed rather than quietly
substituted, because verification is entitled to know that the first form was
wrong and who caught it.

**The defect in the §6 form.** `r["fired"]` is a **direct key access**. The
`isinstance` guard covers the **type** and leaves the **key** unguarded. If
`compare()` ever returns a dict lacking the `fired` key, `r["fired"]` raises
`KeyError` — an uncaught traceback. **A traceback is a DEGRADE, and this lab's
comparators REFUSE (exit 2) rather than degrade** (CLAUDE.md rule 4's binding
artifact language; the same discipline the rung's own grader already implements).
A repair that trades a tautology for a traceback has not finished the job.

**The petitioned form:**

```diff
@@ grade(), step [5] EQUIVALENCE CONTROL @@
         r = cmp_mod.compare(os.path.join(HERE, "C5_%s" % lvl),
                             os.path.join(HERE, "B0_%s" % lvl))
         equiv["C5_%s" % lvl] = str(r)
-        if r is not True and r != 0:
+        if not isinstance(r, dict):
+            refuse("compare() returned %r, not the dict its frozen contract "
+                   "promises; the equivalence limb cannot be read." % type(r))
+        if "fired" not in r:
+            refuse("compare() returned a dict with no 'fired' key; the channel "
+                   "the registration says gates this rung is absent and the "
+                   "equivalence limb cannot be read.")
+        if r["fired"]:
             equiv_ok = False
```

**`refuse()` verified at source, not assumed:** `grade_t25R6a.py:134-136` is

    def refuse(msg):
        print("REFUSE: " + msg)
        sys.exit(EXIT_REFUSE)

with `EXIT_REFUSE = 2` at `grade_t25R6a.py:55`. **It exits 2.** Both new limbs
call that same function, so both refuse rather than degrade, and both are
distinguishable in the log by their message.

> **THE STRENGTHENING MOVES NO GATE AND NO THRESHOLD. IT ONLY ADDS A REFUSAL.**
> A refusal is the **safe direction**: it can convert a would-be `PASS`, `GATE
> FAIL` or traceback into an explicit `REFUSE`, and it can never convert anything
> **into** a `PASS`. Under CLAUDE.md rule 5's ordering principle — a gate may turn
> a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse — this
> addition is on the permitted side by construction.

**Neither limb fires on the data now on disk.** `compare()` has one `return`
(`compare_arms_t25R5.py:292`), it returns `res`, and `res["fired"]` is set
unconditionally at `:282` before it. So on today's frozen comparator the
`isinstance` limb and the `"fired" not in r` limb are both **dead code that
cannot fire** — they exist to keep the predicate honest if the delegated frozen
contract is ever superseded. That is disclosed so that verification does not
grant a stronger guard believing it is currently load-bearing: **it is not; it is
insurance.**

---

## 8. WHETHER THE REQUESTED REPAIR ALTERS A GATE, THRESHOLD, CAP OR LABEL

| what changes | gate? | threshold? | cap? | label? |
|---|---|---|---|---|
| step `[5]`'s equivalence predicate: a type check that can only ever be true → the `fired` channel the registration says gates the rung, plus two refusal limbs | **no** — `G-T6a` and its `Σ CAP ≤ 20,000` are untouched | **no** — `E1_T_K` 1.000e-03 K, `E2_PRGH_PA` 1.0 Pa, `U_DISQ` 1.0e-03 m/s, `PLANT` 1.234e-03 K, `PLANT_TOL_K` 1e-9 all byte-identical | **no** — the price table, `CAP_MARGIN_M = 4.0` (`grade_t25R6a.py:79`) and `F_C5_L2 = 516.15 / 38.07 = 13.5579` (`:86`) are untouched | **no** |

**Explicitly NOT requested:** no widening of the 20,000 ceiling; no change to any
disqualifying threshold in §6.4; no change to `PLANT` or the rule-3 control; no
re-run of any arm; no Roache/rule-5 ordering change.
`compare_arms_t25R5.py` is **frozen and is not edited** — the sha1 of its blob on
disk was recomputed by this lane at the moment of writing and is
`736bd0d9e03c898c1ca991cfc1b8fec8e0058b39`, byte-identical to the registered
`COMPARATOR_BLOB` at `grade_t25R6a.py:72`, so `check_comparator_freeze()` passes
on today's disk. The only file the diff touches is
`grade_t25R6a.py`, and it touches one predicate inside it.

---

## 9. IF VERIFICATION DECLINES

**Heat-transfer will record the honest disposition rather than leave the rung
quietly open.**

- T25R6a stands as published: **`NOT A RESULT`**, ground *"the equivalence control
  FIRED (prereg 6.4)"*, with `T25R6a_C5_REGRADE_RECORD.md` beside it recording
  that the ground is contradicted by the same file's own `'fired': []` and that
  the predicate was unsatisfiable.
- **`G-T6a` is recorded as never evaluated**, and the C5 arm is recorded as
  carrying **no graded `Σ CAP`**.
- The `Σ CAP(C5) = 20,006.80` figure on Sanaa's desk then rests on the regrade
  record alone rather than on a grader-written verdict, and heat-transfer will
  say so on the board in exactly those words.
- **No compute will be spent to route around the refusal.** Re-running the four
  arms would not change the predicate and would be waste under rule 12.

---

## 10. THE EXACT LIST, FOR RULING ONE BY ONE

1. **Under §2d.1, may heat-transfer apply to `grade_t25R6a.py` the §7 predicate
   repair** — replacing `if r is not True and r != 0:` (`:437`), a condition
   tautologically true for the only type `compare()` can return, with a read of
   the `fired` channel the registration says gates the rung, guarded by two
   `refuse()` limbs (non-dict return; missing `fired` key) — **no gate, no
   threshold, no cap, no label changed, `compare_arms_t25R5.py` untouched** —
   given that `Σ CAP(C5)` was never computed and that the repair moves the
   verdict **to `GATE FAIL`, away from a `PASS`**?

2. **Does verification attach conditions**, as it did at `ad9eda53` where five
   were attached to the spine grant including one added against the petitioner?
   Heat-transfer asks for them explicitly rather than inferring them.

3. **Does verification wish to record anything about the artifact in §3.4** — a
   published verdict JSON whose `ground` field asserts a control fired while the
   same file carries `'fired': []` at both levels? **No repair is requested for
   this item**; the file stands unaltered under rule 6.

---

## 11. WHAT HEAT-TRANSFER HAS NOT DONE, PENDING THIS RULING

`grade_t25R6a.py` is **not edited**. `compare_arms_t25R5.py` is **not edited**.
`T25R6a_VERDICT.json` is **not edited**. **No repaired grader has been run and no
post-repair verdict exists anywhere on disk.** `Σ CAP(C5) = 20,006.80` exists
only in `T25R6a_C5_REGRADE_RECORD.md`, which states on its own face that it is a
record and not a graded artifact. No compute has been spent on this rung since
the four arms completed, and none will be spent before a ruling.
