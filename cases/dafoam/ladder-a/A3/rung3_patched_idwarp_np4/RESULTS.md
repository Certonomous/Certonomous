# A3 ONERA M6, sweep rung 3 (79,560 cells) — the patched-IDWarp column at np=4: RESULTS

**Committed on the dafoam supervisor's ruling of 2026-08-23, after their personal sweep** — they
read the kill marker and confirmed the gate-floor arithmetic (`16.0 − 9.2 = 6.8 < 8.0`), and
**confirmed the no-relaunch call**: the cap is not raised and no second budget is taken under this
pre-registration. Nothing here has been added to `docs/DOCKET.md`,
`docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/LAB_STATE.md`, `LADDER_A_STATUS.md`,
`cases/dafoam/INDEX.md` or any charter. **Nothing is filed, sent, uploaded, posted or pushed.
Filing stays NOT APPROVED and is Sanaa's alone.**

Graded against `PREREGISTRATION.md`, frozen at commit **97a54c07** and verified byte-identical to
its committed blob before staging and again immediately before launch. This file revises nothing
in that document.

Run root: `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/`
Executed 2026-08-23, 20:56 – 21:03 UTC.

---

## 1. Verdict

# NOT A RESULT — stopped by memory

**Arm R3-A was killed by its own registered memory guard at 21:03:38 UTC, 85 s into an 2600 s
budget, on the HOST FLOOR limb — not on its own RSS ceiling.**

Per **R3-P7**'s registered disposition and §4 *"It WOULD NOT mean"* item 5, written before the run:
**no conditioning, gradient or patch claim is drawn from this arm in any direction, the cap is NOT
raised, and no second budget is taken** (`COMPUTE_BUDGET_CHARTER.md`). This is the same family rule
that made the *shipped* rung-3 verdict sayable, and it cuts the same way here.

**The measurement this item was bought for — R3-P4, the 11-checkpoint identity — was NOT MADE.**
The arm never reached the Krylov solve: **zero** `Main iteration` lines were printed. **0 of 11
checkpoints matched, because 0 of 11 were reached.** The identity comparator ran, was armed, and
reported `container gone before a decision was reached` (`identity_stop.sh` exit 0).

**The patched rung-3 cell of row 12b therefore stays `PENDING`. It does NOT move to
`GATE FAIL (adjoint, inherited)`, and it does not move to any gradient verdict.** §4's registered
outcome required the arm to actually reproduce the stagnation; it did not run long enough to try.

---

## 2. What actually happened, from the guard's own trace

The container's own RSS was **9.202 GiB at peak — comfortably inside its 15.0 GiB guard ceiling and
its 16 GiB docker cap.** **The arm did not exceed its own budget. The box did.**

| t (s) | container RSS (GiB) | host `MemAvailable` (GiB) | strikes |
|---|---|---|---|
| 5 | 1.062 | 15.0366 | 0 |
| 10–40 | 1.846 – 1.847 | 14.12 – 14.17 | 0 |
| **45** | **7.434** | **8.7984** | 0 |
| 50 | 7.569 | 8.5658 | 0 |
| 55 | 8.340 | 8.2209 | 0 |
| **60** | 9.170 | **7.3767** | **1** |
| **65** | **9.202** | **7.3925** | **2** |
| **70** | 9.129 | **7.3944** | **3 → KILL** |

Guard record, `MEMORY_STOP_FIRED.patched`, verbatim on the operative line:
`reason: host MemAvailable 7.3944 GiB < floor 8.0 GiB`, `sustained for 3 consecutive samples at
5s = 15s`, `last sample: own_RSS_GiB=9.129000 host_MemAvailable_GiB=7.3944`.

The jump at t+45 s is the Jacobian and preconditioner assembly beginning — the log's last progress
line is `dRdWTPC: 100 of 1355, ExecutionTime: 70.36 s`, i.e. the arm was 7% into building the
transonic preconditioner when it was stopped.

### The structural finding, reported and NOT acted on

**The registered launch gate could not have protected the registered floor for this arm, and the
arithmetic says so plainly.** §7 registers the gate's memory limb at `MemAvailable ≥ 16 GiB` and
the neighbourliness floor at `MemAvailable ≥ 8 GiB`. This arm's own peak is **9.2 GiB**. A launch
admitted at exactly the gate threshold leaves `16.0 − 9.2 = 6.8 GiB` — **already below the 8.0 GiB
floor before a single co-tenant grows by one byte.** The gate opened at **16.02 GiB** (poll 2), which
is 0.02 GiB of margin over the limb, and the floor was breached 60 s later.

