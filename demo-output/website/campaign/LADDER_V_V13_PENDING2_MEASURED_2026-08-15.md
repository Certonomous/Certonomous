# V13 PENDING-2 — the two inherited rows, MEASURED

**Executed 2026-08-15, 01:56 → 02:2x UTC (`date -u` at open; machine TZ `Etc/UTC`, so every
timestamp here is UTC without conversion).** Owner: the PENDING-2 measurement pass.

**What this pass is for.** `LADDER_V_V13_CLOSEOUT.md` §8 PENDING-2 held two rows that round 4
(`LADDER_V_V15_ROUND4.md`, rows **Q69** and **Q60**) marked **"Inherited"** — accepted from
another agent's report rather than measured — because measuring them needed capabilities a
read-only, worktree-isolated grader did not have. Q69's evidence lives **outside the
repository**; Q60's verification is **not a read-only act**. This pass had both capabilities.
The records repair at `0b0041b1` had already established that PENDING-2 is **two rows, not
three commits**: `656c09c9`, `63009dd3` and `472f9f92` were in fact read by a non-author in
round 4.

**"Inherited" was not available to this pass as a verdict.** Each row below is
MEASURED-PASS, MEASURED-FAIL, or STILL-UNMEASURABLE-with-reason.

---

## 0. FRAME, STATED BEFORE ANY COUNT

**Non-authorship.** This pass wrote none of `472f9f92`, `2b251689` or `7cd558b1`. Those three
carry the box's shared `Ubuntu <ubuntu@ip-172-31-43-247…>` identity, which **every agent on
this machine commits under**, so the git author field cannot discriminate agents here and is
not offered as the proof. The proof is provenance: all three were authored
**2026-08-11 00:18–00:31 UTC**, and this session opened **2026-08-15 01:56 UTC**, four days
later, on a tree whose HEAD was `74dd8f53`. This pass could not have written them. Their
authorship is stated in their own records — `LADDER_V_V6_V10_V14_CLOSURE.md` (the V6/V10/V14
closure pass) and `BUNDLE_REBUILD_2026-08-10.md`, both signed by that pass, not by this one.

**Tooling, stated because it changes what a zero means.** This shell's `grep` is
**ugrep 7.5.0** invoked as `ugrep --ignore-files`, which **honours `.gitignore`**, and its
`find` is **bfs 4.1.1**, which rejects GNU expressions. Every measurement below used
**`/usr/bin/grep` (GNU grep 3.11)** and **`/usr/bin/find` (GNU findutils 4.9.0)** explicitly.
This matters twice over: the run tree of §1 is outside the repo, and the bundle directory of
§2 is **gitignored at `.gitignore:72`** and therefore invisible to the shell's own `grep`.

**Isolation.** Run in the **main checkout**, never a worktree — worktree isolation is exactly
what made Q69 uncheckable in round 4. Intermediate files went to an exclusive scratch path
outside the repo. Three other agents were committing throughout; HEAD moved from `74dd8f53`
to `297b82a0` during the pass and every number below names the HEAD it was taken at.

**Hygiene.** All `__pycache__` purged before each measurement cell (7 directories on the
first purge, 0 `.pyc` remaining). **Zero solver runs, zero scoring calls; the scoring ledger
was not touched.** The scoring pin at `/home/ubuntu/closure-challenge-benchmark` was not
moved. **Nothing was sent, uploaded, filed or registered.** `dist/` was **not rebuilt and not
edited** — it has a designated owner; the archive was copied to scratch and read there.

---

## 1. Q69 — THE RUN-TREE POSITIVE CONTROL — **MEASURED-PASS**

### 1a. What the control was supposed to demonstrate

The claim is the untrained-path compliance line at
`demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:319`, answering *"Touched any test
data?"*:

> **NO GROUND TRUTH, and the absence is a measurement rather than a blind spot.** Counted
> directly in the run tree: `AR_1_Ret_360_qcr`, `AR_3_Ret_360_qcr` and `AR_14_Ret_180_qcr`
> hold **0** `*_LES*` files each; `AR_7_Ret_180_qcr` and `AR_7_Ret_180_sst` hold **3 each**.

