# The B-52 ladder's "turn" — WITHDRAWN, and the audit's 26 grades re-run against the withdrawal

**Chief ruling, 2026-08-10, recorded at `7abb0ba3`.** This is the canonical
record of the withdrawal and of every disposition applied under it. Sites carry
dated pointer amendments back to this file; **no original text is deleted
anywhere**, and frozen artifacts are not edited at all.

---

## 1. The ruling, and the two independent grounds

> **The B-52 ladder's "turn" — the −4.055 × 10⁻³ increment from rung 6 (330 950
> cells) to rung 7 (441 057 cells) — is WITHDRAWN as a claim.**

**Ground 1 — the pre-registered arm.** `B52_TURN_CLOSURE_RESULTS.md`
(pre-registration `f4ccfe92`, results `c12c876b`): five draws at rung 6, three at
rung 7 give `s₆ = 2.158 × 10⁻³`, `s₇ = 1.109 × 10⁻³`, `T̂ = 1.671`, 90% CI
**[0.846, 2.445]**. The verdict reads INDETERMINATE, but **T_hi = 2.445 < 3.0
excludes SIGNAL at 90% confidence**, which is the limb the audit needed.

**Ground 2 — the arithmetic of how the number was built, which needs no
statistics at all.** Among the eight draws:

| rung | draws (Cd, sorted) |
| --- | --- |
| **6** (n = 5) | 0.0469209, 0.0482808, 0.0486611, 0.0509543, **0.0522755 ← `finer2`** |
| **7** (n = 3) | **0.0482202 ← `rung7`**, 0.0501348, 0.0501473 |

**The published turn is `finer2 − rung7`: the MAXIMUM of the five rung-6 draws
minus the MINIMUM of the three rung-7 draws.** Re-estimated from all eight:

> **mean(rung 7) − mean(rung 6) = +8.223 × 10⁻⁵ ± 1.158 × 10⁻³, t = 0.071** —
> **49.3× smaller than the published turn, of the OPPOSITE sign**, and smaller
> than the ≈1.8 × 10⁻⁴ bias from the two rungs' draws not matching resolution
> exactly.

**A selected extremum is not a measurement.** Nobody selected it — one draw was
taken at each rung and that is where they fell — but the number carries the
statistical properties of an extremum regardless of intent.

The chief's ruling rests on Ground 2. That analysis was **not** pre-registered
and was reported as unregistered; the ruling notes that the arithmetic of how a
number was constructed needs no pre-registration to be true.

## 2. The 26 grades, re-run

The audit graded 35 rows against a **0.91–2.38× bracket**. With the turn
withdrawn outright, the test changes from *"does this survive with the scatter
attached?"* to *"does this survive at all when its subject does not exist?"*

**Five promotions, A → W.** No demotions.

