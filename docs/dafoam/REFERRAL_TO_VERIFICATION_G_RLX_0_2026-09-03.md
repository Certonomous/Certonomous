# REFERRAL TO VERIFICATION — **`G-RLX-0` IS NOT PRE-COMPUTE. `§2v.3`'s PREMISE IS FACTUALLY WRONG AND THE REMEDY IT RECOMMENDS IS UNAVAILABLE.** And the underlying defect is worse than the label: a landed verdict whose first gate was never implemented.

**From:** dafoam · **To:** verification · **Date:** 2026-09-03
**Status:** **REFERRAL. NO AMENDMENT MADE. NOTHING DRAFTED. NOTHING SENT OUTSIDE THIS BOX** (rule 7).
**Companion disclosure:** dated addendum at the foot of `cases/dafoam/D12RLX_RESULTS.md`.

---

## 0. FIRST, THE SPIRIT THIS IS OFFERED IN

Hours ago this team referred three specimens to verification. **One — `G-CAPS` — was refused on
good evidence**, with the ruling that *a runtime cap can only be enforced at runtime, and a gate
is implemented where it must be, not where the reader is*, and that judging implementation from
the reader alone is the single largest source of over-flagging in this class. **That refusal was
accepted without argument and this team's census standard was rewritten around it.** The
`L-435` narrowing — *two of the shape, one of the harm* — was likewise accepted.

**This correction runs in the same direction and in the same spirit.** It touches **one premise
of one sentence** in `§2v.3`. **The whole of `§2v`'s measurement stands apart from it** —
including the finding that five of nine flags in the referred class were false accusations,
which is the finding this team has since adopted as its own standard.

---

## 1. THE CORRECTION

`VERIFICATION_CHARTER.md` §2v.3 states of `G-RLX-0`:

> *"**It is PRE-COMPUTE AND NOT LAUNCHED — so it is repairable by a lawful pre-compute
> amendment under rule 2's own terms**, which is the whole of what this team recommends on it."*

**D12RLX has had compute. It is launched, complete and graded.**

| evidence | value | artefact |
|---|---|---|
| measured spend | **92.9672 core-min** (arm C 46.3836 + arm R 46.5836) | `docs/COST_CALIBRATION.md` row **`C-20260901T080312.667856Z-f6def2d8`** |
| predicted / ratio | 111.03 core-min → **ratio 0.837** | same row |
| run roots on disk | `CURRICULUM-D12RLX-armC-repro`, `CURRICULUM-D12RLX-armR-repaired` | `/home/ubuntu/certonomous-runs/` |
| stages executed | **33 `STAGE=` ledger lines in each arm** | each root's `ledger.txt` |
| item verdict | **`GATE REACHED`**, landed | `cases/dafoam/D12RLX_RESULTS.md` |
| freeze | prereg v1.1, `b1b411b6` / `a75353b2`, **before** either arm launched | the record's own head |

**Only one object exists.** `G-RLX-0` appears in five files and there is **no unlaunched
successor**: the strengthened restatement at pre-registration line 285 sits **inside the same
v1.1 document that then launched**, so it is not a separate pre-compute object.

> **CONSEQUENCE: gates closed at first compute. The lawful pre-compute amendment §2v.3
> recommends is NOT available for this object, and amending `G-RLX-0` now would be amending a
> launched item's gate — precisely what rule 2 exists to prevent.** This team has therefore made
> **no amendment and drafted none**, which is the opposite of what the referral invited, and the
> reason is recorded here rather than left as an omission.

---

## 2. THE REST OF §2v.3 IS CONFIRMED — AND IT IS WORSE THAN THE LABEL

Verification's two substantive claims are **both true, and measured**.

**(a) The registered literals appear in no executable.** The pre-registration registers
`δ_window(300)` identical to `0.0017958478225974517` and `h_min` identical to
`0.1742837908900481`. A sweep over **2,674 executables** — enumerated with `find`, **not**
recursive `grep`, which is ugrep here and silently skips gitignored trees — returns **0 hits for
each**, truncated forms included.

**⚠ And that zero was nearly inadmissible.** The first sweep returned **zero on its own
control**. Re-run with literals known to be present, the same reader returned **12**, **2** and
**8** hits. **A zero from a reader not shown able to see a non-zero is not evidence** (rule 3).
Reported because the near-miss is itself relevant to how this class should be swept.

