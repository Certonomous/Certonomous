#!/usr/bin/env python3
"""SO-1bR -- G-SO1AR (the re-registered precondition) and G-PROV (the travelling
shipped-`GATE FAIL` provenance).  ONE FILE, so the thing the driver EXECUTES is
byte-identically the thing the selftest DRIVES.

WHY THIS FILE EXISTS AT ALL.  SO-1b's frozen chain driver evaluates its dependency
on SO-1a inside an INLINE HEREDOC (`so1b_chain_driver.sh:102-138`) that globs
`SO1a_grade_*.json` under SO-1a's run root and reads `gates.G5_PATCHED` from the
last match.  On 2026-08-28T02:31:50Z that branch fired for real and closed the item
at rc = 7 with the reading

    REFUSE no_gates.G5_PATCHED in=SO1a_grade_20260828T023132Z.json

-- recorded in `curriculum_SO1b/G_SO1A.20260828T023149Z.txt`.  The PRECONDITION IS
NOW SATISFIED IN SUBSTANCE: SO-1a's successor SO-1aR produced a grade artefact that
DOES carry `gates.G5_PATCHED`, reading `PASS` on both the objective gradient and the
constraint gradient.  But the frozen glob `SO1a_grade_*.json` CANNOT MATCH
`SO1aR_grade_*.json` -- the literal `_` after `SO1a` forbids it -- so relaunching
SO-1b unchanged fires the SAME no-launch branch into a GUARANTEED outcome.

THE FORBIDDEN REPAIR, NAMED SO IT IS NOT QUIETLY TAKEN.  Copying or renaming
SO-1aR's grade JSON to `SO1a_grade_*.json` would make a SUCCESSOR's verdict
masquerade as the ORIGINAL's inside a preserved artefact set.  That is evidence
tampering however well intentioned, and this module exists precisely so the repair
is a NEW REGISTERED INPUT rather than a renamed old one.  The input is therefore
pinned BY ABSOLUTE PATH AND BY MD5, and a moved md5 REFUSES.

=========================== G-PROV, AND IT IS THE POINT ===========================
SO-1bR's precondition keys on the PATCHED row, while the ITEM verdict of the upstream
item is `GATE FAIL`.  Building a downstream rung on the PASS row of a `GATE FAIL`
item IS legitimate -- the two-row structure exists precisely so the patched row can
carry work the shipped row cannot.  BUT THE SHIPPED `GATE FAIL` MUST TRAVEL WITH
EVERY DOWNSTREAM CLAIM.  No reader may pick up an SO-1bR result without also picking
up the fact that the SHIPPED toolchain FAILED the gradient that result rests on.

THAT REQUIREMENT IS ENFORCED IN CODE, NOT IN PROSE.  A requirement in prose has no
call sites (L-405's general form).  `require_travelling_provenance()` REFUSES to let
any verdict leave this instrument unless:

  (1) the structured `upstream_provenance` block is present in the output;
  (2) that block's SHIPPED row status is present AND reads exactly `GATE FAIL`;
  (3) the block carries the SHIPPED per-gate detail, not only the row word;
  (4) a human-readable `verdict_line` is present and CONTAINS the literal bytes
      `GATE FAIL`; and
  (5) `verdict_line` is BYTE-IDENTICAL to the bytes this module composed for it.

Clause (5) is not decoration.  On 2026-08-30 this lab lost the words `GATE FAIL`
from `docs/LAB_STATE.md` -- its only handoff channel between sessions -- because an
UNQUOTED heredoc command-substituted the backticked token to nothing (commit
`e779bdc7`), and a sibling defect ate a backticked `Queue:` line from a charter
(L-403).  The remedy landed as `scripts/append_block.py` (L-405): compare the LANDED
BYTES against the INTENDED BYTES.  This item's whole subject is a `GATE FAIL` that
must survive travel, so the same comparison is made here.

VOCABULARY, AND WHAT G-PROV DOES *NOT* DO.  Standing rule 1 fixes the verdict words.
`verdict` therefore stays exactly one of the six and is NEVER decorated.  The
provenance travels in a SEPARATE mandatory field and in `verdict_line`, which is a
ROW DESCRIPTION and not a new verdict word -- the construction the verification
supervisor ruled legitimate for SO-1aR's split verdict at `db0b0124`.

L-332: NO `assert` anywhere.  The module counts `ast.Assert` nodes in its own source
and refuses on any, so `python3 -O` cannot strip a check.
"""

