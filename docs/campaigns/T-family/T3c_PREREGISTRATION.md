# T3c — successor to the T3 R-ladder grading path: the rule-3 planted-zero control moved off an absolute last-ULP tolerance onto the relative predicate three frozen T-family siblings already use

> ~~**STATUS: FROZEN BY COMMIT. NOT ENQUEUED. NO COMPARATOR CODE EXISTS YET —
> BY DESIGN.**~~
>
> **STRUCK 2026-09-03, AND THE STRIKING IS A CONDITION OF LANDING THIS DOCUMENT
> (`VERIFICATION_CHARTER.md` §2d.11.3).** The struck line is left legible rather
> than deleted, per rule 2: *originals are struck, never rewritten.*
>
> **THE STRUCK LINE WAS FALSE ON THE DAY IT WAS WRITTEN.** It was drafted
> 2026-08-30 and asserted this document's own freeze while the document sat in
> **zero commits** — `git log` against it returned nothing and `git ls-files`
> did not know it. Verification recorded it as a rule-2 specimen worth naming:
> not the ordinary failure of a *missing* pre-registration, but one that
> **asserts its own freeze**, which is exactly what would satisfy a reader who
> checks the document instead of the repository. It is struck because committing
> it unchanged would make it **true by accident**, and no later reader could
> distinguish a claim that was verified from one that history happened to
> vindicate.
>
> **STATUS AS LANDED, 2026-09-03: FROZEN BY THE COMMIT THAT CARRIES THIS
> AMENDMENT, AND NOT ONE MINUTE EARLIER. NOT ENQUEUED. NOT GRADED.** The
> comparator code now exists and is committed alongside this document —
> `analyse_t3c.py` and `control_t3c_p2.py`, witnessed by full sha256 in
> AMENDMENT 1 §A1.6. **No row of T3c has been graded and none may be until
> `verification-supervisor` confirms the question in §A1.7.**
> This document is frozen by the commit that first lands it, per standing rule 2:
> the gate, threshold, cap and label are committed BEFORE any compute and, here,
> before the code that will implement them. Dropping T3c into the re-grade queue
> is the heat-transfer supervisor's decision and is explicitly withheld from the
> lane that wrote this. Nothing here is sent anywhere (rule 7).
>
> **THE OPENING DISCLOSURE IS THE OPPOSITE OF T15b's, AND IT IS THIS DOCUMENT'S
> STRONGEST ASSET — NO GRADED QUANTITY OF `R_ff` HAS BEEN MEASURED BY ANYONE.**
> The frozen grader refused at the rule-3 planted-zero control **before** any
> graded quantity was computed. `gate_t3_rff.json` was never written. No person
> and no agent in this lab has seen `R_ff`'s `x_peak/H`, its `St_peak`, its level
> values, its refinement ratios as graded, its observed order `p` or its GCI, and
> **no one knows whether P1 or P2 is right.** This tolerance ruling can therefore
> still be made **GENUINELY BLIND TO THE ANSWER** — a position T15b explicitly
> could not occupy and had to disclose away. **§1 registers that blindness as a
> BINDING CONDITION, not as a remark.**
>
> **This document does not edit, amend or supersede `analyse_t3.py` or
> `analyse_t3_rff.py`.** Both are frozen and both are post-compute; rule 2 bars a
> gate change after first compute and rule 6 bars editing a frozen file at all.
> Verified by hash in §2.4. The repair lives here, in a successor, or nowhere.

Drafted 2026-08-30 by a heat-transfer `lab-lane` on the supervisor's diagnosis
brief. **Every number below was re-derived by this lane from the artifact named
beside it**, not transcribed from the brief; §2.6 boards the three places where
this lane's measurement is sharper than, or differs from, the figure it was
handed. Repository HEAD at drafting: `52632a2dd3cc78fccf0855684dffc386f79dc701`.

---

## 0. Why a successor exists

`R_ff` completed cleanly. `verification/runs/T-family/T3_runs/DONE.R_ff` was
written 2026-08-30T22:42:41Z under the frozen `mark_done_t3_rff.py` (blob
`9436399f`), all six rule-4 clauses asserted, `rc=0`, `capped=no`, 26 757.067
core-minutes spent. **The rung is nevertheless ungraded on every row**: the
frozen grader refuses (exit 2) inside its own rule-3 planted-zero control,
before any row is printed.

The refusal is recorded verbatim at
`verification/runs/T-family/T3_runs/T3_R_FF_GRADE_OUTPUT_20260830T224307Z.txt`
(337 bytes, two lines, read whole by this lane). It contains **no `x_peak/H`
row, no `St_peak` row, no triple classification and no GCI** — the file's entire
content is the control dictionary and the refusal line.

The refusing arm is `verification/runs/T-family/T3_runs/analyse_t3.py:327`:

```
        return dict(passed=(seen >= PLANT - 1e-15), planted=PLANT,
```

with `PLANT = 1.234e-03` K declared at `analyse_t3.py:81`, applied to a
temperature field whose values are ~300 K.

**The defect is in the predicate, not in the reader.** The reader is not blind
and this must be said first, because a refusing planted-zero control normally
means the instrument is broken and that reading would be wrong here. The
refusal artifact itself records `reader_max_change =
1.2339999996129336e-03` against an un-planted baseline of **4.910338816443982e-06 K**
on the same level (re-derived in §2.2) — the reader saw the plant at **251.31×**
the un-planted signal, and the plant landed on disk (`read_back_delta =
1.2340000000108375e-03`). **The instrument passed its own test and the
arithmetic of the test threw the result away.**

**The defect is in the registered predicate, not only in the code.** That is why
no addendum to `T3_R_FF_PREREGISTRATION.md` can reach it and a successor is
required. The parent registration describes the control's negative arm at
`T3_R_FF_PREREGISTRATION.md:361` as *"(identical checkpoints → change 0)"* —
the tolerance is registered prose, and §4 shows that phrase is exactly where the
defect hid.

---

## 1. THE BLINDNESS CLAUSE — REGISTERED, BINDING, AND THE MOST VALUABLE THING THIS DOCUMENT HAS

**REGISTERED CONDITION B-1, binding on every agent of this lab.**

> **No graded quantity of `R_ff` may be measured, computed, printed, inspected or
> estimated until the tolerance question registered in this document has been
> ruled on.** The quantities covered are, exhaustively: `x_peak/H(R_ff)`;
> `St_peak(R_ff)`; `St(10H)` and `St(20H)` on `R_ff`; any level value entering the
> `(R_m, R_f, R_ff)` triple; the triple's classification; the observed order `p`;
> the GCI; and `delta_99/H` on `R_ff`. Reading `R_ff`'s field files for any of
> these purposes is covered. **The prohibition is on measurement, not on
> publication** — a quantity measured and then withheld has already destroyed
> what this clause protects.

