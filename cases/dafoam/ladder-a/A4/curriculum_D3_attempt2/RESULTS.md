# Curriculum item D3 — A4 Ahmed body, CONSTRAINED drag minimisation: RESULTS, **ATTEMPT 2**

**Item verdict: `BLOCKED`.**

**Graded against** `cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/PREREGISTRATION.md`, frozen at
**`092e54e7`** (v1.0) with the supervisor launch authorisation appended as **ADDENDUM A1 at
`60d699fe`** (v1.1) **before any container of this attempt started**. Every gate, band, threshold, cap
and label cited below is that frozen file's, unchanged.

**Author:** dafoam `lab-lane` (Opus), dispatched by dafoam-supervisor. **PHASE 2.**
**Nothing is filed, sent, uploaded, posted or pushed anywhere** (`CLAUDE.md` rule 7). SUBMISSIONS
PARKED.

---

## HEADLINE — the repair worked, and Stage G found the *next* defect for 2.87 core-min

**The two-line repair did exactly what §2.1 said it would.** Attempt 1's
`KeyError: 'Need to add surface "default"'` **does not appear anywhere in this run's 492-line
`geom.log`** (grep count **0**). `prob.setup(mode="rev")` completed, both DVCon calls returned, and the
process ran on past `om.n2` and `OptFuncs` into the `geom_probe` task block — code no run of this item
had ever reached.

**And there it died, at the first line of that block.** `runScript.py:261` → `:253`
`pts = dvg.update("aero")` → pyGeo `DVGeo.py:2012` → `pyBlock.py:745` →
**`KeyError: 'aero'`**. No point set named `"aero"` is embedded in the FFD, so the probe's own
`probe_surface()` cannot ask the FFD for its updated points.

**That is falsifier class `F1c`, decided mechanically and not by narrative.** The pre-registration's
G11(d) crash-frame rule fixes the class by the **final producer frame's line number**: at or above 214
is the common setup path, at or below 248 is the stage's own task block. The final producer frame is
**line 261**. **`F1c` — DOWNSTREAM-PRODUCER class**, which §2.3(1) registered as *possible and
unproven* before this run. **`P15` MISS.**

**The item is `BLOCKED`** (§18: *"a Stage-G crash of any class makes the item `BLOCKED`"*). Stages η,
O and T were **not launched**; nothing further was spent. **Spend 2.8667 core-min of the 69.2 HARD
ceiling; 66.3333 core-min remain unspent and are not carried anywhere.**

**The one thing this run bought that a cheaper instrument could not:** attempt 2's own §2.2 probe
proved the repair through `prob.setup` for 0.1833 core-min and **stopped there, by construction** —
and the defect that stopped this run sits **47 lines past** where the probe stopped. §2.3(1) said in
terms that the probe advanced the frontier *"to the end of `prob.setup(mode="rev")` and no further"*
and that a failure beyond it *"is a new defect"*. **It was.**

---

## 1. Toolchain — two rows (`DAFOAM_CHARTER.md` §6; `PREREGISTRATION.md` §5)

The two rows are **never merged into one verdict** (§18).

| row | image | `libidwarp.so` md5 | how the hash was read | stages executed | verdict |
|---|---|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | **`85f59e87253e0a71a813f64ca6e4c425`** | **LIVE, from inside the process that loaded the library** — `geom.log:4`, printed by the launcher's in-process `hashlib.md5(open(so,"rb").read())` before `mpirun` was reached | **Stage G only** (η, O, T-patched not launched) | **G7 `PASS`**; the row's own item verdict is `BLOCKED` |
| **SHIPPED** | `dafoam/opt-packages:latest` | `f0fcb488e0e98156575cd19548e91663` | **inherited from the A4 record; NOT re-read on this run** | **none** — Stage T-shipped not launched | **`PENDING`** |

