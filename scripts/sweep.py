#!/usr/bin/env python3
"""A repo sweep that states its own frame, and refuses to hand you a bare number.

WHY THIS EXISTS (L-75). `grep` in this environment is a shell function, not
`/usr/bin/grep`. It execs `ugrep -G --ignore-files --hidden -I
--exclude-dir=.git ...`, and `--ignore-files` honours `.gitignore`. This lab
gitignores its large case archives, so a repo-wide `grep -r` here reaches a
fraction of the tree and reports a clean, confident, silent zero over the rest.
Three committed documents inherited counts from it without the filter being
mentioned once.

Measured with this module at commit `83ed6dab`, repo root, and true only for
that moment (L-79 -- a quoted figure is a snapshot and needs its commit):
`everything` selects 59,560 files, `worktree` 58,083, `tracked` 20,562, and
`ignore-honouring` -- the model of what `grep -r` here actually sweeps --
13,626. Of the tracked files, 6,938 are also gitignored, so `grep -r` skips
them despite their being in the index. Re-derive with
`python3 scripts/sweep.py --list-frames` and a sweep of your own rather than
quoting these.

Reproduced with a planted control, in the test file beside this module:
  `test_gitignored_plant_is_seen_by_the_everything_frame`
  `test_positive_control_ignore_honouring_frame_does_not_see_the_plant`
Those two tests are this module's reason to exist; if they ever stop
disagreeing with each other, the defect this module guards has changed shape
and the module needs re-reading rather than trusting.

WHAT THIS MODULE REFUSES TO DO. Four refusals, each one a defect class this
lab has been burned by:

  1. It does not return a count without a FRAME. Root, the file-selection rule
     in words, the filter actually applied, files considered, files searched,
     files skipped broken out BY REASON, and the commit the sweep ran at, all
     ride on the result object and all print in the sweep's own output.
     A count whose frame nobody can state is worse than no number (L-75), and
     a frame is filter AND moment, not one of the two (L-79).
  2. It answers "did the check run?" before "what did it find?" There are
     three verdicts, not two. `MATCHES`, `ZERO`, `UNKNOWN`. A file that raised
     is not a file that contained no match, so a read failure produces UNKNOWN
     even when other files matched: the sweep did not complete, and a partial
     sweep reporting a total is the failure mode itself.
     Evidence: `test_unreadable_file_forces_unknown_not_zero`.
  3. It has no default frame. The caller names one. There is no frame here
     documented as "everything" that is anything less than everything --
     `EVERYTHING_UNDER_ROOT` includes dotfiles and `.git/` internals, and the
     frame that drops VCS metadata is named for what it drops.
     Evidence: `test_everything_frame_includes_git_internals`.
  4. Results from different frames refuse to be compared. Two such numbers are
     two different measurements (L-75), and an unexplained gap between them is
     usually that, not a discovery. `==` between differing frames raises
     `FrameMismatch` rather than answering.
     Evidence: `test_comparing_two_frames_raises_rather_than_answering`.

ON ABSOLUTES (L-76). This lab has published four absolute claims that turned
out to be false, so the rule here is: no `never` / `always` / `cannot` /
`every` / `no longer` in this file's prose without an executed test named on
the same line. That rule is itself executed, not promised:
`test_no_unbacked_absolute_in_sweep_source` reads this file, finds each
absolute, and fails unless a real test in the suite is named beside it.

USAGE

    from scripts.sweep import sweep, EVERYTHING_UNDER_ROOT, TRACKED_ONLY
    res = sweep("adjUseColoring", root=".", frame=EVERYTHING_UNDER_ROOT)
    print(res.report())        # frame block + verdict + hits
    res.verdict                # "MATCHES" | "ZERO" | "UNKNOWN"
    res.matched_files          # int, and it carries its frame with it

    python3 scripts/sweep.py --frame everything 'adjUseColoring'
    python3 -m scripts.sweep --list-frames
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence

__all__ = [
    "Frame",
    "FrameMismatch",
    "Hit",
    "Skips",
    "SweepResult",
    "FRAMES",
    "EVERYTHING_UNDER_ROOT",
    "WORKING_TREE_NO_VCS",
    "TRACKED_ONLY",
    "IGNORE_HONOURING",
    "sweep",
    "select_files",
]

DEFAULT_SIZE_CAP = 4 * 1024 * 1024
_VCS_DIRS = {".git", ".hg", ".svn", ".bzr", ".jj", ".sl"}


class FrameMismatch(RuntimeError):
    """Raised when two counts taken under different frames are compared.

    They are two measurements, not one measurement twice. Reconciling them is
    the mistake L-75 records; the auditor there killed its own sweep rather
    than let a fourth incommensurable number land.
    """


class SweepIncomplete(RuntimeError):
    """Raised by `SweepResult.require_complete()` on an UNKNOWN verdict."""


# --------------------------------------------------------------------------
# Frames. A frame is a named file-selection rule plus the words that describe
# it honestly. The caller picks one; there is no default.
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Frame:
    """A named file-selection rule, its plain-words description, and its filter.

    `selector` yields paths relative to root. `filter_words` states what the
    frame leaves out -- the sentence L-75 says was missing from three
    documents. A frame whose `filter_words` reads "none" is asserting it
    excludes nothing, which `test_everything_frame_includes_git_internals`
    checks for `EVERYTHING_UNDER_ROOT` by planting a file inside `.git/`.
    """

    name: str
    rule_words: str
    filter_words: str
    selector: Callable[[Path], Iterable[Path]]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


def _walk_all(root: Path, drop_vcs: bool) -> Iterator[Path]:
    """Yield each non-directory entry under root, symlinks and oddities kept.

    Entries that are not regular files are not silently dropped here -- they
    are carried through so the reader stage can name them in the skip
    breakdown. A dangling symlink is a thing under the root the sweep could
    not read, and reporting it as "not present" is the exact lie this module
    is built against.
    """
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        if drop_vcs:
            dirnames[:] = [d for d in dirnames if d not in _VCS_DIRS]
        dirnames.sort()
        for name in sorted(filenames):
            yield Path(dirpath) / name


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, check=False)


def _tracked(root: Path) -> Iterator[Path]:
    proc = _git(root, "ls-files", "-z")
    if proc.returncode != 0:
        raise RuntimeError(f"git ls-files failed under {root}: {proc.stderr.strip()}")
    for rel in proc.stdout.split("\0"):
        if rel:
            yield root / rel


def _ignored_paths(root: Path, candidates: Sequence[Path]) -> set[Path]:
    """The subset of `candidates` that .gitignore rules exclude.

    `--no-index` is load-bearing and was checked rather than assumed. Without
    it `git check-ignore` consults the index and reports a tracked file as
    not-ignored, while ugrep's `--ignore-files` knows nothing about the index
    and skips it anyway. This repo carries thousands of tracked-but-gitignored
    files, so the wrong flag here would understate the defect it models.
    """
    if not candidates:
        return set()
    payload = "\0".join(str(p.relative_to(root)) for p in candidates) + "\0"
    proc = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-z", "--no-index", "--stdin"],
        input=payload, capture_output=True, text=True, check=False)
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"git check-ignore failed: {proc.stderr.strip()}")
    return {root / rel for rel in proc.stdout.split("\0") if rel}


def _ignore_honouring(root: Path) -> Iterator[Path]:
    candidates = list(_walk_all(root, drop_vcs=True))
    ignored = _ignored_paths(root, candidates)
    for p in candidates:
        if p not in ignored:
            yield p


EVERYTHING_UNDER_ROOT = Frame(
    name="everything",
    rule_words="os.walk from root; each non-directory entry, dotfiles and "
               ".git/ internals included",
    filter_words="none -- no ignore rules, no directory exclusions",
    selector=lambda root: _walk_all(root, drop_vcs=False),
)

WORKING_TREE_NO_VCS = Frame(
    name="worktree",
    rule_words="os.walk from root; each non-directory entry, dotfiles "
               "included, VCS metadata directories pruned",
    filter_words="drops " + "/".join(sorted(_VCS_DIRS)) + " directories; no "
                 "ignore rules applied",
    selector=lambda root: _walk_all(root, drop_vcs=True),
)

TRACKED_ONLY = Frame(
    name="tracked",
    rule_words="git ls-files -- files in the index, and only those",
    filter_words="drops untracked files, including build output and case "
                 "archives that exist on disk; reaches tracked-but-gitignored "
                 "files that `grep -r` here does not",
    selector=_tracked,
)

IGNORE_HONOURING = Frame(
    name="ignore-honouring",
    rule_words="os.walk from root minus paths .gitignore excludes -- a model "
               "of what `grep -r` in this environment actually sweeps",
    filter_words="drops gitignored paths (git check-ignore --no-index) and "
                 "VCS metadata directories",
    selector=_ignore_honouring,
)

FRAMES: dict[str, Frame] = {
    f.name: f for f in (EVERYTHING_UNDER_ROOT, WORKING_TREE_NO_VCS,
                        TRACKED_ONLY, IGNORE_HONOURING)
}


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------

@dataclass
class Skips:
    """Files that were selected but not searched, broken out by reason.

    Lumping these into one "skipped" number is how a filter goes unstated, so
    each reason is counted and named separately. `unreadable` is the one that
    is a failure rather than a declared policy, and it is the one that drives
    the UNKNOWN verdict.
    """

    binary: int = 0
    over_size_cap: int = 0
    unreadable: int = 0
    not_a_regular_file: int = 0
    unreadable_paths: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (self.binary + self.over_size_cap + self.unreadable
                + self.not_a_regular_file)

    def words(self) -> str:
        return (f"{self.binary} binary, {self.over_size_cap} over size cap, "
                f"{self.unreadable} unreadable (raised), "
                f"{self.not_a_regular_file} not a regular file")


@dataclass(frozen=True)
class Hit:
    path: str
    lineno: int
    line: str


@dataclass
class SweepResult:
    """A sweep count that carries its own frame and refuses naked comparison.

    `verdict` is one of three:

      MATCHES  -- hits found, and the sweep read what it selected.
      ZERO     -- no hits, and the verdict line states what was skipped, so
                  the zero is a zero over a stated frame rather than a bare
                  clean bill.
      UNKNOWN  -- the sweep did not complete: a selected file raised on read,
                  or the walk itself failed. Hits found before that point are
                  still listed, and the verdict is still UNKNOWN, because a
                  partial sweep reporting a total is L-75's failure mode.

    Pinned by `test_unreadable_file_forces_unknown_not_zero` and
    `test_zero_verdict_states_its_skips_in_the_verdict_line`.
    """

    pattern: str
    frame: Frame
    root: str
    commit: str
    dirty: bool
    include_globs: tuple[str, ...]
    size_cap: int | None
    regex: bool
    ignore_case: bool
    considered: int
    searched: int
    skips: Skips
    hits: list[Hit]
    non_utf8_searched: int
    walk_error: str | None

    # -- verdict ----------------------------------------------------------
    @property
    def verdict(self) -> str:
        if self.walk_error is not None or self.skips.unreadable:
            return "UNKNOWN"
        if self.hits:
            return "MATCHES"
        return "ZERO"

    @property
    def complete(self) -> bool:
        """True when the sweep read each file its frame selected."""
        return self.searched == self.considered and self.walk_error is None

    @property
    def matched_files(self) -> int:
        return len({h.path for h in self.hits})

    @property
    def matched_lines(self) -> int:
        return len(self.hits)

    def require_complete(self) -> "SweepResult":
        """Return self, or raise if the verdict is UNKNOWN.

        For callers who would rather stop than publish a number the sweep
        could not stand behind.
        """
        if self.verdict == "UNKNOWN":
            raise SweepIncomplete(self.verdict_line())
        return self

    # -- frame ------------------------------------------------------------
    def frame_block(self) -> str:
        cap = "none" if self.size_cap is None else f"{self.size_cap} bytes"
        globs = ", ".join(self.include_globs) if self.include_globs else "all names"
        lines = [
            "FRAME",
            f"  root            : {self.root}",
            f"  commit          : {self.commit}{' +uncommitted changes' if self.dirty else ''}",
            f"  frame           : {self.frame.name}",
            f"  selection rule  : {self.frame.rule_words}",
            f"  filter applied  : {self.frame.filter_words}",
            f"  name filter     : {globs}",
            f"  pattern         : {self.pattern!r} "
            f"({'regex' if self.regex else 'fixed string'}"
            f"{', case-insensitive' if self.ignore_case else ''})",
            f"  size cap        : {cap}",
            f"  files considered: {self.considered}",
            f"  files searched  : {self.searched}",
            f"  files skipped   : {self.skips.total} ({self.skips.words()})",
        ]
        if self.non_utf8_searched:
            lines.append(f"  non-UTF-8 files : {self.non_utf8_searched} "
                         "(decoded latin-1 and searched, not skipped)")
        if self.walk_error is not None:
            lines.append(f"  walk error      : {self.walk_error}")
        if self.skips.unreadable_paths:
            shown = self.skips.unreadable_paths[:10]
            lines.append(f"  unreadable      : {', '.join(shown)}"
                         + (" ..." if len(self.skips.unreadable_paths) > 10 else ""))
        return "\n".join(lines)

    def verdict_line(self) -> str:
        base = (f"{self.verdict}: {self.matched_files} files / "
                f"{self.matched_lines} lines matched {self.pattern!r} "
                f"under frame '{self.frame.name}' at {self.commit}"
                f"{'+dirty' if self.dirty else ''}; "
                f"{self.searched} of {self.considered} files searched")
        if self.skips.total:
            base += f"; {self.skips.total} not searched ({self.skips.words()})"
        if self.verdict == "UNKNOWN":
            why = self.walk_error or (
                f"{self.skips.unreadable} selected file(s) raised on read")
            base += f"; UNKNOWN because {why}"
        return base

    def report(self, max_hits: int = 50) -> str:
        out = [self.frame_block(), "", self.verdict_line()]
        if self.hits:
            out.append("")
            for h in self.hits[:max_hits]:
                out.append(f"  {h.path}:{h.lineno}: {h.line[:200]}")
            if len(self.hits) > max_hits:
                out.append(f"  ... {len(self.hits) - max_hits} further hit lines")
        return "\n".join(out)

    # -- comparison, refused across frames ---------------------------------
    def _same_measurement(self, other: "SweepResult") -> bool:
        return (self.frame.name == other.frame.name
                and os.path.realpath(self.root) == os.path.realpath(other.root)
                and self.include_globs == other.include_globs
                and self.size_cap == other.size_cap)

    def compare_to(self, other: "SweepResult") -> int:
        """matched_files difference, or raise when the frames differ.

        Two counts taken under different frames are two measurements. L-75:
        an irreconcilable gap between such a pair was the frames, not a
        discrepancy. Pinned by
        `test_comparing_two_frames_raises_rather_than_answering`.
        """
        if not isinstance(other, SweepResult):
            raise TypeError("compare_to expects a SweepResult")
        if not self._same_measurement(other):
            raise FrameMismatch(
                "refusing to compare two different measurements: "
                f"'{self.frame.name}' over {self.root} "
                f"(globs={self.include_globs or 'all'}, cap={self.size_cap}) "
                f"vs '{other.frame.name}' over {other.root} "
                f"(globs={other.include_globs or 'all'}, cap={other.size_cap}). "
                "State both frames side by side instead of subtracting them.")
        return self.matched_files - other.matched_files

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SweepResult):
            return NotImplemented
        if not self._same_measurement(other):
            raise FrameMismatch(
                "refusing to equate results from different frames: "
                f"'{self.frame.name}' vs '{other.frame.name}'")
        return (self.pattern == other.pattern
                and self.matched_files == other.matched_files
                and self.matched_lines == other.matched_lines)

    __hash__ = None  # type: ignore[assignment]


# --------------------------------------------------------------------------
# The sweep
# --------------------------------------------------------------------------

def _head_commit(root: Path) -> tuple[str, bool]:
    proc = _git(root, "rev-parse", "--short", "HEAD")
    if proc.returncode != 0:
        return ("no-git", False)
    sha = proc.stdout.strip()
    status = _git(root, "status", "--porcelain")
    return (sha, bool(status.stdout.strip()))


def select_files(frame: Frame, root: str | os.PathLike = ".",
                 include: Sequence[str] | None = None) -> list[Path]:
    """The file list a frame selects, before anything is read."""
    rootp = Path(root).resolve()
    paths = list(frame.selector(rootp))
    if include:
        paths = [p for p in paths
                 if any(fnmatch.fnmatch(p.name, g) for g in include)]
    return paths


def sweep(pattern: str,
          root: str | os.PathLike = ".",
          frame: Frame | str | None = None,
          *,
          regex: bool = True,
          ignore_case: bool = False,
          include: Sequence[str] | None = None,
          size_cap: int | None = DEFAULT_SIZE_CAP,
          skip_binary: bool = True) -> SweepResult:
    """Search `pattern` under `root` within a named `frame`.

    `frame` is required: pass a `Frame` or one of the names in `FRAMES`.
    There is deliberately no default -- a default frame is a filter the caller
    did not choose and will not state, which is L-75 in one line.
    """
    if frame is None:
        raise TypeError(
            "sweep() requires an explicit frame. Choose one of: "
            + ", ".join(sorted(FRAMES)) + ". A sweep with an unstated frame "
            "is the defect this module exists for (L-75).")
    if isinstance(frame, str):
        if frame not in FRAMES:
            raise KeyError(f"unknown frame {frame!r}; have {sorted(FRAMES)}")
        frame = FRAMES[frame]

    rootp = Path(root).resolve()
    commit, dirty = _head_commit(rootp)
    flags = re.IGNORECASE if ignore_case else 0
    needle = re.compile(pattern if regex else re.escape(pattern), flags)

    skips = Skips()
    hits: list[Hit] = []
    considered = 0
    searched = 0
    non_utf8 = 0
    walk_error: str | None = None

    try:
        paths = select_files(frame, rootp, include)
    except Exception as exc:  # the walk itself failed -> UNKNOWN, not zero
        return SweepResult(
            pattern=pattern, frame=frame, root=str(rootp), commit=commit,
            dirty=dirty, include_globs=tuple(include or ()), size_cap=size_cap,
            regex=regex, ignore_case=ignore_case, considered=0, searched=0,
            skips=skips, hits=[], non_utf8_searched=0,
            walk_error=f"{type(exc).__name__}: {exc}")

    for path in paths:
        considered += 1
        try:
            st = os.lstat(path)
            if stat.S_ISLNK(st.st_mode):
                st = os.stat(path)  # resolve; dangling or looping symlink raises
            if not stat.S_ISREG(st.st_mode):
                skips.not_a_regular_file += 1
                continue
            if size_cap is not None and st.st_size > size_cap:
                skips.over_size_cap += 1
                continue
            raw = path.read_bytes()
        except (OSError, ValueError) as exc:
            skips.unreadable += 1
            skips.unreadable_paths.append(f"{path} ({type(exc).__name__})")
            continue

        if skip_binary and b"\x00" in raw[:8192]:
            skips.binary += 1
            continue

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            # L-76's crash: one non-UTF-8 byte took out an entire audit run.
            # Decoding latin-1 keeps the file searched instead of silently
            # dropped, and the count is stated in the frame either way.
            text = raw.decode("latin-1")
            non_utf8 += 1

        searched += 1
        try:
            rel = str(path.relative_to(rootp))
        except ValueError:  # pragma: no cover - path outside root
            rel = str(path)
        for lineno, line in enumerate(text.splitlines(), start=1):
            if needle.search(line):
                hits.append(Hit(rel, lineno, line.rstrip()))

    return SweepResult(
        pattern=pattern, frame=frame, root=str(rootp), commit=commit,
        dirty=dirty, include_globs=tuple(include or ()), size_cap=size_cap,
        regex=regex, ignore_case=ignore_case, considered=considered,
        searched=searched, skips=skips, hits=hits,
        non_utf8_searched=non_utf8, walk_error=walk_error)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sweep",
        description="Sweep a tree and print the frame the count was taken in.")
    p.add_argument("pattern", nargs="?", help="regex, or fixed string with -F")
    p.add_argument("--frame", choices=sorted(FRAMES),
                   help="required: which files to sweep")
    p.add_argument("--root", default=".")
    p.add_argument("-F", "--fixed", action="store_true",
                   help="treat the pattern as a literal string")
    p.add_argument("-i", "--ignore-case", action="store_true")
    p.add_argument("--include", action="append", default=None,
                   help="glob on the file NAME; repeatable")
    p.add_argument("--size-cap", type=int, default=DEFAULT_SIZE_CAP,
                   help="skip files larger than this; 0 disables the cap")
    p.add_argument("--search-binary", action="store_true",
                   help="do not skip files with NUL bytes")
    p.add_argument("--files-only", action="store_true",
                   help="print matching file names rather than hit lines")
    p.add_argument("--max-hits", type=int, default=50)
    p.add_argument("--list-frames", action="store_true")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.list_frames:
        for name, f in sorted(FRAMES.items()):
            print(f"{name}\n  selects: {f.rule_words}\n  filter : {f.filter_words}\n")
        return 0
    if not args.pattern or not args.frame:
        print("sweep: both a pattern and --frame are required "
              f"(frames: {', '.join(sorted(FRAMES))}). "
              "There is no default frame on purpose -- see L-75.",
              file=sys.stderr)
        return 2
    res = sweep(args.pattern, root=args.root, frame=args.frame,
                regex=not args.fixed, ignore_case=args.ignore_case,
                include=args.include,
                size_cap=None if args.size_cap == 0 else args.size_cap,
                skip_binary=not args.search_binary)
    if args.files_only:
        print(res.frame_block())
        print()
        print(res.verdict_line())
        print()
        for p in sorted({h.path for h in res.hits}):
            print(f"  {p}")
    else:
        print(res.report(max_hits=args.max_hits))
    return {"MATCHES": 0, "ZERO": 1, "UNKNOWN": 3}[res.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
