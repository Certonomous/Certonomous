# EVIDENCE FOR THE SUPERVISOR'S RULING — NOT A RULING, NOT AN AMENDMENT, AUTHORISES NOTHING

**D8G — the `§2d.1` question on `d8g_LEDGER_REFUSED_ROW_DEFECT.diff`.**
Assembled 2026-09-12 by a dafoam `lab-lane` at the dafoam-supervisor's direction.

**THIS FILE DECIDES NOTHING.** It does not grant a repair, does not amend
`PREREGISTRATION.md`, does not license compute, and does not change any instrument. No
diff was applied. `d8g_grade.py` is `12688063e20cbb6fa79cf08d0996d4e1` and
`d8g_run_arm.sh` is `7ce53b9242ac6e850cc330712d93d5b0` at the moment this was written —
the same values they carried before — and
`/home/ubuntu/certonomous-runs/CURRICULUM-D8G-a6-grid-triple/ledger.txt` is
`fc6fb5d41344dc2eb20debe99dd3d824`, unedited.

**ZERO SOLVER CORE-MINUTES WERE SPENT.** Nothing was launched. Every measurement below is
read-only against artifacts already on disk.

**⚠ ONE THING THE SUPERVISOR SHOULD KNOW BEFORE READING ANY OF IT.** The object of this
ruling — `d8g_LEDGER_REFUSED_ROW_DEFECT.diff`, 283 lines — is **UNTRACKED**
(`git status`: `?? cases/dafoam/ladder-a/A6/curriculum_D8G/d8g_LEDGER_REFUSED_ROW_DEFECT.diff`).
Sections 5, 6 and 8 cite it by line number. **`VERIFICATION_CHARTER.md` §2u holds that a
witness in an uncommitted file is not a witness**, and a ruling that rests on line numbers
in a file that is not in any commit rests on something that can change without trace. **This
lane did not commit it — it is the drafting lane's item and committing another agent's work
in the same breath as one's own is how foreign rows get landed unread.** Recorded here so
somebody can be dispatched to land it before, not after, the ruling is written.

**SUBMISSIONS PARKED.**

---

## 0. HOW THE MEASUREMENTS WERE TAKEN, SO THEY CAN BE RE-TAKEN

Every table in sections 4-9 and 11 is produced by
`cases/dafoam/ladder-a/A6/curriculum_D8G/d8g_ledger_repair_probe.py`, committed beside
this file. **It grades nothing, applies nothing, and writes nothing outside a tempdir it
removes itself.** It copies the frozen `d8g_grade.py` bytes, patches the COPIES in memory
into five reader variants, builds eight ledger variants from the real `ledger.txt`, and
prints what `read_ledger()` and `g_completion()` do on each pair. Re-run:

```
python3 cases/dafoam/ladder-a/A6/curriculum_D8G/d8g_ledger_repair_probe.py
```

The probe refuses to run if `read_ledger()`'s head or tail has moved, rather than patching
something it does not recognise.

**Its own rule-3 control is described in section 9 and it already caught one repair
shape.** No number in this document is a reading of code alone.

---

## 1. `VERIFICATION_CHARTER.md` §2d.1's FOUR CONDITIONS, VERBATIM, WITH LINE NUMBERS

The section is numbered **exactly as the brief said** — `## 2d.1` at
`docs/charters/VERIFICATION_CHARTER.md:1914`, headed *"Amendment to 2d: the repair
exception, forced by the first case the rule was run against (added 2026-08-19)"*, with
`:1916` asserting **"Lines whose number changed above this section: 0."**

The four conditions are the block quote at **`:1936-1942`**, reproduced here byte-for-byte
with its line numbering:

```
1936  > **A change on the grading path made after the first graded solve is permitted
1937  > when, and only when, all four hold: (1) it repairs a DEMONSTRABLE ERROR rather
1938  > than a preference; (2) the error was established by an instrument INDEPENDENT
1939  > OF THE HYPOTHESIS -- one that grades nothing, such as a near-identity, a guard
1940  > or a control; (3) the record discloses it, names that instrument, and
1941  > QUANTIFIES WHAT MOVED; and (4) the pre-repair values are recorded beside the
1942  > published ones. Failing any of the four, 2d stands.**
```

Three further lines of §2d.1 bear directly on this ruling and are quoted rather than
summarised:

- **`:1944`** — *"**Condition (2) is the load-bearing one and the other three are
  hygiene.**"*
- **`:1954-1955`** — *"**Nothing a verdict depends on may be repaired on the authority of
  the verdict it produces.**"*
- **`:1952-1953`**, on what the exception still does not permit: *"the numbers looked
  wrong, so the band was widened. A band is not an instrument; it is the hypothesis's own
  scoring rule."*

### 1a. THREE LATER RULINGS NARROW THESE CONDITIONS AND ALL THREE APPLY HERE

A lane that quoted only `:1936-1942` would hand the supervisor a stale test.

| clause | line | what it does to §2d.1 |
|---|---|---|
| **§2d.5** | `:4498` | *"THE FROZEN PRE-REGISTRATION IS AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS FOR CONDITION (2), WHEN AND ONLY WHEN THE DEFECT IS A DEMONSTRABLE DEPARTURE FROM ITS TEXT … The departure must be exhibited by quotation and by measurement, both."* And at `:4540`, the refusal limb: **"Under `§2d.5` silence is not a departure, so condition (2) has no object."** |
| **§2d.3.3** | `:4389-4395` | conditions (3) and (4) may be discharged by **disclosing a measured absence** — *"AVAILABLE ONLY WHILE THAT COUNT IS ZERO… This clause creates no path for repairing a rung that has produced numbers."* |
| **§2d.4** | `:4432` | *"the absence-disclosure shortcut keys on the absence of NUMBERS, never on the absence of a VERDICT. **A rung whose solves have COMPLETED has numbers, whether or not a comparator has consented to grade them. For such a rung, conditions (3) and (4) BITE IN FULL.**"* |

