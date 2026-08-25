# F3 conversion — disposition of the three `PENDING` rows: **BLOCKED, not launchable**

**Written 2026-08-25 by a cfd lab-lane under cfd-supervisor. ZERO COMPUTE: no solver was
started, no case directory was created, no file under `runs/` was touched.**

**Tasked to fire the three unfired rows as a parallel batch.** They were not fired. This
document records why, with the arithmetic, so that the refusal is auditable and so the next
reader does not re-open it as an oversight.

---

## 1. What was verified before anything was decided

| check | result |
| --- | --- |
| `F3_CONVERSION_PREREGISTRATION.md` frozen and hash-identical to HEAD | **YES** — disk `git hash-object` == `HEAD:` blob == `774dad4684295a0bf80299ed7092e06aa4c29b18` |
| `grade_f3.py` byte-identical to HEAD | **YES** — `6fea2e1d64cc3c377dd0e05ee4c08f6e83e1d049` |
| `rerun_f3.py` byte-identical to HEAD | **YES** — `77615bd94b645b97985f9717f489850879d1ae55` |
| the two unlaunched run directories | **ABSENT** — `runs/wedge/M2.5_th10` and `runs/diamond/M2.5_eps5` do not exist; nothing was half-fired |
| HEAD at time of check | `81182ebfffe9ea1ddcfde8976a5f0b7a6b3b2921` |

---

## 2. The three rows, and the two runs beneath them

**Three `PENDING` gate rows, but only TWO unlaunched runs** — `wedge/M2.5_th10/fine` feeds
two gates. This distinction matters: the batch that was requested is a batch of **two**
single-core cases, not three.

| gate row | run it needs | run dir |
| --- | --- | --- |
| G-F3-1 wedge surface pressure / M2.5_th10 | `wedge/M2.5_th10/fine` | absent |
| G-F3-2 wedge shock angle / M2.5_th10 | `wedge/M2.5_th10/fine` (same run) | absent |
| G-F3-5 diamond wave drag / M2.5_eps5 | `diamond/M2.5_eps5/fine` | absent |

Source: `F3_CONVERSION_GRADED.json` (`verdict: "PENDING"`, `note: "fine run absent or
incomplete"`, `core_s: null`) and `F3_CONVERSION_RUN_LEDGER.json`
(`status: "PENDING"`, `reason: "budget: wave 6 not launched"`).

---

## 3. Why they are `PENDING`: a FROZEN HARD CAP fired exactly as registered

`F3_CONVERSION_RUN_LEDGER.json` records `stopped_by: "budget check before wave 6"` and
`cap_respected: true`. That is §7 enforcement point 2 of the frozen pre-registration, whose
code is `rerun_f3.py:151`:

- `CAP_CORE_MIN = 39.5` (**HARD CAP**, `rerun_f3.py:36`), `WAVE_HEADROOM = 1.20` (`:39`)
- spent over the ten launched runs: **2,005.06 core-s = 33.4177 core-min** (measured)
- remaining under the cap: 2,370.0 − 2,005.06 = **364.94 core-s = 6.0823 core-min**
- wave 6 predicted: 148.1 + 189.8 = **337.9 core-s**
- the registered check: 2,005.06 + 337.9 × 1.20 = **2,410.54 > 2,370.0** → **refuse, by 40.54 core-s**

**The cap did not fail. It worked.**

### 3.1 The refusal survives removing the headroom rule

Raw 337.9 predicted core-s would fit inside 364.94 remaining. It does not survive the
**measured** cost of this suite. The calibration ratio over launched runs only is
**1.1290** — every one of the ten launched runs exceeded its prediction (1.01–1.64):

> expected wave-6 actual = 337.9 × 1.1290 = **381.50 core-s** vs **364.94** remaining.

So even with enforcement point 2 disabled, **enforcement point 3 — the global watchdog
(`rerun_f3.py:175`), which is unconditional — terminates every live run on reaching 2,370.0
core-s.** The runs would be killed at roughly **95.7 %** complete, **16.56 core-s short**, and
grade `KILLED`. **Firing produces a killed row, not a result.** That is the quantitative
heart of this refusal: the request cannot be satisfied, not merely that it is disallowed.

---

## 4. Why this is a reason firing cannot cure

Three independent bars, any one of which is sufficient:

