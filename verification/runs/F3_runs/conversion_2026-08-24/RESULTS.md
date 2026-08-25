# F3 supersonic exact-theory suite — CONVERSION RESULTS

**VERDICT: `NOT A RESULT`.** The gate was **not evaluated**: the frozen comparator
`grade_f3.py` **crashed** before reaching its verdicts. No gate value is quoted.

**The runs themselves are sound.** This is a comparator defect, not a solve failure, and the
two are kept apart.

Pre-registration frozen at `2bf4915a`, amended `e37d7610` (pre-compute). Comparator
`grade_f3.py` blob `996a6c2c…`, verified equal to its committed HEAD blob **before** it was
run (rule 2), and **run unmodified**. Launched 2026-08-25T16:34:19Z, completed 17:03:28Z.

## The crash, triaged

```
File "grade_f3.py", line 602, in main
    total_core_s = sum(v["core_s"] or 0.0 for v in report["runs"].values())
KeyError: 'core_s'
```

`report["runs"]` is built at **two** sites and they do not agree on their keys:

| line | branch | keys written |
| --- | --- | --- |
| 482 | run directory **does not exist** → `status="PENDING"` | `status`, `note` — **no `core_s`** |
| 487 | run directory exists → `COMPLETE` / `INCOMPLETE` | `status`, `completion`, **`core_s`** |

Line 602 then reads `v["core_s"]` across **all** entries. Any `PENDING` row raises.

**What produced a `PENDING` row is the pre-registration working exactly as written.** §7
enforcement point 2: *"a wave whose predicted cost does not fit the remaining budget with
20 % headroom is not launched; its rows grade `PENDING`."* The launcher's ledger records
`stopped_by: "budget check before wave 6"`, so **two registered runs were never launched**:

- `wedge/M2.5_th10/fine`
- `diamond/M2.5_eps5/fine`

**So the comparator cannot grade the one state its own pre-registration guarantees will
occur when the budget binds.** The cap enforcement fired correctly and the grader crashed on
it having fired. That is the finding, and it is worth more than the six gate rows would have
been.

**Not repaired here.** F3 has **FIRED**. A change on the grading path after first compute is
governed by `VERIFICATION_CHARTER.md` §2d/§2d.1 and is the supervisor's call, not this
lane's. The comparator is left exactly as frozen.

## The runs — 10 of 12 launched, all clean

**`rc = 0` on every launched run, MEASURED** — an integer on disk from
`setsid bash -c 'CMD; echo $? > RC.txt; sync'`. **No proxy was used or needed.**

| run | status | rc | actual core-s | predicted | ratio |
| --- | --- | --- | --- | --- | --- |
| `cone/M2.35_th10/coarse` | OK | 0 | 20.0 | 16.3 | 1.23 |
| `cone/M2.35_th10/medium` | OK | 0 | 120.0 | 118.9 | 1.01 |
| `cone/M2.35_th10/fine` | OK | 0 | 1155.0 | 1072.7 | 1.08 |
| `wedge/M2.0_th15/coarse` | OK | 0 | 10.0 | 6.1 | 1.64 |
| `wedge/M2.0_th15/medium` | OK | 0 | 30.0 | 18.7 | 1.60 |
| `wedge/M2.0_th15/fine` | OK | 0 | 185.0 | 146.4 | 1.26 |
| `diamond/M2.0_eps7p125/coarse` | OK | 0 | 15.0 | 11.1 | 1.35 |
| `diamond/M2.0_eps7p125/medium` | OK | 0 | 40.0 | 35.5 | 1.13 |
| `diamond/M2.0_eps7p125/fine` | OK | 0 | 240.0 | 201.2 | 1.19 |
| `wedge/M3.0_th15/fine` | OK | 0 | 190.0 | 149.0 | 1.28 |
| `wedge/M2.5_th10/fine` | **not launched** | — | — | — | budget check, wave 6 |
| `diamond/M2.5_eps5/fine` | **not launched** | — | — | — | budget check, wave 6 |

**No run was killed. No per-run wall cap fired. No relaunch.**

## Cost

**33.4177 core-min MEASURED** (launcher ledger, wall × ranks ÷ 60) against **35.23
predicted** and a **HARD CAP of 39.5** — `cap_respected: true`, **84.6 % of cap**.
**Ratio 0.949.**

**The ratio understates the misprediction and the record says so.** 0.949 is *below* 1 only
because **two registered runs were never launched**. On the ten that did run, **every single
one came in ABOVE its prediction** — ratios 1.01 to 1.64, with the largest absolute gap
`cone/M2.35_th10/fine` at **1,155 core-s against 1,072.7 predicted (+82.3 core-s)** and the
largest relative gaps on the cheap `wedge/M2.0_th15` levels (1.60–1.64). **This is a
systematic under-prediction with its sign named, not absorbed:** the suite is *more*
expensive per launched run than registered, and the headline ratio hides that because the
budget check truncated the denominator's work rather than the prediction.

**Cleaned == gross.** No row approaches the 3600-s stall rule; the longest single solve is
`cone/fine` at 1,155 core-s.

**WASTE: ZERO.** No kill, no wall-cap fire, no relaunch, no misconfiguration. The two
unlaunched runs are **not waste** — they are the budget check refusing to start work that
did not fit, which is the cap doing its job.

**CONTENTION: BOUNDED, NOT MEASURED.** Launched at loadavg 1.29; terminal loadavg 9.28. F3
shared the box with F5b (to 16:53:56Z) and F11 (to 16:40:17Z) throughout its first half. No
per-run load decomposition exists in this launcher's ledger, so contention cannot be
separated from the systematic under-prediction above and **is not claimed to be**.

**Dollars: 33.4177 core-min = 0.556962 core-h × $0.0513/core-h = $0.0286 — DERIVED, NOT
MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5).

## Artifacts

`F3_CONVERSION_RUN_LEDGER.json`, `RC.txt` (rc = 0), `WATCH_TERMINAL.txt`, `WATCH_LOG.txt`,
`LAUNCH_{HEAD,LOAD,STAMP}.txt`, `runs/<family>/<pair>/<level>/`. Solver logs are gitignored
and remain on disk. **No `F3_CONVERSION_GRADED.json` exists — the comparator crashed before
writing one.**