**Why it is registered rather than merely observed.** §10's condition (2) — the
§2d.1 requirement that the repair be established by an instrument independent of
the hypothesis — is the condition on which repair registrations are normally
weakest, and it is weak precisely because the drafter usually already knows which
way the verdict would move. T15b had to open by conceding exactly that
(`T15b_PREREGISTRATION.md`, opening disclosure: *"THE GRADED VALUE OF ROW S1 WAS
ALREADY KNOWN WHEN THIS DOCUMENT WAS DRAFTED"*, `S1 = 1.9909386169553251e-04`).
**T3c does not have to concede it, and that is worth more than any argument this
document could make in its place.** No one can be steered toward an answer nobody
has seen.

**REGISTERED CONSEQUENCE B-2.** If any `R_ff` graded quantity is measured before
the ruling, **the blindness is destroyed and cannot be restored**, this document
must be amended at its head to disclose exactly which quantity was measured, by
whom and when, and **the repair loses its strongest defence** — falling back to
the ordinary §2d.1 argument on the floating-point identity alone. The repair may
still be sound; it will no longer be blind, and the two are not the same claim.

**WHAT THIS LANE MEASURED, AND WHAT IT DID NOT — stated so B-1 is auditable
rather than asserted.**

| measured by this lane | level | is it an `R_ff` graded quantity? |
| --- | --- | --- |
| first internal value of `T` at 76 000 and 78 000 | **`R_f`** | no — a convergence diagnostic |
| `max\|T(78000) − T(76000)\|` over 235 520 cells | **`R_f`** | no — the un-planted control baseline |
| first internal value of `T` at 34 000 and 36 000 | **`R_m`** | no |
| `max\|T(36000) − T(34000)\|` over 92 160 cells | **`R_m`** | no |
| IEEE-754 spacing, binade constants, predicate arithmetic | none — pure arithmetic | no |

**No file under `verification/runs/T-family/T3_runs/R_ff/` was opened by this
lane for any purpose.** The `R_ff` figures quoted in §12 (core-minutes, wall
seconds, cell count) come from `STATUS.R_ff` and the C-211 cost row, are
**infrastructure fields under L-342**, and are not graded quantities.

---

## 2. The defect, measured

### 2.1 The predicate and the constant

`analyse_t3.py:81`  `PLANT = 1.234e-03` K
`analyse_t3.py:327` `passed = (seen >= PLANT - 1e-15)`

The slack is an **absolute** `1e-15` K on a field whose values are ~300 K.

| quantity | value | how re-derived |
| --- | --- | --- |
| `ULP(300.0)` | **5.684341886080802e-14 K** | `numpy.spacing(300.0)` |
| the `1e-15` slack, in ULP of the field | **1 / 56.843** | `5.684341886080802e-14 / 1e-15 = 56.843` |

**The slack is 56.84× BELOW one ULP of the field it is applied to.** A tolerance
finer than the representable spacing of the numbers it compares is not a
tolerance; it is a demand for an exact relation between quantities that cannot be
exactly related.

*(Boarded correction: an earlier lane wrote ~66× using `eps × 300 =
6.661338147750939e-14`. That formula gives the spacing of the **top** of the
binade, not of 300.0. `numpy.spacing(300.0)` is the correct spacing and the
correct ratio is **56.843×**. This lane re-derived both and reports the
supervisor's 56.8× figure as confirmed.)*

### 2.2 The two checkpoints, read from disk

`verification/runs/T-family/T3_runs/R_f/{76000,78000}/T`, 235 520 internal
values each, parsed by this lane directly from the `internalField nonuniform
List<scalar>` block:

| quantity | value |
| --- | --- |
| first internal value, 76 000 (`a`) | **299.9999999999993** |
| first internal value, 78 000 (`b`) | **299.9999999999997** |
| drift `b − a` | **+3.979039320256561e-13 K** |
| drift in ULP | **exactly +7.00 ULP** |
| un-planted `max\|T(78000) − T(76000)\|` | **4.910338816443982e-06 K** |

### 2.3 The identity that decides the verdict

`plant_into_T` (`analyse_t3.py:288-304`) adds `PLANT` to the **first internal
value only** and writes `repr(before + PLANT)`. The reader then takes the maximum
absolute difference across all cells. Because `PLANT` = 1.234e-03 K exceeds the
whole field's real drift (4.910e-06 K) by 251.31×, **the maximum is attained at
cell 0 and the control's verdict is decided by that single cell.**

Writing `c` for the rounding of the plant addition inside the binade,

```
    c    ≡ (a + PLANT) − a − PLANT
    seen  = (a + PLANT) − b  =  PLANT + c − (b − a)
```

| term | value |
| --- | --- |
| `c` on binade `[256, 512)` | **+1.0837468075730605e-14 K = +0.19065 ULP** |
| `b − a` (drift) | **+3.979039320256561e-13 K = +7.00 ULP** |
| `seen − PLANT` predicted by the identity | **−3.870664639499255e-13 K** |
| `seen − PLANT` **measured**, from the refusal artifact | **−3.870664639499255e-13 K** |

**The identity reproduces the measured shortfall to the last bit.** Independently,
this lane's own reimplementation of the reader returned `seen =
0.0012339999996129336`, **bit-identical to the `reader_max_change` in the frozen
grader's refusal artifact** — the re-derivation is faithful to the frozen code,
not merely close to it.

### 2.4 The parent files are UNTOUCHED — verified by hash, not asserted

`git hash-object <path>` against `git rev-parse HEAD:<path>`. The shared index is
stale and `git status` / `git diff HEAD` are unreliable at drafting time, so the
comparison is against the **HEAD blob**, never against the index.

| file | worktree blob | HEAD blob | identical |
| --- | --- | --- | --- |
| `verification/runs/T-family/T3_runs/analyse_t3.py` | `d5e4a9eb1aac25d73c88f077c3fb95a549ae9bfb` | `d5e4a9eb1aac25d73c88f077c3fb95a549ae9bfb` | **YES** |
| `verification/runs/T-family/T3_runs/analyse_t3_rff.py` | `44e3e2b8038b9274bc7dcbd96ecdfb29e4b43899` | `44e3e2b8038b9274bc7dcbd96ecdfb29e4b43899` | **YES** |
| `docs/campaigns/T-family/T3_R_FF_PREREGISTRATION.md` | `35d670168d781d5d3f49919d1fe2ae7429ff2759` | `35d670168d781d5d3f49919d1fe2ae7429ff2759` | **YES** |

`analyse_t3_rff.py:30` imports the parent — `import analyse_t3 as A  # frozen
comparator, HEAD blob d5e4a9eb -- imported, not edited` — and calls
`A.planted_zero_control` at line 82. **The defect is inherited by import, which
is why repairing it requires a new module and not a patch.**

### 2.5 The control that proves the mechanism — `R_m` versus `R_f`

The two levels differ in **nothing** relevant to this control except the drift at
cell 0. Both baselines sit in binade `[256, 512)`, so both carry the identical
`c = +1.0837468075730605e-14 K`.

| | `R_m` (34 000 → 36 000) | `R_f` (76 000 → 78 000) |
| --- | --- | --- |
| cells | 92 160 | 235 520 |
| first internal `a` | 299.9999999999999 | 299.9999999999993 |
| first internal `b` | 299.9999999999999 | 299.9999999999997 |
| **drift `b − a`** | **0.0 K = 0.00 ULP** | **+3.979039320256561e-13 K = +7.00 ULP** |
| `c` | +1.0837468075730605e-14 | +1.0837468075730605e-14 |
| `seen` | 0.0012340000000108375 | 0.0012339999996129336 |
| `seen − PLANT` | **+1.0837468075730605e-14** | **−3.870664639499255e-13** |
| **`analyse_t3.py:327` verdict** | **PASSES** | **REFUSES** |
| un-planted baseline (the real signal) | 7.875202e-07 K | 4.910338816443982e-06 K |

**This is the decisive measurement of this document.** The control passed on one
level and refused on the other **for one reason and one reason only: cell 0's
drift was exactly zero on `R_m` and +7 ULP upward on `R_f`.** Both levels'
readers saw the plant. Both readers were sound. One was credited and one was not,
on a quantity carrying no physical information.

### 2.6 Differences between this lane's measurements and the brief it was handed — BOARDED, not silently adopted

Rule: a figure that does not reproduce is boarded. Three items.

1. **`ULP(300.0)` formula.** The brief instructed 56.8× and warned that an
   earlier `eps × 300` derivation giving ~66× was wrong. **Confirmed:
   `numpy.spacing(300.0) = 5.684341886080802e-14`, ratio 56.843×.** The brief's
   figure reproduces; the superseded one does not. No difference to board beyond
   the correction the brief already made.
2. **The pass window is NOT `1e-15`, it is `c + 1e-15`.** The brief states the
   control "fails only when the field drifts UP between the two checkpoints by
   more than 1e-15 K". **This lane measures the true threshold as `c + 1e-15 =
   1.1837468075730606e-14 K = 0.2082 ULP`** — the binade constant `c` donates a
   small favourable offset that the brief's framing omits. The brief's conclusion
   is unaffected and if anything understated: the window is still **4.80× narrower
   than a single ULP**, and it is a *fixed property of the binade*, not of the
   physics. **The brief's mechanism — one-sided, decided by the sign of a
   residual wiggle, unwinnable by tightening convergence — is confirmed in full
   and is now proven by the `R_m`/`R_f` control in §2.5 rather than inferred.**
3. **The closure call sites fail by a DIFFERENT and DETERMINISTIC mechanism.**
   Reported in §11. This is a material difference from the brief's framing and is
   the one place where "the same latent knife-edge" would have been the wrong
   words.

---

## 3. The mechanism, stated correctly — and why convergence cannot win it

**The predicate is ONE-SIDED.** Over-recovery passes freely: a plant recovered
against an exactly-repeated checkpoint lands `+1.0837468075730605e-14 K` **high**
and passes, which is exactly what `R_m` did and exactly what the frozen selftest
does (§4). The control fails **only** when the field drifts **upward** between
the two checkpoints by more than `c + 1e-15 = 1.1837e-14 K`.

**Ordinary residual drift is several ULP in either direction.** `R_f` measured
+7.00 ULP; `R_m` measured 0.00 ULP. The pass window is **0.2082 ULP wide**, i.e.
**4.80× narrower than the smallest difference the field can represent at all.**

**Therefore the outcome is decided by the SIGN of a residual wiggle, which
carries no physical information whatever.**

**And convergence cannot win it.** This is the property that makes the defect
structural rather than incidental:

- Tightening the iterative-convergence criterion shrinks the drift **magnitude**.
- It never shrinks it below `1e-15` K, because it cannot shrink it below one ULP
  of the field — `5.684e-14 K`, itself **56.8× larger than the slack**.
- It does **nothing at all** to the drift's **sign**.

A perfectly converged run whose last-ULP wiggle happens to point upward refuses.
A worse-converged run whose wiggle happens to point downward, or is exactly zero,
passes. **The control rewards the wrong property, and no amount of solver effort
can move it in the right direction.**

**This is the same shape as the `T15_UP_f` defect this team has already disposed
of.** `T15b_PREREGISTRATION.md` §10 condition (1) records it: *"a strict
inequality evaluated at the exact boundary of an identity, decided by
floating-point recomputation noise"*, measured there as a **39 %** refusal rate
over 300 randomised draws. **T3c's arm is the same species with a harsher
constant** — T15's guard sat at the boundary of an identity and coin-flipped;
T3's sits `4.80×` below one ULP on the favourable side of an identity and
coin-flips on the sign of an unrelated residual. **Two independent T-family
comparators have now been stopped by a control decided at the last ULP rather
than by the signal.** That repetition is itself a finding and is why §11's sweep
is registered rather than left to memory.

---

## 4. Was it catchable at freeze? Yes — and the frozen selftest's own arm is the tell

`analyse_t3_rff.py` carries a 13-check `--selftest`, registered at
`T3_R_FF_PREREGISTRATION.md:354-361` as **"PASS under `python3` and `python3 -O`,
13/13"**. This lane counted the `check(` call sites in the file: **13**, matching
the registered figure.

**It passed 13/13 while carrying this defect, and the reason is written into the
registration itself.** `T3_R_FF_PREREGISTRATION.md:360-361` describes the arm as:

> *"the plant read back at `1.2340000000108e-03`; the negative arm (identical
> checkpoints → change 0)."*

The implementation, `analyse_t3_rff.py:203-210`, writes **the identical `body`
string to both `2000/T` and `4000/T`** — one 50-value field starting at exactly
`300.0`. Drift is therefore **exactly 0.0 by construction**, and:

| the frozen selftest's plant arm | value |
| --- | --- |
| `seen` | 0.0012340000000108375 |
| threshold `PLANT − 1e-15` | 0.0012339999999999999 |
| **margin by which it passed** | **+1.1837468075730606e-14 K = +0.2082 ULP** |

**The selftest passed by one fifth of one ULP, and the registered prose says out
loud that it never drove anything else.** The number `1.2340000000108e-03` printed
in the registration is the binade constant `c` in plain sight — the `...0108` tail
**is** `+1.084e-14`.

**What the selftest never drove is the entire failure mode.** It drove drift = 0.
It never drove drift > 0. **A single limb writing a second checkpoint one ULP
higher than the first would have failed the frozen comparator on the bench, in
under a second, at zero compute cost, before 26 757 core-minutes were spent on a
level whose grading it would block.** §9 registers that limb as mandatory.

**The generalisable form, and this lane states it as the lesson rather than the
anecdote:** a negative arm that drives the *absence* of a signal is not the same
control as an arm that drives the *unfavourable sign* of a signal. `identical
checkpoints → change 0` tests that the reader does not hallucinate. It does not
test that the predicate survives reality, because reality never hands you
identical checkpoints. **A control arm built from the easy case certifies the
easy case.**

---

## 5. The replacement predicate — ADOPTED from three frozen siblings, not invented here

**This is load-bearing and it is the reason this repair is not a fix chosen to
fit an answer: the remedy already existed in this family, in frozen files, and it
predates `R_ff`'s data entirely.** Three T-family comparators use the relative
form. This lane read all three and reproduces each verbatim.

| file | line | predicate, byte-for-byte |
| --- | --- | --- |
| `verification/runs/T-family/T1_runs/analyse_pesweep.py` | **141** | `ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)` |
| `verification/runs/T-family/T1_runs/analyse_dts.py` | **594** | `ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)` |
| `verification/runs/T-family/T1_runs/analyse_dts_p.py` | **226** | `ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)` |

**All three are character-identical.** Two of them state the intent in their own
banner prose (`analyse_dts.py:585-586`, `analyse_dts_p.py:217-218`):

> *"acceptance: PLANT <= control <= real + PLANT"*

with `rec = c["max_change"]` the **un-planted** reader output on the real case
(`analyse_dts.py:591`, `analyse_dts_p.py:223`), and `want = max(rec, PLANT)`
printed beside it for the reader.

### 5.1 What T3c registers

**REGISTERED PREDICATE P-1 — the successor comparator MUST implement exactly
this, and nothing else changes.**

```
    rec = <iterative_convergence(real case)>["max_change"]      # un-planted
    got = <iterative_convergence(planted copy)>["max_change"]   # planted
    ok  = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)
