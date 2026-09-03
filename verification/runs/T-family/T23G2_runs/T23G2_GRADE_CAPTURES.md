# T23G2 — THE TWO GRADING CAPTURES, LABELLED AS CAPTURES

**Written 2026-09-02 by a `heat-transfer` lane.** This file labels two stdout
captures of the T23G2 comparator so neither can be mistaken for the other, and so
neither can be mistaken for a re-grade. **Nothing here grades anything. No solver
was launched to produce either capture: both are reads of artifacts already on
disk, 0 core-min, $0.00.**

Required by `VERIFICATION_CHARTER.md` v1.41 §2d.9.1 conditions (3) and (4)
(commit `79bcfd83`), which grant repair `R7` on the condition that **the
pre-repair `G-ORDER` cell is published beside the post-repair cell.**

---

## THE TWO CAPTURES

| | file | sha256 | comparator blob that produced it |
|---|---|---|---|
| **PRE-REPAIR CAPTURE** | `T23G2_GRADE.out` | `40f2fa33f4818cad7834e86257cd9dac8c6b786f24662c87bb0ffe2927261d2b` | `fa4e802f9e0eab63e8d4902e1d74e99f11748a8f` |
| **POST-REPAIR CAPTURE** | `T23G2_GRADE_POST_R7.out` | `dc79492b765a5c7a473119a47ec1364303a7cce420ff42098e6a395adfecc99a` | `d2187518bc3b257d6305db7ac4a4f3c06b746f39` |

**Both are captures of stdout, not records.** `T23G2_GRADE.out` was itself
declared as a byte-identical copy of the 2026-09-02 grading stdout
(`T23G2_R7_ORDER_GATE_PETITION.md` §1.1), placed under the run directory because
the original lived only in a session scratchpad, which `CLAUDE.md` rule 13 forbids
a repository document to cite. **`T23G2_GRADE.out` is not edited by `R7` and was
not edited by this lane** — its sha256 above is the same value the petition
recorded before the repair existed.

---

## THE REPRODUCTION CONTROL, RUN BEFORE THE REPAIR WAS MADE

Before `gate_order` was touched, the unrepaired comparator was re-run over
`verification/runs/T-family/T23G2_runs` and its stdout **diffed against
`T23G2_GRADE.out`**. The diff was **empty — byte-identical** `[MEASURED]`.

**That control is what makes the pre-versus-post diff below mean anything.**
Without it, a difference between the two captures could have come from the run
tree changing under us rather than from the repair. It did not: the same tree, the
same comparator blob, reproduces the retained capture exactly.

---

## WHAT MOVED BETWEEN THEM — TWO HUNKS, ELEVEN LINES, AND NOTHING ELSE

`diff -u T23G2_GRADE.out T23G2_GRADE_POST_R7.out` returns **exactly two hunks**
`[MEASURED]`.

### HUNK 1 — capture line 13. **The comparator's own blob sha. One line.**

```
-      post-repair (working tree) : fa4e802f9e0eab63e8d4902e1d74e99f11748a8f
+      post-repair (working tree) : d2187518bc3b257d6305db7ac4a4f3c06b746f39
```

**This is the `R2` grading-path recorder printing the fingerprint of the file it
is running inside.** Editing `analyse_t23g2.py` changes its blob; the recorder
exists to print that blob. **Its movement is entailed by the repair, and its
NON-movement would have been the finding** — a recorder blind to an edit of its
own file would be worthless. It carries no verdict, no value, no gate, no band,
and no threshold. The `pre-registration (frozen)` column beside it is
**unchanged** at `cc723d6f65245674f7d80c51de55fe986549477a`, and still reads
`DIFFERS`, exactly as it did before `R7`.

### HUNK 2 — capture lines 160–162. **The `G-ORDER` cell. This is the repair.**

