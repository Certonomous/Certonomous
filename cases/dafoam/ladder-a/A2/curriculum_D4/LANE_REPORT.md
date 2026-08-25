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

---

## 8. The 12 GiB floor WAS breached — and the cause was not this arm

**Disclosed, with the numbers, rather than reported as a clean run.**

At 18:19:19Z the floor watch fired: host `MemAvailable` **11.35 GiB**, against this family's
standing **12 GiB floor**. Minimum observed across the arm so far: **11.288 GiB**, i.e.
**0.71 GiB below the floor**.

**This lane's contribution was flat when the breach happened.** The container's own cgroup had
been pinned at `container_peak_gib 5.962` for roughly five minutes and did not move across the
breach — the same 5.962 before, during and after. The growth came from elsewhere, and the
discrimination was done by `ps -eo pid,rss,args`, never by `pgrep`:

| pid | RSS | what it is |
|---|---|---|
| 2230463 | **9.94 GiB** | peer **D8** CRM optimisation — stable, unchanged, **not touched** |
| 2359929–32 | 1.80–1.82 GiB ×4 | **this arm's four ranks** (`d4_opt_runScript.py -task run_driver`) |
| **2370843** | **1.12 GiB** | **a D9 lane — `runScript.py -task=run_driver -optimizer=SLSQP -maxit=1 -out=d9_out.json`** |
| 2203927 | 0.47 GiB | a `buoyantBoussinesqSimpleFoam` (cfd) |

**The D9 lane launched AFTER arm O.** It was not in the launcher's `siblings_pre` census
(`[d8_opt_20260825T165153Z_2230005]` only) and it is not in any census this arm took before
committing to its buy.

Note the cgroup/RSS discrepancy, so neither figure is misread: the four ranks sum to ~7.25 GiB
of RSS while the cgroup reports **5.962 GiB**. RSS double-counts pages shared between ranks;
the cgroup counts them once. **The cgroup figure is the correct one for a container footprint**
and is what the cap is enforced against.

### The finding, which is larger than this item

**A per-lane memory guard cannot enforce a family-wide floor when lanes launch
independently.** This lane sized its buy against a floor with 5.75 GiB of headroom, pinned its
own container to a 12 GiB cgroup cap, measured its own peak continuously, and stayed flat at
5.962 GiB — and the floor was breached anyway, by a peer that arrived afterwards. Every
individual guard held; the aggregate invariant did not. The launcher's sibling census is taken
**once, before the arm**, so it cannot see an arrival mid-arm, and nothing reconciles the sum
of concurrent caps against the floor.

**Recorded as a coordination gap for the family to rule on, not repaired here** — a floor is a
standard, and retiring or amending one is not a lane's call.

### Why this arm was not stopped, stated as a decision with its reasoning

* **OOM risk is nil, measured not assumed.** `MemAvailable` 11.43 GiB with **`Cached`
  10.18 GiB** — the page cache is reclaimable, so the kernel's own availability estimate is
  healthy and no OOM killer is near firing. `MemFree` 0.45 GiB alone would misread this badly.
* **The peer is safe.** D8 sits unchanged at 9.94 GiB. Stopping arm O protects nothing that is
  currently at risk.
* **This arm is bounded and flat**, at 49.7 % of its own registered cap, and a breach of that
  cap kills only this container — a registered G11 outcome, not a host event.
* **The breach is not this arm's to cure.** Killing arm O would surrender the completed
  `dRdW` coloring — the expensive one-time phase — while the two larger consumers continued.

**The floor breach is therefore DISCLOSED and CARRIED, not silently absorbed and not waved
through.** It is reported here with its minimum value, its duration and its attributed cause,
and the arm's own contribution is stated separately from the aggregate.

---

## 9. CORRECTION, dated 2026-08-25 ~18:24Z — this lane's own §6a claim was PREMATURE and is STRUCK

**Struck, from §6a:**

> ~~"the registered 12 GiB cap is roughly **5.7× oversized**, and even a doubling of the working
> set would leave the host near 13.8 GiB available"~~

