#!/usr/bin/env python3
"""cost_channel.py -- STANDING RULE 3, ARMED ON HEAT-TRANSFER'S COST CHANNEL.

    python3 scripts/cost_channel.py --selftest
    python3 scripts/cost_channel.py --no-regression
    python3 -O scripts/cost_channel.py --selftest

WHY THIS FILE EXISTS
--------------------
Rule 3 was armed on the PHYSICS channel and unarmed on the COST channel, lab-wide.
`T3_runs/analyse_t3.py` plants `PLANT = 1.234e-03` into `T` and refuses if the reader
cannot see it; nothing anywhere planted a known non-zero `wall_s` into a sidecar and
refused if the COST reader could not see it.  cfd measured what that costs: at commit
`b0ec4c60` their `read_kv` split each line on the FIRST `=` and took the whole
remainder as the value, so a launcher line carrying four pairs parsed to ONE key, and
`float(st.get("wall_s","0") or 0)` returned a FALSE 0.0.  Committed consequence: ledger
row `C-20260910T052907.204386Z-e9df493d` (commit `4749ae1d`) recorded **0.00 core-min
for a run that cost 34.23**.

The parse was the proximate cause.  The reason nothing caught it is the deeper one and
it is what this file is for: `.get(key, "0")` CANNOT TELL AN ABSENT KEY FROM A MEASURED
ZERO.  A reader that returns 0.0 because the key was never there reports the same value
as one that measured a genuine zero, and no downstream check can separate them.
`cost_channel_guard()` separates them and REFUSES.

THE PARSING RULE -- cfd's, ADOPTED, PLUS ONE BRANCH THEY COULD NOT HAVE SEEN
---------------------------------------------------------------------------
A `key=` TOKEN is an identifier immediately followed by `=`, at line start or after
whitespace:

    (?:(?<=\\s)|^)([A-Za-z_][A-Za-z0-9_]*)=

  (A1) cfd's branch, taken verbatim from `cases/navier_class/watch_grade_calibrate.py`
       at `b0ec4c60`.  A line is a MULTI-PAIR record line if it carries TWO OR MORE
       tokens AND THE FIRST STARTS AT COLUMN 0 of the stripped line.  Each value runs
       from after its `=` to the START OF THE NEXT TOKEN -- never to the next
       whitespace -- so a value containing spaces survives.

  (A2) HEAT-TRANSFER'S FOURTH SHAPE, and the reason this file does not just import
       cfd's rule.  A line whose FIRST token is NOT at column 0 is still a multi-pair
       record when its tokens form a contiguous `;`-DELIMITED RUN: two or more tokens
       where the text between each consecutive pair ends in `;` and the value it
       carries holds no interior space.  Values run to the next token and lose one
       trailing `;`.

  (B)  EVERY OTHER LINE keeps the legacy `partition("=")` parse, BYTE FOR BYTE.

WHY (A2) IS NECESSARY, MEASURED NOT ASSUMED
-------------------------------------------
cfd's column-0 anchor is the whole safety of their change and it is kept.  But applied
alone to heat-transfer's data it LOSES a cost record that the territory's existing
instrument already reads.  `verification/runs/T-family/T3_runs/DONE.R_ff` line 2 is

    infrastructure (disclosed, not gating): wall_s=200678; ranks=8; core_min=26757.067; timeout_s=205500; capped=no; ...

Its first token is not at column 0, so cfd's rule sends it to branch (B), where
`partition("=")` yields the key
`"infrastructure (disclosed, not gating): wall_s"` and loses `ranks`, `core_min`,
`timeout_s` and `capped` outright.  That is a **26,757 core-min** record -- the largest
single cost figure in this territory -- and dropping it is not a conservative failure.

WHY (A2) IS SAFE, ALSO MEASURED.  Censused 2026-09-10 over every `STATUS*`, `DONE*`,
`COST*`, `LAUNCH_RECORD.txt` and `CASE.txt` under `verification/runs/T-family`,
`verification/runs/F14-cooling-ladder` and `verification/runs/THERMAL_K0_runs` --
865 files, 11,222 lines:

    no `=` at all                                          7,279
    single pair, token at column 0            -> (B)       3,230
    two or more tokens, first at column 0     -> (A1)        367
    single token, NOT at column 0             -> (B)         339
    two or more tokens, first not col 0, NOT
        semicolon-delimited                   -> (B)           6
    two or more tokens, semicolon-delimited   -> (A2)          1

(A2) fires on ONE line in the whole territory and it is `DONE.R_ff`.  The six lines it
deliberately declines are prose: draft ledger rows in
`T18_runs/COST_CALIBRATION_ROW_*.txt` quoting `rc=0, capped=no` inside sentences, and
`T25R3_MODULE_runs/S1/STATUS.S1`'s `legA End=1 FATAL=0; legB End=1 FATAL=0`.  Each
falls to (B) and parses exactly as it always did.

WHAT THE ANCHORS PREVENT, IN BOTH DIRECTIONS
--------------------------------------------
Dropping the anchors entirely -- harvesting every `\\w+=\\S+` anywhere in the file, which
is what `cap_census_audit.py:TOK` does today -- FABRICATES keys out of prose.  Measured
on this territory's 764 `STATUS*`/`DONE*` files: that unanchored parse disagrees with
the rule above on 31 files, and on 8 of them the disagreement is a COST-CHANNEL key.
Six are inventions:

    verification/runs/T-family/T5_runs/DONE.T5_CUBE_c
        "DONE T5_CUBE_c under the strict rule (rc=0, End, endTime, fields, age guard)"
        -> unanchored parse yields rc="0,"  from a SENTENCE.  There is no rc record
           in that file at all.
    verification/runs/T-family/T25R3_MODULE_runs/S1/STATUS.S1
        "  ok   1 rc=0, BOTH legs, RECORDED"  -> rc="0,"  from an indented report line.

The rule above returns no `rc` for either, which is the truth.  Two failures with
opposite signs -- an unanchored reader inventing a status, an over-anchored reader
losing 26,757 core-min -- are both live in this territory, and only a rule measured
against the shapes actually on disk avoids both.

NOT WIDENED, DELIBERATELY.  `open()` keeps strict decoding except where a legacy reader
being reproduced used `errors="replace"`; turning a corrupt sidecar into a quiet partial
read would weaken a failure rather than strengthen one.  No refusal here is optional.

NO GUARD HERE IS AN `assert`
----------------------------
`python3 -O` deletes every `assert` statement, so a refusal written as one is a refusal
an interpreter flag switches off.  `no_bare_assert_proof()` PARSES THIS FILE'S OWN AST
and refuses if a single `ast.Assert` node exists anywhere in it -- an AST parse, not a
grep, because a grep cannot tell an `assert` statement from the word "assert" in a
comment or a docstring, and gets it wrong in both directions.

CALL-SITE CONTRACT (CLAUDE.md rule 14 / L-221 / L-222)
------------------------------------------------------
A lesson is not applied until EVERY call site asserts it.  A cost reader in this
territory arms itself by INSERTING, never by replacing:

    from cost_channel import read_cost_row, cost_channel_guard, assert_cost_channel_armed
    assert_cost_channel_armed(scratch_dir)          # refuses (SystemExit 2) if blind
    row = read_cost_row(status_path, ranks_key="ranks")
    refusals = cost_channel_guard([row])
    if refusals:
        raise SystemExit("COST CHANNEL REFUSED: " + "; ".join(refusals))

`assert_cost_channel_armed()` runs the planted control before the caller is allowed to
report a cost.  It is the assert; it is not an `assert`.

BOOKKEEPING NEVER VOIDS PHYSICS (Sanaa, universal rule 2026-08-26).  A refusal from this
module suppresses a COST figure and a calibration row.  It never voids a grade, a gate
or a verdict.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys

# REPAIRED 2026-09-11: this constant was written for the file's ORIGINAL path
# verification/runs/T-family/cost_channel.py, where three ".." reach the repo
# root.  The file was added at scripts/ (417ed0963) and the constant was not
# changed with it, so REPO resolved to '/home' and EVERY fixture path it built
# was wrong -- the planted control could not be armed by anyone, which blocked
# T26's freeze precondition and K2f's comparator.  One "..", from scripts/.
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    ".."))
TREES = ["verification/runs/T-family",
         "verification/runs/F14-cooling-ladder",
         "verification/runs/THERMAL_K0_runs"]
SIDECAR_PREFIX = ("STATUS", "DONE", "COST")
SIDECAR_EXACT = ("LAUNCH_RECORD.txt", "CASE.txt")

EXIT_REFUSE = 2

# The key token.  cfd's regex, character for character (b0ec4c60).
_KV_TOKEN = re.compile(r'(?:(?<=\s)|^)([A-Za-z_][A-Za-z0-9_]*)=')

# Keys whose absence must never be reported as a measured value.
COST_KEYS = ("wall_s", "wall", "core_min", "ranks", "rc", "rc_solve",
             "timeout_s", "cap_core_min", "capped")


# =====================================================================================
# THE READER
# =====================================================================================

def _semicolon_run(line, toks):
    """(A2): do these tokens form a contiguous `;`-delimited run?

    Between consecutive tokens sits `<value><separator>`.  The run is only accepted when
    every such gap ends in `;` and the value before it carries no interior space -- so a
    sentence that happens to contain two `key=` fragments is NOT swept up.
    """
    for i in range(len(toks) - 1):
        gap = line[toks[i].end():toks[i + 1].start()].rstrip()
        if not gap.endswith(";"):
            return False
        if " " in gap[:-1].strip():
            return False
    return True


def parse_kv_text(text):
    """Parse `key=value` sidecar TEXT under the rule documented at the head of this file.

    Branches (A1)/(A2) are INSERTED ahead of the legacy branch; branch (B) reproduces the
    pre-repair reader byte for byte and is what every line that is not a record line
    still takes.
    """
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if "=" not in line:
            continue
        toks = list(_KV_TOKEN.finditer(line))
        multi = False
        strip_semi = False
        if len(toks) >= 2 and toks[0].start() == 0:
            multi = True                      # (A1) cfd's branch, verbatim
        elif len(toks) >= 2 and _semicolon_run(line, toks):
            multi = True                      # (A2) heat-transfer's semicolon record
            strip_semi = True
        if multi:
            for i, m in enumerate(toks):
                end = toks[i + 1].start() if i + 1 < len(toks) else len(line)
                val = line[m.end():end].strip()
                if strip_semi and val.endswith(";"):
                    val = val[:-1].strip()
                out[m.group(1)] = val
        else:
            # (B) LEGACY PATH -- byte-identical to the pre-repair readers.
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    return out


def read_kv(path):
    """Parse ONE NAMED sidecar file.  A missing file is an empty dict, never a zero."""
    if not os.path.isfile(path):
        return {}
    with open(path, errors="replace") as fh:
        return parse_kv_text(fh.read())


# --- THE PRE-REPAIR READERS, KEPT EXECUTABLE VERBATIM. --------------------------------
# Each is a reader that is live somewhere in this territory today.  They exist so the
# planted control can be shown able to say `false`: a control that only ever passes has
# not been shown to work.

def _reader_prerepair_perline(path):
    """VERBATIM `T5_runs/mark_done_t5.py:36` (blob a74ce20d) and the ten
    `analyse_t5*/analyse_t8/analyse_t3*` readers built on it: one pair per line,
    `line.split("=", 1)`.  Cannot see a second pair on a line."""
    d = {}
    if not os.path.isfile(path):
        return d
    with open(path, errors="replace") as fh:
        for line in fh:
            if "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    return d


_I2_RE = re.compile(r"^([A-Za-z_0-9]+)=(.*)$", re.M)


def _reader_prerepair_findall(path):
    """VERBATIM the `dict(re.findall(r"^([a-z_]+)=(.*)$", txt, re.M))` idiom carried by
    37 files in this territory (`mark_done_t24.py:151`, `mark_done_t25R.py:156`,
    `mark_done_t9aR1b.py:61`, ...).  `(.*)$` swallows the rest of the line: the same
    one-pair-per-line defect wearing a regex."""
    if not os.path.isfile(path):
        return {}
    with open(path, errors="replace") as fh:
        return dict(_I2_RE.findall(fh.read()))


_UNANCHORED = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)')


def _reader_unanchored_token(path):
    """VERBATIM `cap_census_audit.py:TOK` -- every `\\w+=\\S+` anywhere in the file, with
    no anchor at all.  Multi-pair safe and PROSE-UNSAFE: it manufactures `rc` out of the
    sentence in `DONE.T5_CUBE_c`.  The negative arm N3 requires it to be caught."""
    if not os.path.isfile(path):
        return {}
    with open(path, errors="replace") as fh:
        return {m.group(1): m.group(2) for m in _UNANCHORED.finditer(fh.read())}


def _reader_constant_zero(path):
    """A reader hard-wired to the answer that was committed at `4749ae1d`: wall 0, rc 0.
    A control that cannot catch THIS is not a control."""
    if not os.path.isfile(path):
        return {}
    return {"wall_s": "0", "wall": "0", "core_min": "0", "rc": "0", "rc_solve": "0",
            "ranks": "1"}


# =====================================================================================
# THE COST ROW, AND THE GUARD THAT MAKES ABSENCE VISIBLE
# =====================================================================================

def _num(d, *keys):
    for k in keys:
        if k in d:
            try:
                return float(str(d[k]).rstrip("s").rstrip(";"))
            except ValueError:
                pass
    return None


def read_cost_row(path, wall_keys=("wall_s", "wall"), ranks_key="ranks",
                  rc_keys=("rc", "rc_solve"), declared_ranks=None,
                  declared_rc=None):
    """One sidecar -> one cost row that CARRIES ITS OWN KEY-PRESENCE FACTS.

    The two `*_key_present` fields are the whole point.  Nothing else in the row can
    distinguish `wall_s` measured as 0 from `wall_s` never written, and that
    indistinguishability is what landed a false 0.00x ratio in another team's ledger.

    `declared_ranks` / `declared_rc` are the ONLY way past the corresponding refusals,
    and each is a PAIR `(value, basis)` where the basis NAMES the document or launcher
    the figure was read from.  A caller that knows a rung's rank count from its
    pre-registration says so on the record; a caller that merely assumes 1 cannot.  The
    declaration does not become a measurement -- the row carries `ranks_basis` so every
    downstream reader can see the figure was declared and by whom.  A declaration with
    no basis string is REFUSED, because an unattributed declaration is the assumption
    this guard exists to catch, wearing a different name.
    """
    st = read_kv(path)
    wall = _num(st, *wall_keys)
    ranks = _num(st, ranks_key)
    ranks_basis = "sidecar key `%s`" % ranks_key if ranks is not None else None
    ranks_declared_bad = None
    if ranks is None and declared_ranks is not None:
        try:
            val, basis = declared_ranks
        except (TypeError, ValueError):
            val, basis = None, None
        if val is None or not (isinstance(basis, str) and basis.strip()):
            ranks_declared_bad = ("declared_ranks=%r carries no naming basis"
                                  % (declared_ranks,))
        else:
            ranks = float(val)
            ranks_basis = "DECLARED by caller: %s" % basis.strip()
    core_min = _num(st, "core_min")
    if core_min is None and wall is not None:
        core_min = wall * (ranks if ranks is not None else 1.0) / 60.0
    rc_key = next((k for k in rc_keys if k in st), None)
    rc = st.get(rc_key) if rc_key else None
    rc_basis = "sidecar key `%s`" % rc_key if rc_key else None
    rc_declared_bad = None
    if rc_key is None and declared_rc is not None:
        try:
            val, basis = declared_rc
        except (TypeError, ValueError):
            val, basis = None, None
        if val is None or not (isinstance(basis, str) and basis.strip()):
            rc_declared_bad = "declared_rc=%r carries no naming basis" % (declared_rc,)
        else:
            rc = str(val)
            rc_basis = "DECLARED by caller: %s" % basis.strip()
    return {
        "source": path,
        "present": os.path.isfile(path),
        "keys": sorted(st),
        "wall_s": wall,
        "wall_key_present": any(k in st for k in wall_keys),
        "ranks": ranks,
        "ranks_key_present": ranks_key in st,
        "ranks_assumed_1": ranks is None,
        "ranks_basis": ranks_basis,
        "ranks_declared_bad": ranks_declared_bad,
        "core_min": core_min,
        "core_min_key_present": "core_min" in st,
        "rc": rc,
        "rc_key_present": rc_key is not None,
        "rc_basis": rc_basis,
        "rc_declared_bad": rc_declared_bad,
        "capped": st.get("capped"),
    }


def cost_channel_guard(rows):
    """Refusals for the COST channel.  Empty list means the channel may be reported.

    A 0.0 that came from an ABSENT key is a reader DEFAULT, not a measurement, and the
    two are never reported as the same thing.  Every clause below is a refusal; none is
    a warning, because a printed discrepancy labelled non-binding is worse than one
    never computed.
    """
    refusals = []
    for r in rows:
        where = r.get("source", "<unnamed>")
        if not r.get("present"):
            refusals.append(
                "%s: no sidecar on disk. An absent record is not a zero cost -- it is "
                "NOT MEASURED, and this channel refuses rather than charging nothing"
                % where)
            continue
        if not r.get("wall_key_present") and not r.get("core_min_key_present"):
            refusals.append(
                "%s: carries NO wall_s/wall key and NO core_min key, so any core-minute "
                "figure reported for it would be a reader DEFAULT and not a measurement"
                % where)
        if r.get("ranks_declared_bad"):
            refusals.append("%s: %s -- an unattributed declaration is the assumption "
                            "this guard exists to catch" % (where, r["ranks_declared_bad"]))
        if r.get("rc_declared_bad"):
            refusals.append("%s: %s -- an unattributed declaration is the assumption "
                            "this guard exists to catch" % (where, r["rc_declared_bad"]))
        if not r.get("core_min_key_present") and r.get("ranks_assumed_1"):
            refusals.append(
                "%s: core-minutes would be derived as wall x ranks / 60 with NO ranks "
                "key present and none declared -- ranks=1 here is an ASSUMPTION, not a "
                "measurement. Four K0eR2/K0eR3 sidecars in this territory carry ranks=2 "
                "and one T3 sidecar carries ranks=8, where that assumption understates "
                "the charge by 2x and 8x. Pass declared_ranks=(n, 'where you read n') "
                "to charge it on the record instead" % where)
        if r.get("rc") is None:
            refusals.append(
                "%s: carries NO rc key and none was declared, so any rc reported for it "
                "is a parse outcome and not a process status -- it cannot be used to "
                "sort waste" % where)
        if r.get("wall_s") is not None and r["wall_s"] < 0:
            refusals.append("%s: wall_s=%r is negative" % (where, r["wall_s"]))
    return refusals


def summarise_cost(rows):
    """Gross / cleaned / waste, in core-minutes.  Rule 12's unit, never wall, never USD."""
    gross = sum(r["core_min"] for r in rows
                if r.get("present") and r.get("core_min") is not None)
    # A row whose rc is None is NOT sorted either way: it is neither charged to waste nor
    # cleared of it.  cost_channel_guard() has already refused it; sorting it here would
    # be the guard's refusal quietly overruled one function later.
    waste_rows = [r for r in rows
                  if r.get("present") and r.get("rc") is not None
                  and str(r.get("rc")) not in ("0", "0.0")]
    waste = sum(r["core_min"] for r in waste_rows if r.get("core_min") is not None)
    return {
        "gross_core_min": gross,
        "waste_core_min": waste,
        "cleaned_core_min": gross - waste,
        "waste_sources": [os.path.basename(r["source"]) for r in waste_rows],
        "n_rows": len([r for r in rows if r.get("present")]),
    }


