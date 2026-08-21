# B3 — decomposition disclosure for the CBFS PCLU adjoint: PRE-REGISTRATION

**Written 2026-08-21, BEFORE any arm of this item ran.** DAFoam team Lane B, against the
supervisor's relay of Sanaa's 2026-08-21 approvals (item 4). Run root
`/home/ubuntu/certonomous-runs/B3-decomposition-np4/`. Cap **4 cores** (`--cpuset-cpus 0-3`),
`--memory=12g`, foreground and `timeout`-bounded, `MemAvailable >= 12 GiB` checked in a bounded
loop before each launch. **No background solver process; nothing needs killing. Nothing is
filed, sent, uploaded or pushed.**

---

## 1. Why this item exists

`DAFOAM_CHARTER.md` §5 now requires every parallel gradient to disclose its decomposition and
forbids carrying an FD reference across `np`. **Every B3 number this lab holds was measured at
np = 4 under `scotch`** — `system/decomposeParDict` reads `numberOfSubdomains 4; method scotch;`
— and that has never been varied on this case. A4 is why it matters: same mesh, same DV, one
partitioner changed, and the gradient moved from **8.95 %** (`scotch`) to **0.00054 %**
(`simple` 4x1x1) against FD, with the effect np-dependent as well (np=2 **0.26 %**, np=3
**6.05 %**).

**But CBFS is on the other side of that reach matrix, and the prediction must respect it.**
`docs/dafoam/PRIOR_WORK_INVENTORY.md` §2, defect **D-B** reach row: *"CLEAN: A1 (4,032),
A2 (38,304), A5 (4,800), **CBFS (21,000)**, naca0015 sail (63,920) — all invariant at
~1e-04."* **So the registered prediction is that this item finds nothing, and the value is in
the disclosure, not in the discovery.** A row that is predicted to confirm is still worth
buying here because the whole S1 line rests on gradients measured under one partitioner.

## 2. Arms, each with its prediction fixed now

Image `dafoam-subpclu:v2`, `DAFOAM_SUBPC_TYPE=lu`, task `compute_totals`, **beta DV (21,000)**,
fresh staged case copy per arm, cold `rm -rf processor*`, sub-LU banner asserted in every log.

| arm | np | `decomposeParDict` | prediction, fixed now |
|---|---|---|---|
| **D-scotch** — the reference already on the record | 4 | `scotch` (as shipped) | **Not re-run.** Arm Pβ of `adjoint_unblock_reproduce/`, measured 2026-08-21: `reason 2`, **667** iterations, `OBJ 1.5279278906359758e-02`, `‖g‖ 1.4558046603e-05`, `min -4.694367e-07`, `max 1.916019e-06` |
| **D-simple** | 4 | `simple`, `n (4 1 1)` | **`reason 2`.** Iteration count **not** predicted to be 667: ASM block boundaries move, so a different count is expected and is not a finding. Registered band **400–1000**. Objective **bit-identical** to `1.5279278906359758e-02` (the primal does not see the ASM). **Gradient agreement with D-scotch: `‖g_simple − g_scotch‖ / ‖g_scotch‖ < 1e-3`** |
| **D-serial** | **1** | n/a — single block over the whole 210,592² operator | **`reason 2`**, and this is the arm that could go either way. At np = 1 the ASM block **is** the whole matrix, so the preconditioner is a complete LU of `dRdWTPC` itself. `PROOF.md` §25.3 factored exactly that matrix offline with `scipy.sparse.linalg.splu` and it **solves at every pivot threshold** (residual 2.38e-10 / 6.41e-12 / 2.54e-12). Iterations predicted **fewer than 667**, band **50–500**, because the block-boundary approximation is gone and what remains is only the `dRdWTPC`-vs-`dRdWTMF` mismatch |

## 3. The gate, and which arm is the reference

**The reference is D-serial, not D-scotch.** `DAFOAM_CHARTER.md` §5 says the serial gradient is
what a parallel one is checked against, and the defect class D-B is defined as the parallel
operator differing from the serial one. **So the graded quantities are:**

