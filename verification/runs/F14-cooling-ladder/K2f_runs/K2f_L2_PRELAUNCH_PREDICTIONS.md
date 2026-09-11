# K2f_L2 — PREDICTIONS REGISTERED BEFORE L2 IS LAUNCHED

**Rung K2f, campaign F14. Written 2026-09-11 by a heat-transfer `lab-lane`,
committed BEFORE `K2f_L2` was built or launched.**

**These GRADE NOTHING.** They alter no gate, threshold, band, cap or label, and
they are not an amendment to the frozen registration
(`docs/campaigns/F14-cooling-ladder/K2f_PREREGISTRATION.md`, frozen at
`e42894dfc`). §13 of that document fixes the form: a prediction is scored HIT or
LOSS and reported either way, and none can move a verdict. They are committed
first so they cannot be chosen to fit the answer.

**State of the disk when this was written:** `K2f_L1` complete and graded on the
frozen path (rule 4 DONE, all six clauses); the comparator REFUSED at exit 2 on
§6.2's planted-cycle positive arm and produced no verdict. **`K2f_L2` does not
exist — no case directory, no `STATUS.K2f_L2`, no `log.solve`.** Checked by
`test -d` on disk, not by asking git.

---

## `P-K2f-L2-COST` — the rate model reproduces

**L2's contention-free cost is 89.35 core-min**, re-derived from `K2f_L1`'s
MEASURED 0.265333 core-s/iteration on §10.1's `N^1.568` exponent
(`N2/N1` = 3.37500, factor 6.7349).

- **HOLDS** if L2's measured contention-free cost lies in **67.0 – 111.7**
  core-min (±25 %).
- **LOSES** outside that band.

This is `P-K2f-3` of the frozen registration, instantiated with a number. Its
registered weakness is carried unchanged: the exponent was fitted on K2d's own
L1→L2 pair, so this tests whether the scaling **reproduces across rungs**, not
whether it was derivable in advance.

## `P-K2f-L2-RANGE` — the monitored quantity acquires a signal

`T_in,max` at `K2f_L1` spanned **6.0922e-04 K** over the whole run, against a
registered rack ΔT of **12 K**: `θ_max` = **4.88e-05** where the gate was
written for order 0.1–1. The quantity had essentially no signal.

- **HOLDS** if `T_in,max`'s run-range at L2 is **≥ 1.0e-02 K** (≥ 16× L1's).
- **LOSES** if it is **< 1.0e-02 K**.

