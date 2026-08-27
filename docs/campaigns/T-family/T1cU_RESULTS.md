# T1c-U results — the unheated upstream arm (`D_Ts_Re25_U` and `L_Ts_U`)

Read 2026-08-27. **NO VERDICT FROM THE FIXED VOCABULARY APPLIES TO THIS RUNG, and
that is by its own registration, not an omission here.**

`DTS_U_registered.json` `.status`, quoted in full:

> **"DIAGNOSTIC, NOT GRADED. No band, cannot PASS or GATE FAIL, and no T1c verdict
> moves on it (the frozen text's own closing clause)."**

So this record reports **completion** and the **one registered reading** the arm
carries, and it stops there. It does not print a `PASS`, a `GATE FAIL`, a
`GATE REACHED` or a `NOT A RESULT`, because a rung with no band cannot earn any
of them.

Registered at `verification/runs/T-family/T1_runs/DIAGNOSTIC_PREDICTION.md:786`,
frozen `6a0d7f45` (2026-08-21). Run root `verification/runs/T-family/T1_runs/`.
Readings at `verification/runs/T-family/T1_runs/log.convergence_dts_u.20260827T170453Z.txt`.

---

## 1. The freeze — two commits, and BOTH precede first compute

| what | frozen at | when |
| --- | --- | --- |
| the predictions and the falsifiers | `6a0d7f45` | 2026-08-21 16:40:34Z |
| the build/run instruments (mesh, `endTime`, caps, launcher, completion rule) | `994daa49` | **2026-08-26 22:52:47Z** |
| **first compute** | — | **2026-08-27 09:01:55Z** |

**The instrument freeze precedes first compute by 10 h 09 m** (rule 2). The split
is legitimate and the registration declares it: the later commit is *"the
pre-first-compute build/run amendment … it adds the mesh, endTime, caps, launcher
and completion rule and **ALTERS NO REGISTERED PREDICTION, BAND, THRESHOLD OR
FALSIFIER**."*

**Hashes, verified rather than assumed:**

| file | frozen blob | on disk | |
| --- | --- | --- | --- |
| `analyse_t1c.py` (the reading instrument) | `3d566802` **at `6a0d7f45`** | `3d566802` | MATCH |
| `DTS_U_registered.json` | `0a589604` at `994daa49` | `0a589604` | MATCH |
| `mark_done_dts_u.py` | `156d8ffd` at `994daa49` | `156d8ffd` | MATCH |
| `build_dts_u.py` | `95308905` at `994daa49` | `95308905` | MATCH |
| `run_one_dts_u.sh` | `0e68db89` at `994daa49` | `0e68db89` | MATCH |

**The reading instrument is byte-identical to its state on 2026-08-21** — six days
and one build amendment later, the function that judges convergence has not
moved.

## 2. Completion — six of six (rule 4)

`mark_done_dts_u.py`: **`DONE`** on `D_Ts_Re25_U_{c,m,f}` and `L_Ts_U_{c,m,f}`,
rc 0. All six `STATUS_u.*` read `rc=0 … capped=no checkmesh_rc=0 note=clean`.
The registration classes `capped` as **INFRASTRUCTURE** and never a completion
conjunct (L-342), and lists `ExecutionTime` count == `endTime` (`deltaT` 1)
among the physics conjuncts.

## 3. The registered convergence criterion — twelve of twelve CONVERGED

`analyse_t1c.iterative_convergence`, last two written checkpoints
(**38000 → 40000** on every case), `max|a−b| / (max(b)−min(b)) ≤ 1e-6`:

| case | cells | T: max\|Δ\| | T: relative | U: max\|Δ\| | U: relative |
| --- | ---: | ---: | ---: | ---: | ---: |
| `D_Ts_Re25_U_c` | 4 800 | **0.000000e+00** | 0.000000e+00 | 6.245005e-16 | 1.647726e-14 |
| `D_Ts_Re25_U_m` | 12 288 | **0.000000e+00** | 0.000000e+00 | 2.445547e-16 | 6.486469e-15 |
| `D_Ts_Re25_U_f` | 31 212 | **0.000000e+00** | 0.000000e+00 | 2.463307e-15 | 6.553109e-14 |
| `L_Ts_U_c` | 4 800 | **0.000000e+00** | 0.000000e+00 | 2.095546e-15 | 1.394681e-14 |
| `L_Ts_U_m` | 12 288 | **0.000000e+00** | 0.000000e+00 | 1.720846e-15 | 1.145019e-14 |
| `L_Ts_U_f` | 31 212 | **0.000000e+00** | 0.000000e+00 | 1.720846e-15 | 1.145743e-14 |

**Every temperature field is BIT-IDENTICAL between iterations 38 000 and 40 000**,
and every velocity field agrees to 1e-14–1e-16 relative — round-off, nothing
more. **This is exactly the check whose own docstring records why it exists**: a
fine case once reached `endTime` *"with its temperature field still moving by
4.081 K"* while the coarse and medium were bit-identical, and *"graded as if
converged, it put Nu at 4.622 against a true 4.364 and turned the grid triple
OSCILLATORY — a verdict about the mesh that was really a verdict about the
iteration count."* Here all six are settled, and the `endTime` ground (*"this
domain is 1.2× longer, so … 40000 is 1.33× and leaves margin"*) held.

## 4. THE ZEROS ARE EVIDENCE — planted control (rule 3)

**Six exact zeros in one column is precisely the pattern that must not be
believed on sight.** The frozen reader was shown able to report the other
outcome, by planting **BY LINE INDEX** into a **scratch copy** and reading it back
through the same function:

| scratch copy | plant | frozen reader returns |
| --- | --- | --- |
| `D_Ts_Re25_U_c/40000/T` line 23: `300.0000000000005` → `301.234` | +1.234 K | `NOT_CONVERGED`, `max_change` **1.234000**, relative 1.170835e-01 |
| `L_Ts_U_f/40000/T` line 23: `300.0000000000001` → `301.234` | +1.234 K | `NOT_CONVERGED`, `max_change` **1.234000**, relative 1.208901e-01 |

The reader recovers the plant **exactly**, on both ladders, and flips its state.
**The live cases were never written to** — the plants went into copies outside the
run tree, which were deleted afterwards. A first attempt at the plant was made by
**string substitution** and produced the corrupt token `301.234.0000000000005`,
which the reader correctly refused to parse; **the plant was redone by line
index**, which is the form L-340 and this lab's own lesson prescribe. The failed
attempt is recorded rather than quietly dropped.

## 5. WHAT THIS RECORD DOES NOT CONTAIN, AND WHY IT WOULD BE WRONG TO ADD IT

The 2026-08-21 text registered a **diagnostic question**, not a gate: whether the
Péclet-dependent term is the inlet-corner flux (in which case the Re 25 − Re 100
difference *"collapses from +0.37 pp towards the combined bands (about
0.05 pp)"*) or developed-flow axial conduction (in which case it *"persists within
the combined bands"*).

**No instrument capable of answering it is registered, and this lane did not
write one.** Checked, not assumed: `DTS_U_registered.json` carries **no
`comparator`, `graded_rows`, `bands`, `grading` or `falsifier` key**, and
`analyse_dts.py`'s `LADDERS` list (`:82`) covers only the parent `D_Ts` ladders —
the U cases are not in it.

**Writing a reader now, with the six converged fields already on disk, would be
building the measurement instrument after seeing the data.** That is the single
thing prediction-first pre-registration exists to prevent, and it is not made
acceptable by the arm being labelled diagnostic. **The diagnostic reading is
therefore `NOT AVAILABLE`**, the fields are complete and converged and will still
be there, and answering the Péclet question needs **a new registration that names
its reader and its stations before it runs** — which is not this lane's call.

## 6. Cost — rule 12, and the registration ASKED for this comparison in advance

- **Predicted: POINT 234.122 core-min**, built from **per-level parent measured
  rates** so that *"the level-to-level rate drift … is carried rather than averaged
  away"*. Cap total **735**.
- **Measured: 277.300 core-min** = (585 + 1 741 + 6 543 + 654 + 1 776 + 5 339)
  wall s × 1 rank ÷ 60.
- **Gross = cleaned.** `D_Ts_Re25_U_f` (6 543 s) and `L_Ts_U_f` (5 339 s) exceed
  the 3 600 wall-s stall figure and **neither is a stall**: rc 0, `capped=no`,
  and both are bit-identical in T across their last 2 000 iterations. **WASTE:
  0.000 core-min.** **No case exceeded 43.6 % of its cap**; the total is **37.7 %
  of 735**.
- **Ratio actual/POINT 1.1844.** Per case: `L_Ts_U_c` 1.442, `L_Ts_U_m` 1.393,
  `D_Ts_Re25_U_f` 1.256, `D_Ts_Re25_U_m` 1.163, `D_Ts_Re25_U_c` 1.063,
  `L_Ts_U_f` 1.055.
- **THE REGISTERED SCRATCH PROBE, NOW SCORED — and the registration set this up
  deliberately.** It measured **6.494e-06 core-s per cell-iteration**, **2.266×
  the parent's own c-level rate**, on 2026-08-26 22:49Z, and attributed it to
  *"box contention — several teams' solves were live at the probe"*. Crucially it
  said: *"Recorded here rather than folded into the POINT, so the completion
  calibration can attribute the gap (rule 12) instead of absorbing it."*
  **The realised c-level rate is 3.0469e-06, just 1.063× the parent rate. The
  probe over-predicted contention by 2.13×.** The arm ran 09:01–11:31Z on a much
  emptier box than the one it was probed on.
- **The CAP reasoning was sound even though the probe number was not.** Caps were
  set at **3.2× POINT** explicitly to absorb the probe's 2.27× *"because rule 12
  stops the run at the cap and an overrun gets no new budget"*. Nothing came close
  to a cap. **A probe used to size a CAP is being used correctly; the same probe
  used as a POINT would have over-priced this arm by more than 2×, and the
  registration is right not to have done so.**
- **Attribution: contention, and it is the only term needed.** The rate ratios
  track the box, not the mesh — the two coarse cases that ran first
  (`L_Ts_U_c` 1.442) are the dearest and the last fine case (`L_Ts_U_f` 1.055)
  the cheapest, the opposite of the mesh-scaling signature seen in T13/T4b.
  **CARRY FORWARD: a contention probe is a CAP-sizing instrument with a shelf life
  of hours, not a rate estimate. Measure it again at launch, or size the cap from
  it and price the POINT from uncontended parent rates — which is what this
  registration did.**
- **Dollars, DERIVED, NOT MEASURED** at $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5): **$0.2371** against POINT $0.2002 and cap
  $0.6284.
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit from the tail.

## 7. Disclosures

- **This rung has no verdict and none is invented.** It is `DIAGNOSTIC, NOT
  GRADED` by registration, and **no T1c verdict moves on it.**
- **The question the arm was built to answer is not answered here** (§5), and the
  reason is that answering it would require writing a reader after seeing the
  data.
- The corrupt first plant is disclosed in §4 rather than dropped.
- No frozen file edited (rule 6). **Nothing sent, filed, uploaded, posted or
  registered outside this box** (rule 7).