Under the registered numbers the gate would need a limb of at least `9.2 + 8.0 = 17.2 GiB` to be
consistent with its own floor. **Changing either number is not a lane's call** — both are
pre-registered thresholds and gates are closed after first compute (CLAUDE.md rule 2). It is
**reported to the supervisor and to verification as a design finding, unruled**, and this item
makes no edit to either.

*Honest qualifier: 9.2 GiB is this arm's peak as measured up to the kill, at 7% of the
preconditioner assembly. The shipped arm at this mesh peaked at **11.65 GiB**
(`A3_RUNG3_N52_RESULT.md:50-51`), so the true requirement is larger than 9.2 and the gate's
shortfall is correspondingly worse, not better. The 17.2 GiB figure above is a floor on the floor.*

### What was NOT the cause

* **Not the arm exceeding its cap.** 9.202 of 16 GiB, 42% headroom unused.
* **Not the colouring.** `coloring_guard.sh` exit **0** — `Reading Coloring dRdWColoring_4`,
  `dRdWTPC: 0 of 1355`, **zero** occurrences of `Calculating dRdW Coloring`. The cache was READ.
* **Not a stall.** 85 s wall against a 2600 s timeout; `rc=137` is the SIGKILL the guard delivered,
  not a hang.
* **Not the `ct_cd` departure.** The departure never got as far as being tested.

---

## 3. Predictions, scored honestly — including the ones that cannot be scored

| # | prediction | band | measured | verdict |
|---|---|---|---|---|
| **R3-P1** | provenance and activity, 5 limbs | exact | (a) **4/4 ranks** `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425`, import path `/opt/idwarp_patched/idwarp/__init__.py`; (b) `transonicPCOption 1;` present; (c) **0** sub-LU banners; (d) solver `nProcs : 4`, 4 `processor*` dirs; (e) version `2.6.2` | **HIT** |
| **R3-P2** | cold start, exact to 16 digits | `1.018123970654079` | **`1.018123970654079`** | **HIT** |
| **R3-P3** | colouring READ, not rebuilt, 1355 colours | exact, wired | 0 `Calculating`; `Reading Coloring dRdWColoring_4`; `dRdWTPC: 0 of 1355`; guard exit 0 | **HIT** |
| **R3-P4** | **THE IDENTITY** — 11 checkpoints bit-identical through iteration 1000 | exact, 11/11 | **NOT MEASURED — 0 of 11 checkpoints reached.** The arm was stopped before the Krylov solve began | **NOT A RESULT** |
| **R3-P5** | the named alternative: the patched adjoint converges | `reason 2` | **NOT MEASURED** — no adjoint ran | **NOT A RESULT** |
| **R3-P6** | the falsifier: the path differs while stagnating | any checkpoint differing ≥ 1.0e-03 | **NOT MEASURED** — did not fire, and **could not have**, because no checkpoint was printed. **This is explicitly not evidence that it would not have fired** | **NOT A RESULT** |
| **R3-P7** | memory | peak RSS 9.0 – 14.0 GiB; host never < 8 GiB | peak **9.202 GiB** — inside the RSS band, but **at 7% of preconditioner assembly, so not the arm's true peak**; host floor **BREACHED at 7.3767 GiB**, guard fired | **RSS limb: inside band but incomplete. HOST limb: MISS — the floor was breached** |
| **R3-P8** | wall and cost | 445 – 1157 s, 29.7 – 77.1 core-min | **85 s, 5.667 core-min** — a stopped arm, **not a wall measurement**. `DAFOAM_CHARTER.md` §7: a stop is not a measurement | **NOT A RESULT** (not a MISS — the quantity was never measured) |
| **R3-P9** | the comparator is proved able to SEE a difference, at zero solver cost, before the arm runs | exits 5 / 6 / 7 on three planted inputs | **limb 6 exit 5** (identity confirmed against **the real shipped rung-3 log**), **limb 7 exit 6** (rung 2's real CD path, differing in the 5th significant figure at iteration 0, **SEEN as DIVERGED**), **limb 8 exit 7** (stood down on a converging path, did not kill) | **HIT** |

**The one prediction this item was bought to test is the one it did not reach.** That is stated
here at the headline of the score table, not in a limits section.

---

## 4. The guards, and the fact that this record is the L-239 repair working

Rung 2 registered this exact host floor with a **record-only** watcher, drove host `MemAvailable`
to 5.85 GiB for 82 of 156 samples, and **no stop fired** (L-239). The repair was to name what polls
the threshold and what performs the stop, and to prove both before launching.

**All eight limbs of `guard_selftest.sh` passed in this session, at 21:00:56 UTC, before the arm
launched**, and `drive.sh` refused to launch without the marker being newer than `mem_guard.sh`,
`coloring_guard.sh`, `identity_stop.sh` and `shipped_cd_checkpoints.txt`:

| limb | what was planted | required | got |
|---|---|---|---|
| 1 | thresholds no container can satisfy | `mem_guard` kills, exit 4 | **exit 4, container gone** |
| 2 | thresholds no container can breach | `mem_guard` does NOT kill, exit 124 | **exit 124, container alive** |
| 3 | rebuild log **with** a masking `Reading Coloring` line | exit 3 | **exit 3** |
| 4 | the genuine warm-cache signature | exit 0 | **exit 0** |
| 5 | rung 1's colour count (1233) at rung 3 | exit 5 | **exit 5** |
| **6** | **the real shipped rung-3 log itself** | exit 5, identity confirmed | **exit 5** |
| **7** | **A3 rung 2's real CD adjoint path** (`2.121211553380e-02` vs rung 3's `2.121343646203e-02`) | exit 6, DIVERGED | **exit 6 — the comparator sees it** |
| **8** | a path matching at iteration 0 then dropping below `1.0e-03` | stand down, do not kill, exit 7 | **exit 7** |

