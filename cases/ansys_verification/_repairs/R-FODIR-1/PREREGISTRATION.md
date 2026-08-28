# R-FODIR-1 — REPAIR REGISTRATION: lexicographic function-object-directory reader

Status: **FROZEN-PENDING (drafted by ansys-lane-opus48; freeze is the supervisor's
act after check-1).**
Class: **repair-registration** (Sanaa 2026-08-28 §3 amendment — a finding-repair is
a frozen, capped, schedulable queue item like a case; queue depth 0 with an open
finding is impossible by definition). This registration is FREEZE-AHEAD work item
1 of 3 for the ansys-verification team, discharging the team's one open measured
finding.
Item: the FODIR (function-object start-time directory) lexicographic-sort defect.
Author lane: ansys-lane-opus48 (Opus 4.8).
Model for successor construction: `cases/ansys_verification/VMFLGPU005/grade_vmflgpu005_s2.py`
(commit `87a624ea`) — the team's own successor-comparator template.

This document is a **prediction-first pre-registration** (CLAUDE.md rule 2). The gate,
standard, acceptance test, cap, and the **predicted outcome of every re-grade** are
committed **before any repair runs**. NO successor comparator is written and NO
re-grade is launched by this document; freezing it is the supervisor's act, and the
successors are built only after the freeze.

---

## 0. VERIFICATION LEDGER — what this lane actually measured (2026-08-28)

Every claim below was measured against disk on 2026-08-28 at HEAD
`c01ae5708ce7b800a5fabc212ec251a17fea7c0e`. Disk-vs-HEAD was judged ONLY by
`git hash-object <p>` vs `git rev-parse HEAD:<p>` (the shared index is poisoned —
~75 territory files are at HEAD but absent from the index, so `git diff HEAD` reports
false pure-deletions on byte-identical files; that method was NOT used).

---

## 1. THE FINDING, WITH ITS MEASURED EVIDENCE

### 1.1 The defect shape

A comparator locates an OpenFOAM function-object time directory with

```python
hits = sorted(glob.glob(pat))     # pat ends in .../<foName>/*/<file>
... return hits[-1]               # or hits[0]  -- "last FO start-time dir"
```

`sorted()` orders directory **names as strings**, i.e. **lexicographically**. Time
directory names are numeric strings, so `"950"` sorts **after** `"2000"` (character
`'9' > '2'`). A reader that intends "the last / numerically-largest start-time
directory" (the code comments say exactly that — `# last FO start-time dir`) silently
reads the **wrong artefact** the moment more than one start-time directory exists.

### 1.2 The 19 hazard sites in 9 files — VERIFIED at the stated line numbers, no drift

Each site below was read from disk on 2026-08-28 and is `sorted(glob.glob(...))` over
a `postProcessing/<foName>/*/...` glob whose `*` matches the FO start-time directory
name, later indexed `[-1]` (all confirmed `[-1]`, the "last start-time dir"). **Every
one of the 19 line numbers in the finding matched byte-for-byte; none has drifted.**

| Case | Grader file | Sites (verified lines) |
|---|---|---|
| VMFL002 | `cases/ansys_verification/VMFL002/grade_vmfl002.py` | 84 (`resid/solverInfo.dat`), 207 (`<name>/surfaceFieldValue.dat`), 214 (`outletT/T_outletPatch.raw`) |
| VMFL004 | `cases/ansys_verification/VMFL004/grade_vmfl004.py` | 84 (`resid`), 206 (`volAvgU`) |
| VMFL004-R2 | `cases/ansys_verification/VMFL004-R2/grade_vmfl004_r2.py` | 129 (`resid`), 318 (`volAvgU`) |
| VMFL011 | `cases/ansys_verification/VMFL011/grade_vmfl011.py` | 84 (`resid`), 195 (`bisector`) |
| VMFL011-R2 | `cases/ansys_verification/VMFL011-R2/grade_vmfl011_r2.py` | 178 (`resid`), 319 (`bisector`) |
| VMFL011-R3 | `cases/ansys_verification/VMFL011-R3/grade_vmfl011_r3.py` | 178 (`resid`), 334 (`bisector`) |
| VMFL021 | `cases/ansys_verification/VMFL021/grade_vmfl021.py` | 123 (`inletMassFlow`), 131 (`outletMassFlow`) |
| VMFL021-R2 | `cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py` | 161 (`inletMassFlow`), 169 (`outletMassFlow`) |
| VMFL022 | `cases/ansys_verification/VMFL022/grade_vmfl022.py` | 123 (`inletMassFlow`), 131 (`outletMassFlow`) |

