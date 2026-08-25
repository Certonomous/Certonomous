# THERMAL SATURATION QUEUE — second pass, 2026-08-25 20:20–20:35Z

**Written by a heat-transfer lane for the heat-transfer supervisor**, under
Sanaa's 2026-08-25 directive that **cost is no longer a reason to refuse, defer
or stop anything** and that caps are **runaway guards, not budget gates** — with
her rigor clause unchanged and flagged by her twice as *"Very important."*

**This lane launched nothing. Zero core-minutes.** No solver, no mesher, no
`blockMesh`, no comparator, no case directory, no MPI rank. Nothing was sent,
fetched, uploaded or filed outside this box. **The fire order is the
supervisor's alone.**

**Verdict vocabulary is CLAUDE.md rule 1 only.** Where this lane did not check
something itself, it writes **VERIFY** rather than guessing.

---

## 0. THE FOUR HEADLINES, BEFORE THE DETAIL

**1. The premise of this lane's own brief has expired in this lane's favour, and
that is the most important line in this document. `T8` WAS COMMITTED AT 20:25Z,
WHILE THIS LANE WAS WORKING.** Commit `96c2fe3c` landed
`docs/campaigns/T-family/T8_PREREGISTRATION.md` **and** its comparator
`verification/runs/T-family/T8_runs/analyse_t8.py` **in one commit**, so §11's
freeze assertion is true at the moment it binds. **Bucket A is no longer empty.**
T8 is committed, frozen, comparator-complete, worktree byte-identical to the HEAD
blobs, and **unfired** — three single-rank cases available to fire on the
supervisor's word. §2.

**2. K0d IS NOT A SOURCE OF OCCUPANCY AND MUST BE STRUCK FROM THE SCHEDULE.**
The brief handed to this lane says *"K0d, when it fires…"* and asks that thermal
work be queued alongside its decaying occupancy table. **K0d is `BLOCKED` at
HEAD, by the heat-transfer supervisor's own ruling**, and the lane dispatched to
fire it reported `BLOCKED` on two independent stops.
`docs/campaigns/F14-cooling-ladder/K0d_FIRE_RULING_2026-08-25.md` line 4:
*"Verdict: `BLOCKED`. Zero core-minutes spent against a registered POINT of
829.36. K0d remains FROZEN, ARMED, UNFIRED; `K0d_runs/` does not exist."*
Confirmed from disk: **no `K0d_runs` directory exists under either
`verification/runs/F14-cooling-ladder/` or `verification/runs/THERMAL_K0_runs/`.**
**K0d contributes 0 cores at every point on the timeline, not 87.5 % decaying to
31.3 %.** Every occupancy number in the brief that assumes otherwise is too high
by up to nine cores. §3.

**3. THE BOX EMPTIED WHILE THIS LANE WORKED, AND THE GAP IS FAR LARGER THAN THE
BRIEF STATES.** The supervisor's 20:19Z reading was load **7.07** with four
dafoam IPOPT ranks live. At **20:24:33Z** this lane measured load average
**3.91 / 4.98 / 6.19** and **exactly three** CPU-bound processes on the box —
this team's own three T1b L4 EXT2 arms. **No dafoam solver process is visible;
they retired between the two readings.** Thermal occupancy is **3 of 16 =
18.75 %**, and **13 cores are free right now**, not ~7. §1.

**4. THE QUEUE RUNS OUT, AND THIS LANE SAYS SO PLAINLY RATHER THAN STRETCHING
IT.** Even with T8 fired the instant this document is read, peak thermal
occupancy is **6 of 16 = 37.5 %**, reached at t = 0 and falling from t ≈ 7 min.
**Nothing this team may legally fire can reach Sanaa's 80–90 % band today.** The
deficit is **7–8 cores at every point on the timeline.** The binding constraint
is **not cores, not memory and not cost — it is committed pre-registrations**,
and manufacturing those is lane-shift writing work, not compute. §6 names what
this lane would ask Sanaa for.

---

## 1. LIVE BOX READING, TAKEN BY THIS LANE

Measured `2026-08-25T20:24:33.409Z`.

| item | measurement |
|---|---:|
| cores | **16** |
| load average (1 / 5 / 15 min) | **3.91 / 4.98 / 6.19** — decaying |
| `MemAvailable` | **27 GiB** of 30 |
| processes at ≥ 95 % CPU | **3** |
| — all three are `buoyantBoussinesqSimpleFoam` | pids **2203927 / 2203944 / 2203947** |
| **thermal occupancy** | **3 / 16 = 18.75 %** |
| **free cores** | **13** |

**The decaying load average is the corroboration.** A 15-minute average of 6.19
against a 1-minute average of 3.91, with exactly three CPU-bound processes plus
this session, is what a box looks like shortly after a multi-rank job retires. It
is consistent with the supervisor's 7.07 reading five minutes earlier and with
dafoam's four IPOPT ranks having ended in between.

**Memory-per-cell, MEASURED on this box rather than borrowed.** Each EXT2 arm
holds **209,920 cells** (`verification/runs/T-family/T1_runs/R_*_x/log.checkMesh`)
at an RSS of **~500,788 kB**, giving **2.386 kB/cell**. The figure K0d and T8
carry as an estimate — 2.4 kB/cell — is **confirmed as a measurement** to within
0.6 %. This lane offers that as a small positive contribution to the cost
calibration: it was an assumption and it is now a measurement.

