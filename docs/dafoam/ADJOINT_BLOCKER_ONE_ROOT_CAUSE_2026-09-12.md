# The 3D adjoint ladder has ONE blocker, and it is measured

**dafoam-supervisor, 2026-09-12, [lab-attributed].** Short by instruction.

## The finding

**Two independent 3D adjoint failures share one root cause: the primal plateaus
ABOVE its own accept floor, so no adjoint and no FD sample can ever be taken.**

| item | how it presented | measured cause |
|---|---|---|
| **D6R** (A2 MACH wing, 3D multipoint opt) | optimiser died at major 73 of `max_iter 80` — `EXIT: Invalid number in NLP function or derivative detected` | the primal it was differentiating could not converge |
| **D6RF3** (A2 FD verification, 3D) | `rc=1` after 17 × `AnalysisError: 'cl04.coupling.solver': Primal solution failed!` (`F_mp` log:2107) | cl04 primal at D6R's endpoint falls to **1.3162e-05 and freezes** (1.316351e-05 → 1.316218e-05 over 200 steps, `nIters: 1`) against a floor of **1.0e-05** = `primalMinResTol 1e-8 × primalMinResTolDiff 1e3` — **1.32× above its own floor** |
| **D6RF10** (A2 convergence probe) | GATE FAIL | same field, `DARhoSimpleFoam`, **1.681e-05, GATE FAIL, and PLATEAUED** (late-window spread 0.307 %) — which is the proof that **running longer cannot fix it** |

Every staging and instrument guard PASSED in D6RF3 (S1–S7, G-DELIVERY, G-ANCHOR,
G-COLD; undeformed reference mesh md5-matched on base and all three points; 78
entries counted on both sides of the copy, so it cannot have passed on a false zero).
**This is physics, not plumbing.**

## Why it matters more than any single run

The charter's bright line: **a DAFoam gradient is not a result until a
finite-difference table stands beside it at a step proved to lie in the plateau.**
A primal that cannot reach its accept floor takes **no FD sample**. So until this
clears, **no 3D gradient in this territory is a result** — which outranks any
individual optimisation run, D6R2 included.

## The fix, already measured — not a proposal

**D6RF10's R3**: `DARhoSimpleCFoam` (SIMPLEC), `nNonOrthogonalCorrectors 12`,
`relax_p 0.70` drives the same binding field to **6.323e-06** — below the 1.0e-05
floor and plateaued (late-window spread 1.47e-5 %), binding verdict **PASS**.

**REFUSED, and named so it is never quietly tried:** loosening `primalMinResTolDiff`
would clear the floor **by moving the floor**. That is the tolerance-equals-gate
defect (`CASE_PROTOCOL_CHARTER` §1), now the fourth time it has been refused in this
territory. The lane did not propose it; this clause exists so a successor does not.

## Cost, registered before any launch

- **Decisive probe** — re-run the cl04 primal at D6R's endpoint under the R3 config and
  read whether it clears 1.0e-05: **618 core-min, $0.53 derived not measured**.
  MEASURED basis: D6RF10's own R3 ledger row, 9,264 wall s × 4 ranks, same case, same
  config, cold start. No measurement exists for a restart from the converged endpoint,
  so the cold figure is registered rather than a guess priced.
- **Full FD table, only if the probe clears**: D6R registered `F_mp` at 231.2 core-min
  under SIMPLE; the MEASURED SIMPLEC per-step penalty is **37.2×** (0.008293 → 0.30880
  core-min/step, D6RF10 R1 vs R3 ledger rows) → **~8,600 core-min ≈ $7.35 derived**.
  **An estimate from a measured ratio, not a measurement**, and labelled as such.

**Registered prediction, before the probe runs:** it clears the floor. **If it does
not, the fix does not transfer across cases, and that is a larger finding than a pass.**

## The same shape one ladder over

A3GC's coarse level stalls for a different reason with an identical consequence: 16
wall-normal layers force r = 2.0880 and the primal freezes at 2.29e-05; the **same
surface** at 64 layers (AR1, this session) converged to **3.761793e-07**, reproducing
the validated anchor's 3.744179e-07 to 0.5 %. **Two ladders, two root causes, one
failure mode — the primal cannot converge as posed, so the adjoint never happens.**
Both now have a measured fix.
