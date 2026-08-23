STATUS: **DRAFT — NOT FILED, NOT LAUNCHED.** Not frozen; Sanaa signs. No run until the signed file is committed and its sha recorded.

# PREREGISTRATION DRAFT — Ling, Kurzawski & Templeton (2016) TBNN, GPU arm

Written 2026-08-22 by the closure GPU-PLAN lane. **Zero compute was spent writing it.**
No GPU instance exists, none was created, no AWS call of any kind was made.
GPU spend sits **outside** the 2026-08-21 CPU blanket approval (`CLAUDE.md` rule 12,
`docs/GPU_CAPABILITY_STATE.md` §6): this file is a draft Sanaa signs, not a frozen file.

Companion to the CPU lane at `../PREREGISTRATION.md` (frozen 2026-08-20) and
`../RESULTS.md` (**GATE REACHED**). This file registers **only what the CPU lane
could not afford**, and does not re-open, re-score or amend anything in those two.

---

## 1. Paper

**Title-verified from the PDF on disk (L-144, Charter §15).**

* Printed title page, line 1-3: `SAND2016-7345J` / *Reynolds Averaged Turbulence
  Modeling using Deep Neural Networks with Embedded Invariance* / Julia Ling and
  Jeremy Templeton (Sandia National Laboratories), Andrew Kurzawski (University of
  Texas at Austin), dated **July 24, 2016**.
* **Path on disk:** `docs/papers/closure/Ling2016_tbnn_embedded_invariance.pdf`
  (17 pp, sha256 `4f4fc80e2373075780e990d27496af3f8450c073c533470749b02c6bce5579c3`),
  sidecar `Ling2016_tbnn_embedded_invariance.txt`.
* **Journal:** *J. Fluid Mech.* 807:155-166 (2016). **arXiv id: none recorded** — the
  on-disk copy is the Sandia unlimited-release report `SAND2016-7345J`, not an arXiv
  preprint, and `MANIFEST.md` records no arXiv identifier for it. **Author order on the
  printed title page is Ling, Templeton, Kurzawski**; the citation of record used
  throughout this lab is Ling, Kurzawski & Templeton. Recorded, not silently harmonised.

## 2. What the reproduction claims to test

The CPU lane already tested the paper's **structural** claim and returned **GATE
REACHED**. This arm tests the two things that lane declared it could not do.

**The paper's headline numbers** (Table I, p. 11 — RMSE of `b_ij` against DNS on two
held-out flows), quoted here for provenance and **not as a target**:

| Model | Duct `Re_b` = 2000 | Wavy wall `Re` = 6850 |
|---|---|---|
| LEVM | 0.23 | 0.18 |
| QEVM | 0.18 | 0.11 |
| **TBNN** | **0.13** | **0.08** |
| plain MLP | 0.33 | 0.09 |

Stated improvements: "43% more accurate than the LEVM and 28% more accurate than the
QEVM" (duct, p. 10); "a 56% reduction in error with respect to LEVM and a 27% reduction
in error with respect to QEVM" (wavy wall, p. 11).

**Stated uncertainty: none.** The paper gives no interval, no seed spread and no error
bar on any of the eight numbers above. Recorded because a reproduction cannot be scored
against a band the source never supplied.

**Why 0.13 is not the target.** None of Ling's nine flows is on this machine
(`../PREREGISTRATION.md` §2). This is a labelled **VARIANT** (Charter §9) on the Closure
Challenge benchmark, exactly as the CPU lane was.

**The two things the CPU lane could not afford, and this arm registers:**

* **ARM-A — Ling's own optimiser, run to convergence.** `../RESULTS.md` departure **D3**:
  *"Ling report lr 2.5e-7 for the TBNN (p. 7) and 2.5e-6 for the MLP (p. 6) with plain
  SGD. We use Adam at 1e-3 for both, because their rates with Adam do not move in 400
  epochs on this data. This is a real departure and it is the most likely place a
  faithful reproduction would differ."* ARM-A removes D3: plain SGD at the paper's own
  rates, epoch cap raised.
