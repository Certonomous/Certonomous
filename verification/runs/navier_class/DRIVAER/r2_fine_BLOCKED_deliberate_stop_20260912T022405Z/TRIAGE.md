# r2_fine — **BLOCKED** — DELIBERATE STOP ON A MEMORY-HEADROOM JUDGEMENT

**Verdict: `BLOCKED`.** It did not fail and it did not crash. **It was never allowed to
finish.** No mesh number is quoted from this directory and no gate was evaluated on it.

**Whose decision this was.** The **cfd-supervisor's**, 2026-09-12, on the reasoning in
§2 below. This lane executed it and did not initiate it. The lane's own earlier
recommendation reached the same conclusion **for a reason the supervisor rejected as
wrong** — see §3, which is the part of this note worth reading.

## 1. What was stopped, and how

`snappyHexMesh` pid 2625466 and its `/usr/bin/time` parent 2625465, **by pid**, after
re-confirming **both `/proc/<pid>/cwd` AND `/proc/<pid>/cmdline` at the moment of
signalling** (L-557). Never by pattern. TERM, then KILL to 2625466 after 8 s with the
cwd re-confirmed a second time. rc=143.

    available BEFORE 10.18 GiB   ->   available AFTER 13.62 GiB
    MEMORY RELEASED              =    3.44 GiB
    snappy RSS at the stop       =    3.43 GiB
    elapsed                      =    3,250 s  = 54.17 core-min (serial)
    progress                     =    735 log lines; castellation refinement COMPLETE
                                      (5 shell refinement iterations, 5,413,223 cells),
                                      entering SNAPPING; the LAYER PHASE never started.

**The headroom guard NEVER FIRED.** Its log records only `snappy no longer running;
guard stands down`. Its trigger stayed at 5.0 GiB throughout and was never lowered,
and `available` never fell below 9.47 GiB in 164 samples. **This was a decision, not a
gate event** — the distinction the supervisor drew: weighing expected value and choosing
is a supervisor's job; manipulating the conditions a gate reads is not.

`EXTERNAL_KILL.txt` in this directory reads *"KILLED FROM OUTSIDE (OOM, operator, or
session end)"*. That text is the wrapper's generic rc=143 limb and its **mechanism** is
right, but its **cause** is wrong: there was no OOM and no session end. **This stop was
deliberate and is recorded here.**

## 2. Why — the supervisor's reasoning, which is narrower than the lane's

**THIS PARTICULAR MESH WOULD NOT HAVE COMPLETED.** A projection built from two
separately measured, mutually isolated factors:

| factor | value | how it was isolated |
|---|---|---|
| layer cost | **1.81x** | A1 122.6 s / r1_coarse 67.6 s — **both uncontended**, so layers alone |
| contention | **3.25x** | r2_medium's own snappy 2,144.8 s / (r1_medium's 364.2 s x 1.81) — **layer factor divided out**, so contention alone |

