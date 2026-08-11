# Ladder V — V15 round 6: the claims audit over the round-6 text

**Auditor:** a fleet agent that wrote none of the text under audit. **Subject:** every
commit since `2026-08-11 00:00`, from `656c09c9` to `2266c4e3` (HEAD moved five times
during the sweep as other agents committed; every measurement below names the commit it
ran at). **Executed 2026-08-11, 21:30–22:20 UTC.** No solver, no compute, nothing sent.

**The verdict the termination rule asks for is a number, and it is not zero.**

---

## 0. The positive control, first

A sweep that finds nothing must first be shown able to find something. Two methods were
used in this round and both were controlled before they were trusted.

### 0.1 Artifact resolution (does the named artifact exist?)

A scratch document was written carrying three claims of a class V15 must catch and three
that must not fire, then run through the resolver:

| plant | class | caught? |
|---|---|---|
| `scripts/check_converge_rule.py` — file does not exist | path | **yes** |
| `test_r_isolate_worktree_is_pruned_from_every_frame` — no such def | test | **yes** |
| `deadbee1`, `c0ffee99` — do not resolve | commit | **yes (both)** |
| `scripts/sweep.py` | real path | correctly silent |
| `test_unreadable_file_forces_unknown_not_zero` | real test | correctly silent |
| `83ed6dab` | real commit | correctly silent |

**4 of 4 plants caught, 0 of 3 true references falsely flagged.**

### 0.2 The W-5 detector (present-tense state claim without a commit anchor)

Four planted paragraphs: one unanchored state claim about a file, the same claim with an
anchor, a rule (which §8.1a exempts), and an unanchored state claim about a check.

**2 of 2 plants caught; the anchored one and the rule both correctly passed.** The first
version of this detector flagged the rule as well — the exemption was widened to any
deontic modal in the unit, which under-reports, which is the safe direction for a defect
count. That miss is declared rather than tuned away.

### 0.3 The placement guard (D4), before committing

`board_placement_faults` from `HEAD:scripts/self_audit.py`, board `deb91557`
(`reissmann` 1, `wu` 2, `liu` 3, `montoya` 4). The control sentence is **assembled from
split tokens rather than spelled out here**, per D4:

```python
name, rank = sorted(board.items(), key=lambda kv: kv[1])[0]   # rank-1 entrant
plant = f"On the closure board, {name} is in " + "sec" + "ond pl" + "ace."
```

→ **rule A 1 fault, guard ARMED.** `docs/DOCKET.md` after my edits → **rule A 0, rule B 0**;
this document → **rule A 0, rule B 0**.

**This check caught me.** The first draft of this section quoted the planted sentence in
full and the guard faulted my own write-up — which is D4's exact recorded shape, *"the
prose about them spells a placement in full"*, now on its sixth file in six agents.

---

## 1. The surface, derived — and the orientation list was incomplete

Derived mechanically from `git diff --name-status 656c09c9^..HEAD`, not from any list.

**169 files: 92 added, 77 modified.** Of these, 123 are prose-bearing
(`.md/.py/.sh/.tex/.html`), 61 of them newly created.

**What the orientation list missed, and it matters.** The list named the ladder rules, the
E2 ruling, three charters, `MEMORY_ARCHITECTURE.md`, `docs/DOCKET.md` and "roughly fifteen
audit and record documents". The derived surface additionally contains **eight external,
travelling or machine-read surfaces** that no hand list mentioned:

```
demo-output/website/closure.html              demo-output/website/benchmarks.html
demo-output/website/benchmarks.json           demo-output/website/wall/wall.json
demo-output/website/latex/closure_challenge_report.{tex,pdf}
demo-output/website/latex/dafoam_defect_report.{tex,pdf}
demo-output/website/closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md
dist/certonomous-demo.zip
```

`dist/certonomous-demo.zip` is a **tracked shipping archive modified this round**. That is
the same object class A14/A15 was written about after the ladder previously missed one.
The two `.tex` files alone carry **241 unbacked absolutes on lines added this round** —
more than any document except `PRODUCT_LIST.md` and `LESSONS.md`.

**This is the rung working:** a hand list of "the largest new texts" is not the surface,
and deriving it found the shipping archive and the two report sources that the list did
not name.

---

## 2. Failures, ranked by whether an outside reader would act on them

Ranked hardest-first: things that are **wrong**, not merely unverified.

