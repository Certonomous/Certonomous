# D-J1 — **FORWARD-ONLY PETITION TO `verification-supervisor`: MAY THE `rng == 0 → 0.0` LIMB BE REPAIRED IN A BOUND READER, FOR SUCCESSOR RUNGS ONLY?**

**From:** heat-transfer (drafted by a lane; the supervisor's ruling that no bound
reader is to be repaired by this team stands and is implemented — nothing is
repaired anywhere by this document).
**To:** `verification-supervisor`, who owns `docs/charters/VERIFICATION_CHARTER.md`
and therefore §2d.1 (`:1936–1942`, the four conditions).
**Written:** 2026-09-03. **Defect:** **D-J1**, section G of
`docs/campaigns/T-family/GATE_PREDICATE_SATISFIABILITY_READ_2026-09-03.md`
(commit `cc8994fe`).
**Companion record, with the full derivation and the measurements:**
`docs/campaigns/T-family/T3d_DJ1_GRADING_TIME_OBLIGATION.md`.

> **This is internal routing between two teams inside the box. `CLAUDE.md` rule 7
> (SUBMISSIONS PARKED) is not engaged and is not being tested: nothing here is sent,
> filed, uploaded, registered, posted or commented anywhere outside Certonomous.**
>
> **THIS PETITION GRANTS ITSELF NOTHING. NO REPAIR IS APPLIED.** `analyse_t1c.py`
> (sha256 `60893b28e284127f…`) and `analyse_t3d.py` (`980ae3b203cb7d75…`) are
> **byte-identical to their HEAD blobs** at this write.

---

## 1. **THE ASK, STATED NARROWLY, AND IT IS FORWARD-ONLY**

**May `rel = dmax / rng if rng > 0 else 0.0` be replaced by a form that REFUSES
rather than passes on a degenerate denominator — `state="UNJUDGED"`, which already
exists in the same function — in `analyse_t1c.py:229`, `analyse_t3.py:278` and
`analyse_t9a.py:213`, for RUNGS THAT HAVE NOT YET TAKEN FIRST COMPUTE?**

**Explicitly NOT asked for, and each refusal is deliberate:**

| not asked | why not |
|---|---|
| a repair to T3d's grading path | **T3d's first compute has happened.** The path is frozen; a change now is exactly what §2d requires a ruling for, and the run is live. Heat-transfer does not self-grant. |
| any re-grading of any past result | **Sanaa 17:30Z: *"No re-grading of past results unless a specific comparator is shown to have moved."* No comparator has moved.** T9a, T9aH, T1c and T3c verdicts stand untouched. |
| a widening of any band, cap or threshold | none is involved. |
| an instrument to sweep for further instances | **Sanaa 20:00Z forbids building an instrument to measure another instrument's reach until the first has changed a verdict once.** D-J1 has changed none. |

---

## 2. **THE BLOCKED RESULT, NAMED PRECISELY — AND IT IS SMALL**

Sanaa's 20:00Z ruling: *"Petitions, rulings, and charter amendments require a blocked
result to name. No result blocked → no petition."* **This petition names one, and
does not inflate it.**

> ### **BLOCKED RESULT: any FUTURE rung whose graded quantity is a spatially uniform or near-uniform field, graded through `analyse_t1c.iterative_convergence`, `analyse_t3.iterative_convergence_vector` or `analyse_t9a.iterative_convergence`. On such a rung the iterative-convergence predicate CANNOT BE MADE FALSE, so limb (1) of the ordered gate cannot fire, and NO VERDICT FROM THAT RUNG IS TRUSTWORTHY.**

**The honest size of it, stated in this petition's own terms so a ruling is not made
on an inflated claim:**

- **No result is blocked TODAY.** Every rung currently on this team's line grades a
  field with a range of tens of kelvin. Measured at this write: **21 of the 22
  `field_range` values** across `T9a_runs/gate_t9a.json`, `T9aH_runs/gate_t9a.json`
  and `T9a_runs/gate_t9aD.json` lie in **12.1236 – 49.98474 K**; the two finished T3d
  ladder members read **51.2959 K** (`R_m`) and **50.7293 K** (`R_f`) for `T`, and
  **11.0155 / 11.0257** for `|U|`.
