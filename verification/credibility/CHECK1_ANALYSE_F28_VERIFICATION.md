# CHECK 1 — `analyse_f28.py` — THE VERIFICATION SUPERVISOR'S INDEPENDENT READ

**Verdict: STAGE 1 DOES NOT OPEN. The instrument must be repaired before it grades.**

- **Read by:** verification-supervisor, personally, in full. `SUPERVISION_CHARTER` §3 check 1 is non-delegable; a relayed check is a summary, not a check.
- **Instrument:** `cases/F28_DUCTED_ACTUATOR_DISK/analyse_f28.py`, 763 lines, md5 `f217d293762b0a644a95f32fb63b850f`.
- **Identity proved before reading:** worktree and the HEAD blob both hash to `f217d293762b0a644a95f32fb63b850f` — **measured on both sides**, so the file read is the file that would grade.
- **Handover:** cfd, `ea6f9992`, which explicitly does **not** treat its own read as sufficient. cfd's read is **independently confirmed on every one of its four findings**, and it was right to refuse to open Stage 1 on its own authority.
- **Compute: zero.** No solver ran. Nothing in this record cites a number produced by this instrument, because it has produced none.

---

## 1. cfd'S HEADLINE FINDING IS CORRECT, AND IT IS SHARPER THAN cfd STATED IT

cfd reports that the planted control guards `read_volScalarField`, which produces no graded number, while every graded quantity arrives through `function_object_series`, which has no control. **Confirmed — and the true statement is stronger.**

**MEASURED: the planted reader's VALUE reaches zero graded numbers. Its entire contribution to the comparator is one array length.** In `disk_pressure_rise` — C1's own function — `read_volScalarField` is called at `:471`, and `vals` is then used at `:472` (a `None` test) and `:477` (`len(vals) != len(vol)`) **and never again**. The graded quantity `delta_p_measured_Pa` at `:506` is `RHO * (dn - up)`, and `dn`/`up` come from `function_object_series` at `:490-491`.

Every graded path traced to its source:

| gate | graded quantity | reader it actually comes from | planted control on that reader |
|---|---|---|---|
| C1 | `delta_p_measured_Pa` | `function_object_series` (`diskPlaneUp`/`Down`) | **none** |
| C2 | `mdot_loaded` / `mdot_baseline` | `function_object_series` (`diskFlow`) | **none** |
| C3 arm (a) | `T_disk_analytic_N` | registered constants | n/a |
| C3 arm (b) | `T_disk_from_source_N` | `read_fvoptions_source` + `cell_volumes` | **none** |
| C4 | `measured_delta_p_Pa` | `function_object_series` | **none** |
| §6.3 | `T_total_N` | `function_object_series` (`forcesDuct`) | **none** |

**Not one graded number passes through the reader the plant certifies.** The instrument proves a reader can see a non-zero, then grades with three readers never shown able to see anything. That is standing rule 3 satisfied in form and defeated in substance, and §2j (the birth requirement) asks the disqualifying question directly: **who wrote the bytes this control reads?** Here — the control itself, into a field nothing grades.

## 2. A SECOND HOLE, NOT ON cfd'S LIST: THE AGE GUARD DOES NOT REACH THE GRADED PATH EITHER

**The same files that carry every graded number are also outside standing rule 4's clause 6.**

`completion()` age-guards exactly `FIELDS_REQUIRED = ("U","p","k","omega","nut")` inside the time directory (`:384-389`). **`postProcessing/` is never stat'd, never age-guarded, and never checked against `endTime`** — `getmtime` appears only at `:383-389`, and no function-object row is compared to `end_time` anywhere in the file.

The only time check on the graded data is `:501`, and it compares `diskPlaneUp` to `diskPlaneDown` **against each other**, never against `endTime`. **Two equally stale files from a previous run satisfy it.** So a `postProcessing/` tree surviving from an earlier solve is graded silently, which is the precise failure clause 6 exists to prevent — the guard is mounted on the fields, and the numbers come from somewhere else.

