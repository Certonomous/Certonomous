# VMFLGPU005 — RESULTS

**Case.** VMFLGPU005 — GPU solver path on **turbulent natural convection in a
tall differentially-heated cavity** (VM2026R1, **manual p. 235**, CPU parent
VMFL052). Reproduced in OpenFOAM v2606 `buoyantSimpleFoam` with the
**petsc4Foam** GPU linear-algebra path on a GPU instance, three-level r = 2
refinement ladder (6 720 / 26 880 / 107 520 cells), `RANKS = 1`, run **twice
per level** — a GPU arm and a forced-CPU control arm (six solves total),
endTime 15000 / 20000 / 25000 for L1 / L2 / L3.

**Verdict: `NOT A RESULT`.** The frozen comparator **GRADED** (exit code 0 — it
did not refuse; contrast VMFLGPU007, which refused at exit 2). The gate produced
readings at every level and then **rule 5 disqualified four of the seven gate
channels**. Per-limb: **B = PASS | C1 = NOT A RESULT | C2 = NOT A RESULT**.
Whole-row verdict is the weakest of the three limbs, per the row-#39 whole-row
precedent: **`NOT A RESULT`**.

**Tier: `NOT HELD`** for the physics. The **GPU path is VERIFIED** (limb B,
same-discrete-problem identity, PASS at 2.957e-10 against a 1e-4 band); the
**physics is NOT verified** (limbs C1 and C2 fell to rule 5). Per this family's
standing format ruling, **the register's PASS count does NOT move on limb B
alone** — a GPU==CPU identity PASS is not the physics-verification credential the
headline tracks.

