# F23c — PRE-REGISTRATION (**UNFROZEN DRAFT**): Hagen–Poiseuille pipe flow on an OpenFOAM axisymmetric WEDGE, re-registered after F23b's `BLOCKED`

**Team:** cfd. **Case id:** `F23c_HP_WEDGE`. **Successor to `F23b_HP_WEDGE`, which stands
`BLOCKED` on its own record and is neither re-graded, amended nor edited by this file.**

> ## STATUS: **UNFROZEN DRAFT. VERDICT `PENDING`. NOT FROZEN, NOT COMMISSIONED, NOT ENQUEUED.**
>
> **This lane may not freeze this document.** The freeze is the cfd supervisor's
> non-delegable check 4 (`SUPERVISION_CHARTER.md` §3; CLAUDE.md rule 2), and a lane may
> not freeze its own registration. **No run root exists, no case code exists, no queue
> entry exists, and no solver was started by this lane.** Every threshold below is a
> **proposal for the supervisor's reading**, not a frozen gate. Nothing in this file is
> an authorisation and nothing in it requests one.

**Successor mechanism:** F23b's AMENDMENT 1 §A1.5 clause (4) already fixes the route —
*"a NEW registration under a NEW sha, never a third arm under this one."* F23b's first
compute occurred at **2026-08-31T00:23:32Z** under freeze commit
`57d31dde434f3af8332cc8a882808bdb28e21079`, so **F23b's gates are CLOSED and this defect
is not repairable there by amendment or addendum** — an addendum may not alter a gate, a
threshold, a cap or a label (rule 2), and the defect below **is** a threshold.

**Capability-grid cell (068c2bf0): axisym · steady · incompressible. CPU-only; no GPU arm
exists on this rung and `BLOCKED-GPU` is not used.**

**Case-selection charter:** `instrument-check` (`CASE_SELECTION_CHARTER.md` §3), labelled
so at registration; not a result; counts toward no challenge column; not filmed.

---

## 1. WHAT F23b DIED ON — MEASURED, AND THE MECHANISM RE-DERIVED INDEPENDENTLY HERE

### 1.1 The incident, from the surviving records

| what | value | artifact |
|---|---|---|
| launched | `2026-08-31T00:23:32Z` | `verification/queue/LAUNCH_LOG.tsv:197` |
| launcher exit | `launcher_rc=1  phase=A0` | `verification/runs/F23b_HP_WEDGE_runs/RUN_STATUS.F23b_HP_WEDGE.txt` |
| ended | `2026-08-31T00:25:57Z` (**145 wall s**) | same |
| charged pre-ladder spend | **1.8666666666666667 core-min** | same |
| the deciding reading | best `\|1 − Ubar\|` over 40 checkpoints = **9.692465e−04** against threshold **1.0e−10** | `cases/F23b_HP_WEDGE/launcher.queue.out` — **prose only, see §3** |

The refusal is `grade_f23b.py:787`, inside `arm_reader_is_born()`, on AMENDMENT 1 §A1.5's
gating clause: A0 did not produce an accepting artifact, so the arm-acceptance reader was
**not born**, ARM-P and ARM-F refuse rather than accept-or-reject, and the rung is
**`BLOCKED`**. **That verdict is correct and F23c does not disturb it.**

### 1.2 THE MECHANISM — `|1 − Ubar|` IS A DISCRETISATION ERROR, GATED AS IF IT WERE AN ITERATIVE RESIDUAL

The case imposes a **fixed** body force `G = 0.32` (`vectorSemiImplicitSource`, not the
adaptive `meanVelocityForce`). Nothing in the discrete problem drives `Ubar` to 1. The
converged discrete bulk velocity is whatever the mesh's own stencil returns, and it
differs from 1 by that mesh's truncation error. `|1 − Ubar|` therefore **floors at the
discretisation error and goes to zero only under mesh refinement, never under more
iterations.**

**Re-derived in this invocation by running the frozen model itself** —
`cases/F23b_HP_WEDGE/exact_f23b.py::discrete(nr)`, which returns `ubar_h` directly, so
this is the registration's own arithmetic and not an inversion of its printed table:

| mesh | NR | cells | `ubar_h` (frozen model) | **predicted `\|1 − Ubar\|` at CONVERGENCE** | × the 1e−10 threshold |
|---|---|---|---|---|---|
| **A0 birth control** | 16 | 1,024 | 1.001946614195 | **1.946614e−03** | **1.947e+07** |
| coarse | 64 | 131,072 | 1.000121552455 | **1.215525e−04** | **1.216e+06** |
| medium | 128 | 524,288 | 1.000030028060 | **3.002806e−05** | 3.003e+05 |
| fine | 256 | 2,097,152 | 1.000007141857 | **7.141857e−06** | **7.142e+04** |

**F23b §5.5 set ARM-P's acceptance at `|1 − Ubar| ≤ 1e−10` on the COARSE mesh, whose own
§12 predicts 1.215525e−04 — 1,215,525× the threshold. The acceptance test contradicted
the registered prediction sitting six sections above it.** A0, ARM-P and ARM-F were all
unsatisfiable on any finite mesh.

**Cross-check that the model's own relation closes:** `f·Re = 2 D² G/(ν Ubar)` with
`D = 1, G = 0.32, ν = 0.01` returns **exactly 64.0 at `Ubar = 1`**
(`exact_f23b.f_re(1.0)` → `64.0`), and `64/f·Re_pred` reproduces `ubar_h` to 1e−16 at all
three levels. So `|1 − Ubar|` and F23b's registered `f·Re` predictions are the same
quantity in two costumes, and the registration predicted both.

### 1.3 WHAT F23b'S CITED EVIDENCE ACTUALLY SUPPORTED — one clause of two

