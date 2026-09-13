# M6J_L1 — GRADING RECORD. `transonic no`, ONERA M6, fine level.

**VERDICT: `GATE FAIL`.**

**Instrument:** `scripts/grade_m6_agard_cp.py`, blob `e9d5c04b420b99201ab19e694b76d1b9eda62443`.
**Hash-verified in the grading shell** against the working tree, against `HEAD`
(`541a04cb1`) and against the registered pin `4c931d97c` — **all three identical**, which is
what §6 of `M6J_TRANSONIC_FAMILY_PREREGISTRATION.md` requires and what proves the frozen file
IS the file that ran.
**Registration:** `verification/campaign/M6J_TRANSONIC_FAMILY_PREREGISTRATION.md`, frozen
`63f579222`, plus ADDENDUM 1 and ADDENDUM 2 (`69bee3f2`, the 16-rank re-rank).
**Machine record:** `m6j_grade_M6J_L1.json` beside this file.

---

## 1. COMPLETION — ALL CLAUSES, MEASURED

| clause | required | measured | |
|---|---|---|---|
| rc | 0 | `RC.txt` = **0** | ✓ |
| `End` line | present | present in `log.rhoSimpleFoam.resume.1` | ✓ |
| last time == `endTime` | 8000 | **8000** | ✓ |
| fields at `endTime` | `T U p alphat nut nuTilda rho phi` | all present in `8000/` | ✓ |
| step set | `{1..8000}` distinct | **8,000**, 0 missing, 0 unexpected | ✓ |
| age guard | every field newer than `0/T` | `0/T` 1789289682 < every `8000/*` (≥1789330697) | ✓ |

**THE STEP SET IS A UNION, AND THE RAW LINE COUNT IS WRONG BY 85.**
`scripts/solver_log_set.py` over `rhoSimpleFoam` returns `n_steps 8000` against
`n_exec_lines_raw 8085`, `line_count_overcounts_by 85` — iterations 3801–3886 were computed
at 4 ranks in segment 2 and recomputed at 16 in segment 3, and are **one physics step each**.
`clause_exec_count: true`, `clause_last_eq_endTime: true`.

🔴 **`log.rhoSimpleFoam` ENDS AT `Time = 3886` AND CARRIES NO `End` LINE.** It is 4,114
iterations stale with nothing on disk marking it so. The grader was handed
`log.rhoSimpleFoam.resume.1`. Had it been handed the obvious filename it would have
**REFUSED on P4** rather than graded a stale log — the instrument fails safe here, but the
hazard is real and is recorded in `GRADING_NOTE_RESUME_ARTIFACTS.md` §1.

`RC.txt = 1` on the first segment is the **deliberate stop** of ADDENDUM 2, not a crash:
`log.rhoSimpleFoam.stderr` is 0 bytes, no `FOAM FATAL`, no MPI message,
`DELIBERATE_STOP_2026-09-13.txt` filed beside `FAILURE_CONTEXT.1.txt`. No crash triage spent.

**Planted control (rule 3): `reader_saw_the_plant: true`** — plant 0.1234 into 47 points at
η 0.44 lower moved the row RMS from 0.032847 to 0.142755, i.e. by **0.109907** against a
required response of 0.0617. The zero-capable reader is shown able to see a non-zero.

**Preconditions:** `cfd_M_inf` 0.8395 vs AGARD TEST 2308 `M0` 0.8395, `mach_delta` **0.0**.

---

## 2. B1 — ROWS IN BAND: **7 of 12**

Band `B1 ≤ 0.050` RMS Cp per station per surface, shock zone excluded (§6, transcribed).

