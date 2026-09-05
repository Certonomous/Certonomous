# A1WRT2 — `SEAM` ARM — RESULTS

**Item:** `A1WRT2`, `SEAM` arm — the wall-resolved α-tail successor's restart-seam probe.
**Registration:** `cases/dafoam/ladder-a/A1/wall_resolved_alpha_tail/A1WRT2_SUCCESSOR_DRAFT.md`,
frozen at **`4e39c370`**; §13 (enqueue) at `6d52f0af`; the queue entry landed at **`a4f71837`**.
**Run root:** `/home/ubuntu/certonomous-runs/A1WRT2`.
**Ran:** 2026-09-05T22:20:44Z → 22:20:48Z. **4 seconds.**
**Written:** 2026-09-06, by a `lab-lane` from the dafoam-supervisor's personally-discharged crash
triage (`SUPERVISION_CHARTER.md` §3 check 2), plus a shared-root-cause investigation and a
family-wide sweep this lane ran and whose results are §5.

> ### VERDICT — `NOT A RESULT`
>
> **The producer died at module import. OpenFOAM never started. No `Time =` line was ever
> written, and no `End`.** There is no measurement here about the restart seam, about
> `startFrom latestTime`, or about anything else physical. **A crash is a finding until triage
> says otherwise, and triage says this one is a harness defect.**
>
> **This is a ONE-ROW `PATCHED` reading** — `ROW=PATCHED IMG=dafoam-idwarp-rot:v1` on the ledger
> row — **and it is not a `DAFOAM_CHARTER.md` §6 verdict about DAFoam at all**, because DAFoam
> was never reached.
>
> **Spend: 0.067 core-min against a 10.0 core-min cap** (0.67 % of cap). No overrun.

**Neither this nor its sibling is a failure of the process.** Sanaa, 2026-09-04: a first
`GATE FAIL` is a waypoint, the case is worked until it passes, **and the gate is never widened to
fit**. This run cost four seconds and surfaced a defect class that no amount of pre-checking had
reached — including this item's own 153-control self-test suite. It is written that way, and not
as a success. **SUBMISSIONS PARKED.**

---

## 1. WHAT HAPPENED

`SEAM/out/rc` reads `1`. `ledger.txt`, in full:

    ARM=SEAM ROW=PATCHED IMG=dafoam-idwarp-rot:v1 rc=1 wall_s=4 ranks=1
    core_min=0.067 cap_core_min=10.0 mode=CONTINUED stamp=20260905T222048Z

`SEAM/out/sweep.log` is **8 lines**. After a benign VSPAERO viewer warning it ends:

| line | content |
|---|---|
| 3–5 | `Traceback (most recent call last):` … `File "/run_root/runScript.py", line 51, in <module>` |
| 6 | `aoa0 = float(os.environ["AOA_ALPHA0"])  # FEASIBILITY: operating point supplied per solve; NOT trimmed to CL_target` |
| 7–8 | `File ".../os.py", line 680, in __getitem__` / `raise KeyError(key) from None` |
| — | `KeyError: 'AOA_ALPHA0'` |

**`line 51, in <module>` is the whole of it.** The read is at **module scope**, so it executes
before any guard *inside* the script can run, and the interpreter exits before OpenFOAM is
invoked. `a1wrt2_seam_watch.out` confirms from the other side, with its own planted control
passing first:

* `CONTROL planted first=4001 last=4200 count=2 … CONTROL PASS — this reader is shown able to see
  an anchored Time line and to reject an indented decoy. Its later zeros are therefore evidence.`
* `OBSERVED sweep.log final: first= last= anchored_count=0 bytes=511`
* `OBSERVED sweep.log End line present: 0`

**`CLAUDE.md` rule 3 is satisfied on the zero:** the watcher was shown able to see a planted
non-zero `Time` line, and only then reported `anchored_count=0`. **The zero is evidence.**

---

## 2. ⚠ THE REGISTERED PREDICTION `P-SEAMTIME` IS **UNRESOLVED**, AND ITS QUANTITY IS **UNMEASURED**

`P-SEAMTIME` was registered before compute with **two** branches and the assertion, verbatim
(draft `:1847`):

