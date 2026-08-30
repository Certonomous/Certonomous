# T16b — successor to the T16 completion marker's D541 contrast limb: a defect-presence detector that loads the pre-repair file by explicit path instead of loading itself

> **STATUS: FROZEN BY THE COMMIT THAT FIRST LANDS IT. NOT ENQUEUED. NO CASE IS
> MARKED AND NOTHING IS GRADED UNDER THIS DOCUMENT UNTIL THE SUPERVISOR HAS READ
> THE SUCCESSOR'S DIFF AS A DIFF.**
>
> This document is frozen by the commit that first lands it, per standing rule 2.
> Marking `T16_MC_f` and running `analyse_t16.py` are the heat-transfer
> supervisor's decisions and are explicitly withheld from the lane that wrote
> this. Nothing here is sent anywhere (rule 7).
>
> **THIS DOCUMENT DOES NOT EDIT, AMEND OR SUPERSEDE `mark_done_t16.py`.** That
> file is frozen at blob `efcf78524dc4f853202cf24dd08c733d7742ac67`, registered
> at `T16_PREREGISTRATION.md:509` by AMENDMENT A1, and it is **byte-identical to
> its HEAD blob** — verified in §1, by hash, not asserted. It stays that way.
> **Zero frozen bytes change under T16b.** The repair lives here, in a successor
> file, or nowhere.
>
> **THIS DOCUMENT DOES NOT MOVE A GATE, A THRESHOLD, A BAND, A CAP OR A LABEL.**
> §3 enumerates every one of them and shows each is carried over byte-identically.
> **One selftest limb changes. Nothing else.**

Drafted 2026-08-30 by a heat-transfer `lab-lane` on the supervisor's disposition
brief. **Every number below was re-derived by this lane from the artifact named
beside it**, not transcribed from the brief; **§9 boards the two places where
this lane's reading differs materially from the brief it was handed, and one of
them corrects the brief's central premise.** Repository HEAD at drafting:
`5563f78533391e8ec5842db915ff70ebd7663685` (HEAD moved three times during
drafting — `ef26ded7` → `fac8c621` → `5563f785` — as peers committed; every hash
in §1 was re-taken against the last of these).

---

## 0. Why a successor exists

`T16_MC_f`, the FINE level of the T16 mixed-convection rung, is complete on all
six conjuncts of standing rule 4 and has been since **2026-08-29T14:13:00Z**.
Read by this lane from `verification/runs/T-family/T16_runs/STATUS.T16_MC_f` and
from the case's own artifacts:

| rule-4 conjunct | reading | source |
| --- | --- | --- |
| P1 `rc = 0` | `rc=0`, `capped=no`, `note=clean` | `STATUS.T16_MC_f` |
| P2 an `End` line | present | `T16_MC_f/log.solve` (28 419 255 bytes, 360 066 lines) |
| P3 last time == `endTime` | `40000` == `40000` | `T16_MC_f/`, `system/controlDict` |
| P4 registered fields present | `T U p_rgh phi` all present at `40000/` | `T16_MC_f/40000/` |
| P5 age guard | **min margin `+129 116.85 s`** (`U`); `T +129 117.40`, `p_rgh +129 116.98`, `phi +129 117.19` | `mtime(40000/<f>) − mtime(0/T)`, re-measured by this lane |
| spend | **2 151.950 core-min** = 129 117 wall s × 1 rank ÷ 60 | `STATUS.T16_MC_f` (`wall_s=129117`, `ranks=1`, `core_min=2151.950`) |

`DONE.T16_MC_c` (2026-08-27 19:18) and `DONE.T16_MC_m` (2026-08-27 21:28) are on
disk. **`DONE.T16_MC_f` is not**, and 2 151.95 core-minutes of completed physics
have sat unrecorded since 2026-08-29.

The obstacle is **not** that the marker refuses `T16_MC_f`. It is that the
marker's own `--selftest` cannot be believed. Run by this lane at HEAD
`5563f785`, three times, under `PYTHONPYCACHEPREFIX` pointed at scratch:

```
exit 1        SELFTEST FAIL (1 failed)
24 ok / 1 FAIL / 0 NOT MEASURED
[FAIL] D541 FROZEN matcher on clean banner  -> no crash token
```

**§2 shows the single FAIL is the least of the three defects in that limb**, and
that the other two produce **green lines that are evidence of nothing** — a
condition no existing ruling covers.

---

## 1. The parent files are UNTOUCHED — verified by hash, not asserted

`git hash-object <path>` against `git rev-parse HEAD:<path>`, taken in one shell
invocation at HEAD `5563f785`. **The shared git index is ~242 commits stale with
389 staged deletions, so `git status` and `git diff HEAD` are actively
misleading here — tracked-ness is read from that stale index. The comparison
below is against the HEAD BLOB and never against the index.**

