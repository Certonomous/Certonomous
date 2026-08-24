# Curriculum item D2 — Optimizer A/B on the D1 problem (IPOPT vs SLSQP): PRE-REGISTRATION

**NOT FILED ANYWHERE.** Nothing in this document or the item it registers is filed, sent, emailed,
uploaded, posted, registered, submitted or commented outside this box, now or ever (`CLAUDE.md`
rule 7; `DAFOAM_CHARTER.md` §10). **SUBMISSIONS PARKED.** Readiness is not sending, and no reading
of this file authorises a send. **The five upstream DAFoam defect drafts are untouched by this item
and remain drafts.**

**Written 2026-08-24T17:48:27Z by Lane D2 (Opus), DAFoam team, for curriculum item **D2**
(`cases/dafoam/EXPERTISE_CURRICULUM.md` §3 Tier 1, RATIFIED 2026-08-23 under the conservative
reading of its §7).** Every UTC stamp in this file is `date -u` output read in the shell invocation
that wrote it into the file (D1 `PREREGISTRATION.md` §15 Amendment 1 §A1.2, adopted here).

**PHASE 1 ONLY. This freeze authorises NOTHING. No container is started, no solver is run and no
core-minute is spent by the invocation that commits this file.** Launch authorisation comes
separately, in writing, from the dafoam-supervisor, after its personal verification of this freeze
(`SUPERVISION_CHARTER.md` §3: pre-registration **committed** before compute, and that check is the
supervisor's, not this lane's). **No agent message is Sanaa's consent** (`CLAUDE.md` rule 9).

**One exception to "zero compute", declared here rather than buried:** a single **image probe** of
**2 s wall × 1 rank = 0.0333 core-min** was run in phase 1 to establish which pyOptSparse optimizers
are actually installed (§3.1). It started no solver, read no case and wrote nothing into any run
root. It is costed in §8 and counted against this item's ceiling.

---

## 0. What this item is, in four lines

1. **Run the *same frozen NLP* — D1's lift-constrained NACA0012 drag minimisation, the same case,
   mesh, FFD, constraint set, image, decomposition and run script — twice, changing exactly one
   token: the pyOptSparse optimizer.** Arm **A** = `IPOPT`, arm **B** = `SLSQP`.
2. **The graded claim is about the optimizers, not about aerodynamics.** What is measured is: do two
   different NLP algorithms reach the same design point; at what iteration and function-evaluation
   cost; and along what constraint-violation path.
3. **Arm A also exists as the item's master control.** It must reproduce D1 arm O (`b10260a0`) to a
   frozen tolerance. If it does not, the staging is not D1's staging and **every A/B figure in this
   item is `NOT A RESULT`** — because a difference between arms could then be the staging rather
   than the optimizer.
4. **The registered hazard, named in the curriculum row and carried into a gate:**
   *optimizer-dependent constraint-violation paths read as physics.* Gate **AB4-H** forbids it in
   words, before either arm runs.

**The conservative reading that binds this item, quoted from `EXPERTISE_CURRICULUM.md` §7:**

> **The approval is therefore read conservatively (`CLAUDE.md` rule 9 — an approval is only as wide
> as what was approved):**
> 1. It authorizes **starting execution** of this curriculum in the recommended sequence, with every
>    item under its own frozen, costed pre-registration, and only **pre-authorised-class items
>    (<$25) run on it**.
> 2. It is **NOT** read as: a per-item cost reading (rule 9 — the blanket is not one); approval of
>    Tier 6 (instances/GPU stay NEEDS COSTING + her explicit per-item approval, GPU outside the
>    2026-08-21 blanket); the D464 **N=29 gate reading** (the chief's relay states this explicitly —
>    N=29-gated arms stay parked); or approval of anything a future prereg finds unusual —
>    **anything unusual, above pre-authorised cost, or outside these pages goes back to Sanaa
>    costed, not read into the blanket.**
> 3. Her standing requirement binds every executed item: **formal .md updates** … and **lab-wide
>    propagation** of any knowledge the entire lab must have, routed through the chief for
>    `CLAUDE.md`/charter-level changes.

**One thing this item finds that §7 item 2 makes this lane raise rather than absorb, stated on the
first screen.** The curriculum's D2 row promises *"optimizer/**trust-region** behavior as a measured
comparison."* **The probe of §3.1 measured that no trust-region optimizer is installed and
importable on this box**: `SNOPT` (licensed), `ParOpt` (a trust-region interior-point method) and
`NLPQLP` all fail to import; the installed and instantiable set is `IPOPT`, `SLSQP`, `PSQP`,
`CONMIN`, `NSGA2`, `ALPSO`. **This item therefore delivers interior-point vs active-set SQP — both
line-search methods — and the "trust-region" half of that curriculum row is `NOT DELIVERED` by
construction, not by choice.** That is a **narrowing** of a ratified deliverable; it is cheaper and
smaller, not wider, so this lane does not treat it as an over-blanket item — **but it is a departure
from the ratified wording and it goes on the supervisor's desk with this freeze, for the
supervisor to decide whether it reaches Sanaa's.** Nothing here reads the narrowing into the
blanket.

---

## 1. Frozen inputs — by md5, read on the host at this freeze

**These are inputs, not results.** A mismatch at launch **VOIDS** the item; it is not repaired,
re-derived or worked around.

### 1.1 D1 arm O — the frozen external reference (gate AB5)

| artifact | absolute path | md5 at this freeze |
|---|---|---|
| arm O's run log | `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO_20260824T160553Z_1400030.log` | **`64bee1631d28ab07973e56ec7e1f4bf3`** (848,000 bytes, 16,632 lines) |

The md5 is **frozen inside the comparator itself** as `d2_ab.py:ARMO_LOG_MD5`, asserted before the
file is opened and re-asserted after the planted-zero control has run, so the control cannot damage
the evidence it reads. **D1's run root is READ ONLY for this item: no file is created, moved or
deleted there, not even a `.plant` file** — the dry run of §5 proves that by md5, before and after.

**Arm O's values, frozen here and in `d2_ab.py:ARMO`** (from `../curriculum_D1/RESULTS.md` §4.2,
§4.4 at commit `b10260a0`, and re-read from the log itself at this freeze):

| quantity | value | log marker |
|---|---|---|
| `CD_feasible` (post-`findFeasibleDesign`, pre-optimiser) | **`0.020943920630946831`** | `D1_FEASIBLE_CD` |
| `CL_feasible` | `0.49999943897261456` | `D1_FEASIBLE_CL` |
| `AoA_feasible` | `5.153023459675001` deg | `D1_FEASIBLE_PATCHV[1]` |
| **`CD` at the accepted design** | **`0.017527899854535338`** | `D1_ENDPOINT_PATCHED_CD` |
| **`CL` at the accepted design** | **`0.49999981209363359`** | `D1_ENDPOINT_PATCHED_CL` |
| **`AoA`** | **`1.128636497545056`** deg | `D1_ENDPOINT_PATCHED_PATCHV[1]` |
| `shape` (8 modes) | `0.02876504584608877, 0.047201042921213354, 0.016871666037627377, 0.036676713888073136, 0.0472289265360477, 0.022959816884178426, 0.008262623112944891, 0.036138219756860344` | `D1_ENDPOINT_PATCHED_SHAPE` |
| **`‖shape‖₂`** | **`0.093899772805341328`** | computed by `d2_ab.py:l2` at this freeze |
| major iterations | **11** | `Number of Iterations....: 11` |
| objective function evaluations, IPOPT's own count | **12** | `Number of objective function evaluations = 12` |
| `debug_print` evaluation blocks, the comparator's count | **13** | `pyOptSparse_IPOPT\|0 … \|12` |
| IPOPT's final accepted step norm `‖d‖` | **`6.09e-03`** | `opt_IPOPT.txt` major 11 |
| driver wall (`prob.run_driver()` alone) | **`278.04`** s | `D1_DRIVER_WALL_S` |
| whole-arm wall / core-min | **361 s / 6.017 core-min** | D1 `RESULTS.md` §2 ledger row 3 |
| peak RSS | **1.6964 GiB** | `D1_OPT_MAXRSS_GiB` |
| **max `\|CL − 0.5\|` over the whole evaluation path** | **`2.6046399999999914e-03`, at block 2** | `d2_ab.py path`, §5.2 |

### 1.2 The staging source — three identities, re-read from disk at this freeze

**Staging source: `/home/ubuntu/certonomous-runs/W5-regrade/a1_unpatched/`, copied and never run
in** — D1 §9.3's own source, on the three identities all matching at this freeze **and matching
D1's own staged `base/` copy byte for byte**:

| file | md5 (re-read at this freeze) |
|---|---|
| `constant/polyMesh/points.gz` | **`38a486d29a540ecd1b06e006e66475e7`** |
| `FFD/wingFFD.xyz` | **`6ddf378b028d03d8a18270488bee1759`** |
| `runScript.py` | **`0557da51f6f179f6de865144343c499f`** |

**The published `W5-regrade` and `P1-a1-np1` trees are copied FROM, never run IN.** Staging removes
any numeric time directory, `processor*` and `reports/`, and restores `0/` from `0.orig/` (G8). The
three md5s are re-asserted on the staged copy before the first launch.

### 1.3 `η` — INHERITED, and it sizes nothing that could be fitted

**`η = 1.957349804806996e-08` is INHERITED from D1 arm E run 2 (MEASURED, `RESULTS.md` §3) and is
NOT re-measured here.** No arm E equivalent is bought. The reasons are D1-C′ §4.4's, adopted with
citation and re-checked against this item:

1. **The primal is the same primal.** Same case, same mesh md5, same image, same `np = 1`, same
   `primalMinResTol 1e-8`, same `printInterval 10`. The reverify A/B pair measured **8 of 8 raw
   `Jfd` components bit-identical** across the two images at np=1 on this case
   (`../reverify_patched_idwarp_np1/RESULTS.md` §3) — a direct measurement that the primal, and so
   its noise floor, does not move.
