# VR5 — THE SHARED-CWD STDOUT COLLISION DETECTOR

**Repair-registration.** Frozen before any work under it. Written 2026-08-30.

## 1. The finding this detects

`scripts/queue_runner.py` `launch()`. Line **:496** computes the status file as `STATUS.{case_id}` —
**keyed by case**. Line **:497** computes `out = cwd / "launcher.queue.out"` — a **FIXED BASENAME PER
CWD**, with no `case_id`, no pid and no timestamp. Line **:502** redirects the launched argv's stdout
into it with a **TRUNCATING** `>`. There is no rotation, no backup and no pre-move.

Two entries sharing a cwd therefore **destroy each other's verdict output, silently**. The STATUS file
survives and says nothing about it, because STATUS is keyed on the case and stdout is keyed on the
directory. The lab's own record of what an instrument printed is the casualty.

Measured by verification, 2026-08-30, before this document: **11 cwds launched into more than once, 34
launches into them, 23 stdout records already destroyed** — dafoam 13, heat-transfer 5, verification 3,
ansys-verification 1, closure 1 — **16 of the 23 CROSS-CASE**. Largest group
`/home/ubuntu/Certonomous/cases/dafoam/curriculum_D12R2`.

## 2. WHAT IS MINE

`scripts/queue_runner.py` is **not this team's file** and a patch there is the chief's to route.
**VR5 IS A DETECTOR, NOT A RUNNER PATCH** and makes no edit to the runner. What is verification's is the
same thing VR2 established: **an unmeasured hazard is not a resting state, it is an unmonitored one.**

### 2a. Rule-2 condition, and how it was checked

No compute has been spent under this document. The condition is that the queue run this item registers
**has not happened**: the run directory artefacts it will create — `STATUS.VR5_SHARED_CWD_COLLISION` and
`launcher.queue.out` under the registered cwd
`/home/ubuntu/Certonomous/verification/monitor/` — **do not exist**, checked by direct `ls` of that
directory on 2026-08-30 before this file was written. Amendments before the first queue launch are
legal and carry this same statement; after it, gates are closed.

### 2b. Disclosed: the driver was DRIVEN before enqueue

Honestly stated rather than presented as first contact. `verification/monitor/vr5_shared_cwd_stdout_collision.py`
was **driven before enqueue and its controls behaved** (five limbs, §3 G3/G4 below), and the numbers in
§1 are that drive's. An entry naming a script that has never run is the L-344 class and is not enqueued
here. The queue run produces the RECORDED artefact under the registered cwd; it is not the first
execution and this document does not pretend it is.

### 2c. The corpus is LIVE and the counts move

The queue corpus and `LAUNCH_LOG.tsv` are written by a running daemon and by five other teams. Between
two reads eight minutes apart on 2026-08-30 the record count moved 211 → 210 and the log moved 127 → 133
rows. **The gate below is therefore on the SIGN, not on any particular count**: it asks whether any
realised destroy exists, and every count is printed beside the verdict so a later reader can see which
corpus produced it.

## 3. Gate (frozen)

A committed detector under `verification/monitor/` that:

- **G1 — MECHANISM, verified not assumed.** It reads `scripts/queue_runner.py` **source** and classifies
  the stdout path construction `PRESENT` / `REPAIRED` / `NOT LOCATED`, locating the assignment and the
  redirect by shape rather than by a remembered line number. `PRESENT` requires both that the basename
  carries no `case_id`, pid or timestamp **and** that the redirect truncates. **If a future runner fixes
  this, VR5 says so and is retired rather than continuing to report a stale hazard.**
- **G2 — REALISED, from the LAUNCH LOG.** Per team, every cwd launched into more than once, the number
  of stdout records destroyed (`launches − 1` per cwd), how many of those are **cross-case**, the
  owning team of each **lost** stdout, and the largest group named.
- **G3 — EXPOSURE, from the CURRENT CORPUS.** Every cwd carrying more than one current queue record,
  split into groups whose destroy has already happened and **LATENT** groups whose destroy is still
  ahead, with per-team entry counts and the largest group named.
