# A3 ONERA M6, sweep rung 1 (21,840 cells) — the patched-IDWarp column at np=4: RESULTS

**Committed on the dafoam supervisor's ruling of 2026-08-23, after their personal sweep** — they
re-derived the table arithmetic (0.3826% / 0.9273%, ratio 0.4126), verified the FD bit-identity on
`shape[115]` and `patchV[1]` across both logs, and read `analyse_r1.py`'s planted control and both
`stage.sh` / `drive.sh` as diffs. **No verdict wording here is final until Sanaa rules on §2's
registered conflict.** Nothing here has been added to `docs/DOCKET.md`,
`docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/LAB_STATE.md`, `LADDER_A_STATUS.md`,
`cases/dafoam/INDEX.md` or any charter. **Nothing is filed, sent, uploaded, posted or pushed.
Filing stays NOT APPROVED and is Sanaa's alone.**

Graded against `PREREGISTRATION.md`, frozen at commit **5d8e2f52** and verified byte-identical to
its committed blob immediately before staging and again before launch. This file revises nothing
in that document.

Run root: `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/`
Executed 2026-08-23, 20:44 – 20:59 UTC.

---

## 1. Headline

**The rung-2 degradation is NOT a property of the patch. It is a property of which side of the FD
reference the shipped analytic happened to sit on.** Prediction **R1-P8b**, registered before the
run precisely so this could not be read favourably afterwards, is a **HIT**.

**One warp-crossing component carries this rung's FD verdict — `shape[115]` — and that was stated
in the pre-registration before the run, not discovered here** (§4, §9 item 1). `patchV[1]` does
not cross the warp chain; `twist[1]` and `shape[5]` were **flagged by name before the run** for
failing the 1% step-consistency gate and carry **NOT A RESULT** in the FD column on every arm.

| component | shipped analytic | patched analytic | analytic moved | FD(h), identical both images | rel err shipped | rel err patched |
|---|---|---|---|---|---|---|
| `patchV[1]` | `7.64611787804267e-03` | `7.64611787804267e-03` | **0** | `7.66002800367815e-03` | 0.1816% | **0.1816%** |
| `twist[1]` ‡flagged | `1.73254475029472e-03` | `1.72299801333938e-03` | 0.5510% toward zero | `1.75500956925284e-03` | 1.2800% | **1.8240%** — **NOT A RESULT** |
| `shape[5]` ‡flagged | `7.34091831960848e-03` | `8.00824398755727e-03` | 9.0905% away from zero | `7.82812275236522e-03` | 6.2238% | **2.3010%** — **NOT A RESULT** |
| **`shape[115]`** | `-1.24189675803981e-01` | `-1.23519403936271e-01` | **0.5397% toward zero** | `-1.23048666802475e-01` | 0.9273% | **0.3826%** (0.4126×) |

At rung 2 the same unchanged library made `shape[115]` **9.2084× worse**; at rung 1 it makes it
**2.42× better** (0.9273% → 0.3826%). Nothing about the library changed between those two
measurements. What changed is the sign of the shipped error: at rung 2 `analytic − FD` was
`+2.2401e-05` (positive), at rung 1 it is `-1.141009e-03` (negative), so the same signed
toward-zero shift moves the number away from FD at rung 2 and toward it at rung 1.

**The honest statement of the claim, and it is deliberately narrower than the result looks:** this
is a **two-rung pattern on one case**. §9 item 10 registered that limitation before the run and it
stands. Two rungs of A3 cannot establish that the patch's analytic delta has a consistent sign in
general.

---

## 2. Verdicts

**Arm R1-A (PATCHED) — `PASS` under this rung's per-component rule.**
Evaluable-and-step-consistent components: `patchV[1]` (0.1816%) and `shape[115]` (0.3826%). Both
PASS at < 5%; two such components, so the arm-verdict condition "all PASS with ≥ 2 such" is met.
No sign flip on any graded component.

**Arm R1-B (SHIPPED, the literal `dafoam/opt-packages:latest`) — `PASS`**, on the same instrument:
`patchV[1]` 0.1816%, `shape[115]` 0.9273%.