2. **`η` cannot reach an A/B statistic.** It enters only through each arm's own **endpoint** FD step
   selection, inside the container, through the frozen D1 instrument. **No A/B comparison statistic
   in §7 is a function of `η`.**
3. **A re-measurement would cost a cold primal (~0.5 core-min) to produce a number that changes
   nothing.** That is listed third, deliberately.

**Bought for nothing and reported:** each arm's own log prints `CD` at `printInterval 10`, so the
endpoint's own noise floor is *observable* from each arm's log at **0.000 core-min** via
`d2_ab.py:eta_observed` (D1 Amendment 2 §A2.2's registered window definition). **It is reported as
`ETA_OBSERVED_A` / `ETA_OBSERVED_B`, it sizes nothing, and it is not used to grade anything.** An
observation is not a measurement, and this file does not upgrade it into one.

---

## 2. The problem — D1's, unchanged, and the reason nothing about it may move

Objective `CD` (minimise, `scaler = 1.0`); **equality constraint `CL = 0.5`**; `thickcon ∈ [0.5,
3.0]` on **20** rows; `volcon ≥ 1.0` on **1** row; `rcon ≥ 0.8` on **2** rows — **24 constraint rows
in total**. Design variables: **8 FFD shape modes + `patchV[1]` (AoA in degrees)**; `patchV[0]`
(`U0`) is pinned `lower = upper = 10.0` and inert. **9 live DVs.** All of it is
`../curriculum_D1/PREREGISTRATION.md` §2, verbatim, and **this item changes none of it** — it
cannot, because the arms run D1's own script, byte for byte (§4).

The constraint normalisation is **already measured, not assumed**: all 24 rows read `1.0` at the
undeformed baseline, worst deviation `2.243e-13` (D1 `RESULTS.md` §3, falsifier F8 did not fire).

---

## 3. Toolchain — two rows, and the row this item grades is the **PATCHED** one

`DAFOAM_CHARTER.md` §6: shipped and patched are always two rows, and a patched row never replaces a
shipped row (R11).

| row | image | image ID / digest | `libidwarp.so` md5 | role in **this** item |
|---|---|---|---|---|
| **PATCHED** — **the row this item grades** | `dafoam-idwarp-rot:v1` | **`2927768a16ac`**, `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | **`85f59e87253e0a71a813f64ca6e4c425`** | **both** arms A and B run here |
| **SHIPPED** — **NOT ENTERED by this item** | `dafoam/opt-packages:latest` | **`9d45679d55fd`**, `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f0fcb488e0e98156575cd19548e91663` | untouched; stays exactly where D1 left it |

Both digests were re-read from `docker images --no-trunc` on this box in the invocation that stamped
and committed this file, and both matched the values D1 §3 registered. A version string is not an
identity: IDWarp reads `2.6.2` on both stacks and the two `.so` files are the same size — **the hash
is the only identity.**

**Which row this item grades, and why only one.** This item's axis is **the optimizer**. Adding the
toolchain axis would make it a 2×2 and confound the comparison: D1's own A/B on this case measured
the shipped `shape[6]` analytic **sign-flipped at the baseline (640.3696 %)**, so a shipped-image
optimisation is *a different question with a different answer*, and D1 §3.3 already registered that
question, priced it at **19.8 core-min**, and **deferred** it. **It stays deferred; this item does
not enter it, re-price it or re-argue it.** The SHIPPED row of the A1 optimisation ledger remains
`BLOCKED` exactly where `../curriculum_D1/RESULTS.md` §1 left it, pending the sibling mini-item
**D1-C′** (`../curriculum_D1_Cprime/`), which **this item does not touch, does not depend on and
does not block.** **R11 stands: this item's verdicts are patched-row verdicts and are never
reported as standing in for a shipped row.**

`dafoam-team:v1` is **rejected by name**, on D1 §3.2's two reasons, unchanged: it does not carry the
IDWarp rotation patch (it is `opt-packages` + the two `DALinearEqn.C` patches, both off by default),
so it would produce stock IDWarp numbers under a patched label; and it ends `USER dafoamuser`, which
collides with §10.1's uid pinning.

### 3.1 The image probe — what is actually installed, measured, not assumed

**Run in phase 1: one container, `--rm`, `--cpus=1`, `--memory=2g`, no case, no mesh, no solver.
2 s wall × 1 rank = 0.0333 core-min, rc 0**, on `dafoam-idwarp-rot:v1` (the graded image).
`pyoptsparse` version **`2.10.1`**, at
`/home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/pyoptsparse/`.

| optimizer | `pyoptsparse.OPT(name)` | class | reading |
|---|---|---|---|
| **`IPOPT`** | **OK** | primal-dual interior point, filter line search | **arm A** |
| **`SLSQP`** | **OK** | active-set SQP, L1 merit line search | **arm B** |
| `PSQP` | OK | preconditioned SQP (Lukšan) | gradient-based, but the frozen script carries **no options branch** for it — using it would require editing the script and would destroy arm A's md5 identity (§4). **Not chosen; named** |
| `CONMIN` | OK | method of feasible directions | **disqualified by the problem: inequality constraints only.** This NLP carries an *equality* (`CL = 0.5`) |
| `NSGA2`, `ALPSO` | OK | population / gradient-free | **wrong class** for a gradient-verified adjoint ladder, and would cost thousands of primals |
| `SNOPT` | **FAIL** — compiled `snopt` module absent | | licensed; not installed |
| **`ParOpt`** | **FAIL** — import error | **trust-region interior point** | **present as a package directory `pyParOpt/`, with no compiled `.so`, and not importable.** This is the A6 forward-AD precedent's shape — a "supported" capability that does not run — and is drafted as an `N-D` capability fact for the supervisor's append |
| `NLPQLP` | **FAIL** — compiled module absent | | not installed |

Compiled extensions actually present in the package: `pyipoptcore`, `slsqp`, `psqp`, `conmin`,
`nsga2` — and **no `snopt`, no `nlpqlp`, no ParOpt extension.**

**The choice of SLSQP, with its four reasons in order of weight:**

1. **It needs ZERO change to the frozen script.** `d1_opt_runScript.py` already carries an `SLSQP`
   options branch at lines **219–224** (`ACC 1.0e-5`, `MAXIT 100`, `IFILE "opt_SLSQP.txt"`) and an
   `-optimizer` command-line argument at line **23**. **The A/B is therefore one CLI token, on a
   byte-identical file** — the strongest form of "identical frozen prereg" the curriculum row asks
   for. Every other installed candidate would require a script edit and would forfeit that.
2. **It is gradient-based and handles the equality constraint**, so the comparison is
   like-for-like; `CONMIN` cannot take the equality at all.
3. **It is the sharpest methodological contrast available in the installed set:** a primal-dual
   **interior-point** barrier method with an adaptive barrier and a filter line search, against an
   **active-set** SQP with an L1 merit-function line search. Interior-point iterates approach the
   active constraints *from inside*; active-set iterates sit *on* them. That difference is exactly
   what the constraint-violation-path gate (AB4) is registered to measure.
4. **`ACC 1e-5` is the same tolerance class as IPOPT's `tol 1e-5`**, so §7's `ΔCD` band is a
   comparison at a comparable stopping criterion rather than at two arbitrary ones.

**What is honestly *not* bought, stated here and not softened:** neither optimizer is a
trust-region method. See §0.

---

## 4. The instruments — frozen in this repository, by md5, before the run root exists

### 4.1 Five files, all frozen by the commit that carries this document

| file | md5 at this freeze | lines | what it is |
|---|---|---|---|
| `d1_opt_runScript.py` | **`4c9811d16f344bc23136981cd6092d8f`** | 471 | **BYTE-IDENTICAL copy of D1's frozen run script**, `cmp`-verified against `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/d1_opt_runScript.py` at this freeze. **Zero registered changes.** Both arms run it |
| `d1_fd_endpoint.py` | **`7e454d2f1830a40086465d9b5c57a941`** | 145 | **BYTE-IDENTICAL copy of D1's frozen endpoint-FD instrument** (the driver Addendum §16 named as the graded instrument), `cmp`-verified. **Zero registered changes** |
| `d2_ab.py` | **`20db6e121556221082133adab35716fb`** | 611 | the A/B comparator: the reader, the four controls, the statistics. **Standard library ONLY** |
| `d2_run_arm.sh` | **`4629c57e64863db21625c6c61fd46e7d`** | 76 | the arm launcher; **7 diff hunks** against D1's `d1_run_arm.sh` (md5 `7571afabecd7760357f3a817a3de07d3`) |
| `d2_preflight.sh` | **`4e8641f93aa7ea6d40635870fdb8ccfc`** | 16 | gate G6, run as its own command; **2 diff hunks** against `d1_preflight.sh` (md5 `f0c841525642e11ddcfee46b97a0ff34`) |

**All five live in this repository directory, are committed with this file, and are copied into the
run root at staging with their md5s re-asserted against the values above — and `d2_run_arm.sh`
re-asserts the two script md5s again immediately before *every* launch.** The grading path is fixed
at the pre-registration commit in the literal sense `CLAUDE.md` rule 2 asks for: **the frozen file
*is* the committed blob, and every launch proves it by hash.**

**None of the five is edited after the first launch. An edit voids every arm that ran before it;
that voiding is reported, not repaired** (D1 §4.2(c), adopted verbatim as this item's own
condition — and D1 has already paid for that clause twice, at L-266 and L-273).

### 4.2 Why D1's filenames are kept inside this directory

`d1_opt_runScript.py` contains `import d1_fd_endpoint as _d1`. **Renaming either file would require
editing a line, and the edit would destroy the md5 identity on which arm A's entire evidentiary
value rests.** The D1 names are therefore kept, deliberately, and they carry their own provenance.
For the same reason the run script's printed markers stay `D1_*`: **the script IS D1's script.**
`d2_run_arm.sh` and `d2_ab.py` read `D1_*` markers and this is registered rather than tidied.

### 4.3 The one token that differs between the arms

| arm | invocation | everything else |
|---|---|---|
| **A** | `python d1_opt_runScript.py -task d1_opt -optimizer IPOPT` | identical |
| **B** | `python d1_opt_runScript.py -task d1_opt -optimizer SLSQP` | identical |

D1 arm O passed **no** `-optimizer` argument and took the script's default, `IPOPT`
(`d1_opt_runScript.py:23`). **Arm A's explicit `-optimizer IPOPT` selects the identical code path**;
the equality is the argparse default, and it is asserted at grading by AB5's reproduction of arm O's
numbers rather than merely argued here.

### 4.4 The `MAXIT 100` / `max_iter 40` asymmetry, disclosed rather than equalised

The frozen script caps IPOPT at `max_iter 40` (D1's registered change) and SLSQP at `MAXIT 100` (the
tutorial's own value). **The caps are not equalised, and the reason is that equalising one would
mean editing the file and forfeiting §4.1's identity.** They are also not the same unit: an IPOPT
major and an SLSQP iteration are different objects. **The binding cap on arm B is neither of them —
it is the `timeout` of §8.1, at ≈ 94 iterations of predicted cost. That is registered here, in
advance, with its consequence spelled out in G-B2.**

---

## 5. The controls — dry-run against the REAL artifact, at zero compute, BEFORE this freeze

`CLAUDE.md` rule 3: *a zero from a reader not shown able to see a non-zero is not evidence.* L-273
adds the half that killed D1 arm C: **a plant seen in a file no producer writes is not that
demonstration.** Every control below plants into, or corrupts, **a copy of D1 arm O's real log** —
the very file format arm A and arm B will emit, from the same producer.

The comparator carries **four** controls plus a statistics self-test, and **all refusals exit 2;
none degrades to a warning**:

* **plant** — perturbs **every consumed channel** (`path_dv`, `path_con`, `path_obj`,
  `marker_scalar`, `marker_vector`) by exactly `PLANT = 1.234e-03`, reads back through the **same**
  reader, and refuses unless **every one** moved by exactly the plant. A consumed channel the
  control does not plant into is precisely the hole L-273 names.
* **negative** — a deliberately blind reader that returns the unperturbed parse whatever path it is
  handed **must be refused**. A control that cannot fail is not a control.
* **key-set** — D1 arm C's own defect replayed: the producer's objective key is renamed to
  `...CD_final` and the comparator must refuse **by name**, not die on a `KeyError` inside a
  consumer.
* **optimizer tag** — an A/B consumes **two** logs; a comparator that cannot tell which arm it is
  reading can silently compare an arm with itself. The tag is renamed and a named refusal is
  required.
* **statistics self-test** — the path-maximum, `l2`, `linf` and `eta_observed` kernels are exercised
  on series with known answers. A statistic that cannot find a planted maximum is not permitted to
  compare two optimisers.

### 5.1 The dry run, pasted verbatim, executed at zero compute before this freeze

**No container. Host `python3`, standard library only. The source artifact's md5 is shown before and
after and is unchanged.** The `WORK` directory is a throwaway scratch directory used only to prove
the reader; **at launch the same code runs with the run root in its place, and no repository
document cites a scratch path** (`CLAUDE.md` rule 13, L-186).

```
UTC 2026-08-24T17:36:29Z | host ip-172-31-43-247 | Python 3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0] | stdlib only, NO container
SRC  = /home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO_20260824T160553Z_1400030.log
WORK = <scratch dry-run dir; the launch invocation uses the run root instead>
SRC md5 BEFORE  = 64bee1631d28ab07973e56ec7e1f4bf3

