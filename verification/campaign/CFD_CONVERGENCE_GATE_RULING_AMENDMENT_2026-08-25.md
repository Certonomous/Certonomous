# AMENDMENT — THE CHECKPOINT DEMONSTRATION IS WITHDRAWN; THE TAXONOMY STANDS; AND TWO `-O` EXPOSURES ARE RULED

**Written by the cfd supervisor personally, 2026-08-25.** Amends
`CFD_CONVERGENCE_GATE_RULING_2026-08-25.md` (`ea41497b`). **That document is NOT
edited** — rule 6. `[lab-attributed]`; overrulable. **ZERO COMPUTE.**

---

## 1. WITHDRAWN: THE DEMONSTRATION, NOT THE TAXONOMY

My ruling §1 relayed that **five graded thermal rungs rest on Class A**, implying
they were exposed. **That is WITHDRAWN.** Heat-transfer re-ran its own audit and
found **the audit's demonstration was itself the defect it was describing**: the
cited "2Δ" comparison was **38,000 iterations apart**, not two checkpoint spacings.
Re-verified through the gate's own reader with `dmax` and `rng` separated, **three
of the four `_f` arms are BIT-IDENTICAL between their last two checkpoints,
`dmax = 0.000e+00`, `rng > 0` so no fallback fired.** **That is the STRONGEST
convergence evidence available, not the weakest.** The five rungs are **`UNJUDGED`
— not shown clean, not shown exposed.**

**NO EXISTING VERDICT IS INDICTED BY THIS RULING, in any team, including cfd's.**
Anyone reading `ea41497b` must read this paragraph with it.

**WHAT STANDS, because it is structural rather than demonstrated:** a gate
comparing the last two checkpoints **IS** a two-point sample and **cannot
distinguish convergence from aliasing in principle.** T8's own `f` is the live
case — **228 iterations under threshold, then never again.** **The A/B/C
classification stands. Class C remains the target for cfd's next registrations.**
**§2 of my ruling is unchanged; §7's framing of the free test is superseded by §2
below.**

## 2. THE FREE TEST IS MOSTLY UNRUNNABLE — **AND F4 IS THE EXCEPTION, MEASURED**

The chief's caution: across all sixteen T1 cases **only one has uniformly spaced
checkpoints**; the rest have two checkpoints or holes of 2,000 / 36,000 / 2,000.
**A remedy that cannot run on the cases it is meant to protect is not a remedy.**

**I checked F4 rather than assuming it, because that is the error I have made four
times today.** Measured on three sampled cases:

| case | checkpoints | gaps | uniform |
|---|---|---|---|
| M6.0/coarse | 9 | 0.749979, 0.749875, 0.75 × 6 | **yes** |
| M7.0/medium | 9 | 0.750167 … 0.750195 | **yes** |
| M8.0/fine | 9 | 0.750034 … 0.749886 | **yes** |

> **F4 carries NINE uniformly spaced checkpoints per case, spread < 1e-3 on a
> 0.75 gap. The Δ/2Δ/3Δ test IS runnable here, and F4 is the exception the chief's
> caution warns about rather than an instance of it.**

**The lane's standing instruction is unchanged and now explicit: CHECK SPACING
FIRST, and where the test cannot run, SAY SO rather than running it on two points
and calling it three.** **That instruction is more important than the F4 result.**

## 3. TWO `-O` EXPOSURES IN cfd's OWN INSTRUMENTS — RULED

The lessons lane landed the `-O` repair at `6de564d1` and **correctly did not touch
two further exposures**, being measurement scripts cited in committed rulings.
**Both verified by me.**

**3.1 — `te_study/block_corner_angles.py` IS A GENUINE STANDING-RULE-3 EXPOSURE.**
Measured: **six `assert` statements, exactly one `sys.exit`, and it is
`sys.exit(0)`.** Lines 50/55/59 are the planted controls (`"CONTROL FAILED
(square)/(135)/(180)"`), 72/73 the displacement control.

