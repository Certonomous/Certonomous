# JF1E — JET-FLAP TURBULENCE-RESIDUAL STALL, ESCALATION LADDER — PRE-REGISTRATION

**Status at freeze: ARMED — never run.** No solver has started against this document.

**Authority.** Sanaa's SANAA-DIRECT of 2026-09-01 ~15:45Z,
`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`
(committed `f4c8e466`), §3, which orders the escalation **in her order, one change
per run, each pre-registered**. This document freezes that ladder.

**This is a NEW registration and it does NOT run against `JF1_PREREGISTRATION.md`
(`12b1bd84`).** No gate of that document scores on any run this document produces —
in particular **gate 6 of `12b1bd84` is not inherited**, since
`verification/campaign/JF1_GATE6_FINDING.md` establishes it is unsatisfiable by a
cosine and its repair is reserved to Sanaa. Nothing here asks for or presumes that
ruling. The gates below are this document's own.

**LABEL: `numerics-diagnostic`.** Every rung of this ladder measures the behaviour of
the iterative scheme. **No rung of this ladder produces a physics verdict, a lift
claim, a discretisation band, a GCI or an observed order.** The physics band for JF1
comes from the companion grid study,
`verification/campaign/JF1G_GRID_CONVERGENCE_PREREGISTRATION.md`, and from nowhere
else.

---

## 0. REGISTER SEARCH BEFORE FREEZING (L-427)

**Registers searched for `jet flap` / `jet-flap` / `JF1` / `blown` / `blowing` /
`jetSlot` / `Cmu` / `circulation control` / `bounding k` / `clipping` / `turbulence
residual` / `k-omega stall`, in `docs/NUMERICS_KNOWLEDGE.md`, `docs/LESSONS.md` and
`verification/campaign/`. What the search returned:**

| register | returned |
|---|---|
| `docs/NUMERICS_KNOWLEDGE.md` (45 `N-*` families) | **NOTHING on jet-flap, blown-slot or `C_mu`.** Nearest neighbours are closure-line facts about `bound(omega)` counting at `:3306`, `:3458`, `:3469` — a different case family (R4 hills/ducts), carried here only as the instrument, not as a result. |
| `docs/LESSONS.md` (max existing number **L-428**) | **L-235** — *a settle criterion that measures change cannot tell convergence from clipping* — **directly applicable and adopted below as the ladder's primary instrument.** **L-341** — a mesh-dependent Robin coefficient turns a grid study into a BC measurement — checked against this case and **does not bite** (§0.1). **L-409** — the gate-unsatisfiability class. **L-425** — `\b(...)\b` inflection blindness in `vocab_sweep_jf1.py`; a screen-vocabulary defect, not a physics one. |
| `verification/campaign/` | `JF1_PREREGISTRATION.md` (frozen `12b1bd84`), `JF1_L1_FEASIBILITY_FIRST_FIELDS.md`, `JF1_GATE6_FINDING.md`, `F28_DUCTED_ACTUATOR_DISK_PREREGISTRATION.md`. **No prior registration of a JF1 numerics escalation ladder exists.** |

**Nothing already on this box refutes any claim registered below.** The one prior
finding that bears directly on it — L-235 — is *adopted*, not contradicted.

### 0.1 L-341 checked against this case, and the answer is negative

L-341's hazard is a boundary condition whose coefficient contains `deltaCoeff`, so
that each mesh level silently carries a different BC. Read off the running case's
own `0/` directory: `airfoil` carries `noSlip` (U), `zeroGradient` (p),
`fixedValue 1e-10` (k), `omegaWallFunction` (omega), `nutLowReWallFunction` (nut);
`farfield` carries `freestreamVelocity` / `freestreamPressure` / `inletOutlet`;
`jetSlot` carries `fixedValue` on U, k and omega. **No hand-rolled `mixed` condition
and no hardcoded coefficient appears anywhere.** `omegaWallFunction` is
mesh-dependent *by construction* — that is the correct low-Re behaviour and is the
opposite of L-341's defect, which is a coefficient frozen at one level's value.
**Recorded as a negative result rather than left unstated.**

---

## 1. THE STALL, MEASURED — THE BASELINE THIS LADDER MOVES

The five completed rows of 2026-08-31 are the baseline. They are labelled
`feasibility`, they score nothing, and reading them here is reading prior art. All
five ran the **identical** 39,984-cell O-mesh from `cases/JF1_JET_FLAP/build_jf1.py`
at `--scale 1.0`.

