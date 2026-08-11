# Sweep reframe audit — every published `grep`-derived count, re-run under a frame that states itself

**Date:** 2026-08-11. **Tool:** `scripts/sweep.py` (landed at `85cc1078`), which
returns no count without its frame. **Frames used below**, all four measured at
commit `83ed6dab`:

| frame | selects | reach at `83ed6dab` |
|---|---|---|
| `everything` | every non-directory entry under root, dotfiles and `.git/` internals included | 59,560 files |
| `worktree` | the same, minus VCS metadata directories | 58,083 files |
| `tracked` | `git ls-files` — honest about being tracked-only | 20,562 files |
| `ignore-honouring` | the walk minus paths `.gitignore` excludes — **a model of what `grep -r` in this environment actually sweeps** | 13,626 files |

6,938 tracked files are *also* gitignored, and `grep -r` here skips them despite
their being in the index. Reproducing that requires `git check-ignore --no-index`;
without `--no-index` git consults the index and under-reports the filter, which is
why the model above uses it.

**Why this audit exists (L-75).** `grep` in this environment is a shell function,
not `/usr/bin/grep`. It execs `ugrep -G --ignore-files --hidden -I
--exclude-dir=.git …`, and `--ignore-files` honours `.gitignore`. Re-verified here
with my own planted control before building on it: one token written to
`visible.txt` and to `ignored/f.txt` with `ignored/` in `.gitignore` — `grep -rl`
returned only `visible.txt`; `find . -exec /usr/bin/grep -l` returned both. A
second plant, a file both tracked and gitignored, is skipped too.

**Population.** 17 published sweeps whose count or null was offered as evidence,
found by reading every tracked `.md` that names a `grep`/`zgrep` invocation
(`tracked` frame, 357 files, complete — 0 skipped). **4 moved (§1). 10 held (§2).
3 UNFRAMED (§3).** The three add to seventeen; an earlier revision of this line read
16 / 4 / 9 / 3 and did not, which is the arithmetic this document exists to catch and
is corrected in place rather than quietly.

Two of the four movers are frame defects. Two are staleness — the sweep was right
when it ran and the tree moved under it (L-79). Both kinds are reported, because a
reader acting on either is acting on a false sentence.

---

## 1. Conclusions that MOVE

### 1.1 A4's Ahmed provenance — the recorded command could not have returned the recorded result

`demo-output/website/dafoam/ladder-a/A4_ahmed_body.md:7`, quoted as the load-bearing
evidence at `demo-output/website/campaign/AHMED_BODY_RECONCILIATION.md:105`.

> *"`grep -ril ahmed` under `demo-output`, `mission-output`, `models`, `sdk` turned
> up a real, already-validated Ahmed body case: `mission-output/geometry-study/study-ahmed_25/`."*

| frame | `mission-output/` files considered | files matching `ahmed` |
|---|---|---|
| `worktree` (honest) | 8,625 | **36 files / 77 lines** |
| `ignore-honouring` (what `grep -ril` sweeps) | **0** | **0 — verdict ZERO over ZERO** |

`mission-output/` has been in `.gitignore` since the repository's **first commit**,
`5336dd57` (2026-07-21T21:10:16-04:00) — a week before A4's own date of 2026-07-28
— and `git ls-files mission-output/` returns **0 files**. The wrapper `grep` cannot
see one byte under that directory. **10 of the 36 matching files are inside
`study-ahmed_25/` itself**, including the `ahmed_25_field.json` whose numbers A4
quotes: the evidence is not merely present, it is abundant, and the recorded command
returns none of it.

**The finding is sound and the provenance is not.** The case is real, on disk, and
exactly where A4 says. But the search that found it was not the search A4 records:
a `grep -ril` under `mission-output` in this environment returns nothing, over
nothing. This matters because `AHMED_BODY_RECONCILIATION.md` cites that sentence to
argue A4 is *scoped rather than wrong*; the sentence it leans on describes a
method that does not reproduce.

