# T23G — PRE-FLIGHT FINDINGS ON THE COMPARATOR'S FILE-READING PATHS

**A REFERRAL DOCUMENT. IT PROPOSES NO REMEDY AND GRADES NOTHING.**

**Status:** REFERRED to verification. **Two defects on the T23G grading path
block or corrupt the grading, and both are found on a rung whose compute has
run** — so any repair to either file needs a `VERIFICATION_CHARTER.md` **§2d.1**
ruling, which is verification's and not heat-transfer's. **This document
therefore records what was measured and stops there.** It does not repair either
file, does not propose which repair to take, and is not a retroactive amendment.

**Date:** 2026-09-01. **Written before the fine level landed** — at the time of
writing `T23G_F` was still solving and **nothing under it was read, not one file,
not even a static log.**

**Nothing in this document is a verdict on the T23G rung.** No quantity here may
be quoted as a result, and the numbers below are instrument diagnostics measured
on scratch copies.

---

## 0. WHY THIS WAS DONE, AND WHAT IT COVERED

`verification/runs/T-family/T23G_runs/analyse_t23g.py` is frozen, and its
arithmetic was driven on **synthetic** triples while it was written. **Its
file-reading paths had never met a real case directory.** The first grading run
would have been their first test, arriving at the moment the fine level lands.
This pre-flight exercised those paths early, on copies.

**What was exercised:** the `--pre-solve` limb against real trees; the
`checkMesh` cell-count reader; the cross-level invariant comparison; the three
field readers; six of the nine planted-zero controls; `iterative_state`,
`plateau_state` and `read_yplus`.

**Method, and the constraint it was run under.** `T23G_C` (rc=0, 364 s) and
`T23G_M` (rc=0, 1669 s, ended 04:27:08Z) were both quiescent and were copied with
`cp -a` to a scratch tree outside `verification/runs/`. **Every read and every
write in this exercise went to those copies.** `T23G_F` was live (pid 1106873)
and was **not touched at all**: after the exercise its case-root `atime` still
read `2026-09-01 04:02:15Z`, unchanged from before. `T23G_C` and `T23G_M` were
verified byte-identical to their copies afterward by `diff -rq`, and **no
`DONE.*` or `STATUS.*` marker was created in `T23G_runs/`.**

**`grade()` was deliberately NOT run.** See **D3**: `analyse_t23g.py:607`
hardcodes `HERE` rather than `root`, so `--root <scratch>` does **not** redirect
the completion limb, and running `grade()` would have written `DONE.*` markers
into the live run directory. The readers were therefore driven directly rather
than through `grade()`.

---

## 1. D2 — THE HARD STOP: THE THREE T23G LEVEL NAMES ARE NOT REGISTERED WITH THE COMPLETION DELEGATE

**`mark_done_t23.py:77`:**

```
CASES = ("T23_P305_U10", "T23_P305_U20", "T23_P305_U30", "T23_P305_U40")
```

`T23G_C`, `T23G_M` and `T23G_F` are not in that tuple, and `run()` refuses on any
name outside it. `analyse_t23g.py:597-615` (`require_done`) calls
`mark_done_t23.py` as a subprocess and refuses on any non-zero return.
`require_done` is the **first** thing `grade()` does after `_level_dirs`
(`:829`), so **the grading refuses before a single field is read.**

**MEASURED**, driven against a scratch root so nothing could be touched:

| driven | result |
|---|---|
| `mark_done_t23.py --root <scratch> T23G_C T23G_M T23G_F` | `REFUSE: 'T23G_C' is not a registered T23 case: T23_P305_U10 T23_P305_U20 T23_P305_U30 T23_P305_U40` — **rc=2** |
| **planted control**, same instrument, a name it *does* know: `--root <scratch> T23_P305_U20` | `NOT DONE T23_P305_U20 - no case directory` — **rc=1** |

**The control is the point.** The instrument was shown able to return something
other than the refusal, so **rc=2 is about the name registry and is not a blanket
failure of the instrument** (`CLAUDE.md` rule 3: a refusal from a reader not shown
able to return a non-refusal is not evidence either).

**The refusal is loud and well-behaved:** exit 2, and `analyse_t23g.py:609-611`
echoes `mark_done`'s own `REFUSE:` line to stdout, so the reason is visible to
the operator rather than swallowed. The instrument is doing its job. **The
problem is that the rung cannot be graded until this is ruled on.**

### 1.1 THE NAME REGISTRY IS THE ONLY BLOCKER IN `require_done` — A PROBE, NOT A COMPLETION VERDICT