---

## 2. THE TWO CITED LINE NUMBERS — VERIFIED BY THIS LANE, NOT TAKEN FROM THE BRIEF

**BOTH CORRECT.**

- **`d8g_run_arm.sh:922`** is the `echo` inside the LA.4 block (`if [ "$LA_RC" -ne 0 ]`,
  opened at `:916`) that writes `ARM=$ARM ROW=$ROW IMG=$IMG DIGEST=$GOT_DIGEST launched:
  false reason=[…] launch_rc=$LA_RC …`, `tee -a`'d to `$BASE/ledger.txt` at `:925`. It
  carries **no `rc=`, no `wall_s=`, no `ranks=`, no `core_min=`** — confirmed against both
  the source line and the row it actually produced, `ledger.txt` line 3. The block then
  `exit "$LA_RC"` at `:927`.
- **`d8g_grade.py:366`** is `LEDGER_RE`; its fourth group at **`:368`** is
  `rc=(?P<rc>-?\d+)`. **`:393-394`** claim every `ARM=`-prefixed line
  (`if not line.startswith("ARM="): continue`) and **`:395-398`** require the match and
  `refuse` on failure with `"PRESENT-BUT-GARBAGE row: refused, never skipped"`.
- **`d8g_grade.py:416`** is the `duplicate_arm_row` refusal, guarded at `:415`.

**The brief's characterisation of the reader is confirmed: it is behaving correctly.**

### 2a. A THIRD FACT ABOUT `:922` THE DIFF DOES NOT STATE, AND IT MATTERS FOR REPAIR A

The LA.4 block exits at **`:927`**. The surviving kernel record
`<ARM>_<STAMP>.inspect.txt` — the fallback `d8g_grade.py:421` reads when an arm has no
ledger row — is written at **`d8g_run_arm.sh:1002`, seventy-five lines later.** **A refused
launch therefore writes NO inspect record.** Confirmed on disk: the run root holds
`L1-P_20260911T234236Z_2435242.inspect.txt` (the launch that succeeded) and **no inspect
file for the 20260911T233045Z attempt that was refused.** This is what makes repair A's
silence terminate in a refusal rather than in a synthesised row — see the repair-A hazard note in section 5.

---

## 3. THE THRESHOLD QUESTION — DOES §2d.1 APPLY AT ALL?

**The supervisor's reading is that a ledger refusal is not a grade, so there has been no
first graded solve and §2d.1 does not apply. THE EVIDENCE DOES NOT SUPPORT THAT READING,
and I state that plainly because it is the answer the supervisor asked me to contradict if
I found it wrong.**

**§2d's trigger is not "first graded solve COMPLETED". It is `:1841-1842`:**

```
1841  > … is fixed at the pre-registration commit and does not change once
1842  > the first graded solve has started.
```

**"has started."** And §2d's own enforceable test, `:1880-1884`, is *"Compare the
comparator's commit timestamp against the **earliest completion marker in its own run
tree**."* Both of those key on the SOLVE, not on the comparator's consent.

On disk, in the run root:

| fact | artifact |
|---|---|
| a graded solve started, twice | `ledger.txt:3` (`stamp=20260911T233045Z`), `ledger.txt:7` (`stamp=20260911T234236Z`) |
| a completion marker exists | `L1-P_20260911T234236Z_2435242.log.ok.20260911T234236Z_2435242` |
| the solver ran to its registered `endTime` | 101 `ExecutionTime` samples, last `Time = 1000` (`L1-P_20260911T234236Z_2435242.log`) |
| numbers were produced AND published | `D8G_L1P_RESULTS.md:34` — `CD 0.0442012 / CL 0.3582862`; `:25-30` — six `initRes` values |
| 16.067 core-min gross was spent | `ledger.txt:7` |

**§2d.4 at `:4432` disposes of the shortcut directly: *"A rung whose solves have COMPLETED
has numbers, whether or not a comparator has consented to grade them."*** D8G has numbers.

**And §2d.4.1 at `:4436` anticipates this exact argument and rejects it by name:**

> *"A comparator that refuses to run is then a qualification for the shortcut — **the
> instrument's own failure becoming the ground for relaxing the rule that governs repairing
> it.** That is circular, and it is the shape §2d.1's closing sentence forbids."*

### 3a. IS D8G LIKE A3GC (S-156)? — NO, AND THE DISANALOGY THE SUPERVISOR NAMED IS THE
### DECIDING ONE

S-156's ground, quoted from `docs/LAB_STATE.md:7028`: *"Legal because rule 2 closes gates
AFTER FIRST COMPUTE and **NO A3GC LEVEL HAS SOLVED** (proved by the lane's planted
control)"*, and *"I checked `VERIFICATION_CHARTER` §2d.1's four-condition repair exception
and it DOES NOT APPLY — it governs changes after the FIRST GRADED SOLVE and there has been
none."*

**That ground was a MEASURED ZERO, proved by a planted control. D8G's is not zero.** A3GC
had no solve and no numbers; D8G has one arm that ran 1,000 iterations, produced CD, CL and
six residuals, published them, and spent 16.067 core-min doing it. **The supervisor's own
disanalogy is correct and it is dispositive:** S-156 and D8G differ on the single fact
S-156 rested on. Ruling that §2d.1 does not apply to D8G would not be consistent with
S-156 — it would be S-156 applied to a case with the opposite fact.

