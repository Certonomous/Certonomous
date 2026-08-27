# Re-firing a chain arm into a populated run root — dafoam

**Scope.** The five chain-arm items whose graders read a per-arm kernel record by
glob: **AV1R, AV2R, D18, SO1a, SO1b**. Not D5 or D6 — those are a different
grader family (D5 globs `logname + ".ok.*"`, `d5_grade.py:335`) and nothing here
applies to them.

**Who this is for.** You re-fired an arm, the grader refused at `G1`, and the
refusal looks like a bug. It is not. Read §1 before you touch anything.

---

## 1. The refusal is the guard working. Never relax it.

A second fire of the same arm leaves a second kernel record in the run root, and
the grader **refuses rather than reads**:

```
G1: {"arm_absent_from_ledger": "<ARM>",
     "inspect_record_candidates": [...],
     "note": "exactly one surviving inspect record may stand in for a missing row"}
```

`av1r_grade.py:183` · `av2r_grade.py:172` · `d18_grade.py:192` ·
`so1a_grade.py:245` · `so1b_grade.py:315`

There is a second, independent refusal on the primary path — the ledger rejects
two rows for one arm (`duplicate_arm_row`, `av1r_grade.py:176`, `av2r:165`,
`d18:182`, `so1a:235`, `so1b:305`). The glob path is only reached when the arm is
**absent from the ledger** (`av1r_grade.py:280`).

**THE `len(cands) != 1` ASSERTION IS NOT TO BE LOOSENED, WEAKENED, OR DOWNGRADED
TO A WARNING, EVER.** The line below it is `parts = open(cands[0])`, and `[0]` is
the *oldest* by lexicographic sort — so relaxing the assertion does not restore
grading, it silently reads **rc from an earlier fire**, and under R-RC the rc
value is physics. The guard converts a silent-wrong into a stop. That is its job.

**The run is not corrupt.** Nothing about the refusal implies the solve is bad.
It says only that two records exist and the grader will not guess between them.

## 2. What may be cleared, and how — ARCHIVE, never delete

Prior records are **evidence of an earlier fire**. A deletion inside a preserved
run root is worse than an added, timestamped artefact. So the operation is a
**move**, and nothing is ever removed.

**Where the records live.** `$BASE/${ARM}_${STAMP}.inspect.txt` and
`$BASE/${ARM}_${STAMP}.log`, written to the **run root**, not the arm directory
(`av1r_run_arm.sh:480`, `av2r:460`, `d18:464`, `so1a:474`, `so1b:564`).

**Why a subdirectory is enough.** Both globs are
`glob.glob(os.path.join(base, "<ARM>_*.<ext>"))` — no `recursive=True`, no `**`,
and `*` never matches a path separator. Verified in all five graders
(`av1r:182,189` · `av2r:171,178` · `d18:191,198` · `so1a:244,253` ·
`so1b:314,323`) and demonstrated empirically: two records in the root give
`len(cands) == 2` and refuse; moving one into a subdirectory gives
`len(cands) == 1` and satisfies the guard, with the bytes still on disk.

**Archive to `$BASE/_prior_fires/`, NOT to the arm directory.**
`WORK="$BASE/$ARM"` and every fire begins `sudo -n rm -rf "$WORK"`
(`av1r_run_arm.sh:304,316,329`; same shape in the other four). An archive placed
inside the arm directory is **destroyed by the next re-fire** — the launcher
would perform exactly the deletion this section forbids. `_prior_fires` is not an
arm name and the chain drivers only create `$BASE` when absent
(`if [ ! -d "$BASE" ]`, `av1r_chain_driver.sh:68`), so it survives.

**Keep the newest, archive every prior one.** The fire you want graded is the
current one. Archive the older `${ARM}_*.inspect.txt`, and move its matching
`${ARM}_*.log` with it so the surviving log and inspect record describe the same
fire. (The log glob has no count guard and takes `[-1]`, the newest, so leaving
logs behind is not itself a refusal — but a mismatched pair is a record nobody
can defend.) The `.log.ok.<STAMP>` sentinels do not match `${ARM}_*.log` and
need not be moved.

## 3. Authorisation and the record

**This is a supervisor-authorised step, not a lane's discretion.** A lane that
hits the refusal reports it and stops.

Record the move in **both** the run root's ledger **and** the item's record,
naming: each file moved, the from-path and to-path, the UTC stamp of the move,
and **the md5 of each moved file** — so the archived record is provably the same
bytes as the one that stood in the root. Compute the md5 before the move and
verify it after.

## 4. The stamp is not an ordering key

The fire stamp is `%Y%m%dT%H%M%SZ_$$`.

> **`%Y%m%dT%H%M%SZ_$$` is chronological ACROSS seconds and NOT WITHIN one
> second, because the PID tiebreak is arbitrary. Never use it as an ordering
> key. Two fires inside one second sort by PID, and PIDs wrap.**

Across seconds the date part is fixed-width, zero-padded and UTC, so
lexicographic order equals temporal order. Within one second `$$` is a
variable-width PID: measured, `..._777073` sorts *before* `..._9999`, because
`'7' < '9'`. Anyone writing `sorted(...)[-1]` over these names and trusting it to
mean "latest" is relying on something that is only sometimes true.

## 5. When NOT to re-fire at all

If the prior fire is **the one that bought the item's registered arms**, a
re-fire is a **re-registration question, not an operational one**. It goes to the
supervisor. Do not archive, do not re-fire, do not grade. Rule 2 closes gates at
first compute, and a second fire against a registered arm is a change to what was
frozen — that decision is not in this runbook and is not a lane's to make.
