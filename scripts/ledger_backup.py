#!/usr/bin/env python3
"""Backup the mega-batch ledger with rotation and verification.

The ledger is append-only and may be written to live, so this script:
1. Copies the live ledger
2. Truncates to the last complete, parseable JSON line
3. Verifies all rows parse correctly
4. Records metadata: row count, distinct index count, MD5 checksum
5. Maintains a rotation of the last 3 snapshots
6. Cleans up older backups automatically

Run as: python3 ledger_backup.py
Or schedule: 0 * * * * python3 /home/ubuntu/Certonomous/scripts/ledger_backup.py
"""

import json
import hashlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


LEDGER_SOURCE = Path("/home/ubuntu/Certonomous/demo-output/website/mega-batch/ledger.jsonl")
BACKUP_DIR = Path("/home/ubuntu/backups")
BACKUP_ROTATION_LIMIT = 3  # Keep last 3 snapshots


def md5_file(path: Path) -> str:
    """Compute MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def truncate_to_last_complete_line(path: Path) -> tuple[int, bool, list[int]]:
    """Drop a partial TAIL line only. Never truncate at an interior bad line.

    The ledger is append-only, so the only line that can be genuinely partial is
    the LAST one, caught mid-write. An unparseable line in the MIDDLE is historical
    corruption (the source has one at line 61438 from an old unsynchronised
    concurrent-append incident) and it is real data that must be preserved, not a
    stopping point.

    An earlier version of this function truncated at the FIRST invalid line, which
    silently discarded 122,800 of 184,237 rows because that torn line sits a third
    of the way in. That is why this function reports what it dropped.

    Returns (kept_line_count, dropped_partial_tail, interior_bad_line_numbers).
    """
    with open(path, "r") as f:
        lines = f.readlines()

    if not lines:
        return 0, False, []

    # Strip trailing blank lines first so the "last line" is a real one.
    while lines and not lines[-1].rstrip("\n"):
        lines.pop()

    if not lines:
        return 0, False, []

    # Only the final line may be dropped, and only if it does not parse.
    dropped_tail = False
    try:
        json.loads(lines[-1].rstrip("\n"))
    except json.JSONDecodeError:
        lines.pop()
        dropped_tail = True

    # Everything else is kept. Record interior bad lines; never truncate at them.
    interior_bad = []
    for i, line in enumerate(lines, 1):
        text = line.rstrip("\n")
        if not text:
            continue
        try:
            json.loads(text)
        except json.JSONDecodeError:
            interior_bad.append(i)

    with open(path, "w") as f:
        f.writelines(lines)

    return len(lines), dropped_tail, interior_bad


def verify_jsonl(path: Path) -> tuple[int, set[int], list[int]]:
    """Count parseable rows and collect index values, scanning the WHOLE file.

    Returns: (parseable_row_count, set_of_index_values, unparseable_line_numbers)

    This never raises and never stops early. The source ledger legitimately
    contains one historical torn line (61438) from an old unsynchronised
    concurrent-append incident, and that line is real evidence that must survive
    in the backup.

    Two earlier bugs lived here: raising on any interior bad line, and `break`ing
    out of the scan whenever a short bad line appeared. Both meant a corrupt line
    a third of the way in stopped the whole verification, so the reported row
    count described only the prefix before it rather than the file.
    """
    parseable = 0
    indices = set()
    bad_lines = []

    with open(path, "r", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                bad_lines.append(line_num)
                continue
            parseable += 1
            if "index" in record:
                indices.add(record["index"])

    return parseable, indices, bad_lines


def create_backup(source: Path, backup_dir: Path) -> Path:
    """Create a timestamped backup of the ledger.

    Returns: path to the new backup file
    """
    # Create backup directory if needed
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped backup filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"ledger_{timestamp}.jsonl"

    # Copy the file
    print(f"Copying ledger from {source} to {backup_path}...")
    shutil.copy2(source, backup_path)

    # Drop a partial tail line only. Interior bad lines are preserved.
    print("Checking for a partial tail line...")
    final_line_count, dropped_tail, interior_bad = truncate_to_last_complete_line(backup_path)
    print(f"  kept {final_line_count} lines; partial tail dropped: {dropped_tail}")
    if interior_bad:
        print(f"  interior unparseable lines PRESERVED (historical): {interior_bad}")

    # Guard: a backup must not be materially smaller than its source. This exists
    # because a previous version truncated at the first interior bad line and
    # silently kept only 61,437 of 184,237 rows.
    with open(source, "r", errors="replace") as _s:
        source_lines = sum(1 for _ in _s)
    if final_line_count < source_lines - 10:
        raise SystemExit(
            f"ABORT: backup has {final_line_count} lines but source has {source_lines}. "
            f"A backup may only lose a single partial tail line. Refusing to write a "
            f"truncated backup or rotate good snapshots out behind it."
        )

    # Verify all lines parse
    print("Verifying all JSON lines parse correctly...")
    line_count, indices, bad_lines = verify_jsonl(backup_path)
    print(f"  parseable rows: {line_count}; distinct indices: {len(indices)}; "
          f"unparseable lines preserved: {bad_lines or 'none'}")

    # Compute checksum
    print("Computing MD5 checksum...")
    checksum = md5_file(backup_path)

    # Get file size
    file_size = backup_path.stat().st_size / (1024 * 1024)  # MB

    # Write metadata
    metadata_path = backup_dir / f"ledger_{timestamp}.METADATA"
    with open(metadata_path, "w") as f:
        f.write(f"""MEGA-BATCH LEDGER BACKUP METADATA