> *"first anchored `Time` **4001** and last **4200** → the restart loaded state. **`Time = 1` →
> the producer resets on a `latestTime` start too, `G-COMPLETE` fails `SEAM`, `TAIL` is refused at
> `rc=7`, and the item stops at ≤ 10.0 core-min with the mechanism measured for the first time in
> this family. BOTH ARE RESULTS.**"*

**NEITHER OCCURRED.** The measured outcome is a third one the prediction did not contemplate:
**no `Time` line of any value was ever emitted, because the mechanism was never exercised.**

> **`P-SEAMTIME` is UNRESOLVED. The quantity it predicts is UNMEASURED.**
>
> **A prediction with two branches met a third outcome. That is not a result about the restart
> mechanism and must not be written up as one.** Specifically: **this run says NOTHING about
> whether the producer honours `startFrom latestTime`.** The draft's own §"what this arm buys"
> named that as the single thing `SEAM` exists to measure; it remains **exactly as unmeasured as
> it was before the 0.067 core-min was spent.**

**Consequences, taken and not softened:**

* **`TAIL` stays PARKED.** Its registered precondition is `SEAM`'s verdict, and `SEAM` has not
  produced one about the seam. The precondition machinery is intact and correct — `a1wrt2_run_arm.sh`
  refuses `--arm TAIL` at `rc=7` against a run root whose `SEAM` verdict does not permit it — but
  **an unresolved prediction is not a permission and is not a refusal either**; it is a hole where
  a measurement should be.
* **`G-COMPLETE` did not fail `SEAM` in the sense the prediction described.** The prediction's
  `Time = 1` branch reached `G-COMPLETE` *through a solve*. This arm never reached `G-COMPLETE`'s
  subject at all. Recording it as "the `Time = 1` branch" would be **inventing a limb**, and the
  arithmetic of §12.5's `S1FDP` lesson applies here in its general form: **a falsifier or
  prediction can only be scored against the test it actually met.**

---

## 3. THE DEFECT — AND IT SHARES A ROOT CAUSE WITH THE LOADER DEFECT. IT SHOULD BE NAMED ONCE.

The triage asked whether `KeyError: 'AOA_ALPHA0'` and the earlier finding that *the arm bodies
never sourced the loader* share a root cause. **They do — and the shared cause is sharper than
"same class". It is one deletion.**

### 3.1 The predecessor ran a TWO-LAYER container command. The successor kept only the inner layer.

**`a1wrt_run_unit.sh:665-680` (the predecessor, `A1WRT`, which RAN):**

    docker run -d --name "$NAME" ... \
        -e OMP_NUM_THREADS=1 \
        -e A1WR_MODE="$MODE" -e A1WR_ALPHAS="$ALPHAS" \
        -e A1WR_TOL="$PRIMAL_TOL" -e A1WR_TMO="$TMO" \
        -v "$WORK":/mnt/case -v "$OUT":/mnt/out \
        -v "$BASE/runScript.py":/mnt/runScript.py:ro \
        -v "$BASE/cmd.sh":/mnt/cmd.sh:ro \
        -w /mnt "$IMG" bash -lc \
        "source /home/dafoamuser/dafoam/loadDAFoam.sh && ... bash /mnt/cmd.sh"

The container's entry point is **`cmd.sh`**, not `runScript.py`. And `cmd.sh`
(`/home/ubuntu/certonomous-runs/A1WRT/cmd.sh`) is the layer that does the translation —
**`:57-64`**:

    AOA_MODE="$MODE_FOR_LEDGER" \
    AOA_ALPHAS="$A1WR_ALPHAS" \
    AOA_POINTS_JSON=/mnt/out/points.json \
    AOA_ALPHA0="$FIRST_ALPHA" \
    ... python /mnt/runScript.py -task sweep > /mnt/out/sweep.log 2>&1

**`cmd.sh` also carries two preflight guards of its own** — `:31`, refusing if
`/mnt/runScript.py` is absent at the point of use, and `:42-44`, the `G-WALLTREAT` assertion that
the staged `runScript.py` carries `"useWallFunction": False,`.