The design is a positive control against the **silent-zero defect (class B1)**: three zeros
on their own are equally consistent with *"no ground truth was present"* and with *"the
finder was broken"*. `AR_7_Ret_180` is the benchmark's **own suggested validation duct** —
reading its truth is legal — so its two arms are where the finder **must** return non-zero.
**The control is what converts the three zeros from an absence of evidence into a
measurement.**

### 1b. Evidence count, printed BEFORE the verdict

Tool: `/usr/bin/find`. Root: `/home/ubuntu/certonomous-runs/w3-qcr-rank1/`.

| arm | files | dirs |
| --- | --- | --- |
| `AR_1_Ret_360_qcr` | 52 | 16 |
| `AR_3_Ret_360_qcr` | 52 | 16 |
| `AR_14_Ret_180_qcr` | 52 | 16 |
| `AR_7_Ret_180_qcr` | **55** | 16 |
| `AR_7_Ret_180_sst` | **55** | 16 |
| **total files searched** | **266** | |

**266 files, not zero.** The finder had real material in every one of the five arms. Had this
been 0 the verdict below would read UNKNOWN, not PASS.

### 1c. The measurement

The cited command, re-run verbatim:

```
$ /usr/bin/find /home/ubuntu/certonomous-runs/w3-qcr-rank1/*/ -name "*_LES*"
.../AR_7_Ret_180_qcr/0/U_LES
.../AR_7_Ret_180_qcr/0/k_LES
.../AR_7_Ret_180_qcr/0/tauij_LES
.../AR_7_Ret_180_sst/0/U_LES
.../AR_7_Ret_180_sst/0/k_LES
.../AR_7_Ret_180_sst/0/tauij_LES
```

| arm | claimed | **measured** |
| --- | --- | --- |
| `AR_1_Ret_360_qcr` | 0 | **0** |
| `AR_3_Ret_360_qcr` | 0 | **0** |
| `AR_14_Ret_180_qcr` | 0 | **0** |
| `AR_7_Ret_180_qcr` | 3 | **3** |
| `AR_7_Ret_180_sst` | 3 | **3** |
| **positive-control hits** | 6 | **6** |

**Every number matches exactly. The control fires. The three zeros are a measurement.**

### 1d. Four corroborations the original claim did not offer

1. **The file-count asymmetry is exactly the control.** The AR_7 arms hold 55 files against
   the test ducts' 52 — a difference of **exactly 3**, and `diff` over the `0/` directories
   returns exactly `U_LES`, `k_LES`, `tauij_LES` and **nothing else**. The five arms are
   otherwise identical in structure.
2. **The LES files carry real content**, not empty placeholders: `U_LES` 971,446 B,
   `k_LES` 290,795 B, `tauij_LES` 1,874,548 B, byte-identical across both AR_7 arms,
   all stamped `2026-08-05 17:41` — the freeze minute recorded in
   `w3-qcr-rank1/RULE_FREEZE.md`, which was written *before* any test-duct directory existed.
3. **No truth under another name.** Case-sensitive `/usr/bin/find . -name '*LES*'` over the
   whole subtree returns **the same 6 files and no others**. An `-iname` sweep for
   `*DNS*`, `*truth*`, `*ref*`, `*label*`, `*target*` returns **0** across all five arms, and
   a full basename census of all 266 files shows every non-LES name appearing 5 or 10 times
   (once or twice per arm) — i.e. the arms are structurally uniform and the LES trio is the
   only asymmetry anywhere.
4. **`ledger.txt`** records all five arms `rc=0`, total 2,217 s solver, and states
   *"NO scoring call made"* — consistent with the untrained-path claim.

**One apparent anomaly, resolved rather than left hanging.** `/usr/bin/grep -c "_LES"` over
`log.simpleFoam` returns **0 in all five arms, including the two control arms** (logs of
5,631 / 27,485 / 125,359 / 65,341 / 65,228 lines). This is not a contradiction: the LES
fields are **scoring inputs read by the Python metric, not fields read by `simpleFoam`**, and
`RULE_FREEZE.md` §2 says so — the arms are *"scored against its shipped LES field
(`0/U_LES`)"* after the solve. A solver log mentioning `_LES` would in fact be the alarming
result.

### 1e. What this control cannot see — the D112 shape applied to Q69

D112's transferable shape is *a clearance verified against an enumeration cannot see the item
beside the ones it lists.* **`*_LES*` is an enumeration by filename pattern.** It cannot
contain:

- **truth read from outside these five arms** — e.g. the benchmark source tree read directly
  by the scoring code at predict time. The glob proves no truth file *sits in the test-duct
  case directories*; it cannot prove none was *read*;
- **truth embedded in the contents of a differently-named file** — the glob matches names,
  not bytes.

**Both gaps are closed elsewhere and by a different instrument, which is why the row stands.**
Round 4's **Q62** and **Q63** audited the code path and both returned PASS-exact:
ground-truth reads at `apply_closure_ph_gate.py:128` and `:228` sit **inside `_PH_TRAIN`
loops**, and the test loop at `:178` calls `_load_rans_fields` at `:179` under the verbatim
annotation `# no U_LES read`. **Q69 is the filesystem half of a two-instrument argument; on
its own it is necessary and not sufficient, and the compliance line should not be cited as
though the glob alone settled it.**

### 1f. Verdict

> **Q69 — MEASURED-PASS.** 266 files searched, 6 control hits, 0/0/0 in the three test-duct
> arms and 3/3 in the two validation arms, matching the claim exactly. The positive control
> fires, so the zeros are an absence and not a broken finder. Measured in the main checkout
> with `/usr/bin/find`, by a pass that wrote none of the audited work.

---

## 2. Q60 — V10's DRIFT CHECK AND HTTP SERVE — **MEASURED-PASS on the claim, with a live FAIL at HEAD**

The claim at `2b251689` is *"drift check PASS at 56 of 56 byte-for-byte"* plus *"served and
read over HTTP"*. This pass re-derived it rather than re-reading it, and the answer splits
cleanly in two: **the claim was true when made, and it is false now** — which is not a
contradiction but the finding.

### 2a. What the drift check actually enumerates

`self_audit.check_bundle_drift()` builds its pair list in `_bundle_pairs()` from
`_BUNDLE_VERBATIM` (`sdk/chief_engineer/**/*` and `scripts/laptop_bundle/*`) plus the three
`_BUNDLE_PAGES`. **Evidence count, printed before any verdict: 56 pairs** —
**49 control-room modules + 4 launcher files + 3 pages = 56**. The denominator in the claim
is exact and this pass reproduces it independently.

The copy list and the file set are **unchanged since the claim commit**: `_BUNDLE_VERBATIM`
and `_BUNDLE_PAGES` are byte-identical at `2b251689` and at HEAD, and
`git ls-tree` gives **49** tracked `sdk/chief_engineer` files and **4** `scripts/laptop_bundle`
files at *both* revisions with an empty set-difference. The reconstruction below is therefore
exact and not anachronistic.

### 2b. The claim, reconstructed at its own commits — **56 / 56, confirmed**

The original check compared sources against `dist/certonomous-demo/`, which is **gitignored**
(`.gitignore:72`) and therefore **untracked and unreconstructable** — its state on 2026-08-11
is gone and no later agent can ever recover it. So this pass verified the claim against a
**stronger and reconstructable** reference: **the tracked shipped zip itself**, extracted from
each commit's own blob into scratch.

| commit | reference | **measured** |
| --- | --- | --- |
| `2b251689` | committed sources vs that commit's `dist/certonomous-demo.zip` (90 files) | **56 / 56 byte-for-byte, 0 differ, 0 absent** |
| `7cd558b1` | same | **56 / 56 byte-for-byte, 0 differ, 0 absent** |

> **The 56/56 claim re-derives exactly, against a harder reference than the one it was made
> with.** V10's self-graded closure is confirmed by a non-author.

### 2c. The HTTP serve, re-executed

Served the **currently shipped** archive — extracted from the tracked blob into scratch,
never from `dist/` — over a port chosen and verified free.

**Port discipline, because this lab has a `REUSEADDR` trap on record** (two servers can share
a port and a stale one answers). `ss -ltnp` showed **8765 (pid 1440)** and **8080 (pid 1444)**
already held by the lab's own control room; a connect probe confirmed both answered.
**Port 9317 was absent from `ss` and refused connection**, so it was chosen.

**Identity of the server that answered, checked three ways rather than by "something
responded":**