# =====================================================================================
# STANDING RULE 3: THE PLANTED CONTROL, DRIVEN THROUGH THE PRODUCTION PATH
# =====================================================================================
# 4321 is non-zero, exact in float, and equal to NO wall figure on disk in this
# territory, so a fixture read that returns a real file's value instead of the plant is
# CAUGHT rather than confused.
COST_PLANT_WALL = 4321
COST_PLANT_RANKS = 2
COST_PLANT_RC_OK = "0"
COST_PLANT_RC_NONZERO = "137"

# family -> the REAL on-disk sidecar whose BYTES are the fixture template.  Not one
# synthetic string among them: a fixture invented by the test tests the test.
PLANT_FAMILIES = {
    "one_pair_per_line": {
        "source": "verification/runs/T-family/T17_runs/STATUS.T17_CY_f",
        "wall_key": "wall_s",
        "shape": "one pair per line (the T-family run-root cost sidecar)",
    },
    "one_line_multi_pair": {
        "source": "verification/runs/F14-cooling-ladder/K0g_runs/STATUS.M1_c",
        "wall_key": "wall",
        "shape": "all pairs on ONE line (the F14 pool sidecar -- cfd's defect shape)",
    },
    "semicolon_record": {
        "source": "verification/runs/T-family/T3_runs/DONE.R_ff",
        "wall_key": "wall_s",
        "shape": "`<prose>: k=v; k=v; ...` (heat-transfer's fourth shape, 26,757 "
                 "core-min, invisible to cfd's rule alone)",
    },
}