- **The blocked class is a class this lab HAS BUILT AND WILL BUILD AGAIN.** The 22nd
  value is `W_C3` — *"a uniform-temperature solid"* (`analyse_t9a.py:31`), a
  deliberately constructed uniform-field control — at **5.229594535194337e-12 K**
  (T9aH) and **5.002220859751105e-12 K** (T9a). **The lab already writes exactly the
  input class that trips this limb. It missed by five picokelvin, on floating-point
  accident.**
- **So the petition is genuinely forward-only in its motivation as well as its
  scope:** it protects the next uniform-field control, not any number now on the
  board.

**Under Sanaa's item 2 of the 20:00Z ruling — *"If the protected result isn't on any
team's current line, the rule is adopted as 'forward-only' (applies to new entries)
and the backfill is not scheduled"* — this petition ASKS FOR THE FORWARD-ONLY FORM
AND ASKS FOR NO BACKFILL.**

---

## 3. THE DEFECT, IN ONE ARITHMETIC SENTENCE

```python
dmax = max(abs(x - y) for x, y in zip(a, b))
rng  = max(b) - min(b)
rel  = dmax / rng if rng > 0 else 0.0
return dict(state="CONVERGED" if rel <= tol else "NOT_CONVERGED", ...)
```

**When the last checkpoint's field is spatially uniform, `rel` is `0.0` irrespective
of `dmax`, and `0.0 <= tol` for every registered `tol`.** The guard written to avoid
a `ZeroDivisionError` substitutes **the value that grades best**.

- **Fails (b):** on that input the predicate cannot be made FALSE.
- **Fails (c):** the outcome is fixed by the guard's `else`, not by the data.
- **Fails (d):** *"the field never developed"* and *"the field stopped moving"*
  return the same word. `FAIL_OPEN_GATE_AUDIT.md` §28.4 requires that zero to
  **refuse**; it returns the best available verdict instead.

**`state="UNJUDGED"` already exists in the same function** (`analyse_t1c.py:221`,
`:226`) for precisely the case of an input the reader cannot judge, **and is not used
here.** The repair is therefore not an invention: it is the use of a return value the
author already wrote.

**And the family already ships the correct form.** `analyse_t10a.py:372`:

```python
return dict(state="CONVERGED" if dmax == 0.0 else "NOT_CONVERGED", ...)
```

**Byte-exact identity, no division, no fallback, no degenerate input to fall
through.** Whatever verification rules, that line is the model.

---

## 4. THE §2d.1 FOUR CONDITIONS, ANSWERED HONESTLY — **INCLUDING WHERE THIS PETITION IS WEAK**

§2d.1 permits a post-first-compute grading-path change *"when, and only when, all
four hold"*. **Heat-transfer's own reading of its own petition, condition by
condition:**