```

`PLANT` stays `1.234e-03` K. **The lower limb is the repair. The upper limb comes
with it and is not optional** — it is what stops a reader that over-reports (a
double-counted plant, a doubled field) from being credited, and dropping it while
keeping the loosened lower limb would be a genuine weakening. The siblings ship
both; T3c takes both.

**STRUCTURAL CONSEQUENCE, registered:** the parent's `planted_zero_control`
returns only the planted reading and never computes `rec`
(`analyse_t3.py:307-331`). The successor **must** call the convergence reader a
second time on the **un-planted** case and return `rec` in its result dictionary,
so the upper limb has an operand and so `rec` is printed beside every verdict.
This is the only structural change to the control's shape.

### 5.2 The two levels under the registered predicate

Re-derived by this lane; `lo = PLANT × (1 − 1e-9) = 0.0012339999987660002`.

| level | `got` | `rec` | `hi = rec + PLANT + 1e-12` | lower limb | upper limb | **verdict** |
| --- | --- | --- | --- | --- | --- | --- |
| `R_m` | 0.0012340000000108375 | 7.875202e-07 | 0.0012347875212 | PASS, margin **+1.2448373495e-12 K** | PASS, margin −7.8752118916e-07 K | **PASSES** |
| `R_f` | 0.0012339999996129336 | 4.910338816443982e-06 | 0.001238910339816444 | PASS, margin **+8.4693341749e-13 K** | PASS, margin −4.9103402035e-06 K | **PASSES** |

**`R_m`'s verdict is unchanged.** The repair does not alter a single level that
the frozen predicate already credited — it rescues the one it discarded for the
sign of a wiggle.

---

## 6. THE REPAIR CANNOT PASS A BLIND READER — the anti-gaming demonstration, with numbers

**The change does NOT loosen any gate.** It loosens exactly one tolerance, inside
a control whose only job is to establish that the reader is not blind, and §6.2
proves the loosened tolerance is still eight orders of magnitude too tight to
credit a blind reader.

### 6.1 What the tolerance change actually is

| | frozen predicate | **T3c registered predicate** |
| --- | --- | --- |
| form | absolute | relative |
| tolerance constant | `1e-15` K | `PLANT × 1e-9` = **1.2340000000000002e-12 K** |
| pass window on upward drift | `c + 1e-15` = 1.1837e-14 K = **0.2082 ULP** | `c + 1.234e-12` = 1.2448e-12 K = **21.8994 ULP** |
| window vs one ULP of the field | **4.80× narrower** | 21.9× wider |
| widening of the window | — | **105.2×** |

**Headroom over the measured failure, stated so the margin is not oversold:**

- allowed shortfall **1.234e-12 K** against the measured shortfall
  **3.870664639499255e-13 K** → **3.1881×**;
- equivalently, allowed upward drift **1.2448e-12 K** against the measured drift
  **3.979039320256561e-13 K** → **3.1285×**, i.e. **21.9 ULP allowed against 7.00
  ULP observed.**

**This is a real margin and it is not unlimited, and the document says so.** A
future level drifting more than ~21.9 ULP upward at cell 0 would refuse again.
That is the intended behaviour: 21.9 ULP is still *far* below anything physical,
so a refusal at that scale would indicate something genuinely wrong with the
files rather than a rounding wiggle.

### 6.2 The proof that a blind reader still fails

**A blind reader is one that reports the field's real change and never sees the
plant at all** — the exact failure rule 3 exists to catch. Its output is `rec`.

| | `R_f` | `R_m` |
| --- | --- | --- |
| what a blind reader would report | **4.910338816443982e-06 K** | **7.875202e-07 K** |
| the registered floor `PLANT × (1 − 1e-9)` | 0.0012339999987660002 K | 0.0012339999987660002 K |
| **blind reader passes?** | **NO** | **NO** |
| how far short it falls | **251.31× too small** | **1 566.94× too small** |

**The margin against gaming, quantified three ways.**

1. **How much would the tolerance have to be loosened to admit the blind `R_f`
   reader?** It would need `PLANT × (1 − x) ≤ 4.910338816443982e-06`, i.e.
   **`x ≥ 0.996021`**. The registered tolerance is **`1e-9`**. **T3c's tolerance
   is 9.9602e8 — very nearly a billion times — too tight to admit a blind
   reader.** There is no continuum here on which the repair "moves toward"
   permissiveness; it sits at one end of an eight-decade gap and the blind reader
   sits at the other.
2. **Against the physical signal.** `R_f`'s real convergence signal is
   4.910338816443982e-06 K = **8.638e7 ULP**. The new tolerance window is
   1.244837e-12 K. **The signal is 3.9446e6× larger than the whole tolerance
   window** — the repair cannot mask, absorb or shade any physical quantity,
   because it operates four million times below the smallest thing the rung
   measures.
3. **Against a half-blind reader.** Any reader recovering less than
   99.9999999 % of the plant refuses. The nearest plausible degraded reader —
   one that recovers half the plant, `6.17e-04` — misses the floor by a factor of
   2, i.e. by **5.0e8 tolerance-widths.**

**The repair is therefore anti-gaming by construction:** it widens a window from
0.21 ULP to 21.9 ULP, both of which are numerically invisible against a signal of
8.6e7 ULP, and it leaves the only discrimination that matters — plant seen versus
plant not seen, a factor of 251 — completely untouched.

---

## 7. The bands carry over VERBATIM and MAY NOT BE CHANGED

**No number in this section is new, and T3c has no authority to alter any of
them.** Reproduced from `docs/campaigns/T-family/T3_R_FF_PREREGISTRATION.md` §9,
HEAD blob `35d670168d781d5d3f49919d1fe2ae7429ff2759`, with line citations.

**P1 — G2 `x_peak/H` on `(R_m, R_f, R_ff)`** — `T3_R_FF_PREREGISTRATION.md:255-261`:

> **P1 — G2 `x_peak/H` on `(R_m, R_f, R_ff)`.** If the medium→fine step 0.00604
> is second-order behaviour, `R_ff` ≈ **6.1436** (step 0.0024 at `r = 1.599`);
> first-order would give 6.1450. **Registered expectation: `x_peak/H(R_ff)` in
> [6.141, 6.148] and the triple CONVERGING with observed order `p` in
> [0.5, 3.0].** A `p` above 3.0 again means the levels cannot resolve an order
> (the §14.4 reading, not superconvergence); a `p` below 0.5 is refused as no
> demonstrated order. Either is reported with the numbers.

**P2 — G1 `St_peak` on the new triple** — `T3_R_FF_PREREGISTRATION.md:263-270`:

> **P2 — G1 `St_peak` on the new triple.** `St_peak` moved +7.02e-5 then
> +7.07e-5 across `(c, m, f)` — equal steps, i.e. no convergence with mesh at
> this `y+` sequence. **Registered expectation: the triple is NOT CONVERGING
> (STAGNANT or DIVERGENT), `St_peak(R_ff)` ≈ 0.00358 if the equal-step pattern
> holds.** If instead it comes in near **0.003536** (the second-order value) and
> the triple is CONVERGING with `p` in [0.5, 3.0], that is the informative
> surprise and is recorded as P2 **wrong**. G3/G4 `St(10H)`, `St(20H)` are
> predicted to follow G1.

**P3 — iterative convergence** — `T3_R_FF_PREREGISTRATION.md:272-275` — carries
over unchanged, including its consequence that a NOT CONVERGED level puts every
row at **NOT A RESULT** on gate (1).

**Everything else carries over unchanged**: the physical case, the four meshes,
the refinement ratios, the graded and reported row sets, the L-342 field classes,
the strict completion rule, the outlet guard, the `delta_99/H` inlet-window flag
(0.67 against the registered [0.80, 1.35]), the closed verdict vocabulary, the
`P_MIN` floor, `Fs = 1.25`, and the Roache ordering of standing rule 5.
**T3c re-grades; it does not re-design.**

**REGISTERED CONDITION V-1.** **The only thing T3c changes is the rule-3
planted-zero control's acceptance predicate.** Every other threshold, band,
floor, guard, cap, timeout, label and clause is byte-identical to the parent. A
successor that also moves a band is doing a different and far more dangerous
thing, and this document is not authority for it.

**REGISTERED CONDITION V-2 — the repair does not rescue gate (1).** The control
establishes that the reader is not blind. It says nothing about whether any level
is iteratively converged. `R_f`'s un-planted change is 4.910338816443982e-06 K
and `R_m`'s is 7.875202e-07 K; **whether those meet the rung's registered
iterative-convergence criterion is a gate-(1) question that this document does
not answer, does not prejudge and does not alter.** If a level is NOT CONVERGED,
P3's registered consequence applies in full and every row is **NOT A RESULT** —
the repaired control changes nothing about that.

---

## 8. What this rung could have earned anyway — the damage, not overstated

**The control defect did not cost this rung a PASS, because a PASS was never
reachable.** `T3_R_FF_PREREGISTRATION.md:289-293`, registered **in advance** of
any compute:

> - **The primary, Vogel & Eaton (1985), DOI 10.1115/1.3247522, is NOT
>   OBTAINED** (`T3_reference_primary.json` absent, `primary_sha256 = null`).
>   Gate (4) is unreachable: **no row can return PASS or GATE FAIL, and HOLDS is
>   unreachable. This level earns `V`/`G` — a grid statement on a converged
>   triple — and nothing beyond it.**

And `T3_R_FF_PREREGISTRATION.md:277-280` fixes the best available outcome:

> A CONVERGING `(R_m, R_f, R_ff)` triple on a row lifts that row from gate
> (1)/(2) to gate (3): **BLOCKED** (the primary is not held, §10) with value,
> triple, GCI and the deviation from the secondary digitisation REPORTED beside
> it.

**So the ceiling on every row of this rung was `BLOCKED`, registered before the
run, for a reason that has nothing to do with this defect.** What the defect
actually cost is worth having and is worth stating precisely — and no more than
precisely:

| lost | not lost |
| --- | --- |
| the triple classification of `(R_m, R_f, R_ff)` on every graded row | any PASS — unreachable at gate (4) |
| the observed order `p` and the GCI at `Fs = 1.25` | any GATE FAIL — equally unreachable |
| the diagnostic rows and the deviation from the secondary digitisation | the run itself: `DONE.R_ff` stands, the fields are on disk, the 26 757 core-minutes are **not** waste |
| the answer to P1 and P2, i.e. whether the registered predictions were right | the completion verdict, which is independent of grading |

**The rung's compute is recoverable in full.** `R_ff` completed under the strict
rule and its fields are intact; the entire remedy is a comparator re-run costing
under one core-minute (§12). **A defect that blocks a grading pass is not a
defect that destroys a run**, and this document declines to describe it as one.

---

## 9. Selftest specification the successor comparator MUST satisfy

**Binding: no row of T3c grades until every arm below has run and printed, with
both limbs where two are specified.** An arm that prints one limb is registered
here as a **failed control**, not a passing one. Zero `assert` statements
(L-332); refusals are explicit and carry exit 2.

**The requirement that the frozen selftest missed is arm S-2, and it is the
reason this section exists.**

| arm | POSITIVE limb — must be SEEN | NEGATIVE limb — must NOT fire |
| --- | --- | --- |
| **S-1 PLANT VISIBLE (the rule-3 requirement itself)** | Plant `1.234e-03` K into the earlier checkpoint of a scratch case built at ~300 K; the reader must return `got` satisfying **both** limbs of P-1, and `read_back_delta` must equal `PLANT` to within `1e-12`. | The plant must be **read back from disk**, not from memory. The arm refuses if the value re-read from the written file does not carry the perturbation. |
| **S-2 BOTH SIGNS OF CHECKPOINT DRIFT — the arm the parent never drove** | Drive the control **four** times on scratch cases identical but for the drift at cell 0: **(a) drift = −7 ULP, (b) drift = 0, (c) drift = +7 ULP, (d) drift = +21 ULP.** **All four must PASS**, and the four `got` values must be printed. **(c) is the exact case that refused on `R_f` and is the arm's whole point.** | **Drift = +200 ULP must REFUSE.** A predicate that passes everything is not a predicate; the arm must demonstrate the repaired form still has a floor it can hit. The refusing value must be printed with its shortfall. |
| **S-3 THE REPAIRED PREDICATE STILL REFUSES A BLIND READER** | Substitute a reader that returns the **un-planted** `max_change` (`4.910338816443982e-06` K, `R_f`'s real value) while the plant is genuinely on disk. **The control MUST REFUSE**, and must print that the reading fell short by **251.31×**. | The same substitution at `R_m`'s baseline `7.875202e-07` K must **also** refuse, short by **1 566.94×**. **Two blind readers, both refused, both quantified** — a single blind mutant does not establish a floor. |
| **S-4 OVER-REPORTING REFUSED (the upper limb is live)** | A reader returning `2 × PLANT + rec` must **REFUSE** on the upper limb `got <= rec + PLANT + 1e-12`, with the excess printed. | The upper limb must **NOT** fire on any of S-2's four passing cases. An upper bound that fires on legitimate readings is a new defect, not a control. |
| **S-5 BINADE INDEPENDENCE (the §11 hazard, closed here)** | Run S-1 on scratch fields whose baseline sits in **each** of the binades `[32,64)`, `[64,128)`, `[256,512)`, `[512,1024)` and `[2048,4096)`. **All must PASS.** Under the frozen absolute predicate, **four of these five refuse for every value in the binade** (§11); this arm proves the repaired form is free of that dependence. | The arm must print each binade's rounding constant `c` beside its verdict, so the reader can see the constant change while the verdict does not. |
| **S-6 `rec` IS REAL AND IS THE UN-PLANTED READING** | The comparator must assert that `rec` was obtained from a case with **no plant in it**, and print `rec`, `got` and `max(rec, PLANT)` on every control line, as the three siblings do. | **REFUSE if `rec` and `got` were read from the same file**, or if `rec` is exactly `0.0` on a real case — a control whose baseline was never driven has established nothing, and must say so rather than pass. |
| **S-7 THE RUN TREE IS NEVER WRITTEN** | Every plant is written into a scratch copy outside the case tree; the arm asserts the scratch path does not resolve inside `verification/runs/`. | **REFUSE** if it does. |
| **S-8 SCHEMA INTEGRITY (the birth requirement)** | Before any plant, assert the parsed field carries the producer's `FoamFile` header with `object T`, `class volScalarField`, and a cell count matching between the two checkpoints. | **REFUSE** on a zero-length internal field or on a cell-count mismatch — the *"empties the tuple it tests"* failure named in Sanaa's 2026-08-28 birth requirement, closed explicitly. |

**S-2 and S-3 are the two arms this registration exists for.** S-2 drives the
unfavourable sign that the frozen 13/13 selftest never drove; S-3 proves the
loosened tolerance did not buy the repair a pass it should not have. **A
comparator that satisfies every other arm but not these two has not discharged
this document.**

---

## 10. Registration under `VERIFICATION_CHARTER.md` §2d.1 — written for verification to rule, NOT ruled here

T3c re-grades artifacts that **already exist**, so a grading-path change is being
made after first compute. **§2d.1 is verification's clause. It is not this lane's
call and not its supervisor's.** This section states the case in the clause's own
four conditions, puts **both** readings of each on the table, and stops.

| §2d.1 condition | T3c's claim | this lane's honest assessment — BOTH readings |
| --- | --- | --- |
| **(1) repairs a DEMONSTRABLE ERROR, not a preference** | `seen − PLANT = c − (b − a)` is an **exact IEEE-754 identity** (§2.3), reproducing the measured shortfall `−3.870664639499255e-13` to the last bit. The frozen predicate's pass window is `0.2082 ULP`, **4.80× narrower than the field's own representable spacing**. §2.5 measures the consequence directly: `R_m` and `R_f` differ **only** in cell 0's drift (0.00 vs +7.00 ULP) and receive opposite verdicts. | **FAVOURABLE:** a tolerance finer than the ULP of the operands is not a preference, it is an arithmetic impossibility, and the `R_m`/`R_f` pair demonstrates it rather than arguing it. **UNFAVOURABLE, and it deserves stating:** a reader could hold that a control *should* be strict and that the correct remedy is to make the checkpoints identical rather than to widen the tolerance. This lane's answer is §3 — the drift cannot be driven below one ULP by any solver effort, so that remedy does not exist — but the objection is legitimate and is not waved away. **Neither reading is adopted here.** |
| **(2) established by an instrument INDEPENDENT OF THE HYPOTHESIS** | The instruments are (i) **the closed-form IEEE-754 identity of §2.3**, which grades nothing and knows nothing about any verdict; (ii) **the `R_m` control of §2.5**, a level whose control PASSED and whose verdict was never at issue; and (iii) **three frozen sibling comparators (§5) that adopted the relative form before `R_ff` existed** — the remedy was not invented after seeing an answer, it was already the family's practice. | **THIS IS THE LOAD-BEARING CONDITION AND VERIFICATION MUST WEIGH IT. FAVOURABLE:** the identity condemns the predicate for *every* input, including inputs that would have made any verdict go either way; the `R_m` limb is the T5c-style strength — the defect is visible on a level that passed; and §1's blindness means **there is no known answer for the repair to have been steered toward**, which is the sharpest form this condition can take. **UNFAVOURABLE, stated plainly:** the *reason* this lane examined the predicate at all was an inconvenient refusal that blocked a rung the team wanted graded. Motivation supplied by an unwelcome outcome is not the same as an instrument selected to produce a wanted one, but a sceptical reader is entitled to note that nobody audited this predicate while it was passing. **Both readings on the table; neither adopted.** |
| **(3) the record discloses it, names the instrument, and QUANTIFIES what moved** | §0–§4 disclose and quantify; §2.6 boards the three points where this lane's measurement differs from or sharpens the brief it was handed, **including the correction that the pass window is `c + 1e-15`, not `1e-15`**; §4 quantifies that the frozen 13/13 selftest passed its plant arm by **+0.2082 ULP** and names the arm it never drove; §6 quantifies the tolerance change in five ways and §11 quantifies the sweep. | **Met.** The one thing this lane cannot quantify is the counterfactual — how many other T-family controls would refuse on an unfavourable-sign drift — because §11's sweep is a *static* sweep of the predicate's text, not a dynamic sweep of every comparator's behaviour. **That limit is stated rather than papered over.** |
| **(4) pre-repair values recorded beside the published ones** | The pre-repair state is **a REFUSAL, not a value.** `T3_R_FF_GRADE_OUTPUT_20260830T224307Z.txt` is 337 bytes and two lines and contains **no graded row of any kind**. That file is cited, not restated. **T3c's comparator MUST print, beside every row it publishes, `PRE-REPAIR STATE: REFUSED (exit 2) at the rule-3 planted-zero control on R_f — no row existed`.** | **Met, and unusually strongly — this is the strongest of the four here.** There is no prior number that a repaired number could be accused of having been steered toward, because **no prior number exists.** Combined with §1's blindness clause, the ordinary §2d.1 anxiety — that a repair was tuned until the answer looked right — **has no object in this case**, and verification can verify that claim independently by confirming `gate_t3_rff.json` does not exist on disk. |

**THE WEAKEST CONDITION IS (2), AND THIS LANE NAMES IT RATHER THAN LETTING
VERIFICATION FIND IT.** Not because the instruments are poor — an exact
floating-point identity is about as independent as an instrument gets — but
because the *occasion* for the audit was a refusal the team did not want. §1's
blindness is the mitigation and it is a strong one, but it mitigates rather than
eliminates, and it only holds for as long as B-1 holds.

**THE STRONGEST IS (4), UNUSUALLY SO**, for the reason in the table.

**NOT RULED HERE.** **No row of T3c may be graded until verification has ruled on
§2d.1.** If verification rules against re-grading the existing artifacts, §12's
costed fresh run is the fallback and it is explicitly not a blocker.

---

## 11. The rule-14 sweep — three call sites, NAMED, and two of them are another team's to fix

**Standing rule 14: a lesson is not applied until EVERY call site asserts it
(L-221/L-222).** A repair that fixes only the site that happened to fire is not a
repair; it is a coincidence.

This lane swept the repository for the absolute form `PLANT - 1e-15` across all
`*.py` outside `.git`. **Exactly three call sites exist:**

| # | file | line | text | HEAD blob | territory |
| --- | --- | --- | --- | --- | --- |
| 1 | `verification/runs/T-family/T3_runs/analyse_t3.py` | **327** | `return dict(passed=(seen >= PLANT - 1e-15), planted=PLANT,` | `d5e4a9eb…` | **heat-transfer — this document** |
| 2 | `cases/RANS_LES_closure_models/M1_multimodel_sweep/stage_m1.py` | **196** | `reader_max_change=seen, passed=seen >= PLANT - 1e-15)` | `ef297541…` | **closure** |
| 3 | `cases/RANS_LES_closure_models/M1_multimodel_sweep/grade_m1.py` | **215** | `reader_max_change=seen, passed=seen >= PLANT - 1e-15)` | `23fb1591…` | **closure** |

Both closure paths **exist and were read by this lane**; both carry the identical
`PLANT = 1.234e-03` (`stage_m1.py:56`, `grade_m1.py:83`, both annotated *"standing
rule 3"*).

### 11.1 The closure sites carry the same predicate but FAIL BY A DIFFERENT MECHANISM — measured, and boarded as a correction

**This is the one place where "the same latent knife-edge" would have been the
wrong words, and this lane reports the difference rather than repeating the
framing it was handed.**

Closure's controls plant into a **copy of the same file** (`stage_m1.py:186-194`,
`grade_m1.py:205-214`: `shutil.copyfile` twice, plant into one, diff the two).
There is no second checkpoint and therefore **no drift term at all**. Their
`seen − PLANT` reduces to the binade constant `c` alone:

```
    seen − PLANT  =  c  =  (x + PLANT) − x − PLANT
