# R1 — PRE-REGISTRATION: THE F3S UNIQUE-SELECTOR REPAIR, as a frozen, capped, schedulable REPAIR ITEM

**Team:** cfd. **Owner:** cfd-supervisor. **Registering lane:** cfd lane **REPAIRQ**, 2026-08-28.
**Status at writing: FROZEN ON COMMIT. No code exists. Zero compute has been spent.**

**Authority for registering a repair as a queue item.** Sanaa's amendment of 2026-08-28T17:01Z
(`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md`), verbatim:
*"Freeze-ahead counts repair-registrations; a team blocked on findings freezes the repairs and
runs them — queue depth 0 with open findings is impossible by definition."* Measured at
2026-08-28T17:08Z by this lane: `verification/queue/cfd/*.json` → **0 entries**. This document is
one of the three repairs that answers that zero.

**The specification this item implements is already frozen and is NOT re-opened here:**
`docs/standards/UNIQUE_SELECTOR_RULE.md`, frozen at commit **`ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6`**
(2026-08-28T16:42:57Z), verified by this lane to be an ancestor of HEAD `7959a75ec9719d17c7a337fda6fa32b15b5c7d12`.
That document fixes the invariant (clauses **U** cardinality and **P** predicate), the refusal
contract (§6), the six controls **C1–C6** (§7), and the ruling that the repair is a **SUCCESSOR**
and never an in-place edit (§8.2). **This registration adds what a specification cannot carry: a
gate, a cap, a cost, a label, and a refusal condition on the instrument itself.**

---

## 1. WHAT THIS ITEM IS, IN ONE PARAGRAPH

Three sites in the F3S rung take `[0]` of a sorted candidate list while assuming the list has one
member, and describe the pressure field by the substring `"p"` rather than naming it. This item
**builds the successor's repaired instruments and drives the controls that prove the repair
works** — it does **not** re-run the F3S ladder and it authorises **no solver compute**. The
product is a control record with a verdict in the fixed vocabulary. The F3S rung's own verdicts
(0 PASS · 0 GATE FAIL · 3 NOT A RESULT, cost row C-112) are **untouched**.

## 2. THE THREE SITES, RE-VERIFIED BY THIS LANE AGAINST THE FILES ON DISK

Read from the one named artefact each, 2026-08-28T17:0xZ, by absolute line number:

| site | the line, verbatim | what is wrong |
|---|---|---|
| `verification/runs/F3_runs/successor_triple_2026-08-26/grade_f3s.py:239` | `cands = sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)`, taken at `:242` as `cands[0]` | substring stands in for the field name; no cardinality guard |
| `.../run_f3s.py:255` | `rawp = sorted(glob.glob(os.path.join(surfd, "*p*.raw")))[0]` | same, plus `IndexError` on an empty match |
| `.../run_f3s.py:285` | `g = sorted(glob.glob(os.path.join(d, "*p*.raw")))` | same, plus the **second, independent** defect below |

**CORRECTION OF FACT OWED UPWARD, one line wide.** The brief routed to this lane states that
*"`run_f3s.py:285`'s defect is DIFFERENT: its `if g:` guard turns a missing pressure sample into a
silently skipped time point"*. **The finding is exactly right and the line number is off by one.**
`:285` is the `g = sorted(glob.glob(...))` assignment; **the `if g:` guard is at `:286`** and the
consumption `v_p.append(p_wall_mean_of(g[0], Lramp))` at `:287`. The plateau series that feeds
rule 5 limb 1 is `v_p`, built in that loop. Substance unchanged; the citation is corrected before
it is frozen, because a reader sent to `:285` for an `if` finds an assignment.

**The realisation ruling is NOT reopened.** `UNIQUE_SELECTOR_RULE.md` §2b measured the defect
**LATENT** across 1,837 of 1,837 directories repo-wide. This lane re-drove the two predicates
against the actual graded directory
`.../runs/wedge/M2.5_th10/fine/postProcessing/surfaceSampleDict/3.11989651/` and measured:

- old predicate (`endswith(".raw") and "p" in f`) → `['p_wedgeSurface.raw']`
- token predicate (`f.split("_",1)[0] == "p"`) → `['p_wedgeSurface.raw']`

**Identical on the directory that produced the landed verdict.** The defect is latent there and
this item does not re-grade it (§12).