> **EVIDENCE SAYS: §2d.1 APPLIES. The threshold question does not dispose of the analysis.**
> The ruling remains the supervisor's.

---

## 4. WHAT EACH REPAIR ACTUALLY DOES — MEASURED

`read_ledger()` outcome per (reader, ledger). `A_applied` is the real ledger with line 3's
prefix changed to `REFUSED_ARM=`, i.e. **the ledger that WOULD have been written had repair
A been in force at 23:30Z.** `PLANT` is the rule-3 control of section 8.

| reader | real | A_applied | PLANT | refused_only | A_applied+refused_only |
|---|---|---|---|---|---|
| **frozen (baseline)** | REFUSE `row_unparseable` | **PARSED** `['L1-P']` rc=1 | REFUSE `row_unparseable` | REFUSE `row_unparseable` | PARSED `[]` |
| **repair B** | **PARSED** `['L1-P','__refused_launches__']` rc=1 | PARSED `['L1-P']` rc=1 | REFUSE `row_unparseable` | REFUSE `refused_launch_and_no_completed_row` | PARSED `[]` |
| naive SKIP *(nobody drafted this)* | PARSED `['L1-P']` | PARSED `['L1-P']` | **PARSED `[]` — CONTROL FAILED** | PARSED `[]` | PARSED `[]` |
| ADMIT-the-row *(nobody drafted this)* | **REFUSE `duplicate_arm_row`** | PARSED `['L1-P']` | REFUSE `row_unparseable` | PARSED `['L1-P']` rc=88 | PARSED `[]` |

### 4a. THE MEASUREMENT THAT MATTERS MOST — WHAT HAPPENS **AFTER** THE LEDGER STOPS BEING THE BLOCKER

`g_completion()` driven on the real run root with each set of parsed rows:

| reader | ledger | next stop |
|---|---|---|
| frozen | A_applied | **REFUSE `G1` — `{"arm":"L1-P","kernel_rc":1,"oomkilled":"false"}`** |
| repair B | real | **REFUSE `G1` — `{"arm":"L1-P","kernel_rc":1,"oomkilled":"false"}`** |
| repair B | A_applied | **REFUSE `G1` — `{"arm":"L1-P","kernel_rc":1,"oomkilled":"false"}`** |

**THE LEDGER IS NOT THE LAST BLOCKER AND IT IS NOT THE BINDING ONE.** `d8g_grade.py:483-485`
refuses any arm whose kernel exit is non-zero — *"a run that fails any clause is not done
(rule 4)"*. **L1-P exited 1.** The solver said so itself
(`L1-P_20260911T234236Z_2435242.log`: `Primal solution failed!`, mpirun exit 1), the kernel
recorded it (`L1-P_20260911T234236Z_2435242.inspect.txt` begins `1 false`), and the ledger
row carries `rc=1 … inspect(exit,oomkilled)=[1 false]`.

**Consequence for the ruling: NEITHER REPAIR CAN MANUFACTURE A FAVOURABLE VERDICT ON THIS
DATA, because on this data the grader refuses two gates later on a ground no ledger repair
touches.** That is a fact about *this* ledger, not a property of repair B, and section 6
says where B's direction hazard genuinely bites.

**⚠ AND IT CONTRADICTS A PUBLISHED CLAIM.** `D8G_L1P_RESULTS.md:6-8` is headed *"The run —
completion held on every limb"* and then states `rc = 1`. **Rule 4's first clause is
`rc = 0`.** The grader measurably refuses on exactly that limb. The rung verdict
`NOT A RESULT` is unaffected — it rests on convergence, not on completion — but the
sentence "completion held on every limb" is not true as written, and a supervisor reading
that record to decide whether L1-P is gradeable would be misled by it.

---

## 5. THE FOUR CONDITIONS, REPAIR BY REPAIR

### REPAIR A — producer side, `d8g_run_arm.sh:922`, `ARM=` → `REFUSED_ARM=`

