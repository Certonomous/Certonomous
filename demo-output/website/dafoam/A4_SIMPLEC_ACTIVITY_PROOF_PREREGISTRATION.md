# L-40 activity proof for `consistent` (SIMPLEC) in DASimpleFoam: PRE-REGISTRATION

Filed 2026-08-10. **~2 core-min, under the ~10 threshold, so executed without a ruling** — but
pre-registered because it hardens a retraction that is currently being routed upstream.
Committed BEFORE compute.

## 1. Why this, and why now

The FD-2 refutation (`35a91e0e`) retracted A4's stated cause for its 22.05% cross-code gap on the
grounds that **`DASimpleFoam` honours `consistent yes`**. That retraction is being routed to the
defect report's author. It currently rests on two *inferential* legs, both verified today:

1. **The source honours it** — `pEqnSimple.H:27` and `DAResidualSimpleFoam.C:189` both gate the
   textbook SIMPLEC correction on `simple.consistent()`, in both images.
2. **The case sets it** — A4's own DAFoam cases (`A4-ahmed-body/{fine,coarse}/system/fvSolution`)
   read `consistent yes;`, checked today.

**Neither leg proves the switch RAN.** That is exactly the L-40 gap this lab has spent the
campaign closing — "configuration survives; activity does not" — and it would be inconsistent to
route a retraction upstream while its central claim rests on a source read plus a config read,
the same evidence class the original wrong verdict rested on.

## 2. The instrument, and why it is the sharpest available

Case: **A1 NACA0012, 4,032 cells, `DASimpleFoam`, `primalMinResTol 1e-8`** — the family's
cheapest incompressible case, whose archived `fvSolution` sets `consistent false;` explicitly, so
the control is the shipped configuration unmodified. Image: **`dafoam-subpclu:v1` with
`DAFOAM_SUBPC_TYPE` unset** — the shipped-behaviour lineage, because the claim under test is
about shipped DAFoam, **not** the locally patched build.

Two primal-only runs (`-task run_model`), identical but for one token in
`system/fvSolution`: `consistent false` → `consistent true`.

**Graded on iteration count to `primalMinResTol`.** SIMPLE and SIMPLEC solve the same discrete
equations by different pressure-velocity coupling paths, so a fully converged run should land on
the same steady state — the *path*, not the answer, is what the flag changes. **Iteration count
is therefore the discriminating instrument**, and it is the same sharpest-possible equality test
Gate A used: it cannot be nudged without the solver stack actually differing.

## 3. Pre-stated outcomes

- **Iteration counts DIFFER** → `consistent` is **ACTIVE** in `DASimpleFoam`. The retraction gains
  its third and decisive leg — measured activity, not inferred — and the FD-2 refutation is
  airtight for the upstream report.
- **Iteration counts are BIT-IDENTICAL** → the flag is inert *in practice* despite the source
  branch and the config both being present. That would mean **my own retraction is wrong**, the
  original FOUND-DEAD verdict was right for a reason nobody had found, and the material routed
  upstream must be corrected before it lands. I would report that at least as loudly as the
  retraction was made.
- **Converged objectives differ materially** (beyond solver tolerance) → recorded as a surprise
  and investigated separately; it would not by itself change the activity verdict.

No third reading invented afterwards.

## 4. Price and mechanics

A1 at 4,032 cells converges in tens of seconds; two primal-only runs at np=2 ≈ **~2 core-min**,
measured against that estimate. Staged copies per arm (guidelines §8), cold start from the
archived `0.orig`, image tag recorded in each `lever_echo.txt`, setsid + `.t0/.rc/.t1` ledger,
polled inline. Memory: A1's measured peak is ~1.6 GiB at 2 ranks; cap 8g, guard unchanged.