| row | `bounding k` in the **final 500** iterations | `bounding omega`, final 500 | k initial residual at `endTime` | CL at `endTime` | CL peak-to-peak, final 2000 |
|---|---|---|---|---|---|
| `JF1_L1_UNBLOWN_A0` | **488 / 500** | 0 | 3.456679e-06 | 0.00005506 | 1.279665e-06 |
| `JF1_L1_BLOWN_CMU005_A0` | **404 / 500** | 167 | 5.940615e-06 | 0.40573320 | 9.107000e-07 |
| `JF1_L1_BLOWN_CMU010_A0` | **494 / 500** | 166 | 2.550196e-05 | 0.54884644 | 1.232540e-06 |
| `JF1_L1_BLOWN_CMU020_A0` | **463 / 500** | 125 | 4.571881e-05 | 0.74399923 | **6.548799e-05** |
| `JF1_L1_BLOWN_CMU040_A0` | **487 / 500** | 125 | 1.472112e-04 | 1.00999416 | 1.336400e-05 |

Read against the case's own registered `residualControl` of **1e-6 on p, U, k and
omega**: **not one row converged, and `k` misses its criterion by 3.5x to 147x.**
Every row is clipping `k` on 81–99 % of its final 500 iterations, i.e. continuously
through the last one.

**Two things in that table are worth naming because they are counter-intuitive and a
successor will otherwise re-derive them the hard way:**

1. **The force is stationary while the turbulence field is not.** CL's peak-to-peak
   over the final 2000 iterations is between `9.1e-07` and `6.5e-05`. A settle test
   on CL alone would call every one of these rows converged. **That is exactly L-235:
   the quantity stopped moving, and the reason it stopped moving is not that the
   solve converged.** This ladder therefore gates on the clipping counter and the
   turbulence residual, **never on the movement of CL.**
2. **`C_mu = 0.20`, not `C_mu = 0.40`, is the least stationary row** (`6.5e-05`
   peak-to-peak, 5x the `C_mu = 0.40` row). The directive anticipates oscillation at
   the top of the sweep; measurement puts the largest residual force motion one rung
   below it. The E4 trigger below is therefore registered on **every** blown row, not
   only on `C_mu = 0.40`.

---

## 2. THE MESH FACT THAT MAKES CONTINUATION POSSIBLE — MEASURED, NOT ASSUMED

Sanaa's chain starts at `C_mu = 0`. The unblown row's `jetSlot` is polyMesh type
`wall`; every blown row's is type `patch`. Seeding a blown case from the unblown
field is only legitimate if the two meshes are the same mesh.

**Measured by md5 of the two run directories' `constant/polyMesh` files:**

| file | unblown (wall slot) vs blown (patch slot) |
|---|---|
| `points` | **IDENTICAL** (`6d900f02…`) |
| `faces` | **IDENTICAL** (`94739a73…`) |
| `owner` | **IDENTICAL** (`a7c34e6a…`) |
| `neighbour` | **IDENTICAL** (`77ab68e4…`) |
| `boundary` | **DIFFERS — three lines**: `type wall;` + `inGroups 1(wall);` → `type patch;` |

**The cell, face and point sets are byte-identical; only the patch's type word
differs.** So a continuation seed is a straight cell-for-cell copy of the internal
field, with the `jetSlot` boundary *entries* rewritten. Registered as the mechanism
in §3.

**⚠ DISCLOSED DEPARTURE FROM THE DIRECTIVE'S WORDING, D-1.** Sanaa's §3 item 1 says
*"from the **converged** solution of the next-lower `C_mu`"*. **This lab has no
converged JF1 solution at any `C_mu`, including zero** — §1 measures that. The chain
is therefore seeded from the **final field of a stationary-but-clipping-held run**.
That is still continuation and it is still the right first rung, but it is **not what
she described**, and no report of this ladder may call the seed converged. Disclosed,
not absorbed.

---

## 3. THE LADDER — FROZEN, ONE CHANGE PER RUNG, IN SANAA'S ORDER

Each rung differs from the rung below it by **exactly one control**. A rung that
reaches its gate ends the ladder; a rung that fails it hands its configuration to the
next rung as the new baseline. **The escalation order and the trigger for each rung
are frozen here and may not be reordered after first compute.**

| rung | the ONE change from the rung below | applied at |
|---|---|---|
| **E0** | *(baseline — the five rows of 2026-08-31; no new compute)* | — |
| **E1** | **Continuation.** Initial field seeded from the next-lower `C_mu`'s final field instead of freestream. Numerics byte-identical to E0. | `C_mu` 0.05, 0.10, 0.20, 0.40, in that order |
| **E2a** | **Turbulence-equation relaxation `0.7 → 0.5`** (applied to `k` and `omega` together — see §3.1) | same four |
| **E2b** | **`nNonOrthogonalCorrectors 1 → 2`** | same four |
| **E2c** | **`div(phi,k)` and `div(phi,omega)`: `limitedLinear 1 → limitedLinear 0.5`** | same four |
| **E3** | **Pseudo-transient**: `pimpleFoam` with `ddtSchemes { default localEuler; }` (local time stepping) toward steady state | same four |
| **E4** | **True transient**: `pimpleFoam`, `dt = 1e-4 s`, 20 flow-throughs (`t = 2.0 s`, one flow-through = `c/U_inf = 0.1 s`), time-averaged over the final 10 flow-throughs | only the rows that trip §5 |

