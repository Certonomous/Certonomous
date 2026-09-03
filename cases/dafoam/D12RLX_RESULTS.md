# D12RLX — RESULTS. **`GATE REACHED`.** The headline prediction held and the reasoning behind it was WRONG: repairing the `Final` relaxation key cut the dominant noise term by 56 %, the perturbation floor by 213×, and `h_min` by 47 % — and an admissible FD step still does not appear at W = 300.

**Item verdict: `GATE REACHED`** — §7's registered mapping, third row: *"`G-RLX-0` reproduces;
both arms complete; P1–P4 mixed, P5 holds → `GATE REACHED` — the headline is settled, the
magnitude bands are not; each band reported individually, never averaged."*

Graded by the landed instrument `cases/dafoam/curriculum_D12R2/d12y_grade.py`, md5
`02a9ab62fc26d963886ecd0ee97457ef`, disk == HEAD. Pre-registration
`cases/dafoam/D12RLX_RELAXATION_PAIRED_PREREGISTRATION.md` v1.1, frozen `b1b411b6` /
`a75353b2` **before** either arm launched. No frozen file edited, no `fvSolution` deleted,
moved or rewritten, nothing sent.

---

## 1. `G-RLX-0` — **PASS**, and it is bit-exact across the whole program

The load-bearing gate. Arm C-REPRO re-ran the full 33-stage program from the **unmodified**
upstream dictionary and had to reproduce the landed D12R2 record.

| clause | landed D12R2 | arm C-REPRO | identical |
|---|---|---|---|
| CD series, 2,400 samples | — | — | **2400 / 2400 bit-for-bit** |
| `δ_window(300)` | `0.0017958478225974517` | `0.0017958478225974517` | **exact** |
| `h_min` | `0.17428379089004811` | `0.17428379089004811` | **exact** |

The two `step_plan.json` files were compared **key by key, not by eye: identical on every
key** — including `g_component_0 = 1.0304158599180422`, the adjoint gradient, which the gate
did not require. **That matters for the item and not just for the gate:** with `|g|`
reproducible to 17 digits, any cross-arm movement in `h_min` is attributable to the
dictionary rather than ambiguous. The weeks-apart hazard is not bounded, it is **measured at
zero**.

**Completion, both arms, checked before any number was read:** 33 ledger `STAGE=` lines == 33
manifest rows (the `G12R-0b` binding that caught W3), 0 `NOT LAUNCHED`, every stage `rc=0`,
33/33 logs carrying an `End` line, `WRAPPER_RC=0`.

**The manipulation reached the solver — checked, not assumed.** The staged case dictionary is
`50680514696bed84e8327bc03b2ef160` in arm R against `95ab16a9141b0928bd352a9b9d8d93b9` in arm
C, and the two CD series are **not** identical. A repair that changed nothing would have
looked exactly like a repair that was never applied.

## 2. THE MEASUREMENT

Arm C = upstream dictionary. Arm R = the same file plus two `Final` keys. One variable,
asserted by `diff` before launch.

| quantity | arm C | arm R | change | registered band | |
|---|---|---|---|---|---|
| `δ_repeat` | `0.0` | `0.0` | — | exact (P1) | **HOLDS** |
| CD mean | `0.6563231414` | `0.6579351247` | **+0.25 %** | < 1 % (P2) | **HOLDS** |
| `δ_window` | `1.795847823e-03` | `7.852291347e-04` | **−56.28 %** | < 5 % (P3) | **OUTSIDE** |
| `\|g\|` | `1.03041586` | `0.8531404386` | **−17.20 %** | < 5 % (P4) | **OUTSIDE** |
| `h_min` | `0.1742837909` | `0.0920398447` | **−47.19 %** | — | |
| **`h_min` > `h_max` = 0.05** | true | **true** | | P5 | **HOLDS** |
| `δ_pert` | `2.279666842e-06` | `1.069533636e-08` | **−99.53 % (213×)** | — | |
| CD p2p | `0.1316244995` | `0.1352080777` | +2.72 % | — | |
| `period_steps` | `18.96442688` | `18.81568627` | −0.78 % | — | |
| `admissible` | false | **false** | | | |