## 3. THE OBSERVABLE — AND IT IS NOT A RICHARDSON QUANTITY

**The observable is the CONTROL OUTCOME VECTOR** `(C1, C2, C3, C4, C5, C6)`, each element one of
`FIRED` / `HELD` / `FLIPPED` / `NOT RUN`, as those six controls are enumerated in
`UNIQUE_SELECTOR_RULE.md` §7 at its freeze commit. It is a **structural/ordinal** reading of a
repaired reader, exactly as F26D's `N*` is an ordinal reading on a bracketing ladder
(`cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md` §4).

**Stated explicitly, so it cannot later be asked for:**

- There is **no grid triple.** There are no levels, no `r`, and no refinement of anything.
- **NO OBSERVED ORDER OF ACCURACY IS COMPUTED** and none will be reported.
- **NO GCI IS COMPUTED OR QUOTED**, at `Fs = 1.25` or at any other factor.
- `scripts/roache_triple.py` is **not called** by this item's driver, and standing rule 5 is
  **not applicable** to it — not waived, not satisfied, **inapplicable**, because rule 5 grades a
  row that has a grid triple and this row does not have one.
- The item therefore **cannot** return `NOT A RESULT` for a triple reason. It can return
  `NOT A RESULT` for exactly the reasons in §8.

## 4. THE REGISTERED GATES — fixed before the work runs

| gate | statement | verdict if met | verdict if not |
|---|---|---|---|
| **G-R1-1 — THE POSITIVE CONTROL FIRES ON THE UNREPAIRED CODE** | On the C3 near-miss fixture, the **old** predicate evaluated **in the same control invocation** returns `T_ramp.raw` as its first element: `sorted(f for f in os.listdir(d) if f.endswith(".raw") and "p" in f)[0] == "T_ramp.raw"` | required for **PASS** | **GATE FAIL** — the defect was never demonstrated, so nothing was shown repaired |
| **G-R1-2 — THE DEFECT STOPS FIRING ON THE REPAIRED CODE** | On the same fixture, `select_one(d, "p")` returns a path whose basename is **exactly** `p_ramp.raw`, no exception | required for **PASS** | **GATE FAIL** |
| **G-R1-3 — CARDINALITY REFUSES** | On `{p_wedgeSurface.raw, p_rgh_wedgeSurface.raw}`, `select_one(d, "p")` raises `SystemExit` with `code == 2`; stderr contains `UNIQUE-SELECTOR`, the substring `matched   : 2`, **and both basenames** | required for **PASS** | **GATE FAIL** |
| **G-R1-4 — THE SINGLETON STILL PASSES** | On the graded directory's exact three-file contents, `select_one(d, "p")` returns basename `p_wedgeSurface.raw`, no exception | required for **PASS** | **GATE FAIL** |
| **G-R1-5 — THE NEGATIVE CONTROL (§6)** | Both absence fixtures **exit 2** with `matched   : 0` | required for **PASS** | **GATE FAIL** |
| **G-R1-6 — THE MUTATION FLIPS** | With `if len(cands) != 1:` mutated to `if False:`, **G-R1-3 and G-R1-5 both flip to failure** | required for **PASS** | **GATE FAIL** — a guard whose deletion changes nothing was never exercised |
| **G-R1-7 — FLAG-PROOF** | `python3 -O <driver> --selftest` returns rc **2**; `ast` node count over every shipped file of the successor returns **zero** `ast.Assert` nodes (counted by AST, never by grep) | required for **PASS** | **GATE FAIL** |
| **G-R1-8 — INVARIANCE** | §7's named set is **bit-identical** before and after | required for **PASS** | **GATE FAIL** |

**PASS iff all eight hold. Any one not holding is `GATE FAIL`.** The conditions in §8 that make the
outcome `NOT A RESULT` or `BLOCKED` take precedence over both.

## 5. THE BIRTH REQUIREMENT — Sanaa directive 1, AS A REFUSAL CONDITION ON THIS INSTRUMENT

Sanaa's directive of 2026-08-28T17:01Z, binding here: *"A control defined in terms of the thing it
controls is not a control. A planted control must travel the real production path — written by the
real producer's code, read through the real reader … no instrument grades anything until that
answer is yes, demonstrated."*

**THE REAL PRODUCER, NAMED.** OpenFOAM v2606 (`Build _481094f-20260618`), invoked as

    postProcess -func surfaceSampleDict -latestTime

