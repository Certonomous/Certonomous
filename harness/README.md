# The team harness

Version 1.0, dated 2026-08-22.

Five standing teams re-form from disk whenever a Claude Code session opens in this
repository, with their charters, reading lists, folder scope, standing rules and
current state — and no hand-written brief.

---

## 1. The problem this solves

Agent teams do not survive. A compaction, a session switch, a crashed terminal or
a hit context limit kills every live agent at once, and nothing about them is
persisted: not what they were told, not what they had read, not what they were
part-way through. Before this harness, re-forming the lab meant a human writing
five briefs from memory, every time. Those briefs drifted — each retelling lost a
charter clause, or a rung's real verdict, or the fact that a solver was still
running — and the drift was invisible, because a brief is not checked against
anything.

The harness does not stop teams being killed. **Nothing in Claude Code can.** What
it changes is the cost and the fidelity of re-forming them: one command, and the
state comes off disk rather than out of somebody's head.

## 2. The four pieces

| Piece | What it holds | Why it is separate |
|---|---|---|
| `CLAUDE.md` | The constitution: lab identity, the standing rules, the roster, the first-action rule, the folder convention | Auto-loaded into **every** session, including every subagent. Rules that must bind unconditionally cannot live anywhere a brief could omit them. |
| `.claude/agents/*.md` | Six agent definitions — five supervisors and the one worker type | Loaded when the agent is spawned. Holds what is **stable** about a team: mandate, charter, reading list, folder scope, delegation rules, duties. |
| `docs/LAB_STATE.md` | The resume board: per-team last commit, live jobs, rungs without verdicts, next actions, Sanaa's desk, blocked items | Holds what **changes**. It is the only handoff channel between sessions. |
| `.claude/skills/form-teams/` | The one command that reads the board and spawns all five in parallel | Makes re-formation a reflex rather than a project. |

The split between the second and third rows is the whole design. **A team's
identity is static and belongs in its definition; a team's situation is dynamic
and belongs on the board.** Putting situation into a definition means editing
agent files all day; putting identity onto the board means it rots. Keeping them
apart is what lets `form-teams` pass a supervisor nothing but its own board
section and have that be sufficient.

## 3. The roster is data

`teams.yaml` is the source of truth. `generate_agents.py` renders it into
`.claude/agents/*.md`, and **the committed agent files are that generated output** —
they carry a `GENERATED ... DO NOT EDIT` banner on their first content line.

```bash
python3 harness/generate_agents.py           # write the agent files
python3 harness/generate_agents.py --check   # verify round-trip; exit 1 on drift
```

`--check` is the regression test. It fails on three things: a file whose content
does not match what the YAML renders, an agent file with no entry in the YAML (an
orphan), and frontmatter that does not parse. The generator also refuses to write
anything at all if any file would be malformed — a half-written roster is worse
than none.

**That third check earned its place during the build.** The first draft emitted
`description: Standing supervisor for the closure team: RANS/LES closure line.`
unquoted. The `": "` inside it makes the line a nested mapping, the whole
frontmatter block fails to parse, and Claude Code surfaces that as an agent which
silently does not exist — no error, just a `subagent_type` that is not there. The
generator now emits every description as a JSON string (valid YAML double-quoted
scalar) and parses back every block it writes before committing to disk.

### Frontmatter emitted, and one deliberate omission

```yaml
---
name: closure-supervisor
description: "Standing supervisor for the closure team: RANS/LES closure line. Owns ..."
model: fable
---
```

`tools` is **deliberately absent**. Omitting it grants all tools; listing tools
explicitly would drop the `Agent` tool and break every supervisor's ability to
spawn lanes — a failure that would show up not as an error but as a supervisor
quietly doing the work itself, which is the exact thing the delegation doctrine
forbids.

`model: fable` for supervisors is not a preference. `SUPERVISION_CHARTER.md` §5:
*"Family supervisors and adversarial verifiers run on Fable. Solver, bookkeeping
and liaison agents inherit the session default."* Lanes are `opus`.

## 4. How a session goes

1. The `SessionStart` hook in `.claude/settings.json` prints the first 40 lines of
   the board and `TEAMS NOT FORMED — run /form-teams`. It fires on `startup`,
   `resume`, `clear` and `compact` — **`compact` is the one that matters**, because
   that is when the fleet dies mid-session.
2. `CLAUDE.md` loads automatically and carries the FIRST-ACTION RULE: read
   `docs/LAB_STATE.md`, run `/form-teams`, before any other work.
