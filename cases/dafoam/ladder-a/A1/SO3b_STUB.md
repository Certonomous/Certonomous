# SO-3b — MULTIPOINT ON THE COMPRESSIBLE PATH: **BOARDED, REGISTERED-BUT-NOT-STARTED**. THIS IS A STUB, NOT A PRE-REGISTRATION.

**Dated 2026-08-31. Lane: dafoam `lab-lane`. Supervisor: `dafoam-supervisor`.**
**Nothing here is filed, sent, emailed, uploaded, registered, posted or commented outside this box** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.**

> **THIS DOCUMENT PROMISES NOTHING AND PREDICTS NOTHING.** It freezes **no** gate, **no** threshold, **no** band, **no** label and **no** cap; it registers **no** run, **no** cost and **no** instrument. **It is not a rule-2 freeze and may never be cited as one.** No number below is a registered cost or a registered band. It exists so the rung has a fixed address on the board and so its gating condition cannot be forgotten.

**STATUS: `PENDING`** — boarded, not frozen, not enqueued, no compute, no run root.

---

## 1. What SO-3b is

Sanaa's ruling of 2026-08-31: **SO-3b is a separate rung on the COMPRESSIBLE path, carried BEHIND the D15/D16 gradient patch, and it DOES NOT START until that shipped gradient gate passes.**

It is the half of her original SO-3 sentence — *"Multipoint (2-3 Mach/alpha) weighted objective"* (standing directives 2026-08-27T16:54Z §4) — that the incompressible ground **cannot** answer. `DASimpleFoam` has constant density, no equation of state and no speed of sound, so `CD` and `CL` are Mach-invariant on it **by construction** and a Mach multipoint there would optimise two or three identical operating points (`SO3_MULTIPOINT_SCOPE_MEMO.md` §1). **A genuine Mach multipoint requires `DARhoSimpleFoam` / `DARhoSimpleCFoam`, and that is D15's and D16's ground.**

## 2. THE GATING CONDITION — why it does not start

**The compressible path's SHIPPED gradients are failing on this lab's own measurements, and a multipoint optimisation driven by them would be driven by a gradient known to be wrong.** `DAFOAM_CHARTER.md` §1: *a DAFoam gradient is not a result until a finite-difference table stands beside it at a step proved to lie in the plateau*, and §2 bars an unverified gradient from entering an optimisation.

| item | M | solver | **worst shipped-vs-patched divergence on the adjoint `CD`** | **worst PATCHED-row FD relative error on `CD`** | S/N | item verdict |
|---|---|---|---|---|---|---|
| **D15** | 0.288 | `DARhoSimpleFoam` | **44.878 %** on **`shape[6]`** | **1.657 %** on **`shape[7]`** | 27.1 | **`GATE FAIL`** |
| **D16** | 0.685 | `DARhoSimpleCFoam` | **5.487 %** on **`shape[0]`** | **0.528 %** on **`shape[7]`** | 10.4 | **`GATE FAIL`** |

`[MEASURED, cases/dafoam/ladder-a/A1/curriculum_D15/RESULTS.md:199-201 and cases/dafoam/ladder-a/A1/curriculum_D16/RESULTS.md:194-197]`

**⚠ READ THE COLUMN HEADINGS — THESE ARE TWO DIFFERENT QUANTITIES AND THEY ARE ROUTINELY CONFLATED.** Column 4 is the **SHIPPED-versus-PATCHED divergence of the adjoint itself**; column 5 is the **PATCHED row's own disagreement with finite differences**, i.e. the common-mode noise floor the divergence must be read against — **and it lands on a DIFFERENT COMPONENT (`shape[7]`) in both items.** Neither column-5 figure is "the patched reading of the column-4 component". For completeness, the **FD** disagreements those rows actually gate on: D15 SHIPPED `shape[6]` **44.8738 %** against PATCHED **0.0072 %** `[MEASURED, curriculum_D15/RESULTS.md:52]`; D16 SHIPPED `shape[0]` **5.1511 %** against PATCHED **0.3555 %** `[MEASURED, curriculum_D16/RESULTS.md:44]`.

**Three readings that survive both items and that SO-3b inherits:** (1) **the defect PERSISTS into the compressible solvers** — the SHIPPED row `GATE FAIL`s at both Mach numbers while the PATCHED row `PASS`es at both; (2) **its magnitude falls about 8× across that Mach step**, 44.878 % → 5.487 %; (3) **the component it lands on MOVES** — `shape[6]` at M 0.288, `shape[0]` at M 0.685 — **which is why a multipoint rung on this path cannot pick a component to watch in advance.**

## 3. THE GATE SO-3b WAITS ON, in one sentence

> **SO-3b does not start until the SHIPPED gradient gate on the compressible path PASSES** — that is, until an item on `DARhoSimpleFoam`/`DARhoSimpleCFoam` produces a **SHIPPED-row** `PASS` on `G5` against an FD table at a step proved to lie in the plateau. **No such item exists on this box today.** Both D15 and D16 stand at **`GATE FAIL`** on that row.

**The PATCHED row passing is NOT the condition, and that is deliberate.** `DAFOAM_CHARTER.md` §6: a DAFoam verdict is **two rows or it is not a verdict about DAFoam**. Building SO-3b on the patched row alone would be legitimate only with the SHIPPED `GATE FAIL` travelling attached to every downstream claim, in code (the `curriculum_SO1bR/so1br_precondition.py` `require_travelling_provenance()` form) — **and Sanaa's ruling did not take that route; she gated SO-3b on the patch.** This stub records her condition as she set it and does not soften it.

## 4. What happens next, and what does NOT

**Next, when the condition is met:** a full pre-registration is written and frozen under `cases/dafoam/ladder-a/A1/curriculum_SO3b/PREREGISTRATION.md`, on the 10-line form, deriving its gates from SO-3a's rather than from this stub, and pinning its precondition on the shipped-gradient item **by absolute path and by md5** — never by glob, which is the defect that closed SO-1b at rc = 7 on 2026-08-28.

**What does NOT happen:** nothing is enqueued, nothing is launched, no cost is registered and no gate is frozen by this file. **⚠ NOTHING MECHANICAL ENFORCES THE ORDERING TODAY** — in those words, per `DAFOAM_CHARTER.md` §18.4's precedent. There is no successor file to carry a precondition, and no queue dependency field this lane could find. What holds the ordering today is this stub, the `dafoam-supervisor`'s pre-compute gate, and Sanaa's ruling itself. **When SO-3b is frozen, the precondition becomes a driven file and the ordering becomes enforced in code; until then it is enforced by a person reading this page.**
