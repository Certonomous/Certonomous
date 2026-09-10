# VMFL046-R9-REGRADE — PRE-REGISTRATION (DRAFT, NOT FROZEN, NOT COMMITTED)

**Case:** VMFL046 — Supersonic Flow with a Normal Shock in a Converging-Diverging Nozzle
(Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p. 155; title-page verified
against the PDF under rule 15 at the R1 registration and carried forward).

**Character of this registration:** **GRADING ONLY. ZERO SOLVER COMPUTE.** No mesh is
generated, no solver is launched, no field is written. The graded artifacts already exist
on disk and were produced under the **frozen VMFL046-R8 registration**
(`cases/ansys_verification/VMFL046-R8/PREREGISTRATION.md`, prereg commit `a7a0e72b`). This
document registers **one act**: running a **repaired reader** over those existing artifacts,
and grading the result against a gate that **does not move by one byte**.

**Predecessor:** VMFL046-R8 — register **Row #71 = `NOT A RESULT`**. All three levels of the
r=2 triple ran to `endTime` with `rc 0` and an `End` line; the frozen comparator then
**refused (exit 2)** because three `^`-anchored regexes could not read a legal
brace-inline `constant/fvOptions`. **590.7413 core-min of sound physics artifacts are intact
on disk and were never evaluated.**

**Status:** DRAFT written by an `ansys-lane-opus`. **NOT committed, NOT frozen.** The
`SUPERVISION_CHARTER` §3 check-1 diff-read and the sha-freeze are the supervisor's, taken
separately. This document is amendment-legal until first compute — and "first compute" here
means **the first invocation of the repaired comparator against the real run root**, which
**has not happened**: `verification/runs/ansys_verification/VMFL046-R8/GRADING_VMFL046_R9.log`
**does not exist**, and no `GRADING_VMFL046_R9.json` exists anywhere under
`verification/runs/ansys_verification/`. That is rule 2's own pre-compute test — *name the
artifact that does not exist* — discharged by name rather than asserted.

---

## 0. THE ORDERING THAT IS THIS DOCUMENT'S ENTIRE EVIDENTIARY CONTENT

The repaired comparator was **committed before it was ever run**, deliberately:

| object | value |
|---|---|
| repaired comparator | `cases/ansys_verification/VMFL046-R9-REGRADE/grade_vmfl046_r8_repaired.py` |
| its commit | `e6ad3459` |
| its blob at that commit | `c7c00bbf1fa627ef4cbdda9c81724b0cd62008e5` |
| its blob on disk now | `c7c00bbf1fa627ef4cbdda9c81724b0cd62008e5` — **equal** |
| frozen R8 comparator, untouched | `cases/ansys_verification/VMFL046-R8/grade_vmfl046_r8.py`, blob `f89114bb6ff81f683c6c6718460040cab305a8ce` — **the blob Row #71 pins, unchanged on disk** |
| diff, frozen → repaired | **1 file, 3 insertions, 3 deletions** (`git diff --no-index --stat`), all at `:1099-1101` |

**Nobody has seen a number from these artifacts.** The gate quantity `x_shock` has never been
computed for VMFL046-R8 at any level, by anyone, by any instrument. The repair was therefore
authored, reviewed and committed under the same blindness that a pre-registration is
supposed to guarantee — and this document is frozen **before the first run of the repaired
reader**, not after.

**This ordering is the protection. Section 1 says why it is nearly the ONLY protection.**

---

## 1. THE `§2d.1` DISCLOSURE — AND IT DOES NOT CLAIM FOUR-CONDITION SUPPORT

`VERIFICATION_CHARTER.md` `§2d.1` permits a change on the grading path made after the first
graded solve **only** when all four hold. They are stated here in full, and then each is
answered honestly, including the one that is worth nothing.

> **(1)** it repairs a **DEMONSTRABLE ERROR** rather than a preference;
> **(2)** the error was established by an instrument **INDEPENDENT OF THE HYPOTHESIS** — one
> that grades nothing, such as a near-identity, a guard or a control;
> **(3)** the record **discloses it, names that instrument, and QUANTIFIES WHAT MOVED**;
> **(4)** the **pre-repair values are recorded beside the published ones**.
> Failing any of the four, `§2d` stands.

### (1) DEMONSTRABLE ERROR — HOLDS, and it is not a judgement call

`constant/fvOptions`, frozen in the **same commit** as the comparator, is written in
OpenFOAM's legal single-line brace-inline form:

```
limitT { type limitTemperature; active yes; selectionMode all; min 150; max 2000; }
```

The frozen comparator's `check_pressure_based_config` reads it with three sibling regexes
that **disagree with each other about anchoring**: `:1097`'s `type\s+limitTemperature` is
unanchored and **matches** (so the function proceeds), while `:1099`/`:1100`'s
`^\s*min\s+…` / `^\s*max\s+…` under `re.M` **cannot** match a key preceded by
`selectionMode all; ` on the same physical line, and return `None`. The comparator then
refuses at `:1103`. **The clamp was present, active, and exactly the frozen value
`[150, 2000]`.** This is not "the reader could be nicer"; it is *a frozen comparator that
cannot parse its own frozen case input* — the `ANSYS_VERIFICATION_CHARTER` `§38.1` class
(*"I FROZE A LAUNCHER THAT CANNOT RUN"*) in its reader form.