### 1.1 What this lane could NOT verify about the box

- **Whether any other team's compute is live but invisible.** `docker ps` is
  denied to this lane's user, so a containerised dafoam job would not appear
  there — though its *processes* would appear in `ps`, and they do not.
  **L-41 stands: a process sweep is blind to fleet agents.** **VERIFY** before
  any launch. Every core this document allocates assumes the other five teams'
  solver occupancy is currently zero; if it is not, the plan overshoots.
- **The three EXT2 arms are NOT to be touched** (brief constraint, honoured).
  They are detached survivors of the fleet kill, mid-run.

### 1.2 The three EXT2 arms — measured progress and measured retirement

Rates derived from each arm's own `log.solve.ext1`, `Time` against
`ExecutionTime`, at the 20:24Z reading. **These are measurements, not estimates.**

| arm | iterations done / `endTime` | measured rate | remaining | **retires in** |
|---|---:|---:|---:|---:|
| `R_100k_x` | 84,370 / 94,000 | 6.158 it/s | 9,630 | **~26 min** |
| `R_300k_x` | 85,819 / 110,000 | 6.264 it/s | 24,181 | **~64 min** |
| `R_10k_x` | 22,758 / 32,000 | 1.661 it/s | 9,242 | **~93 min** |

Registered `timeout` guards are 66,000 / 78,000 / 165,000 s against an elapsed
13,666 s — **no cap is anywhere near binding.**

**Without new work, this team's occupancy reaches ZERO in about 93 minutes.**

---

## 2. TASK 1 — BUCKET A RE-VERIFIED AGAINST HEAD. THE LIST, NOT A NARRATIVE.

Method: every `*PREREGISTRATION*.md` tracked in HEAD under the two campaign
folders was enumerated from `git ls-tree`, each was read for the
`verification/runs/...` path it registers, and that path was checked **on disk**
for a completed run. Two pre-registrations cite no run path in their text; those
were resolved by locating their registered case names on disk instead.

**26 pre-registrations are committed. 25 have run directories holding completed
runs. Two do not, and neither is idle fireable compute.**

| # | pre-registration (committed) | registered run path | run dir on disk? | state |
|---|---|---|---|---|
| 1 | `K0b_D403_RERUN` | `F14/K0b_D403_rerun` | yes | fired |
| 2 | `K0b_D406_REPAIR` | `F14/K0b_D406_repair` | yes | fired |
| 3 | `K0cG` | `F14/K0cG_runs` | yes | fired |
| 4 | `K0cP` | `F14/K0cP_runs` | yes | fired |
| 5 | `K0cQ` | `F14/K0cQ_runs` | yes | fired |
| 6 | `K0cR` | `F14/K0cR_runs` | yes | fired |
| 7 | `K0cS` | *(none cited)* → `F14/K0cS_runs` | yes | fired |
| 8 | `K0cX` | `F14/K0cX_runs` | yes | fired |
| 9 | **`K0d`** | `F14/K0d_runs` | **NO — does not exist** | **`BLOCKED`, see §3** |
| 10 | `K2b_3D_UNSTEADINESS` | *(none cited)* → `F14/K2b_runs/K2bU3_D` | **case built, NEVER RUN** | **pre-registered refusal, see §2.2** |
| 11 | `K2b_UNSTEADINESS` | *(none cited)* → `F14/K2b_runs/K2bU3_*` | yes | fired |
| 12 | `K2e` | *(none cited)* → `F14/K2e_runs` | yes | fired |
| 13 | `E4a` | `T-family/E4_runs` | yes | fired |
| 14 | `E4a2` | `T-family/E4a2_runs` | yes | fired |
| 15 | `T10a` | `T-family/T10a_runs` | yes | fired |
| 16 | `T10aR` | `T-family/T10aR_runs` | yes | fired |
| 17 | `T10aVF` | `T-family/T10aVF_runs` | yes | fired |
| 18 | `T1_FORCED_CONVECTION_CANON` | `T-family/T1_runs` | yes | fired |
| 19 | `T1b_L4_EXT2` | `T-family/T1_runs/R_*_x` | yes | **RUNNING NOW** |
| 20 | `T1b_L4_PLANTED_ZERO_CONTROL` | `T-family/T1_runs` | yes | fired |
| 21 | `T3` | `T-family/T3_runs` | yes | fired |
| 22 | `T9a` | `T-family/T9a_runs` | yes | fired |
| 23 | `T9aD` | `T-family/T9a_runs` under prefix `D_` | yes — `D_A_*`, `D_B_x`, `D_C_*`, `D_R_f` + `DONE.`/`STATUS.` markers | fired |
| 24 | `T9aH` | `T-family/T9aH_runs` | yes | fired |
| 25 | `T5_PREREGISTRATION_DRAFT` | `T-family/T5_runs` | no | **a DRAFT, not a pre-registration** — §5 |
| 26 | `T8_PREREGISTRATION_DRAFT` | `T-family/T8_runs` | superseded | superseded by the real T8, below |
| **27** | **`T8_PREREGISTRATION`** — **committed 20:25Z, commit `96c2fe3c`, AFTER the HEAD this lane was given** | `T-family/T8_runs` | **NO CASE DIRS — UNFIRED** | **BUCKET A. FIREABLE.** |

