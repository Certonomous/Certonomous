#!/usr/bin/env python3
"""Census of QUEUE DIVERGENCE across verification/queue/.

Answers, separately and with a planted control on every reader, the four senses
of "divergence" a supervisor might mean:

  (i)   rows on disk that diverge from what is committed at HEAD;
  (ii)  rows whose committed content diverges from the copy the daemon launched;
  (iii) LAUNCH_LOG.tsv rows with no run root, and run roots with no LAUNCH_LOG row;
  (iv)  the residue -- deleted pending rows with NO launched counterpart, which are
        the only deletions that could be a withdrawal rather than a launch.

RULE 3 (planted zero): every reader below plants a known perturbation, reads it
back through the SAME code path that produces the census, and prints
DISCRIMINATED / BLIND. A reader that prints BLIND has not reported a zero.

HAZARD (verified by the cfd supervisor on F28G L1, 2026-09-04): queue_runner.py
overwrites `_field_classes` with a FIXED TEMPLATE on every launch (see the
`meta["_field_classes"] = dict(...)` assignment in launch()). It also injects
`_launch` and the grading-freeze stamp. So EVERY launched copy differs from its
committed row in those keys, and that difference is the DAEMON's, not a team's.
Sense (ii) is therefore reported twice: raw, and with the daemon's own key set
subtracted. Only the second number can carry a team-caused finding.

Read-only. Writes nothing under verification/. Zero solver compute.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "verification" / "queue"

# Keys the daemon itself writes into the launched copy. Sourced by reading
# queue_runner.py launch(): meta["_launch"], meta["_field_classes"], and the
# grading-freeze stamp key (gfg.GRADING_FREEZE_STAMP == "_grading_freeze").
DAEMON_KEYS = {"_launch", "_field_classes", "_grading_freeze"}


def sh(args: list[str]) -> str:
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True).stdout


def head_blob(path: str) -> str | None:
    """Content of `path` at HEAD, or None if the path is not tracked at HEAD."""
    p = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=REPO,
                       capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def porcelain() -> list[tuple[str, str]]:
    out = sh(["git", "status", "--porcelain", "--", "verification/queue/"])
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        rows.append((line[:2].strip(), line[3:].strip()))
    return rows


def classify_path(path: str) -> tuple[str, str]:
    """-> (team, state) where state in {PENDING, launched, held, refused, OTHER}."""
    parts = path.split("/")
    if len(parts) < 4:
        return ("_root", "OTHER")
    team = parts[2]
    tail = parts[3]
    if tail in ("launched", "held", "refused"):
        return (team, tail)
    return (team, "PENDING")


# --------------------------------------------------------------------------
# SENSE (iv) + HAZARD 1: is a deleted pending row a LAUNCH or a WITHDRAWAL?
# --------------------------------------------------------------------------
def pair_deletions(rows, extra_deleted=None, launched_index=None):
    """For each deleted PENDING row, does a launched/ copy of the same basename exist?

    extra_deleted / launched_index are the PLANT hooks: the caller injects a
    synthetic deletion and a synthetic launched-set so the control travels the
    same code path as the real census.
    """
    if launched_index is None:
        launched_index = {}
        for team_dir in sorted(QUEUE.iterdir()):
            if not team_dir.is_dir():
                continue
            ld = team_dir / "launched"
            if ld.is_dir():
                launched_index[team_dir.name] = {p.name for p in ld.glob("*.json")}
            else:
                launched_index[team_dir.name] = set()

    deleted = [(st, p) for st, p in rows if st == "D"]
    if extra_deleted:
        deleted = deleted + list(extra_deleted)

    launch_consumed, unpaired = [], []
    for _st, path in deleted:
        team, state = classify_path(path)
        if state != "PENDING":
            continue
        name = Path(path).name
        pool = launched_index.get(team, set())
        if name in pool:
            launch_consumed.append((team, path, "exact"))
            continue
        # SECOND PAIRING RULE -- archive_previous_records(): when the same run is
        # re-armed, the PREVIOUS launched record is RENAMED to
        # `<stem>.<its _launch.utc with colons stripped>.json`. So a deleted pending
        # row can have been launched and then archived under a timestamped name, and
        # an exact-basename reader would call that a withdrawal. It is not.
        stem = name[:-5] if name.endswith(".json") else name
        arch = [c for c in pool
                if c.startswith(stem + ".") and c.endswith("Z.json")]
        if arch:
            launch_consumed.append((team, path, f"archived->{sorted(arch)[0]}"))
        else:
            unpaired.append((team, path))
    return launch_consumed, unpaired


def plant_pairing(rows) -> str:
    """PLANT: one deletion whose launched copy CANNOT exist. If the reader
    reports it as unpaired it can see a non-zero; if it lands in launch_consumed
    the reader is blind."""
    fake = ("D", "verification/queue/cfd/__PLANT_NO_SUCH_ROW__.json")
    _, unpaired = pair_deletions(rows, extra_deleted=[fake])
    seen = any(p == fake[1] for _t, p in unpaired)
    # Negative half: the same synthetic name WITH a launched counterpart must NOT
    # be reported unpaired.
    idx = {}
    for team_dir in sorted(QUEUE.iterdir()):
        if team_dir.is_dir():
            ld = team_dir / "launched"
            idx[team_dir.name] = {p.name for p in ld.glob("*.json")} if ld.is_dir() else set()
    idx.setdefault("cfd", set()).add("__PLANT_NO_SUCH_ROW__.json")
    _, unpaired2 = pair_deletions(rows, extra_deleted=[fake], launched_index=idx)
    absorbed = not any(p == fake[1] for _t, p in unpaired2)
    ok = seen and absorbed
    return (f"PLANT[pairing] injected=1 unmatched-deletion seen_as_unpaired={seen} "
            f"matched-deletion absorbed={absorbed} -> "
            f"{'DISCRIMINATED' if ok else 'BLIND'}")


# --------------------------------------------------------------------------
# SENSE (ii): committed row vs launched copy, raw and daemon-subtracted
# --------------------------------------------------------------------------
def key_diff(committed: dict, launched: dict) -> set[str]:
    keys = set(committed) | set(launched)
    return {k for k in keys if committed.get(k, "\0MISSING") != launched.get(k, "\0MISSING")}


def sense_ii(inject=None):
    """Compare every launched/*.json against the SAME BASENAME committed at HEAD.

    The committed row may live at the pending path (the daemon moved it) or
    already at the launched path (a re-arm). Both are tried.
    """
    raw, team_caused, no_committed_origin = [], [], []
    for team_dir in sorted(QUEUE.iterdir()):
        if not team_dir.is_dir():
            continue
        ld = team_dir / "launched"
        if not ld.is_dir():
            continue
        for lp in sorted(ld.glob("*.json")):
            rel_pending = f"verification/queue/{team_dir.name}/{lp.name}"
            rel_launched = f"verification/queue/{team_dir.name}/launched/{lp.name}"
            src = head_blob(rel_pending) or head_blob(rel_launched)
            if src is None:
                no_committed_origin.append((team_dir.name, lp.name))
                continue
            try:
                committed = json.loads(src)
                live = json.loads(lp.read_text())
            except json.JSONDecodeError:
                no_committed_origin.append((team_dir.name, lp.name + " [UNPARSEABLE]"))
                continue
            if inject and inject[0] == lp.name:
                committed = dict(committed)
                committed[inject[1]] = "__PLANTED_DIVERGENCE__"
            d = key_diff(committed, live)
            if d:
                raw.append((team_dir.name, lp.name, d))
            residue = d - DAEMON_KEYS
            if residue:
                team_caused.append((team_dir.name, lp.name, residue))
    return raw, team_caused, no_committed_origin


def plant_sense_ii(sample_name: str) -> str:
    """PLANT: perturb one substantive (non-daemon) key of one committed row and
    confirm the daemon-subtracted reader reports it."""
    base_raw, base_team, _ = sense_ii()
    base_names = {n for _t, n, _d in base_team}
    _r, planted_team, _n = sense_ii(inject=(sample_name, "__plant_field__"))
    planted_names = {n for _t, n, _d in planted_team}
    new = planted_names - base_names
    ok = sample_name in new or (sample_name in planted_names and sample_name not in base_names)
    return (f"PLANT[sense-ii] target={sample_name} injected=1 substantive key; "
            f"reader newly reported it={ok} -> {'DISCRIMINATED' if ok else 'BLIND'}")


# --------------------------------------------------------------------------
# SENSE (iii): LAUNCH_LOG.tsv rows vs run roots on disk
# --------------------------------------------------------------------------
def sense_iii(plant=False):
    log = QUEUE / "LAUNCH_LOG.tsv"
    missing, present, malformed = [], [], []
    lines = log.read_text().splitlines()
    if plant:
        lines = lines + ["2026-01-01T00:00:00Z\tcfd\t__PLANT_CASE__\t1\t1\t1\t1.0\t"
                         "0000000000000000000000000000000000000000\t"
                         "/home/ubuntu/Certonomous/__PLANT_NO_SUCH_DIR__/STATUS.__PLANT_CASE__"]
    for ln in lines:
        f = ln.split("\t")
        if len(f) < 9:
            malformed.append(ln[:80])
            continue
        status_path = Path(f[8])
        root = status_path.parent
        if root.is_dir():
            present.append((f[1], f[2], str(root)))
        else:
            missing.append((f[1], f[2], str(root)))
    return missing, present, malformed


def plant_sense_iii() -> str:
    base_missing, _p, _m = sense_iii(plant=False)
    planted_missing, _p2, _m2 = sense_iii(plant=True)
    seen = any(c == "__PLANT_CASE__" for _t, c, _r in planted_missing)
    delta = len(planted_missing) - len(base_missing)
    ok = seen and delta == 1
    return (f"PLANT[sense-iii] injected=1 log row naming a directory that cannot exist; "
            f"seen_as_missing={seen} delta={delta} -> "
            f"{'DISCRIMINATED' if ok else 'BLIND'}")


def main() -> int:
    rows = porcelain()
    print("=" * 78)
    print("QUEUE DIVERGENCE CENSUS -- verification/queue/")
    print("HEAD =", sh(["git", "rev-parse", "HEAD"]).strip())
    print("=" * 78)

    # ---- sense (i): disk vs HEAD, by team and state
    print("\n[SENSE i] rows on disk diverging from HEAD, by team/state/status")
    tab = {}
    for st, path in rows:
        team, state = classify_path(path)
        tab[(team, state, st)] = tab.get((team, state, st), 0) + 1
    for k in sorted(tab):
        print(f"   {k[0]:<20} {k[1]:<9} {k[2]:<3} {tab[k]:>4}")
    print(f"   TOTAL status lines under verification/queue/: {len(rows)}")

    # ---- hazard 1 / sense (iv)
    print("\n[HAZARD 1 / SENSE iv] every deleted PENDING row: launch or withdrawal?")
    print("   " + plant_pairing(rows))
    consumed, unpaired = pair_deletions(rows)
    exact = sum(1 for _t,_p,h in consumed if h=="exact")
    archd = [(t,p,h) for t,p,h in consumed if h!="exact"]
    print(f"   deleted pending rows PAIRED to a launched/ copy (= DAEMON LAUNCH): {len(consumed)}")
    print(f"      ... by exact basename: {exact}")
    print(f"      ... by ARCHIVER RENAME (archive_previous_records): {len(archd)}")
    for t,pp,h in archd:
        print(f"         ARCHIVED-PAIR {t}: {pp}  {h}")
    print(f"   deleted pending rows with NO launched copy (candidate withdrawal): {len(unpaired)}")
    for team, path in unpaired:
        print(f"      UNPAIRED {team}: {path}")
    bt = {}
    for team, _p, _how in consumed:
        bt[team] = bt.get(team, 0) + 1
    for t in sorted(bt):
        print(f"      launch-consumed {t}: {bt[t]}")

    # ---- sense (ii)
    print("\n[SENSE ii] committed row vs the copy the daemon launched")
    raw, team_caused, orphan = sense_ii()
    sample = raw[0][1] if raw else (team_caused[0][1] if team_caused else None)
    if sample:
        print("   " + plant_sense_ii(sample))
    else:
        print("   PLANT[sense-ii] NOT RUN: no comparable row -> BLIND")
    print(f"   launched copies differing from their committed row (RAW): {len(raw)}")
    print(f"   ... after subtracting the daemon's own keys {sorted(DAEMON_KEYS)}: {len(team_caused)}")
    print(f"   launched copies with NO committed origin at HEAD: {len(orphan)}")
    keyhist = {}
    for _t, _n, d in raw:
        for k in d:
            keyhist[k] = keyhist.get(k, 0) + 1
    print("   histogram of differing keys across RAW set:")
    for k in sorted(keyhist, key=lambda x: -keyhist[x]):
        tag = "DAEMON" if k in DAEMON_KEYS else "TEAM?"
        print(f"      {k:<28} {keyhist[k]:>4}  [{tag}]")
    if team_caused:
        print("   TEAM-CAUSED residue (each named):")
        for t, n, d in team_caused:
            print(f"      {t}: {n}  keys={sorted(d)}")

    # ---- sense (iii)
    print("\n[SENSE iii] LAUNCH_LOG.tsv rows vs run roots on disk")
    print("   " + plant_sense_iii())
    missing, present, malformed = sense_iii()
    print(f"   LAUNCH_LOG rows total: {len(missing) + len(present) + len(malformed)}")
    print(f"   rows whose run root EXISTS: {len(present)}")
    print(f"   rows whose run root IS ABSENT: {len(missing)}")
    print(f"   malformed rows: {len(malformed)}")
    mt = {}
    for t, _c, _r in missing:
        mt[t] = mt.get(t, 0) + 1
    for t in sorted(mt):
        print(f"      absent-root rows, team {t}: {mt[t]}")
    for t, c, r in missing:
        print(f"      ABSENT {t}/{c}: {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