### (2) INDEPENDENT INSTRUMENT — HOLDS. **THIS IS THE LOAD-BEARING CONDITION AND VERY NEARLY THE ONLY ONE.**

`§2d.1:1944-1947` states condition (2)'s purpose: an error found by something that grades
nothing *"cannot have been selected to move a verdict in a wanted direction, because the
thing that found it does not know which direction that is."* Two such instruments are
named, and **they discharge ONE condition between them — they are not two conditions**.

**Instrument A — OpenFOAM's own `limitTemperature` fvOption reporting.** The solver itself
prints, per time step, the bounds it is enforcing and the count of cells it limited. Across
the three graded logs it printed **1,322,778 report lines**, of which **zero** carried bounds
other than `Tmin = 150` / `Tmax = 2000`, and **zero** carried `LimitedCells ≠ 0`. This
instrument is **inside the solver**, it **grades nothing**, it was written by neither this
lab nor this comparator, it cannot know what `x_shock` is and cannot know which direction
any verdict wants. It establishes independently of the comparator that the clamp the
comparator was looking for **was there, was active, and had exactly the frozen bounds** —
i.e. that the refusal was the reader's fault and not the case's.

**Instrument B — the frozen R8 pre-registration itself, under `§2d.5`.** `§2d.5` rules that
*"THE FROZEN PRE-REGISTRATION IS AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS FOR CONDITION
(2), WHEN AND ONLY WHEN THE DEFECT IS A DEMONSTRABLE DEPARTURE FROM ITS TEXT … The departure
must be exhibited by quotation and by measurement, both."* Both are exhibited here.
**Quotation** — R8's frozen `PREREGISTRATION.md` §4(a) registers that
`check_pressure_based_config` *"pins the PIMPLE `fvSolution` (nOuterCorrectors), the frozen
`fvOptions` clamp bounds [150, 2000] active"*. **Measurement** — executed against the actual
frozen file, the two anchored regexes return `None`, and the identical regexes with `^`
removed return `min = 150`, `max = 2000`, `MATCH: True`. **A registered feature that does not
do what the frozen text says it does** is `§2d.5`'s named shape, and `§2d.5`'s exclusion —
*"IT IS NOT AN INSTRUMENT WHERE THE REGISTRATION IS SILENT"* — does not bite, because the
registration is not silent: it states the pin in terms.

### (3) DISCLOSURE AND QUANTIFICATION — DISCHARGED, but read `§2d.4` before believing it is worth much

`§2d.4` rules that the `§2d.3.3` absence-disclosure shortcut *"keys on the absence of
NUMBERS, never on the absence of a VERDICT. A rung whose solves have COMPLETED has numbers,
whether or not a comparator has consented to grade them. For such a rung, conditions (3) and
(4) BITE IN FULL."* **VMFL046-R8's solves completed at all three levels. This registration
therefore does NOT invoke `§2d.3.3` and claims no shortcut.** `§2d.4` names the exact
circularity this case could be dressed in — *"A comparator that refuses to run is then a
qualification for the shortcut — the instrument's own failure becoming the ground for
relaxing the rule that governs repairing it"* — and this document declines it explicitly.

`§2d.4` also names the discharge that IS available: *"running the comparator over the same
data before and after the repair and publishing both."* That is registered here, and it is
free:

- **BEFORE** — already on disk, produced by the **frozen** comparator over **exactly this
  data**: `verification/runs/ansys_verification/VMFL046-R8/GRADING_VMFL046_R8.log`
  (15 lines) and `GRADING_VMFL046_R8.json` (`grade_rc = 2`, `comparator_blob f89114bb…`),
  graded `2026-09-10T04:25:31Z`.
- **AFTER** — this registration's single act, written to
  `GRADING_VMFL046_R9.log` / `GRADING_VMFL046_R9.json` in the same run root, under a
  distinct `R9` filename so **nothing overwrites the "before"**.
- **PUBLISHED SIDE BY SIDE** — as two register rows, not one: Row #71 stands untouched
  (§5 below).

**WHAT MOVED, quantified, and it is a quantification about an INSTRUMENT and not about
physics:** the frozen reader returned `min = None, max = None` on the real frozen
`fvOptions`; the repaired reader returns `min = 150, max = 2000`. Frozen comparator over
this data: **rc 2, refusal at L1, zero gate quantities computed, zero levels evaluated.**
That is the entire measured content of the "before" side, and it is a statement about a
regex, not about a shock.

### (4) PRE-REPAIR VALUES BESIDE THE PUBLISHED ONES — **SATISFIED VACUOUSLY, AND A VACUOUSLY-SATISFIED CONDITION PROTECTS NOTHING**

