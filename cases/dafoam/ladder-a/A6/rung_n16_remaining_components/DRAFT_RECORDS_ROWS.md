# Drafted records — A6 N=16 remaining five components (LANE D)

**These are DRAFTS for the dafoam supervisor to append with `scripts/append_record.py`.**
**No numbers are assigned here** — the helper asserts max+1 per series and the tail is re-derived at
commit time (CLAUDE.md rule 11; D463/L-240). This lane did not edit `docs/LESSONS.md`,
`docs/DOCKET.md`, `docs/NUMERICS_KNOWLEDGE.md`, `INDEX.md`, `LADDER_A_STATUS.md`, `LAB_STATE.md`, any
charter or any frozen file, and did not run the helper.

Source of every figure below: `RESULTS.md` in this directory, commit `9d5029e8`; pre-registration
`baf4e68e`; predecessor items `66f42398` and `../rung_n16_np1/RESULTS.md`.

---

## SERIES: LESSONS — one row

### L-<next>. A trivial baseline at a deliberately wrong step is not merely inaccurate — it is irreproducible in magnitude AND sign, and it takes two draws to show it

**The rule.** Register the Charter-§2c/§4 trivial baseline **per item**, and buy it, rather than
citing a prior item's number for the same probe on the same case. The second draw costs ~2 primals
and converts the claim from *"the harness can return a large number"* into *"the harness returns a
**random** number when the step is wrong"* — which is the claim the clause actually needs. Where an
item does decline the re-buy, register the decline **conditionally**, with an assertable condition
(harness md5s, case identity, image identity) and the registered consequence that a mismatch voids
the decline.

**Why.** A single large error from a wrong step is consistent with two different worlds: a broken
harness, or a genuinely large derivative the good steps got wrong. Two draws of **opposite sign**
from the identical configuration are consistent with only one. The arithmetic is the tell: at
`s = 1e-8`, central FD divides by `2e-8`, so the solve-to-solve noise alone (`δ_repeat` = 2.2104e-06,
N-D15) manufactures a spurious derivative of order **1.1e+02** — of arbitrary sign.

**The incident.** A6 CRM N=16, 41,760 cells, np=1, `dafoam-idwarp-rot:v1`, 2026-08-22. The
`rung_n16_fixed_reference` item bought `patchV` idx1 at `step = 1e-8` and read
**+152.94101058174746** against an adjoint of `+9.01684e-03` — 99.9941%, registered as > 50%, HIT.
The `rung_n16_remaining_components` item **declined to re-buy it by name**, conditionally on the
harness md5s matching. `gen_arm.py` matched byte-for-byte; `run_arm.sh` could not, because it
hard-codes its own run root — **two lines, the run-root path and the container name**. The registered
void condition fired **before launch**, the baseline was re-bought, and it returned
**−28.746957145275864**: **100.031% and the sign reversed.** Same case, image, driver, DV, step and
objective; two runs; answers differing by a factor of 5.3 and in sign. **The condition nobody
expected to fire produced strictly better evidence than the decline would have.** (`9d5029e8` §4.3,
§9 Amendment 1.)

**Corollary.** An md5 condition on a helper script that legitimately must differ per run root will
fire every time. That is not a defect in the condition — write it anyway, and let it buy the control.

---

## SERIES: NUMERICS (N-D family) — three rows

### N-D<next>. A6 N=16's nine-component gradient table is complete: eight graded at 1.0432%, one structurally ungradeable

Measured 2026-08-22, `dafoam-idwarp-rot:v1`, 41,760 cells, np=1, `endTime 1000`,
`primalMinResTolDiff 1.0e4`, `primalMinIters 1000`, `printInterval 10`, central FD, `η = 1.0910e-05`,
clearance `C = |J|·2s/η`, graded only where `C ≥ 5` at the graded step and the two registered steps
agree within 10%.

| DV, idx | adjoint | FD (graded step) | rel err | `C` | plateau |
|---|---|---|---|---|---|
| `patchV` 0 | `+7.334000e-04` | `+7.375983890e-04` @ 3e-1 | 0.569% | 40.56× | 0.59% |
| `patchV` 1 | `+9.016840e-03` | `+8.932878291e-03` @ 3e-2 | 0.940% | 49.13× | 0.58% |
| `twist` 0 | `-2.100900e-03` | `-2.137369846e-03` @ 1e-1 | 1.706% | 39.18× | 4.17% |
| `twist` 1 | `-1.750730e-03` | `-1.774854641e-03` @ 1e-1 | 1.359% | 32.54× | 0.37% |
| `twist` 2 | `-1.469450e-03` | `-1.444417199e-03` @ 1e-1 | 1.733% | 26.48× | 3.65% |
| `twist` 3 | `-1.010980e-03` | `-9.929378034e-04` @ 1e-1 | 1.817% | 18.20× | 0.78% |
| `twist` 4 | `-6.277000e-04` | `-6.212861219e-04` @ 1e-1 | 1.032% | 11.39× | 2.31% |
| `twist` 5 | `-3.797300e-04` | `-3.782595043e-04` @ 2e-1 | 0.389% | 13.87× | 2.83% |
| **`twist` 6** | `-1.361900e-04` | **none at any feasible step** | — | max **2.42×** | **83.53%** |

**Vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` over the eight graded = 1.0432%, zero sign flips**;
the three previously-verified components alone reproduce the published **1.0099%**; the same eight
read at their lower registered step give **1.2921%**. `twist` idx6 is flagged and excluded by name —
`|J|` = 1.362e-04 is too small for any feasible step to lift over the floor, and the only remaining
lever is `η` itself. The predecessor's readings at the noise-dominated `1e-3` were **82.786%,
3.290%, 340.703%, 57.618%, 67.927%, 159.347%, 57.061%, 90.166%, 105.256%**. The adjoint never moved.
(`cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md`, 39.15 core-min.)

### N-D<next>. A clearance bar is a floor, not a target — a component just above `C = 5` is marginal even when its plateau passes

Across the five A6 N=16 components graded 2026-08-22, **every one improved as clearance rose**, and
the two whose lower step sat nearest the `C ≥ 5` bar improved the most: `twist` idx5 went **3.316%
at C 6.74× → 0.389% at C 13.87×** (8.5× better), `twist` idx2 **5.588% at C 7.65× → 1.733% at
C 26.48×** (3.2× better), against `twist` idx1's **0.996% at C 9.73× → 1.359% at C 32.54×** (flat).
**Clearing `C ≥ 5` makes a component gradeable; it does not make it converged.** The pre-registration
had attributed `twist` idx5's expected error to **truncation** at its larger step and widened its
band to 15% for that reason; the measurement shows the opposite — it was still **noise**-limited at
the smaller step. The prediction HIT and its stated mechanism was wrong, which is recorded as a
defect in the reasoning. **Read a component within ~2× of the bar as marginal and report its value at
both steps.**

### N-D<next>. FD steps can be sized mechanically from the stored `|J|` and `η` before the run, and the proxy predicted the measured clearance to within 8% on ten of ten

A6 N=16, 2026-08-22, first use. Rule, registered before any value existed: per component, `s_lo` =
smallest rung of a fixed ladder with predicted `C = |J_adj|·2s/η ≥ 5`; `s_hi` = smallest rung at ratio
≥ 2; graded step is the higher-clearance one, **never selected on agreement**. It chose four different
pairs across five components spanning **4.6×** in `|J|` — `{3e-2,1e-1}`, `{3e-2,1e-1}`, `{5e-2,1e-1}`,
`{1e-1,2e-1}`, `{1e-1,3e-1}` — which no single hand-picked pair could have covered. **All ten
registered steps cleared `C ≥ 5` on the measurement** (smallest 5.83× against a predicted 5.75×),
**all five plateaued** (worst 3.65% against a registered 10%), **none was flagged**.
**The limitation, stated because it is the rule's own blind spot:** it sizes the step from
`|J_adj|` — the quantity under test. Here the adjoint proved right, so the proxy was good; on a rung
where the adjoint is wrong by an order of magnitude the rule would register steps that cannot grade.
**That failure mode is unmeasured.**

---

## SERIES: DOCKET — one row

### D<next>. A6 N=16 is complete at eight of nine and Sanaa's N=29 gate has two registered readings — the choice is hers and the gap between them is one component worth ~5 core-min

**Status: PENDING — reserved to Sanaa, no agent may take it.**

`cases/dafoam/ladder-a/A6/rung_n16_remaining_components/` (`baf4e68e` pre-registration, `9d5029e8`
results) completed the rung's nine-component table: **eight graded, aggregate 1.0432%, zero sign
flips, `twist` idx6 flagged by name.** Sanaa's condition as held by the lane is *"N=29 is approved
ONLY if N=16 passes on the patched image."* **Both readings of "passes" were registered before the
measurement and neither was chosen:**

* **Reading 1 — `DAFOAM_CHARTER.md` §2 verbatim** (PASS requires ≤5% aggregate **and zero flagged
  components**): **`NOT MET`**, and **no FD arm can meet it**, because `twist` idx6 is structurally
  ungradeable on this rung at any feasible step.
* **Reading 2 — subset-complete** (every component graded inside the band or flagged by name with a
  measured reason, none merely un-measured): **`GATE REACHED`**.

**`N=29` is `NOT RUN` under either reading**; nothing was launched, staged, queued or costed for it.
**The gap between the two readings is exactly one component**, and the only lever that reaches it is
`η` itself — the unbought `useMeanStates: True` + `fieldAverage` item, **~5 core-min, \$0.004**,
priced on Sanaa's desk by `66f42398` §11 and still untaken. **Two decisions are hers: which reading
governs, and whether to buy the closing arm.** Nothing is filed, sent, uploaded or pushed.
