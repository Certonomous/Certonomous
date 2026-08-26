#!/usr/bin/env python3
"""Assemble docs/CAPABILITY_GRID.md from the per-family grids at HEAD.

Idempotent and zero-compute: reads every source with `git show HEAD:<path>`
(never the worktree, never the shared index), extracts each family's
"regime/mode per case" derivation table, its cell table, its census line and
its planted-control sha footer, and writes docs/CAPABILITY_GRID.md.  A family
whose file is not yet at HEAD gets a placeholder table (every cell
"CAN NOT DO -- not attempted (table not yet built)") and is picked up on the
next run.  Owner: verification-supervisor.  Sanaa's directive: 068c2bf0.

Usage:  python3 scripts/assemble_capability_grid.py [--out docs/CAPABILITY_GRID.md]
"""
import argparse, datetime, re, subprocess, sys

REPO = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
DIRECTIVE = "068c2bf0"
CAP = "docs/capability/"
FAMILIES = [  # (label, file, cell axes for the placeholder, column headers)
    ("cfd", "cfd_GRID.md",
     [["2D", "axisym", "3D"], ["steady", "unsteady"],
      ["incompressible", "subsonic-compressible", "transonic", "supersonic", "hypersonic",
       "multiphase-free-surface"]],
     ["cell", "verdict"]),
    ("heat-transfer", "heat-transfer_GRID.md",
     [["conduction", "forced conv", "natural conv", "mixed", "conjugate", "radiation"],
      ["laminar", "turbulent"], ["2D", "axisym", "3D"]],
     ["cell", "verdict"]),
    ("dafoam", "dafoam_GRID.md",
     [["2D", "axisym", "3D"], ["steady", "unsteady"],
      ["incompressible", "subsonic-compressible", "transonic", "supersonic", "hypersonic",
       "multiphase-free-surface"]],
     ["cell", "gradients computed + FD-verified", "optimization converged"]),
]
EVIDENCE = ("ansys-verification (VMFL register rows mapped onto cfd / heat-transfer classes)",
            "ansys_ROWS.md")
METRICS = "METRICS_SUMMARY.md"
SHA_RE = re.compile(r"\b[0-9a-f]{7,10}\b")
STRUCK = re.compile(r"~~.*?~~")
AUDIT = {"dafoam": ("dafoam_GRID_AUDIT.md", "verification audit of the dafoam table")}


def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)


def head():
    return git("rev-parse", "HEAD").stdout.strip()


def show(path):
    r = git("show", f"HEAD:{path}")
    return r.stdout if r.returncode == 0 else None


def last_commit(path):
    r = git("log", "-1", "--format=%h", "HEAD", "--", path)
    return r.stdout.strip() or None


PRIOR_DRAFT = re.compile(r"^(## Verification supervisor's draft.*|# .*DRAFT.*)$", re.M)


def split_authority(text):
    """The family's own table is the authority: everything ABOVE the first retained
    prior-draft marker (a second H1, or a '## Verification supervisor's draft' heading)."""
    first_h1 = text.find("\n# ")
    m = PRIOR_DRAFT.search(text, 1)
    cut = m.start() if m else (first_h1 if first_h1 > 0 else -1)
    if cut < 0:
        return text, None
    return text[:cut], text[cut:]


def tables(text):
    """Every markdown table as a list of raw lines, in order."""
    out, cur = [], []
    for ln in text.splitlines():
        if ln.startswith("|"):
            cur.append(ln)
        elif cur:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def census_line(text):
    m = re.search(r"^\*\*Census[^*]*\*\*.*$", text, re.M)
    return m.group(0) if m else "**Census:** (no census line found in source)"


def footer_shas(text):
    """shas listed in the source's own planted-control loop, plus every `@ `sha`` citation."""
    shas = set()
    m = re.search(r"for s in ([0-9a-f \n]+?); do", text)   # the FIRST footer loop only
    if m:
        shas.update(SHA_RE.findall(m.group(1)))
    shas.update(re.findall(r"@ `([0-9a-f]{7,10})`", text))
    return shas


def verdict_census(table_lines):
    """Count cells per Sanaa's three-value verdict across every verdict column."""
    c = {"CAN DO": 0, "CAN DO, CAVEATS": 0, "CAN NOT DO": 0, "CAN NOT DO — not attempted": 0,
         "unclassified": 0}
    ncol = len(table_lines[0].strip().strip("|").split("|")) if table_lines else 2
    for ln in table_lines[2:]:
        # split on pipes that are not inside a backtick code span, then keep only the verdict columns
        cells = [x.strip() for x in re.split(r"\|(?=(?:[^`]*`[^`]*`)*[^`]*$)", ln.strip().strip("|"))][1:ncol]
        for cell in cells:
            t = STRUCK.sub("", cell).replace("*", "").strip()   # a struck ~~old~~ form is never the verdict
            if re.match(r"CAN DO, CAVEATS", t):
                c["CAN DO, CAVEATS"] += 1
            elif re.match(r"CAN DO", t):
                c["CAN DO"] += 1
            elif re.match(r"CAN NOT DO\s*[—–-]+\s*not attempted", t) or re.match(r"CAN NOT DO.*not attempted", t) and "attempted" in t.split("—")[-1] if "—" in t else re.match(r"CAN NOT DO.*not attempted", t):
                c["CAN NOT DO — not attempted"] += 1
            elif re.match(r"CAN NOT DO", t):
                c["CAN NOT DO"] += 1
            else:
                c["unclassified"] += 1
    return c


