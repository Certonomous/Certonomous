# D11 CAPABILITY PROBE — MRF / rotating-frame adjoint reachability — PRE-REGISTRATION

**Form:** the 10-line mini-prereg Sanaa authorised 2026-08-25. This is a **probe**.
**Frozen at the commit that adds this file.**

**Item:** `EXPERTISE_CURRICULUM.md` Tier 4, D11 row — *"PROBE FIRST (MRF+adjoint
reachability, ≤5 core-min); case selection after probe"*; the row is **UNPRICED until
this probe**. Named failure mode, carried verbatim: *"MRF interface derivatives
silently zero — a planted-perturbation control on the interface is mandatory."*
**Author:** dafoam `lab-lane`, 2026-08-25. Nothing filed, sent or posted (rule 7).

---

### 1. Capability under probe
Does DAFoam's **MRF rotating-frame formulation reach the adjoint** on this build —
i.e. with an active `MRFProperties` cell zone, does `DASimpleFoam` return a **non-zero,
FD-consistent** total derivative? DAFoam's MRF enters the state residual at
`src/adjoint/DAResidual/DAResidualSimpleFoam.C` — `:39–40` (`IOMRFZoneListDF` lookup),
`:144` (`MRF_.DDt(U_)`), `:183` (`makeRelative`), `:199` (`constrainPressure`),
`:246` (`correctBoundaryVelocity`) — and the differentiable list lives in
`src/adjoint/DAMisc/MRFDF/`.

**Terminology correction, registered before the run:** the curriculum says *"MRF
interface"*. **In this build MRF is a CELL-ZONE formulation, not an interface** — there
is no MRF interface object (`MRFZoneDF.C`, `MRFZoneListDF.C`; an interface treatment
would be AMI, which is a different capability and is not probed here). The mandatory
plant is therefore placed on **the zone's own rotational rate `omega`**, the single
parameter that switches the entire MRF contribution on and off. A plant anywhere else
in the domain would not test the thing suspected of being zero.