which is exactly what `run_f3s.py:253` runs (`sh("postProcess -func surfaceSampleDict -latestTime", …)`)
and exactly what the retained `log.surfsample` records as its `Exec :` line. The `surfaces`
function object writes `<field>_<surfaceName>.raw`; the surface name is a **free parameter written
by `run_f3s.py:199`**, which hard-codes the string `wedgeSurface` inside the dict it generates.

**THE REAL READER, NAMED.** `select_one(d, want_field)` as specified in `UNIQUE_SELECTOR_RULE.md`
§6, called from the successor's `read_p_wall_mean()` — the same function that produces the graded
`p_wall_mean`. **Not a re-implementation, not a copy inlined in the test.**

**BR-1 — THE DEMONSTRATION, MANDATORY, AND THE INSTRUMENT REFUSES WITHOUT IT.**

> **The C3 near-miss fixture is produced by RUNNING THE REAL SAMPLER.** The driver copies the
> retained F3S fine case
> (`verification/runs/F3_runs/successor_triple_2026-08-26/runs/wedge/M2.5_th10/fine/` — `constant/polyMesh`
> 5.6 MB, `0/`, and the latest time `3.11989651/` 1.2 MB, all **verified present on disk by this
> lane at 2026-08-28T17:0xZ**) into a scratch tree, rewrites **only the surface name** in that
> copy's `system/surfaceSampleDict` from `wedgeSurface` to `ramp`, and invokes
> `postProcess -func surfaceSampleDict -latestTime` **in the copy**. The files
> `p_ramp.raw` and `T_ramp.raw` that C3 reads are then written **by OpenFOAM's own sampler**, at
> the path OpenFOAM chose, with the bytes OpenFOAM computed.
>
> **THE REFUSAL.** Before it grades anything, the driver asserts, in the same invocation:
> (i) the sampler process returned rc 0 and its log carries an `End` line;
> (ii) `p_ramp.raw` and `T_ramp.raw` both **exist** and are both **newer** than the copied
> `system/surfaceSampleDict` that named them;
> (iii) the old predicate, run on that directory, returns a list of **length ≥ 2** whose **first
> element is `T_ramp.raw`** — i.e. the instrument is shown able to see the defect **firing**, on
> files the real producer wrote, before it is allowed to report the defect repaired.
> **If any of (i)–(iii) fails the driver exits 2 and grades NOTHING.** It does not fall back to a
> hand-written `.raw`, it does not synthesise a directory listing, and it does not report `PASS`
> on the remaining controls.

**WHY A HAND-WRITTEN `.raw` IS REFUSED, in this document's own words.** A `.raw` file written by
the control itself is a schema the producer never emitted; it would certify that the reader can
parse the control's idea of a sampler file, which is the reader's own reflection. Sanaa's directive
names this exact failure. The bytes must come from `postProcess`.

**BR-2 — THE SINGLETON CONTROL USES THE REAL FILES, UNMODIFIED.** C2/G-R1-4's fixture is a
**byte-identical copy** of the three files the real sampler wrote for the graded row —
`T_wedgeSurface.raw` (8,065 B), `p_wedgeSurface.raw` (8,070 B), `rho_wedgeSurface.raw` (8,071 B),
all mtime 2026-08-26 03:59 — with **`sha256` asserted equal to the originals in the same
invocation**. A mismatch is a refusal, exit 2.

**THE RESIDUAL, NAMED RATHER THAN DISCOVERED LATER.** No sampler on this disk has previously
emitted the basename `p_ramp.raw`; BR-1 makes one emit it, for the first time, under this item.
What is therefore demonstrated is that **the real producer, given a surface named `ramp`, writes
the basenames that break the old predicate** — which is the claim `UNIQUE_SELECTOR_RULE.md` §2
makes and the claim this item must not take on trust.

## 6. THE NEGATIVE CONTROL — the repair did not disable the thing it repaired

A widening that is really a disable looks identical from outside. Two fixtures, both mandatory,
both driven through the same `select_one`:

| id | fixture | required outcome |
|---|---|---|
| **N1 — genuinely absent** | an **empty** directory | `SystemExit`, `code == 2`, stderr contains `matched   : 0` and the absolute directory path |
| **N2 — present but wrong field** | a directory holding only `T_ramp.raw` and `rho_ramp.raw`, **written by the real sampler under BR-1** | `SystemExit`, `code == 2`, `matched   : 0`, and the stderr listing names **both** entries actually present |