**Compounded with §1: the graded path is unprotected by BOTH standing rule 3 and standing rule 4 clause 6.** Either alone is a repair; together they mean no number this comparator emits is yet evidence.

## 3. A THIRD, MINE: THE GRADER PERMANENTLY REWRITES THE ARTIFACT IT GRADES

`plant_into_p` writes the solved `p` field **twice** — perturb (`:434`) and restore (`:444`) — both through `write_volScalarField_values`, which re-renders **every value** as `%.12g` and rewrites the whole values block.

**After a successful control, `<tdir>/p` is no longer the solver's bytes, and its mtime is the grader's.** The check at `:451` compares **values only**; its own refusal text at `:452` says *"byte-for-value"*, which is honest about what it does not check. This lab's product is defined as a number that cites **an artifact still on disk** — and here the grader has overwritten the artifact.

This also isolates cfd's `%.12g` finding correctly. The restore is exact **only while OpenFOAM's `writePrecision` is ≤ 12 significant digits**, which is nowhere asserted. Above 12 the restore is lossy — and the consequence is a **refusal** at `:451`, so it is fail-closed rather than silent. **cfd's "safe only by accident" is the right characterisation**: the safety is real, unasserted, and owned by a setting in a different file.

## 4. cfd'S REMAINING TWO, CONFIRMED BY MEASUREMENT

- **Registered guards with zero call sites — and there are TWO, not one.** Measured: **`guard_virgin_case` 0 call sites** and **`read_volVectorField` 0 call sites**. The first is the worse of the pair: it implements §11.1's rule that *"no run in this case is ever started on top of an existing time directory"*, it is written correctly, and **nothing invokes it**. A guard that is defined but never called is a dead lever in the exact sense `DEAD_LEVER_AUDIT` uses the term.
- **Non-deterministic row selection.** `function_object_series` iterates `os.listdir` at `:517-518` — arbitrary order — and breaks ties with `>=` at `:535`, so **on equal `Time` the last-visited file wins and the winner is decided by OS iteration order**. Restarts are exactly how two files come to carry the same final `Time`. Additionally `row.get("Time", 0)` **silently defaults a missing `Time` column to 0**, so a malformed series sorts to the bottom instead of refusing — in a file whose stated discipline elsewhere is *"the reader will not guess the alignment"* (`:531`).

## 5. ONE MORE, MINOR AND WORTH FIXING WHILE THE FILE IS OPEN

`total_thrust`'s docstring claims it returns *"`T_total`, `T_disk` and `T_duct`"*. The loop at `:589` has **one** entry and returns **only `T_duct`**, which `control_6_3` then consumes as `t_total` (`:697`). No number is wrong — `T_total` **is** `T_duct` for the empty duct — but a measurement script's docstring naming three quantities and returning one is how a later reader mis-cites the result.

---

## WHAT IS NOT WRONG WITH IT, SAID PLAINLY

The instrument is **well built** and most of it is right, and a review that only lists defects misrepresents it. The three silent factors in its header — `volumeMode`, `WEDGE_SCALE`, and the kinematic-vs-force-density factor of 1.2 — are real, correctly diagnosed, and genuinely caught by C3's two independent arms. `read_fvoptions_source` refuses on the frozen `volumeMode` rather than assuming it. The C4 negative limb is one-way and correctly says so. §6.3 registers **sign as well as magnitude**, which closes a hole the directive left open. `cell_volumes` reads the **built** mesh rather than the requested grading. **None of that is disturbed by the findings above, and none of it should be rewritten in the repair.**

## THE REPAIR THIS READ REQUIRES — SCOPE ONLY; THE FIX IS cfd'S

1. **A planted control on `function_object_series`**, written through the real production path: perturb a `postProcessing/.../surfaceFieldValue.dat` on disk, read it back through that same function, and refuse if the reader cannot see it — with the negative limb, as `plant_into_p` already does correctly for `p`.
2. **Extend the age guard to every file any graded number is read from**, and check each function-object row's `Time` against `endTime`.
3. **Call `guard_virgin_case`**, or strike it and say why.
4. **Make row selection deterministic** (sort the listing; refuse a tie rather than break it) and **refuse a missing `Time` column** instead of defaulting it to 0.
5. **Do not mutate the graded artifact** — plant into a copy, or assert `writePrecision` and restore the original bytes.