| row | RMS dev | in band | max abs dev | mean bias | n graded |
|---|---:|:---:|---:|---:|---:|
| η 0.20 lower | 0.03811 | **✓** | 0.09975 | +0.02569 | 11 |
| η 0.20 upper | 0.07080 | ✗ | 0.17365 | −0.03431 | 19 |
| η 0.44 lower | 0.03285 | **✓** | 0.08862 | +0.01650 | 11 |
| η 0.44 upper | 0.06319 | ✗ | 0.15364 | −0.01545 | 19 |
| η 0.65 lower | 0.01736 | **✓** | 0.04612 | −0.00030 | 11 |
| η 0.65 upper | 0.06863 | ✗ | 0.17659 | −0.01659 | 19 |
| η 0.80 lower | 0.01903 | **✓** | 0.04751 | −0.00250 | 11 |
| η 0.80 upper | 0.04179 | **✓** | 0.12920 | +0.00036 | 19 |
| η 0.90 lower | 0.02318 | **✓** | 0.06177 | +0.00474 | 14 |
| η 0.90 upper | 0.10460 | ✗ | 0.48214 | +0.01215 | 27 |
| η 0.96 lower | 0.02085 | **✓** | 0.05896 | +0.00304 | 14 |
| η 0.96 upper | 0.05752 | ✗ | 0.22323 | +0.00169 | 27 |

**The split is by SURFACE, not by station: all six lower surfaces pass, and five of six upper
surfaces fail.** The one upper-surface pass is η 0.80 at 0.04179. No orifice was dropped
outside the CFD span anywhere (`n_dropped_outside_cfd_span` = 0 on all twelve rows).

**THE RE-PARTITION CANNOT HAVE FLIPPED ANY OF THESE.** `CP_PARTITION_BOUND.txt` registered the
consequence before grading: a B1 row landing in **[0.0462, 0.050]** would be UNRESOLVED BY THIS
RUN, because the measured worst re-partition |ΔCp| is 3.831e-03. **No row lands in that
window.** The nearest is η 0.80 upper at 0.04179, clear of the window's lower edge by 0.0044,
and the nearest failing row is η 0.96 upper at 0.05752, clear above by 0.0075. **Every one of
the twelve B1 outcomes is resolved.**

---

## 3. B2 — SHOCK POSITION AT THE TWO GATE STATIONS

Band is **one local orifice interval measured from the reference file**, asserted against the
registered table to within 0.0125.

| station | x_shock exp | x_shock CFD | \|Δx\| | band Δ_local | registered table | in band |
|---|---:|---:|---:|---:|---:|:---:|
| η 0.65 | 0.47517 | **0.95312** | **0.47795** | 0.05014 | 0.0500 | **✗** |
| η 0.90 | 0.27976 | **0.23983** | **0.03994** | 0.04024 | 0.0400 | **✓** |

**η 0.65 misses by 9.5× the band.** The CFD argmax sits at x/c 0.953 — the trailing edge —
not at the experiment's shock. This is the §6 disclosure firing exactly as registered: the
comparator resamples onto experimental orifices whose intervals widen aft, so its argmax picks
the widest aft interval. **No reader may take this `x_shock` as a physical shock position.**

**η 0.90 clears by 3.05e-04 in x/c — 0.76 % of the band — and that margin is not what makes it
defensible.** What makes it defensible is a robustness check run against the instrument's own
resampled series:

| station | winner rise | at x/c | runner-up rise | at x/c | margin | margin % |
|---|---:|---:|---:|---:|---:|---:|
| η 0.65 | 0.108565 | 0.95312 | 0.106082 | 0.52533 | 2.483e-03 | **2.29 %** |
| η 0.90 | 0.169789 | 0.23983 | 0.164879 | 0.27976 | 4.909e-03 | **2.89 %** |
| η 0.65 *experiment* | 0.424000 | 0.47517 | 0.104000 | 0.95312 | 3.200e-01 | 75.47 % |
| η 0.90 *experiment* | 0.640000 | 0.27976 | 0.146000 | 0.31986 | 4.940e-01 | 77.19 % |

🔴 **THE DETECTOR IS PICKING BETWEEN NEAR-TIES AND THE EXPERIMENT IS NOT.** The experiment's
shock beats its runner-up by ~76 %; the CFD's winner beats its runner-up by ~2–3 %. And the
re-partition bound at η 0.90 is **3.831e-03 ΔCp against a 4.909e-03 winner margin — 78 % of
it.** A perturbation of the size already measured on this run could flip which interval wins.

