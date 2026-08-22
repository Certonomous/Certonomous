---
name: lab-state
description: Print the Certonomous resume board, docs/LAB_STATE.md, with a live reading beside it — current HEAD, running solvers with pid, cwd and iteration, and any uncommitted work. Use when asked for lab status, what is running, where things stand, or what is on Sanaa's desk.
---

# lab-state — print the board

`docs/LAB_STATE.md` is the only handoff channel between sessions. This prints it,
and takes a live reading beside it so a stale board is visible as stale rather
than believed.

## 1. Print the board

```bash
cd /home/ubuntu/Certonomous && cat docs/LAB_STATE.md
```

## 2. Take the live reading

```bash
cd /home/ubuntu/Certonomous
echo "=== HEAD ==="; git log --oneline -5
echo "=== uncommitted ==="; git status --short | head -30
echo "=== solvers ==="; ps aux | grep -iE 'Foam|dafoam' | grep -v grep
```

For every solver pid found:

```bash
echo "pid=$P cwd=$(readlink /proc/$P/cwd)"
ps -o lstart=,etime= -p $P
grep -E '^Time = ' "$(readlink /proc/$P/cwd)"/log.solve 2>/dev/null | tail -1
grep -E '^endTime' "$(readlink /proc/$P/cwd)"/system/controlDict 2>/dev/null
```

**Never touch a running solver.** This skill reads; it does not manage.

## 3. Report

Print the board, then a short reconciliation:

- **Board vs reality** — any line the live reading contradicts. The reading wins,
  and the correction belongs to the supervisor who owns that section, not to you.
- **Live jobs** — pid, cwd, iteration of endTime, ETA, owning team.
- **On Sanaa's desk** — aggregated across all sections, with how long each item
  has been waiting.
- **Staleness** — when each section was last written. A section not updated since
  before the last commit to its territory is stale, and say so.

Do not repair the board from this skill. If it is wrong, that is a finding to
route to the owning supervisor.