**`a1wrt2_run_arm.sh:851-853` (the successor, `A1WRT2/SEAM`, which crashed):**

    timeout 900 docker run --rm --user 0:0 --cpuset-cpus="0" --memory=8g \
      -e OMP_NUM_THREADS=1 -v "$SEAM_CASE:/mnt" -v "$RUN_ROOT:/run_root" \
      "$IMG" /bin/bash -lc "source $DAFOAM_LOADER && cd /mnt && python /run_root/runScript.py -task sweep"

**The successor's arm body is the predecessor's INNERMOST command, transcribed directly, with
`cmd.sh` deleted.** One deletion, and it took four things with it:

| what `cmd.sh` supplied | successor state |
|---|---|
| `source loadDAFoam.sh` — supplied by the predecessor's outer `bash -lc` | **dropped 2026-09-04, RESTORED 2026-09-05** (`a1wrt2_run_arm.sh:828-842` documents the repair) |
| the `AOA_*` environment channel (`cmd.sh:57-61`) | **dropped and NOT restored** — this crash |
| `cmd.sh:31`, the runScript-present-at-point-of-use refusal | **absent from the successor** |
| `cmd.sh:42-44`, **`G-WALLTREAT`** — `"useWallFunction": False,` asserted in the staged script | **absent.** Grepped in this invocation: `WALLTREAT` and `useWallFunction` occur **zero** times in `a1wrt2_run_arm.sh`, `a1wrt2_stage.py` and `a1wrt2_instruments.py`. The draft names the configuration at `:294` and nothing asserts it. |

> **ONE DEFECT, NAMED ONCE.** **`A1WRT2-DEF-ENVSEAM`: the successor's arm body was written as a
> transcription of the predecessor's *innermost* container command, deleting the `cmd.sh`
> indirection layer that supplied its preconditions.** The loader was one casualty. The
> environment channel was a second. Two of `cmd.sh`'s own guards, one of them a registered
> configuration assertion, are a third and fourth and are **still missing**.
>
> **And the 2026-09-05 repair is the part worth keeping.** It restored the loader **because
> driving `measure_image_pins` tripped over `python: command not found`** — a symptom-driven fix.
> It never asked *what else the same deletion had taken*. **A repair aimed at the symptom it
> tripped over will not find the siblings of its own defect**, and here there were three.

**Note the variable names do not even match across the seam:** the predecessor's launcher passes
`A1WR_MODE`/`A1WR_ALPHAS`/`A1WR_TOL`/`A1WR_TMO`; the runScript reads
`AOA_ALPHA0`/`AOA_ALPHAS`/`AOA_MODE`/`AOA_POINTS_JSON`. **`cmd.sh` IS the mapping.** So copying
the predecessor's `-e` block into the successor would *also* have failed — the deleted layer is
not decoration, it is the translation.

### 3.2 Even repaired, `AOA_ALPHA0` alone is not enough

`/home/ubuntu/certonomous-runs/A1WRT2/runScript.py` reads, by AST:

| variable | line | scope | class |
|---|---|---|---|
| `AOA_ALPHA0` | `:51` | **module** | **REQUIRED** — `os.environ[...]`, fatal |
| `AOA_ALPHAS` | `:285` | module | **REQUIRED**, fatal |
| `AOA_MODE` | `:286` | module | **REQUIRED**, fatal |
| `AOA_POINTS_JSON` | `:287` | module | **REQUIRED**, fatal |
| `A1WR_PRIMAL_TOL` | `:60` | module | optional, defaults `"1.0e-8"` |
| `AOA_LEDGER` | `:288` | module | optional, defaults `/mnt/out/LEDGER.tsv` |

**Four fatal reads, all at module scope, and the arm body passes one variable that is none of
them.** Supplying `AOA_ALPHA0` alone buys three more `KeyError`s. **This is stated so that no
successor "fixes" this record's crash by adding a single `-e`.**

### 3.3 ⚠ THE CONTROL THAT SHOULD HAVE CAUGHT IT CANNOT SEE IT, AND THE REASON IS STRUCTURAL

