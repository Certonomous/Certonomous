# H4 Allocation Audit

Executor: [SONNET], by listing rather than memory, per `docs/HANDSHAKE.md` H4.
Grader independence: this report's author did not write `SUPERVISION_CHARTER.md`,
`docs/HANDSHAKE.md`, any commit graded below, or the solve registry. All checks
below are commands executed against the live repo/OS at the timestamps shown,
not summaries of anyone else's account.

Audit executed starting 2026-08-12T16:25:08Z (`date -u` output, first command run).
All "right now" / "currently" claims in this report are anchored to that window
(2026-08-12T16:25Z–16:27Z) per rule W-5; none are bare present-tense.

---

## H4a — ONE AGENT = ONE WORKTREE/SCRATCH; ZERO SHARED PATHS — **FAIL (currently true)**

**Command:** `git worktree list`
**Output:**
```
/home/ubuntu/Certonomous  d1585e3b [main]
```
Exactly one worktree exists. So the violation is not "two worktrees" — it is
two agent sessions sharing the single worktree that exists.

**Command:** `ls -la /tmp/claude-1000/-home-ubuntu-Certonomous/`
**Output:** three scratch dirs: `2d7fba0a-0fff-4eea-a950-4738af616bdb`,
`64b13819-ff95-4d4d-a50f-3720bab19084` (this grader's own, per its system-prompt
scratchpad path), `f3ba2ffe-c31e-4e39-b8dd-69ab43822925`. Three distinct scratch
namespaces exist on disk right now — consistent with at least three sessions
having run recently, though scratch-dir existence alone does not prove
concurrent liveness (a dir can persist after its session ends).

**Live-process check (the part that establishes "right now"):**
`ps -ef --forest` at 16:27:03Z shows two top-level `claude --resume` OS
processes, both with `cwd` = `/home/ubuntu/Certonomous` (confirmed via
`readlink /proc/<pid>/cwd`), both children of the same login shell (PID 1584),
started 30 seconds apart:

```
PID 1630  started 15:42:01  cmdline: "claude --resume 64b13819-ff95-4d4d-a50f-3720bab19084"
PID 1834  started 15:42:31  cmdline: "claude --resume"   (CLAUDE_CONFIG_DIR=/home/ubuntu/.claude-sanaa)
```

At 16:27:03Z, `ps --ppid 1630` returned **zero rows** (no live children —
dormant at that instant, but the process itself is alive and cwd-attached to
the shared worktree). `ps --ppid 1834` returned live children **not issued by
this grader's own tool calls**, running concurrently in `/home/ubuntu/Certonomous`:

```
PID 6845→6900  started 16:23:10/11  python -m pytest sdk/tests/test_rank_claim_surfaces.py  (still R state at 16:26, ~99% CPU, 3-5 min elapsed)
PID 8892→9105  started 16:26:03     git log -p --all + grep for AKIA/API_KEY/SECRET_KEY patterns (a secrets sweep), ugrep child at 9108
```

This grader's own commands appear in the same tree as children of PID 1834
(e.g. the ps-tree check itself is PID 9220→9242/9243/9245). That means: **at
least one other agent process — running the pytest suite and an independent
secrets sweep — was executing inside the same main worktree, under the same
parent PID, at the same wall-clock minute as this grader's own audit
commands**, and a second, separate top-level session (PID 1630) was
simultaneously alive and attached to that same worktree.

This is the "two chief sessions duplicate dispatch" hazard from standing
memory, instantiated on disk at 2026-08-12T16:2x UTC, not a historical
account. **Verdict: FAIL, currently true** — one worktree, at least two live
top-level agent sessions attached to it concurrently, one of them running
commands this grader did not issue.

**The pre-declared known violation (2026-08-11 deaths → 2026-08-12 collision),
verified from `git log`/`git reflog`, not taken on trust:**