**Arm R1-C (trivial baseline, h = 1e-8) — `NOT EVALUABLE`, as predicted.** The gate correctly
rejected the wrong step. The falsifier that would have **withdrawn arm R1-A's verdict** — the
wrong step both clearing the evaluability gate and returning ≤ 5% — **did not fire**.

### The open conflict registered in §4, printed as registered, both readings side by side

The pre-registration named this conflict before the run rather than resolving it, and said the
choice between the two rules **retires or reinterprets a gate threshold and is not a lane's call**.
Both readings, on the same numbers:

| reading | instrument | arm R1-A | arm R1-B |
|---|---|---|---|
| **per-component rule** (`A3_FD3_PREREGISTRATION.md` §4; the instrument the archived rung-1 row was graded on) | flagged components are NOT A RESULT; arm PASSes on ≥ 2 evaluable-and-step-consistent components | **PASS** | **PASS** |
| **aggregate band** (`A_stepsize_study.md:92-94`) | *any flagged component ⇒ FAIL pending investigation*, regardless of the aggregate | **FAIL pending investigation** | **FAIL pending investigation** |

Both readings apply to **both** arms identically, because `twist[1]` and `shape[5]` are flagged on
the shipped arm exactly as on the patched one.

> **NO VERDICT WORDING IN THIS FILE IS FINAL UNTIL SANAA RULES.** Choosing between the two rules
> **reinterprets a gate threshold**, which is reserved to Sanaa (CLAUDE.md, *Reserved to Sanaa*),
> with verification consulted. **Referred upward, unruled.** The `PASS` entries in §2 are the
> per-component rule's reading, printed beside the aggregate band's `FAIL pending investigation`
> reading, because the pre-registration required both to be printed — **not because this item has
> chosen between them.** The dafoam supervisor has confirmed this disposition and has not chosen
> either; neither has this lane.

**The consistency argument, recorded as CONTEXT and explicitly NOT as the decision.** The archived
rung-1 row was graded under the per-component rule (`../grading_confirmation/RESULTS.md:134-136`),
and grading all three rows — archived ‡, fresh literal-SHIPPED, PATCHED — on one instrument is why
the pre-registration named that rule as the one it would apply. **That is a reason a ruling might
go one way. It is not a ruling, it is not this lane's to make, and it is recorded here so that the
argument is visible to whoever does rule rather than being smuggled in as a settled premise.** If
Sanaa rules for the aggregate band, both arms read `FAIL pending investigation` and the archived
row's grade is a separate question this item does not touch (R11: a patched number never moves a
shipped grade).

---

## 3. Every registered prediction, scored