§A1.5 justified A0 with F23 §7's measured `Ux` initial residual **2.3e−16 by iteration
4,000** on the same 16 × 64 mesh under the same α_U = 0.7 dictionary. That is a genuine
**iterative** residual and it is real evidence — **for the acceptance test's SECOND
clause only** (`Ux` ≤ 1e−12). **The registration cited evidence for one clause and applied
it to two.** A residual reaching 2.3e−16 says the solve stopped moving; it says nothing
about *where* `Ubar` stopped, and where it stopped is fixed by the mesh.

### 1.4 THE SAME LESSON THE REGISTRATION APPLIED THREE TIMES AND MISSED THE FOURTH

**L-346** (`docs/LESSONS.md:14836`) — *register the floor FROM the predicted
discretisation error of the ladder being registered.* F23b applied it correctly to
`TOL_REL_WEDGE` (§4.3), to `PLATEAU_TOL` for `f·Re` (§5.4) and to `PLATEAU_TOL` for `E2n`
(§5.4). **The arm-acceptance threshold was the one threshold in the document derived from
nothing at all**, and it is the one that fired.

---

## 2. THE FALSIFICATION ATTEMPT — what was tried against §1 and what survived

This section exists because the finding above arrived from the supervisor and a premise
taken on report is not a premise checked. **Four attempts to break it; all four failed;
one produced a refinement that MAKES THE FINDING STRONGER and exposes a second defect.**

**(a) Is `Ubar` normalised so as to be identically 1 by construction?** **No.** The
acceptance reader is `grade_f23b.py:443 ubar_all_cells()` →
`float(np.sum(V * U[:, 0]) / np.sum(V))`, the **raw** volume-weighted axial velocity over
all cells against each rank's own `processor*/0/V`, and the acceptance quantity is
`abs(1.0 - ub)` at `:766`. **Gate G-F23b-1 IS normalised by the read bulk velocity** —
`e2_normalised()` divides `u` by `ubar_h` — and had the acceptance quantity been
normalised the same way the analysis would change. **It is not.** The two readers are
different functions on different lines.

**(b) Are §5.1's real readings consistent with a quantity that could reach 1e−10?**
**No.** `3.6251e−02` (coarse) and `4.2091e−01` (medium) at iteration 4,000 correspond to
`Ubar` = 0.963749067 and 0.579085973 — both still climbing from rest toward their
discrete answers (1.000122 and 1.000030). They are **iteration**-dominated there, and at
full iterative convergence they floor at 1.215525e−04 and 3.002806e−05. Neither limb
approaches 1e−10.

**(c) Could the discrete `Ubar` be 1 to 1e−10 on some mesh in the family?** **No.** The
model gives 1.947e−03 / 1.216e−04 / 3.003e−05 / 7.142e−06 across NR = 16…256, falling as
h². Reaching 1e−10 would need roughly NR ≈ 2×10⁵, i.e. ~10¹² cells.

**(d) THE ONE THAT ALMOST WORKED — the reader takes the MINIMUM over 40 checkpoints, and
`|1 − Ubar|` TRANSITS ZERO.** `case/0/U.template` sets `internalField` to `(0 0 0)`: the
flow starts **from rest**. `Ubar` therefore climbs 0 → 1.0019466 and **crosses 1 exactly
once**, so `|1 − Ubar|` passes through zero mid-transient. Taken **alone**, the clause is
therefore *not* literally unsatisfiable — a checkpoint landing on the crossing would
satisfy it by a sampling accident. **This does not rescue F23b; it convicts it twice
over:**

1. **The acceptance is a CONJUNCTION at ONE checkpoint** — `grade_f23b.py:766`:
   `ok = (err <= ARM_UBAR_TOL) and (ux is not None) and (ux <= ARM_UX_RES_TOL)`. At the
   crossing the solve is mid-transient and `Ux` is nowhere near 1e−12; at the checkpoint
   where `Ux ≤ 1e−12` the solve has settled on the discrete answer and
   `|1 − Ubar| = 1.9466e−03`. **The two clauses are mutually exclusive in time, so the
   conjunction is unsatisfiable on any finite mesh** — §1.2's conclusion, reached more
   sharply.
2. **The only way the clause could ever have passed alone was for the WRONG REASON** — a
   sampling coincidence at an unconverged state, which would have "born" the reader on an
   artifact that proves nothing. **A one-sided `≤ tol` test on a quantity that transits
   its target is not a convergence test.** §5.2 designs this out.

**And it explains the observation.** `9.692465e-04` is **smaller than the model's
converged 1.946614e−03**, which a monotone approach from rest could not produce. It is a
**mid-transient sample**, not a reading of the discretisation floor. **Consequence, stated
plainly: the lab does not know, and cannot now find out, what A0's converged `|1 − Ubar|`
was — §3 destroyed the checkpoint series.** §5.3's margin is registered without that
number, and is not permitted to be derived from it.

**VERDICT ON THE PREMISE: the supervisor's finding SURVIVES.** It is confirmed by
independent re-derivation from the frozen model, by reading the two readers as code, and
by the initial condition. **One thing the supervisor's statement should be tightened on:**
"unsatisfiable on any finite mesh" is exact for the **conjunction** and for any converged
checkpoint, but the `|1 − Ubar|` clause **read alone** transits zero and is satisfiable by
accident. That is a worse defect, not a lesser one.

---

## 3. THE SECOND DEFECT — `/tmp` FILING, WHICH DESTROYED THE DECIDING MEASUREMENT

`cases/F23b_HP_WEDGE/run_f23b.sh:87`:

    SCRATCH="${TMPDIR:-/tmp}/f23b_preladder_$$"