3. `/form-teams` reads the board, takes a live reading (`git log`, `ps aux`,
   `readlink /proc/<pid>/cwd`), and spawns all five supervisors in **one** parallel
   Agent call, passing each its own board section and the standing directives
   verbatim.
4. Each supervisor updates its own board section at every commit and every
   verdict — not at the end of its turn. That is what makes the next re-formation
   lossless.

The hook is a reminder, not the mechanism. The rule in `CLAUDE.md` is the
mechanism, because it is loaded into context whereas a hook's stdout may only
reach the terminal.

## 5. Known limits, stated plainly

- **Compaction and session switch still kill live agents.** The harness makes
  re-formation one command and, via the board, lossless. It does not make agents
  survive. Any supervisor that has not written its section since its last verdict
  loses that verdict on the next death — which is why the duty is "at every
  commit and every verdict", not "at the end".
- **Agents are loaded at session start, so the harness cannot install itself into
  the session that builds it.** Adding a team, or landing the harness at all, does
  not make those agents spawnable until a NEW session starts; the spawn fails with
  *"Agent type not found"*. **Measured 2026-08-22:** every supervisor was
  unspawnable from the session that wrote it, with correct files on disk. This is
  the harness's sharpest operational edge and `form-teams` now handles it
  explicitly. It also means **`--check` passing is not proof the agents load** —
  it proves the files are well-formed, which is a weaker claim.
- **The board is hand-maintained and can lie.** `/form-teams` and `/lab-state`
  both take a live reading beside it for that reason, and both rule that the
  reading wins. Uncertain entries are marked `VERIFY`.
- **Nothing enforces the lane cap.** "At most 3 lanes live" is written into every
  supervisor definition and checked by nobody. Stated here rather than implied,
  per the charters' own standard: a rule with no check is a preference, and this
  one is currently a preference.
- **Nothing enforces the four personal checks either.** `SUPERVISION_CHARTER.md`
  §7 already says so about itself. The harness does not improve on that; it only
  makes sure every supervisor is told, every time, without a human remembering to.
- **The five teams are an operational split of the charter's four families.**
  `SUPERVISION_CHARTER.md` §2 names four (DAFoam and adjoint; Closure and UQ; Cases
  and campaigns; Infrastructure and standards). This roster splits "cases and
  campaigns" into `heat-transfer` and `cfd`, because the T-family is large enough
  and instrumented enough to be its own line, and maps "infrastructure and
  standards" onto `verification`. Adding or merging a family is Sanaa's call, so
  this is recorded as an operational split, not as a redefinition of the four.

## 6. Adapting this for another lab

Replace `teams:` in `teams.yaml` wholesale and adjust `lab:` and `common:`.
`generate_agents.py` contains no domain knowledge — no CFD, no OpenFOAM, no
mention of any charter by name. Everything domain-specific is in the YAML.

A minimal team entry:

```yaml
  - name: <role>-supervisor        # becomes the subagent_type AND the filename
    team: <short-name>             # the LAB_STATE section heading
    title: <one noun phrase>
    mandate: >-                    # what it owns and the bright line it enforces
      ...
    charters: [ ... ]              # the documents that bind it
    reading:                       # path + WHY; the why is what makes it get read
      - path: ...
        why: ...
    folder_scope: [ ... ]          # what it may touch
    ladders: [ ... ]               # its rungs, so it can say what has no verdict
    notes: [ ... ]                 # optional: standing hazards in its territory
```

Then:

1. Add a matching `## <team>` section to `docs/LAB_STATE.md`.
2. Add the row to the `form-teams` table in `.claude/skills/form-teams/SKILL.md`.
3. Add the row to the TEAM ROSTER table in `CLAUDE.md`.
4. `python3 harness/generate_agents.py && python3 harness/generate_agents.py --check`

**Steps 1–3 used to be manual, and that gap is now closed.** The roster was data in
one place and prose in three others, so a new team could be half-added: `--check`
caught an orphaned agent file but never a team missing from the constitution, the
`form-teams` table or the board. The generator now owns the CLAUDE.md roster table
and the form-teams table as marked regions (`<!-- BEGIN GENERATED ... -->`), and
creates a skeleton board section for any team that lacks one — **never overwriting
an existing section, because sections belong to their supervisors and one may be
mid-write.** So in practice adding a team is: edit `teams.yaml`, run the generator,
run `scripts/check_harness.py`, then **restart the session** so the new agent loads.

What another lab must supply for itself, because it is not portable: the standing
rules in `CLAUDE.md` (they encode this lab's specific failures), the charter
corpus, and the board's initial content.