**Limbs 6–8 are R3-P9, the planted-difference control, and they are the reason a "no difference"
finding from this comparator would have been believable.** CLAUDE.md rule 3: a zero from a reader
not shown able to see a non-zero is not evidence. **The comparator was proved able to see a
non-zero. It then never got a number to read.** Those two facts are separate and both are recorded.

**And limb 1 is why this record exists at all rather than a silently over-committed box.** The guard
that killed this arm is the same guard that was proved 3 minutes earlier to be able to kill.

---

## 5. Departures and observations from execution

1. **D2's placement, disclosed before the run in `stage.sh`'s own header and repeated here.** §3
   departure 5 registers D2 as `log0(repr(totals))` "immediately after `compute_totals`", and gives
   its purpose as *"if the patched adjoint converges, this is what makes the gradient readable at
   all"* — on an arm that runs `-task ct_cd`. The only `compute_totals` this arm executes is the
   one inside the new `ct_cd` branch, so D2 was placed there; a D2 in the pre-existing
   `compute_totals` branch would be dead code this arm never reaches. **Consequence: D2 and D3 are
   textually contiguous and the diff carries TWO insertion hunks rather than three.** The registered
   assert — *"the diff shows only D1, D2, D3"* — was checked literally: **2 insertion hunks, 0
   deletions, 0 modifications, and all three D-markers required present**. Diff on disk at
   `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/runScript_rung3p.diff`.
2. **The §12 pre-flight command as registered does not run**, for the same reason recorded in the
   rung-1 companion's `RESULTS.md` §5 item 1: it hashes `<pkgdir>/../libidwarp.so`, and the library
   is **in-package** at `/opt/idwarp_patched/idwarp/libidwarp.so`. A defect in §12's illustrative
   command, **not in a gate, threshold, band, cap or label.** The pre-flight was run with the path
   resolved, in this session at 20:44 UTC, on **all 4 ranks** of `dafoam-idwarp-rot:v1`:
   md5 `85f59e87253e0a71a813f64ca6e4c425`, 491,344 bytes, version `2.6.2`. It was **not re-run** for
   this item — same image, same session, same measurement — so this item's §8 pre-flight line
   (0.200 core-min) was **not spent**. D1 in the run script re-measures it per rank anyway, and did:
   R3-P1 limb (a) is measured on this arm's own log, not inherited.
3. **`stage.sh` and `drive.sh` were written after the pre-registration commit and committed before
   they ran** (commit landed prior to execution), as §12 requires. Neither changes any gate,
   threshold, band, cap or label.
4. **The archived case was never written to.** `/home/ubuntu/certonomous-runs/A3-rung3-n52/` was
   read only; every assert ran against it and the staged copy under
   `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/patched/`.
5. **Staging asserts all passed**: `points.gz` sha256 `cf35cf14…` matching both the file and
   `constant/birth_certificate.json` (verdict **clean**, cells **79560**); cache md5 `f91c25c1…`;
   `diff -rq 0 0.orig` empty; no `processor*` and no non-`0` time directory in the staged copy.
6. **No peer container or process was touched.** Live throughout and left alone: a peer dafoam
   container on `dafoam-subpclu:v2` (B3 peak-RSS chain), 4 `buoyantBoussinesqSimpleFoam` (T-family)
   and 1 `simpleFoam` (closure). **Those co-tenants are the other half of the floor breach**, and
   the correct response to that was to stop this item's arm, which is what happened.
7. **The shared git index** stages deletions of files present in the worktree and in HEAD,
   including this item's own newly committed `stage.sh` and `drive.sh`. That is a **stale index
   snapshot**, not a deletion. **It was not touched** — the index is the chief's call (CLAUDE.md
   rule 10). All six frozen files were verified byte-identical to blob `97a54c07` before staging and
   again before launch.

