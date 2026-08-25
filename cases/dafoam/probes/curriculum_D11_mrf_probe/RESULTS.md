# D11 MRF CAPABILITY PROBE — RESULTS

## 1. Verdict

**`NOT A RESULT`** — and, explicitly, **NOT `BLOCKED`.**

All five stages died before writing any artifact, so the frozen grader refused, exit 2,
on `artifact missing: …/D11/omegaP/d11_omegaP.json`.

Pre-registration frozen `c2913dcd`, Amendment 1 (before first compute) `c2ceab24`.

## 2. What ran

Image `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`,
720-cell channel, MRF cell zone `rotor` created at **144 cells**, np=1.

| stage | omega | rc | `OOMKilled` | core-min |
|---|---|---|---|---|
| `omegaP` | 300.0 | 1 | false | 0.1500 |
| `omega0` | 0.0 | 1 | false | 0.1500 |
| `clean` | 0.0 | 1 | false | 0.1333 |
| `fdp` | 300.0 | 1 | false | 0.1333 |
| `fdm` | 300.0 | **2** | false | 0.1333 |

## 3. Crash triage — done before anything was rebuilt

Every `rc = 1` stage carried the same fatal:

> `--> FOAM FATAL IO ERROR: (openfoam-2506)`
> `Entry 'MRF' not found in dictionary "constant/MRFProperties"`
> `file: constant/MRFProperties at line 15 to 20.`
> `From Foam::dictionary& Foam::dictionary::subDict(const Foam::word&, Foam::keyType::option)`

The frozen `MRFProperties.template` used OpenFOAM's own **named-zone** layout
(`MRF1 { … }` at top level). DAFoam's differentiable list is not that:
`IOMRFZoneListDF` → `MRFZoneListDF` looks up a **single top-level sub-dictionary
`MRF`**, the layout of DAFoam's own `UAV_Propeller` tutorial. **The defect is in this
lane's instrument.**

## 4. The verdict this probe REFUSED to report, and why it matters more than the crash

The frozen §4 mapping says *"`MRFProperties` rejected … → `BLOCKED` (capability absent
from this build)"*. **The antecedent fired for a reason the mapping did not contemplate,
and reporting `BLOCKED` would have been FALSE.** It would have told D11's costing that
this box cannot do MRF adjoints — when the capability was never reached and so was never
shown absent. `BLOCKED` requires reaching a capability and finding it gone.

**A gate whose antecedent can be tripped by the instrument that tests it is not measuring
what its label says.** That is the transferable finding of this row, and it is now a
gate clause in every D11 successor: *a fatal originating in this lane's own files is
`NOT A RESULT`, never `BLOCKED`.*

**Second miss, recorded rather than smoothed over:** `fdm` exited **2**, not 1, and that
distinct exit code sat unexamined beside four `rc = 1`s. It was a **separate defect**
(`argparse` refusing `-uOffset -1.0e-3`) and it survived two further attempts before
being triaged. **A distinct exit code beside a cluster of others is a distinct finding,
and this lane treated it as noise.**

## 5. Observation, carried forward as an observation and never as a result

`omegaP` printed `TPIn: 1.26299103423533` before dying — the primal completed, and only
the **adjoint-side** MRF list construction failed, hinting the primal and the
differentiable list read the dictionary by different paths. **Not graded, not evidence.**

## 6. Cost

**0.7166 core-min gross**, against a prediction of 3.5 and a cap of 5.0 (`0.205×`; guard
never fired). **= $0.000613 DERIVED, NOT MEASURED**, $0.0513/core-h c7a.4xlarge,
reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5).

**All 0.7166 core-min is NAMED WASTE** (§6) — six containers, no graded quantity — netted
off nothing. Calibration row **C-69**.

## 7. Successors

`../curriculum_D11_mrf_probe_Dprime/` (dictionary, `NOT A RESULT`) →
`../curriculum_D11_mrf_probe_Oprime/` (omega, `NOT A RESULT`) →
`../curriculum_D11_mrf_probe_Fprime/` (CLI, **`GATE REACHED`**).