To find out whether anything *else* in rule 4 would also fail, a **scratch copy**
of `mark_done_t23.py` was taken with the three T23G names appended to `CASES`.
**The frozen original was not edited.** Driven against the scratch tree:

```
NOTE      T23G_C         - rc_source=READ-FROM-STATUS
DONE      T23G_C
NOTE      T23G_M         - rc_source=READ-FROM-STATUS
DONE      T23G_M
                                                          probe rc=0
```

**Both complete levels satisfy all six clauses of rule 4**, with `rc` read from
`STATUS` rather than derived from the log.

> **THIS IS A PROBE OF A MODIFIED COPY AND IS NOT A COMPLETION VERDICT FOR ANY
> LEVEL.** No level of T23G is marked DONE by this document, and nothing here
> may be cited as completion. What the probe establishes is narrower and is only
> this: **within `require_done`, the name registry is the sole blocker.**

**The file that would have to change is `mark_done_t23.py`, not `analyse_t23g.py`.**
That is a different file from the one whose gates are frozen, and it is on the
grading path by `analyse_t23g.py`'s own §7.2 delegation. **Whether it may be
changed is verification's ruling to make.**

---

## 2. D1 — THE DANGEROUS ONE: G-REPRO'S FROZEN REFERENCE AND THE READER IT IS COMPARED AGAINST MEASURE TWO DIFFERENT QUANTITIES

**This defect does not refuse. It produces a wrong verdict**, and the wrong
verdict propagates to the whole rung.

`analyse_t23g.py:150-152`:

```
REPRO_REF_Q1_K = 342.1749743329     # G-REPRO, section 10.  MEASURED from
                                    # T23_P305_U20's own fieldMinMax row 10000.
REPRO_TOL_K = 1.0e-6
```

At `:916` the gate compares that constant against `values["Q1"]["T23G_M"]`, which
comes from `read_max_T` — and `read_max_T:254-259` reads the **`internalField`
only**. The comment at `:150-151` states the reference's provenance honestly:
it was taken from the **`fieldMinMax` function object**, whose max includes
**boundary face values**. **These are two different quantities, and the file
says so on its own face without anyone having noticed the consequence.**

### 2.1 THE THREE NUMBERS, MEASURED SIDE BY SIDE

All three read from `T23G_M`'s own artifacts (via the scratch copy):

| reader | value (K) |
|---|---|
| `read_max_T(T23G_M, "housing")` — `internalField`, 1120 cells | **342.1598289320** |
| the case's own `fieldMinMax.dat`, row 10000, max column | **342.1749743329** |
| max over the **`housing_to_core` boundary patch**, 140 faces | **342.1749743330** |

Artifacts: `verification/runs/T-family/T23G_runs/T23G_M/10000/housing/T` and
`verification/runs/T-family/T23G_runs/T23G_M/postProcessing/housing/housing_T/0/fieldMinMax.dat`.

**Where the reference number comes from is now located, not guessed:** the
hottest place in the `housing` region is the interface with the core, and
`342.1749743330` is the max over that boundary patch. The `fieldMinMax` function
object sees it; `read_max_T` does not, because it reads internal cell values only.

**The gap is 1.5145e-02 K. The gate tolerance is 1.0e-06 K** — the shortfall is
four orders of magnitude past the tolerance. **G-REPRO would read GATE FAIL.**

### 2.2 AND IT CAPS THE ENTIRE RUNG

`analyse_t23g.py:949-952` takes the rung verdict as `min(verdicts)` over Q1, Q2,
Q3 and G-REPRO under `{"NOT A RESULT": 0, "GATE FAIL": 1, "PASS": 2}`. **A GATE
FAIL on G-REPRO holds the whole T23G rung verdict at GATE FAIL regardless of what
the grid triple does.**

### 2.3 THE SENTENCE THAT MATTERS MOST

**`read_max_T(T23_P305_U20, "housing")` gives 342.1598289320 K — identical to
`T23G_M` to every printed digit.**

`T23_P305_U20` was read directly (it is quiescent; nothing under it had been
written in the preceding 30 minutes). **So `T23G_M` does reproduce the
already-solved `T23_P305_U20` exactly. The determinism this gate exists to test
SUCCEEDS, and the gate as written would report it as a failure.** Its own
`fieldMinMax` row 10000 also reads `3.421749743329e+02`, matching the frozen
constant — the two cases agree on *both* readers; they simply do not agree with
*each other's* readers.

### 2.4 THE OPEN QUESTION, STATED WITHOUT A PROPOSED ANSWER