| # | prediction | band | measured | verdict |
|---|---|---|---|---|
| **R1-P1** | provenance and activity, 5 limbs, all 3 arms | exact | (a) 4/4 ranks `85f59e87…` on R1-A and R1-C, 4/4 `f0fcb488…` on R1-B, import paths `/opt/idwarp_patched/idwarp/` and site-packages respectively; (b) `transonicPCOption 1;` present on all 3; (c) **0** sub-LU banners; (d) solver `nProcs : 4` and 4 `processor*` dirs on all 3; (e) version `2.6.2` on **both** stacks | **HIT** |
| **R1-P2** | cold start, 16 digits | `0.5969274433533561` | `0.5969274433533561` on all three arms | **HIT** |
| **R1-P3** | colouring READ, not rebuilt | 1233, zero `Calculating` | 0 `Calculating`; `Reading Coloring dRdWColoring_4`; `dRdWTPC: 0 of 1233` on R1-A and R1-B | **HIT** (see §5 on R1-C) |
| **R1-P4** | adjoint bit-identical across images | 5 pairs + `reason 2` at 368 | 5/5 pairs match the archived row digit for digit on **both** images; `Total iterations: 368. PetscConvergedReason: 2` on both | **HIT** |
| **R1-P5** | **THE CONTROL** — the FD column must not move | bit-identical | **16 of 16** perturbed CD values, **8 of 8** FD estimates, both baselines and the drift **bit-identical** across R1-A, R1-B and the archived row — all three pairings | **HIT** |
| **R1-P6** | the literal shipped image reproduces the archived ‡ row | bit-identical, every printed digit | analytic values identical; FD, baselines and drift bit-identical | **HIT** |
| **R1-P7** | `patchV[1]` identical across images (evidence, not a gate) | exact `7.64611787804267e-03`, rel err 0.1816% | `7.64611787804267e-03`, 0.1816% | **HIT** |
| **R1-P8** | `shape[115]` patched rel err | 0.00 – 2.20%, sign negative, PASS | **0.3826%**, sign negative, PASS | **HIT** (point estimate was 0.78%) |
| **R1-P8b** | **THE DIRECTIONAL PREDICTION** — patched error strictly lower than 0.9273%, delta positive (magnitude decreases) | strictly lower; delta positive | **0.3826% < 0.9273%**; delta **+0.5397% toward zero** | **HIT** |
| **R1-P9** | `twist[1]` and `shape[5]` flagged and not graded; analytic deltas positive, 0.01 – 3.0% | both positive, both in band | flagged and **NOT A RESULT** on every arm ✔; `twist[1]` **+0.5510% toward zero** (in band); `shape[5]` **9.0905% AWAY from zero** | **SPLIT: `twist[1]` HIT, `shape[5]` MISS on both direction and band** |
| **R1-P10** | patch effect, analytic-vs-analytic L2 over the 120-component shape row | 0.005 – 5% | **0.940327%**, 120 of 120 components differing at printed precision, **0** analytic sign flips | **HIT** |
| **R1-P11** | container peak RSS; host floor | 3.5 – 6.5 GiB; host never < 8 GiB | **5.465 / 5.464 / 1.425 GiB**; host `MemAvailable` minimum **11.8361 GiB over 116 samples** (floor 8.0), guard never fired | **HIT** |
| **R1-P12** | R1-A wall and cost | 246 – 640 s, 16.4 – 42.7 core-min | **344 s, 22.933 core-min** (inflation 344/246 = **1.40×**, inside 1.0 – 2.6×) | **HIT** |
| **R1-P13** | shipped arm's own FD verdict | `patchV[1]` 0.10 – 0.30%, `shape[115]` 0.80 – 1.10%, both PASS | **0.1816%** and **0.9273%**, both PASS, zero sign flips | **HIT** |
| **R1-P14** | wrong step fails the evaluability gate | `\|CD(+h)−CD(−h)\|` 3.0e-07 – 6.0e-06; ratio 0.018 – 0.37; NOT EVALUABLE | **2.026280e-06**; ratio **0.1246**; **EVALUABLE = NO** | **HIT** |
| **R1-P15** | the ratio, if computed anyway | > 20% | **1,325,138%**, sign reversed (FD `-1.01313982553419e+02` against analytic `+7.64611787804267e-03`) | **HIT** (carries no verdict of its own) |
| **R1-P16** | control cost | wall 60 – 200 s, 4.0 – 13.3 core-min, RSS < 3 GiB | **57 s, 3.800 core-min**, RSS **1.425 GiB** | **MISS on wall and core-min (below the band by 3 s / 0.2 core-min); HIT on RSS** |

**Score: 15 HIT, 1 SPLIT, 1 MISS.** The MISS is reported as a miss against the registered table,
not against a re-derived one.

### The two misses, said plainly rather than absorbed

**R1-P9 on `shape[5]`** is the interesting one. The prediction was that both flagged components'
analytic magnitudes would **decrease** by 0.01 – 3.0%, "consistent with R1-P8b". `twist[1]` did
(0.5510% toward zero). **`shape[5]` moved 9.0905% AWAY from zero**, three times outside the band
and in the opposite direction. **So the patch's analytic delta is NOT a uniformly signed shift
even within one rung of one case.** That weakens — it does not strengthen — any general claim
about the patch's direction, and it is registered here as such. It also means the R1-P8b mechanism
is a statement about `shape[115]` and `twist[1]` across two rungs, not about the patch's action on
an arbitrary component.

