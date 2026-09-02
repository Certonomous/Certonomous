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
