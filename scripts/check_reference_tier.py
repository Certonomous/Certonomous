#!/usr/bin/env python3
"""Reference-tier gate -- no page shows a completed 3D case above its true reference tier.

Sanaa 2026-09-09 (direct): every completed 3D case is classified by its REFERENCE STRENGTH
(a different axis from the geometric building-block tier in validation_tiers.json) BEFORE any
page shows it; nothing is shown above its true tier; this is a GATE binding the demo and
credential surfaces.

The frozen evidentiary content is  verification/credibility/reference_tier_registry.json  (the
tier of each case is fixed there BEFORE any page is scanned, so a page cannot pick the tier that
flatters it -- rule 2). The companion prose is  verification/credibility/REFERENCE_TIER_STANDARD.md .

The gate scans the display/credential surfaces named in the registry and REFUSES (exit 2) on:
  1. OVER-CLAIM              -- a case shown with an asserted, non-negated claim of a tier ordinally
                                ABOVE its registered tier.
  2. BOUNDED-AGREEMENT       -- a bounded-agreement case shown with an experiment comparison but
     WITHOUT its band          without its explicit band string in the same block.
  3. MISSING CAVEAT          -- an experiment-validated case with a mandatory caveat (A3 shock-offset)
                                shown as validated without it; or a code-/method-verified case shown
                                with a positive/experiment claim and NO disavowal in its section.
  4. DIMENSION LEAK          -- an excluded 2D/axisymmetric id (A1 NACA0012, T23, T24, any VMFL) inside
                                a 3D listing (3D heading or a line carrying a 3D cue).
  5. REGISTRY DRIFT          -- a completed 3D case is not fully classified in the frozen registry
     (fail-closed)            (missing tier or evidence). An unclassified case may not be shown.

CLAIM-READING is a heuristic on prose (limits disclosed in the standard, section 5): a tier ABOVE
method-verified is read as CLAIMED only when an assertion cue ("graded against", "validated against",
"reproduces", ...) co-occurs with a reference token that is NOT negated in its immediate lead-in.
A generic description of what a reference body is does not, by itself, assert that our result was
validated -- this keeps honest disavowals ("no wind-tunnel data", "self-consistency, not validation")
from reading as claims.

PLANTED-ZERO CONTROL (rule 3): --selftest builds temp surfaces, injects (a) a synthetic over-claim
beside a code-verified id and (b) an excluded id inside a synthetic 3D list, and drives THIS FILE's
entry point RED-then-GREEN through those temp surfaces. A zero from a blind scanner is not evidence:
the gate will not certify a clean pass unless both plants are caught. The control is exit-code driven
(no assert carries control logic), so behaviour is byte-identical under `python3 -O` (L-332).

FREEZE (rule 2): once the registry is committed, pass --require-freeze to hard-refuse if the on-disk
registry differs from its committed blob. Before the supervisor commits it (working-tree draft) the
freeze is reported as PENDING, not enforced.

Exit codes:  0 = PASS / clean ;  2 = GATE FAIL (a refusal) ;  3 = selftest control did not fire.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

EXIT_OK, EXIT_REFUSE, EXIT_SELFTEST_FAIL = 0, 2, 3

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_REGISTRY = os.path.join(
    REPO_ROOT, "verification", "credibility", "reference_tier_registry.json")

# Concrete disavowal phrases that satisfy the "not experiment-validated" requirement for a
# code-/method-verified case presented on a page. Any one, present in the case's SECTION, discharges
# the disavowal requirement (a sheet-wide disclaimer covers the sheet).
DISAVOWAL_PHRASES = [
    "not validated", "self-consistency", "no wind tunnel", "no wind-tunnel",
    "no experimental", "no test data", "not against experiment", "code-verified",
    "code verified", "reproduces the tutorial", "tutorial baseline", "no comparison",
    "no wind tunnel data exists", "nothing here is validated", "not a validation",
    "no validation", "solver-backed, not validated",
]

NEG_LEAD_SPAN = 60    # chars of lead-in searched for a negation cue in front of a reference token
ASSERT_SPAN = 90      # chars on each side of a reference token searched for an assertion cue


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
def load_registry(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def _alias_regex(alias: str) -> re.Pattern:
    # whole-token match on lowercased text; alnum boundary so 'sail' does not match 'sailing'.
    return re.compile(r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])")


def build_index(reg: dict):
    tier_ranks = reg["tier_ranks"]
    det = reg["detector"]
    detector = {
        "assertion_cues": [c.lower() for c in det["assertion_cues"]],
        "experiment_tokens": [t.lower() for t in det["experiment_tokens"]],
        "code_tokens": [t.lower() for t in det["code_tokens"]],
        "negation_cues": [n.lower() for n in det["negation_cues"]],
        "band_res": [re.compile(rx) for rx in det["band_regexes"]],
        # 3D cues matched as WHOLE WORDS, never substrings -- a substring '3d' matches hex blob
        # hashes ('c03d285...') and page ranges, which are not 3D listings.
        "three_d_res": [re.compile(r"(?<![a-z0-9])" + re.escape(c.lower()) + r"(?![a-z0-9])")
                        for c in det["three_d_listing_cues"]],
    }
    cases = []
    for c in reg["cases"]:
        cases.append({
            "case_id": c["case_id"],
            "tier": c["tier"],
            "tier_rank": c["tier_rank"],
            "aliases": [(_alias_regex(a), a) for a in c["display_aliases"]],
            "required_caveat_tokens": [t.lower() for t in c.get("required_caveat_tokens", [])],
            "required_disavowal": bool(c.get("required_disavowal", False)),
        })
    excluded = []
    for e in reg["exclusions_not_applicable_dimension"]:
        mats = [(_alias_regex(a), e["case_id"]) for a in e.get("display_aliases", [])]
        for rx in e.get("alias_regexes", []):
            mats.append((re.compile(rx.lower()), e["case_id"]))
        excluded.extend(mats)
    scan = reg["scan"]
    return tier_ranks, detector, cases, excluded, scan, reg["completed_3d_case_ids"]


# --------------------------------------------------------------------------
# claim reading
# --------------------------------------------------------------------------
def _negated_before(text_lower: str, pos: int, neg_cues) -> bool:
    seg = text_lower[max(0, pos - NEG_LEAD_SPAN):pos]
    return any(n in seg for n in neg_cues)


def _asserted_claim(text_lower: str, tokens, assertion_cues, neg_cues):
    """A reference token forms a CLAIM only when it is (i) not negated in its lead-in AND
    (ii) has an assertion cue WITHIN ASSERT_SPAN chars on either side. Proximity matters:
    an assertion cue elsewhere in the window must not pair with an unrelated reference token
    (e.g. a code claim's 'reproduces' must not pair with generic 'Experimental information...'
    ceiling boilerplate). Returns (found, token)."""
    for tok in tokens:
        start = 0
        while True:
            i = text_lower.find(tok, start)
            if i < 0:
                break
            if not _negated_before(text_lower, i, neg_cues):
                seg = text_lower[max(0, i - ASSERT_SPAN): i + len(tok) + ASSERT_SPAN]
                if any(c in seg for c in assertion_cues):
                    return True, tok
            start = i + 1
    return False, None


def classify_block(block_text: str, detector: dict) -> dict:
    tl = block_text.lower()
    exp_claim, exp_tok = _asserted_claim(
        tl, detector["experiment_tokens"], detector["assertion_cues"], detector["negation_cues"])
    code_claim, code_tok = _asserted_claim(
        tl, detector["code_tokens"], detector["assertion_cues"], detector["negation_cues"])
    has_band = any(rx.search(block_text) for rx in detector["band_res"])
    claimed_rank, claimed_tier, claim_tok = None, None, None
    if exp_claim:
        if has_band:
            claimed_rank, claimed_tier = 3, "bounded-agreement"
        else:
            claimed_rank, claimed_tier = 4, "experiment-validated"
        claim_tok = exp_tok
    elif code_claim:
        claimed_rank, claimed_tier, claim_tok = 2, "code-verified", code_tok
    return {
        "exp_claim": exp_claim, "exp_tok": exp_tok, "code_claim": code_claim,
        "code_tok": code_tok, "has_band": has_band,
        "claimed_rank": claimed_rank, "claimed_tier": claimed_tier, "claim_tok": claim_tok,
    }


def section_has_disavowal(section_text: str) -> bool:
    sl = section_text.lower()
    return any(p in sl for p in DISAVOWAL_PHRASES)


# --------------------------------------------------------------------------
# surface enumeration + windowing
# --------------------------------------------------------------------------
def surface_files(root_dir: str, scan: dict, scan_dir_mode: bool):
    """Yield absolute paths of surfaces under root_dir."""
    include = tuple(scan["include_ext"])
    excl = scan["exclude_glob_substrings"]
    selfx = set(scan["self_exclude_basenames"])
    if scan_dir_mode:
        roots = [root_dir]
    else:
        roots = [os.path.join(root_dir, r) for r in scan["surface_roots"]]
    seen = set()
    for base in roots:
        if not os.path.isdir(base):
            continue
        for dp, _dn, fns in os.walk(base):
            for fn in fns:
                if not fn.endswith(include):
                    continue
                if fn in selfx:
                    continue
                ap = os.path.join(dp, fn)
                rel = os.path.relpath(ap, root_dir)
                if any(x in "/" + rel for x in excl):
                    continue
                # docs/campaigns: only the /demo/ subtree is a display surface
                if (not scan_dir_mode) and "docs/campaigns/" in ("/" + rel) and "/demo/" not in ("/" + rel):
                    continue
                if ap in seen:
                    continue
                seen.add(ap)
                yield ap


def _line_of(raw: str, needle_lower: str) -> int:
    low = raw.lower()
    i = low.find(needle_lower)
    if i < 0:
        return 1
    return raw.count("\n", 0, i) + 1


def text_blocks(raw: str):
    """Blank-line delimited blocks with their start line and enclosing section text."""
    lines = raw.split("\n")
    # section boundaries: headings split the file into sections
    def is_heading(line: str):
        s = line.strip()
        if s.startswith("#"):
            return True
        if re.search(r"<h[1-6][ >]", s, re.I):
            return True
        if re.search(r"\\(section|subsection|subsubsection|paragraph)\b", s):
            return True
        return False
    # precompute section index per line
    sec_id = [0] * len(lines)
    cur = 0
    for i, ln in enumerate(lines):
        if is_heading(ln):
            cur += 1
        sec_id[i] = cur
    section_text = {}
    for i, ln in enumerate(lines):
        section_text.setdefault(sec_id[i], []).append(ln)
    section_text = {k: "\n".join(v) for k, v in section_text.items()}
    # blocks
    blocks = []
    buf, start = [], None
    for i, ln in enumerate(lines):
        if ln.strip() == "":
            if buf:
                blocks.append((start + 1, "\n".join(buf), section_text[sec_id[start]]))
                buf, start = [], None
            continue
        if not buf:
            start = i
        buf.append(ln)
    if buf:
        blocks.append((start + 1, "\n".join(buf), section_text[sec_id[start]]))
    return blocks


def json_windows(raw: str):
    """For JSON, group each dict's immediate string values into one window (so a case's basis and
    id travel together). Yields (line, window_text, section_text==window_text)."""
    try:
        obj = json.loads(raw)
    except Exception:
        return
    out = []

    def walk(node):
        if isinstance(node, dict):
            strs = [v for v in node.values() if isinstance(v, str)]
            if strs:
                win = "  ".join(strs)
                # anchor the line on the longest string that occurs exactly ONCE in the file
                # (the entry's own distinctive prose, e.g. its basis), so a citation points at the
                # offending line, not a duplicated id or shared boilerplate.
                raw_low = raw.lower()
                uniq = [s for s in strs if len(s) > 15 and raw_low.count(s.lower()) == 1]
                anchor = max(uniq, key=len) if uniq else (max(strs, key=len) if strs else "")
                line = _line_of(raw, anchor.lower()[:60]) if anchor else 1
                out.append((line, win, win))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(obj)
    return out


# --------------------------------------------------------------------------
# dimension-leak pass
# --------------------------------------------------------------------------
def scan_dimension_leaks(raw: str, path: str, excluded, three_d_res):
    lines = raw.split("\n")

    def is_heading(line: str):
        s = line.strip()
        return (s.startswith("#") or bool(re.search(r"<h[1-6][ >]", s, re.I))
                or bool(re.search(r"\\(section|subsection|subsubsection|paragraph)\b", s)))

    def has_3d(text_lower: str) -> bool:
        return any(rx.search(text_lower) for rx in three_d_res)

    leaks = {}
    in_3d = False
    for ln_no, line in enumerate(lines, 1):
        ll = line.lower()
        if is_heading(line):
            in_3d = has_3d(ll)
        if in_3d or has_3d(ll):
            for matcher, case_id in excluded:
                if matcher.search(ll):
                    leaks.setdefault((ln_no, case_id), line.strip()[:120])
    return [(ln, cid, snip) for (ln, cid), snip in leaks.items()]


# --------------------------------------------------------------------------
# grade
# --------------------------------------------------------------------------
def grade(root_dir: str, reg: dict, scan_dir_mode: bool):
    tier_ranks, detector, cases, excluded, scan, completed = build_index(reg)
    refusals = []
    sidecar = []

    # registry drift (fail-closed): every completed 3D case fully classified.
    classified = {c["case_id"] for c in reg["cases"] if c.get("tier") and c.get("evidence")}
    for cid in completed:
        if cid not in classified:
            refusals.append({
                "rule": "registry-drift", "case_id": cid, "path": os.path.basename(DEFAULT_REGISTRY),
                "line": 0, "detail": "completed 3D case not fully classified (tier+evidence) in the "
                                     "frozen registry -- fail closed, may not be shown."})

    n_surfaces = 0
    n_mentions = 0
    for ap in surface_files(root_dir, scan, scan_dir_mode):
        n_surfaces += 1
        try:
            with open(ap, encoding="utf-8", errors="replace") as f:
                raw = f.read()
        except Exception:
            continue
        rel = os.path.relpath(ap, root_dir)

        # dimension leaks (line-oriented, all file types)
        for ln_no, case_id, snippet in scan_dimension_leaks(raw, ap, excluded, detector["three_d_res"]):
            refusals.append({
                "rule": "dimension-leak", "case_id": case_id, "path": rel, "line": ln_no,
                "detail": f"excluded 2D/axisymmetric id in a 3D listing: {snippet!r}"})

        # claim windows
        if ap.endswith(".json"):
            windows = json_windows(raw) or []
        else:
            windows = text_blocks(raw)

        for (line, block, section) in windows:
            claim = classify_block(block, detector)
            bl = block.lower()
            for case in cases:
                hit_alias = None
                for rx, alias in case["aliases"]:
                    if rx.search(bl):
                        hit_alias = alias
                        break
                if not hit_alias:
                    continue
                n_mentions += 1
                cr = claim["claimed_rank"]
                sidecar.append({
                    "path": rel, "line": line, "case_id": case["case_id"], "alias": hit_alias,
                    "registered_tier": case["tier"], "claimed_tier": claim["claimed_tier"],
                    "has_band": claim["has_band"], "exp_claim": claim["exp_claim"],
                    "code_claim": claim["code_claim"]})

                # rule 1: bounded-agreement case shown with an experiment claim but no band
                if case["tier"] == "bounded-agreement" and claim["exp_claim"] and not claim["has_band"]:
                    refusals.append({
                        "rule": "bounded-agreement-without-band", "case_id": case["case_id"],
                        "path": rel, "line": line,
                        "detail": f"experiment comparison shown without the explicit band "
                                  f"(token {claim['claim_tok']!r}); alias {hit_alias!r}"})
                    continue
                # rule 2: over-claim
                if cr is not None and cr > case["tier_rank"]:
                    refusals.append({
                        "rule": "over-claim", "case_id": case["case_id"], "path": rel, "line": line,
                        "detail": f"shown as {claim['claimed_tier']} (rank {cr}) but registered "
                                  f"{case['tier']} (rank {case['tier_rank']}); token "
                                  f"{claim['claim_tok']!r}, alias {hit_alias!r}"})
                    continue
                # rule 3a: experiment-validated missing required caveat (A3 shock)
                if (case["tier"] == "experiment-validated" and case["required_caveat_tokens"]
                        and claim["exp_claim"]
                        and not any(t in bl for t in case["required_caveat_tokens"])):
                    refusals.append({
                        "rule": "missing-required-caveat", "case_id": case["case_id"], "path": rel,
                        "line": line,
                        "detail": f"shown as validated without required caveat token(s) "
                                  f"{case['required_caveat_tokens']}; alias {hit_alias!r}"})
                    continue
                # rule 3b: code/method case presented WITH a comparison claim but NO disavowal
                # in its section (Sanaa: code-verified never shown as experiment-validated;
                # disavowal required).
                if case["required_disavowal"] and (claim["exp_claim"] or claim["code_claim"]):
                    if not section_has_disavowal(section):
                        refusals.append({
                            "rule": "missing-disavowal", "case_id": case["case_id"], "path": rel,
                            "line": line,
                            "detail": f"{case['tier']} case presented with a comparison claim "
                                      f"(token {claim['claim_tok']!r}) but NO 'not "
                                      f"experiment-validated' disavowal in its section; "
                                      f"alias {hit_alias!r}"})
                        continue

    return refusals, n_surfaces, n_mentions, sidecar


# --------------------------------------------------------------------------
# freeze check
# --------------------------------------------------------------------------
def freeze_status(registry_path: str):
    """Return (state, detail). state in {committed-match, drift, pending-uncommitted, no-git}."""
    rel = os.path.relpath(registry_path, REPO_ROOT)
    try:
        blob = subprocess.run(
            ["git", "-C", REPO_ROOT, "show", f"HEAD:{rel}"],
            capture_output=True, text=True)
    except Exception as e:
        return "no-git", str(e)
    if blob.returncode != 0:
        return "pending-uncommitted", "registry has no committed blob at HEAD (working-tree draft)"
    with open(registry_path, "rb") as f:
        disk = hashlib.sha256(f.read()).hexdigest()
    head = hashlib.sha256(blob.stdout.encode()).hexdigest()
    return ("committed-match" if disk == head else "drift"), f"disk {disk[:12]} vs HEAD {head[:12]}"


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
def emit(refusals, n_surfaces, n_mentions, sidecar, sidecar_path):
    if sidecar_path:
        try:
            with open(sidecar_path, "w") as f:
                json.dump({"surfaces": n_surfaces, "mentions": n_mentions, "map": sidecar},
                          f, indent=2)
        except Exception:
            pass
    if not refusals:
        print(f"PASS: {n_surfaces} surfaces, {n_mentions} case-mentions, 0 tier violations.")
        return EXIT_OK
    print(f"GATE FAIL: {len(refusals)} reference-tier violation(s) across "
          f"{n_surfaces} surfaces ({n_mentions} case-mentions).")
    print("=" * 78)
    for r in refusals:
        loc = f"{r['path']}:{r['line']}" if r["line"] else r["path"]
        print(f"  [{r['rule']}] {r['case_id']}  {loc}")
        print(f"      {r['detail']}")
    print("=" * 78)
    return EXIT_REFUSE


# --------------------------------------------------------------------------
# selftest -- planted-zero control, both directions, exit-code driven (L-332)
# --------------------------------------------------------------------------
def selftest() -> bool:
    print("=" * 78)
    print("PLANTED-ZERO CONTROL -- rule 3.  A zero from a blind scanner is not evidence.")
    print("Drive the gate RED (over-claim + dimension leak) then GREEN (clean) through THIS")
    print("FILE's entry point over temp surfaces.  Both plants must fire.")
    print("=" * 78)

    me = os.path.abspath(__file__)
    ok = True
    tmp = tempfile.mkdtemp(prefix="reftier_plant_")

    def run_dir(d: str) -> int:
        r = subprocess.run([sys.executable, me, "--scan-dir", d, "--no-freeze-check"],
                           capture_output=True, text=True)
        return r.returncode

    def arm(label: str, want: int, got: int):
        nonlocal ok
        good = (got == want)
        ok = ok and good
        print(f"  {label:56s} -> exit {got}  (want {want})  {'PASS' if good else 'FAIL'}")

    def write(sub: str, name: str, text: str) -> str:
        d = os.path.join(tmp, sub)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, name), "w") as f:
            f.write(text)
        return d

    try:
        # ---- CLEAN surface: honestly caveated; must PASS with 0 flags -----------------
        clean = write("clean", "act.md",
            "## CRM wing (code-verified)\n\n"
            "The CRM result reproduces DAFoam's own tutorial baseline CD 0.02090. This is "
            "code-verified only; nothing here is validated against wind-tunnel or test data "
            "(no comparison against the DPW workshop). Self-consistency, not validation.\n\n"
            "## Ahmed body (bounded-agreement)\n\n"
            "The Ahmed body Cd agrees with Ahmed 1984 within +/-15% [0.2423, 0.3278]; "
            "solver-backed, not validated.\n\n"
            "## ONERA M6 (experiment-validated)\n\n"
            "The ONERA M6 wing is validated against the AGARD wind-tunnel experiment; the CFD "
            "shock sits aft of the experimental shock (disclosed offset).\n")
        arm("GREEN clean surface (all caveats/bands present)", EXIT_OK, run_dir(clean))

        # ---- RED-1: over-claim beside a code-verified id -----------------------------
        over = write("over", "bad.md",
            "## CRM wing\n\n"
            "The CRM result was validated against the wind-tunnel experiment and matches the "
            "measured data.\n")
        arm("RED over-claim beside code-verified CRM", EXIT_REFUSE, run_dir(over))
        # control: negate the experiment claim -> the over-claim disappears
        ctl_over = write("over_ctl", "bad.md",
            "## CRM wing\n\n"
            "The CRM result reproduces the tutorial baseline; it is NOT validated against any "
            "wind-tunnel experiment and no test data exists. Code-verified only.\n")
        arm("RED-over control: experiment claim negated -> clean", EXIT_OK, run_dir(ctl_over))

        # ---- RED-2: excluded id inside a synthetic 3D list ---------------------------
        leak = write("leak", "gallery.md",
            "## Completed 3D cases\n\n"
            "- ONERA M6\n- Ahmed body\n- T24 wedge motor\n")
        arm("RED dimension leak (T24 in a 3D listing)", EXIT_REFUSE, run_dir(leak))
        # control: same list under a non-3D heading -> no leak
        ctl_leak = write("leak_ctl", "gallery.md",
            "## Axisymmetric verification cases\n\n"
            "- T24 wedge motor\n")
        arm("RED-leak control: T24 under a 2D/axi heading -> clean", EXIT_OK, run_dir(ctl_leak))

        # ---- RED-3: bounded-agreement shown without its band -------------------------
        noband = write("noband", "bad.md",
            "## Ahmed body\n\n"
            "The Ahmed body Cd agrees with the Ahmed 1984 experiment (validated against the "
            "measured data).\n")
        arm("RED bounded-agreement (Ahmed) shown without band", EXIT_REFUSE, run_dir(noband))
        ctl_noband = write("noband_ctl", "bad.md",
            "## Ahmed body\n\n"
            "The Ahmed body Cd agrees with the Ahmed 1984 experiment within +/-15% "
            "[0.2423, 0.3278].\n")
        arm("RED-band control: band restored -> clean", EXIT_OK, run_dir(ctl_noband))

        # ---- RED-4: experiment-validated case missing its required caveat ------------
        nocav = write("nocav", "bad.md",
            "## ONERA M6\n\n"
            "The ONERA M6 wing is validated against the AGARD wind-tunnel experiment; excellent "
            "agreement across the span.\n")
        arm("RED experiment-validated (M6) missing shock caveat", EXIT_REFUSE, run_dir(nocav))
        ctl_nocav = write("nocav_ctl", "bad.md",
            "## ONERA M6\n\n"
            "The ONERA M6 wing is validated against the AGARD wind-tunnel experiment; the CFD "
            "shock sits aft of the experimental shock (disclosed offset).\n")
        arm("RED-caveat control: shock caveat restored -> clean", EXIT_OK, run_dir(ctl_nocav))

        print("=" * 78)
        if ok:
            print("SELFTEST: PASS -- every arm hit its expected exit code; each RED plant is paired")
            print("with a control that flips it, proving the scanner is not blind (rule 3).")
        else:
            print("SELFTEST: FAIL -- a plant did not fire or a control did not flip; the gate would")
            print("print a zero it cannot defend (rule 3).")
        print("=" * 78)
        return ok
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main(argv) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", default=DEFAULT_REGISTRY, help="frozen registry path")
    ap.add_argument("--root", default=REPO_ROOT, help="repo root for surface scan")
    ap.add_argument("--scan-dir", default=None,
                    help="scan this directory as surfaces (used by --selftest)")
    ap.add_argument("--sidecar", default=None, help="write the mention->tier map JSON here")
    ap.add_argument("--require-freeze", action="store_true",
                    help="hard-refuse if the registry differs from its committed blob")
    ap.add_argument("--no-freeze-check", action="store_true", help="skip the freeze status line")
    ap.add_argument("--selftest", action="store_true",
                    help="drive the planted-zero control both directions; exit 3 if it does not fire")
    args = ap.parse_args(argv)

    if args.selftest:
        return EXIT_OK if selftest() else EXIT_SELFTEST_FAIL

    reg = load_registry(args.registry)

    if not args.no_freeze_check:
        state, detail = freeze_status(args.registry)
        if args.require_freeze and state != "committed-match":
            print(f"GATE FAIL: registry freeze not satisfied [{state}] {detail}")
            return EXIT_REFUSE
        print(f"registry freeze: {state} ({detail})")

    scan_dir_mode = args.scan_dir is not None
    root = args.scan_dir if scan_dir_mode else args.root
    refusals, n_surf, n_ment, sidecar = grade(root, reg, scan_dir_mode)
    return emit(refusals, n_surf, n_ment, sidecar, args.sidecar)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
