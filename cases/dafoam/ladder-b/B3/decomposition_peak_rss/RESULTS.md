# B3 decomposition chain — PEAK RSS, measured: RESULTS

**DRAFT — NOT COMMITTED.** With the dafoam supervisor for a personal read before any verdict is
recorded. Nothing here is filed, sent, uploaded, registered, posted or pushed.

Attempt 2, run 2026-08-23, under registration **`d062aace`** and the supervisor's **Addendum 3**
ruling (`5edfe8c0`) authorising one repair exception via `VERIFICATION_CHARTER.md` §2d.1.
Run root **`/home/ubuntu/certonomous-runs/B3-decomposition-peakrss/`**.

Every dollar figure below is **derived at an owner-stated rate, never measured** — this box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

---

## 1. The graded table, as the frozen grader printed it

`analyse_peak_rss.py` sha256 re-hashed **immediately before grading** and equal to the value frozen
at §4 of the pre-registration: `c4db08fcf7a3e5d23327943d9093feb3b5983ec655083f50a103e30f9c6951eb`.
Grader exit **3** (a graded row is GATE FAIL) — **not** exit 2, so it graded rather than refused.

| row | quantity | value | band | **verdict** |
|---|---|---|---|---|
| **M0** | re-run reproduces every archived digit of the graded arm | 18 of 18 checks true | all identical | **PASS** |
| **M2a** | `D_simple2` peak tree RSS | **9.719 GiB** | 6.0 – 11.0 | **PASS** |
| **M2b** | `D_simple2` cgroup `memory.peak` | **8.000107 GiB** (8,590,049,280 B) | 8.0 – 12.0 | **PASS — by 114,688 B, flagged §1** |
| **M3a** | `D_serial` peak tree RSS | **11.503 GiB** | 5.5 – 9.0 | **GATE FAIL** |
| **M3b** | `D_serial` cgroup `memory.peak` | **11.133 GiB** | 6.0 – 11.0 | **GATE FAIL** |
| **M4** | peak(np=4) > peak(np=1) on **both** instruments | 8.000 vs 11.133; 9.719 vs 11.503 | strictly greater | **GATE FAIL** |
| **M5** | rc=0 both arms; `memory.peak` strictly below 12 GiB; no watcher abort; gap <= 5 s; >= 30 samples | all true | all | **PASS** |

**M0 PASS is what makes the rest of this file a measurement about the graded rows** rather than
about two new runs. Every band row grades normally because identity held; had it failed, the frozen
grader would have turned every row into `NOT A RESULT` and it did not.

Exact bytes, so nothing rests on a rounded GiB:

| arm | `memory.peak` bytes | GiB | peak tree RSS GiB | samples | max gap |
|---|---|---|---|---|---|
| `D_serial` | **11,954,151,424** | 11.133171 | 11.503178 | 581 | 3.0 s |
| `D_simple2` | **8,590,049,280** | 8.000107 | 9.718891 | 157 | 3.0 s |

**FLAGGED — `M2b` passes by 114,688 bytes.** The 8.0 GiB band floor is exactly 8,589,934,592 B; the
arm measured 8,590,049,280 B. The margin is **114,688 B = 112.0 KiB = 0.000107 GiB**, stated in
bytes rather than rounded to a comfortable "8.0, inside", because at this margin the rounded figure
and the band edge are the same number and a reader could not otherwise tell a PASS from a tie.

The band was frozen at `d062aace` before any container ran and **it is not adjusted now**, in either
direction: this row is a `PASS` on the registered arithmetic. But it is a PASS by 0.0013 % of the
band floor, and **it should not be relied on as evidence that `D_simple2`'s peak is comfortably
inside the registered range** — it is evidence that the peak sits essentially *on* the lower edge of
a band this lab set wide precisely because it had never taken this measurement before (§5.2).

---

## 2. The product of the item: the hole in `decomposition_np4/RESULTS.md` is filled

That record's §5/§9 said of `D_serial`: *"6.156 GiB is a `docker stats` sample taken during the
linear solve, **not a true peak** … the exact peak is **NOT MEASURED**."*

**It is now measured, on an instrument that was shown able to see a peak before it was believed.**