**NOTE ON A PATH DRIFT (not a line drift):** the VMFL021-R2 grader is NOT at a
`cases/ansys_verification/VMFL021-R2/` directory (none exists on disk or in HEAD). It
lives NESTED at **`cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py`**, mirroring
its run tree under `verification/runs/ansys_verification/VMFL021/R2/`. The finding's
line numbers (161, 169) are correct for that file.

The 19 sites fall into **two shapes** that need two successor templates:

- **Shape A — reader-helper `f = sorted(glob.glob(...)); ... f[-1]`** (13 sites, 6
  files): VMFL002, VMFL004, VMFL004-R2, VMFL011, VMFL011-R2, VMFL011-R3. Distinct FO
  readers touched: `resid/solverInfo.dat`, `<name>/surfaceFieldValue.dat`,
  `outletT/T_outletPatch.raw`, `volAvgU`, `bisector`.
- **Shape B — `def inlet_dat/outlet_dat: hits = sorted(glob.glob(pat)); return hits[-1]`**
  (6 sites, 3 files): VMFL021, VMFL021-R2, VMFL022 — the `inletMassFlow`/`outletMassFlow`
  mass-flow readers, byte-near-identical across the three files.

### 1.3 Exposure — LATENT, NOT ABSENT (stated exactly, per the supervisor's correction)

All nine cases HAVE register rows in
`verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.tsv` — VERIFIED read-only
on 2026-08-28:

| Row | Case | Landed verdict |
|---|---|---|
| 17 | VMFL022 | NOT A RESULT |
| 18 | VMFL021 | NOT A RESULT |
| 23 | VMFL021-R2 | GATE REACHED |
| 24 | VMFL002 | GATE REACHED |
| 25 | VMFL004 | NOT A RESULT |
| 26 | VMFL011 | NOT A RESULT |
| 28 | VMFL004-R2 | **PASS** |
| 31 | VMFL011-R2 | NOT A RESULT |
| 36 | VMFL011-R3 | GATE FAIL |

So **nine landed verdicts sit on hazard-carrying comparators.** They are **NOT
misread** — but the reason is **NOT** "no rows exist." The reason is that **every one
of those cases produced exactly ONE function-object start-time directory**, so the bug
has no second directory to sort wrongly. **The hazard is LATENT and armed by the first
restart, not absent.** A right conclusion on a false premise is still a defect, and a
comparator carrying an armed reader must not stay in the fleet.

**Measured basis for "exactly one start-time directory" (this is the load-bearing
premise for the §5 prediction):** on 2026-08-28 every function-object folder in every
run root of the eight cases that ran was found to hold exactly ONE immediate
start-time subdirectory:

- VMFL002 (L1/L2/L3): `resid`{0}, `pInlet`{0}, `pOutlet`{0}, `outletT`{5000} — each n=1.
- VMFL004, VMFL004-R2 (L1/L2/L3): `resid`{0}, `volAvgU`{0}, `profile`{20000} — each n=1.
- VMFL011, VMFL011-R2, VMFL011-R3 (L1/L2/L3): `resid`{0}, `bisector`{20000} — each n=1.
- VMFL021, VMFL022 (L1/L2/L3): `inletMassFlow`{0}, `outletMassFlow`{0} — each n=1.
- VMFL021-R2 (L1/L2/L3): `inletMassFlow`{0}, `outletMassFlow`{0} — each n=1.

### 1.4 CORRECTION OF FACT owed upward — VMFL021-R2 DID run

The finding-commit `c7176346` carried the parenthetical "(VMFL021-R2 never ran)". **On
disk this is false.** VMFL021-R2 has a complete run tree at
`verification/runs/ansys_verification/VMFL021/R2/` — L1/L2/L3 each with `0`…`0.003`
time dirs, `DONE.flag`, `RUN_RC.txt`, `log.interPhaseChangeFoam`; a
`FAMILY_DONE.flag`; and `GRADING_VMFL021_R2.json` carrying `"verdict": "GATE REACHED"`.
Register row #23 records that landed GATE REACHED with grader blob `87ce3fa6a818…` and
run root `verification/runs/ansys_verification/VMFL021/R2/`. VMFL021-R2 therefore
belongs in the exposure set exactly as row #23 says; its hazard is latent for the same
single-start-time-dir reason as the rest (each FO n=1, §1.3). The "never ran" wording
should be struck from the record.