**BOTH B2 OUTCOMES SURVIVE THAT FLIP, AND THAT IS WHY THEY STAND:**
- η 0.90, runner-up counterfactual: x/c 0.27976 → **Δx = 0.0**, still within band. Within band
  under **both** candidates.
- η 0.65, runner-up counterfactual: x/c 0.52533 → |Δx| 0.05016 vs band 0.05014, **fails by
  2e-05**. Outside band under **both** candidates.

**So the B2 verdict at each station is invariant to the winner/runner-up flip. The x-positions
are not resolved; the pass/fail outcomes are.** Stated as a limit, not as a reassurance: the
η 0.90 *position* 0.23983 is one near-tie away from 0.27976 and must not be quoted as located.

---

## 4. THE REST OF THE CURE GATE (§6), FOR COMPLETENESS

| limb | threshold | L1 measured | |
|---|---|---:|:---:|
| D1 `cfd_cp_rise` @ η 0.65 | ≥ 0.1401 | 0.10856 | ✗ |
| D2 CFD Cp rise across the experiment's own shock interval @ η 0.65 | ≥ 0.0880 | **0.09150** | **✓** |
| D3 `x_shock_cfd` must leave 0.8851 **forward** | forward | 0.9531 — moved **AFT** | ✗ |
| S1 @ η 0.65 | ≥ 0.212 | 0.10856 | ✗ |
| S1 @ η 0.90 | ≥ 0.320 | 0.16979 | ✗ |
| S2 @ η 0.65 | < 0.85 | 0.9531 | ✗ |
| S2 @ η 0.90 | < 0.85 | **0.2398** | **✓** |
| B1 ≤ 0.050 on 12 rows | 12 of 12 | 7 of 12 | ✗ |
| B2 ≤ Δ_local | both | 1 of 2 | ✗ |

**D2 clears at 0.0915, the first D2 clear in this act's history** (M6I R10's L3 measured
0.0170 — 5.4× below). Computed here from the frozen module's own `d1_shock_from_curve` and
`interp_onto` on the experiment's selected interval [0.45010, 0.50024]; it is a diagnostic read
through the frozen code, not a regrade.

**L1 clears 1 of the 4 shock-bearing conditions (S2 @ η 0.90).** Under
`M6I_R1_SOLVE_PREREGISTRATION.md` ADDENDUM 3 — *"a level is shock-bearing only if S1 AND S2
hold at BOTH η = 0.65 and η = 0.90"* — **L1 is NOT shock-bearing.**

---

## 5. THE FAMILY BAND ACROSS L3 / L2 / L1

| row | L3 | L2 | L1 | in band |
|---|---:|---:|---:|:---:|
| η 0.20 lower | 0.15117 | 0.06773 | 0.03811 | ..L1 |
| η 0.20 upper | 0.22885 | 0.09139 | 0.07080 | — |
| η 0.44 lower | 0.15266 | 0.06414 | 0.03285 | ..L1 |
| η 0.44 upper | 0.28523 | 0.11021 | 0.06319 | — |
| η 0.65 lower | 0.14517 | 0.05221 | 0.01736 | ..L1 |
| η 0.65 upper | 0.31979 | 0.12977 | 0.06863 | — |
| η 0.80 lower | 0.14819 | 0.05217 | 0.01903 | ..L1 |
| η 0.80 upper | 0.34983 | 0.13194 | 0.04179 | ..L1 |
| η 0.90 lower | 0.15215 | 0.05612 | 0.02318 | ..L1 |
| η 0.90 upper | 0.37147 | 0.16712 | 0.10460 | — |
| η 0.96 lower | 0.16275 | 0.06030 | 0.02085 | ..L1 |
| η 0.96 upper | 0.35834 | 0.15414 | 0.05752 | — |

