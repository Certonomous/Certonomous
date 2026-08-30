# R4 — PRE-REGISTRATION: THE QUEUE-VALIDATOR LAUNCH-TARGET REPAIR, as a frozen, capped, schedulable REPAIR ITEM

**Team:** cfd. **Owner:** cfd-supervisor. **Registering lane:** cfd lane **R45**, 2026-08-28.
**Status at writing: FROZEN ON COMMIT. No code exists. Zero compute has been spent.**
**Verdict at registration: `PENDING`** — fully specified, fully capped, schedulable, and
sequenced behind R2 (§11 precondition P1). It is not `BLOCKED`: no clause outside cfd's
ownership stands in its way.

**Authority for registering a repair as a queue item.** Sanaa's amendment of 2026-08-28T17:01Z,
verbatim: *"the finding-repairs are the queue: they're frozen, capped, schedulable work items like
any case"*, and *"Freeze-ahead counts repair-registrations; a team blocked on findings freezes the
repairs and runs them — queue depth 0 with open findings is impossible by definition."*
**Measured by this lane at 2026-08-28T17:38Z: `verification/queue/cfd/*.json` → 0 entries.**

**Model and house style:** `verification/campaign/R1_F3S_SELECTOR_REPAIR_PREREGISTRATION.md`,
`R2_QUEUE_HOST_SCOPE_REPAIR_PREREGISTRATION.md` and `R3_COMMIT_RENAME_MODE_PREREGISTRATION.md`,
all three frozen at commit **`f7da1a24ca8c730d5c49a7ea429840c43378bf1e`**, verified by this lane
to be an ancestor of HEAD `1f74d6de1780c4cac36d7a1539ecde97266fd23d` at 2026-08-28T17:30:10Z.

---

## 1. WHAT THIS ITEM IS, IN ONE PARAGRAPH

`scripts/queue_entry_check.py` can return **success without having validated the thing that
decides whether a launch can work**, in three distinct ways. It never checks that the argv's
launch target exists on disk (`check_schema` at `:171` validates only that `launch_cmd` is a
non-empty list of strings); it never checks that a directly-executed target is executable; and
its `main()` at `:1207-1209` returns **rc 0** when the input set is empty. All three are one
failure wearing three coats — **the validator reporting success without having validated
anything** — which is why they are one registration, one selftest and one cap rather than three.
This item adds a `LAUNCH-TARGET` clause and a non-empty-invocation refusal, and proves by control
that neither becomes a blanket refusal. **It authorises no solver compute.**

## 2. WHAT THIS LANE MEASURED — and THREE STATEMENTS IN THE BRIEF THAT ARE FALSE

Every figure below was read from one named artefact per check, in this lane's own invocations
between 2026-08-28T17:30Z and 17:40Z, at HEAD `1f74d6de`. Worktree copies of both instruments
were confirmed identical to their HEAD blobs by `git rev-parse HEAD:<path>` against
`git hash-object <path>` — the only index-immune comparison, because the shared index currently
stages ~300 whole-file deletions and `git status`, `git diff` and `git ls-files` all misreport.

### 2.1 THE DEFECT IS REAL AND IS AS STATED

`scripts/queue_entry_check.py` contains **no test of any element of `launch_cmd` beyond its
type**. `check_schema` (`:171-243`) rejects a shell-string `launch_cmd` and a non-list, and stops
there. No clause in `CHECKS` (`:414-422`) opens, stats or resolves a launch target. An entry
naming an absent script therefore validates **rc 0**, the runner launches it at
`queue_runner.py:498-503`, the wrapper dies, and `launcher_rc` lands behind a `LAUNCHED` record —
the L-344 class.

**It is not hypothetical for cfd right now, and this lane measured exactly how far it reaches.**
Over **133 queue entries** — every `*.json` under `verification/queue/*/`,
`verification/queue/*/*/` and `verification/campaign/queue_entry_*.json` — resolved by the
algorithm of §3, **exactly three have an absent launch target, and all three are cfd's R1/R2/R3
held entries.** No other entry in the lab, in any team, names a target that is not on disk. The
defect is therefore **LATENT lab-wide and ARMED for exactly the three items cfd froze today**,
which is precisely what R1 §11, R2 §11 and R3 §11 each warned of in their own enqueue
preconditions.

**Independent corroboration that another team already works around it by hand:** three
verification-team entries — `verification/queue/verification/VR2_ORDERING_ARM_MONITOR.json:3`,
`VR3_GUARD_SET_ATTRIBUTION.json:3` and `VR4_EXEC_HOST_CONTROL.json:3` — each carry a field
`"_launch_cmd_asserted"` whose text says the target *"was asserted PRESENT and READABLE on disk at
enqueue time by the enqueuer, because `scripts/queue_entry_check.py` does NOT"* check it. A manual
workaround written into three entries by a second team is the strongest available evidence that
the gap is felt and not merely notional.

### 2.2 FALSIFICATION 1 — **`launch_cmd[1]` IS NOT THE SCRIPT IN 65 OF 133 ENTRIES (49 %)**

The brief states that *"`[1]` is usually the script"* and directs that the check be built on it.
**A check written literally on `launch_cmd[1]` would be a fleet-wide false-refusal engine, not a
repair.** Measured shapes, over all 133:

| shape | count | example argv | what `[1]` actually is |
|---|---|---|---|
| interpreter + script | **68** | `["bash", "/…/run_vmfl063.sh", "/…/VMFL063"]` | the script |
| **bare executable at `[0]`** | **62** | `["/…/run_one_t18.sh", "--case-dir", "/…/T18_CU_m", "--timeout", "1200", …]` | **the flag `--case-dir`** |
| **wrapper chain** | **3** | `["setsid", "nohup", "bash", "/…/d4s_chain_driver.sh", "ACC", "F3"]` | **`nohup`** |

The 62 bare-executable entries are heat-transfer's `run_one_t*.sh` / `launch_*.sh` family and
`scripts/launch_k0f_ext1.sh`. For every one of them `launch_cmd[1]` is the literal string
`--case-dir`, which resolves against `cwd` to a path that does not exist and never will. **A
literal `[1]` check would refuse 62 valid entries across the heat-transfer and F14 ladders, and
would simultaneously miss the script entirely in the 3 dafoam `setsid nohup bash …` entries,
testing `nohup` instead.** The clause as the brief words it is wrong in *both* directions at once.
This is the correction this item exists to make before, not after, the code is written.

### 2.3 FALSIFICATION 2 — **EXECUTABILITY MUST NOT BE REQUIRED OF AN INTERPRETED TARGET, AND THE COST OF GETTING THAT WRONG IS 38 ENTRIES**

The brief warns against over-refusal in principle. **Measured:** of the **65** interpreter+script
targets present on disk, **38 are NOT executable** (`os.access(…, os.X_OK)` → `False`) and are
launched perfectly well because `bash` reads them. Requiring `X_OK` uniformly would refuse 38
currently-valid entries. Conversely all **62** bare-executable targets **are** `X_OK`, so the
executable limb has, today, **zero** live positives — it is a guard against a future entry, and
§6's mutation control is what keeps it honest rather than decorative.

### 2.4 FALSIFICATION 3, OWED TO THE SUPERVISOR'S OWN THIRD CLAUSE — **THE EMPTY-INVOCATION PASS IS NOT LATENT; IT IS REACHABLE TODAY THROUGH THE VALIDATOR'S OWN DOCUMENTED USAGE**

The supervisor's mid-task referral (2026-08-28T17:3xZ) reports the empty-argv rc 0, and **narrows
the realisation claim correctly**: under this box's default `bash` a non-matching glob passes the
literal unexpanded pattern through and the validator **refuses rc 2**. This lane reproduced both,
bare, with the rc read on the bare command and never off a pipeline:

- `python3 scripts/queue_entry_check.py` → **rc 0**, *"No entries given. Nothing to validate;
  nothing was launched."*
- `python3 scripts/queue_entry_check.py verification/queue/cfd/*.json` (default shell) → **rc 2**,
  `SCHEMA: cannot read …/*.json`.
- the same line with `shopt -s nullglob` → **rc 0**.

**But the narrowing is one route too narrow.** The supervisor lists the reachable callers as
`nullglob`/`failglob`, a `find`-built empty list, a Python or CI caller passing `[]`, and a bare
invocation. **A fifth route needs none of those and is the instrument's own documented usage.**
`queue_entry_check.py:59` advertises `python3 scripts/queue_entry_check.py --dir
verification/queue/cfd`. Measured this invocation, with cfd's drop path holding **0** entries:

    python3 scripts/queue_entry_check.py --dir verification/queue/cfd   →   rc 0
    "No entries given. Nothing to validate; nothing was launched."

`--dir` on a directory that **exists and holds zero `*.json`** falls through `:1203-1207` into the
same `if not paths:` return. **No `nullglob`, no `find`, no programmatic caller — the documented
command, on the current tree, returns success having validated nothing.** Classification is
therefore **REALISED THROUGH `--dir`, LATENT THROUGH EVERY OTHER ROUTE**, and it should be
recorded that way rather than as latent.

**Caller sweep, with its own control.** Over the 5,4xx tracked files enumerated by
`git ls-tree -r --name-only HEAD` (never `git ls-files`, which reads the poisoned shared index),
**79 files mention `queue_entry_check`**. Every non-prose mention was opened and read. Result:
- **`shopt -s nullglob` appears in exactly two tracked scripts** — `scripts/audit_transcripts.sh`
  and `scripts/audit_camera_discretion.sh` — and **neither mentions the validator** (`grep -c` on
  each returned **0**). **No caller in this repository both sets `nullglob` and invokes it.**
- **The only programmatic caller is `scripts/queue_runner.py`**, which imports the module at
  `:108` and calls `qec.validate()` directly from `tick()` at `:702`. **It never enters `main()`**,
  so the empty-invocation clause cannot affect the runner in either direction.
- Every remaining mention is prose, a `_schema_note` string in an entry, or a usage line.

