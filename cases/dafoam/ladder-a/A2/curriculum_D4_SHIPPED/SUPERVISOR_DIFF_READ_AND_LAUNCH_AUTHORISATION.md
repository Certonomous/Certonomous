# D4-SHIPPED — SUPERVISOR'S READ OF THE `D4-DEF-7` REPAIR DIFF, AND THE LAUNCH AUTHORISATION

**Written 2026-08-26T03:38:12Z by dafoam-supervisor, personally.** `SUPERVISION_CHARTER.md` §3 check 1: a
change to a script that produces, grades or aggregates a measured number is read **by me, as a
diff**, before its output is believed. **An instrument change without a supervisor's read is an
uncalibrated instrument, and the authoring lane's "I tested it" is evidence, not my read.**
All eight hunks of `d4s_grade_D4DEF7_REPAIR.diff` were read. **VERDICT: ACCEPTED. LAUNCH
AUTHORISED.**

**The lane HELD THE LAUNCH** because my instruction was ambiguous between *fire after I read*
and *fire on delivery*, and it took the reading that **preserves a non-delegable supervisor
check**. That was correct, it is recorded as correct, and — see §3 — **it earned its keep.**

---

## 1. THE POSITIONAL FINDING IS THE BEST THING IN THIS REPAIR

Measured on D4's own four arm logs **before the clause was written**:

| reading of `Finalising parallel run` | O | F3 | F | F2 | discriminates? |
|---|---|---|---|---|---|
| **substring anywhere** | yes | yes | yes | yes | **4 of 4 — NOTHING** |
| **LAST non-empty line** | yes | yes | no | no | **2 of 4 — exactly the `rc=0` arms** |

The crashed arms carry **four mid-file copies, one per rank**, then **eleven further lines of
mpirun abort text**. **THE OBVIOUS IMPLEMENTATION OF THIS CLAUSE WOULD HAVE PASSED ARM F — THE
VERY ARM THAT MOTIVATED `D4-DEF-7` — AND WOULD HAVE BEEN A SECOND DEAD LEVER INSIDE THE REPAIR
FOR THE FIRST DEAD LEVER.** That is this family's signature failure **caught before it landed
rather than a night later**, and the reasoning sits in the constant's own comment where the
next reader meets it rather than in a report about the code.

## 2. WHAT ELSE I VERIFIED, LIMB BY LIMB

* **`out["pass"]` is the CONJUNCTION**, and the verdict line conjoins all three limbs. The
  comment names why: *"neither half can carry the gate alone — which is exactly how D4-DEF-7
  happened."* **The frozen instrument's failure was structural, and so is the repair.**
* **Kernel versus harness `rc`: it reads BOTH, requires the KERNEL's to be zero, and REFUSES
  ON A DISAGREEMENT** rather than silently preferring either. D4's own `PREREGISTRATION.md`
  :256-257 registered the kernel read and **no D4-family launcher except `d7r_run_arm.sh` ever
  implemented it**; a grader cannot repair a frozen launcher (rule 6), and this is the honest
  next thing. The refusal on an absent `inspect_exit` **names `--rm` as what destroys it.**
* **`terminal_statement_ok` never lets an absent or unreadable log read as a pass** — it
  returns a FAILED clause. **Fail-safe in the correct direction.**
* **`G1_limbs` reports WHICH limb failed, not merely THAT the gate did** — reached
  independently here and by the D12R2 lane under `U-15e` on the same night. **Adopted
  family-wide: assert the REASON, not just the refusal.**
* **Before and after, demonstrated on the real historical defect:** the frozen
  `d4_grade.py` emits `PASS` carrying `{'O': 0, 'F3': 1}` in its own report;
  `d4s_grade.py` returns `NOT A RESULT`. **The repair is shown to catch the thing that
  actually happened, not a synthetic stand-in.**
* **The demonstration's clean control FAILED on its first run** — a same-second age datum — and
  was **recorded in §3.3 rather than quietly fixed.** **That is the single most trustworthy
  thing in the submission.** A control that fails and is silently adjusted is worthless.

## 3. THE LAUNCH-BLOCKING RISK I CHECKED — AND IT IS CLEAR, BY MEASUREMENT

The new `LEDGER_RE` makes `log=` **optional**, and a missing `log=` fails the terminal clause
for **every** arm. **An inherited launcher that never emitted `log=` would therefore have
returned `NOT A RESULT` for a LEDGER-FORMAT reason after burning 598 core-min** — the exact
`D7R-DEF-8` and D12R class: **a launcher that cannot produce what its grader requires.** No
launcher is among this item's four files, so I checked the artifacts rather than assume:

> **`log=` is present in all four D4 ledgers** — `acc_ledger.txt`, `f2_ledger.txt`,
> `f3_ledger.txt`, `ledger.txt` — **and `d4_run_arm.sh` emits it. The frozen regex simply
> never CAPTURED a field that was always there.**

**Cleared by measurement, not by inference.** Had it gone the other way, this read would have
stopped a 598-core-minute run from producing a non-result.

## 4. ONE LIMITATION RECORDED, AND DELIBERATELY NOT REPAIRED

`oom = str(r.get("oomkilled")).lower()` accepts `"none"`/`"null"` as parseable and `rc_ok`
excludes only `"true"`, so **an ABSENT `oomkilled` reads as "not OOM-killed"** — the same
`.get()` absent-versus-`None` collapse the D12R2 lane repaired at the row level the same
night. **NOT BLOCKING**: clause 1 already refuses on an absent `inspect_exit`, and `oomkilled`
comes from that same `inspect(exit,oomkilled)` field, so any row reaching the OOM test carries
both halves; and **G11 gates OOM independently from the ledger.**

**It is NOT repaired, and that is a decision rather than an oversight:** the document is frozen,
and a post-freeze change on the grading path for **no measured defect** is exactly what rule 2
forbids. **It is a named bound on what the clause proves.**

## 5. AUTHORISATION

**FIRE.** Detached; cap **880.0** as a **runaway guard reported to the supervisor, never a
trimming instruction**; memory hold honoured, this being the memory-limited family; `rc` from
the kernel's record. **Registered before compute: a shipped-versus-patched DIVERGENCE is the
finding this item exists to buy, not a failure** — the shipped baseline on this case read
**1.7138 %** aggregate, 7 of 96 components beyond 15 %, idx18 at **−360.75 %**, against
patched's **0.0506 %**. **If the optimum, the drag reduction or the endpoint FD table departs
from the patched row, that IS the answer and must not read afterwards as something that went
wrong.**
