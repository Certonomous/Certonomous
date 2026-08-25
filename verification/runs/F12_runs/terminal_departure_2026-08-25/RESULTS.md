# F12 — THE TERMINAL-DEPARTURE PROBE

**cfd lane, 2026-08-25.** Pre-registration
`verification/campaign/F12_TERMINAL_DEPARTURE_PREREGISTRATION.md`, blob
`118fe0d1e409ce5fd64d284fa2172a8c6e5c7788`, sha256
`d155396b5a8bec4059859bc9c3be908a9157411c61ebeba12ae9810968f9292e`, **committed before this
compute** and re-verified against HEAD by the run script in its own invocation
(`evidence/freeze_verified.txt`).

**THIS ARM GRADES NOTHING.** No gate, threshold, band, cap or label moves. F12 rung 1 stands
`NOT A RESULT`; rung 2 stands `BLOCKED` and its interlock was **not read around, not edited
and not invoked**; rungs 3–5 were asserted absent before and after. **No verdict from the
fixed vocabulary is due to this arm and none is issued.**

---

## 1. THE ANSWER, AND IT CONTRADICTS THE DIRECTION THE EVIDENCE WAS POINTING

**The terminal failure is NOT aerofoil-anchored. It is a cold front convected down the WAKE.**

The frozen 15-iteration field-localisation replication established — correctly, for its own
window — that the field departs at iteration 1 anchored on the aerofoil, with the boundaries
last. **That reading does not extend to the crash, and this arm is how we know.**

| window | where the `T` minimum sits |
| --- | --- |
| iterations 1–99 | downstream of the trailing edge in **5 of 99** iterations |
| iterations 120–147 | downstream of the trailing edge in **28 of 28** iterations |

Over iterations 120→147 the `T` minimum marches from `x/c = 1.0280` to `x/c = 2.0819` — from
the trailing edge to **one chord into the wake** — at **0.039 chord per iteration**, with
**one** non-monotone step in 27. Over the same 27 steps `T_min` falls from **141.643 K to
−8.156 K** at **−5.55 K per iteration** with **zero** non-monotone steps, while `T_max` rises
monotonically to **608.505 K**.

**Q1 — when.** The on-disk `T` minimum first falls below **250 K at iteration 14**, **200 K at
102**, **100 K at 130**, and **0 K at 147**. There is a long slow slide and then an
accelerating collapse; the collapse phase is the wake march.

**Q2 — where.** The minimum's own track (`evidence/terminal_departure.json`,
`Q2_T_min_track`, one row per iteration): at iteration 1 it is at the **trailing edge**,
`(0.995630, 0.001004)`; at 100 it is on the **upper surface at `x/c = 0.722`**; at 120 it is
**at the trailing edge**, `(1.028, 0.211)`; at 130 it is at `(1.331, 0.214)`; at 147 it is at
**`(2.081893, 0.269369)`, `r = 1.9179 c` from the quarter chord**, carrying **−8.156073 K**.
The cell index steps by a near-constant increment each iteration — one cell per iteration in
the wake block's index space — which is the signature of a **convected** disturbance, not a
stationary one.

**Q4 — the same death.** Yes, exactly: `rc = 134`, abort at **iteration 148**,
`Negative initial temperature T0: -2.384321367` — bit-identical to the registered rung 1.

## 2. THE FOUR REGISTERED PREDICTIONS

- **P1 — FAITHFULNESS, the clause that gates everything else: PASS.** **885** first-solve
  initial residuals over **148** iterations, fields `Ux Uy e p k omega`, **0 mismatches**
  against the registered rung-1 log. The five values named in the freeze match exactly:
  first-solve `p` = `1` (it 1), `0.009554815904` (it 5), `0.2006112477` (it 10),
  `0.07671622987` (it 15), `0.2117489171` (it 147). *Honest scope: this is equality of the
  solver's printed residuals — agreement to print precision — not a bit-level comparison of
  the field arrays, and it is not reported as one.*