**There are no published values.** The refusal fired on **L1**, inside
`check_pressure_based_config` — which `grade()` invokes at `:1215` as **LIMB (a) config** —
**before** `assert_refining_sampler`, `centreline_history`, `registered_window`,
`shock_series`, `check_shock_stands` (LIMB (c)), `check_T_clamp_nonbinding` (LIMB (b)),
`plateau`, the five planted controls A/B/C1/C2/D, the W1 read audit or `roache` had run at
**any** level. `GRADING_VMFL046_R8.log` is **15 lines** and carries the gate's *definition*
(reference 1.250 m, band ±5 %, `DELTA_X`, the frozen clock arithmetic, the probe-length
floor) and **not one measured value**. Row #71 records the same refusal in terms: *"No
`x_shock`, no gate comparison, no Roache triple, no GCI."*

Condition (4) exists to stop a repair from quietly moving a number that has already been
put on the record. **There is no number on the record for it to protect.** It is therefore
satisfied in form and **delivers zero protection in substance**, and this registration
refuses to bank it as evidence.

### ⚠ THE HONEST BOTTOM LINE, STATED BEFORE THE FREEZE AND NOT AFTER

> **THIS REPAIR IS PROTECTED BY ONE CONDITION, NOT FOUR.**
>
> Condition **(2)** — the independent, grades-nothing instrument — is the protection.
> Condition **(1)** is a machine-provable fact that any reader can re-derive in a minute and
> carries no discretion. Condition **(3)** is discharged, but what it quantifies is a
> **regex returning `None` instead of `150`**, not a value that moved. Condition **(4)** is
> **VACUOUS**.
>
> **Standing where condition (4) normally stands is the FREEZE-BEFORE-RUN ORDERING of §0
> and nothing else**: the repaired comparator was committed at `e6ad3459` before it was ever
> run, this registration is frozen before its first run, and **no agent has seen a gate
> quantity from these artifacts**. If that ordering is ever broken — if the repaired reader
> is run against the real run root before the freeze — **this registration is void and the
> re-grade is `NOT A RESULT` on the ordering alone, whatever it prints.**
>
> **Do not read this document as four-condition support. It is not.**

---

## 2. PRECONDITION — THE SELFTEST GAP THAT LET THIS HAPPEN MUST BE CLOSED **BEFORE** THE RE-GRADE RUNS

**`check_pressure_based_config` has ZERO selftest coverage, in the frozen comparator and in
the repaired one as committed.** The comparator's `selftest()` has a section headed
`== LIMB (b): the fvOptions limitTemperature clamp [150,2000] K must be NON-BINDING ==`
(`:1748`), and its seven arms drive `_clamp_check` and `check_T_clamp_nonbinding` — the
**T-field physics side**. **Not one arm constructs an `fvOptions` file and hands it to the
dictionary reader.** The selftest's synthetic `fvOptions` fixtures elsewhere are written in
the one-key-per-line form its own regexes expected, so the selftest proved the regexes'
*logic* against input it generated itself and never made contact with the real frozen
artifact — the `§39.5` lesson.

**That gap is precisely why a defeated regex reached a 590.74-core-min graded run, and
repairing the regex without closing the gap would leave the lab exactly one typo from
repeating it.** Therefore, pre-registered as a **precondition on the freeze, discharged
before the re-grade is invoked**:

**P1.** The **11 guard arms** the supervisor drove against the repaired regex — on which
**none was weakened relative to the frozen regex and two were strictly strengthened** — are
folded into `selftest()` as a **new section exercising `check_pressure_based_config`
itself**. The arm list is the supervisor's and its text is authoritative; this registration
fixes the **requirement and the count**, not the wording. The folded section must cover, at
minimum: brace-inline `fvOptions` parses to `150`/`2000`; one-key-per-line `fvOptions` still
parses to `150`/`2000`; a commented-out `// min 150;` is **not** matched; a substring key
(`Tmin`, `pMinFactor`-class) is **not** mistaken for `min`; wrong bounds **refuse**;
`active no` **refuses**; absent `limitTemperature` **refuses**; absent `constant/fvOptions`
**refuses**.

**P2.** The change is **ADDITIVE ONLY**: **no existing arm is removed, and no existing arm
is weakened**. Baseline is **75 ok / 0 FAILED**; the post-fold total is therefore **≥ 86 ok
/ 0 FAILED**, and the frozen text records the exact post-fold count.

**P3.** The selftest must be **GREEN under `python3` AND under `python3 -O`** — both, 0
FAILED. (`-O` strips `assert`, so a suite whose arms are asserts silently passes under it;
this comparator's arms are explicit `arm(...)` / `must_refuse(...)` calls and must be shown
to survive.)

**P4 — THE DISCLOSURE THAT COMES WITH IT.** Adding arms **changes `--selftest`'s output**.
The property established for the committed repair — *`--selftest` byte-identical frozen vs
repaired, under `python3` and `python3 -O`* — **is deliberately given up at this point**,
in exchange for closing the gap that caused the defect. This is disclosed here, before the
freeze, as a **chosen trade** and not as an accident. The byte-identity property has already
served its purpose: it demonstrated that the 3-line diff touched nothing the comparator
computes. **After the fold-in, that demonstration rests on the committed diff at `e6ad3459`
(3 insertions, 3 deletions, all at `:1099-1101`) and on the record of the byte-identical
selftest at that blob, not on re-running it.**

