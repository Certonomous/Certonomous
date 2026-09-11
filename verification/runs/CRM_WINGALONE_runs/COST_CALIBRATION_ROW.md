# RULE-12 ESTIMATE-VS-ACTUAL — CRM WING-ALONE MESH LADDER

Unit: **core-minutes = wall s x ranks / 60**, all runs at **1 rank**. Dollars **DERIVED, NOT
MEASURED**, at the owner-stated c7a.4xlarge **$0.0513/core-h** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5), so `cost_basis` = **reported-by-owner, not measured**.

## Graded family (pGridRatio 1.03) — the ladder that carries the verdicts

| level | extrude wall s | convert+check wall s | **core-min** |
|---|---|---|---|
| L1 | 33 | 5 | **0.633** |
| L2 | 79 | 22 | **1.683** |
| L3 | 379 | **184** (convert 62 + checkMesh 122) | **9.383** |

## Superseded and diagnostic spend — NAMED, NEVER ABSORBED INTO THE RATIO (§6 of the budget charter)

| item | wall s | core-min | why it was spent |
|---|---|---|---|
| L1 attempt 1 extrude, pGridRatio 1.1 | 6 | 0.100 | superseded by the single-option-set rebuild |
| L1 attempt 1 convert (x2, missing `fvSchemes`) | 7 | 0.117 | instrument setup |
| L1 triage `s0` = 1.0e-4 | 45 | 0.750 | **G-M4 crash triage — bought the finding that `s0` is not the lever** |
| L1 triage `s0` = 2.0e-4 | 61 | 1.017 | same |
| L2 attempt 1 extrude+convert, pGridRatio 1.1 | 104 | 1.733 | superseded |
| **L3 attempt 1 — pyHyp refused pGridRatio 1.1** | 36 | 0.600 | **bought the pGridRatio finding and the rc=0 instrument defect** |
| **subtotal** | **259** | **4.317** | |

**This is diagnostic spend, not waste.** Two of these rows purchased findings that are the main
product of the rung. Recorded separately so the actual/predicted ratio is not flattered by them.

## The comparison

| | core-min |
|---|---|
| **pre-registered estimate (§6)** | **146.44** (extrude 136.88 + convert/check 9.56) |
| **registered cap (10x)** | **1,464** |
| **actual, graded family** | **11.700** |
| **actual, including all diagnostics** | **16.017 measured + ~4 estimated container probes = ~20.0** |

**Ratio actual/predicted = 0.137 — the rung came in 7.3x cheaper than registered, and used
1.37 % of its cap.** Dollars **DERIVED, NOT MEASURED**: **$0.0171 actual** against **$0.1252**
predicted, at $0.0513/core-h.

*The ~4 core-min for the container census / G-M5 / planted-control runs is **ESTIMATED, not
measured** — those runs were not individually timed. It is stated as an estimate rather than folded
silently into a measured total.*

### Attribution of the gap — misprediction, with a single identified root cause

**Not contention and not waste.** The dominant term is **misprediction in the §6 anchor**, and its
root cause is measured in `PROBE_SURFACE_CORRECTION.md`: the `59dfc5232` probe was believed to have
marched **579,072** cells when it marched **2,316,288** — its surface was `ACT9` (L3's), not `A6`.
That put the registered extrusion rate at **12.952 core-min/Mcell** when the probe's own rate was
**3.246**, a factor of exactly **4.00**.

A second, independent term runs the same way: the probe's rate is itself **dominated by outer-layer
KSP blow-up at `N` = 53** (its CPU went from 35.8 s at layer 40 to 368.5 s at layer 49). At `N` = 209
the per-layer growth is far gentler, so **L3 marched 4x the probe's cells in 275.8 s of pyHyp CPU
against the probe's 451.1 s.** A rate anchored on a low-`N` march over-predicts a high-`N` one.

**Both terms are over-estimates, so no cap or precondition was ever loosened by the error.**

## Disk — predicted vs measured

| | registered §6 | **measured** |
|---|---|---|
| Plot3D volume meshes, all three levels | **2.99 GB** | **0.742 GB** (11.7 + 84.9 + 645.0 MB) |
| bytes/cell (Plot3D) | 282.5 | **73.3 - 81.1** (L2, L1) |
| OpenFOAM `polyMesh`, all three levels | **NOT REGISTERED AT ALL** | **1.995 GB** (23.7 + 205.5 + 1,765.9 MB) |
| **total on disk** | 2.99 GB | **2.74 GB** |

🔴 **The registration costed the Plot3D files and NOT the `polyMesh` they convert into** — and the
`polyMesh` is **2.7x larger than the Plot3D file** it comes from (measured **163-191 bytes/cell**
against 73-81). The two errors happened to cancel to within 9 %, so the headline 2.99 GB was close
by luck rather than by accounting. **A successor rung that keeps only `polyMesh` must budget
~191 bytes/cell, not 282.5 bytes/cell of `.xyz`.**