| arm | figure previously on the record | instrument | **measured here** | ratio |
|---|---|---|---|---|
| `D_serial` | 6.156 GiB (`decomposition_np4/RESULTS.md:132`) | one mid-solve `docker stats` sample | **11.133 GiB** `memory.peak`, **11.503 GiB** tree RSS | **1.81x / 1.87x** |
| `D_simple2` | none — never measured | — | **8.000 GiB** `memory.peak`, **9.719 GiB** tree RSS | — |

The recorded 6.156 GiB figure was an **undersample by a factor of 1.81**. The honest statement in
that record — *"the cap was never approached at any moment observed"* — was correct about what it
observed and wrong as a description of the arm: the arm reached **92.8 % of its 12 GiB cap**.

### 2.1 The prediction that was written off as a miss was right, and the instrument was wrong

`decomposition_np4/PREREGISTRATION.md:69` predicted `D_serial` at **10–14 GiB** from an offline
`splu` factorisation basis. §5.1 of this item's own pre-registration listed that basis as **"the
basis that missed high last time"**, because it stood against a 6.156 GiB sample.

**Both measured `D_serial` numbers land inside 10–14 GiB** (11.133 and 11.503). The 10–14 GiB
prediction did not miss. **The measurement it was judged against did.** This is recorded here
against this lane's own interest: this item's §5.1 wrote that basis down as a miss, and the item's
own result refutes its own characterisation.

---

## 3. M4 — the registered falsifiable claim is FALSIFIED

§5.2 registered M4 as *"the falsifiable claim in the item"*, and registered in advance what its
failure would mean: *"if the serial LU is the larger object, M4 fails and the 'np=1 is the arm at
risk' reasoning of `decomposition_np4/PREREGISTRATION.md:69` is vindicated a run too late."*

**M4 is GATE FAIL, and it fails in that exact direction, on both instruments and by a wide margin:**

| instrument | np=4 (`D_simple2`) | np=1 (`D_serial`) | registered claim | outcome |
|---|---|---|---|---|
| `memory.peak` | 8.000 GiB | **11.133 GiB** | np=4 > np=1 | **false by 3.133 GiB** |
| tree RSS | 9.719 GiB | **11.503 GiB** | np=4 > np=1 | **false by 1.784 GiB** |

**Per-process attribution — the number no container-level instrument can produce**, and the reason
`VmHWM` was registered at §4.1:

| arm | processes at the peak sample | reading |
|---|---|---|
| `D_serial` | one `python` (pid 1201781) at **`VmHWM` 11.487 GiB**, plus `mpirun` 13 MB and `bash` 4 MB | **one process holds essentially the whole peak** — one whole-matrix LU over the 210,592² operator |
| `D_simple2` | four `python` ranks at 2.384 / 2.452 / 2.452 / 2.414 GiB `VmHWM` | **the object is split four ways**; no rank exceeds 2.452 GiB |

So the physical account behind M4's failure is direct and is visible in the per-pid numbers: **one
serial whole-matrix LU is a larger object than four ASM-block LUs put together.** The `D-scotch`
9.044 GiB figure that §5.2 used as the ordering basis is an np=4 number from a *different*
instrument, and using it to predict that np=4 outranks np=1 was the error.

**M4's failure moves no B3 verdict.** G1/G2/G3 stay `PASS`, G4 stays `GATE FAIL`, G5 stays `PASS`,
Stage 4 stays `BLOCKED` under R11 (§1, §8). This item measured memory and nothing else.

---

## 4. The registered directional prediction: one HIT, one MISS

§5.2 registered, *"stated so a miss is a miss"*, that the true peaks would come out **above** the
`docker stats` figures on the record.

| claim | registered floor | measured | outcome |
|---|---|---|---|
| `D_serial` above 6.156 GiB | 6.156 | 11.133 `memory.peak`, 11.503 tree RSS | **HIT**, both instruments |
| `D_simple2` above 9.044 GiB | 9.044 | 9.719 tree RSS | **HIT** |
| `D_simple2` above 9.044 GiB | 9.044 | **8.000 `memory.peak`** | **MISS — reported as one** |

The registration named the consequence in advance: a value below its predecessor's figure *"would
mean the earlier figures were not the underestimates this file assumes."* For `D_simple2`'s
`memory.peak` that is the honest reading, with the caveat that 9.044 GiB is a **`D-scotch`** figure,
a different partitioner, and is therefore a cross-arm comparison rather than a same-arm one.

