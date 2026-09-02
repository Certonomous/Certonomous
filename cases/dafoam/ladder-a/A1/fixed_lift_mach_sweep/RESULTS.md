# MAAOA — FIXED-LIFT (Ma, AoA) SWEEP, A1WR L3, PATCHED BUILD. **NO VERDICT OF RECORD.** The frozen reader refused at `rc = 2`, 664.0 core-min

**Item outcome: NO VERDICT OF RECORD.** The frozen grader —
`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/fixed_lift_mach_sweep/maaoa_read.py`
— **REFUSED**, `reader_rc=2`, and printed no table. **A refusal is not a verdict.**
This record therefore publishes **no** `PASS`, **no** `GATE FAIL`, **no**
`NOT A RESULT` and no other token as this item's verdict, and **none is supplied
here.** The grading path is fixed at the pre-registration commit
(`CLAUDE.md` rule 2), so **no other reader may be substituted** to manufacture one.

| | |
|---|---|
| item | **MAAOA** — NACA0012, A1WR mesh family **L3**, 130,304 cells, wall-resolved, each operating point **trimmed to fixed lift `CL = 0.5`**; incompressible `DASimpleFoam` control + compressible `DARhoSimpleFoam` Mach axis, np = 1, seven points |
| pre-registration | `/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/fixed_lift_mach_sweep/MAAOA_PREREGISTRATION.md` |
| freeze | **`586b72caf39dad1f79b028cf590818da585688a2`**, 2026-09-02T18:18:51Z, through Amendment 2 — **109 s before the driver armed** (18:20:40Z) and **1,070 s before the first solver launched** (18:36:41Z) |
| rule-2 hash check | prereg blob on disk **`c399da2a3dafb6a46ad46579d91a69fab43c352c`** == the blob at `586b72ca` — **the frozen file IS the file that ran**; the reader likewise, blob `2486c9b2a9394c260f5a4ad5e13c506636f4d475` |
| grading path | `maaoa_read.py`, md5 **`79fddadcc748d3b83efb1d4ed8023475`**, manifest `MAAOA_MD5.txt`, `md5sum -c` clean on all four instruments; driver md5 **`fdf184ecf0cde5df59c219b7a23d72a1`** (Amendment 1's re-pin) |
| queue entry | `/home/ubuntu/Certonomous/verification/queue/dafoam/launched/MAAOA_chain.json`, `prereg_commit` `586b72ca…` |
| run root | `/home/ubuntu/certonomous-runs/MAAOA` |
| grader output | `/home/ubuntu/certonomous-runs/MAAOA/MAAOA_read_20260902T182040Z.txt` — **`SELFTEST REFUSED -- M1: 5 controls.`** |
| chain | `STATUS.MAAOA_chain` — `rc=0 phase=COMPLETE spend_total=664.0 reader_rc=2 utc=2026-09-02T21:58:19Z` |
| **cost, MEASURED** | **664.0 core-min gross** against **315** registered (ratio **2.108**), item ceiling 900. **$0.56772 DERIVED, NOT MEASURED** |

**THE REFUSAL AND THE PHYSICS ARE TWO SEPARATE FACTS, AND THE SECOND SURVIVES THE
FIRST.** Sanaa's universal rule of 2026-08-26 — *bookkeeping never voids physics* —
binds here in its exact form: the grader's inability to compose a verdict does not
delete what the solvers wrote to disk. §3 publishes those numbers, **labelled
READINGS and never verdicts.** What is lost is the composition, not the measurement.

---

## 1. THE SEVEN POINTS

Ledger: `/home/ubuntu/certonomous-runs/MAAOA/CHAIN_LEDGER.tsv`.
Launch log: `/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/fixed_lift_mach_sweep/launcher.queue.out`.

| point | arm | U0 (m/s) | M | cpuset | rc | wall s | core-min | oom | outcome in its own log |
|---|---|---|---|---|---|---|---|---|---|
| `MA288` | C | 100.0 | 0.2880 | 2 | **97** | 5,550 | 92.5000 | false | `Primal solution failed!` |
| `MA400` | C | 138.8762 | 0.4000 | 3 | **97** | 5,488 | 91.4667 | false | `Primal solution failed!` |
| `MA500` | C | 173.5952 | 0.5000 | 4 | **97** | 5,549 | 92.4833 | false | `Primal solution failed!` |
| `MA600` | C | 208.3142 | 0.6000 | 5 | **97** | 5,549 | 92.4833 | false | `Primal solution failed!` |
| `MA650` | C | 225.6738 | 0.6500 | 6 | **97** | 5,548 | 92.4667 | false | `Primal solution failed!` |
| `MA685` | C | 237.8254 | 0.6850 | 7 | **97** | 5,547 | 92.4500 | false | `Primal solution failed!` |
| `INCOMP` | I | 10.0 | n/a | 3 | **0** | 6,609 | 110.1500 | false | `FindFeasibleDesign Converged!` |
| **item** | | | | | | **39,840** | **664.0000** | | |

**`rc = 97` is this item's own registered token for a recorded, un-retried
failure**, not a timeout: `maaoa_cmd.sh:6` — *"a trim that raises is RECORDED (rc 97)
and reported as-is"* — and `maaoa_cmd.sh:41-42`, which prints
`MAAOA_POINT_RECORDED_WITH_ERROR … -- reported, not retried` and exits 97. Every
compressible point ran its full 4,000-iteration `endTime` inside its 7,200 s
container deadline (`tmo_s=7200`); **no point was cut by its deadline, no point
was retried, relaxed, re-tuned or dropped**, exactly as §1 of the pre-registration
requires.

**Caps: none breached.** The largest point is `INCOMP` at **110.15 core-min**
against the **120 core-min** per-point cap; the item's **664.0** sits under its
**900** ceiling. `G-CAPS`'s prospective stop never fired and no point is a
cap-stop.

**`G-GATEDEP` released as registered.** The driver launched no solver for
**960 s** while it polled A1WR's stage-1 gate, then recorded
`MAAOA_GATEDEP_PASS … verdict PASS after 960s` at 18:36:40Z. The dependency lived
in the chain and not in agent hands (pre-registration §3), and the wait spent zero.

---

## 2. THE READER REFUSED — AND M2 THROUGH M5 ARE WHY THE REFUSAL IS EVIDENCE

### 2.1 THE FIVE CONTROLS, VERBATIM FROM THE READER'S OWN OUTPUT

From `/home/ubuntu/certonomous-runs/MAAOA/MAAOA_read_20260902T182040Z.txt`:

```
PLANTED CONTROLS -- read back through the real parsers, both directions.
  source: /home/ubuntu/certonomous-runs/MAAOA/MA288/out/trim.log
  sha256: ae964c2f64cd959bc698b3f95e1f5706b9a074a40310c65a3f895b669e9703e2
  M1   unmodified bytes -> full row, TRIMMED                    *** FAIL ***
  M2   planted CL=0.612 -> NOT TRIMMED                          PASS
  M3   parser disabled -> M1 must flip (channel goes blind)     PASS
  M4   planted y+max 1.71 -> read and >= threshold (GATE FAIL path live) PASS
  M5   G-STALL and G-MDD fire on plants, silent on the honest caveats PASS

SELFTEST REFUSED -- M1: 5 controls.
```

The fixture sha256 is confirmed on disk: `sha256sum` of
`/home/ubuntu/certonomous-runs/MAAOA/MA288/out/trim.log` returns
`ae964c2f64cd959bc698b3f95e1f5706b9a074a40310c65a3f895b669e9703e2`, byte-for-byte
the string the reader printed.

### 2.2 **M1 ALONE FAILED. M2, M3, M4 AND M5 ALL PASSED — AND THAT IS WHAT PROVES THE READER WAS NOT BLIND**

`CLAUDE.md` rule 3 exists because a zero from a reader never shown able to see a
non-zero is not evidence. **The same argument applies to a refusal**: a refusal
from an instrument that cannot read anything is worthless, and a refusal from an
instrument demonstrated live on the real bytes is a measurement. This one is the
second kind, and the four passing controls say so one channel at a time:

* **M2 — the trim parser is live and discriminating.** A planted `CL=0.612345` was
  substituted into the real MA288 bytes (`maaoa_read.py:109-115`), the mutation was
  asserted to land (`if b2 == base: … MUTATION DID NOT LAND -- control is inert`),
  and the reader returned `NOT TRIMMED`. **The channel that decides `G-TRIM` was
  shown flipping on a real perturbation of the real file.**
* **M3 — the blind-channel control.** `TRIM_PAT` was replaced with a pattern that
  cannot match (`maaoa_read.py:117-123`) and M1's own subject went to `None`.
  **The reader was shown going blind on demand**, so its sighted state is not an
  assumption.
* **M4 — the `GATE FAIL` path is live.** A `yPlus … max: 1.71` line was planted
  into the real bytes and read back at or above the `G-YPLUS` threshold
  (`maaoa_read.py:125-131`). **The y+ gate's failing branch was exercised on this
  run's own artefact**, not on a build-time fixture.
* **M5 — the two refusal gates fire and stay silent correctly.** `G-STALL` and
  `G-MDD` matched planted claims (*"the stall angle is 12 deg"*, *"drag divergence
  at 0.66"*) and did **not** match the item's honest caveats
  (`maaoa_read.py:133-139`). **The self-refusals this item registered against its
  own worst temptation were demonstrated in both directions.**

**So the instrument that refused was working in four of its five channels, on the
real bytes of this run.**

### 2.3 THE MECHANISM OF M1's FAILURE, EXACTLY

M1 is *"unmodified bytes -> full row, TRIMMED"* (`maaoa_read.py:106-107`): the
unmodified fixture must parse **and** must grade `TRIMMED`.

The fixture is chosen by `maaoa_read.py:163-167`, which walks
`sorted(run.glob("MA*")) + sorted(run.glob("INCOMP"))` and takes **the first
`out/trim.log` that parses**. `MA288` sorts first, and it **does** parse — the
failed point still writes a `MAAOA_TRIM_VALUES` line, carrying the sentinel:

> `MAAOA_TRIM_VALUES mach=MA288 U0=100.000000 alpha_deg=4 CL=1 CD=1 wall_s=5510.49 err=AnalysisError("'scenario1.coupling.solver' <class DAFoamSolver>: Error calling solve_nonlinear(), Primal solution failed!")`
> — `/home/ubuntu/certonomous-runs/MAAOA/MA288/out/trim.log:1580`

`|CL − 0.5| = |1.0 − 0.5| = 0.5` against the registered `G-TRIM` band of `1.0e-3`,
so `trim_verdict` returns `NOT TRIMMED` and M1's required `TRIMMED` cannot be
produced. **MA288 is a FAILED point, so the reader given its unmodified bytes
cannot produce a trimmed row: M1's premise was falsified by the run's own
outcome.** The refusal then fires at `maaoa_read.py:170-172` — the table, the
`G-WALLTREAT` line, every per-point row and every gate composition sit *after*
that return and were never reached.

**THE INSTRUMENT REFUSED RATHER THAN DEGRADING, AND THAT IS CORRECT BEHAVIOUR.**
It is the same discipline `CLAUDE.md` rule 4 fixes for the completion rule —
comparators **refuse (exit 2) rather than degrade** — and it is why this record
carries no verdict instead of a softened one. **A refusal is not a verdict** is
this family's own convention, and it is the convention the family already applied
to itself: D19's `G1_completion` age guard
(`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_D19/d19_grade.py:449`,
refusal machinery at `:128`, `:182`, `:199`) and the recorded treatment of D19R's
own grader refusal, which
`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_D19M/RESULTS.md:214`
names as a state **distinct from** `NOT A RESULT`: *"D19R's grader refused rc=2;
D19R2 grading attempt 1 = NOT A RESULT"*. Two different things, named
differently, by a document that had every incentive to blur them.

**AND THE DEFECT IS IN THE FIXTURE SELECTOR, NOT IN THE GATE.** Had the loop
reached `INCOMP` — which **is** trimmed, §3.1 — M1 would have passed and the table
would have printed. The selector takes the first *parseable* log rather than a log
independently known to be trimmable, and the registered ordering puts `MA*` first.
**The reader is frozen and has had first compute; nothing here is to be touched.**
It is recorded so a successor registers the selector's precondition in advance
rather than discovering it after a 664 core-min spend.

---

## 3. THE PHYSICS — PUBLISHED AS **READINGS**, EXPLICITLY NOT VERDICTS

**Nothing in this section is a gate result.** No gate is composed, no band is
scored, no verdict token is attached to any number below. These are what the
solvers wrote, cited to the file that holds them.

### 3.1 `INCOMP` — THE FIXED-LIFT CONTROL. IT CONVERGED, AND AS A READING IT **IS** TRIMMED

`/home/ubuntu/certonomous-runs/MAAOA/INCOMP/out/trim.json`:

| field | value |
|---|---|
| `alpha_trim_deg` | **4.755644949811032** |
| `CL` | **0.4999987189650539** |
| `CD` | **0.014434696273095972** |
| `wall_s` | 6558.116363763809 |
| `error` | **`null`** |

`rc = 0`, container wall **6,609 s** inside the **7,200 s** cap,
**110.15 core-min** inside the 120 core-min per-point cap.

**`|CL − 0.5| = 1.2810349461211956e-06` against the registered `G-TRIM` band of
`1.0e-3` — a factor of 780.6 inside it.** *(Sanaa's ruling states "three orders";
the artefact gives 2.892 orders. The narrower figure is used, per her own
instruction to prefer the artefact — the substance is unchanged: the trim error is
nearly three decades inside the band.)* **As a reading, this point IS trimmed, and
it would satisfy `G-TRIM`.** **And no gate verdict is composed from it**, because
the reader refused before any composition ran (§2).

DAFoam's own Newton trim closed on it. `INCOMP/out/trim.log`:

| `FindFeasibleDesign Iter` | `DesignVars` (α, deg) | `Constraints` (`CL`) | `Residual Norm` |
|---|---|---|---|
| 0 | 4.0 | 0.42296887 | 0.1540622615031263 |
| 1 | 3.93584835 | 0.41496745 | 0.17006509855869134 |
| 2 | **4.75564495** | **0.49999872** | **2.5620698922423912e-06** |

`FindFeasibleDesign Converged!` (`trim.log:2931`) against the frozen `tol = 1e-4`,
`maxIter = 10`. The Newton residual is the *relative* error and cross-checks the
absolute one exactly: `1.2810349461211956e-06 / 0.5 = 2.5620698922423912e-06`.

**AND ONE CAVEAT THE READING MUST CARRY, BECAUSE IT IS THE PRIMAL THAT PRODUCED
THE PUBLISHED NUMBERS.** Five primals ran across those three Newton iterations,
13,422 time-loop iterations in total:

| primal | last `Time` | DAFoam's convergence line | `Total Residual Norm2` |
|---|---|---|---|
| 001 | 4000 | **none printed** | 1796.807733513592 |
| 002 | 2946 | `Minimal residual 9.997083655914609e-09 satisfied the prescribed tolerance 1e-08` | 32.68805550254275 |
| 003 | 2018 | `Minimal residual 9.997287330332059e-09 satisfied …` | 42.92048357402096 |
| 004 | 458 | `Minimal residual 9.999330409965113e-09 satisfied …` | 52.31878635352416 |
| **005** | **4000** | **none printed** | **45.91224977662464** |

**Primal 005 is the one whose `CL` and `CD` are published above, and it reached the
4,000-iteration `endTime` without DAFoam printing its `satisfied the prescribed
tolerance 1e-08` line.** Stated plainly rather than left to be inferred. What sits
beside it, also measured: its final-iteration equation residuals are
`U0 initRes 2.611685273913492e-09`, `p initRes 6.797482254798008e-09`,
`nuTilda initRes 9.134569451258965e-09` (`trim.log:2892-2898`), all below the
`1e-8` tolerance; its `Total Residual Norm2` of **45.912** lies **inside** the
32.688–52.319 span of the three primals that *did* print the converged line; and
its `CL` settles monotonically over the last five prints —
0.4999718175153083 → 0.4999792638663522 → 0.4999862323140091 →
0.4999927165746502 → 0.4999987189650539. **This record does not resolve that into
a convergence claim. It reports both halves and composes neither.**

**Bounding census, `INCOMP`: 138 lines, every one `Bounding nuTilda>1e-16`. Zero
`p`, zero `rho`, zero `e`, zero `U`.** (`docs/LAB_STATE.md` block `S-27` §1 records
71 such lines; that was a live read while the point was still running. The
completed count is 138 and **the kind-census — nuTilda only — is unchanged**.)

### 3.2 THE SIX COMPRESSIBLE POINTS — A **SETUP** FAILURE, AND EXPLICITLY **NOT** A MACH BOUNDARY

All six behave identically. Each ran **one** primal to `Time = 4000` (41 prints at
`printInterval = 100`), then:

| point | `Primal min residual` (tol `1e-8`) | trim.json `CL` / `CD` | `alpha_trim_deg` | `error` |
|---|---|---|---|---|
| `MA288` | 0.8876809362068909 | 1.0 / 1.0 | 4.0 | `Primal solution failed!` |
| `MA400` | 0.7053095414119999 | 1.0 / 1.0 | 4.0 | `Primal solution failed!` |
| `MA500` | 0.7831534560839503 | 1.0 / 1.0 | 4.0 | `Primal solution failed!` |
| `MA600` | **0.8992977830651211** | 1.0 / 1.0 | 3.0 | `Primal solution failed!` |
| `MA650` | 0.7953179757926796 | 1.0 / 1.0 | 3.0 | `Primal solution failed!` |
| `MA685` | **0.6721839062663296** | 1.0 / 1.0 | 2.0 | `Primal solution failed!` |

Each log carries, in order, `Primal min residual <x>` / `did not satisfy the
prescribed tolerance 1e-08` / `Primal solution failed!` — e.g.
`/home/ubuntu/certonomous-runs/MAAOA/MA288/out/trim.log:1576-1578`. The residuals
span **0.672–0.899**; none is within seven decades of the tolerance. `CL = 1.0`,
`CD = 1.0` are the **sentinel** values the failed-trim path writes, not
measurements, and `alpha_trim_deg` is each point's α0 *guess*, never advanced —
**there is no trim angle and no drag on any of these six rows.**

> **⚠ THIS MUST NOT BE FILED AS THE PRE-REGISTRATION'S REGISTERED OUTCOME (B).**
> Outcome (B) registers *"high-Mach points fail to trim/converge — the steady
> subsonic formulation's boundary in Mach at fixed lift"*
> (`MAAOA_PREREGISTRATION.md:87-89`). **There is no Mach boundary here.** The
> failure is **uniform across every Mach on the axis**, including `MA288` — the
> M 0.288 anchor this family has converged many times — and the sibling item
> measured the same failure at **α = 0**, where stall, separation and high
> incidence are all dead as explanations. Filing a uniform setup failure under a
> registered Mach-boundary outcome would **invent a physical boundary that does
> not exist** and put a fabricated finding into the ladder. **The registration is
> honoured by naming the miss, not by fitting the answer to the nearest
> registered box.**

**The triage is CLOSED and is not re-opened here.** It is
`/home/ubuntu/Certonomous/docs/LAB_STATE.md`, dafoam section, block **`S-27`** —
eleven compressible wall-resolved solves, zero convergences, against an
incompressible solve that converges to 1e-8 **on the same mesh in the same item**;
cause class **SETUP/NUMERICS**, not `PHYSICS-FAIL`, and *"this says nothing about
NACA0012 and everything about the case setup."* **No physics inference is invented
here from these six rows**, and this record adds none.

What this item's own logs contribute to that closed triage, and nothing beyond it:

* **Every one of the seven logs, both arms, prints
  `Max aspect ratio = 212103.6706991908`** — one mesh, one item, two solvers.
* **The bounding signature is clean.** All six compressible points bound `p`,
  `rho`, `e` **and** `U` in addition to `nuTilda` (e.g. `MA288`: 80 `p`, 75 `rho`,
  80 `e`, 112 `U`, 41 `nuTilda`); `INCOMP` bounds `nuTilda` and nothing else.
  **`Bounding p<500000` first appears at `MA288/out/trim.log:536`, inside the
  `Time = 1` block (line 526) and before `Time = 100` (line 545) — it is broken
  before it starts, not late-diverging.**
* **Wall treatment is as frozen, on all seven.** Every log carries
  `Setting nut wall BC for wing. BCType=nutLowReWallFunction`; **not one carries a
  Spalding line.** The six compressible points additionally carry
  `Setting alphat wall BC for wingBCType=fixedValue`; `INCOMP` has no `alphat` at
  all, that field being compressible-only. (These are the raw log facts. The
  `G-WALLTREAT` gate itself was **never reached** — `maaoa_read.py:197` sits after
  the refusal.)

### 3.3 `G-YPLUS` — WHAT THE LOGS CARRY, PER POINT. **NO GATE RESULT IS COMPOSED**

Last printed `yPlus … max` per point, and the full swing across that point's
prints. The registered threshold is `y+max ≥ 1.0 ⇒ GATE FAIL` at that point;
**it is stated here for reference and is not applied to anything.**

| point | prints | `y+max` last | `y+max` min over prints | `y+max` max over prints |
|---|---|---|---|---|
| `MA288` | 41 | **6.6296** | 0.121687 | **6.6296** |
| `MA400` | 41 | 2.97702 | 0.231597 | 2.97702 |
| `MA500` | 41 | 1.10956 | 0.257344 | 3.17651 |
| `MA600` | 41 | 1.05263 | 0.366859 | 1.79359 |
| `MA650` | 41 | 1.14623 | 0.293472 | 1.79359 |
| `MA685` | 41 | **0.489152** | 0.419061 | 1.822 |
| `INCOMP` | 138 | **0.0258773** | 0.0235438 | 0.327444 |

**THE SIX COMPRESSIBLE ROWS ARE NUMBERS FROM A FIELD THAT NEVER CONVERGED, AND A
GATE READING TAKEN OFF THEM WOULD BE A DRAW FROM A DISTRIBUTION WEARING A
MEASUREMENT'S CLOTHES.** `MA288` swings 0.122 → 6.630 within one run; `MA685`'s
last print reads 0.489 while the same run touched 1.822 earlier. Which side of 1.0
each point lands on **is a function of which iteration the last print happened to
be**. That is precisely the failure `S-27` §4 records against the upstream stage-1
probe — a gate that consumes one scalar from one iteration of a swinging field —
and this record refuses to repeat it one level down.

**`INCOMP` is the opposite case and it is worth the contrast.** Across its final
primal's 41 prints, `y+max` spans **0.0243462 – 0.0258774** — a 6 % band, a settled
field — and sits **two orders below** the 1.0 threshold. **As a reading, the
wall-resolved claim on the incompressible arm rests on a field that is real.** No
gate is composed from it either.

---

## 4. ONE ROW ONLY — **BY REGISTRATION AND BY HER ORDER, NOT BY OMISSION**

`/home/ubuntu/Certonomous/docs/dafoam/README.md:76` — **R11**: *"a patched grade is
recorded beside a shipped grade and never in place of it."* Two rows is this
family's standing form and a one-row item destroys the only instrument that can
detect a toolchain-dependent result.

**MAAOA ran the PATCHED image ONLY.** Sanaa's order of 2026-09-02, verbatim, from
`/home/ubuntu/Certonomous/etc/sessions/2026-09-02T1900Z_sanaa_fine_sweeps_launch_order.md:37-40`:

> cool a few more things for the dafoam team baout these runs : 1. They should be
> done with the fine mesh 2. The patching needs to happen (parallelization
> transpose fix) 3. This is an immediate request, meaning the box should be filled
> with this aany time soon.

That is registered on the pre-registration's face (`MAAOA_PREREGISTRATION.md:23`,
`:68`) and enforced at runtime: the driver's `G-IMG` refuses any image but
`dafoam-idwarp-rot:v1` (`sha256:2927768a16ac…f6d35`), and it recorded
`MAAOA_G_IMG_PASS dafoam-idwarp-rot:v1 is the PATCHED build` at 18:20:40Z.

**THE SHIPPED ROW IS ABSENT BY REGISTRATION AND BY HER ORDER — IT IS NOT
CLEAN-BY-OMISSION AND IT IS NOT AN OVERSIGHT.** The precedent wording this record
follows is D13's — *"D13 buys the **PATCHED row only**; the **SHIPPED row is NOT
BOUGHT**"*
(`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/curriculum_D13/PREREGISTRATION.md:29`)
— and A3's, *"PENDING everywhere, not clean-by-omission"*
(`/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/grading_confirmation/RESULTS.md:242`;
also `docs/dafoam/README.md:91`). **This item measures nothing whatever about the
shipped build, and claims nothing about it.** A shipped row on this ground is a
successor purchase, made in advance, in a freeze.

---

## 5. COST CALIBRATION (`CLAUDE.md` rule 12)

Sources: `/home/ubuntu/certonomous-runs/MAAOA/COST_MAAOA.txt` and
`/home/ubuntu/certonomous-runs/MAAOA/CHAIN_LEDGER.tsv`. The calibration row is
`/home/ubuntu/Certonomous/docs/COST_CALIBRATION.md`.

**664.0 core-min actual against 315 registered — ratio 2.108.** Item ceiling 900,
not breached; per-point cap 120, not breached (max 110.15). **$0.56772 DERIVED,
NOT MEASURED**, at c7a.4xlarge $0.0513/core-h, **owner-stated, reported-by-owner**
— the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **GPU:
0 GPU-h.** The two aborted pre-compute fires (Amendments 1 and 2) spent **0.0
core-min** on this item and contribute nothing to any figure here.

**BASIS: GROSS. NO CLEANED FIGURE IS PUBLISHED, AND THE REASON IS NAMED.**
`COMPUTE_BUDGET_CHARTER.md` §2's single cleaning rule — *"a ledger row over 3600
wall seconds is an infrastructure stall, not solver cost"* — applied literally
here would match **all seven rows** (5,488 – 6,609 wall s) and clean 664.0 to
**0.0**. That would be false. Every row's own log shows a live time loop
advancing: 41 `Time =` prints to `Time = 4000` on each compressible point, 141
across `INCOMP`'s five primals, with `ExecutionTime` accumulating to within a few
seconds of the ledger wall (`MA288`: `ExecutionTime = 5518.61` against 5,550 wall
s). The 3,600 s threshold was calibrated on a ledger whose solver rows cluster far
below it; **a 130,304-cell wall-resolved np = 1 solve is outside that population**,
and a cleaned figure whose rule mis-fires is *"a judgement wearing a number's
clothes"* — the charter's own phrase. **Gross, labelled gross.**

### 5.1 THE GAP, ATTRIBUTED: **THE MISS IS IN THE RATE, AND THE RATE'S CAUSE IS CONTENTION**

The registered basis (`MAAOA_PREREGISTRATION.md:122-127`): anchors **MEASURED** at
A1WR §13.2 — **0.37163 s/iter compressible**, 0.35625 s/iter incompressible, at
130,304 cells, np = 1; trim primal count **EXTRAPOLATED** and named at the freeze
as *"the term most likely to be wrong"* — ~7,900 iterations/point ≈ **45 core-min
per point**, × 7 = **315**.

**The registered 45 core-min per point implies 0.34177 s/iter**, which is a shade
*below* both stated anchors. That implied rate is the honest denominator for the
decomposition, and it makes the arithmetic exact:

| | iterations actual / predicted | s/iter actual / implied 0.34177 | product | core-min actual / 45 |
|---|---|---|---|---|
| compressible point (mean of 6) | 4,000 / 7,900 = **0.506** | 1.3846 / 0.34177 = **4.051** | **2.051** | 92.31 / 45 = **2.051** ✔ |
| `INCOMP` | 13,422 / 7,900 = **1.699** | 0.4924 / 0.34177 = **1.441** | **2.448** | 110.15 / 45 = **2.448** ✔ |

**On the six compressible points the iteration count was OVER-predicted by 2× and
the miss is entirely in the rate.** Measured **1.3846 s/iter** on the container
wall basis (mean ledger wall 5,538.5 s ÷ 4,000), **1.3778 s/iter** on the solver
basis (mean last `ExecutionTime` 5,511.34 s ÷ 4,000) — **3.73× and 3.71×** the
0.37163 anchor respectively. *(Sanaa's ruling quotes 1.387 s/iter and 3.73×; that
is the container-wall basis and it is right on that basis. Both are given, each
with its basis named.)*

**AND THE CAUSE IS CONTENTION, BECAUSE THE ANCHOR WAS MEASURED AT LOW CONCURRENCY
AND SPENT AT HIGH CONCURRENCY.** This item ran **six** one-core points
simultaneously on cpusets {2–7} while A1WR held **eight** more units on cpusets
{8–15} of the same 16-core box (`MAAOA_PREREGISTRATION.md:137-143`). The
`launcher.queue.out` load averages are the disclosure in the record itself: 4.60
at the first launch, 5.03 by the sixth, and **8.01** by the time `INCOMP` was
launched at 20:08:10Z. **The same box, at a different concurrency, gives a
different ratio**: `INCOMP` ran at **0.4924 s/iter** against its own 0.35625
anchor — **1.38×**, against the compressible arm's 3.71×.

**AND THE HONEST LIMIT ON THAT ATTRIBUTION.** The two arms differ in concurrency
**and** in solver, so this item cannot separate contention from a
compressible-solver cost specific to the wall-resolved mesh. Contention is the
attribution and the mechanism is named; **it is not isolated by a one-variable
measurement here, and this record does not claim it is.**

**THE ONE PLACE SANAA'S RULING NEEDS NARROWING, AND IT IS NARROWED HERE.** *"The
miss is in the RATE, not in the iteration count"* is exactly right for the six
compressible points. **It is only half right for `INCOMP`**, whose spend misses on
**both** terms: 1.699× the iterations *and* 1.441× the rate. The extra iterations
are real and their cause is in §3.1 — five primals ran, and **two of them
(001 and 005) went the full 4,000 to `endTime` instead of stopping at 1e-8.**

**FORWARD RULES THIS ITEM MEASURES, for A1WR L3 (130,304 cells) at np = 1:**

* a **compressible `DARhoSimpleFoam` iteration on the wall-resolved L3 mesh, run
  6-up beside A1WR's 8 units**, prices at **≈ 1.38 s/iter** — measured six times,
  spanning **1.3720–1.3875 s/iter** on the container basis (ledger wall
  5,488–5,550 s ÷ 4,000);
* an **incompressible `DASimpleFoam` iteration on the same mesh, run 1-up**,
  prices at **≈ 0.49 s/iter**;
* **a fixed-lift Newton trim that converges costs ~13,400 primal iterations, not
  ~7,900** — 5 primals over 3 Newton steps, two of them running the full 4,000.
  **The pre-registration named this term as the one most likely to be wrong and it
  was, in the direction it warned about.**

### 5.2 **NAMED SEPARATELY, NEVER FOLDED INTO THE RATIO: 553.85 core-min RETURNED NO GRADABLE DATA**

`COMPUTE_BUDGET_CHARTER.md` §6 requires waste to stay separately named and never
laundered into a cleaning or into a ratio's explanation.

**The six compressible points spent 553.85 core-min — 83.4 % of this item's entire
spend — and returned no gradable row.** ($0.47354 derived, not measured.) Every
one of them wrote a sentinel `CL = 1.0 / CD = 1.0`, no trim angle and no drag.
**This figure is stated on its own line. It is not subtracted from the gross, it
is not folded into the 2.108 ratio, and the ratio is not explained by it.**

**AND IT WAS NOT VALUELESS, WHICH IS A DIFFERENT CLAIM FROM NOT BEING WASTE.**
Those six failures, standing beside `INCOMP`'s convergence on **the same mesh in
the same item**, are one half of the controlled pair that closed the `S-27`
triage. Under the charter's definition it is still solver cost that bought no
gradable row, and it is named as such; **what it bought was a diagnosis, and a
diagnosis is not the thing this item was costed to produce.**

---

## 6. WHAT THIS ITEM DOES **NOT** ESTABLISH

* **It does not establish a verdict of any kind.** The grader refused, `rc = 2`;
  none is supplied here, and the grading path is fixed at the pre-registration
  commit, so none may be substituted.
* **It does not establish a Mach boundary, a drag-divergence Mach number or a
  stall angle.** §3.2. `G-MDD` and `G-STALL` exist to refuse exactly that, and M5
  demonstrated both firing.
* **It does not establish a fixed-lift drag axis.** One point of seven trimmed.
  **There is no `CD(Ma; CL = 0.5)` curve in this item** and none is drawn.
* **It does not establish anything about the SHIPPED build.** §4 — one row, by
  registration and by her order.
* **It does not establish a grid-converged value.** `G-NOBAND`: no Roache triple
  exists on this mesh family, so `CLAUDE.md` rule 5 has no row to act on and **no
  GCI is quoted anywhere in this record.**
* **It does not establish that `INCOMP`'s final primal converged.** §3.1 reports
  both halves — no `satisfied` line, and residuals below tolerance — and composes
  neither.
* **It does not separate contention from a compressible-solver cost.** §5.1.
* **It does not establish anything about `DARhoSimpleCFoam`**, which was not run,
  or at np ≠ 1.

---

## 7. WHAT A SUCCESSOR MUST KNOW

1. **The grading path refused on a fixture-selection precondition, not on a
   physics gate.** `maaoa_read.py:163-167` takes the first *parseable* point log
   as its planted-control fixture. On a sweep where the alphabetically-first point
   can fail, that fixture cannot satisfy M1. **A successor registers the control
   fixture's precondition in advance** — a log known to be trimmable, or a
   writer-built fixture when no completed trimmed point exists — **and registers
   what the reader does when the premise is falsified.** Both instruments here are
   frozen and have had first compute; neither is to be edited.
2. **`S-27` §9, verbatim: *"The wall-resolved compressible ladder is BLOCKED on a
   setup question, not on a physics one, and it is cheap to answer."*** That is
   the board's word about the ladder, not a verdict on this item, which has none.
   `S-27` §9 names the three candidates — relaxation factors
   retuned for the true aspect ratio, the `alphat` wall treatment, and a mesh level
   with a sane aspect ratio — and requires them separated **one variable per run**
   on the already-built L3 mesh. **The discriminating evidence costs a few
   core-minutes, not a campaign.**
3. **The incompressible line is unaffected and is where this family's live results
   are.** `INCOMP` converged, is trimmed as a reading, and its y+ is settled two
   orders below the threshold on a field that is real.
4. **Price the trim at ~13,400 iterations, not ~7,900, and price the rate at the
   concurrency it will actually be spent at.** §5.1.

---

**SUBMISSIONS PARKED.** Nothing in this item is filed, sent, emailed, uploaded,
registered, posted or commented outside this box — not the readings, not the
`S-27` diagnosis, not the cost figures, not this record (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10; `MAAOA_PREREGISTRATION.md:156`).
