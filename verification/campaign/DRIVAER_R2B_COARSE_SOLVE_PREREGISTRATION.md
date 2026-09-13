# DRIVAER R2b — (b)-SPEC COARSE SOLVE

**Status: STAGED, UNSIGNED, UNLAUNCHED.** Written while probe `R2b-C1` is still
building, so that if the probe holds the decision costs zero minutes. Rung id
`R2b-S1`. 2026-09-12, cfd.

**CONDITIONAL ON THE PROBE, AND THE CONDITION IS NAMED WITH THE DIRECTORY THAT DOES NOT
YET EXIST:** this registration is void unless `R2b-C1` PASSES its own registered gate
(`DRIVAER_R2B_LAYER_PROBE_PREREGISTRATION.md`, frozen `b73c1356`). At the time of
writing `verification/runs/navier_class/DRIVAER/LAYERFIX_C1_coarse_absoluteFirstLayer/C1_MEASURED.json`
**does not exist** and no solve directory for this rung exists. Amendments before first
compute are legal; after it, addenda only.

## 0. THE FALSIFIER, FIRST

**This run is NOT worth having — and must not be dressed up as a result — if any of:**

- **F1 — the layer spec did not transfer.** Layered-group area-weighted median y⁺ outside
  **[30, 300]** on the solve mesh. The whole point of this run is a Cd whose wall
  treatment is inside the wall-function band; outside it, this is just another capped
  level and the verdict is **`NOT A RESULT`**, not a weaker pass.
- **F2 — completion.** Any rule-4 clause fails (rc≠0 from the wrapper's own sidecar, no
  `End`, last ≠ `endTime` 2000, missing `p U k omega nut phi` at 2000, `ExecutionTime`
  count ≠ 2000, or any field not newer than `0/U` — the age guard). → **`NOT A RESULT`**.
- **F3 — not plateaued.** Cd excursion over the frozen window exceeds tolerance, or
  iterative convergence is not read as CONVERGED from the log. → **`NOT A RESULT`**
  (rule 5 limb 1).

**None of these is repairable by re-reading the data differently.**

## 1. What this run is, and the one thing it is NOT

One coarse level, `simpleFoam` kOmegaSST, 4 ranks, `endTime` 2000, built on the (b)
layer spec — `relativeSizes false; firstLayerThickness 2.10e-3; minThickness 5.25e-4`.
It is registered to deliver **PRIORITY 1: one healthy completed 3-D run, wall treatment
inside its band, results on disk.**

**IT IS NOT A GRID-CONVERGED Cd AND NO GCI OR OBSERVED ORDER IS ON OFFER.** One level is
not a triple; `grade_drivaer.py`'s `grade_ladder` path is NOT executed and Gate G is not
registered. Any later citation that drops this sentence is misciting the run.

## 2. Gates

| gate | criterion | instrument |
|---|---|---|
| **Y1 wall admissibility** — the gate this run exists for | layered-group area-weighted median y⁺ **∈ [30, 300]** | `stage_r2_measure.py` `--yplus`, field `gate_Y1` |
| **Y1b unlayered exposure** — REPORTED, NOT GATED | unlayered-group median y⁺ and its **share of wetted area**, both stated beside any Cd | same |
| **A1 completion + instrument** — a real gate | rule-4 completion on the level, on-disk forceCoeffs constants asserted against the pinned reference, all three planted controls fired, iterative state READ from the log, Cd and Cl plateaued | `grade_drivaer.py --stage-a` |
| **A2/A3 gross-error bands** — DIAGNOSTIC, NOT VALIDATION | Cd ∈ [0.15, 0.60], Cl ∈ [−0.50, 0.50] | same |
| **C2 single-level Cd agreement** | \|Cd − 0.2758368\| ≤ **10 %** of 0.2758368, i.e. **[0.24825, 0.30342]** | Cd from `coefficient.dat`; reference from `drivaer_reference_notchback.json` |

**C2's tolerance is the frozen grader's own `CD_BAND_REL = 0.10`. IT IS NOT A NEW NUMBER
AND IT WAS NOT CHOSEN TO FIT.** Widening it for a coarse level is exactly the move rule 2
exists to prevent, so it is not made.