| file | worktree blob | HEAD blob | identical |
| --- | --- | --- | --- |
| `verification/runs/T-family/T16_runs/mark_done_t16.py` | `efcf78524dc4f853202cf24dd08c733d7742ac67` | `efcf78524dc4f853202cf24dd08c733d7742ac67` | **YES** |
| `verification/runs/T-family/T16_runs/mark_done_t16.PRE_D541.py` | `2ae1605c7983e379d586467a8ffb4890d0d1b20d` | `2ae1605c7983e379d586467a8ffb4890d0d1b20d` | **YES** |
| `verification/runs/T-family/T16_runs/analyse_t16.py` | `9054d452b43ddda60c2bb187edc762d698a595ec` | `9054d452b43ddda60c2bb187edc762d698a595ec` | **YES** |
| `docs/campaigns/T-family/T16_PREREGISTRATION.md` | `18485ab4aef0209dc71cb8ad49eb7f7e08d6c9ca` | `18485ab4aef0209dc71cb8ad49eb7f7e08d6c9ca` | **YES** |

`efcf7852` is the blob registered at `T16_PREREGISTRATION.md:509` by AMENDMENT
A1; `2ae1605c` is the preserved pre-repair original registered at `:510`. **Both
reproduce.**

**A LIVE HAZARD THAT MAKES THE HASH CHECK LOAD-BEARING RATHER THAN CEREMONIAL.**
`docs/DEAD_LEVER_AUDIT.md:823-824` records that `mark_done_t16.py` **"is armed
for a 243-line regression right now"** through that same stale index: a
`git checkout` of the path would silently restore the 350-line PRE_D541 content
over the 593-line repaired file, leaving no commit to inspect. §4.1 registers a
digest guard that **fires on exactly this scenario**, which is why it is
specified as a REFUSAL and not a warning.

---

## 2. The defect, measured — and it is three defects in one limb, not one

The limb is `mark_done_t16.py:515-541`. Its purpose is to demonstrate D541 by
driving the **pre-repair** matcher on the same three sacrificial fixtures the
repaired matcher is driven on, and showing the two disagree.

### 2.1 Defect one — THE LIMB LOADS ITSELF

`mark_done_t16.py:515`:

```
    frozen = os.path.join(HERE, "mark_done_t16.py")
```

`HERE` is the directory of the running module and the basename is the running
module's own basename. **The "frozen" module and the running module are the same
file.** When this limb was written, the repair was a *proposal* named
`mark_done_t16.D541_PROPOSED.py` sitting **beside** the frozen
`mark_done_t16.py`, and the path was correct. The A3/A9 promotion at `5bcbaf8c`
renamed the proposal onto that basename. The path did not change; **what the
path pointed at did.**

So the limb loads the repaired matcher, compares it with the repaired matcher,
obtains identical behaviour, and its registered expectation of *"the frozen
matcher still fires on the clean banner"* inverts. That is the single visible
`FAIL`. It is **a defect-presence detector correctly reporting the defect gone**
— which is exactly what it should report about the file it was accidentally
handed, and exactly not what the arm exists to measure.

### 2.2 Defect two — TWO OF THE THREE ARMS ARE GREEN TAUTOLOGICALLY

This is **the defect no ruling covers and the reason T16b exists rather than a
one-line retarget.** The limb's three arms carry the registered expectation
`want_frozen_nonempty = True` on **all three** fixtures. After the self-load:

| arm | expectation | what the self-loaded module actually does | verdict printed | is it evidence? |
| --- | --- | --- | --- | --- |
| clean banner | non-empty | repaired matcher → `[]` | `FAIL` | **yes** — it detects the self-load |
| banner + real serial FPE crash | non-empty | repaired matcher → `['FPE: OpenFOAM sigFpe handler frame']` | `ok` | **NO** |
| banner + real MPI FPE crash | non-empty | repaired matcher → FPE labels | `ok` | **NO** |

Both crash arms pass **because the repaired matcher genuinely detects real FPE
crashes** — which the three arms immediately above them at `:498-512` already
measure, independently and correctly. The self-loaded arms therefore re-measure
the repaired matcher under a label that says `FROZEN`, and pass. **A reader
scanning `24 ok / 1 FAIL` sees two green lines asserting that the pre-repair
matcher was driven and behaved as D541 predicts. The pre-repair matcher was
never loaded at all.**

This is `docs/DEAD_LEVER_AUDIT.md`'s own subject matter one level down: a control
that cannot fail for the reason it names is a dead lever, and two of them are
sitting inside a selftest that the lab reads as a completion gate.

### 2.3 Defect three — THE NARRATION SITS OUTSIDE THE MEASUREMENT AND CANNOT BE CONTRADICTED

