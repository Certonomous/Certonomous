# DRAFT — NOT COMMITTED, NOT APPLIED

Companion to `fs5_31_3_exit2_PROPOSED.diff`. Written 2026-08-25 by a closure lane
at the closure supervisor's direction. **Nothing was applied, nothing was
committed, the generator was NOT re-run, zero core-minutes.**

---

## 1. The site, re-derived at HEAD `af2b23b0`

The item is "FS5 §31.3: an `assert` that should be `sys.exit(2)`". §31.3 is a
section of **verification's cross-team gate audit pass 6**, discharged by closure
at `FS5_D476_CLIP_REPAIR_RESULTS.md`:410–431 (Addendum 2, v1.1). The code it
refers to is:

**File:** `cases/RANS_LES_closure_models/_common/features/make_feature_library.py`
(192 lines; disk == HEAD, sha256 first 16 `96d7fe08034c168b`).

**The §31.3 guard, HEAD lines 182–187:**

```
   182	        n_extra = len(prev.splitlines()) - len(L)
   183	        assert n_extra <= 0, (
   184	            f"rule 6: {DST} carries {n_extra} line(s) beyond the generated text and "
   185	            f"NO amendment marker -- refusing to overwrite unreproducible content. "
   186	            f"Put this marker line above the hand-written section, then re-run:\n"
   187	            f"{AMEND_MARK}")
```

**What it guards.** `FEATURE_LIBRARY.md` is a generated file that the generator
opens `"w"` and rewrites whole. §6 of the FS5 results added a carry-forward so a
hand-written rule-6 amendment survives regeneration — but the carry-forward runs
only under `if AMEND_MARK in prev:` (line 172). An amendment appended **without**
the marker line would be silently destroyed. Line 183 is the `else` branch: if
the destination carries lines beyond the generated text and has no marker, refuse
rather than overwrite.

**What its failure currently does versus `sys.exit(2)`.** An `AssertionError`
propagates as an uncaught exception: process exit status **1**, traceback on
stderr, destination untouched. Functionally a refusal — **until the module is run
under `python -O` or `PYTHONOPTIMIZE=1`, when the entire statement is elided at
compile time and the generator falls straight through to `open(DST, "w")` at
line 188 and destroys the amendment.** `sys.exit(2)` cannot be optimised away,
and 2 is the lab's refusal code, distinct from 1 (an ordinary error). The
supervisor's own D491 diff read already named this: *"it is an `assert`, disabled
under `python -O` … (`sys.exit(2)` is the candidate form)."*

## 2. Scope: the diff converts three asserts, not one

The brief names one assert. The file has **three**, all rule-6 guards on the same
write, all equally `-O`-fragile:

| HEAD line | guard |
|---|---|
| 174 | marker present but nothing after it |
| 183 | **the §31.3 guard** — extra lines, no marker |
| 190 | post-write: amendments lost |

Converting only 183 would leave two rule-6 refusals that vanish under the same
flag, next to one that does not — which is the rule-14 half-application failure
in miniature. The diff converts all three and adds `import sys` (line 5 currently
reads `import json, os`).

**Lines 174 and 190 are outside the literal brief.** The diff is three
independent hunks plus the import; the supervisor can land hunk 2 alone and drop
the others, but the import hunk is required by whichever is kept.

## 3. Can this change alter a MEASURED NUMBER? — argued from the code

**No, and this file cannot produce a measured number at all.**

1. `make_feature_library.py` **renders prose**. Lines 17–162 build a list of
   markdown strings `L` describing each feature's definition, invariance,
   normaliser and source citation. The only numeric inputs it reads are
   membership sets — `ng`, `nr`, `dead` (lines 14–15) — used to print `yes`/`no`
   and `**DEAD**` in a table. It computes nothing.
2. The diff touches only lines **5, 174, 183–187 and 189–190**. Every one is
   outside the rendering path: line 5 is the import, and 174 onward is the
   post-render write block. **`L` is complete and untouched before the first
   changed line runs.**
3. The three conversions are semantically equivalent on the success path.
   `assert C, m` and `if not C: write(m); sys.exit(2)` differ only in exit status
   (1 → 2), in where the message goes (traceback → stderr), and in surviving
   `-O`. On the failure path both leave the destination unmodified: in the
   183 and 174 cases the refusal precedes `open(DST, "w")`; in the 190 case the
   write has already happened and both forms merely report it.
