# B3 — decomposition disclosure for the CBFS PCLU adjoint: RESULTS

**Written 2026-08-21 ~20:0x UTC, DAFoam team Lane B**, scoring the arms against
`PREREGISTRATION.md` in this directory, which was frozen before any arm ran. Run root
`/home/ubuntu/certonomous-runs/B3-decomposition-np4/`. Image `dafoam-subpclu:v2`
(`8352629516bb`) as registered, `DAFOAM_SUBPC_TYPE=lu`, `--cpuset-cpus 0-3`, `--memory=12g`,
every arm foreground and `timeout`-bounded, beta DV (21,000), fresh staged case per arm, cold
`rm -rf processor*`.

**Nothing here is filed, sent, uploaded or pushed. Filing stays NOT APPROVED and is Sanaa's alone.**

---

## 1. Headline

**The registered prediction was that this item would find nothing, and it finds nothing —
to the exact order of magnitude the reach matrix predicted.** All three partitionings converge
(`reason 2`) and their gradients agree with the **serial** reference to **1.1–1.7 x 10⁻⁴**:

| graded row | quantity | measured | as % | PASS band | verdict |
|---|---|---|---|---|---|
| **G1** | `‖g_scotch − g_serial‖ / ‖g_serial‖` | **1.680861e-04** | 0.01681 % | < 1e-3 | **PASS** |
| **G2** | `‖g_simple − g_serial‖ / ‖g_serial‖` | **1.415579e-04** | 0.01416 % | < 1e-3 | **PASS** |
| **G3** | `‖g_simple − g_scotch‖ / ‖g_scotch‖` | **1.132033e-04** | 0.01132 % | < 1e-3 | **PASS** |
| **G4** | objective bit-identical, all three arms | **not bit-identical** — see §4 | spread **1.9e-07** | bit-identical | **GATE FAIL** |
| **G5** | sub-LU banner present, all three arms | present in all three | — | present | **PASS** |

`PRIOR_WORK_INVENTORY.md` §2's defect **D-B** reach row lists **CBFS (21,000)** in the
**CLEAN** column, *"all invariant at ~1e-04."* **Measured: 1.13e-04, 1.42e-04, 1.68e-04.**
The prediction is confirmed on its own stated scale.

**Why that matters despite finding nothing.** Every B3 number this lab holds was measured at
np = 4 under `scotch`, and `DAFOAM_CHARTER.md` §5 forbids carrying an FD reference across `np`
and requires the decomposition to be disclosed. **The whole S1 line rests on gradients measured
under one partitioner, and until now nothing had varied it on this case.** It now has, against
the serial reference the charter names, and the S1 gradients do not inherit a decomposition
defect. **The value is in the disclosure, not the discovery — as registered.**

**And the contrast with A4 is the point.** Same lab, same defect class, one partitioner
changed: A4's gradient moved **8.95 % (`scotch`) → 0.00054 % (`simple` 4×1×1)**, np-dependent
as well (np=2 **0.26 %**, np=3 **6.05 %**). **CBFS moves 0.0113 %.** The defect is real and it
is *case-selective*; CBFS is on the clean side of the reach matrix and now has the measurement
that says so rather than the inference.

## 2. Per-arm table

| arm | np | decomposition | reason | iterations | primal | cold-start continuity | iteration-0 residual | objective | `‖g‖` (serial order) | wall s | core-min |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **D-serial** — **the reference** | **1** | none; one block over the whole 210,592² operator | **2** | **163** | `Time = 1584` | `1.12896526821488e-05` | `7.091589775454e-04` | `1.5279275989724403e-02` | `1.4557054356e-05` | 1266 | 21.10 |
| **D-scotch** — on the record, **not re-run** | 4 | `scotch` (as shipped) | **2** | **667** | `Time = 1580` | `9.30211816115683e-06` | `7.091590452305e-04` | `1.5279278906359758e-02` | `1.4558046603e-05` | 414 | 27.60 |
| **D-simple** | 4 | `simple`, `n (4 1 1)` | **2** | **766** | `Time = 1582` | `1.19187582101953e-05` | `7.091590381747e-04` | `1.5279278602317540e-02` | `1.4558490322e-05` | 301 | 20.07 |

Cites: `logs/D_serial.log:11899` (banner), `:11914` (reason); `logs/D_simple2.log:12095`,
`:12116`; D-scotch is arm Pβ, `../adjoint_unblock_reproduce/logs/arm_Pbeta.log:12047`, `:12067`.
Gradient min/max in serial order: D-serial `-4.694385e-07 / 1.915505e-06`, D-scotch
`-4.6943669e-07 / 1.9160188e-06`, D-simple `-4.6942978e-07 / 1.9159898e-06`.

