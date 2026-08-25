# F5b Physics rung `physics_p1` — RESULTS

**VERDICT: `NOT A RESULT`.** §7 outcome map row 3. Completion clauses **4 (fields present)**
and **6 (age guard)** FAIL. **The gate was NOT evaluated and no partial `A_L` is quoted** —
charter §2: a gate that was not reached is stated as not reached, never replaced by a nearer
gate that was.

Pre-registration frozen at `c1ba1845` (stage 1) / `a80d5f36` (stage 2), body pin
`c44b9130…8177b9df`. Reader `analyse_f5b_physics.py` blob
`6c6d34d02e6de925457dbfdbf75a0e004168f345`, **hashed against its committed blob before it
graded** and **run unmodified**. Launched 2026-08-25T16:14:24Z, serial (1 rank), completed
16:53:56Z.

## The failing clauses, and their single root cause

Both failures have **one** cause, and it is in the reader, not the flow:

- The reader's frozen literal is **`END_TIME_STR = "21.9440"`** (line 120) and it looks for
  `case/21.9440/`.
- **OpenFOAM wrote `case/21.944/`.** It formats time-directory names with its general float
  formatting, which **strips the trailing zero**. A directory named `21.9440` was never
  going to exist.
- Clause 4 therefore reports all five required fields missing; clause 6 reports
  `0/ or endTime dir absent`. **Two clauses, one literal.**

**Reported, and it does NOT re-grade anything:** all five required fields are present under
the name OpenFOAM actually used — `U` (160,265 B), `p` (50,237 B), `k` (59,981 B), `omega`
(49,128 B), `nut` (59,965 B), plus `phi` and `yPlus` — and the oldest of them (16:53:51) is
newer than the newest file in `case/0/` (`phi`, 16:14:25), so the age guard's *substance*
holds. **This is recorded as an observation about the run, not as a grade.** The frozen
reader returned `NOT A RESULT` and that is the verdict. It is not re-posed, not re-run
against a patched literal, and no gate value is extracted by hand — L-44, and charter §8:
a documented failure is shipped as one.

**No entitlement is claimed about what the gate would have said.** `A_L`, `δ_close`, the
collapse pair and the Courant distribution were never computed, because the reader stops at
completion. Any statement about whether dynamic stall was present in this run is **outside
this rung's entitlement**.

## Completion clause accounting — SEVEN evaluated by the reader, ONE at launch

| # | clause | result | how established |
| --- | --- | --- | --- |
| 1 | `rc = 0` | **OK** | **DISCLOSED PROXY — NOT A MEASURED rc** (see below) |
| 2 | `End` line | **OK** | MEASURED — 1 final `End` in `log.pimpleFoam` |
| 3 | last time == `endTime` | **OK** | MEASURED — last `Time = 21.944`, 42,200 `Time` lines |
| 4 | fields present | **FAIL** | MEASURED — `case/21.9440/` does not exist |
| 5 | four-way step count | **OK** | MEASURED — `ExecutionTime` 42,200 == `coefficient.dat` rows 42,200 == `record.json n_steps` 42,200; `^Courant Number mean:` 42,202 == n_steps + 2; `^Mesh Courant Number mean:` 0, anchored out |
| 6 | age guard | **FAIL** | MEASURED — same missing directory |
| 7 | pre-existing-state guard | **OK** | **At LAUNCH**, not by the reader — the wrapper refused-or-passed A1 (D-1) |
| 8 | cap guard | **OK** | MEASURED — `wall_seconds` 2367.3 ≤ 4200 s; **39.455 core-min ≤ 72.0 cap** |

### Clause 1 is a proxy, and this is not softened

**`NO rc IS RECORDED ON DISK`** — the frozen reader's own words, kept on the face of the
clause. **F5b launched before the rc carry-forward existed**, so no `RC.txt` was written and
the rc is **structurally unavailable**: `setsid` detaches so the solver outlives its
launching agent, the wrapper then exits, and nothing ever reaps the driver. `WRAPPER_RC.txt`
= 0 records the **launcher's** exit, not the driver's.

**Disclosed circularity:** part of the proxy is `End` on the three prelude logs, and `End`
is **itself another limb of the same conjunctive rule**. `record.json` presence is the
independent half — and it proves only that the driver **reached its final write**, not that
it **exited cleanly**.

**The proxy was PLANTED and shown able to see a failure**
(`verification/runs/F5b_runs/plant_rc_proxy_control.py`): `record.json` absent → clause 1
FAILS; prelude missing → FAILS; prelude without `End` → FAILS; clean tree → passes. The
`record.json` arm had **never** been exercised by the reader's own selftest before this
plant (L-320). **Bound that remains:** a driver dying *after* writing `record.json` passes
clause 1 **and every other limb**.