`nProcs : 1` asserted present in `geom.log` (G7's second limb). **np = 1 is required, not chosen**
(§13 item 5).

---

## 2. Stages as executed, with costs

| stage | task | image | launched? | rc | wall s | ranks | **core-min** | ceiling | over? | `timeout` | fired? | peak RSS | OOM | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **G** | `geom_probe` | patched | **YES** | **1** | **172** | 1 | **2.8667** | 3.0 | **no** | 180 s | **no** | **0.5973 GiB** | **no** (rc 1, not 137) | **`BLOCKED`** |
| **η** | `eta` | patched | **no** | — | — | — | **0.0** | 6.0 | — | 360 s | — | — | — | **`PENDING`** |
| **O** | `run_driver` | patched | **no** | — | — | — | **0.0** | 42.0 | — | 1900 s | — | — | — | **`PENDING`** |
| **T-patched** | `endpoint_at` | patched | **no** | — | — | — | **0.0** | 12.0 | — | 420 s | — | — | — | **`PENDING`** |
| **T-shipped** | `endpoint_at` | shipped | **no** | — | — | — | **0.0** | 12.0 | — | 420 s | — | — | — | **`PENDING`** |
| **TOTAL** | | | | | **172** | | **2.8667** | **63.0 / HARD 69.2** | **no** | | | | | **`BLOCKED`** |

Ledger of record: `/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/ledger.txt` (one row).
RSS samples: `.../rss_geom.txt` (28 samples at 5–8 s spacing, 18:31:07Z → 18:33:52Z).

**Peak RSS — a defect in the run-root launcher, recorded and NOT fixed.** The ledger row's cell reads
`peak_rss_GiB=11`. **That figure is wrong.** It is a misparse: the launcher's
`awk|sed|bc|sort -g` chain mishandles the sampler's `MemUsage` strings, and `sort -g` then ranks the
malformed tokens lexically. **The correct peak, recomputed directly from `rss_geom.txt`, is
`611.6 MiB` = `0.5973 GiB`** — against the G9 predicted peak 1.4 GiB, the G9 ceiling 2.5 GiB and the
kernel cap 6 GiB. The launcher is **not** a frozen file, but it is not repaired here either: the run is
over and an in-place edit would leave the ledger row and the script disagreeing with no record of why.
**Flagged to the supervisor; the correct number is this paragraph's, not the ledger cell's.**

**`docker inspect` — cannot be run, and the pre-registration is why.** §11 registers **`--rm`**, so the
container is destroyed on exit and no `docker inspect` exit-code / `OOMKilled` read is possible after
the fact. §8 G9 registers the substitute in terms: *"a container the kernel OOM-killed (exit 137)"* —
**the exit code is taken from the launcher's own `wait` on the `docker run` pid: `rc = 1`.** Not 137,
not 124. **This is a disclosed limitation of the frozen invocation, not an omission of this report.**

### 2.1 Staging, and the assertions the pre-registration required (§11, §12, G8, G11 a/b)

Staged from `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base` into
`/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/`, five stage directories.

| assertion | reading |
|---|---|
| run root **ABSENT** before staging (`test ! -e`) | **held** — refused otherwise |
| run root created `chmod 0777` before the first container (L-251) | **held**; no `PermissionError`, `reports/` written by the container as root and `chown`ed back |
| container uid | image default (root, `mpirun --allow-run-as-root`), **no `-u` flag** (L-251) |
| L-252 unique suffix | `1787596244_1548197`, written to each stage's `.d3_uniq` and read back |
| staging source STL md5 | **`ec3abd312d3e3e9d15340b95365ff62f`** = §11's registered value |
| mesh | **2,777 cells** (`geom/log.checkMesh`) — inherited byte-for-byte, **not regenerated, refined or re-decomposed** |
| **G8 cold start**, per stage, before launch | no `processor*`; no numeric time dir but `0`; `0/` restored from `0.orig/`; no `reports/` carried over — **all five stages** |
| **G11 limb (b)** staged md5, asserted **after the copy** and **again immediately before the launch** | **`4dd289f275b512598e74daf2eb39d729`** in all five stage directories = the frozen value |

**G11 limb (a) — the seven static readings of §8 G11(a), re-derived from the STAGED file, all five
copies, and identical in every one:**

| reading | registered §8 | measured on the staged file |
|---|---|---|
| `class Top(` at line | 132 | **132** |
| `prob = om.Problem()` at line / occurrences | 190 / 1 | **190 / 1** |
| `prob.setup(mode="rev")` at line | 214 | **214** |
| first `if args.task ==` at line | 248 | **248** |
| setup precedes the task branch | True | **True** |
| `def configure(self)` definitions | 1 | **1** |
| occurrences of `args.task` inside `class Top` | 0 | **0** |
| executable `self.geometry.nom_setConstraintSurface` calls | 1 | **1** |

**Freeze re-verified inside the launch invocation** (`CLAUDE.md` rule 2): all three frozen executables
hashed on disk against the **committed blobs at `092e54e7`** and equal
(`d3_runScript.py 4dd289f2…`, `d3_grade.py a32f0758…`, `d3_sep_monitor.py cd07d7b8…`), and the latter
two additionally `cmp`-identical to the attempt-1 **`0cbf463c`** blobs. **The frozen file is the file
that ran.**

### 2.2 G6 — the launch gate, as its own command, read before the launch

Run as its **own** command, stamped into
`/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/preflight_history.txt`, and **read before**
the launch command was issued — never polled, never inferred.

| when | reading | gate |
|---|---|---|
| `2026-08-24T18:30:51Z`, before Stage G | `nproc=16 load1=3.29 free_cores=12.71` (floor 4) · `memavail_GiB=27.24` (floor 12) | **`OPEN`**, exit 0 |

**One G6 reading exists because one stage launched.** The gate opened on the **first** reading, so
**zero core-minutes were spent waiting.**

---

## 3. THE FINDING — the repair cleared attempt 1's defect and the frontier moved 47 lines

### 3.1 What the run actually did, quoted from its own log by path and line

Artifact: `/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/geom.log`, 492 lines.

**What is ABSENT is the first finding.** `grep -c 'Need to add surface'` over that file returns **0**.
Attempt 1's raise — `KeyError: 'Need to add surface "default" to the DVConstraints object'` at its
`geom.log:491` — **did not happen.** Both DVCon calls (`nom_addThicknessConstraints2D` at producer
`:173`, `nom_addVolumeConstraint` at `:175`) returned, and execution continued past
`prob.setup(mode="rev")` at `:214`.

**What is present is the second finding.** `geom.log:472-481`:

```
  File "/mnt/geom/runScript.py", line 261, in <module>      base = probe_surface()
  File "/mnt/geom/runScript.py", line 253, in probe_surface pts = dvg.update("aero")
  File ".../pygeo/parameterization/DVGeo.py", line 2012, in update
        Xfinal = self.FFD.getAttachedPoints(ptSetName)
  File ".../pygeo/pyBlock.py", line 745, in getAttachedPoints
        u = self.embeddedVolumes[ptSetName].u
KeyError: 'aero'
```

`d3_summary.json` was **never written** (`geom/d3_summary.json` does not exist), so none of the eight
`G_*` keys exists and **no graded quantity of Stage G was produced**.

### 3.2 The falsifier class, decided by the registered rule and not by the fact that a crash happened

**§8 G11(d) is the decider, and §17.1's F1c row repeats it:** the class follows the **final producer
frame's line number**. Final producer frame: **`runScript.py:261`**. **261 ≥ 248** ⇒ inside the
`geom_probe` task block ⇒ **`F1c` — DOWNSTREAM-PRODUCER class**.

- **`F1a` (missing-prerequisite): NOT FIRED.** Its own evidence is absent — no unregistered-surface
  raise, and the frames are not in a registrar entered from `configure()`.
- **`F1b` (transferability): NOT FIRED.** Nothing here says anything about whether the JBC_Hull/D1-C′
  constraint recipe transfers to a 3×2×2 FFD on a blunt body. The DVCon calls returned; the
  crash is in the probe's own code, downstream of them.
- **`F1c`: FIRED.** Stage G **`BLOCKED`**; **P15 MISS**.

**One honest tension, disclosed rather than resolved on this lane's authority.** The raise is textually
a `KeyError` about an **unregistered object** (`'aero'` absent from `embeddedVolumes`), which matches
the *content* limb of **F1a**'s decision rule as written. The *location* rule — G11(d), which §8 states
**"is what decides falsifier class F1c versus F1a/F1b"** — gives **F1c** unambiguously. **The location
rule governs, and F1c is the recorded class**; the dafoam-supervisor read `geom.log` personally and
ruled F1c on the same ground. **The overlap between F1a's content limb and F1c's location limb is a
real defect in the frozen taxonomy** and is a record candidate (§9.3), not a re-grading of this run.

**This lane proposes no repair and drafts no attempt 3.** §6.3 governs: the stage is `BLOCKED`, the
crash is a **finding** until triage says otherwise, **no frozen file is edited**, and any
re-registration is a `VERIFICATION_CHARTER.md` §2d.1 four-condition decision **for the supervisor** in
a new mini-item directory.

### 3.3 What §2.2's probe could not have caught, measured rather than argued

§2.3(1) registered the limitation in advance. It is now measured:

| | §2.2's probe | this Stage G |
|---|---|---|
| stops at | `prob.setup(mode="rev")` — producer line **214** equivalent | crashed at producer line **261** |
| `om.n2` (producer `:215`) exercised | **no** — the probe's source ends at the `setup` try/except | **yes**, `geom/mphys.html` written, 982,171 bytes |
| `OptFuncs` (producer `:217`) exercised | **no** | **yes** |
| `geom_probe` block (`:249-299`) exercised | **no** | **entered; died on its first statement** |
| cost | 0.1833 core-min | 2.8667 core-min |

**The lesson is one level down from L-273's.** §16.3 already said the key-set control parses *names*
and the selftest plants *values*, and that neither can see a **missing API call** — so the item
registered a no-flow container as the cheapest instrument that can. **What this run adds:** a no-flow
container that stops at `setup` is **also** not that instrument for anything past `setup`. The probe
was priced and read as evidence about the producer, and it was only ever evidence about **the first 214
of its 371 lines.** That is §9.1's record candidate.

---

## 4. Gates — every one, with its verdict word from the fixed vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and no synonyms.

| gate | verdict | reading |
|---|---|---|
| **Gη** noise floor | **`PENDING`** | Stage η **not launched**. δ_repeat **not measured**; the η plant **not seen**; no `eta_call1_CD`. Not `GATE FAIL`, not `BLOCKED` on its own account — **not yet run** (§18: `PENDING` is only for "not yet run") |
| **G1** constraint satisfaction | **`PENDING`** | Stage O not launched; no `opt_IPOPT.txt`, no `final_thickcon_slant`/`final_volcon_aft` |
| **G2** termination | **`PENDING`** | no IPOPT run |
| **G3** endpoint FD per component | **`PENDING`** | no `check_totals` block was produced by any stage of this attempt |
| **G4** trivial baseline (step 1e-1 must FAIL) | **`PENDING`** | the discriminating control was never bought — see §5's table note |
| **G5** planted-zero control | **`PASS`** | §4.1 below — 12 selftest controls **plus 4 live controls on this run root's own `geom.log`** |
| **G6** launch gate | **`PASS`** | `OPEN` on the first reading before the only launch; §2.2 |
| **G7** image identity | **`PASS`** (patched row) / **`PENDING`** (shipped row) | patched read **live from inside the loading process**: `85f59e87253e0a71a813f64ca6e4c425` = registered. Shipped image never loaded |
| **G8** cold start | **`PASS`** on the verified limb; **`PENDING`** on the free limb | no `processor*`, no numeric time dir but `0`, `0/` from `0.orig/`, no `reports/` — verified **before** the launch in all five stages. The **free check** (`eta_call1_CD` reproducing `0.1529738469354696`) was never bought, because Stage η did not run |
| **G9** memory envelope | **`PASS`** | measured peak **0.5973 GiB** against predicted 1.4, ceiling 2.5, kernel cap 6 GiB (`--memory=6g --memory-swap=6g`, equal — no swap escape). **Not OOM-killed**: rc 1, not 137. Headroom was unused, and §8 G9 says in terms that *"a failure with headroom unused is not a memory finding either"* — **this crash is not a memory finding** |
| **G10** cost ceiling | **`PASS`** | **2.8667 core-min** of the attempt's **HARD 69.2** (§10.2, ruled to stand in ADDENDUM A1) and of the frozen comparator's own printed 70.0. **No stage exceeded its ceiling; F12 did not fire** |
| **G11** Stage G reproduces Stage O's setup path | **`PENDING`** — **no limb failed** | limbs (a) and (b) **`PASS`** (§2.1). Limb (c) is a **three-way** check across `geom.log`, `eta.log` and `opt.log`; **`eta.log` and `opt.log` do not exist**, so the cross-stage comparison **cannot be completed**. `geom.log`'s own share is satisfied — see §4.2. Limb (d) was **applied** and returned F1c (§3.2). **`F13` did NOT fire** |
| **Gs** separation-onset monitor | **`PENDING`** | the monitor's graded input is **Stage η's own baseline field**, and Stage η did not run. **No field of this attempt exists to read.** See §5's P11 row for what this does and does not leave standing |
| **Gθ** rear-slant angle, band [12.0°, 25.0°] | **`PENDING`** | Stage G never wrote `G_jac`, so **the measured coefficient pair `(cB, cR)` does not exist** and the comparator had nothing to substitute. The frozen design angle is **25.00°** by construction (§4), and the comparator's own controls read **24.9951°** at `d = (0,0)` and **15.990°** at A4's optimum — **those are selftest controls of the reader, NOT a measurement of this run**, and they carry no verdict here |

### 4.1 G5 evidence — the planted-zero control, run live against **this** run root's artifacts

**Limb 1 — the frozen comparator's own selftest.** `python3 d3_grade.py --selftest`, run with this
directory's carried copy (md5 `a32f075853e264910ee0a6c2473fd948`): **exit 0**, all **12** controls
`SEEN`, closing `ALL CONTROLS SEEN.` Artifact:
`/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/g5_live/selftest.txt`.

**Limb 2 — four controls planted into a copy of the artifact THIS run wrote**, which is what makes the
`[A]` zero evidence rather than an absence. The original `geom.log` is **never written to**; the
plants are made on copies under `<root>/g5_live/`.

| control | file | the frozen comparator's reading |
|---|---|---|
| **[A] UNPLANTED** — byte copy of this run's `geom.log` | `geom_real.log` | **G7 `PASS`** — *"read `85f59e87253e0a71a813f64ca6e4c425`, registered `85f59e87…`"*; **G3+G4 `NOT A RESULT`** — *"plateau needs all of [0.01, 0.001, 0.0001]; log has []"*; **G10 `PASS`** at 2.867 core-min |
| **[B] PLANTED image hash** (`85f59e87…` → `000…0`) | `geom_planted_md5.log` | **G7 `GATE FAIL`** — *"read `00000000000000000000000000000000`, registered `85f59e87…`"*. **The reader sees a corrupted identity in a file this attempt's producer wrote.** |
| **[C] PLANTED `check_totals`** — a **real** block lifted from A4's own `opt.log:59255-59271`, wrapped in the producer's `D3_CHECK_TOTALS_BEGIN/END` markers at all three plateau steps | `geom_planted_ct.log` | the same reader on the same file now returns *"plateau step = 0.001 … `dvs.shape idx0: analytic 2.14102040e-01 fd 2.14770370e-01 rel 0.3112% flip=False`"* — **a non-zero, read back from disk** — and **still** `NOT A RESULT`, because *"trivial baseline at step 0.1 absent — the gate was never shown to discriminate"* |
| **[D] PLANTED sign flip** (same block, FD sign inverted) | `geom_planted_ctflip.log` | *"analytic 2.14102040e-01 fd **−2.14770370e-01** rel **199.6888%** flip=**True**"* — **the per-component flip is seen** |

**Therefore the `[A]` empty-plateau reading is evidence** (`CLAUDE.md` rule 3): the identical reader,
on the identical file, returns a non-zero and a sign flip when one is planted. Artifacts:
`<root>/g5_live/{selftest.txt, geom_real.log, geom_planted_md5.log, geom_planted_ct.log,
geom_planted_ctflip.log, grade_real.txt, grade_md5.txt, grade_ct.txt, grade_ctflip.txt}`.

**The [C] and [D] numbers are PLANTED CONTROLS. They are not a measurement of this item, they carry no
verdict, and they are not the endpoint FD table of §5.** (`docs/LESSONS.md`'s warning on evidence
annotated as non-binding cuts both ways: a planted number presented beside real ones must be labelled
at every appearance, and it is.)

### 4.2 G11 evidence — the five setup markers, and why the gate is `PENDING` and not `PASS`

§8 G11(c) registers five literal markers and requires **all five in `geom.log`, `eta.log` and
`opt.log` alike**. Measured in this run's `geom.log`, with the counts §8 recorded in parentheses:

| marker | registered count | this run |
|---|---|---|
| `Reading the OpenFOAM mesh..` | (2) | **2** |
| `('designSurfaces', [0])` | (1) | **1** |
| `dRdWT Jacobian Free created!` | (1) | **1** |
| `<class DAFoamSolver>` | (1) | **1** |
| `<class DAFoamFunctions>` | (2) | **2** |

**All five present, at exactly the registered counts.** This is real and load-bearing evidence: it says
Stage O's setup path **now reaches past `nom_setConstraintSurface`**, which attempt 1's could not. But
the gate is a **comparison across three logs**, and two of them do not exist. **A one-log reading is
not the three-way check, and this report does not promote it into one.** `G11` = **`PENDING`**;
no limb failed; `F13` did not fire.

---

## 5. Predictions — HIT / MISS / NOT TESTED, with the numbers

| id | prediction | band / HIT rule | **outcome** | measured |
|---|---|---|---|---|
| **P1a** | the DVCon calls return without raising | — | **NOT GRADED** — disclosed as **pre-observed** by §2.2's probe and removed from grading at the freeze | *(corroborated live anyway: `Need to add surface` count **0** in this run's `geom.log`, and execution continued 47 lines past the DVCon calls)* |
| **P1b** | every DVCon baseline value finite and within **1e-6 of 1.0** | 30 `thickcon_slant` rows + 1 `volcon_aft` row, all finite, all within 1e-6 | **NOT TESTED** | the crash at producer `:261` **precedes** `_f("geometry.thickcon_slant")` at `:267`. **No constraint value was ever read.** `d3_summary.json` absent |
| **P2** | measured FFD z-Jacobian vs `(+0.72287, −0.43863)` | within **2 %** | **NOT TESTED** | `G_jac` never written — the Jacobian loop is at `:270-296`, past the crash |
| **P3** | symmetry residual | `max|z(+y) − z(−y)| ≤ 1e-9` | **NOT TESTED** | the symmetry loop is at `:282-292`, past the crash |
| **P4** | δ_repeat at the baseline | **[0, 1.4e-05]**, point est. ≈1e-06 | **NOT TESTED** | Stage η not launched |
| **P5** | the η plant is seen | `|ΔCD|` ∈ **[1.0e-05, 4.0e-05]**, point est. **2.415e-05** | **NOT TESTED** | Stage η not launched |
| **P6** | Stage O termination, majors ∈ **[7, 14]** | `EXIT: Optimal Solution Found.`, NLP error < 1e-6 | **NOT TESTED** | Stage O not launched |
| **P7** | CD reduction **≥ 7.478 %**, band **[7.4 %, 16 %]** | | **NOT TESTED** | Stage O not launched. **No constrained optimum exists**; no CD, no design vector, no constraint values, no majors, no IPOPT `EXIT` line |
| **P8** | two images' analytic gradients agree ≤ **1e-4** relative per component | | **NOT TESTED** | Stage T not launched on either image |
| **P9** | endpoint FD per-component rel. error ∈ **[0.1 %, 2.0 %]**, zero sign flips | | **NOT TESTED** | no `check_totals` block produced by this attempt |
| **P10** | θ at the optimum ∈ **[14°, 22°]** | | **NOT TESTED** | no optimum |
| **P11** | **the separation monitor REFUSES** — `n_rev_global = 0` and `n_cells(B) < 20` on **Stage η's own baseline field** ⇒ `NOT AN INSTRUMENT`, reported `NOT A RESULT` | | **NOT TESTED** | **Stage η's baseline field does not exist.** The monitor was **not run on a substitute**: `<root>/eta/0/U` is a cold initial condition, not a solved field, and running the monitor on it would not be P11's experiment. See the note below |
| **P12** | `m_def_global` at the optimum ∈ **[0.45, 0.75]** | | **NOT TESTED** | no optimum field |
| **P13** | peak RSS **≤ 2.5 GiB**, point est. 1.4 | | **NOT TESTED** | measured **0.5973 GiB**, but on a **no-flow** stage. §7's P13 row says in terms that a no-flow Stage G reading *"is not this prediction's experiment and is not carried as a HIT"* — **that rule is applied to this attempt's own reading, not only to attempt 1's** |
| **P14** | attempt-2 total **≤ 59.2** core-min, **HARD ≤ 69.2** | | **HIT — trivially and uninformatively** | **2.8667** of ≤ 59.2. Three of four stages never launched; the prediction was about a *completed* attempt and this one is not. **Recorded as a HIT and simultaneously as no evidence about the estimate** |
| **P15** | **Stage G runs the WHOLE `geom_probe` block to completion** — `d3_summary.json` with all eight `G_*` keys, rc = 0 | | **MISS** | **rc = 1**; `d3_summary.json` **absent**; **0 of 8** `G_*` keys written. The block was entered and died on its first statement |

