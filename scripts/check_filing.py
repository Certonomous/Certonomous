#!/usr/bin/env python3
"""Enforce this lab's filing and naming convention, so it never drifts again.

Written 2026-08-18 on Sanaa's instruction, after a multi-day reorganisation that
collapsed a 4,924-file webroot and rehomed ~8,000 files. Her words: "make sure to
respect our organization and naming convention now so that our folders and later
our repos are always clean and organized and we dont have to go through the deep
cleaning and reorganization again."

The reason this is a SCRIPT and not a page in a charter: the convention was
already implicit and already near-universal (51 of 51 `docs/*.md` in UPPER_SNAKE,
70 of 72 `scripts/` entries in lower_snake) and it drifted anyway, because
nothing measured it. A convention nobody can fail is a preference. The charter at
`docs/charters/FILING_CHARTER.md` states the rules for a human; this file is what
makes them binding.

Every rule carries a planted control exercised by `--selftest`. A rule that has
never caught a planted violation is not known to work -- this lab has shipped
three false zeros from checks whose populations were empty, so an all-clear here
means nothing unless the controls fire.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Files permitted to sit directly at the repository root. Everything else at the
# root is a violation -- that is the class Sanaa named first ("i dont want random
# pngs everywhere random scripts etc").
ROOT_ALLOW = {"README.md", ".gitignore", ".gitattributes"}

# scripts/ is lower_snake. `auto-stop.sh` is a DELIBERATE exception and not an
# oversight: it is installed to /usr/local/bin/auto-stop.sh and the registry
# compares the two by md5, so the tracked name must match the installed name.
# Renaming it to lower_snake would break that identity check.
SCRIPTS_EXEMPT = {"auto-stop.sh", "auto-stop.sh.proposed"}

UPPER_SNAKE_MD = re.compile(r"^[A-Z0-9][A-Z0-9_-]*\.md$")
# Campaign records are <RUNG>_<PURPOSE>.md, and a rung identifier carries
# lowercase: K0c, K0cT, K2a, K2b, K2e, KV1. Writing this rule as plain
# UPPER_SNAKE flagged `K0c_RESULTS.md` -- the single most canonical filename in
# the campaign -- as a violation. The negative control caught it before the rule
# ever ran on the tree, which is the whole reason the negative controls exist.
CAMPAIGN_RECORD_MD = re.compile(r"^[A-Z][A-Za-z0-9]*(_[A-Z0-9][A-Z0-9_-]*)?\.md$")
LOWER_SNAKE_CODE = re.compile(r"^[a-z0-9][a-z0-9_]*\.(py|sh)$")
# A paper carries its YEAR somewhere in the basename -- that is what makes two
# papers by the same group distinguishable at a glance -- plus lowercase ASCII.
#
# The year is deliberately NOT required to be its own underscore-delimited field.
# The first draft demanded `author_YEAR_rest` and flagged 49 correctly-named
# files, because this library's established habit is to fuse the year into a
# VENUE token: `breuer_..._caf2009_periodic_hills`, `pinelli_..._jfm2010_...`,
# `he_..._aiaaj2020_dafoam_...`, `greenblatt_et_al_cfdval2004_hump`. Those names
# are better than the rule was: they carry venue and year in one token.
#
# A check with a 49-file false-positive rate is a check people learn to scroll
# past, which is worse than no check at all -- so the rule was widened to what
# the convention actually is, not narrowed to what I first assumed.
#
# arXiv identifiers are accepted as year-carrying. `1710.09105`, `2402.16355`,
# `2603.28884` encode YYMM, so the year is present and the identifier is the
# CANONICAL name for the work -- more identifying than a bare year, not less.
# Demanding a redundant `_2017_` beside `1710.09105` would degrade those names.
PAPER_NAME = re.compile(
    r"^[a-z0-9][a-z0-9_.-]*("
    r"(1[89]|20)\d{2}"          # a plain or venue-fused year: 2003, caf2009, aiaaj2020
    r"|\d{4}\.\d{4,5}"          # an arXiv identifier: 1710.09105, 2603.28884
    r")[a-z0-9_.-]*\.(pdf|txt)$")


BAD_CHARS = re.compile(r"[^A-Za-z0-9._/-]")


class Violation:
    def __init__(self, rule: str, path: str, why: str) -> None:
        self.rule, self.path, self.why = rule, path, why

    def __str__(self) -> str:
        return f"  [{self.rule}] {self.path}\n      {self.why}"


def _tracked(root: Path) -> list[str]:
    """Paths in HEAD. HEAD is the referent, never the index.

    Files landed by the private-index commit protocol have no shared-index entry,
    so `git ls-files` and `git diff --cached` misreport them. This lab has been
    bitten by that repeatedly; ask the commit graph, not the staging area.
    """
    # `core.quotePath=false` is load-bearing, not tidiness. By default git
    # returns a non-ASCII path ESCAPED and in quotes --
    # "docs/papers/eca_hoekstra_2014_uncert\303\247.pdf" -- so the very rule
    # that exists to catch non-ASCII names never sees a non-ASCII character, and
    # the path it reports is not a path anyone can open. The planted control for
    # R0 missed for exactly this reason before the flag was added.
    out = subprocess.run(
        ["git", "-c", "core.quotePath=false", "ls-tree", "-r", "HEAD", "--name-only"],
        cwd=root, capture_output=True, text=True,
    )
    if out.returncode != 0:
        return []
    return [line for line in out.stdout.splitlines() if line]


def _loose_root_files(root: Path) -> list[str]:
    """Every FILE sitting directly at the repository root, read from the disk.

    This deliberately does NOT ask git, and both reasons were observed on
    2026-08-18 within one minute of each other:

    1. **git status is blind to ignored files by design.** All twelve genuinely
       loose files at this root -- `badFaces`, ten `mbc_retry*.log/err`, two
       `.whl` wheels -- are matched by .gitignore, so a `?? `-based scan found
       NONE of them. But "gitignored" is not "filed": .gitignore hides a file
       from git while leaving it exactly as visible to a human opening the
       folder, which is the thing Sanaa actually objected to. **A cleanliness
       rule that inherits git's visibility model measures the wrong thing.**

    2. **git status reads stale under concurrency.** With three agents
       committing, `git status` still named `uq_batch.log` and `uq_batch.err`
       as untracked root entries after both had been moved away -- a check
       reporting two files that did not exist while missing twelve that did.

    The filesystem is the ground truth for "is there a loose file at the root",
    so the filesystem is what gets asked.
    """
    try:
        return sorted(e.name for e in root.iterdir() if e.is_file())
    except OSError:
        return []


def check(root: Path, include_untracked: bool = True) -> list[Violation]:
    paths = _tracked(root)
    violations: list[Violation] = []

    # R1 -- nothing loose at the repository root.
    root_files = [p for p in paths if "/" not in p]
    if include_untracked:
        root_files += _loose_root_files(root)
    for name in sorted(set(root_files)):
        if name in ROOT_ALLOW:
            continue
        target = root / name
        if target.is_dir():
            continue
        violations.append(Violation(
            "R1-ROOT-CLEAN", name,
            "sits at the repository root; only README.md, .gitignore and "
            ".gitattributes belong there. Move it under the directory that owns "
            "its theme. Being matched by .gitignore does NOT excuse it -- "
            "ignored means invisible to git, not filed.",
        ))

    for p in paths:
        parts = p.split("/")
        base = parts[-1]

        # R0 -- no spaces, no non-ASCII, anywhere. A space in a path breaks every
        # unquoted shell loop in this lab, and a non-ASCII character makes a file
        # unfindable by anyone typing its name from a printed page.
        bad = sorted(set(BAD_CHARS.findall(p)))
        if bad:
            violations.append(Violation(
                "R0-PORTABLE-NAME", p,
                f"contains {bad!r}; paths are ASCII letters, digits, dot, "
                f"underscore and hyphen only.",
            ))

        # R2 -- docs/*.md is UPPER_SNAKE.
        if len(parts) == 2 and parts[0] == "docs" and base.endswith(".md"):
            if not UPPER_SNAKE_MD.match(base):
                violations.append(Violation(
                    "R2-DOCS-UPPER", p,
                    "documents directly in docs/ are UPPER_SNAKE_CASE.md "
                    "(51 of 51 at the time this rule was written).",
                ))

        # R3 -- scripts/ is lower_snake code.
        if len(parts) == 2 and parts[0] == "scripts" and base not in SCRIPTS_EXEMPT:
            if base.endswith((".py", ".sh")) and not LOWER_SNAKE_CODE.match(base):
                violations.append(Violation(
                    "R3-SCRIPTS-LOWER", p,
                    "executables in scripts/ are lower_snake.py or lower_snake.sh.",
                ))

        # R5 -- media/ and research/ are subdivided; no loose assets.
        if len(parts) == 2 and parts[0] in {"media", "research"}:
            violations.append(Violation(
                "R5-ASSET-SUBDIR", p,
                f"assets live in a themed subdirectory of {parts[0]}/, never "
                f"loose in it (media/plots/, media/acts/, research/closure/ ...).",
            ))

        # R6 -- solver cases belong in a run tree, not in docs/.
        #
        # `models/` is a THIRD legitimate home and is not a violation: it holds
        # reference case DEFINITIONS (the NASA Turbulence Modeling Resource
        # geometries and their mesh families), which are inputs to runs rather
        # than outputs of them. The first draft of this rule flagged all 14 of
        # them; `models/tmr` is referenced by path in five code files, so
        # "fixing" the report by moving the cases would have broken working code
        # to satisfy a rule I had just written. The rule was wrong, not the tree.
        if base == "controlDict" and "system" in parts:
            if not (p.startswith("verification/runs/") or p.startswith("cases/")
                    or p.startswith("models/")):
                violations.append(Violation(
                    "R6-RUNTREE", p,
                    "an OpenFOAM case belongs under verification/runs/<CAMPAIGN>/ "
                    "or cases/, never beside the prose that describes it.",
                ))

        # R6b -- QUEUE-RUNNER ARTIFACTS ARE RUN OUTPUTS AND BELONG UNDER
        # verification/runs/<CAMPAIGN>/, never in a case's INPUT directory.
        # R6-RUNTREE above fires only on `system/controlDict` and whitelists
        # `cases/`, so it is structurally blind to run OUTPUTS committed into a
        # case dir. Measured 2026-08-28: 4 tracked at HEAD under `cases/`
        # against 119 correctly filed under `verification/runs/`.
        #
        # THE DISCRIMINATOR IS THE `.md` SUFFIX AND IT IS LOAD-BEARING.
        # `cases/ansys_verification/VMFL023/STATUS.md` is a PROSE interim-status
        # record -- a legitimate case document -- while `STATUS.W3_chain` and
        # `STATUS.F17c_KV40_FLOOR` are runner artifacts in the runner's own
        # `launcher_rc=... end=... note=...` format. A rule keyed on the
        # `STATUS.` prefix ALONE would flag the prose and be wrong about the
        # tree, which is the exact error this file's R6 comment records making
        # once already with `models/`. Both cases are planted below, and the
        # NEGATIVE limb is the one that matters.
        if p.startswith("cases/"):
            if base in RUNNER_ARTIFACTS or (
                    base.startswith("STATUS.") and not base.endswith(".md")):
                violations.append(Violation(
                    "R6-RUNARTIFACT", p,
                    "a queue-runner artifact is a RUN OUTPUT and belongs under "
                    "verification/runs/<CAMPAIGN>/, not in the case's input "
                    "directory (FILING_CHARTER; CLAUDE.md WHERE THINGS LIVE; "
                    "Sanaa 2026-08-27: logs and attempt dirs stay out of git).",
                ))

        # R7 -- campaign records are UPPER_SNAKE; campaign helper code is lower_snake.
        if len(parts) == 4 and parts[0] == "docs" and parts[1] == "campaigns":
            if base.endswith(".md") and base != "README.md" and not CAMPAIGN_RECORD_MD.match(base):
                violations.append(Violation(
                    "R7-CAMPAIGN-RECORD", p,
                    "campaign records are <RUNG>_<PURPOSE>.md in UPPER_SNAKE "
                    "(K0c_RESULTS.md, K2a_RACK_ROW_MODULE_SPEC.md).",
                ))
            if base.endswith((".py", ".sh")) and not LOWER_SNAKE_CODE.match(base):
                violations.append(Violation(
                    "R7-CAMPAIGN-RECORD", p,
                    "helper code inside a campaign directory is lower_snake.py.",
                ))

        # R8 -- papers are author_year_identifier, filed by topic.
        #
        # `unsorted/` is exempt BY DESIGN. It is the staging area for files whose
        # identity has not been established, and a compliant name cannot be
        # written for a work nobody has identified yet -- demanding one would
        # only produce a confident wrong name. The cost of the exemption is that
        # `unsorted/` must stay small; that is a matter for review, not for this
        # rule.
        if (len(parts) >= 2 and parts[0] == "docs" and parts[1] == "papers"
                and "unsorted" not in parts):
            if base.endswith((".pdf", ".txt")) and not PAPER_NAME.match(base):
                violations.append(Violation(
                    "R8-PAPER-NAME", p,
                    "papers are author_year_identifier.pdf with a matching .txt "
                    "sidecar; the year is what distinguishes two papers by the "
                    "same group.",
                ))

            # R9. THE SIDECAR HALF OF R8 WAS PROSE ONLY, AND THE PROSE WAS RIGHT.
            #
            # FILING_CHARTER R8 says "a PDF and its .txt sidecar always travel
            # together", and this rule tested only that the NAME was well formed.
            # Thirteen in-scope PDFs had no sidecar at all and the check reported
            # ZERO -- including spalart_allmaras_1992_turbulence_model.pdf.
            #
            # That is not a hypothetical cost. A lane writing the thermal-closure
            # synthesis swept the sidecars for prior art on relaminarisation and
            # MISSED ALL THREE AERODYNAMIC STATEMENTS OF IT, one of which is in
            # that very paper, because the sidecar it swept did not exist. The
            # sweep returned a clean zero and the zero meant nothing.
            #
            # The sidecar is not decoration: it is how an agent greps a corpus
            # without re-parsing PDFs, so a missing one silently shrinks the
            # searchable library while leaving the shelf looking full.
            if base.endswith(".pdf"):
                sidecar = (root / p).with_suffix(".txt")
                if not sidecar.exists():
                    violations.append(Violation(
                        "R9-SIDECAR-MISSING", p,
                        "has no .txt sidecar, so its contents are invisible to "
                        "every text sweep of this library. Generate it with "
                        "`pdftotext <file.pdf> <file.txt>`.",
                    ))

    return violations


# --------------------------------------------------------------------------
# Planted controls. Each rule gets a violation shaped exactly like the one it
# exists to catch, plus -- for the two rules most likely to over-fire -- a
# NEGATIVE control that must NOT be caught. A check that catches everything is
# as useless as one that catches nothing, and only the negative control tells
# the two apart.
# --------------------------------------------------------------------------
#: Exact basenames the queue runner writes beside a run. Names, not shapes:
#: these three are unambiguous, while `STATUS.*` needs the `.md` carve-out.
RUNNER_ARTIFACTS = {"launcher.queue.out", "CAP_OVERRUN.txt", "ESTIMATE_OVERRUN.txt"}

PLANTED = [
    ("R1-ROOT-CLEAN",      "stray_plot.png",                                    True),
    ("R1-ROOT-CLEAN",      "build_debris.log",                                  True),
    ("R2-DOCS-UPPER",      "docs/some_lowercase_note.md",                       True),
    ("R3-SCRIPTS-LOWER",   "scripts/BadlyNamed.py",                             True),
    ("R5-ASSET-SUBDIR",    "media/loose_figure.png",                            True),
    ("R6-RUNTREE",         "docs/campaigns/X/case/system/controlDict",          True),
    ("R6-RUNARTIFACT",     "cases/X/STATUS.X_CASE",                             True),
    ("R6-RUNARTIFACT",     "cases/X/launcher.queue.out",                        True),
    ("R6-RUNARTIFACT",     "cases/X/CAP_OVERRUN.txt",                           True),
    # THE DISCRIMINATING NEGATIVES. Without these the rule is a prefix match
    # that would flag a legitimate prose record and a correctly filed run.
    ("R6-RUNARTIFACT",     "cases/X/STATUS.md",                                 False),
    ("R6-RUNARTIFACT",     "verification/runs/CAMP/L1/STATUS.X_CASE",           False),
    ("R6-RUNARTIFACT",     "verification/runs/CAMP/L1/launcher.queue.out",      False),
    ("R7-CAMPAIGN-RECORD", "docs/campaigns/X/lowercase_results.md",             True),
    ("R8-PAPER-NAME",      "docs/papers/buoyancy/Paper1.pdf",                   True),
    ("R0-PORTABLE-NAME",   "docs/papers/buoyancy/van gilder_2005_ipack.pdf",     True),
    ("R0-PORTABLE-NAME",   "docs/papers/buoyancy/eca_hoekstra_2014_uncert\u00e7.pdf", True),
    # negatives -- correct filings that must survive
    (None,                 "docs/VERIFICATION_CHARTER.md",                      False),
    (None,                 "scripts/check_filing.py",                           False),
    (None,                 "docs/campaigns/X/K0c_RESULTS.md",                   False),
    (None,                 "docs/campaigns/X/K0cT_RESULTS.md",                  False),
    (None,                 "docs/campaigns/X/K2b_3D_UNSTEADINESS_PREREGISTRATION.md", False),
    (None,                 "docs/campaigns/X/digitize_wibron2018.py",           False),
    (None,                 "docs/papers/buoyancy/betts_bokhari_2000_ijhff.pdf", False),
    (None,                 "docs/papers/buoyancy/betts_bokhari_2000_ijhff.txt", False),
    (None,                 "docs/papers/bench/breuer_peller_caf2009_hills.pdf",  False),
    (None,                 "docs/papers/bench/breuer_peller_caf2009_hills.txt",  False),
    (None,                 "docs/papers/adj/he_mader_aiaaj2020_dafoam.txt",      False),
    ("R8-PAPER-NAME",      "docs/papers/bench/no_year_in_this_name.pdf",         True),
    ("R9-SIDECAR-MISSING", "docs/papers/bench/lonely_paper_2011_x.pdf",          True),
    (None,                 "docs/papers/rans/singh_medida_1608.03990.pdf",       False),
    (None,                 "docs/papers/rans/singh_medida_1608.03990.txt",       False),
    (None,                 "docs/papers/unsorted/UnidentifiedScan.pdf",          False),
    (None,                 "media/plots/figure.png",                            False),
    (None,                 "verification/runs/F14/case/system/controlDict",     False),
    (None,                 "README.md",                                         False),
]


def selftest() -> int:
    """Plant every shape in a scratch repository and assert each is caught.

    Populations are printed. An empty population is reported as a failure and
    never as a pass -- a check that ran over nothing has not passed, it has not
    run, and this lab has been misled by exactly that three times.
    """
    ok = True
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "selftest@local"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "selftest"], cwd=root, check=True)
        for _rule, rel, _should in PLANTED:
            f = root / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("planted\n")
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)  # scratch repo only
        subprocess.run(["git", "commit", "-qm", "planted"], cwd=root, check=True)

        found = check(root, include_untracked=False)
        by_path: dict[str, set[str]] = {}
        for v in found:
            by_path.setdefault(v.path, set()).add(v.rule)

        print(f"planted {len(PLANTED)} shapes into a scratch tree; "
              f"the check returned {len(found)} violations")
        if not found:
            print("FAIL: the check found nothing at all, which means it did not run")
            return 1

        for rule, rel, should_catch in PLANTED:
            caught = by_path.get(rel, set())
            if should_catch:
                if rule in caught:
                    print(f"  caught   {rule:<20} {rel}")
                else:
                    print(f"  MISSED   {rule:<20} {rel}   (got {caught or 'nothing'})")
                    ok = False
            else:
                if caught:
                    print(f"  FALSE +  {'':<20} {rel}   (flagged {caught})")
                    ok = False
                else:
                    print(f"  ignored  {'(negative)':<20} {rel}")

    positives = sum(1 for _r, _p, s in PLANTED if s)
    negatives = len(PLANTED) - positives
    print()
    print(f"control: {positives} planted violations, {negatives} correct filings that "
          f"must survive; {'every one behaved' if ok else 'SOME DID NOT BEHAVE'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default="/home/ubuntu/Certonomous")
    ap.add_argument("--selftest", action="store_true",
                    help="plant every violation shape and assert each is caught")
    ap.add_argument("--tracked-only", action="store_true",
                    help="ignore untracked root files (they are not yet in HEAD)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    violations = check(Path(args.root), include_untracked=not args.tracked_only)
    if not violations:
        print("PASS: every tracked path follows the filing convention.")
        return 0

    by_rule: dict[str, list[Violation]] = {}
    for v in violations:
        by_rule.setdefault(v.rule, []).append(v)
    for rule in sorted(by_rule):
        print(f"\n{rule}  ({len(by_rule[rule])})")
        for v in by_rule[rule]:
            print(str(v))
    print(f"\nFAIL: {len(violations)} filing violations across {len(by_rule)} rules.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
