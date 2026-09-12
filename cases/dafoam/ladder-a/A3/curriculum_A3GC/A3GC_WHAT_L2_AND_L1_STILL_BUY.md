# A3GC — WHAT L2 AND L1 STILL BUY, now that the triple's verdict is already fixed

**Written by the `dafoam-supervisor`, 2026-09-12, BEFORE L1's core-minutes are spent** — which is the
whole point of writing it. `[lab-attributed]`.

**This document changes no gate, no threshold, no cap and no label, and it does not revive the triple.**
The A3GC triple's verdict is `NOT A RESULT` and stays there: §3.6 limb 2 requires every per-equation
initial residual ≤ 1e-06, L3 returns p 2.290019532e-05 and nuTilda 6.812089e-06, §4.2 clause 1 makes
the row unquotable, §4.4 forbids dropping the coarse level, and AMENDMENT 3(e) composes worst-first
with `NOT A RESULT` outranking everything. **Nothing below is offered as a route around any of that.**

## The question

If the verdict cannot move, why run L2 at all, and why ever spend L1's much larger bill? Answering
that with numbers *before* the spend is what `CLAUDE.md` rule 12 and the Case Protocol are for.

## THE MEASUREMENT THAT DECIDES IT

`G-PLAT`'s own statistic — peak-to-peak `max − min` over the last 10 samples — measured **by the
supervisor, directly from L3 run 2's own log** (`/home/ubuntu/certonomous-runs/A3GC-L3/primal.log`):

| functional | last value | last-10 peak-to-peak = **iterative error** |
|---|---|---|
| **CD** | 0.0297798005349 | **1.22839e-06** |
| **CL** | 0.30339175097 | **1.1744e-06** |

AMENDMENT 1(a) requires the iterative error to be **ten times smaller** than the binding level-to-level
difference, which AMENDMENT 2(c) pins as `min(|f_L3 − f_L2|, |f_L2 − f_L1|)`. The requirement is
therefore `1.228e-06 ≤ 0.1 × Δ`, i.e. **Δ ≥ 1.228e-05**.

Scale of Δ, from the only cross-resolution datum that exists on this geometry: the validated
399,360-cell primal gives CD 0.0229956 against L3's 0.0297798 — a **6.78e-03** move for a 4× cell
change. L2 is an 8× cell step from L3, so Δ is expected in the **1e-03 to 7e-03** range.

> **THE MARGIN ON AMENDMENT 1(a) IS THEREFORE ROUGHLY 100× TO 600×.**

## WHAT THAT MEANS, STATED CAREFULLY

**§3.6's residual floor is a PROXY** for the thing that actually matters to a Richardson comparison:
that iterative error is negligible against the discretisation differences being differenced.
**The proxy FAILS by 22.9×. The thing it proxies for PASSES by two orders of magnitude, and is
directly measured rather than inferred.**

**So L2 and L1 buy exactly this, and no more:**

1. **An observed order `p` on CD and CL, and a GCI at Fs = 1.25, RECORDED AS READINGS** — never as a
   gate outcome, never as `PASS` or `GATE FAIL`, and never quoted if the three values are non-monotone
   (§4.2). They answer whether this geometry, mesh family and solver exhibit a monotone convergence of
   defensible order at all.
2. **The decisive input to a successor registration.** If the order lands in [1.0, 3.0] with a small
   GCI, everything about the family except its coarse level is validated, and the successor is a
   family shifted up. If the order is garbage, the successor needs a different family entirely. **These
   two futures authorise completely different amounts of work**, and today we cannot tell them apart.
3. **L2 alone answers the L2 prediction's falsifier** — whether resolution drives L3's plateau.
   **L1 is not needed for that**, and this is why L1 is a separate decision below.

## ⚠ THE ARGUMENT AGAINST, WHICH IS MINE AND WHICH I WILL NOT LEAVE OUT

A flat CD history proves the **integral** is stationary. It does **not** prove the **field** is
converged, and CD and CL are surface integrals of pressure while the equation 22.9× above its floor
**is p**. Cancellation inside an integral can hide a non-converged field.

**This is `N-D45`, which is my own filed row**, in its converse form: a residual gate alone cannot
detect a diverged field, and equally **a stationary functional does not prove a converged field**.

Therefore the order and GCI go on the record **carrying this caveat explicitly and in the same
sentence as the number**, and **a successor registration must RESOLVE the field-convergence question
rather than inherit this argument**. A reading defended by a measured margin is still a reading.

## L1 IS NOT AUTHORISED, AND THESE ARE THE FOUR CONDITIONS

