# DMR R3 L2 COURANT PROBE — RESULTS

> **Companion to the frozen pre-registration**
> `verification/campaign/DMR_R3_L2_COURANT_PROBE_PREREGISTRATION.md`
> (freeze commit `17958e0d`; DRAFT `e53f96ee`). The prereg body is frozen and is
> **not edited** by this record (rule 6). This RESULTS file records the measured
> probe outcome, the corrected mechanism narrative, and a dated correction note.
> Authored by a cfd `lab-lane`, 2026-09-07, from the cfd supervisor's first-hand
> triage. The probe outcome and mechanism attribution were **decided by the
> supervisor**; this lane recorded them after verifying each cited number at
> source. Rules 2, 3, 4, 5, 6, 10, 12, 13, 16 apply.
>
> **This was a ROBUSTNESS PROBE, NOT a Roache triple.** One level only (N=240),
> no grid triple, no GCI, no Gate T'. The verdict vocabulary below is applied only
> where a gate applies; the probe's own reach is a binary reach/crash and is
> stated as such.

---

## 0. Falsifiable proposition and its answer

**Proposition tested:** halving the Courant number (maxCo `0.1` → `0.05`) on the
finest DMR level (N=240) cures the positivity collapse and lets `rhoCentralFoam`
reach `endTime` `t = 0.2`.

**ANSWER — FALSIFIED (measured negative result).** maxCo `0.05` does **not** cure
the collapse: `rhoCentralFoam` SIGFPE'd (rc=136) at `Time = 0.15006001` and did
**not** reach `endTime` `0.2`. Same `Foam::sqrt` mechanism (post-update sound-speed
`sqrt` of a negative argument at the cell centre).

This is a robustness-probe outcome. There is **no Roache verdict** to state — no
convergence triple, no GCI. Diagnosed answer-blind by the check-1'd reader
(`step0_negativity_reader.py`), per L-501 a MEASURED negative result, never a
capability inference from one crash.

---

## 1. Measured outcome — verified at source

All figures below were read directly from the run directory
`verification/runs/DMR_R3_L2_COURANT_PROBE_runs/` and cross-checked by this lane
before recording; no discrepancy found.

| Quantity | Value | Source artifact |
|---|---|---|
| Solver return code | `136` (SIGFPE, 128+8) | `L2/RC_rhoCentralFoam.txt`, `probe.rc.txt` |
| Last solver `Time` | `0.15006001` | `L2/log.rhoCentralFoam` line 310314 |
| Crash signature | `Foam::sqrt(Field&, UList const&)` → Signal 8 (FPE), rank 1 | `L2/log.rhoCentralFoam` lines 310340–310368 |
| `endTime` target | `0.2` | prereg / case `controlDict` |
| reached_endTime | **no** | `PROGRESS.txt` |
| maxCo (this probe / L2) | `0.05` | generator `make_case_tadmor_co05.py` (pinned in freeze) |

### Cost (rule 12) — authoritative from wall × ranks

- `probe.coresec.txt` reads **`0`** — this is the **same command-substitution
  subshell bookkeeping artifact** seen at STEP-0 (the aggregate roll-up captured 0
  while the per-step line captured the real spend). It is **not** the cost.
- **Authoritative cost** from `PROGRESS.txt`: `rhoCentralFoam` wall `863 s` ×
  `4` ranks = `3452 core-s` = **57.5 core-min**; with pre-steps (blockMesh,
  checkMesh, setExprFields, decomposePar) total ≈ **57.98 core-min**.
- Cap was **90 core-min**. **NO cap breach** — the crash-truncated run spent well
  under the cap. cost_basis: core-minutes derived from logged wall × ranks
  (measured); no dollar figure claimed (the box cannot read its own billing —
  rule 12 / COMPUTE_BUDGET_CHARTER §5).

---

## 2. KEY MEASURED FINDING — the collapse is NOT dt-driven

Halving the Courant number left the crash time **unmoved**:

| Run | Flux / lever | maxCo | Crash `Time` | Source |
|---|---|---|---|---|
| L1 (Tadmor successor, R3t, N=240) | Tadmor flux | `0.1` | `0.15005683` | `verification/runs/DMR_R3_TADMOR_SUCCESSOR_runs/R3t/log.rhoCentralFoam` |
| L2 (this probe, N=240) | Tadmor flux | **`0.05`** | `0.15006001` | `verification/runs/DMR_R3_L2_COURANT_PROBE_runs/L2/log.rhoCentralFoam` |

The two crash times are **identical to dt granularity** (they differ only in the
5th–6th decimal, i.e. by less than one Tadmor timestep). Halving dt made **zero
difference** to when the collapse occurred.

**Conclusion:** the collapse is **NOT temporal / dt-driven; it is spatial /
resolution-driven.** The **L2 / Courant lever is MEASURED-EXHAUSTED** — the
Courant number is not the axis that helps.

**Contrast (the axis that DOES help):** spatial flux diffusion moved the crash
forward — Minmod `t = 0.116` → Tadmor `t = 0.150`. Spatial diffusion is the
helping axis; temporal refinement is not.

---

## 3. CORRECTED mechanism — T-positivity failure at the wall foot

**Per-field minima at the crash step `t = 0.15006001`** (reader JSON
`L2/l2_negativity_result.json`, `per_field_min`):

| Field | min at crash step | location | note |
|---|---|---|---|
| **T** | **`-0.00589395637`** | `(0.147916667, 0.00208333333, 0.005)` | the reflecting-wall foot; T's FIRST negative |
| e | `-745.385525` | same cell | reference-negative (see below) |
| p | `-0.0410179801` | same cell | |
| rho | `1.40000504` (positive) | `(1.08541667, …)` at `t = 1.2e-6` | never goes negative |