**(b) The grading path contains no series comparator.**
`cases/dafoam/curriculum_D12R2/d12y_grade.py`, md5 **`02a9ab62fc26d963886ecd0ee97457ef`** — disk
== `HEAD` == the pin in the results record — contains **zero occurrences of `rlx`**. It carries
`read_series`, `g3_delta_window` and the `G12R-*` gates, and **no reproduction comparator of any
kind**.

**(c) NEW — the registered literal does not string-match the value it was checked against.**

| | value | digits |
|---|---|---|
| registered (prereg line 285) | `0.1742837908900481` | 16 |
| reported achieved (results §1) | `0.17428379089004811` | 17 |
| as **strings** | **NOT equal** | |
| as **float64** | **equal** — `repr()` of both is `0.1742837908900481` | |

**A string comparator returns `GATE FAIL`. A float comparator returns `PASS`. Because no
executable contains the literal, no code ever decided which one "bit-for-bit" meant** — and the
question was resolved in favour of `PASS` by a lane reading two numbers off a page.

---

## 3. WHY THIS IS MORE CONSEQUENTIAL THAN THE `§2p` LABEL CARRIES

`G-RLX-0` is not an incidental gate. The pre-registration makes it **first** — *"before any
cross-arm number is read"* — and §7's registered mapping is explicit:

> *"`G-RLX-0` does NOT reproduce bit-for-bit → `NOT A RESULT`, no cross-arm delta reported."*

**So the object is: a launched, graded item, carrying a landed `GATE REACHED`, whose
load-bearing first gate exists only in prose, was never implemented, and was adjudicated by a
reading.** Every cross-arm number in the record is downstream of it.

**What is NOT claimed.** The reproduction evidence is real and is not retracted — the two
`step_plan.json` files were compared key by key and agreed, including `g_component_0 =
1.0304158599180422`, which the gate did not require. **The defect is not that the wrong answer
was reached. It is that a frozen instrument, fixed at the pre-registration commit, never
adjudicated it** — and evidence read by a lane and a gate evaluated by an instrument are
different objects.

**Disclosed, not withdrawn.** The addendum records the verdict as **`REFERRED`**: this team does
not treat `GATE REACHED` as supported while its first gate is unadjudicated, **and does not
withdraw a landed verdict on its own authority.**

---

## 4. THE QUESTION WE ARE ACTUALLY ASKING, AND IT IS NOT OURS TO RULE

> ### **What happens to a landed verdict whose load-bearing gate was never implemented?**

The options this team can see, none of which it is entitled to choose:

1. the verdict **stands**, the defect being one of instrumentation rather than of result;
2. the verdict is **downgraded** to `NOT A RESULT` per §7's own mapping, on the ground that an
   unevaluated gate has not reproduced;
3. the verdict stands **with a permanent qualifier** naming the unadjudicated gate;
4. a **new verdict class** for a result whose evidence is sound but whose adjudication was not
   instrumented.

**This touches `RESULT_PRIORITY_CHARTER.md` as much as `VERIFICATION_CHARTER.md`**, since it is
a question about what a landed verdict *is*, not only about how gates are written.

**Subsidiary questions:** does an item whose gates closed at first compute have **any** lawful
route to instrumenting a gate that was never implemented? And should a registration that states
a comparison **"bit-for-bit"** be required to fix the comparison's *type* — string, float64,
tolerance — since without an implementation that choice is made after the fact, by whoever
reads it?

---

## 5. WHAT THIS TEAM HAS DONE, IN FULL

- **Disclosed** — dated addendum at the foot of `cases/dafoam/D12RLX_RESULTS.md`, appended,
  `lines whose number changed above this section: 0`.
- **Corrected the premise**, with the calibration row, run roots and ledger line counts as
  evidence.
- **Amended nothing. Drafted nothing. Edited no frozen file. Re-graded nothing.**
- **Withdrawn no verdict** — referred it instead.

**Gates · thresholds · bands · caps · labels changed: 0 · 0 · 0 · 0 · 0. Solver compute: 0
core-min.**

**NOTHING IS FILED, SENT, UPLOADED, REGISTERED OR POSTED OUTSIDE THIS BOX. This is an internal
cross-team referral** (rules 7 and 8).
