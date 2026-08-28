#!/usr/bin/env python3
"""AVWC SHARED REPAIRED READER -- the `writeCompression` cluster, ONE root cause.

THE ROOT CAUSE, one sentence: **a reader that stats an UNCOMPRESSED filename when
`writeCompression on` has written the `.gz`.**  Two manifestations, three items:

  DATUM     `av1_grade.py:198-200` and `av2_grade.py:186-188` pin `DATUM_REF = "0/U"`
            and `os.path.isfile()` it.  The tutorial's `writeCompression on` means the
            solver wrote `0/U.gz`.  Both items returned NOT A RESULT on that alone with
            EVERY PHYSICS ARTEFACT INTACT (`curriculum_AV1/RESULTS.md:17-22`,
            `curriculum_AV2/RESULTS.md:17-22`).
  PARTITION `av1r_x.py:75-87` -- THE PRODUCER, not the grader -- stats
            `processorN/constant/polyMesh/owner` and records `nCells: None` when the
            file is `owner.gz`.  `av1r_grade.py:407-419` then correctly REFUSED on
            `partition_cells: [null, null], sum: 0`.  **AV1R's grader did the right
            thing; the defect is upstream of it.**

NOTHING HERE IS A FOURTH IMPLEMENTATION.  Both readers are ADOPTED from implementations
already in this repository, cited by file and line, and their SEMANTICS are preserved
including the parts that are easy to lose:

  `resolve_datum()`        adopted from `curriculum_SO1a/so1a_grade.py:292-338`
                           (`resolve_datum_ref`) and its `read_write_compression()` at
                           `:277-290`.  The subtle part that is preserved verbatim in
                           substance: **the mtime rule follows the file that was FOUND.**
                           The UNCOMPRESSED name is the one the launcher touched, so it
                           must still carry the recorded datum EXACTLY; the COMPRESSED
                           twin was written by the SOLVER AFTER the datum was taken, so
                           it may only be NEWER.  Losing that asymmetry would turn a
                           repaired guard into no guard at all.
  `partition_record()`     adopted from `curriculum_D12R2/d12y_w3_stage_and_run.sh:799-808`
                           (`for cand in ("owner", "owner.gz")`, `gzip.open` when `.gz`),
                           which is the same loop as `d12y_stage_and_run.sh`,
                           `d12y_w2_stage_and_run.sh` and `d12y_w2r_stage_and_run.sh`.

WHAT A REPAIRED READER MUST NOT DO, and what the birth controls exist to prove: it must
not turn a GENUINELY missing reference into a pass.  Neither candidate on disk is still a
REFUSAL; a compressed twin OLDER than the datum is still a REFUSAL; a partition that does
not sum to the mesh cell count is still a REFUSAL, and that last one is enforced by the
FROZEN grader, untouched.

L-332: NO `assert` anywhere.
"""
import gzip
import os
import re

NOT_MEASURED = "NOT_MEASURED"
CONTROLDICT_REL = os.path.join("system", "controlDict")


class ReaderRefusal(Exception):
    pass


def candidates_for(registered_name):
    """The registered name FIRST, then its compressed twin.  Derived from the frozen
    instrument's OWN `DATUM_REF` so the successor cannot quietly re-register a different
    reference: candidate[0] is always exactly what the frozen document registered."""
    return (registered_name, registered_name + ".gz")


def read_write_compression(adir):
    """`writeCompression` from THE ARM'S OWN system/controlDict.  A READING, never an
    assumption -- it is what turns `0/U` into `0/U.gz`, and it is recorded beside the
    resolution so the record says why rather than a comment saying why.
    ADOPTED: so1a_grade.py:277-290."""
    cd = os.path.join(adir, CONTROLDICT_REL)
    if not os.path.isfile(cd):
        return {"write_compression": NOT_MEASURED, "write_compression_source": cd,
                "note": "controlDict absent from the arm directory"}
    for line in open(cd, errors="replace"):
        s = line.strip()
        if s.startswith("writeCompression"):
            return {"write_compression": s.rstrip(";").split()[-1], "write_compression_source": cd}
    return {"write_compression": NOT_MEASURED, "write_compression_source": cd,
            "note": "key absent from controlDict"}


