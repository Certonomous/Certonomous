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
