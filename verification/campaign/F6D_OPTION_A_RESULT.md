# F6d Option A — result, under a VOID

**Pre-registered at `08822fb2`** (`F6D_OPTION_A_PREREGISTRATION.md`), with the
deviation record at `0a504f63`, the gate escalation at `7fedb88b`, and the
chief's rulings plus the Option C funding rule fixed at **`ce6a66b4` — committed
before the final cases were read.**

All 16 cases ran to `endTime 16000`. 16 of 16 reached `End`.

---

## 1. The experiment is VOID

The pre-registered validity gate fired: control **`d0.2_s000` moved −0.491 x/h**
against a 0.25 threshold.

**Ruled on the literal reading (chief, decision 1).** Not because the mechanism
the gate names is present — §6.2 of the pre-registration shows by measurement
that it is not — but because *"the premise turned out to be false"* is a
conclusion reached **after seeing the outcome**, and **a gate that can be
dissolved by post-hoc argument is not a gate.** If that move is available once
it is available always.

**The gate was not wrong to fire.** Its *trigger* caught something real — the
control was not a control. Only its *stated inference* ("a restart transient")
was named badly. The fix belongs in the next pre-registration and was not
applied to this one.

---

## 2. What survives the VOID

A control exists to isolate a **difference**. A claim that is not a difference
claim never needed one. Everything below is **within-case or univariate**.

### 2.1 Not one of the 13 members reached a settled state

Settledness is the pre-registered metric — peak-to-peak swing of the driving
pressure gradient over the final 500 iterations, normalised by the median |pg|
over the second half. **Settled** was fixed in advance at **< 0.10**.

| case | settledness at 16,000 | settled? |
| --- | --- | --- |
| `null` *(unperturbed control)* | **0.031** | **YES** |
| `d0.2_s020` | 0.223 | no |
| `d0.2_s027` *(control)* | 0.253 | no |
| `d0.2_s036` | 0.295 | no |
| `d0.2_s000` *(control)* | 0.340 | no |
| `d0.6_s022` | 1.412 | no |
| `d0.6_s035` | 1.648 | no |
| `d0.2_s015` | 1.792 | no |
| `d0.6_s039` | 2.243 | no |
| `d0.6_s021` | 2.439 | no |
| `d0.6_s007` | 2.477 | no |
| `d0.2_s019` | 2.698 | no |
| `d0.2_s023` | 2.727 | no |
| `d0.6_s011` | 3.196 | no |
| `d0.6_s000` | 3.250 | no |
| `d0.2_s022` | 4.825 | no |

**Zero of the 13 members settled after 16,000 iterations — four times the
published budget.** Several got *worse*: `d0.2_s022` ends at 4.825.

### 2.2 A case chosen for being well-behaved destabilised

`d0.2_s000` was selected as a control **because it was among the best-settled
members of all 84** — published swing 0.038, second only to `null` itself.
Continued, its reattachment wandered from 6.337 through 5.84, 5.34, 5.85, 5.00,
an excursion beyond **1.3 x/h**, ending at settledness 0.340.

This is one case measured against its own earlier state, so it stands under the
VOID. **A member that looked settled at 4,000 iterations was passing through a
quiet phase of an unsteady flow, not sitting at a steady solution.** It is the
strongest single observation in the experiment, and it is stronger for having
come from a case picked to be well-behaved — and for having cost the experiment
its own validity.

### 2.3 The headline, in the words the chief pre-registered

> **The only settled member of the ensemble is the only unperturbed one.**

`null` — the sole run with `R_sample = R_bar` — is the only case of 16 below the
settledness threshold, at **0.031**. **It says the perturbation, not the
numerics, is what prevents settling.** The solver, mesh, restart path and
iteration budget are identical across all 16; the perturbation is the only thing
that differs, and it is the thing that is present in every unsettled case and
absent from the settled one.

---

## 3. What does NOT survive

**The comparative — how many members moved, and in which direction — is void.**
That is precisely the difference claim the validity gate existed to license. It
is **not** reported here as a verdict, and it is **not** restated as a
description. The raw per-member deltas remain in
`f6d_random_matrix_uq/option_a_result.json` for whoever re-registers the
question; they must not be cited from there as a finding.

**And one point in that file is not this experiment's output.** `d0.2_s000`'s
trajectory contains `[7500, 5.834774]`, written by the duplicate solver of the
launcher collision, not by the run — established per-snapshot in
`F6D_COLLISION_INDEPENDENCE_CHECK.md` §2 and carried in the JSON itself under
that row's `contamination` key. It is **labelled, not removed**: filter it if
you need single-writer provenance, and say that you filtered it. Nothing
reported in this document depends on it — see §5's addendum for the arithmetic.