The entire pre-ladder — A0's `log.build`, `log.decomposePar`, `log.simpleFoam`, `RC.txt`,
`ARM_ALLOWANCE.txt` and all four `processor*/` trees — was written to
`/tmp/f23b_preladder_1644186` and **nothing was copied back**. The reboot later that day
wiped it. **Verified ABSENT in this invocation** by `find / -maxdepth 4 -name
'f23b_preladder*'` (0 hits) and by listing `/tmp`; the run root
`verification/runs/F23b_HP_WEDGE_runs/` holds **one file**, `RUN_STATUS.F23b_HP_WEDGE.txt`.

**Consequence, in the charter's own terms.** `VERIFICATION_CHARTER.md` §1: *"Done means a
gate has a verdict, the verdict cites an artifact, and the artifact is still on disk."*
**`9.692465e-04` now survives only as prose in a launcher stdout capture and is
UNCITABLE AS A RESULT.** It is quoted in §1.1 and §2(d) of this document as *what the
launcher reported*, never as a measurement. This is L-27's failure mode exactly — a real
number, reproducible, and indistinguishable from a fabrication because the run that
produced it wrote to a scratch tree that was thrown away.

**The real constraint that produced the defect, and F23b's correct half of the solution.**
`scripts/queue_runner.py:495` computes `status = cwd / f"STATUS.{case_id}"` and truncates
it unconditionally, so a launcher record named `STATUS.<case_id>` is destroyed by the
runner (F27's richer record was lost to exactly that collision). **F23b solved that
correctly** by naming its own record `RUN_STATUS.F23b_HP_WEDGE.txt`. **F23c keeps that
solution unchanged** — the fix below is about *where* the pre-ladder lives, not about
renaming the status file, and the two must not be confused.

---

## 4. WHAT IS CARRIED FORWARD FROM F23b UNCHANGED

**Everything that was sound, and it is most of the document.** No re-derivation is offered
for any of it and no change is registered to any of it:

- **§2's case**, byte-for-byte: `Re_D = 100`, `R = 0.5`, `ν = 0.01`, `G = 0.32`,
  `u_max = 2`, `f·Re = 64`, `L = 16 D`, `HALF_ANGLE_DEG = 0.04` and its N-AV9
  justification, every patch name and type, and the eight dictionaries kept byte-for-byte
  from F23.
- **§3's ladder**: coarse 64 × 2048, medium 128 × 4096, fine 256 × 8192; `dim = 2`;
  r = 2.000 exactly; 4 ranks; `simple n (1 4 1)`; **decomposition seed `none`**.
- **§4's `G-WEDGE`**, all three limbs, `TOL_REL_WEDGE` (1.215313e−05 / 3.003125e−06 /
  7.142188e−07), `TOL_CM`, `K_CM = 1.0`, `FLOOR_REL = 1e−08`, and **AMENDMENT 1 §A1.4's
  `blockMesh`-path gating control** with its `[2.9, 3.1]×` band and its receipt.
- **§5.3's solve** — `consistent yes` (SIMPLEC), α_U = 1.0, p 1.0, `endTime 400`,
  `writeInterval 10`, 40 checkpoints, Class C window 12 checkpoints = 120 iterations.
- **§5.4's `PLATEAU_TOL`** at every level on every graded quantity, and the L-396
  machine-floor variance clause printed rather than silent.
- **§6's gates, predictions and bands, byte-for-byte**: `G-F23b-1` → **`G-F23c-1`**,
  band `[2.376227e−06, 2.138605e−05]`; `G-F23b-2` → **`G-F23c-2`**, band
  `[63.998628773, 64.001371227]`; `BAND_FACTOR = 3.0`; predicted `f·Re`
  63.992221588 / 63.998078262 / 63.999542924; predicted `E2n`
  1.149980e−04 / 2.869164e−05 / 7.128682e−06; predicted triple **CONVERGING**; predicted
  verdict **PASS × 2**. **Only the gate NAMES change, to keep the two rungs' records
  distinguishable. No definition, no quantity, no band edge and no predicted value moves.**
- **§7's criteria in rule 5's order**, the strict completion rule (rule 4) with the age
  guard, the zero-`assert` census, the hard `-O` refusal, `set -u` dropped around the
  OpenFOAM bashrc source only (L-339), and the `--preflight` contract.
- **§8's controls C-1 … C-14 entire**, including **C-8, the planted-zero control on the
  field readers** (δ = 1.234e−03 on `Ux`, planted into copies of real processor `U` files,
  read back through the real parser, **refuse (exit 2) if the plant does not move the
  reading**) and C-7's must-fire plateau control on F23's retained run root.
- **§9.1's measured rates and §9.2's frozen `D_fine = 1.30` and `S = 2.0`** *for the
  ladder levels*, and the ladder's `ESTIMATE 202.366` / `CAP 293.0` / `CAP_RATIO 1.4479`.
  **§6 of this file changes the PRE-LADDER cost model only.**
- **§5.5's branch rule 1–5 entire**, including rule 4 (double failure → HALT, `BLOCKED`,
  new registration under a new sha, never a third arm) and rule 5 (**both arms reported,
  including a failing one** — Sanaa's anti-gaming clause,
  `docs/standards/NONCONVERGENCE_STANDARD.md`, 2026-08-27T16:54Z; *a smoke arm is an arm*).
- **AMENDMENT 1's principle entire** — the arm-acceptance reader is an instrument that
  decides an outcome, its ACCEPT side is **gating**, and a reader shown only able to
  reject is L-396's constant in its other costume. **F23c does not weaken A0. It repairs
  the threshold A0 was asked to reach.**
- **F23's run root stays retained and read-only** as C-7's must-fire artifact.

---

## 5. DEPARTURE 1 — THE ACCEPTANCE TEST, SEPARATED INTO ITS TWO QUANTITIES

**Registered as an explicit departure from F23b §5.5 and AMENDMENT 1 §A1.5. Reason: §1
and §2 above.**