This file is the artifact the ANSYS VALIDATION REGISTER row (#42) cites. The
comparator's own verbatim stdout is committed beside the run tree at
`verification/runs/ansys_verification/VMFLGPU005/GRADE_OUTPUT_2026-08-28.txt`
(24 lines; git blob `ec36c8e40e49707e12d889a540c3d8bb810d59e4`).

---

## 1. Freeze and identity — all verified in this lane by hashing, not on report

- **Freeze commit** `05555370f0736da40ec979790e7370925b030d61`, an **ancestor of
  HEAD** (verified: `git merge-base --is-ancestor` returns true).
- **Comparator** `grade_vmflgpu005.py`, blob
  `f80254fd712b1cda5a86908de2ad92f4cc85f062` — **IDENTICAL at the freeze commit,
  at HEAD, on the box's disk, and on the GPU instance where it ran**. The
  launcher's own `LAUNCH_RECORD.txt` records the same blob and
  `head = 05555370…`, so the freeze guard fired correctly at launch: the file
  that ran is the file that is frozen.
- **Pre-registration** `PREREGISTRATION.md`, blob
  `34a3570e063882d20a381da38d4f788d4cc99f27` (identical at freeze and HEAD).
- **Launcher** `run_vmflgpu005.sh`, blob
  `35f0fba3829026de6c90dfea5d9c6ab5f060a99d`.
- **Instrument health** (run in this lane after clearing `__pycache__`):
  `--selftest` **29/29 under `python3` AND 29/29 under `python3 -O`**, rc 0 both;
  **`ast.Assert` = 0** by an AST walk of the frozen source. A comparator that
  survives `-O` (which strips `assert`) is not resting its refusals on
  assertions.

---

## 2. Strict completion (CLAUDE.md rule 4) — HOLDS on all six solves

- `rc = 0` and `cap_fired = 0` on every `RUN_RC.*` (six arms).
- An `End` line in each of the six solver logs.
- Last `Time =` equals endTime on each: **15000 / 20000 / 25000** for L1 / L2 /
  L3, both the GPU arm and the forced-CPU arm.
- All six `postProcessing` trees complete with **exactly ONE time
  subdirectory each** — so the family's cardinality guard was **satisfied, not
  merely unexercised**.
- Exactly **one `log.*Foam` per solve directory**.

**Infrastructure, reported and never refusing (L-342):** the `ExecutionTime`
line count is **endTime + 2** on every arm (15002 / 20002 / 25002) because
petsc4Foam prints two init timing lines before the first solve. This is an
infrastructure channel, not a completion failure.

---

## 3. Controls — both live

- **Planted-zero (rule 3): "plant fired" at all three levels.** The reader was
  shown able to see a non-zero perturbation read back from disk; a reader that
  could not see it would have refused.
- **Blender control:** `tanh` confirmed on all **8 wall patches** — `omega` and
  `k` on `coldWall` / `hotWall` / `bottomWall` / `topWall`. The wall-function
  blending is the registered one.
- **y+max = 5.11 / 3.70 / 2.30** across L1 / L2 / L3 — boundary-layer-resolving
  as registered (the reproduction is kOmega + tanh wall functions on an r = 2
  boundary-layer-resolving triple).

---

## 4. The readings — exactly as the frozen comparator printed them

Grid triple: genuine **r = 2**, cells **6 720 / 26 880 / 107 520**.

Per-level gate quantities (GPU arm == forced-CPU arm at every level, to the
printed precision):

| Level | cells | Nu (gpu=cpu) | Vmax (gpu=cpu) | dTdx (gpu=cpu) | y+max |
|---|---|---|---|---|---|
| L1 | 6 720 | 4.7940 | 0.14881 | 52.532 | 5.11 |
| L2 | 26 880 | 4.8521 | 0.14604 | 53.536 | 3.70 |
| L3 | 107 520 | 4.8751 | 0.14465 | 55.565 | 2.30 |

### Limb A — GPU-execution tell
GPU execution **established at every level**; the forced-CPU control reported
**no GPU work at any level**. Clean both ways.

### Limb B — GPU == forced-CPU identity (SAME-DISCRETE-PROBLEM, PASS-capable)
Worst `|dq|/|q| = 2.957e-10` against band **1.0e-04**. **PASS** — a margin of
~338 000× (1e-4 / 2.957e-10 = 3.38e5). The GPU and CPU paths agree to about ten
significant figures. This is the case's only PASS credential, and a triple is
irrelevant to it: identical mesh, identical scheme, so discretisation error
cancels on both sides.

### Limb C1 — mid-height quantities vs Betts & Bokhari (continuum, ceiling GATE REACHED)
- **C1a Nu:** triple **CONVERGING** (p = 1.334, GCI = 0.388 %); value **4.87508**
  vs reference **5.85**, deviation **0.1667 ≤ band 0.20** — **INSIDE**.
- **C1b Vmax:** triple **CONVERGING** (p = 1.001, GCI = 1.2 %); value **0.144652**
  vs reference **0.139**, deviation **0.04066 ≤ band 0.20** — **INSIDE**.
- **C1c dTdx:** triple **DIVERGENT** (|e32| ≥ |e21|, **R = 2.022 ≥ 1** —
  refinement is NOT reducing the error). **Rule 5: `NOT A RESULT` whatever the
  value.**

Limb C1 = **`NOT A RESULT`**.

### Limb C2 — Y/h = 0.05 vertical-velocity / temperature profile vs archive CSV digitisation (continuum, ceiling GATE REACHED)
- **C2 Vup:** triple **OSCILLATORY** (opposite signs, **R = −1.512 < 0** — not
  monotone, no GCI). **Rule 5: `NOT A RESULT`.**
- **C2 Vdown:** triple **OSCILLATORY** (**R = −0.8783 < 0**). **Rule 5: `NOT A
  RESULT`.**
- **C2 Tcore:** triple **DIVERGENT** (**R = 6.416 ≥ 1**). **Rule 5: `NOT A
  RESULT`.**

Limb C2 = **`NOT A RESULT`**.

---

## 5. The point of this row — write it this way

**Two of the seven gate channels converged cleanly and landed INSIDE their
pre-registered bands** — Nu (16.67 % deviation inside a 20 % band with a 0.388 %
GCI) and Vmax (4.07 % inside 20 % with a 1.2 % GCI) — **and the row is still
`NOT A RESULT`**, because four other channels failed triple gating and rule 5
says the gate can only turn a PASS or GATE REACHED **INTO** `NOT A RESULT`, never
the reverse. **The tempting and forbidden move is to report the two good
channels as the result. It is not made here.**

The rule's one-way property held: a would-be reading of two clean bands is
overridden by four non-converged channels, and the lab therefore cannot show the
physics is a converged property of the discretisation.

---

## 6. Reported, never averaged

The comparator prints, and this record carries, that **C1b mid-height Vmax
0.14465** (paper Table 1 = **0.13900**) and **C2 Y/h = 0.05 peak-up 0.12788**
(archive CSV = **0.14783**) are at **DIFFERENT heights and of DIFFERENT
provenance**. The disagreement stands as recorded and is **not reconciled** — a
mid-height value and a Y/h = 0.05 profile value are not the same quantity and are
not averaged into one another.

---

## 7. Model — frozen on the archive selectors

Standard **k-omega (Wilcox) with low-Re correction, INTEGRATE-TO-WALL**, read
from `import_files/VMFL052_natural.cas`: `kw-std-on? #t`, `rng-ke-on? #f`,
`kw-low-re-mod? #t`. Reproduced as **OpenFOAM kOmega + tanh wall functions** on
an r = 2 boundary-layer-resolving triple. **Fluent's low-Re damping terms are
NOT claimed** — a declared modelling difference, and the reason limbs C1 and C2
carry a residual against experiment that a Roache triple cannot cure.

---

## 8. Reference provenance (rule 15 title-page verified)

**Betts & Bokhari 2000**, on the box and title-page verified under rule 15
(dT = 19.6 °C, Ra_W = 0.86e6, matching the manual's 307.85 − 288.25 K), plus the
**VMFL052 archive CSV digitisation** for the C2 profile. **Manual page 235.**

**Tier: value-vs-experiment, capped `GATE REACHED`** by `VERIFICATION_CHARTER.md`
§2f.3 — a Roache triple cures discretisation error but not the model-form error a
residual against an EXPERIMENT still carries. That ceiling is the reason C1 and
C2 could at most have been `GATE REACHED`, and rule 5 then took them below it.

---

## 9. NOT CLAIMED — carried verbatim in substance

- **Nothing about Ansys** — this box has no Fluent.
- **Nothing about GPU performance** — a GPU arm slower than the CPU arm passes
  every limb; no speedup is asserted.
- **No PASS on C2.**
- **No byte-identity with Fluent's low-Re k-omega.**

---

## 10. Cost — measured actuals, derived dollars (rule 12)

Measured from `COST.txt` and the six `RUN_RC.*` files (on the GPU instance / run
bundle; the committed repository evidence for the numbers below is the grade
output and this record):

- **total_wall_s = 15175** (the launcher's own figure, authoritative). The six
  solve wall_s sum to **15165**; the 10 s gap is meshing / bookkeeping outside
  the solves — stated, not hidden.
- **GPU arms** 403 / 1439 / 4218 s = **6 060 s = 1.6833 GPU-h**.
- **CPU arms** 210 / 1379 / 7516 s = **9 105 s = 151.75 core-min** at ranks = 1.
- **Instance occupancy 4.215278 GPU-h** — the card bills wall-clock regardless of
  which arm runs (15175 / 3600).

**Registered estimate** (`PREREGISTRATION.md:247`): *"GPU arm ~1–4 GPU-h across
the six solves (L3 dominant); forced-CPU arm ~60–200 core-min."*

**The estimate is AMBIGUOUS and is stated so rather than read in the flattering
direction.** It says "GPU arm" but "across the six solves" — the GPU arm is three
solves, not six. So it reads either way:

- **GPU-arm-only actual 1.6833 GPU-h**, ratio **0.673×** vs band midpoint 2.5 —
  INSIDE the 1–4 band.
- **Instance-occupancy actual 4.2153 GPU-h**, ratio **1.685×** — **ABOVE the
  band's top of 4.0 by 0.2153 GPU-h**.

**Ruling [lab-attributed]:** the **billing-relevant** figure is instance
occupancy (the card is billed wall-clock); the **physics-relevant** figure is the
GPU-arm total. **Both are reported.** The registration's wording is a
**REGISTRATION DEFECT** — a cost estimate must name its denominator (arm-time or
occupancy) — and the lesson for future registrations is that a GPU cost estimate
must state whether it covers solver time or instance occupancy.

- **CPU: 151.75 core-min** against the 60–200 band, ratio **1.167×** vs midpoint
  130 — INSIDE. The CPU side is a good prediction.

**Caps (registered, per-solve):**
- Registered **GPU cap 6.0 GPU-h PER SOLVE** — largest single GPU solve 4 218 s =
  1.1717 GPU-h = **19.53 %** of cap.
- Registered **CPU cap 240 core-min per arm** — largest single CPU arm 7 516 s =
  125.2667 core-min = **52.19 %** of cap.
- `cap_fired = 0` on all six arms. **Neither registered cap fired or was
  exceeded.**

**Dollars — DERIVED, NOT MEASURED** at the published-list **$0.8048/GPU-h** (the
box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5; the console
figure is owed and supersedes): case occupancy **$3.3925**, GPU arms only
**$1.3547**.

**Waste for the run: 0.000** — nothing was thrown away; all six solves completed
and were graded.

Calibration row: **`docs/COST_CALIBRATION.md` C-193**.

---

## 11. The cap question — disclosed beside the verdict, NEVER used to alter it. REFERRED to `verification-supervisor`.

A file `CAP_OVERRUN.txt` was written at **2026-08-28T03:07:44Z** reading *"CAP
OVERRUN REPORTED, NOT ENFORCED: case VMFLGPU005 … elapsed 14400"*, i.e. a
**launch-level 4-hour cap** that reported an overrun and **did not stop the run**,
where rule 12 says an overrun **stops** the run. Recorded precisely:

- **(a)** That cap is **NOT in the pre-registration.** The registered caps are
  per-solve (6.0 GPU-h/solve, 240 core-min/CPU-arm) and **neither was exceeded**,
  so **NO REGISTERED CAP WAS BREACHED and NOTHING IS VOIDED.**
- **(b)** The 14400 s figure **coincides numerically with the per-solve CPU cap**
  (240 × 60 ÷ 1 rank = 14400 s), very likely how the runner derived it — it
  applied a **per-solve** cap as a **whole-case** wall-clock budget, a scope
  error.
- **(c)** The real defect is a runner that **REPORTS rather than ENFORCES**,
  which on a case whose registered cap **was** exceeded would fail to stop a
  genuine runaway.
- **(d)** `CAP_OVERRUN.txt` was **ABSENT from the bundled run root**, so it lives
  on the instance outside it. **This lane has NOT read its full bytes — marked
  VERIFY, unread here** — and it is not paraphrased beyond the quoted fragment.

**This is REFERRED TO `verification-supervisor` for ruling and is not decided by
this team.**

---

## 12. What is verified and what is not — one line each

- **GPU numerical path:** VERIFIED (limb B, 2.957e-10 ≤ 1e-4).
- **Physics against experiment:** NOT verified (limbs C1 and C2 fell to rule 5).
- **Strict completion:** HELD on all six solves.
- **Controls:** both live (planted-zero fired ×3, blender tanh ×8).
- **Cap enforcement at launch level:** DEFECTIVE (reports, does not enforce) —
  referred, not ruled here.

---

## 13. Dated addendum, 2026-08-28 — the occupancy-ratio arithmetic, and a commit-message discrepancy

**Nothing above this section is edited; this addendum strikes nothing and moves no gate, threshold, cap or label (rule 6). A landed number is corrected by a dated addendum, never by a rewrite.**

**The arithmetic correction — the error is the supervisor's.** The instance-occupancy cost ratio is recorded in three places (this file at §10, the register's row #42, and the reasoning around calibration `C-193`) as **1.685×**. **The correct value is 1.686×.** It was computed as 1.685× from **15 165 s** — the sum of the six solve `wall_s` (see §10, lines around "The six solve wall_s sum to 15165") — while §10 simultaneously states that the authoritative total is `COST.txt`'s **15 175 s**, which includes ~10 s of meshing/bookkeeping outside the solves. `15175 / 3600 / 2.5 = 1.68611` → **1.686×**; `15165 / 3600 / 2.5 = 1.68500` → 1.685×. The two figures used **different denominators for the elapsed time**. The lane that wrote the records **flagged the discrepancy rather than silently correcting it** — the right call — and this addendum is the consequence.

**No finding moves.** The occupancy figure **4.215278 GPU-h is unchanged** and still exceeds the registered band top of 4.0 GPU-h by **0.2153 GPU-h**. The GPU-arm-only ratio **0.673×**, the CPU ratio **1.167×**, the cap percentages (**19.53 %** and **52.19 %**), the verdict **`NOT A RESULT`** and every gate number are **UNAFFECTED**.

**The transferable point.** Two figures for "the same" quantity differed in the third decimal place because they had **DIFFERENT DENOMINATORS** — solver time (15 165 s) versus instance occupancy (15 175 s) — and the registration never named which one it meant. **A cost ratio is meaningless until its denominator is named**, and this is the *second* consequence today of that same registration defect (the first being the arm-time-versus-occupancy ambiguity recorded in §10).

**Commit-message discrepancy.** Commit `c2aaa968`'s **subject line** says "calibration C-191", while the number that actually landed in all three records is **C-193** (peers took C-191 and C-192 mid-flight; the message file was written before the race resolved). **The records are correct at C-193**; only the immutable commit-message text is misdescriptive. Recorded so a future reader searching the log for C-193 is not misled.
