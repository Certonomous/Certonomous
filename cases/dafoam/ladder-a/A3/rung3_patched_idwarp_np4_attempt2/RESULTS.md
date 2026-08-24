# A3 ONERA M6, sweep rung 3 (79,560 cells) — the patched-IDWarp column at np=4, ATTEMPT 2: RESULTS

**Assembled 2026-08-24T17:18:00Z** (`date -u`, read in the shell invocation that wrote this file).

Graded against `PREREGISTRATION.md`, frozen at **`606930b4`** and amended before first compute at
**`8a0b440d`** (Amendment 1, §15: launch-gate memory limb `19.65 → 25.0 GiB`). **This file edits no
frozen file.** `PREREGISTRATION.md`, `stage.sh`, `drive.sh`, `coloring_guard.sh`,
`guard_selftest.sh`, `identity_stop.sh`, `mem_guard.sh` and `shipped_cd_checkpoints.txt` are
untouched by this record.

Run root: `/home/ubuntu/certonomous-runs/P5-a3-rung3-patched-attempt2/`
Executed 2026-08-24, 16:27:59 – 16:38:53 UTC. **Zero compute was spent by this grading lane.**

Nothing here has been added to `docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md`,
`docs/NUMERICS_KNOWLEDGE.md`, `LADDER_A_STATUS.md`, `cases/dafoam/INDEX.md` or any charter (§7,
Escalation). Drafted text for those is in **§9**, for the dafoam supervisor to land or discard.
**Nothing is filed, sent, uploaded, posted, registered or pushed. Filing stays NOT APPROVED and is
Sanaa's alone.**

---

## 1. Verdict

# GATE FAIL — adjoint, inherited

**The patched column's rung-3 adjoint cell.** This is the label §4 item 3 registered in advance for
the predicted outcome, and it is the outcome that occurred.

**And the finding the item was bought for, which is the reason the gate verdict is sayable at all:**

> **IDENTITY CONFIRMED — 11 of 11 printed checkpoints bit-identical, iterations 0 through 1000.**
> The patched-IDWarp CD adjoint reproduces the SHIPPED-equivalent ‡ rung-3 residual path digit for
> digit, in a **stagnating** regime, at 79,560 cells, at np=4.

**The stop is not a measurement failure, and the pre-registration said so before the run.**
`identity_stop.sh` killed the container on the full match and exited **5** — the row registered at
`PREREGISTRATION.md` §7's stop-rule table (~:562) as *"DELIBERATE STOP, identity CONFIRMED. Not a
measurement failure; the finding is complete before the stop"*, and at §10 / `DAFOAM_CHARTER.md` §7
as *a stop is not a measurement*. The finding rests on the eleven matched checkpoints, which are
complete **before** the kill fires, and **not** on the stop. `rc=137` is `128 + SIGKILL`, the
signature of `identity_stop.sh:56`'s `docker kill`, **not** of a `timeout` (which would be 124) and
**not** of a memory stop (`mem_guard.sh` exited 0, no `MEMORY_STOP_FIRED.patched` exists).

**On the verdict word for the identity finding itself, stated rather than assumed.** §5 registers
**exactly one** gate for stage R3-1 — the adjoint gate — and its verdict is the `GATE FAIL` above.
The identity is a **prediction with an exact registered band (R3-P4), and it scores HIT**, 11/11. It
is the *evidence under* the gate, not a second gate: calling it `PASS` would award a gate this
pre-registration does not register, and this record declines to. What the fixed vocabulary does say
about the stop is the negative that matters and that distinguishes this attempt from attempt 1:
**this arm is NOT `NOT A RESULT`.** Attempt 1's R3-P4 was `NOT A RESULT` because zero checkpoints
were reached; attempt 2's is `HIT` because all eleven were.

**The patched FD cell at rung 3 stays `NOT A RESULT`** — not `PASS`, not `FAIL`, and explicitly not
"clean by omission" (§4 WOULD-NOT item 2, §9 item 1). No convergence ⇒ no analytic gradient ⇒ no FD
table ⇒ per `DAFOAM_CHARTER.md` §2 there is nothing to grade.

---

## 2. What this arm measured, and what it did not produce

### 2.1 Measured on this arm's own log

| quantity | value | artifact |
|---|---|---|
| checkpoints bit-identical to the frozen shipped path | **11 of 11**, iterations 0–1000 | `patched.log:893-903` vs `shipped_cd_checkpoints.txt` |
| total residual reduction through iteration 1000 | **1.3133×** (`2.121343646203e-02` → `1.615247229756e-02`) | `patched.log:893,903` |
| flatness, iterations 200 → 1000 | relative change **2.239e-03** | `patched.log:895,903` |
| flatness, iterations 900 → 1000 | relative change **1.446e-06** | `patched.log:902,903` |
| iterations executed of the 4000 GMRES cap | **1000** — stop deliberate, not exhaustion | `patched.log:891,903` |
| preconditioner assembly | **complete**, `dRdWTPC: 0 → 1354 of 1355`, 60.02 → 170.76 s | `patched.log:868-882` |
| container peak aggregate RSS | **11.680 GiB** against a 16 GiB cap and a 15.0 GiB guard ceiling | `ledger.txt`, `rss_patched.txt` (87 samples) |
| host `MemAvailable` minimum over the arm's life | **15.2871 GiB** against an 8.0 GiB floor | `rss_patched.txt`, 87 samples at 5 s |
| guard strikes, any limb, any sample | **0** | `rss_patched.txt` |
| wall / cost | **532 s**, `t0=1787589001` `t1=1787589533`, 4 ranks ⇒ **35.467 core-min** | `ledger.txt` |

### 2.2 What the arm did NOT produce, said plainly

**This arm printed no `PetscConvergedReason` at all** — zero occurrences in
`patched.log`. It was deliberately stopped at iteration 1000 of a 4000-iteration cap, so the
terminal reason was never reached. §5's grading instrument has three components; this arm supplies
two of them and inherits the third:

| §5 instrument component | source |
|---|---|
| iteration count | **measured here** — 1000, stop deliberate |
| total residual reduction | **measured here** — 1.3133×, matching the shipped 1.31× exactly, and reached by iteration 1000 as R3-P4 registered |
| terminal `PetscConvergedReason` | **NOT measured here.** `-3` at 4000 iterations is the **SHIPPED-equivalent ‡ run's** measured value (`/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log`, cited in `shipped_cd_checkpoints.txt`'s header and at `LADDER_A_STATUS.md:35` row 11). It is carried across **by the bit-identity**, which is what the word **"inherited"** in §4 item 3's registered label means |