**`T9aD` was the one genuine near-miss and it resolves cleanly.** There is no
`T9aD_runs` directory, which looks like unrun compute; it is not. The
pre-registration registers, at its own lines 9–10, that the arm runs inside
`verification/runs/T-family/T9a_runs/` **under the prefix `D_`**, following T1c's
diagnostic precedent. Those case directories and their `DONE.`/`STATUS.` markers
are on disk, and `T9aD_RESULTS.md` grades seven rows (3 PASS, 1 GATE FAIL,
3 NOT A RESULT). **Fired.**

### 2.1 THE ONE FIREABLE ITEM, WITH ITS FREEZE VERIFIED BY THIS LANE

**T8 — MTT pure-plume entry rung. DC spine position 3. `BUCKET A`.**

Freeze verified by hashing each worktree file against its HEAD blob directly
(**not** by `git diff`, which reads stale under concurrency):

| file | HEAD blob | worktree |
|---|---|---|
| `docs/campaigns/T-family/T8_PREREGISTRATION.md` | `dd008248f60c2fa351d103f3be199d9e660e36d0` | **identical** |
| `verification/runs/T-family/T8_runs/analyse_t8.py` | `d82c98ae2caf5cf2eb1c01140061cc92295ea82b` | **identical** |
| `verification/runs/T-family/T8_runs/build_t8.py` | `376a41da268c7a97e59cb284f77ec54027652992` | **identical** |
| `verification/runs/T-family/T8_runs/run_one_t8.sh` | `70a37aa634d60473101d0bc6ab98ae5a6cec7c59` | **identical** |

**The blocker the previous queue named is closed.** `analyse_t8.py` did not exist
anywhere on this box when that document was written; it exists now, 84,817 bytes,
and it was committed **in the same commit** as the pre-registration — which is
exactly what rule 2 requires, because committing the document alone would have
frozen a false §11 freeze condition and fixed the grading path onto a file that
did not exist.

**No case directory of any kind exists in `T8_runs/`** — only the three scripts
and a `__pycache__`. The freeze condition's *"zero core-minutes have been spent
on this rung"* is **true as measured on disk.**

Registered numbers, read off `T8_PREREGISTRATION.md` §8 and §6:

| case | cells | `endTime` | **ranks** | POINT core-min | registered cap | `timeout = cap×60÷ranks` | measured-basis RSS |
|---|---:|---:|---:|---:|---:|---:|---:|
| `T8_MTT_c` | 6,400 | 8,000 | **1** | **7.13** | 15 | 900 s | ~75 MB |
| `T8_MTT_m` | 25,600 | 12,000 | **1** | **42.81** | 80 | 4,800 s | ~121 MB |
| `T8_MTT_f` | 102,400 | 20,000 | **1** | **285.40** | 500 | 30,000 s | ~304 MB |
| **total** | | | **3 cores** | **335.34** | **595** | | **~0.50 GB** |

**Derived, not measured:** POINT 335.34 core-min = 5.589 core-h = **$0.287**;
cap 595 core-min = 9.917 core-h = **$0.509**, at the recorded
c7a.4xlarge rate $0.0513/core-h. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so these are **derived, not measured**.
**Under Sanaa's directive these caps are runaway guards, not budget gates.**

**Reference tier: partial EXACT.** Morton–Taylor–Turner plume theory is closed
form. **There is no acquisition step and nothing is blocked on a paper.**

**Registered misprediction exposure, carried forward and not smoothed over
(prereg R6):** the rate `1.196e5 cell·steps/(core·s)` is borrowed from
`K2bU3_L025`, a **transient PIMPLE** case, while T8 is **steady SIMPLE-family**.
The arithmetic is exact; the *rate* is the exposure, and the direction of the
error is not predicted. **At completion this must be attributed as
`misprediction` in the `docs/COST_CALIBRATION.md` row, never absorbed into the
ratio** (rule 12; `COMPUTE_BUDGET_CHARTER.md` §6).

### 2.2 `K2bU3_D` — built, never run, and that is CORRECT, not idle compute

`verification/runs/F14-cooling-ladder/K2b_runs/K2bU3_D/` holds only `0.orig/`,
`CASE.txt`, `constant/` and `system/` — **no time directories, no logs, no
`0/`.** On its face this is a committed pre-registration with unrun compute,
which is exactly what the brief asked this lane to hunt for. **It is not.**

`docs/campaigns/F14-cooling-ladder/K2bU_TIERING_DETERMINATION_2026-08-25.md:44`
records it as *"NEVER RUN, BY REGISTERED DESIGN"*, and its §4 heading reads
*"`K2bU3_D` never ran, and its absence is a pre-registered refusal."* The
control gate that had to pass before the 3D test could mean anything did not
pass, so the test was correctly not run. **The absence of `K2bU3_D/0` is the
instrument working, not compute sitting idle. Firing it would break the
registered gate order.** Reported so nobody later reads the empty directory as an
opportunity.