### 4.1 A registered *construction* claim is refuted on both arms

§5.2 asserted `memory.peak` **">= tree RSS by construction"** and predicted it would read higher.
**It reads LOWER on both arms:**

| arm | `memory.peak` | tree RSS | gap |
|---|---|---|---|
| `D_serial` | 11.133 GiB | 11.503 GiB | tree RSS higher by **0.370 GiB** |
| `D_simple2` | 8.000 GiB | 9.719 GiB | tree RSS higher by **1.719 GiB** |

"By construction" was wrong, and it was wrong in the pre-registration rather than in the
measurement. **Two candidate mechanisms, NEITHER of which this item measured** — they are named so
the next reader does not have to guess, and are not presented as established:

1. **Tree RSS double-counts pages shared between ranks.** It is a *sum of per-process `VmRSS`*; a
   page mapped by all four `D_simple2` ranks is counted four times, while the cgroup charges it
   once. This is the obvious candidate for the 1.719 GiB `D_simple2` gap and cannot explain
   `D_serial`, which has one solver process.
2. **Pages charged to another cgroup still appear in `VmRSS`.** Image-layer and library pages first
   faulted in by an earlier container — the planted-control container ran the *same image* 80
   seconds before `D_serial` — are resident in this process and counted by `VmRSS`, but their page
   charge may sit with the cgroup that first brought them in. This is the candidate for the
   0.370 GiB `D_serial` gap.

**Neither band moved.** M2a/M2b/M3a/M3b were frozen against their own instruments at `d062aace` and
graded against them. **The consequence is for how these numbers are used**, and §5.3 already
registered the rule: **tree RSS is the number for a sizing decision, `memory.peak` is the number for
a cap decision.** That guidance survives, but the reason changes — the two instruments do not bound
each other in the direction the registration assumed.

---

## 5. Strict completion — every clause, per arm

§6 requires all clauses; none is degraded and none is waived.

| clause | `D_serial` | `D_simple2` |
|---|---|---|
| 1. `rc = 0` from `timeout … docker run` | **0** | **0** |
| 2. `Total iterations: N. PetscConvergedReason: 2.` present | yes | yes |
| 3. `N` equals the archived count | **163 = 163** | **766 = 766** |
| 4. `OBJ varianceU` and full `GRAD` line, every digit | identical | identical |
| 5. sub-LU banner present (absent ⇒ arm ran stock ⇒ void) | present (1x) | present (1x) |
| 6. `cbfs_beta_grad.npy` exists and is NEWER than staged `runScript.py` (age guard) | 21:03 > 20:42 ✓ | 21:09 > 20:42 ✓ |
| 7. watcher >= 30 samples, max gap <= 5 s, spans the arm | 581 samples, 3.0 s | 157 samples, 3.0 s |
| 8. `selftest/selftest_verdict.txt` says `PASS` | PASS | PASS |

**The archived digits, reproduced exactly:**

| arm | reason | iters | `OBJ varianceU` | `GRAD` | iter-0 residual |
|---|---|---|---|---|---|
| `D_serial` | 2 | 163 | `1.5279275989724403e-02` | `n=21000 norm=1.4557054356e-05 min=-4.694385e-07 max=1.915505e-06` | `7.091589775454e-04` |
| `D_simple2` | 2 | 766 | `1.5279278602317540e-02` | `n=21000 norm=1.4558490322e-05 min=-4.694298e-07 max=1.915990e-06` | `7.091590381747e-04` |

§5.4 registered that `D_simple2`'s 766 was *"expected exactly, and anything else is an M0 failure,
not a shrug"* — because the partitioner here is identical. **It reproduced at 766.**

### 5.1 The §2.4 staging asymmetry held, and it was checked rather than assumed

§2.4 registered: *"if `D_simple2` regenerates coloring, that is expected; if `D_serial` regenerates
coloring, the staging failed and the arm is void."*

| arm | coloring file | mtime after the run | reading |
|---|---|---|---|
| `D_serial` | `dRdWColoring_1.bin` | **2026-08-21 16:43** — the carried-in file, untouched | **did NOT regenerate** ⇒ staging correct, arm not void |
| `D_simple2` | `dRdWColoring_4.bin` | **2026-08-23 21:05**, inside the arm's own window | **regenerated its own** ⇒ expected |