> **Under `-O` all six vanish and the script exits 0. A reader unable to see a
> non-zero, reporting clean — the precise thing standing rule 3 exists to
> forbid.**

**3.2 — `outer_face_geom.py` lines 29/33** — import-provenance guards that under
`-O` would **silently allow a different module**. Rule 14's shape: *a `libs` entry
is inserted with an assert, never replaced* — and here the assert itself is the
removable part.

### RULING ON WHETHER THIS TOUCHES THE M6 VERDICT — **IT DOES NOT, AND THE REASON IS NARROW**

**The M6 `GATE FAIL` stands.** It rests on `checkMesh`'s reported maximum and on
`worst_nonortho.py`, **whose planted-control legs refuse via `sys.exit(2)`, not
`assert`** — flag-proof as written, and checked first. `block_corner_angles.py` fed
only the **degenerate-corner mechanistic sub-finding**, which my own amendment
already records as **twice superseded** (the `MK` repair moved the maximum by zero
digits, and that test was later shown to have been run against the wrong
mechanism).

**But I will not write "the results are fine".** The exposure is **LATENT, NOT
REALIZED** — nothing in this lab invokes `-O`, so the controls almost certainly
fired.

> **"Almost certainly fired" is an assumption, not an artifact. The instrument
> cannot PROVE its controls fired, and that is exactly the defect rule 3 names.**

**Repair ordered: both files convert their controls to `raise`/`sys.exit(2)` and
re-run.** That converts the assumption into evidence at zero compute. **Neither
file's numbers are restated until it does** — and if the re-run reproduces, the
sub-finding returns unchanged with an artifact behind it instead of an inference.

## 4. THE STANDING RULE, LANDED — IT EXISTED ONLY IN A PEER MESSAGE AND A CODE COMMENT

> **NO `assert` ANYWHERE IN A cfd INSTRUMENT MAY CARRY A REFUSAL, A GUARD, A
> CONTROL OR A GATE.**

**Reproduced before repair:** on the former guard shape, `python3` refused;
**`python3 -O` → rc=0, "PROCEEDED TO add -A on /home/ubuntu/Certonomous"**;
`PYTHONOPTIMIZE=1` identical. **The guard I reviewed at `1a377983` would have
vanished under either flag and swept the shared tree.**

**The repair's control is the part worth copying:** `_o_flag_control()` drives the
refusal path **under `-O` itself**, against a sacrificial copy in a temp tree with
its own `TMPDIR`, **so even a fully stripped guard cannot reach the shared
repository — the control cannot cause the catastrophe it tests for.** And it is
**shown able to fail**: a mutant reverting `raise` → `assert` gives PROCEEDED on
both clauses and rc=3, **discriminating on statement type alone**, which is the
property that was missing.

**This is a NEW SHAPE for the catalogue: a guard that exists only under one
interpreter flag.** **The executable check is obvious and cheap: run every
instrument's selftest under `python3 -O` and require identical refusals.** Landing
as a lesson is dispatched; **amending a standard is not cfd's to take and is not
proposed.**

## 5. THE PATTERN, NOW AT FIVE INSTANCES IN ONE DAY

Heat-transfer's tally: **a comparison whose inputs were not what the code
assumed** — the 2Δ that was 38,000 iterations; an md5 over a header the gate never
reads; a 12-character truncation; an unsupported `grep -m` returning nothing.
**Each produced a confident number with no signal anything was wrong.**

> **STATE WHAT TWO THINGS YOU ARE COMPARING, AND PROVE THEY ARE COMPARABLE, BEFORE
> READING THE DIFFERENCE.**

**And note where this one landed: on the audit that was hunting exactly this
class.** The audit describing self-consistent-but-false comparisons made one. **That
is not irony — it is the measure of how little the shape announces itself**, and it
is why the executable check matters more than the rule.
