# RC2 — RESULTS. The Kaandorp divergence-flag repair and the zero-solver re-grade

**RUN VERDICT: `PASS`.**

**And the registered meaning of that word, quoted from the frozen document rather
than paraphrased** (`PREREGISTRATION.md` §5.3, "RUNG HEADLINE"):

> **`PASS` here means "the re-grade was performed and is defensible", NOT
> "nothing was wrong"** — 16 flag cells are expected to move and that is the
> finding, not a failure.

Sixteen flag cells moved. That is the finding. Nothing in this record moves,
re-grades or re-labels a committed verdict, and this record is not entitled to.

| | |
|---|---|
| item | **RC2_kaandorp_divergence_repair** |
| freeze commit (pre-registration + BOTH instruments, one commit) | `0aa1a0492b159dd724035da2f11115e5fe96e92f` |
| queue entry bound at | `4d0bdcc6c73fd7127574262bdc4ad408bb764bd1` |
| instruments | `rc2_divergence.py` (`ce2acaf0…c15a8e32`), `regrade_rc2.py` (`1c43b3e5…e152c7d9`) — sha-pinned at `PREREGISTRATION.md` §14 |
| run root | `/home/ubuntu/closure-data/rc2/` |
| primary artifact | `/home/ubuntu/closure-data/rc2/REGRADE_RC2.json` |
| citation artifact | `/home/ubuntu/closure-data/rc2/CITATION_MANIFEST.json` |
| launched record | `verification/queue/closure/launched/RC2_kaandorp_divergence_repair.json` |
| launched / ended (UTC) | `2026-09-10T03:49:35Z` → `2026-09-10T03:50:37Z` (`STATUS.queue.RC2_kaandorp_divergence_repair`, `launcher_rc=0`) |
| solver compute | **0 core-min. RC2 launches no solver and re-runs nothing** (`PREREGISTRATION.md` §5.4) |

This file is the graded record **registered in advance**: `PREREGISTRATION.md`
§12's Files table lists `RESULTS.md` with the role *"the graded record, written
after the run"*. Writing it is registered, not an improvisation.

---

## 1. THE CONTROL FIRED IN BOTH DIRECTIONS, BEFORE ANY ROW WAS READ

`PREREGISTRATION.md` §5.1 orders the control **first**: if the two-direction
planted control does not fire in both directions on real producer-written logs,
the successor **refuses (`sys.exit(2)`) and no re-grade runs at all**. It fired.

| leg | registered requirement | measured | artifact |
|---|---|---|---|
| **POSITIVE** — six named real fatal logs, three distinct signature classes (`FOAM FATAL IO ERROR`, `FOAM FATAL ERROR`, `Foam::sigFpe::sigHandler`) | successor reads **fatal** on all six | **6 / 6 read fatal** | `REGRADE_RC2.json` `control.positive_real_fatals = 6` |
| **NEGATIVE** — the case's own 16 preserved banner-only Kaandorp logs | successor reads **NOT-fatal** on all 16 | **16 / 16 read NOT-fatal** | `REGRADE_RC2.json` `control.negative_banner_only = 16` |
| **BLIND MIRROR** — the frozen `run_lane.py:175` predicate reinstated for exactly one call | must **DISAGREE**, reading fatal on all 16, or the corpus is not the corpus the defect lives on and the control refuses | **16 / 16 disagreed** | `REGRADE_RC2.json` `control.blind_frozen_fires = 16` |
| overall | both directions | `control.fired_both_directions = true` | `REGRADE_RC2.json` |

**Why the mirror is the load-bearing leg.** A reader that says "not fatal" on 16
healthy logs has demonstrated nothing on its own; standing rule 3 refuses a zero
from a reader not shown able to see a non-zero. The blind mirror is what proves
these 16 files are the files the D548 defect actually bites — the frozen
predicate reads `true` on every one of them and the successor reads `false` on
every one of them, on the same bytes, in the same invocation.

---

## 2. THE MOVEMENT TABLE — 16 ROWS, EACH CITING ITS OWN ARTIFACT

Every row: read from a preserved `log.run` under
`/home/ubuntu/closure-data/aposteriori/kaandorp/<case>/log.run`, opened
read-only, hashed, and provenance-checked against `results.json` by standing
rule 4's age guard read **backwards** (a log written *after* the results file
did not produce the row).