`a1wrt2_run_arm.sh` §8 carries `g_unbound_precondition()` (`:184`) and `unbound_guard()`
(`:244`, armed at `:790`). **They read the launcher for unbound *shell* variables.**

**`AOA_ALPHA0` is not an unbound shell variable. It is an absent *process environment entry*,
consumed by a *python* interpreter, on the far side of a `docker run`.** A shell unbound-variable
check cannot reach across that boundary, and a missing `-e` is not a shell defect at all — the
launcher's shell is entirely well-formed.

> **The check stops at the container boundary and the variable is consumed on the far side.**
> §8's own title already concedes a class of controls that do not work; **this is a member of
> that class the section did not reach.** The item predicted the shape of its own blind spot and
> did not cover this instance of it.

**This is why the sweep in §5 exists**: a defect that a 153-control suite is structurally unable
to see is not repaired by adding a 154th control of the same kind.

### 3.4 A reporting-surface defect, recorded and deliberately NOT changed

`STATUS.queue.A1WRT2_SEAM` reads:

    launcher_rc=0 end=2026-09-05T22:20:48Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc

**`launcher_rc=0` over a crash.** `run_seam_arm()` returns `0` by design, having written the real
`rc=1` to `$SEAM_OUT/rc` and to `ledger.txt` — which is the *correct* propagation discipline
(`a1wrt2_run_arm.sh:858` names and refuses by construction the `a1wr_cmd.sh:96-102` defect of
recomputing status from markers). The field labels itself honestly.

> **An honest label on a field does not repair a surface that a reader scanning statuses will
> misread.** A reader sweeping `STATUS.queue.*` for failures sees `rc=0` on a crashed arm and
> must open a second file to learn otherwise. **Recorded. Not changed** — first compute has
> happened, the run root exists, and this file is a measurement surface, not a scratch note.

---

## 4. STRICT COMPLETION AND THE GATES

| clause (`CLAUDE.md` rule 4) | reading |
|---|---|
| `rc = 0` | **`rc = 1`. FAILS.** |
| an `End` line | **absent** — `a1wrt2_seam_watch.out`: `End line present: 0` |
| last time == `endTime` | **no `Time` line exists at all** — `anchored_count=0` behind a passing planted control |
| fields at `endTime` newer than `0/T` | unreachable |

**Every gate whose input is a product of the solve is `NOT A RESULT` for want of an input.** The
gates that *did* fire fired correctly and are recorded as passing: `MANIFEST.json` was written
(481 bytes) with `image_digest sha256:2927768a…` and `libidwarp_md5 85f59e87253e0a71a813f64ca6e4c425`,
so `G-IMG`/`G-FREEZE` had their input; `measure_image_pins` resolved `python` and returned the
pinned md5, i.e. **the 2026-09-05 loader repair works.**

**`MANIFEST.json`'s `env_declared` field is worth reading against this record:** it lists
`A1WRT2_RUN_ROOT`, `A1WRT2_STATUS_DIR`, `BASH_SOURCE` — **the launcher's own shell environment,
not the container's.** The manifest faithfully declares the environment of the wrong side of the
boundary, which is §3.3's defect showing up a second time in a second instrument.

---

## 5. FAMILY SWEEP — IS THIS CONFINED TO `A1WRT2`?

**Commissioned by the dafoam-supervisor. Method:** every file under
`/home/ubuntu/Certonomous/cases/dafoam/` containing `docker run` (**137 files**, counted in this
invocation); shell variables
expanded (including `${VAR:-default}`); the `-v HOST:CONTAINER` mount table used to map each
container-side python entry path back to a host file; each resolved script parsed with Python's
`ast`, separating **`os.environ["X"]` (fatal)** from **`os.environ.get(...)`/`getenv` (defaulted)**
and flagging module scope. **Named files read one at a time — no multi-file grep** (ugrep races
on multi-file output; `grep -c` exits 1 on zero).

**PLANTED CONTROL (`CLAUDE.md` rule 3), run before any zero below was believed.** The known
non-zero is this item: `A1WRT2/runScript.py:51` reads `AOA_ALPHA0` at module scope while
`a1wrt2_run_arm.sh` passes only `OMP_NUM_THREADS`. The sweep **refuses (exit 2)** unless it sees
that. **It saw it. The control PASSED, and the zeros below are therefore evidence.**
*(The control earned its keep: the first version of the resolver matched `runScript.py` by
basename, hit 59 candidates across run roots, silently picked the wrong one and reported
A1WRT2 clean. That false zero is exactly what rule 3 exists to catch.)*

