# A3GC-L2 — DATED REPAIR ADDENDUM, 2026-09-12

**Appended record. Amends no gate, no threshold, no cap and no label. SUBMISSIONS PARKED.**

## 1. WHAT I STOPPED, EXACTLY

Sanaa ruled L2 gets **fixed, not run out**. It was a certain `NOT A RESULT`: at Time 1200/6000
with `p` asymptoted at ~1.0e-03 against a 1e-06 gate and ~22 h still to run.

Stopped by **exact container id `97f9b1c7ccfd823a1de985679da214e90381cbaf6f016bd8cd75247aa352b6aa`**
(`/hopeful_engelbart`), whose `State.Pid` was asserted **== 2467121** before the stop. **No pattern
match was used.** The four sibling containers and the A3GC L1 stage-1 mesh job (pid 2656601) were
verified alive **before and after**; all five survived.

**WASTE: 21,873 wall s x 8 ranks = 2,916.4 core-minutes, written off.**
This is **waste**. It is **not** folded into any actual/predicted ratio (budget charter §6).

Nothing was recoverable in place: `writeInterval` is 2000 and the run was at step 1200, so
**no time directory had ever been written** — `processor0/` held only `0` and `constant`.

## 2. THE DIAGNOSIS — THE LEADING HYPOTHESIS IS CONFIRMED, AND ITS STORY IS NOT THE ONE EXPECTED

**Confirmed on disk.** `A3GC-L2/system/fvSolution:19-21` runs `nNonOrthogonalCorrectors 0`,
against a mesh measuring (`A3GC-L2/meshgen/logCheckMesh.txt:96,97,103`):

- **max non-orthogonality 72.07°**, **241 faces severely non-orthogonal (> 70°)**,
- 586 low-quality tet faces, 110,979 small-determinant cells, **Failed 2 mesh checks**,

while `system/fvSchemes:53,58` ask for `Gauss linear corrected` / `snGrad corrected` — **an
explicit non-orthogonal correction that is never iterated.** DAFoam's own `DACheckMesh` threshold
prints as **`maxNonOrth: 70`**, so L2 is past the solver's own limit, not merely past a guideline.

**A second, independent lever, measured:** L2's GAMG pressure solve **terminates on `relTol 0.1`
in 103 of its last 200 steps** at 15-17 iterations, where L3 is relTol-limited in **0** of 200.
The reader that returns 103/200 on L2 returns 0/200 on L3, so the non-zero control is live.

**Which lever is primary, stated honestly:** leftover linear error is ~9.5 % of `initRes`, so
tightening `relTol` alone can buy about one part in ten — **it cannot explain a three-decade
shortfall.** The **non-orthogonal correction is the primary lever; `relTol` is secondary.**

## 3. THE GROWTH RATIO DOES NOT EXPLAIN L2, AND I WILL NOT PRETEND IT DOES

| level | growth ratio r | max non-orth | outcome |
|---|---|---|---|
| AR1 | 1.1674 | **61.16°** | converges |
| L3 | 2.0880 | **61.16°** | stalls at 2.29e-05 |
| L2 | 1.4006 | **72.07°** | stalls at 1.0e-03 |

**Not monotone in r** — L2's r sits *between* the other two. And **max non-orthogonality does not
separate AR1 from L3 either**: those two are identical to five decimals (61.15806658877255) yet
behave differently. What is true of L2 and of **nothing else** is that it is the **only level past
70°**, with 241 severely non-orthogonal faces against **zero non-orthogonal correctors**.

**The evidence points at mesh quality plus zero correctors, not at r.** The deeper cause — A3GC
§2.6 holds `s0` fixed while refining the surface, so aspect ratio and non-orthogonality grow at
every level by construction — is already recorded in `A3GC_P_STALL_MESH_CONDITIONING_EVIDENCE.md`
and is a **registration-level** question, not a numerics knob.

## 4. THE RESTART IS BLOCKED ON A GRADING-PATH DEFECT — AND THAT IS NOT A DETAIL

The obvious repair (`nNonOrthogonalCorrectors` > 0, ported from A2 D6RF10 where 3 GATE FAILed and
12 PASSed) **cannot be graded by the frozen comparator**, and would silently produce a **spurious
PASS**.

`DAUtility::primalResidualControl` is called **inside** `while (simple.correctNonOrthogonal())`
(`pEqnSimple.H:41,52`) and prints one `p initRes:` line **per corrector**. The comparator's
`read_log` walks the last `Time =` block and keeps the **last** match (`a3gc_grade.py:695-702`),
which with correctors on is the **final corrector's** residual — measured from an almost-solved
field — not the outer residual.

**Demonstrated with a planted control rather than asserted.** Fed a synthetic final block whose
true outer value is `p initRes 1.000000e-03`, followed by correctors at 5.5e-05 and a planted
**1.234e-09**, the comparator's own regex returns **1.234e-09**: the plant is read back, and the
1e-06 gate reads *PASS-looking* on a residual that is truly 1.0e-03. The **same reader** returns
the honest 1.000000e-03 from a single-corrector block, so it is shown able to return **both**
answers. L2's current log carries exactly **1** `p initRes:` line per step, which is why the
defect has never yet fired.

**Turning on the fix without ruling on this would convert a certain `NOT A RESULT` into a false
`PASS`.** I did not do it.

## 5. WHAT IS OWED, AND BY WHOM

**`PENDING`** — L2's repaired re-run is **registered as not yet launched**, awaiting a
**supervisor ruling on the grading path**, which is check 4 and is not this lane's to take:

1. amend the comparator to read the **first** `initRes` match per equation per block (the outer
   residual) or the **max** across correctors — a grading-path change that must be committed
   **before** the repaired run starts; **or**
2. rule the defect out of scope and register a repair that leaves `nNonOrthogonalCorrectors` at 0
   — which §2 measures as **unable** to close a three-decade gap.

The repair package is otherwise ready: fresh root, mesh byte-identical to L2, `fvSolution` the
only diff, `np`=8 for parity with L2's decomposition, **no cap of any kind**, memory containment
retained. **Ranks are free: L2's 8 were released by the stop in §1.**

Not registered, not frozen, and **no compute spent** on it.