```
 G-ORDER -- A1.2 at T23G2_PREREGISTRATION.md:834, on Q4, band (0.5, 1.5)
-  p(Q4) = 0.6111, band [0.5, 1.5], finest triple CONVERGING
-  G-ORDER: PASS
+  REPAIR R7 (VERIFICATION_CHARTER.md section 2d.9.1): levels T23G2_L2 are not iteratively
+  converged or not plateaued, so rule 5 step (a) has ALREADY VOIDED the grid claim
+  this gate would otherwise grade.  There is NO ORDER CLAIM to gate.
+  The observed order is 0.6111 and the finest triple reads CONVERGING.  BOTH ARE PRINTED because
+  they are exactly what an unlicensed gate would have graded, and NEITHER licenses
+  anything: the band [0.5, 1.5] on Q4 is untouched and remains registered.
+  G-ORDER: NOT A RESULT
```

**PRE-REPAIR CELL: `G-ORDER: PASS`. POST-REPAIR CELL: `G-ORDER: NOT A RESULT`.**

**No number moved.** p(`Q4`) is **0.6111** in both captures and is printed in
both. The band is **[0.5, 1.5]** in both and is printed in both. The finest triple
reads **CONVERGING** in both. **What changed is the verdict drawn from them, and
the direction is the only one `CLAUDE.md` rule 5 permits: `PASS` → `NOT A
RESULT`.**

### AND THE RUNG VERDICT DID NOT MOVE

```
 RUNG VERDICT: NOT A RESULT
```

**Unchanged, in both captures, and the process exit code is `3` in both**
`[MEASURED]`. The rollup already carried `NOT A RESULT` from three independent
grounds — `G-CONV` `GATE FAIL`, `G-YPLUS` `GATE FAIL`, and five rows voided at
rule 5 step (a) — every one of them established before any repair existed.
**`R7` moves a CELL and not the rung**, which is the distinction §2d.9.1 requires
the record to state rather than leave a reader to infer.

### ⚠ DISCLOSED AGAINST THE STRICTEST READING OF THE CONDITION

The discharge was briefed as a diff differing **only** in the `G-ORDER` lines.
**Hunk 1 is not a `G-ORDER` line, and it moved.** It is disclosed here at the same
prominence as hunk 2 rather than described away: it is one self-referential
provenance line, it was **predicted in writing before the post-repair re-run was
executed**, and no third line moved. A reader who holds the condition literally
should read this discharge as **two hunks, one of them mechanical**, and not as
one.

---

## THE GATE CONTROL — `T23G2_R7_GATE_CONTROL.out`

**`CLAUDE.md` rule 3's principle applied to a verdict rather than to a zero: a
`NOT A RESULT` emitted by a gate never shown able to emit a `PASS` is not
evidence — it is indistinguishable from a gate hard-wired to refuse.**

`r7_gate_control_t23g2.py` drives the **production** `gate_order` — the function
the comparator actually calls, not a copy of it, per `VERIFICATION_CHARTER.md`
§2p.7 limb (d), *"a test that exercises a redundant copy of the guarded logic
tests nothing"* — over five inputs and requires five different answers.

| control | input | required | measured |
|---|---|---|---|
| 1 | as measured: `T23G2_L2` `NOT CONVERGED` | `NOT A RESULT` | `NOT A RESULT` |
| 2 | **PLANT** — same order, every level `CONVERGED`/`PLATEAUED` | **`PASS`** | **`PASS`** |
| 3 | **PLANT** — converged, order `2.9000` outside `[0.5, 1.5]` | **`GATE FAIL`** | **`GATE FAIL`** |
| 4 | plateau limb alone — `T23G2_L3` `NOT PLATEAUED` | `NOT A RESULT` | `NOT A RESULT` |
| 5 | iterative states absent | refusal | refusal |

**5 of 5 passed** `[MEASURED]`, exit code 0.

**Control 2 is the one that matters**: it shows the repaired gate still emits
`PASS` when the precondition holds, so the `NOT A RESULT` in control 1 is a
reading of the data and not a property of the code. **Control 3 shows the
registered band `[0.5, 1.5]` is still live and still discriminating** — `R7` did
not widen it, narrow it or retire it. Control 4 exercises the plateau limb
independently, which the T23G2 data alone never reaches. Control 5 mirrors
`roache_triple.grade_ladder:609-612`.

