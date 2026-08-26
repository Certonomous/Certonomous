# VMFL023 — Oscillating Laminar Flow Around a Circular Cylinder — **`GATE REACHED`**

**Graded 2026-08-26 by `ansys-verification-supervisor`** from the frozen comparator
`grade_vmfl023.py`, blob-verified against HEAD before it ran. Manual **p. 89**.

## 1. The verdict and its numbers

| | |
|---|---|
| **Verdict** | **`GATE REACHED`** (registered ceiling; the reference is a measured correlation, so `PASS` is not available) |
| Gate quantity | Strouhal number **St = D / (T · U)**, shedding period `T` from lift-force zero-crossings |
| Lab value, L3 (384 × 128) | **St = 0.165993** |
| Reference | **St = 0.165** — experimental St–Re correlation, White (1994) / Kim & Lee (2002), manual p. 89 |
| Deviation | **0.6019 %** against a frozen band of **3 %** |
| Roache triple | **CONVERGING** — d32 = 5.252e-03, d21 = 1.394e-03, R = 0.265359 |
| Observed order | **p = 1.9140** (formal 2) |
| **GCI (Fs = 1.25)** | **0.3791 %** |
| Richardson extrapolate | f_ex = 0.165490 |
| Cost | **228.667 core-min** measured, est 210, cap 350 → ratio **1.089**; **$0.195 derived** |

## 2. Controls, and why the zero is evidence

The planted-zero control is **two-sided**, which is stronger than the rule-3 minimum:
- a sinusoid planted at **St = 0.165000** was **recovered as 0.165000** — the reader is shown able to see a known frequency;
- a **flat (dead) signal was REFUSED** — the reader is shown unable to invent one.

## 3. Strict completion (rule 4) — including the clause that nearly went the other way

`rc = 0` at every level; an `End` line at every level; **`ExecutionTime` count = 60 000 = endTime/deltaT = 300/0.005** exactly; `U` and `p` present at endTime; age guard passed; max Courant **0.5239** < 1; stationarity first-half ptp 6.62990e-01 vs second-half 6.63099e-01 (**0.02 %** against a frozen 5 %).

**The `last time == endTime` clause.** L3's final time directory is **299.9999999998** against an `endTime` of **300**, and the pre-registration registers that check with the words *"NO DEPARTURE IS DECLARED"*. **This was not settled by argument.** The frozen comparator implements the clause as `abs(t_last - ENDTIME) > 1e-6 -> refuse("C3")`; the drift is **2e-10**; the instrument **accepts**. The tolerance was frozen before compute and so could not have been chosen to fit the answer — which is the entire evidentiary content of a freeze.

## 4. What this row is and is not

It is a **code-to-correlation gate met with a converging grid triple and a sub-0.4 % GCI**. It is **not** a `PASS`: the reference is measured, not a closed form this lab evaluates itself.
