# M6I RUNG 7 — THE PRESSURE FLOOR. PRE-REGISTRATION. **AND THE LAST RUN ON THIS LINE.**

**Item:** `M6I_R7_PMINFACTOR`
**Team:** cfd. **Lane:** `lab-lane`. **Supervisor:** `cfd-supervisor`.
**Predecessors:** R5 `27a491e77` (+ addendum 1 `1ba860253`) → `L2_PHIDP` **NOT A RESULT**;
R6 `49c4d39a4` → `L2_VANLEER` **NOT A RESULT**, and **R6 §7 DID NOT FIRE** (0.0 % of wing
cells at the ceiling against a ≥ 50 % threshold), so the pressure-term rung was **not**
spent and returned to the supervisor undecided.

## 🔴 STATUS: **DRAFT. NOT FROZEN. NO SOLVER MAY RUN UNDER THIS DOCUMENT.**

Pre-compute condition, checked by this lane: **`verification/runs/M6I_runs/L2_PMIN/` does
not exist.**

## 🔴 §0 — THE HARD LIMIT, WRITTEN FIRST SO IT CANNOT BE MISSED

**R7 IS THE LAST RUN ON THIS LINE, WHATEVER ITS SIGNATURE.** After R7 the next step is
either the **tip-cap mesh question** or the **model rung (SA versus SST)**, and **it is the
supervisor's to authorise — not this lane's, and not by default.** No R8 on the pressure
system is registered or run by anyone. *Rationale, recorded by the supervisor against
himself: CRM spent roughly twenty attempts on one rung tonight because each individual next
change looked reasonable. This limit exists to stop that pattern here.*

---

## 1. WHY THE FLOOR, AND NOT A THIRD SCHEME — THE TWO LIMITERS ARE NOT SYMMETRIC

R6 §3 argued the `pMaxFactor` ceiling could not be censoring physics. **That argument was
correct and it does not transfer to the floor.** Recomputed independently by this lane from
the case's own `gamma = 1.399726300`, `M_inf = 0.8395`, `q_inf = 49,977.11 Pa`:

| landmark | `Cp` | |
|---|---:|---|
| `pMaxFactor 2.0` ceiling (202,650.0 Pa) | **+2.0274** | **26.1 % ABOVE stagnation** |
| stagnation `p0/p_inf = 1.5864` | +1.1888 | the most pressure any physics here can make |
| AGARD measured peak wing suction (η 0.96 upper) | −1.2270 | |
| **`pMinFactor 0.2` floor (20,265.0 Pa)** | **−1.6219** | **only 32.2 % beyond measured peak suction; 0.800 of the way to vacuum** |
| vacuum (p = 0) | −2.0274 | |

**The ceiling sits comfortably OUTSIDE the physics. The floor sits PLAUSIBLY INSIDE it.**
A transonic tip-vortex core routinely goes well below the wing surface's own peak suction,
and **R6's 33 floor-clipped wing cells sit at η 0.978–1.010, x 1.262–1.414 — the tip
trailing edge, exactly where a tip-vortex core would be.**

**🔴 THIS IS THE SAME KIND OF FAILURE AS CRM's, AND R5's WAS NOT.** A clamp positioned
*inside* the solution's real range, catching cells, with the solve then proceeding on a
censored field — that is what CRM does at 92.19 % on temperature. **This document does not
claim M6I and CRM are one problem.** It records that R6's failure and CRM's are the same
*kind*, while R5's — a genuine runaway past stagnation — is not. The R5 non-merge stands.

**🔴 A SECOND CANDIDATE SITS AT THE IDENTICAL LOCATION AND IS NOT DISMISSED.**
**84.13 % of this grid's near-wall faces above 70° sit at η ≥ 0.99** (measured on L1's own
`checkMesh -writeSets` output). **R6 died at η 0.978–1.010.** The mesh's worst region and
the failure's location are the same place. §5 is built to separate them. *Note that this is
a narrow question about the TIP CAP and is NOT the shock-window question already killed:
that kd-tree measurement found **zero** >70° faces in the x/c 0.30–0.70 upper-surface window
at all six graded stations, and it stays dead. Both candidates here lie **outside every
graded station**, which stop at η 0.96.*

## 2. THE ONE CHANGE — AND AN HONEST CORRECTION TO HOW IT WAS DESCRIBED

| file | from | to |
|---|---|---|
| `system/fvSolution` | `pMinFactor      0.2;` | **`pMinFactor      0.05;`** |

New floor **5,066.2 Pa**, `Cp` **−1.9261** — **0.950 of the way to vacuum, still strictly
positive pressure.** `pMaxFactor 2.0` is **NOT** touched; §1 shows the ceiling is not
implicated.