**P11 and F11 — what stands and what does not.** **`F11` did NOT fire and was not testable**: it fires
on `n_rev_global ≥ 1` on Stage η's baseline field, and that field does not exist. **No reading of this
attempt bears on P11 either way.** What stands unchanged is the *prior*, and it is a prior, not a
result: §9's freeze-time measurement on three archived A4 fields (`n_rev_global = 0` on all three,
`min U_x` **23.526 / 24.084 / 24.095 m/s**, `m_def_global` **0.5882 / 0.6021 / 0.6024**,
`n_cells(B) = 2`), plus the supervisor's independent count over every 2,777-cell A4 field on disk —
**zero reverse-flow cells everywhere** — against **528** on a 79,439-cell Ahmed-25 field and **780** on
the cfd team's 9,050-cell F5c field, which is the monitor's **reader-capability control**. **P11 was
expected to HIT and remains unbought.**

**Falsifiers.** `F1c` **FIRED** (§3.2). `F1a`, `F1b`, `F13` **did NOT fire**, each with its own evidence
absent rather than merely unobserved. `F2`–`F12` **NOT TESTED** — every one of them needs a stage that
did not launch. **`F12` (any stage exceeds its ceiling) did not fire: 2.8667 ≤ 3.0.**

**The endpoint per-component FD table — the item's primary report, and it is empty.** §8 G3 fixes it as
per-component and never aggregated. **This attempt produced no `check_totals` block at any step**, so
the table has **zero rows**, `G3` is `PENDING`, and `G4`'s trivial baseline at step 1e-1 — the control
that would show the gate discriminating — **was never bought**. The only per-component rows anywhere in
this record are the **planted controls** of §4.1 [C] and [D], and they are labelled as such at every
appearance.

