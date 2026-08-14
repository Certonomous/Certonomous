"""EVERY GATE DIFFS INSTALLED AGAINST TRACKED. The registry, and the one
mechanism that reads it.

WHY THIS FILE EXISTS (D53, 2026-08-14)
--------------------------------------
On 2026-07-30 a repaired `/usr/local/bin/auto-stop.sh` was written to
`scripts/auto-stop.sh.proposed`, committed, and never installed. `diff` on
2026-08-12 proved the running file was still byte-identical to the pre-repair
backup. The machine ran the broken gate for thirteen days and powered itself
off twice, the second time in the middle of a verification suite. Nothing in
the lab was comparing what was reviewed against what was running.

The defect class is not "the gate had a bad regex". It is:

    A FIX THAT LIVES ONLY IN THE REPO CANNOT BE ASSUMED TO BE RUNNING,
    AND NOTHING WAS CHECKING.

`sdk/tests/test_autostop_gate.py` closed that for ONE artifact by hard-coding
one pair of paths. This module generalises it: the pairs are DATA, the drift
comparison is one mechanism, and adding a gate later is a registry entry rather
than a new test file. `sdk/tests/test_installed_matches_tracked.py` drives it.

WHAT THE MECHANISM PROMISES, AND WHAT IT DOES NOT
-------------------------------------------------
* It TOLERATES ABSENCE. A laptop or CI box has no root crontab and no
  `/usr/local/bin/auto-stop.sh`; nothing is powering that box off, so there is
  nothing to drift. Absence is a skip with a stated reason, never a pass.
* It REFUSES DRIFT. An installed copy that differs from the tracked one is the
  2026-07-30 failure, and it fails loudly with the reinstall command.
* It REFUSES A DANGLING ENTRY. If the TRACKED side of a pair is missing from
  the tree, that is a failure, not a skip -- a registry that points at nothing
  is a checker that can never fire (L-84).
* IT CANNOT SEE what it cannot read. `sudo -n crontab -l` needs passwordless
  sudo; where that is unavailable the root crontab entry reads as ABSENT and
  drift there would go unnoticed. That hole is stated rather than hidden, and
  `reached()` is what a caller uses to find out which entries were actually
  compared on this host instead of trusting a green suite.

ENUMERATED BY EXECUTION ON 2026-08-14, AND DELIBERATELY NOT REGISTERED
----------------------------------------------------------------------
The enumeration was run rather than guessed (`sudo crontab -l`, `crontab -l`,
`/etc/crontab`, `/etc/cron.d`, `/var/spool/cron/crontabs`, `ls /usr/local/bin`,
`ls /usr/local/sbin`, `/etc/systemd/system`, `systemctl list-unit-files
--state=enabled`, `.git/hooks`, `~/.local/bin`). What it found and what was
left out, so the next reader does not have to re-derive the negative:

* `/usr/local/bin/vsp`, `vspaero`, `vspscript`, `vspslicer`, `vspviewer` --
  symlinks into `/opt/OpenVSP`. Third-party install, no tracked counterpart to
  diff against. Their VERSION is a different question and not this one.
* `/usr/local/bin/auto-stop.sh.orig-20260730`, `auto-stop.sh.orig-20260812` --
  backups taken during the incidents. Not running (nothing invokes them), not
  tracked. Kept as evidence; registering them would assert a tracked
  counterpart that does not and should not exist.
* NO local systemd unit on this host references this repository
  (`grep -rl Certonomous /etc/systemd/` is empty), so there is no unit to pair.
* `.git/hooks` contains only the `*.sample` files git ships. No installed hook,
  so no hook pair. A hook added later is a registry entry.
* `/etc/cron.d` holds only `e2scrub_all` and `sysstat`, both distribution
  files, and `/etc/crontab` is stock.
* `dist/certonomous-demo.zip` drifts from the tree too, but it lives INSIDE the
  tree and already has its own gate (`check_bundle_drift`,
  `sdk/tests/test_bundle_drift_gate.py`). This registry is for artifacts that
  live OUTSIDE it.
* `/home/ubuntu/certonomous-runs/*/memwatch.py` and `ugrid_to_foam.py` -- per-run
  copies taken when a case was launched. NOT registered, and the reason is a
  judgement rather than an oversight: a run directory is a PROVENANCE record,
  and a copy frozen at what actually ran is what it is for. Requiring it to
  equal the tracked file forever would destroy the record it exists to keep.
  One of them has nevertheless drifted the DANGEROUS way -- the
  `dpw5-committee-probe` copy of `ugrid_to_foam.py` is 17590 bytes against the
  tracked 15004, i.e. a larger, newer, unreviewed fork that produced published
  results and never came back to the tree. That is a different defect class
  (code that RAN was never reviewed, the mirror of D53's review that never
  ran), filed on its own row rather than forced into this registry.
* `~/.claude/settings.local.json` inside the repo is git-ignored by a
  user-global ignore file OUTSIDE the repo, so it is invisible to repo-scoped
  review while granting a Bash allowlist. Configuration is out of this row's
  scope and was not touched; it is reported rather than registered.

HOW THE TRACKED SIDE OF THREE OF THESE PAIRS CAME TO EXIST, WHICH MATTERS
-------------------------------------------------------------------------
`scripts/installed/crontab.root`, `scripts/installed/crontab.ubuntu` and
`scripts/installed/lab.sh` had NO tracked counterpart before 2026-08-14. Their
tracked copies were ADOPTED from what was running on this box on that date --
they were not authored, reviewed and then installed. So at adoption these three
pairs match BY CONSTRUCTION, and the first comparison of each proves nothing
about whether what is running is right. What they buy starts at the second
comparison: from here, a change on either side that is not made on both is
refused. Anyone reviewing the machine's schedule should review these files
now, because nobody has.
"""

