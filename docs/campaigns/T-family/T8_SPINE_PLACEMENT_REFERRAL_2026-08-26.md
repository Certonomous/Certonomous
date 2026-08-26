# **NOT SENT. NOT FILED. PARKED.** — Referral to Sanaa's desk: T8's place in the DC-cooling spine

> ## **NOTHING IN THIS FILE HAS BEEN SENT, FILED, SUBMITTED, UPLOADED, REGISTERED, POSTED OR COMMENTED ANYWHERE OUTSIDE THIS BOX, AND NOTHING IN IT MAY BE (`CLAUDE.md` rule 7).**
> **This is a DRAFT referral held for Sanaa's reading. It decides nothing. It is
> internal in any case — but the parking stamp is at the top of the file, not in
> a closing paragraph, because that is where a stamp has to be to work.**

**Drafted by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26.**
**ZERO COMPUTE.**

---

## 1. Why this reaches Sanaa's desk rather than being decided in the lab

**H-2 places T8 in the DC-cooling spine — `T3 → T5 → T8 → T12 → K2` rack row —
by Sanaa's own directive of 2026-08-22.**

The heat-transfer supervisor owns `CASE_SELECTION_CHARTER` and **the
case-selection call on T8's formulation is theirs.** But **whether a
mis-specified T8 LEAVES OR MOVES IN THAT SPINE is a change to Sanaa's directive**,
and `CLAUDE.md`'s reserved list puts *"retiring a standard, gate threshold or
charter clause"* and cross-family arbitration on her desk alone. **A supervisor
may rule on the case. Only Sanaa may re-shape the spine she specified.**

**This referral therefore carries the evidence and the options. It does not carry
a decision, and no agent's message anywhere in this thread is her consent
(rule 9).**

## 2. What is now known, in one table

**T8 = `NOT A RESULT`** — full record at `T8_VERDICT_2026-08-26.md`, on two
grounds that share no instrument.

| level | cells | rc | registered convergence gate on `T` (tol `1e-6`) | outcome |
|---|---:|---:|---|---|
| `c` | 6,400 | 0 | **`9.113625e-02`** | reached `endTime` **unconverged** |
| `m` | 25,600 | **136 (SIGFPE)** | — no checkpoint written — | **diverged** at iteration 1086 of 12,000 |
| `f` | 102,400 | 0 | **`1.640285e-02`** | reached `endTime` **unconverged** |

Second, independent ground: the §12 S3 axis-extrapolation precondition
`r₂ = 3·r₁` is **false** on the built mesh — measured **`r₂/r₁ = 2.333313`**
(`7/3`) — so `resolve_planes` refuses and **no row could be graded even if a
level had converged.**

**On identical mesh quality, byte-identical relaxation factors, across 16× in
cell count, the registered steady formulation converges at no resolution, in
three different ways.** Spend to date: **224.667 core-minutes** ($0.19 derived,
not measured), **no cap overrun.**

**The honest limit:** this establishes the failure is grid-dependent and **not**
a mesh-quality or setup error. It does **not** separate *"the plume is physically
unsteady"* from *"the closure is unrealizable on these grids"*. **Both are live**,
and the `epsilon` bounding rate is non-monotone in resolution (3.8 % / 38.6 % /
8.4 %), which **neither hypothesis explains.**

## 3. What is being asked

**T8 was chosen as the spine's stratification-height rung** — the step from T5's
recirculation to T12 (`MATRIX_CONTRIBUTION.md:569-570`). The question is not
whether T8's *registration* is dead; it is, and a successor is a separate
decision that is also Sanaa's and the chief's. **The question is whether the
SPINE still routes through this case.**

**Four options, stated neutrally. This lane recommends none of them** — ranking
them is the supervisor's, and choosing is Sanaa's.

1. **T8 stays, re-registered with an unsteady formulation.** The discriminating
   measurement (an unsteady run on the fine mesh) is registered and run first; if
   the plume is genuinely unsteady, the rung becomes a URANS/statistically-steady
   rung rather than a steady one. **Cost: the discriminator plus a new ladder.**
2. **T8 stays, re-registered steady on a re-chosen ladder** — RULING B's *"finer
   coarse level"*, since `c` stalled and `m` blew up in the middle. **Only viable
   if the discriminator says the closure, not the physics, was the problem.**
3. **T8 moves position in the spine** — its stratification-height role is served
   after T12 or beside it, so the spine is not gated on the rung that is hardest
   to converge.
4. **T8 leaves the spine** and stratification height is sourced from a different
   case entirely.

**Options 3 and 4 change Sanaa's directive. Options 1 and 2 do not** — they are
re-registrations of a rung in its existing spine position, and their
authorisation is the ordinary re-registration route.

> **THE RECOMMENDATION LINE IS THE HEAT-TRANSFER SUPERVISOR'S AND IS
> DELIBERATELY LEFT UNFILLED HERE.** A lane drafting a referral must not
> pre-fill the judgement the referral exists to carry, and a supervisor's
> recommendation relayed by a lane is a summary, not a ruling
> (`SUPERVISION_CHARTER.md` §3).
>
> **RECOMMENDATION — heat-transfer supervisor:** *(to be entered by the
> supervisor before this reaches the desk)*

## 4. What does not depend on the answer

- **The T8 verdict stands either way.** `NOT A RESULT` is recorded and is not
  contingent on the spine question.
- **The transferable lesson stands either way:** *read centroids from disk; never
  register a ratio taken from the nominal mesh spec.* It is the rung's main
  product and it outlives the rung.
- **No compute is queued or fired on this question.** The discriminating
  measurement in option 1 is specified but **not registered**, and rule 2 forbids
  firing before a pre-registration is committed and frozen.

## 5. Cost

**Zero core-minutes.** No solver was launched to produce this referral.

---

> **PARKED IS NOT CANCELLED. This referral stays current as the evidence moves,
> and it goes nowhere until Sanaa takes it there herself.**