$ python3 d2_ab.py selftest
D2_SELFTEST_STATS {"eta_ok": true, "l2_ok": true, "linf_ok": true, "pass": true, "path_max": {"at_block": 2, "first": 0.0, "last": 1.0000000000287557e-06, "max": 0.007000000000000006, "n": 4}}
  rc=0

$ python3 d2_ab.py plantcheck $SRC $WORK IPOPT 64bee1631d28ab07973e56ec7e1f4bf3
D2_G5_PLANTED_ZERO OK {"channel_seen": {"marker_scalar": true, "marker_vector": true, "path_con": true, "path_dv": true, "path_obj": true}, "channels_planted": ["path_dv", "path_con", "path_obj", "marker_scalar", "marker_vector"], "max_residual_vs_plant": {"marker_scalar": 1.0837468075730605e-14, "marker_vector": 1.7932703932910243e-16, "path_con": 6.830473686658678e-17, "path_dv": 1.7932703932910243e-16, "path_obj": 1.0842021724855044e-18}, "n_blocks": 13, "pass": true, "plant": 0.001234, "src_md5_after": "64bee1631d28ab07973e56ec7e1f4bf3", "src_md5_before": "64bee1631d28ab07973e56ec7e1f4bf3", "src_unchanged": true}
  rc=0

$ python3 d2_ab.py negcheck  $SRC $WORK IPOPT
D2_REFUSE PLANTED_ZERO {"channel_seen": {"marker_scalar": false, "marker_vector": false, "path_con": false, "path_dv": false, "path_obj": false}, "channels_planted": ["path_dv", "path_con", "path_obj", "marker_scalar", "marker_vector"], "max_residual_vs_plant": {"marker_scalar": 0.001234, "marker_vector": 0.001234, "path_con": 0.001234, "path_dv": 0.001234, "path_obj": 0.001234}, "n_blocks": 13, "pass": false, "plant": 0.001234, "src_md5_after": "64bee1631d28ab07973e56ec7e1f4bf3", "src_md5_before": "64bee1631d28ab07973e56ec7e1f4bf3", "src_unchanged": true}
D2_G5_NEGATIVE_CONTROL OK refused=PLANTED_ZERO
  rc=0

$ python3 d2_ab.py keycheck  $SRC $WORK IPOPT
D2_REFUSE KEYSET {"block": 0, "expected": ["scenario1.aero_post.functionals.CD"], "extra": ["scenario1.aero_post.functionals.CD_final"], "found": ["scenario1.aero_post.functionals.CD_final"], "header": "Objectives", "missing": ["scenario1.aero_post.functionals.CD"], "where": "keyset_control"}
D2_G5_KEYSET_CONTROL OK refused=KEYSET
  rc=0

$ python3 d2_ab.py tagcheck  $SRC $WORK IPOPT
D2_REFUSE OPTIMIZER_TAG {"block": 0, "expected": "IPOPT", "found": "WRONGOPT", "where": "tag_control"}
D2_G5_TAG_CONTROL OK refused=OPTIMIZER_TAG
  rc=0

$ python3 d2_ab.py abtrivial $SRC $WORK IPOPT
D2_G5_AB_TRIVIAL OK {"AB2_bands": {"l2_rel": 0.1, "linf": 0.008}, "pass": true, "resolution_probe_REPORTED_ONLY": {"dshape_l2_rel": 0.10649653030290579, "dshape_linf": 0.010000000000000002, "fails_AB2_l2": true, "fails_AB2_linf": true, "seen": true, "shift": 0.01}, "self_comparison": {"AB1_dCD_abs": 0.0, "AB1_dCD_rel": 0.0, "AB2_dAoA_deg": 0.0, "AB2_dshape_l2_rel": 0.0, "AB2_dshape_linf": 0.0}, "self_comparison_all_zero": true, "trivial_baseline": {"dshape_l2_rel": 0.21299306060581158, "dshape_linf": 0.020000000000000004, "fails_AB2_l2": true, "fails_AB2_linf": true, "seen": true, "shift": 0.02}}
  rc=0

$ python3 d2_ab.py path $SRC IPOPT
D2_PATH_BLOCKS 13
D2_PATH_CL_VIOLATION {"at_block": 2, "first": 5.599999999827965e-07, "last": 1.900000000110147e-07, "max": 0.0026046399999999914, "n": 13}
D2_PATH_CL ["0.49999944", "0.49999601", "0.49739536", "0.49775456", "0.49855985", "0.49913954", "0.49826749", "0.49989143", "0.49998639", "0.49999762", "0.49999635", "0.49999981", "0.49999981"]
D2_PATH_CD ["0.02094392", "0.020896", "0.01959487", "0.01852187", "0.01789503", "0.01767693", "0.0175681", "0.01753983", "0.01752936", "0.01752809", "0.0175279", "0.0175279", "0.0175279"]
D2_SHAPE_L2 0.093899772805341328
  rc=0