# The prose-fabrication fixture: a REAL file with no rc record whose sentence contains
# `rc=0,`.  Any reader that reports an rc for it is inventing one.
PROSE_FIXTURE = "verification/runs/T-family/T5_runs/DONE.T5_CUBE_c"


def _plant_token(text, key, value):
    """Rewrite `key=<value>` IN THE FILE'S OWN SHAPE.  Returns (text, n_replaced)."""
    pat = re.compile(r'((?:(?<=\s)|^)%s=)[^\s;]*' % re.escape(key), re.M)
    return pat.subn(lambda m: m.group(1) + str(value), text)


def _strip_token(text, key):
    """Delete `key=<value>` entirely -- the absent-key arm's blinding, done to REAL bytes."""
    pat = re.compile(r'(?:(?<=\s)|^)%s=[^\s;]*;?[ \t]?' % re.escape(key), re.M)
    return pat.subn("", text)


def _build_fixture(family, dest_dir, wall, rc, ranks=COST_PLANT_RANKS,
                   drop_wall=False, drop_ranks=False, source_override=None):
    """Write a fixture from a REAL sidecar's bytes.

    FAILS CLOSED: returns (None, refusal) if the real source is missing or does not carry
    the key the plant needs.  It never fabricates a template and never skips.
    """
    fam = PLANT_FAMILIES[family]
    src = source_override if source_override is not None else os.path.join(REPO, fam["source"])
    if not os.path.isfile(src):
        return None, ("FIXTURE MISSING: %s does not exist. The cost planted control "
                      "REFUSES rather than skipping -- a control that goes quiet when "
                      "its input vanishes is the failure it exists to catch." % src)
    try:
        with open(src, errors="replace") as fh:
            template = fh.read()
    except OSError as exc:
        return None, "FIXTURE UNREADABLE: %s (%s)" % (src, exc)

    text = template
    wk = fam["wall_key"]
    if drop_wall:
        text, n_wall = _strip_token(text, wk)
    else:
        text, n_wall = _plant_token(text, wk, wall)
    if n_wall < 1:
        return None, ("FIXTURE REFUSAL: the real template %s carries no %s= token, so "
                      "the plant could not be placed. Not worked around." % (src, wk))
    if drop_ranks:
        text, _ = _strip_token(text, "ranks")
    elif "ranks=" in template:
        text, _ = _plant_token(text, "ranks", ranks)
    for k in ("rc", "rc_solve"):
        if re.search(r'(?:(?<=\s)|^)%s=' % k, text):
            text, _ = _plant_token(text, k, rc)
    # core_min is a RECORDED key in some shapes; it must agree with the plant or the
    # read-back would silently prefer a stale figure over the planted wall.
    if re.search(r'(?:(?<=\s)|^)core_min=', text):
        eff_ranks = 1 if drop_ranks else ranks
        text, _ = _plant_token(text, "core_min", "%.6f" % (wall * eff_ranks / 60.0))

    os.makedirs(dest_dir, exist_ok=True)
    out = os.path.join(dest_dir, os.path.basename(src))
    with open(out, "w") as fh:
        fh.write(text)
    return out, None