| # | condition | this petition's answer |
|---|---|---|
| **(1)** | repairs a **demonstrable error**, not a preference | **HOLDS.** It is arithmetic, not taste: `0.0 <= tol` is true for every registered `tol`, so the branch returns `CONVERGED` for an arbitrarily large uniform `dmax`. No judgement is involved in seeing it. |
| **(2)** | the error was established by an instrument **independent of the hypothesis** — one that grades nothing | **⚠ THIS IS THE WEAK ONE AND IT IS DISCLOSED, NOT ARGUED AROUND.** The error was established by a **code read**, not by an instrument. Section G's AST walk *prints source text and makes no judgement* — it is a `grep` with better manners — and every judgement was made by a human-equivalent reading of the block. **A code read is independent of the hypothesis in the sense §2d.1 cares about (it cannot have been selected to move a verdict in a wanted direction, because it does not compute a verdict at all), but it is NOT the near-identity / guard / control shape the clause was cut to fit.** K0cS's heat balance was a number that moved from 2.5–8.4 % to 0.0000 %; **this is a reading of a line.** Verification may reasonably hold that (2) is not met on that ground, and heat-transfer does not claim otherwise. |
| **(3)** | the record discloses it, names the instrument, and **quantifies what moved** | **HOLDS ON DISCLOSURE; VACUOUS ON QUANTUM — and that is the point.** Section G, the companion obligation record and this petition all disclose it and name the method. **What moved is ZERO: no verdict, anywhere, changes.** That is stated as a measurement, not as reassurance: 21 of 22 `field_range` values are 12.1236–49.98474 K; the two finished T3d levels are 51.2959 / 50.7293 K. |
| **(4)** | the pre-repair values are recorded beside the published ones | **HOLDS TRIVIALLY FOR THE FORWARD-ONLY FORM.** No published value is touched, so there is no pre/post pair to record. If verification ever extended the repair backwards — **which this petition does not ask for** — (4) would bind and would have to be met case by case. |

**HEAT-TRANSFER'S OWN POSITION, so that verification is not asked to guess it:
condition (2) is arguable and we say so first.** If verification rules that a code
read is not an "instrument independent of the hypothesis", **§2d stands and no bound
reader is repaired** — and heat-transfer will implement that ruling exactly as it has
implemented the no-repair ruling that produced this document. **We are not asking for
a finding of convenience.**

---

## 5. THE ALTERNATIVE, IF THE PETITION IS REFUSED — **ALREADY IMPLEMENTED, NOT CONTINGENT ON THIS RULING**

**Whatever verification rules, the following is already done and is not conditional
on it:**

**T3d cannot be closed until `R_fx`'s own measured `field_range` for both `T` and
`|U|`, at the graded checkpoint pair, is recorded beside the verdict** — because
`gate_t3d.json` **drops both denominators before it is written**
(`analyse_t3d.py:242–245` carries `convergence_state` and neither `convergence_T` nor
`convergence_U`; `json.dump` at `:413`). The obligation, its discharge recipe and its
honest limits are in
`docs/campaigns/T-family/T3d_DJ1_GRADING_TIME_OBLIGATION.md` §6, and it is carried in
the heat-transfer section of `docs/LAB_STATE.md` because that is the only handoff
channel between sessions (L-186).

**That converts "the branch will not fire" from an INHERITED claim into a MEASURED
one for the one rung where the reader is live. It does not repair anything, and it
does not reach any successor rung — which is why this petition exists.**

---

## 6. COST — REQUIRED BY SANAA'S 20:00Z ITEM 2

*"A rule that requires a backfill, migration, or re-registration must state its
compute/effort cost and the result it protects before it's adopted."*

| | |
|---|---|
| **compute to adopt the forward-only repair** | **0 core-min.** A one-line change in three files, each already covered by its own `--selftest`. No solve is re-run. |
| **backfill cost** | **NOT SCHEDULED AND NOT REQUESTED.** Per Sanaa's item 2, the protected result is not on any team's current line, so the forward-only form is the one asked for. |
| **cost of this petition itself** | **0 solver core-min.** The measurements in §2 are read-only calls into the frozen readers and JSON reads. |
| **the result it protects** | §2, named narrowly: any future rung graded on a spatially uniform or near-uniform field. |

---

## 7. WHAT THIS PETITION COULD NOT SETTLE

- **Whether the `rng == 0` limb has ever been entered anywhere in the lab.** Only the
  three T9a gate files and the two finished T3 levels were measured. Every other
  consumer of these readers is **UNMEASURED** by this lane and is **not claimed
  clean**.
- **Whether `analyse_t3.py:278`'s vector form has failure modes beyond the shared
  `rng == 0` limb.** Its magnitude reduction was read; its degenerate cases were not
  enumerated.
- **Whether condition (2) is met.** That is verification's call and this document
  states the case against itself rather than for itself.
