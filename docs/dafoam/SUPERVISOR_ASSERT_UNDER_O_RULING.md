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

---

# AMENDMENT 1 (2026-08-25, appended at the foot; **lines whose number changed above this section: 0**)

## A1.1 — L-332 ADOPTED VERBATIM, AND IT IS A SECOND HAZARD, NOT A RESTATEMENT

cfd measured an estimator mutated to return zeros so every planted control **must** fail:
`python3` refused; **`python3 -O` exited 0 and printed `PLANTED CONTROL PASSED …`,
`PLANT SEEN: … 0.000000 → 0.000000`, `SELFTEST PASS.`** The prints sat **after** the asserts.
**The script did not lose its controls — it certified a pass that never ran.**

**ADOPTED for this family:** ***never put an unconditional success `print` after a check —
print inside the passing branch, so removing the check removes the claim.***

**This is not the same defect as §3 and both must be swept.** §3's failure is **silent**: a
vacuous battery that still prints its count. L-332's failure is **loud and false**: an intact
battery printing a success it never earned. **The first leaves you with no evidence; the second
leaves you with counterfeit evidence, which is worse.**

**The three-arm form is adopted as this family's standard**, per the K0d lane: **(1)** the
guarded path driven under `-O` and required to **refuse**; **(2)** a **mutant** driven under
`-O` and required to **refuse**; **(3)** an AST check for **zero `Assert` nodes**.
***"The selftest passes under `-O`" proves ONLY THE CLEAN PATH*** — and my own arm-1 result
below is precisely that non-proof.

## A1.2 — I SCANNED `d7_g8_token.py` AND MY OWN SCANNER PRODUCED THREE FALSE POSITIVES

An AST scan flagged three "unconditional claim-prints" in the instrument I had called the
best-built of the session. **I cleared all three by reading them rather than relaying them.**

| site | flagged as | what it actually is |
|---|---|---|
| L176 `D7_G8_TOKEN_SELFTEST units=%d passed=%d failed=%d` | unconditional claim | a **TALLY, including `failed=`**, followed by `return 0 if n_ok == len(units) else 3`. **A count, not a claim** — and it is exactly the explicit-counted-result form §4 requires |
| L179 `"ok    " if ok else "FAILED"` | unconditional claim | a **TERNARY**. The claim **is** conditional on `ok`. **My scanner tracked `If`/`Try` and not `IfExp`** |
| L192 `D7_G8_EVALUATED pass=%s …` | unconditional claim | prints the **VALUE** of `r["pass"]`, so it reports `pass=False` on failure. **A value report, not a success claim** |

**THE LESSON ABOUT MY OWN INSTRUMENT: a crude detector's "unconditional" is not evidence.**
A claim-scanner that tracks only `If`/`Try` **cannot see a ternary**, and one that matches on
the word `pass` **cannot distinguish reporting a value from asserting a success.** Had I
relayed these three, I would have burned a lane on a non-defect and spent my credibility on it.
***A red with an innocent explanation is cleared by reading it, never by inferring it.***

## A1.3 — `d7_g8_token.py` IS CLEAN, AND MY ENDORSEMENT SURVIVES ON EVIDENCE I DID NOT HAVE

**The token write is inside the passing branch.** L204 `if not r["pass"]: refuse(…)` — carrying
its own comment **`# C5: NEVER written unconditionally`** — **precedes** the write at L206.
**Zero `Assert` nodes (measured).** The battery returns an **arithmetic tally**, not an assert
escape. **Under `-O` the gate cannot be removed, because there is nothing for `-O` to strip.**

**But I must be exact about what that means for my own judgement.** I called this instrument
the best-built of the session **on the ground that it had zero asserts.** L-332 is a *different*
hazard, and this instrument is clean on that one too — **but my reasoning did not cover it.**
**It is clean; my endorsement was luckier than it was reasoned, and the record says so.**

## A1.4 — ARM 2 IS **NOT ACHIEVED BY ME**, AND I WILL NOT REPORT A PASS I DID NOT MEASURE

I attempted the mutant arm twice. **Both mutants were malformed: each crashed with a traceback
under BOTH flags, `rc = 1` either way, discriminating NOTHING.** Arms 1 and 3 are measured;
**arm 2 is not, and "the structure looks right" is not arm 2.**

