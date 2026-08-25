# D11-D′ — THE DICTIONARY RE-BUY of the D11 MRF capability probe — PRE-REGISTRATION

**Form:** the 10-line mini-prereg. **Frozen at the commit that adds this file; no
container of D11-D′ has run.**
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

### 0. Why this exists, and the verdict it does NOT claim

The **D11 capability probe as registered** (`../curriculum_D11_mrf_probe/`, frozen
`c2913dcd`, Amendment 1 `c2ceab24`) **RAN.** All five stages exited non-zero
(`rc = 1, 1, 1, 1, 2`; `OOMKilled false` on every one) on the same fatal:

> `--> FOAM FATAL IO ERROR: (openfoam-2506)`
> `Entry 'MRF' not found in dictionary "constant/MRFProperties"`
> `file: constant/MRFProperties at line 15 to 20.`
> `From Foam::dictionary& Foam::dictionary::subDict(...)`

No JSON was written, so the frozen grader refused on a missing artifact and D11 stands
at **`NOT A RESULT`** — 0.7166 core-min of a 5.0 cap.

**Crash triage, done before anything was rebuilt, because a crash is a finding until
triage says otherwise.** The frozen `MRFProperties.template` used OpenFOAM's own
named-zone layout (`MRF1 { … }` at top level). DAFoam's differentiable list is not that:
`IOMRFZoneListDF` → `MRFZoneListDF` looks up a **single top-level sub-dictionary
`MRF`**, which is the layout of DAFoam's own tutorial
(`/home/ubuntu/dafoam-tutorials/UAV_Propeller/constant/MRFProperties`). **The defect is
in this lane's instrument.**

**This matters more than a normal instrument bug, and it is registered here rather than
tidied away.** D11 §4's frozen mapping says *"`MRFProperties` rejected … → `BLOCKED`
(capability absent from this build)"*. **The antecedent fired for a reason the mapping
did not contemplate, and reporting `BLOCKED` would have been FALSE** — it would have
told D11's costing that this box cannot do MRF adjoints, when the capability was never
reached and therefore never shown absent. **A gate whose antecedent can be tripped by
the instrument that tests it is not measuring what its label says.** The lane refused
that verdict and re-bought instead.

Following D1-C′'s precedent, and for the same reason given in D10-P′ §0, the
`VERIFICATION_CHARTER.md` §2d.1 repair exception is **not invoked**; this is a fresh
freeze.

**One observation is carried forward as an OBSERVATION, never a result:** the omegaP
stage printed `TPIn: 1.26299103423533` before dying, i.e. the primal completed and only
the *adjoint-side* MRF list construction failed. That hints the primal and the
differentiable MRF list read the dictionary by different paths. **It is not graded, it
is not evidence, and D11-D′ does not rest on it.**

### 1. Capability under probe
Unchanged from D11 §1, including the registered terminology correction: **MRF is a
CELL-ZONE formulation in this build, not an interface**, so the mandatory plant sits on
the zone's own `omega`.

### 2. Image, by hash
`dafoam/opt-packages:latest`, digest
**`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**. Unchanged.

### 3. What "reachable" means
**Gates G11-1, G11-2a, G11-2b, G11-3, G11-4 and G11-5 are carried over from D11 §3 with
every threshold UNCHANGED to the digit** — plant floor `1.0e-6`, clean tolerance
`1.0e-12`, derivative floor `1.0e-12`, FD band `5.0e-2`, FD step `h = 1.0e-3 m/s`
central on `patchV[0]`, `omega` plant `300.0 rad/s` against an inert `0.0`. The
substrate (720-cell channel, `rotor` zone of 144 cells over `0.08 ≤ x ≤ 0.12`), the
driver and the objective are D11's, byte-identical.

### 4. What "unreachable" means, and the verdict it maps to
D11 §4 carried over verbatim, **with one clause added before the run**: a fatal that is
a **dictionary or setup error in this lane's own files** is **`NOT A RESULT`**, never
`BLOCKED` — `BLOCKED` is reserved for the capability being shown absent from the build,
which requires reaching it first. That distinction is what D11 paid 0.7166 core-min to
learn, and it is now a gate clause rather than a lesson.

### 5. The planted control — unchanged, on the MRF zone
`omega = 300.0 rad/s` versus `0.0`, substituted into `constant/MRFProperties` from
`OMEGA_PLACEHOLDER`; asserted landed by the launcher before each container; read back
off disk by `d11p_grade.py:read_omega_from_disk()`, which refuses unless the exact value
is present; refusal text and discrimination control unchanged; `dTPIn_dpatchV` asserted
**non-empty** before iteration. **Proven able to refuse:** `python3 d11p_grade.py
--selftest` — 7/7 green before this commit.

### 6. Cost
- **Predicted: 1.2 core-min.** Basis, and it is measured rather than guessed: D11's six
  containers cost **0.7166 core-min** while dying at adjoint setup; D11-D′ runs the same
  six but two of them now carry an adjoint solve through to completion, and D10 measured
  a completed primal+adjoint on this identical 720-cell substrate at 0.1833 core-min
  against 0.1167 for a primal alone.
- **Registered cap: 5.0 core-min**, same guard, same 240 s per-stage timeout.
  **An overrun STOPS the probe.**
- `$0.00103` derived — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`.
- **D11's 0.7166 core-min is reported separately and is NOT absorbed into this row's
  ratio.** Under `COMPUTE_BUDGET_CHARTER.md` §6 it is **named waste** — six containers
  that produced no graded quantity — and it is named as such in
  `docs/COST_CALIBRATION.md`, not folded away.

### 7. np and decomposition
`np = 1`, `numberOfSubdomains 1`. **With np = 1 the parallel-determinism question does
not arise.**

### 8. What this probe does NOT establish
D11 §8 verbatim: reachability only; nothing about the general correctness of MRF adjoint
derivatives; nothing about AMI or sliding interfaces, `DATurboFoam`, MRF as a design
variable (DAFoam 5.0.0 ships no `DAInput` class for it), or any real rotor at scale.

### 9. Frozen instruments (md5 at this commit)
| file | md5 | note |
|---|---|---|
| `d11p_run_script.py` | `2975373099a6125a1c028a935b145e73` | **byte-identical to D11's** |
| `d11p_stage_and_run.sh` | `345b0b596b6e418877e1779cc3201b74` | the `omega` assertion regex, and paths |
| `d11p_grade.py` | `a686c002a01be004d4f2f8726622b27f` | paths and labels only; every threshold identical |
| `d11p_case/constant/MRFProperties.template` | `e7d601ae02d9a3bc1c9f221b6792dea5` | **the one substantive change: DAFoam's `MRF { … }` layout** |

### 10. Disclosure
The corrected layout was taken key-for-key from DAFoam's own `UAV_Propeller` tutorial,
**including its `selectoinMode` misspelling** — that is upstream's spelling, and
correcting it is not this probe's business. No container ran between the D11 failure and
this freeze.