`mark_done_t16.py:540-541`, at the foot of the `else:` block but **outside the
`for` loop over the three arms**, unconditional on any of their outcomes:

```
        print("     ^ the frozen matcher refuses the CLEAN case: that is D541.")
        print("     ^ and it catches the SERIAL crash only via the same banner string.")
```

Both lines print on **every** run of this limb, including the run three lines
above in which the clean arm just printed `FAIL` and `no crash token` — i.e. the
run in which the loaded matcher demonstrably **did not** refuse the clean case.
**The record therefore asserts, in prose, the exact proposition its own
measurement one line earlier disproved.**

This is the shape `docs/LESSONS.md` calls *evidence annotated as non-binding*,
inverted: a printed conclusion with no binding to the measurement beneath it. It
is the most dangerous of the three defects, because the FAIL is at least visible
and the tautological greens are at least checkable, whereas this line is a claim
that **no measurement in this file can ever reach**.

### 2.4 What was NOT wrong, and must be said

**The marker's operational path is sound and is not in question.** At blob
`efcf7852` it was run on `T16_MC_c` and on `T16_MC_m`, printed `DONE` at exit 0,
and wrote both markers (ledger rows `C-170`/`C-180` and `C-184`). `check()`,
`crash_tokens_in_log()`, `read_status()`, `control_end_time()` and `_forge()` are
untouched by anything in this document. **The defect is confined to the
`--selftest` contrast limb and to nothing that grades or marks a case.**

---

## 3. WHAT DOES NOT CHANGE — enumerated, so the claim is checkable rather than asserted

`mark_done_t16b.py` starts from a **byte copy** of `mark_done_t16.py`. Every item
below is carried over **byte-identically** and none may be modified under this
registration. A diff showing any of them altered **invalidates this document**
and the successor must be rejected.

| # | carried over byte-identically | location in the parent |
| --- | --- | --- |
| V-1 | the eight `CRASH_PATTERNS` entries — all three unchanged error banners, all three D541 FPE forms, and both deliberately-unanchored D547 tokens `"Aborted"` and `"signal "` | `:146-171` |
| V-2 | `crash_tokens_in_log()` — the streaming matcher itself, in full | `:175-190` |
| V-3 | the NEEDED field tuple `("T", "U", "p_rgh", "phi")` — **this rung's own tuple, not the lab-wide thermal one** | `:126` |
| V-4 | the physics conjuncts **P1–P5** and their order inside `check()` | `:206-283` |
| V-5 | the L-342 field classes — `INFRA`, and the `ExecutionTime` count staying on the INFRASTRUCTURE side and never entering `fails` | `:127-129`, `:271-274` |
| V-6 | the age-guard predicate `mtime(field at endTime) < mtime(0/T)` and its failure text | `:275-283` |
| V-7 | ruling **R-RC**'s three arms — absent record → inference; absent record + physics failure → NOT DONE; absent record + crash token → REFUSE exit 2 | `:191-204`, `:210-226` |
| V-8 | `read_status()`, `control_end_time()`, `refuse()`, `_forge()`, `_d541_provenance()` and all three verbatim provenance excerpts with their cited sources | `:132-143`, `:191-204`, `:286-409` |
| V-9 | the exit codes `EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2` and their meanings | `:130` |
| V-10 | `CASES`, `main()`, `--root`, the marker text written into `DONE.<case>`, the unregistered-case-name refusal | `:125`, `:560-590` |
| V-11 | the fourteen `expect(...)` arms of the selftest, including both L-342 halves and all three R-RC arms | `:442-465` |
| V-12 | the three **repaired-matcher** contrast arms at `:498-512` and their `want_nonempty` expectations | `:498-512` |
| V-13 | the AST `assert`-counter control and its planted `assert 1` positive control | `:551-557` |

**QUANTIFIED: the number of gates, thresholds, bands, caps, labels, tolerances,
field tuples, crash patterns, exit codes and physics conjuncts that move under
T16b is ZERO.** T16b changes **one selftest limb** — a limb that grades nothing,
marks nothing, and whose only function is to demonstrate a historical defect.

**T16b also does not touch D547.** `"Aborted"` and `"signal "` stay unanchored,
for the reason D547 registers: `"signal "` is a **true positive** on the MPI
control, and anchoring either without a demonstrated false positive would be a
permissive change with no shown need. That standing finding remains OPEN BY
CHOICE and T16b does not disturb it.

---

## 4. WHAT T16b REGISTERS — the contrast limb, specified before the code exists

### 4.1 The target, and TWO REFUSAL conditions — not a skip

The contrast target is registered as an **explicit path**, resolved from the
running module's own directory but under a **different basename**:

```
CONTRAST_TARGET   = "mark_done_t16.PRE_D541.py"
CONTRAST_BLOB     = "2ae1605c7983e379d586467a8ffb4890d0d1b20d"
```

