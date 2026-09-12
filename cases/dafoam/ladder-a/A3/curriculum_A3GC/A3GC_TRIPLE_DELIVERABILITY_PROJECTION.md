# A3GC — CAN THE GRID TRIPLE BE DELIVERED, AND WHEN

**Decision note. Measured 2026-09-12 02:12–02:56Z by a dafoam lane, read-only on both live runs.**
No verdict token is emitted here. Grading is the frozen comparator's alone.

---

## 1. L2 PER-STEP RATE — MEASURED, AND IT IS DECELERATING

`primal.log` prints at `printInterval 100`, so per-step resolution does not exist in the artifact;
the windows below are the finest the log permits. Wall seconds are `ClockTime` from
`/home/ubuntu/certonomous-runs/A3GC-L2/primal.log`; the cross-check column is the host-side
watcher `a3gc_L2_BUDGET_WATCH.txt`, an independent instrument.

| window (steps) | wall s/step (primal.log) | cross-check (BUDGET_WATCH) | CPU s/step (`ExecutionTime`) | ExecTime/ClockTime |
|---|---|---|---|---|
| 100 → 200 | **5.33** (`:1295`,`:1912`) | 5.41 | 3.835 | 0.719 |
| 300 → 400 | **7.11** (`:2529`,`:3146`) | 7.24 | 4.648 | 0.654 |
| 600 → 700 | **17.34** (`:4380`,`:4997`) | 17.05 | 7.280 | 0.420 |
| 700 → 779 (live, derived) | **33.0** | — | — | — |
| last 310 s (5 steps, ±20 %) | **~62** | — | — | — |

**DECELERATING.** 5.33 → 7.11 → 17.34 → 33.0 s/step across four disjoint windows, a 6.2× slowdown
over 679 steps. Two instruments agree to within 2 % on all three completed windows. The naive
linear ETA from any early window is **optimistic and must not be used.**

Of the slowdown, ~1.9× is in the solver's own CPU seconds and ~3.3× in wall — the gap is scheduler
starvation: the master rank's `ExecutionTime/ClockTime` fell **0.719 → 0.420**. Live step count
779 derived by counting `GAMG:  Solving for p` lines past `primal.log:4997` (1 per SIMPLE step).

## 2. L2 LANDING AT endTime 6000

From step 779 at 02:55:53Z, 5,221 steps remain. np = 8.

| case | rate assumed | lands (UTC) | total core-min | × registered 163 |
|---|---|---|---|---|
| LOW — contention clears fully, rate reverts to best observed | 5.33 s/step | **10:35Z 12 Sep** | 4,835 | 30× |
| **CENTRAL — measured live rate holds** | 33.0 s/step | **02:50Z 14 Sep** | **24,100** | **148×** |
| HIGH — most recent sub-window holds | 62 s/step | **20:50Z 15 Sep** | 44,300 | 272× |

**Contention caveat and its direction of error.** Box is 16 cores at load1 39.9 (2.5× oversubscribed)
with cfd and heat-transfer solves alongside; the L2 ranks were reniced to `ni=10` post-start
(`a3gc_L2_BUDGET_WATCH.txt`, nice block), so L2 is structurally the **yielding** job — first to lose
cores, last to regain them. Under the current dispatch policy the error direction is therefore
**toward LATER, not earlier**, and the four measured windows show it has gone later, not earlier,
for the last 2.7 h. Registered estimate 163 core-min (`PREREGISTRATION.md:361`) was already
consumed 6.6× over at step 700 (11.7 % of the run).

## 3. L1 PRIMAL — PROJECTED FROM MEASUREMENT, NOT FROM THE REGISTERED ESTIMATOR

Cell counts from disk: L2 = **798,720** (sum of the 8 processor counts, `primal.log:92–170`);
L1 = **6,389,760** (`PREREGISTRATION.md:133`; L1 uses the c0 fine surface — md5 `e6c853158d…`
matches `m6_surfaceMesh_fine.cgns`, L2's surface is a different md5). **Ratio exactly 8.000.**

**Scaling assumption, stated: linear in cells is a FLOOR, not an estimate.** At fixed np = 8, GAMG
iteration counts grow with problem size and the per-rank working set (8× cells/rank) leaves cache,
so the true exponent is ≥ 1. Every row below is a lower bound on its own case.

| case | L1 s/step (8 × L2) | wall at np=8 | core-min | × registered 1,302 | $ derived |
|---|---|---|---|---|---|
| LOW — best-observed L2 rate, linear | 42.6 | **2.96 days** | 34,100 | 26× | $29 |
| **CENTRAL — L2 whole-run mean, linear** | 86.6 | **6.0 days** | **69,300** | **53×** | $59 |
| HIGH — live L2 rate, linear | 264 | **18.3 days** | 211,200 | 162× | $181 |

Dollars **derived at $0.0513/core-h, not measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). The registered 1,302 core-min is exactly 8 × the registered L2 figure,
i.e. the registered estimator was itself linear-in-cells anchored on 81.4 core-min at 399,360 cells
(`PREREGISTRATION.md:361–362`); the anchor is what missed, not the scaling.

