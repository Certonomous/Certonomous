# RUNG 2 pre-registration — NASA CRM / DPW5 — `R2-M2`, the SUCCESSOR to `R2-M1`: a FOCUSED RE-TEST OF THE ONE ARM THAT RAN, with the COUPLED-SETTING FIX that M1's `GATE FAIL` diagnosed and a WRITER REHEARSAL THAT PROVES THE SNAPSHOT LANDS BEFORE THE RUN PAYS

**Team: cfd. Case id `RUNG2-CRM-M2`. v1.1, drafted 2026-09-06 by a `lab-lane` for the cfd supervisor; pre-compute amendment 2026-09-07 (§13) records the driver and grading path now exist and pins the grader sha256. Gates remain OPEN — no compute has run.**

> # ⚠ DRAFT — NOT AUTHORISED TO LAUNCH. CHECK 4 HAS NOT BEEN PERFORMED.
>
> **NOTHING LAUNCHES AGAINST THIS FILE. NO SOLVER COMPUTE HAS BEEN RUN UNDER IT.**
>
> The rule-2 freeze — pre-registration **committed** before compute — is the cfd supervisor's
> **non-delegable personal check** (`SUPERVISION_CHARTER.md` §3). The drafting lane does not take it.
>
> **No queue row has been placed and this lane placed none.** `verification/queue/` is a live drop
> path and writing into it arms a launch. Placement is the chief's, under its own captured grant.
>
> **Solver core-minutes spent by this lane: ≤ 0.04 (bound), all of it the §5 snapshot rehearsal on a
> tiny icoFoam cavity.** No DPW5 grid was solved, no MPI job was started against the CRM grid, no
> RUNG2_CRM run root was created.
>
> **Registered run root `verification/runs/RUNG2_CRM_runs/M2_snapshot_admission/` verified ABSENT
> under a live planted control (§1.3).**
>
> **THIS PROBE PRODUCES NO CRM CLAIM.** No force, drag, lift, moment or coefficient is read out of
> it. Rung 2 (a)'s drag gate stays `BLOCKED` on the three independent grounds its own registration
> names, binding ground **(iii), the absent refinement triple** (cfd supervisor's §15 ruling,
> commit `006aff45`). Nothing in this file touches that.
>
> **A `PASS` on the admission gate `R2M2-G3` clears BLOCKER 1 ONLY — it does not make Rung 2 (a)
> gradeable.** It would let `M6SR`'s `B5a` relaunch; it moves no CRM number.

---

## 0. WHAT THIS IS, AND WHY IT IS SMALL

`R2-M1` was graded UNATTENDED by the queue daemon on 2026-09-06 (`STATUS.R2_M1`, calibration row
`docs/COST_CALIBRATION.md` `C-20260906T174429.649589Z-c13b2999`, commit `97e92465`). It produced,
verified at source in the M1 run root:

- **`R2M1-G0` `PASS`** — the abort reproduces. B0 `rc=136`, class `ABORTED`, last `Time = 2`, thermo
  library in its own stack.
- **`R2M1-G3` `PASS`** — the warm start **MAPPED** (`b1_warmstart_mapped=1`, `b1_warmstart_note=none
  -- mapped`), unlike M0's A3.
- **`R2M1-G4` `GATE FAIL`** — **and this is the whole reason M2 exists.** B1 **iterated CLEAN to
  `Time = 50`, `End` line, `rc = 0`** — the FIRST compressible arm carried past iteration 2 on this
  grid, zero SIGFPE — yet the gate failed **on the RECORDING, not the physics**: B1 wrote **no field
  snapshot at `endTime`**, so every rule-4 field-at-endTime clause failed.
- **`R2M1-G1`/`G5` `PASS`, `R2M1-G2` `NOT A RESULT`** — the writers were live per arm; the 2×2 cells
  were measured; the mechanism arm B2 (trap off) reached only `Time = 2`, one step short of the
  registered ≥ 3, so no cause was named.

**M1 already answered the two open questions M0 left.** The warm start works (B1 ran to endTime), and
the mechanism/2×2 arms were measured (G1/G5 PASS). **What M1 did NOT get is a gradeable admission
artifact from the arm that ran** — because of a single coupled-setting defect. `R2-M2` is therefore
**not** a seven-arm probe. It is a **two-arm re-test of the one arm that ran**, carrying:

| | what | why it is here |
|---|---|---|
| **(a)** | the coupled-setting fix — `writeInterval` managed with `endTime`, not inherited | the single defect that turned B1's clean 50-step solve into a `GATE FAIL` |
| **(b)** | a snapshot-at-endTime rehearsal, **run before the freeze** | §2ap: M1 paid a full 4.667-core-min arm to discover the snapshot could not exist; M2 proves it can, first, for ≤ 0.04 core-min |
| **(c)** | an estimate priced on B1's **measured full-50-step rate** | M1 proved B1 runs to endTime, so its cost is no longer a survival-conditional guess on a borrowed rate |

**THE FALSIFIABLE PROPOSITION `R2-M2` TESTS.** *Does the warm-started compressible arm — B1's proven
reconstruct→guard→decompose→bounds configuration — with `writeInterval` fixed to write at `endTime`,
reach `endTime` **STRICTLY COMPLETE under all six clauses of rule 4**?* If it does, it is **admission
of the compressible path** and would let `M6SR`'s `B5a` relaunch. If it reaches `endTime` but still
fails a clause, **that clause is the next finding — it is named, and the gate is not widened.** If the
warm start fails to map (contra M1), B1 is `BLOCKED` and `R2M2-G3` is `BLOCKED`, not `GATE FAIL`.