### 3.1 The one reading this ladder takes, and it is registered rather than assumed

Sanaa's item 2 names three controls in one sentence: *"k and omega 0.7 -> 0.5;
nNonOrthogonalCorrectors 2; … limitedLinear 1 -> 0.5 if needed."* Under one-change-
per-run these are **three rungs, not one**, and they are split as E2a/E2b/E2c above.
**`k` and `omega` relaxation is treated as ONE control**, because it is one physical
knob — the relaxation of the turbulence transport pair — and she names it as one
item. That reading is registered here so that a reader can disagree with it in the
open rather than discover it in a diff.

### 3.2 Continuation mechanism, frozen

For each blown target row at `C_mu = X`, seeded from source row at `C_mu = X_prev`:

1. Build the target run root and its mesh exactly as `run_jf1_blown.sh` does
   (`build_jf1.py --level L1 --slot-type patch`, `--scale 1.0`).
2. Assert the target's `constant/polyMesh/{points,faces,owner,neighbour}` md5s equal
   the source's. **REFUSE (exit 2) on any mismatch** — this is the guard that makes
   §2's measurement load-bearing rather than decorative.
3. Copy the source's `<endTime>/{U,p,k,omega,nut}` internal fields into the target's
   `0/`.
4. Overwrite the target's `jetSlot` boundary entries with that row's frozen jet BCs
   (`U`, `k`, `omega` from `run_jf1_blown.sh`'s substitution, unchanged). Overwrite
   `airfoil` and `farfield` entries from the case templates, unchanged.
5. Assert **no `@TOKEN@` survives** into any `0/` field (the existing launcher's
   refusal, retained).
6. `touch 0/*` last, so the rule-4 age guard dates the run.

**`startFrom startTime; startTime 0;` is retained** — the seed is written *into* `0/`
rather than restarted from a later time directory, so that `endTime` counting, the
`ExecutionTime` clause and the age guard all read exactly as they do on E0. This is a
deliberate choice to keep the completion rule's arithmetic identical across rungs.

---

## 4. THE GATE — FROZEN THRESHOLD, FROZEN LABEL

**Gate E, evaluated per rung, on every row that rung runs.**

A rung is **`GATE REACHED`** if and only if, on **all four** blown rows:

| clause | threshold |
|---|---|
| E-1 | `bounding k` events in the **final 500 iterations** == **0** |
| E-2 | `bounding omega` events in the **final 500 iterations** == **0** |
| E-3 | initial residual of `k` at `endTime` **< 1e-6** |
| E-4 | initial residual of `omega` at `endTime` **< 1e-6** |
| E-5 | initial residual of `Ux`, `Uy` and `p` at `endTime` **< 1e-6** |
| E-6 | the run satisfies the **strict completion rule** (CLAUDE.md rule 4) in full |

Otherwise the rung is **`GATE FAIL`** and the ladder escalates to the next rung.
A rung failing **E-6 alone** is **`NOT A RESULT`** for that rung, not `GATE FAIL`,
and is re-run once before escalating; a second E-6 failure is `BLOCKED` with the
crash triaged.

**E-1 and E-2 are the load-bearing clauses and they are L-235's instrument.** The
residual clauses alone would have passed rows whose `k` field was flat because it had
been clipped. **A rung that clears E-3 to E-5 but not E-1/E-2 is `GATE FAIL`, and no
report of it may use the word converged.**

**Zero is a claim, so it carries a planted control (CLAUDE.md rule 3).** The reader
that counts `bounding k` in the final 500 iterations is proven able to return a
non-zero before any zero it returns is believed: it is run against
`JF1_L1_BLOWN_CMU010_A0/log.simpleFoam`, which **must** return **494**, and against a
copy of that log with every `bounding k` line deleted, which **must** return 0. The
comparator **REFUSES (exit 2)** if the first control does not return 494 exactly.

---

## 5. E4 TRIGGER — REGISTERED BEFORE IT CAN BE READ OFF AN ANSWER

E4 (true transient) runs on a row **only if** that row, at the last rung attempted,
shows CL **peak-to-peak over its final 2000 iterations > 1.0e-03 absolute**.

**Provenance of the threshold, stated so it is falsifiable:** the E0 baseline
peak-to-peak values are `9.1e-07` / `1.2e-06` / `6.5e-05` / `1.3e-05` for `C_mu`
0.05 / 0.10 / 0.20 / 0.40 (§1). The threshold sits **15x above the largest of them**.
**On the E0 evidence this trigger does not fire on any row** — it is registered to
catch a rung that *destabilises* a solve that was steady, which is a real risk for E3
and E4's own time-stepping, not to catch the baseline. Registering it at a level the
baseline already clears is the honest way round: the threshold cannot have been
chosen to make a transient look necessary.

If E4 runs, its point is **re-registered as a time-averaged result with its band**,
per the directive, in a dated successor document — never by amending this one.

---

## 6. COST — CLAUDE.md RULE 12

**Basis: MEASURED, from the five E0 rows' own `RUN_STATUS` files.** Serial
(`ranks = 1`) throughout. Per-row measured core-minutes: 23.7667 / 24.4333 / 21.7500
/ 22.3333 / 25.2000, **mean 23.497**. Unit rate `4.0798e-06` core-s per cell per
iteration, derived from `JF1_L1_BLOWN_CMU010_A0` (39,984 cells, 8,000 iterations,
1,305 wall s, 1 rank).

**Every prior JF1 per-solve estimate assumed convergence before the iteration cap.
That has never once happened, so every estimate below is built from the measured
figure and assumes the cap is reached.**

| rung | rows | `endTime` | estimate | **registered cap** |
|---|---|---|---|---|
| E1 | 4 | 8,000 | 94.0 core-min | **150** |
| E2a | 4 | 8,000 | 94.0 | **150** |
| E2b | 4 | 8,000 | 141.0 (2 non-orth correctors ≈ +50 % on `p`) | **220** |
| E2c | 4 | 8,000 | 94.0 | **150** |
| E3 | 4 | LTS to steady | 188.0 (≈2x SIMPLE per step) | **300** |
| E4 | ≤4 | 20,000 steps × 3 outer | 163.2 per row | **400 total** |
| | | | | **LADDER CAP 1,370 core-min** |

**Derived cost at the recorded `c7a.4xlarge` rate of `$0.0513/core-h`: 1,370
core-min = 22.83 core-h = `$1.17`. This dollar figure is DERIVED, NOT MEASURED —
this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).**