This is **not** a typo'd constant, and it should not be ruled on as one. The
question underneath it is definitional: **whether Q1, "max(T) over the whole
`housing` region", is defined to include the interface faces or only the internal
cells.** The registration's §4 wording and `analyse_t23.py`'s own Q1 definition
both bear on it, and one reading makes the reference right and the reader narrow
while the other makes the reader right and the reference wrong.

**This document does not propose which side is wrong.** Both candidate changes
sit on the grading path of a rung whose compute has run.

---

## 3. D3 — `--root` DOES NOT PROPAGATE TO THE COMPLETION LIMB, AND THE STALENESS CHECK CROSSES TREES

`analyse_t23g.py:607` passes `"--root", HERE` — **hardcoded**, not `root`:

```python
r = subprocess.run([sys.executable, md, "--root", HERE] + list(LEVELS), ...)
```

and `:619` reads `os.path.join(HERE, "DONE.%s" % lvl)`, while `:625` takes field
mtimes from `dirs[lvl]`, which **is** derived from `root`.

Under normal operation `root == HERE` and this is inert. Two consequences when it
is not:

1. **`analyse_t23g.py --root <anywhere>` still writes `DONE.*` markers into the
   live `T23G_runs/`.** This is the reason `grade()` was not run in this
   exercise.
2. With a `--root` copy, the `:625` staleness comparison is between mtimes in
   **two different trees** and would refuse spuriously.

---

## 4. D4 — TWO REFUSAL MESSAGES ARE FACTUALLY WRONG

Both still refuse correctly; only the text misleads. Recorded because a wrong
message on a refusal path costs the next reader time at exactly the wrong moment.

- **`:613-615`** — any non-zero from `mark_done` is reported as *"at least one
  level is NOT DONE on rule 4's six clauses."* Under **D2**, no clause was ever
  evaluated. The `:609-611` stdout echo is the only thing that makes the real
  reason visible.
- **`:485-487`** — the format string carries five specifiers and the final `%r`
  is fed `sub` a second time instead of the other level's file set, so a genuine
  file-set divergence would print `[...] vs 'constant'`.

---

## 5. D5 — `grading_path_shas()` OMITS THE COMPLETION DELEGATE

**This is small in size and large in consequence, because of D2.**

`analyse_t23g.py:989-998` records the sha of three files —
`analyse_t23g.py`, `scripts/roache_triple.py`, `analyse_t23.py` — so that a later
edit to any of them is visible rather than silent. **`mark_done_t23.py` is not
among them**, even though `:11-13` and §7.2 delegate rule-4 completion to it and
it is unambiguously on the grading path.

**D2 means someone is about to edit precisely that file.** As it stands, that
edit **would not appear in the grading path recorded on the artifact's own face.**

Blob shas at the time of writing, for the record (`git hash-object`, HEAD
`dca3e0c10d80386b2b3e036baafa8ab12ec94c3b`):

```
e02878a0a9c40e22b76f8d23fd3e1543eb8035a5  verification/runs/T-family/T23G_runs/analyse_t23g.py
78e56a3bc2c2a07571db1cf3c91f4c2c31f246b8  scripts/roache_triple.py
314a2b82b85cd1c620f26d37c1a2613cf76838d6  verification/runs/T-family/T23_runs/analyse_t23.py
1713323f3e81131d83792e816f32df4eb0c72f19  verification/runs/T-family/T23_runs/mark_done_t23.py   <-- NOT RECORDED BY grading_path_shas()
```

---

## 6. WHAT THE READERS DID ON REAL INPUT — THE POSITIVE RESULT

**No uncaught exception occurred anywhere.** Every reader, planter, control,
invariant comparison and log parser was driven inside an exception guard on real
input and **not one of them crashed.**

- **`cells_from_checkmesh` parses real v2606 logs.** All six real logs (C and M ×
  fluid/core/housing) yielded exactly one `cells:` line and matched the frozen
  `EXPECTED_CELLS`: C `8800/840/280`, M `35200/3360/1120`. **Planted control on
  the reader:** a decoy fine level (a copy of C) made it refuse with the
  *measured* number — `T23G_F region fluid has 8800 cells; the frozen
  registration says 140800` — so the reader measures rather than recites.
- **`check_invariants` passes on real trees.** `0.orig/` 12 files, `constant/` 10
  files, `system/` 8 files byte-identical between C and M, and the
  `blockMeshDict` `vertices` block identical. **The amendment-A1 `cellToRegion`
  exemption is doing exactly the work it claims** — nothing else under
  `constant/` differs across the ladder.
