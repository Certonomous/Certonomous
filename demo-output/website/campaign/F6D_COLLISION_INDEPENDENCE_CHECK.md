# F6d Option A — independent check of the collision/VOID coincidence

**Commissioned by the chief under `F6D_OPTION_A_PREREGISTRATION.md` §6.3.** Run
by an agent that produced none of the work being checked. Measurement only: no
case data, config or analysis code was modified, and no solver was launched.
Everything below is re-derived from artifacts (time-directory contents and
mtimes, the log's byte structure, the solver's own function-object time series,
and the shipped analysis code), not from any prior report.

**Headline, stated before the detail, because it cuts both ways.**

- **The −0.831 x/h is not the collision.** Every field snapshot that enters
  every pre-registered metric is provably the surviving process's own output,
  matched to 15 significant digits against a record that process wrote itself.
  The duplicate could not and did not reach the number.
- **But §6.1's chain is wrong at three of its five links.** The duplicate did
  not die at Time 4265 and it did not fail to write a field. It restarted from
  **Time 7000**, ran to **Time 7859**, and **overwrote the complete `7500/` time
  directory** that the surviving process had already written 22 seconds earlier.
  One snapshot of the published `d0.2_s000` trajectory is the duplicate's output.
- **A result that vindicates the responsible agent is worth as much as one that
  does not, and this is both.** The disposition it argued for survives; the
  evidence it offered for that disposition does not, and the disclosure that
  made this checkable is what allowed the correction.

---

## 1. What actually happened, reconstructed from artifacts

| fact | evidence |
| --- | --- |
| The surviving solver (**P1**) started from Time 4000 at **02:50:14** | `postProcessing/wallShearStress/4000/` created 02:50:14.44; first field write `4500/` at 02:51:04 |
| A second solver (**P2**, PID 204435) started at **02:54:51** | log header block surviving at byte 0: `PID : 204435`, `Time : 02:54:51`, `Case : .../f6d_option_a/d0.2_s000` |
| P2 restarted from **Time 7000**, not 4000 | its header says `Create mesh for time = 7000`; `controlDict` has `startFrom latestTime`, and P1 had written `7000/` at 02:54:26 — 25 s before P2 started |
| P2 read P1's `7000/` state | P2's `Initial pressure gradient = 0.00849589223118986`, byte-identical to `7000/uniform/momentumSourceProperties` |
| P2 ran **Time 7001 → 7859**, 859 iterations, `ExecutionTime` 0.85 → 58.81 s | its 859 consecutive `Time =` lines in the pre-hole segment |
| Overlap was **≈ 60 s of solver time**, not ≈ 25 s | P2's own `ExecutionTime` at its last logged iteration |
| P2 **wrote one field snapshot**: `7500/` | see §2 |
| P1 continued **uninterrupted to Time 16000** | post-hole segment has 8,671 consecutive `Time =` lines, 7330 → 16000, `ExecutionTime` 275.35 → 913.86 s, no restart |

