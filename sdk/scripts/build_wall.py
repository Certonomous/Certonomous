"""Reframe the validation wall as a product credential wall (website asset).

Emits a self-contained static section under demo-output/website/wall/:

- ``wall.html`` — an inline-styled, theme-aware fragment (no external CDNs, no
  fonts, no scripts pulled from the network). It leads with the lab's LIFETIME
  counters — missions run, solver core-hours, knowledge entries, experimental
  anchors, benchmarks active — never a "4 of 8" fraction.
- ``wall.json`` — the underlying data.

House discipline (v3-N3): no toy cases headline a website surface. The eight
canonical calibration bodies collapse into ONE expandable "calibration suite"
row; each carries its measured-vs-reference number, its cited source, and its
honest tier. Real-geometry validations, when their credential data is present,
headline above the calibration row.

Data source: by default the same records the server serves at /api/credentials
(``models/curriculum/results/*.json``) plus the lifetime counters from
``lab_stats``; pass ``--server http://127.0.0.1:8770`` to fetch live instead.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import urllib.request
from pathlib import Path

_SDK = Path(__file__).resolve().parents[1]
if str(_SDK) not in sys.path:
    sys.path.insert(0, str(_SDK))

from chief_engineer import lab, lab_stats  # noqa: E402

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

_REPO = _SDK.parent
# MOVE_MAP s4: SPLIT-2, EXECUTED IN BATCH 5.  This module writes TWO files that
# used to share a directory and no longer do: `wall.json` is R18 and leaves for
# `research/closure/data/`, while `wall.html` is one of R13's five served files
# and stays under the webroot until batch 8.  `_OUT = WALL_JSON.parent` was
# therefore correct only while both were in `demo-output/website/wall/`: the
# moment batch 5 landed it would have written the LIVE SERVED PAGE into
# `research/closure/data/wall.html` and left the served copy frozen at its last
# build, with nothing failing.  One `_OUT` cannot name both, so each is named.
_WALL_JSON = lab_paths.WALL_JSON
_WALL_HTML = lab_paths.WEB_WALL_HTML
_RESULTS = _REPO / "models" / "curriculum" / "results"

# Human display titles for the canonical bodies (no file-facing names on camera).
_DISPLAY = {
    "cube": "Cube",
    "sphere": "Sphere",
    "cylinder": "Circular cylinder",
    "flat_plate": "Flat plate",
    "naca0012_wing": "NACA 0012 wing",
    "naca4412_wing": "NACA 4412 wing",
    "ahmed_25": "Ahmed body — 25° slant",
    "ahmed_35": "Ahmed body — 35° slant",
}

# Bodies treated as canonical calibration geometry (collapse into one row).
_CANONICAL = set(_DISPLAY)

_TIER_RANK = {"VALIDATED": 0, "SOLVER-BACKED": 1, "RESEARCH MODEL": 2,
              "REFERENCE REGIME MISMATCH": 3, "TREND ONLY": 4,
              "UNCONVERGED": 5, "NEEDS WORK": 6}


def _credentials_from_disk() -> list[dict]:
    """One card per stored credential, re-derived at build time.

    A result file records what one mission measured on the mesh it solved. The
    refinement ladder for that same case can finish hours later on a finer
    mesh, and the grading rules can tighten after the file was written; both
    used to stop at the file, so the wall could keep showing the coarsest rung
    of a finished ladder under a tier the current rules would refuse.
    ``lab.displayed_credential`` closes that gap from measurement alone: the
    finest rung anchored to this credential's own ladder, graded against the
    reference as it stands on disk. The stored files are never rewritten.
    """
    cards: list[dict] = []
    if not _RESULTS.exists():
        return cards
    for path in sorted(_RESULTS.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not data.get("name"):
            continue
        shown = lab.displayed_credential(data)
        # The card is built by `lab.credential_card`, not by a key list typed
        # here. The list this replaces had drifted from the live panel's copy
        # of the same card and both were dropping the ladder verdict the tier
        # is graded on. ONE number on the card stays the rule: `measured` is
        # the coefficient on the reference's own area basis, the same one the
        # reason text quotes a percentage of, and `credential_card` sets it.
        card = lab.credential_card(data["name"], shown, data)
        card["tier"] = shown["tier"] or "NEEDS WORK"
        cards.append(card)
    cards.sort(key=lambda c: (_TIER_RANK.get(c["tier"], 9), c["name"]))
    return cards


def _fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _e(value) -> str:
    return html.escape("" if value is None else str(value))


# Legacy tier names normalize onto the current fidelity chips before display.
_LEGACY_TIER_ALIAS = {"TREND ONLY": "SOLVER-BACKED",
                      "REFERENCE REGIME MISMATCH": "SOLVER-BACKED",
                      "NEEDS WORK": "UNCONVERGED"}


def _chip_html(tier: str) -> str:
    """The fidelity chip markup, or '' when the tier is the unlabeled default.

    SOLVER-BACKED (a real solve, no experimental comparison) is the standard
    for this simulation platform and renders no badge. VALIDATED, CONCEPTUAL
    MODEL, and UNCONVERGED say more than the baseline, so they render.
    """
    resolved = _LEGACY_TIER_ALIAS.get(tier, tier)
    if resolved == "SOLVER-BACKED":
        return ""
    tier_class = "vt-" + resolved.split()[0].lower()
    return f'<span class="vtier {tier_class}">{_e(resolved)}</span>'


def _counter_html(counters: dict) -> str:
    tiles = [
        ("missions run", f"{counters['missions_run']:,}"),
        ("solver core-hours", f"{counters['solver_core_hours']:g}"),
        ("knowledge entries", f"{counters['knowledge_entries']}"),
        ("experimental anchors", f"{counters['experimental_anchors']}"),
        ("benchmarks active", f"{counters['benchmarks_active']}"),
    ]
    cells = "\n".join(
        f'      <div class="cred-counter"><span class="cred-counter-value">{_e(v)}</span>'
        f'<span class="cred-counter-label">{_e(label)}</span></div>'
        for label, v in tiles
    )
    return f'    <div class="cred-counters">\n{cells}\n    </div>'


def _basis_foot_html() -> str:
    """The measured basis of the two headline counters, stated on the page.

    Added 2026-08-01 after escalation #2 asked what the 208,102 counter is
    entitled to claim, given that 56,190 reduced-order rows record a
    ``wall_seconds`` of exactly 0.0. Every figure below was measured from
    ``demo-output/website/mega-batch/ledger.jsonl`` on 2026-08-01, not copied.
    The finding: those rows are real evaluations recorded below the stored
    precision, so the evaluation count stands and the core-hours figure is a
    floor. Working is in COST_SCALING.md section 6.
    """
    return (
        '  <p class="cred-foot"><strong>The basis of these two counters.</strong> '
        '208,102 is every row of the mega-batch ledger recorded ok '
        '(208,193 rows parsed, 91 failed, 1 torn line), run between '
        '2026-07-23T03:53:37Z and 2026-07-29T11:17:07Z: 139,095 real solves and '
        '69,007 reduced-order evaluations, each labelled as one or the other on '
        'its own row. 239.259 solver core-hours is those rows&rsquo; wall seconds '
        'summed and divided by 3600, every family serial. '
        '56,190 of the reduced-order rows carry a wall time of exactly 0.0. That is '
        'the stored precision, not a missing measurement: wall time is written as '
        'round(seconds, 3), the model costs about 0.32 ms per evaluation, and '
        'anything under 0.5 ms therefore stores as 0.0 &mdash; which is also why the '
        'smallest non-zero wall time anywhere in the ledger is exactly 0.001 s and '
        '96 percent of the reduced-order non-zeros are 0.003 s or less. The rows ran: '
        '400 of 400 sampled reproduce their recorded metrics exactly when the model is '
        're-run on that row&rsquo;s own design. So the evaluation count stands as measured, '
        'and the core-hours figure is a floor &mdash; it understates true time by at most '
        '56,190 &times; 0.0005 s = 28.1 s = 0.008 core-hours, 0.003 percent.</p>'
    )


def _cal_row_html(cards: list[dict]) -> str:
    validated = sum(1 for c in cards if c["tier"] == "VALIDATED")
    rows = []
    for card in cards:
        title = _DISPLAY.get(card["name"], card["name"])
        tier = card["tier"]
        measured = _e(card["measured"])
        ref = card["reference_cd"]
        vs = f"Cd {measured} vs {ref}" if ref is not None else f"Cd {measured}"
        rows.append(
            "        <tr>\n"
            f'          <td class="cal-body">{_e(title)}</td>\n'
            f'          <td class="cal-num">{vs}</td>\n'
            f'          <td class="cal-env">{_e(card["envelope"])}</td>\n'
            f'          <td>{_chip_html(tier)}</td>\n'
            f'          <td class="cal-src">{_e(card["source"])}</td>\n'
            "        </tr>"
        )
    body = "\n".join(rows)
    return f"""    <details class="cal-suite">
      <summary>
        <span class="cal-title">Calibration suite</span>
        <span class="cal-sub">{len(cards)} canonical bodies benchmarked against published experiment · {validated} validated within band</span>
        <span class="cal-hint">expand</span>
      </summary>
      <div class="cal-table-wrap">
      <table class="cal-table">
        <thead><tr><th>Body</th><th>Measured vs reference</th><th>Envelope</th><th>Tier</th><th>Source</th></tr></thead>
        <tbody>
{body}
        </tbody>
      </table>
      </div>
    </details>"""


def build_html(counters: dict, cards: list[dict]) -> str:
    canonical = [c for c in cards if c["name"] in _CANONICAL]
    real_bodies = [c for c in cards if c["name"] not in _CANONICAL]

    headline_cards = ""
    if real_bodies:
        blocks = []
        for card in real_bodies:
            title = _DISPLAY.get(card["name"], card["name"])
            tier = card["tier"]
            ref = card["reference_cd"]
            vs = f"Cd {_e(card['measured'])} vs {ref}" if ref is not None else f"Cd {_e(card['measured'])}"
            blocks.append(
                f'      <div class="cred-card">\n'
                f'        <div class="cred-card-head"><span class="cred-body">{_e(title)}</span>'
                f'{_chip_html(tier)}</div>\n'
                f'        <div class="cred-measure">{vs} <span class="cred-env">{_e(card["envelope"])}</span></div>\n'
                f'        <div class="cred-reason">{_e(card["reason"])}</div>\n'
                f'        <div class="cred-src">{_e(card["source"])}</div>\n'
                f'      </div>'
            )
        headline_cards = ('    <div class="cred-real">\n'
                          '      <h3 class="cred-section-title">Real-geometry validations</h3>\n'
                          '      <div class="cred-card-grid">\n'
                          + "\n".join(blocks) + "\n      </div>\n    </div>")

    return f"""<section class="credential-wall" aria-label="Laboratory credentials">
  <style>
    .credential-wall {{
      --wall-ink: #12130f; --wall-ink2: #5b5a52; --wall-line: #e2e1dc;
      --wall-surface: #fbfbf9; --wall-card: #ffffff; --wall-accent: #1baf7a;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: var(--wall-ink); background: var(--wall-surface);
      border: 1px solid var(--wall-line); border-radius: 14px;
      padding: 28px 30px 30px; max-width: 1100px; margin: 0 auto;
    }}
    @media (prefers-color-scheme: dark) {{
      .credential-wall {{
        --wall-ink: #f4f3ee; --wall-ink2: #b9b8ad; --wall-line: #33332e;
        --wall-surface: #171814; --wall-card: #1f201b; --wall-accent: #37c793;
      }}
    }}
    .credential-wall * {{ box-sizing: border-box; }}
    .cred-kicker {{ font-size: 12px; letter-spacing: .14em; text-transform: uppercase;
      color: var(--wall-accent); font-weight: 700; margin: 0 0 4px; }}
    .cred-title {{ font-size: 26px; font-weight: 700; margin: 0 0 20px; letter-spacing: -.01em; }}
    .cred-counters {{ display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 26px; }}
    .cred-counter {{ flex: 1 1 150px; background: var(--wall-card); border: 1px solid var(--wall-line);
      border-radius: 11px; padding: 16px 18px; display: flex; flex-direction: column; gap: 5px; }}
    .cred-counter-value {{ font-size: 30px; font-weight: 750; line-height: 1;
      font-variant-numeric: tabular-nums; }}
    .cred-counter-label {{ font-size: 12.5px; color: var(--wall-ink2);
      text-transform: uppercase; letter-spacing: .05em; }}
    .cred-section-title {{ font-size: 15px; font-weight: 700; margin: 0 0 12px; }}
    .cred-real {{ margin-bottom: 22px; }}
    .cred-card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }}
    .cred-card {{ background: var(--wall-card); border: 1px solid var(--wall-line);
      border-radius: 11px; padding: 16px 18px; }}
    .cred-card-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
    .cred-body {{ font-weight: 650; font-size: 15px; }}
    .cred-measure {{ font-size: 15px; font-variant-numeric: tabular-nums; margin-bottom: 6px; }}
    .cred-env {{ color: var(--wall-ink2); font-size: 13px; }}
    .cred-reason {{ font-size: 13px; color: var(--wall-ink2); line-height: 1.45; margin-bottom: 6px; }}
    .cred-src {{ font-size: 12px; color: var(--wall-ink2); font-style: italic; }}
    .vtier {{ font-size: 11px; font-weight: 700; letter-spacing: .05em; padding: 3px 9px;
      border-radius: 999px; white-space: nowrap; }}
    .vt-validated {{ background: rgba(27,175,122,.14); color: #12855f; }}
    .vt-reference {{ background: rgba(237,161,0,.16); color: #9a6a00; }}
    .vt-trend {{ background: rgba(42,120,214,.14); color: #1e5aa0; }}
    .vt-needs {{ background: rgba(227,73,72,.14); color: #b23433; }}
    @media (prefers-color-scheme: dark) {{
      .vt-validated {{ color: #37c793; }} .vt-reference {{ color: #edb54a; }}
      .vt-trend {{ color: #6aa4e5; }} .vt-needs {{ color: #e88; }}
    }}
    .cal-suite {{ background: var(--wall-card); border: 1px solid var(--wall-line);
      border-radius: 11px; padding: 4px 8px; }}
    .cal-suite > summary {{ cursor: pointer; list-style: none; padding: 14px 12px;
      display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }}
    .cal-suite > summary::-webkit-details-marker {{ display: none; }}
    .cal-title {{ font-weight: 700; font-size: 16px; }}
    .cal-sub {{ color: var(--wall-ink2); font-size: 13.5px; flex: 1 1 auto; }}
    .cal-hint {{ font-size: 11px; text-transform: uppercase; letter-spacing: .08em;
      color: var(--wall-accent); font-weight: 700; }}
    .cal-suite[open] .cal-hint::after {{ content: "ed"; }}
    .cal-table-wrap {{ overflow-x: auto; }}
    .cal-table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 6px 0 10px; }}
    .cal-table th {{ text-align: left; color: var(--wall-ink2); font-weight: 600;
      border-bottom: 1px solid var(--wall-line); padding: 8px 12px; font-size: 11.5px;
      text-transform: uppercase; letter-spacing: .04em; }}
    .cal-table td {{ border-bottom: 1px solid var(--wall-line); padding: 9px 12px; vertical-align: top; }}
    .cal-body {{ font-weight: 600; }}
    .cal-num {{ font-variant-numeric: tabular-nums; }}
    .cal-env, .cal-src {{ color: var(--wall-ink2); }}
    .cal-src {{ font-size: 12px; }}
    .cred-foot {{ margin-top: 18px; font-size: 12px; color: var(--wall-ink2); line-height: 1.5; }}
  </style>
  <div class="cred-kicker">Certonomous · laboratory credentials</div>
  <h2 class="cred-title">What this lab has measured</h2>
{_counter_html(counters)}
{headline_cards}
{_cal_row_html(canonical)}
  <p class="cred-foot">Every credential is a real evaluation on this machine, graded against a
    published experimental value within a stated band. Tiers are honest: a body earns VALIDATED
    only against an experimental anchor in-regime; otherwise it carries the tier its evidence supports.</p>
{_basis_foot_html()}
</section>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the credential-wall website asset.")
    parser.add_argument("--server", default=None,
                        help="fetch /api/credentials and /api/lab-stats from this base URL")
    args = parser.parse_args(argv)

    if args.server:
        base = args.server.rstrip("/")
        cards = _fetch_json(f"{base}/api/credentials")
        counters = _fetch_json(f"{base}/api/lab-stats")
    else:
        cards = _credentials_from_disk()
        counters = lab_stats.lifetime_counters()

    _WALL_JSON.parent.mkdir(parents=True, exist_ok=True)
    _WALL_HTML.parent.mkdir(parents=True, exist_ok=True)
    _WALL_JSON.write_text(
        json.dumps({"counters": counters, "credentials": cards}, indent=2),
        encoding="utf-8")
    _WALL_HTML.write_text(build_html(counters, cards), encoding="utf-8")
    print(f"[wall] wrote wall.html + wall.json — {counters['missions_run']:,} missions, "
          f"{len(cards)} credentials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