🔴 **THE CHANGE IS SINGLE AGAINST R6's CONFIGURATION, NOT AGAINST L2's, AND THIS DOCUMENT
SAYS SO RATHER THAN REPEATING THE DISPATCH'S WORDING.** The dispatch called it *"one
registered change against the L2 baseline"*. It is not: **R7 = L2 + `vanLeer` +
`pMinFactor 0.05`, which is two changes from L2.** `vanLeer` is retained because R6 earned
it on measurement — p residual **2–3× below R5's at every offset**, **falling** between
iterations 500 and 700, `Tmax` held at the baseline's own **339 K through 700 iterations**
where R5 was already at 378 K, and **1,494 iterations survived against 1,290**. The clean
single-variable comparison is therefore **R7 against R6**, both at `vanLeer`, differing only
in the floor — and every limb in §5 is written against **R6's** measured values for exactly
that reason.

**Also changed, and named rather than buried: `endTime` 5000 → 8000** (the 3,000 further
iterations §6 prices), and the §3 instrument is added. **`endTime` is deliberately absent
from the does-not-change list below, for the reason R5 addendum 1 `1ba860253` records.**

**DOES NOT CHANGE:** grid and `constant/` entire; **`pMaxFactor 2.0`**; `div(phid,p)` and
`div((phi|interpolate(rho)),p)` at **`Gauss vanLeer`** / `bounded Gauss vanLeer`; every
`div(phi,*)` scheme; `nNonOrthogonalCorrectors 2`; `limited corrected 0.33`; every
`relaxationFactors` entry; `transonic yes`; `SpalartAllmaras`; `constant/fvOptions`
including `limitTemperature`; `writeInterval 200`; `purgeWrite 2`; `decomposeParDict`.

**PRE-LAUNCH ASSERTIONS — nothing launches if any fails:** `diff -r` over `constant/`
empty; `cmp` over `system/` returns **exactly three** differing files — `fvSolution`,
`fvSchemes`, `controlDict` — carrying **exactly four** added lines (one `pMinFactor`, two
`vanLeer`, one `endTime`); each anchor matched **exactly once** before replacement.

## 3. THE INSTRUMENT — THE HOLE R6 LEFT, CLOSED, AND IT IS VALIDATED NOT MERELY WRITTEN

**R6 §7 conditioned a verdict on a quantity observable only at write times, on a case with
`writeInterval 200`, and the run died 95 iterations after the last write.** That is a
consistency defect in R6; this lane wrote it and the supervisor's review did not catch it
either. It is closed here, not apologised for.

R7 carries a `coded` functionObject **`clipCount`** printing, **every iteration**, the count
of cells at **both** limiters on the `wing` patch and over the whole volume. It reads `p`
and prints; **it writes no field and modifies none — verdict-inert instrumentation, not a
gate.**

**🔴 IT IS VALIDATED BY PLANTED CONTROL (rule 3), BEFORE THIS DOCUMENT WAS WRITTEN.** A
counter that reports 0 is worthless until shown able to report a non-zero. Run over two
fields whose answers were already measured by an **independent** reader (VTK + numpy)
earlier in this session:

| field | independent reader | `clipCount` | |
|---|---|---|---|
| `L2_PHIDP` t=6000, wing ceiling | 1705 / 1920 | **1705** | EXACT |
| `L2_PHIDP` t=6000, wing floor | 0 | **0** | EXACT |
| `L2_VANLEER` t=6400, wing ceiling | 0 | **0** | EXACT |
| `L2_VANLEER` t=6400, wing floor | 33 | **33** | EXACT |

**The reader is shown able to see a non-zero at BOTH limiters — 1705 at the ceiling on one
field, 33 at the floor on the other. Neither zero is a blind zero.** Record:
`verification/runs/M6I_runs/_clipcount/VALIDATION.txt`.

**It also saw what the wing-only view could not:** in the volume, `L2_PHIDP` had
**76,150 / 122,880 = 62.0 %** at the ceiling and **0** at the floor; `L2_VANLEER` had
**244 = 0.2 %** at the ceiling and **3,377 = 2.7 %** at the floor. **The floor is hit 13.8×
more than the ceiling under `vanLeer`, and zero times under `limitedLinear`.** R6 §7's
verdict is unchanged on either population.

## 4. THE PREDICTION — D1, D2 AND D3 UNCHANGED