SRC md5 AFTER   = 64bee1631d28ab07973e56ec7e1f4bf3
```

**What this dry run establishes, precisely and no wider:** the frozen reader can see a plant in
**the real file the real producer wrote**, on every channel the comparator consumes; it refuses a
blind reader; it refuses the exact key mismatch that blocked D1 arm C; it refuses a wrong optimizer
tag; the comparison returns **exactly zero** against itself and **sees a planted design difference
at its planted size**; and the path statistic reads arm O's real path. **It establishes nothing
about SLSQP, about the container, or about either optimum** — those are what the run is for.

### 5.2 Two things this dry run bought that were not free, and are the reason it ran before the freeze

1. **The A/B trivial baseline FAILED on its first draft, before the freeze, and moved a band.** The
   first draft of gate AB2 carried a band of `‖Δshape‖₂/‖shape_A‖₂ ≤ 25 %`. The trivial baseline —
   a planted `1e-2` displacement of one shape mode, which is **larger than `shape[6]`'s entire
   value of `8.2626e-03`** — measured **10.65 %** and therefore **passed** a band it should have
   failed. **A band that cannot be failed by a plainly different design is not a band.** AB2's band
   was tightened to **`≤ 10 %` and `‖Δshape‖_∞ ≤ 8.0e-03`** *before this freeze*, on that
   measurement, and the trivial shift raised to `2.0e-02` so the control fails both bands with
   margin (**21.30 %** and **2.0e-02**). **The `1e-2` probe is retained and reported as the
   comparison's measured resolution.**
2. **An independent cross-check of the path instrument, for nothing.** The comparator reads
   `max |CL − 0.5| = 2.6046e-03 at block 2` from the `debug_print` blocks. IPOPT's **own** `inf_pr`
   column, a completely separate instrument, reports its maximum primal infeasibility as
   **`2.60e-03` at major 2** (`../curriculum_D1/RESULTS.md` §4.3). **Two independent readers agree
   to the printed digits on the same event.** That agreement is registered as gate AB4's instrument
   check.

---

## 6. Gates — every one with its number

**Grading band (`DAFOAM_CHARTER.md` §2, `VERIFICATION_CHARTER.md` §7), applied PER COMPONENT:**
**PASS ≤ 5 % with zero flagged components; CONDITIONAL 5–15 % with the per-component breakdown
printed; GATE FAIL above 15 % or on ANY sign flip, whatever the aggregate.**

### 6.1 Per-arm gates — D1's, applied identically to arm A and arm B

**G-x1 — constraint satisfaction at the accepted design** (D1 G1, verbatim).
**`|CL − 0.500000| ≤ 1.0e-5`** at the accepted design, **AND** every geometric row inside its
registered bound: `thickcon ∈ [0.5 − 1e-6, 3.0 + 1e-6]` on all 20 rows, `volcon ≥ 1.0 − 1e-6`,
`rcon ≥ 0.8 − 1e-6`. **Any row outside → that arm's optimisation claim is `NOT A RESULT`.**
*Registered substitution, stated in advance:* IPOPT prints its own `Constraint violation....:` line
and arm A is additionally checked against it at `≤ 1.0e-5`; **SLSQP prints no equivalent line, so
for arm B that sub-condition is discharged by the comparator's own reading of `CL` and the 23
geometric rows at the accepted design.** The substitution is registered here, not improvised at
grading.

**G-x2 — termination** (`DAFOAM_CHARTER.md` §9, D1 G2's three rows).

| what the optimiser did | verdict |
|---|---|
| **arm A:** `EXIT: Optimal Solution Found.` with `Overall NLP error < tol 1e-5` — **arm B:** pyOptSparse `inform = 0` (SLSQP's converged code) | **gradeable** — PASS if G-x1 and G-x3 also hold |
| stopped at the frozen iteration cap (`max_iter 40` / `MAXIT 100`), or at the stage `timeout`, or at the **140.0 core-min** ceiling | **`GATE REACHED`** *iff* G-x1 holds at the last accepted design **and** G-x3 holds **and** the reduction against `CD_feasible` is ≥ the registered intermediate threshold of **2.0 %**; otherwise **`NOT A RESULT`** |
| any infeasible / restoration-failure / error exit, or **no inform code printed at all** | **`NOT A RESULT`** |

**Never `PASS`, and never described by the size of the improvement it reached.** The 2.0 %
intermediate threshold is D1's, registered before the run so that `GATE REACHED` cannot be chosen
after the number is seen.

**Two registered consequences, stated now rather than discovered later.** *(a)* **The exact wording
of pyOptSparse's SLSQP exit line has never been printed on this box.** The gate therefore keys on
the numeric **`inform`** code, not on a string; if no inform code is printed anywhere in arm B's log
or `opt_SLSQP.txt`, arm B is **`NOT A RESULT` about termination** and says so plainly. *(b)* **A
`timeout` stop on arm B kills the endpoint block**, so no endpoint JSON exists, so G-B3 cannot hold,
so the second row's `GATE REACHED` is unreachable that way: **arm B has, by construction, two
outcomes — converged-and-gradeable, or `NOT A RESULT`.** That is a consequence of §8.1's timeout
choice and is registered as one.

**G-x3 — endpoint FD spot-check at the design point that arm actually reached** (D1 G3, verbatim;
`DAFOAM_CHARTER.md` §9's mandatory final-point check). Four named components — `shape[6]` (the
LE combo mode, the defect's own component), `shape[1]`, `shape[5]`, `patchV[1]` (the only live DV
that does not cross `warpDeriv`). Steps are selected **inside the container, by the frozen D1
instrument, from that arm's own endpoint `|J_adj|` and the inherited `η` alone, before any FD value
exists**: ladder `{1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2}` for `shape` and `{1e-3, 3e-3, 1e-2, 3e-2,
1e-1}` for `patchV[1]`; `s_lo` = smallest rung with `C(s) = |J_adj|·2s/η ≥ 5` and above the floor;
`s_hi` = smallest rung with `s_hi ≥ 3·s_lo`; **the graded step is `s_hi` and is never selected on
agreement.** A component is GRADED only where `C ≥ 5` at the graded step **and** its two steps agree
within the plateau tolerance of **10 %**; otherwise it is **FLAGGED and excluded BY NAME** from any
aggregate. Verdict: `PASS` ≤ 5 % with zero flips; `CONDITIONAL` 5–15 %; **`GATE FAIL`** > 15 % **or
on any sign flip**.

**Registered and load-bearing: the two arms' graded steps are NOT forced equal.** Each arm's steps
come from its own endpoint gradient. **G-x3 is a per-arm gate and its numbers are never used as an
A/B statistic** — comparing two FD errors taken at two different steps at two different design
points would be a comparison of instruments, not of optimizers.

**G-x4 — trivial baseline, per arm** (`DAFOAM_CHARTER.md` §4). `shape[6]` at `step = 1e-8` on the
patched stack, run automatically by the frozen instrument. Registered prediction **> 50 %** (P15).
**If the wrong step also passes (≤ 5 %), that arm's G-x3 verdict is WITHDRAWN.** Why `1e-8` and not
one order off the registered step: one order off `3e-4` is `3e-3` and `3e-5`, and `3e-3` sits
**inside** A1's measured `1e-4 … 3e-2` plateau, so a step there is not a wrong step on this case.
A1's roundoff branch is severe by `1e-8` — **94.95 %** measured (`../A_stepsize_study.md`),
**132.75 %** on the patched stack (`../reverify_patched_idwarp_np1/RESULTS.md` §4.3) and
**112.6004 %, sign-flipped** at arm O's own endpoint (`../curriculum_D1/RESULTS.md` §6 G4).

### 6.2 The A/B comparison gates — registered before EITHER arm runs

**AB1 — objective agreement at the two optima.**
`Δrel := |CD_B − CD_A| / CD_A`. **Point `< 0.10 %`; band `≤ 1.0 %`.**
*Basis:* both arms stop at the same tolerance class (`tol 1e-5` / `ACC 1e-5`); IPOPT's own objective
column moved **1.86e-05 relative over its last two accepted majors and 1.7e-07 over the last one**
(`../curriculum_D1/RESULTS.md` §4.3), so the objective is settled well inside 1e-4 at that
criterion; and A4 §3.2 measured **two runs of the same optimizer reaching the same optimum to
1.8e-07**, with the largest path-dependence figure the lab holds at a deformed design point being
**0.183 %**. **The 1.0 % band is ≈ 5× that measured 0.183 %**, chosen so a genuinely different
optimum is distinguishable from run-to-run and tolerance noise.
**Above the band → the two optimizers did NOT find the same optimum. That is reported as an
optimizer-dependence finding, `AB2`'s and `AB4`'s attributions are re-read in that light, and it is
NOT reported as an aerodynamic finding.**

**AB2 — design-point agreement.** Two statistics, both frozen, both validated by the §5.1 trivial
baseline:
`‖shape_B − shape_A‖₂ / ‖shape_A‖₂` — **point ≤ 6.5 %, band ≤ 10.0 %**;
`‖shape_B − shape_A‖_∞` — **point ≤ 6.09e-03, band ≤ 8.0e-03**;
`|AoA_B − AoA_A|` — **point ≤ 0.05 deg, band ≤ 0.25 deg**.
*Basis:* IPOPT's **final accepted step norm `‖d‖ = 6.09e-03`** against the measured
`‖shape_A‖₂ = 9.3899772805341328e-02` is **6.486 %** — the scale at which IPOPT itself stopped
moving, so two solutions of the same NLP should agree at about that scale; the `‖·‖_∞` band of
`8.0e-03` sits just under **`shape[6] = 8.2626e-03`**, the smallest mode's entire value: *two
designs whose worst mode differs by as much as the smallest mode's whole value are not the same
design*. AoA travelled **5.153023 → 1.128636 deg** during arm O's optimisation (4.024 deg), so
0.25 deg is 6.2 % of that travel and 0.05 deg is 1.2 %.
**Validated, not asserted:** the §5.1 trivial baseline plants `2.0e-02` into one mode and measures
**21.30 %** and **2.0e-02** — failing both bands — and the `1.0e-02` resolution probe measures
**10.65 %** and **1.0e-02**, also failing both.

**AB3 — iteration and evaluation counts, and the instrument that reads them.**
This is the measurement the item is bought for, so **the gate is on the instrument, not on the size
of a difference.** **PASS** only if, for each arm: the evaluation count is read from **the same**
frozen channel in both arms (`d2_ab.py` `debug_print` block count), **and** it is cross-checked
against the optimizer's own reported count with the **registered offset `n_blocks = evals_reported
+ 1`**, measured on arm O (13 blocks against IPOPT's own 12). If an arm prints no count of its own,
the block count is primary **and the record says so**. **A disagreement other than the registered
offset makes the count comparison `NOT A RESULT`** — it is not reconciled after the fact.
Predictions: P2 (arm A majors), P5 (arm B iterations), P6 (arm B evaluations).

**AB4 — the constraint-violation path. THE REGISTERED HAZARD.**
`V_max := max over the whole function-evaluation path of |CL − 0.5|`, per arm, read by the **same**
frozen comparator from the **same** channel in each arm's own log.
**AB4 (gate, on the instrument): PASS** iff both paths are read in full, `V_max` is printed with the
block index at which it occurs **and the full `CL` path is printed beside it**, and — for arm A —
the comparator's `V_max` agrees with IPOPT's own `inf_pr` maximum to the printed digits, as
measured at this freeze on arm O (**2.6046e-03 vs 2.60e-03, both at index 2**). Otherwise
**GATE FAIL**.
**AB4-C (a real threshold): if `V_max` for either arm exceeds `1.0e-1`**, that arm's path is
recorded as having **left the design-relevant neighbourhood** and **no `CD` value from that path is
quoted anywhere in the record as a drag figure.** *Basis:* `|dCL/dAoA| = 1.345505e-01` per degree
(D1 §2.4), so `|ΔCL| = 0.1` is an AoA excursion of ≈ 0.74 deg on a design whose final AoA is
1.13 deg.
**AB4-H — the hazard clause, registered verbatim before either arm runs:**

> **A difference in the constraint-violation path between two optimizers is a statement about the
> two algorithms' handling of the constraint — interior versus active-set — and NOT about the flow.
> Neither arm's path excursion is reported as an aerodynamic, physical or design finding. An
> intermediate design that violates `CL = 0.5` is an infeasible probe of the optimiser's own path,
> and its `CD` is never quoted as a drag figure. Any sentence in `RESULTS.md` that would do
> otherwise is a GATE FAIL of AB4-H, and the sentence is removed, not annotated.**

*(The last clause is deliberate: a printed discrepancy labelled "diagnostic only" is worse than one
never computed.)*

**AB5 — the identity conditions. The reason arm A is bought.**
Arm A must reproduce D1 arm O. **Two thresholds, both frozen now:**

| # | quantity | **AB5-tight** (the prediction; a miss is reported as a miss) | **AB5-hard** (the gate) |
|---|---|---|---|
| 1 | `\|CD_feasible,A − 0.020943920630946831\| / …` | `≤ 1.0e-9` | **`> 1.0e-5` → NOT A RESULT** |
| 2 | `\|CD_A − 0.017527899854535338\| / …` | `≤ 1.0e-4` | **`> 1.0e-3` → NOT A RESULT** |
| 3 | `\|CL_A − 0.49999981209363359\|` | `≤ 1.0e-6` | **`> 1.0e-5` → NOT A RESULT** |
| 4 | `‖shape_A − shape_O‖_∞` | `≤ 1.0e-4` | **`> 1.0e-3` → NOT A RESULT** |
| 5 | `\|AoA_A − 1.128636497545056\|` deg | `≤ 1.0e-3` | **`> 1.0e-2` → NOT A RESULT** |
| 6 | major iterations | `= 11` | `∉ [9, 13]` → **NOT A RESULT** |

**Consequence of an AB5-hard breach: the staged case is not D1's case, and EVERY A/B figure in this
item is `NOT A RESULT`** — a difference between arms could then be the staging rather than the
optimizer, and the item does not get to choose which.
*Basis for the hard thresholds:* each is **one tenth of the corresponding A/B band** (AB1's 1.0 %,
AB2's 8.0e-03), so a reproducibility error at that level could never be mistaken for an optimizer
difference. Row 1 is tighter than the rest because `findFeasibleDesign` is **deterministic and
optimizer-independent** — it is the pure staging check, and it fires ~30 s into each arm, before
either optimiser has taken a step. *Basis for the tight thresholds:* A4 §3.2 measured two runs of
the same optimizer on the same case reaching the same optimum to **1.8e-07**, and A1's cold baseline
primal reconverges **bit-identically to 16 digits** (D1 `RESULTS.md` §3).

**AB6 — cost comparison, like-for-like: the measurement D1 could not make.**
`../curriculum_D1/RESULTS.md` §9.3 had to report contention as **"not separately measured"**,
because the A4 §6.1 work-marker method needs *the same work timed in two arms* and D1's arm C
produced no work. **This item has two arms doing the same primal on the same mesh on the same
image, so the method is available.** **PASS** iff `RESULTS.md` reports, from each arm's own
`ledger.txt` row and log: core-min per arm; **wall per function evaluation** for each arm (the
like-for-like work marker); core-min per iteration for each arm; and the cross-session marker
`|wall-per-eval_A − wall-per-eval_O| / wall-per-eval_O`, which is this item's **measured** estimate
of the contention/scheduling difference between D1's session and this one. **The gate is on the
instrument, not on the size**; a large contention term is a finding, not a failure.

### 6.3 Operational gates

**G6 — launch gate, re-run immediately before EACH of the two launches.**
**`free_cores ≥ 4` AND `MemAvailable ≥ 12 GiB`**, `free_cores := nproc − load1` (`/proc/loadavg`
field 1; `/proc/meminfo MemAvailable`). **The 12 GiB floor is the lab's standing floor: this item
neither touches it nor argues with it.** Run as its **own command** (`d2_preflight.sh`), output
appended to the run root's `preflight_history.txt` with a UTC stamp, and **its result read before
the launch command is issued** — never polled by a background process. If the gate is not open the
arm **waits and the gate is re-run**; it is not launched under a departure on this lane's authority.
Any departure must be directed in writing by the supervisor and recorded as a dated amendment
**before** the launch, never after.

**G7 — image identity.** `IDWARP_SO_MD5`, printed from inside the process that loaded the library,
must equal **`85f59e87253e0a71a813f64ca6e4c425`** for **both** arms. A mismatch **voids that arm**.
`nProcs : 1` asserted in every arm's log. **`--user 0:0`**, `id -u` prints `0`.

**G8 — cold start, verified BEFORE each launch, not after.** The run root did not exist before
staging (§11); each arm's staged tree contains **no `processor*` directory, no `reports/`, and no
numeric time directory other than `0/` itself**; `0/` is restored from `0.orig/` and its seven
fields are md5-equal to their `0.orig/` counterparts; and the staged tree's file listing is
**asserted identical to D1's own staged `base/`** (§13 step 1, dry-run at zero compute before this
freeze). **pyDAFoam writes the primal end
state back into the time-0 directory at run end, so a second run of a case directory silently
warm-starts** (`DAFOAM_CHARTER.md` §6) — **each arm runs in a freshly staged directory that has
never been run in**, and the staging sources are copied FROM and never run IN. Falsifier **F6** —
each arm's `D1_FEASIBLE_CD` reproducing arm O's to `1e-9` — is what proves it held.

**G9 — memory envelope** (`DAFOAM_CHARTER.md` §7). Predicted peak **1.70 GiB**, ceiling **2.5 GiB**
(P14). **Kernel cap `--memory=6g --memory-swap=6g`** — equal, so there is no swap escape — plus
**`--oom-score-adj=500`** and the per-stage `timeout`. **A container the kernel OOM-killed
(`.State.OOMKilled == true`, or exit 137) is recorded as stopped by memory and is `NOT A RESULT`
about anything else** — it is not re-labelled as a solver finding. Equally, **a failure with
headroom unused is not a memory finding either** (L-15), and the peak is reported beside the cap so
a reader can tell. *Note registered:* SLSQP stores a dense `n × n` Hessian approximation with
`n = 10`; it adds nothing measurable to the envelope, and this item does not claim to characterise
any memory boundary.

**G10 — cost ceiling. HARD ceiling 140.0 core-min = $0.11970 DERIVED.** An overrun **stops the
run**; it does not get a new budget (`CLAUDE.md` rule 12). §8.

---

## 7. Predictions — numeric bands, cited bases, every one scored HIT/MISS in `RESULTS.md`

| id | prediction | point | **band (HIT if inside)** | basis |
|---|---|---|---|---|
| **P1** | arm A termination class | `EXIT: Optimal Solution Found.` | present, with `Overall NLP error < 1e-5` | MEASURED: D1 arm O printed exactly this on the same file, image and task |
| **P2** | arm A major iterations | **11** | **[10, 12]** (AB5-tight row 6; AB5-hard is `[9, 13]`) | MEASURED: arm O took 11 |
| **P3** | arm A reproduction of arm O: `\|ΔCD\|/CD` | **< 1e-6** | **≤ 1.0e-4** | AB5; A4 §3.2's measured same-optimum reproduction to 1.8e-07 |
| **P4** | arm B termination: pyOptSparse `inform` | **0** (converged) | **`{0}`** | SLSQP is a mature Fortran SQP and this NLP is small (9 DVs, 24 rows) and smooth. **Registered risk: no SLSQP run has ever been made in this lab, on any case.** A non-zero inform is a **MISS**, reported as one, with G-B2 deciding the verdict |
| **P5** | arm B iterations | **20** | **[8, 60]** | **ESTIMATED-BY-ANALOGY, labelled.** IPOPT took 11 with `ls = 1` on every major. An active-set SQP on a problem with **4 active constraints at the optimum** (`volcon`, both `rcon`, one `thickcon` row — D1 §4.4) typically needs more iterations than a filter interior-point method, and must additionally identify the active set. **No SLSQP anchor exists on this box; the band's width is its honest content** — the same construction D1's P2 used, and D1's P2 band held while its point did not |
| **P6** | arm B function evaluations (comparator block count) | **30** | **[10, 120]** | P5 × (1 + ~0.5 line-search trials per iteration). IPOPT measured **13 blocks for 11 majors**, i.e. **1.18 evals/major with no backtracking at all**; SLSQP's L1 merit line search will backtrack sometimes, so evals/iteration > 1.18 is predicted |
| **P7** | **AB1**: `\|CD_B − CD_A\| / CD_A` | **< 0.10 %** | **≤ 1.0 %** | §6.2 AB1 |
| **P8** | **AB2**: `‖Δshape‖₂/‖shape_A‖₂`; `‖Δshape‖_∞`; `\|ΔAoA\|` | **≤ 6.5 %**; **≤ 6.09e-03**; **≤ 0.05 deg** | **≤ 10.0 %**; **≤ 8.0e-03**; **≤ 0.25 deg** | §6.2 AB2, validated by the §5.1 trivial baseline |
| **P9** | **AB4**: `V_max(A)` — arm A's `max \|CL − 0.5\|` along the path | **`2.6046e-03`** at block **2** | **[1.30e-03, 5.21e-03]** (0.5×–2×) | MEASURED at this freeze from arm O's own log (§5.1), corroborated by IPOPT's independent `inf_pr` column at `2.60e-03` |
| **P10** | **AB4**: `V_max(B) / V_max(A)` | **∈ [0.2, 5]** | **[0.2, 5]** | An active-set SQP drives toward the constraint boundary rather than approaching it from inside a barrier, so a *smaller* path excursion is as likely as a larger one — **the direction is deliberately NOT predicted**, and the band is symmetric in log space for that reason. AB4-C's `1.0e-1` remains the separate "left the neighbourhood" threshold |
| **P11** | arm B endpoint FD, four components, at the rule's own graded steps | **≤ 1.5 %** each | **every graded component ≤ 5.0 % AND zero sign flips** | arm O measured **≤ 0.2553 %** with **zero flips, 4 of 4 graded** at its own endpoint on this image; arm B's endpoint is a nearby design point on the same case and image |
| **P11b** | arm B's selected step pairs | `{1e-4, 3e-4}` for all three `shape` components; `{1e-3, 3e-3}` for `patchV[1]` | the same pairs | the ladder **floor** bound at arm O's endpoint on every component (clearances 283.1 / 195.3 / 397.1 / 114.8, all ≫ 5) and arm B's endpoint `\|J_adj\|` is expected within an order |
| **P12** | arm B core-min per iteration | **0.465** | **[0.35, 1.20]** | D1 MEASURED **0.42127 core-min/major** for IPOPT with **`ls = 1` on every major — no line-search primal was ever bought** (D1 §9.3). One extra warm primal costs **2.64 s** (arm O: 42.2 s for 16 FD primals), so one line-search trial per iteration gives 25.28 + 2.64 = **27.92 s = 0.465 core-min**. The band's floor is D1's own no-backtrack figure; its ceiling covers ≈ 3 extra trial primals per iteration |
| **P13** | total cost, actual core-min | **16.73** (incl. the 0.033 probe) | **≤ 33.43** (100 % contingency); **HARD ≤ 140.0** | §8 |
| **P14** | peak RSS, either arm | **1.70 GiB** | **≤ 2.5 GiB** | arm O MEASURED **1.6964 GiB** on the same image and problem. **Reported only if `getrusage` is reachable — `/usr/bin/time -v` was ABSENT in every D1 arm (`D1_USRBIN_TIME: absent`), so the in-process `getrusage` figure the frozen script prints is used; if neither exists, P14 is `NOT EVALUATED`, said plainly** |
| **P15** | trivial baseline, each arm, `shape[6]` @ `1e-8` | **> 50 %** | **> 50 %** (the gate) — reported band **[50 %, 10000 %]** | arm O measured **112.6004 %, sign-flipped**; the patched baseline precedent is **132.75 %**. Stated honestly: an FD estimate at `1e-8` is roundoff noise and its **value** is not expected to reproduce — only its magnitude class is predicted |

---

## 8. Cost (`CLAUDE.md` rule 12; `DAFOAM_CHARTER.md` §12)

`cost_basis: c7a.4xlarge at $0.0513/core-h — REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.` The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); **every dollar
figure here is DERIVED.** Core-minutes are **wall seconds × ranks ÷ 60**, billed as **cores × wall
for the whole clock** — the lab's DAFoam convention, because `docker run` holds its cpu allocation
whether the solver saturates it or not.

**Every line below is derived from a MEASURED D1 anchor, and the anchor is named.**

| stage | ranks | predicted wall | predicted core-min | measured anchor |
|---|---|---|---|---|
| phase-1 image probe (§3.1) — **already spent** | 1 | **2 s** | **0.033** | MEASURED in phase 1, rc 0 |
| zero-compute controls, staging, md5 asserts | — | — | **0.000** | no container is started |
| **arm A** — IPOPT, whole container | 1 | **361 s** | **6.017** | **MEASURED: D1 arm O, same image, same script, same task, same np, 361 s** (`../curriculum_D1/RESULTS.md` §2 row 3) |
| **arm B** — SLSQP, whole container | 1 | **641 s** | **10.683** | itemised below |
| **REGISTERED PRICE (point)** | | | **16.733** | **$0.014307 DERIVED** |
| with 100 % contingency | | | **33.466** | $0.028613 DERIVED |
| **HARD CEILING** | | | **140.0** | **$0.11970 DERIVED — an overrun STOPS the run** |

**Arm B, itemised — every row from an arm O measurement:**

| stage of arm B's container | predicted wall | measured anchor |
|---|---|---|
| container start, imports, mesh read, OpenMDAO/DAFoam problem build | **14 s** | D1 arm C reached exactly this point and died at **14 s** on the same image class |
| `findFeasibleDesign` (optimizer-independent) | **10 s** | arm O by subtraction: 361 − 278.04 driver − 54 endpoint − 14 start − 5 teardown ≈ **10 s**. **DERIVED by subtraction and labelled** |
| `run_driver()` — 20 iterations × 27.92 s | **558 s** | P12: D1's measured 25.28 s/major + one 2.64 s line-search primal |
| endpoint block: 1 adjoint + 16 FD primals + 2 trivial primals | **54 s** | arm O log elapsed: adjoint **8.58 s**, 16 FD primals **42.2 s**, trivial **3.50 s** |
| JSON write, `chown`, inspect, teardown | **5 s** | arm O's 361 s whole-arm against its 327.5 s internal clock |
| **TOTAL predicted wall** | **641 s** | |

**The curriculum's own estimate was ~140 core-min / $0.12; this lane re-derives 16.73 and discloses
the gap rather than adopting the number.** `EXPERTISE_CURRICULUM.md` §3 priced D2 as ≈ 2 × D1's
~70 core-min. **D1's own re-derivation was 23.0 and its measured actual was 7.000** (calibration row
**C-24**, ratio **0.304×**), so the curriculum's figure is ≈ 20× the best available anchor. **The
140.0 hard ceiling is kept unchanged at the curriculum's own registered figure** and is not this
lane's to move; it is the brief's ceiling, and the timeouts of §8.1 bind far earlier.

### 8.1 L-250 — `timeout` at the predicted envelope plus a stated margin, never at the budget's edge

*"A per-stage timeout cap is both the bound on a hang and the size of the loss."*

| stage | predicted wall | **registered `timeout`** | stated margin | loss bound if it hangs |
|---|---|---|---|---|
| **arm A** | 361 s | **900 s** | **2.49×** | **15.0 core-min** |
| **arm B** | 641 s | **2,700 s** | **4.21×** | **45.0 core-min** |
| **sum of caps** | | **3,600 s** | | **60.0 core-min — 43 % of the 140.0 ceiling** |

**The `timeout`, not the ceiling, is the binding instrument.** Arm B's 2,700 s cap covers P5's band
ceiling of **60 iterations** (60 × 27.92 s + 83 s of non-driver work = **1,758 s**) with **1.54×**
to spare, so **the timeout only bites outside the registered band** — which is exactly where it
should. At the predicted per-iteration cost it corresponds to **≈ 94 iterations**, so **the frozen
script's `MAXIT 100` is, by construction, unreachable, and the binding cap on arm B is the wall
clock** (§4.4, and G-B2's second registered consequence). **Both arms run foreground-or-polled
under their `timeout`; no unbounded process is started and no watcher script is used** (§9).

### 8.2 The calibration deliverable — Sanaa's standing directive, DRAFTED here and LANDED by the supervisor

Her directive, verbatim (2026-08-23, `CLAUDE.md` rule 12): *"for all teams involved once a process
is completed, the estimated costs must be compared with the actual incurred costs so we can improve
the lab's estimates."*

**This lane does not write `docs/COST_CALIBRATION.md`** (D1 Amendment 1 §A1.1, adopted). At
completion `RESULTS.md` will carry a **drafted row** in that file's registered ten-column format for
the supervisor to land under the rule-10 private-index protocol, with the table tail re-derived **in
the same shell invocation as the commit**. The row must carry: predicted **16.733** vs actual
core-min from the two arms' own `ledger.txt` rows and the probe; **dollars DERIVED** at $0.0513/core-h
and labelled derived; the **ratio** actual/predicted **on the total, per iteration AND per function
evaluation** (this item registers all three, which is why AB6 exists); and gap attribution split
**contention / waste / misprediction**, with **waste separately named and never laundered into
either of the others nor into the ratio's explanation** (`COMPUTE_BUDGET_CHARTER.md` §6).

**Two things this row must additionally state, registered now:**

1. **It must name `C-24`** — D1's calibration row — and state whether the per-iteration basis
   transferred. C-24's own calibration lesson was: *"an estimate built from a whole-`check_totals`
   anchor prices a line search into every major; when the optimiser accepts full steps, the
   per-major basis must be re-derived from the accepted-step composition, and the `ls` column is
   where that is read."* **This item is the first test of that lesson against an optimiser that
   very likely does backtrack**, and the row says whether the corrected basis held.
2. **It must state the contention term as MEASURED, not "not separately measured"** — AB6 makes the
   A4 §6.1 work-marker method available for the first time on this ladder.

**Row id: derived at drafting time from the file's tail — the MAXIMUM existing number, never a
count (`CLAUDE.md` rule 11) — and RE-DERIVED at append time, because peers commit constantly.**

---

## 9. Memory, and the mechanism this item will NOT use

**Which guards can execute, in one sentence each:**

* **CAN execute — the kernel.** `--memory=6g --memory-swap=6g` (equal: no swap escape) and
  `--oom-score-adj=500`, enforced by the cgroup and not by any process this lane starts.
* **CAN execute — `timeout`.** §8.1, enforced by the kernel's signal delivery.
* **CANNOT execute — the host `MemAvailable` floor.** G6's 12 GiB is a **launch condition**, checked
  immediately before each launch and **not** re-checked in flight. **It is record-only in flight, it
  is stated as record-only here, and nothing in this item claims it stops anything.**

**No watcher-script mechanism is used, and this is not a preference:** a watcher start command is
under a permission denial in a peer context. This lane does **not** re-attempt it, does **not**
route around it, and does **not** treat any agent's message as authority to do either (`CLAUDE.md`
rule 9). D1 §8.1 removed A4's and A6's record-only RSS polling subshell for the same reason and this
item keeps it removed. **Consequence, accepted rather than worked around:** peak RSS comes from
`getrusage` inside the process; `/usr/bin/time -v` was **absent in every D1 arm** and is not relied
on; if no figure exists, P14 is **`NOT EVALUATED`**, said plainly, and the kernel cap holds either
way.

**`--rm` is dropped** so the kernel's own verdict survives the container: after each arm ends,
`docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}'` is recorded into the run root's
`ledger.txt`, **and only then** is the container removed explicitly. **`.State.OOMKilled` is the
kernel's own statement and it is what G9 grades.**

