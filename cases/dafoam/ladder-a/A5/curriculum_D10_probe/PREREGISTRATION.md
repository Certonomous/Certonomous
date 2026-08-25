# D10 CAPABILITY PROBE — thermal-objective reachability — PRE-REGISTRATION

**Form:** the 10-line mini-prereg Sanaa authorised 2026-08-25 for standard
verification cases (*"Prereg goes template-speed … minutes to freeze, not sessions"*).
This is a **probe**, not a curriculum case: it buys reachability, nothing else.
**Frozen at the commit that adds this file. No gate, threshold, cap or label below
may change after the first container starts.**

**Item:** `EXPERTISE_CURRICULUM.md` Tier 4, D10 row — *"PROBE FIRST: thermal-objective
reachability on the installed images (zero/cheap probe, ≤5 core-min)"*.
**Author:** dafoam `lab-lane`, 2026-08-25. **Nothing here is filed, sent or posted
anywhere** (`CLAUDE.md` rule 7).

---

### 1. Capability under probe
Can a **thermal objective reach the adjoint** on this box's DAFoam build — specifically
the `DAFunctionWallHeatFlux` function (`"type": "wallHeatFlux"`), declared with
`addToAdjoint: True` on a `DASimpleFoam` case whose `T` field is a solved adjoint state
(`src/adjoint/DAResidual/DAResidualSimpleFoam.C:221–235`)?

### 2. Image, by hash
`dafoam/opt-packages:latest`, digest **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**.
Chosen because it is the **stock** image — the one every published ladder number was
measured on (`TOOLCHAIN_INVENTORY.md` §3) — and the question is what the *shipped*
build can reach, not what a local patch adds. `TOOLCHAIN_INVENTORY.md` §11 binds:
**the hash is the identity; the version string is not.**

### 3. What "reachable" means — a NUMBER read back from disk, frozen before the run
| gate | quantity, read from JSON on disk | threshold |
|---|---|---|
| **G10-1** | `HFX` key present in `base/d10_base.json` with `status == COMPLETE` | present |
| **G10-2** | `HFX_base` | finite AND `\|HFX_base\| > 1.0e-12` |
| **G10-3a** | `\|HFX_clean − HFX_base\| / \|HFX_base\|` (unplanted second copy) | `≤ 1.0e-12` |
| **G10-3b** | `\|HFX_plant − HFX_base\| / \|HFX_base\|` (the plant) | `> 1.0e-6` |
| **G10-4** | `max \|d(HFX)/d(patchV)\|` over a **non-empty** component set | finite AND `> 1.0e-12` |

**"Runs without error" is not a gate here and appears nowhere above.**

### 4. What "unreachable" means, and the verdict it maps to — decided in advance
- `wallHeatFlux` absent from the build / function never constructed / adjoint never
  returns a `dHFX_dpatchV` key → **`BLOCKED`** (capability absent from this image).
- Any `HFX` or derivative component NaN/inf → **`GATE FAIL`**.
- `HFX` finite but the derivative set is **all exactly zero** → **`GATE FAIL`**
  (silently-zero thermal adjoint).
- Plant moves nothing, or the clean copy does not reproduce the baseline → grader
  **REFUSES, exit 2** → **`NOT A RESULT`**.
- All five gates hold → **`GATE REACHED`**.

**This probe can fail four different ways. A probe that cannot fail is not a probe.**

### 5. The planted control (CLAUDE.md rule 3)
- **What:** `+1.234 K` added to the internal field of `0/T`.
- **Where:** the `plant` stage only, at `<run root>/plant/0/T`; the baseline reads
  `internalField uniform 293.15;` and the planted copy reads `uniform 294.384;`.
- **Read back from disk:** `d10_grade.py:read_plant_from_disk()` opens all three staged
  `0/T` files and refuses unless the exact planted string is present. The launcher
  independently asserts the plant landed before the container starts.
