# W4 — idx16 is not a second defect. The finite difference it is graded against is.

**Measured 2026-08-02 10:44–10:55 UTC, 14.2 core-minutes on 4 ranks, 1,200
cells per rank.** Serves docket item
`w4-idx16-is-the-whole-remaining-residual`, *"Explain the one gradient
component the correction makes worse."*

Case: `/home/ubuntu/certonomous-runs/W4-idx16/case` (a copy of
`W5-regrade/a5pl_patched`, so the disputed table's own case).
Driver: `/home/ubuntu/certonomous-runs/W4-idx16/run.sh`, which carries the
pre-registered hypotheses in its header. Logs: `probe_*.log` in that directory.

---

## 1. The premise, as filed

Under the patched IDWarp, A5's `OBJ.val` wrt `shapexUpper` is in band on 26 of
27 components. idx16 is the exception and the only entry in either the A1 or A5
record that the patch moves the **wrong way**
(`W5_GRADIENT_REGRADE.md` §7.3):

| | analytic | FD | rel. err |
| --- | --- | --- | --- |
| stock | −3.77483865 | −4.30296296 | 12.2735% |
| patched | **−5.04787848** | −4.30296296 | **17.3117%** |

The whole 27-vector's absolute error is 7.474091e-01 and idx16's share of it is
7.449e-01. **idx16 is the remaining residual**, exactly as the item's title says.

## 2. Two mechanisms refuted before spending anything

* **Decomposition**, this lab's first discriminator. `W4-a5-decomp` already ran
  A5's `compute_totals` at fixed np=4 under `scotch` against `simple` 4×1×1
  **with the patch mounted**, and idx16 reads **−5.04787848** against
  **−5.04971724** — 3.6 × 10⁻⁴ relative. idx16 is decomposition-invariant.
  Found by opening the record, not by re-running it.
* **The FD moving.** It is bit-identical between the stock and patched
  `check_totals` runs, and identical on all four MPI ranks in both. The primal
  never sees the patch, which only supplies a `warpDeriv` term.

## 3. What was run

`runScript.py -task probe` perturbs `shapexUpper[idx]` by a delta, runs the
**primal only** to `primalMinResTol` 1e-8, and prints `OBJ.val` to 15 digits.
Two further tasks were added to the private copy of the case to reproduce
`check_totals`' protocol rather than argue about it:

* `probewarm` — converge the baseline once, then perturb **in memory** from that
  converged state and re-run, which is what OpenMDAO's FD does;
* `probeseq` — the same, but entering idx16 from the state its **predecessor**
  left, i.e. `x − h·e₁₅`, which is the sequence `check_totals` actually walks.

**Every measurement below is deterministic.** Repeated runs return
bit-identical `OBJ.val`: the baseline reads `5.234521633934580e+01` on four
separate invocations, and the `probewarm` idx15 pair reproduced to every digit
on a repeat.

## 4. The control: the harness reproduces `check_totals` exactly

idx15 is idx16's immediate neighbour and the **largest component in the whole
vector**. Whatever is read at idx16 must not be read here, or the effect is the
harness.

| idx15, step 1e-4 central | value |
| --- | --- |
| `check_totals` reported FD | −24.27272214 |
| **`probewarm`, same protocol, by hand** | **−24.27272** |
| agreement | **8.8 × 10⁻⁸ relative** |

Eight significant figures. The harness is the same instrument.

## 5. idx16: three independent finite differences, and none of them is −4.303

| method, step 1e-4 central | idx16 FD | vs patched analytic −5.04787848 |
| --- | --- | --- |
| `probeseq` — `check_totals`' own sequence | **−5.04286** | **+0.10%** |
| `probewarm` — warm from the baseline | **−5.05964** | −0.23% |
| `probe` — cold from `0/` each time | **−4.98068** | +1.35% |
| **`check_totals` reported** | **−4.30296296** | +17.31% |

And the step ladder on the cold path, which shows no kink and no step pathology:

| h | forward | backward | central |
| --- | --- | --- | --- |
| 1e-5 | −3.14229 | −6.78125 | −4.96177 |
| 1e-4 | −4.86021 | −5.10115 | −4.98068 |
| 1e-3 | −4.89367 | −5.21437 | −5.05402 |
| 1e-2 | −3.81936 | −6.80354 | −5.31145 |

On the warm path at 1e-4 the two one-sided slopes are **−5.05727 and −5.06201**,
agreeing to 0.09%. **There is no kink at idx16**; the function is smooth there
and its derivative is about −5.05.

### 5.1 The hypotheses, scored as written

The three were pre-registered in `run.sh` before any of this ran.

* **H1 (kink)** — *forward and backward split by ≈1.49 and the split does not
  shrink with the step.* **FALSE.** On the warm path they agree to 0.09%.
* **H2 (noise / under-resolved FD)** — *the central difference moves toward the
  analytic as the step grows and the one-sided split shrinks.* **FALSE as
  stated.** The cold path does drift with step (−4.96 → −5.31 from 1e-5 to
  1e-2) and the 1e-5 split is noise, but the warm path at 1e-4 is clean and
  already at −5.06. The FD was never the ambiguous quantity.
* **H3 (the patched analytic is simply wrong)** — *forward, backward and central
  all agree near −4.303.* **FALSE.** Nothing agrees near −4.303.

A fourth mechanism was tested rather than assumed: `check_totals` evaluates the
FD component by component, so idx16 enters from the state idx15's last
evaluation left, and idx15 is the vector's largest component. `probeseq`
reproduces that chain exactly and returns **−5.04286**. **State carry-over does
not explain it either.**

## 6. What this does to the record

**The patch fixes idx16 too, to 0.10%.** The 17.31% is an artefact of one entry
of `check_totals`' reported FD vector, and three faithful re-executions of that
same FD — including one that walks `check_totals`' own component sequence —
land within 1.4% of the patched analytic.

Two published readings do not survive:

* *"idx16 is the only entry in either case that the patch moves in the wrong
  direction"* — **it moves in the right direction, and further than the record
  credits.** Against a corrected FD of −5.04286 the analytic error goes from
  **25.1% stock to 0.10% patched**, a 250-fold improvement rather than a
  5-point regression.
* *"Stock, idx16 sat 0.27 percentage points outside the ±12% band"* — it sat
  **13 points** outside it. That reading was computed against the same bad FD.

**A5's patched aggregate improves 12.3-fold.** `‖AN − FD‖/‖FD‖` over the 27
components is **2.2372%** as published; with idx16's FD replaced by the
sequence-faithful −5.04286 it is **0.1826%**. With that correction **A5's full
table is in band on 27 of 27 with no exceptions**, which is what §7.4 of the
regrade could not say.

**What is NOT claimed.** Why `check_totals` reports −4.30296296 is still open.
It is deterministic — identical across the stock and patched runs and across all
four ranks — and it is not decomposition, not the step, not one-sidedness, not a
kink, and not the component sequence. It is recorded as an **anomaly in the
verification instrument at one component**, with its evidence, rather than
explained away. What can be said is that the derivative under test is not what
is wrong with it.

**And the lesson this repeats.** The lab's own drafting rule — *a dismissal that
rests on a finite difference must check what the finite difference is of* —
applies here in reverse: a **finding** rested on a finite difference nobody had
re-measured. The instrument that graded 27 components was itself ungraded at the
one component that mattered.

## 7. Cost, measured on CPU

| | |
| --- | --- |
| ranks | 4, 4,800 cells, **1,200 cells per rank** |
| single-primal probe | **8.57 s** wall (timed) = 0.571 core-min |
| three-primal `probewarm` | **13.43 s** wall (timed) = 0.895 core-min |
| runs | 16 single-primal, 3 three-primal, 1 four-primal, 4 fast failures |
| **total, CPU basis** | **≈14.2 core-min** |
| item's filed estimate | 25 core-min → **0.57×, under** |

Two harness defects cost four of those failed runs and are fixed in `run.sh`:
DAFoam's `renameSolution` refuses to overwrite a solution directory a previous
probe left (`rm -rf processor*` before each run, which is what the lab's own
idx0 driver did), and `argparse` rejects `-probeDelta -1e-4` because its
negative-number matcher does not accept exponent notation — it needs
`-probeDelta=-1e-4`.