### 5.1 CLAUSE (a) — THE ITERATIVE CLAUSE, KEPT UNCHANGED AT 1e−12

    Ux initial residual  <=  ARM_UX_RES_TOL = 1.0e-12       UNCHANGED FROM F23b

**Why it is kept and why 1e−12 is defensible.** It is a genuine **iterative** residual: on
a fixed mesh it decreases without bound under iteration and is limited only by machine
precision. F23 §7 measured **2.3e−16** on this exact 16 × 64 mesh under this exact
α_U = 0.7 dictionary, so the threshold sits **4,348× above a floor already demonstrated on
the configuration it is applied to**. **This is the one clause F23b's cited evidence
actually supported (§1.3), and it is carried over untouched.**

### 5.2 CLAUSE (b) — THE DISCRETISATION CLAUSE, RE-REGISTERED AS A TWO-SIDED BAND

**F23b's form** — `|1 − Ubar| ≤ 1e−10`, a one-sided iterative tolerance on a
discretisation quantity — **is withdrawn.** In its place:

    delta_pred(NR)   = | 1 - discrete(NR).ubar_h |        the frozen model's own output
    ARM_BAND_FACTOR  = 10.0                               FROZEN (new; see 5.3)

    ACCEPT clause (b)  <=>   delta_pred(NR) / ARM_BAND_FACTOR
                             <=  |1 - Ubar(n)|
                             <=  delta_pred(NR) x ARM_BAND_FACTOR

**Both clauses must hold at the SAME checkpoint `n`**, as F23b's reader already requires.

**Why a BAND and not a ceiling — this is the load-bearing design decision.** §2(d) showed
that a one-sided `≤ tol` test on a quantity that **transits** its target can be satisfied
mid-transient by a sampling accident, at a state that is not converged at all. **The lower
limb is what makes this a control rather than a coincidence detector**: it requires the
solve to have landed *on the mesh's own discrete answer*, not merely to have passed near
1 on its way there. It also satisfies `VERIFICATION_CHARTER.md` §2a's identity test —
`Ubar` comes from the solver and `delta_pred` from the model, so **a wrong treatment
fails**; the quantity is not derivable by construction from its own inputs.

*Honest note on redundancy:* clause (a) at 1e−12 already excludes the transient crossing
on its own, so the lower limb is defence in depth rather than the only thing standing
between the rung and a false birth. It is registered anyway, because two independent
exclusions of the same failure cost nothing and F23b's incident is what a single point of
failure looks like.

### 5.3 THE THRESHOLD DERIVATION, WITH ITS ARITHMETIC AND ITS MARGIN

**The derivation, in one line: the threshold is the level's OWN predicted discretisation
error, from the frozen model, with a stated coefficient margin — not an iterative
tolerance.** This is L-346's discipline, applied to the one threshold F23b left underived.

**Step 1 — `delta_pred` per mesh**, computed by `exact_f23b.discrete(nr)`, whose `ubar_h`
is the converged discrete bulk velocity of the wedge stencil. **This is the same frozen
function that produces §6's `f·Re` predictions; no new model is introduced.**

**Step 2 — the band**, at `ARM_BAND_FACTOR = 10.0`:

| where it is applied | mesh | NR | cells | **`delta_pred`** | **band low** | **band high** | × F23b's 1e−10 |
|---|---|---|---|---|---|---|---|
| **A0** (birth control) | 16 × 64 | 16 | 1,024 | **1.946614e−03** | **1.946614e−04** | **1.946614e−02** | 1.947e+07 |
| **ARM-P / ARM-F** | 64 × 2048 | 64 | 131,072 | **1.215525e−04** | **1.215525e−05** | **1.215525e−03** | 1.216e+06 |

*(Recorded, not gated — no arm runs at these meshes: medium 3.002806e−05, fine
7.141857e−06.)*

**Step 3 — WHY THE MARGIN IS A FACTOR OF 10, derived before compute and not from the
observation.**

The frozen model and OpenFOAM's actual finite-volume discretisation are consistent **at
the same order in h** but differ in the **coefficient** of the h² term, through at least
two identified routes: `wedge_geometry()` places the cell centre at the **polar** centroid
`rt = (2/3)(r_{j+1}³ − r_j³)/(r_{j+1}² − r_j²)` while OpenFOAM computes the actual
polyhedral centroid of a planar-chord trapezoid; and the wall condition is applied at the
face centre at distance `y_wall − yc[j]`. **A coefficient tolerance is therefore required,
and one decade is what is registered.** Three grounds:

1. **The arm acceptance is an instrument control, not a graded gate.** Its purpose is to
   birth a reader and to set one integer (`N_ITER`). **A control tighter than the gate
   downstream of it silently becomes the binding gate without ever being declared as
   one — which is precisely and exactly how F23b bricked itself** with a threshold
   1,215,525× tighter than its own registered prediction. `BAND_FACTOR = 3.0` stays where
   it belongs, on `G-F23c-1` and `G-F23c-2`, **untouched**; the arm sits deliberately
   looser than the physics gate it precedes.
2. **The gap being covered is a coefficient, not an order.** A factor of 10 admits a true
   discrete departure anywhere from 0.1× to 10× the model's — generous for two O(1)
   centroid effects and still four to seven orders tighter than "no check at all".
3. **It was not chosen to clear the observation, and cannot have been.** The only reading
   the lab holds is **9.692465e−04 at NR = 16, and §2(d) established that it is a
   MID-TRANSIENT SAMPLE, not a reading of the converged departure** — so it is not a
   measurement of the quantity this band brackets and could not calibrate it. For the
   record and for the supervisor's own check: **it falls inside the band at a factor of
   10 AND inside it at a factor of 3, so it does not discriminate between the two
   candidates and did not select either.** The narrowest band that would admit it is
   ×2.01, and **×2.01 is not registered** — that would be choosing a gate to fit an
   answer, which is what the freeze exists to prevent.

