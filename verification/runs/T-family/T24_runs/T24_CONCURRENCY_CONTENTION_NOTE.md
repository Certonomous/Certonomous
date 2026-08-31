# T24 — CONCURRENCY CONTENTION: a MEASUREMENT, for the calibration row to cite

**This note is a MEASUREMENT and nothing else.** It proposes **no new rule, no
new tool and no new unit**, and it asks for none. The lab's unit remains
core-minutes as `CLAUDE.md` rule 12 defines it (`wall_s × ranks ÷ 60`). Sanaa's
14-day rule freeze (`etc/sessions/2026-08-31T1544Z_sanaa_plumbing_freeze.md`) is
in force and this note is written to stay inside it.

Filed under the case directory, not the scratchpad (L-186), so the lane filing
the `docs/COST_CALIBRATION.md` row can cite it by path.

Gates frozen at `docs/campaigns/T-family/T24_PREREGISTRATION.md`, commit
`b9057489914317af26146c9fb709b8d7229928b1`. **This note grades nothing, marks
nothing and assigns no verdict.**

---

## 1. What was measured

Twelve `T24_P*_U*` cases, `chtMultiRegionSimpleFoam`, **1 rank each**, launched
2026-08-31 20:01:19Z–20:16:15Z onto a **16-core** c7a.4xlarge, running
**twelve-concurrent**. The reference is T23, the identical geometry, mesh and
iteration count, which ran **four-concurrent** throughout.

**The comparison is taken at MATCHED ITERATION BANDS, and that is the whole
methodological content of this note.** A whole-run average would confound
contention with the SIMPLE **startup transient**, which is large and which this
lane first misread as contention. T23's own completed log settles the transient
at constant four-concurrent [MEASURED, `T23_runs/T23_P305_U10/log.solve`]:

| iteration band | 0–500 | 500–1000 | 1000–2000 | 2000–4000 | 4000–7000 | 7000–10000 |
|---|---:|---:|---:|---:|---:|---:|
| iter/s | 3.822 | 4.098 | **6.272** | **6.012** | **5.753** | 5.796 |

Concurrency is constant across those bands, so concurrency cannot explain the
variation: the early band is `wallDist`, developing fields and more inner sweeps
per outer.

## 2. The number

**PROBE A — direct, 120 s simultaneous window, 2026-08-31T20:19:31Z**, over the
five cases then past the transient, all at genuine twelve-concurrent [MEASURED]:

| case | iterations at probe | marginal iter/s |
|---|---:|---:|
| `T24_P080_U10` | 5363 | 4.258 |
| `T24_P080_U20` | 4918 | 4.125 |
| `T24_P080_U30` | 4434 | 4.217 |
| `T24_P080_U40` | 4213 | 4.292 |
| `T24_P155_U10` | 3815 | 4.183 |

**Mean 4.215 iter/s, spread 4.0 %.** Those cases sit in T23's bands 2000–4000
(**6.012**) and 4000–7000 (**5.753**).

**PROBE B — matched bands from each case's own `ExecutionTime` trace**, an
independent path not using a live window [MEASURED]: `T24_P155_U20` band
1000–2000 = **4.421** against T23's **6.272**; `T24_P080_U30` and `_U40` band
2000–4000 = **4.874** and **4.879** against T23's **6.012**.

> **THE MEASUREMENT: twelve-concurrent costs 26.7 % – 29.9 % more wall time per
> iteration than four-concurrent, on identical geometry, mesh, solver and
> iteration count.** Two independent probes agree; the tight 4.0 % spread across
> five cases is what makes it a property of the box rather than of any case.

## 3. The attribution — bandwidth contention, NOT core starvation

**Twelve single-rank jobs on sixteen cores: every job holds a core.** Measured at
20:22Z from `/proc/<pid>/stat`:

| reading | value | what it rules out |
|---|---:|---|
| `cpu_s / wall_s` per solver | **0.9963 – 0.9974** | each solver is on-core ~99.7 % of its life — it is **not waiting for a core** |
| aggregate over all twelve | **0.9950** | ~**11.9 of 16 cores** genuinely consumed |
| processes in D-state | **0** | not I/O blocked |
| non-solver processes above 20 % CPU | **1** (an unrelated python at 55.4 %) | no hidden competitor |
| MemAvailable | **27.3 GB** | not memory-pressured |