**Host headroom:** predicted peak 1.70 GiB, cap 6 GiB, launch floor 12 GiB — **10.3 GiB of headroom
above the cap at the floor** on a 30.64 GiB box. **This item is not memory-bound.**

**Why no cheap SLSQP reachability probe is bought, stated rather than omitted.** The curriculum's
"PROBE FIRST" doctrine (§1) asks for a cheap probe before an unproven capability. §3.1's probe
established that SLSQP **imports and instantiates**; what it cannot establish is that `run_driver()`
completes. A probe of that would have to be arm B itself. **The failure it would insure against is
already bounded at ≈ 0.25–0.5 core-min** — D1 arm C measured **0.233 core-min** for a pre-solve
death on this image class — **so a probe would cost about as much as the failure it insures.** The
risk is therefore carried, named (falsifier **F11**), and its price is registered, not hidden.

---

## 10. Environment pinning (L-251) and staging discipline (L-252)

### 10.1 L-251 — uid and run-root mode, pinned in the same sentence

**Both containers run as `--user 0:0` (root — the uid every recorded A1 arm on
`dafoam-idwarp-rot:v1` ran under, D1 arms E and O included), and in the same breath the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/` is created mode `0777` (`mkdir -p`
immediately followed by `chmod 0777`, asserted with `stat -c '%a'` inside `d2_run_arm.sh` before
every launch), so that OpenMDAO's `reports/` and `mphys.html` writes cannot hit the
`PermissionError` that killed W4 M2 attempt 1 before its primal and burned 20.00 core-min under
L-250.**

Asserted from inside each container: `id -u` prints **`0`**. After each arm, `sudo -n chown -R
ubuntu:ubuntu` over the log and the arm directory so the host-side grading reads work.

### 10.2 L-252 — per-invocation unique names, `test -s`, provenance assert

*"In shared temp, a generic filename IS an accidental handoff."*

* **Every generated file carries a per-invocation stamp** `STAMP := $(date -u +%Y%m%dT%H%M%SZ)_$$` —
  the logs (`armA_${STAMP}.log`, `armB_${STAMP}.log`), the container names (`d2_armA_${STAMP}`,
  `d2_armB_${STAMP}`), the endpoint outputs (`endpoint_${STAMP}.json`). **No generic filename is
  written or read anywhere in the chain.**
* **Every producing step writes `<file>.ok.${STAMP}` on its own success, and every consuming step
  asserts `test -s <file> && test -f <file>.ok.${STAMP}` before reading, hashing or comparing it.**
  A file that exists but carries no sentinel from **this** invocation is a stale artifact and the
  chain **stops**. *(D1 §17 disclosed that its endpoint JSON carried no such sentinel; this item
  does not inherit that gap — the sentinel assertion is a launch-sequence step in §13.)*
* **`test -s` on every staged file before it is used**, and the five staging md5s re-asserted on the
  staged copies, with the two script md5s re-asserted again inside `d2_run_arm.sh` before **every**
  launch.
* **Explicit `&&` chaining throughout; `set -e` is not relied on** — it did not stop the chain that
  earned L-252.
* **The scratchpad is temp only and is never a handoff channel** (`CLAUDE.md` rule 13, L-186).
  **This document cites no scratch path**, and the run root — not the scratchpad — carries every
  artifact `RESULTS.md` will cite.

---

## 11. Run root

**`/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/`** — registered here as this item's
only run root. **Verified NOT to exist at the moment this pre-registration is frozen**: the check
`test ! -e /home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab` is executed **inside the
same shell invocation that writes this file's commit**, and the commit does not land if it fails.
That is `CLAUDE.md` rule 2's condition made checkable — *name the run directory that does not exist*
— and it is the evidence that no compute preceded this freeze.

Artifacts it will hold: `ledger.txt`, `preflight_history.txt`, `armA_${STAMP}.log`,
`armB_${STAMP}.log` with their `.ok.${STAMP}` sentinels, `armA/endpoint_${STAMP}.json`,
`armB/endpoint_${STAMP}.json`, `armA/opt_IPOPT.txt`, `armB/opt_SLSQP.txt`, the md5-verified copies
of the five frozen instruments, the `ab_report_${STAMP}.json` the comparator writes, and the two
staged case copies. **`RESULTS.md` cites these paths; this repository document cites no scratch
path** (rule 13).

---

## 12. What this item will NOT touch, listed by name

Nothing below is run, staged, queued, costed, edited or prepared by this item.

* **`../curriculum_D1/`'s frozen files** — `PREREGISTRATION.md` (and Amendments 1–2, Addenda §16 and
  §17) and `RESULTS.md`. **Read only. Zero frozen files edited.**
* **D1's run root** `/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/` — **read only,
  md5-asserted before and after every read.** No file is created, moved or deleted there. The two
  instruments this item uses are **copies**, taken into this repository directory and frozen by md5;
  the originals are untouched.
* **`../curriculum_D1_Cprime/`** — the sibling mini-item, `PENDING`. **This item does not touch it,
  does not depend on it, does not block it, and does not pre-empt its shipped-row verdict.** Both
  items read D1 arm O's artifacts read-only and write to disjoint run roots.
* **`../../A4/curriculum_D3/`** — a sibling lane is freezing curriculum item D3 concurrently.
  **No file is shared between the two items**, and this lane writes nothing outside
  `cases/dafoam/ladder-a/A1/curriculum_D2/`.
* **The SHIPPED toolchain row and D1 §3.3's deliverable** — not entered (§3). The shipped-image
  **optimisation twin**, priced at 19.8 core-min, **stays deferred; it is not run, not re-priced and
  not re-argued here.**
* **Anything N=29-gated.** A6 N=29 and the **D464** two-reading gate. **The gate is Sanaa's; it
  stays parked**, and no ratification of any curriculum grants her D464 reading.
* **Tier 6** (D16a CRM full-size, D16b MPhys/TACS, D16c GPU) — **NEEDS COSTING + Sanaa's explicit
  per-item approval**; **GPU spend is OUTSIDE the 2026-08-21 blanket**. Not touched, not costed.
* **The peer session's claimed items** under the `docs/LAB_STATE.md ## dafoam` claim ledger — the
  ADF sweep (GAMG→PBiCGStab / `useMeanStates`), the B3 RSS item, the A3 rung-1 / rung-3 items. Not
  entered.