---

## 3. K0d — STRUCK FROM THE SCHEDULE, WITH THE RULING QUOTED

This is the single largest correction this lane has to make to its own brief.

`docs/campaigns/F14-cooling-ladder/K0d_FIRE_RULING_2026-08-25.md` is **committed
at HEAD**, is authored by the heat-transfer supervisor, and is titled
*"K0d — RULING: NOT FIT TO FIRE. Stop amending; re-register."* Its verdict line:

> **Verdict: `BLOCKED`.** Zero core-minutes spent against a registered POINT of
> 829.36. K0d remains **FROZEN, ARMED, UNFIRED**; `K0d_runs/` does not exist.

The blocker is **not** cost and is therefore **untouched by Sanaa's directive**:
the case's defining parameter is **over-determined**, and two of K0d's own
amendments reconcile it differently. §1 of the ruling tabulates four
`(ν, β)` pairings giving `Ra` of 2.18866e9, 2.13597e9, 2.13000e9 and 2.07873e9
against a registered `Ra = 2.13e9` — a spread of **+2.76 % to −2.41 %**. The
lane dispatched to fire it reported `BLOCKED` on **two independent stops**, both
pre-committed by the supervisor in the dispatching brief, and
`K0d_LANE_REPORT_FIRE.md` records that repairing either one alone still leaves
the other standing.

**Consequences for the schedule, stated plainly:**

- **K0d supplies 0 cores, now and for the whole 24 h window.** Its registered
  §9.3 occupancy table (87.5 % → 31.3 %, mean 62 %) describes a run that has not
  started and, at HEAD, may not start.
- **The gap this lane was asked to backfill is not a decay from 87.5 %. It is a
  floor of 18.75 % falling to 0 % within 93 minutes.**
- **K0d's ceiling is unchanged and is not softened here.** Blay, Mergui &
  Niculae (1992) is `NOT OBTAINED` — independently re-confirmed at §4.3 below.
  Even repaired and fired, K0d can earn **V** and **G** and **cannot earn P**,
  and therefore **cannot be tiered `HOLDS`**.
- **Re-registration is the route out and it is document work, not compute.**

---

## 4. TASKS 2, 3 AND 4 — AND A PROCESS FINDING THE SUPERVISOR NEEDS FIRST

### 4.0 THE PROCESS FINDING: THIS WORK WAS ALREADY DONE, AND IT IS INVISIBLE FROM HEAD

`docs/campaigns/T-family/THERMAL_REFERENCE_TITLE_PAGE_AUDIT.md` — **503 lines,
on disk, NOT COMMITTED.** A previous heat-transfer lane discharged tasks 2, 3 and
4 of this lane's brief in full earlier today. The supervisor's brief was written
as though none of it had happened, which is the expected outcome: **the
supervisor reads from HEAD, and this document is not in HEAD.**

**This lane did not commit it.** It is another lane's work, that lane may still
be live, and committing it would put a foreign row under this lane's message and
risk a duplicate. **It is flagged here so somebody can be dispatched to land it**
(rule 10: say in the message if you left foreign rows uncommitted).

**This lane therefore did not relay that document's conclusions. It re-derived
the load-bearing ones independently**, because a relayed check is a summary, not
a check. Where this lane's own measurement agrees, it says so; where it differs,
it says that too.

### 4.1 TASK 2 — T12 / Nielsen 2010: TITLE PAGE VERIFIED BY THIS LANE. **T12 STAYS `BLOCKED`.**

**The rule-15 verification, done by rendering page 1 at 150 dpi and reading the
rendered page** — never by filename, file type or hash (L-144).

`docs/papers/data_center_indoor_airflow/nielsen_rong_olmedo_2010_clima_annex20.pdf`,
457,435 bytes, 9 pages. Page 1 is a bare cover leaf carrying, centre-page, in
this order **as printed**:

- **Authors:** Peter V. Nielsen, Li Rong and Inés Olmedo
- **Title:** *The IEA Annex 20 Two-Dimensional Benchmark Test for CFD Predictions*
- **ISBN:** 978-975-6907-14-6
- **Venue:** Clima 2010, 10ᵗʰ REHVA World Congress

**Verdict: rule-15 title-page verification `VERIFIED`.** All six filename tokens
— `nielsen` / `rong` / `olmedo` / `2010` / `clima` / `annex20` — match the
printed page. No contradiction with the filename or with any citation of it.

**And this file is a textbook L-144 case that vindicates the rule.** Its embedded
PDF metadata reads `Title: Microsoft Word - 100128 Full paper.doc`,
`Author: pvn`. **A manifest built from metadata would have recorded this paper's
title as a Word filename and its author as "pvn".** The rendered page is the
paper.

**BUT THE UNBLOCK DOES NOT FOLLOW, AND THIS IS THE ANSWER TO THE TASK.** The
brief's hypothesis was that a verified title page would move spine position 4
from `ACQUIRE` to armable. **The title page verified and T12 is still `BLOCKED`,
because the title page was never the blocker.** Three findings, each measured by
this lane:

