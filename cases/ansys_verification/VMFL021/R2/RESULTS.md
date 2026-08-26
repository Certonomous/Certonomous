# VMFL021-R2 — Cavitation Over a Sharp-Edged Orifice, case A — **`GATE REACHED`**

**Graded 2026-08-26 by `ansys-verification-supervisor`** from the frozen comparator
`grade_vmfl021_r2.py`, blob-verified against HEAD before it ran. Manual **p. 85**.

## 1. The verdict and its numbers

| | |
|---|---|
| **Verdict** | **`GATE REACHED`** (registered ceiling) |
| Gate quantity | discharge coefficient **Cd = \|Q_inlet\| / (A2 · V_theo)**, flux read at the pure-liquid inlet |
| Lab value, L3 | **Cd = 0.634868** |
| Reference | **Cd = 0.620** — Nurick (1976), experimental, manual p. 85 |
| Deviation | **2.398 %** against a frozen band of **5 %** |
| Roache triple | **CONVERGING** — d32 = 0.02195, d21 = 0.006570, R = 0.29926 |
| Observed order | **p = 1.7405** (formal 1) |
| **GCI (Fs = 1.25)** | **0.5524 %** |
| Richardson extrapolate | Cd_ex = 0.63206 |
| Cost | **32.933 core-min** measured, est ~40, cap 180 → ratio **0.823**; **$0.028 derived** |

## 2. The regime precondition — why this gate is evaluated on the physics it was registered for

A discharge coefficient for a **cavitating** orifice is meaningless if the solution never cavitated. All three levels satisfy the registered precondition: **alpha_min = 0.0638 / 0.0031 / 0.0001**, all below the 0.01 threshold, all **CAVITATING**. All three also **PLATEAU** (ptp/range **0.104 / 2.434 / 0.002 %**; CoV 0.017 / 0.188 / 0.000 %; windows n = 811 / 1 791 / 3 784), so rule 5 step 1 is cleared **before** the triple is classified.

## 3. Planted-zero control

**1.234e-06 m³/s** planted into L3's real `surfaceFieldValue.dat` and read back as **1.2340000000000766e-06**. The reader is shown able to see a non-zero, so its zeros are evidence.

## 4. Strict completion (rule 4) — a DECLARED departure, not a silent one

`rc = 0`, an `End` line, and fields present at `endTime = 0.003` at every level; age guard passed.

The `ExecutionTime` count is **12 288** lines at L3 against a nominal ~3 000 000 steps at `deltaT = 1e-9`. **This is not an omitted conjunct.** Line 114 of the frozen pre-registration registers *"strict completion (**rule 4, adaptive-dt form**)"* **by name**, with Amendment 3's endTime/writeInterval assertion and field-dir-at-endTime check as the substitute, and the freeze at **22:28:38Z** precedes the first run artifact at **22:29Z**. **A declared departure is a verdict; a silent one would have been `NOT A RESULT`.**

**Forward note, changing nothing frozen:** *"rule 4, adaptive-dt form"* is cited by name rather than written out. A future registration writes the substitute conjunct in full.

## 5. What R2 fixed

Attempt 1 was ungradeable for **machinery** reasons only — a `controlDict` write-control fault that left L1/L2 with a `0` directory only, and a missing `RUN_RC.txt` at L3 after a supervisor dispatch error killed the lane mid-run. **Neither defect touched the reference, gate, geometry, solver or physics**, which is why R2's inherited cost estimate held to 17.7 %.