| condition | verdict | what decides it |
|---|---|---|
| **(1) demonstrable error, not a preference** | **MET** | Two frozen instruments disagree about the shape of a record one writes on purpose, and the disagreement is *exhibited*, not argued: `d8g_run_arm.sh:922` emits an `ARM=`-prefixed line with no `rc=`; `d8g_grade.py:393` claims it and `:368` requires `rc=`; the refusal fired on real data, twice, and is on disk in `D8G_grade_20260911T233603Z.json` and `D8G_grade_20260911T234701Z.json`. Nobody's judgement is load-bearing. |
| **(2) independent instrument that grades nothing** | **CANNOT BE DETERMINED — and on the §2d.5 route it reads NOT MET** | See 5a. This is the condition the ruling turns on and I have not been able to resolve it in the repair's favour. |
| **(3) discloses, names the instrument, quantifies what moved** | **DISCHARGEABLE AT ZERO, not yet discharged** | Under §2d.4 (`:4432`) conditions (3) and (4) bite in full here, and the charter names the discharge: *"running the comparator over the same data before and after the repair and publishing both."* Section 4's two tables are exactly that, at zero solver compute. **A moves nothing on the existing ledger** (section 7) and that is itself the quantity to publish. |
| **(4) pre-repair values beside the published ones** | **DISCHARGEABLE AT ZERO, not yet discharged** | Pre-repair graded values: **none exist** — both grade artifacts are refusals, named above, and the count of graded solves under this registration is **zero**, measured not asserted (§2d.3.3's standard). Published *numbers* do exist (`D8G_L1P_RESULTS.md:34`) and are **unmoved by A**, which is the statement §2d.4 requires. |

**HAZARD OF REPAIR A — the diff says "none identified" and that is an overstatement.**
Measured (section 4, `A_applied+refused_only`): under A, **an arm whose only record is a
refused launch becomes INVISIBLE to `read_ledger()` — `PARSED keys=[]`.** The frozen reader
today refuses that same ledger by name, quoting the row. A converts a **named refusal** into
**silence at the ledger**, and detection moves downstream to
`inspect_file_fallback` (`d8g_grade.py:421-428`), which refuses with
`arm_absent_from_ledger` — a **less informative refusal that does not name the launch
failure**. Because a refused launch writes no inspect record (section 2a), the refusal does
still happen, so **A is not unsafe — it is less legible.** The narrow residual hazard: an
arm with a refused launch *and* a later attempt that wrote an inspect record but no ledger
row would present exactly one candidate to the fallback and be admitted as a synthesised
row. That path is **not demonstrated on this item** and I state it as identified, not
measured.

### REPAIR B — reader side, `d8g_grade.py`, `REFUSED_LAUNCH_RE` + `continue` + tail refusal

| condition | verdict | what decides it |
|---|---|---|
| **(1) demonstrable error, not a preference** | **MET on the same evidence as A** | Identical defect, opposite end. |
| **(2) independent instrument that grades nothing** | **CANNOT BE DETERMINED — and on the §2d.5 route it reads NOT MET, more sharply than for A** | See 5a; B is a change to the comparator itself, which is the object §2d was written to protect. |
| **(3) discloses, names the instrument, quantifies what moved** | **DISCHARGEABLE AT ZERO, not yet discharged — AND THE DIFF'S OWN MITIGATION FOR IT IS FALSE** | Section 4 is the before/after §2d.4 requires. But the diff claims *"every refusal carried into the output"*, and the audit in section 6 shows **`__refused_launches__` is read by nothing and never reaches the output JSON.** |
| **(4) pre-repair values beside the published ones** | **DISCHARGEABLE AT ZERO, not yet discharged** | Same as A: graded values zero and measured; published numbers unmoved (B's next stop is `G1 kernel_rc=1`, section 4a — **no number changes**). |

**HAZARD OF REPAIR B — the diff states it honestly and section 6 completes the audit it
said it had not done.**

### 5a. CONDITION (2), WHICH IS THE WHOLE RULING, AND WHY I CANNOT CLOSE IT FOR EITHER REPAIR

§2d.1 `:1938-1939` requires *"an instrument INDEPENDENT OF THE HYPOTHESIS — one that grades
nothing, such as a near-identity, a guard or a control."* §2d.5 `:4498` adds the only other
route: **the frozen pre-registration**, and only where the defect is *"a demonstrable
departure from its text … exhibited by quotation and by measurement, both."*

**I searched `PREREGISTRATION.md` (108,060 bytes) for a registered ledger-row contract.
There is none.** The four occurrences of "ledger" are `:468` (a D8R cost citation), `:879`,
`:1482` and `:1563` (three statements that an abort happened *before* any ledger row). **The
registration nowhere states the `ARM=` prefix contract, nowhere states what a refused launch
writes, and nowhere states that `read_ledger` skips non-`ARM=` lines.**

> **Under §2d.5 as ruled at `:4540` — "silence is not a departure, so condition (2) has no
> object" — the pre-registration route is CLOSED for both repairs.** That is the R6
> precedent, where a good, strictly-stricter change was **refused as a §2d.1 repair on the
> instrument** and **referred prospectively** to the next registration.

The other candidate instruments, each checked:

| candidate | grades nothing? | did it establish the error? |
|---|---|---|
| `d8g_grade_selftest.sh` / the 50-unit suite | **yes** — a mutation harness, exactly §2d.1's shape | **NO.** Enumerated all 50 units: **not one plants a malformed `ARM=` row and not one plants a duplicate `ARM` key.** U35/U36 cover a row *absent*, never a row *garbage*. The suite passed 50/50 while the defect stood. **It did not find this and could not have.** |
| `d8g_launch_assert_selftest.sh` | yes | **NO.** It exercises the launch-witness return three ways; it never writes or reads `ledger.txt`. |
| `d8g_of_selftest.sh`, `d8g_runScript_selftest.sh` | yes | **NO.** They load `d8g_grade.py` as a *specification* for artefact shape; neither touches the ledger. |
| **the grader's own refusal** (`D8G_grade_*.json`) | **contested** | It is the **hypothesis's scoring instrument**, which §2d.1 excludes in terms. **The counter-argument, stated because it is real and the supervisor must weigh it, not because I endorse it:** in this act the grader produced **no value and no verdict on the physics** — it refused — so it *could not have been selected to move a verdict in a wanted direction*, which `:1944-1946` gives as the *reason* for condition (2). **The counter-counter-argument is §2d.4.1 `:4436`: treating a comparator's own failure as the qualifying instrument is the circularity that ruling names and forbids.** |
| **this lane's probe** (`d8g_ledger_repair_probe.py`) | **yes** — it grades nothing and returns no verdict | **NO — and this is the honest disqualifier.** It was written **today, after** the defect was found by code-reading, **to characterise** it. §2d.1's condition (2) asks what **established** the error, not what measured it afterwards. **An instrument built to confirm a defect already believed in is not independent of the hypothesis that there is one.** |

**How the defect was actually found: by a lane reading `d8g_run_arm.sh:922` against
`d8g_grade.py:366` — code-reading, disclosed as such at the head of the diff.** Under
§2d.5's opening the T23G2 ruling met that same problem — *"Five of the six items were found
by reading the frozen registration against the code … The petition names no instrument, and
none exists. Read literally, five of six fail condition (2)"* (`:4492`) — and the answer
there was §2d.5, **which requires a registration text to depart from. D8G has none.**

> **EVIDENCE SAYS: condition (2) is the binding one for both repairs, and on the routes the
> charter actually provides it is NOT MET for either. It is recorded as CANNOT BE DETERMINED
> rather than NOT MET only because the grader-refusal argument is genuinely arguable and is
> the supervisor's to weigh, not mine.** If the supervisor reads it as I do, then §2d stands
> on both repairs and the R6 remedy — **register the ledger-row contract prospectively, in
> the next item's pre-registration, where it costs nothing and needs no exception** — is the
> route the charter already blesses.

---

## 6. THE DOWNSTREAM-CONSUMER AUDIT THE DRAFTING LANE SAID IT HAD NOT DONE

The diff at `:193-195`: *"A `__refused_launches__` key injected into `rows` is also visible
to every downstream consumer of `read_ledger()`'s return value and MUST be audited against
each of them before this is applied — THIS LANE HAS NOT DONE THAT AUDIT and says so."*

**DONE. Here is every consumer, in-process and out.**

`read_ledger()` is called at exactly one site, `d8g_grade.py:1466`. Every use of the name
`rows` in the file was enumerated (`grep -n '\brows\b'`, 40 hits, of which the ledger dict
accounts for the following):

| consumer | line | how it reaches `rows` | what a `__refused_launches__` key does to it |
|---|---|---|---|
| `g_completion(root, rows)` | `:1467`, body `:466-470` | `for arm in ARMS_REQUIRED: rows.get(arm)` | **nothing** — key lookup only |
| artefact loop | `:1492`, `:1500`, `:1503` | `rows[arm][...]` for `arm in ARMS_REQUIRED` | **nothing** |
| residual plant control | `:1520` | `rows[parm]["log_text"]` | **nothing** |
| `g_primal` / `last_primal_segment` feeds | `:1528`, `:1531` | `rows["<L>-<rk>"]["log_text"]` | **nothing** |
| `g_toolchain(rows)` | `:1581`, body `:1363-1364` | `for arm in ARMS_REQUIRED: rows[arm]` | **nothing** |
| `g_caps(rows)` | `:1581`, body `:1387-1388` | `for arm in ARMS_REQUIRED: rows[arm]` | **nothing** |
| `g_placement(rows)` | `:1581`, body `:1417-1418` | `for arm in ARMS_REQUIRED: rows[arm]` | **nothing** |

**There is NO `rows.items()`, NO `rows.values()`, NO `rows.keys()`, NO `len(rows)` and NO
iteration over `rows` anywhere in the file.** The only membership test is
`row["ARM"] in rows` at `:415`, during construction. And `grade()`'s return dict
(`:1611-1640`) **does not contain `rows`** — it returns gates built from it.

> **AUDIT RESULT, BOTH HALVES:**
> **(a) ZERO CRASH RISK.** No consumer can trip over a key whose value is a list. B is safe
> in the narrow mechanical sense the drafting lane was worried about.
> **(b) AND THE MITIGATION IT WAS OFFERED FOR DOES NOT EXIST.** `__refused_launches__` is
> **read by nothing and appears in no output.** The diff's *"every refusal carried into the
> output"* is **false as drafted.** A refused launch on an arm that later completes would be
> **silently dropped from the record** — which is the opposite of what the repair claims and
> is squarely what `d8g_run_arm.sh:923`'s own line (*"no grading may read it"*) was written
> to prevent. **If B is granted, it must additionally wire the disclosure into `grade()`'s
> return, or it delivers a suppression where it promised a disclosure.**

**Consumers of the grader's OUTPUT, outside the process:** `d8g_chain_driver.sh:365-366` is
the only one. It invokes the grader, records `grader_rc` in `STATUS.chain` and explicitly
annotates `note=comparator-exit-status-NOT-the-verdict`. **It does not parse the JSON.**
`d8g_grade_selftest.sh:35` and `d8g_of_selftest.sh:49` consume the *module*, never a run's
output. **No website, docket, ledger or campaign record anywhere in the repository reads
`D8G_grade_*.json`.** So repair B's admitted row reaches **no consumer that could act on
it** — which limits the blast radius and equally limits the value of the disclosure.

---

## 7. THE QUESTION THE SUPERVISOR SAID DECIDES BETWEEN A AND B

> *Does repair A leave the existing `ledger.txt` permanently ungradeable? Does any path
> grade L1-P without editing evidence or changing the reader?*

**A: YES on the first, and the second has a worse answer than the question assumes.**

**7.1 — A is producer-side and cannot rewrite a row already on disk. CONFIRMED.**
`d8g_run_arm.sh:925` is `tee -a` — append. `ledger.txt` line 3 was written at 23:30:45Z and
stays exactly as it is. Measured (section 4): the **frozen reader on the real ledger refuses
`row_unparseable`**, with or without A applied to the script. **A alone leaves the existing
`ledger.txt` refusing forever.** The diff says this at `:130-132` and it is correct.

**7.2 — BUT THE DEEPER ANSWER IS THAT NO REPAIR GRADES L1-P, AND THIS IS THE FINDING I MOST
WANT THE SUPERVISOR TO HAVE BEFORE RULING.**

`d8g_grade.py` is an **ITEM-level instrument. It cannot grade an arm.** `ARMS_REQUIRED`
(`:212`) is **ten arms** — `L1-P L2-P L3-P A2-P F2-P L1-S L2-S L3-S A2-S F2-S` — and
`g_completion` loops over all ten. There is **no `--arm` flag** (`main()`, `:2157-2182`:
`--root`, `--selftest`, `--tmpdir`, `--out`, and nothing else). An arm absent from the
ledger goes to `inspect_file_fallback`, measured on the real root:

| arm | fallback result |
|---|---|
| `L2-P` | REFUSE `G1 arm_absent_from_ledger`, `inspect_record_candidates: []` |
| `L1-S` | REFUSE `G1 arm_absent_from_ledger`, `inspect_record_candidates: []` |
| `F2-S` | REFUSE `G1 arm_absent_from_ledger`, `inspect_record_candidates: []` |

**So there is no repair — A, B, or any other — after which this instrument returns a graded
number for L1-P alone. It never could. The item needs all ten arms.** The premise that a
parse fix buys an instrument-backed L1-P verdict is **false for reasons that have nothing to
do with the ledger.**

**7.3 — AND EVEN WITH ALL TEN ARMS, THIS L1-P IS UNGRADEABLE.** `rc = 1`. `d8g_grade.py:483`
refuses. Measured three ways in section 4a. **L1-P's `NOT A RESULT` can only ever be a human
reading of a log — not because the reader is broken, but because the run failed, and a
failed run is what rule 4 says it is.** That is not a defect to repair; it is the correct
answer arriving through a refusal instead of through a verdict.

> **EVIDENCE SAYS: "A alone means L1-P can never be graded by an instrument" is TRUE — and
> it is equally true of B, and of every other repair, for three independent reasons: the
> append-only ledger, the ten-arm requirement, and `rc=1`. The choice between A and B cannot
> be made on the ground of rescuing L1-P, because neither rescues it.**

---

## 8. THE `duplicate_arm_row` BLOCKER — MEASURED, NOT REASONED

The diff at `:46-50`: *"SECOND, INDEPENDENT BLOCKER — IT SURVIVES ANY FIX TO THE FIRST …
Teach the parser to read the first and it refuses on the second."*

**MEASURED: THE FIRST CLAUSE IS WRONG AND THE SECOND IS RIGHT. They are not the same
claim.**

| repair shape | `duplicate_arm_row` fires on the real ledger? |
|---|---|
| **repair B** (skips the refused row) | **NO** — parses, `keys=['L1-P','__refused_launches__']` |
| **naive SKIP** (skips any `ARM=` line without `rc=`) | **NO** — parses, `keys=['L1-P']` |
| **a ledger written under repair A**, read by the frozen reader | **NO** — parses, `keys=['L1-P']` |
| **ADMIT** (reads the refused row *as an arm row*) | **YES** — REFUSE `duplicate_arm_row` |

The duplicate refusal at `:416` keys on `row["ARM"] in rows`. **A repair that never puts the
refused row into `rows` never creates the collision.** Both drafted repairs skip; **neither
creates it.** The blocker is real **only for a repair of the ADMIT shape, and nobody drafted
one.**

> **EVIDENCE SAYS: the duplicate blocker is NOT independent of the parse fix. It is
> CONDITIONAL ON THE FIX'S SHAPE, and dissolves under both A and B. The diff's "it survives
> any fix to the first" is measurably false; its "teach the parser to read the first and it
> refuses on the second" is true and describes a repair that does not exist.**

**This removes one of the two grounds on which the item was said to be doubly blocked.** It
does not remove `rc=1` (section 4a), which no repair touches.

### 8a. ⚠ THERE IS ONE THING THE DUPLICATE BLOCKER *IS* INDEPENDENT OF, AND IT IS NOT A REPAIR

**A RE-RUN.** `ledger.txt:7` — `rc=1 … core_min=16.067` — is a **legitimate completed-arm
record**, exactly what `:416` was written to protect. Re-run L1-P into the same run root and
the launcher appends a **second** `ARM=L1-P` completed row at `d8g_run_arm.sh:1010`, and the
collision is real rather than an artefact of any parse choice. Measured (probe scenarios
`rerun_same_ledger` and `A_from_start+rerun`):

| scenario | frozen reader | repair B | naive SKIP | ADMIT |
|---|---|---|---|---|
| A lands today + clean re-run, same ledger | REFUSE `row_unparseable` | **REFUSE `duplicate_arm_row`** | REFUSE `duplicate_arm_row` | REFUSE `duplicate_arm_row` |
| **best case:** A in force from the start + clean re-run | **REFUSE `duplicate_arm_row`** | REFUSE `duplicate_arm_row` | REFUSE `duplicate_arm_row` | REFUSE `duplicate_arm_row` |

**Every reader variant refuses, including the frozen one on the best-case ledger.** Section
12.3 is where this lands.

---

## 9. THE PLANTED-ZERO QUESTION

> *If the repair were applied and the reader still could not see a real row, would anything
> refuse?*

**IN THE FROZEN INSTRUMENT AS IT STANDS: NO SUCH CONTROL EXISTS. I state that first because
it is the answer to the question as asked.**

All 50 selftest units were enumerated. **Not one plants a malformed `ARM=` row; not one
plants a duplicate `ARM` key.** `d8g_grade.py:397` (`row_unparseable`) and `:416`
(`duplicate_arm_row`) are the **only two refusal branches in the ledger reader, and neither
has a unit driving it.** U35 and U36 drive a row *absent*, which is a different branch
(`inspect_file_fallback`). **The 50-unit suite would pass identically with both branches
deleted.** By CLAUDE.md rule 3's own standard, a silence from this reader has never been
licensed by a control.

**One of the two branches has nonetheless been seen alive — on real data, not in a
fixture.** `row_unparseable` fired twice on 2026-09-11, naming the exact row, in
`D8G_grade_20260911T233603Z.json` and `D8G_grade_20260911T234701Z.json`. That is a live
non-zero. **`duplicate_arm_row` has never fired anywhere and remains unwitnessed.**

**THE CONTROL THIS LANE BUILT, ON THE STRONGER REPAIR (B), AND IT ALREADY EARNED ITS KEEP.**
`d8g_ledger_repair_probe.py` drives every reader variant against a ledger whose
**well-formed** row has been corrupted by one token (`rc=` → `rcX=`) — a row the reader
*must* refuse:

| reader | on the one-token-corrupted ledger |
|---|---|
| frozen | **REFUSE** `row_unparseable` — alive |
| **repair B** | **REFUSE** `row_unparseable` — **alive: B's added `continue` does not blind the generic refusal** |
| ADMIT | **REFUSE** `row_unparseable` — alive |
| **naive SKIP** | **PARSED `keys=[]` — CONTROL FAILED. SILENT ON A CORRUPTED ROW.** |

> **EVIDENCE SAYS: repair B survives a planted control that the obvious alternative fails.**
> The naive "skip any `ARM=` line without `rc=`" repair — the shape a hurried fix would
> reach for — **silently swallows a genuinely corrupted row and returns an empty ledger**,
> which is precisely the zero-from-a-blind-reader rule 3 forbids. **That is the strongest
> thing measured in B's favour in this whole document**, and it is a statement about B
> versus a bad alternative, **not** a discharge of condition (2).

**WHAT THE CONTROL DOES NOT SHOW, said plainly:** it exercises `read_ledger` in isolation.
It does not prove that a granted repair, wired into the full `grade()` path and run over ten
completed arms, refuses everything it should. **No such end-to-end control exists for either
repair, and the diff says so at `:214-215`: neither repair has been driven through
`d8g_grade_selftest.sh` or against a planted fixture.** If a repair is granted, **new
selftest units for both ledger refusal branches, with `EXPECTED_UNITS` raised from 50, are
the minimum that would make its silence readable** — and that is itself a change to the
frozen comparator requiring its own disposition.

---

## 10. WHAT THIS LANE COULD NOT VERIFY

- **Condition (2) is not resolved and I did not force it.** Section 5a lays out both sides;
  the grader-refusal-as-instrument argument is arguable in both directions and is the
  supervisor's to weigh.
- **Neither repair was executed against the full `grade()` path**, only against
  `read_ledger()` and `g_completion()`. Nothing downstream of `g_completion` has been driven
  under either repair, because the real data refuses at `G1` before reaching it.
- **The narrow repair-A hazard named in section 5** (an arm with a refused launch *and* exactly one
  surviving inspect record from a later attempt that wrote no ledger row) is an identified
  path, **not a measured one**. It does not occur on this item.
- **`ledger.txt` line 3's own truthfulness was not independently re-derived.** Whether the
  20260911T233045Z container genuinely never reached its first iteration is taken from the
  row and its `launch_pre.tsv`; this lane did not reconstruct it.
- **Repair C is REJECTED by the supervisor as destroying evidence and was not analysed
  further**, per the brief.

---

## 11. THE "NO CAP" NARROWING — TESTED AGAINST THE PRODUCER, AND MY READING DIFFERS FROM THE SUPERVISOR'S ON ALL THREE LIMBS

**PROVENANCE AND ITS LIMIT, stated first.** A supervisor relayed owner words to this lane
mid-task and asked that a reading built on them be tested. **Under CLAUDE.md rule 9 a
relayed message is not Sanaa's consent and this lane treats it as a claim to be measured,
not as authorisation.** Nothing below depends on the directive being in force: every
measurement is against the frozen producer and the row it actually wrote. **The cap-policy
question itself is the supervisor's and Sanaa's; this section answers only the factual
question put — whether removing a cap stops this defect recurring.**

### 11.1 — DOES THE DEFECT STOP RECURRING? **NO. THE READING IS REFUTED, AND BY THE POISONED ROW ITSELF.**

The premise put to me was that the poisoned row *"was written BY an rc=88 launch refusal —
and that rc=88 was a kill on a LAUNCH-WITNESS BUDGET DERIVED FROM THE CAP."*

**`d8g_run_arm.sh:916` is `if [ "$LA_RC" -ne 0 ]`, and `la_assert_launch` (`:670-736`) has
THREE distinct non-zero returns, only ONE of which is budget-derived:**

| rc | line | reason string | budget-derived? |
|---|---|---|---|
| **88** | `:719-720` | `never_started_container_exited` | **NO.** Fires from the `false` branch of the container-state `case` at `:708`, evaluated **before** the budget test. It is the detection that the container **exited**. |
| **89** | `:731-732` | `never_started_wedged: ${budget}s elapsed, container still Running` | **YES** — `:730`, `if [ "$el" -ge "$budget" ]`. This is the only one. |
| **90** | `:701-702`, `:724-725` | `witness_reader_unreadable` (docker logs / docker inspect) | **NO.** An infrastructure reader failure after `LAUNCH_READER_RETRIES` consecutive failures. No budget involvement. |

**All three reach `:922` and all three write an `ARM=`-prefixed row with no `rc=`.** Removing
the cap removes **89 only**. **88 and 90 survive, and the defect recurs on either.**

**AND THE ACTUAL ROW WAS NOT EVEN THE BUDGET PATH.** `ledger.txt:3` reads
`launch_rc=88 waited_s=248 budget_s=352`. **248 < 352 — the budget never expired.** The row
was written by the **88** path, and the cause is on disk in
`L1-P_20260911T233045Z_2423104.log`:

```
[0] --> FOAM FATAL ERROR: (openfoam-2506)
[0] cannot find file "/mnt/L1-P/processor0/constant/thermophysicalProperties"
FOAM exiting
```

**That is the ADDENDUM 5 defect — an unstaged model dict — killing the container at 248 s.
It has nothing whatever to do with a cap, a budget or a timeout.** With no cap in force, the
identical row would have been written at the identical second.

> **EVIDENCE SAYS: limb 1 of the reading is REFUTED. The directive does not stop the defect
> recurring, because the defect's trigger was a dead solver, not a spend limit. The
> supervisor asked to be told plainly if other paths existed — there are two, and the row
> under discussion was written by one of them.**

*(The supervisor's taxonomy — spend-cap kill vs launch-liveness witness vs hang guard — is
sound as a taxonomy and this lane has no quarrel with it. The measurement simply says the
row at issue is in none of the three: it is a **dead-container detection**, which is the
witness doing its job correctly on a container that had already died.)*

### 11.2 — IS THE BLAST RADIUS NOW EXACTLY ONE EXISTING ROW? **HALF CONFIRMED, AND THE HALF THAT FAILS IS THE ONE THAT MATTERS.**

**CONFIRMED:** `ledger.txt:3` is still there, `d8g_grade.py:393` still claims it, `:368`
still requires `rc=`, and the §2d.1 question survives intact. Nothing about a cap touches a
row already appended.

**REFUTED as a bound on the damage, on two grounds:**

1. **One poisoned row is not one refused arm — it is the whole item.** `ledger.txt` is one
   file for all ten arms and the refusal at `:397` fires on **line 3**, before any other
   line is examined. The diff's blast-radius paragraph is correct and unchanged by any
   directive: **L2-P, L3-P, A2-P, F2-P and all four SHIPPED arms would each run to
   completion and then be refused at the ledger.**
2. **The class is not closed.** Per 11.1, rc 88 and rc 90 still write the same shape, and the
   producer that writes them is unchanged.

### 11.3 — THE FOURTH PATH: repair A + a clean L1-P re-run. **MEASURED, AND IT DOES NOT WORK — IN EITHER OF THE TWO FORMS IT CAN TAKE.**

The supervisor asked for this to be measured rather than reasoned and to be told if it is
wrong. **It is wrong, and it fails twice over.**

**(a) Does A's prefix dissolve the `duplicate_arm_row` blocker without touching the reader?**
**The question is malformed, because there is no duplicate to dissolve.** Section 8: the
duplicate never fires under any skipping repair. What A's prefix actually does is make the
frozen reader **parse** a ledger *written with it in force* — measured, `baseline` on
`A_applied` → `PARSED keys=['L1-P']`.

**(b) Would a clean re-run then be graded by the instrument? NO, and the measurements are in
section 8a.**

| what actually happens | measured outcome |
|---|---|
| A lands **today**, L1-P re-runs cleanly, row appended to the same `ledger.txt` | **frozen reader REFUSES `row_unparseable`.** A cannot rewrite line 3 — `:925` is `tee -a`. The fourth path never even reaches the duplicate. |
| **best case:** A had been in force at 23:30Z **and** L1-P re-runs cleanly | **frozen reader REFUSES `duplicate_arm_row`.** `ledger.txt:7` (`rc=1`, 16.067 core-min) is a legitimate completed record; the re-run adds a second `ARM=L1-P`. |
| a **fresh run root** with a fresh `ledger.txt` | parses (`L1-P.rc=0`) — **and then refuses `G1 arm_absent_from_ledger` for the other nine arms** (section 7.2), because `d8g_grade.py` grades the ITEM over `ARMS_REQUIRED`'s ten arms and has no `--arm` mode. |

> **EVIDENCE SAYS: the fourth path buys nothing for ~16 core-min. It does not deliver an
> instrument-backed L1-P verdict, because no configuration of this instrument grades L1-P
> alone — and in the same-root form it is stopped earlier than that, by the very blocker it
> was hoped to dissolve.** The supervisor asked to have the hypothesis refuted now rather
> than after ruling; this is that refutation, and every line of it is re-derivable from
> `d8g_ledger_repair_probe.py`.

**WHAT SURVIVES OF THE FOURTH PATH, said fairly.** If D8G is eventually re-run as a whole
item into a **fresh run root** — all ten arms, a fresh `ledger.txt` — then with **repair A
in force from the start** the frozen reader parses without any reader relaxation, the
poisoned row stays in place in the old root as evidence, and no §2d.1 exception is needed
for the comparator at all. **That is a real and attractive property of A. It is also a
statement about a future item run, not about rescuing the run that exists** — and it is the
same prospective route §2d.5's R6 ruling already prescribes (section 5a).

---

## 12. COST

**0.000 solver core-minutes.** No container, no solve, no queue entry. All work was
read-only file inspection plus in-memory patched copies of a frozen reader, executed in a
self-removing tempdir. **No `docs/COST_CALIBRATION.md` row is owed for this task** — rule 12
keys calibration to a completed *process* (a rung graded, a case closed); **D8G is neither,
and that is exactly the state this document is evidence about.** The item's own calibration
row remains owed at D8G's completion, as `d8g_grade.py:1405` already records.

**SUBMISSIONS PARKED. NOT FILED ANYWHERE. NOTHING LEAVES THE BOX.**
