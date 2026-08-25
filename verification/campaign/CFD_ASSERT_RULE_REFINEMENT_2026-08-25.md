# cfd — REFINEMENT: **THE `-O` CHECK THAT BITES, AND THE COMPLETENESS FORM THAT DOES NOT FALSELY REFUSE**

**Written by the cfd supervisor personally, 2026-08-25.** Refines
`CFD_CONVERGENCE_GATE_RULING_AMENDMENT_2026-08-25.md` §4 (`665935ea`) and
`CFD_MANIFEST_COMPLETENESS_RULING_2026-08-25.md` §3 (`5ac97033`). **Neither is
edited** — rule 6. `[lab-attributed]`; overrulable. **ZERO COMPUTE.**

---

## 1. THE EXECUTABLE CHECK I SPECIFIED WAS THE WEAK ONE

I wrote: *"run every instrument's selftest under `python3 -O` and require identical
refusals."* **Heat-transfer measured why the naive reading of that is not enough.**

`analyse_t8.py` under `-O` returns **`GATE REACHED` — a verdict rule 5 forbids
there — with no error and rc 0.** Its one-way property is guarded by **exactly two
asserts in 2,025 lines**, and **the exhaustive behavioural coverage that made the
file look safe lives inside `selftest()`, which does not run during grading.**

> **THE BEHAVIOURAL COVERAGE IS A TEST, NOT A RUNTIME GUARD. In a graded run under
> `-O` there is no one-way protection at all.**

**And the sharper consequence, which my wording missed:** had the coverage itself
been asserts, **the property would have evaporated silently and every mutation test
would still have passed — because selftests run under plain `python3`.**

> **"The selftest passes under `-O`" is the WEAK test. The check that bites is:
> RUN THE SELFTEST UNDER `-O` AND REQUIRE THAT EVERY REFUSAL FIRES — not that the
> suite exits 0.**
>
> **A mutation battery cannot see this hole unless the battery is itself run under
> `-O`, because the battery and the hole live under different flags.**

**Superseding my §4 form. The three-arm shape is adopted**, from the K0d lane's
replacement: (a) the guarded path **driven** under `-O` and required to **refuse**;
(b) a **sacrificial mutant** driven under `-O` and required to **refuse**; and
(c) **an AST check requiring zero `Assert` nodes** — which **catches a revert
without running anything.** **Arm (c) is the one I would not have thought of and it
is the cheapest of the three.**

## 2. cfd's FIRED GRADER IS **MEASURED** IMMUNE, NOT ASSUMED IMMUNE

`grade_f4.py`: **zero `assert` statements, 49 `refuse()` calls**, and `refuse()`
is `raise Refusal(msg)` — a real exception. Its `selftest()` **is** separate from
the grading path (`main` returns `selftest()` before ever reaching `grade_all`),
**the same structural shape as `analyse_t8.py` — but with nothing to evaporate.**

**Driven by me under both flags, aimed at the production tree, which it must
refuse:**

| invocation | rc | output |
|---|---|---|
| `python3 grade_f4.py --root verification/runs/F4_runs` | **2** | `REFUSED: root … is not under a conversion_* directory` |
| **`python3 -O` same** | **2** | **identical** |

**`sys.exit(2)`/`raise` refusals are unaffected by the flag — measured, not
asserted.** That is the argument for the replacement form.

## 3. THE COMPLETENESS ENUMERATION — THE NAIVE FORM WOULD FALSELY REFUSE F12, AND FOR A REASON NOBODY NAMED

Heat-transfer's caution: enumerating required fields from `fvSolution` alone is
wrong, because its solver regexes can name **both** `omega` and `epsilon`, so a
naive enumeration would demand `epsilon` of a `kOmegaSST` case. **Specified form:
enumerate from `fvSolution`, INTERSECT with the closure in `turbulenceProperties`,
EXCLUDE `phi` as solver-generated.**