**This is scope, not instruction.** The instrument is cfd's, the registration is cfd's, and the repair is cfd's to design; §2d.1's repair exception governs whether any of it may touch a frozen comparator. **Stage 1 stays gated until a re-read.**

---

## DATED CORRECTION, 2026-08-31 — **I CERTIFIED A PERMANENTLY BLIND GUARD AS WORKING, AND SO DID cfd. THE READ WAS NOT THE PROBLEM; READING WAS.**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** Raised by cfd, who withdrew the same sentence from their own record at `9c223449`. **Verified here by me, by exercise rather than by re-reading.**

### THE SENTENCE THAT IS FALSE

My section *"WHAT IS NOT WRONG WITH IT"* asserts: ***"`read_fvoptions_source` refuses on the frozen `volumeMode` rather than assuming it."*** **That is false, and it is struck.**

`read_fvoptions_source` uses `re.search(r"volumeMode\s+(\w+)\s*;", t)` over the **whole file** and takes the **FIRST** match. In `constant/fvOptions` the first occurrence is **line 6 — a banner COMMENT**, which reads:

> `` `volumeMode specific;` APPEARS HERE VERBATIM AND IS LOAD-BEARING. ``

The **live entry is at line 56**. **The guard never reaches it.**

### MEASURED, ON THE REAL FILE, BY DRIVING IT — NOT BY LOOKING AT IT AGAIN

Against `verification/runs/F28_runs/FEAS_L1_dp1000_U20/`, through the real `read_fvoptions_source`:

| what was done to the LIVE entry (line 56) | what the guard reported |
| --- | --- |
| untouched (`specific`) | `specific` |
| **mutated to `absolute`** — the exact silent-rescale failure §2.4 exists to catch | **`specific` — DID NOT REFUSE** |
| **deleted entirely** | **`specific` — DID NOT REFUSE** |

**The guard cannot fail.** It reports `specific` for every possible state of the entry it claims to check, **including the entry's absence** — and the comment that defeats it is the comment explaining why the token is load-bearing.

### THE SIBLINGS, CHECKED BECAUSE RULE 14 REQUIRES EVERY CALL SITE

Same function, same first-match pattern. **`selectionMode` matches line 54 and `cellZone` matches line 55 — both the live entries, both correct.** But `cellZone` also appears in the header comment at line 2, and the pattern's `\s+` **crosses newlines**; it is saved only because line 3 opens with a **backtick** before `disk`, which `(\w+)` cannot match. ***Both siblings are right by luck, not by design***, and the same `\s`-crosses-a-newline trap is already documented in this lab at `scripts/append_record.py:463-469`.

### ⚠ THE META-FINDING, AND IT IS THE PART THAT MATTERS

**Two independent supervisors performed a full, personal, non-delegable check-1 read of this file and BOTH certified a guard that cannot fail.** cfd read it as a diff; I read all 763 lines and traced every graded quantity to its reader. **Neither of us caught it, and the defect is a two-line regex against a file we both had open.**

**cfd's discovery route is the whole lesson: they found it by RUNNING the thing, not by reading it.** So:

> **`SUPERVISION_CHARTER` §3 check 1 is NECESSARY AND NOT SUFFICIENT. A measurement script's guards are not believed until they have been EXERCISED against the artifacts they guard — driven to their refusal by a mutation, exactly as `CLAUDE.md` rule 3 requires of a reader.**

This lab already knows this in one place and not the other: `append_record.py` pairs **every** refusal limb with a driven mutation that must flip it, and that discipline is why its selftest is worth something. **The F28 comparator has a planted control on `p` and no exercised control on any guard in `read_fvoptions_source`.** A guard never driven into its refusal is a guard nobody has seen work — and this one has now been driven, and does not.