**P5.** The fold-in changes the comparator's blob. The **grading path is fixed at THIS
registration's commit** and is the **post-fold blob**, whose sha is recorded in the frozen
text and verified `git hash-object` == committed blob immediately before the re-grade runs
(rule 2). The pre-fold blob `c7c00bbf…` is recorded here as the **provenance of the 3-line
repair**, and both shas appear on the artifact's face, labelled as two different objects —
the `§2d.4.3` requirement.

**P6.** The fold-in touches `selftest()` **only**. Any diff line outside `selftest()` other
than the already-committed `:1099-1101` **voids this precondition** and the re-grade does not
run until a new registration covers it.

### P1–P6 DISCHARGED — MEASURED, 2026-09-10, BEFORE THE FREEZE AND BEFORE ANY RE-GRADE

The fold-in is on disk and **uncommitted**; the supervisor's second `§3` check-1 and the
freeze are still owed. Everything below is measured, not asserted.

| | |
|---|---|
| pre-fold blob (committed, `e6ad3459`) | `c7c00bbf1fa627ef4cbdda9c81724b0cd62008e5` |
| **post-fold blob (on disk, the GRADING PATH this registration pins)** | **`660464f94a2afcbf73c5787e992887233b2b3419`** |
| diff pre-fold → post-fold | **1 hunk, `@@ -1783,6 +1783,163 @@`, +157 net** |
| lines REMOVED | **0** — **purely additive** (P2) |
| containment | `selftest()` spans `:1447-1946`; the hunk lies at `:1783-1945` — **wholly inside `selftest()`** (P6) |
| new arms | **15** (P1 requires ≥ 11) |
| **`python3 --selftest`** | **90 ok, 0 FAILED, rc 0** |
| **`python3 -O --selftest`** | **90 ok, 0 FAILED, rc 0** |
| arm lines under `python3` vs `-O` | **identical, all 90** |

**P1's eight required classes, each carried by a named arm:** brace-inline parses;
one-key-per-line still parses; commented-out clamp refuses; commented decoys do not hijack
live keys; substring keys (`Tmin`/`Tmax`) refuse; `pMinFactor`/`pMaxFactor` neighbours are
not read as the clamp; wrong bounds refuse; `active no` refuses; absent `limitTemperature`
refuses; absent `fvOptions` refuses. Four further arms cover the surrounding plumbing that
also had no coverage (absent `fvSolution`, no `PIMPLE{ nOuterCorrectors }`, a log with no
PIMPLE iteration), and one arm is the machine-checked **non-weakening proof**: over six
fixtures, the repaired pattern matches wherever the frozen anchored pattern did, with the
same captured value — **0 weakened**.

**ARM 1 IS CONTACT WITH THE REAL FROZEN ARTIFACT, NOT A SYNTHETIC FIXTURE.** It reads
`cases/ansys_verification/VMFL046-R8/case/constant/fvOptions` — 598 bytes, blob
`cc81891fd7445e2777a245e16baf0c9b829ec299`, the actual file the frozen reader could not
parse — resolved relative to the comparator's own `__file__`, and **fails rather than skips**
if that file is absent. This is the `§39.5` lesson discharged directly: the gap was never
that the regexes' logic was untested, it was that the suite never touched the real artifact.

### ⚠ THE MUTATION CONTROL — because a new arm that cannot go red proves nothing (rule 3's principle)