**Each arm's decomposition is asserted from its own run, not from its launch command.**
D-simple's `system/decomposeParDict` as DAFoam itself wrote it reads `numberOfSubdomains 4;`,
`method simple;`, `n (4 1 1);`, and the three arms' **cold-start continuity errors differ**
(`9.30e-06` / `1.19e-05` / `1.13e-05`) — the primal really did partition differently. **An arm
whose cold start matched the scotch reference would be an arm that silently ran scotch, and
§6 is where that actually happened.**

## 3. Prediction vs measured

| arm | registered prediction | measured | hit? |
|---|---|---|---|
| **D-simple** | `reason 2` | `reason 2` | **HIT** |
| **D-simple** | iterations **not** 667, band **400–1000**; *"a different count is expected and is not a finding"* | **766** | **HIT** — and the count did move, as registered |
| **D-simple** | `‖g_simple − g_scotch‖/‖g_scotch‖ < 1e-3` | **1.132033e-04** | **HIT** |
| **D-serial** | `reason 2` — *"the arm that could go either way"* | `reason 2` | **HIT** |
| **D-serial** | iterations **fewer than 667**, band **50–500**, *"because the block-boundary approximation is gone"* | **163** | **HIT**, and the stated mechanism is vindicated: removing the ASM block boundaries cut the Krylov count **4.09×** |
| **G1/G2** | < 1e-3 against the serial reference | 1.68e-04 / 1.42e-04 | **HIT** |
| **G4** | objective **bit-identical** across all three arms | **spread 1.9e-07 — not bit-identical** | **MISS** (§4) |
| **memory, D-serial** | **10–14 GiB, may not fit the 12 GiB cap** | sampled **6.156 GiB** mid-solve, never near the cap; no OOM | **MISS**, in the safe direction (§5) |

**Six registered rows hit, two missed, and both misses are recorded rather than reconciled.**

## 4. G4 — the registered gate that fails, and why the *gate* was wrong rather than the runs

The three objectives:

| arm | `OBJ varianceU` | relative to D-serial |
|---|---|---|
| D-serial | `1.5279275989724403e-02` | — |
| D-scotch | `1.5279278906359758e-02` | **1.9089e-07** |
| D-simple | `1.5279278602317540e-02` | **1.7099e-07** |
| *(simple vs scotch)* | | *1.9899e-08* |

**Verdict: GATE FAIL, as the gate was literally written**, and it is reported that way because
the gate was registered that way. But the honest reading of the number is that **the
pre-registration's reasoning was right about the ASM and wrong about `np`.** Its parenthetical
was *"(the primal does not see the ASM)"* — true, and irrelevant here. What changed between
these arms is not only the ASM: it is the **whole primal parallel linear algebra**. Reduction
order, `GAMG` coarsening and `DILUPBiCG` all depend on the partition, and **the primal stops on
a residual tolerance (`1e-06`), not at a fixed point.** The three arms stop at **1580 / 1582 /
1584 iterations** on three slightly different trajectories, so their converged states differ by
reconvergence noise.

**1.9e-07 is roughly three orders of magnitude below the 1e-04 at which the graded gradient
rows sit, and four below their PASS band.** It is not evidence that the primal changed in any
way an ASM choice could cause — which is what G4 was written to catch, and G4 would still catch
it. **The gate should have been "bit-identical between the two np = 4 arms, and within
reconvergence noise of the np = 1 arm."** Between the two np = 4 arms the spread is
**1.99e-08**, still not bit-identical, because `simple` and `scotch` are also two different
parallel reduction trees.

**This is registered as a miss and the gate is not retroactively rewritten.** The correction is
recorded here for the next preregistration that compares objectives across `np`:
**"bit-identical" is only ever a defensible gate between runs that share a decomposition** —
`../adjoint_unblock_reproduce/` arms S/R/P/K share one, which is why bit-identity is the right
gate *there* and the wrong gate *here*.

## 5. Memory — the registered envelope, and the miss

| arm | predicted (prereg §4) | measured |
|---|---|---|
| D-simple, np=4 | 8–10 GiB | inside the cap; no OOM |
| **D-serial, np=1** | **10–14 GiB — may not fit the 12 GiB cap** | **6.156 GiB sampled mid-solve**, no OOM, `rc=0` |

**The prediction missed high, and the arm that was registered as the one at risk was never at
risk.** The basis was `PROOF.md` §25.3's `nnz(L+U)` = 3.22e+08–3.90e+08 for an offline `splu`
of the whole matrix. In-solver, `PCLU` on a single ASM block is **not** that object: the
serial arm still runs ASM with one block and PETSc's own `MATSOLVERPETSC` LU, whose fill on
this matrix is evidently far below SuperLU's, and the 1000-vector GMRES restart basis was never
allocated in full because the solve converged in **163** iterations.