---

## 6. Cost

| item | registered | measured | note |
|---|---|---|---|
| **R3-A** PATCHED stage 1, `ct_cd` | 757 s / 50.5 core-min, band 29.7 – 77.1, timeout 2600 s | **85 s / 5.667 core-min** | **a stopped arm, not a wall measurement** |
| guard selftest (2 `alpine` + 6 file-only limbs) | ~110 s / 1.8 core-min, band 0.5 – 2.0 | 68 s wall (20:59:48 → 21:00:56) ⇒ **~1.13 core-min** | inside band |
| per-rank provenance pre-flight | 0.200 core-min | **0.000 — not re-run**, reused from the rung-1 companion's in-session measurement on the identical image (§5 item 2) | under |
| launch-condition polling | 0.000, up to 4 h | **0.000** — gate opened on **poll 2** (61 s of polling) | — |
| shipped twin re-run | not run, declined by name | **not run** | — |
| fresh colouring pass | not run, cache carried | **not run** — 0 `Calculating` | — |
| `ct_cd` discriminator (§3 dep. 6) | not run, conditional, supervisor's go | **not run** | — |
| stage R3-2, the FD arm | not run, conditional on R3-P5, needs its own pre-registration | **not run** | — |
| **TOTAL** | predicted 52.5, band 32.0 – 79.1 | **≈ 6.80 core-min** | **below the band** |

**REGISTERED CEILING 176.0 core-min — used 3.9% of it. No overrun.**

**Dollars: 6.80 core-min = 0.1133 core-hours × $0.0513/core-hour = $0.0058.**
`cost_basis`: c7a.4xlarge at $0.0513/core-hour, **owner-stated 2026-08-21/22 and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so this dollar figure is REPORTED-BY-OWNER, NOT MEASURED.** The
core-minute figure is measured (wall × ranks ÷ 60, `ledger.txt`).

**The spend was not wasted, and it was not a result either.** It bought: the provenance, cold-start
and colouring proofs on the patched stack at rung 3 (R3-P1, R3-P2, R3-P3, all HIT), the
demonstration that all three guards fire and stand down correctly in this session (R3-P9, HIT), and
the structural finding in §2 about the gate and the floor. It did not buy the identity.

**No second budget is requested, and none may be taken under this pre-registration** — R3-P7 fixes
that disposition and gates are closed after first compute. **Whether to re-buy this cell, and under
what memory arrangements, is the supervisor's call and ultimately Sanaa's, not this lane's.**

---

## 7. What this item cannot see

Every item of §9 stands as registered, and this run adds nothing that narrows any of them, because
it produced no adjoint. In particular §9 item 3 is untouched: **the ladder's conditioning ceiling
stays bracketed between 42,120 and 79,560 cells and unlocated.** Nothing here says the M6 adjoint
is reachable or unreachable at 79,560 cells with the patched stack — **only that this attempt was
stopped by the box before it could ask.**

**And §4 item 6 stands: the shipped rung-3 `GATE FAIL` is neither more nor less true than it was.**
Row 11 stands as it is. Per R11 a patched number never moves a shipped grade — and here there is no
patched number at all.

---

## 8. Standing statements

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.

**A stop is not a measurement** (`DAFOAM_CHARTER.md` §7). The memory stop of R3-P7 carries no claim
of its own in either direction, and unlike R3-P4's *deliberate* stop there is no completed finding
sitting behind it.

**Toolchain identity is an image ID and a library hash, never a version string.** Measured per rank
on this arm: `85f59e87253e0a71a813f64ca6e4c425` on 4 of 4.

**Nothing is filed, sent, uploaded, posted, registered or pushed. Filing stays NOT APPROVED and is
Sanaa's alone.**

## 9. Artifacts

| what | path |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/` |
| arm log | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/patched.log` |
| ledger | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/ledger.txt` |
| **the memory stop record** | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/MEMORY_STOP_FIRED.patched` |
| RSS / host-memory trace | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/rss_patched.txt` |
| guard selftest record | `guard_selftest.log`, `GUARD_SELFTEST_PASS` (in the run root) |
| identity comparator log | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/identity_stop_patched.log` |
| colouring guard log | `/home/ubuntu/certonomous-runs/P4-a3-rung3-patched/coloring_guard_patched.log` |
| staging record + script diff | `stage.log`, `runScript_rung3p.diff`, `runScript_rung3p.py` |
| launch-gate record | `launch_condition.txt`, `lever_echo_patched.txt` |
| shipped comparator (read-only, cited) | `/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log` |
