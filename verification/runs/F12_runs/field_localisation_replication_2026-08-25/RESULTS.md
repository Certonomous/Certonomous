# F12 — THE FIELD-LOCALISATION PROBE, FROZEN REPLICATION

**cfd lane, 2026-08-25.** Pre-registration
`verification/campaign/F12_FIELD_LOCALISATION_PREREGISTRATION.md`, commit `56d72ac3`,
blob sha256 `bca4074a7de26f478115a1efc1706c9cba6daedab8174cf72c202566d534b667`,
**frozen before this compute** and check-4 verified personally by the cfd supervisor.

**THIS ARM GRADES NOTHING.** No gate, threshold, cap or label moves. Rung 1 stands
`NOT A RESULT`; rung 2 stands `BLOCKED` and its interlock was not touched; rungs 3-5
were asserted absent before and after. **No verdict from the fixed vocabulary is due
to this arm and none is issued.** Its output is a location and an iteration number.

---

## 1. THE ANSWER

**The field departs at ITERATION 1, anchored on the AEROFOIL, and the boundaries are
the LAST places to go — not the first.**

Of the four origins the freeze asked to discriminate — boundary/patch, geometric
feature, far field, interior — **the answer is the geometric feature, and it is
definite, not ambiguous.** At iteration 1, from a uniform `101,325 Pa` / `300 K`
start, **6,914 of 23,040 cells (30.01 %)** are already outside the case's own
registered pressure bounds, and **every one of them lies within `r = 0.836` chords of
the quarter chord.** Nothing beyond that radius has moved at all: **19,787 cells
(85.9 %) are still at exactly `300.000000 K`** — a zero read by a reader shown able,
on this run's own written field, to find a departure that is really there (§4).

The departure front then moves strictly **outward**, and reaches the boundaries last.

## 2. THE THREE REGISTERED CRITERIA

Constants quoted from the freeze §3; the reader holds none of its own
(`readers/departure_d123.py`, sha in `evidence/reader_sha256_at_use.txt`).

**D1 — `p` outside the case's own `pressureControl` bounds `[10132.5, 202650]` Pa**
(`pMinFactor 0.1`, `pMaxFactor 2` × `p_ref 101325`), read pre-clip from the solver's
own print because `p` on disk is censored. **First departure `N_p` = 1.**

| iteration | pre-clip `p` min (Pa) | pre-clip `p` max (Pa) | outside bounds |
|---|---|---|---|
| 1 | **−411,376.774** | **2,974,458.981** | yes |
| 2 | −167,638.117 | 658,689.606 | yes |
| 3 | −31,076.548 | 543,586.633 | yes |

At iteration 1 the pre-clip maximum is **29× freestream** and the minimum is a
**negative absolute pressure**, reached in a single iteration from a uniform start.