### F1 — The instrument built to enforce L-76 cites thirteen tests that do not exist, and cannot catch itself doing it (docket D32)

`scripts/check_absolutes.py`, written this round, exists to enforce *"no absolute without
an executed check named beside it."* It backticks **13 distinct `test_*` names under the
literal word "Evidence:"**.

**0 of the 13 resolve to a `def` in any `.py` on disk.** Frame: `find` under the repo
root, `.git` and `.claude/worktrees/` excluded; the same sweep finds **1,459 real test
defs**, so the finder works.

And its own rule does not hold in its own code. The module states:

> *"a cited test that does not exist is reported as its own class,
> `CITES_MISSING_CHECK`, and is counted as unbacked — a name that resolves to nothing is
> a worse claim than none."*

`classify_unit` evaluates `elif resolved:` **before** `elif dangling:`. A single runnable
command anywhere in the same prose unit therefore launders every dangling name into
`BACKED`. Run on itself: **BACKED 15, CITES_MISSING_CHECK 0.**

**Injection control, both directions:**

| unit | verdict |
|---|---|
| `This never fails. Evidence: `test_does_not_exist_anywhere_at_all`.` | `CITES_MISSING_CHECK` |
| the same, plus `python3 scripts/check_absolutes.py --frame tracked` | **`BACKED`** |

The module's `resolved` list for its own docstring is `['<command>', 'path.py:function']`
— and `path.py:function` is the metasyntactic placeholder from its own prose, matched by
its own `FILE_FUNC_RE`.

**Why this ranks first.** Every `BACKED` this checker has reported is unsafe, and B3a's
published 74% false-positive rate was measured on `UNBACKED` only. `CITES_MISSING_CHECK`
has no measured rate at all — and on the round-6 surface **81 of 100 of its firings cite a
name that is a tracked test-*file* stem** (`test_rank_claim_surfaces`,
`test_fail_open_scan`, `test_head_engineer`), i.e. an artifact that exists. An 81%
false-positive rate on an unmeasured defect class, sitting under a 74% figure that does
not cover it.

### F2 — A published zero is false, and the recommendation resting on it would break a citation (docket D33)

`docs/TRACKED_ARTIFACT_SCOPING.md:69` publishes **0** log files cited by exact path, and
§5 recommends *"Move solver **logs** first — 778 files, no path citations."*

Re-executed with a broader citation vocabulary — every path-like token in all 372 tracked
`.md` files, rather than only `*_runs/`-shaped tokens — finds **one**:

```
demo-output/website/tmr/runs/naca-a10-medium/log.checkMesh
  cited at demo-output/website/tmr/C4_naca0012_closure.md:80
```

Tracked, cited by exact backticked path. The published harvester misses it because the
path sits under `tmr/runs/` — no underscore, so it matches no `*_runs/` token. §4 of that
document lists three ways the measurement could be wrong; the restricted vocabulary is not
one of them, and the frame does not state it.

**The sibling claim holds and should be said so.** 0 of the 8,582 solver-output files are
cited by exact path under the broad vocabulary too, and `scripts/corpus_figures.py`
reproduces **8,582 exactly** at `2266c4e3`. The document's largest number is sound; its
zero is not.

### F3 — Docket E1's headline correction is the error (docket D34)

> E1: *"MEASURED 2026-08-11: it is **31 of 34**, not 30 … Three state one; thirty-one
> state none."*

Executed all 34 callables in `scripts.self_audit.CHECKS`, searching `summary` and `detail`
for a blind-spot marker:

**4 state one. 30 state none. 0 raised.** — `check_rank_claim_surfaces`,
`check_board_placement_words`, `check_record_writers_name_their_drops`,
`check_every_check_states_its_basis`.

**This is not rot.** `scripts/self_audit.py` **as of `e551f68f`, the commit that filed
E1**, replayed against the current tree gives the same **4 / 30**, and all four emitters
already existed at that commit. E1 corrected a right number to a wrong one, in the
direction that makes its own finding sound worse, and it contradicts
`INSTRUMENT_INTEGRITY_LEDGER.md:25` and `LEDGER_HEADLINE_AUDIT.md:437` — both of which say
30 / 4 and both of which are right.

E1's own paragraph brags about the positive control that caught its first false zero. The
corrected method still undercounted by one. E1 also carries no commit anchor, which is W-5.

### F4 — Two mission classes declared at the smallest gap in the data (docket D35)