Transcribed from R5 §4.2 and R6 §5, **not re-derived and not re-tuned**, kill-only:
**D1** `cfd_cp_rise_at_shock` at η 0.65 **≥ 0.1401**; **D2** CFD `Cp` rise across the
experiment's own shock interval at η 0.65 **≥ 0.0880**; **D3** `x_shock_cfd` must leave
**0.8851**.
**Cure gate, frozen elsewhere, re-invented nowhere:** **S1** ≥ 0.212 / ≥ 0.320; **S2**
< 0.85; **B1** ≤ 0.050 on 12 rows; **B2** ≤ Δ_local.

## 5. 🔴 THE DISCRIMINATOR — NUMERIC, WRITTEN BEFORE THE RUN, WITH AN ESCAPE HATCH

**Reference values, all measured on R6:** terminated after **1,494 iterations**;
**100 %** of its floor-clipped wing cells (33 of 33) sat at **η ≥ 0.95**.

- **FLOOR IMPLICATED** — the floor was censoring a physically real tip suction — if
  **either**: the run **completes** (rc = 0, `End`, last time 8000, age guard); **or** it
  survives **> 1,494 iterations** *and*, at the last written time, **fewer than 50 %** of
  floor-clipped wing cells lie at **η ≥ 0.95** (the failure moved away from the tip).
- **FLOOR EXONERATED → THE TIP-CAP MESH IS IMPLICATED** if the run terminates at
  **≤ 1,644 iterations** (1,494 + 10 %) *and* **≥ 50 %** of floor-clipped wing cells still
  lie at **η ≥ 0.95**, with the same lower-surface-dominated thermal runaway
  (R6: 45 of 57 cells above 360 K on the lower surface).
- **NEITHER PATTERN** — for example survival past 1,644 with the failure still at the tip,
  or a failure at neither limiter — **returns to the supervisor undecided.** This document
  does not pre-authorise a reading of an outcome it did not anticipate. *(R6's equivalent
  clause fired on its first use; it is kept deliberately.)*

**In every one of the three cases, §0 still binds: R7 is the last run on this line.**

## 6. COST (rule 12)

