# NON-CONVERGENCE STANDARD — the L0–L7 ladder, and the anti-gaming clause

**Status: LAB LAW.** Issued by Sanaa 2026-08-27T16:54Z as §3 of her standing directives, captured
verbatim at `etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md` and boarded in the CHIEF
section at `55b95ba9`. **Binds every team.** Owner of the standard text:
`verification-supervisor`. Cross-cited from `docs/charters/VERIFICATION_CHARTER.md`.

**This file has two voices and they are never mixed.** §1 is **Sanaa's text, verbatim** and is the
authority. §2 is this team's **operationalisation**, marked `[lab-attributed]` throughout, and is
**overrulable by her without touching §1**. Where §2 appears to add a requirement §1 does not
state, §1 governs.

---

## §1 — SANAA'S TEXT, VERBATIM (the authority)

> ## 3. WHEN A CASE WON'T CONVERGE / BREAKS / GIVES WRONG RESULTS (all teams)
> One change per run; every step a pre-registered diagnostic arm with a cap.
> - L0 DIAGNOSE FIRST: oscillation (relaxation) vs growth under flat
>   neighbours (coupling not closing) vs plateau (tolerance vs partition
>   noise); which channel; balance state; where in the domain.
> - L1 numerics dials: under-relaxation, CFL/pseudo-time ramp, tolerance
>   sanity (no channel orders tighter than siblings without justification).
> - L2 linear solver: preconditioner swap, solver swap, restarts.
> - L3 discretization: scheme blend, limiters, gradients — withdrawal
>   pre-compute is a legitimate verdict for structurally non-convergent
>   pairs (F23).
> - L4 mesh: repair offenders, y+/near-wall or localized refinement, remesh.
> - L5 initialization & continuation: potential start, lower-Re /
>   higher-viscosity continuation, BC ramps.
> - L6 model swap within the class's admissible set — pre-registered arm
>   only, re-frozen as a new registration, model-form implication declared.
> - L7 formulation: steady -> pseudo-transient -> unsteady; formulation check.
> - ANTI-GAMING (absolute): convergence aids (L1-L5) tune freely, disclosed.
>   Answer-changing choices (model, scheme class, formulation) are never
>   selected by agreement with the reference. Converged-but-wrong = NOT
>   HELD with diagnosis, never a parameter hunt. Frozen gates never edited
>   post-compute.
> - Crashes: triage class per charter; OOM feeds the memory census.

---

## §2 — OPERATIONALISATION `[lab-attributed]`, one clause per level

### §2.0 The two standing conditions, which bind at EVERY level

Her opening sentence is not preamble, it is the gate on the whole ladder:

> *"One change per run; every step a pre-registered diagnostic arm with a cap."*

- **ONE CHANGE PER RUN.** An arm that moves two dials answers no question: if it converges you do
  not know which dial did it, and if it does not you have spent the budget twice. **An arm that
  changes more than one thing is `NOT A RESULT` for this ladder's purposes** — not because the
  solve is bad, but because it cannot discriminate, and §2c of `VERIFICATION_CHARTER` is the
  clause it fails.
- **EVERY STEP IS A PRE-REGISTERED DIAGNOSTIC ARM WITH A CAP.** Standing rule 2 already forbids
  compute without a committed pre-registration and rule 12 forbids a proposal with no cost.
  **This ladder adds no exception and creates no fast path.** A diagnostic arm is a run: it is
  frozen by sha before it starts, it carries its own core-minute cap, and an overrun stops it.

### §2.1 The levels

| level | what it may change | verdict language it can produce | binding clause |
|---|---|---|---|
| **L0 DIAGNOSE** | **nothing** — L0 is a *reading*, not a run | a named channel + balance state + location | **L0 is MANDATORY and comes FIRST.** Her word is *"DIAGNOSE FIRST"*. An arm launched at L1–L7 without a recorded L0 reading is a parameter hunt with a ladder's vocabulary bolted on. The reading names **which of the three shapes** it is — oscillation (relaxation), growth under flat neighbours (coupling not closing), or plateau (tolerance vs partition noise) — **which channel**, the **balance state**, and **where in the domain**. |
| **L1 numerics dials** | under-relaxation, CFL / pseudo-time ramp, tolerance sanity | convergence aid — **does not change the answer** | *"no channel orders tighter than siblings without justification"* is a **check on the existing registration**, not a licence to loosen. Loosening a tolerance to reach convergence is an **answer-changing** act disguised as a dial: if the loosened channel is the gate channel, it is L7-class and the anti-gaming clause bites. |
| **L2 linear solver** | preconditioner swap, solver swap, restarts | convergence aid | A linear-solver swap must leave the converged solution invariant to the solver tolerance. **If it moves the gate quantity by more than the iterative-convergence band, it is not an L2 change** — it is evidence the system was never converged, and the finding is that, not the swap. |
| **L3 discretization** | scheme blend, limiters, gradients | convergence aid **at the boundary** — see the caveat | **A scheme-CLASS change is answer-changing and is NOT an L3 aid** (anti-gaming names "scheme class" explicitly). L3 covers blend factors, limiter choice and gradient scheme *within* the registered class. **Her sanctioned exit: withdrawal pre-compute is a legitimate verdict for structurally non-convergent pairs.** See §2.2. |
| **L4 mesh** | repair offenders, y+/near-wall or localized refinement, remesh | convergence aid, **with one hazard** | **A mesh change inside a Roache ladder destroys the ladder.** Rule 5's triple requires a controlled refinement family; repairing one level's mesh and not its siblings makes the three values incommensurable and the triple `NOT A RESULT`. **An L4 repair applied to a graded ladder re-registers the whole ladder as a new one.** |
| **L5 initialization & continuation** | potential start, lower-Re / higher-viscosity continuation, BC ramps | convergence aid | A continuation path may not terminate at a different operating point than the one registered. **The final state must be at the registered BCs and the registered Re** — a run that converges at a higher viscosity has converged a different problem. |
| **L6 model swap** | a model within the class's admissible set | **ANSWER-CHANGING** | Her three conditions are cumulative and all three are required: **pre-registered arm only**, **re-frozen as a NEW registration**, and **model-form implication declared**. The new registration is a new row; the old row is not overwritten and its verdict is not withdrawn by the swap. |
| **L7 formulation** | steady → pseudo-transient → unsteady; formulation check | **ANSWER-CHANGING** | Same three conditions as L6. A steady case that only converges unsteady has produced a **finding about the physics** — that the steady formulation does not admit a solution here — and that finding is reportable in its own right, not a defect to be tidied away. |