### 5.1 Result

**47 container entry-script references across the family. 37 resolved to a host file. 10
unresolved. READ-BUT-NOT-PASSED (required): 2 items.**

| item | launcher | entry script | `-e` passed | **READ, NOT PASSED (fatal)** | conditionally forwarded | optional, not passed |
|---|---|---|---|---|---|---|
| **`A1WRT2`** | `ladder-a/A1/wall_resolved_alpha_tail/a1wrt2_run_arm.sh` | `/run_root/runScript.py` → `/home/ubuntu/certonomous-runs/A1WRT2/runScript.py` | `OMP_NUM_THREADS` | **`AOA_ALPHA0`, `AOA_ALPHAS`, `AOA_MODE`, `AOA_POINTS_JSON` — all 4 at MODULE scope** | none | `A1WR_PRIMAL_TOL`, `AOA_LEDGER` |
| **`D13`** | `ladder-a/A1/curriculum_D13/d13_run_arm.sh` | `d13_opt_runScript.py` | `IMG`, `OPT`, `TASK`, `TMO` | **`D1_ENDPOINT_IN` — MODULE scope** | `D13_START_ID` (MODULE) | `D1_ETA`, `D1_ENDPOINT_JSON`, `D1_ENDPOINT_OUT` |
| **`D2`** | `ladder-a/A1/curriculum_D2/d2_run_arm.sh` | `d1_opt_runScript.py` | `IMG`, `OPT`, `TASK`, `TMO` | **zero** | `D1_ENDPOINT_IN` (MODULE) | `D1_ETA`, `D1_ENDPOINT_JSON`, `D1_ENDPOINT_OUT` |
| every other resolved reference | 34 references | — | — | **zero** | — | — |

**31 of the 37 resolved entry scripts read NOTHING from `os.environ` at all** — they are
argparse-driven, and the boundary carries no state for them to lose. **That is a genuine zero and
it is stated as one.** The families in that set include D4/D4_SHIPPED, D5, D6/D6R/D6RF2,
D7/D7F/D7R, D8, D9, D10, D11, D12, S1_fd_plateau, W4, A3 rungs 1 and 3, and the A5 probes.

### 5.2 The third state, which the sweep found and which is not the same defect

`D2` and `D13` do **not** hard-code `-e`. They build a forward list:

    ENVS=""
    for v in D1_ETA D1_ENDPOINT_JSON D1_ENDPOINT_IN D1_ENDPOINT_OUT; do
      if [ -n "${!v:-}" ]; then ENVS="$ENVS -e $v=${!v}"; fi
    done

**Forwarded if the caller set it; silently omitted if not, with no message either way.** That is
weaker than a hard pass and stronger than `A1WRT2`'s nothing, and it is reported in its own
column rather than conflated. **`D13` additionally has one genuinely fatal gap:
`d13_opt_runScript.py` reads `D1_ENDPOINT_IN` at module scope — a `D1_`-prefixed name inherited
from `d1_opt_runScript.py` — and `D13`'s forward loop lists only the three `D13_`-prefixed names.
The prefix changed and one read did not.**

### 5.3 What the sweep could not check, stated rather than omitted

**10 unresolved references, and all 10 are the same file: `genMesh.py`**, in
`d12r_/d12x_/d12y_/d12e_/d12f_/d12_/w3s_stage_and_run.sh`. It is not on the host; it ships inside
the container image, so this sweep cannot read it and **makes no claim about it in either
direction.**

Also not established: whether any launcher supplies the environment by a route this sweep does
not model (`--env-file`, a `docker exec`, an entry script that re-execs). None was observed; none
was searched for exhaustively.

### 5.4 What was NOT done, deliberately