A suite that passes proves nothing until it is shown able to **fail**. Two copies were built
in a scratch tree, with the real `fvOptions` placed as a sibling so `__file__` resolution
holds: a **CONTROL** (the post-fold comparator, unmodified) and a **MUTANT** (identical
except the three lines at `:1099-1101` reverted to the frozen `^`-anchored regexes — i.e.
the row #71 defect put back).

| | result |
|---|---|
| CONTROL | **90 ok, 0 FAILED, rc 0** |
| **MUTANT (row #71 defect restored)** | **86 ok, 4 FAILED, rc 1** |

The four arms that go red under the mutant are the row-#71 class exactly — **the real frozen
`fvOptions` arm, the brace-inline arm, the commented-decoy arm and the `pMinFactor` arm** —
each reported as `UNEXPECTED REFUSAL(2)`. **The remaining 86 arms stay green under the
mutant**, which is the part that matters: the new section is not a blanket that reddens on
any change, and the one-key-per-line arm staying green under the mutant independently
confirms that the frozen regexes really did read that form, so **non-weakening is a measured
property and not a claim**.

> **THE MUTATION CONTROL IS THE ANSWER TO "WOULD THIS HAVE CAUGHT ROW #71?" AND THE ANSWER
> IS YES, MEASURED: with the defect present the suite reports 4 FAILED and exits 1, where
> the frozen suite reported 75 ok / 0 FAILED and exited 0.**

**One defect in the fold-in was found BY the mutation control and repaired before this was
written**, and it is recorded rather than tidied: the pass-side arms originally called
`check_pressure_based_config` directly, so under the mutant the first unexpected refusal
raised `SystemExit(2)` and **aborted the suite** instead of reporting a `[FAIL]` — later arms
never ran. A nested `must_parse()` helper (the pass-side counterpart of the existing
`must_refuse()`) now catches `SystemExit` and reports it as a failed arm. **An aborting
selftest is still not green and P3 would have caught it, but it would have hidden the other
three failures.**

**Honest correction to a stated fact.** `--selftest`'s raw stdout is **not** byte-identical
between `python3` and `python3 -O`, and never was — the comparator's refusal messages embed
`tempfile.mkdtemp()` paths, whose suffixes are random per invocation. That is **pre-existing
behaviour of the frozen comparator, not introduced by this fold-in.** Masking those suffixes,
the two streams are identical; the **90 arm lines are identical verbatim**. P3 asks for
**green under both**, which is measured above and holds.

---

## 3. THE FROZEN PREDICTION — CARRIED FROM R8 BYTE-IDENTICAL. **NOTHING ABOUT THE GATE MOVES.**

This is a **reader repair, not a re-gate.** Every row below is quoted from R8's frozen
`PREREGISTRATION.md` §3 and is **unchanged**:

| quantity | value | source |
|---|---|---|
| gate quantity | **`x_shock`** | R8 §3 |
| primary reference | **1.250 m** (F. M. White, *Fluid Mechanics*, quasi-1D) | R8 §3 |
| band `SHOCK_TOL` | **±5 %**, half-width **±0.0625 m** → band **[1.1875, 1.3125] m** | R8 §3 |
| reader | **INTERPOLATING last downward Mach = 1 crossing** (D3) | R8 §3 |
| registered window | **t ∈ (0.064, 0.080] s** — 33 of the 160 written samples (W1) | R8 §3 |
| plateau `DELTA_X` | **6.250e-04 m** — ptp over two adjacent `W = endTime/10` windows **AND** their mean drift | R8 §3 |
| `endTime` | **0.080 s** | R8 §3 |
| sampler `SAMPLE_DT` | **5.0e-04 s** (160 samples) | R8 §3 |
| grid triple, r = 2 | **L1 (40/120/20) → L2 (80/240/40) → L3 (160/480/80)** | R8 §3 |
| Roache | rule-5 ordering; **GCI at Fs = 1.25** | R8 §5, CLAUDE.md rule 5 |
| secondary, demote-only | observed order p ∉ [0.5, 2.5], or fine GCI > 0.15 → a would-be reach becomes `GATE FAIL` | R8 §5 |
| probe-length floor (W2) | 0.25 of the graded clock (L1 1.0000 / L2 0.9148 / L3 0.9921) | R8 §6 |
| frozen clock arithmetic (W3) | 160 samples, 17 per window, 33 distinct, 5.0 steps per sample | R8 §3 |

**No gate constant, band, tolerance, window, reference value, plateau threshold, triple,
ordering rule or cap is created, moved, widened, narrowed or retired by this registration.
Zero.** The three changed lines at `:1099-1101` are inside a **configuration-pinning
refusal check** and touch nothing the comparator computes, compares or thresholds. It has
already been established, and is relied on here rather than re-derived: **no anchored regex
lies on the `x_shock`, plateau or Roache path** — `read_centreline_raw` uses `str.split()`,
and the gate functions contain no regex at all.

**The five planted controls A / B / C1 / C2 / D and the W1 read audit are unchanged and
remain armed** (standing rule 3). They fire against **this run's real data for the first
time** in the re-grade — see §7.

---

## 4. THE OUTCOME MAP — PRE-REGISTERED BEFORE ANY NUMBER IS SEEN

The single act is one invocation:

```
python3 <post-fold comparator> /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL046-R8
```

| exit code | meaning | **verdict** |
|---|---|---|
| **0** | every limb passed; the triple is `CONVERGING`; `x_shock` lies inside **[1.1875, 1.3125] m**; no demote-only secondary fired | **`GATE REACHED`** |
| **1** | a graded limb resolved against the run — **`GATE FAIL`** if the triple is `CONVERGING` and the value is outside the band, or a demote-only secondary fired; **`NOT A RESULT`** if the triple is not `CONVERGING` or a level did not plateau. **The printed limb decides which, and the log is the authority — not this table and not any reading of it.** | **`GATE FAIL` or `NOT A RESULT`** |
| **2** | the comparator **REFUSED** — incomplete run, unreadable artifact, a planted control not seen, an audit violation, a guard tripped | **`NOT A RESULT`** |

**RULE 5 IS ABSOLUTE AND IS RESTATED HERE SO IT CANNOT BE READ AROUND: a row whose grid
triple is not `CONVERGING` is `NOT A RESULT`, WHATEVER ITS VALUE** — including a value that
lands dead on 1.250 m. The gate can only turn a would-be `GATE REACHED` or `GATE FAIL`
**into** `NOT A RESULT`, never the reverse. **A GCI is never quoted when the three values are
not monotone.** `DIVERGENT`, `STAGNANT`, `OSCILLATORY` and `EXACT` are each `NOT A RESULT`,
with the value, both triples and the orders printed beside them.

**THE CEILING IS `GATE REACHED`. `PASS` IS UNREACHABLE, ON TWO INDEPENDENT GROUNDS:**

1. **The comparator contains no code path that prints `PASS`.** R8's frozen §5 states it,
   and the repair did not add one — the 3-line diff is inside a refusal check.
2. **`ANSYS_VERIFICATION_CHARTER` `§24.4` independently re-caps this case.** `§23.3` lifted
   VMFL046's `GATE REACHED` cap on an **enumerated-channel** model-form bound
   (`dx_shock/x ≤ 0.63 %`). `§24.4` rules such a bound **UNVALIDATED** unless it is (i) a
   total-discrepancy bound, (ii) validated against a measured comparison of the same two
   models, or (iii) carries a frozen, falsifiable completeness argument — and records that
   `§23.3`'s bound was **refuted by the run by 20.5×**. *"An enumerated-channel bound with
   none of these is UNVALIDATED … IT DOES NOT LIFT A CAP."* The reference is an **inviscid
   quasi-1D analytical** shock location and the run is a **viscous 2-D Navier-Stokes**
   solve; model-sameness is DIFFERENT and the cap stands.

**No `PASS` may be recorded for VMFL046-R9-REGRADE under any outcome. A `GATE REACHED` here
is a credential; it is not a `PASS` and must never be relabelled as one.**

**Instrument-fault classification, pre-registered because rc 1 is otherwise ambiguous:** an
exit code **other than 0, 1 or 2**, or an **rc 1 accompanied by a Python traceback rather
than a printed limb verdict**, is an **INSTRUMENT FAULT** and is **`NOT A RESULT`** — never
`GATE FAIL`. A `GATE FAIL` requires the comparator to have **reached the gate and resolved
it against the run**; a crashed reader has resolved nothing.

---

## 5. WHAT THIS RE-GRADE MAY AND MAY NOT DO TO ROW #71

> **ROW #71 STAYS `NOT A RESULT`. IT IS NOT AMENDED, NOT RELABELLED, NOT SUPERSEDED, NOT
> STRUCK, AND NOT ONE BYTE OF IT IS REWRITTEN.**

Row #71 is a **true record of what the frozen instrument did to this data**: it refused, and
under the rule that a sound run with an unreadable instrument yields no number, that is
`NOT A RESULT`. **That remains true after the repair.** A repaired reader does not make the
frozen reader's refusal retrospectively wrong; it makes a **second, differently-instrumented
reading** possible.

The re-grade therefore lands as a **NEW register row** which:

- cites **this registration** by commit and **the post-fold comparator blob** as its grading
  path, and **the pre-fold blob `c7c00bbf…`** as the repair's provenance, the two labelled as
  different objects (`§2d.4.3`);
- cites **Row #71** explicitly, and states that **both readings stand side by side** — the
  frozen reader's refusal and the repaired reader's outcome — which is the `§2d.4`
  before/after publication of §1(3), discharged as a **register fact** rather than a claim;
- carries the `§2d.1` disclosure of §1 **including the statement that condition (4) is
  vacuous and the repair rests on one condition, not four**;
- states in its own "what this row refuses to claim" section that **the underlying solve is
  the SAME solve as Row #71's** — one run, two readings — so that nobody can later count
  590.74 core-min twice or read the pair as two independent confirmations.

**The row number is derived at commit from the register's tail — the MAXIMUM EXISTING
NUMBER, never a count (rule 11's arithmetic).** At drafting time the maximum existing
`## Row #` in `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` is **74** while
the count of such headings is **14**; those are three different figures and the maximum is
the one that governs. The `.tsv` is a **derived view and lags** (its tail is row 39) and is
never the source of the next number.

---

## 6. COST (rule 12) — GRADING ONLY

**SOLVER COMPUTE: 0 core-min. $0.00.** No mesh, no solver, no field written.

**The comparator invocation, honestly:**

- **Measured basis:** the **frozen** comparator's invocation over this same run root took
  **10 s wall, single core** (`AUTOGRADE_WATCH_STATE.txt`: grading started
  `2026-09-10T04:25:21Z`, `grade DONE` `2026-09-10T04:25:31Z`) = **0.167 core-min**. That
  10 s already included L1's full strict-completion pass, which reads L1's **127.7 MB**
  `log.rhoPimpleFoam` in one `open().read()` and runs three `re.findall` passes over it.
- **What the re-grade adds:** L2's **265.3 MB** and L3's **519.1 MB** logs read the same way,
  plus **480 centreline sample files** (160 written per level; the W1 audit restricts the
  reader to the **33** in the registered window per level, so ~99 opened), plus three
  `endTime` `T` fields and the five planted controls.
- **Point estimate: ~3 core-min** (single core; ~180 s wall). **Cap: 30 core-min** — ten
  times the estimate, set deliberately wide because the box is **saturated at drafting time
  (load average 29.6 on 16 cores)** and a single-core reader on a loaded box inflates in
  wall and therefore in core-minutes. **An overrun STOPS the run** (rule 12); it does not
  get a new budget, and a stopped re-grade is `NOT A RESULT`, not a retry with a bigger cap.
- **`cost_basis`:** core-minutes **MEASURED** from the wrapper's own clock; dollars derived
  at **c7a.4xlarge $0.0513/core-h, owner-stated — reported-by-owner, NOT measured** (the box
  cannot read its own billing, `COMPUTE_BUDGET_CHARTER` §5). At the point estimate the
  derived figure is **≈ $0.0026**.

> **THE 590.7413 core-min OF THE UNDERLYING RUN IS ALREADY SPENT AND ALREADY RECORDED AT
> ROW #71, AND IS NOT RE-CHARGED HERE.** Row #71 also names it, separately and unabsorbed,
> as **WASTE** (`COMPUTE_BUDGET_CHARTER` §6): the entire 590.7413 core-min yielded no
> gradeable answer, through an instrument defect and not through contention or a bad solve.
> **This re-grade does not erase that waste and must not be presented as recovering it.**
> What it can do is extract an answer from artifacts already paid for — which is why it is
> worth doing at ~3 core-min, and why the cost of NOT doing it is 590.74 core-min of
> re-solve.

**Estimate-versus-actual calibration is OWED** at completion (rule 12, Sanaa 2026-08-23): a
row in `docs/COST_CALIBRATION.md` stating actual/predicted for **this grading act** (against
the ~3 core-min estimate), separately from Row #71's own solve calibration
(**590.7413 measured vs ~398 estimated = 1.484×**, already recorded).

---

## 7. FAILURE MODES — INCLUDING THE ONE NOBODY CAN RULE OUT

**THE CENTRAL HONEST FACT: the refusal fired at L1 inside LIMB (a), which is EARLIER in
`grade()` than the limb Row #71's prose names.** `grade()`'s order per level is
`check_completion` → **`check_pressure_based_config` (LIMB (a), `:1215`)** →
`assert_refining_sampler` → `centreline_history` → `registered_window` → `shock_series` →
**`check_shock_stands` (LIMB (c), `:1224`)** → **`check_T_clamp_nonbinding` (LIMB (b),
`:1225`)** → `plateau` → plants A/B/C1/C2/D → W1 audit → `roache`. Row #71 and the brief
describe the refusal as LIMB (b) because the failing check pins the clamp that **LIMB (b)
later proves non-binding** — but the refusing call is LIMB (a)'s. **This makes the exposure
larger, not smaller**, and is stated here rather than left to be noticed.

**What has NEVER been exercised against this run's data, at any level:**

| never run against this data | status |
|---|---|
| **LIMB (b)** `check_T_clamp_nonbinding` — the clamp-non-binding proof | **UNTESTED** |
| **LIMB (c)** `check_shock_stands` — washout / shock-stand guard | **UNTESTED** |
| `assert_refining_sampler`, `centreline_history`, `registered_window`, `shock_series` | **UNTESTED** |
| `plateau` — ptp **and** mean-drift ≤ `DELTA_X`, per level | **UNTESTED** |
| planted controls **A / B / C1 / C2 / D** (standing rule 3) | **UNTESTED against real data** |
| W1 read audit | **UNTESTED against real data** |
| **`roache`** — the r = 2 triple and its state | **UNTESTED** |
| `check_completion` at **L2** and **L3** | **UNTESTED** — the loop refused at L1 before reaching them |

Only **L1's `check_completion`** has actually passed against this data (it precedes the
refusing call), so L1's rc, `End` line, `ExecutionTime`/`Time` count equality, last-time,
strict monotonicity and age guard are the **only** rule-4 arithmetic this run has survived.

**Pre-registered as EXPECTED AND LEGITIMATE OUTCOMES, not disappointments:**

1. **The re-grade refuses again at a LATER limb.** LIMB (b), LIMB (c), the sampler assert,
   the plateau, a planted control or the W1 audit may each refuse. **That is `NOT A RESULT`
   and it is a correct outcome**, not a second instrument failure — a guard that fires is a
   guard working. The repair was to **one dictionary reader**; it makes no claim about any
   other limb.
2. **The triple comes back `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT`.** → **`NOT A
   RESULT`**, value and both triples printed. **Pre-registered as a live possibility.**
   VMFL046's own history at `§24.5-§24.6` records a triple whose shock location moved
   **monotonically away** from the analytical reference under refinement
   (1.25763 → 1.19260 → 1.15258). **⚠ THOSE THREE NUMBERS ARE A PRIOR FROM A DIFFERENT RUNG
   OF THIS CASE — register row #54, already published in `ANSYS_VERIFICATION_CHARTER` §24.5
   — AND THEY GATE NOTHING HERE.** They are cited to set the **expectation of difficulty**,
   not to predict this rung's value: the gate (1.250 m, ±5 %) is carried byte-identical from
   R8 and was frozen long before those values existed, and this registration moves no gate
   object. **No reader may treat them as a prediction of VMFL046-R8's `x_shock`, which no
   instrument has computed.** They are a different rung, but the same case and the same reference,
   and this lab has already learned here that *"an agreement obtained at the coarsest level
   is the least trustworthy number in the set, and it is the one that looks most like
   success"* (`§24.6`). **A `GATE FAIL` on this rung would be unsurprising and would be
   recorded as a finding, not softened.**
3. **A level does not plateau** within `DELTA_X = 6.250e-04 m` → **`NOT A RESULT`** under
   rule 5's first clause, before any band comparison.
4. **L2 or L3 fails strict completion** despite `rc 0` and an `End` line — e.g. an
   `ExecutionTime`/`Time` count mismatch or a non-monotone time sequence in a
   half-gigabyte log nothing has yet parsed. → **`NOT A RESULT`**. *Partially de-risked:*
   the **age guard** was checked by `stat` (no comparator run, no gate quantity read) and
   **holds at all three levels** — every level's `0.08/T` is newer than its own `0/T`
   (L1 18:38:55 > 18:31:31; L2 19:34:43 > 18:38:55; L3 2026-09-10 04:24:43 > 19:34:43), and
   `0.08/` carries `T U p phi rho uniform` at every level.
5. **MemoryError or an OS kill** reading L3's 519.1 MB log into one Python string plus three
   `re.findall` passes — a path the frozen comparator never reached. 21 GB was available at
   drafting time so this is unlikely, but on a saturated box it is not impossible. → an
   **INSTRUMENT FAULT**, `NOT A RESULT` per §4, **never** `GATE FAIL`.
6. **An artifact has been touched since 2026-09-10T04:25:31Z.** The age guard and the W1
   audit would catch a rewrite, but a **deletion** would refuse outright. Nothing in this
   territory is authorised to touch the R8 run root, and the freeze check below re-asserts
   it.
7. **The `§2d.1` ground is rejected on review.** If the supervisor or the verification team
   rules that condition (2) is not discharged, or that the freeze-before-run ordering does
   not carry the weight §1 places on it, **the re-grade does not run** and Row #71 stands
   alone. **This registration asks for a ruling; it does not assume one.**

**AND THE ONE NOBODY CAN RULE OUT:** because the physics limbs have never touched this data,
**no one — not this lane, not the supervisor, not the comparator's author — knows whether
these 590.74 core-min contain a gradeable answer at all.** The repair makes the reader able
to read the clamp. It does not make the run gradeable, and this registration **does not
predict that it will be.** The prediction registered here is the **gate and the outcome map**,
not the outcome.

---

## 8. FREEZE CONDITIONS (rule 2)

Freezable when, and only when, all of these hold:

1. **§3 check-1 diff-read, personally by the supervisor, read as a diff:** the total diff
   frozen → post-fold is (a) the 3 lines at `:1099-1101` already committed at `e6ad3459`,
   and (b) the additive `selftest()` fold-in of §2 — **and nothing else**.
2. **P1–P6 of §2 discharged**, with the post-fold arm count and both `python3` /
   `python3 -O` results recorded **in the frozen text** before freezing.
3. **Grading path pinned:** the post-fold blob is
   **`660464f94a2afcbf73c5787e992887233b2b3419`** (measured on disk, §2). At freeze its
   `git hash-object` **==** its committed blob, and this is re-verified immediately before
   the re-grade runs (rule 2's *"the frozen file IS the file that ran"*). **It is
   uncommitted at the time of writing** — the fold-in is on disk only.
4. **The frozen R8 comparator is untouched:**
   `cases/ansys_verification/VMFL046-R8/grade_vmfl046_r8.py` still hashes to
   `f89114bb6ff81f683c6c6718460040cab305a8ce`. **It is never edited** (rule 6).
5. **The "before" artifacts are intact and will not be overwritten:**
   `GRADING_VMFL046_R8.log` / `.json` present; the re-grade writes to the distinct `R9`
   filenames.
6. **No `R9` grading artifact exists** —
   `verification/runs/ansys_verification/VMFL046-R8/GRADING_VMFL046_R9.{log,json}` **absent
   at freeze**, which is this registration's pre-compute test (§0).
7. **The run root is unmodified since `2026-09-10T04:25:31Z`.**
8. **The `§2d.1` ground of §1 is accepted** by the supervisor, on the record, **as a
   one-condition repair** — not as four-condition support.

After the first invocation of the post-fold comparator against the real run root, this
document is closed: changes land only as dated addenda that cannot alter a gate, threshold,
cap or label, and the original text is struck, never rewritten.

---

## 9. WHAT THIS REGISTRATION DOES NOT DO

| | |
|---|---|
| gates created / moved / retired | **0** |
| bands, thresholds, tolerances moved | **0** |
| caps lifted | **0** — `GATE REACHED` ceiling re-affirmed on two grounds (§4) |
| labels changed | **0** — Row #71 stays `NOT A RESULT` |
| register bytes rewritten | **0** — the re-grade **adds** a row |
| solver compute authorised | **0 core-min** — **no run may be launched on the strength of this document** |
| frozen R8 files edited | **0** |
| `§2d.3.3` absence shortcut invoked | **none — expressly declined (§1(3))** |
| `PASS` reachable | **no, under any outcome** |