| # | claim | was | **now** | why the grade moved |
| --- | --- | --- | --- | --- |
| **1.1** | *"the turn is signal and not iterative noise ... 113× the window 2σ"* | A | **W** | *"is signal"* is now **false**, not merely unsupported. Split disposition: the *"not iterative noise"* limb is **true and independently reconfirmed** (D6 is 94.6× the rung's iterative 2σ) and is kept — the withdrawal is of the inference, not the measurement |
| **1.3** | *"the ladder oscillates ... swings getting wider: 0.001857, 0.002377, 0.002702, 0.004055"* | W (trend) + A (sequence) | **W (entire)** | the A limb fell with the turn. The 4th increment is withdrawn; the first three are **unmeasured against draw scatter, not disproven** — each is n = 1, and all three are ≈1× the measured √(s₆²+s₇²) = 2.43 × 10⁻³. Settling them needs their own replicates |
| **1.4** | *"the turn is −4.055 × 10⁻³ ± 47% from mesh construction alone"* | A (supersede the number) | **W** | a claim of the form *X ± Y* does not survive by widening *Y* when **X itself is withdrawn**. Replaced, not banded: the increment is +8.2 × 10⁻⁵ ± 1.2 × 10⁻³ |
| **1.6** | *"**Four for four.**"* (corpus table, B-52 row *"turns twice"*) | A | **W (the headline)** | one of the four no longer turns. The table survives amended; the count does not |
| **1.7** | *"oscillation suggests possible interaction between nearBody shell level 2 refinement and background blockMesh boundary-layer growth"* | A | **W** | with the oscillation withdrawn there is no oscillation to explain. **Re-homed rather than deleted**: `B52_RECIPE_NOTE_BACKGROUND_PRODUCT.md` measures a real stepwise interaction of exactly that kind — **in the delivered cell count**, not in Cd |

**Unchanged:** 1.2, 1.5, 6.1 stay **W**; 1.8 stays **A** (stale for reasons
unrelated to the turn); 2.3, 2.4, 2.5, 3.3, 5.4, 6.4, 6.5, 6.8 stay **S**; the
rest stay **A**.

### Final disposition counts

| grade | before | **after** |
| --- | --- | --- |
| **W — withdraw** | 4 | **8** |
| **A — amend** | 20 | **15** |
| **S — survives** | 8 | **8** |
| **N — no action** (3 classes, ≈152 sites) | 3 | **3** |
| **propose** (new charter rule, 5.5) | 1 | **1** |
| **total graded rows** | **36** | **35** |

**Arithmetic correction, mine.** The audit's §8 summary table reported *"4 W, 22
A, 8 S"* totalling 34 + N. Recounting the rows individually gives **35 graded
rows** and 20 A before the re-grade, not 22 — the §8 table double-counted two
split dispositions (1.3's two limbs, and 5.4's `S`/`A`). Corrected here rather
than carried; this is the second arithmetic slip of mine this thread and both
were found by recounting rather than by re-reading.

## 3. The eight withdrawals, and where each is applied

**Withdrawal never means deletion.** Each site keeps its original text and gains
a dated pointer to this file.

| # | site | applied as |
| --- | --- | --- |
| 1.1 | `b52.json` `seventh_rung.finding` | dated amendment on the field; the "not iterative noise" limb kept and re-affirmed |
| 1.2 | `b52.json` `iterative_audit.finding`; `NOT_PASSING_REGISTER.md` | dated amendment; *"more iterations cannot reach"* survives, *"because the discretization does"* withdrawn |
| 1.3 | `B52_RUNG7_RESULTS.md` §2 | dated amendment |
| 1.4 | `W3_MESH_NOISE_FLOOR_RESULTS.md` §4; `b52.json` `replicate_mesh_control` | dated amendment carrying the replacement number |
| 1.5 | `B52_RUNG7_RESULTS.md` §6 | dated amendment; **R4's Ahmed turn is now the open question** it leaves behind |
| 1.6 | `W3_WING_VALID_FAMILY_RESULTS.md` §"Four for four" | dated amendment |
| 1.7 | `NOT_PASSING_REGISTER.md` §B-52 | dated amendment with the re-homing pointer |
| **6.1** | `R4_PREREGISTRATION.md` §1 | **NOT EDITED — frozen artifact.** Superseding note lives on `R4_ASYMPTOTIC_RESULTS.md` §5 (applied `88efa816`) |

**The frozen-artifact rule was applied to the re-grade too.** None of the five
promotions lands on a pre-registration. `R4_PREREGISTRATION.md` remains the only
frozen artifact in the set and remains byte-untouched.

## 4. What the withdrawal does NOT reach

- **The B-52's Cd values are not wrong.** Eight draws, all settled, all
  certified. What is withdrawn is the *shape* read from their differences.
- **The rung 7 → 8 increment survives** (`−2.78 × 10⁻⁴`, 0.06–0.16× of the
  increment uncertainty): unambiguously noise on every estimator, which is what
  `B52_RUNG8_RESULTS.md` already said. Grades 2.3, 2.4 stay **S**.
- **The ladder's verdict does not change**: `conclusive: false`,
  `not_conclusive_guard: order_window`, no reportable band. It is now better
  founded, not different.
- **`extrapolation_sanity` 0.15 is untouched** (chief ruling 6) and recorded as a
  standing weakness: its upper anchor is a Richardson extrapolate on a
  noise-dominated triple, which is not a stable quantity.
- **`test_uq.py` fixtures are untouched** (chief ruling 7): they are regression
  coverage over a frozen input array, and editing them would silently delete the
  coverage the guard exists to provide.
- **The first three increments are not disproven**, only unmeasured (§2, 1.3).
- **R4's Ahmed 25° turn is not withdrawn.** It has a single replicate pair, which
  is exactly the standing the B-52's turn had this morning. It is flagged as the
  open question 1.5 leaves behind, and is **not** graded here.