```

`c` is **constant across an entire binade** (verified by this lane: 50 000
random draws per binade returned **exactly one distinct value** of `c` in each).
So closure's control is **not a coin flip — it is deterministic, and its verdict
is a fixed function of the field's magnitude:**

| binade of the field value | `c` | frozen predicate verdict |
| --- | --- | --- |
| `[0.0625, 32)` and below | `\|c\| ≤ 1.79e-16` | **PASSES for every value** |
| **`[32, 64)`** | **−3.3733866394713985e-15** | **REFUSES for EVERY value — 100 %** |
| **`[64, 128)`** | **−3.3733866394713985e-15** | **REFUSES for EVERY value — 100 %** |
| `[128, 256)`, `[256, 512)` | +1.0837468075730605e-14 | passes for every value |
| **`[512, 1024)`** | **−4.600595078507741e-14** | **REFUSES for EVERY value — 100 %** |
| `[1024, 2048)` | +6.768089e-14 | passes for every value |
| **`[2048, 4096)`** | **−1.596928e-13** | **REFUSES for EVERY value — 100 %** |

**The hazard is real but it is a different hazard, and the difference matters for
whoever fixes it.** T3's site refuses on the *sign of a residual wiggle* and is
irreproducible run to run. Closure's sites refuse on the *magnitude of the field*
and are perfectly reproducible: a `nut` or `U` field whose planted cell lands in
`[32, 128)` or `[512, 1024)` will refuse **every time, on every run, forever**,
and a field that lands elsewhere will pass every time. `stage_m1.py:54` lists
`PLANT_CANDIDATES = ("nut", "U")`; **this lane did NOT inspect closure's data and
makes no claim about which binade their fields occupy.** That is closure's to
determine.

### 11.2 REPORTED, NEVER TOUCHED — and routed

**This lane did not edit, stage, run or test `stage_m1.py` or `grade_m1.py`, and
T3c has no authority over them.** They are `cases/RANS_LES_closure_models/`,
closure's territory under the roster. Their worktree blobs equal their HEAD
blobs, verified above and unchanged by this lane.

**FLAGGED FOR THE CHIEF TO ROUTE to `closure-supervisor`**, with the finding
stated in the form closure needs it:

> Your M1 rule-3 planted-zero controls at `stage_m1.py:196` and `grade_m1.py:215`
> use `seen >= PLANT - 1e-15`. The `1e-15` slack is smaller than one ULP of any
> field value above ~4.5. Because your controls diff two copies of one file, the
> recovery error is a **constant per binade**, so the predicate is deterministic:
> it refuses for **every** value in `[32,64)`, `[64,128)`, `[512,1024)` and
> `[2048,4096)`, and passes for every value elsewhere. **Nothing has fired yet, so
> far as this lane can see** — this is a latent hazard reported before it costs a
> grading pass, not an incident. The T-family's own frozen remedy is the relative
> form at `analyse_pesweep.py:141`, `analyse_dts.py:594` and `analyse_dts_p.py:226`.

**This is the second T-family comparator stopped by a last-ULP control (§3), and
the sweep says a third and fourth site carry the same predicate in another
family.** Recording it in one team's registration is not applying the lesson —
**the lesson is applied when all three sites assert it**, and T3c can only
discharge one of the three. **The other two remain OPEN and this document does
not claim otherwise.**

---

## 12. Cost — rule 12

**No new solver compute is proposed.** `R_ff`'s fields, `DONE.R_ff`, all four
meshes and every completed level are on disk.

### 12.1 The T3c re-grade

| item | figure | basis |
| --- | --- | --- |
| **POINT** | **0.05 core-min** | comparator time only, 1 rank. Basis: the refused pass measured **0.032 core-min** for the whole grading pass (`mark_done_t3_rff.py` 1.33 s + `analyse_t3_rff.py` 0.61 s = 1.94 s at 1 rank), recorded in the C-211 row; T3c adds one extra un-planted `iterative_convergence` call (§5.1) and the §9 selftest arms |
| **CAP / registered stop** | **1.0 core-min** | ~20× POINT. **An overrun stops the run** (rule 12); a comparator that has not finished in one core-minute on a 235 520-cell field is not slow, it is wrong |
| **USD at POINT** | **$0.0000428** | **DERIVED, NOT MEASURED** — `0.05 / 60 × $0.0513/core-h` |
| **USD at CAP** | **$0.0008550** | **DERIVED, NOT MEASURED** — `1.0 / 60 × $0.0513/core-h` |

The rate `$0.0513/core-h` for c7a.4xlarge is **owner-stated, reported-by-owner,
not measured**: **the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5). **Under a tenth of a cent cannot be a reason to
rule §10 either way**, and it is recorded here so that the ruling is never taken
under cost pressure.

### 12.2 The parent run's actual — rule 12's estimate-versus-actual, recorded not re-opened

Already filed as calibration row **C-211**
(`verification/runs/T-family/T3_runs/COST_CALIBRATION_C211_DRAFT_ROW.txt`); every
figure below re-derived by this lane from that row and re-checked arithmetically.
**T3c does not re-open it and does not restate its attribution.**

| item | figure | basis |
| --- | --- | --- |
| `R_ff` actual | **26 757.067 core-min** | **MEASURED**, `STATUS.R_ff`, `wall_s = 200 678 × 8 ranks / 60`; `rc=0`, `capped=no` |
| in core-hours | **445.9511 core-h** | 26 757.067 / 60 |
| in dollars | **$22.8773** | **DERIVED, NOT MEASURED** at $0.0513/core-h, `COMPUTE_BUDGET_CHARTER.md` §5 |
| registered POINT | 18 218.2 core-min | `T3_R_FF_PREREGISTRATION.md:179`, frozen pre-compute |
| registered CEILING | 27 400 core-min | `T3_R_FF_PREREGISTRATION.md:180` |
| **actual / POINT** | **1.4687×** | 26 757.067 / 18 218.2 — re-derived, reproduces |
| **fraction of CEILING** | **0.9765** | 26 757.067 / 27 400 — re-derived, reproduces |
| waste | **0.000 core-min** | C-211; no cap hit, nothing killed or discarded |

**No overrun.** Rule 12's overrun clause binds on the CEILING and the CEILING was
never reached — the run finished at **97.65 %** of it.

**And the compute is NOT waste.** The 26 757 core-minutes bought a level that
completed under the strict rule and whose fields are intact. **The grading pass
that failed cost 0.032 core-min.** Recovering the rung costs under one more.

### 12.3 The fallback, if verification rules a fresh run is required

| item | figure | basis |
| --- | --- | --- |
| fresh `R_ff` run | **26 757.067 core-min** | **MEASURED** — the actual of the run that already exists, not an estimate |
| in dollars | **$22.8773** | **DERIVED, NOT MEASURED**, as above |
| calibration owed | a fresh row in `docs/COST_CALIBRATION.md` | **NOT discharged by this document** |

**This fallback is expensive and this document says so rather than burying it.**
Unlike T15b (whose fallback was $1.02) and T5c ($0.39), **re-running `R_ff` costs
55.74 hours of wall and $22.88 derived, and would land at 97.65 % of a registered
ceiling with 2.35 % of its timeout unused** — C-211 records that a further 2.4 %
rate degradation would have killed the previous run at the timeout. **A fresh run
is therefore not a comfortable fallback; it is a near-miss repeated.** That is a
reason for verification to weigh the §10 question carefully, and **explicitly not
a reason to rule it favourably.** If verification rules against the re-grade, the
run is re-run.

---

## 13. What this document does not do

- It **does not** edit, amend or supersede any frozen file. `analyse_t3.py`
  (`d5e4a9eb…`) and `analyse_t3_rff.py` (`44e3e2b8…`) are byte-identical to their
  HEAD blobs, verified in §2.4, and stay that way.
- It **does not** contain comparator code, and that is deliberate: the
  registration is frozen **before** the code exists, so the supervisor's personal
  §3 check — every measurement-script diff read as a diff before its output is
  believed — happens against a gate that was fixed first.
- It **does not** grade anything, enqueue anything, or launch anything. No row of
  T3c exists and none may be produced until §10 is ruled and §9's arms print.
- It **does not** move a band, a floor, a cap, a timeout, a guard or a label.
  **One predicate changes. Nothing else.** (§7, V-1.)
- It **does not** claim `R_f` or `R_m` is iteratively converged. That is gate (1)
  and it is untouched. (§7, V-2.)
- It **does not** touch closure's two call sites, and it **does not** claim the
  rule-14 lesson is applied. Two of three sites remain open. (§11.2.)
- It **does not** measure, and forbids measuring, any `R_ff` graded quantity
  before the ruling. (§1, B-1/B-2.)
- It **does not** rule §2d.1. That is verification's clause.
- It **does not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).

---

# AMENDMENT 1 — 2026-09-03 — **THE REGISTERED PREDICATE P-1 WAS TESTED BEFORE IT WAS BUILT ON, AND IT DOES NOT REPAIR THE DEFECT THE GRANT WAS GIVEN FOR. P-1 IS SUPERSEDED BY P-2.**

**Lines whose number changed above this section: 0.** Nothing above is edited,
reordered, inserted or deleted, with the single exception of the **struck**
status line at the head, which `VERIFICATION_CHARTER.md` §2d.11.3 makes a
condition of landing this document at all and which is left legible.

**Made BEFORE first compute under this registration and before any grading run.**
Rule 2 permits pre-compute amendment and requires the condition and how it was
checked to be named: **`gate_t3c.json` does not exist on disk** — verified in the
same shell invocation that wrote this amendment — and no graded `R_ff` quantity
has been computed by anyone. The blindness clause of §1 is intact and binding.

**Authority:** `VERIFICATION_CHARTER.md` §2d.11.1 (v1.45, commit `ad9eda53`),
read at source by this lane as a commit — message and all 116 added lines.

---

## A1.1 WHAT WAS FOUND, AND IT IS A FINDING ABOUT THE GRANT'S OWN PREMISE

**§5.1's registered predicate P-1 was MEASURED before any code was written on it,
and it still passes `R_c` vacuously.**

P-1, as registered at §5.1:

```
ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= rec + PLANT + 1e-12)
```

Driven through the frozen module's own machinery on all four cases:

| case | `rec` (un-planted) | `got` (planted) | P-1 verdict | was the plant the argmax? |
|---|---|---|---|---|
| **`R_c`** | 2.4683725767638407 | **2.4683725767638407** | **PASS** | **NO** |
| `R_m` | 7.875202072682441e-07 | 1.2340000000108375e-03 | PASS | yes |
| `R_f` | 4.910338816443982e-06 | 1.2339999996129336e-03 | PASS | yes |
| `R_ff` | 2.1839413989255263e-04 | 1.2339999996697770e-03 | PASS | yes |

**On `R_c`, `got == rec` to the last digit.** The plant was entirely invisible to
the reader's maximum, and P-1 returns PASS on both limbs.

**P-1 repairs the fails-CLOSED limb only.** It was drafted 2026-08-30, before the
fail-open limb existed as a finding, so it is a registration written against half
the problem — not an error of reasoning by its author. But **the fail-open is the
precise ground on which §2d.11.1 granted Item A**, and P-1 does not touch it.
**A frozen document is evidence about what was predicted, not a guarantee that
the prediction was right**, and this lane tested it rather than inheriting it.

---

## A1.2 THE REPLACEMENT — **P-2**, REGISTERED HERE, SUPERSEDING §5.1

```
LIMB A  (IDENTITY)   got_max == cell_diff
                     the reader's maximum change IS the change at the cell this
                     control planted.  Not a tolerance: when the plant is the
                     argmax these are the SAME subtraction and agree bit-for-bit.