`docs/MISSION_TOKEN_COSTS.md`: *"There are two mission classes here, not a spectrum"* —
given as **88k–160k** and **164k–309k**.

Sorted, the twelve token totals are `88, 103, 157, 160, 164, 168, 185, 196, 197, 228, 249,
309`. The claimed split is the `160 → 164` gap:

| | gap | rank among the 11 gaps | share of range |
|---|---:|---:|---:|
| **claimed token split** | **4k** | **8th of 11** | **1.8%** |
| largest token gap (inside the "homogeneous" class 2) | 60k | 1st | 27% |
| tool-call split `5 → 33` | 28 calls | **1st of 11** | **40%** |

The token distribution is **continuous across the declared boundary**. The finding is real
and the axis is wrong: the discriminator is tool calls, and the document half-notices this
("*10× the tool calls*") while stating the class ranges in tokens first. Secondarily,
class 2 is described as *"15 to 22 minutes"* while containing its own 27-minute and
62-minute rows.

### F5 — R-ISOLATE's own worktree silently doubles the frame-stating instrument (docket D36)

`.claude/worktrees/agent-ad85b7e8a54a4a57b/` is a **full second copy of the repository** —
20,579 files, checked out at `0a51269d`, ~3.5 hours behind `main`, excluded via
`.git/info/exclude` rather than `.gitignore`.

Measured at `64281b6b` against the docstring's figures at `83ed6dab`:

| frame | docstring, `83ed6dab` | measured, `64281b6b` | inflation |
|---|---:|---:|---|
| `everything` | 59,560 | **80,493** | **+35%** |
| `worktree` | 58,083 | **78,414** | **+35%** |
| `tracked` | 20,562 | 20,594 | unaffected |
| `ignore-honouring` | 13,626 | 13,658 | unaffected |

A sweep for `R-ISOLATE` over `*.md` returns **8 matching files under `worktree`, 4 under
`tracked`** — exactly 2×, because it is the same four files twice.

The `worktree` frame's own words are *"drops .bzr/.git/.hg/.jj/.sl/.svn directories"*. It
prunes `.git` **directories**; a nested worktree's metadata is a `.git` **file**, so the
walk goes straight in. The docstring's numbers are anchored and so merely dated — but any
`everything` or `worktree` sweep run today double-counts silently. **This is L-75
reintroduced by R-ISOLATE, the rule written the same evening, into `scripts/sweep.py`, the
instrument written the same evening to prevent the class.**

### F6 — The four standing rules conflict with the charters in six places, and no code enforces any of them (docket D38)

Frame: `git ls-files` + `/usr/bin/grep` for `R-ISOLATE|R-CONVERGE|R-DEPTH|R-VALUE` —
**15 files match. All markdown, plus two test *fixtures* and one docstring mention. No
script, hook, test or dispatch template enforces any part of any of them.**

Against `SUPERVISION_CHARTER.md:136`, written the same evening — *"A rule without a sweep
is a preference"* — all four are currently preferences. And
`LADDER_V_TRIPLE_VERIFICATION.md:213`, *"R-ISOLATE, four parts, **all mechanical**"*, is an
absolute with no executed test beside it, which is L-76 in the rule text itself.

The six conflicts:

1. **`PASS WITH RESIDUALS` is a sixth gate verdict** against `VERIFICATION_CHARTER.md:95`
   *"The verdict vocabulary is fixed."* §16's negative-verdict-review sweep enumerates that
   fixed vocabulary, so **residuals are invisible to it by construction.**
2. **R-VALUE's closing condition is satisfied by R-ISOLATE's own documented fail-open.**
   R-VALUE closes on two rounds returning only findings that would not change a reader's
   belief; R-ISOLATE's fail-open shape is *"an honest, confident, empty result."* Two rules
   in one document, neither citing the other.
3. **R-CONVERGE requires closure declared *before* the first grade**; the E2 ruling in the
   same file sets E2's closing condition **after six rounds**, which
   `VERIFICATION_CHARTER.md:156-164` (§2b) forbids explicitly.
4. **R-DEPTH caps meta-work at depth 2 with no exemption**, while `SUPERVISION_CHARTER.md`
   §3 checks 1 and 3 mandate depth-3 supervisor work *unconditionally*, and A15 mandates it
   too — V16 rounds 5–7 ran exactly that. R-DEPTH supplies no depth-counting method and no
   worked example.