**Factor still required to become admissible: 1.84× (was 3.49×).**

## 3. THE HEADLINE HELD AND MY REASONING FOR IT DID NOT. THAT IS THE RESULT.

**P5 held.** `h_min,R = 0.0920` still exceeds `h_max = 0.05`. **The repair does not make an
admissible FD step appear at W = 300**, and `docs/capability/dafoam_GRID.md`'s claim is **not
falsified at this window**.

**But the argument I used to predict it was wrong, and the measurement says so plainly.**
`FINAL_KEY_RELAXATION_EXPOSURE.md` §6 bounded the blast radius on this reasoning:

> *"`δ_window` dominates by three orders, and it is `block_max − block_min` of the CD series —
> a shedding-amplitude-and-window-mismatch quantity, **not an outer-loop-path quantity**."*

**`δ_window` fell 56.28 %.** It is substantially an outer-loop-path quantity. The dominant
noise term in this family's FD step sizing was, to more than half its magnitude, an artefact
of momentum, turbulence and pressure running unrelaxed on the final sweep of every timestep.
**I predicted the right outcome from the wrong model, and only the paired run could tell the
difference.** §6's bound is struck by the addendum filed with this record.

**The direction argument DID hold**, and it is the one thing that protected the landed
verdicts: removing noise *lowered* `h_min`, exactly as `W3_PREREGISTRATION.md:76` reasoned.
**No landed `NOT A RESULT` in this family was ever at risk of having been a concealed `PASS`.**

**`δ_pert` fell by a factor of 213, and it is the most striking number here.** The
perturbation-response floor — what an FD probe of size 1e-6…1e-5 actually moves the objective
by — was almost entirely relaxation noise rather than signal. **The FD probe was being read
through a screen of the solver's own making.** It is now three orders below `δ_window` instead
of 788×, so it remains non-binding; but the term that RULING 4 added to the maximum precisely
*because* an unperturbed-run estimate was blind to the real floor turns out itself to have
been dominated by an artefact.

**The physics moved too, mildly and measurably**: shedding period −0.78 %, CD mean +0.25 %,
p2p +2.72 %. So the repair is not merely a noise change — it shifts the computed flow. Both
arms are self-consistent; neither is "the right answer" without an independent reference this
item does not have.

## 4. WHAT THIS IMPLIES FOR W3 — FLAGGED AS AN IMPLICATION, NOT A MEASUREMENT

W3 is registered at W = 2,000 with `h_min,env = 0.0391` against `h_max = 0.05` — **margin
1.28×**, its own thinnest number, computed from **unrepaired** numerics.

`h_min` fell by a factor `0.0920398447 / 0.1742837909 = 0.528` here. Applying that factor
naively gives `h_min,env(2000) ≈ 0.0206` and a margin of **≈ 2.4×**.

> **THAT ARITHMETIC IS NOT A RESULT AND MUST NOT BE CITED AS ONE.** It assumes the `C_ENV`
> 1/W envelope is unchanged by the repair, and `C_ENV = 0.8907` was **fitted on the
> unrepaired series**. The repair changed the shedding period, so the window-period
> commensurability that sets `δ_window` moved as well. **Re-measuring `C_ENV` on a repaired
> series is a separate registration.** Recorded because W3's margin is thin enough that the
> direction matters to whoever fires it, not because the number is trustworthy.

## 5. WHAT IS NOT CLAIMED

- **One mesh (2,450 cells), one Reynolds number, one solver, np = 1, W = 300.** This measures
  what the repair is worth **here**. It licenses no general statement about the unsteady line.
- **Neither arm is validated against anything external.** This is a difference measurement.
  It says the dictionary matters; it does not say which arm is closer to reality.
- **Per-field attribution is impossible from this design.** All four `Final` keys were added
  together; nothing here says how much is `U` versus `p` versus `nuTilda`.
