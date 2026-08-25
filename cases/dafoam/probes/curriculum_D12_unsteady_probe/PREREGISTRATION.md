# D12 CAPABILITY PROBE — unsteady-adjoint reachability — PRE-REGISTRATION

**Form:** the 10-line mini-prereg Sanaa authorised 2026-08-25. This is a **probe**.
**Frozen at the commit that adds this file.**

**Item:** `EXPERTISE_CURRICULUM.md` Tier 5, D12 row — *"PROBE FIRST (unsteady-adjoint
reachability, ≤5 core-min)"*; the row **NEEDS COSTING after this probe**, and its
registered gates include a *"checkpoint-storage envelope (disk AND RAM)"*.
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

### 1. Capability under probe
Does the **unsteady adjoint** reach a number on this build — `DAPimpleFoam` driven by
`dafoam.mphys.mphys_dafoam.DAFoamBuilderUnsteady` with
`unsteadyAdjoint: {"mode": "timeAccurate", "reduceIO": True}` — returning a finite,
non-zero total derivative of a **time-averaged** objective (`"timeOp": "average"`)
with respect to a shape design variable? And what does its checkpoint storage cost,
in **RAM and disk**?

### 2. Image, by hash
`dafoam/opt-packages:latest`, digest **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`** —
the stock image. The two patched images differ only in `DALinearEqn.C`
(`TOOLCHAIN_INVENTORY.md` §3), which is the adjoint *linear solver*, not the unsteady
machinery; probing the stock build asks the right question, and R11 adoption is
case-dependent, never global (N-D18).

### 3. What "reachable" means — NUMBERS read back from disk, frozen before the run
Substrate: the **upstream DAFoam `Cylinder` tutorial** — which *is* the curriculum's
D12 case (2D cylinder, time-averaged drag, `DAPimpleFoam`) — at the probe reduction of
§10. np=1.

| gate | quantity, read from JSON on disk | threshold |
|---|---|---|
| **G12-1** | `obj` = time-averaged `CD`, `status == COMPLETE` | finite AND `\|obj\| > 1.0e-12` |
| **G12-3a** | `\|obj_clean − obj_base\| / \|obj_base\|` | `≤ 1.0e-12` |
| **G12-3b** | `\|obj_plant − obj_base\| / \|obj_base\|` — **THE PLANT** | `> 1.0e-9` |
| **G12-2** | `max \|d(obj)/d(shape)\|`, **non-empty** component set | finite AND `> 1.0e-12` |
| **G12-4** | `OOMKilled` from `docker inspect`, every stage | `false` |

**Reported, not gated (the envelope):** `ru_maxrss` after the primal and after the
adjoint, in GiB, written by the run script itself; the staged case directory's byte
delta `du_delta_B` per stage, from the launcher's ledger; `nCells`; `nTimeSteps = 5`.

### 4. What "unreachable" means, and the verdict it maps to — decided in advance
- `DAPimpleFoam` or `mode: timeAccurate` rejected by the build, or the adjoint never
  returns a `dobj_dshape` key → **`BLOCKED`** (capability absent from this image).
  **A `BLOCKED` here is a measured fact about this box's toolchain and it re-prices or
  reshapes D12; it is a result, not a failure.**
- `OOMKilled true` on any stage → **`BLOCKED`** — the checkpoint envelope is exceeded
  at probe scale, which is D12's own named failure mode ("checkpoint storage explosion").
- Any graded quantity NaN/inf → **`GATE FAIL`**.
- Derivative set **all exactly zero** → **`GATE FAIL`** (silently-zero unsteady adjoint).
- Plant moves nothing, plant not readable back from disk, or clean copy does not
  reproduce → grader **REFUSES, exit 2** → **`NOT A RESULT`**.
- All hold → **`GATE REACHED`**.

### 5. The planted control (CLAUDE.md rule 3)
- **What:** `shape[0] = 1.234e-03` (the lab's `1.234` plant constant), the first of the
  tutorial's four shape-function design variables.
- **Where:** the `plant` stage only, passed as `-shapePlant 1.234e-03`; the run script
  writes the realised `shape` vector into `plant/d12_plant.json`.
- **Read back from disk:** `d12_grade.py` reads `plant["shape"][0]` from that JSON and
  **refuses** unless it equals `1.234e-03` to 1e-15. A plant that did not land is not a
  plant.
- **The refusal:** relative `obj` response `≤ 1.0e-9` → `Refusal`, exit 2, *"The
  objective has not been shown able to see the design variable, so no derivative here
  is evidence."*
- **Discrimination control:** the `clean` stage is an unplanted re-run graded on **the
  same quantity that reaches the verdict** (`obj`). L-302: `dobj_dshape` is asserted
  **non-empty** before iteration; an empty set REFUSES.
- **The control is proven able to refuse:** `python3 d12_grade.py --selftest` runs eight
  synthetic records (healthy, blind plant, zero adjoint, empty set, NaN, OOMKilled,
  failed plant read-back, absent adjoint) and asserts each verdict. Run green before
  this file was committed.
- **Completion evidence** (`CLAUDE.md` rule 4, the elements this probe can carry): the
  grader reports `rc`, the presence of an `End` line in the stage log, and whether the
  `endTime` directory `0.05` exists. Cold start is asserted **before** each launch —
  the launcher refuses a stage where `0.01` or `0.05` already exists.

### 6. Cost
- **Predicted: 4.0 core-min** (one mesh container running pyHyp + `plot3dToFoam` +
  `autoPatch` + `createPatch` + `renumberMesh`, then three np=1 stages).
- **Registered cap: 6.0 core-min**, enforced by the cumulative `CAP_CORE_MIN` guard in
  `d12_stage_and_run.sh` and a per-stage `timeout` of **600 s**. **An overrun STOPS the
  probe; it does not get a new budget.**
- **Disclosed departure:** the cap is **1.0 core-min above the curriculum's ≤5 core-min
  estimate** for this probe — `$0.00086` derived. The reason is named in advance: the
  curriculum's estimate did not price **mesh generation**, and this substrate's mesh is
  built by pyHyp inside the probe's own compute. The estimate is the curriculum's; the
  cap is this probe's, and it is registered here before the first container.
- `$0.00342` derived at cap `$0.00513` — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`.