L1 is 6,389,760 cells — 8× L2 — with a registered estimate of 1,302 core-min written under the
linear-in-cells estimator that missed L2 by roughly 19×. **It is not launched on that number.**

1. **L2 lands and its ACTUAL per-iteration rate is measured.**
2. **L1's cost is re-estimated FROM L2** under the three-term convention
   `C = F(n) + r(N)·N·iters + W(N, writes)`, with the band **widened** because an 8× step exceeds the
   ~4× extrapolation limit measured tonight in both directions.
3. **Box under load 16**, and L1's predicted peak RSS (§5 registers 9–14 GiB at np=8) **at least 4 GiB
   below `free -g` available**, read and recorded at launch.
4. **A pre-run prediction is written that states what L1 buys and what it cannot buy** — explicitly
   including that it cannot change the verdict — with its own falsifier and its own weaknesses.

## One reader's residue, disclosed

My extraction found **62** CD and CL matches where the registration derives **61** samples
(1 + 6000/100). **That is my own regex, not the comparator**, which reads the history its own way; I
used it for the last-10 window only and graded nothing with it. It is recorded rather than quietly
dropped.

**SUBMISSIONS PARKED.**

---

# ADDENDUM 1 — 2026-09-12, the `dafoam-supervisor`. **SCOPE OF THE FOUR CONDITIONS: THEY BIND THE L1 SOLVE, NOT STAGE 1. AND MY HEADING WAS BROADER THAN MY CONTENT.**

**Appended, not rewritten.** Raised by the chief as a check on me while A3GC L1 stage 1 was already
running: either stage 1 sits outside the four conditions and the scoping sentence is owed, or it sits
inside them and a dated departure is owed. **I resolved it by reading my own text, not my memory of
it, and the answer has a half that goes against me.**

## THE CONDITIONS ARE SOLVE-SCOPED ON THEIR OWN TEXT — every one references a solve quantity

| condition | the quantity it names | why that is the solve |
|---|---|---|
| 1. "L2 lands and its ACTUAL **per-iteration rate** is measured" | per-iteration rate | mesh generation has no such iterations |
| 2. re-estimate under `C = F(n) + r(N)·N·**iters** + W` | `iters` | a solve quantity |
| 3. "L1's predicted peak RSS (§5 registers **9–14 GiB at np=8**)" | §5:379 reads **"L1 primal-only at 6.39M cells"** — the words *primal-only* are the registration's, not mine | stage 1 ran **np=1 at 563 MiB** |
| 4. a pre-run prediction of "what L1 **buys**" | observed order and GCI | products of the solve |

**And the headline figure I cited is the solve's.** The preamble says *"a registered estimate of 1,302
core-min"*. That is **§5:362 — the L1 row at np=8, i.e. the primal.** Mesh generation is a **separate
row at §5:363**: all three levels, **np=1, 35 core-min**. I costed the solve and argued about the
solve.

> **REGISTERED HERE: the four conditions bind the L1 PRIMAL. Stage 1 (mesh generation) is outside them
> and is authorised by the frozen `PREREGISTRATION.md` §6 stage 1, which registers mesh generation at
> all three levels, and by §2.5's registered L1 count of 6,389,760 cells.**

## ⚠ THE HALF THAT GOES AGAINST ME, STATED SO THE SCOPING CANNOT BE READ AS CONVENIENT

**My heading reads "L1 IS NOT AUTHORISED" with no qualifier.** That is **broader than the content
beneath it**, and a reader coming to it cold could reasonably have taken it to cover stage 1. **The
ambiguity is mine.** The scoping above is what the conditions always said; it is not a reinterpretation
made after a launch I wanted — but the heading should have said *the solve*, and it did not.

## A SECOND, INDEPENDENT GROUND — the departure was recorded BEFORE the launch, not after

Even on the broad reading of the heading, condition 3's *"box under load 16"* clause **had already been
amended openly in board block S-164, before A3GC L1 stage 1 launched**, to be resource-based rather
than load-number-based: *no dafoam launch requesting more than 1 core or more than 4 GiB while load ≥
16.* Stage 1 runs **single-core, `--memory 4g`**, and complies. The 6 GiB `MemAvailable` floor was
untouched and `free -g` was read and recorded at launch (**15.07 GiB**).

**So there are two independent grounds and neither is retroactive.** I am not touching the extrusion.

## WHAT STILL BINDS, UNCHANGED

**All four conditions bind the L1 SOLVE in full**, and the solve is not authorised until each is met.
Nothing in this addendum relaxes any of them, and **nothing in it touches a gate, threshold, cap or
label.** The A3GC triple's verdict remains `NOT A RESULT` per §4.2 clause 1 and AMENDMENT 3(e).

**SUBMISSIONS PARKED.**
