# Headline audit of `docs/INSTRUMENT_INTEGRITY_LEDGER.md`

**Adversarial re-check, 2026-08-11 03:22–03:45 UTC. Read-and-record: nothing in the ledger
was edited, and no instrument, script or test was modified by this pass.**

The ledger's §4.2 headline was falsified before this audit began (L-68). The dispatch was
to assume it is not the only instance, and to test **every** headline against its own body
and against the artifacts, on the L-68 question: *is the headline true standing alone,
separated from its body?*

**Result in one line: the ledger's method is sound and most of its evidence survives
verbatim re-derivation, but its titles and its round numbers do not hold as well as its
bodies do.** Of 42 headline-grade claims tested: **24 SOUND**, **9 TRUE-BUT-HEADLINE-
OVERSTATES**, **9 FALSIFIED** (one of them already withdrawn). Every falsification but two
is a *count* or a *frame*, not a fabricated defect — and two of the corrections move the
ledger's central finding in the direction that makes it **stronger**, not weaker.

---

## 0. The frame these numbers were taken over — read this before any count below

The ledger warns that its own tally was taken over a working tree carrying another agent's
uncommitted 301-line change. That warning was not enough, because **the tree moved four
times during this audit alone**:

| time (UTC) | `HEAD` | what changed under me |
|---|---|---|
| 03:10:47 | `c8d5eec4` | **the ledger's own commit** — the frame every ledger claim is about |
| 03:22:10 | `4dec8fec` | 8 commits later; the V16 rank guard and the transcript-gate fix had landed |
| 03:26:16 | `4dec8fec` | `scripts/case_preflight.sh` acquired a **190-line uncommitted fix** mid-audit |
| 03:31:38 | `4dec8fec` | `DEFECT_REACH_decomposition_cases.md` corrected at `98a39662` |
| 03:38:36 | `0cd06a4d` | the preflight fix committed; L-72 landed on exactly this hazard |

**Every number in this document is stated against a named commit.** Where a claim is about
behaviour, I ran the *pinned* source (`bash <(git show <sha>:<path>)`), never the working
tree, so nothing here is contaminated by an edit that landed while I was reading.

- **`c8d5eec4`** — the ledger's commit. Behavioural reproductions of ledger claims use this.
- **`4dec8fec`** — HEAD during my `self_audit.py` run (03:28). `scripts/self_audit.py` was
  byte-identical to `HEAD` at that moment; the run is reproducible from that sha.
- The base denominator `git ls-files '*.py' '*.sh'` = **534 at `c8d5eec4` and 534 at
  `4dec8fec`** — the one count that is stable across the whole window.

---

## 1. Control-contamination hunt — the result

**Four repointed copies of production scripts are still on disk, and only one class of them
produced a ledger claim.**

Method: every `.py`/`.sh` under both session scratchpads was matched by basename against
every tracked file, hashed, and diffed; then a content-similarity sweep looked for
production scripts copied under a *different* name.

| copy | differs from production by | which ledger claim it produced |
|---|---|---|
| `scratchpad/at_control.sh` | **line 16 only**: `OUT=` → `scratchpad/emptyout` | **§4.2 — the falsified one** |
| `scratchpad/at_control2.sh` | **line 16 only**: `OUT=` → `scratchpad/does_not_exist` | **§4.2 — the falsified one** |
| `scratchpad/gatectl/old_*.sh` (×3) | **line 16 only**: `OUT=` → three control dirs | none — made at 03:17, *after* the ledger, during the L-68 recovery |
| `scratchpad/psshim/ps` | a 4-line fake `ps` emitting a planted cmdline | none — not cited by any ledger finding |
| `scratchpad/sensitivity.py` | shares a basename with `sdk/chief_engineer/sensitivity.py` and **nothing else** | none — an unrelated settledness control |
| `scratchpad/preflight_BEFORE.sh` | **byte-identical** to `c8d5eec4:scripts/case_preflight.sh` | none — and it is **how a control should be filed** (see below) |
| `scratchpad/he_head.py` | byte-identical to `sdk/chief_engineer/head_engineer.py` | none — a read-only working copy |