| level | rows in band | RMS range | mean RMS | verdict |
|---|---:|---|---:|---|
| M6J_L3 | **0 / 12** | [0.14517, 0.37147] | 0.23547 | `GATE FAIL` |
| M6J_L2 | **0 / 12** | [0.05217, 0.16712] | 0.09477 | `GATE FAIL` |
| M6J_L1 | **7 / 12** | [0.01736, 0.10460] | 0.04649 | `GATE FAIL` |

**THE FAMILY BAND IS 0.01736 TO 0.37147 — a factor of 21.4 — AND ALL TWELVE ROWS FALL
MONOTONICALLY L3 → L2 → L1.** Twelve of twelve, no exception.

🔴 **NO ORDER AND NO GCI IS COMPUTED, QUOTED OR IMPLIED HERE, AND THE MONOTONICITY IS NOT AN
INVITATION TO COMPUTE ONE.** ADDENDUM 3 clause 2 governs: not one of the three levels clears
all four shock-bearing conditions (L3 0/4, L2 1/4, L1 1/4 — twelve conditions across the
family, two satisfied), so the comparison carries its registered label:

> **"TWO LEVELS, NO ASYMPTOTIC RANGE DEMONSTRATED"**

The registered label is quoted verbatim as frozen, including its "TWO LEVELS" wording, on a
family of three. ADDENDUM 3 is not being reinterpreted. **A monotone triple on a quantity
whose gate says the feature it measures is absent is not an asymptotic range**; §1 of this
registration said so before the runs, which is the whole point of having said it then.

---

## 6. THE ONE-CHANGE FINDING

**`transonic no` does NOT reproduce the shockless smeared recompression at L1 the way it does
at L2 and L3 — and it does not produce a shock either.** Three things moved and they do not
point the same way:

1. **B1 went from 0 of 12 to 7 of 12.** L1's mean row RMS is 0.04649 against L2's 0.09477 and
   L3's 0.23547. Every lower surface is now inside a band no lower surface cleared at L2.
2. **S1 @ η 0.90 more than doubled**, 0.0827 (`transonic yes`, L1) → **0.16979**. **D2 cleared
   for the first time in the act.** The aft recompression is real and is strengthening.
3. **And it is still not a shock.** S1 misses its thresholds by 2.0× at η 0.65 and 1.9× at
   η 0.90; the detector's winner beats its runner-up by 2–3 % against the experiment's 76 %;
   η 0.65's argmax is at the trailing edge. **The recompression is sharper than the family has
   ever measured and still smeared.**

That is the one-change result, reported as a finding and not as a disappointment, exactly as
§5 branch (b) registered it would be.

---

## 7. THE RE-PARTITION BOUND ON THE GRADED QUANTITY

Control: `verification/runs/M6J_runs/M6J_L1_CP_CONTROL_4RANK`, rc **0**, the preserved 4-rank
state advanced 3800 → 4200 at `n (2 2 1)` against this run's 3800 → 4200 at `n (2 2 4)`.
Same physics, schemes, solvers, relaxation and model; **only the partition differs.**
Compared point-for-point by `verification/runs/M6J_runs/compare_cp_partition.py`, re-run in
the grading shell, **96 points per station on both sides, no station resampled, no refusal.**

| η | max \|ΔCp\| | rms ΔCp | max\|ΔCp\|/range | |
|---|---:|---:|---:|---|
| 0.20 | 2.687e-04 | 6.983e-05 | 1.421e-04 | |
| 0.44 | 3.677e-04 | 1.000e-04 | 1.820e-04 | |
| 0.65 | 1.935e-04 | 6.040e-05 | 9.557e-05 | **GATE** |
| 0.80 | 8.656e-04 | 1.620e-04 | 4.316e-04 | |
| 0.90 | **3.831e-03** | 6.900e-04 | 1.674e-03 | **GATE** |
| 0.96 | 2.252e-03 | 5.171e-04 | 1.031e-03 | |