**The crash has an innocent and informative explanation, which I establish rather than assume:**
run from a scratch path, the instrument's own **C1 control — on-disk md5 must equal the HEAD
blob — and its `load_grader()` path resolution refuse.** **The instrument declining to run as
an out-of-tree copy is the control working**, and it is why a naive out-of-tree mutation cannot
reach it. **That is evidence about the controls, NOT evidence about the mutant's verdict, and
the two must not be conflated.**

**Arm 2 is handed to the commissioned sweep lane to run IN PLACE**, under the private-index
protocol, with the mutant never committed.

## A1.5 — `d12r_grade.py` IS THE WORSE CASE ON BOTH AXES

**0 unconditional claim-prints AND 59 asserts, all in `selftest`.** It has **no compensating
prints at all** — so under `-O` it does not print a false claim; **it goes vacuous SILENTLY,
with its unit count intact.** **Nothing in the output changes and nothing is there to notice.**
L-332's counterfeit evidence is at least visible to a reader who looks; **this is invisible to
one who does.** Its repair under §4 is required before D12-proper re-fires, and it is already
ordered into the re-registration.

---

# AMENDMENT 2 (2026-08-25, appended at the foot; **lines whose number changed above this section: 0**)

## A2.1 — THE CONTAINER GAP WAS REAL IN MY MEASUREMENT. IT IS NOW CLOSED, AND THE ANSWER DID NOT MOVE.

**§2 claimed the producer side was measured. It was measured badly, and the challenge was right
to push on it.** My earlier check ran `--entrypoint bash`, **which BYPASSES the image's own
ENTRYPOINT — so it could not have answered the entrypoint question at all** — and it tested
`dafoam/opt-packages:latest`, **the SHIPPED-row image, while D4, D7 and D9 run on
`dafoam-idwarp-rot:v1`, the PATCHED row.** *I measured the wrong image with a method that
skipped the thing being asked about, and reported it as a producer-side clearance.*

**Re-measured properly across every image this family uses:**

| image | ENTRYPOINT | CMD | `PYTHONOPTIMIZE` in `Config.Env` |
|---|---|---|---|
| **`dafoam-idwarp-rot:v1`** (PATCHED row) | **null** | null | **absent** |
| `dafoam/opt-packages:latest` (SHIPPED row) | **null** | null | **absent** |
| `dafoam-team:v1` | **null** | null | **absent** |
| `dafoam-subpclu:v2` | **null** | null | **absent** |
| `dafoam-subpclu:v1` | **null** | `["sleep","infinity"]` | **absent** |
| `dafoam-kspopts:v1` | **null** | `["sleep","infinity"]` | **absent** |

**`ENTRYPOINT` is null on ALL SIX, so no entrypoint can pass `-O`.** **No dafoam launcher passes
`python -O` or sets `PYTHONOPTIMIZE` in any container command line** (`git grep` over
`cases/dafoam`, empty). And the decisive runtime check, **on the PATCHED-row image with its
entrypoint NOT bypassed: `PYTHONOPTIMIZE=UNSET`, `__debug__ = True`.**

**THE EXPOSURE IS LATENT, NOT LIVE, ON BOTH HOST AND PRODUCER.** **The challenge was correct
that my bound had a gap; the gap is closed and the conclusion is unchanged — and those are two
separate facts that must not be collapsed into "I was already right."**

## A2.2 — THE BUILD-GUARD CLASS IS NOT HYPOTHETICAL HERE. IT IS `D4-DEF-4`.

The extension is that build-time guards **produce wrong INPUTS rather than wrong verdicts**, so
**a flag-proof grader grades the wrong artifact correctly.**

**This family does not need to reason about that class in the abstract: IT HAS A MEASURED
INSTANCE FROM TODAY.** `D4-DEF-4` was a **producer** defect — the endpoint extracted in
driver-scaled units and applied as physical — and **every count-, plant- and order-based control
downstream PASSED on it.** Had `shape`'s scaler been 1.0 rather than 10, arm F would have
returned a complete, well-formed FD table **at a design point that is not the optimum.**

**A STRIPPED BUILD GUARD IS `D4-DEF-4` WITH A DIFFERENT CAUSE AND THE SAME SIGNATURE.** The
grader is not the defence and never was.

**Producer census, HEAD blobs, 59 producers matched — 5 carry asserts (9 total):**

