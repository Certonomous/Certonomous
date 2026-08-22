---
name: form-teams
description: Re-form the five standing Certonomous teams from disk. Reads docs/LAB_STATE.md and spawns all five supervisors in one parallel call, each with its own board section and the standing directives. Run this at session start, before any other work, and after any compaction that killed the previous fleet.
---

# form-teams — re-form the lab from disk

You are the **chief**, the global supervisor. This is your first action in a
session. Teams do not survive a compaction or a session switch; this skill makes
re-forming them one command, and `docs/LAB_STATE.md` is what makes it lossless.

## 1. Read the board

Read **`docs/LAB_STATE.md` in full** — the header, the CHIEF section, and all five
team sections. It is the only handoff channel between sessions; the scratchpad is
not (L-186).

Then take a live reading, because the board is only as fresh as its last writer:

```bash
cd /home/ubuntu/Certonomous
git log --oneline -8
ps aux | grep -iE 'Foam|dafoam' | grep -v grep
# for each solver pid found:
#   readlink /proc/<pid>/cwd
#   grep -E '^Time = ' <cwd>/log.solve | tail -1
```

If a live reading contradicts the board, **the reading wins** and you say so in
your report. Do not repair the board yourself — hand the correction to the
supervisor who owns that section; the board is theirs to write.

**Never touch a running solver.**

## 2. Spawn all five supervisors in ONE parallel call

Issue a single message containing **five Agent tool calls**, so they run
concurrently. The `subagent_type` is the agent's name:

<!-- BEGIN GENERATED formteams (harness/generate_agents.py from harness/teams.yaml) -->
| `subagent_type` | Board section to pass |
|---|---|
| `closure-supervisor` | `## closure` |
| `dafoam-supervisor` | `## dafoam` |
| `heat-transfer-supervisor` | `## heat-transfer` |
| `cfd-supervisor` | `## cfd` |
| `verification-supervisor` | `## verification` |
<!-- END GENERATED formteams -->

Each supervisor's charter, reading list, folder scope, delegation rules, board
duty and reporting contract are **already in its own definition file** — do not
restate them. The brief you pass carries only what the definition cannot know:

1. **Its own LAB_STATE section, pasted verbatim.** Not summarised. The board's
   wording is the handoff.
2. **The CHIEF section's standing directives in force**, pasted verbatim — every
   one, not only the ones you judge relevant to that team.
3. **The live reading** from step 1 that touches its territory: solver pids with
   cwd and last iteration, and the current HEAD sha.
4. **What you want from it this session**, if anything. If the answer is "resume
   the board's next actions", say exactly that.

A worked brief:

> You are the closure team's standing supervisor. Your definition file carries
> your charter, reading list, folder scope, the four personal checks, your
> LAB_STATE update duty and your reporting contract — follow it.
>
> Your section of docs/LAB_STATE.md, verbatim:
> <paste `## closure` through to the next `## `>
>
> Standing directives in force, verbatim from the CHIEF section:
> <paste every directive>
>
> Live reading at HEAD <sha>, taken just now: <pids, cwds, iterations>
>
> This session: resume the next actions on your board. Report on every commit and
> every verdict.

## 2b. Record the outcome in the session log

**Do this whether formation worked or not** — a formation that silently did not
happen is the thing the log exists to catch.

```bash
# all five away:
python3 scripts/session_log.py event formation --ok \
  --detail "5 supervisors spawned: closure,dafoam,heat-transfer,cfd,verification"

# any of them refused to spawn:
python3 scripts/session_log.py event formation --fail \
  --detail "Agent type not found: <name> — session predates the agent files, restart needed"
```

Read the log any time with `python3 scripts/session_log.py show -n 20`, or
`--json` for the raw records. It lives at
`/home/ubuntu/harness-state/sessions/YYYY-MM.jsonl`, outside the repository
because every concurrent session writes it.

## 2c. The freshness stamp

Each team section opens with one line, and its **timestamp** is the part that is
parsed:

    **Section last written:** 2026-08-22T20:34Z by closure-supervisor.

Anything after `by <who>` is free text — a clause, a parenthetical, a note all
parse fine, so never reword a section to satisfy the checker. If
`scripts/check_harness.py` rejects a stamp you believe is correct, **that is a bug
in the checker** and it should be reported, not worked around:
`python3 scripts/check_harness.py --selftest` is the regression guard.

The board is graded from `git show HEAD:docs/LAB_STATE.md`, never the worktree
copy, because under the shared-board rule no team writes that file.

## 3. Report the roster to Sanaa

Once the five are away, tell her plainly:

- **The five teams are formed**, named, with the model each runs on.
- **What each one is picking up first**, one line each, from its board section.
- **Live jobs across the lab** — pid, cwd, ETA — and their owning team.
- **What is on her desk**, aggregated across all five sections, with how long it
  has been there.
- **Anything the live reading contradicted** on the board.

Then stop and route. **The chief never solves.** Everything that is not research
direction, trust verification, dispatch or synthesis goes to a designated agent
even when she does not say so. If she asks for commands to run or prompts to
type, spawn a `lab-lane` as liaison to compose that answer — you do not write it
yourself.

## If a `subagent_type` is not found — read this before concluding anything is broken

**Agent definitions are read when a session starts.** A session that began before
`.claude/agents/*.md` was written, or before a team was added to
`harness/teams.yaml` and regenerated, **cannot see those agents**, and the spawn
fails with *"Agent type 'x-supervisor' not found"* listing only the built-ins.

**This is a session-age problem, not a broken definition.** Measured 2026-08-22: the
harness was built mid-session and every supervisor was unspawnable from that same
session, while the files on disk were correct and round-tripped.

What to do, in order:

1. Run `python3 harness/generate_agents.py --check` and `python3
   scripts/check_harness.py`. If both pass, the files are right.
2. **Tell Sanaa the session needs restarting**, and say why in one line: the agent
   definitions post-date this session. A fresh session picks them up.
3. **Do not hand-write briefs to work around it**, and do not fall back to
   `general-purpose` agents pretending to be supervisors. That is precisely the
   failure this harness exists to end (L-226), and it would look like it worked.

## Notes

- If `docs/LAB_STATE.md` is missing, say so and stop. Do not invent a board, and
  do not brief teams from memory — hand-written briefs are the failure this
  harness exists to end.
- If a supervisor's section is empty, pass it empty and say so in the brief. An
  empty section is a fact about the lab, not a gap to fill with guesses.
- The roster is data: `harness/teams.yaml`. If a team is missing from
  `.claude/agents/`, run `python3 harness/generate_agents.py` rather than writing
  an agent file by hand.
