"""Write the validation-hierarchy tiers and credibility scorecards to the record.

Two approved agenda items land here, and they answer the same question from
two directions: what is the ceiling on the trust a result may carry, and what
does its fidelity chip not tell you.

- ``r1-validation-tier-labels`` places every case the lab holds in the
  building-block validation hierarchy, so a chip that stops short is explained
  by a structural fact about the data that exists in the world rather than by
  a hedge.
- ``r1-credibility-scorecard`` scores the two results-assessment factors the
  chips do not encode, input pedigree and results robustness, on the published
  0 to 4 scale.

NOTHING HERE CHANGES A CHIP, AND NOTHING HERE CARRIES ONE. The chip lives on
each case's own record and stays the single authority on the grade. This
artifact deliberately does not copy it, for two reasons. A second copy of a
grade in a second file is a second thing to drift. And the copy would have
dragged vocabulary along with it: two of the eight graded records on disk
still carry a retired chip and a third carries a string that was never one of
the four, all written before the current convention, and none of them mine to
rewrite. The tier and the scorecard sit beside a chip and explain it; they
never restate it.

The scorecard levels are computed from what each record actually carries, so a
case cannot score for evidence it does not have. A case the lab has placed in
the hierarchy but has not graded gets its tier and no scorecard at all, which
is the honest answer rather than a row of zeros.

Usage::

    python3 sdk/scripts/build_credibility_record.py [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import credibility as cred  # noqa: E402
from chief_engineer.display_names import display_name  # noqa: E402

RESULTS = SDK.parent / "models" / "curriculum" / "results"
DEFAULT_OUT = (SDK.parent / "demo-output" / "website" / "credibility"
               / "validation_tiers.json")

PURPOSE = (
    "Where every case the lab holds sits in the building-block validation "
    "hierarchy, and how well its inputs and its sensitivities are known. "
    "A tier states the ceiling on the trust a result may carry. A scorecard "
    "states the two things a fidelity chip does not encode. Neither changes "
    "what any chip means, and neither is a grade. This is the permanent "
    "record and it is complete: it holds every case the lab has placed, "
    "including the calibration bodies that never appear on a promotional "
    "surface."
)


def _graded_records() -> dict[str, dict]:
    """Every graded case on disk, keyed by the slug the hierarchy uses."""
    out: dict[str, dict] = {}
    if not RESULTS.is_dir():
        return out
    for path in sorted(RESULTS.glob("*.json")):
        try:
            out[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def _is_fallback_name(slug: str, name: str) -> bool:
    """Whether the display-name registry had no entry and fell back.

    The registry's documented fallback title-cases the slug, which reads as a
    slug on any surface that shows it. This never guesses a better name: the
    registry is the one ratified mapping and a second one next to it would be
    exactly the drift it exists to prevent. The record says which names are
    unregistered so a surface can decline to show them and the gap gets fixed
    in the registry rather than here.
    """
    fallback = slug.replace("_", " ").strip()
    fallback = fallback[:1].upper() + fallback[1:]
    return name == fallback


def build() -> dict:
    graded = _graded_records()
    cases = []
    unregistered = []
    for slug in sorted(cred.labelled_cases()):
        label = cred.tier_label(slug)
        name = display_name(slug)
        registered = not _is_fallback_name(slug, name)
        if not registered:
            unregistered.append(slug)
        row = {
            "case": slug,
            "display_name": name,
            "display_name_registered": registered,
            "validation_tier": label["validation_tier"],
            "rank": label["rank"],
            "of": label["of"],
            "basis": label["basis"],
            "data_available": label["data_available"],
            "ceiling": label["ceiling"],
            "unlocked_by": label["unlocked_by"],
        }
        record = graded.get(slug)
        if record:
            row["credibility"] = cred.scorecard(record)
        cases.append(row)
    return {
        "artifact": "validation tiers and credibility scorecards",
        "purpose": PURPOSE,
        "generated_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "hierarchy": [
            {"validation_tier": tier, "rank": index + 1,
             "of": len(cred.VALIDATION_TIERS),
             **cred.TIER_NOTES[tier]}
            for index, tier in enumerate(cred.VALIDATION_TIERS)
        ],
        "scorecard_scale": f"0 to {cred.MAX_LEVEL}",
        "scorecard_factors": [
            {"factor": factor,
             "levels": [{"level": level, "note": note}
                        for level, note in sorted(levels.items())]}
            for factor, levels in ((cred.INPUT_PEDIGREE, cred.PEDIGREE_LEVELS),
                                   (cred.RESULTS_ROBUSTNESS,
                                    cred.ROBUSTNESS_LEVELS))
        ],
        "citations": [cred.OBERKAMPF_CITATION, cred.NASA_CITATION],
        "cases_without_a_registered_display_name": unregistered,
        "cases": cases,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    record = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(args.out.suffix + ".partial")
    temporary.write_text(json.dumps(record, indent=2, ensure_ascii=False),
                         encoding="utf-8")
    temporary.replace(args.out)
    scored = sum(1 for case in record["cases"] if "credibility" in case)
    print(f"{len(record['cases'])} cases placed in the hierarchy, "
          f"{scored} of them graded and scored")
    print(f"written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
