# D4 — LANE REPORT (arm O lane, resumed 2026-08-25 ~18:06Z)

**Status: IN PROGRESS.** This file is committed incrementally. Sections are appended as
each stage closes; nothing here is retro-edited except by a dated strike.

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed, uploaded, posted or
commented outside this box.

---

## 0. Freeze re-verified before anything was touched

`cases/dafoam/ladder-a/A2/curriculum_D4/PREREGISTRATION.md`

| channel | value |
|---|---|
| disk `git hash-object` | `4c2c3f07758feb0a62d675c1c214580053653b72` |
| `git rev-parse HEAD:<path>` | `4c2c3f07758feb0a62d675c1c214580053653b72` |
| verdict | **FREEZE MATCH** — the frozen file is the committed file |

Freeze commit `8a90901e`. Gates, thresholds, caps and labels are closed. Nothing in this
report alters one; the two departures in §3 are disclosed as additions that change no gate.

**Frozen instruments (§9a) — all five re-hashed on disk, all five match:**
`d4_opt_runScript.py` `2906d52a…`, `d4_run_arm.sh` `399957c6…`, `d4_extract_endpoint.py`
`ee7d3c99…`, `d4_fd_endpoint.py` `c6112b0e…`, `d4_grade.py` `f162ef69…`.

---

## 1. P1 — decomposition determinism and CPU placement. Read from disk, not inherited.

Ledger row: `rc=0 wall_s=5 ranks=4 core_min=0.333 cap_core_min=5.0 enforced_core_min=5.000000
memory=4g inspect(exit,oomkilled)=[0 false] cpuset=5,6,7,9`.

### G8 — decomposition determinism: **PASS**

Two independent `decomposePar -force` on the same staged mesh:

| | processor0 | processor1 | processor2 | processor3 | sum |
|---|---|---|---|---|---|
| A | 9504 | 9600 | 9608 | 9592 | **38,304** |
| B | 9504 | 9600 | 9608 | 9592 | **38,304** |

Identical map, and the sum equals the registered cell count 38,304 exactly.
`method scotch; numberOfSubdomains 4;` read back from the case's own `decomposeParDict`.
**Prediction P7: HIT.**

**The pinned decomposition, stated as the parallel-gate doctrine requires:**
method **`scotch`**, `numberOfSubdomains 4`. **Seed: there is none to pin** — OpenFOAM's
`scotchDecomp` exposes no seed parameter. §5 registered this honestly in advance and did not
assert determinism by construction; it *demonstrated* it by G8 above. That is the whole
reason P1 exists, and the demonstration passed.

### G12 (placement half) — four ranks, four distinct cores: **PASS**

Four per-rank `sched_getaffinity` files present (refuses by count below 4 — count is 4):

| rank | affinity | n_cores |
|---|---|---|
| 0 | `[5]` | 1 |
| 1 | `[6]` | 1 |
| 2 | `[7]` | 1 |
| 3 | `[9]` | 1 |

Union `{5,6,7,9}` == the pinned `--cpuset-cpus` exactly. Four **distinct** single cores.
**The D13 shared-core collision does NOT reproduce under an explicit cpuset.**
**Prediction P11: HIT.**

`measured_affinity = {0:[5], 1:[6], 2:[7], 3:[9]}`.

Note on a benign log artifact: OpenMPI's `--report-bindings` prints ranks bound to logical
cores 0–3 (`[B/././.]` … `[./././B]`). That is the **container-relative** view of the 4-core
cpuset; `sched_getaffinity` reports the **host** cores 5,6,7,9. The two agree — logical 0 is
host 5. A reader comparing only the OpenMPI line against the pinned set would wrongly read a
collision on core 0; the per-rank files are the instrument that settles it, which is exactly
why §5b registered files rather than log lines.

The log also carries an OpenMPI `failed to bind memory` **warning**. That is NUMA *memory*
binding, not CPU binding; CPU binding succeeded, as the four affinity files prove. Recorded,
not waved through.