5. **Two live documents are both "the docket", definite article.** `LADDER_V:189` says
   `docs/DOCKET.md`; `ESCALATION_CHARTER.md:85` says
   `demo-output/website/agenda/docket.json`. They overlap on substance — `DOCKET.md` §A2's
   compute authorisation is verbatim ESCALATION §3's routing — and neither names the
   collision, against `MEMORY_ARCHITECTURE.md:613` *"A fact has one home."*
6. **None carries the archive replay and fire rate** that `VERIFICATION_CHARTER.md:622` and
   §16 rule 2 require before a rule is adopted.

**On R-ISOLATE's two amendments specifically, since the rung asked.** Amendment 1 adds a
real mechanism — *"the agent asserts `git merge-base --is-ancestor <subject> HEAD` before
executing anything"* — and it demonstrably catches its case (D19 records the failing
invocation). **Amendment 2 does not.** It says *"pair the ancestry check with a content
check"* with no command, no defined file set, and it leaves in force the stop-order that
caused the incident: amendment 1 says the agent *stops* on ancestry failure, so an agent
obeying it never reaches amendment 2's content check. The actual remedy sits in D21 as
unexecuted work owned by "fleet". The third failure mode — a grade stranded on an unmerged
branch — gets a stated duty and **no mechanism at all.**

### F7 — A charter version register rotted into misquoting the charter it registers (docket D37)