## Cost

**MEASURED: 39.426 core-min** (`ExecutionTime` 2365.55 s × 1 rank ÷ 60) against a
**registered cap of 72.0** — **54.8 % of cap, NOT breached**. Predicted 35.0
(band 28.8–48.0). **Ratio 1.127.** Wall 2,372 s; `record.json wall_seconds` 2367.3.

**Cleaned == gross.** The single solver row is **2,367 s, under the 3,600-s stall rule**, so
the rule does not match and the row is a legitimate long serial solve — stated explicitly
rather than left to the rule to apply itself (§8 close-out clause 3).

**WASTE: ZERO.** No kill, no timeout, no relaunch, no misconfiguration. One run, one arm.

**CONTENTION — SELF-INFLICTED, NAMED SEPARATELY, and it does not move the ratio.** F5b
launched at loadavg **0.24** as the sole job. At 16:34:19Z, with F5b **64 % complete**,
**this same lane launched F11 and F3 onto the same 16-core box.** Terminal loadavg **9.69**.

**Load-conditioned basis — RECONSTRUCTED, NOT MEASURED.** Source: this run's
`WATCH_LOG.txt`, 127 samples at 15 s, `ExecutionTime` differenced between consecutive
samples with each interval attributed to the load reading that opened it; boundaries exact
to ±15 s.

| segment | core-s | share of sampled |
| --- | --- | --- |
| load < 2.0 (quiet) | 739.3 | 38.8 % |
| 2.0 ≤ load < 6.0 | 561.1 | 29.5 % |
| load ≥ 6.0 (contended) | 603.6 | 31.7 % |
| **ET-weighted mean load** | **4.13** | |

**Coverage gap, stated rather than smoothed:** the samples cover **1,904.0 of 2,365.55
core-s (80.5 %)**. The uncovered **461.55 core-s (19.5 %)** is the window between launch
(16:14:24Z) and the sampler being armed (16:22:07Z). That window is **bracketed by two
measured readings — 0.24 at launch and 1.04 at the first sample, both quiet** — so it is
**bounded as quiet, not sampled**. It is not added to the quiet segment.

**§8 item A-4's deliverable — a clean measured cost basis for the F5b family — is NOT
DELIVERED.** In those words. A future lane must **not** re-use 39.426 core-min as an
uncontended basis: roughly a third of it was burned at loadavg ≥ 6 because of concurrency
this lane created.

**Dollars: 39.426 core-min = 0.65710 core-h × $0.0513/core-h = $0.0337 — DERIVED, NOT
MEASURED** (the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5).

## Levers verified active

`Selecting dynamicFvMesh dynamicMotionSolverFvMesh`; `Selecting motion solver: solidBody`;
`Selecting solid-body motion function oscillatingRotatingMotion`; `Selecting RAS turbulence
model kOmegaSST`. **A5's lever echo self-verified**: `log.levers` asserts the captured
`fvSolution` contains `pcorr` (so it is the PIMPLE moving-mesh dictionary, after E2:282's
restore) and its md5 `f50321bf…` matches the live `system/fvSolution`. `pcorr`/`pcorrFinal`
remain **`unverifiable-from-logs`** as registered.

## Carry-forward — THREE items now, for the next F5b registration

1. **A real rc on disk**: `setsid bash -c 'CMD; echo $? > RC.txt; sync'`. Already applied on
   F11 and F3, which needed no proxy.
2. **A clause-1 breaker that actually breaks the `record.json` branch** (L-320).
3. **NEW, and it is what cost this run its verdict: `END_TIME_STR` must not be a hand-written
   literal.** It must be derived from what OpenFOAM actually writes, or matched
   numerically against the time directories on disk rather than by string equality.
   `21.9440` never existed; `21.944` did. **A completion rule that names a directory by a
   formatted string is testing the formatter, not the run.** No selftest caught it because
   `_synthetic_run` *creates* its time directory using the same literal the reader looks
   for — the fixture and the checker share the bug, so the arrangement is self-consistent
   and false. That is L-320's disease again, one layer out.

**None of these may be applied to F5b's frozen artifacts: F5b has FIRED.** Rule 6 governs;
rule 2 closes the grading path at the pre-registration commit.

## Artifacts

`record.json`, `case/log.pimpleFoam`, `case/log.levers`, `case/21.944/`,
`case/postProcessing/forceCoeffs1/0/coefficient.dat` (42,200 rows), `WATCH_LOG.txt`,
`WATCH_TERMINAL.txt`, `WRAPPER_RC.txt`, `LAUNCH_{HEAD,LOAD,CMD,STAMP}.txt`, `LANE_STATE.md`.
Solver logs are gitignored and remain on disk.