**An overrun stops the run; it does not get a new budget.** Each rung's wrapper
carries `timeout` at its own cap and exits non-zero on the kill, as `run_jf1_blown.sh`
already does. The ladder ends the moment a rung reaches Gate E, so the cap above is a
ceiling on the worst case, not a forecast of spend.

**At completion, estimate-versus-actual lands as a row in `docs/COST_CALIBRATION.md`**
per rule 12, stating the ratio actual/predicted and attributing the gap.

---

## 7. REGISTERED REFUSALS — THE COMPARATOR EXITS 2 RATHER THAN DEGRADE

1. Source and target `polyMesh` `{points,faces,owner,neighbour}` md5 mismatch (§3.2).
2. An `@TOKEN@` surviving into a `0/` field.
3. The `bounding k` reader failing its planted control (§4).
4. `checkMesh` not printing `Mesh OK`.
5. Any clause of the strict completion rule unmet (rule 4), reported as `NOT A RESULT`.
6. A rung run out of the frozen order of §3.
7. Any attempt to emit an observed order, a GCI, a discretisation band or a physics
   verdict from a rung of this ladder (§0, LABEL).

---

## 8. WHAT THIS REGISTRATION DOES NOT COVER

- **It sets no lift band and no physics verdict.** That is `JF1G`'s.
- **It does not repair, inherit or rule on gate 6 of `12b1bd84`.** Reserved to Sanaa.
- It does not change the JF1 grid family, the geometry, `tau`, `alpha`, or any jet BC.
- It makes no claim about which rung will succeed. §11-style prediction: **the honest
  pre-registered expectation is that E1 alone is insufficient** — continuation moves
  the starting point, and the measured clipping is continuous through iteration 8000,
  which is a property of the converged-in-forces state rather than of the transient
  from freestream. **If E1 reaches Gate E, that expectation was wrong and it will be
  reported as wrong.**

---

## 9. FREEZE

Frozen at the commit that adds this file. The gate, the thresholds, the caps and the
labels above are fixed from that commit. After first compute, changes land only as
dated addenda that cannot alter a gate, threshold, cap or label; originals are struck,
never rewritten.

**SUBMISSIONS PARKED.** Nothing in or derived from this document is sent, filed,
uploaded, posted or registered outside this box.
