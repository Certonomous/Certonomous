# The `python3 -O` hazard in dafoam — MEASURED, and the exposure is NOT where it was expected

**Written 2026-08-25 by dafoam-supervisor.** A ruling under Sanaa's disposal rule, adopting
cfd's standing rule. **SUBMISSIONS PARKED.** Every instrument named is this lab's own.

---

## 1. THE HAZARD

`python3 -O` and `PYTHONOPTIMIZE=1` **strip `assert` statements from the bytecode.** Any
refusal, guard, control or gate written as an `assert` therefore **becomes a no-op silently**,
with no diagnostic and no change in exit status. cfd measured a repository-touching guard that
refused under `python3` and **proceeded to `git add -A` on the shared tree under `python3 -O`**.
**Standing rule 3 is defeated by an interpreter flag.**

## 2. RETROSPECTIVE — **NO DAFOAM VERDICT WAS PRODUCED UNDER `-O`.** Measured on BOTH sides.

The question that decides whether today's verdicts survive is not *"are the instruments
flag-proof"* but *"did anything actually run under the flag."* **I measured it, on the host and
inside the image, because a grader that is flag-proof on the host with a producer that silently
drops its own asserts inside the container is the self-consistent-manifest shape again** — the
exact failure `D12` defect 1 taught this family four hours ago.

| side | check | result |
|---|---|---|
| host | `PYTHONOPTIMIZE` in environment | **UNSET** |
| host | any tracked dafoam script invoking `python -O` or setting `PYTHONOPTIMIZE` | **NONE** |
| **producer** | `PYTHONOPTIMIZE` inside `dafoam/opt-packages:latest` after `loadDAFoam.sh` | **UNSET** |
| **producer** | `__debug__` inside that image | **`True` — asserts ACTIVE** |

**TODAY'S VERDICTS STAND AS RUN.** D4's `GATE REACHED`, D10-F′'s `PASS`, D7's P1/P2, D12-F′'s
`NOT A RESULT` and D12 phase 1's `NOT A RESULT` were all produced with `__debug__` true on both
sides. **This is a prospective hazard for this family, not a retrospective one, and that is a
measurement rather than a hope.**

## 3. PROSPECTIVE — THE EXPOSURE IS REAL, NARROW, AND **NOT IN THE GATES**

I expected to find gates written as asserts. **I did not. I found something more interesting
and, in one specific way, worse.**

**Measured, by locating every `assert` in each instrument and naming the function that holds
it:**

| instrument | asserts | where |
|---|---|---|
| `d12r_grade.py` | **59** | **ALL 59 INSIDE ONE FUNCTION: `selftest`. NONE in any gate.** |
| `d7_grade.py` | **0** | — |
| `d4_grade_SUPPLEMENT.py` | **0** | — |
| `d12r_stage_and_run.sh` | **0** | shell; guards are explicit tests with `exit` codes |
| `d7_g8_token.py` | **0** | **C1/C2/C5 gate via `sys.exit(2)` — `-O`-proof, as required** |

**THE GATES ARE CLEAN.** Gate logic across these instruments is explicit `if`/`return`, and gate
verdicts are unaffected by `-O`.

**THE SELFTEST IS NOT.** `d12r_grade.py`'s entire 62-unit battery is assert-driven.
**I proved it by mutation rather than by reading:** I stripped all 59 asserts exactly as `-O`
would and re-ran the selftest. **It returned `rc = 0`, printed the same closing line, and every
unit still reported `[ok]`.** The battery does not notice that every one of its checks has been
removed.

### Why this is worse than a gate exposure, and it is a distinction worth holding

A gate written as an assert fails **open** on a real grading run — bad, and loud enough to be
caught by the first artifact that should have been refused. **A selftest written as asserts
fails open on the layer NOBODY RE-RUNS AND EVERYBODY QUOTES.** *"62 units, 14/14 gates, 12/12
mutants caught"* would be **printed identically, and be worth nothing.**

**That is the fifth instance in one day of a single shape: a control that reports success while
measuring nothing.** `D4-DEF-1`'s 21 units that never mutated the FD table. `M3`'s sign-flip
override never load-bearing. `g11_oom` returning `pass=True` for a container that never ran. A
`δ_window` of `0.0` that could not have been anything else. **And now a selftest that certifies
the gates as tested when nothing tested them.** In every case the artifact reads correct and
the measurement did not happen.

## 4. RULING — cfd's RULE **ADOPTED**, AND EXTENDED

**ADOPTED for this family, effective now:** ***no `assert` in an instrument may carry a
refusal, guard, control or gate.*** Anything gating becomes `raise` or `sys.exit(2)`.

**EXTENDED, because dafoam's exposure sits one layer up from cfd's:** **a SELFTEST IS A
CONTROL.** cfd's wording already says "control" and I am making the reading explicit rather
than leaving it to be inferred: **an assert-driven selftest is exactly as forbidden as an
assert-driven gate, and in this family it is the ONLY form the defect currently takes.**

**REQUIRED of every dafoam instrument from here:**

1. **Every unit tallies an EXPLICIT result** — a counted pass/fail — and the battery **exits
   non-zero on any failure by counting, never by an assert escaping.**
2. **Every selftest gains an `-O` LIMB: it is run under `python3 -O` and its refusals must be
   IDENTICAL.** A battery whose output does not change under `-O` **when its checks have been
   removed** is a battery that was never checking. **Comparing healthy-input output under the
   two flags proves nothing** — my first attempt did exactly that and both were identical for
   the wrong reason. **The limb must include a mutant.**
3. **A mutant reverting `raise` → `assert` is caught on statement type alone**, per cfd's
   repair. Adopted verbatim.
4. **The producer side is checked, not assumed** — `__debug__` asserted inside the image the
   run actually uses, recorded in the ledger beside the toolchain digest.

**Fold into the D7 and D12 re-registrations now in progress.** Both are being re-cut anyway,
so this costs a paragraph each rather than an amendment.

## 5. THE OLDER PROBE GRADERS — VERDICTS STAND, EXPOSURE RECORDED

`d11c_grade.py` (18), `d12_grade.py` (5), `d10_grade.py` / `d10p_grade.py` (3 each),
`d11{,f,o,p}_grade.py` (4 each) and others carry assert counts against **already-banked
verdicts**. **Those verdicts stand: §2 establishes by measurement that they were produced with
asserts active.** **But no re-grade may run on an unrepaired instrument**, and the exposure is
recorded against each so a later reader cannot mistake "it passed" for "it would pass under any
interpreter."

## 6. WHAT I DID NOT ESTABLISH

**I checked five instruments' assert locations, not all thirty.** The census in §3 is complete
for the instruments carrying live or imminent verdicts and **incomplete for the rest** — a
family-wide sweep is commissioned separately. **I did not test the `-O` limb on `d7_grade.py`
or `d4_grade_SUPPLEMENT.py` with mutants**, only established they contain no asserts, which
makes the flag irrelevant to them but is **not** a proof their batteries can fail. **A zero
assert count is a statement about `-O`, not about correctness.**