**Why it was wrong.** That sentence was written at 18:16Z from a container peak of **2.114 GiB**
measured during the *primal and coloring* phases. It generalised a plateau to the whole arm
before the arm's memory-heaviest phase had run. **The adjoint solve had not started yet.**

**What the instrument now measures**, once `run_driver` entered the adjoint
(`Solving Linear Equation…`, `Driver total derivatives for iteration: 3`):

| quantity | value |
|---|---|
| **container peak** | **10.308 GiB** |
| container current, steady | 9.72 GiB |
| registered cap | 12 GiB |
| **headroom to the cap** | **1.692 GiB** |
| **fraction of cap used** | **85.9 %** |

**The registered 12 GiB cap is therefore roughly 1.16× the measured peak, not 5.7×.** The cap
was well chosen and is very nearly binding. The correct reading of §8's arm-P2 memory-envelope
registration is the opposite of what this lane wrote at 18:16Z: the envelope is **tight**, and
`OOMKilled false` on P2 was a **meaningful** pass rather than a formality.

**The lesson this lane hands over, against itself.** A memory plateau observed during one
phase of a multi-phase solve is not the arm's peak, and calling a cap "oversized" from it is
the same error class as reading a converged tail as a converged run. **The claim should have
been withheld until the adjoint had allocated**, and the honest statement at 18:16Z was the
narrow one this lane did also make — that the floor was not breached *at that moment* — not
the extrapolation attached to it. The decision that rested on the early number (launch rather
than queue) is **unaffected and remains correct**: the host had 15.9 GiB available then and has
16.0 GiB now, and the arm has never approached a host-level constraint. It is the *sizing
claim about the cap* that was wrong, and it is struck here rather than quietly edited.

§6a's **measurements** stand as recorded — they were correctly labelled as the values observed
at that time. It is the **inference** drawn from them that is withdrawn.

---

## 10. Supervisor rulings adopted into this record (2026-08-25, dafoam-supervisor)

**On the floor breach — DISCLOSED AND ESCALATED, and explicitly NOT softened to a near-miss.**
The supervisor adopted §8's structural finding verbatim and ruled: the breach is **disclosed,
not waived** (0.712 GiB below floor, transient, no OOM, no run harmed, **no verdict adjusted
on account of it**); this lane does **not** repair it and does **not** add a cross-lane lock
mid-item; enforcement moves to the supervisor, who sequences launches against projected peaks;
and the general form is **escalated to the chief**, because every team on this box launches
lanes independently against one shared ~30 GiB, making this a **lab-wide guard-architecture
gap rather than a dafoam defect**. Recorded as instructed: **the invariant broke, and that it
broke harmlessly this time is luck, not design.**

**On the §9 self-correction.** The struck claim stays visible in this record with its
correction beside it, never silently deleted — a pre-repair value published beside the
post-repair one. **This applies to a lane's own inferences, not only to case values.**

**On §2's instrument gap.** Recorded, as instructed, as a textbook **L-302** instance:
**an instrument named for a quantity it cannot see.** P2 is registered as the memory-envelope
check and its frozen sampler carries no memory channel; the peak is `NOT_MEASURED` and
unrecoverable for P1 and P2. §9's measurement makes the severity concrete — the envelope was
at **85.9 % of cap with 1.692 GiB of headroom**, so it was **tight**, and the gap hid a real
margin rather than an academic one.

**On arm F — AUTHORISED, and not optional.** It needs no new registration: the frozen prereg
§8 already registers it at **cap 120.0 core-min**, memory 12g, prediction 53.0. **Bands D and
E stay `PENDING` and D4 is NOT reported complete until arm F lands.**

---

## 11. FINDING — the frozen launcher CANNOT RUN ARM F as written

Discovered while preparing arm F, **before spending anything on it**.

The launcher derives its work directory as one line, `d4_run_arm.sh:136`:

```
WORK="$BASE/$ARM"
```

so for `ARM=F` this resolves to `$BASE/F`. The arm-F branch then requires that directory to
already exist, carrying arm O's history:

```
test -d "$WORK" || { echo "ABORT arm F expects an existing $WORK from arm O"; exit 5; }
test -f "$WORK/OptView.hst" || { echo "ABORT arm F: no OptView.hst to read an endpoint from"; exit 5; }
```

