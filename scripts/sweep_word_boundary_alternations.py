#!/usr/bin/env python3
"""Find alternations wrapped in \\b(...)\\b that carry an alternative which can
never match, or which silently misses the longer word it plainly means to catch.

THE TRAP, IN ONE SENTENCE. A regex of the shape ``\\b(a|b|c)\\b`` applies its
trailing word boundary to EVERY alternative, so an alternative that is a strict
PREFIX of the word it means to catch matches only the bare prefix -- and if the
bare prefix is not a word anybody writes, that alternative matches nothing at
all, for ever, while looking perfectly reasonable in the source.

MEASURED, in this repository, 2026-09-01, in a sheet checker the author wrote
the same day:

    \\b(...|repositor|...)\\b     never matches "repository"
    \\b(60\\s*min|...)\\b          never matches "60 minutes"
    \\b(...|commit(?:ted)?|...)\\b never matches "commits"

The second is the one that matters. That rule exists to keep a sixty-minute
figure off a demo sheet after an explicit owner directive, and "60 minutes" is
the single most likely form of the violation. The rule could see "60 min" and
was blind to the phrase it was written for. **A dead alternative inside a
grading comparator is a gate that cannot fail**, which is why this sweep exists.

WHAT IT DOES, AND WHAT IT REFUSES TO DO. It reports. It edits nothing, and it
is deliberately incapable of editing anything: a comparator belongs to the team
that owns it, and a silent fix to somebody else's gate is exactly what this lab
forbids. Findings are handed to a supervisor for dispatch.

HOW A CANDIDATE IS JUDGED, with no semantic guessing. The corpus is the words
that actually occur in this repository's own tracked prose and source. For each
alternative's trailing literal T:

  DEAD   T never occurs as a standalone word anywhere in the corpus, and T is a
         strict prefix of at least one word that does. The alternative cannot
         match anything anybody in this repository writes.
  NARROW T does occur standalone, and is also a strict prefix of corpus words.
         The alternative works, and silently misses those longer forms. Whether
         that is a defect is the owning team's call, so it is reported
         separately and never mixed into the DEAD count.

    python3 scripts/sweep_word_boundary_alternations.py
    python3 scripts/sweep_word_boundary_alternations.py --selftest
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# THE CORPUS IS PROSE ONLY, AND THE FIRST VERSION OF THIS SCRIPT PROVED WHY.
# With ``*.py`` in the corpus the selftest reported 1/4: every planted dead
# alternative came back NARROW, because THE REGEX'S OWN SOURCE IS IN THE
# CORPUS. The token ``repositor`` occurs in this repository exactly once -- in
# the broken pattern itself -- and that single occurrence was enough to make
# the sweep call a dead alternative a live word. A corpus that contains the
# thing under test is not a corpus, in the same way that a control derived
# from the thing it controls is not a control. Prose is also the right
# question on its own terms: "is this a word anybody writes" is a question
# about writing, not about identifiers.
CORPUS_GLOBS = ("*.md", "*.tex")
#: Files searched for the pattern shape itself.
SOURCE_GLOBS = ("*.py",)

WORD = re.compile(r"[A-Za-z][A-Za-z0-9-]*")
#: The literal tail of an alternative: the trailing run of plain characters.
TAIL = re.compile(r"([A-Za-z][A-Za-z0-9-]*)$")

#: An alternative shorter than this is far too common a fragment to judge.
MIN_TAIL = 3


def _tracked(globs: tuple[str, ...]) -> list[Path]:
    out = subprocess.run(["git", "ls-files", "--", *globs], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return [REPO / line for line in out.stdout.splitlines() if line.strip()]


def build_corpus(paths: list[Path]) -> tuple[set[str], dict[str, str]]:
    """Every word this repository actually writes, lowercased.

    Returns the word set and a map from word to one file that contains it, so
    a finding can name where the word it cannot see actually occurs.
    """
    words: set[str] = set()
    where: dict[str, str] = {}
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(p.relative_to(REPO))
        for m in WORD.finditer(text):
            token = m.group(0).lower()
            # The hyphenated compound AND its parts both count as words people
            # write, because a regex sees "cannot-adjudicate" as the standalone
            # word "cannot" followed by a boundary. Recording only the compound
            # would make "cannot" look like a word nobody writes and land it in
            # the DEAD column, which is the opposite of the truth.
            for w in {token, *token.split("-")}:
                if w and w not in words:
                    words.add(w)
                    where[w] = rel
    return words, where


def _split_alternatives(body: str) -> list[str]:
    """Top-level ``|`` split, respecting nesting, classes and escapes."""
    parts: list[str] = []
    depth = 0
    in_class = False
    buf: list[str] = []
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            buf.append(body[i:i + 2])
            i += 2
            continue
        if in_class:
            if c == "]":
                in_class = False
        elif c == "[":
            in_class = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(c)
        i += 1
    parts.append("".join(buf))
    return parts


def find_groups(text: str) -> list[tuple[int, str]]:
    r"""Every ``\b(...)\b`` or ``\b(?:...)\b`` group, as (line number, body).

    The scan is over the RAW FILE TEXT rather than over parsed string literals,
    because these patterns are written across implicit string concatenation as
    often as not and a literal-aware parser would miss exactly the long ones.
    The trailing ``\b`` is required: without it the trap does not exist, and a
    group with no trailing boundary is not this sweep's business.
    """
    found: list[tuple[int, str]] = []
    for m in re.finditer(r"\\b\((\?:)?", text):
        start = m.end()
        depth = 1
        in_class = False
        i = start
        while i < len(text) and depth:
            c = text[i]
            if c == "\\":
                i += 2
                continue
            if in_class:
                if c == "]":
                    in_class = False
            elif c == "[":
                in_class = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            i += 1
        if depth:
            continue
        close = i
        if not text[close:close + 2] == "\\b":
            continue
        body = text[start:close - 1]
        if "|" not in body:
            continue
        found.append((text.count("\n", 0, m.start()) + 1, body))
    return found


def judge(body: str, words: set[str], where: dict[str, str]
          ) -> list[tuple[str, str, str, str]]:
    """Classify each alternative. Returns (verdict, alternative, tail, note)."""
    out: list[tuple[str, str, str, str]] = []
    for alt in _split_alternatives(body):
        alt = alt.strip()
        if not alt:
            continue
        m = TAIL.search(alt)
        if not m:
            continue                       # ends in a metacharacter: not this trap
        tail = m.group(1).lower()
        if len(tail) < MIN_TAIL:
            continue
        # THE NEXT CHARACTER MUST BE A WORD CHARACTER, and the first version of
        # this sweep forgot it and reported 458 misses that were not misses.
        # ``\b`` SUCCEEDS before a hyphen, so ``\bcannot\b`` matches perfectly
        # well inside "cannot-adjudicate" and that pair is no evidence of
        # anything. Only a letter or digit immediately after the prefix defeats
        # the boundary, which is the entire mechanic being hunted here.
        longer = sorted(w for w in words
                        if w.startswith(tail) and len(w) > len(tail)
                        and w[len(tail)].isalnum())
        if not longer:
            continue                       # nothing longer exists: nothing missed
        example = longer[0]
        note = f"cannot see {example!r} (occurs in {where.get(example, '?')})"
        if tail in words:
            out.append(("NARROW", alt, tail, note))
        else:
            out.append(("DEAD", alt, tail, note))
    return out


# ------------------------------------------------------------------ selftest
#: Planted patterns. Each states what the sweep MUST say about it. A sweep that
#: has never been shown to fire, and never been shown to stay quiet on a clean
#: pattern, is not evidence either way (CLAUDE.md rule 3).
PLANTS: list[tuple[str, str, str]] = [
    (r'X = re.compile(r"\b(version control|repositor|blob)\b")',
     "repositor", "DEAD"),
    (r'X = re.compile(r"\b(60\s*min|one hour)\b")',
     "min", "DEAD"),
    (r'X = re.compile(r"\b(converged|optimum)\b")',
     "converged", "SILENT"),
]


#: THE SELFTEST RUNS ON ITS OWN MINIATURE CORPUS, NOT THE REPOSITORY'S.
#: A control whose expected answers depend on what happens to be written in
#: the tree today is not a control; it is a second measurement. These four
#: words fix every plant's verdict by construction, so the arms mean the same
#: thing on any checkout, on any day.
PLANT_CORPUS = {"repository", "minutes", "converged", "blob"}


def selftest(_words: set[str], _where: dict[str, str]) -> int:
    print("SELFTEST: planted patterns on a fixed corpus, each with what the "
          "sweep must say")
    words, where = PLANT_CORPUS, {w: "<plant corpus>" for w in PLANT_CORPUS}
    bad = 0
    for src, target, expect in PLANTS:
        verdicts = {a: v for grp in find_groups(src)
                    for v, a, t, _n in judge(grp[1], words, where)
                    for a in [t]}
        got = verdicts.get(target, "SILENT")
        ok = got == expect
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'RED '}{target!r}: expected {expect}, got {got}")
    # A pattern with NO trailing \b carries no trap and must be ignored.
    no_boundary = r'X = re.compile(r"\b(repositor|blob)")'
    if find_groups(no_boundary):
        print("  RED  a group without a trailing boundary was picked up")
        bad += 1
    else:
        print("  ok  a group without a trailing boundary is ignored")
    print(f"SELFTEST: {4 - bad}/4 arms behaved")
    return 2 if bad else 0


def main(argv: list[str]) -> int:
    t0 = time.time()
    corpus_paths = _tracked(CORPUS_GLOBS)
    words, where = build_corpus(corpus_paths)
    print(f"CORPUS: {len(words):,} distinct words from "
          f"{len(corpus_paths):,} tracked files")

    if "--selftest" in argv:
        rc = selftest(words, where)
        print(f"\nCOST: {time.time() - t0:.1f} s wall, 1 rank")
        return rc

    if selftest(words, where):
        print("REFUSE: the sweep cannot see its own planted defect")
        return 2
    print()

    dead: list[str] = []
    narrow_by_file: dict[str, int] = defaultdict(int)
    scanned = 0
    for p in _tracked(SOURCE_GLOBS):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "\\b(" not in text:
            continue
        scanned += 1
        rel = str(p.relative_to(REPO))
        for line, body in find_groups(text):
            for verdict, alt, tail, note in judge(body, words, where):
                if verdict == "DEAD":
                    dead.append(f"{rel}:{line}  alternative {alt!r}  {note}")
                else:
                    narrow_by_file[rel] += 1

    print(f"SCANNED: {scanned} tracked files carrying the pattern shape")
    print(f"\nDEAD ALTERNATIVES ({len(dead)}) "
          f"-- these can never match anything written here:")
    for row in dead:
        print(f"  {row}")
    if not dead:
        print("  none")
    print(f"\nNARROW ALTERNATIVES, by file "
          f"({sum(narrow_by_file.values())} across {len(narrow_by_file)} files)"
          f" -- they match, and miss longer forms; the owning team's call:")
    for rel, n in sorted(narrow_by_file.items(), key=lambda kv: -kv[1])[:20]:
        print(f"  {n:4d}  {rel}")
    print(f"\nCOST: {time.time() - t0:.1f} s wall, 1 rank")
    print("REPORT ONLY. Nothing was edited and this script cannot edit.")
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