**Two conditions REFUSE with exit 2 (`refuse()`), and neither may be downgraded
to a skip, a warning or a `NOT MEASURED`:**

- **G-1 ABSENT.** If the target path does not resolve to a file, the successor
  **REFUSES**. The parent's behaviour here was `print(" [ -- ] ... NOT MEASURED")`
  and continue, which is how a missing defect-presence detector becomes
  invisible. Under T16b an absent contrast target is a **structural failure of
  the selftest**, on the same footing as an absent `controlDict`.
- **G-2 IDENTITY.** If the SHA-256 of the target's bytes **equals** the SHA-256 of
  the running module's bytes, the successor **REFUSES**. This is the guard
  against D541's own recurrence: it fires if the target is ever renamed onto the
  running basename, if the running file is ever copied over the target, **and if
  the stale-index `git checkout` hazard of §1 ever restores the PRE_D541 content
  over the running file** — in which case the two would become byte-identical and
  the whole contrast would silently become a self-comparison again.

**G-3 PROVENANCE, a FAIL and not a refusal.** The successor computes the target's
**git blob id** (SHA-1 over `blob <len>\0` + bytes) and compares it with
`CONTRAST_BLOB`. A mismatch is a **selftest FAIL** (exit 1), printed with both
ids. It is deliberately **not** a refusal: G-1 and G-2 answer *"is the contrast
structurally possible?"*, which is a precondition; G-3 answers *"is this the
registered historical artifact?"*, which is a finding. Distinguishing them is
itself registered, so a future reader cannot collapse the two.

### 4.2 The registered per-arm relations — a DISAGREEMENT, not a return value

**The parent's arms asked only whether each matcher returned something. T16b
registers, per arm, what the two matchers must DISAGREE ABOUT.** Every relation
below is derived from reading the two files' patterns — `mark_done_t16.py:146-171`
against `mark_done_t16.PRE_D541.py:97-98` and `:101-113` — **before** the
successor was written or run. Divergence between these registered relations and
what the successor measures is boarded, never quietly adopted.

Let `F(x)` be the pre-repair matcher's sorted hit set on fixture `x`, `R(x)` the
repaired matcher's, and `clean` the fixture carrying only `CLEAN_BANNER_2606`.

| arm | registered relation — ALL limbs must hold | what it proves, and how it can fail |
| --- | --- | --- |
| **C-1 CLEAN — the D541 defect itself** | `F(clean)` is **NON-EMPTY** and contains `"Floating point exception"`; `R(clean)` is **EMPTY**; therefore **`F(clean) != R(clean)`** | The two matchers **disagree on PRESENCE**. Fails if the target does not carry the defect (wrong file loaded) **or** if the repair regressed. This is the arm the parent could only report as `FAIL`. |
| **C-2 SERIAL FPE — the sharpest limb in this document** | `F(A)` is non-empty; `R(A)` is non-empty; **`F(A) == F(clean)` EXACTLY**; and `R(A) − F(A)` contains at least one label matching `^FPE: ` | Both refuse, so a presence test learns nothing — which is precisely why the parent's green here was worthless. The registered relation instead states that **the pre-repair matcher's hit set on a REAL SERIAL FPE CRASH is INDISTINGUISHABLE from its hit set on a CLEAN RUN**: it refused for the banner, not for the crash. Meanwhile the repaired matcher refuses for a reason (`FPE: OpenFOAM sigFpe handler frame`) the pre-repair matcher **cannot produce**. **They disagree on the REASON.** Fails if the frozen sets differ, or if the repaired matcher's refusal is not attributable to an FPE-form pattern. |
| **C-3 MPI FPE** | `F(B)` is non-empty; `R(B)` is non-empty; **`F(B) ∩ F(clean)` is NON-EMPTY** (the banner token is still doing work in the frozen refusal); and `R(B) − F(B)` contains at least one label matching `^FPE: ` | Same reason-level disagreement. `F(B) == F(clean)` is **not** registered here and would be wrong to register: form B's own text carries `"signal "`, which the pre-repair tuple matches independently of the banner, so the frozen set is expected to be a **strict superset** of `F(clean)`. Registering the weaker, correct relation rather than reusing C-2's is deliberate. |

**Every arm additionally requires `R(clean)` to be EMPTY**, re-measured inside the
contrast limb rather than inherited from the arms at `:498-512`. A contrast whose
own baseline is not established is not a contrast.

### 4.3 The narration moves INSIDE the guard

Both narration lines move **inside** the per-arm branch and print **only when the
arm's registered relation was measured and held**, carrying the measured hit sets
beside them. Where a relation fails, the successor prints the failure and the two
sets, and **prints no interpretive claim at all**. **No line of narration in
`mark_done_t16b.py` may be reachable on a path where the measurement it describes
did not hold.** That sentence is the registered acceptance criterion for §2.3.