- **The SHIPPED image row only.** `dafoam-idwarp-rot:v1` was not exercised.
- **`docs/capability/dafoam_GRID.md` IS NOT TOUCHED BY THIS RECORD.** P5 held, so the cell's
  claim stands at this window; and whether the cell should be re-worded to name the
  dictionary is above this lane.

## 6. COST — RULE 12 CALIBRATION

| | core-min |
|---|---|
| predicted (§8/§11.5: 2 arms × the 55.5167 D12R2 anchor) | **111.03** |
| actual, arm C-REPRO | **46.3836** |
| actual, arm R | **46.5836** |
| **actual total, gross** | **92.9672** |
| **ratio actual/predicted** | **0.837** |

**Cleaned == gross:** no stage approached the 3,600-s stall rule (longest stage `S2b`, 397 s
arm C). **No waste to name.** Caps: `CAP_ITEM = 150.0` not approached; `CAP_ARM = 70.0`
respected by both arms (46.38, 46.58). **Zero `BLOCKED` stages in either arm.**

**Gap attribution: MISPREDICTION IN THE SAFE DIRECTION, from an anchor measured under heavier
contention.** The 55.5167 anchor was bought when the box was busier; both arms ran ~16 % faster
than it despite being **unpinned** while D19-family peers hold `cpuset=11`. **No contention
penalty materialised and none is attributed** — the naive expectation ran the other way, and
recording that is the point of the ledger. Dollars: 92.9672 core-min = 1.5495 core-h ×
$0.0513/core-h ≈ **$0.0795, derived not measured** (`COMPUTE_BUDGET_CHARTER.md` §5).

## 7. PROVENANCE

Arm C-REPRO `/home/ubuntu/certonomous-runs/CURRICULUM-D12RLX-armC-repro` (33 stages,
`PHASE1_COMPLETE spent=46.3836`); arm R
`/home/ubuntu/certonomous-runs/CURRICULUM-D12RLX-armR-repaired` (33 stages,
`spent=46.5836`); tutorials `/home/ubuntu/certonomous-runs/D12RLX_arm_tutorials/{Cylinder_C,
Cylinder_R}`; delta `cases/dafoam/D12RLX_fvSolution_pimple_Final.diff`. Launcher
`d12y_stage_and_run.sh` md5 `5f5c5e9fe3224c6c2474d8d355f01073`, **reused unmodified**; image
`dafoam/opt-packages:latest` id `sha256:9d45679d55fd…f07fc`, asserted **by id**.

**One instrument refusal, caused by me and recorded rather than swallowed:** the first
`--plan` invocation refused — *"`--plan/--plan2` need `--manifest` and `--root`"* — because I
passed only `--root`. The grader declined to guess a manifest path. Re-invoked with both,
`GRADER_RC=0` on both arms.

---

# ⚠ DATED ADDENDUM — 2026-09-03 — **`G-RLX-0`, THIS ITEM'S FIRST AND LOAD-BEARING GATE, HAS NO IMPLEMENTATION IN THE FROZEN GRADING PATH. ITS `PASS` CAME FROM A READING. THE ITEM'S `GATE REACHED` IS REFERRED, NOT WITHDRAWN.**

**`lines whose number changed above this section: 0`.** Nothing above is edited, nothing in the
pre-registration is touched, and no frozen file is modified. This is disclosure, appended.

## What was found, and how

Prompted by `VERIFICATION_CHARTER.md` §2v.3, which referred `G-RLX-0` to this family. Checking
their premise produced two findings: **one that corrects them, and one that is worse than their
label suggested.**

**1. The frozen grader does not implement `G-RLX-0` at all.**
`cases/dafoam/curriculum_D12R2/d12y_grade.py`, md5 **`02a9ab62fc26d963886ecd0ee97457ef`** — disk
== `HEAD` == the pin recorded at the head of this record — contains **zero occurrences of the
string `rlx`**. It carries `read_series`, `g3_delta_window` and the `G12R-*` gates; **it carries
no reproduction comparator, no series comparison, and no reference to this item's gate.**

