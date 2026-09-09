# D6RF10 — AMENDMENT A3 (R2 endTime 2000→300) PRE-FREEZE RULING — **SOUND**

**Author:** verification-supervisor. **Date:** 2026-09-09. **Routed by chief**
(gates dafoam's D6RF10 freeze). **Authority:** verdict-preservation / T25 / rule 2
(pre-first-compute) / rule 6 (foot amendment) / rule 5 / §2bb; companion to my
standing ruling **`b88c8926`** (`D6RF10_B300_RULING_2026-09-09.md`). **Scope
self-test:** APPLICATION of standing law, no new precedent, anti-gaming-safe
direction → **NO Sanaa escalation**; chief relays to dafoam. **Cost: 0 solver
core-min, $0.00** (read + reasoning).

Target: AMENDMENT A3 (`1605f211`, PERMISSION = NOT_FROZEN).

---

## 1 — R2 registered endTime = **300 CONFIRMED**. A3 is **verdict-preserving — SOUND.**

**Diff scope (my §3 check-1, read as a diff):** `d6rf10_grade.py` changes
**exactly one line** — `RUNG_CONFIG["R2"]["endTime"] 2000 → 300` (line 128).
R2's `solverName` (DARhoSimpleFoam), `nNonOrth` (12), `relax_p` (0.30),
`relax_eqn` (0.70) and `role` are unchanged; **R1 / R3 / R4 / CONTROL and the
`1.0e-05` accept floor (md5 `c6e63098`) are untouched.** Moves **no gate, no
floor, no cap, no field, no label** — only R2's outer-iteration horizon, and
**downward**.

**Rule-2 legality:** pre-first-compute, condition stated AND how checked — the
graded run root `CURRICULUM-D6RF10-a2-wing-convergence-probe/` is confirmed
**absent** (only the separate `D6RF10-PREFLIGHT-EXERCISE` measurement root
exists; never a graded row); gates OPEN; pins still `PLACEHOLDER_AT_FREEZE`.
Legal. **Rule-6:** appended at foot, "lines whose number changed above: 0". OK.

**Why 300 is the correct horizon (300 vs 2000 is a clean-complete vs
knowing-timeout choice):**
- **At 2000:** R2's per-step wall cost is MEASURED to RISE (4.330 → 5.059 s/step
  over [100,200] → [200,300]); extrapolated, endTime 2000 exhausts a flat-rate
  deadline at **~iter 1447** — a predictable **TIMEOUT → incomplete run** (rule 4:
  last time ≠ endTime). Its `GATE FAIL` would then be an incomplete-run
  **confound** — the exact class D6RF10 exists to REMOVE (cf. the D6RF9-R2 rc=124
  timeout-incomplete, V-134). Keeping 2000 re-introduces the confound.
- **At 300:** R2 ran **COMPLETE, rc=0, stopped=no, cumulative exec ~1052.48 s** in
  the exercise → a clean complete run that measures the floor.

**Verdict preservation (T25 / rule 5):** R2 is a **GATE-FAIL** rung
(p_first_uncorrected@300 = 1.68e-5 > the unchanged 1.0e-5 floor). The binding
field is **monotone-DECREASING** over the outer loop, so a SHORTER horizon
reports a **HIGHER** value → conservative → the shortened R2 can **only stay
GATE FAIL, never manufacture a PASS**. The one residual risk of an early stop —
a *missed PASS* from a plateau LATER than 300 — is **already discharged by
`b88c8926`**: R1 (same DARhoSimpleFoam/SIMPLE solver, the extended-horizon
control) drifts only 4.985e-8 (0.307 %) over 300→2500 = plateaued by 300; R2
tracks R1 to 3–4 sig figs and its deeper corrector loop converges earlier-or-
equal; so R2's 1.68e-5 IS the converged value and will not dip below the floor by
2000. **The transfer is legitimate for R2 precisely because R2 shares R1's solver
(SIMPLE) and timescale** — which is why R3/R4 (SIMPLEC, unmeasured timescale)
were NOT shortened and R3 correctly stays at endTime 2000 (A2, unchanged).

A3 resolves the A2-wording ("R2 endTime per registration" = 2000) vs `b88c8926`
(R2 SOUND at 300) tension in the **only** direction consistent with both the
standing ruling and the measured evidence. **SOUND. Freeze R2 at endTime 300.**

---

## 2 — Instrument flag: the constant-per-step model vs R3's RISING cost — **the disclosed effective-average is ACCEPTABLE here; durable fix specified.**

**The limitation (real):** `scripts/check_ladder_preflight.py` models per-step
wall cost as **CONSTANT** and its fabrication-guard checks only
`projected_wall_s == measured_per_step_wall_s × steps_to_endTime`. For a
**rising-cost** rung this guard is satisfiable by **back-solving** per_step from
any projection, so it no longer independently validates the projection — it
validates internal arithmetic only. R3's projection defensibility then rests on
the manifest **prose note**, which the checker does not parse.

**dafoam's approach for R3:** raw per-step RISES (measured 3.789 → 4.148 s/step);
a linear-rise fit (Basis B) projects cumulative ~13490 s to endTime 2000;
`measured_per_step_wall_s` carries the **effective cumulative average**
13490/2000 = **6.745 s/step** so `projected == per_step × steps` holds; deadline
16900 s ≥ 1.25 × 13490 = 16862.5. Basis A (flat 4.148×2000 = 8296) under-sizes;
Basis C (startup-contaminated) over-sizes.

**RULING — ACCEPTABLE for this freeze**, because verdict integrity is not at
risk in either error direction:
1. It is **fully disclosed** — Basis A/B/C, the raw windows (3.789/4.148), and the
   effective-average derivation are all in the manifest note; an auditor can
   reconstruct the projection.
2. It errs toward **OVER-sizing** the deadline (Basis B 13490 > flat 8296) — the
   **safe** direction. A too-generous deadline cannot manufacture a false verdict;
   it can only permit a longer run.
3. R3 is the **binding must-complete** rung, so the failure the checker guards (an
   UNDER-sized deadline → timeout) would surface as a **rule-4 incomplete → NOT A
   RESULT**, never a silent false PASS.

**Condition (met):** the raw measured windows AND the effective-average must both
remain in the manifest note (they do), and the pre-flight reviewer confirms the
sizing errs toward over-, not under-, provisioning (it does: 13490 > 8296).

**Durable fix (a follow-on to MY instrument, NOT blocking this freeze):**
`check_ladder_preflight.py` gains an optional non-constant-cost basis — accept a
`per_step_windows` array (raw windows + step ranges) plus a named `sizing_basis`,
recompute the projection from the windows, and assert the declared
`projected_wall_s` matches **that recomputation** within tolerance (not merely
`per_step × steps`). That restores an independent projection check for
rising-cost rungs and closes the back-solve gap. Until it lands, a back-solved
effective-average is admissible ONLY with the raw windows disclosed and ONLY in
the over-sizing direction, confirmed by hand at pre-flight.

---

## 3 — What still gates the freeze (unchanged)
dafoam's own non-delegable check-1 (the one-line R2 diff + reverse-substitution
empty + floor md5 `c6e63098` unmoved — I confirmed the diff scope above); a green
`check_ladder_preflight.py` on the rebuilt manifest; the §2ba dual-mechanism run
discipline; nothing frozen/launched/enqueued until then. R3 stays at endTime 2000
(A2), unchanged by this ruling.

*— verification-supervisor, 2026-09-09. Companion to `b88c8926`.*
