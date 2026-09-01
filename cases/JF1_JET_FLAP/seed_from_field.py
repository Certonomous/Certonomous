#!/usr/bin/env python3
"""JF1E continuation seeding: splice a SEED run's converged-time internalField
into a TARGET run's 0/ field, keeping the TARGET's own boundaryField.

Registration: verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md
frozen 6e83157c112cdf606094f88ff0592bf1b02bc4b3, blob 800944bcfeb591973ca8830ae6c8ec6787ce730c
section 3.2.

WHY A SPLICE AND NOT A COPY.  The target row's jet boundary condition is a
DIFFERENT jet: copying the seed's whole field file would carry the seed's
jetSlot velocity, k and omega into the target and silently run the wrong row.
The target's boundaryField is therefore kept verbatim and only the interior is
taken from the seed.

WHY THIS IS LEGITIMATE AT ALL.  The seed and target meshes are the same mesh --
constant/polyMesh/{points,faces,owner,neighbour} are byte-identical between the
wall-slot and patch-slot builds; only three lines of `boundary` differ (the type
word and the inGroups line).  That is measured, and run_jf1e.sh asserts it by
md5 before this script is ever called.  DO NOT call this script without that
assert: on two different meshes the splice would produce a plausible,
cell-misaligned, entirely wrong field.

REFUSALS.  This script exits 2 rather than degrade, on:
  - a missing seed or target file
  - a seed whose internalField cell count is not the target mesh's cell count
  - an output not containing exactly one internalField and one boundaryField
  - a splice that did not change the target's interior (the planted control:
    a seeding step that silently no-ops looks exactly like a successful one,
    which is L-221's shape, so it is refused rather than reported)
"""
import argparse
import re
import sys


def die(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def split_field(text, path):
    """Return (head, internal, tail) where internal is the internalField entry."""
    i = text.find("\ninternalField")
    if i < 0:
        die("no internalField in %s" % path)
    j = text.find("\nboundaryField", i)
    if j < 0:
        die("no boundaryField after internalField in %s" % path)
    if text.find("\ninternalField", i + 1) >= 0:
        die("more than one internalField in %s" % path)
    if text.find("\nboundaryField", j + 1) >= 0:
        die("more than one boundaryField in %s" % path)
    return text[:i + 1], text[i + 1:j + 1], text[j + 1:]


def internal_count(entry, path):
    """Cell count an internalField entry carries. `uniform` carries none."""
    if re.match(r"^internalField\s+uniform", entry):
        return None
    m = re.match(r"^internalField\s+nonuniform\s+List<\w+>\s*\n?\s*(\d+)", entry)
    if not m:
        die("could not read the cell count of internalField in %s" % path)
    return int(m.group(1))


def mesh_cell_count(owner_path):
    """Cell count of the mesh = 1 + max(owner), read from constant/polyMesh/owner.

    build_jf1.py writes no `note "... nCells: N ..."` header, so the count is
    derived from the owner list itself rather than read off a string that this
    generator does not emit.  A header that is not written cannot be parsed, and
    a parser that assumes it would silently take the `except` path.
    """
    try:
        txt = open(owner_path, "r", errors="ignore").read()
    except OSError as exc:
        die("cannot read %s (%s)" % (owner_path, exc))
    i = txt.find("(")
    j = txt.rfind(")")
    if i < 0 or j < 0 or j <= i:
        die("owner file %s has no parenthesised list" % owner_path)
    body = txt[i + 1:j].split()
    if not body:
        die("owner file %s has an empty list" % owner_path)
    try:
        hi = max(int(v) for v in body)
    except ValueError:
        die("owner file %s holds a non-integer entry" % owner_path)
    return hi + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", required=True, help="seed field file, e.g. <run>/8000/U")
    ap.add_argument("--target", required=True, help="target field file, e.g. <run>/0/U")
    ap.add_argument("--owner", required=True, help="target constant/polyMesh/owner")
    args = ap.parse_args()

    try:
        seed_txt = open(args.seed, "r", errors="ignore").read()
        tgt_txt = open(args.target, "r", errors="ignore").read()
    except OSError as exc:
        die("cannot read a field file (%s)" % exc)

    s_head, s_internal, s_tail = split_field(seed_txt, args.seed)
    t_head, t_internal, t_tail = split_field(tgt_txt, args.target)

    ncells = mesh_cell_count(args.owner)
    n_seed = internal_count(s_internal, args.seed)
    if n_seed is None:
        die("seed %s carries a UNIFORM internalField -- it is not a solved field, "
            "so it is not a continuation seed" % args.seed)
    if n_seed != ncells:
        die("seed %s has %d interior values, target mesh has %d cells -- the two "
            "meshes are not the same mesh" % (args.seed, n_seed, ncells))

    # PLANTED CONTROL (CLAUDE.md rule 3).  A seeding step that silently no-ops
    # produces a file that looks exactly like a successful one.  Refuse unless
    # the interior actually changed.
    if s_internal.strip() == t_internal.strip():
        die("the splice would not change %s -- seed and target interiors are "
            "already identical, so this seeding step is a silent no-op" % args.target)

    out = t_head + s_internal + t_tail
    if out.count("\ninternalField") != 1 or out.count("\nboundaryField") != 1:
        die("spliced output for %s is malformed" % args.target)

    with open(args.target, "w") as fh:
        fh.write(out)

    sys.stdout.write(
        "SEEDED %s  <- %s   (%d interior values, boundaryField kept from target)\n"
        % (args.target, args.seed, n_seed))


if __name__ == "__main__":
    main()
