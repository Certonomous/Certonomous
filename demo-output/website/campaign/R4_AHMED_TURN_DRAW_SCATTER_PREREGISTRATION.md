# Ahmed 25° — is the ladder's turn built on an unmeasured draw distribution too?

**Pre-registration, written 2026-08-10 before any new mesh exists.** Chosen under
the chief's standing directive (*pick the highest-value Cases-family work, price
it, report the choice*). Leg 1 is **8.6 core-min**, inside the ~10 core-min the
directive leaves to my judgement; **leg 2 is priced and NOT taken.**

Model rule per SUPERVISION_CHARTER §5: session default. Stated, not silent.

---

## 1. Why this, out of everything available

**The B-52's turn was withdrawn today** (`B52_TURN_WITHDRAWAL_2026-08-10.md`,
chief ruling `7abb0ba3`) on the finding that its published increment was
`max(rung 6) − min(rung 7)` of eight same-recipe draws. **The Ahmed 25° turn is
the last surviving leg of the cross-family claim that withdrawal broke** —
*"two of this lab's two genuine single-knob ladders now both turn"* — and I
flagged it in that record as the open question left behind.

**A zero-compute sweep of the stored ladders, run before choosing:**

| | |
| --- | --- |
| stored ladders in `models/curriculum/uq-studies/` | **12** |
| carrying **any** draw-scatter evidence | **3** (`b52`, `naca0012_wing`, `naca4412_wing`) |
| carrying **none** | **9** |
| publishing a `reportable_band` today | **0** — every one is `conclusive: false` |

So the corpus-wide exposure is real but bounded: nothing is currently *published*
on an unmeasured draw distribution. What makes Ahmed 25° the right target is not
exposure, it is **load**: its turn is the last support under a withdrawn
cross-family claim, and `ahmed_25.json` carries `band_rel = 0.238` — the largest
in the corpus after the two wings.

**And the Ahmed turn is in a far stronger position than the B-52's ever was**,
which is what makes the test interesting rather than a formality:

| | B-52 | **Ahmed 25°** |
| --- | --- | --- |
| replicate pair at a turn rung | rung7/rung7b: **47%** of the increment | c4/c4b: **11%** of the increment |
| `T̂` from that pair | **1.69** | **7.33** |
| reaches `residualControl`? | never, at any iteration count | yes, every rung (158–623 iters) |

**The asymmetry that makes it worth measuring:** the Ahmed's replicate pair sits
at **c4**, the turn's upper end. **Its lower end, c3, has n = 1** — and the B-52's
turn dissolved precisely because one of its two ends was a single draw that
turned out to sit at an extreme of its own distribution. **c3 is the untested
end**, and it is the cheapest rung in the ladder.

## 2. The power arithmetic, before spending — leg 1 does NOT reach a verdict

Stated up front because the same check saved the B-52 closure arm from being
mis-sold, and because the temptation to report leg 1 as a verdict is the obvious
failure mode here.

`T = increment / √(s_c3² + s_c4²)`, 90% CI via Welch. At `T̂ ≈ 7.33`:

| n(c3) | n(c4) | ν | 90% CI on T | verdict | extra core-min |
| --- | --- | --- | --- | --- | --- |
| 1 | 2 | 1.00 | [0.46, 14.37] | indeterminate | — (today) |
| **3** | **2** | 2.67 | **[2.26, 12.07]** | **indeterminate** | **+8.6 (leg 1)** |
| 4 | 2 | 3.00 | [2.51, 11.83] | indeterminate | +12.9 |
| **3** | **3** | 4.00 | **[3.09, 11.29]** | **SIGNAL** | **+26.2 (legs 1+2)** |

> **Leg 1 alone cannot declare SIGNAL** — the CI lower bound reaches 2.26 against
> a 3.0 threshold. **A verdict needs one more c4 draw as well, and that is
> leg 2.** I am not taking leg 2 without approval, and I will not report leg 1 as
> a verdict.

## 3. What leg 1 *does* buy — the test that actually decided the B-52

The chief's ruling on the B-52 rested on **Ground 2: the arithmetic of how the
number was constructed**, which needs no CI at all. Leg 1 runs exactly that test
on the Ahmed.

**Statistic: how far does the turn move when the single c3 draw is replaced by
the mean of three?**