Measured basis: **R6 `L2_VANLEER` ran 1,494 iterations in 255 s at 4 ranks = 17.00
core-minutes = 0.011379 core-min/iteration.**
- **Predicted: 3,000 iterations → 34.1 core-minutes, ≈ 8.5 min wall at 4 ranks.**
- **Cap: 131.1 core-minutes**, unchanged from R6 and deliberately **not** 3 × 34.1, for the
  reason R6 §8 records: a converging run may legitimately need more solver iterations per
  outer iteration than a diverging one, and **a run that is merely slow must not be graded
  `NOT A RESULT` on cost.** A crossing grades the row `NOT A RESULT`; the cap is never
  raised; **nothing is killed on spend or clock** (Sanaa directive #17).
- `cost_basis`: **MEASURED** in core-minutes from the run's own logs. Dollars **DERIVED,
  NOT MEASURED** at $0.0513/core-h → ≈ $0.029.
- Family running total to date: **29.87 core-minutes of waste across R5 + R6, 0 results** —
  **2.7 % of one graded level (L1 cost 1,098).** Estimate-vs-actual lands in
  `docs/COST_CALIBRATION.md` at completion, waste named separately and never absorbed.

## 7. PRECONDITIONS AND CONTROLS

Graded by **`scripts/grade_m6_agard_cp.py`, blob `e9d5c04b` at `4c931d97c`**, unchanged,
**hash-verified against the committed blob in the same shell invocation as the run.** Its §7
planted control must print `reader_saw_the_plant: true` or the result is `NOT A RESULT`. The
strict completion rule applies in full **including the age guard**; P4's `End` line is read
from the terminating stage log via the driver fix at `0bc8fd09d`.

## 8. WHAT THIS DOCUMENT DOES NOT DO

1. **No grid triple, no observed order, no GCI.** One grid.
2. **Does not touch `pMaxFactor`, the `fvOptions` temperature bounds, or any relaxation
   factor.** §1 shows the ceiling is outside the physics.
3. **Does not register the tip-cap mesh change or SA-versus-SST.** §0 and §5 make those
   *consequences* to be authorised, never parallel items.
4. **Does not claim the tip suction IS physical.** §1 says *plausibly* inside the physics;
   §5 is the test, and it can come back exonerating the floor.
5. **Does not revive the shock-window mesh hypothesis**, which measured zero >70° faces at
   all six graded stations and stays dead. §1's mesh candidate is the tip cap only.
6. **Does not merge M6I with CRM.** §1.

*Drafted by a cfd `lab-lane`, 2026-09-13. NOT FROZEN — NOT COMMITTED — NO RUN AUTHORISED.
Alters no existing gate, threshold, band, cap or label. No agent's message is Sanaa's
consent. Submissions parked.*

---

# ADDENDUM 1 — 2026-09-13, cfd-supervisor. §2's LINE COUNT IS ARITHMETICALLY INCOMPATIBLE WITH THE INSTRUMENT §2 AND §3 BOTH MANDATE. AMENDED FROM FOUR TO FIVE.

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.**

**PRE-COMPUTE. Rule 2 therefore permits an AMENDMENT, not merely an addendum.** Verified in
the same shell invocation as this commit: `L2_PMIN/` is staged but **no solver has ever
started against it** — no `RC.txt`, no `LAUNCH.log`, no `LAUNCHED.txt`, no
`log.rhoSimpleFoam`, and no time directory beyond `0` and `0.orig`. **No gate, threshold,
band, cap or label is touched:** D1 ≥ 0.1401, D2 ≥ 0.0880, D3, S1 (≥ 0.212 / ≥ 0.320),
S2 (< 0.85), B1 (≤ 0.050), B2, the 131.1 core-minute cap and the grading path are all
unaffected. §0's hard limit stands: **R7 is the last run on this line.**

## A1.1 THE CONTRADICTION

§2's launch assertion, prefixed *"nothing launches if any fails"*, requires `cmp` over
`system/` to return **exactly three** differing files carrying **exactly four** added lines.

Four lines later, the same §2 says *"…and the §3 instrument is added"*, and §3 says
*"**R7 carries** a `coded` functionObject `clipCount`…"*.

**Installing that instrument necessarily adds a fifth line to `controlDict` — the
`#include "clipCount.fo"` — plus the new file `system/clipCount.fo`. §2's count and §3's
mandate cannot both be satisfied.** Measured on the staged case: the added lines are
`pMinFactor` (fvSolution), two `vanLeer` (fvSchemes), `endTime` (controlDict) and the
`clipCount` include (controlDict) — **five**, and `system/clipCount.fo` at 2,034 bytes.

## A1.2 THE AMENDMENT

§2's *"exactly four added lines"* is **struck** and reads **exactly five added lines** —
one `pMinFactor`, two `vanLeer`, one `endTime`, one `clipCount` include — **plus the new
file `system/clipCount.fo`.** The three-differing-files clause is unchanged and was met.
The original is **not rewritten**; it stands above with this strike recorded here.

The physical configuration is unchanged by this amendment and was never in doubt: nothing
else differs from the L2 baseline, and what is staged is exactly what §2's change table and
§3 mandate.

## A1.3 THE LANE DID NOT ADJUDICATE ITS OWN DEFECT, AND THAT IS WHY THIS IS CLEAN

A defensible reading existed — that "four" enumerates the **numerics** changes and the
instrument is accounted for separately in §3 — and it may well be the right one. **The lane
authored both the defect and the candidate reading, declined to adjudicate from that
position, and stopped with the case fully staged and the solver never started.** On R5 a
lane picked a reading and I had to file an addendum taking the fault; this time the hatch
was respected rather than reasoned around, which is what I asked for in those words.

## A1.4 A DEFECT IN THE CONSISTENCY CHECKER ITSELF — A PRESENCE CHECK IN THE COSTUME OF A CONSISTENCY CHECK

The 46-assertion checker built after R5 passed R7 clean. Its relevant assertion was:

```
chk("assertions: 3 files / 4 lines", 'exactly three' in R7 and 'exactly four' in R7)
```

**It verified the phrases were PRESENT. It never verified the COUNT was CORRECT given what
the document mandates elsewhere.** A checker built to catch documents that contradict
themselves, failing in exactly that way, one level up.

**REQUIRED of any successor:** the expected line count is **recomputed** from the document's
own change table plus its instrumentation clause and compared — never grepped for as a
literal. Recorded so it outlives this session.

## A1.5 TWO THINGS DISCLOSED RATHER THAN SLIPPED IN

**Rule 14 caught a real hazard while staging.** `controlDict` already carried a `functions`
block with `forceCoeffs`, `residuals` and `yPlus`. The lane's assert refused to replace it;
it **inserted** one line and then proved all three survivors byte-identical to L2's. **A
blind-written `functions` block would have silently deleted the force coefficients** — the
channel the verdict is read from.

**The instrument carries one counter beyond §3's description:** `vol_below_old_0p2_floor`,
the count of cells below the *old* 0.2 floor, which says directly whether the solution uses
the room the new floor gives it. **Verdict-inert**, and on `L2_VANLEER` t=6400 it reproduces
the independently measured **3,377** exactly. Disclosed here, not slipped in.
