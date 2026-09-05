# SANAA-DIRECT — pre-run checks are bounded, then launch-with-watcher; and the certonomous-lab plugin (2026-09-05, ~21:30Z)

Captured verbatim from the chief session.

## Sanaa's words, verbatim (part 1 — the check-loop bound)

> about dafoam, we must remember my covernence to run ratio standard. The
> checks before the run are neededand jutsified. However, not in an infinite
> loop.  Past some time the lab must take action (this applied to any team)
> and launcht the run with its attached watcher to fix/ debug and see what
> happens: act accordingly. All of this in in our MD files.

## Sanaa's words, verbatim (part 2 — the plugin)

> Also ive been thinking about this: Here's the structure I'd draft:
>
> certonomous-lab/ (the plugin)
>
> .claude-plugin/marketplace.json — so any fleet box installs the lab with
> one command.
> lab.yaml — the team roster form-teams consumes: the six teams, their
> roles, tool scopes, per-team MEMORY.md seed, and which skills each
> preloads. This file is now the single source of truth for lab structure —
> version it, and "what is the lab" has one answer.
> commands/ — /form-teams (yours), plus /converge, /admit-geometry,
> /register, /verify-gradient, /import-grid.
> skills/ — one SKILL.md per doctrine, auto-triggered by description:
> run-to-convergence (the §0 ladder + escalation)
> geometry-admission (fix-or-refuse, the CAD pipeline)
> fd-verification (the step-ladder, 5% gate, sign-reversal rule)
> grid-import (UGRID lane, two-tier admissibility)
> freeze-enforcement (the hook + comparator-sha check)
> certificate (the what-was-not-checked format, sig-figs, banned-language,
> compute-table shape)
> references/ — the deep specs the skills pull on demand: two-tier mesh
> standard, print-interval lesson, cause-class taxonomy, the doctrine stack.
> scripts/ — append_record.py, check_comparator_freeze.py, the grid
> verifier, the whole-run sanity-bound check — installed to ~/.local, never
> global.
> hooks/ — freeze-enforcement mounted on the grade path (infra item 1).
>
> The payoff: your entire directive history stops being oral tradition on
> boards and becomes an installable, versioned lab. A new box runs install
> certonomous-lab → /form-teams → the six teams exist with doctrine
> auto-loaded, gates hook-enforced, MEMORY seeded. And when doctrine changes
> (a new ruling like the two-tier standard), it's a commit to one skill, not
> a re-paste to six teams.

## Context (chief's reading, not her words)

### Part 1 — operative form of the check-loop bound
- Pre-run checks are NEEDED AND JUSTIFIED — nothing here weakens §2ap,
  rehearsals, or the freeze law. What is bounded is the LOOP: check-repair
  cycles that keep breeding new checks.
- Chief's operative default, correctable by her word: an item's pre-launch
  check phase is bounded by THREE check-repair cycles after its first
  freeze-ready attempt OR 24 HOURS of wall time, whichever comes first.
  At the bound, the team LAUNCHES under the standing launch law — remaining
  procedural concerns recorded as predictions, the fleet watcher attached,
  and debugging proceeds against the LIVE run ("fix/debug and see what
  happens: act accordingly").
- The one surviving hard block is unchanged: the ill-posed/evidentiary-core
  class (an inverted mesh; a gate with no producer feeding it; a freeze with
  nothing to hash). Those are fixed before launch — but the FIX itself is
  subject to the same bound.
- Applies to EVERY team. Immediate applications: dafoam's A1WRT2/W3S/D6RF3
  (the trigger for her question) and any future M6SR-shaped item list.
- Consistency: this is her governance-to-run ratio standard + the 2100Z
  launch rule + the fleet-monitor rule composed, as she says, already in
  the MD files; this capture only fixes the numeric default.

### Part 2 — the plugin
- Standing infra task: build `certonomous-lab/` exactly per her structure,
  as a NEW versioned tree in this repository. Content migrates as COPIES
  from the charters/standards/scripts; nothing live is moved or broken.
- Rule-9 boundary: building the plugin tree is authorized by this capture;
  INSTALLING it (touching `.claude/` config on this or any box) remains an
  explicit act of hers or under her word at install time.
- Sequencing per running-first: one infra lane in parallel; it never
  displaces physics dispatches.
- The payoff line is the requirement: doctrine changes become one-skill
  commits; lab.yaml becomes the single source of truth `form-teams`
  consumes (superseding harness/teams.yaml by migration, not deletion).