**Referred to Sanaa as a candidate standing rule; NOT spawned as one**, because rules spawn only with her approval under the 14-day freeze.

### WHAT STANDS IN THE ORIGINAL RECORD

**The verdict is unchanged and is now over-determined: STAGE 1 DOES NOT OPEN.** Every other finding stands as written — the planted reader's value reaching zero graded numbers, the age guard not reaching `postProcessing/`, the grader rewriting the artifact it grades, the two zero-call-site guards, the non-deterministic row selection. **This correction adds a defect; it withdraws only the one sentence quoted above, and it removes `read_fvoptions_source` from the list of things this instrument does right.**

---

## DATED CORRECTION TO THE CORRECTION, 2026-08-31 — **MY MECHANISM WAS WRONG. THE BACKTICK SAVES NOTHING; WHAT SAVES THE SIBLINGS IS THAT NO COMMENT HAPPENS TO QUOTE THEM IN ENTRY FORM — AND THAT IS ONE CAREFUL COMMENT AWAY FROM EVAPORATING.**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** Raised and measured by cfd; **re-measured here before acceptance.**

### WHAT I GOT WRONG

The correction above says the sibling guards *"are saved only because line 3 opens with a **backtick** before `disk`, which `(\w+)` cannot match."* **The conclusion — right by luck, not by design — was correct. The MECHANISM I gave for it was false**, and a false mechanism in a record is worse than no mechanism, because the next reader defends against the wrong thing.

**MEASURED, on the real patterns:**

| comment text | guard reports |
| --- | --- |
| `` `volumeMode somevalue;` APPEARS HERE VERBATIM `` | **`somevalue`** |
| `` `selectionMode somevalue;` APPEARS HERE VERBATIM `` | **`somevalue`** |
| `` `cellZone somevalue;` APPEARS HERE VERBATIM `` | **`somevalue`** |
| `` quote: `cellZone disk;` end `` — **backticked entry** | **`disk`** |
| `on the cellZone` ⏎ `` `disk`. `` — the real lines 2–3 | **no match** |

**A BACKTICKED VERBATIM QUOTE BLINDS THE GUARD EXACTLY AS WELL AS AN UNBACKTICKED ONE** — line 6, which blinds `volumeMode`, **is itself backticked**. The real `cellZone` comment escapes only because its backtick sits **between the whitespace and the value** (`cellZone` ⏎ `` `disk` ``), so `(\w+)` fails at that one position. **That is a coincidence of prose layout, not a property of backticks.**

### THE SHARPER RULE, WHICH IS THE ONE TO CARRY

> **A guard of this shape goes blind whenever ANY comment in the file contains the dictionary entry in bare `keyword value;` form — with or without surrounding backticks.** The siblings escape only because **no comment happens to quote them that way yet.**

**And the trap is aimed precisely at conscientious authors: quoting the entry verbatim in a comment is exactly what a careful author does.** That is not hypothetical — **it is literally how `volumeMode` was blinded.** The comment that says *"`volumeMode specific;` APPEARS HERE VERBATIM AND IS LOAD-BEARING"* is a careful author explaining a load-bearing token, **and it is the thing that destroyed the guard protecting it.** So the two surviving guards are not merely lucky; **they are one careful comment away from failing, and the more carefully the file is documented the likelier that comment becomes.**

### cfd'S FIX IS THE RIGHT SHAPE, AND IT IS `§2l` IN PRACTICE

cfd's structural repair — **strip comments before parsing; refuse on multiplicity; refuse on absence; with a planted mutation limb that inserts a verbatim-quoting comment** — covers **all three** guards rather than the one that fired. **That is `VERIFICATION_CHARTER` §2l exactly: remove the POSSIBILITY, not the INSTANCE.** Patching `volumeMode` alone would have left two guards standing on prose layout. **Endorsed.**

### ⚠ THE PATTERN IN MY OWN CONDUCT, WHICH IS NOW THE REAL FINDING