* **ARM-B — the Bayesian architecture search that produced 8x30.** Ling state (p. 9)
  that 8 hidden layers of 30 nodes were **chosen by Bayesian optimisation**. The CPU lane
  hard-coded 8x30 as an input (`../train_tbnn.py:82`, `nh=30, nlayers=8`). ARM-B runs the
  search, so 8x30 becomes an output here as it was there.

**What is NOT in this arm.** The a-posteriori propagation (ARM-C below) runs on **CPU**,
not GPU; it is registered here because Charter §2 requires it, and its cost is CPU cost.

## 3. Case / data on disk

**On disk. This is the only one of the five GPU items whose data is present.**

| artefact | exact path | size |
|---|---|---|
| assembled dataset | `/home/ubuntu/closure-data/tbnn/dataset.npz` | 167,118,904 B |
| extended features | `/home/ubuntu/closure-data/tbnn/features_ext.npz` | 39,325,536 B |
| provenance | `/home/ubuntu/closure-data/tbnn/provenance.json` | 286 B |
| CPU checkpoints | `/home/ubuntu/closure-data/tbnn/ckpt/`, `ckpt_mlponly/` | — |
| benchmark clone | `/home/ubuntu/closure-challenge-benchmark` (commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`) | 1.3 GB |

`dataset.npz` arrays, read 2026-08-22: `lam (641652, 5) float32`, `T (641652, 10, 3, 3)
float32`, `b_LES (641652, 3, 3) float32`, `b_RANS (641652, 3, 3) float32`,
`valid (641652,) bool`, `case_id (641652,) int32`, `names (40,)`, `families (40,)`,
`splits (40,)`, `ncells (40,)`.

**Nothing would have to be pulled.** No licence question arises: the benchmark is
already cloned and the derived dataset was built here by `_common/build_dataset.py`.

**Region note.** The data is on `i-0e417e686a5a6ac1a` in **us-east-2c** and the quota is
**us-east-2** (`GPU_CAPABILITY_STATE.md` §3), so a GPU instance reaches it by snapshot or
attached volume without moving it cross-region.

## 4. Architecture, as the paper states it

* **TBNN (paper, p. 9):** input layer = 5 invariants `lambda_1..lambda_5`; **8 hidden
  layers of 30 nodes**, "chosen by Bayesian optimisation"; a Final Hidden Layer of 10
  elements representing `g^(n)`, `n = 1..10`; a Tensor Input Layer of the 10 basis
  tensors `T^(n)`; a Merge Output Layer performing element-wise multiplication and
  summation.
* **Control MLP (paper, p. 6):** 10 hidden layers x 10 nodes, learning rate 2.5e-6.
* **Optimiser (paper, pp. 6-7):** plain SGD, lr 2.5e-7 (TBNN), 2.5e-6 (MLP).
* **Parameter count: the paper does not state it.** Derived from the stated shape,
  `5 -> 8x30 -> 10` with biases: `(5*30+30) + 7*(30*30+30) + (30*10+10)` =
  `180 + 6510 + 310` = **7,000 parameters**. Control MLP `5 -> 10x10 -> 6`:
  `(5*10+10) + 9*(10*10+10) + (10*6+6)` = `60 + 990 + 66` = **1,116 parameters**.
* **Epoch count, batch size, training time, hardware: the paper does not state any of
  them.** This is the reason §6's GPU-hour figure cannot be derived from the paper and is
  derived from this lab's own measured CPU rate instead.
* **Activation function: the paper does not state it.** The CPU lane used
  `LeakyReLU(0.01)` (`../train_tbnn.py:85`) and this arm keeps that, as a carried-forward
  departure, listed again in §11.

## 5. GPU memory need — the arithmetic

All figures **float32**, which is an **assumption** (the paper states no precision).

**Resident dataset**, from the shapes read off `dataset.npz` above:

```
lam    641652 x 5           x 4 B =  12.83 MB
T      641652 x 10 x 3 x 3  x 4 B = 230.99 MB
b_LES  641652 x 3 x 3       x 4 B =  23.10 MB
                                    ---------
resident (b_RANS not needed to train) = 266.93 MB
```

**Parameters and optimiser state** (trivial, and that is the finding):

```
TBNN weights           7,000 x 4 B =  28.0 kB
Adam m + v (ARM-B)     7,000 x 4 B x 2 =  56.0 kB
SGD, no state (ARM-A)                =   0
total parameter-side                 <  0.1 MB
```

**Activations**, the only term that scales with batch. ASSUMED footprint per sample:
9 affine layers x 30 units = 270 floats, plus the `T` slice already resident, plus the
`einsum` output 9 floats; forward + backward + gradient ~= 3x, so
`(270 + 9) x 3 x 4 B ~= 3.35 kB/sample`. **Rounded up to 4 kB/sample** to cover framework
overhead — an assumption, stated as one.

```
batch      8,192 (CPU lane's batch):   8,192 x 4 kB =   32.8 MB  -> total ~ 0.30 GB
batch     65,536:                     65,536 x 4 kB =  262.1 MB  -> total ~ 0.53 GB
batch    641,652 (full batch):       641,652 x 4 kB = 2,566.6 MB -> total ~ 2.83 GB
```

**Registered peak requirement: ~2.9 GB at full batch, ~0.5 GB at batch 65,536.**
Assumed: float32; 4 kB/sample activations; no framework arena beyond that; dataset held
resident rather than streamed.

**Every one of the four candidate instance classes has more GPU memory than this needs.**
The exact figure per class is **to be read** from the AWS console (see §7) — it is not
recalled here, and `GPU_CAPABILITY_STATE.md` §3's per-class GPU-memory column is itself an
unverified recall, flagged rather than relied on.

## 6. Estimated GPU-hours — the arithmetic, and what is assumed

**The paper states no training time and no hardware**, so no scaling from the paper's own
figures is possible. The basis is instead **this lab's own measured CPU rate**, which is a
record: `../RESULTS.md` §9 and `_common/FEASIBILITY.md` §2.1.

**Measured basis, and a disagreement inside the lab's own records, recorded not resolved:**

| record | rate |
|---|---|
| `../RESULTS.md` §9 | **0.78 s/epoch** at `torch.set_num_threads(4)`, batch 8192 |
| `_common/FEASIBILITY.md` §2.1 | **~1.5 s/epoch on 4 threads**; full 10-run sweep ~1 h wall |

Both are called measured; they differ by 1.9x. **The range below carries both ends** and
the disagreement is flagged for whoever re-measures before the signed run.

**ARM-A — Ling's SGD at 2.5e-7, run to convergence.**
Epoch budget is the dominant term and it is an **ASSUMPTION**: Adam at 1e-3 against SGD at
2.5e-7 is a step-size ratio of 4,000x, and the CPU lane measured that the paper's rates
"do not move in 400 epochs". **Assumed epoch cap 200,000** — 500x the CPU lane's 400 — as
the smallest budget under which a null result would mean "did not converge in a budget
500x what failed before" rather than "was not given a chance". **This assumption, not the
hardware, sets the number.**

```
CPU-equivalent, 5 seeds:
  0.78 s/epoch x 200,000 epochs x 5 seeds = 780,000 s = 216.7 wall-h at 4 threads
  1.50 s/epoch x 200,000 epochs x 5 seeds = 1,500,000 s = 416.7 wall-h at 4 threads
```

**Relative throughput assumption, stated and not recalled:** a 7,000-parameter network at
batch 8192 is **kernel-launch-bound, not FLOP-bound**, so the honest assumption is a
*range that includes no speedup at all*: **1x to 20x** a 4-thread CPU, the 20x reached
only by enlarging the batch to fill the device (full batch, §5). No published benchmark is
cited, because citing one from recall is exactly what `CLAUDE.md` rule 12 forbids.

```
ARM-A GPU-h = 216.7 / 20  to  416.7 / 1   =  10.8  to  416.7 GPU-h
```

That upper end is the *no-speedup* case and it is written down rather than hidden. The
**registered planning range takes the batch-enlarged branch only**, because ARM-A will be
run at full batch by construction (§5):

```
ARM-A registered = 216.7/20 to 416.7/10 = 10.8 to 41.7 GPU-h
```

**ARM-B — the Bayesian architecture search.** Ling do not state their search budget.
**Assumed 100 trials x 3 seeds x 400 epochs** (100 trials is this lane's assumption for a
5-dimensional search over depth, width, activation, batch and lr; it is not the paper's).

```
0.78 s/ep x 400 ep x 300 runs =  93,600 s = 26.0 wall-h at 4 threads
1.50 s/ep x 400 ep x 300 runs = 180,000 s = 50.0 wall-h at 4 threads
GPU-h at 5x to 20x            =  26.0/20 to 50.0/5 = 1.3 to 10.0 GPU-h
```

**TOTAL registered range: 12 to 52 GPU-h.** Assumed throughout: the epoch cap (200,000),
the trial count (100), the throughput factor (5-20x, and 1x written down as the floor),
float32, and one instance at a time.

**Registered cap: 60 GPU-h.** An overrun **stops the run** (`CLAUDE.md` rule 12); it does
not get a new budget, and the verdict on overrun is **BLOCKED**.

## 7. Instance class within the 8-vCPU quota

**Registered: `g6.xlarge` (4 vCPU).**

Reasoning: §5 puts the peak requirement at **~2.9 GB**, far below every candidate class, so
GPU memory does not select the instance. The workload is one tiny network with a resident
267 MB dataset — **the host CPU does nothing but feed it**, so the 4-vCPU class is not a
constraint. Choosing `g6.xlarge` over `g6.2xlarge` leaves **4 of the 8 quota vCPUs free**,
which is the headroom the quota request itself was written to buy
(`GPU_CAPABILITY_STATE.md` §2: *"The 8-vCPU request allows a single instance plus headroom
for one size step"*).

| class | vCPU | fits 8-vCPU quota | GPU memory |
|---|---|---|---|
| **`g6.xlarge`** | **4** | **yes, and two would fit** | **to be read** from the console |
| `g6.2xlarge` | 8 | yes, exactly one | **to be read** |
| `g5.xlarge` | 4 | yes | **to be read** |
| `g5.2xlarge` | 8 | yes, exactly one | **to be read** |

`g5.xlarge` is an acceptable substitute if `g6` capacity is unavailable in us-east-2; the
registered arithmetic does not depend on which, because the binding constraint is
kernel-launch rate, not memory or FLOPs. **A substitution is a departure and is logged.**

cost: 12-52 GPU-h x g6.xlarge @ cost_basis: console price, to be read by Sanaa

## 8. Gates, with thresholds

Verdict vocabulary is exactly `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` /
`BLOCKED` / `PENDING` (`CLAUDE.md` rule 1, Charter §12).

**G0 — planted-zero control (§9). Must pass before any other gate is read.**
Refusal or a mis-read plant → **NOT A RESULT** for the whole arm.

**G1 — ARM-A, the paper's own optimiser, a-priori.** TBNN test `b_rms` below k-omega SST
on **>= 6 of the 8 TEST cases**, and below `b = 0` (B2) and the train-mean tensor (B3) on
**>= 6 of 8**. The split is the CPU lane's frozen split (`../PREREGISTRATION.md` §6), with
the same `assert_disjoint()` printed verbatim. Inside → **PASS**; 4 or 5 of 8 →
**GATE FAIL**; <= 3 of 8, or failure to beat `b = 0` anywhere → **NOT A RESULT**.

**G2 — ARM-A, the invariance embedding.** TBNN mean pooled test `b_rms` below the plain
MLP's by more than the seed spread (max-minus-min over 5 seeds), **both** pooled and with
the pooled figure reported beside the per-case reading, because the CPU lane's (iii)
failed **only** on the pooled metric, by seven orders of magnitude on one case
(`../RESULTS.md` §4b). Met → **PASS**; not met → **GATE FAIL**. *Registered in advance:
if G1 passes and G2 fails, that is again **GATE REACHED**, and it will be reported as a
reproduction of the CPU lane's result under a faithful optimiser, not as a new finding.*

**G3 — realisability. This is the gate the CPU lane's preregistration did not have, and
Charter §4 exists because of that hole.** Wording taken verbatim from Charter §4:

> **NOT A RESULT** if the predicted `b` is non-realisable in more than **3x** the truth's
> own violation fraction on the same cells, or if `max ||b||_F` exceeds `sqrt(2/3)` by more
> than a factor of **2**, regardless of RMSE.

The truth's own violation fraction on these cells is **0.79%**, SST's is **0.10%**
(`../RESULTS.md` §0), so the threshold is **2.37%**, and `sqrt(2/3) = 0.8165` so the norm
threshold is **1.633**. The CPU lane's TBNN measured **6.47-15.34%** and `||b||_F ~
1.48e+07`: **applied to that run this gate fires NOT A RESULT**, and it is registered here
knowing that.

**G4 — a-posteriori, and it runs on CPU.** Charter §2: an a-priori score alone is **NOT A
RESULT**. The trained `b` from the best ARM-A/ARM-B seed is propagated through
`simpleFoam` (OpenFOAM v2606, `/usr/lib/openfoam/openfoam2606`) on the 8 TEST cases,
scored against the LES fields, with RMS `div(U)` reported (Charter §7, floor 10.5%).
Velocity error below the frozen-field ceiling on **>= 6 of 8** → **PASS**; 4-5 → **GATE
FAIL**; <= 3, or non-convergence on more than 2 cases → **NOT A RESULT**.

**Capped verdict if G4 is not run: GATE REACHED, and no higher.** This item is the **only
one of the five** whose a-posteriori gate is reachable on artefacts already on disk, and
therefore the only one that can reach **PASS**.

**Charter §22.4:** every prediction reported under G4 ships its shelf-D model-form band,
with the axis the band cannot see named, and the band is never applied as a correction.

## 9. Planted-zero control

**What is planted.** `PLANT = 1.234e-03` (the lab's standing constant — `analyse_t3.py`,
`analyse_t10a.py`, R5C G0), added to the `b_LES[k, 0, 1]` and `b_LES[k, 1, 0]` entries of a
named, recorded cell index `k` in a **copy** of `dataset.npz`, before the scorer reads it.

**How it is read back.** The scorer computes `b_rms` on the planted copy and on the clean
copy. The difference must be non-zero and must reproduce the plant to within 1e-9 relative
when back-solved through the known single-cell contribution to the RMS.

**Refusal rule.** If the scorer returns a difference of exactly zero, or a difference that
does not back-solve to `1.234e-03` within 1e-9 relative, the comparator **exits 2 and
refuses to emit a verdict**. A zero from a reader not shown able to see a non-zero is not
evidence (`CLAUDE.md` rule 3). The arm's verdict is then **NOT A RESULT**.

**A second plant, on the realisability reader**, because G3 is a gate now: a cell is forced
to `b = diag(1, 1, -2)` (`||b||_F = 2.449`, far outside the barycentric triangle) and
`realisability_violation()` must flag it. If it does not, G3 is **NOT A RESULT**.

## 10. Falsifier, pre-stated

**If ARM-A, at Ling's own SGD learning rates and a 200,000-epoch budget, produces a TBNN
whose pooled test `b_rms` is not better than the CPU lane's Adam-trained TBNN by more than
the seed spread, then departure D3 is not the reason the CPU lane fell short of the
paper**, and the claim that "the optimiser is the most likely place a faithful reproduction
would differ" (`../RESULTS.md` D3) is **falsified**. That is the finding and it is reported
as such, whichever way it goes.

**Second falsifier, on ARM-B:** if the Bayesian search selects an architecture materially
different from 8x30 (more than 2 layers or more than 10 nodes away) **and** that
architecture scores better than 8x30 on validation by more than the seed spread, then the
paper's stated architecture is not the optimum of its own stated procedure **on this data**,
and the VARIANT label absorbs the difference rather than the paper being contradicted.

## 11. The CPU question, answered with arithmetic

**Can this run on CPU at all, in reasonable time, on this `c7a.4xlarge` (16 cores,
$0.0513/core-h — owner-stated, `CLAUDE.md` rule 12)?**

Using the measured 0.78-1.50 s/epoch at 4 threads (§6):

| arm | wall-h at 4 threads | core-h (x4 threads) | CPU cost |
|---|---|---|---|
| **ARM-B** (100 trials x 3 seeds x 400 ep) | 26.0 - 50.0 | **104.0 - 200.0** | **$5.34 - $10.26** |
| **ARM-A** (5 seeds x 200,000 ep) | 216.7 - 416.7 | **866.8 - 1,666.8** | **$44.47 - $85.51** |
| **ARM-C / G4** (8 propagations at R4's measured 0.259 core-h/case) | — | **2.07** | **$0.11** |

**Answer, split, because the two arms answer differently:**

* **ARM-B is CPU-feasible.** 104-200 core-h is under Charter §18's 487-core-hour
  pre-authorisation and costs **$5.34-$10.26**. It needs no GPU at all, and saying so is
  part of this file's job.
* **ARM-A is NOT CPU-feasible as registered.** 867-1,667 core-h **exceeds Charter §18's
  487** and would occupy 4 of the box's 16 cores for **9 to 17 days** while the thermal and
  dafoam lanes need them. Under §18 the response is "stop and cost it", which is what this
  line is.
* **ARM-C (G4) is CPU work by nature** and costs **$0.11**. It is not a GPU item and is
  registered here only because Charter §2 requires the a-posteriori gate to exist.

**So the honest GPU case for this item is ARM-A alone**, and Sanaa should be told that
ARM-B can be run on CPU today under the existing blanket for about six dollars.

## 12. What this lane cannot see

* **It cannot see a price.** This box cannot read its own billing
  (`COMPUTE_BUDGET_CHARTER` §5). Every GPU figure here is in GPU-hours and carries no
  dollar amount by design. The CPU dollars above are owner-stated, not measured.
* **It cannot see the GPU memory of any instance class.** Written "to be read" throughout.
  `GPU_CAPABILITY_STATE.md` §3's per-class column is that document's own recall and is not
  treated as a measurement here.
* **It cannot see whether 200,000 epochs is enough.** That number is this lane's
  assumption and it sets the whole cost. A pilot of 5,000 epochs at 2.5e-7 on CPU would
  measure the loss slope for under an hour and would replace the assumption with a
  measurement — **and that pilot has not been run.**
* **It cannot see the throughput of a GPU it has never touched.** The 5-20x factor is an
  assumption with the 1x floor written down beside it, not a benchmark.
* **It cannot see which of the lab's two "measured" epoch rates is right** (0.78 vs
  1.50 s/epoch, §6). Both are in the range.
* **It cannot see whether G4 will converge.** `../RESULTS.md` §10 predicts that a field
  non-realisable on 6-15% of cells "would very likely diverge" if propagated. G3 exists to
  stop that reaching a verdict, but a G3 pass does not guarantee a G4 convergence.
* **It cannot see Ling's own flows.** The VARIANT label stands and 0.13 remains
  uncomparable.
* **It cannot see three dimensions.** Pope's basis has per-cell rank 3.006-3.987 by case
  mean on this benchmark, never above 5 (`FEASIBILITY.md` F2), so nothing here tests the
  claim that ten tensors are what tensor-basis methods need.
* **It cannot authorise itself.** No agent message is Sanaa's consent (`CLAUDE.md` rule 9).

## 13. Departures carried forward from the CPU lane

D1 (flows), D2 (`eps = beta* k omega`, `beta*` = 0.09), D4 (signed-`log1p` input scaling),
D5 (basis RMS rescaling) and the undocumented `LeakyReLU(0.01)` choice are **carried
forward unchanged** from `../RESULTS.md` §8. **D3 is the departure this arm removes.**
D6 (a-priori only) is removed by G4.

---

## 14. Supervisor addition, dated 2026-08-23 (stamp alignment + cost estimate line)

Added by the re-formed closure supervisor after the GPU-PLAN lane that wrote
§1–§13 was killed by the session limit. Nothing above this line was changed
except the first STATUS line, which now carries the canonical
**DRAFT — NOT FILED, NOT LAUNCHED** stamp; no gate, arm, range or cap moved.

**Cost estimate line: 12–52 GPU-h × ~$0.80/GPU-h (g6.xlarge on-demand, agent
recall, NOT a record) ≈ $10–$42 — estimate — needs console confirmation.**
The signed file's `cost_basis` must carry the console-read price
(`docs/GPU_CAPABILITY_STATE.md` §6); §6–§7 above remain the registered
GPU-hour arithmetic and cap (60 GPU-h).
