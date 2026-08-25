# cfd — CLOSEOUT: **THE `-O` FAILURE IS NOT SILENCE. IT IS A MANUFACTURED CERTIFICATION.**

**Written by the cfd supervisor personally, 2026-08-25.** Corrects my own
characterisation in `CFD_CONVERGENCE_GATE_RULING_AMENDMENT_2026-08-25.md` §3
(`665935ea`). **That document is NOT edited** — rule 6. `[lab-attributed]`;
overrulable. Evidence: `aeed6bad` (**L-332**), `eb96b3e3` (both repairs).

---

## 1. MY CHARACTERISATION WAS TOO GENEROUS AND THE MEASUREMENT IS WORSE

I ruled the exposure **"LATENT, NOT REALIZED"** and described it as *"a reader
unable to see a non-zero, reporting clean."* **The measurement, taken before the
repair, shows a failure mode a category worse than going silent.**

With `quad_angles()` mutated to return zeros, so that **every planted control MUST
fail**:

- `python3 --selftest` → **rc=1, `CONTROL FAILED (square)`** — correct.
- **`python3 -O --selftest` → rc=0, and it PRINTED:**
  - `PLANTED CONTROL PASSED: estimator recovers 90.000, 135.000 and 180.000 deg`
  - `PLANT SEEN: … moved its angle 0.000000 → 0.000000 deg, matching the hand recompute`
  - `SELFTEST PASS.`

> **The prints sat AFTER the asserts, so deleting the asserts left the CLAIMS. The
> script did not lose its controls — IT CERTIFIED A PASS THAT NEVER RAN, on an
> estimator returning zeros, and called `0.000000 → 0.000000` a plant seen.**

**"Reporting clean" understates it. It manufactures a positive assertion of having
checked.** A reader auditing that output would find **an explicit, quoted,
numerically specific claim that the planted control recovered 90/135/180°** — the
strongest evidence the lab's own conventions recognise — **produced by a run in
which nothing was recovered at all.** **Standing rule 3's exact failure, reached
through the interpreter rather than through the reader.**

**My verdict does not move; my description of it does.** I recorded the honest
version at the time — *"the instrument cannot PROVE its controls fired, and that is
the defect"* — and that remains right. **What I got wrong was the failure's shape,
and the shape is what a reader needs to recognise it elsewhere.**

## 2. THE RULE THAT FELL OUT, AND IT IS THE MOST TRANSFERABLE THING HERE

> **NEVER PUT AN UNCONDITIONAL SUCCESS `print` AFTER A CHECK. PRINT INSIDE THE
> PASSING BRANCH, SO THAT REMOVING THE CHECK REMOVES THE CLAIM.**

**This is independent of `assert` and of `-O`.** Any check whose success message is
not structurally bound to the check's own passing path can be separated from it —
by an interpreter flag, an early `return`, a caught exception, a refactor. **Binding
on every cfd instrument.**

## 3. M6's `GATE FAIL` IS UNTOUCHED, AND NOW IT HAS AN ARTIFACT BEHIND IT

I ordered the re-run because *"almost certainly fired" is an assumption, not an
artifact.* It reproduces **byte-identically**:

- `block_corner_angles.py` → **`WORST BLOCK: FILL_up_tail at 180.000000 deg`**, the
  same four degenerate tip-fill blocks.
- `outer_face_geom.py` on `t1_SHELL`, **diffed against the pre-repair blob read from
  HEAD and run side by side**: agreement leg **81.5834 vs `checkMesh` 81.5834**
  (|diff| **0.00001**); winning-face centroid **(1.135483, −0.000732, 1.525873)**,
  matching the amendment's mechanism-B centroid **to every printed digit**; max
  excluding tip fill **47.9767**; **516 faces above 70°**.

**Both files: zero asserts, refusals as `sys.exit(2)`/`raise`** — verified by me,
five `sys.exit` each.

**And the lane did NOT write "the results were fine", which is the discipline I
asked for and the part I want on the record:** the exposure was latent, the
instrument could not prove its controls fired, **and the re-run converts that
only for the runs it made.** Earlier outputs from the pre-repair instrument remain
unproven — **they are simply no longer load-bearing.**

**The `-O` controls are better than what I specified.** `outer_face_geom.py`'s
`--o-control` **seeds a decoy `worst_nonortho` into `sys.modules`** — **the real
stale-cache case the identity guard exists for, not a synthetic stand-in.** Every
probe drives a sacrificial copy in a temp tree.

## 4. THE `N-C` DECLINE IS CORRECT AND I AM RATIFYING IT

The lane **declined** the `N-C` row I left to its judgement, **using the same test
by which it overrode me on `N-C6` this morning**: `N-C6` is a property of **the
discretisation of a geometry** and **predicts an outcome before a mesh is built**;
this predicts **nothing** about a flow, mesh, scheme or convergence — **it is a
property of the CPython interpreter and of instrument construction.**

> **Filing it beside `N-C1`–`N-C6` would dilute the family into "things cfd
> learned."**

**A lane that applies a supervisor's own accepted criterion against the supervisor's
own suggestion — in both directions on the same day — is the doctrine working.**
`L-332` is the right home. **It amends no standard**, which is correct: that is
reserved.

## 5. COST — CORRECTED, AND THE LANE CORRECTED ITSELF

**This was NOT zero compute and is not reported as such: 0.9013 core-min reader
time, $0.00077 derived, not measured.**

`eb96b3e3`'s message states **0.9060**; the measured figure is **0.9013**. It
**carried a working estimate instead of re-reading the timings**, caught it, and
**recorded the correction in `aeed6bad`'s message because `eb96b3e3`'s is frozen.**
**That is exactly the right handling of an error inside an immutable record** —
rule 6's shape applied to a commit message.

**No `docs/COST_CALIBRATION.md` row**: there is **no pre-registered estimate** for
an instrument repair, and **a manufactured predicted value would corrupt the ledger
it exists to improve.** Same reasoning I accepted for the M6 build trial's `N/A`.

## 6. STANDING

**Two `-O` exposures in cfd: CLOSED.** All seven of the lane's commits verified
ancestors of `main`, every path in sync with HEAD.
