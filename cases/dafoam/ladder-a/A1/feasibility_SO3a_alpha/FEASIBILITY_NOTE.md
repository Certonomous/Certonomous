# SO-3a ALPHA FEASIBILITY (`SO3aF`) — L1 primal-only feasibility rung

**THIS IS NOT A PRE-REGISTRATION AND ITS OUTPUTS ARE NEVER GRADEABLE AS VERDICTS.**
It files with `prereg_commit = "FEASIBILITY"` under Sanaa's ruling of 2026-08-31,
quoted verbatim from `etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md:5`:

> "start the L1 feasibility solves on Cases 1 and 2 NOW — no freeze required for
> feasibility/physics rungs, never was."

`scripts/queue_entry_check.py:114` encodes that ruling lab-wide as
`UNREGISTERED_PREREG_TAGS = frozenset({"FEASIBILITY", "PHYSICS"})` (commit `9154c8ef`),
exact-match and case-sensitive. **Nothing here is filed, sent or submitted** (rule 7).

## 1. The question, and why it is genuine

SO-3a was frozen today (`curriculum_SO3a/PREREGISTRATION.md`, commit `1a06a7d6`) as an
alpha-multipoint gradient rung on three angles:
**α = {3.13918623195176, 5.13918623195176, 7.13918623195176}°**, equal weights 1/3.

Its own §4 is explicit that the bracket is not measured:

- **α₀ = 5.13918623195176° is a QUOTATION** `[REGISTERED, curriculum_SO2a/so2a_runScript.py:35]` —
  the tutorial's trimmed angle at `CL_target = 0.5`.
- The **±2° bracket is lane-chosen** `[REGISTERED, lane-chosen]`, resting on the argument that
  "at Re ≈ 6.7×10⁵ NACA0012 is attached throughout 3–7°". **That is ARGUED, NEVER MEASURED.**

**No multipoint arm has ever run on this case and none of the three angles has been solved.**
So SO-3a's premise is unverified, and its own registered prediction **P3** — that
`CD(3.139°) < CD(5.139°) < CD(7.139°)` — has never been tested. If the top angle is
separating, the gradient rung would be built on a point that does not solve, and
SO-3a sizes that at ~400 core-min across 306 primals.

**This rung answers that for ~1.5 core-min, before the 400 are spent.**

## 2. What it does

Three **primal-only** `DASimpleFoam` solves, one per registered α, on **SO-2a's existing
4,032-cell A1 NACA0012 mesh, staged by copy** (the SO-2a run root is never written).

**No adjoint. No optimiser. No FFD deformation. No CL trim** — α is the operating point
here, so `run_driver`'s `findFeasibleDesign` is deliberately not used; the entry point is
`-task run_model`, which is `prob.run_model()` and nothing else.

The runScript is `curriculum_SO2a/so2a_runScript.py` copied with **exactly one line changed**
(`aoa0` sourced from `SO3AF_AOA` instead of the hard-coded α₀), so the primal path is the
verified one, not a new harness. Each α starts from a fresh `0/` copied from `0.orig`, so the
three points are independent and none inherits its neighbour's solution.

## 3. What is reported

Per α: rc, whether the primal **converged** (a zero rc is not convergence — the reader looks
for the convergence line separately), residual history, **CL**, **CD**.

Across the bracket: whether **CD is monotone increasing**, and the two secant slopes
`dCL/dα` with their ratio.

**Attachment indicator, stated before any number exists:** for attached flow on a thin
symmetric section CL is very nearly linear in α, so a slope ratio near 1.0 means the bracket
is in the linear attached range and a ratio materially below 1.0 is the separation-onset
signature. **This is an INDICATOR, not a separation measurement** — a real attachment claim
needs wall shear, and this rung does not buy it.

## 4. What it does NOT establish

Nothing about gradients, adjoints, optima or weights. Nothing at np ≠ 1. Nothing about Mach —
`DASimpleFoam` has no equation of state. Nothing about α outside the bracket, and nothing
about stall. **No grid family, no GCI.** No number from this rung may be quoted as a verdict
or carried into SO-3a's grading; if SO-3a wants these numbers it re-measures them under its
own frozen gates.