### 1.5 THE BUG IS DEMONSTRABLY LIVE IN THIS TERRITORY — VMFL076-R2, measured

`verification/runs/ansys_verification/VMFL076-R2/L1/postProcessing/sampleLine` was read
on 2026-08-28: **40 time directories.**

- Lexicographic `sorted(...)[-1]` → **`950`** (string tail `850, 900, 950`).
- Numeric last (`sort -g`) → **`2000`** (numeric tail `1900, 1950, 2000`).
- Lexicographic `[0]` → `100`, then `1000, 1050`.

A hazard-shape reader on this exact input would silently grade the `950` sample as if
it were the final `2000` sample — a wrong artefact, no error raised.

**VMFL076-R2's grader is a CARDINALITY-GUARDED / NUMERIC reference implementation and
does NOT exhibit the defect.** `cases/ansys_verification/VMFL076-R2/grade_vmfl076.py`
`_sample_times()` (lines 663–685) iterates every name under `sampleLine`, casts each
via `t = float(name)` inside a `try/except ValueError` (a numeric-directory test that
correctly rejects a `0.orig`-style name — `float("0.orig")` raises), collects
`(t, file)` tuples, guards the inner file glob with `if len(hits) != 1: refuse("G2",…)`,
and finally `out.sort()` — a **numeric** sort by the float `t`. It selects the
numerically-correct time and never takes a lexicographic `[-1]` of directory names.
This is the reference implementation working on the exact input that breaks the others.

*Honest scope note:* I confirmed the READER is numeric-correct and cardinality-guarded
on the 40-dir input; I did NOT execute the VMFL076-R2 grader end-to-end, so I neither
confirm nor deny any characterization of its final verdict LABEL — I confirm only that
its directory-selection logic does not carry the lexicographic defect.

### 1.6 The nine frozen parents — BEFORE-HASHES (disk == HEAD, all nine)

Recorded 2026-08-28. These are the frozen comparators that **must not change**; §8
re-asserts them after the registration is committed.

| Case | Grader file | before blob (disk == HEAD) |
|---|---|---|
| VMFL002 | `.../VMFL002/grade_vmfl002.py` | `027bcbf72eba…` |
| VMFL004 | `.../VMFL004/grade_vmfl004.py` | `ddea9d473b6d…` |
| VMFL004-R2 | `.../VMFL004-R2/grade_vmfl004_r2.py` | `417b4bbe60f4…` |
| VMFL011 | `.../VMFL011/grade_vmfl011.py` | `e369496bf2e2…` |
| VMFL011-R2 | `.../VMFL011-R2/grade_vmfl011_r2.py` | `45aa4613253d…` |
| VMFL011-R3 | `.../VMFL011-R3/grade_vmfl011_r3.py` | `3975d9ee3a60…` |
| VMFL021 | `.../VMFL021/grade_vmfl021.py` | `7e783fe4aea2…` |
| VMFL021-R2 | `.../VMFL021/R2/grade_vmfl021_r2.py` | `87ce3fa6a818…` |
| VMFL022 | `.../VMFL022/grade_vmfl022.py` | `1c750397a84b…` |

Cross-check: for the three register rows that record a grader blob, the register value
equals the computed before-hash — VMFL022 `1c750397a84b`, VMFL021 `7e783fe4aea2`,
VMFL021-R2 `87ce3fa6a818`. Register, HEAD, and disk agree.

---

## 2. THE ABSOLUTE CONSTRAINT

**THESE ARE FROZEN COMPARATORS WITH LANDED VERDICTS. NONE IS EDITED. EVER.** Rule 2
bars a post-compute edit to a frozen comparator, and all nine have landed register
rows. The repair goes ONLY into **SUCCESSOR comparators frozen by sha**, exactly as
the team did for VMFLGPU005 (`grade_vmflgpu005_s2.py`) and VMFLGPU007-R2 at commit
`87a624ea`. Each successor is a NEW file beside its parent (naming: `grade_<case>_s2.py`,
or `_s3` if an `_s2` already exists for that case), differing from its parent in the
NAMED, MINIMAL set of §3–§4 changes and NOTHING ELSE; every band, threshold, ceiling,
tier, physics constant, completion clause and Roache classifier stays byte-identical to
the parent. §8 re-hashes all nine parents after this commit to prove none moved.