---

## 6. Cost (`CLAUDE.md` rule 12; `COMPUTE_BUDGET_CHARTER.md`)

`cost_basis:` **c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Every dollar figure
below is DERIVED from core-minutes and is never quoted as measured.**

### 6.1 What was spent

| line | core-min | basis |
|---|---|---|
| Stage G | **2.8667** | **MEASURED** — 172 wall s × 1 rank ÷ 60, `<root>/ledger.txt` |
| Stages η, O, T-patched, T-shipped | **0.0** | not launched |
| **attempt 2 total** | **2.8667** | **= $0.002451 DERIVED** |

**Gross or cleaned?** **Gross = cleaned = 2.8667.** The single row's wall is 172 s against the 3600-s
stall rule, so nothing is cleaned out (`COMPUTE_BUDGET_CHARTER.md` §2).

**Against the ceilings:** 2.8667 of the Stage-G ceiling 3.0 (**95.6 %**, no overrun) and of the
attempt's **HARD 69.2** (**4.14 %**). **66.3333 core-min of this attempt's budget were never spent and
are not carried forward to any other item.**

### 6.2 Estimate versus actual — the registered deliverable, and what it does and does not mean

Sanaa's directive, verbatim (2026-08-23): *"for all teams involved once a process is completed, the
estimated costs must be compared with the actual incurred costs so we can improve the lab's estimates"*.