1. **The paper is a pointer to the data, not the data.** Its own sidecar line 69
   reads *"The benchmark is located together with three other benchmarks on the
   web page:"* followed at line 71 by `www.cfd-benchmarks.com`, and line 195
   states *"The benchmark is defined on a web page."* **The measurements live off
   this box. Obtaining them is a fetch, and a fetch is Sanaa's alone (rules 7 and
   8). This lane attempted nothing.**
2. **The measurement primaries it points at are not held.** Its printed reference
   list names Nielsen 1990 (*Specification of a Two-Dimensional Test Case*,
   Aalborg, IEA Annex 20), Restivo 1979 (PhD, Imperial College) and Schwenke 1975
   (Luft- und Kältetechnik, Dresden). **A filename sweep over all four data roots
   returns zero PDFs matching `restivo` or `schwenke`; the same instrument
   matching `nielsen` returns 1** — the reader was shown able to see a non-zero
   before its zero was believed (rule 3).
3. **The paper states no measurement uncertainty, and a graded row needs one.**
   `grep -c -iE 'uncertain|accuracy'` on the Nielsen sidecar returns **0**; the
   **same binary with the same flags** on the Narumanchi sidecar returns **3**.
   **Planted control satisfied.**

**Verdict: T12 `BLOCKED` on both limbs. The record is NOT stale.** The
isothermal limb is blocked on Nielsen 1990 / Restivo 1979, the nonisothermal limb
on Schwenke 1975, and none of the three is on this box. **This lane's independent
reading agrees with the uncommitted audit's §3.** The index's `ACQUIRE, over $25`
cell is untouched by anything here — and note that **the "over $25" half is now
irrelevant under Sanaa's directive, while the acquisition half is not, because
acquiring is a send and sends are parked.**

**What T12 would then need to become fireable:** Sanaa's decision to obtain
Nielsen 1990 and Restivo 1979 (isothermal) and Schwenke 1975 (nonisothermal), or
to authorise a fetch from `www.cfd-benchmarks.com`. **That is a send. It is
reserved to her and this lane neither did it nor proposes that anyone else do
it.**

### 4.2 TASK 3 — THE TITLE-PAGE AUDIT: the count, established from disk

**The brief's claim — "only three PDFs in the whole repository carry a
title-page verification record, and Ampofo, Betts/ERCOFTAC 079 and Nielsen carry
none" — is HALF TRUE, and the half that is false is the reassuring half.**

- **The narrow half was true and is now discharged.** Ampofo, Betts and Nielsen
  carried no rule-15 record. All three have now been read. **Nielsen was read by
  this lane (§4.1). Ampofo and Betts were read by the previous lane and are
  recorded in the uncommitted audit §2.1–§2.2** — this lane did **not**
  re-render those two and marks them **VERIFY** on that lane's record rather
  than asserting them as its own measurement.
- **The broad half was false.** Title-page verification records exist elsewhere
  in the repository — Roshko (1954) NACA Report 1191 at
  `docs/EXTERNAL_REFERENT_AUDIT.md:930`; Greenblatt et al. AIAA-2004-2220 and
  Breuer et al. *Computers & Fluids* 38 (2009) at
  `verification/campaign/MATRIX_CONTRIBUTION.md` §11.2–§11.3; and the Ansys
  Verification Manual per `docs/ansys_verification/README.md`. **VERIFY** — this
  lane read the audit's citations rather than re-opening each record.

**The number the supervisor actually wants, and it is worse than three.** Of
**19 thermal PDFs across the three thermal paper folders, 6 now carry a rule-15
record and 13 do not.** A check never made is `NOT VERIFIED`, never a clean
result. **Zero thermal PDFs have ever FAILED.**

**Two of the thirteen are load-bearing today, and this is the exposure the family
should be least comfortable with:**

| paper | why it is load-bearing |
|---|---|
| **`tian_karayiannis_2000_ijhmt_43`** | Part II is `NOT OBTAINED`, which is why every K0cS turbulence statistic is single-source. **Part I is held here and has never been title-page verified.** |
| **`wibron_ljung_lundstrom_2018_en11030644`** | **K2c-A digitised Figs 6a/6b and 7a–7e off this PDF.** Its sha256 matches the manifest exactly — **and rule 15 says a hash is not verification.** The K2c digitisation rests on a hash-matched, title-page-unverified document. |

**Each is one reading and zero core-minutes to settle. Neither was settled here**
— this lane's brief named T12's paper and this lane read that one rather than
silently widening its own scope. **Recommended as the next zero-compute
dispatch**, ranked above any further queue-building, because a P column resting
on an unverified PDF is a claim the lab has not earned.

**A precision worth carrying, on "ERCOFTAC 079".** The citation names **two
artifacts, not one**: the Betts & Bokhari journal paper, to which rule 15
applies; and the 22 `.dat` files of the ERCOFTAC Case 079 archive, **to which
rule 15's title-page test cannot literally be applied**, since a data archive has
no title page. Recorded so nobody later reads "ERCOFTAC 079 is rule-15 verified"
and believes a data archive was title-page checked.

### 4.3 TASK 4 — T2 / ZUKAUSKAS: THE NUMBER, RE-DERIVED BY THIS LANE. **The evidence, not a ruling.**

**Sweep run by this lane**, using `find … -print0 | xargs -0 grep` over all four
data roots — **not** `grep -r`, which honours ignore files here and is blind to
gitignored archives.