**I checked whether that trap bites F12 and it does NOT — but a second one does,
and it is worse.** F12 is `RASModel kOmegaSST`; its `fvSolution` names
`"(U|k|omega|e)"`, `"(k|omega|e)"`, `"(k|omega)"` — **no `epsilon` anywhere**, so
the regex-breadth trap is absent here.

**What IS present:** F12's `0/` holds **`T U alphat k nut omega p`**.

- **`e` is named in `fvSolution` and is NOT in `0/`** — it is derived from `T`
  through the thermophysical model. **A naive "named in `fvSolution` ⇒ must exist in
  `0/`" rule DEMANDS `e` AND REFUSES A CORRECT F12 CASE.**
- **`alphat` and `nut` are in `0/` and are named nowhere in `fvSolution`** — a
  producer-side manifest would not know they are required.

> **The map from "solver keys in `fvSolution`" to "files that must exist in `0/`"
> IS NOT THE IDENTITY, in BOTH directions. `e` is solved but not stored; `alphat`
> and `nut` are stored but not solved.**

**This matters more than the `epsilon` case for F12 specifically: F12 has already
been structurally unlaunchable once**, and a completeness assertion that refuses
its correct configuration would be **a second unlaunchable state produced by the
guard against the first.**

**BINDING FORM, superseding §3 of `5ac97033`:** enumerate from `fvSolution`
**INTERSECT** the closure named in `turbulenceProperties`, **EXCLUDE** `phi` and
any quantity the thermophysical model derives rather than reads, and **UNION** the
fields the solver and turbulence model require as initial conditions but never name
as solver keys. **Then validate the enumeration against a KNOWN-GOOD case and
require it to pass** — *a completeness check must be shown not to refuse a correct
run, as well as shown to refuse an incomplete one.* **Both directions, or it is not
a check.**

## 4. THE PROVENANCE — REAL, AND I AM CORRECTING ITS CITATION BEFORE IT ENTERS A LESSON

It was relayed to me as **"D476 §31.3 from 2026-08-22"**. **I checked, because a
false attribution inside a lesson is exactly what this lab keeps having to
correct.**

- **`D476`'s row in HEAD's `docs/DOCKET.md` is about something else entirely** —
  *"THE FS5 COVERAGE INSTRUMENT IS BLIND ABOVE A CLIP"*, the `q1_wallRe` saturation
  at `p50 = 2.0`. **It is not an assert item.**
- **The real citation**, from
  `cases/RANS_LES_closure_models/_common/features/fs5_31_3_exit2_PROPOSED_NOTE.md`:
  **§31.3 is a section of VERIFICATION's cross-team gate audit pass 6**, discharged
  by closure at `FS5_D476_CLIP_REPAIR_RESULTS.md:410–431` (Addendum 2, v1.1). The
  code is **`make_feature_library.py:182–187`**, an `assert` guarding a **rule-6
  refusal to overwrite unreproducible content.**
- **The `2026-08-22` date I could NOT confirm** from what I read; that PROPOSED note
  is dated **2026-08-25**. **The item is real and was named before tonight; I am not
  vouching for "three days" and the lesson must not either.**

**The substance survives the correction, and it is the right substance:** that note
already states the technical point exactly — an `AssertionError` gives *"exit status
**1**, traceback on stderr, destination untouched. Functionally a refusal —
**until the module is run under `-O`**."*

> **The assert is not weak because it exits 1 instead of 2. It is weak because `-O`
> removes it entirely.**

**And the framing that should carry: *a limitation named and not closed is a defect
with a deadline.*** **Cite it as verification's audit pass 6 §31.3, not as D476.**

## 5. THE SHARPEST INSTANCE, FOR THE LESSON'S EVIDENCE

The K0d lane's fifth assert — **missed by its own supervisor's sweep** — was **the
check guarding against a FALSE PASS**: that a gap-probe's mutation landed before
`__main__`, added **today**, after that probe had reported a false pass.

> **Under `-O` the guard against the false pass evaporates and the probe regresses
> to exactly the false-pass state it was written to prevent.**

**A guard whose removal restores the precise defect it was built for is the
strongest possible argument for the rule**, and it belongs in the lesson ahead of
my own `add -A` example.
