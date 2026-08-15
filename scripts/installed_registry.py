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

IT COMPARES CONTENT, NOT MODE -- AND MODE BIT THIS FILE WITHIN THE HOUR
------------------------------------------------------------------------
`scripts/installed/lab.sh` was added here on 2026-08-14 with a shebang and a
755 filesystem bit, and landed in the index as 100644: this repository sets
`core.fileMode=false`, so a `chmod` never reaches the tree that travels. The
suite that catches exactly that (`sdk/tests/test_exec_bits.py`) went red at the
commit, and it went red AFTER the check had been run green, because the file
was still untracked when it was run. Two things follow, both stated here rather
than fixed quietly:

* A CONTENT comparison passes on a pair whose reinstall would produce a
  non-executable copy. `reinstall` commands here are of two kinds -- `install
  -m 755`, which sets the mode explicitly and does not care what the tree
  carries, and a bare `cp`, which propagates whatever mode the tracked file
  has. The `cp` entries are the exposed ones.
* Mode is presently governed by a DIFFERENT mechanism, `exec_bits`, with its
  own hand-maintained waiver register -- and `scripts/auto-stop.sh` and
  `docs/aws/provision.sh` are both waived there while their installed copies
  are 755. Adding a mode rule here would put two checks in disagreement over
  the same files, so it was NOT added unilaterally; whether this registry
  should own mode is filed as a docket row rather than decided in this file.

DECLARED DIVERGENCE, FOR ARTIFACTS THIS LAB MAY NOT INSTALL (D65, 2026-08-14)
-----------------------------------------------------------------------------
`/usr/local/bin/auto-stop.sh` is the box's power control, and docket row A4 puts
that with Katie and Sanaa rather than the fleet. So a reviewed repair to it
lands in the tree and then WAITS -- and between the commit and the install,
tracked and installed differ legitimately and this registry is right to see it.

Two wrong answers were available. Deleting the entry, or exempting the pair,
switches off the one check built out of 2026-07-30. Committing nothing leaves
the repair unwritten. The third is `PendingInstall`: the divergence is DECLARED,
with a reason, an owner, an expiry date, and the sha256 of what the installed
copy is expected to still be. Inside that window the pair reads `PENDING` and
does not fail. Outside it -- expired, or an installed copy that is not the
pinned one -- it FAILS, with the waiver named in the message. A waiver left
behind after the fix is installed is reported by `stale_waivers()`.

The hazard being accepted, stated plainly: while a waiver is live, this machine
is knowingly running an older copy than the tree's reviewed one, which is the
2026-07-30 situation with a note attached. The note is the whole difference, so
it is printed on every run and it lapses by itself.

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
import datetime
import hashlib
import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: States a pair can be in. `DRIFT` and `DANGLING` are failures; `ABSENT` is a
#: skip that must carry a reason; `PENDING` is drift that a waiver explains and
#: that expires; `MATCH` is the only pass.
MATCH, DRIFT, ABSENT, DANGLING, PENDING = (
    "match", "drift", "absent", "dangling", "pending")


