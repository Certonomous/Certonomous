# D10-P′ — THE PLANT RE-BUY of the D10 capability probe — PRE-REGISTRATION

**Form:** the 10-line mini-prereg. **Frozen at the commit that adds this file; no
container of D10-P′ has run.**
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

### 0. Why this exists, and what it is NOT

The **D10 capability probe as registered** (`../curriculum_D10_probe/`, frozen
`c2913dcd`, Amendment 1 `c2ceab24`) **RAN and returned `NOT A RESULT`.** Its grader
refused, exit 2, on its own planted control:

> `PLANTED-ZERO REFUSAL: a +1.234 K plant in 0/T moved HFX by only 0.000000e+00 relative (floor 1.0e-06).`

**The refusal is correct and the cause is the instrument, not the capability.** D10's
plant was placed on the **initial internal field** of `0/T`. A converged steady solve is
independent of its initial guess by construction, so that plant **could not have moved
the objective whatever the capability did** — the refusal was guaranteed before the
container started. The measured `0.000000e+00` is the proof, and the three stages
agreeing to the last digit (`HFX = 2846.286928273276` in base, plant and clean alike)
is the same fact stated a second way.

**`CLAUDE.md` rule 2 closes D10's gates after its first compute, and this document does
not reopen them.** D10's verdict stands at `NOT A RESULT` and is not revised. Following
the family's own precedent — D1 arm C crashed on a frozen-comparator key mismatch and
was **re-registered as mini-item D1-C′** rather than repaired in place — the plant is
re-bought here as a **new mini-item with its own freeze**. The
`VERIFICATION_CHARTER.md` §2d.1 repair exception is **deliberately NOT invoked**: it
would arguably fit, but a probe whose gate has already been seen to fail is exactly the
place not to lean on an exception, and a fresh freeze costs 0.4 core-min.

### 1. Capability under probe
Unchanged from D10 §1: can a thermal objective — `DAFunctionWallHeatFlux`,
`"type": "wallHeatFlux"`, `addToAdjoint: True` — **reach the adjoint** on this build?

### 2. Image, by hash
`dafoam/opt-packages:latest`, digest
**`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**. Unchanged.

### 3. What "reachable" means — NUMBERS read back from disk
**Gates G10-1, G10-2, G10-3a, G10-3b and G10-4 are carried over from D10 §3 with their
thresholds UNCHANGED, to the digit.** The only thing that differs anywhere in this
document is **where the plant is placed**, §5.

| gate | quantity, from JSON on disk | threshold |
|---|---|---|
| **G10-1** | `HFX` present, `status == COMPLETE` | present |
| **G10-2** | `HFX_base` | finite AND `\|HFX_base\| > 1.0e-12` |
| **G10-3a** | `\|HFX_clean − HFX_base\| / \|HFX_base\|` | `≤ 1.0e-12` |
| **G10-3b** | `\|HFX_plant − HFX_base\| / \|HFX_base\|` | `> 1.0e-6` |
| **G10-4** | `max \|d(HFX)/d(patchV)\|`, **non-empty** set | finite AND `> 1.0e-12` |

### 4. What "unreachable" means, and the verdict it maps to
Carried over from D10 §4 verbatim: absent capability → **`BLOCKED`**; NaN/inf →
**`GATE FAIL`**; all-exactly-zero derivative → **`GATE FAIL`**; blind plant or noisy
clean copy → grader **REFUSES, exit 2** → **`NOT A RESULT`**; all five hold →
**`GATE REACHED`**.

**Registered in advance, because the failure has already been seen once:** if the
re-bought plant ALSO returns exactly `0.0`, the verdict is again `NOT A RESULT` and the
finding is then about `wallHeatFlux` — a thermal objective that cannot see its own wall
temperature. **This probe is not permitted a third plant.**

### 5. The planted control — THE ONE THING THAT CHANGED
- **What:** the same `+1.234 K`.
- **Where:** the **heated lower wall's `fixedValue` boundary temperature** in `0/T`,
  `353.15 → 354.384`. That is an **input to the converged answer**, not to the initial
  guess, so a solve that responds to its own boundary conditions must move `HFX`.
- **Read back from disk:** `d10p_grade.py:read_plant_from_disk()` refuses unless the
  planted stage's `0/T` carries `uniform 354.384;` and the base and clean stages carry
  `uniform 353.15;`. The launcher asserts the substitution landed before the container.
- **The refusal, the discrimination control and the non-emptiness assertion** are D10's,
  unchanged.
- **Proven able to refuse:** `python3 d10p_grade.py --selftest` — 6/6 green before this
  commit.

### 6. Cost
- **Predicted: 0.45 core-min** — this is no longer an estimate but a **measurement**:
  D10 ran the identical three stages for **0.4167 core-min** gross.
- **Registered cap: 5.0 core-min**, the same guard and the same 240 s per-stage timeout.
  **An overrun STOPS the probe.**
- `$0.00038` derived — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`.
- **D10's 0.4167 core-min is NOT waste and is not absorbed into this row's ratio.** It
  bought a real finding — that a steady-state probe cannot be planted on its initial
  field — and it is reported separately in `docs/COST_CALIBRATION.md`.

### 7. np and decomposition
`np = 1`, `numberOfSubdomains 1`. **With np = 1 the parallel-determinism question does
not arise.**

### 8. What this probe does NOT establish
D10 §8 verbatim: reachability only; nothing about correctness, accuracy or sign of
`HFX` or its derivative; nothing about the U-bend mesh, CHT, `DAHeatTransferFoam` or a
two-objective front.

### 9. Frozen instruments (md5 at this commit)
| file | md5 | note |
|---|---|---|
| `d10p_run_script.py` | `1d04151dba68061fce2c34b35f9fcb4e` | **byte-identical to D10's** — the driver is not what was wrong |
| `d10p_stage_and_run.sh` | `83ade05474fbd3df7b0c4a53dba3a7c2` | plant target moved to the wall BC |
| `d10p_grade.py` | `00949e6d8d5431c65a49f7add4f93f09` | plant constants only |
| `d10p_case/0.orig/T` | `78f76f52d06624ad0d8e734558c37cb6` | **byte-identical to D10's** |

The run script and the case being **byte-identical** is the evidentiary point: the only
difference between a `NOT A RESULT` and whatever this returns is where the plant sits.