**AND C2 IS PREDICTED TO `GATE FAIL`, REGISTERED HERE BEFORE THE RUN.** Coarse RANS on a
detailed bluff body over-predicts drag, and the running `r2_coarse` — same cells, same
solver, out-of-band wall treatment — reads **Cd 0.35616 at iteration 748, +29.1 % against
the reference.** A coarse level is not expected to reach ±10 %. **The value of this run is
not C2.** It is Y1 plus a completed, plateaued, planted-control-verified 3-D solve whose
**residual Cd error is now attributable to grid rather than to a wall model sitting
outside its calibration** — which is the first time that has been true for DrivAer in this
lab. If C2 does pass, that is a finding and it is not the one predicted.

**Tier disavowal, carried with every Cd from this run:** DrivAerML is a scale-resolving
CFD dataset — a **CODE reference, rank 2, NOT experiment.** A C2 pass reproduces a code
reference and is **NOT experiment-validated.**

## 3. Plateau — the criterion, and the windows

**VERDICT LIMB, FROZEN, UNCHANGED:** `grade_drivaer.py`'s `windowed_plateau` —
statistic `(max − min)/|mean|` over the trailing **W = 10 % of endTime = 200 samples**,
tolerance **0.005**. W is derived from the run's registered length, never from the data.

**REPORTED BESIDE IT, DIAGNOSTIC:** the same statistic and the endpoint drift at
**W = 10, 20, 30, 50, 100, 200, 300, 500**, written to `DRIFT_WINDOWS.tsv` by
`watch_grade_r2.sh`. **A PLATEAU IS NOT A FLAT SPELL:** on this very case a Cd read
+0.787 % over 10 iterations, +0.047 % over 20 and +7.039 % over 30 — the same series at
the same instant, disagreeing by 150×. **No plateau claim is made from one window.**

**If a CONVERGED run's excursion over W=200 exceeds 0.005, the criterion is
UNSATISFIABLE and that is a finding to report, not a fail to record** — and the
diagnosis separating genuine drift from a single blip is required before that call.

## 4. Cost — MEASURED per-level, not extrapolated

From `r2_coarse`'s **own** `log.simpleFoam` (816 iterations): **1.904 s/iter/rank of CPU**.
The r1_fine figure of 63,491 cell-it/core-s is **NOT used** — it was measured at 5.03 M
cells on 8 ranks and does not transfer to 187 k cells on 4.

| | value |
|---|---|
| CPU-held work, 2000 iterations, 4 ranks | **254 core-min** (= 1.06 h wall if each rank held a full core) |
| gross at tonight's contention | **2,891 core-min, 12.0 h wall** — efficiency **8.8 %** |
| registered prediction | **254 core-min CPU-held; gross reported as measured, with contention named separately and NEVER absorbed** |
| peak memory | **0.45 GiB** across 4 ranks, MEASURED on `r2_coarse` |
| derived | 254 core-min = 4.23 core-h → **$0.217 DERIVED, NOT MEASURED** at $0.0513/core-h (`COMPUTE_BUDGET_CHARTER` §5) |

Cell count is **PENDING the probe** and the cost scales with it; if the (b) mesh differs
materially from 186,709 cells the CPU-held figure is rescaled at the measured
**24,522 cell-it/core-s** of this level and the rescaling is shown.

**NO CAP KILLS ANYTHING.** Sanaa has ruled no cap three times. The figures above are
predictions scored at completion under rule 12. **The MemAvailable refusal in
`launch_r2_solve.sh` IS armed — it is a physics guard, not a budget guard.**

## 5. Grading path — LITERAL HASHES

| instrument | sha256 at staging |
|---|---|
| `cases/navier_class/DRIVAER/grade_drivaer.py` | `6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7` |
| `cases/navier_class/DRIVAER/mesh/stage_r2_measure.py` | `c86a8ea4317f0dc21a00c9c739f8de7932bebf86345751632deddffd1640bb0e` |
| `cases/navier_class/DRIVAER/mesh/launch_r2_solve.sh` | `60074739b918ce76089818607064ee0f642e365da3d24b991505b72b4afb668d` |
| `cases/navier_class/DRIVAER/mesh/write_solver_case.py` | `b1b67ae1249636ce4a6ad9246ace236ff05035f87f47031117c68dc81dfe3f1f` |
| `cases/navier_class/DRIVAER/mesh/watch_grade_r2.sh` | `aaa727abc77e8091fd0dd07be44e16c2f70429a5f3aac4d92514038e8460156d` |
| `verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json` | `bb504af34ed077f120526771e4852d82890af2f511c907cf36956acf72238c72` |