**Disclosure on the figure itself:** 6.156 GiB is a **`docker stats` sample taken during the
linear solve**, not a true peak — no per-arm high-water mark was recorded, because the chain
did not carry the 5 s memory watcher the ILU-shift chain used. **The honest statement is that
the cap was never approached at any moment observed, not that the peak was 6.156 GiB.** That
the arm registered as most likely to OOM finished with `rc=0` in 1266 s is the load-bearing
fact; the exact peak is **NOT MEASURED**.

## 6. Two harness failures, both caught, both recorded — and the first is a real trap

**Neither cost a graded number; both cost core-minutes, and both are in §7's total.**

### 6a. `system/decomposeParDict` is overwritten by DAFoam at startup — editing it does nothing

The first D-simple arm was staged by rewriting `system/decomposeParDict` to `method simple;`
`n (4 1 1);` — the obvious way, and **it has no effect.** The arm returned `reason 2`, **667**
iterations, objective `1.5279278906359758e-02` and gradient `1.4558046603e-05` — **bit-identical
to D-scotch in every digit** — and its `system/decomposeParDict`, read back afterwards, said
`method scotch; n (2 2 1);`.

**Mechanism, read from the installed source:** `pyDAFoam._writeDecomposeParDict()`
(`pyDAFoam.py:2212`, called from `:1463`) **writes `system/decomposeParDict` from
`daOptions["decomposeParDict"]`** on every run, whose default is
`{"method": "scotch", "simpleCoeffs": {"n": [2,2,1], …}}`. The comment above the option says so
plainly: *"This file will be automatically written such that users can run optimization with
any number of CPU cores without the need to manually change decomposeParDict."*

**The correct channel is `daOptions`**, and the re-run sets it there and prints
`T3 DECOMP OVERRIDE: simple [4, 1, 1]` from inside the run script before the solver starts.
**That arm is `D_simple2` and is the only `simple` arm graded above.** The void arm is retained
as `D_simple_VOID_ranscotch/` and `logs/D_simple_VOID_ranscotch.log`.

> **The generalisable trap: a partitioner set by editing `system/decomposeParDict` is silently
> ignored, and the run looks completely healthy while measuring the default.** The only tell is
> that the answer comes back bit-identical to the `scotch` arm — which, on a case where the
> registered prediction is *"invariant"*, is exactly the answer that would have been believed.
> **This item could have reported a false PASS on G3 and never known.** What caught it was
> reading the decomposition back out of the arm's own directory afterwards, which is now
> recorded as a standing check in §2.

### 6b. `dRdWColoring_4.bin` is keyed on rank count, not on partitioner

The corrected arm's first attempt reused the `dRdWColoring_4.bin` staged from the `scotch` arm
and **aborted 78 s in**:

```
Reading Coloring dRdWColoring_4
Validating Coloring...
--> FOAM FATAL ERROR: (openfoam-2506)
 row: 105370 col1: 52784 col2: 52785 color: 0
    From Conflicting Colors Found!
    in file DAColoring/DAColoring.C at line 1021.
```

The coloring file name encodes only the **number of ranks**, so DAFoam happily loads a coloring
computed for a different partitioning of the same rank count. **Unlike 6a, this one fails
loudly**: `DAColoring.C:1021` validates the coloring against the actual sparsity and aborts
rather than returning a wrong Jacobian. **That is a robustness credit to DAFoam and is worth
saying alongside the defects this lab has filed against it.** The fix is to delete
`dRdWColoring_*.bin` whenever the decomposition changes; the graded arm regenerated it.

## 7. Cost

| arm | wall s | ranks | core-min | status |
|---|---|---|---|---|
| `D_serial` | 1266 | 1 | **21.10** | graded |
| `D_simple2` (fresh coloring) | 301 | 4 | **20.07** | graded |
| *`D_simple` — ran `scotch`, §6a* | *350* | *4* | *23.33* | **waste** |
| *`D_simple2` attempt 1 — stale coloring, §6b* | *78* | *4* | *5.20* | **waste** |
| **graded compute** | | | **41.17** | vs registered **45.0** — **8.5 % under** |
| **total charged** | | | **69.70** | **58.1 % of the 120 core-min ceiling** |

**69.70 core-min = 1.1617 core-h × \$0.0513 = \$0.0596.** Nothing approaches \$25 and nothing
goes on a Sanaa list. **28.53 core-min (40.9 %) is waste**, both attributable to §6, and it is
reported as waste rather than folded into the graded figure. D-scotch's 27.60 core-min is not
counted here — it was bought by `../adjoint_unblock_reproduce/` and is re-used, not re-run,
exactly as the pre-registration specified.