import sys

# ABOVE ANY OTHER IMPORT.  A stale `.pyc` INVERTS mutation tests -- the clean control
# fails while the mutated case passes -- and `PYTHONDONTWRITEBYTECODE` does not cure
# it.  A sibling lane dropped a real `.pyc` into a frozen case directory tonight by
# setting this flag AFTER its imports.
sys.dont_write_bytecode = True

import ast          # noqa: E402
import glob         # noqa: E402
import hashlib      # noqa: E402
import json         # noqa: E402
import os           # noqa: E402

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md governs) -----------------------------
ITEM = "SO1bR"
UPSTREAM_ITEM = "CURRICULUM-SO1aR"

# THE REGISTERED INPUT, PINNED BY ABSOLUTE PATH AND BY MD5.
REGISTERED_INPUT = ("/home/ubuntu/certonomous-runs/"
                    "CURRICULUM-SO1a-a1-naca0012-dragmin-gradient/"
                    "SO1aR_grade_20260828T171830Z.json")
REGISTERED_INPUT_MD5 = "194c0440b8e36e8044795449c7df7edb"
REGISTERED_INPUT_BYTES = 49743

# The glob the FROZEN SO-1b driver uses (`so1b_chain_driver.sh:113`).  Kept here so
# the ruling -- that it CANNOT SEE the registered input -- is EXECUTED as a unit
# rather than restated as a claim.
FROZEN_SO1B_GLOB = "SO1a_grade_*.json"

# G-SO1AR's registered requirement, unchanged in SUBSTANCE from the frozen driver's
# G-SO1A: the PATCHED row's OBJECTIVE gradient (G5, dCD/dx) and its CONSTRAINT
# gradient (G5c, dCL/dx) must BOTH read PASS, on BOTH channels, and the two channels
# must agree.  Those are the two gradients a constrained optimiser consumes.
REQUIRED_PATCHED_GATE_VERDICT = "PASS"
REQUIRED_PATCHED_ROW_VERDICT = "PASS"

# G-PROV's registered requirement.  The upstream SHIPPED row status that must travel.
REQUIRED_SHIPPED_STATUS = "GATE FAIL"
PROVENANCE_TOKEN = "GATE FAIL"

# The fixed vocabulary (standing rule 1).  A verdict outside it REFUSES.
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# The SHIPPED per-gate detail G-PROV requires -- the row word alone is not enough,
# because "the shipped row failed" without its magnitude invites a reader to assume
# a marginal miss.  It was not marginal.
SHIPPED_GATES_REQUIRED = ("G5_CD", "G5c_CL")
SHIPPED_GATE_FIELDS_REQUIRED = ("verdict", "aggregate_rel_err_pct", "n_graded",
                                "n_pass", "sign_flips", "band_D", "band_E")


class Refusal(Exception):
    pass


def _local_refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str))


def count_asserts(path):
    return sum(1 for n in ast.walk(ast.parse(open(path).read()))
               if isinstance(n, ast.Assert))