| row | quantity | PASS | CONDITIONAL | FAIL |
|---|---|---|---|---|
| **G1** | `‖g_scotch − g_serial‖ / ‖g_serial‖` | **< 1e-3** | 1e-3 to 1e-2 | **> 1e-2** — CBFS leaves the CLEAN column of the reach matrix, and **every S1 gradient number inherits the finding** |
| **G2** | `‖g_simple − g_serial‖ / ‖g_serial‖` | **< 1e-3** | 1e-3 to 1e-2 | **> 1e-2** |
| **G3** | `‖g_simple − g_scotch‖ / ‖g_scotch‖` | **< 1e-3** | — | **> 1e-2** — a partitioner-dependent gradient on a case the reach matrix calls CLEAN |
| **G4** | objective, all three arms | **bit-identical** to `1.5279278906359758e-02` | — | any difference: the primal changed, which no ASM choice can do, and **that becomes the headline** |
| **G5** | sub-LU banner present, all three arms | present | — | absent: the arm ran stock and is void |

**Comparison is on the DV vector, and the DV vector is not in serial cell order.**
`S1_CBFS_WEIGHTED_LOSS_VARIANT.md` §0b established that the beta DV index is a distributed
ordering; the exact permutation is recoverable from the concatenated
`processor*/constant/polyMesh/cellProcAddressing` and was verified to **5.1e-15**. **Each arm's
gradient is mapped to serial cell order before any norm is taken**, and the np = 1 arm needs no
mapping. **A comparison of two differently-permuted vectors would manufacture a defect**, and
that is the single most likely way to get this item wrong.

## 4. Memory, predicted before the launch — and D-serial is the one at risk

`DAFOAM_CHARTER.md` §7 requires the envelope before the launch, not after the OOM.

| arm | basis | predicted peak RSS |
|---|---|---|
| D-simple, np = 4 | measured: **9.044 GiB** for D-scotch (`adjoint_unblock_reproduce/RESULTS.md` §6, container `priceless_jepsen`). Block sizes are comparable under `simple` 4x1x1 | **8–10 GiB**, inside the 12 GiB cap |
| **D-serial, np = 1** | complete LU of the **whole** matrix. `PROOF.md` §25.3 measured `nnz(L+U)` = **3.22e+08 to 3.90e+08** for exactly this factorization, i.e. **24–28x the matrix's own 13,710,468 nonzeros**, *"roughly 3 GB on a 21,000-cell case"*. Add ~12 bytes per stored entry, factorization workspace, and a 1000-vector GMRES restart basis at 210,592 x 8 B = 1.7 GB | **10–14 GiB — this may not fit the 12 GiB cap** |

**Registered in advance: if D-serial dies on memory, that is recorded as stopped by memory and
is `NOT A RESULT` about convergence** (charter §7, and L-15's warning in the other direction).
It is **not** re-run at a larger cap inside this item; a larger cap is a new registration with
its own price. **The prediction is what makes that verdict honest, and it is written down here
before the run.**

## 5. Cost, registered before the runs

| arm | basis | est. wall | est. core-min |
|---|---|---|---|
| D-simple, np = 4 | arm Pβ measured 414 s under load, 246 s registered | ~300 s | **20.0** |
| D-serial, np = 1 | arm N1's serial primal took 433 s; add a whole-matrix LU factorization and a longer Krylov solve | ~1,500 s (1 core) | **25.0** |
| **total** | | **~30 min** | **45.0** |

**45 core-min against the 120 core-min ceiling = 0.75 core-h x \$0.0513 = \$0.038.** Nothing
here approaches \$25 and nothing goes on a Sanaa list. Each arm is `timeout 2100`-bounded, and
D-serial carries `timeout 2400` because its factorization has no measured precedent in-solver.

## 6. What this item cannot establish

- Nothing about **closure physics** — same 0.72-uniform inlet defect, same 27 % bulk mismatch.
- Nothing about **FD**. This item compares gradients to each other, not to finite differences.
  A gradient that is decomposition-invariant can still be uniformly wrong, and **A4 is the
  proof**: its `simple` arm agrees with FD to 0.00054 % while its `scotch` arm converges the
  KSP to true-residual 1.7e-07 on an operator **328.8x ‖b‖** away from the transpose Jacobian.
  **Invariance is a necessary condition, never a sufficient one.**
- Nothing about **other partitionings** — `kahip`, `hierarchical`, or `simple` in the other two
  axes. A4 measured `1x4x1` at 0.47 % and `1x1x4` at 0.52 % against `4x1x1`'s 0.00054 %, so the
  subdivision matters as much as the method; only `4x1x1` is bought here.
- Nothing about **np other than 1 and 4**. A4's effect peaked at np = 3, which is not run here.

*Nothing below this line existed when this file was written. The arms launch only after it lands.*