r1_fine snappy (no layers, uncontended) = 2,359 s
=> r2_fine snappy = 2,359 x 1.81 x 3.25 = **13,892 s = 3.86 h**, with the **layer phase
beginning at 1/1.81 = 55 % of that, i.e. ~03:35Z** (03:54–04:14Z if contention is
15–30 % worse than when medium's mesh built, which it is).

Against that, the two events that would have freed memory:

| event | time | frees |
|---|---|---|
| r2_coarse solve lands | ~04:00–04:45Z | 0.44 GiB + 4 ranks — **too small** |
| MRF fine lands | ~06:20–07:00Z | 3.19 GiB + 6 ranks — **too late** |

Fine needed roughly **1.6 GiB more headroom** than it had to reach a 1.12x-corrected
**10.6 GiB** peak and stay above the 5.0 trigger. **On every branch the guard fires
before completion.** So the mesh's expected value tonight was not low — **it was zero** —
while it held the largest contested memory block on a box also carrying another team's
three-and-a-half-day `rhoCentralFoam` and a six-rank MRF solve near landing. Stopping
now bought the same nothing at ~3.4 GiB less cost and two hours sooner.

## 3. The lane's reason was WRONG, and the correction is the useful part

The lane argued the mesh had no tonight-value because *"its only value is as an input to
a run that will not happen for many hours."* **That is false, and the supervisor rejected
it.** **A MESH IS A GRADED ARTIFACT IN ITS OWN RIGHT.** `r2_coarse` and `r2_medium` were
both graded on M1, M2, M3 and Y1 **with no solver involved at all**. A completed
`r2_fine` would have delivered a **third graded level**, a third point on the M3
monotonicity curve, a Y1 at the finest resolution, and a complete three-level family.
**That is real value, tonight, independent of solving.**

The distinction is load-bearing rather than pedantic: **if memory were freeing at 03:00Z
instead of 06:20Z, the lane's argument would still say stop and the supervisor's would
say let it finish.** The conclusion was taken; the reasoning was replaced.

## 4. What survives, and what it is worth

* **`HEADROOM_SERIES.tsv` — 164 samples at 10 s intervals** of `free -g` available and
  snappy RSS with the build stage on every row. It is the only measurement this lab has
  of what a 5.4 M-cell layer build does to a shared box, and it is **worth more than the
  mesh was**. It also carries the finding that the RSS trace **oscillates** with each
  refinement sweep (3.13–5.22 GiB) rather than climbing — which is what falsified an
  earlier hold built on two point-readings.
* **`SYSTEM_PROVENANCE.txt`** — per-file, which source dict was taken and that it matched
  `r1_coarse`. This is the level whose `*.meshbuild` asymmetry caused the attempt-1
  `blockMesh` failure, and the provenance file is the artifact that makes the repair
  auditable.
* **The eMesh was REGENERATED and is byte-identical to `r1_fine`'s** (`RUN_META.txt`).
* `CAP_SCORED.txt`: 54.17 core-min against a 300 core-min prediction, **0.181x** — scored,
  not enforced. **No spend cap was armed and none stopped this run.**

## 5. Cost

**54.17 core-min = $0.0463 derived** at $0.0513/core-h (owner-stated;
the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER` §5 — **derived, not
measured**). **This is spend with no graded output and it is named as such**, not
absorbed into another row. It is not *waste* in the charter §6 sense — nothing was
discarded through error — it is the **priced-in cost of a supervisor decision taken on
a measurement**, and it is attributed there.

## 6. To rebuild

On a quiet box, unchanged: `build_r2_level.sh fine 300 9.5` — note the memory argument
should be **9.5 GiB, not 8.49**, because `r2_medium` measured the 1.508 layer-memory
factor as under-predicting by **1.12x** (predicted 1.7 GiB, measured 1.897 GiB). The
run directory guard will refuse while this stopped attempt exists; satisfy it by
**moving**, never by disabling.

---

## ADDENDUM 1 — 2026-09-12, cfd. Two rulings of the cfd-supervisor's, and a measurement neither of us predicted.

*Appended at the foot; no line above this section changed number.*

### A1.1 The STL in this tree is a DUPLICATE, not evidence — and it needs a pointer

`constant/triSurface/drivaer_466.stl`, 142,346,740 B, hashes
**`9fd0eec1f436e336044c3abebe552e106acd273f63d96d9780c1441cc4c1a3b2`**. That is
byte-for-byte the canonical geometry outside git at
`/home/ubuntu/certonomous-runs/navier_class/DRIVAER/drivaerml_r7a5c094/run_466/drivaer_466.stl`,
**and it is also the sha registered in `drivaer_reference_notchback.json`** — canonical,
copy and registration agree three ways. So there is no finding in the bytes, and the
tree needs a **POINTER to the canonical file, not 144 MB of duplicate.** The canonical
path above is that pointer; nothing in this directory should ever be treated as the
geometry of record.

**What we did not predict, and it is the useful part: the r1 family already did this
right and the r2 family regressed.** `r1_coarse`, `r1_medium`, `r1_fine`, all four
LAYERFIX trees and all four DIAG trees carry the STL as a **93-byte symlink** to the
canonical file. Every `r2` level carries a **full 142,346,740 B copy** — four of them,
**569,386,960 B = 543 MB** — plus ~13 copies of the 5,035,650 B
`extendedFeatureEdgeMesh`. **None of it was gitignored and none of it was tracked**, so
one careless `git add -A <path>` would have swept ~608 MB into a repository that is
pushed (rule 10; L-12: 1,187 files, 25M insertions, twice). A `.gitignore` entry scoped
to `verification/runs/navier_class/DRIVAER/**/constant/{triSurface,extendedFeatureEdgeMesh}/`
now closes that, shadowing **zero** tracked files. **The r2 build path should symlink the
STL as the r1 path does; it copies it, and that is a defect in the build path, not in
this tree.** The lab-wide exposure of the same shape measures **1,732.4 MB across 53
unignored files over 1 MB** and is REPORTED for a ruling rather than swept — a lab-wide
rule would shadow 40 files that are deliberately tracked today in another team's
territory (`R4_runs`' `ahmed_25`, `F8_runs`' `blade`).

### A1.2 The waste question, ruled — §5 of this note is SUPERSEDED on its label, not on its reasoning

§5 above argues that the 54.17 core-min is **not** waste in `COMPUTE_BUDGET_CHARTER` §6
terms because nothing was discarded through error. **The cfd-supervisor has ruled
otherwise and the ruling stands: it is named WASTE.** The accounting question is narrow —
*did this spend yield a graded artifact?* It did not; the mesh never completed and
nothing was graded.

**§5's reasoning is not struck, because it is also true and it goes in the record beside
the label: the spend BOUGHT something.** It purchased the 164-sample `HEADROOM_SERIES.tsv`
and, through it, the two separately-isolated factors — layer cost 1.81× and contention
3.25×, each measured with the other divided out — that produced the 231.5 core-min
projection for the full snappy step, which is the only honest calibration figure this
process has. Information is not nothing.

**Both statements live in the record and NEITHER enters the ratio.** A waste category
that quietly absorbs *"but we learned something"* stops being able to count anything.
The `docs/COST_CALIBRATION.md` row carries the same resolution.