- `ss -ltnp` reported the listener on `127.0.0.1:9317` as **pid 672890**;
- that is **the `setsid` child of the pid 672888 this pass launched**, and
  `readlink /proc/672890/cwd` resolved to **this pass's own scratch extraction directory** —
  a discriminator no other server on this box could match, and a stronger one than the pid;
- the **served bytes hash-matched the zip members**: `site/closure.html`
  sha256 `80d94712ff…`, `site/benchmarks.html` sha256 `681da652…`.

**Shut down when done**: pid 672890 killed, 9317 clear in `ss`, `curl` returns `000`. The
lab's own 8765 and 8080 servers were **verified still listening, untouched**, after shutdown.

**What the HTTP read returned** (HTTP 200 on all three pages):

| check | result |
| --- | --- |
| closure.html hero (`:138`, `class="kpi hero"`) | **`0.0566`** — round-5 score |
| benchmarks.html KPI (`:99`) | **`0.0566`**; benchmarks.html carries **0** hits of `0.0654`, `0.0676`, `0.0741` |
| struck prior-art sentence, discriminating fragments | **0 hits** — `controls where a data-driven correction is allowed to act`, `has been published repeatedly` |
| **planted positive control** | **2 / 2 fragments recovered** |
| rank companion | interval `2–100` ×2, `Reissmann` ×7, `Wu` ×8, `Zhang` ×7, `six-entry` ×5, `2 of 8` ×2 |

The absence check used the **wrap-proof normalised instrument** that `7cd558b1` itself
established (tags stripped, whitespace collapsed, dashes and quotes folded) — 33,926
normalised chars from 41,094 served bytes — **and its own planted control**: the struck
sentence was injected into a scratch copy of the served page **wrapped across five lines and
split by `<b>`/`<i>` tags**, and the same search recovered **both** discriminating fragments
from it. **The zero on the real artifact is therefore an absence, not a broken pipe.**

### 2d. **THE LIVE FINDING — the shipped bundle is stale, and the drift check cannot see it**

Measured at HEAD `297b82a0`, `__pycache__` purged first:

| reference | **measured** |
| --- | --- |
| working-tree sources vs `dist/certonomous-demo/` (what `check_bundle_drift()` compares) | **51 / 56** — `check_bundle_drift()` returns **FAIL**, *"0 file(s) missing and 5 behind the tree, of 56 copied verbatim"* |
| committed sources vs the **tracked shipped zip** | **51 / 56** — 5 differ, 0 missing |

The five stale members, identical in both measurements:

| member | source | shipped |
| --- | --- | --- |
| `sdk/chief_engineer/agenda.py` | 64,270 B | 61,008 B |
| `sdk/chief_engineer/exec_bits.py` | 24,989 B | 24,597 B |
| `demo-output/website/closure.html` | 46,874 B | 41,370 B |
| `demo-output/website/benchmarks.html` | 20,362 B | 19,057 B |
| `demo-output/website/wall/wall.html` | 10,302 B | 10,304 B |

**D112 confirmed in the artifact, by direct read.** The shipped
`site/closure.html:502` carries, **unstruck and as live prose**:

> *"holds no official rank — rank 1 of 5 is our local scoring at a pinned benchmark commit,
> with a seed-uncertainty bound comparable to its margin"*

The repaired source at `demo-output/website/closure.html:554` carries the corrected clause
in bold — **`rank 1 of 7 entrants counting us`**, with a bound **`larger than its margin:
0.0024 against 0.001365 is 177%`** — and the old sentence survives only inside an
`<s>…</s>` tombstone marked **struck 2026-08-15**. `four-entry` appears **5** times in the
source and **3** in the zip; the two extra source hits are the new tombstone and its
explanation. **The defect is live in the artifact that ships and repaired in the source it
ships from.**

**Reported, not repaired. `dist/` has a designated owner and was not touched.**

### 2e. What the drift check's list cannot contain — D112's shape, one level up

The instruction to say what a list cannot contain has a sharper answer here than expected.

1. **`check_bundle_drift()` never opens the shipped artifact.** It compares against
   `dist/certonomous-demo/` — a **gitignored build-scratch directory**, `.gitignore:72`,
   *"the .zip is committed; the extracted tree is not"*. **The only artifact that leaves this
   box is `dist/certonomous-demo.zip`, and the lab's drift detector does not read it.** The
   two agree today only because both were written by the same build at 2026-08-14 21:16.
   **Nothing enforces that.** Regenerate the directory without rebuilding the zip and the
   check goes green over a stale shipped artifact — the silent-zero shape, in the one place
   it costs most. `BUNDLE_REBUILD_2026-08-10.md` §4 ruled the directory KEEP precisely
   because *"the drift check compares against that directory"*; that ruling is sound and this
   is the gap it leaves open.