**D2 — `T ≤ 0` K or `T > 600` K** (floor is `thermoI.H`'s own range check).
**Not reached within the 15-iteration window** — as registered (P4). `T` minimum
falls 279.879 → 271.451 → 266.267 → **244.199 K** at iterations 1, 5, 10, 15.

**D3 — onset by region, `max|T − 300 K| > 0.5 K`.** The registered discriminator is
the **order**, and it is unambiguous:

| first departure | region | cells |
|---|---|---|
| **1** | **aerofoil wall** | 192 |
| **1** | **near field, `r < 1.5c`** | 13,497 |
| 2 | mid, `1.5–6c` | 3,409 |
| 2 | outer, `6–20c` | 2,842 |
| 6 | far, `≥ 20c` | 3,292 |
| 7 | outflow patch | 207 |
| **10** | **inflow patch** | 240 |

**Wall and near field first; both patches last.** A boundary-condition origin is
excluded by the data, and so is a simultaneous/global drift.

**Spatial locator (`evidence/iteration1_spatial_detail.txt`), iteration 1:** pinned
cells occupy `x ∈ [−0.104, 1.076]`, `y ∈ [−0.270, 0.388]`, `r_qc ∈ [0.056, 0.836]`.
The nearest pinned cell sits **0.00033 c from the leading edge** and **0.00448 c from
the trailing edge**; the `T` minimum at iteration 1, **279.879 K**, is at
`(0.995635, 0.001004)` — **the trailing edge**. Radial histogram of the 6,914 pinned
cells: 533 inside `0.1c`, 2,372 in `0.1–0.25c`, 2,140 in `0.25–0.5c`, 1,627 in
`0.5–0.75c`, 242 in `0.75–1.0c`, **0 beyond `1.0c`**.

**Clipped-cell census on disk** (`evidence/departure_D1_D2_D3.json`): 30.01 % of the
domain at iteration 1, all in wall+near; first mid/outer appearance at iteration 10;
**first inflow-patch appearance at iteration 13 (15 cells)**; at iteration 15,
**92.02 %** of the domain is pinned and the outflow patch registers its first 6 cells.

## 3. THE FOUR REGISTERED PREDICTIONS — ALL FOUR HOLD

- **P1 — FAITHFULNESS, the clause that gates everything else: PASS.** All **60**
  first-solve initial residuals over iterations 1-15, fields `Ux Uy e p`, are
  **identical to the registered rung-1 log**, with **0 mismatches**
  (`evidence/P1_first_solve_compare.txt`). The four values named in the freeze match
  exactly: `p` = `1` (it 1), `0.009554815904` (it 5), `0.2006112477` (it 10),
  `0.07671622987` (it 15). **Honest scope: this is equality of the solver's printed
  residuals, which is agreement to print precision — it is not a bit-level
  comparison of the field arrays, and is not reported as one.**
- **P2 — `N_p` = 1: PASS.**
- **P3 — wall and near field depart strictly before both patches: PASS** (1 and 1,
  versus 7 and 10).
- **P4 — D2 not reached by iteration 15: PASS.**

**No prediction failed, so nothing in the recovered prior arm is impeached by this
replication.** Its central observations are now reproduced under criteria fixed in
advance; its own standing is unchanged and remains `NOT A RESULT`
(`../field_observation_2026-08-25/PROVENANCE_AND_STATUS.md`).

## 4. THE CONTROLS

**Planted zero (standing rule 3), on a field written by THIS run — `15/T`, patch
`inflow`: 8/8, exit 0** (`evidence/PLANTED_CONTROL_selftest.txt`). Arms: baseline
read; baseline clean-field-has-no-plant; **POSITIVE** (`−7.654321e+09` returned);
**LOCALISATION** (reported at *exactly* cell 12345); cell-count preserved;
**PATCH** (`−1.357911e+09` reported on `inflow`); **PATCH SPECIFICITY** (no leak to
`outflow`); **NEGATIVE** (the unplanted original returns no plant value).

**The control REFUSED once, correctly, and it is recorded rather than hidden.** The
first attempt named patch `aerofoil`, which carries `type zeroGradient` for `T` and
so has no `value` list; the reader **exited 1 with `CONTROL REFUSED: patch aerofoil
has no nonuniform value list`** rather than reporting a passing patch arm it could
not actually perform. The target was moved to a patch that carries values. **Every
"undeparted" statement in §1 and §2 rests on this control.**

**Case identity: 18/18 files byte-identical** to the registered rung-1 case before
the run (`evidence/case_identity_18.txt`) — `fvSolution`, `fvSchemes`,
`blockMeshDict`, `decomposeParDict`, all seven `0/` fields, both `constant/`
property files, all five `polyMesh` files. **The entire delta is four output-control
lines** (`evidence/controlDict_THE_ENTIRE_DELTA.diff`): `endTime 6000→15`,
`writeInterval 6000→1`, `purgeWrite 1→0`, `+writeCompression off`. No solver,
smoother, preconditioner, tolerance, `relTol`, `residualControl` entry, corrector
count, `pMinFactor`, `pMaxFactor`, relaxation factor, scheme or boundary condition
was touched. **Ranks = 1**, which is what the registered rung 1 itself ran.

**Registered rung-1 directory fingerprint unchanged** before, after and finally:
`14abee9c4223c9cb180615e261cbcc5c6d5a2686768fae93e4b672c849051dbe` at all three
points. **Rungs 2-5 absent before and after.**

## 5. COMPLETION — ALL EIGHT CLAUSES HOLD, AND THE RUN DID *NOT* ABORT

As the freeze §7 predicted against the commissioning brief's expectation:
**`rc = 0`**; an **`End`** line; **last time 15 == `endTime`**; **`ExecutionTime`
count 15 == `endTime`**; time directories **1…15 all present**; fields present —
`T U p k omega nut alphat rho phi` (this case's list; the thermal-family list does
not apply); **age guard PASS**, 9/9 fields at `t = 15` newer than the case's own
`0/T`, which was touched last before launch so that the guard is a real test;
fingerprint unchanged. **Rung 1's abort is at iteration 148, far outside this
window, so no abort was expected here and none occurred.**

`trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)` is present at
line 18 of this run's log and **never fired** — consistent with the supervisor's
Ruling 1 that rung 1 was never an FPE.

## 6. WHAT THIS DOES AND DOES NOT SUPPORT

**Supported.** The departure is aerofoil-anchored and immediate. A **boundary-condition
origin is excluded** — both patches are among the last three regions to move, at
iterations 7 and 10, by which time the near field has been departed for six to nine
iterations. A **global/initial-state drift is excluded** — 85.9 % of the domain is
still exactly at its initial value when 30 % of it is already out of bounds.

**Not supported, and not claimed.** This arm does **not** identify a mechanism, does
not attribute the departure to any specific scheme, boundary condition or mesh
defect, and does **not** explain the `T ≤ 0` abort at iteration 148 — that lies
outside the registered window and, per the supervisor's Ruling 3, **needs its own
registration and does not ride in on this freeze.**

**An honest limitation of D3 to carry forward:** the two available metrics disagree
on the *relative* order of the two patches — D3 on `T` deviation gives outflow (7)
before inflow (10), while the on-disk clipped-`p` census gives inflow (13) before
outflow (15). **They agree on everything the registered question turns on** — that
both patches come last and the aerofoil comes first — but the boundary-vs-boundary
ordering is metric-dependent and should not be quoted as a finding.

## 7. COST — ESTIMATE VERSUS ACTUAL (standing rule 12)

| item | figure |
|---|---|
| Registered cap | **6.0 core-min**, 1 rank |
| Predicted (freeze §6) | **~0.11 core-min** |
| Solver, **measured** (`evidence/WALL_S.txt`) | 2.836569 s × 1 rank ÷ 60 = **0.047276 core-min** |
| `writeCellCentres`, **measured** | 0.183666 s = **0.003061 core-min** |
| Departure reader, **measured** (`evidence/WALL_S_readers.txt`) | 51.426153 s = **0.857103 core-min** |
| **Measured total, non-waste** | **0.907440 core-min — 15.1 % of cap. NOT breached.** |
| **Ratio actual/predicted** | **8.25×** |
| Dollars, **DERIVED not measured** | **$0.000776** at $0.0513/core-h (owner-stated) |

**Gap attribution — and the miss is not where the lab habitually looks.**
The **solver was predicted well**: rung 1's own `ExecutionTime` at `Time = 15` is
1.64 s and this run's is 2.74 s, the 1.10 s difference being exactly the 15
per-iteration field writes the probe exists to produce. **The miss is the READER.**
The freeze priced "field writes, reader selftests and the `writeCellCentres` pass"
at ≤ 0.08 core-min together; the departure reader alone cost **0.857 core-min**, a
**10.7× underprediction**, because D3's region membership recomputes a radial
distance per cell per region and then evaluates a deviation over 23,040 cells × 7
regions × 16 iterations in pure Python. **Calibration lesson for the lab's probe
estimates: a 15-iteration probe's analysis pass cost 18× its solve. Estimates on
this line price the solver and forget the reader.**

**WASTE, NAMED SEPARATELY AND NOT ABSORBED INTO THE RATIO: 0.857103 core-min** — the
departure reader was run twice with byte-identical output, the second pass solely to
obtain an honest timing for this row. It produced no new evidence.

**NOT SEPARATELY TIMED, and stated as absent rather than approximated:** the
planted-control selftest and the iteration-1 spatial-detail pass. Both read strictly
fewer fields than the timed departure pass, so each is bounded above by 0.857
core-min; the arm's worst-case total is therefore **≤ 3.48 core-min, still inside
the 6.0 cap.**

**CONTENTION, disclosed and not absorbed** (`evidence/CONTENTION.txt`): load average
**11.64** at start and **9.77** at end on 16 cores, with heat-transfer, dafoam and
ansys solvers live. `ExecutionTime` 2.74 s versus wall 2.836569 s = **0.966**, i.e.
**3.4 % wall overhead** — contention was measured and is small. **No clean-timing
core reservation was taken.**