**The L1 primal is NOT a same-week deliverable.** The most favourable defensible case — L2's best
observed rate returning AND scaling exactly linear — is 3.0 days of uninterrupted np = 8, and it
requires the box to be otherwise idle, which is the condition that is not true. The measured case
is 6–18 days. L1 primal also cannot start until stage 1 plus `plot3dToFoam`/`renumberMesh`/
`checkMesh`/`decomposePar` complete.

## 4. L1 STAGE 1 (pyHyp) — LANDS TODAY

pid 2656601, `--cpus 1`. Elapsed **4,658 s** wall / 4,079 s CPU (87.6 % of one core) at 02:55:53Z,
from `/proc/2656601/stat` against `/proc/uptime`. `N = 65` → **64 extrusion layers**
(`A3GC-L1/genWingMesh.py`). RSS **353 MB** — pyHyp is not the memory risk.

Measured per-layer series, `A3GC-L1/logMeshGeneration.txt` (col 2 = cumulative pyHyp seconds):
layer 30 at **1,171.1 s**; per-layer cost growing **~12.4 %/layer** over layers 14→30 (13.0 s → 84.4 s).

| model | remaining | stage 1 completes | total core-min (np=1) |
|---|---|---|---|
| per-layer cost saturates at ~420 s | 2.3 h | **~05:15Z 12 Sep** | 218 |
| L2 stage-1 reference × 8 (linear) | ~4.6 h | **~09:10Z 12 Sep** | 450 |
| geometric growth continues at 12.4 %/layer | 9.8 h | **~12:45Z 12 Sep** | 666 |

**Stage 1 is a today item, not a week item** — the week is in the primal.

**Honest gap:** the log is block-buffered and frozen at 4,385 B since 01:59:51Z, so the current layer
(**≈ 44 of 64**) is *derived* by applying the measured growth model to CPU seconds consumed — it is an
inference, not a reading. Liveness is confirmed by container CPU accounting, not by the log.

**Open, unmeasured, unchanged:** whether the **4 GiB** container ceiling suffices for
`plot3dToFoam`/`renumberMesh`/`checkMesh` at 6,389,760 cells. L2's `volumeMesh.xyz` is 56.6 MB ASCII
at 798,720 cells → L1's ≈ 453 MB; arithmetic on the resulting polyMesh (≈6.5 M points, ≈19.3 M faces)
puts `plot3dToFoam` peak at **~3–8 GiB with 64-bit labels, ~2–4 GiB with 32-bit**. **4 GiB is
marginal and more likely to bite than not.** I did not measure it and I did not change the ceiling;
it is held at 4g by the supervisor's gate.

## 5. READINGS ON L2 CONVERGENCE — NOT A GRADE

`p initRes` at each printed step (`primal.log:674,1285,1902,2519,3136,3753,4370,4987`):
1 → 1.0 | 100 → 1.678e-02 | 200 → 2.505e-02 | 300 → 1.259e-02 | 400 → 4.185e-03 |
500 → 2.144e-03 | 600 → 1.040e-03 | **700 → 9.887e-04**

Decay ratio per 100 steps: **0.45** over 200→600, then **0.951** over 600→700. Over the last 79 steps
the per-step GAMG p initial residual oscillates in a two-cycle in **[9.91e-04, 1.037e-03]**, mean
~1.02e-03 — i.e. **above** the step-700 value. Fit on 400→700 (ratio 0.616/100 steps) reaches 1e-06 at
**step ≈ 2,120**; fit on 600→700 alone reaches it at **step ≈ 14,390**; the live 79-step window has no
downward trend and sits at **~1.0e-03, three decades above the Sec. 3.6 floor of 1e-06**
(`PREREGISTRATION.md:252`). **Reading: flattening, not descending.**

`CD` / `CL`: CD 0.02097(300), 0.02132(400), 0.02177(500), 0.02266(600), **0.02237(700)** — peak-to-peak
over 400→700 is **6.0 %**, over the last two samples −1.28 %; **not plateaued**. CL 0.30882(400),
0.30804(500), 0.31254(600), **0.31354(700)** — peak-to-peak over 400→700 is **1.8 %**, last two +0.32 %;
**plateaued from ~step 400 at the 2 % level.** Registered `G-PLAT` (AMENDMENT 1(a)) reads peak-to-peak
over the last 10 printed samples and demands iterative error ≤ 1/10 of the level-to-level difference;
the window currently holds 8 samples, not 10. These are readings for the supervisor, not a grade.

---

## CONCLUSION

**The triple cannot be delivered this week, and the blocker is the L1 primal, not the L1 mesh.**
L1 stage 1 lands today (05:15Z–12:45Z); L2 lands 02:50Z 14 Sep at the measured rate (band 10:35Z
12 Sep – 20:50Z 15 Sep, 4,835–44,300 core-min); the L1 primal is 6.0 days central and 3.0 days
under the most favourable assumption measurement will support, on a box already 2.5× oversubscribed.
**A third decision now sits beside cost: at step 779 the L2 p residual is flat at ~1.0e-03 against
a 1e-06 floor, so 6000 steps may not buy the Sec. 3.6 condition at any price** — the spend question
and the convergence question are no longer separable.

*Counter-argument, one sentence:* if the cfd and heat-transfer solves clear and L2's `ni=10` renice
stops costing it cores, the rate reverts toward 5.33 s/step and L2 lands today — but that same relief
applied to L1 still gives 3.0 days, and it does nothing about a flat residual.