---

## 5. Selftest specification the successor MUST satisfy

**Binding: `DONE.T16_MC_f` may not be written under T16b until every arm below
has run and printed.** An arm that prints one limb where two are specified is
registered here as a **failed control**, not a passing one. Zero `assert`
statements (L-332); refusals are explicit and carry exit 2.

**Arm S-4 is the arm this whole registration exists for: it drives D541's own
defect deliberately and requires the new guard to catch it.**

| arm | POSITIVE limb — must be SEEN | NEGATIVE limb — must NOT fire / must REFUSE |
| --- | --- | --- |
| **S-1 THE FOURTEEN PARENT ARMS, UNCHANGED** | All fourteen `expect(...)` arms of `mark_done_t16.py:442-465` run and pass: the clean case, `rc=1`, `rc=124`+capped, no `End`, missing field, stale fields, both L-342 infrastructure arms, the ExecutionTime short/long arms, and all four R-RC arms. | Any change in any of their verdicts is a **regression** and rejects the successor. These arms are V-11 and are carried byte-identically. |
| **S-2 THE THREE REPAIRED-MATCHER ARMS, UNCHANGED** | `:498-512` run and pass — clean banner → no token; serial FPE → token; MPI FPE → token. | Unchanged (V-12). |
| **S-3 CONTRAST TARGET IS A GENUINELY DIFFERENT FILE — the control the parent lacked** | Print the target's absolute path, its byte length, its SHA-256, **and the running module's SHA-256**, and require the two digests to **DIFFER**. Print the target's git blob id beside `CONTRAST_BLOB` (G-3). | **REFUSE (exit 2)** if the target is absent (G-1) or if the two SHA-256 digests are **equal** (G-2). **FAIL (exit 1)** if the blob id does not match `CONTRAST_BLOB`. |
| **S-4 THE GUARD CATCHES D541's OWN DEFECT — driven, not argued** | Drive the §4.1 guard **a second time, deliberately pointed at the running module's own path** — i.e. reproduce `mark_done_t16.py:515` exactly. The guard must return a **REFUSAL** on condition G-2, and the refusal reason must be printed. | The guard must **NOT** return refusal for the real target. **Two limbs, opposite outcomes, from one guard** — this is what proves the guard is a discriminator and not a constant. A guard that refuses everything, or accepts everything, fails this arm. The negative drive must be performed **without exiting the process**, so the arm is a measurement and not a crash. |
| **S-5 C-1, C-2, C-3 EACH DRIVEN AS A DISAGREEMENT** | Each arm of §4.2 runs, prints `F(x)` and `R(x)` in full beside the arm name, and every limb of its registered relation is evaluated and printed **individually**, so a reader can see which limb carried the arm. | Each limb is independently able to fail and a failure of **any** limb fails the arm. **A relation printed as one aggregate boolean fails this specification** — that collapse is how C-2's content would be lost again. |
| **S-6 `R(clean)` IS EMPTY, RE-MEASURED IN THE LIMB** | The repaired matcher's hit set on the clean fixture is measured **inside** the contrast limb and printed. | It must be **EMPTY**. If it is not, all three arms fail: the baseline of the contrast is gone and no disagreement statement means anything. |
| **S-7 NARRATION IS BOUND TO MEASUREMENT** | Each narration line prints **only** inside the branch where its arm's relation held, and carries the measured sets. | On a forced failure of any arm, the corresponding narration line must **not** appear in the output. This is §4.3's acceptance criterion and is checkable by a reader against a failing run. |
| **S-8 THE RUN TREE IS NEVER WRITTEN** | Every fixture is forged into a `tempfile.mkdtemp` scratch root, and `ROOT` is restored to `HERE` in a `finally` on every path. | No path under `verification/runs/` is written by `--selftest`. The contrast target is opened **read-only** and is never imported with side effects. |
| **S-9 `-O` EQUIVALENCE AND ZERO `assert`** | `--selftest` returns the **same exit code and the same arm table** under `python3` and `python3 -O`. The AST counter reports **0** `assert` statements in the file. | The AST counter must be shown able to see a planted `assert 1` (count 1). A counter that cannot see a planted assert has established nothing (rule 3's form, applied to the counter itself). Carried from V-13. |

**S-3, S-4 and S-5 are the three arms this registration exists for.** S-3 proves
the two files are different; S-4 proves the guard that establishes that would
have caught D541's own defect; S-5 replaces two tautological greens with three
falsifiable disagreements. **A successor satisfying every other arm but not these
three has not discharged this document.**

---

## 6. Registration under `VERIFICATION_CHARTER.md` §2d.1 — the clause, and why T16b sits outside its anxiety

T16b changes a **selftest limb of a completion marker**, after first compute, on
a rung whose fine level is on disk. §2d.1 is verification's clause and is not
this lane's call. The case is stated in the clause's own four conditions, with
both readings, and stops.

| §2d.1 condition | T16b's claim | this lane's honest assessment — BOTH readings |
| --- | --- | --- |
| **(1) repairs a DEMONSTRABLE ERROR, not a preference** | The limb loads its own file (`:515`, §2.1) — an **identity error**, reproducible in one line by hashing the two paths, not a matter of taste. Its consequences are measured in §2.2 (two arms that cannot fail for the reason they name) and §2.3 (a narration line no measurement can reach). | **FAVOURABLE:** a path that resolves to the running module is wrong under any reading of what a *frozen contrast* is; there is no version of this limb's purpose that it currently serves. **UNFAVOURABLE:** a reader could hold that the limb is doing no harm — the marker marks correctly, and the FAIL is already ruled EXPECTED (§7) — so the change is cosmetic and post-compute changes should be refused on principle. **This lane's answer is §2.2:** the two tautological greens are not cosmetic; they are affirmative false statements inside a control the lab reads before believing a completion. **Neither reading is adopted here.** |
| **(2) established by an instrument INDEPENDENT OF THE HYPOTHESIS** | Three instruments, none of which knows anything about `T16_MC_f`: (i) **two file digests** — the defect is `sha256(a) == sha256(b)` and is decidable without running anything; (ii) **the parent's own selftest output**, which prints the FAIL itself; (iii) **`docs/DEAD_LEVER_AUDIT.md`**, which independently flagged this file's exposure for an unrelated reason. | **FAVOURABLE, and unusually strongly:** the defect is a **file-identity fact**, not a numerical judgement. It is true whether `T16_MC_f` completed, crashed or was never launched, and it was true on 2026-08-27, two days before that run landed. **No answer exists for it to have been steered toward** — the contrast limb produces no graded quantity and touches no verdict. **UNFAVOURABLE, stated plainly:** the *occasion* for this lane's examination was an unrecorded 2 151.95 core-min that the team wants marked. Motivation supplied by an inconvenient blockage is not the same as an instrument chosen to produce a wanted outcome, but a sceptical reader is entitled to note it. **Both readings on the table.** |
| **(3) the record discloses it, names the instrument, and QUANTIFIES what moved** | §2 discloses all three defects with line citations; §3 enumerates thirteen carried-over items and quantifies the number of gates, thresholds, bands, caps and labels that move as **ZERO**; §9 boards the two places this lane's reading differs from its brief. | **Met.** The limit this lane states rather than papers over: §3's byte-identity claim is verifiable **only by the supervisor reading the diff**, which is `SUPERVISION_CHARTER.md` §3 check 1 and is explicitly not delegable to this lane's assertion. **This document's §3 is a claim to be checked, not a check that has been performed.** |
| **(4) pre-repair values recorded beside the published ones** | The pre-repair state is recorded in full and is not restated as a repaired value: **`24 ok / 1 FAIL`, exit 1**, with the failing arm named. The parent file is preserved unedited at `efcf7852` and the historical original at `2ae1605c`; **both remain on disk and both remain runnable.** T16b's selftest must print, beside its own result, the parent's `24 ok / 1 FAIL (frozen-contrast arm)` as the pre-repair state. | **Met.** No published T16 number changes, because **the limb publishes no number.** No `DONE` marker written before T16b is invalidated by it — `DONE.T16_MC_c` and `DONE.T16_MC_m` were written by the operational path (§2.4), which T16b does not touch. |

**THE WEAKEST CONDITION IS (1) AND THIS LANE NAMES IT RATHER THAN LETTING
VERIFICATION FIND IT** — not because the error is arguable, but because a reader
may reasonably think a selftest limb too small to be worth a post-compute change.
**THE STRONGEST IS (2)**, because a digest comparison is about as independent of
a physics verdict as an instrument can be.

**NOT RULED HERE.** T16b is written for verification to rule on if the
heat-transfer supervisor refers it. §7 records why this lane believes a referral
may be unnecessary, and does not act on that belief.

---

## 7. D541's SECOND RULING — **IT WAS ANSWERED, AND THE BRIEF'S PREMISE IS CORRECTED HERE**

**This lane was briefed that D541's second ruling "never came" and that T16b
should deliberately not depend on it. The first half is wrong and this section
corrects it rather than transcribing it.**

The ruling was given on **2026-08-27**, by the heat-transfer supervisor, and is
recorded at `docs/LAB_STATE.md:9424`, verbatim:

> **My ruling `[lab-attributed]`: the FAIL is correct behaviour, not a
> regression; the retarget at `PRE_D541.py` is the right fix, is a correctness
> change and not a loosening, and lands as its own small disclosed amendment that
> I read as a diff. Until it does, the honest statement of this selftest's
> expected result is "24 ok / 1 FAIL (frozen-contrast arm, EXPECTED)" — never
> "PASS".**

`docs/DOCKET.md:906` (D541, **CLOSED**) says only *"referred up as a second
ruling"* and does not record the answer. **The docket and the board disagree, and
this lane boards that rather than picking one.** The board is the ruling
instrument; the docket row was written before or without it.

**FOUR CONSEQUENCES, STATED PRECISELY:**

1. **The retarget at `PRE_D541.py` is ALREADY RULED the right fix**, and ruled a
   **correctness change, not a loosening**. T16b implements a ruling that
   exists; it does not seek a new one for that part.
2. **The route ruled was an amendment to the frozen file.** T16b takes a
   **strictly more conservative route**: a successor file, **zero frozen bytes
   changed**. A route that changes less than the route already approved cannot
   need a wider approval than the route already approved. **This is not offered
   as permission** — no agent's message and no lane's reasoning is Sanaa's
   consent (rule 9), and the supervisor's §3 diff read is still owed and is still
   his.
3. **WHAT THE 2026-08-27 RULING DID NOT COVER, AND THIS IS THIS LANE'S OWN
   FINDING:** the ruling addresses **the single FAIL** and nothing else. It does
   not mention the two tautological greens of §2.2, nor the unbound narration of
   §2.3. **Those two defects are unruled because they were never boarded.** §5's
   arms S-4, S-5 and S-7 exist for them.
4. **T16b does not depend on that ruling for its validity.** §6 states the §2d.1
   case from scratch and stands on its own. If verification rules the 2026-08-27
   `[lab-attributed]` ruling insufficient for the retarget, **§6 is the document
   that must carry T16b**, and §5's arms are unaffected either way.

**THE HONEST STATEMENT OF THE PARENT'S SELFTEST REMAINS THE SUPERVISOR'S:
`24 ok / 1 FAIL (frozen-contrast arm, EXPECTED)` — never `PASS`.** T16b does not
retire that statement; it makes it unnecessary going forward, and the parent
keeps it for as long as the parent exists.

---

## 8. Cost — rule 12

**No solver compute is proposed. Nothing is enqueued. `T16_MC_f`'s fields, its
28 419 255-byte `log.solve`, its `STATUS` record and all three levels' artifacts
are already on disk and no re-run is implied by anything in this document.**

### 8.1 The T16b selftest — this registration's own scope

| item | figure | basis |
| --- | --- | --- |
| **POINT** | **0.003 core-min** | 1 rank. Basis: `mark_done_t16.py --selftest` **MEASURED by this lane at 0.082 s median of 3 runs** (0.090 / 0.082 / 0.078 s) = 0.00136 core-min. T16b adds one module import, one extra fixture forge, three SHA-256 digests over ≤ 600 kB and one extra guard drive — **≈ 2× the parent**, rounded up |
| **CAP / registered stop** | **1.0 core-min** | ≈ 735× POINT. **An overrun stops the run** (rule 12). A selftest that forges fixtures in `tmpfs` and has not finished in one core-minute is not slow, it is wrong |
| **USD at POINT** | **$0.00000257** | **DERIVED, NOT MEASURED** — `0.003 / 60 × $0.0513/core-h` |
| **USD at CAP** | **$0.000855** | **DERIVED, NOT MEASURED** — `1.0 / 60 × $0.0513/core-h` |

### 8.2 The marking pass — TASK 4's scope, costed here, NOT authorised here

| item | figure | basis |
| --- | --- | --- |
| **POINT** | **0.30 core-min** | 1 rank. `mark_done_t16b.py T16_MC_f` streams `log.solve` **twice** — once for the eight crash patterns, once for the `End` / `ExecutionTime` counts — over **360 066 lines / 28 419 255 bytes**, plus 4 `stat` calls for the age guard. Scaled from the `T16_MC_m` marking pass, whose log is ~½ this size |
| **CAP** | **5.0 core-min** | ≈ 17× POINT |
| **USD at POINT** | **$0.000257** | **DERIVED, NOT MEASURED** |

The rate **$0.0513/core-h** for c7a.4xlarge is **owner-stated,
reported-by-owner, NOT measured**: **the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5). **Three ten-thousandths of a cent cannot be a
reason to rule §6 either way**, and it is recorded here so that no ruling is ever
taken under cost pressure.