*What to correct:* the recorded command, not the finding. `grep -ril ahmed` →
`find … -exec /usr/bin/grep -ril ahmed`, or state that `mission-output/` was
searched by another means.

### 1.2 "18 files agree" is 121 files — and the lesson is more right than it knew

`LESSONS.md:1230`, corollary 1 of the fvOptions sign lesson.

> *"Grep the count (`grep -rl "eqn += " --include=fvOptions`) and treat **"18 files
> agree"** as one fact, not eighteen."*

| frame | `fvOptions` files considered | matching `eqn += ` |
|---|---|---|
| `everything` / `worktree` | 162 | **121 files, 223 lines** |
| `ignore-honouring` | 50 | **18 files** |
| `tracked` | 50 | 18 files |

The published 18 is precisely the ignore-honouring figure. The honest figure is
**121, of 162 `fvOptions` dictionaries** — 103 of them under the gitignored
`f6d_random_matrix_uq/` tree.

**The conclusion moves in magnitude and in the direction that strengthens it.**
"Copying a dictionary copies its reassurance along with its bug" is 6.7× more true
than the lesson says: one comment was copied 121 times, not 18. The *advice* stands
unchanged; the number quoted beside it is a `grep -r` number and should read 121
under the honest frame, or be scoped explicitly to the band (see §2.1).

### 1.3 `dist/` no longer carries zero `2026-08-11` — and the sweep was right when it ran

`demo-output/website/campaign/LADDER_V_V15_ROUND2.md:201`, finding P11.

> *"Opened `dist/certonomous-demo.zip` with `zipfile` and read **every member**:
> **zero** occurrences of `2026-08-11`. `/bin/grep -rn` over the unpacked
> `dist/certonomous-demo/`: zero. The rebuild at `a1545dbd` (21:39:49) did absorb it."*

Re-derived at HEAD, by the published method and by the `everything` frame:

| measurement | published | now |
|---|---|---|
| zip members containing `2026-08-11` | 0 of 103 | **1 of 103** |
| unpacked tree, `/bin/grep -c` | 0 | **1** |

The survivor is `certonomous-demo/mission-output/aircraft-optimization/certificate.pdf`,
whose generation timestamp reads `2026-08-11T02:04:59Z`. The committed zip carries
it too, so this is not a working-tree artefact.

**This is not the ignore filter — it is L-79.** The claim credits the rebuild at
`a1545dbd`, which is dated **2026-08-10T21:39:49**. The bundle was rebuilt *again*
at **`b9233e51`, 2026-08-11T02:08:31**, four minutes after that certificate was
generated, and that rebuild is what brought the string in. P11 was true when
written and the artifact moved under it two hours later.

**Substance stands, figure is stale.** The thing P11 was checking — that no stale
*corrected date* survives in the shipping bundle — is still true; the one occurrence
is a legitimate build timestamp, not a date claim. But "zero" is now "one", and a
reader checking P11 by re-running it will not get P11's answer.

### 1.4 Prior art: "the three apparent code hits" are six

`demo-output/website/CLOSURE_CHALLENGE_PRIOR_ART.md:204`, repeated verbatim at
`demo-output/website/campaign/LADDER_V_PASS2_2026-08-11.md:304`.

> *"`grep -rniE "buchanan|RITA|2504\.06758|lacatus"` over the tree returns **zero
> hits in any executable file**. The three apparent code hits
> (`sdk/chief_engineer/uq.py`, `sdk/chief_engineer/openfoam.py`,
> `sdk/scripts/closure_eval_battery/build_master_table.py`) are substring matches
> inside the word autho**rita**tive."*

Restricted to executable extensions (`*.py *.sh *.js *.C *.H *.c *.h *.cpp *.bash *.pl *.rb`):

| frame | files considered | hits |
|---|---|---|
| `worktree` (honest) | 1,924 | **6 files / 6 lines** |
| `ignore-honouring` | 567 | 4 files / 4 lines |

Whole-tree, all file types: `worktree` 117 files / 188 lines (verdict UNKNOWN, see
§4) against `ignore-honouring` 105 / 176.