- **worst \|ΔCp\| overall: 3.831e-03** (at η 0.90)
- **worst \|ΔCp\| at the gate stations η 0.65 and 0.90: 3.831e-03** — the overall worst IS at a
  gate station, so the gate stations are not the quiet ones.

**This is 76× larger than the force-integral bound would suggest** (Cd max \|rel diff\|
1.62e-04) — which is the reason the control was run: cancellation hid the local difference
inside the integral, exactly as ADDENDUM 2 §A2.3 said it could. **The integral bound was not
wrong; it was not a bound on this.**

**NOT round-off** — round-off amplified by 400 iterations of an unconverged iterative solve.
The integral perturbation **saturates** at ~2e-06 absolute Cd by ~200 iterations and does not
grow (measured free from the per-iteration force series). **Whether the LOCAL Cp perturbation
saturates is NOT MEASURED**: it was taken at one time, t=4200, because a second point needs a
second control run and the graded run's `t=4000` was destroyed by `purgeWrite 2` before it
could be rescued. **The trend gives no evidence of divergence and that is the strongest
statement the evidence supports. It is not a proof that Cp at t=8000 is perturbed by no more
than 3.831e-03.**

**What the bound does establish, and it is enough for this verdict:** all twelve B1 outcomes
and both B2 outcomes are resolved against it (§2, §3).

**The designed conflict fired as designed:** `fo_series` flagged **85 rows** as disagreeing
between `postProcessing/forceCoeffs/200/` and `/3800/`. Those are iterations 3801–3885 computed
under two partitions. **Recorded, not silenced** — that reporting path is the reader being
shown the disagreement, per `GRADING_NOTE_RESUME_ARTIFACTS.md` §4.

---

## 8. RENDERS (Sanaa's standing ParaView rule)

| what | path |
|---|---|
| **coarse mesh** (M6J_L3 surface, t=3000, 480 faces) | `verification/runs/M6J_runs/RENDERS/M6J_L3_mesh_surface_surface.png` |
| **L1 fields** (`p`, CELLS, t=**8000**, 7,680 faces) | `verification/runs/M6J_runs/RENDERS/M6J_L1_field_p_surface_surface.png` |

Sidecars `*_surface.json` beside each. Both carry **`guard PASS`** on the per-patch face-count
identity (`wing` 480 == 480; `wing` 7,680 == 7,680) and **`graded_tree_untouched: true`** by
census hash before and after. The L1 field render's **planted colour control PASSED**, read
back off the saved PNG: collapsing the transfer function moved **90.53 %** of body pixels
against a 10 % floor — so the picture is coloured by the field and is not a flat-shaded body.
Field range 37,677.5 – 147,233.2 **Pa**, units taken from the field file's own `dimensions`
header. `p` at t=8000 is the graded time.

🔴 **DISCLOSED: both renders exited `rc=1`.** The failure is `X Error … GLXBadContext` on
`X_GLXMakeCurrent`, and it is printed **after** each renderer's own
`WROTE … guard PASS, graded tree untouched` line — an xvfb GLX context teardown after the PNG
and sidecar were written and after both guards reported. The artifacts and their guards are
therefore intact and the images were inspected. **The non-zero rc is reported, not absorbed.**

---

## 9. COST — ESTIMATE VERSUS ACTUAL (rule 12)

**Per segment, each at the rank count it actually ran** (`RANKS_BY_SEGMENT.tsv` is the
authority; `RANKS.txt` holds only the last segment's 16 and pairing it with every
`CORE_MINUTES.txt` row would cost segments 1–2 at 16 ranks and inflate 2,012.40 to 8,049.6 —
a factor of 4):

| segment | ranks | iterations | wall s | core-min | basis |
|---|---:|---|---:|---:|---|
| 1 — first-order ramp | 4 | 1–200 | 3,377 | 225.13 | MEASURED |
| 2 — registered schemes | 4 | 201–3,886 | 26,809 | 1,787.27 | MEASURED |
| 3 — resume | **16** | 3,801–8,000 | 10,234 | **2,729.07** | MEASURED |
| **L1 total** | | **1–8,000** | | **4,741.47** | **MEASURED** |