*The sweep is shown able to see a real hit rather than measuring its own regex:* it found the
three verification `_launch_cmd_asserted` fields of §2.1 and the runner's own `import
queue_entry_check as qec` at `:108` — both genuine, both load-bearing, neither guessed.

### 2.5 THE BASELINE THIS ITEM MAY NOT REGRESS, MEASURED TODAY

    python3 scripts/queue_entry_check.py --selftest   →   rc 0, "SELFTEST PASS: 31 controls
                                                          fired, each shown able to fail",
                                                          0.50 wall s
    python3 scripts/queue_runner.py   --selftest      →   rc 0, "SELFTEST PASS: 41/41 checks,
                                                          0 asserts", 5.24 wall s

**Both taken in this lane's own invocation, rc read on the bare command with output redirected to
a file — never `cmd | tail; echo $?`, which reports `tail`'s status.** The runner's selftest was
run only after reading its isolation: it works exclusively inside `tempfile.mkdtemp(prefix=
"queue_runner_selftest_")` (`:772`), removes only that tree (`:1376`), holds no literal reference
to the real queue root anywhere in `:772-1376`, and sends `SIGTERM` only to a scratch-root daemon
it spawns itself (`:1083`). **The live daemon `pid 1120800` was verified alive before (elapsed
1-00:01:13) and after (1-00:01:47) the run.** R2 §9.1 term (c) declined to take this measurement
and carried a 40.0 s allowance for two runs; the truth is **10.5 s**, so R2's largest term is high
by a factor of **3.8**. R2 is frozen and this lane does **not** amend it — the figure is recorded
here and belongs in `docs/COST_CALIBRATION.md` at R2's completion, as the attributable share of
its ratio.

*A reading error of this lane's own, recorded because it is the same class:* a first attempt to
count the validator's controls with `grep -c '^  ok   '` returned **0** — that instrument prints
its controls in a different shape and publishes its own summary line. **A count that returns zero
on a suite known to have 31 controls is measuring its own regex.** The figure above is the tool's
own final line, not this lane's grep of it.

## 3. WHAT EXACTLY IS CHECKED — THE RESOLUTION RULE, DERIVED FROM THE ENTRIES ON DISK

**The clause does not index `launch_cmd`. It resolves a LAUNCH TARGET**, left to right, from the
argv as a whole:

1. Skip a leading token whose **basename** is a known process wrapper — `setsid`, `nohup`,
   `stdbuf`, `nice`, `ionice`.
2. Skip `timeout` **and its one following non-flag token** (the duration).
3. Skip `env` **and any following `NAME=VALUE` assignments**.
4. Skip a token whose **basename** is a known interpreter — `bash`, `sh`, `dash`, `zsh`, `ksh`,
   `python`, `python3`, `python3.N`, `perl`, `ruby` — and **record that an interpreter was seen**.
5. Skip any token beginning `-`.
6. **The first token that survives is the LAUNCH TARGET.**

Basenames are matched so that `/usr/bin/env` and `/bin/bash` behave as `env` and `bash`.

**Driven over all 133 entries on disk in this invocation, this rule resolved a target for
133/133 with ZERO not-path-shaped results and ZERO false refusals**: 68 interpreter+script,
62 direct-exec, 3 absent (cfd's R1/R2/R3, §2.1). The 3 dafoam `setsid nohup bash …` entries
resolve to `d4s_chain_driver.sh` / `d7fr_run_arm.sh` correctly; the 62 heat-transfer entries
resolve to `argv[0]`, not to `--case-dir`.

**The fail-safe direction is designed in, not discovered later.** If no token survives, or the
surviving token contains **no `/`** — a bare name resolved through `PATH`, e.g. the selftest's own
`["simpleFoam", "-parallel"]` at `queue_entry_check.py:574` — the clause reports
**`NOT EVALUATED`** and **never a refusal**, because the runner's launch environment sources an
OpenFOAM `bashrc` and its `PATH` is not the validator's `PATH`. A refusal derived from the wrong
process's environment would be a well-formed wrong answer, which is the exact class this lab lost
a day to. **Measured: 0 of 133 live entries take this branch**, so it costs nothing today and
exists so that the first entry that does take it is reported rather than guessed at.

### 3.1 Existence versus executability — which test, and why

| target shape | test | reason |
|---|---|---|
| an interpreter was seen before the target (`bash s.sh`, `setsid nohup bash s.sh`) | `os.path.isfile` **and** `os.access(R_OK)`. **`X_OK` is NOT required** | the interpreter reads it. **38 of 65 such targets on disk are not executable and launch correctly** (§2.3). Requiring `X_OK` here is the over-refusal the brief warns against, quantified |
| no interpreter seen — the target is executed directly (`/…/run_one_t18.sh --case-dir …`) | `os.path.isfile` **and** `os.access(X_OK)` | the runner's inner shell `exec`s it; a non-executable file here dies with rc 126 |
| target is not path-shaped, or none survives | **`NOT EVALUATED`**, reported in its own channel | `PATH` at validation time is not `PATH` at launch time |

### 3.2 Relative versus absolute, and the boundary with R2

A relative target resolves against `entry["cwd"]` — `os.path.normpath(os.path.join(cwd, target))` —
because that is what the runner does: `queue_runner.py:502` builds `cd '<cwd>' && <argv>` and
`:509` calls `Popen(..., cwd=str(cwd))`. **Measured: 0 of 133 entries carry a relative target**;
every one is absolute. The rule is registered anyway so that the first relative one is resolved
the way the runner resolves it rather than against the validator's working directory.

**When `cwd` itself is absent, this clause reports `NOT EVALUATED` and issues NO refusal.** That
condition already has an owner: `check_cwd_launchable()` refuses it under the word `EXEC`
(`queue_entry_check.py:330-357`), under ruling **R-AGE-CWD clause 2** in
`docs/standards/QUEUE_ENTRY_VALIDATOR_RULINGS.md`, and R2 §2 re-verified that clause is the one
that produces the eviction. **A second refusal for the same fact is a duplicate, and the
`TEAM-BINDING` clause's own docstring (`:390-392`) already fixes the lab's rule that a condition
refused by one clause is not reported twice.** R4 defers; it does not restate and does not
re-litigate.

## 4. HOST-SENSITIVITY — CONSISTENT WITH R2 BY CONSTRUCTION, NOT BY RESTATEMENT

`LAUNCH-TARGET` reads **this box's** filesystem. For an entry declaring a foreign `host` the
target exists on the other box and not here, so the clause is **host-sensitive in exactly the way
`EXEC` and `AGE-GUARD` are**, and R2's ruling governs it without amendment:
`docs/standards/QUEUE_ENTRY_HOST_SCOPE.md` §4.2, frozen at
`ed77957c4e56cd12e1d5d0c620b218805bd4306b` — **candidate (a): SKIP, report `NOT EVALUATED` in its
own channel, NEVER `PASS`.**

**The mechanism is inheritance, not duplication.** R2's repair introduces the host-scope predicate
and the `unevaluated` reporting channel and applies it to a **named set** of host-sensitive
clauses. **R4 adds `LAUNCH-TARGET` to that set and adds nothing else.** It writes no host
predicate of its own, no second `unevaluated` list, and no independent notion of "foreign". If
R2's set is repaired or narrowed later, R4 follows automatically; a copy would not. This is why
P1 in §11 sequences R4 behind R2 rather than beside it.

`NOT EVALUATED` remains a **clause-reporting token and never a verdict** — R2 §3, unchanged here.
It is not one of the six words of standing rule 1 and never appears on a result row.

## 5. THE THIRD CLAUSE — NON-EMPTY INVOCATION, AND THE EXIT CODE

**Why it is in R4 and not a fourth item.** Both defects are the same proposition failing: *the
validator returned success without having validated anything.* An absent launch target means it
validated an entry it could not have launched; an empty input set means it validated nothing at
all. One clause family, one selftest, one cap. The supervisor's framing is adopted verbatim in
substance and is recorded here so a reader is not left to infer the grouping.

**THE REGISTERED BEHAVIOUR.** `main()` returns a **new, distinct exit code 3** whenever the
resolved input set is empty, in either of its two forms, with a message naming which:

- **no positional entries and no `--dir`** → *"REFUSED: no entries given. This instrument
  validated NOTHING; rc 0 would say it validated everything given."*
- **`--dir <d>` where `<d>` is a directory holding zero `*.json`** → *"REFUSED: `--dir <d>` holds
  0 entries. Nothing was validated."*

**THE EXIT CODE, ARGUED.** The supervisor's leaning is a distinct code and this lane **adopts it,
on a stronger reason than the one offered, and the reason is what makes the refusal safe at all.**

`rc 1` is already taken and means something adjacent but different: `:1198` returns **1** for
`--dir <path that is not a directory>` — a **malformed argument**. `rc 2` means **the entries you
gave me are bad**. "You gave me a well-formed input set that is empty" is neither: the arguments
parsed, the directory existed, and there was simply nothing in it. Collapsing it into 2 tells a
caller its entries failed when it has none, and collapsing it into 1 tells a caller its arguments
were malformed when they were not — each re-creates the ambiguity somewhere else, which is the
supervisor's objection and it is correct.

**And the distinct code is what answers the strongest objection to refusing at all.** An empty
team queue is the *normal* state — cfd's drop path held **0** entries when this document was
written — so a health-check poller running the documented `--dir verification/queue/<team>` would
begin erroring on the ordinary case. That objection is fatal to `rc 2` and **not** fatal to `rc 3`:
a poller reads 3 as *"empty, and that is a fact about the queue, not about the entries"* and can
act on it correctly, while still never mistaking it for *"validated, all good"*. **The choice of a
distinct code and the decision to refuse are therefore the same decision**, and neither survives
without the other. `rc 3` is registered.

**What is NOT changed:** `--selftest` keeps its own exit path (`:1185-1186`) and is untouched;
`--dir <not a directory>` keeps **rc 1**; a non-empty set with failures keeps **rc 2**; a
non-empty set that passes keeps **rc 0**.

## 6. THE OBSERVABLE — AND IT IS NOT A RICHARDSON QUANTITY

**The observable is the CONTROL OUTCOME VECTOR** `(L1 … L13)`, each element one of `FIRED` /
`HELD` / `FLIPPED` / `NOT RUN`, taken together with the two set-equality readings of L13.

**Stated explicitly, so it cannot later be asked for:**

- There is **no grid triple**, no refinement ratio `r`, no mesh, no field, no level.
- **NO OBSERVED ORDER OF ACCURACY IS COMPUTED** and none will be reported.
- **NO GCI IS COMPUTED OR QUOTED**, at `Fs = 1.25` or any other factor.
- `scripts/roache_triple.py` is **not called**. Standing rule 5 is **INAPPLICABLE** to this row —
  not waived, not satisfied — because rule 5 grades a row that has a grid triple and this row has
  none. The in-family precedent for saying so is
  `cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md` §4, and it is the same precedent R1 §3,
  R2 §3 and R3 §3 each cite.
- The counts in §2 (133, 68, 62, 3, 38, 31, 41) are **census readings of a tree at a stated
  commit**, not physical quantities. No uncertainty interval is attached to them and none is
  meaningful; their shelf life is one commit.

## 7. THE REGISTERED GATES — fixed before the work runs

| gate | statement | verdict if met | verdict if not |
|---|---|---|---|
| **G-R4-1 — THE POSITIVE CONTROL FIRES (L1)** | An entry identical to a real launched entry except that its launch target is **absent**, driven through the **real** `validate()`, returns **exactly one** failure opening `LAUNCH-TARGET:`, and that string contains the entry's `case_id`, the **full argv as a list**, the **resolved absolute path**, and the literal word `absent` | required for **PASS** | **GATE FAIL** — the defect was never demonstrated, so nothing was shown repaired |
| **G-R4-2 — THE NEGATIVE CONTROL: A PRESENT TARGET IS STILL ACCEPTED (L2)** | The **otherwise byte-identical** entry with a **present** target returns **zero** `LAUNCH-TARGET:` failures through the same `validate()` | required for **PASS** | **GATE FAIL** — a repair that refuses everything passes any positive control |
| **G-R4-3 — ALL THREE ARGV SHAPES RESOLVE (L3+L4+L5)** | L3 interpreter+script, L4 bare-executable-at-`[0]` with `--case-dir` at `[1]`, L5 `setsid nohup bash <script>` — each built from a **real entry copied off disk** — every one resolves to the **script**, and **L4 does NOT refuse on `--case-dir`** | required for **PASS** | **GATE FAIL** — this is falsification 2.2 turned into a gate |
| **G-R4-4 — EXECUTABILITY IS ASYMMETRIC (L6+L7)** | L6: a **present, non-executable** target behind `bash` is **ACCEPTED**. L7: a **present, non-executable** target at `argv[0]` with no interpreter is **REFUSED**, naming `not executable` | required for **PASS** | **GATE FAIL** — either limb alone permits the wrong rule |
| **G-R4-5 — THE MUTATIONS FLIP (L8)** | With the `X_OK` branch replaced by `True`, **L7 flips to acceptance**; with the existence test replaced by `True`, **L1 flips to acceptance**; with the interpreter set emptied, **L6 flips to refusal** | required for **PASS** | **GATE FAIL** — a guard whose deletion changes nothing was never exercised |
| **G-R4-6 — FOREIGN HOST IS NOT EVALUATED, NOT PASSED AND NOT REFUSED (L9)** | A foreign-host entry with an **absent** target returns **no** `LAUNCH-TARGET:` failure **and** appends a string containing the declared host to R2's `unevaluated` channel; with the append suppressed, **L9 flips on its channel limb** — so the control can tell `NOT EVALUATED` from `PASS` | required for **PASS** | **GATE FAIL** |
| **G-R4-7 — THE EMPTY INVOCATION REFUSES, THROUGH THE REAL `main()` (L10)** | `subprocess.run([sys.executable, <the real script>])` with **no arguments** returns **rc 3**; and the same with `--dir <an empty scratch directory>` returns **rc 3**. Both driven as **real processes on the real file** — never by calling `main([])` in-process | required for **PASS** | **GATE FAIL** |
| **G-R4-8 — THE EMPTY-INVOCATION NEGATIVE TWIN (L11)** | The **same real process invocation** given **one valid entry** returns **rc 0**; given **one invalid entry** returns **rc 2**; given `--dir <not a directory>` returns **rc 1**. **All three required** | required for **PASS** | **GATE FAIL** — a fix that refuses every invocation passes L10 perfectly |
| **G-R4-9 — FLAG-PROOF (L12)** | `python3 -O scripts/queue_entry_check.py --selftest` returns rc **2**; an `ast` walk over the shipped file returns **zero** `ast.Assert` nodes, counted by AST and never by grep | required for **PASS** | **GATE FAIL** |
| **G-R4-10 — NO REGRESSION, AND NOTHING ELSE MOVED (L13)** | `queue_entry_check.py --selftest` returns rc 0 with **at least 31** controls fired and its control-name set differs from today's by **nothing but the rows added here**; `queue_runner.py --selftest` returns rc 0 at **41/41**; and §8's invariance set is **bit-identical** | required for **PASS** | **GATE FAIL** |

**PASS iff all ten hold. Any one not holding is `GATE FAIL`.** §9's conditions take precedence
over both.

## 8. THE BIRTH REQUIREMENT AND THE INVARIANCE SET

### 8.1 Birth requirement — Sanaa directive 1, as a refusal condition on this instrument

Sanaa, 2026-08-28T17:01Z: *"A control defined in terms of the thing it controls is not a control.
A planted control must travel the real production path — written by the real producer's code, read
through the real reader … no instrument grades anything until that answer is yes, demonstrated."*

**THE REAL PRODUCER, NAMED.** `scripts/queue_runner.py::launch()` — `:515` `launched_dir`, `:517`
`dst`, `:520` `shutil.move`, `:536` `dst.write_text` of `meta` = the entry plus `_launch` (`:522`)
and `_field_classes` (`:526-535`). The runner is the producer of an entry's committed on-disk form.

**THE REAL READER, NAMED.** `queue_entry_check.validate(entry, root, entry_path, …)` — the
production function, and for L10/L11 the real `main()` reached as a **real subprocess of the real
file**, never an in-process call.

**BR-1 — MANDATORY, AND THE DRIVER REFUSES WITHOUT IT.** Before it grades anything the driver
asserts, in the same invocation:

> (i) the entries L1/L2 operate on were **written by `queue_runner.launch()`** and carry the
> `_launch` and `_field_classes` keys that only `:522`/`:526-535` add — a hand-composed entry dict
> is refused, because grading against one certifies only that the validator can read the test's
> idea of an entry;
> (ii) L3/L4/L5's argv are **copied verbatim from real entries on disk** — one
> `ansys-verification` interpreter+script entry, one heat-transfer bare-executable entry, one
> dafoam `setsid nohup bash` entry — and the driver asserts each copied argv is **byte-equal** to
> the file it came from;
> (iii) **L1 fires before L2 is read**: the absent-target refusal must be observed through the real
> `validate()` before any acceptance is allowed to count;
> (iv) L6's non-executable fixture is verified `os.access(X_OK) is False` **and** `R_OK is True`
> **before** the call, so the branch under test is actually reachable — R2 §5's lesson that *the
> plant, not the assertion, is where blindness lives*;
> (v) L10's rc is read from `subprocess.run(...).returncode` on the **bare** process, never from a
> pipeline, because `cmd | tail; echo $?` reports `tail`'s status.
>
> **If any of (i)–(v) fails the driver exits 2 and grades NOTHING.**

**THE RESIDUAL, NAMED RATHER THAN DISCOVERED LATER.** No entry on this disk today takes the
not-path-shaped branch of §3, so **that branch ships with a synthetic fixture and no live
witness.** It is registered as `NOT EVALUATED`-returning by construction and its control (part of
L3) proves only that it does not refuse — not that any real entry ever reaches it. Stated so it
cannot later be read as having been exercised in production.

### 8.2 The invariance set — bit-identical, checked by `sha256` before and after

Any difference is `GATE FAIL` under G-R4-10, with the differing path printed.

1. **Every file under `verification/queue/`** — every team directory, every `held/`, every
   `launched/`, `LAUNCH_LOG.tsv`, and the runner's own logs. Every control runs in a `tempfile`
   tree; this set is what proves it.
2. `docs/standards/QUEUE_ENTRY_HOST_SCOPE.md`, `QUEUE_ENTRY_TEAM_BINDING.md`,
   `QUEUE_ENTRY_VALIDATOR_RULINGS.md`, `QUEUE_ENTRY_STANDARD.md`,
   `QUEUE_RUNNER_RECORD_LOCATION.md` — frozen standards; rule 6.
3. This document, and `R1`/`R2`/`R3` at `f7da1a24`.
4. `scripts/queue_runner.py` — **byte-identical, in full. R4 does not touch the runner at all.**
   The runner's selftest is run only as a regression reading.
5. `scripts/roache_triple.py` — named because it is the lab's shared comparator and this item must
   be shown not to have touched it, **not** because it is used (§6: it is not called).

**The live daemon.** `scripts/queue_runner.py --daemon` was running as **pid 1120800** at
2026-08-28T17:34Z, elapsed 1-00:01:47, and was verified alive **after** this lane ran the runner's
selftest. **This item must not restart, signal or race it.** Any restart is the supervisor's
decision, not this item's, and a repair to the validator entitles nobody to bounce the runner.

## 9. CRITERIA — how the verdict is reached, in order

1. **BLOCKED** if §11's enqueue preconditions are unmet at launch — in particular if **P1** is
   unmet, i.e. R2's repair has not landed and the host-scope `unevaluated` channel of §4 does not
   exist. Nothing is graded.
2. **NOT A RESULT** if BR-1 refuses (exit 2) — the instrument was never shown able to see the
   defect through the real code path, so no reading it produces is evidence.
3. **NOT A RESULT** if the driver's own completion clause fails: rc != 0, no terminal record line,
   or any of L1–L13 reported `NOT RUN`.
4. **GATE FAIL** if any of G-R4-1 … G-R4-10 is not met, naming which.
5. **PASS** iff all ten are met and none of 1–3 applies.

**No partial credit and no degraded reading** — rule 4's *refuse rather than degrade* governs the
driver at every refusal point.

## 10. COST, CAP AND CALIBRATION — rule 12

### 10.1 The basis, term by term, each labelled MEASURED or ALLOWANCE

`ranks = 1`. Core-minutes = wall s × ranks ÷ 60.

| term | wall s | basis |
|---|---|---|
| a) `queue_entry_check.py --selftest` × 3 — pre-repair baseline for L13, post-repair run, and the `-O` run at L12 | 1.5 | **MEASURED.** One run took **0.50 wall s**, rc 0, 31 controls, in this lane's invocation. |
| b) the new rows L1–L9 and L12–L13 added to that suite | 2.5 | **ALLOWANCE**, on the measured per-control rate 0.50 ÷ 31 ≈ 0.016 s, carried generously because L1/L2/L9 each build a `tempfile` production-shape queue tree and L3/L4/L5 copy real entries. |
| c) L10/L11's **five real subprocess invocations** of the real file (bare, `--dir` empty, one-valid, one-invalid, `--dir` not-a-directory) | 1.5 | **ALLOWANCE** on a measured ~0.15 s interpreter start plus the file's own 0.5 s worst case; four of the five exit before `repo_root()`. |
| d) `queue_runner.py --selftest` × 2 — the pre and post regression readings of G-R4-10 | **11.0** | **MEASURED, NOT GUESSED.** One run took **5.24 wall s**, rc 0, 41/41, in this lane's invocation, after its `mkdtemp` isolation was read and the live daemon verified alive on both sides. This is the term R2 §9.1 carried at 40.0 s as a declared guess. |
| e) the §3 shape survey re-driven over every entry on disk, the §8.2 `sha256` invariance set, and the record write | 3.0 | **ALLOWANCE.** The survey of §2.2 ran over 133 entries in well under 1 wall s in this invocation. |
| **TOTAL** | **19.5** | |

### 10.2 THE ESTIMATE, THE CAP AND THE RATIO

| | value |
|---|---|
| **cost_core_min_estimate** | **0.3250** core-min (19.5 wall s × 1 rank ÷ 60) |
| **cap_core_min_registered** | **0.4800** core-min |
| **cap / estimate** | **1.4769** |
| dollars at the estimate | **$0.000278** — **DERIVED, NOT MEASURED** |
| dollars at the cap | **$0.000410** — **DERIVED, NOT MEASURED** |

Rate **$0.0513 per core-hour**, c7a.4xlarge, **owner-stated 2026-08-21/22 and
reported-by-owner, never measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). **A tiny cost is still a cost**; rule 12 disqualifies a proposal
that carries none, which is why the terms are enumerated rather than waved at as negligible.

**HOW THE CAP IS ENFORCED, and it is never raised.** The cap converts to a wall allowance of
**28.8 s** at 1 rank, handed to `timeout` **around terms (b), (c) and (e)** — the three
allowance-based terms. Terms (a) and (d) are measured and are not the exposure. An overrun
**kills the step and STOPS the item**, leaving the controls incomplete, which §9 clause 3 grades
**NOT A RESULT**. That is the correct outcome of an overrun and it does not get a second budget.

### 10.3 CALIBRATION AT COMPLETION (rule 12's calibration clause)

At completion the record **must** carry: actual core-minutes from the driver's own log, gross and
cleaned stated separately; waste named separately and never absorbed into the ratio; the ratio
actual/predicted against **0.3250**; the gap attributed to contention, waste or misprediction; and
dollars **derived, not measured**. A row lands in **`docs/COST_CALIBRATION.md`**. **A completion
report without this comparison is incomplete.**

**Carried forward for R2's row, not for this one:** the runner-selftest measurement of §2.5
(**5.24 wall s**, against R2's declared 40.0 s allowance for two runs) is the attributable share
of R2's misprediction and belongs in R2's calibration row when R2 completes. It is recorded here
because this lane took the reading; it does not amend R2, whose gates are frozen.

## 11. RULE-2 ABSENCE CONDITION, CHECKED IN THIS WRITING INVOCATION

**At 2026-08-28T17:35:08Z, in this lane's own invocation, each checked FOUR ways —
`os.path.exists` → False, `os.path.lexists` → False (so not a dangling symlink), `os.path.isdir`
→ False, `glob` on the literal path → `[]`:**

- `/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS` — **DOES NOT EXIST**
- `/home/ubuntu/Certonomous/verification/runs/TOOLING_REPAIRS/R4_QUEUE_LAUNCH_TARGET_2026-08-28` —
  **DOES NOT EXIST**
- `/home/ubuntu/Certonomous/scripts/run_r4_launch_target_repair.sh` — **DOES NOT EXIST**

**A fifth, wider check:** `glob('verification/runs/TOOLING*')` → **`[]`** and
`glob('scripts/run_r[45]*')` → **`[]`**. **0.000 core-min have been spent under this
registration.** No driver, no control record and no scratch tree written by this item exists
anywhere.

Amendments **before** first compute remain legal under rule 2 and must state this condition and
how it was checked, naming the directory that does not exist. **After first compute the gates are
closed** and changes land only as dated addenda that cannot alter a gate, threshold, cap or label;
originals are struck, never rewritten.

**Nothing is ever deleted by this item.** The driver creates; it holds no `rm -rf`, `rmtree` or
`shutil.rmtree` against any case, run or scratch tree it did not itself create in the same
invocation, and §8.2's invariance set is what proves it after the fact.

## 12. LAUNCH SHAPE — for the supervisor's check 4; **NOT an authorisation**

    bash /home/ubuntu/Certonomous/scripts/run_r4_launch_target_repair.sh \
         --prereg-commit=<the sha of THIS document's adding commit>

The driver **fires nothing without `--prereg-commit`**, verifies the sha is a commit in this
repository, and verifies that `docs/standards/QUEUE_ENTRY_HOST_SCOPE.md` at
`ed77957c4e56cd12e1d5d0c620b218805bd4306b` hashes to the blob it was frozen as — §4's ruling is
read from the frozen spec, never from a copy.

**ENQUEUE PRECONDITIONS — five, and the queue validator checks NONE of them.** (That is this
item's own subject matter, and until it lands the list below is the only thing standing between an
absent driver and a `LAUNCHED` record.)

1. **P1 — SEQUENCING.** R2's repair has landed and the host-scope `unevaluated` channel exists in
   `queue_entry_check.validate()`. **R4 adds `LAUNCH-TARGET` to R2's host-sensitive set; it does
   not create one.** If R2 has not landed, R4 is **BLOCKED** under §9 clause 1 — not run with the
   host limb quietly dropped, which would ship a clause that refuses foreign-host entries on a
   local filesystem reading.
2. `scripts/run_r4_launch_target_repair.sh` **exists** at the absolute path in the launch shape.
3. `bash scripts/run_r4_launch_target_repair.sh --selftest` returns **rc 0**, and the driver's
   python entry point under `python3 -O` returns **rc 2** (G-R4-9 at entry).
4. The `queue_entry_check.py` diff is read **as a diff** by the supervisor personally.
   `SUPERVISION_CHARTER.md` §3 check 1 may never be delegated, and a lane's control result is not
   that check.
5. The `prereg_commit` placeholder in the held queue entry has been replaced with the real sha of
   this document's adding commit, re-derived from `git log --diff-filter=A -- <path>` and **never
   from a subject line**.

A queue entry is drafted at
`verification/campaign/queue_entry_R4_QUEUE_LAUNCH_TARGET_REPAIR.json` and is **HELD beside this
registration. THIS LANE DOES NOT ENQUEUE IT and has committed nothing.** **Enqueueing is not
authorisation.**

**A REFERRAL CARRIED FORWARD AND NOT RESOLVED HERE.** `QUEUE_ENTRY_HOST_SCOPE.md` refers to the
chief whether **narrowing** a validator refusal is a tooling ruling of the kind
`QUEUE_ENTRY_VALIDATOR_RULINGS.md` already carries, or an amendment to
`QUEUE_ENTRY_STANDARD.md` — which is Sanaa's alone. R4 **widens** rather than narrows and does not
obviously fall under that referral, but the `NOT EVALUATED` limb it inherits from R2 does. **This
registration does not answer the referral and does not route around it.** If the chief rules it an
amendment, R4's host limb is `BLOCKED` on the same footing as R2's.

## 13. WHAT IS **NOT** CLAIMED, REGISTERED OR AUTHORISED HERE

- **No verdict of any existing rung is re-graded, in any team.** The defect is latent everywhere
  but cfd's own three held entries (§2.1); nothing that has launched was launched wrongly because
  of it, and **no landed verdict is exposed**. That finding is the reason, stated so it cannot
  later be read as leniency.
- **No frozen comparator is edited.** `queue_entry_check.py` is live cfd tooling, not any
  pre-registration's frozen grading path.
- **`scripts/queue_runner.py` is not modified at all** (§8.2 clause 4). It is run twice as a
  regression reading and is otherwise untouched.
- **No entry is edited, moved, dropped or enqueued** — including the three whose targets are
  absent. Their absence is a finding of this document, not a task of it.
- **No gate, threshold, band, cap or label of any other registration is added, moved or removed.**
  R1's, R2's and R3's caps and gates are untouched, and R2's 40.0 s term is **recorded as
  mispredicted, not amended** (§10.3).
- **No verdict-vocabulary word is added or retired.** `NOT EVALUATED` is a clause-reporting token
  and never a verdict (§6).
- **The validator is not made to contact another host.** `_git()`'s read-only allowlist
  (`cat-file`, `rev-parse`, `ls-tree`, `queue_entry_check.py:104`) is unchanged and no subcommand
  is added to it. `ssh` was refused by the host-scope spec and is not reopened.
- **`PATH` is not consulted and `shutil.which` is not called.** A bare-name target is
  `NOT EVALUATED` (§3), because the validator's environment is not the launch environment.
- **No observed order and no GCI is produced** (§6); `roache_triple.py` is not called.
- **The live daemon is not restarted, signalled or reconfigured** (§8.2).
- **No solver compute is authorised.** This item runs two selftests and a control harness.
- **Nothing is sent, filed, uploaded, registered, posted or submitted** (rule 7). Submissions are
  **PARKED**.

---

*Registration ends. Written before implementation; the commit that lands it is the freeze.*

---

## DRAFTING NOTE — 2026-08-28T17:4xZ, BEFORE THE FREEZE, BEFORE ANY COMPUTE

**HEAD at this lane's reads was `1f74d6de1780c4cac36d7a1539ecde97266fd23d`** (2026-08-28T17:30:10Z).
Peers commit constantly and a HEAD sha quoted in a document has a shelf life; every ancestry claim
here is stated against that sha and `f7da1a24ca8c730d5c49a7ea429840c43378bf1e`,
`ed77957c4e56cd12e1d5d0c620b218805bd4306b` and `47e86a46` were each verified ancestors of it in
this lane's own invocation. **The supervisor re-derives the freeze sha at the freeze, from
`git log --diff-filter=A -- <this path>`, never from a subject line.**

**This lane committed nothing, staged nothing and launched nothing.** All four artifacts of this
work — two registrations and two held queue entries — stand as **untracked** working-tree files.
The shared git index was not touched, no `git add` of any form was issued, and `refs/heads/main`
was not moved. **The freeze is the supervisor's act.**

**Filing, measured before the files were written:** `python3 scripts/check_filing.py` returned
**37 violations across 8 rules (rc 1)** at 2026-08-28T17:35Z. The after-reading and the
attribution of any change belong to the freezing invocation, not to this note; a decrease claimed
by the wrong agent is a false record in the cheap direction.