* **O3** — **BLOCKED for Sanaa.** Not touched.
* **The five upstream DAFoam defect drafts** — all **NOT FILED**, and this item files nothing.
* **`DAFOAM_CHARTER.md` §13's PROPOSAL** — unratified. **Not enforced** (§9 registers the underlying
  facts on their own merits, not as compliance with an unratified clause).
* **The `MemAvailable ≥ 12 GiB` standing floor** — neither touched nor argued (§6.3 G6).
* **`docs/COST_CALIBRATION.md`, `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md`,
  `docs/LAB_STATE.md`, `CLAUDE.md`, any charter** — **this lane drafts rows and appends none of
  them.**

---

## 13. The exact launch sequence a phase-2 lane runs

**Nothing below is executed by the invocation that commits this file.** It is registered so the
phase-2 lane executes a frozen sequence rather than an improvised one. **Launch authorisation comes
in writing from the supervisor, after its own freeze verification.**

```
# 0. FREEZE VERIFICATION (the supervisor's, before anything below)
#    git show <this commit>:cases/dafoam/ladder-a/A1/curriculum_D2/PREREGISTRATION.md | md5sum
#    and the five instrument md5s of section 4.1, against the committed blobs.

# 1. STAGE  (host, zero compute)
D2=/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab
REPO=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_D2
test ! -e $D2 && mkdir -p $D2 && chmod 0777 $D2 && test "$(stat -c '%a' $D2)" = "777"
cp -a /home/ubuntu/certonomous-runs/W5-regrade/a1_unpatched $D2/base
rm -rf $D2/base/processor* $D2/base/reports $D2/base/mphys.html $D2/base/dRdWColoring_*.bin*
rm -rf $D2/base/0 && cp -a $D2/base/0.orig $D2/base/0             # G8
#    ASSERT the staged tree IS D1's staged tree -- this diff must be EMPTY:
diff <(cd $D2/base && find . | sort) \
     <(cd /home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/base && find . | sort)
cp -p $REPO/d1_opt_runScript.py $REPO/d1_fd_endpoint.py $REPO/d2_ab.py \
      $REPO/d2_run_arm.sh $REPO/d2_preflight.sh $D2/
#    ASSERT all five md5s of section 4.1 and the three staging md5s of section 1.2, on the STAGED
#    copies, with `md5sum -c -`.  A mismatch STOPS; it is not repaired.
#    (This whole block was DRY-RUN in scratch at zero compute before this freeze: the tree-listing
#     diff came back EMPTY against D1's own base/, the three md5s matched, all seven 0/ fields were
#     md5-equal to their 0.orig/ counterparts, and the G8 conditions held.  L-266 was earned by a
#     rule that was never dry-run on its own ladder.)

# 2. ZERO-COMPUTE CONTROLS, re-run against the real arm O log, into the RUN ROOT
ARMO=/home/ubuntu/certonomous-runs/CURRICULUM-D1-a1-constrained-opt/armO_20260824T160553Z_1400030.log
cd $D2 && for c in selftest plantcheck negcheck keycheck tagcheck abtrivial; do
  case $c in selftest) python3 d2_ab.py selftest ;;
    plantcheck) python3 d2_ab.py plantcheck $ARMO $D2/controls IPOPT 64bee1631d28ab07973e56ec7e1f4bf3 ;;
    *) python3 d2_ab.py $c $ARMO $D2/controls IPOPT ;; esac || exit 2
done                                   # ANY non-zero exit STOPS the item (gate G5, falsifier F3)
md5sum $ARMO                           # must still read 64bee1631d28ab07973e56ec7e1f4bf3

# 3. ARM A  (IPOPT).  Gate as its OWN command, READ before the launch is issued.
./d2_preflight.sh armA || { echo "G6 NOT OPEN - wait and re-run; do NOT launch"; exit 3; }
export D1_ETA=1.957349804806996e-08
export D1_ENDPOINT_JSON=endpoint_$(date -u +%Y%m%dT%H%M%SZ)_$$.json
./d2_run_arm.sh armA dafoam-idwarp-rot:v1 d1_opt IPOPT 900

# 4. AB5-HARD, checked BEFORE arm B is launched.  If it fails, arm B is NOT launched:
#    a comparison against a staging that is not D1's staging is not worth 10.7 core-min.
#    Read D1_FEASIBLE_CD, D1_ENDPOINT_PATCHED_CD/_CL/_SHAPE/_PATCHV from armA's log and check
#    the six AB5-hard rows of section 6.2.

# 5. ARM B  (SLSQP).  Gate re-run as its OWN command.
./d2_preflight.sh armB || { echo "G6 NOT OPEN - wait and re-run; do NOT launch"; exit 3; }
export D1_ENDPOINT_JSON=endpoint_$(date -u +%Y%m%dT%H%M%SZ)_$$.json
./d2_run_arm.sh armB dafoam-idwarp-rot:v1 d1_opt SLSQP 2700

# 6. GRADE  (host, zero compute).  Both logs through the SAME frozen comparator, with the
#    per-arm optimizer tag asserted, into ab_report_${STAMP}.json.
```