*Basis:* K2d measured L2 as the first level to lose steady convergence
(Ux residual floor 1.75e-04 against L1's 9.8e-10, limit-cycling from ~800).
Cross-aisle transport is the only mechanism that can move a rack-inlet **patch
average** off supply temperature. **Named weakness: 1.0e-02 K is a threshold of
significance, not a computed prediction** — no model here predicts the
magnitude, and even a HOLD at this level leaves `θ_max` near 1e-3, still far
below the order the gate was written for.

## `P-K2f-L2-ARM` — §6.2's positive arm PASSES at L2

**Predicted: the frozen comparator does NOT refuse at the `K2f_L2::T_in,max`
planted-cycle positive arm.**

Criterion, measured on L1's own base by driving the frozen
`planted_cycle_control` at f = 3, 4, 4.5, 5, 5.5, 6, 7, 8: the arm classifies
`CYCLING` once the window's monotone drift falls to **≈ 0.66 × the planted
peak-to-peak** (`trend_frac` crosses §6.1's 0.25 ceiling between f = 6,
`trend_frac` 0.3030, and f = 7, `trend_frac` 0.2087). At the registered 2× plant
the peak-to-peak is `8.0e-04 × run_range`, so the arm passes when

> **window_drift / run_range ≤ 5.3e-04.**

**`K2f_L1` measured 1.7399e-03 — a factor 3.3 too drifty, which is why it
refused.**

- **HOLDS** if L2's measured `window_drift / run_range` ≤ **5.3e-04** and the
  comparator does not refuse at this arm.
- **LOSES** if it exceeds 5.3e-04 and the comparator refuses again.

*Basis, and it is independent of `P-K2f-L2-RANGE`:* a limit-cycling series has
no dominant monotone trend, so `trend_frac` collapses whatever the run-range is.
K2d measured 6 sign changes on Ux over L2's final 400 iterations.
**Named falsifier for the mechanism, not just the number: if `K2f_L2` instead
converges deeply as `K2f_L1` did (Ux 6.7e-10, 9.2 decades), the residual creep
returns, `trend_frac` stays above 0.25, and this prediction LOSES.**

**If it LOSES, that is not a third instrument failure.** It is the rung
reporting that the registered quantity has no signal on this module — a finding
about K2a's rack-row case, not about the comparator.

---

*Nothing was sent, filed, uploaded, registered, posted or commented outside this
box (rule 7). No gate, threshold, cap or label is altered by this file.*

---

## SCORING — appended 2026-09-11 after `K2f_L2` completed. **ALL THREE LOSE.**

`K2f_L2` is **DONE** on the frozen rule-4 instrument (all six clauses, exit 0);
`wall_s` 960, 4 ranks, `rc=0`, `note=clean`. The frozen comparator **REFUSED
again at exit 2**, and on the **same L1 arm** — it iterates levels in order and
never reached L2. **No verdict exists for either level.** The scores below were
taken by calling the frozen `planted_cycle_control` / `classify_monitor` path on
L2's own series; they **grade nothing** and produce no verdict.

| prediction | predicted | measured | score |
|---|---|---|---|
| `P-K2f-L2-COST` | 89.35 core-min cf, band 67.0–111.7 | **58.518** cf (64.000 gross) | **LOSS** |
| `P-K2f-L2-RANGE` | `T_in,max` run-range ≥ 1.0e-02 K | **6.9584e-04 K** | **LOSS** |
| `P-K2f-L2-ARM` | §6.2 positive arm PASSES | **FAILS** (`DRIFTING`) | **LOSS** |

**`P-K2f-3` of the frozen registration §13 also LOSES** on the same figures:
L1's measured rate extrapolated at `N^1.568` predicted 89.35 core-min against
L2's measured contention-free 58.518 — **ratio 0.655, outside its ±25 % band.**
The measured L1→L2 exponent is **`N^1.2937`**, not the registered 1.568.

### Why `P-K2f-L2-ARM` lost, and the mechanism was RIGHT while the prediction was WRONG

I predicted the arm would pass **because L2 would limit-cycle and `trend_frac`
would collapse.** **L2 does limit-cycle** — Ux floors at 1.756e-04 with 10 sign
changes over the final 400 iterations, reproducing K2d's L2 — **and
`trend_frac` did collapse, from 0.7648 at L1 to 0.0048 at L2.** The predicted
mechanism is confirmed and the prediction still failed, on a limb I did not
consider: **`sign_changes` = 1, below §6.1's required 3.**

**The control has a CEILING as well as a floor, and the registration relates the
plant to neither.** The 2× plant is sized against the **run-range**; whether it
is detectable depends on the base's **window** behaviour. At L2 the base's own
window spread is **7.756e-05 K = 139.3× the planted peak-to-peak**, so the plant
cannot influence the first-difference sign pattern at all. Driven at f = 2, 10,
50, 100, 200, 400, 800, the arm recovers `CYCLING` **only at f ≈ 200 — a
hundred times the registered plant** — and the crossing tracks
`planted_p2p / window_spread ≈ 0.72`, with `trend_frac` never leaving ~0.005.

**Four arms across two levels, three of them fail, by two opposite mechanisms:**

| level / quantity | limb that failed | figure |
|---|---|---|
| L1 `T_in,max` | trend (FLOOR) | drift / planted p2p = **2.17**, `trend_frac` 0.7648 |
| L1 `U_ha` | — **PASSES** | drift / planted p2p = 0.0003, `trend_frac` 0.0000 |
| L2 `T_in,max` | sign changes (CEILING) | window spread / planted p2p = **139.3**, `sign_changes` 1 |
| L2 `U_ha` | trend (FLOOR) | drift / planted p2p = **15.4**, `trend_frac` 0.9212 |

### The finding `P-K2f-L2-RANGE` bought, and it is the one that matters

**`θ_max` = 4.678e-05 at L2 against 4.876e-05 at L1 — essentially unchanged
across a 3.375× refinement.** `T_in,max` spanned **6.9584e-04 K** at L2 against
6.0922e-04 K at L1, a factor **1.14**, where the prediction needed 16. **Rack
inlet air is supply air at both resolutions**, on a registered rack ΔT of 12 K,
and the T field is healthy at both (L1 289.000 → 301.000 K).

> **The registered gate quantity has no signal on K2a's rack-row module at
> either resolution run.** `G1`, `G2` and `G3` are all functions of `T_in,i`.
> **This is a finding about the case, not about the comparator.**

**`U_ha` is the contrast and it DOES have a signal**: run-range 9.1216e-02 m/s
at L2 against 3.5299e-02 at L1. But its `trend_frac` of 0.9212 says **`U_ha` has
not plateaued at `endTime` 3000** — the one outcome §10.3 registers as the case
where 3,000 iterations may be too short.

**`P-K2f-1` CANNOT BE SCORED and is NOT scored here.** It is written against the
`G-CYCLE` **state**, which the comparator refused to produce. Scoring it from
residuals would score it on a quantity it was not written against — K2d §17.6
refused exactly that, and so does this record.

*Nothing was sent, filed, uploaded, registered, posted or commented outside this
box (rule 7). No gate, threshold, cap or label is altered by this section.*