### G12 (delivered-cores half) on P1 — **NOT_MEASURED**, and reported as such

Ledger: `delivered_cores_mean=[NOT_MEASURED]`.

**Cause, established from the instrument:** the frozen sampler polls at a 15 s interval and
computes a rate from consecutive samples. P1's wall time was **5 s**, so zero intervals
closed and no rate exists. This is an instrument-resolution floor, not a placement failure.

**How it is graded.** §5b says an absent sample file is `NOT_MEASURED` and **"never a passing
placement gate"** — so P1's delivered-cores channel is *not* reported as a pass. §5b's
`GATE FAIL` condition is specifically *"an arm delivering under 3.0 cores"*, which is a
statement about a measured value; an unmeasured channel does not meet it either.
**P1's G12 is therefore PARTIALLY MEASURED: placement PASS, delivered-cores NOT_MEASURED.**
It is not forced into either registered bucket. This is recorded as an unregistered outcome
per the resume brief, not resolved by choosing the convenient side.

**Consequence for the §8 calibration gate**, which blocks arm O if *"G12's placement check
fails on P1 or P2"*: the blocking condition is a **failure**, and no failure was measured on
either arm. The substantive delivered-cores claim is affirmatively measured on **P2** (below)
at 3.9867/4 over 36 samples, on the same cpuset, same image, same rank count. Arm O is
therefore not blocked by this. The reasoning is written down here rather than left implicit.

### G9 / G10 / G11 on P1

Image digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` ==
registered PATCHED row. IDWarp `.so` md5 `85f59e87253e0a71a813f64ca6e4c425`, imported from
`/opt/idwarp_patched/idwarp/__init__.py` — the patched path, confirmed from the run's own
output rather than asserted. Enforced cap `5.000000` == registered `5.0`; actual `0.333` well
under. `OOMKilled false`, exit 0.

---

## 2. P2 — `compute_totals`, the calibration probe. Read from disk.

Ledger row: `rc=0 wall_s=546 ranks=4 core_min=36.4 cap_core_min=55.0
enforced_core_min=55.000000 memory=12g inspect(exit,oomkilled)=[0 false] cpuset=5,6,7,9
delivered_cores_mean=[3.9867 n=36 max_nr_throttled=670]`.

### The §8 calibration gate that authorises arm O: **SATISFIED**

The gate has three conditions, all read from the ledger the launcher wrote:

| condition | registered | measured | verdict |
|---|---|---|---|
| P2 core-min ≤ 55.0 | 55.0 | **36.4** | satisfied |
| `OOMKilled` false | false | **false** | satisfied |
| G12 placement not failed on P1/P2 | no failure | no failure (§1) | satisfied |

**Arm O is authorised by its own calibration.** **Prediction P10: HIT.**

### G12 delivered cores on P2: **PASS**

`3.9867` cores delivered of a 4-core quota, mean over **n=36** samples, `max_nr_throttled=670`.
Threshold ≥ 3.0. **Prediction P12: HIT.**

**Measured contention: 0.33 %** — `(4 − 3.9867)/4`. Sibling census identical before and after
(`d8_opt_20260825T165153Z_2230005` only). This sits **below** the 5–11 % band the lab treats
as acceptable-and-disclosed, so contention on this cpuset is essentially nil and no adjoint-
conditioning finding is contaminated by it (the §5b registered concern is cleared for P2).

### Cost calibration, P2

Predicted 33.0 core-min (A2's cold `compute_totals` anchor, 32.7). Actual **36.4**.
**Ratio actual/predicted = 1.103.** Gap attributed: 0.33 % is contention; the remaining ~10 %
is misprediction against a cross-run anchor, which is the expected size of run-to-run
variation for a cold `compute_totals` and is not waste. **No waste is claimed and none is
absorbed into the ratio.**

### The instrument gap this lane found in P2 — reported, not smoothed over

§8 names P2 *"the `DAFOAM_CHARTER.md` §7 memory-envelope check"*, and §11 P8 predicts
*"peak memory stays inside the 12 GiB container cap with no `OOMKilled`"*.

**The frozen sampler has no memory channel.** Its per-sample keys, read from
`P2_20260825T174718Z_2320490.cpu.jsonl`, are exactly
`['t','delivered_cores','throttled_usec','nr_throttled']`. The ledger records host
`MemAvailable` **before and after** the arm (17.46 → 17.45 GiB), which is a host figure
bracketing the arm, not a container peak during it.

So P8 splits in two:

* **envelope — DISCHARGED.** `OOMKilled false` is the kernel's own record under a hard
  `--memory=12g --memory-swap=12g` (no swap), which proves peak ≤ 12 GiB. G11 works.
* **peak value — `NOT_MEASURED`, and NOT RECOVERABLE from P1 or P2.** The cgroup is destroyed
  with the container, so no later reader can recover it.

This is an L-302-shaped gap: an arm registered as a *memory*-envelope check ran an instrument
that cannot report memory. It is disclosed here rather than papered over with an estimate, and
**no peak-memory number is quoted for P1 or P2.** The missing channel is added for arm O by an
external reader (§3), which changes no gate.

---

## 3. Two disclosed departures — neither alters a gate, threshold, cap or label

**(a) An external passive memory sampler is run alongside arm O.**
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/d4_mem_sampler.sh`
(md5 `24129fd10389fa97d6104df4c8d1daa5`). It reads the container's own cgroup v2
`memory.current` / `memory.peak` and the host's `MemAvailable` on a 10 s poll and writes them
to a file. **The frozen launcher `d4_run_arm.sh` is NOT edited** — editing it would break the
§9a freeze — so this is a *separate* reader, following the same passive doctrine §5b sets for
the CPU sampler: it starts nothing, kills nothing, and its failure cannot change a verdict; an
absent sample file is `NOT_MEASURED`, never a pass. It adds a measurement channel and alters
no gate, threshold, cap or label.