@dataclasses.dataclass(frozen=True)
class PendingInstall:
    """A reviewed fix committed to the tree that this lab MAY NOT install.

    Some installed artifacts are not the fleet's to write. `/usr/local/bin/
    auto-stop.sh` is the box's power control and belongs to Katie and Sanaa
    (docket row A4), so a repair to it lands in the tree and then WAITS. Between
    the commit and the install, tracked and installed differ on purpose, and the
    drift check is right to notice.

    The wrong answer is to silence it, because the check being silenced is the
    one built out of 2026-07-30, when a repaired gate sat in the tree uninstalled
    for thirteen days and nothing said so. This is the other answer: the
    divergence is DECLARED, and the declaration is deliberately fragile.

    * `installed_sha256` pins WHAT the installed copy is expected to still be --
      the normalised text of the version this waiver was written against. The
      waiver excuses exactly one known difference. If the installed copy becomes
      anything else, that is unreviewed drift and it FAILS, waiver or no waiver.
    * `expires` is a date, not a mood. Past it the pair fails with the waiver
      named, so a fix nobody installed cannot go quiet by ageing -- which is the
      thirteen-day failure itself.
    * `owner` and `reason` are there because a red check nobody can act on is a
      fault message, not a fix.

    Removing the waiver when the fix is installed is not optional housekeeping:
    `stale_waivers()` reports a waiver whose difference no longer exists, so a
    stale one is visible rather than sitting there excusing nothing.
    """

    reason: str
    owner: str
    expires: str  # YYYY-MM-DD
    installed_sha256: str

    def expired_on(self, today: datetime.date | None = None) -> bool:
        return (today or datetime.date.today()) > datetime.date.fromisoformat(
            self.expires)


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
    pending: PendingInstall | None = None

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
        pending=PendingInstall(
            reason="D65: clause (3), the control-room test, named ONE session "
                   "config directory and the config directory was migrated out "
                   "from under it. Measured 2026-08-14 22:04Z, the clause was "
                   "firing off a transcript last written 21:46:43Z while the "
                   "live one advanced every few seconds, and would have gone "
                   "silent at 22:16:43Z with five agents at work. The tracked "
                   "copy now scans a glob of every config directory. It is NOT "
                   "installed because /usr/local/bin/auto-stop.sh is the box's "
                   "power control and docket row A4 puts that with Katie and "
                   "Sanaa, not the fleet. Until it is installed, the ONLY "
                   "thing holding this box is .autostop-hold, which lapses "
                   "after 24 hours.",
            owner="Katie / Sanaa (docket A4)",
            expires="2026-08-21",
            # The 2026-08-12 rewrite, which is what /usr/local/bin still runs.
            installed_sha256="1e666fac419298f3a6d269cf12c447489409b3e41a8449"
                             "c8f3f7fcf12abfbf9d",
        ),
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
    Deployment(
        name="nightly lab check cron",
        tracked="scripts/installed/certonomous-lab-check.cron",
        source="/etc/cron.d/certonomous-lab-check",
        why="docket D64: nothing in this lab is scheduled to run any check at "
            "all, so every check reddens only when a human types its name. "
            "This is the schedule that would change that. It is registered "
            "here BEFORE it is installed, on purpose: the pair reads ABSENT "
            "with a reason, and the day somebody installs it the drift check "
            "already covers it -- rather than being added to this registry "
            "some later day by somebody who remembers",
        reinstall="sudo install -m 644 -o root -g root "
                  "scripts/installed/certonomous-lab-check.cron "
                  "/etc/cron.d/certonomous-lab-check",
    ),
    Deployment(
        name="pre-push hook",
        tracked="scripts/installed/pre-push",
        source=str(REPO / ".git" / "hooks" / "pre-push"),
        why="the half of D64 that needs no root. A hook the owner can adopt "
            "alone is worth more than a cron they have to be asked for. Note "
            "that `.git/hooks/` is NOT tracked by git and never travels with a "
            "clone, so this pair is also the only thing that can tell a reader "
            "whether the hook on THIS box is the reviewed one",
        reinstall="install -m 755 scripts/installed/pre-push .git/hooks/pre-push",
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


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def compare(dep: Deployment, repo: Path | None = None,
            today: datetime.date | None = None) -> Finding:
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
    want_n, got_n = _normalize(dep.normalize, want), _normalize(dep.normalize, got)
    if want_n == got_n:
        return Finding(dep, MATCH, "")
    import difflib
    diff = "\n".join(difflib.unified_diff(
        want_n.splitlines(), got_n.splitlines(),
        fromfile=f"tracked {dep.tracked}",
        tofile=f"installed {dep.installed_where}", lineterm="", n=1))
    if dep.pending is not None:
        # A declared, dated, content-pinned divergence. Every one of the three
        # ways out of it below is a FAILURE -- the waiver buys a window, not an
        # exemption.
        p = dep.pending
        if p.expired_on(today):
            return Finding(dep, DRIFT,
                           f"PENDING-INSTALL WAIVER EXPIRED on {p.expires}. "
                           f"{p.reason}\nOwner: {p.owner}\n"
                           f"Either it was installed and nobody said so, or it "
                           f"has waited longer than the waiver claimed it "
                           f"would. This is the 2026-07-30 shape -- a repaired "
                           f"file sitting in the tree while the machine runs "
                           f"the old one -- and the waiver's whole job is to "
                           f"stop being quiet about it.\n" + diff[:2000])
        if _sha(got_n) != p.installed_sha256:
            return Finding(dep, DRIFT,
                           f"the installed copy is NOT the version this "
                           f"pending-install waiver was written against "
                           f"(expected sha256 {p.installed_sha256[:16]}..., "
                           f"found {_sha(got_n)[:16]}...). The waiver excuses "
                           f"one known difference; this is a different one, so "
                           f"something unreviewed is running.\n" + diff[:2000])
        return Finding(dep, PENDING,
                       f"declared divergence, waiver expires {p.expires}. "
                       f"{p.reason}\nOwner: {p.owner}\n"
                       f"install with: {dep.reinstall}\n" + diff[:2000])
    return Finding(dep, DRIFT, diff[:4000])


def report(repo: Path | None = None,
           deployments: tuple[Deployment, ...] | None = None) -> list[Finding]:
    return [compare(dep, repo) for dep in (deployments or DEPLOYMENTS)]


def reached(findings: list[Finding]) -> list[str]:
    """Names of the pairs this host actually compared.

    A suite where every entry skipped is green and blind, which is the shape
    L-84 warns about; a caller that wants to know its reach asks for it.
    `PENDING` counts: the pair WAS read and compared, and the difference is
    known down to its hash. What it is not is unnoticed.
    """
    return [f.dep.name for f in findings if f.state in (MATCH, DRIFT, PENDING)]


def stale_waivers(findings: list[Finding]) -> list[tuple[str, str]]:
    """(name, why) for waivers that no longer excuse anything.

    A pending-install waiver on a pair that now MATCHES means the fix was
    installed and the declaration was left behind. Harmless today and dangerous
    later: the next real divergence of that pair would be met by a waiver
    already sitting there. Reported so it is pruned, on the exec_bits precedent
    of refusing a waiver register that has stopped describing the world.
    """
    return [(f.dep.name,
             f"the fix was installed (tracked and installed now match), so the "
             f"pending-install waiver expiring {f.dep.pending.expires} excuses "
             f"nothing -- remove `pending=` from its registry entry")
            for f in findings
            if f.state == MATCH and f.dep.pending is not None]


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


def failures(findings: list[Finding],
             ghosts: list[tuple[str, str]],
             stale: list[tuple[str, str]]) -> list[str]:
    """Everything printed above that must move the exit code, one line each.

    WHY THIS IS A FUNCTION (V15 round 7 F6, docket D95; repaired 2026-08-15)
    -----------------------------------------------------------------------
    `main()` used to end `return 1 if any(f.is_failure for f in findings)
    else 0`, which covers DRIFT and DANGLING and nothing else. Ghosts and stale
    waivers were computed, PRINTED, and then dropped on the floor: the module
    could print `GHOST scripts/auto-stop.sh.proposed is a tracked staging copy`
    -- which is the 2026-07-30 incident's own artifact, the file that sat in
    the tree for thirteen days while the box ran the broken gate -- and exit 0.
    A finding that reaches stdout and not the exit code is invisible to every
    caller that composes this module, which is all of them.

    WHAT STILL DOES NOT FAIL, and both are argued at length in the module
    docstring rather than being oversights:

      * ABSENT. A laptop or CI box has no root crontab and no
        `/usr/local/bin/auto-stop.sh`; nothing is powering that box off, so
        there is nothing to drift. It is a skip with a stated reason, and
        `reached()` is how a caller finds out what was actually compared.
      * PENDING. A declared divergence with an owner, a reason, an expiry and
        the sha256 of what is expected to still be installed. It fails the
        moment the waiver expires or the installed copy becomes anything other
        than the pinned one -- both of which land in DRIFT above.

    V15 round 7 listed this module's `1 PENDING, 2 ABSENT -> exit 0` alongside
    two genuine fail-opens. Re-executed, that part does not hold: PENDING and
    ABSENT are declared non-failure states and DRIFT and DANGLING do exit 1.
    The part that does hold is GHOST and STALE, and that is what changes here.
    """
    out = [f"{f.state.upper()} {f.dep.name}" for f in findings if f.is_failure]
    out += [f"GHOST {ghost} is a tracked staging copy of {artifact}"
            for ghost, artifact in ghosts]
    out += [f"STALE waiver on {name}" for name, _ in stale]
    return out


def main() -> int:
    findings = report()
    for f in findings:
        line = f"{f.state.upper():8} {f.dep.name}  ({f.dep.tracked} -> "
        print(line + f"{f.dep.installed_where})")
        if f.detail:
            print("         " + f.detail.replace("\n", "\n         "))
        if f.state in (DRIFT, PENDING):
            print(f"         reinstall: {f.dep.reinstall}")
    ghosts = staging_ghosts()
    stale = stale_waivers(findings)
    for ghost, artifact in ghosts:
        print(f"GHOST    {ghost} is a tracked staging copy of {artifact}")
    for name, why in stale:
        print(f"STALE    waiver on {name}: {why}")
    print(f"\nreached on this host: {', '.join(reached(findings)) or 'nothing'}")
    bad = failures(findings, ghosts, stale)
    if bad:
        print(f"FAILURES ({len(bad)}) -- each of these moves the exit code:")
        for b in bad:
            print(f"  · {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
