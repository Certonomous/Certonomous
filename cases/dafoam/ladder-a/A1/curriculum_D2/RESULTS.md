# Curriculum item D2 — Optimizer A/B on the D1 problem (IPOPT vs SLSQP): RESULTS

**NOT FILED ANYWHERE.** Nothing in this document or the item it records is filed, sent, emailed,
uploaded, posted, registered, submitted or commented outside this box, now or ever (`CLAUDE.md`
rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.** **The five upstream DAFoam defect drafts
are untouched by this item and remain drafts.**

**Written 2026-08-24T18:18:58Z by Lane D2 phase 2 (Opus), DAFoam team.** Graded against
`PREREGISTRATION.md` frozen at commit **`03580b8f`** (v1.0), with the supervisor's launch
authorisation appended as §18 at **`641c5938`** (v1.1). **Every threshold, band, cap and label in
this record was fixed before either arm ran.** Every UTC stamp is `date -u` output read in the shell
invocation that wrote it.

**Both arms are patched-toolchain rows (R11).** Neither stands in for a shipped row; the SHIPPED row
of the A1 optimisation ledger remains `BLOCKED` exactly where `../curriculum_D1/RESULTS.md` §1 left
it.

---

## 1. Verdicts at a glance

| row | verdict | the number it rests on |
|---|---|---|
| **AB5 — arm A reproduces D1 arm O** | **PASS** | **all five continuous rows exactly `0.0`**; majors `11 = 11` |
| **G-A1** constraint satisfaction, arm A | **PASS** | `\|CL − 0.5\| = 1.8791e-07`; 23 of 23 geometric rows inside; IPOPT's own `Constraint violation 1.9421e-07` |
| **G-A2** termination, arm A | **gradeable → PASS** | `EXIT: Optimal Solution Found.`, `Overall NLP error 4.0871e-07 < 1e-5` |
| **G-A3** endpoint FD, arm A | **PASS** | 4 of 4 GRADED, zero flagged, zero sign flips, worst **0.2553 %** |
| **G-A4** trivial baseline, arm A | **PASS** | `112.6004 %`, sign-flipped, at `1e-8` |
| **G-B1** constraint satisfaction, arm B | **PASS** | `\|CL − 0.5\| = 2.5566e-06`; 23 of 23 geometric rows inside |
| **G-B2** termination, arm B | **gradeable → PASS** | pyOptSparse **`Inform = 0`, "Optimization terminated successfully."** |
| **G-B3** endpoint FD, arm B | **PASS** | 4 of 4 GRADED, zero flagged, zero sign flips, worst **0.2485 %** |
| **G-B4** trivial baseline, arm B | **PASS** | `111.8888 %`, sign-flipped, at `1e-8` |
| **AB1** objective agreement | **PASS** | `Δrel = 0.7381 %`, inside the `≤ 1.0 %` band; **the `< 0.10 %` point was NOT met** |
| **AB2** design-point agreement | **GATE FAIL** | `‖Δshape‖₂/‖shape_A‖₂ = 33.259 %` (band 10.0 %); `‖Δshape‖_∞ = 1.9379e-02` (band 8.0e-03); `\|ΔAoA\| = 0.2428 deg` (band 0.25, inside) |
| **AB3** count instrument | **PASS** | registered offset `+1` held on **both** arms: 13 = 12+1, 16 = 15+1 |
| **AB4** constraint-violation path instrument | **PASS** | `V_max(A) = 2.60464e-03` at block 2 against IPOPT's own `inf_pr 2.60e-03` at major 2 |
| **AB4-C** left-the-neighbourhood threshold | **not reached by either arm** | `V_max(A) 2.60e-03`, `V_max(B) 3.31e-03`, both ≪ `1.0e-1` |
| **AB4-H** hazard clause | **PASS** | no sentence in this record reads a path excursion as an aerodynamic, physical or design finding |
| **AB6** like-for-like cost instrument | **PASS** | contention **MEASURED** for the first time on this ladder: **−5.1935 %** |
| **G6 / G7 / G8 / G9 / G10** | **PASS** (all five) | §2 |

**The one-line finding.** *Two pyOptSparse optimizers, one CLI token apart on a byte-identical run
script, reached the same objective value to **0.74 %** and **different design points**: the shape
vectors differ by **33.3 %** in `L2` and by **1.94e-02** in `L∞` — more than twice `shape[6]`'s
entire value. **AB1 passes and AB2 fails, and that combination is the result**: on this NLP the
objective is close to flat along the direction that separates the two designs. This is a statement
about the two algorithms and about the problem's conditioning; **it is not an aerodynamic finding**
and is not reported as one.

**The item's other deliverable is a narrowing, and it is stated first rather than buried.** The
ratified curriculum row promised *"optimizer/**trust-region** behavior as a measured comparison."*
**The trust-region half is `NOT DELIVERED BY CONSTRUCTION`** — §3.1's probe measured that no
trust-region optimizer is importable on this box (`ParOpt` ships as a package directory with no
compiled extension; `SNOPT` and `NLPQLP` absent). The supervisor placed that narrowing on Sanaa's
desk as a NOTICE; **it is not read into the blanket** (`CLAUDE.md` rule 9), and **nothing about
building `ParOpt` was run or prepared.**

---

## 2. The ledger, the operational gates, and the falsifiers

**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/` — **asserted ABSENT by
`test ! -d` and `test ! -e` inside the invocation that committed the authorisation addendum**, and
created only after it.

### 2.1 `ledger.txt`, both rows

| arm | optimizer | rc | wall s | ranks | **core-min** | `docker inspect` (exit, OOMKilled) | peak RSS GiB | log |
|---|---|---|---|---|---|---|---|---|
| **armA** | IPOPT | **0** | **336** | 1 | **5.600** | **`0 false`** | **1.6938** | `armA_20260824T175746Z_1524887.log` |
| **armB** | SLSQP | **0** | **391** | 1 | **6.517** | **`0 false`** | **1.6927** | `armB_20260824T180411Z_1530445.log` |

Both rows carry `D1_CONTAINER_UID: 0`, `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425`,
`nProcs : 1`, and the arm's own optimizer tag (`pyOptSparse_IPOPT|` / `pyOptSparse_SLSQP|`).
`D1_USRBIN_TIME: absent` in both arms, exactly as every D1 arm reported — so peak RSS is the
in-process `getrusage` figure, as §9 of the pre-registration registered.

Artifact: `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/ledger.txt`.

### 2.2 Operational gates

**G6 — launch gate, run as its own command before EACH launch and read before the launch was
issued.** `preflight_history.txt`, both rows:

| UTC | arm | `nproc` | `load1` | `free_cores` | `MemAvailable` GiB | gate | action |
|---|---|---|---|---|---|---|---|
| 2026-08-24T17:57:36Z | armA | 16 | 3.24 | **12.76** | **27.31** | **OPEN** | launched |
| 2026-08-24T18:04:04Z | armB | 16 | 3.63 | **12.37** | **27.43** | **OPEN** | launched |

**G6: PASS.** Both gates opened on the first reading; **the gate cost 0.000 core-min and zero
waiting**. Neither limb was near binding. **No departure was taken and none was requested**, and a
concurrent D3 lane was live on the box throughout (3 `docker run` processes observed mid-run) — the
gate handled the co-tenancy exactly as registered.

**G7 — image identity: PASS.** `IDWARP_SO_MD5` printed from inside the process that loaded the
library reads `85f59e87253e0a71a813f64ca6e4c425` in **both** arms, matching §3's registered patched
row. `nProcs : 1` asserted in both logs. `--user 0:0` confirmed by `D1_CONTAINER_UID: 0`.
**Falsifier F1 did not fire.**

**G8 — cold start, verified BEFORE each launch: PASS.** The staged tree's file listing was asserted
**identical to D1's own staged `base/`** (`diff` of the two sorted `find` listings came back
**EMPTY**); the three staging md5s of §1.2 matched on the staged copy
(`points.gz 38a486d29a540ecd1b06e006e66475e7`, `wingFFD.xyz 6ddf378b028d03d8a18270488bee1759`,
`runScript.py 0557da51f6f179f6de865144343c499f`); **all seven `0/` fields were md5-equal to their
`0.orig/` counterparts**; and `d2_run_arm.sh` re-asserted, before each of the two launches, that
there was no `0.0001`, no `processor*`, no `reports/`, and that `0/U` was present. **Nothing under
`0.orig/` was removed at any point.** The proof that it held is measured, not argued: **both arms'
`D1_FEASIBLE_CD` read `0.020943920630946831`, bit-identical to arm O's**. **Falsifier F6 did not
fire, on either arm.**

**G9 — memory envelope: PASS.** Peak RSS **1.6938 GiB** (arm A) and **1.6927 GiB** (arm B) against a
predicted 1.70 GiB, a registered ceiling of 2.5 GiB and a kernel cap of `--memory=6g
--memory-swap=6g`. **`.State.OOMKilled` is `false` and the exit code is `0` for both containers** —
the kernel's own statement, read before the container was removed. This item characterises no memory
boundary and claims none.

**G10 — cost ceiling: PASS.** **12.150 core-min** spent against a **140.0 core-min** hard ceiling
(**8.68 % used**) and a registered price of 16.733. §8.

**The five frozen instruments were byte-identical to their committed blobs at every launch.** The
two script md5s were re-asserted by `d2_run_arm.sh` immediately before *each* of the two `docker
run` invocations and both passed (`4c9811d16f344bc23136981cd6092d8f`,
`7e454d2f1830a40086465d9b5c57a941`). **No frozen instrument was edited at any point in phase 2.**

**L-252 provenance: honoured.** Every generated file carries a per-invocation stamp; both logs carry
their `.ok.${STAMP}` sentinel written by the producing step
(`armA_….log.ok.20260824T175746Z_1524887`, `armB_….log.ok.20260824T180411Z_1530445`) and every
consuming step asserted `test -s <file> && test -f <file>.ok.${STAMP}` before reading. No generic
filename was written or read in the run root.

### 2.3 The controls — run twice: on arm O's real log before the arms, and **live on each arm's own log** before grading

`CLAUDE.md` rule 3: *a zero from a reader not shown able to see a non-zero is not evidence.*

| control | on arm O's log, before either arm ran | **live on arm A's own log** | **live on arm B's own log** |
|---|---|---|---|
| statistics self-test | `pass: true` (`path_max` found the planted maximum at block 2) | — | — |
| **plant** (all five consumed channels) | **OK**, every channel moved by exactly `1.234e-03`, worst residual `1.08e-14` | **OK**, 13 blocks, worst residual `1.08e-14` | **OK**, 16 blocks, worst residual `1.08e-14` |
| **negative** (blind reader) | **refused** `PLANTED_ZERO` | **refused** `PLANTED_ZERO` | **refused** `PLANTED_ZERO` |
| **key-set** (D1 arm C's own defect replayed) | **refused** `KEYSET` by name | — | **refused** `KEYSET` by name |
| **optimizer tag** | **refused** `OPTIMIZER_TAG` | **refused** `OPTIMIZER_TAG` | **refused** `OPTIMIZER_TAG` |
| **A/B trivial baseline** | **OK**: self-comparison exactly `0.0`; planted `2.0e-02` seen at `2.0e-02`, `21.299 %` — fails both AB2 bands | — | **OK**: self-comparison exactly `0.0`; planted `2.0e-02` seen at `2.0e-02`, `22.492 %` — fails both AB2 bands |

**Every control exited 0; none degraded to a warning.** The planted zero was planted into, and read
back from, **the very files the arms produced** — not a synthetic fixture. That is the L-273 repair
carried forward, and it is what entitles this record to report a difference *and* an agreement.

**D1's run root was read-only throughout and is unchanged**: arm O's log md5 read
`64bee1631d28ab07973e56ec7e1f4bf3` **before and after** the controls. No file was created, moved or
deleted there — not even a `.plant` file.

### 2.4 Falsifiers F1–F12, scored

| id | fired? | evidence |
|---|---|---|
| **F1** wrong `IDWARP_SO_MD5` | **NO** | both arms printed `85f59e87253e0a71a813f64ca6e4c425` |
| **F2** AB5-hard breached by arm A | **NO** | all six rows inside hard; five are exactly `0.0` |
| **F3** planted zero blind on any consumed channel | **NO** | all five channels seen, on arm O's log and on each arm's own log |
| **F4** wrong optimizer tag in a consumed log | **NO** | `read_path` accepted `IPOPT` for arm A and `SLSQP` for arm B, and refused `WRONGOPT` in both tag controls |
| **F5** count disagreement other than the registered `+1` | **NO** | 13 = 12+1 (arm A), 16 = 15+1 (arm B) |
| **F6** `D1_FEASIBLE_CD` off arm O by > 1e-9 rel | **NO** | both arms bit-identical: `0.020943920630946831` |
| **F7** accepted design violates G-x1 | **NO** | both arms PASS G-x1 with zero geometric violations |
| **F8** any endpoint sign flip in a graded component | **NO** | zero sign flips, 8 graded components across the two arms |
| **F9** trivial baseline ≤ 5 % | **NO** | `112.6004 %` (A) and `111.8888 %` (B), both sign-flipped |
| **F10** A/B trivial baseline not seen at its planted size / does not fail AB2 | **NO** | `2.0e-02` planted, `2.0e-02` seen, both bands failed, on **both** arms' logs |
| **F11** arm B errors before or inside `run_driver()` | **NO** | arm B ran `run_driver()` to `Inform = 0` |
| **F12** a sentence reading a path excursion as an aerodynamic finding | **NO** | §7.4; the hazard clause is quoted and complied with |

---

## 3. AB5 — the identity condition, graded BEFORE arm B was launched

**This is the registered ordering, and it was followed**: arm A was graded against D1 arm O and the
AB5-hard rows were checked **before** the arm B launch command was issued. Had any hard row breached,
arm B would not have been launched (falsifier F2).

| # | quantity | **measured** | AB5-tight | tight met? | AB5-hard | breached? |
|---|---|---|---|---|---|---|
| 1 | `\|CD_feasible,A − 0.020943920630946831\| / …` | **`0.0` exactly** | ≤ 1.0e-9 | **YES** | > 1.0e-5 | **NO** |
| 2 | `\|CD_A − 0.017527899854535338\| / …` | **`0.0` exactly** | ≤ 1.0e-4 | **YES** | > 1.0e-3 | **NO** |
| 3 | `\|CL_A − 0.49999981209363359\|` | **`0.0` exactly** | ≤ 1.0e-6 | **YES** | > 1.0e-5 | **NO** |
| 4 | `‖shape_A − shape_O‖_∞` | **`0.0` exactly** | ≤ 1.0e-4 | **YES** | > 1.0e-3 | **NO** |
| 5 | `\|AoA_A − 1.128636497545056\|` deg | **`0.0` exactly** | ≤ 1.0e-3 | **YES** | > 1.0e-2 | **NO** |
| 6 | major iterations | **11** | = 11 | **YES** | ∉ [9,13] | **NO** |

**AB5: PASS.** Arm A did not merely reproduce arm O within the tight thresholds — **it reproduced it
bit-identically on every graded quantity**, at eight to seventeen significant figures, from a
freshly staged case in a different session on a differently loaded box, 2 h after arm O ran.

**What that buys, precisely.** The staging *is* D1's staging; the optimizer *is* the same code path
(arm A's explicit `-optimizer IPOPT` selects what arm O took as the argparse default, and the
equality is now measured rather than argued); and **any difference between arm A and arm B is
therefore the optimizer, not the staging.** That is the whole reason arm A was bought, and it
delivered.

**A stronger statement than the pre-registration expected, and worth recording as a fact.** A1 at
`np = 1` on this image is **deterministic to the last printed bit across sessions**, through 11
optimiser majors, ~12 primal solves and a `findFeasibleDesign` — not merely reproducible to the
1.8e-07 that A4 §3.2 measured for two runs of the same optimizer. Drafted as `N-D` in §9.

Artifact: `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/ab5_20260824T175746Z_1524887.json`.

---

## 4. Arm A (IPOPT) — the per-arm gates, in full

**Accepted design.** `CD = 0.017527899854535338`, `CL = 0.4999998120936336`,
`AoA = 1.128636497545056 deg`, `‖shape‖₂ = 0.093899772805341328`.
Feasible point before the optimiser: `CD = 0.020943920630946831`, `CL = 0.49999943897261456`,
`AoA = 5.153023459675001 deg`. Driver wall (`prob.run_driver()` alone) **263.60 s**.

### 4.1 G-A1 — constraint satisfaction at the accepted design: **PASS**

| row | reading | bound | inside? |
|---|---|---|---|
| `\|CL − 0.500000\|` | **`1.8791e-07`** | ≤ 1.0e-5 | **YES** |
| `thickcon`, 20 rows | min **0.5000001258**, max **1.1017024514** | [0.5 − 1e-6, 3.0 + 1e-6] | **YES, all 20** |
| `volcon`, 1 row | **1.0000000173** | ≥ 1.0 − 1e-6 | **YES** |
| `rcon`, 2 rows | **0.8000002615**, **0.8000002615** | ≥ 0.8 − 1e-6 | **YES** |
| IPOPT's own `Constraint violation....:` | **`1.9421312102974042e-07`** | ≤ 1.0e-5 | **YES** |

The registered *substitution* clause was not needed on this arm: IPOPT printed its own line and it
agrees with the comparator's independent reading of `CL` to the same order.

### 4.2 G-A2 — termination: **gradeable → PASS**

`EXIT: Optimal Solution Found.`, `Number of Iterations....: 11`,
`Overall NLP error.......: 4.0871293161759560e-07` — **below the `tol 1e-5`** the frozen script sets.
Not stopped by `max_iter 40`, not stopped by the 900 s `timeout` (336 s used, **2.68× of margin**),
not stopped by the ceiling. **PASS, and it is not described by the size of the improvement it
reached.**

### 4.3 G-A3 — endpoint FD, per component, never folded into an aggregate: **PASS**

Steps selected **inside the container by the frozen D1 instrument**, from that arm's own endpoint
`\|J_adj\|` and the inherited `η = 1.957349804806996e-08` alone, before any FD value existed.

| component | `J_adj` | `s_lo` | FD @ `s_lo` | rel. err | **`s_hi`** (graded) | **FD @ `s_hi`** | **rel. err** | flip | plateau | `C` @ `s_hi` | graded? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `shape[6]` | `-2.77015704e-02` | `1e-4` | `-2.76751976e-02` | 0.0953 % | **`3e-4`** | **`-2.76870222e-02`** | **0.0525 %** | no | 0.0427 % | 848.7 | **YES** |
| `shape[1]` | `+1.91129336e-02` | `1e-4` | `+1.91851082e-02` | 0.3762 % | **`3e-4`** | **`+1.91442968e-02`** | **0.1638 %** | no | 0.2132 % | 586.8 | **YES** |
| `shape[5]` | `+3.88660685e-02` | `1e-4` | `+3.89825724e-02` | 0.2989 % | **`3e-4`** | **`+3.89138868e-02`** | **0.1229 %** | no | 0.1765 % | 1192.9 | **YES** |
| `patchV[1]` | `+1.12325011e-03` | `1e-3` | `+1.13155890e-03` | 0.7343 % | **`3e-3`** | **`+1.12612462e-03`** | **0.2553 %** | no | 0.4826 % | 345.2 | **YES** |

**4 of 4 GRADED. Zero FLAGGED. Zero sign flips. Worst graded component 0.2553 %.** Verdict **PASS**
(≤ 5 % with zero flips). **This table reproduces D1 arm O's §5.2 table to every printed digit** — a
consequence of AB5's bit-identity, not an independent measurement of the adjoint.

### 4.4 G-A4 — trivial baseline: **PASS**

| component | step | `J_adj` | FD | **rel. err** | sign flip |
|---|---|---|---|---|---|
| `shape[6]` | **`1e-8`** | `-2.77015704e-02` | **`+2.19846668e-01`** | **112.6004 %** | **YES** |

**The instrument can fail, and does, at a step A1's own roundoff branch destroys. G-A3's verdict is
NOT withdrawn** — falsifier F9 did not fire and was never close: the wrong step is off by **2,144×**
relative to the graded step's 0.0525 %.

---

## 5. Arm B (SLSQP) — the per-arm gates, in full

**Accepted design.** `CD = 0.01765727302317084`, `CL = 0.49999744336561236`,
`AoA = 1.3714493986917844 deg`, `‖shape‖₂ = 0.088919975`.
Feasible point before the optimiser: `CD = 0.020943920630946831` (**bit-identical to arm A's and to
arm O's** — `findFeasibleDesign` is deterministic and optimizer-independent, exactly as §6.2's basis
for AB5 row 1 said), `CL = 0.49999943897261456`. Driver wall **318.24 s**.

### 5.1 G-B1 — constraint satisfaction at the accepted design: **PASS**

| row | reading | bound | inside? |
|---|---|---|---|
| `\|CL − 0.500000\|` | **`2.5566e-06`** | ≤ 1.0e-5 | **YES** |
| `thickcon`, 20 rows | min **0.7681854693**, max **1.0696469781** | [0.5 − 1e-6, 3.0 + 1e-6] | **YES, all 20** |
| `volcon`, 1 row | **1.0000000190** | ≥ 1.0 − 1e-6 | **YES** |
| `rcon`, 2 rows | **0.8000002005**, **0.8000002005** | ≥ 0.8 − 1e-6 | **YES** |

**The registered substitution was used and is reported as used**: SLSQP prints no constraint-violation
line of its own, so this arm's sub-condition was discharged by the comparator's own reading of `CL`
and the 23 geometric rows at the accepted design — as §6.1 registered **in advance**, not improvised
at grading. Arm B satisfies `CL = 0.5` an order of magnitude less tightly than arm A
(`2.56e-06` against `1.88e-07`) and both are well inside the `1.0e-5` gate; that difference is
consistent with an active-set method stopping *on* the constraint against an interior-point method
approaching it from inside, and it is reported as an algorithmic difference, not a physical one.

### 5.2 G-B2 — termination: **gradeable → PASS**

pyOptSparse printed, verbatim, in `armB_….log`:

```
   Exit Status
      Inform  Description
           0  Optimization terminated successfully.
```

**`Inform = 0`.** The gate keyed on the numeric code, not on a string, precisely because the wording
had never been printed on this box before — and the wording is now on the record for the next item.
`opt_SLSQP.txt` closes at `ITER = 13`, `NUMBER OF FUNC-CALLS: NFUNC = 15`,
`NUMBER OF GRAD-CALLS: NGRAD = 14`.

**Neither registered consequence of §6.1 was triggered.** *(a)* An inform code **was** printed, so
arm B is not `NOT A RESULT` about termination. *(b)* The arm did **not** hit its `timeout`: **391 s
of a 2,700 s cap, 6.91× of margin**, so the endpoint block ran and produced its JSON, and the
"converged-and-gradeable" branch of arm B's two registered outcomes is the one that obtained.
`MAXIT 100` was, as registered, unreachable and irrelevant — the arm stopped at 13 iterations on its
own `ACC 1e-5` criterion.

### 5.3 G-B3 — endpoint FD, per component, at **arm B's own** steps: **PASS**

**The two arms' graded steps are NOT forced equal**, as registered — each arm's steps come from its
own endpoint gradient. They happened to land on the same rungs, and that is a measured coincidence
of the two endpoints' gradient magnitudes, not an imposed equality.

| component | `J_adj` | `s_lo` | rel. err @ `s_lo` | **`s_hi`** (graded) | **FD @ `s_hi`** | **rel. err** | flip | plateau | `C` @ `s_hi` | graded? |
|---|---|---|---|---|---|---|---|---|---|---|
| `shape[6]` | `-2.85135455e-02` | `1e-4` | 0.0832 % | **`3e-4`** | **`-2.84993839e-02`** | **0.0497 %** | no | 0.0335 % | 873.6 | **YES** |
| `shape[1]` | `+2.07995588e-02` | `1e-4` | 0.3845 % | **`3e-4`** | **`+2.08427584e-02`** | **0.2073 %** | no | 0.1779 % | 638.9 | **YES** |
| `shape[5]` | `+3.75491114e-02` | `1e-4` | 0.3480 % | **`3e-4`** | **`+3.75892273e-02`** | **0.1067 %** | no | 0.2421 % | 1152.2 | **YES** |
| `patchV[1]` | `+1.09641755e-03` | `1e-3` | 0.8323 % | **`3e-3`** | **`+1.09914891e-03`** | **0.2485 %** | no | 0.5887 % | 336.9 | **YES** |

**4 of 4 GRADED. Zero FLAGGED. Zero sign flips. Worst graded component 0.2485 %.** Verdict **PASS**.

**This is the item's second-order result and it is worth naming.** The patched adjoint validates to
**better than 0.25 %** at a design point **no D1 arm ever visited** — reached by a different
algorithm, 33 % away in shape space. The gradient's correctness is not an artefact of the one
endpoint D1 happened to stop at.

**These four numbers are NOT an A/B statistic** and are not used as one: comparing two FD errors
taken at two different design points would be a comparison of instruments, not of optimizers
(§6.1, registered).

### 5.4 G-B4 — trivial baseline: **PASS**

| component | step | `J_adj` | FD | **rel. err** | sign flip |
|---|---|---|---|---|---|
| `shape[6]` | **`1e-8`** | `-2.85135455e-02` | **`+2.39835420e-01`** | **111.8888 %** | **YES** |

**G-B3's verdict is NOT withdrawn**; falsifier F9 did not fire. The roundoff branch is severe at
`1e-8` at arm B's endpoint too — **111.8888 %** against arm A's **112.6004 %** and arm O's
**112.6004 %**, i.e. the instrument's failure mode is a property of the case and step, not of the
design point.

---

## 6. The A/B comparison — AB1 … AB6

Both logs read by the **same** frozen comparator, from the **same** channels, with each arm's
optimizer tag asserted. Report:
`/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/ab_report_20260824T180411Z_1530445.json`.

### 6.1 AB1 — objective agreement: **PASS** (band), **point NOT met**

| quantity | measured | point | band | verdict |
|---|---|---|---|---|
| `CD_A` | **`0.017527899854535338`** | — | — | — |
| `CD_B` | **`0.017657273023170840`** | — | — | — |
| `\|CD_B − CD_A\| / CD_A` | **`7.381e-03` = 0.7381 %** | < 0.10 % | ≤ 1.0 % | **PASS** |

**Inside the registered band, and the registered point was missed by 7.4×.** The two optimizers did
find the same optimum *by the gate's own definition*, and the AB1 escalation clause — *"above the
band → the two optimizers did NOT find the same optimum"* — **did not trigger**. Arm A's objective
is the lower of the two by `1.2937e-04` in `CD`.

### 6.2 AB2 — design-point agreement: **GATE FAIL**

| statistic | **measured** | point | band | inside band? |
|---|---|---|---|---|
| `‖shape_B − shape_A‖₂ / ‖shape_A‖₂` | **33.259 %** | ≤ 6.5 % | ≤ 10.0 % | **NO** |
| `‖shape_B − shape_A‖_∞` | **`1.9379e-02`** | ≤ 6.09e-03 | ≤ 8.0e-03 | **NO** |
| `\|AoA_B − AoA_A\|` | **`0.24281 deg`** | ≤ 0.05 deg | ≤ 0.25 deg | **YES** (by 0.0072 deg) |

**Two of three bands breached → AB2 is `GATE FAIL`.** Per mode, never aggregated:

| mode | `shape_A` | `shape_B` | `Δ = B − A` |
|---|---|---|---|
| `shape[0]` | `+0.028765046` | `+0.035705223` | `+0.006940177` |
| `shape[1]` | `+0.047201043` | `+0.057669793` | `+0.010468750` |
| `shape[2]` | `+0.016871666` | `+0.022124018` | `+0.005252352` |
| `shape[3]` | `+0.036676714` | `+0.019186209` | **`-0.017490504`** |
| `shape[4]` | `+0.047228927` | `+0.037410764` | `-0.009818162` |
| `shape[5]` | `+0.022959817` | `+0.026435695` | `+0.003475878` |
| `shape[6]` | `+0.008262623` | `+0.008320563` | `+0.000057940` |
| `shape[7]` | `+0.036138220` | `+0.016759123` | **`-0.019379097`** |
| `‖·‖₂` | **`0.093899773`** | **`0.088919975`** | `0.031229738` |

**The reading, stated at the size of the evidence and no wider.** The `L∞` separation of
**1.938e-02** is **2.35× `shape[6]`'s entire value** — the band was set at `8.0e-03` precisely
because *two designs whose worst mode differs by as much as the smallest mode's whole value are not
the same design*, and this pair differs by more than twice that. **The two optimizers reached two
different designs.** They did so while agreeing on the objective to 0.74 %, which is the same
statement read from the other side: **the objective is close to flat along `Δshape`**, and an NLP
whose optimum is that weakly determined in the design variables will hand different algorithms
different answers. **The two largest disagreements are `shape[7]` and `shape[3]`, which move in
opposite directions** — the two designs are not a scaled version of one another.

**Not claimed:** which design is "better" beyond the objective and constraint readings printed
above; that either optimizer converged to a local rather than global optimum; any aerodynamic
interpretation of the shape difference. This item measured two algorithms on one NLP and reports
that.

**The gate could fail, and was shown able to fail before it was applied.** The A/B trivial baseline
plants `2.0e-02` into one mode and measures **21.299 %** (arm O's log) / **22.492 %** (arm B's log),
failing both bands; the `1.0e-02` resolution probe measures **10.650 % / 11.246 %**, also failing
both. **A comparison that cannot fail is not a comparison** — and the measured `33.259 %` is
comfortably above the `21.3 %` that a deliberately-planted difference produced.

### 6.3 AB3 — iteration and evaluation counts, and the instrument that reads them: **PASS**

| arm | optimizer's **own** reported count | comparator `debug_print` blocks | registered offset `blocks = reported + 1` | iterations |
|---|---|---|---|---|
| **A** (IPOPT) | `Number of objective function evaluations = 12` | **13** | **13 = 12 + 1 ✔** | **11** majors |
| **B** (SLSQP) | `NFUNC = 15` (`opt_SLSQP.txt`), `NGRAD = 14` | **16** | **16 = 15 + 1 ✔** | **13** iterations |

**The gate is on the instrument, not on the size of the difference, and the instrument held on both
arms.** The offset measured on arm O transferred to a *different optimizer* unchanged — which is
evidence that the `+1` is a property of OpenMDAO's `debug_print` (one block for the pre-driver
evaluation), not of IPOPT. **Falsifier F5 did not fire.**

**The registered fallback was not needed.** §6.2 provided that if an arm printed no count of its own
the block count would be primary "and the record says so"; **arm B did print its own count**, in
`opt_SLSQP.txt`, so both arms were genuinely cross-checked. *(The frozen comparator's own regex reads
IPOPT's phrasing only; SLSQP's `NFUNC` line was read from the optimizer's own output file by the
grading driver — see §10.2.)*

**The measured cost comparison the counts support**: SLSQP needed **13 iterations and 15 function
calls** where IPOPT needed **11 majors and 12 evaluations** — **1.18× the iterations and 1.25× the
evaluations**, on evaluations-per-iteration of **1.15** (SLSQP) against **1.09** (IPOPT). **Both
optimizers barely backtracked on this problem.** §8 reads that into the cost.

### 6.4 AB4 — the constraint-violation path: **PASS** (instrument); **AB4-C not reached**; **AB4-H PASS**

`V_max := max over the whole function-evaluation path of |CL − 0.5|`, read by the same frozen
comparator from the same channel in each arm's own log.

| arm | **`V_max`** | at block | blocks | first | last |
|---|---|---|---|---|---|
| **A** (IPOPT) | **`2.60464e-03`** | **2** | 13 | `5.600e-07` | `1.900e-07` |
| **B** (SLSQP) | **`3.31407e-03`** | **4** | 16 | `5.600e-07` | `2.550e-06` |
| **ratio B/A** | **`1.2724`** | | | | |

**The instrument check passed on an independent reader.** The comparator's `V_max(A) = 2.60464e-03
at block 2` agrees with **IPOPT's own `inf_pr` column** — a completely separate instrument, read
from `armA/opt_IPOPT.txt` — which reports its maximum primal infeasibility as **`2.60e-03` at major
2**. Two independent readers, the same event, agreement to the printed digits.

**Full `CL` path, arm A (13 blocks):**
`0.49999944, 0.49999601, 0.49739536, 0.49775456, 0.49855985, 0.49913954, 0.49826749, 0.49989143, 0.49998639, 0.49999762, 0.49999635, 0.49999981, 0.49999981`

**Full `CL` path, arm B (16 blocks):**
`0.49999944, 0.49999314, 0.49986254, 0.49763132, 0.49668593, 0.49910813, 0.49966567, 0.49997931, 0.49995804, 0.499996, 0.49994799, 0.49985981, 0.49999166, 0.49990739, 0.49999746, 0.49999745`

**AB4-C: neither arm left the design-relevant neighbourhood.** Both maxima are **~30× below** the
`1.0e-1` threshold, so no `CD` value is disqualified from quotation on that ground.

**AB4-H — the hazard clause, complied with.** Quoted from the pre-registration, before either arm
ran:

> **A difference in the constraint-violation path between two optimizers is a statement about the
> two algorithms' handling of the constraint — interior versus active-set — and NOT about the flow.
> Neither arm's path excursion is reported as an aerodynamic, physical or design finding. An
> intermediate design that violates `CL = 0.5` is an infeasible probe of the optimiser's own path,
> and its `CD` is never quoted as a drag figure.**

**Accordingly:** arm B's path excursion is **1.27× arm A's**, it occurs two blocks later, and its
tail is **13.4× less converged** in `|CL − 0.5|` at the last evaluation (`2.55e-06` against
`1.90e-07`). **These are statements about two algorithms' handling of an equality constraint.** No
intermediate `CD` from either path is quoted anywhere in this record as a drag figure, and the only
`CD` values reported as drag are the two endpoint values at designs whose `CL` is inside the
registered `1.0e-5` gate. **P10 deliberately did not predict the direction**, and the measured
`1.2724` sits near the middle of its symmetric `[0.2, 5]` band.

### 6.5 AB5 — reported at §3: **PASS**

### 6.6 AB6 — cost comparison, like-for-like: **PASS** — and the measurement D1 could not make

D1 §9.3 had to report contention as **"not separately measured"** because the A4 §6.1 work-marker
method needs the same work timed in two arms and arm C produced no work. **This item has three
comparable arms doing the same primal on the same mesh on the same image**, so the method was
available for the first time on this ladder.

| marker | **arm A** (IPOPT, this session) | **arm B** (SLSQP, this session) | **arm O** (IPOPT, D1's session) |
|---|---|---|---|
| whole-arm core-min | **5.600** | **6.517** | 6.017 |
| whole-arm wall s | 336 | 391 | 361 |
| driver wall s (`run_driver()` alone) | **263.60** | **318.24** | 278.04 |
| evaluations (comparator blocks) | 13 | 16 | 13 |
| iterations | 11 | 13 | 11 |
| **wall per function evaluation** (driver wall ÷ blocks) | **20.2769 s** | **19.8900 s** | **21.3877 s** |
| core-min per iteration (whole arm) | **0.5091** | **0.5013** | 0.5470 |
| driver-only core-min per iteration | 0.3994 | 0.4080 | 0.4213 |

**The cross-session contention marker, MEASURED:**
`(wall-per-eval_A − wall-per-eval_O) / wall-per-eval_O = **−5.1935 %**` — magnitude **5.1935 %**.
**This session was 5.19 % FASTER than D1's session on identical work**, on the same image, script,
task, mesh and rank count, with a concurrent D3 lane live on the box throughout. **A large
contention term would have been a finding, not a failure; a small favourable one is equally a
finding, and it is reported rather than absorbed** (§8).

**Within this session the two arms' work markers agree to 1.9 %** (20.2769 s against 19.8900 s per
evaluation) — the like-for-like confirmation that the two arms bought the *same* primal, so the cost
difference between them is iteration count, not per-evaluation cost.

**AB6: PASS.** Every figure the gate requires is reported from each arm's own `ledger.txt` row and
log. The gate is on the instrument, not on the size.

---

## 7. Predictions P1 – P15, every one scored

| id | prediction | point | band | **measured** | **HIT / MISS** |
|---|---|---|---|---|---|
| **P1** | arm A termination class | `EXIT: Optimal Solution Found.` | present, `NLP error < 1e-5` | **printed; `4.0871e-07`** | **HIT** |
| **P2** | arm A major iterations | 11 | [10, 12] | **11** | **HIT** (point exact) |
| **P3** | arm A reproduction `\|ΔCD\|/CD` | < 1e-6 | ≤ 1.0e-4 | **`0.0` exactly** | **HIT** (point met) |
| **P4** | arm B pyOptSparse `inform` | 0 | `{0}` | **0** | **HIT** |
| **P5** | arm B iterations | 20 | [8, 60] | **13** | **HIT** on the band; **point missed** (0.65×) |
| **P6** | arm B function evaluations (blocks) | 30 | [10, 120] | **16** | **HIT** on the band; **point missed** (0.53×) |
| **P7** | **AB1** `\|ΔCD\|/CD_A` | < 0.10 % | ≤ 1.0 % | **0.7381 %** | **HIT** on the band; **point MISSED by 7.4×** |
| **P8** | **AB2** three statistics | ≤ 6.5 %; ≤ 6.09e-03; ≤ 0.05 deg | ≤ 10.0 %; ≤ 8.0e-03; ≤ 0.25 deg | **33.259 %; 1.9379e-02; 0.24281 deg** | **MISS** — two of three outside the band (AoA inside) |
| **P9** | **AB4** `V_max(A)` | `2.6046e-03` at block 2 | [1.30e-03, 5.21e-03] | **`2.60464e-03` at block 2** | **HIT** (point exact) |
| **P10** | **AB4** `V_max(B)/V_max(A)` | ∈ [0.2, 5] | [0.2, 5] | **1.2724** | **HIT** |
| **P11** | arm B endpoint FD, four components | ≤ 1.5 % each | all graded ≤ 5.0 %, zero flips | **0.0497 / 0.2073 / 0.1067 / 0.2485 %**, 4 of 4 graded, zero flips | **HIT** (point met) |
| **P11b** | arm B's selected step pairs | `{1e-4,3e-4}` shape; `{1e-3,3e-3}` `patchV[1]` | the same pairs | **exactly those pairs, all four components** | **HIT** |
| **P12** | arm B core-min per iteration | 0.465 | [0.35, 1.20] | **0.5013** | **HIT** (1.078× the point) |
| **P13** | total cost, core-min | 16.73 | ≤ 33.43; HARD ≤ 140.0 | **12.150** | **HIT** (0.726× the point) |
| **P14** | peak RSS, either arm | 1.70 GiB | ≤ 2.5 GiB | **1.6938 / 1.6927 GiB** | **HIT** (point met; `getrusage`, `/usr/bin/time -v` absent as registered) |
| **P15** | trivial baseline each arm @ `1e-8` | > 50 % | > 50 % | **112.6004 % / 111.8888 %**, both sign-flipped | **HIT** |

**14 HIT, 1 MISS (P8).** Three predictions hit their band while missing their point (P5, P6, P7) and
those are reported as such rather than as clean hits.

**The MISS is the item's finding, and it is the more valuable outcome.** P8 predicted the two
optimizers would agree on the design point to `‖Δshape‖₂/‖shape_A‖₂ ≤ 10 %`, on a basis that was
explicitly stated: **IPOPT's own final accepted step norm `‖d‖ = 6.09e-03` against
`‖shape_A‖₂ = 9.39e-02` is 6.486 %** — *"the scale at which IPOPT itself stopped moving, so two
solutions of the same NLP should agree at about that scale."* **That reasoning is now measured to be
wrong, and the reason it is wrong is worth carrying forward: an optimiser's own final step norm
measures where **it** stopped, not how sharply the NLP determines its optimum.** The two designs are
**5.1× further apart** than that basis predicted, while the objective separates them by only
0.74 %. Drafted as an `L-` candidate in §9.

---

## 8. Cost — registered versus actual (`CLAUDE.md` rule 12; Sanaa's 2026-08-23 directive)

`cost_basis: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.` The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); **every dollar
figure below is DERIVED.** Core-minutes are wall seconds × ranks ÷ 60, from the run root's own
`ledger.txt` rows — **measured**, not estimated.

| stage | predicted core-min | **actual core-min** | ratio |
|---|---|---|---|
| phase-1 image probe (§3.1) | 0.033 | **0.033** | 1.00× |
| zero-compute controls, staging, md5 asserts, grading | 0.000 | **0.000** | — |
| **arm A** (IPOPT) | 6.017 | **5.600** | **0.931×** |
| **arm B** (SLSQP) | 10.683 | **6.517** | **0.610×** |
| **TOTAL** | **16.733** | **12.150** | **0.726×** |
| in dollars | $0.014307 DERIVED | **$0.010389 DERIVED** | |
| against the 100 % contingency band (≤ 33.466) | | **36.3 % of it** | |
| against the **HARD ceiling 140.0** | | **8.68 % of it** | |
| against the **curriculum row's own ~140 core-min** | | **0.0868×** | |

**No overrun. No arm was stopped by a budget, a timeout or a cap.** Arm A used **37.3 %** of its
900 s timeout; arm B used **14.5 %** of its 2,700 s timeout. The sum of the two caps (60.0 core-min)
was never approached.

**WASTE: 0.000 core-min, named explicitly and separately** (`COMPUTE_BUDGET_CHARTER.md` §6). Both
arms returned `rc = 0`, both produced every artifact the item was bought for, nothing was re-run,
nothing was discarded, no crash occurred, and no arm was launched twice. The launch gate opened on
the first reading for both arms, so **not one core-minute was spent waiting**. There is no waste to
separate out and none is laundered into the ratio's explanation.

**CONTENTION: MEASURED, and favourable — `−5.1935 %`** (§6.6). This is the first time this ladder
has measured a contention term rather than declaring it "not separately measured". It is **not**
netted into the misprediction below; the two are reported separately.

**MISPREDICTION: the whole of the remaining gap, and it is almost entirely arm B.**

* **Arm A came in at 0.931× its prediction** — a prediction that was simply arm O's measured 361 s.
  The 25 s difference is the contention term above (a faster session) plus a shorter driver
  (263.60 s against 278.04 s on identical work).
* **Arm B came in at 0.610×, and the cause decomposes cleanly into two independent factors:**
  * **Iterations over-predicted 20 → 13 (0.65×).** P5's band was registered wide *on purpose*
    (`[8, 60]`) because no SLSQP anchor existed anywhere in this lab; **the band carried the
    prediction and the point carried nothing** — the identical shape of D1's own P2 outcome.
  * **Per-iteration cost over-predicted 27.92 s → 24.48 s of driver wall (0.877×).**

**Whether C-24's calibration lesson transferred — the row this item was registered to answer.**
C-24's lesson was: *"an estimate built from a whole-`check_totals` anchor prices a line search into
every major; when the optimiser accepts full steps, the per-major basis must be re-derived from the
accepted-step composition, and the `ls` column is where that is read."* P12 applied the corrected
lesson and then **added one line-search primal back** (25.28 + 2.64 = 27.92 s), on the reasoning that
an active-set SQP with an L1 merit line search *would* backtrack where IPOPT had not.

**Measured answer: the lesson transferred, and the correction added on top of it was itself an
over-correction.** SLSQP's evaluations-per-iteration is **1.15** (`NFUNC 15` over 13 iterations)
against IPOPT's **1.09** (12 over 11) — **SLSQP backtracked, but barely**, buying roughly **two**
extra primals across the whole run rather than one per iteration. The measured driver cost was
**24.48 s/iteration**, which is **below** even the no-line-search figure of 25.28 s that D1
measured. **The rule to carry forward: price a line-search primal by the measured
evaluations-per-iteration ratio, not by assuming one trial per iteration — and that ratio is
readable after the fact from `NFUNC`/`NGRAD` (SLSQP) or the `ls` column (IPOPT).** Drafted as an
`L-` candidate in §9.

**Per-evaluation and per-iteration ratios, all three registered by §8.2:**

| basis | predicted | actual | ratio |
|---|---|---|---|
| **total** | 16.733 core-min | **12.150** | **0.726×** |
| **arm B per iteration** | 0.465 core-min | **0.5013** | **1.078×** |
| **arm B per function evaluation** | 0.3564 core-min (10.683 ÷ 30) | **0.4073** (6.517 ÷ 16) | **1.143×** |

**A calibration point that only shows up when all three are stated, and which is why §8.2 registered
all three:** the *per-unit* predictions were slightly **under**-estimates (1.08× and 1.14×) while the
*total* was a 1.38× over-estimate. **The whole of the total's error is in the count of units, not in
the price of one.** An estimate whose per-unit basis is good to 8–14 % can still miss the total by
38 % if the iteration count is guessed; **the count is where the estimating effort belongs on this
ladder.**

**The calibration row drafted for the supervisor to land is at §9.4.** This lane does not write
`docs/COST_CALIBRATION.md` under D1 Amendment 1 §A1.1 as adopted — but the brief for this phase
directed this lane to land it, so it is **both** drafted here **and** appended, with the id
re-derived from the file's own tail in the same shell invocation as the commit (`CLAUDE.md`
rule 11), from the **`HEAD` blob**, never from the worktree copy (which was measured stale by 22 ids
at the time of writing — see §10.3).

---

## 9. Record candidates — DRAFTED, for the supervisor's append

**This lane appends none of `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md` or
`docs/LAB_STATE.md`.** Numbers below are placeholders; **every id must be re-derived at append time
from the file's own tail — the MAXIMUM existing number, never a count** (`CLAUDE.md` rule 11).

### 9.1 `N-D` candidates (numerics / capability facts)

**`N-D<next>` — `ParOpt` ships in `dafoam-idwarp-rot:v1` and does not import; this box has no
trust-region optimizer.** Measured by a 2 s × 1 rank image probe (0.0333 core-min, rc 0) on the
graded image, `pyoptsparse 2.10.1` at
`/home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/pyoptsparse/`. `ParOpt`
(a trust-region interior-point method) is present as a package directory `pyParOpt/` **with no
compiled `.so`** and fails to import; `SNOPT` (licensed) and `NLPQLP` fail on absent compiled
modules. The compiled extensions actually present are `pyipoptcore`, `slsqp`, `psqp`, `conmin`,
`nsga2`. **Instantiable set: `IPOPT`, `SLSQP`, `PSQP`, `CONMIN`, `NSGA2`, `ALPSO`.** This is the A6
forward-AD precedent's shape — a "supported" capability that does not run. **Consequence for the
curriculum: any row promising trust-region behaviour is `NOT DELIVERED BY CONSTRUCTION` until
someone decides to build it, and that decision is not a lane's.**

**`N-D<next+1>` — A1 at `np=1` on `dafoam-idwarp-rot:v1` is bit-reproducible across sessions through
a whole optimisation.** Arm A reproduced D1 arm O **exactly** — `CD_feasible`, `CD`, `CL`, all eight
`shape` modes, `AoA` and the major-iteration count all identical to the last printed digit
(five AB5 rows measured **`0.0`**, not merely inside `1e-9`) — from a freshly staged case, in a
different session, 2 h later, on a box carrying a concurrent lane. This is **stronger than A4 §3.2's
1.8e-07 same-optimizer figure** and stronger than the cold-primal bit-identity D1 §3 measured: it
holds through 11 optimiser majors, ~12 primal solves and `findFeasibleDesign`. **Practical use: an
A/B on this case does not need a repeat arm to establish its own reproducibility floor — the floor
is zero.**

**`N-D<next+2>` — the OpenMDAO `debug_print` block count exceeds the optimizer's own reported
function-evaluation count by exactly 1, and the offset is optimizer-independent.** Measured 13 = 12+1
(IPOPT, twice — arm O and arm A) and 16 = 15+1 (SLSQP, `NFUNC` from `opt_SLSQP.txt`). The `+1` is a
property of the driver's printing, not of the optimizer.

**`N-D<next+3>` — pyOptSparse SLSQP's converged termination on this box prints
`Inform 0 / "Optimization terminated successfully."`** under an `Exit Status` header, and
`opt_SLSQP.txt` closes with `ITER = <n>`, `NUMBER OF FUNC-CALLS: NFUNC = <n>`,
`NUMBER OF GRAD-CALLS: NGRAD = <n>`. **This wording had never been printed in this lab before**; the
D2 gate keyed on the numeric code rather than the string for exactly that reason, and the strings are
now on the record for the next item to key on.

### 9.2 `L-` candidates (lessons)

**`L-<next>` — an optimiser's final accepted step norm does NOT bound how far two optimizers'
optima can sit apart.** D2's AB2 band was built on IPOPT's own final `‖d‖ = 6.09e-03` against
`‖shape‖₂ = 9.39e-02` (6.486 %), reasoning that *"two solutions of the same NLP should agree at
about the scale at which the optimiser stopped moving."* **Measured: 33.259 %, 5.1× that basis**,
while the objective separated the two designs by only **0.74 %**. **The step norm measures where one
algorithm stopped; the *conditioning of the NLP* is what bounds the spread of its optima, and on a
flat-valleyed problem those are different by a large factor.** Cost of learning it: one `GATE FAIL`
on a gate that was registered before the run and is reported as failed.

**`L-<next+1>` — price a line-search primal by the measured evaluations-per-iteration ratio, never
by assuming one trial per iteration.** C-24 taught that a `check_totals`-derived per-major basis
prices a line search into every major and over-prices a no-backtracking run. D2's P12 applied that
lesson and then added one line-search primal back on the (correct) reasoning that an active-set SQP
would backtrack where an interior-point filter had not. **It does backtrack — at 1.15
evaluations/iteration against IPOPT's 1.09, i.e. about two extra primals in the whole run, not
thirteen.** The measured per-iteration driver cost, **24.48 s**, came in **below** D1's own
no-line-search 25.28 s. **`NFUNC`/`NGRAD` (SLSQP) and the `ls` column (IPOPT) are where the ratio is
read after the fact; use the ratio, not the assumption.**

**`L-<next+2>` — in a session-shared scratchpad, a generic draft filename is an accidental handoff,
and a `test -s` provenance check will pass on the wrong file.** This lane's first attempt at the
authorisation addendum wrote its draft to a generic `addendum.md` in the session scratchpad, which a
concurrently running D3 lane already held a **different** file under. `test -s` passed on the foreign
file. **The guard that caught it was the per-invocation stamp assertion** (`grep -q "$TS"` on the
draft), which failed and stopped the chain; the frozen file was re-verified byte-unchanged
(`aebf26ed722e417b715cf0eb48cd4493`) and nothing foreign was ever appended. **L-252's rule was
written for run-root artifacts; it binds a lane's own scratch drafts just as hard, and the assertion
that saves you is a content check, not an existence check.**

**`L-<next+3>` — a per-unit cost basis good to 8–14 % can still miss a total by 38 %; the unit
*count* is where estimating effort belongs.** D2 predicted 16.733 core-min and spent 12.150
(**0.726×**), while its per-iteration and per-evaluation bases were **1.078×** and **1.143×** —
i.e. slight *under*-estimates. **The whole of the total's error was in predicting how many iterations
an unfamiliar optimizer would take** (20 predicted, 13 measured). The registered response is the one
D1's P2 and D2's P5 both used and which worked both times: **register a wide band and say plainly
that the width, not the point, is carrying the prediction.**

### 9.3 `D` (docket) candidate

**`D<next>` — curriculum item D2 executed and graded: IPOPT vs SLSQP on the D1 NLP, one CLI token
apart on a byte-identical script.** Both arms `rc = 0`, both per-arm gate sets **PASS**, **AB5
PASS** (arm A reproduced D1 arm O **bit-identically**), **AB1 PASS** (0.7381 %, inside the 1.0 %
band), **AB2 GATE FAIL** (33.259 % / 1.9379e-02 — the two optimizers reached different designs),
**AB3/AB4/AB6 PASS**. **12.150 core-min of a registered 16.733 and a 140.0 ceiling; zero waste;
contention MEASURED at −5.19 %.** 14 of 15 predictions HIT; P8 MISS is the finding.
**The trust-region half of the ratified curriculum row is `NOT DELIVERED BY CONSTRUCTION`** and is on
Sanaa's desk as a supervisor NOTICE, not read into the blanket. Records:
`cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md`; prereg frozen `03580b8f`, authorisation `641c5938`.

### 9.4 `docs/COST_CALIBRATION.md` row — drafted **and landed by this lane on the brief's direction**

Ten columns, id re-derived from the `HEAD` blob's tail at commit time. Its content is §8, condensed:
predicted **16.733** against actual **12.150** (**0.726×**), $0.010389 **DERIVED**, waste **0.000
core-min** named separately, contention **MEASURED at −5.1935 %** (the first on this ladder), the
three ratio bases (total / per-iteration / per-evaluation), and **C-24 named** with the measured
answer that its per-major lesson **transferred and was over-corrected**.

### 9.5 `../../LADDER_A_STATUS.md` row — **DRAFTED, not appended**

| # | rung | what | toolchain | np | verdict | numbers | record |
|---|---|---|---|---|---|---|---|
| *next* | **A1** curriculum **D2** | optimizer A/B on the D1 NLP: IPOPT vs SLSQP, one CLI token apart on a byte-identical script | **PATCHED** | 1 | **arm A PASS / arm B PASS (per-arm); AB2 GATE FAIL; AB1, AB3, AB4, AB5, AB6 PASS** | `CD_A 0.0175279`, `CD_B 0.0176573`, `ΔCD 0.7381 %`; `‖Δshape‖₂/‖shape_A‖₂ **33.259 %**`, `‖Δshape‖_∞ 1.9379e-02`, `ΔAoA 0.2428 deg`; IPOPT 11 majors / 12 evals, SLSQP 13 iters / 15 calls, `Inform 0`; endpoint FD worst **0.2553 % (A)** / **0.2485 % (B)**, 8 of 8 graded, zero flips; **12.150 core-min, zero waste** | `A1/curriculum_D2/RESULTS.md` |

### 9.6 `EXPERTISE_CURRICULUM.md` §7 execution-state ledger row — **DRAFTED, not appended**

| date | item | state | record |
|---|---|---|---|
| 2026-08-24 | **D2** optimizer A/B on the D1 NLP (Tier 1) | **CLOSED — graded.** Both arms ran and were graded (IPOPT / SLSQP, one CLI token apart on a byte-identical script); AB5 PASS bit-identically, AB1/AB3/AB4/AB6 PASS, **AB2 GATE FAIL — the two optimizers reached different designs (33.259 % in `L2`) at the same objective to 0.74 %**. 12.150 core-min of a registered 16.733 (0.726×) against the row's own ~140 figure; zero waste. **The row's "trust-region" half is `NOT DELIVERED BY CONSTRUCTION`: the graded image carries no importable trust-region optimizer (`ParOpt` ships without its compiled extension; `SNOPT` and `NLPQLP` absent), measured by a 0.0333 core-min probe BEFORE the freeze and disclosed on the pre-registration's first screen. This item delivers interior-point vs active-set SQP — both line-search methods. The narrowing is on Sanaa's desk as a supervisor NOTICE and is NOT read into the blanket (`CLAUDE.md` rule 9); nothing about building `ParOpt` was run or prepared.** | prereg `cases/dafoam/ladder-a/A1/curriculum_D2/PREREGISTRATION.md` frozen `03580b8f`, authorisation §18 at `641c5938`; results `…/curriculum_D2/RESULTS.md` |

---

## 10. Departures, disclosures, and what this item did NOT establish

### 10.1 Departures from the frozen sequence: **none in any gate, threshold, band, cap or label**

§13's launch sequence was executed as written: stage → tree-listing diff against D1's `base/` (EMPTY)
→ eight md5 asserts → six zero-compute controls → G6 → arm A → **AB5 checked before arm B** → G6 →
arm B → grade. **No gate was moved, no band widened, no threshold re-read, no arm relaunched, no
frozen file edited.**

### 10.2 One disclosure about the grading path, stated rather than smoothed

**The frozen comparator `d2_ab.py` carries no A/B CLI subcommand.** Its `compare()`,
`path_max_cl_violation()`, `l2()`, `linf()` and `eta_observed()` kernels are reachable only by
import — the CLI exposes `selftest`, `plantcheck`, `negcheck`, `keycheck`, `tagcheck`, `abtrivial`
and `path` only. **The frozen file was therefore imported, unedited, by a grading driver written into
the run root**, which asserts `md5(d2_ab.py) == 20db6e121556221082133adab35716fb` **before** importing
it and refuses (exit 2) on a mismatch.

**The driver contains no statistic of its own.** Every A/B number in §6 comes from the frozen
`compare()`; every path number from the frozen `path_max_cl_violation()`; every norm from the frozen
`l2()`/`linf()`. What the driver adds is (a) transcription of the §6/§7 thresholds, which are frozen
numbers read from the pre-registration, and (b) two readers the frozen comparator does not have:
SLSQP's own `NFUNC`/`NGRAD`/`ITER` from `opt_SLSQP.txt` and IPOPT's own `inf_pr` column from
`opt_IPOPT.txt` — **both of which strengthen the record** (AB3's cross-check on arm B and AB4's
independent-instrument check on arm A) rather than replacing anything frozen.

Two driver files exist and both are kept, by path and md5, because the first graded AB5 **before**
arm B launched and the second graded the A/B **after**:

| file | md5 | what it graded |
|---|---|---|
| `d2_grade_20260824T175938Z_1526213.py` | `f1fbc06540c2ac7267ddffcff7ee95b2` | AB5, before arm B was launched |
| `d2_grade_ab_20260824T181131Z_1537564.py` | `eacee063be9688601f169e8713dc3789` | the full A/B, after both arms |

**The second is the first plus appended readers; the first was not edited.** The AB5 numbers in §3
are the first driver's own output (`ab5_20260824T175746Z_1524887.json`) and are reproduced identically
by the second (`ab_report_20260824T180411Z_1530445.json`), so the pre-arm-B grading is checkable
against the post-arm-B one.

### 10.3 The shared index and the worktree, inspected and never reverted

Twice during this item the shared working tree was measured stale, and in both cases it was
**inspected, never reverted** (`CLAUDE.md` rule 10):

1. **The shared git index carried staged deletions for all six of this item's own files** while the
   same files were byte-identical on disk and at `HEAD` — the D486 shared-index decay. The
   private-index protocol reads its tree from `HEAD` and is unaffected.
2. **`docs/COST_CALIBRATION.md` in the worktree read a maximum id of `C-14` while the `HEAD` blob
   read `C-36`** — the worktree copy was **22 ids behind**. Every id derivation and every blob this
   lane committed was built from `git show <HEAD>:<path>`, never from the worktree.

### 10.4 What this item did NOT establish, listed by name

* **Nothing about the SHIPPED toolchain row.** It was not entered; it remains `BLOCKED` where D1 left
  it, and D1 §3.3's shipped-image optimisation twin **stays deferred at its registered 19.8
  core-min** — not run, not re-priced, not re-argued.
* **Nothing about trust-region behaviour** (§1, §9.1).
* **Nothing about which design is aerodynamically better**, and nothing aerodynamic from either
  arm's constraint-violation path (AB4-H).
* **Nothing about global optimality.** Two algorithms reaching two points is not evidence that either
  is a local rather than a global optimum, and no such claim is made.
* **Nothing about memory boundaries.** Both arms sat at 1.69 GiB against a 6 GiB cap with the launch
  floor at 12 GiB; the item is not memory-bound and characterises no boundary (L-15).
* **`η` was INHERITED, not re-measured**, and it grades nothing here. The per-arm observed noise
  floors — `ETA_OBSERVED_A = 4.7626e-08`, `ETA_OBSERVED_B = 4.5985e-08` — are **observations,
  reported only, sizing nothing.** An observation is not a measurement and this record does not
  upgrade one into one.
* **Nothing N=29-gated, nothing in Tier 6, and nothing about `../curriculum_D1_Cprime/`**, which is
  untouched, unblocked and unaffected.

---

## 11. Artifacts this record cites

All under `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/` unless stated. **This
document cites no scratch path** (`CLAUDE.md` rule 13, L-186).

| artifact | what it carries |
|---|---|
| `ledger.txt` | both arms' rc, wall, ranks, core-min, `docker inspect` exit + OOMKilled, peak RSS |
| `preflight_history.txt` | both G6 readings with their `date -u` stamps |
| `armA_20260824T175746Z_1524887.log` (+ `.ok.<stamp>`) | arm A in full; md5 `72d2a295c22c57ec601fb6245151c08d` |
| `armB_20260824T180411Z_1530445.log` (+ `.ok.<stamp>`) | arm B in full; md5 `5d3b14dae799ac6f869515c62bb11e4f` |
| `armA/endpoint_20260824T175746Z_1524865.json` | arm A's step plan, per-component FD, trivial baseline, constraints, `getrusage` |
| `armB/endpoint_20260824T180411Z_1530423.json` | arm B's, likewise |
| `armA/opt_IPOPT.txt` | IPOPT's own iteration table, incl. the `inf_pr` column AB4 cross-checks against |
| `armB/opt_SLSQP.txt` | SLSQP's own `ITER`/`OBJ` table, `NFUNC = 15`, `NGRAD = 14` |
| `ab5_20260824T175746Z_1524887.json` | AB5 as graded **before** arm B launched |
| `ab_report_20260824T180411Z_1530445.json` | the full A/B report |
| `controls/`, `controls_armA/`, `controls_armB/` | the control working directories |
| `d2_ab.py`, `d1_opt_runScript.py`, `d1_fd_endpoint.py`, `d2_run_arm.sh`, `d2_preflight.sh` | the five frozen instruments, md5-verified copies |
| `d2_grade_20260824T175938Z_1526213.py`, `d2_grade_ab_20260824T181131Z_1537564.py` | the grading drivers (§10.2) |
| `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO_20260824T160553Z_1400030.log` | D1 arm O, **read only**, md5 `64bee1631d28ab07973e56ec7e1f4bf3` before and after |

---

**END OF RESULTS. NOT FILED ANYWHERE. SUBMISSIONS PARKED.**

---

## Addendum 1 — 2026-08-24, supervisor check 1 (measurement-script diff, read personally): both run-root grading drivers RESTATE the A/B band constants INLINE, and every restated constant equals the frozen registration

**Document version: v1.0 → v1.1. Lines whose number changed above this section: 0.**
**Zero compute.** No number, band, gate, threshold, cap, label, verdict, prediction
score, ratio or cost figure moves; nothing above this section is rewritten, no
frozen file is edited and no gate is re-opened. `date -u` at writing:
**2026-08-24T18:26:08Z**.

**What the check found.** §10.2 already discloses that the frozen comparator
`d2_ab.py` carries no A/B CLI subcommand and was therefore imported, unedited, by a
grading driver written into the run root — and that the driver "transcribes the
§6/§7 thresholds". The supervisor's personal §3 check-1 read of that driver **as a
diff** makes the transcription specific, which the prose above does not. **Both**
drivers,

- `d2_grade_20260824T175938Z_1526213.py` (md5 `f1fbc06540c2ac7267ddffcff7ee95b2`), and
- `d2_grade_ab_20260824T181131Z_1537564.py` (md5 `eacee063be9688601f169e8713dc3789`),

carry the A/B bands as **inline literals**, at the **same line numbers in both**:

- **line 42** — `AB1_POINT, AB1_BAND = 1.0e-3, 1.0e-2            # 0.10 % / 1.0 %`
- **line 43** — `AB2_POINT = {"l2_rel": 0.065, "linf": 6.09e-03, "aoa": 0.05}`
- **line 44** — `AB2_BAND  = {"l2_rel": 0.10, "linf": 8.0e-03, "aoa": 0.25}`

**Why the grade nevertheless stands, and this is the load-bearing half.** Every
literal was checked against the **frozen** sources — the comparator committed at
`03580b8f` and the pre-registration frozen at the same commit — not against memory
and not against the record that cites them:

- `0.10` and `8.0e-03` are **byte-for-byte the frozen comparator's own constants**,
  `d2_ab.py:38–39`: `AB2_BAND_L2_REL = 0.10   # gate AB2, frozen band` and
  `AB2_BAND_LINF = 8.0e-03   # gate AB2, frozen band`.
- `0.25` (deg) and the `AB1` pair `1.0e-3` / `1.0e-2` are **not** in `d2_ab.py` at
  all; they are registered in the **pre-registration only**, and they reproduce its
  `P8` and `P7` rows exactly — *"`≤ 10.0 %`; `≤ 8.0e-03`; `≤ 0.25 deg`"* and
  *"`< 0.10 %`" / "`≤ 1.0 %`"* (`PREREGISTRATION.md` :617–:618, §6.2).
- The `AB2_POINT` triple `0.065` / `6.09e-03` / `0.05` likewise reproduces `P8`'s
  registered **point** predictions.

**The instrument is therefore CALIBRATED to the freeze on both A/B gates, and
neither the `AB1` `PASS` nor the `AB2` `GATE FAIL` was produced by a threshold
chosen after the answer was visible.** The margins make this checkable rather than
merely asserted: `AB1` read **0.7381 %** against a 1.0 % band, and `AB2` read
**33.259 %** against 10.0 % — **3.3× outside** — and **1.9379e-02** against
8.0e-03. No plausible transcription error manufactures a 3.3× breach, and the
`AB2` L2 and L∞ literals are in any case the frozen comparator's own.

**What is being disclosed is a STRUCTURAL hazard, not a wrong number.** A band that
lives in two places — the frozen comparator and a transcription in an unfrozen
driver — can drift in the unfrozen copy, and the record above cites the driver's
output. Here the two copies agree and the third source (the pre-registration)
agrees with both. **The hazard is that nothing in the driver asserts that
agreement**: it asserts `md5(d2_ab.py)` before importing it, which pins the
comparator, but it does not assert `AB2_BAND == {d2_ab.AB2_BAND_L2_REL,
d2_ab.AB2_BAND_LINF}`. That assertion is one line and was not written.

**Not repaired here, deliberately.** Both drivers produced this item's graded
numbers; editing either after grading would break the correspondence between this
record and the artifacts that made it, for a change that alters no output. **The
defect is recorded rather than fixed** (the same disposition as
`../curriculum_D1_Cprime/RESULTS.md` Addendum 2), and the correction belongs in the
next DAFoam grading driver that copies this one: *a driver that restates a frozen
band asserts equality against the frozen symbol it copies, or it imports the symbol
and restates nothing.*

**No gate is re-opened and no verdict changes. The item's verdicts stand exactly as
graded: per-arm gate sets `PASS` / `PASS`; `AB1`, `AB3`, `AB4`, `AB5`, `AB6`
`PASS`; `AB2` `GATE FAIL`, reported as failed and not re-banded; `P8` a `MISS`;
12.150 core-min, waste 0.000. NOT FILED ANYWHERE. SUBMISSIONS PARKED.**
