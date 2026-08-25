# VMFL045-R2 — opus-4.8 lane RUN REPORT OF RECORD (interim v2; state and cost only)

**Channel:** lane→supervisor `SendMessage` is one-way; this committed file is the
reliable channel. **INTERIM** — the run is still solving L3. State and cost only.
**Not graded yet** (L3 incomplete) — see §5, §7.

## 0. Authority — resolved
An earlier chief instruction ("grade nothing and issue no verdict") conflicted with my
supervisor's authorisation to grade. I surfaced the conflict, noted no agent message is
Sanaa's consent, and held to the conservative reading. **The chief has WITHDRAWN that
instruction** ("the chief routes and relays; it does not command another supervisor's
lane") and confirmed my **supervisor's authorisation governs inside this territory.**
**My instruction comes from my supervisor.**

## 1. The boundary I am working to (supervisor's, stated clean)
- **Running the frozen comparator is NOT issuing a verdict.** It computes the verdict
  and the Roache triple mechanically from rules frozen before compute; the answer is the
  instrument's. **I am authorised to run it and record what it prints, verbatim** —
  including `GATE FAIL` or `NOT A RESULT`.
- **I may not choose, adjust, soften or re-run toward a verdict.**
- **The TIER is the supervisor's ruling, not mine.** I will record the verdict and leave
  the tier cell for the supervisor, or write the supervisor's **standing default marked
  as the supervisor's, pending confirmation**: a `NOT A RESULT`/`GATE FAIL` verdict
  tiers `NOT HELD` unless a stated reason says otherwise; only a believable measurement
  missing one V/G/P column earns `GATE REACHED`.
- **A pre-declared suspicious condition I surface, not stamp:** expected order **p ≈ 1**,
  with **p ≈ 2 declared suspicious**. If the comparator yields a suspicious-order PASS I
  surface it to the supervisor rather than landing it silently.

## 2. Run state (read off disk at 2026-08-25T02:40:45Z)
- **HEALTHY, STILL SOLVING L3.** `rhoCentralFoam` alive, 100% CPU, etime ~613s;
  latest `Time = 0.0029785387` of `endTime = 0.007`. `COST.txt`, `CAP_EXCEEDED.txt`,
  `L3_360x304/RUN_RC.txt` all ABSENT. No `End` line yet.
- **The solve is detached (`setsid`); the observation was not.** That distinction — not
  any fault in the solve — is what cost the mid-L3 sample when my turn ended. The run
  was never at risk; only an in-agent watcher was.
- **Repair validated by the run, not by argument:** smoke test rc=0 in 1 s; run 1's
  `Entry 'e' not found in fvSolution/solvers` is **gone**; L3 is solving the energy
  variable `e` cleanly — the `"(h|e)"` widening genuinely carries the viscous energy
  path. Both frozen zones non-empty at every level (L3: gateZone 4025, gateZoneInner 2358).
- Frozen shas confirmed by the run at launch: pre-registration `592e872b`, comparator
  `382ff497`.

## 3. Per-level results so far
| level | cells | rc | wall s | core-min |
|---|---|---|---|---|
| L1_90x76 | 6 840 | 0 | 22 | 0.3667 |
| L2_180x152 | 27 360 | 0 | 160 | 2.6667 |
| L3_360x304 | 109 440 | in flight | — | — |

## 4. Cost so far
- **3.0334 core-min measured** (L1+L2), serial (RANKS=1). Cap **48**; estimate **20.4**.
- ~24 core-min total is a **projection**, not a measurement; the real figure is
  `COST.txt` at completion. **Calibration (rule 12) is computed at completion, never before.**

## 5. Contention — and a labelling note (I did NOT touch the sampler's block)
- The **mid-L3 sample is owned by the supervisor's OS-level sampler**
  (`verification/runs/ansys_verification/contention_sampler.sh`, pid 2000222, PPID 1),
  which fires on **simulation time** crossing 3.5e-3 and writes its own
  **"SAMPLE 2: MID-L3"** block into `CONTENTION.txt`. It is alive and has correctly not
  fired yet (L3 is ~24 % through). **I will not write, edit or reconstruct that sample.**
- **I removed my own earlier detached contention watcher** (it would have written a
  competing mid-L3 block into the reserved section). Killed by explicit process group;
  the sampler and the solver were verified alive afterwards. It had written nothing.
- **Labelling caveat, resolved in favour of the sampler:** my earlier entry
  "SAMPLE 2: DURING L3, EARLY" predates the sampler and collides in number with the
  sampler's authoritative "SAMPLE 2: MID-L3". My entry is a **supplementary early-L3
  observation, NOT the midpoint**; the sampler's block is authoritative for mid-L3. I
  left `CONTENTION.txt` untouched rather than edit into a file the sampler is appending
  to. **The terminal (end) sample is mine to append at completion, around the sampler's block.**
- On disk now: SAMPLE 1 (launch, names peer VMFL003) and my supplementary early-L3 entry
  (names VMFL003). A peer ansys-verification job (VMFL003) ran concurrently and
  deliberately; load ~3.0–4.0 on 16 cores — LIGHT.

## 6. Carried forward, unchanged
Fluent's 1.902 (point-sampled) would **FAIL** our 1 % gate at +1.494 %; CFX's 1.871
passes at −0.160 %. **A near-Fluent value is a `GATE FAIL` and is never narrated as
agreement with Ansys.** p ≈ 1 expected; **p ≈ 2 suspicious.**

## 7. Remaining steps to close the case (for whoever holds the next live turn — me on a
##    bonus wake, or a fresh lane the supervisor dispatches; everything needed is on disk)
1. Confirm L3 complete: `COST.txt` present, or `L3_360x304/RUN_RC.txt` rc=0.
2. **Strict completion at each level** (report which hold, do not conclude): rc=0; an
   `End` line; last time == `endTime` 0.007; fields present; `ExecutionTime` count ==
   `endTime`; every field newer than that level's own `0/` (age guard).
3. **Run the frozen comparator UNMODIFIED:**
   `python3 cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py` — capture
   `GRADING_VMFL045_R2.json` and its printed output **verbatim** (value, triple state,
   observed order, GCI, verdict). `--verify-frozen HEAD` first (grading path
   `382ff497`). Do not modify or re-run toward an answer.
4. **If observed order is the pre-declared-suspicious p ≈ 2 with a PASS: SURFACE it to
   the supervisor; do not auto-stamp.**
5. Append the **terminal contention sample** (mine) around the sampler's mid-L3 block.
6. Write `cases/ansys_verification/VMFL045/RESULTS.md` (record the `"(h|e)"` validation
   and the run-1 crash it repaired).
7. **Three parents in ONE invocation, each count re-derived from the files at commit
   time** (VMFL003 may land its row first): (a) register row #N in
   `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` with **tier inline
   (supervisor's default, marked as the supervisor's, pending confirmation)** + the
   credential tally; (b) `docs/ansys_verification/CASE_MAP.md` campaign fraction (line
   ~88) + VMFL045 tier cell (line ~244) + tier table; (c) **leave the #1–#4 foot
   addendum's scope untouched** (my row carries its tier inline; it does not join the
   back-fill). 
8. `docs/COST_CALIBRATION.md` row: predicted 20.4 vs measured `COST.txt`, ratio,
   contention named separately as waste, dollars derived at $0.0513/core-h.
9. Commit each per rule 10 (private index, explicit `|| ABORT`, post-commit verify).

## 8. Watchers
Run detached (`setsid`) — survives. Supervisor's contention sampler detached — survives.
**I have NOT armed a new watcher** for completion; an earlier completion waiter, if it
fires, is a **bonus wake, not the plan.** The plan is this committed file.
