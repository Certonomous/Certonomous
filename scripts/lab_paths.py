"""One place where this repository's tree layout is named, and one only.

WHY THIS MODULE EXISTS
======================
`demo-output/website/campaign/MOVE_MAP_2026-08-16.md` moves 13,084 tracked
files onto the owner's target tree.  Its section 4 census found ~150 files
carrying a path constant with a single mechanical successor, and 13 carrying a
constant with NO single successor -- `scripts/self_audit.py:105`'s
`WEB = REPO/"demo-output"/"website"` being the worst, because `WEB.rglob("*.md")`
at `:4319` and `:4837` reaches markdown that the map scatters across eight
different roots.

The same census found that the prefix was ALREADY being re-spelled rather than
factored: 8 times in one `sdk/tests/` rank-surface module, 4 in
`model_form_batch.py`, 3 verbatim in `mega_batch_keeper.sh`, twice identically
in `sdk/openfoam/qcr/{analyze,battery}.py`.  A move that repairs 13 constants
and leaves the re-spelling in place buys the next reorganisation the same bill.
So: one module, imported, never re-spelled.

THE PROPERTY THAT MAKES A BATCHED MOVE POSSIBLE
===============================================
Every name below is bound to a PAIR -- the legacy path and its successor under
the map -- and resolved against the filesystem at import.  The module is
therefore correct BEFORE the move, DURING it (MOVE_MAP section 9 lands batches
4-8 one region at a time), and AFTER it, with no flag day and no edit to this
file between batches.  That is what lets batch 3 land "behaviour-identical, no
path changes yet" and still be the thing batches 4-8 flip.

Resolution order, per name:

  1. the successor, if it exists on disk   -> the region has moved
  2. the legacy path, if it exists         -> the region has not moved yet
  3. neither                               -> the legacy path is returned AND
                                              the name is recorded in
                                              `UNRESOLVED`

IT DOES NOT FAIL OPEN, AND THAT IS THE POINT
============================================
Case 3 is the failure this repository has already been bitten by.
`scripts/check_absolutes.py`'s `audit(paths=)` filtered on suffix before
stat-ing, so a caller-named path that did not exist returned **PASS** -- a
checker that read nothing reporting clean.  Verified by executing the
pre-repair module: three of four nonexistent paths returned CLEAN/exit 0, the
outcome turning on the filename's suffix.  Repaired and pinned at `b0ab070d`;
a missing named path now returns UNKNOWN/exit 3.  After the move, every caller
naming a moved path would have hit exactly that.

So this module never quietly substitutes a path that is not there.  A name that
resolves to nothing lands in `UNRESOLVED`, `resolved()` reports it, and
`require()` raises.  A consumer that wants the repository's own three-valued
contract (0 PASS / 1 FAIL / 3 UNKNOWN) calls `unknown_reason()` and returns
UNKNOWN rather than PASS.  The rule is the one `b0ab070d` pinned: **a root that
is not there blinds the check; it never passes it.**
Evidence: `test_require_raises_rather_than_returning_a_path_that_is_not_there`,
`test_unknown_reason_names_the_missing_roots`,
`test_resolve_returns_none_for_something_that_never_existed`, and the
must-not-match control `test_the_must_not_match_control`, without which a shim
that answered UNKNOWN to everything would satisfy all three.

WHAT THIS MODULE DECIDES THAT THE MAP LEFT OPEN
===============================================
`MOVE_MAP` section 2.2's R23 says four `closure_*` source directories become
`research/closure`, without saying whether each keeps its own segment.  R21
DOES preserve its segment (`campaign/` survives inside `verification/`), and
section 6 gives the reason: a preserved segment keeps every relative citation
in 45 ladder records alive.  This module applies that reasoning uniformly and
PRESERVES the child segment on every many-to-one merge.  That is a decision,
not a measurement -- it is made in exactly one place, `_MOVES` below, and the
batch that lands R23 must ratify it before it runs.

Three trees below are named by a rule or a constant but hold NO tracked file,
so `git mv` will not move them: see `DARK_TREES` and `scripts/hand_carry.py`.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

__all__ = [
    "REPO", "MOVES", "RULES", "UNRESOLVED", "AMBIGUOUS", "NEVER_MOVE",
    "redirect", "unredirect", "resolve", "require", "resolved",
    "unknown_reason", "state", "run_archive", "web_file",
    "RECORD_ROOTS", "RECORD_ROOT_NAMES", "SWEEP_ROOTS", "BUNDLE_PAGES",
    "SUBMISSION_PACKAGES", "SERVED_SET", "DARK_TREES",
]

REPO = Path(os.environ.get("LAB_REPO") or Path(__file__).resolve().parents[1])

_W = "demo-output/website"


# ---------------------------------------------------------------------------
# Rules that are NOT prefix substitutions.  Checked before the table, because
# a prefix table cannot express "everything under campaign/ EXCEPT the run
# archives", and a table that silently gets it wrong routes 7,940 files to the
# wrong root while looking correct.
# ---------------------------------------------------------------------------

#: X3.  Never touched by this map -- `latex/` is its owner's, `motorbike-video/`
#: is filming.  Listed before everything because `WEB`'s prefix would otherwise
#: sweep them into `web/`.
NEVER_MOVE: tuple[str, ...] = (
    _W + "/latex",
    _W + "/motorbike-video",
)

#: R13's fifth served file.  It sits under `campaign/` and so must be answered
#: before the R20/R21 campaign split.
_SERVED_PNG = _W + "/campaign/duct_secondary_flow_AR_7_validation_qcr.png"

#: R20 vs R21.  Both live under `demo-output/website/campaign/`; the split is
#: on the FIRST segment below it, not on a prefix.
_RUN_ARCHIVE = re.compile(r"^[^/]+_(runs|work)$")

#: R12.  Ten loose PNGs at `demo-output/*.png` -> `media/`.  A glob, not a
#: prefix: `demo-output/plots/` is R11 and `demo-output/acts/` is R10.
_LOOSE_PNG = re.compile(r"^demo-output/[^/]+\.png$")

#: **R25, RULING 1 of 2026-08-17** (`campaign/MOVE_MAP_BATCH0_RULINGS_2026-08-17.md`
#: s1.2).  A run tree is classified by WHAT IT IS, not by where it sits:
#: `docs/campaigns/<campaign>/<tree>/**` where `<tree>` matches `*_runs` or
#: `*_sensitivity` is a run archive and follows R20's destination, not R7's
#: "`docs/**` unchanged".  315 tracked files -- `K0c_runs` 274,
#: `K0b_mesh_sensitivity` 41 -- confirmed unchanged at `4d7c195a`, `7554e5d3`
#: and again at `267a4021` over `git ls-tree -r HEAD`.
#:
#: THE CAMPAIGN SEGMENT IS PRESERVED, and that is the sub-decision the ruling
#: flagged as the owner's: `verification/runs/` is a flat namespace holding 27
#: distinct `*_runs`/`*_work` names already, `docs/campaigns/` is a
#: PER-CAMPAIGN directory, and two campaigns each landing a `K0c_runs` would
#: collide the moment the second one arrives.  If the owner prefers the flat
#: form it is one line here and no count moves.
#:
#: Binding this rule was measured before it was made, at `267a4021` over one
#: `git ls-tree -r HEAD` snapshot handed to both runs of `hand_carry.derive`:
#: **617 dark trees / 5,447 files / 835,459,647 gitignored bytes move from
#: STAYS PUT to RIDES ALONG, and the hand-carry set does not move at all** --
#: 2 trees / 307 files / 1,510,309,145 bytes, byte-identical either way.  Those
#: 617 ride along ONLY if batch 7's `git mv` names the DIRECTORY.
_R25 = re.compile(r"^docs/campaigns/([^/]+)/([^/]+_(?:runs|sensitivity))(/.*)?$")
_R25_BACK = re.compile(
    r"^verification/runs/([^/]+)/([^/]+_(?:runs|sensitivity))(/.*)?$")

#: **R16 / R17** -- loose files sitting directly in the webroot.  19 `*.md` to
#: `research/closure/md/` and 21 `*.json` to `research/closure/data/`.
#:
#: THIS WAS MEASURED MISSING, 2026-08-17.  The table below implements R1-R15
#: and R18-R25 and had no row for these two rules, so all 40 fell through to
#: the `WEB` catch-all and were routed to `web/` -- which contradicts R13's
#: own "the webroot is FIVE files" and would have sent every
#: `closure_challenge_*.json` generator's output to the wrong root under batch
#: 3b.  They cannot be table rows: the rule is "a loose file of this suffix",
#: not a directory prefix.  `benchmarks.json` (R14), `benchmarks.png` (R15) and
#: `wall/wall.json` (R18) have explicit rows and keep them -- see
#: `_EXPLICIT_LEGACY` -- and a loose file of any other suffix still falls to
#: the webroot, which is what R13 means.
_LOOSE_WEB = re.compile(r"^" + re.escape(_W) + r"/([^/]+\.(?:md|json))$")
_LOOSE_WEB_BACK = re.compile(r"^research/closure/(?:md|data)/([^/]+\.(?:md|json))$")


def _special(rel: str) -> str | None | bool:
    """Non-prefix rules.  Returns a successor, None (no rule), or False
    (an explicit never-move, which must not fall through to the table)."""
    for nm in NEVER_MOVE:
        if rel == nm or rel.startswith(nm + "/"):
            return False
    if rel == _SERVED_PNG:
        return "web/campaign/duct_secondary_flow_AR_7_validation_qcr.png"
    camp = _W + "/campaign"
    if rel.startswith(camp + "/"):
        rest = rel[len(camp) + 1:]
        head = rest.split("/", 1)[0]
        if _RUN_ARCHIVE.match(head):
            return "verification/runs/" + rest          # R20
        return "verification/campaign/" + rest          # R21
    if rel == camp:
        return "verification/campaign"
    m = _R25.match(rel)
    if m:                                               # R25
        return "verification/runs/%s/%s%s" % (
            m.group(1), m.group(2), m.group(3) or "")
    m = _LOOSE_WEB.match(rel)
    if m and rel not in _EXPLICIT_LEGACY:               # R16 / R17
        name = m.group(1)
        return ("research/closure/md/" if name.endswith(".md")
                else "research/closure/data/") + name
    if _LOOSE_PNG.match(rel):
        return "media/" + rel.split("/", 1)[1]          # R12
    return None


def _unspecial(rel: str) -> str | None:
    """Inverse of `_special`."""
    if rel == "web/campaign/duct_secondary_flow_AR_7_validation_qcr.png":
        return _SERVED_PNG
    # R25 before R20, and the discriminator is the FIRST segment under
    # `verification/runs/`.  R20 puts a `*_runs`/`*_work` tree name there; R25
    # puts a campaign name.  A campaign that named itself `X_runs` would be
    # read as R20's, which is the right precedence -- R20 owns that namespace
    # and R25 is the guest in it.
    m = _R25_BACK.match(rel)
    if m and not _RUN_ARCHIVE.match(m.group(1)):
        return "docs/campaigns/%s/%s%s" % (
            m.group(1), m.group(2), m.group(3) or "")
    if rel == "verification/runs" or rel.startswith("verification/runs/"):
        rest = rel[len("verification/runs"):].lstrip("/")
        return (_W + "/campaign/" + rest) if rest else (_W + "/campaign")
    if rel == "verification/campaign" or rel.startswith("verification/campaign/"):
        rest = rel[len("verification/campaign"):].lstrip("/")
        return (_W + "/campaign/" + rest) if rest else (_W + "/campaign")
    m = _LOOSE_WEB_BACK.match(rel)
    if m and rel not in _EXPLICIT_TARGET:               # R16 / R17
        return _W + "/" + m.group(1)
    m = re.match(r"^media/([^/]+\.png)$", rel)
    if m:
        return "demo-output/" + m.group(1)
    return None


# ---------------------------------------------------------------------------
# The prefix table.  Every row is (name, legacy, successor, rule).
#
# ORDER MATTERS among rows that actually move: `redirect()` takes the FIRST
# matching prefix, so a longer prefix must precede any prefix of it.
# `_check_prefix_order()` enforces that at import rather than trusting the
# author to have sorted it, because the one thing a longest-prefix table
# reliably does is get re-sorted by somebody tidying it.
# ---------------------------------------------------------------------------

_MOVES: tuple[tuple[str, str, str, str], ...] = (
    # -- R13, the served set (MOVE_MAP s3), closed at depth 2.
    ("WEB_CLOSURE_HTML", _W + "/closure.html", "web/closure.html", "R13"),
    ("WEB_BENCHMARKS_HTML", _W + "/benchmarks.html", "web/benchmarks.html", "R13"),
    ("WEB_SHOOT_HTML", _W + "/shoot.html", "web/shoot.html", "R13"),
    ("WEB_WALL_HTML", _W + "/wall/wall.html", "web/wall/wall.html", "R13"),

    # -- R14 / R15 / R18: generator outputs that leave the webroot.
    ("BENCHMARKS_JSON", _W + "/benchmarks.json",
     "research/closure/data/benchmarks.json", "R14"),
    ("BENCHMARKS_PNG", _W + "/benchmarks.png",
     "research/closure/plots/benchmarks.png", "R15"),
    ("WALL_JSON", _W + "/wall/wall.json",
     "research/closure/data/wall.json", "R18"),

    # -- R22: one folder per physics family.
    ("DAFOAM", _W + "/dafoam", "cases/dafoam", "R22"),
    ("COMMITTEE_GRIDS", _W + "/committee-grids", "cases/committee-grids", "R22"),
    ("TMR_TRANSIENT_300CU", _W + "/tmr-naca0012-transient-300cu",
     "cases/tmr/tmr-naca0012-transient-300cu", "R22"),
    ("TMR_TRANSIENT_A10", _W + "/tmr-naca0012-transient-a10-225x65",
     "cases/tmr/tmr-naca0012-transient-a10-225x65", "R22"),
    ("TMR_FLATPLATE_FINEST", _W + "/tmr-flatplate-finest-grids",
     "cases/tmr/tmr-flatplate-finest-grids", "R22"),
    ("TMR", _W + "/tmr", "cases/tmr", "R22"),
    ("HLPW6", _W + "/hlpw6", "cases/hlpw6", "R22"),
    ("MEGA_BATCH", _W + "/mega-batch", "cases/mega-batch", "R22"),
    ("UNSTEADY_CYLINDER", _W + "/unsteady-cylinder",
     "cases/unsteady-cylinder", "R22"),
    ("VALVE", _W + "/valve", "cases/valve", "R22"),
    ("DEMO_SURFACES", "demo-surfaces", "cases/demo-surfaces", "R5"),

    # -- R23: research topics.
    ("RACE_GUI", _W + "/race-gui", "research/race/race-gui", "R23"),
    ("RACE_REYNOLDS_GRADIENT", _W + "/race-reynolds-gradient",
     "research/race/race-reynolds-gradient", "R23"),
    ("RACE", _W + "/race", "research/race", "R23"),
    ("AGENDA", _W + "/agenda", "research/agenda", "R23"),
    ("CLOSURE_SUBMISSION_ROUND4", _W + "/closure_challenge_submission_round4",
     "research/closure/closure_challenge_submission_round4", "R23"),
    ("CLOSURE_SUBMISSION_ROUND5", _W + "/closure_challenge_submission_round5",
     "research/closure/closure_challenge_submission_round5", "R23"),
    ("CLOSURE_SUBMISSION", _W + "/closure_challenge_submission",
     "research/closure/closure_challenge_submission", "R23"),
    ("CLOSURE_EVAL", _W + "/closure_eval",
     "research/closure/closure_eval", "R23"),
    ("OPTIMIZATION", _W + "/optimization", "research/optimization", "R23"),
    ("UQ_FLATPLATE", _W + "/r2-coefficient-uq-flatplate",
     "research/uq/r2-coefficient-uq-flatplate", "R23"),
    ("UQ_CLOSURE_COEFF", _W + "/r2-closure-coefficient-uncertainty",
     "research/uq/r2-closure-coefficient-uncertainty", "R23"),

    # -- R24 / R19.
    ("CERTIFICATES", _W + "/certificates", "verification/certificates", "R24"),
    ("CREDIBILITY", _W + "/credibility", "verification/credibility", "R24"),
    ("MONITOR", _W + "/monitor", "verification/monitor", "R24"),
    ("PARAVIEW", _W + "/paraview", "ops/paraview", "R19"),

    # -- HAND-CARRY.  These hold NO tracked file, so `git mv` never moves them
    #    (MOVE_MAP s9's standing mechanics).  The constant below moves; the
    #    tree does not, unless `scripts/hand_carry.py` carries it.  Named here
    #    so a consumer importing SOLVE_REGISTRY gets the truth about where the
    #    1.51 GB actually is, rather than where the map says it goes.
    #
    #    Destination follows MOVE_MAP section 7.3's own rule rather than an
    #    invention: "/verification/runs/ is the tracked-record side, /evidence/
    #    is the gitignored bulk."  Both of these are 100% gitignored bulk cited
    #    from records -- `.gitignore:37` and `:76` say so of `solve_registry`
    #    in as many words -- so they go to `/evidence/`, not into the tracked
    #    side of the tree.  This is a DECISION and it is the owner's to ratify.
    ("SOLVE_REGISTRY", _W + "/solve_registry",
     "evidence/solve_registry", "HC1"),
    ("SURFACES", _W + "/surfaces", "evidence/surfaces", "HC2"),

    # -- R10 / R11: filming and plots.
    ("ACTS", "demo-output/acts", "media/acts", "R10"),
    ("GUI_PROOF", "demo-output/gui-proof", "media/gui-proof", "R10"),
    ("FALLBACKS", "demo-output/fallbacks", "media/fallbacks", "R10"),
    ("PLOTS", "demo-output/plots", "media/plots", "R11"),

    # -- R1 / R2: loose root files.
    ("LESSONS", "LESSONS.md", "docs/LESSONS.md", "R1"),
    ("LOCATIONS", "LOCATIONS.md", "docs/LOCATIONS.md", "R1"),
    ("FILMING_COMMANDS", "FILMING_COMMANDS.md",
     "media/FILMING_COMMANDS.md", "R2"),
    ("LAPTOP_SHOOT", "LAPTOP_SHOOT.md", "media/LAPTOP_SHOOT.md", "R2"),

    # -- R6 / R8: aws docs and launchers leave `scripts/`.
    ("AWS_DOCS", "docs/aws", "ops/aws", "R6"),
    ("INSTALLED", "scripts/installed", "ops/installed", "R8"),
    ("LAPTOP_BUNDLE", "scripts/laptop_bundle", "ops/laptop_bundle", "R8"),

    # -- The webroot itself.  LAST among the moving rows, because it is a
    #    prefix of most of them.
    ("WEB", _W, "web", "R13"),

    # ----- BIND-ONLY rows.  These are bound and probed like any other name,
    # but they are excluded from `redirect()` -- either because a non-prefix
    # rule already answers for them (CAMPAIGN, RUNS: the R20/R21 split is
    # decided in `_special`, and a prefix row for them would be dead code that
    # a later reader would trust), or because they are DESTINATION-ONLY names
    # with no single legacy directory (the `research/closure/` family, which
    # R14-R18 and R23 assemble from eight scattered sources).  A
    # destination-only name is deliberately left in `UNRESOLVED` before its
    # batch lands: that is the honest answer, and `unknown_reason()` turns it
    # into UNKNOWN rather than a path that is not there.
    ("CAMPAIGN", _W + "/campaign", "verification/campaign", "R21"),
    ("RUNS", _W + "/campaign", "verification/runs", "R20"),
    # R25's two trees, named so a consumer can ask for one and so `state()`
    # reports each side of the move.  `_special` answers for every path under
    # them, so these rows are BIND-ONLY: a prefix row consulted by `redirect()`
    # would be dead code a later reader would trust.
    ("F14_K0C_RUNS", "docs/campaigns/F14-cooling-ladder/K0c_runs",
     "verification/runs/F14-cooling-ladder/K0c_runs", "R25"),
    ("F14_K0B_MESH_SENSITIVITY",
     "docs/campaigns/F14-cooling-ladder/K0b_mesh_sensitivity",
     "verification/runs/F14-cooling-ladder/K0b_mesh_sensitivity", "R25"),
    ("CLOSURE", "research/closure", "research/closure", "R14-R18/R23"),
    ("CLOSURE_DATA", "research/closure/data", "research/closure/data", "R14"),
    ("CLOSURE_MD", "research/closure/md", "research/closure/md", "R16"),
    ("CLOSURE_PLOTS", "research/closure/plots", "research/closure/plots", "R15"),
    ("SDK", "sdk", "sdk", "R3"),
    ("SDK_CHIEF_RUNS", "sdk/chief-engineer-runs", "sdk/chief-engineer-runs", "-"),
    ("MODELS", "models", "models", "R4"),
    ("DOCS", "docs", "docs", "R7"),
    ("SCRIPTS", "scripts", "scripts", "R9"),
    ("DIST", "dist", "dist", "X1"),
    ("STL_FILES", "Stl_files", "Stl_files", "X2"),
    ("LATEX", _W + "/latex", _W + "/latex", "X3"),
    ("MOTORBIKE_VIDEO", _W + "/motorbike-video", _W + "/motorbike-video", "X3"),
    # Gitignored runtime trees the map's section 1 target tree never mentions.
    # `mission-output/` holds 8,625 files / 573 MB and is named by 13 tracked
    # modules; it does not move, and saying so here is what stops the next
    # sweep from "tidying" it into the new tree.
    ("MISSION_OUTPUT", "mission-output", "mission-output", "-"),
    ("CHIEF_RUNS", "chief-engineer-runs", "chief-engineer-runs", "-"),
    ("DEMO_OUTPUT", "demo-output", "demo-output", "-"),
    ("EVIDENCE", "evidence", "evidence", "R4/s7.3"),
)


class Move:
    """One row of the map: a name, a legacy path, a successor, a rule id."""

    __slots__ = ("name", "legacy", "target", "rule")

    def __init__(self, name: str, legacy: str, target: str, rule: str) -> None:
        self.name, self.legacy, self.target, self.rule = name, legacy, target, rule

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Move {self.name} {self.legacy!r} -> {self.target!r} [{self.rule}]>"

    @property
    def moves(self) -> bool:
        return self.legacy != self.target


#: Bound and probed, but never consulted by `redirect()` -- see the comment on
#: the bind-only block of `_MOVES`.
_BIND_ONLY = frozenset({"CAMPAIGN", "RUNS",
                        "F14_K0C_RUNS", "F14_K0B_MESH_SENSITIVITY"})

MOVES: tuple[Move, ...] = tuple(Move(*row) for row in _MOVES)
_BY_NAME = {m.name: m for m in MOVES}
_MOVING = tuple(m for m in MOVES if m.moves and m.name not in _BIND_ONLY)

#: A path with its OWN row is answered by that row, not by R16/R17's
#: loose-file rule.  `benchmarks.json` is R14 and `wall/wall.json` is R18;
#: both land in `research/closure/data/` either way, but the row is where the
#: rule id lives and a rule that quietly stops being consulted is how a table
#: becomes decoration.  Consulted by `_special` / `_unspecial` at call time,
#: which is after this module finishes importing.
_EXPLICIT_LEGACY = frozenset(m.legacy for m in MOVES)
_EXPLICIT_TARGET = frozenset(m.target for m in MOVES)

#: Every rule of `MOVE_MAP` s2.2 this module implements, INCLUDING the ones
#: that are not table rows.  Named as data so the coverage claim is testable
#: rather than assumed: R12, R16, R17, R20, R21 and R25 are regex rules in
#: `_special` and would otherwise be invisible to a test that reads `MOVES`.
#: Evidence: `test_every_move_rule_of_section_2_2_is_represented`.
RULES: frozenset[str] = frozenset(
    {m.rule for m in MOVES} | {"R12", "R16", "R17", "R20", "R21", "R25"})


def _check_prefix_order() -> None:
    """Refuse to import if a moving row is shadowed by an earlier, shorter one.

    A longest-prefix table that has been re-sorted alphabetically silently
    routes `demo-output/website/dafoam/x` to `web/dafoam/x`.  That is a wrong
    answer that looks right, so it is checked rather than commented.
    Evidence: `test_a_shorter_prefix_placed_first_is_refused_at_import`, which
    mutates this table and asserts the import fails.
    """
    if len(_BY_NAME) != len(MOVES):
        raise RuntimeError("lab_paths._MOVES has a duplicate name")
    seen: list[str] = []
    for m in _MOVING:
        for earlier in seen:
            if m.legacy == earlier or m.legacy.startswith(earlier + "/"):
                raise RuntimeError(
                    "lab_paths._MOVES is mis-ordered: %r is shadowed by the "
                    "earlier row %r; the longer prefix must come first"
                    % (m.legacy, earlier))
        seen.append(m.legacy)


_check_prefix_order()


# ---------------------------------------------------------------------------
# Prefix redirection -- the MOVE_MAP as a function
# ---------------------------------------------------------------------------

def _norm(p) -> str:
    s = str(p).replace(os.sep, "/")
    root = str(REPO).replace(os.sep, "/")
    if s.startswith(root + "/"):
        s = s[len(root) + 1:]
    while s.startswith("./"):
        s = s[2:]
    return s.rstrip("/")


def redirect(path) -> str | None:
    """Map a repo-relative legacy path to its successor, or None if no rule.

    Non-prefix rules first (never-move, the served PNG, the R20/R21 campaign
    split, R12's loose PNGs), then longest-prefix-first over `MOVES`.  A path
    already at its successor, or under a root that does not move, returns None
    -- "no redirect applies" and "the redirect is the identity" are different
    answers and are kept apart.
    Evidence: `test_the_campaign_split_is_on_the_child_segment_not_a_prefix`,
    `test_never_touch_trees_get_no_redirect`,
    `test_longest_prefix_wins_over_the_webroot_catch_all`,
    `test_redirect_does_not_fire_twice`,
    `test_no_two_tracked_paths_collide_on_one_successor` and
    `test_the_webroot_is_fully_classified`, the last two run over every tracked
    path rather than over examples.
    """
    rel = _norm(path)
    sp = _special(rel)
    if sp is False:
        return None
    if sp is not None:
        return sp
    for m in _MOVING:
        if rel == m.legacy:
            return m.target
        if rel.startswith(m.legacy + "/"):
            return m.target + rel[len(m.legacy):]
    return None


def unredirect(path) -> str | None:
    """The inverse: successor -> legacy.  Used to read pre-move records."""
    rel = _norm(path)
    us = _unspecial(rel)
    if us is not None:
        return us
    for m in _MOVING:
        if rel == m.target:
            return m.legacy
        if rel.startswith(m.target + "/"):
            return m.legacy + rel[len(m.target):]
    return None


def resolve(path) -> Path | None:
    """The one of {literal, successor, predecessor} that exists, or None.

    This is the resolver MOVE_MAP section 4.2 asks for: a citation is satisfied
    if it resolves either at its literal location or at its mapped successor.
    A citation to something that never existed still returns None, so the guard
    stays honest and 1,236 citations inside 234 append-only records stay
    unedited.
    Evidence: `test_resolve_finds_a_citation_at_its_successor_after_the_move`,
    `test_resolve_finds_a_citation_at_its_predecessor_before_the_move`, and the
    must-not-match control
    `test_resolve_returns_none_for_something_that_never_existed`.
    """
    rel = _norm(path)
    if not rel:
        return None
    literal = REPO / rel
    if literal.exists():
        return literal
    fwd = redirect(rel)
    if fwd is not None and (REPO / fwd).exists():
        return REPO / fwd
    back = unredirect(rel)
    if back is not None and (REPO / back).exists():
        return REPO / back
    return None


# ---------------------------------------------------------------------------
# Name binding -- resolved against the filesystem, never assumed
# ---------------------------------------------------------------------------

def _bind() -> tuple[dict[str, Path], tuple[str, ...], tuple[str, ...]]:
    out: dict[str, Path] = {}
    missing: list[str] = []
    both: list[str] = []
    for m in MOVES:
        legacy, target = REPO / m.legacy, REPO / m.target
        t_here, l_here = target.exists(), legacy.exists()
        if m.moves and t_here and l_here:
            both.append(m.name)
        if t_here:
            out[m.name] = target
        elif l_here:
            out[m.name] = legacy
        else:
            out[m.name] = legacy
            missing.append(m.name)
    return out, tuple(missing), tuple(both)


_BOUND, UNRESOLVED, AMBIGUOUS = _bind()


def state(name: str) -> str:
    """`moved` / `legacy` / `absent` / `both` for one name."""
    m = _BY_NAME[name]
    t, l = (REPO / m.target).exists(), (REPO / m.legacy).exists()
    if m.moves and t and l:
        return "both"
    if t:
        return "moved"
    if l:
        return "legacy"
    return "absent"


def require(name: str) -> Path:
    """The bound path, or raise.  Use where absence is a programming error."""
    if name in UNRESOLVED:
        m = _BY_NAME[name]
        raise FileNotFoundError(
            "lab_paths.%s resolves to neither its legacy path (%s) nor its "
            "successor (%s). Do not substitute a default: a checker that reads "
            "nothing must not report PASS (b0ab070d)."
            % (name, m.legacy, m.target))
    return _BOUND[name]


def resolved(*names: str) -> bool:
    """True iff every named root is on disk.  The gate before a sweep."""
    wanted = names or tuple(_BY_NAME)
    return not any(n in UNRESOLVED for n in wanted)


def unknown_reason(*names: str) -> str | None:
    """The repository's three-valued contract, in one call.

    Returns None when every named root resolves, otherwise the sentence a
    check should print before exiting 3 (UNKNOWN).  It never returns something
    a caller can mistake for PASS.
    Evidence: `test_unknown_reason_names_the_missing_roots` and its control
    `test_the_must_not_match_control`.
    """
    wanted = names or tuple(_BY_NAME)
    gone = [n for n in wanted if n in UNRESOLVED]
    if not gone:
        return None
    return ("UNKNOWN because %d layout root(s) resolve to neither their legacy "
            "path nor their successor: %s" % (len(gone), ", ".join(sorted(gone))))


def run_archive(name: str, campaign: str | None = None) -> Path | None:
    """Where run archive `<name>` lives right now, or None.

    R20 moves each `*_runs`/`*_work` tree under the webroot's `campaign/` to
    `verification/runs/<name>`.  R25 moves `docs/campaigns/<campaign>/<name>`
    to `verification/runs/<campaign>/<name>`, WITH the campaign segment, so a
    caller that knows the campaign passes it and one that does not gets a
    deterministic search over the campaigns that exist.
    """
    cands = []
    if campaign is not None:
        cands += ["verification/runs/%s/%s" % (campaign, name),
                  "docs/campaigns/%s/%s" % (campaign, name)]
    cands += ["verification/runs/" + name, _W + "/campaign/" + name]
    for cand in cands:
        if (REPO / cand).exists():
            return REPO / cand
    if campaign is None:                       # R25, campaign not named
        for parent in ("verification/runs", "docs/campaigns"):
            root = REPO / parent
            if not root.is_dir():
                continue
            for child in sorted(root.iterdir()):
                cand = child / name
                if cand.exists():
                    return cand
    return None


def web_file(name: str) -> Path:
    """Where a LOOSE webroot file lives right now -- for READING OR WRITING.

    `resolve()` answers for a file that exists.  R16/R17's 40 loose webroot
    files are mostly GENERATOR OUTPUT -- 21 `closure_challenge_*.json` written
    by `sdk/scripts/closure_*.py` -- and a generator names its output before
    the output is there, so `resolve()` returning None is the wrong answer for
    it and a hard-coded successor is the wrong answer too (it would write into
    a directory that does not exist until batch 5).

    So: the successor if the FILE is there, else the successor if its
    DIRECTORY is there (the region has moved, this file has not been written
    yet), else the legacy path.  A name with its own table row -- `benchmarks.
    json` (R14) -- is answered by the row, through `redirect`, not specially.
    Evidence: `test_web_file_answers_where_a_file_that_does_not_exist_yet_goes`
    and its control `test_web_file_prefers_the_side_the_file_is_actually_on`.
    """
    legacy = _W + "/" + name
    fwd = redirect(legacy)
    if fwd is None:
        return REPO / legacy
    target = REPO / fwd
    if target.exists() or target.parent.is_dir():
        return target
    return REPO / legacy


def SUBMISSION_PACKAGES() -> tuple[Path, ...]:
    """The `closure_challenge_submission*` packages, wherever they are now.

    Replaces `self_audit.py`'s `WEB.glob("closure_challenge_submission*")`.
    R23 sends the three of them into `research/closure/`, each keeping its own
    segment, so after batch 5 a glob rooted at the webroot finds nothing and
    the check that walks them reports a clean sweep of zero packages -- this
    corpus's most repeated failure.  Absent packages are dropped, so a caller
    that must not be blinded pairs this with `unknown_reason` on the same
    three names.
    Evidence: `test_submission_packages_reproduces_the_webroot_glob`.
    """
    out = []
    for n in ("CLOSURE_SUBMISSION", "CLOSURE_SUBMISSION_ROUND4",
              "CLOSURE_SUBMISSION_ROUND5"):
        p = _BOUND[n]
        if p.exists():
            out.append(p)
    return tuple(sorted(out))


def __getattr__(name: str) -> Path:
    """Expose every row of the map as a module-level constant."""
    try:
        return _BOUND[name]
    except KeyError:
        raise AttributeError(
            f"module 'lab_paths' has no attribute {name!r}") from None


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(_BOUND))


# ---------------------------------------------------------------------------
# The composite roots -- what replaces a whole-tree rglob
# ---------------------------------------------------------------------------

#: Replaces `WEB.rglob("*.md")` at `self_audit.py:4319` and `:4837`.  Before
#: the move these all sit under the one webroot and the tuple is equivalent to
#: the rglob.  After it they are separate roots, which is exactly why the rglob
#: had no single successor.
RECORD_ROOT_NAMES: tuple[str, ...] = (
    "CAMPAIGN", "RUNS", "CLOSURE_EVAL", "CLOSURE_SUBMISSION",
    "CLOSURE_SUBMISSION_ROUND4", "CLOSURE_SUBMISSION_ROUND5",
    "AGENDA", "DAFOAM", "MEGA_BATCH", "TMR", "HLPW6", "VALVE",
    "UNSTEADY_CYLINDER", "COMMITTEE_GRIDS", "RACE", "OPTIMIZATION",
    "UQ_FLATPLATE", "UQ_CLOSURE_COEFF",
    "CERTIFICATES", "CREDIBILITY", "MONITOR", "WEB",
)


def RECORD_ROOTS(existing_only: bool = True) -> tuple[Path, ...]:
    """The roots a record sweep must walk.

    With `existing_only` (the default) absent roots are dropped, which is right
    mid-move -- `research/closure/` does not exist until batch 5.  A caller
    that must not be blinded by an absent root pairs this with
    `unknown_reason(*RECORD_ROOT_NAMES)` and returns UNKNOWN rather than PASS.
    Deduplicated, because before the move several names resolve to paths under
    the one webroot and walking it twice double-counts every finding.
    Evidence: `test_record_roots_covers_every_record_the_rglob_reached` and
    `test_an_absent_root_does_not_silently_shrink_a_record_sweep`.
    """
    seen: list[Path] = []
    for n in RECORD_ROOT_NAMES:
        p = _BOUND[n]
        if existing_only and not p.exists():
            continue
        if any(p == q or q in p.parents for q in seen):
            continue
        seen = [q for q in seen if p not in q.parents]
        seen.append(p)
    return tuple(seen)


def SWEEP_ROOTS() -> tuple[str, ...]:
    """Replaces `self_audit.py:4309`'s `roots` whitelist.

    Five of its seven roots change under the map; `mission-output/` and
    `dist/` do not.  Both spellings are emitted while both exist on disk, so a
    citation written before the move and one written after both resolve during
    the batches.  Rendered as prefixes with a trailing slash, the form the
    guard already uses.
    Evidence: `test_sweep_roots_reproduces_self_audit_4309_before_the_move`,
    which reads the whitelist out of `self_audit.py`'s own source rather than
    from a copy of it.
    """
    live: list[str] = []
    for n in ("DEMO_OUTPUT", "WEB", "SDK", "SCRIPTS", "MODELS",
              "MISSION_OUTPUT", "DOCS", "DIST", "CAMPAIGN", "RUNS",
              "CLOSURE", "AGENDA", "DAFOAM", "MEGA_BATCH", "EVIDENCE"):
        m = _BY_NAME[n]
        for cand in (m.legacy, m.target):
            token = cand + "/"
            if (REPO / cand).exists() and token not in live:
                live.append(token)
    for extra in ("cases/", "research/", "verification/", "media/", "ops/",
                  "web/"):
        if (REPO / extra).exists() and extra not in live:
            live.append(extra)
    # A prefix already covered by a shorter one in the list adds nothing to a
    # startswith() whitelist and costs the reader a false sense of coverage.
    return tuple(t for t in live
                 if not any(t != o and t.startswith(o) for o in live))


def BUNDLE_PAGES() -> tuple[tuple[str, Path, str], ...]:
    """Replaces `self_audit.py:6484-6489`'s `_BUNDLE_PAGES` triple.

    The member path inside the bundle is NOT the repo path, which is the whole
    reason the triple exists.  `scripts/build_laptop_bundle.py:53`'s
    `SITE_PAGES` deliberately omits `shoot.html`; that omission is preserved.
    Evidence: `test_bundle_pages_reproduces_self_audit_6484_before_the_move`.
    """
    return (
        ("closure.html", _BOUND["WEB_CLOSURE_HTML"], "site/closure.html"),
        ("benchmarks.html", _BOUND["WEB_BENCHMARKS_HTML"], "site/benchmarks.html"),
        ("wall.html", _BOUND["WEB_WALL_HTML"], "site/wall/wall.html"),
    )


#: MOVE_MAP section 3's served set, closed at depth 2.  Five files.  The PNG
#: keeps its `campaign/` segment because `closure.html:350` reaches it
#: relatively, which makes the page move a pure rename with zero edits.
SERVED_SET: tuple[str, ...] = (
    _W + "/closure.html",
    _W + "/benchmarks.html",
    _W + "/shoot.html",
    _W + "/wall/wall.html",
    _SERVED_PNG,
)


# ---------------------------------------------------------------------------
# The hand-carry registry
# ---------------------------------------------------------------------------

#: Trees named by a rule or by a path constant that `git mv` CANNOT move,
#: because they hold no tracked file.  `scripts/hand_carry.py` RE-DERIVES this
#: set from the live tree rather than trusting the list; the names here exist
#: so a consumer can ask `lab_paths.SOLVE_REGISTRY` and get the truth, and so
#: the two modules agree on destinations.  Do not treat this tuple as a census.
#: Evidence: `test_dark_tree_destinations_agree_with_the_table` and
#: `test_solve_registry_is_still_dark`.
DARK_TREES: tuple[tuple[str, str, str], ...] = (
    ("SOLVE_REGISTRY", _W + "/solve_registry", "evidence/solve_registry"),
    ("SURFACES", _W + "/surfaces", "evidence/surfaces"),
    ("THERMAL_K0_RUNS", _W + "/campaign/THERMAL_K0_runs",
     "verification/runs/THERMAL_K0_runs"),
    ("MESH_AUDIT_RUNS", _W + "/campaign/MESH_AUDIT_runs",
     "verification/runs/MESH_AUDIT_runs"),
)