| case | frozen `diverged` | successor `diverged` | flag | independent `converged` field | log bytes | sha256 (first 12) | provenance | row verdict |
|---|---|---|---|---|---|---|---|---|
| `AR_1_Ret_360__NULL` | `true` | `false` | **MOVED** | `false` | 28.9 MiB | `c86d2a291fbc…` | ok: older than `results.json` | `PASS` |
| `AR_1_Ret_360__TRUTH` | `true` | `false` | **MOVED** | `false` | 0.5 MiB | `a51b6e23128e…` | ok: older than `results.json` | `PASS` |
| `AR_1_Ret_360__MEANB` | `true` | `false` | **MOVED** | `false` | 5.1 MiB | `e63c2f284811…` | ok: older than `results.json` | `PASS` |
| `AR_1_Ret_360__ML0` | `true` | `false` | **MOVED** | `false` | 29.2 MiB | `801b79cce2f9…` | ok: older than `results.json` | `PASS` |
| `AR_1_Ret_360__ML1` | `true` | `false` | **MOVED** | `false` | 2.4 MiB | `0359636b3e9e…` | ok: older than `results.json` | `PASS` |
| `AR_1_Ret_360__ML2` | `true` | `false` | **MOVED** | `false` | 2.8 MiB | `e65e905cf496…` | ok: older than `results.json` | `PASS` |
| `AR_1_Ret_360__MEANB64` | `true` | `false` | **MOVED** | `false` | 1.5 MiB | `465eb0bd4959…` | ok: older than `results.json` | `PASS` |
| `AR_3_Ret_360__NULL` | `true` | `false` | **MOVED** | `false` | 28.9 MiB | `87f15834b8ab…` | ok: older than `results.json` | `PASS` |
| `AR_3_Ret_360__TRUTH` | `true` | `false` | **MOVED** | `true` | 3.0 MiB | `c5eef2e9bffb…` | ok: older than `results.json` | `PASS` |
| `AR_3_Ret_360__MEANB` | `true` | `false` | **MOVED** | `false` | 31.2 MiB | `910a0cf2a542…` | ok: older than `results.json` | `PASS` |
| `CBFS13700__NULL` | `true` | `false` | **MOVED** | `false` | 0.9 MiB | `becac070fb10…` | ok: older than `results.json` | `PASS` |
| `CBFS13700__TRUTH` | `true` | `false` | **MOVED** | `false` | 29.0 MiB | `0c902a2337c2…` | ok: older than `results.json` | `PASS` |
| `CBFS13700__MEANB` | `true` | `false` | **MOVED** | `false` | 26.2 MiB | `95c760a41b70…` | ok: older than `results.json` | `PASS` |
| `CBFS13700__ML0` | `true` | `false` | **MOVED** | `false` | 26.2 MiB | `e0d510675948…` | ok: older than `results.json` | `PASS` |
| `CBFS13700__ML1` | `true` | `false` | **MOVED** | `false` | 26.2 MiB | `68909704a00c…` | ok: older than `results.json` | `PASS` |
| `CBFS13700__ML2` | `true` | `false` | **MOVED** | `false` | 26.2 MiB | `e5dd7a56dad0…` | ok: older than `results.json` | `PASS` |

**Totals, read from `REGRADE_RC2.json`:**

| quantity | value | field |
|---|---|---|
| rows re-graded | **16** | `regradable = 16` |
| flag cells moved `true` → `false` | **16 of 16** | `movement.FLAG_MOVED = 16`, `movement.FLAG_MOVED_of = 16` |
| provenance `ok: older than results.json` | **16 of 16** | per-row `provenance` |
| **distinct sha256 over distinct files** | **16 distinct hashes over 16 distinct paths** | per-row `sha256` / `path` |
| corpus read | **268.0 MiB** across the 16 logs | per-row `bytes` summed |
| `not_a_result_this_run` | **0** | `not_a_result_this_run = []` |
| `infra_defects` | **[]** (empty) | `infra_defects` |
| citation files enumerated | **11** | `citation_file_count = 11` |
| consumer-audit citation sites | **7** | `consumer_audit.all_sites`, 7 entries |