### §2.2 F23 — the L3 withdrawal precedent, on the record

Sanaa's L3 clause names F23 as the precedent. It is on disk and it holds:

`cases/F23_HP_WEDGE/queue_entry_F23_HP_WEDGE.WITHDRAWN_2026-08-26T225538Z.json:33-36`, withdrawn
`2026-08-26T22:55:38Z` by `cfd-supervisor`, reason verbatim:

> *"L-346 pre-compute: the registered SIMPLE 0.7/0.3 + central form at 4000 fixed iterations was
> measured NON-CONVERGING at fine cross-sections by the F25_DUCT3D instrument arms (`fc4c479b`
> prereg section 5.1); F23 Amendment 1 (solver form + iteration floor registered from a measured
> scratch arm) ordered before any compute. Entry was HELD by the runner from 22:08Z to withdrawal,
> never LAUNCHED; run root ABSENT."*

**Why it is the right precedent, in four properties any future L3 withdrawal must reproduce:**

1. **PRE-COMPUTE.** The entry was `HELD`, never `LAUNCHED`, and the **run root was ABSENT** — so
   rule 2's amendment window was open and no gate was closed. **A withdrawal after first compute
   is not this manoeuvre**; it is a `NOT A RESULT` with its cost recorded.
2. **MEASURED, NOT ASSERTED.** The non-convergence was measured by a *different* case's instrument
   arms (`F25_DUCT3D`, prereg `fc4c479b` §5.1), not inferred from the registration failing to look
   promising.
3. **THE SUCCESSOR IS ORDERED IN THE SAME BREATH.** Withdrawal is not abandonment: Amendment 1 was
   ordered before any compute, with the floor **registered from a measured scratch arm**.
4. **THE WITHDRAWAL RECORD IS THE ARTEFACT.** It carries `utc`, `by` and `reason` and is filed
   beside the case. **A withdrawal that leaves no record is a deletion**, and this standard does
   not authorise one.

### §2.3 THE ANTI-GAMING CLAUSE — absolute, and this team adds nothing to it

Her clause is `(absolute)` and takes no exception. Three readings, stated so nobody has to infer
them:

- **"Never selected by agreement with the reference."** The prohibited act is **selection by
  outcome**. Trying an admissible model and reporting what it gave is legitimate; trying several
  and keeping the one nearest the reference is not — **and the tell is that the discarded arms are
  not in the record.** An L6/L7 arm therefore reports **every** arm it ran, including the ones that
  went the wrong way. **A single reported arm out of several run is the signature this clause
  exists to catch.**
- **"Converged-but-wrong = NOT HELD with diagnosis, never a parameter hunt."** A converged solve
  that misses its reference is a **result**, and its verdict is `GATE FAIL` under rule 1 with the
  tier `NOT HELD`. **It is not an invitation to re-enter the ladder.** The ladder addresses
  *non-convergence*; it is not a route to a better number.
- **"Frozen gates never edited post-compute."** Unchanged from standing rule 2 and
  `VERIFICATION_CHARTER` §2d. **No level of this ladder is a repair exception**: §2d.1's
  four-condition exception is the only route, and it reaches the *comparator*, never the gate,
  the threshold, the cap or the label.

### §2.4 Crashes

> *"Crashes: triage class per charter; OOM feeds the memory census."*

This is `SUPERVISION_CHARTER` §3 check 2, already binding and not delegable: **a crash, a
divergence or a refused solve is a finding about the case, the method or the toolchain until
triage demonstrates otherwise.** The ladder does not replace triage — **L0 comes after the crash
class is assigned**, because a crash and a non-convergence are different objects and only one of
them has residuals to read. An OOM is additionally a **capacity** measurement and is filed to the
memory census rather than absorbed into the case.

---

## §3 — WHAT THIS STANDARD DOES NOT DO

- **It creates no new verdict word.** Standing rule 1's vocabulary is unchanged. `NOT HELD` in
  Sanaa's anti-gaming clause is a **tier** in the coverage taxonomy, not a gate verdict; the gate
  verdict for converged-but-wrong is `GATE FAIL`.
- **It grants no compute.** Every level's arm is costed and capped under rule 12.
- **It retires nothing.** Retiring or widening a gate threshold or a charter clause is reserved to
  Sanaa (`CLAUDE.md` FIRST-ACTION rule).