---

## 1. CENSUS AND THE PLANT

### 1.1 What exists

| artifact | class | path | state |
|---|---|---|---|
| `R2-M1` registration | pre-registration | `verification/campaign/RUNG2_CRM_M1_PREREGISTRATION.md` | v1.2, frozen, graded against |
| `R2-M1` run root, seven arms | run output | `verification/runs/RUNG2_CRM_runs/M1_mechanism_and_warmstart/` | graded, `GATE FAIL` on `R2M1-G4` |
| `R2-M1` frozen comparator | grading path | `cases/committee-grids/grade_r2_m1.py` | blob `7717d9bd980507a1fdebc6d227d4e4285b7c91e7`. **FROZEN — not edited by this registration (rule 6), and imported by nothing here** |
| `R2-M1` driver | code | `cases/committee-grids/run_r2_m1.sh` | blob `77b40f97`. **FROZEN — the source of the §2 defect; NOT edited. M2 gets its own driver** |
| `R2-M1` calibration row | cost record | `docs/COST_CALIBRATION.md` row `C-20260906T174429.649589Z-c13b2999` (commit `97e92465`) | the measured basis of §6 |
| B1's own graded `controlDict` | evidence of the defect | `.../M1_.../B1/system/controlDict:13,16,17` | `endTime 50; writeInterval 120; purgeWrite 1` — read at source |
| DPW5 `L1.T` hex committee grid | case input | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid/` | 638,976 cells, sha-pinned in `cases/committee-grids/COMMITTEE_GRID_NUMERICS.md` §1 |
| the archived converged **incompressible** solution, `Time = 200` | case input (warm start) | `/home/ubuntu/certonomous-runs/dpw5-committee-probe/run_hex_base_incompressible_a2.11/` | 14 processor dirs; the source B1 maps from |
| **`R2-M2` snapshot rehearsal** | **validation record** | `cases/committee-grids/R2_M2_SNAPSHOT_REHEARSAL.tsv` | **DISCRIMINATES — see §5.** |
| **`R2-M2` driver** | code | `cases/committee-grids/run_r2_m2.sh` | git blob `4f821a3549b928bbc354af3b1be29cf427394b6a`, sha256 `b336575b8a0bb86c7591ff578972866913fdb2c3137ede7ac588ae3f5ba0be73`. **EXISTS** — carries `set_run_window` (§2.3), the pre-solve write-window guard (§2.4), and B1's M1-proven warm-start chain (§4). Written after v1.0; reconciled by the §13 pre-compute amendment. |
| **`R2-M2` grading path** | comparator | `cases/committee-grids/grade_r2_m2.py` | git blob `b40e7dfd4dca04eb4cfff15fec747bbe3f33f275`, **sha256 `7f8089d81fa78e8b863cc0ea35271de61877b7e21e7ecdff1e7f46f247f9c089`** (rule-2 pin — hash the on-disk file against this and against the committed blob before grading). **EXISTS**, imports no frozen comparator, 15/15 selftest controls fire (§13). |

### 1.2 What does not exist

| absent artifact | class |
|---|---|
| any `verification/runs/RUNG2_CRM_runs/M2*` directory | run output |
| any queue row naming `M2` in `verification/queue/cfd` | queue entry |
| any `RUNG2-CRM-M2` row in `docs/COST_CALIBRATION.md` | cost record |
| ~~`cases/committee-grids/run_r2_m2.sh` (the M2 driver)~~ | code — **STRUCK: now EXISTS**, see §1.1 and §13 (pre-compute amendment 2026-09-07) |
| ~~`cases/committee-grids/grade_r2_m2.py` (the M2 grading path)~~ | comparator — **STRUCK: now EXISTS**, see §1.1 and §13 (pre-compute amendment 2026-09-07) |

### 1.3 THE PLANT — the absences above are measured, not assumed

Rule 3. Each reader was shown able to see a hit **at the exact path it searches**, then shown the
absence again. Run 2026-09-06, one shell invocation each:

| reader (exact searched path) | before | probe planted | after removal | |
|---|---|---|---|---|
| `ls -d verification/runs/RUNG2_CRM_runs/M2_snapshot_admission` | **0** | **1** | **0** | **DISCRIMINATES** |
| `ls verification/queue/cfd \| grep -ci M2` | **0** | — | — | **0** (see §1.3a) |

**§1.3a.** The M2 prereg file itself necessarily exists once this file is written, so its absence
plant was taken **before drafting** (before: 0). The queue reader's standing value is 0 and no M2
probe was planted into the live queue path (writing there arms a launch); its discrimination is
inherited from the identical reader exercised in M1 §1.3, which read 0 → 1 → 0 on the same path.

---

## 2. (a) THE COUPLED-SETTING FIX — WHAT M1 GOT WRONG, AND WHY IT IS THE SAME FAMILY AS THE DRY-RUN ANCHOR MISS

### 2.1 The defect, settled at source

`run_r2_m1.sh:281` assembles every arm with `cp -a "$SEED/system"`, copying the seed's
`controlDict` verbatim. The seed's `controlDict` is **internally self-consistent**:

> `run_hex_base_compressible_a2.11/system/controlDict:13,16,17` — `endTime 120; writeInterval 120;
> purgeWrite 1`.

With `writeControl timeStep` and `deltaT 1`, the number of steps equals `endTime` numerically, so the
seed writes **exactly one** snapshot, at its own `endTime 120`. **The invariant the seed satisfies is
`writeInterval == endTime`** (more generally `writeInterval ≤ (endTime − startTime)/deltaT`).

`set_endtime` (`run_r2_m1.sh:325-334`) then rewrites **`endTime` only** — B1 to 50, the diagnostic
arms to 3 — and **never touches `writeInterval`**. The invariant breaks: B1 becomes
`endTime 50; writeInterval 120; purgeWrite 1`. `50 < 120`, so no write ever fires before the run
ends; `purgeWrite 1` keeps only a snapshot that was never written; the driver's end-of-run
`reconstructPar` (`:659`, guarded by `[ -d processor0/$et ]`) finds no `processor0/50` and never
fires. **Verified on B1 at source:** `B1/processor0/` holds only `0` and `constant`; no serial `50/`
exists; `R2M1-G4` fails every field-at-endTime clause while `rc=0` and `End` are both present.

### 2.2 It is a COUPLED-SETTING / INCOMPLETE-ENUMERATION defect — the same family as the dry-run miss

This is the framing that makes the repair safe rather than cosmetic. `endTime` and `writeInterval`
are **coupled**: under `purgeWrite 1` a snapshot lands at `endTime` **only if** `writeInterval`
divides into the step count so that a write coincides with the final step. **Rewriting `endTime`
below `writeInterval` silently defeats the write.** The seed held the invariant; the driver broke it
by rewriting **one member of a coupled pair**.

This is **exactly** the family of `R2-M1`'s own Amendment-2 dry-run finding (§14.1): the stand-in
builder's anchor-assertion list *"had checked three anchors and **omitted `endTime`**"* — an
incomplete enumeration of the things that must move together. M1 fixed that instance in the builder
and did not generalise it to the driver's own `set_endtime`. **M2 generalises it.**

### 2.3 The repair — collapse the pair into one function so they CANNOT drift

The fix is not "also rewrite `writeInterval`" bolted on beside `set_endtime` — two functions a future
edit could again call singly. It is to **rewrite both members of the coupled pair in one function**,
so the run window cannot be set without setting the write that captures its end. The M2 driver
(`run_r2_m2.sh`, §12) will carry, in place of M1's `set_endtime`:

```python
# set_run_window <controlDict> <endTime> -- rewrites endTime AND its COUPLED PARTNER writeInterval
# TOGETHER. Under purgeWrite 1 a snapshot lands at endTime only if writeInterval coincides with the
# final step; rewriting endTime alone (M1's defect, GATE FAIL on R2M1-G4) silently defeats the write.
import re, sys
p, et = sys.argv[1], float(sys.argv[2])
s = open(p).read()
m = re.search(r"^\s*deltaT\s+([0-9.eE+-]+)\s*;", s, re.M)
dt = float(m.group(1)) if m else 1.0
nsteps = int(round(et / dt))                       # steps from startTime 0 to endTime at deltaT
if nsteps < 1:
    raise SystemExit("run window < one step in %s" % p)
