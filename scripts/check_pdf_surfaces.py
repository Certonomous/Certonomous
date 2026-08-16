#!/usr/bin/env python3
"""Grade the PDF/LaTeX arm, which no other instrument in this lab can see.

WHY THIS FILE EXISTS
--------------------
`scripts/check_derived_figures.py:251` and `scripts/check_normative_clauses.py:153`
both set ``PROSE_GLOBS = ("*.md", "*.html")``. Every tracked ``*.tex`` and every
tracked ``*.pdf`` is therefore outside the frame of both standing instruments —
not *missed* by them, never *looked at* by them. That is a silent zero at the
level of the corpus definition, and V14's residual 6 recorded the consequence:
the PDF arm is this corpus's largest single concentration of withdrawn claims.

Widening the glob was measured before this file was written, and it is NOT the
repair. Adding ``*.pdf`` to `check_normative_clauses` took its frame from 424 to
476 opened files and 965 to 1,277 clauses, cost **zero** new faults, and still
returned ``PASS`` on `demo-output/website/latex/closure_challenge_report.pdf` —
a build whose page 1 read "rank 1 of 5, scored locally" and "P(rank 1) = 68%"
five days after its own source was repaired. A clause checker grades normative
DIRECTIVES; a withdrawn ordinal is not a directive. The wider glob made the arm
look covered while the defect class stayed invisible, which is worse than an
admitted gap. Hence a separate instrument with its own claim class.

THE ONE-SIDED DISCRIMINATOR, which is the sound part and generalises
--------------------------------------------------------------------
``\\sout{}`` and ``<s>`` are STRIKE-AND-KEEP. A correctly repaired document
retains the withdrawn figure in its text layer, struck, and adds the correction
beside it. A stale build retains the withdrawn figure and has no correction. So:

* the **presence** of a withdrawn token proves NOTHING — it is equally the
  signature of a correct repair and of a stale artifact;
* the **absence of every post-repair token**, in a document that carries
  withdrawn tokens, proves the artifact predates the repair.

Only the second direction is used to fail an artifact. That asymmetry is why a
text-layer grep can decide staleness without being able to decide correctness,
and it is why this check renders pages to PNG for the cases the discriminator
leaves open rather than guessing at them.

WRAP-SAFETY, printed rather than assumed
----------------------------------------
A pattern written with literal spaces is as blind as a hand-picked line range
and looks rigorous in the record. The heading "Cases where we lead the entire\\n
public leaderboard" wraps between two words, and a literal-space pattern returns
0 on the very file whose heading is the defect. Every inter-word gap in
``CLAIM_PATTERNS`` and ``REPAIR_TOKENS`` is ``\\s+``, and ``--frame`` PRINTS the
self-test that proves it, because an audit of 28 grading records found 0 of them
declaring the wrap-safety of the patterns they swept with.

FRAME: WHAT THIS CAN AND CANNOT SEE
-----------------------------------
CAN: every tracked ``*.pdf`` and ``*.tex``, enumerated with ``git ls-files``.
Enumeration is deliberately NOT a grep: ``.gitattributes`` marks ~1,476 files
binary and ``git grep -I`` skips them, published certificate PDFs among them —
``git grep -Il CERTONOMOUS -- 'demo-output/website/certificates/*.pdf'`` returns
0 where ``git ls-files`` returns 2.

CANNOT: the gitignored PDF arm (counted and named in ``--frame``, not graded —
it is `dist/` and `mission-output/`, and `dist/` is owner-restricted); image-only
PDFs with no text layer (each named, and their presence forces UNKNOWN rather
than a false PASS); whether a claim is *correct*, as opposed to whether the
artifact predates its source's repair; and any surface a renderer cannot open.

CALLER: run by hand, and by whatever registers it — see the registration note in
this pass's docket row. Exit contract below is the machine interface.

EXIT CONTRACT
-------------
    0  PASS     every graded artifact is at least as new as its source, and no
                artifact carries withdrawn tokens with every repair token absent
    1  FAIL     at least one artifact outlived its input, or is stale by the
                one-sided discriminator
    2  FAIL     a CONTROL failed — the instrument did not establish that it can
                find anything, so no zero it prints is evidence
    3  UNKNOWN  the frame could not be established (git failed, no extractor, or
                an image-only PDF blocks a verdict)

Never gate internally through a pipe: a pipe replaces the exit status.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

PASS, FAIL, CONTROL_FAIL, UNKNOWN = 0, 1, 2, 3

#: Withdrawn / four-entry-board claim class. Every inter-word gap is \s+.
CLAIM_PATTERNS = {
    "rank_1_of_5":     r"rank\s+1\s+of\s+5",
    "ordinal_of_5":    r"\b\d+(?:st|nd|rd|th)\s+of\s+5\b",
    "our_model_leads": r"our\s+model\s+leads",
    "lead_whole_board": r"lead(?:s)?\s+the\s+(?:entire|whole)\s+(?:public\s+)?"
                        r"leaderboard",
    "best_on_board_n": r"\b(?:three|four|five|3|4|5)\s+of\s+(?:the\s+)?"
                       r"(?:8|eight)\b",
    "p_rank1_68":      r"P\s*\(\s*rank\s*1\s*\)\s*=?\s*\\?\s*68",
    "interval_2_100":  r"2\s*(?:-|--|–|—)\s*100\s*\\?%",
}

#: Tokens that exist ONLY in a post-2026-08-12 six-entry repair. Absence of ALL
#: of these, in a document carrying CLAIM_PATTERNS, proves the build predates the
#: repair. Presence of any of them proves nothing on its own.
#: A repair token must be one that CANNOT occur before the repair. "two of
#: eight" was tried and REMOVED after adjudication: the report PDF contains
#: "on exactly two of the eight test cases the uncorrected baseline beats all
#: four published entries", which is a decline-gate claim against the FOUR-entry
#: board, not a six-entry correction. An ambiguous repair token silently
#: downgrades a true FAIL to an INDETERMINATE, which is the failure direction
#: that matters here, so every token below names the six-entry board, the
#: entrant who joined it, one of that entrant's values, or the repair's date.
REPAIR_TOKENS = {
    "six_entry":      r"six\s*-\s*entry",
    "tian":           r"Tian",
    "rank_1_of_7":    r"rank\s+1\s+of\s+7",
    "live_min_hill":  r"0\.0432",
    "live_min_hill2": r"0\.0998",
    "zero_of_eight":  r"zero\s+of\s+(?:8|eight)",
    "board_fetched":  r"2026\s*-\s*08\s*-\s*11T23:33",
    "struck_dated":   r"struck\s+2026\s*-\s*08\s*-\s*12",
}


#: Wrapped probes, written out by hand rather than derived from the patterns.
#: A probe DERIVED from its own pattern is not an independent test — it shares
#: the pattern's bug — and the first version of this file proved it by emitting
#: a malformed probe for a sound pattern and failing its own control.
WRAP_PROBES = {
    "rank_1_of_5":      "rank\n1\nof\n5",
    "ordinal_of_5":     "3rd\nof 5",
    "our_model_leads":  "our\nmodel\nleads",
    "lead_whole_board": "lead the entire\npublic leaderboard",
    "best_on_board_n":  "four\nof the eight",
    "p_rank1_68":       "P(rank 1) =\n68",
    "interval_2_100":   "2--100\\%",
}
REPAIR_PROBES = {
    "six_entry":      "six\n-\nentry",
    "tian":           "Tian",
    "rank_1_of_7":    "rank\n1\nof\n7",
    "live_min_hill":  "0.0432",
    "live_min_hill2": "0.0998",
    "zero_of_eight":  "zero\nof\neight",
    "board_fetched":  "2026\n-\n08\n-\n11T23:33",
    "struck_dated":   "struck\n2026\n-\n08\n-\n12",
}


def wrap_safety_selftest() -> tuple[bool, list[str]]:
    """Prove each pattern crosses a line break. Printed, not assumed.

    A pattern whose inter-word gaps are literal spaces returns 0 on wrapped
    prose, and looks rigorous in the record while doing it. Every pattern is
    required to match a hand-written wrapped probe; a pattern with no probe is
    an unproven pattern and fails the control rather than passing silently.
    """
    log, ok = [], True
    for label, pats, probes in (("", CLAIM_PATTERNS, WRAP_PROBES),
                                ("repair:", REPAIR_TOKENS, REPAIR_PROBES)):
        for name, pat in pats.items():
            probe = probes.get(name)
            if probe is None:
                log.append(f"    {label}{name:18s} NO PROBE - unproven")
                ok = False
                continue
            hit = re.search(pat, probe, re.I) is not None
            log.append(f"    {label}{name:18s} wrapped probe "
                       f"{'MATCHES' if hit else 'MISSED'}   {probe!r}")
            ok &= hit
    return ok, log


def positive_control() -> tuple[bool, str]:
    """The instrument must find planted claims, WRAPPED, before any zero counts."""
    planted = ("CONTROL: rank 1\nof 5 scored locally, AR_14 falls to 3rd\nof 5, "
               "our model\nleads, we lead the entire\npublic leaderboard, "
               "four\nof the eight cases, P(rank 1) =\n68\\%, 2--100\\%.")
    fired = {n for n, p in CLAIM_PATTERNS.items() if re.search(p, planted, re.I)}
    want = set(CLAIM_PATTERNS)
    return fired == want, (f"fired {len(fired)}/{len(want)}: "
                           f"missing {sorted(want - fired) or 'none'}")


def negative_control() -> tuple[bool, str]:
    """A buffer with no claim must return zero, so hits are not unconditional."""
    clean = ("The six-entry board fetched 2026-08-11 puts us rank 1 of 7 with "
             "two of eight cases best on board and zero of eight earned.")
    fired = {n for n, p in CLAIM_PATTERNS.items() if re.search(p, clean, re.I)}
    # 'best_on_board_n' legitimately matches 'two of eight'? no: two is not in
    # the alternation. Any hit here is an over-fire.
    return not fired, f"fired {sorted(fired) or 'none'}"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True)


def tracked(*globs: str) -> tuple[list[str], int, str]:
    proc = git("ls-files", "-z", "--", *globs)
    return ([p for p in proc.stdout.split("\0") if p],
            proc.returncode, proc.stderr.strip())


def ignored_pdfs() -> list[str]:
    proc = git("ls-files", "--others", "--ignored", "--exclude-standard", "-z")
    return [p for p in proc.stdout.split("\0")
            if p and p.lower().endswith(".pdf")]


def last_commit(rel: str) -> tuple[str, str]:
    out = git("log", "-1", "--format=%h|%aI", "--", rel).stdout.strip()
    return tuple(out.split("|")) if "|" in out else ("", "")


def pdf_text(path: Path) -> tuple[str | None, str]:
    if shutil.which("pdftotext") is None:
        return None, "pdftotext not installed"
    try:
        pr = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                            capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"pdftotext failed: {exc}"
    if pr.returncode != 0:
        return None, f"pdftotext rc={pr.returncode}"
    return pr.stdout, ""


def render(path: Path, page: int, outdir: Path) -> str:
    outdir.mkdir(parents=True, exist_ok=True)
    stem = outdir / f"{path.stem}-p{page}"
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", "110",
                    "-png", str(path), str(stem)],
                   capture_output=True, text=True, timeout=180)
    hits = sorted(outdir.glob(f"{path.stem}-p{page}*.png"))
    return str(hits[0]) if hits else ""


def pages_with_claims(path: Path, npages: int) -> list[int]:
    out = []
    for pg in range(1, npages + 1):
        pr = subprocess.run(["pdftotext", "-layout", "-f", str(pg), "-l",
                             str(pg), str(path), "-"],
                            capture_output=True, text=True, timeout=120)
        if pr.returncode:
            continue
        if any(re.search(p, pr.stdout, re.I) for p in CLAIM_PATTERNS.values()):
            out.append(pg)
    return out


def page_count(path: Path) -> int:
    pr = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
    m = re.search(r"^Pages:\s*(\d+)", pr.stdout, re.M)
    return int(m.group(1)) if m else 0


def grade(root: Path, do_render: bool, render_dir: Path) -> dict:
    pdfs, rc_p, err_p = tracked("*.pdf")
    texs, rc_t, err_t = tracked("*.tex")
    if rc_p or rc_t:
        return {"verdict": UNKNOWN,
                "reason": f"git ls-files failed: {err_p or err_t}"}

    findings, notes, image_only, unreadable = [], [], [], []
    for rel in sorted(pdfs):
        path = root / rel
        txt, err = pdf_text(path)
        if txt is None:
            unreadable.append(f"{rel}: {err}")
            continue
        if not txt.strip():
            image_only.append(rel)
            continue

        claims = {n: len(re.findall(p, txt, re.I))
                  for n, p in CLAIM_PATTERNS.items()}
        claims = {k: v for k, v in claims.items() if v}
        repairs = {n: len(re.findall(p, txt, re.I))
                   for n, p in REPAIR_TOKENS.items()}
        repairs = {k: v for k, v in repairs.items() if v}

        src = rel[:-4] + ".tex"
        outlived = None
        if (root / src).exists():
            a_sha, a_dt = last_commit(rel)
            s_sha, s_dt = last_commit(src)
            if a_dt and s_dt:
                outlived = s_dt > a_dt
                if outlived:
                    findings.append({
                        "rel": rel, "kind": "OUTLIVED_ITS_INPUT",
                        "artifact_commit": f"{a_sha} {a_dt}",
                        "source": src, "source_commit": f"{s_sha} {s_dt}",
                    })

        if claims and not repairs:
            f = {"rel": rel, "kind": "STALE_BY_DISCRIMINATOR",
                 "claims": claims,
                 "why": "carries withdrawn tokens and NOT ONE post-repair "
                        "token; absence of every repair token is decisive "
                        "where presence of a claim token would not be"}
            if do_render:
                n = page_count(path)
                pgs = pages_with_claims(path, n)[:6]
                f["pages_with_claims"] = pgs
                f["renders"] = [render(path, pg, render_dir) for pg in pgs]
            findings.append(f)
        elif claims and repairs:
            notes.append({"rel": rel, "kind": "INDETERMINATE_FROM_TEXT",
                          "claims": claims, "repairs": repairs,
                          "why": "carries both withdrawn and repair tokens; "
                                 "the text layer cannot separate a repaired "
                                 "document from a stale one, so this needs a "
                                 "visual read"})
    return {"verdict": None, "pdfs": pdfs, "texs": texs,
            "findings": findings, "notes": notes,
            "image_only": image_only, "unreadable": unreadable,
            "ignored_pdfs": ignored_pdfs()}


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="check_pdf_surfaces",
        description="Grade the tracked PDF/LaTeX arm that PROSE_GLOBS excludes.")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--frame", action="store_true",
                    help="print the frame and the control self-tests, then exit")
    ap.add_argument("--render", action="store_true",
                    help="render claim-bearing pages to PNG for visual reading")
    ap.add_argument("--render-dir", default="")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    rdir = Path(args.render_dir) if args.render_dir else root / ".pdf_surface_png"

    ws_ok, ws_log = wrap_safety_selftest()
    pc_ok, pc_msg = positive_control()
    nc_ok, nc_msg = negative_control()

    o: list[str] = ["=" * 78, "check_pdf_surfaces", "=" * 78,
                    "WRAP-SAFETY SELF-TEST (0 of 28 audited grading records "
                    "declared this):"]
    o += ws_log
    o += [f"  wrap-safety      {'OK' if ws_ok else 'BROKEN'}",
          f"  positive control {'FIRED' if pc_ok else 'DEAD'}  ({pc_msg})",
          f"  negative control {'CLEAN' if nc_ok else 'OVER-FIRES'}  ({nc_msg})"]

    if not (ws_ok and pc_ok and nc_ok):
        o += ["", "VERDICT: FAIL (control) - the instrument did not establish "
                  "that it can find anything, so no zero it prints is evidence."]
        print("\n".join(o))
        return CONTROL_FAIL

    res = grade(root, args.render, rdir)
    if res.get("verdict") == UNKNOWN:
        print("\n".join(o + ["", f"VERDICT: UNKNOWN - {res['reason']}"]))
        return UNKNOWN

    o += ["", "FRAME (enumerated with git ls-files, never a grep: .gitattributes",
          "marks ~1476 files binary and git grep -I skips them, published",
          "certificate PDFs among them):",
          f"  tracked *.pdf        {len(res['pdfs'])}",
          f"  tracked *.tex        {len(res['texs'])}",
          f"  gitignored *.pdf     {len(res['ignored_pdfs'])}  "
          f"(NAMED, NOT GRADED - dist/ and mission-output/)",
          f"  image-only (no text) {len(res['image_only'])}",
          f"  unreadable           {len(res['unreadable'])}"]
    for r in res["image_only"]:
        o.append(f"    image-only: {r}")
    for r in res["unreadable"]:
        o.append(f"    unreadable: {r}")

    if args.frame:
        print("\n".join(o))
        return PASS

    o += ["", f"FINDINGS: {len(res['findings'])}"]
    for f in res["findings"]:
        o.append(f"  [{f['kind']}] {f['rel']}")
        for k, v in f.items():
            if k not in ("rel", "kind"):
                o.append(f"      {k}: {v}")
    o += ["", f"NOTES (need a visual read, not a verdict): {len(res['notes'])}"]
    for n in res["notes"]:
        o.append(f"  [{n['kind']}] {n['rel']}  claims={n['claims']} "
                 f"repairs={n['repairs']}")

    verdict = FAIL if res["findings"] else (
        UNKNOWN if (res["image_only"] or res["unreadable"]) else PASS)
    o += ["", "=" * 78,
          f"VERDICT: {{0:'PASS',1:'FAIL',2:'FAIL(control)',3:'UNKNOWN'}}[{verdict}]"
          f" = {['PASS', 'FAIL', 'FAIL(control)', 'UNKNOWN'][verdict]}",
          "=" * 78]

    if args.json:
        print(json.dumps({"verdict": verdict, "frame": {
            "tracked_pdf": len(res["pdfs"]), "tracked_tex": len(res["texs"]),
            "ignored_pdf": len(res["ignored_pdfs"]),
            "image_only": res["image_only"], "unreadable": res["unreadable"]},
            "findings": res["findings"], "notes": res["notes"],
            "controls": {"wrap_safety": ws_ok, "positive": pc_ok,
                         "negative": nc_ok}}, indent=1))
    else:
        print("\n".join(o))
    return verdict


if __name__ == "__main__":
    sys.exit(main())