| sweep | corpus | **hits** |
|---|---|---:|
| `zukausk` \| `zhukausk` \| `ukausk`, case-insensitive | 4 roots, `.txt`/`.md`/`.dat`/`.csv`/`.json` | **5 files** |
| same pattern | **the 96 sidecars in `docs/papers/`** | **0** |
| **planted control** `nusselt`, same binary, same flags | **the same 96-sidecar corpus** | **13** |
| **planted control** `gnielinski`, same instrument | 4 roots | **11** |

**The zero is believed only because the same reader on the same corpus returned
13 (rule 3).** The `ukausk` variant was included deliberately so that a
non-ASCII initial `Ž`, which `-i` does not fold, could not hide a hit.

**All 5 hits are lab prose — the lab talking about the missing correlation, never
the correlation itself:** `docs/LAB_STATE.md`,
`docs/campaigns/T-family/T_FAMILY_INDEX.md`,
`docs/campaigns/T-family/MATRIX_CONTRIBUTION.md`,
`docs/campaigns/T-family/THERMAL_SATURATION_QUEUE.md`, and the uncommitted audit
itself.

**The number the supervisor asked for: ZERO hits across 96 sidecars, against a
planted control of 13 on the same corpus.**

**Why it bears on the tier, stated as evidence and not as a ruling.**
`T_FAMILY_INDEX.md:42` records T2 as tier `FORMULA` and its own state cell
requires *"the correlation's **stated validity range** cited, not just its
algebra."* **Neither half is on disk — not the algebra, not the range.** Algebra
with no stated validity range arms no band, which is the identical defect that
blocks T1a/K0e, where a **held and title-page-verified** correlation still cannot
arm a band on its own.

**THE TIER IS NOT EDITED BY THIS LANE. An over-claimed tier is the supervisor's
ruling.** The evidence is above; the call is the supervisor's.

---

## 5. TASK 5 — THE QUEUE, RANKED AND COSTED

### 5.1 What may fire in the next 24 h — the honest list

**Row 1 is the only row that may fire today. Everything below it needs a
document first, and a document is not compute.**

| rank | rung | pre-registration committed? | comparator exists? | reference obtained + title-page verified? | ranks | est. core-min | derived $ |
|---:|---|---|---|---|---:|---:|---:|
| **1** | **T8** `_c`/`_m`/`_f` | **YES** — `96c2fe3c`, blob `dd008248…` | **YES** — `analyse_t8.py`, blob `d82c98ae…`, same commit | **N/A — MTT is closed form, EXACT, no acquisition** | **1 each = 3** | **335.34 POINT / 595 cap** | **$0.287 / $0.509** |
| 2 | T3 fourth mesh level (`R_m`/`R_f`/`R_ff`) | **NO** — needs its own costed prereg | reuses `analyse_t3.py` **VERIFY** | Vogel & Eaton 1985 `NOT OBTAINED` → **cannot reach P** | 1 each = 3 | **9,000–12,000** | $7.70–$10.26 |
| 3 | T5 heated cubes | **NO** — committed only as a **DRAFT**, blob `d56018d1…`. Its line 5 says it freezes on Sanaa's reading **or on the supervisor's promotion** → **the supervisor can promote it** | **VERIFY** | **YES** — Meinders 1998, title page verified by eye, sidecar OCR-remediated to 501,467 chars | **4 / 4 / 8** | ~1,300–2,900 **VERIFY** | ~$1.1–$2.5 |
| 4 | T11 transient conjugate entry arm | **NO — no document of any kind exists.** Confirmed: no `T11_*` file anywhere in the repo | **NO** | **N/A — lumped and 1D transient are closed form, EXACT, no acquisition** | 1 each = 3 | ~300–600 **VERIFY** | ~$0.26–$0.51 |
| 5 | T4 impinging jet, **flow rows only** | **NO** | **NO** | **partial YES** — ERCOFTAC case025 held; Martin correlation from Narumanchi 2005, title page verified. **`Nu` rows rest on a second-hand 2.4 % uncertainty and cannot reach P** | **VERIFY** | **VERIFY** | — |
| — | **K0d** | committed | registered | Blay 1992 `NOT OBTAINED` | — | **0 — `BLOCKED`, §3** | — |
| — | T12 | no | no | **`BLOCKED` — §4.1** | — | 0 | — |
| — | T2 | no | no | **`BLOCKED` — §4.3, zero of 96 sidecars** | — | 0 | — |

### 5.2 Occupancy over time, with K0d correctly at zero

Assumptions stated so they can be checked: background non-thermal occupancy **0**
(measured at 20:24Z, **VERIFY** per §1.1); 1 core left unallocated for this
session, git and the instruments; EXT2 retirements from the **measured** rates in
§1.2; T8 durations from its §8 POINT lines, where `ranks = 1` makes core-minutes
and wall-minutes numerically coincide.