- **Field readers all resolve** at `10000/<region>/T`. Q1 max(T) housing: C
  `343.910055617` K, M `342.159828932` K. Q3 max(T) core: C `348.006105080` K, M
  `346.265640914` K. Q2 areaAvg on `housing_to_fluid`: C `342.070481175` K, M
  `340.334602785` K.
- **`patch_face_areas`** read 70 faces on C and 140 on M with **identical total
  area 4.089317566e-04 m²** — an independent corroboration that the interface
  geometry is preserved across the ladder.
- **All six available planted-zero controls fired on real fields** (3 quantities ×
  the 2 complete levels): every one `passed=True`, floor `1e-06 K`, read at PLANT
  `1.234000e-03 K` exactly, ladder monotone and exact across all nine rungs. Q2
  planted into all 70 (C) / 140 (M) faces and still read a `mag` shift rather than
  `mag/N`, so the T23 §3.6 clause-7 trap is genuinely closed. **The controls work
  on real OpenFOAM field files and not only on synthetic input.**
- **The copy-out discipline holds, verified rather than assumed.** Each field file
  was hashed before and after every control; all six came back **unchanged**.
- **`iterative_state`**: G-CONV CONVERGED on both levels, all six asserted
  residuals ≤ 1e-8. The Ux exclusion is justified by measurement: max|Ux|/max|Uz|
  = `1.668e-17` (C), `1.832e-16` (M).

---

## 7. THE G-PLATEAU ZERO — THE COMPARATOR HAS NO CONTROL FOR IT, SO ONE WAS SUPPLIED

`plateau_state` returned **spread = 0.0 exactly** on both levels and both regions.
`analyse_t23g.py` carries **no planted-zero control for this reader**, and
`CLAUDE.md` rule 3 forbids believing a zero from a reader not shown able to see a
non-zero.

**A control was supplied.** On a scratch copy, the max column of the last
`fieldMinMax` row was perturbed by **+0.5 K**:

| | state | spread |
|---|---|---|
| as-found | `PLATEAUED` | `0.0` |
| after +0.5 K on the last sample | `NOT PLATEAUED` | `0.5` |

**The reader is not blind, and the 0.0 is genuine** — the last 11 samples are
byte-identical because the solve has converged to the file's write precision. The
column indexing was checked against the real tab-separated file at the same time:
`f[4]` is the max column, as the parser assumes.

**Recorded as a gap in a frozen instrument, not as a defect in this run's
numbers.** Whether the control belongs in the file is not proposed here.

---

## 8. `read_yplus` RETURNS `BLIND` — A SCOPE LIMITATION THE RUNG MUST STATE

`read_yplus` returned **`BLIND`** on both complete levels. This is the instrument
**working correctly**, not failing: `log.yPlus.fluid` says

> `Unable to find turbulence model in the database: yPlus will not be calculated`

and then prints `min = 0, max = 0, average = 0` on all four patches. The reader
refuses those zeros rather than reading them — a live false zero, caught.

**The consequence is a scope limitation and belongs on the rung's face:**
**§7.4's wall-treatment disclosure is unavailable for the entire T23G rung.** The
`yPlus` function object ran without the turbulence model in the database, so no
y+ was ever computed for any level. §7.4 never gated on y+, so no verdict moves —
but the rung cannot state whether the three levels share one wall treatment, and
it must say so rather than leave the disclosure silently unprinted.

---

## 9. NO MESH-QUALITY GATE — THE IMMUNITY AND THE GAP HAVE THE SAME CAUSE

The `analyse_t25R.py` regex defects found on 2026-09-01 (a
`"Max non-orthogonality"` pattern against v2606's `"Mesh non-orthogonality Max:"`
wording, and a skewness character class excluding the minus sign, raising an
uncaught `ValueError` on a negative exponent) were checked for here.

**Both are structurally absent, and so is the check they belong to.**
`analyse_t23g.py` parses exactly one thing out of `checkMesh` — `^\s*cells:\s+(\d+)\s*$`
at `:391` — and there is **no** non-orthogonality, skewness, aspect-ratio or
determinant regex anywhere on the grading path (`analyse_t23g.py`,
`analyse_t23.py`, `scripts/roache_triple.py`; grep clean). No wording mismatch is
possible and no character class can meet a negative exponent, **because no float
is parsed from a mesh-quality line at all.** The real v2606 log writes
`    cells:            1120` and the regex matches it.

**Both halves are stated deliberately: this comparator is immune to that defect
family precisely because it applies no mesh-quality gate whatsoever.** That is a
scope observation about T23G, not a defect in the instrument, and it is recorded
so it is not later mistaken for a check that was passed.

---