| level | predicted | actual | **ratio** | reading |
|---|---|---|---|---|
| **Stage G** | **0.8** core-min | **2.8667** core-min | **3.583×** | **the one calibratable figure this run produced** |
| **attempt 2 total** | **29.6** core-min | **2.8667** core-min | **0.097×** | **NOT A CALIBRATION OF THE ESTIMATE.** Three of the four stages never launched; the denominator prices work that was never attempted. Recorded because the directive asks for the total, and labelled because the number would otherwise read as a 10× over-estimate |

**Gap attribution for the Stage-G 3.583×, with the evidence and its limit.**

The dominant term is **misprediction, and it is located**. `geom/mphys.html` — written by producer line
**215**, `om.n2(prob, …)` — has mtime **18:33:35.815Z**. The container started **18:31:01Z** (172 s wall
ending 18:33:53Z; first RSS sample 18:31:07Z). **Producer line 215 therefore completed ≈154.8 s into a
172 s wall — ≈90 % of the run.** `OptFuncs` (`:217`) and the whole `geom_probe` block up to the crash at
`:261` had **≤ ~17 s**, teardown included.

**So the cost is in the COMMON SETUP PATH, at or before line 215 — the path every stage pays, on every
task.** That is the calibration output, and it is worth more than the ratio: **Stage G's 0.8 prediction
was based on §2.2's probe, which measured container + `prob.setup` at 11 s wall and stopped at line
214 — one line before the expensive one.** §10.1 named that basis explicitly (*"the probe measured
container + `prob.setup` = 0.1833 core-min (11 s)"*), so the misprediction is a **registered and
disclosed risk that materialised**, not a hidden one.

**What is NOT separated, stated plainly.** If the setup path here cost what the probe's whole 11 s
cost, then `om.n2` alone consumed **≈144 s**. That arithmetic assumes the setup path was not itself
inflated, and **that assumption is not measured**. **Contention is NOT measured and is not claimed:**
§10.3 registers the contention basis as *"the same internal work item in two logs"*, and the probe's
log carries **no marker past `setup`**, so there is no like-for-like work item to compare. Host `load1`
was **3.29** at the G6 reading with the container capped at `--cpus=1`, which makes contention a live
candidate and nothing more. **Whole-arm wall clocks are NOT an inflation figure** (§10.3), and none is
offered.

**WASTE — named separately and never absorbed into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6).