**This control grades nothing.** It opens no case, reads no field, and writes no
verdict into any record.

---

## COST — RULE 12

**Solver compute: 0 core-min. $0.00.** No mesh was built, no field was written,
no case directory was modified. Three comparator invocations and one control
invocation, all reads of artifacts already on disk; each completes in under a
second of single-rank wall time, which rounds to **0.0 core-min** at the lab's
unit. `cost_basis = NOT APPLICABLE — no solver compute was incurred.`

**Gates, thresholds, bands, caps, labels created, moved or retired: 0 · 0 · 0 ·
0 · 0. Nothing was re-graded: the rung verdict is `NOT A RESULT` before `R7` and
`NOT A RESULT` after it.**

---

# ⚠ SECTION 2 — **THE `R8` CAPTURES**, ADDED 2026-09-03

**Appended, not rewritten: lines whose number changed above this section: 0.**
Everything above concerns `R7` and is unchanged. **Nothing here grades anything
and no solver was launched to produce any capture below: every one is a read of
artifacts already on disk. 0 core-min, $0.00, `cost_basis = NOT APPLICABLE — no
solver compute was incurred.`**

`analyse_t23g2.py`'s `R8` amendment record defers three figures to this file,
because a figure that counts the lines of the paragraph stating it cannot be
written into that paragraph without falsifying itself. **They are recorded here.**

## THE SHIPPED `R8` COMPARATOR

| | value `[MEASURED]` |
|---|---|
| git blob | `72357dad2bfb39ca74b78ad253cdbca1545d6534` |
| sha256 | `ba7d54b9678219365592581ca3fd13115514e798c463b7934f6278d52393a095` |
| file length | **1613 lines** (pre-`R8` `d2187518…`: 1329; frozen `cc723d6f…`: 653) |
| in-file `R8` amendment record | **161 lines**, a pure comment append below the `__main__` guard, 0 deletions |
| executable repair | **130 inserted, 7 deleted**, net **123**, all inside `g_ratio` and its single call site |

**Both figures close arithmetically against the file lengths** — `1329 − 7 + 291 =
1613` `[MEASURED, difflib]`. The `__main__` guard sat at line **1179** before `R8`
and sits at **1302** after it, moved by the 123 net executable lines above it and
by nothing else. `RATIO_MIN = 10.0` is at line **106** before and after.

## THE FOUR `R8` CAPTURES

| | file | sha256 | comparator blob that produced it |
|---|---|---|---|
| **PRE-REPAIR** | `T23G2_GRADE_PRE_R8.out` | `39f4fce40686f53b337ea1d34f8140d50a073868f7c9d959bc70d7812f163e34` | `d2187518bc3b257d6305db7ac4a4f3c06b746f39` |
| ⚠ **INTERMEDIATE — NOT THE SHIPPED BLOB** | `T23G2_GRADE_POST_R8.out` | `586027bd4a795afef1a969001ad0fd362a23656f0b1b8bbb81526cd89e271bad` | `83bd7550d518269d8702e6e4d42ef8e6fafd27ce` — **in no commit; unresolvable from git** |
| **POST-REPAIR, THE SHIPPED BLOB** | `T23G2_GRADE_POST_R8_RECERT.out` | `39af85a626177fd2eeedd6cc14da90349e0087bdda919b55d6a741d3fef11c4e` | `72357dad2bfb39ca74b78ad253cdbca1545d6534` |
| the diff that discharges §2d.4.1 (3)+(4) | `T23G2_PRE_vs_POST_R8_RECERT.diff` | `14a865eb6a593f7cabf585ff6451f670065319fb37774a7ce1d15afd1c1f7d9d` | — |