**Against the registered per-arm estimates:** D-simple registered ~300 s / 20.0 core-min and
measured **301 s / 20.07** — the closest cost prediction this lane has made. D-serial registered
~1,500 s / 25.0 and measured **1,266 s / 21.10**, 16 % under.

## 8. The ordering trap, and the check that it was avoided

`PREREGISTRATION.md` §3 names one failure mode as *"the single most likely way to get this item
wrong"*: the beta DV index is a **distributed** ordering, so comparing two differently-permuted
21,000-vectors would **manufacture** a defect. Every np = 4 gradient here is mapped to serial
cell order **before any norm is taken**, through the concatenated
`processor*/constant/polyMesh/cellProcAddressing` in rank order; the np = 1 arm needs no
mapping. `analyse_decomp.py` **asserts the permutation is a bijection onto `0..20999`** for each
arm and refuses to proceed otherwise.

**Validation that the mapping is the right one:** applied to arm Pβ's archived gradient it
reproduces `‖g‖ = 1.4558046603291625e-05`, `min = -4.6943669178503126e-07`,
`max = 1.9160188133304114e-06` — every archived digit.

**The scale of the trap, measured rather than asserted.** The unmapped D-simple gradient
differs from the mapped one in **20,930 of 21,000 positions**, and scoring **G2** without the
mapping returns:

| G2, `‖g_simple − g_serial‖ / ‖g_serial‖` | value | what it would have been called |
|---|---|---|
| **unmapped** — the mistake | **1.412254e+00** = **141.2 %** | **GATE FAIL** by four orders of magnitude; *"CBFS leaves the CLEAN column and every S1 gradient inherits the finding"* |
| **mapped** — correct | **1.415579e-04** = **0.01416 %** | **PASS** |

**A factor of 9,977 between the right answer and the wrong one, and the wrong one is a
headline-grade false positive** that would have contradicted the reach matrix, re-opened defect
D-B on a clean case, and put a cloud over the entire S1 line. The pre-registration named this
failure mode in advance and it is the reason the assertion is in the script rather than in a
reviewer's head.

## 9. What this item cannot establish

- Nothing about **closure physics** — same 0.72-uniform inlet defect, same 27 % bulk mismatch.
- Nothing about **FD**. This item compares gradients to **each other**, never to finite
  differences. **A gradient that is decomposition-invariant can still be uniformly wrong, and
  A4 is the proof**: its `simple` arm agrees with FD to 0.00054 % while its `scotch` arm
  converges the KSP to true-residual 1.7e-07 on an operator **328.8× ‖b‖** away from the
  transpose Jacobian. **Invariance is necessary, never sufficient**, and nothing here upgrades
  the CBFS gradient's standing against FD.
- Nothing about **other partitionings** — `kahip`, `hierarchical`, or `simple` in the other two
  axes. A4 measured `1x4x1` at 0.47 % and `1x1x4` at 0.52 % against `4x1x1`'s 0.00054 %, so the
  subdivision matters as much as the method. Only `4x1x1` was bought.
- Nothing about **np other than 1 and 4.** A4's effect **peaked at np = 3**, which is not run
  here, so the CBFS reach conclusion is a two-point one.
- Nothing about **B3 Stage 4**, which stays **BLOCKED** under R11 whatever this item returns.
- **The true peak RSS of any arm** (§5).

## 10. Provenance

| number | where |
|---|---|
| ledger, all six rows incl. the two void arms | `/home/ubuntu/certonomous-runs/B3-decomposition-np4/ledger.csv` |
| graded arm logs | `…/logs/D_serial.log`, `…/logs/D_simple2.log` |
| void arm logs, retained | `…/logs/D_simple_VOID_ranscotch.log`, `…/logs/D_simple2_VOID_stalecoloring.log` |
| mapping + grading, and `grading.json` | `…/analyse_decomp.py`, `…/grading.json` |
| D-scotch reference (arm Pβ), not re-run | `../adjoint_unblock_reproduce/RESULTS.md` §1, `logs/arm_Pbeta.log` |
| DV→serial permutation convention, bijective to 5.1e-15 | `../../S1_CBFS_WEIGHTED_LOSS_VARIANT.md` §0b |
| CBFS in the CLEAN column of the D-B reach matrix | `docs/dafoam/PRIOR_WORK_INVENTORY.md` §2 |
| A4 partitioner precedent 8.95 % → 0.00054 % | `ladder-a/A4/README.md`, `W4-a4-decompcut` |
| `_writeDecomposeParDict` overwrite | in-image `pyDAFoam.py:1463`, `:2212` |
| coloring conflict abort | in-image `DAColoring/DAColoring.C:1021` |

**Nothing in this file was sent anywhere. Filing is Sanaa's call alone.**