**N1 and N2 are what forbid the two cheap fake repairs**: returning `None` for absence (the
behaviour `grade_f3s.py:238/241` has today, which `UNIQUE_SELECTOR_RULE.md` §5.1 deletes), and
never refusing at all. **A repair that makes every input acceptable has repaired nothing**, and
G-R1-6's mutation is what proves N1/N2 are load-bearing rather than incidentally satisfied.

## 7. THE INVARIANCE SET — BIT-IDENTICAL, and it is checked by hash

The following are hashed (`sha256`) **before** the item runs and **again after**, and **every one
must be byte-identical**. A single difference is `GATE FAIL` under G-R1-8, and the differing path
is printed.

1. Every file under `verification/runs/F3_runs/successor_triple_2026-08-26/` — **the whole fired
   rung, including `grade_f3s.py`, `run_f3s.py`, `instrument.py`, `F3S_GRADED.json`,
   `COMPLETION.json`, `RESULTS.md`, `RUN_LEDGER.json`, and every file under `runs/`.**
   `UNIQUE_SELECTOR_RULE.md` §8.2 rules that **nothing** in that directory is repairable in place;
   this set is that ruling made mechanical. The scratch copy of §5 is a **copy**; the originals are
   read and never written.
2. `docs/standards/UNIQUE_SELECTOR_RULE.md` — the frozen spec (rule 6: a frozen file is never
   edited).
3. This document.
4. `scripts/roache_triple.py` — named because it is the lab's shared comparator and this item must
   be shown not to have touched it, **not** because it is used here (§3: it is not called).

## 8. CRITERIA — how the verdict is reached, in order

1. **BLOCKED** if the enqueue preconditions of §11 are not met at launch — in particular if the
   successor directory and driver do not exist, or the driver cannot resolve the frozen spec at its
   commit. Nothing is graded.
2. **NOT A RESULT** if BR-1 or BR-2 refuses (exit 2) — the instrument was never shown able to see a
   non-zero through the real code path, so no reading it produces is evidence. This is the birth
   requirement acting as a refusal, per §5.
3. **NOT A RESULT** if the driver's own completion clause fails: rc != 0, no `End`-equivalent
   terminal line in its record, or any control reported `NOT RUN`.
4. **GATE FAIL** if any of G-R1-1 … G-R1-8 is not met, naming which.
5. **PASS** iff all eight gates are met and none of 1–3 applies.

**There is no partial credit and no degraded reading.** Rule 4's *refuse rather than degrade*
governs the driver at every refusal point.

## 9. COST, CAP AND CALIBRATION — rule 12

### 9.1 The basis, term by term, each labelled MEASURED or ALLOWANCE

`ranks = 1`. Core-minutes = wall s × ranks ÷ 60.

| term | wall s | basis |
|---|---|---|
| a) two scratch case copies (~7 MB each: `constant/polyMesh` 5.6 MB + `0/` 16 KB + `3.11989651/` 1.2 MB + `system/`) | 5.0 | **ALLOWANCE.** Sizes MEASURED by `du` this invocation; the copy rate is not measured. Free space MEASURED 216 GB. |
| b) two real-sampler invocations, `postProcess -func surfaceSampleDict -latestTime`, 28,800 cells | 2.5 | **MEASURED UPPER BOUND ×3.** From the retained artefacts' own nanosecond mtimes: `log.sample` last write 1787716768.921264, `log.surfsample` last write 1787716769.340018 → the whole real sampler invocation completed within **0.4188 wall s**, and `run_f3s.py:252-253` runs the two sequentially so the gap bounds it above. 2 × 0.4188 = 0.838 s, carried at ×3 for a cold page cache. |
| c) the C1–C6 harness, including C5's re-run of C1–C4 against a mutated module and C6's `-O` run — ~12 python process invocations | 3.0 | **MEASURED PROXY.** `scripts/queue_entry_check.py --selftest`, a 31-control suite, ran in **0.53 wall s** (rc 0) in this invocation; 1,000 `os.listdir`+predicate cycles on the real graded directory ran in **0.02 wall s**. |
| d) AST node count over the shipped files, the §7 hash set, and the record write | 1.5 | **ALLOWANCE.** |
| **TOTAL** | **12.0** | |