| t (min) | event | thermal cases live | **cores / 16** | **utilisation** | vs 80–90 % band |
|---:|---|---|---:|---:|---|
| **0** | **fire all three T8 cases at once** — 13 cores are free, so **no staging is required** | 3 EXT2 + 3 T8 | **6** | **37.5 %** | **−7 cores** |
| ~7 | `T8_MTT_c` retires | 3 EXT2 + 2 T8 | 5 | 31.3 % | −8 |
| ~26 | `R_100k_x` retires | 2 EXT2 + 2 T8 | 4 | 25.0 % | −9 |
| ~43 | `T8_MTT_m` retires | 2 EXT2 + 1 T8 | 3 | 18.8 % | −10 |
| ~64 | `R_300k_x` retires | 1 EXT2 + 1 T8 | 2 | 12.5 % | −11 |
| ~93 | `R_10k_x` retires | 1 T8 | **1** | **6.3 %** | −12 |
| ~285 | `T8_MTT_f` retires | none | **0** | **0 %** | −13 |

**Peak is 37.5 %, at t = 0, and it only falls.** T8 is a **long pole, not a wide
one** — it buys one warm core for 4.8 hours, not a batch.

**The band is not reachable today by any legal means available to this team.**
Stated without softening, because the alternative is to write a schedule that
implies otherwise.

### 5.3 The memory guard

**Memory is not the binding constraint and this lane says so with a
measurement rather than by omission.**

- **Per-cell RSS: 2.386 kB/cell, MEASURED** on this box at 20:24Z from the three
  live EXT2 arms (209,920 cells at ~500,788 kB RSS), plus a baseline of ~60 MB
  per process.
- **T8 resident estimate: ~75 / ~121 / ~304 MB, ~0.50 GB for all three.**
- **`MemAvailable` is 27 GiB.** Firing all of T8 leaves ~26.5 GiB.
- **Free-memory floor below which a launch HOLDS: `MemAvailable` < 12 GiB**, this
  family's standing floor. **Current headroom above the floor is 15 GiB.**
- **Even 13 concurrent single-rank cases at these mesh sizes would add ~6.5 GB**,
  leaving `MemAvailable` ≈ 20 GiB — still 8 GiB clear of the floor. **At T-family
  mesh sizes the box runs out of cores long before it runs out of memory.**
- **The re-read is not optional.** `MemAvailable` must be re-read immediately
  before each launch, because the binding memory risk is **not this team**: a
  dafoam container capped at `--memory=12g` restarting would make the floor the
  constraint rather than the cores. **A batch that OOMs is worse than a batch that
  queues.**

### 5.4 The measurement-integrity constraint, preserved as the supervisor required

**This survives Sanaa's directive because it is a MEASUREMENT argument, not a
cost argument**, and this lane preserves it rather than quietly dropping it now
that cost is off the table.

Piling solvers onto already-saturated cores inflates wall-clock and corrupts the
timing basis every cost calibration depends on. **The specific hazard, which is
not obvious:** T8's cap is enforced as a wall-clock `timeout`, admissible **only**
because `ranks = 1` makes core-minutes and wall-seconds coincide. **Under
contention wall inflates and core-minutes do not**, so a heavily contended case
can be killed by its timeout while still under its core-minute cap — and a level
killed by its cap is `PENDING`, a right-censored measurement, never `GATE FAIL`.

**How much headroom there genuinely is right now: 13 free cores.** At 3 T8 cases
the box goes to 6 of 16 — **nowhere near saturation, so the timing basis stays
clean and T8's calibration row will be worth having.** `T8_MTT_f` at 11 %
contention would need 316.8 core-min ≈ 19,008 s against a 30,000 s timeout —
**1.58× of headroom.** **No core reservation is needed for T8.**

**Stage into the headroom, do not oversubscribe it.** The rule this lane would
hand forward: **never let total CPU-bound processes exceed 14 of 16**, and **any
future rung whose cap instrument is wall-clock at `ranks > 1` inherits the hazard
above without the numerical coincidence that makes it admissible** —
`timeout = cap_core_min × 60 ÷ ranks` must be coded as that identity, never as a
copied literal.

**T5 is the one queued rung that will need reserved cores when it fires.** Its
§11 cost model assumes **parallel efficiency 0.85 on 4 ranks (`scotch`)`.` That
0.85 is an assumption, not a measurement**, and measuring it under contention
measures contention instead. **T5 should reserve its ranks and say so, or
register explicitly that the efficiency figure is unmeasurable in that window.**

---

## 6. TASK 6 — THE QUEUE RUNS OUT. WHAT THIS LANE WOULD ASK SANAA FOR.

**Said plainly, because stretching a queue to look busy is the opposite of what
she asked for: after T8, this team has nothing it may legally fire.** Total
legally fireable thermal compute in the next 24 h is **three single-rank cases,
335 core-minutes POINT, 3 of 16 cores** — and the box has 13 free.

**The bottleneck is not cores, not memory, and — since her directive — not cost.
It is committed pre-registrations, and rule 2 makes that non-negotiable: the gate
is frozen before the solver starts.** Thermal cannot spend its way out of this
and cannot fire its way out of it. **It can only write its way out of it.**

**What this lane would ask her for, in priority order:**