**2.8667 core-min GROSS, unrecovered.** Stage G was priced for P1b, P2, P3 and P15 and returned **none**
of them; it returned a producer defect. That is the same accounting attempt 1's §6.1 applied to its own
0.300, and it is applied here to a figure **9.6× larger**. **It is reported gross and is not netted
against what the run did buy.**

**What it did buy, named separately and NOT subtracted from the waste:** the repair proved live (the
attempt-1 `KeyError` gone, execution 47 lines further on); G7 `PASS` read live from inside the loading
process; G11 limbs (a) and (b) `PASS`; all five G11(c) setup markers present in `geom.log` at their
registered counts — evidence that Stage O's setup path now reaches past `nom_setConstraintSurface`; the
next defect located to a line; and the ≈90 %-of-wall setup-path cost measured, which re-prices **every**
stage of any attempt 3.

**Item two-attempt-plus accounting** (§10.2's table, extended by this attempt's actual):

| line | core-min | basis |
|---|---|---|
| attempt 1, Stage G | **0.300** | MEASURED, `<attempt-1 root>/ledger.txt` |
| attempt 1, triage container | **≤ 0.30** | **BOUND, not a measurement** — attempt 1 `RESULTS.md` §6.1/§7.2 |
| attempt 2, pre-freeze diagnostic probe (§2.2) | **0.1833** | MEASURED, `<probe root>/probe_ledger.txt` |
| **attempt 2, Stage G** | **2.8667** | **MEASURED, this run's `ledger.txt`** |
| **item total, worst case** | **≤ 3.6500** | **= $0.003121 DERIVED** |
| **against the curriculum's ~70.0 core-min / $0.06** | **5.21 % of it** | `EXPERTISE_CURRICULUM.md` §3 Tier 1 row D3 |

**The item's budget is not the constraint.** **66.35 core-min of the curriculum figure remain.** What
stops this attempt is `F1c`, not cost — and §6.3's repair policy, not the ledger, decides what happens
next.

### 6.3 The calibration row — landed, and the departure that let this lane land it

**Row `C-46`, appended to `docs/COST_CALIBRATION.md` in the same commit as this file.**

**This is a DEPARTURE from the frozen pre-registration and is recorded as one.** §10.3 says in terms:
*"this lane **DRAFTS** the calibration row into this item's `RESULTS.md`; the **supervisor lands it** in
`docs/COST_CALIBRATION.md`. **No lane writes that file.**"* §13 item 9 lists that file among those this
lane writes none of.

**What changed is not the reading but the authority.** The dafoam-supervisor's dispatch brief for this
phase directs this lane to append the row and names the safeguards, and the supervisor's written
mid-task direction — issued **after** personally reading `geom.log`, the `SUPERVISION_CHARTER.md` §3
crash triage that may not be delegated — repeats it (*"calibration row with the four ledger asserts"*).
**This is the same departure attempt 1 recorded in its own ADDENDUM R1, on the same authority and with
the same safeguards**, and it is disclosed here rather than performed silently.

**Why the direction is answerable rather than merely obeyable** (`CLAUDE.md` rule 9):

1. §10.3's clause is a **procedural allocation of who writes**, not a gate, threshold, band, cap or
   label. **Nothing gated moved.** Rule 2's post-compute closure is untouched: no gate, band or ceiling
   in §§7–10 is altered by this file.
2. The clause's stated **reason** is that `docs/COST_CALIBRATION.md` **lags HEAD by design** under the
   private-index protocol and must never be used as a base. **That reason is honoured, not bypassed** —
   the row was merged onto the **committed blob**, never the worktree, and the measured staleness is
   recorded below.
