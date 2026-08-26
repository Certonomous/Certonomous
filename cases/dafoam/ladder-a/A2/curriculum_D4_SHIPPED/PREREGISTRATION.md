# D4-SHIPPED — pre-registration: **BUY THE SECOND ROW**

**Item id:** `D4-SHIPPED` — the re-buy of `curriculum_D4` on the **SHIPPED** toolchain row.
**Authored** 2026-08-26 by dafoam `lab-lane`, on `dafoam-supervisor`'s authorisation of the
price this lane measured. **Nothing here is sent, filed, uploaded, registered, posted or
commented** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). **No frozen file is edited**
(rule 6): `curriculum_D4`'s pre-registration, grader, launcher and results are **cited by
path and copied, never modified**.

> **ID-NAMESPACE WARNING, carried in the header of every new document in this family.**
> `docs/DOCKET.md:129,130,139,140` carries rows numbered **D5, D6, D14, D15**. Those are
> **fleet SDK/docs defects from the 2026-08-11 B2/B6 audits** — a certificate `unlink`
> swallow, five acts' bare `unlink` outside a `try`, a filming-list referent loss, hand-set
> `reference.yaml` numbers. They are **entirely different objects** from the dafoam
> curriculum items of the same number at `cases/dafoam/EXPERTISE_CURRICULUM.md:95,96,125,126`.
> `docs/DOCKET.md:211` records this exact collision biting twice already. **The two streams
> never touch, and no document in this family may cite a bare `D<n>` without saying which.**

---

## 1. WHY THIS ITEM EXISTS

`DAFOAM_CHARTER.md` §6: **a DAFoam verdict is two rows, shipped and patched, or it is not a
verdict about DAFoam.** `curriculum_D4/PREREGISTRATION.md` §10 bought **PATCHED only**, named
the choice and its consequence before compute, and recorded the second row as **`PENDING` —
not run, not failed** — with its re-buy *"a separate registered item"*. **This is that item.**

**D4, D7R and D8 are all single-row. This family currently holds no two-row verdict.**

## 2. WHAT IS INHERITED **BY CITATION**, AND IS NOT RESTATED HERE

Everything in this block is **taken unchanged** from `cases/dafoam/ladder-a/A2/curriculum_D4/PREREGISTRATION.md`
at the commit that froze it. **It is deliberately NOT copied.** A second copy of a band or a
gate would split the two rows between two definitions of the same threshold, and the whole
evidentiary value of a two-row verdict is that **the two rows were graded by the same rule**.

| inherited | source | value, for the reader's convenience only — **the cited document governs** |
|---|---|---|
| the case | §1 | MACH wing, CD min at fixed CL, 38,304 cells, np=4, twist+shape ~100 DVs |
| bands A–D | §4 | CL per major `5.0e-4`; CL final `1.0e-5`; drag `[25, 45] %`; FD `5.0 %` per component and aggregate |
| the five graded components | §6 | `shape[46]`, `shape[18]`, `shape[0]`, `twist[0]`, `patchV[1]` — **named in advance, by name** |
| the step ladder and plateau rule | §7 | plateau tolerance `10 %` |
| the thirteen gates | §§4–9 | G1–G13, unchanged in name, threshold and label |
| the arm cap table | §8 | P1 `5.0`, P2 `55.0`, O `620.0`, ACC `80.0`, F3 `120.0` core-min |
| the planted-zero control | rule 3 | `PLANT = 1.234e-03`, plant-and-read-back, refusal on a blind reader |
| decomposition | §5 | `scotch`, `numberOfSubdomains 4`; **determinism is not assumed** — arm P1 runs `decomposePar` **twice** and compares the two `processorN` cell-count maps |
| cpuset discipline | §5b | four distinct cores, `--cpuset-cpus`, delivered-cores floor `3.0` of a 4-core quota |

**No band, threshold, cap or label in that table may be altered by this document.** If a
reader finds a number here that disagrees with the cited source, **the cited source wins and
this document is defective.**

## 3. WHAT IS GENUINELY NEW — and it is only these four things

### 3.1 THE ROW IDENTITY IS A HASH, NEVER A VERSION STRING

`DAFOAM_CHARTER.md` §11. A3 rung 2 recorded IDWarp reporting version `"2.6.2"` on the
**patched** stack — **the version string discriminates nothing.** The two rows are separated
by two hashes, **both measured on this box, from two different items' ledgers**:

| row | image | image digest | `libidwarp.so` md5 | measured in |
|---|---|---|---|---|
| **SHIPPED** — bought here | `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **`f0fcb488e0e98156575cd19548e91663`** | `D7R` arm O ledger |
| PATCHED — already bought | `dafoam-idwarp-rot:v1` | `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35` | `85f59e87253e0a71a813f64ca6e4c425` | `D4` arms P1/P2/O/F ledger |

**The launcher refuses on a digest mismatch and the grader refuses on a `.so` md5 mismatch.**
An arm that cannot prove which row it ran is **`NOT A RESULT`**, not a shipped number.

### 3.2 THE `D4-DEF-7` REPAIR — registered here because a new registration is where it belongs

`SUPERVISOR_D4_ACCEPTANCE_AND_D4DEF7.md` §3 found, by reading the code, that
`curriculum_D4/d4_grade.py`'s `g_completion()` **names three clauses and implements one**:
`rc` is written into the output and **never compared to zero**, there is no terminal-statement
check at all, and `main()` composes the verdict from **the age limb alone**. The consequence is
on the graded artifact: `curriculum_D4/ARMF3_d4_grade_verdict.json` carries
`verdicts.G1_completion_and_age = "PASS"` **and** `report.G1_completion.arms.F.rc = 1`
simultaneously, with `F` in `arms_required`. Settled verdicts are not reopened and the remedy
belongs in the next registration. **This is that next registration.**

**All three clauses are implemented and ALL THREE REACH THE VERDICT** in
`d4s_grade.py` (`terminal_statement_ok()`, `g_completion()`, and the composition in `main()`):

1. **`rc == 0`, read from the KERNEL'S OWN RECORD.** `curriculum_D4/PREREGISTRATION.md`:256-257
   registered that the exit comes from `docker inspect .State.ExitCode`, *"the kernel's own
   record, not from the harness's `$?`"*, with `OOMKilled` from the same place — and **this
   lane's audit found that of 36 dafoam launchers containing `docker run`, exactly one
   (`A3/curriculum_D7R/d7r_run_arm.sh`:425) ever implemented it.** A frozen launcher cannot be
   repaired here (rule 6), so the grader does the next honest thing: it reads **both**, requires
   the **kernel's** to be zero, and **REFUSES on a disagreement** rather than silently
   preferring either. `OOMKilled true` fails the clause on a zero exit.
2. **A terminal statement from the producer's own log FILE — POSITIONALLY.** The statement is
   `Finalising parallel run` and it must be **the last non-empty line**.
   **THIS IS REGISTERED IN THIS FORM BECAUSE OF A MEASUREMENT, AND THE MEASUREMENT IS STATED
   BEFORE THE RUN IT GATES.** On D4's four real arm logs:

   | reading | O (rc 0) | F3 (rc 0) | F (rc 1) | F2 (rc 1) | discriminates |
   |---|---|---|---|---|---|
   | substring **anywhere** | yes | yes | **yes** | **yes** | **4 of 4 — NOTHING** |
   | **last non-empty line** | yes | yes | no | no | **2 of 4 — exactly the rc=0 arms** |

   Both crashed arms carry **four** mid-file copies (one per MPI rank) and then **ten further
   lines** of `mpirun detected ... non-zero status` abort text. **The obvious implementation of
   this clause would have passed arm F — the very arm that motivated `D4-DEF-7` — and would
   have been a second dead lever inside the repair.** A missing or unnamed log is a **failed**
   clause, never a passing one.
3. **The age guard**, unchanged, `.d4_age_datum` against `0/U`, strictly newer.

### 3.3 THE DEMONSTRATION — the clauses are shown to fire by MAKING THEM OCCUR

This family's own amendment of 2026-08-25 governs: ***a guard is only shown to work by making
the condition it guards actually occur.*** D4's `29/29 PASS` drove `G1` to `NOT A RESULT`
through the **age limb only**, so it was silent on two thirds of the gate.

`d4s_def7_demonstration.py` runs **7 fixtures under plain `python3` and under `python3 -O`**,
and **four of them use D4's own real arm logs rather than synthetic text**. **RESULT, RECORDED
BEFORE COMPUTE, `rc = 0` under both flags:**

| fixture | verdict, both flags | limb that flipped |
|---|---|---|
| CONTROL, clean | **`PASS`** | rc ✓ terminal ✓ age ✓ |
| arm F's real `rc = 1` | `NOT A RESULT` | **rc** |
| `OOMKilled true` on a zero exit | `NOT A RESULT` | **rc** |
| arm F's real aborted log | `NOT A RESULT` | **terminal** |
| stale artifact | `NOT A RESULT` | **age** |
| harness `$?` 0 vs kernel `1` | **`REFUSED`** | — neither chosen silently |
| log named but absent | `NOT A RESULT` | **terminal** |

**The control passes and each mutant flips exactly one named limb.** *(The control did **not**
pass on the first run — the clean fixture wrote its artifacts in the same second as its datum,
so the strictly-newer age guard failed and every mutant was failing for the control's reason
rather than its own. Caught by running it, repaired, and recorded here rather than quietly
fixed: a demonstration whose clean control fails proves nothing about its mutants.)*

**THE BEFORE/AFTER, which is what proves the repair reaches anything:** on the **same** `rc = 1`
fixture, the **frozen** `curriculum_D4/d4_grade.py` emits **`PASS`** with `{'O': 0, 'F3': 1}`
sitting in its own report, and `d4s_grade.py` returns **`NOT A RESULT`**. **`D4-DEF-7` is
reproduced and repaired, on real artifacts.**

**Neither file contains a single `assert` statement**, checked **by AST on statement type** —
a grep matches `raise AssertionError`, and a behavioural test passes a file whose asserts
happen to hold; **only the statement type distinguishes `assert X`, which `-O` deletes, from
`if not X: raise`, which it does not.**

### 3.4 INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 |
|---|---|
| `d4s_grade.py` | `74841576480992cf21c1cc036537e839` |
| `d4s_def7_demonstration.py` | `7927eafa5e2551b68b317afc0d2db2d4` |
| `d4s_grade_D4DEF7_REPAIR.diff` | the complete difference from the frozen D4 grader, 8 hunks |

The launcher is `curriculum_D4/d4_run_arm.sh` and its siblings, **unmodified**, invoked with
the shipped image. **This item adds no launcher and edits none.**

---

## 4. COST — and the caveat is registered as a caveat, before compute

**PRICED FROM D4's OWN MEASURED `rc = 0` ARMS**, not from arithmetic about them
(`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/{ledger,acc_ledger,f3_ledger}.txt`):

| arm | measured core-min (patched row) | registered cap |
|---|---|---|
| P1 | 0.333 | 5.0 |
| P2 | 36.400 | 55.0 |
| **O** | **511.133** | 620.0 |
| ACC | 3.000 | 80.0 |
| F3 | 47.267 | 120.0 |
| **TOTAL** | **598.133** | **880.0 = `ITEM_CEILING_CORE_MIN`** |

- **ranks 4**; wall **2.49 h** at the estimate, **3.67 h** at the ceiling.
- **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box
  cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED, NOT
  MEASURED**: estimate **$0.5114**, ceiling **$0.7524**.
- **Corroboration, from a document written before this price existed:**
  `curriculum_D4/PREREGISTRATION.md` §10 says both rows are *"~1,200 core-min"* ⇒ ~600 for the
  shipped row. The measured basis **598.133 agrees to 0.31 %**.
- **Excluded from the estimate and named rather than hidden:** arms `F` (1.0) and `F2` (3.733),
  both `rc = 1` — **4.733 core-min of instrument failure already paid on the patched row** and
  repaired by `d4_run_F3.sh`. A re-buy does not re-buy them. Gross patched spend 602.866.

### 4.1 **THE CORE-MINUTE IS AN HONEST UNIT HERE, AND THAT IS MEASURED**

`core-min = wall_s × ranks ÷ 60` overstates the buy if the ranks never got their cores.
**They did.** D7R arm O, np=4 under an explicit `--cpuset-cpus`, measured
**`delivered_cores_mean = 3.9919` of a 4-core quota over 925 cgroup samples — 99.8 % delivery**
(`CURRICULUM-D7R-a3-m6-cdmin/ledger.txt`). **So 598.133 is not inflated by cores the run never
received.** The same row reads **`max_nr_throttled = 52435`**, i.e. the container hitting **its
own** quota ceiling in ~37 % of 100 ms periods — **which is what 99.8 % delivery against one's
own cap looks like, not starvation**, and it would read the same on a re-buy. **That figure is
NOT convertible into lost work**: doing so needs an uncontended control at the same rank count
that this lane **did not buy and does not claim**.

### 4.2 **THE 511.133 IS A LOWER BOUND, NOT A PREDICTION** — registered as such

Arm O's 511.133 core-min was measured **on the patched gradient, at 80 majors**, and carrying
it across assumes **the same 80 majors on a different gradient**. **The shipped gradient is
known wrong on 7 of 96 components, aggregate 1.7138 %, worst `shape[18]` at −360.75 %**
(`curriculum_D4/PREREGISTRATION.md`:62-66), against patched's 0.0506 %. **An IPOPT driver on a
gradient wrong in seven of its search directions may need more majors than 80, or may terminate
early on a line-search failure.** The 880.0 ceiling absorbs a ~72 % overrun on the O arm; beyond
that the runaway guard is what is being bought. **This paragraph is the registered caveat: no
record of this item may quote 511.133 as a prediction that was met or missed without it.**

### 4.3 CAP DISCIPLINE

Caps are **runaway guards that REPORT to the supervisor**, per Sanaa's 2026-08-25 lift, **not
budgets that rigor is trimmed to fit, and not licence to let a known-broken run continue.** A
crossing is written to the ledger and the supervisor decides. A calibration row is owed at
completion in `docs/COST_CALIBRATION.md` (rule 12), stating actual/predicted and attributing
the gap, with **waste named separately, never absorbed into the ratio**.

### 4.4 MEMORY — dafoam is the memory-limited family

**HOLD, do not launch, while `MemAvailable < 16.0 GiB`** for the 12 g arms (container cap plus
~4 GiB host headroom; A3 rung 2 measured peak container RSS **9.263 GiB** at np=4 and D4's four
ranks held ~11.7 GB). **A batch that OOMs is worse than a batch that queues.**

---

## 5. **WHAT A DIVERGENCE MEANS — REGISTERED BEFORE ONE IS SEEN**

**This is the clause the item exists for, and it is written now precisely so that it cannot be
written afterwards.**

If the shipped row's **optimum, drag reduction, or endpoint FD table departs from the patched
row's**, **THAT IS THE FINDING THIS ITEM WAS BOUGHT TO PRODUCE.** It is a measurement that the
toolchain choice reaches the design answer — the strongest possible vindication of
`DAFOAM_CHARTER.md` §6's two-row rule — and **it must not be read, reported or filed afterwards
as a failure of this item, of the shipped toolchain, or of the run.**

**Both outcomes are reportable, and both are registered as reportable now:**

| outcome | label | what it establishes |
|---|---|---|
| the two rows **agree** inside band D | `PASS` on G5, and **D4's optimum becomes toolchain-independent** | the rotation-patch defect does not reach the optimum on this case, and D5/D6/D14 inherit an unqualified result |
| the two rows **diverge** | `PASS` or `GATE FAIL` per the inherited bands — **and a two-row divergence finding in its own right** | the toolchain choice reaches the design answer; every single-row optimisation verdict in this family is qualified by it |
| the shipped driver **fails to converge** or dies on a line search | `NOT A RESULT` for the optimisation, **and a RESULT about the gradient** | a gradient wrong on 7 of 96 directions is shown to be unusable for design, which is itself worth the buy |

**None of these three is a wasted run.** The only wasted outcome is an arm that cannot prove
which row it ran, which §3.1's two hashes exist to prevent.

## 6. WHAT THIS ITEM WILL NOT ESTABLISH

Nothing about a mesh other than D4's 38,304-cell MACH wing; **no grid family, so standing rule 5
has no row to gate and NO GCI IS QUOTED**; nothing about `np ≠ 4`; nothing about the physical
accuracy of the optimum against experiment — the referent is **code-to-code against the patched
row**, not a measurement. **`D5`, `D6` and `D14` (curriculum, not docket) inherit whatever
qualifier this item's outcome leaves standing, and until it completes they still inherit D4's:
patched-only, not toolchain-independent.**

## 7. PREDICTIONS — scored afterwards as HIT or MISS, never adjusted

| id | prediction |
|---|---|
| S1 | arm O costs 400–800 core-min; **511.133 is a lower bound, not a point prediction** (§4.2) |
| S2 | the shipped endpoint FD aggregate over the five registered components exceeds the patched row's 0.1634451673004621 % |
| S3 | `shape[18]` — worst at the shipped baseline, −360.75 % — is **outside** band D at the endpoint |
| S4 | IPOPT prints `EXIT:` in `opt_IPOPT.txt`; whether it is `Optimal Solution Found` is **not** predicted |
| S5 | `G1_completion_and_age` reaches its verdict through **all three** limbs, and the report names which |
| S6 | the `libidwarp.so` md5 inside the shipped container reads `f0fcb488e0e98156575cd19548e91663` |
| S7 | delivered cores ≥ 3.0 of the 4-core quota, mean, on every MPI arm |

## 8. FREEZE

**Committed BEFORE any container starts** (`CLAUDE.md` rule 2; `SUPERVISION_CHARTER.md` §3
check 4, which is the supervisor's own and is **not** discharged by this document). The
grading path is fixed at this commit: `d4s_grade.py` at md5
`74841576480992cf21c1cc036537e839`, verified against its committed blob before grading.
**After first compute the gates are closed**; changes land only as dated addenda that cannot
alter a gate, threshold, cap or label, and originals are struck, never rewritten.

---

# ADDENDUM 1 — 2026-08-26 — **PRE-COMPUTE**, and it adds a launcher

**Version 1.0 → 1.1.** **Lines whose number changed above this section: 0.**

**This is a PRE-FIRST-COMPUTE amendment and `CLAUDE.md` rule 2 is the clause it rests on:**
*"Before first compute, amendments are legal and must state the condition and how it was
checked (name the run directory that does not exist)."*

**THE CONDITION, AND HOW IT WAS CHECKED — not "was checked", the check itself.**
`test -e /home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin` → **ABSENT**,
executed by `d4s_launcher_guard_selftest.sh` as its final check and printed in its output.
**This item has burned 0 core-min and started no container**, so it is before first compute
and **no gate, threshold, band, cap or label is altered by anything below.**

## A1.1 §3.4 WAS WRONG, AND IT WAS WRONG IN THE DESTRUCTIVE DIRECTION

§3.4 said: *"The launcher is `curriculum_D4/d4_run_arm.sh` and its siblings, **unmodified**,
invoked with the shipped image. This item adds no launcher and edits none."* **STRUCK.**

**`D4-LAUNCHER-DEF-1`.** `curriculum_D4/d4_run_arm.sh` hardcodes
`BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin` (`:25`, a plain assignment
with no `${BASE:-…}` override), sets `WORK="$BASE/$ARM"` (`:136`) and runs an **unguarded
`sudo -n rm -rf "$WORK"`** (`:139`) for every arm except F. **Firing the SHIPPED row through it
would have deleted `…/CURRICULUM-D4-a2-wing-cdmin/O` — 5,085 files, 384 MB, holding
`OptView.hst` (16,449,536 bytes) and `opt_IPOPT.txt`: the artifacts D4's ACCEPTED
`GATE REACHED` rests on** — and appended its rows to the same `ledger.txt` (`:282`), leaving
two items interleaved in one file so **neither** row could be graded cleanly afterwards.
**EIGHT launcher files** in that directory carry the same hardcoded `BASE`:
`d4_run_arm.sh`, `d4_run_F2.sh`, `d4_run_F3.sh`, `d4_run_acc.sh`, `d4_stage_ACC.sh`,
`d4_stage_F.sh`, `d4_stage_F2.sh`, `d4_stage_F3.sh`.

**No invocation of those files is safe** — there is no argument, environment variable or
working directory that redirects `BASE`. The repair therefore had to be a new launcher.

## A1.2 THE NEW INSTRUMENTS

| file | md5 | role |
|---|---|---|
| `d4s_run_arm.sh` | ``4b34ad15e986d77b4f8718ebcdc7c022`` | the SHIPPED-row launcher, own run root, own ledger |
| `d4s_launcher_guard_selftest.sh` | ``31087ff6adbbfd037247e31835467812`` | drives the guard against the REAL D4 root |
| `d4s_run_arm_D4LAUNCHERDEF1.diff` | — | the complete difference from the frozen `d4_run_arm.sh` |

**The wrong constant REFUSES; it is not merely different.** A constant that is only different is
one careless edit from being the same again.

- **`G-ROOT.1`** — `BASE` must equal this item's registered root, compared through
  `realpath -m`, so a trailing slash, a `.`, a `..` or a symlink cannot walk around it.
- **`G-ROOT.2`** — an explicit **forbidden-roots list** naming D4's, D7R's, D12R's and D12R2's
  run roots, so the abort says **whose** evidence it just protected.
- **`G-ROOT.3`** — the ledger must belong to this item: any foreign `ITEM=` line, or **any
  `ROW=PATCHED` row**, refuses. A root can be right and its ledger still be a foreign one.
- **`G-ROW`** — **SHIPPED-only.** `DAFOAM_CHARTER.md` §11 makes the hash the identity, so the
  row a run claims and the row it ran must be the same hash or it does not run. The patched
  row is already bought and is not re-bought here.

**THE GUARD IS SHOWN TO FIRE, AGAINST THE REAL D4 ROOT. 12 of 12 checks, `rc = 0`:** it aborts
(exit 3) on `…/CURRICULUM-D4-a2-wing-cdmin`, on the same path with a trailing slash, and on the
same path reached via `O/..`; on D7R's root; on an unregistered path; and on both ledger plants.
**The real D4 root was censused before and after and is UNCHANGED — 261 entries, `O/OptView.hst`
`[1787689205 16449536]` identical.** **NEGATIVE CONTROL: on its own registered root the guard
PASSES and the script stops later for a different reason (exit 64, usage), so it is not a guard
that refuses everything.**

**Two independent barriers, because a test that could destroy what it protects is not an
acceptable test:** the guard completes at `d4s_run_arm.sh:100` and the first **executable**
destructive operation is at `:229` — asserted by parsing the file, not remembered; and every
dangerous invocation passes **no arm argument**, so even with the guard deleted the script
reaches its usage check and exits 64 before staging anything.

**A defect found in this repair, in its own abort path, and fixed before it ran:** the
`G-ROOT.2` message contained **backticks inside a double-quoted string**, which bash
command-substitutes — the guard's own failure path would have executed a bare `rm -rf`. Harmless
in effect, unacceptable in an instrument. Replaced, and the selftest now asserts **zero backticks
on any executable line** of the launcher.

## A1.3 **WHAT `-d` CLOSES, AND WHAT IT DOES NOT — THE CAP EXPOSURE IS REGISTERED OPEN**

The supervisor refused this lane's claim that `docker run -d` plus a polling loop closes both the
`rc` gap and the cap-dies-with-shell defect, and **the refusal is correct and is adopted here
rather than argued with.**

- **CLOSED — `rc` capture.** `rc` comes from `docker inspect .State.ExitCode`, the kernel's own
  record, with `.State.OOMKilled` from the same inspect and **no `--rm`**. This is what
  `curriculum_D4/PREREGISTRATION.md`:256-257 registered and what only
  `A3/curriculum_D7R/d7r_run_arm.sh` had implemented.
- **NOT CLOSED — the cap. `REGISTERED OPEN.`** A foreground `docker run` client is **not** the
  container's parent; **dockerd is**, so containers already survived shell death and `-d` changes
  nothing there. What `timeout` provided was the **cap**, and `timeout` lives in the launching
  shell — **and moving the deadline into a polling loop moves it into the same shell.** On shell
  death the outcome is identical in both designs: **the container runs on, unguarded, with
  nothing left to stop it.** `-d` is an improvement on rc capture and on not blocking the shell.
  **It is not a cap fix and this document does not claim it is one.** Closing it properly needs
  the deadline somewhere that survives the shell — inside the container's entrypoint, or written
  to a file a later poller enforces. **NOT BUILT. Named, and left open.**

## A1.4 A NAMED BOUND ON WHAT CLAUSE 1 PROVES — non-blocking

In `d4s_grade.py`, `oom = str(r.get("oomkilled")).lower()` accepts `"none"`/`"null"` as
parseable and `rc_ok` excludes only `"true"`, so **an absent `oomkilled` reads as
"not OOM-killed"** — the `.get()` absent-versus-`None` collapse. **Non-blocking, and the reason
is structural:** clause 1 already **refuses** when `inspect_exit` is absent, and `oomkilled` comes
from the **same** `inspect(exit,oomkilled)` field, so a row that reaches the OOM test has both
halves; and G11 gates OOM independently from the ledger. **Recorded as a bound on what the clause
proves, not repaired** — the grading path is frozen and a post-freeze edit for no measured defect
is the worse trade.

## A1.5 WHAT IS UNCHANGED

**Every band, threshold, cap, label, gate, component and prediction in §§1–8 stands exactly as
frozen.** The arm caps are unchanged (P1 5.0, P2 55.0, O 620.0, ACC 80.0, F3 120.0, ceiling
880.0); the cost estimate is unchanged at 598.133 core-min; §4.2's lower-bound caveat and §5's
divergence clause are unchanged. **This addendum adds an instrument and strikes one false
sentence. It moves no gate.**