### 5.2 The decomposition was read back out of each arm's own directory, not from the launch command

The graded item's §6a trap was an arm that silently ran `scotch` and looked healthy.

| arm | `system/decomposeParDict` as DAFoam wrote it | `processor*` dirs |
|---|---|---|
| `D_serial` | `numberOfSubdomains 1; method scotch; n (1 1 1)` | 0 |
| `D_simple2` | `numberOfSubdomains 4; method simple; n (4 1 1)` | **4** |

`D_simple2` printed `T3 DECOMP OVERRIDE: simple [4, 1, 1]` once per rank. **The arm ran the
partitioning it was supposed to run.**

---

## 6. The instrument, and the controls it passed before it was believed

### 6.1 The planted control — standing rule 3

Run **before any graded arm**, as §9 step 4 requires, in a container of the **graded image**:

| channel | planted | read back | band | verdict |
|---|---|---|---|---|
| tree RSS | 2.00 GiB | **2.0083 GiB** | 2.00 – 2.60 | inside |
| `memory.peak` | 2.00 GiB + overhead | **2.0116 GiB** | 2.00 – 3.50 | inside |

**Verdict: `PASS`**, at `selftest/selftest_verdict.txt`, timestamped 20:43:16Z.

**The kill-trigger path was separately proved**, per §3.1: driven against an unsatisfiable floor
(`MemTotal`) with the kill redirected at a sentinel, it exited **9** and the sentinel was written.
A registered stop with nothing wired to it is L-239, and this one is wired.

**Image content assertion (§2.2 — a tag is not an identity).** The plant container is the first
container of the chain, and it printed the in-image md5 of
`src/adjoint/DALinearEqn/DALinearEqn.C` as **`5b3159f88dbefcf7c52bd888401d097f`** — equal to the
registered value. The image ID was independently asserted before staging as
`sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46`, equal to §2.2 and to the
ID the graded chain recorded.

### 6.2 Two independent reads of `memory.peak` agree to the byte

Departure `D-2` exists because a 2 s external sampler can only see the peak up to its last tick
before teardown. The in-container read taken **after `mpirun` exits** is exact at exit:

| arm | external sampler | in-container `CGROUP_PEAK_BYTES` | agreement |
|---|---|---|---|
| `D_serial` | 11,954,151,424 | **11,954,151,424** | **exact** |
| `D_simple2` | 8,590,049,280 | **8,590,049,280** | **exact** |

The 2 s cadence lost nothing at teardown on either arm. That is a corroboration of the sampler, not
a substitute for it, and both numbers are recorded.

### 6.3 Attribution — the failure this box has already had

Every number above is read from **one named container's cgroup** (`b3rss_D_serial`,
`b3rss_D_simple2`), resolved name → id → cgroup path. The instrument cannot see a peer's container
and refuses if it cannot resolve its own. This is why `D-1` added `--name`: the sibling lane's
9.786 GiB "peak" belonged to another lane's container
(`../adjoint_unblock_reproduce/RESULTS.md:286-292`).

**A peer dafoam container (`d460_psm`) started on this box 23 s after this chain finished. It was
not touched, and it could not have entered these numbers** — it did not exist while either arm ran.

### 6.4 The mid-run host floor did not fire, and it was close enough to matter

| arm | minimum host `MemAvailable` during the arm | 4 GiB hard floor | 12 GiB launch gate |
|---|---|---|---|
| `D_serial` | **7,598,900 kB = 7.25 GiB** | not breached | **below it** |
| `D_simple2` | 19,859,000 kB = 18.94 GiB | not breached | above it |

**`D_serial` spent part of its run below the 12 GiB launch-gate threshold** while remaining well
above the 4 GiB mid-run floor — precisely the situation §3.1 anticipated when it set the mid-run
floor at 4 GiB rather than 12: *"a mid-run kill at 12 GiB would kill a healthy arm on a shared box
the moment a peer starts."* **The arm that would have been killed by a 12 GiB mid-run floor is the
arm that produced this item's headline number.** No watcher abort fired on either arm.

---

## 7. What attempt 2 did differently, and every departure disclosed

Departures `D-1` … `D-5` of §4.3 all held as registered. Two further disclosures, neither of which
touches a gate, band, threshold, cap or label:

| # | disclosure | effect |
|---|---|---|
| **A2-1** | Staging used **`cp -a`** (mode-preserving) rather than attempt 1's `cp -r`, then `chmod 777` on each arm root with the mode **verified by `stat` after the chmod**, per Addendum 3. The graded 2026-08-21 arms are 777 throughout — root, `0/`, `constant/`, `system/` — and `cp -a` reproduces that exactly, which is what "match the graded chain exactly" means. Stager preserved at `<run root>/stage_attempt2.sh` rather than in scratch (L-186 is the reason attempt 1's staging step was never written down). | the repair Addendum 3 authorised; **no solver input changed** — both `runScript.py` sha256 asserted equal to §2.3 after staging |
| **A2-2** | `chain_peakrss.sh` line 27 **truncates `ledger.csv`** on each launch. The script is a frozen instrument and was **run unedited**, so attempt 1's ledger was preserved byte-for-byte at `attempt1/ledger_attempt1.csv` instead of being kept append-only in place. | attempt-1 evidence intact; the live `ledger.csv` holds attempt-2 rows only. **Disclosed because the supervisor's brief asked for an append-only ledger and the frozen script makes that impossible without editing it — the freeze won.** |

**Attempt-1 artifacts were MOVED, never deleted**, to `<run root>/attempt1/`: both arm directories,
the contents of `logs/` and `selftest/`, the `.done` sentinel, and byte copies of the attempt-1
ledger and chain stdout. The `triage/` directory — the paired m755/m777 control Addendum 3 verified
physically on disk — was left untouched in place.

**Frozen-instrument hashes, re-verified from the committed blobs before use:**

| file | sha256 | vs freeze commit `d062aace` |
|---|---|---|
| `analyse_peak_rss.py` | `c4db08fc…6f9c6951eb` | **identical** |
| `b3_rss_watch.sh` | `e9db593e…d3d463dac29` | **identical** |
| `chain_peakrss.sh` | `0484157b…3d97c7c53da81` | identical to HEAD; **did not exist at `d062aace`** — it was committed at `7a007d67` as the attempt-1 record, and is not part of the §4 frozen grading path. Run unedited. |

---

## 8. Cost, measured

Unit: **core-minutes = wall s × ranks ÷ 60** (`CLAUDE.md` rule 12).

| item | ranks | wall s | **core-min** | source |
|---|---|---|---|---|
| planted-control self-test | 1 | 49 | **0.82** | `selftest/selftest_watch.log`, 20:42:27Z → 20:43:16Z |
| `D_serial` | 1 | **1177** | **19.62** | `ledger.csv` |
| `D_simple2` | 4 | **337** | **22.47** | `ledger.csv` |
| **attempt-2 measured total** | | | **42.91** | |

**Gross = cleaned.** The longest row is 1177 wall s, nowhere near the 3600-s stall rule, so there is
nothing to clean out. **Zero waste in attempt 2** — both arms produced graded measurements.

**Not included, and stated as not measured rather than approximated:** §7 allotted **2.0 core-min**
to "watcher + staging + grading". Staging measured 2 s of wall (20:42:12Z → 20:42:14Z) and grading
about 1 s; the two watchers are 2 s-cadence `bash` loops running **outside** the arms' `cpuset`.
None of this was separately instrumented, so it is **excluded from the 42.91 figure** rather than
folded in at its estimate. The true total is 42.91 core-min plus a small unmeasured overhead.

| | core-min | derived $ at $0.0513/core-h |
|---|---|---|
| §7 estimate for the item | 46.0 | $0.0393 |
| **attempt 2, measured** | **42.91** | **$0.0367** |
| ratio actual/estimate | **0.93x** | |
| attempt-1 waste (Addendum 1 §A1.4) — **stays named as waste** | 21.00 | $0.0180 |
| **item total charged** | **63.91** | **$0.0546** |
| registered ceiling | 182.0 | $0.156 |
| **remaining of the 161.0 Addendum-3 allowance** | **118.09** | |

**35.1 % of the 182.0 core-min ceiling is spent. No overrun; no clause of rule 12 was reached.**
Every dollar figure is **derived at the owner-stated $0.0513/core-h, reported-by-owner, not
measured**. Nothing approaches the $25 bar. CPU on the existing box, so the 2026-08-21 blanket
applies and rule 12's GPU carve-out does not.