§5's budget-versus-wall discriminator table reads the same way: *small total reduction* — measured
here at 1.3133×; *flat at the cap* — measured here; *not resolved by raising the cap* — the shipped
run's own `3.79e-07` relative change over iterations 1300→4000, **the shipped datum, carried, not
re-measured.** A reader who wants the terminal reason measured on the patched image at rung 3 is
asking for the 3000 iterations this pre-registration decided **before the run** not to buy (§6
R3-P4: they reproduce a known stagnation at ~69% of the arm's wall). That decision is disclosed here
as a limit, not presented as a result.

---

## 3. Every registered prediction, scored

Scored against the frozen table and against no re-derived one. **The comparator's ability to see a
non-zero was proved in this session before the arm ran** (R3-P9 / CLAUDE.md rule 3), so a "no
difference found" here is evidence rather than a silent reader.

| id | what it predicts | registered band | measured | score |
|---|---|---|---|---|
| **R3-P1(a)** | 4 ranks print `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425` and an in-package `IDWARP_IMPORTED_FROM:` | exact, 4/4 | **4/4**, all `85f59e87…`, all `/opt/idwarp_patched/idwarp/__init__.py` | **HIT** |
| **R3-P1(b)** | DAOption dump contains `transonicPCOption 1;` | exact | present, `patched.log:430` | **HIT** |
| **R3-P1(c)** | zero `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` | exactly 0 | **0** | **HIT** |
| **R3-P1(d)** | the **solver's** header reads `nProcs : 4`; 4 `processor*` created | exact | `nProcs : 4` at `:83,:110,:268,:575`; the `decomposePar` utility's own `nProcs : 1` at `:50` present as registered and correctly not read as the solver's; **4** `processor*` dirs | **HIT** |
| **R3-P1(e)** | `idwarp` version string `2.6.2` — recorded as discriminating **nothing** | exact | `2.6.2` on all 4 ranks, `patched.log:25-28`. Recorded, never used as a check | **HIT** (as registered: a demonstration, not a check) |
| **R3-P2** | first `Time step continuity errors : sum local` = `1.018123970654079`, `initRes ≈ 1` on all six fields | exact to all 16 digits | **`1.018123970654079`** at `patched.log:651`; U0 `0.9999999999999994`, U1 `1`, U2 `1`, he `0.9999999999985284`, p `0.9999999999995292`, nuTilda `0.9999999999821185` | **HIT** — cold from uniform, no warm start |
| **R3-P3** | colouring **READ**, not rebuilt; colours 1355; zero `Calculating dRdW Coloring` | exact, and wired | all five strings present (`:856,:857,:864,:865,:868`); **0** `Calculating`; cache md5 `f91c25c1…` asserted pre-launch (`stage.log` assert 2); `coloring_guard_patched.log`: *cache READ confirmed, no rebuild, colours=1355*; guard rc **0** | **HIT** — the warm-cache cost basis stands |
| **R3-P4** | **THE IDENTITY** — 11 checkpoints bit-identical through iteration 1000 | exact, 11/11 | **11 of 11**, string-for-string, re-verified independently by this grading lane against the frozen file (not taken from the guard's own log) | **HIT** |
| **R3-P5** | the named alternative: the patched adjoint **converges**, `PetscConvergedReason: 2` | any iteration count | **did not occur.** Zero `PetscConvergedReason` lines; minimum printed residual `1.615247229756e-02`, **>1 decade above** the `1.0e-03` stand-down threshold, so the guard was never near standing down | **BRANCH NOT TAKEN**, as registered *not predicted*. Not scored HIT or MISS: this is a branch, not a band |
| **R3-P6** | the falsifier that would overturn rung 2: any checkpoint **differs** while residual ≥ `1.0e-03` | any differing checkpoint | **0 of 11 differ.** `identity_stop.sh` exited 5, not 6; no `PATH_DIVERGED.patched` exists | **BRANCH NOT TAKEN — and here that is informative**, unlike attempt 1. Eleven checkpoints were printed and compared, and limb 7 proved in this session that the comparator sees a real 5th-significant-figure difference. See §3.1 |
| **R3-P7** | memory: peak RSS **9.0–14.0 GiB** vs a 16 GiB cap; host `MemAvailable` never below **8 GiB** | both limbs | RSS **11.680 GiB** — inside. Host minimum **15.2871 GiB** — **7.29 GiB above** the floor, never approached | **HIT, both limbs.** In attempt 1 the HOST limb scored MISS (floor breached at 7.3767 GiB). The band was carried unchanged, not widened, and it now holds |
| **R3-P8** | wall **445–1157 s**, core-min **29.7–77.1**; point `757 s` / `50.5`, inherited and UNVALIDATED (R4) | band | **532 s / 35.467 core-min** — inside both bands | **HIT on the band** (which is what §6 registers as the band). **The point estimate misses by −225 s / −29.7%** and the miss is reported as a miss in §7, not excused by its inheritance |
| **R3-P9** | the comparator is proved able to SEE a difference, at zero solver cost, in **this** session | exits 5 / 6 / 7 on three planted inputs | limb 6 exit **5** (match on the real shipped log), limb 7 exit **6** (rung 2's real path seen as different), limb 8 exit **7** (stands down on a converging path); plus limbs 1–5 at exits 4, 124, 3, 0, 5. **8 of 8**, 16:28:09→16:29:17Z, `GUARD_SELFTEST_PASS` newer than all four guard files it names | **HIT** |
| **R3-P10** (original, superseded by A1.3, retained and scored) | gate `free_cores ≥ 4` AND `MemAvailable ≥ 19.65 GiB` opens; point YES, confidence **0.6** | not exit 9 | opened on **poll 1**; against the struck 19.65 limb the margin would have been **+7.54 GiB** | **HIT** |
| **R3-P10′** (amended, the version the gate executed) | gate `free_cores ≥ 4` AND `MemAvailable ≥ 25.0 GiB` opens; point YES, confidence **0.25** | not exit 9 | opened on **poll 1 of ≤360**, `MemAvailable` **27.19 GiB** (`margin_mem_GiB=+2.19`), `free_cores` **13** (`margin_cores=+9`), `load1` 5.49, 16:30:00Z | **HIT** — and see §5.2 on the confidence |
| **R3-P11** | peak container RSS, point **11.65 GiB**, band **[9.2, 15.0] GiB** | band, scored separately from P7 | **11.680 GiB** — inside; point off by **+0.030 GiB (+0.26%)**. The preconditioner assembly **completed**, so the P11 incompleteness clause does not apply and the peak is scorable | **HIT** |

**P7 and P11 did not disagree.** The informative disagreement region `(14.0, 15.0]` — where P7 would
score MISS and P11 HIT — was not entered, so this run says nothing about which basis was right
there. §9 item 10's open question, *which of the three recorded peaks (9.202 / 11.65 / 17.19 GiB)
governs this configuration*, is **not resolved**; what is now on the record is that the complete
11.65 GiB basis reproduced to within 0.030 GiB at iteration 1000.

**Two branches not taken, and one prediction whose point missed inside a band that held.** Nothing
was scored MISS. Nothing was scored NOT A RESULT.

### 3.1 Why R3-P6's silence counts here and did not count in attempt 1

Attempt 1's record states the discipline exactly: R3-P6 *"did not fire, and could not have, because
no checkpoint was printed. This is explicitly not evidence that it would not have fired"*
(`../rung3_patched_idwarp_np4/RESULTS.md:107`). Attempt 2 is the opposite case, and the difference
is the whole reason CLAUDE.md rule 3 exists:

1. **Eleven checkpoints were printed and compared**, iterations 0 through 1000.
2. **The comparator was proved able to see a non-zero, in this session, before the arm ran.** Limb 7
   planted A3 rung 2's *real* CD adjoint path — a genuine path from the same solver and case family
   differing in the **5th significant figure at iteration 0** (`2.121211553380e-02` vs
   `2.121343646203e-02`) — and `identity_stop.sh` returned exit **6, DIVERGED**.
3. **The comparison is string-for-string**, and this grading lane re-ran it independently against
   the frozen `shipped_cd_checkpoints.txt` rather than accepting `identity_stop_patched.log`'s own
   claim. 11 of 11 identical, 0 mismatches, 0 checkpoints absent, no checkpoint beyond 1000.

So the zero here is a **planted-control-backed zero**, and R3-P6's non-firing is a finding.

---

## 4. What this does and does not say — the §4 register, applied

§4 was carried verbatim from attempt 1's own pre-registration and frozen before this run precisely
so that no reading of it could be chosen to fit the number. Applied unchanged:

### It DOES say

1. **The patched toolchain inherits rung 3's conditioning wall unchanged.** Adopting
   `dafoam-idwarp-rot:v1` **buys nothing at rung 3 and costs nothing at rung 3** — measured, not
   assumed. That is a direct input to the toolchain-adoption question on Sanaa's desk. It remains
   **her** call (R11, `../../FAMILY_SUPERVISION_GUIDELINES.md` §3.4).
2. **A second, independent confirmation that the patch enters strictly after the Krylov solve** —
   now in a **stagnating** regime at 79,560 cells, where rung 2 showed it on a **converging** solve
   (11/11 pairs, `reason 2`) at a different mesh size and residual regime. **Two regimes, one
   conclusion.**
3. **The patched rung-3 adjoint cell is `GATE FAIL — adjoint, inherited`**, on the same instrument
   as the shipped row's, with §2.2's inheritance chain named. **Row 12b's rung-3 cell moves
   `PENDING → GATE FAIL (adjoint)`** — reported as the registered consequence for the supervisor to
   land, **not edited here** (§7, Escalation).
4. **Memory did not bind, and that is new.** The arm ran to its registered stop with the host floor
   never approached (minimum 15.2871 GiB against an 8.0 GiB floor, 0 strikes on 87 samples) and its
   own RSS at 11.680 of a 15.0 GiB ceiling. **Attempt 1's memory stop is not reproduced.** §4
   WOULD-NOT item 5's branch — *NOT A RESULT, stopped by memory* — did not occur, and §14's
   registered end of the line (no third attempt without Sanaa) is **not** triggered.

### It does NOT say

1. **Nothing about the rotation patch's correctness.** Stated here at the headline and not in a
   limits section, as §4 requires. The patch is downstream of the solve that stagnated; attributing
   the stagnation to it is a category error, and this record makes no such attribution.
2. **It is not a gradient verdict of any kind.** The patched FD cell at rung 3 stays **`NOT A
   RESULT`**.
3. **It does not extend rung 2's degradation finding to rung 3 in either direction.** See §4.1.
4. **It does not locate the ladder's conditioning ceiling.** Still bracketed between **42,120 and
   79,560 cells and unlocated** (`../grading_confirmation/RESULTS.md:262-265`). Nothing here narrows
   the bracket, and nothing here says the M6 adjoint is unreachable at 79,560 cells by any means —
   only that a configuration working at two rungs stagnates at this one, **with memory to spare**.
5. **It is not a memory result** in the §4 sense — no conditioning claim rests on memory here in
   either direction. What §2.1 records is that the memory *envelope* behaved as R3-P7/P11 predicted;
   that is a prediction scored, not a conditioning finding.
6. **It does not make the shipped rung-3 `GATE FAIL` any more or less true.** A patched number never
   moves a shipped grade. **Row 11 stands exactly as it is.**

### 4.1 Rung 2 specifically — what this says and what it cannot

**What it says.** The outcome registered as the one that **would overturn rung 2** — R3-P6, the path
differing while still stagnating — **did not occur**, on eleven printed checkpoints, with a
comparator proved able to see a real difference (§3.1). Therefore:

* *"The patch enters strictly after the Krylov solve"* is **NOT falsified at rung 3.**
* Rung 2's two-image comparability argument, on which its whole `PASS` rests, is **not in question.**
* Rung 2's evidence now has a **second instance in a second residual regime**: converging at rung 2,
  stagnating at rung 3, identical in both.

**What it cannot say, and this is the load-bearing half.**

1. **A non-falsification is not a re-proof.** Rung 2's `PASS` rests on rung 2's own record and is
   **unmoved** by this item. This arm did not re-grade it, could not have, and does not.
2. **It says nothing whatever about rung 2's gradient-degradation finding.** Rung 2 measured the
   patch making `shape[115]` **9.2084×** and `twist[1]` **3.39×** worse against a fixed FD reference
   (`../rung2_patched_idwarp_np4/RESULTS.md:169-171`, Correction 1). **Rung 3 produced no gradient
   at all** and is **silent on degradation in both directions** — it neither confirms, extends,
   weakens nor rescues it. Only rungs 1 and 2 can speak to that, and the rung-1 companion item is
   where that question is actually bought.
3. **The identity is consistent with the mechanism; it does not prove it.** §9 item 9, registered in
   advance: *two rungs of one case in two residual regimes is stronger than one, and is still two
   rungs of one case.*
4. **The comparator is `dafoam-subpclu:v1` with the env unset — SHIPPED-equivalent ‡, not
   `dafoam/opt-packages:latest`.** This item does not close that gap, exactly as rung 2 did not. The
   **‡ label stays on the comparator row.**

### 4.2 What still stands open, unchanged by this item

`DAFOAM_CHARTER.md` §5's *serial before parallel* remains **unsatisfied on A3** — np=4, `scotch`, one
partition, and **A3 still has no decomposition datum** (§9 item 5, §14 disposition 3). Regime 2 of
the rotation defect is not probed (§9 item 6); the `CL` rows are unmeasured on every image at rung 3
(§9 item 7); the 399,360-cell campaign keeps **`PENDING`** (§9 item 8).

---

## 5. The instruments, and how they behaved

### 5.1 Guards — every registered stop, and what it did

| guard | armed | outcome | exit |
|---|---|---|---|
| `identity_stop.sh` | 16:30:01Z, `final_checkpoint=1000`, `conv=1.0e-03` | **IDENTITY CONFIRMED, 11/11, deliberate stop at 16:38:52Z** | **5** |
| `mem_guard.sh` | 16:30:01Z, `rss_ceiling=15.0 GiB`, `host_floor=8.0 GiB`, 3 strikes @ 5 s | **did not fire** — 87 samples, max strikes **0**, 0 samples above the RSS ceiling, 0 below the host floor | **0** |
| `coloring_guard.sh` | 16:30:01Z, `dRdWColoring_4`, `expect_colours=1355` | **did not fire** — cache READ confirmed at 16:31:16Z, no rebuild, colours 1355 | **0** |
| `guard_selftest.sh` | 16:28:09Z | **8 of 8 limbs**, `GUARD_SELFTEST_PASS` 16:29:17Z | pass |
| `timeout 2600` | at launch | not reached — 532 s of 2600 s used | — |

**HAZARD, and it is a real one for anyone reading the run root by `ls`.** Six marker files in the run
root carry a `.gs_*` suffix — `MEMORY_STOP_FIRED.gs_pos`, `PATH_DIVERGED.gs_id_differ`,
`IDENTITY_CONFIRMED.gs_id_match`, `PATH_CONVERGING.gs_id_conv`, `COLORING_REBUILD_DETECTED.gs_col_pos`
and `COLORING_COUNT_MISMATCH.gs_col_cnt`. **Every one of them is a guard-SELFTEST artifact written
against planted inputs at 16:28:09–16:29:17Z, before the arm existed. None of them is the arm.** The
arm's markers carry the suffix **`.patched`**, and this grading lane verified by direct test that the
run root contains **exactly one** such file — `IDENTITY_CONFIRMED.patched` — and that
`MEMORY_STOP_FIRED.patched`, `PATH_DIVERGED.patched`, `COLORING_REBUILD_DETECTED.patched` and
`COLORING_COUNT_MISMATCH.patched` **do not exist**. A reader who counts `MEMORY_STOP_FIRED.gs_pos`
as the arm having been stopped by memory is reading the proof that the guard *can* fire as the guard
*having* fired. `TIME_PROVENANCE.txt` §7 flags this same trap independently.

### 5.2 The gate, and Amendment 1's tightened limb

`launch_condition.txt` carries the `GATE_OPEN` record Amendment 1 §A1.4 made a recording duty,
quoted verbatim as §A1.4 requires:

> `2026-08-24T16:30:00Z patched GATE_OPEN poll=1 limb_GiB=25.0 MemAvailable_GiB=27.19 margin_mem_GiB=+2.19 free_cores=13 margin_cores=9 floor_GiB=8.0 floor_sampled_by=mem_guard.sh_MemAvailable_at_5s`

**The amended gate opened on the first poll of a 360-poll window**, at 82% of `MemTotal` free.
R3-P10′ was registered at confidence **0.25**, and the reasoning behind that number — a 1.26 GiB
freeze margin, a co-tenant with room to grow, and a fleet that had made the gate *unreachable* for
the whole of attempt 1's window — was honest reasoning that the day did not vindicate. The margin at
launch was **+2.19 GiB, larger than the +1.26 GiB at the freeze**: the box got quieter between the
freeze and the launch, not busier. **The confidence was under-stated, and it is recorded here as
under-stated rather than quietly forgotten.** One draw is not a calibration; §9 offers it as a
candidate observation only.

**And the gate did what Amendment 1 bought it for.** Attempt 1 launched at 16.02 GiB and breached the
8.0 GiB floor 60 s later. Attempt 2 launched at 27.19 GiB behind a `8.0 + 15.0 + 2.0` limb and the
host floor was never approached — minimum `MemAvailable` **15.2871 GiB**, 7.29 GiB of headroom, 0
strikes. The A1.2 co-tenant exposure (the named 4.0 GiB gap between arm O's registered 2.0 GiB
ceiling and its enforced 6.0 GiB cap, ruled on at
`SUPERVISOR_RULING_2026-08-24_cotenant_allowance.txt` in the run root) **was not realised**: even at
the run's minimum the host had 7.29 GiB above the floor, more than the 4.0 GiB gap. That is one draw
on one day and is **not** a proof of sufficiency — the ruling says so, and this record does not
upgrade it.

### 5.3 Freeze verification — re-done by this lane, not relayed

The dafoam supervisor reported both checks independently. **This grading lane re-ran both rather than
accepting the relay** (CLAUDE.md rule 9: a delegate's test is evidence, not the supervisor's read —
and the same cuts the other way).

1. **All eight grading-path files hash equal to their committed blobs at HEAD**, verified by
   `git hash-object` against `git rev-parse HEAD:<path>`: `PREREGISTRATION.md`
   (`fa488e7cedf5385b5a4b30f2370a3abfc8fecaf9`, the `8a0b440d` Amendment-1 blob), `drive.sh`,
   `stage.sh`, `coloring_guard.sh`, `guard_selftest.sh`, `identity_stop.sh`, `mem_guard.sh`,
   `shipped_cd_checkpoints.txt`. **8 of 8 MATCH.** The `606930b4` pre-amendment
   `PREREGISTRATION.md` blob is `9f7ec6f1…` and is correctly superseded.
2. **The five carried files also equal their `97a54c07` blobs** (ruling R1, §11):
   `shipped_cd_checkpoints.txt`, `identity_stop.sh`, `mem_guard.sh`, `coloring_guard.sh`,
   `guard_selftest.sh` — **5 of 5 MATCH**, so `mem_guard.sh` and the comparator are byte-identical to
   attempt 1's, as A1.4 asserted.
3. **The eleven checkpoints re-compared independently** against the frozen file as strings, by this
   lane, not read from `identity_stop_patched.log`: **11 identical, 0 mismatched, 0 absent, no
   checkpoint printed beyond iteration 1000.**
4. **`GUARD_SELFTEST_PASS` (16:29:17Z) is newer than all four guard files it names** (all dated
   2026-08-23 19:59–20:01), so the licence-to-run test held.

---

## 6. Deviations and discrepancies found

**Deviations from the frozen document: none.** No gate, threshold, band, cap or label was moved. No
frozen file was edited. No second budget was taken. Neither the `ct_cd` discriminator (§3 departure
6) nor stage R3-2 was launched, under any branch, as §7's decision rule requires.

**Discrepancies found between the artifacts and the numbers reported to this lane in its brief:**

1. **Host `MemAvailable` minimum.** The brief carried *"never below ~15.33 GiB"*. Parsed from all 87
   samples in `rss_patched.txt`, the true minimum is **15.2871 GiB**. The difference is immaterial to
   every verdict — both are far above the 8.0 GiB floor — but the artifact wins and both are shown
   (`REPORTING_CHARTER.md` / L-1). **The figure this record uses is 15.2871 GiB.**
2. **Guard-self-test cost.** The brief's 1.133 core-min is confirmed: 16:28:09Z → 16:29:17Z = **68 s
   at 1 rank = 1.1333 core-min**. §8's registered line is 1.2. No discrepancy.
3. **The pre-flight's wall is not separately instrumented anywhere in this item** — see §7.1. This is
   a gap in the record, not a discrepancy, and it is stated rather than filled with a guess.

---

## 7. Cost — measured spend, and §7.2's registered predicted-versus-actual comparison

**`cost_basis`: c7a.4xlarge at $0.0513/core-hour, owner-stated 2026-08-21/22 and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure below is REPORTED-BY-OWNER, NOT MEASURED,
and every one is DERIVED from a core-minute figure at that rate.** Core-minutes are measured from the
run's own logs and `ledger.txt`.

### 7.1 Actual spend, per §8 line

| §8 line | ranks | measured wall | measured core-min | basis |
|---|---|---|---|---|
| **R3-A** PATCHED stage 1, `ct_cd`, identity stop at iteration 1000 | 4 | **532 s** | **35.467** | `ledger.txt` (`t0=1787589001`, `t1=1787589533`) |
| guard selftest (2 `alpine` containers + 6 file-only limbs) | 1 | **68 s** | **1.133** | `guard_selftest.log` first and last stamps, 16:28:09Z → 16:29:17Z |
| per-rank provenance pre-flight (no solver, no case) | 4 | **≤ 20.0 s, BOUNDED NOT MEASURED** | **0.133 registered / ≤ 1.333 bounded** | see the note below |
| launch-condition polling | — | 1 poll of ≤ 360 | **0.000** | `launch_condition.txt`; host-side `ps`/`awk`, no container |
| staging (`stage.sh`) | — | < 1 s | **0.000** | `stage.log`; host-side, no container, not a costed §8 line |
| shipped twin re-run | — | **not run — declined by name, §2** | **0** | — |
| fresh colouring pass | — | **not run — cache carried, §3 departure 2** | **0** | — |
| `ct_cd` discriminator (§3 departure 6) | — | **not run — R3-P6 did not fire** | **0** | — |
| stage R3-2, the FD arm | — | **not run — R3-P5 did not fire; needs its own pre-registration (§5)** | **0** | — |
| **TOTAL, registered pre-flight basis** | | | **36.733** | |
| **TOTAL, conservative pre-flight bound** | | | **37.933** | |

**The pre-flight note, because a bounded figure must say it is bounded.** §12 step 3 is a bare
`docker run` and **no script in this item writes a `t0`/`t1` for it**; `preflight.log` carries no
timestamps. What is on disk bounds it: `guard_selftest.log`'s terminal stamp is **16:29:17Z** and
`preflight.log`'s mtime is **16:29:37.020Z**, so the step took **≤ 20.0 s wall**, container startup
included, and at `--cpus=4` that is **≤ 1.333 core-min**. §8's registered line is **0.133 core-min**
(attempt 1's measured 2 s at 4 ranks). This record carries **both**, uses the conservative bound for
the ceiling test, and states plainly that **the pre-flight's wall in attempt 2 is not measured.**

**Gross and cleaned (§7.2 item 1).** `COMPUTE_BUDGET_CHARTER.md` §2's 3600-s stall rule matches **no
row**: the longest wall in the table is the arm's **532 s**, then 68 s, then ≤ 20 s. **Cleaned =
gross = 36.733 core-min** (bound 37.933). Stated rather than left blank.

**Dollars, DERIVED at $0.0513/core-h, never measured:**

| | core-min | core-h | $ derived |
|---|---|---|---|
| arm R3-A | 35.467 | 0.591117 | **$0.0303** |
| guard selftest | 1.133 | 0.018889 | **$0.0010** |
| pre-flight (registered / bound) | 0.133 / ≤1.333 | 0.002222 / ≤0.022222 | **$0.0001 / ≤ $0.0011** |
| **item total, attempt 2** | **36.733** (bound 37.933) | 0.612217 | **$0.0314** (bound **$0.0324**) |

**Against the ceiling.** **HARD CEILING 176.0 core-min.** Used **36.733 core-min = 20.9%** (bound
37.933 = 21.6%). The worst case by construction, 174.7, was not approached. **No overrun. No second
budget requested, offered or taken.**

### 7.2 Predicted versus actual — the registered comparison

| §8 line | predicted | actual | ratio actual/predicted |
|---|---|---|---|
| **R3-A**, wall | **757 s** point, band 445–1157 s | **532 s** | **0.703** — inside the band |
| **R3-A**, core-min | **50.5** point, band 29.7–77.1 | **35.467** | **0.702** — inside the band |
| guard selftest | 1.2 | 1.133 | **0.944** |
| per-rank pre-flight | 0.133 | ≤ 1.333, not measured | **not stated as a ratio — the actual is bounded, not measured** |
| launch-condition polling | 0.000 | 0.000 | **exact (0/0)**, gate opened on poll 1 of ≤360 |
| **TOTAL** | **51.8**, band 31.0–78.4 | **36.733** (bound 37.933) | **0.709** (bound **0.732**) — inside the band |
| against the ceiling | 176.0 | 36.733 | **0.209** |

**Gap attribution, split three ways, with waste separately named and never laundered into the others
or into the ratio's explanation (`COMPUTE_BUDGET_CHARTER.md` §6).**

**CONTENTION — and it is essentially the entire gap, in the *under* direction.** §8 derived the point
estimate as `445 s idle basis × 1.7× contention point`, the 1.7 taken from a **1.0–2.6×** band
measured on this box at rung 2 (arm P-A: 955 s against a 452 s idle basis, **2.11×**). The realised
factor was **532 / 445 = 1.1955×** — near the **bottom** of the registered band. The box was quiet:
**13 free cores** and **27.19 GiB** `MemAvailable` at the gate, `load1` 5.49, host `MemAvailable`
never below 15.2871 GiB for the whole run. Arithmetically, `(1.7 − 1.1955) × 445 s = 224.5 s`, which
is **14.97 of the 15.033 core-min** total arm gap; the residual **0.06 core-min** is rounding on the
756.5 → 757 point.

**MISPREDICTION — named, and not excused by the point estimate's inheritance.** The **1.7×
contention point missed by +42%**. §6 R3-P8 registers that the 757 s point is **INHERITED from
`97a54c07` §8 and UNVALIDATED** (ruling R4), and §8 requires the miss to be *reported as a miss*: it
is. **The band held; the point did not.** And there is a structural reason worth recording rather
than absorbing: **Amendment 1's tightened gate (25.0 GiB, 82% of `MemTotal`) selects for a quiet box
by construction**, so a point estimate carrying a *contended-box* multiplier is systematically high
for any arm launched behind such a gate. This is the same shape as C-4's calibration lesson (a
contention-laden per-iteration basis re-applied to a quiet box), arriving from the other direction:
here the gate itself produced the quiet box. Offered as a candidate observation in §9, not as a rule.
**The 445 s idle basis is itself still unvalidated** — the box was not idle, so the measured 532 s is
an *upper bound* on the idle wall, consistent with 445 s but not a confirmation of it.

**WASTE: 0.000 core-min.** Named explicitly rather than left implicit, and it is genuinely zero:

* no row matches the 3600-s stall rule;
* no container was aborted, re-run, restaged or relaunched — **one** arm, **one** launch;
* the gate opened on **poll 1**, so no polling wall was consumed (and polling costs no core-minutes
  in any case: it starts no container);
* the guard self-test is a **registered §8 line** (1.2 core-min) and the price of R3-P9's
  planted-difference control — it is a bought instrument, not waste;
* **the deliberate iteration-1000 stop is a registered cost decision, not waste.** It *avoided* the
  3000 iterations that reproduce a known stagnation — on the shipped run's own `ExecutionTime`
  stamps, ~69% of the arm's wall — and the finding was complete before it fired.

### 7.3 The item across both attempts

Attempt 1 and attempt 2 carry **two separate budgets of 176.0 core-min each**; §8 records attempt
1's as **spent-and-closed at 6.80 of 176.0, with no part of the unspent 169.2 carrying over.** An
underrun does not become credit.

| attempt | verdict | spend | ceiling | $ derived |
|---|---|---|---|---|
| attempt 1 (`P4-a3-rung3-patched`) | **NOT A RESULT — stopped by memory** | **6.80 core-min** | 176.0 | $0.0058 |
| attempt 2 (`P5-a3-rung3-patched-attempt2`) | **GATE FAIL — adjoint, inherited** (identity confirmed 11/11) | **36.733 core-min** (bound 37.933) | 176.0 | $0.0314 |
| **item total, both attempts** | | **43.533 core-min** (bound 44.733) | 352.0 across two budgets | **$0.0372** (bound $0.0382) |

**43.533 core-min = 0.725550 core-hours = $0.0372 derived.** The two attempts together are **0.15%**
of the $25 bar at which an item is listed for Sanaa instead of run. The **cost of producing the
result was 5.4× the cost of the failed attempt** that preceded it — the failed attempt bought the
gate arithmetic (`16.0 − 9.2 = 6.8 < 8.0`) that Amendment 1's 25.0 GiB limb was built from, and this
record does not pretend that was free.

### 7.4 Calibration row, drafted for `docs/COST_CALIBRATION.md`

Registered as a §7.2 item 5 deliverable. **This lane does not write that file** (§7, Escalation) —
the row is delivered here for the dafoam supervisor to land, and is being landed in the same commit
as this record **by the supervisor's separate instruction**, under `CLAUDE.md` rule 10's
private-index protocol and that file's own append rules, with its id re-derived from the file's tail
at commit time. Its text is §9.4 below.

---

## 8. What this record could not verify, stated plainly

1. **The terminal `PetscConvergedReason` on the patched image at rung 3.** Not measured, by design.
   §2.2 names what is measured and what is inherited.
2. **The pre-flight's wall.** Bounded at ≤ 20.0 s from two filesystem mtimes; not instrumented.
3. **Whether the 445 s idle basis is right.** The box was not idle; 532 s bounds it from above and
   confirms nothing.
4. **Whether the identity generalises beyond two rungs of one case** (§9 item 9).
5. **Which of the three recorded peaks governs this configuration** (§9 item 10). Unresolved.
6. **Whether the gate would open again.** R3-P10′ is one draw on a shared machine this lane neither
   schedules nor may ask anyone to quiet (§9 item 11, §7's standing refusals).
7. **The A1.2 co-tenant gap's sufficiency.** Not realised on this day; not proved sufficient. The
   supervisor's ruling in the run root says exactly this and this record does not upgrade it.
8. **The supervisor's own message-relative times.** `TIME_PROVENANCE.txt` §5 discloses that times of
   the form "~16:40Z"/"~16:52Z" in supervisor messages were **projected, not read**, and ran ~20
   minutes fast. This grading lane cannot verify another session's clock and does not. **Every stamp
   in this record is `date -u` output read at its own write, or a filesystem mtime read under
   `TZ=UTC`.**

---

## 9. Drafted for the supervisor to land — NOT landed by this item

This item writes no board, docket, lesson, numerics-fact, ladder-status or index file (§7,
Escalation). The following is **draft text delivered upward**, and nothing below has been appended
anywhere.

### 9.1 Candidate lesson

> **A planted-difference control is what turns a "no difference found" into evidence — and the same
> comparator can produce a worthless zero and a load-bearing one on consecutive attempts of the same
> item.** A3 rung 3, attempts 1 and 2, same `identity_stop.sh`, byte-identical. Attempt 1: the arm
> died before any checkpoint printed, so the comparator found no difference and the record correctly
> wrote *"this is explicitly not evidence that it would not have fired"* — `NOT A RESULT`. Attempt 2:
> eleven checkpoints printed, the comparator's limb 7 had already returned exit 6 on rung 2's **real**
> path differing in the 5th significant figure, and the same zero became the item's headline finding.
> **The discriminator is never the guard's exit code; it is whether the guard was given something to
> read and was proved able to read it in that session.** (CLAUDE.md rule 3; `../rung3_patched_idwarp_np4/RESULTS.md:107`
> against this file §3.1.)

### 9.2 Candidate second lesson — cost calibration

> **A launch gate tight enough to protect its own floor selects for a quiet box, so any wall estimate
> carrying a contended-box contention multiplier is systematically high behind that gate.** A3 rung 3
> attempt 2: Amendment 1 raised the memory limb to 25.0 GiB (82% of `MemTotal`); the gate opened on
> poll 1 at 27.19 GiB with 13 free cores; the realised contention factor was **1.1955×** against a
> **1.7×** point taken from a rung-2 measurement on a **contended** box, and the point missed by
> +42% while the 1.0–2.6× band held. **Record the gate's own memory limb beside any contention
> multiplier, and state which side of the gate the multiplier was measured on.** This is C-4's lesson
> (*record the load average beside a per-iteration cost basis*) arriving from the other direction:
> there the basis carried contention onto a quiet box; here the *gate* made the box quiet.

### 9.3 Candidate numerics facts

> **N-?? (A3, rung 3, 79,560 cells, np=4, `transonicPCOption 1`).** The patched-IDWarp CD adjoint
> residual path is **bit-identical to the SHIPPED-equivalent ‡ path on all 11 printed checkpoints,
> iterations 0–1000**, in a **stagnating** regime. Total residual reduction through iteration 1000 is
> **1.3133×** (`2.121343646203e-02` → `1.615247229756e-02`), flat from iteration 200 (relative change
> 2.239e-03 over 200→1000, **1.446e-06** over 900→1000). With rung 2's 11/11 on a **converging** solve
> this is the second regime, and the second instance, of *the rotation patch enters strictly after the
> Krylov solve*. Two rungs of one case; not a generalisation.
> Source: `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md` §2.1, §3.

> **N-?? (A3, rung 3, memory envelope).** Container peak aggregate RSS at this mesh, np,
> configuration and warm colouring cache, stopped at iteration 1000: **11.680 GiB** — within
> **0.030 GiB (+0.26%)** of the shipped arm's complete measured peak of 11.65 GiB, against a 16 GiB
> cap. Host `MemAvailable` minimum over 87 samples at 5 s: **15.2871 GiB** against an 8.0 GiB floor,
> **0 strikes**. The preconditioner assembly completes at `ExecutionTime` **170.76 s** (1355 colours,
> `dRdWTPC` 0→1354); the Krylov solve begins at 171.41 s.
> Source: same file, §2.1, `ledger.txt`, `rss_patched.txt`.

### 9.4 Calibration row (the text landed in `docs/COST_CALIBRATION.md`, id re-derived at commit)

> `2026-08-24 | dafoam | A3 rung 3 patched-IDWarp np=4 ATTEMPT 2 (identity confirmed 11/11, GATE FAIL — adjoint, inherited)` — predicted **51.8 core-min** (band 31.0–78.4, ceiling 176.0), actual gross **36.733 core-min** (bound 37.933 on an un-instrumented pre-flight), cleaned **= gross** (no row matches the 3600-s stall rule; longest wall 532 s), ratio **0.709**, gap attributed to **contention in the under direction** (realised 1.1955× against a 1.7× point) with **misprediction** named on the inherited-and-unvalidated point estimate and **waste 0.000 core-min**.

### 9.5 Candidate docket items

1. **Row 12b's rung-3 cell: `PENDING → GATE FAIL (adjoint)`**, and the patched column's rung-3 FD
   cell stays **`NOT A RESULT`**. Registered at §4 item 3; **this item does not edit any board.**
2. **Toolchain adoption, for Sanaa's desk, not a session's.** Rung 3 is now a measured input: the
   patch **buys nothing and costs nothing** at this rung. It is one input among the rung-1 and rung-2
   gradient findings, and adoption remains **hers** (R11).
3. **`DAFOAM_CHARTER.md` §5's *serial before parallel* is still unsatisfied on A3** — no decomposition
   datum at any rung. Named in §14 disposition 3 as *declined by name* for this item; it needs its own
   pre-registration if it is wanted.
4. **Stage R3-2 (the FD arm) is NOT reachable.** Its registered precondition — `PetscConvergedReason:
   2` from stage R3-1 — did not occur. It stays unbought, and if it is ever bought it needs its own
   pre-registration (§5), never an addendum to this one.

---

## 10. Standing statements

**Verdict vocabulary:** PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING. No other
word grades an arm here, and none was used.

**Two rows, never merged.** The SHIPPED-equivalent **‡** row is cited from
`../grading_confirmation/RESULTS.md` §2d and `A3-rung3-n52/rung3_stage1.log`; the PATCHED row is
measured here. **A patched grade never replaces a shipped grade.** Row 11 stands as it is.

**Toolchain identity is an image ID and a library hash, never a version string**
(`DAFOAM_CHARTER.md` §6). `idwarp` reports `2.6.2` on both stacks and discriminates nothing; the
discriminators are `image_id=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`
and `IDWARP_SO_MD5 = 85f59e87253e0a71a813f64ca6e4c425`.

**A stop is not a measurement** (`DAFOAM_CHARTER.md` §7). The deliberate stop of R3-P4 carries no
claim of its own; the identity finding rests on the eleven matched checkpoints, which were complete
before the stop fired.

**Attempt 1's documents are not edited by this one.**
`../rung3_patched_idwarp_np4/PREREGISTRATION.md` and its `RESULTS.md` stand exactly as committed at
`97a54c07` and `67edcc19`. **This item edits no frozen file.**

**Nothing is filed, sent, uploaded, posted, registered or pushed. Filing stays NOT APPROVED and is
Sanaa's alone.**

---

## 11. Addendum 1 — 2026-08-24T18:34:42Z, dafoam `lab-lane`: five `patched.log` line citations in §2.1 are off by one and are struck; every value stands

**Record version: v1.0 → v1.1.** v1.0 is this file exactly as committed at `8871acf3`. This is the
first change to the record since, and it is a **dated addendum, not an edit**.

**Lines whose number changed above this section: 0.** The base for this section was taken from
`git show HEAD:cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md` — never from
the worktree, which is decayed by construction (D486) — and the base was asserted to be a **strict
byte prefix** of the file written, before it was staged. Nothing above this line moved.

**Frozen text is never edited** (`CLAUDE.md` rule 6). §2.1's table stands above **unaltered and in
full**; this addendum **strikes five of its artifact cells and only those cells**, and records the
correct citation for each here.

**Zero compute.** No container was launched, no solver re-run, no comparator re-executed. The log
was read read-only from the run root. Cost of this addendum: **0.00 core-min**.

**No value changes. No verdict moves. `GATE FAIL — adjoint, inherited` stands exactly as recorded in
§1**, and the 11-of-11 identity finding stands. What was wrong is the half of each row a reader uses
to check it.

### 11.1 Origin, and dafoam's acceptance of the finding

Verification's cross-team gate audit **pass 10 §77** (`docs/CROSS_TEAM_GATE_AUDIT.md`, committed
`d74a36c2`, §73–81), headed:

> ### 77. **DEFECT FOUND** — five line citations into `patched.log` are off by one, low, and one of them lands a reader on a real but wrong number

Pass 10's verdict at its §80 is **`SOUND WITH DISCLOSED DEVIATIONS`**, CANDIDATE, with this as the
one DEFECT named. The **verification supervisor's own read** promoted it at **`8cbe716b` §82**
(2026-08-24T17:57:20Z): *"Pass 10 (`d74a36c2`, §73–81; C-35 `ac7de7e4`) — BELIEVED: SOUND WITH
DISCLOSED DEVIATIONS, ONE DEFECT"*, reading personally that *"line 903 is iteration 900 (the §2.1
citation range 893–903 is off by one, low — correct 894–904; every value reproduces; dafoam's dated
correction under rule 6)"*.

**dafoam accepts the finding, and re-derived it here rather than relaying it.** This lane read
`/home/ubuntu/certonomous-runs/P5-a3-rung3-patched-attempt2/patched.log` directly — `grep -n 'Main
iteration'` returns the eleven KSP checkpoints at **894, 895, 896, 897, 898, 899, 900, 901, 902,
903, 904**, and `wc -l` returns **904**. The correction below is dafoam's own reading of the file,
and it agrees with pass 10 row for row, including the fifth row, which moves in the *opposite*
direction from the other four.

**Why this is a defect and not a typo, in the record's own terms.** A citation is the half of a
measured row that a reader can check. Two of the five land a reader on `patched.log:903` for *"the
residual at iteration 1000"*, and line 903 carries `1.615249565219e-02` — a real, plausible,
13-figure residual that is the **wrong** one. A citation that lands on a non-number announces itself;
this one does not. It was **not disclosed**: §6 records *"Deviations from the frozen document:
none"*, and §8's list of what the record could not verify does not reach it.

### 11.2 The five struck citations, quoted verbatim by line, with the correction

Each row below quotes the **whole §2.1 table row exactly as it stands above**, then strikes the
artifact cell alone. **The quantity cell and the value cell are not struck in any of the five** —
every value re-derives from the corrected lines and is carried forward unchanged.

**(a) `RESULTS.md:65`** — the identity row, verbatim:

> | checkpoints bit-identical to the frozen shipped path | **11 of 11**, iterations 0–1000 | `patched.log:893-903` vs `shipped_cd_checkpoints.txt` |

~~STRUCK as to the artifact cell alone: `patched.log:893-903`.~~
**Correct: `patched.log:894-904`.** Line 893 is `Solving Linear Equation... 171.41 s` — not a
checkpoint at all; the eleven checkpoints run 894–904 and the block ends at the file's last line.
**11 of 11 stands.**

**(b) `RESULTS.md:66`** — the total-reduction row, verbatim:

> | total residual reduction through iteration 1000 | **1.3133×** (`2.121343646203e-02` → `1.615247229756e-02`) | `patched.log:893,903` |

~~STRUCK as to the artifact cell alone: `patched.log:893,903`.~~
**Correct: `patched.log:894,904`.** Line 894 carries iteration 0, `2.121343646203e-02`; line 904
carries iteration 1000, `1.615247229756e-02`. Line 893 carries no residual, and line 903 carries
**iteration 900**, `1.615249565219e-02` — the wrong-number landing named in §11.1. **1.3133× stands.**

**(c) `RESULTS.md:67`** — the 200→1000 flatness row, verbatim:

> | flatness, iterations 200 → 1000 | relative change **2.239e-03** | `patched.log:895,903` |

~~STRUCK as to the artifact cell alone: `patched.log:895,903`.~~
**Correct: `patched.log:896,904`.** Line 896 carries iteration **200**, `1.618871466028e-02`; the
cited 895 carries iteration **100**. Line 904 carries iteration 1000. **2.239e-03 stands.**

**(d) `RESULTS.md:68`** — the 900→1000 flatness row, verbatim:

> | flatness, iterations 900 → 1000 | relative change **1.446e-06** | `patched.log:902,903` |

~~STRUCK as to the artifact cell alone: `patched.log:902,903`.~~
**Correct: `patched.log:903,904`.** Line 903 carries iteration **900**, `1.615249565219e-02`; the
cited 902 carries iteration **800**. **1.446e-06 stands.**

**(e) `RESULTS.md:69`** — the GMRES-cap row, verbatim:

> | iterations executed of the 4000 GMRES cap | **1000** — stop deliberate, not exhaustion | `patched.log:891,903` |

~~STRUCK as to the artifact cell alone: `patched.log:891,903`.~~
**Correct: `patched.log:890,904`.** Line 890 is `GMRES Max Iterations: 4000`; the cited **891** is
`GMRES Relative Tolerance: 0.0001`. Line 904 carries iteration 1000. **1000 of 4000 stands, and the
stop stays deliberate** — `identity_stop.sh` exit 5, `rc=137`, as §1 and §5 record.

**The error is not one shift.** Rows (a)–(d) cite one line **too low**; row (e) cites one line **too
high**. So there is no single whole-file offset to undo, and no other row can be repaired by
arithmetic on these — each was checked individually below.

### 11.3 What this lane checked and found CORRECT — the bound on the blast radius, measured rather than assumed

Pass 10 bounded the defect by checking one further row. This lane checked **every** remaining line
citation into `patched.log` in this record, and **all of them are correct**:

| `RESULTS.md` line | cited | what is on the cited line(s) | reading |
|---|---|---|---|
| `:70` | `patched.log:868-882` | 868 = `dRdWTPC: 0 of 1355, ExecutionTime: 60.02 s`; 882 = `dRdWTPC: 1354 of 1355, ExecutionTime: 170.76 s` | **CORRECT** |
| `:108` (R3-P1(b)) | `patched.log:430` | `    transonicPCOption 1;` | **CORRECT** |
| `:110` (R3-P1(d)) | `:83,:110,:268,:575` and `:50` | `nProcs : 4` at 83, 110, 268, 575; `nProcs : 1` at 50 and nowhere else | **CORRECT**, all five |
| `:111` (R3-P1(e)) | `patched.log:25-28` | `PROV rank {2,0,1,3} idwarp version = 2.6.2` — the four rank lines exactly | **CORRECT** |
| `:112` (R3-P2) | `patched.log:651` | `Time step continuity errors : sum local = 1.018123970654079` | **CORRECT** |
| `:113` (R3-P3) | `:856,:857,:864,:865,:868` | the five colouring-READ strings the pre-registration registered at `PREREGISTRATION.md:372-374`: `Checking if Coloring file exists..` (856), `dRdWColoring_4.bin exists.` (857), `Reading Coloring dRdWColoring_4` (864), `Validating Coloring...` (865), `dRdWTPC: 0 of 1355` (868) | **CORRECT**, all five |

So the defect is **confined to the five §2.1 rows that cite the KSP checkpoint block**, and every
scored prediction row in §3 cites correctly. This is a measurement of the blast radius, not an
inference from the pattern.

### 11.4 What does NOT change

- **The verdict.** `GATE FAIL — adjoint, inherited` (§1) is untouched, and it was frozen at
  `PREREGISTRATION.md:260` before the gate opened.
- **Every value in §2.1**, including `2.121343646203e-02`, `1.615247229756e-02`, 1.3133×,
  2.239e-03, 1.446e-06, 1000 of 4000, 11 of 11, and the memory figures — all re-derive from the
  corrected lines, unchanged to every digit.
- **Every scored row in §3**, the cost table in §7, the instruments in §5 and the drafted text in
  §9.
- **No frozen file.** `PREREGISTRATION.md`, `stage.sh`, `drive.sh`, `coloring_guard.sh`,
  `guard_selftest.sh`, `identity_stop.sh`, `mem_guard.sh` and `shipped_cd_checkpoints.txt` remain
  untouched by this record, as this file's header (lines 7–9) states.
- **Attempt 1's documents**, which this record already states it does not edit.
- **The §7 cost calibration**, and no row is added to `docs/COST_CALIBRATION.md` for this addendum:
  it spent no compute.

**Nothing is filed, sent, uploaded, posted, registered or pushed by this addendum. Filing stays NOT
APPROVED and is Sanaa's alone** (`CLAUDE.md` rule 7).