def placeholder(axes, cols):
    rows = [f"| {' | '.join(cols)} |", "|" + "---|" * len(cols)]
    import itertools
    for combo in itertools.product(*axes):
        cell = " · ".join(combo)
        rows.append(f"| **{cell}** |" + " CAN NOT DO — not attempted (table not yet built) |" * (len(cols) - 1))
    return rows


def family_block(label, fname, axes, cols):
    path = CAP + fname
    text = show(path)
    out = [f"## {label}", ""]
    if text is None:
        out.append(f"**family table at HEAD: NOT YET LANDED — placeholder: all cells "
                   f"'CAN NOT DO — not attempted (table not yet built)'.** Owed as `{path}` by the "
                   f"{label} supervisor; this script picks it up on re-run.")
        out += ["", *placeholder(axes, cols), ""]
        tbl = placeholder(axes, cols)
        return out, verdict_census(tbl), set(), False
    sha = last_commit(path)
    out.append(f"**family table at HEAD: `{sha}`** (`{path}`; every cell below is copied verbatim "
               f"from that file — the family supervisor's words, not this script's).")
    text, prior = split_authority(text)
    if prior is not None:
        marker = prior.strip().splitlines()[0][:120]
        out.append(f"\n*The family file also carries, below its own table, the **verification supervisor's "
                   f"prior draft, superseded by the family table above** (marker line: `{marker}`). "
                   f"Only the family's FIRST derivation table, FIRST cell table, FIRST census and FIRST "
                   f"footer are read here; the prior draft is neither counted nor reproduced.*")
    tbs = tables(text)
    if not tbs:
        out.append("\n(no markdown tables found in the family file)")
        return out, verdict_census([]), footer_shas(text), True
    # derivation table = first table; cell table = the largest table by row count
    cell_tbl = next((tb for tb in tbs if re.match(r"\|\s*cell\b", tb[0], re.I) and len(tb) >= 20), None) \
        or max(tbs, key=len)
    deriv = [tb for tb in tbs if tb is not cell_tbl and tbs.index(tb) < tbs.index(cell_tbl)]
    if deriv:
        out += ["", "**Regime / mode per case, as derived by the family (their table):**", "", *deriv[0], ""]
    out += ["**The table:**", "", *cell_tbl, "", census_line(text), ""]
    return out, verdict_census(cell_tbl), footer_shas(text), True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/CAPABILITY_GRID.md")
    a = ap.parse_args()
    H = head()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    L = ["# CAPABILITY GRID — Sanaa's taxonomy, assembled from the family tables at HEAD", "",
         f"**Owner:** verification-supervisor. **Directive:** Sanaa's [SANAA-DIRECT] CAPABILITY GRID, "
         f"boarded verbatim at commit `{DIRECTIVE}` (`docs/LAB_STATE.md`, CHIEF ADDENDUM 2026-08-26T17:35Z). "
         f"**Assembled from HEAD `{H[:8]}`** on {now} by `scripts/assemble_capability_grid.py` "
         f"(idempotent; reads only `git show HEAD:` blobs; zero compute). **FIRST DRAFT** — re-run when a "
         f"family table lands.", "",
         "**The verdict vocabulary (Sanaa's, exactly three):** `CAN DO — X cases` (ran successfully, metrics "
         "verified; strongest case cited by path + record sha + what was checked); `CAN DO, CAVEATS` (runs, "
         "credible results, named missing items each ≤ 1 line); `CAN NOT DO` (does not converge / does not "
         "reproduce literature / not enough compute / documented model defect — what was attempted, what "
         "would fix it; empty cell = `CAN NOT DO — not attempted`). One verdict per cell. The lab's fixed gate "
         "vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING) appears inside a cell "
         "as what the record says.", "",
         "**Disclosed mapping rule (this supervisor's, from the lanes' common brief):** CAN DO requires at least "
         "one case whose record at HEAD says PASS (or GATE REACHED with every reached gate passing) under a "
         "frozen prereg with a CONVERGING Roache triple where a triple was claimed; anything weaker that still "
         "produced a credible graded number is CAN DO, CAVEATS; GATE FAIL / NOT A RESULT / BLOCKED-only cells "
         "are CAN NOT DO with the attempt named. Every citation must resolve at HEAD "
         "(`git cat-file -e <sha>^{commit}`); the merged footer below is the planted control.", "",
         "**Order (Sanaa's):** cfd table, heat-transfer table, dafoam table, then the metrics summary.", "",
         "---", ""]
    all_shas, census = set(), {}
    for label, fname, axes, cols in FAMILIES:
        blk, cen, shas, present = family_block(label, fname, axes, cols)
        L += blk
        if label in AUDIT:   # ruling: the audit is its OWN subsection under the table, never folded into cells
            afile, atitle = AUDIT[label]
            atext = show(CAP + afile)
            L += [f"### {atitle}", ""]
            if atext is None:
                L.append(f"**at HEAD: NOT YET LANDED** — `{CAP + afile}`; picked up on re-run.")
            else:
                L.append(f"**at HEAD: `{last_commit(CAP + afile)}`** (`{CAP + afile}`, reproduced verbatim; "
                         "its own footer is superseded by the merged footer below):")
                abody = atext.split("\n", 1)[1] if atext.startswith("# ") else atext
                L += ["", re.sub(r"^(#+) ", lambda m: "#" * (len(m.group(1)) + 2) + " ", abody.rstrip(), flags=re.M)]
                shas |= footer_shas(atext)
            L.append("")
        L += ["---", ""]
        census[label] = (cen, present)
        all_shas |= shas
    # ansys evidence rows
    ev_label, ev_file = EVIDENCE
    ev = show(CAP + ev_file)
    L += [f"## Evidence: {ev_label}", ""]
    if ev is None:
        L.append(f"**at HEAD: NOT YET LANDED** — `{CAP + ev_file}` owed by ansys-verification; picked up on re-run.")
    else:
        L.append(f"**at HEAD: `{last_commit(CAP + ev_file)}`** (`{CAP + ev_file}`, reproduced verbatim):")
        L += ["", ev.rstrip()]
        all_shas |= footer_shas(ev)
    L += ["", "---", ""]
    # metrics summary
    ms = show(CAP + METRICS)
    L += ["## Metrics summary (Sanaa's §1–§6)", ""]
    if ms is None:
        L.append(f"**at HEAD: NOT YET LANDED** — `{CAP + METRICS}`.")
    else:
        L.append(f"**at HEAD: `{last_commit(CAP + METRICS)}`** (`{CAP + METRICS}`, reproduced verbatim; its own "
                 "planted-control footer is superseded by the merged footer below):")
        body = ms.split("\n", 1)[1] if ms.startswith("# ") else ms
        L += ["", body.rstrip()]
        all_shas |= footer_shas(ms)
    L += ["", "---", "", "## Census per family", "",
          "| family | table at HEAD | CAN DO | CAN DO, CAVEATS | CAN NOT DO (attempted) | CAN NOT DO — not attempted | unclassified cells |",
          "|---|---|---|---|---|---|---|"]
    for label, _, _, _ in FAMILIES:
        c, present = census[label]
        L.append(f"| {label} | {'yes' if present else 'NOT YET LANDED (placeholder)'} | {c['CAN DO']} | "
                 f"{c['CAN DO, CAVEATS']} | {c['CAN NOT DO']} | {c['CAN NOT DO — not attempted']} | {c['unclassified']} |")
    L += ["", "(Counts are per verdict cell: dafoam has two verdict columns per class, so its row sums to 72.)", "",
          "---", "", "## Footer — merged planted control: every distinct sha cited by every source, resolved", ""]
    shas = sorted(all_shas)
    ok = missing = 0
    lines = []
    for s in shas:
        r = git("cat-file", "-e", f"{s}^{{commit}}")
        st = "ok" if r.returncode == 0 else "MISSING"
        ok += st == "ok"; missing += st != "ok"
        lines.append(f"{s} {st}")
    L += [f"Run from the repository root; every line must read `ok`; {len(shas)} distinct shas across all sources:", "",
          "```", "for s in " + " ".join(shas) + "; do printf '%s ' \"$s\"; git cat-file -e \"$s^{commit}\" 2>/dev/null && echo ok || echo MISSING; done",
          "```", "",
          f"Reading at assembly time ({now}, HEAD `{H[:8]}`): **{ok} ok, {missing} MISSING, {len(shas)} distinct shas.**"
          + (" MISSING lines: " + ", ".join(l.split()[0] for l in lines if l.endswith("MISSING")) if missing else ""), ""]
    open(f"{REPO}/{a.out}", "w").write("\n".join(L))
    print(f"wrote {a.out}: HEAD {H[:8]}, shas {ok} ok / {missing} MISSING", file=sys.stderr)
    for label, _, _, _ in FAMILIES:
        print(label, census[label], file=sys.stderr)


if __name__ == "__main__":
    main()