`docs/MEMORY_ARCHITECTURE.md:852` reads ``​`VERIFICATION_CHARTER.md:3` (*"Version 1.6,
dated 2026-08-11"*)``. Line 3 actually reads *"Version 1.8, dated 2026-08-11."*
(`2d0e5260` → 1.7, `be1b955c` → 1.8, both today.) **The lab's own register of stale date
literals rotted in exactly the manner it documents.**

Same class, adjacent: `VERIFICATION_CHARTER.md`'s version-history block covers **1.1–1.6
only** — sections **2a, 2b and 6a appear in no changelog entry**, breaking a convention
every prior bump kept. And three surfaces still cite `SUPERVISION_CHARTER.md` as **v1.0**
after today's 1.1 bump: `docs/charters/PROPOSALS_OPEN.md:37`,
`docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md:113`, `docs/PRODUCT_LIST.md:512`.

---

## 3. The counts, each with its frame

### 3.1 L-76 — absolutes with no executed test beside them

**Frame:** lines **added** by commits `656c09c9^..HEAD`, in tracked
`.md/.py/.sh/.tex/.html` files. **127 files, 32,549 added lines.** Classifier:
`scripts/check_absolutes.py` at defaults. A claim is attributed to this round only when its
line number falls in that file's added-line set.

| | count |
|---|---:|
| absolutes on added lines | 3,706 |
| `UNBACKED` | **1,307** |
| `CITES_MISSING_CHECK` | 73 — of which **59 false-positive** (the cited name is a tracked test-*file* stem), 14 nominal |
| **raw L-76 defects introduced this round** | **1,380** |
| **after B3a's own measured 74% false-positive rate on `UNBACKED`** | **≈ 340** |

Top contributors: `docs/PRODUCT_LIST.md` 198, `LESSONS.md` 84, `V16_GRADE.md` 67,
`LADDER_V_V13_CLOSEOUT.md` 51, `scripts/self_audit.py` 49, `LADDER_V_V15_ROUND4.md` 42,
`docs/DOCKET.md` 37, `LADDER_V_TRIPLE_VERIFICATION.md` 35.

**I do not offer 1,380 as the failure count.** It is a raw instrument reading from an
instrument I have just shown (F1) to be miscalibrated in both directions. ≈340 is the
honest estimate and it carries the checker's own uncertainty.

### 3.2 W-5 — unanchored present-tense state claims

**Frame:** the **61 documents created this round** (`--diff-filter=A`, `.md`/`.py`). Unit =
blank-line-delimited paragraph. A paragraph is flagged when it names a resolvable repo
artifact in backticks, carries a present-tense state verb, and contains neither a
git-resolvable commit-shaped token nor a dating phrase. Rules and definitions are exempt
(any deontic modal in the unit), which under-reports.

**263 unanchored present-tense state paragraphs in 52 of the 61 new documents.**

W-5 landed at `6d990fdc`, 21:01 tonight, so text written earlier today predates it and is
*expected* to violate it. That is the rung's own instruction and the number is reported,
not repaired. What is worth noting is the **asymmetry**: the grade documents anchor
routinely (*"Executed against subject `5ef1fd1a`"*, *"As of `64281b6b`"*), and the **rule
and ruling text does not** — including `LADDER_V:189` *"The docket is `docs/DOCKET.md`"*,
which is unanchored and already false-by-collision (F6.5).

---

## 4. What I checked and found SOUND

An audit that reports only failures is not an audit.

- **`0 of 3` proposals hit the 20% calibration bar** — `scripts/calibration_scorecard.py`
  reproduces exactly: three scoreable pairs, 64.9% / 20.7% / 34.4% off, hit rate 0 of 3,
  and the §4 rule correctly reported as runnable-but-unsatisfied. The document's real
  finding — 16 done proposals carry no measured cost — reproduces too.
- **`8,582` tracked solver-output files** — `scripts/corpus_figures.py` reproduces the
  figure exactly at `2266c4e3`. My own independent regex gave 12,000; the generator wins,
  as `TRACKED_ARTIFACT_SCOPING.md` §1 says it should, and my regex was the over-broad one.
- **0 of 8,582 solver-output files cited by exact path** — holds under a *broader*
  vocabulary than the one published (all path-like tokens, all 372 tracked `.md`).
- **`scripts/sweep.py`'s `tracked` and `ignore-honouring` frames** — 20,594 and 13,658
  today against 20,562 and 13,626 at `83ed6dab`; the +32 is one day of commits. The
  `6,938 tracked-and-also-gitignored` figure reproduces **exactly**.

---

## 4a. Containment: none of the four wrong figures reached a travelling surface

Checked explicitly, because a wrong number on an external surface is FAIL severity and a
wrong number in a lab record is not. Searched `closure.html`, `benchmarks.html`, both
`.tex` report sources, `wall/wall.json`,
`closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md` and
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` for `31 of 34`, `thirty-one`, `88k`, `160k`,
`no path citations` and `8,582`: **zero hits on all six.**

`dist/certonomous-demo.zip` was last rebuilt at `b9233e51`, **02:08 UTC** — before any of
the four wrong claims was written (16:31–21:05). The tracked shipping archive does not
carry them.

**All four failures are contained to lab records.** That is the good news in this report,
and it is the reason F1–F4 are corrections rather than withdrawals.

---

## 5. The verdict

**The termination rule wants zero new failures. It is not zero.**

| class | new failures introduced by round-6 text |
|---|---:|
| Claims about execution that re-execution **refutes** | **4** (F1 citation set, F2, F3, F4) |
| Instrument defects introduced this round | **3** (F1 verdict ordering, F1 `CITES_MISSING_CHECK` precision, F5) |
| Cross-document contradictions among the four new standing rules | **6** (F6) |
| Charter-version register rot | **1** (F7) |
| **Discrete, individually actionable failures** | **14** |
| L-76 unbacked absolutes on added lines (raw / FP-corrected) | 1,380 / ≈340 |
| W-5 unanchored present-tense state paragraphs in new documents | 263 |

**Fourteen discrete failures, seven of them filed as docket D32–D38.** Four are claims that
were **wrong when written**, not merely unverified — F1's thirteen citations, F2's zero,
F3's 31-of-34, F4's split point. All four are the chief's.

**The ladder is not green, and the concentration is the story.** Four standing rules and
roughly fifteen documents written by one agent in one evening produced: a rule set that
conflicts with the charters in six places and is enforced by nothing; an L-76 enforcer
whose own evidence is fictional and whose own missing-check class cannot fire on it; and an
isolation rule whose leftover worktree corrupts the frame-stating counter written the same
evening. **The fix pass became the last unverified writer, which is precisely the risk this
rung was created to catch.**

Two things should be said in the chief's favour. The **numbers** are largely sound — the
big ones (8,582, 0 of 3, the sweep frames, 6,938) all reproduce, some exactly. The failures
are concentrated in **inferences drawn from good numbers** (F4), **zeros produced by
unstated filters** (F2), **evidence promised and not written** (F1), and **rules written
faster than they could be reconciled** (F6). That is a different and more fixable disease
than bad measurement.

**What zero would take.** F1, F2, F3, F4 and F7 are corrections the chief can make tonight.
F5 needs a frame fix and a test. **F6 items 1 and 3 are charter amendments and are Katie's**
— a rung cannot close over a rule set that contradicts the charter defining what closing
means.

---

*Nothing in this round was sent, filed, uploaded or published. Submission is PARKED and
reserved to Katie.*