**THE HONEST GAP, REGISTERED RATHER THAN GLOSSED.** **Whether the true converged
`|1 − Ubar|` lies within a factor of 10 of the model is UNKNOWN AND UNMEASURED.** The one
artifact that could have settled it was A0's checkpoint series, and §3 destroyed it. **If
A0 refuses under this band, F23c is `BLOCKED` and the outcome is a NEW registration under
a NEW sha carrying the then-measured converged value — never a widened band under this
one.** That contingency is registered here, before compute, so that widening after the
fact is visibly out of order.

### 5.4 WHAT ELSE THE ARM RULES DO AND DO NOT DO

- **`ARM_N_ACCEPT = 80` and `ARM_N_MAX = 400` are UNCHANGED.** They are iteration counts
  routing between branch rules 1–3, not thresholds on a physical quantity.
- **A0 still runs under F23's α_U = 0.7 dictionary, deliberately**, for AMENDMENT 1
  §A1.5's own reason: the accept side must not depend on the very thing ARM-P tests, or
  it is a control defined in terms of the thing it controls. **Unchanged.**
- **A0's acceptance still has no `n ≤ 80` requirement** — it needs one accepting
  checkpoint anywhere in its 4,000 iterations. **Unchanged.**
- **The arms still decide ONE INTEGER** (`N_ITER`) and no gate, no band, no threshold, no
  tolerance, no label, no level, no rank count and no plateau tolerance. **§5.5's frozen
  branch rule, and the reasoning that makes running the arms under the sha legitimate,
  are carried over verbatim.**
- **`ARM_READING.json`** — the full per-checkpoint series (`time`, `ubar`,
  `abs_1_minus_ubar`, `ux_initial_residual`, `accepts`, and both band edges) is written
  under the run root for **every** arm, accepting or not, so the next reader of this rung
  has the numbers rather than a sentence about them.

---

## 6. DEPARTURE 2 — THE PRE-LADDER IS FILED UNDER THE RUN ROOT AND RETAINED

**Registered as an explicit departure from F23b `run_f23b.sh:87`. Reason: §3 above.**

### 6.1 THE REGISTERED LAYOUT

    verification/runs/F23c_HP_WEDGE_runs/
      RUN_STATUS.F23c_HP_WEDGE.txt          <- the launcher's own EXIT-TRAP record
      preladder/
        A0/            B4_coarse_unperturbed/   B5_coarse_perturbed/
        B6_fine_unperturbed/   B7_fine_perturbed/   ARM-P/   ARM-F/
      coarse/  medium/  fine/                 <- the ladder, unchanged

**Every pre-ladder directory retains, and the launcher deletes NOTHING under the run
root, ever:** `log.blockMesh`, `log.checkMesh`, `log.build`, `log.decomposePar`,
`log.simpleFoam`, `RC.txt`, `ARM_ALLOWANCE.txt`, `MESH_LINE.txt`, `ARM_READING.json`, the
`GWEDGE_CONTROL_RECEIPT` row, and every `processor*/` tree with all 40 checkpoints.

**`SCRATCH` and the `--scratch=` flag are REMOVED**, not merely re-defaulted. A default
that can be overridden back to `/tmp` by an argument is not a repair; there must be no
invocation of this launcher that puts a pre-ladder artifact outside the run root.

### 6.2 WHAT IS **NOT** CHANGED, AND MUST NOT BE

**The launcher's own record stays `RUN_STATUS.F23c_HP_WEDGE.txt`.** It may **NOT** be
named `STATUS.F23c_HP_WEDGE`, because `scripts/queue_runner.py:495` computes
`status = cwd / f"STATUS.{case_id}"` and truncates it unconditionally. **F23b got this
right and F23c keeps it byte-for-byte.** Registered explicitly so a future reader
tidying "two status files" does not reintroduce F27's loss.

### 6.3 DISK, MEASURED