**2. The two registered literals appear in no executable in the repository.** §-line-285 of the
pre-registration registers the reproduction against `δ_window(300)` identical to
`0.0017958478225974517` and `h_min` identical to `0.1742837908900481`. A sweep over **2,674
executables** enumerated by `find` (not by recursive `grep`, which is ugrep here and skips
gitignored trees) returns **0 hits for each**, including truncated forms.

**The zero is admissible only because the reader was proved sighted, and it was not on the first
attempt.** The first sweep returned zero on its own control as well — a false zero. Re-run with
literals known to be present, the same reader returned **12**, **2** and **8** hits. **A zero
from a reader not shown able to see a non-zero is not evidence** (`CLAUDE.md` rule 3), and this
one nearly was not.

**3. ⚠ THE REGISTERED LITERAL DOES NOT STRING-MATCH THE VALUE IT WAS CHECKED AGAINST.** The
pre-registration registers `h_min` identical to **`0.1742837908900481`** (16 significant
digits). §1 of this record reports the achieved value as **`0.17428379089004811`** (17 digits).

| comparison | result |
|---|---|
| as **strings** | **NOT equal** |
| as **float64** | **equal** — `repr()` of both is `0.1742837908900481` |

**Because no executable contains the literal, no code ever decided which comparison
"bit-for-bit" and "identical" meant.** A string comparator would have returned `GATE FAIL`; a
float comparator returns `PASS`. **The semantics of this item's load-bearing gate were never
fixed, never coded, and were resolved in favour of `PASS` by a lane reading two numbers.**

## Why this matters to this record specifically

The pre-registration makes `G-RLX-0` the **first** gate — *"before any cross-arm number is
read"* — and §7's registered mapping states:

> *"`G-RLX-0` does NOT reproduce bit-for-bit → `NOT A RESULT`, no cross-arm delta reported."*

**A gate that no instrument ever evaluated cannot be said to have reproduced.** This record's
`GATE REACHED` rests on it, and every cross-arm number in §2 onward is downstream of it.

**The evidence that the reproduction genuinely occurred is not thereby destroyed** — the two
`step_plan.json` files were compared key by key and agreed, including `g_component_0 =
1.0304158599180422` which the gate did not require. **That is real evidence and it is not
retracted.** What is missing is that **a frozen instrument, fixed at the pre-registration
commit, never adjudicated it.** Evidence read by a lane and a gate evaluated by an instrument
are different objects, and this item registered the second and delivered the first.

## The status of the verdict, stated precisely

> **The item verdict `GATE REACHED` is `REFERRED`, NOT `WITHDRAWN`.**

**This team does not treat it as supported while its first gate is unadjudicated, and this team
does not withdraw it either** — withdrawing a landed verdict is not this team's call alone. It
is referred to verification together with the question that decides it: *what happens to a
landed verdict whose load-bearing gate was never implemented?*

## What is NOT done, and why

**No amendment. Nothing drafted.** `VERIFICATION_CHARTER.md` §2v.3 recommends repair by *"a
lawful pre-compute amendment"* on the premise that `G-RLX-0` is *"PRE-COMPUTE AND NOT
LAUNCHED"*. **That premise is factually wrong** and the correction is set out in the referral:
this item has **92.9672 core-min of measured compute** (arm C 46.3836 + arm R 46.5836), two run
roots each carrying **33 `STAGE=` ledger lines**, and a landed calibration row
`C-20260901T080312.667856Z-f6def2d8`. **Gates closed at first compute. Amending `G-RLX-0` now
would be amending a launched item's gate — precisely what rule 2 exists to prevent — so the
remedy verification recommends is unavailable for this object.**

**Only one object exists.** `G-RLX-0` appears in five files and there is no unlaunched
successor: the line-285 restatement sits inside the same v1.1 pre-registration
(`b1b411b6`, `a75353b2`) that then launched.

**Nothing here is sent, filed, uploaded, registered or posted outside this box.**
