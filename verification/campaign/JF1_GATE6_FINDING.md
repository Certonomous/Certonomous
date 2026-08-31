# JF1 — FINDING: FROZEN GATE 6 IS UNSATISFIABLE BY CONSTRUCTION

**Status: `FINDING`. Not a gate failure — the runs that exposed it are `feasibility` and score
nothing.** Raised to the chief and to Sanaa. **`cfd-supervisor` has NOT amended the gate**: moving
a frozen gate threshold is reserved (`ESCALATION_CHARTER.md`), and this document exists to put the
question on her desk with the arithmetic already done.

- **Registration:** `verification/campaign/JF1_PREREGISTRATION.md`, frozen **`12b1bd84`**, 15:29Z.
- **Gate 6, as frozen:** *jet mass flow through `jetSlot` vs `ρ h V_j`, **≤ 0.5 %**, else
  `NOT A RESULT`.*
- **Found by:** a `lab-lane`, from the running blown feasibility rows. **Verified independently by
  `cfd-supervisor`** before being repeated upward.

---

## 1. THE MEASUREMENT, AND IT IS NOT MARGINAL

Measured `sum(phi)` on the `jetSlot` patch across **all three** running blown rows equals
**exactly `V_j cos τ · h · span`**, not `V_j · h · span`.

| | value |
|---|---|
| measured ratio to the registered comparand | **0.866025404** (identical on every row) |
| `cos(30°)`, re-derived by the supervisor | **0.866025403784** |
| difference | **2.156e-10** |
| shortfall against the comparand | **−13.397460 %** |
| gate 6 threshold | **0.5 %** |
| **outside its own gate by** | **26.8 ×** |

**A ratio that reproduces `cos τ` to ten significant figures on three independent rows is not a
solver artifact.** It is geometry.

## 2. THE MECHANISM

`jetSlot` **is the blunt base**, so its face normal lies along the chord. The jet leaves at
**τ = 30° to the chord**. `sum(phi)` is a **flux through that face**, so it carries only the
**component normal to it** — `V_j cos τ`. The registered comparand `ρ h V_j` is the **full
magnitude**. **The gate compares a projected quantity against an unprojected one and calls the
difference an error.**

No mesh, no solver, no relaxation and no iteration count can close a 13.4 % gap that is a
**cosine**. **Every gated row would return `NOT A RESULT` on gate 6, forever.**

## 3. THIS IS L-409's CLASS FOR THE THIRD TIME IN ONE DAY

`F23b` (a discretisation error gated at an iterative tolerance, **unrepairable, `BLOCKED`**), JF1's
own completion clauses (a comparator that refused every possible run, **repaired pre-compute at
zero cost**), and now this. **Same class, three mechanisms, one day.**

### ⚠ AND IT SHARPENS L-409's OWN REMEDY, WHICH IS THE PART WORTH KEEPING

L-409 remedy 5 is the **satisfiability check**: before freezing, name one concrete outcome that
passes every clause simultaneously. **That check WAS performed on JF1** — §17.3 registers a
constructed exemplar — **and it did not catch this.** The exemplar asserts **0.021 %** agreement on
gate 6, a value the geometry **forbids**.

**So the exemplar was internally consistent and physically impossible.** The refinement this
finding buys, stated for whoever writes the next one:

> **A constructed exemplar must be derived from the case's own geometry and physics, not merely be
> a set of numbers that satisfies the clauses.** An exemplar written *to* the thresholds will
> always pass them. The question is not "do these numbers satisfy the gates" but **"could the case
> produce these numbers"** — and for gate 6 the answer was no, by a cosine, and was available at
> freeze time from the registered `τ = 30°` alone.

## 4. THE REPAIR, AND WHY IT CANNOT BE ANSWER-FITTING

The comparand should be the **patch-normal flux**, `ρ h V_j cos τ` — or equivalently the gate
should compare against the jet's **normal component**, with the full magnitude carried separately
where the momentum coefficient needs it (`C_mu` and the §1.6 jet-reaction term already use the
full magnitude correctly and are **unaffected**).

**`cos τ` is fixed by the registered `τ = 30°`.** It was determined by the geometry **before any
compute**, it is not a value read off a result, and it could have been written at freeze time. **A
repair whose value is pinned by an already-frozen parameter cannot have been chosen to fit an
answer** — which is the only thing rule 2's freeze exists to prevent.

## 5. THE QUESTION FOR SANAA — AND IT IS A CHARTER QUESTION, NOT A CFD ONE

**Rule 2 closes gates at first compute. Has first compute occurred against `12b1bd84`?**

- **Argument that it has:** the launch lines cite `prereg 12b1bd84`. Solvers have run. On the
  literal reading the window is shut and gate 6 is **unrepairable**, exactly as `F23b`'s was.
- **Argument that it has not:** Sanaa's ruling of 2026-08-31 (`9154c8ef`) makes feasibility rungs
  **queue-legal without a freeze** and their outputs **"never gradeable as verdicts."** A run whose
  output can never become a verdict **cannot be used to fit a gate to an answer**, which is the
  hazard rule 2 addresses. On that reading the gated window is still open.

**`cfd-supervisor` does not rule this.** It is the boundary between a charter clause and a
standing directive, and both are reserved. **Recommendation, offered and not acted on:** treat the
feasibility runs as **not** closing the gated window, repair gate 6 to the projected comparand as
a dated pre-compute amendment, and record `cos τ`'s provenance as *fixed by the frozen `τ`*. If
that reading is rejected, JF1's gate 6 must instead be reissued under a **new sha**, as `F23b`'s
successor was.

**Until she rules, nothing gated runs on JF1.** The feasibility rows continue — they score
nothing, and they are the only reason this was found before a gated run wasted its budget on a
gate that could never pass.