- **P2 — the same death: PASS.** `rc = 134` read back from `RC.txt`; abort at iteration 148;
  `T0 = -2.384321367`. **The registered rung 1 is reproducible on this box.**
- **P3 — the failure stays aerofoil-anchored (`r < 1.5 c`): FAIL.** Measured `r = 1.91791 c`.
  **This is the finding.** The prediction was written from the 15-iteration arm's reading and
  the data refused it. The record says so in those words.
- **P4 — the limiter saturates: NOT EVALUABLE AS REGISTERED, and the defect is this lane's
  own.** See §3.

## 3. A MIS-SPECIFIED MEASUREMENT QUANTITY IN THIS LANE'S OWN FREEZE — DISCLOSED, NOT REPLACED

Q3 of the freeze names *"the on-disk count of cells **outside** the case's own registered
bounds `[10132.5, 202650]` Pa"*. P4 names *"the on-disk pressure-**limited** cell fraction"*.
**Those are not the same quantity, and the first is degenerate.**
`pressureControl::limit()` censors `p` on the way to disk, so a limited cell reads **exactly
at** the bound and **never outside** it. Measured: cells outside the bounds, **maximum over
the whole 147-iteration run = 0**, total = **0**. **The registered Q3 quantity could not have
been non-zero, whatever the run did.**

The proxy actually read — cells sitting **at** a bound — gives **71.34 %** at iteration 147
against a registered threshold of 90 %, with the fraction swinging between **0.95 %** and
**92.71 %** over the last 50 iterations. **But that proxy is not the registered quantity and
it is not clean**: it disagrees with the solver's own `pressureControl:` print on **44 of 147
iterations**, because a cell can sit at a bound merely because it was clipped in an *earlier*
iteration and has not moved.

**P4 is therefore reported as NOT EVALUABLE AS REGISTERED. The proxy reading is reported with
its disagreement count and is NOT presented as a refutation of anything.** This is the same
defect class the `ansys-verification` team recorded on VMFL059 — a gate quantity that could
never have passed — and it is named here against this lane rather than left for a reader to
find.

## 4. THE CONTROLS

**Planted zero (standing rule 3), on a field written by THIS run** — `147/T`,
`evidence/terminal_departure.json` → `planted_zero`. Arms, all passing: baseline read;
**negative** (the unplanted original does not contain the plant value); **positive** (the
planted `−7.654321e+09` is returned); **localisation** (reported at *exactly* cell 12345,
where it was placed); cell-count preserved (23,040 before and after); minimum relocates to the
plant. **Every "did not depart" and every count in §1–§3 rests on this control**, and the
reader `refuse()`s with exit 1 rather than reporting a census it cannot justify.

**Case identity: 18/18 files byte-identical** to the registered rung-1 case before the run
(`evidence/case_identity_18.txt`) — `fvSolution`, `fvSchemes`, `blockMeshDict`,
`decomposeParDict`, all seven `0/` fields, both `constant/` property files, all five
`polyMesh` files. **The entire delta is four `controlDict` output-control lines**
(`evidence/controlDict_THE_ENTIRE_DELTA.diff`): `endTime 6000→148`, `writeInterval 6000→1`,
`purgeWrite 1→0`, `+writeCompression off`. No solver, smoother, preconditioner, tolerance,
`relTol`, `residualControl` entry, corrector count, `pMinFactor`, `pMaxFactor`, relaxation
factor, scheme, boundary condition or initial value was touched. **Ranks = 1**, as the
registered rung 1 itself ran.

**Registered rung-1 directory fingerprint unchanged** before and after
(`evidence/rung1_fingerprint_before.txt` == `evidence/rung1_fingerprint_after.txt`).
**Rungs 2–5 asserted absent before and after.** `rc` was captured to `RC.txt`, `sync`'d, and
**read back from the file**; a missing, empty or non-integer `RC.txt` would have been
**REFUSED, never inferred**.