def md5_file(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frozen_glob_can_see(input_path, root=None):
    """THE RULING, EXECUTED.  Does the FROZEN SO-1b driver's own glob match the
    registered input?  It must NOT: that is why SO-1bR exists.  Answering this by
    RUNNING the glob rather than by reading the pattern is the difference between a
    measurement and a claim about a string."""
    root = root or os.path.dirname(input_path)
    matches = sorted(glob.glob(os.path.join(root, FROZEN_SO1B_GLOB)))
    return {"root": root, "pattern": FROZEN_SO1B_GLOB,
            "matches": [os.path.basename(m) for m in matches],
            "registered_input": os.path.basename(input_path),
            "can_see_registered_input": input_path in matches}


def read_registered_input(path=None, md5_expected=None, refuse=None):
    """Load the registered input AFTER proving the file on disk is the file that was
    registered.  ABSENT refuses.  A MOVED md5 refuses.  UNREADABLE refuses.  There is
    no branch in which an unreadable dependency becomes a licence to proceed."""
    refuse = refuse or _local_refuse
    path = path or REGISTERED_INPUT
    md5_expected = md5_expected or REGISTERED_INPUT_MD5
    if not os.path.isfile(path):
        refuse("G-SO1AR", {"registered_input_absent": path,
                           "note": "the registered input is pinned by ABSOLUTE PATH; an "
                                   "absent dependency is a NO-LAUNCH, never a default"})
    got = md5_file(path)
    if got != md5_expected:
        refuse("G-SO1AR", {"registered_input_md5_moved": path,
                           "registered": md5_expected, "on_disk": got,
                           "note": "the input is pinned by md5 so a successor artefact "
                                   "cannot be swapped under a frozen registration"})
    try:
        with open(path) as fh:
            G = json.load(fh)
    except Exception as exc:                                        # noqa: BLE001
        refuse("G-SO1AR", {"registered_input_unreadable": path, "err": repr(exc)[:300]})
    if not isinstance(G, dict):
        refuse("G-SO1AR", {"registered_input_not_an_object": path, "type": type(G).__name__})
    return G, {"path": path, "md5": got, "bytes": os.path.getsize(path),
               "upstream_item": G.get("item")}


def _verdict_of(node):
    return node.get("verdict") if isinstance(node, dict) else node


def precondition(G, source, refuse=None):
    """G-SO1AR.  The frozen driver's registered question, asked of the registered
    input: is the PATCHED row PASS on BOTH G5 (dCD/dx) and G5c (dCL/dx)?

    THE READING IS TAKEN ON TWO CHANNELS -- the per-gate verdicts under
    `gates.G5_PATCHED` and the composed row verdict under `rows.PATCHED` -- and a
    DISAGREEMENT BETWEEN THE CHANNELS REFUSES.  That clause is inherited verbatim in
    SUBSTANCE from `so1b_chain_driver.sh:130-134`; nothing about the threshold, the
    composition or the required word is re-derived here.

    A STRUCTURALLY ABSENT CHANNEL REFUSES.  It never silently proceeds and it never
    silently degrades to the other channel -- an absent `gates.G5_PATCHED` is exactly
    the shape that closed SO-1b, and an absent `rows.PATCHED` is its twin."""
    refuse = refuse or _local_refuse
    gates = G.get("gates")
    if not isinstance(gates, dict):
        refuse("G-SO1AR", {"gates_absent_or_not_an_object": source,
                           "type": type(G.get("gates")).__name__})
    gp = gates.get("G5_PATCHED")
    if not isinstance(gp, dict):
        refuse("G-SO1AR", {"no_gates.G5_PATCHED": source,
                           "note": "this is the EXACT shape that closed SO-1b at rc=7 on "
                                   "2026-08-28T02:31:50Z; it refuses here too"})
    rows = G.get("rows")
    if not isinstance(rows, dict) or "PATCHED" not in rows:
        refuse("G-SO1AR", {"rows.PATCHED_absent": source,
                           "rows_seen": sorted(rows) if isinstance(rows, dict) else None,
                           "note": "the second channel is STRUCTURAL, not optional; its "
                                   "absence refuses rather than falling back to the first"})
    g5 = _verdict_of(gp.get("G5_CD"))
    g5c = _verdict_of(gp.get("G5c_CL"))
    if g5 is None or g5c is None:
        refuse("G-SO1AR", {"patched_gate_verdict_absent": source,
                           "G5_CD": g5, "G5c_CL": g5c})
    row_gate = gp.get("row_verdict")
    row_top = rows.get("PATCHED")
    if row_gate != row_top:
        refuse("G-SO1AR", {"channel_disagreement": source,
                           "gates.G5_PATCHED.row_verdict": row_gate,
                           "rows.PATCHED": row_top,
                           "note": "two channels that disagree mean the artefact is not "
                                   "the one this branch was registered against"})
    for word in (g5, g5c, row_gate):
        if word not in VOCAB:
            refuse("G-SO1AR", {"upstream_word_outside_the_fixed_vocabulary": word,
                               "vocabulary": list(VOCAB), "source": source})
    ok = (g5 == REQUIRED_PATCHED_GATE_VERDICT
          and g5c == REQUIRED_PATCHED_GATE_VERDICT
          and row_gate == REQUIRED_PATCHED_ROW_VERDICT)
    return {"decision": "PROCEED" if ok else "REFUSE",
            "source": source, "upstream_item": G.get("item"),
            "upstream_item_verdict": G.get("verdict"),
            "G5_CD_PATCHED": g5, "G5c_CL_PATCHED": g5c,
            "row_PATCHED_gate_channel": row_gate, "row_PATCHED_top_channel": row_top,
            "channels_agree": True,
            "why": ("the PATCHED row is PASS on BOTH the objective gradient and the "
                    "equality-constraint gradient, on both channels"
                    if ok else
                    "the PATCHED row is NOT PASS on both G5 (dCD/dx) and G5c (dCL/dx); "
                    "the registered NO-LAUNCH branch closes the item at ZERO core-minutes")}


def shipped_provenance(G, source, refuse=None):
    """G-PROV, THE CONSTRUCTION STEP.  Build the block that MUST travel.

    REFUSES if the SHIPPED row status is absent, if the SHIPPED per-gate detail is
    absent, or if the row status is present but is not the registered upstream word.
    A stripped shipped row is the single most dangerous mutation this instrument can
    meet, because everything downstream would still compute correctly -- it would
    simply stop telling the reader what the result rests on."""
    refuse = refuse or _local_refuse
    rows = G.get("rows")
    if not isinstance(rows, dict) or "SHIPPED" not in rows:
        refuse("G-PROV", {"shipped_row_status_absent": source,
                          "rows_seen": sorted(rows) if isinstance(rows, dict) else None,
                          "note": "no SO-1bR verdict may be emitted without the upstream "
                                  "SHIPPED row status travelling beside it"})
    shipped_row = rows.get("SHIPPED")
    if shipped_row != REQUIRED_SHIPPED_STATUS:
        refuse("G-PROV", {"shipped_row_status_not_the_registered_word": shipped_row,
                          "registered": REQUIRED_SHIPPED_STATUS, "source": source,
                          "note": "the registration asserts the upstream SHIPPED row is "
                                  "GATE FAIL; a different word means this is not the "
                                  "artefact SO-1bR was registered against"})
    gates = G.get("gates") or {}
    gs = gates.get("G5_SHIPPED")
    if not isinstance(gs, dict):
        refuse("G-PROV", {"gates.G5_SHIPPED_absent": source,
                          "note": "the row word alone is not enough: without its magnitude "
                                  "a reader may assume a marginal miss.  It was not marginal"})
    detail = {}
    for gname in SHIPPED_GATES_REQUIRED:
        node = gs.get(gname)
        if not isinstance(node, dict):
            refuse("G-PROV", {"shipped_gate_detail_absent": gname, "source": source})
        missing = [f for f in SHIPPED_GATE_FIELDS_REQUIRED if f not in node]
        if missing:
            refuse("G-PROV", {"shipped_gate_fields_absent": gname, "missing": missing,
                              "source": source})
        detail[gname] = {f: node[f] for f in SHIPPED_GATE_FIELDS_REQUIRED}
        worst = None
        for comp in (node.get("components") or []):
            if not isinstance(comp, dict) or "rel_err_pct" not in comp:
                continue
            if worst is None or float(comp["rel_err_pct"]) > float(worst["rel_err_pct"]):
                worst = comp
        if worst is None:
            refuse("G-PROV", {"shipped_gate_components_absent": gname, "source": source})
        detail[gname]["worst_component"] = {
            "dv": worst.get("dv"), "idx": worst.get("idx"),
            "rel_err_pct": worst.get("rel_err_pct"),
            "sign_flip": worst.get("sign_flip"), "verdict": worst.get("verdict")}
        detail[gname]["components_failing_band_D"] = [
            {"dv": c.get("dv"), "idx": c.get("idx"), "rel_err_pct": c.get("rel_err_pct"),
             "sign_flip": c.get("sign_flip")}
            for c in (node.get("components") or [])
            if isinstance(c, dict) and c.get("verdict") != "PASS"]
    return {"upstream_item": G.get("item"), "upstream_source": source,
            "upstream_item_verdict": G.get("verdict"),
            "rows": {"SHIPPED": shipped_row, "PATCHED": rows.get("PATCHED")},
            "G5_SHIPPED": detail,
            "what_this_result_rests_on": (
                "SO-1bR rests on the PATCHED row of an item whose ITEM verdict is "
                "GATE FAIL.  The SHIPPED toolchain FAILED the gradient this result "
                "rests on.  The two-row structure makes that legitimate; it does not "
                "make it omissible.")}


def compose_verdict_line(verdict, prov):
    """The mandatory display sentence.  A ROW DESCRIPTION, never a verdict word.

    Composed HERE, in Python, from the block -- never assembled by a shell, and never
    interpolated into a heredoc.  `verdict_line` is compared BYTE-FOR-BYTE against
    this composition before any emit is allowed, so a token lost in transit is a
    REFUSAL rather than a quieter record."""
    g5 = prov["G5_SHIPPED"]["G5_CD"]
    g5c = prov["G5_SHIPPED"]["G5c_CL"]
    worst = g5["worst_component"]
    return ("SO1bR %s -- RESTS ON THE PATCHED ROW OF %s, WHOSE ITEM VERDICT IS %s "
            "AND WHOSE SHIPPED ROW IS %s: G5_CD %s %d/%d aggregate %.4f%% with %d "
            "sign flip(s), G5c_CL %s %d/%d aggregate %.4f%%, worst component %s[%s] "
            "at %.4f%% sign_flip=%s.  THE SHIPPED TOOLCHAIN FAILED THE GRADIENT THIS "
            "RESULT RESTS ON."
            % (verdict, prov["upstream_item"], prov["upstream_item_verdict"],
               prov["rows"]["SHIPPED"],
               g5["verdict"], g5["n_pass"], g5["n_graded"],
               float(g5["aggregate_rel_err_pct"]), g5["sign_flips"],
               g5c["verdict"], g5c["n_pass"], g5c["n_graded"],
               float(g5c["aggregate_rel_err_pct"]),
               worst["dv"], worst["idx"], float(worst["rel_err_pct"]),
               worst["sign_flip"]))


def require_travelling_provenance(out, refuse=None):
    """G-PROV, THE ENFORCEMENT STEP -- AND IT IS THE CALL SITE.

    No verdict leaves this instrument without its upstream provenance.  Called on the
    output object immediately before it is written, so the requirement cannot be met
    by intention: it is met by the bytes or the emit REFUSES.

    Returns `out` unchanged on success so it can wrap an emit expression directly and
    cannot be forgotten by a caller who merely calls it and drops the result."""
    refuse = refuse or _local_refuse
    verdict = out.get("verdict")
    if verdict not in VOCAB:
        refuse("G-PROV", {"verdict_outside_the_fixed_vocabulary": verdict,
                          "vocabulary": list(VOCAB)})
    prov = out.get("upstream_provenance")
    if not isinstance(prov, dict):
        refuse("G-PROV", {"verdict_without_upstream_provenance": verdict,
                          "note": "the requirement is a CALL SITE, not a footnote: a "
                                  "verdict with no provenance block does not get emitted"})
    rows = prov.get("rows")
    if not isinstance(rows, dict) or "SHIPPED" not in rows:
        refuse("G-PROV", {"provenance_block_without_shipped_row_status": verdict})
    if rows.get("SHIPPED") != REQUIRED_SHIPPED_STATUS:
        refuse("G-PROV", {"provenance_shipped_row_status_wrong": rows.get("SHIPPED"),
                          "registered": REQUIRED_SHIPPED_STATUS})
    gs = prov.get("G5_SHIPPED")
    if not isinstance(gs, dict) or any(g not in gs for g in SHIPPED_GATES_REQUIRED):
        refuse("G-PROV", {"provenance_block_without_shipped_gate_detail":
                          sorted(gs) if isinstance(gs, dict) else None,
                          "required": list(SHIPPED_GATES_REQUIRED)})
    line = out.get("verdict_line")
    if not isinstance(line, str) or not line:
        refuse("G-PROV", {"verdict_line_absent": verdict,
                          "note": "the human-readable channel is mandatory; a reader who "
                                  "sees only the verdict word must still see the upstream "
                                  "failure"})
    if PROVENANCE_TOKEN not in line:
        refuse("G-PROV", {"provenance_token_lost_from_verdict_line": PROVENANCE_TOKEN,
                          "verdict_line": line[:400],
                          "note": "this is the UNQUOTED-HEREDOC shape: on 2026-08-30 this "
                                  "lab lost the words GATE FAIL from docs/LAB_STATE.md "
                                  "because a backticked token was command-substituted to "
                                  "nothing (commit e779bdc7).  A token that vanished in "
                                  "transit refuses here"})
    intended = compose_verdict_line(verdict, prov)
    if line.encode("utf-8") != intended.encode("utf-8"):
        refuse("G-PROV", {"verdict_line_bytes_differ_from_the_intended_bytes": True,
                          "landed": line[:400], "intended": intended[:400],
                          "note": "L-405's remedy, applied here: the LANDED bytes are "
                                  "compared against the INTENDED bytes, because a write "
                                  "whose visible substitutions worked can still be corrupt"})
    return out


def evaluate(input_path=None, input_md5=None, refuse=None):
    """The whole precondition, end to end, for the driver AND for the grader.

    Returns a dict carrying the G-SO1AR decision and the G-PROV block.  Every failure
    path raises; there is no path that returns a soft answer."""
    G, src = read_registered_input(input_path, input_md5, refuse=refuse)
    name = os.path.basename(src["path"])
    pre = precondition(G, name, refuse=refuse)
    prov = shipped_provenance(G, name, refuse=refuse)
    return {"item": ITEM, "input": src, "G_SO1AR": pre, "upstream_provenance": prov,
            "frozen_so1b_glob": frozen_glob_can_see(src["path"])}


def main(argv):
    """Driver entry point.  Prints ONE line the driver's `case` statement reads, then
    the full reading as JSON on the following lines.  Exit 0 on PROCEED, 7 on the
    registered NO-LAUNCH branch, 4 on a refusal."""
    try:
        r = evaluate()
    except Refusal as ex:
        print("REFUSE %s" % str(ex))
        return 4
    dec = r["G_SO1AR"]["decision"]
    prov = r["upstream_provenance"]
    print("%s item=%s input=%s md5=%s G5_CD=%s G5c_CL=%s row_PATCHED=%s "
          "upstream_item_verdict=%s upstream_row_SHIPPED=%s"
          % (dec, r["item"], os.path.basename(r["input"]["path"]), r["input"]["md5"],
             r["G_SO1AR"]["G5_CD_PATCHED"], r["G_SO1AR"]["G5c_CL_PATCHED"],
             r["G_SO1AR"]["row_PATCHED_gate_channel"],
             prov["upstream_item_verdict"], prov["rows"]["SHIPPED"]))
    print(json.dumps(r, sort_keys=True, indent=2, default=str))
    if dec != "PROCEED":
        return 7
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
