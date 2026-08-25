# F12 gate-B probe — `rhoSimpleFoam` **DOES** print its convergence statement

**The hypothesis that gate B is unsatisfiable by `rhoSimpleFoam` on this box is
ELIMINATED.** The probe ran **outside the repository**, at
`/home/ubuntu/certonomous-runs/F12_gateB_probe_2026-08-25/`, and outside every
registered run path. The evidence beside this file is a **copy**; the executing
copy is at that path. Copied in because a finding that lives only outside the
repository is a finding that can be lost.

## 0. The result

| arm | solver | `residualControl` | rc | prints `SIMPLE solution converged`? |
| --- | --- | --- | --- | --- |
| 1 | **`rhoSimpleFoam`** | 1e-1 | **0** | **YES — "SIMPLE solution converged in 14 iterations"** |
| 2 | `simpleFoam` (control) | 1e-1 | 1 | **broken control, see §3** |

Arm 1 used **F12's own** `thermophysicalProperties`, `turbulenceProperties`,
`fvSchemes` and `fvSolution`, with **only the three `residualControl` numbers
changed**, on a trivial 400-cell box. It converged in 14 iterations, printed the
statement, printed `End`, and exited **rc = 0**.

## 1. What this ELIMINATES

1. **"Gate B is unsatisfiable by `rhoSimpleFoam` on this box at all."** Eliminated
   directly. The mechanism fires.
2. **"The `residualControl` key names or the `"(k|omega|e)"` regex do not match
   the solved fields."** Eliminated — the same block, with only the numbers
   changed, fired.
3. **"The `SIMPLE` sub-dictionary is missing something structural."** Eliminated —
   it is F12's own `SIMPLE` block.
4. **"`hConstThermo` / `sensibleInternalEnergy` with energy field `e` breaks the
   check."** Eliminated — F12's exact thermophysical dictionary was used.

**The generalisation drawn from the seven existing `rhoSimpleFoam` logs — that
none has ever printed it — does not support "it cannot".** This probe is the
eighth and it prints. Zero-of-seven was a property of those seven runs, not of
the solver.

## 2. WHY F2 DID NOT PRINT — no anomaly, and a reading correction

**`p` is solved MORE THAN ONCE PER ITERATION** — `nNonOrthogonalCorrectors 2`
gives F2 three `p` solves per iteration. `simpleControl` reads the **first**
solve's initial residual of each iteration. **A tail-read of the log returns the
last corrector's value instead.** Every other channel is solved once, so first
and last coincide — **which is why only `p` is affected, and why the artifact is
easy to miss.**

F2's final iteration, both readings side by side:

| field | FIRST solve (what the criterion reads) | LAST solve (what a tail-read returns) |
| --- | --- | --- |
| Ux | 9.6984e-07 | 9.6984e-07 |
| Uy | 1.8281e-05 | 1.8281e-05 |
| e | 7.1092e-06 | 7.1092e-06 |
| k | 9.9732e-07 | 9.9732e-07 |
| omega | 8.3760e-07 | 8.3760e-07 |
| **p** | **4.2657e-04 — ABOVE its 1e-4 threshold** | 3.2756e-06 |

**Iterations out of 2,000 where every channel's first solve sat below 1e-4: ZERO.**
F2 never satisfied its own `residualControl`; it ran to `endTime`. There is no
anomaly and no mechanism defect. The earlier report that *"every single channel
sat one to two orders of magnitude below its own threshold"* is **struck for `p`**.

## 3. Arm 2 is a BROKEN CONTROL and contributed nothing

It exited rc = 1 on `Entry 'div((nuEff*dev2(T(grad(U)))))' not found in
dictionary "system/fvSchemes/divSchemes"` — this lane reused F12's
**compressible** `fvSchemes` for an **incompressible** solver. It is reported as
broken rather than dropped. **It was not needed:** it existed to prove the search
string if arm 1 came back negative, and arm 1 came back **positive**, which
proves the search string by itself.

## 4. WHAT THIS DOES **NOT** ELIMINATE — and it is the real risk

**`p` is the hard channel, and on the closest analogue it is not converging.**
F2's first-solve `p` residual, by window:

| iterations | median first-solve `p` |
| --- | --- |
| 0–100 | 2.157e-02 |
| 400–500 | 1.319e-03 |
| 900–1000 | 6.386e-04 |
| **1400–1500** | **1.812e-04**  ← lowest |
| **1900–2000** | **3.839e-04**  ← risen again |

Median over 1500–2000 is **1.177×** the median over 1000–1500. **`p` descended,
bottomed out near 1.8e-4 — still above its own 1e-4 threshold — and then drifted
back up. It is not descending, and more iterations would not have reached it.**

**F12 asks 1e-6 on `p`. The closest analogue's `p` bottomed at 1.8e-4 and rose —
about 180× away, on a channel that is not converging.** On this evidence gate B
at 1e-6 is unlikely to be met by any F12 run within 6,000 iterations, and that
is **independent of the relaxation change attempt 3 proposes.** It is a
convergence question, not a mechanism question, and the mechanism question is
now closed.

## 5. Cost

| | value |
| --- | --- |
| registered before the probe | ≤ 2 core-min, seconds-long |
| **actual** | **0.00995 core-min** (arm 1 .322360750 s + arm 2 .274778245 s wall, ranks 1) |
| waste, named separately | arm 2's .274778245 s — a broken control that contributed nothing |
| dollars | **negligible, DERIVED at $0.0513/core-h, reported-by-owner, never measured** |

## 6. The registered roots were untouched, asserted before AND after

`rung1_fingerprint_before.txt` and `rung1_fingerprint_after.txt` are the sha256
of the sha256-list of every file under the fired rung-1 directory. **They are
equal** — the probe left it byte-unchanged. Rungs 2–5 were asserted absent before
and confirmed absent after. No gate, threshold, cap or label was touched, and
`residualControl` in the **registered** case was **not** loosened: that is a
threshold change and it is not available post-freeze.