from __future__ import annotations

import dataclasses
import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: States a pair can be in. `DRIFT` and `DANGLING` are failures; `ABSENT` is a
#: skip that must carry a reason; `MATCH` is the only pass.
MATCH, DRIFT, ABSENT, DANGLING = "match", "drift", "absent", "dangling"


@dataclasses.dataclass(frozen=True)
class Deployment:
    """One (tracked -> installed) pair.

    `source` is either an absolute path (the installed FILE) or a command whose
    stdout IS the installed content -- a crontab has no file a normal user can
    read, so the command is the only honest reader of it.

    `normalize` names how to compare. `"text"` compares bytes. `"crontab"`
    drops the three header comments `crontab` regenerates on every install
    (they carry an install timestamp, which would read as drift every time the
    same content is reinstalled) and trailing whitespace. Normalisation is
    named per entry rather than applied globally so that what is ignored is
    visible at the pair, not buried in the comparator.
    """

    name: str
    tracked: str
    source: str | tuple[str, ...]
    why: str
    reinstall: str
    normalize: str = "text"

    @property
    def slug(self) -> str:
        return re.sub(r"[^A-Z0-9]+", "_", self.name.upper()).strip("_")

    @property
    def env_override(self) -> str:
        """Env var that redirects the INSTALLED side at a file.

        Derived from the name rather than typed per entry, so a new pair gets
        one for free. It exists so drift can be PLANTED in a scratch directory
        and the check shown to redden -- a checker never seen to fail is not a
        detector.
        """
        return f"CERTONOMOUS_INSTALLED_{self.slug}"

    @property
    def installed_where(self) -> str:
        return (self.source if isinstance(self.source, str)
                else "$ " + " ".join(self.source))


DEPLOYMENTS: tuple[Deployment, ...] = (
    Deployment(
        name="auto-stop gate",
        tracked="scripts/auto-stop.sh",
        source="/usr/local/bin/auto-stop.sh",
        why="root cron runs this every 5 minutes and it powers the box off; "
            "the tracked copy is the only reviewed one",
        reinstall="sudo install -m 755 scripts/auto-stop.sh "
                  "/usr/local/bin/auto-stop.sh",
    ),
    Deployment(
        name="root crontab",
        tracked="scripts/installed/crontab.root",
        source=("sudo", "-n", "crontab", "-l"),
        why="the schedule that runs the auto-stop gate. A correct gate on no "
            "schedule is no gate, and a gate on a 1-minute schedule is a "
            "different machine; neither is visible in the script itself",
        reinstall="sudo crontab scripts/installed/crontab.root",
        normalize="crontab",
    ),
    Deployment(
        name="ubuntu crontab",
        tracked="scripts/installed/crontab.ubuntu",
        source=("crontab", "-l"),
        why="brings the demo servers up at boot; an entry silently dropped "
            "here is a control room that is simply not there after a reboot",
        reinstall="crontab scripts/installed/crontab.ubuntu",
        normalize="crontab",
    ),
    Deployment(
        name="provision script",
        tracked="docs/aws/provision.sh",
        source="/home/ubuntu/provision.sh",
        why="the copy that actually provisioned this box. If the reviewed one "
            "and the run one differ, the documented build of this machine is "
            "not the build it has",
        reinstall="cp docs/aws/provision.sh /home/ubuntu/provision.sh",
    ),
    Deployment(
        name="lab session launcher",
        tracked="scripts/installed/lab.sh",
        source="/home/ubuntu/lab.sh",
        why="the tmux session every operator attaches to, and the only thing "
            "that starts the control room by hand. It had NO tracked copy at "
            "all until 2026-08-14 -- unreviewable machinery rather than drift",
        reinstall="cp scripts/installed/lab.sh /home/ubuntu/lab.sh",
    ),
)

#: A staging copy of a registered artifact, tracked and never installed, is the
#: exact ghost that made 2026-07-30 invisible for thirteen days: the tree LOOKS
#: repaired, and the pair a reader diffs is the wrong one.
_GHOST_SUFFIX = re.compile(
    r"\.(proposed|new|fixed|patched|orig|bak|old|installed)"
    r"(?:[-.]?[0-9]{4,})?$", re.I)