**Temperature T goes negative for the FIRST time exactly at the crash step**
(`t = 0.15006001`), at the reflecting-wall foot `(0.147917, 0.00208333, 0.005)`;
T is positive at every earlier step. This is the physical positivity failure that
drives the `sqrt` of a negative sound-speed argument.

**Internal energy `e` is a red herring.** `e` was **already ≈ `-743.589283` at the
very first step (`t = 1.199976e-06`)** — "elsewhere in the domain", not at the
wall — and only drifts to `-745.4` by the crash. `e` is negative **by thermo
reference convention** (an offset baseline), essentially constant, **NOT a
collapse.**

**The STEP-0 "immediate cell-centre energy positivity collapse via e" read is
CORRECTED** (see §4): the true mechanism is a **T-positivity failure at
`t = 0.150` at the wall foot**, not an immediate `e`-collapse at the first step.

---

## 4. CORRECTION NOTE — dated 2026-09-07

### 4(a) e-attribution correction (STEP-0 / DMR-L1)

The earlier STEP-0 / DMR-L1 mechanism narrative attributed the positivity failure
to internal energy `e` ("energy positivity collapse via e", read as immediate at
the first cell-centre step). That attribution was **misled by `e`'s
thermo-reference negativity**: `e` sits below zero from `t ≈ 1.2e-6` by baseline
convention and is essentially constant, so an `e`-keyed reader flags a "first
negative" at the first step that has nothing to do with the physical collapse.

**Corrected:** the physical positivity failure is in **temperature T**, which
first goes negative at `t = 0.15006001` at the reflecting-wall foot, coincident
with the crash. Recorded from the supervisor's first-hand per-field read of the
reader JSON.

### 4(b) DIAGNOSTIC READER DEFECT — `step0_negativity_reader.py`

**Defect:** `step0_negativity_reader.py`
(`verification/runs/DMR_runs/step0_negativity_reader.py`) defines
`PHYS_SCALARS = ("T", "e", "p", "rho")` (line 64) and `first_negative()` returns
the earliest-in-time negative across **all** of `PHYS_SCALARS`, including `e`.
Because `e` is **reference-relative** (negative by baseline convention from the
first step), the reader emits a **false-early `first_negative` on `e`** — its own
`verdict` string reads *"FIRST NEGATIVE: field e min=-7.43…e+02 at t=1.19998e-06
… elsewhere in the domain"* — which **masks the physically meaningful T signal**
at the wall foot.

**Required fix (flagged, not yet applied):** the reader must key positivity on
**T (and rho)**, not on `e`. `e`'s reference-relative minimum may be reported as
diagnostic context but must **not** drive `first_negative` / the mechanism
attribution.

**Gate on reuse:** this fix, and a supervisor **check-1** on the corrected reader,
are **REQUIRED BEFORE the L4 rung reuses this reader**. L4 must not inherit the
`e`-keyed defect.

### 4(c) The STEP-0 / DMR-L1 VERDICTS STILL STAND

The reader defect changed the **mechanism narrative**, not the verdicts. The
supervisor read per-field **T** directly (answer-blind) for the STEP-0 / DMR-L1
outcomes; those remain **`NOT A RESULT`** (crash-truncated, `endTime` not reached),
unchanged. The correction affects only *why* the collapse occurs (T, not e), not
*whether* the runs produced a result.

---

## 5. Ladder status and next lever

- **Courant / dt axis: MEASURED-EXHAUSTED** (§2). Do not spend further compute on
  Courant refinement for this collapse.
- **Spatial-diffusion axis: HELPS** (Minmod → Tadmor delayed the crash). This is
  the productive axis.
- **Next cheap in-solver lever — L4: first-order T reconstruction** at the
  reflecting wall / wall foot. **On the chief's desk** for authorisation (a new
  in-solver lever is not this lane's or this record's call).
- **L5: bounded-T** (limiter / clip on T) **if L4 fails.** Contingent, not yet
  authorised.
- Both L4 and L5 must reuse a **fixed** `step0_negativity_reader.py` per §4(b) —
  fix + supervisor check-1 first.

---

## 6. Calibration (rule 12) — OWED but BLOCKED

The estimate-versus-actual calibration row for this probe (predicted cap 90
core-min; actual ≈ **57.98 core-min**; ratio actual/predicted ≈ **0.64**;
crash-truncated, so the under-spend is attributable to early termination, not
misprediction of a completed run) is **OWED** to `docs/COST_CALIBRATION.md`.

It is **BLOCKED and NOT FILED here.** Calibration-ledger filing is BLOCKED
lab-wide (`append_record.py` poison row, routed to verification). This lane did
**not** run `append_record.py` and did **not** edit `docs/COST_CALIBRATION.md`.
The row is recorded here as **owed-but-blocked**; it lands once the ledger is
unblocked, under that file's append rules and the rule-10 private-index protocol.
Board 78 is held for the calibration unblock and was not touched.

---

## 7. Verdict summary

- **Probe proposition:** FALSIFIED — maxCo `0.05` does not cure the collapse
  (SIGFPE `t = 0.150`, `endTime` `0.2` not reached). Robustness-probe outcome, not
  a Roache triple.
- **dt as the driver:** REJECTED (measured — identical crash time vs L1).
- **Mechanism:** T-positivity failure at the wall foot at `t = 0.150` (`e`
  reference-negativity is a red herring).
- **STEP-0 / DMR-L1 verdicts:** `NOT A RESULT` — **STAND** (unchanged by the
  mechanism correction).
- **Reader defect:** flagged for fix + supervisor check-1 before L4 reuse.
- **Calibration:** OWED, BLOCKED (poison row) — not filed.