- **G4 — CONTROLS, plural, and every corpus limb planted ON DISK and read back through the detector's
  own real corpus reader** (`VERIFICATION_CHARTER` §2j; §2j.2 — *ask who wrote the bytes the control
  reads*). A control that supplies its own trigger downstream of the reader tests the reducer and not
  the reader, and is **refused** here:
  - **C1 (+)** a planted pair sharing a cwd, both launched → must be found REALISED, 1 destroyed,
    1 cross-case.
  - **C2 (−)** a planted pair with **DISTINCT** cwds → must stay **SILENT on both populations**.
  - **C3 (+)** a planted pair sharing a cwd with **one** launch → must be **LATENT**, explicitly **not**
    REALISED.
  - **C5 (+)** two planted launches into a cwd with **zero surviving queue records** → must **still** be
    REALISED. A destroy is a property of the log; it is not undone by the later disappearance of the
    record that caused it.
  - **C4** the mechanism reader must return **REPAIRED** on a keyed-basename source, **REPAIRED** on an
    appending source and **NOT LOCATED** on a source with neither shape — three answers, not one.

## 4. Threshold / label

- **PASS** = controls behave **and** zero REALISED destroys on the launch log; **or** the mechanism reads
  `REPAIRED`, in which case the historic destroys are history, the hazard is retired and this item is
  struck from the queue.
- **GATE FAIL** = mechanism `PRESENT` and **at least one** REALISED destroy. This is a **FINDING ABOUT
  `scripts/queue_runner.py`**, not a failure of this item.
- **NOT A RESULT** = any control limb misbehaves, **or** the mechanism reads `NOT LOCATED` — the
  detector cannot verify its own premise and refuses rather than report a hazard it can no longer see.

**EXPOSURE and LATENT are REPORTED, NEVER GATED**, so a latent group cannot quietly become a gate.

## 5. Cap and cost

- **Cap: 0.5 core-minutes.** An overrun **stops the run**; it does not get a new budget.
- **Estimate: 0.005 core-minutes.** Set from **measurement, not from a floor placeholder**, and from the
  **BUSY-BOX** measurement rather than the flattering one. Driven twice on 2026-08-30: **0.055 s wall =
  0.000912 core-minutes** on a quiet box and **0.099 s wall = 0.001644 core-minutes** with the box at
  ~80% busy under closure's `M1_*` sweep. The estimate is set above the busy figure.
  *(Pre-freeze amendment, legal under standing rule 2: stated while no compute has been spent under
  this document — the condition of §2a holds unchanged, the run directory artefacts still do not
  exist. The first registered estimate was 0.002, taken from the quiet drive alone.)*
  Verification's rule-12 calibration of
  2026-08-30 found VR1–VR4 estimated 0.5 core-min each against actuals of 0.00043 / 0.00176 / 0.00855 /
  0.00047, ratio **0.0056** — a zero-solver instrument item belongs two to three orders below this
  ladder's habitual floor, and this estimate is set there deliberately.
- **Zero solver compute.** Interpreter time only; the item reads files and starts no solver.
- `cost_basis`: c7a.4xlarge at $0.0513/core-h, **REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read
  its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

## 6. The cwd, chosen against this item's own finding

Registered cwd: **`/home/ubuntu/Certonomous/verification/monitor`**. It is **not the repository root**,
and it is **not VR6's cwd**. The root is precisely the mistake that cost this team VR1, VR2 and VR3
their stdout — three cross-case destroys at `/home/ubuntu/Certonomous`, listed by name in the §1 drive.
No other current queue record registers this cwd (checked in the same drive: it appears in no exposure
group). Eating our own dogfood is part of the item.

## 7. Not claimed

- **No repair is made.** `scripts/queue_runner.py` is untouched by this item and by its driver.
- **No verdict of any other team is withdrawn.** A destroyed stdout record is lost *reporting*, and
  whether a given run's own artefacts still support its verdict is that team's question, not this one's.
- **The 23 destroyed records are not recoverable by this item** and it does not claim to recover them.
