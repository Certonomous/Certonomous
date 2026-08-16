#!/usr/bin/env python3
"""Mutation proof for `scripts/check_rung_attribution.py` (D231).

WHY THIS FILE IS TRACKED. `docs/AGENT_ATTRIBUTION.md:243` claimed "every test is
mutation-proved: 12 mutants, all killed", and D173 measured what backed it:
`grep -ci mutant sdk/tests/test_rung_attribution.py` returned 0 and no harness
or record for this module existed anywhere in the tree. That is the same defect
the document is about -- a verification whose evidence does not travel expires
the moment it is made. So the proof is a file a later reader can RUN.

WHAT A MUTATION PROOF IS AND IS NOT. It shows a test detects A change, never
that it detects the RIGHT change. Two instances of that failure were seen in
this lab on 2026-08-15: a guard written by reading an already-mutated file
asserted the mutant and passed its own proof, and a probe survived an inverted
comparison because it asserted a COUNT rather than an IDENTITY. So every mutant
below names the DEFECT it reintroduces, every expectation in the aimed tests is
derived from the module docstring's specification rather than from the code, and
the probes name commits and handles rather than counting them.

HOW IT IS JUDGED. The control is run FIRST over the union of every aimed test
and must be GREEN; a mutant is scored killed only when a test IT AIMED AT is in
the new-failure set. `killed = returncode != 0` is not used: with a red control
that scores every survivor a kill, which is how a clean bill of health gets
manufactured.

THE MUTANT NEVER TOUCHES THE WORKING TREE. Four agents share this checkout, and
a harness here once held a tracked file mutated for ten minutes while
`git status` read clean. Each cell builds a MIRROR: a temporary root of symlinks
back to the repository, with the one mutated file a real copy. `__pycache__` is
purged before every cell in BOTH trees; `PYTHONDONTWRITEBYTECODE=1` does not fix
stale bytecode here and has inverted results in this lab.

Run:  python3 scripts/mutation_harness_rung_attribution.py
      python3 scripts/mutation_harness_rung_attribution.py --list
Exit: 0 when the control is green AND every mutant reddened an aimed test.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TARGET = "scripts/check_rung_attribution.py"
TEST_FILE = "test_rung_attribution.py"
SUITE = "sdk/tests/test_rung_attribution.py"

# Short names for the aimed tests, so the table below reads as an argument
# rather than as a wall of node ids.
HALVES = "BothHalvesOfTheControl"
AMBIG = "TheAmbiguousCasesResolveTheSafeWay"
UNARG = "TheUnargumentedRun"
LIMITS = "TheStatedLimits"
AGENTS = "ThePerAgentIdentity"
PROBE = "TheProbeReadsTheIdentityRatherThanTakingIt"
LIMITSOUT = "TheOutputCarriesItsOwnLimits"
SELECT = "TheGradedSetIsNeverSilentlySmaller"
INTEG = "TheIntegrityRunNeverPassesFromNothing"
GRAM = "TheEmitterCannotProduceWhatTheGrammarRejects"

NON_AUTHOR_HALF = f"{HALVES}::test_a_genuine_non_author_verifies"
AUTHOR_HALF = f"{HALVES}::test_a_same_agent_pair_is_caught"
PREDATES = f"{HALVES}::test_a_commit_predating_the_mechanism_is_unknown_not_either_verdict"
PRE_CLOSING = f"{HALVES}::test_a_pre_anchor_closing_commit_is_unknown_and_says_why"
EMPTY_SET = f"{HALVES}::test_an_empty_graded_set_is_unknown_naming_b1"
UNATTRIBUTED = f"{HALVES}::test_an_unattributed_graded_commit_is_unknown_never_independent"
TAG_NEVER = f"{HALVES}::test_the_self_declared_tag_never_upgrades_a_same_session_pair"
AUTHOR_BEATS = f"{AMBIG}::test_author_beats_partial_unknown"
MALFORMED_NOT_ABSENT = f"{AMBIG}::test_a_malformed_trailer_is_not_treated_as_absent"
TWO_TRAILERS = f"{AMBIG}::test_two_trailers_on_one_commit_do_not_resolve_to_the_first"
EMITTER_GRAMMAR = f"{AMBIG}::test_the_emitter_and_the_grammar_agree"
EMIT_NO_SESSION = f"{AMBIG}::test_emit_without_a_session_emits_nothing_and_says_unknown"
NO_WALK = f"{AMBIG}::test_a_bare_graded_rev_does_not_walk_its_ancestors"
CLEAN_PASSES = f"{UNARG}::test_clean_history_passes_and_reports_adoption_as_a_number"
PRE_ANCHOR_FAIL = f"{UNARG}::test_a_trailer_before_the_anchor_is_a_fail"
BROKEN_EMITTER = f"{UNARG}::test_a_broken_emitter_is_a_fail_not_a_gap_in_adoption"
ABSENT_ANCHOR = f"{UNARG}::test_an_anchor_absent_from_the_clone_is_unknown_not_pass"
UNANCHORED = f"{UNARG}::test_an_unanchored_build_is_unknown_not_pass"
ANCHOR_ALONE = f"{UNARG}::test_an_anchor_with_no_commits_after_it_still_examines_the_anchor"
CHERRY = f"{LIMITS}::test_a_cherry_pick_replays_the_original_agents_trailer"
PRINTS_LIMITS = f"{LIMITS}::test_every_run_prints_what_it_does_not_verify"
PRINTS_FRAME = f"{LIMITS}::test_every_run_prints_its_frame"

AGENT_SPLIT = f"{AGENTS}::test_a_same_session_pair_with_different_agents_is_non_author"
AGENT_SAME = f"{AGENTS}::test_the_same_agent_on_both_sides_is_still_caught"
AGENT_ONE_SIDED = f"{AGENTS}::test_an_agent_id_on_only_the_closing_side_does_not_upgrade"
AGENT_ONE_SIDED_2 = f"{AGENTS}::test_an_agent_id_on_only_the_graded_side_does_not_upgrade"
LEGACY = f"{AGENTS}::test_a_session_only_trailer_still_parses"
BAD_FOURTH = f"{AGENTS}::test_a_fourth_field_that_is_not_an_agent_handle_is_malformed"
DISTINCT_UNIT = f"{AGENTS}::test_distinct_agents_needs_two_well_formed_and_different_handles"

PROBE_ONE = f"{PROBE}::test_a_probe_in_exactly_one_transcript_resolves_to_that_agent"
PROBE_TWO = f"{PROBE}::test_a_probe_in_two_transcripts_is_refused_not_guessed"
PROBE_NONE = f"{PROBE}::test_a_probe_in_no_transcript_is_refused"
PROBE_SHORT = f"{PROBE}::test_a_short_probe_is_refused_before_it_is_searched"
PROBE_BADNAME = f"{PROBE}::test_a_transcript_filename_that_is_not_a_handle_is_not_returned"
PROBE_SESSION = f"{PROBE}::test_a_transcript_of_another_session_is_not_searched"
PROBE_EMIT = f"{PROBE}::test_emit_with_a_probe_yields_a_four_field_trailer_that_parses"
PROBE_REFUSE = f"{PROBE}::test_an_unresolvable_probe_emits_nothing_rather_than_the_weaker_line"
PROBE_CLI_REFUSE = f"{PROBE}::test_the_cli_refuses_an_unresolvable_probe_and_exits_unknown"
PROBE_CLI_EMIT = f"{PROBE}::test_the_cli_emits_the_resolved_handle"

BACKFILL = f"{LIMITSOUT}::test_every_run_prints_the_backfill_statement"
ONE_CONSTANT = f"{LIMITSOUT}::test_one_identity_observed_says_it_has_not_been_shown_to_discriminate"
AGENT_COUNTS = f"{LIMITSOUT}::test_per_agent_handles_are_counted_in_the_integrity_frame"
TWO_IDENTITIES = f"{LIMITSOUT}::test_two_identities_observed_drops_the_never_varied_wording"
JSON_FRAME = f"{LIMITSOUT}::test_the_json_frame_carries_the_granularity_and_the_counts"
NO_OVERCLAIM = f"{LIMITSOUT}::test_a_session_granularity_author_does_not_claim_the_measurer_wrote_it"

RANGE = f"{SELECT}::test_a_range_selector_grades_every_commit_in_the_range"
EMPTY_SELECTOR = f"{SELECT}::test_a_selector_matching_nothing_is_named_not_ignored"
BAD_SPEC = f"{SELECT}::test_an_unresolvable_graded_spec_is_unknown_never_a_verdict"
READ_BAD_REV = f"{SELECT}::test_read_commits_reports_a_bad_rev_rather_than_dropping_it"
DEDUP = f"{SELECT}::test_the_same_commit_named_twice_is_graded_once"
MULTI_CLOSING = f"{SELECT}::test_a_closing_spec_naming_more_than_one_commit_is_refused"
SELF_GRADED = f"{SELECT}::test_a_closing_commit_inside_its_own_graded_set_is_author"
NO_CLOSING = f"{SELECT}::test_graded_without_closing_exits_unknown_with_a_reason"

ZERO_ADOPTION = f"{INTEG}::test_zero_adoption_since_the_anchor_is_unknown_not_pass"
ZERO_EXAMINED = f"{INTEG}::test_zero_commits_examined_is_unknown_naming_b1"
DUPLICATE_FAIL = f"{INTEG}::test_a_duplicate_trailer_is_a_broken_emitter_not_an_adoption_gap"
RATIO = f"{INTEG}::test_the_pass_reason_states_the_adoption_ratio_not_the_examined_count"
OFF_BRANCH = f"{INTEG}::test_an_anchor_on_another_branch_is_unknown_and_says_so"
UNANCHORED_REASON = f"{INTEG}::test_an_unanchored_build_is_unknown_and_names_the_reason"
EMPTY_RANGE = f"{INTEG}::test_a_range_that_comes_back_empty_is_an_error_not_a_clean_sheet"
SWEEP_UNIT = f"{INTEG}::test_a_pre_anchor_sweep_that_cannot_run_is_unknown_not_clean"
SWEEP_WIRED = f"{INTEG}::test_the_integrity_run_reports_a_sweep_that_could_not_run"
ROOT_ANCHOR = f"{INTEG}::test_a_root_anchor_has_no_ancestry_to_sweep"
MERGE_SWEEP = f"{INTEG}::test_the_pre_anchor_sweep_walks_both_parents_of_a_merge"

HOST_MATTERS = f"{GRAM}::test_the_host_distinguishes_two_commits_of_the_same_session_id"
BAD_TAG = f"{GRAM}::test_a_tag_with_a_separator_or_a_space_is_malformed"
TAB_LINE = f"{GRAM}::test_a_tab_separated_broken_line_is_malformed_not_absent"
HOST_SANITISED = f"{GRAM}::test_a_hostile_hostname_is_sanitised_into_something_that_parses"
HOST_UNUSABLE = f"{GRAM}::test_a_hostname_with_no_usable_field_emits_nothing"
TAG_SANITISED = f"{GRAM}::test_a_hostile_tag_is_sanitised_into_something_that_parses"
EMPTY_TAG = f"{GRAM}::test_an_empty_tag_becomes_the_no_tag_marker"
BAD_SESSION_EMIT = f"{GRAM}::test_a_non_uuid_session_emits_nothing_and_exits_unknown"
UNIT_SEPARATOR = f"{GRAM}::test_a_body_carrying_the_unit_separator_keeps_its_trailer"
ANCESTRY_UNKNOWN = f"{GRAM}::test_an_unknown_ancestry_is_not_reported_as_predating_the_anchor"


# (name, the defect it reintroduces, old, new, aimed tests)
MUTATIONS: list[tuple[str, str, str, str, list[str]]] = [

    # ---- parse_trailer, where an identity is read or invented --------------
    ("dup_takes_the_first",
     "a commit claiming two identities resolves to the first one",
     "    if len(claims) > 1:\n        return DUPLICATE, None, None, None",
     "    if len(claims) > 99:\n        return DUPLICATE, None, None, None",
     [TWO_TRAILERS, DUPLICATE_FAIL]),
    ("malformed_reads_as_absent",
     "a broken emitter reads as an agent that did not adopt the mechanism",
     "    if not m:\n        return MALFORMED, None, None, None",
     "    if not m:\n        return ABSENT, None, None, None",
     [MALFORMED_NOT_ABSENT, BROKEN_EMITTER]),
    ("absent_fabricates_an_identity",
     "a commit with no trailer is given a placeholder identity",
     "    if not claims:\n        return ABSENT, None, None, None",
     "    if not claims:\n        return OK, \"h/00000000-0000-0000-0000-000000000000\", \"-\", None",
     [UNATTRIBUTED]),
    ("identity_includes_the_tag",
     "the one field an agent TYPES is allowed to certify independence",
     "    return (OK, f\"{m.group('host')}/{m.group('session')}\",",
     "    return (OK, f\"{m.group('host')}/{m.group('session')}/{m.group('tag')}\",",
     [TAG_NEVER]),
    ("identity_is_host_only",
     "every commit on one box is one identity, so nothing is ever independent",
     "    return (OK, f\"{m.group('host')}/{m.group('session')}\",\n"
     "            m.group(\"tag\"), m.group(\"agent\"))",
     "    return (OK, f\"{m.group('host')}\",\n"
     "            m.group(\"tag\"), m.group(\"agent\"))",
     [NON_AUTHOR_HALF]),
    ("identity_drops_the_host",
     "two boxes' sessions merge into one identity",
     "    return (OK, f\"{m.group('host')}/{m.group('session')}\",\n"
     "            m.group(\"tag\"), m.group(\"agent\"))",
     "    return (OK, f\"{m.group('session')}\",\n"
     "            m.group(\"tag\"), m.group(\"agent\"))",
     [HOST_MATTERS]),
    ("the_agent_field_is_never_read",
     "the repair is reverted: the fourth field is parsed and thrown away",
     "            m.group(\"tag\"), m.group(\"agent\"))",
     "            m.group(\"tag\"), None)",
     [AGENT_SPLIT, JSON_FRAME]),
    ("the_agent_and_tag_are_swapped",
     "the typed field decides and the derived one is printed",
     "            m.group(\"tag\"), m.group(\"agent\"))",
     "            m.group(\"agent\"), m.group(\"tag\"))",
     [AGENT_SPLIT]),

    # ---- the grammar ------------------------------------------------------
    ("grammar_accepts_any_session",
     "a session field that is not a UUID is accepted as an identity",
     "    r\"(?P<session>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/\"",
     "    r\"(?P<session>[^/]+)/\"",
     [MALFORMED_NOT_ABSENT]),
    ("grammar_accepts_any_tag",
     "a tag may contain separators and spaces, so the fields can shift",
     "    r\"(?P<tag>[A-Za-z0-9._-]{1,32})\"",
     "    r\"(?P<tag>[^\\n]*?)\"",
     [BAD_TAG]),
    ("grammar_accepts_any_agent_handle",
     "the fourth field may be anything, including another agent's prose",
     "    r\"(?:/(?P<agent>agent-[0-9a-f]{6,40}))?[ \\t]*$\")",
     "    r\"(?:/(?P<agent>.+))?[ \\t]*$\")",
     [BAD_FOURTH]),
    ("grammar_requires_an_agent_handle",
     "the repair marks its own first four adopters MALFORMED",
     "    r\"(?:/(?P<agent>agent-[0-9a-f]{6,40}))?[ \\t]*$\")",
     "    r\"(?:/(?P<agent>agent-[0-9a-f]{6,40}))[ \\t]*$\")",
     [LEGACY, CLEAN_PASSES]),
    ("any_trailer_requires_a_space",
     "a tab-broken Lab-Agent line reads as no trailer at all",
     "ANY_TRAILER_RE = re.compile(r\"^Lab-Agent:\")",
     "ANY_TRAILER_RE = re.compile(r\"^Lab-Agent: \")",
     [TAB_LINE]),

    # ---- ancestry ---------------------------------------------------------
    ("pre_anchor_reads_as_after",
     "a commit from before the mechanism reads as one that did not adopt it",
     "    if r.returncode == 1:\n        return False\n    return None",
     "    if r.returncode == 1:\n        return True\n    return None",
     [PREDATES, PRE_CLOSING]),
    ("unknown_ancestry_reads_as_before",
     "an ancestry query that ERRORED is read as a No",
     "    if r.returncode == 1:\n        return False\n    return None",
     "    if r.returncode == 1:\n        return False\n    return False",
     [ANCESTRY_UNKNOWN]),
    ("pre_anchor_is_not_labelled",
     "backfill-impossible and did-not-adopt are reported as the same thing",
     "        if state == ABSENT and after is False:\n            state = PRE_ANCHOR",
     "        if state == ABSENT and after is None:\n            state = PRE_ANCHOR",
     [PREDATES, PRE_CLOSING]),

    # ---- reading commits --------------------------------------------------
    ("unreadable_commit_is_dropped",
     "a commit that fails to read is silently removed from the graded set",
     "        if r.returncode != 0:\n            return [], f\"git log failed for {sha!r}: {r.stderr.strip()}\"",
     "        if r.returncode != 0:\n            continue",
     [READ_BAD_REV]),
    ("unreadable_commit_is_dropped_and_the_size_guard_with_it",
     "the same drop with the belt-and-braces size check removed too",
     "        if r.returncode != 0:\n            return [], f\"git log failed for {sha!r}: {r.stderr.strip()}\"",
     "        if r.returncode != 0:\n            continue\n        _ = 0",
     [READ_BAD_REV]),
    # NOT LISTED, and the reason is a finding rather than an omission: removing
    # `if len(out) != len(revs)` ON ITS OWN is an EQUIVALENT MUTANT, because the
    # `return` above it makes the branch unreachable while that guard stands.
    # Its whole job is to kill the mutant BELOW, where both are removed, and
    # that pairing is what proves it is load-bearing rather than decorative.
    ("the_body_is_split_at_every_separator",
     "a commit body containing the unit separator loses its trailer",
     "    parts = blob.split(_UNIT, 3)",
     "    parts = blob.split(_UNIT)",
     [UNIT_SEPARATOR]),
    ("a_short_record_is_accepted",
     "a record with missing fields is indexed anyway",
     "    if len(parts) < 4:",
     "    if len(parts) < 0:",
     [UNIT_SEPARATOR]),

    # ---- selectors, every one of which can shrink the graded set ----------
    ("bare_rev_walks_its_ancestors",
     "`--graded <sha>` grades the whole history under it, guaranteeing AUTHOR",
     "        args = [\"rev-list\", spec] if \"..\" in spec else [\"rev-list\", \"--no-walk\", spec]",
     "        args = [\"rev-list\", spec]",
     [NO_WALK]),
    ("a_range_collapses_to_its_tip",
     "`--graded A..B` grades only B, dropping the author's commits. Measured "
     "while writing this table: `rev-list --no-walk A..B` returns the WHOLE "
     "range, so swapping the two arms is an equivalent mutant and would have "
     "been recorded as a survivor by a harness that did not check",
     "        args = [\"rev-list\", spec] if \"..\" in spec else [\"rev-list\", \"--no-walk\", spec]",
     "        args = [\"rev-list\", \"--no-walk\", spec.split(\"..\")[-1]]",
     [RANGE]),
    ("a_selector_matching_nothing_is_silent",
     "a selector that matched nothing contributes nothing and says nothing",
     "        if not found:\n            return [], f\"{spec!r} resolved to zero commits\"",
     "        if not found:\n            continue",
     [EMPTY_SELECTOR]),
    ("the_dedup_is_dropped",
     "one commit named twice is graded twice and inflates every count",
     "            if sha not in seen:\n                seen.add(sha)\n                shas.append(sha)",
     "            if True:\n                seen.add(sha)\n                shas.append(sha)",
     [DEDUP]),
    ("a_multi_commit_closing_spec_is_accepted",
     "the measurer is whichever commit rev-list happened to print first",
     "    if err or len(closing_shas) != 1:",
     "    if err:",
     [MULTI_CLOSING]),
    ("the_closing_commit_is_filtered_out_of_its_own_graded_set",
     "grading your own closing commit is tidied away into a clean answer",
     "    closing, graded = all_commits[0], all_commits[1:]",
     "    closing, graded = all_commits[0], [c for c in all_commits[1:]\n"
     "                                       if c.sha != all_commits[0].sha]",
     [SELF_GRADED]),
    ("the_graded_shas_are_not_reported",
     "the frame stops naming WHICH commits were graded, leaving only a count",
     "                 graded_shas=[c.sha for c in graded],",
     "                 graded_shas=[],",
     [RANGE, DEDUP]),

    # ---- the verdict ------------------------------------------------------
    ("empty_graded_set_is_non_author",
     "a checker that examined nothing clears the closure",
     "    if not graded:\n        return UNKNOWN, (\"the graded set is empty",
     "    if not graded:\n        return NON_AUTHOR, (\"the graded set is empty",
     [EMPTY_SET]),
    ("the_empty_guard_is_removed",
     "class B1: zero commits matched and a verdict came out anyway",
     "    if not graded:\n        return UNKNOWN, (\"the graded set is empty",
     "    if graded is None:\n        return UNKNOWN, (\"the graded set is empty",
     [EMPTY_SET]),
    ("a_blind_closing_commit_decides",
     "a closing commit with no identity of its own returns a verdict",
     "    if closing.identity is None:\n        if closing.state == PRE_ANCHOR:",
     "    if closing.identity is not None and False:\n        if closing.state == PRE_ANCHOR:",
     [PRE_CLOSING]),
    ("a_pre_anchor_closing_commit_is_not_named",
     "backfill-impossible is reported as an unreadable trailer",
     "        if closing.state == PRE_ANCHOR:",
     "        if closing.state == OK:",
     [PRE_CLOSING]),
    ("same_session_test_is_inverted",
     "the measurer is an author exactly when it is not",
     "    session_mates = [c for c in graded if c.identity == closing.identity]",
     "    session_mates = [c for c in graded if c.identity != closing.identity]",
     [AUTHOR_HALF, NON_AUTHOR_HALF]),
    ("the_same_agent_guard_is_removed",
     "an agent grading its own work is cleared",
     "    if same:\n        names = \", \".join(c.short for c in same[:6])",
     "    if same and False:\n        names = \", \".join(c.short for c in same[:6])",
     [AUTHOR_HALF, AGENT_SAME]),
    ("blind_beats_author",
     "a half-unattributed set hides a proven author behind UNKNOWN",
     "    blind = [c for c in graded if c.identity is None]\n    if blind:",
     "    blind = [c for c in graded if c.identity is None]\n    if blind and False:",
     [AUTHOR_BEATS, UNATTRIBUTED]),
    ("blind_only_counts_malformed",
     "an absent identity stops counting as blind and reads as independence",
     "    blind = [c for c in graded if c.identity is None]",
     "    blind = [c for c in graded if c.state == MALFORMED]",
     [UNATTRIBUTED]),
    ("a_one_sided_agent_handle_decides",
     "a handle on ONE side is treated as evidence about the other",
     "    if not a.agent or not b.agent:\n        return False",
     "    if not a.agent and not b.agent:\n        return False",
     [AGENT_ONE_SIDED, AGENT_ONE_SIDED_2, DISTINCT_UNIT]),
    ("a_malformed_agent_handle_decides",
     "a fourth field the grammar rejects is allowed to certify independence",
     "    if not _AGENT_RE.match(a.agent) or not _AGENT_RE.match(b.agent):\n        return False",
     "    if not _AGENT_RE.match(a.agent) and not _AGENT_RE.match(b.agent):\n        return False",
     [DISTINCT_UNIT]),
    ("the_agent_comparison_is_inverted",
     "an agent grading its own work is cleared BY the repair",
     "    return a.agent != b.agent",
     "    return a.agent == b.agent",
     [AGENT_SAME, DISTINCT_UNIT]),
    ("the_agent_split_is_ignored",
     "the repair is inert: two agents of one chief read as one agent again",
     "    same = [c for c in session_mates if not distinct_agents(c, closing)]",
     "    same = list(session_mates)",
     [AGENT_SPLIT]),
    ("the_granularity_is_always_agent",
     "a session-granularity answer is reported as a per-agent one",
     "            gran, who = G_SESSION, (f\"the closing commit's own SESSION identity \"",
     "            gran, who = G_AGENT, (f\"the closing commit's own SESSION identity \"",
     [AGENT_ONE_SIDED, AGENT_ONE_SIDED_2]),
    ("a_session_author_claims_the_measurer_wrote_it",
     "AUTHOR at session granularity overclaims in the other direction: one "
     "chief session dispatches several agents, so 'the measurer is an author' "
     "is a statement about a session wearing an agent's name",
     "            verdict_tail = (\"The measurer's session is an author. At session \"",
     "            verdict_tail = \"The measurer is an author\"\n"
     "            _unused = (\"The measurer's session is an author. At session \"",
     [NO_OVERCLAIM]),

    # ---- the integrity run ------------------------------------------------
    ("zero_commits_examined_is_pass",
     "class B1 at the top level: nothing was looked at and the answer is clean",
     "    if not commits:\n        return UNKNOWN, (\"zero commits examined since the anchor. Defect class \"",
     "    if not commits:\n        return PASS, (\"zero commits examined since the anchor. Defect class \"",
     [ZERO_EXAMINED]),
    ("pre_anchor_claims_are_ignored",
     "a rewritten history or a fabricated trailer passes",
     "    if pre_anchor_claims:\n        names = \", \".join(s[:8] for s in pre_anchor_claims[:8])",
     "    if pre_anchor_claims and False:\n        names = \", \".join(s[:8] for s in pre_anchor_claims[:8])",
     [PRE_ANCHOR_FAIL]),
    ("a_duplicate_trailer_is_not_broken",
     "a commit claiming two identities is counted as an adoption gap",
     "    broken = [c for c in commits if c.state in (MALFORMED, DUPLICATE)]",
     "    broken = [c for c in commits if c.state in (MALFORMED,)]",
     [DUPLICATE_FAIL]),
    ("a_malformed_trailer_is_not_broken",
     "a broken emitter is counted as an adoption gap",
     "    broken = [c for c in commits if c.state in (MALFORMED, DUPLICATE)]",
     "    broken = [c for c in commits if c.state in (DUPLICATE,)]",
     [BROKEN_EMITTER]),
    ("no_adoption_at_all_is_pass",
     "not one identity anywhere, and the instrument reports green",
     "    if counts[OK] == 0:\n        return UNKNOWN, (\"no commit since the anchor carries a well-formed \"",
     "    if counts[OK] == 0:\n        return PASS, (\"no commit since the anchor carries a well-formed \"",
     [ZERO_ADOPTION]),
    ("the_adoption_number_is_the_examined_number",
     "the ratio that says what a PASS is worth is reported as N of N",
     "                  f\"({counts[OK]} of {len(commits)} commits carry one), and no \"",
     "                  f\"({len(commits)} of {len(commits)} commits carry one), and no \"",
     [RATIO]),
    ("the_distinct_session_count_counts_commits",
     "D173's number stops being a count of IDENTITIES",
     "    sessions = sorted({c.identity for c in commits if c.identity})",
     "    sessions = sorted([c.identity for c in commits if c.identity])",
     [ONE_CONSTANT]),
    ("the_distinct_agent_count_is_never_taken",
     "per-agent handles are not counted, so the frame cannot show the repair",
     "    agents = sorted({c.agent for c in commits if c.agent})",
     "    agents = []",
     [AGENT_COUNTS]),

    # ---- run_integrity's own refusals -------------------------------------
    ("an_unanchored_build_is_not_named",
     "an unanchored build reports the reason of an absent anchor",
     "    if ANCHOR is None:",
     "    if ANCHOR is None and False:",
     [UNANCHORED_REASON, UNANCHORED]),
    ("an_absent_anchor_is_not_named",
     "an anchor missing from the clone reports as a stray branch",
     "    if _git(root, \"cat-file\", \"-e\", f\"{ANCHOR}^{{commit}}\").returncode != 0:",
     "    if _git(root, \"cat-file\", \"-e\", f\"{ANCHOR}^{{commit}}\").returncode != 0 and False:",
     [ABSENT_ANCHOR]),
    ("an_anchor_off_this_branch_is_accepted",
     "a branch not containing the mechanism is checked against it anyway",
     "    if _git(root, \"merge-base\", \"--is-ancestor\", ANCHOR, head_sha).returncode != 0:",
     "    if _git(root, \"merge-base\", \"--is-ancestor\", ANCHOR, head_sha).returncode != 0 and False:",
     [OFF_BRANCH]),
    ("an_empty_range_is_accepted",
     "an impossible empty range is treated as a clean sheet",
     "    if not shas:\n        return [], (f\"the anchor {anchor[:8]} is an ancestor of HEAD but the \"",
     "    if not shas and False:\n        return [], (f\"the anchor {anchor[:8]} is an ancestor of HEAD but the \"",
     [EMPTY_RANGE]),
    ("the_range_uses_first_parent_only",
     "a root anchor makes the range expression throw, and a merge is half-read",
     "    r = _git(root, \"rev-list\", head, \"--not\", f\"{anchor}^@\")",
     "    r = _git(root, \"rev-list\", f\"{anchor}~1..{head}\")",
     [ANCHOR_ALONE, CLEAN_PASSES]),
    ("a_failed_sweep_is_not_carried_to_the_verdict",
     "the sweep refuses, and the caller reports PASS anyway",
     "    if pre_err:\n        frame.update(verdict=UNKNOWN, reason=pre_err, stats={})",
     "    if pre_err and False:\n        frame.update(verdict=UNKNOWN, reason=pre_err, stats={})",
     [SWEEP_WIRED]),

    # ---- the pre-anchor sweep ---------------------------------------------
    ("the_sweep_walks_first_parents_only",
     "a merge anchor's second-parent side is never opened and reports zero",
     "             \"--grep=^Lab-Agent:\", f\"{anchor}^@\")",
     "             \"--grep=^Lab-Agent:\", f\"{anchor}~1\")",
     [MERGE_SWEEP]),
    ("the_sweep_greps_for_nothing",
     "the sweep runs and matches nothing it was meant to match",
     "             \"--grep=^Lab-Agent:\", f\"{anchor}^@\")",
     "             \"--grep=^NoSuchTrailer:\", f\"{anchor}^@\")",
     [PRE_ANCHOR_FAIL]),
    ("a_failed_sweep_is_clean",
     "a sweep that could not run reports nothing found",
     "    if r.returncode != 0:\n        return [], (f\"the pre-anchor sweep could not run",
     "    if r.returncode == 0:\n        return [], (f\"the pre-anchor sweep could not run",
     [PRE_ANCHOR_FAIL, ROOT_ANCHOR]),
    ("an_absent_anchor_is_a_root_commit",
     "an anchor not in this repository looks like one with nothing behind it",
     "        return None, (f\"{rev[:8]} is not a commit in this repository, so its \"",
     "        return False, (f\"{rev[:8]} is not a commit in this repository, so its \"",
     [SWEEP_UNIT]),
    ("the_root_anchor_guard_is_inverted",
     "a parented anchor is not swept and a root anchor is",
     "    if not parented:\n        return [], \"\"",
     "    if parented:\n        return [], \"\"",
     [PRE_ANCHOR_FAIL, ROOT_ANCHOR]),

    # ---- the emitter ------------------------------------------------------
    ("a_missing_session_is_fabricated",
     "a process outside a session emits a placeholder identity",
     "    if not session:\n        return None, (\"CLAUDE_CODE_SESSION_ID is not set",
     "    if not session:\n        return \"Lab-Agent: h/00000000-0000-0000-0000-000000000000/-\", (\"CLAUDE_CODE_SESSION_ID is not set",
     [EMIT_NO_SESSION]),
    ("a_non_uuid_session_is_emitted",
     "the emitter produces exactly what its own grammar rejects",
     "    if not _UUID_RE.match(session):\n"
     "        return None, (f\"CLAUDE_CODE_SESSION_ID={session!r} is not a UUID",
     "    if _UUID_RE.match(session) and False:\n"
     "        return None, (f\"CLAUDE_CODE_SESSION_ID={session!r} is not a UUID",
     [BAD_SESSION_EMIT]),
    ("the_host_is_not_sanitised",
     "a hostname with a separator in it shifts every field of the trailer",
     "    host = re.sub(r\"[^A-Za-z0-9._-]\", \"-\", os.uname().nodename)[:64]",
     "    host = os.uname().nodename",
     [HOST_SANITISED]),
    ("an_unusable_host_emits_anyway",
     "a hostname with no usable characters is emitted as a malformed trailer",
     "    if not host or not host[0].isalnum():",
     "    if host and not host[0].isalnum() and False:",
     [HOST_UNUSABLE]),
    ("the_tag_is_not_sanitised",
     "a tag with a separator in it shifts the agent field",
     "    slug = re.sub(r\"[^A-Za-z0-9._-]\", \"-\", tag)[:32] or \"-\"",
     "    slug = tag",
     [TAG_SANITISED]),
    ("an_empty_tag_emits_an_empty_field",
     "an empty tag emits a trailer with a hole in it",
     "    slug = re.sub(r\"[^A-Za-z0-9._-]\", \"-\", tag)[:32] or \"-\"",
     "    slug = re.sub(r\"[^A-Za-z0-9._-]\", \"-\", tag)[:32]",
     [EMPTY_TAG]),
    ("an_unresolvable_probe_falls_back_to_the_session_line",
     "THE DEFECT THIS REPAIR EXISTS FOR: a caller who asked for a per-agent "
     "identity is handed a session one and cites it as per-agent evidence",
     "    if agent is None:\n        return None, (f\"--probe was given",
     "    if agent is None:\n        return line, (f\"--probe was given",
     [PROBE_REFUSE, PROBE_CLI_REFUSE]),

    # ---- the probe, where the identity is READ rather than typed ----------
    ("the_probe_length_floor_is_dropped",
     "a three-character token matches by accident and names the wrong agent",
     "    if not _PROBE_RE.match(probe or \"\"):",
     "    if not _PROBE_RE.match(probe or \"\") and False:",
     [PROBE_SHORT]),
    ("two_matches_take_the_first",
     "the copied-brief accident resolves, silently, to whoever sorted first",
     "    if len(hits) > 1:",
     "    if len(hits) > 99:",
     [PROBE_TWO]),
    ("zero_matches_returns_a_handle",
     "a probe that matched nothing yields an identity anyway",
     "    if not hits:\n        return None, (f\"probe {probe!r} appears in no subagent transcript under \"",
     "    if not hits:\n        return \"agent-000000\", (f\"probe {probe!r} appears in no subagent transcript under \"",
     [PROBE_NONE]),
    ("the_probe_searches_every_session",
     "another session's transcripts answer for this one",
     "    for path in sorted(base.glob(f\"*/{session}/subagents/agent-*.jsonl\")):",
     "    for path in sorted(base.glob(\"*/*/subagents/agent-*.jsonl\")):",
     [PROBE_SESSION]),
    ("the_transcript_filename_grammar_is_not_checked",
     "a filename the trailer grammar rejects is emitted into a commit",
     "        if not _AGENT_RE.match(name):\n            continue",
     "        if not _AGENT_RE.match(name) and False:\n            continue",
     [PROBE_BADNAME]),
    ("the_probe_flag_is_ignored",
     "--probe is accepted and does nothing, so agent granularity never happens",
     "        trailer, why = local_identity(\n            args.tag, args.probe,",
     "        trailer, why = local_identity(\n            args.tag, None,",
     [PROBE_CLI_EMIT]),
    ("the_transcripts_override_is_ignored",
     "the controls read the real harness state of whatever box they run on",
     "            Path(args.transcripts) if args.transcripts else None)",
     "            None)",
     [PROBE_CLI_EMIT]),

    # ---- what every run must print ----------------------------------------
    ("the_json_mode_is_dropped",
     "--json prints prose, and every machine consumer reads a parse error",
     "    if as_json:\n        print(json.dumps(frame, indent=2, sort_keys=True))",
     "    if as_json and False:\n        print(json.dumps(frame, indent=2, sort_keys=True))",
     [NO_WALK, JSON_FRAME]),
    ("the_forgeability_notice_is_dropped",
     "the output stops saying the trailer is self-asserted",
     "    print(_FORGEABLE)",
     "    pass",
     [PRINTS_LIMITS]),
    ("the_not_verified_notice_is_dropped",
     "the output stops saying it cannot see whether the grader EXECUTED",
     "    print(_NOT_VERIFIED)",
     "    pass",
     [PRINTS_LIMITS]),
    ("the_refusal_notice_is_dropped",
     "the backfill statement disappears and a green reads as covering history",
     "    print(_REFUSES)",
     "    pass",
     [BACKFILL]),
    ("the_discrimination_note_is_dropped",
     "D173's number stops being printed beside the verdict",
     "    print(note)",
     "    pass",
     [ONE_CONSTANT]),
    ("the_granularity_line_is_dropped",
     "a session answer and an agent answer become indistinguishable again",
     "    print(f\"GRANULARITY: {frame['granularity']}\")",
     "    pass",
     [BACKFILL, AGENT_SPLIT]),
    ("the_never_varied_wording_is_unconditional",
     "the notice becomes a slogan that is printed whatever was measured",
     "    if sessions <= 1 and agents == 0:",
     "    if True:",
     [TWO_IDENTITIES]),

    # ---- the exit contract ------------------------------------------------
    ("non_author_exits_fail",
     "a cleared closure exits non-zero and every gate reads it as a failure",
     "    codes = {PASS: EXIT_PASS, NON_AUTHOR: EXIT_PASS,",
     "    codes = {PASS: EXIT_PASS, NON_AUTHOR: EXIT_FAIL,",
     [NON_AUTHOR_HALF]),
    ("author_exits_pass",
     "an agent grading its own work exits 0 and the gate lets it through",
     "             FAIL: EXIT_FAIL, AUTHOR: EXIT_FAIL,",
     "             FAIL: EXIT_FAIL, AUTHOR: EXIT_PASS,",
     [AUTHOR_HALF, AGENT_SAME]),
    ("unknown_exits_pass",
     "every UNKNOWN in this module becomes a green exit code",
     "             UNKNOWN: EXIT_UNKNOWN}",
     "             UNKNOWN: EXIT_PASS}",
     [PREDATES, EMPTY_SET, ABSENT_ANCHOR]),
    ("graded_without_closing_is_accepted",
     "an attribution question with no measurer is answered",
     "        if not args.closing:\n            print(\"--graded needs --closing",
     "        if not args.closing and False:\n            print(\"--graded needs --closing",
     [NO_CLOSING]),
    ("emitting_nothing_exits_pass",
     "the emitter prints no identity and reports success",
     "            print(f\"no identity: {why}\", file=sys.stderr)\n            return EXIT_UNKNOWN",
     "            print(f\"no identity: {why}\", file=sys.stderr)\n            return EXIT_PASS",
     [EMIT_NO_SESSION, BAD_SESSION_EMIT]),
    ("the_anchor_override_is_ignored",
     "every control in the suite grades against the shipped anchor instead",
     "    if args.anchor is not None:\n        ANCHOR = args.anchor",
     "    if args.anchor is None:\n        ANCHOR = args.anchor",
     [CLEAN_PASSES, PRE_ANCHOR_FAIL]),
]


def purge_pycache(root: Path) -> None:
    for path in root.rglob("__pycache__"):
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path, ignore_errors=True)


def build_mirror(tmp: Path, mutated: str | None) -> Path:
    """A root that is the repository, except for one real, mutated file.

    The test file is COPIED rather than symlinked: it computes the repository
    root from `Path(__file__).resolve()`, and `resolve()` follows a symlink
    straight back to the real checkout, where the real -- unmutated -- checker
    lives. A harness that symlinked it would prove nothing and look green.
    """
    root = tmp / "mirror"
    root.mkdir()
    for entry in REPO.iterdir():
        if entry.name in {"scripts", "sdk"}:
            continue
        (root / entry.name).symlink_to(entry)
    (root / "scripts").mkdir()
    for entry in (REPO / "scripts").iterdir():
        if entry.name == Path(TARGET).name and mutated is not None:
            (root / "scripts" / entry.name).write_text(mutated, encoding="utf-8")
        else:
            (root / "scripts" / entry.name).symlink_to(entry)
    (root / "sdk").mkdir()
    for entry in (REPO / "sdk").iterdir():
        if entry.name == "tests":
            continue
        (root / "sdk" / entry.name).symlink_to(entry)
    (root / "sdk" / "tests").mkdir()
    for entry in (REPO / "sdk" / "tests").iterdir():
        if entry.name == TEST_FILE:
            shutil.copy2(entry, root / "sdk" / "tests" / entry.name)
        else:
            (root / "sdk" / "tests" / entry.name).symlink_to(entry)
    return root


_FAIL_RE = re.compile(r"^(?:FAILED|ERROR) (\S+)")


def run_tests(root: Path, targets: list[str]) -> tuple[set[str], str]:
    """(the aimed tests that FAILED, output tail). Not a boolean."""
    purge_pycache(root)
    purge_pycache(REPO)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=no",
         "-p", "no:cacheprovider",
         *[f"{SUITE}::{t}" for t in targets]],
        cwd=root, capture_output=True, text=True, timeout=1800)
    text = proc.stdout + proc.stderr
    failed = set()
    for line in text.splitlines():
        m = _FAIL_RE.match(line.strip())
        if m:
            failed.add(m.group(1).split("::", 1)[-1])
    return failed, text[-600:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true",
                    help="print the mutation table and run nothing")
    args = ap.parse_args()

    aimed_all = sorted({t for _, _, _, _, ts in MUTATIONS for t in ts})
    print(f"FRAME: target {TARGET}, suite {SUITE}, {len(MUTATIONS)} mutants, "
          f"{len(aimed_all)} distinct aimed tests")
    if args.list:
        for name, why, _, _, ts in MUTATIONS:
            print(f"  {name}\n      reintroduces: {why}\n"
                  f"      aimed: {', '.join(t.split('::')[-1] for t in ts)}")
        return 0

    source = (REPO / TARGET).read_text(encoding="utf-8")
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as raw:
        root = build_mirror(Path(raw), None)
        ctrl, tail = run_tests(root, aimed_all)
    print(f"CONTROL (no mutation), {len(aimed_all)} aimed test(s): "
          f"{'GREEN' if not ctrl else 'RED'}")
    if ctrl:
        print(tail)
        print("CONTROL IS NOT GREEN. Every judgment below would be noise: with a "
              "red control a survivor scores as a kill. Stopping.")
        return 2

    for name, why, old, new, targets in MUTATIONS:
        if source.count(old) != 1:
            print(f"{name}: SKIPPED -- anchor occurs {source.count(old)} "
                  f"time(s), not once")
            failures.append(f"{name}: anchor not unique")
            continue
        mutant = source.replace(old, new)
        try:
            compile(mutant, TARGET, "exec")
        except SyntaxError as exc:
            # A mutant that does not PARSE reddens every aimed test for the
            # wrong reason, or -- as happened while this table was written --
            # breaks the import and reddens none of them, which scores as a
            # survivor. Either way the result is noise, so it is a failure of
            # the TABLE and is reported as one.
            print(f"{name}: SKIPPED -- the mutant does not parse: {exc}")
            failures.append(f"{name}: mutant does not parse")
            continue
        with tempfile.TemporaryDirectory() as mraw:
            mirror = build_mirror(Path(mraw), mutant)
            failed, tail = run_tests(mirror, targets)
        hit = sorted(failed & set(targets))
        print(f"{'KILLED  ' if hit else 'SURVIVED'} {name}")
        print(f"    reintroduces: {why}")
        print(f"    aimed: {', '.join(t.split('::')[-1] for t in targets)}")
        if hit:
            print(f"    reddened: {', '.join(t.split('::')[-1] for t in hit)}")
        else:
            failures.append(f"{name}: no aimed test reddened")
            print(f"    {tail.strip()[-200:]}")

    print()
    if failures:
        print("MUTATION PROOF INCOMPLETE:")
        for item in failures:
            print(f"  - {item}")
        return 1
    print(f"MUTATION PROOF COMPLETE: control green over {len(aimed_all)} tests, "
          f"all {len(MUTATIONS)} mutants reddened an aimed test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