LIMB B  (MAGNITUDE)  abs(got_max - PLANT) <= N_ULP * math.ulp(operand)
```

`PLANT` stays **`1.234e-03` K**, unchanged. **No gate, band, threshold on any
graded quantity, cap, label or verdict rule is altered by this amendment.**

**LIMB B's tolerance is COMPUTED FROM `math.ulp()` OF THE ACTUAL OPERANDS at
grade time, never hardcoded** — §2d.11.1 condition 4, which forbids an
"equivalent" constant because a constant equal to *n* ulp of 300 K is wrong at
any other field magnitude. Arm **S-5** proves the tolerance follows the operands
across five binades (48, 96, 384, 768, 3072), all PASS.

---

## A1.3 HOW `N_ULP = 32` WAS FIXED — THE WINDOW, ITS ENDPOINTS, AND EVERY CANDIDATE IN IT

**The value is fixed by arms this document froze on 2026-08-30, before the
question arose.** §9's arm S-2 requires drift **−7 / 0 / +7 / +21 ulp** to PASS
and **+200 ulp** to REFUSE.

| constraint | source | forces |
|---|---|---|
| S-2(d) drift +21 ulp must PASS | §9, frozen | `N_ULP >= 21` |
| real `R_f` err 6.81 ulp must PASS | measured | `N_ULP >= 6.81` |
| real `R_ff` err 5.81 ulp must PASS | measured | `N_ULP >= 5.81` |
| S-2 negative, +200 ulp must REFUSE | §9, frozen | `N_ULP < 200` |

**ADMISSIBLE WINDOW: `21 <= N_ULP < 200`.** Admissible integers: 21…199, **179
values**. Admissible powers of two: **32, 64 AND 128 — three of them.**

> **A CORRECTION THIS LANE MAKES AGAINST ITSELF.** An earlier statement of this
> reasoning claimed 32 was **the unique** admissible power of two. **That was
> false**, and it is corrected here rather than quietly dropped. The window
> admits three, and a coincidence claim that does not survive arithmetic is
> exactly the kind of thing a reviewer goes straight at.

**SELECTION PRINCIPLE, REGISTERED: THE SMALLEST ADMISSIBLE VALUE — the most
restrictive tolerance that still satisfies every frozen must-pass arm.** The
smallest admissible power of two is **32**, giving **1.5238×** margin over the
frozen must-pass ceiling of 21. The smallest admissible *integer* is 21, which is
rejected because it satisfies S-2(d) **only at exact equality** and a
boundary-exact tolerance is brittle under any change of rounding.

**The most restrictive admissible choice is also the one that cannot be accused
of having been tuned to pass something**, and that — not uniqueness — is why 32
is the registered value.

---

## A1.4 THE ARM THIS LANE'S OWN CONTROL FORCED IT TO ADD — **S-9**

**The §2p.3(e) mutation demonstration failed on its first run, against this
lane's own repair, and the failure was informative.**

The first mutation disabled LIMB A and expected `R_c` to wrongly pass. **It did
not.** `R_c` is refused by **LIMB B alone** — its maximum is 2000× the plant,
far outside a 32 ulp window — so **`R_c` never demonstrated that LIMB A does any
work at all.** A mutation that the shipped code survives for the wrong reason is
a control that certifies nothing, which is the same disease this whole amendment
exists to cure.

**REGISTERED ARM S-9 — the case that makes LIMB A load-bearing.** A **decoy
cell** (not the planted cell) changes by `PLANT + 20 ulp`:

- **LIMB B PASSES it** — 20 ulp is inside `N_ULP = 32`, so the magnitude test
  cannot tell the decoy from the plant;
- **LIMB A REFUSES it** — the maximum is not at the planted cell.

**Measured: shipped module `limb_A=False, limb_B=True` → REFUSE. Mutant with the
identity limb disabled → PASS.** The mutation is killed, and LIMB A is shown to
carry weight that LIMB B does not.

**AND LIMB A IS AN IDENTITY, NOT A TOLERANCE, BECAUSE OF S-9.** Had LIMB A used
the same 32 ulp window, the decoy at +20 ulp would have satisfied it too — the
fail-open in a new dress. Measured residual on every real passing case: **0.00
ulp, exactly.**

---

## A1.5 THE §2p.3(e) SHOWING, BOTH LIMBS, THROUGH THE PRODUCTION PATH

`control_t3c_p2.py` drives `analyse_t3c.planted_zero_control_p2` **by import**
(§2p.3(d) — the production function, not a copy). `__pycache__` is cleared before
every run. **Result: CONTROL PASS, 0 did not behave.**

| arm | requirement | measured |
|---|---|---|
| MUST PASS `R_m` | real case, plant seen | PASS, limb_A resid **0.00 ulp**, limb_B err **0.19 ulp**, drift +0.00 ulp |
| MUST PASS `R_f` | real case, plant seen | PASS, resid **0.00 ulp**, err **6.81 ulp**, drift **−7.00 ulp** |
| MUST PASS `R_ff` | real case, plant seen | PASS, resid **0.00 ulp**, err **5.81 ulp**, drift −6.00 ulp |
| MUST FAIL `R_c` | the vacuous pass | **REFUSE**, both limbs; frozen predicate **reproduced as PASS** on the same case |
| MUST FAIL blind reader | returns `rec` | REFUSE on `R_f` (short **251.31×**) and `R_m` (short **1566.94×**) |
| MUST FAIL over-report | returns `2·PLANT + rec` | REFUSE, err **2.180e+10 ulp** |
| MUTATION M1 | identity limb disabled | shipped REFUSES the S-9 decoy, **mutant PASSES** → killed |
| MUTATION M2 | `N_ULP` widened to 256 | +200 ulp **wrongly passes**, then REFUSES again at 32 → killed |

`analyse_t3c.py --selftest`: **SELFTEST PASS, 0 checks failed** — S-1, S-2 (four
positive limbs plus the +200 refusal), S-5 (five binades), S-8, **S-9**, the
frozen verdict logic, and the `DONE`-marker refusal driven to exit 2. Zero
`assert` statements (L-332).

---

## A1.6 THE FROZEN GRADING PATH — FULL sha256 OF THE DISK BYTES

**Recorded as FULL sha256, because `scripts/check_comparator_freeze.py`'s
`sha_witness()` greps the full digest and can see neither a git blob sha1 nor a
16-hex truncation** — the defect §2u names and that this rung supplied the
specimen for.

| file | lines | sha256 of the disk bytes |
|---|---:|---|
| `verification/runs/T-family/T3_runs/analyse_t3c.py` | 407 | `3fff0cc4f7073a1f8bdf20f6936022264218fdc3f1c2b55a8306ec6ebebf055a` |
| `verification/runs/T-family/T3_runs/control_t3c_p2.py` | 174 | `6bc84a609a9ecca7aacea9d2c128bd6f487e4bf550990a8a04445e3f1f58713d` |

**THE PARENTS ARE UNTOUCHED, verified by hash and not asserted** (rule 6,
§2d.11.1 condition 1):

| file | sha256 on disk now |
|---|---|
| `analyse_t3.py` | `f41c544d7552e7abfe6adeb8ff1d7ff4c14288017d36821ea3040f1158498741` |
| `analyse_t3_rff.py` | `e1aaf61b236fa72adb93a25e66f433584a95108947cb49c1e8969c4b28885997` |

### A1.6.1 WHAT THE FREEZE INSTRUMENT WILL SAY ABOUT `analyse_t3c.py`, STATED SO IT IS NOT MISREAD

`check_comparator_freeze.py` will scope this comparator to `DONE.R_m` and
`DONE.R_f` (2026-08-24) and report it **`UNFROZEN`**. **THAT IS A TRUE POSITIVE
AND IS NOT ARGUED AWAY.** Two of the three levels were complete and published in
`gate_t3.json` before this module existed. The same is true of `analyse_t3_rff.py`
and this lane **proved it** rather than inheriting the contrary claim
(`probe_freeze_flip_t3_rff.py`, commit `5b43399a`: the L-362 selftest excision
does not move the margin by one second; only breaking the `LADDER` literal flips
it, and that literal is the grader's real ladder).

**It is dispositioned by the §2d.11.1 grant under §2d.1, which is the disclosure
route §2d provides for exactly this, and not by any claim that the flag is
wrong.** What was **not** known when P-2 was written is every graded `R_ff`
quantity — `gate_t3_rff.json` was never written, and no `St_peak`, `x_peak/H`,
refinement ratio, observed order or GCI has been computed by anyone.

---

## A1.7 THE QUESTION PUT TO `verification-supervisor`, AND NOT ANSWERED HERE

**No row of T3c is graded until this is confirmed.** Heat-transfer's supervisor
has authorised this lane to build P-2; **a supervisor's authorisation is not a
charter owner's ruling on the scope of that charter owner's own grant**, and
treating it as one is the laundering `CLAUDE.md` rule 9 forbids.

> **Does replacing P-1 with P-2 sit inside the §2d.11.1 grant, or does it require
> a fresh §2d.1 petition?**
>
> Heat-transfer's reading, offered and not assumed: **it sits inside.** The grant
> is *for* repairing a control that can pass without seeing its plant; P-1 is
> measured not to do that (§A1.1); P-2 is therefore **the grant executed, not
> exceeded**. Nothing widens: `PLANT` is unchanged, no graded band moves, and the
> tolerance is the **smallest admissible** value under arms frozen before the
> question arose.
>
> **The reason we ask anyway:** §2d.11.1 condition 3 names this document's
> **"+200 ulp refusal arm"** approvingly, and we are moving the predicate that
> arm sits inside. Under P-2 the arm is **preserved and still fires** (§A1.5,
> M2) — but a ruling that cites the thing we are changing deserves a
> confirmation rather than our confidence.

---

## A1.8 COST — RULE 12, AND SANAA'S 2026-09-03 CAP LAW

**No solver compute.** The T3c grading pass reads artifacts already on disk.

| item | figure | basis |
|---|---|---|
| **ESTIMATE (POINT)** | **0.10 core-min** | comparator time, 1 rank. Basis: the refused pass measured 0.032 core-min over the 235 520-cell level; P-2 adds a second un-planted reader call and the S-1…S-9 arms, and `R_ff` is **602 128 cells**, 2.56× `R_f` |
| **HARD CAP = 3 × ESTIMATE** | **0.30 core-min** | Sanaa 2026-09-03 ~18:00Z: a hard per-run cap set by the team at ~3× its own estimate. Arithmetic shown: `0.10 → ×3 → 0.30` |
| USD at estimate | **$0.0000855** | **DERIVED, NOT MEASURED** — `0.10 / 60 × $0.0513/core-h` |
| USD at cap | **$0.0002565** | **DERIVED, NOT MEASURED** |

**An overrun stops the run** (rule 12). Predicted-versus-actual is **owed to
`docs/COST_CALIBRATION.md`** at completion and is **not** discharged here; waste,
if any, is named separately and never absorbed into the ratio.

**The $1,000 envelope is the benchmark ladder's (cfd, Rungs 0–3) and is NOT this
rung's funding basis.** T3c runs under the standing blanket and the cap above.

## A1.9 WHAT THIS AMENDMENT DOES NOT DO

- It does **not** grade anything. `gate_t3c.json` does not exist.
- It does **not** edit `analyse_t3.py` or `analyse_t3_rff.py` — hashes in §A1.6.
- It does **not** move a gate, band, threshold on a graded quantity, cap or label.
- It does **not** rule §2d.1, and does **not** treat a supervisor's go as
  verification's confirmation.
- It does **not** claim the freeze flag on `analyse_t3c.py` is a false positive.
- It does **not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).

---

## AMENDMENT — 2026-09-07 — §2ay LINEAGE LINKAGE (appended at foot; a structured pointer only)

**Predecessor: `T3` (explicit, for §2ay linkage).** This registration is the active, dated fix-successor to **T3**'s `NOT A RESULT` 4/4 (`docs/campaigns/T-family/T3_RESULTS.md` §14 — the ladder stopped at gate (1), iterative non-convergence): T3c **moves the rule-3 planted-zero control off the absolute last-ULP tolerance onto the relative convergence predicate three frozen T-family siblings already use, and re-runs the T3 R-ladder grading path.** Under `VERIFICATION_CHARTER.md` §2ay.2(b) this makes T3 a fail **carrying an active fix-successor**; the predecessor keeps its verdict (`§2an.2`) — this linkage discharges nothing and moves no verdict.

**Lines whose number changed above this section: 0.** Appended per `CLAUDE.md` rule 6 (this file is FROZEN; a dated foot-amendment, never a body edit). No gate, threshold, band, cap, label or verdict on T3 or T3c moves; records that cite this file by line are unaffected.