- published increment (c3 → c4): **+8.895 × 10⁻⁴**
- with c4 already re-estimated over its existing pair {c4, c4b}: **+9.379 × 10⁻⁴**
  (moved 5.4% — the c4 end is already stable)
- leg 1 supplies `mean(c3)` over three draws and the re-estimated increment

> ### The bar, fixed now
> | branch | criterion on the re-estimated increment | meaning |
> | --- | --- | --- |
> | **SURVIVES** | within **25%** of +8.895e-4 **and** same sign | the Ahmed turn is not an artifact of a single draw. The B-52's failure mode is **absent here**, and the two bodies genuinely differ |
> | **DISSOLVES** | below **50%** of it, **or** sign flips | the Ahmed turn joins the B-52's fate and the cross-family claim loses its last leg |
> | **PARTIAL** | between 50% and 75% of it, same sign | reported as partial; no branch claimed |

**Weak test named as weak:** *"is the original c3 an extremum of its three
draws?"* is **not** used as a criterion. Under no selection at all, a draw is an
extremum of three with probability 2/3 — at n = 3 that question is nearly
uninformative, and it is recorded here so it cannot be reached for afterwards.
The criterion is the movement of the increment, which is what the B-52 ruling
actually turned on.

**Secondary, reported not scored:** `s_c3` over the three draws, against c4's
`s ≈ 8.58 × 10⁻⁵`. Whether the two rungs share a σ is exactly what the B-52 arm
found it could not establish.

## 4. The draws, and the gates

Template: `campaign/R4_runs/c3` (complete case, `system/` + `constant/` +
`0.orig`). Recipe held: surface level (3 4), feature level 2, region level 1,
4 MPI ranks scotch, `residualControl` as the stopping rule — **only the
background blockMesh division triple differs**, which is this lab's only draw
mechanism for snappyHexMesh.

| draw | divisions | vs c3's (98 21 59) |
| --- | --- | --- |
| **c3b** | **(99 21 58)** | ny held at 21 |
| **c3c** | **(97 21 60)** | ny held at 21 |

`ny` is held per `B52_RECIPE_NOTE_BACKGROUND_PRODUCT.md`: it is the division that
steps the delivered cell count, and the σ being measured is **draw scatter at
fixed delivered resolution**, conditional on the G1 gate below.

**Gates**, carried unchanged from the B-52 replicate arms: **G1** delivered cells
within ±2.0% of c3's 254 911 (249 813–259 009), re-draw allowed and every refused
attempt recorded, ≤2 re-draws; **G2** mesh birth certificate written at creation,
`certificate_admits` before launch; **G3** the rung must reach `residualControl`
(the Ahmed ladder's own rule — an unconverged rung is not ladder evidence);
**G4** lever echo, equality over lever dictionaries and pre-solve `0.orig` only.
**4 ranks on every draw** — rank count is fixed across this family and varying it
would inject a decomposition artifact into the quantity being measured.

## 5. Cost, from measured bases

| | basis | core-min |
| --- | --- | --- |
| c3 mesh | R4's own cost table, ≈0.9 per rung | 0.9 × 2 = **1.8** |
| c3 solve | **measured: c3 ClockTime 50 s at 4 ranks = 3.39** | 3.39 × 2 = **6.8** |
| **leg 1 total** | | **8.6** |
| leg 2 — one more c4 draw | mesh 0.9 + solve **16.7 to 71.9** | **17.6–72.8** |

**Leg 2's price is a FLOOR, not an estimate, and the reason is measured:** c4
reached `residualControl` in 623 iterations and c4b — the same recipe at the same
resolution — needed **1 668**, a factor of 2.7. Iterations-to-converge is itself
draw-dependent on this body, so a third c4 draw could cost anywhere in that
range. Recording it as a floor is the discipline the calibration scorecard names
and the same one applied to F5c's Stage B.

## 6. What will NOT be claimed

- **No verdict on the Ahmed turn from leg 1** (§2). No SIGNAL, no NOISE.
- No change to `ahmed_25.json`'s band, order, or verdict; it is `conclusive:
  false` and stays so.
- σ measured here is **conditional on the G1 gate** and is not unrestricted
  draw-space scatter.
- The B-52's withdrawal is not revisited by this arm in either direction.
- Nothing about `ahmed_35` or any other stored ladder is inferred from this one.
  Two geometries have already behaved two ways in this lab.

*Nothing below this line existed when this document was committed.*