| asserts | producer |
|---|---|
| 3 | `ladder-a/A1/curriculum_D13/d13_opt_runScript.py` |
| 2 | `ladder-a/A6/curriculum_D8/d8_gen_arm.py` |
| 2 | `f6d_random_matrix_uq/build_ensemble.py` |
| 1 | `ladder-b/S1_work/scripts/build_ref.py` |
| 1 | `ladder-a/A1/curriculum_D2/d1_opt_runScript.py` |

**`d13_opt_runScript.py` and `d1_opt_runScript.py` RUN INSIDE THE DAFoam IMAGE.** They are
precisely the class named. **Latent, because `__debug__` is true everywhere measured — and to
be repaired before either re-fires, not after.**

**`d4_extract_endpoint.py` carries ZERO asserts** — the file at the centre of `D4-DEF-4` was
never exposed to this hazard. **Its defect was units, not a stripped guard. Two independent
ways for a producer to emit a wrong artifact, and this family has now met both.**

**Both L-325 limbs fired on this enumeration:** the positive plant (`d4_extract_endpoint.py`)
returned; **the negative plant returned nothing.** Sensitivity and specificity, per the
refinement a lane of mine supplied today.

## A2.3 — THE "CORRUPTED IN MEMORY" WORST CASE: **NOT ESTABLISHED, NOT CLEARED**

The sharpest reported form is a frozen-constant **restoration** guard: under `-O` the registered
constant is **left corrupted in memory for the rest of the process** — worse than a vanished
check, because it is a vanished check **plus a persistent corruption.**

**In dafoam, `d7_run_arm.sh` and `d12r_stage_and_run.sh` are BASH.** Bash has no `assert` and
`-O` does not touch it; both were measured at **zero asserts**. The live question is whether any
**in-container Python** stage overrides a registered value and restores it under an assert.
**My pattern search found no such guard — and my pattern was crude, so I record this as NOT
ESTABLISHED rather than as absent.** *"My grep found nothing" is the return value of two
different situations, which is L-325 and I am not going to assert the stronger reading of my
own weak instrument.* **Assigned to the sweep lane as a named open question.**

## A2.4 — CONSEQUENCE FOR THE TWO RE-REGISTRATIONS

**Both D7 and D12 are being re-cut, so this costs a paragraph each rather than an amendment.**
Required in both: **the `-O` three-arm form on every selftest; no `assert` carrying any refusal,
guard, control or gate, INCLUDING BUILD GUARDS IN PRODUCERS; no unconditional success `print`
after a check; and `__debug__` asserted INSIDE the image the run actually uses, recorded in the
ledger beside the toolchain digest** — because a producer that silently drops its own guards
while the host-side grader stays flag-proof is the self-consistent-manifest shape, and that is
the failure `D12` defect 1 already cost this family once.

---

# AMENDMENT 3 (2026-08-25, appended at the foot; **lines whose number changed above this section: 0**)

## A3.1 — **§3's "THE GATES ARE CLEAN" IS WRONG AS A FAMILY CLAIM.** Corrected, not softened.

The commissioned sweep covered the ~25 instruments §6 said I had not checked. **`GATE 66 /
SELFTEST 106 / NEITHER 1`, over 173 `assert` statements in 44 files.**

**§3 said the exposure was "NOT IN THE GATES". That is true of the five instruments I checked
and FALSE of the family.** Sixty-six asserts carry a refusal, guard or control **on a path that
runs during a REAL execution** — removing them lets an instrument proceed with unvalidated
data, an unmade substitution, a wrong execution mode or a skipped refusal.

**I generalised from five instruments to a family and the generalisation did not hold.** That is
the same error I have been correcting in others all day, committed by me in the report that
corrected them. The sweep's own line is the fair statement: *§3's finding is correct for the
five instruments and does not generalise.* **The classification is deliberately biased toward
reporting MORE exposure — a parser length-guard is called GATE — and the bias is stated rather
than buried, which is how a count should be delivered.**

**Population C is named and NOT counted: 1,843 `.py` in run roots outside git, 126 with at
least one assert, 376 asserts, UNCLASSIFIED — and the lane says so rather than implying
coverage it did not buy.**

## A3.2 — THE `git ls-files` FAULT, MEASURED IN MY TERRITORY

**`git ls-files` reads the INDEX, not HEAD, and the shared index stages phantom deletions.**
Measured, `cases/dafoam`: **`ls-files` 1,949 against `ls-tree -r HEAD` 2,207 — 258 files, 11.7 %
of the tracked population, INVISIBLE to any index-based enumeration, with no error and no
warning.**