```
git log --format='%H %ad %s'  (--date=iso-strict)
025d59a6  2026-08-12T15:55:16+00:00  "The gate that decides whether this box lives judged work by how a path was spelled"
0c7b968d  2026-08-12T16:13:12+00:00  "D49 settled and D48's disclosure landed..."
5c9c63fb  2026-08-12T16:13:59+00:00  "P(rank 1) recomputed against the live six-entry board..."
```
`git reflog` reproduces the identical SHAs and timestamps (cross-checked, not
re-derived from a different source — same instrument, so this is corroboration
not independent confirmation; see the tracked-file diff below for the
independent leg). `025d59a6` (a third agent's auto-stop-script fix, confirmed
by `git show --stat 025d59a6`, which touches `/usr/local/bin/auto-stop.sh`,
not either recovery agent's files) landed at 15:55:16, **17 minutes before**
the two recovery commits at 16:13:12 and 16:13:59 that are documented (in
`docs/HANDSHAKE.md` H1, which I am verifying rather than citing as fact) as
the recovery of two agents' work left uncommitted since 2026-08-11. The
sequence is consistent with the claim: a third agent committed into the
shared worktree while at least one of the two recovering agents' work was
still uncommitted. **Verdict on the historical instance: CONFIRMED** by
independent timestamp read.

**Is the tracked-file collision still open right now?**
`git status --porcelain=v1` → `M sdk/.filming-keepalive` only. No other
tracked-file collision is open at 16:25Z. So the *specific* 2026-08-11 dirty
files were recovered/committed by 16:13:59Z and are no longer dirty. But the
*structural condition that produced it* — one worktree, multiple live agent
sessions attached to it with no isolation — is independently confirmed still
true right now by the process evidence above, unrelated to whether any file
happens to be dirty at this instant.

**Stash/reflog residue (context, not itself a live violation):** `git stash
list` shows 4 entries, two of them `WIP on main` from earlier in this repo's
history (`5396382`, `8e70529`), not from today. `git fsck --unreachable
--no-reflog` returns ~50 dangling blobs/trees/commits — normal git churn, not
examined further; not claimed as evidence of anything beyond "this repo has
had rewrites."

---

## H4b — SUPERVISION TREE MATCHES THE CHARTER

**Charter clauses tested (quoted from `docs/charters/SUPERVISION_CHARTER.md`,
read in full):**

> §1: "Every big task family has a standing supervisor, and four kinds of
> check are done by a supervisor personally or they have not been done."

> §2: four families — DAFoam/adjoint, Closure/UQ, Cases/campaigns,
> Infrastructure/standards — each "gets a standing family supervisor agent,"
> whose first duty is "Issues family guidelines... in the family's own
> records."

> §4: "The chief supervises the supervisors," retaining scoring-call
> authorization, cross-family arbitration, negative-verdict reviews, list/board
> custody, and "everything the 2026-07-26 delegation doctrine already
> assigns." The charter does not contain a sentence of the form "the
> orchestrator holds only orchestration" — that phrasing is this audit brief's,
> not the charter's; the closest textual anchor is §4's retained-list plus the
> delegation doctrine's "everything else goes to designated agents even when
> she does not say so."

**Guideline-issuance duty — checked by listing, PASS on existence:**
```
find . -iname "*FAMILY_SUPERVISION*" -not -path "./.git/*"
./demo-output/website/CLOSURE_FAMILY_SUPERVISION_REVIEW_2026-08-07.md
./demo-output/website/CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md
./docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md
./demo-output/website/dafoam/FAMILY_SUPERVISION_GUIDELINES.md
./demo-output/website/campaign/CASES_FAMILY_SUPERVISION_GUIDELINES.md
```
All four families have a guidelines document on disk. **Verdict: PASS** on
"a guidelines artifact exists per family." I did not audit content/currency
of these four files — that is a different question than allocation and is
out of this audit's scope.

**"Every live agent has a family owner" — UNKNOWN.** No roster file exists:
```
find . -iname "*roster*" -o -iname "*fleet*status*"  →  no output
```
The only live-agent evidence available to this grader is the OS process list
(§H4a above: PIDs 1630, 1834, and 1834's children). None of these carry any
attribute — env var, cmdline flag, cgroup name — that maps a PID to a named
family-supervisor role. I cannot establish "every live agent has a family
owner" by listing; I can only say no on-disk roster contradicts or confirms
it. Per this audit's discipline, an unmeasurable fact is reported as
**UNKNOWN**, not converted to a PASS by default.

**Orchestrator-scope violation — CONFIRMED, self-declared, and independently
timestamp-corroborated, not merely repeated.** `docs/HANDSHAKE.md` (§H4,
lines 82-88) pre-declares that [ORCH] executed work directly before today's
order arrived: the auto-stop repair and H5's reconciliation. This grader
independently confirms the auto-stop repair commit exists and matches the
claimed content and timing:
```
git show --stat 025d59a6   →  commit 025d59a6, 2026-08-12T15:55:16Z,
  "The gate that decides whether this box lives judged work by how a path was spelled"
  — modifies auto-stop.sh, described in its own body as fixing the idle-detector
    that powered the box off at 02:45 and 15:35 on 2026-08-12.
```
Git provides no field distinguishing "the chief/orchestrator" from any other
committing identity (all commits show author/committer `Ubuntu
<ubuntu@ip-172-31-43-247...>` — see H4e), so I cannot independently verify
*that this specific commit was authored by the orchestrator role* versus
some other agent — I am corroborating the artifact's existence and timing,
not the role-attribution, which rests on `HANDSHAKE.md`'s own admission.
**Verdict: CONFIRMED as a documented, self-reported instance; not
independently attributable to "ORCH" by git evidence alone — flagged as
such rather than silently accepted.** No second instance of ORCH-shaped
direct execution was found after the order's stated arrival time; absence
of evidence here is not strong (git gives no role field to search on), so
this is **UNKNOWN beyond the one declared instance**, not a clean "zero
further violations."

---

## H4c — COLLECTORS ARMED; NO-ORPHAN CHECK

**Commands and output (`demo-output/website/solve_registry`, gitignored,
listed with `find`/`ls`, not `grep -r`, per the known ugrep/.gitignore trap):**
```
find .../solve_registry -type f | wc -l                        → 300
find .../solve_registry -type f -name "*.done" | wc -l         → 142
find .../solve_registry -type f -name "*.done.INTERRUPTED" | wc -l → 4
find .../solve_registry -type f -name "*.partial" | wc -l      → 0
find .../solve_registry -type f -empty | wc -l                 → 9
find .../solve_registry -type f -empty -name "*.done" | wc -l  → 0
find .../solve_registry -type f -empty -name "*.log" | wc -l   → 5
```
The 9 zero-byte files break down as 5 empty `.log` files
(`a1_realseed_idx01_...`, `f8_genmesh_...`, `a5_corrected_composite_...`,
`a5_chainlinks_...`, `a5_tight_adjoint_...`) plus the 4
`.done.INTERRUPTED` records themselves (zero-byte by construction — they are
renamed-not-deleted empty `.done` files per the E2 repair `HANDSHAKE.md`
describes). **Zero `.done` files are zero-byte** — confirmed directly, not
inferred. **Verdict: PASS** on ".done records are not zero-byte" and on
"4 `.done.INTERRUPTED` records exist."

**Positive control for the `.partial` zero:** the same `find` invocation
against the same directory, changing only the suffix, correctly returns 4
for `.done.INTERRUPTED`, 142 for `.done`, and dozens for `.log` — proving the
instrument is not silently returning zero for everything. A second, wider
control (`find /home/ubuntu/Certonomous -iname "*.partial*"` across the whole
repo, excluding `.git`) also returns nothing. **The `.partial` zero is a
validated zero, not an unmeasured one.**

**Live discrepancy found and independently re-derived (not merely cited from
D50):**
```
grep -n "146" docs/PRODUCT_LIST.md
1493, 1521: "Of 146 completion records, 3 carry a rank declaration..."
2920: "146 `.done` records rest on it."
3113, 3135: "over 146" / "all 146 records intact"

python3 -c "import glob; print(len(glob.glob('demo-output/website/solve_registry/*.done')))"
→ 142

grep -n '\.done' scripts/dispatch_queue.py
scripts/dispatch_queue.py:114:  records = sorted(REGISTRY.glob("*.done")) if REGISTRY.is_dir() else []
```
`PRODUCT_LIST.md` cites 146 in five places; both `find` and an independent
`glob.glob` re-derivation, run separately, agree on **142** right now. This
confirms the D50 mismatch is **currently live**, at this audit's timestamp
(2026-08-12T16:2xZ), not only a historical claim — I re-executed the count
myself rather than trusting the docket entry.

**Orphan-process check:**
```
ps aux | grep -iE 'simpleFoam|pimpleFoam|rhoSimpleFoam|adjoint|snappyHexMesh|mpirun|dafoam|openfoam|blockMesh|potentialFoam'
→ no matches (grep exit code 1)
```
**Positive control:** the identical `ps aux | grep` methodology, run for
`pytest` in the same command batch, correctly found the live PID 6900
process — proving the method detects real running processes and is not
silently blind. **Verdict: PASS, validated zero** — no orphaned
solver/mesher process at 2026-08-12T16:2xZ.

Newest registry record by mtime: `f6b3_relax{B,C,PC}_20260811T011859Z.log`,
epoch ~1786411881–1786411393, i.e. 2026-08-11 ~01:2xZ. Nothing newer exists
in the registry. Consistent with (but not, by itself, proof of) "no solve
captured since the outage."

---

## H4d — METER / CONFIG

**`CLAUDE_CONFIG_DIR`:**
```
echo "value: [$CLAUDE_CONFIG_DIR]"   → /home/ubuntu/.claude-sanaa
```
Confirmed independently via `/proc/1834/environ`
(`CLAUDE_CONFIG_DIR=/home/ubuntu/.claude-sanaa`, this grader's own process
lineage). **`/proc/1630/environ`, filtered for `session|claude`, shows no
`CLAUDE_CONFIG_DIR` line at all** — the two concurrently-live top-level
sessions identified in H4a do not have confirmably matching config-dir
environments from what's visible in their filtered environ. This is a soft
finding (the variable could be set and simply not match the grep filter, or
inherited differently), not a hard proof of divergent config — flagged as
**UNKNOWN**, not asserted as a mismatch.

**tmux:**
```
tmux ls  → error connecting to /tmp/tmux-1000/default (No such file or directory)
```
No tmux server exists right now. This is a meaningful, specific error (not a
hang or empty success), so the check is trustworthy: it ran against a real
socket path and got a definite "absent" answer. It is also consistent with
`025d59a6`'s own commit body, independently read via `git show`, which states
the idle-shutdown bug "kill[ed] the tmux server" at 15:35 on 2026-08-12 — the
tmux server has evidently not been restarted since that event, as of 16:2xZ.

**Weekly API limit termination evidence:**
`docs/HANDSHAKE.md:21` states the weekly limit "terminated a three-agent
fleet at ~2026-08-12 00:00 UTC (reset stated as Aug 14 06:00 UTC)."
```
find . -iname "*auto-stop*" -o -iname "*auto_stop*"
→ scripts/auto-stop.sh, scripts/auto-stop.sh.proposed  (the mechanism, no incident log)
grep -rn "weekly limit\|00:00 UTC\|terminated a three-agent" docs/HANDSHAKE.md docs/DOCKET.md
→ only the HANDSHAKE.md:21 line itself
```
I found no independent on-disk artifact (timestamped log, marker file, kill
record) corroborating the specific "weekly API limit at ~00:00 UTC" claim,
distinct from the auto-stop idle-shutdown events that `025d59a6` documents at
02:45 and 15:35. These may be the same family of incident or two different
ones; I cannot resolve that by listing. **Verdict: UNKNOWN** — the claim
rests on `HANDSHAKE.md` prose alone; this audit did not find corroborating
execution evidence for it, and per this audit's discipline that is reported
as UNKNOWN rather than silently accepted or silently dropped.

---

## H4e — MODEL-TO-TASK CONFORMANCE

**Model mapping (quoted from `docs/HANDSHAKE.md`, confirmed via `Read`):**
```
claude-fable-5   → fable  → [FABLE] research / scientific writing
claude-opus-4-8  → opus   → [OPUS] engineering, execution, launches
claude-sonnet-4-6→ sonnet → [SONNET] grading, sweeps, cold reads
claude-haiku-4-5 → haiku  → [HAIKU] hygiene, organization, bookkeeping
```

**Git-log-level attribution is structurally uninformative — checked and
ruled out, not skipped:**
```
git log -20 --format='%H|%an|%ae|%cn|%ce'
→ every row: author=committer="Ubuntu <ubuntu@ip-172-31-43-247...>"
git log -30 --format='%H %s%n%b' | grep -B2 "Co-Authored-By"
→ every trailer sampled (16 of 16): "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
  or "Claude Opus 5 (1M context) <noreply@anthropic.com>" — never Fable/Sonnet/Haiku
```
This is **not** evidence that Opus wrote all of it. The exact string
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` is fixed boilerplate
in this harness's own git-commit tool instructions (visible verbatim in this
grader's own Bash tool schema's HEREDOC example) and is applied regardless of
which model is actually running the committing session. I verify this
directly from my own tool definition rather than assuming it — so I treat
every commit trailer in this repo as **uninformative for model attribution**,
not as proof either of conformance or violation. This is itself a finding:
**there is no reliable per-commit model record in this repo**, only the
per-task self-tags inside `docs/HANDSHAKE.md`.

**Cross-check: does `docs/DOCKET.md` carry independent per-task model tags?**
```
grep -no "\[FABLE\]\|\[OPUS\]\|\[SONNET\]\|\[HAIKU\]\|\[ORCH\]" docs/DOCKET.md
→ no matches
```
No. `docs/HANDSHAKE.md` is the only per-item dispatch record available.

**Assessed against the charter's role classes, item by item, from
`docs/HANDSHAKE.md`'s own tags:**

- H2a `[HAIKU]` MOVE_MAP, H2d `[HAIKU]` sizes-to-docket, H3a `[HAIKU]`
  nothing-loose-at-root, H5 `[HAIKU]` spend header — all hygiene/bookkeeping.
  **Conforms.**
- H2b/c `[OPUS]` filter-repo + clone verification — execution/launches.
  **Conforms.**
- H3b `[SONNET]` planted-file grader test, H4 `[SONNET]` this audit —
  grading/sweeps/cold reads. **Conforms.**
- H1 `[OPUS]`: the work described under this tag is "independently
  re-executed by the committing agent, who was not the author... reproduces
  50.2% exactly" — a verification/re-derivation of someone else's numeric
  claim. That is grading-shaped work under the table's own definition
  ([SONNET] = "grading, sweeps, cold reads"), dispatched to OPUS instead.
  **Flagged as a soft/ambiguous mismatch** — running a script to reproduce a
  number is legitimately "execution" too, so this is not called a clean FAIL,
  but it sits closer to the SONNET class than the OPUS class as the table
  defines them.
- H6 `[FABLE]` for drafting LESSONS/conventions/charters: `HANDSHAKE.md`'s
  own table caption defines FABLE as "research / scientific writing," but
  `SUPERVISION_CHARTER.md` §5 (quoted above) states explicitly **"Long-form
  technical writing goes to Opus."** Charters/LESSONS are long-form technical
  writing. This is a direct tension between the standing charter's rule and
  today's order's own dispatch tag. **Flagged as a pre-execution
  conformance risk**, not a committed violation — `HANDSHAKE.md` itself marks
  H6 "NOT STARTED," so nothing has actually run under this tag yet; there is
  nothing to grade by execution here, only a contradiction to flag before it
  is dispatched.

**Verdict: MIXED/UNKNOWN.** Commit-level model attribution is unavailable by
design of this harness (boilerplate trailer). Task-level self-tags in
`docs/HANDSHAKE.md` conform in 6 of 8 checkable cases, with one soft
ambiguity (H1) and one direct charter-vs-order contradiction not yet executed
(H6).

---

## Summary

| item | verdict | basis |
|---|---|---|
| H4a | **FAIL (currently true)** | single worktree, ≥2 live top-level agent sessions attached concurrently at 2026-08-12T16:2xZ; historical 08-11/08-12 collision independently confirmed via `git log`/`git reflog`/`git show` |
| H4b | **PASS (guideline docs) / UNKNOWN (live-agent ownership) / CONFIRMED-1-INSTANCE (orchestrator scope)** | all 4 family guideline files exist; no roster exists to check live-agent ownership; one self-declared ORCH execution independently timestamp-corroborated, no roster to check for a second |
| H4c | **PASS (collectors), live discrepancy found** | 142 `.done`, 0 zero-byte `.done`, 4 `.done.INTERRUPTED`, 0 `.partial` (validated zero, positive-controlled); 0 orphan solver processes (validated zero, positive-controlled); PRODUCT_LIST's published 146 vs. re-derived 142 confirmed live, not just historical |
| H4d | **PASS (tmux absent, config dir readable) / UNKNOWN (weekly-limit incident, cross-session config-dir match)** | tmux confirmed down with a specific error; weekly-limit claim has no corroborating on-disk artifact found |
| H4e | **MIXED/UNKNOWN** | git provides no real per-commit model signal (boilerplate trailer, verified from this grader's own tool schema); HANDSHAKE.md's self-tags conform in 6/8 checkable items, one soft mismatch (H1), one contradiction with charter §5 not yet executed (H6) |

**Allocation violations found, including orchestrator-attributable ones (in
scope per the brief):**
1. Two live top-level agent sessions (PID 1630, PID 1834) sharing the single
   main worktree concurrently, confirmed live at 2026-08-12T16:27:03Z — the
   standing "two chief sessions" hazard, caught in the act rather than
   inferred.
2. The pre-declared 2026-08-11→08-12 dirty-worktree collision, independently
   confirmed via timestamped `git log`/`git show` rather than accepted from
   `HANDSHAKE.md` prose.
3. The self-declared ORCH direct-execution instance (`025d59a6`,
   2026-08-12T15:55:16Z), independently confirmed to exist and match its
   claimed content, with the caveat that git cannot itself attribute the
   commit to "the orchestrator role" — that attribution rests on
   `HANDSHAKE.md`'s own admission, not on independent evidence this grader
   could produce.
4. H6's `[FABLE]` dispatch tag contradicts `SUPERVISION_CHARTER.md` §5's
   "long-form technical writing goes to Opus" rule — not yet executed, so not
   a committed violation, but flagged before dispatch rather than after.

No claim in this report converts an absence of evidence into a PASS; every
zero above carries its stated positive control, and every UNKNOWN marks a
question this grader could not settle by listing rather than being silently
folded into a green verdict.