3. **Nothing here is a Sanaa-reserved action**: no send, no scoring call, no charter or threshold
   retired, nothing leaving the box. **No permission setting, `CLAUDE.md` or `.claude/` config was
   touched, and a peer's or supervisor's message could not have authorised that if it had asked**
   (rule 9). Rule 12's calibration bullet independently requires the row to land in that file at
   process completion.

**The four ledger asserts, as directed, with their readings.** All four executed **inside the single
commit invocation**, against the **committed blob** at the same `H` passed to `commit-tree -p`:

1. **Id re-derived at commit time as the MAXIMUM EXISTING NUMBER, never a count** (`CLAUDE.md`
   rule 11), over `^\| C-[0-9]+` in the **HEAD blob**: **previous last id `C-45`, new id `C-46`.**
   The worktree copy held max `C-43` and was **not** used as the base. `scripts/append_record.py` was
   run first, with `--rev HEAD --expect-first-id C-46 --dry-run`, and **REFUSED (exit 2)**, correctly:
   *"the worktree is SHORTER than the blob, which is a truncation, not an append"* — **142,111
   worktree bytes against the committed blob's 150,881, diverging at byte 142,111, a 2-row lag.
   Divergence by design; nothing was written and nothing was reverted.** In the same breath the tool
   independently confirmed the id arithmetic — *"series `C-`: maximum existing number — committed blob
   **45** … `ID ASSERT ok: C-46 == max+1`"*. The documented
   `hash-object`-from-the-HEAD-blob fallback was then used, the same fallback D486 and `df36bd3f`
   record, and the worktree copy was left exactly as it was found.
2. **The HEAD blob's last byte verified `\n`**, so the append cannot splice onto an unterminated final
   row.
3. **Prefix identical:** every byte of the committed blob before the appended row is unchanged —
   asserted as **insertions only, 0 deletions** in `git diff-tree --numstat` and again in the
   post-commit `git diff HEAD~1 HEAD --numstat`.
4. **Previous last id on its own line and new id on its own line** — `C-45` and `C-46` each begin a
   line of their own in the **built blob**, asserted by grep on that blob and not on the worktree.

All four readings are stated in the commit message as well as here.

---

## 7. Departures and disclosures — everything this phase did that the frozen file did not say

### 7.1 The reporting form

§19 step 9 says *"RESULTS.md: six report headings"*. **The six fixed headings of
`REPORTING_CHARTER.md` §2 are `SPEND / LADDER POSITIONS / GATES / FD TABLES / REFILLED QUEUE / WAITING
LIST` — the frame of the daily morning report**, matched literally there and required in that document.
They are not the form of a results file, and no results file in this ladder uses them. **This file
follows the A4 sibling's and attempt 1's form** (HEADLINE + §1–§10) and covers the charter's subject
matter in §6 (spend), §4 (gates) and §5 (the tables). **Disclosed as a reading of §19, not as a silent
choice** — identically to attempt 1 §7.1.

### 7.2 The calibration-row departure

§6.3, in full, with its authority, its four asserts and its rule-9 answer.

### 7.3 The ledger's peak-RSS misparse

§2's note. The launcher's ledger cell reads `peak_rss_GiB=11`; the true peak is **0.5973 GiB**. The
launcher is not a frozen file; it was **not** edited, because the run is over and a silent repair would
leave the committed ledger row and the script disagreeing with nothing on the record. **Recorded, not
fixed**, at the supervisor's direction.

### 7.4 `docker inspect` could not be run

§2's note: `--rm` is registered in §11, so the container is destroyed on exit. Exit code taken from the
launcher's `wait` (**rc = 1**); OOM read from the absence of 137, as §8 G9 registers. **A disclosed
limitation of the frozen invocation.**

### 7.5 What was NOT done, deliberately

- **No frozen file was edited.** `PREREGISTRATION.md` gained only ADDENDUM A1, appended at the foot,
  committed **before** the first container, with `lines whose number changed above this section: 0`
  asserted by md5 of `head -n 823` before and after the append in the same invocation.
- **No repair was attempted, in place or otherwise**, and **no attempt 3 is drafted** — the supervisor's
  explicit instruction and §6.3's policy agree.
- **Nothing outside this attempt's run root was written.** Attempt 1's run root and item directory, the
  probe root, the A4 records and the A4 mesh were **read-only** throughout; §13's eleven named
  exclusions all hold.
- **Stages η, O and T were not launched after the Stage-G crash**, and **no second budget was taken**.
- **`docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md` were not
  written by this lane.** §9's candidates are drafts for the supervisor to land.

---

## 8. What this item could not see

1. **Everything Stage G was priced to measure.** No constraint value, no FFD Jacobian, no symmetry
   residual, no `d3_summary.json`. **P1b, P2, P3 unbought.**
2. **The whole constrained-optimisation claim.** No CD, no reduction against A4's **−7.478 %**, no
   constraint values at an optimum, no majors, no IPOPT `EXIT` line, no rear-slant angle. **The
   expertise D3 is meant to buy — 3D geometric constraints under a 3D adjoint — remains unbought after
   two attempts.**
3. **The clean two-image toolchain comparison** (`F10`/`P8`) that A4's own `RESULTS.md` §8 limit 3 named
   as missing. Still missing.
4. **Whether the `geom_probe` block has any further defect past line 261.** The frontier moved from 214
   to 261 and stopped there. **Lines 262–299 remain unexercised**, and by the same argument §2.3(1) made
   about the probe, nothing here is evidence about them.
5. **Whether contention inflated this run.** Not separated; §6.2 says why and does not guess.
6. **Whether the A4 mesh carries separation.** Unchanged and unbought here — the prior stands, `P11`
   and `F11` are both untested, and the item still does not claim the separation content (§9 of the
   pre-registration).

---

## 9. Record candidates — DRAFTED here, landed by the supervisor