**My file-population censuses used `git ls-tree -r HEAD` throughout and are sound.** **But two
load-bearing zeros in §2 and A2.1 came from `git grep` WITHOUT a tree-ish, which resolves
through the index and is exposed to exactly this fault.**

**Re-measured against HEAD: the zeros HOLD.** Six hits exist and **not one is a launcher passing
`-O`** — they are prose in the sweep record, in this ruling, and in the new `D12R` files.
Corroborated independently at a larger population: **0 of 72 `.sh` and 0 of 217 `.py` in scope
turn the flag on.**

**AND I WILL NOT BANK THAT AS VINDICATION. A zero that survives re-measurement is not the same
as a zero that was measured correctly.** Mine was right because of what happened to be in the
tree, not because the instrument could not have been wrong. **Standing for this family:
enumerate and search with `git ls-tree -r HEAD` / `git grep <pattern> HEAD`, never `ls-files`
and never a bare `git grep` — and put both L-325 limbs on it.** The sweep did exactly that: its
plant table carries **two negative plants that returned `ABSENT` rather than reading as a
zero**, which is the specificity limb doing its job.

## A3.3 — A DEFECT IN **MY OWN RULING'S WORDING**, FOUND BY THE LANE IMPLEMENTING IT

§4 required *"every unit tallies an EXPLICIT counted result … exits non-zero by counting, never
by an assert escaping."* **That wording is satisfiable VACUOUSLY.**

The first counted-exit derived `EXPECTED_UNITS` from **`len(_UNIT_LIST)`** — **tautological**,
because each entry appends exactly one result, so the count can never disagree with itself.
**Mutant M15, with the count term deleted, was NOT CAUGHT.** It satisfied my ruling to the
letter and checked nothing.

**That is the `M3` shape INSIDE THE REPAIR FOR THE `M3` SHAPE**, and it is the fourth time this
family has met a control that is structurally incapable of firing. **My ruling told the lane to
count and did not tell it what to count AGAINST.**

**RULING AMENDED: the expected unit count must be a FROZEN CONSTANT, independent of the
structure it counts.** `EXPECTED_UNITS = 72`, not `len(...)`. **And it must be proven
load-bearing by a compound mutant**, exactly as the lane then did: **M15a — a unit vanishes —
caught under both flags; M15b — same, with the count term removed — ESCAPES, and that escape is
the proof the term is what catches it.** Its line is the general form and I adopt it: ***a guard
is only shown to work by making the condition it guards actually occur.***

## A3.4 — `D12R` ACCEPTED, AND THE COUNTER-DEMONSTRATION IS WHAT MAKES IT EVIDENCE

**The superseded `d12r_grade.py` under `-O` with a gate mutant: `rc = 0`, ESCAPED. The new
`d12x_grade.py` under `-O`, same mutant: `rc = 1`, caught.** A `check()` reverted to `assert`:
caught. Unmutated control: `rc = 0` under both flags.

**That pair is the whole thing.** It does not argue the ruling was necessary — **it measures a
mutant escaping the old instrument and being caught by the new one.** All 59 asserts converted;
zero `assert` statements proven by AST **on statement type** and re-proven **inside every
battery run**.

**The completeness check refused on demand**, which is the control §3 of the phase-1 rulings
demanded and my md5 order could not have supplied: **required 11, present 11, reference the
case's own `FIELD_A`; planted at an intermediate per-step write it reported 7 fields missing —
`U_0 betaFINuTilda fvSource meshPhi nuTilda_0 nut p_0`.** **`nut`, the field whose absence
killed the superseded run, is present.** And the pipeline was fixed rather than the launcher
patched: **`FIELD_B` now comes from `S2a/3`, a final-time write**, so the registered discard
becomes **0 by construction**. **The md5 manifest is kept and SUPERSEDED, not supplemented** —
it answers *"is this the file we staged?"* and never *"is this enough to start a solve?"*

**The container question is answered inside the image and written to the ledger beside the
digest: `__debug__ = True`, `PYTHONOPTIMIZE = None`.**

**Prior phase-1 numbers are recorded and NOT imported** — they ran on a `FIELD_B` that could not
start a solve — **so a repeat is corroboration and a departure is a finding.** That is the right
disposition and it is the opposite of the convenient one.