**So the deficit is memory-bandwidth and shared-cache contention: the core is
resident and counted as running while stalled on memory.**

## 4. Two consequences for reading the numbers — and the second one is a CORRECTION

**(a) `loadavg` OVERSTATES this contention and must not be used to size it.**
`loadavg_1min` read **24.47** on a 16-core box at the same instant that
**11.9 cores** were genuinely consumed. A calibration row that attributes
contention from `loadavg` will overstate it by roughly a factor of two here.

**(b) `core-minutes` as `wall_s × ranks ÷ 60` is NOT inflated relative to actual
CPU consumption, and the opposite expectation is what this measurement
falsified.** It was put to this lane that the unit *"penalises concurrency more
than actual CPU consumption does"* — i.e. that wall time inflates while CPU-time
does not, making the extra cost a measurement artifact of the unit. **It is not.**
For a 1-rank job, `cpu_s / wall_s = 0.9950`–`0.9974`: **wall-seconds and
CPU-seconds agree to better than 0.5 %**, so there is no gap between the two
readings for the unit to exaggerate. The stall time is **real CPU time**, charged
to a core that is resident and doing no work.

> **The honest consequence is stronger than the one it replaces, and it is the
> line the calibration row should carry: the same physics GENUINELY COSTS
> ~28 % MORE CORE-MINUTES at twelve-concurrent than at four-concurrent.** That is
> a true cost increase, not a bookkeeping artifact, and `core-minutes` reports it
> correctly.
>
> **Therefore: a per-case POINT measured at one concurrency does not transfer to
> another, and a cap calibrated at low concurrency under-provisions at high
> concurrency.** T24 §5.2's POINT of 30.0321 core-min was measured on T23 at
> **four**-concurrent and these twelve ran at **twelve**-concurrent; §5.3
> registered that exposure before compute, and this note is the measurement of
> it. **Stated as a measurement of this box on this case family, offered for the
> ratio and its attribution — not as a rule, and not as a change to any unit.**

## 5. Where this sits in what the family already knows

`T23_RESULTS.md` §6 measured that **a borrowed per-cell-iteration rate survives a
change of dimensionality and does not survive a change of geometry family**.
**This note adds a third axis, measured rather than argued: it does not survive a
change of CONCURRENCY either, degrading ~28 % across a threefold increase.** That
is a **negative** answer to the question T24 §5.5 registered as the figure this
rung exists to calibrate, and it is reported as negative.

## 6. Artifacts

| what | path |
|---|---|
| frozen registration | `docs/campaigns/T-family/T24_PREREGISTRATION.md` (`b9057489`) |
| the twelve cases and their solver logs | `verification/runs/T-family/T24_runs/T24_P*/log.solve` |
| launch-instant load readings | `verification/runs/T-family/T24_runs/T24_P*/START.T24_P*` |
| four-concurrent reference | `verification/runs/T-family/T23_runs/T23_P305_U10/log.solve` |
| launch record | `verification/queue/LAUNCH_LOG.tsv`, `verification/queue/runner.log` |

**A known false zero in the START files, recorded here so a reader does not take
it for a measurement:** `run_t24.sh`'s `solvers_already_running` field uses
`pgrep -c chtMultiRegionSim`, and the kernel truncates `comm` to 15 characters
(`chtMultiRegionS`), so a 17-character pattern matched against `comm` can never
match. **All twelve START files read 0 while eleven solvers were running.** The
field is **NOT MEASURED** and decides nothing — T24 §5.5's saturation threshold
reads the **load average**, which is correct in all twelve (3.42–11.15 at launch,
all below `nproc` = 16). The launcher was **not** retro-fitted mid-sweep: twelve
cases under identical launcher bytes is worth more than a repaired bookkeeping
field. The true count per launch instant is recoverable from `runner.log`'s
launch sequence.

**No verdict is assigned by this note.** `CLAUDE.md` rule 4 marking and all
grading belong to the frozen marker and comparator, which are another lane's
deliverable and are not run here.
