# `W3-GRADER-DEF-3` — `G12R-0b` fires on the right condition and names the wrong mechanism

**NOT FILED.** Internal record only. Nothing here is sent, posted or reported outside this
box (`CLAUDE.md` rule 7). This is a defect in **this lab's own comparator**, not in DAFoam or
any upstream project, so no upstream draft is owed.

**Status: REGISTERED, NOT REPAIRED.** This record names a defect and repairs nothing. The
comparator file `d12y_grade_w3.py` is **not edited by this record** and its md5 does not move.

**Date:** 2026-08-31. **Item:** `W3` (`CURRICULUM-D12R2W3-cylinder-unsteady`).
**Component:** the frozen successor comparator `d12y_grade_w3.py`, gate `G12R-0b`.
**Found by:** dafoam-supervisor, reading `W3_plan.out`; written up by a dafoam lane.

**Id derivation (rule 11, from the tail as the maximum existing number, never a count).**
The ids in use in this case directory are `W3-LAUNCHER-DEF-1`, `W3-LAUNCHER-DEF-2`,
`W3-GRADER-DEF-2`, `W3-SELFTEST-DEF-1`, `W2R-GRADER-DEF-1`, `D8R-DRIVER-DEF-1`,
`D12R2-DEF-2`. On the `W3-GRADER` series the **maximum existing number is 2**, so this
record takes **3**. **`W3-GRADER-DEF-1` does not exist anywhere in the repository** — a
grep over `cases/`, `docs/` and `scripts/` returns zero hits — exactly the shape of the
missing `C-102` in `docs/COST_CALIBRATION.md`. **The series is therefore two members
numbered 2 and 3, and a count would have produced the wrong id.** The gap is reported and
**not closed by renumbering anything.**

---

## 1. What it changes: NOTHING

**No gate moves. No threshold, band, cap or label moves. No verdict changes, and no verdict
can be changed by this record.** `G12R-0b` **refused correctly** and its refusal **stands**.
W3 is **`NOT A RESULT`** with this defect and would be **`NOT A RESULT`** without it. The
comparator's *decision* is right; only its *explanation of that decision* is wrong.

This record exists because a refusal message is read by an auditor who was not there, and a
refusal that misnames its own mechanism sends that auditor to hunt a bug that does not
exist.

## 2. The observation, verbatim

`cases/dafoam/curriculum_D12R2/W3_plan.out` — the whole file, one line:

> `REFUSAL: G12R-0b: the manifest and the ledger DISAGREE about which stages ran. In the
> ledger but NOT the manifest: S3b_c1_am, S3b_c1_bp, S3b_c1_bm, S3b_c2_ap, S3b_c2_am,
> S3b_c2_bp, S3b_c2_bm, S3b_c3_ap, S3b_c3_am, S3b_c3_bp, S3b_c3_bm, S4_n20_r1, S4_n20_r2,
> S4_n40_r1, S4_n40_r2, S4_n80_r1, S4_n80_r2, S5, S7_plant, S7_clean. In the manifest but
> NOT the ledger: (none). manifest=13 rows, ledger=33 STAGE= lines. A stage that ran and
> left no row is UNGRADED AND SILENT.`

**The final sentence is false of all twenty names it has just printed.** None of those
twenty stages ran. Each of them is in the ledger only because a `BLOCKED` line was written
for it, and each of those lines says so in its own words. The first and the last, quoted
from `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady/ledger.txt`
[MEASURED]:

> `STAGE=S3b_c1_am BLOCKED memavail_GiB=13.5154 below registered floor 14.0 -- NOT LAUNCHED`
> `STAGE=S7_clean BLOCKED memavail_GiB=13.5007 below registered floor 14.0 -- NOT LAUNCHED`