Each row recomputed as `wall × ranks ÷ 60` in the grading shell and matched to <0.02 core-min.

**RATIO, THE HEADLINE:** §7 predicted **998.8** core-min. Actual **4,741.47**.
**actual/predicted = 4.747×.**

**ATTRIBUTION — the terms are named separately and none is absorbed into the ratio:**

1. **MISPREDICTION, and it is the dominant term.** §7's law was 1.27e-07 core-min per
   cell-iteration; the run measured **4.93e-07** at 4 ranks — **the registered law was 3.88×
   low**. ADDENDUM 1 §A1.3 had already caught this at 4.909e-07 from a different segment, and
   the two agree to 0.4 %. Scope did not move: 983,040 cells × 8,000 iterations, exactly as
   registered. **The gap is the rate, not the work.**
2. **RE-RANK, its own line.** The 4-rank counterfactual for segment 3 is 4,200 × 0.4849 =
   **2,036.6** core-min; actual **2,729.07**. **Excess 692.5 core-min**, i.e. **74.8 % parallel
   efficiency** at 61,440 cells/rank. ADDENDUM 2 §A2.4 projected 2,040–2,910 spanning 100 %
   down to 70 % efficiency — **the actual lands inside that band**, at 94 % of its upper edge.
   The re-rank bought wall time and spent core-minutes, as registered; it is not netted against
   idle capacity.
3. **WASTE, named and not absorbed.** 86 iterations (3801–3886) were computed twice: once at
   4 ranks in segment 2 and discarded at the stop, once at 16 in segment 3. Discarded work
   **41.7 core-min** at the measured 4-rank rate. **0.88 % of the total.**
4. **CONTENTION, registered not measured on this run.** The registered figure is n=7, mean
   **+5.1 %**, worst **+6.4 %**, every one of the seven SUBOFF points slower. Applied to the
   2,012.40 core-min of 4-rank work that is ≈ **102.6 core-min**. **This is the registered
   figure applied, NOT a contention measurement taken on this run** — stated as such.

**Against ADDENDUM 2's projection of ≈4,050–4,920: the actual 4,741.47 is INSIDE the band.**
The registration's own updated projection was good; §7's original was 4.7× low.

**§7's cap of 2,996 core-min is CROSSED, by 1,745.47.** Per ADDENDUM 1 §A1.2 and ADDENDUM 2
§A2.4 that clause is **superseded** — Sanaa's directive #17 (2026-09-12, no run stopped by
time or budget cap) and *"bookkeeping never voids physics"*. **The crossing is recorded in the
cost row and is NOT a verdict input.** The `GATE FAIL` above is a physics verdict from the
frozen instrument and does not descend from the cap.

**Diagnostic control run**, its own line, not folded into L1: `M6J_L1_CP_CONTROL_4RANK`
**241.87** core-min MEASURED.

**Dollars DERIVED, NOT MEASURED** at the owner-stated **$0.0513/core-h** — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5): L1 ≈ **$4.05**, control ≈ **$0.21**.

---

## 10. WHAT THIS RECORD DOES NOT ESTABLISH

1. **That Cp at t=8000 is perturbed by the re-partition by no more than 3.831e-03.** The bound
   is at t=4200. The local perturbation's saturation is NOT MEASURED (§7).
2. **A grid-convergence order or GCI.** Forbidden by ADDENDUM 3 clause 2 and not computed (§5).
3. **A physical shock position from `x_shock`.** §6's D2/D3 mislocation disclosure travels with
   both B2 numbers, and the near-tie margins of §3 sharpen it.
4. **A contention measurement on this run.** §9 term 4 applies the registered figure.
5. **L1 at 16 ranks against L2 and L3 at 4** is a declared inhomogeneity in the family
   (ADDENDUM 2 §A2.2). §3's byte-identical-decomposition argument is weakened for L1 and the
   §7 bound is what quantifies the second difference.
