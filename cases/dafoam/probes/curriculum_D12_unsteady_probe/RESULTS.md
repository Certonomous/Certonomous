# D12 UNSTEADY-ADJOINT CAPABILITY PROBE — RESULTS

## 1. Verdict

**`GATE REACHED`.** The **unsteady adjoint** — `DAPimpleFoam` under
`DAFoamBuilderUnsteady` with `unsteadyAdjoint: {"mode": "timeAccurate", "reduceIO": True}`
— returns a finite, non-zero total derivative of a **time-averaged** objective on image
`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`.

Pre-registration frozen `c2913dcd`, Amendment 1 (before first compute) `c2ceab24`;
grading path `d12_grade.py` md5 `7797ec3368390121368513489c812af5`, verified against the
HEAD blob before the launch. **This probe reached its gate on the FIRST attempt.**

## 2. Gates

| gate | verdict | measured |
|---|---|---|
| **G12-1** | `PASS` | `DAPimpleFoam` unsteady primal completed; time-averaged `CD = 8.9903939104e-02` |
| **G12-3a** | `PASS` | clean copy reproduces base to **`0.000e+00`** relative (tol `1.0e-12`) |
| **G12-3b** | `PASS` | **plant response `6.270133e-04`** relative, floor `1.0e-9`; `obj_plant = 8.9960310069e-02` |
| **G12-2** | `PASS` | `max |d(obj)/d(shape)| = 1.1622935280e-01` over **4** components: `[3.5023163495e-02, 2.8868992750e-02, 5.2337196550e-02, −1.1622935280e-01]` |
| **G12-4** | `PASS` | `OOMKilled false` on every stage |

**Completion evidence** (`CLAUDE.md` rule 4, the limbs this probe can carry): `rc = 0`;
an `End` line present in the base stage log; the `endTime` directory `0.05` exists; cold
start asserted **before** each launch. Plant read-back on disk: `plant/d12_plant.json`
carries `shape[0] = 1.234e-03`.

## 3. Checkpoint-storage envelope — REPORTED, not gated

Mesh **2,450 cells** (`Global Cells: 2450`), np=1, 5 timesteps, `reduceIO: True`.

| quantity | measured |
|---|---|
| `maxrss` after primal | **0.7943382263 GiB** |
| `maxrss` after adjoint | **1.3268737793 GiB** |
| **adjoint RSS rise** | **0.5325355530 GiB** |
| case-dir disk delta, primal + adjoint (`base`) | **2,843,578 B** |
| case-dir disk delta, primal only (`clean`) | **2,666,569 B** |
| **adjoint disk delta** | **177,009 B ≈ 0.169 MiB** |
| `OOMKilled` | **false**, every stage |

**With `reduceIO: True` the checkpointing is RAM-dominant**: the adjoint adds 0.53 GiB of
resident memory and **0.17 MiB** of disk.

**Per-step timing anchors, read from the base stage log** — the first this lab holds for
an unsteady adjoint:

| term | measured |
|---|---|
| primal | **0.195 s / timestep** (`ExecutionTime` 0.93 s at `t=0.01` → 1.71 s at `t=0.05`) |
| `dRdWTPC` assembly, once | **≈ 3.92 s** (`Computing dRdWTPC 6.88 s` → `dRdWTPC: 316 of 317, ExecutionTime: 10.8 s`), **317 colours** |
| unsteady adjoint | **2.158 s / timestep** (10.54 s → 21.33 s over 5 backward steps) |
| python/OpenMDAO/IDWarp startup | **≈ 7.7 s** per invocation (29 s wall − 21.33 s final `ExecutionTime`) |

**The adjoint costs ~11× the primal per timestep.** That ratio is the single most useful
number for D12's costing.

## 4. What this does NOT establish

Reachability only. **Nothing** about the correctness, accuracy, FD agreement or sign of
the unsteady adjoint. Nothing about a developed vortex-shedding limit cycle, window
length, or `δ_repeat` on a time average: the probe starts from `0_orig`, **so
`CD = 0.0899` is NOT a physical drag coefficient and is never to be quoted as one.**

**The envelope is a 5-step anchor, not a bound.** A single window length **cannot
separate** the fixed `dRdWTPC` cost from the per-step checkpoint cost — see
`../curriculum_D12_unsteady_probe_Eprime/RESULTS.md`, which bought the second point and
found the per-step term **not resolvable**. `reduceIO: False`, which moves the same
state to disk, is **not probed**.

## 5. Cost

| | |
|---|---|
| predicted | **4.0 core-min** |
| actual gross | **0.8500 core-min** — mesh container + `base` 0.4833 + `plant` 0.1667 + `clean` 0.1500 |
| ratio | **0.213×** |
| cap | 6.0 core-min; **`0.142×` of cap**, guard never fired |
| derived | **$0.000727 DERIVED, NOT MEASURED**, $0.0513/core-h c7a.4xlarge, reported-by-owner |
| waste | **0.000 core-min** |

**The 4.0 core-min prediction over-estimated by 4.7×**, chiefly on the mesh term: the
pyHyp + `plot3dToFoam` + `autoPatch` + `createPatch` + `renumberMesh` chain, which
justified this probe's cap sitting 1.0 core-min above the curriculum's `≤5` estimate,
cost only **≈ 0.037 core-min**. **The disclosed cap increase was not needed.** Calibration
row **C-69**.

## 6. What D12 proper now has

The Tier-5 D12 row's `PROBE FIRST` prerequisite is **discharged**, and its
`NEEDS COSTING` is **answered** — see `../LANE_REPORT.md` §7, which prices D12 from these
anchors and finds the curriculum's `~1,000–3,000 core-min` estimate **4–20× high** for
this mesh and window.