## 5. COMPLETION — THE RUN DID NOT COMPLETE, AND THAT WAS THE POINT

This arm was registered to run **into** an abort, so standing rule 4's completion rule is
reported rather than claimed: `rc = 134` (not 0); **no `End` line**; last written time **147**,
not `endTime = 148`; the run aborted inside iteration 148. **A run that fails a limb of rule 4
is not a completed run, and nothing here is graded as one.** 148 time directories were written
(`0` and `1`…`147`), each carrying `T U p k omega nut alphat rho phi`.

## 6. WHAT THIS SUPPORTS AND WHAT IT DOES NOT

**Supported.** The terminal collapse is **spatially distinct from the initial departure**. The
initial departure is aerofoil-anchored (frozen 15-iteration arm). The collapse is a cold front
that locks onto the wake at about iteration 120 and convects downstream at ~0.039 c per
iteration while its minimum falls ~5.5 K per iteration. **"Where does the field first go
wrong" and "where does it die" have different answers, and the 15-iteration window could not
have shown the second.**

**NOT supported, and NOT claimed.** This arm identifies **no mechanism**. It does not
attribute the wake front to any scheme, boundary condition or mesh property. It does not
establish that the wake is *causal* rather than merely where the coldest cell ends up. **The
mechanism is open, and naming one here would be the fifth corrected mechanism claim on this
line.** A candidate worth testing, and offered as a candidate only: the energy convection
scheme in the wake — `div(phi,e)` is `bounded Gauss linearUpwind limited`
(`system/fvSchemes`), which is second-order and not TVD-bounded, on a wake mesh that coarsens
downstream. **That is a hypothesis for the supervisor's triage, not a finding of this arm.**

**Crash triage is the supervisor's personal check (`SUPERVISION_CHARTER.md` §3 check 2) and
this record does not rule.** It reports evidence and one recommended reading.

## 7. COST — ESTIMATE VERSUS ACTUAL (standing rule 12)

| item | figure |
| --- | --- |
| Registered cap (runaway guard) | **30 core-min**, 1 rank |
| Predicted (freeze §5) | **6.4 core-min** |
| Solver, **measured** (`evidence/WALL_S.txt`) | 25.333804 s × 1 rank ÷ 60 = **0.422230 core-min** |
| Reader, **measured** (`evidence/WALL_S_reader.txt`) | 1.08 s = **0.018000 core-min** |
| **Measured total** | **0.440230 core-min — 1.47 % of cap. NOT breached.** |
| **Ratio actual/predicted** | **0.0688× — a 14.5× OVER-prediction** |
| Dollars, **DERIVED not measured** | **$0.000376** at $0.0513/core-h (owner-stated) |

**Gap attribution, and the miss is entirely mine.** The solver was priced well: predicted
13.3 s from rung 1's measured 3.8975e-6 s per cell-iteration, actual 25.3 s — a 1.9× miss
explained by the 147 per-iteration field writes the probe exists to produce. **The whole
over-prediction is the reader line**: 6.0 core-min predicted, **0.018 measured, a 333×
over-price.** I priced the *previous* arm's reader — which recomputes a radial distance per
cell per region per iteration in pure Python and cost 0.857 core-min for 16 iterations — and
then wrote a different reader that walks each field once. **Calibration lesson: a reader's
cost is a property of the reader you write, not of the last one someone wrote. Pricing from a
predecessor's implementation is not pricing from a measurement.**

**WASTE: ZERO.** The reader was run twice, but the second pass was not a duplicate — it added
the §3 mis-specification disclosure to the evidence JSON, which the first pass did not carry.
No pass produced byte-identical output to a previous one.

**NOT SEPARATELY TIMED, and stated as absent rather than approximated:** the
`postProcess -func writeCellCentres` pass. It reads one mesh and writes four fields, strictly
less work than the solver, so it is bounded above by 0.422 core-min; the arm's worst-case
total is therefore **≤ 0.863 core-min, still 2.9 % of cap.**