**This is my THIRD error on the same 40-line function, and all three are one species.** I certified the guard as working; then I explained its siblings' survival by a mechanism I had not run; **each time I reasoned about a regex from its SHAPE instead of EXECUTING it, and each time cfd found the truth by running it.**

**Three specimens now support the rule this team referred to Sanaa at `§2n.18`, where one supported it an hour ago.** The referral is unchanged in substance and stronger in evidence: **a supervisor's read — however careful, however complete, however senior — is necessary and not sufficient.** The instrument must be **exercised**. I am the specimen, three times over.

---

## DATED CORRECTION, THIRD ORDER, 2026-08-31 — **I OVER-CORRECTED. THE SENTENCE I STRUCK WAS TRUE, AND I STRUCK IT AGAINST A TEST I HAD ALREADY RUN.**

**Appended at the foot; nothing above edited. `Lines whose number changed above this section: 0`.** Raised by the F28 repair lane's three-way positional test; **re-measured here.**

### THE THREE-WAY TEST, WHICH SETTLES IT

Both earlier accounts were right, **about different positions of the backtick**:

| the comment | guard |
| --- | --- |
| backtick before the **KEYWORD** — `` `cellZone disk;` `` | **`disk`** — blocks nothing |
| backtick before the **VALUE** — `cellZone` ⏎ `` `disk`. `` | **NO MATCH — blocks** |
| bare entry form — `cellZone disk;` | **`disk`** — blocks nothing |

### WHAT THIS RESTORES

**My original sentence in the first correction is CORRECT AS WRITTEN and is RESTORED:** *"it is saved only because line 3 opens with a **backtick** before `disk`, which `(\w+)` cannot match."* **It named the VALUE position, and at the value position the backtick genuinely does block.**

**What is false — and what stays struck — is only the GENERALISATION** that backticks block in general. **They do not**: line 6, which blinds `volumeMode`, is itself backticked, because its backtick precedes the **keyword**.

**The operative rule is unchanged and remains the thing to carry:** **a guard of this shape goes blind whenever any comment quotes the dictionary entry in bare `keyword value;` form** — backticks around the whole quote do not save it. And the siblings' survival is still **luck, not design**, exactly as first written.

### ⚠ THE FOURTH ERROR, AND IT IS A DIFFERENT AND WORSE SPECIES THAN THE FIRST THREE

The first three errors were **reasoning from a regex's shape instead of running it**. **This one is the opposite failure: I RAN THE RIGHT EXPERIMENT AND THEN MISREAD MY OWN RESULT.**

The test I executed before writing the second correction contained the line
`backtick BEFORE the value  \`disk\`. : None` — **the direct confirmation that my original sentence was true** — and I nonetheless wrote that *"the MECHANISM I gave for it was false"* and struck it. **The data that exonerated the sentence was on my screen when I withdrew it.**

> **OVER-CORRECTION IS A RECORD DEFECT, NOT A VIRTUE.** A verification lab that withdraws true statements under a peer's critique **destroys correct records while looking rigorous doing it** — and it is harder to catch than under-correction, because the withdrawal reads as humility and nobody audits a concession.

**The mechanism was social, and naming it is the point:** a peer I had just been wrong in front of, twice, told me a sentence of mine was false. **I accepted the frame instead of testing the specific claim against my own data.** The correct move was available and cheap — ask *"does their counter-example address MY sentence, or a generalisation of it?"* — and it is now this supervisor's practice to ask it before conceding.

**This does not weaken `§2n.18`.** Exercising the instrument remains necessary. **It adds the other half: exercise it when accepting a correction too, not only when making a claim.** A concession is a claim about your own record.

### WHAT STANDS

**The verdict is untouched: STAGE 1 DOES NOT OPEN.** `read_fvoptions_source`'s `volumeMode` guard is permanently blind — measured three ways, including with the live entry deleted. The siblings survive **by luck at the value position** and fall to **one comment quoting the entry verbatim**. **cfd's structural fix remains endorsed and remains `§2l` in practice.**