> **No launcher was edited.** First compute has happened on `A1WRT2` and its gates are closed;
> and on every other item a launcher edit is a change to a measurement instrument, which the
> supervisor must read as a diff before its output is believed (`SUPERVISION_CHARTER.md` §3
> check 1). **The set differences are reported and this lane stopped.**

---

## 6. COST — MEASURED, AND WHY NO RATIO IS FILED

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Dollars DERIVED, never measured.**

| | value | basis |
|---|---|---|
| predicted | **3.10344 core-min** | the queue row that cites the registration, `verification/queue/dafoam/launched/A1WRT2_SEAM.json`; the draft's own SEAM term is **1.539 core-min = 200 it × 0.46178 s/it** (the `A-CONT` measured rate) plus staging |
| cap | **10.0 core-min** | `ledger.txt` `cap_core_min=10.0`; arm cap from `a1wrt2_run_arm.sh:116` |
| **actual** | **0.067 core-min GROSS, MEASURED** | `ledger.txt`: `wall_s=4 ranks=1` → `4 × 1 ÷ 60 = 0.0667` |
| cleaned | **= gross** | wall 4 s; the 3600-s stall rule matches nothing |
| derived $ | **$0.00006** | `0.067 ÷ 60 × 0.0513` |
| cap fraction | **0.67 %** | no overrun |

> ### ⚠ NO ESTIMATE-VERSUS-ACTUAL RATIO IS FILED FOR THIS ARM, AND THE REFUSAL IS THE ROW
>
> `0.067 / 3.10344 = 0.0216` is computable and **is not filed as a calibration ratio**, because
> **the estimate's model was never exercised.** The 3.10344 figure prices **200 solver iterations
> at 0.46178 s/it**. **Zero iterations ran.** The producer died at module import, before
> OpenFOAM was invoked. A ratio of 0.0216 would enter the ledger as evidence that this family
> over-estimates by 46× — **and it is evidence of nothing but that a python interpreter exits
> quickly.**
>
> **The honest row is: a crash at 0.067 core-min, with the estimate UNTESTED**, and that is what
> is filed in `docs/COST_CALIBRATION.md`. **Waste: 0.000 core-min**, named separately per
> `COMPUTE_BUDGET_CHARTER.md` §6 — the four seconds bought §3's root cause and §5's sweep.
>
> **This is deliberately treated differently from `D6RF3`'s row**, whose arm *did* run a primal
> to its `endTime` and whose ratio therefore has a (truncated) referent. **One rule applied to
> both would have been wrong in one of them.**

**The forward-useful calibration fact, which is measurable:** an `A1WRT2` container that fails at
python import costs **≈ 0.067 core-min at ranks 1**, essentially all of it container frame.

---

## 7. LEDGER OF WHAT IS AND IS NOT ESTABLISHED

**Established by this run:**

1. `A1WRT2-DEF-ENVSEAM` (§3.1) — the `cmd.sh` deletion, its four casualties, two still open.
2. §3.3 — the shell unbound-variable control cannot see across the container boundary.
3. §3.4 — `STATUS.queue.A1WRT2_SEAM` reads `launcher_rc=0` over a crash.
4. §5 — the family sweep: **2 items with fatal read-but-not-passed, 1 more with a conditional
   forward, 31 of 37 resolved scripts genuinely clean, 10 unresolvable and said to be so.**
5. The 2026-09-05 loader repair **works** — `measure_image_pins` resolved `python` and returned
   the pinned `libidwarp.so` md5.

**NOT established, and nothing in this record may be read as establishing it:**

1. **Whether the producer honours `startFrom latestTime`.** `P-SEAMTIME` UNRESOLVED, quantity
   UNMEASURED.
2. Anything about the restart seam, the α-tail, `G-COMPLETE` on a real solve, or `TAIL`.
3. Whether `G-WALLTREAT` holds for the successor's staged case — **nothing asserts it** (§3.1).
4. Whether the `D13` gap has ever fired in a real run — not investigated; the launcher was not
   edited and no `D13` run was re-read.

**`TAIL` is PARKED.** Its precondition is `SEAM`'s verdict and `SEAM` has not produced one.

**SUBMISSIONS PARKED.** Nothing in this item is sent, filed, posted, uploaded or commented
anywhere outside this box.