### 9.2 THE ESTIMATE, THE CAP AND THE RATIO

| | value |
|---|---|
| **cost_core_min_estimate** | **0.2000** core-min (12.0 wall s × 1 rank ÷ 60) |
| **cap_core_min_registered** | **0.3000** core-min |
| **cap / estimate** | **1.5000** |
| dollars at the estimate | **$0.000171** — **DERIVED, NOT MEASURED** |
| dollars at the cap | **$0.000257** — **DERIVED, NOT MEASURED** |

Rate: **$0.0513 per core-hour**, c7a.4xlarge, **owner-stated 2026-08-21/22 and reported-by-owner,
never measured** — this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).
**A tiny cost is still a cost**; rule 12 disqualifies a proposal that carries none, and this is why
the terms above are enumerated rather than waved at as "negligible".

**HOW THE CAP IS ENFORCED, and it is never raised.** The driver reads its own start time once,
carries the cap as a wall-second allowance of **18.0 s** (0.30 core-min ÷ 1 rank × 60), and hands
that allowance to `timeout` **around the real-sampler invocations** — the only step whose duration
this lane has not measured directly. An overrun **kills the step and STOPS the item**, leaving the
controls incomplete, which §8 clause 3 grades **NOT A RESULT**. That is the correct outcome of an
overrun and it does not get a second budget.

### 9.3 CALIBRATION AT COMPLETION (rule 12's calibration clause)

At completion the record **must** carry: actual core-minutes from the driver's own log, gross and
cleaned stated separately; waste named separately and never absorbed into the ratio; the ratio
actual/predicted against **0.2000**; the gap attributed to contention, waste or misprediction; and
dollars **derived, not measured**. A row lands in **`docs/COST_CALIBRATION.md`**. **A completion
report without this comparison is incomplete.**

## 10. RULE-2 ABSENCE CONDITION, CHECKED IN THIS WRITING INVOCATION

**`/home/ubuntu/Certonomous/verification/runs/F3_runs/successor_selector_2026-08-28` DOES NOT
EXIST at 2026-08-28T17:12:20Z.** Checked **four ways** in that invocation: `os.path.exists` →
**False**; `os.path.lexists` → **False** (so not a dangling symlink); `os.path.isdir` → **False**;
`glob` on the literal path → **[]**. A fifth, wider check:
`glob('verification/runs/F3_runs/successor_*')` returns exactly
`['…/successor_bandonly_2026-08-25', '…/successor_triple_2026-08-26']` — **the name registered here
is not among them.**

**0.000 core-min have been spent under this registration.** No driver, no control record, no
scratch case copy and no `.raw` written by this item exists anywhere.

**The successor directory name is the supervisor's to set.** `UNIQUE_SELECTOR_RULE.md` §8.3
reserves it explicitly. `successor_selector_2026-08-28` is this lane's proposal; if the supervisor
sets another name, that is a **pre-first-compute amendment**, legal under rule 2, which must state
the condition and how it was checked — naming the new directory and showing it absent. Amendments
before first compute are legal; after first compute the gates are closed and changes land only as
dated addenda that cannot alter a gate, threshold, cap or label.

**Nothing is ever deleted by this item.** The driver creates; it has no `rm -rf`, `rmtree` or
`shutil.rmtree` against any case, run or scratch tree that it did not itself create in the same
invocation, and the §7 invariance set is what proves it after the fact.

## 11. LAUNCH SHAPE — for the supervisor's check 4; **NOT an authorisation**

    bash /home/ubuntu/Certonomous/verification/runs/F3_runs/successor_selector_2026-08-28/run_selector_repair.sh \
         --prereg-commit=<the sha of THIS document's adding commit>

The driver **fires nothing without `--prereg-commit`**, verifies the sha is a commit in this
repository, and additionally verifies that
`docs/standards/UNIQUE_SELECTOR_RULE.md` at `ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6` hashes to
the blob it was frozen as — the grading criteria are read from the frozen spec, not from a copy.

**ENQUEUE PRECONDITIONS — three, and the queue validator checks NONE of them.**
Stated because `scripts/queue_entry_check.py` does **not** verify that `launch_cmd[1]` exists; an
entry naming an absent script validates cleanly and then dies at launch behind a LAUNCHED record.