**WHY THERE ARE TWO POST-REPAIR CAPTURES, STATED RATHER THAN TIDIED AWAY.**
`T23G2_GRADE_POST_R8.out` was taken at 23:35Z; the comparator was edited again at
23:38Z to finish its in-file amendment record, which changed its blob. **A capture
is evidence only of the blob that produced it**, so the 23:35Z capture is retained
and **labelled an intermediate**, and the shipped blob was re-captured. The two
differ in **exactly one line — the `R2` recorder's own fingerprint — and in
nothing else** `[MEASURED]`. No gate line, no value, no verdict and no exit code
differs between them.

## WHAT MOVED, PRE-`R8` → SHIPPED POST-`R8`

`diff -u` returns **exactly two hunks** `[MEASURED]`, at capture lines 13 and
95–118.

- **Line 13** — the `R2` recorder printing its own file's blob, `d2187518` →
  `72357dad`. Carries no verdict, no value, no gate, no band and no threshold.
  **Its NON-movement would have been the finding.** The `pre-registration
  (frozen)` column beside it is unchanged at `cc723d6f…` and still reads `DIFFERS`.
- **Lines 95–118** — the six `G-RATIO` per-quantity cells, `PASS` →
  `NOT A RESULT`, and the summary cell `G-RATIO: PASS` → `G-RATIO: NOT A RESULT`,
  plus the block naming both ruled grounds. **NO NUMBER MOVED**: the finest
  iterative change is `0.000000e+00` on all six in both, the six smallest
  inter-level differences are identical in both, the printed ratio is `inf` in
  both, and `needs >= 10` is printed in both.

**`G-PLATEAU` is unchanged at `PASS`. `RUNG VERDICT: NOT A RESULT` is unchanged
and the exit code is `3` in both.** **`R8` moves a CELL, not the rung.**

## THE CONTROLS

| | file | sha256 | result `[MEASURED]` |
|---|---|---|---|
| §2p.3(e) positive control, driving production `g_ratio` **by import** | `T23G2_R8_GATE_CONTROL_RECERT.out` | `9dc8642e1e8d5c814b6c2948667e3316b3abaf48d0de7fff6f457a73a704ea98` | **9 / 9**, exit 0 |
| §2p.7 limb (d) mutation demonstration | `T23G2_R8_MUTATION_DEMO_RECERT.out` | `2a8ff4e501ab20996e264ee3f3d4b85884eb6b0a3ffdd25139ea9d362cc07ee6` | **6 / 6 killed**, `M0` green, production sha unchanged, exit 0 |

**Control 2 returns `PASS` and control 3 returns `GATE FAIL` over the SAME
numerator**, so the only thing separating them is `RATIO_MIN = 10.0` — which is
what shows the registered threshold is still live and still discriminating after a
repair that did not touch it. A gate that refused everything would fail both.

**INDEPENDENTLY RE-RUN ON 2026-09-03 BY THE LANDING LANE**, from a cleared
`__pycache__` in `docs/campaigns/T-family`, `scripts/` and this directory: the
comparator re-run is **byte-identical** to `T23G2_GRADE_POST_R8_RECERT.out`, the
gate control returned **9 / 9** and the mutation demonstration **6 / 6**. The
`_RECERT` captures above are that lane's, less the trailing `EXIT_CODE=` line the
capturing shell appends.

## THE ONE FIGURE CORRECTED AFTER THE `R8` RECORD WAS DRAFTED

`ADDENDUM A3` (`b1d9070c`) inserted **111 lines, 0 deleted** into
`T23G2_PREREGISTRATION.md` `[MEASURED: git diff --numstat 976776f4..HEAD; the file
length closes, 1201 + 111 = 1312]`. **`112`, which appears in
`analyse_t23g2.py`'s `R8` amendment record and in `T23G2_R8_PREDICTION.md` §2.2,
is what `git diff | grep -c '^+'` returns: it counts the `+++` header line.**
Neither of those two texts may be edited — the first because editing it changes the
shipped blob and invalidates every capture above, the second because it is a
committed prediction and is struck, never rewritten. **Both are superseded by this
paragraph.** `T23G2_RESULTS.md` §18.12 carries the same correction.