### 7. np and decomposition
`np = 1` (the tutorial ships np=4; this probe runs serial). **With np = 1 the parallel-
determinism question does not arise.** Container memory ceiling `--memory 12g` with
`--memory-swap` equal to it, so the kernel stops a checkpoint explosion rather than the
box swapping; `--oom-score-adj=500`; no `--rm`, so `OOMKilled` survives to be read.
Host `MemAvailable` is checked before launch against the standing **12 GiB floor**.

### 8. What this probe does NOT establish
Reachability only. **Nothing** about the correctness or accuracy of the unsteady
adjoint, its FD agreement, or its sign. Nothing about a developed vortex-shedding
limit cycle, window length, or `δ_repeat` on a time average — the probe starts from
`0_orig`, not from an equilibrium field, so its `obj` is **not a physical CD** and is
never to be quoted as one. **The envelope is measured at 5 timesteps and is a PER-STEP
ANCHOR, not a bound**: `reduceIO: True` holds checkpoints in RAM, so a longer window
moves the cost into memory roughly linearly, and `reduceIO: False` would move it to
disk instead — that arm is **not probed here**.

### 9. Frozen instruments (md5 at the pre-registration commit)
| file | md5 |
|---|---|
| `d12_run_script.py` | `a57676f6a1003d7d483cb2d799081512` |
| `d12_stage_and_run.sh` | `479611b59242a7611bf7868300df05f1` |
| `d12_grade.py` | `7797ec3368390121368513489c812af5` |
| `d12_controlDict_probe` | `be8581cebf99cb59716ccdf488bb610b` |