**`preflight_BEFORE.sh` is worth naming as the counter-example.** It was made at 03:22 by
the agent fixing R1, it is byte-identical to the ledger-era production script (`diff` is
empty against `c8d5eec4`, non-empty against the now-fixed worktree), and **its filename
says what it is.** That is L-68's first rule satisfied: a control that cannot be mistaken
for production, because its name carries its own status. `at_control.sh` differs from
production by one line and its name says nothing — and it is the one that produced a false
headline.

`scratchpad/{pin,tree,final,oldrepo,s6sdk,v10}/` are whole-repo snapshots at other commits
(211/209/209/2/9/4 files differing from the working tree). They are **version drift, not
edited controls** — no file in them is a one-line repoint of its production twin.

**Verdict on the hunt: the control-contamination pattern produced exactly one ledger
finding, §4.2, and it is the one already withdrawn.** No second finding in the ledger is
traceable to a repointed copy. I looked for this specifically and did not find it.

**But a second mechanism did produce further defects, and it leaves different
fingerprints:** claims that were **true when first written and never re-checked before
being ranked** (§4.4, §5.3, and the whole FP-inherited column), and claims **copied from an
earlier report whose cited source does not support them** (§4.5). Those are covered below
and are L-60 recurring, not L-68.

---

## 2. Per-headline verdicts

### 2.1 FALSIFIED

**F1 — §0: "Two false greens were reproduced firsthand in this pass (§4.1, §4.2). Both are
the empty-corpus shape."**
One was. I re-ran the **shipped** gate from the ledger's own commit against its **default**
`OUT=` — no override, no copy:

```
$ bash <(git show c8d5eec4:scripts/audit_transcripts.sh)
  [REUSE] ahmed-body … [LEAK] ahmed-body … [REUSE] crm-wingbody …
  [REUSE] nasa-hump … [LEAK] unseen-geometry
  5 transcript/rule combinations to review above
```

It printed **five findings and never the word `clean`**, over the 17 transcripts that are
there (`ls mission-output/*/transcript.* | wc -l` = 17). The headline count of two is
wrong; there was one. *This confirms L-68 independently rather than restating it.*

**F2 — §4.2 R2: "`audit_transcripts.sh` reports clean over a corpus root that does not
exist".** Already withdrawn at `50127731`. Re-confirmed false above. The gate at
`c8d5eec4:63` does carry the unqualified `clean:` line the body quotes — the *code* claim
was accurate; the *production behaviour* claim was not. Fixed at `13bea68f`; the gate now
fails closed with exit 2 and prints its own denominator.

**F3 — §5 opening: "Nine reached a DAFoam adjoint stage; two were built and never
executed."**
Contradicted by its own table three rows over. A7 died in `decomposePar`, A8 died on
`dlopen`, and **A9's own row says "Never reached the adjoint linear solve"** — a line I
verified directly: `certonomous-runs/adjwall/HUMP51k/log.run` has `dRdWT Jacobian Free
created!` at line 665, **0** occurrences of `Main iteration`, **0** of `ConvergedReason`,
and ends mid-iteration at its `Jul 30 19:14` mtime. At most **six** (A1–A6) reached an
adjoint solve. *Nine is the count of attempts that were **executed**, not of attempts that
reached the adjoint.*

**F4 — §4.6 R6: "16 self-audit checks and 15 standing instruments have never been shown to
fire."**
The ledger's own §2.2 says **"Reach assumed among the standing set — 9"**, and its §0 table
needs 16 + 9 = 25 to reach the published *reach assumed* total. **15 is not reconcilable
with either.** The 16 is correct (I counted the named list). The 15 appears nowhere else in
the document.