## 5. Cost anchor — the program it prices, named (`DAFOAM_CHARTER.md` §18.1)

**Anchor:** `curriculum_SO3a/PREREGISTRATION.md` §A3 — **0.062585 core-min per primal**
(3.755 wall s) `[DERIVED from two MEASURED figures, curriculum_SO2a/PREREGISTRATION.md:135]`.

**The four properties that anchor prices, and whether this program matches:**

| property | anchor A3 | `SO3aF` | match |
|---|---|---|---|
| ranks | 1 | 1 | **matches** |
| adjoint | none | none | **matches** |
| colouring | none | none | **matches** |
| tree | **WARM** | **COLD** (0/ reset from 0.orig per α, deliberately) | **MISMATCH — adjusted UP** |

The mismatch is on cold/warm and is adjusted rather than carried silently, which was D6R's
defect (a bare multiplier with no derivation). A cold primal pays mesh read and `DASolver`
init that the warm anchor does not: **3 × ~15 s ≈ 45 s** `[EXTRAPOLATED, not measured — no cold
primal on this case has been timed]`, plus container start + `loadDAFoam.sh` **~15 s**
`[EXTRAPOLATED, bounded above by D14M's MEASURED 11 s total container wall on a warm image]`.

**Point ≈ 60 s wall × 1 rank = 1.0 core-min; registered estimate 1.5 core-min** (headroom on an
extrapolated figure); band **[0.5, 4.0]**. **Cap 8.0 core-min = the 480 s `timeout -k 60` INSIDE
the container**, which is what actually stops it. Dollars **$0.0013 point, $0.0068 at cap**,
derived at $0.0513/core-h on c7a.4xlarge, **REPORTED-BY-OWNER, NOT MEASURED**
(`COMPUTE_BUDGET_CHARTER.md` §5). **Calibration row owed at completion** (rule 12).

**Memory floor 6.0 GiB**, from D13's **MEASURED 1.70 GiB** peak RSS for this 4,032-cell 2-D case
at np = 1, plus headroom. Container cap 4g.

**cpuset 15**, disjoint from every registered set in this family — SO1bR **9** (live, unmovable),
W2R 12, D4-SHIPPED 5/6/7/9, D7FR 2/3/4/6, D5 8/10/11/13, D14M 14 — and not core 0.
G-CPUSET refuses a collision at exit 3, driven against the live SO1bR container.

## 6. Guards, each driven rather than asserted

| guard | refuses with | driven |
|---|---|---|
| G-ROOT | 6 — run root already exists | yes, sacrificial root |
| G-SRC | 5 — any instrument or the source mesh absent, **asserted at the point of use** | yes, bogus path |
| G-IMG | 4 — image absent or digest not `9d45679d` | passes on the real image |
| G-CPUSET | 3 — core held by a live container | **yes, real collision with live `so1br` on core 9** |
| MEM wait | 7 — bounded 3600 s poll on **live MemAvailable**, terminating **non-zero** | bound and exit path present |

**Three defects this family paid for today, and how each is closed:**

1. **No `VAR=$(python3 "$VAR" ...)`.** Script paths are `readonly` literals set once, never
   reassigned from their own output, and `test -f` runs **at the point of use**, not only at
   startup (`so1br_chain_driver.sh:83`/`:206`).
2. **The wait is on the TRANSIENT quantity** — live `MemAvailable` — **bounded and terminating
   non-zero**, never a one-shot block (W3 blocked on the transient and lost 20 of 33 stages).
3. **DECLARED and EXECUTED are both counted and both reported**, EXECUTED from the container's
   own emitted per-α markers; **no success token is emitted over a truncated program**
   (W3's unconditional `PHASE1_COMPLETE`).

The in-container program is a **file** (`so3af_cmd.sh`), not an inline heredoc — the SO-1bR
lesson, so it can be md5-pinned and read.
