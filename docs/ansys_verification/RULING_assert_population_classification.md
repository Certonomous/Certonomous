# RULING — the twelve `assert verdict in VERDICTS` sites are NOT one population, and my own repair order named the two that needed it LEAST

**Ruled 2026-08-26T03:0xZ by `ansys-verification-supervisor` personally.** This is
`SUPERVISION_CHARTER` §3 check 1 — a measurement-script question, read by me as code, not
relayed. It corrects an order I gave.

---

## 1. THE ORDER I GAVE, AND WHY IT WAS WRONG

I ordered, before grading, the repair of two comparators carrying Amendment 6's forbidden
`assert`:

    cases/ansys_verification/VMFL021/R2/grade_vmfl021_r2.py:467
    cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py:333

An `ansys-lane-opus` corrected the **population** at `3d2b94df`: enumerated from HEAD there
are **twelve**, not two, and it declined to touch any of them. That correction was right and
its restraint was right.

**But neither I nor that lane asked the question that decides the item: WHAT DOES THE ASSERT
PROTECT?** The lane described the line as *"rule 1's verdict-vocabulary guard, the single
enforcement point for the fixed vocabulary."* **Measured, that description is false for nine
of the twelve.**

## 2. THE MEASUREMENT

An AST classifier over all twelve blobs **at HEAD**, asking of each: is every assignment to
`verdict` a string literal drawn from the fixed vocabulary, or is any of them computed?

**Planted control (rule 3):** the classifier was first handed a constructed source containing
both a computed assignment and a literal one, and **recovered both plus the assert**. The
reader is shown able to see a non-zero, so its zeros are evidence.

| classification | count | meaning |
|---|---|---|
| **TAUTOLOGY** | **9** | every path assigns a vocabulary **string literal**; the assert tests a literal against the tuple it was copied from and **cannot fire** |
| **LIVE GUARD** | **3** | `verdict` is initialised to `None` and filled by a rule-5 branch chain; the assert is the **sole catcher of a fall-through that leaves it `None`** |

**The three live ones:**

| file | line of the `None` initialiser | register row today |
|---|---|---|
| `cases/ansys_verification/VMFL045/grade_vmfl045.py` | 762 | `NOT A RESULT` |
| `cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py` | 762 | **`PASS` — a live credential** |
| `cases/ansys_verification/VMFL051/grade_vmfl051.py` | 729 | `NOT A RESULT` |

**Both files I named are in the nine.** `grade_vmfl021_r2.py` assigns `"NOT A RESULT"` three
times and `"GATE REACHED" if gate_ok else "GATE FAIL"` once; `grade_vmfl017_r2.py` has exactly
one assignment, a ternary over two literals. Under `python3 -O` the assert vanishes **and the
verdict is unchanged, because it was never computed.**

## 3. WHAT MY ORDER WOULD HAVE COST

Both named files are **frozen grading paths**. Editing them changes the blob, breaks the sha
match against the pre-registration commit, and raises the one question a verification lab must
never face — *which version graded this?* **I ruled against exactly that on VMFL010 twelve
hours earlier**, on exactly this reasoning, and then ordered it anyway on a different case.

**The failure is not the miscount. It is that I matched a PATTERN and called it a HAZARD
without reading what the pattern guarded.** A grep hit is a location, not a finding.

## 4. THE RULING

1. **NO FROZEN COMPARATOR IS EDITED FOR THIS.** The nine tautologies are not defects; the
   three live guards are **LATENT, not live** — measured in this territory: the only
   `python3 -O` strings under `cases/ansys_verification/` are records *about* the exposure,
   `PYTHONOPTIMIZE` is unset, and `__debug__` is `True` in the grading interpreter. This
   matches the chief's 22:48Z lab-wide bound.
2. **NO SETTLED VERDICT IS REOPENED**, including `VMFL045-R2`'s `PASS`. It was graded with
   the guard live. Reopening it would be the meta-work Sanaa capped, on a hazard measured
   unrealised.
3. **THE REMEDY IS FORWARD.** Amendment 6/6a binds **new** comparators: no `assert` carries a
   refusal, guard, control or gate; no unconditional success `print` after a check; and every
   new comparator ships a mutation test driven under **both** `python3` and `python3 -O`.
4. **AMENDMENT 6 IS SHARPENED, PROSPECTIVELY.** The defect class is not the `assert` keyword.
   It is **a verdict variable that can reach a record without a branch having set it.** A new
   comparator initialises `verdict` to no value at all, or ends its chain in an `else` that
   assigns one; a `None` initialiser plus a chain of `if`s is the shape to refuse.

## 5. WHAT I COULD NOT VERIFY

Whether the `None` fall-through in the three live files is **reachable** — that needs the
branch chain traced to its end, not just its head. It changes nothing above: an unreachable
fall-through makes those three tautologies too, which only strengthens the ruling. It is
recorded as unmeasured rather than assumed either way.
