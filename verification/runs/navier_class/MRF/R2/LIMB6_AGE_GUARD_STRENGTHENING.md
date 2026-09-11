# Limb 6 (rule-4 age guard) — a measured strengthening, from MRF_R2

**Date:** 2026-09-11
**Author:** cfd MRF lane, at the cfd-supervisor's direction
**Status:** a **disclosed practice** carried by the MRF grading record. **Not a charter
change and not proposed as one** — the measurement is relayed to the verification team,
and the ruling is theirs.
**Closes (as a repair candidate):** the open weakness recorded at commit `0bdf38639` —
*"rule 4's age guard cannot tell a solver-written field from a post-processor-written
one"*, found when a demo export wrote into a graded F25 tree.

---

## 1. The weakness

Rule 4's age guard requires every field at `endTime` to be newer than the case's own `0/`.
As implemented against a **reconstructed** time directory
(`grade_mrf_np.py::strict_completion`, the `age guard` clause), it is satisfied by **any
writer that touches that directory after launch** — `reconstructPar`, a demo export, a
post-processing script. The guard dates *a* write; it does not establish that the write
came from the run allowed to produce the answer.

On MRF_R2 coarse the limb passes on a directory the solver never wrote:
`…/R2/coarse/4000/` was produced by `reconstructPar` at **03:56:41Z**.

## 2. The strengthening

> The age guard checked against a reconstructed time directory is satisfiable by any
> post-processor that writes there. Anchor it **additionally** on the solver-written
> **`processor*/<endTime>/`** fields, which the ordinary post-processing path does not
> produce.

**Measured on MRF_R2 coarse** (`verification/runs/navier_class/MRF/R2/coarse`):

| artifact | mtime |
|---|---|
| `0/` datum (newest entry, `0/U`) | 02:21:10Z |
| solver-written `processor{0,1}/4000/` — all 12 fields | 03:56:38–39Z |
| reconstructed `4000/` — all 6 fields | 03:56:40–41Z |

All twelve decomposed fields newer than the datum; **none stale, none missing**; the
decomposed set precedes the reconstructed set by **2.3 s**, in the order a
solve-then-reconstruct requires.

## 3. The limitation — stated, because without it another family lifts this and gains nothing

The claim *"a post-processor cannot write `processor*/`"* is **too strong, and this note
does not make it.** Two ordinary utilities write decomposed fields:
`decomposePar -fields` and `redistributePar`. The anchor is therefore **not self-proving**
and requires a companion ordering test:

1. **no decomposing utility ran after the solve** — on coarse, a single
   `log.decomposePar` at **02:21:13Z**, **95 minutes before** the `4000/` decomposed
   fields, with **zero occurrences of `fields`** in it; and
2. **decomposed precedes reconstructed**, as above.

Both are read from artifacts on disk, not asserted.

**Second limitation:** a **serial** run has no `processor*/` directories at all, so this
anchor is unavailable there and limb 6 falls back to its existing form. A family lifting
this must say which case it applies to rather than adopting it blanket.

## 4. Why it is worth having anyway

The decomposed fields are the solver's own output in the normal pipeline. An accidental
writer — the F25 demo export, a figure script, a stray `reconstructPar` — touches the
**reconstructed** directory and leaves `processor*/` alone. The strengthening does not
make limb 6 unforgeable; it makes the **common accidental** failure visible, which is the
failure that actually occurred.

## 5. Scope

This note records a measurement and a practice. It asserts **no verdict** on MRF_R2 or any
other case; the grade, and every verdict word, is the cfd-supervisor's.