def resolve_datum(adir, arm, datum, registered_name, refuse):
    """RESOLVE THE AGE-GUARD DATUM BY EXISTENCE, NEVER BY NAME.
    ADOPTED: so1a_grade.py:292-338.  `refuse` is the FROZEN INSTRUMENT'S OWN refusal
    function, so a refusal from here is shaped exactly like the refusal that instrument
    would have raised -- the successor never invents a refusal vocabulary of its own."""
    wc = read_write_compression(adir)
    cands = candidates_for(registered_name)
    found = [(n, os.path.join(adir, n)) for n in cands if os.path.isfile(os.path.join(adir, n))]
    if not found:
        refuse("G1", {"age_reference_absent_in_every_registered_name": {
            "arm": arm, "candidates": [os.path.join(adir, c) for c in cands], **wc,
            "note": "resolved by EXISTENCE; NEITHER name is on disk, so the age guard has "
                    "no reference and the arm is NOT A RESULT"}})
    name, path = found[0]
    compressed = name.endswith(".gz")
    on_disk = int(os.path.getmtime(path))
    if not compressed:
        # the launcher touched this file; it must still carry the datum EXACTLY
        if on_disk != datum:
            refuse("G1", {"age_reference_moved": path, "recorded": datum,
                          "on_disk": on_disk, "resolved_name": name, **wc})
    else:
        # the SOLVER wrote this AFTER the datum was taken; it may only be NEWER
        if on_disk < datum:
            refuse("G1", {"compressed_datum_twin_older_than_the_datum": path,
                          "recorded": datum, "on_disk": on_disk, "resolved_name": name, **wc})
    return {"arm": arm, "registered_name": registered_name, "candidates": list(cands),
            "resolved_name": name, "resolved_path": path, "is_compressed_twin": compressed,
            "recorded_datum_epoch": datum, "reference_mtime_epoch": on_disk,
            "seconds_newer_than_datum": on_disk - datum,
            "rewritten_by_solver": bool(compressed), **wc}


def partition_record(armdir):
    """Per-processor cell counts read FROM THE MESH ON DISK, by the name that EXISTS.
    ADOPTED: d12y_w3_stage_and_run.sh:799-808.  Returns [] when there are no processor
    directories, which is exactly what a serial arm must record (`av1r_grade.py:409-411`
    refuses a NON-empty record at np = 1).  A processor directory whose `owner` cannot be
    read in EITHER name yields `nCells: None` -- the reader reports what it could not read
    and lets the FROZEN grader refuse, rather than repairing a hole it cannot see into."""
    rec = []
    for d in sorted(_processor_dirs(armdir)):
        pm = os.path.join(d, "constant", "polyMesh")
        n, used, detail = None, None, None
        for cand in ("owner", "owner.gz"):
            fp = os.path.join(pm, cand)
            if os.path.isfile(fp):
                used = cand
                try:
                    op = gzip.open if cand.endswith(".gz") else open
                    with op(fp, "rt", errors="replace") as f:
                        head = f.read(4096)
                    m = re.search(r"nCells:\s*(\d+)", head)
                    n = int(m.group(1)) if m else None
                    if m is None:
                        detail = "no nCells: key in the first 4096 bytes of %s" % cand
                except Exception as exc:                                  # noqa: BLE001
                    detail = "could not read %s: %r" % (cand, repr(exc)[:120])
                break
        if used is None:
            detail = "neither owner nor owner.gz present under %s" % pm
        e = {"dir": os.path.basename(d), "nCells": n, "resolved_name": used}
        if detail:
            e["detail"] = detail
        rec.append(e)
    return rec


def _processor_dirs(armdir):
    if not os.path.isdir(armdir):
        return []
    return [os.path.join(armdir, x) for x in os.listdir(armdir)
            if x.startswith("processor") and os.path.isdir(os.path.join(armdir, x))]
