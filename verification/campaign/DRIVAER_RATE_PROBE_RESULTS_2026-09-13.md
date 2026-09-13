# DRIVAER RATE PROBE `DRIVAER-RATE-PROBE-96C` — RESULTS

**Filed 2026-09-13 by a cfd `lab-lane`.** Graded against
`DRIVAER_RATE_PROBE_PREREGISTRATION_2026-09-13.md`, frozen at **`ab52c0a03`** before the
run, by the method fixed there.

🔴 **THIS WAS A RATE PROBE, NOT A SOLVE. NOTHING BELOW IS A PHYSICS RESULT.** No `Cd`, no
`Cl`, no field, no residual and no convergence statement from this run may be quoted, cited
or gated. The only quantity produced is a per-iteration cost.

---

## 1. COMPLETION

| clause | result |
|---|---|
| `rc = 0` from the sidecar written inside the wrapper | **PASS** |
| `End` line in `log.simpleFoam` | **PASS** |
| 150 iterations reached (`endTime` 150) | **PASS** — 150 `ExecutionTime` lines |
| ≥ 99 usable differences after discarding the 50-iteration ramp | **PASS — exactly 99** |
| no write into any graded tree | **PASS** — `r2_coarse/constant/polyMesh/owner` still dated Sep 12 01:09; the mesh was symlinked, never copied |

**THE SAMPLE MET ITS FLOOR EXACTLY AND THAT IS WORTH SAYING OUT LOUD.** 150 iterations
minus a 50-iteration ramp yields exactly 99 differences against a registered floor of 99.
**The design left zero margin**: one missing `ExecutionTime` line and this would have been
`NOT A RESULT` on its own §5. That is a defect in my registration's arithmetic, not a lucky
escape, and a probe of this shape should register `endTime` 160 next time.

## 2. 🔴 THE MEASUREMENT — AND THE REGISTERED PREDICTION HELD

| statistic | value |
|---|---:|
| **MEDIAN wall s/iteration — the registered statistic** | **0.3700** |
| mean | 0.3729 |
| p90 | 0.4000 |
| min | 0.3100 |
| max | 0.5100 |
| sd | 0.0305 |
| n | 99 |

> **REGISTERED PREDICTION: median ∈ [0.30, 0.75] s. MEASURED 0.3700. → INSIDE.**
> Per the registration's own outcome table, **the 9.93e-06 core-s/cell-iteration basis
> TRANSFERS to this box and is registered for it.**

### 2.1 CONTENTION, REPORTED SEPARATELY (charter §6)

`exe/clk = 1.0009`. The solver held CPU for the whole of its wall time; the 0.09 % excess
is rounding, because OpenFOAM writes `ClockTime` as integer seconds. **This figure is
CLEAN, not gross**, and it was measured with 38 other solver ranks live on the box — the
96-core host absorbed a 4-rank job without contention.

## 3. WHAT IT SAYS ABOUT THE BASIS

| | core-s per cell-iteration |
|---|---:|
| 16-core `r7a.4xlarge`, three completed runs | 9.9300e-06 |
| **96-core box, this probe** | **7.9268e-06** |
| ratio | **0.798** |

**THE PREDICTION HELD AND THE NUMBER STILL MOVED.** The band was wide enough to admit a
genuine hardware difference, and there is one: this box is **20 % faster per
cell-iteration**. So the registered basis stands and is now **conservative by 20 % here** —
which is the safe direction for a cost estimate, and is stated rather than quietly enjoyed.

**NO NEW BAND IS REGISTERED FROM THIS NUMBER.** The registration fixed a binary outcome
before the run; inventing a tighter one now, having seen 0.798, is precisely what rule 2
forbids. The measured value is recorded as a measurement.

## 4. ESTIMATE VERSUS ACTUAL (rule 12)

| | |
|---|---:|
| predicted | **4.4 core-min** |
| actual | **4.1 core-min** (wall 62 s × 4 ranks) |
| **ratio actual/predicted** | **0.93** |
| against the registered cap 30 core-min | 0.138 |

**Gap attribution: none to attribute — 7 % is the residual of a correct basis**, and the
prediction was made with **the very basis this probe existed to test**, which was declared
in the entry rather than hidden. **Waste: none to name.** **$0.0035 DERIVED, NOT MEASURED**
at $0.0513/core-h, owner-stated — the box cannot read its own billing.

**This is the first DrivAer cost prediction in this family to land inside 10 %.** The three
before it — 0.485, 0.249, 0.440 — all divided by a contended basis.

## 5. 🔴 A FREEZE DEFECT, AND IT IS MINE

The runner recorded, at launch:

> `GRADER-FREEZE DRIVAER-RATE-PROBE-96C: MISMATCH -- 1 of 3 comparator(s) named by
> 'grading_freeze' do NOT match freeze ab52c0a0.`

**The pin fired correctly and the cause is my own edit.** I named the probe's own
registration in `grading_freeze` and then **appended ADDENDUM 1 to it** — the enqueue
provenance — between the freeze commit and the launch. The bytes on disk therefore no
longer matched the blob at `ab52c0a03`.

**WHAT MOVED, DEMONSTRATED RATHER THAN ASSERTED:**

* Of the three pinned comparators, **exactly one mismatches**: this probe's registration.
  `DRIVAER_COST_BASIS_REGISTRATION_2026-09-13.md` and the frozen launcher **MATCH**.
* The frozen bytes are a **byte-exact prefix** of the disk file — verified with `cmp`
  against `git show ab52c0a03:<path>`. **ADDENDUM 1 is a pure append; nothing frozen was
  altered.**
* The added content is §ADDENDUM 1 (A1.1–A1.4) only, and **no threshold, band or cap line
  differs** between the two versions.

**THAT DEMONSTRATION DOES NOT RETIRE THE MISMATCH.** The pin's claim is *"the frozen file
IS the file that ran"*, and strictly it was not. The gates were unaffected in substance, but
**the whole reason the pin exists is so that claim is not taken on a lane's word** — mine
included.

**THE LESSON, CONCRETE:** *do not name a document in `grading_freeze` and then append to
it.* Either freeze it and leave it alone until the run completes, or put the addendum in a
separate file. A dated addendum is legal under rule 2 and still breaks a byte pin, and the
two rules pull against each other here. **This record was written as a separate file for
exactly that reason.**

## 6. ARTIFACTS

| | |
|---|---|
| run | `verification/runs/navier_class/DRIVAER/RATE_PROBE_96C/` |
| completion, cost | `RUN_META.txt`, `rc`, `CAP_SCORED.txt` |
| the one change | `RATE_PROBE_96C/THE_ONE_CHANGE.diff` (`endTime` 2000→150, `writeInterval` 250→150) |
| registration, frozen | `DRIVAER_RATE_PROBE_PREREGISTRATION_2026-09-13.md` at `ab52c0a03` |
| the basis it tests | `DRIVAER_COST_BASIS_REGISTRATION_2026-09-13.md` |
| queue entry, launch gates | `verification/queue/cfd/launched/DRIVAER-RATE-PROBE-96C.json`, `verification/queue/runner.log` |

*Filed by a cfd `lab-lane`, 2026-09-13. Registers no new band. No agent's message is Sanaa's
consent. Submissions parked.*