**The conclusion HOLDS. Its stated evidence does not.** All six executable hits are
the substring inside *autho**rita**tive*; there is no real hit in any executable
file under a frame 3.4× wider than the one that produced the claim. The data-file
hits are the benchmark paper's author list (`McConkey, Buchanan, Smidt, …`) in
three `demo-output/website/agenda/*.json` records — a citation, not an Appendix-D
coefficient. So *"no Appendix-D coefficient, and no artifact of that model, exists
anywhere in this repository"* survives re-derivation at a wider reach than it was
asserted at.

But the enumeration of apparent hits is wrong, and **not only because of the ignore
filter**. Two of the three extra files are copies inside the gitignored
`dist/certonomous-demo/` tree — those `grep -r` genuinely could not see. The third,
`demo-output/website/campaign/F12_runs/reference/decode_tape.py:26`, is **tracked,
not ignored, and inside `grep -r`'s own reach**; it entered at `5a1e6bf3`
(2026-07-30), eleven days before the claim. A sweep that named three hits when its
own frame contained four was not fully enumerated.

---

## 2. Re-runs that change nothing

Each of these was re-derived under the honest frame and returns what it published.
That is a real result and it is the majority result.

### 2.1 F6a §10.1 / F6d §4.1 — "18 dictionaries, zero use `-=`" — HOLDS exactly

`campaign/F6a_epistemic_propagation.md:652` and `campaign/F6d_random_matrix_uq.md:235`
scope their claim to `demo-output/website/dafoam/f6a_epistemic_band/`. Within that
directory: **18 of 22 `fvOptions` match `eqn += fvc::div(deltaR)`, 0 match `eqn -=`,
identical under `everything`, `ignore-honouring` and `tracked`** — the band is fully
tracked, so all three frames coincide. The 4 non-matching dictionaries are the
`channel1_rans_sweep/` cases, which carry no `deltaR` term.

*Frame note, outside the claim's scope but worth recording:* tree-wide there **are**
7 `fvOptions` using `eqn -=`, all inside gitignored
`f6d_random_matrix_uq/{signdemo,f6a_recheck}/` — the sign-corrected cases F6d itself
built. `grep -r` cannot see them by construction. The scoped claim is unaffected;
an unscoped reading of it would be false.

### 2.2 DEAD_LEVER PC-1 — HOLDS

`campaign/DEAD_LEVER_AUDIT_2026-08-08.md:410`. `adjUseColoring` under
`/home/ubuntu/certonomous-runs/W4-a4-discriminators/` (present, 837 entries):
**9 files / 13 lines**, including exactly the cited
`d_np4scotch_nocolor.log:483:  adjUseColoring  0;`.

### 2.3 DEAD_LEVER PC-3 — HOLDS, and demonstrates the whole problem

Same document, line 412: *"`command grep -rl` … under `mega-batch/work/`
(gitignored) — **PASS**, 17 files found"*. Re-derived: `everything` frame,
**17 files**, exact. And the `ignore-honouring` frame over that same directory
**considers 0 files and returns ZERO**. The author's decision to reach for
`command grep` is the difference between a positive control that fires and a
positive control that silently confirms nothing.

### 2.4 W3 QCR on the host OpenFOAM tree — HOLDS