### 10. Registered probe reductions against the upstream tutorial
Both are reductions, both are registered here before the run, and both are the reason
§8 says what it says:
1. **`endTime 0.05` (5 steps at `deltaT 1e-2`)** instead of the tutorial's `3.0`
   (300 steps).
2. **Start from `0_orig`**, skipping the tutorial's `preProcessing.sh` spin-up
   (`potentialFoam` → 500 `simpleFoam` iterations → a long `pimpleFoam` run to
   equilibrium). A reachability probe does not need a developed flow.
Everything else in `daOptions` is the tutorial's, verbatim.

### 11. Disclosures
- **Pre-freeze reconnaissance, disclosed:** read-only container inspections of the
  image (`DASolver/DAPimpleFoam/` present; `unsteadyAdjoint` sub-dict read at
  `DASolver.C:3427` and `DAPimpleFoam.C:137,141`) and host-side reads of the tutorial.
  **No container ran this case, and no quantity named in §3 was computed, before this
  file was committed.**
- **Prior-work check:** `PRIOR_WORK_INVENTORY.md` records a proposal string
  `f5c-unsteady-probe-run` among **three proposal records the real inbox reader
  REFUSES and which are invisible to the queue** (§3.7, *"Reported, not repaired"*).
  That is an unexecuted, unreachable proposal record — **no unsteady adjoint has run on
  this box**. Not a re-buy. The refused-proposal defect is noted and left alone: it
  does not block this run, and repairing it is not this lane's item.

---

## Amendment 1 — 2026-08-25 — `--bind-to none`, BEFORE FIRST COMPUTE

**Document version 1.1.** The body above is v1.0, committed `c2913dcd`.
**Lines whose number changed above this section: 0.**

**This is a before-first-compute amendment, which `CLAUDE.md` rule 2 permits, and it
therefore states its condition and how the condition was checked.**

**Condition:** no compute had started for any of the three probes.
**How it was checked:** the run root `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12`
**did not exist** — `ls` on it returned *No such file or directory* at 2026-08-25 ~16:58Z,
after the v1.0 freeze and before this amendment. No container of this probe had ever run.

**What changed, and why.** At `ab89210f` (2026-08-25 16:57:52Z), minutes after the
v1.0 freeze, a peer dafoam lane **measured** a defect this probe's launcher was about
to walk into: `mpirun -np 1` inside a container binds every rank to **CPU 0**, because
OpenMPI binds by default and `docker --cpus=1` is a CFS **quota, not a placement**. With
four DAFoam containers live the peer measured each running at **0.2504 of one core** on
a 61 %-idle 16-core box, and **0.9994** after the affinity was corrected — **3.99×, at
zero compute cost** (`cases/dafoam/ladder-a/A6/curriculum_D8/CPU_BINDING_DEFECT_PROPOSED_NOTE.md`,
NOT FILED). Peer containers were live when this probe was about to launch.

The single-token change the peer's note recommends is applied to `d12_stage_and_run.sh`:

    mpirun --allow-run-as-root -np 1 python …
    mpirun --allow-run-as-root --bind-to none -np 1 python …

**What this amendment does NOT do.** It changes **no gate, no threshold, no cap and no
label** — §3, §4, §5, §6 and §7 stand exactly as frozen. It changes only how many host
cores one rank is allowed to land on. Its whole effect is on **wall time**, and
therefore on whether the registered cap in §6 is honest rather than a lottery on peer
scheduling. The cap itself is **unchanged**; had the fix not been applied, an overrun
would still have stopped the probe.

**Instrument hash superseded (§9 of the frozen body is struck for this one row, not
rewritten):**

| file | md5 at v1.0 | md5 at v1.1, the file that ran |
|---|---|---|
| `d12_stage_and_run.sh` | `479611b59242a7611bf7868300df05f1` | `6e3453c2c439b9e7dcfd260b3af225cb` |

All other instrument hashes in §9 are unchanged and still bind.
