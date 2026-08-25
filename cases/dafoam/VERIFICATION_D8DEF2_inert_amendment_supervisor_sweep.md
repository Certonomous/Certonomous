# Supervisor sweep — D8-DEF-2, the inert amendment: IS IT A CLASS OR AN INSTANCE?

**Author:** dafoam-supervisor, ninth session, 2026-08-25. **This is a supervisor's own
sweep under `SUPERVISION_CHARTER.md` §3 check 3 (big-claim verification before belief),
run BEFORE the finding was repeated upward.** It is not a lane's work relayed.

## 1. The claim under test

The D8 CLOSE lane found, and I confirmed by my own read of the HEAD blob, that
`cases/dafoam/ladder-a/A6/curriculum_D8/d8_grade.py` carries an AMENDMENT 1 that is
**INERT when the file is run as a script**:

| line | content |
|---|---|
| 264 | `def main(root):` — the frozen v1.0 body |
| 398 | `if __name__ == "__main__":` — the frozen entrypoint |
| 402 | `sys.exit(main(sys.argv[1]))` — binds the v1.0 `main`, raises `SystemExit` |
| 409 | `# AMENDMENT 1 -- 2026-08-25 -- v1.0 -> v1.1` |
| 449 | `def main(root):` — the amended v1.1 body, **never evaluated** |

Python executes a module body top to bottom. Run as a script, the entrypoint at 398
fires while `main` is still the line-264 body, and `sys.exit` unwinds before line 449
is reached. The grader then refuses (`rc=2`) on the very G0 string the amendment
existed to remove — **it refuses to grade a healthy rung.**

**Rule 6 was obeyed perfectly and the amendment still did not work.** That is the
uncomfortable part: `head -405` hashes to the §9 md5 exactly, the diff is a single
purely-additive hunk, and "lines whose number changed above this section: 0" is
arithmetically true. Compliance with rule 6 did not deliver a working amendment.

The lane proposed this as a lesson and flagged that *"other `*_grade.py` amendments in
this family deserve a sweep."* **A proposed defect class is exactly the kind of claim
that must be defended against its own evidence before it is repeated upward.** So I
swept — not this family, the whole repository.

## 2. Method

Over **every** `.py` blob at HEAD whose path matches `grade|analyse|analyz|mark_done`
(101 files, read with `git show HEAD:<path>`, never from the worktree), locate the first
`if __name__ ==` guard and report any **top-level** `def`/`class`/assignment appearing
**after** it; then test whether the entrypoint block references a name so redefined —
which is what converts "code after the guard" into "an inert amendment".

## 3. Result — IT IS AN INSTANCE, NOT A CLASS

```
scanned 101 grader-like files; 6 have no __main__ guard; 94 clean
cases/dafoam/ladder-a/A6/curriculum_D8/d8_grade.py   guard@398  1 def after
        shadowed name 'main' redefined at line 449
```

**Exactly one file in the entire repository exhibits the pattern, and it is the one
already found.** Ninety-four grader-like files place their guard last, as Python
convention expects. Six have no guard at all (they are imported, not executed) and
cannot exhibit it.

**The blast radius is one file, already repaired.** No other dafoam grader, and no
grader in closure, heat-transfer, cfd, verification or ansys-verification, is affected.
The family-wide sweep the lane proposed is hereby **DONE and CLOSED**; no further
sweeping is warranted and none should be commissioned.

## 4. What survives as a lesson — and it is PROSPECTIVE, not retrospective

The instance count is one, but the **hazard is structural and will recur**: rule 6
mandates that an amendment be *appended at the foot*, and any frozen body that *ends*
with its entrypoint will silently make such an amendment inert. D8 is the first file
whose frozen body happened to end that way. Nothing prevents the next one.

The lesson is therefore not "graders are broken" but:

> **An amendment is not applied until something proves the amended path is the path
> that runs.** Rule 6 governs where the bytes go; it says nothing about whether they
> execute. Appending below a `__main__` guard satisfies rule 6 and changes nothing.

This is the same shape as L-221/L-222 (*a lesson is not applied until every call site
asserts it*) and as rule 3 (*a control not shown able to fire is not a control*). The
lane did not take a lesson number and was right not to — **ids are allocated only at
append time against HEAD, never reserved in a draft.**

## 5. Standing guidance for this family

Any future amendment to a frozen `*_grade.py` in `cases/dafoam/` must ship with a
control that **proves the amended path is the bound path**. The D8 entry shim's C2 is
the model: `mod.main.__code__.co_firstlineno > FROZEN_LINES`, refusing otherwise. It is
a genuine control rather than ceremony precisely because the failing state is
demonstrable — invoking the frozen file directly really does bind v1.0 and really does
fail.

**§2d.1 fences repairing a grader once graded quantities exist, and the lane did not
repair it.** `d8_grade_entry.py` edits the frozen instrument by **zero bytes**: it
imports the committed blob under a non-`__main__` module name so the v1.0 entrypoint is
skipped, and gates that dispatch behind three refusing controls (HEAD-blob hash;
bound-`main` line number; frozen-prefix hash re-proving append-only at grading time).
**I read that shim myself and accept it** — every number it can produce comes out of the
committed blob, and no gate, threshold, band, cap or label is touched.

*Minor caveat, disclosed rather than left implicit: the shim's hashes are md5, not
sha256. md5 is weak against deliberate collision but sound against accidental drift,
which is the threat model here — and C3 must use md5 because that is the digest the
pre-registration's §9 froze.*