**The distinctness is stated because it is the thing a sloppy re-grade gets
wrong.** "16 of 16" is only worth reading if the sixteen are sixteen. They are:
sixteen distinct case directories, sixteen distinct `log.run` paths, sixteen
distinct sha256 values, no repeats — checked over `REGRADE_RC2.json`'s
`regrade_rows`, not asserted.

---

## 3. THE DENOMINATOR — AND WHY IT IS 19, NOT 16

**`results.json` holds 19 run entries, not 16.** `PREREGISTRATION.md` §1.3 says
so in the frozen text, before any compute:

> `/home/ubuntu/closure-data/aposteriori/kaandorp/results.json` holds **19 run
> entries**, of which **16 carry a `diverged` key.**

**So "16 of 16" is never quoted bare in this record. The re-grade covered 16 of
16 SCORED rows, which are 16 of the 19 entries in `results.json`.**

The other three, named:

| entry | `scored` | `diverged` | `wall_s` | case directory on disk |
|---|---|---|---|---|
| `AR_3_Ret_360__ML0` | `false` | `null` | `0.0` | **ABSENT** |
| `AR_3_Ret_360__ML1` | `false` | `null` | `0.0` | **ABSENT** |
| `AR_3_Ret_360__ML2` | `false` | `null` | `0.0` | **ABSENT** |

*(read from `/home/ubuntu/closure-data/aposteriori/kaandorp/results.json`; the
directory absence checked on disk under
`/home/ubuntu/closure-data/aposteriori/kaandorp/`.)*

**These three are never-run, unscored cells.** They carry **no flag**, so there
is no flag to move. And §5.3's `NOT A RESULT` clause does not reach them: that
clause bites *"≥1 row's artifact absent or provenance unestablished"* — a row
that HAS an artifact which is missing, or whose artifact cannot be dated against
`results.json`. A cell that was never run has no artifact to be absent and no
provenance to establish. **`not_a_result_this_run = 0` is therefore CORRECT, and
this paragraph is why it is correct rather than merely convenient.**

The distinction matters in exactly one direction: a reader who takes `16/16` as
a full census of `results.json` would believe the re-grade swept 19 entries. It
swept 16. The three unscored entries are outside the re-grade's reach and are
named here so that the gap is disclosed rather than discovered.

---

## 4. R4 IS UNCONTAMINATED — VERIFIED AT SOURCE, NOT INFERRED FROM THE AUDIT

`PREREGISTRATION.md` §4.2 registered the expectation that R4 reads a **different**
reader. The instrument's own consumer audit reports it:

| citation site | owner |
|---|---|
| `cases/RANS_LES_closure_models/RC2_kaandorp_divergence_repair/regrade_rc2.py:26` | RC2 instrument |
| `cases/RANS_LES_closure_models/RC2_kaandorp_divergence_repair/regrade_rc2.py:27` | RC2 instrument |
| `cases/RANS_LES_closure_models/RC2_kaandorp_divergence_repair/regrade_rc2.py:94` | RC2 instrument |
| `cases/RANS_LES_closure_models/RC2_kaandorp_divergence_repair/regrade_rc2.py:220` | RC2 instrument |
| `cases/RANS_LES_closure_models/RC2_kaandorp_divergence_repair/regrade_rc2.py:271` | RC2 instrument |
| `cases/RANS_LES_closure_models/R4_sparta_build/score_aposteriori.py:195` | **R4** |
| `cases/RANS_LES_closure_models/R4_sparta_build/score_aposteriori.py:196` | **R4** |

**But an audit reporting its own conclusion is not a verification of that
conclusion**, so the claim was re-derived from R4's source by the closure
supervisor, at source, in R4's own file:

1. **R4 defines its OWN reader.** `cases/RANS_LES_closure_models/R4_sparta_build/score_aposteriori.py:55-76` defines a
   local `log_facts(case_dir)` whose fatal test is the **narrow** one —
   `fpe = "Foam::sigFpe::sigHandler" in txt` — with an in-file comment naming
   exactly the `trapFpe` banner hazard that defeats the frozen Kaandorp
   predicate. Its `diverged` is `bool(fpe or blew)`, where `blew` is the last
   `sum local` continuity above 1.0.
