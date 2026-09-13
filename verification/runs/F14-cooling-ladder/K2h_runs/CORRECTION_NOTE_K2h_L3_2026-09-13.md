# CORRECTION NOTE — `GRADE.K2h_L3.json`, 2026-09-13 ~05:20Z

**Dated correction filed BESIDE the grade record. It corrects no number, moves
no gate and changes no verdict.** `K2h_L3` remains **`PASS`**, `DPbar`
**27.981013405397942** m²/s² inside the pre-registered §6 `G-DPBAR` band
[27.9699, 28.0901].

**The grade record is NOT edited and the frozen registration is NOT edited.**
The source string is repaired at the next legitimate edit of that instrument,
with this note as its warrant. A comparator is not touched to fix a sentence
that feeds nothing.

---

## 1. THE STALE SENTENCE — `cap_note` ASSERTS AN OPEN QUESTION THIS TEAM CLOSED

`GRADE.K2h_L3.json` emits, in `cap_note`:

> *"Whether a cap crossing forces `NOT A RESULT` is **ESCALATED AND UNRULED**
> (her item 7 'cap -> NOT A RESULT, never raised' against her 2026-08-26
> universal rule that bookkeeping never voids physics, against this entry's own
> `_field_classes` which places cost among the INFRASTRUCTURE fields)."*

***IT IS NOT ESCALATED AND IT IS NOT UNRULED.*** **ADDENDUM 6** (`606330123`,
2026-09-12 ~23:05Z) resolved it and withdrew it from Sanaa's desk, verbatim:

> *"§AD2.3 escalated whether a cap crossing forces `NOT A RESULT`. **IT IS
> RESOLVED AND IT IS NOT A DESK ITEM.** … **Sanaa's directive #17 of 2026-09-12
> 04:20Z is explicit and standing — no run is stopped by a time or budget cap,
> by any team. THE CAP IS RECORDED AS CROSSED AND THE RUN CONTINUES TO 112 s.**
> The crossing is a **reported fact**, never a verdict and never a kill."*

**The ruling is: `cap recorded, never enforced`.** The string predates
ADDENDUM 6 and was carried into the emitted record unchanged.

***WHY THIS IS WORTH A FILED NOTE RATHER THAN A SHRUG:*** the grade record is
the artifact that travels. **A reader who opens it rather than the board now
finds this lab asserting that a question is open which this lab closed and
announced closed** — and that sentence is exactly the shape that gets quoted
back as evidence the question is still live.

## 2. THE VERDICT IS UNAFFECTED, AND THAT IS VERIFIABLE IN SOURCE RATHER THAN ASSERTED

`cap_note` feeds no verdict. **Every write to `out["verdict"]` in
`analyse_k2h.py` — lines 1040, 1128, 1139, 1144, 1160 — is governed by
`D-COMPLETE`, `D-STATIONARY` or the `G-DPBAR` band, and no cap term appears in
any of them or in any condition governing them.** Checked by reading every
assignment and its guard, not by trusting the instrument's own claim about
itself. The instrument's stated design — *"reports the crossing beside the
physics verdict and lets it move the physics verdict in NEITHER direction"* —
is what the code does; only its account of the escalation's **status** is stale.

## 3. A THIRD ITEM, FOUND WHILE VERIFYING THE SECOND, RECORDED SO IT IS NOT READ AS A DISCREPANCY

**Two committed artifacts carry two different cost figures for this one run, on
two different bases, and both are correct on their own basis:**

| artifact | figure | basis |
|---|---|---|
| `GRADE.K2h_L3.json` `cost.total_core_min` | **1,915.09 core-min** | `ExecutionTime` × ranks ÷ 60 |
| `docs/COST_CALIBRATION.md` row `C-20260913T051107.896956Z-acbb2ded` | **1,919.60 core-min** | **`ClockTime` (wall) × ranks ÷ 60** |

**The calibration row is on the basis `CLAUDE.md` rule 12 fixes — *"wall s ×
ranks ÷ 60"* — and that is the one the ledger must carry.** The difference is
**4.51 core-min**, and it is not a disagreement: **it is exactly the measured
contention, 0.24 %** (`exe/clk` 0.9984 and 0.9975), which is the gap between CPU
held and wall elapsed by definition. Named here so a later reader comparing the
two artifacts finds the reconciliation already done rather than opening an
investigation into a 4.5 core-min "error".

## 4. `GRADE.K2h_L3.json` IS NOT VALID JSON — REPORTED, NOT REPAIRED HERE

The file is a **21,396-byte JSON document followed by 1,167 bytes of
human-readable banner**, total 22,563. **`json.load()` raises
`JSONDecodeError: Extra data: line 557 column 1`**; `raw_decode` recovers the
document intact. The extension asserts something about the file that is false.

**The consumer question was answered before anything was proposed, and the
answer is that NOTHING consumes this file by `json.load` today:**

- The only two code references to `GRADE.K2h_L3.json` are inside this campaign.
  **`autograde_k2h.sh` already handles the banner** — it regex-extracts
  `^\{.*?\n\}` and falls back to grepping a `VERDICT:` line. **`cost_row_k2h.py`
  mentions the filename only inside a prose string** (line 243) and never opens it.
- `scripts/census_never_run.py` sweeps `.json` files at line 506 inside
  `try/except: continue`, so it would **silently skip** this file rather than
  crash — and it is hunting remote-directory keys, not verdicts. Its
  GRADED-overlay limb reads files as **text** and is unaffected.

***THE REASON THIS IS A REAL TRAP AND NOT A THEORETICAL ONE:*** the lab already
has a **working** plain-`json.load` consumer of a sibling grade record —
`sdk/workflows/motor_thermal_act.py:197` does
`json.loads(GRADE.read_text())` on
`verification/runs/T-family/T23_runs/T23_GRADE.json`, **same team, same naming
convention, and that file IS valid JSON, so the consumer works today.** The next
demo workflow written for a `K2h` record would naturally copy that pattern and
break on the banner. **A record a machine cannot read is a record a human
retypes, and retyping is where transcription errors enter.**

**NOT REPAIRED TONIGHT, BY RULING.** Since nothing consumes it, the fix — moving
the banner to a sibling `.txt` — rides with the next legitimate edit of the
instrument rather than justifying another touch of a graded comparator hours
after it graded.

---

*Filed by the heat-transfer lane. Nothing in this rung is sent, filed, uploaded,
registered, posted or commented outside this box (rule 7).*