1. **Lane-shifts for pre-registration writing, not compute.** Four documents
   stand between this team and a full box: the **T3 fourth-mesh-level** prereg
   (the only item in the inventory large enough to hold cores for *days* —
   9,000–12,000 core-min), a **T11 EXACT entry-rung** prereg (cheapest new
   compute on the board, no acquisition step, no document exists yet), a **T4
   flow-rows** prereg, and a **K0d re-registration** that resolves the
   over-determined `Ra`. **This is the single highest-value thing she can direct.**
   Three lanes writing in parallel would convert ~10 cores of work within a shift.
2. **A decision on the five missing primaries — each is a send, and sends are
   hers alone.** **Blay 1992** (K0d's P column; `K0d_PREREGISTRATION.md:17-18`
   already records that *she has purchased the ASME volume and the PDF is not yet
   on disk* — **this may be the cheapest P column on the board to close, and it
   needs no money, only the file**); **Vogel & Eaton 1985** (T3); **Nielsen 1990 /
   Restivo 1979 / Schwenke 1975** or a `www.cfd-benchmarks.com` fetch (T12); a
   **Zukauskas source stating its validity range** (T2); **Tian & Karayiannis
   Part II** (K0cS's single-source caveat). **This lane attempted none of them
   and proposes no route around rule 7.**
3. **Her offer of more cases, taken up specifically.** The T-family and the DC
   spine are **reference-starved, not compute-starved.** The most useful new work
   she could hand this team is **rungs whose reference is closed-form or already
   on disk** — the T1c/T8/T11 shape, which graded a rung the whole class was
   recorded as blocked on. **A new rung needing an unobtainable paper adds a
   document and zero core-minutes.**

**And the one thing that needs no permission at all:** the **two load-bearing
unverified PDFs** in §4.2. Tian & Karayiannis Part I and Wibron 2018 are each
**one reading and zero core-minutes**, and the K2c digitisation currently rests
on a document nobody in this lab has opened the title page of.

---

## 7. WHAT THIS LANE COULD NOT VERIFY

1. **Other teams' live occupancy.** `docker ps` is denied to this user, and
   **L-41** says a process sweep is blind to fleet agents. No non-thermal solver
   process was visible at 20:24Z. **VERIFY before any launch** — the whole §5.2
   schedule assumes their occupancy is zero.
2. **Ampofo and Betts title pages.** Recorded as VERIFIED in the **uncommitted**
   `THERMAL_REFERENCE_TITLE_PAGE_AUDIT.md` §2.1–§2.2. **This lane did not
   re-render them** and marks them **VERIFY** on that lane's record. Nielsen
   (§4.1) this lane read itself.
3. **The repo-wide title-page record count.** §4.2's counter-examples are cited
   from that audit, not re-opened here. **VERIFY.**
4. **Whether `analyse_t3.py` can serve T3's fourth mesh level unmodified.**
   **VERIFY.** Note the registered defect carried in T8's prereg: `analyse_t3.py:384`
   and `analyse_t1c.py:337` both compute the **inverted** Richardson form
   `f_fine + e21/den`, survivable only because it is display-only there.
5. **T5's and T11's core-minute figures in §5.1** are this lane's rough bounds,
   not registered numbers. **VERIFY** — neither has a costed pre-registration,
   which is precisely why neither may fire.
6. **The Blay 1992 absence** rests partly on a filename exclusion for 76
   unsidecared PDFs, and rule 15 says a filename is not verification. **`NOT
   OBTAINED` on strong evidence; not proven to rule 15's positive standard.**
7. **Whether T8's borrowed PIMPLE-derived rate holds for a steady SIMPLE run** —
   registered as exposure R6, direction of error not predicted. It will be
   measured when T8 completes and must be attributed as **misprediction**.

---

## 8. COST OF THIS DOCUMENT, AND WHAT THIS DOCUMENT DOES NOT DO

**Pre-registered: ZERO core-minutes. Actual: ZERO core-minutes. Ratio 1.00.**
No solver, no mesher, no case directory, no MPI rank, no GPU. The work was PDF
page rendering, `find`/`grep` sweeps, blob hashing and reading. **Derived dollar
cost $0.00 — derived, not measured**, because the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **No row is added to
`docs/COST_CALIBRATION.md`:** there is no compute row to calibrate, and a
calibration row built from an invented baseline is worse than an absent one.

- **It launches nothing and authorises nothing.** Every fire order is the
  supervisor's.
- **It creates, moves and retires no gate, threshold, band, cap or label**, and
  it does not edit T2's tier, T12's cell or any verdict.
- **It edits no frozen document.** The K0d and T8 figures quoted above sit
  **beside** the frozen text, never in place of it. No amendment was appended to
  anything.
- **It did not commit another lane's uncommitted audit** (§4.0), flagged so
  somebody can be dispatched to land it.
- **It sends nothing. SUBMISSIONS REMAIN PARKED** (rule 7). Acquiring Blay 1992,
  Vogel & Eaton 1985, Nielsen 1990, Restivo 1979, Schwenke 1975, a Zukauskas
  source or Tian & Karayiannis Part II is a **send**, and sending is Sanaa's
  alone.
- **No agent's message was treated as Sanaa's consent** (rule 9).

---

*Written by a heat-transfer lane, 2026-08-25. Zero core-minutes. No solver ran,
no gate was graded, no tier or verdict was edited, nothing was acquired from
outside the box, and nothing was sent, filed or submitted.*