---

## 3. THE REPAIR STANDARD — what a repaired reader must do

A repaired FO-directory reader must select the **numerically-correct** start-time
directory, or **refuse**. Two acceptable forms; each successor states which it uses at
each site.

- **Form (a) — `one_match` cardinality refusal (PREFERRED where the case emits exactly
  one FO start-time dir, which is every current hazard case, §1.3).** The reader refuses
  unless **exactly one** directory matches. This is the family's existing
  `one_match(pattern, clause, what)` (e.g. `grade_vmflgpu005_s2.py:191`): refuse on
  zero matches ("READER ABSENT — never read as a zero"), refuse on `len(hits) > 1`
  ("ambiguous reader could silently pick the wrong file"), else return the sole match.
  For the present cases this is the tightest possible statement of intent: these runs
  are single-shot, one FO start-time dir is the ONLY valid state, and a second one
  (the restart that would arm the bug) makes the reader REFUSE rather than guess.

- **Form (b) — numeric sort with an explicit numeric-directory test (where a case may
  legitimately carry multiple start-time dirs).** Enumerate names, keep a name ONLY if
  it passes a numeric test — `try: t = float(name) except ValueError: skip` (the
  VMFL076-R2 reference form, §1.5) — sort by `key=float` / by the parsed `t`, and take
  the numeric extreme. **NEVER a `[0-9]*` glob** as the directory test: `[0-9]*` also
  matches `0.orig` and would read a template directory as an answer (L-339). The float
  cast is the correct membership test; the glob is not.

**Refusal discipline (both forms):** every refusal is an explicit branch into
`refuse()`, **never** an `assert` (`python3 -O` strips asserts, evaporating the guard
exactly when run for speed). Every planted-failure arm asserts the expected refusal
TEXT, not merely a non-zero exit (L-357).

**Site-by-site plan:** because every current hazard case emits exactly one FO
start-time dir (§1.3), **Form (a) is used at all 19 sites.** Form (b) is registered as
the standard for any FUTURE reader that must legitimately span multiple start-time
dirs, and is the pattern a successor MUST switch to if, on re-grade, a case is found to
carry more than one FO start-time dir (which would also be the §5 major-finding
trigger).

---

## 4. THE PLANTED-ZERO REQUIREMENT (rule 3 + Sanaa 2026-08-28 §1 birth requirement)

Every successor carries a planted-zero control meeting the birth requirement in full,
modelled on `grade_vmflgpu005_s2.py:637` (`planted_zero_control`):

1. **Written by the real producer's path, read back FROM DISK through the REAL reader.**
   The plant is written into a COPY of the case's own real FO sample file on disk (the
   same file the gate reader parses, located through the successor's OWN reader), then
   read BACK through the successor's unmodified file reader — never injected downstream
   of the reader into already-parsed rows (that is exactly the register-row-#31-class
   failure the VMFLGPU005 parent carried and S2 repaired).
2. **Through the FULL gate functional.** After read-back, the planted file is run
   through the same reducer the gate uses (max/mean/window), and the control asserts the
   gate quantity MOVED by the planted amount — a plant the raw reader sees but the gate
   does not is still blindness.