### 8.3 The parent run's actual — recorded, not re-opened

`T16_MC_f` spent **2 151.950 core-min MEASURED** (`STATUS.T16_MC_f`,
`wall_s=129117` × `ranks=1` ÷ 60), **$1.83992 DERIVED, NOT MEASURED** at
$0.0513/core-h. Its registered figures are POINT **1 063.103** core-min, CEILING
**1 603.994**, CAP **2 400** (`T16_registered.json`, `cases.T16_MC_f`), giving
**actual / POINT = 2.024×** and **0.897 of the CAP**, `capped=no` — **no
overrun.** **The calibration row for this level is OWED and is deliberately NOT
written here:** rule 12 requires it *at process completion*, and the process is
not complete until the level is marked and the rung graded. Writing it now would
repeat the `C-179`/`C-170` duplication that `C-180` withdrew. **The row must
grep the ledger for the process key `T16_MC_f` before it is appended, not merely
re-derive a free id** — `C-180`'s own lesson.

**T16b's own arithmetic is not waste and does not re-spend anything:** the
2 151.95 core-min are on disk. A defect in a selftest limb costs **zero
core-minutes** to repair, exactly as `C-179` measured for D541 itself.

---

## 9. Differences between this lane's reading and the brief it was handed — BOARDED, not silently adopted