To be used, it must be **re-registered and re-earned** — with a gate whose
trigger and whose stated inference agree, e.g. voiding on the *unperturbed*
control moving, or on all controls moving together.

---

## 4. Option C — NOT funded, by the rule fixed before these numbers were read

The rule (`ce6a66b4`, §6.3): *"If at completion no member of the 13 has settled →
Option C is NOT funded. 25.7 core-hours buys 80 more arbitrary phases of an
unsteady flow. A longer run of a thing that does not converge is not more
evidence; it is the same evidence at higher cost."*

**No member settled. Option C is not funded.** Note the asymmetry that makes
this safe: the evidence that survives the VOID points at **Outcome 3**, and the
evidence that died is what would have supported Outcome 1 — so the VOID can only
stop spending, never start it.

**Consequence for the audit's claims.** They do **not** move. The nine graded
INVALID stay INVALID and the recoverability question stays **open**, because the
experiment that would have closed it is void. What *has* changed is the price of
closing it: the cheap route was Option A, it has been spent, and the surviving
evidence says a longer steady run is not the instrument. **If the band is to be
recovered at all, the next pre-registration should price a time-averaged
unsteady statistic, not another steady ensemble.**

---

## 5. Pending, and deliberately not mine

**The case that collided is the case that went VOID.** That coincidence must be
broken by evidence rather than argument, and **I cannot be the one to break it**
— it is my collision and my gate. An independent check of that chain is
commissioned: that the duplicate died at Time ≈ 4265 *before* the first write at
4500; that the write ladder is monotonic and single-writer; that reattachment
reads from **fields** (intact) while the damage was to the **log**.

**Until it reports, §6.1 of the pre-registration should not be relied on** — and
with it, §2.2 above, which rests on `d0.2_s000`. §2.1 and §2.3, the headline,
do not depend on that case at all: dropping `d0.2_s000` entirely leaves 12 of 12
members unsettled and `null` still the only settled run.

### ADDENDUM, 2026-08-11 — the independent check has reported

`F6D_COLLISION_INDEPENDENCE_CHECK.md`. The section above is left as written,
because re-basing a commissioning note onto its own outcome destroys the record
of what was asked on what evidence. What it asked for, and what came back:

**Verdict: COLLISION EXCLUDED** for the −0.831 x/h — but **not by the chain
§6.1 offered.** Three of that chain's five links are false. The duplicate did
*not* die at Time ≈ 4265 and it did *not* fail to write a field: `startFrom
latestTime` made it restart from the survivor's **7000/**, so it was a **fork,
not a repeat**, and it competed for the same snapshot filenames. It ran to Time
7859 and **completely overwrote the `7500/` directory**, plus the nine
`singleGraph_x*/7500/` profiles. "Only the log was damaged" is false, and so is
"no rewrites".

**What carries the verdict instead is per-snapshot writer identification**, not
a chain: the stored pressure gradient and the survivor's own untouched
`wallShearStress.dat` independently name the writer of all 24 continuation
snapshots. **Exactly one — 7500 — is the duplicate's; 23 are the run's own.**

**Nothing in §1–§4 moves, and this is measured.** t=7500 lies outside every
pre-registered metric window. The gate number reproduces exactly at **−0.8313**
at the 13500 cut from fields alone, on a 4000 baseline md5-identical to the
published `ens/` tree; **Δ at completion is −0.4906**; both breach 0.25, so the
**VOID stands** and the **completion value stands**. Settledness recomputed from
the survivor's log segment alone is 0.3392 against the shipped 0.3401 — 0.27 %.
The destabilisation's topological onset precedes the duplicate by 105 s, and the
oscillation grows for 8,500 iterations after it is dead.

**§2.2 is therefore released** — it rests on `d0.2_s000` and `d0.2_s000`'s
numbers survive.

**The one thing that does not survive is the survivor's own 7500 snapshot.** It
was overwritten in place, no copy exists, and it **cannot be reconstructed** —
only bounded by its neighbours (6.358 at 7000, 5.940 at 8000). The published
trajectory keeps the duplicate's point, labelled, per §3.

**And a marker was cheap.** The check produced a free double-writer detector out
of this incident: *a rewrite leaves a directory older than the files inside it* —
no log, no PID, no cooperation from the writer, and it works retrospectively on
any archive. Shipped as `scripts/detect_overwrite_signature.py`.