1. The successor directory and `run_selector_repair.sh` **exist** at the absolute path above, and
   the repaired `select_one` is present in the successor's own copies of `grade_f3s.py` and
   `run_f3s.py` — never in the fired rung's.
2. `bash run_selector_repair.sh --selftest` returns **rc 0**, and `python3 -O` on the driver's
   python entry point returns **rc 2** (G-R1-7 at entry).
3. The `prereg_commit` placeholder in the held queue entry has been replaced with the real sha of
   this document's adding commit.

A queue entry is drafted at
`verification/campaign/queue_entry_R1_F3S_SELECTOR_REPAIR.json` and is **HELD beside this
registration. THIS LANE DOES NOT ENQUEUE IT and has committed nothing.**
`SUPERVISION_CHARTER.md` §3 check 4 — pre-registration committed before compute — is the
supervisor's own and is **not** discharged by this document, by the queue-entry validator, or by
anything a lane can run. **Enqueueing is not authorisation.**

## 12. WHAT IS **NOT** CLAIMED, REGISTERED OR AUTHORISED HERE

- **No verdict of any existing rung is re-graded.** F3 stays CLOSED at 5 PASS · 1 GATE FAIL · 1 NOT
  A RESULT · 3 PENDING. F3S stays at 0 PASS · 0 GATE FAIL · 3 NOT A RESULT, cost row **C-112**,
  15.8298 core-min measured of a 17.6541 cap. The defect is **latent** (§2) and no landed verdict is
  exposed — that finding is the reason, stated so it cannot later be read as leniency.
- **No frozen comparator is edited.** Nothing under `successor_triple_2026-08-26/` is written to,
  by ruling (`UNIQUE_SELECTOR_RULE.md` §8.2) and by mechanism (§7).
- **No gate, threshold, band, cap or label of any OTHER registration is added, moved or removed.**
  F3S's bands stay ±0.5 % / ±2.0 % / ±1.0 %; its cap stays 17.6541 core-min.
- **No solver compute is authorised.** This item runs a sampler on a retained mesh and a control
  harness. The successor rung's *ladder* — its solves, its triple, its bands — is a **separate
  pre-registration that does not exist yet**, and nothing here authorises it.
- **No observed order and no GCI is produced** (§3), and `roache_triple.py` is not called.
- **No claim is made about readers outside cfd.** `UNIQUE_SELECTOR_RULE.md`'s own referral — whether
  the rule becomes lab-wide — is the chief's, and is untouched.
- **Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7). Submissions are
  PARKED.

---

*Registration ends. Written before implementation; the commit that lands it is the freeze.*

---

## DRAFTING NOTE — 2026-08-28T17:1xZ, BEFORE THE FREEZE, BEFORE ANY COMPUTE

**HEAD MOVED WHILE THIS DOCUMENT WAS BEING WRITTEN.** At this lane's first read HEAD was
`7959a75ec9719d17c7a337fda6fa32b15b5c7d12`; on completion it was
`83cb13dabdba2a053ccd2e3d0a1af226ccb151a9`. Peers commit constantly, and a HEAD sha quoted in a
document has a shelf life. **Re-verified in the closing invocation: all three of
`ae2c8c49366259fe2c5bb8ece09d32bc8017c3f6`, `ed77957c4e56cd12e1d5d0c620b218805bd4306b` and
`7959a75ec9719d17c7a337fda6fa32b15b5c7d12` are ancestors of the new HEAD.** Every ancestry claim
above therefore still holds; only the reference point moved. **The supervisor re-derives the freeze
sha at the freeze, from `git log --diff-filter=A -- <this path>`, never from a subject line.**

**This lane committed nothing and staged nothing.** All six artifacts of this item — three
registrations and three held queue entries — stand as **untracked** working-tree files. The shared
git index was not touched, no `git add` of any form was issued, and `refs/heads/main` was not moved.

**Filing, measured before and after in this invocation:** `python3 scripts/check_filing.py` returned
**37 violations across 8 rules (rc 1)** before these files were written and **35 violations across 8
rules (rc 1)** after. **These six files contributed ZERO violations**; the decrease of two is a
peer's removal of `cases/F17c_kovasznay_floor/STATUS.F17c_KV40_FLOOR` and
`cases/F17c_kovasznay_floor/launcher.queue.out` under `R6-RUNARTIFACT` and is **not** this lane's
doing. Stated with its attribution because an improvement claimed by the wrong agent is a false
record in the cheap direction.