All twenty carry the token `NOT LAUNCHED` [MEASURED: 20 of 33 `STAGE=` lines match
`BLOCKED`, and the same 20 match `NOT LAUNCHED`, in that ledger]. The floor is the
**registered** `MEMAVAIL_FLOOR_GIB = 14.0` [REGISTERED, `W3_PREREGISTRATION.md` §2 and the
run's own ledger header line `CAP_S8=400.0 MEMAVAIL_FLOOR_GIB=14.0`].

**So the true mechanism is a registered resource gate refusing to launch, working exactly as
frozen. The message asserts a data-loss mechanism — a stage that ran and whose manifest row
went missing — which is the opposite thing and implicates a different component.**

## 3. Where it is, in code

`cases/dafoam/curriculum_D12R2/d12y_grade_w3.py`, function `g0b_manifest_ledger_binding`.

The ledger side of the binding is built at **`:578-580`** by

```python
m = re.match(r"^STAGE=(\S+)\s", line)
if m:
    names_ledger.append(m.group(1))
```

**That regex matches a `BLOCKED … NOT LAUNCHED` line exactly as readily as a completed
stage's row.** `names_ledger` is therefore a list of *declared* stages, not of *executed*
ones, and the set difference computed at `:587-588` is a difference between "declared in the
ledger" and "graded in the manifest" — a perfectly sound thing to refuse on, and **not** the
thing the message at `:589-596` describes.

The wrong sentence is the string literal at **`:592-593`**:

```
"stage that ran and left no row is UNGRADED AND SILENT."
```

**The docstring at `:523-546` shows why the wrong sentence is there and is not a slip.** The
gate was written for `D12R`, where phase 1 **ran** 33 stages and the manifest carried 32 —
`S0` *"did not fail a check — IT VANISHED"*. Against that history the sentence is exactly
right. **The gate was correct for the failure it was born from and was never asked what else
could put a name in the ledger and not in the manifest.** A second mechanism arrived — a
registered floor blocking a launch, a facility that also predates this comparator — and the
message had no branch for it.

## 4. Why the refusal is still correct, stated so the repair is not over-scoped

Two independent limbs of `G12R-0b` refuse this pair, and **both** are right:

1. **The set-difference limb** (`:587-596`; the `if` at `:589`), which fires. The manifest and the ledger *do*
   disagree about which stages the record accounts for, and a comparator must not grade a
   13-row manifest against a 33-stage registered graph.
2. **The registered-count limb** (`:597-602`), which would fire next: *"REGISTERED stage
   count is 33; manifest has 13 rows"*. **This one is unreachable here only because the
   first raises first** — it would refuse the same pair on the same day for a reason that is
   true without qualification.

**A repair that made the message right must not make the gate pass.** The correct shape is a
message that separates the twenty `NOT LAUNCHED` names from any genuinely missing row and
tells the reader which mechanism it found — while still refusing. **This record proposes no
diff.** Any repair to a frozen comparator after first compute is `VERIFICATION_CHARTER.md`
§2b/§2d territory and is the supervisor's call, not a lane's.

## 5. What it cost, and what it would have cost

**Zero core-minutes.** `G12R-0b` runs at zero solver compute and refused at zero. The
defect's price is entirely in **reader time**: an auditor handed `W3_plan.out` alone is told
that twenty stages ran and lost their manifest rows, and would reasonably open the launcher's
manifest writer, the `python open(…, "a")` append path and the `tee -a` ledger path hunting a
write that never went missing. **The ledger itself refutes the message in the same
directory**, which is the only reason this cost minutes rather than hours.

## 6. An adjacent observation, deliberately NOT given an id here

The same ledger closes with

> `PHASE1_COMPLETE spent=63.2332 core-min` [MEASURED, that ledger's last `PHASE1_` line]

**after 20 of its 33 stages were blocked and never launched.** `PHASE1_COMPLETE` is not true
of that run, and `W3_PREREGISTRATION.md` registers prediction **`P4`** to be scored *"from
the ledger's `PHASE1_COMPLETE spent=`"* — so a later reader could book `P4` a **MISS** off a
line that is measuring a different program from the one `P4` prices. **This is a launcher
statement, not a comparator statement, so it is a different component and a different id.**
It is reported here so it is on the record beside the finding it was discovered with, and
**its id is left to the dafoam-supervisor to assign.** Nothing in this record depends on it.

## 7. Provenance of every number above (`DAFOAM_CHARTER.md` §18.6)

| number | tag | artefact |
|---|---|---|
| 33 `STAGE=` lines | MEASURED | `/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady/ledger.txt` |
| 20 `BLOCKED`, 20 `NOT LAUNCHED` | MEASURED | same file |
| 13 manifest rows | MEASURED | `W3_plan.out`, the comparator's own count, corroborated by the 13 executed `STAGE=` rows in the ledger |
| `MEMAVAIL_FLOOR_GIB = 14.0` | REGISTERED | `W3_PREREGISTRATION.md`; echoed in the run's ledger header |
| line numbers `:523-546`, `:578-580`, `:587-588`, `:589-596`, `:593`, `:597-602` | MEASURED | `cases/dafoam/curriculum_D12R2/d12y_grade_w3.py` as of this record |
| 0 core-min cost of the defect | MEASURED | no container fired for `--plan`; `W3_plan.out` is the whole output |
| `W3-GRADER-DEF-1` absent | MEASURED | grep over `cases/`, `docs/`, `scripts/` returns zero hits |

## 8. Cross-references

* Calibration row for the W3 run this was found on: `docs/COST_CALIBRATION.md` **`C-222`**,
  which refuses the whole-item ratio for the same underlying fact (20 of 33 stages never
  ran) and cites this record.
* Sibling defects in this item: `W3-LAUNCHER-DEF-1` (`W3_PREREGISTRATION.md` §11.2),
  `W3-GRADER-DEF-2` (§13), `W3-LAUNCHER-DEF-2`, `W3-SELFTEST-DEF-1`.
* The gate's ancestor defect: `D12R2-DEF-2`, the vanished `S0` that `G12R-0b` was written
  for (`d12y_grade_w3.py:12`, `:2023-2026`).