2. **R4 builds its rows from that reader, over R4's own case directories.**
   `score_aposteriori.py:182-184`: `lf = log_facts(cd)` for `cd` under R4's
   `WORK` tree, then `entry = dict(complete=ok, completion_reason=why,
   stop_state=..., **lf)`.
3. **R4's `entry.get("diverged")` therefore reads R4's own value.**
   `score_aposteriori.py:195` consumes `entry.get("diverged")` — the key
   supplied by the `**lf` splat at :184, not any key from the Kaandorp tree.
4. **A repo grep finds ZERO reads of the Kaandorp tree in any R4 script.**
   `grep -rn -i "kaandorp" cases/RANS_LES_closure_models/R4_sparta_build/*.py`
   returns **0**.

**Conclusion, and its exact width: R4's frozen reference frame does not inherit
the D548 defect.** R4's own `GATE FAIL` stands on R4's own reader and is untouched
by anything in this record. This record makes no other claim about R4.

---

## 5. `TRIGGER_DISARMED` — ITS OWN CATEGORY, AND EXPLICITLY NOT FOLDED INTO "NO VERDICT MOVED"

`PREREGISTRATION.md` §4.3 registers three categories, and the third
deliberately:

> **The third category is registered deliberately.** … A repair that disarms one
> leg of a two-leg clause without changing the verdict is **still a change to a
> registered trigger after first compute**, and burying it inside "no verdict
> moved" is exactly the shape of an evidence-annotated-as-non-binding failure. It
> is reported as its own category.

**The finding, in two legs:**

| leg of the Kaandorp `GATE FAIL` clause | registered at | state after the re-grade | rows |
|---|---|---|---|
| **"any ML seed *diverges*"** | Kaandorp `PREREGISTRATION.md:230-231`, `:291-294` | **DISARMED** — frozen `true` → successor `false` | **all 16** |
| **"or fails to converge"** | the same two-leg clause | **STAYS ARMED** — `converged == false`, computed independently from the residual history at `run_lane.py:183-196` | **15 of 16** |
| sole exception | | `converged == true`, so neither leg armed on that row | **`AR_3_Ret_360__TRUTH`** |

Read from `REGRADE_RC2.json`: `movement.TRIGGER_DISARMED.diverges_leg`,
`.fails_to_converge_leg`, `.converged_true_rows = ["AR_3_Ret_360__TRUTH"]`, and
the per-row `converged_field` (15 × `false`, 1 × `true`).

**This is stated as its own category and is not summarised as "no verdict
moved."** The two are different facts. A registered gate trigger has changed
state on 16 rows after first compute. That it changes no headline — because the
second leg of the same clause remains armed on 15 of them — is a *separate*
observation, and collapsing the first into the second is precisely the failure
mode §4.3 registered against.

The registered expectation at §4.4 was **`TRIGGER DISARMED ≥ 1, on H1`**, with
the prediction that the *fails-to-converge* leg would stay armed on 15 rows and
that `AR_3_Ret_360__TRUTH` would be the exception. **The measurement matches the
prediction on both counts** — 15 armed, that one exception, named in advance. A
matched prediction is worth more than a matched number, and §4.4 exists so that
this could have been visibly wrong.

---

## 6. THE 10 PRE_RELAUNCH CELLS — THE REGISTERED DISPOSITION, DISCHARGED AS REGISTERED