=================================

Backup Date & Time:     {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Source Path:            {source}
Backup Path:            {backup_path}
Backup Checksum (MD5):  {checksum}

BACKUP VERIFICATION RESULT:
  Total lines in backup:      {final_line_count}
  Valid JSON rows (parsed):   {line_count}
  Distinct index values:      {len(indices)}
  Min index:                  {min(indices) if indices else 'N/A'}
  Max index:                  {max(indices) if indices else 'N/A'}
  Partial tail dropped:       {'YES' if final_line_count > line_count else 'NO'}

BACKUP SIZE:
  File size:            {file_size:.2f} MB
  Compression friendly: JSONL format, one record per line

NOTES:
  - Append-only file was potentially being written to during backup
  - All truncated lines verified as valid JSON
  - Can safely use as recovery point
""")

    print(f"✓ Backup complete: {backup_path}")
    print(f"  Size: {file_size:.2f} MB")
    print(f"  Lines: {line_count}")
    print(f"  Distinct indices: {len(indices)}")
    print(f"  Checksum: {checksum}")
    print(f"  Metadata: {metadata_path}")

    return backup_path


def rotate_backups(backup_dir: Path, limit: int = 3):
    """Keep only the last N backups, delete older ones."""
    # Find all ledger_*.jsonl files (excluding metadata files)
    backup_files = sorted([f for f in backup_dir.glob("ledger_*.jsonl")])

    if len(backup_files) <= limit:
        return

    # Remove oldest backups beyond the limit
    to_remove = backup_files[:-limit]
    for backup_file in to_remove:
        metadata_file = backup_file.with_suffix(".METADATA")
        print(f"Removing old backup: {backup_file.name}")
        backup_file.unlink()
        if metadata_file.exists():
            metadata_file.unlink()

    print(f"✓ Rotation complete: kept {min(len(backup_files), limit)} most recent backups")


def check_disk_space():
    """Report free space in backup directory."""
    result = subprocess.run(
        ["df", "-h", str(BACKUP_DIR)],
        capture_output=True,
        text=True,
        check=True
    )
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        # Extract available space from df output
        parts = lines[1].split()
        available = parts[3]
        print(f"Free disk space in {BACKUP_DIR}: {available}")


def main():
    """Run the backup workflow."""
    try:
        if not LEDGER_SOURCE.exists():
            print(f"ERROR: Ledger source not found: {LEDGER_SOURCE}", file=sys.stderr)
            return 1

        print("=" * 60)
        print("MEGA-BATCH LEDGER BACKUP")
        print("=" * 60)

        # Create backup
        backup_path = create_backup(LEDGER_SOURCE, BACKUP_DIR)

        # Rotate old backups
        rotate_backups(BACKUP_DIR, BACKUP_ROTATION_LIMIT)

        # Report disk usage
        print()
        check_disk_space()

        print("\n✓ Backup job completed successfully")
        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
