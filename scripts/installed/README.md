# Tracked copies of things that run OUTSIDE this tree

**These files are not run from here.** They are the reviewable copy of machinery
that lives elsewhere on the box, so that `scripts/installed_registry.py` can diff
what is INSTALLED against what is TRACKED, and
`sdk/tests/test_installed_matches_tracked.py` can refuse any difference.

## What is mirrored

Six files, read from the registry at frame `8cefb4e9`. Re-derive the state column
with `python3 scripts/installed_registry.py`, which is the only thing that can
tell you whether the copy on THIS box is the reviewed one.

| Tracked copy | The thing it mirrors | State at `8cefb4e9` | How to install |
|---|---|---|---|
| `crontab.root` | root's crontab, `sudo crontab -l`. Runs the auto-stop gate every five minutes | MATCH | `sudo crontab scripts/installed/crontab.root` |
| `crontab.ubuntu` | the `ubuntu` user's crontab, `crontab -l`. Brings the demo servers up at boot | MATCH | `crontab scripts/installed/crontab.ubuntu` |
| `lab.sh` | `/home/ubuntu/lab.sh`, the tmux session operators attach to | MATCH | `cp scripts/installed/lab.sh /home/ubuntu/lab.sh` |
| `pre-commit` | `.git/hooks/pre-commit`, the index guard | MATCH | `install -m 755 scripts/installed/pre-commit .git/hooks/pre-commit` |
| `pre-push` | `.git/hooks/pre-push` | ABSENT, not installed | `install -m 755 scripts/installed/pre-push .git/hooks/pre-push` |
| `certonomous-lab-check.cron` | `/etc/cron.d/certonomous-lab-check` | ABSENT, not installed | `sudo cp scripts/installed/certonomous-lab-check.cron /etc/cron.d/` |

The registry carries two further rows whose tracked copy lives outside this
directory: the provision script (`docs/aws/provision.sh`, MATCH) and the
auto-stop gate (`scripts/auto-stop.sh`, PENDING under a declared divergence
waiver). Eight rows in total.

`.git/hooks/` is not tracked by git and never travels with a clone, so a hook
being present in this directory is not evidence that it is armed on any given
machine.

## Editing rules

**Do not add a comment to the crontab files as documentation.** The comparison is
against `crontab -l` output, and a comment present on one side and not the other
reads as drift. Only the three headers `crontab` regenerates on every install are
normalised away, and deliberately nothing else. See
`installed_registry._normalize`.

**The auto-stop gate itself is not mirrored here.** `scripts/auto-stop.sh` stays
where it is and is registered from there. Moving reviewed, executed scripts into
this directory would make it look like the place fixes go to wait, which is the
exact defect this directory exists to close.

## Limits

1. **These copies were adopted from what was already running, not authored,
   reviewed and then installed.** Each pair therefore matched by construction on
   the day it was added, and that first green proves nothing about whether the
   schedule is right. Only that the tree now records it.

2. **The value starts at the second comparison.** A change made on one side and
   not the other is refused from that point on. Before that point the mechanism
   has said nothing.

3. **Nobody has reviewed the content of these files.** That review is still owed,
   and no green from the registry or the test substitutes for it.

4. **Two of the six are not installed anywhere**, so for those rows the registry
   is comparing a tracked file against nothing and reports ABSENT rather than a
   match or a difference.