def _read_plant_back(path, reader, expect_wall, expect_rc, expect_ranks,
                     expect_guard_clean=True):
    """Read the fixture back THROUGH THE PRODUCTION PATH -- read_cost_row() then
    summarise_cost() then cost_channel_guard() -- and return (ok, findings, row).

    Nothing here re-implements the reader.  `reader` is installed as the module-global
    `read_kv` that `read_cost_row` resolves, so a blinded reader blinds the PRODUCTION
    path itself and not a copy of it.
    """
    findings = []
    ok = True
    row = _with_reader(reader, lambda: read_cost_row(path))
    if not row["present"]:
        return False, ["fixture %s vanished before read-back" % path], row
    if row["wall_s"] is None or abs(row["wall_s"] - float(expect_wall)) > 1e-9:
        ok = False
        findings.append("wall read %r, plant was %s -- THE READER CANNOT SEE THE PLANT"
                        % (row["wall_s"], expect_wall))
    if expect_ranks is not None:
        if row["ranks"] is None or abs(row["ranks"] - float(expect_ranks)) > 1e-9:
            ok = False
            findings.append("ranks read %r, plant was %s" % (row["ranks"], expect_ranks))
    if expect_rc is not None and str(row["rc"]) != str(expect_rc):
        ok = False
        findings.append("rc read %r, plant was %r" % (row["rc"], expect_rc))
    exp_cm = float(expect_wall) * float(expect_ranks if expect_ranks else 1) / 60.0
    if row["core_min"] is None or abs(row["core_min"] - exp_cm) > 1e-3:
        ok = False
        findings.append("core_min read %r, plant implies %.6f" % (row["core_min"], exp_cm))
    cost = summarise_cost([row])
    if abs(cost["gross_core_min"] - (row["core_min"] or 0.0)) > 1e-9:
        ok = False
        findings.append("summarise_cost disagrees with the row it was given")
    guard = cost_channel_guard([row])
    if expect_guard_clean and guard:
        ok = False
        findings.append("cost_channel_guard REFUSED: " + "; ".join(guard))
    row["_guard"] = guard
    return ok, findings, row