**But arm O's work directory is `$BASE/O`, not `$BASE/F`** — arm O was staged into `$BASE/O`
by the same `WORK="$BASE/$ARM"` line. Verified on disk: `$BASE/O` exists; **`$BASE/F` does not
and never will be created by any arm.** Run as written, arm F aborts with **exit 5** having
computed nothing.

The comment on that very line — *"arm F expects an existing `$WORK` from arm O"* — shows the
author's intent was for arm F to operate on **arm O's tree**. The naming convention
`WORK=$BASE/$ARM` silently defeats that intent. It is a latent defect that could only surface
when arm F was first attempted, which is now.

### How it is handled — WITHOUT touching a frozen file

`d4_run_arm.sh` is frozen at md5 `399957c616215c8f1ae078abe2e97958` in prereg §9a. **It is not
edited** (rule 6; editing it would break the freeze and invalidate the §9a hash the launcher's
own record rests on).

**The remedy is to satisfy the launcher's stated precondition rather than change it:** stage
`$BASE/F` as a copy of the **completed** `$BASE/O` tree, then invoke the frozen launcher
unmodified. This alters **no gate, threshold, cap or label** — arm F still runs its registered
command, under its registered 120.0 core-min cap and 12g memory cap, on the endpoint arm O
actually produced.

It also has a property worth stating because the grader depends on it: `d4_grade.py` takes a
**single** `--work`, and reads `opt_IPOPT.txt`, `d4_major_history.json` **and**
`d4_fd_endpoint.json` from it. Staging `F` as a copy of `O` puts all three in one directory,
so the grader reads a coherent set rather than being pointed at two trees it cannot reconcile.

**Arm O's own tree is NOT moved, renamed or deleted** — it is copied. The original remains as
the evidence of arm O.

*Recorded as a defect in a frozen instrument, disclosed here as a dated departure that changes
no gate. Whether the launcher is amended for future items is not a lane's call.*

---

# 2026-08-25 19:05Z — CUSTODY LANE (successor after a session-limit kill)

**The previous D4 lane was killed by a session usage limit. THE RUN WAS NOT KILLED.** This
section is written by the successor custody lane. Its first act was a reading, not a launch.

## 1. Custody reading — arm O is LIVE and was never interrupted

Established from disk and from the process table at **19:04:33Z**, without touching the run:

| item | value | artifact |
|---|---|---|
| launcher pid | `2359354`, `bash d4_run_arm.sh O dafoam-idwarp-rot:v1`, elapsed `3129 s` | process table |
| MPI ranks | pids `2359929/30/31/32`, each `~99.5 %` CPU, RSS `~2.93 GB` each | process table |
| launch epoch | `18:12:37Z` under `timeout 9300` | `O_20260825T181237Z_2359354.log` name + ledger |
| **hard cap-stop time** | **`20:47:37Z`** = 18:12:37Z + 9300 s | derived from the enforced timeout |
| delivered cores, latest sample | `3.9717` of the 4-core quota (`nr_throttled` 8792) | `O_20260825T181237Z_2359354.cpu.jsonl` |
| container peak memory | `10.308 GiB` against the `12g` cap | `O_mem.jsonl` |

**NOTHING WAS RELAUNCHED, KILLED, OR DUPLICATED.** No second arm O exists. The frozen
launcher's guard (a run directory that already exists is refused) was **not** routed around,
and no parallel tree was created. A run interrupted by a fleet kill would not be a completed
run — but this run was never interrupted; only its watcher died (`agent watchers die with the
agent`: the correct response is to reattach, not to restart).

## 2. Optimiser state, PARSED FROM FILES (never from stdout)

Prereg §9 registers that MPI log splicing is **measured on this exact case** (commit
`79679a84`), so every number below is read from a file a single writer owns.

From `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` — IPOPT's
own output file — at 19:04Z:

