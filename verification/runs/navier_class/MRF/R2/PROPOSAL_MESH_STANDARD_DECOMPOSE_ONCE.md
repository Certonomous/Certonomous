# PROPOSAL to `docs/standards/MESH_STANDARD.md` — decompose once, and archive the partition

**A PROPOSAL, NOT AN AMENDMENT. NOT FILED, NOT SENT.** Drafted by a cfd `lab-lane`,
2026-09-11. **This lane does not amend a standard**; a standard is retired, changed or
extended by its owners, and this document asks rather than acts (CLAUDE.md rule 7; the
`MESH_STANDARD` is not cfd's to edit). It is placed under the case whose evidence produced
it rather than in a scratch path (rule 13).

---

## 1. THE MEASUREMENT

`scotch` partitions the same mesh differently on every invocation. Measured on one
154,715-cell mesh, from **one identical `decomposeParDict`** — md5 `ea1336801ca0`,
`method scotch;`, **no seed, no coeffs** — across four separate runs:

| invocation | processor0 cells | processor1 cells |
|---|---:|---:|
| control arm A | 77,900 | 76,815 |
| control arm B | 77,011 | 77,704 |
| control arm C (identical in every file to A) | 77,505 | 77,210 |
| clean control | 76,965 | 77,750 |

Arm C is the one that settles it: **nothing differed from arm A — `diff -r` over the staged
trees returned nothing — and it still took its own partition.**

## 2. THE JUSTIFICATION HAS BEEN REWRITTEN, AND THAT IS STATED RATHER THAN HIDDEN

**This proposal was first drafted on a justification that was subsequently REFUTED.** The
original claim was that non-reproducible partitions put a noise floor under the graded value
large enough to swamp the level-to-level signal. **That was wrong.** Measured on windowed
means, two runs on different partitions agree to **2.907564e-04** relative — **below** the
registered discrimination criterion of 5.095632e-04 — and their separation is **0.034** of one
within-run standard deviation. **Different `scotch` partitions converge to the same answer.**
The noise that matters turned out to be within-run oscillation of the graded quantity, and it
is the subject of a separate referral (`REFERRAL_GRADING_STATISTIC_NOISE.md`), not of this one.

***A repair that survives the refutation of its original justification needs its justification
rewritten, not withdrawn.*** The two justifications below are what remain, and they are
sufficient on their own.

## 3. WHAT IS PROPOSED

**Decompose once per level, and archive `processor*/constant/polyMesh` as a run artifact
alongside the case's other inputs.**

## 4. WHY — two reasons, neither of which is "it reduces noise"

**(a) REPRODUCIBILITY.** A parallel run whose partition is not recorded **cannot be
reproduced from its inputs.** Every `polyMesh`, `controlDict`, `fvSchemes` and `0.orig` can be
byte-identical and the run will still not repeat, because the one input that was never written
down is regenerated differently each time. That is true of **every parallel run in this lab**,
and no run has ever been checked for it.

**(b) RE-GRADEABILITY WITHOUT RE-SOLVING.** With the partition archived, a graded run can be
re-decomposed-free and re-examined later. Without it, any question that requires re-running is
a full re-solve.

## 5. WHAT IT COSTS — NEGATIVE

**The 8000 family's disk problem is 49.1 GiB of `processor*` FIELD writes we throw away, while
the ~60 MB of `processor*/constant/polyMesh` that would make the run reproducible is the part
nobody kept.**

Measured: fine's `processor*` field writes run to **314 MiB per written step**, 160 steps at
`endTime` 8000 = **49.1 GiB**, and nothing reads them — the grader reads the reconstructed
`endTime` directory and `postProcessing/`, and `reconstructPar -latestTime` touches only the
last time. The partition itself is a **one-off ~60 MB**. **Keeping the thing that makes a run
reproducible costs about 0.1 % of what we already spend throwing away the thing that does not.**

## 6. WHAT THIS PROPOSAL DOES NOT CLAIM

- It does **not** claim partitions move the graded answer. They do not, at the windows measured
  (§2). Any future citation of this proposal that says otherwise is citing the withdrawn
  justification.
- It does **not** propose a deterministic decomposition **method** (`simple`, `hierarchical`)
  in place of `scotch`. That would change partition quality and is a bigger question than this
  one; archiving the partition achieves reproducibility without touching the method.
- It does **not** propose any change to a frozen grading path, band, threshold, cap or label.
- It is **ours, not an OpenFOAM defect.** The library offers deterministic methods and we asked
  for none; `scotch`'s behaviour is a known property of the library. Same class as a mesh in
  inches with no `transformPoints -scale`: the tool did what it was told, and we did not tell
  it enough. **It is deliberately NOT filed as a §2da defect** — the moment a permission widens
  is the moment everything starts to look like the thing it permits.