1. **Standing rule 12** — *"An overrun stops the run; it does not get a new budget."* The
   cap is spent. There is no lawful budget to fire into.
2. **Standing rule 2 / VERIFICATION §2d** — after first compute, gates are closed and changes
   land only as dated addenda that **cannot alter a gate, threshold, cap or label.** The
   39.5 core-min cap is a **cap**. It cannot be raised by any addendum, by any agent.
3. **The frozen run matrix.** §6 fixes 12 runs and §7 fixes the launch order and the waves.

**A re-partition of wave 6 was considered and is REJECTED.** Splitting the wave would let the
cheaper run (`wedge/M2.5_th10/fine`, 148.1 pred) pass a per-run budget check — 2,005.06 +
177.72 = 2,182.78 < 2,370.0 — while the second would still be refused. It is rejected because
re-partitioning the waves **changes what the cap does, after compute, having seen that it
refused.** The motive is the giveaway: the re-partition is attractive only because the
refusal is already known. That is re-posing a cap to fit an answer, which is the precise
thing rule 2 exists to prevent. **It is also above a lane's level and is not taken here.**

**No result was manufactured to fill a cell.** The three cells stay `PENDING` in
`F3_CONVERSION_GRADED.json` and `RESULTS.md`, exactly as the frozen comparator wrote them.

---

## 5. The separate deliberately-withheld item, named so it is not re-discovered as an oversight

§6 records the **cone M3.0 / θc12** pair as **deliberately NOT re-run**: the old record
graded it `PASS` on a medium mesh with **no fine level**, and a fine cone mesh costs ~17.9
core-min alone. Its 2026-07-28 `PASS` is **not converted and is not a credential.** It is not
one of the three `PENDING` rows and it is not a budget casualty — it was withheld by design.

---

## 6. The only lawful route to these three cells, which is NOT a lane's call

The two runs are physically trivial — **~381 core-s ≈ 6.36 core-min ≈ $0.0054 derived at
$0.0513/core-h, derived NOT measured.** Cheapness is not the obstacle; the frozen cap is.

The lawful route is a **new pre-registration for a new rung**, frozen before compute, with its
own cap, its own gate bands and its own grading path. Two hazards must be carried into any
such decision and are recorded here rather than left for the drafter to rediscover:

- **Band contamination.** G-F3-1, G-F3-2 and G-F3-5 bands would be re-derived by an agent
  that now knows this suite's measured deviations. F3's own §2 confronts exactly this and
  defends it by deriving every band from a **stated principle** — reference class, or the
  detector's quantization floor from mesh geometry — never from a measured deviation. Any
  successor must meet that same standard explicitly.
- **It cannot change F3's tally.** F3 is closed at **5 PASS, 1 GATE FAIL, 1 NOT A RESULT,
  3 PENDING**. A successor rung produces its own rows under its own registration; it does not
  retroactively fill these cells, and this record must not be cited as if it could.

**Referred to cfd-supervisor. Not taken here.**

---

## 7. Cost calibration (standing rule 12)

**No compute was incurred by this lane: 0.0000 core-minutes, $0.00.** No estimate-versus-actual
row is added to `docs/COST_CALIBRATION.md`, because no process consuming compute completed —
manufacturing a calibration row for zero compute would put a fictitious measurement in the
ledger.

The F3 conversion's own calibration is **already on record** and is not restated as new:
rows **C-66** (original) and **C-68** (correction), ratio **1.1290** over launched runs only,
waste **zero**, contention **bounded, not measured, and known to be under-counted**.

---

## 8. Verdict

| gate row | verdict | reason |
| --- | --- | --- |
| G-F3-1 / M2.5_th10 | **BLOCKED** | frozen 39.5 core-min HARD CAP spent; run unlaunchable within it |
| G-F3-2 / M2.5_th10 | **BLOCKED** | same run as above |
| G-F3-5 / M2.5_eps5 | **BLOCKED** | frozen 39.5 core-min HARD CAP spent; run unlaunchable within it |

**`BLOCKED` is the disposition of the LAUNCH REQUEST.** The **graded cells stay `PENDING`**
in the frozen comparator's output, which is the correct label there under §9: *not launched,
budget or otherwise.* Neither word is used to soften the other, and no frozen file was edited
to record this.
