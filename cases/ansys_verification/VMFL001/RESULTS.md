# VMFL001 — Flow Between Rotating and Stationary Concentric Cylinders: RESULTS, run 1

**NOT FILED ANYWHERE. Nothing in this document is sent, emailed, uploaded, filed,
posted, registered or commented outside this box, now or ever** (CLAUDE.md rules 7
and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The manual is proprietary Ansys
documentation. **SUBMISSIONS PARKED.**

**This file does not revise `PREREGISTRATION.md` and cannot.** The gate, the
tolerance, the cap, the labels and the grading path were frozen before compute and
are unchanged; nothing here edits a line above Amendment 1 of that file (CLAUDE.md
rules 2 and 6).

**Written 2026-08-24T17:54:24Z (`date -u`) by `ansys-lane-opus`, on the
`ansys-verification-supervisor`'s verdict after its own personal triage of the logs**
(`SUPERVISION_CHARTER.md` §3 check 2: a crash or a refusal is a finding until triage
says otherwise).

---

## 1. VERDICT

# `NOT A RESULT`

**Run 1 of VMFL001 produced no lab value.** Three levels completed cleanly and
inside budget, and then the rung failed on **two independent grounds**, either of
which alone is sufficient:

1. **The frozen comparator REFUSED (exit 2)** — it could not find the sampled file
   it was frozen to read, and it refuses rather than guessing a column.
2. **The finest level L3 fails the registered iterative-convergence clause**
   (`PREREGISTRATION.md` §7), which under CLAUDE.md rule 5 step 1 and
   `PREREGISTRATION.md` §4 makes the rung `NOT A RESULT` **before the Roache triple
   is even classified** — so a repaired parser would not have rescued this run.

**There is no lab value, no planted-zero firing, and no grid triple.** The gate was
never reached, so it is neither met nor failed: `GATE FAIL` would be the wrong word
and is not used. The verdict is from the fixed vocabulary (CLAUDE.md rule 1;
`PREREGISTRATION.md` §11).

**This is a statement about this lab's run of this case. It is not a statement about
Ansys** (`ANSYS_VERIFICATION_CHARTER.md` §2). This box has no Fluent and no CFX;
`rot_conc_cyl.cas` and `rotating_cylinder.def` were not run, and no VM2026R1 archive
was opened.

---

## 2. What ran, and what the artifacts prove

`run_vmfl001.sh` (frozen blob `f2b09aa2`, Amendment 1 applied **before any compute**,
commit `a9e73c5d`) built and ran all three levels serially at
`HEAD = cffd90e7`, finishing 2026-08-24T17:47:22Z.

| level | cells (`log.checkMesh`) | registered cells | rc | wall s | core-min |
|---|---|---|---|---|---|
| `L1_16x64` | **1024** | 16 × 64 = 1024 ✅ | 0 | 2 | 0.0333 |
| `L2_32x128` | **4096** | 32 × 128 = 4096 ✅ | 0 | 13 | 0.2167 |
| `L3_64x256` | **16384** | 64 × 256 = 16384 ✅ | 0 | 104 | 1.7333 |
| **total** | 21,504 | | | **119** | **1.9833** |

### 2.1 Strict completion rule (CLAUDE.md rule 4, as adapted in `PREREGISTRATION.md` §7)

All six clauses hold at **all three** levels — checked from the committed artifacts,
not inferred:

| clause | L1 | L2 | L3 |
|---|---|---|---|
| 1. `rc = 0` (`RUN_RC.txt`) | ✅ | ✅ | ✅ |
| 2. `End` line in `log.simpleFoam` (count) | ✅ 1 | ✅ 1 | ✅ 1 |
| 3. last time == `endTime` == 3000 | ✅ | ✅ | ✅ |
| 4. `U` and `p` present at `endTime` | ✅ | ✅ | ✅ |
| 5. `ExecutionTime` line count == 3000 | ✅ 3000 | ✅ 3000 | ✅ 3000 |
| 6. age guard: `3000/{U,p}` newer than the case's own `0/U` | ✅ +2 s | ✅ +13 s | ✅ +104 s |

`fvSolution` carries no `residualControl`, so SIMPLE could not stop early — clause 3
is meaningful rather than tautological, exactly as §7 registered. No
`CAP_EXCEEDED.txt` exists; the 10 core-minute cap was never approached.

**Completion is not convergence.** The run is complete and the rung is still
`NOT A RESULT` — §3 and §4 are why.

---

## 3. Failure mechanism 1 — the comparator REFUSED on the v2606 sampled-file naming

The frozen comparator `grade_vmfl001.py` (blob **`8cb29610`**, re-hashed at analysis
time against `PREREGISTRATION.md` §9 and **matching**) printed, as its first line:

> `REFUSE: no sampled file for set 'gateAxis', field 'U' at time 3000 under
> /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL001/L1_16x64/postProcessing`

and exited **2**. It refused on the **coarsest** level, so it never reached L2, L3,
the planted-zero control, the triple or the gate.

**The mechanism, exactly.** The comparator was frozen expecting the sampled output at
`postProcessing/<fo>/<time>/U_gateAxis.*` — **field first, set second** — and
expecting a `#` comment header naming the columns. OpenFOAM **v2606**'s `sets`
function object with `setFormat raw` actually writes

    postProcessing/radialProbes/3000/gateAxis_p_U.xy

— **set name first, then the fields in alphabetical order** (`p` before `U`), joined
by underscores — and it emits **no `#` header at all**. Columns are `x y z` then the
fields in that same order: `p` (1 column), then `U` (3 columns).

**The refusal is the comparator working as frozen, not a comparator bug.**
`PREREGISTRATION.md` §9 stated in advance: *"If the comparator cannot parse the real
output, it refuses and the rung is `NOT A RESULT` — it never guesses a column."* It
did precisely that. A comparator that had shrugged and taken "the last column that
looks like a velocity" would have produced a number here, and that number would have
been worth nothing.

**What made this survivable-in-principle and fatal-in-fact.** The comparator's
`--selftest` passed **18/18 checks at its own commit**, including a positive read of
a synthetic raw file and a **refusal** on a headerless one. But the synthetic fixture
was written by the comparator's author to the comparator's own belief about v2606 —
wrong filename convention, and a header v2606 does not emit. **A selftest built on
its own fixture verifies the reader's belief about the writer, never the writer.**
That is the lesson filed as `L-286`, and the cheapest possible repair — running the
reader once against a 2-second coarse level before the freeze — is named there.

---

## 4. Failure mechanism 2 — L3 is not iteratively converged (independent of any parser)

`PREREGISTRATION.md` §7 registered, in advance and at **every** level, two clauses
that both had to hold:

- **residuals**: initial residual of `Ux`, `Uy` and `p` at the final iteration **< 1e-6**;
- **plateau**: peak-to-peak of the per-iteration v_θ(35 mm) probe **< 1e-6 m/s over the
  last 20 %** (600 of 3000 iterations).

Measured from the committed artifacts:

| level | Ux init. resid. @3000 | Uy init. resid. @3000 | p init. resid. @3000 | plateau ptp, last 600 (m/s) | §7 verdict |
|---|---|---|---|---|---|
| `L1_16x64` | 4.69187e-14 | 4.56645e-14 | 6.50871e-11 | **1.00e-14** | ✅ converged |
| `L2_32x128` | 1.48771e-12 | 1.48751e-12 | 4.85296e-11 | **1.27e-11** | ✅ converged |
| `L3_64x256` | **1.19876e-06** | **1.19876e-06** | **2.89185e-06** | **2.77178e-05** | ❌ **FAILS BOTH** |

L3 misses the residual clause by a factor **1.20** on the velocities and **2.89** on
pressure, and misses the plateau clause by a factor **27.7**. It is close, and close
is not the criterion: the number was frozen at 1e-6 before the run and it is not
moved afterwards.

**`PREREGISTRATION.md` §4, verdict order, step 1:** *"any level not iteratively
converged or not plateaued ⇒ `NOT A RESULT`"*. This fires before the triple is
classified. **The gate can only turn a PASS or GATE FAIL *into* `NOT A RESULT`, never
the reverse** (CLAUDE.md rule 5), and here it never got as far as a PASS or a
GATE FAIL to turn.

**Why this is the more important of the two failures.** Mechanism 1 is a filename;
it costs one afternoon. Mechanism 2 says the **registered iteration budget was wrong
for the fine level**: 3000 SIMPLE iterations at `p 0.3 / U 0.7` relaxation drives the
residual to 4.7e-14 at 1,024 cells, 1.5e-12 at 4,096 and only 1.2e-06 at 16,384. A
**single frozen `endTime` across a grid triple** is adequate at the coarse levels and
inadequate at the fine one — and the triple is exactly the instrument that exposes it.
Filed as `L-287` and, as a measured fact, as `N-AV5`.

---

## 5. Disclosure — raw sampled rows were seen, and they are NOT a lab value

**Disclosed because it happened, not because it helps.** While diagnosing *why* the
comparator could not find its file, the running lane opened
`L3_64x256/postProcessing/radialProbes/3000/gateAxis_p_U.xy` directly and therefore
**saw the raw `U_y` column**, including the row at r = 20 mm, whose value is
**`0.0151085` m/s**. The lane reported this rather than concealing it, and it is
recorded here for the same reason.

**What this number is not:**

- it is **not a lab value** — it was read by eye out of a file, not extracted by the
  frozen comparator, so no planted-zero control has ever been shown able to see a
  non-zero in that reader (CLAUDE.md rule 3), and a number from a reader not proven
  able to see a perturbation **is not evidence**;
- it is **not at the gated radius** — the gate and the triple are on v_θ(**35 mm**),
  the manual's worst-agreement point;
- it is **not on a level that passed §7** — L3 is the level that failed convergence;
- it is **not the registered extraction** — §4 fixes v_θ = −U_x sin θ + U_y cos θ from
  the sampled coordinates, not "column 6".

**It therefore enters no gate, no triple, no register cell and no comparison against
the manual's 0.0151 target, and the fact that it is numerically near that target
changes none of that.** Writing it down while refusing to grade on it is the point:
the alternative — a number that looks right, quietly promoted after the frozen
instrument refused — is precisely the failure this lab's freeze exists to prevent.
The register's lab-value cell reads *"none — comparator refused (exit 2) + L3 not
converged"*, and it will keep reading that.

**No other quantity from run 1 is quoted anywhere as a lab value.**

---

## 6. Cost, and the estimate-versus-actual calibration (CLAUDE.md rule 12)

| item | value |
|---|---|
| ranks | 1 (serial); core-min = wall_s × 1 / 60 |
| **predicted** | **3.0 core-min** (`PREREGISTRATION.md` §8), cap **10 core-min** |
| **actual, measured** | **1.9833 core-min** (119 wall s; 2 + 13 + 104 from the three `RUN_RC.txt`, totalled in `COST.txt`) |
| gross vs cleaned | **identical — 1.9833 core-min both ways.** No run was stopped, relaunched or discarded; no level was rebuilt; the run script and comparator each ran once. No row is anywhere near the 3600 wall-s stall rule (the longest is 104 s) |
| **ratio actual/predicted** | **0.661** |
| against the cap | 19.8 % of 10 core-min; the cap was never approached and no `CAP_EXCEEDED.txt` exists |
| dollars | **$0.001696** derived (1.9833 ÷ 60 × $0.0513/core-h) — predicted was $0.00257 |
| `cost_basis` | owner-stated rate **$0.0513/core-h** (c7a.4xlarge, Sanaa 2026-08-21/22). **Dollars are DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| authorisation | under the 2026-08-21 blanket for CPU runs under $25. **A per-item cost, not a new ceiling** (CLAUDE.md rule 9) |

**Gap attribution: misprediction, in the conservative direction. Waste: zero.
Contention: none.** The §8 estimate was an order-of-magnitude cell-iteration count
(≈ 6.5 × 10⁷ cell-iterations at ≈ 1 µs each ≈ 65 s ≈ 1.1 core-min, rounded up to 3.0
for safety); the box did the same work in 119 s. The estimate was **too pessimistic**,
which is the safe direction and is reported as a miss all the same. The three levels
ran serially on an otherwise-loaded 16-core box, but serial single-core wall time
under `nice` can only be *inflated* by contention, so contention cannot explain a
sub-1 ratio and is not credited with any of it.

**The 1.9833 core-min bought no lab value.** It is not called waste — the runs
completed correctly and their artifacts are the evidence for both findings and for
two lessons and two numerics facts — but it is honestly a rung that must be re-run.

Landed as row **`C-37`** in `docs/COST_CALIBRATION.md`.

---

## 7. Frozen shas — re-hashed at analysis time, all MATCHING

`PREREGISTRATION.md` §9: *"a freeze that is claimed and not checked is a claim about
intent."* Every path below was re-hashed with `git hash-object` on the worktree and
compared against `HEAD` **and** against `cffd90e7` (the HEAD the run executed at).
All three agree for all three files.

| what | blob sha | note |
|---|---|---|
| `PREREGISTRATION.md`, **original freeze** | **`e0afc25936277798d3054137734fd9775311fbbb`** | commit `ffeed580` |
| `PREREGISTRATION.md`, **as amended and as it ran** | **`d6ea5de9286ad5c8699b6e709e105c2cd484e8c1`** | Amendment 1, commit `a9e73c5d` — **pre-compute**, and the run script's own guard 2 recorded this blob in every `RUN_RC.txt` |
| `grade_vmfl001.py` (comparator) | **`8cb29610e5d6f6fa4291df503a98bc99d0ff660f`** | byte-identical to the freeze; not opened, not edited, not repaired |
| `run_vmfl001.sh` | **`f2b09aa230c569629145b3b03613ca8f1873ed0b`** | frozen by Amendment 1, superseding `3da645cf` |
| HEAD at the run | **`cffd90e7`** | |

**Amendment 1 preceded compute.** It relaxed `nounset` across the vendor OpenFOAM
bashrc source (which reads `WM_PROJECT_DIR` before exporting it) and added a positive
`command -v simpleFoam` check in its place. It altered **no** gate, threshold, cap or
label, and it was committed while
`verification/runs/ansys_verification/VMFL001/` held **zero files** — a condition
checked with `find … -type f | wc -l` → `0`, not assumed.

---

## 8. Artifacts — every number above cites one, and all of them are in the repository

Committed at **`ae30f914`** (23 files, 7,896,913 bytes), under
`verification/runs/ansys_verification/VMFL001/`:

| artifact | what it proves here |
|---|---|
| `COST.txt` | 119 wall s, 1.9833 core-min, cap 10 |
| `GRADING_VMFL001.stdout.txt` | the comparator's `REFUSE:` line and exit-2 behaviour, §3 |
| `<level>/RUN_RC.txt` | `rc = 0`, per-level wall s, and the prereg blob `d6ea5de9` the run bound itself to |
| `<level>/log.checkMesh` | the mesh birth certificate: cells 1024 / 4096 / 16384 |
| `<level>/log.simpleFoam` | `End`, 3000 `ExecutionTime` lines, last `Time = 3000`, and the final-iteration residuals of §4 |
| `<level>/postProcessing/radialProbes/3000/gateAxis_p_U.xy` | the v2606-named, header-less sampled file of §3 — the file the comparator could not find |
| `<level>/postProcessing/radialProbes/3000/azimuthCheck_p_U.xy` | the diagnostic azimuth set, ungraded |
| `<level>/postProcessing/gateProbes/0/U` | the 3000-row per-iteration plateau probe of §4. **Cell values; never the graded number** (`PREREGISTRATION.md` §7) |

**Not committed, and deliberately:** `constant/polyMesh` (regenerable by the frozen
run script from the frozen `blockMeshDict.template`, blob `45286819`), and the `0/`
and `3000/` field directories.

**Disclosed:** the nine `postProcessing/` files match `.gitignore` line 67
(`**/postProcessing/`). They are in the repository because `git update-index --add` on
explicit paths does not consult `.gitignore`, and because a record must not cite an
artifact that only exists on the disk. Their presence was verified after the commit,
not assumed.

---

## 9. What the repair must change — and why the re-run is a NEW rung

**Two things must change, and they are different in kind.**

**(a) The comparator's reader (mechanical).** `grade_vmfl001.py` must accept the real
v2606 layout: `postProcessing/<fo>/<time>/<setName>_<fields alphabetical>.xy`,
**no header**, columns `x y z` then the fields in that order. It must keep refusing
when it cannot identify the columns — the fix is to teach it the true convention, never
to make it tolerant. And per `L-286`, the repaired reader must be **exercised against
real solver output from a 2-second coarse level before the new freeze**, not against a
fixture it wrote itself.

**(b) The iteration budget (substantive).** A single `endTime = 3000` for all three
levels is the actual defect. The repair is either a **per-level `endTime`** registered
in advance (the fine level needs several times the coarse level's iterations at this
relaxation), or a **convergence-based stop** — a `residualControl` at 1e-8 with a
generous `endTime` ceiling. The second is cleaner physics and costs the strict
completion rule its clause 3, since the last time would no longer be `endTime` by
construction; a replacement clause must then be registered in the same freeze (last
time < `endTime` **and** the `SIMPLE solution converged` line present **and** the
`ExecutionTime` count equal to the last time). **Whichever is chosen is chosen now, in
the new pre-registration, before the new run.**

**Why this cannot be an addendum to run 1.** `PREREGISTRATION.md` §7's iteration
budget and §9's grading path are **frozen and compute has happened**. CLAUDE.md rule 2
closes gates after first compute: *"changes land only as dated addenda that cannot
alter a gate, threshold, cap or label."* Changing `endTime`, or changing the comparator
that produces the graded number, does both. Any temptation to repair the parser and
re-grade **these same artifacts** is precisely the thing the freeze exists to stop —
the repaired parser would be chosen knowing what number it would produce, and the
`0.0151085` in §5 is on the record as proof that the number was already visible.

**So: the repair is a NEW pre-registration, frozen by sha before any compute, and the
re-run lands as a NEW register row citing row #1** —
`ANSYS_VERIFICATION_CHARTER.md` §6: *"A re-run after a repair is a new row citing the
old one."* **Row #1 is never removed, never re-labelled and never softened to
`PENDING`.** `NOT A RESULT` is what run 1 was, and the register will say so
permanently.

**Register row #1** is in `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`.
The credential count stands at **0 PASS of 1 run**.

---

## 10. What this run does NOT claim, restated

- **Nothing about Ansys.** The manual's Fluent (0.0151 / 0.0105 / 0.0072 / 0.0045) and
  CFX (0.0150 / 0.0105 / 0.0071 / 0.0045) columns are context and were never the gate
  (`PREREGISTRATION.md` §2.3). No archive was opened.
- **Nothing about this lab's accuracy on VMFL001**, in either direction. A refused
  comparator and an unconverged fine level produce no evidence of agreement *and no
  evidence of disagreement*.
- **Nothing about the transport properties.** The comparator's §5 provenance checks on
  `nu` and `omega` never ran — it refused before reaching them.
- **Nothing about grid convergence.** No triple was classified; no GCI exists and none
  is quoted.