3. **Sized to the channel, applied to every element.** The plant is a fraction of the
   in-window signal scale (never a fixed absolute an averaging reader dilutes as
   1/√N — L-340), and applied to EVERY row so it can never fall outside the reader's
   support (L-347's out-of-support placement failure).
4. **Refuses via `refuse()`, never `assert`** (`python3 -O`-safe).
5. **Driven to BOTH outcomes in `--selftest`.** A positive arm shows the control FIRES
   on the planted bytes; a suppress arm (`_selftest_suppress_plant=True`) withholds the
   plant and shows the control REFUSES — proving the instrument can fail, not merely
   pass. A control only ever shown passing certifies nothing.

Because this repair concerns **which directory** is read, each successor's planted-zero
control additionally travels through the **repaired directory selector** — i.e. the
plant is written into the file inside the directory the repaired reader SELECTS, so the
control proves the successor reads the plant from the directory it claims to read.

---

## 5. THE ACCEPTANCE TEST — pre-registered before any repair runs

Each successor's `--selftest` MUST contain a directory-selection test that **proves the
bug existed and that the fix defeats it**, not merely that the right answer comes out:

1. Build a scratch tree with start-time directories **`0`, `950`, `2000`** under a
   mock `postProcessing/<foName>/`, each holding the FO's expected file.
2. Assert the **lexicographic** answer WOULD be `950`:
   `assert sorted(os.listdir(mockdir))[-1] == "950"` — i.e. demonstrate, in the test,
   that the OLD selector picks the wrong directory on this input. (This assertion is a
   TEST-fixture check of a library primitive, not a production guard, so `assert` is
   acceptable here; the production selector uses `refuse()`.)
3. Assert the **repaired** helper returns the directory whose numeric time is `2000`
   (Form (b) path), OR — for Form (a) — assert the repaired helper **REFUSES** on this
   3-directory input (because `len(hits) == 3 > 1`), with the expected refusal clause
   text. Under Form (a) the acceptance criterion is: *the repaired reader refuses to
   silently pick, where the parent would have silently picked `950`.*
4. A test that only checks the right answer on a single-directory input does NOT show
   the bug was ever present and is INSUFFICIENT.

The acceptance test is frozen HERE, before any successor is written.

---

## 6. THE RE-GRADE ARM AND ITS PREDICTION (prediction-first)

Each repaired successor re-grades its case's **preserved artefacts** (the run roots in
§1.3, already on disk) at **ZERO SOLVER COMPUTE** — the successor reads the same
preserved outputs the parent graded; no solver runs.

**PREDICTION, registered before any re-grade runs:** because every hazard case emits
**exactly one** FO start-time directory (§1.3, measured), the repaired reader selects
the same sole directory the parent selected. Therefore **NO VERDICT MOVES.** Every
re-grade is predicted to reproduce the parent's landed verdict EXACTLY:

| Row | Case | Landed verdict | Predicted re-grade verdict |
|---|---|---|---|
| 24 | VMFL002 | GATE REACHED | GATE REACHED (unchanged) |
| 25 | VMFL004 | NOT A RESULT | NOT A RESULT (unchanged) |
| 28 | VMFL004-R2 | PASS | PASS (unchanged) |
| 26 | VMFL011 | NOT A RESULT | NOT A RESULT (unchanged) |
| 31 | VMFL011-R2 | NOT A RESULT | NOT A RESULT (unchanged) |
| 36 | VMFL011-R3 | GATE FAIL | GATE FAIL (unchanged) |
| 18 | VMFL021 | NOT A RESULT | NOT A RESULT (unchanged) |
| 23 | VMFL021-R2 | GATE REACHED | GATE REACHED (unchanged) |
| 17 | VMFL022 | NOT A RESULT | NOT A RESULT (unchanged) |

**Both outcomes are named as live.** If a verdict DOES move, the prediction was WRONG,
and that is a **major finding** — it would mean a case in fact carried more than one FO
start-time directory (contradicting §1.3) and its landed verdict rested on the misread
`950`-class artefact. Under Form (a) a "move" surfaces as a REFUSAL (the successor
refuses on `len(hits) > 1`), which is itself the correct, honest outcome and flags the
case for re-run. The pre-registration exists precisely so this fork is decided before
the numbers are seen. Row #28 VMFL004-R2 (PASS) is the highest-value verdict in the set
and its non-movement is predicted with the same basis as the rest.

*Note:* a re-grade that reproduces a parent's NOT A RESULT / GATE FAIL does NOT
re-license the verdict beyond what the parent earned; it confirms the reader defect did
not manufacture it. The verdict credential remains the parent's.

---

## 7. COST

Repair work is **grader authoring (lane token work, not solver core-minutes) plus
zero-solver-compute re-grades**. The costed compute is only the successor Python
processes: for each case, one `--selftest` run (drives every guard, the §4 planted-zero
both arms, and the §5 acceptance test) and one re-grade over preserved artefacts. Each
is a single-rank Python invocation over on-disk files, wall time seconds, no solver.

- **Per-case cap: 3.0 core-min** (generous; measured comparators of this family run in
  a few seconds wall × 1 rank ≈ well under 0.5 core-min for selftest + re-grade
  combined; the cap absorbs re-runs and I/O on the larger run trees).