### 8.1 Gap attribution

| line | estimate | actual | gap | attribution |
|---|---|---|---|---|
| self-test | 1.0 | 0.82 | −0.18 | misprediction, conservative |
| `D_serial` | 21.7 | **19.62** | **−2.08** | **favourable load** — 1177 s against the 1266 s basis of 2026-08-21, which ran at load ≈ 11–15; this arm launched at load 10 |
| `D_simple2` | 21.3 | **22.47** | **+1.17** | **contention** — 337 s against 301 s, with a live peer lane on the box (D-5) |
| watcher/staging/grading | 2.0 | not measured | — | excluded, see above |

**The two solver gaps are two-sided and nearly cancel.** §5.3 registered in advance that a
wall-time difference is a load artefact and **not a finding** provided M0 holds — M0 held, so
neither gap is read as a finding about the solver. Core-minutes are charged as measured regardless.

---

## 9. What this item still cannot establish

§8 of the pre-registration stands unchanged. Restated with what is now known:

- **Nothing about B3's verdicts.** G1/G2/G3 `PASS`, G4 `GATE FAIL`, G5 `PASS`, Stage 4 `BLOCKED`
  under R11 — untouched, M4's failure included.
- **These are peaks under a 12 GiB cap, not unconstrained peaks.** `D_serial` reached **92.8 % of
  its cap** with **0.867 GiB** of headroom. A cgroup limit changes reclaim behaviour, so an
  unconstrained peak is **not** derivable from 11.133 GiB, and it may be higher. **This is now the
  live question the item hands on**, and it is a new registration with its own price, not an
  addendum here.
- **Nothing about `D-scotch`'s true peak.** Not re-run (§2.1); its 9.044 GiB stays a 5 s
  `docker stats` maximum. After this item it is **the weakest of the three arms' figures by a wider
  margin than before**, since the two arms measured here show that instrument undersampling by up
  to 1.87x.
- **Nothing about other partitionings, other `np`, other cases, or scaling.** Two points on one
  21,000-cell case.
- **Nothing about whether the gradient is right.** `decomposition_np4/RESULTS.md:243-247` stands:
  *"invariance is necessary, never sufficient."*
- **Nothing about the MemAvailable launch-gate ruling**, which is **Sanaa's**. This item produces an
  input to it — §6.4's reading that `D_serial` ran healthily below the 12 GiB threshold — and **no
  agent may move that threshold on the strength of it** (standing rule 9). It stayed at 12 GiB here.
- **The §4.1 instrument-relation finding is not a mechanism.** Two candidates are named; neither was
  measured by this item.

---

## 10. Artifacts

| what | absolute path |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/B3-decomposition-peakrss/` |
| grader output (machine) | `…/peak_rss.json` |
| ledger, attempt 2 | `…/ledger.csv` |
| chain stdout, both attempts | `…/chain_peakrss.out` |
| watcher logs | `…/logs/D_serial_rss.log`, `…/logs/D_simple2_rss.log` |
| solver logs | `…/logs/D_serial.log`, `…/logs/D_simple2.log` |
| decomposition read-back | `…/logs/D_serial_decomp.txt`, `…/logs/D_simple2_decomp.txt` |
| planted-control record | `…/selftest/selftest_verdict.txt`, `…/selftest/selftest_watch.log`, `…/selftest/selftest_plant.log`, `…/selftest/selftest_trigger.log` |
| attempt-2 stager | `…/stage_attempt2.sh` |
| **attempt-1 evidence, preserved** | `…/attempt1/` (arm dirs, `logs/`, `selftest/`, `ledger_attempt1.csv`, `chain_peakrss_attempt1.out`, `.done`) |
| Addendum-3 paired mode control | `…/triage/m777/reports`, `…/triage/m755/` |
| pre-registration, frozen | `/home/ubuntu/Certonomous/cases/dafoam/ladder-b/B3/decomposition_peak_rss/PREREGISTRATION.md` (`d062aace`; Addenda at `7a007d67`, `5edfe8c0`) |

---

*Nothing in this file has been filed, sent, uploaded, registered, posted or pushed. The item-level
verdict is the supervisor's to record; this draft reports the rows the frozen grader produced.*