`PREREGISTRATION.md` §5.3's fourth row pre-registers the disposition **before
the run**: *"the 10 PRE_RELAUNCH cells → `NOT A RESULT — artifact provenance
unestablished`, registered in advance (§3.3)"*. Ten cells, and the instrument
emitted exactly ten:

| cell | verdict |
|---|---|
| `AR_1_Ret_360__NULL` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_1_Ret_360__TRUTH` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_1_Ret_360__MEANB` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_1_Ret_360__ML0` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_1_Ret_360__ML1` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_1_Ret_360__ML2` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_1_Ret_360__MEANB64` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_3_Ret_360__NULL` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_3_Ret_360__TRUTH` | `NOT A RESULT — artifact provenance unestablished` |
| `AR_3_Ret_360__MEANB` | `NOT A RESULT — artifact provenance unestablished` |

Read from `REGRADE_RC2.json` `pre_relaunch_not_a_result` (10 entries), each
carrying the reason *"artifact provenance unestablished; no hash of the
PRE_RELAUNCH-era log was preserved (section 3.3)"*.

**This is a discharge, not a discovery.** The disposition was fixed in the
frozen document before the run; the instrument applied it; nothing about it was
decided after looking. It is recorded here so that a reader counting rows finds
all of them accounted for: 16 re-graded `PASS`, 10 `NOT A RESULT` on the
PRE_RELAUNCH era, 0 `NOT A RESULT` arising from this run.

---

## 7. ROUTING — AND THIS RECORD MOVES NOTHING

`PREREGISTRATION.md` §5.4, frozen before the run:

> **It may not change a committed verdict.** If a verdict moves, RC2 **reports
> the movement**; the ruling is the closure supervisor's and, per Sanaa's
> routing, verification rules on each moved verdict. **A lane does not move a
> verdict.**

**Applied literally to this record:**

* RC2 **reports movement**. It has reported it: 16 flag cells, one trigger leg,
  on 16 named rows citing 16 named artifacts.
* **The ruling on any moved verdict is the closure supervisor's**, and per
  Sanaa's routing **verification rules on each moved verdict**.
* **This record moves no verdict, re-grades no verdict, and re-labels no
  verdict.** The Kaandorp headline, R4's `GATE FAIL`, R5C's `GATE FAIL` and every
  other committed verdict stand exactly as committed. `REGRADE_RC2.json`
  `movement.VERDICT_MOVED` reads *"reported: 0 expected; RC2 does not adjudicate
  — routed to supervisor then verification (section 5.4)"*.
* **No frozen file was edited by this item.**
  `Kaandorp2020_TBRF/aposteriori/run_lane.py` is untouched — it is reproduced
  verbatim only inside the blind mirror control and is never imported, patched or
  rewritten. `results.json` and `results_PRE_RELAUNCH_2026-08-23.json` were
  opened **read-only**; the re-grade wrote a **new** file, `REGRADE_RC2.json`, in
  the RC2 run root.
* **Nothing has been sent, filed, uploaded, registered, posted or commented.**
  SUBMISSIONS PARKED (standing rule 7).

---

## 8. COST — ESTIMATE VERSUS ACTUAL (standing rule 12)

**Unit: core-minutes** = wall s × ranks ÷ 60. **ranks = 1** (`launched` record
`ranks: 1`; `LAUNCH_LOG.tsv` row `2026-09-10T03:49:35Z`, ranks `1`).

| figure | value | source |
|---|---|---|
| wall | **62.14 s** | `REGRADE_RC2.json` `wall_s = 62.14`; corroborated by the queue window `03:49:35Z` → `03:50:37Z` (62 s) in `STATUS.queue.RC2_kaandorp_divergence_repair` |
| **measured actual** | **1.036 core-min** (62.14 × 1 ÷ 60) | derived from the two measured quantities above |
| registered estimate | **4.0 core-min** | `PREREGISTRATION.md` §7; `launched` record `cost_core_min_estimate: 4.0` |
| registered cap | **12.0 core-min** | `PREREGISTRATION.md` §7; `launched` record `cap_core_min_registered: 12.0` |
| **ratio actual / estimate** | **0.259** | |
| ratio actual / cap | **0.086** — **8.6 % of the cap**; no cap fired, no `CAP_OVERRUN.txt` or `ESTIMATE_OVERRUN.txt` written | run root listing |
| gross vs cleaned | **gross = cleaned = 1.036 core-min** — 62.14 s is far below the `COMPUTE_BUDGET_CHARTER` §2 3600-s stall rule | |
| **waste** | **0.000 core-min**, named separately per `COMPUTE_BUDGET_CHARTER` §6 and never folded into the ratio | no re-run, no crash, no refusal, no cap fire |
| **solver compute** | **0 core-min registered and 0 spent** | `PREREGISTRATION.md` §7; RC2 launches no solver |
| dollars | **$0.00089 — DERIVED, NOT MEASURED** at the owner-stated $0.0513/core-h, reported-by-owner | the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

**Gap attribution: MISPREDICTION, IN THE CONSERVATIVE DIRECTION. Not contention,
not waste, not a stopped run.** §7's line-item budget totals 133 s wall; the
graded invocation measured 62.14 s. The dominant attributable line is §7's
*"`--selftest` ×2 (`python3`, `python3 -O`), report and JSON assembly, startup —
60 s"*, but the registered `launch_cmd` is a bare
`python3 regrade_rc2.py --run-root /home/ubuntu/closure-data/rc2` with **no
`--selftest`**: roughly 60 of the 133 budgeted seconds priced work the graded
invocation never performs. Those two selftests were run separately, by the
supervisor, at the freeze (§14.1). Contention was **present but not dominant**:
the daemon measured the box at **busy 66.8 % (~10.7/16 cores), MemAvailable
21.5 GB** at launch (`verification/queue/runner.log`, `2026-09-10T03:49:35Z`) —
and contention pushes an actual **up**, not down, so it explains none of the
under-run.

**The calibration row lands in `docs/COST_CALIBRATION.md` as id `C-20260910T040337.011383Z-01cfe9a4`**
(standing rule 12; landed under the rule-10 private-index protocol via
`scripts/append_record.py`).

---

## 9. POST-COMPUTE DISCLOSURES — FOUR, ALL IN THE AMENDMENT, NONE MOVING A GATE

Four departures were observed after compute. **None alters a gate, threshold,
cap or label.** They are disclosed in the dated amendment appended at the foot of
`PREREGISTRATION.md` **below** its §14 freeze stamp (standing rule 6), and are
listed here only so that a reader of this record is pointed at them rather than
left to find them:

| # | disclosure | why it does not move the verdict |
|---|---|---|
| **(a)** | `REGRADE_RC2.json` carries a **stale hardcoded `status` string**, `"DRAFT/UNFROZEN -- not a registered result until the freeze commit"`, emitted at `regrade_rc2.py:294`. It is **FALSE for this run** | the run executed against freeze `0aa1a049` and the entry's `prereg_commit` cites it. The instrument is **not edited** (rule 6); the amendment is the correction of record |
| **(b)** | §7's registered cap mechanism — *"a wall-clock `timeout 720`"* — was **not in the launch path**; the entry's `launch_cmd` is a bare `python3` | the cap was never at risk (62 s against a 720 s equivalent) and the daemon's own `cap_watch` covered it — but the **registered** mechanism was absent, and that is disclosed, not absorbed |
| **(c)** | §8's claim that the instrument wraps itself in `/usr/bin/time -v` and records MaxRSS is **not implemented** — zero occurrences in either instrument | so `memory_floor_gb = 0.5` remains an **ALLOWANCE** and was not converted into a reading. §8 pre-registers exactly this as an **INFRASTRUCTURE defect, not a refusal** (L-342: a bookkeeping failure invalidates the bookkeeping, never the physics) |
| **(d)** | **`GRADER-FREEZE: UNPINNED`** — the queue entry declares no `grading_freeze` key (`verification/queue/runner.log`, `2026-09-10T03:49:35Z`) | an **ENTRY-level infrastructure gap, NOT a rule-2 gap**: the grading path is fixed by §11 and §14 of the frozen document, and all three files were re-hashed against their committed blobs **before and after** the run and were unchanged. Adding the field post-compute would be a gate-touching change and is **not** done. Reported, not fixed |

---

## 10. WHAT THIS RECORD DOES NOT ESTABLISH

Stated plainly, because an honest gap is worth more than a confident summary:

1. **It does not establish that any of the 16 runs did or did not diverge in the
   physical sense.** The repaired reader answers one question — did this solver
   die on a genuine fatal — and reads `no` on all 16. Physical divergence by
   residual growth is a different question and is not asked here.
2. **It does not sweep the three unscored `results.json` entries** (§3). Sixteen
   of nineteen were re-graded.
3. **It does not adjudicate anything.** Movement is reported; the ruling is the
   closure supervisor's and verification's (§7).
4. **It takes no MaxRSS reading** (§9 (c)); `memory_floor_gb = 0.5` stands as an
   allowance.

---

*Record written after the run, as `PREREGISTRATION.md` §12 registers. Vocabulary:
`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`,
and nothing else. Nothing sent, filed, uploaded, registered, posted or
commented — SUBMISSIONS PARKED.*