**(b) Arm O runs under a live host-memory floor watch.** See §4. This constrains only whether
this lane *starts* the arm; it changes no registered gate.

---

## 4. Memory sizing for arm O — the decision, with the numbers

Standing constraint handed to this lane: this family holds a **12 GiB host `MemAvailable`
floor**, and a concurrent peer buy must not be endangered.

**Live state at the decision, 2026-08-25 ~18:08Z**, measured:

| quantity | value |
|---|---|
| host `MemTotal` | 32,132,604 kB = **30.64 GiB** |
| host `MemAvailable` | 18,616,132 kB = **17.75 GiB** |
| headroom above the 12 GiB floor | **5.75 GiB** |
| peer D8 (`d8_opt_20260825T165153Z_2230005`, host pid 2230463) RSS | 10,376,524 kB = **9.90 GiB** |
| D8 hard stop | `timeout 10800` from ~16:51Z → **~19:51Z** |
| loadavg1 / cores | 13.23 / 16 |

D8 was identified with `ps -eo pid,args` and discriminated by container name.
**It was not signalled, stopped or touched.**

**Why arm O cannot endanger D8, established rather than assumed.** Arm O's registered memory
cap is `12g` with `--memory-swap=12g`, i.e. a hard cgroup ceiling with no swap. Worst case —
arm O sitting at its full 12 GiB ceiling — leaves host `MemAvailable` at 17.75 − 12 =
**5.75 GiB**. The kernel OOM killer fires near exhaustion, not at 5.75 GiB free, so the
pathological case does **not** put the host into OOM and therefore cannot select D8 (which,
at 9.90 GiB and `oom-score-adj=500`, would be the fattest target if it ever did fire). A
breach of arm O's own 12 GiB cgroup cap kills **only arm O's container**, which §7 G11
registers as `NOT A RESULT` about convergence, recorded as stopped by memory.