_CRONTAB_HEADER = re.compile(
    r"^# (DO NOT EDIT THIS FILE|\(- installed on |\(Cron version)")


def _normalize(kind: str, text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    if kind == "crontab":
        lines = [ln for ln in lines if not _CRONTAB_HEADER.match(ln)]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def installed_text(dep: Deployment) -> tuple[str | None, str]:
    """(text, reason it is absent). Exactly one of the two is meaningful.

    Absence is never an exception escaping into the caller: a missing file, an
    unreadable one, a missing binary and a command that exits non-zero are all
    the same statement -- there is no installed copy this host can show us --
    and each carries the reason with it so a skip can never read as a pass.
    """
    override = os.environ.get(dep.env_override)
    source: str | tuple[str, ...] = override if override else dep.source
    if isinstance(source, str):
        try:
            return Path(source).read_text(), ""
        except FileNotFoundError:
            return None, f"{source} does not exist on this host"
        except (PermissionError, OSError, UnicodeDecodeError) as exc:
            return None, f"{source} is not readable: {type(exc).__name__}: {exc}"
    try:
        run = subprocess.run(source, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, (f"`{' '.join(source)}` could not be run: "
                      f"{type(exc).__name__}: {exc}")
    if run.returncode != 0:
        return None, (f"`{' '.join(source)}` exited {run.returncode}: "
                      f"{(run.stderr or run.stdout).strip()[:200]}")
    return run.stdout, ""


@dataclasses.dataclass(frozen=True)
class Finding:
    dep: Deployment
    state: str
    detail: str

    @property
    def is_failure(self) -> bool:
        return self.state in (DRIFT, DANGLING)


def compare(dep: Deployment, repo: Path | None = None) -> Finding:
    """One pair, one verdict."""
    root = Path(repo) if repo else REPO
    tracked = root / dep.tracked
    try:
        want = tracked.read_text()
    except OSError as exc:
        return Finding(dep, DANGLING,
                       f"the TRACKED side is unreadable at {tracked} "
                       f"({type(exc).__name__}). A registry entry whose "
                       f"reviewed copy is missing can never fire.")
    got, why = installed_text(dep)
    if got is None:
        return Finding(dep, ABSENT, why)
    if _normalize(dep.normalize, want) == _normalize(dep.normalize, got):
        return Finding(dep, MATCH, "")
    import difflib
    diff = "\n".join(difflib.unified_diff(
        _normalize(dep.normalize, want).splitlines(),
        _normalize(dep.normalize, got).splitlines(),
        fromfile=f"tracked {dep.tracked}",
        tofile=f"installed {dep.installed_where}", lineterm="", n=1))
    return Finding(dep, DRIFT, diff[:4000])


def report(repo: Path | None = None,
           deployments: tuple[Deployment, ...] | None = None) -> list[Finding]:
    return [compare(dep, repo) for dep in (deployments or DEPLOYMENTS)]


def reached(findings: list[Finding]) -> list[str]:
    """Names of the pairs this host actually compared.

    A suite where every entry skipped is green and blind, which is the shape
    L-84 warns about; a caller that wants to know its reach asks for it.
    """
    return [f.dep.name for f in findings if f.state in (MATCH, DRIFT)]


def staging_ghosts(repo: Path | None = None,
                   deployments: tuple[Deployment, ...] | None = None
                   ) -> list[tuple[str, str]]:
    """Tracked (ghost, artifact) pairs: a staging sibling of a registered file.

    `git ls-files` rather than a filesystem walk on purpose -- `grep` on this
    box honours .gitignore (L-75) and an untracked scratch copy is nobody's
    ghost. What makes a ghost is being COMMITTED beside the real artifact while
    not being what runs.
    """
    root = Path(repo) if repo else REPO
    try:
        tracked = subprocess.run(["git", "ls-files"], cwd=root, text=True,
                                 capture_output=True, timeout=120,
                                 check=True).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return []
    ghosts = []
    for dep in (deployments or DEPLOYMENTS):
        for path in tracked:
            if path == dep.tracked or not path.startswith(dep.tracked + "."):
                continue
            if _GHOST_SUFFIX.search(path):
                ghosts.append((path, dep.tracked))
    return sorted(ghosts)


def main() -> int:
    findings = report()
    for f in findings:
        line = f"{f.state.upper():8} {f.dep.name}  ({f.dep.tracked} -> "
        print(line + f"{f.dep.installed_where})")
        if f.detail:
            print("         " + f.detail.replace("\n", "\n         "))
        if f.state == DRIFT:
            print(f"         reinstall: {f.dep.reinstall}")
    for ghost, artifact in staging_ghosts():
        print(f"GHOST    {ghost} is a tracked staging copy of {artifact}")
    print(f"\nreached on this host: {', '.join(reached(findings)) or 'nothing'}")
    return 1 if any(f.is_failure for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