**B-1 — THE SECOND RULING WAS ANSWERED. The brief's central premise is
corrected.** The brief states the D541 second ruling *"never came"* and that
T16b should be built so as not to wait for it. **It came on 2026-08-27**, is
quoted verbatim in §7, and rules the `PRE_D541.py` retarget *"the right fix …
a correctness change and not a loosening."* The brief's **disposition** is
nonetheless correct and is followed unchanged: a successor registration needs no
ruling, and the ruling that exists covers only the FAIL, not §2.2's tautological
greens. **The correction strengthens T16b's position and is recorded because a
document that understates its own authority is as inaccurate as one that
overstates it.**

**B-2 — "IT CANNOT BE MARKED DONE" IS TOO STRONG.** The brief says `T16_MC_f`
*"cannot be marked DONE because `mark_done_t16.py --selftest` FAILS."* The marker
**can** mark it: the same blob `efcf7852` marked `T16_MC_c` and `T16_MC_m` at
exit 0, and the supervisor's 2026-08-27 ruling already declares the FAIL EXPECTED
and correct behaviour, which would make such a marking legitimate under
disclosure. **The accurate statement is that the team declines to rest a marking
on a guard whose contrast limb carries two green lines that are evidence of
nothing** — a stricter and better-founded position than the brief's, and the one
this document registers.