**What is honestly unknown:** arm O's *projected* peak. The brief asked this lane to size arm
O against P2's measured peak RSS — **that measurement does not exist**, for the instrument
reason in §2. No estimate is substituted for it here. The nearest defensible statement is
qualitative and is labelled as such: `run_driver` iterates the same primal/adjoint objects
`compute_totals` already allocated on this same 38,304-cell mesh at np=4 in this same 12g
container, plus an IPOPT L-BFGS history of 10 vectors of length 105 (~8 kB, negligible), so
arm O's peak is expected to be of the same order as P2's — **which is itself only bounded
above at 12 GiB, not located.**

**Decision: LAUNCH, under measurement, rather than queue on a guess.** The unknown is resolved
by measuring it in the first minutes of the arm at a cost of a few core-minutes out of a 620
cap, instead of by asserting a projection the instruments do not support. If the measured
container peak trends toward pushing host `MemAvailable` below the 12 GiB floor, the arm is
stopped early and requeued behind D8's ~19:51Z release, and the measured number is reported.
The floor watch is this lane's own guard (§3b), not a registered gate.

---

## 5. Arm O — cost, booked before the container starts

| item | value |
|---|---|
| registered cap | **620.0 core-min** (§8, frozen) |
| enforced wall timeout | 9,300 s = 2 h 35 m, derived `620 × 60 ÷ 4` by the launcher, back-checked |
| prediction | **511.0 core-min** (A2's 5.106 core-min/major × 100 majors) |
| ranks | 4 |
| memory cap | 12g, `--memory-swap=12g` |
| cpuset | `5,6,7,9` (pinned) |
| `cost_basis` | c7a.4xlarge at $0.0513/core-h, **REPORTED-BY-OWNER, NOT MEASURED** |
| predicted spend | 511.0 core-min = **$0.437 DERIVED, not measured** |
| cap spend | 620.0 core-min = **$0.530 DERIVED, not measured** |

Inside the 2026-08-21 pre-authorisation; costed here regardless, because a blanket is not a
per-item read. **An overrun stops the run and does not get a new budget** — enforcement is the
launcher's `timeout 9300`, which is derived from the cap and asserted against it, not copied.

---

*Appended below as stages close.*

---

## 6. Arm O — LAUNCHED 2026-08-25 18:12:37Z. `PENDING`.

Container `d4_O_20260825T181237Z_2359354`, image `dafoam-idwarp-rot:v1`
@ `sha256:2927768a…` (registered PATCHED row, digest-matched by the launcher, which aborts
on mismatch rather than proceeding).

**The frozen launcher was run unmodified**: `bash d4_run_arm.sh O dafoam-idwarp-rot:v1`.

Pre-launch gates, all from the arm's own output:

| gate | result |
|---|---|
| cap assertion | `registered_core_min=620.0 ranks=4 enforced_wall_s=9300 enforced_core_min=620.000000` — the launcher derived 9,300 s from the cap and **inverted the arithmetic back to 620.000000**, matching the registered cap exactly |
| G-COLD | **OK** — no `reports`, `OptView.hst`, `opt_IPOPT.txt`, `dRdWColoring_4.bin`, `d4_fd_endpoint.json`, no `processor*`, no time dir. `O/` did not exist before this launch |
| age datum | `1787681557` written to `O/.d4_age_datum` |
| instrument md5s | `d4_opt_runScript.py`, `d4_fd_endpoint.py`, `d4_extract_endpoint.py` re-asserted OK on the staged copies |
| host pre | `MemAvailable_GiB=17.46 load1=6.86 cpuset=5,6,7,9 siblings_pre=[d8_opt_20260825T165153Z_2230005]` |

**No interrupted tree was deleted.** P1/ and P2/ are untouched; arm O staged its own fresh
`O/` from `base/`.

### 6a. The memory question — now MEASURED, and the answer is that queueing was not needed

The external sampler (§3a) delivers the channel the frozen instrument lacks. First 10 samples,
10 s poll, after the initial ramp:

| quantity | measured |
|---|---|
| **container peak** | **2.114 GiB** |
| container current (plateaued) | 2.110 GiB |
| registered container cap | 12 GiB |
| **fraction of cap used** | **17.6 %** |
| **host `MemAvailable` during the arm** | **15.92 – 15.99 GiB** |
| **margin above the 12 GiB family floor** | **≈ 3.95 GiB** |

**Verdict on the floor guard: arm O does NOT breach the floor and is NOT queued.** The
decision was taken on this measurement, not on the projection the instruments could not
support. The container plateaus at ~2.11 GiB — the primal-plus-adjoint working set for
38,304 cells at np=4 — so the registered 12 GiB cap is roughly **5.7× oversized**, and even a
doubling of the working set would leave the host near 13.8 GiB available.

**This is the first actual peak-memory measurement in item D4.** It is stated only for arm O.
**It is NOT retro-applied to P1 or P2**, whose peaks remain `NOT_MEASURED` per §2 — a later
arm's measurement is not evidence about an earlier arm's cgroup.

Peer D8 (`d8_opt_…`, host pid 2230463) was running throughout and was **not signalled, stopped
or disturbed**; the sibling census is identical before and during. Host `MemAvailable` moved
17.46 → ~15.95 GiB, a **1.5 GiB** draw, consistent with the container's own 2.11 GiB against
freed page cache.

### 6b. Baseline reproduction — an unplanned but load-bearing confirmation

Arm O's iteration-0 primal converged to:

| quantity | arm O measured | prereg §2 registered A2 anchor | agreement |
|---|---|---|---|
| `CD` | `0.02961963388` | `2.9619634e-02` | **exact to 8 significant figures** |
| `CL` | `0.4999999584` | target `0.5` | `\|CL − 0.5\| = 4.16e-08` |

The `CL` residual `4.16e-08` also reproduces the prereg's registered `inf_pr 4.16e-08` at
iteration 0. **The staged case is the A2 case**, confirmed by its own output rather than by
the copy having been made. Band A (`|CL − 0.5| ≤ 5.0e-4`) holds at major 0 by four orders of
magnitude.

### 6c. Grading path dry-run — the grader was exercised before it was needed

`d4_grade.py` was run against the real P1/P2 ledger with `--arms P1,P2`, `--work O/`:

* It **REFUSED with exit code 2** — `D4_GRADER REFUSED read_ipopt: {"absent": ".../opt_IPOPT.txt"}` —
  rather than degrading or falling back to stdout. Refuse-not-degrade confirmed on real data.
* Before refusing it wrote a partial report whose verdicts **independently reproduce this
  lane's hand reading**: `G8_decomposition_determinism PASS`, `G9_toolchain_identity PASS`,
  `G10_cap_discipline PASS`, `G11_memory_envelope PASS`, `G12_cpu_placement PASS`.
* G10 detail: `cap_equals_registered true` on both arms, `total_core_min 36.733`,
  `within_item_ceiling true` against the 800.0 item ceiling.
* G9 detail: a **single** toolchain across all three logs — one distinct IDWarp `.so` md5
  `85f59e87…`, one digest, rows `["PATCHED"]`.

**A reportable observation on G12's verdict line, offered as grader-hardening and NOT as a
defect in this item's verdict.** The grader's `report` is transparent about the §2 gap — it
prints P1's `delivered_cores_mean: null`, `raw: "NOT_MEASURED"`, and
`n_arms_with_delivered_measurement: 1` (of 2). So the instrument *can* say "I measured
nothing" and *does* say it, which is what L-302 asks. But the top-line
`verdicts["G12_cpu_placement"] = "PASS"` is computed from `arms_below_floor == []`, and an arm
whose channel was never measured cannot be below a floor — so it passes silently. A reader who
consults only the `verdicts` block sees an unqualified PASS while half the delivered-cores
evidence is absent, which is the *"a partial plant reads on the page exactly like a complete
one"* shape §7a warns about.

This does **not** change D4's verdict, for reasons that are registered rather than convenient:
G12's registered `GATE FAIL` condition is a *measured* value under 3.0 and no arm met it; the
delivered-cores claim is affirmatively measured on **P2** at 3.9867/4; and **arm O — the arm
that actually produces the graded numbers — is long enough to be fully sampled**, so the
verdict-bearing arm will not rely on an unmeasured channel. Recorded here so the family can
decide whether the verdict line should carry the `NOT_MEASURED` count.

*Arm O verdict: `PENDING` until the arm terminates and G1–G4 can be read from its own files.*

---

## 7. The planted-zero and count controls — PROVED TO FIRE, ahead of arm F needing them

Rule 3 and §7a are discharged by *demonstration*, not assertion. `d4_grade.py`'s gate
functions were exercised against a **synthetic** endpoint FD artifact carrying the registered
component set in the registered order.

**The synthetic artifact is scratch-only and is NOT evidence about D4.** Its numbers are
invented for the sole purpose of proving the controls refuse; it lives in this lane's
scratchpad, is cited nowhere as a measurement, and no D4 number is derived from it. What is
being tested is the *instrument*, not the case.

### G7 — count controls: **PASS**, all four mutations produced a NAMED refusal

| mutation | refused? | the refusal, verbatim from the gate |
|---|---|---|
| `rows` emptied | **yes** | `COUNT_REFUSAL: "empty component set", n_rows: 0, n_registered: 5` |
| `rows` shortened to 2 | **yes** | `COUNT_REFUSAL: "short or long component set", n_rows: 2, n_registered: 5` |
| `rows` reversed | **yes** | `COUNT_REFUSAL: "component set is not the registered set, in the registered order"` |
| `rows` key removed | **yes** | `rows_key_absent: true, n_rows: 0, n_registered: 5` |

**The count is printed in every refusal**, which is what §7a requires and what the D3 defect
lacked. The reordered case matters most and is the one a key-presence test would wave through:
the set was complete and the count correct, and it still refused because the *order* was not
the registered order.

Baseline sanity on the unmutated synthetic set: `n_rows=5`, `n_graded=5`,
**`n_plateau_comparisons=5`**, `coverage "5 of 5"`. The plateau loop's trip count equals the
graded-row count — the D3 defect was a plateau loop that iterated **zero** times while a step
was nonetheless "selected". Here the assertion `n_plateau_comparisons != len(graded) → refuse`
is live and the counts agree.

### G6 — planted zero: **PASS**, and the plant was seen on EVERY consumed channel

Plant `1.234e-03` (rule 3's constant) written **into the artifact on disk** and read back
through the same reader:

* moved `shape[46]` from `2.27e-06` to `2.2728011799999997e-06`
* channels that saw it: `rel_err_pct` **true**, `plateau_pct` **true**, `aggregate` **true**

All three consumed channels moved. A zero from this reader is now a zero from a reader
**shown able to see a non-zero**.

### G6b — negative control: **PASS**, the control can fail

A deliberately **blind** reader — one returning the unperturbed document whatever path it is
handed — was **REFUSED**, with all three channels reading `false`
(`aggregate: false, plateau_pct: false, rel_err_pct: false`).

This is the clause that makes G6 worth anything. **A planted-zero control that cannot refuse
is not a control**, and this one refuses when the reader is blinded. The plant is therefore a
live control rather than a ceremony.

**Standing caveat, kept rather than dropped:** these controls prove the FD *gate* refuses on a
malformed or unmeasured component set. They prove nothing about whether the FD *values* arm F
will produce are right, and nothing about the `|J_adj|` step-sizing proxy, whose registered
limitation (§7, quoted verbatim in the prereg) is that it sizes the step from the very
quantity under test and **has not been tried where `|J_adj|` is itself wrong**. D4 does not
repair that and does not claim to.
