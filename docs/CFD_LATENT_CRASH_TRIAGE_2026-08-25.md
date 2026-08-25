# CFD — TRIAGE OF THE TWO ARMED LATENT-CRASH FILES, AND A DEFECT IN THE INSTRUMENT THAT FOUND THEM

**Written by the cfd supervisor personally, 2026-08-25.** Crash triage is a
`SUPERVISION_CHARTER.md` §3 check 2 and may not be delegated; the instrument read below is a
§3 check 1 and was done as a read of the code, not as a relay of a lane's test.
`[lab-attributed]` under Sanaa's desk-item disposal rule of this date. **Overrulable.**

**Scope discipline.** This triages **two ARMED, NOT FIRED** files. It **re-audits nothing that
has been graded**. The F6b and F9 records on disk are not reopened, not re-audited and not
called into question — an armed latent crash is not evidence that anything already graded is
wrong. That boundary is the capped meta-work boundary and it is respected here.

Origin: `docs/CFD_GRADER_SELF_BLINDNESS_SWEEP_2026-08-25.md` (commit `b12e8806`), ERROR
findings 3 and 4, both explicitly recorded there as **"Not triaged by this lane."** This is
that triage.

---

## THE DECISIVE QUESTION NEITHER THE SWEEP NOR EITHER BLOCKER ASKED

Both blockers assert a `KeyError` on a divergent-schema read. **Neither established that the
short branch is REACHABLE at the read.** A subscript that sits behind `if "k" in d`, behind
`d.get(k)`, or inside `try/except KeyError` is not an armed crash — it is a correctly
defensive read. Reachability is the whole question, and it is answerable statically in
minutes.

**Answered, it splits the two findings apart.**

---

## 1. F9 `f9_criteria.py` — **FALSE POSITIVE. THE BLOCKER IS LIFTED.**

The sweep reported `status` read **unconditionally** at L816 and L826. **It is not read
unconditionally. It is read behind an explicit membership guard, at both sites:**

```
815:        if "status" in rec:
825:        if "status" in rec:
```

and in both cases the body is `print(...rec['status']...)` followed by `continue`. That is
precisely the defensive shape the short branch requires: the branch writes
`{"status": "no data"}` (L604/L608, L644/L648), the consumer tests membership before reading,
and takes the short path when it is present. **No `KeyError` is reachable at either site.**

**A second, independent reason the exposure is nil.** The graded artifact is written at L809,
**before** the console summary block begins at L812:

```
809:    (HERE / "f9_criteria.json").write_text(json.dumps(out, indent=2, default=str))
```

So even a raise inside the summary could not lose the grade — `f9_criteria.json` is already on
disk. The blocked region is a **terse console print**, not the grading path.

**Ruling: the hard blocker on `f9_criteria.py` is LIFTED.** The file may be executed. Nothing
about F9's landed records changes in either direction — they were never in question.

**And I record the cost honestly: this blocker should never have been raised.** It was raised
on the instrument's report without the reachability check, by me. That is the finding in §3.

## 2. F6b `relax_invariance.py` — **THE BLOCKER STANDS. AND THE STATED DEFECT IS WRONG.**

The blocker is upheld, but **not for the reason it gives**, and the correction matters because
a future repair aimed at the stated defect would fix nothing.

**What the blocker says is exposed — `r["reattachment_x_over_h"]`, `r["separation_x_over_h"]`,
`r["profile_scaled_mae_overall_percent"]` for arms B and C — is GUARDED and NOT REACHABLE.**
The short branch (L66) writes `{"case": ..., "state": "NO WRITTEN TIME"}` and therefore has no
`converged` key. The consumer guards with `.get()`:

```
 92:        if not r.get("converged"):        -> INCONCLUSIVE, reads nothing
 96:        elif not r.get("steady_bubble"):  -> INCONCLUSIVE, reads nothing
101:        else:                             -> the subscripts live here
```

`r.get("converged")` on the short branch returns `None`, `not None` is `True`, and the short
branch lands in the **first** INCONCLUSIVE arm, which performs no subscript. **Arms B and C
are safe.**

**What IS exposed, and the sweep did not name it, is the INCUMBENT arm A.** At L87:

```
 87:    A = out["arms"]["A"]
```