def _with_reader(reader, fn):
    """Run fn() with the module-level read_kv temporarily replaced, restored in a
    finally so a failing arm cannot leave a caller holding a blinded reader."""
    g = globals()
    saved = g["read_kv"]
    g["read_kv"] = reader
    try:
        return fn()
    finally:
        g["read_kv"] = saved


def no_bare_assert_proof(path=None):
    """PARSE this file's AST and refuse if ANY `assert` statement exists in it."""
    src_path = path or os.path.abspath(__file__)
    try:
        with open(src_path) as fh:
            src = fh.read()
    except OSError as exc:
        return False, "cannot read own source %s (%s)" % (src_path, exc)
    try:
        tree = ast.parse(src, filename=src_path)
    except SyntaxError as exc:
        return False, "own source does not parse: %s" % exc
    bad = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if bad:
        return False, ("%d bare assert statement(s) at line(s) %s -- these VANISH under "
                       "python3 -O" % (len(bad), ", ".join(str(b) for b in bad)))
    return True, "0 ast.Assert nodes in %d AST nodes" % sum(1 for _ in ast.walk(tree))


def cost_plant_control(scratch, verbose=True, blind_production_reader=False):
    """The rule-3 planted control for heat-transfer's COST channel.

    `blind_production_reader` installs a PRE-REPAIR reader for the positive arms, which
    must make the control REFUSE -- so the refusal can be driven and seen to fire under
    both `python3` and `python3 -O`.
    """
    root = os.path.join(scratch, "cost_plant")
    os.makedirs(root, exist_ok=True)
    arms = []

    def note(name, kind, passed, detail):
        arms.append({"arm": name, "kind": kind, "passed": passed, "detail": detail})
        if verbose:
            print("  %-40s %-10s %-7s %s" % (name, kind, "OK" if passed else "FAILED",
                                             detail))

    ok_ast, ast_detail = no_bare_assert_proof()
    note("A0 no-bare-assert (AST parse)", "structure", ok_ast, ast_detail)

    # ---- FAIL-CLOSED ARM ------------------------------------------------------------
    bogus = os.path.join(root, "no_such_source_STATUS")
    if os.path.exists(bogus):
        os.remove(bogus)
    _, refusal = _build_fixture("one_line_multi_pair", os.path.join(root, "failclosed"),
                                COST_PLANT_WALL, COST_PLANT_RC_OK,
                                source_override=bogus)
    note("F1 fixture-missing fails CLOSED", "failclosed", refusal is not None,
         (refusal or "NO REFUSAL -- the control would have skipped")[:110])

    reader = _reader_prerepair_perline if blind_production_reader else read_kv

    # ---- POSITIVE ARMS: one per REAL on-disk shape ----------------------------------
    positives = [
        # (arm, family, rc plant, does the shape carry a bare `rc` record?)
        ("P1 one-pair-per-line, rc=0", "one_pair_per_line", COST_PLANT_RC_OK, True),
        ("P2 one-line multi-pair, rc=0", "one_line_multi_pair", COST_PLANT_RC_OK, True),
        ("P3 one-line multi-pair, rc=137", "one_line_multi_pair",
         COST_PLANT_RC_NONZERO, True),
        # P4's template, DONE.R_ff, carries NO bare `rc` -- only `checkmesh_rc` and
        # `decomposepar_rc`.  That is a fact about the file, not a weakening of the arm:
        # the arm proves the PARSE sees the planted wall/ranks/core_min in the semicolon
        # shape, and arm N7 below proves the guard REFUSES that same file for its missing
        # rc.  Claiming an rc here would be inventing one, which is the failure N3 exists
        # to catch.
        ("P4 semicolon record (wall/ranks/core_min)", "semicolon_record",
         COST_PLANT_RC_OK, False),
    ]
    for name, family, rc, has_rc in positives:
        dest = os.path.join(root, name.split()[0])
        got, refusal = _build_fixture(family, dest, COST_PLANT_WALL, rc)
        if refusal:
            note(name, "positive", False, refusal[:110])
            continue
        expect_ranks = COST_PLANT_RANKS if "ranks=" in open(got).read() else None
        ok, findings, row = _read_plant_back(got, reader, COST_PLANT_WALL,
                                             rc if has_rc else None, expect_ranks,
                                             expect_guard_clean=has_rc)
        note(name, "positive", ok,
             ("saw wall=%d ranks=%s%s -> %.4f core-min (%s)"
              % (COST_PLANT_WALL, row["ranks"],
                 " rc=%s" % row["rc"] if has_rc else " (no rc record in this shape)",
                 row["core_min"], PLANT_FAMILIES[family]["shape"]))
             if ok else "; ".join(findings)[:200])

    # ---- NEGATIVE ARMS: a blinded reader MUST be caught -----------------------------
    dest = os.path.join(root, "N")
    got, refusal = _build_fixture("one_line_multi_pair", dest, COST_PLANT_WALL,
                                  COST_PLANT_RC_OK)
    if refusal:
        note("N1/N2/N4 negative arms", "negative", False, refusal[:110])
    else:
        expect_ranks = COST_PLANT_RANKS if "ranks=" in open(got).read() else None
        blinds = [
            ("N1 pre-repair per-line reader", _reader_prerepair_perline),
            ("N2 pre-repair findall reader", _reader_prerepair_findall),
            ("N4 reader hard-wired to zero", _reader_constant_zero),
        ]
        for nname, blind in blinds:
            ok, findings, _ = _read_plant_back(got, blind, COST_PLANT_WALL,
                                               COST_PLANT_RC_OK, expect_ranks)
            note(nname, "negative", (not ok),
                 ("CAUGHT: " + "; ".join(findings)[:150]) if not ok
                 else "NOT CAUGHT -- the control cannot say `false` and is worthless")

    # N3: the UNANCHORED reader inventing an rc out of prose.  The production reader must
    # report no rc for this REAL file and the guard must refuse; the unanchored one must
    # report an rc, which is the fabrication.
    prose = os.path.join(REPO, PROSE_FIXTURE)
    if not os.path.isfile(prose):
        note("N3 unanchored reader invents rc", "negative", False,
             "FIXTURE MISSING: %s -- refusing rather than skipping" % prose)
    else:
        row_true = read_cost_row(prose)
        row_fab = _with_reader(_reader_unanchored_token,
                               lambda: read_cost_row(prose))
        caught = (not row_true["rc_key_present"]) and row_fab["rc_key_present"] \
            and bool(cost_channel_guard([row_true]))
        note("N3 unanchored reader invents rc", "negative", caught,
             ("CAUGHT: this rule reports rc=%r (no record) and REFUSES; the unanchored "
              "reader reports rc=%r out of the sentence in %s"
              % (row_true["rc"], row_fab["rc"], PROSE_FIXTURE))
             if caught else
             "NOT CAUGHT -- prose fabrication is indistinguishable from a record here")

    # N5: a REAL sidecar with the wall key REMOVED.  The parse is fine; the figure a
    # caller would report is a DEFAULT, and the guard must refuse.
    dest5 = os.path.join(root, "N5")
    got5, refusal = _build_fixture("one_line_multi_pair", dest5, COST_PLANT_WALL,
                                   COST_PLANT_RC_OK, drop_wall=True)
    if refusal:
        note("N5 wall key removed", "negative", False, refusal[:110])
    else:
        g5 = cost_channel_guard([read_cost_row(got5)])
        note("N5 wall key removed", "negative", bool(g5),
             ("CAUGHT: " + g5[0][:140]) if g5
             else "NOT CAUGHT -- an absent key was reported as a measured 0.0")

    # N6: a REAL ranks=2 sidecar with the ranks key REMOVED.  wall is still readable, so
    # a caller WOULD produce a plausible number -- at half the true charge.
    dest6 = os.path.join(root, "N6")
    got6, refusal = _build_fixture("one_line_multi_pair", dest6, COST_PLANT_WALL,
                                   COST_PLANT_RC_OK, drop_ranks=True)
    if refusal:
        note("N6 ranks key removed (halves charge)", "negative", False, refusal[:110])
    else:
        r6 = read_cost_row(got6)
        g6 = cost_channel_guard([r6])
        # It is only a real trap if the sidecar HAS a derivable wall and no core_min.
        trap = (r6["wall_s"] is not None and not r6["core_min_key_present"])
        note("N6 ranks key removed (halves charge)", "negative",
             bool(g6) if trap else True,
             ("CAUGHT: " + g6[0][:140]) if g6
             else ("no trap: this shape records core_min directly, so ranks is not "
                   "load-bearing here" if not trap
                   else "NOT CAUGHT -- ranks=1 was assumed and the charge halved"))

    # N7: the semicolon record's OWN missing rc.  This is not a synthetic blinding -- it
    # is the real `DONE.R_ff`, the largest single cost record in this territory
    # (26,757 core-min), and it carries `checkmesh_rc` and `decomposepar_rc` but NO bare
    # `rc`.  The guard must refuse to sort its waste rather than reading one of the other
    # two as a solver status.  A REAL FINDING, surfaced by this control rather than
    # discovered later.
    real_rff = os.path.join(REPO, PLANT_FAMILIES["semicolon_record"]["source"])
    if not os.path.isfile(real_rff):
        note("N7 semicolon record has no rc", "negative", False,
             "FIXTURE MISSING: %s -- refusing rather than skipping" % real_rff)
    else:
        r7 = read_cost_row(real_rff)
        g7 = cost_channel_guard([r7])
        caught = bool(g7) and not r7["rc_key_present"] and r7["core_min"] is not None
        note("N7 semicolon record has no rc", "negative", caught,
             ("CAUGHT: DONE.R_ff reads %.3f core-min (wall_s=%s x ranks=%s) and the "
              "guard REFUSES its waste sort: %s"
              % (r7["core_min"], r7["wall_s"], r7["ranks"], g7[0][:90]))
             if caught else
             "NOT CAUGHT -- a cost record with no process status was reported as sortable")

    # ---- THE DECLARATION CHANNEL -----------------------------------------------------
    # 202 sidecars in this territory derive core-minutes from a wall with NO ranks key.
    # A caller that knows the rank count from a pre-registration may declare it; a caller
    # that merely assumes 1 may not.  The difference is the BASIS, and P5/N8 prove the
    # basis is load-bearing rather than decorative -- an unattributed declaration is
    # permission laundering on the cost channel (CLAUDE.md rule 9) and is refused.
    dest8 = os.path.join(root, "D")
    got8, refusal = _build_fixture("one_line_multi_pair", dest8, COST_PLANT_WALL,
                                   COST_PLANT_RC_OK, drop_ranks=True)
    if refusal:
        note("P5/N8 declaration arms", "structure", False, refusal[:110])
    else:
        good = read_cost_row(got8,
                             declared_ranks=(COST_PLANT_RANKS,
                                             "T-family cost-channel selftest fixture"))
        g_good = cost_channel_guard([good])
        ok5 = (not g_good) and good["ranks"] == float(COST_PLANT_RANKS) \
            and "DECLARED" in (good["ranks_basis"] or "")
        note("P5 ranks DECLARED with a basis", "positive", ok5,
             ("accepted and recorded: ranks=%s, basis %r, %.4f core-min"
              % (good["ranks"], good["ranks_basis"], good["core_min"]))
             if ok5 else "declaration with a basis was not honoured: %s" % (g_good or good))

        bad = read_cost_row(got8, declared_ranks=(COST_PLANT_RANKS, "   "))
        g_bad = cost_channel_guard([bad])
        ok8 = bool(g_bad) and bad["ranks"] is None
        note("N8 ranks declared with NO basis", "negative", ok8,
             ("CAUGHT: " + g_bad[0][:140]) if ok8
             else "NOT CAUGHT -- an unattributed declaration passed as a measurement")

    passed = all(a["passed"] for a in arms)
    result = {
        "control": "standing rule 3, planted control, COST channel (heat-transfer)",
        "plant_wall": COST_PLANT_WALL,
        "plant_ranks": COST_PLANT_RANKS,
        "fixture_sources": {k: v["source"] for k, v in PLANT_FAMILIES.items()},
        "prose_fixture": PROSE_FIXTURE,
        "read_back_through": "read_cost_row() + summarise_cost() + cost_channel_guard()"
                             " -- the production path",
        "production_reader_blinded": blind_production_reader,
        "optimised_interpreter": not __debug__,
        "arms": arms,
        "passed": passed,
    }
    if verbose:
        if passed:
            # Counted from the arms actually run.  A hard-coded tally inside a
            # measurement report is worse than a false one, because no input can
            # falsify it (cfd, b0ec4c60, deletion 2).
            n_pos = sum(1 for a in arms if a["kind"] == "positive")
            n_neg = sum(1 for a in arms if a["kind"] == "negative")
            print("COST PLANTED CONTROL PASSED: the reader was shown able to see a "
                  "planted wall=%d and ranks=%d on %d positive arms covering every real "
                  "on-disk shape in this territory, and %d blinded or blind-spot arms "
                  "were CAUGHT."
                  % (COST_PLANT_WALL, COST_PLANT_RANKS, n_pos, n_neg))
        else:
            print("REFUSED (exit %d): the cost channel is NOT trusted. Failing arms: %s"
                  % (EXIT_REFUSE, ", ".join(a["arm"] for a in arms if not a["passed"])),
                  file=sys.stderr)
    return result