### 2. Image, by hash
`dafoam/opt-packages:latest`, digest **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`** —
the stock image, for the same reason as D10: the question is what the shipped build
reaches. `TOOLCHAIN_INVENTORY.md` §11: the hash is the identity.

### 3. What "reachable" means — NUMBERS read back from disk, frozen before the run
Substrate: a 720-cell 2D channel with an MRF cell zone `rotor` (144 cells,
0.08 ≤ x ≤ 0.12), `DASimpleFoam` + Spalart-Allmaras, objective `TPIn`
(`totalPressure` at the inlet), input `patchV` (`patchVelocity`), np=1.

| gate | quantity, read from JSON on disk | threshold |
|---|---|---|
| **G11-1** | `TPIn` at `omega = 300 rad/s` and at `omega = 0` | both finite, `\|TPIn(0)\| > 1.0e-12` |
| **G11-2a** | `\|TPIn_clean − TPIn(0)\| / \|TPIn(0)\|` | `≤ 1.0e-12` |
| **G11-2b** | `\|TPIn(300) − TPIn(0)\| / \|TPIn(0)\|` — **THE PLANT** | `> 1.0e-6` |
| **G11-3** | `max \|d(TPIn)/d(patchV)\|` at `omega = 300`, **non-empty** set | finite AND `> 1.0e-12` |
| **G11-4** | the MRF-active and MRF-inert derivative vectors | **not bit-identical** |
| **G11-5** | `\|adj − FD\| / \|FD\|`, MRF **ON**, central FD, `h = 1.0e-3 m/s` on `patchV[0]` | `≤ 5.0e-2` |

### 4. What "unreachable" means, and the verdict it maps to — decided in advance
- `MRFProperties` rejected / zone not found / adjoint never returns a derivative key →
  **`BLOCKED`** (capability absent from this build).
- Any graded quantity NaN/inf → **`GATE FAIL`**.
- Derivative set **all exactly zero** → **`GATE FAIL`** — this is the curriculum's
  named failure mode and it has its own branch.
- MRF-active and MRF-inert derivatives **bit-identical** while the primal responded →
  **`GATE FAIL`** (the `omega` key reached nothing).
- G11-5 outside its band → **`GATE FAIL`**, with `adj`, `FD` and the error printed.
- FD reference `≤ 1.0e-12` (ratio cannot be formed) → **`NOT A RESULT`** for G11-5.
- Plant moves nothing, or the clean copy does not reproduce → grader **REFUSES, exit 2**
  → **`NOT A RESULT`**: with MRF inert in the primal, no derivative measured here is
  evidence about MRF.
- All six hold → **`GATE REACHED`**.

**G11-4 is registered as a DIAGNOSTIC, necessary and not sufficient**: the base states
differ between the two runs, so a difference does not prove the MRF term is
differentiated. Only **exact identity** is gated on. G11-5 is the real linearisation
test and is gated properly.

### 5. The planted control (CLAUDE.md rule 3), on the MRF zone
- **What:** the MRF zone's rotational rate. **Magnitude: `omega = 300.0 rad/s`**
  (≈ 2865 rpm) against an inert `omega = 0.0`. DAFoam's `MRFZoneDF.C:217` reads a
  scalar key **`omega`**, not `rpm` — verified in-image before the freeze.
- **Where:** `<run root>/omegaP/constant/MRFProperties`, substituted from
  `MRFProperties.template`'s `OMEGA_PLACEHOLDER` by the launcher, which asserts the
  substitution landed before the container starts.
- **Read back from disk:** `d11_grade.py:read_omega_from_disk()` parses all three
  staged `MRFProperties` files and refuses unless the exact planted value is present.
- **The refusal:** relative TPIn response `≤ 1.0e-6` → `Refusal`, exit 2, *"The MRF term
  is not entering the primal, so NO derivative measured here is evidence about MRF."*
- **Discrimination control:** the `clean` stage re-runs `omega = 0` from a fresh stage
  and is graded on **the same quantity that reaches the verdict** (TPIn). L-302's trap
  is closed: `dTPIn_dpatchV` is asserted **non-empty** before iteration; an empty set
  REFUSES.
- **The control is proven able to refuse:** `python3 d11_grade.py --selftest` runs seven
  synthetic records (healthy, inert MRF, zero adjoint, empty set, bit-identical
  adjoints, FD disagreement, noisy clean copy) and asserts each verdict. Run green
  before this file was committed.

### 6. Cost
- **Predicted: 3.5 core-min** (one mesh container + five np=1 stages on 720 cells).
- **Registered cap: 5.0 core-min**, enforced by the cumulative `CAP_CORE_MIN` guard in
  `d11_stage_and_run.sh` and a per-stage `timeout` of **240 s**. **An overrun STOPS the
  probe; it does not get a new budget.**
- `$0.00299` derived at cap `$0.00428` — **DERIVED, NOT MEASURED**.
- `cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED`.

### 7. np and decomposition
`np = 1`, `numberOfSubdomains 1`. **With np = 1 the parallel-determinism question does
not arise.**

### 8. What this probe does NOT establish
Reachability only. **Nothing** about the correctness of MRF adjoint derivatives in
general — G11-5 says only that on this one configuration, this one component, the
adjoint and a central FD agree inside a 5 % band; nothing about AMI or sliding
interfaces, `DATurboFoam`, `MRF` as a design variable (DAFoam 5.0.0 ships **no**
`DAInput` class for MRF — checked, `src/adjoint/DAInput/`), or any real rotor at scale.
It does not price D11's case; §6 of the LANE_REPORT does that separately, or says
UNPRICED and why.

### 9. Frozen instruments (md5 at the pre-registration commit)
| file | md5 |
|---|---|
| `d11_run_script.py` | `2975373099a6125a1c028a935b145e73` |
| `d11_stage_and_run.sh` | `5d50149f915f966931d230a0db85ae88` |
| `d11_grade.py` | `2c9a501514ebdf7134de6196fe13a543` |
| `d11_case/constant/MRFProperties.template` | `0415ab6494e0a32dbb021d3b1ee1d506` |
| `d11_case/system/topoSetDict` | `51b12278a0be51fa63457fc3b5d80d59` |

### 10. Disclosures
- **Pre-freeze reconnaissance, disclosed:** read-only container inspections of the
  image's MRF source (which established the `omega`-not-`rpm` key and the cell-zone
  correction in §1), and **one mesh-only container run** (`blockMesh` + `topoSet`:
  720 cells, cellZone `rotor` created at 144 cells). **No solver ran, and no quantity
  named in §3 was computed, before this file was committed.**
- **Prior-work check:** `PRIOR_WORK_INVENTORY.md` holds no MRF or rotating-frame
  record; the family's rotation work (D-A, `getRotationMatrix3d`) is an **IDWarp mesh-
  warping** defect and is unrelated to MRF. Not a re-buy.
- A registered instrument reduction: the substrate is a purpose-built box, not a real
  ducted fan or swirl passage. That is deliberate — cost is deterministic and the
  capability question is image-level — and it is exactly why §8 says what it says.