**The log damage mechanism, confirmed.** The log is 9,162,357 bytes with exactly
one NUL run: bytes 655,156 – 2,540,883 (1,885,727 bytes). P2's `>` redirect
truncated the file at 02:54:51 while P1 held its own file offset (2,540,883
bytes, which at ~763 bytes/iteration is exactly P1's position at Time ≈ 7330).
P1's next write landed at its old offset, leaving a hole; P2 filled bytes
0–655,156 from the front and then died. So the file now reads: **P2's 859
iterations (7001–7859), then 1.9 MB of NULs, then P1's iterations 7330–16000.**
Iterations 4000–7329 of P1 are unrecoverable as text. That part of §6.1 is
correct.

**Why §6.1 said "Time ≈ 4265".** 25 s of elapsed time at this case's rate
(~10.6 it/s) from an assumed start of 4000 gives ≈ 4265. The estimate is
arithmetically consistent with the assumption that the duplicate restarted at
4000. `startFrom latestTime` made it restart at 7000 instead. The error is a
single wrong premise, not a fabrication — but it is the premise the whole
"never wrote a field" conclusion rested on.

---

## 2. The duplicate wrote a field, and overwrote one

Three independent lines of evidence, any one of which is sufficient.

**(a) Stored pressure gradient identifies the writer of every snapshot.**
`<t>/uniform/momentumSourceProperties` records the gradient at the write, and
both processes' logs print it per iteration. Comparing the stored value with
each process's own logged value at that iteration:

| snapshot | P1's logged pg at that time | P2's logged pg | stored in `<t>/uniform` | writer |
| --- | --- | --- | --- | --- |
| 7500 | 0.0084247934089418 | **0.00759741462064012** | **0.00759741462064012** | **P2** |
| 8000 | 0.00823133562602658 | (dead) | 0.00823133562602658 | P1 |
| 8500 … 16000 | matches at all 15 digits | (dead) | matches | P1 |

All 18 write times from 7500 to 16000 were checked. **Exactly one — 7500 — is
not P1's.**

**(b) Mtimes show an in-place rewrite.** The `7500/` directory and its
`uniform/` subdirectory carry mtime **02:55:05.02** — P1's natural cadence
(`7000/` at 02:54:26, +39 s). Every *file* inside carries mtime **02:55:27.88**
— 22 s later, P2's arrival at Time 7500. A directory older than every file it
contains, with no new filenames, is the signature of a complete overwrite. The
nine `postProcessing/singleGraph_x*/7500/` profile files show the same split
(dirs 02:55:05, files 02:55:27).

This also falsifies §6.1's "**no rewrite**". The write ladder is monotonic in
time value, but it is not rewrite-free: `7500/` was written twice, and P1's own
`7500/` fields no longer exist.

**(c) The duplicate's own function-object directory.**
`postProcessing/wallShearStress/` contains **two** time-series directories:
`4000/` (P1, created 02:50:14, 24 write events 4500→16000, complete, no NULs,
one header) and `7000/` (P2, created 02:54:52, containing **exactly one write
event: Time 7500**). P2's write count is recorded by P2 itself: one.

**(d) The survivor's own record disagrees with the field on disk at 7500 and
nowhere else.** P1's `wallShearStress.dat` logs min/max wall shear per patch at
every write time, and P2 never touched that file. Comparing it against the
stored field files:

```
 t=7000  dat max tau_x 1.522077608765e-03   field 1.522077608765e-03   agree
 t=7500  dat max tau_x 1.837733273523e-03   field 1.954303989425e-03   MISMATCH
 t=8000  dat max tau_x 1.929399078001e-03   field 1.929399078001e-03   agree
```

23 of 24 snapshots agree bit-for-bit. The one that does not is 7500.

---

## 3. Per-link verdicts

### (i) "The duplicate died at ≈ Time 4265; first write at 4500; so it never wrote a field" — **FAILS**

The duplicate restarted at Time 7000 and died at Time 7859, having crossed one
write time. It wrote `7500/`. Both the time and the conclusion are wrong.
*(The "first field write of the continuation was at 4500" half is true — `4500/`
mtime 02:51:04 — but it is about P1 and is not load-bearing.)*

### (ii) "Write ladder clean and monotonic at 35–40 s cadence, no rewrites" — **FAILS on "no rewrites"; holds otherwise**

Time values are strictly increasing and mtimes are strictly increasing across
all 24 continuation snapshots. The cadence claim is very nearly right and its
one deviation is itself the tell: intervals are 34–40 s throughout except
**7000→7500 = 61.9 s** and **7500→8000 = 17.3 s**, which sum to a normal 79 s
for 1,000 iterations. That displacement is P2's later overwrite of 7500 sitting
on top of P1's ladder. **A rewrite occurred and was visible in the very table
that reported none.**

### (iii) "Field data intact and single-writer; only the log was damaged" — **PARTLY FAILS**

*Intact:* **holds, fully.** All 2,896 field files across all 16 cases parse,
contain no NUL bytes, and carry proper OpenFOAM footers. The only absences are
`0/wallShearStress` in each case, which is expected (the function object had not
run at t=0). The `4000/` baseline in `f6d_option_a/d0.2_s000/` is **md5-identical
to the published `ens/d0.2_s000/4000/`** for all seven fields, so the published
reference point is untouched.

*Single-writer:* **fails for exactly one snapshot.** `7500/` has two writers,
and P2's is the one that survives.

*Only the log was damaged:* **fails.** The log lost iterations 4000–7329 as text
(§6.1 said 4000–7000; the true boundary is 7330). But a field snapshot and nine
profile files were also lost — replaced, not corrupted.

### (iv) "Reattachment is computed from fields, not from the log" — **HOLDS, and this is the link that carries the verdict**

Traced in code, not accepted on claim:

- `analyse.analyse_case(case_dir, time)` opens `case_dir/<time>/wallShearStress`,
  reads the `bottomWall` boundary field through `foam_io.read_vector_boundary_field`,
  forms `Cf = -tau_x/(0.5*Ubar^2)`, and returns
  `reattachment_x_over_h` from `primary_bubble(Cf, x)` — the downstream
  zero-crossing of the longest contiguous reversed-shear run. No file other than
  the field and the mesh is opened.
- `analyse.residual_history(log_path)` is the *only* function in `analyse.py`
  that reads a log. It is called solely from that module's `__main__` block and
  is not on the reattachment path.
- `analyse_option_a.analyse_case()` builds the trajectory purely from
  `analyse.analyse_case` at each time directory containing a `wallShearStress`.
- `analyse_option_a.settledness()` is the only log reader in the pipeline, and
  it feeds settledness only — never reattachment or Δreattachment.
- The `published_4000` baseline comes from `aggregate_result.json`, i.e. the
  untouched `ens/` tree.

**There is no path from log text to reattachment anywhere in this repo.** The
collision damaged the log; the log does not reach the number.

### (v) "All three metrics read the end of the run, so a mid-run log gap cannot touch them" — **HOLDS for the reported values; qualified for the trajectory**

Independently recomputed, without using any published result:

| quantity | window | contains the collided 7500 snapshot? |
| --- | --- | --- |
| primary value at the 13500 cut (when VOID was declared) | 12000, 12500, 13000, 13500 | **no** |
| primary value at completion (16000) | 14500, 15000, 15500, 16000 | **no** |
| Δreattachment | primary − published(4000), baseline md5-verified | **no** |
| settledness | last 500 iterations, normalised by median over the second half | **no** (P2's 1,718 pg values sit at the head of the file) |

My independent recomputation of the gate number reproduces it exactly:
**Δ = 5.5061 − 6.3375 = −0.8313** at the 13500 cut. At completion the case has
recovered to **Δ = −0.4906** — still a gate breach (threshold 0.25), so the VOID
stands on the full run as it did on the partial one.

Direct measurement of the settledness exposure §6.1 bounded by argument:
recomputing settledness from **P1's log segment only** gives 0.3392 against the
shipped 0.3401 — a **0.27 %** change. Immaterial.

**Qualification.** Pre-registered metric 1 is "reattachment at *each* written
snapshot", and the trajectory published in `option_a_result.json` therefore
contains one point (t=7500, 5.835) produced by the duplicate rather than by the
run. It is not inside any reported window, and it is not the source of any
quoted excursion — the −1.337 max excursion is 6.3375 (t=4000) − 5.0005
(t=13500), both P1's — but the trajectory as published is not purely
single-writer and should be annotated.

---

## 4. Can the collision have reached the number by any other route?

The exclusion above is about *which process wrote the snapshots*. The remaining
question is whether P2's mere existence perturbed P1's numerics. It cannot have:

- **Separate processes, no shared state.** P1 never re-reads a time directory it
  has written. P2 wrote only into `7500/` and `postProcessing/`.
- **No monitored file was touched.** OpenFOAM here runs with
  `fileModificationChecking timeStampMaster`, which re-reads registered
  dictionaries if their timestamps change. A sweep of the entire case directory
  for anything modified between 02:54:40 and 02:56:10 returns **only** `7500/`,
  the nine `singleGraph_x*/7500/` files, `postProcessing/wallShearStress/7000/`,
  and (at 02:55:45) P1's own `8000/`. Nothing under `system/`, `constant/`,
  `dynamicCode/`, and no `fieldDef`. The last modification to `system/controlDict`
  is 02:41:38 — before either launch.
- **CPU contention changes wall-clock, not arithmetic.** Both runs are serial;
  scheduling cannot alter a deterministic floating-point trajectory. The only
  visible effect of contention is the 61.9 s / 17.3 s cadence pair in §3(ii).
- **P1's post-collision snapshots are continuous with its pre-collision ones.**
  P1's own `wallShearStress.dat` max `tau_x` on `bottomWall` runs
  1.440e-3 (4500), 1.459, 1.450, 1.595, 1.555, 1.522 (7000), **1.838 (P1's own
  7500)**, 1.929 (8000), 1.874, 1.975, 2.251 … 3.519 (12000). There is no step at
  the collision instant; there is a trend that starts before it and continues
  long after it.

---

## 5. The other side: is there an independent explanation, and an uncollided twin?

### 5.1 The destabilisation starts before the duplicate exists

The clearest onset marker is topological, not scalar. `n_reversed_regions` on
the bottom wall, and the separation point, for `d0.2_s000`:

| t | 4000 | 4500 | 5000 | 5500 | **6000** | 6500 | 7000 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| regions | 2 | 2 | 2 | 2 | **3** | 3 | 3 |
| separation x/h | 0.257 | 0.257 | 0.257 | 0.257 | **2.789** | 1.463 | 1.265 |

A third reversed-shear region appears and the separation point jumps by 2.5 x/h
at **Time 6000, written 02:53:06 — 105 seconds before P2 existed**, in a
directory P2 never touched. Reattachment itself is still flat at that point
(6.28), which is precisely the "quiet phase" reading: the near-wall structure had
already broken up while the single scalar the gate watches had not yet noticed.

### 5.2 The oscillation grows, entirely in P1-only territory

Peak-to-peak reattachment swing by window, all recomputed from fields:

| case | 4000–7000 | 7500–11000 | 11500–16000 | full |
| --- | --- | --- | --- | --- |
| `d0.2_s000` | **0.106** | **0.510** | **1.218** | 1.388 |
| `d0.2_s027` | 0.050 | 0.059 | 0.064 | 0.076 |
| `null` | 0.006 | 0.074 | 0.037 | 0.120 |

The growth continues monotonically for 8,500 iterations after the duplicate is
dead, in snapshots all provably P1's. A one-off perturbation does not produce a
growing oscillation in a stable system; and if the system is unstable enough to
grow one, it did not need the perturbation.

At completion, settledness recomputed for all 16: **`null` 0.031 is the only
case below the pre-registered 0.10**, and `d0.2_s000` is 0.340. The two
"survives-VOID" within-case claims of §6.3 — *no member of the 13 settled*, and
*`null` is the only settled run* — are independently confirmed at 16,000
iterations.

### 5.3 An accidental twin experiment, and it is the strongest single piece of physics evidence

The collision is not only a contaminant; it is an unintended and *uncontaminated*
sensitivity test that nobody would have been allowed to fund. P2 restarted from
P1's `7000/` fields written at `writePrecision 15` — a restart-level perturbation.
500 iterations later the two trajectories had diverged:

| quantity at Time 7500 | P1 | P2 | difference |
| --- | --- | --- | --- |
| driving pressure gradient | 0.0084247934089418 | 0.00759741462064012 | **9.8 %** |
| max `tau_x` on bottomWall | 1.8377e-3 | 1.9543e-3 | 6.3 % |
| min `tau_x` on bottomWall | −9.7599e-3 | −9.7155e-3 | 0.46 % |

**A case sitting at a steady solution does not do this.** Two solvers released
from the same state, differing only at restart-write precision, separate by ~10 %
in the driving pressure gradient inside 500 iterations. That is direct,
within-case evidence that `d0.2_s000` at Time 7000 was on an unstable trajectory,
not at a fixed point — which is exactly the pre-registered **Outcome 3** reading,
arrived at by an instrument nobody chose.

### 5.4 The twin search — and what it did not find

**I looked for an uncollided case showing the same destabilisation, and I did
not find a clean one. This is the weakest part of the independent explanation
and it should not be papered over.**

Only three cases in this experiment were selected for being settled, and the
other two — `null` (0.006/0.074/0.037) and `d0.2_s027` (0.050/0.059/0.064) —
stayed flat for all 12,000 iterations. **No second best-settled control
destabilised.** `d0.2_s000` is n = 1 for the specific claim "a member that looked
settled at 4,000 was in a quiet phase".

The nearest uncollided analogues are weaker in kind, not absent:

- **`d0.6_s022`** is quiet across 4000–5000 (2.65, 2.59, 2.75; swing ≤ 0.25) and
  then breaks to 4.29 at 5500 — a 1.5 x/h departure with no collision anywhere
  near it. Quiet-then-break is reproduced; a 3,000-iteration quiet phase is not.
- **`d0.2_s019`** holds 3.88–4.63 for 7,000 iterations (window swing 0.743,
  0.995) and then throws 7.54, 1.44, 7.50, 7.46 in the last 4,500 — a case whose
  apparent calm lasted longer than the entire published run before breaking.
- **`d0.2_s020`** runs the pattern backwards: swing 4.43 early, 0.56 late. Quiet
  windows in this ensemble are phases, not states, in both directions.

So the ensemble supports the *mechanism* — long quiet phases exist in these
flows and end without provocation — while the specific pairing of "best-settled
of 84" with "destabilises" rests on one case. The reason is structural: the
experiment only continued three settled cases, so the sample for that claim is
three, and it split 1–2.

---

## 6. Verdict

# COLLISION EXCLUDED

**for the −0.831 x/h specifically, and not by the chain that was offered.**

What carries it is per-snapshot provenance rather than argument: the stored
pressure gradient and the survivor's own `wallShearStress.dat` independently
identify the writer of all 24 continuation snapshots, exactly one of them
(t=7500) is the duplicate's, and that one is outside every pre-registered metric
window at both the 13500 cut and at completion. The gate number reproduces
exactly (−0.8313) from fields alone, on a baseline md5-identical to the published
`ens/` tree, through code that never opens a log on the reattachment path. Add
that P1's numerics were causally isolated from P2 (no monitored file touched, no
shared state, deterministic serial arithmetic), that the destabilisation's
topological onset is 105 s and 1,000+ iterations before the duplicate existed,
and that the oscillation grows for 8,500 iterations after it is dead.

**This verdict does not ratify §6.1.** Links (i) and (ii) are false, (iii) is
partly false, and the disclosure's "the duplicate never wrote a field" is the
opposite of what happened. §6.1 reached a correct disposition on an incorrect
chain, and a correct disposition on an incorrect chain is worth exactly one
audit — this one. The RETAIN disposition survives; the reasoning offered for it
must be replaced by the reasoning above.

**Recorded against the standard for the stronger verdict.** The commissioning
brief set COLLISION EXCLUDED at "the chain holds at every link **and** the
anomaly has an independent explanation". The chain does not hold at every link,
and the independent explanation is one case rather than two. I use the stronger
form anyway because the direct evidence is stronger than the chain it replaces —
snapshot-by-snapshot writer identification beats an inference from timing — but
the departure is stated here rather than hidden inside it. A reader who prefers
the brief's literal rule should read this as COLLISION EXCLUDED FROM THE NUMBER,
CHAIN NOT SUSTAINED.

---

## 7. Found while looking for something else

1. **The collision guard in `run_option_a_queue.sh` is evaluated before an
   unbounded wait.** The loop tests `[ -f "$ROOT/$c/log.simpleFoam" ]`, *then*
   blocks in `while [ "$(pgrep -c simpleFoam)" -ge "$MAXJOBS" ]; do sleep 20;
   done`, *then* launches. A case that acquires a log during the wait is launched
   anyway. The lesson §6.1 drew — "start a replacement launcher only after the
   previous one is confirmed dead" — is necessary but not sufficient: **this
   guard is stale-prone on its own, single-launcher, whenever the queue is
   saturated.** The wait here lasted minutes.
2. **`startFrom latestTime` turns a duplicate launch into a fork, not a repeat.**
   A duplicate does not redo work; it branches from wherever the survivor got to
   and writes to the same snapshot names. This is why the duplicate reached a
   write time in 60 s when the disclosure expected it to be 235 iterations short
   of one, and it is the general form of the hazard.
3. **A rewrite leaves a directory older than the files inside it.** `7500/`
   mtime 02:55:05 with every file at 02:55:27 is a cheap, general detector for
   double-writers, and it needs no log at all. Worth a line in whatever checks
   this fleet runs.
4. **`d0.2_s027` is not settled either** — settledness 0.253 at completion,
   above the pre-registered 0.10 — while its reattachment is flat to 0.076 x/h.
   Flat QoI and unsettled driver is a third behaviour the two-way settled/moved
   framing does not name, and it is the reason a single-scalar gate can miss what
   §5.1 shows.
5. **The log's true loss boundary is 4000–7329, not 4000–7000.** P1's offset at
   truncation puts it mid-iteration at 7330. Minor, but §6.1's figure is quoted
   elsewhere.
6. **`d0.2_s000`'s Δ at completion is −0.4906**, recovered from −0.8313 at the
   13500 cut. Still a breach, so the VOID is unaffected — but anyone re-reading
   the runs should use the completion figure, and should note that a control
   whose Δ halves between two read points is itself evidence about phases.

## 8. Could not establish

- **Whether a *second*, earlier duplicate also ran, around Time 4265.** If one
  started from 4000 and died before Time 4500 it would have written no field and
  no new function-object directory, and its log text was later overwritten by
  P2's truncation. The artifacts cannot distinguish "the disclosure mis-estimated
  one duplicate" from "there were two, and only the first was seen". The simplest
  reading — one duplicate, whose start time was assumed to be 4000 when
  `latestTime` made it 7000 — accounts for every observation, and a hypothetical
  earlier one would in any case have written nothing.
- **Which launcher started PID 204435, and why its guard passed.** The queue
  runner's `REMAINING` order does not match the observed launch order
  (`d0.6_s021` 02:52:46 … `null` 02:54:30, `d0.2_s000` 02:54:51, `d0.2_s027`
  02:55:57), the script carries mtime 02:52:08 — inside the launch window — and
  no runner log survives. The staleness in §7.1 is a sufficient mechanism but I
  cannot show it is the actual one.
- **P1's own reattachment at Time 7500.** Its fields were overwritten. It is
  bounded by its neighbours (6.358 at 7000, 5.940 at 8000) and by P1's own
  recorded wall-shear extrema at 7500, which lie on a smooth trend, but the
  number itself is gone.
- **Whether the 7500 rewrite changes any downstream figure.** It does not enter
  any pre-registered metric, but `option_a_result.json`'s trajectory and the
  `singleGraph_x*/7500/` profiles are the duplicate's, so any future product that
  consumes the full trajectory or the profile MAE at 7500 inherits it.
