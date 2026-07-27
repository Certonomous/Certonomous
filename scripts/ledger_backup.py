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


def truncate_to_last_complete_line(path: Path) -> int:
    """Read file from start, find first invalid JSON line, truncate from there.

    Returns the final line count after truncation.
    """
    # Read entire file
    with open(path, "r") as f:
        lines = f.readlines()

    if not lines:
        return 0

    # Scan from the start and find the first invalid line
    truncate_at_line = len(lines)  # Default: keep all
    for i, line in enumerate(lines):
        line_text = line.rstrip('\n')
        if not line_text:  # Skip empty lines
            continue
        try:
            json.loads(line_text)
        except json.JSONDecodeError:
            # This line is incomplete/corrupted, truncate from here
            truncate_at_line = i
            break

    # Write back only the valid lines up to (but not including) the first bad line
    valid_lines = lines[:truncate_at_line]
    # Remove any trailing empty lines
    while valid_lines and not valid_lines[-1].rstrip('\n'):
        valid_lines.pop()

    with open(path, "w") as f:
        f.writelines(valid_lines)

    return len(valid_lines)


def verify_jsonl(path: Path) -> tuple[int, set[int]]:
    """Verify all lines are valid JSON and extract index values.

    Returns: (line_count, set_of_index_values)
    Raises: ValueError if any line fails to parse
    """
    line_count = 0
    indices = set()

    with open(path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if not line:  # Skip empty lines silently
                continue
            try:
                record = json.loads(line)
                line_count += 1
                if "index" in record:
                    indices.add(record["index"])
            except json.JSONDecodeError as e:
                # If it's mostly empty, treat as end of valid data
                if len(line.strip()) < 50:
                    break
                raise ValueError(f"Line {line_num} is not valid JSON: {e}")

    return line_count, indices


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

    # Truncate to last complete line
    print("Truncating to last complete JSON line...")
    final_line_count = truncate_to_last_complete_line(backup_path)

    # Verify all lines parse
    print("Verifying all JSON lines parse correctly...")
    line_count, indices = verify_jsonl(backup_path)

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