- **The refusal:** if the relative HFX response is `≤ 1.0e-6` the grader raises
  `Refusal` and exits 2 with *"the reader has not been shown able to see a non-zero"*.
- **Discrimination control:** the `clean` stage is an unplanted second copy graded on
  **the same quantity that reaches the verdict** (HFX), so the plant response cannot be
  attributed to run-to-run noise. L-302's trap is closed explicitly: `dHFX_dpatchV`
  is asserted **non-empty** before it is iterated, and an empty set REFUSES.
- **The control is proven able to refuse:** `python3 d10_grade.py --selftest` runs six
  synthetic records — healthy, blind plant, zero adjoint, empty component set, noisy
  clean copy, absent function — and asserts the verdict each must produce. It was run
  green before this file was committed.

### 6. Cost
- **Predicted: 2.5 core-min** (one mesh container + three np=1 stages on 720 cells).
- **Registered cap: 5.0 core-min**, enforced in `d10_stage_and_run.sh` by a cumulative
  `CAP_CORE_MIN` guard that refuses to launch the next stage, and by a per-stage
  `timeout` of **240 s** wall. **An overrun STOPS the probe; it does not get a new budget.**
- `$0.00214` derived at cap `$0.00428` — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`
  (`COMPUTE_BUDGET_CHARTER.md` §5 — the box cannot read its own billing).

### 7. np and decomposition
`np = 1`, `system/decomposeParDict` carries `numberOfSubdomains 1`. **With np = 1 the
parallel-determinism question does not arise**, and the decomposition defect class
(D-B) is out of reach of this probe by construction.

### 8. What this probe does NOT establish
Reachability only. It establishes **nothing** about the correctness, accuracy or sign of
`HFX` or of `d(HFX)/d(patchV)`; nothing about the U-bend mesh, CHT coupling,
`DAHeatTransferFoam`, wall-function sensitivity, or a two-objective front; and nothing
about D10 at its own scale. **A correct plant-and-refuse is evidence about the gate it
guards, never about the file.**

### 9. Frozen instruments (md5 at the pre-registration commit)
| file | md5 |
|---|---|
| `d10_run_script.py` | `1d04151dba68061fce2c34b35f9fcb4e` |
| `d10_stage_and_run.sh` | `66671537257458238d94c38d45b112c1` |
| `d10_grade.py` | `0ef3e76a83fa6baa88d5b0e3d28a300b` |
| `d10_case/system/blockMeshDict` | `a7c5e3cf6a86eb42b47455cfcdc56fbd` |
| `d10_case/0.orig/T` | `78f76f52d06624ad0d8e734558c37cb6` |

### 10. Disclosures
- **Pre-freeze reconnaissance, disclosed** (the D2 precedent, where a 0.0333 core-min
  probe ran before the freeze and was named on the prereg's first screen): four
  read-only container inspections of the image's source tree and Python layer
  (which `DAFunction` classes exist, whether `DAResidualSimpleFoam` carries a `T`
  residual, what `pyDAFoam.py` documents), and **one mesh-only container run**
  (`blockMesh` + `checkMesh`; 720 cells, *Mesh OK*, max aspect ratio 2.0). **No solver
  ran, and no quantity named in §3 was computed, before this file was committed.**
- **Prior-work check (`CLAUDE.md` rule 9 / PRIOR_WORK_INVENTORY):** A5's U-bend
  run script declares an `HFX` `wallHeatFlux` function with **`addToAdjoint: False`**
  (`A5_work/UBend_Channel_pressureloss/runScript.py`), so a wallHeatFlux *value* has
  been computed incidentally on this box before. **The adjoint half — a thermal
  objective with `addToAdjoint: True` — has never run here, was never graded, and is
  what D10 actually needs.** This probe is not a re-buy.
- **Territory:** thermal *objective design* for D10 proper is coordinated with
  heat-transfer at the chief's table (curriculum D10 row); this probe is DAFoam
  execution inside `cases/dafoam/` and asks nothing of that team.