s, n1 = re.subn(r"^(\s*endTime\s+)[0-9.eE+-]+\s*;",      r"\g<1>%s;" % et,     s, count=1, flags=re.M)
s, n2 = re.subn(r"^(\s*writeInterval\s+)[0-9.eE+-]+\s*;", r"\g<1>%d;" % nsteps, s, count=1, flags=re.M)
if n1 != 1 or n2 != 1:
    raise SystemExit("run window not fully rewritten (endTime=%d writeInterval=%d) in %s" % (n1, n2, p))
open(p, "w").write(s)
# ASSERT THE COUPLING HOLDS on disk: writeInterval must be >=1 and <= the step count, so a write
# coincides with the final step. A guard that only ever passes is not a guard.
t = open(p).read()
wi = int(re.search(r"^\s*writeInterval\s+([0-9]+)\s*;", t, re.M).group(1))
assert 1 <= wi <= nsteps, "writeInterval %d does not capture endTime (nsteps %d)" % (wi, nsteps)
```

Setting `writeInterval := nsteps` gives **exactly one** snapshot, at the final step, under
`purgeWrite 1` — no per-step I/O tax, and the field present at `endTime` is the converged (or
diverged) state the admission gate must read. The top-level `writeInterval` is rewritten; the
function-object block's own `writeInterval 1` (the `fieldMinMax` writer, §7 of the M1 registration)
is **untouched** — the regex is anchored to column 0 (`^\s*writeInterval`) and the function object's
key is indented, matching only the top-level line (confirmed against B1's real `controlDict`:
lines 16 and 30/31 are distinct).

### 2.4 A run-time assertion, so the fix is checked on THIS run and not merely on the rehearsal

The M2 driver will, **after assembling every arm and before any solve**, parse each arm's
`controlDict` and refuse (exit 7) unless `writeInterval ≤ round((endTime − startTime)/deltaT)` — i.e.
a snapshot at `endTime` is **possible** for every arm that reaches it. This converts §5's pre-freeze
rehearsal into a per-run guard: M1's arm was assembled with a `controlDict` that could not write, and
nothing in the driver noticed. This driver notices.

---

## 3. THE ARM SET — TWO ARMS, AND WHY NOT SEVEN

| arm | energy | `transonic` | bounds | FPE trap | `endTime` | `writeInterval` (coupled) | what it is for |
|---|---|---|---|---|---|---|---|
| **B0** | `sensibleInternalEnergy` | no | none | on | 120 (seed's own) | 120 (seed's own, already coupled) | **reproduction control.** Anchors M2's instrument/assembly to the known abort. |
| **B1** | `sensibleInternalEnergy` | no | **yes** | on | **50** | **50 (set by §2.3)** | **THE WARM START**, B1's proven M1 config, `writeInterval` fixed. Carries the only admission gate. |

**Why only these two.** M1 already measured the mechanism (`R2M1-G2` design, arm B2) and the 2×2
de-confound (`R2M1-G5` `PASS`, arms B3–B6). Re-running them buys the same measurements again. The
**single** thing M1 left unmeasured is whether B1's clean 50-step solve yields a gradeable admission
artifact once the recording defect is repaired. B0 is retained because a probe whose reproduction
control does not reproduce is `NOT A RESULT` (M1's `R2M1-G0` ordering) — it is the guard that the
arms were assembled correctly. **Everything B1 needs to survive is carried forward from M1 unchanged:
the reconstruct→binary-safe-guard→decompose warm-start chain, the run-time both-directions guard
control, and the `limitTemperature` + `pMin/pMax` bounds.** M2 re-litigates none of it — M1 proved it.

**B0's `writeInterval` is left at the seed's 120.** It is already coupled (`writeInterval 120 ==
endTime 120`), and B0 aborts at `Time = 2` regardless, so it never reaches a write. The §2.4 run-time
assertion still passes for B0 (`120 ≤ 120`).

---

## 4. WHAT B1 CARRIES FORWARD FROM M1, VERBATIM AND UNCHANGED

These are M1-proven and are **not re-opened** (see M1 registration §2, §13.2):

1. **The warm-start chain** — `reconstructPar -time 200 -fields (U k omega)` on the archived
   incompressible solution → the **binary-safe** patch guard (`open(...,'rb')`, bytes-in bytes-out) →
   `decomposePar -fields -time 0` onto B1's own 14-way addressing → `WARMSTART_MAPPED` marker. M1
   measured this end to end: reconstruct 2 core-s, decompose-fields 7 core-s, marker written, B1 ran.
2. **The run-time guard control** — the guard is driven both ways on the real reconstructed field in
   the run (accepts the real `U`, refuses a `farfield`-scrubbed copy) before its verdict is trusted;
   if it does not discriminate, B1 is `BLOCKED` and the guard's verdict is discarded.
3. **The bounds** — `limitTemperature` (100–1000 K) fvOption and `pMin 1000; pMax 1e7` in `SIMPLE`.
4. **The `fieldMinMax` writer block** (`(T p rho U)`, `writeControl timeStep`, `writeInterval 1`),
   inserted not substituted (L-221/L-222). M0's `forceCoeffs` object is **not** carried; no force
   claim is produced.

The **only** change from M1's B1 is §2.3: `writeInterval` is coupled to `endTime` so the endTime
snapshot lands.

---

## 5. (b) THE SNAPSHOT REHEARSAL — RUN BEFORE THE FREEZE, PROVING THE WRITER WRITES

`VERIFICATION_CHARTER.md` §2ap: prove the writer writes before the run pays for it. M1 paid a full
50-step arm (4.667 core-min) to discover its snapshot could not exist. This rehearsal proves the fix
makes it exist, first, for a bounded ≤ 0.04 core-min.

**Script** `cases/committee-grids/rehearse_r2_m2_snapshot.sh`; **record**
`cases/committee-grids/R2_M2_SNAPSHOT_REHEARSAL.tsv`. It builds a tiny, stable icoFoam cavity — **NOT
the DPW5 grid, and the record says so on its own first line** — and runs it in **parallel** to
`endTime` **twice**, both with `purgeWrite 1`, `writeFormat binary`, `writeControl timeStep`, exactly
M1's `controlDict` shape, differing in **one line**: the config is run through the same chain B1 runs
(parallel solve → `reconstructPar -time <endTime>` → serial snapshot), and a snapshot-counting reader
is read back per-processor and reconstructed.

| config | `writeInterval` | solve `rc` | per-processor snap at `endTime` | reconstructed serial snap | fields `U`,`p` present |
|---|---|---|---|---|---|
| **BROKEN** (M1's inherited 120; steps = 5 < 120) | 120 | 0 | **0** | **0** | 0 |
| **FIXED** (`writeInterval == nStep`, §2.3) | 5 | 0 | **1** | **1** | **2 / 2** |

**THE PLANTED CONTROL / DISCRIMINATES LINE (rule 3, §2ap), using the SAME reader in both directions:**

> **reader sees the endTime snapshot PRESENT under FIXED (per-proc = 1, serial = 1, fields = 2/2) and
> ABSENT under BROKEN = M1's config (per-proc = 0, serial = 0) — DISCRIMINATES.**

The zero (BROKEN) is a zero from a reader shown, in the same run, able to see a non-zero (FIXED): the
plant is live, not asserted. **Measured cost: 1.09 wall s total (0.36 s user + 0.42 s system);
conservative upper bound treating the whole wall as 2-rank = 0.036 core-min GROSS per pass; ≤ 0.04
core-min across the passes kept.** `cost_basis: on-box-owner-stated, REPORTED-BY-OWNER`;
**$0.000034 DERIVED, NOT MEASURED**.

**What the rehearsal does NOT establish (stated plainly).** It is a controlDict-IO test on a 400-cell
cavity. It says **nothing** about whether B1 survives on the DPW5 grid — M1 already showed it did, and
that is a separate fact from whether the snapshot lands. It establishes exactly one thing, the thing
M1 lacked: **the coupled-setting fix makes a field snapshot land at `endTime`, per-processor and
reconstructed, where M1's inherited config writes none.**

---

## 6. (c) THE COST — RE-PRICED ON B1's MEASURED FULL-RUN RATE

### 6.1 Why the structure is different from M1's

M1's headline priced **all seven arms aborting at iteration ≤ 2** and put B1's survival in a
**conditional** term on a **borrowed** 0.626 core-min/step rate, because *nothing on this box had yet
carried a compressible arm past iteration 2*. **M1 changed that fact.** B1 ran 50 steps clean, and the
per-step rate is now **MEASURED**. So M2's headline prices B1 on its **own measured full-50-step
rate**, incurred as the established behaviour — not as a survival gamble on a borrowed number.

### 6.2 The rate anchors, all now MEASURED (from the M1 calibration row `97e92465`)

| anchor | value | provenance |
|---|---|---|
| B1, warm-started + bounded, per step, 14 ranks, this grid | **0.09333 core-min/step** | **MEASURED.** M1: B1 = 20 wall s × 14 ranks = 280 core-s over 50 steps. |
| B0 reproduction abort, 14 ranks, this grid | **1.1667 core-min** | **MEASURED.** M1: B0 = 5 wall s × 14 ranks = 70 core-s (aborts at `Time = 2`). |
| `reconstructPar` warm-start, serial, 3 fields | **0.0333 core-min** | **MEASURED.** M1 `COST.tsv` `B1_reconstruct` = 2 core-s. |
| `decomposePar -fields`, serial, this grid | **0.1167 core-min** | **MEASURED.** M1 `COST.tsv` `B1_decompose_fields` = 7 core-s. **M1 had this ESTIMATED at 0.500; it is now measured.** |
| `reconstructPar` at `endTime`, serial, full field set | **0.20 core-min** | **ESTIMATED.** Has never run on this grid — M1 never wrote an endTime snapshot to reconstruct. ~7 fields at ≥ the 2 core-s the 3-field warm-start reconstruct took; 12 core-s allowed. |
| assembly, mesh `decomposePar` ×2, selftest, grade | **0.10 core-min** | **measured-anchored.** M1 spent 0.033 for five arms' bookkeeping; M2 has two. |

### 6.3 HEADLINE — incurred on M1-established behaviour, NOT on a survival gamble

| line item | derivation | rate provenance | core-min |
|---|---|---|---|
| B0 reproduction abort | 1 × 1.1667 | **MEASURED** | **1.167** |
| B1 warm-start `reconstructPar` | — | **MEASURED** | 0.033 |
| B1 warm-start `decomposePar -fields` | — | **MEASURED** | 0.117 |
| **B1 full 50-step solve** | 50 × 0.09333 | **MEASURED (M1 `97e92465`)** | **4.667** |
| B1 `reconstructPar` at `endTime` (NEW — M1 never did this) | — | **ESTIMATED** | 0.200 |
| assembly / mesh-decompose ×2 / selftest / grade | — | measured-anchored | 0.100 |
| **the §5 snapshot rehearsal — ALREADY SPENT at drafting** | — | **MEASURED** | 0.040 |
| **REGISTERED HEADLINE ESTIMATE** | | | **6.32** |

**93.7 % of the headline (5.92 of 6.32) rests on MEASURED anchors.** The one estimated line, the
endTime reconstruct, is 3.2 % of the headline and is named as the term most likely to be wrong,
because it is the one operation in the whole probe that has never run on this grid.

### 6.4 ABORT-CONDITIONAL / DOWNSIDE — stated separately, folded into nothing

M1 established B1 runs to endTime, so these are the **contra-M1** branches; each costs **less** than
the headline, not more, and none is added into the total or the cap arithmetic:

| conditional line item | condition | effect on cost |
|---|---|---|
| B1's warm start fails to map (contra M1) | `reconstructPar`/guard/`decompose` fails | B1 `BLOCKED`; the 4.667 solve + 0.20 endTime-reconstruct **NOT incurred** → headline drops to ~1.45 core-min. `R2M2-G3` `BLOCKED`, `R2M2-G4` `BLOCKED` not `GATE FAIL`. |
| B1 aborts before `endTime` (contra M1 — e.g. the write config perturbs numerics) | SIGFPE at step k < 50 | B1 costs `k × 0.09333` < 4.667; `R2M2-G4` `GATE FAIL` on the physics, and the failing step is named. |

**There is no upside conditional term.** M2 adds no survival-gated cost above the headline, because
the only survival question (does B1 reach endTime) was already answered by M1.

### 6.5 Cap, and dollars

**REGISTERED CAP: 12.0 core-min.** = headline 6.32 + ≈1.9× margin. Tighter than M1's 55.0 (10.4×
headline) **because every rate here is MEASURED, not borrowed** — the huge margin M1 carried existed
to cover the untested 0.626 rate, which no longer applies. **An overrun STOPS the run; it does not get
a new budget** (rule 12). The driver charges `wall × ranks` after every step and records remaining
arms `BLOCKED` on a cap hit, never extended.

**Dollars are DERIVED, NOT MEASURED — the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5). At `c7a.4xlarge` $0.0513/core-h, `cost_basis:
on-box-owner-stated, REPORTED-BY-OWNER`:

- headline 6.32 core-min = 0.10533 core-h → **$0.0054 DERIVED**
- cap 12.0 core-min = 0.20000 core-h → **$0.0103 DERIVED**

The single-run escalation line is $150 = 175,439 core-min; **this cap is 0.0068 % of it.** On-box run,
no rented node, no GPU.

### 6.6 The calibration row this run will owe

Rule 12. At completion the row states the ratio **against the headline**; the endTime-reconstruct
line, being the only estimate, is reported on its own line; any contra-M1 branch (§6.4) that is taken
is reported as a **branch not taken from the headline**, in those words, never divided into the ratio.
Co-residency is recorded from a box-state reading taken at launch, or stated **ABSENT** if none
survives (M1's row had to state it absent because the daemon fired unattended).

---

## 7. THE GATES

| id | gate | **threshold (pre-registered)** | cap (core-min) | label if met | label if not |
|---|---|---|---|---|---|
| **R2M2-G0** | **Reproduction control.** B0 reproduces the known abort with M2's instrument/assembly attached. | B0 exits **136**, log classifies `ABORTED`, last `Time ≤ 2`, `libfluidThermophysicalModels.so` in its own stack | 1.2 | proceed | **`NOT A RESULT` for the whole probe** — no conclusion is drawn from B1 |
| **R2M2-G1** | **Writer liveness, per arm** (carried from `R2M1-G1`). | For every launched arm: W1 records == `steps_completed`, exactly, for each of `T`, `p`, `rho`, `mag(U)`; W2 ≥ `steps_completed`; a zero-step arm satisfies this with zero records | 0.0 (inside G0/G3 runs) | **`PASS`** | **`GATE FAIL` on the writer**, and the writer, not the physics, is named |
| **R2M2-G2** | **The warm start MAPS AND EXERCISES** (carried from `R2M1-G3`). | `B1/WARMSTART_MAPPED` present — written only after the binary-safe guard **discriminated at run time** and `decomposePar -fields` returned 0 — and B1's arm state is not `BLOCKED` | 0.6 | **`PASS`** | **`BLOCKED`** — the remedy is untested. **Explicitly NOT `GATE FAIL`** |
| **R2M2-G3** | **ADMISSION — the only admission gate, and THE ITEM VERDICT.** The repaired warm start reaches `endTime` STRICTLY COMPLETE. | B1 reaches `Time = 50` satisfying **all six clauses of rule 4**: `rc = 0`; `End`; last time == `endTime`; `ExecutionTime` count == `endTime`; the field set `T U p k omega nut alphat` present at `endTime` **(the field list M1's frozen comparator graded)**; **every field newer than the case's own `0/T`** (age guard) — with **no** signal 8 and **no** `nan`/`inf` token in the log | 5.0 | **`PASS`** — the compressible path is ADMITTED; Blocker 1 clears; `M6SR`'s `B5a` may relaunch | **`GATE FAIL`** — the failing clause is **named** and is the next finding; the gate is **not** widened. If `R2M2-G2` is `BLOCKED`, this is **`BLOCKED`**, not `GATE FAIL` |
| **R2M2-G4** | **Planted control on the reader** (rule 3), and **the snapshot-lands rehearsal** (§2ap). | The comparator's ≥ 12 controls fire — the completion rule driven in the refusing direction, the age guard both ways, the field-at-endTime reader planted present/absent — **and** the §5 rehearsal DISCRIMINATES (already measured) | 0.5 (rehearsal spent: **0.040**) | **`PASS`** | **`NOT A RESULT` for every other gate** — a reader not shown able to see both outcomes has measured nothing |

**The item verdict is carried by `R2M2-G3`.** `R2M2-G0` and `R2M2-G4` can only turn a `PASS` or
`GATE FAIL` **into** `NOT A RESULT`, never the reverse (rule 5's ordering applied to a gate table).
**`R2M2-G2` returning `BLOCKED` is a real, reportable outcome, not a failure to report.**

---

## 8. THE GRADING PATH — NOT YET WRITTEN, AND WHAT IT MUST BE

**`cases/committee-grids/grade_r2_m2.py` NOW EXISTS** (pre-compute amendment 2026-09-07, §13; sha256
`7f8089d8…f9c089`). M0 v1.0 **failed check 4** for naming a comparator that was not in git; this
file **exists, imports nothing from the frozen `grade_r2_m1.py` (rule 6), passes its own selftest
15/15 with the field-at-endTime plant proven to fire in the refusing direction, and is committed
together with this registration's amendment (§13).** It reuses M1's proven control structure
conceptually (not by import):

- the completion rule (rule 4) driven in the **refusing** direction — each of the six clauses failing
  on its own clause, all six together passing (M1's C11);
- the age guard both ways (M1's C6), the run-root guard (M1's C7);
- the field-at-endTime reader **planted present and absent** — this is the control that speaks
  directly to M1's `GATE FAIL`, and M1's comparator did **not** carry it because M1's arms never
  wrote an endTime snapshot to read;
- the writer gate (M1's C10) and W1/W2 reader plants (M1's C8/C9), carried for `R2M2-G1`;
- `R2M2-G0` reproduction classification against the real archived abort/clean logs (M1's C1–C5).

**Original v1.0 note (STRUCK 2026-09-07):** ~~This lane did not write it: the task scoped compute to
the §5 rehearsal only… It is the immediate next artifact and is named, not silently deferred.~~ It
has since been written, selftested and committed — see §13.

---

## 9. WHAT THIS PROBE MAY NOT CLAIM

1. **No force, drag, lift, moment, coefficient or CRM number.** None is read out.
2. **A `PASS` on `R2M2-G3` does not make Rung 2 (a) gradeable.** It clears **Blocker 1 only**; it
   would let `M6SR`'s `B5a` relaunch. Rung 2 (a)'s drag gate stays `BLOCKED` on binding ground
   **(iii), the absent refinement triple** — a compute result cannot move a ground about grids that
   do not exist on this box.
3. **No mechanism claim and no 2×2 cause.** Those were M1's business (`R2M1-G2` `NOT A RESULT`,
   `R2M1-G5` reported cells and named no cause); M2 does not reopen them and reads no cause from B1.
4. **The rehearsal is not a physics result** and is cited as one nowhere.
5. **A `GATE FAIL` on `R2M2-G3` names its failing clause and stops.** It does not license widening
   the gate or a third remedy on B1 without a new registration.

---

## 10. THE FALSIFIABLE PROPOSITION, RESTATED FOR THE GRADER

Registered before the run, so it cannot be produced afterwards as if it had been:

> **B1 — the warm-started, bounded compressible arm, with `writeInterval` coupled to `endTime = 50`
> — will reach `Time = 50` and write a field snapshot there that satisfies all six clauses of rule 4.**
>
> **FALSIFIER.** If B1 reaches `Time = 50` (`rc = 0`, `End`) but a rule-4 clause still fails — a
> field absent, a field older than `0/T`, a `nan` token — the proposition is **wrong**, and that
> clause is recorded as the next finding. A wrong proposition changes **no** gate, threshold or
> label: `R2M2-G3` grades whether the admission artifact was *produced complete*, not whether this
> lane guessed the outcome.

---

## 11. HONEST RECORD OF THIS DRAFTING

**Check-repair cycles, counted (the check-loop bound is three per stage):**

| stage | cycles | what each was |
|---|---|---|
| §5 snapshot rehearsal | **1** | The reader returned empty and the DISCRIMINATES check tripped `[: integer expression`. Cause: `local label=$1 wi=$2 d="$WORK/$label"` on one line — bash expands `$label` in the third assignment **before** `label` is bound, and under `set -u` inside a `$( )` command substitution that kills the subshell silently, so `run_config` emitted nothing. Split into two `local` lines; the rerun DISCRIMINATED. A confirming re-measurement (not a repair) followed. |
| this registration | **0** | check 4 not yet performed — it is the supervisor's |

**Spend by this lane: ≤ 0.04 core-min (bound), all of it §5, all of it on a 400-cell serial+2-rank
cavity.** `cost_basis: on-box-owner-stated`; **≤ $0.000034 DERIVED, NOT MEASURED**. No DPW5 solve, no
MPI job against the CRM grid, no RUNG2_CRM run root, no queue row.

**What this lane could not settle, and it needs someone else:**

1. **`reconstructPar` at `endTime` on this grid has never run** — M1 never wrote an endTime snapshot
   to reconstruct. Its cost is ESTIMATED (§6.2), not measured. **Named and stopped.**
2. **The M2 driver `run_r2_m2.sh` and grading path `grade_r2_m2.py` do not exist** (§1.2, §8, §12).
   Building and driving them is the next step and needs review; this registration is **not
   freeze-ready** until the grading path exists and is committed with it (the M0 check-4 lesson).
3. **Check 4 — the pre-registration committed before compute — is the cfd supervisor's and is not
   taken here.**

---

## 12. STATUS

| | |
|---|---|
| registration | **v1.1 DRAFT — gates OPEN, amendments legal until first compute; §13 pre-compute amendment 2026-09-07 landed the driver + grading path and pinned the grader sha256** |
| check 4 | **NOT PERFORMED** — the cfd supervisor's, non-delegable |
| queue row | **NONE PLACED.** Placement is the chief's, under its own captured grant |
| run root | `verification/runs/RUNG2_CRM_runs/M2_snapshot_admission/` — **ABSENT**, plant-verified 0 → 1 → 0 (§1.3) |
| grading path | `cases/committee-grids/grade_r2_m2.py` — **EXISTS**, sha256 `7f8089d8…f9c089` (§1.1). Selftested 15/15 with the field-at-endTime plant proven to fire in the refusing direction (§13). **Freeze-ready pending the cfd supervisor's check 4.** |
| driver | `cases/committee-grids/run_r2_m2.sh` — **EXISTS**, sha256 `b336575b…0be73` (§1.1). Carries the §2.3 coupled `set_run_window`, the §2.4 pre-solve write-window guard, and B1's M1-proven warm-start chain (§4). `--selftest-window` 5/5, `--selftest-cap` 7/7, bare call exits 8 (§13). |
| snapshot rehearsal | `cases/committee-grids/R2_M2_SNAPSHOT_REHEARSAL.tsv` — **DISCRIMINATES** (§5), committed with this draft |
| solver core-min spent under this registration | **≤ 0.04 (bound)**, all of it the §5 rehearsal on a 400-cell box |
| Rung 2 (a) | **BLOCKED**, untouched, binding ground **(iii)** |

---

## 13. PRE-COMPUTE AMENDMENT — 2026-09-07 — THE DRIVER AND GRADING PATH EXIST, AND THE GRADER SHA IS PINNED

**This is a rule-2 pre-first-compute amendment. It states its condition and how it was checked.**
**Condition:** no compute has run under this registration. **Checked at source 2026-09-07T03:40Z:**
the registered run root `verification/runs/RUNG2_CRM_runs/M2_snapshot_admission/` is **ABSENT**
(`ls -d` errored, no such directory); there is **no** `M2*` run directory under
`verification/runs/RUNG2_CRM_runs/`; there is **no** `RUNG2-CRM-M2` row in
`docs/COST_CALIBRATION.md`. Gates are therefore still OPEN and this amendment is legal. **It alters
no gate, threshold, cap or label.** The banner (NOT AUTHORISED) and check 4 (the cfd supervisor's,
non-delegable) are untouched by it.

**What it reconciles.** v1.0 §1.2, §8 and §12 asserted the driver and grading path *did not exist* —
true when v1.0 was drafted, false now. Both were written and committed at `a2996ed0` (2026-09-06,
after the v1.0 registration commit `4214375c`). This amendment strikes the "does not exist" cells
(they are struck, not silently rewritten), records the artifacts in §1.1, and pins the grader by
sha256 so rule 2's "hash the frozen file against what ran" check has a registered target.

**The artifacts, pinned.**

| artifact | git blob | sha256 |
|---|---|---|
| `cases/committee-grids/grade_r2_m2.py` | `b40e7dfd4dca04eb4cfff15fec747bbe3f33f275` | `7f8089d81fa78e8b863cc0ea35271de61877b7e21e7ecdff1e7f46f247f9c089` |
| `cases/committee-grids/run_r2_m2.sh` | `4f821a3549b928bbc354af3b1be29cf427394b6a` | `b336575b8a0bb86c7591ff578972866913fdb2c3137ede7ac588ae3f5ba0be73` |

The driver's run-time rule-2 check (`run_r2_m2.sh:681-687`) compares `git hash-object` of the grader
against `git rev-parse HEAD:<grader>` and records `comparator_matches_committed_blob`. The sha256
above is the additional content pin for a hash-against-the-committed-blob check off the git object.

**The evidence, measured 2026-09-07 (no solver launched — all of it pure comparator/driver logic).**

1. **Grader selftest — present → PASS.** `python3 grade_r2_m2.py --selftest` → **15/15 controls fire,
   exit 0.** The field-at-endTime plant is present as **C12** (synthetic: reader sees all 7 fields
   PRESENT, then ABSENT for an empty time dir and for a missing time dir — DISCRIMINATES) and **C13**
   (the plant driven in the refusing direction on M1's REAL B1 arm, which reached `endTime` and wrote
   no snapshot: the reader reports 0 fields at `50/` — the exact zero M1's `R2M1-G4` GATE FAIL turned
   on). C14 confirms the §5 rehearsal record DISCRIMINATES.
2. **Grader — reader-cannot-see → REFUSE (the falsifying half).** A scratch mutant that blinds the
   field-at-endTime reader (`read_endtime_fields` forced to return `[]`) makes **C12, C11 and C6 FAIL
   and the comparator REFUSE with exit 2** (`R2M2-G4: NOT A RESULT — 12/15`). So the plant fires in
   the refusing direction: a comparator whose reader cannot see the planted-present field does not
   grade — exactly the control M1's comparator lacked. The mutant lived only in the scratchpad; the
   committed grader's sha256 is unchanged.
3. **Driver `--selftest-window` → 5/5.** `set_run_window(50)` couples top-level `writeInterval := 50`
   while preserving the function-object's indented `writeInterval 1`; the pre-solve guard PASSES the
   coupled dict and B0's untouched seed, and **REFUSES M1's exact defect** (endTime 50 with
   writeInterval 120 > 50 steps) and a sub-one-step window.
4. **Driver `--selftest-cap` → 7/7**; bare call **exits 8** (never a clean-looking no-op run).

**Freeze-readiness.** With the grading path committed, sha-pinned, selftested in both directions, and
the driver's write-window guard shown to refuse the M1 defect, this registration is **freeze-ready
pending the cfd supervisor's check 4**, which this lane does not take. No queue row is placed; no
solver is launched; the run root stays ABSENT.

**`lines whose number changed above this section: N/A — this is a DRAFT with open gates, not a frozen
file; rule 6's line-stability assertion applies only after the freeze.`** No other record cites this
draft by line.