2. **The check's own docstring names its second exclusion**: recorded missions, the
   credentials snapshot and everything derived at build time are deliberately outside the 56.
   **The zip holds 90 files; the check grades 56.** The 34 ungraded members include
   `snapshot/lab_stats.json` — the file that carried defect 4 of the original rebuild. **A
   stale score in the snapshot would not appear in any numerator on this page.**
3. **The 56/56 claim's own reference is unreconstructable.** Because the comparison directory
   is untracked, **no later agent can ever verify what `check_bundle_drift()` saw on
   2026-08-11.** This pass could confirm the claim only by substituting the tracked zip. A
   verification whose reference is gitignored is a verification that expires the moment it is
   made.

**Filed as docket `D118`.**

### 2f. Verdict

> **Q60 — MEASURED-PASS on the claim as made, and MEASURED-FAIL on the artifact as it stands
> today.** The `56 / 56` numerator and denominator both re-derive **exactly** at `2b251689`
> and `7cd558b1`, against the tracked shipped zip — a harder reference than the untracked
> directory the claim used. The HTTP serve re-executes: hero and KPI both `0.0566`, the
> struck sentence absent under a wrap-proof instrument whose planted control passes 2/2,
> the rank companion carrying its interval and its not-decided pairs. **At HEAD `297b82a0`
> the same check measures `51 / 56` and returns FAIL**, five members stale, and the shipped
> `closure.html:502` carries D112's unstruck four-entry-board claim while its source is
> repaired. The V10 closure is confirmed; the artifact it closed has since drifted.

---

## 3. WHAT THIS PASS DID NOT DO, AND WHO CAN CLOSE THE RUNG

**No rung is marked green here, and this pass may not mark one.** Under **R-ISOLATE** a rung
closes when a **non-author measures it**, and the measurer may not also be the one who
declares it closed. This pass is the measurer. It records what it measured and stops.

**What is now discharged:** V13 §8 **PENDING-2 has no inherited rows left.** Both Q69 and Q60
carry a non-author's measurement, and the records repair at `0b0041b1` had already discharged
the three-commits half.

**Who can confirm and close.**

- **PENDING-2 itself → the V13 close-out owner, or any Ladder V pass owner who wrote none of
  `472f9f92`, `2b251689`, `7cd558b1` and none of this file.** The measurements above are
  re-runnable in minutes: §1 is one `/usr/bin/find`, §2b is two `git show` extractions and a
  byte compare.
- **V6 → still PASS-pending-confirmation on its own terms**, unchanged by this pass; its
  `472f9f92` half was read by a non-author in round 4 per `0b0041b1`.
- **V10 → the self-grade is now confirmed by a non-author** and can move off
  CLOSED-BY-ITS-AUTHOR **as a statement about `2b251689`**. It must not be restated as a
  claim about the bundle that ships today, which is `51 / 56`.
- **The bundle itself → `dist/`'s designated owner**, per D112 settlement item (i) and D118.
  **Not this pass, and not any Ladder V rung.**

**Standing caution carried forward.** Round 4's own words apply to this pass too: *do not read
a silence as a pass.* Two rows moved from inherited to measured; that is what changed, and
nothing more.

---

## 4. SIGNATURE

**The V13 PENDING-2 measurement pass, 2026-08-15.** Main checkout, never a worktree; exclusive
scratch outside the repo. Wrote none of `472f9f92`, `2b251689` or `7cd558b1` — all three
predate this session by four days. Evidence counts printed before every verdict (**266** run-tree
files; **56** drift pairs; **2/2** planted control). **Zero solver runs, zero scoring calls;
the scoring ledger was not touched and the scoring pin was not moved.** `dist/`, `latex/*`,
`LAPTOP_SHOOT.md`, `scripts/self_audit.py` and the other listed files were **read only, never
written**. **Nothing was sent, uploaded, filed or registered; submissions remain PARKED.**
**No rung marked green.**