*A second-order note, offered as an observation and not as a claim: `shape[5]`'s move happens to
take it toward FD (6.2238% → 2.3010%), but `shape[5]` fails the step-consistency gate at 8.2023%
and **its FD reference is therefore not trustworthy** — which is exactly why it carries NOT A
RESULT and why no rescue is attempted here (§4, R1-P9's named alternative).*

**R1-P16** undershot its wall band. The control ran 57 s against a 60 – 200 s band derived by
scaling rung 2's measured 152 s control. The box was less contended at 20:58 than the derivation
assumed. Reported as a miss.

---

## 4. The controls, and why the zeros in this record are evidence

Three of this item's central findings are **negative** results — R1-P5's "the FD column did not
move", R1-P6's "no digit differs", R1-P4's "the adjoint is identical". CLAUDE.md standing rule 3
says a zero from a reader not shown able to see a non-zero is not evidence. Each is therefore
preceded by a control that was **run, not asserted**:

* **`guard_selftest.sh`, all five limbs, in this session, before any arm launched.** Limb 1
  planted thresholds no container can satisfy and required `mem_guard.sh` to **kill** — it fired
  at exit 4 in 14 s and the container was gone. Limb 2 planted thresholds no container can breach
  and required it **not** to — exit 124, container alive. Limbs 3–5 planted a rebuild log carrying
  a masking `Reading Coloring` line, a genuine warm-cache log, and a log with rung 3's colour
  count, and got exits 3, 0 and 5. `GUARD_SELFTEST_PASS` was written at 20:45:55 and `drive.sh`
  refused to launch without it and without it being newer than both guard scripts.
  **This is the L-239 repair, exercised: rung 2's record-only watcher would have passed limb 1 by
  doing nothing.**
* **The FD comparator's planted difference.** Before comparing the three arms' FD columns, the
  reader corrupted one digit of one perturbed CD value in a copy of the archived vector and
  required the same comparison path to see it. It reported `1 of 16 perturbed CD values differ`.
  Only then was the real comparison run.
* **The L2 reader's planted difference.** Before reporting the R1-P10 L2, the reader planted a
  0.1234% relative perturbation on component 0 of the shipped vector and required the L2 it
  computes to come back at the arithmetically expected size: it reported `1.918239e-03%` against
  an expected `1.918239e-03%`. A refusal (exit 2) was wired for either control failing.

---

## 5. Departures and limitations found during execution, disclosed

1. **The §12 pre-flight command as registered does not run.** Step 3 of the registered launch
   sequence hashes `os.path.join(os.path.dirname(idwarp.__file__), "../libidwarp.so")`. That path
   does not exist in either image: the library is **in-package**, at
   `/opt/idwarp_patched/idwarp/libidwarp.so` (patched) and
   `…/site-packages/idwarp/libidwarp.so` (shipped). The registered command returned
   `FileNotFoundError`. **This is a defect in §12's illustrative command, not in a gate, threshold,
   band, cap or label** — §12 is the convenience listing, and the binding requirement is R1-P1(a),
   which asks for the md5 of "the `libidwarp.so` adjacent to the loaded package" printed per rank.
   The pre-flight was re-run resolving the path (in-package first, then one level up, printing the
   path it resolved), and **D1 in the run script does the same** — so R1-P1(a) is measured, not
   inferred. Both images were checked, on all 4 ranks:
   * patched: `/opt/idwarp_patched/idwarp/libidwarp.so`, md5 `85f59e87253e0a71a813f64ca6e4c425`,
     491,344 bytes, version `2.6.2`, on ranks 0–3.
   * shipped: `…/site-packages/idwarp/libidwarp.so`, md5 `f0fcb488e0e98156575cd19548e91663`,
     **491,344 bytes** — the same size — version `2.6.2`, on ranks 0–3.
   * **The identical byte count on both stacks is the concrete demonstration of `BUILD.md` §2's
     point:** neither the version string nor the file size discriminates. Only the hash does.
   **Cost consequence, reported as a miss:** the §8 table budgets **0.200 core-min** for one
   pre-flight. Three were run (one failed, then one per image, at 0.200 + 0.133 + 0.133) =
   **0.466 core-min**. Over that line by 0.266 core-min; the item ceiling is unaffected (§6).
2. **`coloring_guard.sh` returned exit 7 on arm R1-C, and that is correct rather than a failure.**
   The `fd1wrong` branch runs no adjoint, so it never reads the colouring cache and neither
   signature can appear. Exit 7 is the guard's registered "neither signature reachable" code.
   **R1-P3 is therefore measured on R1-A and R1-B and is NOT MEASURED on R1-C** — stated here
   rather than counted as a pass by silence.
3. **`stage.sh` and `drive.sh` were written after the pre-registration commit and committed before
   they ran**, as §12 requires (commit `789ed3b6`). `analyse_r1.py` was likewise committed before
   it ran. **No external comparator is registered by this pre-registration**; the grading
   instrument is the FD3 TABLE printed by the **unchanged** `fd3` branch — the identical code path
   that produced the archived shipped row, D1/D2/D2b being log-only and D3 a new branch — plus §4's
   per-component rule. `analyse_r1.py` is a **reader**, not a replacement grader, and says so in its
   own docstring.
4. **The `runScript_fd3.py` → `runScript_fd3p.py` diff was asserted before staging**: exactly **4
   insertion hunks, 0 deletions, 0 modifications**. Diff on disk at
   `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/runScript_fd3p.diff`. No numeric option, DV
   set, scheme, tolerance, step or component ordering in the `fd3` branch was changed, and the
   identical `runScript_fd3p.py` ran on all three arms.
5. **The shared git index.** At the time this item ran, the shared index staged **deletions** of
   files that exist in the worktree and in HEAD — including this item's own newly committed
   `stage.sh`, `drive.sh` and `analyse_r1.py`, which appeared as staged deletions the moment they
   were committed. That is the signature of a **stale index snapshot**, not of anyone deleting
   anything. **The index was not touched** — it is the chief's call (CLAUDE.md rule 10). All ten
   frozen files of both A3 items were verified byte-identical to their pre-registration blobs
   before anything ran, and every commit here used the private-index protocol with a post-commit
   verify showing only this item's paths.

---

## 6. Cost, against the registered table and not a re-derived one

| item | registered | measured | inside band? |
|---|---|---|---|
| R1-A PATCHED `fd3` | 418 s / 27.9 core-min, band 16.4 – 42.7 | **344 s / 22.933 core-min** | yes |
| R1-B SHIPPED `fd3` | 418 s / 27.9 core-min, band 16.4 – 42.7 | **311 s / 20.733 core-min** | yes |
| R1-C trivial baseline | 110 s / 7.3 core-min, band 4.0 – 13.3 | **57 s / 3.800 core-min** | **no — below the band (R1-P16 MISS)** |
| guard selftest | ~110 s / 1.8 core-min, band 0.5 – 2.0 | 68 s wall (20:44:47 → 20:45:55), 4 `alpine` containers at `--cpus=1` ⇒ **~1.13 core-min** | yes |
| per-rank pre-flight | 0.200 core-min | **0.466 core-min** (3 runs; see §5 item 1) | **no — over by 0.266** |
| launch-condition polling | 0.000 | **0.000** — the gate opened on **poll 1** for all three arms | yes |
| rung-1 plateau sweep | not run, declined by name | **not run** | — |
| fresh colouring pass | not run, cache carried | **not run** — 0 `Calculating` on every arm | — |
| **TOTAL** | predicted **65.1**, band 37.5 – 100.3 | **49.06 core-min** | **inside the band** |

**Solver-arm subtotal: 47.466 core-min.** Item total **49.06 core-min**.

**REGISTERED CEILING 127.0 core-min — used 38.6% of it. HARD STOP not approached; no overrun.**

**Dollars: 49.06 core-min = 0.8177 core-hours × $0.0513/core-hour = $0.0419.**
`cost_basis`: c7a.4xlarge at $0.0513/core-hour, **owner-stated 2026-08-21/22 and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so this dollar figure is REPORTED-BY-OWNER, NOT MEASURED.** The
core-minute figures are measured (wall × ranks ÷ 60 from `ledger.txt`).

**Contention disclosure.** The box was shared throughout. Live at launch and not touched: 4
`buoyantBoussinesqSimpleFoam` (T-family), 1 `simpleFoam` (closure), and a peer dafoam container
`b3rss_D_serial` on `dafoam-subpclu:v2` (B3 peak-RSS attempt 2). `load1` ranged 8.4 – 18.9 during
the arms. **The 344 s and 311 s walls are contended walls and are NOT offered as a clean cost
basis for scaling.** Measured inflation against the 246 s idle basis: **1.40×** (R1-A) and
**1.26×** (R1-B), both inside the registered 1.0 – 2.6×.

---

## 7. What this rung still cannot see

Every item of §9 stands as registered. The two that this run's numbers make sharper:

* **§9 item 1 — three of four FD components carry no verdict**, and the run confirmed why:
  `shape[5]`'s analytic moved 9.0905% while its FD reference is untrustworthy at 8.2023%
  step-consistency. **R1-P10 measured a 0.940327% patch effect across all 120 shape components,
  and 119 of them have no FD beside them.** Unlike rung 2, this rung found **zero** analytic sign
  flips — but that is a statement about 120 numbers nobody has FD'd, not a clean bill.
* **§9 item 2 — the plateau at rung 1 is a two-point read, not a proved plateau.** No third step
  was bought, by design (§5). This item claims a measured two-point step-consistency check at a
  step with measured floor clearance, and **does not claim `DAFOAM_CHARTER.md` §3 is satisfied at
  rung 1.**

**One thing this run closes that was open before it.** R1-P6 was registered as a by-product so it
could not be claimed as a discovery afterwards, and it landed: **the literal
`dafoam/opt-packages:latest` reproduces the archived `dafoam-subpclu:v1`-with-env-unset ‡ row
bit-for-bit at rung 1.** That ‡ equivalence assertion carries every SHIPPED-equivalent row on the
A3 sweep ladder (`LADDER_A_STATUS.md:33-36`) and **had never been tested directly at any A3 rung.**
It is now tested at one. **This is a finding for the supervisor to route, not a ladder edit made
here** — this item edits no board, no satellite and no frozen file.

---

## 8. Standing statements

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.

**Three rows, never merged.** The archived SHIPPED-equivalent ‡ row (cited), the fresh
literal-SHIPPED row (measured, arm R1-B), the PATCHED row (measured, arm R1-A). **A patched grade
never replaces a shipped grade** — that requires the fix shipping upstream or Sanaa formally
adopting a forked toolchain, and it is her call, not a session's (R11).

**Toolchain identity is an image ID and a library hash, never a version string.** Both stacks
report `idwarp 2.6.2` **and identical 491,344-byte libraries**. Only the md5 separates them.

**Nothing is filed, sent, uploaded, posted, registered or pushed. Filing stays NOT APPROVED and is
Sanaa's alone.**

## 9. Artifacts

| what | path |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/` |
| arm logs | `patched.log`, `shipped.log`, `wrongstep.log` (in the run root) |
| ledger | `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/ledger.txt` |
| RSS traces | `rss_patched.txt`, `rss_shipped.txt`, `rss_wrongstep.txt` |
| guard selftest record | `guard_selftest.log`, `GUARD_SELFTEST_PASS` |
| staging record + script diff | `stage.log`, `runScript_fd3p.diff`, `runScript_fd3p.py` |
| launch-gate record | `launch_condition.txt`, `lever_echo_{patched,shipped,wrongstep}.txt` |
| reader output | `reader_output.json` |
| archived shipped row (read-only, cited) | `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/fd3_run.log` |