Free space on `/` measured **216 GB** at 2026-08-31T15:08Z (`df -BG /`). Pre-ladder
retention adds, over F23b's plan: A0 ≈ 10 MB (1,024 cells × 40 checkpoints × 4 ranks);
ARM-P and ARM-F ≈ 859 MB each (F23's measured coarse figure for 40 checkpoints); the four
control meshes ≈ 3.4 GB (coarse ×2 small, fine ×2 at 2.1 M cells). **Pre-ladder ≈ 5.2 GB;
ladder ≈ 17.9 GB (F23b §9.4, measured); rung total ≈ 23.1 GB = 10.7 % of free space.**
Retention is affordable and is registered as unconditional. Run output is **not
committed**.

---

## 7. THE COST MODEL — REPAIRED, AND THE TWO BOOKKEEPING DEFECTS F23b MEASURED

**Both defects below are `INFRASTRUCTURE` under L-342 (`docs/LESSONS.md:14663`, Sanaa's
universal rule of 2026-08-26): they void a COST CLAIM and never a physics artifact.**
F23b's `BLOCKED` verdict is untouched by either.

### 7.1 DEFECT 1 — A0 OVERRAN ITS OWN LINE ITEM BY ×5.333

| | core-min | source |
|---|---|---|
| A0 **registered** (build 0.050 + solve 0.294) | **0.350** | F23b AMENDMENT 1 §A1.5 |
| A0 **actual charged solve** | **1.8666666666666667** | `RUN_STATUS.F23b_HP_WEDGE.txt` |
| **overrun** | **×5.333** | |

**Cause, named:** §A1.5 priced a **1,024-cell** solve at **§9.1's coarse rate**
(4.30298 core-µs/cell-iteration), which was measured on **131,072 cells**. At 1,024 cells
across 4 ranks each rank holds 256 cells and the per-iteration cost is dominated by
fixed overhead — MPI collectives, GAMG setup and coarse-grid solve, residual I/O — not by
cell work. **A per-cell-iteration rate measured on a 128× larger mesh is not
transferable downward, and §9.1's own warning about transferred rates was aimed the other
way.**

### 7.2 DEFECT 2 — THE LAUNCHER CHARGES ONLY THE `mpirun`

`RUN_STATUS.F23b_HP_WEDGE.txt` records `spent_preladder_core_min=1.8666666666666667`,
which is **28.0 wall s × 4 ranks ÷ 60** — the `mpirun` alone. The phase ran
**145 wall s** end to end (`00:23:32Z` → `00:25:57Z`), so **≈ 117 wall s at 1 rank
≈ 1.95 core-min of build, `decomposePar`, instrument selftests and freeze verification
sat OUTSIDE every running total and outside every cap.** *(Derived by subtraction from
two timestamps and one charged figure; the phase's internal breakdown is not separately
recorded and cannot now be recovered — §3.)*

### 7.3 THE REPAIRED PRE-LADDER MODEL — AFFINE, AND CALIBRATED ON TWO MEASURED POINTS

    WALL_MS_PER_ITER(cells) = A x cells + B
    SOLVE_CORE_MIN(cells, n_iter, ranks, S) = WALL_MS_PER_ITER(cells) x n_iter x ranks x S / 60000

    A = 1.030388780e-03 ms per cell-iteration (wall, 4 ranks)  = 4.12156 core-us/cell-iteration
    B = 5.944882 ms per iteration, fixed                       = 23.7795 core-ms/iteration

**Calibrated on the lab's own two measurements of this exact solver, dictionary family,
box and rank count:**

| point | cells | iterations | wall | ms/iteration | source |
|---|---|---|---|---|---|
| F23b A0 | 1,024 | 4,000 | 28.0 s | **7.0000** | `RUN_STATUS.F23b_HP_WEDGE.txt` (1.8666667 core-min ÷ 4 × 60) |
| F23 coarse | 131,072 | 4,000 | 564 s | **141.0000** | `verification/runs/F23_HP_WEDGE_runs/coarse/log.simpleFoam` `ClockTime` |

**The `B` term is the whole repair**: it is the per-iteration cost that does not scale with
cells, it is 85 % of A0's cost and 4.2 % of coarse's, and F23b's single-rate model could
not represent it at all.

**HELD-OUT CHECK, and it is reported against this model rather than hidden.** F23 medium
(524,288 cells, `ClockTime` 2,357 s = 157.133 core-min) is **not** a calibration point.
The model predicts **145.644 core-min — 7.3 % LOW**, because this box's per-cell rate is
not monotone in problem size (F17c §8.2's L3 finding, which F23b §9.2 already cites).
**Therefore the affine model is registered for the PRE-LADDER ONLY**, where every solve
sits at 1,024 or 131,072 cells — i.e. **at its two calibration points, interpolating and
never extrapolating.** **It is NOT used for the ladder**, where F23b's per-level measured
rates with `D_fine = 1.30` and `S = 2.0` stand unchanged.

**Two agreements worth stating, because they bound the blast radius of the repair.** The
new model returns **1.866667 core-min for A0** (against F23b's 0.294 for the solve — the
5.333× is closed) and **7.520 core-min for ARM-P at 400 iterations with `S = 2.0`**, which
is **F23b's registered ARM-P figure to the digit**. **The cost defect was confined to the
small-mesh item, and the repair leaves every large-mesh figure where it was.**

### 7.4 THE PRE-LADDER BUDGET — EVERY NON-SOLVE ITEM CHARGED

**Defect 2's repair: builds, `decomposePar`, selftests and freeze verification are line
items, and the cap is enforced against a running total that includes them.**

| id | item | ranks | basis | expected | **worst registered** |
|---|---|---|---|---|---|
| L0 | launcher startup: path resolution, four instrument selftests, freeze verification, `--preflight`, cap assertions | 1 | **MEASURED upper bound** — F23b's 117 wall s (§7.2), which also contained B0 | 2.500 | 2.500 |
| B0 | A0 mesh build + `decomposePar`, 1,024 cells | 1 | inside L0's measured 117 s; charged separately here | 0.500 | 0.500 |
| **A0** | **arm-acceptance reader birth control** — 16 × 64, 4,000 iterations, α_U = 0.7 | 4 | **MEASURED 1.866667** (§7.1) | **2.500** | **2.500** |
| B4 | §4.4 control build, coarse, UNPERTURBED | 1 | F23 measured coarse build 6 wall s + `postProcess` | 0.500 | 0.500 |
| B5 | §4.4 control build, coarse, PERTURBED | 1 | as B4 | 0.500 | 0.500 |
| B6 | §4.4 control build, **fine**, UNPERTURBED | 1 | F23 measured fine build 65 wall s + `postProcess` | 2.500 | 2.500 |
| B7 | §4.4 control build, **fine**, PERTURBED | 1 | as B6 | 2.500 | 2.500 |
| BP | ARM-P mesh build + `decomposePar`, coarse | 1 | as B4 plus `decomposePar` at 131 k cells | 0.750 | 0.750 |
| P | **ARM-P solve**, coarse, `S = 2.0` — expected: accepts at n ≤ 80; worst: runs 400 out | 4 | §7.3 model at a calibration point | 1.504 | **7.520** |
| F | **ARM-F solve**, coarse, α_U = 0.9 — expected: does not fire | 4 | as P | 0.000 | **7.520** |
| | **TOTAL** | | | **13.754** | **27.290** |

**PROPOSED PRE-LADDER CAP: 32.0 core-minutes** = **×1.173 the worst registered case** (the
ratio the 1.50 ceiling applies to) and **×2.327 the expected path** (because the fallback
arm is registered and expected not to fire). **Both ratios are stated; neither is the
other in disguise.**

**It sits BESIDE the ladder cap, not inside it**, for F23b §9.0's two reasons, unchanged:
folding a branch-dependent pre-ladder spend into the ladder cap would make the fine
level's `timeout` kill threshold a function of whether ARM-F fired, and
`COMPUTE_BUDGET_CHARTER.md` §6 keeps separately-named spend separately named.

    LADDER CAP      293.0    (F23b's, UNCHANGED — ESTIMATE 202.366, CAP_RATIO 1.4479)
    PRE-LADDER CAP   32.0    (was 20.0; raised because every non-solve item is now charged)
    TOTAL RUNG CAP  325.0    asserted as the sum of its two parts; NOT a third budget

**Wall allowances**, by F23b §9.3's frozen arithmetic
`ALLOW_S = floor((CAP − SPENT_so_far) × 60 / RANKS)`, against the **full** running total:

| item | spent before it | remaining pre-ladder cap | **wall allowance** | projected wall | headroom |
|---|---|---|---|---|---|
| A0 | 3.000 | 29.000 | **435 s** | 28.0 s | ×15.54 |
| ARM-P | 12.250 | 19.750 | **296 s** | 112.8 s | ×2.624 |
| ARM-F | 19.770 | 12.230 | **183 s** | 112.8 s | ×1.622 |

A kill leaves an arm that did not reach its acceptance, which branch rule 3 or 4 handles
exactly as a failure. **An overrun stops the run and does not get a new budget; no cap is
raised by any route.**

**Dollars — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, owner-stated
2026-08-21/22; **this box cannot read its own billing**, `COMPUTE_BUDGET_CHARTER.md` §5):
total expected **216.120 core-min = $0.1848**; total cap **325.0 core-min = $0.2779**.
Under the $25 pre-authorisation, and this paragraph is the per-item read a blanket does
not supply (rule 9).

**`cost_basis:`** *ladder rates MEASURED on this case's own meshes, `D_fine` and `S`
EXTRAPOLATED (F23b §9.2, unchanged); pre-ladder from an AFFINE model calibrated on two
MEASURED points and used only between them, held-out check 7.3 % low reported; A0
MEASURED; dollars derived, reported-by-owner, not measured.*

### 7.5 CALIBRATION AT COMPLETION (rule 12)

At completion the results record must carry the estimate-versus-actual comparison — gross
and cleaned stated separately, waste named separately and never absorbed into the ratio,
the ratio actual/predicted, the gap attributed to contention / waste / misprediction, and
a row in **`docs/COST_CALIBRATION.md`**. **`A` and `B` are reported separately**, since the
`B` term is this rung's new extrapolated structure and the point of §7.3 is to find out
whether it holds. **A completion report without this comparison is incomplete.**

**OWED AND NOT WRITTEN BY THIS LANE: F23b's own calibration row.** F23b's A0 is a
completed process (1.8666667 core-min charged, plus ≈1.95 uncharged) and rule 12 requires
its row. **This lane did not write it** — it belongs to F23b's record, not F23c's, and two
lanes filing one row is two records for one run. Flagged for the supervisor's dispatch.

---

## 8. RULE-2 ABSENCE CONDITION, CHECKED IN THIS INVOCATION

**0.000 core-minutes have been spent on this rung. No solver was started by this lane. No
`LAUNCHED` line exists for `F23c`.** The diagnostics of §1, §2 and §7 are read-only
Python over F23's and F23b's existing artifacts plus the frozen model, charged to
INFRASTRUCTURE and folded into no case ratio (`COMPUTE_BUDGET_CHARTER.md` §6).

Checked at **2026-08-31T15:08:06Z**:

| path | `test -e` |
|---|---|
| `verification/runs/F23c_HP_WEDGE_runs` | **ABSENT** |
| `verification/runs/F23c_runs` | **ABSENT** |
| `cases/F23c_HP_WEDGE` | **ABSENT** |
| `verification/campaign/F23c_HP_WEDGE_PREREGISTRATION.md` (before writing) | **ABSENT** |

**PLANTED CONTROLS ON THE READERS (rule 3 — a zero from a reader not shown able to see a
non-zero is not evidence).** In the same invocation and the same loop, `test -e` returned
**PRESENT** for `verification/runs/F23_HP_WEDGE_runs` and for `cases/F23b_HP_WEDGE`.
`find verification/runs -maxdepth 1 -name 'F23c*'` returned **0** while the same `find`
with `-name 'F23*'` returned **2**. `git ls-tree -r HEAD --name-only | grep -c F23c`
returned **0** while the same matcher on the same listing returned **19** for `F23b`.
Out-of-tree run roots by name: `/home/ubuntu/certonomous-runs` (557 entries) **0**,
`/home/ubuntu/closure-data` (29) **0**, `/home/ubuntu/closure-challenge-benchmark` (7)
**0**. **Every reader used above can return a non-zero, so its zeros are evidence.**

**Rung id derivation (rule 11 — from the TAIL, the MAXIMUM EXISTING SUFFIX, never a
count).** The F23 family's existing members are `F23` and `F23b`; the maximum existing
letter suffix on 23 is `b`, so the successor is **`F23c`**. This follows the lab's
successor convention (`F23` → `F23b`; `F26` → `F26D`) rather than taking a new F-number,
and `F23c` was verified free by the three independent listers above. **It is re-derived in
the same shell invocation as the commit.**

---

## 9. WHAT IS **NOT** REGISTERED HERE

- **F23b's record is untouched.** It stands **`BLOCKED`** on its own record. This file
  does not re-grade it, does not amend it, does not edit it, and reaches none of its
  frozen files. Its freeze commit `57d31dde` remains a byte-exact prefix of the file on
  disk.
- **F23's record is untouched.** It stands `NOT A RESULT`. Its run root is retained
  read-only as C-7's and A0's control artifact.
- **No case code exists and none was written by this lane.** §10's frozen-file table is a
  placeholder for the supervisor.
- **No queue entry.** Nothing was filed into `verification/queue/cfd/`.
- **No compute of any kind was launched.**
- **No claim that the true converged `|1 − Ubar|` lies inside §5.3's band.** It is a
  registered prediction that may fail, and if it fails the rung is `BLOCKED` (§5.3).
- **No amendment to any standard, charter, lesson or N-* entry**, and no lesson number
  claimed. Whether §1's defect class — *an iterative tolerance applied to a discretisation
  quantity* — earns an `L-*` or an `N-*` entry is the supervisor's call, not this lane's.
- **No `docs/COST_CALIBRATION.md` row** (§7.5).
- **No GPU arm and no `BLOCKED-GPU`.** CPU-only.
- **Nothing is sent, emailed, filed, uploaded, registered, posted or submitted** (rule 7).
  **SUBMISSIONS ARE PARKED.**

---

## 10. FROZEN FILES AT THE FREEZE — **TO BE COMPLETED BY THE SUPERVISOR**

    cases/F23c_HP_WEDGE/exact_f23c.py      <sha256>
    cases/F23c_HP_WEDGE/build_f23c.py      <sha256>     <- carries G-WEDGE (section 4 of F23b, carried forward)
    cases/F23c_HP_WEDGE/foam_io_f23c.py    <sha256>
    cases/F23c_HP_WEDGE/grade_f23c.py      <sha256>     <- carries section 5's acceptance band
    cases/F23c_HP_WEDGE/proj_f23c.py       <sha256>
    cases/F23c_HP_WEDGE/run_f23c.sh        <sha256>     <- carries section 6's filing repair; NO --scratch flag
    cases/F23c_HP_WEDGE/case/0/{p,U.template}
    cases/F23c_HP_WEDGE/case/constant/{transportProperties,turbulenceProperties,fvOptions}
    cases/F23c_HP_WEDGE/case/system/{blockMeshDict.template,controlDict,fvSchemes,fvSolution,decomposeParDict}
    verification/campaign/F23c_HP_WEDGE_PREREGISTRATION.md   (this file)

The grading path is fixed at the pre-registration commit and the frozen file that ran is
verified by hashing it against the committed blob (`scripts/check_comparator_freeze.py`).
**`grade_f23c.py` must CHECK `--prereg-commit` against this rung's freeze commit and
refuse any other, as `grade_f23b.py:272` does — not merely record it, which four of five
cfd graders do and which defeats rule 2 entirely.** The freeze verifier is a **PREFIX**
check, for F23b §A2.3's reason: rule 6 permits dated amendments appended at the foot.

---

## 11. QUESTIONS FOR THE SUPERVISOR — this lane does not decide these

**Q1. Is `ARM_BAND_FACTOR = 10.0` the right width?** §5.3 argues it from the principle
that a control must not be tighter than the gate downstream of it. The supervisor may
prefer `BAND_FACTOR = 3.0` for consistency with the graded gates; **the one number the
lab holds does not discriminate between them** (§5.3, ground 3). The risk of 3 is a second
`BLOCKED` on a coefficient gap; the risk of 10 is a control that is looser than it needed
to be. **This lane registered 10 and states the alternative rather than burying it.**

**Q2. Should A0 keep the two-sided band at all, or accept on clause (a) alone?** Clause
(a) at 1e−12 already excludes the transient crossing. Registering (b) as well makes A0 a
statement about the physics as well as the instrument — and makes it able to fail on the
physics. This lane judged two exclusions better than one; the supervisor may disagree.

**Q3. Does §1's defect class earn a lesson number?** *An iterative tolerance applied to a
discretisation quantity, in a document that applied L-346 correctly to three other
thresholds and missed the fourth.* This lane claims no number (rule 11).

**Q4. Does the `/tmp` pre-ladder defect reach other cfd launchers?** This lane checked
`run_f23b.sh` only and makes **no claim about any other case**. `SCRATCH="${TMPDIR:-/tmp}/…"`
is a shape that could recur; a sweep is the supervisor's to commission.

**Q5. F23b's calibration row** (§7.5) — whose dispatch?

---

| draft record | **v0.1, UNFROZEN** |
|---|---|
| status | **DRAFT — NOT FROZEN, NOT COMMISSIONED, NOT ENQUEUED** |
| verdict | **`PENDING`** |
| solver core-minutes spent by this draft | **0.000** |
| run root at the time of writing | **`verification/runs/F23c_HP_WEDGE_runs` ABSENT, planted control PRESENT on two paths** |
| gates carried forward unchanged from F23b | **`G-F23c-1`, `G-F23c-2`, `G-WEDGE` (3 limbs)** — definitions, quantities and bands byte-for-byte; names only changed |
| registered departures from F23b | **2** (§5 the acceptance test; §6 the pre-ladder filing) |
| thresholds re-derived | **1** (`\|1 − Ubar\|`, from the frozen model's own `ubar_h` with a stated ×10 coefficient margin) |
| thresholds kept unchanged | `Ux` 1e−12, `TOL_REL_WEDGE`, `TOL_CM`, `K_CM`, `FLOOR_REL`, `PLATEAU_TOL`, transverse 1e−10 × U_MAX, `BAND_FACTOR = 3.0`, `[2.9, 3.1]×`, `ARM_N_ACCEPT = 80`, `ARM_N_MAX = 400` |
| caps | ladder **293.0** (unchanged), pre-ladder **32.0** (was 20.0), total **325.0** |
| freeze | **RESERVED TO THE CFD SUPERVISOR. A lane may not freeze its own registration.** |