`campaign/W3_QCR_DUCT_FALSIFIER.md:31`: `grep -rli qcr` over
`/usr/lib/openfoam/openfoam2606/src` → *"zero hits"*. Re-derived: **verdict ZERO
over 19,601 entries, 0 binary skips, 0 size-capped, 0 unreadable — a complete
sweep**, the cleanest null in this audit. (OpenFOAM ships no `.gitignore` in that
tree, so the wrapper's filter was inert there.)

### 2.5 B2 duct baseline, the frozen turbulence library — HOLDS

`dafoam/ladder-b/B2_duct_baseline.md:71`: *"a `grep -rl` across the entire repo
finds zero hits outside the `controlDict` references themselves"*.
`libfrozenIncompressibleTurbulenceModels` in `/home/ubuntu/closure-challenge-benchmark`:
**12 files, all 12 `system/controlDict`**, identical under `worktree` and
`ignore-honouring`. The 173 binary skips do not threaten it — the clone holds no
`*frozen*` file of any kind and no `.so` at all.

### 2.6 `docs/FAIL_OPEN_GATE_POPULATION.md` — HOLDS, and is the model

Published at its own stated commit `b3de90c5`, with its frame declared as
tracked-only and L-75 named. Re-derived with `git grep` **at that commit**:

| quantity | published | re-derived at `b3de90c5` |
|---|---|---|
| tracked `.py` naming `PASS`/`FAIL` | 42 | **42** |
| `def check_` lines | 44, of which 34 in `scripts/self_audit.py` | **44 / 34** |
| `except <something>` sites | 419 | **418** |

The one-line gap on the last row is worktree-versus-commit, not the ignore filter:
the published command ran `git ls-files … | xargs /usr/bin/grep` over a working tree
that held another agent's uncommitted edit. At current HEAD the same counts read 44
and 432 — the tree moved, which is why the document's decision to stamp its commit
is what makes it re-derivable at all. **This is the document every other sweep in
this audit should have been.**

### 2.7 V16_GRADE claim 7 — HOLDS

`campaign/V16_GRADE.md:774` re-ran its own completeness sweep three ways and got
*"the identical four files"*. Re-derived under `worktree` on `15 rungs|V1–V15`:
**4 files** — `LADDER_V_TRIPLE_VERIFICATION.md`, `LADDER_V_V15_LADDER_TEXT_CLAIMS.md`,
`V16_GRADE.md`, `docs/PRODUCT_LIST.md`. *(The pattern as recorded also includes
`all 15`, which alone matches 15 unrelated lines about features, faces and steps;
the rung-count subset is what the verdict rests on.)*

A re-run after this document was first committed returns **five**, the fifth being
`docs/SWEEP_REFRAME_AUDIT.md` — this file, quoting the pattern in order to check it.
The count is a property of the corpus at a moment, and an audit is part of the
corpus it audits. Stated rather than filtered out, because filtering it out is how a
census quietly stops counting itself (`IMPROVEMENT_DASHBOARD`'s orphan list, §2.10,
is the same shape caught the other way).

### 2.8 The 6,938 figure — HOLDS

`LADDER_V_TRIPLE_VERIFICATION.md:387`, `V16_GRADE.md` §8.3 and `docs/PRODUCT_LIST.md`
×2 all state **6,938 tracked-but-gitignored files**. Independently re-derived here
via `git ls-files` + `git check-ignore --no-index`: **6,938**. This is the one number
in the corpus that was already about the filter, and it is correct.

### 2.9 The `comfortab` census — conclusion HOLDS, figures have drifted

`campaign/LADDER_V_V6_V10_V14_CLOSURE.md:268`, echoed at `LADDER_V_PASS2:245` and
`LADDER_V_V15_ROUND2:279`: *"`/bin/grep -rniI "comfortab" --exclude-dir=.git .`:
**76 hit lines tree-wide, 59 under `demo-output/website/`, 15 in the closure line**."*

| measurement | published | re-derived (`worktree`) |
|---|---|---|
| hit lines tree-wide | 76 | **97** (65 files, verdict UNKNOWN — 16 files vanished mid-walk) |
| under `demo-output/website/` | 59 | **79** (48 files) |
| in "the closure line" | 15 | **not re-derivable** — the closure-line file set is not enumerated anywhere I could find |

The conclusion those figures support — *no surface describes the AR_14 lead, or any
lead, as a comfortable win* — is unaffected. The drift is the tree growing: the
published sweep explicitly excluded "this ladder's own reports", and more reports
have been written since. **The ignore filter contributes almost none of it**: the
honest frame returns 97 lines against the ignore-honouring frame's 94. This sweep
used `/bin/grep` and was right to.

### 2.10 "Sole namer, 9 of 9" — HOLDS exactly

`campaign/LESSON_PROPAGATION_L53_L57_2026-08-11.md:184`: *"`/bin/grep -rl -F <name>
demo-output docs` returns **exactly one file for each orphan, and in every case it
is this dashboard**."* Re-derived for all nine orphan directory names
(`W4-a4-localize`, `W4-repro-fromscratch`, `cache-bypass-check2-4fe617`,
`cache-bypass-check-docker2-2a0877`, `study-airliner_wing_span52-2cdf8e`,
`study-airliner_wing_span52-medium-e565e1`, `vspaero-proof`,
`yplus-check-production`, `modelform-cases`): **each name appears in exactly one
file, and in all nine cases that file is
`campaign/IMPROVEMENT_DASHBOARD_2026-08.md`.** Identical under `worktree` (46,820
files considered) and `ignore-honouring` (12,947); `docs/` returns ZERO over 122
files under both. 9 of 9, exact.

---

## 3. UNFRAMED — cannot be re-derived, and not left looking sound

| sweep | published | why it cannot be re-derived |
|---|---|---|
| `dafoam/PROOF.md:831` — `grep -rn yWall src/adjoint/` inside `dafoam/opt-packages:latest` | *"locates every place the …"* | **Container unreachable.** `docker ps` returns `permission denied … /var/run/docker.sock` from this session. Inputs exist somewhere; this session cannot open them. |
| `campaign/W3_QCR_DUCT_FALSIFIER.md:32` — `grep -rli qcr` inside OpenFOAM v2506 in the same container | *"zero hits"* | Same container, same reason. Note its host-tree twin (§2.4) re-derives cleanly, so the *conclusion* "QCR does not ship" has one of its two legs re-verified and one unavailable. |
| `campaign/DEAD_LEVER_AUDIT_2026-08-08.md:411` — PC-2, `zgrep -c "Selecting RAS turbulence model"` on *"an archived `log.simpleFoam.gz`"* | *"PASS — banner read inside gz"* | **Input unidentified.** The command is recorded; the archive it ran against is not named, and the tree holds hundreds of candidates. Any number I produced would be from a file of my choosing, not theirs. |

No figure is guessed for any of these three.

---

## 4. Two findings about the instrument, not about any one count

**A sweep of this tree cannot currently return a clean ZERO, and that is correct
behaviour.** Three full-tree sweeps run for this audit returned verdict **UNKNOWN**
rather than a count: 238 selected files raised on read in one pass, 119 in another,
1 in two later ones, and 0 in a fifth. The cause is concurrent agents — files are
created and deleted underneath a four-minute walk, so the path list goes stale
between selection and read. A re-walk minutes later found zero unreadable entries,
confirming churn rather than damage.

The point is what the old instrument did with the same races. `grep -r` prints *"No
such file or directory"* to **stderr** and continues; a `| wc -l` pipeline discards
that entirely. **Every historical repo-wide sweep in this lab absorbed an unknown
number of vanished files as "no match", silently, on top of the ignore filter.**
The new helper cannot: an unread file forces UNKNOWN and names itself.

**The size cap and binary skip are real filters and now appear in the verdict
line.** A full-tree sweep at the 4 MB default skips **794 over-size files** — many of
them plain-text solver logs — and ~2,400 binaries. Every tree-wide figure in this
audit carries those counts; none of the published figures it re-derives carried
either.

---

## 5. What this audit did not do

- It re-ran **published** sweeps. A `grep -r` count that was used in reasoning and
  never written down is out of reach by construction, and no claim is made about
  how many of those exist.
- It did not re-run sweeps over paths outside this host (§3).
- The `worktree`-frame figures here were taken between `85cc1078` and `da8d6624` on
  a tree three other agents were writing to. Per L-79 they are snapshots: the
  commit is stated so a reader can tell "true at that moment" from "true now", and
  the command to re-derive each is `scripts/sweep.py --frame worktree`.