| quantity | value |
|---|---|
| iteration rows present | **29** (iters `0`–`28`), i.e. **28 majors completed** past the baseline |
| baseline objective, iter 0 | `CD = 2.9619634e-02` at `inf_pr = 4.16e-08` |
| latest objective, iter 28 | `CD = 2.1490696e-02` at `inf_pr = 7.11e-04`, `inf_du = 3.82e-04` |
| drag reduction so far | `(2.9619634e-02 − 2.1490696e-02) / 2.9619634e-02` = **27.44 %** |
| `EXIT` line | **ABSENT** — `grep -a EXIT` returns nothing. The optimiser has NOT terminated |

Cross-check from the live log's last completed adjoint block: the driver reports
`CD = 0.0214907` and `CL = 0.49928921` with `volcon = 1.00261444`, consistent with iter 28.

**27.44 % sits inside frozen band C `[25 %, 45 %]`** — but band C is graded at the ENDPOINT by
the frozen grader, not here, and a mid-run reading is not a verdict.

**Band A is NOT gradeable from `inf_pr`.** `inf_pr` is the maximum violation over *all*
nonlinear constraints — `thickcon` (100 rows), `volcon` and `CL` together — so the `6.19e-03`
peak at iter 11 says nothing about `|CL − 0.5|` on its own. Band A and band B are graded from
`d4_major_history.json`, extracted from `OptView.hst` by the frozen extractor, exactly as
prereg §7 G2 registers. No feasibility claim is made in this section.

## 3. Instrument verification — DONE BEFORE ANY GRADING

Every frozen instrument was hashed against the **committed blob** at `HEAD` and against the
md5 registered in prereg §9a. All five agree, and the staged copies in the run root agree too:

| file | md5 | vs `git show HEAD:` | vs prereg §9a |
|---|---|---|---|
| `d4_grade.py` | `f162ef69a7385e5d0586ef5f27657cbb` | MATCH | MATCH |
| `d4_fd_endpoint.py` | `c6112b0ec3bfdb5287345e350500f64a` | MATCH | MATCH |
| `d4_extract_endpoint.py` | `ee7d3c99fd716da23779cb651961918e` | MATCH | MATCH |
| `d4_opt_runScript.py` | `2906d52a5dbed2bacbaeaf85a37d3fe8` | MATCH | MATCH |
| `d4_run_arm.sh` | `399957c616215c8f1ae078abe2e97958` | MATCH | MATCH |

The frozen file **is** the file that ran (prereg §9a's closing requirement).

## 4. Termination is a verdict — registered here BEFORE it happens

Prereg §7 gate **G3** and `DAFOAM_CHARTER.md` §9 are restated so no later reading can soften
them:

* An `EXIT: Optimal Solution Found.` line in `opt_IPOPT.txt` is the ONLY route to `PASS`.
* A **cap-stop** — wall clock at `20:47:37Z`, or `max_iter 100`, or budget — is
  **`GATE REACHED`** if bands C and A both hold, else **`NOT A RESULT`**. It is **NEVER
  `PASS`**, whatever the drag number says.
* An adjoint `-9`-class exit is **`BLOCKED`**, recorded, not skipped.
* `OOMKilled true` → **`NOT A RESULT` about convergence** (G11), recorded as stopped by memory.

**Projection, stated as a projection and not as a measurement.** 28 majors in 3129 s is
`~112 s/major`; the driver's own total-derivative counter stood at `30` at `3086 s`. At that
rate the 9300 s timeout lands near **major 83**, short of `max_iter 100`. **Prediction P1
(`EXIT` within 100 majors) is therefore at risk of being a MISS by wall clock rather than by
optimiser behaviour** — and if the timeout fires first, that is a CAP-STOP and the ceiling
verdict available to this item is `GATE REACHED`. This is written down now, before the fact,
so it cannot be presented afterwards as an expectation that was met.

## 5. Cost so far

Arm O, in flight: `3129 s × 4 ranks ÷ 60` = **208.6 core-min** of its registered **620.0**
cap. Completed arms from `ledger.txt`: P1 `0.333`, P2 `36.4` core-min. Item total spent to
this reading: **245.3 core-min** of the **800.0** ceiling.
`cost_basis: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED` — dollars are
**DERIVED**: 245.3 core-min = **$0.210 derived, not measured**.

**Status at this commit: PENDING** — arm O is still running. No verdict is claimed.