- **Cap shape: PER CASE, and a RUNNING TOTAL for the registered tranche.** The running
  total is `3.0 core-min × (number of cases in the tranche)`. First tranche (§9, 3
  cases) running-total cap = **9.0 core-min**. An overrun STOPS the run (rule 12); it
  does not get a new budget.
- **`cost_basis`: DERIVED, not measured**, at c7a.4xlarge $0.0513/core-h (the box
  cannot read its own billing). 9.0 core-min = 0.15 core-h → **$0.0077 derived** for
  the first tranche; the full nine cases ≈ 27 core-min → 0.45 core-h → **$0.023
  derived**. Estimate-vs-actual calibration (rule 12) is filed to
  `docs/COST_CALIBRATION.md` at completion of each tranche by the supervisor.

---

## 8. FROZEN-PARENT RE-ASSERTION (post-commit, this registration only)

This registration writes ONLY files under
`cases/ansys_verification/_repairs/R-FODIR-1/`. It touches NO grader. §1.6's nine
before-hashes are re-computed immediately after this document is committed; each must
still equal its §1.6 value. Any successor written later re-asserts them again before
and after its own commit.

---

## 9. SEQUENCING — recommended order and why

The nine hazard cases are all EQUALLY latent (each single-start-time-dir, §1.3); none
is more realized than another, so ordering is by **template economy and validation
value**, not by exposure. Two shapes (§1.2) need two successor templates; each template
covers a family cheaply.

**RECOMMENDED FIRST TRANCHE (register and run under the §7 cap = 9.0 core-min):
Shape B — the mass-flow readers, 3 cases.**

1. **VMFL022** (row #17) — first. Shape B, self-contained, and its parent already
   carries a `LANE_REPORT_opus48_collision.md` note, so it is the cleanest place to
   validate the successor pattern.
2. **VMFL021** (row #18) — Shape B, byte-near-identical `inlet_dat`/`outlet_dat`; the
   VMFL022 successor transfers almost verbatim.
3. **VMFL021-R2** (row #23) — Shape B, and its record needs the §1.4 correction landed;
   its re-grade confirms GATE REACHED holds and closes the "never ran" error with a
   fresh grading artefact.

Rationale for a capped 3-case first tranche (per the brief's invitation): registering
all nine here would make the cap dishonest, because Shape A spans **five distinct FO
readers** (`resid`, `surfaceFieldValue`, `outletT` raw, `volAvgU`, `bisector`) whose
successors are not a single transferable template and warrant their own sized
registration. Shape B is one template over three near-identical files — a tight,
honestly-capped unit that also validates the whole successor+planted-zero+acceptance-
test machinery before the more varied Shape A work.

**SECOND TRANCHE (to be registered separately, NOT covered by this cap): Shape A — 6
cases.** Suggested order VMFL011 → VMFL011-R2 → VMFL011-R3 (shared `bisector`/`resid`
readers, one template covers three) → VMFL004 → VMFL004-R2 (shared `volAvgU`/`resid`)
→ VMFL002 (the widest, 3 sites incl. `outletT` and `surfaceFieldValue`). That tranche
gets its own PREREGISTRATION with its own cap.

---

## 10. WHAT THIS LANE DID NOT VERIFY

- I did NOT execute any grader (parent or successor) or launch any re-grade; §5/§6 are
  pre-registered predictions, not measurements, by design.
- I did NOT run the VMFL076-R2 grader end-to-end; §1.5 confirms only that its
  directory-SELECTION logic is numeric/guarded, not any final verdict label.
- I did NOT exhaustively re-classify all `sorted(glob.glob(...))` sites in the
  territory (31+ across all ansys graders) into hazard vs guarded; I VERIFIED the 19
  named sites and confirmed each is the hazard shape, and I confirmed the VMFL076-R2
  reference is numeric/guarded. The claim "these 19 are the COMPLETE hazard set" rests
  on the supervisor's prior sweep, not on an independent full re-derivation by me.
- I did NOT read the full body of every one of the nine parents; I read the sites, the
  indexing context, and hashed each file whole.
- The register rows were read read-only from the `.tsv`; three rows carry `UNPARSED`
  grader-blob cells, so for six of the nine I could not cross-check the register's
  recorded blob against disk (I cross-checked the three that were parseable, all match).