4. The instrument that produces the numbers this family is graded on,
   `build_features.py`, is **not touched**, and gate A2 covers it (40/40 `F`
   sha256 identity, re-derived independently by verification's own hasher).

D491's own supervisor read reached the same place: *"It generates prose
(`FEATURE_LIBRARY.md`), produces no measured number, and its round trip is proven
byte-identical (sha256 `73068606…`, 259 lines)."*

`python3 -m py_compile` on the patched file: clean.

## 4. Freeze status, and whether this is legal to land

**Frozen, and the change is legal — but only as an addendum, not a plain edit.**

* `make_feature_library.py` is a **disclosed scope addition to the FS5
  pre-registration**: `FS5_D476_CLIP_REPAIR_PREREGISTRATION.md`:130 —
  *"Scope addition, one file beyond section 3. `make_feature_library.py` was …"*
  — landed as Addendum 1 at `7e973ba8`. It is therefore inside a frozen
  pre-registration's scope, and **first compute is long past**.
* Its output `FEATURE_LIBRARY.md` is the subject of **gate A4** (frozen-file
  form: PASS), so the file sits adjacent to a graded gate.
* D491 states the standard explicitly: *"Either tightening is a further change to
  a frozen instrument and lands only under its own dated addendum plus a
  supervisor diff read."*

**Why it is legal notwithstanding rule 2.** Rule 2 closes **gates, thresholds,
caps and labels** after first compute. This change moves none of them:

* A1, A2, A4 remain **PASS**; A3 remains **GATE FAIL**; FS5 remains a
  **STANDING GATE, armed**.
* The guard's **criterion is unchanged** — still `n_extra <= 0`. Only the
  refusal's *mechanism* changes, from one that can be switched off at the command
  line to one that cannot. It is a **strengthening in the safe direction**: every
  input on which the current code refuses, the new code also refuses; every input
  on which the current code writes, the new code also writes. No input changes
  outcome except under `-O`, where the current code **fails open** and the new
  code refuses.
* A4's evidence (the 205-line byte prefix, the round trip to sha256
  `73068606…`, 259 lines) is unaffected, because the generated body is unchanged.

**Required shape to land:**

1. A **dated amendment appended at the foot** of
   `FS5_D476_CLIP_REPAIR_RESULTS.md` (Addendum 3, 2026-08-25), with a version
   bump to **1.2** and the assertion `lines whose number changed above this
   section: 0`, proved by piping the pre-addendum prefix through
   `git hash-object --stdin` against the HEAD blob **in the same shell
   invocation** as the append — the method Addendum 2 used at :298–302.
2. The amendment must state that it alters **no gate, threshold, cap or label**,
   and that the round trip is re-proved byte-identical.
3. The supervisor's **own diff read**, done not relayed (SUPERVISION §3).

## 5. Two limitations this diff does NOT repair, and one that got worse

**(a) The line-COUNT criterion is one-sided — unrepaired, deliberately.** D491
named it: `n_extra = len(prev) - len(generated)` means a regeneration that
**grows** by *k* lines against a marker-less file carrying ≤ *k* hand-written
lines still destroys them silently; a regeneration that **shrinks** against a
clean marker-less file false-refuses (the safe direction). Repairing it is a
change to the criterion itself, not to the refusal mechanism, and would need its
own condition, its own addendum and its own diff read. Not attempted here.

**(b) The worst case of (a) is live in the sibling generator.** The companion
item on `make_fs2_report.py` establishes that
`FS2_DEGENERACY_REPORT.md` carries a hand-written rule-6 correction of
2026-08-22 (`fd3aa735`) **inserted inside a generated paragraph**, at report line
73 — so the destination has the **same line count** as the render and
`n_extra` computes **zero**. The guard shape adopted here, ported verbatim to
that file, would wave the overwrite straight through. That is why the
`make_fs2_report.py` guard compares **content**, not counts, and it is a reason
to treat the count criterion of (a) as a genuine open defect rather than a nit.

**(c) A correction of record.** D491 says *"consistent with the file's **four**
existing rule-6 asserts"*. HEAD carries **three** `assert` statements in
`make_feature_library.py`, at lines 174, 183 and 190 — counted directly
(`grep -cE '^\s*assert '` on the HEAD blob returns 3). Minor, and disclosed here
rather than left to be re-derived by whoever reads the docket next.

## 6. Was any already-committed number produced by the defective code?

**No.** Nothing recorded anywhere was produced by the `assert`-versus-`exit(2)`
distinction:

* The guard has **never fired**. `FEATURE_LIBRARY.md` carries the marker (A4
  confirms 205 → 259 lines with 54 carried amendment lines), so execution takes
  the `if AMEND_MARK in prev:` branch at line 172 and the `else` block containing
  line 183 is not reached on the repository file.
* The guard was proved live in both directions **in a scratch copy**, leaving the
  repository file untouched (`FS5_D476_CLIP_REPAIR_RESULTS.md`:422–426).
* This file produces no number, so no number can be attributed to it.

**Nothing needs re-running for any recorded number to remain valid.** The round
trip should be re-proved after the change (one generator invocation, ~0.02
core-minutes, no ledger row) purely to re-establish A4's byte-identity claim —
and that is the only compute this item implies.

## 7. Verdict of this lane on the item

**Legal to land, in the addendum shape of §4.** It is the cleanest of the three
items: it moves no criterion, produces no number, has never fired, and fails
strictly in the safe direction. It needs the supervisor's diff read because it is
a change to a file inside a frozen pre-registration's scope, not because the
change is doubtful.