**Each is re-computed and compared against the literal above before any verdict is
believed. A mismatch is a REFUSAL, not a note.** Not a `git rev-parse` recipe — a recipe
that re-reads the file agrees with itself at every commit and proves nothing.

## 6. Durability

The solve is launched by `launch_r2_solve.sh` (rc captured inside the wrapper;
`reconstructPar -newTimes` so the age guard is not defeated by restamping `0/`) and
watched by a **frozen per-run copy** of `watch_grade_r2.sh` at
`<run>/watch_grade_r2.frozen.sh`, setsid-detached. **bash re-reads a running script by
byte offset**, so the watcher runs from a frozen copy and never from a path an editor
may touch. The watcher signals nothing, ever, and re-asserts `/proc/<pid>/cwd` AND
cmdline on every poll.

---

## ADDENDUM 1 — 2026-09-13 — **THE CASE-WRITER sha256 PINNED AT §114 IS STALE AGAINST THE LIVE PATH, AND THAT IS EXPECTED**

**lines whose number changed above this section: 0.** No gate, threshold, cap, label or band is
altered. **No regrade is implied and no verdict of this registration is affected.**

**The pin at line 114 reads `b1b67ae1249636ce4a6ad9246ace236ff05035f87f47031117c68dc81dfe3f1f`
against `cases/navier_class/DRIVAER/mesh/write_solver_case.py`.** That file was changed on
2026-09-13 at commit `e7702536125743b22b485074cfb5e253f7952ca5` and now hashes to
`498f5b10054a996fe2d32b7bbb5acf2a4cea73642519aed12f88838bb9ba2a71`.

**1. THE PINNED HASH IS RESOLVED THROUGH GIT, NEVER FROM DISK.** The canonical form is:

```
git show ed67a279c416d7a516922b67e6871401f397a04c:cases/navier_class/DRIVAER/mesh/write_solver_case.py | sha256sum
  -> b1b67ae1249636ce4a6ad9246ace236ff05035f87f47031117c68dc81dfe3f1f
```

`ed67a279c` is **this registration's own freeze commit**. Verified, not asserted.

**2. THE CHANGE POSTDATES THE RUNS.** Last file activity is **2026-09-12 05:26** in `r2_medium` and
**2026-09-12 17:30** in `r2_coarse`, both carrying `RUN_RC = 0`; the writer changed **2026-09-13
18:43**. **The runs this registration governs were produced by `b1b67ae1…`, and nothing about them
is altered.**

**3. WHAT CHANGED, IN ONE LINE.** The `nut` wall treatment became a **required argument with no
default** (`--nut-wall-vehicle`, `--nut-wall-floor`), so the writer refuses to write a case whose
wall treatment nobody stated; a count-based readback asserts the written bytes carry exactly the
requested treatments. **The reason: R5 registers `nutUSpaldingWallFunction` while the staged case
carried `nutkWallFunction`, and a silent default is what allowed that divergence.**

**4. 🔴 A `DRIFTED` RESULT AGAINST THE LIVE PATH IS EXPECTED AND IS NOT EVIDENCE OF TAMPERING.** A
verifier re-checking this pin against the filesystem **will** disagree, and that disagreement is
this addendum, not a finding. **Re-check through git at the commit named in item 1.**

**5. THE GENERAL DEFECT, RECORDED BECAUSE IT HAS NOW BITTEN THREE INSTRUMENTS IN ONE NIGHT.** *"A
document pinned as a frozen instrument cannot also be the file that evolves."* Any registration
pinning a script **by disk hash** acquires a landmine the first time that script is **legitimately
improved** — PPTC's comparator, CRM's pin naming a blob and a commit that never went together, and
this. **The fix is the same in all three: pin by commit, resolve through git, never from the
filesystem.**
```

---