**F5 — §2.1: "32 of the 34 checks have no test at all. Only `check_rank_claim_surfaces` and
`check_bundle_drift` are exercised by `sdk/tests/`."**
Three are. `grep -oE 'check_[a-z0-9_]+' $(git ls-files 'test_*.py')` over the tracked suite
returns `check_board_placement_words`, `check_bundle_drift`, `check_rank_claim_surfaces`.
**The ledger names the third itself, two paragraphs above** ("two more
(`check_board_placement_words`, `check_bundle_drift`) pass but carry tests"). The correct
figures for its own tree are **31 of 34** and **three**.

**F6 — §2.1: "Eighteen checks are currently non-PASS."**
Its own tally is PASS 15 / WARN 8 / FAIL 8 / INFO 3 = 34, so non-PASS is **19** counting
INFO or **16** counting WARN+FAIL. Eighteen is neither. The classification arithmetic in
the same paragraph requires 16 (15 firing + the rank guard); 18 is the size of PASS+INFO.
A transposition, and it is the only sentence in §2.1 that does not reconcile.

**F7 — §1.3: "the largest family there is 20 copies of `hump_gate_analysis.py`, one per
sweep arm."**
`git ls-files | grep -c hump_gate_analysis.py` = **23**, at both `c8d5eec4` and `HEAD`, all
23 in axis B and in the 296-file union: 4 under `channel1_rans_sweep/`, 3 under
`channel3_eigenvalue_perturbation/`, 15 under `r4_band_tightening_hump/`, 1 under
`f6a_nasa_hump/case/`. Off by three on a one-command check.

**F8 — §5.4: "two 906 MB tarballs left unopened."**
There are exactly two unopened tarballs at `/home/ubuntu`, and **neither is 906 MB**:

```
544,309,252 B = 544.3 MB   certonomous-git-backup-20260730T033814Z.tar.gz
362,066,284 B = 362.1 MB   certonomous-cache.tar.gz
                 906.4 MB   ← the SUM
```

`find /home/ubuntu -name "*.tar*" -size +500M` returns **one** file across the whole
filesystem, so no 906 MB tarball exists anywhere, let alone two. **906 MB is the pair's
total, written as though it were each one's size** — a `du`-style aggregate reported over
the wrong frame, which is the single most repeated defect in this ledger (see O2, O3, F9).
The substance moves with it: the unexamined residual is **906 MB in total, not 1.8 GB**.
*This is the one §5.4 figure that turned out to be decidable, and it decided against the
ledger.*

**F9 — §1.3: "The remainder are one-shot campaign-local gates under
`demo-output/website/campaign/**` and `demo-output/website/dafoam/**` (24 candidates)."**
Internally impossible. The **142** are defined by the ledger itself as *"production
(non-test, non-`demo-output`)"* — their remainder cannot live under `demo-output`. The
union does contain **98** `demo-output` files, 23 of which are the `hump_gate_analysis`
family. Whatever 24 counts, it is not the remainder of 142 and it cannot contain a
23-member family plus anything else.

---

### 2.2 TRUE-BUT-HEADLINE-OVERSTATES — *the category that caused the damage*

**O1 — §1.1: "`mesh_certificate.py` … is not found by any verdict-word search of its
source."**
The underlying finding is real: `mesh_certificate.py` is in axis B only, not A, C or D.
**But the sentence as written is false.** `grep -E "VERDICT|CLEAN|PASS|FAIL"
sdk/chief_engineer/mesh_certificate.py` returns **7 lines**, including
`ACCEPTED_VERDICTS = ("clean", "flagged")` and `VERDICT_UNVERIFIED = "unverified"`. What
misses it is *axis A specifically*, whose rule requires the verdict word to sit on a
`print`/`echo`/`write` line — and `mesh_certificate.py` has **zero** such lines. This is
the closest thing in the document to a second L-68: a true finding about a stated rule,
titled as a claim about *any* search.

> **Standalone-true replacement:** *"`mesh_certificate.py` — the instrument whose
> false-clean is item 3 in the director's own list — carries the word `VERDICT` seven times
> and never on a line that emits one, so **axis A cannot see it**; only its filename
> reveals it."*
> What makes this standalone-true: it names the axis instead of quantifying over all
> searches, and it states the fact (7 occurrences, 0 on emitting lines) that makes the
> distinction load-bearing.

**O2 — §1 table, "files *only* this axis found" column: 6 / 8 / 59 / 2.**
These are correct — **over the 142 production files**. Over the 296-file union in the same
table's own `union` row they are **13 / 96 / 92 / 4**. The `hits` column beside them
(89/137/165/24) is over all 534. **Two frames sit in adjacent columns of one table with
neither declared.** I confirmed the restriction exactly: restricting to `u_prod` reproduces
6/8/59/2 on all four axes; restricting to non-`demo-output` gives 6/56/59/2, and no
restriction gives 13/96/92/4.

> **Standalone-true replacement:** add a column header — *"files only this axis found
> **among the 142 production files**"* — and a footnote: *"the hits column is over all 534
> tracked files; over that frame the unique counts are 13 / 96 / 92 / 4."*

**O3 — §1.1: "Axis C alone contributed 59 unique files".**
Same defect, promoted to a bolded bullet. 59 is the production frame; **92** is the union
frame the sentence sits in. The neighbouring bullet ("Axis A missed 12 of axis D's 24") is
over the *union* frame and is correct there — so the two bullets in one list are counted
over different denominators.

> **Standalone-true replacement:** *"Axis C alone contributed 92 unique files across the
> union — 59 of them production — but it is the least specific: a non-zero exit is also how
> ordinary scripts report I/O errors."*

**O4 — §0 / §2: "reach demonstrated **30** · reach assumed **25** · known-blind **11**".**
The arithmetic is exact and internally consistent (17+13 / 16+9 / 1+10 = 66 = 34+32; shares
45/38/17% all correct to the rounding). **Two rows do not meet the ledger's own definition
of *demonstrated*** — *"shown to FIRE on a true positive: a planted bad input, a
known-answer suite, or an observed firing on a real defect"*:

- `scripts/contention_audit.py` — basis given is *"the model citizen: its own output says
  'A window that reads clean here is not PROVEN clean'"*. I verified that line verbatim at
  `contention_audit.py:190`. **It is a reach statement, not a firing.** No test file, no
  observed fire.
- `scripts/mint_retrospective_certificates.py` — basis given is *"every refusal is a named
  class; **no test file**"*. A taxonomy of refusals is not a demonstration that one fires.

**Reclassifying both moves the numbers to demonstrated 28 / assumed 27 / known-blind 11 —
which makes the ledger's own headline finding stronger: "more than one in three has never
been shown to fire" becomes 41%, not 38%.** The direction matters: this is not a
correction that rescues the instruments.

Separately, one *known-blind* row — `audit_transcripts.sh` — survives its class on a
**different** basis than the one printed. The stated basis ("clean over a non-existent
root") is F2, falsified. The real blindness (a gate that could not distinguish *scanned 17
and found nothing* from *scanned nothing*) is genuine, and fixing it surfaced 8 real hits.
**The count of 11 holds; one of its eleven cells needs its evidence replaced.**

**O5 — §0 / §3.2: "14 of 34 self-audit checks carry a numeric denominator".**
Over `4dec8fec` I count the summary lines carrying an explicit `N of M` or `all N` and get
**11**, or 12 if the percentage in `ledger stall contamination` counts. The gap is inside
the judgment margin of the category, and the tree moved — but the number is not
reproducible as stated. **A related definitional defect is checkable and holds:** category
C is defined as *"bare fault count, no denominator at all"*, yet **three of the four
examples printed under it carry no count at all** (`PASS the wall quotes the current entry
of record`, `PASS F2 Cd and Cl match the raw force file`, `PASS published memory law
reproduces from its own data`). The category is really *"no denominator"*, and its name
says *"fault count"*.

> **Standalone-true replacement for the category:** *"C — no denominator: a bare fault
> count, or a bare assertion with no count at all."*

**O6 — §4.5 R5: "`is_idle.sh` powers the box off from an absence. Cost of a false green: a
mid-campaign power-off. **Already realized, 2026-07-30 10:40.**"**
**The code defect is real and current**, verified line by line at `HEAD`: `found` is built
from `pgrep -x` over a hand-written executable list; `pgrep`'s exit status is never read;
an empty `found` prints `IDLE` and exits 0; and `checkMesh`, `potentialFoam`,
`surfaceFeatureExtract`, `setFields`, `sample`, `topoSet` are all absent from the list —
six work classes, exactly as claimed.

**The causal attribution is not established.** The claim is inherited from the prior pass,
whose table cites `OTHER_WORK_STATUS.md:50` as its evidence. I read that line: it records
`is_idle.sh`'s **purpose** (*"detect real work for auto-stop watchdog"*) and status
(*"Live"*). **It records no power-off and no date.** And no caller exists: a repo-wide
search for `is_idle` finds only `exec_bits.py`'s manifest, a permission entry in
`.claude/settings.local.json`, and the script's own self-exclusion. **I could find no
wiring from `is_idle.sh` to anything that halts the machine.** The lab's own standing note
attributes the 2026-07-30 10:40 power-off to an auto-stop that *"ignores the control
room"* — filming looking like an idle box — which is a different mechanism.

> **Standalone-true replacement:** *"R5 — `is_idle.sh` concludes IDLE from an absence, over
> a hand-written work list missing six utility classes and with `pgrep`'s exit status never
> read. **It is written for an auto-stop watchdog and is not currently wired to one**; the
> 2026-07-30 10:40 power-off is attributed to it by FP-9 on a citation
> (`OTHER_WORK_STATUS.md:50`) that does not record it."*
> What makes this standalone-true: it separates the verified code defect from the
> unverified causal history, and it says so in the title rather than in a footnote.

**O7 — §4.4 R4: "the rank-claim guard is anchored to a spelling, **and the fix is
uncommitted**".**
True at `c8d5eec4` — I confirmed `_RANK_CLAIM = re.compile(` at exactly the cited
`self_audit.py:407`. **The fix landed 19 minutes later at `862d2cff`.** At `4dec8fec` the
guard prints its own frame line (*"20552 tracked path(s) … 37 of those assert a rank-1
placement. Blind to: …"*) and `check_board_placement_words` exists beside it. A headline
whose truth expires in 19 minutes is not standalone-true once the document is published
from.

> **Standalone-true replacement:** *"R4 — the rank-claim guard was anchored to a spelling;
> the word-form replacement was uncommitted **as of `c8d5eec4`, 2026-08-11 03:10 UTC** and
> landed at `862d2cff`."* Any headline asserting the state of a working tree must carry the
> commit and clock it was true at.

**O8 — §3.1 / §4.3 line citation `scripts/self_audit.py:3713`.**
The finding is fully sound (see S5) but **the cited line resolves to nothing in any
committed state**: `c8d5eec4:3713` is blank and at `4dec8fec` the print sits at **3744**.
It is a line number in an uncommitted working tree that no longer exists.

> **Standalone-true replacement:** cite the condition, not the line — *"the `if declared and
> (declared[0] in (GENERATOR, TRANSCRIBED) or declared[3])` gate around the `BLIND TO:`
> print"* — which I resolved unambiguously at both commits.

**O9 — §4.7 R7 / §3.3: "`log_signatures`' **six** detectors return a bare `None`".**
The claim's substance is exactly right and I verified it: `grade_bounding_episode` is the
only function in the module carrying `{"graded": ...}` (2 occurrences, lines 1071/1081),
and every other detector's signature is `-> dict[str, Any] | None`. **But there are eight
`detect_*` functions, not six** (`residual_stall`, `courant_excursion`, `ceiling_clip`,
`normalisation_collapse`, `residual_norm_contradiction`, `system_operations`,
`unsettled_stop`, `magnitude_explosion`), and §2.2's own S-numbering (S6, S8–S12, S10d)
enumerates seven. I could not reconcile six with either.

---

### 2.3 SOUND — these survive, and I want them on the record

**S1 — §4.1 R1: "`case_preflight.sh` returns PASS on an empty directory, silently, at the
one call site that matters."** **Reproduced exactly**, running the pinned ledger-era
source:

```
$ bash <(git show c8d5eec4:scripts/case_preflight.sh) <empty dir>
  ok:   no processor dirs (will decompose fresh)   /  (model undetermined; skipping field check)
  ok:   solver field headers parsed                /  (no polyMesh/boundary yet … skipping patch check)
  PREFLIGHT PASS -- clear to launch                                          exit=0
$ … --quiet                                        (no output whatsoever)    exit=0
```

Every supporting fact checks out: `launch_solve.sh` does invoke it as `"$PF" "$CASE"
--quiet` (both the `exec` and the `bash` arms); the `.done` corpus is **146** records; and
the F11 citation is real at `F11_lid_driven_cavity_ladder.md:174–175` — *the phrase wraps
across a line break, so a line-bounded `grep` for it returns zero, which is L-61's own trap
and is why I read the lines rather than trusting the grep.* Note the precision of the
headline's adverb: I confirmed with a genuinely failing case that **failures are audible
under `--quiet` and only the PASS is silent**, which is what the headline says and is the
worse of the two defects. Fixed in the working tree at 03:26 and committed by 03:38 —
**7 of 136 evaluable launches now blocked.**

**S2 — §0/§1: base denominator 534.** `git ls-files '*.py' '*.sh' | wc -l` = 534 at
`c8d5eec4` and at `4dec8fec`; 0 untracked `.py`/`.sh` in the tree.

**S3 — the four axes are internally exact.** From the author's own retained axis files:
`|A|=89, |B|=137, |C|=165, |D|=24`, `A∪B∪C∪D` is **exactly** the 296-file union with no
stragglers, `u_prod` (142) is a strict subset of the union with **zero** `demo-output`
members and one `test`-containing basename
(`sdk/scripts/closure_criterion_on_test_features.py`, which is not a test). *Caveat I owe:
my independent implementation of the four rules **as printed** gives 44/134/143/37 and a
union of 268 — the prose rules are not precise enough to reproduce the published counts
(case-sensitivity, word boundaries and what counts as an emitting line are all
underdetermined). This is a reproducibility gap, not a discrepancy: the author's sets are
self-consistent and every member I spot-checked satisfies its rule.*

**S4 — §1.1: "Axis A missed 12 of axis D's 24."** `|D − A| = 12` exactly. And all ten files
named as found only by their names verify: every one is in B, none in A, none in D.

**S5 — §4.3 R3 / §3.1: "30 of 34 self-audit blind spots are written down and never
printed."** The strongest verified finding in the document. Importing `self_audit` at
`4dec8fec`: `BASIS` has **34** entries; **zero** have an empty blind-spot string; the kind
census is **EVIDENCE 13, PROPERTY 13, SURFACE 4, GENERATOR 2, META 2** — matching the
ledger digit for digit; and evaluating the print condition yields **4** checks that would
print `BLIND TO:` (`check_gate_table_vs_transcripts`,
`check_wall_credentials_vs_results`, `check_stored_fits_reproduce_their_values`,
`check_order_window_declines_state_their_dimensionality`). The live run confirms it:
**4 `BLIND TO:` lines across 34 verdicts.** 30 suppressed, as claimed.

**S6 — §2.2, the test-count column: 9 of 9 exact.** `log_signatures` 72 · `exec_bits` 15 ·
`mesh_certificate` 33 · `lever_echo` 54 · `uncertainty_band` 14 · `uq` 59 ·
`tmr_verification` 76 · `validate_motorbike_pressure` 37 · `morning_report` 17 — every
figure matches `grep -c 'def test_'` on the named file. **This column was not estimated.**

**S7 — §2.2: `check_convergence.py` "re-run in this pass, all 13 pass".** Re-run again here:
`All 13 known-answer cases passed`, including the `NOT_CONVERGED` and `CANNOT_TELL` arms.

**S8 — §1.2: "no `.github/workflows`, no non-sample hooks".** `.github` does not exist;
`.git/hooks` contains only `.sample` files.

**S9 — §3.3, the line-citation table: 6 of 8 resolve verbatim at `c8d5eec4`.**
`launch_solve.sh:199`, `contention_audit.py:190`, `closure_divergence_audit.py:132`,
`validate_closure_mesh_recon.py:116`, `audit_camera_discretion.sh:162`,
`audit_transcripts.sh:63`, `case_preflight.sh:249` all print exactly the quoted line.
`is_idle.sh:73` is off by one (`fi`; the `echo "IDLE"` is line 74). `self_audit.py:3713` is
O8.

**S10 — the inherited FP column, spot-checked and still current at `HEAD`.** FP-6:
`geometry_study.mesh_gates_pass` contains no reference to `returncode` at all and coerces
`None` to 0, so a missing reading passes. FP-16: `closure_divergence_audit.py:272` really
does read `.get("regenerated_vs_shipped_round4_csv_max_abs_diff", 0.0) < 5e-7`, so a
missing key reads as agreement. FP-19: `lab.trust` takes `grid_conclusive: bool | None`
against a bare `converged: bool`. **These were inherited but they have not gone stale.**

**S11 — §5, the hump table, on every point I could reach.** A9's log verified line by line
(above). A10: no `hump_rich`, `globalPCIters` or "Richardson-wrapped" entry exists anywhere
under `demo-output/website/agenda/` — the proposal really was never filed — while
`certonomous-runs/W4-adjoint-pc-unblock/runScript_hump_rich.py` exists. A11:
`run_hump_fd.sh` exists in the same directory and **zero** hump FD logs exist anywhere
under any `fdlogs/`. The abandonment counts reconcile against the table: 4 abandoned with
no root cause (A4, A5, A6, A9), 2 built and never executed (A10, A11), 0 reproduced as
negative controls.

**S12 — §5.3 defect 1, sound when written and now remedied.** At `c8d5eec4` the offending
sentence is present at the cited line — *"the NASA-hump beta-field gradient … has not been
re-run under a second decomposition"*. It was corrected at `98a39662` (03:29:15, 19 minutes
after the ledger), which now reads *"no hump beta gradient has ever been produced, so the
gate has no object on this case (corrected 2026-08-11)"*. **Rung V9 is already discharged.**

**S13 — §5.3 defect 2.** `44.54` appears in `certonomous-runs/adjwall/**` only inside
`.xyz` mesh files, in no archived hump **log**. The claim holds as worded.

**S14 — §6 and §7.** The rungs name owners and prerequisites and author no fixes, exactly
as the ledger promises, and §7's five "could not establish" items are all genuinely
open. Two rungs have since been discharged by other agents (V2 at `13bea68f`, V9 at
`98a39662`), one is committed (V3, by 03:38), and **V1 — the highest-leverage rung in the
document — is still open: 4 of 34 at `4dec8fec`.**

---

## 3. Re-derivation of the counts, with the frame stated

**Frame: `git ls-files '*.py' '*.sh'` over commit `c8d5eec4` (the ledger's own commit),
cross-checked at `4dec8fec`. Identical at both.**

| ledger figure | frame it is actually over | my re-derivation | verdict |
|---|---|---|---|
| 534 tracked `.py`/`.sh` | all tracked files, both commits | **534** | **holds** |
| union 296 | all 534 | **296** — `A∪B∪C∪D` exactly, no stragglers | **holds** (author's sets; rules as printed give 268) |
| 142 production | union minus `demo-output` minus tests | **142**, strict subset, 0 `demo-output` | **holds** |
| 66 profiled | 34 + 32 | **66** | **holds** |
| per-axis unique 6/8/59/2 | **the 142, not the 296** | 13/96/92/4 over the union | **frame unstated → O2/O3** |
| 30 / 25 / 11 | the 66 | arithmetic exact; **2 rows misclassified** | **28 / 27 / 11 → O4** |
| 14 of 34 numeric denominators | the 34 checks | **11** at `4dec8fec` | **not reproducible → O5** |
| 30 of 34 blind spots suppressed | the 34 checks | **34 declared, 4 printed** | **holds exactly** |
| PASS 15 / WARN 8 / FAIL 8 / INFO 3 | a working tree that no longer exists | **13 / 9 / 9 / 3** at `4dec8fec` | **unverifiable by construction; honestly labelled** |
| 11 attempts + 3 staging faults | the hump table | reconciles as A1–A11 + A0's three | **holds** (see note) |
| 20 copies of `hump_gate_analysis.py` | tracked files | **23** | **falsified → F7** |
| 24 candidates | undefined | union has 98 `demo-output` members | **falsified → F8** |

*Note on the hump count:* "11 distinct attempts + 3 staging faults" counts A7 and A8 as
attempts, while §5.1 calls them *"trivially-diagnosed staging faults"*. The total is right
under either reading; the two readings disagree about which rows are which.

---

## 4. Things I was not looking for

1. **The tree moved five times during a 20-minute audit** — including `case_preflight.sh`
   acquiring a 190-line fix at 03:26, mid-verification, and `HEAD` advancing twice. L-72
   landed on exactly this hazard while I was writing. **Any number taken over a working
   tree in this lab needs a commit sha beside it, not a date.** The ledger's §2.1 caveat
   was the right instinct and still was not enough: it named the change but not the sha,
   so its tally can never be re-derived.
2. **The ledger's line citations are its most fragile surface.** Seven of eight resolve
   perfectly at its own commit, but the one that does not (`self_audit.py:3713`) points
   into an uncommitted tree — and that is the citation for the ledger's **highest-leverage
   finding**. A finding that good deserves a citation that outlives a working tree.
3. **`docs/PRODUCT_LIST.md:2884` carries the R5 headline in its most compressed form** —
   *"`is_idle.sh` — powers the box off from an absence; 6 work classes missing; cost already
   realised 2026-07-30"* — which is the O6 attribution travelling one document further, the
   same propagation path L-68 describes. Not touched by this pass; flagged for its owner.
4. **`scratchpad/psshim/ps`** is a planted fake `ps` returning an em-dash-bearing cmdline.
   It produced no ledger claim, but it is a live control-shaped artifact sitting one
   `PATH` entry away from any process-probing instrument. It is unlabelled and undisposed —
   exactly what L-68 says a control must never be.
5. **The `hump_gate_analysis.py` family is a 23-way duplicate of one gate.** The ledger
   notes it as a counting curiosity; it is also 23 independent copies of one instrument
   that can drift apart, and nothing in the estate checks them against each other.
6. **This audit's own instrument has an undeclared reach, and I only found it by reading a
   process list.** `grep` in this environment resolves to
   `ugrep -G --ignore-files --hidden -I --exclude-dir=.git …`. **`--ignore-files` honours
   ignore files**, so every `grep -r` count in this document — and every `grep -r` count in
   the ledger, and in the prior pass — is over *the files ignore rules permit*, not over
   the filesystem. None of the three documents says so. It changes no verdict here, because
   every count I ruled on was taken over `git ls-files` (which has the same reach by
   construction) or over `find` (which has none); but it is exactly the ledger's own
   finding — **a verdict that does not state what it swept** — recurring in the tool the
   auditors used to check the instruments. *A fourth document could inherit these numbers
   without ever learning the filter exists.*

## 5. Things I could not establish

- **FP-7's "8 of 9 archived reports print `Geometry | n/a, no issues found`".** I could not
  locate the nine archived reports — `chief-engineer-runs/` holds two directories and the
  literal string appears nowhere in the tree. The claim is inherited from the prior pass
  and `head_engineer.py` was being edited by another agent throughout. **Unverified,
  neither confirmed nor refuted.**
- **§5.4's `transonicPCOption` population of 651.** `du -sh` gives **66 GB** for
  `certonomous-runs` (matches) and **19 GB** for `Certonomous` against the stated 17 GB —
  plausibly an hour's growth, not a defect. But no restriction I tried reproduces 651:
  **810** files carry the marker across both trees, **507** under `certonomous-runs`, and
  **387** of those are log-named. 651 sits between two of my numbers and equals none of
  them, and the ledger does not state which restriction produced it. **And my own
  instrument has an unstated reach here** (see §4.6): `grep` in this environment is
  `ugrep --ignore-files`, which honours ignore files, so my counts are not a raw
  filesystem census and are **not the same measurement** the ledger made. **I can neither
  confirm 651 nor call it wrong**, and I am not going to convert an incommensurable
  number into a verdict. *(F8 was carved out of this bullet once it became decidable on
  `find`, which carries no such filter.)*
- **Whether the ledger's `PASS 15 / WARN 8 / FAIL 8 / INFO 3` was correct.** The tree it was
  taken over was never committed and no longer exists. This is unfalsifiable by
  construction, which is itself the finding — and it is why F5 and F6 could only be caught
  by internal arithmetic rather than by re-running anything.
- **The precise membership of the four axes.** The rules as printed do not reproduce the
  published counts (S3). I can confirm the sets are self-consistent and that spot-checked
  members satisfy their rules; I cannot confirm the sets are what the printed rules select.

---

## 6. What this audit does not claim

The ledger's **enumeration method — four axes chosen so no two share a failure mode, unioned,
with the per-axis shortfalls published — is good work and it held up.** Every one of its
disagreement findings that I could check was true. Its `case_preflight.sh` finding was real,
load-bearing, and has already produced a fix that refuses 7 of 136 evaluable launches. Its
`BLIND TO:` finding is exact to the digit and is still unfixed. Its test-count column is
exact on 9 of 9 rows.

**The defect is not in what this ledger found. It is that its titles and its round numbers
were not held to the standard its bodies were.** Nine falsifications, and eight of them are
a count or a frame that a single command would have settled — over a document whose own
subject is instruments that report clean without stating what they counted.

*Compiled read-only. No instrument, script, test or record was modified; the ledger file was
not touched. Nothing was sent, filed or uploaded.*
