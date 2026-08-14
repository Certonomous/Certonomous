# Tracked copies of things that run OUTSIDE this tree

**Adopted 2026-08-14 (docket D53). These files are not run from here.** They are
the reviewable copy of machinery that lives elsewhere on the box, so that
`scripts/installed_registry.py` can diff what is INSTALLED against what is
TRACKED and `sdk/tests/test_installed_matches_tracked.py` can refuse any
difference.

| file | the thing it mirrors | how to reinstall |
|---|---|---|
| `crontab.root` | root's crontab (`sudo crontab -l`) — runs the auto-stop gate every 5 minutes | `sudo crontab scripts/installed/crontab.root` |
| `crontab.ubuntu` | the `ubuntu` user's crontab (`crontab -l`) — brings the demo servers up at boot | `crontab scripts/installed/crontab.ubuntu` |
| `lab.sh` | `/home/ubuntu/lab.sh` — the tmux session operators attach to | `cp scripts/installed/lab.sh /home/ubuntu/lab.sh` |

**What these files ARE NOT.** They were **adopted from what was running on
2026-08-14**, not authored, reviewed and then installed. So each pair matched by
construction on the day it was added, and that first green proves nothing about
whether the schedule is *right* — only that the tree now records it. The value
starts at the second comparison: a change made on one side and not the other is
refused from here on. **Nobody has reviewed the content of these three; that
review is still owed.**

**Do not add a comment to the crontab files as documentation.** The comparison is
against `crontab -l` output, and a comment present on one side and not the other
reads as drift. Only the three headers `crontab` regenerates on every install
are normalised away, and deliberately nothing else — see
`installed_registry._normalize`.

**The gate itself is not here.** `scripts/auto-stop.sh` stays where it is and is
registered from there; moving reviewed, executed scripts into this directory
would make it look like the place fixes go to wait, which is the exact defect
D53 exists to close.