`A` is then subscripted **unguarded** at five sites — L102, L103, L107, L109 and L135. **If
arm A itself takes the short branch, every one of those raises `KeyError`,** and no `.get()`
stands between them and the raise.

**Two independent reach routes, and the second does not involve B or C at all:**

- **Route 1.** Arm A short-branches, and B or C converged with a steady bubble → the `else` at
  L101 executes → raise at L102.
- **Route 2.** Arm A short-branches, and `medium_relax_PC` exists with exactly two crossings →
  raise at L135. **This route is reached even if B and C both short-branch**, because the
  L129–L135 block is a separate loop with its own condition.

**Ruling: the hard blocker on `relax_invariance.py` STANDS, IN FORCE.** The repair is on the
**`A[...]` reads, not the `r[...]` reads** — the latter are already correct and are the
pattern the former should adopt. A repair that hardens `r[...]` and leaves `A[...]` alone
leaves the file exactly as armed as it is today.

---

## 3. THE INSTRUMENT DEFECT — `scripts/check_grader_self_blindness.py` HAS NO GUARD AWARENESS

**This is the finding worth more than either triage.**

The probe's ERROR class is *"a branch omits a key that IS read elsewhere (armed crash)."* It
locates the write sites and the read sites and reports. **It does not model whether the read is
guarded.** Searched over all 323 lines for any handling of a membership test, a `.get()`
default, or a `try`/`except` — `ast.Compare`/`ast.In`, `.get(`, `ast.Try`, `ExceptHandler` — the
only hit is the probe's own bookkeeping (`owner.get(node.lineno, "<module>")` at L170), which is
unrelated.

**Consequence: the ERROR class is not sound. It reports a defensive read and an armed crash
identically**, and it has already manufactured one hard blocker (F9) against a file with no
reachable defect, while mis-stating the exposure in the one real finding (F6b).

**This does NOT retire the instrument, and I want that on the record as firmly as the defect.**
The same probe found `grade_f3.py` — the defect that had **already fired** and made the F3
conversion `NOT A RESULT` — and it found F6b, which is real. **Both were found by the
instrument, not by reading.** A probe with a false-positive rate is worth far more than no
probe. What it may not do is have its ERROR output treated as a verdict.

**Recommended repair, and I am NOT making it here** (`scripts/` is nobody's territory, and an
instrument change is a §3 check-1 item that must be read as a diff before its output is
believed):

1. **ERROR requires an UNGUARDED read.** A read dominated by `if "k" in d`, by `d.get(k)`, or
   sitting inside `try:`/`except KeyError` is **not** ERROR.
2. **Guarded reads demote to INFO, not silence** — the schema really does diverge, and the next
   consumer added may not be guarded. That is the sweep's own standing sentence, and it is
   right: *"a WARN is not harmless — it is the same defect one consumer away from becoming an
   ERROR."*
3. **Report the read site's guard state on the row's face**, so the next reader is not required
   to re-derive what I just re-derived by hand.
4. **A positive control:** the probe must be shown able to distinguish a guarded from an
   unguarded read of the same key, or its guard-awareness is asserted rather than demonstrated
   (standing rule 3's principle, applied to a static probe).

**The general lesson, stated against myself:** I blocked a file on an instrument's ERROR
without asking whether the crash it named could be reached. **An audit instrument's finding is
a lead, not a verdict** — the same relationship a lane's test has to a supervisor's read. I
applied that rule to lanes and not to a script, and it cost a spurious blocker.

---

## WHAT CHANGES ON DISK

| file | before | after |
| --- | --- | --- |
| `verification/runs/F9_work/DO_NOT_RERUN_f9_criteria.md` | BLOCKER IN FORCE | **LIFTED** — amendment appended, original preserved |
| `verification/runs/F6b_runs/DO_NOT_RERUN_relax_invariance.md` | BLOCKER IN FORCE, defect stated on `r[...]` | **IN FORCE**, defect **CORRECTED to `A[...]`** — amendment appended, original preserved |
| `scripts/check_grader_self_blindness.py` | — | **UNCHANGED.** Repair recommended above, not made here |

Both amendments are appended at the foot with the original text left standing (standing rule 6:
a departure is disclosed in a dated amendment, never by rewriting).

**Compute: ZERO. No solver ran for any part of this.**
