# COST BASIS — VMFLGPU family GPU spend

**DRAFT, `ansys-lane-opus48` for `ansys-verification-supervisor`, 2026-08-25. FIRST
ARROW: no compute incurred; this is the cost *basis* the runs will carry, not a measured
spend.**

## The governing rules (not relaxed here)

- **GPU spend is OUTSIDE the 2026-08-21 blanket** (`CLAUDE.md` rule 12; charter §8;
  `GPU_CAPABILITY_STATE.md` §6). That blanket was given when no GPU could launch; reading
  it onto GPU-hours is permission laundering (rule 9). **Every GPU run carries its own
  `cost_basis` in GPU-hours, priced from the console, never from recall.**
- Sanaa's cost directive (via the supervisor's brief, verbatim): *"I want the three teams
  to forget about cost constraints for now… So no team stops anything in the name of
  saving compute."* **This lifts constraints, not measurement.** Caps below are RUNAWAY
  GUARDS, not budget gates; costing and calibration continue. **This does NOT license idle
  GPU billing, which is waste, not compute** — the 7.88-GPU-h idle-waste row of record is
  exactly what must not recur.

## The rate — published price list, NOT console, NOT recall

| item | value | provenance |
|---|---|---|
| `g6.xlarge`, Linux, on-demand, us-east-2 | **$0.8048 / GPU-h** | AWS **published price list** feed, retrieved 2026-08-23 21:00:47Z by a closure lane; `GPU_CAPABILITY_STATE.md` §9; rateCode `JRTCKXETXF` |

**Provenance label, stated plainly:** this is the **published price-list rate, retrieved
2026-08-23** — it satisfies "never from recall" (it is an artifact with a URL, a JSON
path and a retrieval stamp), but **it is NOT a console reading.** The console figure is
**still owed** and is Sanaa's to read; a console figure supersedes this one if they differ
(`GPU_CAPABILITY_STATE.md` §9). Dollars derived from it are labelled **derived, not
measured** — this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).

**I did not invent a rate and I did not fabricate a console reading.** Where a console
number is genuinely unavailable to me, the honest states are (a) cite the on-record
published-list figure with its label, as above, or (b) mark a line **UNPRICED**. The
GPU-hour line uses (a); the EBS-snapshot line below uses (b).

## The cost lines the VMFLGPU family will carry

Each of the ten cases carries its **own** GPU-hour `cost_basis` in its (frozen)
pre-registration; the drafts in `DRAFT_PREREGISTRATIONS_VMFLGPU.md` carry a per-case
estimate. The **family-level** lines:

| line | basis | figure | note |
|---|---|---|---|
| **Build (one-time)** | GPU-h the instance is up while PETSc + petsc4Foam compile | **ESTIMATE, not measured**: the compile is CPU-bound but the GPU-hour meter runs the whole time the instance is up. Order **1–3 GPU-h** for a from-source PETSc-CUDA + petsc4Foam build. Priced at $0.8048/GPU-h ⇒ **~$0.80–$2.41 derived**. **The AMI snapshot makes this a ONE-TIME cost** (`AMI_SNAPSHOT_PROCEDURE.md`) | the single biggest idle-billing risk; the AMI removes it from every later boot |
| **Per case (10×)** | GPU-h per case = wall-hours the instance is up for that case | **ESTIMATE per case in each draft prereg** (trivial cases minutes; turbulent/radiation cases longer). Family total is small — all ten are the manual's *small/trivial* class | each case's own frozen cap is a runaway guard, not a budget gate |
| **Idle (target ZERO)** | GPU-h between smoke/case completion and shutdown | **MUST be ~0.** Driver self-shutdown (`GPU_CAPABILITY_STATE.md` §10) ends every driver with `sudo shutdown -h now` after the completion marker. Any idle GPU-h is **waste**, reported separately in `COST_CALIBRATION.md`, never absorbed | the 7.88-GPU-h row of record is the anti-pattern |
| **EBS snapshot storage (AMI)** | GB-month of the AMI's EBS snapshot while the instance is stopped | **UNPRICED** — I have no console EBS-snapshot GB-month rate on record and will not invent one. Small (~15–20 GB delta) but a standing charge; Sanaa reads the rate from the console | separate from GPU-hours; do not fold in |

## Calibration duty (rule 12, continues)

At **every** completion — the build, each of the ten cases — the actual GPU-hours (from
the instance's own up-time, reported-by-owner since this box cannot read billing) are
compared against the estimate above; the ratio actual/predicted, the gap attribution
(contention / waste / misprediction, waste named separately), and dollars derived at
$0.8048/GPU-h (labelled derived) land as a row in `docs/COST_CALIBRATION.md`. A completion
report without this row is incomplete.

## What is genuinely UNKNOWN on cost

1. **Console GPU-hour price** — still owed; the $0.8048 figure is published-list, not
   console.
2. **EBS-snapshot GB-month rate** — UNPRICED; not on record.
3. **Actual build GPU-hours** — an estimate until the build runs; the biggest single
   number and the one the AMI is designed to pay only once.