**This lane writes none of `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`, `docs/DOCKET.md` or
`docs/LAB_STATE.md`.** Ids are deliberately **not** assigned — rule 11 fixes them at commit time from
the tail's maximum.

### 9.1 LESSON candidate — a probe is evidence about the lines it reached, and no further

A zero-flow probe was registered, priced and read as the cheap instrument that catches a producer
defect before a paid primal. **It caught one, and then a second defect 47 lines past where it stopped
cost 9.6× more than the probe did.** §2.2's probe ended at `prob.setup(mode="rev")` and §2.3(1)
disclosed that limit precisely — **and the item still spent its Stage-G budget discovering that the
disclosure was load-bearing.** The lesson is one level down from L-273: a key-set control parses names,
a selftest plants values, a setup probe reaches `setup` — **and a producer block is only evidenced by
running the producer block.** Operationally: **a probe intended to de-risk a stage must be dry-run
against the frozen inputs to the END of that stage's own task block, not only through setup**; where it
cannot be (because the block needs state `setup` does not build), the pre-registration should say which
lines remain unexercised and price the stage as if they will fail. *(The lesson's own limit, stated:
this run does not prove a cheap end-to-end dry run was available here — `dvg.update("aero")` needs a
constructed DVGeo, so the instrument may be the paid container itself.)*

### 9.2 NUMERICS-FACT candidate — `nom_add_discipline_coords` does not embed a point set named for its discipline

**Measured, not inferred**, at `<root>/geom.log:472-481`: with the attempt-2 repair in place and
`prob.setup(mode="rev")` complete, `DVGeo.update("aero")` raises **`KeyError: 'aero'`** from
`pyBlock.getAttachedPoints` at `pyBlock.py:745` (`self.embeddedVolumes[ptSetName]`), reached from
`DVGeo.py:2012`. **The name `"aero"` passed to `nom_add_discipline_coords("aero", points)` is not the
key under which the point set is embedded in the FFD.** Image `dafoam-idwarp-rot:v1`, DAFoam v5.0.0,
np = 1, 2,777-cell A4 mesh. **What this fact does NOT establish:** what the correct key *is* — that
requires reading `nom_add_discipline_coords`'s body, which is a triage step for the supervisor and was
not taken here.

### 9.3 LESSON / defect candidate — F1a's content limb and F1c's location limb overlap

§17.1 gives **F1a** a *content* decision rule (*"a `KeyError`/`AttributeError` about an unregistered
object"*) and **F1c** a *location* rule (*"the final producer frame is at or below line 248"*), while
§8 G11(d) declares the location rule the decider. **This run produced an event satisfying both limbs at
once** — a `KeyError` about an unregistered object, raised from inside the task block — and only G11(d)
resolved it. The taxonomy that attempt 1's mis-reading of F1 was written to prevent has an ambiguity of
its own. **Candidate rule: where a falsifier taxonomy carries both a content test and a location test,
the pre-registration must state which governs, in the falsifier row itself and not only in the gate
that references it.** *(Applied here as registered: location governs, class F1c.)*

### 9.4 NUMERICS-FACT candidate — the setup path, not the task, is where this producer's wall clock lives

On the A4 2,777-cell case with two shape-function DVs and two DVConstraints, **producer line 215
(`om.n2`) completed ≈154.8 s into a 172 s no-flow run** (`geom/mphys.html` mtime 18:33:35.815Z against a
container start of 18:31:01Z), while §2.2's probe reached line 214 in **11 s wall** including container
start. **≈90 % of a no-flow stage's wall sits at or before line 215, in the path every task pays.**
**Limit, stated:** the split between `om.n2` and an inflated setup is **not measured**, and contention
is **not measured** (no like-for-like work marker exists — §10.3's registered basis is unavailable
here). **Consequence for any attempt 3: every per-stage price in §10.1 is based on a setup cost of ~11 s
and must be re-derived before it is frozen again.**

### 9.5 DOCKET candidate

**D3 attempt 2 — `BLOCKED` at Stage G, falsifier class `F1c`.** The `nom_setConstraintSurface` repair
worked; the next defect is `dvg.update("aero")` → `KeyError: 'aero'` at producer `:253`. 2.8667
core-min spent of the 69.2 HARD; item total ≤ 3.6500 of the curriculum's ~70.0. **On the supervisor's
desk:** the §6.3 / `VERIFICATION_CHARTER.md` §2d.1 four-condition decision on whether a third
registration is warranted, and if so at what price given §9.4. **This lane drafted no attempt 3.**

---

## 10. Verdict vocabulary

**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING** — and no synonyms.

- **Item: `BLOCKED`.** §18 fixes it: *"a Stage-G crash of any class makes the item `BLOCKED`"* — a
  precondition prevented the measurement. **Not `NOT A RESULT`**, which is reserved for a value produced
  and ungradeable, and no value was produced.
- **Stage G: `BLOCKED`.** The crash is a **finding** until the supervisor's triage says otherwise
  (`SUPERVISION_CHARTER.md` §3).
- **`PENDING` is used here only for "not yet run"**, never to soften anything: Gη, G1, G2, G3, G4, Gs,
  Gθ and the shipped toolchain row are `PENDING` because their stages did not launch.
- **`NOT AN INSTRUMENT` does not appear as a verdict anywhere in this file.** It is the frozen monitor's
  printed **reason**, and the monitor did not run — so there is no `Gs` reason to print beside a
  `NOT A RESULT` this time either (ruling 4 is carried, unexercised).
- **Shipped and patched are separate rows** and are never merged into one verdict.
- **The 12 selftest controls and the 4 live planted controls of §4.1 are CONTROLS, not results.** No
  number produced by a plant carries a verdict about this item.

**NOT FILED ANYWHERE** (`CLAUDE.md` rule 7). SUBMISSIONS PARKED.
