#!/usr/bin/env python3
"""Assemble the offline laptop bundle -- the backup console for the shoot.

    python3 scripts/build_laptop_bundle.py [--out DIR] [--state DIR]
                                           [--output-root DIR] [--zip]

WHAT GOES IN, AND WHY IT IS SMALL
---------------------------------
The bundle replays recorded missions; it does not run solvers. So it needs
the control-room code (pure standard library -- verified), the recorded
mission events, and ONLY the artifact files those recordings actually point
at. The main install's mission-output is 467 MB because it accumulates every
run ever made; the four filmed acts reference a small fraction of it, so this
walks each recording, collects the /api/plot, /api/field, /api/surface and
/api/certificate URLs it mentions, and copies just those.

WHAT IS DELIBERATELY LEFT OUT
-----------------------------
The mesh and solve caches (654 MB). They are inputs to OpenFOAM, and OpenFOAM
cannot run on the laptop, so shipping them would add 654 MB that nothing in
the bundle could read.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[1]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

# The four filmed acts, in running order.
WANTED_INTENTS = ("aircraft-optimization", "nasa-hump",
                  "geometry-study", "race-comparison")

ARTIFACT_RE = re.compile(r"/api/(plot|field|surface|certificate)/([A-Za-z0-9._-]+)"
                         r"(?:/([A-Za-z0-9._-]+))?")

# The certificate is the one artifact whose URL is never written down. Plots,
# fields and surfaces arrive in the recording as "/api/plot/..." strings, so
# scanning the text finds them. The certificate arrives as a `certificate.ready`
# event carrying a directory, and the browser builds "/api/certificate/<dir>"
# at render time -- so the scan matched nothing and every bundle ever built
# shipped zero certificates. The link on the laptop answered "no certificate
# for this mission" on all four acts, which is the sealed evidence page the
# whole demo ends on.
CERTIFICATE_EVENT = "certificate.ready"

SITE_PAGES = ("closure.html", "benchmarks.html")


def mission_intent(events_path: Path) -> str | None:
    try:
        with events_path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                event = json.loads(line)
                if event.get("event") == "mission.routed":
                    return event["payload"].get("intent")
    except (OSError, ValueError, KeyError):
        return None
    return None


def mission_candidates(state_dir: Path) -> dict[str, list[tuple[str, Path, Path]]]:
    """Every COMPLETE recording per filmed intent, most recently finished first."""
    found: dict[str, list[tuple[float, str, Path, Path]]] = {}
    for meta_path in state_dir.glob("m-*.json"):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if meta.get("state") != "complete":
            continue
        events_path = meta_path.with_suffix(".events.jsonl")
        if not events_path.exists():
            continue
        intent = mission_intent(events_path)
        if intent not in WANTED_INTENTS:
            continue
        stamp = float(meta.get("finished_at") or 0)
        found.setdefault(intent, []).append(
            (stamp, str(meta["mission_id"]), meta_path, events_path))
    return {intent: [(m, meta, ev) for _, m, meta, ev
                     in sorted(rows, key=lambda r: r[0], reverse=True)]
            for intent, rows in found.items()}


# --------------------------------------------------------------------------
# Certificate pairing
# --------------------------------------------------------------------------
#
# THE BUG THIS EXISTS TO MAKE IMPOSSIBLE (docket D136).
#
# A recording is FROZEN: `<mission>.events.jsonl` states, in its
# `certificate.ready` event, the exact seal and certificate number the page
# carried when that mission ran. The artifact path is MUTABLE: every later run
# of the same act rewrites `mission-output/<dir>/certificate.pdf`, and rewrites
# it after `withdraw_certificate()` has deleted the previous page. Picking the
# newest recording and then copying whatever occupies the path today pairs the
# two only by luck, and the luck ran out on 2026-08-10: five consecutive
# bundles shipped an airliner recording announcing seal d889461d... /
# C-2026-0918 beside a PDF printing aeccc6bf... / C-2026-5686.
#
# That is camera-facing. `control_room.html` renders `EVIDENCE SEAL <the
# EVENT's hash>` directly above a link to the PDF, so on the laptop the console
# shows one seal and the certificate one click away shows another -- the demo's
# own tamper-evidence claim visibly failing, in Act 1, inside the only artifact
# that leaves this box.
#
# Two mechanisms below, and they are deliberately both:
#   1. SELECTION. `pick_missions` no longer takes the newest recording on
#      faith. It walks the complete recordings newest-first and takes the
#      first one whose certificate events AGREE with the files on disk, so a
#      recording is chosen because the artifact describes it, not because it
#      happens to be last. This is the fix: several intents share one output
#      directory, so "newest complete mission of this intent" was never the
#      same question as "the run that wrote this file".
#   2. ASSERTION. `check_bundle_pairing` re-reads the COPIED bundle and
#      compares event seal to PDF seal on the shipped bytes. It is not an
#      optional script and there is no flag to skip it: `main` refuses to
#      finish the build when it finds a disagreement, because a bundle that
#      contradicts itself is worse than no bundle.
#
# Unverifiable counts as failure. If a certificate's seal cannot be read out
# of the PDF, the pairing is not guaranteed, and an unguaranteed pairing is
# exactly what shipped for five builds.

_SEAL_RE = re.compile(rb"\(([0-9a-f]{32})\)\s*Tj")
_SERIAL_RE = re.compile(rb"\(C-\d{4}-\d{4}\)\s*Tj")


def pdf_identity(pdf_path: Path) -> tuple[str | None, str | None]:
    """(seal, certificate_no) as PRINTED on a certificate PDF, or (None, None).

    The page renders the SHA-256 in two 32-hex halves (`seal[:32]`, `seal[32:]`
    -- see `certificate.py`), so the seal is the first two halves concatenated.
    The content streams these certificates carry are uncompressed, which is why
    a plain byte scan reaches them; a compressed page yields None and, by the
    rule above, fails the build rather than passing unchecked.
    """
    try:
        raw = pdf_path.read_bytes()
    except OSError:
        return (None, None)
    halves = _SEAL_RE.findall(raw)
    seal = (halves[0] + halves[1]).decode("ascii") if len(halves) >= 2 else None
    serial_hit = _SERIAL_RE.search(raw)
    serial = serial_hit.group(0)[1:-4].strip().decode("ascii") if serial_hit else None
    if serial:
        serial = serial.rstrip(")").strip()
    return (seal, serial)


def certificate_expectations(events_path: Path) -> dict[str, dict[str, str]]:
    """{<output-dir>: {"hash": ..., "certificate_no": ...}} the recording states.

    This is the frozen half of the pair: what the console will display on
    camera when it replays this recording.
    """
    expected: dict[str, dict[str, str]] = {}
    for line in events_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if CERTIFICATE_EVENT not in line:
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("event") != CERTIFICATE_EVENT:
            continue
        payload = event.get("payload") or {}
        directory = str(payload.get("dir") or "").strip()
        if not directory or "/" in directory or directory in (".", ".."):
            continue
        expected[directory] = {
            "hash": str(payload.get("hash") or ""),
            "certificate_no": str(payload.get("certificate_no") or ""),
        }
    return expected


def pairing_faults(events_path: Path, output_root: Path, *,
                   require_present: bool = False) -> list[str]:
    """Every way this recording disagrees with the certificates on disk.

    Empty list means the pair is safe to ship. A certificate that is present
    and says something else is always a fault.

    `require_present` separates the two callers, and the difference matters.
    SELECTION passes True: a recording is only worth choosing if the page it
    announces actually exists to be paired with, since an act whose console
    announces a seal and whose link opens nothing is a different camera-facing
    failure from the same root. The GATE passes False, because by then the copy
    step has already reported referenced-but-absent artifacts by name and a
    bundle carrying no certificate contradicts nobody.
    """
    faults: list[str] = []
    for directory, expected in sorted(certificate_expectations(events_path).items()):
        pdf = output_root / directory / "certificate.pdf"
        if not pdf.exists():
            if require_present:
                faults.append(f"{directory}: recording announces "
                              f"{expected['certificate_no'] or 'a certificate'} "
                              f"but no page exists at {pdf}")
            continue
        seal, serial = pdf_identity(pdf)
        if seal is None:
            faults.append(f"{directory}: seal unreadable in {pdf} "
                          f"(pairing cannot be guaranteed)")
            continue
        if expected["hash"] and seal != expected["hash"]:
            faults.append(
                f"{directory}: recording says seal {expected['hash'][:16]}... "
                f"but {pdf.name} prints {seal[:16]}...")
        if expected["certificate_no"] and serial and serial != expected["certificate_no"]:
            faults.append(
                f"{directory}: recording says {expected['certificate_no']} "
                f"but {pdf.name} prints {serial}")
    return faults


def pick_missions(state_dir: Path,
                  output_root: Path) -> tuple[dict[str, tuple[str, Path, Path]],
                                              dict[str, list[str]]]:
    """The newest COMPLETE recording per intent whose certificates match disk.

    Returns (picked, rejected) where `rejected` maps an intent to the reasons
    each newer candidate was passed over, so a build that ends up with nothing
    for an intent can say why rather than silently shipping a mismatch.
    """
    picked: dict[str, tuple[str, Path, Path]] = {}
    rejected: dict[str, list[str]] = {}
    for intent, candidates in mission_candidates(state_dir).items():
        for mission_id, meta_path, events_path in candidates:
            # A recording that seals nothing cannot be checked against
            # anything, so "no faults" would be vacuously true for it. Taking
            # such a recording would trade a contradictory certificate for a
            # MISSING one and report it only as a count -- the sealed page is
            # the beat every act ends on, so that is not an improvement and it
            # must not be reached silently.
            if not certificate_expectations(events_path):
                rejected.setdefault(intent, []).append(
                    f"{mission_id}: no certificate.ready event to pair "
                    f"(an act must ship the sealed page it ends on)")
                continue
            faults = pairing_faults(events_path, output_root,
                                    require_present=True)
            if not faults:
                picked[intent] = (mission_id, meta_path, events_path)
                break
            rejected.setdefault(intent, []).extend(
                f"{mission_id}: {f}" for f in faults)
    return picked, rejected


def pick_unpairable(state_dir: Path, output_root: Path,
                    intents) -> dict[str, tuple[str, Path, Path, list[str]]]:
    """Last resort for an act NO recording can be paired with (docket D177).

    `pick_missions` is right to refuse a contradictory pair, but refusing the
    PAIR was implemented as refusing the ACT, and those are not the same size.
    The airliner act is fifteen zip members: one certificate, nine `.stl`, three
    `.png` and the two recording files. Twelve of those artifacts are on disk,
    unambiguous and referenced by the recording; only the certificate disagrees.
    Dropping all fifteen to withhold the one is a fourteen-member overcorrection,
    and it happened silently enough that a rebuild-and-commit remedy was printed
    and costed as `one command` while it shipped a demo missing an entire act.

    So: for an intent with no paired recording, take the newest complete
    recording that seals something and whose NON-certificate artifacts are all
    present, ship those, and withhold the certificate by name. The caller must
    write the withdrawal note and must not exit 0 -- an act without its sealed
    page is a real loss, it is just a smaller and a NAMED one. Nothing here
    relaxes `check_bundle_pairing`: no contradicting PDF is copied, so the gate
    on the shipped bytes still passes on truth rather than on tolerance.

    Returns {intent: (mission_id, meta_path, events_path, faults)} where
    `faults` is why the certificate could not be paired.
    """
    fallback: dict[str, tuple[str, Path, Path, list[str]]] = {}
    wanted = set(intents)
    for intent, candidates in mission_candidates(state_dir).items():
        if intent not in wanted:
            continue
        for mission_id, meta_path, events_path in candidates:
            if not certificate_expectations(events_path):
                continue
            absent = [f"{d}/{f}" for d, f in sorted(referenced_artifacts(events_path))
                      if f != "certificate.pdf" and not (output_root / d / f).exists()]
            if absent:
                continue
            faults = pairing_faults(events_path, output_root,
                                    require_present=True)
            if not faults:  # pick_missions would have taken it
                continue
            fallback[intent] = (mission_id, meta_path, events_path, faults)
            break
    return fallback


def withheld_directories(events_path: Path, output_root: Path) -> list[str]:
    """The announced certificate directories this recording cannot be paired to.

    Per DIRECTORY, not per recording: an act that seals two pages and disagrees
    about one of them must still ship the one it agrees about.
    """
    bad: list[str] = []
    for directory in sorted(certificate_expectations(events_path)):
        pdf = output_root / directory / "certificate.pdf"
        if not pdf.exists():
            bad.append(directory)
            continue
        seal, serial = pdf_identity(pdf)
        expected = certificate_expectations(events_path)[directory]
        if seal is None:
            bad.append(directory)
        elif expected["hash"] and seal != expected["hash"]:
            bad.append(directory)
        elif (expected["certificate_no"] and serial
              and serial != expected["certificate_no"]):
            bad.append(directory)
    return bad


def check_bundle_pairing(bundle: Path) -> list[str]:
    """Re-check the pairing on the SHIPPED bytes, inside the built bundle.

    Selection above chose a matching pair out of the lab tree; this reads the
    copies actually in the archive, so a copy that went to the wrong place, or
    a path rewritten between selection and copy, is still caught.
    """
    state_dir = bundle / "mission-state"
    output_root = bundle / "mission-output"
    faults: list[str] = []
    for events_path in sorted(state_dir.glob("m-*.events.jsonl")):
        faults.extend(f"{events_path.name} -> {f}"
                      for f in pairing_faults(events_path, output_root))
    return faults


def referenced_artifacts(events_path: Path) -> set[tuple[str, str]]:
    """(<output-dir>, <filename>) pairs a recording points at."""
    found: set[tuple[str, str]] = set()
    text = events_path.read_text(encoding="utf-8", errors="replace")
    for kind, first, second in ARTIFACT_RE.findall(text):
        if kind == "certificate":
            found.add((first, "certificate.pdf"))
        elif second:
            found.add((first, second))
    # The certificate, which no URL in the text names. Read the event instead
    # and take the directory it states, which is the same value the control
    # room puts in the link it builds.
    for line in text.splitlines():
        if CERTIFICATE_EVENT not in line:
            continue
        try:
            payload = json.loads(line).get("payload") or {}
        except ValueError:
            continue
        directory = str(payload.get("dir") or "").strip()
        if directory and "/" not in directory and directory not in (".", ".."):
            found.add((directory, "certificate.pdf"))
    return found


def _capture_panels() -> dict:
    """Compute the credentials wall and lab-stats header with the full repo
    present, so the bundle serves the same values the lab box does."""
    sys.path.insert(0, str(REPO / "sdk"))
    # Make sure the derived panels read the REPO's data, not any bundle
    # override that happens to be in the environment.
    for key in ("CERTONOMOUS_CREDENTIALS", "CERTONOMOUS_MEGABATCH_LEDGER",
                "CERTONOMOUS_OUTPUT", "CHIEF_ENGINEER_STATE_DIR"):
        os.environ.pop(key, None)
    captured: dict = {}
    try:
        from chief_engineer import server as cr
        captured["credentials"] = cr._credentials()
    except Exception as exc:  # a snapshot is best-effort, never fatal
        print(f"  WARNING: credentials snapshot failed: {exc}")
        captured["credentials"] = []
    try:
        from chief_engineer import lab_stats
        captured["lab_stats"] = lab_stats.lifetime_counters()
    except Exception as exc:
        print(f"  WARNING: lab-stats snapshot failed: {exc}")
        captured["lab_stats"] = {}
    return captured


def copy_tree(src: Path, dst: Path, *, ignore_pycache: bool = True) -> None:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc") if ignore_pycache else None
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path,
                        default=REPO / "dist" / "certonomous-demo")
    parser.add_argument("--state", type=Path,
                        default=REPO / "sdk" / "chief-engineer-runs" / "mission-state")
    parser.add_argument("--output-root", type=Path, default=REPO / "mission-output")
    parser.add_argument("--zip", action="store_true", help="also write a .zip beside --out")
    args = parser.parse_args()

    out = args.out.resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # ---- 1. the control-room code (standard library only) ----------------
    copy_tree(REPO / "sdk" / "chief_engineer", out / "sdk" / "chief_engineer")
    # workflows/ is NOT copied: it is only reachable from the launch path,
    # which this bundle closes, and it pulls in numpy/scipy/matplotlib.
    (out / "sdk" / "chief_engineer" / "__init__.py").touch(exist_ok=True)

    # ---- 2. the recorded missions ----------------------------------------
    picked, rejected = pick_missions(args.state, args.output_root)
    fallback = pick_unpairable(args.state, args.output_root,
                               [i for i in WANTED_INTENTS if i not in picked])
    withheld: dict[str, list[str]] = {}   # output directory -> why
    for intent, (mission_id, meta_path, events_path, faults) in fallback.items():
        picked[intent] = (mission_id, meta_path, events_path)
        for directory in withheld_directories(events_path, args.output_root):
            withheld[directory] = faults
    missing = [i for i in WANTED_INTENTS if i not in picked]
    for intent in WANTED_INTENTS:
        for reason in rejected.get(intent, []):
            print(f"  SKIPPED  {intent:24s} {reason}")
    state_out = out / "mission-state"
    state_out.mkdir(parents=True)
    artifacts: set[tuple[str, str]] = set()
    for intent in WANTED_INTENTS:
        if intent not in picked:
            continue
        mission_id, meta_path, events_path = picked[intent]
        shutil.copy2(meta_path, state_out / meta_path.name)
        shutil.copy2(events_path, state_out / events_path.name)
        artifacts |= referenced_artifacts(events_path)
        print(f"  mission  {intent:24s} {mission_id}")

    # ---- 3. only the artifacts those recordings point at ------------------
    copied = skipped = 0
    absent: list[str] = []
    for directory, filename in sorted(artifacts):
        if filename == "certificate.pdf" and directory in withheld:
            continue    # named below and left out on purpose, not lost
        src = args.output_root / directory / filename
        if not src.exists():
            skipped += 1
            absent.append(f"{directory}/{filename}")
            continue
        dst = out / "mission-output" / directory / filename
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    certs = sorted(d for d, f in artifacts
                   if f == "certificate.pdf" and d not in withheld)
    print(f"  certificates {len(certs)} of {len(picked)} acts: "
          f"{', '.join(certs) if certs else 'NONE'}")

    # The withdrawal note travels INSIDE the archive. A count printed on a
    # terminal that nobody kept is how fifteen members went missing under a
    # remedy costed at "one command"; a file in the bundle is readable by
    # whoever opens the bundle, which is the person the omission is about.
    for directory, faults in sorted(withheld.items()):
        note = out / "mission-output" / directory / "CERTIFICATE_WITHDRAWN.txt"
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            "No certificate is shipped for this act.\n\n"
            "The recording in this bundle announces a seal, and the page at "
            f"mission-output/{directory}/certificate.pdf on the lab box "
            "describes a different run, so shipping it would put one seal in "
            "the console and another one click away. The rest of the act -- "
            "the recording and every geometry and plot it references -- is "
            "here and is unchanged.\n\n"
            + "".join(f"  {f}\n" for f in faults)
            + "\nThe repair is to re-run this act through the control room so "
              "that one run writes both the recording and the certificate; it "
              "is not to copy whatever occupies the path today.\n",
            encoding="utf-8")
        print(f"  WITHHELD  {directory}/certificate.pdf -- "
              f"{len(faults)} pairing fault(s), note written beside it")

    # ---- 4. the standing panels, as a build-time snapshot -----------------
    # These two panels are DERIVED, not stored: the credentials wall re-grades
    # each body at serve time against the refinement ladders on disk, and the
    # lab-stats header counts 208k rows out of a 97 MB mega-batch ledger.
    #
    # Copying only the small inputs gets both WRONG, and wrong in the worst
    # direction: with the ladders absent, three bodies re-graded from
    # SOLVER-BACKED up to VALIDATED -- the bundle would have claimed more than
    # the lab box does. So the values are computed here, once, with the whole
    # repo present, and shipped as a snapshot the console serves verbatim.
    snapshot_dir = out / "snapshot"
    snapshot_dir.mkdir(parents=True)
    snapshot = _capture_panels()
    for name, payload in snapshot.items():
        (snapshot_dir / f"{name}.json").write_text(
            json.dumps(payload, indent=1), encoding="utf-8")
    creds_count = len(snapshot.get("credentials") or [])
    stats = snapshot.get("lab_stats") or {}
    print(f"  snapshot credentials {creds_count} cards, "
          f"lab-stats {stats.get('missions_run', '?')} evaluations / "
          f"{stats.get('solver_core_hours', '?')} core-hours")

    # ---- 5. the static site (self-contained pages, audited: no CDN) -------
    site_out = out / "site"
    site_out.mkdir(parents=True)
    website = lab_paths.WEB
    for page in SITE_PAGES:
        if (website / page).exists():
            shutil.copy2(website / page, site_out / page)
    if (website / "wall" / "wall.html").exists():
        (site_out / "wall").mkdir(exist_ok=True)
        shutil.copy2(website / "wall" / "wall.html", site_out / "wall" / "wall.html")

    # ---- 6. launchers and the guide --------------------------------------
    here = lab_paths.LAPTOP_BUNDLE
    for name in ("replay_console.py", "run-demo.sh", "run-demo.ps1", "START-HERE.md"):
        if (here / name).exists():
            shutil.copy2(here / name, out / name)
    os.chmod(out / "run-demo.sh", 0o755)

    # ---- report -----------------------------------------------------------
    total = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"\nBundle: {out}")
    print(f"  artifacts copied {copied}, referenced-but-absent {skipped}")
    print(f"  size {total / 1024 / 1024:.1f} MB")
    if absent:
        print(f"  WARNING: referenced but absent: {', '.join(absent)}")
    if withheld:
        print(f"\n  WARNING: the certificate is WITHHELD for: "
              f"{', '.join(sorted(withheld))}")
        print("  Those acts ship complete except for the sealed page, with "
              "CERTIFICATE_WITHDRAWN.txt beside it saying why. This build "
              "does NOT exit 0: an act without its certificate is a real "
              "loss, it is only a named and a much smaller one than dropping "
              "the act.")
    if missing:
        print(f"\n  WARNING: no complete recording could be PAIRED with the "
              f"certificate on disk for: {', '.join(missing)}")
        print("  Those acts are absent from this bundle rather than shipped "
              "with a certificate describing a different run. The SKIPPED "
              "lines above say which recording disagreed and how.")

    # ---- 7. the pairing gate, on the shipped bytes ------------------------
    # Not optional, and deliberately BEFORE the zip: a bundle whose console
    # announces one seal and whose certificate prints another must not become
    # an archive that leaves this box. See the pairing note above (D136).
    faults = check_bundle_pairing(out)
    if faults:
        print("\n  BUILD REFUSED: event seal does not match the certificate "
              "it is paired with")
        for fault in faults:
            print(f"    {fault}")
        print("  Nothing was zipped. The bundle at "
              f"{out} is INTERNALLY CONTRADICTORY and must not ship.")
        return 2
    print("  pairing  every bundled event seal matches its bundled certificate")

    # A whole filmed act missing is not something a caller should be able to
    # ship by ignoring an exit code. The gate above refuses to zip a bundle
    # that contradicts itself; this refuses to zip one that is short an act,
    # which is the failure that actually reached the owner as "one command".
    if missing and args.zip:
        print("\n  NOT ZIPPED: a filmed act is absent, so no archive was "
              "written. Fix the pairing (or pass --out and inspect) rather "
              "than shipping a bundle that is short an act.")
        return 3

    if args.zip:
        archive = shutil.make_archive(str(out), "zip", root_dir=out.parent,
                                      base_dir=out.name)
        print(f"  zip  {archive}  "
              f"({Path(archive).stat().st_size / 1024 / 1024:.1f} MB)")
    if missing:
        return 3
    return 1 if withheld else 0


if __name__ == "__main__":
    sys.exit(main())