**Between every step:** `test -s <file> && test -f <file>.ok.${STAMP}` on every produced artifact
before it is read (L-252). **Every stamp is `date -u` read in the invocation that writes it**
(Amendment 1 §A1.2). **Neither arm is relaunched after a failure without the supervisor's written
direction**: a crash is a finding until triage says otherwise (`SUPERVISION_CHARTER.md` §3), and
D1 arm C's `BLOCKED` is the precedent for not routing around one.

---

## 14. Falsifiers — registered before the run, each with its consequence

| id | falsifier | consequence |
|---|---|---|
| **F1** | an arm's printed `IDWARP_SO_MD5` ≠ `85f59e87253e0a71a813f64ca6e4c425` | **that arm is VOID**; no figure from it is reported |
| **F2** | **AB5-hard breached by arm A** (§6.2) | the staged case is not D1's case — **EVERY A/B figure in this item is `NOT A RESULT`**, and arm B is not launched |
| **F3** | the planted-zero control cannot see its plant on any consumed channel | **exit 2**; **no figure computed from a log is reported anywhere** |
| **F4** | the optimizer tag in a consumed log ≠ that arm's registered optimizer | comparator **refuses** (`OPTIMIZER_TAG`) — the comparison may not silently compare an arm with itself |
| **F5** | an arm's block count and its optimizer's own reported evaluation count disagree by other than the registered offset (`+1`) | the **count comparison is `NOT A RESULT`**; it is not reconciled after the fact |
| **F6** | an arm's `D1_FEASIBLE_CD` ≠ `0.020943920630946831` to `1e-9` relative | the staging or the cold start is wrong — **stop; nothing else in that arm means anything** (this single assertion proves cold start, mesh identity and setup identity at once, and it fires ≈ 30 s in, before either optimiser has taken a step) |
| **F7** | an arm's accepted design violates G-x1 | **that arm's optimisation claim is `NOT A RESULT`** |
| **F8** | any endpoint component shows a **sign flip** | that arm's **G-x3 is `GATE FAIL`** and its design is not validated, regardless of the aggregate |
| **F9** | the trivial baseline at `1e-8` returns **≤ 5 %** | that arm's **G-x3 verdict is WITHDRAWN** — the instrument cannot fail (`DAFOAM_CHARTER.md` §4) |
| **F10** | the **A/B** trivial baseline (a planted `2.0e-02` design difference) is not seen at its planted size, or does not fail AB2's bands | **the comparison instrument cannot fail and EVERY A/B figure is WITHDRAWN** |
| **F11** | arm B errors out before or inside `run_driver()` — SLSQP rejects the equality form, the 24-row constraint set, or the driver configuration | arm B is **`BLOCKED`**, not `GATE FAIL` — no gate was reached. **The crash is triaged as a finding, not repaired in place** (§4.1's no-edit condition governs). The A/B is `NOT DELIVERED`; arm A's AB5 reproduction verdict stands alone. **Bounded at ≈ 0.25–0.5 core-min** (§9) |
| **F12** | any sentence in `RESULTS.md` reads a path excursion as an aerodynamic or physical finding | **AB4-H is `GATE FAIL`**; the sentence is removed, not annotated |

---

## 15. What this item owes on completion

Discharged at completion and **not before**:

1. **`RESULTS.md`** in this directory — every prediction **P1–P15 scored HIT/MISS**, MISSes reported
   as MISSes; **the per-arm tables printed in full and never folded into an aggregate**; every gate
   `G-A1…G-B4`, `AB1…AB6`, `G6…G10` with its verdict from the fixed vocabulary; falsifiers F1–F12
   scored; the §8.2 cost comparison; and the ledger.
2. **A drafted `docs/COST_CALIBRATION.md` row** in that file's ten-column format, naming **C-24**
   and stating whether its per-major calibration lesson transferred, with the id **re-derived at
   append time from the maximum** — **drafted by this lane, landed by the supervisor.**
3. **A drafted `../../LADDER_A_STATUS.md` row** for the D2 A/B, **drafted, not appended.**
4. **A drafted execution-state ledger row** for `EXPERTISE_CURRICULUM.md` §7 — **drafted, not
   appended** — which must record, in the state cell, that the *trust-region* half of the D2 row was
   **NOT DELIVERED** and why (§0, §3.1).
5. **Drafted `L-` / `N-D` / `D` rows** for the supervisor's append (`DAFOAM_CHARTER.md` §11) —
   including the **capability fact** that `ParOpt` ships as a package directory in
   `dafoam-idwarp-rot:v1` and **does not import**. **Numbers re-derived at commit time, in the same
   shell invocation, from the tail — the MAXIMUM existing number, never a count** (`CLAUDE.md`
   rule 11).
6. **Lab-wide propagation** of anything the whole lab must know — routed **through the chief** for
   `CLAUDE.md` or charter-level changes, **never edited by this lane.**

---

## 16. Verdict vocabulary

**`PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`.** No other word grades
anything in this item, and no adjective softens one. A verdict is valid only against a gate or
falsifier registered above, **before** the run. **Arm A and arm B are reported as two separate rows
and are never merged into a single "the optimisation" verdict.** **Shipped- and patched-toolchain
verdicts remain two rows (R11); this item produces patched-row verdicts only and none of them stands
in for a shipped row.** **An optimiser stopped by a wall clock, an iteration cap or a budget is
`GATE REACHED` or `NOT A RESULT`, never `PASS`, and is never described by the size of the
improvement it reached** (`DAFOAM_CHARTER.md` §9).

---

## 17. Launch-gate reading at the moment of this freeze

**Recorded because it is data, not authorisation. It is a snapshot; G6 is re-run as its own command
immediately before each of the two launches and its reading at that moment is what governs.**

| quantity | reading, **2026-08-24T17:48:27Z** | gate | status |
|---|---|---|---|
| `nproc` | **16** | — | — |
| 1-minute load average | **3.69** | — | — |
| **free_cores** = `nproc − load1` | **12.31** | **≥ 4** | **OPEN** |
| **MemAvailable** | **28703104 kB = 27.37 GiB** | **≥ 12 GiB** | **OPEN** |
| `MemTotal` | 32132604 kB = 30.64 GiB | — | — |

**NO LAUNCH IS AUTHORISED BY THIS READING**, and it confers no authority on any later moment: the
box is shared, peers commit and launch constantly, and G6 is re-run immediately before each launch.
**Contention is attributed at grading, never absorbed into the ratio** (§8.2).

---

**END OF PRE-REGISTRATION. Frozen by commit. Nothing below this line existed when the gates,
thresholds, caps, bands and labels above were fixed. NOT FILED ANYWHERE.**