## 10. WHAT WAS NOT VERIFIED

Stated plainly, because an honest gap is worth more than a confident guess.

- **`T23G_F` was not exercised in any way.** Nothing under it was read — not one
  file, not even its static `log.checkMesh.*`. Its cell counts (140800 / 13440 /
  4480), its invariant files and its field readability are **entirely untested.**
- **The three-level limbs have only been driven on a pair plus a decoy.**
  `check_ladder_structure`'s ratio arithmetic and `check_invariants` were
  exercised on the genuine C↔M comparison; the fine level's arm is untested.
- **`roache_triple`'s grading arithmetic has never met three real values.**
  `grade_quantity`, `all_triples` and `grade_ladder` were not called. **The dT
  shift-invariance assertion at `:669-682` remains synthetic-only.**
- **The §1.1 probe is a probe**, run against a modified scratch copy of the
  completion instrument. It is not a completion verdict for any level.
- **No verdict on T23G is stated or implied anywhere in this document.**

---

## 11. THE ABSENCE, MEASURED AND NAMED — THE §2d.3.3 STANDARD

Both defects sit on the grading path of a rung whose **compute has run**, so
`CLAUDE.md` rule 2 and `VERIFICATION_CHARTER.md` **§2d.2** have closed the gates,
and any repair needs the **§2d.1** exception. **§2d.3.3** holds that conditions
(3) and (4) — *quantify what moved*, *record the pre-repair values* — may be
satisfied **by disclosing an absence, but only where the absence is MEASURED AND
NAMED, never asserted**, and only while the count of graded solves is zero. That
standard is met here and the measurement is recorded so verification can rule
without re-deriving it.

**GRADED SOLVES UNDER THE T23G REGISTRATION: ZERO.** No level has been graded,
and by **D2** none can be until this is ruled on.

**Artifacts that do not exist**, checked both on disk and at `HEAD`
(`dca3e0c10d80386b2b3e036baafa8ab12ec94c3b`):

| artifact | on disk | at HEAD |
|---|---|---|
| `verification/runs/T-family/T23G_runs/DONE.T23G_C` | ABSENT | NOT AT HEAD |
| `verification/runs/T-family/T23G_runs/DONE.T23G_M` | ABSENT | NOT AT HEAD |
| `verification/runs/T-family/T23G_runs/DONE.T23G_F` | ABSENT | NOT AT HEAD |
| `verification/runs/T-family/T23G_runs/T23G_GRADED.json` | ABSENT | NOT AT HEAD |
| `docs/campaigns/T-family/T23G_RESULTS.md` | ABSENT | NOT AT HEAD |

A `find` over the repository for `T23G*` outside the three case directories
returns only `docs/campaigns/T-family/T23G_PREREGISTRATION.md` and the run
directory itself. **No T23G result, json or grading record exists anywhere.**

**This measurement is offered as evidence for a ruling. It is not a claim that a
repair is legal, and no repair is proposed.**

---

## 12. WHAT THIS DOCUMENT DOES NOT DO

- It **does not repair** `analyse_t23g.py` or `mark_done_t23.py`. Neither file
  was edited. The `§1.1` probe used a scratch copy.
- It **does not propose which repair to take** for D1 or D2, and takes no
  position on the Q1 definitional question in §2.4.
- It **is not a retroactive amendment** to `T23G_PREREGISTRATION.md`, and no
  gate, threshold, band, cap or label is moved by it.
- It **states no verdict** on the T23G rung or on any level.
- **The ruling is verification's.** The precedent is T20's §2d.1 referral,
  granted at **§2d.3**, on the same shape: a defect found by an instrument that
  grades nothing, before any graded solve. **§2d.3.5** is noted as well — a
  §2d.1 grant removes a legal obstacle and **is not a budget, not a launch order
  and not a verdict.**

---

## 13. COST

**Approximately 6 core-minutes, single-rank Python.** **ESTIMATED FROM WALL
CLOCK, NOT READ FROM A SOLVER LOG**, and therefore not a measured figure in the
sense rule 12 requires of a run.

**No solver compute was consumed by this exercise.** The pre-registered T23G
compute budget is untouched, and `T23G_F` ran throughout without interference.

---

*Pre-flight performed 2026-09-01 by a heat-transfer lane on scratch copies at
`/tmp/.../scratchpad/t23g_preflight` (temporary; deliberately not cited as
evidence — L-186 forbids a repository document resting on a scratch path). Every
number above is re-derivable from the artifacts named beside it under
`verification/runs/T-family/T23G_runs/` and `verification/runs/T-family/T23_runs/`.*
