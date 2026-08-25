# D12-E′ — CHECKPOINT-ENVELOPE SECOND POINT — PRE-REGISTRATION

**Form:** the 10-line mini-prereg. **Frozen at the commit that adds this file; no
container of D12-E′ has run.**
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

### 0. What this is, and the sharper thing it is NOT

**This probe grades no capability and reaches no verdict about DAFoam.** D12 already did
that and returned **`GATE REACHED`** (`../curriculum_D12_unsteady_probe/`, frozen
`c2913dcd`). This is a **measurement**, pre-registered because rules 2 and 12 do not
exempt measurements from being registered and costed before a container starts.

**The problem it fixes.** D12's registered envelope was measured at **one** window
length — 5 timesteps — and returned `maxrss 0.7943 GiB` after the primal and
`1.3269 GiB` after the adjoint, a rise of **0.5325 GiB**. That rise contains **two
different things**: the **fixed** cost of the `dRdWTPC` preconditioner matrix (317
colours, assembled once, `Computing dRdWTPC 6.88 s` → `10.8 s` in the base log) and the
**per-step** cost of the checkpoints. **One point cannot separate them, and a single
point extrapolates to anything.** Attributing the whole rise to the 5 steps gives
`0.1065 GiB/step`, which at the tutorial's own 300-step window projects to ~32 GiB —
**above this 30 GiB box and far above the standing 12 GiB `MemAvailable` floor.** That
projection is an **UPPER BOUND with no lower bound beside it**, and D12's costing must
not be written on it. Publishing a memory ceiling derived from an unseparated fixed
term would be the same error class as quoting a GCI from three non-monotone values.

### 1. Capability under probe
**None.** The capability question is closed by D12.

### 2. Image, by hash
`dafoam/opt-packages:latest`, digest
**`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**, and the
case, mesh, `daOptions` and run script are **byte-identical to D12's**
(`d12e_run_script.py` md5 `a57676f6a1003d7d483cb2d799081512`, unchanged). **Only
`endTime` differs: `0.05` → `0.10`, i.e. 5 steps → 10 steps.**

### 3. What is measured, and what is registered before the run
One stage, `base`, `compute_totals`, np=1. Read back from disk:

| quantity | source |
|---|---|
| `maxrss_GiB_after_primal`, `maxrss_GiB_after_adjoint` | `base/d12e_base.json`, written by the run script |
| `du_delta_B` | the launcher's ledger |
| `OOMKilled`, `rc` | `docker inspect`, no `--rm` |

**The registered derivation, fixed in advance so it cannot be chosen to fit:** with
`ΔR(n)` the adjoint's RSS rise at `n` steps, the two-point fit is

    per_step_GiB = (ΔR(10) − ΔR(5)) / 5
    fixed_GiB    = ΔR(5) − 5 × per_step_GiB

using **`ΔR(5) = 0.5325 GiB` from D12's own artifact**, not re-measured here.

### 4. What a failure means, and the verdict it maps to
- `OOMKilled true` or `rc ≠ 0` → **`NOT A RESULT`** for the fit, and D12's costing keeps
  the single-point **UPPER BOUND** with its "no lower bound" caveat intact.
- **`per_step_GiB ≤ 0`** — i.e. 10 steps cost no more RSS than 5 → **`NOT A RESULT`**,
  stated plainly rather than reported as "zero per-step cost". A non-positive slope
  means either `reduceIO: True` is not holding per-step state in RAM at all, or the
  allocator is not returning the difference to `ru_maxrss`; **this probe cannot tell
  those apart and will not pretend to.**
- A finite positive slope → the fit is **reported**, and it is reported as a **two-point
  fit on a linear assumption that this probe does not test** — two points cannot detect
  curvature.

**There is no `PASS` available here, because there is no gate.** The outputs are
`NOT A RESULT` or a reported measurement with its assumptions named.

### 5. Control
The control is D12's own artifact: `ΔR(5)` is read from `D12/base/d12_base.json`, a file
committed to by a frozen probe that already passed its planted control and its
clean-copy discrimination control. **This probe plants nothing**, and that is disclosed
rather than dressed up: it measures a resource, not a physical quantity, and there is no
"blind reader" failure mode for `ru_maxrss` that a plant would catch. **The honest
control on a resource measurement is the second point itself**, which is what this is.

### 6. Cost
- **Predicted: 0.75 core-min.** Measured basis: D12's `base` stage ran 5 steps for
  **0.4833 core-min** (29 s wall), of which ~7.7 s is python/IDWarp startup, ~3.9 s the
  one-off `dRdWTPC` assembly, `0.195 s`/step primal and `2.158 s`/step adjoint. Five more
  steps adds `5 × (0.195 + 2.158) ≈ 11.8 s ≈ 0.20 core-min`.
- **Registered cap: 3.0 core-min**, the same cumulative guard, 600 s per-stage timeout.
  **An overrun STOPS the probe.**
- `$0.00064` derived — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`.

### 7. np and decomposition
`np = 1`, `numberOfSubdomains 1`. **With np = 1 the parallel-determinism question does
not arise.** Container ceiling `--memory 12g` with `--memory-swap` equal; host
`MemAvailable` checked against the 12 GiB floor before launch.

### 8. What this probe does NOT establish
It measures **`ru_maxrss` of one process on one mesh at two window lengths**, nothing
more. It does not establish that the envelope is linear in steps — **two points cannot**
— nor that `ru_maxrss` tracks the checkpoint allocation faithfully, nor anything about
`reduceIO: False`, which moves the same state to disk and is **not probed**, nor
anything at np > 1, nor anything about a mesh other than this 2,450-cell one.

### 9. Frozen instruments (md5 at this commit)
| file | md5 | note |
|---|---|---|
| `d12e_run_script.py` | `a57676f6a1003d7d483cb2d799081512` | **byte-identical to D12's** |
| `d12e_controlDict_probe` | `a5da68342f7ffec577d7100a857fc0be` | `endTime 0.10` — the only substantive change |
| `d12e_stage_and_run.sh` | `3d62bd782aaf6e13125b6a3513424532` | one stage instead of three; paths |