def assert_cost_channel_armed(scratch, verbose=False):
    """THE ASSERT A CALL SITE INSERTS (CLAUDE.md rule 14).

    Runs the planted control before the caller is allowed to report a cost, and RAISES
    SystemExit(2) if any arm fails.  It is not an `assert` statement, so `python3 -O`
    cannot delete it.  Returns the control record so the caller can file it beside the
    figure it authorised.
    """
    rec = cost_plant_control(scratch, verbose=verbose)
    if not rec["passed"]:
        failed = ", ".join("%s (%s)" % (a["arm"], a["detail"])
                           for a in rec["arms"] if not a["passed"])
        raise SystemExit(
            "COST CHANNEL REFUSED (standing rule 3): the reader behind this figure has "
            "NOT been shown able to see a planted non-zero. No cost may be reported and "
            "no calibration row may be written. Failing arms: %s. The grade and the "
            "verdict above are unaffected -- bookkeeping never voids physics." % failed)
    return rec


# =====================================================================================
# NO-REGRESSION: every real sidecar in this territory, both legacy readers, this reader
# =====================================================================================

def iter_sidecars(root=None):
    root = root or REPO
    for tree in TREES:
        base = os.path.join(root, tree)
        if not os.path.isdir(base):
            continue
        for dp, _dns, fns in os.walk(base):
            for fn in fns:
                if fn.startswith(SIDECAR_PREFIX) or fn in SIDECAR_EXACT:
                    yield os.path.join(dp, fn)


_IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def _classify_lost_key(k, new):
    """A key present in a legacy parse and absent from this one: REAL LOSS or SUPERSEDED?

    A legacy key is SUPERSEDED -- and only then -- when it is not a valid identifier at
    all (it is a merge artifact: the legacy reader split on the first `=` and swallowed
    whatever preceded it), AND every `key=` token inside its own text is present in the
    repaired dict.  So the information the malformed key carried is provably still there,
    under its real names, before the malformed name is allowed to disappear.

    Anything else is a REAL LOSS and the no-regression run REFUSES on it.
    """
    if _IDENT.match(k):
        return "real_loss"
    inner = [m.group(1) for m in _KV_TOKEN.finditer(k + "=")]
    tail = k.split()[-1] if k.split() else k
    if _IDENT.match(tail) and tail in new:
        return "superseded"
    if inner and all(t in new for t in inner):
        return "superseded"
    return "real_loss"


def no_regression(verbose=True):
    """Prove branch (B) is byte-for-byte the legacy parse on every line that is not a
    record line, over EVERY real sidecar in this territory.

    REAL KEYS LOST must be 0 against BOTH pre-repair readers.  A malformed compound key
    the repair supersedes is counted and NAMED separately, never folded into "0 lost";
    it is only excused when the keys it had merged are provably present.  Keys gained are
    the repair.  Exceptions must be 0: a reader that throws on a real file is not a
    reader.
    """
    stats = {
        "files": 0, "exceptions": 0,
        "perline_lost": {}, "perline_superseded": {},
        "perline_gained": 0, "perline_changed_value": 0, "perline_merge_confirmed": 0,
        "findall_lost": {}, "findall_superseded": {},
        "findall_gained": 0, "findall_changed_value": 0, "findall_merge_confirmed": 0,
        "lines_A1": 0, "lines_A2": 0, "lines_legacy": 0, "lines_no_eq": 0,
        "cost_keys_recovered": {},
    }
    for p in iter_sidecars():
        stats["files"] += 1
        try:
            with open(p, errors="replace") as fh:
                text = fh.read()
            new = parse_kv_text(text)
            old1 = _reader_prerepair_perline(p)
            old2 = _reader_prerepair_findall(p)
        except Exception as exc:                       # noqa: BLE001 -- it is counted
            stats["exceptions"] += 1
            if verbose:
                print("  EXCEPTION on %s: %s" % (p, exc))
            continue
        for line in text.splitlines():
            s = line.strip()
            if "=" not in s:
                stats["lines_no_eq"] += 1
                continue
            toks = list(_KV_TOKEN.finditer(s))
            if len(toks) >= 2 and toks[0].start() == 0:
                stats["lines_A1"] += 1
            elif len(toks) >= 2 and _semicolon_run(s, toks):
                stats["lines_A2"] += 1
            else:
                stats["lines_legacy"] += 1
        for old, pfx in ((old1, "perline"), (old2, "findall")):
            for k in set(old) - set(new):
                bucket = ("%s_superseded" % pfx
                          if _classify_lost_key(k, new) == "superseded"
                          else "%s_lost" % pfx)
                stats[bucket][k] = stats[bucket].get(k, 0) + 1
            stats["%s_gained" % pfx] += len(set(new) - set(old))
            for k in set(old) & set(new):
                if old[k] == new[k]:
                    continue
                stats["%s_changed_value" % pfx] += 1
                # The claim behind every changed value is that the LEGACY value was a
                # MERGE: it began with the true value and ran on into the next pair.
                # Checked, not asserted.
                if old[k].startswith(new[k]) and "=" in old[k][len(new[k]):]:
                    stats["%s_merge_confirmed" % pfx] += 1
        for k in (set(new) - set(old1)) & set(COST_KEYS):
            stats["cost_keys_recovered"][k] = stats["cost_keys_recovered"].get(k, 0) + 1
    if verbose:
        print("NO-REGRESSION over %d real sidecars in %s" % (stats["files"], ", ".join(TREES)))
        print("  lines: (A1) %d  (A2) %d  legacy (B) %d  no `=` %d"
              % (stats["lines_A1"], stats["lines_A2"], stats["lines_legacy"],
                 stats["lines_no_eq"]))
        for pfx, label in (("perline", "PER-LINE"), ("findall", "FINDALL ")):
            print("  vs pre-repair %s reader: REAL keys lost %s"
                  % (label, stats["%s_lost" % pfx] or "NONE"))
            print("      superseded malformed keys (merge artifacts, their tokens "
                  "provably recovered): %s" % (stats["%s_superseded" % pfx] or "none"))
            print("      keys gained %d; values changed %d, of which %d confirmed to be "
                  "legacy MERGES"
                  % (stats["%s_gained" % pfx], stats["%s_changed_value" % pfx],
                     stats["%s_merge_confirmed" % pfx]))
        print("  cost keys recovered: %s" % (stats["cost_keys_recovered"] or "none"))
        print("  exceptions: %d" % stats["exceptions"])
    return stats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="run the rule-3 planted control on all arms")
    ap.add_argument("--no-regression", dest="noreg", action="store_true",
                    help="parse every real sidecar in this territory, both readers")
    ap.add_argument("--blind", action="store_true",
                    help="drive the refusal: install the pre-repair reader on the "
                         "POSITIVE arms, which must make the control REFUSE")
    ap.add_argument("--read", metavar="PATH", help="read one sidecar and print its row")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--scratch", default=os.environ.get(
        "COST_CHANNEL_SCRATCH",
        "/tmp/claude-1000/-home-ubuntu-Certonomous/cost_channel_scratch"))
    a = ap.parse_args(argv)

    if a.read:
        row = read_cost_row(a.read)
        print(json.dumps({"row": row, "guard": cost_channel_guard([row])}, indent=2))
        return 0 if not cost_channel_guard([row]) else EXIT_REFUSE

    rc = 0
    if a.noreg:
        st = no_regression(verbose=not a.json)
        bad = st["exceptions"] or st["perline_lost"] or st["findall_lost"] \
            or (st["perline_changed_value"] != st["perline_merge_confirmed"]) \
            or (st["findall_changed_value"] != st["findall_merge_confirmed"])
        if a.json:
            print(json.dumps(st, indent=2, default=str))
        if bad:
            print("NO-REGRESSION FAILED: a REAL key was lost, a value changed without "
                  "being a confirmed legacy merge, or a file threw.", file=sys.stderr)
            rc = EXIT_REFUSE
    if a.selftest or a.blind:
        print("=== standing rule 3, COST channel, planted control "
              "(%s interpreter)%s" % ("optimised" if not __debug__ else "plain",
                                      " -- BLIND DRIVE" if a.blind else ""))
        rec = cost_plant_control(a.scratch, verbose=True,
                                 blind_production_reader=a.blind)
        if a.blind:
            # The blind drive is a NEGATIVE run of the whole control: it MUST refuse.
            if rec["passed"]:
                print("BLIND DRIVE FAILED: the control passed with the PRE-REPAIR reader "
                      "installed on its positive arms. It cannot say `false`.",
                      file=sys.stderr)
                rc = EXIT_REFUSE
            else:
                print("BLIND DRIVE OK: the control REFUSED with the pre-repair reader "
                      "installed -- the refusal has been seen to fire.")
        elif not rec["passed"]:
            rc = EXIT_REFUSE
    if not (a.selftest or a.noreg or a.blind or a.read):
        ap.print_help()
    return rc


if __name__ == "__main__":
    sys.exit(main())