**B-3 — every other figure in the brief reproduces**, re-derived by this lane
from the artifact named: `2 151.95` core-min, the `2026-08-29T14:13:00Z` landing,
35h52m (129 117 wall s), the minimum age margin **`+129 116.85 s`** on `U`, all
six rule-4 conjuncts, `24 ok / 1 FAIL` at exit 1, the `:515` self-load, the
narration at `:540-541` sitting outside the loop, blob `efcf7852` == HEAD, blob
`2ae1605c` on disk, and **no `.py` anywhere in the repository naming
`PRE_D541`** — the target is referenced in prose alone, in four `.md` files and
in no executable check. **T16b is the first executable reference to it**, which
is why §4.1's G-1 is a refusal: a target nothing asserts is a target that can be
deleted without anything noticing.

---

## 10. What this document does not do

- It **does not** edit, amend or supersede any frozen file. `mark_done_t16.py`
  (`efcf7852…`) and `mark_done_t16.PRE_D541.py` (`2ae1605c…`) are byte-identical
  to their HEAD blobs, verified in §1, and stay that way. **Zero frozen bytes
  change.**
- It **does not** amend `T16_PREREGISTRATION.md` (`18485ab4…`). No addendum, no
  version bump, no struck row.
- It **does not** move a gate, band, floor, threshold, cap, timeout, label,
  field tuple, crash pattern, exit code or physics conjunct. §3 enumerates
  thirteen carried-over items; the count that moves is **ZERO**.
- It **does not** repair D547. `"Aborted"` and `"signal "` stay unanchored, OPEN
  BY CHOICE, for D547's stated reason.
- It **does not** mark `T16_MC_f`, write any `DONE` marker, run `analyse_t16.py`,
  grade any row of T16, enqueue anything or launch any compute. **T16 stays
  `PENDING`.**
- It **does not** invalidate `DONE.T16_MC_c` or `DONE.T16_MC_m`, which were
  written by the operational path T16b does not touch (§2.4).
- It **does not** write the `T16_MC_f` calibration row. That row is owed at
  process completion and must grep the ledger for `T16_MC_f` first (§8.3).
- It **does not** treat the supervisor's 2026-08-27 `[lab-attributed]` ruling, or
  any agent's message, as Sanaa's consent (rule 9). The supervisor's §3 check-1
  diff read is owed, is his, and is not discharged by anything in this document.
- It **does not** rule `VERIFICATION_CHARTER.md` §2d.1. That is verification's
  clause.
- It **does not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).
